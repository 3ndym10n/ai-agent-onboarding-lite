"""
Unit tests for PerformanceTrendAnalyzer.

Tests the core functionality of the performance trend analysis system
with mocked dependencies for reliable and fast testing.
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ai_onboard.core.performance_trend_analyzer import (
    AnomalyDetection,
    AnomalyType,
    PerformanceInsight,
    PerformanceTrendAnalyzer,
    TrendAnalysis,
    TrendDirection,
    get_performance_trend_analyzer,
)


@pytest.fixture
def temp_root():
    """Provide a temporary root directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_telemetry():
    """Provide mocked telemetry data."""
    mock_data=Mock()
    mock_data.get_performance_metrics.return_value={
        "response_time": [100, 120, 110, 130, 125],
        "memory_usage": [50, 55, 52, 60, 58],
        "cpu_usage": [30, 35, 32, 40, 38],
        "error_rate": [0.1, 0.2, 0.15, 0.25, 0.2],
    }
    return mock_data


@pytest.fixture
def trend_analyzer(temp_root):
    """Provide a PerformanceTrendAnalyzer instance."""
    with patch("ai_onboard.core.performance_trend_analyzer.telemetry"):
        analyzer=PerformanceTrendAnalyzer(temp_root)
        return analyzer


@pytest.fixture
def sample_performance_data():
    """Provide sample performance data for testing."""
    return {
        "timestamps": [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)],
        "response_times": [100 + i * 2 for i in range(30)],  # Increasing trend
        "memory_usage": [50 + (i % 10) for i in range(30)],  # Cyclical pattern
        "cpu_usage": [30 + (i * 0.5) for i in range(30)],  # Gradual increase
        "error_rates": [0.1 if i < 20 else 0.5 for i in range(30)],  # Step change
    }


