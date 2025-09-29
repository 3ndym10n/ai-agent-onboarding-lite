"""
Pytest configuration and fixtures for AI Onboard testing.

This module provides shared fixtures, configuration, and plugins for all tests,
including integration with the ContinuousImprovementValidator system.
"""

import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import pytest

from ai_onboard.core.continuous_improvement import (
    ContinuousImprovementValidator,
    ValidationCategory,
    ValidationReport,
    ValidationResult,
    ValidationTestCase,
)

# Global test configuration
TEST_CONFIG = {
    "timeout_seconds": 30,
    "temp_dir_prefix": "ai_onboard_test_",
    "validation_enabled": True,
    "performance_tracking": True,
    "integration_testing": True,
}


@pytest.fixture(scope="session")
def test_root():
    """Provide a temporary test root directory for the entire test session."""
    with tempfile.TemporaryDirectory(prefix=TEST_CONFIG["temp_dir_prefix"]) as temp_dir:
        test_root = Path(temp_dir)

        # Create necessary directories
        (test_root / ".ai_onboard").mkdir(exist_ok=True)
        (test_root / ".ai_onboard" / "logs").mkdir(exist_ok=True)
        (test_root / ".ai_onboard" / "cache").mkdir(exist_ok=True)

        # Provide fixture data expected by preference learning components
        now = datetime.now(timezone.utc).isoformat()
        user_profiles_path = test_root / ".ai_onboard" / "user_profiles.json"
        sample_profile = {
            "fixture_user": {
                "experience_level": "beginner",
                "preferences": {},
                "behavior_patterns": [],
                "interaction_history": [
                    {
                        "interaction_id": "interaction_fixture",
                        "interaction_type": "command_execution",
                        "timestamp": now,
                        "context": {"source": "fixture"},
                        "duration": None,
                        "outcome": None,
                        "satisfaction_score": None,
                        "feedback": None,
                    }
                ],
                "satisfaction_scores": [],
                "feedback_history": [],
                "last_activity": now,
                "total_interactions": 1,
                "average_satisfaction": 0.0,
                "created_at": now,
            }
        }
        user_profiles_path.write_text(
            json.dumps(sample_profile, indent=2), encoding="utf-8"
        )

        # Set environment variables for testing
        os.environ["AI_ONBOARD_TEST_MODE"] = "true"
        os.environ["AI_ONBOARD_TEST_ROOT"] = str(test_root)

        yield test_root

        # Cleanup
        os.environ.pop("AI_ONBOARD_TEST_MODE", None)
        os.environ.pop("AI_ONBOARD_TEST_ROOT", None)


@pytest.fixture(scope="session")
def continuous_improvement_validator(test_root):
    """Provide a ContinuousImprovementValidator instance for the test session."""
    if not TEST_CONFIG["validation_enabled"]:
        pytest.skip("Continuous improvement validation disabled")

    try:
        validator = ContinuousImprovementValidator(test_root)
        yield validator
    except ImportError as e:
        pytest.skip(f"ContinuousImprovementValidator not available: {e}")


@pytest.fixture
def temp_project_root(tmp_path):
    """Provide a temporary project root for individual tests."""
    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create AI Onboard directory structure
    ai_onboard_dir = project_root / ".ai_onboard"
    ai_onboard_dir.mkdir()
    (ai_onboard_dir / "logs").mkdir()
    (ai_onboard_dir / "cache").mkdir()
    (ai_onboard_dir / "temp").mkdir()

    return project_root


@pytest.fixture
def mock_validation_config():
    """Provide mock validation configuration for testing."""
    return {
        "test_timeout_seconds": 10,
        "performance_thresholds": {
            "response_time_ms": 500,
            "memory_usage_mb": 50,
            "cpu_usage_percent": 70,
        },
        "data_integrity_checks": True,
        "integration_tests": True,
        "performance_tests": True,
        "end_to_end_tests": True,
    }


