"""
AI Integration components for AI Onboard.

This module contains AI agent collaboration, Cursor AI integration,
decision pipelines, user experience systems, and AI-related utilities.
"""

from .advanced_agent_decision_pipeline import *
from .agent_auto_gate import *
from .agent_gate_detector import *
from .ai_agent_collaboration_protocol import *
from .ai_agent_guidance import *
from .ai_agent_wrapper import *
from .cursor_ai_integration import *
from .enhanced_conversation_context import *
from .intelligent_development_monitor import *
from .kaizen_automation import *
from .user_experience_system import *
from .user_preference_learning import *
from .natural_language_intent_parser import *
from .conversation_memory_system import *
from .progressive_disclosure_ui import *
from .clarification_question_system import *
from .user_journey_mapper import *
from .prompt_based_intent_parser import *
from .prompt_based_journey_mapper import *

__all__ = [
    # AI Agent Systems
    "AIAgentCollaborationProtocol",
    "AIAgentWrapper",
    "AgentGateDetector",
    "AgentAutoGate",
    # Cursor AI Integration
    "CursorAIIntegration",
    "get_cursor_ai_integration",
    # Decision & Intelligence
    "AdvancedAgentDecisionPipeline",
    "IntelligentDevelopmentMonitor",
    "setup_intelligent_monitoring",
    # User Experience
    "UserExperienceSystem",
    "get_user_experience_system",
    # Learning & Context
    "UserPreferenceLearningSystem",
    "EnhancedConversationContext",
    "get_enhanced_context_manager",
    "NaturalLanguageIntentParser",
    "get_natural_language_intent_parser",
    "ConversationMemoryManager",
    "get_conversation_memory_manager",
    "ProgressiveDisclosureEngine",
    "get_progressive_disclosure_engine",
    "ClarificationQuestionEngine",
    "get_clarification_question_engine",
    "UserJourneyMapper",
    "get_user_journey_mapper",
    "PromptBasedIntentParser",
    "get_prompt_based_intent_parser",
    "PromptBasedJourneyMapper",
    "get_prompt_based_journey_mapper",
    # Continuous Improvement
    "KaizenAutomation",
    "get_kaizen_automation",
    # Guidance
    "AIAgentGuidance",
]
