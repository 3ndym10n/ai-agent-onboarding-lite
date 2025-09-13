"""Append - only run log (.ai_onboard / log.jsonl)."""

import json
import time
from pathlib import Path
from typing import Any, Dict


def _path(root: Path) -> Path:
    d = root / ".ai_onboard"
    d.mkdir(parents = True, exist_ok = True)
    return d / "log.jsonl"


def write_event(root: Path, kind: str, payload: Dict[str, Any]) -> None:
    rec = {
        "ts": time.time(),
        "kind": kind,
        "data": payload,
    }
    p = _path(root)
    with p.open("a", encoding="utf - 8") as f:
        f.write(json.dumps(rec) + "\n")
