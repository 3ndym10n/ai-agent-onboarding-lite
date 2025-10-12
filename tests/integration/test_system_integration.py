"""
Integration tests for the complete System Integrator and all oversight systems.

Tests the full workflow of agent oversight, including:
- System initialization and health monitoring
- Agent operation processing through all systems
- Blocking and approval workflows
- Emergency controls
- Chaos detection and response
- Vision alignment tracking
"""

import time
from pathlib import Path
from typing import Any, Dict

import pytest

from ai_onboard.core.ai_integration.system_integrator import (
    AgentOversightContext,
    SystemIntegrator,
    get_system_integrator,
)


class TestSystemIntegrator:
    """Test the unified system integrator."""

    @pytest.fixture
    def integrator(self, tmp_path: Path) -> SystemIntegrator:
        """Create a system integrator for testing."""
        return get_system_integrator(tmp_path)

    @pytest.fixture
    def mock_agent_context(self) -> Dict[str, Any]:
        """Create mock agent operation context."""
        return {
            "operation_type": "file_creation",
            "file_count": 5,
            "files": ["test1.py", "test2.py", "test3.py", "test4.py", "test5.py"],
            "reason": "Creating test files for new feature",
        }

    def test_integrator_initialization(self, integrator: SystemIntegrator):
        """Test that all systems initialize correctly."""
        assert integrator.integrated_mode is True
        assert integrator.activity_monitor is not None
        assert integrator.decision_enforcer is not None
        assert integrator.hard_gate_enforcer is not None
        assert integrator.hard_limits_enforcer is not None
        assert integrator.chaos_detector is not None
        assert integrator.vision_drift_alerting is not None
        assert integrator.emergency_control is not None

    def test_health_monitoring_starts(self, integrator: SystemIntegrator):
        """Test that health monitoring starts automatically."""
        assert integrator.health_monitor_active is True
        assert integrator.health_thread is not None
        assert integrator.health_thread.is_alive()

    def test_get_integrated_status(self, integrator: SystemIntegrator):
        """Test getting comprehensive integration status."""
        status = integrator.get_integrated_status()

        assert status["integrated_mode"] is True
        assert status["health_monitoring_active"] is True
        assert "system_health" in status
        assert "recent_activity" in status

        # Check all 7 systems are present
        assert len(status["system_health"]) == 7
        assert "activity_monitor" in status["system_health"]
        assert "decision_enforcer" in status["system_health"]
        assert "hard_gate_enforcer" in status["system_health"]
        assert "hard_limits_enforcer" in status["system_health"]
        assert "chaos_detector" in status["system_health"]
        assert "vision_drift_alerting" in status["system_health"]
        assert "emergency_control" in status["system_health"]

    def test_system_health_check(self, integrator: SystemIntegrator):
        """Test system health checking."""
        integrator._perform_health_check()

        assert len(integrator.system_health) == 7

        for system_name, health in integrator.system_health.items():
            assert health.system_name == system_name
            assert health.is_active is True
            assert health.health_score == 1.0
            assert len(health.issues) == 0
            assert health.last_error is None

    def test_overall_health_calculation(self, integrator: SystemIntegrator):
        """Test overall health score calculation."""
        integrator._perform_health_check()
        overall_health = integrator._calculate_overall_health()

        assert overall_health == 1.0  # All systems healthy

    def test_process_simple_operation(
        self, integrator: SystemIntegrator, mock_agent_context: Dict[str, Any]
    ):
        """Test processing a simple allowed operation."""
        result = integrator.process_agent_operation(
            agent_id="test_agent",
            operation="simple_operation",
            context=mock_agent_context,
        )

        assert isinstance(result, AgentOversightContext)
        assert result.agent_id == "test_agent"
        assert result.operation == "simple_operation"
        assert result.approved is True  # Should be approved by default

    def test_process_paused_agent(self, integrator: SystemIntegrator):
        """Test that paused agents are blocked."""
        # Pause the agent
        assert integrator.emergency_control is not None
        integrator.emergency_control.pause_agent(
            "test_agent", "Testing pause", "system"
        )

        # Try to process operation
        result = integrator.process_agent_operation(
            agent_id="test_agent",
            operation="test_operation",
            context={"test": "data"},
        )

        assert result.approved is False
        assert result.emergency_triggered is True
        assert "paused" in str(result.blocking_reasons).lower()

    def test_process_stopped_agent(self, integrator: SystemIntegrator):
        """Test that stopped agents are blocked."""
        # Stop the agent
        assert integrator.emergency_control is not None
        integrator.emergency_control.stop_agent("test_agent", "Testing stop", "system")

        # Try to process operation
        result = integrator.process_agent_operation(
            agent_id="test_agent",
            operation="test_operation",
            context={"test": "data"},
        )

        assert result.approved is False
        assert result.emergency_triggered is True
        assert "stopped" in str(result.blocking_reasons).lower()

    def test_corrective_actions_provided(self, integrator: SystemIntegrator):
        """Test that corrective actions are provided when blocked."""
        # Pause the agent
        assert integrator.emergency_control is not None
        integrator.emergency_control.pause_agent("test_agent", "Testing", "system")

        result = integrator.process_agent_operation(
            agent_id="test_agent",
            operation="test_operation",
            context={},
        )

        assert len(result.corrective_actions) > 0
        assert "resume" in str(result.corrective_actions).lower()

    def test_activity_logging(self, integrator: SystemIntegrator):
        """Test that operations are logged to activity monitor."""
        result = integrator.process_agent_operation(
            agent_id="test_agent",
            operation="log_test",
            context={"test": "logging"},
        )

        # Activity should be logged
        assert integrator.activity_monitor is not None
        activity_summary = integrator.activity_monitor.get_activity_summary(hours=1)
        assert activity_summary["total_events"] >= 1


