"""Task completion detector compatibility shim."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from warnings import warn

from .pm_compatibility import get_legacy_task_completion_detector


class TaskCompletionDetector:
    """Deprecated facade delegating to unified project management engine."""

    def __init__(self, project_root: Path):
        warn(
            "TaskCompletionDetector is deprecated; use pm_compatibility.get_legacy_task_completion_detector",
            DeprecationWarning,
            stacklevel=2,
        )
        self._delegate = get_legacy_task_completion_detector(project_root)

    def detect_completed_tasks(self) -> Dict[str, Any]:
        warn(
            "TaskCompletionDetector.detect_completed_tasks is deprecated",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._delegate.detect_completed_tasks()


def run_task_completion_scan(project_root: Path) -> Dict[str, Any]:
    warn(
        "run_task_completion_scan is deprecated; use pm_compatibility.get_legacy_task_completion_detector",
        DeprecationWarning,
        stacklevel=2,
    )
    detector = get_legacy_task_completion_detector(project_root)
    return detector.detect_completed_tasks()
