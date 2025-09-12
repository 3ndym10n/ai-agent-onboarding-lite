"""
Performance Trend Analysis CLI Commands.

This module provides CLI commands for performance trend analysis, anomaly detection,
forecasting, and insight generation.
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..core.performance_trend_analyzer import (
    get_performance_trend_analyzer,
    TrendDirection,
    TrendSeverity,
    ForecastConfidence
)
from ..core import utils


def add_performance_trend_commands(subparsers):
    """Add performance trend analysis commands to the CLI."""
    parser = subparsers.add_parser(
        "perf-trends",
        help="Performance trend analysis and forecasting",
        description="Analyze performance trends, detect anomalies, and generate forecasts"
    )
    
    subcommands = parser.add_subparsers(dest="trend_cmd", help="Performance trend commands")
    
    # Analyze trends command
    analyze_parser = subcommands.add_parser(
        "analyze",
        help="Analyze performance trends",
        description="Analyze performance trends for specified metrics and time periods"
    )
    analyze_parser.add_argument(
        "--metrics",
        nargs="+",
        help="Specific metrics to analyze (default: all available metrics)"
    )
    analyze_parser.add_argument(
        "--period",
        default="7d",
        help="Time period for analysis (e.g., '7d', '30d', '24h')"
    )
    analyze_parser.add_argument(
        "--format",
        choices=["table", "json", "summary"],
        default="table",
        help="Output format"
    )
    analyze_parser.add_argument(
        "--severity",
        choices=["low", "medium", "high", "critical"],
        help="Filter by minimum severity level"
    )
    
    # Detect anomalies command
    anomaly_parser = subcommands.add_parser(
        "anomalies",
        help="Detect performance anomalies",
        description="Detect performance anomalies using statistical methods"
    )
    anomaly_parser.add_argument(
        "--metrics",
        nargs="+",
        help="Specific metrics to analyze for anomalies"
    )
    anomaly_parser.add_argument(
        "--lookback",
        type=int,
        default=24,
        help="Lookback period in hours"
    )
    anomaly_parser.add_argument(
        "--threshold",
        type=float,
        help="Anomaly detection threshold (standard deviations)"
    )
    anomaly_parser.add_argument(
        "--format",
        choices=["table", "json", "summary"],
        default="table",
        help="Output format"
    )
    
    # Generate forecasts command
    forecast_parser = subcommands.add_parser(
        "forecast",
        help="Generate performance forecasts",
        description="Generate performance forecasts for capacity planning"
    )
    forecast_parser.add_argument(
        "--metric",
        required=True,
        help="Metric to forecast"
    )
    forecast_parser.add_argument(
        "--horizon",
        type=int,
        default=30,
        help="Forecast horizon in days"
    )
    forecast_parser.add_argument(
        "--format",
        choices=["table", "json", "chart"],
        default="table",
        help="Output format"
    )
    forecast_parser.add_argument(
        "--confidence",
        action="store_true",
        help="Include confidence intervals"
    )
    
    # Generate insights command
    insights_parser = subcommands.add_parser(
        "insights",
        help="Generate performance insights",
        description="Generate actionable performance insights and recommendations"
    )
    insights_parser.add_argument(
        "--lookback",
        type=int,
        default=30,
        help="Lookback period in days"
    )
    insights_parser.add_argument(
        "--category",
        choices=["optimization", "capacity", "reliability", "efficiency"],
        help="Filter by insight category"
    )
    insights_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high", "critical"],
        help="Filter by minimum priority level"
    )
    insights_parser.add_argument(
        "--format",
        choices=["table", "json", "detailed"],
        default="detailed",
        help="Output format"
    )
    
    # Dashboard command
    dashboard_parser = subcommands.add_parser(
        "dashboard",
        help="Performance trend dashboard",
        description="Display comprehensive performance trend dashboard"
    )
    dashboard_parser.add_argument(
        "--refresh",
        type=int,
        help="Auto-refresh interval in seconds"
    )
    dashboard_parser.add_argument(
        "--compact",
        action="store_true",
        help="Compact dashboard view"
    )
    
    # History command
    history_parser = subcommands.add_parser(
        "history",
        help="View trend analysis history",
        description="View historical trend analysis results"
    )
    history_parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days of history to show"
    )
    history_parser.add_argument(
        "--metric",
        help="Filter by specific metric"
    )
    history_parser.add_argument(
        "--format",
        choices=["table", "json", "timeline"],
        default="table",
        help="Output format"
    )


def handle_performance_trend_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle performance trend analysis commands."""
    if not hasattr(args, 'trend_cmd') or args.trend_cmd is None:
        print("❌ No performance trend command specified. Use --help for available commands.")
        return
    
    if args.trend_cmd == "analyze":
        _handle_analyze_trends(args, root)
    elif args.trend_cmd == "anomalies":
        _handle_detect_anomalies(args, root)
    elif args.trend_cmd == "forecast":
        _handle_generate_forecast(args, root)
    elif args.trend_cmd == "insights":
        _handle_generate_insights(args, root)
    elif args.trend_cmd == "dashboard":
        _handle_show_dashboard(args, root)
    elif args.trend_cmd == "history":
        _handle_show_history(args, root)
    else:
        print(f"❌ Unknown performance trend command: {args.trend_cmd}")


