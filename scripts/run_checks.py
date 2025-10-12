"""
Run local quality checks for production readiness.

This script intentionally avoids adding dependencies. It runs what is
available in the environment and reports concise results.

Checks:
- Unit tests via pytest (if installed)
- Type checks via mypy (if installed)
- Dependency audit via pip-audit (if installed)

Usage:
  python scripts/run_checks.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> int:
    try:
        print("$", " ".join(cmd))
        return subprocess.run(cmd, check=False).returncode
    except Exception as e:
        print(f"[WARN] failed to run {' '.join(cmd)}: {e}")
        return 1


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    rc = 0

    # pytest
    if shutil.which("pytest"):
        print("\n[TEST] Running unit tests...")
        rc |= run([sys.executable, "-m", "pytest", "-q"])
    else:
        print("[SKIP] pytest not installed")

    # mypy
    if shutil.which("mypy"):
        print("\n[TYPE] Running mypy (py38 target)...")
        rc |= run(["mypy", "--python-version", "3.8", str(root / "ai_onboard")])
    else:
        print("[SKIP] mypy not installed")

    # pip-audit
    if shutil.which("pip-audit"):
        print("\n[SEC] Running pip-audit...")
        rc |= run(["pip-audit", "-r", str(root / "requirements.txt")]) if (root / "requirements.txt").exists() else run(["pip-audit"]) 
    else:
        print("[SKIP] pip-audit not installed")

    print("\n[SUMMARY] Exit code:", rc)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

