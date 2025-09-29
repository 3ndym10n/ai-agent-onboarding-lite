#!/usr/bin/env python3
"""
Simple Anti-Drift Demo - Shows the system working in action.
"""

import tempfile
from pathlib import Path

# Import our anti-drift components
from ai_onboard.core.ai_integration import (
    get_clarification_question_engine,
    get_conversation_memory_manager,
    get_natural_language_intent_parser,
    get_progressive_disclosure_engine,
    get_user_journey_mapper,
)


def main():
    """Run the simple anti-drift demonstration."""
    print("ANTI-DRIFT SYSTEM DEMONSTRATION")
    print("=" * 50)
    print("Testing all anti-drift components...")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        # Test 1: Intent Parser
        print("\n1. INTENT PARSER")
        parser = get_natural_language_intent_parser(root)
        result = parser.parse_user_intent(
            "I want to make a website where people can buy my handmade stuff",
            "test_user",
        )
        print(f"   Project Type: {result.project_type}")
        print(f"   Confidence: {result.confidence_score:.1%}")
        print(f"   Features: {', '.join(result.primary_features)}")

        # Test 2: Conversation Memory
        print("\n2. CONVERSATION MEMORY")
        memory = get_conversation_memory_manager(root)
        conv_id = memory.start_conversation("test_user", "Build e-commerce site")
        print(f"   Conversation: {conv_id}")
        memory.add_message_to_conversation(conv_id, "What technologies should I use?")
        context = memory.get_conversation_context(conv_id)
        print(f"   Stage: {context['current_stage']}")

        # Test 3: Progressive UI
        print("\n3. PROGRESSIVE UI")
        ui = get_progressive_disclosure_engine(root)
        interface = ui.get_simplified_interface("beginner_user", "project_setup")
        print(f"   Elements for beginner: {len(interface['elements'])}")
        print(f"   User expertise: {interface['user_expertise']}")

        # Test 4: Clarification Questions
        print("\n4. CLARIFICATION QUESTIONS")
        questions = get_clarification_question_engine(root)
        q_list = questions.generate_clarification_questions(
            "I want something", "test_user", {}
        )
        print(f"   Questions generated: {len(q_list)}")
        if q_list:
            print(f"   Sample question: {q_list[0].question_text}")

        # Test 5: Journey Mapping
        print("\n5. JOURNEY MAPPING")
        journey = get_user_journey_mapper(root)
        journey_rec = journey.get_recommended_journey("Build a website", "test_user")
        if journey_rec:
            print(f"   Recommended: {journey_rec.name}")
            print(f"   Steps: {len(journey_rec.steps)}")

        print("\n" + "=" * 50)
        print("SUCCESS: All anti-drift components working!")
        print(
            "The system can now prevent AI agent drift and help users complete projects."
        )


if __name__ == "__main__":
    main()
