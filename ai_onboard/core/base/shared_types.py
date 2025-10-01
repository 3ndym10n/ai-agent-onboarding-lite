"""
Shared Type Definitions - Common types used across the AI Onboard system.

This module consolidates commonly used type definitions to avoid duplication
and ensure consistency across the codebase.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class UserExpertiseLevel(Enum):
    """User expertise levels for adaptive interface."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class DisclosureLevel(Enum):
    """Levels of information disclosure."""

    MINIMAL = "minimal"  # Show only essentials
    BASIC = "basic"  # Show common options
    INTERMEDIATE = "intermediate"  # Show most options
    ADVANCED = "advanced"  # Show all options
    EXPERT = "expert"  # Show advanced + technical details


class UIComplexityLevel(Enum):
    """Complexity levels for UI elements."""

    SIMPLE = "simple"  # Single-click actions
    MODERATE = "moderate"  # Some configuration needed
    COMPLEX = "complex"  # Multiple steps/configuration
    TECHNICAL = "technical"  # Requires technical knowledge


class QuestionType(Enum):
    """Types of clarification questions."""

    CLARIFYING = "clarifying"  # Basic clarification
    SPECIFYING = "specifying"  # More specific details
    VALIDATING = "validating"  # Confirm understanding
    EXPLORING = "exploring"  # Discover new requirements
    PRIORITIZING = "prioritizing"  # Rank importance


class QuestionComplexity(Enum):
    """Complexity levels for questions."""

    SIMPLE = "simple"  # Yes/no or single choice
    MODERATE = "moderate"  # Short answer required
    COMPLEX = "complex"  # Multiple aspects to consider
    TECHNICAL = "technical"  # Requires technical knowledge


class JourneyStage(Enum):
    """Stages in a typical development journey."""

    DISCOVERY = "discovery"  # Understanding user needs
    PLANNING = "planning"  # Creating project plan
    SETUP = "setup"  # Initial setup and configuration
    DEVELOPMENT = "development"  # Building the application
    TESTING = "testing"  # Testing and validation
    DEPLOYMENT = "deployment"  # Launching the application
    MAINTENANCE = "maintenance"  # Ongoing maintenance


class StepComplexity(Enum):
    """Complexity levels for journey steps."""

    TRIVIAL = "trivial"  # 1-2 minutes, obvious action
    SIMPLE = "simple"  # 5-10 minutes, clear instructions
    MODERATE = "moderate"  # 15-30 minutes, some decisions needed
    COMPLEX = "complex"  # 30+ minutes, multiple sub-steps
    TECHNICAL = "technical"  # Requires technical knowledge


@dataclass
class UserProfile:
    """User profile information."""

    user_id: str
    experience_level: UserExpertiseLevel = UserExpertiseLevel.INTERMEDIATE
    preferences: Dict[str, Any] = field(default_factory=dict)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: str(Path.cwd()))
    last_updated: str = field(default_factory=lambda: str(Path.cwd()))


@dataclass
class ConversationContext:
    """Conversation context with memory management."""

    conversation_id: str
    user_id: str
    session_id: str
    created_at: float
    last_updated: float

    # Core conversation state
    current_topic: str = "initial_request"
    conversation_stage: str = "discovery"  # discovery, planning, implementation, review
    user_intent_summary: str = ""
    project_context: Dict[str, Any] = field(default_factory=dict)

    # Memory management
    memory_segments: List[Any] = field(default_factory=list)
    active_memory_window: List[str] = field(default_factory=list)
    critical_memory_items: List[str] = field(default_factory=list)

    # Performance tracking
    message_count: int = 0
    context_switches: int = 0
    memory_accesses: int = 0


@dataclass
class ValidationResult:
    """Result of validation operations."""

    success: bool
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class RiskLevel:
    """Risk assessment levels."""

    level: str  # low, medium, high
    score: float  # 0.0-1.0
    factors: List[str] = field(default_factory=list)
    mitigation: List[str] = field(default_factory=list)


@dataclass
class CleanupOperation:
    """Details of a cleanup operation."""

    operation_id: str
    operation_type: str
    target_path: str
    reason: str
    risk_level: str
    estimated_impact: str
    prerequisites: List[str] = field(default_factory=list)
    rollback_plan: str = ""


