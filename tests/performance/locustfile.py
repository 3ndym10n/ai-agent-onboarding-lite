"""
Performance Load Testing for AI Onboard System

Uses Locust to simulate multiple users performing various AI onboard operations
to test system performance under load and identify bottlenecks.
"""

import json
import time
from pathlib import Path

from locust import between, events, task
from locust.contrib.fasthttp import FastHttpUser


class AIAgentUser(FastHttpUser):
    """Simulates AI agent users performing onboarding operations."""

    wait_time = between(1, 3)  # Random wait between 1-3 seconds

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_root = Path(__file__).parent.parent.parent
        self.session_data = {}

    def on_start(self):
        """Initialize user session."""
        self.session_data = {
            "user_id": f"perf_user_{self.__class__.__name__}_{time.time()}",
            "session_start": time.time(),
            "operations_completed": 0,
        }

    @task(3)  # 30% of operations
    def code_quality_analysis(self):
        """Simulate code quality analysis operations."""
        # Simulate analyzing a Python file
        test_file_content = '''
def example_function():
    """Example function for performance testing."""
    data = [1, 2, 3, 4, 5]
    result = sum(data)
    return result

class ExampleClass:
    def __init__(self):
        self.value = 42

    def get_value(self):
        return self.value
'''

        payload = {
            "files": {"test_module.py": test_file_content},
            "user_id": self.session_data["user_id"],
            "analysis_type": "quality",
        }

        with self.client.post(
            "/api/analyze", json=payload, catch_response=True
        ) as response:
            if response.status_code == 200:
                self.session_data["operations_completed"] += 1
                response.success()
            else:
                response.failure(f"Analysis failed: {response.status_code}")

    @task(2)  # 20% of operations
    def file_organization_check(self):
        """Simulate file organization analysis."""
        payload = {
            "file_structure": {
                "src/": ["main.py", "utils.py", "config.py"],
                "tests/": ["test_main.py", "test_utils.py"],
                "docs/": ["README.md", "API.md"],
            },
            "user_id": self.session_data["user_id"],
        }

        with self.client.post(
            "/api/organize", json=payload, catch_response=True
        ) as response:
            if response.status_code == 200:
                self.session_data["operations_completed"] += 1
                response.success()
            else:
                response.failure(f"Organization check failed: {response.status_code}")

    @task(2)  # 20% of operations
    def duplicate_detection(self):
        """Simulate duplicate code detection."""
        code_blocks = [
            "def calculate_total(items):\n    return sum(items)",
            "def compute_sum(values):\n    return sum(values)",
            "def get_total(data):\n    total = 0\n    for item in data:\n        total += item\n    return total",
        ]

        payload = {
            "code_blocks": code_blocks,
            "user_id": self.session_data["user_id"],
            "min_block_size": 3,
        }

        with self.client.post(
            "/api/duplicates", json=payload, catch_response=True
        ) as response:
            if response.status_code == 200:
                self.session_data["operations_completed"] += 1
                response.success()
            else:
                response.failure(f"Duplicate detection failed: {response.status_code}")

    @task(1)  # 10% of operations
    def comprehensive_project_analysis(self):
        """Simulate full project analysis (most expensive operation)."""
        project_structure = {
            "python_files": 25,
            "total_lines": 2500,
            "complexity_score": 45.2,
            "test_coverage": 78.5,
            "dependencies": ["fastapi", "pydantic", "sqlalchemy", "pytest"],
        }

        payload = {
            "project_data": project_structure,
            "user_id": self.session_data["user_id"],
            "analysis_depth": "comprehensive",
            "include_recommendations": True,
        }

        with self.client.post(
            "/api/project-analysis", json=payload, catch_response=True
        ) as response:
            if response.status_code == 200:
                self.session_data["operations_completed"] += 1
                response.success()
            else:
                response.failure(f"Project analysis failed: {response.status_code}")

    @task(1)  # 10% of operations
    def user_experience_simulation(self):
        """Simulate user experience interactions."""
        interactions = [
            {"type": "command", "command": "analyze", "success": True},
            {"type": "command", "command": "validate", "success": True},
            {"type": "command", "command": "test", "success": False},
            {"type": "suggestion", "accepted": True},
            {"type": "help", "topic": "testing"},
        ]

        payload = {
            "user_id": self.session_data["user_id"],
            "interactions": interactions,
            "session_duration": time.time() - self.session_data["session_start"],
        }

        with self.client.post(
            "/api/user-experience", json=payload, catch_response=True
        ) as response:
            if response.status_code == 200:
                self.session_data["operations_completed"] += 1
                response.success()
            else:
                response.failure(f"UX simulation failed: {response.status_code}")

    @task(1)  # 10% of operations
    def concurrent_collaboration(self):
        """Simulate collaborative operations."""
        team_members = ["alice", "bob", "charlie", "diana"]
        shared_tasks = [
            "code_review",
            "merge_conflict_resolution",
            "pair_programming_session",
            "knowledge_sharing",
        ]

        payload = {
            "team_id": f"team_{self.session_data['user_id']}",
            "members": team_members,
            "shared_tasks": shared_tasks,
            "collaboration_type": "async",
        }

        with self.client.post(
            "/api/collaborate", json=payload, catch_response=True
        ) as response:
            if response.status_code == 200:
                self.session_data["operations_completed"] += 1
                response.success()
            else:
                response.failure(f"Collaboration failed: {response.status_code}")


