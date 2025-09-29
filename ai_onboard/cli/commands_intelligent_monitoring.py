"""
CLI commands for intelligent development monitoring.

Provides commands to control and interact with the intelligent development monitor
that automatically applies development tools based on activities and context.
"""

import time
from pathlib import Path

from ..core.ai_integration.intelligent_development_monitor import (
    get_development_monitor,
    start_intelligent_monitoring,
    stop_intelligent_monitoring,
)
from ..core.utilities.unicode_utils import print_status


def add_intelligent_monitoring_commands(subparsers):
    """Add intelligent monitoring commands to the argument parser."""

    # Main intelligent command
    intelligent_parser = subparsers.add_parser(
        "intelligent", help="Intelligent development monitoring and tool orchestration"
    )

    intelligent_sub = intelligent_parser.add_subparsers(
        dest="intelligent_cmd", help="Intelligent monitoring subcommands"
    )

    # Start monitoring
    start_parser = intelligent_sub.add_parser(
        "start", help="Start intelligent development monitoring"
    )

    # Stop monitoring
    stop_parser = intelligent_sub.add_parser(
        "stop", help="Stop intelligent development monitoring"
    )

    # Status monitoring
    status_parser = intelligent_sub.add_parser(
        "status", help="Show intelligent monitoring status"
    )

    # Manual analysis trigger
    analyze_parser = intelligent_sub.add_parser(
        "analyze", help="Manually trigger development analysis"
    )
    analyze_parser.add_argument(
        "analysis_type",
        choices=["code_quality", "organization", "risk", "comprehensive"],
        help="Type of analysis to trigger",
    )

    # Activity history
    history_parser = intelligent_sub.add_parser(
        "history", help="Show recent development activities"
    )
    history_parser.add_argument(
        "--limit", type=int, default=10, help="Number of recent activities to show"
    )


def handle_intelligent_monitoring_commands(args, root: Path):
    """Handle intelligent monitoring commands."""

    monitor = get_development_monitor(root)

    if args.intelligent_cmd == "start":
        print("🚀 Starting Intelligent Development Monitor...")
        start_intelligent_monitoring(root)
        print_status("✅ Intelligent monitoring started")
        print("   📊 System will now automatically apply development tools")
        print("   🔍 Monitoring file changes, git operations, and conversations")

    elif args.intelligent_cmd == "stop":
        print("🛑 Stopping Intelligent Development Monitor...")
        stop_intelligent_monitoring()
        print_status("✅ Intelligent monitoring stopped")

    elif args.intelligent_cmd == "status":
        status = monitor.get_monitoring_status()
        print("🧠 INTELLIGENT DEVELOPMENT MONITOR STATUS")
        print("=" * 50)
        print(f"Monitoring Active: {'✅' if status['monitoring_active'] else '❌'}")
        print(f"Activities Detected: {status['activities_detected']}")
        print(f"Active Rules: {status['rules_active']}")

        if status["recent_activities"]:
            print(f"\n📋 RECENT ACTIVITIES (last {len(status['recent_activities'])}):")
            for i, activity in enumerate(status["recent_activities"], 1):
                print(
                    f"   {i}. {activity['type']} - {activity['tools_triggered'] or 'No tools'}"
                )
        else:
            print("\n📋 No recent activities detected")

        print("\n🤖 AUTO-TRIGGER RULES:")
        for rule in monitor.trigger_rules:
            cooldown_status = ""
            if rule.last_triggered:
                time_since = time.time() - rule.last_triggered
                if time_since < rule.cooldown_seconds:
                    cooldown_status = (
                        f" (cooldown: {int(rule.cooldown_seconds - time_since)}s)"
                    )
            print(f"   • {rule.rule_name}: {rule.required_tools} {cooldown_status}")

    elif args.intelligent_cmd == "analyze":
        monitor.manually_trigger_analysis(args.analysis_type)

    elif args.intelligent_cmd == "history":
        status = monitor.get_monitoring_status()
        activities = status.get("recent_activities", [])

        if not activities:
            print("📋 No development activities recorded yet")
            return

        print("📚 DEVELOPMENT ACTIVITY HISTORY")
        print("=" * 50)

        # Show activities up to the limit
        for i, activity in enumerate(activities[-args.limit :], 1):
            print(f"{i}. {activity['type'].upper()}")
            print(f"   Timestamp: {time.ctime(activity['timestamp'])}")
            if activity["tools_triggered"]:
                print(f"   Tools Applied: {', '.join(activity['tools_triggered'])}")
            else:
                print("   Tools Applied: None")
            print()

        print(f"Total activities in history: {len(activities)}")


# Integration functions for automatic startup


def initialize_intelligent_monitoring(root: Path):
    """
    Initialize intelligent monitoring on system startup.

    This should be called during ai_onboard initialization to ensure
    the intelligent monitor is always running in the background.
    """
    try:
        # Start intelligent monitoring automatically
        start_intelligent_monitoring(root)
        from ..core.utilities.unicode_utils import ensure_unicode_safe

        ensure_unicode_safe("🧠 Intelligent Development Monitor initialized")
    except Exception as e:
        from ..core.utilities.unicode_utils import ensure_unicode_safe

        ensure_unicode_safe(f"⚠️ Failed to initialize intelligent monitoring: {e}")


def shutdown_intelligent_monitoring():
    """Shutdown intelligent monitoring on system exit."""
    try:
        stop_intelligent_monitoring()
        from ..core.utilities.unicode_utils import ensure_unicode_safe

        ensure_unicode_safe("🧠 Intelligent Development Monitor shutdown")
    except Exception as e:
        from ..core.utilities.unicode_utils import ensure_unicode_safe

        ensure_unicode_safe(f"⚠️ Error during intelligent monitoring shutdown: {e}")
