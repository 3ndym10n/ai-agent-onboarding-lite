#!/usr/bin/env python3
"""
Debug Self-Improvement System Issues
"""
from ai_onboard.core.common_imports import ai_onboard, sys

from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_onboard.core.learning_persistence import LearningPersistenceManager
from ai_onboard.core.automatic_error_prevention import AutomaticErrorPrevention


def debug_pattern_recognition():
    print("🔍 Debugging Pattern Recognition")
    pattern_system = PatternRecognitionSystem(project_root)

    # Test with the exact error from the test
    cli_error = {
        "type": "ArgumentError",
        "message": "invalid choice: '--invalid-option'",
        "traceback": "invalid choice: '--invalid-option'",
    }

    print(f"Testing error: {cli_error}")

    # Check existing patterns
    print(f"Existing patterns: {len(pattern_system.patterns)}")
    for pid, pattern in pattern_system.patterns.items():
        print(f"  {pid}: {pattern.pattern_type} (confidence: {pattern.confidence})")

    match = pattern_system.analyze_error(cli_error)
    print(f"Match result: pattern_id={match.pattern_id}, confidence={match.confidence}")
    print(f"Prevention suggestions: {match.prevention_suggestions}")

    # Check pattern stats
    stats = pattern_system.get_pattern_stats()
    print(f"Pattern stats: {stats}")


def debug_learning_persistence():
    print("\n🔍 Debugging Learning Persistence")
    persistence = LearningPersistenceManager(project_root)

    # Check current stats
    stats = persistence.get_learning_stats()
    print(f"Current stats: {stats}")

    # Check learning history
    history = persistence.get_learning_history(10)
    print(f"Recent history ({len(history)} events):")
    for event in history[:5]:
        print(f"  {event['event_type']}: {event['event_data']}")


def debug_prevention_system():
    print("\n🔍 Debugging Prevention System")
    pattern_system = PatternRecognitionSystem(project_root)
    prevention_system = AutomaticErrorPrevention(project_root, pattern_system)

    # Test with fixable code
    fixable_code = "def bad_function():  \nprint('hello')   \n"
    print(f"Testing code: {repr(fixable_code)}")

    result = prevention_system.prevent_code_errors(fixable_code)
    print(
        f"Prevention result: risk_level={result['risk_level']}, confidence={result['confidence']}"
    )
    print(f"Preventions applied: {len(result['prevention_applied'])}")
    print(f"Recommendations: {len(result['recommendations'])}")

    # Try automatic fixes
    fixed_content, applied_fixes = prevention_system.apply_automatic_fixes(
        fixable_code, result
    )
    print(f"Applied fixes: {applied_fixes}")
    print(f"Fixed content: {repr(fixed_content)}")


if __name__ == "__main__":
    debug_pattern_recognition()
    debug_learning_persistence()
    debug_prevention_system()
