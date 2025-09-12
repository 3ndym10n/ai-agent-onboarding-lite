"""
Continuous Improvement Analytics and Reporting System.

This module provides comprehensive analytics and reporting capabilities for the continuous improvement system:
- Performance metrics and KPIs tracking
- Trend analysis and forecasting
- Custom report generation
- Dashboard data aggregation
- Export capabilities for various formats
- Real-time monitoring and alerts
"""

import csv
import io
import json
import statistics
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from . import continuous_improvement_system, telemetry, utils


class ReportType(Enum):
    """Types of reports that can be generated."""

    PERFORMANCE_SUMMARY = "performance_summary"
    LEARNING_ANALYTICS = "learning_analytics"
    RECOMMENDATION_EFFECTIVENESS = "recommendation_effectiveness"
    SYSTEM_HEALTH = "system_health"
    KNOWLEDGE_BASE_GROWTH = "knowledge_base_growth"
    USER_SATISFACTION = "user_satisfaction"
    TREND_ANALYSIS = "trend_analysis"
    CUSTOM = "custom"


class MetricType(Enum):
    """Types of metrics tracked."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


class AlertLevel(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class Metric:
    """A single metric measurement."""

    metric_id: str
    metric_type: MetricType
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KPI:
    """A Key Performance Indicator."""

    kpi_id: str
    name: str
    description: str
    current_value: float
    target_value: float
    unit: str
    trend: str  # "up", "down", "stable"
    last_updated: datetime
    historical_values: List[Tuple[datetime, float]] = field(default_factory=list)
    alerts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Report:
    """A generated report."""

    report_id: str
    report_type: ReportType
    title: str
    description: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    data: Dict[str, Any]
    summary: str
    recommendations: List[str] = field(default_factory=list)
    charts: List[Dict[str, Any]] = field(default_factory=list)
    export_formats: List[str] = field(default_factory=list)


@dataclass
class Alert:
    """A system alert."""

    alert_id: str
    alert_level: AlertLevel
    title: str
    description: str
    metric_name: str
    current_value: float
    threshold_value: float
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContinuousImprovementAnalytics:
    """Comprehensive analytics and reporting system for continuous improvement."""

    def __init__(self, root: Path):
        self.root = root
        self.metrics_path = root / ".ai_onboard" / "analytics_metrics.jsonl"
        self.kpis_path = root / ".ai_onboard" / "analytics_kpis.json"
        self.reports_path = root / ".ai_onboard" / "analytics_reports.jsonl"
        self.alerts_path = root / ".ai_onboard" / "analytics_alerts.jsonl"
        self.analytics_config_path = root / ".ai_onboard" / "analytics_config.json"

        # Initialize subsystems
        self.continuous_improvement = (
            continuous_improvement_system.get_continuous_improvement_system(root)
        )

        # Analytics state
        self.metrics: List[Metric] = []
        self.kpis: Dict[str, KPI] = {}
        self.reports: List[Report] = []
        self.alerts: List[Alert] = []

        # Analytics configuration
        self.analytics_config = self._load_analytics_config()
        self.kpi_definitions = self._get_kpi_definitions()

        # Ensure directories exist
        self._ensure_directories()

        # Load existing data
        self._load_metrics()
        self._load_kpis()
        self._load_reports()
        self._load_alerts()

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for path in [
            self.metrics_path,
            self.kpis_path,
            self.reports_path,
            self.alerts_path,
            self.analytics_config_path,
        ]:
            utils.ensure_dir(path.parent)

    def _load_analytics_config(self) -> Dict[str, Any]:
        """Load analytics configuration."""
        return utils.read_json(
            self.analytics_config_path,
            default={
                "metrics_retention_days": 90,
                "kpi_update_interval_minutes": 15,
                "report_generation_enabled": True,
                "alerting_enabled": True,
                "dashboard_refresh_interval_seconds": 30,
                "export_formats": ["json", "csv", "html"],
                "kpi_thresholds": {
                    "learning_rate": {"warning": 0.1, "critical": 0.05},
                    "recommendation_acceptance_rate": {"warning": 0.6, "critical": 0.4},
                    "system_health_score": {"warning": 0.7, "critical": 0.5},
                    "user_satisfaction": {"warning": 0.7, "critical": 0.5},
                    "knowledge_growth_rate": {"warning": 0.05, "critical": 0.02},
                },
                "report_schedules": {
                    "daily": ["performance_summary", "system_health"],
                    "weekly": ["learning_analytics", "recommendation_effectiveness"],
                    "monthly": ["knowledge_base_growth", "trend_analysis"],
                },
            },
        )

    def _get_kpi_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get KPI definitions and calculations."""
        return {
            "learning_rate": {
                "name": "Learning Rate",
                "description": "Rate of new learning events per day",
                "unit": "events/day",
                "target": 10.0,
                "calculation": self._calculate_learning_rate,
            },
            "recommendation_acceptance_rate": {
                "name": "Recommendation Acceptance Rate",
                "description": "Percentage of recommendations that are accepted",
                "unit": "%",
                "target": 80.0,
                "calculation": self._calculate_recommendation_acceptance_rate,
            },
            "system_health_score": {
                "name": "System Health Score",
                "description": "Overall system health score",
                "unit": "score",
                "target": 90.0,
                "calculation": self._calculate_system_health_score,
            },
            "user_satisfaction": {
                "name": "User Satisfaction",
                "description": "Average user satisfaction score",
                "unit": "score",
                "target": 85.0,
                "calculation": self._calculate_user_satisfaction,
            },
            "knowledge_growth_rate": {
                "name": "Knowledge Growth Rate",
                "description": "Rate of knowledge base growth",
                "unit": "items/day",
                "target": 5.0,
                "calculation": self._calculate_knowledge_growth_rate,
            },
            "error_resolution_time": {
                "name": "Error Resolution Time",
                "description": "Average time to resolve errors",
                "unit": "minutes",
                "target": 30.0,
                "calculation": self._calculate_error_resolution_time,
            },
            "performance_improvement": {
                "name": "Performance Improvement",
                "description": "Percentage improvement in system performance",
                "unit": "%",
                "target": 15.0,
                "calculation": self._calculate_performance_improvement,
            },
        }

    def _load_metrics(self):
        """Load metrics from storage."""
        if not self.metrics_path.exists():
            return

        cutoff_date = datetime.now() - timedelta(
            days=self.analytics_config["metrics_retention_days"]
        )

        with open(self.metrics_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    metric_timestamp = datetime.fromisoformat(data["timestamp"])

                    # Skip old metrics
                    if metric_timestamp < cutoff_date:
                        continue

                    metric = Metric(
                        metric_id=data["metric_id"],
                        metric_type=MetricType(data["metric_type"]),
                        name=data["name"],
                        value=data["value"],
                        timestamp=metric_timestamp,
                        tags=data.get("tags", {}),
                        metadata=data.get("metadata", {}),
                    )
                    self.metrics.append(metric)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

    def _load_kpis(self):
        """Load KPIs from storage."""
        if not self.kpis_path.exists():
            return

        data = utils.read_json(self.kpis_path, default={})

        for kpi_id, kpi_data in data.items():
            historical_values = [
                (datetime.fromisoformat(timestamp), value)
                for timestamp, value in kpi_data.get("historical_values", [])
            ]

            kpi = KPI(
                kpi_id=kpi_id,
                name=kpi_data["name"],
                description=kpi_data["description"],
                current_value=kpi_data["current_value"],
                target_value=kpi_data["target_value"],
                unit=kpi_data["unit"],
                trend=kpi_data["trend"],
                last_updated=datetime.fromisoformat(kpi_data["last_updated"]),
                historical_values=historical_values,
                alerts=kpi_data.get("alerts", []),
            )
            self.kpis[kpi_id] = kpi

    def _load_reports(self):
        """Load reports from storage."""
        if not self.reports_path.exists():
            return

        with open(self.reports_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    report = Report(
                        report_id=data["report_id"],
                        report_type=ReportType(data["report_type"]),
                        title=data["title"],
                        description=data["description"],
                        generated_at=datetime.fromisoformat(data["generated_at"]),
                        period_start=datetime.fromisoformat(data["period_start"]),
                        period_end=datetime.fromisoformat(data["period_end"]),
                        data=data["data"],
                        summary=data["summary"],
                        recommendations=data.get("recommendations", []),
                        charts=data.get("charts", []),
                        export_formats=data.get("export_formats", []),
                    )
                    self.reports.append(report)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

    def _load_alerts(self):
        """Load alerts from storage."""
        if not self.alerts_path.exists():
            return

        with open(self.alerts_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    alert = Alert(
                        alert_id=data["alert_id"],
                        alert_level=AlertLevel(data["alert_level"]),
                        title=data["title"],
                        description=data["description"],
                        metric_name=data["metric_name"],
                        current_value=data["current_value"],
                        threshold_value=data["threshold_value"],
                        triggered_at=datetime.fromisoformat(data["triggered_at"]),
                        resolved_at=(
                            datetime.fromisoformat(data["resolved_at"])
                            if data.get("resolved_at")
                            else None
                        ),
                        acknowledged=data.get("acknowledged", False),
                        metadata=data.get("metadata", {}),
                    )
                    self.alerts.append(alert)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

    def collect_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        tags: Dict[str, str] = None,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Record a new metric."""
        metric_id = f"metric_{int(time.time())}_{utils.random_string(8)}"

        metric = Metric(
            metric_id=metric_id,
            metric_type=metric_type,
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            metadata=metadata or {},
        )

        self.metrics.append(metric)
        self._save_metric(metric)

        # Check for alerts
        self._check_metric_alerts(metric)

        # Update relevant KPIs
        self._update_related_kpis(metric)

        telemetry.log_event(
            "metric_recorded",
            metric_id=metric_id,
            name=name,
            value=value,
            metric_type=metric_type.value,
        )

        return metric_id

    def _save_metric(self, metric: Metric):
        """Save a metric to storage."""
        data = {
            "metric_id": metric.metric_id,
            "metric_type": metric.metric_type.value,
            "name": metric.name,
            "value": metric.value,
            "timestamp": metric.timestamp.isoformat(),
            "tags": metric.tags,
            "metadata": metric.metadata,
        }

        with open(self.metrics_path, "a", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    def _check_metric_alerts(self, metric: Metric):
        """Check if a metric triggers any alerts."""
        if not self.analytics_config["alerting_enabled"]:
            return

        # Check KPI thresholds
        for kpi_id, kpi_def in self.kpi_definitions.items():
            if kpi_def["name"].lower() in metric.name.lower():
                thresholds = self.analytics_config["kpi_thresholds"].get(kpi_id, {})

                for level, threshold in thresholds.items():
                    if metric.value <= threshold:
                        self._create_alert(
                            alert_level=(
                                AlertLevel.WARNING
                                if level == "warning"
                                else AlertLevel.CRITICAL
                            ),
                            title=f"{kpi_def['name']} Alert",
                            description=f"{kpi_def['name']} is {metric.value:.2f}, below {level} threshold of {threshold}",
                            metric_name=metric.name,
                            current_value=metric.value,
                            threshold_value=threshold,
                        )

    def _create_alert(
        self,
        alert_level: AlertLevel,
        title: str,
        description: str,
        metric_name: str,
        current_value: float,
        threshold_value: float,
        metadata: Dict[str, Any] = None,
    ):
        """Create a new alert."""
        alert_id = f"alert_{int(time.time())}_{utils.random_string(8)}"

        alert = Alert(
            alert_id=alert_id,
            alert_level=alert_level,
            title=title,
            description=description,
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            triggered_at=datetime.now(),
            metadata=metadata or {},
        )

        self.alerts.append(alert)
        self._save_alert(alert)

        telemetry.log_event(
            "alert_created",
            alert_id=alert_id,
            alert_level=alert_level.value,
            title=title,
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
        )

    def _save_alert(self, alert: Alert):
        """Save an alert to storage."""
        data = {
            "alert_id": alert.alert_id,
            "alert_level": alert.alert_level.value,
            "title": alert.title,
            "description": alert.description,
            "metric_name": alert.metric_name,
            "current_value": alert.current_value,
            "threshold_value": alert.threshold_value,
            "triggered_at": alert.triggered_at.isoformat(),
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "acknowledged": alert.acknowledged,
            "metadata": alert.metadata,
        }

        with open(self.alerts_path, "a", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    def _update_related_kpis(self, metric: Metric):
        """Update KPIs related to a metric."""
        for kpi_id, kpi_def in self.kpi_definitions.items():
            if kpi_def["name"].lower() in metric.name.lower():
                # Calculate new KPI value
                new_value = kpi_def["calculation"](self)

                if kpi_id in self.kpis:
                    kpi = self.kpis[kpi_id]
                    kpi.historical_values.append((datetime.now(), new_value))
                    kpi.current_value = new_value
                    kpi.last_updated = datetime.now()

                    # Calculate trend
                    if len(kpi.historical_values) >= 2:
                        recent_values = [v for _, v in kpi.historical_values[-5:]]
                        if len(recent_values) >= 2:
                            if recent_values[-1] > recent_values[0]:
                                kpi.trend = "up"
                            elif recent_values[-1] < recent_values[0]:
                                kpi.trend = "down"
                            else:
                                kpi.trend = "stable"
                else:
                    # Create new KPI
                    kpi = KPI(
                        kpi_id=kpi_id,
                        name=kpi_def["name"],
                        description=kpi_def["description"],
                        current_value=new_value,
                        target_value=kpi_def["target"],
                        unit=kpi_def["unit"],
                        trend="stable",
                        last_updated=datetime.now(),
                        historical_values=[(datetime.now(), new_value)],
                    )
                    self.kpis[kpi_id] = kpi

                self._save_kpis()

    def _calculate_learning_rate(self) -> float:
        """Calculate learning rate KPI."""
        # Count learning events in the last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        learning_events = [
            metric
            for metric in self.metrics
            if "learning" in metric.name.lower() and metric.timestamp >= cutoff
        ]
        return len(learning_events)

    def _calculate_recommendation_acceptance_rate(self) -> float:
        """Calculate recommendation acceptance rate KPI."""
        # This would analyze recommendation acceptance data
        # For now, return a simulated value
        return 75.0

    def _calculate_system_health_score(self) -> float:
        """Calculate system health score KPI."""
        # This would integrate with the health monitoring system
        # For now, return a simulated value
        return 85.0

    def _calculate_user_satisfaction(self) -> float:
        """Calculate user satisfaction KPI."""
        # This would analyze user satisfaction data
        # For now, return a simulated value
        return 82.0

    def _calculate_knowledge_growth_rate(self) -> float:
        """Calculate knowledge growth rate KPI."""
        # Count knowledge additions in the last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        knowledge_metrics = [
            metric
            for metric in self.metrics
            if "knowledge" in metric.name.lower() and metric.timestamp >= cutoff
        ]
        return len(knowledge_metrics)

    def _calculate_error_resolution_time(self) -> float:
        """Calculate error resolution time KPI."""
        # This would analyze error resolution data
        # For now, return a simulated value
        return 25.0

    def _calculate_performance_improvement(self) -> float:
        """Calculate performance improvement KPI."""
        # This would analyze performance metrics over time
        # For now, return a simulated value
        return 12.0

    def _save_kpis(self):
        """Save KPIs to storage."""
        data = {}
        for kpi_id, kpi in self.kpis.items():
            data[kpi_id] = {
                "name": kpi.name,
                "description": kpi.description,
                "current_value": kpi.current_value,
                "target_value": kpi.target_value,
                "unit": kpi.unit,
                "trend": kpi.trend,
                "last_updated": kpi.last_updated.isoformat(),
                "historical_values": [
                    (timestamp.isoformat(), value)
                    for timestamp, value in kpi.historical_values
                ],
                "alerts": kpi.alerts,
            }

        utils.write_json(self.kpis_path, data)

    def generate_report(
        self,
        report_type: Union[ReportType, str],
        period_start: datetime,
        period_end: datetime,
        title: str = None,
        description: str = None,
    ) -> str:
        """Generate a comprehensive report."""
        # Convert string to enum if needed
        if isinstance(report_type, str):
            try:
                report_type = ReportType(report_type)
            except ValueError:
                # If not a valid enum value, use a default
                report_type = ReportType.PERFORMANCE_SUMMARY

        report_id = f"report_{int(time.time())}_{utils.random_string(8)}"

        # Generate report data based on type
        if report_type == ReportType.PERFORMANCE_SUMMARY:
            data = self._generate_performance_summary_data(period_start, period_end)
        elif report_type == ReportType.LEARNING_ANALYTICS:
            data = self._generate_learning_analytics_data(period_start, period_end)
        elif report_type == ReportType.RECOMMENDATION_EFFECTIVENESS:
            data = self._generate_recommendation_effectiveness_data(
                period_start, period_end
            )
        elif report_type == ReportType.SYSTEM_HEALTH:
            data = self._generate_system_health_data(period_start, period_end)
        elif report_type == ReportType.KNOWLEDGE_BASE_GROWTH:
            data = self._generate_knowledge_base_growth_data(period_start, period_end)
        elif report_type == ReportType.USER_SATISFACTION:
            data = self._generate_user_satisfaction_data(period_start, period_end)
        elif report_type == ReportType.TREND_ANALYSIS:
            data = self._generate_trend_analysis_data(period_start, period_end)
        else:
            data = {"error": f"Unknown report type: {report_type}"}

        # Generate summary and recommendations
        summary = self._generate_report_summary(report_type, data)
        recommendations = self._generate_report_recommendations(report_type, data)

        # Create report
        report = Report(
            report_id=report_id,
            report_type=report_type,
            title=title or f"{report_type.value.replace('_', ' ').title()} Report",
            description=description or f"Comprehensive {report_type.value} analysis",
            generated_at=datetime.now(),
            period_start=period_start,
            period_end=period_end,
            data=data,
            summary=summary,
            recommendations=recommendations,
            export_formats=self.analytics_config["export_formats"],
        )

        self.reports.append(report)
        self._save_report(report)

        telemetry.log_event(
            "report_generated",
            report_id=report_id,
            report_type=report_type.value,
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
        )

        return report_id

    def _generate_performance_summary_data(
        self, period_start: datetime, period_end: datetime
    ) -> Dict[str, Any]:
        """Generate performance summary report data."""
        # Filter metrics for the period
        period_metrics = [
            metric
            for metric in self.metrics
            if period_start <= metric.timestamp <= period_end
        ]

        # Calculate performance metrics
        total_metrics = len(period_metrics)
        avg_value = (
            statistics.mean([m.value for m in period_metrics]) if period_metrics else 0
        )

        # Group by metric type
        by_type = defaultdict(list)
        for metric in period_metrics:
            by_type[metric.metric_type.value].append(metric.value)

        return {
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
                "duration_days": (period_end - period_start).days,
            },
            "summary": {
                "total_metrics": total_metrics,
                "average_value": avg_value,
                "metrics_by_type": {k: len(v) for k, v in by_type.items()},
            },
            "kpis": {
                kpi_id: {
                    "name": kpi.name,
                    "current_value": kpi.current_value,
                    "target_value": kpi.target_value,
                    "trend": kpi.trend,
                }
                for kpi_id, kpi in self.kpis.items()
            },
            "alerts": {
                "total": len(
                    [
                        a
                        for a in self.alerts
                        if period_start <= a.triggered_at <= period_end
                    ]
                ),
                "by_level": dict(
                    Counter(
                        a.alert_level.value
                        for a in self.alerts
                        if period_start <= a.triggered_at <= period_end
                    )
                ),
            },
        }

    def _generate_learning_analytics_data(
        self, period_start: datetime, period_end: datetime
    ) -> Dict[str, Any]:
        """Generate learning analytics report data."""
        # This would analyze learning events and patterns
        return {
            "learning_events": {"total": 0, "by_type": {}, "trend": "stable"},
            "knowledge_acquisition": {
                "new_knowledge_items": 0,
                "knowledge_quality_score": 0.0,
            },
            "pattern_discovery": {
                "patterns_discovered": 0,
                "pattern_confidence_avg": 0.0,
            },
        }

    def _generate_recommendation_effectiveness_data(
        self, period_start: datetime, period_end: datetime
    ) -> Dict[str, Any]:
        """Generate recommendation effectiveness report data."""
        # This would analyze recommendation acceptance and impact
        return {
            "recommendations": {
                "total_generated": 0,
                "accepted": 0,
                "rejected": 0,
                "acceptance_rate": 0.0,
            },
            "effectiveness": {
                "average_impact_score": 0.0,
                "successful_implementations": 0,
            },
        }

    def _generate_system_health_data(
        self, period_start: datetime, period_end: datetime
    ) -> Dict[str, Any]:
        """Generate system health report data."""
        # This would integrate with the health monitoring system
        return {
            "health_score": {"current": 85.0, "average": 82.0, "trend": "improving"},
            "issues": {"total": 0, "resolved": 0, "active": 0},
            "self_healing": {"actions_taken": 0, "success_rate": 0.0},
        }

    def _generate_knowledge_base_growth_data(
        self, period_start: datetime, period_end: datetime
    ) -> Dict[str, Any]:
        """Generate knowledge base growth report data."""
        # This would analyze knowledge base evolution
        return {
            "growth": {"new_items": 0, "growth_rate": 0.0, "total_items": 0},
            "quality": {"average_confidence": 0.0, "high_quality_percentage": 0.0},
            "patterns": {"discovered": 0, "validated": 0},
        }

    def _generate_user_satisfaction_data(
        self, period_start: datetime, period_end: datetime
    ) -> Dict[str, Any]:
        """Generate user satisfaction report data."""
        # This would analyze user feedback and satisfaction metrics
        return {
            "satisfaction": {
                "current_score": 82.0,
                "average_score": 80.0,
                "trend": "stable",
            },
            "feedback": {"total_responses": 0, "positive_percentage": 0.0},
        }

    def _generate_trend_analysis_data(
        self, period_start: datetime, period_end: datetime
    ) -> Dict[str, Any]:
        """Generate trend analysis report data."""
        # This would analyze trends across all metrics and KPIs
        return {
            "trends": {
                "performance": "improving",
                "learning": "stable",
                "health": "improving",
            },
            "forecasts": {"next_week": {}, "next_month": {}},
        }

    def _generate_report_summary(
        self, report_type: ReportType, data: Dict[str, Any]
    ) -> str:
        """Generate a summary for a report."""
        if report_type == ReportType.PERFORMANCE_SUMMARY:
            return f"Performance summary shows {data['summary']['total_metrics']} metrics tracked with average value of {data['summary']['average_value']:.2f}."
        elif report_type == ReportType.LEARNING_ANALYTICS:
            return "Learning analytics indicate stable knowledge acquisition patterns."
        elif report_type == ReportType.SYSTEM_HEALTH:
            return f"System health is {data['health_score']['trend']} with current score of {data['health_score']['current']:.1f}."
        else:
            return f"Report generated for {report_type.value} covering the specified period."

    def _generate_report_recommendations(
        self, report_type: ReportType, data: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for a report."""
        recommendations = []

        if report_type == ReportType.PERFORMANCE_SUMMARY:
            if data["summary"]["average_value"] < 50:
                recommendations.append("Consider performance optimization initiatives")
            if data["alerts"]["total"] > 10:
                recommendations.append("Review alert thresholds to reduce noise")

        elif report_type == ReportType.SYSTEM_HEALTH:
            if data["health_score"]["current"] < 80:
                recommendations.append("Investigate system health issues")
            if data["issues"]["active"] > 5:
                recommendations.append("Prioritize resolution of active issues")

        return recommendations

    def _save_report(self, report: Report):
        """Save a report to storage."""
        data = {
            "report_id": report.report_id,
            "report_type": report.report_type.value,
            "title": report.title,
            "description": report.description,
            "generated_at": report.generated_at.isoformat(),
            "period_start": report.period_start.isoformat(),
            "period_end": report.period_end.isoformat(),
            "data": report.data,
            "summary": report.summary,
            "recommendations": report.recommendations,
            "charts": report.charts,
            "export_formats": report.export_formats,
        }

        with open(self.reports_path, "a", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard display."""
        return {
            "kpis": {
                kpi_id: {
                    "name": kpi.name,
                    "current_value": kpi.current_value,
                    "target_value": kpi.target_value,
                    "unit": kpi.unit,
                    "trend": kpi.trend,
                    "last_updated": kpi.last_updated.isoformat(),
                }
                for kpi_id, kpi in self.kpis.items()
            },
            "recent_alerts": [
                {
                    "alert_id": alert.alert_id,
                    "level": alert.alert_level.value,
                    "title": alert.title,
                    "triggered_at": alert.triggered_at.isoformat(),
                    "acknowledged": alert.acknowledged,
                }
                for alert in self.alerts[-10:]  # Last 10 alerts
            ],
            "recent_metrics": [
                {
                    "name": metric.name,
                    "value": metric.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "type": metric.metric_type.value,
                }
                for metric in self.metrics[-20:]  # Last 20 metrics
            ],
            "system_status": {
                "total_metrics": len(self.metrics),
                "active_kpis": len(self.kpis),
                "total_reports": len(self.reports),
                "active_alerts": len([a for a in self.alerts if not a.resolved_at]),
            },
        }

    def export_report(self, report_id: str, format: str = "json") -> str:
        """Export a report in the specified format."""
        # Find the report
        report = None
        for r in self.reports:
            if r.report_id == report_id:
                report = r
                break

        if not report:
            raise ValueError(f"Report {report_id} not found")

        if format == "json":
            return json.dumps(
                {
                    "report_id": report.report_id,
                    "title": report.title,
                    "generated_at": report.generated_at.isoformat(),
                    "period": {
                        "start": report.period_start.isoformat(),
                        "end": report.period_end.isoformat(),
                    },
                    "summary": report.summary,
                    "data": report.data,
                    "recommendations": report.recommendations,
                },
                indent=2,
            )

        elif format == "csv":
            # Convert report data to CSV format
            output = io.StringIO()
            writer = csv.writer(output)

            # Write summary data
            writer.writerow(["Metric", "Value"])
            for key, value in report.data.items():
                if isinstance(value, (int, float, str)):
                    writer.writerow([key, value])

            return output.getvalue()

        elif format == "html":
            # Generate HTML report
            html = f"""
            <html>
            <head>
                <title>{report.title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    .summary {{ margin: 20px 0; }}
                    .recommendations {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{report.title}</h1>
                    <p>Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Period: {report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}</p>
                </div>
                <div class="summary">
                    <h2>Summary</h2>
                    <p>{report.summary}</p>
                </div>
                <div class="recommendations">
                    <h2>Recommendations</h2>
                    <ul>
                        {''.join(f'<li>{rec}</li>' for rec in report.recommendations)}
                    </ul>
                </div>
            </body>
            </html>
            """
            return html

        else:
            raise ValueError(f"Unsupported export format: {format}")

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary."""
        return {
            "metrics": {
                "total": len(self.metrics),
                "by_type": dict(Counter(m.metric_type.value for m in self.metrics)),
                "recent_count": len(
                    [
                        m
                        for m in self.metrics
                        if m.timestamp >= datetime.now() - timedelta(hours=24)
                    ]
                ),
            },
            "kpis": {
                "total": len(self.kpis),
                "on_target": len(
                    [k for k in self.kpis.values() if k.current_value >= k.target_value]
                ),
                "trending_up": len([k for k in self.kpis.values() if k.trend == "up"]),
                "trending_down": len(
                    [k for k in self.kpis.values() if k.trend == "down"]
                ),
            },
            "reports": {
                "total": len(self.reports),
                "recent": len(
                    [
                        r
                        for r in self.reports
                        if r.generated_at >= datetime.now() - timedelta(days=7)
                    ]
                ),
            },
            "alerts": {
                "total": len(self.alerts),
                "active": len([a for a in self.alerts if not a.resolved_at]),
                "by_level": dict(Counter(a.alert_level.value for a in self.alerts)),
            },
        }


def get_continuous_improvement_analytics(root: Path) -> ContinuousImprovementAnalytics:
    """Get continuous improvement analytics system instance."""
    return ContinuousImprovementAnalytics(root)
