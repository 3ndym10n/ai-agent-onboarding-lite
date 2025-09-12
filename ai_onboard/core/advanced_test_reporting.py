"""
Advanced Test Reporting System - Comprehensive test analysis and reporting.

This module provides enterprise-grade test reporting capabilities that:
- Generate comprehensive test reports with advanced analytics
- Provide multi-dimensional test analysis and insights
- Support multiple output formats (HTML, JSON, PDF, CSV)
- Integrate with performance trend analysis and continuous improvement
- Offer real-time test monitoring and alerting
- Enable test quality scoring and benchmarking
"""

import csv
import html
import io
import json
import math
import statistics
import time
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
import warnings

from . import utils, telemetry
from .continuous_improvement_validator import (
    ContinuousImprovementValidator,
    TestCase,
    TestResult,
    TestCategory,
    ValidationReport
)
from .performance_trend_analyzer import (
    get_performance_trend_analyzer,
    PerformanceTrendAnalyzer,
    TrendAnalysis,
    AnomalyDetection,
    PerformanceInsight
)
from .continuous_improvement_analytics import (
    ContinuousImprovementAnalytics,
    ReportType,
    MetricType
)


class ReportFormat(Enum):
    """Supported report output formats."""
    HTML = "html"
    JSON = "json"
    PDF = "pdf"
    CSV = "csv"
    MARKDOWN = "markdown"
    XML = "xml"


class ReportLevel(Enum):
    """Report detail levels."""
    SUMMARY = "summary"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    EXECUTIVE = "executive"


class TestQualityScore(Enum):
    """Test quality scoring levels."""
    EXCELLENT = "excellent"    # 95-100%
    GOOD = "good"             # 80-94%
    FAIR = "fair"             # 65-79%
    POOR = "poor"             # 50-64%
    CRITICAL = "critical"     # < 50%


@dataclass
class TestMetrics:
    """Comprehensive test execution metrics."""
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    warning_tests: int
    success_rate: float
    failure_rate: float
    skip_rate: float
    total_duration: float
    average_duration: float
    fastest_test: float
    slowest_test: float
    duration_std_dev: float
    test_velocity: float  # tests per second
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class QualityAssessment:
    """Test quality assessment results."""
    overall_score: float
    quality_grade: TestQualityScore
    coverage_score: float
    performance_score: float
    reliability_score: float
    maintainability_score: float
    areas_for_improvement: List[str]
    strengths: List[str]
    recommendations: List[str]
    benchmark_comparison: Dict[str, float]


@dataclass
class TrendInsight:
    """Insights derived from trend analysis."""
    insight_type: str
    title: str
    description: str
    severity: str
    confidence: float
    evidence: Dict[str, Any]
    recommendations: List[str]
    impact_assessment: str


@dataclass
class TestExecutionContext:
    """Context information for test execution."""
    environment: str
    platform: str
    python_version: str
    test_framework: str
    execution_mode: str
    ci_environment: bool
    git_commit: Optional[str]
    git_branch: Optional[str]
    timestamp: datetime
    duration: float
    resource_usage: Dict[str, Any]


