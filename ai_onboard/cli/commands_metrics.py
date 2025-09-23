"""
CLI commands for the Unified Metrics Collection System.

This module provides command - line interfaces for:
- Querying collected metrics with filtering and aggregation
- Generating performance and usage reports
- Managing alerts and thresholds
- Exporting metrics data in various formats
"""

import argparse
import csv
import io
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from ..core import unified_metrics_collector
from ..core.unified_metrics_collector import MetricCategory, MetricQuery, MetricSource


def add_metrics_commands(subparsers):
    """Add metrics - related commands to the CLI."""

    # Main unified metrics command
    metrics_parser = subparsers.add_parser(
        "unified - metrics", help="Unified metrics collection and analysis"
    )
    metrics_sub = metrics_parser.add_subparsers(dest="metrics_cmd", required=True)

    # Query command
    query_parser = metrics_sub.add_parser("query", help="Query collected metrics")
    query_parser.add_argument(
        "--metric", help="Metric name or pattern (supports wildcards)"
    )
    query_parser.add_argument(
        "--source", choices=[s.value for s in MetricSource], help="Metric source"
    )
    query_parser.add_argument(
        "--category", choices=[c.value for c in MetricCategory], help="Metric category"
    )
    query_parser.add_argument("--last", help="Time period (e.g., '1h', '24h', '7d')")
    query_parser.add_argument("--start", help="Start time (ISO format)")
    query_parser.add_argument("--end", help="End time (ISO format)")
    query_parser.add_argument("--limit", type=int, default=100, help="Maximum results")
    query_parser.add_argument(
        "--agg",
        choices=["sum", "avg", "min", "max", "count"],
        help="Aggregation function",
    )
    query_parser.add_argument(
        "--format",
        choices=["json", "table", "csv"],
        default="table",
        help="Output format",
    )
    query_parser.add_argument(
        "--dimension", action="append", help="Filter by dimension (key = value)"
    )

    # Trend command
    trend_parser = metrics_sub.add_parser("trend", help="Show metric trends over time")
    trend_parser.add_argument("--metric", required=True, help="Metric name")
    trend_parser.add_argument(
        "--days", type=int, default=7, help="Number of days to analyze"
    )
    trend_parser.add_argument(
        "--interval", default="1h", help="Time interval for grouping"
    )
    trend_parser.add_argument(
        "--format",
        choices=["json", "table", "chart"],
        default="table",
        help="Output format",
    )

    # Stats command
    stats_parser = metrics_sub.add_parser("stats", help="Show collection statistics")
    stats_parser.add_argument(
        "--format", choices=["json", "table"], default="table", help="Output format"
    )

    # Alert command
    alert_parser = metrics_sub.add_parser("alert", help="Manage metric alerts")
    alert_sub = alert_parser.add_subparsers(dest="alert_action", required=True)

    # Alert list
    alert_list_parser = alert_sub.add_parser("list", help="List active alerts")
    alert_list_parser.add_argument(
        "--severity",
        choices=["low", "medium", "high", "critical"],
        help="Filter by severity",
    )

    # Alert create
    alert_create_parser = alert_sub.add_parser("create", help="Create alert rule")
    alert_create_parser.add_argument("--metric", required=True, help="Metric name")
    alert_create_parser.add_argument(
        "--condition", required=True, help="Condition (e.g., '> 90')"
    )
    alert_create_parser.add_argument(
        "--severity", choices=["low", "medium", "high", "critical"], default="medium"
    )

    # Report command
    report_parser = metrics_sub.add_parser("report", help="Generate metrics reports")
    report_parser.add_argument(
        "--type",
        choices=["performance", "usage", "health", "custom"],
        default="performance",
    )
    report_parser.add_argument("--period", default="24h", help="Report period")
    report_parser.add_argument(
        "--format", choices=["json", "html", "csv"], default="json"
    )
    report_parser.add_argument("--output", help="Output file path")

    # Export command
    export_parser = metrics_sub.add_parser("export", help="Export metrics data")
    export_parser.add_argument(
        "--start", required=True, help="Start date (YYYY - MM - DD)"
    )
    export_parser.add_argument(
        "--end", help="End date (YYYY - MM - DD, default: today)"
    )
    export_parser.add_argument(
        "--format", choices=["json", "csv", "jsonl"], default="csv"
    )
    export_parser.add_argument("--output", required=True, help="Output file path")
    export_parser.add_argument("--metric", help="Specific metric to export")


