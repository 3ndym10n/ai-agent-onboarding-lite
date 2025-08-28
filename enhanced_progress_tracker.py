#!/usr/bin/env python3
"""
Enhanced Progress Tracker for VectorFlow

Significantly reduces false positives by using runtime validation and
requirement compliance checking instead of just file existence.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from validation_system import EnhancedValidator

class EnhancedProgressTracker:
    """
    Enhanced progress tracking with runtime validation to reduce false positives.
    """

    def __init__(self, project_root: str = ".."):
        self.project_root = Path(project_root).resolve()
        self.validator = EnhancedValidator(project_root)
        self.status_file = self.project_root / "onboarding" / "PROJECT_STATUS_TRACKER.md"

        # Enhanced component expectations with validation criteria
        self.component_validations = {
            "infrastructure": {
                "unified_data_service": {
                    "file": "data_pipeline/unified_data_service_v2.py",
                    "required_classes": ["UnifiedDataServiceV2"],
                    "required_methods": ["start", "stop", "collect_data"],
                    "validation_type": "data_component",
                    "critical_requirements": [
                        "async_operations",
                        "connection_handling",
                        "error_recovery"
                    ]
                },
                "unified_analytics_service": {
                    "file": "analytics/unified_analytics_service.py",
                    "required_classes": ["UnifiedAnalyticsService"],
                    "required_methods": ["process_data", "get_signals"],
                    "validation_type": "analytics_component",
                    "critical_requirements": [
                        "data_processing",
                        "signal_generation",
                        "integration_capability"
                    ]
                },
                "database_pool": {
                    "file": "utils/database_pool.py",
                    "required_classes": ["DatabasePool"],
                    "required_methods": ["execute", "batch_insert"],
                    "validation_type": "generic_component",
                    "critical_requirements": [
                        "connection_pooling",
                        "error_handling"
                    ]
                },
                "config_management": {
                    "file": "config/config.yaml",
                    "required_keys": ["exchanges", "symbols", "analytics"],
                    "validation_type": "config_component",
                    "critical_requirements": [
                        "valid_yaml",
                        "required_keys_present"
                    ]
                }
            },

            "analytics_modules": {
                "tpo_analyzer": {
                    "file": "analytics/tpo_market_profile.py",
                    "required_classes": ["TPOMarketProfile"],
                    "required_methods": ["analyze", "detect_anomalies"],
                    "validation_type": "analytics_component",
                    "critical_requirements": [
                        "data_analysis",
                        "anomaly_detection",
                        "output_generation"
                    ]
                },
                "regime_detector": {
                    "file": "analytics/regime_detector.py",
                    "required_classes": ["RegimeDetector"],
                    "required_methods": ["detect_regime", "get_confidence"],
                    "validation_type": "analytics_component",
                    "critical_requirements": [
                        "regime_classification",
                        "confidence_scoring",
                        "market_condition_analysis"
                    ]
                },
                "trap_detector": {
                    "file": "analytics/advanced_trap_spoof_detector.py",
                    "required_classes": ["AdvancedTrapSpoofDetector"],
                    "required_methods": ["detect_traps", "calculate_confidence"],
                    "validation_type": "analytics_component",
                    "critical_requirements": [
                        "trap_detection",
                        "spoof_identification",
                        "confidence_calculation"
                    ]
                },
                "supply_demand": {
                    "file": "analytics/multi_timeframe_supply_demand.py",
                    "required_classes": ["MultiTimeframeSupplyDemand"],
                    "required_methods": ["detect_zones", "get_strength"],
                    "validation_type": "analytics_component",
                    "critical_requirements": [
                        "zone_detection",
                        "strength_calculation",
                        "multi_timeframe_analysis"
                    ]
                }
            },

            "critical_missing": {
                "oi_5s_aggregator": {
                    "file": "analytics/oi_5s_aggregator.py",
                    "required_classes": ["OI5sAggregator"],
                    "required_methods": ["aggregate_oi", "detect_spikes", "check_whole_numbers"],
                    "validation_type": "analytics_component",
                    "critical_requirements": [
                        "oi_aggregation",
                        "spike_detection",
                        "whole_number_analysis"
                    ]
                },
                "signal_fusion_engine": {
                    "file": "analytics/signal_fusion_engine.py",
                    "required_classes": ["SignalFusionEngine"],
                    "required_methods": ["fuse_signals", "calculate_holistic_score", "generate_reasons"],
                    "validation_type": "analytics_component",
                    "critical_requirements": [
                        "signal_fusion",
                        "holistic_scoring",
                        "reason_generation"
                    ]
                },
                "ai_playbook_generator": {
                    "file": "analytics/ai_playbook_generator.py",
                    "required_classes": ["AIPlaybookGenerator"],
                    "required_methods": ["generate_playbooks", "query_grok", "fallback_generation"],
                    "validation_type": "analytics_component",
                    "critical_requirements": [
                        "playbook_generation",
                        "ai_integration",
                        "fallback_handling"
                    ]
                },
                "dashboard_mvp": {
                    "file": "dashboard/streamlit_mvp.py",
                    "required_functions": ["main", "render_chart", "render_terminal"],
                    "validation_type": "ui_component",
                    "critical_requirements": [
                        "streamlit_integration",
                        "70_30_layout",
                        "data_visualization",
                        "terminal_interface",
                        "real_time_updates"
                    ]
                }
            }
        }

    def scan_with_validation(self) -> Dict:
        """
        Scan codebase with enhanced validation to reduce false positives.

        Returns detailed validation results for each component.
        """
        print("🔍 Starting enhanced validation scan...")
        print("   This may take a moment as we test actual functionality...\n")

        results = {
            "infrastructure": {},
            "analytics_modules": {},
            "critical_missing": {},
            "scan_timestamp": datetime.now().isoformat(),
            "validation_method": "enhanced_runtime"
        }

        total_components = 0
        validated_components = 0

        for category, components in self.component_validations.items():
            print(f"📂 Validating {category.replace('_', ' ')}...")

            for component_name, config in components.items():
                total_components += 1
                print(f"   🔬 Testing {component_name}...")

                # Use enhanced validation
                validation_result = self.validator.validate_component(component_name, config)

                results[category][component_name] = {
                    "file_path": config["file"],
                    "validation_type": config.get("validation_type", "generic"),
                    "exists": Path(self.project_root / config["file"]).exists(),
                    "completion_percentage": validation_result["confidence"],
                    "status": validation_result["status"],
                    "issues": validation_result["issues"],
                    "recommendations": validation_result["recommendations"],
                    "is_valid": validation_result["valid"],
                    "critical_requirements": config.get("critical_requirements", []),
                    "last_validated": datetime.now().isoformat()
                }

                if validation_result["valid"]:
                    validated_components += 1
                    print("   ✅ PASSED")
                else:
                    print(f"   ❌ FAILED - {len(validation_result['issues'])} issues")

            print()

        results["summary"] = {
            "total_components": total_components,
            "validated_components": validated_components,
            "validation_rate": (validated_components / total_components * 100) if total_components > 0 else 0,
            "false_positive_reduction": "Enabled"
        }

        return results

    def generate_detailed_report(self) -> str:
        """Generate detailed validation report"""
        results = self.scan_with_validation()

        report = f"""# 🔬 ENHANCED VALIDATION REPORT

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Validation Method:** Runtime + Requirement Compliance
**False Positive Reduction:** ✅ ACTIVE