@pytest.fixture
def sample_test_results():
    """Provide sample test results for testing validation functionality."""
    return [
        ValidationTestCase(
            test_id="test_integration_basic_001",
            name="test_integration_basic",
            description="Basic integration test",
            category=ValidationCategory.INTEGRATION,
            result=ValidationResult.PASS,
            duration=0.1205,
            error_message=None,
        ),
        ValidationTestCase(
            test_id="test_performance_response_time_002",
            name="test_performance_response_time",
            description="Performance response time test",
            category=ValidationCategory.PERFORMANCE,
            result=ValidationResult.WARNING,
            duration=0.8,
            error_message="Response time exceeded threshold",
        ),
        ValidationTestCase(
            test_id="test_data_integrity_check_003",
            name="test_data_integrity_check",
            description="Data integrity check test",
            category=ValidationCategory.DATA_INTEGRITY,
            result=ValidationResult.PASS,
            duration=0.045,
            error_message=None,
        ),
        ValidationTestCase(
            test_id="test_end_to_end_workflow_004",
            name="test_end_to_end_workflow",
            description="End - to - end workflow test",
            category=ValidationCategory.END_TO_END,
            result=ValidationResult.FAIL,
            duration=2.0,
            error_message="Authentication failed: invalid credentials",
        ),
    ]


class ValidationTestCollector:
    """Collects test results for integration with ContinuousImprovementValidator."""

    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.end_time = None
        self.performance_metrics = {}

    def add_test_result(
        self,
        nodeid: str,
        outcome: str,
        duration: float,
        keywords: List[str],
        longrepr: Optional[str] = None,
    ):
        """Add a test result to the collection."""
        # Map pytest outcomes to our ValidationResult enum
        result_mapping = {
            "passed": ValidationResult.PASS,
            "failed": ValidationResult.FAIL,
            "skipped": ValidationResult.SKIP,
            "error": ValidationResult.FAIL,
        }

        # Determine test category from keywords / markers
        category = ValidationCategory.INTEGRATION  # Default
        if "unit" in keywords:
            category = (
                ValidationCategory.INTEGRATION
            )  # Unit tests are part of integration
        elif "performance" in keywords or "slow" in keywords:
            category = ValidationCategory.PERFORMANCE
        elif "integration" in keywords:
            category = ValidationCategory.INTEGRATION
        elif "end_to_end" in keywords or "e2e" in keywords:
            category = ValidationCategory.END_TO_END

        test_case = ValidationTestCase(
            test_id=f"pytest_{nodeid.replace('::', '_').replace('/', '_')}",
            name=nodeid.split("::")[-1],  # Extract test function name
            description=f"Pytest test: {nodeid}",
            category=category,
            result=result_mapping.get(outcome, ValidationResult.FAIL),
            duration=duration,  # Keep in seconds
            error_message=str(longrepr) if longrepr else None,
        )

        self.test_results.append(test_case)

    def generate_validation_report(self) -> Optional[ValidationReport]:
        """Generate a validation report from collected test results."""
        if not self.test_results:
            return None

        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for t in self.test_results if t.result == ValidationResult.PASS
        )
        failed_tests = sum(
            1 for t in self.test_results if t.result == ValidationResult.FAIL
        )
        warning_tests = sum(
            1 for t in self.test_results if t.result == ValidationResult.WARNING
        )
        skipped_tests = sum(
            1 for t in self.test_results if t.result == ValidationResult.SKIP
        )

        # Calculate health score based on test results
        if total_tests == 0:
            health_score = 0.0
        else:
            health_score = (passed_tests / total_tests) * 100.0
            # Reduce score for warnings
            health_score -= (warning_tests / total_tests) * 10.0
            health_score = max(0.0, min(100.0, health_score))

        # Generate recommendations based on failures
        recommendations = []
        for test in self.test_results:
            if test.result == ValidationResult.FAIL and test.error_message:
                recommendations.append(
                    f"Fix failing test: {test.name} - {test.error_message}"
                )
            elif test.result == ValidationResult.WARNING:
                recommendations.append(f"Address warning in test: {test.name}")

        if not recommendations:
            recommendations.append("All tests passed successfully!")

        # Generate summary
        summary = f"Executed {total_tests} tests: {passed_tests} passed, {failed_tests} failed, {warning_tests} warnings, {skipped_tests} skipped. Health score: {health_score:.1f}%"

        return ValidationReport(
            report_id=f"pytest_validation_{int(time.time())}",
            generated_at=datetime.now(),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            warning_tests=warning_tests,
            skipped_tests=skipped_tests,
            test_results=self.test_results,
            system_health_score=health_score,
            recommendations=recommendations[:10],  # Limit recommendations
            summary=summary,
        )


