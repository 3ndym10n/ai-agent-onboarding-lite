# Core modules for ai-onboard

# Import base infrastructure first (needed by other modules)
from .base import utils

# Essential core modules
# Import AI integration systems
from .ai_integration import (
    AgentCapability,
    AgentProfile,
    CollaborationMode,
    CursorAIIntegration,
    SafetyLevel,
)
from .ai_integration.cursor_ai_integration import (
    CursorAIIntegration,
    get_cursor_integration,
)

# Import continuous improvement systems

# Export commonly used classes and functions
from .continuous_improvement.continuous_improvement_validator import (
    ContinuousImprovementValidator,
    ValidationCategory,
    ValidationReport,
    ValidationResult,
    ValidationTestCase,
)

# Import legacy cleanup systems

# Import monitoring and analytics systems

# Import orchestration systems

# Import project management systems

# Import quality and safety systems

# Import vision systems

# compatibility shim exports preserved for legacy CLI imports
# progress_dashboard removed - was deprecated shim

__all__ = [
    # Base utilities
    "utils",
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
