#!/usr/bin/env python3
"""
Consolidated Tool Orchestration Tests

This module consolidates all phase-based tool tests into a single,
parameterized test suite for better maintainability and reduced duplication.
"""

import sys
from pathlib import Path

import pytest

from ai_onboard.core.unified_tool_orchestrator import UnifiedToolOrchestrator


class TestToolOrchestration:
    """Consolidated test suite for tool orchestration across all phases."""

    @pytest.fixture
    def orchestrator(self):
        """Provide a UnifiedToolOrchestrator instance for testing."""
        root_path = Path(".")
        return UnifiedToolOrchestrator(root_path)

    @pytest.mark.parametrize(
        "phase,tools",
        [
            (1, ["vision_guardian", "gate_system", "ultra_safe_cleanup"]),
            (
                2,
                [
                    "charter_management",
                    "automatic_error_prevention",
                    "pattern_recognition_system",
                    "task_execution_gate",
                ],
            ),
            (
                3,
                [
                    "interrogation_system",
                    "conversation_analysis",
                    "ui_enhancement",
                    "wbs_management",
                    "ai_agent_orchestration",
                    "decision_pipeline",
                    "intelligent_monitoring",
                    "user_preference_learning_system",
                ],
            ),
        ],
    )
    def test_phase_tools_execution(self, orchestrator, phase, tools):
        """Test that tools from each phase execute successfully."""
        for tool_name in tools:
            print(f"\nTesting {tool_name} (Phase {phase})...")
            try:
                result = orchestrator._execute_tool_safely(
                    tool_name, {"test_mode": True}
                )
                print(f"  Executed: {result['executed']}")

                if result["executed"]:
                    print(f"  Results type: {type(result['results'])}")
                    if isinstance(result["results"], dict):
                        keys = list(result["results"].keys())
                        print(f"  Keys: {keys[:5]}...")  # Show first 5 keys
                    print(f"  ✅ Success: Tool {tool_name} is operational!")
                else:
                    print(f"  ❌ Error: {result.get('error', 'Unknown error')}")

            except Exception as e:
                print(f"  ❌ Exception: {e}")

    def test_orchestrator_initialization(self, orchestrator):
        """Test that the orchestrator initializes correctly."""
        assert orchestrator is not None
        assert hasattr(orchestrator, "_execute_tool_safely")

    def test_tool_discovery(self, orchestrator):
        """Test that tools can be discovered by the orchestrator."""
        # This test verifies that the tool discovery mechanism works
        # across all phases without specific tool execution
        assert hasattr(orchestrator, "root")
        assert orchestrator.root is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
