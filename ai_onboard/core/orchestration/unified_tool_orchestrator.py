"""
Unified Tool Orchestrator

Consolidates functionality from:
- intelligent_tool_orchestrator.py (trigger-based execution, learning)
- holistic_tool_orchestration.py (strategy-based coordination, vision alignment)
- ai_agent_orchestration.py (session management, decision pipeline)

This unified system provides comprehensive tool orchestration with safety,
vision alignment, user preferences, and intelligent automation.
"""

import logging
import os
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


def _debug_fallbacks_enabled() -> bool:
    """Return True when fallback logging is enabled via environment variable."""
    return os.environ.get("AI_ONBOARD_DEBUG_FALLBACKS", "").lower() in {
        "1",
        "true",
        "yes",
    }


def _log_fallback(component: str, fallback: str) -> None:
    """Log when a fallback implementation is selected (opt-in)."""
    if _debug_fallbacks_enabled():
        logger.info(
            "UnifiedToolOrchestrator using fallback for %s (%s)", component, fallback
        )


# Core tool imports - using try/except for optional dependencies
PatternRecognitionSystem: Optional[Any] = None
try:
    from .pattern_recognition_system import PatternRecognitionSystem
except ImportError:
    _log_fallback("pattern_recognition_system", "disabled")


# Define fallback first, then try to import the real one
def get_tool_tracker_fallback(root_path: Path) -> Any:
    """Get tool tracker - fallback implementation."""

    class MockTracker:
        def track_tool_usage(
            self,
            tool_name: str,
            metadata: Optional[Dict[str, Any]] = None,
            session_id: Optional[str] = None,
        ) -> None:
            pass

    return MockTracker()


# Try to import the real function
try:
    from .tool_usage_tracker import get_tool_tracker
except ImportError:
    _log_fallback("tool_usage_tracker", "mock")
    get_tool_tracker = get_tool_tracker_fallback  # type: ignore[assignment]

UserPreferenceLearningSystem: Optional[Any] = None
try:
    from ..ai_integration.user_preference_learning import UserPreferenceLearningSystem
except ImportError:
    _log_fallback("user_preference_learning_system", "disabled")


# Discovery and metadata - define fallback first
def get_comprehensive_tool_discovery_fallback(root_path: Any) -> Any:
    """Get comprehensive tool discovery - fallback implementation."""

    class MockDiscovery:
        pass

    return MockDiscovery()


try:
    from .comprehensive_tool_discovery import get_comprehensive_tool_discovery
except ImportError:
    _log_fallback("comprehensive_tool_discovery", "mock")
    get_comprehensive_tool_discovery = get_comprehensive_tool_discovery_fallback


# Session and context management
SessionStorageManager: Optional[Any] = None
try:
    from ..base.session_storage import SessionStorageManager
except ImportError:
    _log_fallback("session_storage_manager", "disabled")


# Enhanced context manager - define fallback first
def get_enhanced_context_manager_fallback(root_path: Any) -> Any:
    """Get enhanced context manager - fallback implementation."""

    class MockContextManager:
        pass

    return MockContextManager()


try:
    from ..ai_integration.enhanced_conversation_context import (
        get_enhanced_context_manager,
    )
except ImportError:
    _log_fallback("enhanced_conversation_context", "mock")
    get_enhanced_context_manager = get_enhanced_context_manager_fallback  # type: ignore[assignment]


# Mandatory gate - define fallback first
def get_mandatory_gate_fallback(root_path: Any) -> Any:
    """Get mandatory gate - fallback implementation."""

    class MockGate:
        pass

    return MockGate()


try:
    from .mandatory_tool_consultation_gate import get_mandatory_gate
except ImportError:
    _log_fallback("mandatory_tool_consultation_gate", "mock")
    get_mandatory_gate = get_mandatory_gate_fallback


# Safety and alignment
FileOrganizationAnalyzer: Optional[Any] = None
try:
    from ..monitoring_analytics.file_organization_analyzer import (
        FileOrganizationAnalyzer,
    )
except ImportError:
    _log_fallback("file_organization_analyzer", "disabled")

StructuralRecommendationEngine: Optional[Any] = None
try:
    from ..quality_safety.structural_recommendation_engine import (
        StructuralRecommendationEngine,
    )
except ImportError:
    _log_fallback("structural_recommendation_engine", "disabled")

RiskAssessmentFramework: Optional[Any] = None
try:
    from ..quality_safety.risk_assessment_framework import RiskAssessmentFramework
except ImportError:
    _log_fallback("risk_assessment_framework", "disabled")

DependencyMapper: Optional[Any] = None
try:
    from ..quality_safety.dependency_mapper import DependencyMapper
except ImportError:
    _log_fallback("dependency_mapper", "disabled")

DuplicateDetector: Optional[Any] = None
try:
    from ..quality_safety.duplicate_detector import DuplicateDetector
except ImportError:
    _log_fallback("duplicate_detector", "disabled")


# IASGuardrails fallback class
class IASGuardrailsFallback:
    """Fallback implementation of IASGuardrails."""

    pass


IASGuardrails: Optional[Any] = None
try:
    from ..ai_integration.ai_agent_wrapper import IASGuardrails
except ImportError:
    _log_fallback("IASGuardrails", "fallback")
    IASGuardrails = IASGuardrailsFallback


class UnifiedOrchestrationStrategy(Enum):
    """Unified orchestration strategies combining all approaches."""

    # From holistic_tool_orchestration.py
    VISION_FIRST = "vision_first"  # Check vision alignment before any tools
    USER_PREFERENCE_DRIVEN = "user_preference_driven"  # Prioritize user preferences
    SAFETY_FIRST = "safety_first"  # Apply safety gates before execution
    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"  # Use multiple tools
    ADAPTIVE = "adaptive"  # Adapt strategy based on context and user behavior

    # From intelligent_tool_orchestrator.py (trigger-based)
    TRIGGER_BASED = "trigger_based"  # Execute based on triggers
    LEARNING_DRIVEN = "learning_driven"  # Use pattern recognition and learning

    # From ai_agent_orchestration.py (session-based)
    SESSION_AWARE = "session_aware"  # Consider conversation context and history
    ROLLBACK_SAFE = "rollback_safe"  # Enable rollback capabilities


class UnifiedToolCategory(Enum):
    """Unified tool categories from all orchestration systems."""

    # Core Analysis Tools
    CODE_QUALITY = "code_quality"
    FILE_ORGANIZATION = "file_organization"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    DUPLICATE_DETECTION = "duplicate_detection"
    STRUCTURAL_RECOMMENDATIONS = "structural_recommendations"
    RISK_ASSESSMENT = "risk_assessment"

    # Vision & Alignment Tools
    VISION_ALIGNMENT = "vision_alignment"
    CHARTER_MANAGEMENT = "charter_management"
    INTERROGATION = "interrogation"
    ALIGNMENT_CHECK = "alignment_check"

    # User Experience Tools
    USER_PREFERENCES = "user_preferences"
    CONVERSATION_ANALYSIS = "conversation_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"

    # Safety & Validation Tools
    GATE_SYSTEM = "gate_system"
    SAFETY_CHECKS = "safety_checks"
    ERROR_PREVENTION = "error_prevention"

    # Session & Context Tools
    SESSION_MANAGEMENT = "session_management"
    CONTEXT_CONTINUITY = "context_continuity"
    DECISION_PIPELINE = "decision_pipeline"


@dataclass
class ToolExecutionTrigger:
    """Unified trigger system combining keyword, context, pattern, and session triggers."""

    trigger_type: str  # 'keyword', 'context', 'pattern', 'time_based', 'session_event'
    keywords: List[str] = field(default_factory=list)
    contexts: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    session_events: List[str] = field(default_factory=list)  # Session-based triggers
    priority: int = 1  # 1-5, higher = more important
    cooldown_minutes: int = 30  # Don't reapply same tool too frequently
    requires_user_confirmation: bool = False  # Gate system integration
    vision_alignment_required: bool = False  # Vision alignment check


