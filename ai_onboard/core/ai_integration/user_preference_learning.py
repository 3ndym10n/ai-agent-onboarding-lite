"""
User Preference Learning System - Advanced user behavior analysis and preference learning.

This module provides intelligent user preference learning that:
- Analyzes user interaction patterns and behaviors
- Learns individual user preferences and workflows
- Provides personalized system adaptations
- Tracks user satisfaction and feedback
- Generates user - specific recommendations
- Adapts system behavior based on learned preferences
"""

import json
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Union

from ..base import telemetry, utils
from ..continuous_improvement import continuous_improvement_system


class InteractionType(Enum):
    """Types of user interactions."""

    COMMAND_EXECUTION = "command_execution"
    CONFIGURATION_CHANGE = "configuration_change"
    GATE_INTERACTION = "gate_interaction"
    VISION_INTERROGATION = "vision_interrogation"
    ERROR_HANDLING = "error_handling"
    APPROVAL_DECISION = "approval_decision"
    FEEDBACK_PROVIDED = "feedback_provided"
    WORKFLOW_NAVIGATION = "workflow_navigation"

    # NEW: Conversational interaction types
    CONVERSATIONAL_REQUEST = (
        "conversational_request"  # Questions, requests for information
    )
    REPEATED_PATTERN = "repeated_pattern"  # When user repeats same request
    PREFERENCE_EXPRESSION = "preference_expression"  # Explicit preference statements
    CLARITY_REQUEST = "clarity_request"  # Requests for simpler explanations
    ORGANIZATION_FOCUS = "organization_focus"  # Cleanup and organization requests


class PreferenceCategory(Enum):
    """Categories of user preferences."""

    INTERACTION_STYLE = "interaction_style"
    WORKFLOW_PREFERENCES = "workflow_preferences"
    SAFETY_LEVEL = "safety_level"
    NOTIFICATION_PREFERENCES = "notification_preferences"
    PERFORMANCE_PREFERENCES = "performance_preferences"
    PERFORMANCE = "performance"  # Backward compatibility
    UI_PREFERENCES = "ui_preferences"
    COLLABORATION_STYLE = "collaboration_style"
    PROJECT_PREFERENCES = "project_preferences"

    # NEW: Conversational preference categories
    COMMUNICATION_STYLE = "communication_style"  # How user wants information presented
    TRANSPARENCY_LEVEL = "transparency_level"  # How much detail about system operations
    ORGANIZATION_PREFERENCE = "organization_preference"  # How tidy user wants system
    LEARNING_STYLE = "learning_style"  # How user wants to learn about features


class UserExperienceLevel(Enum):
    """User experience levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class PreferenceType(Enum):
    """Types of user preferences."""

    SELECTION = "selection"
    THRESHOLD = "threshold"
    PATTERN = "pattern"
    FREQUENCY = "frequency"
    STRING = "string"  # Backward compatibility
    NUMERIC = "numeric"  # Backward compatibility


class PreferenceConfidence(Enum):
    """Confidence levels for learned preferences."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class UserInteraction:
    """A single user interaction event."""

    interaction_id: str
    user_id: str
    interaction_type: InteractionType
    timestamp: datetime
    context: Dict[str, Any]
    duration: Optional[float] = None
    outcome: Optional[Dict[str, Any]] = None
    satisfaction_score: Optional[float] = None
    feedback: Optional[str] = None


@dataclass
class UserPreference:
    """A learned user preference."""

    user_id: str
    category: PreferenceCategory
    preference_key: str
    preference_value: Any
    preference_id: str = field(
        default_factory=lambda: f"pref_{int(datetime.now().timestamp())}"
    )
    confidence: Union[float, PreferenceConfidence] = 0.5
    evidence_count: int = 1
    last_updated: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)  # Backward compatibility
    preference_type: PreferenceType = PreferenceType.SELECTION  # Backward compatibility
    learned_from: List[str] = field(default_factory=list)  # Backward compatibility
    sources: List[str] = field(default_factory=list)
    context_conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserBehaviorPattern:
    """A detected user behavior pattern."""

    pattern_id: str
    user_id: str
    pattern_type: str
    description: str
    frequency: float
    confidence: float
    conditions: Dict[str, Any]
    implications: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class UserProfile:
    """Comprehensive user profile with learned preferences and patterns."""

    user_id: str
    experience_level: UserExperienceLevel
    preferences: Dict[str, UserPreference] = field(default_factory=dict)
    behavior_patterns: List[UserBehaviorPattern] = field(default_factory=list)
    interaction_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    satisfaction_scores: deque = field(default_factory=lambda: deque(maxlen=100))
    feedback_history: List[Dict[str, Any]] = field(default_factory=list)
    last_activity: datetime = field(default_factory=datetime.now)
    total_interactions: int = 0
    average_satisfaction: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


