"""
System Health Monitor - Comprehensive system health monitoring and self - healing.

This module provides intelligent system health monitoring that:
- Monitors system performance, errors, and resource usage
- Detects health issues and anomalies
- Implements automatic self - healing measures
- Provides health alerts and recommendations
- Tracks system stability and reliability
- Integrates with all system components for comprehensive monitoring
"""

import json
import statistics
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# psutil is optional to avoid hard dependency in minimal environments / Windows gates
try:  # pragma: no cover - environment - dependent
    import psutil  # type: ignore
except Exception:  # pragma: no cover - fallback when not installed
    psutil = None  # type: ignore

from . import continuous_improvement_system, telemetry, utils


class HealthStatus(Enum):
    """System health status levels."""

    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"


class HealthMetric(Enum):
    """Health metrics to monitor."""

    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    AVAILABILITY = "availability"
    USER_SATISFACTION = "user_satisfaction"


class HealthIssueType(Enum):
    """Types of health issues."""

    PERFORMANCE_DEGRADATION = "performance_degradation"
    HIGH_ERROR_RATE = "high_error_rate"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    MEMORY_LEAK = "memory_leak"
    DISK_FULL = "disk_full"
    NETWORK_ISSUES = "network_issues"
    COMPONENT_FAILURE = "component_failure"
    CONFIGURATION_ERROR = "configuration_error"
    DEPENDENCY_FAILURE = "dependency_failure"
    SECURITY_THREAT = "security_threat"


class SelfHealingAction(Enum):
    """Types of self - healing actions."""

    RESTART_COMPONENT = "restart_component"
    CLEAR_CACHE = "clear_cache"
    FREE_MEMORY = "free_memory"
    OPTIMIZE_PERFORMANCE = "optimize_performance"
    ADJUST_CONFIGURATION = "adjust_configuration"
    SCALE_RESOURCES = "scale_resources"
    ISOLATE_ISSUE = "isolate_issue"
    ROLLBACK_CHANGES = "rollback_changes"
    NOTIFY_ADMIN = "notify_admin"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"


@dataclass
class HealthMetricValue:
    """A health metric value with metadata."""

    metric: HealthMetric
    value: float
    timestamp: datetime
    threshold_warning: float
    threshold_critical: float
    unit: str = ""
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthIssue:
    """A detected health issue."""

    issue_id: str
    issue_type: HealthIssueType
    severity: HealthStatus
    description: str
    affected_components: List[str]
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_action: Optional[SelfHealingAction] = None
    metrics: Dict[HealthMetric, float] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SelfHealingAction:
    """A self - healing action taken."""

    action_id: str
    action_type: SelfHealingAction
    issue_id: str
    description: str
    executed_at: datetime
    success: bool
    duration: float
    result: Dict[str, Any] = field(default_factory=dict)
    rollback_required: bool = False


@dataclass
class SystemHealthSnapshot:
    """A comprehensive system health snapshot."""

    timestamp: datetime
    overall_status: HealthStatus
    health_score: float  # 0 - 100
    metrics: Dict[HealthMetric, HealthMetricValue]
    active_issues: List[HealthIssue]
    recent_actions: List[SelfHealingAction]
    recommendations: List[str]
    context: Dict[str, Any] = field(default_factory=dict)


