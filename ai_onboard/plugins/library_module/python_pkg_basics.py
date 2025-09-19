import os

class PyProjectBasics:
    name = "python.pyproject_basics"

    def run(self, paths: List[str], ctx: Dict[str, Any]):
        root = ctx["root"]
        has_req = os.path.exists(os.path.join(root, "requirements.txt"))
        has_pyproj = os.path.exists(os.path.join(root, "pyproject.toml"))
        if has_req or has_pyproj:
            return []
        return [
            Issue(
                "PY_PROJECT_META",
                "warn",
                "No pyproject.toml or requirements.txt found",
                root,
                confidence=0.8,
            )
        ]


def _register():
    register("library_module", "python", PyProjectBasics())


_register()
