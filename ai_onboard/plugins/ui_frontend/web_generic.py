import json, os
from typing import List, Dict, Any
from ...core.issue import Issue
from ...core.registry import register

class NodeScriptsPresent:
    name = "node.pkg_scripts_present"
    def run(self, paths: List[str], ctx: Dict[str, Any]):
        root = ctx["root"]; pkg = os.path.join(root, "package.json")
        if not os.path.exists(pkg):
            return [Issue("NODE_SCRIPTS_DEFINED","warn","package.json missing", pkg, confidence=0.6)]
        try:
            data = json.loads(open(pkg, "r", encoding="utf-8").read())
        except Exception as e:
            return [Issue("NODE_SCRIPTS_DEFINED","error",f"package.json unreadable: {e}", pkg, confidence=0.9)]
        scripts = (data.get("scripts") or {})
        need = {"build","lint","test"}
        if need.intersection(set(scripts.keys())):
            return []
        return [Issue("NODE_SCRIPTS_DEFINED","warn","No build/lint/test scripts in package.json", pkg, confidence=0.9)]

def _register():
    register("ui_frontend","node_ts", NodeScriptsPresent())
_register()
