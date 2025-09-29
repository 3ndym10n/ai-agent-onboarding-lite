#!/usr/bin/env python3
"""
Comprehensive Test Suite for Self-Improvement System Integration

This script tests that the self-improvement system (4.8, 4.9, 4.10) is working correctly:
- Pattern Recognition System (4.8)
- Learning Persistence (4.9)
- Automatic Error Prevention (4.10)

Tests include:
- Pattern learning and recognition
- Persistence across sessions
- Automatic prevention before code creation
- Integration with validation system
"""

import json
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_onboard.core.continuous_improvement.learning_persistence import (
    LearningPersistenceManager,
)
from ai_onboard.core.orchestration.automatic_error_prevention import (
    AutomaticErrorPrevention,
)
from ai_onboard.core.orchestration.pattern_recognition_system import (
    PatternRecognitionSystem,
)


def test_pattern_recognition():
    """Test 4.8: Pattern Recognition System"""
    print("🧪 Testing Pattern Recognition System (4.8)")
    print("=" * 50)

    pattern_system = PatternRecognitionSystem(project_root)

    # Test CLI error pattern
    cli_error = {
        "type": "ArgumentError",
        "message": "invalid choice: '--invalid-option'",
        "traceback": "invalid choice: '--invalid-option'",
    }

    match = pattern_system.analyze_error(cli_error)
    assert match.pattern_id != "unknown_error", "Should recognize CLI error pattern"
    assert match.confidence >= 0.7, f"High confidence expected, got {match.confidence}"
    print("✅ CLI error pattern recognition: PASS")

    # Test import error pattern
    import_error = {
        "type": "ImportError",
        "message": "No module named 'nonexistent_module'",
        "traceback": "ImportError: No module named 'nonexistent_module'",
    }

    match = pattern_system.analyze_error(import_error)
    assert match.pattern_id != "unknown_error", "Should recognize import error pattern"
    assert match.confidence >= 0.7, f"High confidence expected, got {match.confidence}"
    print("✅ Import error pattern recognition: PASS")

    # Test styling error pattern
    styling_error = {
        "type": "StyleError",
        "message": "trailing whitespace found",
        "traceback": "line has trailing whitespace",
    }

    match = pattern_system.analyze_error(styling_error)
    assert match.pattern_id != "unknown_error", "Should recognize styling error pattern"
    print("✅ Styling error pattern recognition: PASS")

    stats = pattern_system.get_pattern_stats()
    assert stats["total_patterns"] > 0, "Should have learned patterns"
    print(f"✅ Pattern learning: {stats['total_patterns']} patterns learned")


def test_learning_persistence():
    """Test 4.9: Learning Persistence"""
    print("\n🧪 Testing Learning Persistence (4.9)")
    print("=" * 50)

    pattern_system = PatternRecognitionSystem(project_root)
    persistence = LearningPersistenceManager(project_root)

    # Record some learning events
    persistence.record_learning_event(
        "pattern_learned",
        {
            "pattern_id": "test_pattern_1",
            "pattern_type": "cli_error",
            "confidence": 0.9,
        },
    )

    persistence.record_learning_event(
        "error_prevented",
        {
            "pattern_id": "test_pattern_1",
            "prevention_type": "cli_validation",
            "impact": "high",
        },
    )

    # Test backup creation
    success = persistence.save_pattern_backup(pattern_system)
    assert success, "Pattern backup should succeed"
    print("✅ Pattern backup creation: PASS")

    # Test backup restoration
    new_pattern_system = PatternRecognitionSystem(project_root)
    success = persistence.load_pattern_backup(new_pattern_system)
    assert success, "Pattern backup restoration should succeed"
    print("✅ Pattern backup restoration: PASS")

    # Test learning stats
    stats = persistence.get_learning_stats()
    assert stats["total_learning_events"] >= 2, "Should have recorded learning events"
    assert stats["patterns_learned"] >= 1, "Should have learned patterns"
    assert stats["errors_prevented"] >= 1, "Should have prevented errors"
    print(f"✅ Learning statistics: {stats['total_learning_events']} events recorded")


