"""
Tests for checkpoint system.

This module tests the core checkpoint functionality that allows
saving and restoring project states for recovery and rollback.
"""

import json
from pathlib import Path

from ai_onboard.core.base.checkpoints import (
    _ckpt_dir,
    _normalize_scope,
    create,
    list,
    restore,
)


class TestCheckpointDirectory:
    """Test checkpoint directory management."""

    def test_ckpt_dir_creation(self, tmp_path):
        """Test checkpoint directory path generation."""
        result = _ckpt_dir(tmp_path)
        expected = tmp_path / ".ai_onboard" / "checkpoints"

        assert result == expected
        assert isinstance(result, Path)


class TestScopeNormalization:
    """Test file scope normalization."""

    def test_normalize_scope_files(self, tmp_path):
        """Test normalizing file paths."""
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "subdir" / "file2.txt"
        file1.write_text("content1")
        file2.parent.mkdir()
        file2.write_text("content2")

        scope = ["file1.txt", "subdir/file2.txt"]
        result = _normalize_scope(tmp_path, scope)

        assert len(result) == 2
        assert Path("file1.txt") in result
        assert Path("subdir/file2.txt") in result
        assert all(isinstance(p, Path) for p in result)

    def test_normalize_scope_directories(self, tmp_path):
        """Test normalizing directory paths."""
        # Create test directory with files
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")

        scope = ["test_dir"]
        result = _normalize_scope(tmp_path, scope)

        assert len(result) == 1  # only the directory itself
        assert Path("test_dir") in result
        assert all(isinstance(p, Path) for p in result)

    def test_normalize_scope_empty(self, tmp_path):
        """Test normalizing empty scope."""
        scope = []
        result = _normalize_scope(tmp_path, scope)

        assert result == []

    def test_normalize_scope_nonexistent(self, tmp_path):
        """Test normalizing non-existent files."""
        scope = ["nonexistent.txt"]
        result = _normalize_scope(tmp_path, scope)

        # Should return empty list for non-existent files
        assert len(result) == 0


class TestCreateCheckpoint:
    """Test checkpoint creation functionality."""

    def test_create_checkpoint_basic(self, tmp_path):
        """Test basic checkpoint creation."""
        # Create test files
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        result = create(tmp_path, ["test.txt"], "test checkpoint")

        assert isinstance(result, dict)
        assert "id" in result
        assert "ts" in result  # timestamp field
        assert "reason" in result
        assert "scope" in result
        assert result["reason"] == "test checkpoint"
        assert "test.txt" in result["scope"]

    def test_create_checkpoint_with_directory(self, tmp_path):
        """Test checkpoint creation with directory scope."""
        # Create test directory structure
        test_dir = tmp_path / "project"
        test_dir.mkdir()
        (test_dir / "main.py").write_text("print('hello')")
        (test_dir / "utils.py").write_text("def util(): pass")

        result = create(tmp_path, ["project"], "project backup")

        assert isinstance(result, dict)
        assert "id" in result
        assert result["reason"] == "project backup"
        # Should include only the directory in scope
        assert "project" in result["scope"]

    def test_create_checkpoint_empty_scope(self, tmp_path):
        """Test checkpoint creation with empty scope."""
        result = create(tmp_path, [], "empty checkpoint")

        assert isinstance(result, dict)
        assert "id" in result
        assert result["reason"] == "empty checkpoint"
        assert result["scope"] == []


class TestListCheckpoints:
    """Test checkpoint listing functionality."""

    def test_list_checkpoints_empty(self, tmp_path):
        """Test listing checkpoints when none exist."""
        result = list(tmp_path)

        assert result == []
        assert len(result) == 0

    def test_list_checkpoints_with_data(self, tmp_path):
        """Test listing checkpoints with existing data."""
        # Create checkpoint directory and index file
        ckpt_dir = tmp_path / ".ai_onboard" / "checkpoints"
        ckpt_dir.mkdir(parents=True)
        index_file = ckpt_dir / "index.jsonl"

        checkpoint_data = {
            "id": "test-ckpt-123",
            "ts": "2024-01-01T12:00:00",
            "reason": "test checkpoint",
            "scope": ["file1.txt"],
        }

        index_file.write_text(json.dumps(checkpoint_data) + "\n")

        result = list(tmp_path)

        assert result == [checkpoint_data]
        assert len(result) == 1
        assert result[0]["id"] == "test-ckpt-123"
        assert result[0]["reason"] == "test checkpoint"

    def test_list_checkpoints_multiple(self, tmp_path):
        """Test listing multiple checkpoints."""
        ckpt_dir = tmp_path / ".ai_onboard" / "checkpoints"
        ckpt_dir.mkdir(parents=True)
        index_file = ckpt_dir / "index.jsonl"

        # Create multiple checkpoint entries in index
        entries = []
        for i in range(3):
            ckpt_data = {
                "id": f"ckpt-{i}",
                "ts": f"2024-01-{i + 1:02d}T12:00:00",
                "reason": f"checkpoint {i}",
                "scope": [],
            }
            entries.append(ckpt_data)

        # Write to index file in reverse order (newest first)
        content = "\n".join(json.dumps(entry) for entry in reversed(entries)) + "\n"
        index_file.write_text(content)

        result = list(tmp_path)

        assert len(result) == 3
        # Should be in the order they appear in the file
        assert result[0]["id"] == "ckpt-2"
        assert result[1]["id"] == "ckpt-1"
        assert result[2]["id"] == "ckpt-0"


class TestRestoreCheckpoint:
    """Test checkpoint restoration functionality."""

    def test_restore_checkpoint_not_found(self, tmp_path):
        """Test restoring non-existent checkpoint."""
        result = restore(tmp_path, "nonexistent-id")

        assert result == {
            "restored": 0,
            "errors": ["missing checkpoint: nonexistent-id"],
        }

    def test_restore_checkpoint_success(self, tmp_path):
        """Test successful checkpoint restoration."""
        # Create a file to checkpoint
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World!")

        # Create checkpoint
        ckpt_result = create(tmp_path, ["test.txt"], "test restore")

        # Modify the file
        test_file.write_text("Modified content")

        # Restore checkpoint
        result = restore(tmp_path, ckpt_result["id"])

        assert isinstance(result, dict)
        assert result["restored"] == 1
        assert result["errors"] == []
        # File should be restored
        assert test_file.read_text() == "Hello World!"


class TestIntegration:
    """Integration tests for checkpoint system."""

    def test_full_checkpoint_workflow(self, tmp_path):
        """Test complete checkpoint create-list-restore workflow."""
        # Create a test file
        test_file = tmp_path / "integration.txt"
        test_file.write_text("Integration test content")

        # Create checkpoint
        ckpt_info = create(tmp_path, ["integration.txt"], "integration test")

        assert "id" in ckpt_info
        ckpt_id = ckpt_info["id"]

        # List checkpoints
        checkpoints = list(tmp_path)
        assert len(checkpoints) == 1
        assert checkpoints[0]["id"] == ckpt_id

        # Modify the file
        test_file.write_text("Modified content")

        # Restore checkpoint
        restore(tmp_path, ckpt_id)

        # Verify file was restored
        assert test_file.read_text() == "Integration test content"
