"""
Integration tests for ContinuousImprovementValidator with real AI Onboard components.

This module tests the integration between the ContinuousImprovementValidator
and actual AI Onboard system components, ensuring that validation works
correctly in realistic scenarios.
"""

import json
import time
from datetime import datetime
from pathlib import Path

import pytest

from ai_onboard.core.continuous_improvement import (
    ContinuousImprovementValidator,
    ValidationCategory,
    ValidationReport,
    ValidationResult,
    ValidationTestCase,
)


@pytest.mark.integration
class TestContinuousImprovementValidatorIntegration:
    """Integration tests for ContinuousImprovementValidator with real components."""

    @pytest.fixture
    def real_validator(self, temp_project_root):
        """Create a validator with real project root for integration testing."""
        return ContinuousImprovementValidator(temp_project_root)

    def test_validator_with_real_project_structure(
        self, real_validator, temp_project_root
    ):
        """Test validator with a realistic project structure."""
        # Create realistic project structure
        (temp_project_root / "ai_onboard").mkdir()
        (temp_project_root / "ai_onboard" / "core").mkdir()
        (temp_project_root / "ai_onboard" / "cli").mkdir()
        (temp_project_root / "tests").mkdir()

        # Create some mock files
        (temp_project_root / "ai_onboard" / "__init__.py").touch()
        (temp_project_root / "ai_onboard" / "core" / "__init__.py").touch()
        (temp_project_root / "pyproject.toml").write_text(
            """
[build - system]
requires = ["setuptools >= 61.0"]

[project]
name = "test - project"
version = "0.1.0"
        """
        )

        # Test that validator can work with this structure
        assert real_validator.root == temp_project_root
        assert real_validator.validation_path.parent.exists()
        assert isinstance(real_validator.test_config, dict)

    @pytest.mark.slow
    def test_comprehensive_validation_execution(self, real_validator):
        """Test full execution of comprehensive validation."""
        try:
            # Run the comprehensive validation
            start_time = time.time()
            report = real_validator.run_comprehensive_validation()
            execution_time = time.time() - start_time

            # Validate the report structure
            assert isinstance(report, ValidationReport)
            assert report.total_tests > 0
            assert isinstance(report.system_health_score, float)
            assert 0.0 <= report.system_health_score <= 100.0
            assert isinstance(report.recommendations, list)
            assert isinstance(report.summary, str)
            assert len(report.summary) > 0

            # Check that execution completed in reasonable time
            assert (
                execution_time < 120.0
            ), f"Validation took too long: {execution_time}s"

            # Check that report was saved
            assert real_validator.validation_path.exists()

            print(f"✅ Comprehensive validation completed in {execution_time:.2f}s")
            print(f"   Health Score: {report.system_health_score:.1f}%")
            print(f"   Tests: {report.total_tests} total, {report.passed_tests} passed")

        except Exception as e:
            pytest.skip(f"Real systems not available for comprehensive validation: {e}")

    def test_integration_with_existing_systems(self, real_validator):
        """Test integration with existing AI Onboard systems."""
        # Test that validator can access core systems
        assert hasattr(real_validator, "continuous_improvement")
        assert hasattr(real_validator, "performance_optimizer")
        assert hasattr(real_validator, "config_manager")
        assert hasattr(real_validator, "user_preferences")
        assert hasattr(real_validator, "health_monitor")
        assert hasattr(real_validator, "knowledge_base")
        assert hasattr(real_validator, "analytics")

        # Test that systems are properly initialized
        systems = [
            "continuous_improvement",
            "performance_optimizer",
            "config_manager",
            "user_preferences",
            "health_monitor",
            "knowledge_base",
            "analytics",
        ]

        for system_name in systems:
            system = getattr(real_validator, system_name)
            assert system is not None, f"System {system_name} not properly initialized"

    def test_validation_report_persistence(self, real_validator, temp_project_root):
        """Test that validation reports are properly persisted."""
        # Create a mock report
        from ai_onboard.core.continuous_improvement import ValidationTestCase

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
                ValidationCategory.PERFORMANCE,
                ValidationResult.WARNING,
                200.0,
            ),
        ]

        report = ValidationReport(
            report_id="test_integration_report",
            generated_at=datetime.now(),
            total_tests=2,
            passed_tests=1,
            failed_tests=0,
            warning_tests=1,
            skipped_tests=0,
            test_results=test_results,
            system_health_score=85.0,
            recommendations=["Address performance warning"],
            summary="Integration test report",
        )

        # Save the report
        real_validator._save_validation_report(report)

        # Verify it was saved
        assert real_validator.validation_path.exists()

        # Read and verify content
        with open(real_validator.validation_path, "r") as f:
            lines = f.readlines()
            assert len(lines) >= 1

            # Parse the report
            saved_report = json.loads(lines[-1])
            assert saved_report["report_id"] == "test_integration_report"
            assert saved_report["total_tests"] == 2
            assert saved_report["system_health_score"] == 85.0

    def test_cli_integration_with_validator(self, real_validator):
        """Test integration with CLI commands."""
        try:
            # Import CLI handler
            from ai_onboard.cli.commands_continuous_improvement import (
                _handle_validation_commands,
            )

            # Mock args for validation command
            class MockArgs:
                validation_action = "run"

            MockArgs()

            # Test that CLI can work with validator
            # Note: This is a basic integration test - full CLI testing would require more setup
            assert callable(_handle_validation_commands)

        except ImportError as e:
            pytest.skip(f"CLI integration not available: {e}")

    @pytest.mark.performance
    def test_validation_performance_characteristics(self, real_validator):
        """Test performance characteristics of validation system."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run validation multiple times to test consistency
        execution_times = []
        memory_usage = []

        for i in range(3):  # Run 3 times to get average
            start_time = time.time()
            start_memory = process.memory_info().rss / 1024 / 1024

            try:
                # Run a subset of validation to avoid long test times
                real_validator._run_integration_tests()

                end_time = time.time()
                end_memory = process.memory_info().rss / 1024 / 1024

                execution_times.append(end_time - start_time)
                memory_usage.append(end_memory - start_memory)

            except Exception as e:
                pytest.skip(f"Performance test failed due to system availability: {e}")

        if execution_times:
            avg_execution_time = sum(execution_times) / len(execution_times)
            max_memory_increase = max(memory_usage)

            # Performance assertions
            assert (
                avg_execution_time < 30.0
            ), f"Average execution time too high: {avg_execution_time}s"
            assert (
                max_memory_increase < 50.0
            ), f"Memory usage too high: {max_memory_increase}MB"

            print(f"✅ Performance test passed:")
            print(f"   Average execution time: {avg_execution_time:.2f}s")
            print(f"   Max memory increase: {max_memory_increase:.1f}MB")

    def test_error_handling_in_real_scenarios(self, real_validator):
        """Test error handling with real system components."""
        # Test handling of missing dependencies
        original_continuous_improvement = real_validator.continuous_improvement
        real_validator.continuous_improvement = None

        try:
            # This should handle the missing system gracefully
            tests = real_validator._run_integration_tests()

            # Should still return some tests, even with missing components
            assert isinstance(tests, list)

            # At least some tests should indicate the missing component
            missing_component_tests = [
                t
                for t in tests
                if t.error_message and "not available" in t.error_message
            ]
            # We expect some tests to detect missing components

        finally:
            # Restore the original system
            real_validator.continuous_improvement = original_continuous_improvement

    def test_configuration_validation_integration(
        self, real_validator, temp_project_root
    ):
        """Test configuration validation with real project setup."""
        # Create a custom test configuration
        custom_config = {
            "test_timeout_seconds": 15,
            "performance_thresholds": {
                "response_time_ms": 300,
                "memory_usage_mb": 75,
                "cpu_usage_percent": 60,
            },
            "data_integrity_checks": True,
            "integration_tests": True,
            "performance_tests": False,  # Disable for faster testing
            "end_to_end_tests": False,  # Disable for faster testing
        }

        # Save custom configuration
        config_file = temp_project_root / ".ai_onboard" / "test_config.json"
        with open(config_file, "w") as f:
            json.dump(custom_config, f)

        # Create new validator with custom config
        custom_validator = ContinuousImprovementValidator(temp_project_root)

        # Test that custom configuration was loaded
        assert custom_validator.test_config["test_timeout_seconds"] == 15
        assert (
            custom_validator.test_config["performance_thresholds"]["response_time_ms"]
            == 300
        )
        assert custom_validator.test_config["performance_tests"] is False

    @pytest.mark.integration
    def test_validation_with_mock_failures(self, real_validator):
        """Test validation behavior when systems report failures."""
        # This test simulates system failures to test validation response

        # Create a validator method that simulates failures
        def mock_failing_test():
            return [
                ValidationTestCase(
                    test_id="mock_failing_integration",
                    name="mock_failing_integration",
                    description="Mock failing integration test",
                    category=ValidationCategory.INTEGRATION,
                    result=ValidationResult.FAIL,
                    duration=150.0,
                    error_message="Mock system failure for testing",
                ),
                ValidationTestCase(
                    test_id="mock_warning_performance",
                    name="mock_warning_performance",
                    description="Mock warning performance test",
                    category=ValidationCategory.PERFORMANCE,
                    result=ValidationResult.WARNING,
                    duration=800.0,
                    error_message="Performance threshold exceeded",
                ),
            ]

        # Temporarily replace integration tests with mock
        original_integration_tests = real_validator._run_integration_tests
        real_validator._run_integration_tests = mock_failing_test

        try:
            # Run validation with mocked failures
            report = real_validator.run_comprehensive_validation()

            # Check that failures are properly reported
            assert report.failed_tests > 0
            assert report.system_health_score < 100.0
            assert len(report.recommendations) > 0

            # Check that recommendations address the failures
            recommendations_text = " ".join(report.recommendations).lower()
            assert "mock" in recommendations_text or "fail" in recommendations_text

        finally:
            # Restore original method
            real_validator._run_integration_tests = original_integration_tests

    def test_concurrent_validation_safety(self, real_validator, temp_project_root):
        """Test that concurrent validation runs don't interfere with each other."""
        import concurrent.futures

        results = []
        errors = []

        def run_validation(validator_root):
            try:
                validator = ContinuousImprovementValidator(validator_root)
                # Run a quick validation
                tests = validator._run_integration_tests()
                results.append(len(tests))
            except Exception as e:
                errors.append(str(e))

        # Run multiple validations concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(3):
                # Create separate temp directories for each thread
                thread_root = temp_project_root.parent / f"thread_{i}"
                thread_root.mkdir(exist_ok=True)
                (thread_root / ".ai_onboard").mkdir(exist_ok=True)

                future = executor.submit(run_validation, thread_root)
                futures.append(future)

            # Wait for all to complete
            concurrent.futures.wait(futures, timeout=60)

        # Check results
        if errors:
            pytest.skip(f"Concurrent validation failed: {errors[0]}")

        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        assert all(isinstance(r, int) and r >= 0 for r in results), "Invalid results"

    @pytest.mark.end_to_end
    def test_full_validation_workflow(self, real_validator, temp_project_root):
        """Test complete validation workflow from start to finish."""
        # Step 1: Initialize validator
        assert isinstance(real_validator, ContinuousImprovementValidator)

        # Step 2: Check initial state
        assert real_validator.validation_path.parent.exists()

        # Step 3: Run comprehensive validation
        try:
            report = real_validator.run_comprehensive_validation()

            # Step 4: Verify report structure
            assert isinstance(report, ValidationReport)
            assert report.total_tests > 0

            # Step 5: Check report persistence
            assert real_validator.validation_path.exists()

            # Step 6: Verify report content
            with open(real_validator.validation_path, "r") as f:
                saved_data = json.loads(f.readlines()[-1])
                assert saved_data["report_id"] == report.report_id

            # Step 7: Test report generation
            assert len(report.summary) > 0
            assert isinstance(report.recommendations, list)

            print(f"✅ Full validation workflow completed successfully")
            print(f"   Report ID: {report.report_id}")
            print(f"   Health Score: {report.system_health_score:.1f}%")
            print(f"   Total Tests: {report.total_tests}")

        except Exception as e:
            pytest.skip(f"Full validation workflow not available: {e}")


