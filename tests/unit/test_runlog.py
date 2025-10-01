"""
Tests for run logging system.

This module tests the run logging functionality that tracks
system events and operations for debugging and monitoring.
"""

import json
from pathlib import Path

from ai_onboard.core.base.runlog import _path, write_event


class TestRunlogPath:
    """Test runlog path management."""

    def test_path_generation(self, tmp_path):
        """Test runlog path generation."""
        result = _path(tmp_path)
        expected = tmp_path / ".ai_onboard" / "log.jsonl"

        assert result == expected
        assert isinstance(result, Path)


class TestWriteEvent:
    """Test event writing functionality."""

    def test_write_event_basic(self, tmp_path):
        """Test basic event writing."""
        # Write an event
        payload = {"action": "test", "status": "success", "duration": 1.5}
        write_event(tmp_path, "test_event", payload)

        # Verify file was written
        log_file = tmp_path / ".ai_onboard" / "log.jsonl"
        assert log_file.exists()

        # Read and verify content
        content = log_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 1

        # Parse JSON line
        event_data = json.loads(lines[0])

        assert event_data["kind"] == "test_event"
        assert "ts" in event_data  # timestamp as unix timestamp
        assert event_data["data"] == payload  # payload under "data" key

    def test_write_event_multiple(self, tmp_path):
        """Test writing multiple events."""
        # Write multiple events
        events = [
            ("event1", {"data": "first"}),
            ("event2", {"data": "second", "value": 42}),
            ("event3", {"data": "third", "status": "complete"}),
        ]

        for kind, payload in events:
            write_event(tmp_path, kind, payload)

        # Verify file content
        log_file = tmp_path / ".ai_onboard" / "log.jsonl"
        assert log_file.exists()
        content = log_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 3

        # Verify each event
        for i, (expected_kind, expected_payload) in enumerate(events):
            event_data = json.loads(lines[i])
            assert event_data["kind"] == expected_kind
            assert "ts" in event_data  # timestamp as unix timestamp
            assert event_data["data"] == expected_payload

    def test_write_event_empty_payload(self, tmp_path):
        """Test writing event with empty payload."""
        write_event(tmp_path, "empty_event", {})

        log_file = tmp_path / ".ai_onboard" / "log.jsonl"
        assert log_file.exists()
        content = log_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 1

        event_data = json.loads(lines[0])
        assert event_data["kind"] == "empty_event"
        assert event_data["data"] == {}

    def test_write_event_complex_payload(self, tmp_path):
        """Test writing event with complex nested payload."""
        complex_payload = {
            "operation": "file_backup",
            "details": {
                "source": "/path/to/source",
                "destination": "/path/to/dest",
                "files": ["file1.txt", "file2.txt", "file3.txt"],
            },
            "metrics": {"duration": 2.5, "bytes_copied": 1048576, "success": True},
            "metadata": {
                "user": "test_user",
                "session_id": "abc-123-def",
                "tags": ["backup", "automated", "daily"],
            },
        }

        write_event(tmp_path, "complex_operation", complex_payload)

        log_file = tmp_path / ".ai_onboard" / "log.jsonl"
        assert log_file.exists()
        content = log_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 1

        event_data = json.loads(lines[0])
        assert event_data["kind"] == "complex_operation"
        assert event_data["data"] == complex_payload


class TestIntegration:
    """Integration tests for runlog system."""

    def test_runlog_workflow(self, tmp_path):
        """Test complete runlog workflow."""
        # Write several events of different types
        events = [
            ("system_start", {"version": "1.0.0", "mode": "test"}),
            ("user_action", {"action": "create_file", "filename": "test.txt"}),
            (
                "operation_complete",
                {"operation": "backup", "status": "success", "duration": 1.2},
            ),
            ("system_shutdown", {"reason": "normal", "uptime": 3600}),
        ]

        for kind, payload in events:
            write_event(tmp_path, kind, payload)

        # Verify log file exists
        log_file = tmp_path / ".ai_onboard" / "log.jsonl"
        assert log_file.exists()

        # Read and verify all events
        content = log_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 4

        # Parse and verify each event
        for i, (expected_kind, expected_payload) in enumerate(events):
            event_data = json.loads(lines[i])
            assert event_data["kind"] == expected_kind
            assert event_data["data"] == expected_payload
            assert "ts" in event_data

    def test_runlog_file_format(self, tmp_path):
        """Test that runlog uses proper JSON Lines format."""
        write_event(tmp_path, "format_test", {"test": "data"})

        log_file = tmp_path / ".ai_onboard" / "log.jsonl"
        assert log_file.exists()

        content = log_file.read_text()

        # Should be valid JSON when parsed line by line
        lines = content.strip().split("\n")
        for line in lines:
            # Each line should be valid JSON
            json.loads(line)

        # Should end with newline
        assert content.endswith("\n")

    def test_runlog_append_mode(self, tmp_path):
        """Test that multiple writes append to the same file."""
        # Write first event
        write_event(tmp_path, "first", {"order": 1})

        log_file = tmp_path / ".ai_onboard" / "log.jsonl"

        # Get initial size
        initial_size = log_file.stat().st_size

        # Write second event
        write_event(tmp_path, "second", {"order": 2})

        # File should be larger
        final_size = log_file.stat().st_size
        assert final_size > initial_size

        # Should contain both events
        content = log_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 2

        first_event = json.loads(lines[0])
        second_event = json.loads(lines[1])

        assert first_event["kind"] == "first"
        assert second_event["kind"] == "second"
