from __future__ import annotations

from typing import Any, Dict, List

from .errors import PolicyError


ALLOWED_ACTIONS = {"allow", "warn", "require_approval", "block"}


def _is_str(x: Any) -> bool:
    return isinstance(x, str) and len(x) >= 1


def validate_policy(policy: Dict[str, Any]) -> None:
    """Lightweight policy validator aligned to policy.schema.json.

    - rules: optional list of objects with required id:str and action in ALLOWED_ACTIONS
    - message: optional str
    Additional properties are allowed; unknown keys are ignored here.
    Raises PolicyError on violations with a concise message.
    """
    if policy is None:
        return
    rules = policy.get("rules")
    if rules is None:
        return
    if not isinstance(rules, list):
        raise PolicyError("policy.rules must be an array")
    for idx, r in enumerate(rules):
        if not isinstance(r, dict):
            raise PolicyError(f"policy.rules[{idx}] must be an object")
        rid = r.get("id")
        action = r.get("action")
        if not _is_str(rid):
            raise PolicyError(f"policy.rules[{idx}].id must be a non-empty string")
        if not _is_str(action) or action not in ALLOWED_ACTIONS:
            raise PolicyError(
                f"policy.rules[{idx}].action must be one of {sorted(ALLOWED_ACTIONS)}"
            )
        msg = r.get("message")
        if msg is not None and not _is_str(msg):
            raise PolicyError(f"policy.rules[{idx}].message must be a string if present")

