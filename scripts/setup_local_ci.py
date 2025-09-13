#!/usr/bin/env python3
"""
Setup script for local CI validation tools.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def setup_pre_commit():
    """Setup pre-commit hooks with proper configuration."""
    print("🔧 Setting up pre-commit hooks...")

    # Create symlink from root to config directory
    root_config = Path(".pre-commit-config.yaml")
    config_file = Path("config/pre-commit-config.yaml")

    # Remove existing root config if it exists
    if root_config.exists():
        if root_config.is_symlink():
            root_config.unlink()
        else:
            print(f"⚠️  Moving existing {root_config} to {root_config}.backup")
            shutil.move(str(root_config), f"{root_config}.backup")

    # Create symlink to config directory
    try:
        if os.name == "nt":  # Windows
            # On Windows, create a copy instead of symlink for compatibility
            shutil.copy2(str(config_file), str(root_config))
            print(f"✅ Copied pre-commit config from {config_file} to {root_config}")
        else:  # Unix-like systems
            root_config.symlink_to(config_file)
            print(f"✅ Created symlink from {root_config} to {config_file}")
    except Exception as e:
        print(f"❌ Failed to setup pre-commit config: {e}")
        return False

    # Install pre-commit hooks
    try:
        # Try using python -m pre_commit first
        result = subprocess.run(
            [sys.executable, "-m", "pre_commit", "install"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✅ Pre-commit hooks installed successfully")
            return True
        else:
            print(f"⚠️  Pre-commit install warning: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Error with python -m pre_commit: {e}")

    # Try direct pre-commit command
    try:
        result = subprocess.run(
            ["pre-commit", "install"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✅ Pre-commit hooks installed successfully")
            return True
        else:
            print(f"⚠️  Pre-commit direct install failed: {result.stderr}")
    except FileNotFoundError:
        print("⚠️  pre-commit command not found in PATH")
    except Exception as e:
        print(f"⚠️  Error with direct pre-commit: {e}")

    # Try installing and configuring pre-commit
    try:
        print("⚠️  Installing pre-commit...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pre-commit"], check=True
        )

        # Try again with python -m
        result = subprocess.run(
            [sys.executable, "-m", "pre_commit", "install"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✅ Pre-commit installed and configured")
            return True
        else:
            print(f"⚠️  Still having issues: {result.stderr}")
            print("⚠️  Pre-commit may not be properly configured, but continuing...")
            return True  # Don't fail the entire setup

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install pre-commit: {e}")
        print("⚠️  Continuing without pre-commit hooks...")
        return True  # Don't fail the entire setup

    return True


def setup_git_hooks():
    """Setup custom git hooks."""
    print("🔧 Setting up git hooks...")

    # Create .githooks directory if it doesn't exist
    githooks_dir = Path(".githooks")
    githooks_dir.mkdir(exist_ok=True)

    # Create pre-push hook
    pre_push_hook = githooks_dir / "pre-push"
    pre_push_content = """#!/bin/sh
# Pre-push hook that runs local CI validation

echo "🚀 Running local CI validation before push..."

# Run local CI validation
python scripts/local_ci_validation.py --no-fast-fail

if [ $? -ne 0 ]; then
    echo "❌ Local CI validation failed!"
    echo "   Fix issues before pushing or use --no-verify to bypass"
    exit 1
fi

echo "✅ Local CI validation passed!"
exit 0
"""

    with open(pre_push_hook, "w", encoding="utf-8") as f:
        f.write(pre_push_content)

    # Make executable on Unix-like systems
    if os.name != "nt":
        pre_push_hook.chmod(0o755)

    print(f"✅ Created pre-push hook at {pre_push_hook}")

    # Configure git to use .githooks
    try:
        subprocess.run(
            ["git", "config", "core.hooksPath", ".githooks"],
            check=True,
            capture_output=True,
        )
        print("✅ Configured git to use .githooks directory")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Failed to configure git hooks: {e}")
        print("   You can manually run: git config core.hooksPath .githooks")

    return True


def create_makefile():
    """Create a Makefile for common development tasks."""
    print("🔧 Creating development Makefile...")

    makefile_content = """# AI Onboard Development Makefile

.PHONY: help install dev-install test lint format security ci-local clean

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \\033[36m%-15s\\033[0m %s\\n", $$1, $$2}'

install:  ## Install package dependencies
	pip install -e .

dev-install:  ## Install development dependencies
	pip install -e .[dev]
	python scripts/setup_local_ci.py

test:  ## Run all tests
	python -m pytest tests/ -v

test-unit:  ## Run unit tests only
	python -m pytest tests/unit/ -v

test-integration:  ## Run integration tests only
	python -m pytest tests/integration/ -v

test-smoke:  ## Run smoke tests only
	python -m pytest tests/smoke/ -v

lint:  ## Run linting checks
	python -m flake8 ai_onboard/ tests/ scripts/
	python -m mypy --config-file=config/mypy.ini ai_onboard/

format:  ## Format code
	python -m black ai_onboard/ tests/ scripts/
	python -m isort ai_onboard/ tests/ scripts/

format-check:  ## Check code formatting
	python -m black --check ai_onboard/ tests/ scripts/
	python -m isort --check-only ai_onboard/ tests/ scripts/

security:  ## Run security checks
	python -m bandit -r ai_onboard/
	python -m safety check

ci-local:  ## Run full local CI validation
	python scripts/local_ci_validation.py

ci-fast:  ## Run fast local CI validation
	python scripts/local_ci_validation.py --step quality

validate-env:  ## Validate development environment
	python scripts/validate_dev_env.py

validate-structure:  ## Validate project structure
	python scripts/validate_project_structure.py

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

pre-commit-run:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

pre-commit-update:  ## Update pre-commit hooks
	pre-commit autoupdate
"""

    makefile_path = Path("Makefile")
    with open(makefile_path, "w", encoding="utf-8") as f:
        f.write(makefile_content)

    print(f"✅ Created {makefile_path}")
    return True


def main():
    """Main setup function."""
    print("🚀 Setting up Local CI Validation")
    print("=" * 50)

    success = True

    # Setup pre-commit
    if not setup_pre_commit():
        success = False

    # Setup git hooks
    if not setup_git_hooks():
        success = False

    # Create Makefile
    if not create_makefile():
        success = False

    if success:
        print("\n🎉 Local CI setup completed successfully!")
        print("\nNext steps:")
        print("  1. Run 'make ci-local' to validate your environment")
        print("  2. Use 'make format' to format your code")
        print("  3. Use 'make test' to run tests")
        print("  4. Git hooks will automatically run validation on push")
    else:
        print("\n💥 Some setup steps failed. Please check the output above.")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