def _handle_analyze_trends(args: argparse.Namespace, root: Path) -> None:
    """Handle trend analysis command."""
    print("📈 Analyzing Performance Trends")
    print("=" * 40)
    
    try:
        analyzer = get_performance_trend_analyzer(root)
        
        # Analyze trends
        trends = analyzer.analyze_performance_trends(
            metric_names=args.metrics,
            time_period=args.period
        )
        
        if not trends:
            print("⚠️ No trends found for the specified criteria")
            return
        
        # Filter by severity if specified
        if args.severity:
            severity_filter = TrendSeverity(args.severity)
            severity_order = {
                TrendSeverity.LOW: 1,
                TrendSeverity.MEDIUM: 2,
                TrendSeverity.HIGH: 3,
                TrendSeverity.CRITICAL: 4
            }
            min_level = severity_order[severity_filter]
            trends = [t for t in trends if severity_order.get(t.severity, 0) >= min_level]
        
        # Display results
        if args.format == "json":
            _display_trends_json(trends)
        elif args.format == "summary":
            _display_trends_summary(trends)
        else:
            _display_trends_table(trends)
        
        print(f"\n✅ Analyzed {len(trends)} trends over {args.period}")
        
    except Exception as e:
        print(f"❌ Error analyzing trends: {e}")


def _handle_detect_anomalies(args: argparse.Namespace, root: Path) -> None:
    """Handle anomaly detection command."""
    print("🔍 Detecting Performance Anomalies")
    print("=" * 40)
    
    try:
        analyzer = get_performance_trend_analyzer(root)
        
        # Override threshold if specified
        if args.threshold:
            analyzer.anomaly_threshold = args.threshold
        
        # Detect anomalies
        anomalies = analyzer.detect_performance_anomalies(
            metric_names=args.metrics,
            lookback_hours=args.lookback
        )
        
        if not anomalies:
            print("✅ No anomalies detected in the specified time period")
            return
        
        # Display results
        if args.format == "json":
            _display_anomalies_json(anomalies)
        elif args.format == "summary":
            _display_anomalies_summary(anomalies)
        else:
            _display_anomalies_table(anomalies)
        
        print(f"\n⚠️ Detected {len(anomalies)} anomalies in the last {args.lookback} hours")
        
        # Show severity breakdown
        severity_counts = {}
        for anomaly in anomalies:
            severity_counts[anomaly.severity.value] = severity_counts.get(anomaly.severity.value, 0) + 1
        
        print("\n📊 Severity Breakdown:")
        for severity, count in severity_counts.items():
            print(f"   {severity.capitalize()}: {count}")
        
    except Exception as e:
        print(f"❌ Error detecting anomalies: {e}")


def _handle_generate_forecast(args: argparse.Namespace, root: Path) -> None:
    """Handle forecast generation command."""
    print(f"🔮 Generating Performance Forecast for {args.metric}")
    print("=" * 50)
    
    try:
        analyzer = get_performance_trend_analyzer(root)
        
        # Generate forecast
        forecast = analyzer.generate_performance_forecast(
            metric_name=args.metric,
            horizon_days=args.horizon
        )
        
        if not forecast:
            print(f"⚠️ Unable to generate forecast for {args.metric} - insufficient data or configuration disabled")
            return
        
        # Display results
        if args.format == "json":
            _display_forecast_json(forecast)
        elif args.format == "chart":
            _display_forecast_chart(forecast)
        else:
            _display_forecast_table(forecast, include_confidence=args.confidence)
        
        print(f"\n✅ Generated {args.horizon}-day forecast for {args.metric}")
        print(f"📊 Confidence Level: {forecast.forecast_confidence.value}")
        
        if forecast.recommendations:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(forecast.recommendations, 1):
                print(f"   {i}. {rec}")
        
    except Exception as e:
        print(f"❌ Error generating forecast: {e}")


