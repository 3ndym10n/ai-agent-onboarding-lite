"""
WBS Synchronization Engine (T4.14) - Ensures all WBS views stay synchronized.

This module provides a centralized synchronization framework for WBS data access,
ensuring consistency across dashboard views, CLI displays, critical path analysis,
and all other WBS-dependent components.
"""

import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from . import utils
from .tool_usage_tracker import track_tool_usage


@dataclass
class SynchronizationEvent:
    """Represents a WBS synchronization event."""

    event_type: str  # 'load', 'update', 'invalidate', 'sync'
    timestamp: float
    source: str  # Component that triggered the event
    data: Dict[str, Any] = field(default_factory=dict)
    affected_views: Set[str] = field(default_factory=set)


@dataclass
class ViewCache:
    """Cache for a specific WBS view."""

    view_name: str
    data: Dict[str, Any]
    timestamp: float
    ttl: int = 300  # 5 minutes default TTL


class WBSSynchronizationEngine:
    """
    Central synchronization engine for WBS data access and consistency.

    This engine ensures that all WBS views remain synchronized by:
    1. Providing centralized data access with caching
    2. Validating data consistency across views
    3. Broadcasting synchronization events
    4. Managing cache invalidation
    5. Ensuring atomic updates
    """

    def __init__(self, root: Path):
        self.root = root
        self.project_plan_path = root / ".ai_onboard" / "project_plan.json"
        self.cache_dir = root / ".ai_onboard" / "wbs_cache"
        self.events_log_path = root / ".ai_onboard" / "wbs_sync_events.jsonl"

        # Ensure directories exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Thread safety
        self._lock = threading.RLock()

        # Cache storage
        self._view_caches: Dict[str, ViewCache] = {}
        self._master_data: Optional[Dict[str, Any]] = None
        self._master_timestamp: float = 0.0

        # Event system
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._event_queue: List[SynchronizationEvent] = []

        # Data validators
        self._validators: List[Callable] = [
            self._validate_wbs_structure,
            self._validate_task_references,
            self._validate_completion_consistency,
        ]

        # View dependencies (what views depend on what data)
        self._view_dependencies: Dict[str, Set[str]] = {
            "dashboard": {
                "work_breakdown_structure",
                "executive_summary",
                "milestones",
            },
            "critical_path": {"work_breakdown_structure"},
            "progress": {"work_breakdown_structure", "executive_summary"},
            "task_priorities": {"work_breakdown_structure"},
            "wbs_analysis": {"work_breakdown_structure"},
        }

    def get_wbs_data(
        self, view_name: str = "default", use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get synchronized WBS data for a specific view.

        Args:
            view_name: Name of the view requesting data
            use_cache: Whether to use cached data if available

        Returns:
            Synchronized WBS data
        """
        track_tool_usage(
            "wbs_synchronization_engine",
            "data_access",
            {"action": "get_wbs_data", "view": view_name, "cache": use_cache},
            "success",
        )

        with self._lock:
            # Check if we need to reload master data
            if self._should_reload_master_data():
                self._load_master_data()

            # Check cache for this view
            if use_cache and view_name in self._view_caches:
                cache = self._view_caches[view_name]
                if not self._is_cache_expired(cache):
                    return cache.data.copy()

            # Generate view data
            view_data = self._generate_view_data(view_name)

            # Cache the result
            self._view_caches[view_name] = ViewCache(
                view_name=view_name, data=view_data, timestamp=time.time()
            )

            # Record access event
            self._record_event(
                SynchronizationEvent(
                    event_type="load",
                    timestamp=time.time(),
                    source=view_name,
                    data={"cached": False},
                )
            )

            return view_data.copy()

    def update_wbs_data(self, updates: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Atomically update WBS data and synchronize all dependent views.

        Args:
            updates: Data updates to apply
            source: Component making the update

        Returns:
            Update result with success status and affected views
        """
        track_tool_usage(
            "wbs_synchronization_engine",
            "data_update",
            {
                "action": "update_wbs_data",
                "source": source,
                "update_keys": list(updates.keys()),
            },
            "success",
        )

        with self._lock:
            # Load current data
            if self._master_data is None:
                self._load_master_data()

            if self._master_data is None:
                return {"success": False, "error": "Could not load WBS data for update"}

            # Create backup
            backup_result = self._create_backup()
            if not backup_result["success"]:
                return backup_result

            # Apply updates
            original_data = self._master_data.copy()
            try:
                self._apply_updates(updates)

                # Validate consistency
                validation_result = self._validate_data_consistency()
                if not validation_result["valid"]:
                    # Restore from backup
                    self._master_data = original_data
                    return {
                        "success": False,
                        "error": f"Validation failed: {validation_result['errors']}",
                    }

                # Save to disk
                save_result = self._save_master_data()
                if not save_result["success"]:
                    self._master_data = original_data
                    return save_result

                # Update timestamp
                self._master_timestamp = time.time()

                # Invalidate affected caches
                affected_views = self._invalidate_affected_caches(updates)

                # Broadcast update event
                self._record_event(
                    SynchronizationEvent(
                        event_type="update",
                        timestamp=time.time(),
                        source=source,
                        data={
                            "updates": updates,
                            "affected_views": list(affected_views),
                        },
                        affected_views=affected_views,
                    )
                )

                # Notify event handlers
                self._notify_event_handlers("update", affected_views)

                return {
                    "success": True,
                    "affected_views": list(affected_views),
                    "timestamp": self._master_timestamp,
                }

            except Exception as e:
                # Restore on any error
                self._master_data = original_data
                return {"success": False, "error": f"Update failed: {str(e)}"}

    def invalidate_view_cache(self, view_name: str) -> bool:
        """
        Invalidate cache for a specific view.

        Args:
            view_name: Name of view to invalidate

        Returns:
            True if cache was invalidated
        """
        with self._lock:
            if view_name in self._view_caches:
                del self._view_caches[view_name]
                self._record_event(
                    SynchronizationEvent(
                        event_type="invalidate",
                        timestamp=time.time(),
                        source="system",
                        data={"view": view_name},
                    )
                )
                return True
            return False

    def invalidate_all_caches(self) -> int:
        """
        Invalidate all view caches.

        Returns:
            Number of caches invalidated
        """
        with self._lock:
            count = len(self._view_caches)
            self._view_caches.clear()
            self._record_event(
                SynchronizationEvent(
                    event_type="invalidate",
                    timestamp=time.time(),
                    source="system",
                    data={"all_caches": True, "count": count},
                )
            )
            return count

    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register an event handler for synchronization events.

        Args:
            event_type: Type of event to handle
            handler: Function to call when event occurs
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    def get_data_consistency_report(self) -> Dict[str, Any]:
        """
        Generate a report on WBS data consistency.

        Returns:
            Consistency report with validation results
        """
        with self._lock:
            if self._master_data is None:
                self._load_master_data()

            if self._master_data is None:
                return {"valid": False, "error": "Could not load WBS data"}

            validation_result = self._validate_data_consistency()
            cache_status = self._get_cache_status()

            return {
                "valid": validation_result["valid"],
                "errors": validation_result.get("errors", []),
                "warnings": validation_result.get("warnings", []),
                "cache_status": cache_status,
                "master_timestamp": self._master_timestamp,
                "last_check": time.time(),
            }

    def sync_all_views(self) -> Dict[str, Any]:
        """
        Force synchronization of all views.

        Returns:
            Synchronization results
        """
        with self._lock:
            self.invalidate_all_caches()

            # Reload master data
            self._load_master_data()

            # Broadcast sync event
            self._record_event(
                SynchronizationEvent(
                    event_type="sync",
                    timestamp=time.time(),
                    source="system",
                    data={"forced": True},
                )
            )

            # Notify all handlers
            self._notify_event_handlers("sync", set(self._view_dependencies.keys()))

            return {
                "success": True,
                "timestamp": time.time(),
                "message": "All views synchronized",
            }

    def _should_reload_master_data(self) -> bool:
        """Check if master data needs to be reloaded from disk."""
        if self._master_data is None:
            return True

        try:
            if self.project_plan_path.exists():
                file_mtime = self.project_plan_path.stat().st_mtime
                return file_mtime > self._master_timestamp
        except Exception:
            pass

        return False

    def _load_master_data(self) -> None:
        """Load master WBS data from disk."""
        try:
            if self.project_plan_path.exists():
                self._master_data = utils.read_json(
                    self.project_plan_path, default=None
                )
                self._master_timestamp = time.time()
            else:
                self._master_data = None
        except Exception as e:
            print(f"Warning: Failed to load WBS data: {e}")
            self._master_data = None

    def _generate_view_data(self, view_name: str) -> Dict[str, Any]:
        """Generate view-specific data from master data."""
        if self._master_data is None:
            return {}

        # Get view dependencies
        dependencies = self._view_dependencies.get(view_name, set())

        # Extract relevant data
        view_data = {}
        for dep in dependencies:
            if dep in self._master_data:
                view_data[dep] = self._master_data[dep]

        # Add view-specific processing
        if view_name == "dashboard":
            view_data = self._generate_dashboard_view(view_data)
        elif view_name == "critical_path":
            view_data = self._generate_critical_path_view(view_data)
        elif view_name == "progress":
            view_data = self._generate_progress_view(view_data)

        return view_data

    def _generate_dashboard_view(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dashboard-specific view data."""
        wbs = base_data.get("work_breakdown_structure", {})

        # Calculate milestone progress
        milestones = []
        for phase_key, phase_data in wbs.items():
            if not phase_key.endswith(".0"):
                continue

            phase_name = phase_data.get("name", phase_key)
            subtasks = phase_data.get("subtasks", {})

            if subtasks:
                total_tasks = len(subtasks)
                completed_tasks = sum(
                    1 for task in subtasks.values() if task.get("status") == "completed"
                )
                progress_percentage = int(completed_tasks / total_tasks * 100)
            else:
                progress_percentage = (
                    100 if phase_data.get("status") == "completed" else 0
                )

            milestones.append(
                {
                    "name": phase_name,
                    "progress_percentage": progress_percentage,
                    "status": phase_data.get("status", "pending"),
                }
            )

        return {
            **base_data,
            "dashboard_milestones": milestones,
            "generated_at": time.time(),
        }

    def _generate_critical_path_view(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate critical path analysis view data."""
        # Add critical path specific data
        return {**base_data, "critical_path_ready": True, "generated_at": time.time()}

    def _generate_progress_view(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate progress analysis view data."""
        wbs = base_data.get("work_breakdown_structure", {})

        # Calculate overall progress
        total_tasks = 0
        completed_tasks = 0

        for phase_key, phase_data in wbs.items():
            if not phase_key.endswith(".0"):
                continue

            subtasks = phase_data.get("subtasks", {})
            for subtask_data in subtasks.values():
                total_tasks += 1
                if subtask_data.get("status") == "completed":
                    completed_tasks += 1

        overall_progress = (
            int(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        )

        return {
            **base_data,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "overall_progress": overall_progress,
            "generated_at": time.time(),
        }

    def _apply_updates(self, updates: Dict[str, Any]) -> None:
        """Apply updates to master data."""

        def deep_update(base: Dict[str, Any], update: Dict[str, Any]) -> None:
            for key, value in update.items():
                if (
                    isinstance(value, dict)
                    and key in base
                    and isinstance(base[key], dict)
                ):
                    deep_update(base[key], value)
                else:
                    base[key] = value

        deep_update(self._master_data, updates)

    def _validate_data_consistency(self) -> Dict[str, Any]:
        """Validate consistency of WBS data."""
        if self._master_data is None:
            return {"valid": False, "errors": ["No data to validate"]}

        errors = []
        warnings = []

        # Run all validators
        for validator in self._validators:
            try:
                result = validator(self._master_data)
                if result.get("errors"):
                    errors.extend(result["errors"])
                if result.get("warnings"):
                    warnings.extend(result["warnings"])
            except Exception as e:
                errors.append(f"Validator error: {str(e)}")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _validate_wbs_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate WBS structural integrity."""
        errors = []
        warnings = []

        wbs = data.get("work_breakdown_structure", {})

        if not wbs:
            errors.append("Missing work_breakdown_structure")
            return {"errors": errors, "warnings": warnings}

        for phase_key, phase_data in wbs.items():
            if not isinstance(phase_data, dict):
                errors.append(f"Invalid phase data for {phase_key}")
                continue

            # Check required fields
            if "name" not in phase_data:
                warnings.append(f"Phase {phase_key} missing name")
            if "status" not in phase_data:
                warnings.append(f"Phase {phase_key} missing status")

            # Validate subtasks
            subtasks = phase_data.get("subtasks", {})
            if not isinstance(subtasks, dict):
                errors.append(f"Invalid subtasks for phase {phase_key}")
                continue

            for subtask_key, subtask_data in subtasks.items():
                if not isinstance(subtask_data, dict):
                    errors.append(f"Invalid subtask data for {subtask_key}")
                    continue

                if "name" not in subtask_data:
                    warnings.append(f"Subtask {subtask_key} missing name")

        return {"errors": errors, "warnings": warnings}

    def _validate_task_references(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate task references and dependencies."""
        errors = []
        warnings = []

        wbs = data.get("work_breakdown_structure", {})

        # Build task ID index
        task_ids = set()
        for phase_key, phase_data in wbs.items():
            if not phase_key.endswith(".0"):
                continue

            subtasks = phase_data.get("subtasks", {})
            for subtask_key in subtasks:
                task_ids.add(subtask_key)

        # Check for duplicate task IDs (basic check)
        seen_ids = set()
        for task_id in task_ids:
            if task_id in seen_ids:
                errors.append(f"Duplicate task ID: {task_id}")
            seen_ids.add(task_id)

        return {"errors": errors, "warnings": warnings}

    def _validate_completion_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate task completion consistency."""
        errors = []
        warnings = []

        wbs = data.get("work_breakdown_structure", {})

        for phase_key, phase_data in wbs.items():
            if not phase_key.endswith(".0"):
                continue

            subtasks = phase_data.get("subtasks", {})
            phase_completed = phase_data.get("status") == "completed"

            if phase_completed and subtasks:
                # If phase is completed, all subtasks should be completed
                incomplete_subtasks = [
                    subtask_key
                    for subtask_key, subtask_data in subtasks.items()
                    if subtask_data.get("status") != "completed"
                ]

                if incomplete_subtasks:
                    warnings.append(
                        f"Phase {phase_key} marked completed but has incomplete subtasks: "
                        f"{', '.join(incomplete_subtasks)}"
                    )

        return {"errors": errors, "warnings": warnings}

    def _invalidate_affected_caches(self, updates: Dict[str, Any]) -> Set[str]:
        """Invalidate caches for views affected by the updates."""
        affected_views = set()

        # Determine which data sections were updated
        updated_sections = set()

        def collect_sections(data: Any, path: str = ""):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    updated_sections.add(current_path)
                    collect_sections(value, current_path)

        collect_sections(updates)

        # Find views that depend on updated sections
        for view_name, dependencies in self._view_dependencies.items():
            if any(
                dep in updated_sections
                or any(dep in section for section in updated_sections)
                for dep in dependencies
            ):
                affected_views.add(view_name)
                if view_name in self._view_caches:
                    del self._view_caches[view_name]

        return affected_views

    def _is_cache_expired(self, cache: ViewCache) -> bool:
        """Check if a cache entry has expired."""
        return time.time() - cache.timestamp > cache.ttl

    def _create_backup(self) -> Dict[str, Any]:
        """Create a backup of current WBS data."""
        try:
            backup_path = self.cache_dir / f"wbs_backup_{int(time.time())}.json"
            if self._master_data:
                utils.write_json(backup_path, self._master_data)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": f"Backup failed: {str(e)}"}

    def _save_master_data(self) -> Dict[str, Any]:
        """Save master data to disk."""
        try:
            if self._master_data:
                utils.write_json(self.project_plan_path, self._master_data)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": f"Save failed: {str(e)}"}

    def _notify_event_handlers(self, event_type: str, affected_views: Set[str]) -> None:
        """Notify registered event handlers."""
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(event_type, affected_views)
                except Exception as e:
                    print(f"Warning: Event handler failed: {e}")

    def _record_event(self, event: SynchronizationEvent) -> None:
        """Record a synchronization event."""
        try:
            with open(self.events_log_path, "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "event_type": event.event_type,
                            "timestamp": event.timestamp,
                            "source": event.source,
                            "data": event.data,
                            "affected_views": list(event.affected_views),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        except Exception as e:
            print(f"Warning: Failed to record sync event: {e}")

    def _get_cache_status(self) -> Dict[str, Any]:
        """Get status of all caches."""
        status = {}
        for view_name, cache in self._view_caches.items():
            status[view_name] = {
                "age": time.time() - cache.timestamp,
                "ttl": cache.ttl,
                "expired": self._is_cache_expired(cache),
                "size": len(json.dumps(cache.data, default=str)),
            }
        return status


def get_wbs_sync_engine(root: Path = None) -> WBSSynchronizationEngine:
    """
    Get or create the WBS synchronization engine singleton.

    Args:
        root: Project root directory

    Returns:
        WBS synchronization engine instance
    """
    if root is None:
        root = Path.cwd()

    # Simple singleton pattern
    if not hasattr(get_wbs_sync_engine, "_instance"):
        get_wbs_sync_engine._instance = WBSSynchronizationEngine(root)

    return get_wbs_sync_engine._instance


def sync_wbs_views(root: Path = None) -> Dict[str, Any]:
    """
    Convenience function to synchronize all WBS views.

    Args:
        root: Project root directory

    Returns:
        Synchronization results
    """
    engine = get_wbs_sync_engine(root)
    return engine.sync_all_views()
