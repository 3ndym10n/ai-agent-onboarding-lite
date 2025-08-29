from __future__ import annotations

import sys
import subprocess
import json
import fnmatch


PROTECTED = [
    ".github/**",
    "pyproject.toml",
    "README_ai_onboard.md",
    "AGENTS.md",
    "ai_onboard/__init__.py",
    "ai_onboard/__main__.py",
    "ai_onboard/VERSION",
    "ai_onboard/cli/commands.py",
    "ai_onboard/core/**",
    "ai_onboard/policies/**",
    "ai_onboard/schemas/**",
]


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    cp = subprocess.run([
        "git", "diff", "--name-status", base, "HEAD"
    ], text=True, capture_output=True, check=False)
    hits = []
    for ln in (cp.stdout or "").splitlines():
        parts = ln.split("\t", 1)
        if len(parts) < 2:
            continue
        status, path = parts
        touched = any(fnmatch.fnmatch(path, pat) for pat in PROTECTED)
        if touched:
            hits.append({"path": path, "status": status})
    if hits:
        print(json.dumps({"protected_touched": hits}, indent=2))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
