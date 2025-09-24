"""
Task Execution Gate System - Ensures WBS is updated before work begins on tasks.

This module implements a comprehensive gate system that:
1. Validates task states before execution
2. Prevents execution until WBS updates are complete
3. Provides emergency bypass mechanisms
4. Enforces safety protocols for task execution
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from . import utils
from .task_integration_logic import integrate_task
from .tool_usage_tracker import track_tool_usage
from .wbs_synchronization_engine import get_wbs_sync_engine
from .wbs_update_engine import update_wbs_for_task


class TaskExecutionGate:
    """Comprehensive gate system for task execution control."""

    def __init__(self, root: Path):
        self.root = root
        self.pending_tasks_path = root / ".ai_onboard" / "pending_tasks.json"
        self.execution_log_path = root / ".ai_onboard" / "task_execution_log.jsonl"
        self.gate_bypass_log_path = root / ".ai_onboard" / "gate_bypass_log.jsonl"
        self.wbs_sync_engine = get_wbs_sync_engine(root)

        utils.ensure_dir(self.pending_tasks_path.parent)

        # Initialize pending tasks if it doesn't exist
        if not self.pending_tasks_path.exists():
            utils.write_json(
                self.pending_tasks_path,
                {"pending_tasks": [], "last_updated": utils.now_iso()},
            )

        # Gate configuration
        self.gate_config = {
            "strict_mode": True,  # Require all tasks to be WBS-updated
            "auto_update": True,  # Attempt to update WBS automatically
            "emergency_bypass_timeout": 3600,  # 1 hour bypass validity
            "max_blocked_attempts": 3,
            # Allow retries before requiring manual intervention
        }

    def register_new_task(
        self,
        task_data: Dict[str, Any],
        source: str = "unknown",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Register a newly identified task that requires WBS integration.

        Args:
            task_data: Task information
            source: Where the task was identified from (e.g.,
                "error_analysis", "user_request")
            context: Additional context

        Returns:
            Registration result
        """
        # Analyze the task first to see if it needs integration
        integration_result = integrate_task(task_data, context, self.root)

        if integration_result["confidence_score"] < 0.6:
            # Low confidence - don't block, but log for manual review
            self._log_task_registration(task_data, "low_confidence", integration_result)
            return {
                "registered": False,
                "reason": "low_confidence",
                "confidence": integration_result["confidence_score"],
                "message": "Task registered for manual review - confidence too low for auto-integration",
            }

        # Add to pending tasks that require WBS update
        pending_data = utils.read_json(
            self.pending_tasks_path, default={"pending_tasks": []}
        )

        task_registration = {
            "task_id": integration_result["integration_plan"]["task_id"],
            "task_data": task_data,
            "integration_recommendation": integration_result,
            "source": source,
            "context": context or {},
            "registered_at": utils.now_iso(),
            "status": "pending_wbs_update",
            "wbs_updated": False,
            "execution_allowed": False,
        }

        pending_data["pending_tasks"].append(task_registration)
        pending_data["last_updated"] = utils.now_iso()

        utils.write_json(self.pending_tasks_path, pending_data)

        self._log_task_registration(task_data, "registered", integration_result)

        return {
            "registered": True,
            "task_id": task_registration["task_id"],
            "requires_wbs_update": True,
            "message": "Task registered - WBS update required before execution",
        }

    def update_wbs_for_pending_tasks(self) -> Dict[str, Any]:
        """Update WBS for all pending tasks."""
        pending_data = utils.read_json(
            self.pending_tasks_path, default={"pending_tasks": []}
        )
        pending_tasks = pending_data.get("pending_tasks", [])

        updated_count = 0
        failed_count = 0
        results = []

        for task_reg in pending_tasks:
            if not task_reg.get("wbs_updated", False):
                try:
                    # Apply WBS update
                    update_result = update_wbs_for_task(
                        task_reg["task_data"], task_reg.get("context"), self.root
                    )

                    if update_result["success"]:
                        task_reg["wbs_updated"] = True
                        task_reg["wbs_update_result"] = update_result
                        task_reg["execution_allowed"] = True
                        task_reg["updated_at"] = utils.now_iso()
                        updated_count += 1

                        results.append(
                            {
                                "task_id": task_reg["task_id"],
                                "status": "success",
                                "phase_updated": update_result.get("phase_updated"),
                                "update_type": update_result.get("update_type"),
                            }
                        )
                    else:
                        task_reg["wbs_update_result"] = update_result
                        task_reg["last_error"] = update_result.get(
                            "error", "Unknown error"
                        )
                        failed_count += 1

                        results.append(
                            {
                                "task_id": task_reg["task_id"],
                                "status": "failed",
                                "error": update_result.get("error", "Unknown error"),
                            }
                        )

                except Exception as e:
                    task_reg["last_error"] = str(e)
                    failed_count += 1
                    results.append(
                        {
                            "task_id": task_reg["task_id"],
                            "status": "exception",
                            "error": str(e),
                        }
                    )

        # Save updated pending tasks
        pending_data["pending_tasks"] = pending_tasks
        pending_data["last_updated"] = utils.now_iso()
        utils.write_json(self.pending_tasks_path, pending_data)

        return {
            "total_processed": len(pending_tasks),
            "updated": updated_count,
            "failed": failed_count,
            "results": results,
        }

    def check_execution_allowed(self, task_id: str) -> Dict[str, Any]:
        """Check if execution is allowed for a given task."""
        pending_data = utils.read_json(
            self.pending_tasks_path, default={"pending_tasks": []}
        )

        for task_reg in pending_data.get("pending_tasks", []):
            if task_reg.get("task_id") == task_id:
                return {
                    "allowed": task_reg.get("execution_allowed", False),
                    "wbs_updated": task_reg.get("wbs_updated", False),
                    "status": task_reg.get("status", "unknown"),
                    "last_error": task_reg.get("last_error"),
                    "task_info": {
                        "task_id": task_id,
                        "task_name": task_reg.get("task_data", {}).get(
                            "name", "Unknown"
                        ),
                        "registered_at": task_reg.get("registered_at"),
                    },
                }

        return {
            "allowed": True,  # Task not in pending list, assume allowed
            "wbs_updated": False,
            "status": "not_registered",
            "message": "Task not found in pending tasks - assuming execution allowed",
        }

    def check_execution_gates(
        self,
        command: str,
        args: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Check all execution gates for a command before allowing execution.

        Args:
            command: Command being executed
            args: Command arguments
            context: Execution context

        Returns:
            Gate check result with execution permission
        """
        track_tool_usage(
            "task_execution_gate",
            "safety",
            {"action": "check_gates", "command": command},
            "success",
        )

        # Check for active emergency bypass
        bypass_check = self._check_emergency_bypass(command)
        if bypass_check["bypassed"]:
            return {
                "allowed": True,
                "gates_passed": True,
                "bypass_active": True,
                "bypass_reason": bypass_check["reason"],
                "message": f"Execution allowed via emergency bypass: {bypass_check['reason']}",
            }

        # Check for pending tasks that would be affected
        affected_tasks = self._identify_affected_tasks(command, args, context)
        if not affected_tasks:
            return {
                "allowed": True,
                "gates_passed": True,
                "affected_tasks": [],
                "message": "No affected tasks found - execution allowed",
            }

        # Check if all affected tasks are WBS-updated
        gate_violations = []
        wbs_updates_needed = []

        for task_id in affected_tasks:
            task_check = self.check_execution_allowed(task_id)
            if not task_check["allowed"]:
                gate_violations.append(
                    {
                        "task_id": task_id,
                        "reason": "wbs_update_required",
                        "task_name": task_check["task_info"]["task_name"],
                        "status": task_check["status"],
                    }
                )
                wbs_updates_needed.append(task_id)

        if gate_violations:
            # Attempt auto-update if enabled
            if self.gate_config["auto_update"] and wbs_updates_needed:
                auto_update_result = self._attempt_auto_wbs_updates(wbs_updates_needed)
                if auto_update_result["all_updated"]:
                    return {
                        "allowed": True,
                        "gates_passed": True,
                        "auto_updated": True,
                        "updated_tasks": auto_update_result["updated_tasks"],
                        "message": f"Auto-updated {len(auto_update_result['updated_tasks'])} tasks - execution allowed",
                    }

            # Gates failed
            return {
                "allowed": False,
                "gates_passed": False,
                "violations": gate_violations,
                "wbs_updates_needed": wbs_updates_needed,
                "auto_update_attempted": self.gate_config["auto_update"],
                "emergency_bypass_available": True,
                "message": f"Execution blocked: {len(gate_violations)} tasks require WBS updates",
            }

        return {
            "allowed": True,
            "gates_passed": True,
            "affected_tasks": affected_tasks,
            "message": "All gates passed - execution allowed",
        }

    def enforce_execution_gates(
        self,
        command: str,
        args: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Enforce execution gates - block execution if gates fail.

        Args:
            command: Command to execute
            args: Command arguments
            context: Execution context

        Returns:
            Enforcement result - allowed or blocked
        """
        gate_check = self.check_execution_gates(command, args, context)

        if not gate_check["allowed"]:
            # Log the gate violation
            self._log_gate_violation(command, args, gate_check)

            # Increment blocked attempts counter
            self._increment_blocked_attempts(command, args)

            return {
                "allowed": False,
                "reason": "gate_violation",
                "violations": gate_check.get("violations", []),
                "suggested_actions": [
                    "Run 'ai_onboard wbs auto-update' to update WBS",
                    "Run 'ai_onboard task-gate status' to check task states",
                    f'Use emergency bypass: \'ai_onboard task-gate bypass --reason "emergency" --command "{command}"\'',
                ],
                "emergency_bypass_available": True,
                "message": gate_check["message"],
            }

        # Log successful gate check
        self._log_gate_success(command, args, gate_check)

        return gate_check

    def create_emergency_bypass(
        self,
        command: str,
        reason: str,
        authorized_by: str = "system",
        validity_hours: int = 1,
    ) -> Dict[str, Any]:
        """
        Create an emergency bypass for gate enforcement.

        Args:
            command: Command to bypass
            reason: Reason for bypass
            authorized_by: Who authorized the bypass
            validity_hours: How long the bypass is valid

        Returns:
            Bypass creation result
        """
        bypass_token = {
            "bypass_id": f"bypass_{int(time.time())}_{command.replace(' ', '_')}",
            "command": command,
            "reason": reason,
            "authorized_by": authorized_by,
            "created_at": time.time(),
            "expires_at": time.time() + (validity_hours * 3600),
            "used": False,
            "validity_hours": validity_hours,
        }

        # Save bypass token
        try:
            with open(self.gate_bypass_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(bypass_token, ensure_ascii=False) + "\n")

            return {
                "success": True,
                "bypass_token": bypass_token["bypass_id"],
                "expires_at": bypass_token["expires_at"],
                "message": f"Emergency bypass created for command '{command}'. Valid for {validity_hours} hour(s).",
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to create bypass: {str(e)}"}

    def _identify_affected_tasks(
        self, command: str, args: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """
        Identify tasks that would be affected by executing this command.

        This is a heuristic approach - in practice, this would need to be
        more sophisticated to accurately identify task dependencies.
        """
        affected_tasks = []

        # Check if command mentions specific task IDs
        command_str = command + " " + " ".join(str(v) for v in args.values() if v)
        for potential_task_id in command_str.split():
            if potential_task_id.startswith(("T", "t")) and len(potential_task_id) > 1:
                # Look for task IDs like T1.1, t4.13, etc.
                if self._task_id_exists(potential_task_id[1:]):  # Remove T/t prefix
                    affected_tasks.append(potential_task_id[1:])

        # Check pending tasks for any that might be affected by this command type
        pending_data = utils.read_json(
            self.pending_tasks_path, default={"pending_tasks": []}
        )

        for task_reg in pending_data.get("pending_tasks", []):
            task_data = task_reg.get("task_data", {})
            task_name = task_data.get("name", "").lower()
            command_lower = command.lower()

            # Simple heuristic: if command mentions keywords from task name
            task_keywords = set(task_name.split()) - {
                "the",
                "a",
                "an",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
            }
            command_words = set(command_lower.split())

            if task_keywords & command_words:  # Any overlap
                affected_tasks.append(task_reg["task_id"])

        return list(set(affected_tasks))  # Remove duplicates

    def _task_id_exists(self, task_id: str) -> bool:
        """Check if a task ID exists in the system."""
        try:
            # Check WBS data
            wbs_data = self.wbs_sync_engine.get_wbs_data("default", use_cache=True)

            for phase_data in wbs_data.get("work_breakdown_structure", {}).values():
                if "subtasks" in phase_data:
                    if task_id in phase_data["subtasks"]:
                        return True

            # Check pending tasks
            pending_data = utils.read_json(
                self.pending_tasks_path, default={"pending_tasks": []}
            )

            for task_reg in pending_data.get("pending_tasks", []):
                if task_reg.get("task_id") == task_id:
                    return True

            return False
        except Exception:
            return False

    def _attempt_auto_wbs_updates(self, task_ids: List[str]) -> Dict[str, Any]:
        """Attempt to automatically update WBS for specified tasks."""
        updated_tasks = []
        failed_tasks = []

        for task_id in task_ids:
            try:
                # Find the task registration
                pending_data = utils.read_json(
                    self.pending_tasks_path, default={"pending_tasks": []}
                )

                task_reg = None
                for reg in pending_data.get("pending_tasks", []):
                    if reg.get("task_id") == task_id:
                        task_reg = reg
                        break

                if task_reg and not task_reg.get("wbs_updated", False):
                    # Attempt WBS update
                    update_result = update_wbs_for_task(
                        task_reg["task_data"], task_reg.get("context"), self.root
                    )

                    if update_result["success"]:
                        task_reg["wbs_updated"] = True
                        task_reg["execution_allowed"] = True
                        task_reg["updated_at"] = utils.now_iso()
                        updated_tasks.append(task_id)
                    else:
                        failed_tasks.append(
                            {"task_id": task_id, "error": update_result.get("error")}
                        )

            except Exception as e:
                failed_tasks.append({"task_id": task_id, "error": str(e)})

        # Save updated pending tasks
        if updated_tasks:
            utils.write_json(self.pending_tasks_path, pending_data)

        return {
            "all_updated": len(failed_tasks) == 0,
            "updated_tasks": updated_tasks,
            "failed_tasks": failed_tasks,
            "total_attempted": len(task_ids),
        }

    def _check_emergency_bypass(self, command: str) -> Dict[str, Any]:
        """Check if there's an active emergency bypass for this command."""
        try:
            if not self.gate_bypass_log_path.exists():
                return {"bypassed": False}

            active_bypasses = []
            current_time = time.time()

            with open(self.gate_bypass_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        bypass = json.loads(line.strip())
                        if (
                            bypass["command"] == command
                            and not bypass.get("used", False)
                            and bypass["expires_at"] > current_time
                        ):
                            active_bypasses.append(bypass)
                    except json.JSONDecodeError:
                        continue

            if active_bypasses:
                # Use the most recent bypass
                bypass = max(active_bypasses, key=lambda x: x["created_at"])
                bypass["used"] = True  # Mark as used

                # Update the bypass log
                self._update_bypass_usage(bypass)

                return {
                    "bypassed": True,
                    "reason": bypass["reason"],
                    "bypass_id": bypass["bypass_id"],
                }

        except Exception as e:
            print(f"Warning: Error checking emergency bypass: {e}")

        return {"bypassed": False}

    def _update_bypass_usage(self, bypass: Dict[str, Any]) -> None:
        """Update bypass usage in the log."""
        try:
            # Read all bypasses
            bypasses = []
            if self.gate_bypass_log_path.exists():
                with open(self.gate_bypass_log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            b = json.loads(line.strip())
                            if b["bypass_id"] == bypass["bypass_id"]:
                                b["used"] = True
                                b["used_at"] = time.time()
                            bypasses.append(b)
                        except json.JSONDecodeError:
                            continue

            # Rewrite the file
            with open(self.gate_bypass_log_path, "w", encoding="utf-8") as f:
                for b in bypasses:
                    f.write(json.dumps(b, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"Warning: Error updating bypass usage: {e}")

    def _log_gate_violation(
        self, command: str, args: Dict[str, Any], gate_check: Dict[str, Any]
    ) -> None:
        """Log a gate violation event."""
        log_entry = {
            "event_type": "gate_violation",
            "timestamp": time.time(),
            "command": command,
            "args": args,
            "violations": gate_check.get("violations", []),
            "message": gate_check.get("message", ""),
        }

        try:
            with open(self.execution_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Warning: Failed to log gate violation: {e}")

    def _log_gate_success(
        self, command: str, args: Dict[str, Any], gate_check: Dict[str, Any]
    ) -> None:
        """Log a successful gate check."""
        log_entry = {
            "event_type": "gate_success",
            "timestamp": time.time(),
            "command": command,
            "args": args,
            "affected_tasks": gate_check.get("affected_tasks", []),
            "auto_updated": gate_check.get("auto_updated", False),
        }

        try:
            with open(self.execution_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Warning: Failed to log gate success: {e}")

    def _increment_blocked_attempts(self, command: str, args: Dict[str, Any]) -> None:
        """Increment the counter of blocked attempts for this command."""
        # This could be enhanced to track attempts per command/args combination
        # For now, it's a placeholder for future enhancement
        pass

    def get_pending_tasks_summary(self) -> Dict[str, Any]:
        """Get a summary of all pending tasks."""
        pending_data = utils.read_json(
            self.pending_tasks_path, default={"pending_tasks": []}
        )
        pending_tasks = pending_data.get("pending_tasks", [])

        summary = {
            "total_pending": len(pending_tasks),
            "wbs_updated": sum(1 for t in pending_tasks if t.get("wbs_updated", False)),
            "execution_allowed": sum(
                1 for t in pending_tasks if t.get("execution_allowed", False)
            ),
            "failed_updates": sum(1 for t in pending_tasks if t.get("last_error")),
            "last_updated": pending_data.get("last_updated", "never"),
        }

        # Group by source
        sources = {}
        for task in pending_tasks:
            source = task.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1

        summary["by_source"] = sources

        return summary

    def cleanup_completed_tasks(self, max_age_days: int = 30) -> int:
        """Remove old completed tasks from the pending list."""
        import time
        from datetime import datetime, timedelta

        pending_data = utils.read_json(
            self.pending_tasks_path, default={"pending_tasks": []}
        )
        pending_tasks = pending_data.get("pending_tasks", [])

        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)

        # Keep tasks that are:
        # 1. Not completed (still need attention), OR
        # 2. Recently completed (for audit purposes)
        filtered_tasks = []
        removed_count = 0

        for task in pending_tasks:
            if not task.get("execution_allowed", False):
                # Keep pending tasks
                filtered_tasks.append(task)
            else:
                # Check if recently completed
                updated_at = task.get("updated_at", task.get("registered_at", ""))
                if updated_at:
                    try:
                        # Parse ISO timestamp and check age
                        task_time = datetime.fromisoformat(
                            updated_at.replace("Z", "+00:00")
                        ).timestamp()
                        if task_time > cutoff_time:
                            filtered_tasks.append(task)
                        else:
                            removed_count += 1
                    except (ValueError, AttributeError):
                        # Keep if we can't parse the date
                        filtered_tasks.append(task)
                else:
                    # Keep if no timestamp
                    filtered_tasks.append(task)

        pending_data["pending_tasks"] = filtered_tasks
        pending_data["last_updated"] = utils.now_iso()
        utils.write_json(self.pending_tasks_path, pending_data)

        return removed_count

    def _log_task_registration(
        self, task_data: Dict[str, Any], action: str, integration_result: Dict[str, Any]
    ) -> None:
        """Log task registration events."""
        log_entry = {
            "timestamp": utils.now_iso(),
            "action": action,
            "task_name": task_data.get("name", "unknown"),
            "task_description": task_data.get("description", "unknown")[:100],
            "confidence_score": integration_result.get("confidence_score", 0),
            "recommended_phase": integration_result.get(
                "placement_recommendation", {}
            ).get("recommended_phase"),
            "placement_type": integration_result.get(
                "placement_recommendation", {}
            ).get("placement_type"),
        }

        try:
            with open(self.execution_log_path, "a", encoding="utf-8") as f:
                json.dump(log_entry, f, ensure_ascii=False, separators=(",", ":"))
                f.write("\n")
        except Exception:
            pass  # Best effort logging

    def force_wbs_update(self, task_id: str) -> Dict[str, Any]:
        """Force a WBS update for a specific pending task."""
        pending_data = utils.read_json(
            self.pending_tasks_path, default={"pending_tasks": []}
        )

        for task_reg in pending_data.get("pending_tasks", []):
            if task_reg.get("task_id") == task_id:
                if task_reg.get("wbs_updated", False):
                    return {
                        "success": False,
                        "message": f"Task {task_id} already has WBS updated",
                    }

                # Force update
                update_result = update_wbs_for_task(
                    task_reg["task_data"], task_reg.get("context"), self.root
                )

                if update_result["success"]:
                    task_reg["wbs_updated"] = True
                    task_reg["wbs_update_result"] = update_result
                    task_reg["execution_allowed"] = True
                    task_reg["updated_at"] = utils.now_iso()

                    utils.write_json(self.pending_tasks_path, pending_data)

                    return {
                        "success": True,
                        "task_id": task_id,
                        "message": "WBS update forced successfully",
                        "update_result": update_result,
                    }
                else:
                    task_reg["wbs_update_result"] = update_result
                    task_reg["last_error"] = update_result.get("error", "Unknown error")

                    utils.write_json(self.pending_tasks_path, pending_data)

                    return {
                        "success": False,
                        "task_id": task_id,
                        "message": "WBS update failed",
                        "error": update_result.get("error", "Unknown error"),
                    }

        return {
            "success": False,
            "message": f"Task {task_id} not found in pending tasks",
        }


def check_task_execution_allowed(
    task_id: str, root: Optional[Path] = None
) -> Dict[str, Any]:
    """Convenience function to check if task execution is allowed."""
    if root is None:
        root = Path.cwd()

    gate = TaskExecutionGate(root)
    return gate.check_execution_allowed(task_id)


def register_task_for_execution(
    task_data: Dict[str, Any],
    source: str = "unknown",
    context: Optional[Dict[str, Any]] = None,
    root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Convenience function to register a task for execution."""
    if root is None:
        root = Path.cwd()

    gate = TaskExecutionGate(root)
    return gate.register_new_task(task_data, source, context)
