from pathlib import Path
from . import utils

def record_run(root: Path, res: dict) -> None:
    metrics_path = root / ".ai_onboard" / "metrics.jsonl"
    utils.ensure_dir(metrics_path.parent)
    summary = res.get("summary", {})
    rec = {
        "ts": utils.now_iso(),
        "pass": bool(summary.get("pass")),
        "components": [
            {"name": r["component"], "score": r["score"], "issue_count": len(r["issues"])}
            for r in res.get("results", [])
        ]
    }
    with open(metrics_path, "a", encoding="utf-8") as f:
        f.write(f"{rec}\n")
