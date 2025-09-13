"""
Unit tests for UserPreferenceLearningSystem.

Tests the core functionality of the user preference learning system
with mocked dependencies for reliable testing.
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from ai_onboard.core.user_preference_learning import (
    PreferenceCategory,
    PreferenceConfidence,
    PreferenceType,
    UserPreference,
    UserPreferenceLearningSystem,
    get_user_preference_learning_system,
)


@pytest.fixture
def temp_root():
    """Provide a temporary root directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def preference_system(temp_root):
    """Provide a UserPreferenceLearningSystem instance."""
    with patch("ai_onboard.core.user_preference_learning.telemetry"), patch(
        "ai_onboard.core.user_preference_learning.get_unified_metrics_collector"
    ):
        system=UserPreferenceLearningSystem(temp_root)
        return system


@pytest.fixture
def sample_user_interactions():
    """Provide sample user interaction data."""
    return [
        {
            "user_id": "test_user",
            "action": "command_execution",
            "command": "charter",
            "timestamp": datetime.now(),
            "success": True,
            "duration": 2.5,
            "context": {"project_type": "web_app"},
        },
        {
            "user_id": "test_user",
            "action": "preference_selection",
            "preference": "detailed_output",
            "value": True,
            "timestamp": datetime.now(),
            "context": {"command": "validate"},
        },
        {
            "user_id": "test_user",
            "action": "error_handling",
            "error_type": "validation_error",
            "resolution": "retry_with_fix",
            "timestamp": datetime.now(),
            "success": True,
        },
    ]


