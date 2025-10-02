"""
AI Gate Mediator - Intelligent intermediary between AI agents and the gate system.

This module provides an intelligent mediator that:
1. Assesses confidence of AI agent operations
2. Routes high-confidence operations directly
3. Provides smart defaults for low-confidence operations
4. Routes critical decisions to vibe coders with enhanced context
5. Learns from interactions to improve over time
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..continuous_improvement.learning_persistence import LearningPersistenceManager
from ..legacy_cleanup.gate_system import GateRequest, GateSystem, GateType


@dataclass
class MediationResult:
    """Result of mediation process."""

    proceed: bool
    response: Optional[Dict[str, Any]]
    confidence: float
    gate_created: bool
    smart_defaults_used: bool


class AIGateMediator:
    """Intelligent mediator between AI agents and gate system."""

    def __init__(self, project_root: Path, confidence_threshold: float = 0.75):
        self.project_root = project_root
        self.confidence_threshold = confidence_threshold

        # Initialize existing systems
        self.learning_system = LearningPersistenceManager(project_root)
        self.gate_system = GateSystem(project_root)

        # Cache for performance
        self._confidence_cache: Dict[str, float] = {}
        self._smart_defaults_cache: Dict[str, Dict[str, Any]] = {}

    def process_agent_request(
        self, agent_id: str, operation: str, context: Dict[str, Any]
    ) -> MediationResult:
        """
        Process AI agent request through intelligent mediation.

        Args:
            agent_id: ID of the requesting AI agent
            operation: Description of the operation being performed
            context: Additional context about the operation

        Returns:
            MediationResult with decision and response
        """
        # 1. Assess confidence using existing guidance system
        confidence = self._assess_confidence(agent_id, operation, context)

        # 2. Check for cached results first
        cache_key = f"{agent_id}:{operation}:{hash(str(context))}"
        if cache_key in self._confidence_cache:
            cached_confidence = self._confidence_cache[cache_key]
            if abs(cached_confidence - confidence) < 0.05:  # Within 5% tolerance
                confidence = cached_confidence

        # 3. Route based on confidence
        if confidence >= self.confidence_threshold:
            return self._proceed_autonomously(agent_id, operation, context, confidence)
        else:
            return self._mediate_gate_process(agent_id, operation, context, confidence)

    def _assess_confidence(
        self, agent_id: str, operation: str, context: Dict[str, Any]
    ) -> float:
        """Assess confidence of operation using multiple factors."""
        # Start with base confidence
        base_confidence = 0.7  # Default moderate confidence

        # Adjust based on operation complexity
        complexity_factor = self._calculate_complexity_factor(operation, context)

        # Adjust based on historical performance
        history_factor = self._get_history_factor(agent_id, operation)

        # Combine factors
        final_confidence = (
            base_confidence * 0.5 + complexity_factor * 0.3 + history_factor * 0.2
        )

        return min(1.0, max(0.0, final_confidence))

    def _calculate_complexity_factor(
        self, operation: str, context: Dict[str, Any]
    ) -> float:
        """Calculate complexity factor for operation."""
        # Simple heuristic based on operation characteristics
        complexity_score = 0.0

        # File operations are generally less complex
        if "file" in operation.lower():
            complexity_score -= 0.1

        # System operations are more complex
        if any(word in operation.lower() for word in ["system", "install", "deploy"]):
            complexity_score += 0.2

        # Multi-file operations are more complex
        if "files" in context and len(context["files"]) > 5:
            complexity_score += 0.1

        return 0.5 + complexity_score  # Normalize to 0.3-0.8 range

    def _get_history_factor(self, agent_id: str, operation: str) -> float:
        """Get confidence adjustment based on historical performance."""
        try:
            # Get recent learning events for this agent and operation type
            history = self.learning_system.get_learning_history(limit=50)

            relevant_events = [
                event
                for event in history
                if event.get("agent_id") == agent_id
                and operation.lower() in str(event.get("context", "")).lower()
            ]

            if not relevant_events:
                return 0.5  # Neutral if no history

            # Calculate success rate
            successful_events = sum(
                1
                for event in relevant_events
                if event.get("outcome", {}).get("success", False)
            )
            success_rate = successful_events / len(relevant_events)

            return success_rate

        except Exception:
            return 0.5  # Neutral on error

    def _proceed_autonomously(
        self, agent_id: str, operation: str, context: Dict[str, Any], confidence: float
    ) -> MediationResult:
        """Allow high-confidence operations to proceed autonomously."""
        # Log the autonomous decision for learning
        self.learning_system.record_learning_event(
            event_type="autonomous_decision",
            event_data={
                "agent_id": agent_id,
                "operation": operation,
                "confidence": confidence,
                "proceeded": True,
            },
        )

        return MediationResult(
            proceed=True,
            response={"action": "proceed", "confidence": confidence},
            confidence=confidence,
            gate_created=False,
            smart_defaults_used=False,
        )

    def _mediate_gate_process(
        self, agent_id: str, operation: str, context: Dict[str, Any], confidence: float
    ) -> MediationResult:
        """Handle low-confidence operations through intelligent gate process."""
        # 1. Check for smart defaults first
        smart_defaults = self._get_smart_defaults(operation, context)

        if smart_defaults and self._validate_smart_defaults(smart_defaults, confidence):
            return self._apply_smart_defaults(
                operation, context, smart_defaults, confidence
            )

        # 2. Route to human with enhanced context
        return self._route_to_human_with_context(
            agent_id, operation, context, confidence
        )

    def _get_smart_defaults(
        self, operation: str, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get smart defaults based on similar past decisions."""
        cache_key = f"{operation}:{hash(str(context))}"

        if cache_key in self._smart_defaults_cache:
            return self._smart_defaults_cache[cache_key]  # type: ignore

        try:
            # Use simple pattern matching for common operations
            if "file" in operation.lower() and len(context.get("files", [])) <= 3:
                # Small file operations are usually safe to proceed
                result = {"user_decision": "proceed"}
                self._smart_defaults_cache[cache_key] = result
                return result

            if "analysis" in operation.lower():
                # Analysis operations are usually safe
                result = {"user_decision": "proceed"}
                self._smart_defaults_cache[cache_key] = result
                return result

            # For other operations, check learning history
            history = self.learning_system.get_learning_history(limit=20)
            similar_operations = [
                event
                for event in history
                if operation.lower() in str(event.get("context", {})).lower()
            ]

            if similar_operations:
                # Use majority vote from history
                decisions: Dict[str, int] = {}
                for event in similar_operations:
                    decision = event.get("outcome", {}).get("user_decision", "unknown")
                    decisions[decision] = decisions.get(decision, 0) + 1

                if decisions:
                    most_common = max(decisions.items(), key=lambda x: x[1])
                    if most_common[1] >= len(similar_operations) * 0.6:  # 60% agreement
                        result = {"user_decision": most_common[0]}
                        self._smart_defaults_cache[cache_key] = result
                        return result

        except Exception:
            pass

        return None

    def _validate_smart_defaults(
        self, defaults: Dict[str, Any], confidence: float
    ) -> bool:
        """Validate if smart defaults are appropriate for this situation."""
        # Only use smart defaults if confidence is reasonably high
        return confidence >= 0.6 and defaults.get("user_decision") in [
            "proceed",
            "modify",
        ]

    def _apply_smart_defaults(
        self,
        operation: str,
        context: Dict[str, Any],
        defaults: Dict[str, Any],
        confidence: float,
    ) -> MediationResult:
        """Apply smart defaults and proceed."""
        # Record the use of smart defaults for learning
        self.learning_system.record_learning_event(
            event_type="smart_defaults_applied",
            event_data={
                "operation": operation,
                "confidence": confidence,
                "used_defaults": True,
                "decision": defaults,
            },
        )

        return MediationResult(
            proceed=True,
            response=defaults,
            confidence=confidence,
            gate_created=False,
            smart_defaults_used=True,
        )

    def _route_to_human_with_context(
        self, agent_id: str, operation: str, context: Dict[str, Any], confidence: float
    ) -> MediationResult:
        """Route to human with enhanced context and smart questions."""
        # 1. Generate context-aware questions
        questions = self._generate_enhanced_questions(operation, context, confidence)

        # 2. Create enhanced gate request
        gate_request = GateRequest(
            gate_type=GateType.CLARIFICATION_NEEDED,
            title=f"AI Agent Needs Clarification: {operation}",
            description=self._generate_gate_description(operation, context),
            context=context,
            questions=questions,
            confidence=confidence,
        )

        # 3. Create gate asynchronously
        gate_result = self.gate_system.create_gate(gate_request)

        # 4. Calculate optimal timeout based on complexity
        timeout = self._calculate_optimal_timeout(operation, context)

        # 5. Wait for response asynchronously (don't block)
        response = self._wait_for_gate_response_async(gate_result, timeout)

        if response:
            # Learn from the response
            self.learning_system.record_learning_event(
                event_type="human_gate_response",
                event_data={
                    "operation": operation,
                    "confidence": confidence,
                    "response": response,
                    "authoritative": True,  # Human responses are authoritative
                },
            )

            return MediationResult(
                proceed=response.get("user_decision") == "proceed",
                response=response,
                confidence=confidence,
                gate_created=True,
                smart_defaults_used=False,
            )
        else:
            # Timeout or no response - default to stop for safety
            return MediationResult(
                proceed=False,
                response={"user_decision": "stop", "reason": "timeout"},
                confidence=confidence,
                gate_created=True,
                smart_defaults_used=False,
            )

    def _generate_enhanced_questions(
        self, operation: str, context: Dict[str, Any], confidence: float
    ) -> List[str]:
        """Generate context-aware questions for the gate."""
        questions = []

        # Base question about proceeding
        questions.append(f"Should I proceed with: {operation}?")

        # Context-specific questions
        if "files" in context:
            questions.append(
                f"This involves {len(context['files'])} files. Is this the scope you want?"
            )

        if confidence < 0.5:
            questions.append(
                "What specific outcome are you looking for from this operation?"
            )

        # Vision alignment question
        questions.append("Does this align with your original project vision?")

        return questions

    def _generate_gate_description(
        self, operation: str, context: Dict[str, Any]
    ) -> str:
        """Generate human-friendly description of the gate."""
        # Simple description generation
        description = f"Your AI agent wants to perform: {operation}"

        if "files" in context:
            file_count = len(context["files"])
            description += (
                f" involving {file_count} file{'s' if file_count != 1 else ''}"
            )

        if "confidence" in context:
            description += f" with {context['confidence']:.1%} confidence"

        return description

    def _calculate_optimal_timeout(
        self, operation: str, context: Dict[str, Any]
    ) -> int:
        """Calculate optimal timeout based on operation complexity."""
        base_timeout = 30  # Base 30 seconds

        # Adjust based on complexity
        if any(word in operation.lower() for word in ["complex", "system", "deploy"]):
            base_timeout += 30

        if "files" in context and len(context["files"]) > 10:
            base_timeout += 20

        return base_timeout

    def _wait_for_gate_response_async(
        self, gate_result: Dict[str, Any], timeout: int
    ) -> Optional[Dict[str, Any]]:
        """Wait for gate response asynchronously."""
        # Simple polling implementation (could be enhanced with proper async)
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.gate_system.is_gate_active():
                # Check if response file exists
                response_file = (
                    self.project_root / ".ai_onboard" / "gates" / "gate_response.json"
                )
                if response_file.exists():
                    try:
                        with open(response_file, "r") as f:
                            response = json.load(f)
                        response_file.unlink()  # Clean up
                        return response  # type: ignore
                    except (json.JSONDecodeError, IOError):
                        pass

            time.sleep(1)  # Poll every second

        return None


def get_ai_gate_mediator(project_root: Path) -> AIGateMediator:
    """Get or create AI gate mediator for the project."""
    return AIGateMediator(project_root)