def _handle_generate_insights(args: argparse.Namespace, root: Path) -> None:
    """Handle insight generation command."""
    print("💡 Generating Performance Insights")
    print("=" * 40)
    
    try:
        analyzer = get_performance_trend_analyzer(root)
        
        # Generate insights
        insights = analyzer.generate_performance_insights(lookback_days=args.lookback)
        
        if not insights:
            print("✅ No actionable insights found - system performance appears stable")
            return
        
        # Filter by category if specified
        if args.category:
            insights = [i for i in insights if i.category == args.category]
        
        # Filter by priority if specified
        if args.priority:
            priority_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            min_level = priority_order[args.priority]
            insights = [i for i in insights if priority_order.get(i.priority, 0) >= min_level]
        
        if not insights:
            print(f"⚠️ No insights found matching the specified filters")
            return
        
        # Display results
        if args.format == "json":
            _display_insights_json(insights)
        elif args.format == "table":
            _display_insights_table(insights)
        else:
            _display_insights_detailed(insights)
        
        print(f"\n✅ Generated {len(insights)} actionable insights")
        
        # Show category breakdown
        category_counts = {}
        for insight in insights:
            category_counts[insight.category] = category_counts.get(insight.category, 0) + 1
        
        print("\n📊 Insight Categories:")
        for category, count in category_counts.items():
            print(f"   {category.capitalize()}: {count}")
        
    except Exception as e:
        print(f"❌ Error generating insights: {e}")


def _handle_show_dashboard(args: argparse.Namespace, root: Path) -> None:
    """Handle dashboard display command."""
    print("📊 Performance Trend Dashboard")
    print("=" * 40)
    
    try:
        analyzer = get_performance_trend_analyzer(root)
        
        # Get recent trends
        trends = analyzer.analyze_performance_trends(time_period="7d")
        
        # Get recent anomalies
        anomalies = analyzer.detect_performance_anomalies(lookback_hours=24)
        
        # Get recent insights
        insights = analyzer.generate_performance_insights(lookback_days=7)
        
        # Display dashboard
        if args.compact:
            _display_compact_dashboard(trends, anomalies, insights)
        else:
            _display_full_dashboard(trends, anomalies, insights)
        
    except Exception as e:
        print(f"❌ Error displaying dashboard: {e}")


def _handle_show_history(args: argparse.Namespace, root: Path) -> None:
    """Handle history display command."""
    print(f"📜 Performance Trend History ({args.days} days)")
    print("=" * 50)
    
    try:
        # Load historical trend data
        trends_file = root / ".ai_onboard" / "performance_trends.jsonl"
        
        if not trends_file.exists():
            print("⚠️ No historical trend data found")
            return
        
        # Read and filter historical data
        cutoff_date = datetime.now() - timedelta(days=args.days)
        historical_trends = []
        
        with open(trends_file, 'r') as f:
            for line in f:
                try:
                    trend_data = json.loads(line.strip())
                    trend_date = datetime.fromisoformat(trend_data['timestamp'])
                    
                    if trend_date >= cutoff_date:
                        if not args.metric or trend_data['metric_name'] == args.metric:
                            historical_trends.append(trend_data)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
        
        if not historical_trends:
            print(f"⚠️ No trend history found for the specified criteria")
            return
        
        # Display results
        if args.format == "json":
            print(json.dumps(historical_trends, indent=2))
        elif args.format == "timeline":
            _display_history_timeline(historical_trends)
        else:
            _display_history_table(historical_trends)
        
        print(f"\n📊 Found {len(historical_trends)} historical trend records")
        
    except Exception as e:
        print(f"❌ Error displaying history: {e}")


# Display functions
def _display_trends_table(trends):
    """Display trends in table format."""
    if not trends:
        return
    
    print(f"\n📈 Performance Trends Analysis")
    print("-" * 80)
    print(f"{'Metric':<20} {'Direction':<12} {'Severity':<10} {'Change%':<8} {'Confidence':<10} {'Points':<8}")
    print("-" * 80)
    
    for trend in trends:
        direction_icon = {
            TrendDirection.IMPROVING: "📈",
            TrendDirection.DEGRADING: "📉",
            TrendDirection.STABLE: "➡️",
            TrendDirection.VOLATILE: "📊",
            TrendDirection.UNKNOWN: "❓"
        }.get(trend.direction, "")
        
        severity_icon = {
            TrendSeverity.LOW: "🟢",
            TrendSeverity.MEDIUM: "🟡",
            TrendSeverity.HIGH: "🟠",
            TrendSeverity.CRITICAL: "🔴"
        }.get(trend.severity, "")
        
        print(f"{trend.metric_name:<20} {direction_icon} {trend.direction.value:<10} "
              f"{severity_icon} {trend.severity.value:<8} {trend.change_percent:>6.1f}% "
              f"{trend.confidence:>8.2f} {trend.data_points:>6}")


