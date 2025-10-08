"""
Agent Activity Monitor - Real-time tracking of AI agent activities and progress.

This module provides the core functionality for monitoring what AI agents are doing,
tracking their progress, and detecting their current state for the oversight dashboard.
"""

import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil  # type: ignore[import-untyped]

from ..base import utils
from .ai_gate_mediator import get_ai_gate_mediator


@dataclass
class AgentSession:
    """Active agent session information."""

    session_id: str
    agent_id: str
    start_time: float
    last_activity: float
    current_task: str = "idle"
    progress_percentage: float = 0.0
    vision_alignment: float = 0.0
    is_active: bool = True
    process_id: Optional[int] = None


@dataclass
class AgentActivityEvent:
    """Individual agent activity event."""

    timestamp: float
    agent_id: str
    activity_type: (
        str  # "task_started", "task_progress", "gate_created", "file_modified", etc.
    )
    description: str
    confidence: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentActivityMonitor:
    """
    Real-time monitor for AI agent activities and progress.

    Tracks:
    - Active agent sessions and their current tasks
    - Progress toward project goals
    - Alignment with project vision
    - Activity history and patterns
    - Resource usage and performance
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ai_onboard_dir = project_root / ".ai_onboard"

        # Core systems
        self.gate_mediator = get_ai_gate_mediator(project_root)

        # Activity tracking
        self.active_sessions: Dict[str, AgentSession] = {}
        self.activity_history: List[AgentActivityEvent] = []
        self.session_log_path = self.ai_onboard_dir / "session_log.jsonl"
        self.activity_cache_path = self.ai_onboard_dir / "activity_cache.json"

        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_scan_time = 0.0
        self.scan_interval = 5.0  # seconds

        # Ensure directories exist
        self.ai_onboard_dir.mkdir(exist_ok=True)

        # Load existing activity data
        self._load_activity_cache()

    def start_monitoring(self) -> None:
        """Start real-time agent activity monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        print("🤖 Agent Activity Monitor started")

    def stop_monitoring(self) -> None:
        """Stop agent activity monitoring."""
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)

        self._save_activity_cache()
        print("⏹️ Agent Activity Monitor stopped")

    def get_current_activity(self) -> Optional[AgentSession]:
        """Get the most active/recent agent session."""
        if not self.active_sessions:
            return None

        # Return the session with most recent activity
        most_recent = max(self.active_sessions.values(), key=lambda s: s.last_activity)

        # Check if session is still active (not idle for too long)
        if time.time() - most_recent.last_activity > 300:  # 5 minutes
            most_recent.is_active = False

        return most_recent if most_recent.is_active else None

    def update_agent_activity(
        self,
        agent_id: str,
        task: str,
        progress: float = 0.0,
        confidence: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update agent activity with current task and progress."""
        current_time = time.time()

        # Get or create session
        session_id = f"{agent_id}_{int(current_time)}"
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = AgentSession(
                session_id=session_id,
                agent_id=agent_id,
                start_time=current_time,
                last_activity=current_time,
            )

        session = self.active_sessions[session_id]
        session.current_task = task
        session.last_activity = current_time
        session.progress_percentage = progress
        session.vision_alignment = self._calculate_vision_alignment(
            agent_id, task, metadata or {}
        )

        # Log activity event
        event = AgentActivityEvent(
            timestamp=current_time,
            agent_id=agent_id,
            activity_type="task_progress",
            description=f"Agent {agent_id} working on: {task}",
            confidence=confidence,
            metadata=metadata or {},
        )
        self.activity_history.append(event)

        # Keep only recent history (last 100 events)
        if len(self.activity_history) > 100:
            self.activity_history = self.activity_history[-100:]

        # Save to disk periodically
        if current_time - self.last_scan_time > 30:  # Every 30 seconds
            self._save_activity_cache()

    def log_agent_action(
        self,
        agent_id: str,
        action_type: str,
        description: str,
        confidence: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a specific agent action or decision."""
        event = AgentActivityEvent(
            timestamp=time.time(),
            agent_id=agent_id,
            activity_type=action_type,
            description=description,
            confidence=confidence,
            metadata=metadata or {},
        )

        self.activity_history.append(event)

        # Update session activity if this agent has an active session
        for session in self.active_sessions.values():
            if session.agent_id == agent_id and session.is_active:
                session.last_activity = event.timestamp
                break

    def detect_idle_agents(self) -> List[str]:
        """Detect agents that appear to be idle."""
        current_time = time.time()
        idle_threshold = 300  # 5 minutes

        idle_agents = []
        for session_id, session in self.active_sessions.items():
            if (
                session.is_active
                and (current_time - session.last_activity) > idle_threshold
            ):
                idle_agents.append(session.agent_id)
                session.is_active = False

        return idle_agents

    def get_activity_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of agent activities over specified time period."""
        cutoff_time = time.time() - (hours * 3600)

        # Filter recent activities
        recent_events = [
            event for event in self.activity_history if event.timestamp > cutoff_time
        ]

        # Group by agent
        agent_summary: Dict[str, Dict[str, Any]] = {}
        for event in recent_events:
            agent_id = event.agent_id
            if agent_id not in agent_summary:
                agent_summary[agent_id] = {
                    "events_count": 0,
                    "activity_types": set(),
                    "last_activity": 0.0,
                    "total_confidence": 0.0,
                }

            summary = agent_summary[agent_id]
            summary["events_count"] += 1
            summary["activity_types"].add(event.activity_type)
            summary["last_activity"] = max(summary["last_activity"], event.timestamp)
            summary["total_confidence"] += event.confidence

        # Calculate averages
        for agent_id, summary in agent_summary.items():
            if summary["events_count"] > 0:
                summary["avg_confidence"] = (
                    summary["total_confidence"] / summary["events_count"]
                )
            summary["activity_types"] = list(summary["activity_types"])

        return {
            "time_range_hours": hours,
            "total_events": len(recent_events),
            "active_agents": len(agent_summary),
            "agent_details": agent_summary,
            "generated_at": time.time(),
        }

    def _monitoring_loop(self) -> None:
        """Main monitoring loop running in background thread."""
        while self.monitoring_active:
            try:
                self._scan_for_agent_activity()
                time.sleep(self.scan_interval)
            except Exception as e:
                print(f"Warning: Agent activity monitoring error: {e}")
                time.sleep(self.scan_interval)

    def _scan_for_agent_activity(self) -> None:
        """Scan for current agent activities and update tracking."""
        current_time = time.time()
        self.last_scan_time = current_time

        # Check for active Cursor sessions
        self._detect_cursor_activity()

        # Check for active gate sessions
        self._detect_gate_activity()

        # Check system processes for AI-related activity
        self._detect_process_activity()

        # Clean up old inactive sessions
        self._cleanup_inactive_sessions()

    def _detect_cursor_activity(self) -> None:
        """Detect Cursor AI activity."""
        try:
            current_time = time.time()
            cursor_config = utils.read_json(
                self.ai_onboard_dir / "cursor_config.json", default={}
            )

            if cursor_config.get("active", False):
                session_id = "cursor_main"
                if session_id not in self.active_sessions:
                    self.active_sessions[session_id] = AgentSession(
                        session_id=session_id,
                        agent_id="cursor_ai",
                        start_time=current_time,
                        last_activity=current_time,
                        current_task="AI development session",
                    )

                # Update activity
                session = self.active_sessions[session_id]
                session.last_activity = current_time
                session.vision_alignment = self._calculate_vision_alignment(
                    "cursor_ai", session.current_task, {}
                )

        except Exception as e:
            print(f"Warning: Error detecting Cursor activity: {e}")

    def _detect_gate_activity(self) -> None:
        """Detect activity from gate system."""
        try:
            # Check for active gates
            current_gate_file = self.ai_onboard_dir / "gates" / "current_gate.md"
            if current_gate_file.exists():
                gate_status = utils.read_json(
                    self.ai_onboard_dir / "gates" / "gate_status.json", default={}
                )

                if gate_status.get("status") == "pending":
                    agent_id = gate_status.get("agent_id", "unknown")

                    # Update or create session for this agent
                    session_id = f"{agent_id}_gate_{int(time.time())}"
                    if session_id not in self.active_sessions:
                        self.active_sessions[session_id] = AgentSession(
                            session_id=session_id,
                            agent_id=agent_id,
                            start_time=time.time(),
                            last_activity=time.time(),
                            current_task=f"Waiting for gate approval: {gate_status.get('question', 'Unknown')}",
                        )

                    session = self.active_sessions[session_id]
                    session.last_activity = time.time()
                    session.current_task = (
                        f"Gate pending: {gate_status.get('question', 'Unknown')}"
                    )

        except Exception as e:
            print(f"Warning: Error detecting gate activity: {e}")

    def _detect_process_activity(self) -> None:
        """Detect AI-related process activity."""
        try:
            # Look for Python processes that might be AI agents
            for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
                try:
                    if self._is_ai_agent_process(proc):
                        agent_id = self._identify_agent_from_process(proc)
                        if agent_id:
                            # Update session for this process
                            session_id = f"process_{proc.info['pid']}"
                            if session_id not in self.active_sessions:
                                self.active_sessions[session_id] = AgentSession(
                                    session_id=session_id,
                                    agent_id=agent_id,
                                    start_time=proc.info["create_time"],
                                    last_activity=time.time(),
                                    current_task="Running AI agent process",
                                    process_id=proc.info["pid"],
                                )

                            session = self.active_sessions[session_id]
                            session.last_activity = time.time()

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            print(f"Warning: Error detecting process activity: {e}")

    def _is_ai_agent_process(self, proc) -> bool:
        """Check if a process is likely an AI agent."""
        try:
            cmdline = " ".join(proc.info.get("cmdline", []))

            # Look for AI-related keywords
            ai_indicators = [
                "cursor",
                "copilot",
                "claude",
                "gpt",
                "openai",
                "anthropic",
                "ai_onboard",
                "python -m",
                "uvicorn",
                "fastapi",
            ]

            return any(indicator in cmdline.lower() for indicator in ai_indicators)

        except Exception:
            return False

    def _identify_agent_from_process(self, proc) -> Optional[str]:
        """Try to identify which AI agent a process belongs to."""
        try:
            cmdline = " ".join(proc.info.get("cmdline", []))

            if "cursor" in cmdline.lower():
                return "cursor_ai"
            elif "copilot" in cmdline.lower():
                return "copilot"
            elif "claude" in cmdline.lower():
                return "claude"
            elif any(
                ai_term in cmdline.lower() for ai_term in ["openai", "gpt", "anthropic"]
            ):
                return "llm_agent"
            elif "ai_onboard" in cmdline.lower():
                return "ai_onboard"

        except Exception:
            pass

        return None

    def _calculate_vision_alignment(
        self, agent_id: str, current_task: str, metadata: Dict[str, Any]
    ) -> float:
        """Calculate how aligned current agent activity is with project vision."""
        try:
            # Load current vision
            charter_data = utils.read_json(
                self.ai_onboard_dir / "charter.json", default={}
            )

            if not charter_data:
                return 0.5  # Neutral alignment if no vision

            vision = charter_data.get("vision", {})
            primary_goal = vision.get("primary_goal", "")

            if not primary_goal:
                return 0.5

            # Simple keyword matching for alignment
            task_lower = current_task.lower()
            goal_lower = primary_goal.lower()

            # Check for direct matches
            alignment_score = 0.0

            # High alignment for direct matches
            if any(word in task_lower for word in goal_lower.split()):
                alignment_score = 0.9

            # Medium alignment for related concepts
            elif any(
                concept in task_lower
                for concept in ["build", "create", "implement", "develop"]
            ):
                alignment_score = 0.7

            # Low alignment for generic tasks
            else:
                alignment_score = 0.3

            return min(1.0, alignment_score)

        except Exception:
            return 0.5

    def _cleanup_inactive_sessions(self) -> None:
        """Clean up sessions that have been inactive for too long."""
        current_time = time.time()
        inactive_threshold = 1800  # 30 minutes

        inactive_sessions = []
        for session_id, session in self.active_sessions.items():
            if (current_time - session.last_activity) > inactive_threshold:
                inactive_sessions.append(session_id)

        for session_id in inactive_sessions:
            del self.active_sessions[session_id]

    def _load_activity_cache(self) -> None:
        """Load cached activity data from disk."""
        try:
            if self.activity_cache_path.exists():
                cache_data = utils.read_json(self.activity_cache_path)

                # Restore active sessions
                sessions_data = cache_data.get("active_sessions", {})
                for session_id, session_data in sessions_data.items():
                    self.active_sessions[session_id] = AgentSession(**session_data)

                # Restore recent activity history
                history_data = cache_data.get("recent_activity", [])
                for event_data in history_data:
                    self.activity_history.append(AgentActivityEvent(**event_data))

        except Exception as e:
            print(f"Warning: Could not load activity cache: {e}")

    def _save_activity_cache(self) -> None:
        """Save current activity data to disk."""
        try:
            cache_data = {
                "active_sessions": {
                    session_id: {
                        "session_id": session.session_id,
                        "agent_id": session.agent_id,
                        "start_time": session.start_time,
                        "last_activity": session.last_activity,
                        "current_task": session.current_task,
                        "progress_percentage": session.progress_percentage,
                        "vision_alignment": session.vision_alignment,
                        "is_active": session.is_active,
                        "process_id": session.process_id,
                    }
                    for session_id, session in self.active_sessions.items()
                },
                "recent_activity": [
                    {
                        "timestamp": event.timestamp,
                        "agent_id": event.agent_id,
                        "activity_type": event.activity_type,
                        "description": event.description,
                        "confidence": event.confidence,
                        "metadata": event.metadata,
                    }
                    for event in self.activity_history[-20:]  # Save last 20 events
                ],
                "saved_at": time.time(),
            }

            utils.write_json(self.activity_cache_path, cache_data)

        except Exception as e:
            print(f"Warning: Could not save activity cache: {e}")

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status and statistics."""
        return {
            "monitoring_active": self.monitoring_active,
            "active_sessions": len(self.active_sessions),
            "total_activity_events": len(self.activity_history),
            "last_scan": self.last_scan_time,
            "uptime_seconds": time.time() - (self.last_scan_time or time.time()),
            "cache_size_mb": (
                self.activity_cache_path.stat().st_size / (1024 * 1024)
                if self.activity_cache_path.exists()
                else 0
            ),
        }


def get_agent_activity_monitor(project_root: Path) -> AgentActivityMonitor:
    """Get or create agent activity monitor for the project."""
    return AgentActivityMonitor(project_root)
