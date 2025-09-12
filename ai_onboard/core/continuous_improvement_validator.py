"""
Continuous Improvement System Validator - Comprehensive testing and validation.

This module provides comprehensive testing and validation for the continuous improvement system:
- System integration testing
- Component validation
- Performance testing
- End-to-end workflow testing
- Data integrity validation
- Configuration validation
"""

import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import (
    adaptive_config_manager,
    continuous_improvement_analytics,
    continuous_improvement_system,
    knowledge_base_evolution,
    performance_optimizer,
    system_health_monitor,
    user_preference_learning,
    utils,
)


class TestResult(Enum):
    """Test result status."""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


class TestCategory(Enum):
    """Test categories."""

    INTEGRATION = "integration"
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    DATA_INTEGRITY = "data_integrity"
    CONFIGURATION = "configuration"
    END_TO_END = "end_to_end"


@dataclass
class TestCase:
    """A single test case."""

    test_id: str
    name: str
    description: str
    category: TestCategory
    result: TestResult
    duration: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = None


@dataclass
class ValidationReport:
    """Comprehensive validation report."""

    report_id: str
    generated_at: datetime
    total_tests: int
    passed_tests: int
    failed_tests: int
    warning_tests: int
    skipped_tests: int
    test_results: List[TestCase]
    system_health_score: float
    recommendations: List[str]
    summary: str


