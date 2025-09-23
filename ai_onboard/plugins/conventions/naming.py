
TS_PATTERN = re.compile(r"^[a - z0 - 9\-]+\.tsx?$")  # kebab - case for ts / js files
IGNORE_DIRS = {".git", ".ai_onboard", "ai_onboard", "node_modules", "__pycache__"}


class NamingConventionsPython:
    name = "conv.python_filenames_snake_case"


    def run(self, paths: List[str], ctx: Dict[str, Any]):
        root = ctx["root"]
        issues: List[Issue] = []
        for dirpath, _, filenames in os.walk(root):
            if any(part in IGNORE_DIRS for part in dirpath.split(os.sep)):
                continue
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                if not PY_PATTERN.match(fn):
                    issues.append(
                        Issue(
                            "NAMING_PY_SNAKE_CASE",
                            "warn",
                            f"Python filename should be snake_case: {fn}",
                            os.path.join(dirpath, fn),
                            confidence=0.9,
                        )
                    )
        return issues


class NamingConventionsTS:
    name = "conv.ts_filenames_kebab_case"


    def run(self, paths: List[str], ctx: Dict[str, Any]):
        root = ctx["root"]
        issues: List[Issue] = []
        for dirpath, _, filenames in os.walk(root):
            if any(part in IGNORE_DIRS for part in dirpath.split(os.sep)):
                continue
            for fn in filenames:
                if not (
                    fn.endswith(".ts")
                    or fn.endswith(".tsx")
                    or fn.endswith(".js")
                    or fn.endswith(".jsx")
                ):
                    continue
                if not TS_PATTERN.match(fn):
                    issues.append(
                        Issue(
                            "NAMING_TS_KEBAB_CASE",
                            "warn",
                            f"TypeScript / JS filename should be kebab - case: {fn}",
                            os.path.join(dirpath, fn),
                            confidence=0.85,
                        )
                    )
        return issues


def _register():
    register("library_module", "python", NamingConventionsPython())
    register("ui_frontend", "node_ts", NamingConventionsTS())

_register()
