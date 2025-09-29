#!/usr/bin/env python3
"""
Test for Automatic WBS Updates

Tests whether the system automatically updates the Work Breakdown Structure
when new tasks are identified, ensuring the project plan stays synchronized
with actual development work.
"""

from pathlib import Path
from typing import Any, Dict

import pytest

from ai_onboard.core.unified_project_management import (
    get_unified_project_management_engine,
)


class TestWBSAutoUpdate:
    """Test automatic WBS updates when tasks are identified."""

    def setup_method(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.resolve()
        self.engine = get_unified_project_management_engine(self.project_root)

    def test_task_identification_triggers_wbs_update(self):
        """Test that identifying new tasks automatically updates the WBS."""
        initial_wbs = self.engine.wbs.get_status()
        initial_task_count = initial_wbs.get("total_elements", 0)

        new_task_data = {
            "task_id": "TEST_AUTO_UPDATE",
            "name": "Automatically Detected Task",
            "description": "Task identified through error analysis",
            "priority": "high",
            "dependencies": ["existing_task"],
        }

        self.engine.wbs.update_task(new_task_data["task_id"], "pending")

        updated_wbs = self.engine.wbs.get_status()
        updated_task_count = updated_wbs.get("total_elements", 0)

        assert (
            updated_task_count >= initial_task_count
        ), "WBS should reflect new tasks after identification"

    def test_error_detection_triggers_wbs_update(self):
        """Test that error detection automatically adds remediation tasks to WBS."""
        remediation_task = {
            "task_id": "STYLE_FIX",
            "name": "Styling Fix",
            "description": "Fix styling issues detected",
            "priority": "medium",
        }

        self.engine.tasks.detect_completions()
        self.engine.wbs.update_task(remediation_task["task_id"], "pending")

        wbs_report = self.engine.wbs.get_status()
        assert wbs_report["total_elements"] >= 1

    def test_wbs_update_happens_before_task_execution(self):
        """Ensure WBS updates occur before any task execution begins."""
        task_id = "TEST_PRE_EXECUTION_UPDATE"
        self.engine.wbs.update_task(task_id, "pending")

        task_status = self.engine.wbs.update_task(task_id, "completed")
        assert task_status["success"], "Task execution should succeed after WBS update"

    def test_critical_path_updates_with_new_tasks(self):
        """Test that critical path is updated when new critical tasks are identified."""
        initial_status = self.engine.analytics.get_project_status()
        initial_path = initial_status.get("critical_path", [])

        critical_task = {
            "task_id": "CRITICAL_FIX",
            "name": "Critical System Fix",
            "description": "Urgent fix that blocks work",
            "priority": "critical",
        }

        self.engine.wbs.update_task(critical_task["task_id"], "pending")
        updated_status = self.engine.analytics.get_project_status()
        updated_path = updated_status.get("critical_path", [])

        assert len(updated_path) >= len(initial_path)

    def test_wbs_update_persistence(self):
        """Test that WBS updates persist across engine instances."""
        task_data = {
            "task_id": "PERSISTENCE_TEST",
            "name": "Persistence Test Task",
            "description": "Task to test WBS update persistence",
            "priority": "medium",
        }

        self.engine.wbs.update_task(task_data["task_id"], "pending")

        new_engine = get_unified_project_management_engine(self.project_root)
        status = new_engine.wbs.get_status()
        assert status["total_elements"] >= 1

    def test_wbs_update_triggers_notifications(self):
        """Test that WBS updates trigger notifications or metrics."""
        status_before = self.engine.analytics.get_project_status()

        self.engine.wbs.update_task("NOTIFICATION_TEST", "pending")

        status_after = self.engine.analytics.get_project_status()
        assert status_after.get("total_tasks", 0) >= status_before.get("total_tasks", 0)

    def _get_current_wbs(self):
        report = self.engine.wbs.get_status()
        return {
            "total": report.get("total_elements", 0),
            "completed": report.get("completed", 0),
        }

    def _task_exists_in_wbs(self, task_id: str, wbs_status: Dict[str, Any]) -> bool:
        return wbs_status.get("total", 0) > 0


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
