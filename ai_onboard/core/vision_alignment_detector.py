"""
Vision Alignment Detector

Detects when actions or decisions don't align with the user's vision, charter, or project plan.
This addresses the user's need to be consulted when things might be drifting.
"""

# Import read_json, write_json from utils.py module
import importlib.util
import time
_utils_spec.loader.exec_module(_utils_module)
read_json = _utils_module.read_json
write_json = _utils_module.write_json


class AlignmentLevel(Enum):
    """Levels of alignment with vision/charter."""

    PERFECT = "perfect"  # Fully aligned
    GOOD = "good"  # Mostly aligned, minor issues
    CONCERNING = "concerning"  # Some misalignment, needs review
    CRITICAL = "critical"  # Major misalignment, must stop
    UNKNOWN = "unknown"  # Cannot determine alignment


class DriftType(Enum):
    """Types of vision drift detected."""

    VISION_MISALIGNMENT = "vision_misalignment"
    CHARTER_VIOLATION = "charter_violation"
    PROJECT_PLAN_DEVIATION = "project_plan_deviation"
    RISK_THRESHOLD_EXCEEDED = "risk_threshold_exceeded"
    TOOL_BYPASS_ATTEMPT = "tool_bypass_attempt"
    SAFETY_VIOLATION = "safety_violation"
    USER_PREFERENCE_IGNORED = "user_preference_ignored"


@dataclass
class AlignmentCheck:
    """Result of an alignment check."""

    timestamp: float
    action_description: str
    alignment_level: AlignmentLevel
    drift_types: List[DriftType] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    requires_user_input: bool = False
    blocking: bool = False
    confidence: float = 0.0  # 0-1 confidence in the assessment


@dataclass
class VisionCharter:
    """User's vision and charter preferences."""

    vibe_coder_approach: bool = True
    requires_risk_profiles: bool = True
    prefers_phased_implementation: bool = True
    wants_approval_before_changes: bool = True
    safety_first: bool = True
    practical_over_perfect: bool = True
    collaborative_development: bool = True
    rigorous_but_flexible: bool = True


