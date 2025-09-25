#!/usr / bin / env python3
"""
Script to systematically fix linting issues.
"""

import re
import subprocess
from pathlib import Path
from typing import List


def remove_unused_imports(file_path: Path) -> bool:
    """Remove unused imports from a Python file."""
    try:
        # Use autoflake to remove unused imports
        result = subprocess.run(
            [
                "python",
                "-m",
                "autoflake",
                "--remove - all - unused - imports",
                "--remove - unused - variables",
                "--in - place",
                str(file_path),
            ],
            capture_output=True,
            text=True,
        )

        return result.returncode == 0
    except FileNotFoundError:
        print(f"⚠️  autoflake not available, skipping {file_path}")
        return False


def fix_line_length_issues(file_path: Path) -> bool:
    """Fix line length issues using Black."""
    try:
        result = subprocess.run(
            ["python", "-m", "black", "--line - length = 88", str(file_path)],
            capture_output=True,
            text=True,
        )

        return result.returncode == 0
    except Exception as e:
        print(f"⚠️  Error formatting {file_path}: {e}")
        return False


def fix_whitespace_issues(file_path: Path) -> bool:
    """Fix whitespace issues manually."""
    try:
        with open(file_path, "r", encoding="utf - 8") as f:
            content = f.read()

        # Fix missing whitespace around operators
        content = re.sub(r"(\w)([+\-*/%=<>!]+)(\w)", r"\1 \2 \3", content)
        content = re.sub(r"(\w),(\w)", r"\1, \2", content)

        # Remove trailing whitespace
        lines = content.split("\n")
        lines = [line.rstrip() for line in lines]

        # Remove blank lines with whitespace
        lines = [line if line.strip() else "" for line in lines]

        content = "\n".join(lines)

        with open(file_path, "w", encoding="utf - 8") as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"⚠️  Error fixing whitespace in {file_path}: {e}")
        return False


def get_python_files() -> List[Path]:
    """Get all Python files to process."""
    python_files = []

    # Core directories
    for pattern in ["ai_onboard/**/*.py", "tests/**/*.py", "scripts/*.py"]:
        python_files.extend(Path(".").glob(pattern))

    # Filter out __pycache__ and other unwanted files
    return [
        f for f in python_files if "__pycache__" not in str(f) and f.suffix == ".py"
    ]


def main():
    """Main function to fix linting issues."""
    print("🔧 Starting systematic linting fixes...")

    python_files = get_python_files()
    print(f"📁 Found {len(python_files)} Python files to process")

    # Step 1: Fix formatting and line length with Black
    print("\n🎨 Step 1: Fixing formatting and line length...")
    for file_path in python_files:
        if fix_line_length_issues(file_path):
            print(f"✅ Formatted: {file_path}")
        else:
            print(f"❌ Failed to format: {file_path}")

    # Step 2: Fix import sorting
    print("\n📦 Step 2: Fixing import sorting...")
    try:
        result = subprocess.run(
            [
                "python",
                "-m",
                "isort",
                "--profile = black",
                "--line - length = 88",
                "ai_onboard/",
                "tests/",
                "scripts/",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Import sorting completed")
        else:
            print(f"❌ Import sorting failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Import sorting error: {e}")

    # Step 3: Try to install and use autoflake for unused imports
    print("\n🧹 Step 3: Installing autoflake and removing unused imports...")
    try:
        # Install autoflake
        subprocess.run(
            ["python", "-m", "pip", "install", "autoflake"],
            check=True,
            capture_output=True,
        )

        # Remove unused imports
        for file_path in python_files:
            if remove_unused_imports(file_path):
                print(f"✅ Cleaned imports: {file_path}")
    except Exception as e:
        print(f"⚠️  Could not install / use autoflake: {e}")

    # Step 4: Fix whitespace issues
    print("\n⚪ Step 4: Fixing whitespace issues...")
    for file_path in python_files:
        if fix_whitespace_issues(file_path):
            print(f"✅ Fixed whitespace: {file_path}")

    print("\n🎉 Linting fixes completed!")
    print(
        "Run 'python scripts/ci/local_ci_validation.py --step quality' to check results"
    )


if __name__ == "__main__":
    main()
