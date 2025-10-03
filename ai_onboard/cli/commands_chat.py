"""
Chat interface for natural language interaction with ai-onboard.

This module provides a conversational interface for vibe coders who want to
describe what they want in plain English, rather than using CLI commands.
"""

from pathlib import Path
from typing import Any, Dict, List

from ..core.ai_integration.prompt_based_intent_parser import (
    get_prompt_based_intent_parser,
)


def add_chat_commands(subparsers):
    """Add chat command parser."""
    chat_parser = subparsers.add_parser(
        "chat",
        help="Chat with AI Onboard in natural language",
        description="Have a natural conversation to describe what you want to build",
    )

    chat_parser.add_argument(
        "message",
        nargs="*",
        help="Your message to the AI (or omit for interactive mode)",
    )

    chat_parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Start interactive chat session",
    )

    chat_parser.add_argument(
        "--context",
        action="store_true",
        help="Show current project context",
    )


def handle_chat_commands(args, root: Path):
    """Handle chat command execution."""

    if args.context:
        _show_project_context(root)
        return

    # Check if we have a message or should go interactive
    if args.interactive or not args.message:
        _run_interactive_chat(root)
    else:
        # Single message mode
        message = " ".join(args.message)
        _process_single_message(root, message)


def _show_project_context(root: Path):
    """Show current project context."""
    from ..core.base import state
    from ..core.base.utils import read_json

    print("\n📊 **Current Project Context**\n")

    # Check for charter
    charter_path = root / ".ai_onboard" / "charter.json"
    if charter_path.exists():
        charter = read_json(charter_path)
        print(f"✅ **Charter**: {charter.get('name', 'Untitled Project')}")
        if "description" in charter:
            print(f"   📝 {charter['description'][:100]}...")
    else:
        print(
            "❌ **No Charter** - Run `ai_onboard charter` or "
            "tell me what you want to build"
        )

    # Check for plan
    plan_path = root / ".ai_onboard" / "plan.json"
    if plan_path.exists():
        plan = read_json(plan_path)
        tasks = plan.get("tasks", [])
        print(f"✅ **Plan**: {len(tasks)} tasks defined")
    else:
        print("❌ **No Plan** - I can help you create one")

    # Check state
    current_state = state.load(root)
    phase = current_state.get("phase", "unknown")
    print(f"📍 **Current Phase**: {phase}")

    print("\n💬 Ready to chat! Tell me what you'd like to do.\n")


def _run_interactive_chat(root: Path):
    """Run interactive chat session."""
    print("\n🤖 **AI Onboard Chat**")
    print("━" * 60)
    print("Hi! I'm here to help you build your project.")
    print("Tell me what you want to build, and I'll guide you through it.")
    print("\n**Commands:**")
    print("  • 'exit' or 'quit' - End the conversation")
    print("  • 'context' - See your current project status")
    print("  • 'gate' - Check for active gates")
    print("  • 'respond: <answer>' - Respond to active gate")
    print("━" * 60)
    print()

    # Show context first
    _show_project_context(root)

    # Check for active gates on startup (quiet check)
    last_gate_check = _check_and_display_gate(root, silent=True)

    # Get intent parser
    parser = get_prompt_based_intent_parser(root)

    # Chat loop
    while True:
        try:
            # Check for NEW gates (only notify if gate status changed)
            current_gate_status = _gate_exists(root)
            if current_gate_status and not last_gate_check:
                # New gate appeared!
                print("\n⚠️  **NEW GATE DETECTED** - An AI agent needs your input!")
                _check_and_display_gate(root, force=True)
            last_gate_check = current_gate_status

            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Check for special commands
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n👋 Goodbye! Your project is saved. Come back anytime!\n")
                break

            if user_input.lower() == "context":
                _show_project_context(root)
                continue

            if user_input.lower() == "gate":
                _check_and_display_gate(root, force=True)
                continue

            # Direct gate response command
            if user_input.lower().startswith(
                "respond:"
            ) or user_input.lower().startswith("answer:"):
                # Extract response after colon
                response_text = user_input.split(":", 1)[1].strip()
                if _submit_gate_response_direct(root, response_text):
                    continue

            # Check if there's an active gate and user might be responding
            if current_gate_status and not user_input.lower().startswith(
                ("i want", "create", "build", "show")
            ):
                # Might be a gate response - offer to submit it
                if _offer_gate_response(root, user_input):
                    # Response submitted, continue
                    continue

            # Process the message
            print()  # Blank line before response
            _process_single_message(root, user_input)
            print()  # Blank line after response

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Your project is saved. Come back anytime!\n")
            break
        except Exception as e:
            print(f"\n❌ Oops, something went wrong: {e}")
            print("Let's try again...\n")


