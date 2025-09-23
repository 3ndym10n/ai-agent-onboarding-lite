
from pathlib import Path
from typing import Dict, List


def _snapshot(root: Path):
    snap = {}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        parts = {part.lower() for part in p.parts}
        if "ai_onboard" in parts or ".git" in parts or ".ai_onboard" in parts:
            continue
        try:
            snap[str(p)] = os.path.getmtime(p)
        except Exception:
            pass
    return snap


def load(root: Path) -> dict:
    return utils.read_json(
        root / ".ai_onboard" / "cache_index.json",
        default={"rules": {}, "map": {}, "snapshot": {}},
    )


def save(root: Path, idx: dict) -> None:
    utils.write_json(root / ".ai_onboard" / "cache_index.json", idx)


def changed_files(root: Path, idx: dict) -> List[str]:
    new = _snapshot(root)
    old = idx.get("snapshot", {})
    changed = [k for k, v in new.items() if old.get(k) != v]
    idx["snapshot"] = new
    return changed


def rule_impacted(idx: dict, rule_id: str, changed: List[str]) -> bool:
    globs = idx.get("map", {}).get(rule_id, ["**/*"])
    for g in globs:
        for f in changed:
            if fnmatch.fnmatch(f, g):
                return True
    return False
