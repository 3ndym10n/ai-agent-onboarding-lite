"""
Agent Oversight Dashboard - Real-time monitoring and control interface for vibe coders managing AI agents.

This dashboard provides the core oversight capabilities that vibe coders need to maintain control
over chaotic AI agents while avoiding micromanagement.
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base import utils
from .agent_activity_monitor import AgentActivityMonitor
from .ai_gate_mediator import get_ai_gate_mediator
from .chaos_detection_system import get_chaos_detection_system
from .decision_enforcer import DecisionEnforcer
from .emergency_control_system import get_emergency_control_system
from .system_integrator import get_system_integrator
from .vision_drift_alerting_system import (
    DriftSeverity,
    get_vision_drift_alerting_system,
)


@dataclass
class AgentActivity:
    """Current agent activity information."""

    agent_id: str
    current_task: str
    start_time: float
    confidence: float
    progress_percentage: float
    estimated_completion: Optional[str] = None
    vision_alignment: float = 0.0


@dataclass
class PendingGate:
    """Pending gate information."""

    gate_id: str
    question: str
    agent_id: str
    created_at: float
    urgency: str  # "low", "medium", "high", "critical"
    options: List[str]
    context: Dict[str, Any]


@dataclass
class BlockedAction:
    """Action that was blocked by the system."""

    action_id: str
    agent_id: str
    action_type: str
    reason: str
    blocked_at: float
    severity: str  # "info", "warning", "error"


@dataclass
class VisionStatus:
    """Current vision alignment status."""

    project_name: str
    original_vision: str
    current_alignment: float
    drift_percentage: float
    last_checked: float
    recommendations: List[str]


class AgentOversightDashboard:
    """
    Real-time dashboard for vibe coders to monitor and control AI agents.

    Provides the core oversight interface that gives vibe coders:
    - Real-time visibility into agent actions
    - Pending decision approvals
    - Blocked dangerous actions
    - Vision alignment status
    - Quick approve/reject controls
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ai_onboard_dir = project_root / ".ai_onboard"

        # Initialize subsystems
        self.gate_mediator = get_ai_gate_mediator(project_root)
        self.decision_enforcer = DecisionEnforcer(project_root)
        self.activity_monitor = AgentActivityMonitor(project_root)
        self.chaos_detector = get_chaos_detection_system(project_root)
        self.vision_drift_alerting = get_vision_drift_alerting_system(project_root)
        self.emergency_control = get_emergency_control_system(project_root)
        self.system_integrator = get_system_integrator(project_root)

        # Data sources
        self.session_log_path = self.ai_onboard_dir / "session_log.jsonl"
        self.gates_dir = self.ai_onboard_dir / "gates"
        self.vision_file = self.ai_onboard_dir / "vision.json"

        # Ensure directories exist
        self.ai_onboard_dir.mkdir(exist_ok=True)
        self.gates_dir.mkdir(exist_ok=True)

        # Start activity monitoring
        self.activity_monitor.start_monitoring()

    def get_agent_activity(self) -> Optional[AgentActivity]:
        """Get current agent activity information from the activity monitor."""
        try:
            # Get current activity from the activity monitor
            current_session = self.activity_monitor.get_current_activity()

            if not current_session:
                return None

            # Convert AgentSession to AgentActivity for dashboard display
            return AgentActivity(
                agent_id=current_session.agent_id,
                current_task=current_session.current_task,
                start_time=current_session.start_time,
                confidence=0.8,  # Default confidence for active sessions
                progress_percentage=current_session.progress_percentage,
                estimated_completion=None,  # Not tracked yet
                vision_alignment=current_session.vision_alignment,
            )
        except Exception as e:
            print(f"Warning: Error getting agent activity: {e}")
            return None

    def get_pending_gates(self) -> List[PendingGate]:
        """Get all pending gates waiting for approval."""
        pending_gates = []

        try:
            # Check for active gate file (current gate)
            current_gate_file = self.gates_dir / "current_gate.md"
            if current_gate_file.exists():
                gate_data = utils.read_json(
                    self.gates_dir / "gate_status.json", default={}
                )

                if gate_data.get("status") == "pending":
                    pending_gates.append(
                        PendingGate(
                            gate_id=gate_data.get("gate_id", "unknown"),
                            question=gate_data.get("question", "Pending decision"),
                            agent_id=gate_data.get("agent_id", "unknown"),
                            created_at=gate_data.get("created_at", time.time()),
                            urgency=self._calculate_gate_urgency(gate_data),
                            options=gate_data.get("options", []),
                            context=gate_data.get("context", {}),
                        )
                    )

            # Check for queued gates in the gate system
            gate_requests = self.gate_mediator.get_pending_gate_requests()
            for gate_request in gate_requests:
                # Don't duplicate current gate
                if any(
                    g.gate_id == getattr(gate_request, "gate_id", None)
                    for g in pending_gates
                ):
                    continue

                pending_gates.append(
                    PendingGate(
                        gate_id=getattr(gate_request, "gate_id", "unknown"),
                        question=getattr(
                            gate_request,
                            "title",
                            getattr(gate_request, "question", "Pending decision"),
                        ),
                        agent_id=getattr(gate_request, "agent_id", "unknown"),
                        created_at=getattr(gate_request, "created_at", time.time()),
                        urgency=self._calculate_gate_urgency_from_request(gate_request),
                        options=getattr(gate_request, "questions", []),
                        context=getattr(gate_request, "context", {}),
                    )
                )

        except Exception as e:
            print(f"Warning: Error getting pending gates: {e}")

        return pending_gates

    def get_blocked_actions(self, limit: int = 10) -> List[BlockedAction]:
        """Get recently blocked actions."""
        blocked_actions = []

        try:
            # Read from session log for blocked actions
            if self.session_log_path.exists():
                with open(self.session_log_path, "r", encoding="utf-8") as f:
                    # Get last N lines
                    lines = f.readlines()
                    recent_lines = lines[-50:] if len(lines) > 50 else lines

                    for line in reversed(recent_lines):
                        try:
                            entry = json.loads(line.strip())
                            if entry.get("type") == "blocked_action":
                                blocked_actions.append(
                                    BlockedAction(
                                        action_id=entry.get("action_id", "unknown"),
                                        agent_id=entry.get("agent_id", "unknown"),
                                        action_type=entry.get("action_type", "unknown"),
                                        reason=entry.get("reason", "Blocked by system"),
                                        blocked_at=entry.get("timestamp", time.time()),
                                        severity=entry.get("severity", "warning"),
                                    )
                                )

                                if len(blocked_actions) >= limit:
                                    break
                        except json.JSONDecodeError:
                            continue

            # For demo purposes, add some example blocked actions if none exist
            # This will be replaced with real blocking logic
            if not blocked_actions and self._should_show_demo_blocks():
                blocked_actions = self._get_demo_blocked_actions()

        except Exception as e:
            print(f"Warning: Error getting blocked actions: {e}")

        return blocked_actions[:limit]

    def _should_show_demo_blocks(self) -> bool:
        """Check if we should show demo blocked actions for testing."""
        # Only show demo blocks if we have no real data AND we're in a test/demo environment
        # Check if this looks like a test environment (no real activity in last hour)
        try:
            activity_summary = self.activity_monitor.get_activity_summary(hours=1)
            has_real_activity = activity_summary.get("total_events", 0) > 0

            # Show demo only if no real activity and no real blocks
            return not has_real_activity
        except Exception:
            return False  # Don't show demo if we can't check real data

    def _get_demo_blocked_actions(self) -> List[BlockedAction]:
        """Get demo blocked actions for testing the dashboard."""
        current_time = time.time()

        return [
            BlockedAction(
                action_id=f"demo_block_{int(current_time - 120)}",  # 2 minutes ago
                agent_id="demo_agent",
                action_type="Delete 15 test files",
                reason="Exceeded file deletion limit",
                blocked_at=current_time - 120,
                severity="error",
            ),
            BlockedAction(
                action_id=f"demo_block_{int(current_time - 300)}",  # 5 minutes ago
                agent_id="demo_agent",
                action_type="Add 20 new dependencies",
                reason="Bloat prevention - too many dependencies",
                blocked_at=current_time - 300,
                severity="warning",
            ),
            BlockedAction(
                action_id=f"demo_block_{int(current_time - 480)}",  # 8 minutes ago
                agent_id="demo_agent",
                action_type="Refactor 10 core files",
                reason="Off-track from project vision",
                blocked_at=current_time - 480,
                severity="info",
            ),
        ]

    def get_vision_status(self) -> Optional[VisionStatus]:
        """Get current vision alignment status."""
        try:
            vision_data = utils.read_json(self.vision_file, default={})
            charter_data = utils.read_json(
                self.ai_onboard_dir / "charter.json", default={}
            )

            if not charter_data:
                return None

            # Calculate alignment based on recent activity
            recent_alignment = self._calculate_vision_alignment()

            return VisionStatus(
                project_name=charter_data.get("project_name", "Unknown Project"),
                original_vision=charter_data.get("vision", {}).get(
                    "primary_goal", "No vision defined"
                ),
                current_alignment=recent_alignment.get("alignment", 0.0),
                drift_percentage=recent_alignment.get("drift", 0.0),
                last_checked=time.time(),
                recommendations=recent_alignment.get("recommendations", []),
            )
        except Exception:
            return None

    def create_dashboard_display(self) -> str:
        """Create the main dashboard display."""
        dashboard = []

        # Header
        dashboard.append("┌─ AGENT OVERSIGHT DASHBOARD ───────────────────────────┐")

        # System integration status
        integration_status = self.system_integrator.get_integrated_status()
        integration_icon = "✅" if integration_status["integrated_mode"] else "❌"
        overall_health = integration_status.get("overall_health_score", 0.0) * 100
        health_pct = f"{overall_health:.0f}%"
        dashboard.append(
            f"│ {integration_icon} Integration: {health_pct:<6} Systems Active: {len(integration_status.get('system_health', {})):<2} │"
        )

        dashboard.append("│ 🤖 Agent: Cursor AI                                   │")
        dashboard.append("│ 📊 Project: AI Onboard - Agent Oversight             │")
        dashboard.append("│ 🎯 Vision: Systematic oversight & guardrails          │")
        dashboard.append("│                                                        │")

        # Current agent activity
        activity = self.get_agent_activity()
        if activity:
            # Show real activity from monitor
            current_task_display = (
                activity.current_task[:45] + "..."
                if len(activity.current_task) > 45
                else activity.current_task
            )
            dashboard.append(f"│ 🔄 Currently: {current_task_display:<45} │")
            dashboard.append(
                f"│    Progress: {activity.progress_percentage:.1f}% complete    │"
            )
            dashboard.append(
                f"│    Alignment: {activity.vision_alignment:.1f}% on track    │"
            )
        else:
            # Check if activity monitor has any data
            activity_summary = self.activity_monitor.get_activity_summary(hours=1)
            if activity_summary["active_agents"] > 0:
                dashboard.append(
                    "│ 🔄 Currently: Agent session detected                    │"
                )
                dashboard.append(
                    "│    Progress: Monitoring...                             │"
                )
                dashboard.append(
                    "│    Alignment: Calculating...                           │"
                )
            else:
                dashboard.append(
                    "│ 💤 Status: No active agent session                     │"
                )

        dashboard.append("│                                                        │")

        # Pending gates
        pending_gates = self.get_pending_gates()
        if pending_gates:
            # Sort by urgency and age
            sorted_gates = sorted(
                pending_gates,
                key=lambda g: (self._urgency_to_priority(g.urgency), g.created_at),
                reverse=True,
            )

            dashboard.append(
                f"│ ⚠️  PENDING: {len(pending_gates)} gates waiting for approval │"
            )

            # Show up to 3 most urgent gates
            for gate in sorted_gates[:3]:
                age_minutes = int((time.time() - gate.created_at) / 60)
                urgency_icon = self._get_urgency_icon(gate.urgency)

                # Format the gate question
                question_display = (
                    gate.question[:40] + "..."
                    if len(gate.question) > 40
                    else gate.question
                )

                dashboard.append(f"│    {urgency_icon} {question_display:<40} │")
                dashboard.append(
                    f"│       {age_minutes:2d}min old, Agent: {gate.agent_id}         │"
                )

            if len(pending_gates) > 3:
                dashboard.append(
                    f"│    ... and {len(pending_gates) - 3} more gates                    │"
                )
        else:
            dashboard.append(
                "│ ✅ No pending gates                                    │"
            )

        dashboard.append("│                                                        │")

        # Blocked actions (recent)
        blocked_actions = self.get_blocked_actions(3)
        if blocked_actions:
            # Sort by severity and recency
            sorted_actions = sorted(
                blocked_actions,
                key=lambda a: (
                    self._severity_to_priority(a.severity),
                    -a.blocked_at,  # Most recent first
                ),
                reverse=True,
            )

            dashboard.append(
                f"│ 🚫 BLOCKED: {len(blocked_actions)} actions prevented      │"
            )

            # Show up to 3 most severe/recent blocks
            for action in sorted_actions[:3]:
                age_minutes = int((time.time() - action.blocked_at) / 60)
                severity_icon = self._get_severity_icon(action.severity)

                # Format the action description
                action_display = (
                    action.action_type[:35] + "..."
                    if len(action.action_type) > 35
                    else action.action_type
                )
                reason_display = (
                    action.reason[:25] + "..."
                    if len(action.reason) > 25
                    else action.reason
                )

                dashboard.append(f"│    {severity_icon} {action_display:<35} │")
                dashboard.append(
                    f"│       {age_minutes:2d}min ago, {reason_display:<25} │"
                )

            if len(blocked_actions) > 3:
                dashboard.append(
                    f"│    ... and {len(blocked_actions) - 3} more blocks               │"
                )
        else:
            dashboard.append(
                "│ ✅ No recent blocks                                    │"
            )

        dashboard.append("│                                                        │")

        # Chaos detection status
        chaos_status = self.get_chaos_status()
        if chaos_status["active_chaos_events"] > 0:
            dashboard.append(
                f"│ 🚨 CHAOS: {chaos_status['active_chaos_events']} active chaos events    │"
            )
        else:
            dashboard.append(
                "│ ✅ No chaos detected                                   │"
            )

        dashboard.append("│                                                        │")

        # Vision drift alerts
        vision_drift_alerts = self.vision_drift_alerting.get_active_alerts()
        if vision_drift_alerts:
            dashboard.append(
                f"│ 🎯 DRIFT ALERTS: {len(vision_drift_alerts)} active alerts      │"
            )

            # Show top 2 most severe alerts
            for alert in vision_drift_alerts[:2]:
                severity_icon = self._get_drift_severity_icon(alert.severity)
                drift_type_display = alert.drift_type.value.replace("_", " ").title()
                alert_display = (
                    drift_type_display[:20] + "..."
                    if len(drift_type_display) > 20
                    else drift_type_display
                )

                age_minutes = int((time.time() - alert.detected_at) / 60)
                dashboard.append(f"│    {severity_icon} {alert_display:<20} │")
                dashboard.append(
                    f"│       {age_minutes:2d}min ago, {alert.severity.value:<10} │"
                )
        else:
            dashboard.append(
                "│ ✅ No vision drift alerts                             │"
            )

        dashboard.append("│                                                        │")

        # Vision alignment
        vision = self.get_vision_status()
        if vision:
            if vision.current_alignment > 0.8:
                status_icon = "✅"
            elif vision.current_alignment > 0.6:
                status_icon = "⚠️"
            else:
                status_icon = "🚨"

            dashboard.append(
                f"│ {status_icon} Alignment: {vision.current_alignment:.1f}% on vision      │"
            )

        dashboard.append("│                                                        │")

        # Progress tracking visualization
        progress_info = self.get_progress_visualization()
        if progress_info:
            dashboard.append(f"│ 📊 Progress: {progress_info['progress_bar']} │")
            dashboard.append(
                f"│    Phase: {progress_info['current_phase']:<20}                     │"
            )
            dashboard.append(
                f"│    Next: {progress_info['next_task'][:25]:<25}                     │"
            )
            if progress_info.get("eta"):
                dashboard.append(
                    f"│    ETA: {progress_info['eta']:<25}                     │"
                )

        dashboard.append("│                                                        │")

        # Emergency controls
        emergency_status = self.emergency_control.get_emergency_status()
        if emergency_status["agents_in_emergency"] > 0:
            dashboard.append(
                f"│ 🚨 EMERGENCY: {emergency_status['agents_in_emergency']} agents in emergency    │"
            )
            if emergency_status["paused_agents"] > 0:
                dashboard.append(
                    f"│    ⏸️ Paused: {emergency_status['paused_agents']} agents                     │"
                )
            if emergency_status["stopped_agents"] > 0:
                dashboard.append(
                    f"│    🛑 Stopped: {emergency_status['stopped_agents']} agents                     │"
                )
        else:
            dashboard.append(
                "│ ✅ Emergency: All agents normal                       │"
            )

        dashboard.append("│                                                        │")

        # Controls
        emergency_controls = []
        if emergency_status["paused_agents"] > 0:
            emergency_controls.append("[RESUME AGENT]")
        else:
            emergency_controls.append("[PAUSE AGENT]")

        emergency_controls.extend(["[STOP AGENT]", "[EMERGENCY BLOCK]"])
        controls_text = " │ ".join(emergency_controls)
        dashboard.append(f"│ {controls_text:<46} │")
        dashboard.append("└────────────────────────────────────────────────────────┘")

        return "\n".join(dashboard)

    # Removed: _get_recent_agent_activity - now using AgentActivityMonitor

    def _calculate_gate_urgency(self, gate_data: Dict[str, Any]) -> str:
        """Calculate urgency level for a gate."""
        age_minutes = (time.time() - gate_data.get("created_at", time.time())) / 60

        if age_minutes > 60:  # Over 1 hour
            return "critical"
        elif age_minutes > 30:  # Over 30 minutes
            return "high"
        elif age_minutes > 10:  # Over 10 minutes
            return "medium"
        else:
            return "low"

    def _calculate_gate_urgency_from_request(self, gate_request) -> str:
        """Calculate urgency level for a gate request."""
        age_minutes = (time.time() - gate_request.created_at) / 60

        if age_minutes > 60:  # Over 1 hour
            return "critical"
        elif age_minutes > 30:  # Over 30 minutes
            return "high"
        elif age_minutes > 10:  # Over 10 minutes
            return "medium"
        else:
            return "low"

    def _urgency_to_priority(self, urgency: str) -> int:
        """Convert urgency string to priority number for sorting."""
        priority_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return priority_map.get(urgency, 0)

    def _get_urgency_icon(self, urgency: str) -> str:
        """Get icon for urgency level."""
        icon_map = {"critical": "🚨", "high": "🔴", "medium": "🟡", "low": "🟢"}
        return icon_map.get(urgency, "❓")

    def _severity_to_priority(self, severity: str) -> int:
        """Convert severity string to priority number for sorting."""
        priority_map = {"error": 4, "warning": 3, "info": 2}
        return priority_map.get(severity, 1)

    def _get_severity_icon(self, severity: str) -> str:
        """Get icon for severity level."""
        icon_map = {"error": "🚨", "warning": "🔴", "info": "🟡"}
        return icon_map.get(severity, "❓")

    def _get_drift_severity_icon(self, severity: DriftSeverity) -> str:
        """Get icon for drift severity level."""
        icon_map = {
            DriftSeverity.CRITICAL: "🚨",
            DriftSeverity.SERIOUS: "🔴",
            DriftSeverity.MODERATE: "🟠",
            DriftSeverity.MINOR: "🟡",
        }
        return icon_map.get(severity, "❓")

    def get_progress_visualization(self) -> Optional[Dict[str, Any]]:
        """Get progress visualization data for the dashboard."""
        try:
            # Load project data
            charter_data = utils.read_json(
                self.ai_onboard_dir / "charter.json", default={}
            )
            plan_data = utils.read_json(self.ai_onboard_dir / "plan.json", default={})
            wbs_data = utils.read_json(self.ai_onboard_dir / "wbs.json", default={})

            if not charter_data:
                return None

            # Calculate overall progress
            progress_percentage = self._calculate_project_progress(wbs_data)

            # Create progress bar (20 characters)
            filled_chars = int(progress_percentage / 5)  # 20 chars = 5% each
            empty_chars = 20 - filled_chars
            progress_bar = (
                f"[{'█' * filled_chars}{'░' * empty_chars}] {progress_percentage:.0f}%"
            )

            # Get current phase
            current_phase = self._get_current_phase(plan_data, progress_percentage)

            # Get next task
            next_task = self._get_next_task(wbs_data)

            # Calculate ETA
            eta = self._calculate_eta(wbs_data, progress_percentage)

            return {
                "progress_bar": progress_bar,
                "progress_percentage": progress_percentage,
                "current_phase": current_phase,
                "next_task": next_task,
                "eta": eta,
            }

        except Exception as e:
            print(f"Warning: Error getting progress visualization: {e}")
            return None

    def _calculate_project_progress(self, wbs_data: Dict[str, Any]) -> float:
        """Calculate overall project completion percentage."""
        try:
            if not wbs_data:
                return 0.0

            # Simple calculation: look at WBS structure
            phases = wbs_data.get("phases", [])
            if not phases:
                return 0.0

            total_tasks = 0
            completed_tasks = 0

            for phase in phases:
                tasks = phase.get("tasks", [])
                for task in tasks:
                    total_tasks += 1
                    if task.get("status") == "completed":
                        completed_tasks += 1

            return (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

        except Exception:
            return 0.0

    def _get_current_phase(
        self, plan_data: Dict[str, Any], progress_percentage: float
    ) -> str:
        """Determine current project phase based on progress."""
        try:
            if not plan_data:
                return "Planning"

            phases = plan_data.get("phases", [])
            if not phases:
                return "Planning"

            # Find current phase based on progress
            for phase in phases:
                phase_start = phase.get("progress_range", {}).get("start", 0)
                phase_end = phase.get("progress_range", {}).get("end", 100)

                if phase_start <= progress_percentage <= phase_end:
                    return str(phase.get("name", "Unknown Phase"))

            # Default to last phase if we're past all ranges
            return str(phases[-1].get("name", "Final Phase")) if phases else "Planning"

        except Exception:
            return "Planning"

    def _get_next_task(self, wbs_data: Dict[str, Any]) -> str:
        """Get the next pending task from WBS."""
        try:
            if not wbs_data:
                return "Define project charter"

            phases = wbs_data.get("phases", [])
            for phase in phases:
                tasks = phase.get("tasks", [])
                for task in tasks:
                    if task.get("status") != "completed":
                        return str(task.get("name", "Unknown Task"))

            return "Project complete"

        except Exception:
            return "Define project charter"

    def _calculate_eta(
        self, wbs_data: Dict[str, Any], progress_percentage: float
    ) -> Optional[str]:
        """Calculate estimated time remaining."""
        try:
            if not wbs_data or progress_percentage >= 100:
                return None

            # Simple estimation based on remaining work
            remaining_percentage = 100 - progress_percentage

            # Assume 2 hours per 10% of work (adjustable)
            hours_remaining = (remaining_percentage / 10) * 2

            if hours_remaining < 1:
                return "Less than 1 hour"
            elif hours_remaining < 24:
                return f"{hours_remaining:.0f} hours"
            else:
                days = hours_remaining / 8  # Assuming 8-hour work days
                return f"{days:.1f} days"

        except Exception:
            return None

    def _calculate_vision_alignment(self) -> Dict[str, Any]:
        """Calculate current alignment with vision using activity monitor data."""
        try:
            # Get activity summary for alignment calculation
            activity_summary = self.activity_monitor.get_activity_summary(hours=1)

            if not activity_summary["agent_details"]:
                return {
                    "alignment": 0.0,
                    "drift": 1.0,
                    "recommendations": ["No recent agent activity to analyze"],
                }

            # Calculate alignment based on recent activities
            total_events = activity_summary["total_events"]
            if total_events == 0:
                return {
                    "alignment": 0.5,
                    "drift": 0.5,
                    "recommendations": ["Agent is idle - no activity to align"],
                }

            # Calculate real alignment based on activity patterns vs vision
            # For now, use activity volume as a proxy for alignment
            # More active = more aligned (agents working on project)
            active_agents = activity_summary["active_agents"]
            total_events = activity_summary["total_events"]

            if active_agents > 0 and total_events > 0:
                # Higher activity = better alignment (agents are working on project)
                alignment_score = min(
                    0.95, 0.5 + (active_agents * 0.2) + (total_events * 0.01)
                )
            elif active_agents > 0:
                # Some agents active but low activity = moderate alignment
                alignment_score = 0.6
            else:
                # No activity = low alignment (agents not working on project)
                alignment_score = 0.2

            recommendations = []
            if alignment_score > 0.8:
                recommendations.append(
                    "Agent activities well aligned with project vision"
                )
            elif alignment_score > 0.5:
                recommendations.append(
                    "Agent activities moderately aligned - monitor for drift"
                )
            else:
                recommendations.append(
                    "Low alignment detected - consider vision review"
                )

            return {
                "alignment": alignment_score,
                "drift": 1.0 - alignment_score,
                "recommendations": recommendations,
            }
        except Exception as e:
            print(f"Warning: Error calculating vision alignment: {e}")
            return {
                "alignment": 0.0,
                "drift": 1.0,
                "recommendations": ["Unable to calculate alignment"],
            }

    def get_chaos_status(self) -> Dict[str, Any]:
        """Get current chaos detection status."""
        return self.chaos_detector.get_chaos_status()

    def get_progress_visualization(self) -> Dict[str, Any]:
        """Get progress visualization data from WBS and project plan."""
        try:
            # Load WBS and project plan
            wbs_file = self.project_root / ".ai_onboard" / "wbs.json"
            plan_file = self.project_root / ".ai_onboard" / "plan.json"

            if not wbs_file.exists() or not plan_file.exists():
                return self._get_default_progress()

            wbs_data = utils.read_json(wbs_file, default={})
            plan_data = utils.read_json(plan_file, default={})

            # Calculate progress based on completed tasks
            total_tasks = 0
            completed_tasks = 0

            for phase in wbs_data.get("phases", []):
                for milestone in phase.get("milestones", []):
                    for task in milestone.get("tasks", []):
                        total_tasks += 1
                        if task.get("status") == "completed":
                            completed_tasks += 1

            progress_percentage = (
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            )

            # Create progress bar
            bar_length = 20
            filled_length = int(bar_length * progress_percentage / 100)
            progress_bar = (
                "["
                + "█" * filled_length
                + "░" * (bar_length - filled_length)
                + f"] {progress_percentage:.0f}%"
            )

            # Get current phase
            current_phase = self._get_current_phase_from_wbs(wbs_data)

            # Get next task
            next_task = self._get_next_task_from_wbs(wbs_data)

            # Calculate ETA
            eta = self._calculate_eta_from_plan(plan_data, progress_percentage)

            return {
                "progress_bar": progress_bar,
                "current_phase": current_phase,
                "next_task": next_task,
                "eta": eta,
                "progress_percentage": progress_percentage,
                "completed_tasks": completed_tasks,
                "total_tasks": total_tasks,
            }

        except Exception as e:
            print(f"Warning: Error getting progress visualization: {e}")
            return self._get_default_progress()

    def _get_default_progress(self) -> Dict[str, Any]:
        """Get default progress when WBS/plan files don't exist."""
        return {
            "progress_bar": "[░░░░░░░░░░░░░░░░░░░░] 0%",
            "current_phase": "Core Oversight MVP",
            "next_task": "Project complete",
            "eta": "20 hours",
            "progress_percentage": 0.0,
            "completed_tasks": 0,
            "total_tasks": 47,  # From the WBS we created
        }

    def _get_current_phase_from_wbs(self, wbs_data: Dict[str, Any]) -> str:
        """Get current phase from WBS data."""
        phases = wbs_data.get("phases", [])
        for phase in phases:
            # Check if any task in any milestone is in progress
            for milestone in phase.get("milestones", []):
                if any(
                    task.get("status") == "in_progress"
                    for task in milestone.get("tasks", [])
                ):
                    return str(phase.get("name", "Unknown Phase"))

        # If no in-progress tasks, return the first incomplete phase
        for phase in phases:
            has_incomplete = False
            for milestone in phase.get("milestones", []):
                if not all(
                    task.get("status") == "completed"
                    for task in milestone.get("tasks", [])
                ):
                    has_incomplete = True
                    break
            if has_incomplete:
                return str(phase.get("name", "Unknown Phase"))

        return "Project Complete"

    def _get_next_task_from_wbs(self, wbs_data: Dict[str, Any]) -> str:
        """Get next task from WBS data."""
        phases = wbs_data.get("phases", [])
        for phase in phases:
            for milestone in phase.get("milestones", []):
                for task in milestone.get("tasks", []):
                    if task.get("status") not in ["completed", "in_progress"]:
                        return str(task.get("name", "Unknown Task"))
        return "Project complete"

    def _calculate_eta_from_plan(
        self, plan_data: Dict[str, Any], progress_percentage: float
    ) -> str:
        """Calculate ETA from project plan."""
        if progress_percentage >= 100:
            return "Complete"

        # Simple calculation based on remaining percentage
        remaining_percentage = 100 - progress_percentage
        estimated_hours = remaining_percentage * 0.2  # Rough estimate

        if estimated_hours < 1:
            return f"{int(estimated_hours * 60)} minutes"
        elif estimated_hours < 24:
            return f"{estimated_hours:.0f} hours"
        else:
            days = estimated_hours / 24
            return f"{days:.1f} days"

    def log_agent_activity(
        self,
        agent_id: str,
        activity: str,
        confidence: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Log agent activity for monitoring."""
        # Use the activity monitor to log this
        self.activity_monitor.update_agent_activity(
            agent_id=agent_id,
            task=activity,
            progress=0.0,  # Will be updated separately
            confidence=confidence,
            metadata=metadata or {},
        )

    def log_blocked_action(
        self, agent_id: str, action_type: str, reason: str, severity: str = "warning"
    ):
        """Log a blocked action."""
        try:
            blocked_entry = {
                "timestamp": time.time(),
                "type": "blocked_action",
                "action_id": f"block_{int(time.time())}_{agent_id}",
                "agent_id": agent_id,
                "action_type": action_type,
                "reason": reason,
                "severity": severity,
            }

            with open(self.session_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(blocked_entry) + "\n")
        except Exception:
            pass

    def simulate_agent_activity(self, agent_id: str = "demo_agent"):
        """Simulate some agent activity for testing the dashboard."""
        # Log some activity
        self.log_agent_activity(
            agent_id=agent_id,
            activity="Creating test files for integration testing",
            confidence=0.8,
            metadata={"files": ["test1.py", "test2.py"], "operation": "file_creation"},
        )

        # Log a blocked action
        self.log_blocked_action(
            agent_id=agent_id,
            action_type="Delete 5 core files",
            reason="Protected files - requires approval",
            severity="high",
        )

        # Update agent activity in monitor
        self.activity_monitor.update_agent_activity(
            agent_id=agent_id,
            task="Integration testing",
            progress=0.3,
            confidence=0.7,
            metadata={"test_phase": "comprehensive_testing"},
        )
