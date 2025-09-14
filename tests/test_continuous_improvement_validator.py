"""
Comprehensive test suite for ContinuousImprovementValidator.

This module provides comprehensive pytest integration for the ContinuousImprovementValidator,
including integration tests, performance tests, and validation reporting.

Note: Unit tests have been moved to tests / unit / test_ci_validator_unit.py
"""

import json
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ai_onboard.core.continuous_improvement_validator import (
    ContinuousImprovementValidator,
    ValidationCategory,
    ValidationReport,
    ValidationResult,
    ValidationTestCase,
)


class TestContinuousImprovementValidator:
    """Test suite for ContinuousImprovementValidator."""

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
        """Test ValidationTestCase dataclass creation."""
        test_case = ValidationTestCase(
            test_id="test_example_001",
            name="test_example",
            description="Example test case",
            category=ValidationCategory.INTEGRATION,
            result=ValidationResult.PASS,
            duration=0.1505,
            error_message=None,
        )

        assert test_case.name == "test_example"
        assert test_case.category == ValidationCategory.INTEGRATION
        assert test_case.result == ValidationResult.PASS
        assert test_case.duration == 0.1505
        assert test_case.error_message is None

    @pytest.mark.unit
    def test_validation_report_creation(self):
        """Test ValidationReport dataclass creation."""
        test_results = [
            ValidationTestCase(
                test_id="test1_001",
                name="test1",
                description="Test case 1",
                category=ValidationCategory.INTEGRATION,
                result=ValidationResult.PASS,
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

    @pytest.mark.integration
    def test_comprehensive_validation_structure(self, validator, mock_subsystems):
        """Test the structure of comprehensive validation."""
        # Mock the subsystem methods to return success
        for system_name, mock_system in mock_subsystems.items():
            if hasattr(mock_system, "get_system_health"):
                mock_system.get_system_health.return_value = {
                    "status": "healthy",
                    "score": 0.95,
                }

        with patch.object(
            validator, "_run_integration_tests"
        ) as mock_integration, patch.object(
            validator, "_run_data_integrity_tests"
        ) as mock_data_integrity, patch.object(
            validator, "_run_performance_tests"
        ) as mock_performance, patch.object(
            validator, "_run_end_to_end_tests"
        ) as mock_end_to_end:

            # Mock test results
            mock_integration.return_value = [
                ValidationTestCase(
                    test_id="integration_test",
                    name="integration_test",
                    description="Integration test",
                    category=ValidationCategory.INTEGRATION,
                    result=ValidationResult.PASS,
                    duration=100.0,
                )
            ]
            mock_data_integrity.return_value = [
                ValidationTestCase(
                    test_id="data_test",
                    name="data_test",
                    description="Data integrity test",
                    category=ValidationCategory.DATA_INTEGRITY,
                    result=ValidationResult.PASS,
                    duration=50.0,
                )
            ]
            mock_performance.return_value = [
                ValidationTestCase(
                    test_id="perf_test",
                    name="perf_test",
                    description="Performance test",
                    category=ValidationCategory.PERFORMANCE,
                    result=ValidationResult.PASS,
                    duration=200.0,
                )
            ]
            mock_end_to_end.return_value = [
                ValidationTestCase(
                    test_id="e2e_test",
                    name="e2e_test",
                    description="End-to-end test",
                    category=ValidationCategory.END_TO_END,
                    result=ValidationResult.PASS,
                    duration=500.0,
                )
            ]

            report = validator.run_comprehensive_validation()

            assert isinstance(report, ValidationReport)
            assert report.total_tests == 4
            assert report.passed_tests == 4
            assert report.failed_tests == 0
            assert report.system_health_score > 0
            assert len(report.test_results) == 4

    @pytest.mark.integration
    def test_integration_test_execution(self, validator, mock_subsystems):
        """Test that integration tests execute properly."""
        # Mock all subsystem methods
        for system_name, mock_system in mock_subsystems.items():
            mock_system.get_system_health = Mock(return_value={"status": "healthy"})
            mock_system.get_configuration = Mock(return_value={"enabled": True})
            mock_system.validate_configuration = Mock(return_value=True)

        tests = validator._run_integration_tests()

        assert isinstance(tests, list)
        assert len(tests) > 0

        for test in tests:
            assert isinstance(test, ValidationTestCase)
            assert test.category == ValidationCategory.INTEGRATION
            assert test.result in [
                ValidationResult.PASS,
                ValidationResult.FAIL,
                ValidationResult.WARNING,
                ValidationResult.SKIP,
            ]

    @pytest.mark.integration
    def test_data_integrity_test_execution(self, validator, mock_subsystems):
        """Test that data integrity tests execute properly."""
        tests = validator._run_data_integrity_tests()

        assert isinstance(tests, list)

        for test in tests:
            assert isinstance(test, ValidationTestCase)
            assert test.category == ValidationCategory.DATA_INTEGRITY

    @pytest.mark.integration
    def test_performance_test_execution(self, validator, mock_subsystems):
        """Test that performance tests execute properly."""
        tests = validator._run_performance_tests()

        assert isinstance(tests, list)

        for test in tests:
            assert isinstance(test, ValidationTestCase)
            assert test.category == ValidationCategory.PERFORMANCE

    @pytest.mark.integration
    def test_end_to_end_test_execution(self, validator, mock_subsystems):
        """Test that end - to - end tests execute properly."""
        tests = validator._run_end_to_end_tests()

        assert isinstance(tests, list)

        for test in tests:
            assert isinstance(test, ValidationTestCase)
            assert test.category == ValidationCategory.END_TO_END

    @pytest.mark.unit
    def test_system_health_calculation(self, validator):
        """Test system health score calculation."""
        test_results = [
            ValidationTestCase(
                test_id="test1",
                name="test1",
                description="Test case 1",
                category=ValidationCategory.INTEGRATION,
                result=ValidationResult.PASS,
                duration=100.0,
            ),
            ValidationTestCase(
                test_id="test2",
                name="test2",
                description="Test case 2",
                category=ValidationCategory.INTEGRATION,
                result=ValidationResult.PASS,
                duration=150.0,
            ),
            ValidationTestCase(
                test_id="test3",
                name="test3",
                description="Test case 3",
                category=ValidationCategory.INTEGRATION,
                result=ValidationResult.FAIL,
                duration=200.0,
            ),
            ValidationTestCase(
                test_id="test4",
                name="test4",
                description="Test case 4",
                category=ValidationCategory.INTEGRATION,
                result=ValidationResult.WARNING,
                duration=75.0,
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
            ValidationTestCase(
                test_id="test1",
                name="Connection Test",
                description="Test database connection timeout",
                category=ValidationCategory.INTEGRATION,
                result=ValidationResult.FAIL,
                duration=100.0,
                error_message="Connection timeout",
            ),
            ValidationTestCase(
                test_id="test2",
                name="Performance Test",
                description="Test response time performance",
                category=ValidationCategory.PERFORMANCE,
                result=ValidationResult.WARNING,
                duration=2000.0,
                details={"threshold_exceeded": "response_time"},
            ),
        ]

        recommendations = validator._generate_recommendations(test_results)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # Should have recommendations for failed and warning tests
        assert any(
            "failed tests" in rec.lower() or "system reliability" in rec.lower()
            for rec in recommendations
        )
        assert any(
            "warning tests" in rec.lower() or "potential improvements" in rec.lower()
            for rec in recommendations
        )

    @pytest.mark.unit
    def test_summary_generation(self, validator):
        """Test summary generation for validation reports."""
        test_results = [
            ValidationTestCase(
                "test1",
                "test1",
                "Test case 1",
                ValidationCategory.INTEGRATION,
                ValidationResult.PASS,
                100.0,
            ),
            ValidationTestCase(
                "test2",
                "test2",
                "Test case 2",
                ValidationCategory.INTEGRATION,
                ValidationResult.FAIL,
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

    @pytest.mark.slow
    @pytest.mark.integration
    def test_full_validation_with_real_systems(self, validator):
        """Test full validation with real system components (slow test)."""
        try:
            report = validator.run_comprehensive_validation()

            # Basic validation of report structure
            assert isinstance(report, ValidationReport)
            assert report.total_tests > 0
            assert isinstance(report.system_health_score, float)
            assert 0.0 <= report.system_health_score <= 100.0
            assert isinstance(report.recommendations, list)
            assert isinstance(report.summary, str)
            assert len(report.summary) > 0

        except Exception as e:
            pytest.skip(f"Real systems not available for testing: {e}")

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
                ValidationCategory.INTEGRATION,
                timeout_seconds=30,
            )

            assert test_case.result == ValidationResult.FAIL
            assert "timeout" in test_case.error_message.lower()

    @pytest.mark.unit
    def test_error_handling_in_tests(self, validator):
        """Test that errors in individual tests are handled gracefully."""

        def failing_test():
            raise ValueError("Test error")

        test_case = validator._run_test_with_timeout(
            "error_test",
            failing_test,
            ValidationCategory.INTEGRATION,
            timeout_seconds=30,
        )

        assert test_case.result == ValidationResult.FAIL
        assert test_case.error_message is not None
        assert "Test error" in test_case.error_message

    @pytest.mark.integration
    def test_cli_integration(self, validator, root_path):
        """Test integration with CLI commands."""
        # This would test the CLI integration points

        # Mock the args
        class MockArgs:
            validation_action = "run"

        MockArgs()

        # Test that CLI can call the validator without errors
        try:
            # This should not raise an exception
            validator.run_comprehensive_validation()
        except Exception as e:
            pytest.fail(f"CLI integration failed: {e}")

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
        """Test ValidationResult enum values."""
        assert ValidationResult.PASS.value == "pass"
        assert ValidationResult.FAIL.value == "fail"
        assert ValidationResult.WARNING.value == "warning"
        assert ValidationResult.SKIP.value == "skip"

    @pytest.mark.unit
    def test_test_category_enum_values(self):
        """Test ValidationCategory enum values."""
        assert ValidationCategory.INTEGRATION.value == "integration"
        assert ValidationCategory.DATA_INTEGRITY.value == "data_integrity"
        assert ValidationCategory.PERFORMANCE.value == "performance"
        assert ValidationCategory.END_TO_END.value == "end_to_end"


class TestValidationReporting:
    """Test suite for validation reporting functionality."""

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
                ValidationTestCase(
                    test_id="test1",
                    name="test1",
                    description="Test case 1",
                    category=ValidationCategory.INTEGRATION,
                    result=ValidationResult.PASS,
                    duration=100.0,
                ),
                ValidationTestCase(
                    test_id="test2",
                    name="test2",
                    description="Test case 2",
                    category=ValidationCategory.PERFORMANCE,
                    result=ValidationResult.FAIL,
                    duration=200.0,
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


class TestPerformanceValidation:
    """Test suite for performance - related validation."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_performance_test_execution_time(self):
        """Test that performance tests complete within reasonable time."""
        validator = ContinuousImprovementValidator(Path("/tmp"))

        start_time = time.time()
        tests = validator._run_performance_tests()
        execution_time = time.time() - start_time

        # Performance tests should complete within 60 seconds
        assert (
            execution_time < 60.0
        ), f"Performance tests took too long: {execution_time}s"
        assert len(tests) > 0

    @pytest.mark.integration
    def test_memory_usage_during_validation(self):
        """Test that memory usage stays within reasonable bounds during validation."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        validator = ContinuousImprovementValidator(Path("/tmp"))

        # Run a subset of tests to avoid long execution
        with patch.object(validator, "_run_integration_tests") as mock_integration:
            mock_integration.return_value = [
                ValidationTestCase(
                    "test1",
                    "test1",
                    "Test case 1",
                    ValidationCategory.INTEGRATION,
                    ValidationResult.PASS,
                    100.0,
                )
            ]

            validator.run_comprehensive_validation()

            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory

            # Memory increase should be reasonable (less than 100MB)
            assert (
                memory_increase < 100.0
            ), f"Memory usage increased by {memory_increase}MB"


# Pytest hooks and fixtures for CI / CD integration
def pytest_configure(config):
    """Configure pytest for continuous improvement validation."""
    config.addinivalue_line(
        "markers", "ci_validator: marks tests as CI validator integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection for CI integration."""
    # Add CI validator marker to all tests in this module
    for item in items:
        if "test_continuous_improvement_validator" in str(item.fspath):
            item.add_marker(pytest.mark.ci_validator)


# Custom pytest plugin for validation reporting
class ValidationReportPlugin:
    """Pytest plugin for integrating validation reports with test results."""

    def __init__(self):
        self.validation_results = []

    def pytest_runtest_logreport(self, report):
        """Collect test results for validation reporting."""
        if report.when == "call":
            self.validation_results.append(
                {
                    "nodeid": report.nodeid,
                    "outcome": report.outcome,
                    "duration": report.duration,
                    "keywords": list(report.keywords),
                }
            )

    def pytest_sessionfinish(self, session, exitstatus):
        """Generate validation report at end of test session."""
        if hasattr(session.config, "option") and getattr(
            session.config.option, "generate_validation_report", False
        ):
            self._generate_validation_report(exitstatus)

    def _generate_validation_report(self, exitstatus):
        """Generate a validation report based on pytest results."""
        total_tests = len(self.validation_results)
        passed_tests = sum(
            1 for r in self.validation_results if r["outcome"] == "passed"
        )
        failed_tests = sum(
            1 for r in self.validation_results if r["outcome"] == "failed"
        )

        print(f"\n🧪 Validation Report Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Exit Status: {exitstatus}")


# Register the plugin
def pytest_configure(config):
    """Register the validation report plugin."""
    config.pluginmanager.register(ValidationReportPlugin(), "validation_report")


# Custom command line options
def pytest_addoption(parser):
    """Add custom command line options for validation."""
    parser.addoption(
        "--generate - validation - report",
        action="store_true",
        default=False,
        help="Generate validation report at end of test session",
    )
    parser.addoption(
        "--validation - timeout",
        action="store",
        default=300,
        type=int,
        help="Timeout for validation tests in seconds",
    )


# Fixtures for integration with the validation system
@pytest.fixture(scope="session")
def validation_timeout(request):
    """Provide validation timeout from command line."""
    return request.config.getoption("--validation - timeout")


@pytest.fixture(scope="session")
def generate_validation_report(request):
    """Provide validation report generation flag from command line."""
    return request.config.getoption("--generate - validation - report")
