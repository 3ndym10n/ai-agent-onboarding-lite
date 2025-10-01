import json
from datetime import datetime, timezone

import pytest

from ai_onboard.core.continuous_improvement_validator import (  # type: ignore[import-untyped]
    ContinuousImprovementValidator,
    ValidationCategory,
    ValidationResult,
    ValidationTestCase,
)
from ai_onboard.core.smart_debugger import SmartDebugger  # type: ignore[import-untyped]


@pytest.fixture
def project_root(tmp_path):
    project_root = tmp_path
    ai_dir = project_root / ".ai_onboard"
    ai_dir.mkdir()

    now = datetime.now(timezone.utc).isoformat()
    sample_profile = {
        "fixture_user": {
            "experience_level": "beginner",
            "preferences": {},
            "behavior_patterns": [],
            "interaction_history": [
                {
                    "interaction_id": "interaction_fixture",
                    "interaction_type": "command_execution",
                    "timestamp": now,
                    "context": {"source": "test"},
                    "duration": None,
                    "outcome": None,
                    "satisfaction_score": None,
                    "feedback": None,
                }
            ],
            "satisfaction_scores": [],
            "feedback_history": [],
            "last_activity": now,
            "total_interactions": 1,
            "average_satisfaction": 0.0,
            "created_at": now,
        }
    }

    (ai_dir / "user_profiles.json").write_text(
        json.dumps(sample_profile, indent=2), encoding="utf-8"
    )

    return project_root


class TestSelfImprovementSystem:
    def test_debugger_logs_error(self, project_root):
        debugger = SmartDebugger(project_root)
        error_data = {
            "type": "StyleError",
            "message": "Missing spaces around operators",
            "context": {"file": "sample.py", "line": 10},
        }

        debugger.analyze_error(error_data)

        assert debugger.debug_log_path.exists()
        log_lines = debugger.debug_log_path.read_text(encoding="utf-8").splitlines()
        assert any("Missing spaces around operators" in line for line in log_lines)

    def test_validator_compiles_report(self, project_root, monkeypatch):
        validator = ContinuousImprovementValidator(project_root)

        stub_results = [
            ValidationTestCase(
                test_id="integration_pass",
                name="integration passes",
                description="Stub integration pass",
                category=ValidationCategory.INTEGRATION,
                result=ValidationResult.PASS,
                duration=0.05,
                details={"component": "integration"},
            ),
            ValidationTestCase(
                test_id="integration_fail",
                name="integration fails",
                description="Stub integration fail",
                category=ValidationCategory.INTEGRATION,
                result=ValidationResult.FAIL,
                duration=0.07,
                error_message="Stub failure",
                details={"component": "integration"},
            ),
        ]

        monkeypatch.setattr(
            validator, "_run_integration_tests", lambda: list(stub_results)
        )
        monkeypatch.setattr(validator, "_run_data_integrity_tests", lambda: [])
        monkeypatch.setattr(validator, "_run_performance_tests", lambda: [])
        monkeypatch.setattr(validator, "_run_end_to_end_tests", lambda: [])
        monkeypatch.setattr(validator, "_print_validation_results", lambda report: None)
        monkeypatch.setattr(validator, "_save_validation_report", lambda report: None)

        report = validator.run_comprehensive_validation()

        assert report.total_tests == 2
        assert report.failed_tests == 1
        assert report.system_health_score == 50.0
        assert "Fair status" in report.summary
        assert report.test_results[0].result == ValidationResult.PASS
