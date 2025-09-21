#!/usr/bin/env python3
"""
Automatically fix utils import issues in ai_onboard/core/

This script finds all files that import utils incorrectly and fixes them
to use the dynamic import approach instead of the conflicting package import.
"""

import os
import re

def find_files_with_bad_imports() -> List[Path]:
    """Find all Python files that have the problematic utils import."""
    core_dir = Path("ai_onboard/core")
    bad_files = []

    for py_file in core_dir.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for the problematic import pattern
            if re.search(r"from \. import.*utils", content):
                bad_files.append(py_file)
        except Exception as e:
            print(f"Error reading {py_file}: {e}")

    return bad_files


def fix_utils_import(file_path: Path) -> bool:
    """Fix the utils import in a single file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find the problematic import line
        import_match = re.search(
            r"^(from \. import.*)utils(.*)$", content, re.MULTILINE
        )
        if not import_match:
            print(f"No problematic import found in {file_path}")
            return False

        # Extract the import line and what comes after utils
        before_utils = import_match.group(1)
        after_utils = import_match.group(2)

        # Remove 'utils' from the import list
        if after_utils.strip():
            # There are other imports after utils
            new_import = before_utils.rstrip() + after_utils
        else:
            # utils was the last import, remove the comma before it
            new_import = re.sub(r",\s*utils\s*$", "", before_utils)
            new_import = re.sub(r"utils,\s*", "", new_import)

        # If the import line becomes empty or just "from . import", remove it entirely
        new_import = new_import.strip()
        if new_import == "from . import":
            new_import = ""

        # Add the dynamic import code
        dynamic_import = """
# Import utils functions from utils.py module (avoiding utils/ package conflict)
import importlib.util
from pathlib import Path
_utils_path = Path(__file__).parent / 'utils.py'
_utils_spec = importlib.util.spec_from_file_location('utils_module', _utils_path)
_utils_module = importlib.util.module_from_spec(_utils_spec)
_utils_spec.loader.exec_module(_utils_module)
utils = _utils_module
""".strip()

        # Replace the old import with the new one
        old_import_line = import_match.group(0)
        if new_import:
            new_content = content.replace(
                old_import_line, new_import + "\n\n" + dynamic_import
            )
        else:
            new_content = content.replace(old_import_line + "\n", dynamic_import + "\n")

        # Write back the fixed content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"Fixed {file_path}")
        return True

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    """Main entry point."""
    print("🔍 Finding files with problematic utils imports...")

    bad_files = find_files_with_bad_imports()
    print(f"Found {len(bad_files)} files with import issues:")

    for file_path in bad_files:
        print(f"  - {file_path}")

    print("\n🔧 Fixing imports...")

    fixed_count = 0
    for file_path in bad_files:
        if fix_utils_import(file_path):
            fixed_count += 1

    print("\n📊 Import Fix Summary:")
    print(f"   Files found: {len(bad_files)}")
    print(f"   Files fixed: {fixed_count}")
    print(f"   Errors: {len(bad_files) - fixed_count}")

    if fixed_count > 0:
        print("\n✅ Import fixes applied. Run your tests to verify functionality.")

    return fixed_count == len(bad_files)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
