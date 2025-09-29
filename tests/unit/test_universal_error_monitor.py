"""
Unit tests for Universal Error Monitor functionality.
Tests error interception, pattern recognition, and context enrichment.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_onboard.core.orchestration.universal_error_monitor import (
    UniversalErrorMonitor,
    get_error_monitor,
    setup_global_error_handler,
)


class TestUniversalErrorMonitor:
    """Unit tests for Universal Error Monitor."""

    @pytest.fixture
    def temp_root(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def error_monitor(self, temp_root):
        """Create an error monitor instance for testing."""
        return UniversalErrorMonitor(temp_root)

    def test_error_monitor_initialization(self, error_monitor, temp_root):
        """Test that error monitor initializes correctly."""
        assert error_monitor.root == temp_root
        # Files are created lazily; verify paths are set
        assert error_monitor.error_log_path.suffix == ".jsonl"
        assert error_monitor.capability_usage_path.suffix == ".json"

    def test_basic_error_interception(self, error_monitor):
        """Test basic error interception functionality."""
        # Create a test error
        test_error = ValueError("Test error message")
        context = {
            "agent_type": "test_agent",
            "command": "test_command",
            "session_id": "test_session_123",
        }

        # Intercept the error
        result = error_monitor.intercept_error(test_error, context)

        # Verify the result structure
        assert "error_data" in result
        assert "debug_result" in result
        assert result["handled"] is True

        # Verify error data
        error_data = result["error_data"]
        assert error_data["type"] == "ValueError"
        assert error_data["message"].startswith("Test error message")
        assert error_data["agent_type"] == "test_agent"
        assert error_data["command"] == "test_command"
        assert error_data["session_id"] == "test_session_123"

    def test_error_logging(self, error_monitor):
        """Test that errors are properly logged to file."""
        # Clear any existing log
        if error_monitor.error_log_path.exists():
            error_monitor.error_log_path.unlink()

        # Create and log an error
        test_error = RuntimeError("Logging test error")
        error_monitor.intercept_error(test_error, {"command": "test"})

        # Verify error was logged
        assert error_monitor.error_log_path.exists()

        # Read and verify log content
        with open(error_monitor.error_log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 1

            logged_error = json.loads(lines[0])
            assert logged_error["type"] == "RuntimeError"
            assert "Logging test error" in logged_error["message"]
            assert logged_error["command"] == "test"

    def test_capability_usage_tracking(self, error_monitor):
        """Test capability usage tracking."""
        # Track some capability usage
        error_monitor.track_capability_usage("error_interception", {"test": True})
        error_monitor.track_capability_usage("command_execution", {"success": True})

        # Get usage report
        report = error_monitor.get_usage_report()

        # Verify usage was recorded
        assert report["total_capability_uses"] >= 2
        assert "error_interception" in report["capability_breakdown"]
        assert "command_execution" in report["capability_breakdown"]

    def test_command_monitoring_context_manager(self, error_monitor):
        """Test command monitoring context manager."""
        # Test successful command
        with error_monitor.monitor_command_execution(
            "test_cmd", "test_agent", "session_123"
        ) as monitor:
            assert monitor.command == "test_cmd"
            assert monitor.agent_type == "test_agent"
            assert monitor.session_id == "session_123"
            # Command executes successfully

        # Test failed command
        with pytest.raises(ValueError):
            with error_monitor.monitor_command_execution(
                "failing_cmd", "test_agent", "session_456"
            ):
                raise ValueError("Command failed")

        # Verify both were tracked
        report = error_monitor.get_usage_report()
        assert report["total_capability_uses"] >= 2

    def test_error_pattern_analysis_empty(self, error_monitor):
        """Test error pattern analysis with no errors."""
        patterns = error_monitor.analyze_error_patterns(days_back=1)

        assert "patterns" in patterns
        assert "insights" in patterns
        assert "recommendations" in patterns
        assert patterns.get("total_errors_analyzed", 0) == 0

    def test_error_pattern_analysis_with_data(self, error_monitor):
        """Test error pattern analysis with error data."""
        # Create some test errors
        errors = [
            ("ValueError", "cmd1", "agent1"),
            ("AttributeError", "cmd2", "agent2"),
            ("ValueError", "cmd1", "agent1"),
            ("ImportError", "cmd3", "agent3"),
        ]

        for error_type, command, agent in errors:
            try:
                if error_type == "ValueError":
                    raise ValueError(f"Test {error_type}")
                elif error_type == "AttributeError":
                    raise AttributeError(f"Test {error_type}")
                elif error_type == "ImportError":
                    raise ImportError(f"Test {error_type}")
            except Exception as e:
                error_monitor.intercept_error(
                    e,
                    {
                        "command": command,
                        "agent_type": agent,
                        "session_id": "test_session",
                    },
                )

        # Analyze patterns
        patterns = error_monitor.analyze_error_patterns(days_back=1)

        # Verify pattern analysis
        assert patterns["total_errors_analyzed"] == 4
        assert "ValueError" in patterns["patterns"]["error_types"]
        assert "AttributeError" in patterns["patterns"]["error_types"]
        assert "ImportError" in patterns["patterns"]["error_types"]

        # Check insights
        assert len(patterns["insights"]) > 0
        assert any(
            "Most common error type" in insight for insight in patterns["insights"]
        )

        # Check recommendations
        assert len(patterns["recommendations"]) > 0

    def test_error_context_enrichment(self, error_monitor):
        """Test error context enrichment functionality."""
        test_error = KeyError("missing_key")
        context = {
            "agent_type": "test_agent",
            "command": "test_command",
            "session_id": "test_session_123",
        }

        result = error_monitor.intercept_error(test_error, context)

        # Verify enriched context is present
        assert "enriched_context" in result["error_data"]
        enriched = result["error_data"]["enriched_context"]

        # Check that enrichment categories are present (allowing for graceful degradation)
        enrichment_keys = [
            "system_info",
            "performance_metrics",
            "environment",
            "stack_analysis",
            "recent_activity",
            "configuration_snapshot",
            "related_patterns",
            "resource_usage",
        ]

        # At least some enrichment should be present
        enriched_keys = set(enriched.keys())
        enrichment_keys_set = set(enrichment_keys)
        assert len(enriched_keys.intersection(enrichment_keys_set)) > 0

        # If enrichment failed, there should be an error indicator
        if "enrichment_failed" in enriched:
            assert enriched["enrichment_failed"] is True
            assert "enrichment_error" in enriched

    def test_error_context_enrichment_graceful_failure(self, error_monitor):
        """Test that context enrichment fails gracefully."""
        test_error = Exception("Test error")
        context = {"command": "test"}

        # Mock a failure in enrichment (simulate psutil not available)
        with patch.object(
            error_monitor,
            "_get_performance_metrics",
            side_effect=Exception("Mock failure"),
        ):
            result = error_monitor.intercept_error(test_error, context)

            # Should still succeed overall
            assert result["handled"] is True
            assert "enriched_context" in result["error_data"]

            # But enrichment should indicate failure
            enriched = result["error_data"]["enriched_context"]
            assert enriched["enrichment_failed"] is True
            assert "enrichment_error" in enriched

    def test_usage_report_includes_error_patterns(self, error_monitor):
        """Test that usage report includes error pattern analysis."""
        # Create some errors first
        try:
            raise ValueError("Test error for patterns")
        except Exception as e:
            error_monitor.intercept_error(e, {"command": "test"})

        # Get usage report
        report = error_monitor.get_usage_report()

        # Should include error patterns
        assert "error_patterns" in report
        assert "patterns" in report["error_patterns"]
        assert "insights" in report["error_patterns"]
        assert "recommendations" in report["error_patterns"]

    def test_recent_errors_functionality(self, error_monitor):
        """Test recent errors retrieval functionality."""
        # Initially should be empty
        recent = error_monitor._get_recent_errors(5)
        assert recent == []

        # Add some errors
        for i in range(3):
            try:
                raise ValueError(f"Error {i}")
            except Exception as e:
                error_monitor.intercept_error(e, {"command": f"cmd{i}"})

        # Should now have recent errors
        recent = error_monitor._get_recent_errors(5)
        assert len(recent) == 3

        # Test limit
        recent_limited = error_monitor._get_recent_errors(2)
        assert len(recent_limited) == 2

    def test_error_rate_calculation(self, error_monitor):
        """Test error rate calculation functionality."""
        # Initially should be 0
        rate = error_monitor._calculate_error_rate()
        assert rate == 0.0

        # Add some capability usage with errors
        usage_data = {
            "capabilities": {"test_capability": 10},
            "usage_history": [
                {"capability": "test_capability", "context": {"success": True}},
                {"capability": "test_capability", "context": {"success": False}},
                {"capability": "test_capability", "context": {"success": True}},
                {"capability": "test_capability", "context": {"success": False}},
                {"capability": "test_capability", "context": {"success": True}},
            ],
        }

        # Mock the usage data
        from ai_onboard.core.base import utils

        with patch.object(utils, "read_json", return_value=usage_data):
            rate = error_monitor._calculate_error_rate()
            # 2 errors out of 5 usages = 40% error rate
            assert rate == 0.4

    def test_global_error_handler_setup(self, temp_root):
        """Test global error handler setup."""
        with patch(
            "ai_onboard.core.orchestration.universal_error_monitor.get_error_monitor"
        ) as mock_get_monitor:
            mock_monitor = MagicMock()
            mock_get_monitor.return_value = mock_monitor

            previous_hook = sys.excepthook
            try:
                setup_global_error_handler(temp_root)
                mock_get_monitor.assert_called_once_with(temp_root)
                assert sys.excepthook is not previous_hook
            finally:
                sys.excepthook = previous_hook

    def test_factory_function(self, temp_root):
        """Test the factory function for creating error monitor."""
        monitor = get_error_monitor(temp_root)
        assert isinstance(monitor, UniversalErrorMonitor)
        assert monitor.root == temp_root

    def test_error_monitor_with_smart_debugger_integration(self, error_monitor):
        """Test integration with smart debugger."""
        test_error = TypeError("Test type error")
        context = {"command": "test", "agent_type": "test_agent"}

        # Mock the debugger
        with patch.object(error_monitor.debugger, "analyze_error") as mock_analyze:
            mock_analyze.return_value = {"confidence": 0.8, "solution": "Fix type"}

            result = error_monitor.intercept_error(test_error, context)

            # Verify debugger was called
            mock_analyze.assert_called_once()
            assert "debug_result" in result
            assert result["debug_result"]["confidence"] == 0.8

    def test_error_monitor_with_telemetry_integration(self, error_monitor):
        """Test integration with telemetry system."""
        test_error = ConnectionError("Network error")
        context = {"command": "network_cmd", "agent_type": "network_agent"}

        # Mock telemetry
        with patch(
            "ai_onboard.core.orchestration.universal_error_monitor.telemetry"
        ) as mock_telemetry:
            result = error_monitor.intercept_error(test_error, context)

            # Verify telemetry was called
            mock_telemetry.log_event.assert_called_once()
            call_args = mock_telemetry.log_event.call_args
            assert call_args[1]["error_type"] == "ConnectionError"
            assert call_args[1]["agent_type"] == "network_agent"
