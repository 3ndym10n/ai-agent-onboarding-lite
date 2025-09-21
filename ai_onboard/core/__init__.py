# Core modules for ai-onboard

# Essential core modules
from . import (
    # Planning and project management
    charter,
    planning,
    dynamic_planner,
    progress_utils,
    # Validation and testing
    continuous_improvement_validator,
    # AI agent collaboration
    ai_agent_collaboration_protocol,
    cursor_ai_integration,
    # System utilities
    utils,
    state,
    telemetry,
    # Vision and alignment
    vision_interrogator,
    vision_guardian,
    alignment,
    # Safety and cleanup
    cleanup_safety_gates,
    # Context and debugging
    smart_debugger,
)

# Export commonly used classes and functions
from .continuous_improvement_validator import (
    ContinuousImprovementValidator,
    ValidationResult,
    ValidationCategory,
    ValidationTestCase,
    ValidationReport,
)

from .ai_agent_collaboration_protocol import (
    AgentProfile,
    AgentCapability,
    CollaborationMode,
    SafetyLevel,
)

from .cursor_ai_integration import (
    CursorAIIntegration,
    get_cursor_integration,
)

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