class VisionAlignmentDetector:
    """
    Detects when actions don't align with the user's vision and charter.

    This system ensures:
    1. Actions align with user's "vibe coder" approach
    2. Risk profiles are provided for major changes
    3. User preferences are respected
    4. Safety protocols are followed
    5. Project plan is maintained
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.charter_path = root_path / ".ai_onboard" / "vision_charter.json"
        self.alignment_log_path = root_path / ".ai_onboard" / "alignment_checks.jsonl"

        # Ensure directories exist
        self.charter_path.parent.mkdir(parents=True, exist_ok=True)

        # Load user's vision charter
        self.vision_charter = self._load_vision_charter()

        # Alignment check history
        self.recent_checks: List[AlignmentCheck] = []

    def _load_vision_charter(self) -> VisionCharter:
        """Load the user's vision charter preferences."""
        try:
            data = read_json(self.charter_path, default={})
            return VisionCharter(**data)
        except Exception:
            # Default charter based on user's stated preferences
            return VisionCharter(
                vibe_coder_approach=True,
                requires_risk_profiles=True,
                prefers_phased_implementation=True,
                wants_approval_before_changes=True,
                safety_first=True,
                practical_over_perfect=True,
                collaborative_development=True,
                rigorous_but_flexible=True,
            )

    def _save_vision_charter(self):
        """Save the vision charter."""
        try:
            data = {
                "vibe_coder_approach": self.vision_charter.vibe_coder_approach,
                "requires_risk_profiles": self.vision_charter.requires_risk_profiles,
                "prefers_phased_implementation": self.vision_charter.prefers_phased_implementation,
                "wants_approval_before_changes": self.vision_charter.wants_approval_before_changes,
                "safety_first": self.vision_charter.safety_first,
                "practical_over_perfect": self.vision_charter.practical_over_perfect,
                "collaborative_development": self.vision_charter.collaborative_development,
                "rigorous_but_flexible": self.vision_charter.rigorous_but_flexible,
            }
            write_json(self.charter_path, data)
        except Exception as e:
            print(f"⚠️ Failed to save vision charter: {e}")

    def check_alignment(
        self,
        action_description: str,
        action_type: str,
        risk_level: str = "unknown",
        tools_used: List[str] = None,
        user_preferences_applied: bool = True,
        safety_checks_passed: bool = True,
        project_plan_aligned: bool = True,
    ) -> AlignmentCheck:
        """
        Check if an action aligns with the user's vision and charter.

        Returns an AlignmentCheck with recommendations.
        """

        if tools_used is None:
            tools_used = []

        # Initialize alignment check
        check = AlignmentCheck(
            timestamp=time.time(),
            action_description=action_description,
            alignment_level=AlignmentLevel.UNKNOWN,
            confidence=0.0,
        )

        # Check various alignment factors
        concerns = []
        drift_types = []
        recommendations = []

        # 1. Check if risk profiles are provided for major changes
        if (
            risk_level in ["high", "critical"]
            and self.vision_charter.requires_risk_profiles
        ):
            if "risk_assessment" not in tools_used:
                concerns.append("High-risk change without risk assessment")
                drift_types.append(DriftType.RISK_THRESHOLD_EXCEEDED)
                recommendations.append("Provide risk assessment before proceeding")

        # 2. Check if user wants approval before changes
        if self.vision_charter.wants_approval_before_changes:
            if action_type in ["file_deletion", "major_refactor", "system_change"]:
                concerns.append("Major change without user approval")
                drift_types.append(DriftType.USER_PREFERENCE_IGNORED)
                recommendations.append("Request user approval before proceeding")

        # 3. Check if safety protocols are followed
        if self.vision_charter.safety_first and not safety_checks_passed:
            concerns.append("Safety checks not passed")
            drift_types.append(DriftType.SAFETY_VIOLATION)
            recommendations.append("Complete safety checks before proceeding")

        # 4. Check if project plan is maintained
        if not project_plan_aligned:
            concerns.append("Action deviates from project plan")
            drift_types.append(DriftType.PROJECT_PLAN_DEVIATION)
            recommendations.append("Align action with project plan")

        # 5. Check if user preferences are applied
        if not user_preferences_applied:
            concerns.append("User preferences not applied")
            drift_types.append(DriftType.USER_PREFERENCE_IGNORED)
            recommendations.append("Apply user preferences to action")

        # 6. Check for tool bypass attempts
        if action_type in ["direct_file_change", "bypass_validation"]:
            concerns.append("Attempting to bypass system tools")
            drift_types.append(DriftType.TOOL_BYPASS_ATTEMPT)
            recommendations.append("Use appropriate system tools")

        # Determine overall alignment level
        if not concerns:
            check.alignment_level = AlignmentLevel.PERFECT
            check.confidence = 0.9
        elif len(concerns) == 1 and drift_types[0] in [
            DriftType.USER_PREFERENCE_IGNORED
        ]:
            check.alignment_level = AlignmentLevel.GOOD
            check.confidence = 0.7
        elif len(concerns) <= 2:
            check.alignment_level = AlignmentLevel.CONCERNING
            check.confidence = 0.8
            check.requires_user_input = True
        else:
            check.alignment_level = AlignmentLevel.CRITICAL
            check.confidence = 0.9
            check.requires_user_input = True
            check.blocking = True

        # Set concerns and recommendations
        check.concerns = concerns
        check.drift_types = drift_types
        check.recommendations = recommendations

        # Add to recent checks
        self.recent_checks.append(check)

        # Keep only last 50 checks
        if len(self.recent_checks) > 50:
            self.recent_checks = self.recent_checks[-50:]

        # Save to persistent storage
        self._save_alignment_check(check)

        return check

    def _save_alignment_check(self, check: AlignmentCheck):
        """Save alignment check to persistent storage."""
        try:
            check_data = {
                "timestamp": check.timestamp,
                "action_description": check.action_description,
                "alignment_level": check.alignment_level.value,
                "drift_types": [dt.value for dt in check.drift_types],
                "concerns": check.concerns,
                "recommendations": check.recommendations,
                "requires_user_input": check.requires_user_input,
                "blocking": check.blocking,
                "confidence": check.confidence,
            }

            with open(self.alignment_log_path, "a", encoding="utf-8") as f:
                import json

                f.write(json.dumps(check_data) + "\n")
        except Exception as e:
            print(f"⚠️ Failed to save alignment check: {e}")

    def display_alignment_check(self, check: AlignmentCheck):
        """Display alignment check results to the user."""

        # Alignment emoji mapping
        alignment_emoji = {
            AlignmentLevel.PERFECT: "🌟",
            AlignmentLevel.GOOD: "✅",
            AlignmentLevel.CONCERNING: "⚠️",
            AlignmentLevel.CRITICAL: "🚨",
            AlignmentLevel.UNKNOWN: "❓",
        }

        print(f"\n🎯 VISION ALIGNMENT CHECK")
        print(f"=" * 50)
        print(f"📝 Action: {check.action_description}")
        print(
            f"{alignment_emoji[check.alignment_level]} Alignment: {check.alignment_level.value.upper()}"
        )
        print(f"🎯 Confidence: {check.confidence:.1%}")

        if check.concerns:
            print(f"\n⚠️ Concerns:")
            for concern in check.concerns:
                print(f"   • {concern}")

        if check.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in check.recommendations:
                print(f"   • {rec}")

        if check.requires_user_input:
            print(f"\n👤 USER INPUT REQUIRED")
            if check.blocking:
                print(f"🚫 This action is BLOCKED until resolved")
            else:
                print(f"⚠️ Please review and provide guidance")

        print(f"=" * 50)

    def get_alignment_summary(self) -> Dict[str, Any]:
        """Get summary of recent alignment checks."""
        if not self.recent_checks:
            return {"message": "No alignment checks performed"}

        total_checks = len(self.recent_checks)
        perfect_count = len(
            [
                c
                for c in self.recent_checks
                if c.alignment_level == AlignmentLevel.PERFECT
            ]
        )
        good_count = len(
            [c for c in self.recent_checks if c.alignment_level == AlignmentLevel.GOOD]
        )
        concerning_count = len(
            [
                c
                for c in self.recent_checks
                if c.alignment_level == AlignmentLevel.CONCERNING
            ]
        )
        critical_count = len(
            [
                c
                for c in self.recent_checks
                if c.alignment_level == AlignmentLevel.CRITICAL
            ]
        )

        return {
            "total_checks": total_checks,
            "perfect_alignment": perfect_count,
            "good_alignment": good_count,
            "concerning_alignment": concerning_count,
            "critical_alignment": critical_count,
            "overall_alignment_score": (
                (
                    (perfect_count * 100 + good_count * 80 + concerning_count * 40)
                    / total_checks
                )
                if total_checks > 0
                else 0
            ),
            "recent_concerns": [
                c.concerns for c in self.recent_checks[-5:] if c.concerns
            ],
        }

    def update_vision_charter(self, **kwargs):
        """Update the vision charter based on user feedback."""
        for key, value in kwargs.items():
            if hasattr(self.vision_charter, key):
                setattr(self.vision_charter, key, value)

        self._save_vision_charter()
        print(f"✅ Vision charter updated")


def get_vision_alignment_detector(root_path: Path) -> VisionAlignmentDetector:
    """Get the global vision alignment detector instance."""
    global _alignment_detector_instance
    if _alignment_detector_instance is None:
        _alignment_detector_instance = VisionAlignmentDetector(root_path)
    return _alignment_detector_instance


# Global instance
_alignment_detector_instance: Optional[VisionAlignmentDetector] = None
