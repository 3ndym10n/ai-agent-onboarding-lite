from pathlib import Path

from . import methodology, utils

TEMPLATE = {
    "version": 1,
    "project_name": "TBD",
    "vision": "One sentence purpose.",
    "objectives": [],
    "non_goals": [],
    "stakeholders": [{"name": "Owner", "role": "PM", "decider": True}],
    "constraints": {"time": "", "budget": "", "compliance": []},
    "assumptions": [],
    "success_metrics": [{"name": "Lead time", "target": "<7d"}],
    "risk_appetite": "medium",
    "delivery_horizon_days": 30,
    "team_size": 3,
    "preferred_methodology": "auto",
}


def ensure(root: Path, interactive: bool = False) -> dict:
    path = root / ".ai_onboard" / "charter.json"
    ch = utils.read_json(path, default=TEMPLATE.copy())
    if ch["project_name"] == "TBD":
        ch["project_name"] = root.name
    ch["methodology"] = methodology.pick(ch)
    utils.write_json(path, ch)
    return ch


def require_gate(root: Path, needed: str) -> None:
    from . import state

    state.require_gate(root, needed)


def load_charter(root: Path) -> dict:
    """Load the project charter"""
    path = root / ".ai_onboard" / "charter.json"
    return utils.read_json(path, default=TEMPLATE.copy())
