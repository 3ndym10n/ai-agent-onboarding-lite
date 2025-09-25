"""Unit tests for Unified Project Management telemetry trend analysis."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

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


class TestUnifiedPMTelemetry:
    """Verify telemetry data emitted by the unified project management engine."""

    def test_single_session_telemetry(
        self, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(project_root)
        tracker = get_tool_tracker(project_root)
        tracker.start_task_session("telemetry_single")
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

        assert payloads
        tool_names = {entry["tool_name"] for entry in payloads}
        assert tool_names == {"unified_project_management"}

    def test_repeated_calls_accumulate_entries(
        self, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(project_root)
        tracker = get_tool_tracker(project_root)
        tracker.start_task_session("telemetry_repeat")
        engine = get_unified_project_management_engine(project_root)

        for _ in range(5):
            engine.tasks.prioritize_tasks()
            engine.analytics.get_project_status()

        tracker.end_task_session()

        log_path = project_root / ".ai_onboard" / "tool_usage.jsonl"
        assert log_path.exists()
        payloads = [
            json.loads(line)
            for line in log_path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        assert len(payloads) >= 5
        timestamps = [entry.get("timestamp") for entry in payloads]
        assert all(isinstance(ts, str) and ts for ts in timestamps)
        assert len(set(timestamps)) >= 1

    def test_recent_activity_truncation(self, project_root: Path) -> None:
        events_path = project_root / ".ai_onboard" / "learning_events.jsonl"
        events_path.parent.mkdir(parents=True, exist_ok=True)
        events_path.write_text(
            "\n".join(
                json.dumps({"timestamp": datetime.now().isoformat(), "id": idx})
                for idx in range(10)
            )
            + "\n",
            encoding="utf-8",
        )
        engine = get_unified_project_management_engine(project_root)
        recent = engine.analytics.get_project_status()["recent_activity"]
        assert len(recent) <= 5


@pytest.mark.integration
class TestUnifiedPMTelemetryIntegration:
    """Integration checks ensuring telemetry logs persist."""

    def test_tool_usage_log_exists(
        self, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(project_root)
        tracker = get_tool_tracker(project_root)
        tracker.start_task_session("telemetry_integration")
        engine = get_unified_project_management_engine(project_root)
        engine.analytics.get_project_status()
        tracker.end_task_session()
        log_path = project_root / ".ai_onboard" / "tool_usage.jsonl"
        assert log_path.exists()
        assert log_path.read_text(encoding="utf-8").strip()
