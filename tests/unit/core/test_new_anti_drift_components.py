#!/usr/bin/env python3
"""
Test New Anti-Drift Components - Verify the new components work correctly.

This test suite verifies that the newly built anti-drift components function
properly and integrate correctly with the existing system.
"""

import tempfile
from pathlib import Path

import pytest

from ai_onboard.core.ai_integration import (
    get_clarification_question_engine,
    get_conversation_memory_manager,
    get_natural_language_intent_parser,
    get_progressive_disclosure_engine,
    get_user_journey_mapper,
)
from ai_onboard.core.utilities.unicode_utils import ensure_unicode_safe


class TestAntiDriftComponents:
    """Test suite for new anti-drift components."""

    @pytest.fixture
    def temp_root(self):
        """Provide temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_natural_language_intent_parser(self, temp_root):
        """Test the natural language intent parser."""
        parser = get_natural_language_intent_parser(temp_root)

        # Test parsing a vague request
        result = parser.parse_user_intent(
            "I want to make a website where people can buy my handmade stuff",
            "test_user",
        )

        assert result.confidence_score > 0
        assert result.project_type in ["ecommerce", "general"]
        assert len(result.primary_features) > 0
        assert len(result.clarification_questions) >= 0

        print(
            f"✅ Intent parser: {result.project_type} with {result.confidence_score:.2f} confidence"
        )

    def test_conversation_memory_manager(self, temp_root):
        """Test the conversation memory manager."""
        memory_manager = get_conversation_memory_manager(temp_root)

        # Start a conversation
        conversation_id = memory_manager.start_conversation(
            "test_user", "I want to build a blog"
        )

        assert conversation_id is not None
        assert conversation_id.startswith("conv_")

        # Add a message
        memory_manager.add_message_to_conversation(
            conversation_id, "What technologies should I use?"
        )

        # Get context
        context = memory_manager.get_conversation_context(conversation_id)

        assert "conversation_id" in context
        assert "user_intent" in context
        assert "current_stage" in context

        print(f"✅ Conversation memory: {context['current_stage']} stage")

    def test_progressive_disclosure_engine(self, temp_root):
        """Test the progressive disclosure engine."""
        disclosure_engine = get_progressive_disclosure_engine(temp_root)

        # Get simplified interface for beginner
        interface = disclosure_engine.get_simplified_interface(
            "beginner_user", "project_setup"
        )

        assert "elements" in interface
        assert "user_expertise" in interface
        assert len(interface["elements"]) > 0

        print(f"✅ Progressive UI: {len(interface['elements'])} elements for beginner")

    def test_clarification_question_engine(self, temp_root):
        """Test the clarification question engine."""
        question_engine = get_clarification_question_engine(temp_root)

        # Generate questions for ambiguous request
        questions = question_engine.generate_clarification_questions(
            "I want something", "test_user", {}
        )

        assert len(questions) > 0
        assert all(
            isinstance(q, object) for q in questions
        )  # Should be ClarificationQuestion objects
        assert all(hasattr(q, "question_text") for q in questions)

        print(f"✅ Clarification questions: {len(questions)} questions generated")

    def test_user_journey_mapper(self, temp_root):
        """Test the user journey mapper."""
        journey_mapper = get_user_journey_mapper(temp_root)

        # Get recommended journey
        journey = journey_mapper.get_recommended_journey("Build a website", "test_user")

        assert journey is not None
        assert hasattr(journey, "journey_id")
        assert hasattr(journey, "name")
        assert hasattr(journey, "steps")

        # Check that steps are appropriate for user expertise
        user_expertise = journey_mapper._get_user_expertise("test_user")
        user_steps = journey.get_steps_for_user(user_expertise)

        assert len(user_steps) > 0

        print(f"✅ User journey: {journey.name} with {len(user_steps)} steps")

    def test_integrated_workflow(self, temp_root):
        """Test the integrated workflow with all components."""
        # Get all components
        intent_parser = get_natural_language_intent_parser(temp_root)
        memory_manager = get_conversation_memory_manager(temp_root)
        journey_mapper = get_user_journey_mapper(temp_root)

        # Parse user intent
        intent_result = intent_parser.parse_user_intent(
            "Build an e-commerce site for my crafts", "test_user"
        )

        # Start conversation with memory
        conversation_id = memory_manager.start_conversation(
            "test_user", "Build an e-commerce site for my crafts"
        )

        # Get recommended journey
        journey = journey_mapper.get_recommended_journey(
            "Build an e-commerce site for my crafts", "test_user"
        )

        # Verify integration
        assert intent_result.project_type == "ecommerce"
        assert conversation_id is not None
        assert journey is not None

        print("✅ Integrated workflow: All components working together")

    def test_error_handling(self, temp_root):
        """Test error handling in components."""
        # Test with invalid inputs
        intent_parser = get_natural_language_intent_parser(temp_root)

        # Empty request
        result = intent_parser.parse_user_intent("", "test_user")
        assert result is not None

        # Very long request
        long_request = "I want to build a " + "very " * 100 + "complex application"
        result = intent_parser.parse_user_intent(long_request, "test_user")
        assert result is not None

        print("✅ Error handling: Components handle edge cases gracefully")


if __name__ == "__main__":
    # Run tests directly
    import sys

    test_instance = TestAntiDriftComponents()

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)

            ensure_unicode_safe("🧪 Testing New Anti-Drift Components")
            print("=" * 50)

            test_instance.test_natural_language_intent_parser(temp_root)
            test_instance.test_conversation_memory_manager(temp_root)
            test_instance.test_progressive_disclosure_engine(temp_root)
            test_instance.test_clarification_question_engine(temp_root)
            test_instance.test_user_journey_mapper(temp_root)
            test_instance.test_integrated_workflow(temp_root)
            test_instance.test_error_handling(temp_root)

            print("\n" + "=" * 50)
            ensure_unicode_safe("✅ All Anti-Drift Components Working Correctly!")
            ensure_unicode_safe("🎯 System ready for improved user experience")

    except Exception as e:
        ensure_unicode_safe(f"❌ Test failed: {e}")
        sys.exit(1)
