#!/usr/bin/env python3
"""
Import Change Monitor - Monitors and tracks import changes during consolidation.

This tool provides real-time monitoring of import changes, tracks consolidation progress,
and provides metrics for the migration process.

Features:
- Real-time import change detection
- Consolidation progress tracking
- Performance metrics collection
- Integration with existing monitoring systems
- Automated alerting for issues
"""
import ast
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from ai_onboard.core.common_imports import json, sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# from ai_onboard.core.telemetry import TelemetryCollector  # Not available
from ai_onboard.core.utils import ensure_dir, read_json, write_json


class ChangeType(Enum):
    """Types of import changes that can be detected."""

    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    CONSOLIDATED = "consolidated"
    RESTORED = "restored"


class AlertLevel(Enum):
    """Alert levels for monitoring."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ImportChange:
    """Represents a single import change."""

    file_path: Path
    line_number: int
    change_type: ChangeType
    original_import: str
    new_import: str
    timestamp: datetime
    consolidation_target: Optional[str] = None
    impact_score: float = 0.0


@dataclass
class ConsolidationProgress:
    """Tracks progress of consolidation migration."""

    target_name: str
    total_files: int
    processed_files: int
    successful_changes: int
    failed_changes: int
    start_time: datetime
    estimated_completion: Optional[datetime] = None
    progress_percentage: float = 0.0


@dataclass
class MonitoringMetrics:
    """Comprehensive monitoring metrics."""

    total_changes: int
    changes_by_type: Dict[ChangeType, int]
    changes_by_file: Dict[str, int]
    consolidation_progress: List[ConsolidationProgress]
    performance_metrics: Dict[str, float]
    error_rate: float
    success_rate: float
    average_change_time: float
    last_update: datetime


@dataclass
class Alert:
    """Represents a monitoring alert."""

    level: AlertLevel
    message: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False


class ImportChangeMonitor:
    """Monitors and tracks import changes during consolidation."""

    def __init__(self, root: Path):
        self.root = root
        self.monitoring_log = root / ".ai_onboard" / "import_monitoring_log.jsonl"
        self.metrics_file = root / ".ai_onboard" / "import_metrics.json"
        self.alerts_file = root / ".ai_onboard" / "import_alerts.json"

        # Initialize telemetry (placeholder - TelemetryCollector not available)
        # self.telemetry = TelemetryCollector(root)

        # Ensure directories exist
        ensure_dir(self.monitoring_log.parent)

        # Load existing data
        self.import_snapshots: Dict[str, Dict[str, Any]] = {}
        self.change_history: List[ImportChange] = []
        self.consolidation_progress: Dict[str, ConsolidationProgress] = {}
        self.active_alerts: List[Alert] = []

        # Load existing data
        self._load_existing_data()

        # Monitoring configuration
        self.config = self._load_monitoring_config()

        # Performance tracking
        self.performance_history: deque = deque(maxlen=1000)
        self.change_times: deque = deque(maxlen=100)

    def _load_monitoring_config(self) -> Dict[str, Any]:
        """Load monitoring configuration."""
        default_config = {
            "monitoring_interval": 5,  # seconds
            "alert_thresholds": {
                "error_rate": 0.1,  # 10%
                "performance_regression": 0.2,  # 20%
                "failed_changes": 5,
                "consolidation_stall": 300,  # 5 minutes
            },
            "metrics_retention": 7,  # days
            "alert_retention": 30,  # days
            "performance_tracking": True,
            "real_time_alerts": True,
        }

        config_file = self.root / ".ai_onboard" / "monitoring_config.json"
        return read_json(config_file, default_config)

    def _load_existing_data(self):
        """Load existing monitoring data."""
        # Load metrics
        if self.metrics_file.exists():
            try:
                metrics_data = read_json(self.metrics_file, {})
                self.consolidation_progress = {
                    name: ConsolidationProgress(**data)
                    for name, data in metrics_data.get(
                        "consolidation_progress", {}
                    ).items()
                }
            except Exception as e:
                print(f"Warning: Could not load existing metrics: {e}")

        # Load alerts
        if self.alerts_file.exists():
            try:
                alerts_data = read_json(self.alerts_file, [])
                self.active_alerts = [Alert(**alert) for alert in alerts_data]
            except Exception as e:
                print(f"Warning: Could not load existing alerts: {e}")

    def start_monitoring(self, consolidation_targets: List[str]):
        """Start monitoring import changes for consolidation targets."""
        print(
            f"🔍 Starting import change monitoring for targets: {', '.join(consolidation_targets)}"
        )

        # Initialize progress tracking for each target
        for target in consolidation_targets:
            self.consolidation_progress[target] = ConsolidationProgress(
                target_name=target,
                total_files=0,
                processed_files=0,
                successful_changes=0,
                failed_changes=0,
                start_time=datetime.now(),
            )

        # Take initial snapshot
        self._take_snapshot()

        print("✅ Monitoring started successfully")

    def stop_monitoring(self):
        """Stop monitoring and save final metrics."""
        print("🛑 Stopping import change monitoring...")

        # Save final metrics (guard against None)
        try:
            self._save_metrics()
        except Exception:
            pass

        # Generate final report (guard)
        try:
            final_report = self._generate_final_report()
        except Exception:
            final_report = {"error": "failed_to_generate_report"}

        # Save final report
        try:
            report_file = (
                self.root / ".ai_onboard" / "import_monitoring_final_report.json"
            )
            write_json(report_file, final_report)
        except Exception:
            pass

        print("✅ Monitoring stopped and final report saved")

    def record_import_change(
        self,
        file_path: Path,
        line_number: int,
        change_type: ChangeType,
        original_import: str,
        new_import: str,
        consolidation_target: Optional[str] = None,
    ):
        """Record a single import change."""
        change = ImportChange(
            file_path=file_path,
            line_number=line_number,
            change_type=change_type,
            original_import=original_import,
            new_import=new_import,
            timestamp=datetime.now(),
            consolidation_target=consolidation_target,
            impact_score=self._calculate_impact_score(original_import, new_import),
        )

        self.change_history.append(change)

        # Update progress if this is a consolidation change
        if consolidation_target and consolidation_target in self.consolidation_progress:
            progress = self.consolidation_progress[consolidation_target]
            progress.processed_files += 1

            if change_type == ChangeType.CONSOLIDATED:
                progress.successful_changes += 1
            else:
                progress.failed_changes += 1

            # Update progress percentage
            if progress.total_files > 0:
                progress.progress_percentage = (
                    progress.processed_files / progress.total_files
                ) * 100

        # Check for alerts
        self._check_alerts(change)

        # Log change
        self._log_change(change)

        # Update metrics
        self._update_metrics()

    def _calculate_impact_score(self, original: str, new: str) -> float:
        """Calculate impact score for an import change."""
        # Simple scoring based on import complexity
        original_complexity = len(original.split("."))
        new_complexity = len(new.split("."))

        # Base score on complexity difference
        complexity_diff = abs(original_complexity - new_complexity)

        # Add bonus for consolidation
        if "consolidated" in new.lower() or "common" in new.lower():
            complexity_diff += 0.5

        return min(complexity_diff, 5.0)  # Cap at 5.0

    def _check_alerts(self, change: ImportChange):
        """Check if change triggers any alerts."""
        # Check error rate
        recent_changes = [
            c
            for c in self.change_history
            if c.timestamp > datetime.now() - timedelta(minutes=5)
        ]
        if recent_changes:
            error_rate = sum(
                1 for c in recent_changes if c.change_type == ChangeType.REMOVED
            ) / len(recent_changes)
            if error_rate > self.config["alert_thresholds"]["error_rate"]:
                self._create_alert(
                    AlertLevel.WARNING,
                    f"High error rate detected: {error_rate:.1%}",
                    {"error_rate": error_rate, "recent_changes": len(recent_changes)},
                )

        # Check for consolidation stall
        for target, progress in self.consolidation_progress.items():
            if progress.processed_files > 0:
                time_since_last = datetime.now() - progress.start_time
                if (
                    time_since_last.total_seconds()
                    > self.config["alert_thresholds"]["consolidation_stall"]
                ):
                    self._create_alert(
                        AlertLevel.WARNING,
                        f"Consolidation stall detected for {target}",
                        {
                            "target": target,
                            "time_since_start": time_since_last.total_seconds(),
                        },
                    )

        # Check for failed changes
        if change.change_type == ChangeType.REMOVED:
            self._create_alert(
                AlertLevel.ERROR,
                f"Import change failed in {change.file_path}",
                {"file": str(change.file_path), "line": change.line_number},
            )

    def _create_alert(self, level: AlertLevel, message: str, context: Dict[str, Any]):
        """Create a new alert."""
        alert = Alert(
            level=level, message=message, timestamp=datetime.now(), context=context
        )

        self.active_alerts.append(alert)

        # Log alert
        self._log_alert(alert)

        # Send real-time alert if enabled
        if self.config["real_time_alerts"]:
            self._send_real_time_alert(alert)

    def _send_real_time_alert(self, alert: Alert):
        """Send real-time alert (placeholder for integration with alerting system)."""
        print(f"🚨 ALERT [{alert.level.value.upper()}]: {alert.message}")
        if alert.context:
            for key, value in alert.context.items():
                print(f"    {key}: {value}")

    def _log_change(self, change: ImportChange):
        """Log import change to monitoring log."""
        log_entry = {
            "timestamp": change.timestamp.isoformat(),
            "file_path": str(change.file_path),
            "line_number": change.line_number,
            "change_type": change.change_type.value,
            "original_import": change.original_import,
            "new_import": change.new_import,
            "consolidation_target": change.consolidation_target,
            "impact_score": change.impact_score,
        }

        with open(self.monitoring_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def _log_alert(self, alert: Alert):
        """Log alert to monitoring log."""
        log_entry = {
            "timestamp": alert.timestamp.isoformat(),
            "type": "alert",
            "level": alert.level.value,
            "message": alert.message,
            "context": alert.context,
            "resolved": alert.resolved,
        }

        with open(self.monitoring_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def _take_snapshot(self):
        """Take a snapshot of current import state."""
        snapshot_time = datetime.now().isoformat()
        snapshot = {}

        # Scan all Python files for imports
        python_files = list(self.root.rglob("*.py"))
        python_files = [
            f
            for f in python_files
            if not f.name.startswith("__") and "test" not in str(f)
        ]

        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                file_imports = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            file_imports.append(
                                {
                                    "type": "import",
                                    "module": alias.name,
                                    "alias": alias.asname,
                                    "line": node.lineno,
                                }
                            )
                    elif isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            file_imports.append(
                                {
                                    "type": "from_import",
                                    "module": node.module or "",
                                    "name": alias.name,
                                    "alias": alias.asname,
                                    "line": node.lineno,
                                }
                            )

                snapshot[str(file_path)] = file_imports

            except Exception as e:
                print(f"Warning: Could not parse {file_path}: {e}")
                continue

        self.import_snapshots[snapshot_time] = snapshot

        # Clean up old snapshots
        self._cleanup_old_snapshots()

    def _cleanup_old_snapshots(self):
        """Clean up old snapshots based on retention policy."""
        retention_days = self.config["metrics_retention"]
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        snapshots_to_remove = []
        for timestamp_str in self.import_snapshots:
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp < cutoff_date:
                    snapshots_to_remove.append(timestamp_str)
            except ValueError:
                snapshots_to_remove.append(timestamp_str)

        for timestamp_str in snapshots_to_remove:
            del self.import_snapshots[timestamp_str]

    def _update_metrics(self):
        """Update monitoring metrics."""
        # Calculate metrics
        total_changes = len(self.change_history)
        changes_by_type = defaultdict(int)
        changes_by_file = defaultdict(int)

        for change in self.change_history:
            changes_by_type[change.change_type] += 1
            changes_by_file[str(change.file_path)] += 1

        # Calculate success/error rates
        successful_changes = sum(
            1 for c in self.change_history if c.change_type == ChangeType.CONSOLIDATED
        )
        failed_changes = sum(
            1 for c in self.change_history if c.change_type == ChangeType.REMOVED
        )

        success_rate = (successful_changes / total_changes) if total_changes > 0 else 0
        error_rate = (failed_changes / total_changes) if total_changes > 0 else 0

        # Calculate average change time
        if self.change_times:
            average_change_time = sum(self.change_times) / len(self.change_times)
        else:
            average_change_time = 0.0

        # Create metrics object
        metrics = MonitoringMetrics(
            total_changes=total_changes,
            changes_by_type=dict(changes_by_type),
            changes_by_file=dict(changes_by_file),
            consolidation_progress=list(self.consolidation_progress.values()),
            performance_metrics=self._calculate_performance_metrics(),
            error_rate=error_rate,
            success_rate=success_rate,
            average_change_time=average_change_time,
            last_update=datetime.now(),
        )

        # Save metrics
        self._save_metrics(metrics)

    def _calculate_performance_metrics(self) -> Dict[str, float]:
        """Calculate performance metrics."""
        if not self.performance_history:
            return {}

        recent_performance = list(self.performance_history)[
            -100:
        ]  # Last 100 measurements

        return {
            "average_processing_time": sum(recent_performance)
            / len(recent_performance),
            "max_processing_time": max(recent_performance),
            "min_processing_time": min(recent_performance),
            "performance_trend": self._calculate_performance_trend(),
        }

    def _calculate_performance_trend(self) -> float:
        """Calculate performance trend (positive = improving, negative = degrading)."""
        if len(self.performance_history) < 10:
            return 0.0

        recent = list(self.performance_history)[-10:]
        older = (
            list(self.performance_history)[-20:-10]
            if len(self.performance_history) >= 20
            else recent
        )

        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)

        return (older_avg - recent_avg) / older_avg if older_avg > 0 else 0.0

    def _save_metrics(self, metrics: Optional[MonitoringMetrics] = None):
        """Save monitoring metrics to file."""
        if metrics is None:
            # Load existing metrics and update
            if self.metrics_file.exists():
                try:
                    existing_data = read_json(self.metrics_file, {})
                    metrics = MonitoringMetrics(**existing_data)
                except Exception:
                    metrics = MonitoringMetrics(
                        total_changes=0,
                        changes_by_type={},
                        changes_by_file={},
                        consolidation_progress=[],
                        performance_metrics={},
                        error_rate=0.0,
                        success_rate=0.0,
                        average_change_time=0.0,
                        last_update=datetime.now(),
                    )

        # Convert to dict for JSON serialization
        metrics_data = {
            "total_changes": metrics.total_changes,
            "changes_by_type": metrics.changes_by_type,
            "changes_by_file": metrics.changes_by_file,
            "consolidation_progress": [
                {
                    "target_name": progress.target_name,
                    "total_files": progress.total_files,
                    "processed_files": progress.processed_files,
                    "successful_changes": progress.successful_changes,
                    "failed_changes": progress.failed_changes,
                    "start_time": progress.start_time.isoformat(),
                    "estimated_completion": (
                        progress.estimated_completion.isoformat()
                        if progress.estimated_completion
                        else None
                    ),
                    "progress_percentage": progress.progress_percentage,
                }
                for progress in metrics.consolidation_progress
            ],
            "performance_metrics": metrics.performance_metrics,
            "error_rate": metrics.error_rate,
            "success_rate": metrics.success_rate,
            "average_change_time": metrics.average_change_time,
            "last_update": metrics.last_update.isoformat(),
        }

        write_json(self.metrics_file, metrics_data)

    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final monitoring report."""
        # Calculate final metrics
        total_changes = len(self.change_history)
        successful_changes = sum(
            1 for c in self.change_history if c.change_type == ChangeType.CONSOLIDATED
        )
        failed_changes = sum(
            1 for c in self.change_history if c.change_type == ChangeType.REMOVED
        )

        success_rate = (successful_changes / total_changes) if total_changes > 0 else 0
        error_rate = (failed_changes / total_changes) if total_changes > 0 else 0

        # Calculate consolidation progress
        consolidation_summary = {}
        for target, progress in self.consolidation_progress.items():
            consolidation_summary[target] = {
                "total_files": progress.total_files,
                "processed_files": progress.processed_files,
                "successful_changes": progress.successful_changes,
                "failed_changes": progress.failed_changes,
                "progress_percentage": progress.progress_percentage,
                "duration": (datetime.now() - progress.start_time).total_seconds(),
            }

        # Generate report
        report = {
            "monitoring_summary": {
                "total_changes": total_changes,
                "successful_changes": successful_changes,
                "failed_changes": failed_changes,
                "success_rate": success_rate,
                "error_rate": error_rate,
                "monitoring_duration": (
                    (
                        datetime.now() - min(c.timestamp for c in self.change_history)
                    ).total_seconds()
                    if self.change_history
                    else 0
                ),
            },
            "consolidation_progress": consolidation_summary,
            "performance_metrics": self._calculate_performance_metrics(),
            "alerts_summary": {
                "total_alerts": len(self.active_alerts),
                "alerts_by_level": {
                    level.value: sum(1 for a in self.active_alerts if a.level == level)
                    for level in AlertLevel
                },
                "unresolved_alerts": sum(
                    1 for a in self.active_alerts if not a.resolved
                ),
            },
            "recommendations": self._generate_final_recommendations(),
            "timestamp": datetime.now().isoformat(),
        }

        return report

    def _generate_final_recommendations(self) -> List[str]:
        """Generate final recommendations based on monitoring data."""
        recommendations = []

        # Check success rate
        if self.change_history:
            success_rate = sum(
                1
                for c in self.change_history
                if c.change_type == ChangeType.CONSOLIDATED
            ) / len(self.change_history)
            if success_rate < 0.8:
                recommendations.append(
                    f"Low success rate ({success_rate:.1%}). Review failed changes and improve error handling."
                )

        # Check for unresolved alerts
        unresolved_alerts = sum(1 for a in self.active_alerts if not a.resolved)
        if unresolved_alerts > 0:
            recommendations.append(
                f"Address {unresolved_alerts} unresolved alerts before proceeding."
            )

        # Check performance
        if self.performance_history:
            recent_performance = list(self.performance_history)[-10:]
            if recent_performance:
                avg_performance = sum(recent_performance) / len(recent_performance)
                if avg_performance > 5.0:  # 5 seconds
                    recommendations.append(
                        "Performance degradation detected. Consider optimizing import processing."
                    )

        # Check consolidation progress
        for target, progress in self.consolidation_progress.items():
            if progress.progress_percentage < 100:
                recommendations.append(
                    f"Complete consolidation for {target} ({progress.progress_percentage:.1f}% done)."
                )

        return recommendations

    def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        return {
            "monitoring_active": len(self.consolidation_progress) > 0,
            "total_changes": len(self.change_history),
            "active_alerts": len([a for a in self.active_alerts if not a.resolved]),
            "consolidation_targets": list(self.consolidation_progress.keys()),
            "last_update": datetime.now().isoformat(),
        }

    def get_consolidation_progress(self, target: str) -> Optional[Dict[str, Any]]:
        """Get progress for a specific consolidation target."""
        if target not in self.consolidation_progress:
            return None

        progress = self.consolidation_progress[target]
        return {
            "target_name": progress.target_name,
            "total_files": progress.total_files,
            "processed_files": progress.processed_files,
            "successful_changes": progress.successful_changes,
            "failed_changes": progress.failed_changes,
            "progress_percentage": progress.progress_percentage,
            "start_time": progress.start_time.isoformat(),
            "estimated_completion": (
                progress.estimated_completion.isoformat()
                if progress.estimated_completion
                else None
            ),
        }


