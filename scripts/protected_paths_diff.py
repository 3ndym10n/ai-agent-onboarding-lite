from __future__ import annotations

import fnmatch
import json
import os
import subprocess
import sys

PROTECTED = [
    ".github/**",
    "pyproject.toml",
    "README.md",
    "AGENTS.md",
    "ai_onboard / __init__.py",
    "ai_onboard / __main__.py",
    "ai_onboard / VERSION.txt",
    "ai_onboard / cli / commands_refactored.py",
    "ai_onboard / core/**",
    "ai_onboard / policies/**",
    "ai_onboard / schemas/**",
]


def is_feature_branch() -> bool:
    """Check if we're on a feature branch (not main / master)."""
    try:
        # First try: get current branch name
        result = subprocess.run(
            ["git", "rev - parse", "--abbrev - ref", "HEAD"],
            text = True,
            capture_output = True,
            check = True,
        )
        current_branch = result.stdout.strip()

        # Debug output for CI
        print(f"DEBUG: Current branch: '{current_branch}'")

        # If we're in a detached HEAD state (like in GitHub Actions), try alternative methods
        if current_branch == "HEAD":
            print(
                "DEBUG: Detected detached HEAD, trying alternative branch detection..."
            )

            # Method 1: Check if we're in a PR context by looking at remote refs
            try:
                remote_result = subprocess.run(
                    ["git", "branch", "-r", "--contains", "HEAD"],
                    text = True,
                    capture_output = True,
                    check = True,
                )
                remote_branches = remote_result.stdout.strip().split("\n")
                print(f"DEBUG: Remote branches containing HEAD: {remote_branches}")

                # Look for feature branches in remote refs
                for branch in remote_branches:
                    if branch.strip() and any(
                        pat in branch
                        for pat in [
                            "feature/",
                            "feat/",
                            "bugfix/",
                            "hotfix/",
                            "release/",
                        ]
                    ):
                        print(f"DEBUG: Found feature branch in remote refs: {branch}")
                        return True
            except subprocess.CalledProcessError as e:
                print(f"DEBUG: Error checking remote refs: {e}")

            # Method 2: Check if we're in a PR by looking at the base ref
            try:
                # In GitHub Actions, we can check if we're comparing against main
                base_ref = sys.argv[1] if len(sys.argv) > 1 else "origin / main"
                if "main" in base_ref:
                    print(
                        "DEBUG: Comparing against main branch, likely a feature branch"
                    )
                    return True
            except Exception as e:
                print(f"DEBUG: Error checking base ref: {e}")

            # Method 3: Check if we're in a GitHub Actions PR context
            if os.environ.get("GITHUB_EVENT_NAME") == "pull_request":
                print("DEBUG: GitHub Actions PR context detected")
                return True

        # Check if this is a feature branch using standard patterns
        feature_patterns = [
            "feature/",
            "feat/",
            "bugfix/",
            "hotfix/",
            "release/",
            "fix/",
        ]
        is_feature = any(current_branch.startswith(pat) for pat in feature_patterns)

        print(f"DEBUG: Is feature branch: {is_feature}")
        print(f"DEBUG: Feature patterns checked: {feature_patterns}")

        return is_feature
    except subprocess.CalledProcessError as e:
        # If we can't determine branch, be conservative and assume it's not a feature branch
        print(f"DEBUG: Error getting branch: {e}")
        print(f"DEBUG: stderr: {e.stderr}")
        return False


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "origin / main"
    print(f"DEBUG: Base reference: '{base}'")

    # Check if we're on a feature branch
    is_feature = is_feature_branch()

    # Debug: show git status
    try:
        status_result = subprocess.run(
            ["git", "status", "--porcelain"], text = True, capture_output = True, check = True
        )
        print(f"DEBUG: Git status:\n{status_result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"DEBUG: Error getting git status: {e}")

    cp = subprocess.run(
        ["git", "diff", "--name - status", base, "HEAD"],
        text = True,
        capture_output = True,
        check = False,
    )

    print(f"DEBUG: Git diff command: git diff --name - status {base} HEAD")
    print(f"DEBUG: Git diff exit code: {cp.returncode}")
    if cp.stderr:
        print(f"DEBUG: Git diff stderr: {cp.stderr}")

    hits = []
    for ln in (cp.stdout or "").splitlines():
        parts = ln.split("\t", 1)
        if len(parts) < 2:
            continue
        status, path = parts
        touched = any(fnmatch.fnmatch(path, pat) for pat in PROTECTED)
        if touched:
            hits.append({"path": path, "status": status})

    print(f"DEBUG: Protected paths touched: {len(hits)}")

    if hits:
        print(
            json.dumps(
                {
                    "protected_touched": hits,
                    "is_feature_branch": is_feature,
                    "message": "Protected paths touched"
                    + (" (allowed on feature branch)" if is_feature else ""),
                },
                indent = 2,
            )
        )

        # On feature branches, allow changes to protected paths (development is expected)
        # On main branch or unknown, fail (protection is critical)
        if is_feature:
            print(
                "SUCCESS: Allowing protected path changes on feature branch (legitimate development)"
            )
            return 0
        else:
            print(
                "BLOCKED: Blocking protected path changes on main branch (security violation)"
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
