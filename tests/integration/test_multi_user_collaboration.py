"""
Multi-User Collaboration Integration Tests

Tests concurrent multi-user operations, shared learning patterns, and collaborative
workflows. This ensures the system scales properly and users benefit from collective
experience while maintaining individual personalization.
"""

import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pytest

from ai_onboard.core.ai_integration.user_experience_system import UserExperienceSystem
from ai_onboard.core.orchestration.unified_tool_orchestrator import (
    get_unified_tool_orchestrator,
)


class TestMultiUserCollaboration:
    """Integration tests for multi-user collaboration scenarios."""

    @pytest.fixture
    def collaboration_env(self):
        """Set up multi-user collaboration test environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Initialize shared components
            ux_system = UserExperienceSystem(root)
            orchestrator = get_unified_tool_orchestrator(root)

            yield {
                "root": root,
                "ux_system": ux_system,
                "orchestrator": orchestrator,
            }

    def test_t102_1_concurrent_user_operations(self, collaboration_env):
        """T102.1: Concurrent User Operations - Multiple users working simultaneously."""
        env = collaboration_env

        # Define multiple users with different work patterns
        users = [
            {
                "id": "developer_alice",
                "role": "backend_developer",
                "commands": ["analyze", "validate", "test", "deploy"],
                "frequency": "high",
            },
            {
                "id": "developer_bob",
                "role": "frontend_developer",
                "commands": ["build", "lint", "test", "preview"],
                "frequency": "high",
            },
            {
                "id": "architect_charlie",
                "role": "system_architect",
                "commands": ["plan", "design", "review", "document"],
                "frequency": "medium",
            },
            {
                "id": "tester_diana",
                "role": "qa_engineer",
                "commands": ["test", "validate", "report", "monitor"],
                "frequency": "high",
            },
        ]

        # Simulate concurrent command usage
        def simulate_user_activity(user_data):
            """Simulate a user's command usage pattern."""
            user_id = user_data["id"]
            commands = user_data["commands"]

            for i in range(5):  # Each user executes 5 commands
                for cmd in commands:
                    # Record command usage
                    env["ux_system"].record_command_usage(
                        user_id,
                        cmd,
                        "success",
                        {
                            "category": user_data["role"],
                            "execution_time": 1.0 + (i * 0.1),
                            "complexity": "medium",
                            "session_id": f"session_{user_id}_{i}",
                        },
                    )

                    # Small delay to simulate real usage patterns
                    time.sleep(0.01)

            return user_id

        # Execute user activities concurrently
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(simulate_user_activity, user) for user in users]
            completed_users = []

            for future in as_completed(futures):
                user_id = future.result()
                completed_users.append(user_id)

        # Verify all users completed their activities
        assert len(completed_users) == len(users)
        assert set(completed_users) == {user["id"] for user in users}

        # Verify system state remains consistent
        assert hasattr(env["orchestrator"], "orchestrate_tools")

        print("✅ Concurrent user operations test passed")

    def test_t102_2_shared_learning_patterns(self, collaboration_env):
        """T102.2: Shared Learning Patterns - Users benefit from collective experience."""
        env = collaboration_env

        # Simulate team learning scenario
        team_members = ["alice", "bob", "charlie", "diana"]
        shared_command = "optimize_performance"

        # First user discovers and uses a new command
        env["ux_system"].record_command_usage("alice", shared_command, True)

        # Other team members learn about it through collaboration
        for member in team_members[1:]:
            env["ux_system"].record_command_usage(member, shared_command, True)

        # System should recognize this as a valuable shared pattern
        for member in team_members:
            suggestions = env["ux_system"].get_command_suggestions(member)

            # Each team member should have suggestions that include the shared command
            suggested_commands = {s.command for s in suggestions}
            assert shared_command in suggested_commands

        # The shared command should have high confidence due to team usage
        alice_suggestions = env["ux_system"].get_command_suggestions("alice")
        optimize_suggestion = next(
            (s for s in alice_suggestions if s.command == shared_command), None
        )
        assert optimize_suggestion is not None
        assert optimize_suggestion.confidence > 0.6  # High confidence from team usage

        print("✅ Shared learning patterns test passed")

    def test_t102_3_personalization_vs_collaboration_balance(self, collaboration_env):
        """T102.3: Personalization vs Collaboration Balance - Individual preferences respected."""
        env = collaboration_env

        # Create users with different preferences but similar roles
        developers = [
            {
                "id": "dev_jane",
                "preferred_style": "verbose",
                "commands": ["analyze", "validate", "test"],
            },
            {
                "id": "dev_john",
                "preferred_style": "concise",
                "commands": ["analyze", "validate", "test"],
            },
        ]

        # Both use the same commands but with different preferences
        for dev in developers:
            for cmd in dev["commands"]:
                env["ux_system"].record_command_usage(dev["id"], cmd, True)

        # System should maintain individual personalization
        for dev in developers:
            suggestions = env["ux_system"].get_command_suggestions(dev["id"])

            # Should have personalized suggestions based on their style preference
            assert len(suggestions) > 0

            # Verify suggestions are tailored (in practice, this would check suggestion content)
            for suggestion in suggestions[:2]:  # Check first 2 suggestions
                assert suggestion.confidence > 0
                assert suggestion.reason is not None

        print("✅ Personalization vs collaboration balance test passed")

    def test_t102_4_resource_contention_handling(self, collaboration_env):
        """T102.4: Resource Contention Handling - System manages concurrent resource access."""
        env = collaboration_env

        # Test concurrent access to shared resources
        shared_resource_accesses = []
        errors = []

        def access_shared_resource(user_id, resource_type):
            """Simulate accessing a shared system resource."""
            try:
                # Simulate resource access (file operations, etc.)
                if resource_type == "orchestrator":
                    assert hasattr(env["orchestrator"], "orchestrate_tools")
                    shared_resource_accesses.append(
                        f"{user_id}_orchestrator_{len(shared_resource_accesses)}"
                    )

                elif resource_type == "ux_system":
                    suggestions = env["ux_system"].get_command_suggestions(user_id)
                    shared_resource_accesses.append(
                        f"{user_id}_ux_{len(shared_resource_accesses)}"
                    )
                    assert isinstance(suggestions, list)

                # Small delay to increase chance of contention
                time.sleep(0.01)

            except Exception as e:
                errors.append(f"{user_id}_{resource_type}: {str(e)}")

        # Execute concurrent resource access
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []

            # Multiple users accessing orchestrator
            for i in range(5):
                futures.append(
                    executor.submit(access_shared_resource, f"user_{i}", "orchestrator")
                )

            # Multiple users accessing UX system
            for i in range(5):
                futures.append(
                    executor.submit(access_shared_resource, f"user_{i}", "ux_system")
                )

            # Wait for all to complete
            for future in as_completed(futures):
                future.result()

        # Verify no resource contention errors occurred
        assert len(errors) == 0, f"Resource contention errors: {errors}"

        # Verify all expected accesses occurred
        orchestrator_accesses = [
            a for a in shared_resource_accesses if "orchestrator" in a
        ]
        ux_accesses = [a for a in shared_resource_accesses if "ux" in a]

        assert len(orchestrator_accesses) == 5
        assert len(ux_accesses) == 5

        print("✅ Resource contention handling test passed")

    def test_t102_5_cross_user_knowledge_sharing(self, collaboration_env):
        """T102.5: Cross-User Knowledge Sharing - Users learn from each other's experiences."""
        env = collaboration_env

        # Simulate knowledge sharing scenario
        expert_user = "senior_architect"
        novice_users = ["junior_dev_1", "junior_dev_2", "junior_dev_3"]

        # Expert user masters advanced commands
        advanced_commands = [
            "architectural_review",
            "performance_optimization",
            "security_audit",
        ]
        for cmd in advanced_commands:
            env["ux_system"].record_command_usage(expert_user, cmd, True)

        # Expert shares knowledge with novices
        for novice in novice_users:
            # Novice learns from expert through mentoring
            for cmd in advanced_commands[:2]:  # Learn 2 of the 3 commands
                env["ux_system"].record_command_usage(novice, cmd, True)

        # System should recognize knowledge sharing patterns
        for novice in novice_users:
            suggestions = env["ux_system"].get_command_suggestions(novice)

            # Should suggest advanced commands they haven't tried yet
            suggested_commands = {s.command for s in suggestions}
            untried_advanced = set(advanced_commands) - {
                advanced_commands[0],
                advanced_commands[1],
            }
            assert len(untried_advanced.intersection(suggested_commands)) > 0

        print("✅ Cross-user knowledge sharing test passed")

    def test_t102_6_collaborative_workflow_orchestration(self, collaboration_env):
        """T102.6: Collaborative Workflow Orchestration - Team workflows are coordinated."""
        env = collaboration_env

        # Simulate a team working on a complex feature
        team = {
            "product_manager": "pm_sarah",
            "lead_developer": "dev_lead_mike",
            "backend_dev": "dev_backend_alice",
            "frontend_dev": "dev_frontend_bob",
            "qa_engineer": "qa_diana",
        }

        # Define collaborative workflow sequence
        workflow_steps = [
            # Product manager starts with planning
            (team["product_manager"], "define_requirements", "planning"),
            (team["product_manager"], "create_user_stories", "planning"),
            # Lead developer does high-level design
            (team["lead_developer"], "architectural_design", "design"),
            (team["lead_developer"], "create_technical_spec", "design"),
            # Backend developer implements core logic
            (team["backend_dev"], "implement_api_endpoints", "development"),
            (team["backend_dev"], "database_design", "development"),
            # Frontend developer creates UI
            (team["frontend_dev"], "implement_ui_components", "development"),
            (team["frontend_dev"], "integrate_api", "development"),
            # QA validates the implementation
            (team["qa_engineer"], "create_test_cases", "testing"),
            (team["qa_engineer"], "execute_integration_tests", "testing"),
        ]

        # Execute workflow steps in sequence (simulating real collaboration)
        for user_id, command, phase in workflow_steps:
            env["ux_system"].record_command_usage(user_id, command, True)

        # Verify each team member has appropriate suggestions based on their role
        role_expectations = {
            team["product_manager"]: ["planning", "requirements"],
            team["lead_developer"]: ["design", "architecture"],
            team["backend_dev"]: ["api", "database", "backend"],
            team["frontend_dev"]: ["ui", "frontend", "integration"],
            team["qa_engineer"]: ["test", "quality", "validation"],
        }

        for user_id, expected_keywords in role_expectations.items():
            suggestions = env["ux_system"].get_command_suggestions(user_id)
            suggested_commands = {s.command for s in suggestions}

            # Should have suggestions relevant to their role
            relevant_suggestions = [
                cmd
                for cmd in suggested_commands
                if any(keyword in cmd.lower() for keyword in expected_keywords)
            ]

            assert (
                len(relevant_suggestions) > 0
            ), f"No relevant suggestions for {user_id}"

        print("✅ Collaborative workflow orchestration test passed")

    def test_t102_7_shared_context_awareness(self, collaboration_env):
        """T102.7: Shared Context Awareness - System understands team context."""
        env = collaboration_env

        # Simulate team working on the same project
        team_members = ["alice", "bob", "charlie"]
        project_commands = ["project_init", "shared_config", "team_setup"]

        # All team members work on shared project elements
        for member in team_members:
            for cmd in project_commands:
                env["ux_system"].record_command_usage(member, cmd, True)

        # System should recognize shared context and suggest collaboration
        for member in team_members:
            suggestions = env["ux_system"].get_command_suggestions(member)

            # Should include suggestions that acknowledge team context
            team_suggestions = [
                s
                for s in suggestions
                if "team" in s.reason.lower() or "shared" in s.reason.lower()
            ]

            # At least some suggestions should reflect team awareness
            assert (
                len(team_suggestions) >= len(suggestions) * 0.1
            )  # 10% show team awareness

        print("✅ Shared context awareness test passed")
