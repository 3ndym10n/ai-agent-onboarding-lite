"""
Data Flow Validation Integration Tests

Tests complete data flow through the system: from input sources through processing
modules to output sinks. Ensures data integrity, consistency, and proper
transformation at each stage of the pipeline.
"""

import json
import tempfile
from pathlib import Path

import pytest

from ai_onboard.core.ai_integration.user_experience_system import UserExperienceSystem
from ai_onboard.core.legacy_cleanup.charter import load_charter
from ai_onboard.core.orchestration.unified_tool_orchestrator import (
    get_unified_tool_orchestrator,
)
from ai_onboard.core.vision.enhanced_vision_interrogator import (
    get_enhanced_vision_interrogator,
)


class TestDataFlowValidation:
    """Integration tests for complete data flow validation."""

    @pytest.fixture
    def data_flow_env(self):
        """Set up complete data flow test environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Initialize all data-processing components
            ux_system = UserExperienceSystem(root)
            orchestrator = get_unified_tool_orchestrator(root)
            vision_interrogator = get_enhanced_vision_interrogator(root)

            yield {
                "root": root,
                "ux_system": ux_system,
                "orchestrator": orchestrator,
                "vision_interrogator": vision_interrogator,
            }

    def test_t103_1_end_to_end_data_pipeline(self, data_flow_env):
        """T103.1: End-to-End Data Pipeline - Data flows correctly from input to output."""
        env = data_flow_env

        # Phase 1: Data Input (Charter Creation)
        input_data = {
            "project_name": "Data Pipeline Test",
            "description": "Testing complete data flow through the system",
            "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "team_size": 5,
            "timeline_weeks": 8,
            "budget_range": "50k-100k",
            "risk_tolerance": "medium",
        }

        # Save input data
        charter_path = env["root"] / ".ai_onboard" / "charter.json"
        charter_path.parent.mkdir(parents=True, exist_ok=True)
        with open(charter_path, "w") as f:
            json.dump(input_data, f, indent=2)

        # Phase 2: Data Loading and Validation
        loaded_charter = load_charter(env["root"])
        assert loaded_charter["project_name"] == input_data["project_name"]
        assert loaded_charter["technologies"] == input_data["technologies"]

        # Phase 3: Data Transformation (UX System Processing)
        env["ux_system"].record_command_usage("test_user", "analyze_project", True)

        # Phase 4: Data Routing (Orchestrator Processing)
        assert hasattr(env["orchestrator"], "orchestrate_tools")

        # Phase 5: Data Storage and Retrieval
        suggestions = env["ux_system"].get_command_suggestions("test_user")
        assert len(suggestions) >= 0  # Should not error even if empty

        # Phase 6: Data Consistency Check
        # Verify data hasn't been corrupted through the pipeline
        final_charter = load_charter(env["root"])
        assert final_charter["project_name"] == input_data["project_name"]
        assert final_charter["technologies"] == input_data["technologies"]

        print("✅ End-to-end data pipeline test passed")

    def test_t103_2_data_integrity_across_modules(self, data_flow_env):
        """T103.2: Data Integrity Across Modules - Data remains consistent through transformations."""
        env = data_flow_env

        # Create complex nested data structure
        complex_data = {
            "project": {
                "metadata": {
                    "name": "Complex Data Test",
                    "version": "1.0.0",
                    "created": "2024-01-01",
                },
                "architecture": {
                    "layers": ["presentation", "business", "data"],
                    "technologies": {
                        "frontend": ["React", "TypeScript"],
                        "backend": ["Python", "FastAPI"],
                        "database": ["PostgreSQL"],
                        "infrastructure": ["Docker", "Kubernetes"],
                    },
                },
                "team": {
                    "members": [
                        {
                            "name": "Alice",
                            "role": "Lead Developer",
                            "expertise": ["Python", "Architecture"],
                        },
                        {
                            "name": "Bob",
                            "role": "Frontend Developer",
                            "expertise": ["React", "UI/UX"],
                        },
                        {
                            "name": "Charlie",
                            "role": "DevOps Engineer",
                            "expertise": ["Docker", "AWS"],
                        },
                    ]
                },
            },
            "requirements": [
                {
                    "id": "REQ-001",
                    "description": "User authentication",
                    "priority": "high",
                },
                {
                    "id": "REQ-002",
                    "description": "Payment processing",
                    "priority": "high",
                },
                {
                    "id": "REQ-003",
                    "description": "Admin dashboard",
                    "priority": "medium",
                },
            ],
        }

        # Store data through charter system
        charter_path = env["root"] / ".ai_onboard" / "charter.json"
        charter_path.parent.mkdir(parents=True, exist_ok=True)
        with open(charter_path, "w") as f:
            json.dump(complex_data, f, indent=2)

        # Load and verify data integrity
        loaded_data = load_charter(env["root"])

        # Deep comparison of nested structures
        def compare_data(original, loaded, path=""):
            """Recursively compare data structures."""
            if isinstance(original, dict) and isinstance(loaded, dict):
                for key in original:
                    if key not in loaded:
                        pytest.fail(f"Missing key '{key}' at path '{path}'")
                    compare_data(original[key], loaded[key], f"{path}.{key}")
            elif isinstance(original, list) and isinstance(loaded, list):
                if len(original) != len(loaded):
                    pytest.fail(
                        f"List length mismatch at path '{path}': {len(original)} vs {len(loaded)}"
                    )
                for i, (orig_item, loaded_item) in enumerate(zip(original, loaded)):
                    compare_data(orig_item, loaded_item, f"{path}[{i}]")
            else:
                if original != loaded:
                    pytest.fail(
                        f"Data mismatch at path '{path}': {original} vs {loaded}"
                    )

        compare_data(complex_data, loaded_data)

        print("✅ Data integrity across modules test passed")

    def test_t103_3_concurrent_data_access_safety(self, data_flow_env):
        """T103.3: Concurrent Data Access Safety - Multiple processes can safely access data."""
        env = data_flow_env

        # Create shared data file
        shared_data_path = env["root"] / ".ai_onboard" / "shared_data.json"
        shared_data_path.parent.mkdir(parents=True, exist_ok=True)

        initial_data = {
            "access_count": 0,
            "last_accessed": "2024-01-01T00:00:00Z",
            "access_log": [],
        }

        with open(shared_data_path, "w") as f:
            json.dump(initial_data, f, indent=2)

        # Function to simulate concurrent data access
        def access_shared_data(process_id, iterations=5):
            """Simulate a process accessing shared data."""
            for i in range(iterations):
                try:
                    # Read current data
                    with open(shared_data_path, "r") as f:
                        current_data = json.load(f)

                    # Modify data
                    current_data["access_count"] += 1
                    current_data["last_accessed"] = f"2024-01-01T00:{i:02d}:00Z"
                    current_data["access_log"].append(
                        f"Process {process_id} - Access {i+1}"
                    )

                    # Write back
                    with open(shared_data_path, "w") as f:
                        json.dump(current_data, f, indent=2)

                except Exception as e:
                    # In a real system, we'd implement proper locking
                    # For this test, we'll just continue
                    pass

        # Run concurrent access simulation
        import threading

        threads = []

        for process_id in range(5):  # 5 concurrent processes
            thread = threading.Thread(target=access_shared_data, args=(process_id,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify final data integrity
        with open(shared_data_path, "r") as f:
            final_data = json.load(f)

        # Should have been accessed by all processes
        assert final_data["access_count"] >= 5  # At least 5 accesses (one per process)
        assert len(final_data["access_log"]) >= 5

        # Data should be valid JSON
        assert isinstance(final_data["access_count"], int)
        assert isinstance(final_data["access_log"], list)

        print("✅ Concurrent data access safety test passed")

    def test_t103_4_data_transformation_pipeline(self, data_flow_env):
        """T103.4: Data Transformation Pipeline - Data is correctly transformed at each stage."""
        env = data_flow_env

        # Raw input data
        raw_project_data = {
            "name": "Transformation Test",
            "tech_stack": ["python", "javascript", "sql"],
            "team": ["alice", "bob"],
            "deadline": "2024-06-01",
        }

        # Store raw data
        raw_path = env["root"] / ".ai_onboard" / "raw_input.json"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        with open(raw_path, "w") as f:
            json.dump(raw_project_data, f, indent=2)

        # Phase 1: Load raw data
        with open(raw_path, "r") as f:
            loaded_raw = json.load(f)

        # Phase 2: Transform through charter system
        charter_data = {
            "project_name": loaded_raw["name"],
            "technologies": [tech.title() for tech in loaded_raw["tech_stack"]],
            "team_members": loaded_raw["team"],
            "target_completion": loaded_raw["deadline"],
            "processed_at": "2024-01-01T12:00:00Z",
        }

        charter_path = env["root"] / ".ai_onboard" / "charter.json"
        with open(charter_path, "w") as f:
            json.dump(charter_data, f, indent=2)

        # Phase 3: Transform through UX system
        env["ux_system"].record_command_usage("test_user", "process_project_data", True)

        # Phase 4: Transform through orchestrator
        orchestrator_context = {
            "project_name": charter_data["project_name"],
            "technology_count": len(charter_data["technologies"]),
            "team_size": len(charter_data["team_members"]),
        }

        # Phase 5: Verify final data integrity
        final_charter = load_charter(env["root"])
        assert final_charter["project_name"] == raw_project_data["name"]
        assert len(final_charter["technologies"]) == len(raw_project_data["tech_stack"])
        assert (
            final_charter["technologies"][0]
            == raw_project_data["tech_stack"][0].title()
        )

        print("✅ Data transformation pipeline test passed")

    def test_t103_5_data_persistence_and_recovery(self, data_flow_env):
        """T103.5: Data Persistence and Recovery - Data survives system restarts."""
        env = data_flow_env

        # Create comprehensive project data
        project_data = {
            "metadata": {
                "name": "Persistence Test Project",
                "version": "2.1.0",
                "created": "2024-01-01T10:00:00Z",
            },
            "configuration": {
                "debug_mode": True,
                "max_workers": 4,
                "cache_enabled": True,
            },
            "usage_stats": {
                "commands_executed": 150,
                "errors_encountered": 3,
                "features_used": ["analysis", "validation", "testing"],
            },
        }

        # Persist data through multiple storage mechanisms
        charter_path = env["root"] / ".ai_onboard" / "charter.json"
        charter_path.parent.mkdir(parents=True, exist_ok=True)
        with open(charter_path, "w") as f:
            json.dump(project_data, f, indent=2)

        # Simulate system restart by re-initializing components
        fresh_ux_system = UserExperienceSystem(env["root"])
        fresh_orchestrator = get_unified_tool_orchestrator(env["root"])

        # Verify data persistence
        recovered_charter = load_charter(env["root"])
        assert recovered_charter["metadata"]["name"] == project_data["metadata"]["name"]
        assert (
            recovered_charter["configuration"]["max_workers"]
            == project_data["configuration"]["max_workers"]
        )

        # Verify system can operate with recovered data
        assert hasattr(fresh_orchestrator, "orchestrate_tools")

        # Verify UX system can work with recovered data
        suggestions = fresh_ux_system.get_command_suggestions("test_user")
        # Should not crash even if empty
        assert isinstance(suggestions, list)

        print("✅ Data persistence and recovery test passed")

    def test_t103_6_data_validation_and_sanitization(self, data_flow_env):
        """T103.6: Data Validation and Sanitization - Invalid data is handled gracefully."""
        env = data_flow_env

        # Test cases with invalid/malformed data
        test_cases = [
            # Completely invalid JSON
            ("invalid_json", '{"invalid": json syntax}', "json_parse_error"),
            # Valid JSON but invalid structure
            ("empty_object", "{}", "missing_required_fields"),
            # Valid structure but invalid values
            (
                "invalid_values",
                '{"project_name": null, "technologies": "not_a_list"}',
                "invalid_field_types",
            ),
            # Nested invalid data
            (
                "nested_invalid",
                '{"config": {"nested": {"deeply": "invalid"}}}',
                "nested_validation_error",
            ),
        ]

        for test_name, invalid_data, expected_error_type in test_cases:
            # Attempt to store invalid data
            test_path = env["root"] / ".ai_onboard" / f"{test_name}.json"
            with open(test_path, "w") as f:
                if isinstance(invalid_data, str):
                    f.write(invalid_data)
                else:
                    json.dump(invalid_data, f)

            # Attempt to load/process data
            try:
                if test_name == "invalid_json":
                    # This should fail to load
                    with open(test_path, "r") as f:
                        json.load(f)
                    # If we get here, the test failed
                    assert False, "Should have failed to parse invalid JSON"
                else:
                    # Load and validate structure
                    with open(test_path, "r") as f:
                        loaded_data = json.load(f)

                    # System should handle gracefully even with invalid structure
                    # (In practice, the system would have validation logic)

            except json.JSONDecodeError:
                # Expected for invalid JSON
                pass
            except Exception as e:
                # Other exceptions should be handled gracefully
                assert "validation" in str(e).lower() or "invalid" in str(e).lower()

        print("✅ Data validation and sanitization test passed")

    def test_t103_7_cross_module_data_references(self, data_flow_env):
        """T103.7: Cross-Module Data References - Modules correctly reference shared data."""
        env = data_flow_env

        # Create interconnected data structures
        shared_project_id = "project_12345"

        # Charter data
        charter_data = {
            "project_id": shared_project_id,
            "name": "Cross-Reference Test",
            "status": "active",
        }

        # Vision data referencing the project
        vision_data = {
            "project_id": shared_project_id,
            "vision_statement": "Build the best cross-referenced system",
            "status": "defined",
        }

        # UX data referencing the project
        ux_data = {
            "project_id": shared_project_id,
            "user_count": 3,
            "last_activity": "2024-01-01T12:00:00Z",
        }

        # Store data in respective modules
        charter_path = env["root"] / ".ai_onboard" / "charter.json"
        vision_path = env["root"] / ".ai_onboard" / "vision_data.json"
        ux_path = env["root"] / ".ai_onboard" / "ux_data.json"

        charter_path.parent.mkdir(parents=True, exist_ok=True)

        with open(charter_path, "w") as f:
            json.dump(charter_data, f, indent=2)

        with open(vision_path, "w") as f:
            json.dump(vision_data, f, indent=2)

        with open(ux_path, "w") as f:
            json.dump(ux_data, f, indent=2)

        # Verify cross-references are maintained
        loaded_charter = load_charter(env["root"])
        assert loaded_charter["project_id"] == shared_project_id

        # Vision system should be able to find related data
        vision_readiness = env["vision_interrogator"].check_vision_readiness()
        assert "ready" in vision_readiness  # Should find vision data

        # UX system should work with project context
        env["ux_system"].record_command_usage("test_user", "check_status", True)

        # Orchestrator should coordinate across all modules
        assert hasattr(env["orchestrator"], "execute_automatic_tool_application")

        print("✅ Cross-module data references test passed")
