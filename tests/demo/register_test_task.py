#!/usr/bin/env python3
"""Register a test task to demonstrate the WBS auto-update system."""

from ai_onboard.core.task_execution_gate import register_task_for_execution

# Register a test task to demonstrate the system
task_data = {
    "name": "Implement Advanced Logging System",
    "description": (
        "Create a comprehensive logging system with structured logs, log levels, "
        "and external log aggregation support. This is critical for production "
        "monitoring and debugging."
    ),
    "priority": "high",
}

result = register_task_for_execution(
    task_data, "demonstration", {"source": "test_script"}
)
print("Task registration result:")
print(f'Registered: {result["registered"]}')
print(f'Task ID: {result.get("task_id", "N/A")}')
print(f'Message: {result["message"]}')
