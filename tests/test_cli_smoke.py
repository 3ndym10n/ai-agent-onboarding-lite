import json
import subprocess
import sys


def test_prompt_state_smoke():
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
