"""
Comprehensive Cursor AI Integration Tests.

This module consolidates all Cursor AI integration testing, combining both
comprehensive workflow testing and simplified validation testing.

Tests include:
- Basic Cursor integration functionality
- UX system integration
- Context management
- Decision pipeline processing
- API server functionality
- Metrics collection
- End - to - end workflows
- Multi - agent collaboration
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pytest


class TestCursorIntegrationBasics:
    """Test basic Cursor AI integration functionality."""

    @pytest.fixture
    def cursor_integration(self):
        """Get Cursor integration instance for testing."""
        from ai_onboard.core.cursor_ai_integration import get_cursor_integration

        root = Path.cwd()
        return get_cursor_integration(root)

    @pytest.fixture
    def test_user_id(self):
        """Provide test user ID."""
        return "test_cursor_user"

    def test_cursor_initialization(self, cursor_integration):
        """Test Cursor AI integration initialization."""
        config = cursor_integration.get_configuration()

        # Validate configuration
        required_fields = ["agent_id", "safety_level", "max_autonomous_actions"]
        missing_fields = [f for f in required_fields if f not in config]

        assert (
            len(missing_fields) == 0
        ), f"Missing required config fields: {missing_fields}"
        assert config["agent_id"] is not None
        assert config["safety_level"] in ["low", "medium", "high"]
        assert isinstance(config["max_autonomous_actions"], int)

    def test_agent_profile_creation(self, cursor_integration, test_user_id):
        """Test creating and managing agent profiles."""
        profile_data = {
            "name": "Test Cursor Agent",
            "capabilities": ["code_generation", "planning", "project_analysis"],
            "specializations": ["python", "javascript", "project_management"],
            "collaboration_style": "collaborative",
            "safety_level": "medium",
        }

        profile = cursor_integration.create_agent_profile(test_user_id, profile_data)

        assert profile is not None
        assert profile.get("agent_id") is not None

        # Test profile retrieval
        retrieved_profile = cursor_integration.get_agent_profile(profile["agent_id"])
        assert retrieved_profile is not None

    def test_session_management(self, cursor_integration, test_user_id):
        """Test session creation and management."""
        session = cursor_integration.create_session(
            user_id = test_user_id,
            project_context={
                "project_name": "Test Project",
                "project_type": "software_development",
                "current_phase": "testing",
            },
        )

        assert session is not None
        assert "session_id" in session

        # Test session retrieval
        retrieved_session = cursor_integration.get_session(session["session_id"])
        assert retrieved_session is not None


class TestUXSystemIntegration:
    """Test UX system integration with Cursor workflows."""

    @pytest.fixture
    def ux_system(self):
        """Get UX enhancement system for testing."""
        from ai_onboard.core.user_experience_enhancements import (
            get_ux_enhancement_system,
        )

        root = Path.cwd()
        return get_ux_enhancement_system(root)

    @pytest.fixture
    def test_user_id(self):
        """Provide test user ID."""
        return "test_cursor_user"

    def test_ux_event_recording(self, ux_system, test_user_id):
        """Test UX event recording and intervention generation."""
        from ai_onboard.core.user_experience_enhancements import UXEventType

        # Record cursor command execution event
        event = ux_system.record_ux_event(
            UXEventType.COMMAND_EXECUTION,
            test_user_id,
            command="cursor",
            success = True,
            context={"integration_test": True, "duration_ms": 150},
        )

        assert event is not None
        assert event.event_id is not None
        assert event.event_type == UXEventType.COMMAND_EXECUTION

        # Check for any interventions generated
        interventions = ux_system.get_pending_interventions(test_user_id)
        assert isinstance(interventions, list)

    def test_satisfaction_tracking(self, ux_system, test_user_id):
        """Test satisfaction tracking and trend analysis."""
        # Record satisfaction feedback
        satisfaction_scores = [4, 5, 3, 4, 5]
        contexts = [
            "testing",
            "integration",
            "documentation",
            "troubleshooting",
            "workflow",
        ]

        for score, context in zip(satisfaction_scores, contexts):
            ux_system.satisfaction_tracker.record_satisfaction(
                test_user_id, context, score, f"Test feedback for {context}"
            )

        # Get satisfaction trend
        trend_data = ux_system.satisfaction_tracker.get_satisfaction_trend(
            test_user_id, days = 1
        )

        assert trend_data is not None
        assert trend_data.get("total_responses", 0) == len(satisfaction_scores)
        assert isinstance(trend_data.get("average", 0), (int, float))


class TestContextManagement:
    """Test enhanced conversation context management."""

    @pytest.fixture
    def context_manager(self):
        """Get enhanced conversation context manager."""
        from ai_onboard.core.enhanced_conversation_context import (
            get_enhanced_conversation_context,
        )

        root = Path.cwd()
        return get_enhanced_conversation_context(root)

    @pytest.fixture
    def test_user_id(self):
        """Provide test user ID."""
        return "test_cursor_user"

    def test_context_creation_and_retrieval(self, context_manager, test_user_id):
        """Test creating and retrieving conversation contexts."""
        context_data = {
            "conversation_id": "test_conversation_001",
            "user_id": test_user_id,
            "project_context": {
                "name": "AI Onboard Testing",
                "phase": "integration_testing",
                "goals": ["validate_cursor_integration", "test_workflows"],
            },
            "conversation_history": [
                {
                    "role": "user",
                    "content": "Let's test the Cursor integration",
                    "timestamp": datetime.now().isoformat(),
                }
            ],
        }

        context = context_manager.create_enhanced_context(
            context_data["conversation_id"],
            context_data["user_id"],
            context_data,
        )

        assert context is not None
        assert context.context_id == context_data["conversation_id"]
        assert context.user_id == test_user_id

        # Test context retrieval
        retrieved_context = context_manager.get_context(context_data["conversation_id"])
        assert retrieved_context is not None

    def test_cross_session_context(self, context_manager, test_user_id):
        """Test cross - session context sharing and continuity."""
        session1_id = "test_session_001"
        session2_id = "test_session_002"

        # Session 1: Initial context
        context1 = context_manager.create_enhanced_context(
            session1_id,
            test_user_id,
            {
                "project_insights": [
                    "cursor_integration_complex",
                    "api_testing_needed",
                ],
                "user_preferences": {
                    "detail_level": "comprehensive",
                    "format": "structured",
                },
            },
        )

        # Session 2: Should inherit context
        context2 = context_manager.create_enhanced_context(
            session2_id,
            test_user_id,
            {
                "continuation_from": session1_id,
                "new_goals": ["performance_testing", "error_handling_validation"],
            },
        )

        assert context1 is not None
        assert context2 is not None

        # Test context sharing
        shared_context = context_manager.get_shared_context(
            test_user_id, [session1_id, session2_id]
        )
        assert shared_context is not None


class TestDecisionPipeline:
    """Test advanced agent decision pipeline."""

    @pytest.fixture
    def decision_pipeline(self):
        """Get advanced decision pipeline."""
        from ai_onboard.core.advanced_agent_decision_pipeline import (
            get_advanced_decision_pipeline,
        )

        root = Path.cwd()
        return get_advanced_decision_pipeline(root)

    @pytest.fixture
    def test_user_id(self):
        """Provide test user ID."""
        return "test_cursor_user"

    def test_decision_pipeline_processing(self, decision_pipeline, test_user_id):
        """Test multi - stage decision pipeline processing."""
        decision_request = {
            "request_id": "test_decision_001",
            "user_id": test_user_id,
            "context": {
                "current_task": "cursor_integration_testing",
                "project_phase": "validation",
                "available_tools": [
                    "api_server",
                    "cursor_integration",
                    "metrics_collector",
                ],
            },
            "query": "What's the best approach to validate Cursor AI integration comprehensively?",
            "constraints": {
                "time_limit": "3_hours",
                "risk_tolerance": "medium",
                "automation_level": "high",
            },
        }

        # Process through decision pipeline
        decision_result = decision_pipeline.process_decision(
            decision_request["request_id"],
            decision_request["user_id"],
            decision_request["query"],
            decision_request["context"],
        )

        assert decision_result is not None
        assert decision_result.get("success", False) is True
        assert isinstance(decision_result.get("confidence", 0), (int, float))
        assert isinstance(decision_result.get("stages_completed", []), list)

    def test_contextual_decision_making(self, decision_pipeline, test_user_id):
        """Test contextual reasoning in decision pipeline."""
        scenarios = [
            {
                "name": "high_risk_scenario",
                "context": {
                    "risk_level": "high",
                    "user_expertise": "beginner",
                    "project_criticality": "production",
                },
                "query": "Should we proceed with automated testing of the API integration?",
            },
            {
                "name": "low_risk_scenario",
                "context": {
                    "risk_level": "low",
                    "user_expertise": "expert",
                    "project_criticality": "development",
                },
                "query": "Should we proceed with automated testing of the API integration?",
            },
        ]

        results = {}
        for scenario in scenarios:
            result = decision_pipeline.process_decision(
                f"test_{scenario['name']}",
                test_user_id,
                scenario["query"],
                scenario["context"],
            )
            results[scenario["name"]] = result

        # Validate that different contexts produce different recommendations
        high_risk_result = results.get("high_risk_scenario", {})
        low_risk_result = results.get("low_risk_scenario", {})

        assert high_risk_result.get("success", False)
        assert low_risk_result.get("success", False)

        # Results should be different for different risk contexts
        high_actions = high_risk_result.get("recommended_actions", [])
        low_actions = low_risk_result.get("recommended_actions", [])
        assert high_actions != low_actions  # Should have different recommendations


class TestAPIServerFunctionality:
    """Test API server functionality for Cursor integration."""

    def test_api_server_configuration(self):
        """Test API server configuration and setup."""
        try:
            from ai_onboard.api.server import create_app

            app = create_app(Path.cwd())

            assert app is not None
            # Test that FastAPI app was created successfully
            assert hasattr(app, "routes")

        except ImportError:
            pytest.skip("API server components not available")

    def test_api_server_health_check(self):
        """Test API server health endpoint if server is running."""
        try:
            import requests

            # Check if API server is running
            response = requests.get("http://127.0.0.1:8000 / health", timeout = 2)

            if response.status_code == 200:
                # Server is running, test endpoints
                assert response.json().get("status") == "healthy"

                # Test API info endpoint
                info_response = requests.get("http://127.0.0.1:8000 / api / info")
                assert info_response.status_code == 200

            else:
                pytest.skip("API server not running")

        except (requests.exceptions.RequestException, ImportError):
            pytest.skip("API server not accessible or requests not available")


class TestMetricsCollection:
    """Test unified metrics collection system."""

    @pytest.fixture
    def metrics_collector(self):
        """Get unified metrics collector."""
        from ai_onboard.core.unified_metrics_collector import (
            get_unified_metrics_collector,
        )

        root = Path.cwd()
        return get_unified_metrics_collector(root)

    def test_metrics_collection_system(self, metrics_collector):
        """Test metrics collection system functionality."""

        # Test metric collection capability
        assert hasattr(metrics_collector, "collect_metric")

        # Test that collector is properly initialized
        assert metrics_collector is not None


class TestEndToEndWorkflows:
    """Test complete end - to - end Cursor workflows."""

    @pytest.fixture
    def all_systems(self):
        """Initialize all systems for end - to - end testing."""
        root = Path.cwd()
        systems = {}

        try:
            from ai_onboard.core.cursor_ai_integration import get_cursor_integration

            systems["cursor_integration"] = get_cursor_integration(root)
        except ImportError:
            systems["cursor_integration"] = None

        try:
            from ai_onboard.core.user_experience_enhancements import (
                get_ux_enhancement_system,
            )

            systems["ux_system"] = get_ux_enhancement_system(root)
        except ImportError:
            systems["ux_system"] = None

        return systems

    def test_project_setup_workflow(self, all_systems):
        """Test complete project setup workflow with Cursor integration."""
        cursor_integration = all_systems["cursor_integration"]
        ux_system = all_systems["ux_system"]

        if not cursor_integration or not ux_system:
            pytest.skip("Required systems not available for end - to - end testing")

        test_user_id = "test_workflow_user"
        workflow_steps = []

        # Step 1: Initialize Cursor integration
        try:
            cursor_init = cursor_integration.initialize_integration(
                {
                    "user_id": test_user_id,
                    "project_name": "Test Project Setup",
                    "integration_level": "comprehensive",
                }
            )
            workflow_steps.append(("cursor_init", cursor_init is not None))
        except Exception:
            workflow_steps.append(("cursor_init", False))

        # Step 2: Record UX events
        try:
            from ai_onboard.core.user_experience_enhancements import UXEventType

            ux_event = ux_system.record_ux_event(
                UXEventType.WORKFLOW_COMPLETION,
                test_user_id,
                context={"workflow": "project_setup", "success": True},
            )
            workflow_steps.append(("ux_recording", ux_event is not None))
        except Exception:
            workflow_steps.append(("ux_recording", False))

        # Evaluate workflow success
        successful_steps = sum(1 for _, success in workflow_steps if success)
        total_steps = len(workflow_steps)
        success_rate = successful_steps / total_steps if total_steps > 0 else 0

        assert success_rate >= 0.5  # At least 50% success rate for basic functionality

    def test_cursor_integration_basic_validation(self):
        """Test basic Cursor integration functionality - simplified version."""
        try:
            from ai_onboard.core.cursor_ai_integration import get_cursor_integration

            root = Path.cwd()

            # Test integration initialization
            cursor_integration = get_cursor_integration(root)

            # Test configuration retrieval
            config = cursor_integration.get_configuration()

            # Validate basic configuration
            required_fields = ["agent_id", "safety_level", "max_autonomous_actions"]
            missing_fields = [f for f in required_fields if f not in config]

            assert (
                len(missing_fields) == 0
            ), f"Missing configuration fields: {missing_fields}"

        except Exception as e:
            pytest.fail(f"Basic Cursor integration validation failed: {e}")


# Utility functions for testing
def run_comprehensive_cursor_testing(root: Path) -> Dict[str, Any]:
    """Run comprehensive Cursor workflow testing - legacy function for compatibility."""
    import subprocess
    import sys

    # Run pytest on this module
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(Path(__file__)), "-v", "--tb = short"],
        capture_output = True,
        text = True,
    )

    return {
        "overall_success": result.returncode == 0,
        "output": result.stdout,
        "errors": result.stderr,
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    # Run the comprehensive test suite
    root = Path.cwd()
    results = run_comprehensive_cursor_testing(root)

    print("🧪 Cursor Integration Test Results")
    print("=" * 50)
    print(f"Overall Success: {'✅' if results['overall_success'] else '❌'}")
    print(f"Timestamp: {results['timestamp']}")

    if results["output"]:
        print("\nTest Output:")
        print(results["output"])

    if results["errors"]:
        print("\nErrors:")
        print(results["errors"])

    # Exit with appropriate code
    exit(0 if results["overall_success"] else 1)
