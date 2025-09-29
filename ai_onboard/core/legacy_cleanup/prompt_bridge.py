from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from ..base import telemetry, utils
from ..utilities import summarizer


def dumps_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def _manifest(root: Path) -> Dict[str, Any]:
    return utils.read_json(root / "ai_onboard.json", default={}) or {}


def get_project_state(root: Path) -> Dict[str, Any]:
    man = _manifest(root)
    last = telemetry.last_run(root) or {}
    return {
        "manifest_present": bool(man),
        "components": [c.get("name") for c in man.get("components", [])],
        "features": man.get("features", {}),
        "last_metrics": {
            "ts": last.get("ts"),
            "pass": last.get("pass"),
            "components": last.get("components", []),
        },
    }


def get_applicable_rules(
    root: Path, target_path: str = ".", change_summary: str = ""
) -> Dict[str, Any]:
    man = _manifest(root)
    try:
        parsed = json.loads(change_summary) if change_summary else {}
    except Exception:
        parsed = {"_note": "non - json change summary provided"}
    rules = utils.applicable_rules(root, man, target_path, parsed)
    return {"rules": rules}


def summary(root: Path, level: str = "brief") -> Dict[str, Any]:
    return summarizer.make_summary(root, level=level)


def propose_action(root: Path, diff_json: str = "") -> Dict[str, Any]:
    try:
        diff = json.loads(diff_json) if diff_json else {}
    except Exception as e:
        return {"decision": "deny", "reason": f"invalid diff json: {e}"}
    man = _manifest(root)
    return utils.propose_intent_decision(root, man, diff)
