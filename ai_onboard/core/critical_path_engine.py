"""
Critical Path Engine - Automatically detects and updates critical path tasks.

This module implements the Critical Path Method (CPM) to:
- Analyze task dependencies and durations
- Identify the critical path (longest sequence of dependent tasks)
- Calculate task slack/float
- Automatically update critical path designations
"""

from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from . import utils
from .tool_usage_tracker import track_tool_usage


class CriticalPathEngine:
    """Engine for analyzing and updating project critical paths."""


    def __init__(self, root: Path):
        self.root = root
        self.project_plan_path = root / ".ai_onboard" / "project_plan.json"
        track_tool_usage(
            "critical_path_engine", "ai_system", {"action": "initialize"}, "success"
        )


    def analyze_critical_path(self) -> Dict[str, Any]:
        """
        Perform complete critical path analysis of the project.

        Returns:
            Dict containing critical path analysis results
        """
        track_tool_usage(
            "critical_path_engine",
            "ai_system",
            {"action": "analyze_critical_path"},
            "success",
        )

        plan_data = utils.read_json(self.project_plan_path, default={})
        wbs = plan_data.get("work_breakdown_structure", {})

        # Extract all tasks with dependencies
        tasks = self._extract_tasks_with_dependencies(wbs)

        # Build dependency graph
        dependency_graph = self._build_dependency_graph(tasks)
        reverse_graph = self._build_reverse_graph(dependency_graph)

        # Calculate earliest/latest start/finish times
        timing_data = self._calculate_task_timing(
            tasks, dependency_graph, reverse_graph
        )

        # Identify critical path
        critical_path = self._identify_critical_path(tasks, timing_data)

        # Calculate slack/float for all tasks
        slack_data = self._calculate_slack(timing_data)

        # Generate analysis results
        analysis_results = {
            "critical_path": critical_path,
            "timing_data": timing_data,
            "slack_data": slack_data,
            "total_project_duration": self._calculate_project_duration(timing_data),
            "critical_tasks_count": len(critical_path),
            "total_tasks_analyzed": len(tasks),
            "analysis_timestamp": utils.now_iso(),
        }

        return analysis_results


    def _extract_tasks_with_dependencies(
        self, wbs: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Extract all tasks and normalize their dependency information."""
        tasks = {}


        def extract_from_phase(phase_id: str, phase_data: Dict[str, Any]):
            # Add the phase itself
            if "name" in phase_data:
                tasks[phase_id] = dict(phase_data)
                tasks[phase_id]["task_type"] = "phase"
                # Normalize dependencies
                deps = phase_data.get("dependencies", [])
                if isinstance(deps, str):
                    tasks[phase_id]["dependencies"] = [
                        d.strip() for d in deps.split(",") if d.strip()
                    ]
                elif isinstance(deps, list):
                    tasks[phase_id]["dependencies"] = deps
                else:
                    tasks[phase_id]["dependencies"] = []

            # Extract subtasks
            subtasks = phase_data.get("subtasks", {})
            for subtask_id, subtask_data in subtasks.items():
                # Use subtask_id directly - it's already properly formatted (e.g., "4.1", "4.2")
                tasks[subtask_id] = dict(subtask_data)
                tasks[subtask_id]["task_type"] = "subtask"
                tasks[subtask_id]["parent_phase"] = phase_id

                # Normalize dependencies for subtasks
                deps = subtask_data.get("dependencies", [])
                if isinstance(deps, str):
                    tasks[subtask_id]["dependencies"] = [
                        d.strip() for d in deps.split(",") if d.strip()
                    ]
                elif isinstance(deps, list):
                    tasks[subtask_id]["dependencies"] = deps
                else:
                    tasks[subtask_id]["dependencies"] = []

        for phase_id, phase_data in wbs.items():
            extract_from_phase(phase_id, phase_data)

        return tasks


    def _build_dependency_graph(
        self, tasks: Dict[str, Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Build forward dependency graph (task -> tasks that depend on it)."""
        graph = defaultdict(list)

        for task_id, task_data in tasks.items():
            dependencies = task_data.get("dependencies", [])
            for dep in dependencies:
                if dep in tasks:  # Only include dependencies that exist
                    graph[dep].append(task_id)

        return dict(graph)


    def _build_reverse_graph(
        self, dependency_graph: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Build reverse dependency graph (task -> tasks it depends on)."""
        reverse_graph = defaultdict(list)

        for predecessor, successors in dependency_graph.items():
            for successor in successors:
                reverse_graph[successor].append(predecessor)

        return dict(reverse_graph)


    def _calculate_task_timing(
        self,
        tasks: Dict[str, Dict[str, Any]],
        dependency_graph: Dict[str, List[str]],
        reverse_graph: Dict[str, List[str]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate earliest/latest start and finish times for all tasks.

        Uses forward pass (earliest times) and backward pass (latest times).
        """
        timing = {}

        # Forward pass - calculate earliest start/finish times
        for task_id in tasks:
            timing[task_id] = {
                "earliest_start": 0,
                "earliest_finish": self._estimate_task_duration(tasks[task_id]),
                "latest_start": float("inf"),
                "latest_finish": float("inf"),
            }

        # Process tasks in topological order for forward pass
        processed = set()
        queue = deque(
            [task_id for task_id in tasks if not reverse_graph.get(task_id, [])]
        )

        while queue:
            task_id = queue.popleft()
            if task_id in processed:
                continue
            processed.add(task_id)

            task_data = timing[task_id]
            successors = dependency_graph.get(task_id, [])

            for successor in successors:
                if successor in timing:
                    # Earliest start of successor = max(earliest finish of predecessors)
                    timing[successor]["earliest_start"] = max(
                        timing[successor]["earliest_start"],
                        task_data["earliest_finish"],
                    )
                    timing[successor]["earliest_finish"] = timing[successor][
                        "earliest_start"
                    ] + self._estimate_task_duration(tasks[successor])

                    # Add successor to queue if all predecessors processed
                    pred_count = len(reverse_graph.get(successor, []))
                    processed_preds = sum(
                        1 for p in reverse_graph.get(successor, []) if p in processed
                    )
                    if processed_preds == pred_count:
                        queue.append(successor)

        # Backward pass - calculate latest start/finish times
        # Find tasks with no successors (end tasks)
        end_tasks = [
            task_id for task_id in tasks if not dependency_graph.get(task_id, [])
        ]

        # Set latest finish for end tasks to their earliest finish
        project_end = max(timing[task_id]["earliest_finish"] for task_id in end_tasks)

        for task_id in end_tasks:
            timing[task_id]["latest_finish"] = project_end
            timing[task_id]["latest_start"] = timing[task_id][
                "latest_finish"
            ] - self._estimate_task_duration(tasks[task_id])

        # Process backward from end tasks
        processed_back = set(end_tasks)
        queue_back = deque(end_tasks)

        while queue_back:
            task_id = queue_back.popleft()
            task_data = timing[task_id]
            predecessors = reverse_graph.get(task_id, [])

            for predecessor in predecessors:
                if predecessor in timing:
                    # Latest finish of predecessor = min(latest start of successors)
                    timing[predecessor]["latest_finish"] = min(
                        timing[predecessor]["latest_finish"], task_data["latest_start"]
                    )
                    timing[predecessor]["latest_start"] = timing[predecessor][
                        "latest_finish"
                    ] - self._estimate_task_duration(tasks[predecessor])

                    if predecessor not in processed_back:
                        processed_back.add(predecessor)
                        queue_back.append(predecessor)

        return timing


    def _estimate_task_duration(self, task_data: Dict[str, Any]) -> int:
        """Estimate task duration based on effort level and status."""
        effort = task_data.get("estimated_effort", "medium").lower()
        status = task_data.get("status", "pending").lower()

        # Base duration by effort level (in days)
        effort_duration = {"small": 1, "medium": 3, "large": 7, "xlarge": 14}.get(
            effort, 3
        )

        # Adjust for status
        if status == "completed":
            return 0  # Completed tasks don't contribute to remaining duration
        elif status == "in_progress":
            return max(1, effort_duration // 2)  # Assume half remaining
        elif status == "blocked":
            return effort_duration * 2  # Blocked tasks take longer
        else:
            return effort_duration


    def _identify_critical_path(
        self, tasks: Dict[str, Dict[str, Any]], timing_data: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Identify tasks on the critical path (those with zero slack)."""
        critical_tasks = []

        for task_id, timing in timing_data.items():
            slack = timing["latest_start"] - timing["earliest_start"]
            if abs(slack) < 0.1:  # Consider zero slack (within small tolerance)
                critical_tasks.append(task_id)

        # Sort critical tasks by earliest start time to create the path sequence
        critical_tasks.sort(key=lambda x: timing_data[x]["earliest_start"])

        return critical_tasks


    def _calculate_slack(
        self, timing_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Calculate slack/float for all tasks."""
        slack_data = {}

        for task_id, timing in timing_data.items():
            total_slack = timing["latest_start"] - timing["earliest_start"]
            free_slack = 0  # Would need more complex calculation for free slack

            slack_data[task_id] = {
                "total_slack": max(0, total_slack),  # Ensure non-negative
                "free_slack": free_slack,
                "is_critical": abs(total_slack) < 0.1,
            }

        return slack_data


    def _calculate_project_duration(
        self, timing_data: Dict[str, Dict[str, Any]]
    ) -> int:
        """Calculate total project duration from critical path."""
        if not timing_data:
            return 0

        max_finish = max(timing["earliest_finish"] for timing in timing_data.values())
        return int(max_finish)


    def update_critical_path_in_plan(
        self, analysis_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update the project plan to mark critical path tasks.

        Args:
            analysis_results: Pre-computed analysis results (optional)

        Returns:
            Dict with update results
        """
        track_tool_usage(
            "critical_path_engine",
            "ai_system",
            {"action": "update_critical_path"},
            "success",
        )

        if analysis_results is None:
            analysis_results = self.analyze_critical_path()

        plan_data = utils.read_json(self.project_plan_path, default={})
        wbs = plan_data.get("work_breakdown_structure", {})

        critical_tasks = set(analysis_results["critical_path"])
        updated_count = 0

        # Update tasks in WBS

        def update_phase_critical_path(phase_id: str, phase_data: Dict[str, Any]):
            nonlocal updated_count

            # Update phase
            was_critical = phase_data.get("is_critical_path", False)
            is_critical = phase_id in critical_tasks

            if was_critical != is_critical:
                phase_data["is_critical_path"] = is_critical
                updated_count += 1

            # Update subtasks
            subtasks = phase_data.get("subtasks", {})
            for subtask_id, subtask_data in subtasks.items():
                full_id = (
                    f"{phase_id}.{subtask_id.split('.')[-1]}"
                    if "." in subtask_id
                    else subtask_id
                )

                was_critical = subtask_data.get("is_critical_path", False)
                is_critical = full_id in critical_tasks

                if was_critical != is_critical:
                    subtask_data["is_critical_path"] = is_critical
                    updated_count += 1

        for phase_id, phase_data in wbs.items():
            update_phase_critical_path(phase_id, phase_data)

        # Update project metadata
        plan_data["work_breakdown_structure"] = wbs
        plan_data["last_updated"] = utils.now_iso()

        # Add critical path summary
        plan_data["critical_path_analysis"] = {
            "last_updated": utils.now_iso(),
            "critical_tasks": analysis_results["critical_path"],
            "project_duration": analysis_results["total_project_duration"],
            "total_tasks": analysis_results["total_tasks_analyzed"],
        }

        utils.write_json(self.project_plan_path, plan_data)

        return {
            "success": True,
            "critical_tasks_updated": updated_count,
            "critical_path_length": len(analysis_results["critical_path"]),
            "project_duration": analysis_results["total_project_duration"],
            "message": f"Updated {updated_count} tasks with critical path designations",
        }


    def get_critical_path_report(self) -> Dict[str, Any]:
        """Generate a comprehensive critical path report."""
        track_tool_usage(
            "critical_path_engine",
            "ai_system",
            {"action": "generate_report"},
            "success",
        )

        analysis = self.analyze_critical_path()

        # Build detailed report
        report = {
            "summary": {
                "total_tasks": analysis["total_tasks_analyzed"],
                "critical_tasks": analysis["critical_tasks_count"],
                "project_duration_days": analysis["total_project_duration"],
                "critical_percentage": round(
                    (
                        analysis["critical_tasks_count"]
                        / max(analysis["total_tasks_analyzed"], 1)
                    )
                    * 100,
                    1,
                ),
            },
            "critical_path": [],
            "bottlenecks": [],
            "recommendations": [],
        }

        # Build critical path details
        for task_id in analysis["critical_path"]:
            timing = analysis["timing_data"][task_id]
            slack = analysis["slack_data"][task_id]

            report["critical_path"].append(
                {
                    "task_id": task_id,
                    "task_name": f"Task {task_id}",  # Would need to look up actual name
                    "duration": timing["earliest_finish"] - timing["earliest_start"],
                    "start_day": int(timing["earliest_start"]),
                    "finish_day": int(timing["earliest_finish"]),
                    "slack": slack["total_slack"],
                }
            )

        # Identify bottlenecks (tasks with high impact)
        for task_id, slack_info in analysis["slack_data"].items():
            if slack_info["total_slack"] == 0 and task_id in analysis["critical_path"]:
                # This is a critical task - check if it has many dependencies
                timing = analysis["timing_data"][task_id]
                duration = timing["earliest_finish"] - timing["earliest_start"]
                if duration > 5:  # Arbitrary threshold for "long" tasks
                    report["bottlenecks"].append(
                        {
                            "task_id": task_id,
                            "duration": int(duration),
                            "impact": "high",
                        }
                    )

        # Generate recommendations
        if report["summary"]["critical_percentage"] > 70:
            report["recommendations"].append(
                "⚠️ HIGH CRITICAL PATH: Too many tasks on critical path - consider parallelization"
            )

        if report["bottlenecks"]:
            report["recommendations"].append(
                f"🎯 BOTTLENECKS: {len(report['bottlenecks'])} long critical tasks - consider breaking down"
            )

        if not report["critical_path"]:
            report["recommendations"].append(
                "✅ NO CRITICAL PATH: All tasks have slack - project is flexible"
            )

        return report


def analyze_critical_path(root: Optional[Path] = None) -> Dict[str, Any]:
    """Convenience function to analyze critical path."""
    if root is None:
        root = Path.cwd()

    engine = CriticalPathEngine(root)
    return engine.analyze_critical_path()


def update_critical_path(root: Optional[Path] = None) -> Dict[str, Any]:
    """Convenience function to update critical path in project plan."""
    if root is None:
        root = Path.cwd()

    engine = CriticalPathEngine(root)
    return engine.update_critical_path_in_plan()
