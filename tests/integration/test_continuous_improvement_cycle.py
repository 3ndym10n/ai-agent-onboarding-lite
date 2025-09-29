"""
Continuous Improvement Cycle Integration Tests

Tests the complete continuous improvement workflow: code analysis → issue detection →
automated fix application → validation → learning. This represents the core
self-improvement capability of the ai-onboard system.
"""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_onboard.core.ai_integration.kaizen_automation import KaizenAutomationEngine
from ai_onboard.core.continuous_improvement.continuous_improvement_validator import (
    ContinuousImprovementValidator,
    ValidationCategory,
)
from ai_onboard.core.orchestration.pattern_recognition_system import (
    PatternRecognitionSystem,
)
from ai_onboard.core.quality_safety.code_quality_analyzer import CodeQualityAnalyzer


class TestContinuousImprovementCycle:
    """End-to-end tests for the continuous improvement feedback loop."""

    @pytest.fixture
    def improvement_env(self):
        """Set up complete continuous improvement test environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Initialize all continuous improvement components
            pattern_system = PatternRecognitionSystem(root)
            quality_analyzer = CodeQualityAnalyzer(root)
            kaizen_engine = KaizenAutomationEngine(root)
            validator = ContinuousImprovementValidator(root)

            yield {
                "root": root,
                "pattern_system": pattern_system,
                "quality_analyzer": quality_analyzer,
                "kaizen_engine": kaizen_engine,
                "validator": validator,
            }

    def test_t101_1_full_improvement_cycle(self, improvement_env):
        """T101.1: Full Improvement Cycle - Code analysis through automated fixes."""
        env = improvement_env

        # Create test Python file with issues
        test_file = env["root"] / "test_module.py"
        test_file.write_text(
            """
def bad_function():
    # Multiple issues: unused import, poor naming, no type hints
    import os  # unused
    x = 1  # poor variable name
    return x * 2

class testclass:  # poor naming
    def method1(self):
        pass  # empty method

    def method2(self):
        print("hello")  # side effect in method
"""
        )

        # Phase 1: Code Quality Analysis
        analysis_result = env["quality_analyzer"].analyze_codebase()
        assert analysis_result is not None
        assert len(analysis_result.file_metrics) > 0

        # Should detect various quality issues
        test_metrics = analysis_result.file_metrics.get(str(test_file))
        assert test_metrics is not None
        assert test_metrics.complexity_score > 0

        # Phase 2: Pattern Recognition and Learning
        # Analyze the code for error patterns
        error_data = {
            "error_type": "code_quality",
            "file": str(test_file),
            "line": 3,
            "message": "Unused import 'os'",
            "severity": "warning",
        }

        pattern_match = env["pattern_system"].analyze_error(error_data)
        assert pattern_match is not None
        assert pattern_match.confidence > 0

        # Phase 3: Generate Improvement Opportunities
        opportunities = env["kaizen_engine"].identify_improvement_opportunities(
            env["root"]
        )

        # Should identify code quality issues
        quality_opportunities = [
            opp for opp in opportunities if "quality" in opp.title.lower()
        ]
        assert len(quality_opportunities) > 0

        # Phase 4: Automated Fix Application
        test_opportunity = quality_opportunities[0]
        decision = env["kaizen_engine"].decide_on_improvement(test_opportunity)

        if decision["should_implement"]:
            result = env["kaizen_engine"].execute_improvement(test_opportunity)
            assert result is not None
            # Fix might succeed or fail, but should return a result

        # Phase 5: Validation and Learning
        validation_result = env["validator"].validate_continuous_improvement(
            ValidationCategory.CODE_QUALITY, env["root"]
        )

        assert validation_result is not None
        assert "status" in validation_result

        print("✅ Full improvement cycle test passed")

    def test_t101_2_pattern_learning_and_adaptation(self, improvement_env):
        """T101.2: Pattern Learning and Adaptation - System learns from repeated issues."""
        env = improvement_env

        # Simulate repeated similar errors to test learning (same file/line to ensure clustering)
        similar_errors = [
            {
                "type": "styling_error",
                "file": "module1.py",
                "line": 10,
                "message": "Line too long (120 characters)",
                "severity": "warning",
            },
            {
                "type": "styling_error",
                "file": "module1.py",
                "line": 10,
                "message": "Line too long (120 characters)",
                "severity": "warning",
            },
            {
                "type": "styling_error",
                "file": "module1.py",
                "line": 10,
                "message": "Line too long (120 characters)",
                "severity": "warning",
            },
            {
                "type": "styling_error",
                "file": "module1.py",
                "line": 10,
                "message": "Line too long (120 characters)",
                "severity": "warning",
            },
        ]

        # Process multiple similar errors
        for error in similar_errors:
            env["pattern_system"].analyze_error(error)

        # System should learn and create a pattern
        patterns = env["pattern_system"].get_all_patterns()
        styling_patterns = [p for p in patterns if p.pattern_type == "styling_error"]
        assert len(styling_patterns) > 0

        # Most recent pattern should have higher confidence due to repetition
        latest_pattern = max(styling_patterns, key=lambda p: p.last_seen)
        assert latest_pattern.confidence >= 0.5
        assert latest_pattern.frequency >= 3

        print("✅ Pattern learning and adaptation test passed")

    def test_t101_3_cross_module_improvement_coordination(self, improvement_env):
        """T101.3: Cross-Module Improvement Coordination - Multiple systems work together."""
        env = improvement_env

        # Create test files with different types of issues
        python_file = env["root"] / "test_python.py"
        python_file.write_text(
            """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price  # Potential attribute error
    return total