# Global test collector instance
_test_collector = ValidationTestCollector()


class ContinuousImprovementPlugin:
    """Pytest plugin for integrating with ContinuousImprovementValidator."""

    def __init__(self):
        self.collector = _test_collector
        self.validator = None
        self.test_session_start = None

    def pytest_configure(self, config):
        """Configure the plugin."""
        # Add custom markers
        config.addinivalue_line(
            "markers", "ci_validation: Continuous improvement validation test"
        )
        config.addinivalue_line("markers", "performance: Performance test")
        config.addinivalue_line("markers", "integration: Integration test")
        config.addinivalue_line("markers", "end_to_end: End - to - end test")
        config.addinivalue_line("markers", "data_integrity: Data integrity test")

    def pytest_sessionstart(self, session):
        """Called at the start of the test session."""
        self.test_session_start = time.time()
        self.collector.start_time = datetime.now()

        # Try to initialize validator if available
        try:
            test_root = Path(os.environ.get("AI_ONBOARD_TEST_ROOT", "/tmp"))
            self.validator = ContinuousImprovementValidator(test_root)
        except Exception:
            # Validator not available, continue without it
            pass

    def pytest_runtest_logreport(self, report):
        """Called for each test report."""
        if report.when == "call":  # Only collect call phase results
            keywords = [
                marker.name
                for marker in report.keywords.values()
                if hasattr(marker, "name")
            ]

            self.collector.add_test_result(
                nodeid=report.nodeid,
                outcome=report.outcome,
                duration=report.duration,
                keywords=keywords,
                longrepr=str(report.longrepr) if report.longrepr else None,
            )

    def pytest_sessionfinish(self, session, exitstatus):
        """Called at the end of the test session."""
        self.collector.end_time = datetime.now()

        # Generate and save validation report
        if (
            hasattr(session.config.option, "ci_validation_report")
            and session.config.option.ci_validation_report
        ):
            self._generate_ci_validation_report(session, exitstatus)

    def _generate_ci_validation_report(self, session, exitstatus):
        """Generate continuous improvement validation report."""
        report = self.collector.generate_validation_report()

        if report:
            # Save report to file
            report_file = Path(".ai_onboard") / "pytest_validation_report.json"
            report_file.parent.mkdir(exist_ok=True)

            report_data = {
                "report_id": report.report_id,
                "generated_at": report.generated_at.isoformat(),
                "total_tests": report.total_tests,
                "passed_tests": report.passed_tests,
                "failed_tests": report.failed_tests,
                "warning_tests": report.warning_tests,
                "skipped_tests": report.skipped_tests,
                "system_health_score": report.system_health_score,
                "recommendations": report.recommendations,
                "summary": report.summary,
                "pytest_exit_status": exitstatus,
                "test_results": [
                    {
                        "name": t.name,
                        "category": t.category.value,
                        "result": t.result.value,
                        "duration": t.duration,
                        "description": t.description,
                        "error_message": t.error_message,
                    }
                    for t in report.test_results
                ],
            }

            with open(report_file, "w") as f:
                json.dump(report_data, f, indent=2)

            # Print summary
            print(f"\n🧪 Continuous Improvement Validation Report Generated")
            print(f"   Report ID: {report.report_id}")
            print(f"   Health Score: {report.system_health_score:.1f}%")
            print(
                f"   Tests: {report.total_tests} total, {report.passed_tests} passed, {report.failed_tests} failed"
            )
            print(f"   Report saved to: {report_file}")

            # Integrate with validator if available
            if self.validator:
                try:
                    self.validator._save_validation_report(report)
                    print(f"   Integrated with ContinuousImprovementValidator")
                except Exception as e:
                    print(f"   Warning: Could not integrate with validator: {e}")


def pytest_addoption(parser):
    """Add command line options for continuous improvement integration."""
    parser.addoption(
        "--ci - validation - report",
        action="store_true",
        default=False,
        help="Generate continuous improvement validation report",
    )
    parser.addoption(
        "--ci - validation - timeout",
        action="store",
        default=300,
        type=int,
        help="Timeout for continuous improvement validation tests",
    )
    parser.addoption(
        "--performance - baseline",
        action="store",
        help="Performance baseline file for comparison",
    )