def handle_metrics_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle metrics commands."""
    collector = unified_metrics_collector.get_unified_metrics_collector(root)

    if args.metrics_cmd == "query":
        _handle_metrics_query(args, collector)
    elif args.metrics_cmd == "trend":
        _handle_metrics_trend(args, collector)
    elif args.metrics_cmd == "stats":
        _handle_metrics_stats(args, collector)
    elif args.metrics_cmd == "alert":
        _handle_metrics_alert(args, collector)
    elif args.metrics_cmd == "report":
        _handle_metrics_report(args, collector)
    elif args.metrics_cmd == "export":
        _handle_metrics_export(args, collector)
    else:
        print(f"Unknown metrics command: {args.metrics_cmd}")


def _handle_metrics_query(args: argparse.Namespace, collector) -> None:
    """Handle metrics query command."""
    # Build query
    query = MetricQuery()

    if args.metric:
        query.name_pattern = args.metric

    if args.source:
        query.source = MetricSource(args.source)

    if args.category:
        query.category = MetricCategory(args.category)

    if args.limit:
        query.limit = args.limit

    if args.agg:
        query.aggregation = args.agg

    # Parse time ranges
    if args.last:
        query.end_time = datetime.now()
        query.start_time = _parse_time_period(args.last)
    else:
        if args.start:
            query.start_time = datetime.fromisoformat(args.start)
        if args.end:
            query.end_time = datetime.fromisoformat(args.end)

    # Parse dimensions
    if args.dimension:
        for dim in args.dimension:
            if "=" in dim:
                key, value = dim.split("=", 1)
                query.dimensions[key] = value

    # Execute query
    result = collector.query_metrics(query)

    # Output results
    if args.format == "json":
        _output_json_result(result)
    elif args.format == "csv":
        _output_csv_result(result)
    else:  # table
        _output_table_result(result, query.aggregation)


def _handle_metrics_trend(args: argparse.Namespace, collector) -> None:
    """Handle metrics trend command."""
    # Query metrics for trend analysis
    end_time = datetime.now()
    start_time = end_time - timedelta(days=args.days)

    query = MetricQuery(
        name_pattern=args.metric,
        start_time=start_time,
        end_time=end_time,
        limit=10000,  # Large limit for trend analysis
    )

    result = collector.query_metrics(query)

    if not result.metrics:
        print(f"📊 No data found for metric: {args.metric}")
        return

    # Group by time intervals
    intervals = _group_by_interval(result.metrics, args.interval)

    if args.format == "json":
        print(json.dumps(intervals, indent=2, default=str))
    elif args.format == "chart":
        _display_ascii_chart(intervals, args.metric)
    else:  # table
        _display_trend_table(intervals, args.metric)


def _handle_metrics_stats(args: argparse.Namespace, collector) -> None:
    """Handle metrics stats command."""
    stats = collector.get_collection_stats()

    if args.format == "json":
        print(json.dumps(stats, indent=2, default=str))
    else:  # table
        print("📊 Metrics Collection Statistics")
        print("=" * 40)
        print(f"Total Collected: {stats['total_collected']:,}")
        print(f"Collection Errors: {stats['collection_errors']:,}")
        print(f"Avg Collection Time: {stats['avg_collection_time_ms']:.2f}ms")
        print(f"Hot Storage Count: {stats['hot_storage_count']:,}")
        print(f"Indexed Metrics: {stats['indexed_metrics']:,}")
        print(f"Active Alerts: {stats['active_alerts']:,}")
        if stats["last_collection_time"]:
            print(f"Last Collection: {stats['last_collection_time']}")


def _handle_metrics_alert(args: argparse.Namespace, collector) -> None:
    """Handle metrics alert commands."""
    if args.alert_action == "list":
        alerts = list(collector.active_alerts.values())

        if args.severity:
            alerts = [a for a in alerts if a.severity == args.severity]

        if not alerts:
            print("🔕 No active alerts")
            return

        print(f"🚨 Active Alerts ({len(alerts)})")
        print("=" * 60)

        for alert in sorted(alerts, key=lambda a: a.timestamp, reverse=True):
            severity_icon = {
                "low": "🟡",
                "medium": "🟠",
                "high": "🔴",
                "critical": "💥",
            }
            icon = severity_icon.get(alert.severity, "⚪")

            print(f"{icon} {alert.metric_name}: {alert.current_value}")
            print(f"   Condition: {alert.condition}")
            print(f"   Time: {alert.timestamp.strftime('%Y -% m -% d %H:%M:%S')}")
            print(f"   Actions: {', '.join(alert.suggested_actions[:2])}")
            print()

    elif args.alert_action == "create":
        # Parse condition
        condition_parts = args.condition.split()
        if len(condition_parts) != 2:
            print("❌ Invalid condition format. Use: '> 90' or '< 0.05'")
            return

        operator, threshold_str = condition_parts
        try:
            threshold = float(threshold_str)
        except ValueError:
            print(f"❌ Invalid threshold value: {threshold_str}")
            return

        # Add to collector's alert rules
        collector.alert_rules[args.metric] = {
            "threshold": threshold,
            "condition": operator,
            "severity": args.severity,
        }

        # Save configuration
        collector.config["alert_rules"] = collector.alert_rules
        with open(collector.config_path, "w") as f:
            json.dump(collector.config, f, indent=2)

        print(
            f"✅ Alert rule created: {args.metric} {args.condition} (severity: {args.severity})"
        )


def _handle_metrics_report(args: argparse.Namespace, collector) -> None:
    """Handle metrics report generation."""
    # Parse period
    end_time = datetime.now()
    start_time = _parse_time_period(args.period)

    # Generate report based on type
    if args.type == "performance":
        report = _generate_performance_report(collector, start_time, end_time)
    elif args.type == "usage":
        report = _generate_usage_report(collector, start_time, end_time)
    elif args.type == "health":
        report = _generate_health_report(collector, start_time, end_time)
    else:
        report = {"error": f"Unknown report type: {args.type}"}

    # Output report
    if args.format == "json":
        output = json.dumps(report, indent=2, default=str)
    elif args.format == "html":
        output = _generate_html_report(report, args.type)
    else:  # csv
        output = _generate_csv_report(report)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"📄 Report saved to: {args.output}")
    else:
        print(output)


def _handle_metrics_export(args: argparse.Namespace, collector) -> None:
    """Handle metrics data export."""
    # Parse dates
    start_date = datetime.strptime(args.start, "%Y -% m -% d")
    end_date = (
        datetime.strptime(args.end, "%Y -% m -% d") if args.end else datetime.now()
    )

    # Query metrics
    query = MetricQuery(
        name_pattern=args.metric,
        start_time=start_date,
        end_time=end_date,
        limit=100000,  # Large limit for export
    )

    result = collector.query_metrics(query)

    if not result.metrics:
        print("📦 No metrics found for export criteria")
        return

    # Export in requested format
    if args.format == "json":
        data = [
            {
                "id": m.id,
                "name": m.name,
                "value": m.value,
                "source": m.source.value,
                "category": m.category.value,
                "timestamp": m.timestamp.isoformat(),
                "unit": m.unit,
                "dimensions": m.dimensions,
                "metadata": m.metadata,
            }
            for m in result.metrics
        ]
        with open(args.output, "w") as f:
            json.dump(data, f, indent=2)

    elif args.format == "csv":
        with open(args.output, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["id", "name", "value", "source", "category", "timestamp", "unit"]
            )

            for m in result.metrics:
                writer.writerow(
                    [
                        m.id,
                        m.name,
                        m.value,
                        m.source.value,
                        m.category.value,
                        m.timestamp.isoformat(),
                        m.unit or "",
                    ]
                )

    else:  # jsonl
        with open(args.output, "w") as f:
            for m in result.metrics:
                data = {
                    "id": m.id,
                    "name": m.name,
                    "value": m.value,
                    "source": m.source.value,
                    "category": m.category.value,
                    "timestamp": m.timestamp.isoformat(),
                    "unit": m.unit,
                    "dimensions": m.dimensions,
                    "metadata": m.metadata,
                }
                f.write(json.dumps(data) + "\n")

    print(f"📦 Exported {len(result.metrics)} metrics to: {args.output}")


def _parse_time_period(period: str) -> datetime:
    """Parse time period string like '1h', '24h', '7d' into datetime."""
    now = datetime.now()

    if period.endswith("h"):
        hours = int(period[:-1])
        return now - timedelta(hours=hours)
    elif period.endswith("d"):
        days = int(period[:-1])
        return now - timedelta(days=days)
    elif period.endswith("m"):
        minutes = int(period[:-1])
        return now - timedelta(minutes=minutes)
    else:
        raise ValueError(f"Invalid time period: {period}")


def _output_json_result(result) -> None:
    """Output query result as JSON."""
    data = {
        "total_count": result.total_count,
        "query_time_ms": result.query_time_ms,
        "aggregated_value": result.aggregated_value,
        "metrics": [
            {
                "id": m.id,
                "name": m.name,
                "value": m.value,
                "source": m.source.value,
                "category": m.category.value,
                "timestamp": m.timestamp.isoformat(),
                "unit": m.unit,
                "dimensions": m.dimensions,
            }
            for m in result.metrics
        ],
    }
    print(json.dumps(data, indent=2))


def _output_csv_result(result) -> None:
    """Output query result as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["name", "value", "source", "category", "timestamp", "unit"])
    for m in result.metrics:
        writer.writerow(
            [
                m.name,
                m.value,
                m.source.value,
                m.category.value,
                m.timestamp.isoformat(),
                m.unit or "",
            ]
        )

    print(output.getvalue())


