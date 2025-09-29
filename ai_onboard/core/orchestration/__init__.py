"""
Orchestration components for AI Onboard.

This module contains tool orchestration, discovery, execution management,
safety gates, and error prevention systems.
"""

# Import specific classes to avoid conflicts
from .automatic_error_prevention import AutomaticErrorPrevention
from .comprehensive_tool_discovery import ComprehensiveToolDiscovery
from .mandatory_tool_consultation_gate import MandatoryToolConsultationGate
from .orchestration_compatibility import AIAgentOrchestrationLayer
from .pattern_recognition_system import PatternRecognitionSystem
from .task_execution_gate import TaskExecutionGate
from .task_integration_logic import TaskIntegrationLogic
from .tool_usage_tracker import ToolUsageTracker, get_tool_tracker
from .unified_tool_orchestrator import (
    UnifiedToolOrchestrator,
    get_unified_tool_orchestrator,
)
from .universal_error_monitor import UniversalErrorMonitor

__all__ = [
    # Tool Orchestration
    "UnifiedToolOrchestrator",
    "get_unified_tool_orchestrator",
    # Tool Discovery
    "ComprehensiveToolDiscovery",
    # Safety & Gates
    "MandatoryToolConsultationGate",
    "TaskExecutionGate",
    # Error Prevention
    "AutomaticErrorPrevention",
    "UniversalErrorMonitor",
    # Pattern Recognition
    "PatternRecognitionSystem",
    # Compatibility
    "AIAgentOrchestrationLayer",
    # Tool Tracking
    "ToolUsageTracker",
    "get_tool_tracker",
    # Task Integration
    "TaskIntegrationLogic",
]
