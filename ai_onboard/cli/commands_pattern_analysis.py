"""
Pattern Analysis Commands - CLI commands for pattern recognition and learning.

This module provides commands to:
- View pattern insights and recommendations
- Trigger learning from errors
- Analyze CLI usage patterns and behavior
"""

import argparse
from pathlib import Path
from typing import Any, Dict

from ..core.pattern_recognition_system import PatternRecognitionSystem
from ..core.tool_usage_tracker import track_tool_usage


def add_pattern_analysis_commands(subparsers: argparse._SubParsersAction) -> None:
    """Add pattern analysis commands to the CLI."""
    pattern_parser = subparsers.add_parser(
        "patterns", help="Analyze and learn from error patterns and user behavior"
    )

    pattern_subparsers = pattern_parser.add_subparsers(
        dest="pattern_action", help="Pattern analysis actions"
    )

    # Insights command
    pattern_subparsers.add_parser(
        "insights",
        help="Show pattern insights, CLI recommendations, and behavior analysis",
    )

    # Learn command
    pattern_subparsers.add_parser(
        "learn", help="Trigger learning from recent errors and command patterns"
    )

    # Stats command
    pattern_subparsers.add_parser(
        "stats", help="Show pattern learning statistics and system health"
    )


def handle_pattern_analysis_commands(args: argparse.Namespace, root: Path) -> bool:
    """
    Handle pattern analysis commands.

    Args:
        args: Parsed command line arguments
        root: Project root directory

    Returns:
        True if command was handled, False otherwise
    """
    pattern_action = getattr(args, "pattern_action", None)

    if pattern_action == "insights":
        return _handle_insights(args, root)
    elif pattern_action == "learn":
        return _handle_learn(args, root)
    elif pattern_action == "stats":
        return _handle_stats(args, root)

    return False


