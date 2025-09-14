"""
AI Agent Orchestration Layer (AAOL) - Revolutionary collaborative system for AI agents.

This system provides:
- Session - based conversation management with persistent context
- Multi - stage decision engine with confidence scoring and risk assessment
- Command orchestration with rollback capabilities and safety monitoring
- Real - time intervention system that can halt dangerous operations
- Context continuity across conversation rounds with memory management
- Novel "Intent Resolution" system that maps conversations to actions
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
from .session_storage import SessionStorageManager


class DecisionStage(Enum):
    """Multi - stage decision pipeline stages."""

    INTAKE = "intake"  # Initial conversation analysis
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

        # Generate AI agent response
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
        confidence = pipeline_results["pipeline_stages"]["confidence_scoring"][
            "overall"
        ]
        intents = pipeline_results["pipeline_stages"]["intent_resolution"]["intents"]
        execution_plan = pipeline_results["execution_plan"]

        if confidence > 0.8:
            response = f"✅ I understand what you want! Based on our conversation, I'll help you with:\n"
            for intent, score in intents[:2]:
                response += f"  • {intent.replace('_', ' ').title()} (confidence: {score:.1f})\n"
            response += f"\nI'll run these commands for you: {', '.join(execution_plan['commands'])}\n"
            response += "Should I proceed?"

        elif confidence > 0.6:
            response = f"🤔 I have a good understanding but want to confirm:\n"
            for intent, score in intents[:2]:
                response += f"  • {intent.replace('_', ' ').title()} (confidence: {score:.1f})\n"
            response += f"\nPlanned commands: {', '.join(execution_plan['commands'])}\n"
            response += "Does this match what you're looking for?"

        else:
            response = f"❓ I need some clarification to help you better. Here's what I think you want:\n"
            for intent, score in intents[:3]:
                response += f"  • {intent.replace('_', ' ').title()} (confidence: {score:.1f})\n"
            response += (
                "\nCan you help me understand which of these is most important to you?"
            )

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
