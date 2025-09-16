"""
Canonical progress computation and visualization utilities.

All components should import from this module to compute project progress
and render progress bars to ensure consistency across CLI, gates, and reports.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from . import utils


def _convert_project_plan_to_legacy_format(
    project_plan: Dict[str, Any],
) -> Dict[str, Any]:
    """Convert project_plan.json format to legacy plan format for compatibility."""
    try:
        wbs = project_plan.get("work_breakdown_structure", {})
        milestones = project_plan.get("milestones", [])

        # Convert WBS to tasks format
        tasks = []
        task_counter = 1

        for phase_id, phase_data in wbs.items():
            # Add main phase as a task
            phase_task = {
                "id": f"phase_{phase_id}",
                "name": phase_data.get("name", f"Phase {phase_id}"),
                "status": phase_data.get("status", "pending"),
                "completion_percentage": phase_data.get("completion_percentage", 0),
                "priority": (
                    "high" if phase_data.get("status") == "in_progress" else "medium"
                ),
            }
            if phase_data.get("completion_date"):
                phase_task["completion_date"] = phase_data.get("completion_date")
            tasks.append(phase_task)

            # Add subtasks
            subtasks = phase_data.get("subtasks", {})
            for subtask_id, subtask_data in subtasks.items():
                subtask = {
                    "id": f"{phase_id}_{subtask_id}",
                    "name": subtask_data.get("name", f"Subtask {subtask_id}"),
                    "status": subtask_data.get("status", "pending"),
                    "completion_percentage": subtask_data.get("completion", 0),
                    "priority": "medium",
                }
                if subtask_data.get("completion_date"):
                    subtask["completion_date"] = subtask_data.get("completion_date")
                tasks.append(subtask)

        # Convert milestones to legacy format
        legacy_milestones: List[Dict[str, Any]] = []
        for milestone in milestones:
            legacy_milestone = {
                "id": milestone.get("id", f"milestone_{len(legacy_milestones) + 1}"),
                "name": milestone.get("name", ""),
                "status": milestone.get("status", "pending"),
                "target_date": milestone.get("date"),
                "priority": (
                    "high" if milestone.get("status") == "in_progress" else "medium"
                ),
            }
            legacy_milestones.append(legacy_milestone)

        return {
            "tasks": tasks,
            "milestones": legacy_milestones,
            "project_name": project_plan.get("project_name", ""),
            "completion_percentage": project_plan.get("executive_summary", {}).get(
                "completion_percentage", 0
            ),
        }
    except Exception as e:
        # Fallback to empty structure if conversion fails
        return {"tasks": [], "milestones": []}


def load_plan(root: Path) -> Dict[str, Any]:
    """Load the plan JSON from .ai_onboard / project_plan.json, or an empty stub."""
    # Try project_plan.json first (new format), then fallback to plan.json (legacy)
    project_plan_path = root / ".ai_onboard" / "project_plan.json"
    legacy_plan_path = root / ".ai_onboard" / "plan.json"

    if project_plan_path.exists():
        plan_data = utils.read_json(project_plan_path, default={})
        # Convert project_plan.json format to expected format
        return _convert_project_plan_to_legacy_format(plan_data)
    elif legacy_plan_path.exists():
        return utils.read_json(
            legacy_plan_path, default={"tasks": [], "milestones": []}
        )
    else:
        return {"tasks": [], "milestones": []}


def create_progress_bar(percentage: float, width: int = 20) -> str:
    """Create an ASCII / Unicode progress bar for a percentage using canonical logic.

    - percentage is clamped to [0, 100]
    - filled cells computed with rounding instead of truncation
    - width is respected strictly
    """
    # Clamp
    percentage = max(0.0, min(100.0, float(percentage)))

    # Compute bar fill using rounding for better visual accuracy
    filled = round(width * percentage / 100)
    if filled > width:
        filled = width
    if filled < 0:
        filled = 0

    bar = "█" * filled + "░" * (width - filled)
    return f"{bar} {percentage:.1f}%"


def compute_overall_progress(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Compute overall project progress from a plan object.

    Returns a dictionary with completion stats and a canonical progress bar string.
    """
    tasks: List[Dict[str, Any]] = plan.get("tasks", [])
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.get("status") == "completed"])
    in_progress_tasks = len([t for t in tasks if t.get("status") == "in_progress"])
    pending_tasks = len([t for t in tasks if t.get("status") == "pending"])

    pct = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "pending_tasks": pending_tasks,
        "completion_percentage": round(pct, 1),
        "visual_bar": create_progress_bar(pct, width=20),
    }


def compute_milestone_progress(
    plan: Dict[str, Any], width: int = 15
) -> List[Dict[str, Any]]:
    """Compute progress for each milestone in the plan.

    Progress is task - count based to match existing semantics.
    """
    milestones: List[Dict[str, Any]] = plan.get("milestones", [])
    tasks_index: Dict[str, Dict[str, Any]] = {
        t.get("id"): t for t in plan.get("tasks", [])
    }

    results: List[Dict[str, Any]] = []
    for ms in milestones:
        name = ms.get("name", "")
        task_ids: List[str] = ms.get("tasks", [])
        if not task_ids:
            continue

        completed = 0
        for tid in task_ids:
            t = tasks_index.get(tid)
            if t and t.get("status") == "completed":
                completed += 1

        progress_pct = (completed / len(task_ids) * 100) if task_ids else 0.0
        status = "completed" if progress_pct == 100 else "in_progress"

        results.append(
            {
                "name": name,
                "completed_tasks": completed,
                "total_tasks": len(task_ids),
                "progress_percentage": round(progress_pct, 1),
                "status": status,
                "target_date": ms.get("target_date"),
                "priority": ms.get("priority", "medium"),
                "visual_bar": create_progress_bar(progress_pct, width=width),
            }
        )

    # Sort by most complete first
    results.sort(key=lambda x: x["progress_percentage"], reverse=True)
    return results
