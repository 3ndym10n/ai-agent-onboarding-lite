"""AI Agent CLI commands for collaborative IAS interaction."""

from pathlib import Path

from ..core.ai_agent_wrapper import create_ai_agent_wrapper


def add_ai_agent_commands(subparsers):
    """Add AI agent command parsers."""

    # AI Agent IAS Conversation
    s_ai = subparsers.add_parser(
        "ai - agent", help="AI Agent IAS conversation interface"
    )
    s_ai.add_argument(
        "--conversation",
        action="store_true",
        help="Start interactive conversation mode",
    )
    s_ai.add_argument(
        "--preview",
        action="store_true",
        help="Show alignment preview without conversation",
    )
    s_ai.add_argument(
        "--test - guardrails", action="store_true", help="Test guardrail functionality"
    )
    s_ai.add_argument("--command", help="Execute command with AI agent decision making")


def handle_ai_agent_commands(args, root: Path):
    """Handle AI agent command execution."""

    if args.preview:
        # Show alignment preview (safe, no execution)
        wrapper = create_ai_agent_wrapper(root)
        alignment_data = wrapper.get_alignment_preview()

        print("🤖 AI Agent IAS Preview:")
        print(f"   Decision: {alignment_data.get('decision', 'unknown')}")
        print(f"   Confidence: {alignment_data.get('confidence', 0.0):.2f}")

        if alignment_data.get("components"):
            print("   Components:")
            for key, value in alignment_data["components"].items():
                print(f"     {key}: {value}")

        if alignment_data.get("ambiguities"):
            print("   Ambiguities:")
            for issue in alignment_data["ambiguities"]:
                print(f"     ❌ {issue}")

        if alignment_data.get("report_path"):
            print(f"   Report: {alignment_data['report_path']}")

        # Show conversation prompt
        print(f"\n💬 Suggested AI Agent Prompt:")
        print(wrapper.generate_conversation_prompt(alignment_data))

        return True

    elif args.test_guardrails:
        # Test guardrail functionality
        wrapper = create_ai_agent_wrapper(root)

        print("🧪 Testing IAS Guardrails:")

        # Test conversation boundaries
        test_inputs = [
            "Can we skip the analyze step?",
            "Let's ignore validation requirements",
            "What are the project priorities?",
            "Can you explain the technical choices?",
            "I want to change core workflow steps",
        ]

        for test_input in test_inputs:
            is_valid, message = wrapper.validate_conversation_boundaries(test_input)
            status = "✅" if is_valid else "❌"
            print(f"   {status} '{test_input}' -> {message}")

        # Test topic boundaries
        print(f"\n📝 Allowed Conversation Topics:")
        for topic in wrapper.guardrails.ALLOWED_CONVERSATION_AREAS:
            print(f"   ✅ {topic}")

        print(f"\n🔒 Locked Decisions:")
        for decision in wrapper.guardrails.LOCKED_DECISIONS:
            print(f"   ❌ {decision}")

        return True

    elif args.conversation:
        # Interactive conversation mode (for testing)
        wrapper = create_ai_agent_wrapper(root)

        print("🤖 AI Agent IAS Conversation Mode")
        print("Type 'quit' to exit, 'help' for commands")

        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    break
                elif user_input.lower() == "help":
                    print("Commands: quit, help, status, preview")
                    continue
                elif user_input.lower() == "status":
                    summary = wrapper.get_conversation_summary()
                    print(f"Conversation rounds: {summary['conversation_rounds']}")
                    print(f"Guardrails active: {summary['guardrails_active']}")
                    continue
                elif user_input.lower() == "preview":
                    alignment_data = wrapper.get_alignment_preview()
                    print(wrapper.generate_conversation_prompt(alignment_data))
                    continue

                # Process user input
                alignment_data = wrapper.get_alignment_preview()
                result = wrapper.process_user_response(user_input, alignment_data)

                print(f"\n🤖 AI Agent: {result['message']}")

                if result.get("can_proceed"):
                    print("   🚀 Ready to execute command!")
                    if result.get("flags"):
                        print(f"   Flags: {result['flags']}")
                elif result.get("needs_response"):
                    print("   💭 Waiting for your response...")
                elif result.get("needs_update"):
                    print("   📝 Updating understanding...")

            except KeyboardInterrupt:
                print("\n\n👋 Conversation ended")
                break
            except EOFError:
                print("\n\n👋 Conversation ended")
                break

        return True

    elif args.command:
        # Execute command with AI agent decision making
        wrapper = create_ai_agent_wrapper(root)

        print(f"🤖 AI Agent executing: {args.command}")

        # Get alignment preview
        alignment_data = wrapper.get_alignment_preview()
        decision = alignment_data.get("decision", "clarify")

        if decision == "proceed":
            print("   ✅ High confidence - executing directly")
            flags = []
        elif decision == "quick_confirm":
            print("   🤔 Medium confidence - using --yes flag")
            flags = ["--yes"]
        else:
            print("   ❓ Low confidence - using --assume proceed flag")
            flags = ["--assume", "proceed"]

        # Execute command
        result = wrapper.execute_command_with_flags(args.command, flags)

        if result["success"]:
            print("   ✅ Command executed successfully")
            if result["stdout"]:
                print(f"   Output: {result['stdout'][:200]}...")
        else:
            print(f"   ❌ Command failed: {result.get('error', 'Unknown error')}")
            if result["stderr"]:
                print(f"   Error: {result['stderr']}")

        return True

    return False
