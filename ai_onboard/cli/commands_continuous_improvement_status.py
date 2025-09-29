"""
Continuous Improvement Status Commands.

This module handles status and health-related commands for the continuous improvement system.
"""

import argparse
from pathlib import Path

from ai_onboard.core.continuous_improvement.continuous_improvement_analytics import (
    MetricType,
    get_continuous_improvement_analytics,
)
from ai_onboard.core.continuous_improvement.continuous_improvement_validator import (
    get_continuous_improvement_validator,
)
from ai_onboard.core.continuous_improvement.system_health_monitor import (
    get_system_health_monitor,
)


def add_status_commands(subparsers):
    """Add status-related commands to the CLI."""

    status_parser = subparsers.add_parser(
        "status",
        help="Check system status and health",
    )
    status_subparsers = status_parser.add_subparsers(
        dest="status_cmd", help="Status command"
    )

    # System status
    system_parser = status_subparsers.add_parser(
        "system", help="Show overall system status"
    )
    system_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed metrics"
    )

    # Health check
    health_parser = status_subparsers.add_parser(
        "health", help="Run system health check"
    )
    health_parser.add_argument("--component", help="Check specific component")

    # Analytics
    analytics_parser = status_subparsers.add_parser(
        "analytics", help="Show system analytics"
    )
    analytics_parser.add_argument(
        "--metric", choices=[m.value for m in MetricType], help="Specific metric"
    )
    analytics_parser.add_argument("--days", type=int, default=7, help="Days to include")

    # Validation
    validation_parser = status_subparsers.add_parser(
        "validate", help="Run system validation"
    )
    validation_parser.add_argument("--component", help="Validate specific component")


def _handle_status_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle status-related commands."""
    health_monitor = get_system_health_monitor(root)
    analytics = get_continuous_improvement_analytics(root)
    validator = get_continuous_improvement_validator(root)

    if args.status_cmd == "system":
        _handle_system_status(args, health_monitor)
    elif args.status_cmd == "health":
        _handle_health_check(args, health_monitor)
    elif args.status_cmd == "analytics":
        _handle_analytics(args, analytics)
    elif args.status_cmd == "validate":
        _handle_validation(args, validator)
    else:
        print("Unknown status command")


def _handle_system_status(args: argparse.Namespace, health_monitor) -> None:
    """Show overall system status."""
    try:
        status = health_monitor.get_system_status()

        print("System Status:")
        print(f"  Overall Health: {status.get('health_score', 0):.1f}/100")
        print(f"  Active Components: {status.get('active_components', 0)}")
        print(f"  Error Rate: {status.get('error_rate', 0):.2%}")
        print(f"  Response Time: {status.get('avg_response_time', 0):.2f}s")

        if args.detailed:
            metrics = health_monitor.get_detailed_metrics()
            print("Detailed Metrics:")
            for key, value in metrics.items():
                print(f"  {key}: {value}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error getting system status: {e}")


def _handle_health_check(args: argparse.Namespace, health_monitor) -> None:
    """Run system health check."""
    try:
        if args.component:
            # Check specific component
            health = health_monitor.check_component_health(args.component)
            print(f"Component Health ({args.component}):")
            print(f"  Status: {health.get('status', 'Unknown')}")
            print(f"  Score: {health.get('health_score', 0):.1f}/100")
        else:
            # Run full health check
            health_report = health_monitor.run_health_check()
            print("System Health Check:")
            print(f"  Overall Score: {health_report.get('overall_score', 0):.1f}/100")
            print(f"  Components Checked: {health_report.get('components_checked', 0)}")
            print(f"  Issues Found: {health_report.get('issues_found', 0)}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error running health check: {e}")


def _handle_analytics(args: argparse.Namespace, analytics) -> None:
    """Show system analytics."""
    try:
        if args.metric:
            # Show specific metric
            metric_data = analytics.get_metric_data(
                MetricType(args.metric), days=args.days
            )
            print(f"Metric: {args.metric}")
            print(f"  Current Value: {metric_data.get('current_value', 'Unknown')}")
            print(f"  Trend: {metric_data.get('trend', 'Unknown')}")
            print(f"  Data Points: {len(metric_data.get('data_points', []))}")
        else:
            # Show overview
            overview = analytics.get_analytics_overview(days=args.days)
            print("Analytics Overview:")
            print(f"  Total Events: {overview.get('total_events', 0)}")
            print(f"  Success Rate: {overview.get('success_rate', 0):.1%}")
            print(
                f"  Average Response Time: {overview.get('avg_response_time', 0):.2f}s"
            )

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error getting analytics: {e}")


def _handle_validation(args: argparse.Namespace, validator) -> None:
    """Run system validation."""
    try:
        if args.component:
            # Validate specific component
            validation = validator.validate_component(args.component)
            print(f"Component Validation ({args.component}):")
            print(f"  Valid: {validation.get('valid', False)}")
            print(f"  Score: {validation.get('validation_score', 0):.1f}/100")
        else:
            # Run full validation
            validation_report = validator.run_full_validation()
            print("System Validation:")
            print(f"  Overall Valid: {validation_report.get('overall_valid', False)}")
            print(
                f"  Components Validated: {validation_report.get('components_validated', 0)}"
            )
            print(f"  Issues Found: {validation_report.get('issues_found', 0)}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error running validation: {e}")