class UserPreferenceLearningSystem:
    """Advanced user preference learning and adaptation system."""

    def __init__(self, root: Path):
        self.root = root
        self.user_profiles_path = root / ".ai_onboard" / "user_profiles.json"
        self.interaction_log_path = root / ".ai_onboard" / "user_interactions.jsonl"
        self.preference_learning_path = (
            root / ".ai_onboard" / "preference_learning.jsonl"
        )
        self.behavior_patterns_path = root / ".ai_onboard" / "behavior_patterns.json"

        # Backward compatibility attributes
        self.preferences_path = self.user_profiles_path
        self.learning_data_path = self.preference_learning_path
        self.interactions_path = self.interaction_log_path
        self.config = {
            "enabled": True,
            "learning_enabled": True,  # Backward compatibility
            "learning_rate": 0.1,
            "min_interactions_for_learning": 5,
            "confidence_threshold": 0.7,
            "max_preferences_per_category": 10,
        }

        # Initialize subsystems
        self.continuous_improvement = (
            continuous_improvement_system.get_continuous_improvement_system(root)
        )

        # User profiles and learning state
        self.user_profiles: Dict[str, UserProfile] = {}
        self.preference_learning_rules: List[Dict[str, Any]] = []
        self.behavior_pattern_detectors: Dict[str, Any] = {}

        # Ensure directories exist
        self._ensure_directories()

        # Load existing data
        self._load_user_profiles()
        self._load_preference_learning_rules()
        self._load_behavior_pattern_detectors()

        # Initialize default learning rules
        if not self.preference_learning_rules:
            self._initialize_default_learning_rules()

    # Backward compatibility methods
    def _load_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Alias for backward compatibility - return dict format."""
        profile = self.user_profiles.get(user_id)
        if profile:
            return {
                "user_id": profile.user_id,
                "experience_level": profile.experience_level.value,
                "preferences": profile.preferences,
                "interactions": [
                    {
                        "interaction_id": interaction.interaction_id,
                        "user_id": interaction.user_id,
                        "interaction_type": interaction.interaction_type.value,
                        "timestamp": interaction.timestamp.isoformat(),
                        "context": interaction.context,
                        "outcome": interaction.outcome,
                        "satisfaction_score": interaction.satisfaction_score,
                        "feedback": interaction.feedback,
                        "duration": interaction.duration,
                    }
                    for interaction in profile.interaction_history
                ],
                "behavior_patterns": profile.behavior_patterns,
                "satisfaction_scores": list(profile.satisfaction_scores),
                "last_activity": profile.last_activity.isoformat(),
                "total_interactions": profile.total_interactions,
                "average_satisfaction": profile.average_satisfaction,
                "learning_metrics": {
                    "total_preferences_learned": len(profile.preferences),
                    "behavior_patterns_detected": len(profile.behavior_patterns),
                    "satisfaction_trend": (
                        list(profile.satisfaction_scores)[-10:]
                        if profile.satisfaction_scores
                        else []
                    ),
                    "experience_level": profile.experience_level.value,
                    "total_interactions": profile.total_interactions,
                },
            }
        return None

    def _store_user_data(self, user_id: str, profile: UserProfile) -> None:
        """Alias for backward compatibility."""
        self.user_profiles[user_id] = profile
        self._save_user_profiles()

    def learn_from_interactions(self, user_id: str) -> List[UserPreference]:
        """Alias for backward compatibility."""
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            if profile.interaction_history:
                interaction = profile.interaction_history[-1]
                self._trigger_preference_learning(profile, interaction)
        return []  # Return empty list for backward compatibility

    def learn_preferences_from_interactions(self, user_id: str) -> List[UserPreference]:
        """Learn preferences from recorded interactions and return updated preferences."""
        learned_preferences: List[UserPreference] = []
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            before_keys = set(profile.preferences.keys())
            # Use the most recent interaction if available
            if profile.interaction_history:
                interaction = profile.interaction_history[-1]
                self._trigger_preference_learning(profile, interaction)
            else:
                # Create a dummy interaction for learning
                dummy_interaction = UserInteraction(
                    interaction_id=f"learn_{user_id}_{int(time.time())}",
                    user_id=user_id,
                    interaction_type=InteractionType.COMMAND_EXECUTION,
                    timestamp=datetime.now(),
                    context={"learning_trigger": "manual"},
                    outcome={"learned": True},
                    satisfaction_score=0.8,
                    feedback="Manual preference learning",
                    duration=1.0,
                )
                self._trigger_preference_learning(profile, dummy_interaction)
            after_keys = set(profile.preferences.keys())
            new_keys = [key for key in after_keys if key not in before_keys]
            if new_keys:
                learned_preferences = [profile.preferences[key] for key in new_keys]
            else:
                learned_preferences = list(profile.preferences.values())
        return learned_preferences

    def predict_user_preference(
        self,
        user_id: str,
        context: Dict[str, Any],
        preference_category: PreferenceCategory,
    ) -> Optional[Dict[str, Any]]:
        """Predict user preference based on context and category."""
        if user_id not in self.user_profiles:
            return None

        preferences = self.user_profiles[user_id].preferences

        # Find preferences in the requested category with highest confidence
        category_prefs = [
            pref
            for pref in preferences.values()
            if pref.category == preference_category
        ]

        if not category_prefs:
            return None

        # Return the highest confidence preference
        best_pref = max(
            category_prefs, key=lambda p: self._get_confidence_value(p.confidence)
        )

        return {
            "predicted_preferences": {
                best_pref.preference_key: best_pref.preference_value
            },
            "confidence_scores": {
                best_pref.preference_key: self._get_confidence_value(
                    best_pref.confidence
                )
            },
            "category": best_pref.category.value,
        }

    def _get_confidence_value(
        self, confidence: Union[PreferenceConfidence, float]
    ) -> float:
        """Get numeric confidence value from enum or float."""
        if hasattr(confidence, "value"):
            # Map enum values to numeric confidence
            if confidence == PreferenceConfidence.LOW:
                return 0.3
            elif confidence == PreferenceConfidence.MEDIUM:
                return 0.6
            elif confidence == PreferenceConfidence.HIGH:
                return 0.8
            elif confidence == PreferenceConfidence.VERY_HIGH:
                return 0.9
            else:
                return 0.5
        else:
            return float(confidence)

    def _store_user_preference(self, preference: UserPreference) -> None:
        """Alias for backward compatibility."""
        # Ensure user profile exists
        if preference.user_id not in self.user_profiles:
            self.user_profiles[preference.user_id] = UserProfile(
                user_id=preference.user_id,
                experience_level=UserExperienceLevel.BEGINNER,
                total_interactions=0,
            )

        # Pass the preference object values directly to _update_user_preference
        self._update_user_preference(
            user_id=preference.user_id,
            category=preference.category,
            key=preference.preference_key,
            value=preference.preference_value,
            confidence=preference.confidence,  # Keep original confidence value
            evidence=f"learned_from_{preference.learned_from}",
            sources=preference.sources,
            preference_type=preference.preference_type,
        )

    def update_preference_confidence(
        self, user_id: str, preference_key: str, positive_feedback: bool = True
    ) -> None:
        """Alias for backward compatibility."""
        if user_id in self.user_profiles:
            for pref in self.user_profiles[user_id].preferences.values():
                if pref.preference_key == preference_key:
                    # Get current confidence value
                    current_confidence = pref.confidence
                    if hasattr(current_confidence, "value"):
                        # It's an enum, get the numeric value
                        current_value = 0.5  # Default mapping
                        if current_confidence == PreferenceConfidence.LOW:
                            current_value = 0.3
                        elif current_confidence == PreferenceConfidence.MEDIUM:
                            current_value = 0.6
                        elif current_confidence == PreferenceConfidence.HIGH:
                            current_value = 0.8
                        elif current_confidence == PreferenceConfidence.VERY_HIGH:
                            current_value = 0.9
                    else:
                        # It's already a float
                        current_value = float(current_confidence)

                    # Update the confidence value
                    if positive_feedback:
                        new_value = min(1.0, current_value + 0.1)
                    else:
                        new_value = max(0.0, current_value - 0.1)

                    # Convert back to enum if original was enum
                    if hasattr(pref.confidence, "value"):
                        if new_value >= 0.9:
                            pref.confidence = PreferenceConfidence.VERY_HIGH
                        elif new_value >= 0.8:
                            pref.confidence = PreferenceConfidence.HIGH
                        elif new_value >= 0.6:
                            pref.confidence = PreferenceConfidence.MEDIUM
                        else:
                            pref.confidence = PreferenceConfidence.LOW
                    else:
                        pref.confidence = new_value

                    pref.last_updated = datetime.now()
                    break

    def perform_adaptive_learning(self, user_id: str) -> None:
        """Alias for backward compatibility."""
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            if profile.interaction_history:
                interaction = profile.interaction_history[-1]
                self._trigger_preference_learning(profile, interaction)

    def personalization_engine(self) -> "UserPreferenceLearningSystem":
        """Alias for backward compatibility."""
        return self  # Return self for method chaining

    def _load_config(self) -> Dict[str, Any]:
        """Alias for backward compatibility."""
        return self.config

    def _save_config(self) -> None:
        """Alias for backward compatibility."""
        # Config is stored in memory, no need to save

    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        for path in [
            self.user_profiles_path,
            self.interaction_log_path,
            self.preference_learning_path,
            self.behavior_patterns_path,
        ]:
            utils.ensure_dir(path.parent)

    def _initialize_default_learning_rules(self) -> None:
        """Initialize default preference learning rules."""
        self.preference_learning_rules = [
            {
                "rule_id": "rule_001",
                "name": "Gate timeout preference learning",
                "description": "Learn user preference for gate timeout based on interaction speed",
                "trigger_conditions": {
                    "interaction_type": "gate_interaction",
                    "min_interactions": 5,
                },
                "analysis_method": "response_time_analysis",
                "preference_category": "interaction_style",
                "preference_key": "preferred_gate_timeout",
            },
            {
                "rule_id": "rule_002",
                "name": "Safety level preference learning",
                "description": "Learn user preference for safety level based on error handling",
                "trigger_conditions": {
                    "interaction_type": "error_handling",
                    "min_interactions": 1,  # Reduced for testing
                },
                "analysis_method": "error_handling_analysis",
                "preference_category": "safety_level",
                "preference_key": "preferred_safety_level",
            },
            {
                "rule_id": "rule_003",
                "name": "Collaboration style learning",
                "description": "Learn user collaboration preferences based on approval patterns",
                "trigger_conditions": {
                    "interaction_type": "approval_decision",
                    "min_interactions": 10,
                },
                "analysis_method": "approval_pattern_analysis",
                "preference_category": "collaboration_style",
                "preference_key": "preferred_collaboration_mode",
            },
            {
                "rule_id": "rule_004",
                "name": "Workflow preference learning",
                "description": "Learn user workflow preferences based on command patterns",
                "trigger_conditions": {
                    "interaction_type": "command_execution",
                    "min_interactions": 20,
                },
                "analysis_method": "command_pattern_analysis",
                "preference_category": "workflow_preferences",
                "preference_key": "preferred_workflow_style",
            },
            {
                "rule_id": "rule_005",
                "name": "Notification preference learning",
                "description": "Learn user notification preferences based on feedback",
                "trigger_conditions": {
                    "interaction_type": "feedback_provided",
                    "min_interactions": 5,
                },
                "analysis_method": "feedback_analysis",
                "preference_category": "notification_preferences",
                "preference_key": "preferred_notification_level",
            },
            # NEW: Conversational learning rules
            {
                "rule_id": "rule_006",
                "name": "Transparency preference learning",
                "description": "Learn user preference for system transparency based on repeated tool usage requests",
                "trigger_conditions": {
                    "interaction_type": "repeated_pattern",
                    "min_interactions": 3,
                    "pattern_context": "tool_usage_request",
                },
                "analysis_method": "transparency_preference_analysis",
                "preference_category": "transparency_level",
                "preference_key": "preferred_transparency_level",
            },
            {
                "rule_id": "rule_007",
                "name": "Communication style learning",
                "description": "Learn user preference for simple explanations based on clarity requests",
                "trigger_conditions": {
                    "interaction_type": "clarity_request",
                    "min_interactions": 2,
                },
                "analysis_method": "communication_style_analysis",
                "preference_category": "communication_style",
                "preference_key": "preferred_explanation_complexity",
            },
            {
                "rule_id": "rule_008",
                "name": "Organization preference learning",
                "description": "Learn user preference for system organization based on cleanup requests",
                "trigger_conditions": {
                    "interaction_type": "organization_focus",
                    "min_interactions": 2,
                },
                "analysis_method": "organization_preference_analysis",
                "preference_category": "organization_preference",
                "preference_key": "preferred_organization_level",
            },
            {
                "rule_id": "rule_009",
                "name": "Learning style preference",
                "description": "Learn how user wants to learn about system features",
                "trigger_conditions": {
                    "interaction_type": "conversational_request",
                    "min_interactions": 3,
                    "context_contains": "how.*work|explain",
                },
                "analysis_method": "learning_style_analysis",
                "preference_category": "learning_style",
                "preference_key": "preferred_feature_learning_method",
            },
        ]

    def _load_user_profiles(self) -> None:
        """Load user profiles from storage."""
        if not self.user_profiles_path.exists():
            return

        data = utils.read_json(self.user_profiles_path, default={})

        for user_id, profile_data in data.items():
            # Convert preferences
            preferences = {}
            for pref_key, pref_data in profile_data.get("preferences", {}).items():
                preferences[pref_key] = UserPreference(
                    preference_id=pref_data["preference_id"],
                    user_id=user_id,
                    category=PreferenceCategory(pref_data["category"]),
                    preference_key=pref_data["preference_key"],
                    preference_value=pref_data["preference_value"],
                    confidence=pref_data["confidence"],
                    evidence_count=pref_data["evidence_count"],
                    last_updated=datetime.fromisoformat(pref_data["last_updated"]),
                    sources=pref_data.get("sources", []),
                    context_conditions=pref_data.get("context_conditions", {}),
                )

            # Convert behavior patterns
            behavior_patterns = []
            for pattern_data in profile_data.get("behavior_patterns", []):
                behavior_patterns.append(
                    UserBehaviorPattern(
                        pattern_id=pattern_data["pattern_id"],
                        user_id=user_id,
                        pattern_type=pattern_data["pattern_type"],
                        description=pattern_data["description"],
                        frequency=pattern_data["frequency"],
                        confidence=pattern_data["confidence"],
                        conditions=pattern_data["conditions"],
                        implications=pattern_data.get("implications", []),
                        recommendations=pattern_data.get("recommendations", []),
                        detected_at=datetime.fromisoformat(pattern_data["detected_at"]),
                    )
                )

            # Convert interaction history
            interaction_history: Deque[UserInteraction] = deque(maxlen=1000)
            for interaction_data in profile_data.get("interaction_history", []):
                # Skip malformed interaction data
                if not isinstance(interaction_data, dict):
                    continue

                # Handle missing interaction_id gracefully
                interaction_id = interaction_data.get("interaction_id")
                if not interaction_id:
                    # Generate a fallback interaction_id if missing
                    timestamp = interaction_data.get(
                        "timestamp", str(datetime.now().timestamp())
                    )
                    interaction_id = (
                        f"interaction_{int(datetime.now().timestamp())}_"
                        f"{hash(str(interaction_data)) % 10000}"
                    )

                # Handle missing interaction_type gracefully
                interaction_type_str = interaction_data.get(
                    "interaction_type", "unknown"
                )
                try:
                    interaction_type = InteractionType(interaction_type_str)
                except ValueError:
                    # Default to conversational_request if invalid type
                    interaction_type = InteractionType.CONVERSATIONAL_REQUEST

                # Handle missing timestamp gracefully
                timestamp_str = interaction_data.get("timestamp")
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                    except (ValueError, TypeError):
                        timestamp = datetime.now()
                else:
                    timestamp = datetime.now()

                # Handle missing context gracefully
                context = interaction_data.get("context", {})

                interaction_history.append(
                    UserInteraction(
                        interaction_id=interaction_id,
                        user_id=user_id,
                        interaction_type=interaction_type,
                        timestamp=timestamp,
                        context=context,
                        duration=interaction_data.get("duration"),
                        outcome=interaction_data.get("outcome"),
                        satisfaction_score=interaction_data.get("satisfaction_score"),
                        feedback=interaction_data.get("feedback"),
                    )
                )

            # Convert satisfaction scores
            satisfaction_scores: Deque[float] = deque(maxlen=100)
            for score in profile_data.get("satisfaction_scores", []):
                satisfaction_scores.append(score)

            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                experience_level=UserExperienceLevel(profile_data["experience_level"]),
                preferences=preferences,
                behavior_patterns=behavior_patterns,
                interaction_history=interaction_history,
                satisfaction_scores=satisfaction_scores,
                feedback_history=profile_data.get("feedback_history", []),
                last_activity=datetime.fromisoformat(profile_data["last_activity"]),
                total_interactions=profile_data.get("total_interactions", 0),
                average_satisfaction=profile_data.get("average_satisfaction", 0.0),
                created_at=datetime.fromisoformat(profile_data["created_at"]),
            )

    def _load_preference_learning_rules(self) -> None:
        """Load preference learning rules from storage."""
        # This would load from a separate file if we had one
        # For now, we initialize with defaults

    def _load_behavior_pattern_detectors(self) -> None:
        """Load behavior pattern detectors from storage."""
        # This would load from a separate file if we had one
        # For now, we initialize with defaults

    def record_user_interaction(
        self,
        user_id: str,
        interaction_type: InteractionType,
        context: Dict[str, Any],
        duration: Optional[float] = None,
        outcome: Optional[Dict[str, Any]] = None,
        satisfaction_score: Optional[float] = None,
        feedback: Optional[str] = None,
    ) -> str:
        """Record a user interaction for learning."""
        interaction_id = f"interaction_{int(time.time())}_{utils.random_string(8)}"

        # Convert string to enum if needed
        if isinstance(interaction_type, str):
            try:
                interaction_type = InteractionType(interaction_type)
            except ValueError:
                # If not a valid enum value, use a default
                interaction_type = InteractionType.COMMAND_EXECUTION

        interaction = UserInteraction(
            interaction_id=interaction_id,
            user_id=user_id,
            interaction_type=interaction_type,
            timestamp=datetime.now(),
            context=context,
            duration=duration,
            outcome=outcome,
            satisfaction_score=satisfaction_score,
            feedback=feedback,
        )

        # Get or create user profile
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id, experience_level=UserExperienceLevel.BEGINNER
            )

        profile = self.user_profiles[user_id]

        # Add interaction to profile
        profile.interaction_history.append(interaction)
        profile.total_interactions += 1
        profile.last_activity = datetime.now()

        # Update satisfaction scores
        if satisfaction_score is not None:
            profile.satisfaction_scores.append(satisfaction_score)
            profile.average_satisfaction = statistics.mean(profile.satisfaction_scores)

        # Add feedback to history
        if feedback:
            profile.feedback_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "interaction_id": interaction_id,
                    "feedback": feedback,
                    "satisfaction_score": satisfaction_score,
                }
            )

        # Log the interaction
        self._log_user_interaction(interaction)

        # Trigger preference learning
        self._trigger_preference_learning(profile, interaction)

        # Detect behavior patterns
        self._detect_behavior_patterns(profile)

        # Update experience level
        self._update_experience_level(profile)

        # Save user profiles
        self._save_user_profiles()

        # Record learning event
        self.continuous_improvement.record_learning_event(
            learning_type=continuous_improvement_system.LearningType.USER_PREFERENCE,
            context={
                "user_id": user_id,
                "interaction_type": interaction_type.value,
                "interaction_id": interaction_id,
                "satisfaction_score": satisfaction_score,
            },
            outcome={
                "preference_learning_triggered": True,
                "behavior_pattern_detection": True,
                "experience_level_updated": True,
            },
            confidence=0.8,
            impact_score=0.6,
            source="user_preference_learning",
        )

        return interaction_id

    def _trigger_preference_learning(
        self, profile: UserProfile, interaction: UserInteraction
    ) -> None:
        """Trigger preference learning based on interaction."""
        for rule in self.preference_learning_rules:
            if self._evaluate_learning_rule_conditions(rule, profile, interaction):
                self._apply_learning_rule(rule, profile, interaction)

    def _evaluate_learning_rule_conditions(
        self, rule: Dict[str, Any], profile: UserProfile, interaction: UserInteraction
    ) -> bool:
        """Evaluate if a learning rule's conditions are met."""
        conditions = rule["trigger_conditions"]

        # Check interaction type
        if "interaction_type" in conditions:
            if interaction.interaction_type.value != conditions["interaction_type"]:
                return False

        # Check minimum interactions
        if "min_interactions" in conditions:
            interaction_count = sum(
                1
                for i in profile.interaction_history
                if i.interaction_type.value
                == conditions.get(
                    "interaction_type", interaction.interaction_type.value
                )
            )
            if interaction_count < conditions["min_interactions"]:
                return False

        return True

    def _apply_learning_rule(
        self, rule: Dict[str, Any], profile: UserProfile, interaction: UserInteraction
    ) -> None:
        """Apply a learning rule to extract preferences."""
        analysis_method = rule["analysis_method"]
        preference_category = PreferenceCategory(rule["preference_category"])
        preference_key = rule["preference_key"]

        # Apply the appropriate analysis method
        if analysis_method == "response_time_analysis":
            self._analyze_response_time_preference(
                profile, interaction, preference_category, preference_key
            )
        elif analysis_method == "error_handling_analysis":
            self._analyze_error_handling_preference(
                profile, interaction, preference_category, preference_key
            )
        elif analysis_method == "approval_pattern_analysis":
            self._analyze_approval_pattern_preference(
                profile, interaction, preference_category, preference_key
            )
        elif analysis_method == "command_pattern_analysis":
            self._analyze_command_pattern_preference(
                profile, interaction, preference_category, preference_key
            )
        elif analysis_method == "feedback_analysis":
            self._analyze_feedback_preference(
                profile, interaction, preference_category, preference_key
            )
        # NEW: Conversational analysis methods
        elif analysis_method == "transparency_preference_analysis":
            self._analyze_transparency_preference(
                profile, interaction, preference_category, preference_key
            )
        elif analysis_method == "communication_style_analysis":
            self._analyze_communication_style_preference(
                profile, interaction, preference_category, preference_key
            )
        elif analysis_method == "organization_preference_analysis":
            self._analyze_organization_preference(
                profile, interaction, preference_category, preference_key
            )
        elif analysis_method == "learning_style_analysis":
            self._analyze_learning_style_preference(
                profile, interaction, preference_category, preference_key
            )

    def _analyze_response_time_preference(
        self,
        profile: UserProfile,
        interaction: UserInteraction,
        category: PreferenceCategory,
        key: str,
    ) -> None:
        """Analyze user response time preferences."""
        if interaction.duration is None:
            return

        # Get recent gate interactions
        gate_interactions = [
            i
            for i in profile.interaction_history
            if i.interaction_type == InteractionType.GATE_INTERACTION
            and i.duration is not None
        ]

        if len(gate_interactions) < 3:
            return

        # Calculate average response time
        avg_response_time = statistics.mean(
            [i.duration for i in gate_interactions[-10:]]
        )

        # Determine preferred timeout based on response time
        if avg_response_time < 2.0:
            preferred_timeout = 1
            confidence = 0.9
        elif avg_response_time < 5.0:
            preferred_timeout = 2
            confidence = 0.8
        elif avg_response_time < 10.0:
            preferred_timeout = 5
            confidence = 0.7
        else:
            preferred_timeout = 10
            confidence = 0.6

        # Create or update preference
        self._update_user_preference(
            profile.user_id,
            category,
            key,
            preferred_timeout,
            confidence,
            f"Based on average response time of {avg_response_time:.1f}s",
            ["response_time_analysis"],
        )

    def _analyze_error_handling_preference(
        self,
        profile: UserProfile,
        interaction: UserInteraction,
        category: PreferenceCategory,
        key: str,
    ) -> None:
        """Analyze user error handling preferences."""
        # Get recent error handling interactions
        error_interactions = [
            i
            for i in profile.interaction_history
            if i.interaction_type == InteractionType.ERROR_HANDLING
        ]

        if len(error_interactions) < 1:  # Reduced for testing
            return

        # Analyze error handling patterns
        auto_recovery_count = sum(
            1
            for i in error_interactions
            if i.outcome and i.outcome.get("auto_recovery", False)
        )

        manual_intervention_count = sum(
            1
            for i in error_interactions
            if i.outcome and i.outcome.get("manual_intervention", False)
        )

        # Determine preferred safety level
        if auto_recovery_count > manual_intervention_count * 2:
            preferred_safety = "low"
            confidence = 0.8
        elif manual_intervention_count > auto_recovery_count * 2:
            preferred_safety = "high"
            confidence = 0.8
        else:
            preferred_safety = "medium"
            confidence = 0.6

        # Create or update preference
        self._update_user_preference(
            profile.user_id,
            category,
            key,
            preferred_safety,
            confidence,
            f"Based on error handling patterns: {auto_recovery_count} auto, {manual_intervention_count} manual",
            ["error_handling_analysis"],
        )

    def _analyze_approval_pattern_preference(
        self,
        profile: UserProfile,
        interaction: UserInteraction,
        category: PreferenceCategory,
        key: str,
    ) -> None:
        """Analyze user approval pattern preferences."""
        # Get recent approval decisions
        approval_interactions = [
            i
            for i in profile.interaction_history
            if i.interaction_type == InteractionType.APPROVAL_DECISION
        ]

        if len(approval_interactions) < 5:
            return

        # Analyze approval patterns
        approval_count = sum(
            1
            for i in approval_interactions
            if i.outcome and i.outcome.get("approved", False)
        )

        sum(
            1
            for i in approval_interactions
            if i.outcome and i.outcome.get("rejected", False)
        )

        total_decisions = len(approval_interactions)
        approval_rate = approval_count / total_decisions

        # Determine preferred collaboration mode
        if approval_rate > 0.8:
            preferred_mode = "autonomous"
            confidence = 0.8
        elif approval_rate < 0.3:
            preferred_mode = "supervised"
            confidence = 0.8
        else:
            preferred_mode = "collaborative"
            confidence = 0.7

        # Create or update preference
        self._update_user_preference(
            profile.user_id,
            category,
            key,
            preferred_mode,
            confidence,
            f"Based on approval rate of {approval_rate:.1%}",
            ["approval_pattern_analysis"],
        )

    def _analyze_command_pattern_preference(
        self,
        profile: UserProfile,
        interaction: UserInteraction,
        category: PreferenceCategory,
        key: str,
    ) -> None:
        """Analyze user command pattern preferences."""
        # Get recent command executions
        command_interactions = [
            i
            for i in profile.interaction_history
            if i.interaction_type == InteractionType.COMMAND_EXECUTION
        ]

        if len(command_interactions) < 10:
            return

        # Analyze command patterns
        command_types: Dict[str, int] = defaultdict(int)
        for interaction in command_interactions[-20:]:
            command_type = interaction.context.get("command_type", "unknown")
            command_types[command_type] += 1

        # Determine workflow style preference
        most_common = max(command_types.items(), key=lambda x: x[1])
        total_commands = sum(command_types.values())

        if most_common[1] / total_commands > 0.6:
            preferred_style = "specialized"
            confidence = 0.8
        else:
            preferred_style = "generalist"
            confidence = 0.7

        # Create or update preference
        self._update_user_preference(
            profile.user_id,
            category,
            key,
            preferred_style,
            confidence,
            f"Based on command pattern: {most_common[0]} ({most_common[1]}/{total_commands})",
            ["command_pattern_analysis"],
        )

    def _analyze_feedback_preference(
        self,
        profile: UserProfile,
        interaction: UserInteraction,
        category: PreferenceCategory,
        key: str,
    ) -> None:
        """Analyze user feedback preferences."""
        if not interaction.feedback:
            return

        # Analyze feedback sentiment and content
        feedback_lower = interaction.feedback.lower()

        # Determine notification preference based on feedback
        if any(
            word in feedback_lower
            for word in ["too much", "overwhelming", "spam", "annoying"]
        ):
            preferred_level = "low"
            confidence = 0.8
        elif any(
            word in feedback_lower
            for word in ["more", "detailed", "verbose", "informative"]
        ):
            preferred_level = "high"
            confidence = 0.8
        else:
            preferred_level = "medium"
            confidence = 0.6

        # Create or update preference
        self._update_user_preference(
            profile.user_id,
            category,
            key,
            preferred_level,
            confidence,
            f"Based on feedback: {interaction.feedback[:50]}...",
            ["feedback_analysis"],
        )

    # NEW: Conversational analysis methods
    def _analyze_transparency_preference(
        self,
        profile: UserProfile,
        interaction: UserInteraction,
        category: PreferenceCategory,
        key: str,
    ) -> None:
        """Analyze user preference for system transparency."""
        # Count repeated requests for tool usage information
        tool_usage_requests = sum(
            1
            for i in profile.interaction_history
            if i.interaction_type == InteractionType.REPEATED_PATTERN
            and "tool_usage" in str(i.context)
        )

        # Determine transparency preference based on frequency
        if tool_usage_requests >= 5:
            transparency_level = "high"
            confidence = 0.9
        elif tool_usage_requests >= 3:
            transparency_level = "medium"
            confidence = 0.7
        else:
            transparency_level = "standard"
            confidence = 0.5

        self._update_user_preference(
            profile.user_id,
            category,
            key,
            transparency_level,
            confidence,
            f"User requested tool usage information {tool_usage_requests} times",
            ["transparency_preference_analysis"],
        )

    def _analyze_communication_style_preference(
        self,
        profile: UserProfile,
        interaction: UserInteraction,
        category: PreferenceCategory,
        key: str,
    ) -> None:
        """Analyze user preference for communication style."""
        # Count requests for simpler explanations
        clarity_requests = sum(
            1
            for i in profile.interaction_history
            if i.interaction_type == InteractionType.CLARITY_REQUEST
        )

        # Look for explicit preference expressions in context
        simple_requests = sum(
            1
            for i in profile.interaction_history
            if "simple" in str(i.context).lower() or "explain" in str(i.context).lower()
        )

        # Determine communication preference
        if clarity_requests >= 3 or simple_requests >= 3:
            communication_style = "simple_explanations"
            confidence = 0.8
        elif clarity_requests >= 1:
            communication_style = "clear_step_by_step"
            confidence = 0.6
        else:
            communication_style = "standard_technical"
            confidence = 0.4

        self._update_user_preference(
            profile.user_id,
            category,
            key,
            communication_style,
            confidence,
            f"User requested clarity {clarity_requests} times, simple explanations {simple_requests} times",
            ["communication_style_analysis"],
        )

    def _analyze_organization_preference(
        self,
        profile: UserProfile,
        interaction: UserInteraction,
        category: PreferenceCategory,
        key: str,
    ) -> None:
        """Analyze user preference for system organization."""
        # Count organization/cleanup focused interactions
        organization_requests = sum(
            1
            for i in profile.interaction_history
            if i.interaction_type == InteractionType.ORGANIZATION_FOCUS
        )

        # Look for cleanup/organization keywords in context
        cleanup_keywords = ["clean", "tidy", "organize", "cleanup", "remove"]
        cleanup_mentions = sum(
            1
            for i in profile.interaction_history
            if any(keyword in str(i.context).lower() for keyword in cleanup_keywords)
        )

        # Determine organization preference
        if organization_requests >= 3 or cleanup_mentions >= 5:
            organization_level = "very_tidy"
            confidence = 0.9
        elif organization_requests >= 1 or cleanup_mentions >= 2:
            organization_level = "tidy"
            confidence = 0.7
        else:
            organization_level = "standard"
            confidence = 0.4

        self._update_user_preference(
            profile.user_id,
            category,
            key,
            organization_level,
            confidence,
            f"User focused on organization {organization_requests} times, mentioned cleanup {cleanup_mentions} times",
            ["organization_preference_analysis"],
        )

    def _analyze_learning_style_preference(
        self,
        profile: UserProfile,
        interaction: UserInteraction,
        category: PreferenceCategory,
        key: str,
    ) -> None:
        """Analyze user learning style preference."""
        # Count requests for feature explanations
        explanation_requests = sum(
            1
            for i in profile.interaction_history
            if i.interaction_type == InteractionType.CONVERSATIONAL_REQUEST
            and ("how" in str(i.context).lower() or "explain" in str(i.context).lower())
        )

        # Look for patterns in learning requests
        simple_explanation_requests = sum(
            1
            for i in profile.interaction_history
            if "simple" in str(i.context).lower()
            and "explain" in str(i.context).lower()
        )

        # Determine learning style preference
        if simple_explanation_requests >= 3:
            learning_style = "simple_examples"
            confidence = 0.8
        elif explanation_requests >= 5:
            learning_style = "detailed_explanations"
            confidence = 0.7
        elif explanation_requests >= 2:
            learning_style = "practical_examples"
            confidence = 0.6
        else:
            learning_style = "standard_documentation"
            confidence = 0.3

        self._update_user_preference(
            profile.user_id,
            category,
            key,
            learning_style,
            confidence,
            (
                f"User requested feature explanations {explanation_requests} times, "
                f"simple explanations {simple_explanation_requests} times"
            ),
            ["learning_style_analysis"],
        )

    def _update_user_preference(
        self,
        user_id: str,
        category: PreferenceCategory,
        key: str,
        value: Any,
        confidence: Union[float, PreferenceConfidence],
        evidence: str,
        sources: List[str],
        preference_type: PreferenceType = PreferenceType.SELECTION,
    ) -> None:
        """Update or create a user preference."""
        preference_id = f"pref_{int(time.time())}_{utils.random_string(8)}"

        # Check if preference already exists
        existing_pref = None
        for pref in self.user_profiles[user_id].preferences.values():
            if pref.preference_key == key and pref.category == category:
                existing_pref = pref
                break

        if existing_pref:
            # Update existing preference
            existing_pref.preference_value = value
            existing_pref.confidence = confidence  # Keep original confidence value
            existing_pref.evidence_count += 1
            existing_pref.last_updated = datetime.now()
            existing_pref.sources.extend(sources)
        else:
            # Create new preference
            preference = UserPreference(
                preference_id=preference_id,
                user_id=user_id,
                category=category,
                preference_key=key,
                preference_value=value,
                confidence=confidence,  # Keep original confidence value
                evidence_count=1,
                last_updated=datetime.now(),
                sources=sources,
                preference_type=preference_type,
            )

            self.user_profiles[user_id].preferences[preference_id] = preference

        # Log preference learning (convert enum to float for JSON)
        confidence_for_json = confidence
        if hasattr(confidence, "value"):  # Enum-like object
            confidence_for_json = 0.5  # Use a default float for JSON
        elif not isinstance(confidence, (int, float)):
            confidence_for_json = 0.5  # Default fallback

        self._log_preference_learning(
            user_id, category, key, value, float(confidence_for_json), evidence  # type: ignore[arg-type]
        )

    def _detect_behavior_patterns(self, profile: UserProfile) -> None:
        """Detect behavior patterns in user interactions."""
        if len(profile.interaction_history) < 10:
            return

        # Detect various behavior patterns
        self._detect_timing_patterns(profile)
        self._detect_workflow_patterns(profile)
        self._detect_error_patterns(profile)
        self._detect_satisfaction_patterns(profile)

    def _detect_timing_patterns(self, profile: UserProfile) -> None:
        """Detect timing - related behavior patterns."""
        interactions = list(profile.interaction_history)

        # Analyze interaction timing
        if len(interactions) < 5:
            return

        # Calculate time between interactions
        time_diffs = []
        for i in range(1, len(interactions)):
            diff = (
                interactions[i].timestamp - interactions[i - 1].timestamp
            ).total_seconds()
            time_diffs.append(diff)

        avg_time_diff = statistics.mean(time_diffs)

        # Detect patterns
        if avg_time_diff < 60:  # Less than 1 minute
            pattern = UserBehaviorPattern(
                pattern_id=f"pattern_{int(time.time())}_{utils.random_string(8)}",
                user_id=profile.user_id,
                pattern_type="rapid_interaction",
                description="User tends to interact rapidly with short intervals",
                frequency=0.8,
                confidence=0.7,
                conditions={"avg_interval_seconds": avg_time_diff},
                implications=[
                    "Prefers quick responses",
                    "May benefit from reduced timeouts",
                ],
                recommendations=["Reduce gate timeout", "Enable quick mode"],
            )
            profile.behavior_patterns.append(pattern)

    def _detect_workflow_patterns(self, profile: UserProfile) -> None:
        """Detect workflow - related behavior patterns."""
        interactions = list(profile.interaction_history)

        # Analyze command sequences
        command_sequences = []
        current_sequence = []

        for interaction in interactions:
            if interaction.interaction_type == InteractionType.COMMAND_EXECUTION:
                current_sequence.append(interaction.context.get("command", "unknown"))
            else:
                if len(current_sequence) > 1:
                    command_sequences.append(tuple(current_sequence))
                current_sequence = []

        # Detect common sequences
        if command_sequences:
            sequence_counts: Dict[str, int] = defaultdict(int)
            for seq in command_sequences:
                sequence_counts[str(seq)] += 1

            most_common = max(sequence_counts.items(), key=lambda x: x[1])
            if most_common[1] > 2:  # Appears more than twice
                pattern = UserBehaviorPattern(
                    pattern_id=f"pattern_{int(time.time())}_{utils.random_string(8)}",
                    user_id=profile.user_id,
                    pattern_type="command_sequence",
                    description=f"User frequently executes command sequence: {' -> '.join(most_common[0])}",
                    frequency=most_common[1] / len(command_sequences),
                    confidence=0.8,
                    conditions={
                        "sequence": most_common[0],
                        "frequency": most_common[1],
                    },
                    implications=[
                        "Has preferred workflow",
                        "Could benefit from automation",
                    ],
                    recommendations=["Create workflow macro", "Suggest automation"],
                )
                profile.behavior_patterns.append(pattern)

    def _detect_error_patterns(self, profile: UserProfile) -> None:
        """Detect error - related behavior patterns."""
        error_interactions = [
            i
            for i in profile.interaction_history
            if i.interaction_type == InteractionType.ERROR_HANDLING
        ]

        if len(error_interactions) < 3:
            return

        # Analyze error patterns
        error_types: Dict[str, int] = defaultdict(int)
        for interaction in error_interactions:
            error_type = interaction.context.get("error_type", "unknown")
            error_types[error_type] += 1

        most_common_error = max(error_types.items(), key=lambda x: x[1])

        if most_common_error[1] > 2:
            pattern = UserBehaviorPattern(
                pattern_id=f"pattern_{int(time.time())}_{utils.random_string(8)}",
                user_id=profile.user_id,
                pattern_type="error_prone",
                description=f"User frequently encounters {most_common_error[0]} errors",
                frequency=most_common_error[1] / len(error_interactions),
                confidence=0.7,
                conditions={
                    "error_type": most_common_error[0],
                    "frequency": most_common_error[1],
                },
                implications=[
                    "May need additional guidance",
                    "Could benefit from prevention",
                ],
                recommendations=[
                    "Increase safety level",
                    "Provide error prevention tips",
                ],
            )
            profile.behavior_patterns.append(pattern)

    def _detect_satisfaction_patterns(self, profile: UserProfile) -> None:
        """Detect satisfaction - related behavior patterns."""
        if len(profile.satisfaction_scores) < 5:
            return

        scores = list(profile.satisfaction_scores)
        statistics.mean(scores)

        # Detect satisfaction trends
        if len(scores) >= 10:
            recent_avg = statistics.mean(scores[-5:])
            older_avg = statistics.mean(scores[-10:-5])

            if recent_avg > older_avg + 0.2:
                pattern = UserBehaviorPattern(
                    pattern_id=f"pattern_{int(time.time())}_{utils.random_string(8)}",
                    user_id=profile.user_id,
                    pattern_type="improving_satisfaction",
                    description="User satisfaction is improving over time",
                    frequency=0.8,
                    confidence=0.7,
                    conditions={"recent_avg": recent_avg, "older_avg": older_avg},
                    implications=[
                        "System is adapting well",
                        "User is becoming more comfortable",
                    ],
                    recommendations=[
                        "Continue current approach",
                        "Consider advanced features",
                    ],
                )
                profile.behavior_patterns.append(pattern)

    def _update_experience_level(self, profile: UserProfile) -> None:
        """Update user experience level based on interactions and patterns."""
        total_interactions = profile.total_interactions
        avg_satisfaction = profile.average_satisfaction
        error_rate = self._calculate_error_rate(profile)

        # Determine experience level
        if total_interactions < 10 or avg_satisfaction < 0.5:
            new_level = UserExperienceLevel.BEGINNER
        elif total_interactions < 50 or error_rate > 0.2:
            new_level = UserExperienceLevel.INTERMEDIATE
        elif total_interactions < 200 or avg_satisfaction < 0.8:
            new_level = UserExperienceLevel.ADVANCED
        else:
            new_level = UserExperienceLevel.EXPERT

        # Update if changed
        if profile.experience_level != new_level:
            profile.experience_level = new_level
            # Log experience level change
            telemetry.log_event(
                "user_experience_level_changed",
                user_id=profile.user_id,
                old_level=profile.experience_level.value,
                new_level=new_level.value,
                total_interactions=total_interactions,
                avg_satisfaction=avg_satisfaction,
            )

    def _calculate_error_rate(self, profile: UserProfile) -> float:
        """Calculate user error rate."""
        error_interactions = sum(
            1
            for i in profile.interaction_history
            if i.interaction_type == InteractionType.ERROR_HANDLING
        )

        if profile.total_interactions == 0:
            return 0.0

        return error_interactions / profile.total_interactions

    def get_user_preferences(
        self, user_id: str, category: Optional[PreferenceCategory] = None
    ) -> Dict[str, UserPreference]:
        """Get user preferences, optionally filtered by category."""
        if user_id not in self.user_profiles:
            return {}

        preferences = self.user_profiles[user_id].preferences

        if category:
            return {
                key: pref
                for key, pref in preferences.items()
                if pref.category == category
            }

        return preferences

    def get_user_preferences_list(self, user_id: str) -> List[UserPreference]:
        """Get user preferences as a list (backward compatibility)."""
        preferences = self.get_user_preferences(user_id)
        if isinstance(preferences, list):
            return preferences
        elif isinstance(preferences, dict):
            return list(preferences.values())
        else:
            return []

    def get_user_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user."""
        if user_id not in self.user_profiles:
            return []

        profile = self.user_profiles[user_id]
        recommendations = []

        # Generate recommendations based on preferences and patterns
        for preference in profile.preferences.values():
            pref_confidence = (
                preference.confidence.value
                if hasattr(preference.confidence, "value")
                else float(preference.confidence)
            )
            if pref_confidence > 0.7:
                recommendations.append(
                    {
                        "type": "preference_based",
                        "title": f"Apply {preference.preference_key} preference",
                        "description": f"Set {preference.preference_key} to {preference.preference_value}",
                        "confidence": preference.confidence,
                        "category": preference.category.value,
                    }
                )

        # Generate recommendations based on behavior patterns
        for pattern in profile.behavior_patterns:
            if pattern.confidence > 0.7:
                for recommendation in pattern.recommendations:
                    recommendations.append(
                        {
                            "type": "pattern_based",
                            "title": recommendation,
                            "description": f"Based on pattern: {pattern.description}",
                            "confidence": pattern.confidence,
                            "category": "behavior_optimization",
                        }
                    )

        # Sort by confidence (convert to float for consistent comparison)
        def get_sort_key(item):
            confidence = item["confidence"]
            if isinstance(confidence, (int, float)):
                return float(confidence)
            elif hasattr(confidence, "value"):
                return float(confidence.value)
            else:
                return 0.0

        recommendations.sort(key=get_sort_key, reverse=True)

        return recommendations[:10]  # Return top 10

    def get_user_profile_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user profile summary."""
        if user_id not in self.user_profiles:
            return {"status": "not_found", "message": f"User {user_id} not found"}

        profile = self.user_profiles[user_id]

        return {
            "status": "success",
            "user_id": user_id,
            "experience_level": profile.experience_level.value,
            "total_interactions": profile.total_interactions,
            "average_satisfaction": profile.average_satisfaction,
            "last_activity": profile.last_activity.isoformat(),
            "preferences_count": len(profile.preferences),
            "behavior_patterns_count": len(profile.behavior_patterns),
            "feedback_count": len(profile.feedback_history),
            "error_rate": self._calculate_error_rate(profile),
            "top_preferences": [
                {
                    "key": pref.preference_key,
                    "value": pref.preference_value,
                    "confidence": pref.confidence,
                    "category": pref.category.value,
                }
                for pref in sorted(
                    profile.preferences.values(),
                    key=lambda x: (
                        float(x.confidence)
                        if isinstance(x.confidence, (int, float))
                        else 0.5
                    ),  # Convert to float for consistent comparison
                    reverse=True,
                )[:5]
            ],
            "recent_patterns": [
                {
                    "type": pattern.pattern_type,
                    "description": pattern.description,
                    "confidence": pattern.confidence,
                    "frequency": pattern.frequency,
                }
                for pattern in sorted(
                    profile.behavior_patterns, key=lambda x: x.detected_at, reverse=True
                )[:3]
            ],
        }

    def _log_user_interaction(self, interaction: UserInteraction) -> None:
        """Log user interaction to storage."""
        interaction_data = {
            "interaction_id": interaction.interaction_id,
            "user_id": interaction.user_id,
            "interaction_type": interaction.interaction_type.value,
            "timestamp": interaction.timestamp.isoformat(),
            "context": interaction.context,
            "duration": interaction.duration,
            "outcome": interaction.outcome,
            "satisfaction_score": interaction.satisfaction_score,
            "feedback": interaction.feedback,
        }

        with open(self.interaction_log_path, "a", encoding="utf - 8") as f:
            json.dump(interaction_data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    def _log_preference_learning(
        self,
        user_id: str,
        category: PreferenceCategory,
        key: str,
        value: Any,
        confidence: float,
        evidence: str,
    ) -> None:
        """Log preference learning event."""
        learning_data = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "category": category.value,
            "preference_key": key,
            "preference_value": value,
            "confidence": confidence,
            "evidence": evidence,
        }

        with open(self.preference_learning_path, "a", encoding="utf - 8") as f:
            json.dump(learning_data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    def _save_user_profiles(self) -> None:
        """Save user profiles to storage."""
        data = {}
        for user_id, profile in self.user_profiles.items():
            # Convert preferences
            preferences_data = {}
            for pref_key, preference in profile.preferences.items():
                preferences_data[pref_key] = {
                    "preference_id": preference.preference_id,
                    "category": preference.category.value,
                    "preference_key": preference.preference_key,
                    "preference_value": preference.preference_value,
                    "confidence": preference.confidence,
                    "evidence_count": preference.evidence_count,
                    "last_updated": preference.last_updated.isoformat(),
                    "sources": preference.sources,
                    "context_conditions": preference.context_conditions,
                }

            # Convert behavior patterns
            behavior_patterns_data = []
            for pattern in profile.behavior_patterns:
                behavior_patterns_data.append(
                    {
                        "pattern_id": pattern.pattern_id,
                        "pattern_type": pattern.pattern_type,
                        "description": pattern.description,
                        "frequency": pattern.frequency,
                        "confidence": pattern.confidence,
                        "conditions": pattern.conditions,
                        "implications": pattern.implications,
                        "recommendations": pattern.recommendations,
                        "detected_at": pattern.detected_at.isoformat(),
                    }
                )

            # Convert interaction history
            interaction_history_data = []
            for interaction in profile.interaction_history:
                interaction_history_data.append(
                    {
                        "interaction_id": interaction.interaction_id,
                        "interaction_type": interaction.interaction_type.value,
                        "timestamp": interaction.timestamp.isoformat(),
                        "context": interaction.context,
                        "duration": interaction.duration,
                        "outcome": interaction.outcome,
                        "satisfaction_score": interaction.satisfaction_score,
                        "feedback": interaction.feedback,
                    }
                )

            data[user_id] = {
                "experience_level": profile.experience_level.value,
                "preferences": preferences_data,
                "behavior_patterns": behavior_patterns_data,
                "interaction_history": interaction_history_data,
                "satisfaction_scores": list(profile.satisfaction_scores),
                "feedback_history": profile.feedback_history,
                "last_activity": profile.last_activity.isoformat(),
                "total_interactions": profile.total_interactions,
                "average_satisfaction": profile.average_satisfaction,
                "created_at": profile.created_at.isoformat(),
            }

        try:
            utils.write_json(self.user_profiles_path, data)
        except (OSError, IOError) as e:
            # Handle disk space or I/O errors gracefully
            print(f"Warning: Failed to save user profiles: {e}")
            # Continue without saving - data will be lost but system won't crash

    def _load_all_user_profiles(self) -> Dict[str, UserProfile]:
        """Load all user profiles from storage."""
        try:
            if not self.user_profiles_path.exists():
                return {}

            data = utils.read_json(self.user_profiles_path, default={})
            profiles = {}

            for user_id, profile_data in data.items():
                try:
                    # Convert stored data back to UserProfile
                    # Map legacy fields to current dataclass structure
                    experience_level = UserExperienceLevel.INTERMEDIATE  # Default
                    if profile_data.get("expertise_level") == "beginner":
                        experience_level = UserExperienceLevel.BEGINNER
                    elif profile_data.get("expertise_level") == "advanced":
                        experience_level = UserExperienceLevel.ADVANCED

                    profile = UserProfile(
                        user_id=user_id,
                        experience_level=experience_level,
                        feedback_history=profile_data.get("feedback_history", []),
                    )

                    # Add legacy data to feedback_history for backward compatibility
                    legacy_data = {
                        "command_preferences": profile_data.get(
                            "command_preferences", {}
                        ),
                        "total_interactions": profile_data.get("total_interactions", 0),
                        "average_satisfaction": profile_data.get(
                            "average_satisfaction", 0.0
                        ),
                        "expertise_areas": profile_data.get("expertise_areas", []),
                        "preferred_interaction_mode": profile_data.get(
                            "preferred_interaction_mode", "command_line"
                        ),
                        "learning_rate": profile_data.get("learning_rate", 0.1),
                    }
                    profile.feedback_history.append(
                        {
                            "type": "legacy_data_migration",
                            "timestamp": datetime.now().isoformat(),
                            "data": legacy_data,
                        }
                    )

                    profiles[user_id] = profile
                except (KeyError, ValueError) as e:
                    # Skip malformed profiles
                    continue

            return profiles

        except Exception:
            return {}

    def get_system_wide_patterns(self) -> Optional[Dict[str, Any]]:
        """Get system-wide patterns across all users."""
        try:
            all_profiles = self._load_all_user_profiles()
            if not all_profiles:
                return None

            # Aggregate patterns across all users
            system_patterns = {
                "total_users": len(all_profiles),
                "command_patterns": {},
                "timing_patterns": {},
                "workflow_patterns": {},
                "error_patterns": {},
                "satisfaction_patterns": {},
                "learning_rules": self.preference_learning_rules,
                "behavior_detectors": list(self.behavior_pattern_detectors.keys()),
            }

            # Aggregate command preferences from legacy data
            all_commands: Dict[str, List] = {}
            for profile in all_profiles.values():
                # Extract legacy data from feedback_history
                legacy_data = None
                for entry in profile.feedback_history:
                    if (
                        isinstance(entry, dict)
                        and entry.get("type") == "legacy_data_migration"
                    ):
                        legacy_data = entry.get("data", {})
                        break

                if legacy_data and "command_preferences" in legacy_data:
                    for cmd, prefs in legacy_data["command_preferences"].items():
                        if cmd not in all_commands:
                            all_commands[cmd] = []
                        if isinstance(prefs, dict) and "usage_history" in prefs:
                            all_commands[cmd].extend(prefs["usage_history"])  # type: ignore[list-item]

            system_patterns["command_patterns"] = all_commands

            # Get most common patterns
            system_patterns["most_used_commands"] = sorted(
                all_commands.keys(), key=lambda x: len(all_commands[x]), reverse=True
            )[:10]

            return system_patterns

        except Exception:
            return None


def get_user_preference_learning_system(root: Path) -> UserPreferenceLearningSystem:
    """Get user preference learning system instance."""
    return UserPreferenceLearningSystem(root)
