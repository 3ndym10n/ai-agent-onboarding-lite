"""
T16: Test integration with real Cursor workflows

This comprehensive testing suite validates the complete AI collaboration system
including Cursor AI integration, API communication, context management,
decision pipelines, and user experience enhancements.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from ai_onboard.api.models import *
from ai_onboard.api.server import create_app
from ai_onboard.core.advanced_agent_decision_pipeline import (
    get_advanced_decision_pipeline,
)
from ai_onboard.core.ai_agent_orchestration import get_ai_agent_orchestration_layer

# Import our core systems
from ai_onboard.core.cursor_ai_integration import get_cursor_integration
from ai_onboard.core.enhanced_conversation_context import (
    get_enhanced_conversation_context,
)
from ai_onboard.core.unified_metrics_collector import get_unified_metrics_collector
from ai_onboard.core.user_experience_enhancements import get_ux_enhancement_system


class CursorWorkflowTester:
    """Comprehensive tester for real Cursor workflows."""

    def __init__(self, root: Path):
        self.root = root
        self.test_results = []
        self.performance_metrics = {}
        self.error_log = []

        # Initialize all systems
        self.cursor_integration = get_cursor_integration(root)
        self.aaol = get_ai_agent_orchestration_layer(root)
        self.context_manager = get_enhanced_conversation_context(root)
        self.decision_pipeline = get_advanced_decision_pipeline(root)
        self.ux_system = get_ux_enhancement_system(root)
        self.metrics_collector = get_unified_metrics_collector(root)

        # Test configuration
        self.test_user_id = "test_cursor_user"
        self.test_session_id = None

    def log_test_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """Log a test result with timing and details."""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details,
        }
        self.test_results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not success and "error" in details:
            print(f"   Error: {details['error']}")
        if "duration_ms" in details:
            print(f"   Duration: {details['duration_ms']:.1f}ms")

    def measure_performance(self, operation_name: str):
        """Context manager for measuring operation performance."""

        class PerformanceMeasurer:
            def __init__(self, tester, name):
                self.tester = tester
                self.name = name
                self.start_time = None

            def __enter__(self):
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                duration = (time.time() - self.start_time) * 1000
                self.tester.performance_metrics[self.name] = duration

        return PerformanceMeasurer(self, operation_name)


class TestCursorIntegrationBasics(CursorWorkflowTester):
    """Test basic Cursor AI integration functionality."""

    def test_cursor_initialization(self):
        """Test Cursor AI integration initialization."""
        try:
            with self.measure_performance("cursor_init"):
                # Test initialization
                config = self.cursor_integration.get_configuration()

                # Validate configuration
                required_fields = ["agent_id", "safety_level", "max_autonomous_actions"]
                missing_fields = [f for f in required_fields if f not in config]

                success = len(missing_fields) == 0
                details = {
                    "config_fields": list(config.keys()),
                    "missing_fields": missing_fields,
                    "duration_ms": self.performance_metrics.get("cursor_init", 0),
                }

                if not success:
                    details["error"] = (
                        f"Missing required config fields: {missing_fields}"
                    )

                self.log_test_result("cursor_initialization", success, details)
                return success

        except Exception as e:
            self.log_test_result(
                "cursor_initialization",
                False,
                {"error": str(e), "exception_type": type(e).__name__},
            )
            return False

    def test_agent_profile_creation(self):
        """Test creating and managing agent profiles."""
        try:
            with self.measure_performance("agent_profile"):
                # Create test agent profile
                profile_data = {
                    "name": "Test Cursor Agent",
                    "capabilities": ["code_generation", "planning", "analysis"],
                    "specializations": ["python", "javascript", "project_management"],
                    "collaboration_style": "pair_programming",
                    "safety_level": "medium",
                }

                profile = self.cursor_integration.create_agent_profile(
                    self.test_user_id, profile_data
                )

                # Validate profile creation
                success = profile is not None and profile.get("agent_id") is not None
                details = {
                    "profile_created": success,
                    "agent_id": profile.get("agent_id") if profile else None,
                    "duration_ms": self.performance_metrics.get("agent_profile", 0),
                }

                if success:
                    # Test profile retrieval
                    retrieved_profile = self.cursor_integration.get_agent_profile(
                        profile["agent_id"]
                    )
                    details["profile_retrievable"] = retrieved_profile is not None
                    success = success and retrieved_profile is not None

                self.log_test_result("agent_profile_creation", success, details)
                return success

        except Exception as e:
            self.log_test_result(
                "agent_profile_creation",
                False,
                {"error": str(e), "exception_type": type(e).__name__},
            )
            return False

    def test_session_management(self):
        """Test session creation and management."""
        try:
            with self.measure_performance("session_mgmt"):
                # Create session
                session = self.cursor_integration.create_session(
                    user_id=self.test_user_id,
                    project_context={
                        "project_name": "Test Project",
                        "project_type": "software_development",
                        "current_phase": "testing",
                    },
                )

                success = session is not None and "session_id" in session
                details = {
                    "session_created": success,
                    "session_id": session.get("session_id") if session else None,
                    "duration_ms": self.performance_metrics.get("session_mgmt", 0),
                }

                if success:
                    self.test_session_id = session["session_id"]

                    # Test session retrieval
                    retrieved_session = self.cursor_integration.get_session(
                        self.test_session_id
                    )
                    details["session_retrievable"] = retrieved_session is not None
                    success = success and retrieved_session is not None

                self.log_test_result("session_management", success, details)
                return success

        except Exception as e:
            self.log_test_result(
                "session_management",
                False,
                {"error": str(e), "exception_type": type(e).__name__},
            )
            return False


class TestContextManagement(CursorWorkflowTester):
    """Test enhanced conversation context management."""

    def test_context_creation_and_retrieval(self):
        """Test creating and retrieving conversation contexts."""
        try:
            with self.measure_performance("context_ops"):
                # Create enhanced context
                context_data = {
                    "conversation_id": "test_conversation_001",
                    "user_id": self.test_user_id,
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

                context = self.context_manager.create_enhanced_context(
                    context_data["conversation_id"],
                    context_data["user_id"],
                    context_data,
                )

                success = context is not None
                details = {
                    "context_created": success,
                    "context_id": context.context_id if context else None,
                    "duration_ms": self.performance_metrics.get("context_ops", 0),
                }

                if success:
                    # Test context retrieval
                    retrieved_context = self.context_manager.get_context(
                        context_data["conversation_id"]
                    )
                    details["context_retrievable"] = retrieved_context is not None
                    success = success and retrieved_context is not None

                self.log_test_result("context_creation_retrieval", success, details)
                return success

        except Exception as e:
            self.log_test_result(
                "context_creation_retrieval",
                False,
                {"error": str(e), "exception_type": type(e).__name__},
            )
            return False

    def test_cross_session_context(self):
        """Test cross-session context sharing and continuity."""
        try:
            with self.measure_performance("cross_session"):
                # Create multiple sessions with shared context
                session1_id = "test_session_001"
                session2_id = "test_session_002"

                # Session 1: Initial context
                context1 = self.context_manager.create_enhanced_context(
                    session1_id,
                    self.test_user_id,
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
                context2 = self.context_manager.create_enhanced_context(
                    session2_id,
                    self.test_user_id,
                    {
                        "continuation_from": session1_id,
                        "new_goals": [
                            "performance_testing",
                            "error_handling_validation",
                        ],
                    },
                )

                # Test context sharing
                shared_context = self.context_manager.get_shared_context(
                    self.test_user_id, [session1_id, session2_id]
                )

                success = (
                    context1 is not None
                    and context2 is not None
                    and shared_context is not None
                )

                details = {
                    "context1_created": context1 is not None,
                    "context2_created": context2 is not None,
                    "shared_context_available": shared_context is not None,
                    "duration_ms": self.performance_metrics.get("cross_session", 0),
                }

                if success and shared_context:
                    details["shared_insights_count"] = len(
                        shared_context.get("insights", [])
                    )
                    details["shared_preferences"] = shared_context.get(
                        "user_preferences", {}
                    )

                self.log_test_result("cross_session_context", success, details)
                return success

        except Exception as e:
            self.log_test_result(
                "cross_session_context",
                False,
                {"error": str(e), "exception_type": type(e).__name__},
            )
            return False


class TestDecisionPipeline(CursorWorkflowTester):
    """Test advanced agent decision pipeline."""

    def test_decision_pipeline_processing(self):
        """Test multi-stage decision pipeline processing."""
        try:
            with self.measure_performance("decision_pipeline"):
                # Create test decision request
                decision_request = {
                    "request_id": "test_decision_001",
                    "user_id": self.test_user_id,
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
                decision_result = self.decision_pipeline.process_decision(
                    decision_request["request_id"],
                    decision_request["user_id"],
                    decision_request["query"],
                    decision_request["context"],
                )

                success = decision_result is not None and decision_result.get(
                    "success", False
                )
                details = {
                    "pipeline_completed": success,
                    "decision_confidence": (
                        decision_result.get("confidence", 0) if decision_result else 0
                    ),
                    "stages_completed": (
                        decision_result.get("stages_completed", [])
                        if decision_result
                        else []
                    ),
                    "duration_ms": self.performance_metrics.get("decision_pipeline", 0),
                }

                if success:
                    details["recommended_actions"] = decision_result.get(
                        "recommended_actions", []
                    )
                    details["risk_assessment"] = decision_result.get(
                        "risk_assessment", {}
                    )

                self.log_test_result("decision_pipeline_processing", success, details)
                return success

        except Exception as e:
            self.log_test_result(
                "decision_pipeline_processing",
                False,
                {"error": str(e), "exception_type": type(e).__name__},
            )
            return False

    def test_contextual_decision_making(self):
        """Test contextual reasoning in decision pipeline."""
        try:
            with self.measure_performance("contextual_decisions"):
                # Test different context scenarios
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
                    result = self.decision_pipeline.process_decision(
                        f"test_{scenario['name']}",
                        self.test_user_id,
                        scenario["query"],
                        scenario["context"],
                    )
                    results[scenario["name"]] = result

                # Validate that different contexts produce different recommendations
                high_risk_result = results.get("high_risk_scenario", {})
                low_risk_result = results.get("low_risk_scenario", {})

                success = high_risk_result.get(
                    "success", False
                ) and low_risk_result.get("success", False)

                details = {
                    "both_scenarios_processed": success,
                    "high_risk_confidence": high_risk_result.get("confidence", 0),
                    "low_risk_confidence": low_risk_result.get("confidence", 0),
                    "contextual_differentiation": (
                        high_risk_result.get("recommended_actions", [])
                        != low_risk_result.get("recommended_actions", [])
                    ),
                    "duration_ms": self.performance_metrics.get(
                        "contextual_decisions", 0
                    ),
                }

                self.log_test_result("contextual_decision_making", success, details)
                return success

        except Exception as e:
            self.log_test_result(
                "contextual_decision_making",
                False,
                {"error": str(e), "exception_type": type(e).__name__},
            )
            return False


class TestUXEnhancements(CursorWorkflowTester):
    """Test user experience enhancement system."""

    def test_ux_event_recording(self):
        """Test UX event recording and intervention generation."""
        try:
            with self.measure_performance("ux_events"):
                # Record various UX events
                events_to_test = [
                    {
                        "event_type": "COMMAND_EXECUTION",
                        "context": {
                            "command": "cursor",
                            "success": True,
                            "duration_ms": 150,
                        },
                    },
                    {
                        "event_type": "ERROR_ENCOUNTER",
                        "context": {"error_type": "ConnectionError", "command": "api"},
                        "error_details": "Failed to connect to API server",
                    },
                    {
                        "event_type": "HELP_REQUEST",
                        "context": {
                            "topic": "cursor_integration",
                            "user_expertise": "intermediate",
                        },
                    },
                ]

                recorded_events = []
                for event_data in events_to_test:
                    from ai_onboard.core.user_experience_enhancements import UXEventType

                    event_type = getattr(UXEventType, event_data["event_type"])

                    event = self.ux_system.record_ux_event(
                        event_type,
                        self.test_user_id,
                        **event_data.get("context", {}),
                        error_details=event_data.get("error_details"),
                    )
                    recorded_events.append(event)

                success = len(recorded_events) == len(events_to_test)
                details = {
                    "events_recorded": len(recorded_events),
                    "expected_events": len(events_to_test),
                    "event_ids": [e.event_id for e in recorded_events],
                    "duration_ms": self.performance_metrics.get("ux_events", 0),
                }

                # Check if interventions were generated
                interventions = self.ux_system.get_pending_interventions(
                    self.test_user_id
                )
                details["interventions_generated"] = len(interventions)

                self.log_test_result("ux_event_recording", success, details)
                return success

        except Exception as e:
            self.log_test_result(
                "ux_event_recording",
                False,
                {"error": str(e), "exception_type": type(e).__name__},
            )
            return False

    def test_satisfaction_tracking(self):
        """Test satisfaction tracking and trend analysis."""
        try:
            with self.measure_performance("satisfaction_tracking"):
                # Record satisfaction feedback
                satisfaction_scores = [4, 5, 3, 4, 5, 4, 3, 5]
                contexts = [
                    "testing",
                    "integration",
                    "documentation",
                    "troubleshooting",
                    "workflow",
                    "performance",
                    "usability",
                    "overall",
                ]

                for score, context in zip(satisfaction_scores, contexts):
                    self.ux_system.satisfaction_tracker.record_satisfaction(
                        self.test_user_id,
                        context,
                        score,
                        f"Test feedback for {context}",
                    )

                # Get satisfaction trend
                trend_data = self.ux_system.satisfaction_tracker.get_satisfaction_trend(
                    self.test_user_id, days=1
                )

                success = trend_data is not None and trend_data.get(
                    "total_responses", 0
                ) == len(satisfaction_scores)

                details = {
                    "satisfaction_records": len(satisfaction_scores),
                    "trend_data_available": trend_data is not None,
                    "average_satisfaction": (
                        trend_data.get("average", 0) if trend_data else 0
                    ),
                    "satisfaction_trend": (
                        trend_data.get("trend", "unknown") if trend_data else "unknown"
                    ),
                    "duration_ms": self.performance_metrics.get(
                        "satisfaction_tracking", 0
                    ),
                }

                self.log_test_result("satisfaction_tracking", success, details)
                return success

        except Exception as e:
            self.log_test_result(
                "satisfaction_tracking",
                False,
                {"error": str(e), "exception_type": type(e).__name__},
            )
            return False


class TestEndToEndWorkflows(CursorWorkflowTester):
    """Test complete end-to-end workflows."""

    def test_project_setup_workflow(self):
        """Test complete project setup workflow with Cursor integration."""
        try:
            with self.measure_performance("project_setup_workflow"):
                workflow_steps = []

                # Step 1: Initialize Cursor integration
                cursor_init = self.cursor_integration.initialize_integration(
                    {
                        "user_id": self.test_user_id,
                        "project_name": "Test Project Setup",
                        "integration_level": "comprehensive",
                    }
                )
                workflow_steps.append(("cursor_init", cursor_init is not None))

                # Step 2: Create enhanced context
                context = self.context_manager.create_enhanced_context(
                    "project_setup_001",
                    self.test_user_id,
                    {
                        "workflow": "project_setup",
                        "stage": "initialization",
                        "tools_available": ["cursor", "api", "ux_system"],
                    },
                )
                workflow_steps.append(("context_creation", context is not None))

                # Step 3: Process setup decision
                decision = self.decision_pipeline.process_decision(
                    "setup_decision_001",
                    self.test_user_id,
                    "What's the optimal project setup sequence for this workflow?",
                    {
                        "workflow_type": "cursor_integration",
                        "user_experience": "comprehensive",
                    },
                )
                workflow_steps.append(
                    (
                        "decision_processing",
                        decision is not None and decision.get("success", False),
                    )
                )

                # Step 4: Record UX events
                from ai_onboard.core.user_experience_enhancements import UXEventType

                ux_event = self.ux_system.record_ux_event(
                    UXEventType.WORKFLOW_COMPLETION,
                    self.test_user_id,
                    context={"workflow": "project_setup", "success": True},
                )
                workflow_steps.append(("ux_recording", ux_event is not None))

                # Evaluate workflow success
                successful_steps = sum(1 for _, success in workflow_steps if success)
                total_steps = len(workflow_steps)
                success = successful_steps == total_steps

                details = {
                    "total_steps": total_steps,
                    "successful_steps": successful_steps,
                    "success_rate": (
                        successful_steps / total_steps if total_steps > 0 else 0
                    ),
                    "step_results": dict(workflow_steps),
                    "duration_ms": self.performance_metrics.get(
                        "project_setup_workflow", 0
                    ),
                }

                self.log_test_result("project_setup_workflow", success, details)
                return success

        except Exception as e:
            self.log_test_result(
                "project_setup_workflow",
                False,
                {"error": str(e), "exception_type": type(e).__name__},
            )
            return False

    def test_ai_collaboration_workflow(self):
        """Test AI collaboration workflow with multiple agents."""
        try:
            with self.measure_performance("ai_collaboration_workflow"):
                collaboration_steps = []

                # Step 1: Set up multi-agent collaboration
                agent_profiles = [
                    {
                        "name": "Code Generator",
                        "capabilities": ["code_generation", "refactoring"],
                        "specializations": ["python", "testing"],
                    },
                    {
                        "name": "Project Manager",
                        "capabilities": ["planning", "coordination"],
                        "specializations": [
                            "workflow_optimization",
                            "quality_assurance",
                        ],
                    },
                ]

                agents_created = []
                for profile_data in agent_profiles:
                    profile = self.cursor_integration.create_agent_profile(
                        self.test_user_id, profile_data
                    )
                    agents_created.append(profile is not None)

                collaboration_steps.append(("agent_creation", all(agents_created)))

                # Step 2: Create collaborative session
                collab_session = self.cursor_integration.create_session(
                    user_id=self.test_user_id,
                    project_context={
                        "collaboration_mode": "multi_agent",
                        "agents": len(agent_profiles),
                        "task": "comprehensive_testing",
                    },
                )
                collaboration_steps.append(
                    ("collaborative_session", collab_session is not None)
                )

                # Step 3: Test context sharing between agents
                shared_context = self.context_manager.create_shared_context(
                    ["agent_1", "agent_2"],
                    {
                        "shared_goals": ["testing_validation", "workflow_optimization"],
                        "coordination_rules": [
                            "no_conflicting_actions",
                            "progress_updates",
                        ],
                    },
                )
                collaboration_steps.append(
                    ("context_sharing", shared_context is not None)
                )

                # Step 4: Coordinate decisions
                coordination_decision = self.decision_pipeline.process_decision(
                    "collaboration_coordination",
                    self.test_user_id,
                    "How should multiple agents coordinate for testing validation?",
                    {
                        "agent_count": len(agent_profiles),
                        "task_complexity": "high",
                        "coordination_mode": "structured",
                    },
                )
                collaboration_steps.append(
                    (
                        "decision_coordination",
                        coordination_decision is not None
                        and coordination_decision.get("success", False),
                    )
                )

                # Evaluate collaboration workflow
                successful_steps = sum(
                    1 for _, success in collaboration_steps if success
                )
                total_steps = len(collaboration_steps)
                success = successful_steps == total_steps

                details = {
                    "total_steps": total_steps,
                    "successful_steps": successful_steps,
                    "success_rate": (
                        successful_steps / total_steps if total_steps > 0 else 0
                    ),
                    "step_results": dict(collaboration_steps),
                    "agents_created": sum(agents_created),
                    "duration_ms": self.performance_metrics.get(
                        "ai_collaboration_workflow", 0
                    ),
                }

                self.log_test_result("ai_collaboration_workflow", success, details)
                return success

        except Exception as e:
            self.log_test_result(
                "ai_collaboration_workflow",
                False,
                {"error": str(e), "exception_type": type(e).__name__},
            )
            return False


def run_comprehensive_cursor_testing(root: Path) -> Dict[str, Any]:
    """Run comprehensive Cursor workflow testing."""
    print("🧪 Starting Comprehensive Cursor Integration Testing (T16)")
    print("=" * 60)

    tester = CursorWorkflowTester(root)

    # Test suites to run
    test_suites = [
        ("Basic Integration", TestCursorIntegrationBasics(root)),
        ("Context Management", TestContextManagement(root)),
        ("Decision Pipeline", TestDecisionPipeline(root)),
        ("UX Enhancements", TestUXEnhancements(root)),
        ("End-to-End Workflows", TestEndToEndWorkflows(root)),
    ]

    suite_results = {}
    overall_success = True

    for suite_name, test_suite in test_suites:
        print(f"\n🔍 Running {suite_name} Tests")
        print("-" * 40)

        # Run all test methods in the suite
        test_methods = [
            method
            for method in dir(test_suite)
            if method.startswith("test_") and callable(getattr(test_suite, method))
        ]

        suite_passed = 0
        suite_total = len(test_methods)

        for test_method_name in test_methods:
            test_method = getattr(test_suite, test_method_name)
            try:
                result = test_method()
                if result:
                    suite_passed += 1
            except Exception as e:
                test_suite.log_test_result(
                    test_method_name,
                    False,
                    {"error": str(e), "exception_type": type(e).__name__},
                )

        suite_success = suite_passed == suite_total
        suite_results[suite_name] = {
            "passed": suite_passed,
            "total": suite_total,
            "success_rate": suite_passed / suite_total if suite_total > 0 else 0,
            "success": suite_success,
        }

        overall_success = overall_success and suite_success

        status = "✅ PASS" if suite_success else "❌ FAIL"
        print(f"{status}: {suite_name} ({suite_passed}/{suite_total} tests passed)")

    # Generate comprehensive test report
    test_report = {
        "overall_success": overall_success,
        "test_suites": suite_results,
        "total_tests": sum(r["total"] for r in suite_results.values()),
        "total_passed": sum(r["passed"] for r in suite_results.values()),
        "overall_success_rate": (
            sum(r["passed"] for r in suite_results.values())
            / sum(r["total"] for r in suite_results.values())
            if sum(r["total"] for r in suite_results.values()) > 0
            else 0
        ),
        "performance_metrics": tester.performance_metrics,
        "detailed_results": tester.test_results,
        "timestamp": datetime.now().isoformat(),
    }

    print(f"\n📊 Test Summary")
    print("=" * 40)
    print(f"Overall Success: {'✅ PASS' if overall_success else '❌ FAIL'}")
    print(f"Tests Passed: {test_report['total_passed']}/{test_report['total_tests']}")
    print(f"Success Rate: {test_report['overall_success_rate']:.1%}")

    # Save test report
    report_file = root / ".ai_onboard" / "cursor_test_report.json"
    with open(report_file, "w") as f:
        json.dump(test_report, f, indent=2)

    print(f"\n📄 Detailed test report saved to: {report_file}")

    return test_report


if __name__ == "__main__":
    # Run the comprehensive test suite
    root = Path.cwd()
    results = run_comprehensive_cursor_testing(root)

    # Exit with appropriate code
    exit(0 if results["overall_success"] else 1)
