from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

# Minimal set of paths that must exist in any valid repo state
REQUIRED_FILES = [
    "pyproject.toml",
    "README_ai_onboard.md",
    "AGENTS.md",
    "ai_onboard/__main__.py",
    "ai_onboard/cli/commands.py",
    "ai_onboard/core/validation_runtime.py",
    "ai_onboard/core/telemetry.py",
    "ai_onboard/core/state.py",
]

REQUIRED_DIRS = [
    ".github",
    "ai_onboard",
    "ai_onboard/core",
    "ai_onboard/plugins",
]


def main() -> int:
    ok = True

    missing_files = [p for p in REQUIRED_FILES if not (REPO_ROOT / p).exists()]
    missing_dirs = [p for p in REQUIRED_DIRS if not (REPO_ROOT / p).exists()]

    if missing_files or missing_dirs:
        print("Protected paths check failed:")
        if missing_files:
            print("- Missing required files:")
            for p in missing_files:
                print(f"  - {p}")
        if missing_dirs:
            print("- Missing required directories:")
            for p in missing_dirs:
                print(f"  - {p}")
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

