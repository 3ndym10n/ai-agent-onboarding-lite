"""
Chaos Detection System - Detects and prevents chaotic AI agent behavior.

This module identifies when AI agents are exhibiting chaotic patterns like:
- Creating excessive files or bloat
- Making rapid, uncoordinated changes
- Drifting from project vision
- Creating technical debt
- Working on unrelated tasks

The system provides early warning and automatic intervention.
"""

import json
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base import utils
from .agent_activity_monitor import AgentActivityMonitor


class ChaosType(Enum):
    """Types of chaotic behavior that can be detected."""

    FILE_BLOAT = "file_bloat"  # Too many files created rapidly
    RAPID_CHANGES = "rapid_changes"  # Too many changes in short time
    VISION_DRIFT = "vision_drift"  # Actions not aligned with vision
    TECHNICAL_DEBT = "technical_debt"  # Creating complexity without benefit
    UNRELATED_WORK = "unrelated_work"  # Working on tasks outside scope
    REPETITIVE_FAILURES = "repetitive_failures"  # Repeated failed operations


class ChaosSeverity(Enum):
    """Severity levels for chaotic behavior."""

    LOW = "low"  # Minor issues, just monitor
    MEDIUM = "medium"  # Concerning patterns, alert user
    HIGH = "high"  # Serious chaos, trigger gates
    CRITICAL = "critical"  # Immediate intervention needed


@dataclass
class ChaosEvent:
    """Represents a detected chaotic behavior event."""

    event_id: str
    chaos_type: ChaosType
    severity: ChaosSeverity
    agent_id: str
    description: str
    confidence: float
    detected_at: float
    evidence: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[float] = None
    resolution: Optional[str] = None


@dataclass
class ChaosMetrics:
    """Current chaos detection metrics."""

    agent_id: str
    time_window: float  # seconds

    # File creation patterns
    files_created_recently: int = 0
    files_created_rate: float = 0.0  # files per minute

    # Change patterns
    changes_made_recently: int = 0
    changes_rate: float = 0.0  # changes per minute

    # Vision alignment
    vision_alignment_score: float = 0.0
    vision_drift_detected: bool = False

    # Technical debt indicators
    complexity_increase: float = 0.0
    dependency_additions: int = 0

    # Failure patterns
    recent_failures: int = 0
    failure_rate: float = 0.0

    # Overall chaos score
    chaos_score: float = 0.0
    risk_level: str = "low"