def _process_single_message(root: Path, message: str):
    """Process a single chat message."""
    # Get intent parser
    parser = get_prompt_based_intent_parser(root)

    # Parse intent from message
    intent_result = parser.parse_user_intent(message)

    print(f"🤖 **AI**: ", end="")

    # Route based on intent result
    intent_dict = intent_result.interpreted_intent
    intent_type = intent_dict.get("primary_action", "unknown")
    confidence = intent_result.confidence_score

    if confidence < 0.3:
        # Low confidence - ask for clarification
        print("I'm not sure I understand. Could you rephrase that?")
        print("\nHere are some things I can help with:")
        print("  • 'Create a charter for a todo app'")
        print("  • 'Generate a plan for my project'")
        print("  • 'Show me the next task to work on'")
        print("  • 'Validate my progress'")
        return

    # High-level routing
    if intent_type in ["create_charter", "describe_project", "charter"]:
        _handle_charter_intent(root, message, intent_dict)
    elif intent_type in ["create_plan", "plan_project", "plan"]:
        _handle_plan_intent(root, message, intent_dict)
    elif intent_type in ["show_progress", "status"]:
        _handle_status_intent(root, message, intent_dict)
    elif intent_type in ["next_task", "what_next"]:
        _handle_next_task_intent(root, message, intent_dict)
    elif intent_type == "validate":
        _handle_validate_intent(root, message, intent_dict)
    else:
        # Generic response - try to help
        print(f"I heard you want to: {message}")
        print("\nLet me see what I can do...")
        _suggest_next_steps(root)


def _handle_charter_intent(root: Path, message: str, intent_dict: Dict[str, Any]):
    """Handle charter creation intent with enforced decisions."""
    print("Great! Let's create a charter for your project.\n")

    # Check if charter already exists
    charter_path = root / ".ai_onboard" / "charter.json"
    if charter_path.exists():
        print("📝 You already have a charter. Would you like to update it?")
        print("   (Run `ai_onboard charter --interactive` to update)")
        return

    # Use enforcer to get project type if not specified
    from ..core.ai_integration.decision_enforcer import (
        DecisionPoint,
        get_decision_enforcer,
        register_common_decisions,
    )

    enforcer = get_decision_enforcer(root)
    register_common_decisions(enforcer)

    # Determine project type
    project_type = intent_dict.get("project_type")

    if not project_type:
        # Create project type decision
        project_type_decision = DecisionPoint(
            name="project_type",
            question="What type of project do you want to build?",
            options={
                "web_app": "Web Application - Interactive website",
                "api": "API/Backend - REST or GraphQL API",
                "cli": "CLI Tool - Command-line application",
                "library": "Library/Package - Reusable code",
                "mobile": "Mobile App - iOS/Android application",
            },
        )
        enforcer.register_decision(project_type_decision)

        result = enforcer.enforce_decision(
            decision_name="project_type",
            context={"user_message": message},
            agent_id="chat_assistant",
        )

        if result.proceed and result.response:
            user_responses = result.response.get("user_responses", ["web_app"])
            project_type = user_responses[0] if user_responses else "web_app"
        else:
            project_type = "web_app"

    print(f"✅ Project type: {project_type}\n")
    print("To create a comprehensive charter, run:")
    print(f"   `ai_onboard charter --interrogate`")
    print("\nThis will guide you through detailed questions about your project.")


def _handle_plan_intent(root: Path, message: str, intent_dict: Dict[str, Any]):
    """Handle plan creation intent."""
    from ..core.base.utils import read_json

    # Check for charter first
    charter_path = root / ".ai_onboard" / "charter.json"
    if not charter_path.exists():
        print("I need a charter first before creating a plan.")
        print("Tell me what you want to build, and I'll help create one!")
        return

    print("Perfect! Let me create a plan for your project...\n")

    # Import and run planning
    from ..core.vision.planning import build as planning_build

    try:
        planning_build(root, analyze_codebase=None)  # Auto-detect

        # Load the plan and summarize
        plan_path = root / ".ai_onboard" / "plan.json"
        plan = read_json(plan_path)

        tasks = plan.get("tasks", [])
        milestones = plan.get("milestones", [])

        print(f"✅ **Plan Created!**\n")
        print(f"   📋 {len(tasks)} tasks defined")
        print(f"   🎯 {len(milestones)} milestones")

        if milestones:
            print(f"\n**First Milestone**: {milestones[0].get('name', 'Unknown')}")

        if tasks:
            pending_tasks = [t for t in tasks if t.get("status") == "pending"]
            if pending_tasks:
                print(f"\n**Next Task**: {pending_tasks[0].get('name', 'Unknown')}")

        print(f"\n💾 Plan saved to: {plan_path}")

    except Exception as e:
        print(f"❌ Error creating plan: {e}")
        print("Let's try debugging this together...")


