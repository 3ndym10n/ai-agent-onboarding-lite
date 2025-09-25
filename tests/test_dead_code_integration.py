#!/usr/bin/env python3
"""Test dead code validation integration."""

from pathlib import Path

from ai_onboard.core.orchestration_compatibility import get_intelligent_orchestrator


def test_dead_code_validation():
    """Test that dead code validation can be executed through the orchestrator."""
    print("Testing dead code validation integration...")

    orchestrator = get_intelligent_orchestrator(Path("."))
    result = orchestrator.execute_automatic_tool_application("dead_code_validation", {})

    print(f"Executed: {result.get('executed', False)}")
    if result.get("executed"):
        print("✅ Tool executed successfully")
        results = result.get("results", {})
        print(f"Return code: {results.get('returncode')}")
        print("STDOUT:")
        print(results.get("stdout", ""))
        print("STDERR:")
        print(results.get("stderr", ""))
        if results.get("success"):
            print("✅ Validation completed successfully")
        else:
            print("❌ Validation failed")
    else:
        print(f"❌ Execution failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    test_dead_code_validation()
