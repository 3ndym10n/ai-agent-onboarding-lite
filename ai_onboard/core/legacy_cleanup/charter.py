from pathlib import Path

from ..base import utils

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
    if isinstance(ch, dict) and ch["project_name"] == "TBD":
        ch["project_name"] = root.name
    if isinstance(ch, dict):
        ch["methodology"] = utils.pick_methodology(ch)
        utils.write_json(path, ch)
        return ch
    return TEMPLATE.copy()


def require_gate(root: Path, needed: str) -> None:
    from ..base import state

    state.require_gate(root, needed)


def load_charter(root: Path) -> dict:
    """Load the project charter"""
    path = root / ".ai_onboard" / "charter.json"
    data = utils.read_json(path, default=TEMPLATE.copy())
    return data if isinstance(data, dict) else TEMPLATE.copy()
