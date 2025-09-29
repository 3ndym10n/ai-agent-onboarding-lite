"""
Simplified UX-Enhanced CLI Commands - Streamlined user experience improvements.

This module provides essential UX enhancements with:
- Smart help and contextual suggestions
- Adaptive command discovery
- Project status dashboard
- Design validation for UI/UX projects
"""

import argparse
import json
from pathlib import Path

from ..core.ai_integration.user_experience_system import get_user_experience_system
from ..core.utilities.unicode_utils import ensure_unicode_safe


def add_ux_enhanced_commands(subparsers):
    """Add UX-enhanced commands to the CLI."""

    # Smart help command
    help_parser = subparsers.add_parser(
        "help", help="Smart help with contextual suggestions"
    )
    help_parser.add_argument("command", nargs="?", help="Get help for specific command")
    help_parser.add_argument(
        "--suggestions", action="store_true", help="Show smart suggestions"
    )
    help_parser.add_argument(
        "--examples", action="store_true", help="Show usage examples"
    )

    # Project dashboard
    dashboard_parser = subparsers.add_parser(
        "dashboard", help="Project status dashboard"
    )
    dashboard_parser.add_argument(
        "--compact", action="store_true", help="Compact display"
    )

    # Smart suggestions
    suggest_parser = subparsers.add_parser(
        "suggest", help="Get smart command suggestions"
    )
    suggest_parser.add_argument(
        "--context", help="Provide context for better suggestions"
    )

    # Design validation (for UI/UX projects)
    design_parser = subparsers.add_parser(
        "design", help="Design validation for UI/UX projects"
    )
    design_subparsers = design_parser.add_subparsers(
        dest="design_cmd", help="Design commands"
    )

    validate_parser = design_subparsers.add_parser(
        "validate", help="Validate design decisions"
    )
    validate_parser.add_argument(
        "--description", required=True, help="Description of design decision"
    )
    validate_parser.add_argument("--screenshot", help="Path to screenshot for analysis")

    # Project status
    status_parser = subparsers.add_parser("status", help="Enhanced project status")
    status_parser.add_argument("--json", action="store_true", help="JSON output")


