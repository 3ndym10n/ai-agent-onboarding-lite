"""Interrogate commands for ai-onboard CLI."""

import argparse
import json
from pathlib import Path
from ..core import vision_interrogator, prompt_bridge


def add_interrogate_commands(subparsers):
    """Add interrogate command parsers."""
    
    s_interrogate = subparsers.add_parser("interrogate", help="Vision interrogation system")
    si_sub = s_interrogate.add_subparsers(dest="interrogate_cmd", required=True)
    
    si_sub.add_parser("check", help="Check if vision is ready for AI agents")
    si_sub.add_parser("start", help="Start vision interrogation process")
    
    submit_parser = si_sub.add_parser("submit", help="Submit response to interrogation question")
    submit_parser.add_argument("--phase", help="Interrogation phase")
    submit_parser.add_argument("--question-id", help="Question ID")
    submit_parser.add_argument("--response", help="Response data (JSON)")
    
    si_sub.add_parser("questions", help="Get current interrogation questions")
    si_sub.add_parser("summary", help="Get interrogation summary")
    si_sub.add_parser("force-complete", help="Force complete interrogation (use with caution)")


def handle_interrogate_commands(args, root: Path):
    """Handle interrogate command execution."""
    
    if args.cmd != "interrogate":
        return False
    
    icmd = getattr(args, "interrogate_cmd", None)
    if not icmd:
        print("{\"error\":\"no interrogate subcommand specified\"}")
        return True
    
    # Initialize interrogator
    interrogator = vision_interrogator.VisionInterrogator(root)
    
    if icmd == "check":
        # Check if vision is ready
        result = interrogator.check_vision_readiness()
        print(prompt_bridge.dumps_json(result))
        return True
    elif icmd == "start":
        # Start interrogation
        result = interrogator.start_interrogation()
        print(prompt_bridge.dumps_json(result))
        return True
    elif icmd == "submit":
        # Submit response
        phase = getattr(args, 'phase', None)
        question_id = getattr(args, 'question_id', None)
        response_data = getattr(args, 'response', None)
        
        if not all([phase, question_id, response_data]):
            print("{\"error\":\"missing required arguments: phase, question-id, and response are required\"}")
            return True
        
        try:
            # Try to parse as JSON first
            try:
                response = json.loads(response_data)
            except json.JSONDecodeError:
                # If JSON fails, treat as plain text
                response = {"answer": response_data}
            
            result = interrogator.submit_response(phase, question_id, response)
            print(prompt_bridge.dumps_json(result))
        except Exception as e:
            print(f"{{\"error\":\"failed to submit response: {str(e)}\"}}")
        return True
    elif icmd == "questions":
        # Get current questions
        result = interrogator.get_current_questions()
        print(prompt_bridge.dumps_json(result))
        return True
    elif icmd == "summary":
        # Get interrogation summary
        result = interrogator.get_interrogation_summary()
        print(prompt_bridge.dumps_json(result))
        return True
    elif icmd == "force-complete":
        # Force complete interrogation
        result = interrogator.force_complete_interrogation()
        print(prompt_bridge.dumps_json(result))
        return True
    
    print("{\"error\":\"unknown interrogate subcommand\"}")
    return True
