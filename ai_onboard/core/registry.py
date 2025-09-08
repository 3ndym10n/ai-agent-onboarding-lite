from typing import Any, Dict, List, Protocol, Tuple

from .issue import Issue


class CheckPlugin(Protocol):
    name: str

    def run(self, paths: List[str], ctx: Dict[str, Any]) -> List[Issue]: ...


REGISTRY: Dict[Tuple[str, str], List[CheckPlugin]] = {}


def register(component_type: str, language: str, plugin: CheckPlugin):
    REGISTRY.setdefault((component_type, language), []).append(plugin)
