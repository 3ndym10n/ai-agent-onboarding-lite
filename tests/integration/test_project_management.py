"""Integration tests for unified project management engine and compatibility layer."""

import json
from pathlib import Path

import pytest

from ai_onboard.core.pm_compatibility import (
    get_legacy_progress_dashboard,
    get_legacy_task_completion_detector,
    get_legacy_task_prioritization_engine,
    get_legacy_wbs_sync_engine,
)
from ai_onboard.core.unified_project_management import (
    UnifiedProjectManagementEngine,
    get_unified_project_management_engine,
)


@pytest.fixture()
def project_root(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    (root / ".ai_onboard").mkdir(parents=True, exist_ok=True)
    plan = {
        "project_id": "demo",
        "project_name": "Test Project",
        "work_breakdown_structure": {
            "phase1": {
                "name": "Phase 1",
                "status": "in_progress",
                "completion_percentage": 40,
                "subtasks": {
                    "1": {"name": "Task 1", "status": "completed"},
                    "2": {"name": "Task 2", "status": "in_progress"},
                },
            }
        },
        "milestones": [
            {
                "id": "m1",
                "name": "Milestone",
                "status": "in_progress",
                "completion_percentage": 50,
            }
        ],
        "critical_path": ["phase1"],
    }
    (root / ".ai_onboard" / "project_plan.json").write_text(
        json.dumps(plan, indent=2), encoding="utf-8"
    )
    return root


def test_unified_engine_singleton(project_root: Path):
    engine_a = get_unified_project_management_engine(project_root)
    engine_b = get_unified_project_management_engine(project_root)
    assert engine_a is engine_b


def test_task_prioritization_compat_layer(project_root: Path):
    engine = get_legacy_task_prioritization_engine(project_root)
    with pytest.warns(DeprecationWarning):
        result = engine.prioritize_all_tasks()
    assert result["total_tasks"] == 3
    assert "task_priorities" in result


def test_task_completion_compat_layer(project_root: Path):
    engine = get_legacy_task_completion_detector(project_root)
    with pytest.warns(DeprecationWarning):
        result = engine.detect_completed_tasks()
    assert result["total_tasks"] == 3


def test_wbs_status_compat_layer(project_root: Path):
    engine = get_legacy_wbs_sync_engine(project_root)
    with pytest.warns(DeprecationWarning):
        status = engine.get_wbs_status()
    assert status["total_elements"] == 1


def test_progress_dashboard_compat_layer(project_root: Path):
    dashboard = get_legacy_progress_dashboard(project_root)
    with pytest.warns(DeprecationWarning):
        status = dashboard.generate_dashboard()
    assert status["project_name"] == "Test Project"
