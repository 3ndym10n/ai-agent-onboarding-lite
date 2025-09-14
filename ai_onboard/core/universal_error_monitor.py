"""
Universal Error Monitor: Intercepts and processes errors from any agent (foreground or background).
"""

import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict

from . import smart_debugger, telemetry, utils


class UniversalErrorMonitor:
    """Monitors and processes errors from any agent interaction."""

    def __init__(self, root: Path):
        self.root = root
        self.debugger = smart_debugger.SmartDebugger(root)
        self.error_log_path = root / ".ai_onboard" / "agent_errors.jsonl"
        self.capability_usage_path = root / ".ai_onboard" / "capability_usage.json"
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure required directories exist."""
        utils.ensure_dir(self.error_log_path.parent)
        utils.ensure_dir(self.capability_usage_path.parent)

    def intercept_error(
        self, error: Exception, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Intercept and process any error from agent interactions."""
        if context is None:
            context = {}

        # Extract error information
        error_data = {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
            "context": context,
            "timestamp": utils.now_iso(),
            "agent_type": context.get("agent_type", "unknown"),
            "command": context.get("command", "unknown"),
            "session_id": context.get("session_id", "unknown"),
        }

        # Log the error
        self._log_error(error_data)

        # Analyze with smart debugger (with error handling)
        debug_result = {}
        try:
            debug_result = self.debugger.analyze_error(error_data)
        except Exception as debug_error:
            # If debugger fails, log the debugging error but don't fail the error interception
            debug_error_data = {
                "type": type(debug_error).__name__,
                "message": str(debug_error),
                "traceback": traceback.format_exc(),
                "context": {"original_error": str(error)},
                "timestamp": utils.now_iso(),
                "agent_type": "error_monitor",
                "command": "debug_analysis",
                "session_id": context.get("session_id", "unknown"),
            }
            self._log_error(debug_error_data)
            debug_result = {"confidence": 0, "error": "debugger_failed"}

        # Record capability usage (error handling was used)
        self._record_capability_usage(
            "error_interception",
            {
                "error_type": error_data["type"],
                "debug_confidence": debug_result.get("confidence", 0),
                "success": True,
            },
        )

        # Log telemetry event (with error handling)
        try:
            telemetry.log_event(
                "agent_error_intercepted",
                error_type=error_data["type"],
                agent_type=error_data["agent_type"],
                confidence=debug_result.get("confidence", 0),
            )
        except Exception as telemetry_error:
            # Log telemetry failure but don't fail the error interception
            telemetry_error_data = {
                "type": type(telemetry_error).__name__,
                "message": str(telemetry_error),
                "traceback": traceback.format_exc(),
                "context": {"original_error": str(error)},
                "timestamp": utils.now_iso(),
                "agent_type": "error_monitor",
                "command": "telemetry_logging",
                "session_id": context.get("session_id", "unknown"),
            }
            self._log_error(telemetry_error_data)

        return {"error_data": error_data, "debug_result": debug_result, "handled": True}

    def monitor_command_execution(
        self, command: str, agent_type: str = "foreground", session_id: str = None
    ) -> Callable:
        """Create a context manager to monitor command execution."""

        class CommandMonitor:
            def __init__(self, monitor, command, agent_type, session_id):
                self.monitor = monitor
                self.command = command
                self.agent_type = agent_type
                self.session_id = session_id
                self.start_time = datetime.now()

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    # Error occurred, intercept it (with error handling)
                    try:
                        context = {
                            "command": self.command,
                            "agent_type": self.agent_type,
                            "session_id": self.session_id,
                            "execution_time": (
                                datetime.now() - self.start_time
                            ).total_seconds(),
                        }
                        self.monitor.intercept_error(exc_val, context)
                    except Exception as monitor_error:
                        # If error monitoring fails, log it but don't fail the command
                        print(f"Warning: Error monitoring failed: {monitor_error}")
                else:
                    # Success - record capability usage (with error handling)
                    try:
                        self.monitor._record_capability_usage(
                            "command_execution",
                            {
                                "command": self.command,
                                "agent_type": self.agent_type,
                                "success": True,
                                "execution_time": (
                                    datetime.now() - self.start_time
                                ).total_seconds(),
                            },
                        )
                    except Exception as usage_error:
                        # If capability usage recording fails, log it but don't fail the command
                        print(
                            f"Warning: Capability usage recording failed: {usage_error}"
                        )

                # Don't suppress the exception
                return False

        return CommandMonitor(self, command, agent_type, session_id)

    def track_capability_usage(self, capability: str, context: Dict[str, Any] = None):
        """Track when system capabilities are used."""
        if context is None:
            context = {}

        self._record_capability_usage(capability, context)

    def get_usage_report(self) -> Dict[str, Any]:
        """Get a report of system capability usage."""
        usage_data = utils.read_json(self.capability_usage_path, default={})

        # Calculate usage statistics
        total_uses = sum(usage_data.get("capabilities", {}).values())
        most_used = (
            max(usage_data.get("capabilities", {}).items(), key=lambda x: x[1])
            if usage_data.get("capabilities")
            else ("none", 0)
        )
        least_used = (
            min(usage_data.get("capabilities", {}).items(), key=lambda x: x[1])
            if usage_data.get("capabilities")
            else ("none", 0)
        )

        return {
            "total_capability_uses": total_uses,
            "most_used_capability": most_used[0],
            "least_used_capability": least_used[0],
            "capability_breakdown": usage_data.get("capabilities", {}),
            "recent_errors": self._get_recent_errors(),
            "error_rate": self._calculate_error_rate(),
        }

    def _log_error(self, error_data: Dict[str, Any]):
        """Log error to persistent storage."""
        with open(self.error_log_path, "a", encoding="utf-8") as f:
            json.dump(error_data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    def _record_capability_usage(self, capability: str, context: Dict[str, Any]):
        """Record capability usage for tracking."""
        usage_data = utils.read_json(
            self.capability_usage_path,
            default={"capabilities": {}, "usage_history": []},
        )

        # Update capability count
        if "capabilities" not in usage_data:
            usage_data["capabilities"] = {}
        usage_data["capabilities"][capability] = (
            usage_data["capabilities"].get(capability, 0) + 1
        )

        # Add to usage history
        usage_entry = {
            "capability": capability,
            "timestamp": utils.now_iso(),
            "context": context,
        }
        usage_data["usage_history"].append(usage_entry)

        # Keep only last 1000 entries
        if len(usage_data["usage_history"]) > 1000:
            usage_data["usage_history"] = usage_data["usage_history"][-1000:]

        utils.write_json(self.capability_usage_path, usage_data)

    def _get_recent_errors(self, limit: int = 10) -> list:
        """Get recent errors from the log."""
        if not self.error_log_path.exists():
            return []

        errors = []
        with open(self.error_log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                try:
                    error = json.loads(line.strip())
                    errors.append(
                        {
                            "type": error.get("type"),
                            "message": error.get("message"),
                            "timestamp": error.get("timestamp"),
                            "agent_type": error.get("agent_type"),
                        }
                    )
                except json.JSONDecodeError:
                    continue

        return errors

    def _calculate_error_rate(self) -> float:
        """Calculate error rate over recent usage."""
        usage_data = utils.read_json(self.capability_usage_path, default={})
        recent_usage = usage_data.get("usage_history", [])[-100:]  # Last 100 uses

        if not recent_usage:
            return 0.0

        error_count = sum(
            1 for use in recent_usage if not use.get("context", {}).get("success", True)
        )
        return error_count / len(recent_usage)


def get_error_monitor(root: Path) -> UniversalErrorMonitor:
    """Get universal error monitor instance."""
    return UniversalErrorMonitor(root)


# Global error handler for uncaught exceptions
def setup_global_error_handler(root: Path):
    """Set up global error handler for uncaught exceptions."""
    monitor = get_error_monitor(root)

    def global_exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't intercept keyboard interrupts
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Intercept the error (with error handling)
        try:
            context = {
                "agent_type": "global",
                "command": "uncaught_exception",
                "session_id": "global",
            }
            monitor.intercept_error(exc_value, context)
        except Exception as monitor_error:
            # If error monitoring fails, print to stderr but continue
            print(f"Error monitor failed: {monitor_error}", file=sys.stderr)

        # Call the original exception handler
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = global_exception_handler