class ProjectManagerUser(FastHttpUser):
    """Simulates project manager users coordinating multiple analyses."""

    wait_time = between(2, 5)  # Project managers work more deliberately

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = f"perf_project_{time.time()}"

    @task(5)  # 50% of operations
    def project_status_dashboard(self):
        """Check comprehensive project status."""
        payload = {
            "project_id": self.project_id,
            "metrics": ["quality", "coverage", "complexity", "velocity"],
            "time_range": "last_30_days",
        }

        with self.client.get(
            f"/api/projects/{self.project_id}/status", json=payload, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status dashboard failed: {response.status_code}")

    @task(3)  # 30% of operations
    def generate_reports(self):
        """Generate comprehensive project reports."""
        payload = {
            "project_id": self.project_id,
            "report_types": ["quality", "performance", "team_velocity"],
            "format": "json",
            "include_charts": True,
        }

        with self.client.post(
            f"/api/projects/{self.project_id}/reports",
            json=payload,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Report generation failed: {response.status_code}")

    @task(2)  # 20% of operations
    def coordination_operations(self):
        """Simulate project coordination tasks."""
        payload = {
            "project_id": self.project_id,
            "actions": [
                {"type": "schedule_review", "assignee": "alice"},
                {"type": "update_milestones", "milestone": "Q1_delivery"},
                {"type": "resource_allocation", "team": "backend"},
            ],
        }

        with self.client.post(
            f"/api/projects/{self.project_id}/coordinate",
            json=payload,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Coordination failed: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Initialize test environment."""
    print("🚀 Starting AI Onboard Performance Test")
    print(f"Target: {environment.host}")
    print(f"Users: {environment.parsed_options.num_users}")
    print(f"Spawn rate: {environment.parsed_options.spawn_rate}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Clean up after test completion."""
    print("✅ AI Onboard Performance Test Completed")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Average response time: {environment.stats.total.avg_response_time:.2f}ms")
    print(f"Requests per second: {environment.stats.total.total_rps:.2f}")


@events.request.add_listener
def on_request(
    request_type,
    name,
    response_time,
    response_length,
    response,
    context,
    exception,
    start_time,
    url,
    **kwargs,
):
    """Log performance metrics for analysis."""
    if exception:
        print(f"❌ Request failed: {name} - {exception}")
    elif response_time > 5000:  # Log slow requests (>5 seconds)
        print(f"🐌 Slow request: {name} - {response_time}ms")
