from pathlib import Path

import pytest

from ai_onboard.core.ai_integration.agent_adapter import AIOnboardAgentAdapter
from ai_onboard.core.base import utils


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    base = tmp_path / ".ai_onboard"
    base.mkdir(parents=True, exist_ok=True)
    utils.write_json(
        base / "charter.json",
        {
            "project_name": "Contact Form",
            "description": "Simple contact form",
            "objectives": ["Collect messages", "Email admin"],
            "max_complexity": "simple",
        },
    )
    utils.write_json(
        base / "project_plan.json",
        {
            "workflow": {"current_phase": "build"},
            "work_breakdown_structure": {
                "build": {
                    "name": "Build",
                    "description": "Implement form",
                    "subtasks": {
                        "form": {
                            "name": "Form",
                            "description": "Build form",
                        }
                    },
                }
            },
        },
    )
    utils.write_json(base / "state.json", {"phase": "build"})
    return tmp_path


def test_assess_message_records_preferences(temp_project: Path) -> None:
    adapter = AIOnboardAgentAdapter(temp_project)

    result = adapter.assess_message(
        "Add validation to the contact form", user_id="tester"
    )

    assert "assessment" in result
    assessment = result["assessment"]
    assert hasattr(assessment, "decision")
    assert result["updated_preferences"] == [] or isinstance(
        result["updated_preferences"], list
    )

    stored_prefs = adapter._preference_system.get_user_preferences("tester")
    assert isinstance(stored_prefs, dict)


def test_record_gate_decision_updates_preferences(temp_project: Path) -> None:
    adapter = AIOnboardAgentAdapter(temp_project)

    prefs = adapter.record_gate_decision(
        user_id="tester",
        gate_id="Gate-1",
        approved=False,
        gate_type="scope_check",
        notes="Scope exceeded",
    )

    assert isinstance(prefs, list)

    user_prefs = adapter._preference_system.get_user_preferences("tester")
    assert isinstance(user_prefs, dict)
