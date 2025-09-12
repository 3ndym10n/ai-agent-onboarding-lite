"""
Context Continuity Manager: Maintains project context across agent sessions and prevents drift.
"""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from . import utils, vision_guardian


class ContextContinuityManager:
    """Manages context continuity across agent sessions and prevents drift."""

    def __init__(self, root: Path):
        self.root = root
        self.context_path = root / ".ai_onboard" / "context.json"
        self.session_log_path = root / ".ai_onboard" / "session_log.jsonl"
        self.drift_detection_path = root / ".ai_onboard" / "drift_detection.json"

    def get_current_context(self) -> Dict[str, Any]:
        """Get the current project context for agents."""
        context = utils.read_json(self.context_path, default={})

        # Ensure context is up to date
        if not self._is_context_current(context):
            context = self._rebuild_context()

        return context

    def update_context(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update context with new session data."""
        current_context = self.get_current_context()

        # Extract key information from session
        session_id = session_data.get("session_id", utils.generate_id())
        agent_id = session_data.get("agent_id", "unknown")
        activities = session_data.get("activities", [])
        decisions = session_data.get("decisions", [])

        # Update context with session information
        if "sessions" not in current_context:
            current_context["sessions"] = []

        session_summary = {
            "session_id": session_id,
            "agent_id": agent_id,
            "timestamp": utils.now_iso(),
            "activities_count": len(activities),
            "decisions_count": len(decisions),
            "key_decisions": self._extract_key_decisions(decisions),
            "context_hash": self._calculate_context_hash(current_context),
        }

        current_context["sessions"].append(session_summary)

        # Keep only recent sessions (last 10)
        if len(current_context["sessions"]) > 10:
            current_context["sessions"] = current_context["sessions"][-10:]

        # Update project state
        current_context["last_updated"] = utils.now_iso()
        current_context["context_hash"] = self._calculate_context_hash(current_context)

        # Save updated context
        utils.write_json(self.context_path, current_context)

        # Log session
        self._log_session(session_data, session_summary)

        return {
            "status": "context_updated",
            "session_id": session_id,
            "context_hash": current_context["context_hash"],
            "drift_detected": self._check_for_drift(current_context),
        }

    def check_context_drift(self) -> Dict[str, Any]:
        """Check for context drift between sessions."""
        current_context = self.get_current_context()
        drift_analysis = self._analyze_drift(current_context)

        # Save drift analysis
        utils.write_json(self.drift_detection_path, drift_analysis)

        return drift_analysis

    def resolve_context_drift(
        self, drift_type: str, resolution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve detected context drift."""
        current_context = self.get_current_context()

        if drift_type == "vision_drift":
            # Vision drift resolution
            resolution = self._resolve_vision_drift(current_context, resolution_data)
        elif drift_type == "scope_drift":
            # Scope drift resolution
            resolution = self._resolve_scope_drift(current_context, resolution_data)
        elif drift_type == "priority_drift":
            # Priority drift resolution
            resolution = self._resolve_priority_drift(current_context, resolution_data)
        else:
            resolution = {
                "status": "unknown_drift_type",
                "message": f"Unknown drift type: {drift_type}",
            }

        # Update context with resolution
        if resolution.get("status") == "resolved":
            current_context["last_drift_resolution"] = {
                "type": drift_type,
                "resolved_at": utils.now_iso(),
                "resolution": resolution_data,
            }
            utils.write_json(self.context_path, current_context)

        return resolution

    def get_context_summary(self, level: str = "brief") -> Dict[str, Any]:
        """Get a context summary for agents."""
        current_context = self.get_current_context()

        if level == "brief":
            return {
                "project_name": current_context.get("project_name", "Unknown"),
                "vision": current_context.get("vision", ""),
                "current_phase": current_context.get("current_phase", "Unknown"),
                "active_milestones": current_context.get("active_milestones", []),
                "recent_decisions": current_context.get("recent_decisions", []),
                "context_hash": current_context.get("context_hash", ""),
                "last_updated": current_context.get("last_updated", ""),
            }
        else:
            return current_context

    def validate_agent_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if an agent decision aligns with current context."""
        current_context = self.get_current_context()

        # Check vision alignment
        vision_guardian = vision_guardian.get_vision_guardian(self.root)
        vision_validation = vision_guardian.validate_decision_alignment(decision)

        # Check context consistency
        context_validation = self._validate_context_consistency(
            decision, current_context
        )

        # Combine validations
        overall_score = (
            vision_validation.get("alignment_score", 0)
            + context_validation.get("consistency_score", 0)
        ) / 2

        return {
            "decision_id": decision.get("id", utils.generate_id()),
            "vision_alignment": vision_validation,
            "context_consistency": context_validation,
            "overall_score": overall_score,
            "recommendation": (
                "approve"
                if overall_score > 0.7
                else "review" if overall_score > 0.3 else "reject"
            ),
        }

    def _rebuild_context(self) -> Dict[str, Any]:
        """Rebuild context from current project state."""
        # Get charter and plan
        charter_data = utils.read_json(
            self.root / ".ai_onboard" / "charter.json", default={}
        )
        plan_data = utils.read_json(self.root / ".ai_onboard" / "plan.json", default={})

        # Build comprehensive context
        context = {
            "project_name": charter_data.get("project_name", self.root.name),
            "vision": charter_data.get("vision", ""),
            "objectives": charter_data.get("objectives", []),
            "non_goals": charter_data.get("non_goals", []),
            "constraints": charter_data.get("constraints", {}),
            "current_phase": self._determine_current_phase(plan_data),
            "active_milestones": self._get_active_milestones(plan_data),
            "completed_milestones": self._get_completed_milestones(plan_data),
            "recent_decisions": self._get_recent_decisions(),
            "sessions": [],
            "context_hash": "",
            "last_updated": utils.now_iso(),
            "context_version": "1.0",
        }

        # Calculate context hash
        context["context_hash"] = self._calculate_context_hash(context)

        # Save rebuilt context
        utils.write_json(self.context_path, context)

        return context

    def _is_context_current(self, context: Dict[str, Any]) -> bool:
        """Check if context is current and up to date."""
        last_updated = context.get("last_updated", "")
        if not last_updated:
            return False

        # Check if context is older than 1 hour
        try:
            last_update = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
            if datetime.now(last_update.tzinfo) - last_update > timedelta(hours=1):
                return False
        except:
            return False

        return True

    def _calculate_context_hash(self, context: Dict[str, Any]) -> str:
        """Calculate a hash of the context for change detection."""
        # Create a stable representation for hashing
        context_copy = context.copy()
        context_copy.pop("context_hash", None)  # Remove hash from calculation
        context_copy.pop("last_updated", None)  # Remove timestamp from calculation

        context_str = json.dumps(context_copy, sort_keys=True)
        return hashlib.sha256(context_str.encode()).hexdigest()[:16]

    def _extract_key_decisions(
        self, decisions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract key decisions from session decisions."""
        key_decisions = []

        for decision in decisions:
            if decision.get("importance", "low") in ["high", "critical"]:
                key_decisions.append(
                    {
                        "type": decision.get("type", "unknown"),
                        "description": decision.get("description", ""),
                        "impact": decision.get("impact", "unknown"),
                    }
                )

        return key_decisions

    def _log_session(
        self, session_data: Dict[str, Any], session_summary: Dict[str, Any]
    ) -> None:
        """Log session data for analysis."""
        utils.ensure_dir(self.session_log_path.parent)
        entry = {
            "ts": utils.now_iso(),
            "session_data": session_data,
            "session_summary": session_summary,
        }
        with open(self.session_log_path, "a", encoding="utf-8") as f:
            json.dump(entry, f)
            f.write("\n")

    def _check_for_drift(self, context: Dict[str, Any]) -> bool:
        """Check if context drift is detected."""
        # Simple drift detection based on context hash changes
        previous_context = utils.read_json(self.context_path, default={})
        previous_hash = previous_context.get("context_hash", "")
        current_hash = context.get("context_hash", "")

        return previous_hash != "" and previous_hash != current_hash

    def _analyze_drift(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze context drift patterns."""
        sessions = context.get("sessions", [])

        if len(sessions) < 2:
            return {
                "drift_detected": False,
                "reason": "Insufficient session data for drift analysis",
            }

        # Analyze decision patterns
        decision_patterns = self._analyze_decision_patterns(sessions)

        # Analyze activity patterns
        activity_patterns = self._analyze_activity_patterns(sessions)

        # Detect drift types
        drift_types = []

        if decision_patterns.get("inconsistent_decisions", 0) > 2:
            drift_types.append("decision_drift")

        if activity_patterns.get("scope_expansion", 0) > 0.3:
            drift_types.append("scope_drift")

        if activity_patterns.get("priority_shifts", 0) > 0.2:
            drift_types.append("priority_drift")

        return {
            "drift_detected": len(drift_types) > 0,
            "drift_types": drift_types,
            "decision_patterns": decision_patterns,
            "activity_patterns": activity_patterns,
            "recommendations": self._generate_drift_recommendations(drift_types),
        }

    def _analyze_decision_patterns(
        self, sessions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze decision patterns across sessions."""
        all_decisions = []
        for session in sessions:
            all_decisions.extend(session.get("key_decisions", []))

        # Count decision types
        decision_types: Dict[str, int] = {}
        for decision in all_decisions:
            decision_type = decision.get("type", "unknown")
            decision_types[decision_type] = decision_types.get(decision_type, 0) + 1

        # Check for inconsistencies
        inconsistent_decisions = 0
        if len(decision_types) > 3:  # Too many different decision types
            inconsistent_decisions = len(decision_types) - 3

        return {
            "total_decisions": len(all_decisions),
            "decision_types": decision_types,
            "inconsistent_decisions": inconsistent_decisions,
        }

    def _analyze_activity_patterns(
        self, sessions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze activity patterns across sessions."""
        activity_counts = [s.get("activities_count", 0) for s in sessions]

        if not activity_counts:
            return {"scope_expansion": 0.0, "priority_shifts": 0.0}

        # Calculate scope expansion (increasing activity counts)
        scope_expansion = 0.0
        for i in range(1, len(activity_counts)):
            if activity_counts[i] > activity_counts[i - 1] * 1.5:
                scope_expansion += 1.0

        scope_expansion = scope_expansion / max(len(activity_counts) - 1, 1)

        # Calculate priority shifts (variance in activity counts)
        avg_activities = sum(activity_counts) / len(activity_counts)
        variance = sum(
            (count - avg_activities) ** 2 for count in activity_counts
        ) / len(activity_counts)
        priority_shifts = (
            min(variance / (avg_activities**2), 1.0) if avg_activities > 0 else 0.0
        )

        return {
            "scope_expansion": scope_expansion,
            "priority_shifts": priority_shifts,
            "activity_trend": (
                "increasing"
                if scope_expansion > 0.3
                else "stable" if scope_expansion < 0.1 else "variable"
            ),
        }

    def _generate_drift_recommendations(self, drift_types: List[str]) -> List[str]:
        """Generate recommendations for addressing drift."""
        recommendations = []

        for drift_type in drift_types:
            if drift_type == "decision_drift":
                recommendations.append(
                    "Review recent decisions for consistency with project vision"
                )
            elif drift_type == "scope_drift":
                recommendations.append("Reassess project scope and objectives")
            elif drift_type == "priority_drift":
                recommendations.append(
                    "Revisit project priorities and milestone sequencing"
                )

        return recommendations

    def _validate_context_consistency(
        self, decision: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate if decision is consistent with current context."""
        consistency_score = 1.0
        issues = []

        # Check if decision aligns with current phase
        current_phase = context.get("current_phase", "")
        decision_phase = decision.get("phase", "")

        if decision_phase and current_phase and decision_phase != current_phase:
            consistency_score -= 0.2
            issues.append(
                f"Decision phase '{decision_phase}' doesn't match current phase '{current_phase}'"
            )

        # Check if decision supports active milestones
        active_milestones = context.get("active_milestones", [])
        decision_milestones = decision.get("milestones", [])

        if decision_milestones and active_milestones:
            overlap = set(decision_milestones) & set(active_milestones)
            if not overlap:
                consistency_score -= 0.3
                issues.append("Decision doesn't support any active milestones")

        # Check recent decision patterns
        recent_decisions = context.get("recent_decisions", [])
        if recent_decisions:
            similar_decisions = [
                d for d in recent_decisions if d.get("type") == decision.get("type")
            ]
            if len(similar_decisions) > 2:
                consistency_score -= 0.1
                issues.append("Multiple similar decisions may indicate indecision")

        return {
            "consistency_score": max(consistency_score, 0.0),
            "issues": issues,
            "recommendation": (
                "consistent"
                if consistency_score > 0.7
                else "review" if consistency_score > 0.4 else "inconsistent"
            ),
        }

    def _determine_current_phase(self, plan_data: Dict[str, Any]) -> str:
        """Determine current project phase from plan data."""
        milestones = plan_data.get("milestones", [])
        completed = self._get_completed_milestones(plan_data)

        # Simple phase determination based on milestone completion
        if len(completed) == 0:
            return "planning"
        elif len(completed) < len(milestones) * 0.3:
            return "early_development"
        elif len(completed) < len(milestones) * 0.7:
            return "development"
        elif len(completed) < len(milestones):
            return "testing"
        else:
            return "complete"

    def _get_active_milestones(self, plan_data: Dict[str, Any]) -> List[str]:
        """Get currently active milestones."""
        milestones = plan_data.get("milestones", [])
        completed = self._get_completed_milestones(plan_data)

        return [
            m.get("name", "") for m in milestones if m.get("name", "") not in completed
        ]

    def _get_completed_milestones(self, plan_data: Dict[str, Any]) -> List[str]:
        """Get completed milestones."""
        # This would integrate with progress tracking
        return []

    def _get_recent_decisions(self) -> List[Dict[str, Any]]:
        """Get recent decisions from decision log."""
        decision_log = self.root / ".ai_onboard" / "decision_log.jsonl"
        if not decision_log.exists():
            return []

        recent_decisions = []
        try:
            with open(decision_log, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("decision") == "ALIGN" and entry.get("approved"):
                            recent_decisions.append(
                                {
                                    "subject": entry.get("subject", ""),
                                    "note": entry.get("note", ""),
                                    "timestamp": entry.get("ts", ""),
                                }
                            )
                    except json.JSONDecodeError:
                        continue
        except:
            pass

        return recent_decisions[-5:]  # Last 5 decisions

    def _resolve_vision_drift(
        self, context: Dict[str, Any], resolution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve vision drift."""
        # Implementation for vision drift resolution
        return {
            "status": "resolved",
            "type": "vision_drift",
            "resolution": resolution_data,
        }

    def _resolve_scope_drift(
        self, context: Dict[str, Any], resolution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve scope drift."""
        # Implementation for scope drift resolution
        return {
            "status": "resolved",
            "type": "scope_drift",
            "resolution": resolution_data,
        }

    def _resolve_priority_drift(
        self, context: Dict[str, Any], resolution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve priority drift."""
        # Implementation for priority drift resolution
        return {
            "status": "resolved",
            "type": "priority_drift",
            "resolution": resolution_data,
        }


def get_context_continuity_manager(root: Path) -> ContextContinuityManager:
    """Get context continuity manager instance for the project."""
    return ContextContinuityManager(root)