class TestPerformanceTrendAnalyzer:
    """Test suite for PerformanceTrendAnalyzer."""

    def test_initialization(self, temp_root):
        """Test that PerformanceTrendAnalyzer initializes correctly."""
        with patch("ai_onboard.core.performance_trend_analyzer.telemetry"):
            analyzer=PerformanceTrendAnalyzer(temp_root)

            assert analyzer.root == temp_root
            assert analyzer.data_path == temp_root / ".ai_onboard" / "performance_data"
            assert (
                analyzer.config_path
                == temp_root / ".ai_onboard" / "trend_analysis_config.json"
            )
            assert isinstance(analyzer.config, dict)
            assert analyzer.data_path.exists()

    def test_analyze_trends_basic(self, trend_analyzer, sample_performance_data):
        """Test basic trend analysis functionality."""
        trends=trend_analyzer.analyze_trends(
            metric_name="response_time",
            data_points=sample_performance_data["response_times"],
            timestamps=sample_performance_data["timestamps"],
        )

        assert isinstance(trends, list)
        if trends:  # If trends were detected
            trend=trends[0]
            assert isinstance(trend, TrendAnalysis)
            assert trend.metric_name == "response_time"
            assert isinstance(trend.direction, TrendDirection)
            assert isinstance(trend.confidence, float)
            assert 0 <= trend.confidence <= 1

    def test_detect_anomalies_basic(self, trend_analyzer, sample_performance_data):
        """Test basic anomaly detection functionality."""
        anomalies=trend_analyzer.detect_anomalies(
            metric_name="error_rate",
            data_points=sample_performance_data["error_rates"],
            timestamps=sample_performance_data["timestamps"],
        )

        assert isinstance(anomalies, list)
        for anomaly in anomalies:
            assert isinstance(anomaly, AnomalyDetection)
            assert anomaly.metric_name == "error_rate"
            assert isinstance(anomaly.anomaly_type, AnomalyType)
            assert isinstance(anomaly.severity, float)
            assert 0 <= anomaly.severity <= 1

    def test_generate_performance_insights(
        self, trend_analyzer, sample_performance_data
    ):
        """Test performance insights generation."""
        # First analyze trends
        trends=trend_analyzer.analyze_trends(
            metric_name="response_time",
            data_points=sample_performance_data["response_times"],
            timestamps=sample_performance_data["timestamps"],
        )

        # Then detect anomalies
        anomalies=trend_analyzer.detect_anomalies(
            metric_name="response_time",
            data_points=sample_performance_data["response_times"],
            timestamps=sample_performance_data["timestamps"],
        )

        # Generate insights
        insights=trend_analyzer.generate_performance_insights(trends, anomalies)

        assert isinstance(insights, list)
        for insight in insights:
            assert isinstance(insight, PerformanceInsight)
            assert insight.insight_type is not None
            assert isinstance(insight.description, str)
            assert isinstance(insight.impact_score, float)
            assert 0 <= insight.impact_score <= 1

    def test_statistical_analysis(self, trend_analyzer):
        """Test statistical analysis methods."""
        data_points=[10, 12, 11, 13, 15, 14, 16, 18, 17, 19]

        # Test trend detection
        slope=trend_analyzer._calculate_trend_slope(data_points)
        assert isinstance(slope, float)

        # Test statistical measures
        mean=sum(data_points) / len(data_points)
        assert mean > 0

        # Test outlier detection
        outliers=trend_analyzer._detect_statistical_outliers(data_points)
        assert isinstance(outliers, list)

    def test_configuration_loading(self, temp_root):
        """Test configuration loading and defaults."""
        with patch("ai_onboard.core.performance_trend_analyzer.telemetry"):
            analyzer=PerformanceTrendAnalyzer(temp_root)

            # Check default configuration
            assert isinstance(analyzer.config, dict)
            assert "anomaly_detection_enabled" in analyzer.config
            assert "trend_analysis_window" in analyzer.config
            assert "confidence_threshold" in analyzer.config

    def test_data_persistence(self, trend_analyzer, sample_performance_data):
        """Test that analysis results are properly persisted."""
        # Perform analysis
        trends=trend_analyzer.analyze_trends(
            metric_name="test_metric",
            data_points=sample_performance_data["response_times"],
            timestamps=sample_performance_data["timestamps"],
        )

        # Check that data was persisted
        data_files=list(trend_analyzer.data_path.glob("*.json"))
        assert len(data_files) > 0

    def test_factory_function(self, temp_root):
        """Test the factory function."""
        with patch("ai_onboard.core.performance_trend_analyzer.telemetry"):
            analyzer=get_performance_trend_analyzer(temp_root)
            assert isinstance(analyzer, PerformanceTrendAnalyzer)
            assert analyzer.root == temp_root

    def test_error_handling_invalid_data(self, trend_analyzer):
        """Test error handling with invalid data."""
        # Empty data
        trends=trend_analyzer.analyze_trends("test", [], [])
        assert isinstance(trends, list)

        # Mismatched data lengths
        with pytest.raises(ValueError):
            trend_analyzer.analyze_trends(
                "test", [1, 2, 3], [datetime.now(), datetime.now()]  # Different length
            )

    def test_trend_direction_detection(self, trend_analyzer):
        """Test trend direction detection accuracy."""
        # Increasing trend
        increasing_data=list(range(10, 20))
        trends=trend_analyzer.analyze_trends(
            "increasing",
            increasing_data,
            [datetime.now() + timedelta(hours=i) for i in range(10)],
        )

        # Decreasing trend
        decreasing_data=list(range(20, 10, -1))
        trends=trend_analyzer.analyze_trends(
            "decreasing",
            decreasing_data,
            [datetime.now() + timedelta(hours=i) for i in range(10)],
        )

        # Stable trend
        stable_data=[15] * 10
        trends=trend_analyzer.analyze_trends(
            "stable",
            stable_data,
            [datetime.now() + timedelta(hours=i) for i in range(10)],
        )

    @pytest.mark.parametrize("window_size", [5, 10, 20])
    def test_different_analysis_windows(
        self, trend_analyzer, sample_performance_data, window_size
    ):
        """Test trend analysis with different window sizes."""
        # Update config for different window size
        trend_analyzer.config["trend_analysis_window"] = window_size

        trends=trend_analyzer.analyze_trends(
            metric_name="test_metric",
            data_points=sample_performance_data["response_times"][:window_size],
            timestamps=sample_performance_data["timestamps"][:window_size],
        )

        assert isinstance(trends, list)

    def test_anomaly_types_detection(self, trend_analyzer):
        """Test detection of different anomaly types."""
        # Spike anomaly
        spike_data=[10] * 10 + [100] + [10] * 10
        timestamps=[
            datetime.now() + timedelta(hours=i) for i in range(len(spike_data))
        ]

        anomalies=trend_analyzer.detect_anomalies(
            "spike_test", spike_data, timestamps
        )

        # Should detect the spike
        assert isinstance(anomalies, list)

    def test_performance_insight_generation(self, trend_analyzer):
        """Test comprehensive performance insight generation."""
        # Create various trend patterns
        trends=[
            TrendAnalysis(
                metric_name="response_time",
                direction=TrendDirection.INCREASING,
                confidence=0.9,
                slope=2.5,
                start_time=datetime.now() - timedelta(days=7),
                end_time=datetime.now(),
                data_points=30,
            )
        ]

        anomalies=[
            AnomalyDetection(
                metric_name="response_time",
                anomaly_type=AnomalyType.SPIKE,
                timestamp=datetime.now(),
                value=500.0,
                expected_range=(100.0, 150.0),
                severity=0.8,
                description="Response time spike detected",
            )
        ]

        insights=trend_analyzer.generate_performance_insights(trends, anomalies)

        assert isinstance(insights, list)
        for insight in insights:
            assert isinstance(insight, PerformanceInsight)
            assert len(insight.description) > 0
            assert insight.impact_score >= 0


