"""
Task Prioritization Engine - Automatically prioritizes tasks based on multiple factors.

This module analyzes tasks in the project plan and assigns priorities based on:
- Critical path impact
- Dependency relationships
- Effort estimation
- Risk assessment
- Business value
- Resource availability
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from . import utils
from .tool_usage_tracker import track_tool_usage


class TaskPrioritizationEngine:
    """Engine for automatically prioritizing tasks in the project plan."""

    def __init__(self, root: Path):
        self.root = root
        self.project_plan_path = root / ".ai_onboard" / "project_plan.json"
        track_tool_usage(
            "task_prioritization_engine",
            "ai_system",
            {"action": "initialize"},
            "success",
        )

    def prioritize_all_tasks(self) -> Dict[str, Any]:
        """
        Analyze and prioritize all tasks in the project plan.

        Returns:
            Dict containing prioritization results and recommendations
        """
        track_tool_usage(
            "task_prioritization_engine",
            "ai_system",
            {"action": "prioritize_all_tasks"},
            "success",
        )

        plan_data = utils.read_json(self.project_plan_path, default={})
        wbs = plan_data.get("work_breakdown_structure", {})

        # Extract all tasks
        all_tasks = self._extract_all_tasks(wbs)

        # Calculate priorities for each task
        task_priorities = {}
        for task_id, task_data in all_tasks.items():
            priority_score = self._calculate_task_priority(
                task_id, task_data, all_tasks
            )
            task_priorities[task_id] = {
                "task_name": task_data.get("name", "Unknown Task"),
                "current_priority": task_data.get("priority", "medium"),
                "calculated_priority": priority_score["priority_level"],
                "priority_score": priority_score["score"],
                "priority_factors": priority_score["factors"],
                "recommendations": priority_score["recommendations"],
            }

        # Generate prioritization recommendations
        recommendations = self._generate_prioritization_recommendations(task_priorities)

        return {
            "task_priorities": task_priorities,
            "recommendations": recommendations,
            "analysis_timestamp": utils.now_iso(),
            "total_tasks_analyzed": len(all_tasks),
        }

    def _extract_all_tasks(self, wbs: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract all tasks from the WBS into a flat dictionary."""
        tasks = {}

        def extract_from_phase(phase_id: str, phase_data: Dict[str, Any]):
            # Add the phase itself if it's a task-like entry
            if "name" in phase_data and "status" in phase_data:
                tasks[phase_id] = dict(phase_data)
                tasks[phase_id]["task_type"] = "phase"

            # Extract subtasks
            subtasks = phase_data.get("subtasks", {})
            for subtask_id, subtask_data in subtasks.items():
                full_id = (
                    f"{phase_id}.{subtask_id.split('.')[-1]}"
                    if "." in subtask_id
                    else subtask_id
                )
                tasks[full_id] = dict(subtask_data)
                tasks[full_id]["task_type"] = "subtask"
                tasks[full_id]["parent_phase"] = phase_id

        for phase_id, phase_data in wbs.items():
            extract_from_phase(phase_id, phase_data)

        return tasks

    def _calculate_task_priority(
        self,
        task_id: str,
        task_data: Dict[str, Any],
        all_tasks: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculate priority score for a single task based on multiple factors.

        Returns:
            Dict with priority_level, score, factors, and recommendations
        """
        factors = {}
        score = 0

        # Factor 1: Critical Path Impact (0-30 points)
        critical_path_factor = self._assess_critical_path_impact(
            task_id, task_data, all_tasks
        )
        factors["critical_path_impact"] = critical_path_factor
        score += critical_path_factor["score"]

        # Factor 2: Dependency Impact (0-25 points)
        dependency_factor = self._assess_dependency_impact(
            task_id, task_data, all_tasks
        )
        factors["dependency_impact"] = dependency_factor
        score += dependency_factor["score"]

        # Factor 3: Effort vs. Value (0-20 points)
        effort_value_factor = self._assess_effort_value_ratio(task_data)
        factors["effort_value_ratio"] = effort_value_factor
        score += effort_value_factor["score"]

        # Factor 4: Risk Level (0-15 points)
        risk_factor = self._assess_risk_level(task_data)
        factors["risk_level"] = risk_factor
        score += risk_factor["score"]

        # Factor 5: Status Urgency (0-10 points)
        status_factor = self._assess_status_urgency(task_data)
        factors["status_urgency"] = status_factor
        score += status_factor["score"]

        # Determine priority level based on total score
        priority_level = self._score_to_priority_level(score)
        recommendations = self._generate_task_recommendations(
            task_id, task_data, factors, score
        )

        return {
            "priority_level": priority_level,
            "score": score,
            "factors": factors,
            "recommendations": recommendations,
        }

    def _assess_critical_path_impact(
        self,
        task_id: str,
        task_data: Dict[str, Any],
        all_tasks: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Assess how the task impacts the critical path."""
        score = 0
        reasons = []

        # Check if task is explicitly on critical path
        if task_data.get("is_critical_path", False):
            score += 20
            reasons.append("Explicitly marked as critical path task")

        # Check if task blocks many other tasks
        blocking_count = 0
        for other_id, other_data in all_tasks.items():
            if other_id != task_id:
                dependencies = other_data.get("dependencies", [])
                if isinstance(dependencies, list) and task_id in dependencies:
                    blocking_count += 1
                elif isinstance(dependencies, str) and task_id in dependencies:
                    blocking_count += 1

        if blocking_count > 3:
            score += 10
            reasons.append(f"Blocks {blocking_count} other tasks")
        elif blocking_count > 0:
            score += 5
            reasons.append(f"Blocks {blocking_count} other tasks")

        # Check task type priority
        task_type = task_data.get("task_type", "task")
        if task_type == "phase":
            score += 5
            reasons.append("Phase-level task with broad impact")

        return {
            "score": min(score, 30),  # Cap at 30
            "assessment": "high" if score >= 20 else "medium" if score >= 10 else "low",
            "reasons": reasons,
        }

    def _assess_dependency_impact(
        self,
        task_id: str,
        task_data: Dict[str, Any],
        all_tasks: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Assess how dependent this task is on others."""
        score = 0
        reasons = []

        dependencies = task_data.get("dependencies", [])
        if isinstance(dependencies, str):
            dependencies = [dep.strip() for dep in dependencies.split(",")]
        elif not isinstance(dependencies, list):
            dependencies = []

        dep_count = len(dependencies)

        # Tasks with many dependencies are lower priority (harder to start)
        if dep_count == 0:
            score += 15
            reasons.append("No dependencies - can start immediately")
        elif dep_count <= 2:
            score += 10
            reasons.append(f"Only {dep_count} dependencies")
        elif dep_count <= 5:
            score += 5
            reasons.append(f"Moderate dependencies ({dep_count})")
        else:
            score += 0
            reasons.append(f"Many dependencies ({dep_count}) - harder to schedule")

        # Check if dependencies are completed or in progress
        completed_deps = 0
        for dep in dependencies:
            if dep in all_tasks:
                dep_status = all_tasks[dep].get("status", "unknown")
                if dep_status == "completed":
                    completed_deps += 1

        if dep_count > 0:
            completion_ratio = completed_deps / dep_count
            if completion_ratio == 1.0:
                score += 10
                reasons.append("All dependencies completed")
            elif completion_ratio >= 0.8:
                score += 7
                reasons.append("Most dependencies completed")
            elif completion_ratio >= 0.5:
                score += 3
                reasons.append("Half dependencies completed")

        return {
            "score": min(score, 25),  # Cap at 25
            "assessment": "high" if score >= 15 else "medium" if score >= 8 else "low",
            "reasons": reasons,
            "dependency_count": dep_count,
            "completed_dependencies": completed_deps,
        }

    def _assess_effort_value_ratio(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the effort vs. value ratio of the task."""
        score = 0
        reasons = []

        effort = task_data.get("estimated_effort", "medium")
        priority = task_data.get("priority", "medium")

        # Effort levels: small, medium, large, xlarge
        effort_scores = {"small": 4, "medium": 2, "large": 1, "xlarge": 0}
        effort_score = effort_scores.get(effort.lower(), 2)

        # Priority levels: critical, high, medium, low
        priority_multipliers = {"critical": 3, "high": 2, "medium": 1.5, "low": 1}
        priority_multiplier = priority_multipliers.get(priority.lower(), 1.5)

        base_score = effort_score * priority_multiplier

        if base_score >= 6:
            score += 15
            reasons.append(f"High value, {effort} effort task")
        elif base_score >= 4:
            score += 10
            reasons.append(f"Good value-effort ratio")
        elif base_score >= 2:
            score += 5
            reasons.append(f"Moderate value-effort ratio")
        else:
            score += 0
            reasons.append(f"Low value relative to effort")

        return {
            "score": min(score, 20),  # Cap at 20
            "assessment": "high" if score >= 15 else "medium" if score >= 8 else "low",
            "reasons": reasons,
            "effort_level": effort,
            "priority_level": priority,
            "value_score": base_score,
        }

    def _assess_risk_level(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the risk level of the task."""
        score = 0
        reasons = []

        # Check for risk indicators
        description = task_data.get("description", "").lower()
        name = task_data.get("name", "").lower()

        risk_indicators = [
            "security",
            "safety",
            "critical",
            "breaking",
            "migration",
            "refactor",
            "rewrite",
            "dangerous",
            "complex",
            "high-risk",
        ]

        risk_count = 0
        for indicator in risk_indicators:
            if indicator in description or indicator in name:
                risk_count += 1

        if risk_count >= 3:
            score += 12
            reasons.append("High-risk task - multiple risk indicators")
        elif risk_count >= 2:
            score += 8
            reasons.append("Moderate risk task")
        elif risk_count >= 1:
            score += 4
            reasons.append("Some risk indicators present")
        else:
            score += 2
            reasons.append("Low-risk task")

        # Check if task has been attempted before (failed status might indicate risk)
        status = task_data.get("status", "pending")
        if status == "failed":
            score += 3
            reasons.append("Previously failed - higher risk")

        return {
            "score": min(score, 15),  # Cap at 15
            "assessment": "high" if score >= 10 else "medium" if score >= 6 else "low",
            "reasons": reasons,
            "risk_indicators_found": risk_count,
        }

    def _assess_status_urgency(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess urgency based on task status."""
        score = 0
        reasons = []

        status = task_data.get("status", "pending")

        # Status-based urgency
        if status == "in_progress":
            score += 8
            reasons.append("Currently in progress - maintain momentum")
        elif status == "blocked":
            score += 6
            reasons.append("Blocked - needs attention to unblock")
        elif status == "pending":
            score += 4
            reasons.append("Ready to start")
        elif status == "failed":
            score += 10
            reasons.append("Failed - needs immediate attention")
        elif status == "completed":
            score += 0
            reasons.append("Already completed")

        # Check for due dates
        due_date = task_data.get("due_date")
        if due_date:
            try:
                # Simple date comparison (would need proper date parsing in real implementation)
                if "immediate" in due_date.lower() or "urgent" in due_date.lower():
                    score += 5
                    reasons.append("Urgent due date")
            except:
                pass

        return {
            "score": min(score, 10),  # Cap at 10
            "assessment": "high" if score >= 7 else "medium" if score >= 4 else "low",
            "reasons": reasons,
            "current_status": status,
        }

    def _score_to_priority_level(self, total_score: float) -> str:
        """Convert numerical score to priority level."""
        if total_score >= 70:
            return "critical"
        elif total_score >= 50:
            return "high"
        elif total_score >= 30:
            return "medium"
        elif total_score >= 15:
            return "low"
        else:
            return "lowest"

    def _generate_task_recommendations(
        self,
        task_id: str,
        task_data: Dict[str, Any],
        factors: Dict[str, Any],
        total_score: float,
    ) -> List[str]:
        """Generate specific recommendations for the task."""
        recommendations = []
        current_priority = task_data.get("priority", "medium")
        calculated_priority = self._score_to_priority_level(total_score)

        # Priority change recommendations
        if calculated_priority != current_priority:
            if calculated_priority == "critical" and current_priority != "critical":
                recommendations.append(
                    f"🚨 ESCALATE: Priority should be {calculated_priority} (currently {current_priority})"
                )
            elif (
                calculated_priority in ["high", "medium"] and current_priority == "low"
            ):
                recommendations.append(
                    f"⬆️ INCREASE: Priority should be {calculated_priority} (currently {current_priority})"
                )
            elif calculated_priority == "low" and current_priority == "high":
                recommendations.append(
                    f"⬇️ DECREASE: Priority should be {calculated_priority} (currently {current_priority})"
                )

        # Specific action recommendations based on factors
        critical_path = factors.get("critical_path_impact", {})
        if critical_path.get("score", 0) >= 20:
            recommendations.append(
                "🎯 CRITICAL PATH: Focus resources on this task immediately"
            )

        dependencies = factors.get("dependency_impact", {})
        if dependencies.get("score", 0) >= 15:
            recommendations.append("⚡ QUICK WIN: No dependencies - start immediately")

        risk = factors.get("risk_level", {})
        if risk.get("score", 0) >= 10:
            recommendations.append(
                "⚠️ HIGH RISK: Plan carefully and consider breaking into smaller tasks"
            )

        status = factors.get("status_urgency", {})
        if status.get("current_status") == "blocked":
            recommendations.append(
                "🚧 BLOCKED: Identify and resolve blocking dependencies"
            )

        return recommendations

    def _generate_prioritization_recommendations(
        self, task_priorities: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate overall prioritization recommendations."""
        recommendations = {
            "priority_changes": [],
            "immediate_actions": [],
            "resource_allocation": [],
            "risk_mitigations": [],
        }

        # Analyze priority distribution
        priority_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "lowest": 0}
        changes_needed = []

        for task_id, priority_data in task_priorities.items():
            current = priority_data["current_priority"]
            calculated = priority_data["calculated_priority"]

            priority_counts[calculated] += 1

            if current != calculated:
                changes_needed.append(
                    {
                        "task_id": task_id,
                        "current": current,
                        "recommended": calculated,
                        "score": priority_data["priority_score"],
                    }
                )

        # Sort changes by score (highest first)
        changes_needed.sort(key=lambda x: x["score"], reverse=True)

        recommendations["priority_changes"] = changes_needed[:10]  # Top 10 changes

        # Generate resource allocation recommendations
        if priority_counts["critical"] > 0:
            recommendations["immediate_actions"].append(
                f"Focus {priority_counts['critical']} critical tasks immediately"
            )

        if priority_counts["high"] >= 3:
            recommendations["resource_allocation"].append(
                "Allocate additional resources to high-priority tasks"
            )

        # Risk mitigation recommendations
        high_risk_tasks = [
            task_id
            for task_id, data in task_priorities.items()
            if data["priority_factors"]["risk_level"]["assessment"] == "high"
        ]
        if high_risk_tasks:
            recommendations["risk_mitigations"].append(
                f"Review {len(high_risk_tasks)} high-risk tasks for mitigation strategies"
            )

        return recommendations

    def update_task_priorities(self, apply_changes: bool = False) -> Dict[str, Any]:
        """
        Update task priorities in the project plan.

        Args:
            apply_changes: If True, actually update the project plan

        Returns:
            Dict with update results
        """
        track_tool_usage(
            "task_prioritization_engine",
            "ai_system",
            {"action": "update_priorities", "apply_changes": apply_changes},
            "success",
        )

        prioritization_results = self.prioritize_all_tasks()

        if not apply_changes:
            return {
                "success": True,
                "mode": "preview",
                "results": prioritization_results,
                "message": "Preview mode - no changes applied",
            }

        # Apply the priority changes
        plan_data = utils.read_json(self.project_plan_path, default={})
        wbs = plan_data.get("work_breakdown_structure", {})

        changes_applied = 0
        changes_failed = 0

        for task_id, priority_data in prioritization_results["task_priorities"].items():
            current_priority = priority_data["current_priority"]
            new_priority = priority_data["calculated_priority"]

            if current_priority != new_priority:
                # Find and update the task in WBS
                if self._update_task_priority_in_wbs(wbs, task_id, new_priority):
                    changes_applied += 1
                else:
                    changes_failed += 1

        # Save updated plan
        plan_data["work_breakdown_structure"] = wbs
        plan_data["last_updated"] = utils.now_iso()
        utils.write_json(self.project_plan_path, plan_data)

        return {
            "success": True,
            "mode": "applied",
            "changes_applied": changes_applied,
            "changes_failed": changes_failed,
            "results": prioritization_results,
            "message": f"Applied {changes_applied} priority changes, {changes_failed} failed",
        }

    def _update_task_priority_in_wbs(
        self, wbs: Dict[str, Any], task_id: str, new_priority: str
    ) -> bool:
        """Update a task's priority in the WBS structure."""
        # Handle both phase and subtask updates
        if "." in task_id:
            # Subtask
            phase_id = task_id.split(".")[0]
            subtask_key = task_id
        else:
            # Phase
            phase_id = task_id
            subtask_key = None

        if phase_id in wbs:
            if subtask_key and subtask_key in wbs[phase_id].get("subtasks", {}):
                wbs[phase_id]["subtasks"][subtask_key]["priority"] = new_priority
                return True
            elif not subtask_key:
                wbs[phase_id]["priority"] = new_priority
                return True

        return False


def prioritize_tasks(
    root: Optional[Path] = None, apply_changes: bool = False
) -> Dict[str, Any]:
    """Convenience function to prioritize tasks."""
    if root is None:
        root = Path.cwd()

    engine = TaskPrioritizationEngine(root)
    return engine.update_task_priorities(apply_changes)
