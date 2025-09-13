"""
Progress Dashboard and Milestone Tracking System

Provides visual progress tracking, milestone completion monitoring,
and project health metrics for the AI onboarding system.

This dashboard keeps stakeholders informed about project progress
and helps identify areas needing attention.
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class ProgressDashboard:
    """Provides comprehensive progress tracking and visualization."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.plan_path = project_root / ".ai_onboard" / "plan.json"
        self.learning_log_path = project_root / ".ai_onboard" / "learning_events.jsonl"

    def generate_dashboard(self) -> Dict[str, Any]:
        """
        Generate a comprehensive progress dashboard.

        Returns:
            Dict containing all dashboard metrics and visualizations
        """
        if not self.plan_path.exists():
            return {"error": "Project plan not found"}

        with open(self.plan_path, "r") as f:
            plan = json.load(f)

        return {
            "header": self._generate_header(),
            "overall_progress": self._generate_overall_progress(plan),
            "milestone_progress": self._generate_milestone_progress(plan),
            "task_status_breakdown": self._generate_task_status_breakdown(plan),
            "timeline_view": self._generate_timeline_view(plan),
            "health_metrics": self._generate_health_metrics(plan),
            "upcoming_deadlines": self._generate_upcoming_deadlines(plan),
            "blockers_and_risks": self._generate_blockers_and_risks(plan),
            "recent_activity": self._generate_recent_activity(),
            "recommendations": self._generate_recommendations(plan),
        }

    def _generate_header(self) -> Dict[str, Any]:
        """Generate dashboard header with key summary stats."""
        return {
            "title": "AI Onboarding System - Progress Dashboard",
            "last_updated": datetime.now().isoformat(),
            "project_phase": "Development & Testing",
            "status": "ACTIVE",
        }

    def _generate_overall_progress(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall project progress metrics via canonical utils."""
        from . import progress_utils

        overall = progress_utils.compute_overall_progress(plan)

        # Calculate progress rate (tasks per day) and estimated completion using existing helpers
        progress_rate = self._calculate_progress_rate(plan)

        return {
            "completion_percentage": overall["completion_percentage"],
            "completed_tasks": overall["completed_tasks"],
            "total_tasks": overall["total_tasks"],
            "in_progress_tasks": overall["in_progress_tasks"],
            "pending_tasks": overall["pending_tasks"],
            "progress_rate": progress_rate,
            "estimated_completion": self._estimate_completion_date(plan, progress_rate),
            "visual_bar": overall["visual_bar"],
        }

    def _generate_milestone_progress(
        self, plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate detailed milestone progress tracking via canonical utils."""
        from . import progress_utils

        milestone_progress = progress_utils.compute_milestone_progress(plan, width=15)

        # Enrich with days_remaining and normalized status where needed
        for item in milestone_progress:
            target_date = item.get("target_date")
            item["days_remaining"] = self._calculate_days_remaining(target_date)
            # Keep existing status semantics, already set by progress_utils

        return milestone_progress

    def _generate_task_status_breakdown(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed task status breakdown by category."""
        status_breakdown: Dict[str, int] = defaultdict(int)
        category_breakdown: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        for task in plan["tasks"]:
            status = task.get("status", "unknown")
            category = task.get("wbs_id", "unknown")

            status_breakdown[status] += 1
            category_breakdown[category][status] += 1

        return {
            "by_status": dict(status_breakdown),
            "by_category": dict(category_breakdown),
            "status_distribution": self._calculate_status_distribution(
                status_breakdown
            ),
        }

    def _generate_timeline_view(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate timeline view of task completions."""
        timeline_data = []

        # Group completions by week
        weekly_completions: Dict[str, int] = defaultdict(int)
        weekly_effort: Dict[str, float] = defaultdict(float)

        for task in plan["tasks"]:
            if task.get("status") == "completed" and "completion_date" in task:
                completion_date = task["completion_date"][:10]  # YYYY - MM - DD
                week_start = self._get_week_start(completion_date)

                weekly_completions[week_start] += 1
                weekly_effort[week_start] += task.get("effort_days", 0)

        # Convert to timeline format
        for week, count in weekly_completions.items():
            timeline_data.append(
                {
                    "week": week,
                    "completions": count,
                    "effort_completed": weekly_effort[week],
                }
            )

        return {
            "weekly_completions": sorted(timeline_data, key=lambda x: x["week"]),
            "total_weeks": len(timeline_data),
            "peak_week": None,  # TODO: Implement with proper typing
        }

    def _generate_health_metrics(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project health metrics."""
        total_tasks = len(plan["tasks"])
        completed_tasks = len(
            [t for t in plan["tasks"] if t.get("status") == "completed"]
        )
        overdue_tasks = self._count_overdue_tasks(plan)

        # Calculate health score (0 - 100)
        completion_score = (
            (completed_tasks / total_tasks) * 50 if total_tasks > 0 else 0
        )
        timeliness_score = max(0, 50 - (overdue_tasks * 5))  # Penalty for overdue tasks
        health_score = min(100, completion_score + timeliness_score)

        return {
            "overall_health_score": round(health_score, 1),
            "completion_health": round(completion_score, 1),
            "timeliness_health": round(timeliness_score, 1),
            "overdue_tasks": overdue_tasks,
            "health_status": self._get_health_status(health_score),
            "health_color": self._get_health_color(health_score),
        }

    def _generate_upcoming_deadlines(
        self, plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate list of upcoming task and milestone deadlines."""
        upcoming = []

        # Task deadlines
        for task in plan["tasks"]:
            deadline = task.get("deadline")
            if deadline and task.get("status") != "completed":
                days_remaining = self._calculate_days_remaining(deadline)
                if days_remaining >= 0:  # Not overdue
                    upcoming.append(
                        {
                            "type": "task",
                            "id": task["id"],
                            "name": task["name"],
                            "deadline": deadline,
                            "days_remaining": days_remaining,
                            "priority": task.get("priority", "medium"),
                        }
                    )

        # Milestone deadlines
        for milestone in plan.get("milestones", []):
            target_date = milestone.get("target_date")
            if target_date:
                days_remaining = self._calculate_days_remaining(target_date)
                if days_remaining >= 0:
                    upcoming.append(
                        {
                            "type": "milestone",
                            "name": milestone["name"],
                            "deadline": target_date,
                            "days_remaining": days_remaining,
                            "priority": milestone.get("priority", "medium"),
                        }
                    )

        return sorted(upcoming, key=lambda x: x["days_remaining"])[:10]

    def _generate_blockers_and_risks(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate blockers and risks analysis."""
        blockers = []

        # Identify blocked tasks
        for task in plan["tasks"]:
            if task.get("status") == "pending":
                dependencies = task.get("dependencies", [])
                blocked_by = []

                for dep_id in dependencies:
                    dep_task = next(
                        (t for t in plan["tasks"] if t["id"] == dep_id), None
                    )
                    if dep_task and dep_task.get("status") != "completed":
                        blocked_by.append(dep_id)

                if blocked_by:
                    blockers.append(
                        {
                            "task_id": task["id"],
                            "task_name": task["name"],
                            "blocked_by": blocked_by,
                            "days_blocked": self._calculate_days_blocked(task),
                        }
                    )

        return {
            "task_blockers": blockers[:10],  # Top 10 blockers
            "project_risks": plan.get("risks", []),
            "total_blockers": len(blockers),
            "critical_blockers": len(
                [b for b in blockers if b.get("days_blocked", 0) > 7]
            ),
        }

    def _generate_recent_activity(self) -> List[Dict[str, Any]]:
        """Generate recent activity from learning events."""
        recent_activity = []

        if self.learning_log_path.exists():
            try:
                with open(self.learning_log_path, "r") as f:
                    lines = f.readlines()[-10:]  # Last 10 events

                for line in lines:
                    if line.strip():
                        event = json.loads(line)
                        recent_activity.append(
                            {
                                "timestamp": event.get("timestamp"),
                                "type": event.get("type"),
                                "activity": event.get("activity"),
                                "category": event.get("category"),
                            }
                        )
            except:
                pass

        return recent_activity

    def _generate_recommendations(self, plan: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on current progress."""
        recommendations = []

        # Check for overdue tasks
        overdue_count = self._count_overdue_tasks(plan)
        if overdue_count > 0:
            recommendations.append(
                f"Address {overdue_count} overdue tasks to improve timeliness health"
            )

        # Check for blocked tasks
        blocked_tasks = []
        for task in plan["tasks"]:
            if task.get("status") == "pending":
                dependencies = task.get("dependencies", [])
                for dep_id in dependencies:
                    dep_task = next(
                        (t for t in plan["tasks"] if t["id"] == dep_id), None
                    )
                    if dep_task and dep_task.get("status") != "completed":
                        blocked_tasks.append(task["id"])
                        break

        if blocked_tasks:
            recommendations.append(
                f"Resolve dependencies for {len(blocked_tasks)} blocked tasks"
            )

        # Check milestone progress
        for milestone in plan.get("milestones", []):
            tasks = milestone.get("tasks", [])
            if tasks:

                def is_task_completed(task_id: str) -> bool:
                    task: Dict[str, Any] = next(
                        (t for t in plan["tasks"] if t["id"] == task_id), {}
                    )
                    return task.get("status", "") == "completed"

                completed_count = sum(
                    1 for task_id in tasks if is_task_completed(task_id)
                )
                if completed_count < len(tasks):
                    days_remaining = self._calculate_days_remaining(
                        milestone.get("target_date")
                    )
                    if days_remaining < 7:
                        recommendations.append(
                            f"Focus on completing '{milestone['name']}' milestone ({days_remaining} days remaining)"
                        )

        return recommendations[:5]  # Top 5 recommendations

    # Helper methods

    def _calculate_progress_rate(self, plan: Dict[str, Any]) -> float:
        """Calculate tasks completed per day."""
        completed_tasks = [
            t
            for t in plan["tasks"]
            if t.get("status") == "completed" and "completion_date" in t
        ]

        if not completed_tasks:
            return 0.0

        # Find earliest and latest completion dates
        dates = [datetime.fromisoformat(t["completion_date"]) for t in completed_tasks]
        if len(dates) < 2:
            return 0.0

        date_range = max(dates) - min(dates)
        days = date_range.days or 1  # Avoid division by zero

        return len(completed_tasks) / days

    def _estimate_completion_date(
        self, plan: Dict[str, Any], progress_rate: float
    ) -> Optional[str]:
        """Estimate project completion date."""
        remaining_tasks = len(
            [t for t in plan["tasks"] if t.get("status") != "completed"]
        )

        if progress_rate == 0:
            return None

        days_remaining = remaining_tasks / progress_rate
        estimated_date = datetime.now() + timedelta(days=days_remaining)

        return estimated_date.strftime("%Y -% m-%d")

    def _generate_progress_bar(self, percentage: float) -> str:
        """Legacy wrapper kept for compatibility; delegates to canonical utils."""
        from . import progress_utils

        return progress_utils.create_progress_bar(percentage, width=20)

    def _calculate_milestone_status(
        self, progress: float, target_date: Optional[str]
    ) -> str:
        """Calculate milestone status based on progress and deadline."""
        if progress == 100:
            return "completed"
        elif progress >= 75:
            return "on_track"
        elif progress >= 50:
            return "at_risk"
        else:
            return "behind"

    def _calculate_days_remaining(self, target_date: Optional[str]) -> int:
        """Calculate days remaining until target date."""
        if not target_date:
            return 999

        try:
            target = datetime.fromisoformat(target_date)
            remaining = target - datetime.now()
            return remaining.days
        except:
            return 999

    def _calculate_status_distribution(
        self, status_breakdown: Dict[str, int]
    ) -> Dict[str, float]:
        """Calculate percentage distribution of task statuses."""
        total = sum(status_breakdown.values())
        if total == 0:
            return {}

        return {
            status: (count / total) * 100 for status, count in status_breakdown.items()
        }

    def _get_week_start(self, date_str: str) -> str:
        """Get the start of the week for a given date."""
        date = datetime.fromisoformat(date_str)
        # Monday is 0 in isocalendar
        week_start = date - timedelta(days=date.weekday())
        return week_start.strftime("%Y -% m-%d")

    def _count_overdue_tasks(self, plan: Dict[str, Any]) -> int:
        """Count overdue tasks."""
        overdue = 0
        for task in plan["tasks"]:
            deadline = task.get("deadline")
            if deadline and task.get("status") != "completed":
                if self._calculate_days_remaining(deadline) < 0:
                    overdue += 1
        return overdue

    def _calculate_days_blocked(self, task: Dict[str, Any]) -> int:
        """Calculate how long a task has been blocked."""
        # Simplified - could be enhanced with actual blocking start dates
        return 0

    def _get_health_status(self, score: float) -> str:
        """Get health status description."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Needs Attention"

    def _get_health_color(self, score: float) -> str:
        """Get health color for visualization."""
        if score >= 80:
            return "green"
        elif score >= 60:
            return "yellow"
        elif score >= 40:
            return "orange"
        else:
            return "red"

    def display_dashboard(self) -> None:
        """Display the progress dashboard in a readable format."""
        dashboard = self.generate_dashboard()

        if "error" in dashboard:
            print(f"Error: {dashboard['error']}")
            return

        print("🚀 AI ONBOARDING SYSTEM - PROGRESS DASHBOARD")
        print("=" * 60)

        # Overall Progress
        overall = dashboard["overall_progress"]
        print(f"📊 OVERALL PROGRESS: {overall['completion_percentage']}%")
        print(f"   {overall['visual_bar']}")
        print(
            f"   ✅ {overall['completed_tasks']}/{overall['total_tasks']} tasks completed"
        )
        print(f"   🔄 {overall['in_progress_tasks']} in progress")
        print(f"   ⏳ {overall['pending_tasks']} pending")
        print()

        # Health Metrics
        health = dashboard["health_metrics"]
        print(
            f"💚 PROJECT HEALTH: {health['overall_health_score']}/100 ({health['health_status']})"
        )
        print(f"   Completion Health: {health['completion_health']}/50")
        print(f"   Timeliness Health: {health['timeliness_health']}/50")
        print()

        # Milestone Progress
        print("🏁 MILESTONE PROGRESS:")
        for milestone in dashboard["milestone_progress"][:5]:  # Top 5
            status_icon = "✅" if milestone["status"] == "completed" else "🔄"
            print(
                f"   {status_icon} {milestone['name']}: {milestone['progress_percentage']}%"
            )
            print(f"      {milestone['visual_bar']}")
            if milestone["target_date"]:
                days = milestone["days_remaining"]
                if days >= 0:
                    print(f"      ⏰ {days} days remaining")
                else:
                    print(f"      ⚠️  {-days} days overdue")
        print()

        # Upcoming Deadlines
        print("📅 UPCOMING DEADLINES:")
        for item in dashboard["upcoming_deadlines"][:5]:  # Top 5
            icon = "🎯" if item["type"] == "milestone" else "📋"
            print(f"   {icon} {item['name']}: {item['days_remaining']} days")
        print()

        # Recommendations
        if dashboard["recommendations"]:
            print("💡 RECOMMENDATIONS:")
            for rec in dashboard["recommendations"]:
                print(f"   • {rec}")
        print()

        print("📈 Dashboard generated at:", dashboard["header"]["last_updated"])


def generate_progress_report(project_root: Path) -> Dict[str, Any]:
    """
    Generate a complete progress report for the project.

    Args:
        project_root: Path to the project root directory

    Returns:
        Dict containing the complete progress dashboard
    """
    dashboard = ProgressDashboard(project_root)
    return dashboard.generate_dashboard()


if __name__ == "__main__":
    # Generate and display progress dashboard
    project_root = Path.cwd()
    dashboard = ProgressDashboard(project_root)
    dashboard.display_dashboard()
