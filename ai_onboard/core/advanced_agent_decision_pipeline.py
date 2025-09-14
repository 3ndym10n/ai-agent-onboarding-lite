"""
Advanced Agent Decision Pipeline (T9) - Sophisticated decision - making system for AI agents.

This module provides an enhanced decision pipeline that integrates with conversation context,
user preferences, project history, and advanced reasoning capabilities to make intelligent
decisions about AI agent actions.
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import alignment
from .ai_agent_orchestration import (
    ConversationContext,
)
from .enhanced_conversation_context import get_enhanced_context_manager
from .unified_metrics_collector import (
    MetricCategory,
    MetricEvent,
    MetricSource,
    get_unified_metrics_collector,
)
from .user_preference_learning import get_user_preference_learning_system


class DecisionComplexity(Enum):
    """Complexity levels for decision - making."""

    SIMPLE = "simple"  # Single command, low risk
    MODERATE = "moderate"  # Multiple commands, medium risk
    COMPLEX = "complex"  # Complex workflow, high risk
    CRITICAL = "critical"  # System - level changes, critical risk


class DecisionConfidence(Enum):
    """Confidence levels for decisions."""

    VERY_LOW = "very_low"  # 0.0 - 0.3
    LOW = "low"  # 0.3 - 0.5
    MEDIUM = "medium"  # 0.5 - 0.7
    HIGH = "high"  # 0.7 - 0.9
    VERY_HIGH = "very_high"  # 0.9 - 1.0


class DecisionOutcome(Enum):
    """Possible decision outcomes."""

    PROCEED = "proceed"  # Execute immediately
    PROCEED_WITH_MONITORING = (
        "proceed_with_monitoring"  # Execute with safety monitoring
    )
    REQUEST_CONFIRMATION = "request_confirmation"  # Ask user for confirmation
    REQUEST_CLARIFICATION = "request_clarification"  # Need more information
    ESCALATE = "escalate"  # Escalate to human review
    REJECT = "reject"  # Reject the request
    DEFER = "defer"  # Defer to later


@dataclass
class DecisionContext:
    """Enhanced context for decision - making."""

    # Basic context
    session_id: str
    user_id: str
    agent_id: str
    decision_id: str
    created_at: float

    # Input context
    user_input: str
    resolved_intents: List[Tuple[str, float]]
    conversation_history: List[Dict[str, Any]]

    # Enhanced context
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    project_context: Dict[str, Any] = field(default_factory=dict)
    historical_patterns: Dict[str, Any] = field(default_factory=dict)
    cross_session_insights: Dict[str, Any] = field(default_factory=dict)

    # Decision factors
    complexity_level: DecisionComplexity = DecisionComplexity.SIMPLE
    risk_factors: List[str] = field(default_factory=list)
    confidence_factors: Dict[str, float] = field(default_factory=dict)

    # Constraints
    time_constraints: Optional[Dict[str, Any]] = None
    safety_constraints: List[str] = field(default_factory=list)
    user_constraints: List[str] = field(default_factory=list)


@dataclass
class DecisionResult:
    """Result of a decision pipeline execution."""

    decision_id: str
    outcome: DecisionOutcome
    confidence: float
    confidence_level: DecisionConfidence

    # Decision details
    reasoning: str
    alternative_options: List[Dict[str, Any]] = field(default_factory=list)
    execution_plan: Optional[Dict[str, Any]] = None
    monitoring_plan: Optional[Dict[str, Any]] = None

    # Metadata
    processing_time_ms: float = 0.0
    pipeline_stages: Dict[str, Any] = field(default_factory=dict)
    decision_factors: Dict[str, Any] = field(default_factory=dict)

    # Follow - up actions
    requires_confirmation: bool = False
    confirmation_message: Optional[str] = None
    clarification_questions: List[str] = field(default_factory=list)
    escalation_reason: Optional[str] = None


class ContextualReasoningEngine:
    """Advanced reasoning engine that considers context, history, and patterns."""

    def __init__(self, root: Path):
        self.root = root
        self.enhanced_context = get_enhanced_context_manager(root)
        self.preference_system = get_user_preference_learning_system(root)
        self.metrics_collector = get_unified_metrics_collector(root)

    def analyze_decision_context(self, context: DecisionContext) -> Dict[str, Any]:
        """Analyze the full context for decision - making."""
        analysis = {
            "user_behavior_analysis": self._analyze_user_behavior(context),
            "project_context_analysis": self._analyze_project_context(context),
            "historical_pattern_analysis": self._analyze_historical_patterns(context),
            "risk_assessment": self._assess_contextual_risks(context),
            "complexity_assessment": self._assess_complexity(context),
        }

        return analysis

    def _analyze_user_behavior(self, context: DecisionContext) -> Dict[str, Any]:
        """Analyze user behavior patterns and preferences."""
        try:
            # Get user profile from preference system
            user_profile = self.preference_system.get_user_profile_summary(
                context.user_id
            )

            # Get cross - session context
            continuity_summary = self.enhanced_context.get_context_continuity_summary(
                context.user_id
            )

            if "error" in continuity_summary:
                return {"error": continuity_summary["error"]}

            behavior_analysis = {
                "experience_level": continuity_summary["user_profile"][
                    "experience_level"
                ],
                "communication_style": continuity_summary["user_profile"][
                    "communication_style"
                ],
                "collaboration_mode": continuity_summary["user_profile"][
                    "collaboration_mode"
                ],
                "preferred_commands": continuity_summary["continuity_metrics"][
                    "preferred_commands"
                ],
                "avg_session_length": continuity_summary["continuity_metrics"][
                    "avg_session_length"
                ],
                "patterns": {
                    "prefers_detailed_explanations": continuity_summary["user_profile"][
                        "communication_style"
                    ]
                    == "detailed",
                    "comfortable_with_automation": continuity_summary["user_profile"][
                        "collaboration_mode"
                    ]
                    in ["autonomous", "collaborative"],
                    "experienced_user": continuity_summary["user_profile"][
                        "experience_level"
                    ]
                    in ["intermediate", "expert"],
                },
            }

            return behavior_analysis

        except Exception as e:
            return {"error": str(e)}

    def _analyze_project_context(self, context: DecisionContext) -> Dict[str, Any]:
        """Analyze current project context and state."""
        try:
            # Get project state
            from . import state, telemetry

            project_state = state.load(self.root)
            latest_metrics = telemetry.last_run(self.root)

            # Get alignment data
            alignment_data = alignment.preview(self.root)

            project_analysis = {
                "current_phase": project_state.get("phase", "unknown"),
                "project_health": (
                    latest_metrics.get("health_score", 0.0) if latest_metrics else 0.0
                ),
                "alignment_confidence": alignment_data.get("confidence", 0.0),
                "recent_activity": (
                    latest_metrics.get("recent_commands", []) if latest_metrics else []
                ),
                "project_maturity": self._assess_project_maturity(
                    project_state, latest_metrics
                ),
            }

            return project_analysis

        except Exception as e:
            return {"error": str(e)}

    def _analyze_historical_patterns(self, context: DecisionContext) -> Dict[str, Any]:
        """Analyze historical patterns and outcomes."""
        try:
            # Get relevant memories from enhanced context
            session = self.enhanced_context.session_storage.load_session(
                context.session_id
            )
            if not session:
                return {"error": "Session not found"}

            relevant_memories = self.enhanced_context._get_relevant_memories(
                context.session_id, context.user_id
            )

            # Analyze patterns
            successful_patterns = []
            failure_patterns = []

            for memory in relevant_memories:
                if memory.successful_patterns:
                    successful_patterns.extend(memory.successful_patterns)
                if memory.resolved_issues:
                    failure_patterns.extend(memory.resolved_issues)

            pattern_analysis = {
                "successful_patterns": successful_patterns,
                "common_issues": failure_patterns,
                "pattern_confidence": len(successful_patterns)
                / max(len(relevant_memories), 1),
                "historical_success_rate": self._calculate_historical_success_rate(
                    context.user_id
                ),
            }

            return pattern_analysis

        except Exception as e:
            return {"error": str(e)}

    def _assess_contextual_risks(self, context: DecisionContext) -> Dict[str, Any]:
        """Assess risks based on context and history."""
        risks = []
        risk_score = 0.0

        # Check for high - risk intents
        high_risk_intents = [
            "system_modification",
            "file_deletion",
            "configuration_change",
        ]
        for intent, confidence in context.resolved_intents:
            if intent in high_risk_intents:
                risks.append(f"High - risk intent: {intent}")
                risk_score += 0.3

        # Check user experience level
        if context.user_preferences.get("experience_level") == "new":
            risks.append("New user - increased supervision needed")
            risk_score += 0.2

        # Check project context
        if context.project_context.get("project_health", 1.0) < 0.5:
            risks.append("Low project health - careful execution needed")
            risk_score += 0.2

        # Check for conflicting intents
        if len(context.resolved_intents) > 3:
            risks.append("Multiple conflicting intents detected")
            risk_score += 0.1

        return {
            "risk_factors": risks,
            "risk_score": min(risk_score, 1.0),
            "risk_level": (
                "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low"
            ),
        }

    def _assess_complexity(self, context: DecisionContext) -> DecisionComplexity:
        """Assess the complexity of the decision."""
        complexity_score = 0

        # Number of intents
        complexity_score += len(context.resolved_intents) * 0.1

        # Risk factors
        complexity_score += len(context.risk_factors) * 0.2

        # User experience (inverse)
        if context.user_preferences.get("experience_level") == "new":
            complexity_score += 0.3

        # Project context complexity
        if context.project_context.get("project_health", 1.0) < 0.5:
            complexity_score += 0.2

        if complexity_score > 0.8:
            return DecisionComplexity.CRITICAL
        elif complexity_score > 0.6:
            return DecisionComplexity.COMPLEX
        elif complexity_score > 0.3:
            return DecisionComplexity.MODERATE
        else:
            return DecisionComplexity.SIMPLE

    def _assess_project_maturity(
        self, project_state: Dict[str, Any], metrics: Optional[Dict[str, Any]]
    ) -> str:
        """Assess project maturity level."""
        if not metrics:
            return "unknown"

        commands_run = len(metrics.get("recent_commands", []))
        health_score = metrics.get("health_score", 0.0)

        if commands_run > 20 and health_score > 0.8:
            return "mature"
        elif commands_run > 10 and health_score > 0.6:
            return "developing"
        elif commands_run > 5:
            return "early"
        else:
            return "new"

    def _calculate_historical_success_rate(self, user_id: str) -> float:
        """Calculate historical success rate for user."""
        try:
            # This would analyze historical command success / failure rates
            # For now, return a placeholder based on user experience
            user_sessions = self.enhanced_context.session_storage.get_user_sessions(
                user_id
            )

            if not user_sessions:
                return 0.5  # Default for new users

            # Simple calculation based on session count (more sessions = more experience)
            session_count = len(user_sessions)
            return min(0.5 + (session_count * 0.05), 0.95)

        except Exception:
            return 0.5


class AdvancedDecisionPipeline:
    """Advanced decision pipeline for AI agents with sophisticated reasoning capabilities."""

    def __init__(self, root: Path):
        self.root = root
        self.reasoning_engine = ContextualReasoningEngine(root)
        self.enhanced_context = get_enhanced_context_manager(root)
        self.preference_system = get_user_preference_learning_system(root)
        self.metrics_collector = get_unified_metrics_collector(root)

        # Decision pipeline configuration
        self.confidence_thresholds = {
            DecisionComplexity.SIMPLE: 0.6,
            DecisionComplexity.MODERATE: 0.7,
            DecisionComplexity.COMPLEX: 0.8,
            DecisionComplexity.CRITICAL: 0.9,
        }

        # Decision strategies
        self.decision_strategies = {
            DecisionComplexity.SIMPLE: self._simple_decision_strategy,
            DecisionComplexity.MODERATE: self._moderate_decision_strategy,
            DecisionComplexity.COMPLEX: self._complex_decision_strategy,
            DecisionComplexity.CRITICAL: self._critical_decision_strategy,
        }

    def process_decision(
        self,
        session_id: str,
        user_id: str,
        agent_id: str,
        user_input: str,
        resolved_intents: List[Tuple[str, float]],
        conversation_context: ConversationContext,
    ) -> DecisionResult:
        """Process a decision through the advanced pipeline."""

        start_time = time.time()
        decision_id = f"decision_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        # Create decision context
        decision_context = DecisionContext(
            session_id=session_id,
            user_id=user_id,
            agent_id=agent_id,
            decision_id=decision_id,
            created_at=time.time(),
            user_input=user_input,
            resolved_intents=resolved_intents,
            conversation_history=conversation_context.conversation_rounds,
        )

        pipeline_stages = {}

        try:
            # Stage 1: Context Enhancement
            pipeline_stages["context_enhancement"] = self._enhance_decision_context(
                decision_context
            )

            # Stage 2: Contextual Analysis
            pipeline_stages["contextual_analysis"] = (
                self.reasoning_engine.analyze_decision_context(decision_context)
            )

            # Stage 3: Complexity Assessment
            decision_context.complexity_level = (
                self.reasoning_engine._assess_complexity(decision_context)
            )
            pipeline_stages["complexity_assessment"] = {
                "complexity_level": decision_context.complexity_level.value
            }

            # Stage 4: Confidence Calculation
            confidence_result = self._calculate_advanced_confidence(
                decision_context, pipeline_stages
            )
            pipeline_stages["confidence_calculation"] = confidence_result

            # Stage 5: Decision Strategy
            strategy_result = self._apply_decision_strategy(
                decision_context, confidence_result["confidence"]
            )
            pipeline_stages["decision_strategy"] = strategy_result

            # Stage 6: Execution Planning
            if strategy_result["outcome"] in [
                DecisionOutcome.PROCEED,
                DecisionOutcome.PROCEED_WITH_MONITORING,
            ]:
                execution_plan = self._create_execution_plan(
                    decision_context, resolved_intents
                )
                pipeline_stages["execution_planning"] = execution_plan
            else:
                execution_plan = None

            # Stage 7: Monitoring Planning
            monitoring_plan = None
            if strategy_result["outcome"] == DecisionOutcome.PROCEED_WITH_MONITORING:
                monitoring_plan = self._create_monitoring_plan(decision_context)
                pipeline_stages["monitoring_planning"] = monitoring_plan

            # Create decision result
            result = DecisionResult(
                decision_id=decision_id,
                outcome=strategy_result["outcome"],
                confidence=confidence_result["confidence"],
                confidence_level=self._get_confidence_level(
                    confidence_result["confidence"]
                ),
                reasoning=strategy_result["reasoning"],
                alternative_options=strategy_result.get("alternatives", []),
                execution_plan=execution_plan,
                monitoring_plan=monitoring_plan,
                processing_time_ms=(time.time() - start_time) * 1000,
                pipeline_stages=pipeline_stages,
                decision_factors=confidence_result["factors"],
                requires_confirmation=strategy_result.get(
                    "requires_confirmation", False
                ),
                confirmation_message=strategy_result.get("confirmation_message"),
                clarification_questions=strategy_result.get(
                    "clarification_questions", []
                ),
                escalation_reason=strategy_result.get("escalation_reason"),
            )

            # Record decision metrics
            self._record_decision_metrics(decision_context, result)

            return result

        except Exception as e:
            # Handle pipeline errors gracefully
            error_result = DecisionResult(
                decision_id=decision_id,
                outcome=DecisionOutcome.ESCALATE,
                confidence=0.0,
                confidence_level=DecisionConfidence.VERY_LOW,
                reasoning=f"Pipeline error: {str(e)}",
                processing_time_ms=(time.time() - start_time) * 1000,
                pipeline_stages=pipeline_stages,
                escalation_reason=f"Decision pipeline error: {str(e)}",
            )

            self._record_decision_metrics(decision_context, error_result)
            return error_result

    def _enhance_decision_context(self, context: DecisionContext) -> Dict[str, Any]:
        """Enhance decision context with additional information."""
        enhancement_result = {}

        # Get enhanced session context
        enhanced_session = self.enhanced_context.enhance_session_context(
            context.session_id
        )
        if "error" not in enhanced_session:
            context.cross_session_insights = enhanced_session.get(
                "cross_session_insights", {}
            )
            context.user_preferences = enhanced_session["cross_session_insights"]
            enhancement_result["enhanced_session"] = True
        else:
            enhancement_result["enhanced_session_error"] = enhanced_session["error"]

        # Get project context
        try:
            from . import state

            project_state = state.load(self.root)
            context.project_context = project_state
            enhancement_result["project_context"] = True
        except Exception as e:
            enhancement_result["project_context_error"] = str(e)

        return enhancement_result

    def _calculate_advanced_confidence(
        self, context: DecisionContext, pipeline_stages: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate advanced confidence score considering all factors."""

        factors = {}

        # Base confidence from intent clarity
        intent_confidence = sum(score for _, score in context.resolved_intents) / max(
            len(context.resolved_intents), 1
        )
        factors["intent_clarity"] = intent_confidence

        # User behavior factor
        behavior_analysis = pipeline_stages.get("contextual_analysis", {}).get(
            "user_behavior_analysis", {}
        )
        if "error" not in behavior_analysis:
            experience_bonus = {
                "expert": 0.2,
                "intermediate": 0.1,
                "beginner": 0.05,
                "new": 0.0,
            }.get(behavior_analysis.get("experience_level", "new"), 0.0)
            factors["user_experience"] = experience_bonus
        else:
            factors["user_experience"] = 0.0

        # Project context factor
        project_analysis = pipeline_stages.get("contextual_analysis", {}).get(
            "project_context_analysis", {}
        )
        if "error" not in project_analysis:
            project_health = project_analysis.get("project_health", 0.5)
            alignment_confidence = project_analysis.get("alignment_confidence", 0.5)
            factors["project_health"] = project_health * 0.2
            factors["alignment"] = alignment_confidence * 0.2
        else:
            factors["project_health"] = 0.0
            factors["alignment"] = 0.0

        # Historical pattern factor
        pattern_analysis = pipeline_stages.get("contextual_analysis", {}).get(
            "historical_pattern_analysis", {}
        )
        if "error" not in pattern_analysis:
            historical_success = pattern_analysis.get("historical_success_rate", 0.5)
            pattern_confidence = pattern_analysis.get("pattern_confidence", 0.5)
            factors["historical_success"] = historical_success * 0.15
            factors["pattern_matching"] = pattern_confidence * 0.1
        else:
            factors["historical_success"] = 0.0
            factors["pattern_matching"] = 0.0

        # Risk penalty
        risk_assessment = pipeline_stages.get("contextual_analysis", {}).get(
            "risk_assessment", {}
        )
        risk_penalty = risk_assessment.get("risk_score", 0.0) * 0.3
        factors["risk_penalty"] = -risk_penalty

        # Calculate overall confidence
        overall_confidence = sum(factors.values())
        overall_confidence = max(0.0, min(1.0, overall_confidence))

        return {
            "confidence": overall_confidence,
            "factors": factors,
            "breakdown": {
                "base_intent_confidence": intent_confidence,
                "experience_bonus": factors.get("user_experience", 0.0),
                "project_factors": factors.get("project_health", 0.0)
                + factors.get("alignment", 0.0),
                "historical_factors": factors.get("historical_success", 0.0)
                + factors.get("pattern_matching", 0.0),
                "risk_penalty": factors.get("risk_penalty", 0.0),
            },
        }

    def _apply_decision_strategy(
        self, context: DecisionContext, confidence: float
    ) -> Dict[str, Any]:
        """Apply appropriate decision strategy based on complexity and confidence."""
        strategy_func = self.decision_strategies[context.complexity_level]
        return strategy_func(context, confidence)

    def _simple_decision_strategy(
        self, context: DecisionContext, confidence: float
    ) -> Dict[str, Any]:
        """Strategy for simple decisions."""
        threshold = self.confidence_thresholds[DecisionComplexity.SIMPLE]

        if confidence >= threshold:
            return {
                "outcome": DecisionOutcome.PROCEED,
                "reasoning": f"Simple decision with high confidence ({confidence:.2f}). Proceeding directly.",
                "alternatives": [],
            }
        elif confidence >= 0.4:
            return {
                "outcome": DecisionOutcome.REQUEST_CONFIRMATION,
                "reasoning": f"Simple decision with moderate confidence ({confidence:.2f}). Requesting confirmation.",
                "requires_confirmation": True,
                "confirmation_message": "I understand what you want to do. Should I proceed?",
            }
        else:
            return {
                "outcome": DecisionOutcome.REQUEST_CLARIFICATION,
                "reasoning": f"Simple decision with low confidence ({confidence:.2f}). Need clarification.",
                "clarification_questions": [
                    "Can you provide more details about what you want to accomplish?",
                    "Which specific aspect is most important to you?",
                ],
            }

    def _moderate_decision_strategy(
        self, context: DecisionContext, confidence: float
    ) -> Dict[str, Any]:
        """Strategy for moderate complexity decisions."""
        threshold = self.confidence_thresholds[DecisionComplexity.MODERATE]

        if confidence >= threshold:
            return {
                "outcome": DecisionOutcome.PROCEED_WITH_MONITORING,
                "reasoning": f"Moderate decision with sufficient confidence ({confidence:.2f}). Proceeding with monitoring.",
                "alternatives": [],
            }
        elif confidence >= 0.5:
            return {
                "outcome": DecisionOutcome.REQUEST_CONFIRMATION,
                "reasoning": f"Moderate decision needs confirmation ({confidence:.2f}).",
                "requires_confirmation": True,
                "confirmation_message": "This involves multiple steps. Here's what I plan to do:\n"
                + self._format_planned_actions(context)
                + "\nShould I proceed?",
            }
        else:
            return {
                "outcome": DecisionOutcome.REQUEST_CLARIFICATION,
                "reasoning": f"Moderate decision requires more information ({confidence:.2f}).",
                "clarification_questions": [
                    "What is your primary goal with this request?",
                    "Are there any specific constraints I should be aware of?",
                    "What would success look like for you?",
                ],
            }

    def _complex_decision_strategy(
        self, context: DecisionContext, confidence: float
    ) -> Dict[str, Any]:
        """Strategy for complex decisions."""
        threshold = self.confidence_thresholds[DecisionComplexity.COMPLEX]

        if confidence >= threshold:
            return {
                "outcome": DecisionOutcome.REQUEST_CONFIRMATION,
                "reasoning": f"Complex decision requires confirmation even with high confidence ({confidence:.2f}).",
                "requires_confirmation": True,
                "confirmation_message": "This is a complex operation that will:\n"
                + self._format_planned_actions(context)
                + "\nI'll monitor each step carefully. Proceed?",
            }
        elif confidence >= 0.6:
            return {
                "outcome": DecisionOutcome.REQUEST_CLARIFICATION,
                "reasoning": f"Complex decision needs more clarity ({confidence:.2f}).",
                "clarification_questions": [
                    "Can you break down your request into specific steps?",
                    "What are the most critical parts of this operation?",
                    "Are there any parts you'd prefer to handle manually?",
                ],
            }
        else:
            return {
                "outcome": DecisionOutcome.ESCALATE,
                "reasoning": f"Complex decision with low confidence ({confidence:.2f}) requires human review.",
                "escalation_reason": "Complex operation with insufficient confidence for autonomous execution",
            }

    def _critical_decision_strategy(
        self, context: DecisionContext, confidence: float
    ) -> Dict[str, Any]:
        """Strategy for critical decisions."""
        threshold = self.confidence_thresholds[DecisionComplexity.CRITICAL]

        if confidence >= threshold:
            return {
                "outcome": DecisionOutcome.ESCALATE,
                "reasoning": f"Critical decision always requires human oversight, even with high confidence ({confidence:.2f}).",
                "escalation_reason": "Critical system operation requires human approval",
            }
        else:
            return {
                "outcome": DecisionOutcome.ESCALATE,
                "reasoning": f"Critical decision with insufficient confidence ({confidence:.2f}) requires human review.",
                "escalation_reason": "Critical operation with low confidence requires expert review",
            }

    def _create_execution_plan(
        self, context: DecisionContext, intents: List[Tuple[str, float]]
    ) -> Dict[str, Any]:
        """Create detailed execution plan."""
        # Map intents to commands
        intent_to_command_map = {
            "project_analysis": ["analyze"],
            "charter_creation": ["charter"],
            "plan_generation": ["plan"],
            "validation": ["validate"],
            "optimization": ["kaizen"],
        }

        commands = []
        for intent, confidence in intents:
            if intent in intent_to_command_map:
                commands.extend(intent_to_command_map[intent])

        # Remove duplicates while preserving order
        seen = set()
        unique_commands = []
        for cmd in commands:
            if cmd not in seen:
                seen.add(cmd)
                unique_commands.append(cmd)

        return {
            "commands": unique_commands,
            "execution_order": unique_commands,
            "estimated_duration": len(unique_commands) * 30,  # 30 seconds per command
            "rollback_plan": {
                "checkpoints": [f"before_{cmd}" for cmd in unique_commands],
                "rollback_commands": ["rollback"] if len(unique_commands) > 1 else [],
            },
        }

    def _create_monitoring_plan(self, context: DecisionContext) -> Dict[str, Any]:
        """Create monitoring plan for execution."""
        return {
            "monitoring_frequency": "per_command",
            "safety_checks": [
                "file_integrity_check",
                "configuration_validation",
                "output_verification",
            ],
            "intervention_triggers": [
                "error_rate > 0.1",
                "unexpected_file_changes",
                "user_cancellation_request",
            ],
            "progress_reporting": True,
            "rollback_triggers": [
                "critical_error",
                "safety_violation",
                "user_intervention",
            ],
        }

    def _format_planned_actions(self, context: DecisionContext) -> str:
        """Format planned actions for user display."""
        actions = []
        for intent, confidence in context.resolved_intents[:3]:  # Top 3 intents
            action_name = intent.replace("_", " ").title()
            actions.append(f"• {action_name} (confidence: {confidence:.1f})")

        return "\n".join(actions)

    def _get_confidence_level(self, confidence: float) -> DecisionConfidence:
        """Convert numeric confidence to confidence level."""
        if confidence >= 0.9:
            return DecisionConfidence.VERY_HIGH
        elif confidence >= 0.7:
            return DecisionConfidence.HIGH
        elif confidence >= 0.5:
            return DecisionConfidence.MEDIUM
        elif confidence >= 0.3:
            return DecisionConfidence.LOW
        else:
            return DecisionConfidence.VERY_LOW

    def _record_decision_metrics(
        self, context: DecisionContext, result: DecisionResult
    ):
        """Record metrics for decision pipeline analysis."""
        try:
            # Record decision outcome
            outcome_event = MetricEvent(
                name="decision_pipeline_outcome",
                value=1.0,
                source=MetricSource.SYSTEM,
                category=MetricCategory.TIMING,
                dimensions={
                    "outcome": result.outcome.value,
                    "complexity": context.complexity_level.value,
                    "confidence_level": result.confidence_level.value,
                    "user_id": context.user_id,
                    "agent_id": context.agent_id,
                },
                unit="count",
            )
            self.metrics_collector.collect_metric(outcome_event)

            # Record processing time
            time_event = MetricEvent(
                name="decision_pipeline_processing_time",
                value=result.processing_time_ms,
                source=MetricSource.SYSTEM,
                category=MetricCategory.TIMING,
                dimensions={
                    "complexity": context.complexity_level.value,
                    "outcome": result.outcome.value,
                },
                unit="milliseconds",
            )
            self.metrics_collector.collect_metric(time_event)

            # Record confidence score
            confidence_event = MetricEvent(
                name="decision_pipeline_confidence",
                value=result.confidence,
                source=MetricSource.SYSTEM,
                category=MetricCategory.QUALITY,
                dimensions={
                    "complexity": context.complexity_level.value,
                    "user_experience": context.user_preferences.get(
                        "experience_level", "unknown"
                    ),
                },
                unit="score",
            )
            self.metrics_collector.collect_metric(confidence_event)

        except Exception as e:
            # Don't fail decision pipeline on metrics errors
            print(f"Warning: Failed to record decision metrics: {e}")


# Global instance
_advanced_decision_pipeline: Optional[AdvancedDecisionPipeline] = None


def get_advanced_decision_pipeline(root: Path) -> AdvancedDecisionPipeline:
    """Get the global advanced decision pipeline instance."""
    global _advanced_decision_pipeline
    if _advanced_decision_pipeline is None:
        _advanced_decision_pipeline = AdvancedDecisionPipeline(root)
    return _advanced_decision_pipeline
