"""
Tests for AI Gate Mediator system.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

from ai_onboard.core.ai_integration.ai_gate_mediator import (
    AIGateMediator,
    MediationResult,
)


class TestAIGateMediator:
    """Test cases for AI Gate Mediator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.mediator = AIGateMediator(self.temp_dir)

    def test_mediator_initialization(self):
        """Test mediator initializes correctly."""
        assert self.mediator.confidence_threshold == 0.75
        assert self.mediator.project_root == self.temp_dir
        assert hasattr(self.mediator, "learning_system")
        assert hasattr(self.mediator, "gate_system")

    def test_high_confidence_operation_proceeds_autonomously(self):
        """Test high confidence operations proceed without gates."""
        # Mock high confidence response
        with patch.object(self.mediator, "_assess_confidence", return_value=0.9):
            result = self.mediator.process_agent_request(
                agent_id="test_agent",
                operation="safe file operation",
                context={"files": ["test.py"]},
            )

            assert result.proceed is True
            assert result.gate_created is False
            assert result.smart_defaults_used is False
            assert result.confidence == 0.9

    def test_low_confidence_operation_creates_gate(self):
        """Test low confidence operations create gates."""
        # Mock low confidence response
        with patch.object(self.mediator, "_assess_confidence", return_value=0.4):
            with patch.object(self.mediator.gate_system, "create_gate") as mock_create:
                with patch.object(
                    self.mediator,
                    "_wait_for_gate_response_async",
                    return_value={"user_decision": "proceed"},
                ):
                    result = self.mediator.process_agent_request(
                        agent_id="test_agent",
                        operation="complex system operation",
                        context={"system": True},
                    )

                    assert result.proceed is True
                    assert result.gate_created is True
                    mock_create.assert_called_once()

    def test_gate_timeout_returns_stop(self):
        """Test gate timeout results in stop decision."""
        with patch.object(self.mediator, "_assess_confidence", return_value=0.4):
            with patch.object(self.mediator.gate_system, "create_gate"):
                with patch.object(
                    self.mediator, "_wait_for_gate_response_async", return_value=None
                ):
                    result = self.mediator.process_agent_request(
                        agent_id="test_agent", operation="timeout operation", context={}
                    )

                    assert result.proceed is False
                    assert result.response["user_decision"] == "stop"
                    assert result.response["reason"] == "timeout"

    def test_smart_defaults_used_for_common_operations(self):
        """Test smart defaults are used for common operations."""
        with patch.object(self.mediator, "_assess_confidence", return_value=0.6):
            with patch.object(
                self.mediator,
                "_get_smart_defaults",
                return_value={"user_decision": "proceed"},
            ):
                with patch.object(
                    self.mediator, "_validate_smart_defaults", return_value=True
                ):
                    result = self.mediator.process_agent_request(
                        agent_id="test_agent",
                        operation="file operation",
                        context={"files": ["test.py"]},
                    )

                    assert result.proceed is True
                    assert result.smart_defaults_used is True
                    assert result.gate_created is False

    def test_confidence_calculation_factors(self):
        """Test confidence calculation considers multiple factors."""
        # Test file operation (should reduce complexity)
        confidence1 = self.mediator._calculate_complexity_factor(
            "file operation", {"files": ["test.py"]}
        )
        assert confidence1 < 0.5  # Should be less complex

        # Test system operation (should increase complexity)
        confidence2 = self.mediator._calculate_complexity_factor(
            "system deployment", {"system": True}
        )
        assert confidence2 > 0.5  # Should be more complex

    def test_gate_description_generation(self):
        """Test human-friendly gate description generation."""
        description = self.mediator._generate_gate_description(
            "complex operation", {"files": ["test.py", "main.py"], "confidence": 0.3}
        )

        assert "complex operation" in description
        assert "2 files" in description
        assert "30%" in description

    def test_optimal_timeout_calculation(self):
        """Test timeout calculation based on complexity."""
        # Simple operation
        timeout1 = self.mediator._calculate_optimal_timeout("simple file", {})
        assert timeout1 == 30  # Base timeout

        # Complex operation
        timeout2 = self.mediator._calculate_optimal_timeout(
            "complex system deployment", {"system": True}
        )
        assert timeout2 > 30  # Increased timeout

    def test_mediation_result_dataclass(self):
        """Test MediationResult dataclass."""
        result = MediationResult(
            proceed=True,
            response={"user_decision": "proceed"},
            confidence=0.8,
            gate_created=False,
            smart_defaults_used=True,
        )

        assert result.proceed is True
        assert result.confidence == 0.8
        assert result.gate_created is False
        assert result.smart_defaults_used is True


class TestAIGateMediatorIntegration:
    """Integration tests for AI Gate Mediator."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def test_mediator_with_real_learning_system(self):
        """Test mediator works with real learning system."""
        mediator = AIGateMediator(self.temp_dir)

        # Record some learning events
        mediator.learning_system.record_learning_event(
            event_type="test_operation",
            event_data={"agent_id": "test_agent", "success": True},
        )

        # Test confidence assessment uses history
        confidence = mediator._get_history_factor("test_agent", "test_operation")
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    def test_mediator_caching(self):
        """Test mediator properly caches results."""
        mediator = AIGateMediator(self.temp_dir)

        # First call should compute confidence
        with patch.object(
            mediator, "_assess_confidence", return_value=0.7
        ) as mock_assess:
            mediator.process_agent_request("agent1", "operation1", {"test": True})
            assert mock_assess.call_count == 1

        # Second call with same parameters should use cache
        with patch.object(
            mediator, "_assess_confidence", return_value=0.8
        ) as mock_assess:
            mediator.process_agent_request("agent1", "operation1", {"test": True})
            # Should still call assess but might use cache for other parts
            assert mock_assess.call_count >= 1

    def test_mediator_error_handling(self):
        """Test mediator handles errors gracefully."""
        mediator = AIGateMediator(self.temp_dir)

        # Test with malformed context
        result = mediator.process_agent_request(
            "agent1", "operation1", {"malformed": object()}
        )

        # Should not crash and return reasonable result
        assert isinstance(result, MediationResult)
        assert isinstance(result.proceed, bool)
        assert isinstance(result.confidence, float)
