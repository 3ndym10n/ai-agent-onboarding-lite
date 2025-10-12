#!/usr/bin/env python3
import json
from ai_onboard.core.base.progress_utils import compute_overall_progress

# Load the plan file and compute progress directly
with open(".ai_onboard/plan.json", "r") as f:
    plan = json.load(f)

print("Plan file exists and loaded successfully")
print("Total tasks in plan:", len(plan.get("tasks", [])))

# Count completed tasks manually
tasks = plan.get("tasks", [])
completed_tasks = [t for t in tasks if t.get("status") == "completed"]
print("Tasks with status=completed:", len(completed_tasks))

for task in completed_tasks[:5]:
    task_id = task.get("id")
    task_name = task.get("name")
    task_status = task.get("status")
    print(f"  - {task_id}: {task_name} ({task_status})")

progress = compute_overall_progress(plan)
print("Progress calculation:")
print(f'Total tasks: {progress["total_tasks"]}')
print(f'Completed tasks: {progress["completed_tasks"]}')
print(f'Completion percentage: {progress["completion_percentage"]}%')