def _display_trends_summary(trends):
    """Display trends in summary format."""
    if not trends:
        return
    
    print(f"\n📊 Trends Summary")
    print("-" * 30)
    
    # Count by direction
    direction_counts = {}
    severity_counts = {}
    
    for trend in trends:
        direction_counts[trend.direction.value] = direction_counts.get(trend.direction.value, 0) + 1
        severity_counts[trend.severity.value] = severity_counts.get(trend.severity.value, 0) + 1
    
    print("Direction Distribution:")
    for direction, count in direction_counts.items():
        print(f"  {direction.capitalize()}: {count}")
    
    print("\nSeverity Distribution:")
    for severity, count in severity_counts.items():
        print(f"  {severity.capitalize()}: {count}")


def _display_trends_json(trends):
    """Display trends in JSON format."""
    trends_data = []
    for trend in trends:
        trends_data.append({
            "metric_name": trend.metric_name,
            "time_period": trend.time_period,
            "direction": trend.direction.value,
            "severity": trend.severity.value,
            "confidence": trend.confidence,
            "change_percent": trend.change_percent,
            "data_points": trend.data_points,
            "trend_strength": trend.trend_strength
        })
    
    print(json.dumps(trends_data, indent=2))


def _display_anomalies_table(anomalies):
    """Display anomalies in table format."""
    if not anomalies:
        return
    
    print(f"\n🔍 Performance Anomalies")
    print("-" * 90)
    print(f"{'Metric':<20} {'Type':<10} {'Severity':<10} {'Value':<10} {'Expected':<10} {'Deviation':<10} {'Time':<15}")
    print("-" * 90)
    
    for anomaly in anomalies:
        severity_icon = {
            TrendSeverity.LOW: "🟢",
            TrendSeverity.MEDIUM: "🟡",
            TrendSeverity.HIGH: "🟠",
            TrendSeverity.CRITICAL: "🔴"
        }.get(anomaly.severity, "")
        
        time_str = anomaly.anomaly_timestamp.strftime("%H:%M %m/%d")
        
        print(f"{anomaly.metric_name:<20} {anomaly.anomaly_type:<10} "
              f"{severity_icon} {anomaly.severity.value:<8} {anomaly.anomaly_value:>8.1f} "
              f"{anomaly.expected_value:>8.1f} {anomaly.deviation_score:>8.1f} {time_str:<15}")


def _display_anomalies_summary(anomalies):
    """Display anomalies in summary format."""
    if not anomalies:
        return
    
    print(f"\n🔍 Anomalies Summary")
    print("-" * 30)
    
    # Count by type and severity
    type_counts = {}
    severity_counts = {}
    
    for anomaly in anomalies:
        type_counts[anomaly.anomaly_type] = type_counts.get(anomaly.anomaly_type, 0) + 1
        severity_counts[anomaly.severity.value] = severity_counts.get(anomaly.severity.value, 0) + 1
    
    print("Anomaly Types:")
    for anomaly_type, count in type_counts.items():
        print(f"  {anomaly_type.capitalize()}: {count}")
    
    print("\nSeverity Distribution:")
    for severity, count in severity_counts.items():
        print(f"  {severity.capitalize()}: {count}")


def _display_anomalies_json(anomalies):
    """Display anomalies in JSON format."""
    anomalies_data = []
    for anomaly in anomalies:
        anomalies_data.append({
            "metric_name": anomaly.metric_name,
            "anomaly_type": anomaly.anomaly_type,
            "severity": anomaly.severity.value,
            "anomaly_value": anomaly.anomaly_value,
            "expected_value": anomaly.expected_value,
            "deviation_score": anomaly.deviation_score,
            "confidence": anomaly.confidence,
            "detection_method": anomaly.detection_method,
            "timestamp": anomaly.anomaly_timestamp.isoformat()
        })
    
    print(json.dumps(anomalies_data, indent=2))


