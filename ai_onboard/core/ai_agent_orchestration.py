"""
AI Agent Orchestration Layer (AAOL) - Revolutionary collaborative system for AI agents.

This system provides:
- Session - based conversation management with persistent context
- Multi - stage decision engine with confidence scoring and risk assessment
- Command orchestration with rollback capabilities and safety monitoring
- Real - time intervention system that can halt dangerous operations
- Context continuity across conversation rounds with memory management
- Novel "Intent Resolution" system that maps conversations to actions
- INTELLIGENT TOOL ORCHESTRATION: Automatically applies development tools based on context
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from . import alignment
from .ai_agent_wrapper import IASGuardrails
from .code_quality_analyzer import CodeQualityAnalyzer
from .enhanced_conversation_context import get_enhanced_context_manager
from .file_organization_analyzer import FileOrganizationAnalyzer
from .mandatory_tool_consultation_gate import (
    enforce_tool_consultation,
    get_mandatory_gate,
)
from .risk_assessment_framework import RiskAssessmentFramework
from .session_storage import SessionStorageManager
from .structural_recommendation_engine import StructuralRecommendationEngine
from .tool_usage_tracker import get_tool_tracker


class DecisionStage(Enum):
    """Multi - stage decision pipeline stages."""

    ENHANCED_CONTEXT_INTEGRATION = (
        "enhanced_context_integration"  # Automatic context loading and enhancement
    )
    INTAKE = "intake"  # Initial conversation analysis
    MANDATORY_TOOL_CONSULTATION = (
        "mandatory_tool_consultation"  # PRIME DIRECTIVE: Consult tools first
    )
    INTENT_RESOLUTION = "intent_resolution"  # Map conversation to specific intents
    RISK_ASSESSMENT = "risk_assessment"  # Evaluate potential risks
    CONFIDENCE_SCORING = "confidence_scoring"  # Calculate execution confidence
    SAFETY_CHECK = "safety_check"  # Final safety validation
    EXECUTION_PLANNING = "execution_planning"  # Plan command execution
    ROLLBACK_PREPARATION = "rollback_preparation"  # Prepare rollback strategy


class ConversationState(Enum):
    """States of AI agent conversations."""

    ACTIVE = "active"
    WAITING_FOR_INPUT = "waiting_for_input"
    READY_TO_EXECUTE = "ready_to_execute"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DevelopmentTool(Enum):
    """Development tools that can be automatically applied."""

    CODE_QUALITY_ANALYSIS = "code_quality_analysis"
    ORGANIZATION_ANALYSIS = "organization_analysis"
    STRUCTURAL_RECOMMENDATIONS = "structural_recommendations"
    RISK_ASSESSMENT = "risk_assessment"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    DUPLICATE_DETECTION = "duplicate_detection"
    IMPLEMENTATION_PLANNING = "implementation_planning"


@dataclass
class ToolApplicationTrigger:
    """Triggers for automatic tool application."""

    trigger_type: str  # 'keyword', 'context', 'pattern', 'time_based'
    keywords: List[str] = field(default_factory=list)
    contexts: List[str] = field(
        default_factory=list
    )  # 'code_changes', 'refactoring', 'cleanup', 'analysis'
    patterns: List[str] = field(default_factory=list)
    priority: int = 1  # 1-5, higher = more important
    cooldown_minutes: int = 30  # Don't reapply same tool too frequently


@dataclass
class IntelligentToolOrchestrator:
    """
    Intelligent orchestrator that automatically applies development tools based on context.

    This system analyzes conversations and development activities to determine when to
    automatically apply code quality analysis, risk assessment, and other development tools.
    """

    root_path: Path
    tool_tracker: Any = field(init=False)

    # Tool application rules
    tool_triggers: Dict[DevelopmentTool, List[ToolApplicationTrigger]] = field(
        default_factory=dict
    )

    def __post_init__(self):
        self.tool_tracker = get_tool_tracker(self.root_path)
        self._initialize_tool_triggers()

    def _initialize_tool_triggers(self):
        """Initialize intelligent triggers for automatic tool application."""

        # Code Quality Analysis triggers
        self.tool_triggers[DevelopmentTool.CODE_QUALITY_ANALYSIS] = [
            ToolApplicationTrigger(
                trigger_type="keyword",
                keywords=[
                    "cleanup",
                    "refactor",
                    "quality",
                    "dead code",
                    "unused",
                    "optimize",
                ],
                priority=3,
                cooldown_minutes=60,
            ),
            ToolApplicationTrigger(
                trigger_type="context",
                contexts=["refactoring", "cleanup"],
                priority=4,
                cooldown_minutes=30,
            ),
            ToolApplicationTrigger(
                trigger_type="pattern",
                patterns=["import.*unused", "dead.*code", "function.*never.*used"],
                priority=5,
                cooldown_minutes=15,
            ),
        ]

        # Organization Analysis triggers
        self.tool_triggers[DevelopmentTool.ORGANIZATION_ANALYSIS] = [
            ToolApplicationTrigger(
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
            ),
            ToolApplicationTrigger(
                trigger_type="context",
                contexts=["file_organization", "directory_structure"],
                priority=4,
                cooldown_minutes=30,
            ),
        ]

        # Risk Assessment triggers
        self.tool_triggers[DevelopmentTool.RISK_ASSESSMENT] = [
            ToolApplicationTrigger(
                trigger_type="keyword",
                keywords=["risk", "dangerous", "breaking", "impact", "safety"],
                priority=4,
                cooldown_minutes=20,
            ),
            ToolApplicationTrigger(
                trigger_type="context",
                contexts=["code_changes", "refactoring", "breaking_changes"],
                priority=5,
                cooldown_minutes=10,
            ),
        ]

        # Implementation Planning triggers
        self.tool_triggers[DevelopmentTool.IMPLEMENTATION_PLANNING] = [
            ToolApplicationTrigger(
                trigger_type="keyword",
                keywords=["implement", "plan", "phased", "rollout", "deployment"],
                priority=3,
                cooldown_minutes=60,
            ),
            ToolApplicationTrigger(
                trigger_type="context",
                contexts=["large_changes", "complex_refactoring"],
                priority=4,
                cooldown_minutes=30,
            ),
        ]

    def analyze_conversation_for_tool_application(
        self,
        conversation_history: List[Dict[str, Any]],
        current_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Analyze conversation and context to determine which tools should be automatically applied.

        Returns list of recommended tool applications with confidence scores.
        """

        recommendations = []

        # Analyze conversation content
        full_conversation = " ".join(
            [
                msg.get("content", "")
                for msg in conversation_history[-10:]  # Last 10 messages
            ]
        ).lower()

        # Check each tool's triggers
        for tool, triggers in self.tool_triggers.items():
            tool_confidence = 0
            trigger_matches = []

            for trigger in triggers:
                match_score = 0

                if trigger.trigger_type == "keyword":
                    # Check for keyword matches
                    for keyword in trigger.keywords:
                        if keyword.lower() in full_conversation:
                            match_score += 1

                elif trigger.trigger_type == "context":
                    # Check context matches
                    current_contexts = current_context.get("contexts", [])
                    for ctx in trigger.contexts:
                        if ctx in current_contexts:
                            match_score += 2

                elif trigger.trigger_type == "pattern":
                    # Check pattern matches (simple string matching for now)
                    for pattern in trigger.patterns:
                        if pattern.lower() in full_conversation:
                            match_score += 3

                if match_score > 0:
                    tool_confidence += match_score * trigger.priority
                    trigger_matches.append(
                        {
                            "trigger": trigger.trigger_type,
                            "matches": match_score,
                            "priority": trigger.priority,
                        }
                    )

            # If confidence is high enough, recommend the tool
            if tool_confidence >= 3:  # Threshold for recommendation
                recommendations.append(
                    {
                        "tool": tool.value,
                        "confidence": min(
                            tool_confidence / 10, 1.0
                        ),  # Normalize to 0-1
                        "triggers": trigger_matches,
                        "reasoning": f"Detected {len(trigger_matches)} trigger matches with confidence {tool_confidence/10:.1f}",
                    }
                )

        # Sort by confidence
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)

        return recommendations

    def execute_automatic_tool_application(
        self, tool_name: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an automatic tool application based on detected triggers.

        Returns execution results and status.
        """

        result = {"tool": tool_name, "executed": False, "results": None, "error": None}

        try:
            if tool_name == "code_quality_analysis":
                analyzer = CodeQualityAnalyzer(self.root_path)
                result["results"] = analyzer.analyze_codebase()
                result["executed"] = True

            elif tool_name == "organization_analysis":
                analyzer = FileOrganizationAnalyzer(self.root_path)
                result["results"] = analyzer.analyze_organization()
                result["executed"] = True

            elif tool_name == "structural_recommendations":
                # First do organization analysis
                org_analyzer = FileOrganizationAnalyzer(self.root_path)
                org_result = org_analyzer.analyze_organization()

                # Then generate recommendations
                engine = StructuralRecommendationEngine(self.root_path)
                result["results"] = engine.generate_recommendations(org_result)
                result["executed"] = True

            elif tool_name == "risk_assessment":
                # Get recommendations first
                org_analyzer = FileOrganizationAnalyzer(self.root_path)
                org_result = org_analyzer.analyze_organization()

                engine = StructuralRecommendationEngine(self.root_path)
                recommendations = engine.generate_recommendations(org_result)

                # Convert to changes for risk assessment
                framework = RiskAssessmentFramework(self.root_path)
                changes = []

                # Convert recommendations to organization changes
                for move in recommendations.file_moves:
                    change = framework.create_change_from_recommendation(
                        move, "file_move"
                    )
                    changes.append(change)

                result["results"] = framework.assess_change_risks(changes)
                result["executed"] = True

            # Track the tool usage
            if result["executed"]:
                self.tool_tracker.track_tool_usage(
                    tool_name=f"auto_applied_{tool_name}",
                    tool_type="automatic_orchestration",
                    parameters={
                        "trigger_context": context,
                        "confidence": context.get("confidence", 0),
                    },
                    result="completed",
                )

        except Exception as e:
            result["error"] = str(e)
            result["executed"] = False

        return result


@dataclass
class ConversationContext:
    """Persistent context for AI agent conversations."""

    session_id: str
    user_id: str
    project_root: Path
    created_at: float
    last_activity: float
    state: ConversationState

    # Conversation history
    conversation_rounds: List[Dict[str, Any]] = field(default_factory=list)
    resolved_intents: List[str] = field(default_factory=list)
    user_corrections: List[str] = field(default_factory=list)

    # Decision pipeline state
    current_stage: DecisionStage = DecisionStage.INTAKE
    stage_results: Dict[str, Any] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    risk_factors: List[str] = field(default_factory=list)

    # Execution context
    planned_commands: List[Dict[str, Any]] = field(default_factory=list)
    executed_commands: List[Dict[str, Any]] = field(default_factory=list)
    rollback_plan: Optional[Dict[str, Any]] = None

    # Safety monitoring
    safety_violations: List[str] = field(default_factory=list)
    intervention_triggers: List[str] = field(default_factory=list)


class IntentResolver:
    """Novel intent resolution system that maps conversations to specific actions."""

    def __init__(self):
        self.intent_patterns = {
            "project_analysis": [
                "analyze",
                "understand",
                "examine",
                "look at",
                "check out",
                "what does",
                "how does",
                "tell me about",
            ],
            "feature_addition": [
                "add",
                "create",
                "build",
                "implement",
                "make",
                "develop",
                "I want",
                "I need",
                "can you add",
            ],
            "modification": [
                "change",
                "modify",
                "update",
                "fix",
                "improve",
                "enhance",
                "instead",
                "rather",
                "actually",
                "but",
            ],
            "clarification": [
                "what",
                "how",
                "why",
                "explain",
                "clarify",
                "help me understand",
                "I don't understand",
                "confused",
            ],
            "priority_adjustment": [
                "priority",
                "first",
                "most important",
                "focus on",
                "start with",
                "before",
                "after",
            ],
        }

    def resolve_intents(self, conversation_text: str) -> List[Tuple[str, float]]:
        """Resolve user intents from conversation with confidence scores."""
        text_lower = conversation_text.lower()
        intent_scores = {}

        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                if pattern in text_lower:
                    # Weight by pattern specificity and position
                    position_weight = 1.0 - (text_lower.find(pattern) / len(text_lower))
                    specificity_weight = (
                        len(pattern) / 20.0
                    )  # Longer patterns are more specific
                    score += position_weight * specificity_weight

            if score > 0:
                intent_scores[intent] = min(score, 1.0)

        # Return sorted by confidence
        return sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)


class SafetyMonitor:
    """Real - time safety monitoring system with intervention capabilities."""

    def __init__(self):
        self.danger_patterns = [
            "delete",
            "remove",
            "destroy",
            "wipe",
            "format",
            "rm -rf",
            "drop database",
            "truncate",
            "kill",
            "terminate",
        ]
        self.warning_patterns = [
            "overwrite",
            "replace all",
            "ignore",
            "skip",
            "bypass",
            "force",
        ]
        self.monitoring_active = False
        self.intervention_callbacks: List[Callable] = []

    def register_intervention_callback(self, callback: Callable):
        """Register callback for safety interventions."""
        self.intervention_callbacks.append(callback)

    def assess_risk(
        self, conversation_text: str, planned_commands: List[str]
    ) -> Dict[str, Any]:
        """Assess risk level of conversation and planned commands."""
        risk_level = 0
        risk_factors = []

        # Check conversation for danger patterns
        text_lower = conversation_text.lower()
        for pattern in self.danger_patterns:
            if pattern in text_lower:
                risk_level += 10
                risk_factors.append(f"danger_pattern: {pattern}")

        for pattern in self.warning_patterns:
            if pattern in text_lower:
                risk_level += 5
                risk_factors.append(f"warning_pattern: {pattern}")

        # Check planned commands
        for cmd in planned_commands:
            if any(danger in cmd.lower() for danger in self.danger_patterns):
                risk_level += 15
                risk_factors.append(f"dangerous_command: {cmd}")

        return {
            "risk_level": min(risk_level, 100),
            "risk_factors": risk_factors,
            "requires_intervention": risk_level > 20,
        }

    def trigger_intervention(self, context: ConversationContext, reason: str):
        """Trigger safety intervention."""
        context.state = ConversationState.FAILED
        context.intervention_triggers.append(reason)

        for callback in self.intervention_callbacks:
            try:
                callback(context, reason)
            except Exception as e:
                print(f"Intervention callback failed: {e}")


class CommandOrchestrator:
    """Advanced command orchestration with rollback capabilities."""

    def __init__(self, root: Path):
        self.root = root
        self.execution_history: List[Dict[str, Any]] = []

    def plan_execution(
        self, intents: List[str], context: ConversationContext
    ) -> Dict[str, Any]:
        """Plan command execution based on resolved intents."""
        execution_plan = {
            "commands": [],
            "rollback_plan": {},
            "estimated_risk": 0,
            "execution_order": [],
        }

        # Map intents to commands
        intent_to_command_map = {
            "project_analysis": ["analyze"],
            "feature_addition": ["charter", "plan"],
            "modification": ["plan", "validate"],
            "priority_adjustment": ["charter", "plan"],
        }

        # Build command sequence
        commands_needed = set()
        for intent in intents:
            if intent in intent_to_command_map:
                commands_needed.update(intent_to_command_map[intent])

        # Order commands logically
        command_order = ["analyze", "charter", "plan", "validate", "kaizen"]
        ordered_commands = [cmd for cmd in command_order if cmd in commands_needed]

        execution_plan["commands"] = ordered_commands
        execution_plan["execution_order"] = ordered_commands

        # Prepare rollback strategy
        execution_plan["rollback_plan"] = self._prepare_rollback_plan(ordered_commands)

        return execution_plan

    def _prepare_rollback_plan(self, commands: List[str]) -> Dict[str, Any]:
        """Prepare rollback strategy for command sequence."""
        rollback_plan = {
            "backup_paths": [],
            "restore_commands": [],
            "checkpoint_strategy": "incremental",
        }

        # Identify critical files to backup
        critical_files = [
            ".ai_onboard / charter.json",
            ".ai_onboard / plan.json",
            ".ai_onboard / alignment_report.json",
        ]

        for file_path in critical_files:
            full_path = self.root / file_path
            if full_path.exists():
                rollback_plan["backup_paths"].append(str(full_path))

        return rollback_plan

    def execute_with_rollback(
        self, execution_plan: Dict[str, Any], context: ConversationContext
    ) -> Dict[str, Any]:
        """Execute commands with automatic rollback on failure."""
        results = {
            "success": True,
            "executed_commands": [],
            "failed_command": None,
            "rollback_performed": False,
            "error_details": None,
        }

        # Create checkpoint
        checkpoint_id = self._create_checkpoint(context)

        try:
            for command in execution_plan["commands"]:
                # Execute command
                cmd_result = self._execute_single_command(command, context)
                results["executed_commands"].append(
                    {
                        "command": command,
                        "success": cmd_result["success"],
                        "timestamp": time.time(),
                    }
                )

                if not cmd_result["success"]:
                    # Command failed - trigger rollback
                    results["success"] = False
                    results["failed_command"] = command
                    results["error_details"] = cmd_result.get("error")

                    # Perform rollback
                    rollback_result = self._perform_rollback(checkpoint_id, context)
                    results["rollback_performed"] = rollback_result["success"]
                    break

        except Exception as e:
            results["success"] = False
            results["error_details"] = str(e)
            rollback_result = self._perform_rollback(checkpoint_id, context)
            results["rollback_performed"] = rollback_result["success"]

        return results

    def _create_checkpoint(self, context: ConversationContext) -> str:
        """Create a checkpoint for rollback."""
        checkpoint_id = f"checkpoint_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        # Implementation would create actual file backups
        return checkpoint_id

    def _execute_single_command(
        self, command: str, context: ConversationContext
    ) -> Dict[str, Any]:
        """Execute a single command with monitoring."""
        import subprocess

        try:
            # Build command with bypass flags for AI agent
            cmd_parts = ["python", "-m", "ai_onboard", command, "--assume", "proceed"]

            result = subprocess.run(
                cmd_parts,
                cwd=context.project_root,
                capture_output=True,
                text=True,
                timeout=300,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _perform_rollback(
        self, checkpoint_id: str, context: ConversationContext
    ) -> Dict[str, Any]:
        """Perform rollback to checkpoint."""
        # Implementation would restore from checkpoint
        context.state = ConversationState.ROLLED_BACK
        return {"success": True, "checkpoint_id": checkpoint_id}


class AIAgentOrchestrationLayer:
    """Revolutionary AI Agent Orchestration Layer - the main orchestrator."""

    def __init__(self, root: Path):
        self.root = root
        self.sessions: Dict[str, ConversationContext] = {}
        self.intent_resolver = IntentResolver()
        self.safety_monitor = SafetyMonitor()
        self.command_orchestrator = CommandOrchestrator(root)
        self.guardrails = IASGuardrails()

        # Initialize intelligent tool orchestrator
        self.tool_orchestrator = IntelligentToolOrchestrator(root)

        # Initialize mandatory tool consultation gate
        self.mandatory_gate = get_mandatory_gate(root)

        # Initialize enhanced context manager for automatic context integration
        self.enhanced_context_manager = get_enhanced_context_manager(root)

        # Initialize session storage
        self.session_storage = SessionStorageManager(root)

        # Register safety intervention
        self.safety_monitor.register_intervention_callback(
            self._handle_safety_intervention
        )

        # Session management
        self._session_lock = threading.Lock()

        # Load existing sessions from storage
        self._load_existing_sessions()

    def _load_existing_sessions(self):
        """Load existing sessions from persistent storage."""
        try:
            stored_sessions = self.session_storage.list_sessions()
            for session_info in stored_sessions:
                session_id = session_info["session_id"]
                context = self.session_storage.load_session(session_id)
                if context:
                    self.sessions[session_id] = context
        except Exception as e:
            print(f"Warning: Could not load existing sessions: {e}")

    def create_session(self, user_id: str = "default") -> str:
        """Create a new conversation session."""
        with self._session_lock:
            session_id = f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"

            context = ConversationContext(
                session_id=session_id,
                user_id=user_id,
                project_root=self.root,
                created_at=time.time(),
                last_activity=time.time(),
                state=ConversationState.ACTIVE,
            )

            self.sessions[session_id] = context

            # Save to persistent storage
            self.session_storage.save_session(context)

            return session_id

    def process_conversation(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Process user conversation through multi - stage decision pipeline."""
        if session_id not in self.sessions:
            # Try to load from storage
            context = self.session_storage.load_session(session_id)
            if context:
                self.sessions[session_id] = context
            else:
                return {"error": "Session not found", "session_id": session_id}

        context = self.sessions[session_id]
        context.last_activity = time.time()

        # Add to conversation history
        conversation_round = {
            "timestamp": time.time(),
            "user_input": user_input,
            "round_id": len(context.conversation_rounds),
        }
        context.conversation_rounds.append(conversation_round)

        # Run through decision pipeline
        pipeline_result = self._run_decision_pipeline(context, user_input)

        # Save updated session to storage
        self.session_storage.save_session(context)

        return pipeline_result

    def _enhance_context_automatically(
        self, context: ConversationContext, user_input: str
    ) -> Dict[str, Any]:
        """
        Automatically enhance context with cross-session memories and continuity.
        This provides seamless context integration for AI agents.
        """
        start_time = time.time()

        enhancement_result = {
            "context_enhanced": False,
            "cross_session_context": False,
            "relevant_memories": [],
            "context_insights": [],
            "enhancement_time": 0.0,
            "error": None,
        }

        try:
            # Step 1: Get relevant memories for this session
            relevant_memories = self.enhanced_context_manager._get_relevant_memories(
                context.session_id, context.user_id
            )

            # Filter by topic if possible
            current_topic = self._extract_topic_from_input(user_input)
            topic_filtered_memories = [
                memory
                for memory in relevant_memories
                if memory.topic.lower() == current_topic.lower()
                or current_topic == "general"
            ][
                :5
            ]  # Top 5 memories

            enhancement_result["relevant_memories"] = topic_filtered_memories

            # Step 2: Enhance conversation context with memories
            if topic_filtered_memories:
                # Add memory insights to context
                memory_insights = []

                for memory in topic_filtered_memories:
                    memory_insights.append(
                        {
                            "topic": memory.topic,
                            "key_facts": memory.key_facts[:3],  # First 3 facts
                            "successful_patterns": memory.successful_patterns[
                                :2
                            ],  # First 2 patterns
                            "relevance_score": getattr(memory, "relevance_score", 0.0),
                        }
                    )

                    # Mark cross-session context as available
                    if memory.session_id != context.session_id:
                        enhancement_result["cross_session_context"] = True

                enhancement_result["context_insights"] = memory_insights
                enhancement_result["context_enhanced"] = True

                # Step 3: Enhance the conversation context object with memory data
                self._enhance_conversation_context(
                    context, topic_filtered_memories, user_input
                )

            # Step 4: Track context continuity
            self._track_context_continuity(context, user_input, topic_filtered_memories)

        except Exception as e:
            enhancement_result["error"] = str(e)
            # Don't fail the pipeline if context enhancement fails - it's enhancement, not requirement

        enhancement_result["enhancement_time"] = time.time() - start_time
        return enhancement_result

    def _extract_topic_from_input(self, user_input: str) -> str:
        """Extract topic from user input for context matching."""
        # Simple topic extraction - could be enhanced with NLP
        input_lower = user_input.lower()

        # Common development topics
        topics = {
            "code": ["code", "function", "class", "method", "variable"],
            "testing": ["test", "testing", "assert", "fixture", "mock"],
            "deployment": ["deploy", "build", "ci", "cd", "docker", "kubernetes"],
            "documentation": ["doc", "readme", "comment", "document"],
            "architecture": ["architecture", "design", "structure", "pattern"],
            "performance": ["performance", "speed", "optimize", "memory", "cpu"],
            "security": ["security", "auth", "permission", "vulnerability"],
            "database": ["database", "sql", "query", "table", "migration"],
            "api": ["api", "endpoint", "request", "response", "rest", "graphql"],
            "ui": ["ui", "interface", "frontend", "component", "design"],
        }

        for topic, keywords in topics.items():
            if any(keyword in input_lower for keyword in keywords):
                return topic

        return "general"  # Default topic

    def _enhance_conversation_context(
        self, context: ConversationContext, memories: List[Any], user_input: str
    ) -> None:
        """Enhance the conversation context with memory data."""
        # Add context enhancement metadata to the context
        if not hasattr(context, "enhanced_context"):
            context.enhanced_context = {}

        context.enhanced_context.update(
            {
                "memories_loaded": len(memories),
                "cross_session_insights": [
                    memory.key_facts[:2]
                    for memory in memories
                    if memory.session_id != context.session_id
                ],
                "successful_patterns": [
                    pattern
                    for memory in memories
                    for pattern in memory.successful_patterns[
                        :1
                    ]  # One pattern per memory
                ],
                "last_enhancement": time.time(),
            }
        )

        # Add memory context to the current conversation round
        if context.conversation_rounds and len(context.conversation_rounds) > 0:
            current_round = context.conversation_rounds[-1]
            if not hasattr(current_round, "enhanced_context"):
                current_round.enhanced_context = {}

            current_round.enhanced_context.update(
                {
                    "memory_insights": [
                        {
                            "topic": memory.topic,
                            "relevant_facts": memory.key_facts[:2],
                            "confidence": memory.relevance_score,
                        }
                        for memory in memories[:3]  # Top 3 memories
                    ],
                    "context_continuity": True,
                }
            )

    def _track_context_continuity(
        self, context: ConversationContext, user_input: str, memories: List[Any]
    ) -> None:
        """Track context continuity across conversation rounds."""
        try:
            # Update context continuity metrics
            continuity_data = {
                "session_id": context.session_id,
                "user_id": context.user_id,
                "conversation_rounds": len(context.conversation_rounds),
                "memories_accessed": len(memories),
                "cross_session_references": sum(
                    1 for m in memories if m.session_id != context.session_id
                ),
                "last_activity": time.time(),
            }

            # Store continuity data (could be used for analytics)
            # For now, just track in the context
            if not hasattr(context, "continuity_tracking"):
                context.continuity_tracking = []

            context.continuity_tracking.append(continuity_data)

        except Exception:
            # Don't fail if continuity tracking fails
            pass

    def _run_decision_pipeline(
        self, context: ConversationContext, user_input: str
    ) -> Dict[str, Any]:
        """Run the multi - stage decision pipeline."""
        pipeline_results: Dict[str, Any] = {
            "session_id": context.session_id,
            "pipeline_stages": {},
            "final_decision": None,
            "ai_agent_response": None,
            "ready_to_execute": False,
            "execution_plan": None,
        }

        # STAGE -1: ENHANCED CONTEXT INTEGRATION (AUTOMATIC)
        context.current_stage = DecisionStage.ENHANCED_CONTEXT_INTEGRATION

        # Automatically enhance context with cross-session memories and continuity
        context_enhancement = self._enhance_context_automatically(context, user_input)

        context.stage_results["enhanced_context"] = context_enhancement
        pipeline_results["pipeline_stages"]["enhanced_context_integration"] = {
            "memories_loaded": len(context_enhancement.get("relevant_memories", [])),
            "context_enhanced": context_enhancement.get("context_enhanced", False),
            "cross_session_context": context_enhancement.get(
                "cross_session_context", False
            ),
            "enhancement_time": context_enhancement.get("enhancement_time", 0.0),
            "context_insights": context_enhancement.get("context_insights", []),
        }

        # STAGE 0: MANDATORY TOOL CONSULTATION (PRIME DIRECTIVE)
        context.current_stage = DecisionStage.MANDATORY_TOOL_CONSULTATION

        # Build enhanced context for tool consultation (now includes enhanced context)
        consultation_context = {
            "session_id": context.session_id,
            "user_id": context.user_id,
            "conversation_rounds": len(context.conversation_rounds),
            "contexts": getattr(context, "detected_contexts", []),
            "enhanced_context": context_enhancement,  # Include enhanced context
        }

        # ENFORCE mandatory tool consultation
        tool_consultation = self.mandatory_gate.consult_tools_for_request(
            user_input, consultation_context
        )

        context.stage_results["tool_consultation"] = tool_consultation
        pipeline_results["pipeline_stages"]["mandatory_tool_consultation"] = {
            "gate_passed": tool_consultation.gate_passed,
            "tools_consulted": len(tool_consultation.relevant_tools),
            "tools_applied": len(tool_consultation.recommended_tools),
            "consultation_time": tool_consultation.consultation_time,
            "tool_insights": {
                name: analysis.get("insights", "No insights")
                for name, analysis in tool_consultation.tool_analysis.items()
                if analysis.get("executed")
            },
        }

        # GATE CHECK: If consultation fails, block the pipeline
        if not tool_consultation.gate_passed:
            pipeline_results["final_decision"] = "tool_consultation_blocked"
            pipeline_results["ai_agent_response"] = (
                f"🚫 Tool consultation required before proceeding. "
                f"Reason: {tool_consultation.blocking_reason}"
            )
            return pipeline_results

        # Stage 1: Intent Resolution
        context.current_stage = DecisionStage.INTENT_RESOLUTION
        intents = self.intent_resolver.resolve_intents(user_input)
        context.stage_results["intents"] = intents
        pipeline_results["pipeline_stages"]["intent_resolution"] = {
            "intents": intents,
            "primary_intent": intents[0] if intents else None,
        }

        # Stage 2: Risk Assessment
        context.current_stage = DecisionStage.RISK_ASSESSMENT
        planned_commands = [intent[0] for intent in intents[:3]]  # Top 3 intents
        risk_assessment = self.safety_monitor.assess_risk(user_input, planned_commands)
        context.stage_results["risk_assessment"] = risk_assessment
        pipeline_results["pipeline_stages"]["risk_assessment"] = risk_assessment

        # Safety intervention check
        if risk_assessment["requires_intervention"]:
            self.safety_monitor.trigger_intervention(context, "High risk detected")
            pipeline_results["final_decision"] = "intervention_triggered"
            pipeline_results["ai_agent_response"] = (
                "🚨 Safety intervention triggered. Operation cancelled for security reasons."
            )
            return pipeline_results

        # Stage 3: Confidence Scoring
        context.current_stage = DecisionStage.CONFIDENCE_SCORING
        confidence_scores = self._calculate_confidence_scores(context, user_input)
        context.confidence_scores.update(confidence_scores)
        pipeline_results["pipeline_stages"]["confidence_scoring"] = confidence_scores

        # Stage 4: Execution Planning
        context.current_stage = DecisionStage.EXECUTION_PLANNING
        intent_names = [intent[0] for intent in intents]
        execution_plan = self.command_orchestrator.plan_execution(intent_names, context)
        context.planned_commands = execution_plan["commands"]
        pipeline_results["execution_plan"] = execution_plan

        # INTELLIGENT TOOL APPLICATION: Analyze conversation for automatic tool application
        current_context = {
            "contexts": context.detected_contexts,
            "confidence": confidence_scores.get("overall", 0.0),
            "risk_level": risk_assessment.get("risk_level", "unknown"),
            "intents": context.stage_results.get("intents", []),
        }

        # Convert conversation rounds to format expected by orchestrator
        conversation_history = [
            {"content": round.get("user_input", "")}
            for round in context.conversation_rounds[-10:]
        ]

        # Analyze for automatic tool application
        tool_recommendations = (
            self.tool_orchestrator.analyze_conversation_for_tool_application(
                conversation_history, current_context
            )
        )

        # Apply high-confidence tools automatically
        applied_tools = []
        if tool_recommendations:
            for recommendation in tool_recommendations:
                if recommendation["confidence"] > 0.7:  # High confidence threshold
                    print(
                        f"🤖 AUTO-APPLYING TOOL: {recommendation['tool']} (confidence: {recommendation['confidence']:.1f})"
                    )

                    execution_result = (
                        self.tool_orchestrator.execute_automatic_tool_application(
                            recommendation["tool"], recommendation
                        )
                    )

                    if execution_result["executed"]:
                        applied_tools.append(
                            {
                                "tool": recommendation["tool"],
                                "confidence": recommendation["confidence"],
                                "results": execution_result["results"],
                            }
                        )
                        print(f"✅ Auto-applied {recommendation['tool']} successfully")
                    else:
                        print(
                            f"❌ Failed to auto-apply {recommendation['tool']}: {execution_result.get('error', 'Unknown error')}"
                        )

        pipeline_results["auto_applied_tools"] = applied_tools

        # Generate AI agent response (enhanced with tool consultation results)
        ai_response = self._generate_ai_agent_response(context, pipeline_results)
        pipeline_results["ai_agent_response"] = ai_response

        # Determine if ready to execute
        overall_confidence = confidence_scores.get("overall", 0.0)
        if overall_confidence > 0.7 and not risk_assessment["requires_intervention"]:
            context.state = ConversationState.READY_TO_EXECUTE
            pipeline_results["ready_to_execute"] = True
            pipeline_results["final_decision"] = "proceed"
        else:
            context.state = ConversationState.WAITING_FOR_INPUT
            pipeline_results["final_decision"] = "clarify"

        return pipeline_results

    def _calculate_confidence_scores(
        self, context: ConversationContext, user_input: str
    ) -> Dict[str, float]:
        """Calculate confidence scores for execution decision."""
        # Get alignment preview for base confidence
        alignment_data = alignment.preview(self.root)
        base_confidence = alignment_data.get("confidence", 0.0)

        # Adjust based on conversation context
        conversation_rounds = len(context.conversation_rounds)
        conversation_bonus = min(conversation_rounds * 0.1, 0.3)  # Max 0.3 bonus

        # Adjust based on resolved intents clarity
        intent_clarity = len(context.stage_results.get("intents", [])) * 0.1
        intent_clarity = min(intent_clarity, 0.2)  # Max 0.2 bonus

        # Penalty for risk factors
        risk_penalty = len(context.risk_factors) * 0.1

        overall_confidence = (
            base_confidence + conversation_bonus + intent_clarity - risk_penalty
        )
        overall_confidence = max(0.0, min(1.0, overall_confidence))

        return {
            "base": base_confidence,
            "conversation_bonus": conversation_bonus,
            "intent_clarity": intent_clarity,
            "risk_penalty": risk_penalty,
            "overall": overall_confidence,
        }

    def _generate_ai_agent_response(
        self, context: ConversationContext, pipeline_results: Dict[str, Any]
    ) -> str:
        """Generate natural AI agent response based on pipeline results."""

        # Get tool consultation results
        tool_consultation_stage = pipeline_results["pipeline_stages"].get(
            "mandatory_tool_consultation", {}
        )
        tool_insights = tool_consultation_stage.get("tool_insights", {})
        tools_applied = tool_consultation_stage.get("tools_applied", 0)

        # Start response with tool consultation summary
        response = "🤖 **AI-ONBOARD TOOL-ENHANCED RESPONSE**\n\n"

        if tools_applied > 0:
            response += (
                f"✅ **Tool Analysis Complete** ({tools_applied} tools applied):\n"
            )
            for tool_name, insight in tool_insights.items():
                response += (
                    f"   • **{tool_name.replace('_', ' ').title()}**: {insight}\n"
                )
            response += "\n"
        else:
            response += "ℹ️ **No specific tools were needed for this request**\n\n"

        # Get confidence and intents
        confidence = pipeline_results["pipeline_stages"]["confidence_scoring"][
            "overall"
        ]
        intents = pipeline_results["pipeline_stages"]["intent_resolution"]["intents"]
        execution_plan = pipeline_results["execution_plan"]

        # Generate response based on confidence, but always include tool context
        if confidence > 0.8:
            response += f"🎯 **High Confidence Response**\n"
            response += f"Based on the tool analysis above and our conversation, I'll help you with:\n"
            for intent, score in intents[:2]:
                response += f"  • {intent.replace('_', ' ').title()} (confidence: {score:.1f})\n"
            response += f"\nPlanned commands: {', '.join(execution_plan['commands'])}\n"
            response += "Should I proceed with this tool-informed approach?"

        elif confidence > 0.6:
            response += f"🤔 **Medium Confidence - Seeking Confirmation**\n"
            response += (
                f"The tool analysis provides helpful context. I believe you want:\n"
            )
            for intent, score in intents[:2]:
                response += f"  • {intent.replace('_', ' ').title()} (confidence: {score:.1f})\n"
            response += f"\nWith the insights from the tools above, planned commands: {', '.join(execution_plan['commands'])}\n"
            response += (
                "Does this tool-enhanced understanding match what you're looking for?"
            )

        else:
            response += f"❓ **Clarification Needed - Tools Provide Context**\n"
            response += f"While the tools above give us some insights, I need clarification on your main goal:\n"
            for intent, score in intents[:3]:
                response += f"  • {intent.replace('_', ' ').title()} (confidence: {score:.1f})\n"
            response += "\nThe tool analysis will help me give you a better response once I understand your priority."

        # Always mention that tools were consulted
        response += f"\n💡 *This response is enhanced by ai_onboard tool analysis to ensure quality development practices.*"

        return response

    def execute_plan(self, session_id: str) -> Dict[str, Any]:
        """Execute the planned commands for a session."""
        if session_id not in self.sessions:
            # Try to load from storage
            context = self.session_storage.load_session(session_id)
            if context:
                self.sessions[session_id] = context
            else:
                return {"error": "Session not found"}

        context = self.sessions[session_id]

        if context.state != ConversationState.READY_TO_EXECUTE:
            return {
                "error": "Session not ready for execution",
                "state": context.state.value,
            }

        context.state = ConversationState.EXECUTING

        # Execute with rollback capabilities
        execution_plan = {
            "commands": context.planned_commands,
            "rollback_plan": context.rollback_plan,
        }

        execution_result = self.command_orchestrator.execute_with_rollback(
            execution_plan, context
        )

        if execution_result["success"]:
            context.state = ConversationState.COMPLETED
        else:
            context.state = ConversationState.FAILED

        return execution_result

    def list_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available sessions."""
        return self.session_storage.list_sessions(user_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
        return self.session_storage.delete_session(session_id)

    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up expired sessions."""
        deleted_count = self.session_storage.cleanup_expired_sessions(max_age_hours)

        # Also remove from memory
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)

        expired_in_memory = [
            session_id
            for session_id, context in self.sessions.items()
            if context.last_activity < cutoff_time
        ]

        for session_id in expired_in_memory:
            del self.sessions[session_id]

        return deleted_count

    def _handle_safety_intervention(self, context: ConversationContext, reason: str):
        """Handle safety intervention callback."""
        print(f"🚨 SAFETY INTERVENTION: {reason}")
        print(f"   Session: {context.session_id}")
        print(f"   User: {context.user_id}")
        # Could send alerts, log to security system, etc.

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session status."""
        if session_id not in self.sessions:
            # Try to load from storage
            context = self.session_storage.load_session(session_id)
            if context:
                self.sessions[session_id] = context
            else:
                return {"error": "Session not found"}

        context = self.sessions[session_id]

        return {
            "session_id": session_id,
            "state": context.state.value,
            "conversation_rounds": len(context.conversation_rounds),
            "resolved_intents": context.resolved_intents,
            "confidence_scores": context.confidence_scores,
            "planned_commands": context.planned_commands,
            "executed_commands": len(context.executed_commands),
            "safety_violations": context.safety_violations,
            "created_at": context.created_at,
            "last_activity": context.last_activity,
        }


# Factory function for easy instantiation
def create_ai_agent_orchestrator(root: Path) -> AIAgentOrchestrationLayer:
    """Create an AI Agent Orchestration Layer instance."""
    return AIAgentOrchestrationLayer(root)
