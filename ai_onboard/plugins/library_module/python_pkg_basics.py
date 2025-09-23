from typing import Any

from ai_onboard.core.common_imports import Dict, List, os


class PythonPkgBasicsPlugin:

    def run(self, paths: List[str], ctx: Dict[str, Any]):
        return {"status": "ok", "message": "Python package basics plugin"}
