#!/usr / bin / env python3
"""
Development Environment Setup Script for ai - onboard

This script sets up a complete development environment including:
- Python virtual environment
- Development dependencies
- Pre - commit hooks
- Git configuration
- IDE configuration files
"""
from ai_onboard.core.common_imports import json, sys

import platform
import subprocess
from pathlib import Path
from typing import List

# mypy: ignore - errors


class DevEnvironmentSetup:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.venv_path = project_root / "venv"
        self.python_exe = sys.executable
        self.is_windows = platform.system() == "Windows"

    def run_command(
        self, cmd: List[str], cwd: Path = None
    ) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        if cwd is None:
            cwd = self.project_root

        print(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd, cwd=cwd, capture_output=True, text=True, check=True
            )
            print(f"✅ Success: {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e.stderr.strip()}")
            raise

    def check_prerequisites(self) -> bool:
        """Check if required tools are installed."""
        print("🔍 Checking prerequisites...")

        required_tools = {
            "python": ["python", "--version"],
            "git": ["git", "--version"],
            "pip": ["pip", "--version"],
        }

        missing_tools = []
        for tool, cmd in required_tools.items():
            try:
                self.run_command(cmd)
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing_tools.append(tool)

        if missing_tools:
            print(f"❌ Missing required tools: {', '.join(missing_tools)}")
            return False

        print("✅ All prerequisites met")
        return True

    def create_virtual_environment(self) -> bool:
        """Create a Python virtual environment."""
        print("🐍 Creating virtual environment...")

        if self.venv_path.exists():
            print("✅ Virtual environment already exists")
            return True

        try:
            self.run_command([self.python_exe, "-m", "venv", str(self.venv_path)])
            print("✅ Virtual environment created")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to create virtual environment")
            return False

    def get_venv_python(self) -> str:
        """Get the path to the virtual environment Python executable."""
        if self.is_windows:
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")

    def get_venv_pip(self) -> str:
        """Get the path to the virtual environment pip executable."""
        if self.is_windows:
            return str(self.venv_path / "Scripts" / "pip.exe")
        else:
            return str(self.venv_path / "bin" / "pip")

    def install_dependencies(self) -> bool:
        """Install project dependencies."""
        print("📦 Installing dependencies...")

        venv_pip = self.get_venv_pip()

        try:
            # Upgrade pip first (ignore errors)
            try:
                self.run_command([venv_pip, "install", "--upgrade", "pip"])
            except subprocess.CalledProcessError:
                print("⚠️  Pip upgrade failed, continuing...")

            # Install project in development mode
            self.run_command([venv_pip, "install", "-e", "."])

            # Install development dependencies
            self.run_command([venv_pip, "install", "-e", ".[dev]"])

            # Install additional development tools
            dev_tools = [
                "pre - commit >= 3.0.0",
                "isort >= 5.12.0",
                "flake8 - docstrings >= 1.7.0",
                "types - PyYAML >= 6.0.0",
            ]

            for tool in dev_tools:
                try:
                    self.run_command([venv_pip, "install", tool])
                except subprocess.CalledProcessError:
                    print(f"⚠️  Failed to install {tool}, continuing...")

            print("✅ Dependencies installed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

    def setup_pre_commit_hooks(self) -> bool:
        """Set up pre - commit hooks."""
        print("🪝 Setting up pre - commit hooks...")

        venv_python = self.get_venv_python()

        try:
            # Install pre - commit hooks
            self.run_command([venv_python, "-m", "pre_commit", "install"])
            print("✅ Pre - commit hooks installed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to set up pre - commit hooks")
            return False

    def setup_git_config(self) -> bool:
        """Set up Git configuration for the project."""
        print("🔧 Setting up Git configuration...")

        try:
            # Set up protected paths hook
            githooks_dir = self.project_root / ".githooks"
            githooks_dir.mkdir(exist_ok=True)

            # Create pre - push hook
            pre_push_hook = githooks_dir / "pre - push"
            pre_push_content = """#!/bin / bash
# Pre - push hook to check protected paths
python scripts / protected_paths_diff.py
"""
            pre_push_hook.write_text(pre_push_content)
            pre_push_hook.chmod(0o755)

            # Configure Git to use our hooks
            self.run_command(["git", "config", "core.hooksPath", ".githooks"])

            print("✅ Git configuration set up")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to set up Git configuration")
            return False

    def create_ide_configs(self) -> bool:
        """Create IDE configuration files."""
        print("💻 Creating IDE configuration files...")

        try:
            # VS Code settings
            vscode_dir = self.project_root / ".vscode"
            vscode_dir.mkdir(exist_ok=True)

            vscode_settings = {
                "python.defaultInterpreterPath": (
                    "./venv / Scripts / python.exe"
                    if self.is_windows
                    else "./venv / bin / python"
                ),
                "python.linting.enabled": True,
                "python.linting.flake8Enabled": True,
                "python.linting.mypyEnabled": True,
                "python.formatting.provider": "black",
                "python.sortImports.args": ["--profile", "black"],
                "editor.formatOnSave": True,
                "editor.codeActionsOnSave": {"source.organizeImports": True},
                "files.exclude": {
                    "**/__pycache__": True,
                    "**/*.pyc": True,
                    ".ai_onboard/": True,
                    "venv/": True,
                },
            }


            (vscode_dir / "settings.json").write_text(
                json.dumps(vscode_settings, indent=2)
            )

            # PyCharm configuration
            idea_dir = self.project_root / ".idea"
            if not idea_dir.exists():
                idea_dir.mkdir(exist_ok=True)
                (idea_dir / "misc.xml").write_text(
                    """<?xml version="1.0" encoding="UTF - 8"?>
<project version="4">
  <component name="ProjectRootManager" version="2" project - jdk - name="Python 3.8" project - jdk - type="Python SDK" />
</project>"""
                )

            print("✅ IDE configuration files created")
            return True
        except Exception as e:
            print(f"❌ Failed to create IDE configs: {e}")
            return False

    def run_initial_tests(self) -> bool:
        """Run initial tests to verify setup."""
        print("🧪 Running initial tests...")

        venv_python = self.get_venv_python()

        try:
            # Run system tests
            self.run_command([venv_python, "scripts / test_system.py"])

            # Run smoke tests
            self.run_command([venv_python, "-m", "pytest", "tests/", "-v"])

            print("✅ Initial tests passed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Initial tests failed")
            return False

    def setup_development_environment(self) -> bool:
        """Set up the complete development environment."""
        print("🚀 Setting up development environment for ai - onboard...")
        print(f"Project root: {self.project_root}")

        steps = [
            ("Check prerequisites", self.check_prerequisites),
            ("Create virtual environment", self.create_virtual_environment),
            ("Install dependencies", self.install_dependencies),
            ("Set up pre - commit hooks", self.setup_pre_commit_hooks),
            ("Set up Git configuration", self.setup_git_config),
            ("Create IDE configurations", self.create_ide_configs),
            ("Run initial tests", self.run_initial_tests),
        ]

        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"❌ Setup failed at: {step_name}")
                return False

        print("\n🎉 Development environment setup complete!")
        print("\nNext steps:")
        print("1. Activate the virtual environment:")
        if self.is_windows:
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv / bin / activate")
        print("2. Run 'python -m ai_onboard --help' to test the CLI")
        print("3. Run 'python scripts / test_system.py' to verify everything works")

        return True


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    setup = DevEnvironmentSetup(project_root)

    try:
        success = setup.setup_development_environment()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
