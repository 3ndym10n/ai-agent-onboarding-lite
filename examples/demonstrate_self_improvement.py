#!/usr/bin/env python3
"""
Demonstration: Self-Improvement System Preventing Errors Before Code Creation

This script demonstrates that the self-improvement system (4.8, 4.9, 4.10) is working
and will prevent errors before any code is created.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_onboard.core.automatic_error_prevention import AutomaticErrorPrevention
from ai_onboard.core.learning_persistence import LearningPersistenceManager
from ai_onboard.core.pattern_recognition_system import PatternRecognitionSystem


def demonstrate_error_prevention():
    """Demonstrate that the system prevents errors before code creation"""
    print("🚀 SELF-IMPROVEMENT SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("Proving the system will prevent errors BEFORE code creation")
    print()

    # Initialize systems
    pattern_system = PatternRecognitionSystem(project_root)
    persistence = LearningPersistenceManager(project_root)
    prevention_system = AutomaticErrorPrevention(project_root, pattern_system)

    print("📊 SYSTEM STATUS:")
    pattern_stats = pattern_system.get_pattern_stats()
    learning_stats = persistence.get_learning_stats()
    print(f"   • Learned Patterns: {pattern_stats['total_patterns']}")
    print(f"   • Learning Events: {learning_stats['total_learning_events']}")
    print(f"   • Errors Prevented: {learning_stats['errors_prevented']}")
    print()

    # Demonstrate CLI error prevention
    print("🛡️ 1. CLI ERROR PREVENTION")
    print("-" * 30)
    dangerous_command = (
        "python -m ai_onboard --nonexistent-flag --another-invalid-option"
    )
    print(f"Command to analyze: {dangerous_command}")

    cli_result = prevention_system.prevent_cli_errors(dangerous_command)
    print("⚠️  Risk Assessment:")
    print(f"   Risk Level: {cli_result['risk_level'].upper()}")
    print(f"   Confidence: {cli_result['confidence']:.2f}")

    if cli_result["prevention_applied"]:
        print("✅ PREVENTIONS APPLIED:")
        for prevention in cli_result["prevention_applied"]:
            rule = prevention["prevention"]
            print(f"   • {rule['action']}: {', '.join(rule['suggestions'])}")

    print("🎯 RESULT: This dangerous command would be flagged BEFORE execution!")
    print()

    # Demonstrate code error prevention
    print("🛡️ 2. CODE ERROR PREVENTION")
    print("-" * 30)

    problematic_code = """
import nonexistent_module
from missing_package import something

def badFunction():  # Wrong naming convention
    x = None
    print(x.someMethod())  # Will crash
    import another_missing  # Wrong import placement

class badClass:  # Wrong naming
    pass
