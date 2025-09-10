#!/usr/bin/env python3
# mypy: ignore-errors
"""
Development Environment Validation Script

This script validates that the development environment is properly set up
and all tools are working correctly.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


class DevEnvironmentValidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.is_windows = platform.system() == "Windows"
        self.results = {}

    def run_command(self, cmd: List[str], cwd: Path = None) -> Tuple[bool, str, str]:
        """Run a command and return success, stdout, stderr."""
        if cwd is None:
            cwd = self.project_root

        try:
            result = subprocess.run(
                cmd, cwd=cwd, capture_output=True, text=True, check=True
            )
            return True, result.stdout.strip(), result.stderr.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stdout.strip(), e.stderr.strip()
        except FileNotFoundError:
            return False, "", f"Command not found: {cmd[0]}"

    def check_python_environment(self) -> Dict[str, Any]:
        """Check Python environment setup."""
        print("🐍 Checking Python environment...")

        results = {
            "python_version": None,
            "virtual_env": None,
            "pip_version": None,
            "package_installed": None,
        }

        # Check Python version
        success, stdout, stderr = self.run_command([sys.executable, "--version"])
        if success:
            results["python_version"] = stdout
            print(f"✅ Python: {stdout}")
        else:
            print(f"❌ Python version check failed: {stderr}")

        # Check virtual environment
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            results["virtual_env"] = sys.prefix
            print(f"✅ Virtual environment: {sys.prefix}")
        else:
            print("⚠️  Not in virtual environment (recommended for development)")

        # Check pip version
        success, stdout, stderr = self.run_command(
            [sys.executable, "-m", "pip", "--version"]
        )
        if success:
            results["pip_version"] = stdout
            print(f"✅ pip: {stdout}")
        else:
            print(f"❌ pip version check failed: {stderr}")

        # Check if package is installed
        try:
            import ai_onboard

            results["package_installed"] = ai_onboard.__version__
            print(f"✅ ai-onboard package: {ai_onboard.__version__}")
        except ImportError:
            print("❌ ai-onboard package not installed")

        return results

    def check_development_tools(self) -> Dict[str, Any]:
        """Check development tools installation."""
        print("\n🛠️  Checking development tools...")

        tools = {
            "black": ["black", "--version"],
            "flake8": ["flake8", "--version"],
            "mypy": ["mypy", "--version"],
            "pytest": ["pytest", "--version"],
            "pre-commit": ["pre-commit", "--version"],
            "isort": ["isort", "--version"],
        }

        results = {}
        for tool, cmd in tools.items():
            success, stdout, stderr = self.run_command(cmd)
            if success:
                results[tool] = stdout
                print(f"✅ {tool}: {stdout}")
            else:
                results[tool] = None
                print(f"❌ {tool}: Not installed or not working")

        return results

    def check_git_configuration(self) -> Dict[str, Any]:
        """Check Git configuration."""
        print("\n🔧 Checking Git configuration...")

        results = {
            "git_version": None,
            "hooks_path": None,
            "pre_commit_installed": None,
        }

        # Check Git version
        success, stdout, stderr = self.run_command(["git", "--version"])
        if success:
            results["git_version"] = stdout
            print(f"✅ Git: {stdout}")
        else:
            print(f"❌ Git version check failed: {stderr}")

        # Check Git hooks path
        success, stdout, stderr = self.run_command(["git", "config", "core.hooksPath"])
        if success:
            results["hooks_path"] = stdout
            print(f"✅ Git hooks path: {stdout}")
        else:
            print("⚠️  Git hooks path not configured")

        # Check if pre-commit is installed
        success, stdout, stderr = self.run_command(["git", "config", "core.hooksPath"])
        if success and "pre-commit" in stdout:
            results["pre_commit_installed"] = True
            print("✅ Pre-commit hooks installed")
        else:
            results["pre_commit_installed"] = False
            print("⚠️  Pre-commit hooks not installed")

        return results

    def check_project_structure(self) -> Dict[str, Any]:
        """Check project structure and files."""
        print("\n📁 Checking project structure...")

        required_files = [
            "pyproject.toml",
            "README_ai_onboard.md",
            "DEVELOPMENT.md",
            ".pre-commit-config.yaml",
            "dev-config.yaml",
            "scripts/setup_dev_env.py",
            "scripts/validate_dev_env.py",
            "scripts/test_system.py",
            ".github/workflows/ci.yml",
        ]

        required_dirs = [
            "ai_onboard",
            "ai_onboard/cli",
            "ai_onboard/core",
            "ai_onboard/plugins",
            "ai_onboard/policies",
            "ai_onboard/schemas",
            "tests",
            "docs",
            "scripts",
        ]

        results = {"files": {}, "directories": {}}

        # Check required files
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                results["files"][file_path] = True
                print(f"✅ File: {file_path}")
            else:
                results["files"][file_path] = False
                print(f"❌ Missing file: {file_path}")

        # Check required directories
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                results["directories"][dir_path] = True
                print(f"✅ Directory: {dir_path}")
            else:
                results["directories"][dir_path] = False
                print(f"❌ Missing directory: {dir_path}")

        return results

    def check_system_functionality(self) -> Dict[str, Any]:
        """Check system functionality."""
        print("\n🧪 Checking system functionality...")

        results = {"cli_help": None, "system_tests": None, "unit_tests": None}

        # Check CLI help
        success, stdout, stderr = self.run_command(
            [sys.executable, "-m", "ai_onboard", "--help"]
        )
        if success:
            results["cli_help"] = True
            print("✅ CLI help command works")
        else:
            results["cli_help"] = False
            print(f"❌ CLI help command failed: {stderr}")

        # Check system tests
        success, stdout, stderr = self.run_command(
            [sys.executable, "scripts/test_system.py"]
        )
        if success:
            results["system_tests"] = True
            print("✅ System tests pass")
        else:
            results["system_tests"] = False
            print(f"❌ System tests failed: {stderr}")

        # Check unit tests
        success, stdout, stderr = self.run_command(
            [sys.executable, "-m", "pytest", "tests/", "-v"]
        )
        if success:
            results["unit_tests"] = True
            print("✅ Unit tests pass")
        else:
            results["unit_tests"] = False
            print(f"❌ Unit tests failed: {stderr}")

        return results

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report."""
        print("🔍 Validating development environment...")
        print("=" * 50)

        report = {
            "python_environment": self.check_python_environment(),
            "development_tools": self.check_development_tools(),
            "git_configuration": self.check_git_configuration(),
            "project_structure": self.check_project_structure(),
            "system_functionality": self.check_system_functionality(),
        }

        # Calculate overall score
        total_checks = 0
        passed_checks = 0

        for category, results in report.items():
            if isinstance(results, dict):
                for key, value in results.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in results[key].items():
                            total_checks += 1
                            if sub_value is True or (
                                isinstance(sub_value, str) and sub_value
                            ):
                                passed_checks += 1
                    else:
                        total_checks += 1
                        if value is True or (isinstance(value, str) and value):
                            passed_checks += 1

        report["overall_score"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "percentage": (
                (passed_checks / total_checks * 100) if total_checks > 0 else 0
            ),
        }

        return report

    def print_summary(self, report: Dict[str, Any]):
        """Print a summary of the validation results."""
        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)

        score = report["overall_score"]
        percentage = score["percentage"]

        print(
            f"Overall Score: {score['passed_checks']}/{score['total_checks']} ({percentage:.1f}%)"
        )

        if percentage >= 90:
            print("🎉 Excellent! Development environment is fully configured.")
        elif percentage >= 75:
            print("✅ Good! Development environment is mostly configured.")
        elif percentage >= 50:
            print("⚠️  Fair. Some issues need attention.")
        else:
            print("❌ Poor. Significant issues need to be resolved.")

        print("\nNext steps:")
        if percentage < 100:
            print("1. Run 'python scripts/setup_dev_env.py' to fix issues")
            print("2. Check the error messages above for specific problems")
            print("3. Re-run this validation script after fixes")
        else:
            print("1. You're ready to start developing!")
            print("2. Run 'python -m ai_onboard --help' to test the CLI")
            print("3. Check out DEVELOPMENT.md for more information")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    validator = DevEnvironmentValidator(project_root)

    try:
        report = validator.generate_report()
        validator.print_summary(report)

        # Save report to file
        import json

        report_file = project_root / ".ai_onboard" / "dev_env_report.json"
        report_file.parent.mkdir(exist_ok=True)
        report_file.write_text(json.dumps(report, indent=2))
        print(f"\n📄 Detailed report saved to: {report_file}")

        # Exit with appropriate code
        score = report["overall_score"]["percentage"]
        sys.exit(0 if score >= 75 else 1)

    except KeyboardInterrupt:
        print("\n❌ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
