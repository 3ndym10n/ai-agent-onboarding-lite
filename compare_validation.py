#!/usr/bin/env python3
"""
Validation Comparison Tool

Compares the old basic validation with the new enhanced validation
to demonstrate false positive reduction.
"""

import sys
from pathlib import Path
from enhanced_progress_tracker import EnhancedProgressTracker
from validation_system import EnhancedValidator

class ValidationComparator:
    """Compare old vs new validation methods"""

    def __init__(self, project_root: str = ".."):
        self.project_root = Path(project_root).resolve()
        self.enhanced_tracker = EnhancedProgressTracker(project_root)
        self.enhanced_validator = EnhancedValidator(project_root)

    def compare_dashboard_validation(self):
        """Compare old vs new validation for dashboard component"""
        print("🎯 DASHBOARD VALIDATION COMPARISON")
        print("=" * 50)

        dashboard_config = {
            "file": "dashboard/streamlit_mvp.py",
            "required_functions": ["main", "render_chart", "render_terminal"]
        }

        # Old validation (file existence + basic checks)
        print("\n📊 OLD VALIDATION METHOD:")
        print("   ✅ Checks for:")
        print("      - File exists")
        print("      - Required functions present")
        print("      - Basic syntax/structure")

        old_result = self._simulate_old_validation(dashboard_config)
        print(f"   📈 Result: {old_result['status']} ({old_result['confidence']}%)")

        if old_result["issues"]:
            print("   🚨 Issues:")
            for issue in old_result["issues"]:
                print(f"      - {issue}")

        # New enhanced validation
        print("\n🔬 NEW ENHANCED VALIDATION METHOD:")
        print("   ✅ Checks for:")
        print("      - File exists and is readable")
        print("      - Required functions present")
        print("      - Streamlit integration works")
        print("      - 70/30 layout implemented")
        print("      - Error handling present")
        print("      - Runtime import test")
        print("      - Data integration")

        new_result = self.enhanced_validator.validate_component("dashboard_mvp", dashboard_config)
        print(f"   📈 Result: {new_result['status']} ({new_result['confidence']:.1f}%)")
        print(f"   ✅ Valid: {new_result['valid']}")

        if new_result["issues"]:
            print("   🚨 Issues Found:")
            for issue in new_result["issues"]:
                print(f"      - {issue}")

        if new_result["recommendations"]:
            print("   💡 Recommendations:")
            for rec in new_result["recommendations"]:
                print(f"      - {rec}")

        # Comparison
        print("\n📊 COMPARISON:")
        confidence_diff = new_result["confidence"] - old_result["confidence"]
        if confidence_diff != 0:
            direction = "⬆️ MORE" if confidence_diff > 0 else "⬇️ LESS"
            print(f"   📈 Confidence: {direction} ACCURATE ({abs(confidence_diff):.1f}%)")
        else:
            print("   📈 Confidence: SAME")

        old_valid = old_result["confidence"] >= 80
        new_valid = new_result["valid"]

        if old_valid and not new_valid:
            print("   🎯 FALSE POSITIVE DETECTED!")
            print("      Old method: ✅ Complete")
            print("      New method: ❌ Actually broken")
        elif not old_valid and new_valid:
            print("   🎯 FALSE NEGATIVE CORRECTED!")
            print("      Old method: ❌ Incomplete")
            print("      New method: ✅ Actually working")
        else:
            print("   ✅ Results consistent")

        return {
            "old": old_result,
            "new": new_result,
            "comparison": {
                "false_positive_detected": old_valid and not new_valid,
                "confidence_difference": confidence_diff
            }
        }

    def compare_analytics_validation(self):
        """Compare validation methods for analytics components"""
        print("\n🎯 ANALYTICS VALIDATION COMPARISON")
        print("=" * 50)

        analytics_configs = {
            "tpo_analyzer": {
                "file": "analytics/tpo_market_profile.py",
                "required_classes": ["TPOMarketProfile"],
                "required_methods": ["analyze", "detect_anomalies"]
            },
            "regime_detector": {
                "file": "analytics/regime_detector.py",
                "required_classes": ["RegimeDetector"],
                "required_methods": ["detect_regime", "get_confidence"]
            }
        }

        results = {}

        for comp_name, config in analytics_configs.items():
            print(f"\n🔬 {comp_name.upper()} VALIDATION:")

            # Old method
            old_result = self._simulate_old_validation(config)
            print(f"   📊 Old: {old_result['status']} ({old_result['confidence']}%)")

            # New method
            new_result = self.enhanced_validator.validate_component(comp_name, config)
            print(f"   🔬 New: {new_result['status']} ({new_result['confidence']:.1f}%) - Valid: {new_result['valid']}")

            if new_result["issues"]:
                print("      Issues:")
                for issue in new_result["issues"][:3]:  # Show first 3
                    print(f"         - {issue}")

            results[comp_name] = {
                "old": old_result,
                "new": new_result,
                "improvement": new_result["confidence"] - old_result["confidence"]
            }

        return results

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

            # Check classes, methods, functions
            for check_type in ["required_classes", "required_methods", "required_functions"]:
                if check_type in config:
                    for element in config[check_type]:
                        total_elements += 1
                        if f"def {element}" in content or f"class {element}" in content:
                            found_elements += 1
                        else:
                            missing_elements.append(f"{element}")

            completeness = (found_elements / total_elements * 100) if total_elements > 0 else 100

            return {
                "status": "COMPLETED" if completeness == 100 else "IN_PROGRESS" if completeness >= 50 else "STARTED",
                "confidence": completeness,
                "issues": missing_elements
            }

        except Exception as e:
            return {
                "status": "ERROR",
                "confidence": 0,
                "issues": [f"Error reading file: {e}"]
            }

    def generate_comparison_report(self):
        """Generate comprehensive comparison report"""
        print("🔬 VECTORFLOW VALIDATION COMPARISON REPORT")
        print("=" * 60)
        print("Comparing old file-existence validation vs new runtime validation")
        print()

        # Dashboard comparison
        dashboard_comp = self.compare_dashboard_validation()

        # Analytics comparison
        analytics_comp = self.compare_analytics_validation()

        # Summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY & RECOMMENDATIONS")
        print("=" * 60)

        false_positives_found = dashboard_comp["comparison"]["false_positive_detected"]

        if false_positives_found:
            print("🚨 FALSE POSITIVES DETECTED!")
            print("   The old validation method reported components as complete")
            print("   when they were actually broken or incomplete.")
        else:
            print("✅ No false positives detected in this sample")

        print("\n🎯 KEY IMPROVEMENTS:")
        print("   • Runtime testing prevents false completion claims")
        print("   • Requirement compliance validation")
        print("   • Integration testing for UI components")
        print("   • Actual functionality verification")

        print("\n💡 RECOMMENDATIONS:")
        print("   • Use enhanced validation for all UI/UX components")
        print("   • Implement runtime testing for critical features")
        print("   • Add requirement compliance checking")
        print("   • Validate integrations between components")

        return {
            "dashboard_comparison": dashboard_comp,
            "analytics_comparison": analytics_comp,
            "false_positives_detected": false_positives_found
        }


def main():
    """Run validation comparison"""
    comparator = ValidationComparator()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--dashboard":
            comparator.compare_dashboard_validation()
        elif sys.argv[1] == "--analytics":
            comparator.compare_analytics_validation()
        elif sys.argv[1] == "--full":
            comparator.generate_comparison_report()
    else:
        comparator.generate_comparison_report()


if __name__ == "__main__":
    main()