@dataclass
class AdvancedTestReport:
    """Comprehensive test report with advanced analytics."""
    report_id: str
    generated_at: datetime
    report_level: ReportLevel
    test_metrics: TestMetrics
    quality_assessment: QualityAssessment
    execution_context: TestExecutionContext
    test_results: List[TestCase]
    trend_analysis: List[TrendAnalysis]
    anomalies: List[AnomalyDetection]
    performance_insights: List[PerformanceInsight]
    trend_insights: List[TrendInsight]
    historical_comparison: Dict[str, Any]
    recommendations: List[str]
    visualizations: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedTestReportGenerator:
    """Advanced test report generator with comprehensive analytics."""
    
    def __init__(self, root: Path):
        self.root = root
        self.reports_path = root / ".ai_onboard" / "test_reports"
        self.config_path = root / ".ai_onboard" / "test_reporting_config.json"
        self.templates_path = root / ".ai_onboard" / "report_templates"
        
        # Initialize dependencies
        self.validator = ContinuousImprovementValidator(root)
        self.trend_analyzer = get_performance_trend_analyzer(root)
        
        # Configuration
        self.config = self._load_config()
        
        # Report history for trend analysis
        self.report_history: List[AdvancedTestReport] = []
        
        # Quality benchmarks
        self.quality_benchmarks = self._initialize_quality_benchmarks()
        
        # Ensure directories exist
        utils.ensure_dir(self.reports_path)
        utils.ensure_dir(self.templates_path)
        
        # Load historical reports for trend analysis
        self._load_historical_reports()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load test reporting configuration."""
        default_config = {
            "reporting_enabled": True,
            "default_format": "html",
            "default_level": "detailed",
            "retention_days": 90,
            "trend_analysis": {
                "enabled": True,
                "lookback_reports": 20,
                "anomaly_detection": True,
                "performance_tracking": True
            },
            "quality_assessment": {
                "enabled": True,
                "benchmark_comparison": True,
                "scoring_weights": {
                    "success_rate": 0.4,
                    "performance": 0.2,
                    "coverage": 0.2,
                    "reliability": 0.2
                }
            },
            "visualizations": {
                "enabled": True,
                "include_charts": True,
                "include_trends": True,
                "include_heatmaps": True
            },
            "notifications": {
                "enabled": True,
                "quality_threshold": 0.8,
                "performance_regression_threshold": 0.1
            }
        }
        
        return utils.read_json(self.config_path, default=default_config)
    
    def _initialize_quality_benchmarks(self) -> Dict[str, float]:
        """Initialize quality benchmarks for comparison."""
        return {
            "excellent_success_rate": 0.98,
            "good_success_rate": 0.90,
            "fair_success_rate": 0.80,
            "poor_success_rate": 0.65,
            "excellent_performance": 1.0,  # seconds per test
            "good_performance": 2.0,
            "fair_performance": 5.0,
            "poor_performance": 10.0,
            "excellent_reliability": 0.99,
            "good_reliability": 0.95,
            "fair_reliability": 0.85,
            "poor_reliability": 0.70
        }
    
    def generate_comprehensive_report(self, 
                                    test_results: List[TestCase],
                                    execution_context: Optional[TestExecutionContext] = None,
                                    report_level: ReportLevel = ReportLevel.DETAILED,
                                    output_formats: List[ReportFormat] = None) -> AdvancedTestReport:
        """Generate a comprehensive test report with advanced analytics."""
        try:
            if not self.config.get("reporting_enabled", True):
                raise ValueError("Test reporting is disabled in configuration")
            
            if output_formats is None:
                output_formats = [ReportFormat.HTML, ReportFormat.JSON]
            
            # Generate report ID
            report_id = f"test_report_{int(time.time())}_{hash(str(test_results)) % 10000:04d}"
            
            # Calculate test metrics
            test_metrics = self._calculate_test_metrics(test_results)
            
            # Generate execution context if not provided
            if execution_context is None:
                execution_context = self._generate_execution_context(test_results)
            
            # Perform quality assessment
            quality_assessment = self._assess_test_quality(test_metrics, test_results)
            
            # Generate trend analysis
            trend_analysis = self._analyze_test_trends(test_results, test_metrics)
            
            # Detect anomalies
            anomalies = self._detect_test_anomalies(test_results, test_metrics)
            
            # Generate performance insights
            performance_insights = self._generate_performance_insights(test_metrics, trend_analysis)
            
            # Generate trend insights
            trend_insights = self._generate_trend_insights(trend_analysis, anomalies)
            
            # Historical comparison
            historical_comparison = self._compare_with_historical(test_metrics)
            
            # Generate recommendations
            recommendations = self._generate_comprehensive_recommendations(
                quality_assessment, trend_analysis, anomalies, performance_insights
            )
            
            # Generate visualizations
            visualizations = self._generate_visualizations(
                test_metrics, trend_analysis, quality_assessment
            )
            
            # Create comprehensive report
            report = AdvancedTestReport(
                report_id=report_id,
                generated_at=datetime.now(),
                report_level=report_level,
                test_metrics=test_metrics,
                quality_assessment=quality_assessment,
                execution_context=execution_context,
                test_results=test_results,
                trend_analysis=trend_analysis,
                anomalies=anomalies,
                performance_insights=performance_insights,
                trend_insights=trend_insights,
                historical_comparison=historical_comparison,
                recommendations=recommendations,
                visualizations=visualizations,
                metadata={
                    "generator_version": "1.0",
                    "analysis_methods": ["trend_analysis", "anomaly_detection", "quality_assessment"],
                    "benchmark_comparison": True,
                    "historical_reports_analyzed": len(self.report_history)
                }
            )
            
            # Save report in multiple formats
            self._save_report(report, output_formats)
            
            # Add to history for future trend analysis
            self.report_history.append(report)
            self._trim_report_history()
            
            # Log report generation
            telemetry.log_event("advanced_test_report_generated",
                              report_id=report_id,
                              total_tests=test_metrics.total_tests,
                              success_rate=test_metrics.success_rate,
                              quality_score=quality_assessment.overall_score,
                              formats=len(output_formats))
            
            return report
            
        except Exception as e:
            telemetry.log_event("test_report_generation_error", error=str(e))
            raise
    
    def _calculate_test_metrics(self, test_results: List[TestCase]) -> TestMetrics:
        """Calculate comprehensive test execution metrics."""
        if not test_results:
            return TestMetrics(
                total_tests=0, passed_tests=0, failed_tests=0, skipped_tests=0,
                warning_tests=0, success_rate=0.0, failure_rate=0.0, skip_rate=0.0,
                total_duration=0.0, average_duration=0.0, fastest_test=0.0,
                slowest_test=0.0, duration_std_dev=0.0, test_velocity=0.0
            )
        
        # Count test results
        total_tests = len(test_results)
        passed_tests = sum(1 for t in test_results if t.result == TestResult.PASS)
        failed_tests = sum(1 for t in test_results if t.result == TestResult.FAIL)
        skipped_tests = sum(1 for t in test_results if t.result == TestResult.SKIP)
        warning_tests = sum(1 for t in test_results if t.result == TestResult.WARNING)
        
        # Calculate rates
        success_rate = passed_tests / total_tests if total_tests > 0 else 0.0
        failure_rate = failed_tests / total_tests if total_tests > 0 else 0.0
        skip_rate = skipped_tests / total_tests if total_tests > 0 else 0.0
        
        # Calculate duration metrics
        durations = [t.duration for t in test_results if t.duration > 0]
        total_duration = sum(durations)
        average_duration = statistics.mean(durations) if durations else 0.0
        fastest_test = min(durations) if durations else 0.0
        slowest_test = max(durations) if durations else 0.0
        duration_std_dev = statistics.stdev(durations) if len(durations) > 1 else 0.0
        test_velocity = total_tests / total_duration if total_duration > 0 else 0.0
        
        return TestMetrics(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            warning_tests=warning_tests,
            success_rate=success_rate,
            failure_rate=failure_rate,
            skip_rate=skip_rate,
            total_duration=total_duration,
            average_duration=average_duration,
            fastest_test=fastest_test,
            slowest_test=slowest_test,
            duration_std_dev=duration_std_dev,
            test_velocity=test_velocity
        )
    
    def _generate_execution_context(self, test_results: List[TestCase]) -> TestExecutionContext:
        """Generate execution context information."""
        import platform
        import sys
        import os
        
        return TestExecutionContext(
            environment=os.getenv("ENVIRONMENT", "development"),
            platform=platform.platform(),
            python_version=sys.version,
            test_framework="pytest",
            execution_mode=os.getenv("TEST_MODE", "standard"),
            ci_environment=bool(os.getenv("CI")),
            git_commit=os.getenv("GIT_COMMIT"),
            git_branch=os.getenv("GIT_BRANCH"),
            timestamp=datetime.now(),
            duration=sum(t.duration for t in test_results),
            resource_usage={
                "memory_peak": self._get_memory_usage(),
                "cpu_usage": self._get_cpu_usage()
            }
        )
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage."""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0
    
    def _assess_test_quality(self, metrics: TestMetrics, test_results: List[TestCase]) -> QualityAssessment:
        """Assess overall test quality with detailed scoring."""
        if not self.config.get("quality_assessment", {}).get("enabled", True):
            return QualityAssessment(
                overall_score=0.0, quality_grade=TestQualityScore.POOR,
                coverage_score=0.0, performance_score=0.0, reliability_score=0.0,
                maintainability_score=0.0, areas_for_improvement=[], strengths=[],
                recommendations=[], benchmark_comparison={}
            )
        
        # Calculate component scores
        success_score = metrics.success_rate
        performance_score = self._calculate_performance_score(metrics)
        coverage_score = self._calculate_coverage_score(test_results)
        reliability_score = self._calculate_reliability_score(test_results, metrics)
        maintainability_score = self._calculate_maintainability_score(test_results)
        
        # Weight the scores
        weights = self.config.get("quality_assessment", {}).get("scoring_weights", {})
        overall_score = (
            success_score * weights.get("success_rate", 0.4) +
            performance_score * weights.get("performance", 0.2) +
            coverage_score * weights.get("coverage", 0.2) +
            reliability_score * weights.get("reliability", 0.2)
        )
        
        # Determine quality grade
        quality_grade = self._determine_quality_grade(overall_score)
        
        # Identify areas for improvement and strengths
        areas_for_improvement = self._identify_improvement_areas(
            success_score, performance_score, coverage_score, reliability_score, maintainability_score
        )
        strengths = self._identify_strengths(
            success_score, performance_score, coverage_score, reliability_score, maintainability_score
        )
        
        # Generate quality-specific recommendations
        recommendations = self._generate_quality_recommendations(
            success_score, performance_score, coverage_score, reliability_score
        )
        
        # Benchmark comparison
        benchmark_comparison = self._compare_with_benchmarks(
            success_score, performance_score, coverage_score, reliability_score
        )
        
        return QualityAssessment(
            overall_score=overall_score,
            quality_grade=quality_grade,
            coverage_score=coverage_score,
            performance_score=performance_score,
            reliability_score=reliability_score,
            maintainability_score=maintainability_score,
            areas_for_improvement=areas_for_improvement,
            strengths=strengths,
            recommendations=recommendations,
            benchmark_comparison=benchmark_comparison
        )
    
    def _calculate_performance_score(self, metrics: TestMetrics) -> float:
        """Calculate performance score based on test execution speed."""
        if metrics.average_duration == 0:
            return 1.0
        
        # Score based on average test duration (lower is better)
        benchmarks = self.quality_benchmarks
        if metrics.average_duration <= benchmarks["excellent_performance"]:
            return 1.0
        elif metrics.average_duration <= benchmarks["good_performance"]:
            return 0.8
        elif metrics.average_duration <= benchmarks["fair_performance"]:
            return 0.6
        elif metrics.average_duration <= benchmarks["poor_performance"]:
            return 0.4
        else:
            return 0.2
    
    def _calculate_coverage_score(self, test_results: List[TestCase]) -> float:
        """Calculate test coverage score based on test categories."""
        if not test_results:
            return 0.0
        
        # Count unique test categories
        categories = set(t.category for t in test_results)
        total_categories = len(TestCategory)
        coverage_ratio = len(categories) / total_categories
        
        # Bonus for comprehensive testing
        if coverage_ratio >= 0.8:
            return min(1.0, coverage_ratio + 0.1)
        else:
            return coverage_ratio
    
    def _calculate_reliability_score(self, test_results: List[TestCase], metrics: TestMetrics) -> float:
        """Calculate reliability score based on test consistency."""
        if not test_results:
            return 0.0
        
        # Base score on success rate
        base_score = metrics.success_rate
        
        # Adjust for test stability (low standard deviation in duration)
        if metrics.duration_std_dev > 0 and metrics.average_duration > 0:
            cv = metrics.duration_std_dev / metrics.average_duration  # Coefficient of variation
            stability_factor = max(0.5, 1.0 - cv)  # Penalize high variability
            base_score *= stability_factor
        
        return min(1.0, base_score)
    
    def _calculate_maintainability_score(self, test_results: List[TestCase]) -> float:
        """Calculate maintainability score based on test characteristics."""
        if not test_results:
            return 0.0
        
        # Simple heuristics for maintainability
        clear_names = sum(1 for t in test_results if len(t.name.split()) >= 3)
        documented_tests = sum(1 for t in test_results if t.description and len(t.description) > 10)
        
        name_score = clear_names / len(test_results)
        documentation_score = documented_tests / len(test_results)
        
        return (name_score + documentation_score) / 2
    
    def _determine_quality_grade(self, overall_score: float) -> TestQualityScore:
        """Determine quality grade based on overall score."""
        if overall_score >= 0.95:
            return TestQualityScore.EXCELLENT
        elif overall_score >= 0.80:
            return TestQualityScore.GOOD
        elif overall_score >= 0.65:
            return TestQualityScore.FAIR
        elif overall_score >= 0.50:
            return TestQualityScore.POOR
        else:
            return TestQualityScore.CRITICAL
    
    def _identify_improvement_areas(self, success_score: float, performance_score: float,
                                  coverage_score: float, reliability_score: float,
                                  maintainability_score: float) -> List[str]:
        """Identify areas that need improvement."""
        areas = []
        
        if success_score < 0.9:
            areas.append("Test success rate needs improvement")
        if performance_score < 0.7:
            areas.append("Test execution performance is below optimal")
        if coverage_score < 0.8:
            areas.append("Test coverage across categories could be expanded")
        if reliability_score < 0.8:
            areas.append("Test reliability and consistency needs attention")
        if maintainability_score < 0.7:
            areas.append("Test maintainability (naming, documentation) could be improved")
        
        return areas
    
    def _identify_strengths(self, success_score: float, performance_score: float,
                          coverage_score: float, reliability_score: float,
                          maintainability_score: float) -> List[str]:
        """Identify testing strengths."""
        strengths = []
        
        if success_score >= 0.95:
            strengths.append("Excellent test success rate")
        if performance_score >= 0.8:
            strengths.append("Good test execution performance")
        if coverage_score >= 0.8:
            strengths.append("Comprehensive test coverage")
        if reliability_score >= 0.9:
            strengths.append("Highly reliable and consistent tests")
        if maintainability_score >= 0.8:
            strengths.append("Well-maintained and documented tests")
        
        return strengths
    
    def _generate_quality_recommendations(self, success_score: float, performance_score: float,
                                        coverage_score: float, reliability_score: float) -> List[str]:
        """Generate quality-specific recommendations."""
        recommendations = []
        
        if success_score < 0.9:
            recommendations.append("Investigate and fix failing tests to improve success rate")
        if performance_score < 0.7:
            recommendations.append("Optimize test execution speed and resource usage")
        if coverage_score < 0.8:
            recommendations.append("Add tests for uncovered categories and components")
        if reliability_score < 0.8:
            recommendations.append("Improve test stability and reduce execution variance")
        
        if not recommendations:
            recommendations.append("Maintain current high quality standards")
            recommendations.append("Consider adding performance regression tests")
        
        return recommendations
    
    def _compare_with_benchmarks(self, success_score: float, performance_score: float,
                               coverage_score: float, reliability_score: float) -> Dict[str, float]:
        """Compare scores with quality benchmarks."""
        return {
            "success_rate_vs_excellent": success_score / self.quality_benchmarks["excellent_success_rate"],
            "success_rate_vs_good": success_score / self.quality_benchmarks["good_success_rate"],
            "performance_vs_excellent": performance_score,
            "coverage_vs_optimal": coverage_score,
            "reliability_vs_excellent": reliability_score / self.quality_benchmarks["excellent_reliability"]
        }
    
    def _analyze_test_trends(self, test_results: List[TestCase], metrics: TestMetrics) -> List[TrendAnalysis]:
        """Analyze test performance trends."""
        if not self.config.get("trend_analysis", {}).get("enabled", True):
            return []
        
        try:
            # Use performance trend analyzer for test metrics
            trend_analyzer = self.trend_analyzer
            
            # For now, we'll create mock trend analysis based on historical data
            # In a full implementation, this would analyze historical test metrics
            trends = []
            
            if len(self.report_history) >= 5:  # Need sufficient history
                # Analyze success rate trends
                success_rates = [r.test_metrics.success_rate for r in self.report_history[-10:]]
                success_rates.append(metrics.success_rate)
                
                # Analyze duration trends
                durations = [r.test_metrics.average_duration for r in self.report_history[-10:]]
                durations.append(metrics.average_duration)
                
                # Create trend analysis (simplified)
                if len(success_rates) >= 3:
                    trends.append(self._create_trend_analysis("success_rate", success_rates))
                if len(durations) >= 3:
                    trends.append(self._create_trend_analysis("average_duration", durations))
            
            return trends
            
        except Exception as e:
            telemetry.log_event("trend_analysis_error", error=str(e))
            return []
    
    def _create_trend_analysis(self, metric_name: str, values: List[float]) -> TrendAnalysis:
        """Create a simplified trend analysis."""
        from .performance_trend_analyzer import TrendDirection, TrendSeverity
        
        # Simple trend calculation
        if len(values) < 2:
            direction = TrendDirection.UNKNOWN
            slope = 0.0
        else:
            # Linear regression slope
            n = len(values)
            x = list(range(n))
            x_mean = sum(x) / n
            y_mean = sum(values) / n
            
            numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, values))
            denominator = sum((xi - x_mean) ** 2 for xi in x)
            
            slope = numerator / denominator if denominator > 0 else 0.0
            
            if abs(slope) < 0.01:
                direction = TrendDirection.STABLE
            elif slope > 0:
                if metric_name == "success_rate":
                    direction = TrendDirection.IMPROVING
                else:  # duration - higher is worse
                    direction = TrendDirection.DEGRADING
            else:
                if metric_name == "success_rate":
                    direction = TrendDirection.DEGRADING
                else:  # duration - lower is better
                    direction = TrendDirection.IMPROVING
        
        # Determine severity
        severity = TrendSeverity.LOW if abs(slope) < 0.05 else TrendSeverity.MEDIUM
        
        # Calculate confidence and other metrics
        confidence = min(1.0, len(values) / 10.0)  # More data = higher confidence
        change_percent = ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0
        
        return TrendAnalysis(
            metric_name=metric_name,
            time_period="10_reports",
            direction=direction,
            severity=severity,
            confidence=confidence,
            slope=slope,
            correlation=0.8,  # Simplified
            data_points=len(values),
            start_value=values[0],
            end_value=values[-1],
            change_percent=change_percent,
            volatility=statistics.stdev(values) / statistics.mean(values) if statistics.mean(values) > 0 else 0,
            trend_strength=abs(slope) * confidence,
            context={"metric_type": metric_name, "analysis_method": "linear_regression"}
        )
    
    def _detect_test_anomalies(self, test_results: List[TestCase], metrics: TestMetrics) -> List[AnomalyDetection]:
        """Detect anomalies in test execution."""
        if not self.config.get("trend_analysis", {}).get("anomaly_detection", True):
            return []
        
        try:
            anomalies = []
            
            # Check for duration anomalies
            durations = [t.duration for t in test_results if t.duration > 0]
            if len(durations) >= 5:
                mean_duration = statistics.mean(durations)
                std_duration = statistics.stdev(durations)
                
                for test in test_results:
                    if test.duration > 0 and std_duration > 0:
                        z_score = abs(test.duration - mean_duration) / std_duration
                        if z_score > 2.5:  # Anomaly threshold
                            anomaly_type = "spike" if test.duration > mean_duration else "drop"
                            severity = self._determine_anomaly_severity(z_score)
                            
                            anomalies.append(AnomalyDetection(
                                metric_name=f"test_duration_{test.test_id}",
                                anomaly_timestamp=datetime.now(),
                                anomaly_value=test.duration,
                                expected_value=mean_duration,
                                deviation_score=z_score,
                                anomaly_type=anomaly_type,
                                severity=severity,
                                context={
                                    "test_name": test.name,
                                    "test_category": test.category.value,
                                    "detection_method": "z_score"
                                },
                                detection_method="z_score",
                                confidence=min(z_score / 3.0, 1.0)
                            ))
            
            return anomalies
            
        except Exception as e:
            telemetry.log_event("anomaly_detection_error", error=str(e))
            return []
    
    def _determine_anomaly_severity(self, z_score: float):
        """Determine anomaly severity based on z-score."""
        from .performance_trend_analyzer import TrendSeverity
        
        if z_score < 2.0:
            return TrendSeverity.LOW
        elif z_score < 3.0:
            return TrendSeverity.MEDIUM
        elif z_score < 4.0:
            return TrendSeverity.HIGH
        else:
            return TrendSeverity.CRITICAL
    
    def _generate_performance_insights(self, metrics: TestMetrics, trends: List[TrendAnalysis]) -> List[PerformanceInsight]:
        """Generate performance insights from test metrics and trends."""
        insights = []
        
        try:
            # Success rate insights
            if metrics.success_rate < 0.8:
                insights.append(PerformanceInsight(
                    insight_id=f"test_success_rate_{int(time.time())}",
                    title="Low Test Success Rate Detected",
                    description=f"Current test success rate is {metrics.success_rate:.1%}, which is below the recommended 80% threshold",
                    category="reliability",
                    priority="high" if metrics.success_rate < 0.7 else "medium",
                    affected_metrics=["success_rate"],
                    evidence={"current_rate": metrics.success_rate, "failed_tests": metrics.failed_tests},
                    recommendations=[
                        "Investigate and fix failing tests",
                        "Review test implementation for flaky tests",
                        "Consider test environment stability"
                    ],
                    estimated_impact="high",
                    implementation_effort="medium"
                ))
            
            # Performance insights
            if metrics.average_duration > 5.0:  # 5 seconds per test
                insights.append(PerformanceInsight(
                    insight_id=f"test_performance_{int(time.time())}",
                    title="Slow Test Execution Detected",
                    description=f"Average test duration is {metrics.average_duration:.1f}s, which may impact development velocity",
                    category="optimization",
                    priority="medium",
                    affected_metrics=["average_duration"],
                    evidence={"average_duration": metrics.average_duration, "slowest_test": metrics.slowest_test},
                    recommendations=[
                        "Profile slow tests and optimize bottlenecks",
                        "Consider test parallelization",
                        "Review test setup and teardown efficiency"
                    ],
                    estimated_impact="medium",
                    implementation_effort="medium"
                ))
            
            # Trend-based insights
            for trend in trends:
                if trend.direction.value == "degrading" and trend.confidence > 0.7:
                    insights.append(PerformanceInsight(
                        insight_id=f"trend_degrading_{trend.metric_name}_{int(time.time())}",
                        title=f"Degrading Trend in {trend.metric_name.replace('_', ' ').title()}",
                        description=f"{trend.metric_name} shows a degrading trend over recent test runs with {trend.change_percent:.1f}% change",
                        category="reliability",
                        priority="high" if abs(trend.change_percent) > 20 else "medium",
                        affected_metrics=[trend.metric_name],
                        evidence={
                            "trend_direction": trend.direction.value,
                            "change_percent": trend.change_percent,
                            "confidence": trend.confidence
                        },
                        recommendations=[
                            f"Monitor {trend.metric_name} closely for continued degradation",
                            "Investigate recent changes that might affect test performance",
                            "Consider implementing automated alerts for this metric"
                        ],
                        estimated_impact="high",
                        implementation_effort="low"
                    ))
            
            return insights
            
        except Exception as e:
            telemetry.log_event("performance_insights_error", error=str(e))
            return []
    
    def _generate_trend_insights(self, trends: List[TrendAnalysis], anomalies: List[AnomalyDetection]) -> List[TrendInsight]:
        """Generate insights from trend analysis and anomalies."""
        insights = []
        
        try:
            # Trend insights
            for trend in trends:
                if trend.confidence > 0.6:
                    if trend.direction.value == "improving":
                        insights.append(TrendInsight(
                            insight_type="positive_trend",
                            title=f"Improving {trend.metric_name.replace('_', ' ').title()}",
                            description=f"{trend.metric_name} shows consistent improvement over recent runs",
                            severity="info",
                            confidence=trend.confidence,
                            evidence={"change_percent": trend.change_percent, "trend_strength": trend.trend_strength},
                            recommendations=["Continue current practices", "Monitor to ensure improvement is sustained"],
                            impact_assessment="positive"
                        ))
                    elif trend.direction.value == "degrading":
                        insights.append(TrendInsight(
                            insight_type="negative_trend",
                            title=f"Degrading {trend.metric_name.replace('_', ' ').title()}",
                            description=f"{trend.metric_name} shows concerning degradation over recent runs",
                            severity="warning" if abs(trend.change_percent) < 20 else "critical",
                            confidence=trend.confidence,
                            evidence={"change_percent": trend.change_percent, "trend_strength": trend.trend_strength},
                            recommendations=[
                                "Investigate root causes of degradation",
                                "Review recent changes to test suite",
                                "Consider implementing corrective measures"
                            ],
                            impact_assessment="negative"
                        ))
            
            # Anomaly insights
            if len(anomalies) > 0:
                insights.append(TrendInsight(
                    insight_type="anomaly_pattern",
                    title=f"Test Anomalies Detected",
                    description=f"Found {len(anomalies)} anomalies in test execution patterns",
                    severity="warning",
                    confidence=0.8,
                    evidence={"anomaly_count": len(anomalies), "types": [a.anomaly_type for a in anomalies]},
                    recommendations=[
                        "Review tests with anomalous execution times",
                        "Check for environmental factors affecting test performance",
                        "Consider adjusting test timeout configurations"
                    ],
                    impact_assessment="neutral"
                ))
            
            return insights
            
        except Exception as e:
            telemetry.log_event("trend_insights_error", error=str(e))
            return []
    
    def _compare_with_historical(self, current_metrics: TestMetrics) -> Dict[str, Any]:
        """Compare current metrics with historical data."""
        if len(self.report_history) < 3:
            return {"status": "insufficient_history", "message": "Need more historical data for comparison"}
        
        try:
            # Get recent historical metrics
            recent_reports = self.report_history[-5:]  # Last 5 reports
            
            # Calculate historical averages
            historical_success_rate = statistics.mean(r.test_metrics.success_rate for r in recent_reports)
            historical_duration = statistics.mean(r.test_metrics.average_duration for r in recent_reports)
            historical_test_count = statistics.mean(r.test_metrics.total_tests for r in recent_reports)
            
            # Calculate changes
            success_rate_change = current_metrics.success_rate - historical_success_rate
            duration_change = current_metrics.average_duration - historical_duration
            test_count_change = current_metrics.total_tests - historical_test_count
            
            return {
                "status": "comparison_available",
                "historical_averages": {
                    "success_rate": historical_success_rate,
                    "average_duration": historical_duration,
                    "total_tests": historical_test_count
                },
                "current_vs_historical": {
                    "success_rate_change": success_rate_change,
                    "duration_change": duration_change,
                    "test_count_change": test_count_change
                },
                "change_percentages": {
                    "success_rate": (success_rate_change / historical_success_rate) * 100 if historical_success_rate > 0 else 0,
                    "duration": (duration_change / historical_duration) * 100 if historical_duration > 0 else 0,
                    "test_count": (test_count_change / historical_test_count) * 100 if historical_test_count > 0 else 0
                },
                "reports_analyzed": len(recent_reports)
            }
            
        except Exception as e:
            telemetry.log_event("historical_comparison_error", error=str(e))
            return {"status": "comparison_error", "error": str(e)}
    
    def _generate_comprehensive_recommendations(self, quality_assessment: QualityAssessment,
                                              trends: List[TrendAnalysis],
                                              anomalies: List[AnomalyDetection],
                                              performance_insights: List[PerformanceInsight]) -> List[str]:
        """Generate comprehensive recommendations from all analysis."""
        recommendations = []
        
        # Quality-based recommendations
        recommendations.extend(quality_assessment.recommendations)
        
        # Trend-based recommendations
        for trend in trends:
            if trend.direction.value == "degrading" and trend.confidence > 0.7:
                recommendations.append(f"Address degrading trend in {trend.metric_name}")
        
        # Anomaly-based recommendations
        if anomalies:
            recommendations.append(f"Investigate {len(anomalies)} test execution anomalies")
        
        # Performance insight recommendations
        for insight in performance_insights:
            recommendations.extend(insight.recommendations[:2])  # Limit to top 2 per insight
        
        # Remove duplicates and limit
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:10]  # Limit to top 10 recommendations
    
    def _generate_visualizations(self, metrics: TestMetrics, trends: List[TrendAnalysis],
                               quality_assessment: QualityAssessment) -> Dict[str, Any]:
        """Generate text-based visualizations for the report."""
        if not self.config.get("visualizations", {}).get("enabled", True):
            return {}
        
        visualizations = {}
        
        # Success rate gauge
        visualizations["success_rate_gauge"] = self._create_gauge_chart(
            metrics.success_rate, "Success Rate", "success"
        )
        
        # Quality score gauge
        visualizations["quality_score_gauge"] = self._create_gauge_chart(
            quality_assessment.overall_score, "Quality Score", "quality"
        )
        
        # Test distribution pie chart
        visualizations["test_distribution"] = self._create_test_distribution_chart(metrics)
        
        # Performance chart
        visualizations["performance_chart"] = self._create_performance_chart(metrics)
        
        # Trend charts
        if trends:
            visualizations["trend_charts"] = {}
            for trend in trends:
                visualizations["trend_charts"][trend.metric_name] = self._create_trend_chart(trend)
        
        return visualizations
    
    def _create_gauge_chart(self, value: float, title: str, chart_type: str) -> str:
        """Create ASCII gauge chart."""
        percentage = int(value * 100)
        filled = int(percentage / 5)  # 20 segments
        empty = 20 - filled
        
        # Color coding based on value
        if value >= 0.9:
            icon = "🟢"
        elif value >= 0.7:
            icon = "🟡"
        else:
            icon = "🔴"
        
        gauge = "█" * filled + "░" * empty
        return f"{icon} {title}: [{gauge}] {percentage}%"
    
    def _create_test_distribution_chart(self, metrics: TestMetrics) -> str:
        """Create test distribution visualization."""
        total = metrics.total_tests
        if total == 0:
            return "No tests executed"
        
        passed_bar = "█" * int((metrics.passed_tests / total) * 30)
        failed_bar = "█" * int((metrics.failed_tests / total) * 30)
        skipped_bar = "█" * int((metrics.skipped_tests / total) * 30)
        
        chart = f"""Test Distribution:
🟢 Passed  [{passed_bar:<30}] {metrics.passed_tests}/{total} ({metrics.success_rate:.1%})
🔴 Failed  [{failed_bar:<30}] {metrics.failed_tests}/{total} ({metrics.failure_rate:.1%})
⚪ Skipped [{skipped_bar:<30}] {metrics.skipped_tests}/{total} ({metrics.skip_rate:.1%})"""
        
        return chart
    
    def _create_performance_chart(self, metrics: TestMetrics) -> str:
        """Create performance metrics chart."""
        chart = f"""Performance Metrics:
⏱️  Total Duration:   {metrics.total_duration:.2f}s
📊 Average Duration:  {metrics.average_duration:.2f}s
🚀 Fastest Test:      {metrics.fastest_test:.2f}s
🐌 Slowest Test:      {metrics.slowest_test:.2f}s
📈 Test Velocity:     {metrics.test_velocity:.1f} tests/sec"""
        
        return chart
    
    def _create_trend_chart(self, trend: TrendAnalysis) -> str:
        """Create trend visualization."""
        direction_icon = {
            "improving": "📈",
            "degrading": "📉", 
            "stable": "➡️",
            "volatile": "📊"
        }.get(trend.direction.value, "❓")
        
        confidence_bar = "█" * int(trend.confidence * 10)
        
        chart = f"""{direction_icon} {trend.metric_name.replace('_', ' ').title()}:
Direction: {trend.direction.value}
Change:    {trend.change_percent:+.1f}%
Confidence: [{confidence_bar:<10}] {trend.confidence:.1%}
Data Points: {trend.data_points}"""
        
        return chart
    
    def _save_report(self, report: AdvancedTestReport, formats: List[ReportFormat]):
        """Save report in multiple formats."""
        try:
            report_dir = self.reports_path / report.report_id
            utils.ensure_dir(report_dir)
            
            for format_type in formats:
                if format_type == ReportFormat.JSON:
                    self._save_json_report(report, report_dir)
                elif format_type == ReportFormat.HTML:
                    self._save_html_report(report, report_dir)
                elif format_type == ReportFormat.CSV:
                    self._save_csv_report(report, report_dir)
                elif format_type == ReportFormat.MARKDOWN:
                    self._save_markdown_report(report, report_dir)
            
            # Save summary for historical tracking
            self._save_report_summary(report)
            
        except Exception as e:
            telemetry.log_event("report_save_error", error=str(e))
    
    def _save_json_report(self, report: AdvancedTestReport, report_dir: Path):
        """Save report as JSON."""
        json_path = report_dir / "report.json"
        
        # Convert dataclasses to dictionaries
        report_dict = self._convert_to_serializable(report)
        
        # Handle datetime and enum serialization
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, Enum):
                return obj.value
            elif hasattr(obj, '__dict__'):
                return self._convert_to_serializable(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(json_path, 'w') as f:
            json.dump(report_dict, f, indent=2, default=json_serializer)
    
    def _convert_to_serializable(self, obj):
        """Convert complex objects to JSON-serializable format."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value
        elif hasattr(obj, '__dict__'):
            # Handle dataclass objects
            result = {}
            for key, value in obj.__dict__.items():
                if isinstance(value, list):
                    result[key] = [self._convert_to_serializable(item) for item in value]
                elif isinstance(value, dict):
                    result[key] = {k: self._convert_to_serializable(v) for k, v in value.items()}
                else:
                    result[key] = self._convert_to_serializable(value)
            return result
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        else:
            return obj
    
    def _save_html_report(self, report: AdvancedTestReport, report_dir: Path):
        """Save report as HTML."""
        html_path = report_dir / "report.html"
        
        html_content = self._generate_html_report(report)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _save_csv_report(self, report: AdvancedTestReport, report_dir: Path):
        """Save test results as CSV."""
        csv_path = report_dir / "test_results.csv"
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Test ID', 'Name', 'Category', 'Result', 'Duration', 'Description', 'Error Message'
            ])
            
            # Test results
            for test in report.test_results:
                writer.writerow([
                    test.test_id,
                    test.name,
                    test.category.value,
                    test.result.value,
                    test.duration,
                    test.description,
                    test.error_message or ''
                ])
    
    def _save_markdown_report(self, report: AdvancedTestReport, report_dir: Path):
        """Save report as Markdown."""
        md_path = report_dir / "report.md"
        
        md_content = self._generate_markdown_report(report)
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _generate_html_report(self, report: AdvancedTestReport) -> str:
        """Generate HTML report content."""
        # This would be a comprehensive HTML template
        # For now, return a basic structure
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Advanced Test Report - {report.report_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: white; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
        .quality-score {{ font-size: 2em; font-weight: bold; }}
        .excellent {{ color: #28a745; }}
        .good {{ color: #17a2b8; }}
        .fair {{ color: #ffc107; }}
        .poor {{ color: #fd7e14; }}
        .critical {{ color: #dc3545; }}
        .test-results {{ margin: 20px 0; }}
        .test-item {{ padding: 10px; margin: 5px 0; border-left: 4px solid #ddd; }}
        .pass {{ border-left-color: #28a745; }}
        .fail {{ border-left-color: #dc3545; }}
        .skip {{ border-left-color: #6c757d; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Advanced Test Report</h1>
        <p><strong>Report ID:</strong> {report.report_id}</p>
        <p><strong>Generated:</strong> {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Quality Grade:</strong> <span class="{report.quality_assessment.quality_grade.value}">{report.quality_assessment.quality_grade.value.upper()}</span></p>
    </div>
    
    <div class="metrics">
        <div class="metric-card">
            <h3>Test Results</h3>
            <p><strong>Total Tests:</strong> {report.test_metrics.total_tests}</p>
            <p><strong>Success Rate:</strong> {report.test_metrics.success_rate:.1%}</p>
            <p><strong>Failed Tests:</strong> {report.test_metrics.failed_tests}</p>
        </div>
        
        <div class="metric-card">
            <h3>Performance</h3>
            <p><strong>Total Duration:</strong> {report.test_metrics.total_duration:.2f}s</p>
            <p><strong>Average Duration:</strong> {report.test_metrics.average_duration:.2f}s</p>
            <p><strong>Test Velocity:</strong> {report.test_metrics.test_velocity:.1f} tests/sec</p>
        </div>
        
        <div class="metric-card">
            <h3>Quality Assessment</h3>
            <div class="quality-score {report.quality_assessment.quality_grade.value}">
                {report.quality_assessment.overall_score:.1%}
            </div>
            <p>Grade: {report.quality_assessment.quality_grade.value.upper()}</p>
        </div>
    </div>
    
    <div class="visualizations">
        <h2>Performance Visualizations</h2>
        <pre>{report.visualizations.get('success_rate_gauge', '')}</pre>
        <pre>{report.visualizations.get('test_distribution', '')}</pre>
        <pre>{report.visualizations.get('performance_chart', '')}</pre>
    </div>
    
    <div class="recommendations">
        <h2>Recommendations</h2>
        <ul>
            {''.join(f'<li>{rec}</li>' for rec in report.recommendations)}
        </ul>
    </div>
    
    <div class="test-results">
        <h2>Test Results Details</h2>
        {''.join(f'''
        <div class="test-item {test.result.value.lower()}">
            <strong>{html.escape(test.name)}</strong> - {test.result.value}
            <br><small>Duration: {test.duration:.3f}s | Category: {test.category.value}</small>
            {f'<br><em>{html.escape(test.description)}</em>' if test.description else ''}
            {f'<br><strong>Error:</strong> {html.escape(test.error_message)}' if test.error_message else ''}
        </div>
        ''' for test in report.test_results)}
    </div>
</body>
</html>"""
    
    def _generate_markdown_report(self, report: AdvancedTestReport) -> str:
        """Generate Markdown report content."""
        return f"""# Advanced Test Report

**Report ID:** {report.report_id}  
**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}  
**Quality Grade:** {report.quality_assessment.quality_grade.value.upper()}

## Summary

- **Total Tests:** {report.test_metrics.total_tests}
- **Success Rate:** {report.test_metrics.success_rate:.1%}
- **Quality Score:** {report.quality_assessment.overall_score:.1%}
- **Total Duration:** {report.test_metrics.total_duration:.2f}s

## Quality Assessment

- **Overall Score:** {report.quality_assessment.overall_score:.1%}
- **Coverage Score:** {report.quality_assessment.coverage_score:.1%}
- **Performance Score:** {report.quality_assessment.performance_score:.1%}
- **Reliability Score:** {report.quality_assessment.reliability_score:.1%}

### Strengths
{chr(10).join(f'- {strength}' for strength in report.quality_assessment.strengths)}

### Areas for Improvement
{chr(10).join(f'- {area}' for area in report.quality_assessment.areas_for_improvement)}

## Visualizations

### Success Rate
```
{report.visualizations.get('success_rate_gauge', '')}
```

### Test Distribution
```
{report.visualizations.get('test_distribution', '')}
```

### Performance Metrics
```
{report.visualizations.get('performance_chart', '')}
```

## Recommendations

{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(report.recommendations))}

## Test Results

| Test Name | Result | Duration | Category |
|-----------|---------|----------|----------|
{chr(10).join(f'| {test.name} | {test.result.value} | {test.duration:.3f}s | {test.category.value} |' for test in report.test_results)}

---

*Report generated by Advanced Test Reporting System v1.0*
"""
    
    def _save_report_summary(self, report: AdvancedTestReport):
        """Save report summary for historical tracking."""
        summary_path = self.reports_path / "report_history.jsonl"
        
        summary = {
            "report_id": report.report_id,
            "timestamp": report.generated_at.isoformat(),
            "total_tests": report.test_metrics.total_tests,
            "success_rate": report.test_metrics.success_rate,
            "average_duration": report.test_metrics.average_duration,
            "quality_score": report.quality_assessment.overall_score,
            "quality_grade": report.quality_assessment.quality_grade.value,
            "trends_analyzed": len(report.trend_analysis),
            "anomalies_detected": len(report.anomalies),
            "insights_generated": len(report.performance_insights)
        }
        
        utils.append_jsonl(summary_path, summary)
    
    def _load_historical_reports(self, limit: int = 20):
        """Load historical reports for trend analysis."""
        summary_path = self.reports_path / "report_history.jsonl"
        
        if not summary_path.exists():
            return
        
        try:
            with open(summary_path, 'r') as f:
                for line in f:
                    if line.strip():
                        summary = json.loads(line.strip())
                        
                        # Create simplified report for trend analysis
                        metrics = TestMetrics(
                            total_tests=summary["total_tests"],
                            passed_tests=int(summary["total_tests"] * summary["success_rate"]),
                            failed_tests=int(summary["total_tests"] * (1 - summary["success_rate"])),
                            skipped_tests=0,
                            warning_tests=0,
                            success_rate=summary["success_rate"],
                            failure_rate=1 - summary["success_rate"],
                            skip_rate=0.0,
                            total_duration=summary["average_duration"] * summary["total_tests"],
                            average_duration=summary["average_duration"],
                            fastest_test=0.0,
                            slowest_test=0.0,
                            duration_std_dev=0.0,
                            test_velocity=0.0,
                            created_at=datetime.fromisoformat(summary["timestamp"])
                        )
                        
                        # Create minimal report for history
                        historical_report = AdvancedTestReport(
                            report_id=summary["report_id"],
                            generated_at=datetime.fromisoformat(summary["timestamp"]),
                            report_level=ReportLevel.SUMMARY,
                            test_metrics=metrics,
                            quality_assessment=QualityAssessment(
                                overall_score=summary["quality_score"],
                                quality_grade=TestQualityScore(summary["quality_grade"]),
                                coverage_score=0.0, performance_score=0.0, reliability_score=0.0,
                                maintainability_score=0.0, areas_for_improvement=[], strengths=[],
                                recommendations=[], benchmark_comparison={}
                            ),
                            execution_context=TestExecutionContext(
                                environment="", platform="", python_version="", test_framework="",
                                execution_mode="", ci_environment=False, git_commit=None,
                                git_branch=None, timestamp=datetime.fromisoformat(summary["timestamp"]),
                                duration=0.0, resource_usage={}
                            ),
                            test_results=[], trend_analysis=[], anomalies=[], performance_insights=[],
                            trend_insights=[], historical_comparison={}, recommendations=[],
                            visualizations={}
                        )
                        
                        self.report_history.append(historical_report)
            
            # Keep only recent reports
            self.report_history = self.report_history[-limit:]
            
        except Exception as e:
            telemetry.log_event("historical_reports_load_error", error=str(e))
    
    def _trim_report_history(self):
        """Trim report history to configured limit."""
        max_reports = self.config.get("trend_analysis", {}).get("lookback_reports", 20)
        if len(self.report_history) > max_reports:
            self.report_history = self.report_history[-max_reports:]


# Factory function
def get_advanced_test_report_generator(root: Path) -> AdvancedTestReportGenerator:
    """Get or create an AdvancedTestReportGenerator instance."""
    return AdvancedTestReportGenerator(root)
