
class ExamplePolicy:
    name = "example.policy"


    def run(self, paths: List[str], ctx: Dict[str, Any]):
        # No - op example: always returns an info - level issue on first path
        target = (paths or ["."])[0]
        return [
            Issue(
                "EXAMPLE_POLICY", "info", "Example policy ran", target, confidence=0.1
            )
        ]


def _register():
    # Register under a generic component / language pairing for visibility
    register("library_module", "python", ExamplePolicy())

_register()
