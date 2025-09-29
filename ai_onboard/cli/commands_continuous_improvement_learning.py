"""
Continuous Improvement Learning Commands.

This module handles learning-related commands for the continuous improvement system.
"""

import argparse
from pathlib import Path

from ai_onboard.core.ai_integration.user_preference_learning import (
    get_user_preference_learning_system,
)
from ai_onboard.core.continuous_improvement.continuous_improvement_system import (
    LearningType,
    get_continuous_improvement_system,
)


def add_learning_commands(subparsers):
    """Add learning-related commands to the CLI."""

    learning_parser = subparsers.add_parser(
        "learning",
        help="Manage learning and adaptation features",
    )
    learning_subparsers = learning_parser.add_subparsers(
        dest="learning_cmd", help="Learning command"
    )

    # Record learning event
    record_parser = learning_subparsers.add_parser(
        "record", help="Record a learning event"
    )
    record_parser.add_argument(
        "--type",
        choices=[t.value for t in LearningType],
        required=True,
        help="Type of learning event",
    )
    record_parser.add_argument(
        "--description", required=True, help="Description of the learning event"
    )
    record_parser.add_argument("--user", default="default", help="User ID")
    record_parser.add_argument("--session", help="Session ID")
    record_parser.add_argument("--outcome", help="Learning outcome")

    # Show learning summary
    summary_parser = learning_subparsers.add_parser(
        "summary", help="Show learning summary"
    )
    summary_parser.add_argument("--user", default="default", help="User ID")
    summary_parser.add_argument("--days", type=int, default=7, help="Days to include")

    # Show learning events
    events_parser = learning_subparsers.add_parser(
        "events", help="Show learning events"
    )
    events_parser.add_argument("--user", default="default", help="User ID")
    events_parser.add_argument("--limit", type=int, default=10, help="Maximum events")


def _handle_learning_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle learning-related commands."""
    system = get_continuous_improvement_system(root)
    preference_system = get_user_preference_learning_system(root)

    if args.learning_cmd == "record":
        _handle_record_learning(args, system)
    elif args.learning_cmd == "summary":
        _handle_learning_summary(args, system)
    elif args.learning_cmd == "events":
        _handle_learning_events(args, system)
    else:
        print("Unknown learning command")


def _handle_record_learning(args: argparse.Namespace, system) -> None:
    """Record a learning event."""
    try:
        learning_type = LearningType(args.type)

        # Record the learning event
        event_id = system.record_learning_event(
            user_id=args.user,
            session_id=args.session,
            learning_type=learning_type,
            description=args.description,
            outcome=args.outcome,
        )

        print(f"Learning event recorded with ID: {event_id}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error recording learning event: {e}")


def _handle_learning_summary(args: argparse.Namespace, system) -> None:
    """Show learning summary."""
    try:
        summary = system.get_learning_summary(user_id=args.user, days=args.days)

        print("Learning Summary:")
        print(f"  Total Events: {summary.get('total_events', 0)}")
        print(f"  Learning Rate: {summary.get('learning_rate', 0):.2f}")
        print(f"  Adaptation Events: {summary.get('adaptation_events', 0)}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error getting learning summary: {e}")


def _handle_learning_events(args: argparse.Namespace, system) -> None:
    """Show learning events."""
    try:
        events = system.get_learning_events(user_id=args.user, limit=args.limit)

        print(f"Recent Learning Events ({len(events)}):")
        for event in events:
            print(
                f"  {event.get('timestamp', 'Unknown')} - {event.get('type', 'Unknown')}"
            )
            print(f"    {event.get('description', 'No description')}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error getting learning events: {e}")
