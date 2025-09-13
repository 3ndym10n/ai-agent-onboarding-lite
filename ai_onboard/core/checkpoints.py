from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List

from . import utils

INDEX = "index.jsonl"


def _ckpt_dir(root: Path) -> Path:
    p = root / ".ai_onboard" / "checkpoints"
    utils.ensure_dir(p)
    return p


def _normalize_scope(root: Path, scope: Iterable[str]) -> List[Path]:
    # Convert globs to concrete paths, ignore protected internals by convention
    out: List[Path] = []
    for pat in scope:
        for p in root.glob(pat):
            try:
                rp = p.relative_to(root)
            except Exception:
                continue
            if any(str(rp).startswith(x) for x in (".ai_onboard/", ".git/")):
                continue
            out.append(rp)
    # Deduplicate
    seen = set()
    uniq: List[Path] = []
    for p in out:
        s = str(p)
        if s in seen:
            continue
        seen.add(s)
        uniq.append(p)
    return uniq


def create(root: Path, scope: Iterable[str], reason: str = "") -> Dict[str, Any]:
    items = _normalize_scope(root, scope)
    ckid = f"ckpt_{uuid.uuid4().hex[:8]}"
    based = _ckpt_dir(root) / ckid
    filesd = based / "files"
    utils.ensure_dir(filesd)
    # Copy files preserving relative structure
    for rel in items:
        src = root / rel
        dst = filesd / rel
        utils.ensure_dir(dst.parent)
        if src.is_dir():
            # Skip directories; only snapshot regular files
            continue
        shutil.copy2(src, dst)
    rec = {
        "ts": utils.now_iso(),
        "id": ckid,
        "scope": [str(p) for p in items],
        "reason": reason,
    }
    with open(_ckpt_dir(root) / INDEX, "a", encoding="utf - 8") as f:
        f.write(json.dumps(rec, ensure_ascii = False, separators=(",", ":")) + "\n")
    return rec


def list(root: Path) -> List[Dict[str, Any]]:
    idxp = _ckpt_dir(root) / INDEX
    if not idxp.exists():
        return []
    out: List[Dict[str, Any]] = []
    with open(idxp, "r", encoding="utf - 8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def restore(root: Path, ckpt_id: str) -> Dict[str, Any]:
    based = _ckpt_dir(root) / ckpt_id
    filesd = based / "files"
    if not filesd.exists():
        return {"restored": 0, "errors": [f"missing checkpoint: {ckpt_id}"]}
    restored = 0
    errors: List[str] = []
    for src in filesd.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(filesd)
        dst = root / rel
        try:
            utils.ensure_dir(dst.parent)
            shutil.copy2(src, dst)
            restored += 1
        except Exception as e:
            errors.append(f"{rel}: {e}")
    return {"restored": restored, "errors": errors}
