"""Backward compatibility wrappers for legacy project management modules."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Dict, Optional

from .unified_project_management import (
    UnifiedProjectManagementEngine,
    get_unified_project_management_engine,
)


class LegacyTaskPrioritizationEngine:
    """Wrapper exposing legacy TaskPrioritizationEngine API."""

    def __init__(self, root: Path):
        self._engine = get_unified_project_management_engine(root)

    def prioritize_all_tasks(self) -> Dict[str, Any]:
        warnings.warn(
            "TaskPrioritizationEngine is deprecated; use UnifiedProjectManagementEngine.tasks",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._engine.tasks.prioritize_tasks()


class LegacyTaskCompletionDetector:
    """Wrapper exposing legacy TaskCompletionDetector API."""

    def __init__(self, root: Path):
        self._engine = get_unified_project_management_engine(root)

    def detect_completed_tasks(self) -> Dict[str, Any]:
        warnings.warn(
            "TaskCompletionDetector is deprecated; use UnifiedProjectManagementEngine.tasks",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._engine.tasks.detect_completions()


class LegacyWBSSynchronizationEngine:
    """Wrapper exposing legacy WBS synchronization API."""

    def __init__(self, root: Path):
        self._engine = get_unified_project_management_engine(root)

    def get_wbs_status(self) -> Dict[str, Any]:
        warnings.warn(
            "WBSSynchronizationEngine is deprecated; use UnifiedProjectManagementEngine.wbs",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._engine.wbs.get_status()

    def update_task(self, task_id: str, status: str) -> Dict[str, Any]:
        warnings.warn(
            "WBSSynchronizationEngine.update_task is deprecated; use UnifiedProjectManagementEngine.wbs.update_task",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._engine.wbs.update_task(task_id, status)


class LegacyProgressDashboard:
    """Wrapper exposing legacy progress dashboard API."""

    def __init__(self, root: Path):
        self._engine = get_unified_project_management_engine(root)

    def generate_dashboard(self) -> Dict[str, Any]:
        warnings.warn(
            "ProgressDashboard is deprecated; use UnifiedProjectManagementEngine.analytics",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._engine.analytics.get_project_status()


def get_legacy_task_prioritization_engine(root: Path) -> LegacyTaskPrioritizationEngine:
    return LegacyTaskPrioritizationEngine(root)


def get_legacy_task_completion_detector(root: Path) -> LegacyTaskCompletionDetector:
    return LegacyTaskCompletionDetector(root)


def get_legacy_wbs_sync_engine(root: Path) -> LegacyWBSSynchronizationEngine:
    return LegacyWBSSynchronizationEngine(root)


def get_legacy_progress_dashboard(root: Path) -> LegacyProgressDashboard:
    return LegacyProgressDashboard(root)

