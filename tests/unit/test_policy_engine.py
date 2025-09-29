"""
Tests for policy engine system.

This module tests the core policy loading and evaluation functionality
that manages quality gates and policy enforcement.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from ai_onboard.core.quality_safety.policy_engine import _merge, _read_policy_file, load


class TestReadPolicyFile:
    """Test policy file reading functionality."""

    def test_read_policy_file_exists(self, tmp_path):
        """Test reading an existing policy file."""
        policy_file = tmp_path / "policy.json"
        policy_data = {
            "rules": [{"id": "test-rule", "action": "allow", "condition": "test"}],
            "scoring": {
                "pass_threshold": 0.8,
                "weights": {"error": 1.0, "warn": 0.5, "info": 0.2},
            },
        }

        import json

        policy_file.write_text(json.dumps(policy_data))

        result = _read_policy_file(policy_file)

        assert result == policy_data
        assert "rules" in result
        assert "scoring" in result
        assert result["rules"][0]["id"] == "test-rule"

    def test_read_policy_file_not_exists(self, tmp_path):
        """Test reading a non-existent policy file returns defaults."""
        policy_file = tmp_path / "nonexistent.json"

        result = _read_policy_file(policy_file)

        # Should return default policy structure
        assert "rules" in result
        assert "scoring" in result
        assert result["rules"] == []
        assert result["scoring"]["pass_threshold"] == 0.7
        assert "weights" in result["scoring"]


class TestLoadPolicy:
    """Test policy loading functionality."""

    @patch("ai_onboard.core.quality_safety.policy_engine._read_policy_file")
    @patch("ai_onboard.core.quality_safety.policy_engine.Path")
    def test_load_basic_policy(self, mock_path_class, mock_read_policy):
        """Test loading a basic policy."""
        mock_root = Path("/test/root")
        mock_path_class.return_value = mock_root / ".ai_onboard" / "policy.json"

        policy_data = {
            "rules": [{"id": "rule1", "action": "allow"}],
            "scoring": {"pass_threshold": 0.8},
        }
        mock_read_policy.return_value = policy_data

        result = load(mock_root)

        assert result == policy_data
        mock_read_policy.assert_called_once()


class TestMergeFunction:
    """Test policy merging functionality."""

    def test_merge_basic(self):
        """Test basic dictionary merging."""
        dst = {"a": 1, "b": {"x": 1}}
        src = {"b": {"y": 2}, "c": 3}

        _merge(dst, src)

        assert dst["a"] == 1  # unchanged
        assert dst["b"]["x"] == 1  # preserved
        assert dst["b"]["y"] == 2  # added
        assert dst["c"] == 3  # added

    def test_merge_lists(self):
        """Test merging lists."""
        dst = {"rules": [{"id": "rule1"}]}
        src = {"rules": [{"id": "rule2"}]}

        _merge(dst, src)

        assert len(dst["rules"]) == 2
        assert dst["rules"][0]["id"] == "rule1"
        assert dst["rules"][1]["id"] == "rule2"

    def test_merge_empty_src(self):
        """Test merging with empty source."""
        dst = {"a": 1, "b": 2}
        src = {}

        _merge(dst, src)

        assert dst == {"a": 1, "b": 2}

    def test_merge_overwrite_values(self):
        """Test that scalar values get overwritten."""
        dst = {"threshold": 0.7}
        src = {"threshold": 0.9}

        _merge(dst, src)

        assert dst["threshold"] == 0.9


class TestIntegration:
    """Integration tests for policy engine."""

    def test_full_policy_loading_workflow(self, tmp_path):
        """Test complete policy loading workflow."""
        # Create policy directory
        policy_dir = tmp_path / ".ai_onboard"
        policy_dir.mkdir()

        # Create base policy
        base_policy = policy_dir / "policy.json"
        base_policy.write_text(
            '{"rules": [{"id": "base"}], "scoring": {"pass_threshold": 0.7}}'
        )

        result = load(tmp_path)

        assert isinstance(result, dict)
        assert "rules" in result
        assert "scoring" in result