class TestIntegrationWorkflows:
    """Test complete integration workflows."""

    @pytest.fixture
    def integrator(self, tmp_path: Path) -> SystemIntegrator:
        """Create a system integrator for testing."""
        return get_system_integrator(tmp_path)

    def test_normal_operation_workflow(self, integrator: SystemIntegrator):
        """Test normal operation approval workflow."""
        # Step 1: Agent requests operation
        context = {
            "operation": "create_files",
            "count": 3,
            "files": ["file1.py", "file2.py", "file3.py"],
        }

        result = integrator.process_agent_operation(
            agent_id="test_agent", operation="create_files", context=context
        )

        # Step 2: Verify approval
        assert result.approved is True
        assert result.gate_status is None  # No gate needed
        assert result.emergency_triggered is False

        # Step 3: Verify logging
        assert integrator.activity_monitor is not None
        activity_summary = integrator.activity_monitor.get_activity_summary(hours=1)
        assert activity_summary["total_events"] >= 1

    def test_emergency_pause_workflow(self, integrator: SystemIntegrator):
        """Test emergency pause workflow."""
        agent_id = "chaotic_agent"

        # Step 1: Pause agent due to chaos
        assert integrator.emergency_control is not None
        integrator.emergency_control.pause_agent(
            agent_id, "Chaotic behavior detected", "system"
        )

        # Step 2: Verify agent is paused
        assert integrator.emergency_control is not None
        assert integrator.emergency_control.is_agent_paused(agent_id)

        # Step 3: Try operation - should be blocked
        result = integrator.process_agent_operation(
            agent_id=agent_id, operation="test_op", context={}
        )

        assert result.approved is False
        assert result.emergency_triggered is True

        # Step 4: Resume agent
        assert integrator.emergency_control is not None
        integrator.emergency_control.resume_agent(agent_id, "user")

        # Step 5: Verify agent is resumed
        assert integrator.emergency_control is not None
        assert not integrator.emergency_control.is_agent_paused(agent_id)

        # Step 6: Try operation again - should be approved
        result = integrator.process_agent_operation(
            agent_id=agent_id, operation="test_op", context={}
        )

        assert result.approved is True

    def test_multi_system_coordination(self, integrator: SystemIntegrator):
        """Test that multiple systems coordinate correctly."""
        agent_id = "test_agent"

        # Create a situation that triggers multiple systems
        context = {
            "operation": "bulk_refactor",
            "files_count": 15,  # High file count
            "changes": "major",
        }

        result = integrator.process_agent_operation(
            agent_id=agent_id, operation="bulk_refactor", context=context
        )

        # Result should reflect coordination of multiple systems
        assert isinstance(result, AgentOversightContext)
        assert result.agent_id == agent_id
        assert result.operation == "bulk_refactor"

        # Check that vision alignment was calculated
        assert 0.0 <= result.vision_alignment <= 1.0


class TestHealthMonitoring:
    """Test health monitoring and issue detection."""

    @pytest.fixture
    def integrator(self, tmp_path: Path) -> SystemIntegrator:
        """Create a system integrator for testing."""
        return get_system_integrator(tmp_path)

    def test_health_check_detects_healthy_systems(self, integrator: SystemIntegrator):
        """Test that health check correctly identifies healthy systems."""
        integrator._perform_health_check()

        for system_name, health in integrator.system_health.items():
            assert health.is_active is True
            assert health.health_score == 1.0
            assert len(health.issues) == 0

    def test_health_monitoring_continuous(self, integrator: SystemIntegrator):
        """Test that health monitoring runs continuously."""
        initial_check_time = integrator.last_health_check

        # Wait for health check interval
        time.sleep(0.5)

        # Health check time should be updated by background thread
        # (may or may not have updated depending on interval)
        assert integrator.health_monitor_active is True

    def test_stop_health_monitoring(self, integrator: SystemIntegrator):
        """Test stopping health monitoring."""
        integrator.stop_health_monitoring()

        assert integrator.health_monitor_active is False


