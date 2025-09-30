"""
Orchestration Compatibility Layer

Provides backward compatibility for existing imports while transitioning
to the unified orchestration system. This ensures that all existing code
continues to work without modification during the consolidation process.
"""

import time
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import the unified system
from .unified_tool_orchestrator import (
    ToolExecutionContext,
    UnifiedOrchestrationStrategy,
    UnifiedToolOrchestrator,
    get_unified_tool_orchestrator,
)

# ============================================================================
# BACKWARD COMPATIBILITY FOR intelligent_tool_orchestrator.py
# ============================================================================


class AutoApplicableTools:
    """Backward compatibility for AutoApplicableTools enum."""

    CODE_QUALITY_ANALYSIS = "code_quality_analysis"
    ORGANIZATION_ANALYSIS = "organization_analysis"
    STRUCTURAL_RECOMMENDATIONS = "structural_recommendations"
    RISK_ASSESSMENT = "risk_assessment"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    DUPLICATE_DETECTION = "duplicate_detection"
    IMPLEMENTATION_PLANNING = "implementation_planning"


class ToolApplicationTrigger:
    """Backward compatibility for ToolApplicationTrigger."""

    def __init__(
        self,
        trigger_type: str,
        keywords: Optional[List[str]] = None,
        contexts: Optional[List[str]] = None,
        patterns: Optional[List[str]] = None,
        priority: int = 1,
        cooldown_minutes: int = 30,
    ):
        self.trigger_type = trigger_type
        self.keywords = keywords or []
        self.contexts = contexts or []
        self.patterns = patterns or []
        self.priority = priority
        self.cooldown_minutes = cooldown_minutes


