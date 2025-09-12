"""
Unit tests for ContinuousImprovementValidator.

This module contains focused unit tests for the ContinuousImprovementValidator
class, testing individual methods and components in isolation.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

from ai_onboard.core.continuous_improvement_validator import (
    ContinuousImprovementValidator,
    TestCase,
    TestCategory,
    TestResult,
    ValidationReport,
)


class TestContinuousImprovementValidatorUnit:
    """Unit tests for ContinuousImprovementValidator."""

    @pytest.fixture
    def root_path(self, tmp_path):
        """Provide a temporary root path for testing."""
        return tmp_path

    @pytest.fixture
    def validator(self, root_path):
        """Create a ContinuousImprovementValidator instance for testing."""
        return ContinuousImprovementValidator(root_path)

    @pytest.fixture
    def mock_subsystems(self):
        """Mock all subsystems to avoid dependencies during unit tests."""
        with patch.multiple(
            "ai_onboard.core.continuous_improvement_validator",
            continuous_improvement_system=Mock(),
            performance_optimizer=Mock(),
            adaptive_config_manager=Mock(),
            user_preference_learning=Mock(),
            system_health_monitor=Mock(),
            knowledge_base_evolution=Mock(),
            continuous_improvement_analytics=Mock(),
        ) as mocks:
            yield mocks

    def test_validator_initialization(self, validator, root_path):
        """Test that validator initializes correctly."""
        assert validator.root == root_path
        assert (
            validator.validation_path
            == root_path / ".ai_onboard" / "validation_reports.jsonl"
        )
        assert (
            validator.test_config_path == root_path / ".ai_onboard" / "test_config.json"
        )
        assert isinstance(validator.test_config, dict)

    def test_test_config_loading(self, validator):
        """Test that test configuration loads with proper defaults."""
        config = validator.test_config

        # Check required configuration keys
        assert "test_timeout_seconds" in config
        assert "performance_thresholds" in config
        assert "data_integrity_checks" in config
        assert "integration_tests" in config
        assert "performance_tests" in config
        assert "end_to_end_tests" in config

        # Check performance thresholds
        thresholds = config["performance_thresholds"]
        assert "response_time_ms" in thresholds
        assert "memory_usage_mb" in thresholds
        assert "cpu_usage_percent" in thresholds

    @pytest.mark.unit
    def test_test_case_creation(self):
        """Test TestCase dataclass creation."""
        test_case = TestCase(
            test_id="test_example_001",
            name="test_example",
            description="Example test case",
            category=TestCategory.INTEGRATION,
            result=TestResult.PASS,
            duration=0.1505,
            error_message=None,
        )

        assert test_case.name == "test_example"
        assert test_case.category == TestCategory.INTEGRATION
        assert test_case.result == TestResult.PASS
        assert test_case.duration == 0.1505
        assert test_case.error_message is None

    @pytest.mark.unit
    def test_validation_report_creation(self):
        """Test ValidationReport dataclass creation."""
        test_results = [
            TestCase(
                test_id="test1_001",
                name="test1",
                description="Test case 1",
                category=TestCategory.INTEGRATION,
                result=TestResult.PASS,
                duration=0.1,
            )
        ]

        report = ValidationReport(
            report_id="test_report_123",
            generated_at=datetime.now(),
            total_tests=1,
            passed_tests=1,
            failed_tests=0,
            warning_tests=0,
            skipped_tests=0,
            test_results=test_results,
            system_health_score=95.0,
            recommendations=["All systems healthy"],
            summary="All tests passed successfully",
        )

        assert report.total_tests == 1
        assert report.passed_tests == 1
        assert report.system_health_score == 95.0
        assert len(report.recommendations) == 1

    @pytest.mark.unit
    def test_system_health_calculation(self, validator):
        """Test system health score calculation."""
        test_results = [
            TestCase(
                "test1",
                "test1",
                "Test case 1",
                TestCategory.INTEGRATION,
                TestResult.PASS,
                100.0,
            ),
            TestCase(
                "test2",
                "test2",
                "Test case 2",
                TestCategory.INTEGRATION,
                TestResult.PASS,
                150.0,
            ),
            TestCase(
                "test3",
                "test3",
                "Test case 3",
                TestCategory.INTEGRATION,
                TestResult.FAIL,
                200.0,
            ),
            TestCase(
                "test4",
                "test4",
                "Test case 4",
                TestCategory.INTEGRATION,
                TestResult.WARNING,
                75.0,
            ),
        ]

        health_score = validator._calculate_system_health_score(test_results)

        assert isinstance(health_score, float)
        assert 0.0 <= health_score <= 100.0
        # With 2 passes, 1 fail, 1 warning, score should be moderate
        assert 40.0 <= health_score <= 70.0

    @pytest.mark.unit
    def test_recommendation_generation(self, validator):
        """Test that recommendations are generated based on test results."""
        test_results = [
            TestCase(
                "test1",
                TestCategory.INTEGRATION,
                TestResult.FAIL,
                100.0,
                error_message="Connection timeout",
            ),
            TestCase(
                "test2",
                TestCategory.PERFORMANCE,
                TestResult.WARNING,
                2000.0,
                details={"threshold_exceeded": "response_time"},
            ),
        ]

        recommendations = validator._generate_recommendations(test_results)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # Should have recommendations for failed and warning tests
        assert any(
            "timeout" in rec.lower() or "connection" in rec.lower()
            for rec in recommendations
        )
        assert any(
            "performance" in rec.lower() or "response" in rec.lower()
            for rec in recommendations
        )

    @pytest.mark.unit
    def test_summary_generation(self, validator):
        """Test summary generation for validation reports."""
        test_results = [
            TestCase(
                "test1",
                "test1",
                "Test case 1",
                TestCategory.INTEGRATION,
                TestResult.PASS,
                100.0,
            ),
            TestCase(
                "test2",
                "test2",
                "Test case 2",
                TestCategory.INTEGRATION,
                TestResult.FAIL,
                150.0,
            ),
        ]

        summary = validator._generate_summary(test_results, 75.0)

        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "75.0" in summary  # Health score should be mentioned
        assert "2" in summary  # Total tests should be mentioned

    @pytest.mark.unit
    def test_validation_report_persistence(self, validator, root_path):
        """Test that validation reports are saved correctly."""
        report = ValidationReport(
            report_id="test_report_123",
            generated_at=datetime.now(),
            total_tests=2,
            passed_tests=1,
            failed_tests=1,
            warning_tests=0,
            skipped_tests=0,
            test_results=[],
            system_health_score=75.0,
            recommendations=["Fix failed test"],
            summary="Mixed results",
        )

        validator._save_validation_report(report)

        # Check that report file exists
        assert validator.validation_path.exists()

        # Read and verify content
        with open(validator.validation_path, "r") as f:
            lines = f.readlines()
            assert len(lines) >= 1

            # Parse the last line (most recent report)
            report_data = json.loads(lines[-1])
            assert report_data["report_id"] == "test_report_123"
            assert report_data["total_tests"] == 2
            assert report_data["system_health_score"] == 75.0

    @pytest.mark.unit
    def test_test_timeout_handling(self, validator):
        """Test that test timeouts are handled properly."""
        # Mock a test that takes too long
        with patch("time.time") as mock_time:
            mock_time.side_effect = [0, 35]  # 35 seconds elapsed

            # This should trigger timeout handling
            test_case = validator._run_test_with_timeout(
                "timeout_test",
                lambda: time.sleep(40),  # Function that would take 40 seconds
                TestCategory.INTEGRATION,
                timeout_seconds=30,
            )

            assert test_case.result == TestResult.FAIL
            assert "timeout" in test_case.error_message.lower()

    @pytest.mark.unit
    def test_error_handling_in_tests(self, validator):
        """Test that errors in individual tests are handled gracefully."""

        def failing_test():
            raise ValueError("Test error")

        test_case = validator._run_test_with_timeout(
            "error_test", failing_test, TestCategory.INTEGRATION, timeout_seconds=30
        )

        assert test_case.result == TestResult.FAIL
        assert test_case.error_message is not None
        assert "ValueError" in test_case.error_message
        assert "Test error" in test_case.error_message

    @pytest.mark.unit
    def test_test_configuration_validation(self, validator):
        """Test that test configuration is validated properly."""
        config = validator.test_config

        # Required configuration keys should be present
        required_keys = [
            "test_timeout_seconds",
            "performance_thresholds",
            "data_integrity_checks",
            "integration_tests",
            "performance_tests",
            "end_to_end_tests",
        ]

        for key in required_keys:
            assert key in config, f"Missing required config key: {key}"

        # Performance thresholds should have required keys
        thresholds = config["performance_thresholds"]
        threshold_keys = ["response_time_ms", "memory_usage_mb", "cpu_usage_percent"]

        for key in threshold_keys:
            assert key in thresholds, f"Missing performance threshold: {key}"
            assert isinstance(thresholds[key], (int, float))

    @pytest.mark.unit
    def test_test_result_enum_values(self):
        """Test TestResult enum values."""
        assert TestResult.PASS.value == "pass"
        assert TestResult.FAIL.value == "fail"
        assert TestResult.WARNING.value == "warning"
        assert TestResult.SKIP.value == "skip"

    @pytest.mark.unit
    def test_test_category_enum_values(self):
        """Test TestCategory enum values."""
        assert TestCategory.INTEGRATION.value == "integration"
        assert TestCategory.DATA_INTEGRITY.value == "data_integrity"
        assert TestCategory.PERFORMANCE.value == "performance"
        assert TestCategory.END_TO_END.value == "end_to_end"


class TestValidationReporting:
    """Unit tests for validation reporting functionality."""

    @pytest.fixture
    def sample_report(self):
        """Create a sample validation report for testing."""
        return ValidationReport(
            report_id="sample_report_123",
            generated_at=datetime.now(),
            total_tests=10,
            passed_tests=7,
            failed_tests=2,
            warning_tests=1,
            skipped_tests=0,
            test_results=[
                TestCase(
                    "test1",
                    "test1",
                    "Test case 1",
                    TestCategory.INTEGRATION,
                    TestResult.PASS,
                    100.0,
                ),
                TestCase(
                    "test2",
                    "test2",
                    "Test case 2",
                    TestCategory.PERFORMANCE,
                    TestResult.FAIL,
                    200.0,
                    error_message="Performance threshold exceeded",
                ),
            ],
            system_health_score=78.5,
            recommendations=[
                "Investigate performance issues",
                "Review failed integration tests",
            ],
            summary="System health is good with some areas for improvement",
        )

    @pytest.mark.unit
    def test_report_serialization(self, sample_report):
        """Test that reports can be serialized to JSON."""
        # The validator should be able to serialize reports
        validator = ContinuousImprovementValidator(Path("/tmp"))

        serialized = validator._serialize_report(sample_report)

        assert isinstance(serialized, dict)
        assert serialized["report_id"] == "sample_report_123"
        assert serialized["total_tests"] == 10
        assert serialized["system_health_score"] == 78.5
        assert len(serialized["recommendations"]) == 2

    @pytest.mark.unit
    def test_report_formatting(self, sample_report):
        """Test that reports are formatted correctly for display."""
        validator = ContinuousImprovementValidator(Path("/tmp"))

        # Test that the report can be printed without errors
        try:
            validator._print_validation_results(sample_report)
        except Exception as e:
            pytest.fail(f"Report formatting failed: {e}")


class TestValidatorHelperMethods:
    """Unit tests for validator helper methods."""

    @pytest.fixture
    def validator(self, tmp_path):
        """Create validator instance for testing."""
        return ContinuousImprovementValidator(tmp_path)

    @pytest.mark.unit
    def test_test_case_factory_method(self, validator):
        """Test helper method for creating test cases."""
        test_case = validator._create_test_case(
            name="helper_test",
            category=TestCategory.INTEGRATION,
            result=TestResult.PASS,
            duration=150.0,
            error_message=None,
        )

        assert isinstance(test_case, TestCase)
        assert test_case.name == "helper_test"
        assert test_case.category == TestCategory.INTEGRATION
        assert test_case.result == TestResult.PASS
        assert test_case.duration == 150.0

    @pytest.mark.unit
    def test_metric_threshold_validation(self, validator):
        """Test validation of performance metric thresholds."""
        thresholds = validator.test_config["performance_thresholds"]

        # Test that threshold validation works
        test_metrics = {
            "response_time_ms": 250,  # Under threshold
            "memory_usage_mb": 100,  # Over threshold
            "cpu_usage_percent": 45,  # Under threshold
        }

        violations = validator._check_threshold_violations(test_metrics, thresholds)

        assert isinstance(violations, list)
        # Should detect memory usage violation
        assert any("memory" in str(v).lower() for v in violations)

    @pytest.mark.unit
    def test_report_id_generation(self, validator):
        """Test that report IDs are generated correctly."""
        report_id = validator._generate_report_id()

        assert isinstance(report_id, str)
        assert len(report_id) > 0
        assert "validation_" in report_id

        # Should be unique
        report_id2 = validator._generate_report_id()
        assert report_id != report_id2


# Helper functions for unit testing
def create_mock_test_case(
    name: str,
    result: TestResult,
    duration: float = 100.0,
    category: TestCategory = TestCategory.INTEGRATION,
    error_message: Optional[str] = None,
) -> TestCase:
    """Create a mock test case for testing purposes."""
    return TestCase(
        test_id=f"mock_{name}",
        name=name,
        description=f"Mock test case: {name}",
        category=category,
        result=result,
        duration=duration,
        error_message=error_message,
    )


def create_mock_validation_report(test_results: List[TestCase]) -> ValidationReport:
    """Create a mock validation report for testing purposes."""
    total_tests = len(test_results)
    passed_tests = sum(1 for t in test_results if t.result == TestResult.PASS)
    failed_tests = sum(1 for t in test_results if t.result == TestResult.FAIL)
    warning_tests = sum(1 for t in test_results if t.result == TestResult.WARNING)
    skipped_tests = sum(1 for t in test_results if t.result == TestResult.SKIP)

    health_score = (passed_tests / total_tests * 100.0) if total_tests > 0 else 0.0

    return ValidationReport(
        report_id=f"mock_report_{int(time.time())}",
        generated_at=datetime.now(),
        total_tests=total_tests,
        passed_tests=passed_tests,
        failed_tests=failed_tests,
        warning_tests=warning_tests,
        skipped_tests=skipped_tests,
        test_results=test_results,
        system_health_score=health_score,
        recommendations=[],
        summary=f"Mock report with {total_tests} tests",
    )


if __name__ == "__main__":
    # Run unit tests
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(Path(__file__)),
            "-v",
            "--tb=short",
            "-m",
            "unit",
        ],
        capture_output=True,
        text=True,
    )

    print("🧪 CI Validator Unit Test Results")
    print("=" * 50)
    print(f"Success: {'✅' if result.returncode == 0 else '❌'}")

    if result.stdout:
        print("\nOutput:")
        print(result.stdout)

    if result.stderr:
        print("\nErrors:")
        print(result.stderr)

    exit(result.returncode)
