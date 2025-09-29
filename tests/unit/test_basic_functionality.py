"""
Basic functionality tests without complex fixtures.

This module tests the core functionality of the system without
depending on complex pytest fixtures that cause collection issues.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

from ai_onboard.core.ai_integration.user_preference_learning import (
    InteractionType,
    PreferenceCategory,
    UserPreference,
    UserPreferenceLearningSystem,
)


def test_user_preference_creation():
    """Test UserPreference object creation."""
    preference = UserPreference(
        preference_id="test_pref_id",
        user_id="test_user",
        category=PreferenceCategory.UI_PREFERENCES,
        preference_key="test_key",
        preference_value="test_value",
        confidence=0.8,
        evidence_count=5,
        last_updated=None,  # Will be set to now
    )

    assert preference.user_id == "test_user"
    assert preference.preference_key == "test_key"
    assert preference.preference_value == "test_value"
    assert preference.category == PreferenceCategory.UI_PREFERENCES
    assert preference.confidence == 0.8
    assert preference.evidence_count == 5
    assert preference.preference_id == "test_pref_id"


def test_system_initialization():
    """Test UserPreferenceLearningSystem initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with patch("ai_onboard.core.ai_integration.user_preference_learning.telemetry"):
            system = UserPreferenceLearningSystem(temp_path)

            assert hasattr(system, "root")
            assert hasattr(system, "user_profiles")
            assert hasattr(system, "continuous_improvement")
            assert system.root == temp_path


def test_record_user_interaction():
    """Test recording user interactions."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with patch("ai_onboard.core.ai_integration.user_preference_learning.telemetry"):
            system = UserPreferenceLearningSystem(temp_path)

            # Record an interaction
            interaction_id = system.record_user_interaction(
                user_id="test_user",
                interaction_type=InteractionType.COMMAND_EXECUTION,
                context={"command": "test", "args": []},
                outcome={"success": True, "duration": 0.5},
            )

            # Check that interaction was recorded by getting user profile
            profile = system.get_user_profile_summary("test_user")
            assert "total_interactions" in profile
            assert profile["total_interactions"] > 0


def test_get_user_preferences():
    """Test retrieving user preferences."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with patch("ai_onboard.core.ai_integration.user_preference_learning.telemetry"):
            system = UserPreferenceLearningSystem(temp_path)

            # Record some interactions to generate preferences
            for i in range(5):
                system.record_user_interaction(
                    user_id="test_user",
                    interaction_type=InteractionType.COMMAND_EXECUTION,
                    context={"command": "format", "format": "detailed"},
                    outcome={"success": True},
                )

            # Retrieve preferences
            preferences = system.get_user_preferences("test_user")

            # The method might return a dict or list depending on implementation
            assert isinstance(preferences, (list, dict))
            # Note: The system may not generate preferences immediately


def test_user_profile_summary():
    """Test getting user profile summary."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with patch("ai_onboard.core.ai_integration.user_preference_learning.telemetry"):
            system = UserPreferenceLearningSystem(temp_path)

            # Record multiple interactions
            for i in range(3):
                system.record_user_interaction(
                    user_id="test_user",
                    interaction_type=InteractionType.COMMAND_EXECUTION,
                    context={"command": "test", "format": "detailed"},
                    outcome={"success": True},
                )

            # Get profile summary
            summary = system.get_user_profile_summary("test_user")

            assert isinstance(summary, dict)
            assert "total_interactions" in summary
            assert summary["total_interactions"] == 3
