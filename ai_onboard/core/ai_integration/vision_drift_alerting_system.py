"""
Vision Drift Alerting System - Detects and alerts on agent deviation from project vision.

This module provides sophisticated vision alignment monitoring that:
- Analyzes agent activities against project charter and WBS
- Identifies specific drift patterns and off-track work
- Provides detailed alerts with corrective suggestions
- Integrates with dashboard for real-time visibility
"""

import json
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..base import utils
from .agent_activity_monitor import AgentActivityMonitor


class DriftType(Enum):
    """Types of vision drift that can be detected."""

    SCOPE_CREEP = "scope_creep"  # Working on unapproved features
    OFF_TRACK_TASKS = "off_track_tasks"  # Tasks not in current WBS phase
    UNAUTHORIZED_CHANGES = "unauthorized_changes"  # Changing protected areas
    MISSION_DEVIATION = "mission_deviation"  # Work not aligned with charter mission
    DEPENDENCY_BLOAT = "dependency_bloat"  # Adding unnecessary dependencies
    ARCHITECTURE_DRIFT = "architecture_drift"  # Deviating from approved architecture


class DriftSeverity(Enum):
    """Severity levels for vision drift."""

    MINOR = "minor"  # Slight deviation, monitor only
    MODERATE = "moderate"  # Concerning drift, alert user
    SERIOUS = "serious"  # Significant deviation, require approval
    CRITICAL = "critical"  # Mission-critical drift, immediate intervention


@dataclass
class VisionDriftAlert:
    """Represents a detected vision drift alert."""

    alert_id: str
    drift_type: DriftType
    severity: DriftSeverity
    agent_id: str
    description: str
    detected_at: float
    confidence: float

    # Detailed analysis
    current_activity: str
    expected_activity: str
    drift_reason: str
    corrective_action: str

    # Evidence
    evidence: Dict[str, Any] = field(default_factory=dict)

    # Resolution
    resolved: bool = False
    resolved_at: Optional[float] = None
    resolution_action: Optional[str] = None

    # Escalation tracking
    escalation_level: int = 0
    last_escalation: Optional[float] = None


@dataclass
class VisionAlignmentMetrics:
    """Metrics for tracking vision alignment."""

    agent_id: str
    time_window: float  # seconds

    # Alignment scores (0.0 = no alignment, 1.0 = perfect alignment)
    charter_alignment: float = 0.0
    wbs_alignment: float = 0.0
    scope_alignment: float = 0.0
    mission_alignment: float = 0.0

    # Activity breakdown
    on_track_activities: int = 0
    off_track_activities: int = 0
    total_activities: int = 0

    # Drift detection
    active_drifts: int = 0
    resolved_drifts: int = 0
    drift_score: float = 0.0

    # Risk assessment
    drift_risk_level: str = "low"
    requires_attention: bool = False


