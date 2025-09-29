#!/usr/bin/env python3
"""
Simple Performance Testing API Server

Provides mock endpoints for AI Onboard performance testing.
This server simulates the behavior of the real AI Onboard API
for load testing purposes.
"""

import json
import random
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict


class PerformanceAPIHandler(BaseHTTPRequestHandler):
    """Mock API handler for performance testing."""

    def __init__(self, *args, **kwargs):
        self.response_times = {
            "analyze": (0.1, 0.5),  # 100-500ms
            "organize": (0.05, 0.2),  # 50-200ms
            "duplicates": (0.2, 1.0),  # 200-1000ms
            "project-analysis": (0.5, 2.0),  # 500-2000ms
            "user-experience": (0.02, 0.1),  # 20-100ms
            "collaborate": (0.1, 0.8),  # 100-800ms
        }
        super().__init__(*args, **kwargs)

    def do_POST(self):
        """Handle POST requests."""
        try:
            # Parse request
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))

            # Determine operation type from URL
            path = self.path.strip("/")
            operation = path.split("/")[-1] if "/" in path else path

            # Simulate processing time
            if operation in self.response_times:
                min_time, max_time = self.response_times[operation]
                processing_time = random.uniform(min_time, max_time)
            else:
                processing_time = random.uniform(0.05, 0.2)  # Default

            time.sleep(processing_time)

            # Generate response
            response_data = self._generate_response(operation, data)

            # Send response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("X-Processing-Time", f"{processing_time:.3f}")
            self.end_headers()

            self.wfile.write(json.dumps(response_data).encode("utf-8"))

        except Exception as e:
            # Simulate occasional errors
            if random.random() < 0.02:  # 2% error rate
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                error_response = {"error": "Internal server error", "message": str(e)}
                self.wfile.write(json.dumps(error_response).encode("utf-8"))
            else:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                error_response = {"error": "Bad request", "message": str(e)}
                self.wfile.write(json.dumps(error_response).encode("utf-8"))

    def do_GET(self):
        """Handle GET requests."""
        try:
            path = self.path.strip("/")

            if path.startswith("api/projects/"):
                # Project status endpoint
                project_id = path.split("/")[-2]  # Extract project ID
                response_data = self._generate_project_status(project_id)
                processing_time = random.uniform(0.05, 0.3)
                time.sleep(processing_time)
            else:
                response_data = {"error": "Not found"}
                self.send_response(404)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def _generate_response(
        self, operation: str, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate appropriate response based on operation type."""

        if operation == "analyze":
            return {
                "status": "completed",
                "analysis": {
                    "complexity": random.uniform(5.0, 15.0),
                    "quality_score": random.uniform(60.0, 95.0),
                    "issues_found": random.randint(0, 10),
                    "recommendations": [
                        "Consider adding type hints",
                        "Review function complexity",
                        "Add more comprehensive tests",
                    ][: random.randint(0, 3)],
                },
                "user_id": request_data.get("user_id"),
                "timestamp": time.time(),
            }

        elif operation == "organize":
            return {
                "status": "completed",
                "organization": {
                    "score": random.uniform(70.0, 95.0),
                    "issues": [
                        "Missing __init__.py files",
                        "Inconsistent naming",
                        "Deep directory structure",
                    ][: random.randint(0, 3)],
                    "recommendations": [
                        "Create missing __init__.py files",
                        "Standardize naming conventions",
                        "Consider flattening directory structure",
                    ][: random.randint(0, 3)],
                },
                "user_id": request_data.get("user_id"),
                "timestamp": time.time(),
            }

        elif operation == "duplicates":
            return {
                "status": "completed",
                "duplicates": {
                    "exact_duplicates": random.randint(0, 5),
                    "near_duplicates": random.randint(0, 15),
                    "total_lines_duplicated": random.randint(0, 200),
                    "largest_duplicate_block": random.randint(5, 50),
                },
                "user_id": request_data.get("user_id"),
                "timestamp": time.time(),
            }

        elif operation == "project-analysis":
            return {
                "status": "completed",
                "project_metrics": {
                    "overall_health": random.uniform(60.0, 95.0),
                    "test_coverage": random.uniform(70.0, 95.0),
                    "technical_debt_ratio": random.uniform(0.1, 0.4),
                    "maintainability_index": random.uniform(50.0, 85.0),
                },
                "insights": [
                    "Good test coverage indicates reliable code",
                    "Some technical debt accumulation detected",
                    "Consider refactoring complex modules",
                ][: random.randint(1, 3)],
                "user_id": request_data.get("user_id"),
                "timestamp": time.time(),
            }

        elif operation == "user-experience":
            return {
                "status": "completed",
                "ux_metrics": {
                    "satisfaction_score": random.uniform(7.0, 9.5),
                    "learning_progress": random.uniform(0.1, 0.8),
                    "command_success_rate": random.uniform(85.0, 98.0),
                    "time_savings": random.uniform(10.0, 45.0),  # minutes saved
                },
                "personalized_suggestions": [
                    "Try using 'analyze --deep' for comprehensive analysis",
                    "Consider 'organize --auto-fix' for automatic corrections",
                    "Use 'test --coverage' to check test effectiveness",
                ][: random.randint(0, 3)],
                "user_id": request_data.get("user_id"),
                "timestamp": time.time(),
            }

        elif operation == "collaborate":
            return {
                "status": "completed",
                "collaboration": {
                    "team_members": len(request_data.get("members", [])),
                    "tasks_completed": random.randint(
                        1, len(request_data.get("shared_tasks", []))
                    ),
                    "knowledge_shared": random.randint(2, 8),
                    "conflicts_resolved": random.randint(0, 3),
                },
                "team_insights": [
                    "Good collaboration patterns detected",
                    "Consider regular code reviews",
                    "Team learning opportunities identified",
                ][: random.randint(0, 3)],
                "team_id": request_data.get("team_id"),
                "timestamp": time.time(),
            }

        else:
            return {
                "status": "completed",
                "message": f"Operation '{operation}' completed successfully",
                "user_id": request_data.get("user_id"),
                "timestamp": time.time(),
            }

    def _generate_project_status(self, project_id: str) -> Dict[str, Any]:
        """Generate mock project status data."""
        return {
            "project_id": project_id,
            "status": "active",
            "metrics": {
                "quality_score": random.uniform(75.0, 95.0),
                "test_coverage": random.uniform(80.0, 98.0),
                "complexity_score": random.uniform(5.0, 12.0),
                "velocity": random.uniform(15.0, 35.0),  # story points per week
                "technical_debt": random.uniform(10.0, 40.0),  # hours
            },
            "last_updated": time.time(),
            "active_users": random.randint(2, 8),
            "open_tasks": random.randint(5, 25),
        }

    def log_message(self, format, *args):
        """Override to reduce log noise during performance testing."""
        # Only log errors, not every request
        if "error" in format.lower() or "exception" in format.lower():
            super().log_message(format, *args)


def run_server(host: str = "localhost", port: int = 8080):
    """Run the performance testing API server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, PerformanceAPIHandler)

    print(f"🚀 Performance Testing API Server running on http://{host}:{port}")
    print("📊 Ready to handle load testing requests...")
    print("Press Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Performance Testing API Server")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8080, help="Server port")

    args = parser.parse_args()
    run_server(args.host, args.port)
