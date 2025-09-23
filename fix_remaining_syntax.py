#!/usr/bin/env python3
"""
Fix remaining syntax errors in Python files.
"""

import os
import re
from pathlib import Path


def fix_terminated_strings(content):
    """Fix unterminated string literals."""
    lines = content.split("\n")
    new_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for unterminated strings
        if ('"' in line and line.count('"') % 2 == 1) or (
            "'" in line and line.count("'") % 2 == 1
        ):
            # Look for continuation on next line
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # If next line is indented and has a quote, join them
                if next_line.strip().startswith('"') or next_line.strip().startswith(
                    "'"
                ):
                    # Join the lines
                    new_line = line.rstrip() + " " + next_line.strip()
                    new_lines.append(new_line)
                    i += 2
                    continue

        new_lines.append(line)
        i += 1

    return "\n".join(new_lines)


def fix_file(file_path):
    """Fix syntax errors in a single file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply fixes
        content = fix_terminated_strings(content)

        # Only write if content changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        else:
            return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    """Main function to fix syntax errors in all Python files."""
    ai_onboard_dir = Path("ai_onboard")

    if not ai_onboard_dir.exists():
        print("ai_onboard directory not found!")
        return

    python_files = list(ai_onboard_dir.rglob("*.py"))

    print(f"Found {len(python_files)} Python files to check...")

    fixed_count = 0
    for file_path in python_files:
        if fix_file(file_path):
            fixed_count += 1

    print(f"\nFixed {fixed_count} files out of {len(python_files)} total files.")


if __name__ == "__main__":
    main()
