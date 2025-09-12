"""Refactored main CLI entry point for ai-onboard."""

import argparse
from pathlib import Path

from ..core.universal_error_monitor import get_error_monitor
from ..plugins import example_policy  # ensure example plugin registers on import
from .commands_aaol import add_aaol_commands, handle_aaol_commands
from .commands_advanced_test_reporting import (
    add_advanced_test_reporting_commands,
    handle_advanced_test_reporting_commands,
)
from .commands_ai_agent import add_ai_agent_commands, handle_ai_agent_commands
from .commands_ai_agent_collaboration import (
    add_ai_agent_collaboration_parser,
    handle_ai_agent_collaboration_commands,
)
from .commands_api import add_api_commands, handle_api_commands
from .commands_background_agents import (
    add_background_agent_commands,
    handle_background_agent_commands,
)
from .commands_capability_tracking import (
    add_capability_tracking_commands,
    handle_capability_tracking_commands,
)
from .commands_continuous_improvement import (
    add_continuous_improvement_parser,
    handle_continuous_improvement_commands,
)
from .commands_core import add_core_commands, handle_core_commands
from .commands_cursor import add_cursor_commands, handle_cursor_commands
from .commands_decision_pipeline import (
    add_decision_pipeline_commands,
    handle_decision_pipeline_commands,
)
from .commands_enhanced_context import (
    add_enhanced_context_commands,
    handle_enhanced_context_commands,
)
from .commands_enhanced_testing import (
    add_enhanced_testing_commands,
    handle_enhanced_testing_commands,
)
from .commands_enhanced_vision import (
    add_enhanced_vision_parser,
    handle_enhanced_vision_commands,
)
from .commands_interrogate import add_interrogate_commands, handle_interrogate_commands
from .commands_kaizen import add_kaizen_commands, handle_kaizen_commands
from .commands_metrics import add_metrics_commands, handle_metrics_commands
from .commands_optimization_experiments import (
    add_optimization_experiment_commands,
    handle_optimization_experiment_commands,
)
from .commands_performance_trends import (
    add_performance_trend_commands,
    handle_performance_trend_commands,
)
from .commands_prompt import add_prompt_commands, handle_prompt_commands
from .commands_ui_enhanced import add_ui_enhanced_commands, handle_ui_enhanced_commands
from .commands_ux_enhancements import (
    add_ux_enhancement_commands,
    handle_ux_enhancement_commands,
)
from .ux_middleware import get_ux_middleware, with_ux_enhancements