def _handle_status_intent(root: Path, message: str, intent_dict: Dict[str, Any]):
    """Handle status check intent."""
    _show_project_context(root)


def _handle_next_task_intent(root: Path, message: str, intent_dict: Dict[str, Any]):
    """Handle next task request."""
    from ..core.base.utils import read_json

    plan_path = root / ".ai_onboard" / "plan.json"
    if not plan_path.exists():
        print("I don't have a plan yet. Let's create one!")
        print("Tell me what you want to build.")
        return

    plan = read_json(plan_path)
    tasks = plan.get("tasks", [])

    # Find next pending task
    next_task = None
    for task in tasks:
        if task.get("status") == "pending":
            next_task = task
            break

    if next_task:
        print(f"**Next up**: {next_task.get('name', 'Unknown task')}\n")
        if "description" in next_task:
            print(f"📝 {next_task['description']}\n")
        if "dependencies" in next_task:
            print(f"⚠️  **Dependencies**: {', '.join(next_task['dependencies'])}")
    else:
        print("🎉 All tasks are done! Congratulations!")


def _handle_validate_intent(root: Path, message: str, intent_dict: Dict[str, Any]):
    """Handle validation request."""
    print("Let me check your project...\n")

    # Run validation
    from ..core.base.validation_runtime import validate_all  # type: ignore

    try:
        errors: List[str] = []
        warnings: List[str] = []

        validate_all(root, errors, warnings)

        if not errors and not warnings:
            print("✅ **Everything looks good!**")
        else:
            if errors:
                print(f"❌ **{len(errors)} error(s) found:**")
                for err in errors[:3]:  # Show first 3
                    print(f"   • {err}")
            if warnings:
                print(f"⚠️  **{len(warnings)} warning(s):**")
                for warn in warnings[:3]:  # Show first 3
                    print(f"   • {warn}")

    except Exception as e:
        print(f"❌ Validation failed: {e}")


def _suggest_next_steps(root: Path):
    """Suggest next steps based on current state."""
    charter_path = root / ".ai_onboard" / "charter.json"
    plan_path = root / ".ai_onboard" / "plan.json"

    print("\n**Here's what I suggest:**\n")

    if not charter_path.exists():
        print("1. Tell me what you want to build so I can create a charter")
        print("   Example: 'I want to build a todo app'")
    elif not plan_path.exists():
        print("1. Let's create a plan for your project")
        print("   Say: 'Create a plan' or run `ai_onboard plan`")
    else:
        print("1. Check your next task: Say 'What's next?'")
        print("2. Validate your progress: Say 'Validate'")
        print("3. See your project status: Say 'Status'")


def _submit_gate_response_direct(
    root: Path, response_text: str, decision: str = "proceed"
) -> bool:
    """
    Submit a gate response directly without prompts.

    Args:
        root: Project root directory
        response_text: User's response text
        decision: User decision (proceed/modify/stop)

    Returns:
        True if response was submitted, False otherwise
    """
    import json
    import time

    gates_dir = root / ".ai_onboard" / "gates"
    response_file = gates_dir / "gate_response.json"

    # Check if there's an active gate
    if not _gate_exists(root):
        print("\n❌ No active gate to respond to.")
        print("   Type 'gate' to check for gates.\n")
        return False

    # Create response JSON
    response = {
        "user_responses": [response_text],
        "user_decision": decision,
        "additional_context": f"Direct response via chat: {response_text}",
        "timestamp": time.time(),
    }

    # Write response file
    try:
        response_file.write_text(json.dumps(response, indent=2), encoding="utf-8")
        print("\n✅ **Response Submitted!**")
        print(f'   Your response: "{response_text}"')
        print(f"   Decision: {decision}")
        print(f"   The AI agent will now continue with your guidance.")
        print()
        return True
    except Exception as e:
        print(f"\n❌ Failed to submit response: {e}\n")
        return False