@dataclass
class ToolExecutionContext:
    """Unified context for tool execution combining all orchestration needs."""

    # From intelligent_tool_orchestrator.py
    user_request: str = ""
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    trigger_matches: List[Dict[str, Any]] = field(default_factory=list)

    # From holistic_tool_orchestration.py
    strategy: UnifiedOrchestrationStrategy = UnifiedOrchestrationStrategy.ADAPTIVE
    vision_context: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    safety_requirements: Dict[str, Any] = field(default_factory=dict)

    # From ai_agent_orchestration.py
    session_id: Optional[str] = None
    user_id: str = "default"
    conversation_state: str = "active"
    action_type: str = "unknown"
    rollback_enabled: bool = True
    checkpoint_id: Optional[str] = None

    # Additional context for extensibility
    additional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UnifiedOrchestrationResult:
    """Unified result combining all orchestration result types."""

    # Basic execution info
    success: bool = False
    executed_tools: List[str] = field(default_factory=list)
    tool_results: Dict[str, Any] = field(default_factory=dict)
    total_execution_time: float = 0.0

    # Quality and alignment scores
    vision_alignment_score: float = 0.0
    user_preference_compliance: float = 0.0
    safety_compliance: float = 1.0  # Default to safe

    # Insights and recommendations
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Session and learning info
    session_context: Dict[str, Any] = field(default_factory=dict)
    learning_updates: List[Dict[str, Any]] = field(default_factory=list)

    # Rollback and safety info
    checkpoint_created: Optional[str] = None
    rollback_available: bool = False


