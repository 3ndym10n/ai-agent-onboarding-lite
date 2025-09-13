#!/usr/bin/env python3
"""
Validate project structure against expected layout.
"""

import os
import sys


def validate_structure() -> bool:
    """Validate the project structure."""
    print("🔍 Validating project structure...")

    required_files = [
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        "AGENTS.md",
        "ai_onboard/__init__.py",
        "ai_onboard/__main__.py",
        "ai_onboard/VERSION.txt",
        "ai_onboard/core/__init__.py",
        "ai_onboard/cli/__init__.py",
        "ai_onboard/plugins/__init__.py",
        "ai_onboard/policies/__init__.py",
        "ai_onboard/schemas/__init__.py",
    ]

    required_dirs = [
        "ai_onboard",
        "ai_onboard/core",
        "ai_onboard/cli",
        "ai_onboard/plugins",
        "ai_onboard/policies",
        "ai_onboard/schemas",
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/smoke",
        "scripts",
        "config",
        "docs",
        "examples",
    ]

    protected_files = [
        "ai_onboard/policies/base.json",
        "ai_onboard/policies/base.yaml",
        "scripts/protected_paths.py",
        "scripts/protected_paths_diff.py",
    ]

    issues = []

    # Check required files
    for file_path in required_files:
        if not os.path.exists(file_path):
            issues.append(f"Missing required file: {file_path}")

    # Check required directories
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            issues.append(f"Missing required directory: {dir_path}")
        elif not os.path.isdir(dir_path):
            issues.append(f"Path exists but is not a directory: {dir_path}")

    # Check protected files
    for file_path in protected_files:
        if not os.path.exists(file_path):
            issues.append(f"Missing protected file: {file_path}")

    # Check for proper __init__.py files in Python packages
    python_packages = [
        "ai_onboard",
        "ai_onboard / core",
        "ai_onboard / cli",
        "ai_onboard / plugins",
        "ai_onboard / policies",
        "ai_onboard / schemas",
        "tests",
        "tests / unit",
        "tests / integration",
        "tests / smoke",
    ]

    for package in python_packages:
        init_file = os.path.join(package, "__init__.py")
        if os.path.exists(package) and not os.path.exists(init_file):
            issues.append(f"Missing __init__.py in Python package: {package}")

    # Check configuration structure
    config_files = [
        "config/mypy.ini",
        "config/tox.ini",
        "config/dev-config.yaml",
    ]

    for config_file in config_files:
        if not os.path.exists(config_file):
            issues.append(f"Missing configuration file: {config_file}")

    if issues:
        print("❌ Project structure validation failed:")
        for issue in issues:
            print(f"  • {issue}")
        return False

    print("✅ Project structure validation passed")
    return True


def check_file_permissions() -> bool:
    """Check that executable files have proper permissions."""
    print("🔍 Checking file permissions...")

    executable_files = [
        "scripts / protected_paths.py",
        "scripts / protected_paths_diff.py",
        "scripts / validate_dev_env.py",
        "scripts / check_requirements_consistency.py",
        "scripts / validate_project_structure.py",
    ]

    issues = []

    for file_path in executable_files:
        if os.path.exists(file_path):
            # On Windows, we just check if file exists and is readable
            if not os.access(file_path, os.R_OK):
                issues.append(f"File not readable: {file_path}")

    if issues:
        print("❌ File permission issues found:")
        for issue in issues:
            print(f"  • {issue}")
        return False

    print("✅ File permissions check passed")
    return True


def main() -> bool:
    """Main validation function."""
    structure_ok = validate_structure()
    permissions_ok = check_file_permissions()

    return structure_ok and permissions_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
