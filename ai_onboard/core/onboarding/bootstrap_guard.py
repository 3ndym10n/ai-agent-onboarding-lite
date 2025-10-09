"""Bootstrap guard that enforces the charter -> state -> plan onboarding flow."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Set, Tuple


class OnboardingStage(Enum):
    """Represents the initialization stage for a project."""

    UNINITIALIZED = "uninitialized"
    NEEDS_STATE = "needs_state"
    NEEDS_PLAN = "needs_plan"
    READY = "ready"


@dataclass(frozen=True)
class StageGuidance:
    """Guidance returned when onboarding is incomplete."""

    message: str
    next_command: Optional[str]


class BootstrapGuard:
    """Checks onboarding prerequisites and blocks commands until complete."""

    _ALWAYS_ALLOWED: Set[str] = {"help", "version", "quickstart", "doctor"}
    _STAGE_ALLOWED: Dict[OnboardingStage, Set[str]] = {
        OnboardingStage.UNINITIALIZED: {"charter", "prompt", "interrogate", "quickstart", "doctor"},
        OnboardingStage.NEEDS_STATE: {"analyze", "charter", "prompt", "interrogate", "quickstart", "doctor"},
        OnboardingStage.NEEDS_PLAN: {
            "plan",
            "analyze",
            "charter",
            "prompt",
            "interrogate",
            "quickstart",
            "doctor",
        },
        OnboardingStage.READY: set(),
    }

    _GUIDANCE: Dict[OnboardingStage, StageGuidance] = {
        OnboardingStage.UNINITIALIZED: StageGuidance(
            message=(
                "Project onboarding blocked: no charter found. "
                "Run `ai_onboard charter --interrogate` or `ai_onboard quickstart` first."
            ),
            next_command="ai_onboard charter --interrogate",
        ),
        OnboardingStage.NEEDS_STATE: StageGuidance(
            message="Project onboarding blocked: run `ai_onboard analyze` to capture the current state.",
            next_command="ai_onboard analyze",
        ),
        OnboardingStage.NEEDS_PLAN: StageGuidance(
            message=(
                "Project onboarding blocked: no project plan detected. "
                "Run `ai_onboard plan --analyze-codebase` to generate the initial plan."
            ),
            next_command="ai_onboard plan --analyze-codebase",
        ),
        OnboardingStage.READY: StageGuidance(message="", next_command=None),
    }

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()

    # ------------------------------------------------------------------ #
    # Stage detection helpers
    # ------------------------------------------------------------------ #
    def _charter_path(self) -> Path:
        return self.project_root / ".ai_onboard" / "charter.json"

    def _state_path(self) -> Path:
        return self.project_root / ".ai_onboard" / "state.json"

    def _plan_paths(self) -> Tuple[Path, Path]:
        base = self.project_root / ".ai_onboard"
        return base / "project_plan.json", base / "plan.json"

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def get_stage(self) -> OnboardingStage:
        """Return the current onboarding stage for this project."""
        if not self._charter_path().exists():
            return OnboardingStage.UNINITIALIZED

        if not self._state_path().exists():
            return OnboardingStage.NEEDS_STATE

        plan_paths = self._plan_paths()
        if not any(path.exists() for path in plan_paths):
            return OnboardingStage.NEEDS_PLAN

        return OnboardingStage.READY

    def get_requirements_status(self) -> Dict[str, bool]:
        """Return the presence of key onboarding artifacts."""
        plan_paths = self._plan_paths()
        return {
            "charter": self._charter_path().exists(),
            "state": self._state_path().exists(),
            "plan": any(path.exists() for path in plan_paths),
        }

    def get_guidance(self, stage: Optional[OnboardingStage] = None) -> StageGuidance:
        """Return guidance for the given stage (defaults to current stage)."""
        return self._GUIDANCE[stage or self.get_stage()]

    def check_command(self, command: Optional[str]) -> Tuple[bool, str, OnboardingStage]:
        """
        Determine whether the supplied command is allowed in the current stage.

        Returns:
            Tuple of (allowed, message, stage). ``message`` is an empty string when allowed.
        """
        stage = self.get_stage()
        if stage is OnboardingStage.READY:
            return True, "", stage

        normalized = (command or "").replace("_", "-")
        if normalized in self._ALWAYS_ALLOWED:
            return True, "", stage

        if normalized in self._STAGE_ALLOWED.get(stage, set()):
            return True, "", stage

        guidance = self.get_guidance(stage)
        return False, guidance.message, stage
