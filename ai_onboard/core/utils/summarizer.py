from pathlib import Path
from typing import Any, Dict, List


def _brief(last: Dict[str, Any], changed: List[str]) -> Dict[str, Any]:
    comps = last.get("components", [])
    top = [
        {"name": c.get("name"), "score": c.get("score"), "issues": c.get("issue_count")}
        for c in comps[:5]
    ]
    # Include canonical progress snapshot
    try:

        root = Path.cwd()
        plan = progress_utils.load_plan(root)
        overall = progress_utils.compute_overall_progress(plan)
    except Exception:
        overall = {}
    return {
        "ts": last.get("ts"),
        "pass": last.get("pass"),
        "top_components": top,
        "recent_changed_files": changed[:10],
        "progress": overall,
    }


def _full(last: Dict[str, Any], changed: List[str]) -> Dict[str, Any]:
    try:

        root = Path.cwd()
        plan = progress_utils.load_plan(root)
        overall = progress_utils.compute_overall_progress(plan)
        milestones = progress_utils.compute_milestone_progress(plan)
    except Exception:
        overall = {}
        milestones = []
    return {
        "last_run": last,
        "recent_changed_files": changed,
        "progress": {
            "overall": overall,
            "milestones": milestones,
        },
    }


def make_summary(root: Path, level: str = "brief") -> Dict[str, Any]:
    last = telemetry.last_run(root) or {}
    idx = cache.load(root)
    # Convert absolute paths to repo - relative for readability
    abs_changed = cache.changed_files(root, idx)
    prefix = str(root.resolve())
    changed = [
        (
            c[len(prefix) + 1 :]
            if c.startswith(prefix + "\\") or c.startswith(prefix + "/")
            else c
        )
        for c in abs_changed
    ]
    if level == "full":
        return _full(last, changed)
    return _brief(last, changed)