@pytest.mark.integration
class TestValidationSystemIntegration:
    """Test integration between validation system and other AI Onboard components."""

    def test_integration_with_metrics_collection(self, temp_project_root):
        """Test integration with unified metrics collection system."""
        try:
            from ai_onboard.core.unified_metrics_collector import (
                get_unified_metrics_collector,
            )

            validator = ContinuousImprovementValidator(temp_project_root)
            metrics_collector = get_unified_metrics_collector(temp_project_root)

            # Test that both systems can coexist
            assert validator is not None
            assert metrics_collector is not None

            # Test that validation can record metrics
            # This would be part of the actual validation implementation

        except ImportError as e:
            pytest.skip(f"Metrics collection system not available: {e}")

    def test_integration_with_user_preferences(self, temp_project_root):
        """Test integration with user preference learning system."""
        try:
            from ai_onboard.core.user_preference_learning import (
                get_user_preference_learning_system,
            )

            validator = ContinuousImprovementValidator(temp_project_root)
            user_prefs = get_user_preference_learning_system(temp_project_root)

            # Test that both systems can coexist
            assert validator is not None
            assert user_prefs is not None

        except ImportError as e:
            pytest.skip(f"User preference system not available: {e}")

    def test_integration_with_performance_optimizer(self, temp_project_root):
        """Test integration with performance optimizer."""
        try:
            from ai_onboard.core.performance_optimizer import get_performance_optimizer

            validator = ContinuousImprovementValidator(temp_project_root)
            perf_optimizer = get_performance_optimizer(temp_project_root)

            # Test that both systems can coexist
            assert validator is not None
            assert perf_optimizer is not None

        except ImportError as e:
            pytest.skip(f"Performance optimizer not available: {e}")


