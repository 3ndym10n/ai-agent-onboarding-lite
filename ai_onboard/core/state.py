from pathlib import Path
from . import utils

ORDER = ["unchartered", "chartered", "planned", "aligned", "executing", "kaizen_cycle"]

def load(root: Path) -> dict:
    return utils.read_json(root / ".ai_onboard" / "state.json", default={"state": "unchartered"})

def save(root: Path, st: dict) -> None:
    utils.write_json(root / ".ai_onboard" / "state.json", st)

def advance(root: Path, st: dict, target: str) -> None:
    cur = st.get("state", "unchartered")
    if ORDER.index(target) < ORDER.index(cur):
        return
    st["state"] = target
    save(root, st)

def require_gate(root: Path, needed: str) -> None:
    st = load(root)
    if ORDER.index(st.get("state", "unchartered")) < ORDER.index(needed):
        raise SystemExit(f"Blocked: state must be ≥ {needed} (current: {st.get('state')})")
