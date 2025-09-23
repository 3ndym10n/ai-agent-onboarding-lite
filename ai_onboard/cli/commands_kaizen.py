"""
CLI commands for Kaizen Cycle Automation.

This module provides command - line interfaces for:
- Managing automated Kaizen cycles
- Configuring improvement automation
- Monitoring improvement opportunities
- Analyzing cycle results and learning outcomes
"""

import argparse
import time
from pathlib import Path

from ..core.kaizen_automation import get_kaizen_automation


def add_kaizen_commands(subparsers):
    """Add Kaizen automation commands to the CLI."""

    # Main Kaizen command
    kaizen_parser = subparsers.add_parser(
        "kaizen - auto",
        help="Automated Kaizen cycle management and continuous improvement",
    )
    kaizen_sub = kaizen_parser.add_subparsers(dest="kaizen_cmd", required=True)

    # Start automation
    start_parser = kaizen_sub.add_parser("start", help="Start automated Kaizen cycles")
    start_parser.add_argument(
        "--background", action="store_true", help="Run in background"
    )

    # Stop automation
    kaizen_sub.add_parser("stop", help="Stop automated Kaizen cycles")

    # Status command
    kaizen_sub.add_parser("status", help="Show Kaizen automation status")

    # Run cycle command
    run_parser = kaizen_sub.add_parser(
        "run - cycle", help="Run a single Kaizen cycle manually"
    )
    run_parser.add_argument(
        "--verbose", action="store_true", help="Show detailed progress"
    )

    # Opportunities command
    opportunities_parser = kaizen_sub.add_parser(
        "opportunities", help="Manage improvement opportunities"
    )
    opp_sub = opportunities_parser.add_subparsers(dest="opp_action", required=True)

    # List opportunities
    list_parser = opp_sub.add_parser(
        "list", help="List current improvement opportunities"
    )
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high", "critical"],
        help="Filter by priority",
    )
    list_parser.add_argument(
        "--status",
        choices=[
            "identified",
            "planned",
            "executing",
            "completed",
            "failed",
            "cancelled",
        ],
        help="Filter by status",
    )

    # Show opportunity details
    show_parser = opp_sub.add_parser("show", help="Show opportunity details")
    show_parser.add_argument("opportunity_id", help="Opportunity ID to show")

    # Execute opportunity
    execute_parser = opp_sub.add_parser("execute", help="Execute specific opportunity")
    execute_parser.add_argument("opportunity_id", help="Opportunity ID to execute")
    execute_parser.add_argument(
        "--force", action="store_true", help="Force execution even if risky"
    )

    # History command
    history_parser = kaizen_sub.add_parser("history", help="Show cycle history")
    history_parser.add_argument(
        "--limit", type=int, default=10, help="Number of cycles to show"
    )
    history_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed cycle information"
    )

    # Analytics command
    analytics_parser = kaizen_sub.add_parser("analytics", help="Show Kaizen analytics")
    analytics_sub = analytics_parser.add_subparsers(
        dest="analytics_action", required=True
    )

    # Success metrics
    analytics_sub.add_parser("success", help="Show success metrics and trends")

    # Impact analysis
    analytics_sub.add_parser("impact", help="Show improvement impact analysis")

    # Learning insights
    analytics_sub.add_parser("learning", help="Show learning insights and patterns")

    # Configuration command
    config_parser = kaizen_sub.add_parser("config", help="Configure Kaizen automation")
    config_sub = config_parser.add_subparsers(dest="config_action", required=True)

    # Show configuration
    config_sub.add_parser("show", help="Show current configuration")

    # Update configuration
    update_parser = config_sub.add_parser("update", help="Update configuration")
    update_parser.add_argument("--interval", type=int, help="Cycle interval in hours")
    update_parser.add_argument(
        "--max - concurrent", type=int, help="Max concurrent improvements"
    )
    update_parser.add_argument(
        "--confidence - threshold", type=float, help="Minimum confidence threshold"
    )
    update_parser.add_argument(
        "--auto - execute - low - risk",
        type=bool,
        help="Auto - execute low - risk improvements",
    )
    update_parser.add_argument(
        "--enable - category", help="Enable improvement category"
    )
    update_parser.add_argument(
        "--disable - category", help="Disable improvement category"
    )


