# Core modules for ai-onboard

# Essential core modules
from . import (
    ai_agent_collaboration_protocol,
    alignment,
    charter,
    cleanup_safety_gates,
    continuous_improvement_validator,
    cursor_ai_integration,
    dynamic_planner,
    planning,
    progress_utils,
    smart_debugger,
    state,
    telemetry,
    utils,
    vision_guardian,
    vision_interrogator,
)
from .ai_agent_collaboration_protocol import (
    AgentCapability,
    AgentProfile,
    CollaborationMode,
    SafetyLevel,
)

# Export commonly used classes and functions
from .continuous_improvement_validator import (
    ContinuousImprovementValidator,
    ValidationCategory,
    ValidationReport,
    ValidationResult,
    ValidationTestCase,
)
from .cursor_ai_integration import CursorAIIntegration, get_cursor_integration

# compatibility shim exports preserved for legacy CLI imports
from . import progress_dashboard as progress_tracker

__all__ = [
    # Validators
    "ContinuousImprovementValidator",
    "ValidationResult",
    "ValidationCategory",
    "ValidationTestCase",
    "ValidationReport",
    # AI Agent Collaboration
    "AgentProfile",
    "AgentCapability",
    "CollaborationMode",
    "SafetyLevel",
    # Cursor Integration
    "CursorAIIntegration",
    "get_cursor_integration",
]