def main(argv=None):
    """Main CLI entry point with refactored command structure."""
    p = argparse.ArgumentParser(
        prog="ai_onboard",
        description=(
            "AI Onboard: drop-in project coach "
            "(charter + plan + align + validate + kaizen + interrogate + prompt + ai-agent + aaol)"
        ),
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # Add core commands
    add_core_commands(sub)

    # Add interrogate commands
    add_interrogate_commands(sub)

    # Add prompt commands
    add_prompt_commands(sub)

    # Add AI agent commands
    add_ai_agent_commands(sub)

    # Add AAOL commands
    add_aaol_commands(sub)

    # Add enhanced vision commands
    add_enhanced_vision_parser(sub)

    # Add AI agent collaboration commands
    add_ai_agent_collaboration_parser(sub)

    # Add continuous improvement commands
    add_continuous_improvement_parser(sub)

    # Add metrics commands
    add_metrics_commands(sub)

    # Add Cursor AI integration commands
    add_cursor_commands(sub)

    # Add API server commands
    add_api_commands(sub)

    # Add enhanced conversation context commands
    add_enhanced_context_commands(sub)

    # Add advanced decision pipeline commands
    add_decision_pipeline_commands(sub)

    # Add Kaizen automation commands
    add_kaizen_commands(sub)

    # Add optimization experiment commands
    add_optimization_experiment_commands(sub)

    # Add UI-enhanced commands
    add_ui_enhanced_commands(sub)

    # Add UX enhancement commands
    add_ux_enhancement_commands(sub)

    # Add capability tracking commands
    add_capability_tracking_commands(sub)

    # Add background agent commands
    add_background_agent_commands(sub)

    # Add enhanced testing commands
    add_enhanced_testing_commands(sub)

    # Add performance trend commands
    add_performance_trend_commands(sub)

    # Add advanced test reporting commands
    add_advanced_test_reporting_commands(sub)

    # TODO: Add other domain commands as they're refactored
    # from .commands_vision import add_vision_commands, handle_vision_commands
    # from .commands_design import add_design_commands, handle_design_commands
    # from .commands_planning import add_planning_commands, handle_planning_commands
    # from .commands_debug import add_debug_commands, handle_debug_commands
    # from .commands_context import add_context_commands, handle_context_commands

    args = p.parse_args(argv)
    root = Path.cwd()

    # Fast path for simple commands - avoid heavy initialization
    if args.cmd in ["version", "help"]:
        # Handle these directly without middleware overhead
        if args.cmd == "version":
            try:
                from .. import __version__

                print(f"ai-onboard {__version__}")
            except ImportError:
                print("ai-onboard (version unknown)")
        elif args.cmd == "help":
            p.print_help()
        return

    # Initialize UX middleware only for interactive commands
    if args.cmd not in ["status"]:
        ux_middleware = get_ux_middleware(root)
        user_id = "default"  # Could be extracted from environment or config
        ux_middleware.show_welcome_message(user_id)
    else:
        ux_middleware = None

    # Initialize error monitor for command execution monitoring
    error_monitor = get_error_monitor(root)

    # Handle core commands with error monitoring
    if args.cmd in [
        "analyze",
        "charter",
        "plan",
        "align",
        "validate",
        "kaizen",
        "optimize",
        "version",
        "metrics",
        "cleanup",
        "gate",
    ]:
        with error_monitor.monitor_command_execution(
            args.cmd, "foreground", "cli_session"
        ):
            handle_core_commands(args, root)
        return

    # Handle interrogate commands with error monitoring
    if args.cmd == "interrogate":
        with error_monitor.monitor_command_execution(
            "interrogate", "foreground", "cli_session"
        ):
            if handle_interrogate_commands(args, root):
                return

    # Handle prompt commands with error monitoring
    if args.cmd == "prompt":
        with error_monitor.monitor_command_execution(
            "prompt", "foreground", "cli_session"
        ):
            if handle_prompt_commands(args, root):
                return

    # Handle AI agent commands with error monitoring
    if args.cmd == "ai-agent":
        with error_monitor.monitor_command_execution(
            "ai-agent", "foreground", "cli_session"
        ):
            if handle_ai_agent_commands(args, root):
                return

    # Handle AAOL commands with error monitoring
    if args.cmd == "aaol":
        with error_monitor.monitor_command_execution(
            "aaol", "foreground", "cli_session"
        ):
            if handle_aaol_commands(args, root):
                return

    # Handle enhanced vision commands with error monitoring
    if args.cmd == "enhanced-vision":
        with error_monitor.monitor_command_execution(
            "enhanced-vision", "foreground", "cli_session"
        ):
            handle_enhanced_vision_commands(args, root)
            return

    # Handle AI agent collaboration commands with error monitoring
    if args.cmd == "ai-collaboration":
        with error_monitor.monitor_command_execution(
            "ai-collaboration", "foreground", "cli_session"
        ):
            handle_ai_agent_collaboration_commands(args, root)
            return

    # Handle continuous improvement commands with error monitoring
    if args.cmd == "continuous-improvement":
        with error_monitor.monitor_command_execution(
            "continuous-improvement", "foreground", "cli_session"
        ):
            handle_continuous_improvement_commands(args, root)
            return

    # Handle user preference learning (quick-path) with error monitoring
    if args.cmd == "user-prefs":
        with error_monitor.monitor_command_execution(
            "user-prefs", "foreground", "cli_session"
        ):
            handle_continuous_improvement_commands(args, root)
            return

    # Handle unified metrics commands with error monitoring
    if args.cmd == "unified-metrics":
        with error_monitor.monitor_command_execution(
            "unified-metrics", "foreground", "cli_session"
        ):
            handle_metrics_commands(args, root)
            return

    # Handle Cursor AI integration commands with error monitoring
    if args.cmd == "cursor":
        with error_monitor.monitor_command_execution(
            "cursor", "foreground", "cli_session"
        ):
            handle_cursor_commands(args, root)
            return

    # Handle API server commands with error monitoring
    if args.cmd == "api":
        with error_monitor.monitor_command_execution(
            "api", "foreground", "cli_session"
        ):
            handle_api_commands(args, root)
            return

    # Handle enhanced conversation context commands with error monitoring
    if args.cmd == "enhanced-context":
        with error_monitor.monitor_command_execution(
            "enhanced-context", "foreground", "cli_session"
        ):
            handle_enhanced_context_commands(args, root)
            return

    # Handle advanced decision pipeline commands with error monitoring
    if args.cmd == "decision-pipeline":
        with error_monitor.monitor_command_execution(
            "decision-pipeline", "foreground", "cli_session"
        ):
            handle_decision_pipeline_commands(args, root)
            return

    # Handle Kaizen automation commands with error monitoring
    if args.cmd == "kaizen-auto":
        with error_monitor.monitor_command_execution(
            "kaizen-auto", "foreground", "cli_session"
        ):
            handle_kaizen_commands(args, root)
            return

    # Handle optimization experiment commands with error monitoring
    if args.cmd == "opt-experiments":
        with error_monitor.monitor_command_execution(
            "opt-experiments", "foreground", "cli_session"
        ):
            handle_optimization_experiment_commands(args, root)
            return

    # Handle UI-enhanced commands with error monitoring
    if args.cmd in [
        "help",
        "dashboard",
        "suggest",
        "discover",
        "config",
        "wizard",
        "status",
    ]:
        with error_monitor.monitor_command_execution(
            args.cmd, "foreground", "cli_session"
        ):
            handle_ui_enhanced_commands(args, root)
            return

    # Handle UX enhancement commands with error monitoring
    if args.cmd == "ux":
        with error_monitor.monitor_command_execution("ux", "foreground", "cli_session"):
            handle_ux_enhancement_commands(args, root)
            return

    # Handle capability tracking commands with error monitoring
    if args.cmd == "capability-tracking":
        with error_monitor.monitor_command_execution(
            "capability-tracking", "foreground", "cli_session"
        ):
            handle_capability_tracking_commands(args, root)
            return

    # Handle enhanced testing commands with error monitoring
    if args.cmd == "enhanced-testing":
        with error_monitor.monitor_command_execution(
            "enhanced-testing", "foreground", "cli_session"
        ):
            handle_enhanced_testing_commands(args, root)
            return

    # Handle performance trend commands with error monitoring
    if args.cmd == "perf-trends":
        with error_monitor.monitor_command_execution(
            "perf-trends", "foreground", "cli_session"
        ):
            handle_performance_trend_commands(args, root)
            return

    # Handle advanced test reporting commands with error monitoring
    if args.cmd == "test-reports":
        with error_monitor.monitor_command_execution(
            "test-reports", "foreground", "cli_session"
        ):
            handle_advanced_test_reporting_commands(args, root)
            return

    # Handle background agent commands with error monitoring
    if args.cmd == "background-agents":
        with error_monitor.monitor_command_execution(
            "background-agents", "foreground", "cli_session"
        ):
            handle_background_agent_commands(args, root)
            return

    # TODO: Handle other domain commands as they're refactored
    # elif args.cmd in ["vision", "design", "planning", "debug", "context"]:
    #     handle_vision_commands(args, root)
    #     return

    # Fallback for unimplemented commands
    print(f"Command '{args.cmd}' not yet implemented in refactored CLI.")
    print("Please use the original commands.py for now.")

    # Show completion celebration for milestones
    # Only show completion celebration for interactive commands
    if ux_middleware is not None:
        ux_middleware.show_completion_celebration(user_id)


if __name__ == "__main__":
    main()
