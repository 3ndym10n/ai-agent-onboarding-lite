"""
Continuous Improvement Implementation Commands.

This module handles implementation-related commands for the continuous improvement system.
"""

import argparse
from pathlib import Path

from ai_onboard.core.continuous_improvement.continuous_improvement_system import (
    get_continuous_improvement_system,
)


def add_implementation_commands(subparsers):
    """Add implementation-related commands to the CLI."""

    implementation_parser = subparsers.add_parser(
        "implementation",
        help="Manage system implementation and deployment",
    )
    implementation_subparsers = implementation_parser.add_subparsers(
        dest="implementation_cmd", help="Implementation command"
    )

    # Deploy improvements
    deploy_parser = implementation_subparsers.add_parser(
        "deploy", help="Deploy approved improvements"
    )
    deploy_parser.add_argument("recommendation_id", help="Recommendation ID to deploy")
    deploy_parser.add_argument(
        "--auto", action="store_true", help="Deploy automatically"
    )

    # Rollback improvements
    rollback_parser = implementation_subparsers.add_parser(
        "rollback", help="Rollback a deployed improvement"
    )
    rollback_parser.add_argument("deployment_id", help="Deployment ID to rollback")
    rollback_parser.add_argument("--reason", required=True, help="Reason for rollback")

    # Show deployments
    deployments_parser = implementation_subparsers.add_parser(
        "deployments", help="Show deployment history"
    )
    deployments_parser.add_argument(
        "--limit", type=int, default=10, help="Maximum deployments"
    )


def _handle_implementation_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle implementation-related commands."""
    system = get_continuous_improvement_system(root)

    if args.implementation_cmd == "deploy":
        _handle_deploy_improvement(args, system)
    elif args.implementation_cmd == "rollback":
        _handle_rollback_improvement(args, system)
    elif args.implementation_cmd == "deployments":
        _handle_show_deployments(args, system)
    else:
        print("Unknown implementation command")


def _handle_deploy_improvement(args: argparse.Namespace, system) -> None:
    """Deploy an approved improvement."""
    try:
        if args.auto:
            result = system.deploy_improvement_auto(args.recommendation_id)
            print(f"Auto-deployed improvement: {result.get('status', 'Unknown')}")
        else:
            result = system.deploy_improvement_manual(args.recommendation_id)
            print(f"Manual deployment initiated: {result.get('status', 'Unknown')}")

        if result.get("deployment_id"):
            print(f"Deployment ID: {result['deployment_id']}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error deploying improvement: {e}")


def _handle_rollback_improvement(args: argparse.Namespace, system) -> None:
    """Rollback a deployed improvement."""
    try:
        result = system.rollback_improvement(args.deployment_id, args.reason)

        if result.get("success"):
            print(f"Successfully rolled back deployment {args.deployment_id}")
        else:
            print(f"Failed to rollback deployment {args.deployment_id}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error rolling back improvement: {e}")


def _handle_show_deployments(args: argparse.Namespace, system) -> None:
    """Show deployment history."""
    try:
        deployments = system.get_deployment_history(limit=args.limit)

        print(f"Recent Deployments ({len(deployments)}):")
        for deployment in deployments:
            status = deployment.get("status", "Unknown")
            status_icon = {"success": "✓", "failed": "✗", "rolled_back": "↺"}.get(
                status, "?"
            )
            print(
                f"  {status_icon} {deployment.get('id', 'Unknown')} - {deployment.get('recommendation_id', 'Unknown')}"
            )
            print(f"      Status: {status}")
            print(f"      Deployed: {deployment.get('deployed_at', 'Unknown')}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error getting deployments: {e}")
