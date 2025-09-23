#!/usr/bin/env python3
"""
Fix all syntax errors in Python files.
"""

import re
from pathlib import Path


def fix_all_syntax_errors():
    ai_onboard_dir = Path("ai_onboard")
    python_files = list(ai_onboard_dir.rglob("*.py"))

    fixed_count = 0
    for file_path in python_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix unterminated strings by joining lines
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
                        if next_line.strip().startswith(
                            '"'
                        ) or next_line.strip().startswith("'"):
                            # Join the lines
                            new_line = line.rstrip() + " " + next_line.strip()
                            new_lines.append(new_line)
                            i += 2
                            continue

                new_lines.append(line)
                i += 1

            new_content = "\n".join(new_lines)

            if new_content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Fixed: {file_path}")
                fixed_count += 1

        except Exception as e:
            print(f"Error fixing {file_path}: {e}")

    print(f"Fixed {fixed_count} files")


if __name__ == "__main__":
    fix_all_syntax_errors()
