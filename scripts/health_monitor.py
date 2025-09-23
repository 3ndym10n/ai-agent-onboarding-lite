#!/usr/bin/env python3
"""
Automated Health Monitoring System for ai-onboard Tool Ecosystem

This system provides comprehensive health monitoring for all operational tools,
including performance tracking, failure detection, and automated reporting.
"""

import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

sys.path.insert(0, ".")

from ai_onboard.core.intelligent_tool_orchestrator import IntelligentToolOrchestrator


class HealthStatus(Enum):
    """Health status levels for tools and the system."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class ToolHealthMetrics:
    """Health metrics for a single tool."""

    tool_name: str
    status: HealthStatus
    last_check: datetime
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_execution_time: float = 0.0
    last_execution_time: float = 0.0
    error_messages: List[str] = field(default_factory=list)
    performance_trend: str = "stable"  # improving, stable, degrading
    consecutive_failures: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None


@dataclass
class SystemHealthReport:
    """Comprehensive system health report."""

    timestamp: datetime
    overall_status: HealthStatus
    total_tools: int
    healthy_tools: int
    warning_tools: int
    critical_tools: int
    system_metrics: Dict[str, Any]
    tool_metrics: Dict[str, ToolHealthMetrics]
    recommendations: List[str]


class AutomatedHealthMonitor:
    """Automated health monitoring system for the tool ecosystem."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.orchestrator = IntelligentToolOrchestrator(root_path)
        self.health_data_path = root_path / ".ai_onboard" / "health_monitoring"
        self.health_data_path.mkdir(exist_ok=True)

        # Health monitoring configuration
        self.health_check_interval = 300  # 5 minutes
        self.critical_failure_threshold = 3  # consecutive failures
        self.warning_performance_threshold = 2.0  # 2x normal execution time
        self.health_history_days = 7  # Keep 7 days of history

        # Load existing health data
        self.tool_metrics: Dict[str, ToolHealthMetrics] = {}
        self.load_health_data()

    def load_health_data(self) -> None:
        """Load existing health monitoring data."""
        health_file = self.health_data_path / "tool_health.json"
        if health_file.exists():
            try:
                with open(health_file, "r") as f:
                    data = json.load(f)

                for tool_name, metrics_data in data.items():
                    # Convert string timestamps back to datetime
                    last_check = datetime.fromisoformat(metrics_data["last_check"])
                    last_success = (
                        datetime.fromisoformat(metrics_data["last_success"])
                        if metrics_data.get("last_success")
                        else None
                    )
                    last_failure = (
                        datetime.fromisoformat(metrics_data["last_failure"])
                        if metrics_data.get("last_failure")
                        else None
                    )

                    self.tool_metrics[tool_name] = ToolHealthMetrics(
                        tool_name=tool_name,
                        status=HealthStatus(metrics_data["status"]),
                        last_check=last_check,
                        execution_count=metrics_data["execution_count"],
                        success_count=metrics_data["success_count"],
                        failure_count=metrics_data["failure_count"],
                        average_execution_time=metrics_data["average_execution_time"],
                        last_execution_time=metrics_data["last_execution_time"],
                        error_messages=metrics_data["error_messages"][
                            -10:
                        ],  # Keep last 10 errors
                        performance_trend=metrics_data["performance_trend"],
                        consecutive_failures=metrics_data["consecutive_failures"],
                        last_success=last_success,
                        last_failure=last_failure,
                    )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load health data: {e}")
                self.initialize_tool_metrics()

        if not self.tool_metrics:
            self.initialize_tool_metrics()

    def initialize_tool_metrics(self) -> None:
        """Initialize health metrics for all operational tools."""
        # Get list of operational tools from orchestrator
        operational_tools = [
            "dependency_mapper",
            "code_quality_analyzer",
            "file_organization_analyzer",
            "duplicate_detector",
            "vision_guardian",
            "gate_system",
            "ultra_safe_cleanup",
            "charter_management",
            "automatic_error_prevention",
            "pattern_recognition_system",
            "task_execution_gate",
            "interrogation_system",
            "conversation_analysis",
            "ui_enhancement",
            "wbs_management",
            "ai_agent_orchestration",
            "decision_pipeline",
            "intelligent_monitoring",
            "user_preference_learning_system",
        ]

        now = datetime.now()
        for tool_name in operational_tools:
            if tool_name not in self.tool_metrics:
                self.tool_metrics[tool_name] = ToolHealthMetrics(
                    tool_name=tool_name, status=HealthStatus.UNKNOWN, last_check=now
                )

    def save_health_data(self) -> None:
        """Save current health monitoring data."""
        health_file = self.health_data_path / "tool_health.json"

        data = {}
        for tool_name, metrics in self.tool_metrics.items():
            data[tool_name] = {
                "status": metrics.status.value,
                "last_check": metrics.last_check.isoformat(),
                "execution_count": metrics.execution_count,
                "success_count": metrics.success_count,
                "failure_count": metrics.failure_count,
                "average_execution_time": metrics.average_execution_time,
                "last_execution_time": metrics.last_execution_time,
                "error_messages": metrics.error_messages,
                "performance_trend": metrics.performance_trend,
                "consecutive_failures": metrics.consecutive_failures,
                "last_success": (
                    metrics.last_success.isoformat() if metrics.last_success else None
                ),
                "last_failure": (
                    metrics.last_failure.isoformat() if metrics.last_failure else None
                ),
            }

        with open(health_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def check_tool_health(self, tool_name: str) -> ToolHealthMetrics:
        """Check the health of a specific tool."""
        metrics = self.tool_metrics[tool_name]
        start_time = time.time()

        try:
            # Execute the tool
            result = self.orchestrator.execute_automatic_tool_application(
                tool_name, {"health_check": True}
            )

            execution_time = time.time() - start_time
            metrics.execution_count += 1
            metrics.last_execution_time = execution_time
            metrics.last_check = datetime.now()

            if result.get("executed", False):
                # Success
                metrics.success_count += 1
                metrics.consecutive_failures = 0
                metrics.last_success = datetime.now()

                # Update average execution time
                if metrics.average_execution_time == 0:
                    metrics.average_execution_time = execution_time
                else:
                    metrics.average_execution_time = (
                        (metrics.average_execution_time * (metrics.execution_count - 1))
                        + execution_time
                    ) / metrics.execution_count

                # Check performance trend
                if (
                    execution_time
                    > metrics.average_execution_time
                    * self.warning_performance_threshold
                ):
                    if metrics.performance_trend != "degrading":
                        metrics.performance_trend = "degrading"
                elif execution_time < metrics.average_execution_time * 0.8:
                    if metrics.performance_trend != "improving":
                        metrics.performance_trend = "improving"
                else:
                    metrics.performance_trend = "stable"

                # Determine health status
                if metrics.consecutive_failures == 0:
                    if metrics.performance_trend == "degrading":
                        metrics.status = HealthStatus.WARNING
                    else:
                        metrics.status = HealthStatus.HEALTHY
                else:
                    metrics.status = HealthStatus.WARNING

            else:
                # Failure
                metrics.failure_count += 1
                metrics.consecutive_failures += 1
                metrics.last_failure = datetime.now()

                error_msg = result.get("error", "Unknown error")
                metrics.error_messages.append(
                    f"{datetime.now().isoformat()}: {error_msg}"
                )
                metrics.error_messages = metrics.error_messages[-10:]  # Keep last 10

                # Determine health status
                if metrics.consecutive_failures >= self.critical_failure_threshold:
                    metrics.status = HealthStatus.CRITICAL
                else:
                    metrics.status = HealthStatus.WARNING

        except Exception as e:
            execution_time = time.time() - start_time
            metrics.execution_count += 1
            metrics.failure_count += 1
            metrics.consecutive_failures += 1
            metrics.last_failure = datetime.now()
            metrics.last_execution_time = execution_time
            metrics.last_check = datetime.now()

            error_msg = f"Exception during health check: {str(e)}"
            metrics.error_messages.append(f"{datetime.now().isoformat()}: {error_msg}")
            metrics.error_messages = metrics.error_messages[-10:]

            if metrics.consecutive_failures >= self.critical_failure_threshold:
                metrics.status = HealthStatus.CRITICAL
            else:
                metrics.status = HealthStatus.WARNING

        return metrics

    def perform_comprehensive_health_check(self) -> SystemHealthReport:
        """Perform a comprehensive health check of all tools."""
        print("🏥 Starting Comprehensive Health Check")
        print("=" * 50)

        start_time = time.time()
        system_start_time = datetime.now()

        # Check system metrics
        system_metrics = self._collect_system_metrics()

        # Check all tools
        healthy_count = 0
        warning_count = 0
        critical_count = 0

        for tool_name in self.tool_metrics.keys():
            print(f"  🔍 Checking {tool_name}...")
            metrics = self.check_tool_health(tool_name)

            if metrics.status == HealthStatus.HEALTHY:
                healthy_count += 1
                print(f"    ✅ Healthy")
            elif metrics.status == HealthStatus.WARNING:
                warning_count += 1
                print(f"    ⚠️  Warning")
            elif metrics.status == HealthStatus.CRITICAL:
                critical_count += 1
                print(f"    ❌ Critical")
            else:
                print(f"    ❓ Unknown")

        # Determine overall system status
        if critical_count > 0:
            overall_status = HealthStatus.CRITICAL
        elif warning_count > 0:
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.HEALTHY

        # Generate recommendations
        recommendations = self._generate_recommendations(
            healthy_count, warning_count, critical_count
        )

        # Save updated health data
        self.save_health_data()

        # Create comprehensive report
        report = SystemHealthReport(
            timestamp=system_start_time,
            overall_status=overall_status,
            total_tools=len(self.tool_metrics),
            healthy_tools=healthy_count,
            warning_tools=warning_count,
            critical_tools=critical_count,
            system_metrics=system_metrics,
            tool_metrics=self.tool_metrics.copy(),
            recommendations=recommendations,
        )

        # Save report
        self._save_health_report(report)

        execution_time = time.time() - start_time
        print(".2f")
        print(f"📊 Status: {overall_status.value.upper()}")
        print(f"✅ Healthy: {healthy_count}")
        print(f"⚠️  Warning: {warning_count}")
        print(f"❌ Critical: {critical_count}")

        return report

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level health metrics."""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage("/").percent,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": sys.platform,
                "uptime_seconds": time.time() - psutil.boot_time(),
            }
        except Exception as e:
            return {
                "error": f"Could not collect system metrics: {e}",
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": sys.platform,
            }

    def _generate_recommendations(
        self, healthy: int, warning: int, critical: int
    ) -> List[str]:
        """Generate health recommendations based on current status."""
        recommendations = []

        if critical > 0:
            recommendations.append(
                f"🚨 CRITICAL: {critical} tools are failing - immediate attention required"
            )
            recommendations.append("   • Check tool error logs for failure patterns")
            recommendations.append("   • Verify system dependencies and permissions")
            recommendations.append("   • Consider rolling back recent changes")

        if warning > 0:
            recommendations.append(f"⚠️  WARNING: {warning} tools showing issues")
            recommendations.append(
                "   • Monitor performance trends for degrading tools"
            )
            recommendations.append("   • Review error logs for recurring patterns")
            recommendations.append("   • Check system resources (CPU, memory, disk)")

        if healthy == len(self.tool_metrics):
            recommendations.append("🎉 EXCELLENT: All tools are healthy")
            recommendations.append(
                "   • Continue regular monitoring to maintain health"
            )
            recommendations.append("   • Consider performance optimizations if needed")

        # Performance recommendations
        slow_tools = [
            name
            for name, metrics in self.tool_metrics.items()
            if metrics.performance_trend == "degrading"
        ]
        if slow_tools:
            recommendations.append(
                f"🐌 PERFORMANCE: {len(slow_tools)} tools showing performance degradation"
            )
            recommendations.append(
                f"   • Monitor: {', '.join(slow_tools[:3])}{'...' if len(slow_tools) > 3 else ''}"
            )

        return recommendations

    def _save_health_report(self, report: SystemHealthReport) -> None:
        """Save health report to file."""
        report_file = (
            self.health_data_path
            / f"health_report_{report.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        )

        report_data = {
            "timestamp": report.timestamp.isoformat(),
            "overall_status": report.overall_status.value,
            "summary": {
                "total_tools": report.total_tools,
                "healthy_tools": report.healthy_tools,
                "warning_tools": report.warning_tools,
                "critical_tools": report.critical_tools,
            },
            "system_metrics": report.system_metrics,
            "recommendations": report.recommendations,
            "tool_details": {},
        }

        for tool_name, metrics in report.tool_metrics.items():
            report_data["tool_details"][tool_name] = {
                "status": metrics.status.value,
                "last_check": metrics.last_check.isoformat(),
                "execution_count": metrics.execution_count,
                "success_rate": (
                    (metrics.success_count / metrics.execution_count * 100)
                    if metrics.execution_count > 0
                    else 0
                ),
                "average_execution_time": metrics.average_execution_time,
                "performance_trend": metrics.performance_trend,
                "consecutive_failures": metrics.consecutive_failures,
                "last_success": (
                    metrics.last_success.isoformat() if metrics.last_success else None
                ),
                "last_failure": (
                    metrics.last_failure.isoformat() if metrics.last_failure else None
                ),
                "recent_errors": (
                    metrics.error_messages[-3:] if metrics.error_messages else []
                ),
            }

        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

        # Also save latest report
        latest_report = self.health_data_path / "latest_health_report.json"
        with open(latest_report, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

    def get_health_dashboard(self) -> Dict[str, Any]:
        """Get a dashboard view of current health status."""
        report = self.perform_comprehensive_health_check()

        dashboard = {
            "timestamp": report.timestamp.isoformat(),
            "overall_status": report.overall_status.value,
            "summary": {
                "total_tools": report.total_tools,
                "healthy_tools": report.healthy_tools,
                "warning_tools": report.warning_tools,
                "critical_tools": report.critical_tools,
                "health_percentage": (
                    (report.healthy_tools / report.total_tools * 100)
                    if report.total_tools > 0
                    else 0
                ),
            },
            "system_metrics": report.system_metrics,
            "critical_tools": [
                {
                    "name": name,
                    "consecutive_failures": metrics.consecutive_failures,
                    "last_error": (
                        metrics.error_messages[-1]
                        if metrics.error_messages
                        else "No error details"
                    ),
                }
                for name, metrics in report.tool_metrics.items()
                if metrics.status == HealthStatus.CRITICAL
            ],
            "warning_tools": [
                {
                    "name": name,
                    "performance_trend": metrics.performance_trend,
                    "consecutive_failures": metrics.consecutive_failures,
                }
                for name, metrics in report.tool_metrics.items()
                if metrics.status == HealthStatus.WARNING
            ],
            "recommendations": report.recommendations,
        }

        return dashboard

    def start_continuous_monitoring(self, interval_seconds: int = 300) -> None:
        """Start continuous health monitoring."""
        print(
            f"🔄 Starting continuous health monitoring (interval: {interval_seconds}s)"
        )
        print("Press Ctrl+C to stop")

        try:
            while True:
                self.perform_comprehensive_health_check()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n🛑 Health monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Health monitoring stopped due to error: {e}")

    def cleanup_old_reports(self, days_to_keep: int = 7) -> int:
        """Clean up old health reports."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0

        for report_file in self.health_data_path.glob("health_report_*.json"):
            if report_file.name != "latest_health_report.json":
                # Extract timestamp from filename
                try:
                    timestamp_str = report_file.stem.replace("health_report_", "")
                    file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                    if file_date < cutoff_date:
                        report_file.unlink()
                        deleted_count += 1
                except (ValueError, OSError):
                    continue

        return deleted_count


def main():
    """Main entry point for health monitoring."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Automated Health Monitoring for ai-onboard tools"
    )
    parser.add_argument(
        "--check", action="store_true", help="Perform single health check"
    )
    parser.add_argument(
        "--monitor", action="store_true", help="Start continuous monitoring"
    )
    parser.add_argument(
        "--dashboard", action="store_true", help="Show health dashboard"
    )
    parser.add_argument(
        "--interval", type=int, default=300, help="Monitoring interval in seconds"
    )
    parser.add_argument(
        "--cleanup", type=int, default=7, help="Clean up reports older than N days"
    )

    args = parser.parse_args()

    root_path = Path(".")
    monitor = AutomatedHealthMonitor(root_path)

    if args.check:
        # Single health check
        report = monitor.perform_comprehensive_health_check()
        print(
            f"\n🏥 Health Check Complete - Status: {report.overall_status.value.upper()}"
        )

    elif args.monitor:
        # Continuous monitoring
        monitor.start_continuous_monitoring(args.interval)

    elif args.dashboard:
        # Show dashboard
        dashboard = monitor.get_health_dashboard()
        print("\n🏥 HEALTH DASHBOARD")
        print("=" * 50)
        print(f"Status: {dashboard['overall_status'].upper()}")
        print(
            f"Healthy: {dashboard['summary']['healthy_tools']}/{dashboard['summary']['total_tools']}"
        )
        print(".1f")
        if dashboard["critical_tools"]:
            print(f"\n❌ Critical Tools ({len(dashboard['critical_tools'])}):")
            for tool in dashboard["critical_tools"]:
                print(
                    f"  • {tool['name']}: {tool['consecutive_failures']} consecutive failures"
                )

        if dashboard["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in dashboard["recommendations"]:
                print(f"  {rec}")

    elif args.cleanup > 0:
        # Clean up old reports
        deleted = monitor.cleanup_old_reports(args.cleanup)
        print(f"🧹 Cleaned up {deleted} old health reports")

    else:
        # Default: single health check
        report = monitor.perform_comprehensive_health_check()
        print(
            f"\n🏥 Health Check Complete - Status: {report.overall_status.value.upper()}"
        )


if __name__ == "__main__":
    main()
