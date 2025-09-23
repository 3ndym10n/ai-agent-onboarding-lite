"""
Unified Metrics Collection System - Central hub for all metrics collection.

This module provides a comprehensive, high - performance metrics collection system that:
- Unifies all metrics collection into a single entry point
- Provides real - time processing and alerting capabilities
- Generates actionable insights and recommendations
- Ensures privacy and security of collected data
- Scales efficiently with system growth
"""

import threading
import time
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from . import telemetry, utils


class MetricSource(Enum):
    """Sources of metrics."""

    SYSTEM = "system"
    USER = "user"
    PERFORMANCE = "performance"
    LEARNING = "learning"
    BUSINESS = "business"
    SECURITY = "security"


class MetricCategory(Enum):
    """Categories of metrics."""

    HEALTH = "health"
    TIMING = "timing"
    INTERACTION = "interaction"
    CONFIDENCE = "confidence"
    ADOPTION = "adoption"
    ERROR = "error"
    RESOURCE = "resource"

@dataclass

class MetricEvent:
    """A single metric event."""

    name: str
    value: Union[float, int]
    source: MetricSource
    category: MetricCategory
    timestamp: datetime = field(default_factory=datetime.now)
    unit: Optional[str] = None
    dimensions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None


    def __post_init__(self):
        if self.id is None:
            self.id = f"metric_{int(time.time())}_{utils.random_string(8)}"

@dataclass

class MetricQuery:
    """Query parameters for metric retrieval."""

    name_pattern: Optional[str] = None
    source: Optional[MetricSource] = None
    category: Optional[MetricCategory] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    dimensions: Dict[str, Any] = field(default_factory=dict)
    limit: int = 1000
    aggregation: Optional[str] = None  # sum, avg, min, max, count

@dataclass

class MetricResult:
    """Result of a metric query."""

    metrics: List[MetricEvent]
    total_count: int
    aggregated_value: Optional[float] = None
    query_time_ms: float = 0.0

@dataclass

class MetricAlert:
    """A metric - based alert."""

    alert_id: str
    metric_name: str
    condition: str
    threshold: float
    current_value: float
    severity: str  # low, medium, high, critical
    timestamp: datetime
    description: str
    suggested_actions: List[str] = field(default_factory=list)


