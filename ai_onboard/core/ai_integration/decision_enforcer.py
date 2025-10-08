"""
Decision Enforcer - Bulletproof gate creation enforcement.

This module automatically creates gates for uncertain decisions,
regardless of whether AI agents remember to do it themselves.
"""

import inspect
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from .ai_gate_mediator import MediationResult, get_ai_gate_mediator
from .hard_gate_enforcer import get_hard_gate_enforcer
from .hard_limits_enforcer import get_hard_limits_enforcer
from .user_preference_learning import (
    InteractionType,
    get_user_preference_learning_system,
)

# Type variable for decorated functions
F = TypeVar("F", bound=Callable[..., Any])


class DecisionPoint:
    """Represents a decision point that might require a gate."""

    def __init__(
        self,
        name: str,
        question: str,
        options: Dict[str, str],
        default: Optional[str] = None,
        confidence_calculator: Optional[Callable[..., float]] = None,
    ):
        self.name = name
        self.question = question
        self.options = options
        self.default = default
        self.confidence_calculator = confidence_calculator

    def calculate_confidence(self, **kwargs) -> float:
        """Calculate confidence for this decision."""
        if self.confidence_calculator:
            return self.confidence_calculator(**kwargs)

        # Default: low confidence if no default or multiple options
        if not self.default and len(self.options) > 1:
            return 0.3  # Low confidence - need user input
        elif self.default:
            return 0.8  # High confidence - have default
        else:
            return 0.5  # Medium confidence


