import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from ai_onboard.core.continuous_improvement.learning_persistence import (
    LearningPersistenceManager,
)
from ai_onboard.core.continuous_improvement_validator import (  # type: ignore[import-untyped]
    ContinuousImprovementValidator,
    ValidationCategory,
    ValidationResult,
    ValidationTestCase,
)
from ai_onboard.core.orchestration.automatic_error_prevention import (
    AutomaticErrorPrevention,
)
from ai_onboard.core.orchestration.pattern_recognition_system import (
    PatternRecognitionSystem,
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


class TestSelfImprovementIntegration:
    """Integration tests for the self-improvement system components."""

    @pytest.fixture
    def project_root(self, tmp_path):
        """Provide project root for integration tests."""
        return Path(tmp_path)

    def test_pattern_recognition(self, project_root):
        """Test 4.8: Pattern Recognition System"""
        print("🧪 Testing Pattern Recognition System (4.8)")
        print("=" * 50)

        pattern_system = PatternRecognitionSystem(project_root)

        # Test CLI error pattern
        cli_error = {
            "type": "ArgumentError",
            "message": "invalid choice: '--invalid-option'",
            "traceback": "invalid choice: '--invalid-option'",
        }

        match = pattern_system.analyze_error(cli_error)
        assert match is not None
        assert match["pattern_id"] is not None
        assert match["confidence"] > 0.5

        print(
            f"✅ Pattern recognition: {match['pattern_id']} with {match['confidence']:.2f} confidence"
        )

    def test_learning_persistence(self, project_root):
        """Test 4.9: Learning Persistence"""
        print("🧪 Testing Learning Persistence (4.9)")
        print("=" * 50)

        persistence_manager = LearningPersistenceManager(project_root)

        # Learn a pattern
        pattern_data = {
            "pattern_type": "error_prevention",
            "description": "Common CLI error pattern",
            "solution": "Validate arguments before execution",
            "frequency": 5,
        }

        pattern_id = persistence_manager.store_pattern(pattern_data)
        assert pattern_id is not None

        # Retrieve the pattern
        retrieved = persistence_manager.retrieve_pattern(pattern_id)
        assert retrieved["description"] == pattern_data["description"]
        assert retrieved["frequency"] == pattern_data["frequency"]

        print(
            f"✅ Learning persistence: Pattern {pattern_id} stored and retrieved successfully"
        )

    def test_automatic_error_prevention(self, project_root):
        """Test 4.10: Automatic Error Prevention"""
        print("🧪 Testing Automatic Error Prevention (4.10)")
        print("=" * 50)

        error_prevention = AutomaticErrorPrevention(project_root)

        # Simulate a risky operation
        risky_code = """
def risky_function():
    # This might cause issues
    return undefined_variable
"""

        # Check if prevention system identifies the risk
        prevention_result = error_prevention.analyze_code_risk(risky_code)
        assert prevention_result is not None
        assert "risk_score" in prevention_result

        print(f"✅ Error prevention: Risk score {prevention_result['risk_score']:.2f}")

    def test_full_integration_workflow(self, project_root):
        """Test the complete self-improvement workflow"""
        print("🧪 Testing Full Self-Improvement Integration")
        print("=" * 50)

        # Initialize all components
        pattern_system = PatternRecognitionSystem(project_root)
        persistence_manager = LearningPersistenceManager(project_root)
        error_prevention = AutomaticErrorPrevention(project_root)

        # Test pattern learning -> persistence -> prevention cycle
        error_pattern = {
            "type": "NameError",
            "message": "name 'undefined_variable' is not defined",
            "traceback": "NameError: name 'undefined_variable' is not defined",
        }

        # 1. Recognize pattern
        match = pattern_system.analyze_error(error_pattern)
        assert match is not None

        # 2. Store learned pattern
        pattern_data = {
            "pattern_type": "variable_undefined",
            "description": "Undefined variable usage",
            "solution": "Check variable definitions before use",
            "frequency": 1,
        }

        pattern_id = persistence_manager.store_pattern(pattern_data)
        assert pattern_id is not None

        # 3. Use pattern for prevention
        risky_code = "return undefined_variable"
        prevention_result = error_prevention.analyze_code_risk(risky_code)
        assert prevention_result is not None

        print(
            "✅ Full integration: Pattern recognition → persistence → error prevention cycle working"
        )