class UnifiedMetricsCollector:
    """Central hub for all metrics collection and analysis."""


    def __init__(self, root: Path):
        self.root = root
        self.metrics_path = root / ".ai_onboard" / "unified_metrics.jsonl"
        self.alerts_path = root / ".ai_onboard" / "metric_alerts.jsonl"
        self.config_path = root / ".ai_onboard" / "metrics_config.json"

        # In - memory storage for hot data (last 7 days)
        self.hot_metrics: deque = deque(maxlen=10000)  # Last 10k metrics
        self.metric_index: Dict[str, List[MetricEvent]] = defaultdict(list)

        # Threading for async processing
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="metrics")
        self.processing_lock = threading.Lock()

        # Alert thresholds and rules
        self.alert_rules: Dict[str, Dict] = {}
        self.active_alerts: Dict[str, MetricAlert] = {}

        # Performance tracking
        self.collection_stats = {
            "total_collected": 0,
            "collection_errors": 0,
            "avg_collection_time_ms": 0.0,
            "last_collection_time": None,
        }

        # Ensure directories exist
        utils.ensure_dir(self.metrics_path.parent)

        # Load configuration
        self._load_config()

        # Load existing metrics into hot storage
        self._load_existing_metrics()

        # Start background processing
        self._start_background_processing()


    def _load_config(self):
        """Load metrics collection configuration."""
        default_config = {
            "collection_enabled": True,
            "batch_size": 100,
            "flush_interval_seconds": 30,
            "hot_storage_days": 7,
            "alert_rules": {
                "cpu_usage": {"threshold": 90.0, "condition": ">", "severity": "high"},
                "memory_usage": {
                    "threshold": 85.0,
                    "condition": ">",
                    "severity": "medium",
                },
                "error_rate": {
                    "threshold": 0.05,
                    "condition": ">",
                    "severity": "critical",
                },
                "response_time": {
                    "threshold": 5000.0,
                    "condition": ">",
                    "severity": "medium",
                },
            },
            "privacy": {
                "anonymize_user_ids": True,
                "retention_days": 90,
                "sensitive_fields": ["user_id", "session_id", "ip_address"],
            },
        }

        self.config = utils.read_json(self.config_path, default=default_config)
        self.alert_rules = self.config.get("alert_rules", {})


    def _load_existing_metrics(self):
        """Load existing metrics from storage into hot storage for recent data."""
        if not self.metrics_path.exists():
            return

        try:
            # Load recent metrics (last 7 days) into hot storage
            cutoff_time = datetime.now() - timedelta(days=7)
            loaded_count = 0

            with open(self.metrics_path, "r", encoding="utf - 8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        metric_data = json.loads(line)

                        # Parse timestamp
                        timestamp_str = metric_data.get("timestamp")
                        if timestamp_str:
                            metric_timestamp = datetime.fromisoformat(
                                timestamp_str.replace("Z", "+00:00")
                            )

                            # Only load recent metrics
                            if metric_timestamp >= cutoff_time:
                                # Create MetricEvent from stored data
                                metric = MetricEvent(
                                    name=metric_data["name"],
                                    value=metric_data["value"],
                                    source=MetricSource(
                                        metric_data.get("source", "system")
                                    ),
                                    category=MetricCategory(
                                        metric_data.get("category", "health")
                                    ),
                                    timestamp=metric_timestamp,
                                    unit=metric_data.get("unit"),
                                    dimensions=metric_data.get("dimensions", {}),
                                    metadata=metric_data.get("metadata", {}),
                                )

                                # Add to hot storage and index
                                self.hot_metrics.append(metric)
                                self.metric_index[metric.name].append(metric)
                                loaded_count += 1

                    except (json.JSONDecodeError, ValueError, KeyError) as e:
                        # Skip malformed entries
                        continue

            # Update collection stats
            self.collection_stats["total_collected"] = loaded_count

            if loaded_count > 0:
                print(f"📊 Loaded {loaded_count} recent metrics into hot storage")

        except Exception as e:
            print(f"Warning: Failed to load existing metrics: {e}")


    def collect_metric(self, metric: MetricEvent) -> str:
        """Collect a single metric event."""
        if not self.config.get("collection_enabled", True):
            return metric.id

        start_time = time.time()

        try:
            # Anonymize sensitive data if configured
            if self.config.get("privacy", {}).get("anonymize_user_ids", False):
                self._anonymize_metric(metric)

            # Add to hot storage
            with self.processing_lock:
                self.hot_metrics.append(metric)
                self.metric_index[metric.name].append(metric)

                # Limit index size per metric name
                if len(self.metric_index[metric.name]) > 1000:
                    self.metric_index[metric.name] = self.metric_index[metric.name][
                        -500:
                    ]

            # Async processing (alerts, persistence)
            self.executor.submit(self._process_metric_async, metric)

            # Update collection stats
            collection_time = (time.time() - start_time) * 1000
            self._update_collection_stats(collection_time, success=True)

            return metric.id

        except Exception as e:
            self._update_collection_stats(0, success=False)
            telemetry.log_event(
                "metric_collection_error", error=str(e), metric_name=metric.name
            )
            return metric.id


    def batch_collect(self, metrics: List[MetricEvent]) -> List[str]:
        """High - performance batch collection of multiple metrics."""
        if not metrics or not self.config.get("collection_enabled", True):
            return [m.id for m in metrics]

        start_time = time.time()
        collected_ids = []

        try:
            # Process all metrics
            processed_metrics = []
            for metric in metrics:
                if self.config.get("privacy", {}).get("anonymize_user_ids", False):
                    self._anonymize_metric(metric)
                processed_metrics.append(metric)
                collected_ids.append(metric.id)

            # Batch add to hot storage
            with self.processing_lock:
                self.hot_metrics.extend(processed_metrics)
                for metric in processed_metrics:
                    self.metric_index[metric.name].append(metric)

                    # Limit index size
                    if len(self.metric_index[metric.name]) > 1000:
                        self.metric_index[metric.name] = self.metric_index[metric.name][
                            -500:
                        ]

            # Async batch processing
            self.executor.submit(self._process_metrics_batch_async, processed_metrics)

            # Update stats
            batch_time = (time.time() - start_time) * 1000
            self._update_collection_stats(batch_time / len(metrics), success=True)

            return collected_ids

        except Exception as e:
            self._update_collection_stats(0, success=False)
            telemetry.log_event(
                "metric_batch_collection_error", error=str(e), batch_size=len(metrics)
            )
            return collected_ids


    def query_metrics(self, query: MetricQuery) -> MetricResult:
        """Query collected metrics with filtering and aggregation."""
        start_time = time.time()

        try:
            # Search in hot storage first
            matching_metrics = []

            with self.processing_lock:
                search_pool = list(self.hot_metrics)

                # If specific metric name, use index for faster search
                if query.name_pattern and not any(
                    c in query.name_pattern for c in ["*", "?", "["]
                ):
                    search_pool = self.metric_index.get(query.name_pattern, [])

            # Apply filters
            for metric in search_pool:
                if self._matches_query(metric, query):
                    matching_metrics.append(metric)

            # Sort by timestamp (newest first)
            matching_metrics.sort(key=lambda m: m.timestamp, reverse=True)

            # Apply limit
            if query.limit:
                matching_metrics = matching_metrics[: query.limit]

            # Calculate aggregation if requested
            aggregated_value = None
            if query.aggregation and matching_metrics:
                values = [
                    m.value
                    for m in matching_metrics
                    if isinstance(m.value, (int, float))
                ]
                if values:
                    if query.aggregation == "sum":
                        aggregated_value = sum(values)
                    elif query.aggregation == "avg":
                        aggregated_value = sum(values) / len(values)
                    elif query.aggregation == "min":
                        aggregated_value = min(values)
                    elif query.aggregation == "max":
                        aggregated_value = max(values)
                    elif query.aggregation == "count":
                        aggregated_value = len(values)

            query_time = (time.time() - start_time) * 1000

            return MetricResult(
                metrics=matching_metrics,
                total_count=len(matching_metrics),
                aggregated_value=aggregated_value,
                query_time_ms=query_time,
            )

        except Exception as e:
            telemetry.log_event("metric_query_error", error=str(e))
            return MetricResult(
                metrics=[],
                total_count=0,
                query_time_ms=(time.time() - start_time) * 1000,
            )


    def get_collection_stats(self) -> Dict[str, Any]:
        """Get metrics collection performance statistics."""
        return {
            **self.collection_stats,
            "hot_storage_count": len(self.hot_metrics),
            "indexed_metrics": len(self.metric_index),
            "active_alerts": len(self.active_alerts),
            "config": self.config,
        }


    def _anonymize_metric(self, metric: MetricEvent):
        """Anonymize sensitive fields in metric data."""
        sensitive_fields = self.config.get("privacy", {}).get("sensitive_fields", [])

        for field_name in sensitive_fields:
            if field_name in metric.dimensions:
                # Hash the value for anonymization
                original_value = str(metric.dimensions[field_name])
                metric.dimensions[field_name] = (
                    f"hash_{hash(original_value) % 1000000:06d}"
                )

            if field_name in metric.metadata:
                original_value = str(metric.metadata[field_name])
                metric.metadata[field_name] = (
                    f"hash_{hash(original_value) % 1000000:06d}"
                )


    def _matches_query(self, metric: MetricEvent, query: MetricQuery) -> bool:
        """Check if a metric matches the query criteria."""
        # Name pattern matching
        if query.name_pattern:
            if "*" in query.name_pattern or "?" in query.name_pattern:
                import fnmatch

                if not fnmatch.fnmatch(metric.name, query.name_pattern):
                    return False
            else:
                if metric.name != query.name_pattern:
                    return False

        # Source filtering
        if query.source and metric.source != query.source:
            return False

        # Category filtering
        if query.category and metric.category != query.category:
            return False

        # Time range filtering
        if query.start_time and metric.timestamp < query.start_time:
            return False
        if query.end_time and metric.timestamp > query.end_time:
            return False

        # Dimension filtering
        for key, value in query.dimensions.items():
            if key not in metric.dimensions or metric.dimensions[key] != value:
                return False

        return True


    def _process_metric_async(self, metric: MetricEvent):
        """Async processing of a single metric (alerts, persistence)."""
        try:
            # Check for alert conditions
            self._check_alert_conditions(metric)

            # Persist to storage
            self._persist_metric(metric)

        except Exception as e:
            telemetry.log_event(
                "async_metric_processing_error", error=str(e), metric_id=metric.id
            )


    def _process_metrics_batch_async(self, metrics: List[MetricEvent]):
        """Async processing of metric batch."""
        try:
            # Check alerts for all metrics
            for metric in metrics:
                self._check_alert_conditions(metric)

            # Batch persist to storage
            self._persist_metrics_batch(metrics)

        except Exception as e:
            telemetry.log_event(
                "async_batch_processing_error", error=str(e), batch_size=len(metrics)
            )


    def _check_alert_conditions(self, metric: MetricEvent):
        """Check if metric triggers any alert conditions."""
        if metric.name not in self.alert_rules:
            return

        rule = self.alert_rules[metric.name]
        threshold = rule.get("threshold", 0)
        condition = rule.get("condition", ">")
        severity = rule.get("severity", "medium")

        # Evaluate condition
        triggered = False
        if condition == ">" and metric.value > threshold:
            triggered = True
        elif condition == "<" and metric.value < threshold:
            triggered = True
        elif condition == ">=" and metric.value >= threshold:
            triggered = True
        elif condition == "<=" and metric.value <= threshold:
            triggered = True
        elif condition == "==" and metric.value == threshold:
            triggered = True

        if triggered:
            alert = MetricAlert(
                alert_id=f"alert_{int(time.time())}_{utils.random_string(6)}",
                metric_name=metric.name,
                condition=f"{metric.name} {condition} {threshold}",
                threshold=threshold,
                current_value=metric.value,
                severity=severity,
                timestamp=metric.timestamp,
                description=f"Metric {metric.name} value {metric.value} {condition} threshold {threshold}",
                suggested_actions=self._generate_alert_actions(metric, rule),
            )

            self.active_alerts[alert.alert_id] = alert
            self._persist_alert(alert)

            telemetry.log_event(
                "metric_alert_triggered",
                alert_id=alert.alert_id,
                metric_name=metric.name,
                severity=severity,
                value=metric.value,
            )


    def _generate_alert_actions(self, metric: MetricEvent, rule: Dict) -> List[str]:
        """Generate suggested actions for an alert."""
        actions = []

        if metric.name == "cpu_usage":
            actions = [
                "Check for high CPU processes",
                "Consider scaling resources",
                "Review recent code changes for performance issues",
            ]
        elif metric.name == "memory_usage":
            actions = [
                "Check for memory leaks",
                "Review caching strategies",
                "Monitor garbage collection",
            ]
        elif metric.name == "error_rate":
            actions = [
                "Check error logs for patterns",
                "Review recent deployments",
                "Validate input handling",
            ]
        else:
            actions = [
                f"Investigate {metric.name} spike",
                "Check system logs",
                "Review recent changes",
            ]

        return actions


    def _persist_metric(self, metric: MetricEvent):
        """Persist a single metric to storage."""
        data = {
            "id": metric.id,
            "name": metric.name,
            "value": metric.value,
            "source": metric.source.value,
            "category": metric.category.value,
            "timestamp": metric.timestamp.isoformat(),
            "unit": metric.unit,
            "dimensions": metric.dimensions,
            "metadata": metric.metadata,
        }

        with open(self.metrics_path, "a", encoding="utf - 8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")


    def _persist_metrics_batch(self, metrics: List[MetricEvent]):
        """Persist a batch of metrics to storage."""
        with open(self.metrics_path, "a", encoding="utf - 8") as f:
            for metric in metrics:
                data = {
                    "id": metric.id,
                    "name": metric.name,
                    "value": metric.value,
                    "source": metric.source.value,
                    "category": metric.category.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "unit": metric.unit,
                    "dimensions": metric.dimensions,
                    "metadata": metric.metadata,
                }
                json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
                f.write("\n")


    def _persist_alert(self, alert: MetricAlert):
        """Persist an alert to storage."""
        data = {
            "alert_id": alert.alert_id,
            "metric_name": alert.metric_name,
            "condition": alert.condition,
            "threshold": alert.threshold,
            "current_value": alert.current_value,
            "severity": alert.severity,
            "timestamp": alert.timestamp.isoformat(),
            "description": alert.description,
            "suggested_actions": alert.suggested_actions,
        }

        with open(self.alerts_path, "a", encoding="utf - 8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")


    def _update_collection_stats(self, collection_time_ms: float, success: bool):
        """Update collection performance statistics."""
        if success:
            self.collection_stats["total_collected"] += 1

            # Update rolling average
            current_avg = self.collection_stats["avg_collection_time_ms"]
            total = self.collection_stats["total_collected"]
            new_avg = ((current_avg * (total - 1)) + collection_time_ms) / total
            self.collection_stats["avg_collection_time_ms"] = new_avg
        else:
            self.collection_stats["collection_errors"] += 1

        self.collection_stats["last_collection_time"] = datetime.now().isoformat()


    def _start_background_processing(self):
        """Start background processing tasks."""

        # Periodic cleanup of old hot storage data

        def cleanup_hot_storage():
            cutoff_time = datetime.now() - timedelta(
                days=self.config.get("hot_storage_days", 7)
            )

            with self.processing_lock:
                # Remove old metrics from hot storage
                self.hot_metrics = deque(
                    [m for m in self.hot_metrics if m.timestamp > cutoff_time],
                    maxlen=self.hot_metrics.maxlen,
                )

                # Clean up metric index
                for metric_name in list(self.metric_index.keys()):
                    self.metric_index[metric_name] = [
                        m
                        for m in self.metric_index[metric_name]
                        if m.timestamp > cutoff_time
                    ]
                    if not self.metric_index[metric_name]:
                        del self.metric_index[metric_name]

        # Schedule periodic cleanup (every hour)
        import threading


        def periodic_cleanup():
            while True:
                time.sleep(3600)  # 1 hour
                try:
                    cleanup_hot_storage()
                except Exception as e:
                    telemetry.log_event("cleanup_error", error=str(e))

        cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
        cleanup_thread.start()

# Global instance
_metrics_collector: Optional[UnifiedMetricsCollector] = None


def get_unified_metrics_collector(root: Path) -> UnifiedMetricsCollector:
    """Get the global unified metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = UnifiedMetricsCollector(root)
    return _metrics_collector

# Convenience functions for common metric types

def collect_performance_metric(
    name: str, value: float, unit: str = "ms", **dimensions
) -> str:
    """Collect a performance timing metric."""
    collector = get_unified_metrics_collector(Path.cwd())
    metric = MetricEvent(
        name=name,
        value=value,
        source=MetricSource.PERFORMANCE,
        category=MetricCategory.TIMING,
        unit=unit,
        dimensions=dimensions,
    )
    return collector.collect_metric(metric)


def collect_user_metric(
    name: str, value: float, unit: str = "score", **dimensions
) -> str:
    """Collect a user experience metric."""
    collector = get_unified_metrics_collector(Path.cwd())
    metric = MetricEvent(
        name=name,
        value=value,
        source=MetricSource.USER,
        category=MetricCategory.INTERACTION,
        unit=unit,
        dimensions=dimensions,
    )
    return collector.collect_metric(metric)


def collect_system_metric(
    name: str, value: float, unit: str = "%", **dimensions
) -> str:
    """Collect a system health metric."""
    collector = get_unified_metrics_collector(Path.cwd())
    metric = MetricEvent(
        name=name,
        value=value,
        source=MetricSource.SYSTEM,
        category=MetricCategory.HEALTH,
        unit=unit,
        dimensions=dimensions,
    )
    return collector.collect_metric(metric)