def _display_forecast_table(forecast, include_confidence=False):
    """Display forecast in table format."""
    print(f"\n🔮 Performance Forecast: {forecast.metric_name}")
    print("-" * 60)
    
    if include_confidence:
        print(f"{'Day':<5} {'Predicted':<12} {'Lower CI':<12} {'Upper CI':<12}")
        print("-" * 60)
        
        for i, (pred, (lower, upper)) in enumerate(zip(forecast.predicted_values, forecast.confidence_intervals)):
            print(f"{i+1:<5} {pred:>10.2f} {lower:>10.2f} {upper:>10.2f}")
    else:
        print(f"{'Day':<5} {'Predicted Value':<15}")
        print("-" * 25)
        
        for i, pred in enumerate(forecast.predicted_values):
            print(f"{i+1:<5} {pred:>13.2f}")
    
    print(f"\nForecast Confidence: {forecast.forecast_confidence.value}")
    print(f"Methodology: {forecast.methodology}")


def _display_forecast_json(forecast):
    """Display forecast in JSON format."""
    forecast_data = {
        "metric_name": forecast.metric_name,
        "forecast_horizon": forecast.forecast_horizon,
        "predicted_values": forecast.predicted_values,
        "confidence_intervals": forecast.confidence_intervals,
        "forecast_confidence": forecast.forecast_confidence.value,
        "methodology": forecast.methodology,
        "assumptions": forecast.assumptions,
        "risk_factors": forecast.risk_factors,
        "recommendations": forecast.recommendations
    }
    
    print(json.dumps(forecast_data, indent=2))


def _display_forecast_chart(forecast):
    """Display forecast in simple ASCII chart format."""
    print(f"\n📊 Forecast Chart: {forecast.metric_name}")
    print("-" * 50)
    
    values = forecast.predicted_values[:14]  # Show first 2 weeks
    if not values:
        return
    
    max_val = max(values)
    min_val = min(values)
    range_val = max_val - min_val if max_val != min_val else 1
    
    for i, value in enumerate(values):
        normalized = int(((value - min_val) / range_val) * 30)
        bar = "█" * normalized + "░" * (30 - normalized)
        print(f"Day {i+1:2d}: {bar} {value:6.1f}")
    
    print(f"\nRange: {min_val:.1f} - {max_val:.1f}")


def _display_insights_detailed(insights):
    """Display insights in detailed format."""
    if not insights:
        return
    
    print(f"\n💡 Performance Insights")
    print("=" * 50)
    
    for i, insight in enumerate(insights, 1):
        priority_icon = {
            "low": "🟢",
            "medium": "🟡", 
            "high": "🟠",
            "critical": "🔴"
        }.get(insight.priority, "")
        
        print(f"\n{i}. {priority_icon} {insight.title}")
        print(f"   Category: {insight.category.capitalize()}")
        print(f"   Priority: {insight.priority.capitalize()}")
        print(f"   Description: {insight.description}")
        
        if insight.affected_metrics:
            print(f"   Affected Metrics: {', '.join(insight.affected_metrics)}")
        
        print(f"   Impact: {insight.estimated_impact}")
        print(f"   Effort: {insight.implementation_effort}")
        
        if insight.recommendations:
            print(f"   Recommendations:")
            for rec in insight.recommendations:
                print(f"     • {rec}")


def _display_insights_table(insights):
    """Display insights in table format."""
    if not insights:
        return
    
    print(f"\n💡 Performance Insights")
    print("-" * 80)
    print(f"{'Title':<30} {'Category':<12} {'Priority':<10} {'Impact':<10} {'Metrics':<15}")
    print("-" * 80)
    
    for insight in insights:
        priority_icon = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠", 
            "critical": "🔴"
        }.get(insight.priority, "")
        
        metrics_str = ', '.join(insight.affected_metrics[:2])  # Show first 2 metrics
        if len(insight.affected_metrics) > 2:
            metrics_str += "..."
        
        print(f"{insight.title[:28]:<30} {insight.category:<12} "
              f"{priority_icon} {insight.priority:<8} {insight.estimated_impact:<10} {metrics_str:<15}")


def _display_insights_json(insights):
    """Display insights in JSON format."""
    insights_data = []
    for insight in insights:
        insights_data.append({
            "title": insight.title,
            "description": insight.description,
            "category": insight.category,
            "priority": insight.priority,
            "affected_metrics": insight.affected_metrics,
            "estimated_impact": insight.estimated_impact,
            "implementation_effort": insight.implementation_effort,
            "recommendations": insight.recommendations
        })
    
    print(json.dumps(insights_data, indent=2))


