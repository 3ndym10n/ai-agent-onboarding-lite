#!/usr / bin / env python3
"""
Comprehensive CI testing script.

This script runs all the tests and validations that would be run in CI / CD.
"""

import subprocess
import sys
from typing import List, Tuple


def run_command(command: List[str], description: str) -> Tuple[bool, str]:
    """Run a command and return success status and output."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            capture_output = True,
            text = True,
            check = True,
            shell = True,  # Use shell for Windows compatibility
        )
        print(f"✅ {description} - SUCCESS")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False, e.stderr


def run_python_command(module: str, description: str) -> Tuple[bool, str]:
    """Run a Python module command."""
    return run_command([sys.executable, "-m", module], description)


def run_script_command(script: str, description: str) -> Tuple[bool, str]:
    """Run a script command."""
    return run_command([sys.executable, script], description)


def main():
    """Main function."""
    print("🧪 Running Comprehensive CI Tests")
    print("=" * 50)

    # Track results
    results = []

    # 1. Code formatting checks
    print("\n📝 Code Formatting Checks")
    print("-" * 30)

    results.append(
        run_command(
            [
                sys.executable,
                "-m",
                "black",
                "--check",
                "ai_onboard/",
                "tests/",
                "scripts/",
            ],
            "Black formatter check",
        )
    )

    results.append(
        run_command(
            [
                sys.executable,
                "-m",
                "isort",
                "--check - only",
                "ai_onboard/",
                "tests/",
                "scripts/",
            ],
            "Import sorting check",
        )
    )

    # 2. Linting and type checking
    print("\n🔍 Linting and Type Checking")
    print("-" * 30)

    results.append(
        run_command(
            [sys.executable, "-m", "flake8", "ai_onboard/", "tests/", "scripts/"],
            "Flake8 linting",
        )
    )

    results.append(
        run_command(
            [
                sys.executable,
                "-m",
                "mypy",
                "ai_onboard/",
                "--ignore - missing - imports",
            ],
            "MyPy type checking",
        )
    )

    # 3. Security checks
    print("\n🔒 Security Checks")
    print("-" * 30)

    results.append(
        run_command(
            [sys.executable, "-m", "bandit", "-r", "ai_onboard/", "-f", "json"],
            "Bandit security scan",
        )
    )

    results.append(
        run_command(
            [sys.executable, "-m", "safety", "check", "--json"],
            "Safety dependency check",
        )
    )

    # 4. Unit tests
    print("\n🧪 Unit Tests")
    print("-" * 30)

    results.append(
        run_command(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "-v",
                "--cov = ai_onboard",
                "--cov - report = xml",
            ],
            "Unit tests with coverage",
        )
    )

    # 5. System tests
    print("\n🔧 System Tests")
    print("-" * 30)

    results.append(
        run_script_command("scripts / test_system.py", "System integration tests")
    )

    results.append(
        run_script_command(
            "scripts / validate_dev_env.py", "Development environment validation"
        )
    )

    # 6. AI Agent Collaboration Protocol tests
    print("\n🤖 AI Agent Collaboration Tests")
    print("-" * 30)

    results.append(
        run_python_command(
            "ai_onboard ai - collaboration test", "AI Agent Collaboration Protocol test"
        )
    )

    # 7. Enhanced Vision System tests
    print("\n👁️ Enhanced Vision System Tests")
    print("-" * 30)

    results.append(
        run_python_command(
            "ai_onboard enhanced - vision status", "Enhanced Vision System status check"
        )
    )

    # 8. Core system tests
    print("\n⚙️ Core System Tests")
    print("-" * 30)

    results.append(run_python_command("ai_onboard analyze", "Project analysis test"))

    results.append(run_python_command("ai_onboard validate", "System validation test"))

    # 9. Build and package tests
    print("\n📦 Build and Package Tests")
    print("-" * 30)

    results.append(run_command([sys.executable, "-m", "build"], "Package build test"))

    results.append(
        run_command(
            [sys.executable, "-m", "twine", "check", "dist/*"],
            "Package validation test",
        )
    )

    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)

    passed = sum(1 for success, _ in results if success)
    total = len(results)

    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {(passed / total) * 100:.1f}%")

    if passed == total:
        print("\n🎉 All tests passed! CI / CD pipeline would succeed.")
        return 0
    else:
        print(f"\n❌ {total - passed} tests failed. CI / CD pipeline would fail.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
