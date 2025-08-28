from pathlib import Path
from . import utils

def run(root: Path, allow_exec: bool=False) -> dict:
    has_py = (root / "pyproject.toml").exists() or (root / "requirements.txt").exists()
    has_node = (root / "package.json").exists()
    components = []
    if has_node:
        components.append({"name":"ui","type":"ui_frontend","language":"node_ts","paths":["."],"tech":{"framework":"unknown"}})
    if has_py:
        components.append({"name":"lib","type":"library_module","language":"python","paths":["."]})
    manifest = {
        "project_type": "unknown",
        "languages": [x for x,ok in (("python",has_py),("node_ts",has_node)) if ok],
        "components": components,
        "policies": {"base": "./ai_onboard/policies/base.json", "overlays": []},
        "execution": {"allowExec": False, "max_workers": 4, "timeouts_ms": {"default": 2000}},
        "ci": {"enabled": True, "provider": "github_actions"}
    }
    return manifest
