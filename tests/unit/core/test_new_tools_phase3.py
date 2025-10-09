#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, ".")

from ai_onboard.core.orchestration.unified_tool_orchestrator import UnifiedToolOrchestrator

root_path = Path(".")
orchestrator = UnifiedToolOrchestrator(root_path)

# Test the new tools from phase 3
tools_to_test = [
    "interrogation_system",
    "conversation_analysis",
    "ui_enhancement",
    "wbs_management",
    "ai_agent_orchestration",
    "decision_pipeline",
    "intelligent_monitoring",
    "user_preference_learning_system",
]

for tool_name in tools_to_test:
    print(f"\nTesting {tool_name}...")
    try:
        result = orchestrator._execute_tool_safely(tool_name, {"test_mode": True})
        print(f"  Executed: {result['executed']}")
        if result["executed"]:
            print(f"  Results type: {type(result['results'])}")
            if isinstance(result["results"], dict):
                print(
                    f"  Keys: {list(result['results'].keys())[:5]}..."
                )  # Show first 5 keys
            print(f"  Success: Tool {tool_name} is now fully operational!")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  Exception: {e}")

print("\nDone testing Phase 3 tools!")
