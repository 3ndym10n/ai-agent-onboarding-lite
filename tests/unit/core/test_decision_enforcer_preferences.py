from ai_onboard.core.ai_integration.decision_enforcer import (
    DecisionEnforcer,
    DecisionPoint,
)
from ai_onboard.core.ai_integration.user_preference_learning import (
    InteractionType,
    PreferenceCategory,
    PreferenceType,
)


def test_decision_enforcer_reuses_learned_preference(tmp_path):
    """Ensure decisions reuse a previously recorded user preference."""

    enforcer = DecisionEnforcer(tmp_path)

    decision = DecisionPoint(
        name="framework_choice",
        question="Select framework",
        options={"fastapi": "FastAPI", "flask": "Flask"},
    )
    enforcer.register_decision(decision)

    # Seed the preference system as if a prior decision recorded it.
    enforcer.preference_system.record_user_interaction(
        user_id="user123",
        interaction_type=InteractionType.COMMAND_EXECUTION,
        context={"test": True},
    )
    enforcer.preference_system._update_user_preference(
        user_id="user123",
        category=PreferenceCategory.PROJECT_PREFERENCES,
        key="framework_choice",
        value="fastapi",
        confidence=0.9,
        evidence="unit_test",
        sources=["unit_test"],
        preference_type=PreferenceType.SELECTION,
    )

    prefs = enforcer.preference_system.get_user_preferences("user123")
    assert any(
        pref.preference_key == "framework_choice"
        and pref.preference_value == "fastapi"
        for pref in prefs.values()
    )

    # The next enforcement should auto-select the learned preference.
    result = enforcer.enforce_decision(
        "framework_choice", {"user_id": "user123"}, agent_id="user123"
    )

    assert result.smart_defaults_used is True
    assert result.response["source"] == "learned_preference"
    assert result.response["user_responses"] == ["fastapi"]
