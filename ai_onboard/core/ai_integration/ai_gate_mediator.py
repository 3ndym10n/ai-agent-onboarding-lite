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

    def __init__(self, project_root: Path, confidence_threshold: float = 0.5):
        self.project_root = project_root
        # Lower threshold (0.5 instead of 0.75) allows more autonomous operation
        # while still checking in on genuinely uncertain decisions
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
            # Get recent learning events for pattern analysis
            history = self.learning_system.get_learning_history(limit=100)

            # Look for patterns in operation types and outcomes
            operation_patterns = self._analyze_operation_patterns(operation, history)

            if operation_patterns["sample_size"] < 5:
                return 0.5  # Not enough data for reliable patterns

            # Use pattern analysis for confidence adjustment
            pattern_confidence = self._calculate_pattern_confidence(operation_patterns)

            # Adjust based on recency - more recent events are more relevant
            recency_factor = self._calculate_recency_factor(
                operation_patterns["recent_events"]
            )

            final_confidence = (pattern_confidence * 0.7) + (recency_factor * 0.3)

            return min(0.9, max(0.1, final_confidence))

        except Exception:
            return 0.5  # Neutral on error

    def _analyze_operation_patterns(
        self, operation: str, history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze patterns in historical operations."""
        relevant_events = []

        for event in history:
            event_context = event.get("context", {})
            event_operation = str(event_context.get("operation", "")).lower()

            # Look for similar operations (partial matches)
            if (
                operation.lower() in event_operation
                or event_operation in operation.lower()
            ):
                relevant_events.append(event)

        if not relevant_events:
            return {"sample_size": 0, "success_rate": 0.5, "recent_events": 0}

        # Calculate success rate based on whether operations proceeded successfully
        successful_events = sum(
            1
            for event in relevant_events
            if event.get("outcome", {}).get("proceeded", False)
            and not event.get("outcome", {}).get("failed", False)
        )

        success_rate = (
            successful_events / len(relevant_events) if relevant_events else 0.5
        )

        # Count recent events (last 20 events)
        recent_threshold = 20
        recent_events = min(len(relevant_events), recent_threshold)

        return {
            "sample_size": len(relevant_events),
            "success_rate": success_rate,
            "recent_events": recent_events,
        }

    def _calculate_pattern_confidence(self, patterns: Dict[str, Any]) -> float:
        """Calculate confidence based on historical patterns."""
        success_rate = patterns["success_rate"]

        # Higher success rate = higher confidence
        # But we need enough samples to be confident
        sample_size = patterns["sample_size"]

        if sample_size < 5:
            return 0.5  # Not enough data

        # Scale confidence based on success rate and sample size
        base_confidence = success_rate

        # More samples = more confidence in the pattern
        sample_confidence = min(1.0, sample_size / 20.0)  # Max out at 20 samples

        result = (base_confidence * 0.7) + (sample_confidence * 0.3)
        return float(result)

    def _calculate_recency_factor(self, recent_events: int) -> float:
        """Calculate how recent the relevant events are."""
        # More recent events = higher confidence in current patterns
        if recent_events == 0:
            return 0.3  # Low confidence if no recent events

        # Scale from 0.3 (no recent events) to 0.9 (many recent events)
        return 0.3 + (recent_events / 20.0 * 0.6)

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
        """Route to human with collaborative guidance options."""
        # 1. Generate collaborative guidance options
        guidance_options = self._generate_collaborative_options(
            operation, context, confidence
        )

        # 2. Create collaborative gate request
        options_text = "\n".join(f"{k}) {v}" for k, v in guidance_options.items())
        gate_request = GateRequest(
            gate_type=GateType.CLARIFICATION_NEEDED,
            title=f"AI Agent Collaboration: {operation}",
            description=self._generate_collaborative_description(operation, context),
            context=context,
            questions=[f"Choose your preferred approach:\n{options_text}"],
            confidence=confidence,
        )

        # 3. Create gate and start AI agent work in parallel
        gate_result = self.gate_system.create_gate(gate_request)

        # 4. Start AI agent work while waiting for guidance
        ai_work_result = self._start_parallel_ai_work(
            agent_id, operation, context, guidance_options
        )

        # 5. Wait for guidance with shorter timeout (since AI is working)
        timeout = self._calculate_collaborative_timeout(operation, context)
        response = self.gate_system._wait_for_response(
            timeout, gate_request=gate_request
        )

        if response:
            # Learn from the collaborative guidance
            self._learn_from_collaborative_response(
                operation, context, response, confidence
            )

            # Combine AI work with user guidance
            final_result = self._combine_ai_work_with_guidance(
                ai_work_result, response, guidance_options
            )
            # Handle collaborative gates that should not block
            user_decision = response.get("user_decision", "")
            should_proceed = user_decision in [
                "proceed",
                "proceed_with_guidance",
                "proceed_with_defaults",
            ]

            # Mark smart defaults as used if it's a default response
            smart_defaults_used = user_decision == "proceed_with_defaults"

            return MediationResult(
                proceed=should_proceed,
                response=final_result,
                confidence=confidence,
                gate_created=True,
                smart_defaults_used=smart_defaults_used,
            )
        else:
            # Timeout - use AI work with smart defaults applied
            final_result = self._apply_defaults_to_ai_work(
                ai_work_result, operation, context
            )
            return MediationResult(
                proceed=True,
                response=final_result,
                confidence=confidence,
                gate_created=True,
                smart_defaults_used=True,
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
        # Create conversational, vibe-coder friendly description
        parts = []

        # Main action in plain English
        parts.append(f"🤖 **I want to**: {operation}")

        # Add context details
        if "files" in context and context["files"]:
            file_count = len(context["files"])
            if file_count == 1:
                parts.append(f"📄 **File**: {context['files'][0]}")
            elif file_count <= 3:
                parts.append(f"📄 **Files**: {', '.join(context['files'])}")
            else:
                parts.append(f"📄 **Files**: {file_count} files")

        if "command" in context:
            parts.append(f"⚙️  **Command**: `{context['command']}`")

        # Add confidence level in friendly terms
        confidence = context.get("confidence", 0.5)
        if confidence >= 0.8:
            parts.append("✅ **Confidence**: High - I'm pretty sure about this")
        elif confidence >= 0.5:
            parts.append("🤔 **Confidence**: Medium - I could use your input")
        else:
            parts.append("❓ **Confidence**: Low - I need your guidance")

        # Add helpful context
        if "phase" in context:
            parts.append(f"📍 **Phase**: {context['phase']}")

        return "\n".join(parts)

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

    def _learn_from_guidance_response(
        self,
        operation: str,
        context: Dict[str, Any],
        response: Dict[str, Any],
        confidence: float,
    ) -> None:
        """Learn from human guidance responses to improve future decisions."""
        try:
            # Record that human guidance was needed and what the response was
            self.learning_system.record_learning_event(
                event_type="guidance_provided",
                event_data={
                    "operation": operation,
                    "confidence": confidence,
                    "human_response": response,
                    "context": context,
                    "guidance_helpful": True,  # Human guidance is always authoritative
                },
            )

            # If the operation was uncertain but user approved, learn that this operation type
            # might be safe to do autonomously in the future
            if response.get("user_decision") == "proceed" and confidence < 0.7:
                self.learning_system.record_learning_event(
                    event_type="autonomy_confidence_increased",
                    event_data={
                        "operation": operation,
                        "previous_confidence": confidence,
                        "new_confidence": min(
                            confidence + 0.1, 0.9
                        ),  # Gradually increase confidence
                    },
                )

        except Exception:
            # Don't fail if learning fails
            pass

    def _apply_guidance_to_operation(
        self, operation: str, context: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply human guidance to modify the operation."""
        # Extract guidance from response
        user_responses = response.get("user_responses", [])

        # Apply guidance to context for future operations
        if user_responses:
            # Store guidance for this operation type
            guidance_context = {
                "operation": operation,
                "user_guidance": user_responses,
                "applied": True,
            }
            # This could be used to modify future similar operations

        return {
            "action": "proceed_with_guidance",
            "guidance_applied": user_responses,
            "confidence": response.get("confidence", 0.8),
        }

    def _apply_timeout_defaults(
        self, operation: str, context: Dict[str, Any], confidence: float
    ) -> Dict[str, Any]:
        """Apply smart defaults when human response times out."""
        # Use learning history to determine safe defaults
        smart_defaults = self._get_smart_defaults(operation, context)

        if smart_defaults:
            return {
                "action": "proceed_with_defaults",
                "defaults_applied": smart_defaults,
                "reason": "timeout_fallback",
            }
        else:
            # Conservative default - proceed but log the uncertainty
            return {
                "action": "proceed_with_caution",
                "confidence": confidence,
                "reason": "timeout_no_defaults",
            }

    def _generate_guiding_questions(
        self, operation: str, context: Dict[str, Any], confidence: float
    ) -> List[str]:
        """Generate guiding questions instead of blocking questions."""
        questions = []

        # Focus on clarifying intent rather than blocking
        questions.append(
            f"I want to {operation}. What specific outcome are you looking for?"
        )

        # Ask about scope and priorities
        if "files" in context:
            file_count = len(context["files"])
            questions.append(
                f"This involves {file_count} files. Should I focus on all of them or prioritize certain ones?"
            )

        # Ask about vision alignment
        questions.append("How does this fit with your overall project vision?")

        # Ask about complexity preferences
        if confidence < 0.6:
            questions.append(
                "Do you prefer a simple solution or a more comprehensive one?"
            )

        return questions

    def _generate_guiding_description(
        self, operation: str, context: Dict[str, Any]
    ) -> str:
        """Generate a guiding description instead of a blocking one."""
        # Focus on collaboration rather than uncertainty
        description = f"I'm working on: {operation}"

        if "files" in context:
            file_count = len(context["files"])
            description += (
                f" involving {file_count} file{'s' if file_count != 1 else ''}"
            )

        description += ". I want to make sure I'm building exactly what you need."

        return description

    def create_context_snapshot(
        self, agent_id: str, operation: str, context: Dict[str, Any]
    ) -> str:
        """Create a context snapshot for handover to other agents."""
        try:
            snapshot_id = f"{agent_id}_{operation}_{int(time.time())}"

            snapshot = {
                "snapshot_id": snapshot_id,
                "timestamp": time.time(),
                "agent_id": agent_id,
                "operation": operation,
                "context": context,
                "current_confidence": self._assess_confidence(
                    agent_id, operation, context
                ),
                "decisions_made": self._extract_decision_history(),
                "user_preferences": self._extract_user_preferences(),
                "vision_alignment": self._check_vision_alignment(context),
            }

            # Store snapshot for future retrieval
            self._store_context_snapshot(snapshot)

            return snapshot_id

        except Exception:
            return f"temp_{int(time.time())}"  # Fallback snapshot ID

    def load_context_for_handoff(
        self, snapshot_id: str, new_agent_id: str
    ) -> Dict[str, Any]:
        """Load context for handover to a new agent."""
        try:
            snapshot = self._retrieve_context_snapshot(snapshot_id)

            if not snapshot:
                return {"error": "No context snapshot found"}

            # Enhance context for the new agent
            handoff_context = {
                "previous_agent": snapshot["agent_id"],
                "previous_operation": snapshot["operation"],
                "previous_context": snapshot["context"],
                "previous_decisions": snapshot["decisions_made"],
                "user_preferences": snapshot["user_preferences"],
                "vision_alignment": snapshot["vision_alignment"],
                "confidence_history": snapshot["current_confidence"],
                "handoff_timestamp": time.time(),
                "new_agent_id": new_agent_id,
            }

            # Record the handoff for learning
            self.learning_system.record_learning_event(
                event_type="context_handoff",
                event_data={
                    "from_agent": snapshot["agent_id"],
                    "to_agent": new_agent_id,
                    "operation": snapshot["operation"],
                    "context_preserved": True,
                },
            )

            return handoff_context

        except Exception:
            return {"error": "Failed to load context for handoff"}

    def _extract_decision_history(self) -> List[Dict[str, Any]]:
        """Extract recent decision history for context."""
        try:
            history = self.learning_system.get_learning_history(limit=20)

            decisions = []
            for event in history:
                if event.get("event_type") in [
                    "autonomous_decision",
                    "guidance_provided",
                ]:
                    decisions.append(
                        {
                            "timestamp": event.get("timestamp"),
                            "operation": event.get("context", {}).get("operation"),
                            "confidence": event.get("context", {}).get("confidence"),
                            "outcome": event.get("outcome", {}),
                        }
                    )

            return decisions

        except Exception:
            return []

    def _extract_user_preferences(self) -> Dict[str, Any]:
        """Extract learned user preferences."""
        try:
            # Look for guidance responses that indicate preferences
            history = self.learning_system.get_learning_history(limit=50)

            preferences = {
                "complexity_preference": "unknown",
                "speed_vs_quality": "unknown",
                "risk_tolerance": "unknown",
            }

            guidance_events = [
                event
                for event in history
                if event.get("event_type") == "guidance_provided"
            ]

            if guidance_events:
                # Analyze responses for patterns
                complexity_responses = []
                for event in guidance_events:
                    response = event.get("context", {}).get("human_response", {})
                    if "simple" in str(response).lower():
                        complexity_responses.append("simple")
                    elif "comprehensive" in str(response).lower():
                        complexity_responses.append("comprehensive")

                if complexity_responses:
                    # Most common preference
                    from collections import Counter

                    most_common = Counter(complexity_responses).most_common(1)
                    if most_common:
                        preferences["complexity_preference"] = most_common[0][0]

            return preferences

        except Exception:
            return {"complexity_preference": "unknown"}

    def _check_vision_alignment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if current operation aligns with project vision."""
        try:
            # This would integrate with the vision system to check alignment
            # For now, return a basic assessment
            return {
                "aligned": True,  # Assume aligned unless we can check otherwise
                "confidence": 0.8,
                "last_checked": time.time(),
            }
        except Exception:
            return {"aligned": True, "confidence": 0.5}

    def _store_context_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Store context snapshot for future retrieval."""
        try:
            # Store in a context snapshots file
            snapshots_file = (
                self.project_root / ".ai_onboard" / "context_snapshots.json"
            )

            existing_snapshots = {}
            if snapshots_file.exists():
                with open(snapshots_file, "r") as f:
                    existing_snapshots = json.load(f)

            existing_snapshots[snapshot["snapshot_id"]] = snapshot

            # Keep only the last 50 snapshots to avoid file bloat
            if len(existing_snapshots) > 50:
                oldest_keys = sorted(existing_snapshots.keys())[
                    : len(existing_snapshots) - 50
                ]
                for key in oldest_keys:
                    del existing_snapshots[key]

            with open(snapshots_file, "w") as f:
                json.dump(existing_snapshots, f, indent=2)

        except Exception:
            pass  # Don't fail if snapshot storage fails

    def _retrieve_context_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve context snapshot by ID."""
        try:
            snapshots_file = (
                self.project_root / ".ai_onboard" / "context_snapshots.json"
            )

            if not snapshots_file.exists():
                return None

            with open(snapshots_file, "r") as f:
                snapshots = json.load(f)

            snapshot = snapshots.get(snapshot_id)
            return snapshot if isinstance(snapshot, dict) else None

        except Exception:
            return None

    def assess_operation_risk(
        self, operation: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess the risk level of an operation for protected paths."""
        risk_level = "low"
        risk_factors = []

        # Check for file operations that might be risky
        if "files" in context:
            files = context["files"]
            file_count = len(files)

            # Large number of files = higher risk
            if file_count > 10:
                risk_level = "high"
                risk_factors.append(f"Large number of files ({file_count})")

            # Check for sensitive file patterns
            sensitive_patterns = [
                ".env",
                "secrets",
                ".pem",
                "id_rsa",
                ".key",
                "password",
            ]
            sensitive_files = [
                f
                for f in files
                if any(pattern in str(f).lower() for pattern in sensitive_patterns)
            ]

            if sensitive_files:
                risk_level = "high"
                risk_factors.append(f"Sensitive files detected: {sensitive_files}")

        # Check for delete operations
        if "delete" in operation.lower() or "remove" in operation.lower():
            risk_level = "high"
            risk_factors.append("Delete operation detected")

        # Check for system-level operations
        if any(
            word in operation.lower()
            for word in ["system", "install", "deploy", "uninstall"]
        ):
            risk_level = "medium"
            risk_factors.append("System-level operation")

        # Assess based on user history and preferences
        user_risk_tolerance = self._assess_user_risk_tolerance()
        if user_risk_tolerance == "high" and risk_level == "medium":
            risk_level = "low"  # User has shown tolerance for this type of risk

        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "user_risk_tolerance": user_risk_tolerance,
            "recommendation": self._get_risk_recommendation(
                risk_level, operation, context
            ),
        }

    def _assess_user_risk_tolerance(self) -> str:
        """Assess user's risk tolerance based on historical responses."""
        try:
            history = self.learning_system.get_learning_history(limit=30)

            risk_acceptance_events = [
                event
                for event in history
                if event.get("event_type") == "guidance_provided"
                and event.get("context", {})
                .get("human_response", {})
                .get("user_decision")
                == "proceed"
            ]

            if len(risk_acceptance_events) > 5:
                return "high"  # User frequently accepts risks
            elif len(risk_acceptance_events) > 2:
                return "medium"  # User sometimes accepts risks
            else:
                return "low"  # User is cautious

        except Exception:
            return "medium"  # Default to medium tolerance

    def _get_risk_recommendation(
        self, risk_level: str, operation: str, context: Dict[str, Any]
    ) -> str:
        """Get recommendation based on risk level."""
        if risk_level == "low":
            return "proceed"

        elif risk_level == "medium":
            return "ask_user"

        else:  # high risk
            return "require_confirmation"

    def get_protection_guidance(
        self, operation: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get guidance for potentially risky operations."""
        risk_assessment = self.assess_operation_risk(operation, context)

        if risk_assessment["recommendation"] == "proceed":
            return {"action": "proceed", "guidance": "Operation appears safe"}

        elif risk_assessment["recommendation"] == "ask_user":
            return {
                "action": "ask_user",
                "guidance": f"This operation may affect {len(context.get('files', []))} files. Should I proceed?",
                "risk_factors": risk_assessment["risk_factors"],
            }

        else:  # require_confirmation
            return {
                "action": "require_confirmation",
                "guidance": (
                    "This operation involves sensitive files or delete operations. "
                    "Please confirm you want to proceed."
                ),
                "risk_factors": risk_assessment["risk_factors"],
                "alternatives": self._suggest_safer_alternatives(operation, context),
            }

    def _suggest_safer_alternatives(
        self, operation: str, context: Dict[str, Any]
    ) -> List[str]:
        """Suggest safer alternatives for risky operations."""
        alternatives = []

        if "delete" in operation.lower():
            alternatives.append("Use 'backup' command first to preserve files")
            alternatives.append("Consider 'archive' instead of 'delete'")

        if "files" in context and len(context["files"]) > 5:
            alternatives.append("Process files in smaller batches")
            alternatives.append(
                "Use 'dry-run' mode first to see what would be affected"
            )

        return alternatives

    def _generate_collaborative_options(
        self, operation: str, context: Dict[str, Any], confidence: float
    ) -> Dict[str, str]:
        """Generate collaborative options instead of questions."""
        options = {}

        # Base options based on operation type
        if "create" in operation.lower() or "build" in operation.lower():
            options["A"] = "Simple approach (basic functionality)"
            options["B"] = "Comprehensive approach (full features)"
            options["C"] = "Let me specify exactly what I want"

        elif "modify" in operation.lower() or "update" in operation.lower():
            options["A"] = "Make minimal changes"
            options["B"] = "Make significant improvements"
            options["C"] = "Let me specify the exact changes"

        elif "delete" in operation.lower() or "remove" in operation.lower():
            options["A"] = "Delete selected items only"
            options["B"] = "Archive instead of delete"
            options["C"] = "Show me what would be affected first"

        else:
            # Generic options
            options["A"] = "Proceed with current approach"
            options["B"] = "Try a different approach"
            options["C"] = "Let me provide more specific guidance"

        # Add context-specific options
        if "files" in context:
            file_count = len(context["files"])
            if file_count > 5:
                options["D"] = (
                    f"Process files in batches of 5 (you have {file_count} files)"
                )

        if confidence < 0.6:
            options["E"] = "I'm not sure - can you explain the options?"

        return options

    def _generate_collaborative_description(
        self, operation: str, context: Dict[str, Any]
    ) -> str:
        """Generate a collaborative description."""
        description = f"I'm working on: {operation}"

        if "files" in context:
            file_count = len(context["files"])
            description += (
                f" involving {file_count} file{'s' if file_count != 1 else ''}"
            )

        description += ". I want to make sure I'm building exactly what you need."
        description += (
            "\n\nPlease choose your preferred approach from the options below."
        )

        return description

    def _start_parallel_ai_work(
        self,
        agent_id: str,
        operation: str,
        context: Dict[str, Any],
        guidance_options: Dict[str, str],
    ) -> Dict[str, Any]:
        """Start AI agent work in parallel while waiting for guidance."""
        # For now, return a placeholder that indicates work is in progress
        # In a real implementation, this would start actual AI agent work
        return {
            "status": "working_in_parallel",
            "operation": operation,
            "agent_id": agent_id,
            "context": context,
            "guidance_options": guidance_options,
            "started_at": time.time(),
        }

    def _calculate_collaborative_timeout(
        self, operation: str, context: Dict[str, Any]
    ) -> int:
        """Calculate shorter timeout since AI agent is working in parallel."""
        base_timeout = 15  # Shorter than before since AI is working

        # Adjust based on operation complexity
        if any(word in operation.lower() for word in ["complex", "system", "deploy"]):
            base_timeout += 10

        if "files" in context and len(context["files"]) > 10:
            base_timeout += 5

        return base_timeout

    def _wait_for_guidance_response(
        self, gate_result: Dict[str, Any], timeout: int
    ) -> Optional[Dict[str, Any]]:
        """Wait for guidance response (same as before but with shorter timeout)."""
        return self._wait_for_gate_response_async(gate_result, timeout)

    def _learn_from_collaborative_response(
        self,
        operation: str,
        context: Dict[str, Any],
        response: Dict[str, Any],
        confidence: float,
    ) -> None:
        """Learn from collaborative guidance responses."""
        try:
            # Record that collaborative guidance was provided
            user_responses = response.get("user_responses", ["unknown"])
            user_choice = user_responses[0] if user_responses else "unknown"

            self.learning_system.record_learning_event(
                event_type="collaborative_guidance",
                event_data={
                    "operation": operation,
                    "confidence": confidence,
                    "user_choice": user_choice,
                    "context": context,
                    "guidance_helpful": True,
                },
            )

            # Learn which options users prefer for different operation types
            user_responses = response.get("user_responses", [])
            if user_responses:
                choice = user_responses[0]
                if choice in ["A", "B", "C", "D", "E"]:
                    self.learning_system.record_learning_event(
                        event_type="user_preference_learned",
                        event_data={
                            "operation_type": (
                                operation.split()[0] if operation.split() else "generic"
                            ),
                            "preferred_choice": choice,
                            "confidence": confidence,
                        },
                    )

        except Exception:
            pass

    def _combine_ai_work_with_guidance(
        self,
        ai_work_result: Dict[str, Any],
        response: Dict[str, Any],
        guidance_options: Dict[str, str],
    ) -> Dict[str, Any]:
        """Combine AI agent work with user guidance."""
        user_responses = response.get("user_responses", [])
        user_choice = user_responses[0] if user_responses else "A"

        return {
            "action": "proceed_with_collaborative_guidance",
            "ai_work": ai_work_result,
            "user_choice": user_choice,
            "guidance_applied": guidance_options.get(user_choice, "Custom guidance"),
            "confidence": response.get("confidence", 0.8),
        }

    def _apply_defaults_to_ai_work(
        self, ai_work_result: Dict[str, Any], operation: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply smart defaults to AI agent work when no guidance received."""
        # Use the most common choice from learning history
        smart_choice = self._get_most_common_choice(operation)

        return {
            "action": "proceed_with_smart_defaults",
            "ai_work": ai_work_result,
            "smart_choice": smart_choice,
            "reason": "timeout_collaborative_fallback",
        }

    def _get_most_common_choice(self, operation: str) -> str:
        """Get the most common user choice for this operation type."""
        try:
            history = self.learning_system.get_learning_history(limit=50)

            choices: Dict[str, int] = {}
            for event in history:
                if event.get("event_type") == "user_preference_learned":
                    op_type = event.get("context", {}).get("operation_type", "")
                    if op_type in operation.lower() or operation.lower() in op_type:
                        choice = event.get("context", {}).get("preferred_choice", "A")
                        choices[choice] = choices.get(choice, 0) + 1

            if choices:
                most_common = max(choices.items(), key=lambda x: x[1])
                return str(most_common[0])

        except Exception:
            pass

        return "A"  # Default to first option


def get_ai_gate_mediator(project_root: Path) -> AIGateMediator:
    """Get or create AI gate mediator for the project."""
    return AIGateMediator(project_root)
