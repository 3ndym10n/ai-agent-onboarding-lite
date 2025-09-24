"""
Unified Tool Orchestrator

Consolidates functionality from:
- intelligent_tool_orchestrator.py (trigger-based execution, learning)
- holistic_tool_orchestration.py (strategy-based coordination, vision alignment)
- ai_agent_orchestration.py (session management, decision pipeline)

This unified system provides comprehensive tool orchestration with safety,
vision alignment, user preferences, and intelligent automation.
"""

import time
import threading
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Core tool imports
from .pattern_recognition_system import PatternRecognitionSystem
from .tool_usage_tracker import get_tool_tracker
from .user_preference_learning import UserPreferenceLearningSystem

# Discovery and metadata
from .comprehensive_tool_discovery import get_comprehensive_tool_discovery

# Session and context management
from .session_storage import SessionStorageManager
from .enhanced_conversation_context import get_enhanced_context_manager
from .mandatory_tool_consultation_gate import get_mandatory_gate

# Safety and alignment
from .ai_agent_wrapper import IASGuardrails


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
    rollback_enabled: bool = True
    checkpoint_id: Optional[str] = None


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
        
        # Learning and intelligence systems
        self.pattern_system = PatternRecognitionSystem(root_path)
        self.user_preference_system = UserPreferenceLearningSystem(root_path)
        
        # Session and context management
        self.session_storage = SessionStorageManager(root_path)
        self.enhanced_context_manager = get_enhanced_context_manager(root_path)
        
        # Safety and alignment systems
        self.guardrails = IASGuardrails()
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
    
    def _initialize_unified_triggers(self):
        """Initialize unified trigger system combining all orchestration approaches."""
        
        # Code Quality Analysis - Enhanced with session awareness
        self.tool_triggers[UnifiedToolCategory.CODE_QUALITY.value] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["cleanup", "refactor", "quality", "dead code", "unused", "optimize"],
                priority=4,
                cooldown_minutes=60,
                vision_alignment_required=True
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["refactoring", "cleanup", "code_changes"],
                priority=5,
                cooldown_minutes=30,
                requires_user_confirmation=True
            ),
            ToolExecutionTrigger(
                trigger_type="session_event",
                session_events=["large_code_change", "multiple_file_edit"],
                priority=4,
                cooldown_minutes=45
            )
        ]
        
        # File Organization - Strategy-aware triggers
        self.tool_triggers[UnifiedToolCategory.FILE_ORGANIZATION.value] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["organize", "structure", "layout", "reorganize", "move files"],
                priority=3,
                cooldown_minutes=45,
                vision_alignment_required=True
            ),
            ToolExecutionTrigger(
                trigger_type="pattern",
                patterns=["file.*move", "directory.*restructure", "organize.*files"],
                priority=4,
                cooldown_minutes=30
            )
        ]
        
        # Risk Assessment - Safety-first approach
        self.tool_triggers[UnifiedToolCategory.RISK_ASSESSMENT.value] = [
            ToolExecutionTrigger(
                trigger_type="keyword",
                keywords=["risk", "dangerous", "breaking", "impact", "safety"],
                priority=5,
                cooldown_minutes=10,
                requires_user_confirmation=True,
                vision_alignment_required=True
            ),
            ToolExecutionTrigger(
                trigger_type="context",
                contexts=["breaking_changes", "system_changes", "major_refactoring"],
                priority=5,
                cooldown_minutes=5,
                requires_user_confirmation=True
            )
        ]
        
        # Session Management triggers
        self.tool_triggers[UnifiedToolCategory.SESSION_MANAGEMENT.value] = [
            ToolExecutionTrigger(
                trigger_type="session_event",
                session_events=["session_start", "context_switch", "user_change"],
                priority=2,
                cooldown_minutes=5
            )
        ]
    
    def orchestrate_tools(
        self,
        user_request: str,
        context: Optional[ToolExecutionContext] = None,
        strategy: UnifiedOrchestrationStrategy = UnifiedOrchestrationStrategy.ADAPTIVE,
        session_id: Optional[str] = None
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
                user_request=user_request,
                strategy=strategy,
                session_id=session_id
            )
        
        # Track orchestration start
        self.tool_tracker.track_tool_usage(
            tool_name="unified_tool_orchestration",
            tool_type="Tool_Orchestration",
            parameters={
                "user_request": user_request[:100],
                "strategy": strategy.value,
                "session_id": session_id
            },
            result="started"
        )
        
        try:
            # Step 1: Initialize tool discovery if needed
            if not self.discovery_result:
                self.discovery_result = self.discovery.discover_all_tools()
            
            # Step 2: Route to appropriate orchestration approach
            trigger_strategies = [
                UnifiedOrchestrationStrategy.TRIGGER_BASED,
                UnifiedOrchestrationStrategy.LEARNING_DRIVEN
            ]
            holistic_strategies = [
                UnifiedOrchestrationStrategy.VISION_FIRST,
                UnifiedOrchestrationStrategy.COMPREHENSIVE_ANALYSIS
            ]
            session_strategies = [
                UnifiedOrchestrationStrategy.SESSION_AWARE,
                UnifiedOrchestrationStrategy.ROLLBACK_SAFE
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
                    "strategy": strategy.value
                },
                result="completed"
            )
            
        except Exception as e:
            result.errors.append(f"Unified orchestration failed: {str(e)}")
            result.total_execution_time = time.time() - start_time
            
            # Track failure
            self.tool_tracker.track_tool_usage(
                tool_name="unified_tool_orchestration",
                tool_type="Tool_Orchestration",
                parameters={"error": str(e), "execution_time": result.total_execution_time},
                result="failed"
            )
        
        return result
    
    def _execute_intelligent_orchestration(self, context: ToolExecutionContext) -> UnifiedOrchestrationResult:
        """Execute intelligent/trigger-based orchestration (from intelligent_tool_orchestrator.py)."""
        
        result = UnifiedOrchestrationResult()
        
        # Analyze conversation for trigger matches
        trigger_analysis = self._analyze_triggers(context)
        
        # Execute tools based on triggers
        for tool_recommendation in trigger_analysis:
            tool_name = tool_recommendation["tool"]
            confidence = tool_recommendation["confidence"]
            
            if confidence >= 0.3:  # Threshold for execution
                tool_result = self._execute_tool_safely(tool_name, context)
                if tool_result:
                    result.executed_tools.append(tool_name)
                    result.tool_results[tool_name] = tool_result
                    result.insights.extend(tool_result.get("insights", []))
        
        return result
    
    def _execute_holistic_orchestration(self, context: ToolExecutionContext) -> UnifiedOrchestrationResult:
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
            if tool_result:
                result.executed_tools.append(tool_name)
                result.tool_results[tool_name] = tool_result
        
        return result
    
    def _execute_session_orchestration(self, context: ToolExecutionContext) -> UnifiedOrchestrationResult:
        """Execute session-aware orchestration (from ai_agent_orchestration.py)."""
        
        result = UnifiedOrchestrationResult()
        
        # Session management
        if context.session_id:
            session_context = self._get_or_create_session(context.session_id, context.user_id)
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
            if tool_result:
                result.executed_tools.append(tool_name)
                result.tool_results[tool_name] = tool_result
        
        return result
    
    def _execute_adaptive_orchestration(self, context: ToolExecutionContext) -> UnifiedOrchestrationResult:
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
    
    # Placeholder methods for core functionality - to be implemented
    def _analyze_triggers(self, context: ToolExecutionContext) -> List[Dict[str, Any]]:
        """Analyze triggers from conversation and context."""
        # Implementation from intelligent_tool_orchestrator.py
        return []
    
    def _execute_tool_safely(self, tool_name: str, context: ToolExecutionContext) -> Optional[Dict[str, Any]]:
        """Execute a tool with safety checks and error handling."""
        # Consolidated implementation from all three orchestrators
        return {"executed": True, "insights": [f"Tool {tool_name} executed successfully"]}
    
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
    
    def _merge_results(self, result1: UnifiedOrchestrationResult, result2: UnifiedOrchestrationResult) -> UnifiedOrchestrationResult:
        """Merge two orchestration results."""
        result1.executed_tools.extend(result2.executed_tools)
        result1.tool_results.update(result2.tool_results)
        result1.insights.extend(result2.insights)
        result1.recommendations.extend(result2.recommendations)
        result1.errors.extend(result2.errors)
        result1.warnings.extend(result2.warnings)
        
        # Take maximum scores
        result1.vision_alignment_score = max(result1.vision_alignment_score, result2.vision_alignment_score)
        result1.user_preference_compliance = max(result1.user_preference_compliance, result2.user_preference_compliance)
        result1.safety_compliance = min(result1.safety_compliance, result2.safety_compliance)  # Take minimum for safety
        
        return result1
    
    def _learn_from_execution(self, context: ToolExecutionContext, result: UnifiedOrchestrationResult):
        """Learn from execution for future improvements."""
        # Implementation from intelligent_tool_orchestrator.py learning system
        pass
    
    def _load_user_preferences(self) -> Dict[str, Any]:
        """Load user preferences."""
        return {
            "communication_style": "concise",
            "tool_preferences": ["code_quality", "file_organization"],
            "safety_level": "high",
            "vision_alignment_required": True
        }
    
    def _load_vision_context(self) -> Dict[str, Any]:
        """Load vision context."""
        return {
            "project_goals": ["build_robust_ai_system", "ensure_safety"],
            "non_goals": ["quick_hacks", "unsafe_operations"],
            "risk_appetite": "low"
        }
    
    def _load_safety_gates(self) -> Dict[str, Any]:
        """Load safety gate configurations."""
        return {
            "cleanup_gate": {"enabled": True, "threshold": 0.9},
            "vision_gate": {"enabled": True, "threshold": 0.8},
            "safety_gate": {"enabled": True, "threshold": 0.95}
        }


# Factory function for creating unified orchestrator
_orchestrator_instance: Optional[UnifiedToolOrchestrator] = None

def get_unified_tool_orchestrator(root_path: Path) -> UnifiedToolOrchestrator:
    """Get singleton instance of unified tool orchestrator."""
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        _orchestrator_instance = UnifiedToolOrchestrator(root_path)
    
    return _orchestrator_instance