def test_automatic_prevention():
    """Test 4.10: Automatic Error Prevention"""
    print("\n🧪 Testing Automatic Error Prevention (4.10)")
    print("=" * 50)

    pattern_system = PatternRecognitionSystem(project_root)
    prevention_system = AutomaticErrorPrevention(project_root, pattern_system)

    # Test CLI command prevention
    cli_result = prevention_system.prevent_cli_errors(
        "python -m ai_onboard --invalid-option"
    )
    assert (
        cli_result["risk_level"] == "high"
    ), f"High risk expected, got {cli_result['risk_level']}"
    assert cli_result["prevention_applied"], "Should have applied CLI preventions"
    assert (
        cli_result["confidence"] > 0.8
    ), f"High confidence expected, got {cli_result['confidence']}"
    print("✅ CLI command prevention: PASS")

    # Test code prevention
    bad_code = "import nonexistent_module\nprint('hello')"
    code_result = prevention_system.prevent_code_errors(bad_code)
    assert (
        code_result["risk_level"] == "high"
    ), f"High risk expected, got {code_result['risk_level']}"
    assert code_result["prevention_applied"], "Should have applied code preventions"
    print("✅ Code error prevention: PASS")

    # Test automatic fixes
    fixable_code = "def bad_function():  \nprint('hello')   \n"
    fix_result = prevention_system.prevent_code_errors(fixable_code)
    fixed_content, applied_fixes = prevention_system.apply_automatic_fixes(
        fixable_code, fix_result
    )
    assert applied_fixes, "Should have applied automatic fixes"
    assert (
        "Removed trailing whitespace" in applied_fixes
    ), "Should fix trailing whitespace"
    print("✅ Automatic fixes: PASS")

    # Test prevention stats
    stats = prevention_system.get_prevention_stats()
    assert stats.get("preventions_applied", 0) >= 2, "Should have applied preventions"
    print(
        f"✅ Prevention statistics: {stats.get('preventions_applied', 0)} preventions applied"
    )


def test_integration_validation():
    """Test integration with validation system"""
    print("\n🧪 Testing Validation System Integration")
    print("=" * 50)

    # Test that validation runtime includes prevention
    from ai_onboard.core.monitoring_analytics.validation_runtime import run

    # Create a simple test manifest
    test_manifest = {
        "name": "test_component",
        "components": [
            {
                "name": "test_comp",
                "type": "python",
                "language": "python",
                "paths": ["ai_onboard/core/pattern_recognition_system.py"],
            }
        ],
    }

    # Write test manifest
    test_manifest_path = project_root / "ai_onboard.json"
    original_content = None
    if test_manifest_path.exists():
        with open(test_manifest_path, "r") as f:
            original_content = f.read()

    with open(test_manifest_path, "w") as f:
        json.dump(test_manifest, f, indent=2)

    try:
        # Run validation
        result = run(project_root)

        # Check that prevention analysis was included
        components = result.get("results", [])
        assert len(components) > 0, "Should have validation results"

        comp_result = components[0]
        prevention_analysis = comp_result.get("prevention_analysis", {})
        assert prevention_analysis, "Should include prevention analysis"

        print("✅ Validation integration: PASS")
        print(
            f"   📊 Prevention analysis included for {len(prevention_analysis)} files"
        )

    finally:
        # Restore original manifest
        if original_content:
            with open(test_manifest_path, "w") as f:
                f.write(original_content)
        elif test_manifest_path.exists():
            test_manifest_path.unlink()


def test_end_to_end_workflow():
    """Test complete end-to-end workflow"""
    print("\n🧪 Testing End-to-End Workflow")
    print("=" * 50)

    # 1. Create error pattern
    pattern_system = PatternRecognitionSystem(project_root)
    error_data = {
        "type": "ImportError",
        "message": "No module named 'test_module'",
        "traceback": "ImportError: No module named 'test_module'",
    }

    # 2. Learn pattern
    match = pattern_system.analyze_error(error_data)
    assert match.pattern_id != "unknown_error", "Should learn new pattern"
    print("✅ Pattern learning: PASS")

    # 3. Persist pattern
    persistence = LearningPersistenceManager(project_root)
    success = persistence.save_pattern_backup(pattern_system)
    assert success, "Should persist patterns"
    print("✅ Pattern persistence: PASS")

    # 4. Prevent similar error
    prevention_system = AutomaticErrorPrevention(project_root, pattern_system)
    similar_code = "import another_missing_module\nprint('test')"
    result = prevention_system.prevent_code_errors(similar_code)
    assert result["prevention_applied"], "Should prevent similar errors"
    print("✅ Error prevention: PASS")

    # 5. Verify learning history
    history = persistence.get_learning_history()
    assert len(history) > 0, "Should have learning history"
    print(f"✅ Learning history: {len(history)} events recorded")


def main():
    """Run comprehensive test suite"""
    print("🚀 Comprehensive Self-Improvement System Test Suite")
    print("=" * 60)
    print(f"Testing system at: {project_root}")
    print()

    tests = [
        ("Pattern Recognition (4.8)", test_pattern_recognition),
        ("Learning Persistence (4.9)", test_learning_persistence),
        ("Automatic Prevention (4.10)", test_automatic_prevention),
        ("Validation Integration", test_integration_validation),
        ("End-to-End Workflow", test_end_to_end_workflow),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"🎉 {test_name}: PASSED\n")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED\n")
                failed += 1
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}\n")
            failed += 1

    print("=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed / (passed + failed)) * 100:.1f}%")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print(
            "✨ Self-improvement system is fully functional and will prevent errors before code creation!"
        )
        return True
    else:
        print(f"\n⚠️ {failed} tests failed. System needs attention.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
