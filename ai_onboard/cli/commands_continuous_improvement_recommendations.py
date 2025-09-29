"""
Continuous Improvement Recommendations Commands.

This module handles recommendation-related commands for the continuous improvement system.
"""

import argparse
from pathlib import Path

from ai_onboard.core.continuous_improvement.continuous_improvement_system import (
    get_continuous_improvement_system,
)


def add_recommendations_commands(subparsers):
    """Add recommendation-related commands to the CLI."""

    recommendations_parser = subparsers.add_parser(
        "recommendations",
        help="Manage system recommendations",
    )
    recommendations_subparsers = recommendations_parser.add_subparsers(
        dest="recommendations_cmd", help="Recommendations command"
    )

    # List recommendations
    list_parser = recommendations_subparsers.add_parser(
        "list", help="List system recommendations"
    )
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument(
        "--limit", type=int, default=10, help="Maximum recommendations"
    )

    # Show recommendation details
    show_parser = recommendations_subparsers.add_parser(
        "show", help="Show recommendation details"
    )
    show_parser.add_argument("recommendation_id", help="Recommendation ID")

    # Approve recommendation
    approve_parser = recommendations_subparsers.add_parser(
        "approve", help="Approve a recommendation"
    )
    approve_parser.add_argument("recommendation_id", help="Recommendation ID")
    approve_parser.add_argument("--user", default="default", help="User ID")

    # Reject recommendation
    reject_parser = recommendations_subparsers.add_parser(
        "reject", help="Reject a recommendation"
    )
    reject_parser.add_argument("recommendation_id", help="Recommendation ID")
    reject_parser.add_argument("--reason", help="Reason for rejection")


def _handle_recommendations_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle recommendation-related commands."""
    system = get_continuous_improvement_system(root)

    if args.recommendations_cmd == "list":
        _handle_list_recommendations(args, system)
    elif args.recommendations_cmd == "show":
        _handle_show_recommendation(args, system)
    elif args.recommendations_cmd == "approve":
        _handle_approve_recommendation(args, system)
    elif args.recommendations_cmd == "reject":
        _handle_reject_recommendation(args, system)
    else:
        print("Unknown recommendations command")


def _handle_list_recommendations(args: argparse.Namespace, system) -> None:
    """List system recommendations."""
    try:
        recommendations = system.get_recommendations(
            category=args.category, limit=args.limit
        )

        print(f"System Recommendations ({len(recommendations)}):")
        for rec in recommendations:
            print(f"  {rec.get('id', 'Unknown')} - {rec.get('title', 'No title')}")
            print(f"    Priority: {rec.get('priority', 'Unknown')}")
            print(f"    Category: {rec.get('category', 'Unknown')}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error listing recommendations: {e}")


def _handle_show_recommendation(args: argparse.Namespace, system) -> None:
    """Show recommendation details."""
    try:
        recommendation = system.get_recommendation_details(args.recommendation_id)

        if not recommendation:
            print(f"Recommendation {args.recommendation_id} not found")
            return

        print(f"Recommendation: {recommendation.get('title', 'Unknown')}")
        print(f"ID: {args.recommendation_id}")
        print(f"Priority: {recommendation.get('priority', 'Unknown')}")
        print(f"Category: {recommendation.get('category', 'Unknown')}")
        print(f"Description: {recommendation.get('description', 'No description')}")
        print(f"Impact: {recommendation.get('estimated_impact', 'Unknown')}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error showing recommendation: {e}")


def _handle_approve_recommendation(args: argparse.Namespace, system) -> None:
    """Approve a recommendation."""
    try:
        result = system.approve_recommendation(
            recommendation_id=args.recommendation_id, user_id=args.user
        )

        if result:
            print(f"Recommendation {args.recommendation_id} approved")
        else:
            print(f"Failed to approve recommendation {args.recommendation_id}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error approving recommendation: {e}")


def _handle_reject_recommendation(args: argparse.Namespace, system) -> None:
    """Reject a recommendation."""
    try:
        result = system.reject_recommendation(
            recommendation_id=args.recommendation_id, reason=args.reason
        )

        if result:
            print(f"Recommendation {args.recommendation_id} rejected")
        else:
            print(f"Failed to reject recommendation {args.recommendation_id}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error rejecting recommendation: {e}")
