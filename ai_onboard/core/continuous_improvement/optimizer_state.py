from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..base import utils

STATE_PATH = ".ai_onboard/optimizer_state.json"


def load(root: Path) -> Dict[str, Any]:
    data = utils.read_json(root / STATE_PATH, default={"rules": {}})
    return data if isinstance(data, dict) else {"rules": {}}


def save(root: Path, state: Dict[str, Any]) -> None:
    utils.write_json(root / STATE_PATH, state)


def update_rule_stats(
    state: Dict[str, Any], rule_id: str, duration_s: float, issues_found: int
) -> None:
    rules = state.setdefault("rules", {})
    r = rules.setdefault(
        rule_id, {"runs": 0, "issues": 0, "avg_time": 0.0, "passes_in_row": 0}
    )
    runs_prev = r["runs"]
    # Online averages
    r["runs"] = runs_prev + 1
    r["issues"] += int(issues_found)
    r["avg_time"] = (r["avg_time"] * runs_prev + float(duration_s)) / max(1, r["runs"])
    # Update pass streak
    if issues_found == 0:
        r["passes_in_row"] = int(r.get("passes_in_row", 0)) + 1
    else:
        r["passes_in_row"] = 0


def fault_yield(state: Dict[str, Any], rule_id: str) -> float:
    r = state.get("rules", {}).get(rule_id)
    if not r or not isinstance(r, dict) or r.get("runs", 0) == 0:
        return 0.05
    issues = r.get("issues", 0)
    runs = r.get("runs", 1)
    if isinstance(issues, (int, float)) and isinstance(runs, (int, float)):
        return max(0.0, min(1.0, float(issues) / float(runs)))
    return 0.05


def avg_time(state: Dict[str, Any], rule_id: str) -> float:
    r = state.get("rules", {}).get(rule_id)
    if not r or r["runs"] == 0:
        return 0.2
    return max(1e-3, float(r["avg_time"]))


def passes_in_row(state: Dict[str, Any], rule_id: str) -> int:
    r = state.get("rules", {}).get(rule_id)
    if not r:
        return 0
    return int(r.get("passes_in_row", 0))
