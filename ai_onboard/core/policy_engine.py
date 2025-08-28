from pathlib import Path
from . import utils

def load(root: Path) -> dict:
    manifest = utils.read_json(root / "ai_onboard.json", default={"policies":{}})
    base_path = Path(manifest.get("policies",{}).get("base","./ai_onboard/policies/base.json"))
    policy = utils.read_json(root / base_path, default={
        "rules":[],
        "scoring":{"pass_threshold":0.7,"weights":{"error":1.0,"warn":0.4,"info":0.1}}
    })
    for overlay in manifest.get("policies",{}).get("overlays", []):
        o = utils.read_json(root / overlay, default={})
        _merge(policy, o)
    return policy

def _merge(dst: dict, src: dict) -> None:
    for k,v in src.items():
        if isinstance(v, list):
            dst.setdefault(k,[]).extend(v)
        elif isinstance(v, dict):
            dst.setdefault(k,{}); _merge(dst[k], v)
        else:
            dst[k] = v
