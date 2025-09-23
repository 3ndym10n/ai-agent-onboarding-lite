"""
WBS Update Engine - Applies task integration recommendations to the project plan.

This module handles the actual modification of the Work Breakdown Structure (WBS)
based on task integration recommendations from the TaskIntegrationLogic.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import utils
from .task_integration_logic import integrate_task
from .tool_usage_tracker import track_tool_usage
from .wbs_synchronization_engine import get_wbs_sync_engine


class WBSUpdateEngine:
    """Engine for updating the Work Breakdown Structure based on task integration."""


    def __init__(self, root: Path):
        self.root = root
        self.project_plan_path = root / ".ai_onboard" / "project_plan.json"
        self.backup_dir = root / ".ai_onboard" / "wbs_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)


    def apply_task_integration(
        self, task_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Apply task integration recommendations to the project plan.

        Args:
            task_data: Task information to integrate
            context: Additional context for integration

        Returns:
            Update result with success status and details
        """
        track_tool_usage(
            "wbs_update_engine",
            "project_management",
            {"action": "apply_integration", "task_name": task_data.get("name")},
            "success",
        )

        # First, get integration recommendations
        integration_result = integrate_task(task_data, context, self.root)

        if integration_result["confidence_score"] < 0.5:
            return {
                "success": False,
                "reason": "low_confidence",
                "confidence": integration_result["confidence_score"],
                "message": "Integration confidence too low - manual review required",
            }

        # Get synchronization engine
        sync_engine = get_wbs_sync_engine(self.root)

        try:
            # Apply the integration through synchronization engine
            update_result = self._apply_integration_updates_through_sync(
                integration_result, sync_engine
            )

            if update_result["success"]:
                # Update project metadata
                self._update_project_metadata(update_result)

                return {
                    "success": True,
                    "task_id": update_result["task_id"],
                    "phase_updated": update_result["phase"],
                    "update_type": update_result["update_type"],
                    "affected_views": update_result.get("affected_views", []),
                    "message": f"Successfully integrated task into WBS",
                }
            else:
                # Restore backup on failure
                self._restore_backup(backup_path)
                return {
                    "success": False,
                    "reason": "update_failed",
                    "error": update_result.get("error", "Unknown error"),
                    "backup_restored": True,
                }

        except Exception as e:
            # Restore backup on exception
            self._restore_backup(backup_path)
            return {
                "success": False,
                "reason": "exception",
                "error": str(e),
                "backup_restored": True,
            }


    def _apply_integration_updates_through_sync(
        self, integration_result: Dict[str, Any], sync_engine
    ) -> Dict[str, Any]:
        """Apply integration updates through the synchronization engine."""
        # Get current WBS data through sync engine
        wbs_data = sync_engine.get_wbs_data("default", use_cache=False)

        if "work_breakdown_structure" not in wbs_data:
            return {"success": False, "error": "No WBS found in project plan"}

        wbs = wbs_data["work_breakdown_structure"]
        placement = integration_result["placement_recommendation"]
        plan = integration_result["integration_plan"]

        phase_id = placement["recommended_phase"]
        update_type = placement["placement_type"]

        # Validate phase exists
        if phase_id not in wbs:
            return {"success": False, "error": f"Phase {phase_id} not found in WBS"}

        if update_type == "new_subtask":
            result = self._add_new_subtask(wbs, phase_id, placement, plan)
        elif update_type == "modify_existing":
            result = self._modify_existing_subtask(wbs, placement, plan)
        elif update_type == "new_phase":
            result = self._add_new_phase(wbs, phase_id, placement, plan)
        else:
            return {"success": False, "error": f"Unknown update type: {update_type}"}

        if result["success"]:
            # Prepare updates for synchronization engine
            updates = {"work_breakdown_structure": wbs, "last_updated": utils.now_iso()}

            # Apply updates through sync engine
            sync_result = sync_engine.update_wbs_data(updates, "wbs_update_engine")

            if sync_result["success"]:
                return {
                    "success": True,
                    "task_id": plan["task_id"],
                    "phase": phase_id,
                    "update_type": update_type,
                    "affected_views": sync_result.get("affected_views", []),
                    **result,
                }
            else:
                return {
                    "success": False,
                    "error": f"Sync update failed: {sync_result.get('error')}",
                }
        else:
            return result


    def _apply_integration_updates(
        self, integration_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply the actual integration updates to the project plan."""
        plan_data = utils.read_json(self.project_plan_path, default={})

        if "work_breakdown_structure" not in plan_data:
            return {"success": False, "error": "No WBS found in project plan"}

        wbs = plan_data["work_breakdown_structure"]
        placement = integration_result["placement_recommendation"]
        plan = integration_result["integration_plan"]

        phase_id = placement["recommended_phase"]
        update_type = placement["placement_type"]

        # Validate phase exists
        if phase_id not in wbs:
            return {"success": False, "error": f"Phase {phase_id} not found in WBS"}

        if update_type == "new_subtask":
            result = self._add_new_subtask(wbs, phase_id, placement, plan)
        elif update_type == "modify_existing":
            result = self._modify_existing_subtask(wbs, placement, plan)
        elif update_type == "new_phase":
            result = self._add_new_phase(wbs, phase_id, placement, plan)
        else:
            return {"success": False, "error": f"Unknown update type: {update_type}"}

        if result["success"]:
            # Save the updated plan
            plan_data["work_breakdown_structure"] = wbs
            plan_data["last_updated"] = utils.now_iso()

            utils.write_json(self.project_plan_path, plan_data)

            return {
                "success": True,
                "task_id": plan["task_id"],
                "phase": phase_id,
                "update_type": update_type,
                **result,
            }
        else:
            return result


    def _add_new_subtask(
        self,
        wbs: Dict[str, Any],
        phase_id: str,
        placement: Dict[str, Any],
        plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add a new subtask to an existing phase."""
        phase = wbs[phase_id]

        # Ensure subtasks exist
        if "subtasks" not in phase:
            phase["subtasks"] = {}

        subtasks = phase["subtasks"]
        subtask_id = placement["placement_details"]["subtask_id"]

        # Check if subtask already exists
        if subtask_id in subtasks:
            return {"success": False, "error": f"Subtask {subtask_id} already exists"}

        # Create the new subtask
        subtask_data = {
            "name": plan["task_name"],
            "status": "pending",
            "completion": 0,
            "description": plan["task_description"],
            "estimated_effort": plan["estimated_effort"],
            "priority": plan["priority"],
            "required_skills": plan["required_skills"],
            "dependencies": plan["dependencies"],
            "created_by_integration": True,
            "integration_date": utils.now_iso(),
            "confidence_score": plan.get("confidence_score", 0),
        }

        subtasks[subtask_id] = subtask_data

        # Update phase completion percentage (slight decrease due to new work)
        current_completion = phase.get("completion_percentage", 100)
        if current_completion > 0:
            phase["completion_percentage"] = max(0, current_completion - 5)

        return {"success": True, "subtask_id": subtask_id}


    def _modify_existing_subtask(
        self, wbs: Dict[str, Any], placement: Dict[str, Any], plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Modify an existing subtask to include the new task."""
        existing_subtask_id = placement["placement_details"]["existing_subtask"]

        # Find the subtask across all phases
        for phase_id, phase_data in wbs.items():
            if (
                "subtasks" in phase_data
                and existing_subtask_id in phase_data["subtasks"]
            ):
                subtask = phase_data["subtasks"][existing_subtask_id]

                # Update subtask description to include new task
                current_desc = subtask.get("description", "")
                new_desc = (
                    f"{current_desc}\n- {plan['task_name']}: {plan['task_description']}"
                )

                subtask["description"] = new_desc
                subtask["last_modified"] = utils.now_iso()
                subtask["integrated_tasks"] = subtask.get("integrated_tasks", [])
                subtask["integrated_tasks"].append(
                    {
                        "task_name": plan["task_name"],
                        "task_id": plan["task_id"],
                        "added_date": utils.now_iso(),
                    }
                )

                # Slightly decrease completion if it was high
                current_completion = subtask.get("completion", 0)
                if current_completion > 80:
                    subtask["completion"] = max(0, current_completion - 10)

                return {
                    "success": True,
                    "modified_subtask": existing_subtask_id,
                    "phase": phase_id,
                }

        return {
            "success": False,
            "error": f"Could not find subtask {existing_subtask_id}",
        }


    def _add_new_phase(
        self,
        wbs: Dict[str, Any],
        phase_id: str,
        placement: Dict[str, Any],
        plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add a new phase to the WBS."""
        # This is more complex and should be rare
        # For now, we'll create a basic phase structure

        new_phase_data = {
            "name": f"Auto-generated Phase {phase_id}",
            "status": "pending",
            "completion_percentage": 0,
            "deliverables": [f"Deliver {plan['task_name']}"],
            "description": f"Auto-generated phase for integrated task: {plan['task_description']}",
            "subtasks": {
                f"{phase_id}.1": {
                    "name": plan["task_name"],
                    "status": "pending",
                    "completion": 0,
                    "description": plan["task_description"],
                    "estimated_effort": plan["estimated_effort"],
                    "priority": plan["priority"],
                    "required_skills": plan["required_skills"],
                    "dependencies": plan["dependencies"],
                    "created_by_integration": True,
                    "integration_date": utils.now_iso(),
                }
            },
        }

        wbs[phase_id] = new_phase_data

        return {"success": True, "new_phase": phase_id}


    def _update_project_metadata(self, update_result: Dict[str, Any]) -> None:
        """Update project metadata after successful integration."""
        plan_data = utils.read_json(self.project_plan_path, default={})

        # Update overall completion percentage (slight decrease due to new work)
        current_completion = plan_data.get("executive_summary", {}).get(
            "completion_percentage", 100
        )
        if current_completion > 0:
            plan_data["executive_summary"]["completion_percentage"] = max(
                0, current_completion - 2
            )

        # Add to next actions if high priority
        if update_result.get("priority") in ["critical", "high"]:
            next_actions = plan_data.get("next_actions", [])
            next_actions.append(
                {
                    "priority": update_result.get("priority", "medium"),
                    "action": f"Execute integrated task: {update_result.get('task_name', 'Unknown')}",
                    "owner": "AI Assistant",
                    "due_date": utils.now_iso(),  # Immediate attention needed
                    "dependencies": [],
                    "task_id": update_result.get("task_id", "unknown"),
                    "created_by_integration": True,
                }
            )
            plan_data["next_actions"] = next_actions[:10]  # Keep only latest 10

        # Update last updated timestamp
        plan_data["last_updated"] = utils.now_iso()

        utils.write_json(self.project_plan_path, plan_data)


    def _create_backup(self) -> Path:
        """Create a backup of the current project plan."""
        timestamp = (
            utils.now_iso()
            .replace(":", "")
            .replace("-", "")
            .replace("+", "_")
            .replace("Z", "")
        )
        backup_path = self.backup_dir / f"project_plan_backup_{timestamp}.json"

        plan_data = utils.read_json(self.project_plan_path, default={})
        utils.write_json(backup_path, plan_data)

        return backup_path


    def _restore_backup(self, backup_path: Path) -> bool:
        """Restore project plan from backup."""
        try:
            backup_data = utils.read_json(backup_path, default={})
            utils.write_json(self.project_plan_path, backup_data)
            return True
        except Exception:
            return False


    def validate_wbs_integrity(self) -> Dict[str, Any]:
        """Validate the integrity of the WBS after updates."""
        plan_data = utils.read_json(self.project_plan_path, default={})
        wbs = plan_data.get("work_breakdown_structure", {})

        issues = []

        # Check for required fields
        for phase_id, phase_data in wbs.items():
            if "name" not in phase_data:
                issues.append(f"Phase {phase_id} missing name")
            if "status" not in phase_data:
                issues.append(f"Phase {phase_id} missing status")
            if "subtasks" in phase_data:
                for subtask_id, subtask_data in phase_data["subtasks"].items():
                    if "name" not in subtask_data:
                        issues.append(f"Subtask {subtask_id} missing name")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "phase_count": len(wbs),
            "total_subtasks": sum(
                len(phase.get("subtasks", {})) for phase in wbs.values()
            ),
        }


    def get_integration_history(self) -> List[Dict[str, Any]]:
        """Get history of all integration operations."""
        history_file = self.backup_dir / "integration_history.jsonl"

        if not history_file.exists():
            return []

        history = []
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            history.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception:
            pass

        return history


    def record_integration_operation(self, operation_data: Dict[str, Any]) -> None:
        """Record an integration operation for audit purposes."""
        history_file = self.backup_dir / "integration_history.jsonl"

        record = {"timestamp": utils.now_iso(), **operation_data}

        try:
            with open(history_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            pass  # Best effort - don't fail the integration


def update_wbs_for_task(
    task_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Convenience function to update WBS for a task."""
    if root is None:
        root = Path.cwd()

    engine = WBSUpdateEngine(root)
    result = engine.apply_task_integration(task_data, context)

    # Record the operation
    engine.record_integration_operation(
        {
            "operation": "task_integration",
            "task_name": task_data.get("name", "unknown"),
            "success": result["success"],
            "result": result,
        }
    )

    return result