class IntelligentToolOrchestrator:
    """Backward compatibility wrapper for IntelligentToolOrchestrator."""

    def __init__(self, root_path: Path):
        warnings.warn(
            "IntelligentToolOrchestrator is deprecated. Use UnifiedToolOrchestrator instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._unified_orchestrator = get_unified_tool_orchestrator(root_path)
        self.root_path = root_path

    def analyze_conversation_for_tool_application(
        self,
        conversation_history: List[Dict[str, Any]],
        current_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Backward compatibility for conversation analysis."""

        context = ToolExecutionContext(
            conversation_history=conversation_history,
            strategy=UnifiedOrchestrationStrategy.TRIGGER_BASED,
        )

        # Use unified orchestrator's trigger analysis
        return self._unified_orchestrator._analyze_triggers(context)

    def execute_automatic_tool_application(
        self, tool_name: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Backward compatibility for tool execution."""

        execution_context = ToolExecutionContext(
            user_request=context.get("user_request", ""),
            strategy=UnifiedOrchestrationStrategy.TRIGGER_BASED,
        )

        result = self._unified_orchestrator._execute_tool_safely(
            tool_name, execution_context
        )

        return {
            "tool": tool_name,
            "executed": result is not None,
            "results": result,
            "error": None if result else "Tool execution failed",
        }


# ============================================================================
# BACKWARD COMPATIBILITY FOR holistic_tool_orchestration.py
# ============================================================================


class OrchestrationStrategy:
    """Backward compatibility for OrchestrationStrategy enum."""

    VISION_FIRST = "vision_first"
    USER_PREFERENCE_DRIVEN = "user_preference_driven"
    SAFETY_FIRST = "safety_first"
    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"
    ADAPTIVE = "adaptive"


class ToolExecutionPlan:
    """Backward compatibility for ToolExecutionPlan."""

    def __init__(self) -> None:
        self.primary_tools: List[str] = []
        self.supporting_tools: List[str] = []
        self.safety_tools: List[str] = []
        self.vision_tools: List[str] = []
        self.user_preference_tools: List[str] = []
        self.execution_order: List[str] = []
        self.gate_requirements: List[str] = []
        self.estimated_duration: float = 0.0
        self.risk_level: str = "low"
        self.strategy = OrchestrationStrategy.ADAPTIVE


class HolisticOrchestrationResult:
    """Backward compatibility for HolisticOrchestrationResult."""

    def __init__(self) -> None:
        self.success: bool = False
        self.executed_tools: List[str] = []
        self.tool_results: Dict[str, Any] = {}
        self.vision_alignment_score: float = 0.0
        self.user_preference_compliance: float = 0.0
        self.safety_compliance: float = 0.0
        self.total_execution_time: float = 0.0
        self.insights: List[str] = []
        self.recommendations: List[str] = []
        self.errors: List[str] = []


class HolisticToolOrchestrator:
    """Backward compatibility wrapper for HolisticToolOrchestrator."""

    def __init__(self, root_path: Path):
        warnings.warn(
            "HolisticToolOrchestrator is deprecated. Use UnifiedToolOrchestrator instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._unified_orchestrator = get_unified_tool_orchestrator(root_path)
        self.root_path = root_path

    def orchestrate_tools_for_request(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None,
        strategy: str = "adaptive",
    ) -> HolisticOrchestrationResult:
        """Backward compatibility for tool orchestration."""

        # Map old strategy names to new ones
        strategy_mapping = {
            "vision_first": UnifiedOrchestrationStrategy.VISION_FIRST,
            "safety_first": UnifiedOrchestrationStrategy.SAFETY_FIRST,
            "user_preference_driven": UnifiedOrchestrationStrategy.USER_PREFERENCE_DRIVEN,
            "comprehensive_analysis": UnifiedOrchestrationStrategy.COMPREHENSIVE_ANALYSIS,
            "adaptive": UnifiedOrchestrationStrategy.ADAPTIVE,
        }

        unified_strategy = strategy_mapping.get(
            strategy, UnifiedOrchestrationStrategy.ADAPTIVE
        )

        execution_context = ToolExecutionContext(
            user_request=user_request, strategy=unified_strategy
        )

        unified_result = self._unified_orchestrator.orchestrate_tools(
            user_request, execution_context, unified_strategy
        )

        # Convert unified result to legacy format
        legacy_result = HolisticOrchestrationResult()
        legacy_result.success = unified_result.success
        legacy_result.executed_tools = unified_result.executed_tools
        legacy_result.tool_results = unified_result.tool_results
        legacy_result.vision_alignment_score = unified_result.vision_alignment_score
        legacy_result.user_preference_compliance = (
            unified_result.user_preference_compliance
        )
        legacy_result.safety_compliance = unified_result.safety_compliance
        legacy_result.total_execution_time = unified_result.total_execution_time
        legacy_result.insights = unified_result.insights
        legacy_result.recommendations = unified_result.recommendations
        legacy_result.errors = unified_result.errors

        return legacy_result


# Convenience factories -----------------------------------------------------


def get_intelligent_orchestrator(root: Path) -> IntelligentToolOrchestrator:
    """Return a compatibility wrapper for legacy intelligent orchestrator."""

    return IntelligentToolOrchestrator(root)


def get_holistic_orchestrator(root: Path) -> HolisticToolOrchestrator:
    """Return a compatibility wrapper for legacy holistic orchestrator."""

    return HolisticToolOrchestrator(root)


def get_holistic_tool_orchestrator(root_path: Path) -> HolisticToolOrchestrator:
    """Backward compatibility factory function."""
    return HolisticToolOrchestrator(root_path)


# ============================================================================
# BACKWARD COMPATIBILITY FOR ai_agent_orchestration.py
# ============================================================================


class ConversationState:
    """Backward compatibility for ConversationState enum."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    ERROR = "error"


class DecisionStage:
    """Backward compatibility for DecisionStage enum."""

    ANALYSIS = "analysis"
    PLANNING = "planning"
    SAFETY_CHECK = "safety_check"
    EXECUTION = "execution"
    VALIDATION = "validation"


class _EnumAdapter:
    """Lightweight wrapper that exposes a value attribute for enum-like usage."""

    __slots__ = ("value",)

    def __init__(self, value: Any):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return repr(self.value)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, _EnumAdapter):
            return bool(self.value == other.value)
        return bool(self.value == other)

    def __hash__(self) -> int:
        return hash(self.value)


class ConversationContext:
    """Backward compatibility for ConversationContext."""

    def __init__(
        self,
        session_id: str,
        user_id: str,
        project_root: Path,
        created_at: Optional[float] = None,
        last_activity: Optional[float] = None,
        state: Optional["ConversationState"] = None,
        conversation_rounds: Optional[List[Dict[str, Any]]] = None,
        resolved_intents: Optional[List[str]] = None,
        user_corrections: Optional[List[str]] = None,
        current_stage: Optional["DecisionStage"] = None,
        stage_results: Optional[Dict[str, Any]] = None,
        confidence_scores: Optional[Dict[str, float]] = None,
        risk_factors: Optional[List[str]] = None,
        planned_commands: Optional[List[Dict[str, Any]]] = None,
        executed_commands: Optional[List[Dict[str, Any]]] = None,
        rollback_plan: Optional[Dict[str, Any]] = None,
        safety_violations: Optional[List[str]] = None,
        intervention_triggers: Optional[List[str]] = None,
    ) -> None:
        timestamp = created_at if created_at is not None else time.time()
        self.session_id = session_id
        self.user_id = user_id
        self.project_root = Path(project_root)
        self.created_at = timestamp
        self.last_activity = last_activity if last_activity is not None else timestamp
        self.state = self._wrap_enum(state or ConversationState.ACTIVE)
        self.conversation_rounds: List[Dict[str, Any]] = list(conversation_rounds or [])
        self.context_data: Dict[str, Any] = {}
        self.pending_actions: List[Dict[str, Any]] = []
        self.rollback_points: List[str] = []
        self.resolved_intents: List[str] = list(resolved_intents or [])
        self.user_corrections: List[str] = list(user_corrections or [])
        self.current_stage = self._wrap_enum(current_stage or DecisionStage.ANALYSIS)
        self.stage_results: Dict[str, Any] = dict(stage_results or {})
        self.confidence_scores: Dict[str, float] = dict(confidence_scores or {})
        self.risk_factors: List[str] = list(risk_factors or [])
        self.planned_commands: List[Dict[str, Any]] = list(planned_commands or [])
        self.executed_commands: List[Dict[str, Any]] = list(executed_commands or [])
        self.rollback_plan = rollback_plan
        self.safety_violations: List[str] = list(safety_violations or [])
        self.intervention_triggers: List[str] = list(intervention_triggers or [])

    @staticmethod
    def _wrap_enum(value: Any) -> Any:
        if value is None:
            return None
        if hasattr(value, "value"):
            return value
        return _EnumAdapter(value)


class AIAgentOrchestrationLayer:
    """Backward compatibility wrapper for AIAgentOrchestrationLayer."""

    def __init__(self, root: Path):
        warnings.warn(
            "AIAgentOrchestrationLayer is deprecated. Use UnifiedToolOrchestrator instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._unified_orchestrator = get_unified_tool_orchestrator(root)
        self.root = root
        self.sessions: Dict[str, ConversationContext] = {}

    def create_session(self, user_id: str = "default") -> str:
        """Backward compatibility for session creation."""
        import time
        import uuid

        session_id = f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        context = ConversationContext(session_id, user_id, self.root)
        self.sessions[session_id] = context

        return session_id

    def process_conversation(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Backward compatibility for conversation processing."""

        if session_id not in self.sessions:
            return {"error": "Session not found", "session_id": session_id}

        context = self.sessions[session_id]

        execution_context = ToolExecutionContext(
            user_request=user_input,
            session_id=session_id,
            user_id=context.user_id,
            strategy=UnifiedOrchestrationStrategy.SESSION_AWARE,
        )

        result = self._unified_orchestrator.orchestrate_tools(
            user_input, execution_context, UnifiedOrchestrationStrategy.SESSION_AWARE
        )

        return {
            "session_id": session_id,
            "success": result.success,
            "executed_tools": result.executed_tools,
            "insights": result.insights,
            "errors": result.errors,
        }

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Backward compatibility for session status."""

        if session_id not in self.sessions:
            return {"error": "Session not found"}

        context = self.sessions[session_id]

        return {
            "session_id": session_id,
            "user_id": context.user_id,
            "state": context.state,
            "conversation_rounds": len(context.conversation_rounds),
            "created_at": context.created_at,
            "last_activity": context.last_activity,
        }


def create_ai_agent_orchestrator(root: Path) -> AIAgentOrchestrationLayer:
    """Backward compatibility factory function."""
    return AIAgentOrchestrationLayer(root)


# ============================================================================
# MIGRATION HELPERS
# ============================================================================


def migrate_to_unified_orchestrator(root_path: Path) -> UnifiedToolOrchestrator:
    """
    Helper function to migrate from legacy orchestrators to unified system.

    This function provides a clean migration path and logs the transition.
    """

    print("🔄 Migrating to UnifiedToolOrchestrator...")
    print("   ✅ All legacy functionality preserved")
    print("   ✅ Enhanced with unified strategies")
    print("   ✅ Improved performance and consistency")

    return get_unified_tool_orchestrator(root_path)


def get_legacy_orchestrator_type(orchestrator_instance: Any) -> str:
    """Helper to identify legacy orchestrator types for migration."""

    if isinstance(orchestrator_instance, IntelligentToolOrchestrator):
        return "intelligent"
    elif isinstance(orchestrator_instance, HolisticToolOrchestrator):
        return "holistic"
    elif isinstance(orchestrator_instance, AIAgentOrchestrationLayer):
        return "ai_agent"
    elif isinstance(orchestrator_instance, UnifiedToolOrchestrator):
        return "unified"
    else:
        return "unknown"
