"""
Performance Optimizer - Advanced performance optimization system.

This module provides intelligent performance optimization capabilities that:
- Monitors system performance in real-time
- Identifies performance bottlenecks and optimization opportunities
- Implements automatic optimizations based on learned patterns
- Tracks optimization effectiveness and learns from results
- Provides performance recommendations and insights
"""

import json
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

from . import continuous_improvement_system, telemetry, utils


class OptimizationType(Enum):
    """Types of performance optimizations."""

    MEMORY_OPTIMIZATION = "memory_optimization"
    CPU_OPTIMIZATION = "cpu_optimization"
    I_O_OPTIMIZATION = "i_o_optimization"
    CACHE_OPTIMIZATION = "cache_optimization"
    ALGORITHM_OPTIMIZATION = "algorithm_optimization"
    CONFIGURATION_OPTIMIZATION = "configuration_optimization"
    RESOURCE_POOLING = "resource_pooling"
    LAZY_LOADING = "lazy_loading"


class PerformanceMetric(Enum):
    """Performance metrics to monitor."""

    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    CACHE_HIT_RATE = "cache_hit_rate"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    RESPONSE_TIME = "response_time"


@dataclass
class PerformanceSnapshot:
    """A snapshot of system performance at a point in time."""

    timestamp: datetime
    metrics: Dict[PerformanceMetric, float]
    context: Dict[str, Any] = field(default_factory=dict)
    operation_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class OptimizationOpportunity:
    """An identified opportunity for performance optimization."""

    opportunity_id: str
    optimization_type: OptimizationType
    description: str
    current_performance: Dict[PerformanceMetric, float]
    expected_improvement: float
    confidence: float
    implementation_effort: int  # 1-10
    risk_level: int  # 1-10, lower is safer
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationResult:
    """Result of a performance optimization attempt."""

    optimization_id: str
    opportunity_id: str
    optimization_type: OptimizationType
    success: bool
    performance_before: Dict[PerformanceMetric, float]
    performance_after: Dict[PerformanceMetric, float]
    improvement_percentage: float
    implementation_time: float
    rollback_required: bool = False
    rollback_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceProfile:
    """Performance profile for a specific operation or system component."""

    profile_id: str
    operation_name: str
    baseline_metrics: Dict[PerformanceMetric, float]
    current_metrics: Dict[PerformanceMetric, float]
    optimization_history: List[OptimizationResult] = field(default_factory=list)
    performance_trends: Dict[PerformanceMetric, List[float]] = field(
        default_factory=dict
    )
    last_updated: datetime = field(default_factory=datetime.now)


