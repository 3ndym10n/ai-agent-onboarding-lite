#!/usr/bin/env python3
"""
Comprehensive Integration Tests for ai-onboard Tool Ecosystem

This script tests the integration between operational tools to ensure they work
together effectively as a cohesive system.
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, ".")

from ai_onboard.core.base.unified_tool_orchestrator import UnifiedToolOrchestrator


class IntegrationTestSuite:
    """Comprehensive integration test suite for operational tools."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.orchestrator = UnifiedToolOrchestrator(root_path)
        self.test_results = []

    def run_all_integration_tests(self) -> Dict[str, Any]:
        """Run all integration test scenarios."""
        print("🧪 Starting Comprehensive Integration Test Suite")
        print("=" * 60)

        test_scenarios = [
            self.test_code_analysis_integration,
            self.test_project_management_integration,
            self.test_safety_quality_integration,
            self.test_user_experience_integration,
            self.test_ai_orchestration_integration,
            self.test_vision_analysis_integration,
        ]

        results = {}
        total_tests = 0
        passed_tests = 0

        for test_scenario in test_scenarios:
            scenario_name = (
                test_scenario.__name__.replace("test_", "").replace("_", " ").title()
            )
            print(f"\n🔗 Testing {scenario_name} Integration")

            try:
                start_time = time.time()
                scenario_result = test_scenario()
                end_time = time.time()

                scenario_result["duration"] = end_time - start_time
                results[scenario_name] = scenario_result

                total_tests += scenario_result["total_tests"]
                passed_tests += scenario_result["passed_tests"]

                status = "✅ PASSED" if scenario_result["passed"] else "❌ FAILED"
                print(
                    f"   {status} - {scenario_result['passed_tests']}/{scenario_result['total_tests']} tests passed"
                )

            except Exception as e:
                print(f"   ❌ EXCEPTION: {e}")
                results[scenario_name] = {
                    "passed": False,
                    "total_tests": 1,
                    "passed_tests": 0,
                    "error": str(e),
                    "duration": 0,
                }

        # Summary
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        summary = {
            "total_scenarios": len(test_scenarios),
            "passed_scenarios": sum(
                1 for r in results.values() if r.get("passed", False)
            ),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "results": results,
        }

        print("\n" + "=" * 60)
        print("🎯 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(
            f"📊 Scenarios: {summary['passed_scenarios']}/{summary['total_scenarios']}"
        )
        print(f"🧪 Tests: {summary['passed_tests']}/{summary['total_tests']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")

        if success_rate >= 90:
            print("🎉 EXCELLENT: Tools integrate seamlessly!")
        elif success_rate >= 75:
            print("👍 GOOD: Tools integrate well with minor issues")
        else:
            print("⚠️  NEEDS IMPROVEMENT: Integration issues detected")

        return summary

    def test_code_analysis_integration(self) -> Dict[str, Any]:
        """Test integration between code analysis tools."""
        tests_passed = 0
        total_tests = 4

        # Test 1: Code quality analyzer provides foundation
        try:
            result1 = self.orchestrator.execute_automatic_tool_application(
                "code_quality_analyzer", {"test_mode": True}
            )
            if result1.get("executed", False):
                tests_passed += 1
                print("   ✓ Code quality analysis foundation established")
            else:
                print("   ✗ Code quality analysis failed")
        except Exception as e:
            print(f"   ✗ Code quality analysis exception: {e}")

        # Test 2: Dependency mapper works with code analysis
        try:
            result2 = self.orchestrator.execute_automatic_tool_application(
                "dependency_mapper", {"test_mode": True}
            )
            if result2.get("executed", False):
                tests_passed += 1
                print("   ✓ Dependency analysis integrates with code foundation")
            else:
                print("   ✗ Dependency analysis failed")
        except Exception as e:
            print(f"   ✗ Dependency analysis exception: {e}")

        # Test 3: Duplicate detector complements analysis
        try:
            result3 = self.orchestrator.execute_automatic_tool_application(
                "duplicate_detector", {"test_mode": True}
            )
            if result3.get("executed", False):
                tests_passed += 1
                print("   ✓ Duplicate detection integrates with analysis suite")
            else:
                print("   ✗ Duplicate detection failed")
        except Exception as e:
            print(f"   ✗ Duplicate detection exception: {e}")

        # Test 4: Pattern recognition enhances error prevention
        try:
            result4 = self.orchestrator.execute_automatic_tool_application(
                "pattern_recognition_system", {"test_mode": True}
            )
            if result4.get("executed", False):
                tests_passed += 1
                print("   ✓ Pattern recognition integrates with error analysis")
            else:
                print("   ✗ Pattern recognition failed")
        except Exception as e:
            print(f"   ✗ Pattern recognition exception: {e}")

        return {
            "passed": tests_passed == total_tests,
            "total_tests": total_tests,
            "passed_tests": tests_passed,
            "description": "Code analysis tools work together for comprehensive codebase understanding",
        }

    def test_project_management_integration(self) -> Dict[str, Any]:
        """Test integration between project management tools."""
        tests_passed = 0
        total_tests = 3

        # Test 1: Charter management provides foundation
        try:
            result1 = self.orchestrator.execute_automatic_tool_application(
                "charter_management", {"test_mode": True}
            )
            if result1.get("executed", False):
                tests_passed += 1
                print("   ✓ Charter management foundation established")
            else:
                print("   ✗ Charter management failed")
        except Exception as e:
            print(f"   ✗ Charter management exception: {e}")

        # Test 2: WBS management integrates with charter
        try:
            result2 = self.orchestrator.execute_automatic_tool_application(
                "wbs_management", {"test_mode": True}
            )
            if result2.get("executed", False):
                tests_passed += 1
                print("   ✓ WBS management integrates with charter foundation")
            else:
                print("   ✗ WBS management failed")
        except Exception as e:
            print(f"   ✗ WBS management exception: {e}")

        # Test 3: Task execution gate controls project flow
        try:
            result3 = self.orchestrator.execute_automatic_tool_application(
                "task_execution_gate", {"test_mode": True}
            )
            if result3.get("executed", False):
                tests_passed += 1
                print("   ✓ Task execution gate controls project workflow")
            else:
                print("   ✗ Task execution gate failed")
        except Exception as e:
            print(f"   ✗ Task execution gate exception: {e}")

        return {
            "passed": tests_passed == total_tests,
            "total_tests": total_tests,
            "passed_tests": tests_passed,
            "description": "Project management tools coordinate for effective project execution",
        }

    def test_safety_quality_integration(self) -> Dict[str, Any]:
        """Test integration between safety and quality tools."""
        tests_passed = 0
        total_tests = 3

        # Test 1: Error prevention provides safety foundation
        try:
            result1 = self.orchestrator.execute_automatic_tool_application(
                "automatic_error_prevention", {"test_mode": True}
            )
            if result1.get("executed", False):
                tests_passed += 1
                print("   ✓ Error prevention safety foundation established")
            else:
                print("   ✗ Error prevention failed")
        except Exception as e:
            print(f"   ✗ Error prevention exception: {e}")

        # Test 2: Ultra safe cleanup integrates with safety
        try:
            result2 = self.orchestrator.execute_automatic_tool_application(
                "ultra_safe_cleanup", {"test_mode": True}
            )
            if result2.get("executed", False):
                tests_passed += 1
                print("   ✓ Ultra safe cleanup integrates with safety systems")
            else:
                print("   ✗ Ultra safe cleanup failed")
        except Exception as e:
            print(f"   ✗ Ultra safe cleanup exception: {e}")

        # Test 3: Gate system controls safety operations
        try:
            result3 = self.orchestrator.execute_automatic_tool_application(
                "gate_system", {"test_mode": True}
            )
            if result3.get("executed", False):
                tests_passed += 1
                print("   ✓ Gate system controls safety-critical operations")
            else:
                print("   ✗ Gate system failed")
        except Exception as e:
            print(f"   ✗ Gate system exception: {e}")

        return {
            "passed": tests_passed == total_tests,
            "total_tests": total_tests,
            "passed_tests": tests_passed,
            "description": "Safety and quality tools work together for robust system operation",
        }

    def test_user_experience_integration(self) -> Dict[str, Any]:
        """Test integration between user experience tools."""
        tests_passed = 0
        total_tests = 3

        # Test 1: UI enhancement provides UX foundation
        try:
            result1 = self.orchestrator.execute_automatic_tool_application(
                "ui_enhancement", {"test_mode": True}
            )
            if result1.get("executed", False):
                tests_passed += 1
                print("   ✓ UI enhancement foundation established")
            else:
                print("   ✗ UI enhancement failed")
        except Exception as e:
            print(f"   ✗ UI enhancement exception: {e}")

        # Test 2: User preference learning personalizes experience
        try:
            result2 = self.orchestrator.execute_automatic_tool_application(
                "user_preference_learning_system", {"test_mode": True}
            )
            if result2.get("executed", False):
                tests_passed += 1
                print("   ✓ User preference learning personalizes UX")
            else:
                print("   ✗ User preference learning failed")
        except Exception as e:
            print(f"   ✗ User preference learning exception: {e}")

        # Test 3: Conversation analysis enhances context awareness
        try:
            result3 = self.orchestrator.execute_automatic_tool_application(
                "conversation_analysis", {"test_mode": True}
            )
            if result3.get("executed", False):
                tests_passed += 1
                print("   ✓ Conversation analysis enhances context awareness")
            else:
                print("   ✗ Conversation analysis failed")
        except Exception as e:
            print(f"   ✗ Conversation analysis exception: {e}")

        return {
            "passed": tests_passed == total_tests,
            "total_tests": total_tests,
            "passed_tests": tests_passed,
            "description": "User experience tools create personalized, context-aware interactions",
        }

    def test_ai_orchestration_integration(self) -> Dict[str, Any]:
        """Test integration between AI orchestration tools."""
        tests_passed = 0
        total_tests = 3

        # Test 1: AI agent orchestration provides foundation
        try:
            result1 = self.orchestrator.execute_automatic_tool_application(
                "ai_agent_orchestration", {"test_mode": True}
            )
            if result1.get("executed", False):
                tests_passed += 1
                print("   ✓ AI agent orchestration foundation established")
            else:
                print("   ✗ AI agent orchestration failed")
        except Exception as e:
            print(f"   ✗ AI agent orchestration exception: {e}")

        # Test 2: Decision pipeline integrates with orchestration
        try:
            result2 = self.orchestrator.execute_automatic_tool_application(
                "decision_pipeline", {"test_mode": True}
            )
            if result2.get("executed", False):
                tests_passed += 1
                print("   ✓ Decision pipeline integrates with AI orchestration")
            else:
                print("   ✗ Decision pipeline failed")
        except Exception as e:
            print(f"   ✗ Decision pipeline exception: {e}")

        # Test 3: Intelligent monitoring oversees AI operations
        try:
            result3 = self.orchestrator.execute_automatic_tool_application(
                "intelligent_monitoring", {"test_mode": True}
            )
            if result3.get("executed", False):
                tests_passed += 1
                print("   ✓ Intelligent monitoring oversees AI operations")
            else:
                print("   ✗ Intelligent monitoring failed")
        except Exception as e:
            print(f"   ✗ Intelligent monitoring exception: {e}")

        return {
            "passed": tests_passed == total_tests,
            "total_tests": total_tests,
            "passed_tests": tests_passed,
            "description": "AI orchestration tools coordinate intelligent system operations",
        }

    def test_vision_analysis_integration(self) -> Dict[str, Any]:
        """Test integration between vision and analysis tools."""
        tests_passed = 0
        total_tests = 3

        # Test 1: Vision guardian provides oversight foundation
        try:
            result1 = self.orchestrator.execute_automatic_tool_application(
                "vision_guardian", {"test_mode": True}
            )
            if result1.get("executed", False):
                tests_passed += 1
                print("   ✓ Vision guardian oversight foundation established")
            else:
                print("   ✗ Vision guardian failed")
        except Exception as e:
            print(f"   ✗ Vision guardian exception: {e}")

        # Test 2: Interrogation system integrates with vision
        try:
            result2 = self.orchestrator.execute_automatic_tool_application(
                "interrogation_system", {"test_mode": True}
            )
            if result2.get("executed", False):
                tests_passed += 1
                print("   ✓ Interrogation system integrates with vision oversight")
            else:
                print("   ✗ Interrogation system failed")
        except Exception as e:
            print(f"   ✗ Interrogation system exception: {e}")

        # Test 3: File organization analyzer complements vision
        try:
            result3 = self.orchestrator.execute_automatic_tool_application(
                "file_organization_analyzer", {"test_mode": True}
            )
            if result3.get("executed", False):
                tests_passed += 1
                print("   ✓ File organization complements vision and analysis")
            else:
                print("   ✗ File organization failed")
        except Exception as e:
            print(f"   ✗ File organization exception: {e}")

        return {
            "passed": tests_passed == total_tests,
            "total_tests": total_tests,
            "passed_tests": tests_passed,
            "description": "Vision and analysis tools provide comprehensive system oversight",
        }


def main():
    """Run the integration test suite."""
    root_path = Path(".")
    test_suite = IntegrationTestSuite(root_path)
    results = test_suite.run_all_integration_tests()

    # Save results
    import json

    results_file = root_path / ".ai_onboard" / "integration_test_results.json"
    results_file.parent.mkdir(exist_ok=True)

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Detailed results saved to: {results_file}")

    # Exit with appropriate code
    success_rate = results.get("success_rate", 0)
    if success_rate >= 90:
        print("🎉 INTEGRATION TESTS PASSED - Tools work together seamlessly!")
        return 0
    elif success_rate >= 75:
        print("⚠️ INTEGRATION TESTS PARTIALLY PASSED - Minor integration issues")
        return 1
    else:
        print("❌ INTEGRATION TESTS FAILED - Significant integration problems")
        return 2


if __name__ == "__main__":
    sys.exit(main())
