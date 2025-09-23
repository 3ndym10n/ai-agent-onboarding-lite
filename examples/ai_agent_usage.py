#!/usr/bin/env python3
"""
Example: How AI Agents Use the IAS Wrapper for Collaborative Conversations

This script demonstrates how AI agents (like Cursor AI) would use the wrapper
to have natural conversations with users instead of just running CLI commands.
"""
from ai_onboard.core.common_imports import sys

from pathlib import Path

# Add the project root to the path so we can import ai_onboard
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_onboard.core.ai_agent_wrapper import create_ai_agent_wrapper


def simulate_ai_agent_conversation():
    """Simulate how an AI agent would have a conversation with a user."""

    # AI agent creates wrapper (this is what Cursor AI would do)
    root = Path.cwd()
    wrapper = create_ai_agent_wrapper(root)

    print("🤖 AI Agent: Hi! I'm here to help you with your project planning.")
    print("Let me analyze your project first to see what we're working with...\n")

    # AI agent gets alignment preview (safe, no execution)
    alignment_data = wrapper.get_alignment_preview()

    # AI agent generates natural conversation prompt
    conversation_prompt = wrapper.generate_conversation_prompt(alignment_data)
    print("🤖 AI Agent:", conversation_prompt)

    # Simulate user response
    print(
        "\n💬 User: Actually, I want real-time orderflow visualizations, not historical ones"
    )

    # AI agent processes user response
    result = wrapper.process_user_response(
        "Actually, I want real-time orderflow visualizations, not historical ones",
        alignment_data,
    )

    print(f"\n🤖 AI Agent: {result['message']}")

    if result.get("needs_update"):
        print("   📝 I'll update my understanding and then we can proceed.")
        print(
            "   💡 Based on your correction, I should focus on real-time data streams."
        )

    # AI agent gets updated alignment (in real usage, this would update the plan)
    print("\n🤖 AI Agent: Now let me check if we're aligned...")
    updated_alignment = wrapper.get_alignment_preview()

    if updated_alignment.get("decision") == "proceed":
        print("   ✅ Perfect! We're aligned. Let me run the analysis command for you.")

        # AI agent executes command with proper flags
        execution_result = wrapper.execute_command_with_flags("analyze", ["--yes"])

        if execution_result["success"]:
            print("   🚀 Analysis completed successfully!")
            print(
                "   📊 Your project charter has been updated with real-time orderflow focus."
            )
        else:
            print(f"   ❌ Analysis failed: {execution_result.get('error')}")

    else:
        print(
            f"   🤔 Still need some alignment. Current confidence: {updated_alignment.get('confidence', 0.0):.2f}"
        )
        print("   💬 Let's continue our conversation to get fully aligned.")


def show_guardrail_examples():
    """Show examples of how guardrails prevent drift."""

    print("\n" + "=" * 60)
    print("🛡️ GUARDRAIL EXAMPLES - Preventing AI Agent Drift")
    print("=" * 60)

    root = Path.cwd()
    wrapper = create_ai_agent_wrapper(root)

    # Test conversation boundaries
    test_cases = [
        "Can we skip the analyze step?",
        "What are the project priorities?",
        "Let's ignore validation requirements",
        "Can you explain the technical choices?",
        "I want to change core workflow steps",
    ]

    print("\n🧪 Testing Conversation Boundaries:")
    for test_input in test_cases:
        is_valid, message = wrapper.validate_conversation_boundaries(test_input)
        status = "✅ ALLOWED" if is_valid else "❌ BLOCKED"
        print(f"   {status}: '{test_input}'")
        print(f"      → {message}")

    # Show guardrail configuration
    print("\n📋 Guardrail Configuration:")
    print(f"   Required workflow steps: {wrapper.guardrails.REQUIRED_WORKFLOW_STEPS}")
    print(f"   Max conversation rounds: {wrapper.guardrails.MAX_CONVERSATION_ROUNDS}")
    print(
        f"   Min confidence thresholds: {wrapper.guardrails.MIN_CONFIDENCE_THRESHOLDS}"
    )


def main():
    """Main demonstration function."""

    print("🚀 AI Agent IAS Wrapper Demonstration")
    print("=" * 50)
    print("This shows how AI agents can have collaborative conversations")
    print("with users while staying within guardrails.\n")

    try:
        # Simulate the conversation
        simulate_ai_agent_conversation()

        # Show guardrail examples
        show_guardrail_examples()

        print("\n" + "=" * 60)
        print("🎯 KEY BENEFITS:")
        print("✅ Natural conversation instead of CLI prompts")
        print("✅ AI agents handle technical execution")
        print("✅ Guardrails prevent drift from core processes")
        print("✅ All existing functionality preserved")
        print("✅ Perfect for Cursor AI and other agents")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        print("Make sure you're in a project directory with ai_onboard.json")


if __name__ == "__main__":
    main()