class DecisionEnforcer:
    """
    Enforces gate creation for decision points.

    This is the bulletproof layer that ensures gates are created
    even if AI agents forget to do it themselves.
    """

    def __init__(self, project_root: Path, confidence_threshold: float = 0.5):
        self.project_root = project_root
        self.confidence_threshold = confidence_threshold
        self.mediator = get_ai_gate_mediator(project_root)
        self.preference_system = get_user_preference_learning_system(project_root)
        self.hard_enforcer = get_hard_gate_enforcer(project_root)
        self.limits_enforcer = get_hard_limits_enforcer(project_root)

        # Registry of known decision points
        self.decision_points: Dict[str, DecisionPoint] = {}

    def register_decision(self, decision: DecisionPoint) -> None:
        """Register a decision point that should be enforced."""
        self.decision_points[decision.name] = decision

    def _determine_operation_type(
        self, decision: DecisionPoint, context: Dict[str, Any]
    ) -> str:
        """Determine the type of operation being performed for limits checking."""
        question_lower = decision.question.lower()
        context_str = str(context).lower()

        # File operations
        if any(
            word in question_lower for word in ["create file", "new file", "add file"]
        ):
            return "file_create"
        elif any(
            word in question_lower for word in ["delete file", "remove file", "rm file"]
        ):
            return "file_delete"
        elif any(
            word in question_lower
            for word in ["modify file", "edit file", "change file"]
        ):
            return "file_modify"

        # Refactoring operations
        elif any(
            word in question_lower for word in ["refactor", "restructure", "rename"]
        ):
            return "refactor"

        # Dependency operations
        elif any(
            word in question_lower
            for word in ["dependency", "package", "install", "add library"]
        ):
            return "dependency_add"

        # Bulk operations
        elif (
            any(word in question_lower for word in ["bulk", "multiple", "batch"])
            or "files_affected" in context
        ):
            return "bulk_operation"

        # Default to unknown
        return "unknown"

    def _record_user_preference(
        self,
        decision_name: str,
        decision: DecisionPoint,
        result: MediationResult,
        context: Dict[str, Any],
        agent_id: str,
    ) -> None:
        """Record user's choice as a learned preference."""
        try:
            # Extract user's choice from response
            if not result.response:
                return

            user_responses = result.response.get("user_responses", [])
            if not user_responses:
                return

            user_choice = user_responses[0]

            # Get user ID from context or use agent_id
            user_id = context.get("user_id", agent_id)
            if user_id == "system":
                user_id = "vibe_coder"  # Use actual user ID

            # Determine preference category based on decision name
            category_map = {
                "framework_choice": "framework_preference",
                "database_choice": "database_preference",
                "auth_method": "auth_preference",
                "styling_approach": "styling_preference",
                "methodology_choice": "methodology_preference",
                "project_type": "project_type_preference",
            }
            category = category_map.get(decision_name, "general_preference")

            # Record the interaction
            self.preference_system.record_user_interaction(
                user_id=user_id,
                interaction_type=InteractionType.PREFERENCE_EXPRESSION,
                context={
                    "decision_name": decision_name,
                    "decision_question": decision.question,
                    "user_choice": user_choice,
                    "available_options": decision.options,
                    "confidence": result.confidence,
                    "gate_created": result.gate_created,
                },
            )

            # The record_user_interaction call above will trigger
            # preference learning automatically through the system's
            # learning rules

        except Exception as e:
            # Don't fail the decision if preference recording fails
            print(f"[WARNING] Failed to record preference: {e}")

    def _check_learned_preference(
        self, decision_name: str, context: Dict[str, Any], agent_id: str
    ) -> Optional[str]:
        """Check if user has a learned preference for this decision."""
        try:
            user_id = context.get("user_id", agent_id)
            if user_id == "system":
                user_id = "vibe_coder"

            # Get all user preferences
            preferences = self.preference_system.get_user_preferences(user_id=user_id)

            # Look for a preference matching this decision
            for pref_key, pref in preferences.items():
                if pref.preference_key == decision_name:
                    # Get confidence as float for comparison
                    confidence_value = (
                        pref.confidence.value
                        if hasattr(pref.confidence, "value")
                        else float(pref.confidence)
                    )
                    if confidence_value >= 0.7:
                        # Strong preference exists
                        return str(pref.preference_value)

        except Exception:
            pass

        return None

    def _check_cleanup_preference(
        self,
        decision_name: str,
        context: Dict[str, Any],
        agent_id: str,
    ) -> Optional[str]:
        """Check for user's cleanup preferences."""
        try:
            # Get user ID from context or use agent_id
            user_id = context.get("user_id", agent_id)
            if user_id == "system":
                user_id = "vibe_coder"  # Use actual user ID

            # Check for cleanup preferences in preference system
            if hasattr(self.preference_system, "get_user_preferences"):
                cleanup_prefs = self.preference_system.get_user_preferences(
                    user_id, "organization_focus"
                )

                # Map decision names to preference keys
                preference_map = {
                    "temp_file_placement": "root_directory_cleanliness",
                    "cleanup_frequency": "cleanup_frequency",
                    "temp_file_retention": "temp_file_retention",
                }

                pref_key = preference_map.get(decision_name)
                if pref_key:
                    for pref_id, pref in cleanup_prefs.items():
                        if pref.preference_key == pref_key:
                            # Check confidence level
                            confidence_value = (
                                float(pref.confidence)
                                if isinstance(pref.confidence, (int, float))
                                else 0.5
                            )
                            if confidence_value >= 0.7:
                                # Strong preference exists
                                return str(pref.preference_value)

            # Check for explicit cleanup preferences in context
            if context.get("user_prefers_lean"):
                if decision_name == "temp_file_placement":
                    return "cache_dir"  # Use cache directory for lean root
                elif decision_name == "cleanup_frequency":
                    return "daily"  # Daily cleanup for lean directory
                elif decision_name == "temp_file_retention":
                    return "immediate"  # Delete immediately for lean directory

        except Exception:
            pass

        return None

    def _log_blocked_action(
        self,
        agent_id: str,
        action_type: str,
        reason: str,
        severity: str = "warning",
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a blocked action for the oversight dashboard."""
        try:
            # Import here to avoid circular imports
            from .agent_oversight_dashboard import AgentOversightDashboard

            dashboard = AgentOversightDashboard(self.project_root)
            dashboard.log_blocked_action(
                agent_id=agent_id,
                action_type=action_type,
                reason=reason,
                severity=severity,
            )
        except Exception as e:
            print(f"[DEBUG] Failed to log blocked action: {e}")

    def enforce_decision(
        self,
        decision_name: str,
        context: Dict[str, Any],
        agent_id: str = "system",
    ) -> MediationResult:
        """
        Enforce a decision point - create gate if needed.

        Args:
            decision_name: Name of registered decision
            context: Context for the decision
            agent_id: ID of the agent making the decision

        Returns:
            MediationResult with the decision outcome
        """
        if decision_name not in self.decision_points:
            raise ValueError(f"Unknown decision point: {decision_name}")

        decision = self.decision_points[decision_name]

        # Check for learned preference first
        learned_preference = self._check_learned_preference(
            decision_name, context, agent_id
        )

        # If we have a strong preference, use it and skip the gate
        if learned_preference:
            return MediationResult(
                proceed=True,
                response={
                    "user_responses": [learned_preference],
                    "user_decision": "proceed",
                    "source": "learned_preference",
                    "confidence": 0.95,
                },
                confidence=0.95,  # High confidence from learned preference
                gate_created=False,
                smart_defaults_used=True,
            )

        # Check for user cleanup preferences for cleanup-related decisions
        if decision_name in [
            "temp_file_placement",
            "cleanup_frequency",
            "temp_file_retention",
        ]:
            cleanup_preference = self._check_cleanup_preference(
                decision_name, context, agent_id
            )
            if cleanup_preference:
                return MediationResult(
                    proceed=True,
                    response={
                        "user_responses": [cleanup_preference],
                        "user_decision": "proceed",
                        "source": "cleanup_preference",
                        "confidence": 0.9,
                    },
                    confidence=0.9,  # High confidence from cleanup preference
                    gate_created=False,
                    smart_defaults_used=True,
                )

        # Calculate confidence
        confidence = decision.calculate_confidence(**context)

        # Add decision details to context
        full_context = {
            **context,
            "decision_point": decision.name,
            "question": decision.question,
            "options": decision.options,
            "default": decision.default,
        }

        # Check for hard limits before proceeding
        operation_type = self._determine_operation_type(decision, full_context)
        limits_allowed, limits_reason, limit_violation = (
            self.limits_enforcer.check_operation_allowed(
                agent_id, operation_type, full_context
            )
        )

        if not limits_allowed:
            # Operation exceeds hard limits - return blocked result
            return MediationResult(
                proceed=False,
                response={
                    "blocked": True,
                    "block_type": "hard_limits",
                    "violation_id": (
                        limit_violation.violation_id if limit_violation else None
                    ),
                    "reason": f"Hard limits: {limits_reason}",
                    "message": f"Operation '{decision.question}' exceeds safety limits",
                },
                gate_created=False,
                confidence=1.0,
                smart_defaults_used=False,
            )

        # Check for hard blocks before proceeding
        should_block, block_id, block_reason = (
            self.hard_enforcer.should_block_operation(
                agent_id, decision.question, full_context
            )
        )

        if should_block and block_id:
            # Operation is blocked - return blocked result
            return MediationResult(
                proceed=False,
                response={
                    "blocked": True,
                    "block_id": block_id,
                    "reason": (
                        f"Hard enforcement: {block_reason.value}"
                        if block_reason
                        else "Operation blocked"
                    ),
                    "message": f"Operation '{decision.question}' is blocked pending approval",
                },
                confidence=0.0,
                gate_created=True,
                smart_defaults_used=False,
            )

        # Use mediator to handle the decision
        result = self.mediator.process_agent_request(
            agent_id=agent_id,
            operation=decision.question,
            context=full_context,
        )

        # Record user preference if they made a choice
        if result.proceed and result.response:
            self._record_user_preference(
                decision_name=decision.name,
                decision=decision,
                result=result,
                context=context,
                agent_id=agent_id,
            )

        # Log blocked actions when gates are created (agent blocked from proceeding)
        elif not result.proceed and not result.gate_created:
            self._log_blocked_action(
                agent_id=agent_id,
                action_type=f"Decision enforcement: {decision_name}",
                reason="Required approval before proceeding",
                severity="warning",
                context=context,
            )

        return result

    def require_decision(
        self,
        decision_name: str,
        question: str,
        options: Dict[str, str],
        default: Optional[str] = None,
        confidence_calculator: Optional[Callable[..., float]] = None,
    ) -> Callable[[F], F]:
        """
        Decorator to enforce a decision point in a function.

        Usage:
            @enforcer.require_decision(
                "framework_choice",
                "Which framework should I use?",
                {"react": "React", "vue": "Vue", "angular": "Angular"}
            )
            def build_frontend(framework: str = None):
                # If framework is None, gate is created automatically
                # If framework is provided, gate is skipped
                ...
        """

        # Register the decision
        decision = DecisionPoint(
            name=decision_name,
            question=question,
            options=options,
            default=default,
            confidence_calculator=confidence_calculator,
        )
        self.register_decision(decision)

        def decorator(func: F) -> F:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Check if decision has already been made (parameter provided)
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())

                # Find the decision parameter (usually first parameter)
                decision_param = param_names[0] if param_names else None

                # Check if value was provided
                decision_value = kwargs.get(decision_param) if decision_param else None
                if not decision_value and args:
                    decision_value = args[0]

                # If no value provided, enforce the decision
                if decision_value is None:
                    result = self.enforce_decision(
                        decision_name=decision_name,
                        context={"function": func.__name__, **kwargs},
                        agent_id="system",
                    )

                    if result.proceed:
                        # Extract decision from result
                        user_response = result.response.get("user_responses", [])
                        if user_response:
                            decision_value = user_response[0]
                        elif default:
                            decision_value = default
                        else:
                            # Use first option as fallback
                            decision_value = list(options.keys())[0]

                        # Inject decision into kwargs
                        if decision_param:
                            kwargs[decision_param] = decision_value
                    else:
                        # User said stop
                        raise RuntimeError("User stopped execution via gate")

                # Call original function with decision
                return func(*args, **kwargs)

            return cast(F, wrapper)

        return decorator


# Global enforcer instance
_enforcer: Optional[DecisionEnforcer] = None


def get_decision_enforcer(project_root: Path) -> DecisionEnforcer:
    """Get or create the global decision enforcer."""
    global _enforcer
    if _enforcer is None or _enforcer.project_root != project_root:
        _enforcer = DecisionEnforcer(project_root)
    return _enforcer


# Convenience decorator for common use case
def require_decision(
    decision_name: str,
    question: str,
    options: Dict[str, str],
    default: Optional[str] = None,
) -> Callable[[F], F]:
    """
    Convenience decorator that uses the global enforcer.

    Usage:
        @require_decision(
            "database_choice",
            "Which database?",
            {"postgresql": "PostgreSQL", "mongodb": "MongoDB"}
        )
        def setup_database(database: str = None):
            # Gate created automatically if database is None
            print(f"Setting up {database}")
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get project root from context or use cwd
            project_root = Path.cwd()

            enforcer = get_decision_enforcer(project_root)
            decorated = enforcer.require_decision(
                decision_name, question, options, default
            )(func)
            return decorated(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


# Predefined decision points
COMMON_DECISIONS = {
    "framework_choice": DecisionPoint(
        name="framework_choice",
        question="Which frontend framework should I use?",
        options={
            "react": "React - Most popular, large ecosystem",
            "vue": "Vue - Simple, progressive framework",
            "angular": "Angular - Full-featured, opinionated",
            "svelte": "Svelte - Modern, compiled framework",
        },
    ),
    "database_choice": DecisionPoint(
        name="database_choice",
        question="Which database should I use?",
        options={
            "postgresql": "PostgreSQL - Relational, robust",
            "mongodb": "MongoDB - NoSQL, flexible",
            "sqlite": "SQLite - Lightweight, embedded",
            "mysql": "MySQL - Popular, widely supported",
        },
    ),
    "auth_method": DecisionPoint(
        name="auth_method",
        question="Which authentication method?",
        options={
            "jwt": "JWT tokens with local storage",
            "session": "Session-based with cookies",
            "oauth": "OAuth with third-party providers",
            "magic_link": "Magic link via email",
        },
    ),
    "styling_approach": DecisionPoint(
        name="styling_approach",
        question="Which styling approach?",
        options={
            "css": "Plain CSS",
            "tailwind": "Tailwind CSS - Utility-first",
            "styled_components": "Styled Components - CSS-in-JS",
            "sass": "Sass/SCSS - CSS preprocessor",
        },
    ),
    # Cleanup and organization decisions
    "temp_file_placement": DecisionPoint(
        name="temp_file_placement",
        question="Where should temporary files be created?",
        options={
            "root": "Create in root directory (not recommended)",
            "cache_dir": "Create in .ai_onboard/cache/ (recommended)",
            "temp_dir": "Create in system temp directory",
            "skip_creation": "Skip temp file creation if possible",
        },
        default="cache_dir",
        confidence_calculator=lambda **kwargs: (
            0.8 if kwargs.get("user_prefers_lean") else 0.3
        ),
    ),
    "cleanup_frequency": DecisionPoint(
        name="cleanup_frequency",
        question="How often should automatic cleanup run?",
        options={
            "never": "Never run automatic cleanup",
            "hourly": "Clean up every hour",
            "daily": "Clean up daily",
            "weekly": "Clean up weekly",
            "on_demand": "Only clean up when explicitly requested",
        },
        default="daily",
        confidence_calculator=lambda **kwargs: (
            0.7 if kwargs.get("user_prefers_lean") else 0.4
        ),
    ),
    "temp_file_retention": DecisionPoint(
        name="temp_file_retention",
        question="How long should temporary files be kept?",
        options={
            "immediate": "Delete immediately after use",
            "short": "Keep for 1 hour",
            "medium": "Keep for 24 hours",
            "long": "Keep for 7 days",
            "permanent": "Keep permanently",
        },
        default="immediate",
        confidence_calculator=lambda **kwargs: (
            0.9 if kwargs.get("user_prefers_lean") else 0.5
        ),
    ),
}


def register_common_decisions(enforcer: DecisionEnforcer) -> None:
    """Register all common decision points."""
    for decision in COMMON_DECISIONS.values():
        enforcer.register_decision(decision)
