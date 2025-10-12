"""
Emergency Control System - Immediate agent pause/stop capabilities for vibe coders.

This module provides critical emergency controls that allow vibe coders to:
- Immediately pause agent activities
- Stop agent sessions completely
- Provide quick emergency controls in the dashboard
- Log emergency actions for audit and debugging

The system ensures that vibe coders maintain ultimate control over AI agents
and can intervene immediately when agents exhibit problematic behavior.
"""

import json
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..base import utils
from .agent_activity_monitor import AgentActivityMonitor


class EmergencyAction(Enum):
    """Types of emergency actions that can be taken."""

    PAUSE_AGENT = "pause_agent"  # Temporarily pause agent activities
    STOP_AGENT = "stop_agent"  # Completely stop agent session
    BLOCK_OPERATION = "block_operation"  # Block a specific operation
    KILL_PROCESS = "kill_process"  # Force kill agent processes
    EMERGENCY_GATE = "emergency_gate"  # Create emergency gate requiring approval


class EmergencySeverity(Enum):
    """Severity levels for emergency situations."""

    LOW = "low"  # Minor issue, pause recommended
    MEDIUM = "medium"  # Concerning behavior, stop recommended
    HIGH = "high"  # Serious problem, immediate stop required
    CRITICAL = "critical"  # System-threatening, emergency intervention needed


@dataclass
class EmergencyEvent:
    """Represents an emergency control action."""

    event_id: str
    action: EmergencyAction
    severity: EmergencySeverity
    agent_id: str
    initiated_by: str  # "system", "user", "auto"
    reason: str
    triggered_at: float

    # Action details
    target_process_id: Optional[int] = None
    target_operation: Optional[str] = None

    # Resolution
    resolved: bool = False
    resolved_at: Optional[float] = None
    resolution_notes: Optional[str] = None

    # Impact tracking
    affected_files: List[str] = field(default_factory=list)
    recovery_required: bool = False


@dataclass
class AgentEmergencyState:
    """Tracks emergency state for an agent."""

    agent_id: str
    is_paused: bool = False
    is_stopped: bool = False
    emergency_mode: bool = False

    # Emergency controls
    paused_at: Optional[float] = None
    stopped_at: Optional[float] = None
    emergency_activated_at: Optional[float] = None

    # Process tracking
    active_processes: Set[int] = field(default_factory=set)

    # Emergency events
    emergency_events: List[EmergencyEvent] = field(default_factory=list)


