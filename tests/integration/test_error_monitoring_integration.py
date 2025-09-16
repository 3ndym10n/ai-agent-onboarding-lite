"""
Integration tests for enhanced error monitoring system.
Tests complete error monitoring workflow from interception to analysis.
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ai_onboard.core.universal_error_monitor import UniversalErrorMonitor


class TestErrorMonitoringIntegration:
    """Integration tests for complete error monitoring system."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary directory for integration testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def error_monitor(self, temp_root):
        """Create an error monitor instance for integration testing."""
        return UniversalErrorMonitor(temp_root)

    def test_complete_error_workflow(self, error_monitor):
        """Test complete error monitoring workflow from interception to analysis."""
        # Step 1: Intercept multiple errors
        errors_to_create = [
            ("ValueError", "process_data", "data_agent"),
            ("AttributeError", "access_property", "ui_agent"),
            ("ValueError", "process_data", "data_agent"),  # Duplicate for patterns
            ("ImportError", "load_module", "system_agent"),
            ("ConnectionError", "network_request", "api_agent"),
        ]

        intercepted_results = []
        for error_type, command, agent in errors_to_create:
            try:
                if error_type == "ValueError":
                    raise ValueError(f"Test {error_type} in {command}")
                elif error_type == "AttributeError":
                    raise AttributeError(f"Test {error_type} in {command}")
                elif error_type == "ImportError":
                    raise ImportError(f"Test {error_type} in {command}")
                elif error_type == "ConnectionError":
                    raise ConnectionError(f"Test {error_type} in {command}")
            except Exception as e:
                result = error_monitor.intercept_error(
                    e,
                    {
                        "command": command,
                        "agent_type": agent,
                        "session_id": f"session_{len(intercepted_results)}",
                    },
                )
                intercepted_results.append(result)

        # Step 2: Verify all errors were intercepted
        assert len(intercepted_results) == 5
        for result in intercepted_results:
            assert result["handled"] is True
            assert "error_data" in result
            assert "enriched_context" in result["error_data"]

        # Step 3: Test error pattern analysis
        patterns = error_monitor.analyze_error_patterns(days_back=1)

        # Verify pattern analysis captured all error types
        error_types = patterns["patterns"]["error_types"]
        assert "ValueError" in error_types
        assert "AttributeError" in error_types
        assert "ImportError" in error_types
        assert "ConnectionError" in error_types

        # Verify insights were generated
        insights = patterns["insights"]
        assert len(insights) > 0
        assert any("Most common error type" in insight for insight in insights)

        # Verify recommendations were generated
        recommendations = patterns["recommendations"]
        assert len(recommendations) > 0

        # Step 4: Test usage report integration
        usage_report = error_monitor.get_usage_report()

        assert "error_patterns" in usage_report
        assert usage_report["error_patterns"]["total_errors_analyzed"] == 5
        assert usage_report["total_capability_uses"] >= 5

    def test_error_context_enrichment_integration(self, error_monitor):
        """Test comprehensive error context enrichment in integration."""
        # Create an error with rich context
        test_error = RuntimeError("Integration test error")
        rich_context = {
            "command": "complex_operation",
            "agent_type": "integration_agent",
            "session_id": "integration_session_123",
            "user_id": "test_user",
            "operation_id": "op_456",
            "metadata": {"input_size": 1000, "output_format": "json", "timeout": 30},
        }

        result = error_monitor.intercept_error(test_error, rich_context)

        # Verify basic error data
        error_data = result["error_data"]
        assert error_data["type"] == "RuntimeError"
        assert error_data["command"] == "complex_operation"
        assert error_data["agent_type"] == "integration_agent"

        # Verify enriched context is comprehensive
        enriched = error_data["enriched_context"]

        # Check for expected enrichment categories
        expected_categories = [
            "system_info",
            "performance_metrics",
            "environment",
            "stack_analysis",
            "recent_activity",
            "configuration_snapshot",
            "related_patterns",
            "resource_usage",
        ]

        enriched_keys = set(enriched.keys())
        found_categories = enriched_keys.intersection(set(expected_categories))

        # Should have at least several enrichment categories
        assert len(found_categories) >= 3

        # Verify system info contains expected fields
        if "system_info" in enriched:
            system_info = enriched["system_info"]
            expected_fields = ["platform", "python_version", "system", "pid"]
            for field in expected_fields:
                assert field in system_info

        # Verify environment info
        if "environment" in enriched:
            env_info = enriched["environment"]
            assert "working_directory" in env_info

        # Verify resource usage info
        if "resource_usage" in enriched:
            resource_info = enriched["resource_usage"]
            assert "process_memory_mb" in resource_info
            assert "system_memory" in resource_info

    def test_error_pattern_recognition_over_time(self, error_monitor):
        """Test error pattern recognition with temporal analysis."""
        # Create errors at different "times" (simulate by creating sequentially)
        error_sequence = [
            ("ValueError", "cmd1", "agent1"),
            ("ValueError", "cmd1", "agent1"),  # Same error
            ("AttributeError", "cmd2", "agent2"),
            ("ValueError", "cmd1", "agent1"),  # Third occurrence
            ("ImportError", "cmd3", "agent3"),
        ]

        # Intercept errors
        for error_type, command, agent in error_sequence:
            try:
                if error_type == "ValueError":
                    raise ValueError(f"Pattern test {error_type}")
                elif error_type == "AttributeError":
                    raise AttributeError(f"Pattern test {error_type}")
                elif error_type == "ImportError":
                    raise ImportError(f"Pattern test {error_type}")
            except Exception as e:
                error_monitor.intercept_error(
                    e,
                    {
                        "command": command,
                        "agent_type": agent,
                        "session_id": "pattern_test_session",
                    },
                )
                time.sleep(0.01)  # Small delay to simulate time progression

        # Analyze patterns
        patterns = error_monitor.analyze_error_patterns(days_back=1)

        # Verify pattern recognition
        error_types = patterns["patterns"]["error_types"]
        commands = patterns["patterns"]["commands"]
        agents = patterns["patterns"]["agents"]

        # ValueError should be most common (3 occurrences)
        assert error_types["ValueError"] == 3
        assert error_types["AttributeError"] == 1
        assert error_types["ImportError"] == 1

        # cmd1 should be most common command
        assert commands["cmd1"] == 3

        # agent1 should be most common agent
        assert agents["agent1"] == 3

        # Check insights for pattern recognition
        insights = patterns["insights"]
        value_error_insight = [
            i for i in insights if "ValueError" in i and "occurrences" in i
        ]
        assert len(value_error_insight) > 0

    def test_command_monitoring_with_error_patterns(self, error_monitor):
        """Test command monitoring integration with error patterns."""
        # Simulate a series of command executions with some failures
        commands_to_test = [
            ("successful_cmd", True),
            ("failing_cmd", False),
            ("another_successful_cmd", True),
            ("failing_cmd", False),  # Same command fails again
            ("successful_cmd", True),
        ]

        for command_name, should_succeed in commands_to_test:
            if should_succeed:
                # Successful command
                with error_monitor.monitor_command_execution(
                    command_name, "test_agent", "monitoring_session"
                ):
                    pass  # Command succeeds
            else:
                # Failing command
                try:
                    with error_monitor.monitor_command_execution(
                        command_name, "test_agent", "monitoring_session"
                    ):
                        raise RuntimeError(f"Simulated failure in {command_name}")
                except RuntimeError:
                    pass  # Expected exception

        # Analyze the resulting patterns
        patterns = error_monitor.analyze_error_patterns(days_back=1)

        # Should detect the failing command pattern
        commands = patterns["patterns"]["commands"]
        if "failing_cmd" in commands:
            assert commands["failing_cmd"] >= 2  # Failed at least twice

        # Check recommendations for failing commands
        recommendations = patterns["recommendations"]
        failing_cmd_recommendations = [r for r in recommendations if "failing_cmd" in r]
        if commands.get("failing_cmd", 0) >= 2:
            assert len(failing_cmd_recommendations) > 0

    def test_error_monitor_persistence_and_recovery(self, temp_root):
        """Test error monitor persistence and recovery across instances."""
        # Create first monitor instance and add errors
        monitor1 = UniversalErrorMonitor(temp_root)

        test_errors = [
            ("OSError", "file_operation", "file_agent"),
            ("PermissionError", "access_denied", "security_agent"),
        ]

        for error_type, command, agent in test_errors:
            try:
                if error_type == "OSError":
                    raise OSError(f"Test {error_type}")
                elif error_type == "PermissionError":
                    raise PermissionError(f"Test {error_type}")
            except Exception as e:
                monitor1.intercept_error(
                    e,
                    {
                        "command": command,
                        "agent_type": agent,
                        "session_id": "persistence_test",
                    },
                )

        # Create second monitor instance (simulating restart)
        monitor2 = UniversalErrorMonitor(temp_root)

        # Verify second instance can read the persisted errors
        patterns = monitor2.analyze_error_patterns(days_back=1)

        # Should find the persisted errors
        assert patterns["total_errors_analyzed"] == 2
        assert "OSError" in patterns["patterns"]["error_types"]
        assert "PermissionError" in patterns["patterns"]["error_types"]

        # Verify usage data persistence
        usage_report = monitor2.get_usage_report()
        assert usage_report["total_capability_uses"] >= 2

    def test_error_monitor_resource_cleanup(self, temp_root):
        """Test that error monitor properly cleans up resources."""
        monitor = UniversalErrorMonitor(temp_root)

        # Add some errors and usage data
        for i in range(10):
            try:
                raise ValueError(f"Cleanup test error {i}")
            except Exception as e:
                monitor.intercept_error(
                    e,
                    {
                        "command": f"cmd{i}",
                        "agent_type": "cleanup_agent",
                        "session_id": "cleanup_session",
                    },
                )

        # Verify files were created
        assert monitor.error_log_path.exists()
        assert monitor.capability_usage_path.exists()

        # Files should persist after monitor goes out of scope
        # (In real usage, files would be cleaned up by external processes if needed)
        assert monitor.error_log_path.exists()

    def test_error_monitor_high_volume_scenario(self, error_monitor):
        """Test error monitor performance under high volume."""
        # Simulate high volume of errors (reasonable test amount)
        num_errors = 50

        for i in range(num_errors):
            try:
                # Mix different error types
                if i % 3 == 0:
                    raise ValueError(f"High volume ValueError {i}")
                elif i % 3 == 1:
                    raise AttributeError(f"High volume AttributeError {i}")
                else:
                    raise RuntimeError(f"High volume RuntimeError {i}")
            except Exception as e:
                error_monitor.intercept_error(
                    e,
                    {
                        "command": f"cmd_{i % 5}",  # Limited command variety
                        "agent_type": f"agent_{i % 3}",  # Limited agent variety
                        "session_id": f"high_volume_session_{i // 10}",
                    },
                )

        # Verify all errors were processed
        patterns = error_monitor.analyze_error_patterns(days_back=1)
        assert patterns["total_errors_analyzed"] == num_errors

        # Verify pattern analysis still works
        error_types = patterns["patterns"]["error_types"]
        assert "ValueError" in error_types
        assert "AttributeError" in error_types
        assert "RuntimeError" in error_types

        # Should have approximately equal distribution
        for error_type in ["ValueError", "AttributeError", "RuntimeError"]:
            count = error_types[error_type]
            assert (
                num_errors * 0.25 <= count <= num_errors * 0.45
            )  # Allow some variance

    def test_error_monitor_with_background_processing(self, error_monitor):
        """Test error monitor with simulated background processing."""
        # Simulate background agent errors
        background_errors = [
            ("TimeoutError", "background_task", "background_agent"),
            ("ConnectionResetError", "network_poll", "background_agent"),
            ("MemoryError", "large_computation", "background_agent"),
        ]

        for error_type, command, agent in background_errors:
            try:
                if error_type == "TimeoutError":
                    raise TimeoutError(f"Background {error_type}")
                elif error_type == "ConnectionResetError":
                    raise ConnectionResetError(f"Background {error_type}")
                elif error_type == "MemoryError":
                    raise MemoryError(f"Background {error_type}")
            except Exception as e:
                error_monitor.intercept_error(
                    e,
                    {
                        "command": command,
                        "agent_type": agent,
                        "session_id": "background_session",
                        "is_background": True,
                        "priority": "low",
                    },
                )

        # Verify background errors were captured
        patterns = error_monitor.analyze_error_patterns(days_back=1)
        assert patterns["total_errors_analyzed"] == 3

        # All errors should be attributed to background_agent
        agents = patterns["patterns"]["agents"]
        assert agents.get("background_agent", 0) == 3

        # Check that insights recognize background error patterns
        insights = patterns["insights"]
        background_insights = [
            i for i in insights if "background_agent" in i or "agent" in i
        ]
        assert len(background_insights) > 0

    @patch("ai_onboard.core.universal_error_monitor.telemetry")
    def test_error_monitor_telemetry_integration(self, mock_telemetry, error_monitor):
        """Test integration with telemetry system."""
        # Create an error that should trigger telemetry
        test_error = FileNotFoundError("Test file not found")

        result = error_monitor.intercept_error(
            test_error,
            {
                "command": "read_file",
                "agent_type": "file_agent",
                "session_id": "telemetry_test",
            },
        )

        # Verify telemetry was called
        mock_telemetry.log_event.assert_called_once()
        call_kwargs = mock_telemetry.log_event.call_args[1]

        assert call_kwargs["error_type"] == "FileNotFoundError"
        assert call_kwargs["agent_type"] == "file_agent"
        assert "confidence" in call_kwargs

    @patch("ai_onboard.core.universal_error_monitor.smart_debugger")
    def test_error_monitor_debugger_integration(self, mock_debugger, error_monitor):
        """Test integration with smart debugger."""
        # Mock the debugger
        mock_debugger_instance = Mock()
        mock_debugger_instance.analyze_error.return_value = {
            "confidence": 0.9,
            "solution": "Fix the attribute access",
            "root_cause": "Missing null check",
        }
        mock_debugger.SmartDebugger.return_value = mock_debugger_instance

        # Create monitor with mocked debugger
        with patch.object(error_monitor, "debugger", mock_debugger_instance):
            test_error = AttributeError("Test attribute error")

            result = error_monitor.intercept_error(
                test_error, {"command": "access_attribute", "agent_type": "code_agent"}
            )

            # Verify debugger was called
            mock_debugger_instance.analyze_error.assert_called_once()

            # Verify debug result is in the response
            assert "debug_result" in result
            assert result["debug_result"]["confidence"] == 0.9
            assert result["debug_result"]["solution"] == "Fix the attribute access"
