from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[1]

# Keep in sync with scripts / protected_paths.py
PROTECTED_FILES = {
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
    # Baseline policy
    "ai_onboard / policies / base.json",
}


def get_staged_deletions() -> List[str]:
    # Use name - status to detect deletions (D) and renames (Rxxx)
    out = subprocess.check_output(
        ["git", "-C", str(REPO_ROOT), "diff", "--cached", "--name - status"],
        text=True,
        stderr=subprocess.DEVNULL,
    )
    deleted: List[str] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        status, *rest = line.split("\t")
        code = status[:1]
        if code == "D" and rest:
            deleted.append(rest[0])
        elif code == "R" and len(rest) == 2:
            # Rename: old path -> new path; treat old as deleted
            old_path, _new_path = rest
            deleted.append(old_path)
    return deleted


def main() -> int:
    if os.getenv("BYPASS_PROTECTED_HOOK") == "1":
        print("[pre - commit] Bypass enabled via BYPASS_PROTECTED_HOOK = 1")
        return 0

    try:
        deletions = get_staged_deletions()
    except subprocess.CalledProcessError:
        # If git diff fails (unlikely in hook), do not block
        return 0

    violations = [p for p in deletions if p.replace("\\", "/") in PROTECTED_FILES]

    if violations:
        print("\nProtected deletions detected; commit blocked:\n")
        for p in violations:
            print(f" - {p}")
        print(
            "\nThese files are protected (core / CLI / policies). If you truly intend to remove them,\n"
            "either set BYPASS_PROTECTED_HOOK = 1 for this commit or use --no - verify,\n"
            "then ensure CI and CODEOWNERS approvals are satisfied."
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
