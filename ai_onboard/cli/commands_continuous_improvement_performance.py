"""
Continuous Improvement Performance Commands.

This module handles performance-related commands for the continuous improvement system.
"""

import argparse
from pathlib import Path

from ai_onboard.core.continuous_improvement.performance_optimizer import (
    get_performance_optimizer,
)
from ai_onboard.core.continuous_improvement.system_health_monitor import (
    get_system_health_monitor,
)


def add_performance_commands(subparsers):
    """Add performance-related commands to the CLI."""

    performance_parser = subparsers.add_parser(
        "performance",
        help="Manage system performance and optimization",
    )
    performance_subparsers = performance_parser.add_subparsers(
        dest="performance_cmd", help="Performance command"
    )

    # Monitor performance
    monitor_parser = performance_subparsers.add_parser(
        "monitor", help="Monitor system performance"
    )
    monitor_parser.add_argument(
        "--duration", type=int, default=60, help="Monitor duration in seconds"
    )

    # Show opportunities
    opportunities_parser = performance_subparsers.add_parser(
        "opportunities", help="Show performance optimization opportunities"
    )
    opportunities_parser.add_argument("--category", help="Filter by category")

    # Optimize performance
    optimize_parser = performance_subparsers.add_parser(
        "optimize", help="Optimize system performance"
    )
    optimize_parser.add_argument(
        "--auto", action="store_true", help="Apply optimizations automatically"
    )
    optimize_parser.add_argument("--category", help="Optimize specific category")


def _handle_performance_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle performance-related commands."""
    optimizer = get_performance_optimizer(root)
    health_monitor = get_system_health_monitor(root)

    if args.performance_cmd == "monitor":
        _handle_performance_monitor(args, optimizer, health_monitor)
    elif args.performance_cmd == "opportunities":
        _handle_performance_opportunities(args, optimizer)
    elif args.performance_cmd == "optimize":
        _handle_performance_optimize(args, optimizer)
    else:
        print("Unknown performance command")


def _handle_performance_monitor(
    args: argparse.Namespace, optimizer, health_monitor
) -> None:
    """Monitor system performance."""
    try:
        print(f"Monitoring system performance for {args.duration} seconds...")

        # Start monitoring
        health_monitor.start_monitoring()

        import time

        start_time = time.time()
        while time.time() - start_time < args.duration:
            time.sleep(5)  # Check every 5 seconds
            metrics = health_monitor.get_current_metrics()

            print(f"  CPU: {metrics.get('cpu_percent', 0):.1f}%")
            print(f"  Memory: {metrics.get('memory_percent', 0):.1f}%")
            print(f"  Active Sessions: {metrics.get('active_sessions', 0)}")

        health_monitor.stop_monitoring()
        print("Performance monitoring completed")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error monitoring performance: {e}")


def _handle_performance_opportunities(args: argparse.Namespace, optimizer) -> None:
    """Show performance optimization opportunities."""
    try:
        opportunities = optimizer.get_optimization_opportunities(category=args.category)

        print(f"Performance Optimization Opportunities ({len(opportunities)}):")
        for opp in opportunities[:10]:  # Show top 10
            print(f"  {opp.get('id', 'Unknown')} - {opp.get('title', 'No title')}")
            print(f"    Potential Impact: {opp.get('estimated_impact', 'Unknown')}")
            print(f"    Effort: {opp.get('estimated_effort', 'Unknown')}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error getting optimization opportunities: {e}")


def _handle_performance_optimize(args: argparse.Namespace, optimizer) -> None:
    """Optimize system performance."""
    try:
        if args.auto:
            # Apply all available optimizations
            results = optimizer.apply_all_optimizations()
            print(f"Applied {len(results)} automatic optimizations")
        else:
            # Apply specific category optimizations
            results = optimizer.apply_optimizations(category=args.category)
            print(f"Applied optimizations for category: {args.category}")

        for result in results[:5]:  # Show first 5 results
            print(
                f"  {result.get('optimization', 'Unknown')}: {result.get('status', 'Unknown')}"
            )

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error optimizing performance: {e}")
