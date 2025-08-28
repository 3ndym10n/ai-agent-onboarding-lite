from pathlib import Path
from . import utils

def open_checkpoint(root: Path, name: str) -> None:
    log = root / ".ai_onboard" / "decision_log.jsonl"
    utils.ensure_dir(log.parent)
    with open(log, "a", encoding="utf-8") as f:
        f.write(f'{{"ts":"{utils.now_iso()}","decision":"OPEN","subject":"{name}"}}\n')

def record_decision(root: Path, decision: str, subject: str, approved: bool, note: str) -> None:
    log = root / ".ai_onboard" / "decision_log.jsonl"
    utils.ensure_dir(log.parent)
    with open(log, "a", encoding="utf-8") as f:
        f.write(f'{{"ts":"{utils.now_iso()}","decision":"{decision}","subject":"{subject}","approved":{str(approved).lower()},"note":{repr(note)}}}\n')

def require_alignment(root: Path, checkpoint: str) -> None:
    log = root / ".ai_onboard" / "decision_log.jsonl"
    if not log.exists():
        raise SystemExit(f"Alignment required: {checkpoint}")
    ok = False
    for line in log.read_text(encoding="utf-8").splitlines():
        if f'"decision":"ALIGN"' in line and f'"subject":"{checkpoint}"' in line and '"approved":true' in line:
            ok = True
    if not ok:
        raise SystemExit(f"Alignment approval missing for {checkpoint}")

def require_state(root: Path, needed: str) -> None:
    from . import state
    state.require_gate(root, needed)