def main():
    """Main CLI interface for import change monitor."""
    import argparse

    parser = argparse.ArgumentParser(description="Import Change Monitor")
    parser.add_argument(
        "--root", type=Path, default=Path.cwd(), help="Project root directory"
    )
    parser.add_argument(
        "--start", nargs="+", help="Start monitoring for consolidation targets"
    )
    parser.add_argument("--stop", action="store_true", help="Stop monitoring")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--progress", help="Show progress for specific target")
    parser.add_argument(
        "--record-change",
        nargs=6,
        metavar=("FILE", "LINE", "TYPE", "ORIGINAL", "NEW", "TARGET"),
        help="Record a single change",
    )

    args = parser.parse_args()

    monitor = ImportChangeMonitor(args.root)

    if args.start:
        monitor.start_monitoring(args.start)
        print(f"✅ Started monitoring for: {', '.join(args.start)}")

    elif args.stop:
        monitor.stop_monitoring()
        print("✅ Stopped monitoring")

    elif args.status:
        status = monitor.get_current_status()
        print("📊 Current Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

    elif args.progress:
        progress = monitor.get_consolidation_progress(args.progress)
        if progress:
            print(f"📈 Progress for {args.progress}:")
            for key, value in progress.items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ No progress found for target: {args.progress}")

    elif args.record_change:
        file_path, line_number, change_type, original, new, target = args.record_change
        change_type_enum = ChangeType(change_type)
        monitor.record_import_change(
            Path(file_path), int(line_number), change_type_enum, original, new, target
        )
        print(f"✅ Recorded change: {change_type} in {file_path}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