def _display_full_dashboard(trends, anomalies, insights):
    """Display full performance dashboard."""
    print(f"\n📊 Performance Overview")
    print("-" * 40)
    
    # Trends summary
    print(f"\n📈 Trends (Last 7 days): {len(trends)} analyzed")
    if trends:
        degrading = sum(1 for t in trends if t.direction == TrendDirection.DEGRADING)
        improving = sum(1 for t in trends if t.direction == TrendDirection.IMPROVING)
        stable = sum(1 for t in trends if t.direction == TrendDirection.STABLE)
        
        print(f"   📉 Degrading: {degrading}")
        print(f"   📈 Improving: {improving}")
        print(f"   ➡️ Stable: {stable}")
    
    # Anomalies summary
    print(f"\n🔍 Anomalies (Last 24 hours): {len(anomalies)} detected")
    if anomalies:
        critical = sum(1 for a in anomalies if a.severity == TrendSeverity.CRITICAL)
        high = sum(1 for a in anomalies if a.severity == TrendSeverity.HIGH)
        
        if critical > 0:
            print(f"   🔴 Critical: {critical}")
        if high > 0:
            print(f"   🟠 High: {high}")
    
    # Insights summary
    print(f"\n💡 Insights (Last 7 days): {len(insights)} generated")
    if insights:
        critical_insights = sum(1 for i in insights if i.priority == "critical")
        high_insights = sum(1 for i in insights if i.priority == "high")
        
        if critical_insights > 0:
            print(f"   🔴 Critical: {critical_insights}")
        if high_insights > 0:
            print(f"   🟠 High: {high_insights}")
    
    # Top recommendations
    if insights:
        print(f"\n🎯 Top Recommendations:")
        for i, insight in enumerate(insights[:3], 1):
            print(f"   {i}. {insight.title}")


def _display_compact_dashboard(trends, anomalies, insights):
    """Display compact performance dashboard."""
    print(f"\n📊 Quick Status")
    print("-" * 20)
    
    # Status indicators
    trend_status = "🔴" if any(t.severity == TrendSeverity.CRITICAL for t in trends) else \
                   "🟡" if any(t.severity == TrendSeverity.HIGH for t in trends) else "🟢"
    
    anomaly_status = "🔴" if any(a.severity == TrendSeverity.CRITICAL for a in anomalies) else \
                     "🟡" if any(a.severity == TrendSeverity.HIGH for a in anomalies) else "🟢"
    
    insight_status = "🔴" if any(i.priority == "critical" for i in insights) else \
                     "🟡" if any(i.priority == "high" for i in insights) else "🟢"
    
    print(f"Trends: {trend_status} ({len(trends)})")
    print(f"Anomalies: {anomaly_status} ({len(anomalies)})")
    print(f"Insights: {insight_status} ({len(insights)})")


def _display_history_table(historical_trends):
    """Display historical trends in table format."""
    if not historical_trends:
        return
    
    print(f"\n📜 Historical Trends")
    print("-" * 70)
    print(f"{'Date':<12} {'Metric':<20} {'Direction':<12} {'Severity':<10} {'Change%':<8}")
    print("-" * 70)
    
    for trend_data in sorted(historical_trends, key=lambda x: x['timestamp'], reverse=True):
        date_str = datetime.fromisoformat(trend_data['timestamp']).strftime("%m/%d %H:%M")
        
        print(f"{date_str:<12} {trend_data['metric_name']:<20} "
              f"{trend_data['direction']:<12} {trend_data['severity']:<10} "
              f"{trend_data.get('change_percent', 0):>6.1f}%")


def _display_history_timeline(historical_trends):
    """Display historical trends in timeline format."""
    if not historical_trends:
        return
    
    print(f"\n📅 Trend Timeline")
    print("-" * 40)
    
    # Group by date
    from collections import defaultdict
    by_date = defaultdict(list)
    
    for trend_data in historical_trends:
        date_key = datetime.fromisoformat(trend_data['timestamp']).strftime("%Y-%m-%d")
        by_date[date_key].append(trend_data)
    
    for date_key in sorted(by_date.keys(), reverse=True):
        print(f"\n📅 {date_key}")
        for trend_data in by_date[date_key]:
            time_str = datetime.fromisoformat(trend_data['timestamp']).strftime("%H:%M")
            print(f"   {time_str} - {trend_data['metric_name']}: {trend_data['direction']} ({trend_data['severity']})")