def pytest_configure(config):
    """Configure pytest with continuous improvement plugin."""
    if config.getoption("--ci - validation - report"):
        config.pluginmanager.register(ContinuousImprovementPlugin(), "ci_plugin")


@pytest.fixture(scope="session")
def ci_validation_enabled(request):
    """Check if CI validation is enabled."""
    return request.config.getoption("--ci - validation - report")


@pytest.fixture(scope="session")
def ci_validation_timeout(request):
    """Get CI validation timeout."""
    return request.config.getoption("--ci - validation - timeout")


@pytest.fixture(scope="session")
def performance_baseline(request):
    """Get performance baseline file path."""
    baseline_file = request.config.getoption("--performance - baseline")
    if baseline_file and Path(baseline_file).exists():
        with open(baseline_file, "r") as f:
            return json.load(f)
    return None


# Performance tracking fixtures
@pytest.fixture
def performance_tracker():
    """Provide a performance tracker for tests."""

    class PerformanceTracker:
        def __init__(self):
            self.metrics = {}
            self.start_times = {}

        def start(self, metric_name: str):
            self.start_times[metric_name] = time.time()

        def end(self, metric_name: str):
            if metric_name in self.start_times:
                duration = time.time() - self.start_times[metric_name]
                self.metrics[metric_name] = duration
                return duration
            return None

        def get_metrics(self):
            return self.metrics.copy()

    return PerformanceTracker()


# Integration test helpers
@pytest.fixture
def integration_test_helper():
    """Provide helper functions for integration tests."""

    class IntegrationTestHelper:
        @staticmethod
        def create_test_case(
            name: str,
            result: ValidationResult,
            duration: float = 0.1,
            category: ValidationCategory = ValidationCategory.INTEGRATION,
            error_message: Optional[str] = None,
        ) -> ValidationTestCase:
            return ValidationTestCase(
                test_id=f"helper_{name}",
                name=name,
                description=f"Test case: {name}",
                category=category,
                result=result,
                duration=duration,
                error_message=error_message,
            )

        @staticmethod
        def create_validation_report(
            test_results: List[ValidationTestCase],
        ) -> ValidationReport:
            total_tests = len(test_results)
            passed_tests = sum(
                1 for t in test_results if t.result == ValidationResult.PASS
            )
            failed_tests = sum(
                1 for t in test_results if t.result == ValidationResult.FAIL
            )
            warning_tests = sum(
                1 for t in test_results if t.result == ValidationResult.WARNING
            )
            skipped_tests = sum(
                1 for t in test_results if t.result == ValidationResult.SKIP
            )

            health_score = (
                (passed_tests / total_tests * 100.0) if total_tests > 0 else 0.0
            )

            return ValidationReport(
                report_id=f"test_report_{int(time.time())}",
                generated_at=datetime.now(),
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                warning_tests=warning_tests,
                skipped_tests=skipped_tests,
                test_results=test_results,
                system_health_score=health_score,
                recommendations=[],
                summary=f"Test report with {total_tests} tests",
            )

    return IntegrationTestHelper()


# Custom markers for better test organization
def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their names and locations."""
    for item in items:
        # Mark performance tests
        if "performance" in item.name.lower() or "perf" in item.name.lower():
            item.add_marker(pytest.mark.performance)

        # Mark slow tests
        if "slow" in item.name.lower() or "integration" in item.name.lower():
            item.add_marker(pytest.mark.slow)

        # Mark CI validation tests
        if (
            "continuous_improvement" in str(item.fspath)
            or "validator" in item.name.lower()
        ):
            item.add_marker(pytest.mark.ci_validation)

        # Mark end - to - end tests
        if "end_to_end" in item.name.lower() or "e2e" in item.name.lower():
            item.add_marker(pytest.mark.end_to_end)


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_test_artifacts():
    """Automatically clean up test artifacts after each test."""
    yield

    # Clean up any test files in the current directory
    test_files = [
        ".ai_onboard / test_*.json",
        ".ai_onboard / validation_*.jsonl",
        ".ai_onboard / temp_*",
    ]

    for pattern in test_files:
        import glob

        for file_path in glob.glob(pattern):
            try:
                Path(file_path).unlink()
            except Exception:
                pass  # Ignore cleanup errors
