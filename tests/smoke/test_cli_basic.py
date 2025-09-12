"""
Smoke tests for basic CLI functionality.

These tests provide quick validation that core CLI commands work correctly.
They are designed to run fast and catch major regressions.
"""

import json
import subprocess
import sys


def test_prompt_state_smoke():
    """Test that 'prompt state' command returns valid JSON."""
    cp = subprocess.run(
        [sys.executable, "-m", "ai_onboard", "prompt", "state"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert cp.returncode == 0, cp.stderr
    data = json.loads(cp.stdout)
    assert isinstance(data, dict)
    assert "manifest_present" in data


def test_prompt_summary_brief_smoke():
    """Test that 'prompt summary --level brief' command returns valid JSON."""
    cp = subprocess.run(
        [sys.executable, "-m", "ai_onboard", "prompt", "summary", "--level", "brief"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert cp.returncode == 0, cp.stderr
    data = json.loads(cp.stdout)
    assert isinstance(data, dict)
    assert "top_components" in data


def test_status_command_smoke():
    """Test that 'status' command runs without error."""
    cp = subprocess.run(
        [sys.executable, "-m", "ai_onboard", "status"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert cp.returncode == 0, f"Status command failed: {cp.stderr}"
    assert len(cp.stdout) > 0, "Status command produced no output"


def test_help_command_smoke():
    """Test that help command works."""
    cp = subprocess.run(
        [sys.executable, "-m", "ai_onboard", "--help"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert cp.returncode == 0, f"Help command failed: {cp.stderr}"
    assert (
        "usage:" in cp.stdout.lower()
    ), "Help output doesn't contain usage information"
