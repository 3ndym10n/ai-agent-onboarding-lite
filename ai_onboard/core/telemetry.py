from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from . import utils


def _safe_components(results: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert validation results into a compact, robust component summary.

    Safely extracts component information with defaults to avoid KeyError.
    Handles various formats of issue counts gracefully.
    """
    components = []

    for result in results or []:
        component_info = {
            "name": result.get("component", "unknown"),
            "score": result.get("score"),
            "issue_count": _extract_issue_count(result.get("issues", [])),
        }
        components.append(component_info)

    return components


def _extract_issue_count(issues) -> int:
    """
    Safely extract issue count from various formats.

    Args:
        issues: Can be a list, tuple, int, or other format

    Returns:
        Integer count of issues, defaulting to 0 on error
    """
    try:
        if isinstance(issues, (list, tuple)):
            return len(issues)
        elif isinstance(issues, (int, str)):
            return int(issues)
        else:
            return 0
    except (ValueError, TypeError):
        return 0


def record_run(root: Path, res: Dict[str, Any]) -> None:
    """Append a single metrics record in JSONL format.

    Best - effort: never raises on write failures; logs a minimal error entry instead.
    Schema (stable):
    - ts: ISO8601 timestamp
    - pass: bool (overall pass / fail)
    - components: list of { name, score, issue_count }
    """
    metrics_path = root / ".ai_onboard" / "metrics.jsonl"
    utils.ensure_dir(metrics_path.parent)

    summary = (res or {}).get("summary", {}) or {}
    rec: Dict[str, Any] = {
        "ts": utils.now_iso(),
        "pass": bool(summary.get("pass", False)),
        "components": _safe_components((res or {}).get("results", []) or []),
    }

    try:
        with open(metrics_path, "a", encoding="utf - 8") as f:
            json.dump(rec, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
    except Exception as e:
        # Best - effort: capture minimal error info without crashing the CLI.
        err_path = metrics_path.with_suffix(".errors.log")
        try:
            with open(err_path, "a", encoding="utf - 8") as ef:
                ef.write(
                    f"{utils.now_iso()} | telemetry_write_error | {type(e).__name__}: {e}\n"
                )
        except Exception:
            # Swallow secondary errors to avoid surfacing telemetry issues to users.
            pass


def read_metrics(root: Path) -> List[Dict[str, Any]]:
    """Read all metrics records from JSONL, newest last. Returns [] if missing."""
    metrics_path = root / ".ai_onboard" / "metrics.jsonl"
    if not metrics_path.exists():
        return []
    out: List[Dict[str, Any]] = []
    with open(metrics_path, "r", encoding="utf - 8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                # Skip malformed lines to keep reader tolerant.
                continue
    return out


def last_run(root: Path) -> Dict[str, Any] | None:
    """Return the most recent metrics record, or None if none exist."""
    items = read_metrics(root)
    return items[-1] if items else None


# Lightweight event logger for audits

def log_event(event: str, **fields: Any) -> None:
    logs_dir = Path(".ai_onboard") / "logs"
    utils.ensure_dir(logs_dir)
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": event}
    rec.update(fields or {})
    path = logs_dir / "events.jsonl"
    try:
        with open(path, "a", encoding="utf - 8") as f:
            json.dump(rec, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
    except Exception:
        # Best - effort; do not raise from telemetry
        pass
