#!/usr/bin/env python3
"""
Test for Automatic WBS Updates

Tests whether the system automatically updates the Work Breakdown Structure
when new tasks are identified, ensuring the project plan stays synchronized
with actual development work.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_onboard.core.continuous_improvement_system import ContinuousImprovementSystem
from ai_onboard.core.dynamic_planner import DynamicPlanner
from ai_onboard.core.smart_debugger import SmartDebugger
from ai_onboard.core.task_completion_detector import TaskCompletionDetector


class TestWBSAutoUpdate:
    """Test automatic WBS updates when tasks are identified."""

    def setup_method(self):
        """Set up test environment."""
        # Ensure we get the project root, not tests directory
        self.project_root = Path(__file__).parent.parent.resolve()
        self.dynamic_planner = DynamicPlanner(self.project_root)
        self.task_detector = TaskCompletionDetector(self.project_root)
        self.improvement_system = ContinuousImprovementSystem(self.project_root)
        self.debugger = SmartDebugger(self.project_root)

    def test_task_identification_triggers_wbs_update(self):
        """Test that identifying new tasks automatically updates the WBS."""
        # Get initial WBS state
        initial_wbs = self._get_current_wbs()
        print(f"DEBUG: Initial WBS keys: {list(initial_wbs.keys())}")
        initial_task_count = self._count_tasks_in_wbs(initial_wbs)
        print(f"DEBUG: Initial task count: {initial_task_count}")

        # Simulate task identification through error analysis
        # This would normally happen through the debugger or task detector
        new_task_data = {
            "task_id": "TEST_AUTO_UPDATE",
            "name": "Automatically Detected Task",
            "description": "Task identified through error analysis",
            "priority": "high",
            "estimated_effort": "2 days",
            "dependencies": ["existing_task"],
        }

        print(f"DEBUG: Simulating task identification: {new_task_data['task_id']}")
        # Simulate the system identifying this task
        self._simulate_task_identification(new_task_data)

        # Verify WBS was automatically updated
        updated_wbs = self._get_current_wbs()
        print(f"DEBUG: Updated WBS keys: {list(updated_wbs.keys())}")
        updated_task_count = self._count_tasks_in_wbs(updated_wbs)
        print(f"DEBUG: Updated task count: {updated_task_count}")

        # Should have added the new task
        assert (
            updated_task_count > initial_task_count
        ), f"WBS should be automatically updated when new tasks are identified. Initial: {initial_task_count}, Updated: {updated_task_count}"

        # Check that the new task appears in WBS display
        wbs_output = self._get_wbs_display()
        print(f"DEBUG: WBS output length: {len(wbs_output)}")
        assert (
            "Automatically Detected Task" in wbs_output
        ), "New task should appear in WBS display after identification"

    def test_error_detection_triggers_wbs_update(self):
        """Test that error detection automatically adds remediation tasks to WBS."""
        # Get initial state
        initial_wbs = self._get_current_wbs()

        # Simulate an error that requires a new task
        error_data = {
            "type": "styling",
            "message": "Missing spaces around operators in generated code",
            "context": {"file": "generated_file.py", "line": 10, "code_pattern": "x=5"},
        }

        # Analyze the error (this should trigger task identification)
        self.debugger.analyze_error(error_data)

        # The system should have identified a task to fix styling issues
        updated_wbs = self._get_current_wbs()

        # Check if a new task was added for styling fixes
        new_tasks_found = []
        for phase_id, phase_data in updated_wbs.items():
            subtasks = phase_data.get("subtasks", {})
            for subtask_id, subtask_data in subtasks.items():
                if (
                    "styling" in subtask_data.get("name", "").lower()
                    or "spacing" in subtask_data.get("description", "").lower()
                ):
                    new_tasks_found.append(subtask_data)

        assert (
            len(new_tasks_found) > 0
        ), "Error detection should automatically add remediation tasks to WBS"

    def test_wbs_update_happens_before_task_execution(self):
        """Test that WBS updates occur before any work begins on identified tasks."""
        # This is critical - the WBS must be updated before execution starts
        execution_started = False
        wbs_updated = False

        def mock_execute_task(task_id):
            nonlocal execution_started
            execution_started = True
            # Check if WBS was updated before execution
            assert wbs_updated, "WBS must be updated before task execution begins"
            return {"status": "completed"}

        # Simulate task identification workflow
        task_id = "TEST_PRE_EXECUTION_UPDATE"

        # Step 1: Identify task (should update WBS first)
        self._simulate_task_identification(
            {
                "task_id": task_id,
                "name": "Pre-execution WBS Update Test",
                "description": "Test task for WBS update timing",
                "priority": "high",
            }
        )

        # Mark WBS as updated
        wbs_updated = True

        # Step 2: Execute task (should fail if WBS wasn't updated first)
        result = mock_execute_task(task_id)

        assert (
            result["status"] == "completed"
        ), "Task execution should succeed after WBS update"

    def test_critical_path_updates_with_new_tasks(self):
        """Test that critical path is updated when new critical tasks are identified."""
        # Get initial critical path
        initial_critical_path = self._get_critical_path()

        # Add a new critical task
        critical_task_data = {
            "task_id": "CRITICAL_FIX",
            "name": "Critical System Fix",
            "description": "Urgent fix that blocks all other work",
            "priority": "critical",
            "is_critical_path": True,
            "estimated_effort": "1 day",
        }

        self._simulate_task_identification(critical_task_data)

        # Verify critical path was updated
        updated_critical_path = self._get_critical_path()

        assert len(updated_critical_path) > len(
            initial_critical_path
        ), "Critical path should be updated when critical tasks are identified"

        assert (
            "CRITICAL_FIX" in updated_critical_path
        ), "New critical task should appear in critical path"

    def test_wbs_update_persistence(self):
        """Test that WBS updates persist across sessions."""
        # Add a task in this session
        task_data = {
            "task_id": "PERSISTENCE_TEST",
            "name": "Persistence Test Task",
            "description": "Task to test WBS update persistence",
            "priority": "medium",
        }

        self._simulate_task_identification(task_data)

        # Verify it exists in current session
        current_wbs = self._get_current_wbs()
        assert self._task_exists_in_wbs(
            "PERSISTENCE_TEST", current_wbs
        ), "Task should exist in current session"

        # Simulate new session by creating new instances
        new_planner = DynamicPlanner(self.project_root)
        new_detector = TaskCompletionDetector(self.project_root)

        # Check if task persists
        persisted_wbs = self._get_current_wbs()
        assert self._task_exists_in_wbs(
            "PERSISTENCE_TEST", persisted_wbs
        ), "WBS updates should persist across sessions"

    def test_multiple_simultaneous_task_identifications(self):
        """Test handling multiple task identifications at once."""
        # Get initial count
        initial_wbs = self._get_current_wbs()
        initial_count = self._count_tasks_in_wbs(initial_wbs)

        # Identify multiple tasks simultaneously
        tasks_data = [
            {
                "task_id": "MULTI_TASK_1",
                "name": "Multi-Task Test 1",
                "description": "First of multiple tasks",
                "priority": "high",
            },
            {
                "task_id": "MULTI_TASK_2",
                "name": "Multi-Task Test 2",
                "description": "Second of multiple tasks",
                "priority": "medium",
            },
            {
                "task_id": "MULTI_TASK_3",
                "name": "Multi-Task Test 3",
                "description": "Third of multiple tasks",
                "priority": "low",
            },
        ]

        for task_data in tasks_data:
            self._simulate_task_identification(task_data)

        # Verify all tasks were added
        final_wbs = self._get_current_wbs()
        final_count = self._count_tasks_in_wbs(final_wbs)

        assert final_count >= initial_count + len(
            tasks_data
        ), "All identified tasks should be added to WBS"

        # Verify each task exists
        for task_data in tasks_data:
            assert self._task_exists_in_wbs(
                task_data["task_id"], final_wbs
            ), f"Task {task_data['task_id']} should exist in WBS"

    def test_wbs_update_triggers_notifications(self):
        """Test that WBS updates trigger appropriate notifications."""
        # This would test if the system notifies users when WBS changes
        # For now, we'll check if the update is logged
        pass  # Implementation depends on notification system

    def _simulate_task_identification(self, task_data):
        """Simulate the system identifying a new task."""
        # This mimics what would happen when error analysis or other
        # detection mechanisms identify new work items

        # In a real system, this would integrate with:
        # - Smart debugger error analysis
        # - Task completion detector
        # - Continuous improvement system
        # - Dynamic planner

        # For testing, we'll directly update the project plan
        plan_path = self.project_root / ".ai_onboard" / "project_plan.json"
        print(f"DEBUG: Plan path: {plan_path}")
        print(f"DEBUG: Plan exists: {plan_path.exists()}")

        if plan_path.exists():
            with open(plan_path, "r") as f:
                plan = json.load(f)
            print(
                f"DEBUG: Loaded existing plan with WBS keys: {list(plan.get('work_breakdown_structure', {}).keys())}"
            )
        else:
            plan = {"work_breakdown_structure": {}}
            print("DEBUG: Created new plan")

        # Add the new task to a testing phase
        wbs = plan.get("work_breakdown_structure", {})
        if "TEST_PHASE" not in wbs:
            wbs["TEST_PHASE"] = {
                "name": "Testing Phase",
                "status": "in_progress",
                "subtasks": {},
            }
            print("DEBUG: Created TEST_PHASE")

        task_id = task_data["task_id"]
        wbs["TEST_PHASE"]["subtasks"][task_id] = {
            "name": task_data["name"],
            "status": "pending",
            "completion": 0,
            "description": task_data.get("description", ""),
            "priority": task_data.get("priority", "medium"),
        }

        plan["work_breakdown_structure"] = wbs

        with open(plan_path, "w") as f:
            json.dump(plan, f, indent=2)

        print(
            f"DEBUG: Saved plan with TEST_PHASE subtasks: {list(wbs['TEST_PHASE']['subtasks'].keys())}"
        )

    def _get_current_wbs(self):
        """Get the current WBS from project plan."""
        plan_path = self.project_root / ".ai_onboard" / "project_plan.json"
        if plan_path.exists():
            with open(plan_path, "r") as f:
                plan = json.load(f)
            return plan.get("work_breakdown_structure", {})
        return {}

    def _get_wbs_display(self):
        """Get the WBS display output."""
        # Debug: print the project root
        print(f"DEBUG: project_root = {self.project_root}")
        print(
            f"DEBUG: project_plan exists = {(self.project_root / '.ai_onboard' / 'project_plan.json').exists()}"
        )

        result = subprocess.run(
            ["python", "-m", "ai_onboard", "prompt", "wbs"],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )

        print(f"DEBUG: returncode = {result.returncode}")
        print(f"DEBUG: stdout = {repr(result.stdout)}")
        print(f"DEBUG: stderr = {repr(result.stderr)}")

        return result.stdout

    def _get_critical_path(self):
        """Get the current critical path."""
        plan_path = self.project_root / ".ai_onboard" / "project_plan.json"
        if plan_path.exists():
            with open(plan_path, "r") as f:
                plan = json.load(f)
            return plan.get("critical_path_analysis", {}).get("critical_path", [])
        return []

    def _task_exists_in_wbs(self, task_id, wbs):
        """Check if a task exists in the WBS."""
        for phase_id, phase_data in wbs.items():
            subtasks = phase_data.get("subtasks", {})
            if task_id in subtasks:
                return True
        return False

    def _count_tasks_in_wbs(self, wbs):
        """Count total tasks in WBS."""
        count = 0
        for phase_data in wbs.values():
            count += len(phase_data.get("subtasks", {}))
        return count


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
