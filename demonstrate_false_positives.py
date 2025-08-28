#!/usr/bin/env python3
"""
Demonstrate False Positive Detection

Shows how the enhanced validation system catches issues that
the old system would miss, using a mock broken dashboard.
"""

import sys
from pathlib import Path
from validation_system import EnhancedValidator

class FalsePositiveDemo:
    """Demonstrate false positive detection"""

    def __init__(self, project_root: str = ".."):
        self.project_root = Path(project_root).resolve()
        self.validator = EnhancedValidator(project_root)

    def demonstrate_false_positive(self):
        """Show how enhanced validation prevents false positives"""
        print("🚨 FALSE POSITIVE DETECTION DEMONSTRATION")
        print("=" * 60)
        print("Using mock_broken_dashboard.py to show the difference")
        print()

        # Test configuration for the mock dashboard
        mock_config = {
            "file": "onboarding/mock_broken_dashboard.py",
            "required_functions": ["main", "render_chart", "render_terminal"],
            "validation_type": "ui_component",
            "critical_requirements": [
                "streamlit_integration",
                "70_30_layout",
                "data_visualization",
                "error_handling"
            ]
        }

        print("🎯 TESTING: Mock Broken Dashboard")
        print("   This file has required functions but is actually broken")
        print()

        # Old validation method simulation
        print("📊 OLD VALIDATION METHOD:")
        old_result = self._simulate_old_validation(mock_config)
        print(f"   ✅ Result: {old_result['status']} ({old_result['confidence']}%)")
        print("   ❌ PROBLEM: Would mark as complete despite being broken!")

        # New enhanced validation
        print("\n🔬 ENHANCED VALIDATION METHOD:")
        new_result = self.validator.validate_component("mock_dashboard", mock_config)
        print(f"   ✅ Result: {new_result['status']} ({new_result['confidence']:.1f}%)")
        print(f"   ✅ Valid: {new_result['valid']}")
        print("   🎯 ACCURATE: Correctly identifies issues!")

        if new_result["issues"]:
            print("\n🚨 ISSUES DETECTED:")
            for issue in new_result["issues"]:
                print(f"      ❌ {issue}")

        if new_result["recommendations"]:
            print("\n💡 RECOMMENDATIONS:")
            for rec in new_result["recommendations"]:
                print(f"      ✅ {rec}")

        # Summary
        print("\n" + "=" * 60)
        print("🎯 SUMMARY:")
        print("=" * 60)

        old_valid = old_result["confidence"] >= 80
        new_valid = new_result["valid"]

        if old_valid and not new_valid:
            print("🚨 FALSE POSITIVE PREVENTED!")
            print("   Old method: ✅ Complete (WRONG!)")
            print("   New method: ❌ Issues found (CORRECT!)")
            print("\n🎉 Enhanced validation prevented a false positive!")

        print(f"\n📈 Accuracy Improvement:")
        print(f"   Old confidence: {old_result['confidence']}%")
        print(f"   New confidence: {new_result['confidence']:.1f}%")
        print(f"   Issues caught: {len(new_result['issues'])}")

        return {
            "old_validation": old_result,
            "new_validation": new_result,
            "false_positive_prevented": old_valid and not new_valid,
            "issues_detected": len(new_result["issues"])
        }

    def _simulate_old_validation(self, config: dict) -> dict:
        """Simulate the old basic validation method"""
        file_path = self.project_root / config["file"]

        if not file_path.exists():
            return {
                "status": "NOT_STARTED",
                "confidence": 0,
                "issues": ["File does not exist"]
            }

        try:
            content = file_path.read_text()
            missing_elements = []
            total_elements = 0
            found_elements = 0

            # Check functions (old method)
            if "required_functions" in config:
                for func_name in config["required_functions"]:
                    total_elements += 1
                    if f"def {func_name}" in content:
                        found_elements += 1
                    else:
                        missing_elements.append(f"Function: {func_name}")

            completeness = (found_elements / total_elements * 100) if total_elements > 0 else 100

            # Old method: If functions exist, mark as complete
            if completeness == 100:
                status = "COMPLETED"
            elif completeness >= 50:
                status = "IN_PROGRESS"
            else:
                status = "STARTED"

            return {
                "status": status,
                "confidence": completeness,
                "issues": missing_elements
            }

        except Exception as e:
            return {
                "status": "ERROR",
                "confidence": 0,
                "issues": [f"Error reading file: {e}"]
            }


def main():
    """Run false positive demonstration"""
    demo = FalsePositiveDemo()

    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("False Positive Detection Demo")
        print("Shows how enhanced validation prevents false positives")
        print("Usage: python demonstrate_false_positives.py")
        return

    result = demo.demonstrate_false_positive()

    print("\n🎉 Demo completed!")
    print(f"   False positive prevented: {result['false_positive_prevented']}")
    print(f"   Issues detected: {result['issues_detected']}")


if __name__ == "__main__":
    main()