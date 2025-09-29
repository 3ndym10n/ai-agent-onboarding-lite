"""
Universal Error Monitor: Intercepts and \
    processes errors from any agent (foreground or background).
"""

import json
import os
import platform
import sys
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import psutil

from ..base import telemetry, utils
from ..legacy_cleanup.smart_debugger import SmartDebugger

# Import moved to function level to avoid circular import
from .tool_usage_tracker import track_tool_usage


class UniversalErrorMonitor:
    """Monitors and processes errors from any agent interaction."""

    def __init__(self, root: Path):
        self.root = root
        self.debugger = SmartDebugger(root)
        from .pattern_recognition_system import PatternRecognitionSystem

        self.pattern_recognition = PatternRecognitionSystem(root)
        track_tool_usage(
            "pattern_recognition_system",
            "ai_system",
            {"action": "initialize_monitor"},
            "success",
        )
        self.error_log_path = root / ".ai_onboard" / "agent_errors.jsonl"
        self.capability_usage_path = root / ".ai_onboard" / "capability_usage.json"
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure required directories exist."""
        utils.ensure_dir(self.error_log_path.parent)
        utils.ensure_dir(self.capability_usage_path.parent)

    def intercept_error(
        self, error: Exception, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Intercept and process any error from agent interactions."""
        if context is None:
            context = {}

        # Extract basic error information
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

        # Enrich with comprehensive context
        error_data["enriched_context"] = self._enrich_error_context(error, context)

        # Log the error
        self._log_error(error_data)

        # Analyze with pattern recognition system
        pattern_match = self.pattern_recognition.analyze_error(error_data)
        track_tool_usage(
            "pattern_recognition_system",
            "ai_system",
            {"action": "analyze_error", "error_type": error_data["type"]},
            "success",
        )

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

        # Update pattern with this occurrence
        if pattern_match.pattern_id != "unknown_error":
            self.pattern_recognition.update_pattern(
                pattern_match.pattern_id, error_data
            )
            track_tool_usage(
                "pattern_recognition_system",
                "ai_system",
                {"action": "update_pattern", "pattern_id": pattern_match.pattern_id},
                "success",
            )

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

        return {
            "error_data": error_data,
            "debug_result": debug_result,
            "pattern_match": {
                "pattern_id": pattern_match.pattern_id,
                "confidence": pattern_match.confidence,
                "prevention_suggestions": pattern_match.prevention_suggestions,
            },
            "handled": True,
        }

    def monitor_command_execution(
        self,
        command: str,
        agent_type: str = "foreground",
        session_id: Optional[str] = None,
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

        return CommandMonitor(self, command, agent_type, session_id)  # type: ignore[return-value]

    def track_capability_usage(
        self, capability: str, context: Optional[Dict[str, Any]] = None
    ):
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
            "error_patterns": self.analyze_error_patterns(days_back=7),
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

    def analyze_error_patterns(self, days_back: int = 7) -> Dict[str, Any]:
        """Analyze error patterns from logged errors."""
        if not self.error_log_path.exists():
            return {"patterns": {}, "insights": [], "recommendations": []}

        errors = []
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_back)

        # Read all errors from log
        with open(self.error_log_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    error = json.loads(line.strip())
                    timestamp_str = error.get("timestamp", "")
                    # Handle timezone suffix 'Z' which fromisoformat doesn't support
                    if timestamp_str.endswith("Z"):
                        timestamp_str = timestamp_str[:-1]  # Just remove the 'Z'
                    elif not timestamp_str:
                        continue  # Skip if no timestamp
                    error_time = datetime.fromisoformat(timestamp_str)
                    if error_time >= cutoff_time:
                        errors.append(error)
                except (json.JSONDecodeError, ValueError):
                    continue

        if not errors:
            return {"patterns": {}, "insights": [], "recommendations": []}

        # Analyze patterns
        patterns = self._extract_error_patterns(errors)
        insights = self._generate_error_insights(patterns, errors)
        recommendations = self._generate_error_recommendations(patterns, insights)

        return {
            "patterns": patterns,
            "insights": insights,
            "recommendations": recommendations,
            "analysis_period_days": days_back,
            "total_errors_analyzed": len(errors),
        }

    def _extract_error_patterns(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract error patterns from error logs."""
        patterns: Dict[str, Any] = {
            "error_types": {},
            "commands": {},
            "agents": {},
            "time_distribution": {},
            "frequent_messages": {},
            "error_sequences": [],
        }

        # Count error types
        for error in errors:
            error_type = error.get("type", "Unknown")
            patterns["error_types"][error_type] = (
                patterns["error_types"].get(error_type, 0) + 1
            )

            command = error.get("command", "unknown")
            patterns["commands"][command] = patterns["commands"].get(command, 0) + 1

            agent = error.get("agent_type", "unknown")
            patterns["agents"][agent] = patterns["agents"].get(agent, 0) + 1

            # Extract common error messages (first 100 chars)
            message = error.get("message", "")[:100]
            if message:
                patterns["frequent_messages"][message] = (
                    patterns["frequent_messages"].get(message, 0) + 1
                )

        # Analyze time distribution (hourly)
        for error in errors:
            try:
                timestamp_str = error.get("timestamp", "")
                # Handle timezone suffix 'Z' which fromisoformat doesn't support
                if timestamp_str.endswith("Z"):
                    timestamp_str = timestamp_str[:-1]  # Just remove the 'Z'
                error_time = datetime.fromisoformat(timestamp_str)
                hour = error_time.hour
                patterns["time_distribution"][hour] = (
                    patterns["time_distribution"].get(hour, 0) + 1
                )
            except ValueError:
                continue

        # Sort patterns by frequency
        for key in patterns:
            if isinstance(patterns[key], dict):
                patterns[key] = dict(
                    sorted(patterns[key].items(), key=lambda x: x[1], reverse=True)
                )

        return patterns

    def _generate_error_insights(
        self, patterns: Dict[str, Any], errors: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate insights from error patterns."""
        insights = []

        # Most common error types
        if patterns["error_types"]:
            most_common_error = list(patterns["error_types"].keys())[0]
            error_count = patterns["error_types"][most_common_error]
            insights.append(
                f"Most common error type: {most_common_error} ({error_count} occurrences)"
            )

        # Command failure patterns
        if patterns["commands"]:
            failing_commands = [
                (cmd, count)
                for cmd, count in patterns["commands"].items()
                if cmd != "unknown"
            ]
            if failing_commands:
                worst_command = max(failing_commands, key=lambda x: x[1])
                insights.append(
                    f"Most failing command: {worst_command[0]} ({worst_command[1]} failures)"
                )

        # Agent failure patterns
        if patterns["agents"]:
            failing_agents = [
                (agent, count)
                for agent, count in patterns["agents"].items()
                if agent != "unknown"
            ]
            if failing_agents:
                worst_agent = max(failing_agents, key=lambda x: x[1])
                insights.append(
                    f"Most error-prone agent: {worst_agent[0]} ({worst_agent[1]} errors)"
                )

        # Time-based patterns
        if patterns["time_distribution"]:
            peak_hour = max(patterns["time_distribution"].items(), key=lambda x: x[1])
            insights.append(
                f"Peak error hour: {peak_hour[0]:02d}:00 ({peak_hour[1]} errors)"
            )

        # Error frequency trends
        total_errors = len(errors)
        if total_errors > 10:
            insights.append(f"Total errors in period: {total_errors}")

        return insights

    def _generate_error_recommendations(
        self, patterns: Dict[str, Any], insights: List[str]
    ) -> List[str]:
        """Generate recommendations based on error patterns and insights."""
        recommendations = []

        # Recommendations based on error types
        if "AttributeError" in patterns["error_types"]:
            recommendations.append("Consider adding null checks for attribute access")

        if "ValueError" in patterns["error_types"]:
            recommendations.append("Review input validation and type checking")

        if "ImportError" in patterns["error_types"]:
            recommendations.append("Check dependency management and module imports")

        # Recommendations based on command failures
        if patterns["commands"]:
            failing_commands = [
                cmd for cmd, count in patterns["commands"].items() if count >= 2
            ]
            for cmd in failing_commands:
                recommendations.append(
                    f"Investigate frequent failures in '{cmd}' command"
                )

        # Recommendations based on agent failures
        if patterns["agents"]:
            failing_agents = [
                agent for agent, count in patterns["agents"].items() if count > 5
            ]
            for agent in failing_agents:
                recommendations.append(f"Review error handling in {agent} agent")

        # Time-based recommendations
        if patterns["time_distribution"]:
            peak_errors = sum(
                count
                for hour, count in patterns["time_distribution"].items()
                if count > 5
            )
            if peak_errors > 10:
                recommendations.append(
                    "Consider implementing rate limiting or circuit breaker patterns"
                )

        # Generic recommendations
        total_errors = sum(patterns["error_types"].values())
        if total_errors > 20:
            recommendations.append(
                "Consider implementing comprehensive error recovery mechanisms"
            )
        elif total_errors > 50:
            recommendations.append(
                "URGENT: High error rate detected - immediate investigation required"
            )

        return recommendations

    def _enrich_error_context(
        self, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enrich error context with comprehensive debugging information."""
        enriched: Dict[str, Any] = {}

        try:
            # System information
            enriched["system_info"] = self._get_system_info()

            # Performance metrics
            enriched["performance_metrics"] = self._get_performance_metrics()

            # Environment details
            enriched["environment"] = self._get_environment_info()

            # Stack frame analysis
            enriched["stack_analysis"] = self._analyze_stack_frames(error)

            # Recent activity context
            enriched["recent_activity"] = self._get_recent_activity_context(context)

            # Configuration state
            enriched["configuration_snapshot"] = self._get_configuration_snapshot()

            # Related errors pattern
            enriched["related_patterns"] = self._find_related_error_patterns(
                error, context
            )

            # Resource usage at error time
            enriched["resource_usage"] = self._get_resource_usage_snapshot()

        except Exception as enrichment_error:
            # If enrichment fails, provide basic fallback
            enriched["enrichment_error"] = str(enrichment_error)
            enriched["enrichment_failed"] = True

        return enriched

    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        try:
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture(),
                "processor": platform.processor(),
                "machine": platform.machine(),
                "system": platform.system(),
                "node": platform.node(),
                "cpu_count": os.cpu_count(),
                "pid": os.getpid(),
                "ppid": os.getppid() if hasattr(os, "getppid") else None,
            }
        except Exception as e:
            return {"system_info_error": str(e)}

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics at the time of error."""
        try:
            import time

            return {
                "timestamp": time.time(),
                "process_uptime": time.process_time(),
                "system_uptime": time.time() - psutil.boot_time(),
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": (
                    psutil.disk_usage("/").percent if os.path.exists("/") else None
                ),
            }
        except Exception as e:
            return {"performance_metrics_error": str(e)}

    def _get_environment_info(self) -> Dict[str, Any]:
        """Get environment and configuration information."""
        try:
            return {
                "working_directory": os.getcwd(),
                "user": os.getenv("USER") or os.getenv("USERNAME"),
                "path": (
                    os.getenv("PATH", "")[:200] + "..."
                    if len(os.getenv("PATH", "")) > 200
                    else os.getenv("PATH")
                ),
                "pythonpath": os.getenv("PYTHONPATH"),
                "environment_variables_count": len(dict(os.environ)),
                "umask": oct(os.umask(os.umask(0))) if hasattr(os, "umask") else None,
            }
        except Exception as e:
            return {"environment_info_error": str(e)}

    def _analyze_stack_frames(self, error: Exception) -> Dict[str, Any]:
        """Analyze stack frames for additional context."""
        try:
            import inspect

            # Get the current stack
            stack = inspect.stack()

            # Analyze the stack frames
            stack_info = []
            for frame_info in stack[-5:]:  # Last 5 frames
                frame_data = {
                    "filename": frame_info.filename,
                    "line_number": frame_info.lineno,
                    "function": frame_info.function,
                    "code_context": (
                        frame_info.code_context[0].strip()
                        if frame_info.code_context
                        else None
                    ),
                }
                stack_info.append(frame_data)

            # Extract local variables from error frame if available
            tb = sys.exc_info()[2]
            if tb:
                local_vars = {}
                while tb:
                    frame = tb.tb_frame
                    local_vars.update(
                        {
                            k: str(v)[:100] + "..." if len(str(v)) > 100 else str(v)
                            for k, v in frame.f_locals.items()
                            if not k.startswith("_")  # Skip private variables
                        }
                    )
                    tb = tb.tb_next

                # Limit to most relevant variables
                local_vars = dict(list(local_vars.items())[:10])

                return {
                    "stack_frames": stack_info,
                    "local_variables": local_vars,
                    "stack_depth": len(stack),
                }

            return {"stack_frames": stack_info}

        except Exception as e:
            return {"stack_analysis_error": str(e)}

    def _get_recent_activity_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent activity context around the error."""
        try:
            # Get recent capability usage
            usage_data = utils.read_json(self.capability_usage_path, default={})
            recent_usage = usage_data.get("usage_history", [])[-5:]  # Last 5 activities

            # Get recent errors
            recent_errors = self._get_recent_errors(3)  # Last 3 errors

            return {
                "recent_capability_usage": [
                    {
                        "capability": item.get("capability"),
                        "timestamp": item.get("timestamp"),
                        "success": item.get("context", {}).get("success"),
                    }
                    for item in recent_usage
                ],
                "recent_errors": recent_errors,
                "session_context": {
                    "session_id": context.get("session_id"),
                    "agent_type": context.get("agent_type"),
                    "command": context.get("command"),
                },
            }
        except Exception as e:
            return {"recent_activity_error": str(e)}

    def _get_configuration_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of current configuration state."""
        try:
            # This would capture relevant configuration files or settings
            config_info: Dict[str, Any] = {
                "config_files_exist": {},
                "important_paths": {},
            }

            # Check for important configuration files
            config_paths = [
                ".ai_onboard",
                "pyproject.toml",
                "requirements.txt",
                ".env",
                "config",
            ]

            for path_str in config_paths:
                path = self.root / path_str
                if path.exists():
                    if path.is_file():
                        config_info["config_files_exist"][path_str] = "file"
                    else:
                        config_info["config_files_exist"][path_str] = "directory"

            # Get important environment paths
            config_info["important_paths"] = {
                "root_directory": str(self.root),
                "error_log_path": str(self.error_log_path),
                "capability_usage_path": str(self.capability_usage_path),
            }

            return config_info

        except Exception as e:
            return {"configuration_snapshot_error": str(e)}

    def _find_related_error_patterns(
        self, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Find patterns related to this specific error."""
        try:
            # Get recent patterns for comparison
            patterns = self.analyze_error_patterns(days_back=1)

            error_type = type(error).__name__
            command = context.get("command", "unknown")

            # Find similar errors
            similar_errors = []
            if "patterns" in patterns and "error_types" in patterns["patterns"]:
                error_type_count = patterns["patterns"]["error_types"].get(
                    error_type, 0
                )
                if error_type_count > 1:
                    similar_errors.append(
                        f"Found {error_type_count} similar {error_type} errors recently"
                    )

            # Find command-specific patterns
            if "patterns" in patterns and "commands" in patterns["patterns"]:
                command_count = patterns["patterns"]["commands"].get(command, 0)
                if command_count > 1:
                    similar_errors.append(
                        f"Command '{command}' has failed {command_count} times recently"
                    )

            return {
                "similar_errors": similar_errors,
                "error_type_frequency": patterns.get("patterns", {})
                .get("error_types", {})
                .get(error_type, 0),
                "command_failure_rate": patterns.get("patterns", {})
                .get("commands", {})
                .get(command, 0),
                "is_recurring_error": len(similar_errors) > 0,
            }

        except Exception as e:
            return {"related_patterns_error": str(e)}

    def _get_resource_usage_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of resource usage at error time."""
        try:
            process = psutil.Process()

            return {
                "process_memory_mb": process.memory_info().rss / (1024 * 1024),
                "process_cpu_percent": process.cpu_percent(),
                "process_threads": process.num_threads(),
                "process_open_files": (
                    len(process.open_files())
                    if hasattr(process, "open_files")
                    else None
                ),
                "process_connections": (
                    len(process.net_connections(kind="all"))
                    if hasattr(process, "net_connections")
                    else (
                        len(process.connections())
                        if hasattr(process, "connections")
                        else None
                    )
                ),
                "system_memory": {
                    "total_gb": psutil.virtual_memory().total / (1024**3),
                    "available_gb": psutil.virtual_memory().available / (1024**3),
                    "percent_used": psutil.virtual_memory().percent,
                },
                "system_cpu": {
                    "percent": psutil.cpu_percent(interval=0.1),
                    "cores": psutil.cpu_count(),
                },
            }
        except Exception as e:
            return {"resource_usage_error": str(e)}


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
