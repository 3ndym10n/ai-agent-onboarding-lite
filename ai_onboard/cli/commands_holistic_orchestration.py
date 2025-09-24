"""
CLI commands for holistic tool orchestration system.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from ..core.comprehensive_tool_discovery import get_comprehensive_tool_discovery
from ..core.holistic_tool_orchestration import (
    OrchestrationStrategy,
    get_holistic_tool_orchestrator,
)
from ..core.tool_usage_tracker import get_tool_tracker


def add_holistic_orchestration_commands(subparsers):
    """Add holistic orchestration commands to CLI."""

    # Holistic orchestration main command
    holistic_parser = subparsers.add_parser(
        "holistic", help="Holistic tool orchestration - coordinate all available tools"
    )

    holistic_subparsers = holistic_parser.add_subparsers(
        dest="holistic_cmd", required=True, help="Holistic orchestration subcommands"
    )

    # Discover all tools
    discover_parser = holistic_subparsers.add_parser(
        "discover", help="Discover all available tools in the system"
    )
    discover_parser.add_argument(
        "--categories", action="store_true", help="Show tools grouped by category"
    )
    discover_parser.add_argument(
        "--details", action="store_true", help="Show detailed tool information"
    )

    # Orchestrate tools for a request
    orchestrate_parser = holistic_subparsers.add_parser(
        "orchestrate", help="Orchestrate all relevant tools for a request"
    )
    orchestrate_parser.add_argument(
        "request", help="User request to orchestrate tools for"
    )
    orchestrate_parser.add_argument(
        "--strategy",
        choices=[
            "vision_first",
            "safety_first",
            "user_preference_driven",
            "comprehensive_analysis",
            "adaptive",
        ],
        default="adaptive",
        help="Orchestration strategy to use",
    )
    orchestrate_parser.add_argument(
        "--context", help="Additional context for the request (JSON format)"
    )
    orchestrate_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Maximum execution time in seconds (default: 300)",
    )

    # Show orchestration status
    status_parser = holistic_subparsers.add_parser(
        "status", help="Show holistic orchestration system status"
    )
    status_parser.add_argument(
        "--history", action="store_true", help="Show execution history"
    )
    status_parser.add_argument(
        "--stats", action="store_true", help="Show orchestration statistics"
    )


def handle_holistic_orchestration_commands(args, root: Path):
    """Handle holistic orchestration commands."""

    if args.holistic_cmd == "discover":
        handle_discover_tools(args, root)
    elif args.holistic_cmd == "orchestrate":
        handle_orchestrate_tools(args, root)
    elif args.holistic_cmd == "status":
        handle_orchestration_status(args, root)
    else:
        print(f"❌ Unknown holistic command: {args.holistic_cmd}")


def handle_discover_tools(args, root: Path):
    """Handle tool discovery command."""

    print("🔍 Discovering all available tools in the ai_onboard system...")

    # Get tool discovery
    discovery = get_comprehensive_tool_discovery(root)
    result = discovery.discover_all_tools()

    print(f"\n📊 DISCOVERY RESULTS:")
    print(f"   • Total tools discovered: {result.total_tools}")
    print(f"   • Categories: {len(result.tools_by_category)}")

    if result.discovery_errors:
        print(f"   • Errors: {len(result.discovery_errors)}")
        for error in result.discovery_errors:
            print(f"     - {error}")

    if args.categories:
        print(f"\n📂 TOOLS BY CATEGORY:")
        for category, tools in result.tools_by_category.items():
            print(f"   {category.value}: {len(tools)} tools")

            if args.details:
                for tool in tools[:5]:  # Show first 5 tools per category
                    print(f"     • {tool.name}: {tool.description}")
                if len(tools) > 5:
                    print(f"     ... and {len(tools) - 5} more")

    if args.details and not args.categories:
        print(f"\n🛠️  ALL TOOLS:")
        for tool_name, metadata in result.all_tools.items():
            print(f"   • {tool_name}")
            print(f"     Category: {metadata.category.value}")
            print(f"     Description: {metadata.description}")
            if metadata.keywords:
                print(f"     Keywords: {', '.join(metadata.keywords[:5])}")
            if metadata.gate_requirements:
                print(f"     Gates: {', '.join(metadata.gate_requirements)}")
            print()


def handle_orchestrate_tools(args, root: Path):
    """Handle tool orchestration command."""

    print(f"🎯 Orchestrating tools for request: '{args.request}'")
    print(f"📋 Strategy: {args.strategy}")

    # Get orchestration strategy
    strategy_map = {
        "vision_first": OrchestrationStrategy.VISION_FIRST,
        "safety_first": OrchestrationStrategy.SAFETY_FIRST,
        "user_preference_driven": OrchestrationStrategy.USER_PREFERENCE_DRIVEN,
        "comprehensive_analysis": OrchestrationStrategy.COMPREHENSIVE_ANALYSIS,
        "adaptive": OrchestrationStrategy.ADAPTIVE,
    }

    strategy = strategy_map[args.strategy]

    # Parse context if provided
    context = {}
    if args.context:
        try:

            context = json.loads(args.context)
        except json.JSONDecodeError:
            print(f"⚠️  Invalid JSON context, ignoring: {args.context}")

    # Get holistic orchestrator
    orchestrator = get_holistic_tool_orchestrator(root)

    # Execute orchestration
    print(f"\n🚀 Starting holistic orchestration...")
    result = orchestrator.orchestrate_tools_for_request(args.request, context, strategy)

    # Display results
    print(f"\n📊 ORCHESTRATION RESULTS:")
    print(f"   • Success: {'✅' if result.success else '❌'}")
    print(f"   • Tools executed: {len(result.executed_tools)}")
    print(f"   • Execution time: {result.total_execution_time:.2f}s")
    print(f"   • Vision alignment: {result.vision_alignment_score:.2f}")
    print(f"   • User preference compliance: {result.user_preference_compliance:.2f}")
    print(f"   • Safety compliance: {result.safety_compliance:.2f}")

    if result.executed_tools:
        print(f"\n🛠️  EXECUTED TOOLS:")
        for tool_name in result.executed_tools:
            print(f"   • {tool_name}")

    if result.insights:
        print(f"\n💡 INSIGHTS:")
        for insight in result.insights[:10]:  # Show first 10 insights
            print(f"   • {insight}")
        if len(result.insights) > 10:
            print(f"   ... and {len(result.insights) - 10} more insights")

    if result.recommendations:
        print(f"\n🎯 RECOMMENDATIONS:")
        for recommendation in result.recommendations[
            :5
        ]:  # Show first 5 recommendations
            print(f"   • {recommendation}")
        if len(result.recommendations) > 5:
            print(f"   ... and {len(result.recommendations) - 5} more recommendations")

    if result.errors:
        print(f"\n❌ ERRORS:")
        for error in result.errors:
            print(f"   • {error}")


def handle_orchestration_status(args, root: Path):
    """Handle orchestration status command."""

    print("📊 Holistic Tool Orchestration System Status")
    print("=" * 50)

    # Get orchestrator
    orchestrator = get_holistic_tool_orchestrator(root)

    # Show discovery status
    discovery = get_comprehensive_tool_discovery(root)
    discovery_result = discovery.discover_all_tools()

    print(f"🔍 Tool Discovery:")
    print(f"   • Total tools: {discovery_result.total_tools}")
    print(f"   • Categories: {len(discovery_result.tools_by_category)}")
    print(f"   • Discovery errors: {len(discovery_result.discovery_errors)}")

    # Show user preferences
    print(f"\n👤 User Preferences:")
    print(
        f"   • Communication style: {orchestrator.user_preferences.get('communication_style', 'unknown')}"
    )
    print(
        f"   • Tool preferences: {len(orchestrator.user_preferences.get('tool_preferences',
            []))} tools"
    )
    print(
        f"   • Safety level: {orchestrator.user_preferences.get('safety_level', 'unknown')}"
    )
    print(
        f"   • Vision alignment required: {orchestrator.user_preferences.get('vision_alignment_required',
            False)}"
    )

    # Show vision context
    print(f"\n🎯 Vision Context:")
    print(
        f"   • Project goals: {len(orchestrator.vision_context.get('project_goals',
            []))}"
    )
    print(f"   • Non-goals: {len(orchestrator.vision_context.get('non_goals', []))}")
    print(
        f"   • Risk appetite: {orchestrator.vision_context.get('risk_appetite', 'unknown')}"
    )
    print(f"   • Milestones: {len(orchestrator.vision_context.get('milestones', []))}")

    # Show safety gates
    print(f"\n🛡️  Safety Gates:")
    for gate_name, gate_config in orchestrator.safety_gates.items():
        enabled = gate_config.get("enabled", False)
        threshold = gate_config.get("threshold", 0.0)
        print(f"   • {gate_name}: {'✅' if enabled else '❌'} (threshold: {threshold})")

    # Show execution history
    if args.history:
        print(f"\n📈 Execution History:")
        if orchestrator.execution_history:
            for i, execution in enumerate(
                orchestrator.execution_history[-10:]
            ):  # Show last 10
                timestamp = execution["timestamp"]
                request = (
                    execution["user_request"][:50] + "..."
                    if len(execution["user_request"]) > 50
                    else execution["user_request"]
                )
                tools_count = len(execution["executed_tools"])
                success = "✅" if execution["success"] else "❌"
                exec_time = execution["execution_time"]

                print(f"   {i+1}. {success} {request}")
                print(
                    f"      Tools: {tools_count}, "
                    f"Time: {exec_time:.2f}s, Strategy: {execution['strategy']}"
                )
        else:
            print("   No execution history available")

    # Show statistics
    if args.stats:
        print(f"\n📊 Statistics:")
        if orchestrator.execution_history:
            total_executions = len(orchestrator.execution_history)
            successful_executions = sum(
                1 for e in orchestrator.execution_history if e["success"]
            )
            avg_execution_time = (
                sum(e["execution_time"] for e in orchestrator.execution_history)
                / total_executions
            )
            total_tools_executed = sum(
                len(e["executed_tools"]) for e in orchestrator.execution_history
            )

            print(f"   • Total executions: {total_executions}")
            print(
                f"   • Success rate: {successful_executions/total_executions*100:.1f}%"
            )
            print(f"   • Average execution time: {avg_execution_time:.2f}s")
            print(f"   • Total tools executed: {total_tools_executed}")
            print(
                f"   • Average tools per execution: {total_tools_executed/total_executions:.1f}"
            )
        else:
            print("   No statistics available (no execution history)")
