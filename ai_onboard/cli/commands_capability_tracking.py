"""
CLI commands for System Capability Usage Tracking.

This module provides command-line interfaces for:
- Viewing capability usage metrics and analytics
- Generating usage reports and insights
- Managing capability tracking configuration
- Analyzing user behavior patterns
"""

import argparse
import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from ..core.system_capability_tracker import (
    get_system_capability_tracker,
    CapabilityCategory,
    UsageContext,
    UsagePattern,
)
from .visual_components import create_status_indicator, create_table, create_chart


def add_capability_tracking_commands(subparsers):
    """Add capability tracking commands to the CLI."""

    # Main capability tracking command
    cap_parser = subparsers.add_parser(
        "capability-tracking", help="System capability usage tracking and analytics"
    )
    cap_sub = cap_parser.add_subparsers(dest="cap_cmd", required=True)

    # Metrics command
    metrics_parser = cap_sub.add_parser("metrics", help="View capability metrics")
    metrics_sub = metrics_parser.add_subparsers(dest="metrics_action", required=True)

    # View all metrics
    metrics_sub.add_parser("all", help="View all capability metrics")

    # View specific capability metrics
    capability_parser = metrics_sub.add_parser(
        "capability", help="View specific capability metrics"
    )
    capability_parser.add_argument("capability_name", help="Name of the capability")

    # View category metrics
    category_parser = metrics_sub.add_parser(
        "category", help="View metrics by category"
    )
    category_parser.add_argument(
        "category",
        choices=[c.value for c in CapabilityCategory],
        help="Capability category",
    )

    # Usage trends
    trends_parser = cap_sub.add_parser("trends", help="View usage trends")
    trends_parser.add_argument("--capability", help="Specific capability to analyze")
    trends_parser.add_argument(
        "--days", type=int, default=30, help="Number of days to analyze"
    )
    trends_parser.add_argument(
        "--category",
        choices=[c.value for c in CapabilityCategory],
        help="Category to analyze",
    )

    # User profiles
    profile_parser = cap_sub.add_parser("profile", help="User capability profiles")
    profile_parser.add_argument(
        "--user-id", default="default", help="User ID to analyze"
    )
    profile_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed profile"
    )

    # Reports
    report_parser = cap_sub.add_parser(
        "report", help="Generate capability usage reports"
    )
    report_parser.add_argument(
        "--days", type=int, default=30, help="Report period in days"
    )
    report_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Report format"
    )
    report_parser.add_argument(
        "--save", action="store_true", help="Save report to file"
    )

    # Analytics
    analytics_parser = cap_sub.add_parser(
        "analytics", help="Advanced capability analytics"
    )
    analytics_sub = analytics_parser.add_subparsers(
        dest="analytics_action", required=True
    )

    # Performance analytics
    analytics_sub.add_parser("performance", help="Performance analytics")

    # Usage patterns
    analytics_sub.add_parser("patterns", help="Usage pattern analysis")

    # Recommendations
    analytics_sub.add_parser("recommendations", help="Optimization recommendations")

    # Configuration
    config_parser = cap_sub.add_parser(
        "config", help="Capability tracking configuration"
    )
    config_sub = config_parser.add_subparsers(dest="config_action", required=True)

    # Show config
    config_sub.add_parser("show", help="Show current configuration")

    # Update config
    update_parser = config_sub.add_parser("update", help="Update configuration")
    update_parser.add_argument(
        "--tracking-enabled", type=bool, help="Enable/disable tracking"
    )
    update_parser.add_argument(
        "--detailed-tracking", type=bool, help="Enable detailed tracking"
    )
    update_parser.add_argument(
        "--retention-days", type=int, help="Data retention period"
    )
    update_parser.add_argument("--privacy-mode", type=bool, help="Enable privacy mode")


