"""
WBS Update Engine - Applies task integration recommendations to the project plan.

This module handles the actual modification of the Work Breakdown Structure (WBS)
based on task integration recommendations from the TaskIntegrationLogic.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from warnings import warn

from . import utils
from .pm_compatibility import get_legacy_wbs_sync_engine
from .task_integration_logic import integrate_task
from .tool_usage_tracker import track_tool_usage


class WBSUpdateEngine:
    """Deprecated shim delegating to unified PM engine with legacy helpers."""

    def __init__(self, root: Path):
        warn(
            "WBSUpdateEngine is deprecated; use UnifiedProjectManagementEngine",
            DeprecationWarning,
            stacklevel=2,
        )
        self.root = root
        self.project_plan_path = root / ".ai_onboard" / "project_plan.json"
        self.sync_engine = get_legacy_wbs_sync_engine(root)

    def apply_task_integration(
        self, task_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        warn(
            "WBSUpdateEngine.apply_task_integration is deprecated",
            DeprecationWarning,
            stacklevel=2,
        )
        track_tool_usage(
            "wbs_update_engine",
            "project_management",
            {"action": "apply_integration", "task_name": task_data.get("name")},
            "success",
        )

        integration_result = integrate_task(task_data, context, self.root)
        result = self._apply_integration_updates(integration_result)
        self._update_project_metadata(result)
        self.record_integration_operation(result)
        return result

    def _apply_integration_updates(
        self, integration_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        placement = integration_result.get("placement_recommendation", {})
        plan_data = utils.read_json(self.project_plan_path, default={})
        wbs = plan_data.setdefault("work_breakdown_structure", {})

        if placement.get("action") == "add_new_subtask":
            return self._add_new_subtask(plan_data, wbs, placement)
        if placement.get("action") == "update_existing_subtask":
            return self._modify_existing_subtask(wbs, placement, plan_data)
        if placement.get("action") == "add_new_phase":
            return self._add_new_phase(plan_data, wbs, placement)
        return {"success": False, "message": "no_action"}

    def _add_new_subtask(
        self,
        plan_data: Dict[str, Any],
        wbs: Dict[str, Any],
        placement: Dict[str, Any],
    ) -> Dict[str, Any]:
        phase_id = placement.get("phase_id")
        if not phase_id or phase_id not in wbs:
            return {"success": False, "message": "invalid_phase"}
        phase = wbs[phase_id]
        subtasks = phase.setdefault("subtasks", {})
        subtask_id = placement.get("subtask_id") or utils.generate_id()
        subtasks[subtask_id] = placement.get("task_data", {})
        self._write_plan(plan_data)
        return {"success": True, "subtask_id": f"{phase_id}.{subtask_id}"}

    def _modify_existing_subtask(
        self, wbs: Dict[str, Any], placement: Dict[str, Any], plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        target_id = placement.get("subtask_id")
        if not target_id:
            return {"success": False, "message": "missing_subtask"}
        for phase_id, phase in wbs.items():
            subtasks = phase.get("subtasks", {})
            if target_id in subtasks:
                subtasks[target_id].update(placement.get("task_data", {}))
                self._write_plan(plan)
                return {"success": True, "subtask_id": f"{phase_id}.{target_id}"}
        return {"success": False, "message": "subtask_not_found"}

    def _add_new_phase(
        self,
        plan_data: Dict[str, Any],
        wbs: Dict[str, Any],
        placement: Dict[str, Any],
    ) -> Dict[str, Any]:
        phase_id = placement.get("phase_id") or f"phase_{len(wbs) + 1}"
        wbs[phase_id] = placement.get(
            "phase_data",
            {"name": "New Phase", "status": "pending", "subtasks": {}},
        )
        self._write_plan(plan_data)
        return {"success": True, "new_phase": phase_id}

    def _write_plan(self, plan: Dict[str, Any]) -> None:
        backup_path = self._create_backup()
        try:
            utils.write_json(self.project_plan_path, plan)
            self.sync_engine.update_task("wbs_refresh", "triggered")
        except Exception:
            utils.restore_backup(backup_path, self.project_plan_path)
            raise

    def _update_project_metadata(self, update_result: Dict[str, Any]) -> None:
        if not update_result.get("success"):
            return
        metadata_path = self.project_plan_path.parent / "wbs_update_metadata.json"
        metadata = utils.read_json(metadata_path, default={})
        history = metadata.setdefault("history", [])
        history.append(
            {
                "timestamp": utils.now_iso(),
                "result": update_result,
            }
        )
        utils.write_json(metadata_path, metadata)

    def _create_backup(self) -> Path:
        backup_dir = self.project_plan_path.parent / "wbs_backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return utils.create_timestamped_backup(self.project_plan_path, backup_dir)

    def _restore_backup(self, backup_path: Path) -> bool:
        return utils.restore_backup(backup_path, self.project_plan_path)

    def validate_wbs_integrity(self) -> Dict[str, Any]:
        plan = utils.read_json(self.project_plan_path, default={})
        wbs = plan.get("work_breakdown_structure", {})
        issues: List[str] = []
        for phase_id, phase in wbs.items():
            if "name" not in phase:
                issues.append(f"Phase {phase_id} missing name")
        return {"issues": issues, "valid": not issues}

    def get_integration_history(self) -> List[Dict[str, Any]]:
        metadata_path = self.project_plan_path.parent / "wbs_update_metadata.json"
        metadata = utils.read_json(metadata_path, default={})
        return metadata.get("history", [])

    def record_integration_operation(self, operation_data: Dict[str, Any]) -> None:
        metadata_path = self.project_plan_path.parent / "wbs_update_metadata.json"
        metadata = utils.read_json(metadata_path, default={})
        history = metadata.setdefault("history", [])
        history.append(operation_data)
        utils.write_json(metadata_path, metadata)


def update_wbs_for_task(
    task_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    root: Optional[Path] = None,
) -> Dict[str, Any]:
    warn(
        "update_wbs_for_task is deprecated; use WBSUpdateEngine or UnifiedProjectManagementEngine",
        DeprecationWarning,
        stacklevel=2,
    )
    engine = WBSUpdateEngine(root or Path("."))
    return engine.apply_task_integration(task_data, context)
