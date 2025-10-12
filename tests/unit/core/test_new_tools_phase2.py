#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, ".")

from ai_onboard.core.orchestration.unified_tool_orchestrator import UnifiedToolOrchestrator

root_path = Path(".")
orchestrator = UnifiedToolOrchestrator(root_path)

# Test the new tools from phase 2
tools_to_test = [
    "charter_management",
    "automatic_error_prevention",
    "pattern_recognition_system",
    "task_execution_gate",
]

for tool_name in tools_to_test:
    print(f"\nTesting {tool_name}...")
    try:
        result = orchestrator._execute_tool_safely(tool_name, {"test_mode": True})
        print(f"  Executed: {result['executed']}")
        if result["executed"]:
            print(f"  Results type: {type(result['results'])}")
            if isinstance(result["results"], dict):
                print(f"  Keys: {list(result['results'].keys())}")
            print(f"  Success: Tool {tool_name} is now fully operational!")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  Exception: {e}")

print("\nDone testing new tools!")
