from __future__ import annotations

from pathlib import Path

from ai_onboard.core.base.common_imports import sys

REPO_ROOT = Path(__file__).resolve().parents[1]

# Minimal set of paths that must exist in any valid repo state
REQUIRED_FILES = [
    # Top - level project metadata
    "pyproject.toml",
    "README.md",
    "AGENTS.md",
    # Package identity
    "ai_onboard / __init__.py",
    "ai_onboard / __main__.py",
    "ai_onboard / VERSION.txt",
    # CLI entry
    "ai_onboard / cli / __init__.py",
    "ai_onboard / cli / commands_refactored.py",
    # Core runtime (minimum viable)
    "ai_onboard / core / __init__.py",
    "ai_onboard / core / utils.py",
    "ai_onboard / core / state.py",
    "ai_onboard / core / telemetry.py",
    "ai_onboard / core / validation_runtime.py",
    "ai_onboard / core / policy_engine.py",
    "ai_onboard / core / registry.py",
    # Policies (baseline)
    "ai_onboard / policies / base.json",
]

REQUIRED_DIRS = [
    ".github",
    ".github / workflows",
    "ai_onboard",
    "ai_onboard / cli",
    "ai_onboard / core",
    "ai_onboard / plugins",
    "ai_onboard / plugins / conventions",
    "ai_onboard / plugins / library_module",
    "ai_onboard / plugins / ui_frontend",
    "ai_onboard / policies",
    "ai_onboard / policies / overlays",
    "ai_onboard / schemas",
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
