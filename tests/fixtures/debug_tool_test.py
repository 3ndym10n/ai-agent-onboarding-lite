#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, ".")

from ai_onboard.core.mandatory_tool_consultation_gate import get_mandatory_gate
from ai_onboard.core.unified_tool_orchestrator import UnifiedToolOrchestrator

root_path = Path(".")
orchestrator = UnifiedToolOrchestrator(root_path)
consultation_gate = get_mandatory_gate(root_path)

# Test just dependency_mapper
tool_name = "dependency_mapper"
print(f"Testing {tool_name}...")

result = orchestrator._execute_tool_safely(tool_name, {"test_mode": True})
print(f'Executed: {result["executed"]}')

if result["executed"]:
    print("Results type:", type(result["results"]))
    if hasattr(result["results"], "circular_dependencies"):
        print(
            f'Has circular_dependencies: {len(result["results"].circular_dependencies)}'
        )
    if hasattr(result["results"], "modules_analyzed"):
        print(f'Modules analyzed: {result["results"].modules_analyzed}')

    insights = consultation_gate._extract_tool_insights(tool_name, result["results"])
    print(f"Insights: {insights}")