class UnifiedToolOrchestrator:
    """
    Unified Tool Orchestrator - Consolidates all orchestration functionality.

    This class combines the best features from:
    - IntelligentToolOrchestrator: Trigger-based execution, learning, pattern recognition
    - HolisticToolOrchestrator: Strategy-based coordination, vision alignment
    - AIAgentOrchestrationLayer: Session management, decision pipeline, rollback
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path

        # Core systems
        self.tool_tracker = get_tool_tracker(root_path)
        self.discovery = get_comprehensive_tool_discovery(root_path)
        self.discovery_result: Optional[Any] = None

        # Learning and intelligence systems (optional dependencies)
        if PatternRecognitionSystem:
            self.pattern_system = PatternRecognitionSystem(root_path)
        else:
            self.pattern_system = None

        if UserPreferenceLearningSystem:
            self.user_preference_system = UserPreferenceLearningSystem(root_path)
        else:
            self.user_preference_system = None

        # Session and context management (optional dependency)
        if SessionStorageManager:
            self.session_storage = SessionStorageManager(root_path)
        else:
            self.session_storage = None
        self.enhanced_context_manager = get_enhanced_context_manager(root_path)

        # Safety and alignment systems
        if IASGuardrails:
            self.guardrails = IASGuardrails()
        else:
            self.guardrails = None
        self.mandatory_gate = get_mandatory_gate(root_path)

        # Session management
        self.sessions: Dict[str, ToolExecutionContext] = {}
        self._session_lock = threading.Lock()

        # Tool execution cache and triggers
        self._analyzer_cache: Dict[str, Any] = {}
        self.tool_triggers: Dict[str, List[ToolExecutionTrigger]] = {}

        # Configuration
        self.user_preferences = self._load_user_preferences()
        self.vision_context = self._load_vision_context()
        self.safety_gates = self._load_safety_gates()

        # Execution history for learning
        self.execution_history: List[Dict[str, Any]] = []

        # Initialize tool triggers
        self._initialize_unified_triggers()

    def _initialize_unified_triggers(self) -> None:
        """Initialize unified trigger system combining all orchestration approaches."""

        # Code Quality Analysis - Enhanced with session awareness
        self.tool_triggers[UnifiedToolCategory.CODE_QUALITY.value] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=[
                    "cleanup",
                    "refactor",
                    "quality",
                    "dead code",
                    "unused",
                    "optimize",
                ],
                priority=4,
                cooldown_minutes=60,
                vision_alignment_required=True,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["refactoring", "cleanup", "code_changes"],
                priority=5,
                cooldown_minutes=30,
                requires_user_confirmation=True,
            ),
            ToolExecutionTrigger(
                trigger_type="session_event",
                session_events=["large_code_change", "multiple_file_edit"],
                priority=4,
                cooldown_minutes=45,
            ),
        ]

        # File Organization - Strategy-aware triggers
        self.tool_triggers[UnifiedToolCategory.FILE_ORGANIZATION.value] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=[
                    "organize",
                    "structure",
                    "layout",
                    "reorganize",
                    "move files",
                ],
                priority=3,
                cooldown_minutes=45,
                vision_alignment_required=True,
            ),
            ToolExecutionTrigger(
                trigger_type="pattern",
                patterns=["file.*move", "directory.*restructure", "organize.*files"],
                priority=4,
                cooldown_minutes=30,
            ),
        ]

        # Risk Assessment - Safety-first approach
        self.tool_triggers[UnifiedToolCategory.RISK_ASSESSMENT.value] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["risk", "dangerous", "breaking", "impact", "safety"],
                priority=5,
                cooldown_minutes=10,
                requires_user_confirmation=True,
                vision_alignment_required=True,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["breaking_changes", "system_changes", "major_refactoring"],
                priority=5,
                cooldown_minutes=5,
                requires_user_confirmation=True,
            ),
        ]

        # Session Management triggers
        self.tool_triggers[UnifiedToolCategory.SESSION_MANAGEMENT.value] = [
            ToolExecutionTrigger(
                trigger_type="session_event",
                session_events=["session_start", "context_switch", "user_change"],
                priority=2,
                cooldown_minutes=5,
            )
        ]

        # Continuous Improvement triggers
        self.tool_triggers["kaizen_automation"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=[
                    "kaizen",
                    "continuous improvement",
                    "automate",
                    "improve",
                    "cycle",
                ],
                priority=3,
                cooldown_minutes=60,
                vision_alignment_required=True,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=[
                    "continuous_improvement",
                    "automation",
                    "system_optimization",
                ],
                priority=4,
                cooldown_minutes=30,
            ),
        ]

        # Debugging triggers
        self.tool_triggers["smart_debugger"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["debug", "debugger", "error", "fix", "problem", "issue"],
                priority=4,
                cooldown_minutes=15,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["debugging", "error_handling", "troubleshooting"],
                priority=5,
                cooldown_minutes=10,
            ),
        ]

        # Performance triggers
        self.tool_triggers["performance_optimizer"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["performance", "optimize", "speed", "slow", "efficiency"],
                priority=4,
                cooldown_minutes=45,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["performance_issues", "optimization", "bottlenecks"],
                priority=5,
                cooldown_minutes=30,
            ),
        ]

        # Safety and Damage Detection triggers
        self.tool_triggers["system_damage_detector"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=[
                    "damage",
                    "system damage",
                    "integrity",
                    "corruption",
                    "safety",
                ],
                priority=5,
                cooldown_minutes=10,
                requires_user_confirmation=True,
                vision_alignment_required=True,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["system_integrity", "damage_assessment", "safety_check"],
                priority=5,
                cooldown_minutes=5,
                requires_user_confirmation=True,
            ),
        ]

        # Vision Alignment triggers
        self.tool_triggers["enhanced_vision_interrogator"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["vision", "alignment", "align", "goal", "objective"],
                priority=3,
                cooldown_minutes=30,
                vision_alignment_required=True,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["vision_check", "alignment_verification", "goal_assessment"],
                priority=4,
                cooldown_minutes=20,
            ),
        ]

        # AI Agent Gate triggers
        self.tool_triggers["agent_gate_detector"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["ai agent", "gate", "agent gate", "ai safety"],
                priority=4,
                cooldown_minutes=15,
                requires_user_confirmation=True,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["ai_agent_management", "gate_system", "ai_safety"],
                priority=5,
                cooldown_minutes=10,
                requires_user_confirmation=True,
            ),
        ]

        # Metrics and Monitoring triggers
        self.tool_triggers["unified_metrics_collector"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["metrics", "monitor", "analytics", "tracking", "data"],
                priority=2,
                cooldown_minutes=30,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["monitoring", "metrics_collection", "analytics"],
                priority=3,
                cooldown_minutes=20,
            ),
        ]

        self.tool_triggers["universal_error_monitor"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["error monitor", "universal monitor", "error tracking"],
                priority=3,
                cooldown_minutes=15,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["error_monitoring", "system_errors", "universal_tracking"],
                priority=4,
                cooldown_minutes=10,
            ),
        ]

        # Learning and Persistence triggers
        self.tool_triggers["learning_persistence"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["learning", "persistence", "memory", "knowledge", "persist"],
                priority=2,
                cooldown_minutes=60,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=[
                    "learning_system",
                    "knowledge_persistence",
                    "memory_management",
                ],
                priority=3,
                cooldown_minutes=45,
            ),
        ]

        self.tool_triggers["continuous_improvement_validator"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=[
                    "validate improvement",
                    "improvement check",
                    "continuous validate",
                ],
                priority=3,
                cooldown_minutes=45,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=[
                    "improvement_validation",
                    "continuous_validation",
                    "system_validation",
                ],
                priority=4,
                cooldown_minutes=30,
            ),
        ]

        # Planning and Configuration triggers
        self.tool_triggers["dynamic_planner"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["plan", "planning", "dynamic", "strategy", "roadmap"],
                priority=3,
                cooldown_minutes=60,
                vision_alignment_required=True,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["strategic_planning", "dynamic_planning", "system_planning"],
                priority=4,
                cooldown_minutes=45,
            ),
        ]

        self.tool_triggers["adaptive_config_manager"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["config", "configuration", "adaptive", "adapt", "settings"],
                priority=2,
                cooldown_minutes=45,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=[
                    "configuration_management",
                    "adaptive_config",
                    "system_config",
                ],
                priority=3,
                cooldown_minutes=30,
            ),
        ]

        # WBS Management triggers
        self.tool_triggers["wbs_auto_update_engine"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["wbs update", "auto update", "work breakdown", "task update"],
                priority=3,
                cooldown_minutes=30,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["wbs_updates", "task_management", "work_breakdown"],
                priority=4,
                cooldown_minutes=20,
            ),
        ]

        self.tool_triggers["wbs_synchronization_engine"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["wbs sync", "synchronize", "wbs synchronization"],
                priority=4,
                cooldown_minutes=15,
                requires_user_confirmation=True,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["wbs_sync", "synchronization", "task_sync"],
                priority=5,
                cooldown_minutes=10,
                requires_user_confirmation=True,
            ),
        ]

        self.tool_triggers["wbs_update_engine"] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["wbs engine", "update engine", "work breakdown engine"],
                priority=3,
                cooldown_minutes=30,
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["wbs_engine", "update_management", "task_updates"],
                priority=4,
                cooldown_minutes=20,
            ),
        ]

        # Background and Optimization triggers

    def orchestrate_tools(
        self,
        user_request: str,
        context: Optional[ToolExecutionContext] = None,
        strategy: UnifiedOrchestrationStrategy = UnifiedOrchestrationStrategy.ADAPTIVE,
        session_id: Optional[str] = None,
    ) -> UnifiedOrchestrationResult:
        """
        Main orchestration method combining all approaches.

        This method intelligently routes to the appropriate orchestration approach
        based on the strategy and context provided.
        """

        start_time = time.time()
        result = UnifiedOrchestrationResult()

        # Create or get execution context
        if context is None:
            context = ToolExecutionContext(
                user_request=user_request, strategy=strategy, session_id=session_id
            )

        # Track orchestration start
        self.tool_tracker.track_tool_usage(
            tool_name="unified_tool_orchestration",
            tool_type="Tool_Orchestration",
            parameters={
                "user_request": user_request[:100],
                "strategy": strategy.value,
                "session_id": session_id,
            },
            result="started",
        )

        try:
            # Step 1: Initialize tool discovery if needed
            if not self.discovery_result:
                self.discovery_result = self.discovery.discover_all_tools()

            # Step 2: Route to appropriate orchestration approach
            trigger_strategies = [
                UnifiedOrchestrationStrategy.TRIGGER_BASED,
                UnifiedOrchestrationStrategy.LEARNING_DRIVEN,
            ]
            holistic_strategies = [
                UnifiedOrchestrationStrategy.VISION_FIRST,
                UnifiedOrchestrationStrategy.COMPREHENSIVE_ANALYSIS,
            ]
            session_strategies = [
                UnifiedOrchestrationStrategy.SESSION_AWARE,
                UnifiedOrchestrationStrategy.ROLLBACK_SAFE,
            ]

            if strategy in trigger_strategies:
                result = self._execute_intelligent_orchestration(context)
            elif strategy in holistic_strategies:
                result = self._execute_holistic_orchestration(context)
            elif strategy in session_strategies:
                result = self._execute_session_orchestration(context)
            else:  # ADAPTIVE - use intelligent routing
                result = self._execute_adaptive_orchestration(context)

            result.total_execution_time = time.time() - start_time
            result.success = True

            # Learn from successful execution
            self._learn_from_execution(context, result)

            # Track successful completion
            self.tool_tracker.track_tool_usage(
                tool_name="unified_tool_orchestration",
                tool_type="Tool_Orchestration",
                parameters={
                    "tools_executed": len(result.executed_tools),
                    "execution_time": result.total_execution_time,
                    "strategy": strategy.value,
                },
                result="completed",
            )

        except Exception as e:
            result.errors.append(f"Unified orchestration failed: {str(e)}")
            result.total_execution_time = time.time() - start_time

            # Track failure
            self.tool_tracker.track_tool_usage(
                tool_name="unified_tool_orchestration",
                tool_type="Tool_Orchestration",
                parameters={
                    "error": str(e),
                    "execution_time": result.total_execution_time,
                },
                result="failed",
            )

        return result

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current orchestrator status and statistics."""
        return {
            "status": "active",
            "tools_available": (
                len(self.tool_registry) if hasattr(self, "tool_registry") else 0
            ),
            "active_sessions": (
                len(self.active_sessions) if hasattr(self, "active_sessions") else 0
            ),
            "last_activity": time.time(),
            "version": "1.0.0",
        }

    def _execute_intelligent_orchestration(
        self, context: ToolExecutionContext
    ) -> UnifiedOrchestrationResult:
        """Execute intelligent/trigger-based orchestration (from intelligent_tool_orchestrator.py)."""

        result = UnifiedOrchestrationResult()

        trigger_analysis = self._analyze_triggers(context)
        context.trigger_matches = trigger_analysis

        for recommendation in trigger_analysis:
            tool_name = recommendation["tool"]
            confidence = recommendation.get("confidence", 0)
            if confidence < 0.3:
                continue

            execution_context = {
                "user_request": context.user_request,
                "confidence": confidence,
                "trigger_details": recommendation.get("triggers", []),
                "conversation_history": context.conversation_history,
                "session_id": context.session_id,
            }

            tool_result = self._execute_tool_safely(
                tool_name, context, execution_context
            )
            if tool_result and tool_result.get("executed", False):
                result.executed_tools.append(tool_name)
                result.tool_results[tool_name] = (
                    tool_result.get("results") or tool_result
                )
                result.insights.extend(tool_result.get("insights", []))

        return result

    def _execute_holistic_orchestration(
        self, context: ToolExecutionContext
    ) -> UnifiedOrchestrationResult:
        """Execute holistic/strategy-based orchestration (from holistic_tool_orchestration.py)."""

        result = UnifiedOrchestrationResult()

        # Vision alignment check
        if context.strategy == UnifiedOrchestrationStrategy.VISION_FIRST:
            vision_score = self._check_vision_alignment(context)
            result.vision_alignment_score = vision_score
            if vision_score < 0.7:  # Vision alignment threshold
                result.warnings.append("Request may not align with project vision")

        # Execute comprehensive analysis
        analysis_tools = self._select_analysis_tools(context)
        for tool_name in analysis_tools:
            tool_result = self._execute_tool_safely(tool_name, context)
            if tool_result and tool_result.get("executed", False):
                result.executed_tools.append(tool_name)
                result.tool_results[tool_name] = (
                    tool_result.get("results") or tool_result
                )
                result.insights.extend(tool_result.get("insights", []))

        return result

    def _execute_session_orchestration(
        self, context: ToolExecutionContext
    ) -> UnifiedOrchestrationResult:
        """Execute session-aware orchestration (from ai_agent_orchestration.py)."""

        result = UnifiedOrchestrationResult()

        # Session management
        if context.session_id:
            session_context = self._get_or_create_session(
                context.session_id, context.user_id
            )
            result.session_context = {"session_id": context.session_id, "active": True}

        # Create checkpoint if rollback enabled
        if context.rollback_enabled:
            checkpoint_id = self._create_checkpoint(context)
            result.checkpoint_created = checkpoint_id
            result.rollback_available = True

        # Execute tools with session awareness
        session_tools = self._select_session_aware_tools(context)
        for tool_name in session_tools:
            tool_result = self._execute_tool_safely(tool_name, context)
            if tool_result and tool_result.get("executed", False):
                result.executed_tools.append(tool_name)
                result.tool_results[tool_name] = (
                    tool_result.get("results") or tool_result
                )
                result.insights.extend(tool_result.get("insights", []))

        return result

    def _execute_adaptive_orchestration(
        self, context: ToolExecutionContext
    ) -> UnifiedOrchestrationResult:
        """Execute adaptive orchestration combining all approaches intelligently."""

        result = UnifiedOrchestrationResult()

        # Analyze context to determine best approach
        if self._should_use_triggers(context):
            trigger_result = self._execute_intelligent_orchestration(context)
            result = self._merge_results(result, trigger_result)

        if self._should_check_vision(context):
            vision_result = self._execute_holistic_orchestration(context)
            result = self._merge_results(result, vision_result)

        if self._should_use_session(context):
            session_result = self._execute_session_orchestration(context)
            result = self._merge_results(result, session_result)

        return result

    def _analyze_triggers(self, context: ToolExecutionContext) -> List[Dict[str, Any]]:
        """Analyze context and conversation to determine applicable tools."""

        recent_messages = " ".join(
            msg.get("content", "") for msg in context.conversation_history[-10:]
        ).lower()

        # Also include the current user request for trigger matching
        if context.user_request:
            recent_messages += " " + context.user_request.lower()

        recommendations: List[Dict[str, Any]] = []
        now = time.time()

        for tool_name, triggers in self.tool_triggers.items():
            confidence = 0
            trigger_matches: List[Dict[str, Any]] = []

            for trigger in triggers:
                score = 0

                if trigger.trigger_type == "keyword":
                    score += sum(
                        1 for keyword in trigger.keywords if keyword in recent_messages
                    )
                elif trigger.trigger_type == "context":
                    score += sum(
                        2
                        for ctx in trigger.contexts
                        if ctx in context.safety_requirements.get("contexts", [])
                        or ctx in context.user_preferences.get("focus_areas", [])
                    )
                elif trigger.trigger_type == "pattern":
                    score += sum(
                        3
                        for pattern in trigger.patterns
                        if re.search(pattern, recent_messages)
                    )
                elif trigger.trigger_type == "session_event" and context.session_id:
                    score += 2

                if score > 0:
                    confidence += score * trigger.priority
                    trigger_matches.append(
                        {
                            "trigger": trigger.trigger_type,
                            "score": score,
                            "priority": trigger.priority,
                            "cooldown": trigger.cooldown_minutes,
                        }
                    )

            if confidence:
                normalized = min(confidence / 10, 1.0)
                recommendations.append(
                    {
                        "tool": tool_name,
                        "confidence": normalized,
                        "triggers": trigger_matches,
                        "last_evaluated": now,
                        "reasoning": f"{len(trigger_matches)} trigger matches, confidence {normalized:.2f}",
                    }
                )

        recommendations.sort(key=lambda item: item.get("confidence", 0), reverse=True)
        return recommendations

    def _execute_tool_safely(
        self,
        tool_name: str,
        context: ToolExecutionContext,
        trigger_context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Execute a tool with unified safety checks and tracking."""

        execution_result: Dict[str, Any] = {
            "tool": tool_name,
            "executed": False,
            "results": None,
            "insights": [],
            "error": None,
        }

        try:
            unified_handlers: Dict[
                str, Callable[[ToolExecutionContext], Dict[str, Any]]
            ] = {
                # Core analysis tools
                "code_quality_analysis": lambda ctx: self._run_code_quality(ctx),
                "organization_analysis": lambda ctx: self._run_file_organization(ctx),
                "structural_recommendations": lambda ctx: self._run_structural_recommendations(
                    ctx
                ),
                "structural_recommendation_engine": lambda ctx: self._run_structural_recommendations(
                    ctx, organization_required=False
                ),
                "risk_assessment": lambda ctx: self._run_risk_assessment(ctx),
                "dependency_analysis": lambda ctx: self._run_dependency_analysis(ctx),
                "dependency_mapper": lambda ctx: self._run_dependency_analysis(ctx),
                "code_quality_analyzer": lambda ctx: self._run_code_quality(ctx),
                "file_organization_analyzer": lambda ctx: self._run_file_organization(
                    ctx
                ),
                "duplicate_detector": lambda ctx: self._run_duplicate_detection(ctx),
                "duplicate_detection": lambda ctx: self._run_duplicate_detection(ctx),
                "syntax_validator": lambda ctx: self._run_syntax_validation(ctx),
                "dependency_checker": lambda ctx: self._run_dependency_checker(ctx),
                # Project management and workflow tools
                "approval_workflow": lambda ctx: self._run_approval_workflow(ctx),
                "critical_path_engine": lambda ctx: self._run_critical_path(ctx),
                "progress_dashboard": lambda ctx: self._run_progress_dashboard(ctx),
                "task_completion_detector": lambda ctx: self._run_task_completion(ctx),
                "task_prioritization_engine": lambda ctx: self._run_task_prioritization(
                    ctx
                ),
                "wbs_management": lambda ctx: self._run_wbs_management(ctx),
                "task_integration_logic": lambda ctx: self._run_task_integration(ctx),
                "task_execution_gate": lambda ctx: self._run_task_execution_gate(ctx),
                # Safety, vision, and user preference tools
                "enhanced_vision_interrogator": lambda ctx: self._run_enhanced_vision_interrogator(
                    ctx
                ),
                "vision_guardian": lambda ctx: self._run_vision_guardian(ctx),
                "gate_system": lambda ctx: self._run_gate_system(ctx),
                "ultra_safe_cleanup": lambda ctx: self._run_ultra_safe_cleanup(ctx),
                "charter_management": lambda ctx: self._run_charter_management(ctx),
                "automatic_error_prevention": lambda ctx: self._run_automatic_error_prevention(
                    ctx
                ),
                "pattern_recognition_system": lambda ctx: self._run_pattern_recognition(
                    ctx
                ),
                "conversation_analysis": lambda ctx: self._run_conversation_analysis(
                    ctx
                ),
                "user_preference_learning_system": lambda ctx: self._run_user_preferences(
                    ctx
                ),
                "ui_enhancement": lambda ctx: self._run_ui_enhancement(ctx),
                # Agent orchestration and validation tools
                "ai_agent_orchestration": lambda ctx: self._run_ai_agent_status(ctx),
                "decision_pipeline": lambda ctx: self._run_decision_pipeline(ctx),
                "intelligent_monitoring": lambda ctx: self._run_intelligent_monitoring(
                    ctx
                ),
                "automated_health_monitoring": lambda ctx: self._run_health_monitoring(
                    ctx
                ),
                "validation_runtime": lambda ctx: self._run_validation_runtime(ctx),
                "dead_code_validation": lambda ctx: self._run_dead_code_validation(ctx),
                # Continuous improvement and automation tools
                "kaizen_automation": lambda ctx: self._run_kaizen_automation(ctx),
                "smart_debugger": lambda ctx: self._run_smart_debugger(ctx),
                "performance_optimizer": lambda ctx: self._run_performance_optimizer(
                    ctx
                ),
                "system_damage_detector": lambda ctx: self._run_system_damage_detector(
                    ctx
                ),
                "agent_gate_detector": lambda ctx: self._run_agent_gate_detector(ctx),
                # Metrics and monitoring tools
                "unified_metrics_collector": lambda ctx: self._run_unified_metrics_collector(
                    ctx
                ),
                "universal_error_monitor": lambda ctx: self._run_universal_error_monitor(
                    ctx
                ),
                "continuous_improvement_validator": lambda ctx: self._run_continuous_improvement_validator(
                    ctx
                ),
                "learning_persistence": lambda ctx: self._run_learning_persistence(ctx),
                # Planning and configuration tools
                "dynamic_planner": lambda ctx: self._run_dynamic_planner(ctx),
                "adaptive_config_manager": lambda ctx: self._run_adaptive_config_manager(
                    ctx
                ),
                # WBS management tools
                "wbs_auto_update_engine": lambda ctx: self._run_wbs_auto_update_engine(
                    ctx
                ),
                "wbs_synchronization_engine": lambda ctx: self._run_wbs_synchronization_engine(
                    ctx
                ),
                "wbs_update_engine": lambda ctx: self._run_wbs_update_engine(ctx),
                # Background and optimization tools
            }

            handler = unified_handlers.get(tool_name)
            if not handler:
                execution_result["error"] = "Handler not implemented"
                return execution_result

            handler_result = handler(context)
            execution_result["results"] = handler_result
            execution_result["executed"] = True

            if handler_result and isinstance(handler_result, dict):
                insights = handler_result.get("insights") or []
                if insights and isinstance(insights, list):
                    execution_result["insights"].extend(insights)

            self.tool_tracker.track_tool_usage(
                tool_name=f"unified_{tool_name}",
                tool_type="Unified_Execution",
                parameters={
                    "trigger_context": trigger_context or {},
                    "strategy": context.strategy.value,
                    "session_id": context.session_id,
                },
                result="completed",
            )

            if self.user_preference_system:
                self._learn_from_tool_execution(tool_name, context, execution_result)

        except Exception as exc:  # pylint: disable=broad-except
            error_message = str(exc)
            execution_result["error"] = error_message
            execution_result["executed"] = False
            execution_result.setdefault("insights", []).append(
                f"Tool {tool_name} execution failed: {error_message}"
            )

            self.tool_tracker.track_tool_usage(
                tool_name=f"unified_{tool_name}",
                tool_type="Unified_Execution",
                parameters={
                    "trigger_context": trigger_context or {},
                    "strategy": context.strategy.value,
                    "session_id": context.session_id,
                },
                result="failed",
            )

            self._learn_from_tool_failure(tool_name, context, error_message)

        return execution_result

    def _check_vision_alignment(self, context: ToolExecutionContext) -> float:
        """Check vision alignment score."""
        return 0.8  # Placeholder

    def _select_analysis_tools(self, context: ToolExecutionContext) -> List[str]:
        """Select tools for comprehensive analysis."""
        return ["code_quality_analyzer", "file_organization_analyzer"]

    def _select_session_aware_tools(self, context: ToolExecutionContext) -> List[str]:
        """Select tools based on session context."""
        return ["pattern_recognition_system", "user_preference_learning"]

    def _get_or_create_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Get or create session context."""
        return {"session_id": session_id, "user_id": user_id}

    def _create_checkpoint(self, context: ToolExecutionContext) -> str:
        """Create rollback checkpoint."""
        return f"checkpoint_{int(time.time())}"

    def _should_use_triggers(self, context: ToolExecutionContext) -> bool:
        """Determine if trigger-based orchestration should be used."""
        return len(context.conversation_history) > 0

    def _should_check_vision(self, context: ToolExecutionContext) -> bool:
        """Determine if vision alignment should be checked."""
        return "vision" in context.user_request.lower()

    def _should_use_session(self, context: ToolExecutionContext) -> bool:
        """Determine if session-based orchestration should be used."""
        return context.session_id is not None

    def _merge_results(
        self, result1: UnifiedOrchestrationResult, result2: UnifiedOrchestrationResult
    ) -> UnifiedOrchestrationResult:
        """Merge two orchestration results."""
        result1.executed_tools.extend(result2.executed_tools)
        result1.tool_results.update(result2.tool_results)
        result1.insights.extend(result2.insights)
        result1.recommendations.extend(result2.recommendations)
        result1.errors.extend(result2.errors)
        result1.warnings.extend(result2.warnings)

        # Take maximum scores
        result1.vision_alignment_score = max(
            result1.vision_alignment_score, result2.vision_alignment_score
        )
        result1.user_preference_compliance = max(
            result1.user_preference_compliance, result2.user_preference_compliance
        )
        result1.safety_compliance = min(
            result1.safety_compliance, result2.safety_compliance
        )  # Take minimum for safety

        return result1

    def _learn_from_execution(
        self,
        context: ToolExecutionContext,
        result: UnifiedOrchestrationResult,
    ) -> None:
        """Learn from successful tool execution for pattern recognition."""
        try:
            user_request = context.user_request or ""
            tool_name = (
                result.executed_tools[0] if result.executed_tools else "unknown_tool"
            )
            # Convert result to serializable dictionary
            serializable_result = {
                "success": result.success,
                "executed_tools": result.executed_tools,
                "tool_results_keys": list(result.tool_results.keys()),
                "total_execution_time": result.total_execution_time,
                "insights_count": len(result.insights),
                "recommendations_count": len(result.recommendations),
                "errors_count": len(result.errors),
                "warnings_count": len(result.warnings),
            }

            self.pattern_system.learn_from_cli_usage(
                command=(
                    f"tool_execution:{context.strategy.value}:"
                    f"{context.session_id or 'default_session'}:{tool_name}"
                ),
                success=True,
                context={
                    "tool_name": tool_name,
                    "user_request": user_request[:100],
                    "strategy": context.strategy.value,
                    "session_id": context.session_id,
                    "execution_result": serializable_result,
                },
            )

            user_id = context.user_id or "default_user"
            self.user_preference_system.record_user_interaction(
                user_id=user_id,
                interaction_type="command_execution",
                context={
                    "tool_name": tool_name,
                    "request": user_request[:200],
                    "auto_applied": True,
                    "strategy": context.strategy.value,
                },
                outcome={
                    "tool_success": True,
                    "insights": result.insights,
                },
                satisfaction_score=None,
            )

        except Exception as exc:  # pylint: disable=broad-except
            print(f"⚠️ Learning from tool execution failed: {exc}")

    def _learn_from_tool_failure(
        self,
        tool_name: str,
        context: ToolExecutionContext,
        error: str,
    ) -> None:
        """Learn from failed tool execution for error prevention."""
        try:
            user_request = context.user_request or ""
            self.pattern_system.learn_from_cli_usage(
                command=(
                    f"tool_execution:{context.strategy.value}:"
                    f"{context.session_id or 'default_session'}:{tool_name}"
                ),
                success=False,
                context={
                    "tool_name": tool_name,
                    "user_request": user_request[:100],
                    "strategy": context.strategy.value,
                    "error": error,
                    "failure_type": "tool_execution_error",
                },
            )

        except Exception as exc:  # pylint: disable=broad-except
            print(f"⚠️ Learning from tool failure failed: {exc}")

    def _load_user_preferences(self) -> Dict[str, Any]:
        """Load user preferences."""
        return {
            "communication_style": "concise",
            "tool_preferences": ["code_quality", "file_organization"],
            "safety_level": "high",
            "vision_alignment_required": True,
        }

    def _load_vision_context(self) -> Dict[str, Any]:
        """Load vision context."""
        return {
            "project_goals": ["build_robust_ai_system", "ensure_safety"],
            "non_goals": ["quick_hacks", "unsafe_operations"],
            "risk_appetite": "low",
        }

    def _load_safety_gates(self) -> Dict[str, Any]:
        """Load safety gate configurations."""
        return {
            "cleanup_gate": {"enabled": True, "threshold": 0.9},
            "vision_gate": {"enabled": True, "threshold": 0.8},
            "safety_gate": {"enabled": True, "threshold": 0.95},
        }

    def _get_cached_analyzer(self, name: str, analyzer_class: type) -> Any:
        """Get a cached analyzer instance."""
        if name not in self._analyzer_cache:
            self._analyzer_cache[name] = analyzer_class(self.root_path)
        return self._analyzer_cache[name]

    def _learn_from_tool_execution(
        self, tool_name: str, context: ToolExecutionContext, result: Dict[str, Any]
    ) -> None:
        """Learn from tool execution for future improvements."""
        if not self.user_preference_system:
            return

        try:
            # Record user interaction for learning
            self.user_preference_system.record_user_interaction(
                user_id=context.user_id,
                action=f"tool_execution_{tool_name}",
                context={
                    "tool": tool_name,
                    "strategy": context.strategy.value,
                    "success": result.get("executed", False),
                    "user_request": context.user_request,
                },
                outcome="positive" if result.get("executed", False) else "negative",
            )
        except Exception:
            # Don't let learning failures break tool execution
            pass

    def _run_code_quality(self, context: ToolExecutionContext) -> Dict[str, Any]:
        try:
            from ..quality_safety.code_quality_analyzer import CodeQualityAnalyzer

            analyzer = self._get_cached_analyzer("code_quality", CodeQualityAnalyzer)
            analysis = analyzer.analyze_codebase()
            return {
                "results": analysis,
                "insights": [
                    "Code quality analysis completed",
                    f"Identified {len(getattr(analysis, 'issues', []))} code quality issues",
                    f"Overall quality score: {getattr(analysis, 'overall_quality_score', 0):.1f}",
                ],
            }
        except ImportError:
            return {
                "results": {"issues": [], "overall_quality_score": 8.5, "mock": True},
                "insights": [
                    "Code quality analysis completed (mock mode - analyzer not available)",
                    "Mock analysis shows 0 issues",
                    "Overall quality score: 8.5 (mock)",
                ],
            }

    def _run_file_organization(self, context: ToolExecutionContext) -> Dict[str, Any]:
        try:
            from ..monitoring_analytics.file_organization_analyzer import (
                FileOrganizationAnalyzer,
            )

            analyzer = self._get_cached_analyzer(
                "organization", FileOrganizationAnalyzer
            )
            organization = analyzer.analyze_organization()
            return {
                "results": organization,
                "insights": [
                    "File organization analysis completed",
                    f"Identified {len(getattr(organization, 'issues', []))} organization issues",
                    f"Files analyzed: {getattr(organization, 'files_analyzed', 0)}",
                ],
            }
        except ImportError:
            return {
                "results": {"issues": [], "files_analyzed": 50, "mock": True},
                "insights": [
                    "File organization analysis completed (mock mode - analyzer not available)",
                    "Mock analysis shows 0 organization issues",
                    "Files analyzed: 50 (mock)",
                ],
            }

    def _run_structural_recommendations(
        self, context: ToolExecutionContext, organization_required: bool = True
    ) -> Dict[str, Any]:
        org_result = None
        if organization_required and FileOrganizationAnalyzer:
            org_result = FileOrganizationAnalyzer(self.root_path).analyze_organization()

        if StructuralRecommendationEngine:
            engine = StructuralRecommendationEngine(self.root_path)
            recommendations = engine.generate_recommendations(org_result)
        else:
            recommendations = []
        return {
            "results": recommendations,
            "insights": [
                "Structural recommendations generated",
                f"File moves suggested: {len(getattr(recommendations, 'file_moves', []))}",
            ],
        }

    def _run_risk_assessment(self, context: ToolExecutionContext) -> Dict[str, Any]:
        if not (
            FileOrganizationAnalyzer
            and StructuralRecommendationEngine
            and RiskAssessmentFramework
        ):
            return {
                "results": {},
                "insights": ["Risk assessment not available - analyzers not loaded"],
            }

        org_result = FileOrganizationAnalyzer(self.root_path).analyze_organization()
        recommendations = StructuralRecommendationEngine(
            self.root_path
        ).generate_recommendations(org_result)

        framework = RiskAssessmentFramework(self.root_path)
        changes = []
        for move in getattr(recommendations, "file_moves", []):
            change = framework.create_change_from_recommendation(move, "file_move")
            if change:
                changes.append(change)

        risk_result = framework.assess_change_risks(changes)
        return {
            "results": risk_result,
            "insights": [
                "Risk assessment completed",
                f"Changes evaluated: {len(changes)}",
            ],
        }

    def _run_dependency_analysis(self, context: ToolExecutionContext) -> Dict[str, Any]:
        if not DependencyMapper:
            return {
                "results": {},
                "insights": ["Dependency analysis not available - mapper not loaded"],
            }

        mapper = DependencyMapper(self.root_path)
        dependencies = mapper.analyze_dependencies()
        return {
            "results": dependencies,
            "insights": ["Dependency analysis completed"],
        }

    def _run_duplicate_detection(self, context: ToolExecutionContext) -> Dict[str, Any]:
        if not DuplicateDetector:
            return {
                "results": {},
                "insights": ["Duplicate detection not available - detector not loaded"],
            }

        detector = self._get_cached_analyzer("duplicate", DuplicateDetector)
        duplicates = detector.analyze_duplicates()
        return {
            "results": duplicates,
            "insights": [
                "Duplicate detection completed",
                f"Duplicate groups found: {len(getattr(duplicates, 'duplicate_groups', []))}",
            ],
        }

    def _run_syntax_validation(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from ..quality_safety.syntax_validator import validate_python_syntax

        exclude_dirs = {
            "venv",
            "__pycache__",
            ".git",
            ".vscode",
            ".idea",
            "node_modules",
            "dist",
            "build",
            ".ai_onboard",
            ".pytest_cache",
            ".mypy_cache",
            ".tox",
        }

        syntax_results = []
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    try:
                        with open(
                            filepath, "r", encoding="utf-8"
                        ) as fh:  # pylint: disable=unspecified-encoding
                            code_content = fh.read()
                        result_status = validate_python_syntax(code_content)
                        syntax_results.append(
                            {
                                "file": filepath,
                                "valid": result_status.get("valid", False),
                                "status": result_status,
                            }
                        )
                    except Exception as exc:  # pylint: disable=broad-except
                        syntax_results.append(
                            {
                                "file": filepath,
                                "valid": False,
                                "error": str(exc),
                            }
                        )

        return {
            "results": {
                "total_files": len(syntax_results),
                "valid_files": len([r for r in syntax_results if r.get("valid")]),
                "invalid_files": len([r for r in syntax_results if not r.get("valid")]),
                "details": syntax_results,
            },
            "insights": [
                "Syntax validation completed",
                f"Valid Python files: {len([r for r in syntax_results if r.get('valid')])}",
            ],
        }

    def _run_dependency_checker(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from ..quality_safety.dependency_checker import check_cleanup_dependencies

        cleanup_targets: List[Path] = []
        for root, _, files in os.walk(self.root_path):
            for file in files:
                if file.endswith((".pyc", ".pyo", "__pycache__", ".tmp", ".bak")):
                    cleanup_targets.append(Path(root) / file)

        if cleanup_targets:
            checked = check_cleanup_dependencies(self.root_path, cleanup_targets[:10])
            results = {
                "safe_to_remove": checked,
                "total_targets": len(cleanup_targets),
                "checked_targets": min(10, len(cleanup_targets)),
                "message": f"Found {len(cleanup_targets)} cleanup targets",
            }
        else:
            results = {
                "safe_to_remove": True,
                "total_targets": 0,
                "checked_targets": 0,
                "message": "No cleanup targets found",
            }

        return {
            "results": results,
            "insights": [
                "Dependency cleanup analysis completed",
                f"Potential cleanup targets: {len(cleanup_targets)}",
            ],
        }

    def _run_approval_workflow(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from ..project_management.approval_workflow import get_approval_workflow

        workflow = get_approval_workflow(self.root_path)
        pending = workflow.get_pending_requests()
        return {
            "results": {
                "pending_requests": len(pending),
                "requests": [
                    {
                        "id": req.request_id,
                        "action": (
                            req.proposed_actions[0].description
                            if req.proposed_actions
                            else "Unknown"
                        ),
                        "urgency": req.urgency,
                    }
                    for req in pending[:5]
                ],
            },
            "insights": [
                "Approval workflow status retrieved",
                f"Pending approvals: {len(pending)}",
            ],
        }

    def _run_critical_path(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from ..project_management.critical_path_engine import analyze_critical_path

        analysis = analyze_critical_path(self.root_path)
        return {
            "results": analysis,
            "insights": ["Critical path analysis completed"],
        }

    def _run_progress_dashboard(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from ..legacy_cleanup.pm_compatibility import get_legacy_progress_dashboard

        dashboard = get_legacy_progress_dashboard(self.root_path)
        status = dashboard.generate_dashboard()
        return {
            "results": status,
            "insights": ["Progress dashboard updated"],
        }

    def _run_task_completion(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from ..legacy_cleanup.pm_compatibility import (
            get_legacy_task_completion_detector,
        )

        detector = get_legacy_task_completion_detector(self.root_path)
        scan_result = detector.detect_completed_tasks()
        return {
            "results": scan_result,
            "insights": ["Task completion scan completed"],
        }

    def _run_task_prioritization(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from ..legacy_cleanup.pm_compatibility import (
            get_legacy_task_prioritization_engine,
        )

        engine = get_legacy_task_prioritization_engine(self.root_path)
        priorities = engine.prioritize_all_tasks()
        return {
            "results": priorities,
            "insights": ["Task prioritization generated"],
        }

    def _run_wbs_management(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from ..legacy_cleanup.pm_compatibility import get_legacy_wbs_sync_engine

        engine = get_legacy_wbs_sync_engine(self.root_path)
        report = engine.get_wbs_status()
        return {
            "results": report,
            "insights": ["WBS management report generated"],
        }

    def _run_task_integration(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from .task_integration_logic import TaskIntegrationLogic

        integration = TaskIntegrationLogic(self.root_path)
        # Get basic integration status - would need placement context for full analysis
        status = {"integration_available": True, "placement_needed": True}
        return {
            "results": status,
            "insights": ["Task integration status retrieved"],
        }

    def _run_task_execution_gate(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from .task_execution_gate import TaskExecutionGate

        gate = TaskExecutionGate(self.root_path)
        summary = gate.get_pending_tasks_summary()
        return {
            "results": summary,
            "insights": ["Task execution gate summary collected"],
        }

    def _run_enhanced_vision_interrogator(
        self, context: ToolExecutionContext
    ) -> Dict[str, Any]:
        from ..vision.enhanced_vision_interrogator import (
            get_enhanced_vision_interrogator,
        )

        interrogator = get_enhanced_vision_interrogator(self.root_path)

        # Check vision alignment for the current request
        if context.user_request:
            alignment = interrogator.check_vision_alignment(
                action_description=context.user_request,
                action_type="analysis",
                risk_level="low",
            )
        else:
            alignment = {
                "alignment_score": 0.5,
                "action": "unknown",
                "reason": "No request provided",
            }

        # Get interrogation status
        status = interrogator.get_enhanced_interrogation_status()

        return {
            "results": {"alignment": alignment, "status": status},
            "insights": [
                f"Vision alignment score: {alignment.get('alignment_score', 0):.2f}",
                f"Recommended action: {alignment.get('action', 'unknown')}",
                f"Interrogation status: {status.get('status', 'unknown')}",
            ],
        }

    def _run_vision_guardian(self, context: ToolExecutionContext) -> Dict[str, Any]:
        """Run vision guardian to validate vision alignment and context."""
        vision_context = self._load_vision_context()

        # Check if current context aligns with vision
        alignment_score = self._check_vision_alignment(context)

        # Get project charter and objectives
        from ..legacy_cleanup import charter

        charter_data = charter.load_charter(self.root_path)
        objectives = charter_data.get("objectives", [])

        return {
            "vision": vision_context.get("project_goals", []),
            "objectives": objectives,
            "alignment_score": alignment_score,
            "insights": [
                f"Vision guardian validated {len(objectives)} project objectives",
                f"Current alignment score: {alignment_score:.2f}",
                "Vision context loaded successfully",
            ],
        }

    def _run_gate_system(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from ..legacy_cleanup.gate_system import GateSystem

        gate_system = GateSystem(self.root_path)
        gate_status = {
            "gate_active": gate_system.is_gate_active(),
            "system_status": "operational",
        }
        return {
            "results": gate_status,
            "insights": ["Gate system status collected"],
        }

    def _run_ultra_safe_cleanup(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from ..quality_safety.ultra_safe_cleanup import UltraSafeCleanupEngine

        cleanup = UltraSafeCleanupEngine(self.root_path)
        targets = cleanup.scan_for_cleanup_targets()
        return {
            "results": {
                "targets_found": len(targets),
                "total_size_mb": (
                    sum(t.size_bytes for t in targets) / (1024 * 1024) if targets else 0
                ),
                "risk_levels": (
                    list({t.risk_level.value for t in targets}) if targets else []
                ),
                "targets_available": bool(targets),
            },
            "insights": ["Ultra safe cleanup scan completed"],
        }

    def _run_charter_management(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from ..legacy_cleanup import charter

        charter_data = charter.load_charter(self.root_path)
        return {
            "results": charter_data,
            "insights": ["Charter management data loaded"],
        }

    def _run_automatic_error_prevention(
        self, context: ToolExecutionContext
    ) -> Dict[str, Any]:
        from .automatic_error_prevention import AutomaticErrorPrevention

        prevention = AutomaticErrorPrevention(self.root_path, self.pattern_system)
        stats = prevention.get_prevention_stats()
        return {
            "results": stats,
            "insights": ["Automatic error prevention stats collected"],
        }

    def _run_pattern_recognition(self, context: ToolExecutionContext) -> Dict[str, Any]:
        stats = self.pattern_system.get_pattern_stats()
        return {
            "results": stats,
            "insights": ["Pattern recognition system status retrieved"],
        }

    def _run_conversation_analysis(
        self, context: ToolExecutionContext
    ) -> Dict[str, Any]:
        summary = self.enhanced_context_manager.get_context_continuity_summary(
            context.user_id or "default_user"
        )
        return {
            "results": summary,
            "insights": ["Conversation analysis summary generated"],
        }

    def _run_user_preferences(self, context: ToolExecutionContext) -> Dict[str, Any]:
        profile = self.user_preference_system.get_user_profile_summary(
            context.user_id or "default_user"
        )
        return {
            "results": profile,
            "insights": ["User preference profile summary generated"],
        }

    def _run_ui_enhancement(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from ..ai_integration.user_experience_system import get_user_experience_system

        ux_system = get_user_experience_system(self.root_path)
        analytics = ux_system.get_project_status(context.user_id or "default_user")
        return {
            "results": analytics,
            "insights": ["UI enhancement analytics retrieved"],
        }

    def _run_ai_agent_status(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from .orchestration_compatibility import AIAgentOrchestrationLayer

        orchestrator = AIAgentOrchestrationLayer(self.root_path)
        status = orchestrator.get_session_status(
            context.session_id or "default_session"
        )
        return {
            "results": status,
            "insights": ["AI agent orchestration status retrieved"],
        }

    def _run_decision_pipeline(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from ..ai_integration.advanced_agent_decision_pipeline import (
            AdvancedDecisionPipeline,
        )

        pipeline = AdvancedDecisionPipeline(self.root_path)
        status = {
            "pipeline_active": True,
            "decision_capabilities": [
                "risk_assessment",
                "execution_planning",
                "rollback_support",
            ],
            "supported_actions": [
                "code_generation",
                "file_operations",
                "system_commands",
            ],
        }
        return {
            "results": status,
            "insights": ["Decision pipeline capabilities summarized"],
        }

    def _run_intelligent_monitoring(
        self, context: ToolExecutionContext
    ) -> Dict[str, Any]:
        from ..ai_integration.intelligent_development_monitor import (
            get_development_monitor,
        )

        monitor = get_development_monitor(self.root_path)
        status = monitor.get_monitoring_status()
        return {
            "results": status,
            "insights": ["Intelligent monitoring status retrieved"],
        }

    def _run_health_monitoring(self, context: ToolExecutionContext) -> Dict[str, Any]:
        sys_path_backup = list(sys.path)
        sys.path.insert(0, str(self.root_path / "scripts"))
        try:
            from ..continuous_improvement.system_health_monitor import (
                get_system_health_monitor,
            )

            monitor = get_system_health_monitor(self.root_path)
            dashboard = monitor.get_health_summary()
            return {
                "results": dashboard,
                "insights": ["Automated health monitoring completed"],
            }
        except ImportError as exc:
            return {
                "results": {"error": f"Health monitoring not available: {exc}"},
                "insights": ["Automated health monitoring unavailable"],
            }
        finally:
            sys.path = sys_path_backup

    def _run_validation_runtime(self, context: ToolExecutionContext) -> Dict[str, Any]:
        from ..quality_safety.syntax_validator import validate_python_syntax

        validation = validate_python_syntax(str(self.root_path))
        return {
            "results": validation,
            "insights": ["Validation runtime executed"],
        }

    def _run_dead_code_validation(
        self, context: ToolExecutionContext
    ) -> Dict[str, Any]:
        try:
            validation_process = subprocess.run(
                [sys.executable, "scripts/analysis/validate_dead_code.py"],
                capture_output=True,
                text=True,
                cwd=self.root_path,
                timeout=60,
            )
            return {
                "results": {
                    "returncode": validation_process.returncode,
                    "stdout": validation_process.stdout,
                    "stderr": validation_process.stderr,
                    "success": validation_process.returncode == 0,
                },
                "insights": ["Dead code validation executed"],
            }
        except subprocess.TimeoutExpired:
            return {
                "results": {"error": "Validation timeout"},
                "insights": ["Dead code validation timed out"],
            }
        except Exception as exc:  # pylint: disable=broad-except
            return {
                "results": {"error": str(exc)},
                "insights": [f"Dead code validation failed: {exc}"],
            }

    def _run_kaizen_automation(self, context: ToolExecutionContext) -> Dict[str, Any]:
        try:
            from ..ai_integration.kaizen_automation import get_kaizen_automation

            engine = get_kaizen_automation(self.root_path)
            status = engine.get_automation_status()
            return {
                "results": status,
                "insights": [
                    "Kaizen automation status retrieved",
                    f"Active cycles: {status.get('active_cycles', 0)}",
                    f"Total opportunities: {status.get('total_opportunities', 0)}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "Kaizen automation not available"},
                "insights": ["Kaizen automation system not available"],
            }

    def _run_smart_debugger(self, context: ToolExecutionContext) -> Dict[str, Any]:
        try:
            from ..legacy_cleanup.smart_debugger import get_smart_debugger

            debugger = get_smart_debugger(self.root_path)
            stats = debugger.get_debugging_stats()
            return {
                "results": stats,
                "insights": [
                    "Smart debugger stats retrieved",
                    f"Debug patterns: {len(stats.get('patterns', []))}",
                    f"Solutions: {len(stats.get('solutions', []))}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "Smart debugger not available"},
                "insights": ["Smart debugger system not available"],
            }

    def _run_performance_optimizer(
        self, context: ToolExecutionContext
    ) -> Dict[str, Any]:
        try:
            from ..continuous_improvement.performance_optimizer import (
                get_performance_optimizer,
            )

            optimizer = get_performance_optimizer(self.root_path)
            summary = optimizer.get_performance_summary()
            return {
                "results": summary,
                "insights": [
                    "Performance optimization summary retrieved",
                    f"Optimization opportunities: {len(summary.get('opportunities', []))}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "Performance optimizer not available"},
                "insights": ["Performance optimizer not available"],
            }

    def _run_system_damage_detector(
        self, context: ToolExecutionContext
    ) -> Dict[str, Any]:
        try:
            from ..continuous_improvement.system_damage_detector import (
                get_system_damage_detector,
            )

            detector = get_system_damage_detector(self.root_path)
            summary = detector.get_damage_summary()
            return {
                "results": summary,
                "insights": [
                    "System damage summary retrieved",
                    f"Detected damages: {len(summary.get('damages', []))}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "System damage detector not available"},
                "insights": ["System damage detector not available"],
            }

    def _run_agent_gate_detector(self, context: ToolExecutionContext) -> Dict[str, Any]:
        try:
            from ..ai_integration.agent_gate_detector import AIAgentGateDetector

            detector = AIAgentGateDetector(self.root_path)
            active_gate = detector.check_for_active_gate()
            status = {
                "active_gate": active_gate,
                "gates_active": 1 if active_gate else 0,
            }
            return {
                "results": status,
                "insights": [
                    "AI agent gate status retrieved",
                    f"Gates active: {status.get('gates_active', 0)}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "Agent gate detector not available"},
                "insights": ["Agent gate detector not available"],
            }

    def _run_unified_metrics_collector(
        self, context: ToolExecutionContext
    ) -> Dict[str, Any]:
        try:
            from ..monitoring_analytics.unified_metrics_collector import (
                get_unified_metrics_collector,
            )

            collector = get_unified_metrics_collector(self.root_path)
            stats = collector.get_collection_stats()
            return {
                "results": stats,
                "insights": [
                    "Unified metrics stats retrieved",
                    f"Total metrics: {stats.get('total_metrics', 0)}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "Unified metrics collector not available"},
                "insights": ["Unified metrics collector not available"],
            }

    def _run_universal_error_monitor(
        self, context: ToolExecutionContext
    ) -> Dict[str, Any]:
        try:
            from .universal_error_monitor import UniversalErrorMonitor

            monitor = UniversalErrorMonitor(self.root_path)
            status = monitor.get_usage_report()
            return {
                "results": status,
                "insights": [
                    "Universal error monitoring report retrieved",
                    f"Capabilities tracked: {len(status.get('capabilities', {}))}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "Universal error monitor not available"},
                "insights": ["Universal error monitor not available"],
            }

    def _run_continuous_improvement_validator(
        self, context: ToolExecutionContext
    ) -> Dict[str, Any]:
        try:
            from ..continuous_improvement.continuous_improvement_validator import (
                ContinuousImprovementValidator,
            )

            validator = ContinuousImprovementValidator(self.root_path)
            report = validator.run_comprehensive_validation()
            return {
                "results": {
                    "validation_report": (
                        report.__dict__ if hasattr(report, "__dict__") else str(report)
                    ),
                    "passed": report.passed if hasattr(report, "passed") else True,
                    "total_tests": (
                        len(report.test_results)
                        if hasattr(report, "test_results")
                        else 0
                    ),
                },
                "insights": [
                    "Continuous improvement validation completed",
                    f"Tests run: {len(report.test_results) if hasattr(report, 'test_results') else 0}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "Continuous improvement validator not available"},
                "insights": ["Continuous improvement validator not available"],
            }

    def _run_learning_persistence(
        self, context: ToolExecutionContext
    ) -> Dict[str, Any]:
        try:
            from ..continuous_improvement.learning_persistence import (
                LearningPersistenceManager,
            )

            manager = LearningPersistenceManager(self.root_path)
            stats = manager.get_learning_stats()
            return {
                "results": stats,
                "insights": [
                    "Learning persistence stats retrieved",
                    f"Total learning events: {stats.get('total_learning_events', 0)}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "Learning persistence manager not available"},
                "insights": ["Learning persistence manager not available"],
            }

    def _run_dynamic_planner(self, context: ToolExecutionContext) -> Dict[str, Any]:
        try:
            from ..legacy_cleanup.dynamic_planner import DynamicPlanner

            planner = DynamicPlanner(self.root_path)
            plan = planner.get_current_plan()
            return {
                "results": plan,
                "insights": [
                    "Dynamic plan retrieved",
                    f"Current plan status: {plan.get('status', 'unknown')}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "Dynamic planner not available"},
                "insights": ["Dynamic planner not available"],
            }

    def _run_adaptive_config_manager(
        self, context: ToolExecutionContext
    ) -> Dict[str, Any]:
        try:
            from ..continuous_improvement.adaptive_config_manager import (
                AdaptiveConfigManager,
            )

            manager = AdaptiveConfigManager(self.root_path)
            configs = manager.get_all_configurations()
            return {
                "results": configs,
                "insights": [
                    "Adaptive configurations retrieved",
                    f"Total configurations: {len(configs)}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "Adaptive config manager not available"},
                "insights": ["Adaptive config manager not available"],
            }

    def _run_wbs_auto_update_engine(
        self, context: ToolExecutionContext
    ) -> Dict[str, Any]:
        try:
            from ..project_management.wbs_auto_update_engine import WBSAutoUpdateEngine

            engine = WBSAutoUpdateEngine(self.root_path)
            result = engine.auto_update_wbs()
            return {
                "results": result,
                "insights": [
                    "WBS auto-update completed",
                    f"Tasks updated: {len(result.get('updated_tasks', []))}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "WBS auto-update engine not available"},
                "insights": ["WBS auto-update engine not available"],
            }

    def _run_wbs_synchronization_engine(
        self, context: ToolExecutionContext
    ) -> Dict[str, Any]:
        try:
            from ..project_management.wbs_synchronization_engine import (
                WBSSynchronizationEngine,
            )

            engine = WBSSynchronizationEngine(self.root_path)
            report = engine.get_data_consistency_report()
            return {
                "results": report,
                "insights": [
                    "WBS data consistency report retrieved",
                    f"Inconsistencies found: {len(report.get('inconsistencies', []))}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "WBS synchronization engine not available"},
                "insights": ["WBS synchronization engine not available"],
            }

    def _run_wbs_update_engine(self, context: ToolExecutionContext) -> Dict[str, Any]:
        try:
            from ..project_management.wbs_update_engine import WBSUpdateEngine

            engine = WBSUpdateEngine(self.root_path)
            integrity = engine.validate_wbs_integrity()
            return {
                "results": integrity,
                "insights": [
                    "WBS integrity validated",
                    f"Integrity checks passed: {integrity.get('valid', False)}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "WBS update engine not available"},
                "insights": ["WBS update engine not available"],
            }

    def _run_optimizer(self, context: ToolExecutionContext) -> Dict[str, Any]:
        try:
            from ..continuous_improvement.optimizer import get_optimizer  # type: ignore

            optimizer = get_optimizer(self.root_path)
            optimizations = optimizer.get_optimization_status()
            return {
                "results": optimizations,
                "insights": [
                    "Optimizer status retrieved",
                    f"Optimizations applied: {len(optimizations.get('applied_optimizations', []))}",
                ],
            }
        except ImportError:
            return {
                "results": {"error": "Optimizer not available"},
                "insights": ["Optimizer not available"],
            }

    def execute_automatic_tool_application(
        self, context: "ToolExecutionContext"
    ) -> Dict[str, Any]:
        """
        Execute automatic tool application based on context analysis.

        This method automatically selects and applies the most appropriate
        tools based on the current development context and user needs.
        """
        try:
            # Analyze the context to determine what tools are needed
            trigger_analysis = self._analyze_triggers(context)

            if not trigger_analysis:
                return {
                    "executed": False,
                    "reason": "No applicable tools found for current context",
                    "tools_considered": [],
                }

            # Select appropriate tools based on triggers
            selected_tools = []
            for trigger in trigger_analysis:
                tool_name = trigger.get("tool")
                if tool_name:
                    selected_tools.append(tool_name)

            if not selected_tools:
                return {
                    "executed": False,
                    "reason": "No tools selected for execution",
                    "tools_considered": selected_tools,
                }

            # Execute the orchestration
            result = self.orchestrate_tools(context.user_request, context)

            return {
                "executed": True,
                "tools_applied": selected_tools,
                "orchestration_result": result,
                "context": {
                    "session_id": context.session_id,
                    "user_id": context.user_id,
                    "action_type": context.action_type,
                },
            }

        except Exception as e:
            return {"executed": False, "error": str(e), "tools_considered": []}


# Factory function for creating unified orchestrator
_orchestrator_instance: Optional[UnifiedToolOrchestrator] = None


def get_unified_tool_orchestrator(root_path: Path) -> UnifiedToolOrchestrator:
    """Get singleton instance of unified tool orchestrator."""
    global _orchestrator_instance

    if _orchestrator_instance is None:
        _orchestrator_instance = UnifiedToolOrchestrator(root_path)

    return _orchestrator_instance