---

## 📊 VALIDATION SUMMARY

### Overall Results
- **Components Tested:** {results['summary']['total_components']}
- **Validation Success Rate:** {results['summary']['validation_rate']:.1f}%
- **False Positive Protection:** Active

### Category Breakdown

"""

        for category in ["infrastructure", "analytics_modules", "critical_missing"]:
            if category in results:
                components = results[category]
                total = len(components)
                passed = sum(1 for comp in components.values() if comp["is_valid"])

                report += f"""#### {category.replace('_', ' ').title()}
- **Components:** {total}
- **Passed:** {passed} ({(passed/total*100):.1f}%)
- **Failed:** {total-passed}
- **Status:** {'✅ GOOD' if passed/total >= 0.8 else '🔄 NEEDS WORK' if passed/total >= 0.5 else '❌ CRITICAL'}

"""

        report += """---

## 🔬 DETAILED VALIDATION RESULTS

"""

        for category in ["infrastructure", "analytics_modules", "critical_missing"]:
            if category in results:
                report += f"""### {category.replace('_', ' ').title()}

"""

                for comp_name, details in results[category].items():
                    status_emoji = "✅" if details["is_valid"] else "❌"
                    confidence = details["completion_percentage"]

                    report += f"""#### {status_emoji} {comp_name.replace('_', ' ').title()}