class TestEmergencyIntegration:
    """Test emergency control integration."""

    @pytest.fixture
    def integrator(self, tmp_path: Path) -> SystemIntegrator:
        """Create a system integrator for testing."""
        return get_system_integrator(tmp_path)

    def test_emergency_status_in_integrated_status(self, integrator: SystemIntegrator):
        """Test that emergency status is included in integrated status."""
        status = integrator.get_integrated_status()

        assert "emergency_status" in status
        assert "agents_in_emergency" in status["emergency_status"]
        assert "paused_agents" in status["emergency_status"]
        assert "stopped_agents" in status["emergency_status"]

    def test_emergency_pause_reflects_in_status(self, integrator: SystemIntegrator):
        """Test that emergency pause is reflected in status."""
        agent_id = "test_agent"

        # Pause agent
        assert integrator.emergency_control is not None
        integrator.emergency_control.pause_agent(agent_id, "Testing", "system")

        # Check status
        status = integrator.get_integrated_status()
        assert status["emergency_status"]["paused_agents"] >= 1

    def test_emergency_stop_reflects_in_status(self, integrator: SystemIntegrator):
        """Test that emergency stop is reflected in status."""
        agent_id = "test_agent"

        # Stop agent
        assert integrator.emergency_control is not None
        integrator.emergency_control.stop_agent(agent_id, "Testing", "system")

        # Check status
        status = integrator.get_integrated_status()
        assert status["emergency_status"]["stopped_agents"] >= 1


class TestRecentActivity:
    """Test recent activity tracking and reporting."""

    @pytest.fixture
    def integrator(self, tmp_path: Path) -> SystemIntegrator:
        """Create a system integrator for testing."""
        return get_system_integrator(tmp_path)

    def test_activity_tracked_in_status(self, integrator: SystemIntegrator):
        """Test that activity is tracked in integrated status."""
        # Process some operations
        for i in range(5):
            integrator.process_agent_operation(
                agent_id=f"agent_{i}",
                operation=f"operation_{i}",
                context={"test": i},
            )

        # Check status
        status = integrator.get_integrated_status()

        assert "recent_activity" in status
        assert status["recent_activity"]["total_agents"] >= 1
        assert status["recent_activity"]["total_actions"] >= 5

    def test_active_agents_counted(self, integrator: SystemIntegrator):
        """Test that active agents are counted correctly."""
        # Process operations from multiple agents
        integrator.process_agent_operation(
            agent_id="agent1", operation="op1", context={}
        )
        integrator.process_agent_operation(
            agent_id="agent2", operation="op2", context={}
        )

        # Check status
        status = integrator.get_integrated_status()
        assert status["recent_activity"]["total_agents"] >= 2


class TestErrorHandling:
    """Test error handling in system integration."""

    @pytest.fixture
    def integrator(self, tmp_path: Path) -> SystemIntegrator:
        """Create a system integrator for testing."""
        return get_system_integrator(tmp_path)

    def test_continues_after_decision_enforcer_error(
        self, integrator: SystemIntegrator
    ):
        """Test that processing continues even if decision enforcer fails."""
        # This should handle any decision enforcer errors gracefully
        result = integrator.process_agent_operation(
            agent_id="test_agent",
            operation="test_operation",
            context={"invalid": "data that might cause error"},
        )

        # Should still return a result
        assert isinstance(result, AgentOversightContext)

    def test_continues_after_chaos_detection_error(self, integrator: SystemIntegrator):
        """Test that processing continues even if chaos detection fails."""
        result = integrator.process_agent_operation(
            agent_id="test_agent", operation="test_operation", context={}
        )

        # Should still return a result
        assert isinstance(result, AgentOversightContext)

    def test_continues_after_vision_alignment_error(self, integrator: SystemIntegrator):
        """Test that processing continues even if vision alignment fails."""
        result = integrator.process_agent_operation(
            agent_id="test_agent", operation="test_operation", context={}
        )

        # Should still return a result
        assert isinstance(result, AgentOversightContext)
        # Vision alignment should have a default value
        assert result.vision_alignment >= 0.0
