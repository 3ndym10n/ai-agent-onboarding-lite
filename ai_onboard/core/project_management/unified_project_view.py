"""
Unified Project View - Single dashboard for charter + plan + WBS + progress.

This provides vibe coders with clear visibility into:
- What the project is (vision)
- Where we are (phase, progress)
- What's being done (current task)
- What's next (upcoming tasks)
- How far along (completion percentage)

No more chaos - clear systematic visibility.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base import utils


@dataclass
class ProjectDashboard:
    """Complete project dashboard for vibe coders."""
    
    # Vision & goals
    project_name: str
    vision: str
    goals: List[str] = field(default_factory=list)
    
    # Current state
    current_phase: str = "unknown"
    progress_percentage: float = 0.0
    
    # WBS task tracking
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_task: Optional[Dict[str, Any]] = None
    next_tasks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Estimates & timing
    estimated_remaining_days: Optional[float] = None
    blockers: List[str] = field(default_factory=list)
    
    # Recent activity
    recent_completions: List[str] = field(default_factory=list)


class UnifiedProjectView:
    """
    Unified view of project state combining charter, plan, and WBS.
    
    This is what vibe coders see to understand:
    - Where we are
    - What's happening
    - What's next
    - How we're progressing
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ai_onboard_dir = project_root / ".ai_onboard"
        
        # File paths
        self.charter_file = self.ai_onboard_dir / "charter.json"
        self.plan_file = self.ai_onboard_dir / "plan.json"
        self.wbs_file = self.ai_onboard_dir / "wbs.json"

    def get_dashboard(self) -> ProjectDashboard:
        """Get complete project dashboard."""
        
        # Load all data
        charter = self._load_charter()
        plan = self._load_plan()
        wbs = self._load_wbs()
        
        # Build dashboard
        dashboard = ProjectDashboard(
            project_name=charter.get("project_name", "Untitled Project"),
            vision=charter.get("vision", "No vision defined"),
            goals=charter.get("goals", [])
        )
        
        # Add plan info
        if plan:
            dashboard.current_phase = self._get_current_phase(plan)
        
        # Add WBS info
        if wbs:
            dashboard.total_tasks = self._count_total_tasks(wbs)
            dashboard.completed_tasks = self._count_completed_tasks(wbs)
            dashboard.progress_percentage = self._calculate_progress(wbs)
            dashboard.in_progress_task = self._get_current_task(wbs)
            dashboard.next_tasks = self._get_next_tasks(wbs, count=3)
            dashboard.recent_completions = self._get_recent_completions(wbs, count=3)
        
        return dashboard

    def _load_charter(self) -> Dict[str, Any]:
        """Load project charter."""
        return utils.read_json(self.charter_file, default={})

    def _load_plan(self) -> Dict[str, Any]:
        """Load project plan."""
        return utils.read_json(self.plan_file, default={})

    def _load_wbs(self) -> Dict[str, Any]:
        """Load WBS data."""
        return utils.read_json(self.wbs_file, default={})

    def _get_current_phase(self, plan: Dict[str, Any]) -> str:
        """Determine current phase from plan."""
        phases = plan.get("phases", [])
        
        for phase in phases:
            if phase.get("status") == "in_progress":
                return phase.get("name", "unknown")
        
        # If no in-progress phase, find first not-completed
        for phase in phases:
            if phase.get("status") != "completed":
                return phase.get("name", "unknown")
        
        return "unknown"

    def _count_total_tasks(self, wbs: Dict[str, Any]) -> int:
        """Count total tasks in WBS."""
        tasks = wbs.get("tasks", [])
        return len(tasks)

    def _count_completed_tasks(self, wbs: Dict[str, Any]) -> int:
        """Count completed tasks."""
        tasks = wbs.get("tasks", [])
        return sum(1 for task in tasks if task.get("status") == "completed")

    def _calculate_progress(self, wbs: Dict[str, Any]) -> float:
        """Calculate completion percentage."""
        total = self._count_total_tasks(wbs)
        if total == 0:
            return 0.0
        
        completed = self._count_completed_tasks(wbs)
        return (completed / total) * 100.0

    def _get_current_task(self, wbs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get the current in-progress task."""
        tasks = wbs.get("tasks", [])
        
        for task in tasks:
            if task.get("status") == "in_progress":
                return {
                    "id": task.get("id"),
                    "name": task.get("name"),
                    "description": task.get("description", ""),
                    "phase": task.get("phase", "unknown")
                }
        
        return None

    def _get_next_tasks(self, wbs: Dict[str, Any], count: int = 3) -> List[Dict[str, Any]]:
        """Get next N tasks to be done."""
        tasks = wbs.get("tasks", [])
        next_tasks = []
        
        for task in tasks:
            if task.get("status") == "pending":
                next_tasks.append({
                    "id": task.get("id"),
                    "name": task.get("name"),
                    "description": task.get("description", ""),
                    "phase": task.get("phase", "unknown")
                })
                
                if len(next_tasks) >= count:
                    break
        
        return next_tasks

    def _get_recent_completions(self, wbs: Dict[str, Any], count: int = 3) -> List[str]:
        """Get recently completed task names."""
        tasks = wbs.get("tasks", [])
        completed = [
            task.get("name", "Unknown task")
            for task in tasks
            if task.get("status") == "completed"
        ]
        
        # Return last N completed (most recent)
        return completed[-count:] if completed else []

    def show_systematic_path(self) -> str:
        """Show clear systematic execution path."""
        dashboard = self.get_dashboard()
        
        lines = []
        lines.append("📋 **Project Execution Path**")
        lines.append("=" * 60)
        
        # Current position
        lines.append(f"\n📍 **Current Position**")
        lines.append(f"   Phase: {dashboard.current_phase}")
        lines.append(f"   Progress: {dashboard.progress_percentage:.1f}% complete")
        lines.append(f"   ({dashboard.completed_tasks}/{dashboard.total_tasks} tasks)")
        
        # What's happening now
        if dashboard.in_progress_task:
            task = dashboard.in_progress_task
            lines.append(f"\n🔄 **Currently Working On**")
            lines.append(f"   {task['id']}: {task['name']}")
            if task.get('description'):
                lines.append(f"   └─ {task['description']}")
        
        # What's next
        if dashboard.next_tasks:
            lines.append(f"\n📝 **Next Steps** (in order)")
            for i, task in enumerate(dashboard.next_tasks, 1):
                lines.append(f"   {i}. {task['name']}")
                if task.get('description'):
                    lines.append(f"      └─ {task['description']}")
        
        # Recent completions
        if dashboard.recent_completions:
            lines.append(f"\n✅ **Recently Completed**")
            for completion in dashboard.recent_completions:
                lines.append(f"   • {completion}")
        
        return "\n".join(lines)

    def get_status_summary(self) -> str:
        """Get a brief status summary for quick checks."""
        dashboard = self.get_dashboard()
        
        summary = []
        summary.append(f"📊 **{dashboard.project_name}**")
        summary.append(f"   {dashboard.progress_percentage:.0f}% complete | {dashboard.current_phase}")
        
        if dashboard.in_progress_task:
            summary.append(f"   Current: {dashboard.in_progress_task['name']}")
        
        if dashboard.next_tasks:
            summary.append(f"   Next: {dashboard.next_tasks[0]['name']}")
        
        return "\n".join(summary)


def get_unified_project_view(project_root: Path) -> UnifiedProjectView:
    """Get unified project view for the project."""
    return UnifiedProjectView(project_root)