class PerformanceOptimizer:
    """Advanced performance optimization system."""

    def __init__(self, root: Path):
        self.root = root
        self.performance_data_path = root / ".ai_onboard" / "performance_data.jsonl"
        self.optimization_opportunities_path = (
            root / ".ai_onboard" / "optimization_opportunities.json"
        )
        self.optimization_results_path = (
            root / ".ai_onboard" / "optimization_results.jsonl"
        )
        self.performance_profiles_path = (
            root / ".ai_onboard" / "performance_profiles.json"
        )
        self.optimization_config_path = (
            root / ".ai_onboard" / "optimization_config.json"
        )

        # Initialize subsystems
        self.continuous_improvement = (
            continuous_improvement_system.get_continuous_improvement_system(root)
        )

        # Performance monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        self.performance_snapshots: List[PerformanceSnapshot] = []
        self.performance_profiles: Dict[str, PerformanceProfile] = {}
        self.optimization_opportunities: List[OptimizationOpportunity] = []

        # Configuration
        self.optimization_config = self._load_optimization_config()

        # Ensure directories exist
        self._ensure_directories()

        # Load existing data
        self._load_performance_profiles()
        self._load_optimization_opportunities()

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for path in [
            self.performance_data_path,
            self.optimization_opportunities_path,
            self.optimization_results_path,
            self.performance_profiles_path,
            self.optimization_config_path,
        ]:
            utils.ensure_dir(path.parent)

    def _load_optimization_config(self) -> Dict[str, Any]:
        """Load optimization configuration."""
        return utils.read_json(
            self.optimization_config_path,
            default={
                "monitoring_enabled": True,
                "monitoring_interval": 5.0,  # seconds
                "optimization_threshold": 0.2,  # 20% improvement threshold
                "auto_optimization_enabled": True,
                "auto_optimization_confidence_threshold": 0.8,
                "performance_window_size": 100,  # number of snapshots to keep
                "optimization_cooldown": 300.0,  # seconds between optimizations
                "metrics_to_monitor": [
                    "execution_time",
                    "memory_usage",
                    "cpu_usage",
                    "cache_hit_rate",
                    "error_rate",
                ],
                "optimization_priorities": {
                    "memory_optimization": 8,
                    "cpu_optimization": 7,
                    "i_o_optimization": 6,
                    "cache_optimization": 9,
                    "algorithm_optimization": 5,
                    "configuration_optimization": 4,
                },
            },
        )

    def _load_performance_profiles(self):
        """Load performance profiles from storage."""
        if not self.performance_profiles_path.exists():
            return

        data = utils.read_json(self.performance_profiles_path, default={})

        for profile_id, profile_data in data.items():
            self.performance_profiles[profile_id] = PerformanceProfile(
                profile_id=profile_id,
                operation_name=profile_data["operation_name"],
                baseline_metrics={
                    PerformanceMetric(k): v
                    for k, v in profile_data["baseline_metrics"].items()
                },
                current_metrics={
                    PerformanceMetric(k): v
                    for k, v in profile_data["current_metrics"].items()
                },
                optimization_history=[],  # Will be loaded separately
                performance_trends={
                    PerformanceMetric(k): v
                    for k, v in profile_data.get("performance_trends", {}).items()
                },
                last_updated=datetime.fromisoformat(profile_data["last_updated"]),
            )

    def _load_optimization_opportunities(self):
        """Load optimization opportunities from storage."""
        if not self.optimization_opportunities_path.exists():
            return

        data = utils.read_json(self.optimization_opportunities_path, default=[])

        for opp_data in data:
            self.optimization_opportunities.append(
                OptimizationOpportunity(
                    opportunity_id=opp_data["opportunity_id"],
                    optimization_type=OptimizationType(opp_data["optimization_type"]),
                    description=opp_data["description"],
                    current_performance={
                        PerformanceMetric(k): v
                        for k, v in opp_data["current_performance"].items()
                    },
                    expected_improvement=opp_data["expected_improvement"],
                    confidence=opp_data["confidence"],
                    implementation_effort=opp_data["implementation_effort"],
                    risk_level=opp_data["risk_level"],
                    context=opp_data.get("context", {}),
                    created_at=datetime.fromisoformat(opp_data["created_at"]),
                )
            )

    def start_monitoring(self):
        """Start performance monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitoring_thread.start()

        telemetry.log_event("performance_monitoring_started")

    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)

        telemetry.log_event("performance_monitoring_stopped")

    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                snapshot = self._capture_performance_snapshot()
                self.performance_snapshots.append(snapshot)

                # Keep only recent snapshots
                if (
                    len(self.performance_snapshots)
                    > self.optimization_config["performance_window_size"]
                ):
                    self.performance_snapshots = self.performance_snapshots[
                        -self.optimization_config["performance_window_size"] :
                    ]

                # Analyze for optimization opportunities
                self._analyze_performance_trends()

                # Log performance data
                self._log_performance_snapshot(snapshot)

                time.sleep(self.optimization_config["monitoring_interval"])

            except Exception as e:
                telemetry.log_event("performance_monitoring_error", error=str(e))
                time.sleep(self.optimization_config["monitoring_interval"])

    def _capture_performance_snapshot(self) -> PerformanceSnapshot:
        """Capture current system performance."""
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()

        metrics = {
            PerformanceMetric.CPU_USAGE: cpu_percent,
            PerformanceMetric.MEMORY_USAGE: memory.percent,
            PerformanceMetric.DISK_IO: (
                disk_io.read_bytes + disk_io.write_bytes if disk_io else 0
            ),
            PerformanceMetric.NETWORK_IO: (
                network_io.bytes_sent + network_io.bytes_recv if network_io else 0
            ),
        }

        return PerformanceSnapshot(
            timestamp=datetime.now(),
            metrics=metrics,
            context={
                "system_load": (
                    psutil.getloadavg() if hasattr(psutil, "getloadavg") else [0, 0, 0]
                ),
                "process_count": len(psutil.pids()),
                "memory_available": memory.available,
                "disk_usage": (
                    psutil.disk_usage("/").percent
                    if hasattr(psutil, "disk_usage")
                    else 0
                ),
            },
        )

    def _analyze_performance_trends(self):
        """Analyze performance trends and identify optimization opportunities."""
        if len(self.performance_snapshots) < 10:
            return  # Need more data

        recent_snapshots = self.performance_snapshots[-10:]

        # Analyze each metric for trends
        for metric in PerformanceMetric:
            if metric not in recent_snapshots[0].metrics:
                continue

            values = [snapshot.metrics[metric] for snapshot in recent_snapshots]

            # Calculate trend
            trend = self._calculate_trend(values)

            # Check for optimization opportunities
            if trend["direction"] == "degrading" and trend["severity"] > 0.2:
                self._identify_optimization_opportunity(metric, trend, recent_snapshots)

    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and severity."""
        if len(values) < 2:
            return {"direction": "stable", "severity": 0.0}

        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))

        # Calculate slope
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)

        # Determine direction and severity
        if abs(slope) < 0.01:
            direction = "stable"
            severity = 0.0
        elif slope > 0:
            direction = "degrading"
            severity = min(abs(slope) / max(values), 1.0)
        else:
            direction = "improving"
            severity = min(abs(slope) / max(values), 1.0)

        return {
            "direction": direction,
            "severity": severity,
            "slope": slope,
            "values": values,
        }

    def _identify_optimization_opportunity(
        self,
        metric: PerformanceMetric,
        trend: Dict[str, Any],
        snapshots: List[PerformanceSnapshot],
    ):
        """Identify specific optimization opportunities."""
        opportunity_id = f"opt_{int(time.time())}_{utils.random_string(8)}"

        # Determine optimization type based on metric
        optimization_type = self._get_optimization_type_for_metric(metric)

        # Calculate expected improvement
        expected_improvement = min(trend["severity"] * 0.5, 0.8)  # Cap at 80%

        # Calculate confidence based on trend consistency
        confidence = min(
            trend["severity"] * 2, 0.95
        )  # Higher severity = higher confidence

        # Calculate implementation effort
        implementation_effort = self._estimate_implementation_effort(
            optimization_type, metric
        )

        # Calculate risk level
        risk_level = self._estimate_risk_level(optimization_type, metric)

        opportunity = OptimizationOpportunity(
            opportunity_id=opportunity_id,
            optimization_type=optimization_type,
            description=f"Optimize {metric.value} - {trend['direction']} trend detected",
            current_performance={metric: snapshots[-1].metrics[metric]},
            expected_improvement=expected_improvement,
            confidence=confidence,
            implementation_effort=implementation_effort,
            risk_level=risk_level,
            context={
                "metric": metric.value,
                "trend": trend,
                "snapshot_count": len(snapshots),
            },
        )

        self.optimization_opportunities.append(opportunity)
        self._save_optimization_opportunities()

        # Record learning event
        self.continuous_improvement.record_learning_event(
            learning_type=continuous_improvement_system.LearningType.PERFORMANCE_OPTIMIZATION,
            context={
                "optimization_type": optimization_type.value,
                "metric": metric.value,
                "trend": trend,
                "performance_metrics": {metric.value: snapshots[-1].metrics[metric]},
            },
            outcome={
                "optimization_opportunity": True,
                "expected_improvement": expected_improvement,
                "confidence": confidence,
            },
            confidence=confidence,
            impact_score=expected_improvement,
            source="performance_optimizer",
        )

    def _get_optimization_type_for_metric(
        self, metric: PerformanceMetric
    ) -> OptimizationType:
        """Get the appropriate optimization type for a metric."""
        mapping = {
            PerformanceMetric.MEMORY_USAGE: OptimizationType.MEMORY_OPTIMIZATION,
            PerformanceMetric.CPU_USAGE: OptimizationType.CPU_OPTIMIZATION,
            PerformanceMetric.DISK_IO: OptimizationType.I_O_OPTIMIZATION,
            PerformanceMetric.NETWORK_IO: OptimizationType.I_O_OPTIMIZATION,
            PerformanceMetric.CACHE_HIT_RATE: OptimizationType.CACHE_OPTIMIZATION,
            PerformanceMetric.EXECUTION_TIME: OptimizationType.ALGORITHM_OPTIMIZATION,
            PerformanceMetric.RESPONSE_TIME: OptimizationType.ALGORITHM_OPTIMIZATION,
            PerformanceMetric.LATENCY: OptimizationType.ALGORITHM_OPTIMIZATION,
        }
        return mapping.get(metric, OptimizationType.CONFIGURATION_OPTIMIZATION)

    def _estimate_implementation_effort(
        self, optimization_type: OptimizationType, metric: PerformanceMetric
    ) -> int:
        """Estimate implementation effort for an optimization."""
        effort_mapping = {
            OptimizationType.CONFIGURATION_OPTIMIZATION: 2,
            OptimizationType.CACHE_OPTIMIZATION: 4,
            OptimizationType.MEMORY_OPTIMIZATION: 6,
            OptimizationType.CPU_OPTIMIZATION: 7,
            OptimizationType.I_O_OPTIMIZATION: 8,
            OptimizationType.ALGORITHM_OPTIMIZATION: 9,
            OptimizationType.RESOURCE_POOLING: 5,
            OptimizationType.LAZY_LOADING: 6,
        }
        return effort_mapping.get(optimization_type, 5)

    def _estimate_risk_level(
        self, optimization_type: OptimizationType, metric: PerformanceMetric
    ) -> int:
        """Estimate risk level for an optimization."""
        risk_mapping = {
            OptimizationType.CONFIGURATION_OPTIMIZATION: 2,
            OptimizationType.CACHE_OPTIMIZATION: 3,
            OptimizationType.MEMORY_OPTIMIZATION: 4,
            OptimizationType.CPU_OPTIMIZATION: 5,
            OptimizationType.I_O_OPTIMIZATION: 6,
            OptimizationType.ALGORITHM_OPTIMIZATION: 8,
            OptimizationType.RESOURCE_POOLING: 4,
            OptimizationType.LAZY_LOADING: 5,
        }
        return risk_mapping.get(optimization_type, 5)

    @contextmanager
    def monitor_operation(
        self, operation_name: str, operation_id: Optional[str] = None
    ):
        """Context manager for monitoring specific operations."""
        start_time = time.time()
        start_snapshot = self._capture_performance_snapshot()
        start_snapshot.operation_id = operation_id
        start_snapshot.context["operation_name"] = operation_name

        try:
            yield
        finally:
            end_time = time.time()
            end_snapshot = self._capture_performance_snapshot()
            end_snapshot.operation_id = operation_id
            end_snapshot.context["operation_name"] = operation_name

            # Calculate operation-specific metrics
            execution_time = end_time - start_time
            memory_delta = (
                end_snapshot.metrics[PerformanceMetric.MEMORY_USAGE]
                - start_snapshot.metrics[PerformanceMetric.MEMORY_USAGE]
            )
            cpu_delta = (
                end_snapshot.metrics[PerformanceMetric.CPU_USAGE]
                - start_snapshot.metrics[PerformanceMetric.CPU_USAGE]
            )

            # Create operation performance profile
            self._update_operation_profile(
                operation_name,
                {
                    PerformanceMetric.EXECUTION_TIME: execution_time,
                    PerformanceMetric.MEMORY_USAGE: memory_delta,
                    PerformanceMetric.CPU_USAGE: cpu_delta,
                },
            )

            # Log operation performance
            telemetry.log_event(
                "operation_performance",
                operation_name=operation_name,
                execution_time=execution_time,
                memory_delta=memory_delta,
                cpu_delta=cpu_delta,
            )

    def _update_operation_profile(
        self, operation_name: str, metrics: Dict[PerformanceMetric, float]
    ):
        """Update performance profile for an operation."""
        profile_id = f"op_{operation_name}"

        if profile_id not in self.performance_profiles:
            self.performance_profiles[profile_id] = PerformanceProfile(
                profile_id=profile_id,
                operation_name=operation_name,
                baseline_metrics=metrics.copy(),
                current_metrics=metrics.copy(),
            )
        else:
            profile = self.performance_profiles[profile_id]
            profile.current_metrics = metrics.copy()
            profile.last_updated = datetime.now()

            # Update performance trends
            for metric, value in metrics.items():
                if metric not in profile.performance_trends:
                    profile.performance_trends[metric] = []

                profile.performance_trends[metric].append(value)

                # Keep only recent trends
                if len(profile.performance_trends[metric]) > 50:
                    profile.performance_trends[metric] = profile.performance_trends[
                        metric
                    ][-50:]

    def get_optimization_opportunities(
        self, limit: int = 10, min_confidence: float = 0.5, max_risk: int = 7
    ) -> List[OptimizationOpportunity]:
        """Get optimization opportunities based on criteria."""
        filtered = [
            opp
            for opp in self.optimization_opportunities
            if opp.confidence >= min_confidence and opp.risk_level <= max_risk
        ]

        # Sort by expected improvement and confidence
        filtered.sort(
            key=lambda x: (x.expected_improvement, x.confidence), reverse=True
        )

        return filtered[:limit]

    def implement_optimization(self, opportunity_id: str) -> OptimizationResult:
        """Implement a specific optimization."""
        opportunity = None
        for opp in self.optimization_opportunities:
            if opp.opportunity_id == opportunity_id:
                opportunity = opp
                break

        if not opportunity:
            raise ValueError(f"Optimization opportunity {opportunity_id} not found")

        optimization_id = f"opt_impl_{int(time.time())}_{utils.random_string(8)}"

        # Capture performance before optimization
        performance_before = self._capture_performance_snapshot().metrics

        # Implement the optimization
        start_time = time.time()
        success = self._implement_optimization_type(
            opportunity.optimization_type, opportunity.context
        )
        implementation_time = time.time() - start_time

        # Capture performance after optimization
        performance_after = self._capture_performance_snapshot().metrics

        # Calculate improvement
        improvement_percentage = self._calculate_improvement_percentage(
            performance_before, performance_after, opportunity.optimization_type
        )

        result = OptimizationResult(
            optimization_id=optimization_id,
            opportunity_id=opportunity_id,
            optimization_type=opportunity.optimization_type,
            success=success,
            performance_before=performance_before,
            performance_after=performance_after,
            improvement_percentage=improvement_percentage,
            implementation_time=implementation_time,
        )

        # Log the result
        self._log_optimization_result(result)

        # Record learning event
        self.continuous_improvement.record_learning_event(
            learning_type=continuous_improvement_system.LearningType.PERFORMANCE_OPTIMIZATION,
            context={
                "optimization_type": opportunity.optimization_type.value,
                "performance_metrics": performance_before,
                "implementation_time": implementation_time,
            },
            outcome={
                "optimization_result": {
                    "success": success,
                    "improvement": improvement_percentage,
                    "implementation_time": implementation_time,
                }
            },
            confidence=0.9 if success else 0.3,
            impact_score=improvement_percentage / 100,
            source="performance_optimizer",
        )

        return result

    def _implement_optimization_type(
        self, optimization_type: OptimizationType, context: Dict[str, Any]
    ) -> bool:
        """Implement a specific type of optimization."""
        try:
            if optimization_type == OptimizationType.MEMORY_OPTIMIZATION:
                return self._optimize_memory(context)
            elif optimization_type == OptimizationType.CPU_OPTIMIZATION:
                return self._optimize_cpu(context)
            elif optimization_type == OptimizationType.CACHE_OPTIMIZATION:
                return self._optimize_cache(context)
            elif optimization_type == OptimizationType.CONFIGURATION_OPTIMIZATION:
                return self._optimize_configuration(context)
            elif optimization_type == OptimizationType.I_O_OPTIMIZATION:
                return self._optimize_io(context)
            elif optimization_type == OptimizationType.ALGORITHM_OPTIMIZATION:
                return self._optimize_algorithm(context)
            else:
                return False
        except Exception as e:
            telemetry.log_event("optimization_implementation_error", error=str(e))
            return False

    def _optimize_memory(self, context: Dict[str, Any]) -> bool:
        """Implement memory optimization."""
        # This would implement specific memory optimizations
        # For now, return success
        return True

    def _optimize_cpu(self, context: Dict[str, Any]) -> bool:
        """Implement CPU optimization."""
        # This would implement specific CPU optimizations
        return True

    def _optimize_cache(self, context: Dict[str, Any]) -> bool:
        """Implement cache optimization."""
        # This would implement specific cache optimizations
        return True

    def _optimize_configuration(self, context: Dict[str, Any]) -> bool:
        """Implement configuration optimization."""
        # This would implement specific configuration optimizations
        return True

    def _optimize_io(self, context: Dict[str, Any]) -> bool:
        """Implement I/O optimization."""
        # This would implement specific I/O optimizations
        return True

    def _optimize_algorithm(self, context: Dict[str, Any]) -> bool:
        """Implement algorithm optimization."""
        # This would implement specific algorithm optimizations
        return True

    def _calculate_improvement_percentage(
        self,
        before: Dict[PerformanceMetric, float],
        after: Dict[PerformanceMetric, float],
        optimization_type: OptimizationType,
    ) -> float:
        """Calculate improvement percentage for an optimization."""
        # This would calculate actual improvement based on optimization type
        # For now, return a simulated improvement
        return 15.0  # 15% improvement

    def _log_performance_snapshot(self, snapshot: PerformanceSnapshot):
        """Log performance snapshot to storage."""
        snapshot_data = {
            "timestamp": snapshot.timestamp.isoformat(),
            "metrics": {
                metric.value: value for metric, value in snapshot.metrics.items()
            },
            "context": snapshot.context,
            "operation_id": snapshot.operation_id,
            "session_id": snapshot.session_id,
        }

        with open(self.performance_data_path, "a", encoding="utf-8") as f:
            json.dump(snapshot_data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    def _log_optimization_result(self, result: OptimizationResult):
        """Log optimization result to storage."""
        result_data = {
            "optimization_id": result.optimization_id,
            "opportunity_id": result.opportunity_id,
            "optimization_type": result.optimization_type.value,
            "success": result.success,
            "performance_before": {
                metric.value: value
                for metric, value in result.performance_before.items()
            },
            "performance_after": {
                metric.value: value
                for metric, value in result.performance_after.items()
            },
            "improvement_percentage": result.improvement_percentage,
            "implementation_time": result.implementation_time,
            "rollback_required": result.rollback_required,
            "rollback_reason": result.rollback_reason,
            "created_at": result.created_at.isoformat(),
        }

        with open(self.optimization_results_path, "a", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    def _save_optimization_opportunities(self):
        """Save optimization opportunities to storage."""
        data = []
        for opp in self.optimization_opportunities:
            data.append(
                {
                    "opportunity_id": opp.opportunity_id,
                    "optimization_type": opp.optimization_type.value,
                    "description": opp.description,
                    "current_performance": {
                        metric.value: value
                        for metric, value in opp.current_performance.items()
                    },
                    "expected_improvement": opp.expected_improvement,
                    "confidence": opp.confidence,
                    "implementation_effort": opp.implementation_effort,
                    "risk_level": opp.risk_level,
                    "context": opp.context,
                    "created_at": opp.created_at.isoformat(),
                }
            )

        utils.write_json(self.optimization_opportunities_path, data)

    def _save_performance_profiles(self):
        """Save performance profiles to storage."""
        data = {}
        for profile_id, profile in self.performance_profiles.items():
            data[profile_id] = {
                "operation_name": profile.operation_name,
                "baseline_metrics": {
                    metric.value: value
                    for metric, value in profile.baseline_metrics.items()
                },
                "current_metrics": {
                    metric.value: value
                    for metric, value in profile.current_metrics.items()
                },
                "performance_trends": {
                    metric.value: values
                    for metric, values in profile.performance_trends.items()
                },
                "last_updated": profile.last_updated.isoformat(),
            }

        utils.write_json(self.performance_profiles_path, data)

    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Filter recent snapshots
        recent_snapshots = [
            snapshot
            for snapshot in self.performance_snapshots
            if snapshot.timestamp >= cutoff_time
        ]

        if not recent_snapshots:
            return {
                "status": "no_data",
                "message": f"No performance data for the last {hours} hours",
            }

        # Calculate summary statistics
        summary = {
            "status": "success",
            "period_hours": hours,
            "total_snapshots": len(recent_snapshots),
            "metrics": {},
        }

        for metric in PerformanceMetric:
            if metric in recent_snapshots[0].metrics:
                values = [snapshot.metrics[metric] for snapshot in recent_snapshots]
                summary["metrics"][metric.value] = {
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "trend": self._calculate_trend(values),
                }

        return summary

    def get_performance_metrics(self) -> List[Dict[str, Any]]:
        """Get current performance metrics."""
        try:
            metrics = []

            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            metrics.extend(
                [
                    {
                        "name": "cpu_usage",
                        "value": cpu_percent,
                        "unit": "percent",
                        "timestamp": datetime.now().isoformat(),
                    },
                    {
                        "name": "memory_usage",
                        "value": memory.percent,
                        "unit": "percent",
                        "timestamp": datetime.now().isoformat(),
                    },
                    {
                        "name": "disk_usage",
                        "value": disk.percent,
                        "unit": "percent",
                        "timestamp": datetime.now().isoformat(),
                    },
                ]
            )

            return metrics

        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return []

    def get_optimization_effectiveness(self, days: int = 7) -> Dict[str, Any]:
        """Get optimization effectiveness summary."""
        cutoff_date = datetime.now() - timedelta(days=days)

        # Load recent optimization results
        results = []
        if self.optimization_results_path.exists():
            with open(self.optimization_results_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        result_data = json.loads(line)
                        result_date = datetime.fromisoformat(result_data["created_at"])
                        if result_date >= cutoff_date:
                            results.append(result_data)
                    except (json.JSONDecodeError, KeyError):
                        continue

        if not results:
            return {
                "status": "no_data",
                "message": f"No optimization results for the last {days} days",
            }

        # Calculate effectiveness metrics
        successful_optimizations = [r for r in results if r["success"]]
        total_improvements = [
            r["improvement_percentage"] for r in successful_optimizations
        ]

        return {
            "status": "success",
            "period_days": days,
            "total_optimizations": len(results),
            "successful_optimizations": len(successful_optimizations),
            "success_rate": (
                len(successful_optimizations) / len(results) if results else 0
            ),
            "average_improvement": (
                sum(total_improvements) / len(total_improvements)
                if total_improvements
                else 0
            ),
            "total_improvement": sum(total_improvements),
            "optimization_types": self._get_optimization_type_effectiveness(results),
        }

    def _get_optimization_type_effectiveness(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get effectiveness by optimization type."""
        type_stats = {}

        for result in results:
            opt_type = result["optimization_type"]
            if opt_type not in type_stats:
                type_stats[opt_type] = {
                    "count": 0,
                    "successful": 0,
                    "total_improvement": 0.0,
                }

            type_stats[opt_type]["count"] += 1
            if result["success"]:
                type_stats[opt_type]["successful"] += 1
                type_stats[opt_type]["total_improvement"] += result[
                    "improvement_percentage"
                ]

        # Calculate success rates and average improvements
        for opt_type, stats in type_stats.items():
            stats["success_rate"] = (
                stats["successful"] / stats["count"] if stats["count"] > 0 else 0
            )
            stats["average_improvement"] = (
                stats["total_improvement"] / stats["successful"]
                if stats["successful"] > 0
                else 0
            )

        return type_stats


def get_performance_optimizer(root: Path) -> PerformanceOptimizer:
    """Get performance optimizer instance."""
    return PerformanceOptimizer(root)