def _handle_insights(args: argparse.Namespace, root: Path) -> bool:
    """Handle pattern insights display."""
    track_tool_usage(
        "pattern_analysis", "cli_command", {"action": "insights"}, "success"
    )

    try:
        pattern_system = PatternRecognitionSystem(root)

        print("🎯 PATTERN RECOGNITION INSIGHTS")
        print("=" * 50)

        # CLI recommendations
        cli_recommendations = pattern_system.get_cli_recommendations()
        if cli_recommendations:
            print("\n💡 CLI Usage Recommendations:")
            for i, rec in enumerate(cli_recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print("\n💡 CLI Usage: No recommendations available yet")
            print("   Run more commands to build usage patterns")

        # Behavior insights
        behavior_insights = pattern_system.get_behavior_insights()
        if behavior_insights:
            print("\n🧠 User Behavior Insights:")
            for i, insight in enumerate(behavior_insights, 1):
                print(f"   {i}. [{insight['pattern_type']}] {insight['description']}")
                print(
                    f"      Frequency: {insight['frequency']}, Confidence: {insight['confidence']:.2f}"
                )
                if insight["recommendations"]:
                    print(f"      💡 {insight['recommendations'][0]}")
        else:
            print("\n🧠 Behavior Patterns: No insights available yet")
            print("   Continue using the system to develop behavior patterns")

        print("\n📊 Pattern Statistics:")
        print(f"   Error Patterns: {len(pattern_system.patterns)}")
        print(f"   CLI Patterns: {len(pattern_system.cli_patterns)}")
        print(f"   Behavior Patterns: {len(pattern_system.behavior_patterns)}")
        print(f"   Command History: {len(pattern_system.command_history)}")

        return True

    except Exception as e:
        print(f"❌ Error getting pattern insights: {e}")
        track_tool_usage(
            "pattern_analysis",
            "cli_command",
            {"action": "insights", "error": str(e)},
            "failed",
        )
        return True


def _handle_learn(args: argparse.Namespace, root: Path) -> bool:
    """Handle pattern learning from recent errors."""
    track_tool_usage("pattern_analysis", "cli_command", {"action": "learn"}, "success")

    try:
        print("🔍 Scanning for recent errors to learn from...")

        pattern_system = PatternRecognitionSystem(root)

        print(
            f"✅ Pattern system ready - {len(pattern_system.patterns)} existing patterns"
        )
        print("💡 The system automatically learns from command usage and errors")

        # Learn from recent learning history errors
        learned_count = 0
        try:
            # Get recent learning events that contain errors
            recent_learning_events = pattern_system.persistence.get_learning_history(
                limit=50
            )

            # Filter for error-related learning events
            error_events = [
                event
                for event in recent_learning_events
                if event.get("event_type") in ["pattern_learned", "error_prevented"]
                or "error" in event.get("event_type", "").lower()
            ]

            if error_events:
                print(
                    f"\n📚 Found {len(error_events)} recent error-related learning events to analyze"
                )
                for event in error_events[:5]:  # Learn from first 5
                    event_data = event.get("event_data", {})

                    # Reconstruct error data from learning event
                    error_data = {
                        "type": event_data.get("error_type", "unknown"),
                        "message": event_data.get("error_message", ""),
                        "timestamp": event.get("timestamp", 0),
                        "file": event_data.get("file", ""),
                        "traceback": event_data.get("traceback", ""),
                    }
                    pattern_system.learn_from_repeated_errors(error_data)
                    learned_count += 1

                if learned_count > 0:
                    print(f"✅ Learned from {learned_count} error patterns")
            else:
                print("\n📚 No recent error events found in learning history")

        except Exception as e:
            print(f"⚠️  Could not scan learning history: {e}")

        # Show updated pattern counts
        print("\n📊 Updated Pattern Statistics:")
        print(f"   Error Patterns: {len(pattern_system.patterns)}")
        print(f"   CLI Patterns: {len(pattern_system.cli_patterns)}")
        print(f"   Behavior Patterns: {len(pattern_system.behavior_patterns)}")

        return True

    except Exception as e:
        print(f"❌ Error during pattern learning: {e}")
        track_tool_usage(
            "pattern_analysis",
            "cli_command",
            {"action": "learn", "error": str(e)},
            "failed",
        )
        return True


def _handle_stats(args: argparse.Namespace, root: Path) -> bool:
    """Handle pattern statistics display."""
    track_tool_usage("pattern_analysis", "cli_command", {"action": "stats"}, "success")

    try:
        pattern_system = PatternRecognitionSystem(root)

        print("📊 PATTERN LEARNING STATISTICS")
        print("=" * 40)

        print(f"Error Patterns: {len(pattern_system.patterns)}")
        if pattern_system.patterns:
            # Show top patterns by frequency
            top_patterns = sorted(
                pattern_system.patterns.values(),
                key=lambda p: p.frequency,
                reverse=True,
            )[:5]

            print("\n🎯 Top Error Patterns by Frequency:")
            for i, pattern in enumerate(top_patterns, 1):
                print(f"   {i}. {pattern.pattern_type}: {pattern.signature[:60]}...")
                print(
                    f"      Frequency: {pattern.frequency}, Confidence: {pattern.confidence:.2f}"
                )

        print(f"\nCLI Patterns: {len(pattern_system.cli_patterns)}")
        if pattern_system.cli_patterns:
            # Show successful command patterns
            successful_patterns = [
                p for p in pattern_system.cli_patterns.values() if p.success_rate > 70
            ]
            print(f"   High Success Rate (>70%): {len(successful_patterns)}")

        print(f"\nBehavior Patterns: {len(pattern_system.behavior_patterns)}")
        if pattern_system.behavior_patterns:
            # Show confident behavior patterns
            confident_patterns = [
                p
                for p in pattern_system.behavior_patterns.values()
                if p.confidence > 0.7
            ]
            print(f"   High Confidence (>70%): {len(confident_patterns)}")

        print(f"\nCommand History: {len(pattern_system.command_history)} entries")

        # Learning persistence stats
        try:
            persistence = pattern_system.persistence
            print("\n💾 Learning Persistence:")
            print(
                f"   Patterns Learned: {persistence.stats.get('patterns_learned', 0)}"
            )
            print(
                f"   Patterns Applied: {persistence.stats.get('patterns_applied', 0)}"
            )
            print(
                f"   Errors Prevented: {persistence.stats.get('errors_prevented', 0)}"
            )
        except Exception:
            print("\n💾 Learning Persistence: Stats unavailable")

        return True

    except Exception as e:
        print(f"❌ Error getting pattern stats: {e}")
        track_tool_usage(
            "pattern_analysis",
            "cli_command",
            {"action": "stats", "error": str(e)},
            "failed",
        )
        return True
