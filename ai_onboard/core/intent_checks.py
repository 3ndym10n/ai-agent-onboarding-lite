from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json

from . import meta_policy, utils


def applicable_rules(root: Path, manifest: Dict[str, Any], target_path: str, change: Dict[str, Any]) -> List[Dict[str, Any]]:
    rules = meta_policy.rules_summary(manifest)
    # Optionally tailor by target
    for r in rules:
        r["target"] = target_path
    return rules


def propose(root: Path, manifest: Dict[str, Any], diff: Dict[str, Any]) -> Dict[str, Any]:
    ff = (manifest.get("features") or {})
    if ff.get("intent_checks", True) is False:
        return {"decision": "allow", "reasons": [{"rule": "feature_flag", "detail": "intent_checks disabled"}]}
    return meta_policy.evaluate(manifest, diff)

