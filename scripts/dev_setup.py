#!/usr/bin/env python3
"""
Development setup script for ai-onboard.
Sets up development environment and runs initial checks.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False


def main():
    """Set up development environment."""
    print("🚀 Setting up ai-onboard development environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install development dependencies
    success = True
    success &= run_command("pip install -e .[dev]", "Installing development dependencies")
    
    # Run linting
    success &= run_command("python -m flake8 ai_onboard/", "Running code linting")
    
    # Run type checking
    success &= run_command("python -m mypy ai_onboard/", "Running type checking")
    
    # Run tests
    success &= run_command("python -m pytest tests/ -v", "Running tests")
    
    # Test the CLI
    success &= run_command("python -m ai_onboard --help", "Testing CLI help")
    
    if success:
        print("\n🎉 Development environment setup complete!")
        print("\n📋 Next steps:")
        print("  - Run 'python -m ai_onboard analyze' to test the system")
        print("  - Check .ai_onboard/ directory for generated files")
        print("  - Review error logs in .ai_onboard/agent_errors.jsonl")
    else:
        print("\n❌ Some setup steps failed. Check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
