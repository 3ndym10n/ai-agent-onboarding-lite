"""
Performance Testing Configuration

Shared fixtures and configuration for performance tests.
"""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def performance_baseline():
    """Load or create performance baseline data."""
    baseline_file = Path(__file__).parent / "baseline.json"

    if baseline_file.exists():
        import json

        with open(baseline_file, "r") as f:
            return json.load(f)
    else:
        # Create initial baseline
        return {
            "code_quality_analysis": {"median": 100.0, "stddev": 10.0},
            "file_organization_analysis": {"median": 200.0, "stddev": 20.0},
            "duplicate_detection": {"median": 150.0, "stddev": 15.0},
            "user_experience_operations": {"median": 50.0, "stddev": 5.0},
            "orchestrator_coordination": {"median": 25.0, "stddev": 2.5},
            "timestamp": "2024-01-01T00:00:00Z",
        }


@pytest.fixture
def performance_workspace():
    """Create a temporary workspace for performance testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)

        # Create realistic project structure
        (workspace / "src").mkdir()
        (workspace / "tests").mkdir()
        (workspace / "docs").mkdir()

        # Create some basic files
        (workspace / "src" / "__init__.py").write_text('"""Main package."""\n')
        (workspace / "src" / "main.py").write_text('def main():\n    print("Hello")\n')
        (workspace / "tests" / "__init__.py").write_text("")
        (workspace / "README.md").write_text(
            "# Test Project\n\nPerformance testing project.\n"
        )

        yield workspace


def pytest_benchmark_update_machine_info(config, machine_info):
    """Add custom machine information for performance tracking."""
    machine_info.update(
        {
            "python_implementation": "CPython",
            "performance_test": True,
            "ai_onboard_version": "lite",
        }
    )


def pytest_benchmark_update_json(config, benchmarks, output_json):
    """Update benchmark JSON with additional metadata."""
    output_json["metadata"] = {
        "test_type": "performance_regression",
        "ai_onboard_system": True,
        "benchmark_version": "1.0",
    }


@pytest.fixture(autouse=True)
def performance_monitoring(request):
    """Monitor performance during tests."""
    import os
    import time

    import psutil

    start_time = time.time()
    process = psutil.Process(os.getpid())
    start_memory = process.memory_info().rss

    def finalize():
        end_time = time.time()
        end_memory = process.memory_info().rss

        duration = end_time - start_time
        memory_delta = end_memory - start_memory

        # Log performance metrics for monitoring
        if duration > 1.0:  # Only log for operations taking > 1 second
            print(f"Performance: {duration:.4f}s, Memory: {memory_delta:.2f}MB")

    request.addfinalizer(finalize)
