from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from . import utils


def record_event(root: Path, rec: Dict[str, Any]) -> None:
    """Append a single cross-agent record to agents.jsonl. Best-effort."""
    path = root / ".ai_onboard" / "agents.jsonl"
    utils.ensure_dir(path.parent)
    out = {
        "ts": utils.now_iso(),
    }
    out.update(rec or {})
    try:
        with open(path, "a", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
    except Exception:
        pass
