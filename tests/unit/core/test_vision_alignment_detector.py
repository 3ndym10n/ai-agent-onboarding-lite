import json
from pathlib import Path

from ai_onboard.core.vision.vision_alignment_detector import VisionAlignmentDetector


def _write_json(root: Path, relative: str, data: dict) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _basic_charter() -> dict:
    return {
        "project_name": "Contact Form",
        "description": "Simple contact form that emails submissions.",
        "objectives": [
            "Collect contact requests via form",
            "Send notification emails to site owner",
            "Prevent spam submissions",
        ],
        "non_features": ["user accounts", "authentication"],
        "technologies": ["html", "css", "javascript"],
        "scope": "minimal",
        "max_complexity": "simple",
    }


def _basic_plan() -> dict:
    return {
        "workflow": {"current_phase": "build"},
        "work_breakdown_structure": {
            "build": {
                "name": "Build Contact Form",
                "description": "Create the HTML form and validation logic.",
                "subtasks": {
                    "email_notifications": {
                        "name": "Email notifications",
                        "description": "Send an email when the form is submitted.",
                    },
                    "spam_filter": {
                        "name": "Spam filter",
                        "description": "Prevent automated spam submissions.",
                    },
                },
            },
            "test": {
                "name": "Testing",
                "description": "Functional and usability testing for the form.",
                "subtasks": {
                    "test_cases": {
                        "name": "Test cases",
                        "description": "Create and execute test cases.",
                    }
                },
            },
        },
    }


def test_blocks_non_feature_scope_creep(tmp_path):
    _write_json(tmp_path, ".ai_onboard/charter.json", _basic_charter())
    _write_json(tmp_path, ".ai_onboard/project_plan.json", _basic_plan())
    detector = VisionAlignmentDetector(tmp_path)

    assessment = detector.assess("Implement user authentication and roles.")

    assert assessment.decision == "block"
    assert any("non-feature" in hit.lower() for hit in assessment.constraint_hits)


def test_proceeds_for_in_scope_enhancement(tmp_path):
    _write_json(tmp_path, ".ai_onboard/charter.json", _basic_charter())
    _write_json(tmp_path, ".ai_onboard/project_plan.json", _basic_plan())
    detector = VisionAlignmentDetector(tmp_path)

    suggestion = "Add email validation to ensure contact requests include a valid address."
    assessment = detector.assess(suggestion)

    assert assessment.decision == "proceed"
    assert assessment.score >= detector.thresholds["proceed"]


def test_reviews_when_phase_mismatch(tmp_path):
    charter = _basic_charter()
    plan = _basic_plan()
    plan["workflow"]["current_phase"] = "test"

    _write_json(tmp_path, ".ai_onboard/charter.json", charter)
    _write_json(tmp_path, ".ai_onboard/project_plan.json", plan)
    detector = VisionAlignmentDetector(tmp_path)

    suggestion = "Improve the HTML form styling and validation logic."
    assessment = detector.assess(suggestion)

    assert assessment.decision in {"review", "block"}
    assert assessment.components["phase"] < 1.0
