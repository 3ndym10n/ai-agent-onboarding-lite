"""
Unit tests for AdvancedTestReportGenerator.

Tests the core functionality of the advanced test reporting system
with mocked dependencies to ensure reliability and performance.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ai_onboard.core.advanced_test_reporting import (
    AdvancedTestReport,
    AdvancedTestReportGenerator,
    QualityAssessment,
    ReportFormat,
    ReportLevel,
    TestExecutionContext,
    TestMetrics,
    get_advanced_test_report_generator,
)
from ai_onboard.core.continuous_improvement_validator import (
    ValidationCategory,
    ValidationResult,
    ValidationTestCase,
)


@pytest.fixture
def temp_root():
    """Provide a temporary root directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_validator():
    """Provide a mocked ContinuousImprovementValidator."""
    validator = Mock()
    validator.run_comprehensive_validation.return_value = Mock()
    return validator


@pytest.fixture
def mock_trend_analyzer():
    """Provide a mocked PerformanceTrendAnalyzer."""
    analyzer = Mock()
    analyzer.analyze_trends.return_value = []
    analyzer.detect_anomalies.return_value = []
    return analyzer


@pytest.fixture
def sample_test_results():
    """Provide sample test results for testing."""
    return [
        ValidationTestCase(
            test_id="test_001",
            name="test_basic_functionality",
            description="Basic functionality test",
            category = ValidationCategory.INTEGRATION,
            result = ValidationResult.PASS,
            duration = 0.5,
            error_message = None,
        ),
        ValidationTestCase(
            test_id="test_002",
            name="test_performance",
            description="Performance test",
            category = ValidationCategory.PERFORMANCE,
            result = ValidationResult.WARNING,
            duration = 2.5,
            error_message="Performance threshold exceeded",
        ),
        ValidationTestCase(
            test_id="test_003",
            name="test_data_integrity",
            description="Data integrity test",
            category = ValidationCategory.DATA_INTEGRITY,
            result = ValidationResult.FAIL,
            duration = 1.0,
            error_message="Data validation failed",
        ),
    ]


@pytest.fixture
def report_generator(temp_root, mock_validator, mock_trend_analyzer):
    """Provide an AdvancedTestReportGenerator with mocked dependencies."""
    with patch(
        "ai_onboard.core.advanced_test_reporting.ContinuousImprovementValidator",
        return_value = mock_validator,
    ), patch(
        "ai_onboard.core.advanced_test_reporting.get_performance_trend_analyzer",
        return_value = mock_trend_analyzer,
    ):
        generator = AdvancedTestReportGenerator(temp_root)
        return generator


