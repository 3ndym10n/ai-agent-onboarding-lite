"""
AI Agent Onboarding System - Drop-in project coach for AI-assisted development.

This package provides charter + plan + align + validate + kaizen capabilities
for AI-assisted development governance and validation.
"""

__version__ = "0.2.0"

# Import key components for easy access
from .core import (
    AgentCapability,
    AgentProfile,
    CollaborationMode,
    ContinuousImprovementValidator,
    CursorAIIntegration,
    SafetyLevel,
    ValidationCategory,
    ValidationReport,
    ValidationResult,
    ValidationTestCase,
    get_cursor_integration,
)

__all__ = [
    # Core functionality
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
    # Version
    "__version__",
]

