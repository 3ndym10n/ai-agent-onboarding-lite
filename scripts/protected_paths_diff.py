from __future__ import annotations

import sys
import subprocess
import json
import fnmatch


PROTECTED = [
    ".github/**",
    "ai_onboard/**",
    "ai_onboard/cli/**",
    "ai_onboard/core/**",
    "ai_onboard/plugins/**",
    "ai_onboard/policies/**",
    "ai_onboard/schemas/**",
    "ai_onboard/__init__.py",
    "ai_onboard/__main__.py",
    "ai_onboard/VERSION",
]


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    cp = subprocess.run([
        "git", "diff", "--name-only", base, "HEAD"
    ], text=True, capture_output=True, check=False)
    changed = [p.strip() for p in (cp.stdout or "").splitlines() if p.strip()]
    hits = []
    for pat in PROTECTED:
        hits.extend([p for p in changed if fnmatch.fnmatch(p, pat)])
    if hits:
        print(json.dumps({"protected_touched": sorted(set(hits))}, indent=2))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

