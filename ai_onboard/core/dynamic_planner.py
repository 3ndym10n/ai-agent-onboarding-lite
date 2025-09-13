"""Dynamic Project Planner.

Updates project plans as milestones are hit and activities completed.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from . import utils


class DynamicPlanner:
    """Manages dynamic project planning with milestone tracking and plan updates."""

    def __init__(self, root: Path):
        self.root = root
        self.plan_path = root / ".ai_onboard" / "plan.json"
        self.progress_path = root / ".ai_onboard" / "progress.json"
        self.milestone_log_path = root / ".ai_onboard" / "milestone_log.jsonl"

    def get_current_plan(self) -> Dict[str, Any]:
        """Get the current project plan."""
        return utils.read_json(self.plan_path, default={})

    def get_progress(self) -> Dict[str, Any]:
        """Get current project progress."""
        return utils.read_json(
            self.progress_path,
            default={
                "milestones": {},
                "activities": {},
                "last_updated": utils.now_iso(),
            },
        )

    def mark_milestone_complete(
        self, milestone_name: str, completion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mark a milestone as complete and update the plan."""
        progress = self.get_progress()
        plan = self.get_current_plan()

        # Update progress
        progress["milestones"][milestone_name] = {
            "status": "completed",
            "completed_at": utils.now_iso(),
            "completion_data": completion_data,
        }

        # Log milestone completion
        self._log_milestone_event("completed", milestone_name, completion_data)

        # Check if this triggers plan updates
        plan_updates = self._check_plan_updates(plan, progress)

        if plan_updates["needs_update"]:
            updated_plan = self._apply_plan_updates(plan, plan_updates["updates"])
            utils.write_json(self.plan_path, updated_plan)
            plan = updated_plan

        # Save progress
        progress["last_updated"] = utils.now_iso()
        utils.write_json(self.progress_path, progress)

        return {
            "status": "milestone_completed",
            "milestone": milestone_name,
            "plan_updated": plan_updates["needs_update"],
            "next_milestones": self._get_next_milestones(plan, progress),
        }

    def update_activity_progress(
        self, activity_id: str, progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update progress on a specific activity."""
        progress = self.get_progress()
        plan = self.get_current_plan()

        # Update activity progress
        if "activities" not in progress:
            progress["activities"] = {}

        progress["activities"][activity_id] = {
            "last_updated": utils.now_iso(),
            "progress_data": progress_data,
        }

        # Check if activity completion triggers milestone completion
        milestone_updates = self._check_milestone_completion(plan, progress)

        # Save progress
        progress["last_updated"] = utils.now_iso()
        utils.write_json(self.progress_path, progress)

        return {
            "status": "activity_updated",
            "activity": activity_id,
            "milestones_triggered": milestone_updates["completed_milestones"],
        }

    def auto_update_plan(self) -> Dict[str, Any]:
        """Automatically update plan based on current progress and conditions."""
        progress = self.get_progress()
        plan = self.get_current_plan()

        # Check for plan updates needed
        plan_updates = self._check_plan_updates(plan, progress)

        if not plan_updates["needs_update"]:
            return {
                "status": "no_updates_needed",
                "reason": "Current plan is up to date",
            }

        # Apply updates
        updated_plan = self._apply_plan_updates(plan, plan_updates["updates"])
        utils.write_json(self.plan_path, updated_plan)

        # Log plan update
        self._log_milestone_event(
            "plan_updated",
            "auto_update",
            {
                "updates_applied": plan_updates["updates"],
                "reason": plan_updates["reason"],
            },
        )

        return {
            "status": "plan_updated",
            "updates_applied": plan_updates["updates"],
            "reason": plan_updates["reason"],
        }

    def add_new_milestone(self, milestone_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new milestone to the project plan."""
        plan = self.get_current_plan()

        if "milestones" not in plan:
            plan["milestones"] = []

        # Generate milestone ID
        milestone_id = f"M{len(plan['milestones']) + 1}"
        milestone_data["id"] = milestone_id
        milestone_data["created_at"] = utils.now_iso()

        plan["milestones"].append(milestone_data)
        utils.write_json(self.plan_path, plan)

        # Log new milestone
        self._log_milestone_event("created", milestone_id, milestone_data)

        return {
            "status": "milestone_added",
            "milestone_id": milestone_id,
            "milestone_data": milestone_data,
        }

    def _check_plan_updates(
        self, plan: Dict[str, Any], progress: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if plan needs updates based on current progress."""
        updates = []
        reason = ""

        # Check if all milestones in a phase are complete
        completed_milestones = set(progress.get("milestones", {}).keys())

        # Check for phase transitions
        if "phases" in plan:
            for phase in plan["phases"]:
                phase_milestones = set(phase.get("milestones", []))
                if phase_milestones.issubset(completed_milestones):
                    # Phase complete - check if next phase needs activation
                    updates.append(
                        {
                            "type": "phase_complete",
                            "phase": phase["name"],
                            "action": "activate_next_phase",
                        }
                    )
                    reason = f"Phase '{phase['name']}' completed"

        # Check for timeline adjustments
        timeline_updates = self._check_timeline_adjustments(plan, progress)
        if timeline_updates:
            updates.extend(timeline_updates)
            reason = "Timeline adjustments needed"

        # Check for risk updates
        risk_updates = self._check_risk_updates(plan, progress)
        if risk_updates:
            updates.extend(risk_updates)
            reason = "Risk profile updated"

        return {"needs_update": len(updates) > 0, "updates": updates, "reason": reason}

    def _apply_plan_updates(
        self, plan: Dict[str, Any], updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply updates to the project plan."""
        updated_plan = plan.copy()

        for update in updates:
            if update["type"] == "phase_complete":
                # Activate next phase
                updated_plan = self._activate_next_phase(updated_plan, update["phase"])
            elif update["type"] == "timeline_adjustment":
                # Adjust timeline
                updated_plan = self._adjust_timeline(updated_plan, update["adjustment"])
            elif update["type"] == "risk_update":
                # Update risk profile
                updated_plan = self._update_risk_profile(
                    updated_plan, update["risk_data"]
                )

        return updated_plan

    def _check_milestone_completion(
        self, plan: Dict[str, Any], progress: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if any milestones should be marked complete based on activity progress."""
        completed_milestones = []

        # Check milestone completion criteria
        for milestone in plan.get("milestones", []):
            milestone_id = milestone.get("id", milestone.get("name", "unknown"))
            if milestone_id in progress.get("milestones", {}):
                continue  # Already completed

            # Check if milestone criteria are met
            if self._milestone_criteria_met(milestone, progress):
                completed_milestones.append(milestone_id)

        return {"completed_milestones": completed_milestones}

    def _milestone_criteria_met(
        self, milestone: Dict[str, Any], progress: Dict[str, Any]
    ) -> bool:
        """Check if milestone completion criteria are met."""
        criteria = milestone.get("completion_criteria", {})

        # Check activity completion
        required_activities = criteria.get("activities", [])
        completed_activities = 0
        for activity_id in required_activities:
            if activity_id in progress.get("activities", {}):
                activity_data = progress["activities"][activity_id]
                if activity_data.get("progress_data", {}).get("status") == "completed":
                    completed_activities += 1

        if required_activities and completed_activities < len(required_activities):
            return False

        # Check other criteria (can be expanded)
        return True

    def _get_next_milestones(
        self, plan: Dict[str, Any], progress: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get the next milestones to work on."""
        completed_milestones = set(progress.get("milestones", {}).keys())
        next_milestones = []

        for milestone in plan.get("milestones", []):
            milestone_id = milestone.get("id", milestone.get("name", "unknown"))
            if milestone_id not in completed_milestones:
                # Check dependencies
                dependencies = milestone.get("dependencies", [])
                if all(dep in completed_milestones for dep in dependencies):
                    next_milestones.append(milestone)

        return next_milestones

    def _activate_next_phase(
        self, plan: Dict[str, Any], completed_phase: str
    ) -> Dict[str, Any]:
        """Activate the next phase after a phase is completed."""
        # Implementation depends on phase structure
        return plan

    def _adjust_timeline(
        self, plan: Dict[str, Any], adjustment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adjust project timeline based on progress."""
        # Implementation for timeline adjustments
        return plan

    def _update_risk_profile(
        self, plan: Dict[str, Any], risk_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update project risk profile."""
        # Implementation for risk updates
        return plan

    def _check_timeline_adjustments(
        self, plan: Dict[str, Any], progress: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check if timeline adjustments are needed."""
        # Implementation for timeline checking
        return []

    def _check_risk_updates(
        self, plan: Dict[str, Any], progress: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check if risk profile needs updates."""
        # Implementation for risk checking
        return []

    def _log_milestone_event(
        self, event_type: str, milestone_id: str, data: Dict[str, Any]
    ) -> None:
        """Log milestone - related events."""
        utils.ensure_dir(self.milestone_log_path.parent)
        entry = {
            "ts": utils.now_iso(),
            "event": event_type,
            "milestone_id": milestone_id,
            "data": data,
        }
        with open(self.milestone_log_path, "a", encoding="utf - 8") as f:
            json.dump(entry, f)
            f.write("\n")


def get_dynamic_planner(root: Path) -> DynamicPlanner:
    """Get dynamic planner instance for the project."""
    return DynamicPlanner(root)