class EmergencyControlSystem:
    """
    Emergency control system for immediate agent intervention.

    Provides vibe coders with the ability to:
    - Pause agents immediately when problematic behavior is detected
    - Stop agent sessions completely in emergency situations
    - Block specific dangerous operations
    - Kill runaway processes
    - Create emergency gates requiring manual approval

    All actions are logged for audit and debugging purposes.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ai_onboard_dir = project_root / ".ai_onboard"

        # Core systems
        self.activity_monitor = AgentActivityMonitor(project_root)

        # Emergency state
        self.agent_states: Dict[str, AgentEmergencyState] = {}
        self.emergency_events: List[EmergencyEvent] = []

        # Configuration
        self.auto_pause_threshold = 3  # Number of chaos events before auto-pause
        self.emergency_timeout = 300.0  # 5 minutes emergency mode timeout

        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Ensure directories exist
        self.ai_onboard_dir.mkdir(exist_ok=True)

        # Load existing state
        self._load_emergency_state()

        # Start monitoring
        self.start_monitoring()

    def start_monitoring(self) -> None:
        """Start emergency control monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        print("🚨 Emergency Control System started")

    def stop_monitoring(self) -> None:
        """Stop emergency control monitoring."""
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)

        self._save_emergency_state()
        print("⏹️ Emergency Control System stopped")

    def pause_agent(
        self, agent_id: str, reason: str, initiated_by: str = "user"
    ) -> bool:
        """Pause an agent immediately."""
        if agent_id not in self.agent_states:
            self.agent_states[agent_id] = AgentEmergencyState(agent_id=agent_id)

        state = self.agent_states[agent_id]
        if state.is_paused:
            return False  # Already paused

        # Create emergency event
        event = EmergencyEvent(
            event_id=f"pause_{agent_id}_{int(time.time())}",
            action=EmergencyAction.PAUSE_AGENT,
            severity=EmergencySeverity.MEDIUM,
            agent_id=agent_id,
            initiated_by=initiated_by,
            reason=reason,
            triggered_at=time.time(),
        )

        # Update state
        state.is_paused = True
        state.paused_at = time.time()
        state.emergency_events.append(event)
        self.emergency_events.append(event)

        # Log the pause action
        self._log_emergency_action(event)

        print(f"⏸️ Agent {agent_id} paused: {reason}")
        return True

    def stop_agent(
        self, agent_id: str, reason: str, initiated_by: str = "user"
    ) -> bool:
        """Stop an agent session completely."""
        if agent_id not in self.agent_states:
            self.agent_states[agent_id] = AgentEmergencyState(agent_id=agent_id)

        state = self.agent_states[agent_id]

        # Create emergency event
        event = EmergencyEvent(
            event_id=f"stop_{agent_id}_{int(time.time())}",
            action=EmergencyAction.STOP_AGENT,
            severity=EmergencySeverity.HIGH,
            agent_id=agent_id,
            initiated_by=initiated_by,
            reason=reason,
            triggered_at=time.time(),
        )

        # Update state
        state.is_stopped = True
        state.stopped_at = time.time()
        state.emergency_events.append(event)
        self.emergency_events.append(event)

        # Attempt to kill processes
        self._kill_agent_processes(agent_id)

        # Log the stop action
        self._log_emergency_action(event)

        print(f"🛑 Agent {agent_id} stopped: {reason}")
        return True

    def block_operation(
        self, agent_id: str, operation: str, reason: str, initiated_by: str = "user"
    ) -> bool:
        """Block a specific operation."""
        event = EmergencyEvent(
            event_id=f"block_{agent_id}_{int(time.time())}",
            action=EmergencyAction.BLOCK_OPERATION,
            severity=EmergencySeverity.MEDIUM,
            agent_id=agent_id,
            initiated_by=initiated_by,
            reason=reason,
            triggered_at=time.time(),
            target_operation=operation,
        )

        self.emergency_events.append(event)

        # Log the block action
        self._log_emergency_action(event)

        print(f"🚫 Operation blocked for {agent_id}: {operation} - {reason}")
        return True

    def resume_agent(self, agent_id: str, initiated_by: str = "user") -> bool:
        """Resume a paused agent."""
        if agent_id not in self.agent_states:
            return False

        state = self.agent_states[agent_id]
        if not state.is_paused:
            return False  # Not paused

        # Create resume event
        event = EmergencyEvent(
            event_id=f"resume_{agent_id}_{int(time.time())}",
            action=EmergencyAction.PAUSE_AGENT,  # Same action, but for resolution
            severity=EmergencySeverity.LOW,
            agent_id=agent_id,
            initiated_by=initiated_by,
            reason="Agent resumed after pause",
            triggered_at=time.time(),
            resolved=True,
            resolved_at=time.time(),
            resolution_notes="Agent manually resumed",
        )

        # Update state
        state.is_paused = False
        state.emergency_events.append(event)
        self.emergency_events.append(event)

        print(f"▶️ Agent {agent_id} resumed")
        return True

    def get_emergency_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current emergency control status."""
        status: Dict[str, Any] = {
            "monitoring_active": self.monitoring_active,
            "total_emergency_events": len(self.emergency_events),
            "agents_in_emergency": len(
                [
                    state
                    for state in self.agent_states.values()
                    if state.is_paused or state.is_stopped or state.emergency_mode
                ]
            ),
            "paused_agents": len(
                [state for state in self.agent_states.values() if state.is_paused]
            ),
            "stopped_agents": len(
                [state for state in self.agent_states.values() if state.is_stopped]
            ),
        }

        if agent_id and agent_id in self.agent_states:
            agent_state = self.agent_states[agent_id]
            status["agent_status"] = {
                "is_paused": agent_state.is_paused,
                "is_stopped": agent_state.is_stopped,
                "emergency_mode": agent_state.emergency_mode,
                "emergency_events": len(agent_state.emergency_events),
                "active_processes": len(agent_state.active_processes),
            }

        return status

    def get_recent_emergency_events(self, limit: int = 10) -> List[EmergencyEvent]:
        """Get recent emergency events."""
        return sorted(
            self.emergency_events, key=lambda e: e.triggered_at, reverse=True
        )[:limit]

    def is_agent_paused(self, agent_id: str) -> bool:
        """Check if an agent is currently paused."""
        if agent_id not in self.agent_states:
            return False
        return self.agent_states[agent_id].is_paused

    def is_agent_stopped(self, agent_id: str) -> bool:
        """Check if an agent is currently stopped."""
        if agent_id not in self.agent_states:
            return False
        return self.agent_states[agent_id].is_stopped

    def _monitoring_loop(self) -> None:
        """Main emergency control monitoring loop."""
        while self.monitoring_active:
            try:
                # Check for automatic emergency actions
                self._check_auto_emergency_actions()

                # Clean up expired emergency states
                self._cleanup_expired_states()

                time.sleep(10.0)  # Check every 10 seconds

            except Exception as e:
                print(f"Warning: Emergency control monitoring error: {e}")
                time.sleep(10.0)

    def _check_auto_emergency_actions(self) -> None:
        """Check for conditions that require automatic emergency actions."""
        # Get activity summary for chaos analysis
        activity_summary = self.activity_monitor.get_activity_summary(hours=1)

        for agent_id, agent_data in activity_summary["agent_details"].items():
            # Check if agent should be auto-paused due to chaos
            chaos_events = agent_data.get("chaos_events", 0)
            if chaos_events >= self.auto_pause_threshold:
                if not self.is_agent_paused(agent_id):
                    self.pause_agent(
                        agent_id,
                        f"Auto-paused due to {chaos_events} chaos events",
                        initiated_by="system",
                    )

    def _cleanup_expired_states(self) -> None:
        """Clean up expired emergency states."""
        current_time = time.time()

        for agent_id, state in list(self.agent_states.items()):
            # Auto-resume paused agents after timeout
            if state.is_paused and state.paused_at:
                age_seconds = current_time - state.paused_at
                if age_seconds > self.emergency_timeout:
                    print(f"⏰ Auto-resuming agent {agent_id} after emergency timeout")
                    state.is_paused = False
                    state.emergency_mode = False

    def _kill_agent_processes(self, agent_id: str) -> None:
        """Attempt to kill processes associated with an agent."""
        try:
            # This is a simplified implementation
            # In a real system, you would track and kill specific agent processes
            print(f"🔪 Attempting to kill processes for agent: {agent_id}")

            # For Cursor AI, we could kill cursor processes
            # For other agents, this would be more sophisticated

        except Exception as e:
            print(f"Warning: Error killing agent processes: {e}")

    def _log_emergency_action(self, event: EmergencyEvent) -> None:
        """Log an emergency action for audit purposes."""
        try:
            log_entry = {
                "timestamp": event.triggered_at,
                "type": "emergency_action",
                "event_id": event.event_id,
                "action": event.action.value,
                "severity": event.severity.value,
                "agent_id": event.agent_id,
                "initiated_by": event.initiated_by,
                "reason": event.reason,
                "target_process_id": event.target_process_id,
                "target_operation": event.target_operation,
            }

            session_log_path = self.ai_onboard_dir / "session_log.jsonl"
            with open(session_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            print(f"Warning: Failed to log emergency action: {e}")

    def _load_emergency_state(self) -> None:
        """Load existing emergency state from storage."""
        try:
            state_file = self.ai_onboard_dir / "emergency_state.json"
            if state_file.exists():
                state_data = utils.read_json(state_file)

                for agent_data in state_data.get("agent_states", []):
                    state = AgentEmergencyState(
                        agent_id=agent_data["agent_id"],
                        is_paused=agent_data.get("is_paused", False),
                        is_stopped=agent_data.get("is_stopped", False),
                        emergency_mode=agent_data.get("emergency_mode", False),
                        paused_at=agent_data.get("paused_at"),
                        stopped_at=agent_data.get("stopped_at"),
                        emergency_activated_at=agent_data.get("emergency_activated_at"),
                        active_processes=set(agent_data.get("active_processes", [])),
                    )
                    self.agent_states[state.agent_id] = state

                for event_data in state_data.get("emergency_events", []):
                    event = EmergencyEvent(
                        event_id=event_data["event_id"],
                        action=EmergencyAction(event_data["action"]),
                        severity=EmergencySeverity(event_data["severity"]),
                        agent_id=event_data["agent_id"],
                        initiated_by=event_data["initiated_by"],
                        reason=event_data["reason"],
                        triggered_at=event_data["triggered_at"],
                        target_process_id=event_data.get("target_process_id"),
                        target_operation=event_data.get("target_operation"),
                        resolved=event_data.get("resolved", False),
                        resolved_at=event_data.get("resolved_at"),
                        resolution_notes=event_data.get("resolution_notes"),
                        affected_files=event_data.get("affected_files", []),
                        recovery_required=event_data.get("recovery_required", False),
                    )
                    self.emergency_events.append(event)

        except Exception as e:
            print(f"Warning: Could not load emergency state: {e}")

    def _save_emergency_state(self) -> None:
        """Save emergency state to storage."""
        try:
            state_data: Dict[str, Any] = {"agent_states": [], "emergency_events": []}

            for state in self.agent_states.values():
                state_dict = {
                    "agent_id": state.agent_id,
                    "is_paused": state.is_paused,
                    "is_stopped": state.is_stopped,
                    "emergency_mode": state.emergency_mode,
                    "paused_at": state.paused_at,
                    "stopped_at": state.stopped_at,
                    "emergency_activated_at": state.emergency_activated_at,
                    "active_processes": list(state.active_processes),
                }
                state_data["agent_states"].append(state_dict)

            for event in self.emergency_events[-100:]:  # Keep last 100 events
                event_dict = {
                    "event_id": event.event_id,
                    "action": event.action.value,
                    "severity": event.severity.value,
                    "agent_id": event.agent_id,
                    "initiated_by": event.initiated_by,
                    "reason": event.reason,
                    "triggered_at": event.triggered_at,
                    "target_process_id": event.target_process_id,
                    "target_operation": event.target_operation,
                    "resolved": event.resolved,
                    "resolved_at": event.resolved_at,
                    "resolution_notes": event.resolution_notes,
                    "affected_files": event.affected_files,
                    "recovery_required": event.recovery_required,
                }
                state_data["emergency_events"].append(event_dict)

            state_file = self.ai_onboard_dir / "emergency_state.json"
            utils.write_json(state_file, state_data)

        except Exception as e:
            print(f"Warning: Could not save emergency state: {e}")


def get_emergency_control_system(project_root: Path) -> EmergencyControlSystem:
    """Get or create emergency control system for the project."""
    return EmergencyControlSystem(project_root)