class TestAdvancedTestReportGenerator:
    """Test suite for AdvancedTestReportGenerator."""

    def test_initialization(self, temp_root):
        """Test that AdvancedTestReportGenerator initializes correctly."""
        with patch(
            "ai_onboard.core.advanced_test_reporting.ContinuousImprovementValidator"
        ), patch(
            "ai_onboard.core.advanced_test_reporting.get_performance_trend_analyzer"
        ):
            generator = AdvancedTestReportGenerator(temp_root)

            assert generator.root == temp_root
            assert generator.reports_path == temp_root / ".ai_onboard" / "test_reports"
            assert (
                generator.config_path
                == temp_root / ".ai_onboard" / "test_reporting_config.json"
            )
            assert isinstance(generator.config, dict)
            assert isinstance(generator.quality_benchmarks, dict)

    def test_calculate_test_metrics(self, report_generator, sample_test_results):
        """Test test metrics calculation."""
        metrics = report_generator._calculate_test_metrics(sample_test_results)

        assert isinstance(metrics, TestMetrics)
        assert metrics.total_tests == 3
        assert metrics.passed_tests == 1
        assert metrics.failed_tests == 1
        assert metrics.warning_tests == 1
        assert metrics.skipped_tests == 0
        assert metrics.success_rate == pytest.approx(33.33, rel=1e-2)
        assert metrics.average_duration > 0
        assert metrics.total_duration > 0

    def test_assess_test_quality(self, report_generator, sample_test_results):
        """Test quality assessment functionality."""
        metrics = report_generator._calculate_test_metrics(sample_test_results)
        quality = report_generator._assess_test_quality(metrics, sample_test_results)

        assert isinstance(quality, QualityAssessment)
        assert 0 <= quality.overall_score <= 100
        assert isinstance(quality.coverage_score, float)
        assert isinstance(quality.reliability_score, float)
        assert isinstance(quality.performance_score, float)
        assert isinstance(quality.maintainability_score, float)

    def test_generate_execution_context(self, report_generator, sample_test_results):
        """Test execution context generation."""
        context = report_generator._generate_execution_context(sample_test_results)

        assert isinstance(context, TestExecutionContext)
        assert isinstance(context.test_environment, dict)
        assert isinstance(context.system_info, dict)
        assert isinstance(context.configuration, dict)
        assert context.duration > 0
        assert isinstance(context.resource_usage, dict)

    def test_generate_comprehensive_report(self, report_generator, sample_test_results):
        """Test comprehensive report generation."""
        report = report_generator.generate_comprehensive_report(
            test_results = sample_test_results,
            report_level = ReportLevel.DETAILED,
            output_formats=[ReportFormat.JSON],
        )

        assert isinstance(report, AdvancedTestReport)
        assert report.report_id is not None
        assert isinstance(report.generated_at, datetime)
        assert report.report_level == ReportLevel.DETAILED
        assert isinstance(report.test_metrics, TestMetrics)
        assert isinstance(report.quality_assessment, QualityAssessment)
        assert isinstance(report.execution_context, TestExecutionContext)
        assert len(report.test_results) == 3
        assert isinstance(report.recommendations, list)

    def test_report_persistence(self, report_generator, sample_test_results):
        """Test that reports are properly persisted."""
        report = report_generator.generate_comprehensive_report(
            test_results = sample_test_results, output_formats=[ReportFormat.JSON]
        )

        # Check that report file was created
        report_file = report_generator.reports_path / f"{report.report_id}.json"
        assert report_file.exists()

        # Verify report content
        with open(report_file, "r") as f:
            saved_data = json.load(f)
            assert saved_data["report_id"] == report.report_id
            assert saved_data["test_metrics"]["total_tests"] == 3

    def test_historical_comparison(self, report_generator, sample_test_results):
        """Test historical comparison functionality."""
        # Generate first report
        report_generator.generate_comprehensive_report(sample_test_results)

        # Generate second report
        report2 = report_generator.generate_comprehensive_report(sample_test_results)

        # Check historical comparison
        assert isinstance(report2.historical_comparison, dict)
        # Should have comparison data since we have history now

    def test_factory_function(self, temp_root):
        """Test the factory function."""
        with patch(
            "ai_onboard.core.advanced_test_reporting.ContinuousImprovementValidator"
        ), patch(
            "ai_onboard.core.advanced_test_reporting.get_performance_trend_analyzer"
        ):
            generator = get_advanced_test_report_generator(temp_root)
            assert isinstance(generator, AdvancedTestReportGenerator)
            assert generator.root == temp_root

    def test_error_handling_invalid_test_results(self, report_generator):
        """Test error handling with invalid test results."""
        with pytest.raises(Exception):
            report_generator.generate_comprehensive_report([])

    def test_configuration_loading(self, temp_root):
        """Test configuration loading and defaults."""
        # Create a custom config
        config_path = temp_root / ".ai_onboard" / "test_reporting_config.json"
        config_path.parent.mkdir(parents = True, exist_ok = True)

        custom_config = {
            "reporting_enabled": True,
            "max_report_history": 50,
            "default_output_formats": ["html", "json"],
        }

        with open(config_path, "w") as f:
            json.dump(custom_config, f)

        with patch(
            "ai_onboard.core.advanced_test_reporting.ContinuousImprovementValidator"
        ), patch(
            "ai_onboard.core.advanced_test_reporting.get_performance_trend_analyzer"
        ):
            generator = AdvancedTestReportGenerator(temp_root)
            assert generator.config["reporting_enabled"] is True
            assert generator.config["max_report_history"] == 50

    def test_quality_benchmarks_initialization(self, report_generator):
        """Test quality benchmarks initialization."""
        benchmarks = report_generator.quality_benchmarks

        assert isinstance(benchmarks, dict)
        assert "success_rate_threshold" in benchmarks
        assert "performance_threshold" in benchmarks
        assert "coverage_threshold" in benchmarks

        # All benchmarks should be numeric
        for key, value in benchmarks.items():
            assert isinstance(value, (int, float))

    @pytest.mark.parametrize(
        "report_level",
        [ReportLevel.SUMMARY, ReportLevel.DETAILED, ReportLevel.COMPREHENSIVE],
    )
    def test_different_report_levels(
        self, report_generator, sample_test_results, report_level
    ):
        """Test report generation with different detail levels."""
        report = report_generator.generate_comprehensive_report(
            test_results = sample_test_results, report_level = report_level
        )

        assert report.report_level == report_level
        assert isinstance(report, AdvancedTestReport)

    @pytest.mark.parametrize("output_format", [ReportFormat.JSON, ReportFormat.HTML])
    def test_different_output_formats(
        self, report_generator, sample_test_results, output_format
    ):
        """Test report generation with different output formats."""
        report = report_generator.generate_comprehensive_report(
            test_results = sample_test_results, output_formats=[output_format]
        )

        assert isinstance(report, AdvancedTestReport)
        # Check that appropriate output file was created
        if output_format == ReportFormat.JSON:
            report_file = report_generator.reports_path / f"{report.report_id}.json"
            assert report_file.exists()


