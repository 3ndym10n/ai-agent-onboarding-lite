"""
Advanced Test Reporting CLI Commands.

This module provides CLI commands for generating, viewing, and managing
advanced test reports with comprehensive analytics.
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from ..core import utils
from ..core.advanced_test_reporting import (
    ReportFormat,
    ReportLevel,
    get_advanced_test_report_generator,
)
from ..core.continuous_improvement_validator import (
    ContinuousImprovementValidator,
    ValidationTestCase,
)


def add_advanced_test_reporting_commands(subparsers):
    """Add advanced test reporting commands to the CLI."""
    parser = subparsers.add_parser(
        "test - reports",
        help="Advanced test reporting and analytics",
        description="Generate comprehensive test reports with advanced analytics and \
            insights",
    )

    subcommands = parser.add_subparsers(
        dest="report_cmd", help="Test reporting commands"
    )

    # Generate report command
    generate_parser = subcommands.add_parser(
        "generate",
        help="Generate comprehensive test report",
        description="Generate advanced test report with analytics and insights",
    )
    generate_parser.add_argument(
        "--formats",
        nargs="+",
        choices=["html", "json", "csv", "markdown", "pdf"],
        default=["html", "json"],
        help="Output formats for the report",
    )
    generate_parser.add_argument(
        "--level",
        choices=["summary", "detailed", "comprehensive", "executive"],
        default="detailed",
        help="Report detail level",
    )
    generate_parser.add_argument(
        "--run - tests", action="store_true", help="Run tests before generating report"
    )
    generate_parser.add_argument(
        "--test - categories",
        nargs="+",
        choices=[
            "integration",
            "performance",
            "end_to_end",
            "data_integrity",
            "ci_validation",
        ],
        help="Specific test categories to run (if --run - tests is used)",
    )
    generate_parser.add_argument(
        "--output - dir", help="Custom output directory for reports"
    )

    # View reports command
    view_parser = subcommands.add_parser(
        "view",
        help="View existing test reports",
        description="View and browse existing test reports",
    )
    view_parser.add_argument("--report - id", help="Specific report ID to view")
    view_parser.add_argument(
        "--latest", action="store_true", help="View the latest report"
    )
    view_parser.add_argument(
        "--format",
        choices=["summary", "detailed", "json"],
        default="summary",
        help="Display format",
    )
    view_parser.add_argument(
        "--days", type=int, default=7, help="Show reports from last N days"
    )

    # Analytics command
    analytics_parser = subcommands.add_parser(
        "analytics",
        help="Test analytics and trends",
        description="Analyze test trends and performance over time",
    )
    analytics_parser.add_argument(
        "--metric",
        choices=["success_rate", "duration", "quality_score", "test_count"],
        help="Specific metric to analyze",
    )
    analytics_parser.add_argument(
        "--period", default="30d", help="Analysis period (e.g., '7d', '30d', '90d')"
    )
    analytics_parser.add_argument(
        "--format",
        choices=["table", "chart", "json"],
        default="table",
        help="Output format",
    )
    analytics_parser.add_argument(
        "--trend - analysis",
        action="store_true",
        help="Include detailed trend analysis",
    )

    # Quality command
    quality_parser = subcommands.add_parser(
        "quality",
        help="Test quality assessment",
        description="Assess and track test quality metrics",
    )
    quality_parser.add_argument(
        "--threshold", type=float, default=0.8, help="Quality threshold for alerts"
    )
    quality_parser.add_argument(
        "--benchmark", action="store_true", help="Compare with quality benchmarks"
    )
    quality_parser.add_argument(
        "--history",
        type=int,
        default=10,
        help="Number of historical reports to analyze",
    )

    # Export command
    export_parser = subcommands.add_parser(
        "export",
        help="Export test data",
        description="Export test results and analytics in various formats",
    )
    export_parser.add_argument(
        "--format", choices=["csv", "json", "xml"], default="csv", help="Export format"
    )
    export_parser.add_argument(
        "--data - type",
        choices=["results", "metrics", "trends", "all"],
        default="all",
        help="Type of data to export",
    )
    export_parser.add_argument("--period", default="30d", help="Time period to export")
    export_parser.add_argument("--output", help="Output file path")

    # Dashboard command
    dashboard_parser = subcommands.add_parser(
        "dashboard",
        help="Test reporting dashboard",
        description="Display comprehensive test reporting dashboard",
    )
    dashboard_parser.add_argument(
        "--refresh", type=int, help="Auto - refresh interval in seconds"
    )
    dashboard_parser.add_argument(
        "--compact", action="store_true", help="Compact dashboard view"
    )
    dashboard_parser.add_argument(
        "--metrics",
        nargs="+",
        choices=["success_rate", "quality", "performance", "trends"],
        default=["success_rate", "quality", "performance"],
        help="Metrics to display",
    )

    # Config command
    config_parser = subcommands.add_parser(
        "config",
        help="Configure test reporting",
        description="Configure test reporting settings and preferences",
    )
    config_parser.add_argument(
        "--set", nargs=2, metavar=("KEY", "VALUE"), help="Set configuration value"
    )
    config_parser.add_argument("--get", help="Get configuration value")
    config_parser.add_argument(
        "--list", action="store_true", help="List all configuration settings"
    )
    config_parser.add_argument(
        "--reset", action="store_true", help="Reset to default configuration"
    )


def handle_advanced_test_reporting_commands(
    args: argparse.Namespace, root: Path
) -> None:
    """Handle advanced test reporting commands."""
    if not hasattr(args, "report_cmd") or args.report_cmd is None:
        print(
            "❌ No test reporting command specified. Use --help for available commands."
        )
        return

    if args.report_cmd == "generate":
        _handle_generate_report(args, root)
    elif args.report_cmd == "view":
        _handle_view_reports(args, root)
    elif args.report_cmd == "analytics":
        _handle_analytics(args, root)
    elif args.report_cmd == "quality":
        _handle_quality_assessment(args, root)
    elif args.report_cmd == "export":
        _handle_export_data(args, root)
    elif args.report_cmd == "dashboard":
        _handle_dashboard(args, root)
    elif args.report_cmd == "config":
        _handle_config(args, root)
    else:
        print(f"❌ Unknown test reporting command: {args.report_cmd}")


def _handle_generate_report(args: argparse.Namespace, root: Path) -> None:
    """Handle report generation command."""
    print("📊 Generating Advanced Test Report")
    print("=" * 50)

    try:
        generator = get_advanced_test_report_generator(root)

        # Parse formats
        formats = [ReportFormat(fmt) for fmt in args.formats]
        level = ReportLevel(args.level)

        # Get test results
        test_results = []

        if args.run_tests:
            print("🧪 Running tests before generating report...")
            test_results = _run_tests_for_report(root, args.test_categories)
        else:
            # Load recent test results from validator
            validator = ContinuousImprovementValidator(root)
            print("📋 Loading recent test results...")

            # Run a quick validation to get current results
            validation_report = validator.run_comprehensive_validation()
            test_results = validation_report.test_results

        if not test_results:
            print(
                "⚠️ No test results available. Consider running tests first with --run - tests"
            )
            return

        print(f"📈 Analyzing {len(test_results)} test results...")

        # Generate comprehensive report
        report = generator.generate_comprehensive_report(
            test_results=test_results, report_level=level, output_formats=formats
        )

        # Display summary
        print(f"\n✅ Report Generated Successfully")
        print(f"📋 Report ID: {report.report_id}")
        print(
            f"🎯 Quality Grade: {report.quality_assessment.quality_grade.value.upper()}"
        )
        print(f"📊 Overall Score: {report.quality_assessment.overall_score:.1%}")
        print(f"✅ Success Rate: {report.test_metrics.success_rate:.1%}")
        print(f"⏱️ Total Duration: {report.test_metrics.total_duration:.2f}s")

        # Show output locations
        print(f"\n📁 Report Files Generated:")
        report_dir = root / ".ai_onboard" / "test_reports" / report.report_id
        for fmt in formats:
            if fmt == ReportFormat.HTML:
                print(f"   🌐 HTML: {report_dir / 'report.html'}")
            elif fmt == ReportFormat.JSON:
                print(f"   📄 JSON: {report_dir / 'report.json'}")
            elif fmt == ReportFormat.CSV:
                print(f"   📊 CSV: {report_dir / 'test_results.csv'}")
            elif fmt == ReportFormat.MARKDOWN:
                print(f"   📝 Markdown: {report_dir / 'report.md'}")

        # Show key insights
        if report.recommendations:
            print(f"\n💡 Top Recommendations:")
            for i, rec in enumerate(report.recommendations[:3], 1):
                print(f"   {i}. {rec}")

        # Show quality assessment
        if report.quality_assessment.areas_for_improvement:
            print(f"\n🎯 Areas for Improvement:")
            for area in report.quality_assessment.areas_for_improvement[:3]:
                print(f"   • {area}")

        if report.quality_assessment.strengths:
            print(f"\n✨ Strengths:")
            for strength in report.quality_assessment.strengths[:3]:
                print(f"   • {strength}")

    except Exception as e:
        print(f"❌ Error generating report: {e}")


def _handle_view_reports(args: argparse.Namespace, root: Path) -> None:
    """Handle view reports command."""
    print("📋 Test Reports")
    print("=" * 30)

    try:
        reports_dir = root / ".ai_onboard" / "test_reports"

        if not reports_dir.exists():
            print("⚠️ No test reports found. Generate a report first.")
            return

        if args.report_id:
            # View specific report
            _view_specific_report(args.report_id, reports_dir, args.format)
        elif args.latest:
            # View latest report
            _view_latest_report(reports_dir, args.format)
        else:
            # List recent reports
            _list_recent_reports(reports_dir, args.days, args.format)

    except Exception as e:
        print(f"❌ Error viewing reports: {e}")


def _handle_analytics(args: argparse.Namespace, root: Path) -> None:
    """Handle analytics command."""
    print("📈 Test Analytics")
    print("=" * 30)

    try:
        # Load historical data
        history_file = root / ".ai_onboard" / "test_reports" / "report_history.jsonl"

        if not history_file.exists():
            print("⚠️ No historical data available. Generate some reports first.")
            return

        # Parse period
        period_days = _parse_period(args.period)
        cutoff_date = datetime.now() - timedelta(days=period_days)

        # Load and filter historical data
        historical_data = []
        with open(history_file, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line.strip())
                    report_date = datetime.fromisoformat(data["timestamp"])
                    if report_date >= cutoff_date:
                        historical_data.append(data)

        if not historical_data:
            print(f"⚠️ No data found for the last {period_days} days")
            return

        # Display analytics
        if args.metric:
            _display_metric_analytics(historical_data, args.metric, args.format)
        else:
            _display_general_analytics(
                historical_data, args.format, args.trend_analysis
            )

    except Exception as e:
        print(f"❌ Error generating analytics: {e}")


def _handle_quality_assessment(args: argparse.Namespace, root: Path) -> None:
    """Handle quality assessment command."""
    print("🎯 Test Quality Assessment")
    print("=" * 40)

    try:
        # Load recent reports
        history_file = root / ".ai_onboard" / "test_reports" / "report_history.jsonl"

        if not history_file.exists():
            print("⚠️ No historical data available for quality assessment.")
            return

        # Load recent data
        recent_data = []
        with open(history_file, "r") as f:
            lines = f.readlines()
            for line in lines[-args.history :]:
                if line.strip():
                    recent_data.append(json.loads(line.strip()))

        if not recent_data:
            print("⚠️ No recent data available")
            return

        # Calculate quality metrics
        latest_report = recent_data[-1]

        print(f"📊 Current Quality Status")
        print("-" * 30)
        print(f"Quality Score: {latest_report['quality_score']:.1%}")
        print(f"Quality Grade: {latest_report['quality_grade'].upper()}")
        print(f"Success Rate: {latest_report['success_rate']:.1%}")
        print(f"Average Duration: {latest_report['average_duration']:.2f}s")

        # Quality threshold check
        if latest_report["quality_score"] < args.threshold:
            print(
                f"\n⚠️ Quality Alert: Score {latest_report['quality_score']:.1%} is below threshold {args.threshold:.1%}"
            )
        else:
            print(
                f"\n✅ Quality Status: Score {latest_report['quality_score']:.1%} meets threshold {args.threshold:.1%}"
            )

        # Historical trend
        if len(recent_data) >= 3:
            scores = [r["quality_score"] for r in recent_data]
            trend = _calculate_simple_trend(scores)

            trend_icon = "📈" if trend > 0.01 else "📉" if trend < -0.01 else "➡️"
            print(
                f"\n{trend_icon} Quality Trend: {trend:+.1%} over last {len(recent_data)} reports"
            )

        # Benchmark comparison
        if args.benchmark:
            print(f"\n📏 Benchmark Comparison")
            print("-" * 25)

            benchmarks = {"Excellent": 0.95, "Good": 0.80, "Fair": 0.65, "Poor": 0.50}

            current_score = latest_report["quality_score"]
            for level, threshold in benchmarks.items():
                status = "✅" if current_score >= threshold else "❌"
                print(
                    f"{status} {level}: {threshold:.0%} (Current: {current_score:.1%})"
                )

    except Exception as e:
        print(f"❌ Error in quality assessment: {e}")


def _handle_export_data(args: argparse.Namespace, root: Path) -> None:
    """Handle data export command."""
    print("📤 Exporting Test Data")
    print("=" * 30)

    try:
        # Determine output file
        if args.output:
            output_file = Path(args.output)
        else:
            timestamp = datetime.now().strftime("%Y % m % d_ % H % M % S")
            output_file = root / f"test_export_{timestamp}.{args.format}"

        # Load data based on period
        period_days = _parse_period(args.period)
        cutoff_date = datetime.now() - timedelta(days=period_days)

        # Export based on format and data type
        if args.format == "csv":
            _export_csv(root, output_file, args.data_type, cutoff_date)
        elif args.format == "json":
            _export_json(root, output_file, args.data_type, cutoff_date)
        elif args.format == "xml":
            _export_xml(root, output_file, args.data_type, cutoff_date)

        print(f"✅ Data exported to: {output_file}")

    except Exception as e:
        print(f"❌ Error exporting data: {e}")


def _handle_dashboard(args: argparse.Namespace, root: Path) -> None:
    """Handle dashboard command."""
    print("📊 Test Reporting Dashboard")
    print("=" * 40)

    try:
        # Load latest data
        history_file = root / ".ai_onboard" / "test_reports" / "report_history.jsonl"

        if not history_file.exists():
            print("⚠️ No data available for dashboard")
            return

        # Load recent reports
        recent_reports = []
        with open(history_file, "r") as f:
            lines = f.readlines()
            for line in lines[-10:]:  # Last 10 reports
                if line.strip():
                    recent_reports.append(json.loads(line.strip()))

        if not recent_reports:
            print("⚠️ No recent reports available")
            return

        latest = recent_reports[-1]

        if args.compact:
            _display_compact_dashboard(latest, recent_reports, args.metrics)
        else:
            _display_full_dashboard(latest, recent_reports, args.metrics)

    except Exception as e:
        print(f"❌ Error displaying dashboard: {e}")


def _handle_config(args: argparse.Namespace, root: Path) -> None:
    """Handle configuration command."""
    print("⚙️ Test Reporting Configuration")
    print("=" * 40)

    try:
        config_file = root / ".ai_onboard" / "test_reporting_config.json"

        if args.reset:
            # Reset configuration
            if config_file.exists():
                config_file.unlink()
            print("✅ Configuration reset to defaults")
            return

        # Load current config
        config = utils.read_json(config_file, default={})

        if args.set:
            # Set configuration value
            key, value = args.set

            # Parse value type
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "").isdigit():
                value = float(value)

            # Set nested keys
            keys = key.split(".")
            current = config
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value

            # Save config
            utils.write_json(config_file, config)
            print(f"✅ Set {key} = {value}")

        elif args.get:
            # Get configuration value
            keys = args.get.split(".")
            current = config
            try:
                for key in keys:
                    current = current[key]
                print(f"{args.get} = {current}")
            except KeyError:
                print(f"❌ Configuration key '{args.get}' not found")

        elif args.list:
            # List all configuration
            print("Current Configuration:")
            print("-" * 25)
            _print_config_recursive(config, "")

        else:
            print("❌ No configuration action specified")

    except Exception as e:
        print(f"❌ Error managing configuration: {e}")

# Helper functions

def _run_tests_for_report(
    root: Path, categories: Optional[List[str]]
) -> List[ValidationTestCase]:
    """Run tests and return results."""
    try:
        validator = ContinuousImprovementValidator(root)

        if categories:
            # Run specific categories
            test_results = []
            for category in categories:
                if category == "integration":
                    test_results.extend(validator._run_integration_tests())
                elif category == "performance":
                    test_results.extend(validator._run_performance_tests())
                elif category == "end_to_end":
                    test_results.extend(validator._run_end_to_end_tests())
                elif category == "data_integrity":
                    test_results.extend(validator._run_data_integrity_tests())
            return test_results
        else:
            # Run comprehensive validation
            report = validator.run_comprehensive_validation()
            return report.test_results

    except Exception as e:
        print(f"⚠️ Error running tests: {e}")
        return []


def _view_specific_report(report_id: str, reports_dir: Path, format_type: str):
    """View a specific report."""
    report_dir = reports_dir / report_id

    if not report_dir.exists():
        print(f"❌ Report {report_id} not found")
        return

    if format_type == "json":
        json_file = report_dir / "report.json"
        if json_file.exists():
            with open(json_file, "r") as f:
                report_data = json.load(f)
                print(json.dumps(report_data, indent=2))
        else:
            print("❌ JSON report file not found")
    else:
        # Load and display summary
        json_file = report_dir / "report.json"
        if json_file.exists():
            with open(json_file, "r") as f:
                report_data = json.load(f)
                _display_report_summary(report_data, format_type == "detailed")


def _view_latest_report(reports_dir: Path, format_type: str):
    """View the latest report."""
    # Find latest report directory
    report_dirs = [d for d in reports_dir.iterdir() if d.is_dir()]
    if not report_dirs:
        print("❌ No reports found")
        return

    latest_dir = max(report_dirs, key=lambda d: d.stat().st_mtime)
    _view_specific_report(latest_dir.name, reports_dir, format_type)


def _list_recent_reports(reports_dir: Path, days: int, format_type: str):
    """List recent reports."""
    cutoff_date = datetime.now() - timedelta(days=days)

    # Load report history
    history_file = reports_dir / "report_history.jsonl"
    if not history_file.exists():
        print("❌ No report history found")
        return

    recent_reports = []
    with open(history_file, "r") as f:
        for line in f:
            if line.strip():
                data = json.loads(line.strip())
                report_date = datetime.fromisoformat(data["timestamp"])
                if report_date >= cutoff_date:
                    recent_reports.append(data)

    if not recent_reports:
        print(f"❌ No reports found in the last {days} days")
        return

    # Sort by timestamp (newest first)
    recent_reports.sort(key=lambda x: x["timestamp"], reverse=True)

    print(f"📋 Recent Reports (Last {days} days)")
    print("-" * 60)
    print(f"{'Report ID':<25} {'Date':<20} {'Quality':<10} {'Success Rate':<12}")
    print("-" * 60)

    for report in recent_reports:
        report_date = datetime.fromisoformat(report["timestamp"]).strftime(
            "%Y -% m -% d %H:%M"
        )
        quality_grade = report["quality_grade"][:4].upper()

        print(
            f"{report['report_id']:<25} {report_date:<20} "
            f"{quality_grade:<10} {report['success_rate']:>10.1%}"
        )


def _display_metric_analytics(data: List[Dict], metric: str, format_type: str):
    """Display analytics for a specific metric."""
    values = [d[metric] for d in data if metric in d]

    if not values:
        print(f"❌ No data found for metric: {metric}")
        return

    print(f"📊 {metric.replace('_', ' ').title()} Analytics")
    print("-" * 40)

    # Basic statistics
    import statistics

    print(f"Count: {len(values)}")
    print(f"Average: {statistics.mean(values):.3f}")
    print(f"Median: {statistics.median(values):.3f}")
    print(f"Min: {min(values):.3f}")
    print(f"Max: {max(values):.3f}")
    if len(values) > 1:
        print(f"Std Dev: {statistics.stdev(values):.3f}")

    # Trend
    if len(values) >= 3:
        trend = _calculate_simple_trend(values)
        trend_icon = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
        print(f"Trend: {trend_icon} {trend:+.3f}")

    # Chart
    if format_type == "chart":
        _display_simple_chart(values, metric)


def _display_general_analytics(
    data: List[Dict], format_type: str, include_trends: bool
):
    """Display general analytics."""
    if not data:
        return

    print(f"📊 General Test Analytics ({len(data)} reports)")
    print("-" * 50)

    # Success rate analytics
    success_rates = [d["success_rate"] for d in data]
    print(
        f"Success Rate: {statistics.mean(success_rates):.1%} ± {statistics.stdev(success_rates):.1%}"
    )

    # Quality score analytics
    quality_scores = [d["quality_score"] for d in data]
    print(
        f"Quality Score: {statistics.mean(quality_scores):.1%} ± {statistics.stdev(quality_scores):.1%}"
    )

    # Duration analytics
    durations = [d["average_duration"] for d in data]
    print(
        f"Avg Duration: {statistics.mean(durations):.2f}s ± {statistics.stdev(durations):.2f}s"
    )

    # Test count analytics
    test_counts = [d["total_tests"] for d in data]
    print(
        f"Test Count: {statistics.mean(test_counts):.0f} ± {statistics.stdev(test_counts):.0f}"
    )

    if include_trends:
        print("\n📈 Trend Analysis")
        print("-" * 20)

        metrics = {
            "Success Rate": success_rates,
            "Quality Score": quality_scores,
            "Avg Duration": durations,
            "Test Count": test_counts,
        }

        for name, values in metrics.items():
            if len(values) >= 3:
                trend = _calculate_simple_trend(values)
                trend_icon = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
                print(f"{trend_icon} {name}: {trend:+.3f}")


def _display_compact_dashboard(latest: Dict, recent: List[Dict], metrics: List[str]):
    """Display compact dashboard."""
    print(f"📊 Quick Status")
    print("-" * 20)

    if "success_rate" in metrics:
        rate = latest["success_rate"]
        status = "🟢" if rate >= 0.9 else "🟡" if rate >= 0.8 else "🔴"
        print(f"Success Rate: {status} {rate:.1%}")

    if "quality" in metrics:
        score = latest["quality_score"]
        grade = latest["quality_grade"]
        status = "🟢" if score >= 0.9 else "🟡" if score >= 0.8 else "🔴"
        print(f"Quality: {status} {grade.upper()} ({score:.1%})")

    if "performance" in metrics:
        duration = latest["average_duration"]
        status = "🟢" if duration <= 2.0 else "🟡" if duration <= 5.0 else "🔴"
        print(f"Performance: {status} {duration:.2f}s avg")

    if "trends" in metrics and len(recent) >= 3:
        success_trend = _calculate_simple_trend([r["success_rate"] for r in recent])
        trend_icon = (
            "📈" if success_trend > 0.01 else "📉" if success_trend < -0.01 else "➡️"
        )
        print(f"Trend: {trend_icon} {success_trend:+.1%}")


def _display_full_dashboard(latest: Dict, recent: List[Dict], metrics: List[str]):
    """Display full dashboard."""
    print(f"📊 Test Reporting Dashboard")
    print("-" * 40)

    # Current status
    print(f"\n📋 Current Status")
    print(f"Report ID: {latest['report_id']}")
    print(
        f"Generated: {datetime.fromisoformat(latest['timestamp']).strftime('%Y -% m -% d %H:%M')}"
    )
    print(f"Total Tests: {latest['total_tests']}")

    if "success_rate" in metrics:
        print(f"\n✅ Success Metrics")
        print(f"Success Rate: {latest['success_rate']:.1%}")
        if len(recent) >= 2:
            prev_rate = recent[-2]["success_rate"]
            change = latest["success_rate"] - prev_rate
            trend_icon = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            print(f"Change: {trend_icon} {change:+.1%}")

    if "quality" in metrics:
        print(f"\n🎯 Quality Assessment")
        print(f"Quality Score: {latest['quality_score']:.1%}")
        print(f"Quality Grade: {latest['quality_grade'].upper()}")

        if len(recent) >= 3:
            quality_scores = [r["quality_score"] for r in recent]
            trend = _calculate_simple_trend(quality_scores)
            trend_icon = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
            print(f"Trend: {trend_icon} {trend:+.1%}")

    if "performance" in metrics:
        print(f"\n⚡ Performance Metrics")
        print(f"Average Duration: {latest['average_duration']:.2f}s")

        if len(recent) >= 2:
            prev_duration = recent[-2]["average_duration"]
            change = latest["average_duration"] - prev_duration
            trend_icon = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            print(f"Change: {trend_icon} {change:+.2f}s")

    # Historical summary
    print(f"\n📈 Historical Summary (Last {len(recent)} reports)")
    success_rates = [r["success_rate"] for r in recent]
    quality_scores = [r["quality_score"] for r in recent]

    print(f"Success Rate Range: {min(success_rates):.1%} - {max(success_rates):.1%}")
    print(f"Quality Score Range: {min(quality_scores):.1%} - {max(quality_scores):.1%}")


def _export_csv(root: Path, output_file: Path, data_type: str, cutoff_date: datetime):
    """Export data as CSV."""
    import csv

    history_file = root / ".ai_onboard" / "test_reports" / "report_history.jsonl"

    if not history_file.exists():
        raise ValueError("No historical data available")

    # Load data
    data = []
    with open(history_file, "r") as f:
        for line in f:
            if line.strip():
                record = json.loads(line.strip())
                record_date = datetime.fromisoformat(record["timestamp"])
                if record_date >= cutoff_date:
                    data.append(record)

    # Write CSV
    with open(output_file, "w", newline="", encoding="utf - 8") as f:
        if data_type in ["results", "all"]:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)


def _export_json(root: Path, output_file: Path, data_type: str, cutoff_date: datetime):
    """Export data as JSON."""
    history_file = root / ".ai_onboard" / "test_reports" / "report_history.jsonl"

    if not history_file.exists():
        raise ValueError("No historical data available")

    # Load data
    data = []
    with open(history_file, "r") as f:
        for line in f:
            if line.strip():
                record = json.loads(line.strip())
                record_date = datetime.fromisoformat(record["timestamp"])
                if record_date >= cutoff_date:
                    data.append(record)

    # Write JSON
    with open(output_file, "w", encoding="utf - 8") as f:
        json.dump(data, f, indent=2)


def _export_xml(root: Path, output_file: Path, data_type: str, cutoff_date: datetime):
    """Export data as XML."""
    # Basic XML export implementation
    history_file = root / ".ai_onboard" / "test_reports" / "report_history.jsonl"

    if not history_file.exists():
        raise ValueError("No historical data available")

    # Load data
    data = []
    with open(history_file, "r") as f:
        for line in f:
            if line.strip():
                record = json.loads(line.strip())
                record_date = datetime.fromisoformat(record["timestamp"])
                if record_date >= cutoff_date:
                    data.append(record)

    # Write XML
    with open(output_file, "w", encoding="utf - 8") as f:
        f.write('<?xml version="1.0" encoding="UTF - 8"?>\n')
        f.write("<test_reports>\n")

        for record in data:
            f.write("  <report>\n")
            for key, value in record.items():
                f.write(f"    <{key}>{value}</{key}>\n")
            f.write("  </report>\n")

        f.write("</test_reports>\n")


def _display_report_summary(report_data: Dict, detailed: bool):
    """Display report summary."""
    print(f"📋 Report: {report_data['report_id']}")
    print(f"Generated: {report_data['generated_at']}")
    print(f"Level: {report_data['report_level']}")

    metrics = report_data["test_metrics"]
    print(f"\n📊 Test Metrics:")
    print(f"  Total Tests: {metrics['total_tests']}")
    print(f"  Success Rate: {metrics['success_rate']:.1%}")
    print(f"  Total Duration: {metrics['total_duration']:.2f}s")

    quality = report_data["quality_assessment"]
    print(f"\n🎯 Quality Assessment:")
    print(f"  Overall Score: {quality['overall_score']:.1%}")
    print(f"  Quality Grade: {quality['quality_grade'].upper()}")

    if detailed:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(report_data.get("recommendations", [])[:5], 1):
            print(f"  {i}. {rec}")


def _parse_period(period: str) -> int:
    """Parse period string to days."""
    if period.endswith("d"):
        return int(period[:-1])
    elif period.endswith("w"):
        return int(period[:-1]) * 7
    elif period.endswith("m"):
        return int(period[:-1]) * 30
    else:
        return int(period)  # Assume days


def _calculate_simple_trend(values: List[float]) -> float:
    """Calculate simple linear trend."""
    if len(values) < 2:
        return 0.0

    n = len(values)
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(values) / n

    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, values))
    denominator = sum((xi - x_mean) ** 2 for xi in x)

    return numerator / denominator if denominator > 0 else 0.0


def _display_simple_chart(values: List[float], metric: str):
    """Display simple ASCII chart."""
    if len(values) < 2:
        return

    print(f"\n📊 {metric.replace('_', ' ').title()} Chart")
    print("-" * 30)

    # Normalize values for display
    min_val = min(values)
    max_val = max(values)
    range_val = max_val - min_val if max_val != min_val else 1

    for i, value in enumerate(values):
        normalized = int(((value - min_val) / range_val) * 20)
        bar = "█" * normalized + "░" * (20 - normalized)
        print(f"T{i + 1:2d}: [{bar}] {value:.3f}")


def _print_config_recursive(config: Dict, prefix: str):
    """Print configuration recursively."""
    for key, value in config.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            _print_config_recursive(value, full_key)
        else:
            print(f"  {full_key} = {value}")

import statistics
