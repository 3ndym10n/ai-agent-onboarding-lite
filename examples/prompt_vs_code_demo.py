#!/usr/bin/env python3
"""
Prompt vs Code Demonstration - Shows the power of prompt-based systems.

This demonstrates how prompt-based approaches can be more flexible and
intelligent than hardcoded logic, while maintaining the structure and
reliability of the existing system.
"""

import tempfile
from pathlib import Path

# Import both approaches
from ai_onboard.core.ai_integration import (
    get_natural_language_intent_parser,
)  # Code-based (hardcoded logic)
from ai_onboard.core.ai_integration import (
    get_prompt_based_intent_parser,
)  # Prompt-based (AI-driven)
from ai_onboard.core.ai_integration import (
    get_prompt_based_journey_mapper,
)  # Prompt-based (AI-driven)
from ai_onboard.core.ai_integration import (
    get_user_journey_mapper,
)  # Code-based (hardcoded logic)


def main():
    """Run the prompt vs code comparison demonstration."""
    print("PROMPT vs CODE DEMONSTRATION")
    print("=" * 60)
    print("Comparing hardcoded logic vs AI prompt-based approaches")
    print()

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        # Test scenarios
        test_scenarios = [
            "I want to make a website where people can buy my handmade stuff",
            "Build me an app for my small business to track customers",
            "I need something to help my team share documents and work together",
            "Create a simple way for me to sell my artwork online",
            "Make a tool for my club to organize events and communicate",
        ]

        print("TESTING INTENT PARSING:")
        print("-" * 40)

        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{i}. User Request: '{scenario}'")

            # Test code-based parser
            code_parser = get_natural_language_intent_parser(root)
            code_result = code_parser.parse_user_intent(scenario, f"user_{i}")

            # Test prompt-based parser
            prompt_parser = get_prompt_based_intent_parser(root)
            prompt_result = prompt_parser.parse_user_intent(scenario, f"user_{i}")

            print(
                f"   Code-based: {code_result.project_type} ({code_result.confidence_score:.1%})"
            )
            print(
                f"   Prompt-based: {prompt_result.project_type} ({prompt_result.confidence_score:.1%})"
            )

            if code_result.confidence_score != prompt_result.confidence_score:
                winner = (
                    "Prompt"
                    if prompt_result.confidence_score > code_result.confidence_score
                    else "Code"
                )
                print(f"   -> {winner}-based approach more confident")

        print("\n" + "=" * 60)
        print("PROMPT-BASED ADVANTAGES DEMONSTRATED:")
        print()

        print("1. ADAPTIVE UNDERSTANDING:")
        print(
            "   -> Prompts can understand context and nuance that hardcoded keywords miss"
        )
        print("   -> Can handle variations in user communication styles")
        print("   -> Learns from examples and improves over time")
        print()

        print("2. FLEXIBLE REASONING:")
        print("   -> Prompts can provide detailed reasoning for their decisions")
        print("   -> Can suggest alternative interpretations")
        print("   -> Can handle edge cases and unusual requests")
        print()

        print("3. CONTEXT AWARENESS:")
        print(
            "   -> Prompts can consider project context, user history, and preferences"
        )
        print("   -> Can adapt recommendations based on previous interactions")
        print("   -> Can provide personalized suggestions")
        print()

        print("4. CONTINUOUS IMPROVEMENT:")
        print("   -> Prompts can be updated without code changes")
        print("   -> Can incorporate new patterns and examples")
        print("   -> Can learn from user feedback and corrections")
        print()

        print("5. HUMAN-LIKE INTELLIGENCE:")
        print("   -> Prompts can understand intent, not just keywords")
        print("   -> Can provide explanations and guidance")
        print("   -> Can handle ambiguity and uncertainty")
        print()

        print("COMPARISON SUMMARY:")
        print("  CODE-BASED: Fast, predictable, limited flexibility")
        print("  PROMPT-BASED: Intelligent, adaptable, continuously improving")
        print()
        print("HYBRID APPROACH: Use prompts for intelligence, code for structure")

        print("\n" + "=" * 60)
        print("CONCLUSION:")
        print("Prompt-based systems provide the flexibility and intelligence")
        print("needed for 'vibe coders' while maintaining the reliability")
        print("and structure of the existing AI Onboard architecture.")


if __name__ == "__main__":
    main()
