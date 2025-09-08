"""Refactored main CLI entry point for ai-onboard."""

import argparse
from pathlib import Path

from ..core.universal_error_monitor import get_error_monitor
from ..plugins import example_policy  # ensure example plugin registers on import
from .commands_aaol import add_aaol_commands, handle_aaol_commands
from .commands_ai_agent import add_ai_agent_commands, handle_ai_agent_commands
from .commands_ai_agent_collaboration import (
    add_ai_agent_collaboration_parser,
    handle_ai_agent_collaboration_commands,
)
from .commands_core import add_core_commands, handle_core_commands
from .commands_enhanced_vision import (
    add_enhanced_vision_parser,
    handle_enhanced_vision_commands,
)
from .commands_interrogate import add_interrogate_commands, handle_interrogate_commands
from .commands_prompt import add_prompt_commands, handle_prompt_commands


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

    # TODO: Add other domain commands as they're refactored
    # from .commands_vision import add_vision_commands, handle_vision_commands
    # from .commands_design import add_design_commands, handle_design_commands
    # from .commands_planning import add_planning_commands, handle_planning_commands
    # from .commands_debug import add_debug_commands, handle_debug_commands
    # from .commands_context import add_context_commands, handle_context_commands

    args = p.parse_args(argv)
    root = Path.cwd()

    # Initialize error monitor
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

    # TODO: Handle other domain commands as they're refactored
    # elif args.cmd in ["vision", "design", "planning", "debug", "context"]:
    #     handle_vision_commands(args, root)
    #     return

    # Fallback for unimplemented commands
    print(f"Command '{args.cmd}' not yet implemented in refactored CLI.")
    print("Please use the original commands.py for now.")


if __name__ == "__main__":
    main()
