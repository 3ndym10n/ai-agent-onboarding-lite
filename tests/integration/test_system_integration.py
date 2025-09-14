"""
System Integration Tests for Enhanced Error Monitoring System.
Tests complete integration of all components: Universal Error Monitor,
Smart Debugger, Error Pattern Recognition, Context Enrichment, and Test Suite.
"""

import json
import tempfile
import time
import pytest
from pathlib import Path

from ai_onboard.core.universal_error_monitor import get_error_monitor
from ai_onboard.core.smart_debugger import get_smart_debugger
from ai_onboard.core.continuous_improvement_validator import (
    ContinuousImprovementValidator,
    ValidationCategory,
)


class TestSystemIntegration:
    """Comprehensive integration tests for the complete error monitoring system."""

    @pytest.fixture
    def integration_env(self):
        """Set up complete integration test environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Initialize all system components
            error_monitor = get_error_monitor(root)
            smart_debugger = get_smart_debugger(root)
            validator = ContinuousImprovementValidator(root)

            yield {
                "root": root,
                "error_monitor": error_monitor,
                "smart_debugger": smart_debugger,
                "validator": validator,
            }

    def test_t48_1_system_integration_setup(self, integration_env):
        """T48.1: System Integration Setup - Validate all components initialize correctly."""
        env = integration_env

        # Verify all components are properly initialized
        assert env["error_monitor"] is not None
        assert env["smart_debugger"] is not None
        assert env["validator"] is not None

        # Verify component directories exist
        assert env["root"].exists()
        assert (env["root"] / ".ai_onboard").exists()

        # Verify error monitor files
        assert env["error_monitor"].error_log_path.parent.exists()
        assert env["error_monitor"].capability_usage_path.parent.exists()

        # Verify debugger files
        assert env["smart_debugger"].debug_log_path.parent.exists()
        assert env["smart_debugger"].patterns_path.parent.exists()

        print("✅ T48.1 PASSED: All system components initialized successfully")

    def test_t48_2_cross_component_communication(self, integration_env):
        """T48.2: Cross-Component Communication Testing."""
        env = integration_env

        # Test error monitor communication with smart debugger
        test_error = ValueError("Integration test error")
        context = {
            "agent_type": "integration_test",
            "command": "test_communication",
            "session_id": "integration_session",
        }

        # Intercept error with monitor
        result = env["error_monitor"].intercept_error(test_error, context)

        # Verify error data was captured
        assert "error_data" in result
        assert result["error_data"]["type"] == "ValueError"

        # Test smart debugger analysis
        debug_result = env["smart_debugger"].analyze_error(result["error_data"])
        assert "solution" in debug_result
        assert "confidence" in debug_result

        # Verify enhanced analysis includes contextual insights
        assert "enhanced_analysis" in debug_result
        enhanced = debug_result["enhanced_analysis"]
        assert "code_analysis" in enhanced

        print("✅ T48.2 PASSED: Cross-component communication working correctly")

    def test_t48_3_end_to_end_error_flow(self, integration_env):
        """T48.3: End-to-End Error Flow Testing."""
        env = integration_env

        # Simulate complete error journey
        errors_to_test = [
            (
                "AttributeError",
                "test_attr_access",
                "AttributeError: 'NoneType' object has no attribute 'test'",
            ),
            (
                "ImportError",
                "test_import",
                "ImportError: No module named 'nonexistent_module'",
            ),
            (
                "ValueError",
                "test_validation",
                "ValueError: invalid literal for int() with base 10: 'abc'",
            ),
        ]

        for error_type, command, error_msg in errors_to_test:
            # Create appropriate error type
            if error_type == "AttributeError":
                test_error = AttributeError(error_msg)
            elif error_type == "ImportError":
                test_error = ImportError(error_msg)
            elif error_type == "ValueError":
                test_error = ValueError(error_msg)

            context = {
                "agent_type": "e2e_test",
                "command": command,
                "session_id": "e2e_session_001",
            }

            # Step 1: Error interception
            interception_result = env["error_monitor"].intercept_error(
                test_error, context
            )
            assert interception_result["handled"] is True

            # Step 2: Error analysis by smart debugger
            analysis_result = env["smart_debugger"].analyze_error(
                interception_result["error_data"]
            )
            assert "solution" in analysis_result

            # Step 3: Pattern recognition
            patterns = env["error_monitor"].analyze_error_patterns(days_back=1)
            assert "patterns" in patterns
            assert "insights" in patterns

            # Step 4: Validation system integration
            test_case = env["validator"]._run_test_with_timeout(
                f"integration_test_{command}",
                lambda: None,  # Simple test function
                ValidationCategory.INTEGRATION,
                timeout_seconds=10,
            )
            assert test_case is not None

        print("✅ T48.3 PASSED: End-to-end error flow working correctly")

    def test_t48_4_performance_under_load(self, integration_env):
        """T48.4: Performance Under Load Testing."""
        env = integration_env

        # Test with moderate load (100 errors)
        num_errors = 100
        start_time = time.time()

        for i in range(num_errors):
            try:
                raise ValueError(f"Load test error {i}")
            except Exception as e:
                env["error_monitor"].intercept_error(
                    e,
                    {
                        "agent_type": "load_test",
                        "command": f"cmd_{i % 10}",
                        "session_id": "load_test_session",
                    },
                )

        processing_time = time.time() - start_time
        errors_per_second = num_errors / processing_time

        # Performance requirements (adjusted for comprehensive analysis)
        assert (
            errors_per_second > 1.5
        )  # At least 1.5 errors/second (reasonable for comprehensive analysis)
        assert (
            processing_time < 120
        )  # Should complete within 2 minutes (accounting for analysis overhead)

        # Verify all errors were processed
        patterns = env["error_monitor"].analyze_error_patterns(days_back=1)
        assert patterns["total_errors_analyzed"] == num_errors

        print(
            (
                f"✅ T48.4 PASSED: Processed {num_errors} errors in "
                f"{processing_time:.2f}s ({errors_per_second:.1f} errors/sec)"
            )
        )

    def test_t48_5_configuration_management(self, integration_env):
        """T48.5: Configuration Management Testing."""
        env = integration_env

        # Test configuration persistence and loading
        config_data = {
            "test_setting": "integration_test_value",
            "error_threshold": 100,
            "debug_level": "INFO",
        }

        # Save configuration
        config_path = env["root"] / ".ai_onboard" / "integration_test_config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        # Verify configuration is accessible to components
        assert config_path.exists()

        # Test configuration usage in error monitor
        usage_report = env["error_monitor"].get_usage_report()
        assert "error_patterns" in usage_report

        # Test configuration in smart debugger
        debug_stats = env["smart_debugger"].get_enhanced_debugging_stats()
        assert "pattern_database_metrics" in debug_stats

        print("✅ T48.5 PASSED: Configuration management working correctly")

    def test_t48_6_data_persistence_integration(self, integration_env):
        """T48.6: Data Persistence Integration Testing."""
        env = integration_env

        # Test data flow between components
        initial_error_count = 0

        # Add errors to error monitor
        for i in range(5):
            try:
                raise RuntimeError(f"Persistence test error {i}")
            except Exception as e:
                env["error_monitor"].intercept_error(
                    e,
                    {
                        "command": f"persistence_cmd_{i}",
                        "agent_type": "persistence_test",
                    },
                )

        # Verify data persisted in error monitor
        patterns = env["error_monitor"].analyze_error_patterns(days_back=1)
        assert patterns["total_errors_analyzed"] >= 5

        # Test data persistence in smart debugger
        debug_result = env["smart_debugger"].analyze_error(
            {
                "type": "RuntimeError",
                "message": "Persistence test error",
                "context": {"command": "test"},
            }
        )
        assert debug_result is not None

        # Test learning data persistence
        env["smart_debugger"].update_confidence_model(
            {"type": "RuntimeError", "message": "Test error"}, True
        )  # Mark as successful

        print("✅ T48.6 PASSED: Data persistence integration working correctly")

    def test_t48_7_api_integration_testing(self, integration_env):
        """T48.7: API Integration Testing."""
        env = integration_env

        # Test internal API integrations between components
        # This tests the component interfaces and data exchange

        # Test error monitor API
        error_result = env["error_monitor"].intercept_error(
            ValueError("API test error"),
            {"command": "api_test", "agent_type": "api_test"},
        )
        assert error_result["handled"] is True

        # Test smart debugger API
        debug_result = env["smart_debugger"].analyze_error(error_result["error_data"])
        assert "solution" in debug_result
        assert "confidence" in debug_result

        # Test validator API
        test_case = env["validator"]._run_test_with_timeout(
            "api_integration_test",
            lambda: "test_result",
            ValidationCategory.INTEGRATION,
            timeout_seconds=5,
        )
        assert test_case.result.name == "PASS"

        # Test pattern analysis API
        patterns = env["error_monitor"].analyze_error_patterns(days_back=1)
        assert isinstance(patterns, dict)
        assert "patterns" in patterns

        print("✅ T48.7 PASSED: API integration working correctly")

    def test_t48_8_error_recovery_testing(self, integration_env):
        """T48.8: Error Recovery Testing."""
        env = integration_env

        # Test system behavior with various error types and recovery

        # First, establish baseline functionality
        try:
            raise ValueError("Baseline test error")
        except Exception as e:
            baseline_result = env["error_monitor"].intercept_error(
                e, {"command": "baseline_test"}
            )
            assert baseline_result["handled"] is True

        # Test that system continues to work with different error types
        error_types = [ValueError, AttributeError, TypeError, RuntimeError, OSError]
        for error_class in error_types:
            try:
                raise error_class(f"Recovery test for {error_class.__name__}")
            except Exception as e:
                result = env["error_monitor"].intercept_error(
                    e,
                    {
                        "command": f"recovery_test_{error_class.__name__}",
                        "agent_type": "recovery_test",
                    },
                )

                # System should handle all error types gracefully
                assert result["handled"] is True
                assert "error_data" in result
                assert result["error_data"]["type"] == error_class.__name__

        # Test pattern analysis still works after multiple errors
        patterns = env["error_monitor"].analyze_error_patterns(days_back=1)
        total_errors = patterns["total_errors_analyzed"]
        assert total_errors >= 6  # Baseline + 5 error types

        # Verify all error types were captured in patterns
        error_type_counts = patterns["patterns"]["error_types"]
        for error_class in error_types:
            assert error_class.__name__ in error_type_counts

        # Test that system maintains functionality after heavy usage
        usage_report = env["error_monitor"].get_usage_report()
        assert "total_capability_uses" in usage_report
        assert usage_report["total_capability_uses"] >= total_errors

        print("✅ T48.8 PASSED: Error recovery mechanisms working correctly")

    def test_t48_9_scalability_testing(self, integration_env):
        """T48.9: Scalability Testing."""
        env = integration_env

        # Test system scalability with increasing complexity

        # Start with simple errors
        simple_errors = 10
        for i in range(simple_errors):
            try:
                raise ValueError(f"Simple error {i}")
            except Exception as e:
                env["error_monitor"].intercept_error(
                    e, {"command": "simple_cmd", "agent_type": "scalability_test"}
                )

        # Add more complex errors with detailed context
        complex_errors = 5
        for i in range(complex_errors):
            try:
                raise RuntimeError(
                    f"Complex error {i} with detailed context and additional information"
                )
            except Exception as e:
                env["error_monitor"].intercept_error(
                    e,
                    {
                        "command": f"complex_cmd_{i}",
                        "agent_type": "scalability_test",
                        "metadata": {
                            "complexity": "high",
                            "data_size": 1000 + i * 100,
                            "nested_context": {"level1": {"level2": f"value_{i}"}},
                        },
                    },
                )

        # Verify system handles complexity scaling
        patterns = env["error_monitor"].analyze_error_patterns(days_back=1)
        total_errors = patterns["total_errors_analyzed"]

        assert total_errors == simple_errors + complex_errors

        # Verify pattern analysis scales
        error_types = patterns["patterns"]["error_types"]
        assert "ValueError" in error_types
        assert "RuntimeError" in error_types

        print(
            f"✅ T48.9 PASSED: System scales to handle {total_errors} errors of varying complexity"
        )

    def test_t48_10_production_readiness_validation(self, integration_env):
        """T48.10: Production Readiness Validation."""
        env = integration_env

        # Comprehensive production readiness checks

        # 1. System Health Check
        usage_report = env["error_monitor"].get_usage_report()
        assert "total_capability_uses" in usage_report
        assert "error_patterns" in usage_report

        debug_stats = env["smart_debugger"].get_enhanced_debugging_stats()
        assert "pattern_database_metrics" in debug_stats
        assert "confidence_model_metrics" in debug_stats

        # 2. Data Integrity Check
        patterns = env["error_monitor"].analyze_error_patterns(days_back=7)
        assert isinstance(patterns, dict)
        assert "patterns" in patterns
        assert "insights" in patterns

        # 3. Performance Validation
        start_time = time.time()
        for i in range(50):  # Production load simulation
            try:
                raise Exception(f"Production readiness test {i}")
            except Exception as e:
                env["error_monitor"].intercept_error(
                    e, {"command": "production_test", "agent_type": "readiness_test"}
                )
        end_time = time.time()

        processing_time = end_time - start_time
        assert (
            processing_time < 45
        )  # Should handle 50 errors in under 45 seconds (accounting for comprehensive analysis)

        # 4. Error Rate Validation
        final_patterns = env["error_monitor"].analyze_error_patterns(days_back=1)
        error_count = final_patterns["total_errors_analyzed"]
        assert error_count >= 50  # All errors should be captured

        # 5. Component Integration Validation
        # Test that all components can communicate
        test_error = OSError("Final integration test")
        result = env["error_monitor"].intercept_error(
            test_error, {"command": "final_test", "agent_type": "production_readiness"}
        )

        assert result["handled"] is True
        assert "enriched_context" in result["error_data"]

        # 6. Learning System Validation
        env["smart_debugger"].update_confidence_model(result["error_data"], True)
        updated_stats = env["smart_debugger"].get_enhanced_debugging_stats()
        assert "adaptation_stats" in updated_stats["confidence_model_metrics"]

        print("✅ T48.10 PASSED: System validated for production readiness")

    def test_complete_system_integration_workflow(self, integration_env):
        """Test complete system integration workflow from error to resolution."""
        env = integration_env

        # Simulate a realistic error scenario
        try:
            # Simulate a complex application error
            def problematic_function():
                data = None
                return data.some_attribute  # This will raise AttributeError

            result = problematic_function()

        except AttributeError as e:
            # Step 1: Error is intercepted by the monitor
            interception_result = env["error_monitor"].intercept_error(
                e,
                {
                    "agent_type": "application",
                    "command": "data_processing",
                    "session_id": "integration_workflow_test",
                    "file": "test_module.py",
                    "line": 42,
                    "function": "problematic_function",
                },
            )

            # Step 2: Smart debugger analyzes the error
            analysis_result = env["smart_debugger"].analyze_error(
                interception_result["error_data"]
            )

            # Step 3: Validator runs integration tests
            validation_result = env["validator"]._run_test_with_timeout(
                "integration_workflow_validation",
                lambda: True,  # Simple validation
                ValidationCategory.INTEGRATION,
            )

            # Step 4: Pattern analysis provides insights
            pattern_insights = env["error_monitor"].analyze_error_patterns(days_back=1)

            # Verify complete workflow
            assert interception_result["handled"] is True
            assert "enhanced_analysis" in analysis_result
            assert validation_result.result.name == "PASS"
            assert pattern_insights["total_errors_analyzed"] >= 1

            # Verify enriched context includes expected information
            enriched = interception_result["error_data"]["enriched_context"]
            assert "system_info" in enriched
            assert "environment" in enriched
            assert "stack_analysis" in enriched

            print("✅ COMPLETE SYSTEM INTEGRATION WORKFLOW TEST PASSED")


if __name__ == "__main__":
    # Run integration tests manually if needed
    print("🔧 T48 INTEGRATION TESTING SUITE")
    print("=" * 40)
    print("Run with: python -m pytest tests/integration/test_system_integration.py -v")
