from pathlib import Path
from . import utils
from typing import Any, Dict


def _read_policy_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"rules": [], "scoring": {"pass_threshold": 0.7, "weights": {"error": 1.0, "warn": 0.4, "info": 0.1}}}
    suffix = path.suffix.lower()
    try:
        if suffix in (".yaml", ".yml"):
            try:
                import yaml  # type: ignore
            except Exception:
                # YAML not available; return empty policy (non-fatal)
                return {}
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        # default JSON
        return utils.read_json(path, default={}) or {}
    except Exception:
        return {}

def load(root: Path) -> dict:
    manifest = utils.read_json(root / "ai_onboard.json", default={"policies": {}}) or {"policies": {}}
    base_default = "./ai_onboard/policies/base.yaml"
    base_path = Path(manifest.get("policies", {}).get("base", base_default))
    base_full = (root / base_path)
    # If configured base points to json but yaml exists, prefer configured; otherwise if default and json missing, try yaml
    policy = _read_policy_file(base_full)
    for overlay in manifest.get("policies", {}).get("overlays", []):
        o = _read_policy_file(root / Path(overlay))
        _merge(policy, o)
    # Ensure scoring defaults present
    policy.setdefault("scoring", {"pass_threshold": 0.7, "weights": {"error": 1.0, "warn": 0.4, "info": 0.1}})
    policy.setdefault("rules", [])
    return policy

def _merge(dst: dict, src: dict) -> None:
    for k,v in src.items():
        if isinstance(v, list):
            dst.setdefault(k,[]).extend(v)
        elif isinstance(v, dict):
            dst.setdefault(k,{}); _merge(dst[k], v)
        else:
            dst[k] = v