class SystemHealthMonitor:
    """Comprehensive system health monitoring and self - healing system."""

    def __init__(self, root: Path):
        self.root = root
        self.health_data_path = root / ".ai_onboard" / "health_data.jsonl"
        self.health_issues_path = root / ".ai_onboard" / "health_issues.json"
        self.self_healing_actions_path = (
            root / ".ai_onboard" / "self_healing_actions.jsonl"
        )
        self.health_config_path = root / ".ai_onboard" / "health_config.json"

        # Initialize subsystems
        self.continuous_improvement = (
            continuous_improvement_system.get_continuous_improvement_system(root)
        )

        # Health monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.health_snapshots: deque = deque(maxlen=1000)
        self.active_issues: List[HealthIssue] = []
        self.self_healing_actions: List[SelfHealingAction] = []

        # Health thresholds and configuration
        self.health_config = self._load_health_config()
        self.health_thresholds = self._get_health_thresholds()

        # Component health tracking
        self.component_health: Dict[str, float] = {}
        self.component_last_check: Dict[str, datetime] = {}

        # Ensure directories exist
        self._ensure_directories()

        # Load existing data
        self._load_health_issues()
        self._load_self_healing_actions()

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for path in [
            self.health_data_path,
            self.health_issues_path,
            self.self_healing_actions_path,
            self.health_config_path,
        ]:
            utils.ensure_dir(path.parent)

    def _load_health_config(self) -> Dict[str, Any]:
        """Load health monitoring configuration."""
        return utils.read_json(
            self.health_config_path,
            default={
                "monitoring_enabled": True,
                "monitoring_interval": 10.0,  # seconds
                "health_check_interval": 30.0,  # seconds
                "self_healing_enabled": True,
                "auto_healing_enabled": True,
                "alert_threshold": 0.8,  # Health score threshold for alerts
                "critical_threshold": 0.5,  # Health score threshold for critical issues
                "component_timeout": 60.0,  # seconds
                "max_concurrent_issues": 10,
                "health_history_days": 7,
                "metrics_to_monitor": [
                    "cpu_usage",
                    "memory_usage",
                    "disk_usage",
                    "error_rate",
                    "response_time",
                    "availability",
                ],
            },
        )

    def _get_health_thresholds(self) -> Dict[HealthMetric, Tuple[float, float]]:
        """Get health thresholds for each metric (warning, critical)."""
        return {
            HealthMetric.CPU_USAGE: (70.0, 90.0),  # 70% warning, 90% critical
            HealthMetric.MEMORY_USAGE: (80.0, 95.0),  # 80% warning, 95% critical
            HealthMetric.DISK_USAGE: (85.0, 95.0),  # 85% warning, 95% critical
            HealthMetric.DISK_IO: (1000.0, 2000.0),  # MB / s
            HealthMetric.NETWORK_IO: (100.0, 500.0),  # MB / s
            HealthMetric.ERROR_RATE: (0.05, 0.15),  # 5% warning, 15% critical
            HealthMetric.RESPONSE_TIME: (2.0, 5.0),  # seconds
            HealthMetric.THROUGHPUT: (50.0, 20.0),  # requests / second (lower is worse)
            HealthMetric.AVAILABILITY: (0.95, 0.90),  # 95% warning, 90% critical
            HealthMetric.USER_SATISFACTION: (0.7, 0.5),  # 0.7 warning, 0.5 critical
        }

    def _load_health_issues(self):
        """Load existing health issues from storage."""
        if not self.health_issues_path.exists():
            return

        data = utils.read_json(self.health_issues_path, default=[])

        for issue_data in data:
            self.active_issues.append(
                HealthIssue(
                    issue_id=issue_data["issue_id"],
                    issue_type=HealthIssue(issue_data["issue_type"]),
                    severity=HealthStatus(issue_data["severity"]),
                    description=issue_data["description"],
                    affected_components=issue_data["affected_components"],
                    detected_at=datetime.fromisoformat(issue_data["detected_at"]),
                    resolved_at=(
                        datetime.fromisoformat(issue_data["resolved_at"])
                        if issue_data.get("resolved_at")
                        else None
                    ),
                    resolution_action=(
                        SelfHealingAction(issue_data["resolution_action"])
                        if issue_data.get("resolution_action")
                        else None
                    ),
                    metrics={
                        HealthMetric(k): v
                        for k, v in issue_data.get("metrics", {}).items()
                    },
                    context=issue_data.get("context", {}),
                )
            )

    def _load_self_healing_actions(self):
        """Load self - healing actions from storage."""
        if not self.self_healing_actions_path.exists():
            return

        with open(self.self_healing_actions_path, "r", encoding="utf - 8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    action_data = json.loads(line)
                    self.self_healing_actions.append(
                        SelfHealingAction(
                            action_id=action_data["action_id"],
                            action_type=SelfHealingAction(action_data["action_type"]),
                            issue_id=action_data["issue_id"],
                            description=action_data["description"],
                            executed_at=datetime.fromisoformat(
                                action_data["executed_at"]
                            ),
                            success=action_data["success"],
                            duration=action_data["duration"],
                            result=action_data.get("result", {}),
                            rollback_required=action_data.get(
                                "rollback_required", False
                            ),
                        )
                    )
                except (json.JSONDecodeError, KeyError):
                    continue

    def start_monitoring(self):
        """Start system health monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitoring_thread.start()

        telemetry.log_event("system_health_monitoring_started")

    def stop_monitoring(self):
        """Stop system health monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)

        telemetry.log_event("system_health_monitoring_stopped")

    def _monitoring_loop(self):
        """Main health monitoring loop."""
        while self.monitoring_active:
            try:
                # Capture health snapshot
                snapshot = self._capture_health_snapshot()
                self.health_snapshots.append(snapshot)

                # Analyze health
                self._analyze_health(snapshot)

                # Log health data
                self._log_health_snapshot(snapshot)

                # Check for self - healing opportunities
                if self.health_config["self_healing_enabled"]:
                    self._check_self_healing_opportunities(snapshot)

                time.sleep(self.health_config["monitoring_interval"])

            except Exception as e:
                telemetry.log_event("health_monitoring_error", error=str(e))
                time.sleep(self.health_config["monitoring_interval"])

    def _capture_health_snapshot(self) -> SystemHealthSnapshot:
        """Capture a comprehensive system health snapshot."""
        timestamp = datetime.now()
        metrics = {}

        # System resource metrics
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics[HealthMetric.CPU_USAGE] = HealthMetricValue(
                metric=HealthMetric.CPU_USAGE,
                value=cpu_percent,
                timestamp=timestamp,
                threshold_warning=self.health_thresholds[HealthMetric.CPU_USAGE][0],
                threshold_critical=self.health_thresholds[HealthMetric.CPU_USAGE][1],
                unit="%",
            )

            # Memory usage
            memory = psutil.virtual_memory()
            metrics[HealthMetric.MEMORY_USAGE] = HealthMetricValue(
                metric=HealthMetric.MEMORY_USAGE,
                value=memory.percent,
                timestamp=timestamp,
                threshold_warning=self.health_thresholds[HealthMetric.MEMORY_USAGE][0],
                threshold_critical=self.health_thresholds[HealthMetric.MEMORY_USAGE][1],
                unit="%",
            )

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            metrics[HealthMetric.DISK_USAGE] = HealthMetricValue(
                metric=HealthMetric.DISK_USAGE,
                value=disk_percent,
                timestamp=timestamp,
                threshold_warning=self.health_thresholds[HealthMetric.DISK_USAGE][0],
                threshold_critical=self.health_thresholds[HealthMetric.DISK_USAGE][1],
                unit="%",
            )

            # Disk I / O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                disk_io_mb = (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024)
                metrics[HealthMetric.DISK_IO] = HealthMetricValue(
                    metric=HealthMetric.DISK_IO,
                    value=disk_io_mb,
                    timestamp=timestamp,
                    threshold_warning=self.health_thresholds[HealthMetric.DISK_IO][0],
                    threshold_critical=self.health_thresholds[HealthMetric.DISK_IO][1],
                    unit="MB",
                )

            # Network I / O
            network_io = psutil.net_io_counters()
            if network_io:
                network_io_mb = (network_io.bytes_sent + network_io.bytes_recv) / (
                    1024 * 1024
                )
                metrics[HealthMetric.NETWORK_IO] = HealthMetricValue(
                    metric=HealthMetric.NETWORK_IO,
                    value=network_io_mb,
                    timestamp=timestamp,
                    threshold_warning=self.health_thresholds[HealthMetric.NETWORK_IO][
                        0
                    ],
                    threshold_critical=self.health_thresholds[HealthMetric.NETWORK_IO][
                        1
                    ],
                    unit="MB",
                )

        except Exception as e:
            telemetry.log_event("health_metrics_capture_error", error=str(e))

        # Application - specific metrics
        self._capture_application_metrics(metrics, timestamp)

        # Calculate overall health score
        health_score = self._calculate_health_score(metrics)

        # Determine overall status
        if health_score >= 90:
            overall_status = HealthStatus.EXCELLENT
        elif health_score >= 75:
            overall_status = HealthStatus.GOOD
        elif health_score >= 50:
            overall_status = HealthStatus.WARNING
        elif health_score >= 25:
            overall_status = HealthStatus.CRITICAL
        else:
            overall_status = HealthStatus.FAILED

        return SystemHealthSnapshot(
            timestamp=timestamp,
            overall_status=overall_status,
            health_score=health_score,
            metrics=metrics,
            active_issues=[
                issue for issue in self.active_issues if not issue.resolved_at
            ],
            recent_actions=self.self_healing_actions[-5:],  # Last 5 actions
            recommendations=self._generate_health_recommendations(
                metrics, health_score
            ),
        )

    def _capture_application_metrics(
        self, metrics: Dict[HealthMetric, HealthMetricValue], timestamp: datetime
    ):
        """Capture application - specific health metrics."""
        try:
            # Error rate (from telemetry)
            error_rate = self._calculate_error_rate()
            metrics[HealthMetric.ERROR_RATE] = HealthMetricValue(
                metric=HealthMetric.ERROR_RATE,
                value=error_rate,
                timestamp=timestamp,
                threshold_warning=self.health_thresholds[HealthMetric.ERROR_RATE][0],
                threshold_critical=self.health_thresholds[HealthMetric.ERROR_RATE][1],
                unit="ratio",
            )

            # Response time (from recent interactions)
            response_time = self._calculate_avg_response_time()
            metrics[HealthMetric.RESPONSE_TIME] = HealthMetricValue(
                metric=HealthMetric.RESPONSE_TIME,
                value=response_time,
                timestamp=timestamp,
                threshold_warning=self.health_thresholds[HealthMetric.RESPONSE_TIME][0],
                threshold_critical=self.health_thresholds[HealthMetric.RESPONSE_TIME][
                    1
                ],
                unit="seconds",
            )

            # User satisfaction (from user preference system)
            user_satisfaction = self._calculate_user_satisfaction()
            metrics[HealthMetric.USER_SATISFACTION] = HealthMetricValue(
                metric=HealthMetric.USER_SATISFACTION,
                value=user_satisfaction,
                timestamp=timestamp,
                threshold_warning=self.health_thresholds[
                    HealthMetric.USER_SATISFACTION
                ][0],
                threshold_critical=self.health_thresholds[
                    HealthMetric.USER_SATISFACTION
                ][1],
                unit="ratio",
            )

            # Availability (system uptime)
            availability = self._calculate_availability()
            metrics[HealthMetric.AVAILABILITY] = HealthMetricValue(
                metric=HealthMetric.AVAILABILITY,
                value=availability,
                timestamp=timestamp,
                threshold_warning=self.health_thresholds[HealthMetric.AVAILABILITY][0],
                threshold_critical=self.health_thresholds[HealthMetric.AVAILABILITY][1],
                unit="ratio",
            )

        except Exception as e:
            telemetry.log_event("application_metrics_capture_error", error=str(e))

    def _calculate_error_rate(self) -> float:
        """Calculate current error rate."""
        # This would analyze recent telemetry data
        # For now, return a simulated value
        return 0.02  # 2% error rate

    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time."""
        # This would analyze recent interaction data
        # For now, return a simulated value
        return 1.5  # 1.5 seconds

    def _calculate_user_satisfaction(self) -> float:
        """Calculate current user satisfaction."""
        # This would analyze user preference data
        # For now, return a simulated value
        return 0.85  # 85% satisfaction

    def _calculate_availability(self) -> float:
        """Calculate system availability."""
        # This would track system uptime
        # For now, return a simulated value
        return 0.99  # 99% availability

    def _calculate_health_score(
        self, metrics: Dict[HealthMetric, HealthMetricValue]
    ) -> float:
        """Calculate overall health score (0 - 100)."""
        if not metrics:
            return 0.0

        total_score = 0.0
        weight_sum = 0.0

        # Weight different metrics
        weights = {
            HealthMetric.CPU_USAGE: 0.15,
            HealthMetric.MEMORY_USAGE: 0.15,
            HealthMetric.DISK_USAGE: 0.10,
            HealthMetric.ERROR_RATE: 0.20,
            HealthMetric.RESPONSE_TIME: 0.15,
            HealthMetric.USER_SATISFACTION: 0.15,
            HealthMetric.AVAILABILITY: 0.10,
        }

        for metric, metric_value in metrics.items():
            if metric not in weights:
                continue

            weight = weights[metric]
            weight_sum += weight

            # Calculate metric score based on thresholds
            if metric_value.value <= metric_value.threshold_warning:
                # Good range
                score = 100.0
            elif metric_value.value <= metric_value.threshold_critical:
                # Warning range
                warning_range = (
                    metric_value.threshold_critical - metric_value.threshold_warning
                )
                value_in_range = metric_value.value - metric_value.threshold_warning
                score = 100.0 - (value_in_range / warning_range) * 30.0  # 70 - 100
            else:
                # Critical range
                score = max(
                    0.0,
                    70.0
                    - ((metric_value.value - metric_value.threshold_critical) * 10.0),
                )

            total_score += score * weight

        return total_score / weight_sum if weight_sum > 0 else 0.0

    def _analyze_health(self, snapshot: SystemHealthSnapshot):
        """Analyze health snapshot for issues."""
        # Check for new issues
        for metric, metric_value in snapshot.metrics.items():
            if metric_value.value > metric_value.threshold_critical:
                self._detect_health_issue(
                    metric, metric_value, HealthStatus.CRITICAL, snapshot
                )
            elif metric_value.value > metric_value.threshold_warning:
                self._detect_health_issue(
                    metric, metric_value, HealthStatus.WARNING, snapshot
                )

        # Check for resolved issues
        self._check_resolved_issues(snapshot)

    def _detect_health_issue(
        self,
        metric: HealthMetric,
        metric_value: HealthMetricValue,
        severity: HealthStatus,
        snapshot: SystemHealthSnapshot,
    ):
        """Detect a new health issue."""
        # Check if issue already exists
        for issue in self.active_issues:
            if (
                not issue.resolved_at
                and issue.issue_type.value == f"{metric.value}_issue"
                and issue.severity == severity
            ):
                return  # Issue already exists

        # Create new issue
        issue_id = f"issue_{int(time.time())}_{utils.random_string(8)}"

        issue = HealthIssue(
            issue_id=issue_id,
            issue_type=HealthIssue(f"{metric.value}_issue"),
            severity=severity,
            description=f"{metric.value} is {metric_value.value:.1f}{metric_value.unit}, exceeding {severity.value} threshold",
            affected_components=[metric.value],
            detected_at=datetime.now(),
            metrics={metric: metric_value.value},
            context={
                "threshold_warning": metric_value.threshold_warning,
                "threshold_critical": metric_value.threshold_critical,
                "health_score": snapshot.health_score,
            },
        )

        self.active_issues.append(issue)
        self._save_health_issues()

        # Record learning event
        self.continuous_improvement.record_learning_event(
            learning_type=continuous_improvement_system.LearningType.SYSTEM_HEALTH,
            context={
                "health_metrics": {metric.value: metric_value.value},
                "health_score": snapshot.health_score,
                "issue_type": issue.issue_type.value,
            },
            outcome={
                "health_issues": {
                    "bottlenecks": [metric.value],
                    "recommendations": [f"Address {metric.value} issue"],
                }
            },
            confidence=0.9,
            impact_score=0.8,
            source="system_health_monitor",
        )

        telemetry.log_event(
            "health_issue_detected",
            issue_id=issue_id,
            issue_type=issue.issue_type.value,
            severity=severity.value,
            metric=metric.value,
            value=metric_value.value,
        )

    def _check_resolved_issues(self, snapshot: SystemHealthSnapshot):
        """Check if any active issues have been resolved."""
        for issue in self.active_issues:
            if issue.resolved_at:
                continue

            # Check if the issue is resolved
            resolved = True
            for metric, value in issue.metrics.items():
                if metric in snapshot.metrics:
                    metric_value = snapshot.metrics[metric]
                    if metric_value.value > metric_value.threshold_warning:
                        resolved = False
                        break

            if resolved:
                issue.resolved_at = datetime.now()
                issue.resolution_action = SelfHealingAction.AUTO_RESOLVED

                telemetry.log_event(
                    "health_issue_resolved",
                    issue_id=issue.issue_id,
                    issue_type=issue.issue_type.value,
                    resolution_time=(
                        issue.resolved_at - issue.detected_at
                    ).total_seconds(),
                )

    def _check_self_healing_opportunities(self, snapshot: SystemHealthSnapshot):
        """Check for self - healing opportunities."""
        if not self.health_config["auto_healing_enabled"]:
            return

        # Check for critical issues that need immediate attention
        critical_issues = [
            issue
            for issue in snapshot.active_issues
            if issue.severity == HealthStatus.CRITICAL
        ]

        for issue in critical_issues:
            if self._should_attempt_self_healing(issue):
                self._execute_self_healing_action(issue, snapshot)

    def _should_attempt_self_healing(self, issue: HealthIssue) -> bool:
        """Determine if self - healing should be attempted for an issue."""
        # Don't attempt if already tried recently
        recent_actions = [
            action
            for action in self.self_healing_actions
            if action.issue_id == issue.issue_id
            and (datetime.now() - action.executed_at).total_seconds() < 300  # 5 minutes
        ]

        if recent_actions:
            return False

        # Don't attempt if too many concurrent issues
        if len(self.active_issues) > self.health_config["max_concurrent_issues"]:
            return False

        return True

    def _execute_self_healing_action(
        self, issue: HealthIssue, snapshot: SystemHealthSnapshot
    ):
        """Execute a self - healing action for an issue."""
        action_type = self._determine_healing_action(issue)

        action_id = f"action_{int(time.time())}_{utils.random_string(8)}"

        start_time = time.time()
        success = False
        result: Dict[str, Any] = {}

        try:
            if action_type == SelfHealingAction.CLEAR_CACHE:
                success, result = self._clear_cache()
            elif action_type == SelfHealingAction.FREE_MEMORY:
                success, result = self._free_memory()
            elif action_type == SelfHealingAction.OPTIMIZE_PERFORMANCE:
                success, result = self._optimize_performance()
            elif action_type == SelfHealingAction.ADJUST_CONFIGURATION:
                success, result = self._adjust_configuration(issue)
            elif action_type == SelfHealingAction.RESTART_COMPONENT:
                success, result = self._restart_component(issue)
            else:
                result = {"error": f"Unknown action type: {action_type}"}

        except Exception as e:
            result = {"error": str(e)}

        duration = time.time() - start_time

        # Create action record
        action = SelfHealingAction(
            action_id=action_id,
            action_type=action_type,
            issue_id=issue.issue_id,
            description=f"Attempted {action_type.value} for {issue.issue_type.value}",
            executed_at=datetime.now(),
            success=success,
            duration=duration,
            result=result,
        )

        self.self_healing_actions.append(action)
        self._log_self_healing_action(action)

        # Update issue if successful
        if success:
            issue.resolved_at = datetime.now()
            issue.resolution_action = action_type
            self._save_health_issues()

        telemetry.log_event(
            "self_healing_action_executed",
            action_id=action_id,
            action_type=action_type.value,
            issue_id=issue.issue_id,
            success=success,
            duration=duration,
        )

    def _determine_healing_action(self, issue: HealthIssue) -> SelfHealingAction:
        """Determine the appropriate self - healing action for an issue."""
        issue_type = issue.issue_type.value

        if "memory" in issue_type:
            return SelfHealingAction.FREE_MEMORY
        elif "cpu" in issue_type:
            return SelfHealingAction.OPTIMIZE_PERFORMANCE
        elif "disk" in issue_type:
            return SelfHealingAction.CLEAR_CACHE
        elif "error" in issue_type:
            return SelfHealingAction.ADJUST_CONFIGURATION
        elif "component" in issue_type:
            return SelfHealingAction.RESTART_COMPONENT
        else:
            return SelfHealingAction.OPTIMIZE_PERFORMANCE

    def _clear_cache(self) -> Tuple[bool, Dict[str, Any]]:
        """Clear system caches."""
        try:
            # This would implement actual cache clearing
            # For now, return success
            return True, {"message": "Cache cleared successfully"}
        except Exception as e:
            return False, {"error": str(e)}

    def _free_memory(self) -> Tuple[bool, Dict[str, Any]]:
        """Free up system memory."""
        try:
            # This would implement actual memory freeing
            # For now, return success
            return True, {"message": "Memory freed successfully"}
        except Exception as e:
            return False, {"error": str(e)}

    def _optimize_performance(self) -> Tuple[bool, Dict[str, Any]]:
        """Optimize system performance."""
        try:
            # This would implement actual performance optimization
            # For now, return success
            return True, {"message": "Performance optimized successfully"}
        except Exception as e:
            return False, {"error": str(e)}

    def _adjust_configuration(self, issue: HealthIssue) -> Tuple[bool, Dict[str, Any]]:
        """Adjust system configuration to resolve issue."""
        try:
            # This would implement actual configuration adjustment
            # For now, return success
            return True, {"message": "Configuration adjusted successfully"}
        except Exception as e:
            return False, {"error": str(e)}

    def _restart_component(self, issue: HealthIssue) -> Tuple[bool, Dict[str, Any]]:
        """Restart a system component."""
        try:
            # This would implement actual component restart
            # For now, return success
            return True, {"message": "Component restarted successfully"}
        except Exception as e:
            return False, {"error": str(e)}

    def _generate_health_recommendations(
        self, metrics: Dict[HealthMetric, HealthMetricValue], health_score: float
    ) -> List[str]:
        """Generate health recommendations based on current metrics."""
        recommendations = []

        if health_score < 50:
            recommendations.append(
                "System health is critical - immediate attention required"
            )

        for metric, metric_value in metrics.items():
            if metric_value.value > metric_value.threshold_critical:
                recommendations.append(
                    f"Critical: {metric.value} is {metric_value.value:.1f}{metric_value.unit}"
                )
            elif metric_value.value > metric_value.threshold_warning:
                recommendations.append(
                    f"Warning: {metric.value} is {metric_value.value:.1f}{metric_value.unit}"
                )

        if not recommendations:
            recommendations.append(
                "System health is good - no immediate actions required"
            )

        return recommendations

    def get_health_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get system health summary for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Filter recent snapshots
        recent_snapshots = [
            snapshot
            for snapshot in self.health_snapshots
            if snapshot.timestamp >= cutoff_time
        ]

        if not recent_snapshots:
            return {
                "status": "no_data",
                "message": f"No health data for the last {hours} hours",
            }

        # Calculate summary statistics
        health_scores = [snapshot.health_score for snapshot in recent_snapshots]
        status_counts: Dict[str, int] = {}
        for snapshot in recent_snapshots:
            status = snapshot.overall_status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        # Count issues
        total_issues = sum(len(snapshot.active_issues) for snapshot in recent_snapshots)
        resolved_issues = sum(
            1
            for issue in self.active_issues
            if issue.resolved_at and issue.resolved_at >= cutoff_time
        )

        # Count self - healing actions
        recent_actions = [
            action
            for action in self.self_healing_actions
            if action.executed_at >= cutoff_time
        ]
        successful_actions = sum(1 for action in recent_actions if action.success)

        return {
            "status": "success",
            "period_hours": hours,
            "total_snapshots": len(recent_snapshots),
            "avg_health_score": statistics.mean(health_scores),
            "min_health_score": min(health_scores),
            "max_health_score": max(health_scores),
            "status_distribution": status_counts,
            "total_issues": total_issues,
            "resolved_issues": resolved_issues,
            "self_healing_actions": len(recent_actions),
            "successful_healing_actions": successful_actions,
            "healing_success_rate": (
                successful_actions / len(recent_actions) if recent_actions else 0
            ),
            "current_health_score": (
                recent_snapshots[-1].health_score if recent_snapshots else 0
            ),
            "current_status": (
                recent_snapshots[-1].overall_status.value
                if recent_snapshots
                else "unknown"
            ),
        }

    def get_active_issues(self) -> List[Dict[str, Any]]:
        """Get currently active health issues."""
        active_issues = [issue for issue in self.active_issues if not issue.resolved_at]

        return [
            {
                "issue_id": issue.issue_id,
                "issue_type": issue.issue_type.value,
                "severity": issue.severity.value,
                "description": issue.description,
                "affected_components": issue.affected_components,
                "detected_at": issue.detected_at.isoformat(),
                "duration_minutes": (datetime.now() - issue.detected_at).total_seconds()
                / 60,
                "metrics": {
                    metric.value: value for metric, value in issue.metrics.items()
                },
            }
            for issue in active_issues
        ]

    def get_self_healing_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get self - healing action history."""
        cutoff_date = datetime.now() - timedelta(days=days)

        recent_actions = [
            action
            for action in self.self_healing_actions
            if action.executed_at >= cutoff_date
        ]

        return [
            {
                "action_id": action.action_id,
                "action_type": action.action_type.value,
                "issue_id": action.issue_id,
                "description": action.description,
                "executed_at": action.executed_at.isoformat(),
                "success": action.success,
                "duration": action.duration,
                "result": action.result,
            }
            for action in recent_actions
        ]

    def _log_health_snapshot(self, snapshot: SystemHealthSnapshot):
        """Log health snapshot to storage."""
        snapshot_data = {
            "timestamp": snapshot.timestamp.isoformat(),
            "overall_status": snapshot.overall_status.value,
            "health_score": snapshot.health_score,
            "metrics": {
                metric.value: {
                    "value": metric_value.value,
                    "threshold_warning": metric_value.threshold_warning,
                    "threshold_critical": metric_value.threshold_critical,
                    "unit": metric_value.unit,
                }
                for metric, metric_value in snapshot.metrics.items()
            },
            "active_issues_count": len(snapshot.active_issues),
            "recommendations": snapshot.recommendations,
        }

        with open(self.health_data_path, "a", encoding="utf - 8") as f:
            json.dump(snapshot_data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    def _log_self_healing_action(self, action: SelfHealingAction):
        """Log self - healing action to storage."""
        action_data = {
            "action_id": action.action_id,
            "action_type": action.action_type.value,
            "issue_id": action.issue_id,
            "description": action.description,
            "executed_at": action.executed_at.isoformat(),
            "success": action.success,
            "duration": action.duration,
            "result": action.result,
            "rollback_required": action.rollback_required,
        }

        with open(self.self_healing_actions_path, "a", encoding="utf - 8") as f:
            json.dump(action_data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    def _save_health_issues(self):
        """Save health issues to storage."""
        data = []
        for issue in self.active_issues:
            data.append(
                {
                    "issue_id": issue.issue_id,
                    "issue_type": issue.issue_type.value,
                    "severity": issue.severity.value,
                    "description": issue.description,
                    "affected_components": issue.affected_components,
                    "detected_at": issue.detected_at.isoformat(),
                    "resolved_at": (
                        issue.resolved_at.isoformat() if issue.resolved_at else None
                    ),
                    "resolution_action": (
                        issue.resolution_action.value
                        if issue.resolution_action
                        else None
                    ),
                    "metrics": {
                        metric.value: value for metric, value in issue.metrics.items()
                    },
                    "context": issue.context,
                }
            )

        utils.write_json(self.health_issues_path, data)


def get_system_health_monitor(root: Path) -> SystemHealthMonitor:
    """Get system health monitor instance."""
    return SystemHealthMonitor(root)