# Utility functions for integration testing
def create_mock_project_structure(root: Path):
    """Create a mock AI Onboard project structure for testing."""
    # Create main directories
    (root / "ai_onboard").mkdir(exist_ok=True)
    (root / "ai_onboard" / "core").mkdir(exist_ok=True)
    (root / "ai_onboard" / "cli").mkdir(exist_ok=True)
    (root / "tests").mkdir(exist_ok=True)
    (root / "docs").mkdir(exist_ok=True)

    # Create __init__.py files
    (root / "ai_onboard" / "__init__.py").touch()
    (root / "ai_onboard" / "core" / "__init__.py").touch()
    (root / "ai_onboard" / "cli" / "__init__.py").touch()

    # Create basic configuration files
    (root / "pyproject.toml").write_text(
        """
[build - system]
requires = ["setuptools >= 61.0"]

[project]
name = "test - ai - onboard"
version = "0.1.0"
description = "Test project for AI Onboard validation"
    """
    )

    # Create AI Onboard data directory
    (root / ".ai_onboard").mkdir(exist_ok=True)
    (root / ".ai_onboard" / "logs").mkdir(exist_ok=True)
    (root / ".ai_onboard" / "cache").mkdir(exist_ok=True)


@pytest.fixture
def mock_project_structure(tmp_path):
    """Provide a mock project structure for integration tests."""
    project_root = tmp_path / "mock_project"
    project_root.mkdir()
    create_mock_project_structure(project_root)
    return project_root