class VisionDriftAlertingSystem:
    """
    Advanced vision drift alerting system for AI agent oversight.

    Monitors agent activities against project charter and WBS to detect:
    - Scope creep and unauthorized features
    - Off-track task execution
    - Mission deviation
    - Architecture drift
    - Dependency bloat
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ai_onboard_dir = project_root / ".ai_onboard"

        # Core systems
        self.activity_monitor = AgentActivityMonitor(project_root)

        # Alert state
        self.active_alerts: Dict[str, VisionDriftAlert] = {}
        self.resolved_alerts: List[VisionDriftAlert] = []
        self.agent_metrics: Dict[str, VisionAlignmentMetrics] = {}

        # Configuration
        self.alert_thresholds = self._load_alert_thresholds()
        self.scan_interval = 30.0  # seconds
        self.max_alerts_per_agent = 10

        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Ensure directories exist
        self.ai_onboard_dir.mkdir(exist_ok=True)

        # Load existing alerts
        self._load_alerts()

        # Start monitoring
        self.start_monitoring()

    def start_monitoring(self) -> None:
        """Start vision drift monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        print("🎯 Vision Drift Alerting System started")

    def stop_monitoring(self) -> None:
        """Stop vision drift monitoring."""
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)

        self._save_alerts()
        print("⏹️ Vision Drift Alerting System stopped")

    def get_drift_status(self) -> Dict[str, Any]:
        """Get current vision drift status."""
        return {
            "monitoring_active": self.monitoring_active,
            "active_alerts": len(self.active_alerts),
            "resolved_alerts": len(self.resolved_alerts),
            "agents_monitored": len(self.agent_metrics),
            "drift_thresholds": self.alert_thresholds,
            "uptime": time.time() - (self._get_start_time() or time.time()),
        }

    def get_active_alerts(
        self, agent_id: Optional[str] = None
    ) -> List[VisionDriftAlert]:
        """Get active drift alerts, optionally filtered by agent."""
        alerts = list(self.active_alerts.values())
        if agent_id:
            alerts = [a for a in alerts if a.agent_id == agent_id]

        # Sort by severity and time (most severe and recent first)
        return sorted(
            alerts,
            key=lambda a: (self._severity_priority(a.severity), a.detected_at),
            reverse=True,
        )

    def get_agent_alignment_score(self, agent_id: str) -> float:
        """Get overall vision alignment score for an agent (0.0-1.0)."""
        if agent_id not in self.agent_metrics:
            return 0.5  # Neutral if no data

        metrics = self.agent_metrics[agent_id]

        # Weighted average of alignment scores
        return (
            metrics.charter_alignment * 0.4
            + metrics.wbs_alignment * 0.3
            + metrics.scope_alignment * 0.2
            + metrics.mission_alignment * 0.1
        )

    def detect_drift_for_agent(self, agent_id: str) -> List[VisionDriftAlert]:
        """Detect vision drift for a specific agent."""
        alerts: List[VisionDriftAlert] = []

        # Update alignment metrics
        self._update_agent_metrics(agent_id)

        # Check for various drift patterns
        alerts.extend(self._detect_scope_creep(agent_id))
        alerts.extend(self._detect_off_track_tasks(agent_id))
        alerts.extend(self._detect_mission_deviation(agent_id))
        alerts.extend(self._detect_architecture_drift(agent_id))
        alerts.extend(self._detect_dependency_bloat(agent_id))

        # Add new alerts to active list
        for alert in alerts:
            if alert.alert_id not in self.active_alerts:
                self.active_alerts[alert.alert_id] = alert

        # Limit alerts per agent
        self._enforce_alert_limits(agent_id)

        return alerts

    def resolve_alert(self, alert_id: str, resolution_action: str) -> bool:
        """Mark an alert as resolved."""
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.resolved = True
        alert.resolved_at = time.time()
        alert.resolution_action = resolution_action

        # Move to resolved list
        self.resolved_alerts.append(alert)
        del self.active_alerts[alert_id]

        # Keep only recent resolved alerts
        if len(self.resolved_alerts) > 100:
            self.resolved_alerts = self.resolved_alerts[-100:]

        return True

    def escalate_alert(self, alert_id: str) -> bool:
        """Escalate an alert to higher severity."""
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]

        # Increase escalation level
        alert.escalation_level += 1
        alert.last_escalation = time.time()

        # Potentially increase severity
        if alert.escalation_level >= 3 and alert.severity == DriftSeverity.MINOR:
            alert.severity = DriftSeverity.MODERATE
        elif alert.escalation_level >= 5 and alert.severity in [
            DriftSeverity.MINOR,
            DriftSeverity.MODERATE,
        ]:
            alert.severity = DriftSeverity.SERIOUS

        return True

    def _monitoring_loop(self) -> None:
        """Main vision drift monitoring loop."""
        while self.monitoring_active:
            try:
                # Update metrics for all active agents
                self._update_all_agent_metrics()

                # Check for drift in each agent
                for agent_id in list(self.agent_metrics.keys()):
                    drift_alerts = self.detect_drift_for_agent(agent_id)

                    # Log significant alerts
                    for alert in drift_alerts:
                        if alert.severity in [
                            DriftSeverity.SERIOUS,
                            DriftSeverity.CRITICAL,
                        ]:
                            self._log_drift_alert(alert)

                    # Auto-escalate unresolved alerts
                    self._auto_escalate_alerts(agent_id)

                time.sleep(self.scan_interval)

            except Exception as e:
                print(f"Warning: Vision drift monitoring error: {e}")
                time.sleep(self.scan_interval)

    def _update_all_agent_metrics(self) -> None:
        """Update alignment metrics for all monitored agents."""
        # Get recent activity summary
        activity_summary = self.activity_monitor.get_activity_summary(hours=1)

        for agent_id in activity_summary["agent_details"]:
            self._update_agent_metrics(agent_id)

    def _update_agent_metrics(self, agent_id: str) -> None:
        """Update vision alignment metrics for a specific agent."""
        current_time = time.time()
        window_seconds = 3600.0  # 1 hour window

        # Get recent activities
        recent_activities = self._get_agent_activities_window(agent_id, window_seconds)

        if not recent_activities:
            return

        # Calculate alignment scores
        charter_alignment = self._calculate_charter_alignment(
            agent_id, recent_activities
        )
        wbs_alignment = self._calculate_wbs_alignment(agent_id, recent_activities)
        scope_alignment = self._calculate_scope_alignment(agent_id, recent_activities)
        mission_alignment = self._calculate_mission_alignment(
            agent_id, recent_activities
        )

        # Activity counts
        on_track, off_track = self._analyze_activity_alignment(recent_activities)
        total_activities = len(recent_activities)

        # Drift score (0.0 = perfect alignment, 1.0 = maximum drift)
        drift_score = 1.0 - (
            charter_alignment * 0.4
            + wbs_alignment * 0.3
            + scope_alignment * 0.2
            + mission_alignment * 0.1
        )

        # Update metrics
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = VisionAlignmentMetrics(
                agent_id=agent_id, time_window=window_seconds
            )

        metrics = self.agent_metrics[agent_id]
        metrics.charter_alignment = charter_alignment
        metrics.wbs_alignment = wbs_alignment
        metrics.scope_alignment = scope_alignment
        metrics.mission_alignment = mission_alignment
        metrics.on_track_activities = on_track
        metrics.off_track_activities = off_track
        metrics.total_activities = total_activities
        metrics.drift_score = drift_score
        metrics.active_drifts = len(
            [a for a in self.active_alerts.values() if a.agent_id == agent_id]
        )

        # Determine risk level
        if drift_score > 0.7:
            metrics.drift_risk_level = "critical"
        elif drift_score > 0.5:
            metrics.drift_risk_level = "high"
        elif drift_score > 0.3:
            metrics.drift_risk_level = "medium"
        else:
            metrics.drift_risk_level = "low"

        metrics.requires_attention = drift_score > 0.4 or metrics.active_drifts > 0

    def _get_agent_activities_window(
        self, agent_id: str, window_seconds: float
    ) -> List:
        """Get recent activities for an agent within time window."""
        cutoff_time = time.time() - window_seconds

        return [
            event
            for event in self.activity_monitor.activity_history
            if event.agent_id == agent_id and event.timestamp > cutoff_time
        ]

    def _calculate_charter_alignment(self, agent_id: str, activities: List) -> float:
        """Calculate alignment with project charter."""
        try:
            charter_data = utils.read_json(
                self.ai_onboard_dir / "charter.json", default={}
            )

            if not charter_data:
                return 0.5

            # Extract key charter elements
            vision = charter_data.get("vision", {})
            primary_goal = vision.get("primary_goal", "").lower()
            mission = charter_data.get("mission", "").lower()
            core_principles = [
                p.lower() for p in charter_data.get("core_principles", [])
            ]

            if not any([primary_goal, mission, core_principles]):
                return 0.5

            aligned_count = 0
            total_count = len(activities)

            for activity in activities:
                activity_desc = activity.description.lower()

                # Check alignment with charter elements
                alignment_found = False

                if primary_goal and any(
                    word in activity_desc for word in primary_goal.split()
                ):
                    alignment_found = True

                if mission and any(word in activity_desc for word in mission.split()):
                    alignment_found = True

                if any(
                    any(cp_word in activity_desc for cp_word in cp.split())
                    for cp in core_principles
                ):
                    alignment_found = True

                if alignment_found:
                    aligned_count += 1

            return aligned_count / total_count if total_count > 0 else 0.5

        except Exception:
            return 0.5

    def _calculate_wbs_alignment(self, agent_id: str, activities: List) -> float:
        """Calculate alignment with current WBS phase."""
        try:
            wbs_data = utils.read_json(self.ai_onboard_dir / "wbs.json", default={})

            if not wbs_data:
                return 0.5

            # Find current phase
            current_phase = None
            for phase in wbs_data.get("phases", []):
                if phase.get("status") == "in_progress":
                    current_phase = phase
                    break

            if not current_phase:
                return 0.5

            # Get current phase tasks
            current_tasks = [
                task.get("name", "").lower()
                for task in current_phase.get("tasks", [])
                if task.get("status") == "pending"
                or task.get("status") == "in_progress"
            ]

            if not current_tasks:
                return 0.5

            aligned_count = 0
            total_count = len(activities)

            for activity in activities:
                activity_desc = activity.description.lower()

                # Check if activity aligns with current phase tasks
                if any(
                    any(task_word in activity_desc for task_word in task.split())
                    for task in current_tasks
                ):
                    aligned_count += 1

            return aligned_count / total_count if total_count > 0 else 0.5

        except Exception:
            return 0.5

    def _calculate_scope_alignment(self, agent_id: str, activities: List) -> float:
        """Calculate alignment with approved project scope."""
        try:
            plan_data = utils.read_json(self.ai_onboard_dir / "plan.json", default={})

            if not plan_data:
                return 0.5

            # Get approved features/deliverables
            approved_items = []
            for phase in plan_data.get("phases", []):
                approved_items.extend(
                    [item.lower() for item in phase.get("deliverables", [])]
                )

            if not approved_items:
                return 0.5

            aligned_count = 0
            total_count = len(activities)

            for activity in activities:
                activity_desc = activity.description.lower()

                # Check alignment with approved scope
                if any(
                    any(item_word in activity_desc for item_word in item.split())
                    for item in approved_items
                ):
                    aligned_count += 1

            return aligned_count / total_count if total_count > 0 else 0.5

        except Exception:
            return 0.5

    def _calculate_mission_alignment(self, agent_id: str, activities: List) -> float:
        """Calculate alignment with core mission."""
        # This is a simplified version - in practice would use NLP/semantic analysis
        charter_alignment = self._calculate_charter_alignment(agent_id, activities)
        return charter_alignment  # For now, use charter alignment as proxy

    def _analyze_activity_alignment(self, activities: List) -> Tuple[int, int]:
        """Analyze activities and return (on_track_count, off_track_count)."""
        on_track = 0
        off_track = 0

        for activity in activities:
            # Simplified analysis - check for keywords indicating alignment
            desc = activity.description.lower()

            # On-track indicators
            on_track_keywords = [
                "dashboard",
                "gate",
                "oversight",
                "monitoring",
                "control",
                "vision",
                "alignment",
                "chaos",
                "detection",
                "alert",
                "enforcement",
                "block",
                "pause",
                "stop",
                "emergency",
            ]

            # Off-track indicators (things that suggest scope creep)
            off_track_keywords = [
                "game",
                "social",
                "media",
                "blog",
                "cms",
                "ecommerce",
                "mobile",
                "ios",
                "android",
                "desktop",
                "web",
                "api",
            ]

            if any(keyword in desc for keyword in on_track_keywords):
                on_track += 1
            elif any(keyword in desc for keyword in off_track_keywords):
                off_track += 1
            else:
                # Neutral - count as on-track for now
                on_track += 1

        return on_track, off_track

    def _detect_scope_creep(self, agent_id: str) -> List[VisionDriftAlert]:
        """Detect when agent is working on unapproved features."""
        alerts: List[VisionDriftAlert] = []
        metrics = self.agent_metrics.get(agent_id)

        if not metrics or metrics.scope_alignment > 0.7:
            return alerts

        # Check for activities that suggest scope creep
        recent_activities = self._get_agent_activities_window(
            agent_id, 1800
        )  # 30 minutes

        for activity in recent_activities[-5:]:  # Check last 5 activities
            desc = activity.description.lower()

            # Look for patterns that indicate scope creep
            scope_creep_indicators = [
                "new feature",
                "additional functionality",
                "extra",
                "bonus",
                "enhancement",
                "improvement",
                "extension",
                "module",
            ]

            if any(indicator in desc for indicator in scope_creep_indicators):
                alert = VisionDriftAlert(
                    alert_id=f"scope_creep_{agent_id}_{int(time.time())}_{len(alerts)}",
                    drift_type=DriftType.SCOPE_CREEP,
                    severity=DriftSeverity.MODERATE,
                    agent_id=agent_id,
                    description="Agent appears to be implementing unapproved features",
                    detected_at=time.time(),
                    confidence=0.6,
                    current_activity=activity.description,
                    expected_activity="Focus on approved WBS deliverables",
                    drift_reason="Activity suggests implementation of features outside approved scope",
                    corrective_action="Review and approve feature before continuing",
                    evidence={
                        "activity": activity.description,
                        "scope_alignment": metrics.scope_alignment,
                        "timestamp": activity.timestamp,
                    },
                )
                alerts.append(alert)
                break  # Only one alert per detection cycle

        return alerts

    def _detect_off_track_tasks(self, agent_id: str) -> List[VisionDriftAlert]:
        """Detect when agent is working on tasks not in current WBS phase."""
        alerts: List[VisionDriftAlert] = []
        metrics = self.agent_metrics.get(agent_id)

        if not metrics or metrics.wbs_alignment > 0.6:
            return alerts

        recent_activities = self._get_agent_activities_window(agent_id, 1800)

        for activity in recent_activities[-3:]:
            desc = activity.description.lower()

            # Check if this activity aligns with current WBS phase
            wbs_alignment = self._calculate_wbs_alignment(agent_id, [activity])

            if wbs_alignment < 0.3:  # Low alignment
                alert = VisionDriftAlert(
                    alert_id=f"off_track_{agent_id}_{int(time.time())}_{len(alerts)}",
                    drift_type=DriftType.OFF_TRACK_TASKS,
                    severity=DriftSeverity.SERIOUS,
                    agent_id=agent_id,
                    description="Agent working on tasks outside current WBS phase",
                    detected_at=time.time(),
                    confidence=0.8,
                    current_activity=activity.description,
                    expected_activity="Complete current phase deliverables first",
                    drift_reason=f"Activity not aligned with current WBS phase (alignment: {wbs_alignment:.1%})",
                    corrective_action="Redirect agent to current phase tasks or update WBS",
                    evidence={
                        "activity": activity.description,
                        "wbs_alignment": wbs_alignment,
                        "current_phase_alignment": metrics.wbs_alignment,
                        "timestamp": activity.timestamp,
                    },
                )
                alerts.append(alert)
                break

        return alerts

    def _detect_mission_deviation(self, agent_id: str) -> List[VisionDriftAlert]:
        """Detect when agent activities deviate from core mission."""
        alerts: List[VisionDriftAlert] = []
        metrics = self.agent_metrics.get(agent_id)

        if not metrics or metrics.mission_alignment > 0.7:
            return alerts

        recent_activities = self._get_agent_activities_window(agent_id, 1800)

        # Check for pattern of low mission alignment
        low_alignment_count = sum(
            1
            for activity in recent_activities
            if self._calculate_mission_alignment(agent_id, [activity]) < 0.4
        )

        if low_alignment_count >= 3:  # 3+ activities with low alignment
            alert = VisionDriftAlert(
                alert_id=f"mission_drift_{agent_id}_{int(time.time())}",
                drift_type=DriftType.MISSION_DEVIATION,
                severity=DriftSeverity.CRITICAL,
                agent_id=agent_id,
                description="Agent activities consistently deviate from project mission",
                detected_at=time.time(),
                confidence=0.9,
                current_activity=f"{low_alignment_count} recent activities misaligned",
                expected_activity="Activities aligned with agent oversight mission",
                drift_reason=f"Multiple activities ({low_alignment_count}) show low mission alignment",
                corrective_action="Immediate intervention required - review agent direction",
                evidence={
                    "low_alignment_activities": low_alignment_count,
                    "mission_alignment_score": metrics.mission_alignment,
                    "total_activities": len(recent_activities),
                },
            )
            alerts.append(alert)

        return alerts

    def _detect_architecture_drift(self, agent_id: str) -> List[VisionDriftAlert]:
        """Detect when agent deviates from approved architecture."""
        alerts: List[VisionDriftAlert] = []
        # This would analyze code changes against approved architecture patterns
        # For now, return empty - would need more sophisticated analysis
        return alerts

    def _detect_dependency_bloat(self, agent_id: str) -> List[VisionDriftAlert]:
        """Detect when agent is adding unnecessary dependencies."""
        alerts: List[VisionDriftAlert] = []
        # This would monitor dependency additions and check against approval
        # For now, return empty - would need integration with dependency management
        return alerts

    def _severity_priority(self, severity: DriftSeverity) -> int:
        """Get priority value for severity sorting."""
        priorities = {
            DriftSeverity.CRITICAL: 4,
            DriftSeverity.SERIOUS: 3,
            DriftSeverity.MODERATE: 2,
            DriftSeverity.MINOR: 1,
        }
        return priorities.get(severity, 0)

    def _enforce_alert_limits(self, agent_id: str) -> None:
        """Ensure we don't have too many active alerts per agent."""
        agent_alerts = [
            (alert_id, alert)
            for alert_id, alert in self.active_alerts.items()
            if alert.agent_id == agent_id
        ]

        if len(agent_alerts) <= self.max_alerts_per_agent:
            return

        # Sort by severity and keep only the most important ones
        agent_alerts.sort(
            key=lambda x: (self._severity_priority(x[1].severity), x[1].detected_at),
            reverse=True,
        )

        # Remove excess alerts
        excess_alerts = agent_alerts[self.max_alerts_per_agent :]
        for alert_id, _ in excess_alerts:
            del self.active_alerts[alert_id]

    def _auto_escalate_alerts(self, agent_id: str) -> None:
        """Auto-escalate unresolved alerts that have been active too long."""
        current_time = time.time()

        for alert_id, alert in list(self.active_alerts.items()):
            if alert.agent_id != agent_id:
                continue

            age_hours = (current_time - alert.detected_at) / 3600

            # Escalate based on age and current severity
            if (
                (alert.severity == DriftSeverity.MINOR and age_hours > 2)
                or (alert.severity == DriftSeverity.MODERATE and age_hours > 4)
                or (alert.severity == DriftSeverity.SERIOUS and age_hours > 6)
            ):
                self.escalate_alert(alert_id)

    def _load_alert_thresholds(self) -> Dict[str, float]:
        """Load vision drift alert thresholds."""
        return {
            "charter_alignment_threshold": 0.7,
            "wbs_alignment_threshold": 0.6,
            "scope_alignment_threshold": 0.7,
            "mission_alignment_threshold": 0.8,
            "max_alerts_per_agent": 10,
            "auto_escalation_hours": 2,
        }

    def _load_alerts(self) -> None:
        """Load existing alerts from storage."""
        try:
            alerts_file = self.ai_onboard_dir / "vision_drift_alerts.json"
            if alerts_file.exists():
                alerts_data = utils.read_json(alerts_file)

                for alert_data in alerts_data.get("active", []):
                    alert = VisionDriftAlert(
                        alert_id=alert_data["alert_id"],
                        drift_type=DriftType(alert_data["drift_type"]),
                        severity=DriftSeverity(alert_data["severity"]),
                        agent_id=alert_data["agent_id"],
                        description=alert_data["description"],
                        detected_at=alert_data["detected_at"],
                        confidence=alert_data["confidence"],
                        current_activity=alert_data["current_activity"],
                        expected_activity=alert_data["expected_activity"],
                        drift_reason=alert_data["drift_reason"],
                        corrective_action=alert_data["corrective_action"],
                        evidence=alert_data.get("evidence", {}),
                        resolved=alert_data.get("resolved", False),
                        resolved_at=alert_data.get("resolved_at"),
                        resolution_action=alert_data.get("resolution_action"),
                        escalation_level=alert_data.get("escalation_level", 0),
                        last_escalation=alert_data.get("last_escalation"),
                    )
                    self.active_alerts[alert.alert_id] = alert

                for alert_data in alerts_data.get("resolved", []):
                    alert = VisionDriftAlert(
                        alert_id=alert_data["alert_id"],
                        drift_type=DriftType(alert_data["drift_type"]),
                        severity=DriftSeverity(alert_data["severity"]),
                        agent_id=alert_data["agent_id"],
                        description=alert_data["description"],
                        detected_at=alert_data["detected_at"],
                        confidence=alert_data["confidence"],
                        current_activity=alert_data["current_activity"],
                        expected_activity=alert_data["expected_activity"],
                        drift_reason=alert_data["drift_reason"],
                        corrective_action=alert_data["corrective_action"],
                        evidence=alert_data.get("evidence", {}),
                        resolved=True,
                        resolved_at=alert_data.get("resolved_at"),
                        resolution_action=alert_data.get("resolution_action"),
                        escalation_level=alert_data.get("escalation_level", 0),
                        last_escalation=alert_data.get("last_escalation"),
                    )
                    self.resolved_alerts.append(alert)

        except Exception as e:
            print(f"Warning: Could not load vision drift alerts: {e}")

    def _save_alerts(self) -> None:
        """Save alerts to storage."""
        try:
            alerts_data: Dict[str, List[Dict[str, Any]]] = {
                "active": [],
                "resolved": [],
            }

            for alert in self.active_alerts.values():
                alert_dict = {
                    "alert_id": alert.alert_id,
                    "drift_type": alert.drift_type.value,
                    "severity": alert.severity.value,
                    "agent_id": alert.agent_id,
                    "description": alert.description,
                    "detected_at": alert.detected_at,
                    "confidence": alert.confidence,
                    "current_activity": alert.current_activity,
                    "expected_activity": alert.expected_activity,
                    "drift_reason": alert.drift_reason,
                    "corrective_action": alert.corrective_action,
                    "evidence": alert.evidence,
                    "resolved": alert.resolved,
                    "resolved_at": alert.resolved_at,
                    "resolution_action": alert.resolution_action,
                    "escalation_level": alert.escalation_level,
                    "last_escalation": alert.last_escalation,
                }
                alerts_data["active"].append(alert_dict)

            for alert in self.resolved_alerts[-50:]:  # Keep last 50 resolved
                alert_dict = {
                    "alert_id": alert.alert_id,
                    "drift_type": alert.drift_type.value,
                    "severity": alert.severity.value,
                    "agent_id": alert.agent_id,
                    "description": alert.description,
                    "detected_at": alert.detected_at,
                    "confidence": alert.confidence,
                    "current_activity": alert.current_activity,
                    "expected_activity": alert.expected_activity,
                    "drift_reason": alert.drift_reason,
                    "corrective_action": alert.corrective_action,
                    "evidence": alert.evidence,
                    "resolved": alert.resolved,
                    "resolved_at": alert.resolved_at,
                    "resolution_action": alert.resolution_action,
                    "escalation_level": alert.escalation_level,
                    "last_escalation": alert.last_escalation,
                }
                alerts_data["resolved"].append(alert_dict)

            alerts_file = self.ai_onboard_dir / "vision_drift_alerts.json"
            utils.write_json(alerts_file, alerts_data)

        except Exception as e:
            print(f"Warning: Could not save vision drift alerts: {e}")

    def _log_drift_alert(self, alert: VisionDriftAlert) -> None:
        """Log a significant drift alert."""
        try:
            log_entry = {
                "timestamp": time.time(),
                "type": "vision_drift_alert",
                "alert_id": alert.alert_id,
                "drift_type": alert.drift_type.value,
                "severity": alert.severity.value,
                "agent_id": alert.agent_id,
                "description": alert.description,
                "confidence": alert.confidence,
                "drift_reason": alert.drift_reason,
                "corrective_action": alert.corrective_action,
            }

            session_log_path = self.ai_onboard_dir / "session_log.jsonl"
            with open(session_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            print(f"Warning: Failed to log drift alert: {e}")

    def _get_start_time(self) -> Optional[float]:
        """Get approximate start time from oldest alert."""
        all_alerts = list(self.active_alerts.values()) + self.resolved_alerts
        if not all_alerts:
            return None

        oldest_alert = min(all_alerts, key=lambda a: a.detected_at)
        return oldest_alert.detected_at


def get_vision_drift_alerting_system(project_root: Path) -> VisionDriftAlertingSystem:
    """Get or create vision drift alerting system for the project."""
    return VisionDriftAlertingSystem(project_root)
