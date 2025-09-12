"""
Performance Trend Analysis System - Advanced trend detection and forecasting.

This module provides comprehensive performance trend analysis capabilities that:
- Analyze historical performance data to identify patterns and trends
- Detect performance anomalies and degradation patterns
- Generate predictive forecasts for capacity planning
- Provide actionable insights and optimization recommendations
- Support multiple time series analysis techniques
"""

import json
import math
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
import warnings

from . import utils, telemetry
from .unified_metrics_collector import (
    UnifiedMetricsCollector,
    MetricEvent,
    MetricSource,
    MetricCategory,
    get_unified_metrics_collector,
)
from .performance_optimizer import (
    PerformanceOptimizer,
    PerformanceSnapshot,
    PerformanceMetric,
    get_performance_optimizer,
)


class TrendDirection(Enum):
    """Direction of performance trends."""

    IMPROVING = "improving"
    DEGRADING = "degrading"
    STABLE = "stable"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


class TrendSeverity(Enum):
    """Severity levels for performance trends."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ForecastConfidence(Enum):
    """Confidence levels for performance forecasts."""

    LOW = "low"  # < 60%
    MEDIUM = "medium"  # 60-80%
    HIGH = "high"  # 80-95%
    VERY_HIGH = "very_high"  # > 95%


@dataclass
class TrendAnalysis:
    """Results of trend analysis for a specific metric."""

    metric_name: str
    time_period: str
    direction: TrendDirection
    severity: TrendSeverity
    confidence: float
    slope: float
    correlation: float
    data_points: int
    start_value: float
    end_value: float
    change_percent: float
    volatility: float
    trend_strength: float
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceForecast:
    """Performance forecast for future time periods."""

    metric_name: str
    forecast_horizon: str
    predicted_values: List[float]
    confidence_intervals: List[Tuple[float, float]]
    forecast_confidence: ForecastConfidence
    methodology: str
    assumptions: List[str]
    risk_factors: List[str]
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyDetection:
    """Results of anomaly detection analysis."""

    metric_name: str
    anomaly_timestamp: datetime
    anomaly_value: float
    expected_value: float
    deviation_score: float
    anomaly_type: str  # "spike", "drop", "drift", "outlier"
    severity: TrendSeverity
    context: Dict[str, Any]
    detection_method: str
    confidence: float


@dataclass
class PerformanceInsight:
    """Actionable insights derived from trend analysis."""

    insight_id: str
    title: str
    description: str
    category: str  # "optimization", "capacity", "reliability", "efficiency"
    priority: str  # "low", "medium", "high", "critical"
    affected_metrics: List[str]
    evidence: Dict[str, Any]
    recommendations: List[str]
    estimated_impact: str
    implementation_effort: str
    created_at: datetime = field(default_factory=datetime.now)


class PerformanceTrendAnalyzer:
    """Advanced performance trend analysis and forecasting system."""

    def __init__(self, root: Path):
        self.root = root
        self.trends_path = root / ".ai_onboard" / "performance_trends.jsonl"
        self.forecasts_path = root / ".ai_onboard" / "performance_forecasts.jsonl"
        self.anomalies_path = root / ".ai_onboard" / "performance_anomalies.jsonl"
        self.insights_path = root / ".ai_onboard" / "performance_insights.jsonl"
        self.config_path = root / ".ai_onboard" / "trend_analysis_config.json"

        # Initialize dependencies
        self.metrics_collector = get_unified_metrics_collector(root)
        self.performance_optimizer = get_performance_optimizer(root)

        # Analysis configuration
        self.config = self._load_config()

        # In-memory caches for performance
        self.trend_cache: Dict[str, TrendAnalysis] = {}
        self.anomaly_cache: List[AnomalyDetection] = []
        self.forecast_cache: Dict[str, PerformanceForecast] = {}

        # Statistical thresholds
        self.anomaly_threshold = self.config.get(
            "anomaly_threshold", 2.5
        )  # Standard deviations
        self.trend_min_points = self.config.get("trend_min_points", 10)
        self.forecast_horizon_days = self.config.get("forecast_horizon_days", 30)

        # Ensure directories exist
        utils.ensure_dir(self.trends_path.parent)

        # Initialize baseline data
        self._initialize_baselines()

    def _load_config(self) -> Dict[str, Any]:
        """Load trend analysis configuration."""
        default_config = {
            "analysis_enabled": True,
            "trend_analysis": {
                "min_data_points": 10,
                "lookback_days": 30,
                "confidence_threshold": 0.7,
                "volatility_threshold": 0.3,
            },
            "anomaly_detection": {
                "enabled": True,
                "threshold_std_devs": 2.5,
                "window_size": 50,
                "sensitivity": "medium",
            },
            "forecasting": {
                "enabled": True,
                "horizon_days": 30,
                "methods": ["linear", "exponential", "seasonal"],
                "confidence_intervals": [0.68, 0.95],
            },
            "insights": {
                "enabled": True,
                "min_impact_threshold": 0.1,
                "priority_weights": {
                    "performance_impact": 0.4,
                    "frequency": 0.3,
                    "trend_strength": 0.3,
                },
            },
        }

        return utils.read_json(self.config_path, default=default_config)

    def _initialize_baselines(self):
        """Initialize performance baselines from historical data."""
        try:
            # Load recent performance data to establish baselines
            cutoff_date = datetime.now() - timedelta(
                days=self.config["trend_analysis"]["lookback_days"]
            )

            # This would load historical metrics for baseline calculation
            # For now, we'll establish basic baselines
            self.baselines = {
                "cpu_usage": {"mean": 25.0, "std": 15.0, "p95": 60.0},
                "memory_usage": {"mean": 45.0, "std": 20.0, "p95": 80.0},
                "response_time": {"mean": 200.0, "std": 100.0, "p95": 500.0},
                "error_rate": {"mean": 0.01, "std": 0.005, "p95": 0.02},
            }

            telemetry.log_event(
                "trend_analyzer_initialized", baselines_count=len(self.baselines)
            )

        except Exception as e:
            telemetry.log_event("trend_analyzer_init_error", error=str(e))
            self.baselines = {}

    def analyze_performance_trends(
        self, metric_names: Optional[List[str]] = None, time_period: str = "7d"
    ) -> List[TrendAnalysis]:
        """Analyze performance trends for specified metrics and time period."""
        if not self.config.get("analysis_enabled", True):
            return []

        try:
            # Get available metrics if none specified
            if not metric_names:
                metric_names = self._get_available_performance_metrics()

            trends = []
            for metric_name in metric_names:
                trend = self._analyze_metric_trend(metric_name, time_period)
                if trend:
                    trends.append(trend)
                    self.trend_cache[f"{metric_name}_{time_period}"] = trend

            # Save trends to persistent storage
            self._save_trends(trends)

            telemetry.log_event(
                "performance_trends_analyzed",
                metrics_count=len(metric_names),
                trends_found=len(trends),
                time_period=time_period,
            )

            return trends

        except Exception as e:
            telemetry.log_event("trend_analysis_error", error=str(e))
            return []

    def _analyze_metric_trend(
        self, metric_name: str, time_period: str
    ) -> Optional[TrendAnalysis]:
        """Analyze trend for a specific metric over the given time period."""
        try:
            # Get historical data for the metric
            data_points = self._get_metric_history(metric_name, time_period)

            if len(data_points) < self.trend_min_points:
                return None

            # Extract values and timestamps
            values = [point["value"] for point in data_points]
            timestamps = [point["timestamp"] for point in data_points]

            # Calculate trend statistics
            trend_stats = self._calculate_trend_statistics(values)

            # Determine trend direction and severity
            direction = self._determine_trend_direction(trend_stats)
            severity = self._determine_trend_severity(trend_stats, metric_name)

            # Calculate additional metrics
            volatility = self._calculate_volatility(values)
            correlation = self._calculate_autocorrelation(values)
            trend_strength = self._calculate_trend_strength(trend_stats, volatility)

            return TrendAnalysis(
                metric_name=metric_name,
                time_period=time_period,
                direction=direction,
                severity=severity,
                confidence=trend_stats["confidence"],
                slope=trend_stats["slope"],
                correlation=correlation,
                data_points=len(values),
                start_value=values[0],
                end_value=values[-1],
                change_percent=(
                    ((values[-1] - values[0]) / values[0]) * 100
                    if values[0] != 0
                    else 0
                ),
                volatility=volatility,
                trend_strength=trend_strength,
                context={
                    "time_range": f"{timestamps[0]} to {timestamps[-1]}",
                    "baseline": self.baselines.get(metric_name, {}),
                    "statistics": trend_stats,
                },
            )

        except Exception as e:
            telemetry.log_event(
                "metric_trend_analysis_error", metric=metric_name, error=str(e)
            )
            return None

    def _calculate_trend_statistics(self, values: List[float]) -> Dict[str, float]:
        """Calculate comprehensive trend statistics using linear regression."""
        n = len(values)
        if n < 2:
            return {"slope": 0, "intercept": 0, "r_squared": 0, "confidence": 0}

        # Linear regression calculation
        x = list(range(n))
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y**2 for y in values)

        # Avoid division by zero
        denominator = n * sum_x2 - sum_x**2
        if abs(denominator) < 1e-10:
            return {"slope": 0, "intercept": sum_y / n, "r_squared": 0, "confidence": 0}

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

        # Calculate R-squared (coefficient of determination)
        y_mean = sum_y / n
        ss_tot = sum((y - y_mean) ** 2 for y in values)
        ss_res = sum((values[i] - (slope * i + intercept)) ** 2 for i in range(n))

        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Calculate confidence based on R-squared and data points
        confidence = min(r_squared * (1 + math.log(n) / 10), 1.0)

        return {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_squared,
            "confidence": confidence,
            "mean": y_mean,
            "std": statistics.stdev(values) if n > 1 else 0,
        }

    def _determine_trend_direction(self, stats: Dict[str, float]) -> TrendDirection:
        """Determine the direction of the trend based on statistics."""
        slope = stats["slope"]
        confidence = stats["confidence"]
        r_squared = stats["r_squared"]

        # Low confidence or R-squared indicates unknown/volatile trend
        if confidence < 0.3 or r_squared < 0.1:
            return (
                TrendDirection.VOLATILE if r_squared > 0.05 else TrendDirection.UNKNOWN
            )

        # Determine direction based on slope
        if abs(slope) < 0.01:  # Very small slope
            return TrendDirection.STABLE
        elif slope > 0:
            return (
                TrendDirection.DEGRADING
            )  # For performance metrics, increasing usually means degrading
        else:
            return TrendDirection.IMPROVING

    def _determine_trend_severity(
        self, stats: Dict[str, float], metric_name: str
    ) -> TrendSeverity:
        """Determine the severity of the trend."""
        slope = abs(stats["slope"])
        confidence = stats["confidence"]
        baseline = self.baselines.get(metric_name, {})

        # Get baseline standard deviation for context
        baseline_std = baseline.get("std", 1.0)

        # Normalize slope by baseline standard deviation
        normalized_slope = slope / baseline_std if baseline_std > 0 else slope

        # Severity based on normalized slope and confidence
        severity_score = normalized_slope * confidence

        if severity_score < 0.1:
            return TrendSeverity.LOW
        elif severity_score < 0.3:
            return TrendSeverity.MEDIUM
        elif severity_score < 0.6:
            return TrendSeverity.HIGH
        else:
            return TrendSeverity.CRITICAL

    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (coefficient of variation) of the values."""
        if len(values) < 2:
            return 0.0

        mean_val = statistics.mean(values)
        if mean_val == 0:
            return 0.0

        std_val = statistics.stdev(values)
        return std_val / mean_val

    def _calculate_autocorrelation(self, values: List[float], lag: int = 1) -> float:
        """Calculate autocorrelation to detect patterns in the data."""
        if len(values) <= lag:
            return 0.0

        try:
            n = len(values)
            mean_val = statistics.mean(values)

            # Calculate autocorrelation at specified lag
            numerator = sum(
                (values[i] - mean_val) * (values[i - lag] - mean_val)
                for i in range(lag, n)
            )
            denominator = sum((x - mean_val) ** 2 for x in values)

            return numerator / denominator if denominator > 0 else 0.0

        except Exception:
            return 0.0

    def _calculate_trend_strength(
        self, stats: Dict[str, float], volatility: float
    ) -> float:
        """Calculate overall trend strength combining multiple factors."""
        r_squared = stats["r_squared"]
        confidence = stats["confidence"]

        # Trend strength is high R-squared, high confidence, low volatility
        volatility_factor = max(0, 1 - volatility)
        trend_strength = r_squared * 0.4 + confidence * 0.4 + volatility_factor * 0.2

        return min(trend_strength, 1.0)

    def detect_performance_anomalies(
        self, metric_names: Optional[List[str]] = None, lookback_hours: int = 24
    ) -> List[AnomalyDetection]:
        """Detect performance anomalies using statistical methods."""
        if not self.config.get("anomaly_detection", {}).get("enabled", True):
            return []

        try:
            if not metric_names:
                metric_names = self._get_available_performance_metrics()

            anomalies = []
            for metric_name in metric_names:
                metric_anomalies = self._detect_metric_anomalies(
                    metric_name, lookback_hours
                )
                anomalies.extend(metric_anomalies)

            # Cache and save anomalies
            self.anomaly_cache.extend(anomalies)
            self._save_anomalies(anomalies)

            telemetry.log_event(
                "anomaly_detection_completed",
                metrics_analyzed=len(metric_names),
                anomalies_found=len(anomalies),
            )

            return anomalies

        except Exception as e:
            telemetry.log_event("anomaly_detection_error", error=str(e))
            return []

    def _detect_metric_anomalies(
        self, metric_name: str, lookback_hours: int
    ) -> List[AnomalyDetection]:
        """Detect anomalies for a specific metric using multiple methods."""
        try:
            # Get recent data
            time_period = f"{lookback_hours}h"
            data_points = self._get_metric_history(metric_name, time_period)

            if len(data_points) < 10:  # Need minimum data for anomaly detection
                return []

            values = [point["value"] for point in data_points]
            timestamps = [point["timestamp"] for point in data_points]

            anomalies = []

            # Method 1: Z-score based detection
            z_score_anomalies = self._detect_zscore_anomalies(
                metric_name, values, timestamps
            )
            anomalies.extend(z_score_anomalies)

            # Method 2: Interquartile Range (IQR) based detection
            iqr_anomalies = self._detect_iqr_anomalies(metric_name, values, timestamps)
            anomalies.extend(iqr_anomalies)

            # Method 3: Moving average deviation
            ma_anomalies = self._detect_moving_average_anomalies(
                metric_name, values, timestamps
            )
            anomalies.extend(ma_anomalies)

            return anomalies

        except Exception as e:
            telemetry.log_event(
                "metric_anomaly_detection_error", metric=metric_name, error=str(e)
            )
            return []

    def _detect_zscore_anomalies(
        self, metric_name: str, values: List[float], timestamps: List[str]
    ) -> List[AnomalyDetection]:
        """Detect anomalies using Z-score method."""
        if len(values) < 3:
            return []

        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)

        if std_val == 0:
            return []

        anomalies = []
        threshold = self.anomaly_threshold

        for i, (value, timestamp) in enumerate(zip(values, timestamps)):
            z_score = abs(value - mean_val) / std_val

            if z_score > threshold:
                anomaly_type = "spike" if value > mean_val else "drop"
                severity = self._determine_anomaly_severity(z_score)

                anomalies.append(
                    AnomalyDetection(
                        metric_name=metric_name,
                        anomaly_timestamp=datetime.fromisoformat(
                            timestamp.replace("Z", "+00:00")
                        ),
                        anomaly_value=value,
                        expected_value=mean_val,
                        deviation_score=z_score,
                        anomaly_type=anomaly_type,
                        severity=severity,
                        context={
                            "method": "z_score",
                            "threshold": threshold,
                            "mean": mean_val,
                            "std": std_val,
                        },
                        detection_method="z_score",
                        confidence=min(z_score / threshold, 1.0),
                    )
                )

        return anomalies

    def _detect_iqr_anomalies(
        self, metric_name: str, values: List[float], timestamps: List[str]
    ) -> List[AnomalyDetection]:
        """Detect anomalies using Interquartile Range method."""
        if len(values) < 4:
            return []

        sorted_values = sorted(values)
        n = len(sorted_values)

        q1 = sorted_values[n // 4]
        q3 = sorted_values[3 * n // 4]
        iqr = q3 - q1

        if iqr == 0:
            return []

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        anomalies = []
        median_val = statistics.median(values)

        for i, (value, timestamp) in enumerate(zip(values, timestamps)):
            if value < lower_bound or value > upper_bound:
                anomaly_type = "outlier"
                deviation_score = max(
                    (lower_bound - value) / iqr if value < lower_bound else 0,
                    (value - upper_bound) / iqr if value > upper_bound else 0,
                )

                severity = self._determine_anomaly_severity(deviation_score)

                anomalies.append(
                    AnomalyDetection(
                        metric_name=metric_name,
                        anomaly_timestamp=datetime.fromisoformat(
                            timestamp.replace("Z", "+00:00")
                        ),
                        anomaly_value=value,
                        expected_value=median_val,
                        deviation_score=deviation_score,
                        anomaly_type=anomaly_type,
                        severity=severity,
                        context={
                            "method": "iqr",
                            "q1": q1,
                            "q3": q3,
                            "iqr": iqr,
                            "bounds": [lower_bound, upper_bound],
                        },
                        detection_method="iqr",
                        confidence=min(deviation_score / 2.0, 1.0),
                    )
                )

        return anomalies

    def _detect_moving_average_anomalies(
        self, metric_name: str, values: List[float], timestamps: List[str]
    ) -> List[AnomalyDetection]:
        """Detect anomalies using moving average deviation."""
        window_size = min(10, len(values) // 3)
        if window_size < 3:
            return []

        anomalies = []

        for i in range(window_size, len(values)):
            window = values[i - window_size : i]
            window_mean = statistics.mean(window)
            window_std = statistics.stdev(window) if len(window) > 1 else 1.0

            if window_std == 0:
                continue

            current_value = values[i]
            deviation = abs(current_value - window_mean) / window_std

            if deviation > self.anomaly_threshold:
                anomaly_type = "drift"
                severity = self._determine_anomaly_severity(deviation)

                anomalies.append(
                    AnomalyDetection(
                        metric_name=metric_name,
                        anomaly_timestamp=datetime.fromisoformat(
                            timestamps[i].replace("Z", "+00:00")
                        ),
                        anomaly_value=current_value,
                        expected_value=window_mean,
                        deviation_score=deviation,
                        anomaly_type=anomaly_type,
                        severity=severity,
                        context={
                            "method": "moving_average",
                            "window_size": window_size,
                            "window_mean": window_mean,
                            "window_std": window_std,
                        },
                        detection_method="moving_average",
                        confidence=min(deviation / self.anomaly_threshold, 1.0),
                    )
                )

        return anomalies

    def _determine_anomaly_severity(self, deviation_score: float) -> TrendSeverity:
        """Determine severity based on deviation score."""
        if deviation_score < 2.0:
            return TrendSeverity.LOW
        elif deviation_score < 3.0:
            return TrendSeverity.MEDIUM
        elif deviation_score < 4.0:
            return TrendSeverity.HIGH
        else:
            return TrendSeverity.CRITICAL

    def generate_performance_forecast(
        self, metric_name: str, horizon_days: Optional[int] = None
    ) -> Optional[PerformanceForecast]:
        """Generate performance forecast for a specific metric."""
        if not self.config.get("forecasting", {}).get("enabled", True):
            return None

        try:
            if horizon_days is None:
                horizon_days = self.forecast_horizon_days

            # Get historical data for forecasting
            data_points = self._get_metric_history(
                metric_name, "30d"
            )  # Use 30 days for forecasting

            if len(data_points) < 20:  # Need sufficient data for forecasting
                return None

            values = [point["value"] for point in data_points]

            # Generate forecast using multiple methods
            linear_forecast = self._linear_forecast(values, horizon_days)
            exponential_forecast = self._exponential_forecast(values, horizon_days)

            # Combine forecasts (simple average for now)
            combined_forecast = [
                (linear + exponential) / 2
                for linear, exponential in zip(linear_forecast, exponential_forecast)
            ]

            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(
                values, combined_forecast
            )

            # Determine forecast confidence
            forecast_confidence = self._determine_forecast_confidence(
                values, combined_forecast
            )

            # Generate recommendations
            recommendations = self._generate_forecast_recommendations(
                metric_name, values, combined_forecast, forecast_confidence
            )

            forecast = PerformanceForecast(
                metric_name=metric_name,
                forecast_horizon=f"{horizon_days}d",
                predicted_values=combined_forecast,
                confidence_intervals=confidence_intervals,
                forecast_confidence=forecast_confidence,
                methodology="combined_linear_exponential",
                assumptions=[
                    "Historical patterns continue",
                    "No major system changes",
                    "Current usage patterns persist",
                ],
                risk_factors=self._identify_forecast_risks(metric_name, values),
                recommendations=recommendations,
                metadata={
                    "data_points_used": len(values),
                    "forecast_methods": ["linear", "exponential"],
                    "baseline_stats": {
                        "mean": statistics.mean(values),
                        "std": statistics.stdev(values) if len(values) > 1 else 0,
                        "trend": self._calculate_trend_statistics(values),
                    },
                },
            )

            # Cache and save forecast
            self.forecast_cache[metric_name] = forecast
            self._save_forecast(forecast)

            return forecast

        except Exception as e:
            telemetry.log_event(
                "forecast_generation_error", metric=metric_name, error=str(e)
            )
            return None

    def _linear_forecast(self, values: List[float], horizon_days: int) -> List[float]:
        """Generate linear trend forecast."""
        trend_stats = self._calculate_trend_statistics(values)
        slope = trend_stats["slope"]
        intercept = trend_stats["intercept"]

        n = len(values)
        forecast = []

        for i in range(1, horizon_days + 1):
            predicted_value = slope * (n + i) + intercept
            forecast.append(max(0, predicted_value))  # Ensure non-negative values

        return forecast

    def _exponential_forecast(
        self, values: List[float], horizon_days: int
    ) -> List[float]:
        """Generate exponential smoothing forecast."""
        if len(values) < 2:
            return [values[0]] * horizon_days if values else [0] * horizon_days

        alpha = 0.3  # Smoothing parameter

        # Calculate exponential smoothing
        smoothed = [values[0]]
        for i in range(1, len(values)):
            smoothed_value = alpha * values[i] + (1 - alpha) * smoothed[i - 1]
            smoothed.append(smoothed_value)

        # Forecast future values
        last_smoothed = smoothed[-1]
        last_actual = values[-1]

        # Simple trend adjustment
        trend = (last_actual - smoothed[-2]) if len(smoothed) > 1 else 0

        forecast = []
        for i in range(horizon_days):
            predicted_value = last_smoothed + trend * (i + 1) * 0.1  # Dampened trend
            forecast.append(max(0, predicted_value))

        return forecast

    def _calculate_confidence_intervals(
        self, historical: List[float], forecast: List[float]
    ) -> List[Tuple[float, float]]:
        """Calculate confidence intervals for forecast values."""
        if len(historical) < 2:
            return [(value, value) for value in forecast]

        historical_std = statistics.stdev(historical)

        intervals = []
        for i, predicted in enumerate(forecast):
            # Increase uncertainty over time
            uncertainty = historical_std * (1 + i * 0.1)

            lower_bound = max(0, predicted - 1.96 * uncertainty)  # 95% confidence
            upper_bound = predicted + 1.96 * uncertainty

            intervals.append((lower_bound, upper_bound))

        return intervals

    def _determine_forecast_confidence(
        self, historical: List[float], forecast: List[float]
    ) -> ForecastConfidence:
        """Determine overall confidence in the forecast."""
        if len(historical) < 10:
            return ForecastConfidence.LOW

        # Calculate trend consistency
        trend_stats = self._calculate_trend_statistics(historical)
        r_squared = trend_stats["r_squared"]

        # Calculate volatility
        volatility = self._calculate_volatility(historical)

        # Confidence score based on R-squared and inverse volatility
        confidence_score = r_squared * (1 - min(volatility, 0.8))

        if confidence_score > 0.8:
            return ForecastConfidence.VERY_HIGH
        elif confidence_score > 0.6:
            return ForecastConfidence.HIGH
        elif confidence_score > 0.4:
            return ForecastConfidence.MEDIUM
        else:
            return ForecastConfidence.LOW

    def _generate_forecast_recommendations(
        self,
        metric_name: str,
        historical: List[float],
        forecast: List[float],
        confidence: ForecastConfidence,
    ) -> List[str]:
        """Generate actionable recommendations based on forecast."""
        recommendations = []

        # Analyze forecast trend
        if len(forecast) >= 7:
            week_1_avg = statistics.mean(forecast[:7])
            last_week_avg = (
                statistics.mean(historical[-7:])
                if len(historical) >= 7
                else historical[-1]
            )

            change_percent = (
                ((week_1_avg - last_week_avg) / last_week_avg) * 100
                if last_week_avg != 0
                else 0
            )

            if change_percent > 20:
                recommendations.append(
                    f"⚠️ {metric_name} expected to increase by {change_percent:.1f}% - consider capacity planning"
                )
            elif change_percent < -20:
                recommendations.append(
                    f"📈 {metric_name} expected to improve by {abs(change_percent):.1f}% - monitor for sustained improvement"
                )

        # Confidence-based recommendations
        if confidence == ForecastConfidence.LOW:
            recommendations.append(
                "⚠️ Low forecast confidence - increase monitoring frequency and collect more data"
            )
        elif confidence == ForecastConfidence.VERY_HIGH:
            recommendations.append(
                "✅ High forecast confidence - suitable for capacity planning and SLA setting"
            )

        # Metric-specific recommendations
        if metric_name == "cpu_usage":
            if max(forecast) > 80:
                recommendations.append(
                    "🔥 CPU usage forecast exceeds 80% - plan for scaling or optimization"
                )
        elif metric_name == "memory_usage":
            if max(forecast) > 85:
                recommendations.append(
                    "💾 Memory usage forecast exceeds 85% - consider memory optimization or scaling"
                )
        elif metric_name == "response_time":
            if max(forecast) > 1000:
                recommendations.append(
                    "⏱️ Response time forecast exceeds 1s - investigate performance bottlenecks"
                )

        if not recommendations:
            recommendations.append(
                "📊 Forecast indicates stable performance - continue monitoring"
            )

        return recommendations

    def _identify_forecast_risks(
        self, metric_name: str, values: List[float]
    ) -> List[str]:
        """Identify risk factors that could affect forecast accuracy."""
        risks = []

        # High volatility risk
        volatility = self._calculate_volatility(values)
        if volatility > 0.5:
            risks.append("High historical volatility may reduce forecast accuracy")

        # Limited data risk
        if len(values) < 30:
            risks.append("Limited historical data may affect forecast reliability")

        # Trend change risk
        recent_trend = (
            self._calculate_trend_statistics(values[-10:])
            if len(values) >= 10
            else None
        )
        overall_trend = self._calculate_trend_statistics(values)

        if (
            recent_trend
            and abs(recent_trend["slope"] - overall_trend["slope"])
            > overall_trend["std"]
        ):
            risks.append(
                "Recent trend changes detected - forecast may not capture new patterns"
            )

        # Seasonal patterns (basic check)
        if len(values) >= 7:
            weekly_pattern = self._detect_weekly_pattern(values)
            if weekly_pattern:
                risks.append(
                    "Weekly patterns detected - consider seasonal forecasting methods"
                )

        return risks

    def _detect_weekly_pattern(self, values: List[float]) -> bool:
        """Basic weekly pattern detection."""
        if len(values) < 14:  # Need at least 2 weeks
            return False

        try:
            # Simple autocorrelation at lag 7 (weekly)
            weekly_correlation = self._calculate_autocorrelation(values, lag=7)
            return weekly_correlation > 0.3
        except Exception:
            return False

    def generate_performance_insights(
        self, lookback_days: int = 30
    ) -> List[PerformanceInsight]:
        """Generate actionable performance insights from trend analysis."""
        if not self.config.get("insights", {}).get("enabled", True):
            return []

        try:
            insights = []

            # Analyze recent trends
            trends = self.analyze_performance_trends(time_period=f"{lookback_days}d")

            # Detect anomalies
            anomalies = self.detect_performance_anomalies(
                lookback_hours=lookback_days * 24
            )

            # Generate insights from trends
            trend_insights = self._generate_trend_insights(trends)
            insights.extend(trend_insights)

            # Generate insights from anomalies
            anomaly_insights = self._generate_anomaly_insights(anomalies)
            insights.extend(anomaly_insights)

            # Generate capacity planning insights
            capacity_insights = self._generate_capacity_insights(trends)
            insights.extend(capacity_insights)

            # Prioritize insights
            prioritized_insights = self._prioritize_insights(insights)

            # Save insights
            self._save_insights(prioritized_insights)

            telemetry.log_event(
                "performance_insights_generated",
                insights_count=len(prioritized_insights),
                trends_analyzed=len(trends),
                anomalies_found=len(anomalies),
            )

            return prioritized_insights

        except Exception as e:
            telemetry.log_event("insight_generation_error", error=str(e))
            return []

    def _generate_trend_insights(
        self, trends: List[TrendAnalysis]
    ) -> List[PerformanceInsight]:
        """Generate insights from trend analysis results."""
        insights = []

        for trend in trends:
            if trend.severity in [TrendSeverity.HIGH, TrendSeverity.CRITICAL]:
                if trend.direction == TrendDirection.DEGRADING:
                    insight = PerformanceInsight(
                        insight_id=f"trend_degrading_{trend.metric_name}_{int(time.time())}",
                        title=f"Performance Degradation Detected: {trend.metric_name}",
                        description=f"{trend.metric_name} has shown a {trend.severity.value} degrading trend over {trend.time_period} with {trend.change_percent:.1f}% increase",
                        category="optimization",
                        priority=trend.severity.value,
                        affected_metrics=[trend.metric_name],
                        evidence={
                            "trend_direction": trend.direction.value,
                            "severity": trend.severity.value,
                            "confidence": trend.confidence,
                            "change_percent": trend.change_percent,
                            "data_points": trend.data_points,
                        },
                        recommendations=self._generate_degradation_recommendations(
                            trend
                        ),
                        estimated_impact=(
                            "high"
                            if trend.severity == TrendSeverity.CRITICAL
                            else "medium"
                        ),
                        implementation_effort="medium",
                    )
                    insights.append(insight)

                elif (
                    trend.direction == TrendDirection.IMPROVING
                    and trend.confidence > 0.7
                ):
                    insight = PerformanceInsight(
                        insight_id=f"trend_improving_{trend.metric_name}_{int(time.time())}",
                        title=f"Performance Improvement Detected: {trend.metric_name}",
                        description=f"{trend.metric_name} has shown consistent improvement over {trend.time_period} with {abs(trend.change_percent):.1f}% decrease",
                        category="efficiency",
                        priority="low",
                        affected_metrics=[trend.metric_name],
                        evidence={
                            "trend_direction": trend.direction.value,
                            "confidence": trend.confidence,
                            "change_percent": trend.change_percent,
                            "trend_strength": trend.trend_strength,
                        },
                        recommendations=[
                            f"Document the factors contributing to {trend.metric_name} improvement",
                            "Consider applying similar optimizations to other metrics",
                            "Monitor to ensure improvement is sustained",
                        ],
                        estimated_impact="positive",
                        implementation_effort="low",
                    )
                    insights.append(insight)

        return insights

    def _generate_degradation_recommendations(self, trend: TrendAnalysis) -> List[str]:
        """Generate specific recommendations for performance degradation."""
        recommendations = []
        metric = trend.metric_name.lower()

        if "cpu" in metric:
            recommendations.extend(
                [
                    "Analyze CPU-intensive processes and optimize algorithms",
                    "Consider horizontal scaling or CPU upgrade",
                    "Review recent code changes for performance regressions",
                    "Implement CPU usage monitoring and alerting",
                ]
            )
        elif "memory" in metric:
            recommendations.extend(
                [
                    "Investigate memory leaks and optimize memory usage",
                    "Review caching strategies and garbage collection",
                    "Consider memory scaling or optimization",
                    "Analyze memory allocation patterns",
                ]
            )
        elif "response" in metric or "latency" in metric:
            recommendations.extend(
                [
                    "Profile application performance and identify bottlenecks",
                    "Optimize database queries and caching",
                    "Review network latency and connection pooling",
                    "Consider load balancing and caching strategies",
                ]
            )
        else:
            recommendations.extend(
                [
                    f"Investigate root causes of {trend.metric_name} degradation",
                    "Review recent system changes and deployments",
                    "Implement monitoring and alerting for early detection",
                    "Consider capacity planning and scaling options",
                ]
            )

        return recommendations

    def _generate_anomaly_insights(
        self, anomalies: List[AnomalyDetection]
    ) -> List[PerformanceInsight]:
        """Generate insights from anomaly detection results."""
        insights = []

        # Group anomalies by metric and type
        anomaly_groups = defaultdict(list)
        for anomaly in anomalies:
            key = f"{anomaly.metric_name}_{anomaly.anomaly_type}"
            anomaly_groups[key].append(anomaly)

        for group_key, group_anomalies in anomaly_groups.items():
            if len(group_anomalies) >= 3:  # Multiple anomalies indicate a pattern
                metric_name = group_anomalies[0].metric_name
                anomaly_type = group_anomalies[0].anomaly_type

                insight = PerformanceInsight(
                    insight_id=f"anomaly_pattern_{group_key}_{int(time.time())}",
                    title=f"Recurring Performance Anomalies: {metric_name}",
                    description=f"Detected {len(group_anomalies)} {anomaly_type} anomalies in {metric_name} indicating potential systemic issues",
                    category="reliability",
                    priority=(
                        "high"
                        if any(
                            a.severity == TrendSeverity.CRITICAL
                            for a in group_anomalies
                        )
                        else "medium"
                    ),
                    affected_metrics=[metric_name],
                    evidence={
                        "anomaly_count": len(group_anomalies),
                        "anomaly_type": anomaly_type,
                        "severity_distribution": [
                            a.severity.value for a in group_anomalies
                        ],
                        "detection_methods": list(
                            set(a.detection_method for a in group_anomalies)
                        ),
                    },
                    recommendations=[
                        f"Investigate root cause of recurring {anomaly_type} anomalies in {metric_name}",
                        "Review system logs and monitoring data during anomaly periods",
                        "Consider implementing automated anomaly response procedures",
                        "Adjust monitoring thresholds based on anomaly patterns",
                    ],
                    estimated_impact="high",
                    implementation_effort="medium",
                )
                insights.append(insight)

        return insights

    def _generate_capacity_insights(
        self, trends: List[TrendAnalysis]
    ) -> List[PerformanceInsight]:
        """Generate capacity planning insights."""
        insights = []

        for trend in trends:
            if trend.direction == TrendDirection.DEGRADING and trend.confidence > 0.6:
                # Generate forecast for capacity planning
                forecast = self.generate_performance_forecast(
                    trend.metric_name, horizon_days=90
                )

                if forecast and forecast.forecast_confidence in [
                    ForecastConfidence.HIGH,
                    ForecastConfidence.VERY_HIGH,
                ]:
                    max_forecast = max(forecast.predicted_values)

                    # Check if forecast exceeds capacity thresholds
                    threshold_exceeded = False
                    threshold_value = 0

                    if "cpu" in trend.metric_name.lower() and max_forecast > 80:
                        threshold_exceeded = True
                        threshold_value = 80
                    elif "memory" in trend.metric_name.lower() and max_forecast > 85:
                        threshold_exceeded = True
                        threshold_value = 85

                    if threshold_exceeded:
                        insight = PerformanceInsight(
                            insight_id=f"capacity_planning_{trend.metric_name}_{int(time.time())}",
                            title=f"Capacity Planning Alert: {trend.metric_name}",
                            description=f"{trend.metric_name} forecast indicates potential capacity issues within 90 days, with predicted peak of {max_forecast:.1f}% (threshold: {threshold_value}%)",
                            category="capacity",
                            priority="high",
                            affected_metrics=[trend.metric_name],
                            evidence={
                                "current_trend": trend.direction.value,
                                "forecast_peak": max_forecast,
                                "threshold": threshold_value,
                                "forecast_confidence": forecast.forecast_confidence.value,
                                "time_to_threshold": self._estimate_time_to_threshold(
                                    forecast, threshold_value
                                ),
                            },
                            recommendations=[
                                f"Plan for {trend.metric_name} scaling before reaching {threshold_value}% threshold",
                                "Review current capacity and scaling policies",
                                "Consider proactive scaling or optimization measures",
                                "Set up automated alerts for capacity thresholds",
                            ],
                            estimated_impact="critical",
                            implementation_effort="high",
                        )
                        insights.append(insight)

        return insights

    def _estimate_time_to_threshold(
        self, forecast: PerformanceForecast, threshold: float
    ) -> Optional[str]:
        """Estimate time until threshold is reached based on forecast."""
        for i, value in enumerate(forecast.predicted_values):
            if value > threshold:
                return f"{i + 1} days"
        return None

    def _prioritize_insights(
        self, insights: List[PerformanceInsight]
    ) -> List[PerformanceInsight]:
        """Prioritize insights based on impact and urgency."""
        priority_weights = self.config.get("insights", {}).get(
            "priority_weights",
            {"performance_impact": 0.4, "frequency": 0.3, "trend_strength": 0.3},
        )

        # Sort by priority and category
        priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        category_order = {
            "capacity": 4,
            "reliability": 3,
            "optimization": 2,
            "efficiency": 1,
        }

        def priority_score(insight: PerformanceInsight) -> Tuple[int, int]:
            priority_val = priority_order.get(insight.priority, 0)
            category_val = category_order.get(insight.category, 0)
            return (priority_val, category_val)

        return sorted(insights, key=priority_score, reverse=True)

    def _get_available_performance_metrics(self) -> List[str]:
        """Get list of available performance metrics."""
        # This would query the metrics collector for available metrics
        # For now, return common performance metrics
        return [
            "cpu_usage",
            "memory_usage",
            "response_time",
            "error_rate",
            "disk_io",
            "network_io",
        ]

    def _get_metric_history(
        self, metric_name: str, time_period: str
    ) -> List[Dict[str, Any]]:
        """Get historical data for a specific metric."""
        # This would query the unified metrics collector
        # For now, return mock data for demonstration

        # Parse time period
        if time_period.endswith("d"):
            days = int(time_period[:-1])
        elif time_period.endswith("h"):
            days = int(time_period[:-1]) / 24
        else:
            days = 1

        # Generate mock historical data
        import random

        now = datetime.now()
        data_points = []

        for i in range(int(days * 24)):  # Hourly data points
            timestamp = now - timedelta(hours=i)

            # Generate realistic mock data based on metric type
            if "cpu" in metric_name.lower():
                base_value = 25.0
                variation = random.gauss(0, 10)
            elif "memory" in metric_name.lower():
                base_value = 45.0
                variation = random.gauss(0, 15)
            elif "response" in metric_name.lower():
                base_value = 200.0
                variation = random.gauss(0, 50)
            else:
                base_value = 50.0
                variation = random.gauss(0, 20)

            value = max(
                0, base_value + variation + (i * 0.1)
            )  # Add slight upward trend

            data_points.append(
                {
                    "timestamp": timestamp.isoformat(),
                    "value": value,
                    "metric_name": metric_name,
                }
            )

        return list(reversed(data_points))  # Return chronological order

    def _save_trends(self, trends: List[TrendAnalysis]):
        """Save trend analysis results to persistent storage."""
        try:
            for trend in trends:
                trend_data = {
                    "id": f"trend_{trend.metric_name}_{trend.time_period}_{int(time.time())}",
                    "timestamp": trend.analysis_timestamp.isoformat(),
                    "metric_name": trend.metric_name,
                    "time_period": trend.time_period,
                    "direction": trend.direction.value,
                    "severity": trend.severity.value,
                    "confidence": trend.confidence,
                    "slope": trend.slope,
                    "correlation": trend.correlation,
                    "data_points": trend.data_points,
                    "start_value": trend.start_value,
                    "end_value": trend.end_value,
                    "change_percent": trend.change_percent,
                    "volatility": trend.volatility,
                    "trend_strength": trend.trend_strength,
                    "context": trend.context,
                }

                utils.append_jsonl(self.trends_path, trend_data)

        except Exception as e:
            telemetry.log_event("trend_save_error", error=str(e))

    def _save_anomalies(self, anomalies: List[AnomalyDetection]):
        """Save anomaly detection results to persistent storage."""
        try:
            for anomaly in anomalies:
                anomaly_data = {
                    "id": f"anomaly_{anomaly.metric_name}_{int(anomaly.anomaly_timestamp.timestamp())}",
                    "timestamp": datetime.now().isoformat(),
                    "metric_name": anomaly.metric_name,
                    "anomaly_timestamp": anomaly.anomaly_timestamp.isoformat(),
                    "anomaly_value": anomaly.anomaly_value,
                    "expected_value": anomaly.expected_value,
                    "deviation_score": anomaly.deviation_score,
                    "anomaly_type": anomaly.anomaly_type,
                    "severity": anomaly.severity.value,
                    "context": anomaly.context,
                    "detection_method": anomaly.detection_method,
                    "confidence": anomaly.confidence,
                }

                utils.append_jsonl(self.anomalies_path, anomaly_data)

        except Exception as e:
            telemetry.log_event("anomaly_save_error", error=str(e))

    def _save_forecast(self, forecast: PerformanceForecast):
        """Save performance forecast to persistent storage."""
        try:
            forecast_data = {
                "id": f"forecast_{forecast.metric_name}_{int(forecast.created_at.timestamp())}",
                "timestamp": forecast.created_at.isoformat(),
                "metric_name": forecast.metric_name,
                "forecast_horizon": forecast.forecast_horizon,
                "predicted_values": forecast.predicted_values,
                "confidence_intervals": forecast.confidence_intervals,
                "forecast_confidence": forecast.forecast_confidence.value,
                "methodology": forecast.methodology,
                "assumptions": forecast.assumptions,
                "risk_factors": forecast.risk_factors,
                "recommendations": forecast.recommendations,
                "metadata": forecast.metadata,
            }

            utils.append_jsonl(self.forecasts_path, forecast_data)

        except Exception as e:
            telemetry.log_event("forecast_save_error", error=str(e))

    def _save_insights(self, insights: List[PerformanceInsight]):
        """Save performance insights to persistent storage."""
        try:
            for insight in insights:
                insight_data = {
                    "id": insight.insight_id,
                    "timestamp": insight.created_at.isoformat(),
                    "title": insight.title,
                    "description": insight.description,
                    "category": insight.category,
                    "priority": insight.priority,
                    "affected_metrics": insight.affected_metrics,
                    "evidence": insight.evidence,
                    "recommendations": insight.recommendations,
                    "estimated_impact": insight.estimated_impact,
                    "implementation_effort": insight.implementation_effort,
                }

                utils.append_jsonl(self.insights_path, insight_data)

        except Exception as e:
            telemetry.log_event("insight_save_error", error=str(e))


# Factory function
def get_performance_trend_analyzer(root: Path) -> PerformanceTrendAnalyzer:
    """Get or create a PerformanceTrendAnalyzer instance."""
    return PerformanceTrendAnalyzer(root)
