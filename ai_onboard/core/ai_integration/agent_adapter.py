"""High-level adapter for GPT-style agents integrating ai_onboard guardrails."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from ..onboarding import BootstrapGuard, OnboardingStage
from ..vision.vision_alignment_detector import AlignmentAssessment
from .decision_enforcer import get_decision_enforcer
from .user_preference_learning import (
    InteractionType,
    UserPreference,
    get_user_preference_learning_system,
)


class AIOnboardAgentAdapter:
    """Convenience wrapper that exposes alignment + preference recording.

    Typical usage from an LLM agent loop::

        adapter = AIOnboardAgentAdapter(Path.cwd())
        result = adapter.assess_message("Add email validation")
        if result["assessment"].decision == "block":
            ...

    The adapter automatically records interactions with the preference system so
    repeated agent conversations gradually personalise behaviour.
    """

    def __init__(self, project_root: Path, *, agent_id: str = "assistant") -> None:
        self.project_root = Path(project_root).resolve()
        self.agent_id = agent_id
        self._decision_enforcer = get_decision_enforcer(self.project_root)
        self._preference_system = get_user_preference_learning_system(self.project_root)
        self._bootstrap_guard = BootstrapGuard(self.project_root)

    # ------------------------------------------------------------------
    # Alignment evaluation
    # ------------------------------------------------------------------
    def assess_message(
        self,
        message: str,
        *,
        user_id: str = "vibe_coder",
        metadata: Optional[Dict[str, Any]] = None,
        record_preferences: bool = True,
    ) -> Dict[str, Any]:
        """Assess a natural language message for alignment and optionally log it.

        Returns a dictionary containing the raw :class:`AlignmentAssessment` and a
        serialised list of recently learned preferences (may be empty).
        """

        metadata_payload = metadata or {}

        stage = self._bootstrap_guard.get_stage()
        if stage is not OnboardingStage.READY:
            guidance = self._bootstrap_guard.get_guidance(stage)
            assessment = AlignmentAssessment(
                decision="block",
                score=0.0,
                reasons=[guidance.message],
                constraint_hits=[f"onboarding:{stage.value}"],
                matches={},
                phase_alignment={"current": None, "match": None},
                components={"alignment": 0.0, "phase": 0.0, "complexity": 0.0},
            )
            updated_preferences: List[Dict[str, Any]] = []
            if record_preferences:
                updated_preferences = self._record_alignment_interaction(
                    user_id=user_id,
                    message=message,
                    assessment=assessment,
                    metadata=metadata_payload,
                )
            return {
                "assessment": assessment,
                "updated_preferences": updated_preferences,
            }

        assessment = self._decision_enforcer.assess_alignment_for_message(
            message, metadata=metadata_payload
        )

        preferences: List[Dict[str, Any]] = []
        if record_preferences:
            preferences = self._record_alignment_interaction(
                user_id=user_id,
                message=message,
                assessment=assessment,
                metadata=metadata_payload,
            )

        return {
            "assessment": assessment,
            "updated_preferences": preferences,
        }

    # ------------------------------------------------------------------
    # Preference logging helpers
    # ------------------------------------------------------------------
    def record_gate_decision(
        self,
        *,
        user_id: str = "vibe_coder",
        gate_id: str,
        approved: bool,
        gate_type: str = "generic",
        notes: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Record a gate approval/denial and trigger preference learning."""

        context = {
            "gate_id": gate_id,
            "gate_type": gate_type,
            "agent_id": self.agent_id,
        }
        if notes:
            context["notes"] = notes

        outcome = {"approved": approved}

        self._preference_system.record_user_interaction(
            user_id=user_id,
            interaction_type=InteractionType.GATE_INTERACTION,
            context=context,
            outcome=outcome,
        )
        return self._serialize_preferences(
            self._preference_system.learn_preferences_from_interactions(user_id)
        )

    def record_command_execution(
        self,
        *,
        user_id: str = "vibe_coder",
        command: str,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Record the outcome of a command/tool execution."""

        context = {
            "command": command,
            "agent_id": self.agent_id,
        }
        if metadata:
            context.update(metadata)

        outcome = {"success": success}

        self._preference_system.record_user_interaction(
            user_id=user_id,
            interaction_type=InteractionType.COMMAND_EXECUTION,
            context=context,
            outcome=outcome,
            satisfaction_score=1.0 if success else 0.0,
        )
        return self._serialize_preferences(
            self._preference_system.learn_preferences_from_interactions(user_id)
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _record_alignment_interaction(
        self,
        *,
        user_id: str,
        message: str,
        assessment,
        metadata: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        interaction_type = InteractionType.CONVERSATIONAL_REQUEST
        outcome: Dict[str, Any] = {
            "decision": assessment.decision,
            "score": assessment.score,
        }

        if assessment.decision == "block":
            interaction_type = InteractionType.GATE_INTERACTION
            outcome["blocked"] = True
        elif assessment.decision == "review":
            outcome["requires_review"] = True

        context = {
            "message": message,
            "agent_id": self.agent_id,
            "components": assessment.components,
            "reasons": assessment.reasons,
            "phase_alignment": assessment.phase_alignment,
        }
        if assessment.constraint_hits:
            context["constraint_hits"] = assessment.constraint_hits
        if metadata:
            context.update(metadata)

        self._preference_system.record_user_interaction(
            user_id=user_id,
            interaction_type=interaction_type,
            context=context,
            outcome=outcome,
        )
        return self._serialize_preferences(
            self._preference_system.learn_preferences_from_interactions(user_id)
        )

    @staticmethod
    def _serialize_preferences(
        preferences: Optional[Iterable[UserPreference]]
    ) -> List[Dict[str, Any]]:
        if not preferences:
            return []
        serialised: List[Dict[str, Any]] = []
        for pref in preferences:
            data = asdict(pref)
            # normalise enums for JSON consumers
            if hasattr(pref.category, "value"):
                data["category"] = pref.category.value
            if hasattr(pref.preference_type, "value"):
                data["preference_type"] = pref.preference_type.value
            if hasattr(pref.confidence, "value"):
                data["confidence"] = pref.confidence.value
            serialised.append(data)
        return serialised
