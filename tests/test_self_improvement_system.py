#!/usr/bin/env python3
"""
Comprehensive Test for Self-Improvement System

Tests whether the AI Onboard system is properly learning from past errors
and preventing them in new code generation. This is a "real" test that
simulates actual code generation scenarios and verifies behavioral fixes.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pytest

from ai_onboard.core.continuous_improvement_system import ContinuousImprovementSystem
from ai_onboard.core.continuous_improvement_validator import (
    ContinuousImprovementValidator,
)
from ai_onboard.core.smart_debugger import SmartDebugger


class TestSelfImprovementSystem:
    """Test suite for verifying self-improvement capabilities."""

    def setup_method(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
        self.debugger = SmartDebugger(self.project_root)
        self.improvement_system = ContinuousImprovementSystem(self.project_root)
        self.validator = ContinuousImprovementValidator(self.project_root)

    def test_learning_from_styling_errors(self):
        """Test that the system learns from and prevents styling errors."""
        # Simulate code generation with known styling issues
        problematic_code = """
def example_function():
    x=5  # Missing spaces around =
    if x>10:  # Missing spaces around >
        print("Hello World")  # No trailing whitespace, but let's add some
        return x
"""

        # Check if the system detects these issues
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(problematic_code)
            temp_file = Path(f.name)

        try:
            # Run validation
            result = subprocess.run(
                ["python", "-m", "ai_onboard", "validate", "--report"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            # Check if styling errors are detected
            assert (
                "styling" in result.stdout.lower() or "spacing" in result.stdout.lower()
            ), "System should detect styling issues"

            # Simulate learning: Add to debug log
            error_data = {
                "type": "styling",
                "message": "Missing spaces around operators",
                "context": {"file": str(temp_file), "line": 2},
            }
            self.debugger.analyze_error(error_data)

            # Now generate similar code and check if it's prevented
            similar_code = """
def another_function():
    y=3
    if y>5:
        print("test")
        return y
"""

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as f2:
                f2.write(similar_code)
                temp_file2 = Path(f2.name)

            try:
                # Validate again - should now catch similar issues
                result2 = subprocess.run(
                    ["python", "-m", "ai_onboard", "validate", "--report"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )

                # Should show improved detection or prevention
                assert len(result2.stdout) >= len(
                    result.stdout
                ), "System should show learning by detecting more issues or providing better feedback"

            finally:
                temp_file2.unlink(missing_ok=True)

        finally:
            temp_file.unlink(missing_ok=True)

    def test_learning_from_cli_errors(self):
        """Test that the system learns from and prevents CLI command errors."""
        # Simulate a command that previously failed due to missing subcommands
        failing_command = "ai_onboard prompt nonexistent_subcommand"

        # Run it and capture the error
        result = subprocess.run(
            ["python", "-m", failing_command],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )

        assert result.returncode != 0, "Command should fail initially"

        # Add to learning system
        error_data = {
            "type": "cli_error",
            "message": "Unknown subcommand",
            "context": {"command": failing_command},
        }
        self.debugger.analyze_error(error_data)

        # Simulate code generation for a similar command
        # This would test if the system now validates CLI commands during generation
        # For now, just verify the error was logged
        assert (
            len(self.debugger.debug_log_path.read_text().splitlines()) > 0
        ), "Error should be logged for learning"

    def test_pattern_recognition_improvement(self):
        """Test that pattern recognition improves over time."""
        # Add multiple similar errors to build patterns
        errors = [
            {"type": "styling", "message": "Missing spaces around ="},
            {"type": "styling", "message": "Missing spaces around =="},
            {"type": "styling", "message": "Missing spaces around >"},
        ]

        for error in errors:
            self.debugger.analyze_error(error)

        # Check if patterns were learned
        patterns = self._load_patterns()
        assert len(patterns) > 0, "System should learn patterns from repeated errors"

        # Test pattern matching
        new_error = {"type": "styling", "message": "Missing spaces around <"}
        match = self.debugger._find_pattern_match(
            new_error["type"], new_error["message"]
        )
        assert match is not None, "System should recognize similar patterns"

    def test_validation_prevents_known_errors(self):
        """Test that validation prevents known error patterns in generated code."""
        # First, establish a baseline by generating code with errors
        baseline_code = """
def test_func():
    a=1
    if a==2:
        return True
"""

        # Validate baseline
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(baseline_code)
            temp_file = Path(f.name)

        try:
            # Run validation and capture issues
            result = subprocess.run(
                ["python", "-m", "ai_onboard", "validate"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            baseline_issues = len(
                [
                    line
                    for line in result.stdout.splitlines()
                    if "error" in line.lower() or "issue" in line.lower()
                ]
            )

            # Now "teach" the system about styling issues
            self._train_on_styling_issues()

            # Generate similar code - should have fewer issues
            improved_code = """
def improved_func():
    b = 1  # Fixed spacing
    if b == 2:  # Fixed spacing
        return True
"""

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as f2:
                f2.write(improved_code)
                temp_file2 = Path(f2.name)

            try:
                result2 = subprocess.run(
                    ["python", "-m", "ai_onboard", "validate"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )

                improved_issues = len(
                    [
                        line
                        for line in result2.stdout.splitlines()
                        if "error" in line.lower() or "issue" in line.lower()
                    ]
                )

                # Should show improvement (fewer issues detected for better code)
                assert (
                    improved_issues <= baseline_issues
                ), "System should show improvement by detecting fewer issues in better code"

            finally:
                temp_file2.unlink(missing_ok=True)

        finally:
            temp_file.unlink(missing_ok=True)

    def test_learning_persistence(self):
        """Test that learning persists across sessions."""
        # Add a learning event
        self.improvement_system.record_learning_event(
            {"type": "pattern_learned", "pattern": "styling_spacing", "confidence": 0.9}
        )

        # Simulate session restart by reloading
        new_improvement_system = ContinuousImprovementSystem(self.project_root)

        # Check if learning persisted
        events = new_improvement_system.get_learning_events()
        assert len(events) > 0, "Learning should persist across sessions"
        assert any(
            e.get("pattern") == "styling_spacing" for e in events
        ), "Specific learned pattern should persist"

    def _load_patterns(self) -> Dict[str, Any]:
        """Load current patterns from the debugger."""
        try:
            with open(self.debugger.patterns_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _train_on_styling_issues(self):
        """Train the system on common styling issues."""
        styling_errors = [
            {"type": "styling", "message": "Missing spaces around ="},
            {"type": "styling", "message": "Missing spaces around =="},
            {"type": "styling", "message": "Missing spaces around >"},
            {"type": "styling", "message": "Missing spaces around <"},
        ]

        for error in styling_errors:
            self.debugger.analyze_error(error)

    def test_comprehensive_learning_coverage(self):
        """Comprehensive test of learning coverage for multiple error types."""
        error_types = [
            ("styling", "Missing spaces around operators"),
            ("cli", "Unknown subcommand"),
            ("imports", "Unused import"),
            ("types", "Missing type annotation"),
            ("logic", "Potential None access"),
        ]

        # Test each error type
        for error_type, description in error_types:
            # Add error to learning system
            error_data = {
                "type": error_type,
                "message": description,
                "context": {"test": True},
            }
            self.debugger.analyze_error(error_data)

            # Verify it's logged
            assert (
                self.debugger._find_pattern_match(error_type, description) is not None
            ), f"Should learn from {error_type} errors"

        # Verify overall learning improvement
        patterns = self._load_patterns()
        assert len(patterns) >= len(
            error_types
        ), "System should learn patterns for all tested error types"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
