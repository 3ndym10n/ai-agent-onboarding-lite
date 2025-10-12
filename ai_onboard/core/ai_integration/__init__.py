"""
AI Integration components for AI Onboard.

This module contains AI agent collaboration, Cursor AI integration,
decision pipelines, user experience systems, and AI-related utilities.
"""

# Explicit imports to avoid F403/F405 linter errors
# Handle ConversationContext naming conflict by importing with alias
from .advanced_agent_decision_pipeline import (
    AdvancedDecisionPipeline,
    get_advanced_decision_pipeline,
)
from .agent_auto_gate import auto_handle_gates, handle_gate_now, submit_gate_response
from .agent_gate_detector import AIAgentGateDetector
from .ai_agent_collaboration_protocol import (
    AIAgentCollaborationProtocol,
    AgentCapability,
    AgentProfile,
    CollaborationMode,
    SafetyLevel,
    get_collaboration_protocol,
)
from .ai_agent_guidance import AIAgentGuidanceSystem, get_ai_agent_guidance_system
from .ai_agent_wrapper import AIAgentIASWrapper, create_ai_agent_wrapper
from .cursor_ai_integration import CursorAIIntegration, get_cursor_integration
from .enhanced_conversation_context import (
    EnhancedConversationContextManager,
    get_enhanced_context_manager,
)
from .intelligent_development_monitor import (
    IntelligentDevelopmentMonitor,
    get_development_monitor,
)
from .kaizen_automation import KaizenAutomationEngine, get_kaizen_automation
from .user_experience_system import UserExperienceSystem, get_user_experience_system
from .user_preference_learning import (
    UserPreferenceLearningSystem,
    get_user_preference_learning_system,
)
from .natural_language_intent_parser import (
    NaturalLanguageIntentParser,
    get_natural_language_intent_parser,
)
from .conversation_memory_system import (
    ConversationMemoryManager,
    get_conversation_memory_manager,
)
from .progressive_disclosure_ui import (
    ProgressiveDisclosureEngine,
    get_progressive_disclosure_engine,
)
from .clarification_question_system import (
    ClarificationQuestionEngine,
    get_clarification_question_engine,
)
from .user_journey_mapper import UserJourneyMapper, get_user_journey_mapper
from .prompt_based_intent_parser import (
    PromptBasedIntentParser,
    get_prompt_based_intent_parser,
)
from .prompt_based_journey_mapper import (
    PromptBasedJourneyMapper,
    get_prompt_based_journey_mapper,
)
from .ai_gate_mediator import AIGateMediator, get_ai_gate_mediator
from .agent_adapter import AIOnboardAgentAdapter
from .decision_enforcer import (
    DecisionEnforcer,
    DecisionPoint,
    get_decision_enforcer,
    register_common_decisions,
    require_decision,
    COMMON_DECISIONS,
)

__all__ = [
    # AI Agent Systems
    "AIAgentCollaborationProtocol",
    "AIAgentIASWrapper",
    "AIAgentGateDetector",
    "AgentCapability",
    "AgentProfile",
    "CollaborationMode",
    "SafetyLevel",
    "get_collaboration_protocol",
    "create_ai_agent_wrapper",
    # Cursor AI Integration
    "CursorAIIntegration",
    "get_cursor_integration",
    # Decision & Intelligence
    "AdvancedDecisionPipeline",
    "IntelligentDevelopmentMonitor",
    "get_advanced_decision_pipeline",
    "get_development_monitor",
    # User Experience
    "UserExperienceSystem",
    "get_user_experience_system",
    # Learning & Context
    "UserPreferenceLearningSystem",
    "EnhancedConversationContextManager",
    "NaturalLanguageIntentParser",
    "ConversationMemoryManager",
    "ProgressiveDisclosureEngine",
    "ClarificationQuestionEngine",
    "UserJourneyMapper",
    "PromptBasedIntentParser",
    "PromptBasedJourneyMapper",
    "get_user_preference_learning_system",
    "get_enhanced_context_manager",
    "get_natural_language_intent_parser",
    "get_conversation_memory_manager",
    "get_progressive_disclosure_engine",
    "get_clarification_question_engine",
    "get_user_journey_mapper",
    "get_prompt_based_intent_parser",
    "get_prompt_based_journey_mapper",
    # Continuous Improvement
    "KaizenAutomationEngine",
    "get_kaizen_automation",
    # Guidance
    "AIAgentGuidanceSystem",
    "get_ai_agent_guidance_system",
    # Gate Mediation
    "AIGateMediator",
    "get_ai_gate_mediator",
    # Gate utilities
    "auto_handle_gates",
    "handle_gate_now",
    "submit_gate_response",
    # Decision Enforcement
    "DecisionEnforcer",
    "DecisionPoint",
    "get_decision_enforcer",
    "register_common_decisions",
    "require_decision",
    "COMMON_DECISIONS",
    "AIOnboardAgentAdapter",
]