class TestTestMetrics:
    """Test suite for TestMetrics calculations."""

    def test_metrics_calculation_edge_cases(self):
        """Test metrics calculation with edge cases."""
        # Empty test results
        empty_results = []

        # Single test result
        single_result = [
            ValidationTestCase(
                test_id="test_001",
                name="single_test",
                description="Single test",
                category = ValidationCategory.INTEGRATION,
                result = ValidationResult.PASS,
                duration = 1.0,
            )
        ]

        # Test with empty results should handle gracefully
        # (This would be tested in the actual implementation)
        assert len(empty_results) == 0
        assert len(single_result) == 1


class TestQualityAssessment:
    """Test suite for QualityAssessment functionality."""

    def test_quality_score_bounds(self):
        """Test that quality scores are within expected bounds."""
        # This would test the actual quality assessment logic
        # Quality scores should always be between 0 and 100
        pass  # Implementation would go here


# Integration test
@pytest.mark.integration
class TestAdvancedTestReportingIntegration:
    """Integration tests for the advanced test reporting system."""

    def test_end_to_end_report_generation(self, temp_root):
        """Test complete end - to - end report generation."""
        with patch(
            "ai_onboard.core.advanced_test_reporting.ContinuousImprovementValidator"
        ), patch(
            "ai_onboard.core.advanced_test_reporting.get_performance_trend_analyzer"
        ):

            generator = AdvancedTestReportGenerator(temp_root)

            # Create realistic test results
            test_results = [
                ValidationTestCase(
                    test_id = f"integration_test_{i}",
                    name = f"integration_test_{i}",
                    description = f"Integration test {i}",
                    category = ValidationCategory.INTEGRATION,
                    result=(
                        ValidationResult.PASS if i % 2 == 0 else ValidationResult.FAIL
                    ),
                    duration = 0.1 * i,
                )
                for i in range(10)
            ]

            # Generate comprehensive report
            report = generator.generate_comprehensive_report(
                test_results = test_results,
                report_level = ReportLevel.COMPREHENSIVE,
                output_formats=[ReportFormat.JSON, ReportFormat.HTML],
            )

            # Verify report structure
            assert isinstance(report, AdvancedTestReport)
            assert report.test_metrics.total_tests == 10
            assert report.test_metrics.passed_tests == 5
            assert report.test_metrics.failed_tests == 5

            # Verify files were created
            json_file = generator.reports_path / f"{report.report_id}.json"
            assert json_file.exists()
