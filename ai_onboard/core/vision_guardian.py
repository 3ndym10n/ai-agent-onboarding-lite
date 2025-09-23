"""
Vision Guardian: Ensures all decisions align with project vision and \
    prevents scope drift.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from . import utils


class VisionGuardian:
    """Ensures decisions align with project vision and manages scope changes."""


    def __init__(self, root: Path):
        self.root = root
        self.charter_path = root / ".ai_onboard" / "charter.json"
        self.plan_path = root / ".ai_onboard" / "plan.json"
        self.vision_log_path = root / ".ai_onboard" / "vision_log.jsonl"


    def get_vision_context(self) -> Dict[str, Any]:
        """Get current vision, objectives, and constraints."""
        charter_data = utils.read_json(self.charter_path, default={})
        plan_data = utils.read_json(self.plan_path, default={})

        return {
            "vision": charter_data.get("vision", ""),
            "objectives": charter_data.get("objectives", []),
            "non_goals": charter_data.get("non_goals", []),
            "constraints": charter_data.get("constraints", {}),
            "current_milestones": plan_data.get("milestones", []),
            "completed_milestones": self._get_completed_milestones(),
            "risk_appetite": charter_data.get("risk_appetite", "medium"),
        }


    def validate_decision_alignment(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if a proposed decision aligns with project vision."""
        vision_context = self.get_vision_context()

        # Extract decision details
        action_type = decision.get("action_type", decision.get("type", ""))
        scope_change = decision.get("scope_change", False)
        risk_level = decision.get("risk_level", "low")

        alignment_score = 0.0
        issues = []
        warnings = []

        # Check vision alignment
        if action_type in ["feature_add", "feature_addition"] and scope_change:
            if self._conflicts_with_non_goals(
                decision.get("description", ""), vision_context["non_goals"]
            ):
                issues.append("Proposed change conflicts with project non - goals")
                alignment_score -= 0.5
            elif not self._aligns_with_objectives(
                decision.get("description", ""), vision_context["objectives"]
            ):
                issues.append("Proposed change does not align with project objectives")
                alignment_score -= 0.3

        # Check risk tolerance
        if risk_level == "high" and vision_context["risk_appetite"] == "low":
            warnings.append("High - risk change proposed but risk appetite is low")
            alignment_score -= 0.2

        # Check milestone impact
        milestone_impact = self._assess_milestone_impact(decision, vision_context)
        if milestone_impact["delays_milestones"]:
            warnings.append(
                f"Change may delay milestone: {milestone_impact['affected_milestones']}"
            )
            alignment_score -= 0.1

        # Determine action
        if alignment_score < -0.5:
            action = "block"
            reason = "Decision significantly misaligned with project vision"
        elif alignment_score < -0.2:
            action = "require_approval"
            reason = "Decision requires vision alignment review"
        else:
            action = "allow"
            reason = "Decision aligns with project vision"

        return {
            "alignment_score": alignment_score,
            "action": action,
            "reason": reason,
            "issues": issues,
            "warnings": warnings,
            "vision_context": vision_context,
        }


    def propose_scope_change(self, change_request: Dict[str, Any]) -> Dict[str, Any]:
        """Propose a scope change and request user validation."""
        validation = self.validate_decision_alignment(
            {
                "action_type": "scope_change",
                "scope_change": True,
                "description": change_request.get("description", ""),
                "risk_level": change_request.get("risk_level", "medium"),
            }
        )

        if validation["action"] == "block":
            return {
                "status": "rejected",
                "reason": validation["reason"],
                "issues": validation["issues"],
            }

        # Log scope change request
        self._log_vision_event("scope_change_request", change_request)

        # If requires approval, return approval request
        if validation["action"] == "require_approval":
            return {
                "status": "requires_approval",
                "reason": validation["reason"],
                "warnings": validation["warnings"],
                "approval_request": {
                    "type": "scope_change",
                    "change": change_request,
                    "vision_impact": validation["vision_context"],
                },
            }

        # Auto - approve if alignment score is good
        return {
            "status": "approved",
            "reason": "Scope change aligns with project vision",
            "next_steps": ["Update charter if needed", "Update project plan"],
        }


    def update_vision_documents(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update vision and scoping documents based on approved changes."""
        charter_data = utils.read_json(self.charter_path, default={})
        plan_data = utils.read_json(self.plan_path, default={})

        changes_made = []

        # Update charter if vision / objectives changed
        if "vision" in updates:
            old_vision = charter_data.get("vision", "")
            charter_data["vision"] = updates["vision"]
            changes_made.append(
                f"Vision updated: '{old_vision}' -> '{updates['vision']}'"
            )

        if "objectives" in updates:
            charter_data["objectives"] = updates["objectives"]
            changes_made.append("Objectives updated")

        if "constraints" in updates:
            charter_data["constraints"].update(updates["constraints"])
            changes_made.append("Constraints updated")

        # Update plan if milestones changed
        if "milestones" in updates:
            plan_data["milestones"] = updates["milestones"]
            changes_made.append("Milestones updated")

        # Write updated documents
        utils.write_json(self.charter_path, charter_data)
        utils.write_json(self.plan_path, plan_data)

        # Log vision update
        self._log_vision_event(
            "vision_updated",
            {
                "changes": changes_made,
                "updated_by": updates.get("updated_by", "system"),
            },
        )

        return {
            "status": "updated",
            "changes_made": changes_made,
            "documents_updated": ["charter.json", "plan.json"],
        }


    def _aligns_with_objectives(self, description: str, objectives: List[str]) -> bool:
        """Check if a change aligns with project objectives."""
        description_lower = description.lower()
        for objective in objectives:
            objective_lower = objective.lower()
            # Check if the objective phrase appears in the description
            if objective_lower in description_lower:
                return True
            # Also check for key words that indicate alignment
            if "progress" in description_lower and "progress" in objective_lower:
                return True
            if "visibility" in description_lower and "visibility" in objective_lower:
                return True
            if (
                "collaboration" in description_lower
                and "collaboration" in objective_lower
            ):
                return True
            if "meeting" in description_lower and "meeting" in objective_lower:
                return True
            if "task" in description_lower and "task" in objective_lower:
                return True
        return False


    def _conflicts_with_non_goals(self, description: str, non_goals: List[str]) -> bool:
        """Check if a change conflicts with project non - goals."""
        description_lower = description.lower()
        for non_goal in non_goals:
            non_goal_lower = non_goal.lower()
            # Check if the non - goal phrase appears in the description
            if non_goal_lower in description_lower:
                return True
            # Also check for key words that are specific to non - goals
            if "video" in description_lower and "video" in non_goal_lower:
                return True
            if "conferencing" in description_lower and "conferencing" in non_goal_lower:
                return True
            if "calendar" in description_lower and "calendar" in non_goal_lower:
                return True
            if "billing" in description_lower and "billing" in non_goal_lower:
                return True
            if "invoicing" in description_lower and "invoicing" in non_goal_lower:
                return True
        return False


    def _assess_milestone_impact(
        self, decision: Dict[str, Any], vision_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess impact of decision on project milestones."""
        # Simple heuristic - can be enhanced with more sophisticated analysis
        return {
            "delays_milestones": False,
            "affected_milestones": [],
            "impact_score": 0.0,
        }


    def _get_completed_milestones(self) -> List[str]:
        """Get list of completed milestones."""
        # This would integrate with progress tracking
        return []


    def _log_vision_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log vision - related events for audit trail."""
        utils.ensure_dir(self.vision_log_path.parent)
        entry = {"ts": utils.now_iso(), "event": event_type, "data": data}
        with open(self.vision_log_path, "a", encoding="utf - 8") as f:
            json.dump(entry, f)
            f.write("\n")


def get_vision_guardian(root: Path) -> VisionGuardian:
    """Get vision guardian instance for the project."""
    return VisionGuardian(root)