def _offer_gate_response(root: Path, user_input: str) -> bool:
    """
    Offer to submit user input as a gate response.

    Args:
        root: Project root directory
        user_input: User's input that might be a gate response

    Returns:
        True if response was submitted, False otherwise
    """
    import json
    import time

    gates_dir = root / ".ai_onboard" / "gates"
    response_file = gates_dir / "gate_response.json"

    # Ask user if this is a gate response
    print(f"\n💡 I see there's an active gate. Is this your response to it?")
    print(f'   Your input: "{user_input}"')
    print(f"\n   Options:")
    print(f"   • 'yes' or 'y' - Submit this as gate response")
    print(f"   • 'no' or 'n' - Process as normal chat message")

    confirmation = input("\nSubmit as gate response? (y/n): ").strip().lower()

    if confirmation not in ["y", "yes"]:
        return False

    # Get user decision
    print("\nHow should the AI agent proceed?")
    print("  1) proceed - Continue with my response")
    print("  2) modify - I want to provide more details")
    print("  3) stop - Stop and don't proceed")

    decision_input = (
        input("\nYour choice (1/2/3 or proceed/modify/stop): ").strip().lower()
    )

    # Map input to decision
    decision_map = {
        "1": "proceed",
        "2": "modify",
        "3": "stop",
        "proceed": "proceed",
        "modify": "modify",
        "stop": "stop",
        "p": "proceed",
        "m": "modify",
        "s": "stop",
    }

    user_decision = decision_map.get(decision_input, "proceed")

    # Ask for additional context
    print("\nAny additional context for the AI agent? (press Enter to skip)")
    additional_context = input("Additional context: ").strip()

    # Create response JSON
    response = {
        "user_responses": [user_input],
        "user_decision": user_decision,
        "additional_context": additional_context or f"Response via chat: {user_input}",
        "timestamp": time.time(),
    }

    # Write response file
    try:
        response_file.write_text(json.dumps(response, indent=2), encoding="utf-8")
        print("\n✅ **Response Submitted!**")
        print(f"   Decision: {user_decision}")
        print(f"   The AI agent will now continue with your guidance.")
        print()
        return True
    except Exception as e:
        print(f"\n❌ Failed to submit response: {e}")
        print("You can try again or respond manually.")
        print()
        return False


def _gate_exists(root: Path) -> bool:
    """Quick check if a gate file exists (lightweight)."""
    gates_dir = root / ".ai_onboard" / "gates"
    current_gate_file = gates_dir / "current_gate.md"
    status_file = gates_dir / "gate_status.json"

    if not current_gate_file.exists():
        return False

    # Check if gate is actually active
    if status_file.exists():
        try:
            import json

            status = json.loads(status_file.read_text(encoding="utf-8"))
            return bool(status.get("gate_active", False))
        except Exception:
            pass

    return False


def _check_and_display_gate(
    root: Path, force: bool = False, silent: bool = False
) -> bool:
    """
    Check for active gates and display them in chat.

    Args:
        root: Project root directory
        force: If True, always display gate info even if none active
        silent: If True, just check without displaying anything

    Returns:
        True if a gate is active, False otherwise
    """
    gates_dir = root / ".ai_onboard" / "gates"
    current_gate_file = gates_dir / "current_gate.md"
    status_file = gates_dir / "gate_status.json"

    # Check if gate exists
    if not current_gate_file.exists():
        if force and not silent:
            print("\n✅ **No Active Gates**")
            print("No AI agent is currently waiting for your input.\n")
        return False

    # Check if gate is actually active
    gate_active = False
    if status_file.exists():
        try:
            import json

            status = json.loads(status_file.read_text(encoding="utf-8"))
            gate_active = status.get("gate_active", False)
        except Exception:
            pass

    if not gate_active and not force:
        return False

    # If silent mode, just return status
    if silent:
        return gate_active

    # Read and parse the gate
    try:
        gate_content = current_gate_file.read_text(encoding="utf-8")

        # Display gate in user-friendly format
        print("\n" + "━" * 60)
        print("🚪 **AI AGENT NEEDS YOUR INPUT**")
        print("━" * 60)

        # Parse gate content to extract key information
        lines = gate_content.split("\n")
        in_questions = False
        in_context = False

        for line in lines:
            if "# Gate:" in line or "## Gate:" in line:
                # Extract gate title
                title = line.replace("#", "").replace("Gate:", "").strip()
                print(f"\n📋 **{title}**\n")
            elif "Questions for User:" in line or "## Questions" in line:
                in_questions = True
                print("**Questions:**")
                continue
            elif "Context:" in line or "## Context" in line:
                in_context = True
                in_questions = False
                print("\n**Context:**")
                continue
            elif line.startswith("##") or line.startswith("---"):
                in_questions = False
                in_context = False
                continue

            # Display questions and context
            if in_questions and line.strip():
                if line.strip().startswith("-") or line.strip().startswith("*"):
                    print(f"  {line.strip()}")
                elif line.strip() and not line.strip().startswith("#"):
                    print(f"  {line.strip()}")
            elif in_context and line.strip():
                if not line.strip().startswith("#"):
                    print(f"  {line.strip()}")

        print("\n" + "━" * 60)
        print("💡 **How to Respond:**")
        print("   The AI agent will read this gate and ask you these questions.")
        print("   Answer them in chat, and the agent will continue working.")
        print("━" * 60 + "\n")

        return True

    except Exception as e:
        if force:
            print(f"\n❌ Error reading gate: {e}\n")
        return False
