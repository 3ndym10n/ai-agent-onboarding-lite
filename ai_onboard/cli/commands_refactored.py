"""Refactored main CLI entry point for ai-onboard."""

import argparse
from pathlib import Path
from .commands_core import add_core_commands, handle_core_commands
from .commands_interrogate import add_interrogate_commands, handle_interrogate_commands
from .commands_prompt import add_prompt_commands, handle_prompt_commands
from .commands_ai_agent import add_ai_agent_commands, handle_ai_agent_commands
from ..plugins import example_policy  # ensure example plugin registers on import


def main(argv=None):
    """Main CLI entry point with refactored command structure."""
    p = argparse.ArgumentParser(
        prog="ai_onboard",
        description=(
            "AI Onboard: drop-in project coach "
            "(charter + plan + align + validate + kaizen + interrogate + prompt + ai-agent)"
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
    
    # TODO: Add other domain commands as they're refactored
    # from .commands_vision import add_vision_commands, handle_vision_commands
    # from .commands_design import add_design_commands, handle_design_commands
    # from .commands_planning import add_planning_commands, handle_planning_commands
    # from .commands_debug import add_debug_commands, handle_debug_commands
    # from .commands_context import add_context_commands, handle_context_commands

    args = p.parse_args(argv)
    root = Path.cwd()

    # Handle core commands
    if args.cmd in ["analyze", "charter", "plan", "align", "validate", "kaizen", "optimize", "version", "metrics", "cleanup"]:
        handle_core_commands(args, root)
        return

    # Handle interrogate commands
    if args.cmd == "interrogate":
        if handle_interrogate_commands(args, root):
            return

    # Handle prompt commands
    if args.cmd == "prompt":
        if handle_prompt_commands(args, root):
            return

    # Handle AI agent commands
    if args.cmd == "ai-agent":
        if handle_ai_agent_commands(args, root):
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
