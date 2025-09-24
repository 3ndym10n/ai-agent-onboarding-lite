import hashlib
from pathlib import Path
from typing import List

from . import utils
from .utils import Issue


def fingerprint(message: str, where: str) -> str:
    h = hashlib.sha256(f"{message}|{where}".encode("utf - 8")).hexdigest()[:12]
    return f"F{h}"


def record_kb(root: Path, fp: str, move: str, outcome: str) -> None:
    kb = root / ".ai_onboard" / "error_kb.jsonl"
    utils.ensure_dir(kb.parent)
    with open(kb, "a", encoding="utf - 8") as f:
        f.write(
            f'{{"ts":"{utils.now_iso()}","fp":"{fp}","move":"{move}","outcome":"{outcome}"}}\n'
        )


def touch_fp(root: Path, fp: str) -> None:
    meta = utils.read_json(root / ".ai_onboard" / "error_meta.json", default={})
    c = meta.get(fp, {}).get("count", 0) + 1
    meta[fp] = {"count": c, "last": utils.now_iso()}
    utils.write_json(root / ".ai_onboard" / "error_meta.json", meta)


def should_ask(root: Path, fp: str) -> bool:
    meta = utils.read_json(root / ".ai_onboard" / "error_meta.json", default={})
    c = meta.get(fp, {}).get("count", 0)
    return c in (2, 5)  # ask at 2nd and 5th repeat as a simple heuristic


def ask_card(root: Path, question: str, options: List[str]) -> None:
    card = root / ".ai_onboard" / "ask_card.md"
    text = ["# Ask Card", "", question, ""] + [f"- [ ] {opt}" for opt in options]
    utils.ensure_dir(card.parent)
    card.write_text("\n".join(text), encoding="utf - 8")


def issue_from_fp(fp: str, rule_id: str, message: str) -> Issue:
    return Issue(
        rule_id=rule_id,
        severity="error",
        message=f"{message} (fp={fp})",
        confidence=0.9,
    )


# Very small rule→suggestion mapping (extendable)


def suggest_move_from_rule(rule_id: str, message: str) -> dict:
    if "NODE_SCRIPTS_DEFINED" in rule_id:
        return {
            "question": "No build / lint / test scripts detected. Add default scripts or relax this rule?",
            "options": ["Add default scripts", "Downgrade to warning for this repo"],
        }
    if "PY_PROJECT_META" in rule_id or "ModuleNotFoundError" in message:
        return {
            "question": "Python dependency / config missing. Add requirement or skip this check?",
            "options": ["Add to requirements.txt", "Skip this check for now"],
        }
    return {
        "question": "How do you want to handle this validation failure?",
        "options": ["Apply suggested patch", "Skip this rule for this repo"],
    }
