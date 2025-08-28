from typing import Protocol, List, Dict, Any
from .issue import Issue

class CheckPlugin(Protocol):
    name: str
    def run(self, paths: List[str], ctx: Dict[str, Any]) -> List[Issue]: ...

REGISTRY: dict[tuple[str,str], list[CheckPlugin]] = {}

def register(component_type: str, language: str, plugin: CheckPlugin):
    REGISTRY.setdefault((component_type, language), []).append(plugin)
