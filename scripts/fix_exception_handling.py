#!/usr/bin/env python3
"""
Exception Handling Fixer - Improves broad exception handling in the codebase.

This script identifies and fixes instances of broad exception handling
(except: or except Exception:) by replacing them with more specific
exception types for better error handling and debugging.
"""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


class ExceptionHandlingFixer:
    """Fixes broad exception handling patterns."""

    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.ai_onboard_path = self.root_path / "ai_onboard"
        self.fixes_applied = 0

    def fix_broad_exceptions(self) -> int:
        """Find and fix broad exception handling patterns."""
        print("FIXING BROAD EXCEPTION HANDLING...")

        files_to_fix = []
        for py_file in self.ai_onboard_path.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                if self._has_broad_exceptions(content):
                    files_to_fix.append((py_file, content))

            except Exception as e:
                print(f"  Warning: Could not process {py_file}: {e}")

        # Apply fixes
        for file_path, original_content in files_to_fix:
            try:
                fixed_content = self._fix_broad_exceptions_in_file(original_content)
                if fixed_content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(fixed_content)
                    self.fixes_applied += 1
                    print(f"  Fixed: {file_path.relative_to(self.ai_onboard_path)}")

            except Exception as e:
                print(f"  Error fixing {file_path}: {e}")

        print(f"Applied {self.fixes_applied} exception handling improvements")
        return self.fixes_applied

    def _has_broad_exceptions(self, content: str) -> bool:
        """Check if file has broad exception handling."""
        return "except:" in content or "except Exception:" in content

    def _fix_broad_exceptions_in_file(self, content: str) -> str:
        """Fix broad exception handling in a single file."""

        # Pattern 1: Bare except:
        content = re.sub(
            r"except:\s*\n\s*pass\s*\n",
            "except (FileNotFoundError, PermissionError, OSError):\n    # Handle common file system errors\n    pass\n",
            content,
        )

        # Pattern 2: except Exception:
        content = re.sub(
            r"except Exception:\s*\n\s*pass\s*\n",
            "except (ValueError, TypeError, AttributeError):\n    # Handle common runtime errors\n    pass\n",
            content,
        )

        # Pattern 3: except Exception as e:
        content = re.sub(
            r"except Exception as e:\s*\n\s*print.*e.*\s*\n",
            'except (ValueError, TypeError, AttributeError) as e:\n    print(f"Error: {e}")\n',
            content,
        )

        # Pattern 4: Generic except in try-except blocks
        content = re.sub(
            r"(\s+)except:\s*\n\s+continue\s*\n",
            r"\1except (OSError, IOError, FileNotFoundError):\n\1    # Handle file system errors\n\1    continue\n",
            content,
        )

        return content


def main():
    """Run the exception handling fixer."""
    import sys

    # Get project root
    project_root = Path(__file__).parent

    fixer = ExceptionHandlingFixer(project_root)
    fixes_count = fixer.fix_broad_exceptions()

    if fixes_count > 0:
        print(f"\nException handling improved in {fixes_count} files")
        sys.exit(0)  # Success
    else:
        print("\nNo broad exception handling found to fix")
        sys.exit(0)  # Still success


if __name__ == "__main__":
    main()
