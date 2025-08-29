from pathlib import Path
import json

from . import utils

def open_checkpoint(root: Path, name: str) -> None:
    log = root / ".ai_onboard" / "decision_log.jsonl"
    utils.ensure_dir(log.parent)
    with open(log, "a", encoding="utf-8") as f:
        f.write(
            f'{{"ts":"{utils.now_iso()}","decision":"OPEN","subject":"{name}"}}\n'
        )

def record_decision(root: Path, decision: str, subject: str, approved: bool, note: str) -> None:
    """Record a decision to the JSON lines log.

    Each decision is stored as a single JSON object per line. ``json.dump`` is
    used so that notes are escaped safely.
    """
    log = root / ".ai_onboard" / "decision_log.jsonl"
    utils.ensure_dir(log.parent)
    entry = {
        "ts": utils.now_iso(),
        "decision": decision,
        "subject": subject,
        "approved": approved,
        "note": note,
    }
    with open(log, "a", encoding="utf-8") as f:
        json.dump(entry, f)
        f.write("\n")

def require_alignment(root: Path, checkpoint: str) -> None:
    """Ensure that ``checkpoint`` has an approved ALIGN decision.

    The decision log stores JSON objects, one per line. Each line is parsed to
    check for a matching approved ALIGN entry. Malformed lines are skipped.
    """
    log = root / ".ai_onboard" / "decision_log.jsonl"
    if not log.exists():
        raise SystemExit(f"Alignment required: {checkpoint}")

    ok = False
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            entry.get("decision") == "ALIGN"
            and entry.get("subject") == checkpoint
            and entry.get("approved") is True
        ):
            ok = True
            break

    if not ok:
        raise SystemExit(f"Alignment approval missing for {checkpoint}")

def require_state(root: Path, needed: str) -> None:
    from . import state
    state.require_gate(root, needed)