class TestUserPreferenceLearningSystem:
    """Test suite for UserPreferenceLearningSystem."""

    def test_initialization(self, temp_root):
        """Test that UserPreferenceLearningSystem initializes correctly."""
        with patch("ai_onboard.core.user_preference_learning.telemetry"), patch(
            "ai_onboard.core.user_preference_learning.get_unified_metrics_collector"
        ):
            system=UserPreferenceLearningSystem(temp_root)

            assert system.root == temp_root
            assert (
                system.preferences_path
                == temp_root / ".ai_onboard" / "user_preferences"
            )
            assert (
                system.learning_data_path == temp_root / ".ai_onboard" / "learning_data"
            )
            assert isinstance(system.config, dict)
            assert system.preferences_path.exists()
            assert system.learning_data_path.exists()

    def test_record_user_interaction(self, preference_system, sample_user_interactions):
        """Test recording user interactions."""
        interaction=sample_user_interactions[0]

        preference_system.record_user_interaction(
            user_id=interaction["user_id"],
            action=interaction["action"],
            context=interaction["context"],
            outcome={
                "success": interaction["success"],
                "duration": interaction["duration"],
            },
        )

        # Check that interaction was recorded
        user_data=preference_system._load_user_data(interaction["user_id"])
        assert len(user_data["interactions"]) > 0
        assert user_data["interactions"][-1]["action"] == interaction["action"]

    def test_learn_preferences_from_interactions(
        self, preference_system, sample_user_interactions
    ):
        """Test learning preferences from user interactions."""
        user_id="test_user"

        # Record multiple interactions
        for interaction in sample_user_interactions:
            preference_system.record_user_interaction(
                user_id=user_id,
                action=interaction["action"],
                context=interaction.get("context", {}),
                outcome={"success": interaction.get("success", True)},
            )

        # Learn preferences
        learned_preferences=preference_system.learn_preferences_from_interactions(
            user_id
        )

        assert isinstance(learned_preferences, list)
        for pref in learned_preferences:
            assert isinstance(pref, UserPreference)
            assert pref.user_id == user_id
            assert isinstance(pref.category, PreferenceCategory)
            assert isinstance(pref.preference_type, PreferenceType)
            assert isinstance(pref.confidence, PreferenceConfidence)

    def test_get_user_preferences(self, preference_system):
        """Test retrieving user preferences."""
        user_id="test_user"

        # Create a test preference
        test_preference=UserPreference(
            user_id=user_id,
            preference_key="output_format",
            preference_value="detailed",
            category=PreferenceCategory.INTERFACE,
            preference_type=PreferenceType.SELECTION,
            confidence=PreferenceConfidence.HIGH,
            learned_from=["command_usage", "explicit_setting"],
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )

        # Store the preference
        preference_system._store_user_preference(test_preference)

        # Retrieve preferences
        preferences=preference_system.get_user_preferences(user_id)

        assert isinstance(preferences, list)
        assert len(preferences) > 0
        assert preferences[0].user_id == user_id
        assert preferences[0].preference_key == "output_format"

    def test_update_preference_confidence(self, preference_system):
        """Test updating preference confidence based on usage."""
        user_id="test_user"
        preference_key="test_preference"

        # Create initial preference
        preference=UserPreference(
            user_id=user_id,
            preference_key=preference_key,
            preference_value="test_value",
            category=PreferenceCategory.WORKFLOW,
            preference_type=PreferenceType.BOOLEAN,
            confidence=PreferenceConfidence.LOW,
            learned_from=["initial_interaction"],
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )

        preference_system._store_user_preference(preference)

        # Update confidence
        preference_system.update_preference_confidence(
            user_id=user_id, preference_key=preference_key, positive_feedback=True
        )

        # Check updated preference
        updated_prefs=preference_system.get_user_preferences(user_id)
        updated_pref=next(
            p for p in updated_prefs if p.preference_key == preference_key
        )

        # Confidence should have increased
        assert updated_pref.confidence.value >= preference.confidence.value

    def test_predict_user_preference(self, preference_system):
        """Test predicting user preferences for new contexts."""
        user_id="test_user"

        # Store some historical preferences
        preferences=[
            UserPreference(
                user_id=user_id,
                preference_key="output_verbosity",
                preference_value="detailed",
                category=PreferenceCategory.INTERFACE,
                preference_type=PreferenceType.SELECTION,
                confidence=PreferenceConfidence.HIGH,
                learned_from=["usage_pattern"],
                created_at=datetime.now(),
                last_updated=datetime.now(),
            )
        ]

        for pref in preferences:
            preference_system._store_user_preference(pref)

        # Predict preference for new context
        prediction=preference_system.predict_user_preference(
            user_id=user_id,
            context={"command": "validate", "project_type": "web_app"},
            preference_category=PreferenceCategory.INTERFACE,
        )

        assert isinstance(prediction, dict)
        assert "predicted_preferences" in prediction
        assert "confidence_scores" in prediction

    def test_adaptive_learning(self, preference_system, sample_user_interactions):
        """Test adaptive learning from user feedback."""
        user_id="test_user"

        # Record interactions over time
        for i, interaction in enumerate(sample_user_interactions):
            # Simulate time progression
            interaction_time=datetime.now() - timedelta(
                days=len(sample_user_interactions) - i
            )

            preference_system.record_user_interaction(
                user_id=user_id,
                action=interaction["action"],
                context=interaction.get("context", {}),
                outcome={"success": interaction.get("success", True)},
                timestamp=interaction_time,
            )

        # Trigger adaptive learning
        preference_system.perform_adaptive_learning(user_id)

        # Check that learning occurred
        user_data=preference_system._load_user_data(user_id)
        assert "learning_metrics" in user_data
        assert user_data["learning_metrics"]["total_interactions"] > 0

    def test_preference_persistence(self, preference_system):
        """Test that preferences are properly persisted."""
        user_id="test_user"

        preference=UserPreference(
            user_id=user_id,
            preference_key="persistence_test",
            preference_value="test_value",
            category=PreferenceCategory.WORKFLOW,
            preference_type=PreferenceType.STRING,
            confidence=PreferenceConfidence.MEDIUM,
            learned_from=["test"],
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )

        # Store preference
        preference_system._store_user_preference(preference)

        # Create new system instance to test persistence
        with patch("ai_onboard.core.user_preference_learning.telemetry"), patch(
            "ai_onboard.core.user_preference_learning.get_unified_metrics_collector"
        ):
            new_system=UserPreferenceLearningSystem(preference_system.root)

            # Retrieve preferences
            retrieved_prefs=new_system.get_user_preferences(user_id)

            assert len(retrieved_prefs) > 0
            assert any(p.preference_key == "persistence_test" for p in retrieved_prefs)

    def test_factory_function(self, temp_root):
        """Test the factory function."""
        with patch("ai_onboard.core.user_preference_learning.telemetry"), patch(
            "ai_onboard.core.user_preference_learning.get_unified_metrics_collector"
        ):
            system=get_user_preference_learning_system(temp_root)
            assert isinstance(system, UserPreferenceLearningSystem)
            assert system.root == temp_root

    def test_configuration_loading(self, temp_root):
        """Test configuration loading and defaults."""
        # Create custom config
        config_path=temp_root / ".ai_onboard" / "preference_learning_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        custom_config={
            "learning_enabled": True,
            "confidence_threshold": 0.7,
            "max_interaction_history": 1000,
        }

        with open(config_path, "w") as f:
            json.dump(custom_config, f)

        with patch("ai_onboard.core.user_preference_learning.telemetry"), patch(
            "ai_onboard.core.user_preference_learning.get_unified_metrics_collector"
        ):
            system=UserPreferenceLearningSystem(temp_root)

            assert system.config["learning_enabled"] is True
            assert system.config["confidence_threshold"] == 0.7

    def test_error_handling_invalid_user(self, preference_system):
        """Test error handling with invalid user IDs."""
        # Non - existent user
        preferences=preference_system.get_user_preferences("non_existent_user")
        assert isinstance(preferences, list)
        assert len(preferences) == 0

    def test_preference_categories_and_types(self, preference_system):
        """Test different preference categories and types."""
        user_id="test_user"

        # Test different preference types
        preferences=[
            UserPreference(
                user_id=user_id,
                preference_key="boolean_pref",
                preference_value=True,
                category=PreferenceCategory.INTERFACE,
                preference_type=PreferenceType.BOOLEAN,
                confidence=PreferenceConfidence.HIGH,
                learned_from=["test"],
                created_at=datetime.now(),
                last_updated=datetime.now(),
            ),
            UserPreference(
                user_id=user_id,
                preference_key="numeric_pref",
                preference_value=42,
                category=PreferenceCategory.PERFORMANCE,
                preference_type=PreferenceType.NUMERIC,
                confidence=PreferenceConfidence.MEDIUM,
                learned_from=["test"],
                created_at=datetime.now(),
                last_updated=datetime.now(),
            ),
            UserPreference(
                user_id=user_id,
                preference_key="selection_pref",
                preference_value="option_a",
                category=PreferenceCategory.WORKFLOW,
                preference_type=PreferenceType.SELECTION,
                confidence=PreferenceConfidence.LOW,
                learned_from=["test"],
                created_at=datetime.now(),
                last_updated=datetime.now(),
            ),
        ]

        for pref in preferences:
            preference_system._store_user_preference(pref)

        # Retrieve and verify
        retrieved_prefs=preference_system.get_user_preferences(user_id)
        assert len(retrieved_prefs) == 3

        # Check that all types are represented
        pref_types={p.preference_type for p in retrieved_prefs}
        assert PreferenceType.BOOLEAN in pref_types
        assert PreferenceType.NUMERIC in pref_types
        assert PreferenceType.SELECTION in pref_types

    @pytest.mark.parametrize(
        "confidence_level",
        [
            PreferenceConfidence.LOW,
            PreferenceConfidence.MEDIUM,
            PreferenceConfidence.HIGH,
            PreferenceConfidence.VERY_HIGH,
        ],
    )
    def test_confidence_levels(self, preference_system, confidence_level):
        """Test different confidence levels."""
        user_id="test_user"

        preference=UserPreference(
            user_id=user_id,
            preference_key=f"confidence_test_{confidence_level.value}",
            preference_value="test",
            category=PreferenceCategory.INTERFACE,
            preference_type=PreferenceType.STRING,
            confidence=confidence_level,
            learned_from=["test"],
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )

        preference_system._store_user_preference(preference)

        retrieved_prefs=preference_system.get_user_preferences(user_id)
        matching_pref=next(
            p
            for p in retrieved_prefs
            if p.preference_key == f"confidence_test_{confidence_level.value}"
        )

        assert matching_pref.confidence == confidence_level