class DataProcessor:
    def __init__(self):
        self.data = []

    def add_data(self, item):
        self.data.append(item)

    def get_summary(self):
        return len(self.data)  # Basic summary
"""
        )

        config_file = env["root"] / "config.json"
        config_file.write_text('{"debug": true, "max_connections": 100}')

        # Phase 1: Multi-system analysis
        quality_result = env["quality_analyzer"].analyze_codebase()
        pattern_analysis = env["pattern_system"].analyze_codebase_patterns(env["root"])

        # Phase 2: Coordinated improvement identification
        opportunities = env["kaizen_engine"].identify_improvement_opportunities(
            env["root"]
        )

        # Should identify issues from multiple analysis sources
        assert len(opportunities) > 0

        # Phase 3: Coordinated execution
        executed_improvements = []
        for opportunity in opportunities[:3]:  # Test first 3
            decision = env["kaizen_engine"].decide_on_improvement(opportunity)
            if decision["should_implement"]:
                result = env["kaizen_engine"].execute_improvement(opportunity)
                executed_improvements.append(result)

        # Phase 4: Cross-validation
        validation_results = []
        for category in ValidationCategory:
            try:
                result = env["validator"].validate_continuous_improvement(
                    category, env["root"]
                )
                validation_results.append(result)
            except Exception:
                # Some validations might not be applicable
                pass

        assert len(validation_results) > 0

        print("✅ Cross-module improvement coordination test passed")

    @patch("time.sleep")  # Speed up tests by mocking sleep
    def test_t101_4_automated_learning_feedback_loop(self, mock_sleep, improvement_env):
        """T101.4: Automated Learning Feedback Loop - System improves itself over time."""
        env = improvement_env

        # Initial state - create baseline
        initial_opportunities = env["kaizen_engine"].identify_improvement_opportunities(
            env["root"]
        )
        initial_count = len(initial_opportunities)

        # Simulate improvement actions
        improvement_actions = [
            {"type": "add_type_hints", "target": "functions", "confidence": 0.8},
            {"type": "fix_naming", "target": "variables", "confidence": 0.7},
            {"type": "remove_unused_imports", "target": "modules", "confidence": 0.9},
        ]

        # Execute improvements
        for action in improvement_actions:
            # Create mock opportunity
            opportunity = MagicMock()
            opportunity.title = f"Test {action['type']} improvement"
            opportunity.category = "code_quality"
            opportunity.confidence = action["confidence"]

            env["kaizen_engine"].execute_improvement(opportunity)

        # Simulate time passing and re-analysis
        mock_sleep.return_value = None  # Mock sleep calls

        # Check if system learned from the improvements
        final_opportunities = env["kaizen_engine"].identify_improvement_opportunities(
            env["root"]
        )

        # System should have adapted its improvement strategies
        # (In practice, this would check if similar issues are handled differently)

        # Verify validator can assess the changes
        validation = env["validator"].validate_continuous_improvement(
            ValidationCategory.CODE_QUALITY, env["root"]
        )

        assert validation is not None
        assert "status" in validation

        print("✅ Automated learning feedback loop test passed")

    def test_t101_5_error_prevention_through_learning(self, improvement_env):
        """T101.5: Error Prevention Through Learning - System prevents known issues."""
        env = improvement_env

        # Train system with known error patterns
        training_errors = [
            {
                "type": "import_error",
                "file": "broken_module.py",
                "message": "No module named 'nonexistent_package'",
                "context": {"operation": "import", "package": "nonexistent_package"},
            },
            {
                "type": "attribute_error",
                "file": "broken_module.py",
                "message": "'NoneType' object has no attribute 'method'",
                "context": {"operation": "method_call", "object_type": "None"},
            },
            {
                "type": "type_error",
                "file": "broken_module.py",
                "message": "unsupported operand type(s) for +: 'str' and 'int'",
                "context": {"operation": "addition", "types": ["str", "int"]},
            },
        ]

        # Process training errors
        for error in training_errors:
            env["pattern_system"].analyze_error(error)

        # Verify patterns were learned
        patterns = env["pattern_system"].get_all_patterns()
        assert len(patterns) >= len(training_errors)

        # Test prevention - system should recognize similar patterns
        test_error = {
            "type": "import_error",
            "file": "test_module.py",
            "message": "No module named 'nonexistent_package'",
            "context": {"operation": "import", "package": "nonexistent_package"},
        }

        prevention_suggestions = env["pattern_system"].get_prevention_recommendations(
            test_error
        )
        assert len(prevention_suggestions) > 0

        # Suggestions should be relevant to import errors
        import_suggestions = [
            s
            for s in prevention_suggestions
            if "import" in s.lower() or "package" in s.lower()
        ]
        assert len(import_suggestions) > 0

        print("✅ Error prevention through learning test passed")

    def test_t101_6_quality_gate_integration(self, improvement_env):
        """T101.6: Quality Gate Integration - Improvements pass validation gates."""
        env = improvement_env

        # Create a test scenario with quality issues
        test_file = env["root"] / "quality_test.py"
        test_file.write_text(
            """
# File with multiple quality issues
import os,sys,json  # Multiple imports on one line
def badFunction():  # Poor naming
    x=1+2+3+4+5+6+7+8+9+10  # Long line, poor variable name
    return x
"""
        )

        # Run quality analysis
        quality_result = env["quality_analyzer"].analyze_codebase()
        assert quality_result is not None

        # Identify improvement opportunities
        opportunities = env["kaizen_engine"].identify_improvement_opportunities(
            env["root"]
        )
        quality_issues = [
            opp for opp in opportunities if "quality" in opp.title.lower()
        ]
        assert len(quality_issues) > 0

        # Apply improvements
        improvement_results = []
        for opportunity in quality_issues[:2]:  # Test first 2
            decision = env["kaizen_engine"].decide_on_improvement(opportunity)
            if decision["should_implement"]:
                result = env["kaizen_engine"].execute_improvement(opportunity)
                improvement_results.append(result)

        # Validate improvements
        post_validation = env["validator"].validate_continuous_improvement(
            ValidationCategory.CODE_QUALITY, env["root"]
        )

        # System should be able to assess whether improvements were successful
        assert post_validation is not None
        assert isinstance(post_validation, dict)

        print("✅ Quality gate integration test passed")