def handle_ux_enhanced_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle UX-enhanced commands."""

    ux_system = get_user_experience_system(root)
    user_id = "default"  # Could be extracted from environment or config

    # Record command usage for learning
    ux_system.record_command_usage(user_id, args.cmd, True)

    if args.cmd == "help":
        _handle_smart_help(args, ux_system, user_id)
    elif args.cmd == "dashboard":
        _handle_dashboard(args, ux_system, user_id)
    elif args.cmd == "suggest":
        _handle_suggestions(args, ux_system, user_id)
    elif args.cmd == "design":
        _handle_design_validation(args, ux_system, user_id)
    elif args.cmd == "status":
        _handle_status(args, ux_system, user_id)
    else:
        print(f"Unknown UX command: {args.cmd}")


def _handle_smart_help(args: argparse.Namespace, ux_system, user_id: str) -> None:
    """Handle smart help command."""
    print("🤖 AI-Onboard Smart Help")
    print("=" * 50)

    if args.command:
        # Get adaptive help for specific command
        help_info = ux_system.get_adaptive_help(args.command, user_id)

        ensure_unicode_safe(f"\n📋 Command: {args.command}")
        print(
            f"Description: {help_info.get('description', 'No description available')}"
        )
        print(f"Usage: {help_info.get('usage', 'No usage example available')}")
        print(f"Category: {help_info.get('category', 'Unknown')}")
        print(f"Expertise Level: {help_info.get('expertise_required', 'Unknown')}")

        if help_info.get("prerequisites"):
            print(f"\nPrerequisites:")
            for prereq in help_info["prerequisites"]:
                print(f"  • {prereq}")

        if help_info.get("related_commands"):
            print(f"\nRelated Commands:")
            for related in help_info["related_commands"]:
                print(f"  • {related}")

        if help_info.get("getting_started"):
            print(f"\n💡 Getting Started Tips:")
            for tip in help_info["getting_started"]:
                print(f"  • {tip}")

    else:
        # Show general help with suggestions
        ensure_unicode_safe("\n🎯 Available Commands by Category:")
        ensure_unicode_safe("\n📋 Project Management:")
        print("  • charter    - Create project charter and vision")
        print("  • plan       - Generate project plan")
        print("  • align      - Check alignment with vision")
        print("  • validate   - Validate project progress")

        ensure_unicode_safe("\n🔧 Development:")
        print("  • cleanup    - Safe file cleanup")
        print("  • code-quality - Code analysis")

        print("\n🤖 AI Integration:")
        print("  • cursor     - Cursor AI tools")
        print("  • ai-collaboration - AI agent management")

    # Always show suggestions if requested or no specific command
    if args.suggestions or not args.command:
        suggestions = ux_system.get_smart_suggestions(user_id)
        if suggestions:
            print(f"\n💡 Smart Suggestions:")
            for suggestion in suggestions:
                print(f"  • {suggestion.command}: {suggestion.reason}")
                if suggestion.next_steps:
                    print(f"    → {suggestion.next_steps[0]}")


def _handle_dashboard(args: argparse.Namespace, ux_system, user_id: str) -> None:
    """Handle project dashboard."""
    ensure_unicode_safe("📊 Project Dashboard")
    print("=" * 50)

    status = ux_system.get_project_status(user_id)

    ensure_unicode_safe("\n🏗️  Project Setup:")
    print(f"  Charter: {status['project_setup']['charter']}")
    print(f"  Plan: {status['project_setup']['plan']}")

    if status["recent_activity"]:
        ensure_unicode_safe(f"\n📈 Recent Activity:")
        for cmd in status["recent_activity"]:
            print(f"  • {cmd}")

    print(f"\n👤 Your Expertise Level: {status['expertise_level'].title()}")

    if status["suggestions"]:
        print(f"\n� Suggestions:")
        for suggestion in status["suggestions"]:
            confidence_bar = "█" * int(suggestion.confidence * 10)
            print(f"  • {suggestion.command}: {suggestion.reason}")
            print(f"    Confidence: {confidence_bar} ({suggestion.confidence:.1f})")

    if not args.compact:
        ensure_unicode_safe(f"\n🎯 Next Steps:")
        if not status["project_setup"]["charter"] == "✅":
            print("  1. Create a project charter: python -m ai_onboard charter")
        elif not status["project_setup"]["plan"] == "✅":
            print("  2. Generate a project plan: python -m ai_onboard plan")
        else:
            print("  • Run validation: python -m ai_onboard validate")
            print("  • Check alignment: python -m ai_onboard align")


def _handle_suggestions(args: argparse.Namespace, ux_system, user_id: str) -> None:
    """Handle smart suggestions."""
    print("💡 Smart Suggestions")
    print("=" * 30)

    context = args.context or ""
    suggestions = ux_system.get_smart_suggestions(user_id, context)

    if not suggestions:
        print("\n✨ You're doing great! No specific suggestions right now.")
        print("Try running 'python -m ai_onboard help' to explore available commands.")
        return

    print(f"\nBased on your usage patterns, here are some suggestions:")

    for i, suggestion in enumerate(suggestions, 1):
        ensure_unicode_safe(f"\n{i}. 🎯 {suggestion.command}")
        print(f"   Reason: {suggestion.reason}")
        print(f"   Category: {suggestion.category.value}")
        print(
            f"   Confidence: {'★' * int(suggestion.confidence * 5)} ({suggestion.confidence:.1f})"
        )

        if suggestion.next_steps:
            print(f"   Next: {suggestion.next_steps[0]}")


def _handle_design_validation(
    args: argparse.Namespace, ux_system, user_id: str
) -> None:
    """Handle design validation."""
    if args.design_cmd == "validate":
        print("🎨 Design Validation")
        print("=" * 30)

        screenshot_path = Path(args.screenshot) if args.screenshot else None
        validation = ux_system.validate_design(args.description, screenshot_path)

        print(
            f"\n📊 Overall Score: {'★' * int(validation.score * 5)} ({validation.score:.1f}/1.0)"
        )
        print(
            f"Accessibility: {'★' * int(validation.accessibility_score * 5)} ({validation.accessibility_score:.1f}/1.0)"
        )
        print(
            f"Consistency: {'★' * int(validation.consistency_score * 5)} ({validation.consistency_score:.1f}/1.0)"
        )

        if validation.issues:
            ensure_unicode_safe(f"\n⚠️  Issues Found:")
            for issue in validation.issues:
                print(f"  • {issue}")

        if validation.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in validation.recommendations:
                print(f"  • {rec}")

        if validation.score >= 0.8:
            ensure_unicode_safe(f"\n✅ Great design! Your approach looks solid.")
        elif validation.score >= 0.6:
            print(f"\n👍 Good design with room for improvement.")
        else:
            print(f"\n🔄 Consider addressing the issues above for better UX.")

    else:
        print("Available design commands:")
        print("  validate --description 'your design description'")


def _handle_status(args: argparse.Namespace, ux_system, user_id: str) -> None:
    """Handle enhanced status display."""
    status = ux_system.get_project_status(user_id)

    if args.json:
        print(json.dumps(status, indent=2))
        return

    ensure_unicode_safe("📋 Project Status")
    print("=" * 20)

    setup = status["project_setup"]
    ensure_unicode_safe(f"Charter: {setup['charter']}  Plan: {setup['plan']}")

    if status["recent_activity"]:
        recent = ", ".join(status["recent_activity"][-3:])
        print(f"Recent: {recent}")

    if status["suggestions"]:
        print(f"Suggestions: {len(status['suggestions'])} available")
        print("Run 'python -m ai_onboard suggest' to see them")