class TestUserPreference:
    """Test suite for UserPreference data structure."""

    def test_user_preference_creation(self):
        """Test UserPreference object creation."""
        preference=UserPreference(
            user_id="test_user",
            preference_key="test_key",
            preference_value="test_value",
            category=PreferenceCategory.INTERFACE,
            preference_type=PreferenceType.STRING,
            confidence=PreferenceConfidence.HIGH,
            learned_from=["interaction_pattern"],
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )

        assert preference.user_id == "test_user"
        assert preference.preference_key == "test_key"
        assert preference.preference_value == "test_value"
        assert preference.category == PreferenceCategory.INTERFACE
        assert preference.preference_type == PreferenceType.STRING
        assert preference.confidence == PreferenceConfidence.HIGH


# Integration tests
@pytest.mark.integration
class TestUserPreferenceLearningIntegration:
    """Integration tests for the user preference learning system."""

    def test_end_to_end_learning_cycle(self, temp_root):
        """Test complete end - to - end learning cycle."""
        with patch("ai_onboard.core.user_preference_learning.telemetry"), patch(
            "ai_onboard.core.user_preference_learning.get_unified_metrics_collector"
        ):

            system=UserPreferenceLearningSystem(temp_root)
            user_id="integration_test_user"

            # Simulate user interactions over time
            interactions=[
                {"action": "command_execution", "command": "charter", "success": True},
                {
                    "action": "preference_selection",
                    "preference": "verbose_output",
                    "value": True,
                },
                {"action": "command_execution", "command": "validate", "success": True},
                {
                    "action": "preference_selection",
                    "preference": "auto_fix",
                    "value": False,
                },
                {
                    "action": "error_handling",
                    "error_type": "validation",
                    "resolution": "manual_fix",
                },
            ]

            # Record interactions
            for interaction in interactions:
                system.record_user_interaction(
                    user_id=user_id,
                    action=interaction["action"],
                    context=interaction,
                    outcome={"success": interaction.get("success", True)},
                )

            # Learn preferences
            learned_prefs=system.learn_preferences_from_interactions(user_id)

            # Perform adaptive learning
            system.perform_adaptive_learning(user_id)

            # Get final preferences
            final_prefs=system.get_user_preferences(user_id)

            # Verify learning occurred
            assert len(final_prefs) > 0
            assert isinstance(learned_prefs, list)

            # Test prediction
            prediction=system.predict_user_preference(
                user_id=user_id,
                context={"command": "new_command"},
                preference_category=PreferenceCategory.INTERFACE,
            )

            assert isinstance(prediction, dict)
            assert "predicted_preferences" in prediction