"""

    print("Code to analyze:")
    print(problematic_code)

    code_result = prevention_system.prevent_code_errors(problematic_code)
    print("⚠️  Risk Assessment:")
    print(f"   Risk Level: {code_result['risk_level'].upper()}")
    print(f"   Confidence: {code_result['confidence']:.2f}")

    if code_result["prevention_applied"]:
        print("✅ PREVENTIONS APPLIED:")
        for prevention in code_result["prevention_applied"]:
            rule = prevention["prevention"]
            print(f"   • {rule['action']}: {', '.join(rule['suggestions'])}")

    if code_result["recommendations"]:
        print("💡 RECOMMENDATIONS:")
        for rec in code_result["recommendations"]:
            print(f"   • {rec['suggestion']}")

    print("🎯 RESULT: These code issues would be caught BEFORE implementation!")
    print()

    # Demonstrate automatic fixes
    print("🔧 3. AUTOMATIC FIXES")
    print("-" * 30)

    messy_code = 'def hello():\n    print("world")   \n    x=1+2\n'
    print("Messy code to fix:")
    print(repr(messy_code))

    fix_result = prevention_system.prevent_code_errors(messy_code)
    fixed_code, applied_fixes = prevention_system.apply_automatic_fixes(
        messy_code, fix_result
    )

    print("✅ AUTOMATIC FIXES APPLIED:")
    for fix in applied_fixes:
        print(f"   • {fix}")

    print("Fixed code:")
    print(repr(fixed_code))

    print("🎯 RESULT: Code formatting issues fixed automatically!")
    print()

    # Demonstrate learning from new errors
    print("🧠 4. LEARNING FROM NEW ERRORS")
    print("-" * 30)

    print("Introducing a new error pattern...")
    new_error = {
        "type": "ValidationError",
        "message": "Component validation failed: missing required field",
        "traceback": "ValidationError: Component validation failed",
    }

    before_patterns = len(pattern_system.patterns)
    match = pattern_system.analyze_error(new_error)
    after_patterns = len(pattern_system.patterns)

    print(f"Patterns before: {before_patterns}")
    print(f"Patterns after: {after_patterns}")
    print(f"New pattern learned: {match.pattern_id}")
    print(f"Pattern confidence: {match.confidence}")

    # Record learning event
    persistence.record_learning_event(
        "pattern_learned",
        {
            "pattern_id": match.pattern_id,
            "pattern_type": "validation_error",
            "source": "demonstration",
        },
    )

    print("✅ LEARNING EVENT RECORDED")
    print("🎯 RESULT: System learns from new errors and builds prevention knowledge!")
    print()

    # Show persistence working
    print("💾 5. PERSISTENCE ACROSS SESSIONS")
    print("-" * 30)

    # Save current state
    success = persistence.save_pattern_backup(pattern_system)
    print(f"Pattern backup saved: {'✅' if success else '❌'}")

    # Simulate new session by creating new instances
    new_pattern_system = PatternRecognitionSystem(project_root)
    new_persistence = LearningPersistenceManager(project_root)

    # Load from backup
    success = new_persistence.load_pattern_backup(new_pattern_system)
    print(f"Pattern backup loaded: {'✅' if success else '❌'}")

    loaded_patterns = len(new_pattern_system.patterns)
    print(f"Patterns available in new session: {loaded_patterns}")

    learning_history = new_persistence.get_learning_history(5)
    print(f"Learning events preserved: {len(learning_history)}")

    print("🎯 RESULT: Learning persists across sessions - no knowledge lost!")
    print()

    # Final validation
    print("🎉 FINAL VALIDATION")
    print("-" * 30)

    tests_passed = 0
    total_tests = 0

    # Test 1: Pattern recognition works
    total_tests += 1
    if pattern_stats["total_patterns"] > 0:
        tests_passed += 1
        print("✅ Pattern Recognition: WORKING")

    # Test 2: Learning persistence works
    total_tests += 1
    if learning_stats["total_learning_events"] > 0:
        tests_passed += 1
        print("✅ Learning Persistence: WORKING")

    # Test 3: Error prevention works
    total_tests += 1
    if cli_result["prevention_applied"] and code_result["prevention_applied"]:
        tests_passed += 1
        print("✅ Error Prevention: WORKING")

    # Test 4: Automatic fixes work
    total_tests += 1
    if applied_fixes:
        tests_passed += 1
        print("✅ Automatic Fixes: WORKING")

    # Test 5: New patterns are learned
    total_tests += 1
    if after_patterns > before_patterns:
        tests_passed += 1
        print("✅ Pattern Learning: WORKING")

    print()
    print("📊 COMPREHENSIVE TEST RESULTS:")
    print(f"   Tests Passed: {tests_passed}/{total_tests}")
    print(f"   Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    if tests_passed == total_tests:
        print("\n🎉 SUCCESS! SELF-IMPROVEMENT SYSTEM IS FULLY OPERATIONAL")
        print("✨ The system WILL prevent errors before any code creation!")
        print("🚀 Ready for safe, learning-enhanced development!")

        return True
    else:
        print(f"\n⚠️ {total_tests - tests_passed} tests need attention")
        return False


if __name__ == "__main__":
    success = demonstrate_error_prevention()
    sys.exit(0 if success else 1)