- **File:** `{details['file_path']}`
- **Validation:** {details['validation_type'].replace('_', ' ').title()}
- **Status:** {details['status']} ({confidence:.1f}% confidence)
- **Exists:** {'Yes' if details['exists'] else 'No'}

"""

                    if details["issues"]:
                        report += "**Issues Found:**\n"
                        for issue in details["issues"]:
                            report += f"- {issue}\n"

                    if details["recommendations"]:
                        report += "**Recommendations:**\n"
                        for rec in details["recommendations"]:
                            report += f"- {rec}\n"

                    if details["critical_requirements"]:
                        report += "**Critical Requirements:**\n"
                        for req in details["critical_requirements"]:
                            report += f"- {req.replace('_', ' ').title()}\n"

                    report += "\n"

        # Add validation methodology explanation
        report += """---

## 🎯 VALIDATION METHODOLOGY

### What We Test
- **File Structure:** Required classes, methods, functions exist
- **Import Validation:** Modules can be imported without errors
- **Runtime Testing:** Components can execute basic operations
- **Requirement Compliance:** Specific functionality requirements met
- **Integration Ready:** Components work together properly

### False Positive Prevention
- **UI Components:** Test actual Streamlit integration and layout
- **Analytics:** Validate data processing and output generation
- **Data Services:** Test connection handling and async operations
- **Configuration:** Validate YAML structure and required keys

### Confidence Scoring
- **90-100%:** Fully functional and tested
- **70-89%:** Basic functionality present but needs refinement
- **50-69%:** Started but significant issues remain
- **0-49%:** Not ready or missing critical components

---

**🎯 This enhanced validation significantly reduces false positives by testing actual functionality rather than just file existence.**
"""

        return report

    def save_report(self, output_path: Optional[str] = None):
        """Save detailed validation report"""
        if output_path is None:
            output_path = self.status_file

        report = self.generate_detailed_report()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"📄 Enhanced validation report saved to: {output_path}")
        return output_path

    def get_completion_status(self, component_name: str, category: str) -> Dict:
        """Get detailed completion status for a specific component"""
        if category not in self.component_validations:
            return {"error": "Category not found"}

        if component_name not in self.component_validations[category]:
            return {"error": "Component not found"}

        config = self.component_validations[category][component_name]
        validation_result = self.validator.validate_component(component_name, config)

        return {
            "component": component_name,
            "category": category,
            "validation_result": validation_result,
            "config": config,
            "validated_at": datetime.now().isoformat()
        }


def main():
    """Command line interface for enhanced progress tracking"""
    import sys

    tracker = EnhancedProgressTracker()

    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        # Generate and save detailed report
        tracker.save_report()
    elif len(sys.argv) > 2 and sys.argv[1] == "--check":
        # Check specific component
        component_name = sys.argv[2]
        category = sys.argv[3] if len(sys.argv) > 3 else "critical_missing"

        result = tracker.get_completion_status(component_name, category)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            validation = result["validation_result"]
            print(f"🔬 Component: {component_name}")
            print(f"📊 Status: {validation['status']} ({validation['confidence']:.1f}%)")
            print(f"✅ Valid: {validation['valid']}")

            if validation["issues"]:
                print("🚨 Issues:")
                for issue in validation["issues"]:
                    print(f"   - {issue}")

            if validation["recommendations"]:
                print("💡 Recommendations:")
                for rec in validation["recommendations"]:
                    print(f"   - {rec}")
    else:
        # Generate report
        tracker.save_report()


if __name__ == "__main__":
    main()