@dataclass
class CommandInfo:
    """Information about a CLI command."""

    name: str
    category: str
    description: str
    usage_example: str
    expertise_level: UserExpertiseLevel = UserExpertiseLevel.BEGINNER
    tags: List[str] = field(default_factory=list)
    related_commands: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class SmartSuggestion:
    """A contextual suggestion for the user."""

    command: str
    reason: str
    confidence: float
    category: str
    next_steps: List[str] = field(default_factory=list)


@dataclass
class DesignValidation:
    """Design validation result."""

    score: float  # 0.0-1.0
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    accessibility_score: float = 0.0
    consistency_score: float = 0.0


@dataclass
class UIElement:
    """Represents a UI element with complexity metadata."""

    element_id: str
    display_name: str
    description: str
    complexity_level: UIComplexityLevel
    expertise_required: UserExpertiseLevel
    category: str

    # Progressive disclosure settings
    default_visibility: bool = True
    can_be_hidden: bool = True
    requires_confirmation: bool = False

    # Dependencies
    prerequisite_elements: List[str] = field(default_factory=list)
    conflicting_elements: List[str] = field(default_factory=list)

    # Metadata
    usage_frequency: float = 0.0
    user_satisfaction: float = 0.5


@dataclass
class ClarificationQuestion:
    """A clarification question with metadata."""

    question_id: str
    question_text: str
    question_type: QuestionType
    complexity: QuestionComplexity
    category: str

    # Context and relevance
    context_keywords: List[str] = field(default_factory=list)
    required_for_understanding: bool = False
    prerequisite_questions: List[str] = field(default_factory=list)

    # User experience
    user_friendly_alternatives: List[str] = field(default_factory=list)
    expected_answer_format: str = "text"  # text, choice, number, boolean
    suggested_answers: List[str] = field(default_factory=list)

    # Priority and timing
    priority_score: float = 0.5
    ask_early: bool = False
    ask_only_if_confused: bool = False

    # Usage tracking
    times_asked: int = 0
    times_answered: int = 0
    average_response_quality: float = 0.5


@dataclass
class JourneyStep:
    """A single step in a user journey."""

    step_id: str
    title: str
    description: str
    complexity: StepComplexity
    estimated_time_minutes: int

    # Journey flow
    stage: JourneyStage
    order: int
    prerequisites: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)

    # User experience
    beginner_friendly: bool = True
    requires_clarification: bool = False
    can_be_skipped: bool = False

    # Help and guidance
    help_text: str = ""
    common_mistakes: List[str] = field(default_factory=list)
    success_indicators: List[str] = field(default_factory=list)

    # Progress tracking
    completion_criteria: List[str] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)


@dataclass
class MemorySegment:
    """A segment of conversation memory with importance scoring."""

    segment_id: str
    session_id: str
    user_id: str
    timestamp: float
    start_message_index: int
    end_message_index: int

    # Memory content
    key_topics: List[str] = field(default_factory=list)
    important_facts: List[str] = field(default_factory=list)
    decisions_made: List[str] = field(default_factory=list)
    user_preferences_expressed: Dict[str, Any] = field(default_factory=dict)

    # Importance metrics
    importance_score: float = 0.5
    relevance_to_current_context: float = 0.5
    access_count: int = 0
    last_accessed: float = 0.0

    # Retention policy
    retention_priority: str = "normal"  # low, normal, high, critical
    expires_at: Optional[float] = None


# Export all types for easy importing
__all__ = [
    # Enums
    "UserExpertiseLevel",
    "DisclosureLevel",
    "UIComplexityLevel",
    "QuestionType",
    "QuestionComplexity",
    "JourneyStage",
    "StepComplexity",
    # Dataclasses
    "UserProfile",
    "ConversationContext",
    "ValidationResult",
    "RiskLevel",
    "CleanupOperation",
    "CommandInfo",
    "SmartSuggestion",
    "DesignValidation",
    "UIElement",
    "ClarificationQuestion",
    "JourneyStep",
    "MemorySegment",
]
