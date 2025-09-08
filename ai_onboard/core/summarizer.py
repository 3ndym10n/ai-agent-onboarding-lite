from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from . import cache, telemetry, utils


def _brief(last: Dict[str, Any], changed: List[str]) -> Dict[str, Any]:
    comps = last.get("components", [])
    top = [
        {"name": c.get("name"), "score": c.get("score"), "issues": c.get("issue_count")}
        for c in comps[:5]
    ]
    return {
        "ts": last.get("ts"),
        "pass": last.get("pass"),
        "top_components": top,
        "recent_changed_files": changed[:10],
    }


def _full(last: Dict[str, Any], changed: List[str]) -> Dict[str, Any]:
    return {
        "last_run": last,
        "recent_changed_files": changed,
    }


def make_summary(root: Path, level: str = "brief") -> Dict[str, Any]:
    last = telemetry.last_run(root) or {}
    idx = cache.load(root)
    # Convert absolute paths to repo-relative for readability
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
