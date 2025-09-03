"""Prompt commands for ai-onboard CLI."""

import argparse
from pathlib import Path
from ..core import prompt_bridge


def add_prompt_commands(subparsers):
    """Add prompt command parsers."""
    
    s_prompt = subparsers.add_parser("prompt", help="Prompt management and generation")
    sp_sub = s_prompt.add_subparsers(dest="prompt_cmd", required=True)
    
    summary_parser = sp_sub.add_parser("summary", help="Generate project summary")
    summary_parser.add_argument("--level", choices=["brief", "detailed", "comprehensive"], default="brief", help="Summary detail level")


def handle_prompt_commands(args, root: Path):
    """Handle prompt command execution."""
    
    if args.cmd != "prompt":
        return False
    
    pcmd = getattr(args, "prompt_cmd", None)
    if not pcmd:
        print("{\"error\":\"no prompt subcommand specified\"}")
        return True
    
    if pcmd == "summary":
        # Generate project summary
        level = getattr(args, 'level', 'brief')
        try:
            result = prompt_bridge.summary(root, level)
            print(prompt_bridge.dumps_json(result))
        except Exception as e:
            print(f"{{\"error\":\"failed to generate summary: {str(e)}\"}}")
        return True
    
    print("{\"error\":\"unknown prompt subcommand\"}")
    return True