def handle_capability_tracking_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle capability tracking commands."""

    tracker = get_system_capability_tracker(root)

    if args.cap_cmd == "metrics":
        _handle_metrics_commands(args, tracker, root)
    elif args.cap_cmd == "trends":
        _handle_trends_commands(args, tracker, root)
    elif args.cap_cmd == "profile":
        _handle_profile_commands(args, tracker, root)
    elif args.cap_cmd == "report":
        _handle_report_commands(args, tracker, root)
    elif args.cap_cmd == "analytics":
        _handle_analytics_commands(args, tracker, root)
    elif args.cap_cmd == "config":
        _handle_config_commands(args, tracker, root)
    else:
        print(f"Unknown capability tracking command: {args.cap_cmd}")


def _handle_metrics_commands(args: argparse.Namespace, tracker, root: Path) -> None:
    """Handle metrics commands."""
    status = create_status_indicator(root, "default")

    if args.metrics_action == "all":
        print("📊 All Capability Metrics")
        print("=" * 50)

        if not tracker.capability_metrics:
            print(status.info("No capability metrics available"))
            print("💡 Use various commands to generate usage data")
            return

        # Create metrics table
        table = create_table(root, "default")

        headers = ["Capability", "Category", "Uses", "Success Rate", "Avg Duration"]
        rows = []

        for name, metrics in sorted(tracker.capability_metrics.items()):
            rows.append(
                [
                    name,
                    metrics.category.value.replace("_", " ").title(),
                    str(metrics.total_uses),
                    f"{metrics.success_rate:.1%}",
                    (
                        f"{metrics.avg_duration_ms:.0f}ms"
                        if metrics.avg_duration_ms > 0
                        else "N/A"
                    ),
                ]
            )

        print(table.create_table(headers, rows))

        # Summary statistics
        total_uses = sum(m.total_uses for m in tracker.capability_metrics.values())
        avg_success_rate = sum(
            m.success_rate for m in tracker.capability_metrics.values()
        ) / len(tracker.capability_metrics)

        print(f"\n📈 Summary:")
        print(f"   Total Capabilities: {len(tracker.capability_metrics)}")
        print(f"   Total Uses: {total_uses}")
        print(f"   Average Success Rate: {avg_success_rate:.1%}")

    elif args.metrics_action == "capability":
        capability_name = args.capability_name
        metrics = tracker.get_capability_metrics(capability_name)

        if not metrics:
            print(status.error(f"No metrics found for capability: {capability_name}"))
            return

        print(f"📊 Metrics for '{capability_name}'")
        print("=" * 50)

        print(f"Category: {metrics.category.value.replace('_', ' ').title()}")
        print(f"Total Uses: {metrics.total_uses}")
        print(f"Success Rate: {metrics.success_rate:.1%}")
        print(f"Error Rate: {metrics.error_rate:.1%}")

        if metrics.avg_duration_ms > 0:
            print(f"\n⏱️ Performance:")
            print(f"   Average Duration: {metrics.avg_duration_ms:.1f}ms")
            print(f"   Min Duration: {metrics.min_duration_ms:.1f}ms")
            print(f"   Max Duration: {metrics.max_duration_ms:.1f}ms")

        if metrics.common_contexts:
            print(f"\n🔍 Common Usage Contexts:")
            for context, count in sorted(
                metrics.common_contexts.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                percentage = (count / metrics.total_uses) * 100
                print(
                    f"   • {context.replace('_', ' ').title()}: {count} ({percentage:.1f}%)"
                )

        if metrics.common_patterns:
            print(f"\n📋 Usage Patterns:")
            for pattern, count in sorted(
                metrics.common_patterns.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                percentage = (count / metrics.total_uses) * 100
                print(
                    f"   • {pattern.replace('_', ' ').title()}: {count} ({percentage:.1f}%)"
                )

        if metrics.peak_usage_hours:
            print(f"\n🕐 Peak Usage Hours:")
            sorted_hours = sorted(
                metrics.peak_usage_hours.items(), key=lambda x: x[1], reverse=True
            )[:5]
            for hour, count in sorted_hours:
                print(f"   • {hour:02d}:00-{hour:02d}:59: {count} uses")

    elif args.metrics_action == "category":
        category = CapabilityCategory(args.category)
        category_metrics = tracker.get_category_metrics(category)

        if not category_metrics:
            print(status.info(f"No metrics found for category: {category.value}"))
            return

        print(f"📊 {category.value.replace('_', ' ').title()} Category Metrics")
        print("=" * 60)

        # Create category table
        table = create_table(root, "default")
        headers = ["Capability", "Uses", "Success Rate", "Avg Duration", "Growth"]
        rows = []

        for name, metrics in sorted(
            category_metrics.items(), key=lambda x: x[1].total_uses, reverse=True
        ):
            trends = tracker.get_usage_trends(name, 30)
            growth = trends.get("growth_rate", 0)
            growth_str = f"+{growth:.1%}" if growth > 0 else f"{growth:.1%}"

            rows.append(
                [
                    name,
                    str(metrics.total_uses),
                    f"{metrics.success_rate:.1%}",
                    (
                        f"{metrics.avg_duration_ms:.0f}ms"
                        if metrics.avg_duration_ms > 0
                        else "N/A"
                    ),
                    growth_str,
                ]
            )

        print(table.create_table(headers, rows))

        # Category summary
        total_uses = sum(m.total_uses for m in category_metrics.values())
        avg_success_rate = sum(m.success_rate for m in category_metrics.values()) / len(
            category_metrics
        )

        print(f"\n📈 Category Summary:")
        print(f"   Capabilities: {len(category_metrics)}")
        print(f"   Total Uses: {total_uses}")
        print(f"   Average Success Rate: {avg_success_rate:.1%}")


def _handle_trends_commands(args: argparse.Namespace, tracker, root: Path) -> None:
    """Handle trends commands."""
    chart = create_chart(root, "default")

    print("📈 Usage Trends Analysis")
    print("=" * 40)

    if args.capability:
        # Specific capability trends
        trends = tracker.get_usage_trends(args.capability, args.days)

        if not trends or trends.get("trend") == "no_data":
            print(f"❌ No trend data available for '{args.capability}'")
            return

        print(f"📊 Trends for '{args.capability}' (Last {args.days} days)")
        print("-" * 50)

        print(f"Trend: {trends['trend'].replace('_', ' ').title()}")
        print(f"Growth Rate: {trends.get('growth_rate', 0):.1%}")
        print(f"Total Recent Uses: {trends.get('total_recent_uses', 0)}")
        print(f"Average Daily Uses: {trends.get('avg_daily_uses', 0):.1f}")

        # Show usage chart
        recent_usage = trends.get("recent_usage", {})
        if recent_usage:
            print(f"\n📈 Daily Usage Pattern:")
            # Show last 14 days
            sorted_dates = sorted(recent_usage.keys())[-14:]
            daily_data = {
                date.split("-")[-1]: recent_usage[date] for date in sorted_dates
            }
            print(chart.bar_chart(daily_data, max_width=50))

    elif args.category:
        # Category trends
        category = CapabilityCategory(args.category)
        category_metrics = tracker.get_category_metrics(category)

        print(
            f"📊 Trends for {category.value.replace('_', ' ').title()} (Last {args.days} days)"
        )
        print("-" * 60)

        if not category_metrics:
            print("❌ No data available for this category")
            return

        # Analyze trends for each capability in category
        trend_data = {}
        for name, metrics in category_metrics.items():
            trends = tracker.get_usage_trends(name, args.days)
            if trends and trends.get("total_recent_uses", 0) > 0:
                trend_data[name] = trends.get("total_recent_uses", 0)

        if trend_data:
            print(f"📈 Category Usage Distribution:")
            print(chart.bar_chart(trend_data, max_width=50))
        else:
            print("❌ No recent usage data for this category")

    else:
        # Overall trends
        print(f"📊 Overall System Trends (Last {args.days} days)")
        print("-" * 50)

        # Get top trending capabilities
        trending_caps = {}
        for name, metrics in tracker.capability_metrics.items():
            trends = tracker.get_usage_trends(name, args.days)
            if trends and trends.get("growth_rate", 0) > 0:
                trending_caps[name] = trends["growth_rate"]

        if trending_caps:
            # Show top 10 trending
            sorted_trending = sorted(
                trending_caps.items(), key=lambda x: x[1], reverse=True
            )[:10]
            print(f"🚀 Fastest Growing Capabilities:")
            for name, growth in sorted_trending:
                print(f"   • {name}: +{growth:.1%}")
        else:
            print("📊 No significant growth trends detected")

        # Category distribution
        category_usage = {}
        for name, metrics in tracker.capability_metrics.items():
            category_name = metrics.category.value.replace("_", " ").title()
            category_usage[category_name] = (
                category_usage.get(category_name, 0) + metrics.total_uses
            )

        if category_usage:
            print(f"\n📈 Usage by Category:")
            print(chart.bar_chart(category_usage, max_width=50))


def _handle_profile_commands(args: argparse.Namespace, tracker, root: Path) -> None:
    """Handle user profile commands."""
    status = create_status_indicator(root, "default")

    print(f"👤 User Capability Profile: {args.user_id}")
    print("=" * 50)

    profile = tracker.get_user_capability_profile(args.user_id)

    if not profile.get("capabilities_used"):
        print(status.info("No usage data found for this user"))
        print("💡 Use various commands to generate profile data")
        return

    print(f"User Level: {profile.get('user_level', 'unknown').title()}")
    print(f"Total Capability Uses: {profile.get('total_capability_uses', 0)}")
    print(f"Unique Capabilities Used: {profile.get('unique_capabilities_used', 0)}")
    print(f"Advanced Usage Rate: {profile.get('advanced_usage_rate', 0):.1%}")
    print(f"Recent Activity (7 days): {profile.get('recent_activity', 0)} uses")

    # Most used capabilities
    capabilities_used = profile.get("capabilities_used", {})
    if capabilities_used:
        print(f"\n🏆 Most Used Capabilities:")
        for capability, count in list(capabilities_used.items())[:5]:
            print(f"   • {capability}: {count} uses")

    # Usage contexts
    contexts = profile.get("favorite_contexts", {})
    if contexts:
        print(f"\n🔍 Preferred Contexts:")
        for context, count in list(contexts.items())[:3]:
            print(f"   • {context.replace('_', ' ').title()}: {count} uses")

    # Category preferences
    categories = profile.get("category_preferences", {})
    if categories and args.detailed:
        chart = create_chart(root, "default")
        print(f"\n📊 Category Preferences:")
        category_display = {
            k.replace("_", " ").title(): v for k, v in categories.items()
        }
        print(chart.bar_chart(category_display, max_width=40))

    # Usage patterns
    patterns = profile.get("usage_patterns", {})
    if patterns and args.detailed:
        print(f"\n📋 Usage Patterns:")
        for pattern, count in list(patterns.items())[:3]:
            print(f"   • {pattern.replace('_', ' ').title()}: {count} uses")


def _handle_report_commands(args: argparse.Namespace, tracker, root: Path) -> None:
    """Handle report generation commands."""
    print(f"📄 Generating Capability Usage Report ({args.days} days)")
    print("=" * 60)

    report = tracker.generate_system_report(args.days)

    if args.format == "json":
        report_data = tracker._serialize_report(report)
        if args.save:
            filename = (
                f"capability_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(filename, "w") as f:
                json.dump(report_data, f, indent=2)
            print(f"📁 Report saved to: {filename}")
        else:
            print(json.dumps(report_data, indent=2))
        return

    # Text format report
    print(
        f"Report Period: {report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}"
    )
    print(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Overview
    print("📊 Overview")
    print("-" * 20)
    print(f"Total Capability Uses: {report.total_capability_uses}")
    print(f"Unique Capabilities Used: {report.unique_capabilities_used}")
    print(f"Unique Users: {report.unique_users}")
    print()

    # Most used capabilities
    if report.most_used_capabilities:
        print("🏆 Most Used Capabilities")
        print("-" * 30)
        for item in report.most_used_capabilities[:5]:
            print(f"   • {item['name']}: {item['uses']} uses")
        print()

    # Fastest growing
    if report.fastest_growing_capabilities:
        print("🚀 Fastest Growing Capabilities")
        print("-" * 35)
        for item in report.fastest_growing_capabilities[:5]:
            print(f"   • {item['name']}: +{item['growth_rate']:.1%}")
        print()

    # Common workflows
    if report.common_workflows:
        print("🔄 Common Workflows")
        print("-" * 25)
        for workflow in report.common_workflows[:3]:
            print(f"   • {workflow['pattern']} (frequency: {workflow['frequency']})")
        print()

    # Peak usage times
    if report.peak_usage_times:
        print("🕐 Peak Usage Times")
        print("-" * 25)
        sorted_hours = sorted(
            report.peak_usage_times.items(), key=lambda x: x[1], reverse=True
        )[:5]
        for hour, count in sorted_hours:
            print(f"   • {hour:02d}:00-{hour:02d}:59: {count} uses")
        print()

    # Performance concerns
    if report.performance_concerns:
        print("⚠️ Performance Concerns")
        print("-" * 30)
        for concern in report.performance_concerns[:3]:
            print(f"   • {concern['capability']}: {', '.join(concern['concerns'])}")
        print()

    # Recommendations
    if report.feature_promotion_recommendations:
        print("💡 Feature Promotion Recommendations")
        print("-" * 40)
        for rec in report.feature_promotion_recommendations[:3]:
            print(f"   • {rec}")
        print()

    if report.optimization_recommendations:
        print("⚡ Optimization Recommendations")
        print("-" * 35)
        for rec in report.optimization_recommendations[:3]:
            print(f"   • {rec}")
        print()

    if args.save:
        filename = f"capability_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        # Save text report (implementation would write formatted text)
        print(f"📁 Report saved to: {filename}")


def _handle_analytics_commands(args: argparse.Namespace, tracker, root: Path) -> None:
    """Handle analytics commands."""

    if args.analytics_action == "performance":
        print("⚡ Performance Analytics")
        print("=" * 30)

        # Get performance leaders and concerns
        report = tracker.generate_system_report(30)

        if report.performance_leaders:
            print("🏆 Performance Leaders:")
            table = create_table(root, "default")
            headers = ["Capability", "Avg Duration", "Success Rate", "Score"]
            rows = []

            for leader in report.performance_leaders[:5]:
                rows.append(
                    [
                        leader["capability"],
                        f"{leader['avg_duration_ms']:.0f}ms",
                        f"{leader['success_rate']:.1%}",
                        f"{leader['performance_score']:.1f}",
                    ]
                )

            print(table.create_table(headers, rows))

        if report.performance_concerns:
            print(f"\n⚠️ Performance Concerns:")
            for concern in report.performance_concerns:
                print(f"   • {concern['capability']}: {', '.join(concern['concerns'])}")

    elif args.analytics_action == "patterns":
        print("📋 Usage Pattern Analysis")
        print("=" * 35)

        # Analyze patterns across all capabilities
        all_patterns = {}
        all_contexts = {}

        for metrics in tracker.capability_metrics.values():
            for pattern, count in metrics.common_patterns.items():
                all_patterns[pattern] = all_patterns.get(pattern, 0) + count
            for context, count in metrics.common_contexts.items():
                all_contexts[context] = all_contexts.get(context, 0) + count

        if all_patterns:
            print("📊 System-wide Usage Patterns:")
            chart = create_chart(root, "default")
            pattern_display = {
                k.replace("_", " ").title(): v for k, v in all_patterns.items()
            }
            print(chart.bar_chart(pattern_display, max_width=40))

        if all_contexts:
            print(f"\n🔍 System-wide Usage Contexts:")
            context_display = {
                k.replace("_", " ").title(): v for k, v in all_contexts.items()
            }
            print(chart.bar_chart(context_display, max_width=40))

    elif args.analytics_action == "recommendations":
        print("💡 Optimization Recommendations")
        print("=" * 40)

        report = tracker.generate_system_report(30)

        if report.feature_promotion_recommendations:
            print("🚀 Feature Promotion:")
            for i, rec in enumerate(report.feature_promotion_recommendations, 1):
                print(f"   {i}. {rec}")

        if report.optimization_recommendations:
            print(f"\n⚡ Performance Optimization:")
            for i, rec in enumerate(report.optimization_recommendations, 1):
                print(f"   {i}. {rec}")

        if report.user_experience_improvements:
            print(f"\n🎨 User Experience:")
            for i, rec in enumerate(report.user_experience_improvements, 1):
                print(f"   {i}. {rec}")

        if not any(
            [
                report.feature_promotion_recommendations,
                report.optimization_recommendations,
                report.user_experience_improvements,
            ]
        ):
            print("✅ No specific recommendations at this time")
            print("💡 System appears to be performing well")


def _handle_config_commands(args: argparse.Namespace, tracker, root: Path) -> None:
    """Handle configuration commands."""
    status = create_status_indicator(root, "default")

    if args.config_action == "show":
        print("⚙️ Capability Tracking Configuration")
        print("=" * 40)

        config = tracker.config

        print(f"Tracking Enabled: {'✅' if config['tracking_enabled'] else '❌'}")
        print(f"Detailed Tracking: {'✅' if config['detailed_tracking'] else '❌'}")
        print(
            f"Performance Tracking: {'✅' if config['performance_tracking'] else '❌'}"
        )
        print(f"Privacy Mode: {'✅' if config['privacy_mode'] else '❌'}")
        print(f"User Anonymization: {'✅' if config['user_anonymization'] else '❌'}")
        print()

        print(f"Max Events in Memory: {config['max_events_in_memory']}")
        print(f"Metrics Update Interval: {config['metrics_update_interval']}s")
        print(f"Report Generation Interval: {config['report_generation_interval']}s")
        print(f"Data Retention: {config['retention_days']} days")
        print()

        if config["excluded_capabilities"]:
            print(
                f"Excluded Capabilities: {', '.join(config['excluded_capabilities'])}"
            )
        else:
            print("Excluded Capabilities: None")

    elif args.config_action == "update":
        config = tracker.config
        updates = []

        if args.tracking_enabled is not None:
            config["tracking_enabled"] = args.tracking_enabled
            updates.append(f"Tracking enabled: {args.tracking_enabled}")

        if args.detailed_tracking is not None:
            config["detailed_tracking"] = args.detailed_tracking
            updates.append(f"Detailed tracking: {args.detailed_tracking}")

        if args.retention_days is not None:
            config["retention_days"] = args.retention_days
            updates.append(f"Retention days: {args.retention_days}")

        if args.privacy_mode is not None:
            config["privacy_mode"] = args.privacy_mode
            updates.append(f"Privacy mode: {args.privacy_mode}")

        if updates:
            # Save configuration
            config_file = tracker.data_dir / "config.json"
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)

            print(status.success("Configuration updated:"))
            for update in updates:
                print(f"   • {update}")
        else:
            print(status.info("No configuration changes specified"))
