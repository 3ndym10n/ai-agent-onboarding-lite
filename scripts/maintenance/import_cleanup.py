#!/usr/bin/env python3
"""
Import Cleanup Automation Script

This script automates the process of cleaning up imports across the codebase:
1. Removes unused imports (F401 errors)
2. Sorts imports with isort
3. Reports results

Usage:
    python scripts/import_cleanup.py [files...]

If no files are specified, it will check all Python files in ai_onboard/core/
"""
import subprocess
from pathlib import Path
from typing import List

from ai_onboard.core.base.common_imports import sys


def run_command(cmd: List[str], cwd: Path = None) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd, cwd=cwd or Path.cwd(), capture_output=True, text=True, encoding="utf-8"
    )
    return result.returncode, result.stdout, result.stderr


def cleanup_imports(file_path: Path) -> dict:
    """Clean up imports in a single file."""
    results = {
        "file": str(file_path),
        "unused_removed": False,
        "sorted": False,
        "errors": [],
    }

    try:
        # Check for unused imports
        returncode, stdout, stderr = run_command(
            [sys.executable, "-m", "flake8", "--select=F401", str(file_path)]
        )

        if returncode == 0 and stdout.strip():
            # Has unused imports, try to fix them
            print(f"🔍 Found unused imports in {file_path}")

            # For now, we'll just report them
            # Automated removal would require more complex parsing
            results["unused_found"] = True
            results["flake8_output"] = stdout.strip()
        else:
            results["unused_found"] = False

        # Sort imports with isort
        returncode, stdout, stderr = run_command(
            [sys.executable, "-m", "isort", str(file_path)]
        )

        if returncode == 0:
            results["sorted"] = True
        else:
            results["errors"].append(f"isort failed: {stderr}")

    except Exception as e:
        results["errors"].append(f"Error processing {file_path}: {e}")

    return results


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Specific files provided
        files = [Path(f) for f in sys.argv[1:]]
    else:
        # Check all Python files in ai_onboard/core/
        core_dir = Path("ai_onboard/core")
        files = list(core_dir.rglob("*.py"))

    print(
        f"🧹 Starting from .legacy_cleanup.cleanup import cleanup for {len(files)} files..."
    )

    total_processed = 0
    total_with_unused = 0
    total_sorted = 0
    total_errors = 0

    for file_path in files:
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        results = cleanup_imports(file_path)
        total_processed += 1

        if results.get("unused_found"):
            total_with_unused += 1
            print(
                f"📋 {results['file']}: {len(results.get('flake8_output', '').splitlines())} unused imports"
            )

        if results["sorted"]:
            total_sorted += 1

        if results["errors"]:
            total_errors += 1
            for error in results["errors"]:
                print(f"❌ {error}")

    print("\n📊 Import Cleanup Summary:")
    print(f"   Files processed: {total_processed}")
    print(f"   Files with unused imports: {total_with_unused}")
    print(f"   Files sorted: {total_sorted}")
    print(f"   Errors: {total_errors}")

    if total_with_unused > 0:
        print("\n💡 Note: Unused imports found. These need manual review and removal.")
        print("   Run 'python -m flake8 --select=F401 <file>' to see details.")


if __name__ == "__main__":
    main()
