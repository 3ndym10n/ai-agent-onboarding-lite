from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


DEFAULTS = {
    "MAX_DELETE_LINES": 100,
    "MAX_REFACTOR_FILES": 10,
    "REQUIRES_TEST_COVERAGE": True,
}


def _cfg(manifest: Dict[str, Any]) -> Dict[str, Any]:
    # Read from manifest["metaPolicies"] or top-level thresholds fallback
    m = manifest or {}
    mp = (m.get("metaPolicies") or {})
    out = DEFAULTS.copy()
    out.update({k: v for k, v in mp.items() if k in DEFAULTS})
    # Legacy variables (if present at top-level)
    for k in DEFAULTS:
        if k in m:
            out[k] = m[k]
    return out


def rules_summary(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    cfg = _cfg(manifest)
    return [
        {"id": "MAX_DELETE_LINES", "threshold": cfg["MAX_DELETE_LINES"], "action": "confirm"},
        {"id": "MAX_REFACTOR_FILES", "threshold": cfg["MAX_REFACTOR_FILES"], "action": "confirm"},
        {"id": "REQUIRES_TEST_COVERAGE", "enabled": bool(cfg["REQUIRES_TEST_COVERAGE"]), "action": "confirm"},
    ]


def evaluate(manifest: Dict[str, Any], diff: Dict[str, Any]) -> Dict[str, Any]:
    """Return a decision with rationale based on diff summary.

    Diff schema (best-effort, optional keys):
    - files_changed: list[str]
    - lines_deleted: int
    - has_tests: bool
    - subsystems: list[str]
    """
    cfg = _cfg(manifest)
    files = diff.get("files_changed", []) or []
    if isinstance(files, int):
        files = []  # If files_changed is an integer, treat as empty list
    deleted = int(diff.get("lines_deleted", 0) or 0)
    has_tests = bool(diff.get("has_tests", False))
    subsystems = diff.get("subsystems", []) or []

    hits: List[Dict[str, Any]] = []

    if deleted > cfg["MAX_DELETE_LINES"]:
        hits.append({
            "rule": "MAX_DELETE_LINES",
            "severity": "warn",
            "detail": {"deleted": deleted, "threshold": cfg["MAX_DELETE_LINES"]},
            "action": "confirm",
        })

    if len(files) > cfg["MAX_REFACTOR_FILES"]:
        hits.append({
            "rule": "MAX_REFACTOR_FILES",
            "severity": "warn",
            "detail": {"files": len(files), "threshold": cfg["MAX_REFACTOR_FILES"]},
            "action": "confirm",
        })

    if cfg["REQUIRES_TEST_COVERAGE"] and (deleted > 0 or len(files) > 0) and not has_tests:
        hits.append({
            "rule": "REQUIRES_TEST_COVERAGE",
            "severity": "warn",
            "detail": {"has_tests": has_tests},
            "action": "confirm",
        })

    # Subsystem breadth heuristic: touching multiple components should confirm
    if len(subsystems) > 1:
        hits.append({
            "rule": "SUBSYSTEM_BREADTH",
            "severity": "warn",
            "detail": {"subsystems": subsystems},
            "action": "confirm",
        })

    # Decision aggregation
    decision = "allow" if not hits else "confirm"
    return {"decision": decision, "reasons": hits}