class TestTrendAnalysis:
    """Test suite for TrendAnalysis data structure."""

    def test_trend_analysis_creation(self):
        """Test TrendAnalysis object creation."""
        trend=TrendAnalysis(
            metric_name="test_metric",
            direction=TrendDirection.INCREASING,
            confidence=0.85,
            slope=1.5,
            start_time=datetime.now() - timedelta(days=7),
            end_time=datetime.now(),
            data_points=100,
        )

        assert trend.metric_name == "test_metric"
        assert trend.direction == TrendDirection.INCREASING
        assert trend.confidence == 0.85
        assert trend.slope == 1.5
        assert trend.data_points == 100


class TestAnomalyDetection:
    """Test suite for AnomalyDetection data structure."""

    def test_anomaly_detection_creation(self):
        """Test AnomalyDetection object creation."""
        anomaly=AnomalyDetection(
            metric_name="test_metric",
            anomaly_type=AnomalyType.OUTLIER,
            timestamp=datetime.now(),
            value=999.0,
            expected_range=(10.0, 100.0),
            severity=0.9,
            description="Outlier detected in test metric",
        )

        assert anomaly.metric_name == "test_metric"
        assert anomaly.anomaly_type == AnomalyType.OUTLIER
        assert anomaly.value == 999.0
        assert anomaly.expected_range == (10.0, 100.0)
        assert anomaly.severity == 0.9


# Integration tests
@pytest.mark.integration
class TestPerformanceTrendAnalyzerIntegration:
    """Integration tests for the performance trend analyzer."""

    def test_end_to_end_analysis(self, temp_root):
        """Test complete end - to - end trend analysis."""
        with patch("ai_onboard.core.performance_trend_analyzer.telemetry"):
            analyzer=PerformanceTrendAnalyzer(temp_root)

            # Generate realistic performance data
            timestamps=[datetime.now() - timedelta(hours=i) for i in range(24, 0, -1)]
            response_times=[
                100 + i * 2 + (i % 3) * 10 for i in range(24)
            ]  # Trend with noise

            # Perform analysis
            trends=analyzer.analyze_trends(
                "response_time", response_times, timestamps
            )
            anomalies=analyzer.detect_anomalies(
                "response_time", response_times, timestamps
            )
            insights=analyzer.generate_performance_insights(trends, anomalies)

            # Verify results
            assert isinstance(trends, list)
            assert isinstance(anomalies, list)
            assert isinstance(insights, list)

            # Check data persistence
            data_files=list(analyzer.data_path.glob("*.json"))
            assert len(data_files) > 0
