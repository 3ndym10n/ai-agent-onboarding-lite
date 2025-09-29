"""
Performance Regression Tests using pytest-benchmark

These tests ensure that code changes don't introduce performance regressions
by benchmarking critical operations and comparing against baseline performance.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ai_onboard.core.ai_integration.user_experience_system import UserExperienceSystem
from ai_onboard.core.monitoring_analytics.file_organization_analyzer import (
    FileOrganizationAnalyzer,
)
from ai_onboard.core.orchestration.unified_tool_orchestrator import (
    get_unified_tool_orchestrator,
)
from ai_onboard.core.quality_safety.code_quality_analyzer import CodeQualityAnalyzer
from ai_onboard.core.quality_safety.duplicate_detector import DuplicateDetector


class TestPerformanceRegression:
    """Performance regression tests for critical operations."""

    @pytest.fixture
    def perf_env(self):
        """Set up performance test environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Initialize components
            ux_system = UserExperienceSystem(root)
            orchestrator = get_unified_tool_orchestrator(root)
            quality_analyzer = CodeQualityAnalyzer(root)
            org_analyzer = FileOrganizationAnalyzer(root)
            duplicate_detector = DuplicateDetector(root)

            yield {
                "root": root,
                "ux_system": ux_system,
                "orchestrator": orchestrator,
                "quality_analyzer": quality_analyzer,
                "org_analyzer": org_analyzer,
                "duplicate_detector": duplicate_detector,
            }

    def test_code_quality_analysis_performance(self, benchmark, perf_env):
        """Benchmark code quality analysis performance."""
        # Create test Python file with realistic content
        test_file = perf_env["root"] / "test_module.py"
        test_content = '''
"""
Test module with realistic Python code for performance testing.
"""
import os
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path
import json


class DataProcessor:
    """Process data with various operations."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_cache = {}
        self.processed_count = 0

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate input data structure."""
        required_fields = ["id", "name", "value"]
        return all(field in data for field in required_fields)

    def process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single data item."""
        if not self.validate_data(item):
            raise ValueError("Invalid data structure")

        # Simulate processing logic
        processed = {
            "id": item["id"],
            "name": item["name"].upper(),
            "value": item["value"] * 1.1,  # 10% increase
            "processed_at": "2024-01-01T12:00:00Z",
            "status": "processed"
        }

        self.processed_count += 1
        self.data_cache[item["id"]] = processed

        return processed

    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            "total_processed": self.processed_count,
            "cache_size": len(self.data_cache),
            "average_value": sum(item["value"] for item in self.data_cache.values()) / max(1, len(self.data_cache))
        }


def batch_process_items(items: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process multiple items in batch."""
    processor = DataProcessor(config)
    results = []

    for item in items:
        try:
            result = processor.process_item(item)
            results.append(result)
        except ValueError as e:
            print(f"Skipping invalid item {item.get('id', 'unknown')}: {e}")
            continue

    return results


def main():
    """Main function for demonstration."""
    # Sample configuration
    config = {
        "batch_size": 100,
        "validate_inputs": True,
        "output_format": "json"
    }

    # Sample data
    sample_items = [
        {"id": "001", "name": "item1", "value": 100.0},
        {"id": "002", "name": "item2", "value": 200.0},
        {"id": "003", "name": "item3", "value": 150.0},
    ]

    # Process items
    results = batch_process_items(sample_items, config)

    # Print results
    print(f"Processed {len(results)} items successfully")
    print(json.dumps(results, indent=2))

    return results


if __name__ == "__main__":
    main()
'''
        test_file.write_text(test_content)

        def run_quality_analysis():
            """Function to benchmark."""
            result = perf_env["quality_analyzer"].analyze_codebase(perf_env["root"])
            return result

        # Benchmark the operation
        result = benchmark(run_quality_analysis)

        # Basic assertions to ensure it works
        assert result is not None
        assert len(result.file_metrics) > 0

    def test_file_organization_analysis_performance(self, benchmark, perf_env):
        """Benchmark file organization analysis performance."""
        # Create realistic file structure
        root = perf_env["root"]

        # Create directories
        (root / "src").mkdir()
        (root / "src" / "core").mkdir()
        (root / "src" / "utils").mkdir()
        (root / "tests").mkdir()
        (root / "tests" / "unit").mkdir()
        (root / "tests" / "integration").mkdir()
        (root / "docs").mkdir()
        (root / "scripts").mkdir()

        # Create Python files
        python_files = [
            "src/__init__.py",
            "src/main.py",
            "src/core/__init__.py",
            "src/core/processor.py",
            "src/core/validator.py",
            "src/utils/__init__.py",
            "src/utils/helpers.py",
            "src/utils/logging.py",
            "tests/__init__.py",
            "tests/unit/test_processor.py",
            "tests/unit/test_validator.py",
            "tests/integration/test_workflow.py",
            "scripts/setup.py",
            "scripts/deploy.py",
        ]

        for file_path in python_files:
            full_path = root / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(
                f'"""Module: {file_path}"""\n\ndef placeholder():\n    pass\n'
            )

        # Create documentation files
        docs = ["README.md", "API.md", "CONTRIBUTING.md", "CHANGELOG.md"]
        for doc in docs:
            (root / "docs" / doc).write_text(
                f"# {doc.replace('.md', '')}\n\nContent here.\n"
            )

        # Create config files
        config_files = ["pyproject.toml", "requirements.txt", ".gitignore"]
        for config in config_files:
            (root / config).write_text("# Configuration file\n")

        def run_org_analysis():
            """Function to benchmark."""
            result = perf_env["org_analyzer"].analyze_organization(perf_env["root"])
            return result

        # Benchmark the operation
        result = benchmark(run_org_analysis)

        # Basic assertions
        assert result is not None
        assert "organization_score" in result

    def test_duplicate_detection_performance(self, benchmark, perf_env):
        """Benchmark duplicate detection performance."""
        # Create test files with some duplicated code
        root = perf_env["root"]

        # Create files with duplicated functions
        duplicated_function = '''
def calculate_total(items):
    """Calculate total of numeric items."""
    total = 0
    for item in items:
        if isinstance(item, (int, float)):
            total += item
    return total
'''

        unique_function = '''
def calculate_average(items):
    """Calculate average of numeric items."""
    total = 0
    count = 0
    for item in items:
        if isinstance(item, (int, float)):
            total += item
            count += 1
    return total / count if count > 0 else 0
'''

        # Create multiple files with duplicated code
        for i in range(5):
            file_path = root / f"module_{i}.py"
            content = f'"""Module {i}"""\n\n{duplicated_function}\n\n{unique_function}\n\n# Unique code for module {i}\ndef module_{i}_specific():\n    return "module_{i}"\n'
            file_path.write_text(content)

        def run_duplicate_detection():
            """Function to benchmark."""
            result = perf_env["duplicate_detector"].analyze_duplicates(perf_env["root"])
            return result

        # Benchmark the operation
        result = benchmark(run_duplicate_detection)

        # Basic assertions
        assert result is not None
        assert hasattr(result, "exact_duplicates") or hasattr(result, "near_duplicates")

    def test_user_experience_operations_performance(self, benchmark, perf_env):
        """Benchmark user experience system operations."""
        # Simulate user interaction patterns
        user_commands = [
            ("analyze", True),
            ("validate", True),
            ("test", False),  # Failed command
            ("build", True),
            ("deploy", True),
            ("monitor", True),
            ("optimize", True),
            ("document", True),
        ]

        def run_ux_operations():
            """Function to benchmark multiple UX operations."""
            results = []
            for cmd, success in user_commands:
                perf_env["ux_system"].record_command_usage(
                    "perf_test_user", cmd, success
                )
                suggestions = perf_env["ux_system"].get_command_suggestions(
                    "perf_test_user"
                )
                results.append(len(suggestions))
            return results

        # Benchmark the operations
        result = benchmark(run_ux_operations)

        # Basic assertions
        assert isinstance(result, list)
        assert len(result) == len(user_commands)

    def test_orchestrator_coordination_performance(self, benchmark, perf_env):
        """Benchmark orchestrator coordination performance."""
        # Create mock tool execution context
        from ai_onboard.core.orchestration.unified_tool_orchestrator import (
            ToolExecutionContext,
        )

        context = ToolExecutionContext(
            user_request="analyze code quality and check for duplicates",
            user_id="perf_test_user",
            conversation_history=[],
            session_id="perf_session_123",
            action_type="analysis",
        )

        def run_orchestration():
            """Function to benchmark orchestrator operations."""
            # Mock the actual tool execution to avoid external dependencies
            with perf_env["orchestrator"]._analyzer_cache_lock:
                perf_env["orchestrator"]._analyzer_cache.clear()

            # Test orchestrator initialization and basic coordination
            status = perf_env["orchestrator"].get_orchestrator_status()
            return status

        # Benchmark the operation
        result = benchmark(run_orchestration)

        # Basic assertions
        assert isinstance(result, dict)
        assert "initialized" in result

    def test_memory_usage_stability(self, benchmark, perf_env):
        """Test memory usage stability under repeated operations."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        def run_memory_test():
            """Function to benchmark memory usage."""
            # Perform multiple operations
            for i in range(10):
                perf_env["ux_system"].record_command_usage(
                    f"user_{i}", f"cmd_{i}", True
                )
                suggestions = perf_env["ux_system"].get_command_suggestions(f"user_{i}")

            # Check memory usage
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - initial_memory

            return {
                "initial_memory": initial_memory,
                "current_memory": current_memory,
                "memory_increase": memory_increase,
            }

        # Benchmark memory usage
        result = benchmark(run_memory_test)

        # Memory should not grow excessively
        assert (
            result["memory_increase"] < 50
        )  # Less than 50MB increase for 10 operations
        assert result["current_memory"] > 0
