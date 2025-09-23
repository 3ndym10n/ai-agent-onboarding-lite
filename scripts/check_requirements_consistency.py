#!/usr / bin / env python3
"""
Check consistency between requirements.txt and pyproject.toml dependencies.
"""
from ai_onboard.core.common_imports import sys

import tomllib
from pathlib import Path
from typing import Dict, Tuple


def parse_requirements_txt() -> Dict[str, str]:
    """Parse requirements.txt and return package versions."""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return {}

    packages = {}
    with open(requirements_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "==" in line:
                    name, version = line.split("==", 1)
                    packages[name.strip()] = version.strip()
                else:
                    packages[line] = "unpinned"

    return packages


def parse_pyproject_toml() -> Tuple[Dict[str, str], Dict[str, str]]:
    """Parse pyproject.toml and return main and dev dependencies."""
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        print("❌ pyproject.toml not found")
        return {}, {}

    with open(pyproject_file, "rb") as f:
        data = tomllib.load(f)

    main_deps = {}
    dev_deps = {}

    # Parse main dependencies
    if "project" in data and "dependencies" in data["project"]:
        for dep in data["project"]["dependencies"]:
            if "==" in dep:
                name, version = dep.split("==", 1)
                main_deps[name.strip()] = version.strip()
            else:
                main_deps[dep] = "unpinned"

    # Parse dev dependencies
    if (
        "project" in data
        and "optional - dependencies" in data["project"]
        and "dev" in data["project"]["optional - dependencies"]
    ):
        for dep in data["project"]["optional - dependencies"]["dev"]:
            if "==" in dep:
                name, version = dep.split("==", 1)
                dev_deps[name.strip()] = version.strip()
            else:
                dev_deps[dep] = "unpinned"

    return main_deps, dev_deps


def check_consistency() -> bool:
    """Check consistency between requirements files."""
    print("🔍 Checking requirements consistency...")

    requirements_packages = parse_requirements_txt()
    main_deps, dev_deps = parse_pyproject_toml()

    # Combine pyproject dependencies
    all_pyproject_deps = {**main_deps, **dev_deps}

    inconsistencies = []

    # Check for version mismatches
    for pkg, req_version in requirements_packages.items():
        if pkg in all_pyproject_deps:
            pyproject_version = all_pyproject_deps[pkg]
            if req_version != pyproject_version:
                inconsistencies.append(
                    f"Version mismatch for {pkg}: "
                    f"requirements.txt={req_version}, pyproject.toml={pyproject_version}"
                )

    # Check for missing packages
    req_packages = set(requirements_packages.keys())
    pyproject_packages = set(all_pyproject_deps.keys())

    missing_in_pyproject = req_packages - pyproject_packages
    missing_in_requirements = pyproject_packages - req_packages

    for pkg in missing_in_pyproject:
        inconsistencies.append(
            f"Package {pkg} in requirements.txt but not in pyproject.toml"
        )

    for pkg in missing_in_requirements:
        inconsistencies.append(
            f"Package {pkg} in pyproject.toml but not in requirements.txt"
        )

    if inconsistencies:
        print("❌ Requirements consistency issues found:")
        for issue in inconsistencies:
            print(f"  • {issue}")
        return False

    print("✅ Requirements are consistent")
    return True


if __name__ == "__main__":
    success = check_consistency()
    sys.exit(0 if success else 1)
