"""
Tool Usage Tracker: Tracks and reports system tools used during task execution.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import telemetry, utils


class ToolUsageTracker:
    """Tracks which system tools and commands are used during task execution."""

    def __init__(self, root: Path):
        self.root = root
        self.tools_log_path = root / ".ai_onboard" / "tool_usage.jsonl"
        self.session_tools_path = root / ".ai_onboard" / "session_tools.json"
        self.current_session: Optional[str] = None
        self.session_tools: List[Dict[str, Any]] = []
        utils.ensure_dir(self.tools_log_path.parent)

    def start_task_session(self, task_name: str, task_type: str = "command") -> str:
        """Start tracking a task session.

        Args:
            task_name: Name of the task being executed
            task_type: Type of task (command, analysis, etc.)

        Returns:
            Session ID for the task
        """
        session_id = f"{task_name}_{int(time.time())}"
        self.current_session = session_id
        self.session_tools = []

        # Log session start
        telemetry.log_event(
            "task_session_started",
            session_id=session_id,
            task_name=task_name,
            task_type=task_type,
        )

        # Save session info
        session_data = {
            "session_id": session_id,
            "task_name": task_name,
            "task_type": task_type,
            "start_time": utils.now_iso(),
            "tools_used": [],
        }
        utils.write_json(self.session_tools_path, session_data)

        return session_id

    def track_tool_usage(
        self,
        tool_name: str,
        tool_type: str = "system",
        parameters: Optional[Dict[str, Any]] = None,
        result: Optional[str] = None,
        duration: Optional[float] = None,
    ) -> None:
        """Track usage of a specific tool.

        Args:
            tool_name: Name of the tool/command used
            tool_type: Type of tool (system, cli, api, etc.)
            parameters: Parameters passed to the tool
            result: Result/status of tool usage
            duration: Time taken to execute (seconds)
        """
        if not self.current_session:
            return

        tool_usage = {
            "session_id": self.current_session,
            "timestamp": utils.now_iso(),
            "tool_name": tool_name,
            "tool_type": tool_type,
            "parameters": parameters or {},
            "result": result,
            "duration": duration,
        }

        # Add to current session
        self.session_tools.append(tool_usage)

        # Log to telemetry
        telemetry.log_event(
            "tool_used",
            session_id=self.current_session,
            tool_name=tool_name,
            tool_type=tool_type,
            parameters=parameters,
            result=result,
            duration=duration,
        )

        # Save to persistent log
        try:
            with open(self.tools_log_path, "a", encoding="utf-8") as f:
                json.dump(tool_usage, f, ensure_ascii=False, separators=(",", ":"))
                f.write("\n")
        except Exception:
            # Best effort - don't fail if logging fails
            pass

    def end_task_session(
        self, final_status: str = "completed", summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """End the current task session and return a summary.

        Args:
            final_status: Final status of the task
            summary: Optional summary of the task execution

        Returns:
            Summary of tools used during the session
        """
        if not self.current_session:
            return {}

        session_summary = {
            "session_id": self.current_session,
            "end_time": utils.now_iso(),
            "final_status": final_status,
            "summary": summary,
            "total_tools_used": len(self.session_tools),
            "tools_summary": self._generate_tools_summary(),
            "tools_used": self.session_tools,
        }

        # Update session file
        try:
            session_data = utils.read_json(self.session_tools_path, default={})
            session_data.update(
                {
                    "end_time": session_summary["end_time"],
                    "final_status": final_status,
                    "summary": summary,
                    "total_tools_used": session_summary["total_tools_used"],
                    "tools_summary": session_summary["tools_summary"],
                }
            )
            utils.write_json(self.session_tools_path, session_data)
        except Exception:
            pass

        # Log session end
        telemetry.log_event(
            "task_session_ended",
            session_id=self.current_session,
            final_status=final_status,
            total_tools_used=session_summary["total_tools_used"],
        )

        # Reset session
        self.current_session = None
        temp_tools = self.session_tools.copy()
        self.session_tools = []

        return session_summary

    def _generate_tools_summary(self) -> Dict[str, Any]:
        """Generate a summary of tools used in the current session."""
        if not self.session_tools:
            return {}

        tool_counts = {}
        tool_types = {}
        total_duration = 0.0
        tools_with_duration = 0

        for tool in self.session_tools:
            tool_name = tool["tool_name"]
            tool_type = tool["tool_type"]

            # Count tool usage
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
            tool_types[tool_type] = tool_types.get(tool_type, 0) + 1

            # Track duration
            if tool.get("duration"):
                total_duration += tool["duration"]
                tools_with_duration += 1

        return {
            "tool_usage_counts": tool_counts,
            "tool_type_counts": tool_types,
            "total_duration": round(total_duration, 2),
            "tools_with_duration": tools_with_duration,
            "unique_tools": len(tool_counts),
            "unique_tool_types": len(tool_types),
        }

    def display_tools_summary(self, session_summary: Dict[str, Any]) -> None:
        """Display a formatted summary of tools used during task execution."""
        if not session_summary or session_summary.get("total_tools_used", 0) == 0:
            print("ℹ️  No system tools were used during this task.")
            return

        print("\n" + "=" * 60)
        print("🔧 SYSTEM TOOLS USED DURING TASK EXECUTION")
        print("=" * 60)

        tools_summary = session_summary.get("tools_summary", {})

        # Overall stats
        print("📊 OVERVIEW:")
        print(f"   • Total tools used: {session_summary['total_tools_used']}")
        print(f"   • Unique tools: {tools_summary.get('unique_tools', 0)}")
        print(f"   • Tool categories: {tools_summary.get('unique_tool_types', 0)}")
        if tools_summary.get("total_duration", 0) > 0:
            print(".2f")

        # Tool usage breakdown
        if tools_summary.get("tool_usage_counts"):
            print("\n🛠️  TOOLS USED:")
            for tool_name, count in sorted(tools_summary["tool_usage_counts"].items()):
                print(f"   • {tool_name}: {count} time{'s' if count != 1 else ''}")

        # Tool types breakdown
        if tools_summary.get("tool_type_counts"):
            print("\n📂 TOOL CATEGORIES:")
            for tool_type, count in sorted(tools_summary["tool_type_counts"].items()):
                print(
                    f"   • {tool_type.title()}: {count} tool{'s' if count != 1 else ''}"
                )

        # Detailed tool list (if not too many)
        tools_used = session_summary.get("tools_used", [])
        if len(tools_used) <= 10:  # Only show details for reasonable number of tools
            print("\n📋 DETAILED TOOL EXECUTION:")
            for i, tool in enumerate(tools_used, 1):
                tool_name = tool["tool_name"]
                tool_type = tool["tool_type"]
                result = tool.get("result", "completed")
                duration = tool.get("duration")
                duration_str = ".2f" if duration else ""

                print(f"   {i}. {tool_name} ({tool_type}){duration_str} - {result}")

        print("=" * 60 + "\n")

    def get_recent_tool_usage(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent tool usage from the log."""
        if not self.tools_log_path.exists():
            return []

        tools = []
        try:
            with open(self.tools_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            tools.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception:
            return []

        # Return most recent tools
        return tools[-limit:]


# Global instance for easy access
_tool_tracker = None


def get_tool_tracker(root: Path) -> ToolUsageTracker:
    """Get the global tool usage tracker instance."""
    global _tool_tracker
    if _tool_tracker is None or _tool_tracker.root != root:
        _tool_tracker = ToolUsageTracker(root)
    return _tool_tracker


def track_tool_usage(
    tool_name: str,
    tool_type: str = "system",
    parameters: Optional[Dict[str, Any]] = None,
    result: Optional[str] = None,
    duration: Optional[float] = None,
    root: Optional[Path] = None,
) -> None:
    """Convenience function to track tool usage."""
    if root is None:
        root = Path.cwd()

    tracker = get_tool_tracker(root)
    tracker.track_tool_usage(tool_name, tool_type, parameters, result, duration)