class ChaosDetectionSystem:
    """
    Real-time chaos detection system for AI agent oversight.

    Monitors agent behavior patterns and detects when agents are:
    - Creating excessive files or bloat
    - Making rapid, uncoordinated changes
    - Drifting from project vision
    - Creating technical debt
    - Working on unrelated tasks
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ai_onboard_dir = project_root / ".ai_onboard"

        # Core systems
        self.activity_monitor = AgentActivityMonitor(project_root)

        # Chaos detection state
        self.chaos_events: List[ChaosEvent] = []
        self.agent_metrics: Dict[str, ChaosMetrics] = {}
        self.detection_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )

        # Configuration
        self.scan_interval = 15.0  # seconds
        self.metrics_window = 300.0  # 5 minutes for metrics calculation
        self.chaos_thresholds = self._load_chaos_thresholds()

        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Ensure directories exist
        self.ai_onboard_dir.mkdir(exist_ok=True)

        # Load existing chaos events
        self._load_chaos_events()

        # Start monitoring
        self.start_monitoring()

    def start_monitoring(self) -> None:
        """Start chaos detection monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        print("🔍 Chaos Detection System started")

    def stop_monitoring(self) -> None:
        """Stop chaos detection monitoring."""
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)

        self._save_chaos_events()
        print("⏹️ Chaos Detection System stopped")

    def get_chaos_status(self) -> Dict[str, Any]:
        """Get current chaos detection status."""
        return {
            "monitoring_active": self.monitoring_active,
            "total_chaos_events": len(self.chaos_events),
            "active_chaos_events": len(
                [e for e in self.chaos_events if not e.resolved]
            ),
            "agents_monitored": len(self.agent_metrics),
            "detection_uptime": time.time() - (self._get_start_time() or time.time()),
            "chaos_thresholds": self.chaos_thresholds,
        }

    def get_agent_chaos_score(self, agent_id: str) -> float:
        """Get current chaos score for an agent."""
        if agent_id not in self.agent_metrics:
            return 0.0

        return self.agent_metrics[agent_id].chaos_score

    def get_recent_chaos_events(self, limit: int = 10) -> List[ChaosEvent]:
        """Get recent chaos events."""
        # Sort by detection time (most recent first)
        sorted_events = sorted(
            self.chaos_events, key=lambda e: e.detected_at, reverse=True
        )

        return sorted_events[:limit]

    def detect_chaos_for_agent(self, agent_id: str) -> List[ChaosEvent]:
        """Detect chaos patterns for a specific agent."""
        events: List[ChaosEvent] = []

        # Update metrics for this agent
        self._update_agent_metrics(agent_id)

        # Check for various chaos patterns
        events.extend(self._detect_file_bloat(agent_id))
        events.extend(self._detect_rapid_changes(agent_id))
        events.extend(self._detect_vision_drift(agent_id))
        events.extend(self._detect_technical_debt(agent_id))
        events.extend(self._detect_unrelated_work(agent_id))
        events.extend(self._detect_repetitive_failures(agent_id))

        # Save new events
        for event in events:
            self.chaos_events.append(event)

        # Keep only recent events (last 1000)
        if len(self.chaos_events) > 1000:
            self.chaos_events = self.chaos_events[-1000:]

        return events

    def _monitoring_loop(self) -> None:
        """Main chaos detection monitoring loop."""
        while self.monitoring_active:
            try:
                # Update metrics for all active agents
                self._update_all_agent_metrics()

                # Detect chaos for each agent
                for agent_id in list(self.agent_metrics.keys()):
                    chaos_events = self.detect_chaos_for_agent(agent_id)

                    # Log significant chaos events
                    for event in chaos_events:
                        if event.severity in [
                            ChaosSeverity.HIGH,
                            ChaosSeverity.CRITICAL,
                        ]:
                            self._log_chaos_event(event)

                time.sleep(self.scan_interval)

            except Exception as e:
                print(f"Warning: Chaos detection error: {e}")
                time.sleep(self.scan_interval)

    def _update_all_agent_metrics(self) -> None:
        """Update chaos metrics for all monitored agents."""
        # Get activity summary for chaos calculation
        activity_summary = self.activity_monitor.get_activity_summary(hours=1)

        for agent_id, agent_data in activity_summary["agent_details"].items():
            self._update_agent_metrics(agent_id)

    def _update_agent_metrics(self, agent_id: str) -> None:
        """Update chaos metrics for a specific agent."""
        current_time = time.time()

        # Get recent activity for this agent
        recent_activity = self._get_agent_activity_window(agent_id, self.metrics_window)

        # Calculate metrics
        files_created = len(
            [a for a in recent_activity if a.activity_type == "file_created"]
        )
        changes_made = len(
            [
                a
                for a in recent_activity
                if a.activity_type in ["file_modified", "file_created", "file_deleted"]
            ]
        )

        # Calculate rates (per minute)
        time_span = max(1, self.metrics_window / 60)  # avoid division by zero
        files_rate = files_created / time_span
        changes_rate = changes_made / time_span

        # Calculate vision alignment (simplified)
        vision_alignment = self._calculate_vision_alignment(agent_id, recent_activity)

        # Calculate chaos score
        chaos_score = self._calculate_chaos_score(
            files_rate, changes_rate, vision_alignment, recent_activity
        )

        # Update metrics
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = ChaosMetrics(
                agent_id=agent_id, time_window=self.metrics_window
            )

        metrics = self.agent_metrics[agent_id]
        metrics.files_created_recently = files_created
        metrics.files_created_rate = files_rate
        metrics.changes_made_recently = changes_made
        metrics.changes_rate = changes_rate
        metrics.vision_alignment_score = vision_alignment
        metrics.chaos_score = chaos_score

        # Determine risk level
        if chaos_score > 0.8:
            metrics.risk_level = "critical"
        elif chaos_score > 0.6:
            metrics.risk_level = "high"
        elif chaos_score > 0.4:
            metrics.risk_level = "medium"
        else:
            metrics.risk_level = "low"

    def _get_agent_activity_window(self, agent_id: str, window_seconds: float) -> List:
        """Get recent activity for an agent within time window."""
        cutoff_time = time.time() - window_seconds

        return [
            event
            for event in self.activity_monitor.activity_history
            if event.agent_id == agent_id and event.timestamp > cutoff_time
        ]

    def _calculate_vision_alignment(
        self, agent_id: str, recent_activity: List
    ) -> float:
        """Calculate how well agent activities align with project vision."""
        try:
            # Load current vision
            charter_data = utils.read_json(
                self.ai_onboard_dir / "charter.json", default={}
            )

            if not charter_data:
                return 0.5  # Neutral if no vision

            vision = charter_data.get("vision", {})
            primary_goal = vision.get("primary_goal", "")

            if not primary_goal:
                return 0.5

            # Analyze recent activities for alignment
            aligned_activities = 0.0
            total_activities = len(recent_activity)

            if total_activities == 0:
                return 0.5

            for activity in recent_activity:
                activity_desc = activity.description.lower()
                goal_lower = primary_goal.lower()

                # Check for alignment keywords
                if any(word in activity_desc for word in goal_lower.split()):
                    aligned_activities += 1
                elif any(
                    concept in activity_desc
                    for concept in ["build", "create", "implement", "develop"]
                ):
                    aligned_activities += 0.5  # Partial alignment

            return aligned_activities / total_activities

        except Exception:
            return 0.5

    def _calculate_chaos_score(
        self,
        files_rate: float,
        changes_rate: float,
        vision_alignment: float,
        recent_activity: List,
    ) -> float:
        """Calculate overall chaos score (0.0 = no chaos, 1.0 = maximum chaos)."""
        score = 0.0

        # File creation chaos (too many files too fast)
        if files_rate > self.chaos_thresholds["file_creation_rate"]:
            file_chaos = min(
                1.0, (files_rate - self.chaos_thresholds["file_creation_rate"]) / 10
            )
            score += file_chaos * 0.3

        # Change rate chaos (too many changes too fast)
        if changes_rate > self.chaos_thresholds["change_rate"]:
            change_chaos = min(
                1.0, (changes_rate - self.chaos_thresholds["change_rate"]) / 20
            )
            score += change_chaos * 0.25

        # Vision drift (low alignment)
        if vision_alignment < self.chaos_thresholds["vision_alignment_threshold"]:
            drift_chaos = (
                self.chaos_thresholds["vision_alignment_threshold"] - vision_alignment
            ) / 0.5
            score += drift_chaos * 0.3

        # Technical debt indicators (complex patterns)
        complexity_score = self._analyze_technical_debt(recent_activity)
        score += complexity_score * 0.15

        return min(1.0, score)

    def _analyze_technical_debt(self, recent_activity: List) -> float:
        """Analyze recent activity for technical debt indicators."""
        debt_score = 0.0

        # Look for patterns that indicate technical debt
        for activity in recent_activity:
            desc = activity.description.lower()

            # Adding many dependencies
            if "depend" in desc and activity.confidence < 0.7:
                debt_score += 0.2

            # Large refactoring operations
            if "refactor" in desc and "file" in desc:
                debt_score += 0.15

            # Complex file operations
            if any(word in desc for word in ["complex", "advanced", "sophisticated"]):
                debt_score += 0.1

        return min(1.0, debt_score)

    def _detect_file_bloat(self, agent_id: str) -> List[ChaosEvent]:
        """Detect file bloat patterns."""
        events: List[ChaosEvent] = []
        metrics = self.agent_metrics.get(agent_id)

        if (
            not metrics
            or metrics.files_created_rate <= self.chaos_thresholds["file_creation_rate"]
        ):
            return events

        # Calculate severity based on how much over threshold
        over_threshold = (
            metrics.files_created_rate / self.chaos_thresholds["file_creation_rate"]
        )

        if over_threshold > 3.0:
            severity = ChaosSeverity.CRITICAL
        elif over_threshold > 2.0:
            severity = ChaosSeverity.HIGH
        elif over_threshold > 1.5:
            severity = ChaosSeverity.MEDIUM
        else:
            severity = ChaosSeverity.LOW

        event = ChaosEvent(
            event_id=f"file_bloat_{agent_id}_{int(time.time())}",
            chaos_type=ChaosType.FILE_BLOAT,
            severity=severity,
            agent_id=agent_id,
            description=(
                f"Agent creating {metrics.files_created_rate:.1f} files/min "
                f"(threshold: {self.chaos_thresholds['file_creation_rate']})"
            ),
            confidence=0.8,
            detected_at=time.time(),
            evidence={
                "files_rate": metrics.files_created_rate,
                "threshold": self.chaos_thresholds["file_creation_rate"],
                "over_threshold": over_threshold,
            },
        )

        events.append(event)
        return events

    def _detect_rapid_changes(self, agent_id: str) -> List[ChaosEvent]:
        """Detect rapid change patterns."""
        events: List[ChaosEvent] = []
        metrics = self.agent_metrics.get(agent_id)

        if not metrics or metrics.changes_rate <= self.chaos_thresholds["change_rate"]:
            return events

        over_threshold = metrics.changes_rate / self.chaos_thresholds["change_rate"]

        if over_threshold > 3.0:
            severity = ChaosSeverity.CRITICAL
        elif over_threshold > 2.0:
            severity = ChaosSeverity.HIGH
        elif over_threshold > 1.5:
            severity = ChaosSeverity.MEDIUM
        else:
            severity = ChaosSeverity.LOW

        event = ChaosEvent(
            event_id=f"rapid_changes_{agent_id}_{int(time.time())}",
            chaos_type=ChaosType.RAPID_CHANGES,
            severity=severity,
            agent_id=agent_id,
            description=(
                f"Agent making {metrics.changes_rate:.1f} changes/min "
                f"(threshold: {self.chaos_thresholds['change_rate']})"
            ),
            confidence=0.8,
            detected_at=time.time(),
            evidence={
                "changes_rate": metrics.changes_rate,
                "threshold": self.chaos_thresholds["change_rate"],
                "over_threshold": over_threshold,
            },
        )

        events.append(event)
        return events

    def _detect_vision_drift(self, agent_id: str) -> List[ChaosEvent]:
        """Detect vision drift patterns."""
        events: List[ChaosEvent] = []
        metrics = self.agent_metrics.get(agent_id)

        if (
            not metrics
            or metrics.vision_alignment_score
            >= self.chaos_thresholds["vision_alignment_threshold"]
        ):
            return events

        drift_amount = (
            self.chaos_thresholds["vision_alignment_threshold"]
            - metrics.vision_alignment_score
        )

        if drift_amount > 0.3:
            severity = ChaosSeverity.CRITICAL
        elif drift_amount > 0.2:
            severity = ChaosSeverity.HIGH
        elif drift_amount > 0.1:
            severity = ChaosSeverity.MEDIUM
        else:
            severity = ChaosSeverity.LOW

        event = ChaosEvent(
            event_id=f"vision_drift_{agent_id}_{int(time.time())}",
            chaos_type=ChaosType.VISION_DRIFT,
            severity=severity,
            agent_id=agent_id,
            description=f"Agent activities {drift_amount:.1%} below vision alignment threshold",
            confidence=0.7,
            detected_at=time.time(),
            evidence={
                "alignment_score": metrics.vision_alignment_score,
                "threshold": self.chaos_thresholds["vision_alignment_threshold"],
                "drift_amount": drift_amount,
            },
        )

        events.append(event)
        return events

    def _detect_technical_debt(self, agent_id: str) -> List[ChaosEvent]:
        """Detect technical debt creation patterns."""
        events: List[ChaosEvent] = []
        metrics = self.agent_metrics.get(agent_id)

        if not metrics:
            return events

        # Check for high complexity increase
        if metrics.complexity_increase > self.chaos_thresholds["complexity_threshold"]:
            severity = (
                ChaosSeverity.HIGH
                if metrics.complexity_increase > 0.8
                else ChaosSeverity.MEDIUM
            )

            event = ChaosEvent(
                event_id=f"technical_debt_{agent_id}_{int(time.time())}",
                chaos_type=ChaosType.TECHNICAL_DEBT,
                severity=severity,
                agent_id=agent_id,
                description=f"High complexity increase detected: {metrics.complexity_increase:.1%}",
                confidence=0.6,
                detected_at=time.time(),
                evidence={
                    "complexity_increase": metrics.complexity_increase,
                    "threshold": self.chaos_thresholds["complexity_threshold"],
                },
            )

            events.append(event)

        return events

    def _detect_unrelated_work(self, agent_id: str) -> List[ChaosEvent]:
        """Detect work that seems unrelated to project scope."""
        events: List[ChaosEvent] = []

        # This would analyze recent activities against project charter
        # For now, return empty (would need more sophisticated analysis)

        return events

    def _detect_repetitive_failures(self, agent_id: str) -> List[ChaosEvent]:
        """Detect patterns of repeated failures."""
        events: List[ChaosEvent] = []
        metrics = self.agent_metrics.get(agent_id)

        if (
            not metrics
            or metrics.failure_rate <= self.chaos_thresholds["failure_rate_threshold"]
        ):
            return events

        if metrics.failure_rate > 0.5:  # More than 50% failure rate
            severity = ChaosSeverity.HIGH
        elif metrics.failure_rate > 0.3:
            severity = ChaosSeverity.MEDIUM
        else:
            severity = ChaosSeverity.LOW

        event = ChaosEvent(
            event_id=f"repetitive_failures_{agent_id}_{int(time.time())}",
            chaos_type=ChaosType.REPETITIVE_FAILURES,
            severity=severity,
            agent_id=agent_id,
            description=(
                f"Agent failure rate: {metrics.failure_rate:.1%} "
                f"(threshold: {self.chaos_thresholds['failure_rate_threshold']})"
            ),
            confidence=0.7,
            detected_at=time.time(),
            evidence={
                "failure_rate": metrics.failure_rate,
                "threshold": self.chaos_thresholds["failure_rate_threshold"],
            },
        )

        events.append(event)
        return events

    def _load_chaos_thresholds(self) -> Dict[str, float]:
        """Load chaos detection thresholds from configuration."""
        return {
            "file_creation_rate": 5.0,  # files per minute
            "change_rate": 10.0,  # changes per minute
            "vision_alignment_threshold": 0.7,  # 70% alignment required
            "complexity_threshold": 0.6,  # 60% complexity increase threshold
            "failure_rate_threshold": 0.3,  # 30% failure rate threshold
        }

    def _load_chaos_events(self) -> None:
        """Load existing chaos events from storage."""
        try:
            events_file = self.ai_onboard_dir / "chaos_events.json"
            if events_file.exists():
                events_data = utils.read_json(events_file)

                for event_data in events_data:
                    event = ChaosEvent(
                        event_id=event_data["event_id"],
                        chaos_type=ChaosType(event_data["chaos_type"]),
                        severity=ChaosSeverity(event_data["severity"]),
                        agent_id=event_data["agent_id"],
                        description=event_data["description"],
                        confidence=event_data["confidence"],
                        detected_at=event_data["detected_at"],
                        evidence=event_data.get("evidence", {}),
                        resolved=event_data.get("resolved", False),
                        resolved_at=event_data.get("resolved_at"),
                        resolution=event_data.get("resolution"),
                    )

                    self.chaos_events.append(event)

        except Exception as e:
            print(f"Warning: Could not load chaos events: {e}")

    def _save_chaos_events(self) -> None:
        """Save chaos events to storage."""
        try:
            events_data = []
            for event in self.chaos_events[-100:]:  # Save last 100 events
                event_dict = {
                    "event_id": event.event_id,
                    "chaos_type": event.chaos_type.value,
                    "severity": event.severity.value,
                    "agent_id": event.agent_id,
                    "description": event.description,
                    "confidence": event.confidence,
                    "detected_at": event.detected_at,
                    "evidence": event.evidence,
                    "resolved": event.resolved,
                    "resolved_at": event.resolved_at,
                    "resolution": event.resolution,
                }
                events_data.append(event_dict)

            events_file = self.ai_onboard_dir / "chaos_events.json"
            utils.write_json(events_file, events_data)

        except Exception as e:
            print(f"Warning: Could not save chaos events: {e}")

    def _log_chaos_event(self, event: ChaosEvent) -> None:
        """Log a chaos event for monitoring."""
        try:
            # Log to session log
            log_entry = {
                "timestamp": time.time(),
                "type": "chaos_detected",
                "event_id": event.event_id,
                "chaos_type": event.chaos_type.value,
                "severity": event.severity.value,
                "agent_id": event.agent_id,
                "description": event.description,
                "confidence": event.confidence,
            }

            session_log_path = self.ai_onboard_dir / "session_log.jsonl"
            with open(session_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            print(f"Warning: Failed to log chaos event: {e}")

    def _get_start_time(self) -> Optional[float]:
        """Get approximate start time from oldest chaos event."""
        if not self.chaos_events:
            return None

        oldest_event = min(self.chaos_events, key=lambda e: e.detected_at)
        return oldest_event.detected_at

    def resolve_chaos_event(self, event_id: str, resolution: str) -> bool:
        """Mark a chaos event as resolved."""
        for event in self.chaos_events:
            if event.event_id == event_id:
                event.resolved = True
                event.resolved_at = time.time()
                event.resolution = resolution
                return True

        return False


def get_chaos_detection_system(project_root: Path) -> ChaosDetectionSystem:
    """Get or create chaos detection system for the project."""
    return ChaosDetectionSystem(project_root)