def _output_table_result(result, aggregation) -> None:
    """Output query result as formatted table."""
    print(
        f"📊 Query Results ({result.total_count} metrics, {result.query_time_ms:.1f}ms)"
    )

    if aggregation and result.aggregated_value is not None:
        print(f"🔢 {aggregation.upper()}: {result.aggregated_value}")

    if not result.metrics:
        print("No metrics found")
        return

    print("=" * 80)
    print(f"{'Metric':<25} {'Value':<12} {'Source':<12} {'Category':<12} {'Time':<16}")
    print("-" * 80)

    for m in result.metrics[:20]:  # Limit display
        timestamp_str = m.timestamp.strftime("%m -% d %H:%M:%S")
        unit_str = f" {m.unit}" if m.unit else ""
        print(
            f"{m.name:<25} {m.value:<12}{unit_str} {m.source.value:<12} {m.category.value:<12} {timestamp_str:<16}"
        )

    if len(result.metrics) > 20:
        print(f"... and {len(result.metrics) - 20} more")


def _group_by_interval(metrics, interval: str) -> Dict[str, List]:
    """Group metrics by time interval."""
    from collections import defaultdict

    # Parse interval
    if interval.endswith("h"):
        interval_hours = int(interval[:-1])
    elif interval.endswith("m"):
        interval_hours = int(interval[:-1]) / 60
    else:
        interval_hours = 1

    groups = defaultdict(list)

    for metric in metrics:
        # Round timestamp to interval
        timestamp = metric.timestamp
        interval_start = timestamp.replace(
            minute=0, second=0, microsecond=0
        ) - timedelta(hours=timestamp.hour % interval_hours)

        key = interval_start.strftime("%Y -% m -% d %H:%M")
        groups[key].append(metric.value)

    # Calculate aggregates for each interval
    result = {}
    for key, values in groups.items():
        result[key] = {
            "count": len(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "sum": sum(values),
        }

    return result


def _display_ascii_chart(intervals: Dict, metric_name: str) -> None:
    """Display ASCII chart of trend data."""
    print(f"📈 Trend Chart: {metric_name}")
    print("=" * 60)

    if not intervals:
        print("No data to chart")
        return

    # Get values for charting
    sorted_intervals = sorted(intervals.items())
    values = [data["avg"] for _, data in sorted_intervals]

    if not values:
        print("No values to chart")
        return

    # Simple ASCII bar chart
    max_val = max(values)
    min_val = min(values)
    range_val = max_val - min_val if max_val != min_val else 1

    for time_key, data in sorted_intervals:
        bar_length = int(((data["avg"] - min_val) / range_val) * 40)
        bar = "█" * bar_length + "░" * (40 - bar_length)
        print(f"{time_key[-8:]} │{bar}│ {data['avg']:.1f}")

    print(f"Scale: {min_val:.1f} to {max_val:.1f}")


def _display_trend_table(intervals: Dict, metric_name: str) -> None:
    """Display trend data as table."""
    print(f"📈 Trend Analysis: {metric_name}")
    print("=" * 70)
    print(f"{'Time':<16} {'Count':<8} {'Avg':<10} {'Min':<10} {'Max':<10}")
    print("-" * 70)

    for time_key in sorted(intervals.keys()):
        data = intervals[time_key]
        print(
            f"{time_key:<16} {data['count']:<8} {data['avg']:<10.2f} {data['min']:<10.2f} {data['max']:<10.2f}"
        )


def _generate_performance_report(collector, start_time, end_time) -> Dict:
    """Generate performance metrics report."""
    # Query performance metrics
    query = MetricQuery(
        source=MetricSource.PERFORMANCE,
        start_time=start_time,
        end_time=end_time,
        limit=10000,
    )

    result = collector.query_metrics(query)

    # Analyze performance data
    response_times = []
    error_rates = []

    for metric in result.metrics:
        if "response_time" in metric.name or "execution_time" in metric.name:
            response_times.append(metric.value)
        elif "error_rate" in metric.name:
            error_rates.append(metric.value)

    return {
        "period": f"{start_time.isoformat()} to {end_time.isoformat()}",
        "total_metrics": len(result.metrics),
        "performance": {
            "avg_response_time": (
                sum(response_times) / len(response_times) if response_times else 0
            ),
            "max_response_time": max(response_times) if response_times else 0,
            "avg_error_rate": sum(error_rates) / len(error_rates) if error_rates else 0,
        },
    }


def _generate_usage_report(collector, start_time, end_time) -> Dict:
    """Generate usage metrics report."""
    query = MetricQuery(
        source=MetricSource.USER, start_time=start_time, end_time=end_time, limit=10000
    )

    result = collector.query_metrics(query)

    return {
        "period": f"{start_time.isoformat()} to {end_time.isoformat()}",
        "total_interactions": len(result.metrics),
        "unique_users": len(
            set(m.dimensions.get("user_id", "unknown") for m in result.metrics)
        ),
    }


def _generate_health_report(collector, start_time, end_time) -> Dict:
    """Generate system health report."""
    query = MetricQuery(
        source=MetricSource.SYSTEM,
        start_time=start_time,
        end_time=end_time,
        limit=10000,
    )

    result = collector.query_metrics(query)

    return {
        "period": f"{start_time.isoformat()} to {end_time.isoformat()}",
        "health_checks": len(result.metrics),
        "alerts": len(collector.active_alerts),
    }


def _generate_html_report(report: Dict, report_type: str) -> str:
    """Generate HTML report."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head >< title>{report_type.title()} Report </ title ></ head>
    <body>
        <h1>{report_type.title()} Report </ h1>
        <pre>{json.dumps(report, indent = 2)}</pre>
    </body>
    </html>
    """
    return html


def _generate_csv_report(report: Dict) -> str:
    """Generate CSV report."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write report data as key - value pairs

    def write_dict(d, prefix=""):
        for key, value in d.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                write_dict(value, full_key)
            else:
                writer.writerow([full_key, value])

    writer.writerow(["Metric", "Value"])
    write_dict(report)

    return output.getvalue()