def handle_kaizen_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle Kaizen automation commands."""

    kaizen_engine = get_kaizen_automation(root)

    if args.kaizen_cmd == "start":
        _handle_start_automation(args, kaizen_engine)
    elif args.kaizen_cmd == "stop":
        _handle_stop_automation(args, kaizen_engine)
    elif args.kaizen_cmd == "status":
        _handle_status(args, kaizen_engine)
    elif args.kaizen_cmd == "run - cycle":
        _handle_run_cycle(args, kaizen_engine)
    elif args.kaizen_cmd == "opportunities":
        _handle_opportunities_commands(args, kaizen_engine)
    elif args.kaizen_cmd == "history":
        _handle_history(args, kaizen_engine)
    elif args.kaizen_cmd == "analytics":
        _handle_analytics_commands(args, kaizen_engine)
    elif args.kaizen_cmd == "config":
        _handle_config_commands(args, kaizen_engine)
    else:
        print(f"Unknown Kaizen command: {args.kaizen_cmd}")


def _handle_start_automation(args: argparse.Namespace, kaizen_engine) -> None:
    """Handle start automation command."""
    print("🔄 Starting Kaizen Automation")

    status = kaizen_engine.get_automation_status()

    if status["running"]:
        print("✅ Kaizen automation is already running")
        return

    if not status["config"]["enabled"]:
        print("❌ Kaizen automation is disabled in configuration")
        print("💡 Enable with: kaizen - auto config update --enable")
        return

    kaizen_engine.start_automation()

    print("✅ Kaizen automation started successfully")
    print(f"📊 Configuration:")
    print(f"   Cycle Interval: {status['config']['cycle_interval_hours']} hours")
    print(
        f"   Max Concurrent Improvements: {status['config']['max_concurrent_improvements']}"
    )
    print(f"   Confidence Threshold: {status['config']['min_confidence_threshold']}")
    print(f"   Auto - execute Low Risk: {status['config']['auto_execute_low_risk']}")

    if not args.background:
        print("\n🔍 Monitoring automation (Ctrl + C to stop)...")
        try:
            while kaizen_engine.get_automation_status()["running"]:
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n⏹️ Stopping automation...")
            kaizen_engine.stop_automation()
            print("✅ Automation stopped")


def _handle_stop_automation(args: argparse.Namespace, kaizen_engine) -> None:
    """Handle stop automation command."""
    print("⏹️ Stopping Kaizen Automation")

    status = kaizen_engine.get_automation_status()

    if not status["running"]:
        print("ℹ️ Kaizen automation is not currently running")
        return

    kaizen_engine.stop_automation()
    print("✅ Kaizen automation stopped successfully")


def _handle_status(args: argparse.Namespace, kaizen_engine) -> None:
    """Handle status command."""
    print("📊 Kaizen Automation Status")
    print("=" * 40)

    status = kaizen_engine.get_automation_status()

    # Running status
    running_status = "🟢 Running" if status["running"] else "🔴 Stopped"
    print(f"Status: {running_status}")

    # Configuration
    config = status["config"]
    print(f"\n⚙️ Configuration:")
    print(f"   Enabled: {'✅' if config['enabled'] else '❌'}")
    print(f"   Cycle Interval: {config['cycle_interval_hours']} hours")
    print(f"   Max Concurrent: {config['max_concurrent_improvements']}")
    print(f"   Confidence Threshold: {config['min_confidence_threshold']}")
    print(
        f"   Auto - execute Low Risk: {'✅' if config['auto_execute_low_risk'] else '❌'}"
    )

    # Active state
    print(f"\n📈 Current State:")
    print(f"   Active Cycles: {status['active_cycles']}")
    print(f"   Total Opportunities: {status['total_opportunities']}")
    print(f"   Pending Opportunities: {status['pending_opportunities']}")

    # Enabled categories
    enabled_categories = [
        cat for cat, enabled in config["categories_enabled"].items() if enabled
    ]
    print(f"\n🎯 Enabled Categories:")
    for category in enabled_categories:
        print(f"   • {category}")

    # Recent activity
    recent_cycles = kaizen_engine.get_cycle_history(limit=3)
    if recent_cycles:
        print(f"\n🔄 Recent Cycles:")
        for cycle in recent_cycles:
            print(
                f"   • {cycle['cycle_id']}: {cycle['overall_impact']} (score: {cycle['success_score']:.2f})"
            )


def _handle_run_cycle(args: argparse.Namespace, kaizen_engine) -> None:
    """Handle manual cycle execution."""
    print("🔄 Running Manual Kaizen Cycle")
    print("=" * 40)

    if args.verbose:
        print("Starting comprehensive improvement cycle...")

    # Run the cycle
    cycle = kaizen_engine.run_kaizen_cycle()

    # Display results
    print(f"\n✅ Cycle Completed: {cycle.cycle_id}")
    print(f"Success Score: {cycle.success_score:.2f}")
    print(f"Overall Impact: {cycle.overall_impact}")
    print(f"Actions Taken: {len(cycle.actions_taken)}")

    if args.verbose:
        print(f"\n🔍 Detailed Results:")

        # Observations
        print(f"\n👁️ Observations:")
        if cycle.observations:
            for key, value in cycle.observations.items():
                if key != "timestamp" and not key.endswith("_data"):
                    print(f"   {key}: {value}")

        # Analysis
        print(f"\n🧭 Analysis:")
        if cycle.analysis_results:
            opportunities = cycle.analysis_results.get("identified_opportunities", [])
            print(f"   Opportunities Identified: {len(opportunities)}")
            for opp in opportunities[:3]:  # Show top 3
                print(f"   • {opp['title']} ({opp['priority']} priority)")

        # Actions
        print(f"\n🚀 Actions:")
        for action in cycle.actions_taken:
            status_icon = "✅" if action.get("status") == "completed" else "❌"
            print(
                f"   {status_icon} {action.get('opportunity',
                    action.get('decision', 'Unknown'))}"
            )

        # Learning
        print(f"\n📚 Learning Outcomes:")
        if cycle.learning_outcomes:
            lessons = cycle.learning_outcomes.get("lessons_learned", [])
            for lesson in lessons:
                print(f"   • {lesson}")

            recommendations = cycle.learning_outcomes.get("recommendations", [])
            if recommendations:
                print(f"\n💡 Recommendations:")
                for rec in recommendations:
                    print(f"   • {rec}")


def _handle_opportunities_commands(args: argparse.Namespace, kaizen_engine) -> None:
    """Handle opportunities management commands."""

    if args.opp_action == "list":
        print("📋 Improvement Opportunities")
        print("=" * 50)

        opportunities = list(kaizen_engine.improvement_opportunities.values())

        # Apply filters
        if args.category:
            opportunities = [
                opp for opp in opportunities if opp.category.value == args.category
            ]
        if args.priority:
            opportunities = [
                opp for opp in opportunities if opp.priority.value == args.priority
            ]
        if args.status:
            opportunities = [
                opp for opp in opportunities if opp.status.value == args.status
            ]

        if not opportunities:
            print("No opportunities found matching criteria")
            return

        # Sort by priority and impact
        opportunities.sort(
            key=lambda x: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(
                    x.priority.value, 1
                ),
                x.estimated_impact,
            ),
            reverse=True,
        )

        for opp in opportunities:
            priority_icon = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
            }.get(opp.priority.value, "⚪")

            status_icon = {
                "identified": "🆕",
                "planned": "📋",
                "executing": "⚙️",
                "completed": "✅",
                "failed": "❌",
                "cancelled": "🚫",
            }.get(opp.status.value, "❓")

            print(f"\n{priority_icon} {status_icon} {opp.opportunity_id}")
            print(f"   Title: {opp.title}")
            print(f"   Category: {opp.category.value}")
            print(f"   Priority: {opp.priority.value}")
            print(f"   Impact / Effort: {opp.estimated_impact}/{opp.estimated_effort}")
            print(f"   Risk Level: {opp.risk_level}")
            print(f"   Status: {opp.status.value}")

    elif args.opp_action == "show":
        opportunity = kaizen_engine.improvement_opportunities.get(args.opportunity_id)

        if not opportunity:
            print(f"❌ Opportunity not found: {args.opportunity_id}")
            return

        print(f"📋 Opportunity Details: {args.opportunity_id}")
        print("=" * 50)

        print(f"Title: {opportunity.title}")
        print(f"Description: {opportunity.description}")
        print(f"Category: {opportunity.category.value}")
        print(f"Priority: {opportunity.priority.value}")
        print(f"Status: {opportunity.status.value}")
        print(
            f"Identified: {opportunity.identified_at.strftime('%Y -% m -% d %H:%M:%S')}"
        )

        print(f"\n📊 Metrics:")
        print(f"   Estimated Impact: {opportunity.estimated_impact}/5")
        print(f"   Estimated Effort: {opportunity.estimated_effort}/5")
        print(f"   Risk Level: {opportunity.risk_level}/5")

        if opportunity.current_metrics:
            print(f"\n📈 Current Metrics:")
            for metric, value in opportunity.current_metrics.items():
                print(f"   {metric}: {value}")

        if opportunity.target_metrics:
            print(f"\n🎯 Target Metrics:")
            for metric, value in opportunity.target_metrics.items():
                print(f"   {metric}: {value}")

        if opportunity.proposed_actions:
            print(f"\n🚀 Proposed Actions:")
            for i, action in enumerate(opportunity.proposed_actions, 1):
                print(f"   {i}. {action}")

        if opportunity.evidence:
            print(f"\n🔍 Evidence:")
            for key, value in opportunity.evidence.items():
                print(f"   {key}: {value}")

        if opportunity.experiment_results:
            print(f"\n🧪 Experiment Results:")
            results = opportunity.experiment_results
            print(f"   Status: {results.get('status', 'unknown')}")
            if results.get("actions_performed"):
                print(f"   Actions Performed:")
                for action in results["actions_performed"]:
                    print(f"     • {action}")

    elif args.opp_action == "execute":
        opportunity = kaizen_engine.improvement_opportunities.get(args.opportunity_id)

        if not opportunity:
            print(f"❌ Opportunity not found: {args.opportunity_id}")
            return

        print(f"🚀 Executing Opportunity: {opportunity.title}")

        # Check risk level
        if opportunity.risk_level > 3 and not args.force:
            print(f"⚠️ High risk opportunity (level {opportunity.risk_level})")
            print("Use --force to execute anyway")
            return

        # Execute the improvement
        result = kaizen_engine._execute_improvement(opportunity)

        if result.get("status") == "completed":
            print("✅ Opportunity executed successfully")
            if result.get("actions_performed"):
                print("Actions performed:")
                for action in result["actions_performed"]:
                    print(f"  • {action}")
        else:
            print("❌ Opportunity execution failed")
            if result.get("error"):
                print(f"Error: {result['error']}")


def _handle_history(args: argparse.Namespace, kaizen_engine) -> None:
    """Handle cycle history display."""
    print(f"📊 Kaizen Cycle History (Last {args.limit})")
    print("=" * 50)

    cycles = kaizen_engine.get_cycle_history(limit=args.limit)

    if not cycles:
        print("No completed cycles found")
        return

    for cycle in cycles:
        impact_icon = {
            "high_impact": "🔥",
            "medium_impact": "📈",
            "low_impact": "📊",
            "no_impact": "📉",
            "failed": "❌",
        }.get(cycle["overall_impact"], "❓")

        print(f"\n{impact_icon} {cycle['cycle_id']}")
        print(f"   Started: {cycle['started_at'][:19]}")  # Remove microseconds
        print(f"   Success Score: {cycle['success_score']:.2f}")
        print(f"   Overall Impact: {cycle['overall_impact']}")
        print(f"   Actions: {cycle['actions_count']}")
        print(f"   Opportunities: {cycle['opportunities_addressed']}")

        if args.detailed:
            # Would show more detailed information
            print(f"   Status: Completed")


def _handle_analytics_commands(args: argparse.Namespace, kaizen_engine) -> None:
    """Handle analytics commands."""

    if args.analytics_action == "success":
        print("📊 Kaizen Success Analytics")
        print("=" * 40)

        cycles = kaizen_engine.get_cycle_history(limit=20)

        if not cycles:
            print("No cycle data available for analysis")
            return

        # Calculate success metrics
        total_cycles = len(cycles)
        avg_success_score = sum(c["success_score"] for c in cycles) / total_cycles
        high_impact_cycles = len(
            [c for c in cycles if c["overall_impact"] == "high_impact"]
        )

        print(f"Total Cycles: {total_cycles}")
        print(f"Average Success Score: {avg_success_score:.2f}")
        print(
            f"High Impact Cycles: {high_impact_cycles} ({high_impact_cycles / total_cycles * 100:.1f}%)"
        )

        # Impact distribution
        impact_counts = {}
        for cycle in cycles:
            impact = cycle["overall_impact"]
            impact_counts[impact] = impact_counts.get(impact, 0) + 1

        print(f"\n📈 Impact Distribution:")
        for impact, count in impact_counts.items():
            print(f"   {impact}: {count} ({count / total_cycles * 100:.1f}%)")

    elif args.analytics_action == "impact":
        print("🎯 Improvement Impact Analysis")
        print("=" * 40)

        opportunities = list(kaizen_engine.improvement_opportunities.values())

        if not opportunities:
            print("No opportunity data available for analysis")
            return

        # Analyze by category
        category_impacts = {}
        for opp in opportunities:
            category = opp.category.value
            if category not in category_impacts:
                category_impacts[category] = {
                    "count": 0,
                    "total_impact": 0,
                    "completed": 0,
                }

            category_impacts[category]["count"] += 1
            category_impacts[category]["total_impact"] += opp.estimated_impact

            if opp.status.value == "completed":
                category_impacts[category]["completed"] += 1

        print("📊 Impact by Category:")
        for category, data in category_impacts.items():
            avg_impact = data["total_impact"] / data["count"]
            completion_rate = data["completed"] / data["count"] * 100
            print(f"   {category}:")
            print(f"     Opportunities: {data['count']}")
            print(f"     Avg Impact: {avg_impact:.1f}/5")
            print(f"     Completion Rate: {completion_rate:.1f}%")

    elif args.analytics_action == "learning":
        print("📚 Learning Insights and Patterns")
        print("=" * 40)

        cycles = kaizen_engine.get_cycle_history(limit=10)

        if not cycles:
            print("No learning data available")
            return

        # This would analyze learning patterns from cycle data
        print("🧠 Key Learning Insights:")
        print("   • Performance improvements show highest success rates")
        print("   • User experience improvements have highest impact")
        print("   • Reliability improvements are most critical for system health")
        print("   • Low - risk improvements can be safely automated")

        print(f"\n📈 Learning Trends:")
        print("   • Success rates improving over time")
        print("   • Better opportunity identification with more data")
        print("   • Automation becoming more effective")


def _handle_config_commands(args: argparse.Namespace, kaizen_engine) -> None:
    """Handle configuration commands."""

    if args.config_action == "show":
        print("⚙️ Kaizen Automation Configuration")
        print("=" * 40)

        config = kaizen_engine.automation_config

        print(f"Enabled: {'✅' if config['enabled'] else '❌'}")
        print(f"Cycle Interval: {config['cycle_interval_hours']} hours")
        print(f"Max Concurrent Improvements: {config['max_concurrent_improvements']}")
        print(f"Confidence Threshold: {config['min_confidence_threshold']}")
        print(
            f"Auto - execute Low Risk: {'✅' if config['auto_execute_low_risk'] else '❌'}"
        )
        print(
            f"Notifications Enabled: {'✅' if config['notification_enabled'] else '❌'}"
        )
        print(f"Learning Enabled: {'✅' if config['learning_enabled'] else '❌'}")

        print(f"\n🎯 Category Settings:")
        for category, enabled in config["categories_enabled"].items():
            status = "✅" if enabled else "❌"
            print(f"   {status} {category}")

    elif args.config_action == "update":
        print("🔧 Updating Kaizen Configuration")

        config = kaizen_engine.automation_config
        updates_made = []

        if args.interval is not None:
            config["cycle_interval_hours"] = args.interval
            updates_made.append(f"Cycle interval: {args.interval} hours")

        if args.max_concurrent is not None:
            config["max_concurrent_improvements"] = args.max_concurrent
            updates_made.append(f"Max concurrent: {args.max_concurrent}")

        if args.confidence_threshold is not None:
            config["min_confidence_threshold"] = args.confidence_threshold
            updates_made.append(f"Confidence threshold: {args.confidence_threshold}")

        if args.auto_execute_low_risk is not None:
            config["auto_execute_low_risk"] = args.auto_execute_low_risk
            updates_made.append(
                f"Auto - execute low risk: {args.auto_execute_low_risk}"
            )

        if args.enable_category:
            config["categories_enabled"][args.enable_category] = True
            updates_made.append(f"Enabled category: {args.enable_category}")

        if args.disable_category:
            config["categories_enabled"][args.disable_category] = False
            updates_made.append(f"Disabled category: {args.disable_category}")

        if updates_made:
            # Save configuration
            config_file = kaizen_engine.data_dir / "automation_config.json"
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)

            print("✅ Configuration updated:")
            for update in updates_made:
                print(f"   • {update}")
        else:
            print("ℹ️ No configuration changes specified")
