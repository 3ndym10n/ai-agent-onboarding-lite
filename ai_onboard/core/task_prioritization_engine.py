"""Task prioritization engine compatibility shim."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from warnings import warn

from .pm_compatibility import get_legacy_task_prioritization_engine


class TaskPrioritizationEngine:
    """Deprecated facade delegating to unified project management engine."""

    def __init__(self, root: Path):
        warn(
            "TaskPrioritizationEngine is deprecated; use pm_compatibility.get_legacy_task_prioritization_engine",
            DeprecationWarning,
            stacklevel=2,
        )
        self._delegate = get_legacy_task_prioritization_engine(root)

    def prioritize_all_tasks(self) -> Dict[str, Any]:
        warn(
            "TaskPrioritizationEngine.prioritize_all_tasks is deprecated",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._delegate.prioritize_all_tasks()

    def get_task_priorities(self) -> Dict[str, Any]:
        warn(
            "TaskPrioritizationEngine.get_task_priorities is deprecated",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._delegate.prioritize_all_tasks()
