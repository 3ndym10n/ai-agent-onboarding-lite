"""
Lean localhost approval server for human - in - the - loop confirmation.

No external dependencies. Serves a single page with Approve / Stop and
optional textareas for questions. Returns a result dict and shuts down.

Compatible with Python 3.8+.
"""

import socket
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs


def _find_free_port(preferred: int = 8765) -> int:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("127.0.0.1", preferred))
            return preferred
    except OSError:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]


class _ApprovalHandler(BaseHTTPRequestHandler):
    server_version = "LeanApproval / 1.0"

    def _html(self, body: str) -> bytes:
        head = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>AI Onboard Approval</title>"
            "<style>body{font-family:system-ui,Arial;margin:24px;max-width:860px}"
            "button{padding:10px 16px;margin-right:8px}</style>"
            "</head><body>"
        )
        tail = "</body></html>"
        return (head + body + tail).encode("utf-8")

    def do_GET(self):  # noqa: N802
        ctx = self.server.context  # type: ignore[attr - defined]
        title = ctx.get("title", "Approval Required")
        description = ctx.get("description", "Please review and choose.")
        questions: List[str] = ctx.get("questions", [])

        inputs = []
        for idx, q in enumerate(questions):
            inputs.append(
                f"<div style='margin:12px 0'><div >< strong > Q{idx + 1}.</strong> {q}</div>"
                f"<textarea name='answer_{idx}' rows='3' style='width:100%;margin - top:6px'></textarea ></ div>"
            )

        body = (
            f"<h2>{title}</h2>"
            f"<p>{description}</p>"
            "<form method='POST' action='/submit'>"
            + "".join(inputs)
            + "<div style='margin - top:16px'>"
            "<button type='submit' name='decision' value='proceed'>Approve </ button>"
            "<button type='submit' name='decision' value='stop'>Stop </ button>"
            "</div>"
            "</form>"
        )

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(self._html(body))

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length).decode("utf-8")
        form = parse_qs(data)
        decision = (form.get("decision", [""])[0] or "stop").strip()

        # Extract answers in index order
        answers: List[str] = []
        for key in sorted(
            (k for k in form.keys() if k.startswith("answer_")),
            key=lambda x: int(x.split("_", 1)[1]),
        ):
            answers.append((form.get(key, [""])[0] or "").strip())

        # Store and shutdown
        self.server.result = {  # type: ignore[attr - defined]
            "user_decision": "proceed" if decision == "proceed" else "stop",
            "user_responses": answers,
            "ts": time.time(),
        }
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(self._html("<h3>Thanks! You may close this tab.</h3>"))
        # Shutdown in background to let response flush
        Thread(
            target=self.server.shutdown, daemon=True
        ).start()  # type: ignore[attr - defined]


def request_approval(
    title: str,
    description: str,
    questions: Optional[List[str]] = None,
    timeout_seconds: int = 300,
) -> Dict[str, Any]:
    """Start a small local server and block until user approves or stops.

    Returns a dict: { user_decision: "proceed"|"stop", user_responses: [...] }
    """
    questions = questions or []
    port = _find_free_port()
    addr = ("127.0.0.1", port)
    httpd = HTTPServer(addr, _ApprovalHandler)
    # attach context / result to server instance
    httpd.context = {  # type: ignore[attr - defined]
        "title": title,
        "description": description,
        "questions": questions,
    }
    httpd.result = None  # type: ignore[attr - defined]

    t = Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    url = f"http://{addr[0]}:{addr[1]}"
    print(f"[APPROVE] Open {url} to approve or stop. Waiting for your click...")

    start = time.time()
    try:
        while time.time() - start < timeout_seconds:
            res = getattr(httpd, "result", None)
            if res:
                return res  # type: ignore[return - value]
            time.sleep(0.2)
    finally:
        try:
            httpd.shutdown()
        except Exception:
            pass

    return {
        "user_decision": "stop",
        "user_responses": [],
        "ts": time.time(),
    }
