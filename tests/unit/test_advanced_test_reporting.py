"""Unit tests for unified project management reporting and telemetry."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_onboard.core.pm_compatibility import (
    get_legacy_progress_dashboard,
    get_legacy_task_completion_detector,
    get_legacy_task_prioritization_engine,
    get_legacy_wbs_sync_engine,
)
from ai_onboard.core.tool_usage_tracker import get_tool_tracker
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


class TestUnifiedProjectManagementReporting:
    """Validate analytics and task reporting for the unified engine."""

    def test_engine_initialization(self, project_root: Path) -> None:
        engine = get_unified_project_management_engine(project_root)

        assert isinstance(engine, UnifiedProjectManagementEngine)
        assert engine.root_path == project_root
        assert engine.gateway.plan_dir == project_root / ".ai_onboard"

    def test_task_prioritization_report(self, project_root: Path) -> None:
        engine = get_unified_project_management_engine(project_root)
        result = engine.tasks.prioritize_tasks()

        assert result["total_tasks"] == 3
        priorities = result["task_priorities"]
        assert {"phase1", "phase1.1", "phase1.2"}.issubset(priorities.keys())
        assert priorities["phase1"]["calculated_priority"] in {"low", "medium", "high"}

    def test_task_completion_updates_plan(self, project_root: Path) -> None:
        engine = get_unified_project_management_engine(project_root)
        result = engine.tasks.detect_completions()

        assert result["total_tasks"] == 3
        assert result["newly_completed"]  # should record at least one completion
        refreshed_plan = engine.gateway.load_project_plan(force_reload=True).raw
        completed_task = refreshed_plan["work_breakdown_structure"]["phase1"][
            "subtasks"
        ]["1"]
        assert completed_task["status"] == "completed"
        # ensure completion metadata is captured via result payload
        assert any(entry["task_id"] == "phase1.1" for entry in result["new_completions"])  # type: ignore[index]

    def test_wbs_status_report(self, project_root: Path) -> None:
        engine = get_unified_project_management_engine(project_root)
        status = engine.wbs.get_status()

        assert status["total_elements"] == 1
        assert "consistency_score" in status
        assert "hierarchy_summary" in status

    def test_progress_dashboard_report(self, project_root: Path) -> None:
        engine = get_unified_project_management_engine(project_root)
        dashboard = engine.analytics.get_project_status()

        assert dashboard["project_name"] == "Test Project"
        assert "total_tasks" in dashboard
        assert isinstance(dashboard["milestones"], list)

    def test_compatibility_wrappers_delegate(self, project_root: Path) -> None:
        with pytest.warns(DeprecationWarning):
            prioritizer = get_legacy_task_prioritization_engine(project_root)
            result = prioritizer.prioritize_all_tasks()
            assert result["total_tasks"] == 3

        with pytest.warns(DeprecationWarning):
            detector = get_legacy_task_completion_detector(project_root)
            result = detector.detect_completed_tasks()
            assert result["total_tasks"] == 3

        with pytest.warns(DeprecationWarning):
            wbs_engine = get_legacy_wbs_sync_engine(project_root)
            status = wbs_engine.get_wbs_status()
            assert status["total_elements"] == 1

        with pytest.warns(DeprecationWarning):
            dashboard = get_legacy_progress_dashboard(project_root)
            status = dashboard.generate_dashboard()
            assert status["project_name"] == "Test Project"

    def test_telemetry_logging(
        self, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(project_root)
        tracker = get_tool_tracker(project_root)
        tracker.start_task_session("test_upme")

        engine = get_unified_project_management_engine(project_root)
        engine.tasks.prioritize_tasks()
        engine.tasks.detect_completions()
        engine.wbs.get_status()
        engine.analytics.get_project_status()

        tracker.end_task_session()

        log_path = project_root / ".ai_onboard" / "tool_usage.jsonl"
        assert log_path.exists()

        payloads = [
            json.loads(line)
            for line in log_path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        assert payloads, "Expected telemetry entries to be recorded"
        tool_names = {entry["tool_name"] for entry in payloads}
        assert "unified_project_management" in tool_names


@pytest.mark.integration
class TestUnifiedProjectManagementIntegration:
    """Integration checks covering end-to-end reporting persistence."""

    def test_report_persistence(self, project_root: Path) -> None:
        engine = get_unified_project_management_engine(project_root)
        result = engine.tasks.detect_completions()

        assert result["total_tasks"] == 3
        refreshed_plan = engine.gateway.load_project_plan(force_reload=True).raw
        completed_task = refreshed_plan["work_breakdown_structure"]["phase1"][
            "subtasks"
        ]["1"]
        assert completed_task["status"] == "completed"
        assert any(entry["task_id"] == "phase1.1" for entry in result["new_completions"])  # type: ignore[index]