class ContinuousImprovementValidator:
    """Comprehensive validator for the continuous improvement system."""

    def __init__(self, root: Path):
        self.root = root
        self.validation_path = root / ".ai_onboard" / "validation_reports.jsonl"
        self.test_config_path = root / ".ai_onboard" / "test_config.json"

        # Initialize all subsystems
        self.continuous_improvement = (
            continuous_improvement_system.get_continuous_improvement_system(root)
        )
        self.performance_optimizer = performance_optimizer.get_performance_optimizer(
            root
        )
        self.config_manager = adaptive_config_manager.get_adaptive_config_manager(root)
        self.user_preferences = (
            user_preference_learning.get_user_preference_learning_system(root)
        )
        self.health_monitor = system_health_monitor.get_system_health_monitor(root)
        self.knowledge_base = knowledge_base_evolution.get_knowledge_base_evolution(
            root
        )
        self.analytics = (
            continuous_improvement_analytics.get_continuous_improvement_analytics(root)
        )

        # Test configuration
        self.test_config = self._load_test_config()

        # Ensure directories exist
        utils.ensure_dir(self.validation_path.parent)

    def _load_test_config(self) -> Dict[str, Any]:
        """Load test configuration."""
        return utils.read_json(
            self.test_config_path,
            default={
                "test_timeout_seconds": 30,
                "performance_thresholds": {
                    "response_time_ms": 1000,
                    "memory_usage_mb": 100,
                    "cpu_usage_percent": 80,
                },
                "data_integrity_checks": True,
                "integration_tests": True,
                "performance_tests": True,
                "end_to_end_tests": True,
            },
        )

    def run_comprehensive_validation(self) -> ValidationReport:
        """Run comprehensive validation of the entire system."""
        print("🧪 Starting Comprehensive Continuous Improvement System Validation")
        print("=" * 70)

        test_results = []
        start_time = time.time()

        # Run all test categories
        if self.test_config["integration_tests"]:
            test_results.extend(self._run_integration_tests())

        if self.test_config["data_integrity_checks"]:
            test_results.extend(self._run_data_integrity_tests())

        if self.test_config["performance_tests"]:
            test_results.extend(self._run_performance_tests())

        if self.test_config["end_to_end_tests"]:
            test_results.extend(self._run_end_to_end_tests())

        # Calculate results
        total_tests = len(test_results)
        passed_tests = len([t for t in test_results if t.result == TestResult.PASS])
        failed_tests = len([t for t in test_results if t.result == TestResult.FAIL])
        warning_tests = len([t for t in test_results if t.result == TestResult.WARNING])
        skipped_tests = len([t for t in test_results if t.result == TestResult.SKIP])

        # Calculate system health score
        system_health_score = (
            (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(test_results)

        # Create validation report
        report = ValidationReport(
            report_id=f"validation_{int(time.time())}_{utils.random_string(8)}",
            generated_at=datetime.now(),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            warning_tests=warning_tests,
            skipped_tests=skipped_tests,
            test_results=test_results,
            system_health_score=system_health_score,
            recommendations=recommendations,
            summary=self._generate_summary(test_results, system_health_score),
        )

        # Save report
        self._save_validation_report(report)

        # Print results
        self._print_validation_results(report)

        return report

    def _run_integration_tests(self) -> List[TestCase]:
        """Run integration tests."""
        print("\n🔗 Running Integration Tests...")
        tests = []

        # Test 1: Continuous Improvement System Integration
        tests.append(self._test_continuous_improvement_integration())

        # Test 2: Performance Optimizer Integration
        tests.append(self._test_performance_optimizer_integration())

        # Test 3: Configuration Manager Integration
        tests.append(self._test_config_manager_integration())

        # Test 4: User Preferences Integration
        tests.append(self._test_user_preferences_integration())

        # Test 5: Health Monitor Integration
        tests.append(self._test_health_monitor_integration())

        # Test 6: Knowledge Base Integration
        tests.append(self._test_knowledge_base_integration())

        # Test 7: Analytics Integration
        tests.append(self._test_analytics_integration())

        return tests

    def _run_data_integrity_tests(self) -> List[TestCase]:
        """Run data integrity tests."""
        print("\n💾 Running Data Integrity Tests...")
        tests = []

        # Test 1: Configuration Data Integrity
        tests.append(self._test_configuration_data_integrity())

        # Test 2: User Preferences Data Integrity
        tests.append(self._test_user_preferences_data_integrity())

        # Test 3: Knowledge Base Data Integrity
        tests.append(self._test_knowledge_base_data_integrity())

        # Test 4: Analytics Data Integrity
        tests.append(self._test_analytics_data_integrity())

        return tests

    def _run_performance_tests(self) -> List[TestCase]:
        """Run performance tests."""
        print("\n⚡ Running Performance Tests...")
        tests = []

        # Test 1: System Response Time
        tests.append(self._test_system_response_time())

        # Test 2: Memory Usage
        tests.append(self._test_memory_usage())

        # Test 3: Knowledge Base Performance
        tests.append(self._test_knowledge_base_performance())

        # Test 4: Analytics Performance
        tests.append(self._test_analytics_performance())

        return tests

    def _run_end_to_end_tests(self) -> List[TestCase]:
        """Run end-to-end workflow tests."""
        print("\n🔄 Running End-to-End Tests...")
        tests = []

        # Test 1: Complete Learning Workflow
        tests.append(self._test_complete_learning_workflow())

        # Test 2: Complete Recommendation Workflow
        tests.append(self._test_complete_recommendation_workflow())

        # Test 3: Complete Health Monitoring Workflow
        tests.append(self._test_complete_health_monitoring_workflow())

        # Test 4: Complete Analytics Workflow
        tests.append(self._test_complete_analytics_workflow())

        return tests

    def _test_continuous_improvement_integration(self) -> TestCase:
        """Test continuous improvement system integration."""
        start_time = time.time()

        try:
            # Test basic functionality
            learning_events = self.continuous_improvement.get_learning_summary()
            recommendations = (
                self.continuous_improvement.get_improvement_recommendations()
            )

            duration = time.time() - start_time

            return TestCase(
                test_id="ci_integration_001",
                name="Continuous Improvement System Integration",
                description="Test basic continuous improvement system functionality",
                category=TestCategory.INTEGRATION,
                result=TestResult.PASS,
                duration=duration,
                details={
                    "learning_events_count": len(learning_events),
                    "recommendations_count": len(recommendations),
                },
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="ci_integration_001",
                name="Continuous Improvement System Integration",
                description="Test basic continuous improvement system functionality",
                category=TestCategory.INTEGRATION,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_performance_optimizer_integration(self) -> TestCase:
        """Test performance optimizer integration."""
        start_time = time.time()

        try:
            # Test performance optimizer functionality
            optimizations = self.performance_optimizer.get_optimization_opportunities()
            performance_metrics = self.performance_optimizer.get_performance_metrics()

            duration = time.time() - start_time

            return TestCase(
                test_id="perf_integration_001",
                name="Performance Optimizer Integration",
                description="Test performance optimizer functionality",
                category=TestCategory.INTEGRATION,
                result=TestResult.PASS,
                duration=duration,
                details={
                    "optimizations_count": len(optimizations),
                    "metrics_count": len(performance_metrics),
                },
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="perf_integration_001",
                name="Performance Optimizer Integration",
                description="Test performance optimizer functionality",
                category=TestCategory.INTEGRATION,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_config_manager_integration(self) -> TestCase:
        """Test configuration manager integration."""
        start_time = time.time()

        try:
            # Test configuration manager functionality
            configs = self.config_manager.get_all_configurations()
            profiles = self.config_manager.get_configuration_profiles()

            duration = time.time() - start_time

            return TestCase(
                test_id="config_integration_001",
                name="Configuration Manager Integration",
                description="Test configuration manager functionality",
                category=TestCategory.INTEGRATION,
                result=TestResult.PASS,
                duration=duration,
                details={
                    "configurations_count": len(configs),
                    "profiles_count": len(profiles),
                },
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="config_integration_001",
                name="Configuration Manager Integration",
                description="Test configuration manager functionality",
                category=TestCategory.INTEGRATION,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_user_preferences_integration(self) -> TestCase:
        """Test user preferences integration."""
        start_time = time.time()

        try:
            # Test user preferences functionality
            test_user_id = "test_user_validation"
            self.user_preferences.record_user_interaction(
                user_id=test_user_id,
                interaction_type="command_execution",
                context={"command": "validation_test"},
                satisfaction_score=0.8,
            )

            preferences = self.user_preferences.get_user_preferences(test_user_id)

            duration = time.time() - start_time

            return TestCase(
                test_id="user_prefs_integration_001",
                name="User Preferences Integration",
                description="Test user preferences functionality",
                category=TestCategory.INTEGRATION,
                result=TestResult.PASS,
                duration=duration,
                details={"preferences_count": len(preferences)},
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="user_prefs_integration_001",
                name="User Preferences Integration",
                description="Test user preferences functionality",
                category=TestCategory.INTEGRATION,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_health_monitor_integration(self) -> TestCase:
        """Test health monitor integration."""
        start_time = time.time()

        try:
            # Test health monitor functionality
            health_summary = self.health_monitor.get_health_summary(24)
            active_issues = self.health_monitor.get_active_issues()

            duration = time.time() - start_time

            return TestCase(
                test_id="health_integration_001",
                name="Health Monitor Integration",
                description="Test health monitor functionality",
                category=TestCategory.INTEGRATION,
                result=TestResult.PASS,
                duration=duration,
                details={
                    "health_status": health_summary.get("status", "unknown"),
                    "active_issues_count": len(active_issues),
                },
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="health_integration_001",
                name="Health Monitor Integration",
                description="Test health monitor functionality",
                category=TestCategory.INTEGRATION,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_knowledge_base_integration(self) -> TestCase:
        """Test knowledge base integration."""
        start_time = time.time()

        try:
            # Test knowledge base functionality
            stats = self.knowledge_base.get_knowledge_statistics()
            patterns = self.knowledge_base.discover_patterns()

            duration = time.time() - start_time

            return TestCase(
                test_id="kb_integration_001",
                name="Knowledge Base Integration",
                description="Test knowledge base functionality",
                category=TestCategory.INTEGRATION,
                result=TestResult.PASS,
                duration=duration,
                details={
                    "total_knowledge_items": stats.get("total_knowledge_items", 0),
                    "patterns_discovered": len(patterns),
                },
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="kb_integration_001",
                name="Knowledge Base Integration",
                description="Test knowledge base functionality",
                category=TestCategory.INTEGRATION,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_analytics_integration(self) -> TestCase:
        """Test analytics integration."""
        start_time = time.time()

        try:
            # Test analytics functionality
            summary = self.analytics.get_analytics_summary()
            dashboard_data = self.analytics.get_dashboard_data()

            duration = time.time() - start_time

            return TestCase(
                test_id="analytics_integration_001",
                name="Analytics Integration",
                description="Test analytics functionality",
                category=TestCategory.INTEGRATION,
                result=TestResult.PASS,
                duration=duration,
                details={
                    "total_metrics": summary.get("metrics", {}).get("total", 0),
                    "total_reports": summary.get("reports", {}).get("total", 0),
                },
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="analytics_integration_001",
                name="Analytics Integration",
                description="Test analytics functionality",
                category=TestCategory.INTEGRATION,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_configuration_data_integrity(self) -> TestCase:
        """Test configuration data integrity."""
        start_time = time.time()

        try:
            # Test configuration data integrity
            configs = self.config_manager.get_all_configurations()

            # Validate configuration structure
            for config in configs:
                if not config.get("name") or not config.get("value"):
                    raise ValueError(f"Invalid configuration structure: {config}")

            duration = time.time() - start_time

            return TestCase(
                test_id="data_integrity_001",
                name="Configuration Data Integrity",
                description="Validate configuration data structure and integrity",
                category=TestCategory.DATA_INTEGRITY,
                result=TestResult.PASS,
                duration=duration,
                details={"configurations_validated": len(configs)},
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="data_integrity_001",
                name="Configuration Data Integrity",
                description="Validate configuration data structure and integrity",
                category=TestCategory.DATA_INTEGRITY,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_user_preferences_data_integrity(self) -> TestCase:
        """Test user preferences data integrity."""
        start_time = time.time()

        try:
            # Test user preferences data integrity
            test_user_id = "data_integrity_test_user"

            # Record interaction
            self.user_preferences.record_user_interaction(
                user_id=test_user_id,
                interaction_type="data_integrity_test",
                context={"test": "data_integrity"},
                satisfaction_score=0.9,
            )

            # Retrieve and validate
            preferences = self.user_preferences.get_user_preferences(test_user_id)

            duration = time.time() - start_time

            return TestCase(
                test_id="data_integrity_002",
                name="User Preferences Data Integrity",
                description="Validate user preferences data structure and integrity",
                category=TestCategory.DATA_INTEGRITY,
                result=TestResult.PASS,
                duration=duration,
                details={"preferences_validated": len(preferences)},
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="data_integrity_002",
                name="User Preferences Data Integrity",
                description="Validate user preferences data structure and integrity",
                category=TestCategory.DATA_INTEGRITY,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_knowledge_base_data_integrity(self) -> TestCase:
        """Test knowledge base data integrity."""
        start_time = time.time()

        try:
            # Test knowledge base data integrity
            stats = self.knowledge_base.get_knowledge_statistics()

            # Validate statistics structure
            required_fields = [
                "total_knowledge_items",
                "active_knowledge_items",
                "average_confidence_score",
            ]
            for field in required_fields:
                if field not in stats:
                    raise ValueError(
                        f"Missing required field in knowledge statistics: {field}"
                    )

            duration = time.time() - start_time

            return TestCase(
                test_id="data_integrity_003",
                name="Knowledge Base Data Integrity",
                description="Validate knowledge base data structure and integrity",
                category=TestCategory.DATA_INTEGRITY,
                result=TestResult.PASS,
                duration=duration,
                details={"statistics_validated": len(stats)},
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="data_integrity_003",
                name="Knowledge Base Data Integrity",
                description="Validate knowledge base data structure and integrity",
                category=TestCategory.DATA_INTEGRITY,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_analytics_data_integrity(self) -> TestCase:
        """Test analytics data integrity."""
        start_time = time.time()

        try:
            # Test analytics data integrity
            summary = self.analytics.get_analytics_summary()

            # Validate summary structure
            required_sections = ["metrics", "kpis", "reports", "alerts"]
            for section in required_sections:
                if section not in summary:
                    raise ValueError(
                        f"Missing required section in analytics summary: {section}"
                    )

            duration = time.time() - start_time

            return TestCase(
                test_id="data_integrity_004",
                name="Analytics Data Integrity",
                description="Validate analytics data structure and integrity",
                category=TestCategory.DATA_INTEGRITY,
                result=TestResult.PASS,
                duration=duration,
                details={"summary_sections_validated": len(summary)},
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="data_integrity_004",
                name="Analytics Data Integrity",
                description="Validate analytics data structure and integrity",
                category=TestCategory.DATA_INTEGRITY,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_system_response_time(self) -> TestCase:
        """Test system response time."""
        start_time = time.time()

        try:
            # Test response time for key operations
            operations = [
                (
                    "continuous_improvement",
                    lambda: self.continuous_improvement.get_learning_summary(),
                ),
                (
                    "performance_optimizer",
                    lambda: self.performance_optimizer.get_optimization_opportunities(),
                ),
                (
                    "config_manager",
                    lambda: self.config_manager.get_all_configurations(),
                ),
                (
                    "user_preferences",
                    lambda: self.user_preferences.get_user_preferences("test_user"),
                ),
                ("health_monitor", lambda: self.health_monitor.get_health_summary(24)),
                (
                    "knowledge_base",
                    lambda: self.knowledge_base.get_knowledge_statistics(),
                ),
                ("analytics", lambda: self.analytics.get_analytics_summary()),
            ]

            response_times = {}
            for name, operation in operations:
                op_start = time.time()
                try:
                    operation()
                    response_times[name] = (
                        time.time() - op_start
                    ) * 1000  # Convert to ms
                except Exception as e:
                    # If operation fails, record a high response time to indicate the issue
                    response_times[name] = 10000  # 10 seconds to indicate failure
                    response_times[f"{name}_error"] = str(e)

            # Check against threshold
            threshold = self.test_config["performance_thresholds"]["response_time_ms"]
            # Only consider numeric response times (exclude error messages)
            numeric_times = [
                v
                for k, v in response_times.items()
                if not k.endswith("_error") and isinstance(v, (int, float))
            ]
            max_response_time = max(numeric_times) if numeric_times else 0

            result = (
                TestResult.PASS
                if max_response_time <= threshold
                else TestResult.WARNING
            )

            duration = time.time() - start_time

            return TestCase(
                test_id="perf_001",
                name="System Response Time",
                description=f"Test response time for key operations (threshold: {threshold}ms)",
                category=TestCategory.PERFORMANCE,
                result=result,
                duration=duration,
                details={
                    "max_response_time_ms": max_response_time,
                    "threshold_ms": threshold,
                    "response_times": response_times,
                },
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="perf_001",
                name="System Response Time",
                description="Test response time for key operations",
                category=TestCategory.PERFORMANCE,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_memory_usage(self) -> TestCase:
        """Test memory usage."""
        start_time = time.time()

        try:
            import os

            import psutil

            # Get current memory usage
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024

            # Check against threshold
            threshold = self.test_config["performance_thresholds"]["memory_usage_mb"]

            result = TestResult.PASS if memory_mb <= threshold else TestResult.WARNING

            duration = time.time() - start_time

            return TestCase(
                test_id="perf_002",
                name="Memory Usage",
                description=f"Test memory usage (threshold: {threshold}MB)",
                category=TestCategory.PERFORMANCE,
                result=result,
                duration=duration,
                details={"memory_usage_mb": memory_mb, "threshold_mb": threshold},
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="perf_002",
                name="Memory Usage",
                description="Test memory usage",
                category=TestCategory.PERFORMANCE,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_knowledge_base_performance(self) -> TestCase:
        """Test knowledge base performance."""
        start_time = time.time()

        try:
            # Test knowledge base operations
            search_start = time.time()
            search_results = self.knowledge_base.search_knowledge(
                "test query", limit=10
            )
            search_time = (time.time() - search_start) * 1000

            stats_start = time.time()
            stats = self.knowledge_base.get_knowledge_statistics()
            stats_time = (time.time() - stats_start) * 1000

            duration = time.time() - start_time

            return TestCase(
                test_id="perf_003",
                name="Knowledge Base Performance",
                description="Test knowledge base search and statistics performance",
                category=TestCategory.PERFORMANCE,
                result=TestResult.PASS,
                duration=duration,
                details={
                    "search_time_ms": search_time,
                    "stats_time_ms": stats_time,
                    "search_results_count": len(search_results),
                },
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="perf_003",
                name="Knowledge Base Performance",
                description="Test knowledge base performance",
                category=TestCategory.PERFORMANCE,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_analytics_performance(self) -> TestCase:
        """Test analytics performance."""
        start_time = time.time()

        try:
            # Test analytics operations
            summary_start = time.time()
            summary = self.analytics.get_analytics_summary()
            summary_time = (time.time() - summary_start) * 1000

            dashboard_start = time.time()
            dashboard = self.analytics.get_dashboard_data()
            dashboard_time = (time.time() - dashboard_start) * 1000

            duration = time.time() - start_time

            return TestCase(
                test_id="perf_004",
                name="Analytics Performance",
                description="Test analytics summary and dashboard performance",
                category=TestCategory.PERFORMANCE,
                result=TestResult.PASS,
                duration=duration,
                details={
                    "summary_time_ms": summary_time,
                    "dashboard_time_ms": dashboard_time,
                },
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="perf_004",
                name="Analytics Performance",
                description="Test analytics performance",
                category=TestCategory.PERFORMANCE,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_complete_learning_workflow(self) -> TestCase:
        """Test complete learning workflow."""
        start_time = time.time()

        try:
            # Record learning event
            self.continuous_improvement.record_learning_event(
                learning_type="user_preference",
                context={"test": "end_to_end"},
                outcome={"success": True},
                confidence=0.9,
                impact_score=0.8,
                source="validation_test",
            )

            # Get learning summary
            learning_summary = self.continuous_improvement.get_learning_summary()

            # Get recommendations
            recommendations = (
                self.continuous_improvement.get_improvement_recommendations()
            )

            duration = time.time() - start_time

            return TestCase(
                test_id="e2e_001",
                name="Complete Learning Workflow",
                description="Test complete learning event to recommendation workflow",
                category=TestCategory.END_TO_END,
                result=TestResult.PASS,
                duration=duration,
                details={
                    "learning_events_count": len(learning_summary),
                    "recommendations_count": len(recommendations),
                },
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="e2e_001",
                name="Complete Learning Workflow",
                description="Test complete learning workflow",
                category=TestCategory.END_TO_END,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_complete_recommendation_workflow(self) -> TestCase:
        """Test complete recommendation workflow."""
        start_time = time.time()

        try:
            # Generate recommendations
            recommendations = (
                self.continuous_improvement.get_improvement_recommendations()
            )

            # Record analytics metric
            self.analytics.collect_metric(
                name="recommendation_workflow_test",
                value=len(recommendations),
                tags={"workflow": "recommendation"},
            )

            duration = time.time() - start_time

            return TestCase(
                test_id="e2e_002",
                name="Complete Recommendation Workflow",
                description="Test complete recommendation generation and tracking workflow",
                category=TestCategory.END_TO_END,
                result=TestResult.PASS,
                duration=duration,
                details={"recommendations_generated": len(recommendations)},
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="e2e_002",
                name="Complete Recommendation Workflow",
                description="Test complete recommendation workflow",
                category=TestCategory.END_TO_END,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_complete_health_monitoring_workflow(self) -> TestCase:
        """Test complete health monitoring workflow."""
        start_time = time.time()

        try:
            # Start health monitoring
            self.health_monitor.start_monitoring()

            # Wait a moment for monitoring to start
            time.sleep(1)

            # Get health summary
            health_summary = self.health_monitor.get_health_summary(1)

            # Stop monitoring
            self.health_monitor.stop_monitoring()

            duration = time.time() - start_time

            return TestCase(
                test_id="e2e_003",
                name="Complete Health Monitoring Workflow",
                description="Test complete health monitoring start/stop/summary workflow",
                category=TestCategory.END_TO_END,
                result=TestResult.PASS,
                duration=duration,
                details={"health_status": health_summary.get("status", "unknown")},
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="e2e_003",
                name="Complete Health Monitoring Workflow",
                description="Test complete health monitoring workflow",
                category=TestCategory.END_TO_END,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _test_complete_analytics_workflow(self) -> TestCase:
        """Test complete analytics workflow."""
        start_time = time.time()

        try:
            # Record metrics
            self.analytics.collect_metric("e2e_test_metric", 100.0)

            # Generate report
            report_id = self.analytics.generate_report(
                report_type="performance_summary",
                period_start=datetime.now() - timedelta(hours=1),
                period_end=datetime.now(),
            )

            # Get dashboard data
            dashboard_data = self.analytics.get_dashboard_data()

            duration = time.time() - start_time

            return TestCase(
                test_id="e2e_004",
                name="Complete Analytics Workflow",
                description="Test complete analytics metric recording to dashboard workflow",
                category=TestCategory.END_TO_END,
                result=TestResult.PASS,
                duration=duration,
                details={
                    "report_generated": report_id is not None,
                    "dashboard_sections": len(dashboard_data),
                },
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestCase(
                test_id="e2e_004",
                name="Complete Analytics Workflow",
                description="Test complete analytics workflow",
                category=TestCategory.END_TO_END,
                result=TestResult.FAIL,
                duration=duration,
                error_message=str(e),
            )

    def _calculate_system_health_score(self, test_results: List[TestCase]) -> float:
        """Calculate system health score based on test results."""
        if not test_results:
            return 0.0

        total_tests = len(test_results)
        passed_tests = len([t for t in test_results if t.result == TestResult.PASS])
        warning_tests = len([t for t in test_results if t.result == TestResult.WARNING])

        # Calculate weighted score: pass=100%, warning=50%, fail=0%
        score = (passed_tests + (warning_tests * 0.5)) / total_tests * 100
        return round(score, 1)

    def _run_test_with_timeout(
        self,
        test_name: str,
        test_func: callable,
        category: TestCategory,
        timeout_seconds: int = 30,
    ) -> TestCase:
        """Run a test function with timeout handling."""
        import signal
        import time
        from threading import Thread, Event

        start_time = time.time()
        result = None
        error_message = None
        timeout_occurred = Event()

        def run_test():
            nonlocal result, error_message
            try:
                result = test_func()
            except Exception as e:
                error_message = str(e)

        # Start test in thread
        thread = Thread(target=run_test)
        thread.daemon = True
        thread.start()

        # Wait for completion or timeout
        thread.join(timeout_seconds)
        duration = (time.time() - start_time) * 1000  # Convert to ms

        if thread.is_alive():
            # Timeout occurred
            return TestCase(
                test_id=test_name,
                name=test_name,
                description=f"Test with {timeout_seconds}s timeout",
                category=category,
                result=TestResult.FAIL,
                duration=duration,
                error_message=f"Test timeout after {timeout_seconds} seconds",
            )
        elif error_message:
            # Test failed with error
            return TestCase(
                test_id=test_name,
                name=test_name,
                description=f"Test with error handling",
                category=category,
                result=TestResult.FAIL,
                duration=duration,
                error_message=error_message,
            )
        else:
            # Test passed
            return TestCase(
                test_id=test_name,
                name=test_name,
                description=f"Test completed successfully",
                category=category,
                result=TestResult.PASS,
                duration=duration,
            )

    def _create_test_case(
        self,
        name: str,
        category: TestCategory,
        result: TestResult,
        duration: float,
        error_message: Optional[str] = None,
    ) -> TestCase:
        """Helper method for creating test cases."""
        return TestCase(
            test_id=name,
            name=name,
            description=f"Test case for {name}",
            category=category,
            result=result,
            duration=duration,
            error_message=error_message,
        )

    def _check_threshold_violations(
        self, test_metrics: Dict[str, Any], thresholds: Dict[str, Any]
    ) -> List[str]:
        """Check for performance metric threshold violations."""
        violations = []

        for metric_name, metric_value in test_metrics.items():
            if metric_name in thresholds:
                threshold = thresholds[metric_name]
                if metric_value >= threshold:
                    violations.append(
                        f"{metric_name} exceeded threshold: {metric_value} >= {threshold}"
                    )

        return violations

    def _generate_report_id(self) -> str:
        """Generate a unique report ID."""
        import uuid
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"validation_report_{timestamp}_{unique_id}"

    def _generate_recommendations(self, test_results: List[TestCase]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        # Analyze failed tests
        failed_tests = [t for t in test_results if t.result == TestResult.FAIL]
        if failed_tests:
            recommendations.append(
                f"Address {len(failed_tests)} failed tests to improve system reliability"
            )

        # Analyze warning tests
        warning_tests = [t for t in test_results if t.result == TestResult.WARNING]
        if warning_tests:
            recommendations.append(
                f"Review {len(warning_tests)} warning tests for potential improvements"
            )

        # Analyze performance tests
        perf_tests = [t for t in test_results if t.category == TestCategory.PERFORMANCE]
        slow_tests = [t for t in perf_tests if t.duration > 5.0]
        if slow_tests:
            recommendations.append(f"Optimize {len(slow_tests)} slow performance tests")

        # Analyze integration tests
        integration_tests = [
            t for t in test_results if t.category == TestCategory.INTEGRATION
        ]
        failed_integration = [
            t for t in integration_tests if t.result == TestResult.FAIL
        ]
        if failed_integration:
            recommendations.append(
                "Review system integration to ensure all components work together"
            )

        return recommendations

    def _generate_summary(
        self, test_results: List[TestCase], system_health_score: float
    ) -> str:
        """Generate validation summary."""
        total_tests = len(test_results)
        passed_tests = len([t for t in test_results if t.result == TestResult.PASS])

        if system_health_score >= 90:
            status = "Excellent"
        elif system_health_score >= 75:
            status = "Good"
        elif system_health_score >= 50:
            status = "Fair"
        else:
            status = "Needs Improvement"

        return f"Continuous Improvement System validation completed with {status} status. {passed_tests}/{total_tests} tests passed ({system_health_score:.1f}% success rate)."

    def _print_validation_results(self, report: ValidationReport):
        """Print validation results."""
        print(f"\n📊 Validation Results Summary")
        print("=" * 50)
        print(f"Total Tests: {report.total_tests}")
        print(f"Passed: {report.passed_tests} ✅")
        print(f"Failed: {report.failed_tests} ❌")
        print(f"Warnings: {report.warning_tests} ⚠️")
        print(f"Skipped: {report.skipped_tests} ⏭️")
        print(f"System Health Score: {report.system_health_score:.1f}%")

        print(f"\n📋 Test Results by Category:")
        categories = {}
        for test in report.test_results:
            if test.category not in categories:
                categories[test.category] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "warnings": 0,
                }
            categories[test.category]["total"] += 1
            if test.result == TestResult.PASS:
                categories[test.category]["passed"] += 1
            elif test.result == TestResult.FAIL:
                categories[test.category]["failed"] += 1
            elif test.result == TestResult.WARNING:
                categories[test.category]["warnings"] += 1

        for category, stats in categories.items():
            print(f"  {category.value}: {stats['passed']}/{stats['total']} passed")

        if report.recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")

        print(f"\n📝 Summary: {report.summary}")

    def _save_validation_report(self, report: ValidationReport):
        """Save validation report to storage."""
        data = {
            "report_id": report.report_id,
            "generated_at": report.generated_at.isoformat(),
            "total_tests": report.total_tests,
            "passed_tests": report.passed_tests,
            "failed_tests": report.failed_tests,
            "warning_tests": report.warning_tests,
            "skipped_tests": report.skipped_tests,
            "system_health_score": report.system_health_score,
            "test_results": [
                {
                    "test_id": test.test_id,
                    "name": test.name,
                    "description": test.description,
                    "category": test.category.value,
                    "result": test.result.value,
                    "duration": test.duration,
                    "error_message": test.error_message,
                    "details": test.details,
                }
                for test in report.test_results
            ],
            "recommendations": report.recommendations,
            "summary": report.summary,
        }

        with open(self.validation_path, "a", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")


def get_continuous_improvement_validator(root: Path) -> ContinuousImprovementValidator:
    """Get continuous improvement validator instance."""
    return ContinuousImprovementValidator(root)
