"""Unified Project Management Engine."""

from __future__ import annotations

import json
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

from . import progress_utils, utils
from .tool_usage_tracker import track_tool_usage


@dataclass
class ProjectPlanSnapshot:
    """Snapshot of project plan data loaded through the gateway."""

    raw: Dict[str, Any]
    path: Path


class ProjectDataGateway:
    """Canonical access layer for project plan artifacts."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.plan_dir = root_path / ".ai_onboard"
        self.project_plan_path = self.plan_dir / "project_plan.json"
        self.legacy_plan_path = self.plan_dir / "plan.json"
        self.roadmap_path = self.plan_dir / "roadmap.json"
        self.pending_tasks_path = self.plan_dir / "pending_tasks.json"
        self.learning_events_path = self.plan_dir / "learning_events.jsonl"
        self._cache: Optional[ProjectPlanSnapshot] = None
        self._lock = RLock()

    def _load_json(
        self, path: Path, default: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not path.exists():
            return default or {}
        return utils.read_json(path, default=default or {})

    def load_project_plan(self, force_reload: bool = False) -> ProjectPlanSnapshot:
        with self._lock:
            if self._cache and not force_reload:
                return self._cache

            data = self._load_json(self.project_plan_path, default={})
            if not data and self.legacy_plan_path.exists():
                data = self._load_json(self.legacy_plan_path, default={})

            snapshot = ProjectPlanSnapshot(raw=data, path=self.project_plan_path)
            self._cache = snapshot
            return snapshot

    def write_project_plan(self, data: Dict[str, Any]) -> None:
        with self._lock:
            self._ensure_backup()
            utils.write_json(self.project_plan_path, data)
            self._cache = ProjectPlanSnapshot(raw=data, path=self.project_plan_path)

    def _ensure_backup(self) -> None:
        backup_dir = self.plan_dir / "wbs_backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        if self.project_plan_path.exists():
            utils.create_timestamped_backup(self.project_plan_path, backup_dir)

    def load_roadmap(self) -> Dict[str, Any]:
        return self._load_json(self.roadmap_path, default={})

    def load_pending_tasks(self) -> Dict[str, Any]:
        return self._load_json(self.pending_tasks_path, default={"pending_tasks": []})

    def load_learning_events(self) -> List[Dict[str, Any]]:
        if not self.learning_events_path.exists():
            return []
        records: List[Dict[str, Any]] = []
        with self.learning_events_path.open("r", encoding="utf-8") as stream:
            for line in stream:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return records

    def append_learning_event(self, event: Dict[str, Any]) -> None:
        self.learning_events_path.parent.mkdir(parents=True, exist_ok=True)
        with self.learning_events_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event) + "\n")

    def invalidate_cache(self) -> None:
        with self._lock:
            self._cache = None


class TaskLifecycleService:
    """Consolidated task discovery, prioritization, and completion handling."""

    def __init__(self, gateway: ProjectDataGateway):
        self.gateway = gateway

    def _flatten_tasks(
        self, plan: Dict[str, Any]
    ) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
        wbs = plan.get("work_breakdown_structure", {})
        tasks: Dict[str, Dict[str, Any]] = {}
        for phase_id, phase_data in wbs.items():
            phase_copy = dict(phase_data)
            phase_copy["task_type"] = "phase"
            tasks[phase_id] = phase_copy
            for subtask_id, subtask in phase_data.get("subtasks", {}).items():
                full_id = (
                    f"{phase_id}.{subtask_id}" if "." not in subtask_id else subtask_id
                )
                sub_copy = dict(subtask)
                sub_copy["task_type"] = "subtask"
                sub_copy["parent_phase"] = phase_id
                tasks[full_id] = sub_copy
        return tasks, wbs

    def prioritize_tasks(self) -> Dict[str, Any]:
        start = time.time()
        snapshot = self.gateway.load_project_plan()
        plan = snapshot.raw
        tasks, _ = self._flatten_tasks(plan)
        critical_path = set(plan.get("critical_path", []))
        priorities: Dict[str, Dict[str, Any]] = {}
        for task_id, task in tasks.items():
            score = 0
            reasons: List[str] = []
            if task_id in critical_path or task.get("is_critical_path"):
                score += 40
                reasons.append("Critical path task")
            dependencies = task.get("dependencies", [])
            dep_count = len(dependencies) if isinstance(dependencies, list) else 0
            if dep_count > 0:
                score += min(20, dep_count * 5)
                reasons.append(f"Depends on {dep_count} tasks")
            effort = task.get("effort_days") or task.get("effort")
            if effort:
                score += 10 if effort <= 2 else 5
                reasons.append("Effort considered")
            risk = task.get("risk", "medium")
            if risk == "high":
                score += 15
            elif risk == "low":
                score += 5
            status = task.get("status", "pending")
            if status == "pending":
                score += 10
            priority_level = self._score_to_priority(score)
            priorities[task_id] = {
                "task_name": task.get("name", task_id),
                "calculated_priority": priority_level,
                "priority_score": score,
                "priority_factors": reasons,
                "status": status,
            }
        duration = time.time() - start
        track_tool_usage(
            "unified_project_management",
            "task_service",
            {
                "action": "prioritize",
                "task_count": len(priorities),
                "duration": duration,
            },
            "success",
        )
        return {
            "task_priorities": priorities,
            "analysis_timestamp": utils.now_iso(),
            "total_tasks": len(priorities),
            "duration_seconds": duration,
        }

    def _score_to_priority(self, score: int) -> str:
        if score >= 60:
            return "high"
        if score >= 35:
            return "medium"
        return "low"

    def detect_completions(self) -> Dict[str, Any]:
        start = time.time()
        snapshot = self.gateway.load_project_plan()
        plan = snapshot.raw
        tasks, _ = self._flatten_tasks(plan)
        completed = []
        newly_completed = []
        now = utils.now_iso()
        for task_id, task in tasks.items():
            if task.get("status") == "completed":
                completed.append(task_id)
                if not task.get("completion_date"):
                    task["completion_date"] = now
                    newly_completed.append(
                        {"task_id": task_id, "name": task.get("name", task_id)}
                    )
        if newly_completed:
            self.gateway.write_project_plan(plan)
        breakdown = self._completion_by_category(tasks)
        duration = time.time() - start
        track_tool_usage(
            "unified_project_management",
            "task_service",
            {
                "action": "detect_completions",
                "total_tasks": len(tasks),
                "new": len(newly_completed),
                "duration": duration,
            },
            "success",
        )
        return {
            "completed_tasks": len(completed),
            "total_tasks": len(tasks),
            "newly_completed": len(newly_completed),
            "new_completions": newly_completed,
            "completion_by_category": breakdown,
            "analysis_timestamp": now,
            "duration_seconds": duration,
        }

    def _completion_by_category(
        self, tasks: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        breakdown: Dict[str, Dict[str, Any]] = {}
        for task_id, task in tasks.items():
            category = task.get("parent_phase", task_id)
            bucket = breakdown.setdefault(category, {"completed": 0, "total": 0})
            bucket["total"] += 1
            if task.get("status") == "completed":
                bucket["completed"] += 1
        return breakdown


class WBSSynchronizationService:
    """Handles WBS status queries and updates."""

    def __init__(self, gateway: ProjectDataGateway):
        self.gateway = gateway

    def get_status(self) -> Dict[str, Any]:
        start = time.time()
        snapshot = self.gateway.load_project_plan()
        plan = snapshot.raw
        wbs = plan.get("work_breakdown_structure", {})
        total = len(wbs)
        completed = len(
            [1 for pdata in wbs.values() if pdata.get("status") == "completed"]
        )
        result = {
            "total_elements": total,
            "completed": completed,
            "consistency_score": self._calculate_consistency(plan),
            "hierarchy_summary": self._hierarchy_summary(wbs),
        }
        duration = time.time() - start
        track_tool_usage(
            "unified_project_management",
            "wbs_service",
            {
                "action": "status",
                "total": total,
                "completed": completed,
                "duration": duration,
            },
            "success",
        )
        result["duration_seconds"] = duration
        return result

    def update_task(self, task_id: str, status: str) -> Dict[str, Any]:
        snapshot = self.gateway.load_project_plan()
        plan = dict(snapshot.raw)
        wbs = plan.setdefault("work_breakdown_structure", {})
        if task_id in wbs:
            wbs[task_id]["status"] = status
            self.gateway.write_project_plan(plan)
            return {"success": True, "updated_task": task_id}
        for phase_id, phase in wbs.items():
            subtasks = phase.get("subtasks", {})
            if task_id in subtasks:
                subtasks[task_id]["status"] = status
                self.gateway.write_project_plan(plan)
                return {"success": True, "updated_task": task_id}
        return {"success": False, "error": "task_not_found"}

    def _calculate_consistency(self, plan: Dict[str, Any]) -> float:
        milestones = plan.get("milestones", [])
        completed = len([m for m in milestones if m.get("status") == "completed"])
        total = len(milestones) or 1
        return round((completed / total) * 100, 1)

    def _hierarchy_summary(self, wbs: Dict[str, Any]) -> Dict[str, int]:
        summary: Dict[str, int] = {"phases": len(wbs), "subtasks": 0}
        for phase in wbs.values():
            summary["subtasks"] += len(phase.get("subtasks", {}))
        return summary


class ProgressAnalyticsService:
    """Generates progress summaries from consolidated plan data."""

    def __init__(self, gateway: ProjectDataGateway):
        self.gateway = gateway

    def get_project_status(self) -> Dict[str, Any]:
        start = time.time()
        snapshot = self.gateway.load_project_plan()
        plan = snapshot.raw
        overall = progress_utils.compute_overall_progress(plan)
        milestone_progress = progress_utils.compute_milestone_progress(plan, width=20)
        recent = self._recent_activity()
        duration = time.time() - start
        track_tool_usage(
            "unified_project_management",
            "analytics_service",
            {
                "action": "project_status",
                "milestones": len(milestone_progress),
                "duration": duration,
            },
            "success",
        )
        return {
            "project_name": plan.get("project_name", "Unknown Project"),
            "completion_percentage": overall.get("completion_percentage", 0),
            "completed_tasks": overall.get("completed_tasks", 0),
            "total_tasks": overall.get("total_tasks", 0),
            "milestones": milestone_progress,
            "critical_path": plan.get("critical_path", []),
            "recent_activity": recent,
            "duration_seconds": duration,
        }

    def _recent_activity(self) -> List[Dict[str, Any]]:
        events = self.gateway.load_learning_events()
        latest = sorted(events, key=lambda e: e.get("timestamp", ""), reverse=True)
        return latest[:5]


class UnifiedProjectManagementEngine:
    """Facade providing consolidated project management capabilities."""

    _instances: Dict[Path, "UnifiedProjectManagementEngine"] = {}
    _instances_lock = RLock()

    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.gateway = ProjectDataGateway(self.root_path)
        self.tasks = TaskLifecycleService(self.gateway)
        self.wbs = WBSSynchronizationService(self.gateway)
        self.analytics = ProgressAnalyticsService(self.gateway)

    @classmethod
    def get_instance(cls, root_path: Path) -> "UnifiedProjectManagementEngine":
        root = Path(root_path)
        with cls._instances_lock:
            if root not in cls._instances:
                cls._instances[root] = cls(root)
            return cls._instances[root]


# Compatibility helpers


def get_unified_project_management_engine(
    root_path: Path,
) -> UnifiedProjectManagementEngine:
    return UnifiedProjectManagementEngine.get_instance(root_path)


def get_legacy_wbs_sync_engine(root_path: Path) -> WBSSynchronizationService:
    warnings.warn(
        "Legacy WBS sync engine call is deprecated; use UnifiedProjectManagementEngine.wbs",
        DeprecationWarning,
        stacklevel=2,
    )
    return UnifiedProjectManagementEngine.get_instance(root_path).wbs
