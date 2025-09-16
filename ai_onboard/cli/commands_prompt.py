"""Prompt commands for ai - onboard CLI."""

from pathlib import Path

from ..core import prompt_bridge


def add_prompt_commands(subparsers):
    """Add prompt command parsers."""

    s_prompt = subparsers.add_parser("prompt", help="Prompt management and generation")
    sp_sub = s_prompt.add_subparsers(dest="prompt_cmd", required=True)

    # state
    sp_sub.add_parser(
        "state", help="Show prompt - related project state (manifest, last metrics)"
    )

    # summary
    summary_parser = sp_sub.add_parser("summary", help="Generate project summary")
    summary_parser.add_argument(
        "--level",
        choices=["brief", "detailed", "comprehensive"],
        default="brief",
        help="Summary detail level",
    )

    # progress (canonical task completion progress)
    sp_sub.add_parser(
        "progress", help="Show task completion progress from project plan"
    )

    # wbs (work breakdown structure)
    wbs_parser = sp_sub.add_parser(
        "wbs",
        help="Show Work Breakdown Structure with completion status and critical path",
    )
    wbs_parser.add_argument(
        "--format",
        choices=["tree", "table", "json"],
        default="tree",
        help="Output format for WBS display",
    )
    wbs_parser.add_argument(
        "--critical-path", action="store_true", help="Highlight critical path tasks"
    )

    # sweep (consistency sweep)
    sp_sub.add_parser(
        "sweep", help="Run consistency sweep between gates and canonical progress"
    )


def handle_prompt_commands(args, root: Path):
    """Handle prompt command execution."""

    if args.cmd != "prompt":
        return False

    pcmd = getattr(args, "prompt_cmd", None)
    if not pcmd:
        print('{"error":"no prompt subcommand specified"}')
        return True

    if pcmd == "state":
        result = prompt_bridge.get_project_state(root)
        print(prompt_bridge.dumps_json(result))
        return True

    if pcmd == "summary":
        # Generate project summary
        level = getattr(args, "level", "brief")
        try:
            result = prompt_bridge.summary(root, level)
            print(prompt_bridge.dumps_json(result))
        except Exception as e:
            print(f'{{"error":"failed to generate summary: {str(e)}"}}')
        return True

    if pcmd == "progress":
        # Task completion progress snapshot via progress_utils
        try:
            from ..core import progress_utils

            plan = progress_utils.load_plan(root)
            task_progress = progress_utils.compute_overall_progress(plan)
            milestones = progress_utils.compute_milestone_progress(plan)
            out = {
                "task_completion": task_progress,
                "milestones": milestones,
                "description": "Task completion progress based on individual task status",
            }
            print(prompt_bridge.dumps_json(out))
        except Exception as e:
            print(f'{"error":"failed to compute task completion progress: {str(e)}"}')
        return True

    if pcmd == "wbs":
        # Work Breakdown Structure display
        try:
            from ..core import progress_utils

            plan = progress_utils.load_plan(root)
            wbs_data = _generate_wbs_display(
                plan, root, args.format, args.critical_path
            )

            if args.format == "json":
                print(prompt_bridge.dumps_json(wbs_data))
            else:
                print(wbs_data)
        except Exception as e:
            print(f'{"error":"failed to generate WBS: {str(e)}"}')
        return True

    if pcmd == "sweep":
        # Consistency sweep: compare gate visualization vs canonical progress
        try:
            from ..core import progress_utils

            gates_dir = root / ".ai_onboard" / "gates"
            current_gate = gates_dir / "current_gate.md"
            plan = progress_utils.load_plan(root)
            overall = progress_utils.compute_overall_progress(plan)
            report = {
                "canonical_completion_pct": overall.get("completion_percentage"),
                "canonical_bar": overall.get("visual_bar"),
                "gate_present": current_gate.exists(),
                "gate_contains_progress": False,
                "gate_progress_snapshot": None,
                "status": "ok",
            }
            if current_gate.exists():
                content = current_gate.read_text(encoding="utf - 8", errors="ignore")
                # crude parse for a percentage line
                for line in content.splitlines():
                    if "%" in line and (
                        "Progress" in line
                        or "progress" in line
                        or "New Progress Level" in line
                    ):
                        report["gate_contains_progress"] = True
                        report["gate_progress_snapshot"] = line.strip()
                        break
                report["status"] = (
                    "drift_possible" if report["gate_contains_progress"] else "ok"
                )
            print(prompt_bridge.dumps_json(report))
        except Exception as e:
            print(f'{"error":"sweep failed: {str(e)}"}')
        return True


def _generate_wbs_display(
    plan: dict, root: Path, format_type: str, show_critical_path: bool
) -> str:
    """Generate Work Breakdown Structure display."""
    try:
        # Load project plan for WBS data
        project_plan_path = root / ".ai_onboard" / "project_plan.json"
        if project_plan_path.exists():
            import json

            with open(project_plan_path, "r") as f:
                project_plan = json.load(f)

            wbs = project_plan.get("work_breakdown_structure", {})
            critical_path = project_plan.get("critical_path_analysis", {}).get(
                "critical_path", []
            )
            milestones = project_plan.get("milestones", [])

            if format_type == "json":
                return {
                    "wbs": wbs,
                    "critical_path": critical_path,
                    "milestones": milestones,
                    "summary": _generate_wbs_summary(wbs),
                }
            elif format_type == "table":
                return _generate_wbs_table(wbs, critical_path, show_critical_path)
            else:  # tree format
                return _generate_wbs_tree(wbs, critical_path, show_critical_path)
        else:
            return "No project plan found. Run 'ai_onboard plan' to create one."
    except Exception as e:
        return f"Error generating WBS: {str(e)}"


def _generate_wbs_summary(wbs: dict) -> dict:
    """Generate WBS summary statistics."""
    total_phases = len(wbs)
    completed_phases = 0
    in_progress_phases = 0
    total_tasks = 0
    completed_tasks = 0

    for phase_id, phase_data in wbs.items():
        status = phase_data.get("status", "pending")
        if status == "completed":
            completed_phases += 1
        elif status == "in_progress":
            in_progress_phases += 1

        # Count subtasks
        subtasks = phase_data.get("subtasks", {})
        for subtask_id, subtask_data in subtasks.items():
            total_tasks += 1
            if subtask_data.get("status") == "completed":
                completed_tasks += 1

    return {
        "total_phases": total_phases,
        "completed_phases": completed_phases,
        "in_progress_phases": in_progress_phases,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "phase_completion_pct": (
            (completed_phases / total_phases * 100) if total_phases > 0 else 0
        ),
        "task_completion_pct": (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        ),
    }


def _generate_wbs_tree(wbs: dict, critical_path: list, show_critical_path: bool) -> str:
    """Generate tree format WBS display."""
    output = []
    output.append("📋 Work Breakdown Structure (WBS)")
    output.append("=" * 50)
    output.append("")

    # Legend
    if show_critical_path:
        output.append("Legend:")
        output.append("  🔴 Critical Path Task")
        output.append("  ✅ Completed")
        output.append("  🔄 In Progress")
        output.append("  ⏳ Pending")
        output.append("")

    for phase_id, phase_data in wbs.items():
        phase_name = phase_data.get("name", f"Phase {phase_id}")
        status = phase_data.get("status", "pending")

        # Calculate phase completion based on subtasks or explicit percentage
        if "completion_percentage" in phase_data:
            completion_pct = phase_data["completion_percentage"]
        elif status == "completed":
            completion_pct = 100
        elif status == "in_progress":
            # Calculate based on subtask completion
            subtasks = phase_data.get("subtasks", {})
            if subtasks:
                completed_subtasks = sum(
                    1
                    for s in subtasks.values()
                    if s.get("status") == "completed" or s.get("completion", 0) >= 100
                )
                completion_pct = (completed_subtasks / len(subtasks)) * 100
            else:
                completion_pct = 50  # Default for in-progress phases with no subtasks
        else:
            completion_pct = 0

        # Status icon
        if status == "completed":
            status_icon = "✅"
        elif status == "in_progress":
            status_icon = "🔄"
        else:
            status_icon = "⏳"

        # Critical path indicator
        critical_indicator = (
            "🔴 " if show_critical_path and phase_id in critical_path else ""
        )

        output.append(
            f"{critical_indicator}{status_icon} {phase_name} ({completion_pct}%)"
        )

        # Subtasks
        subtasks = phase_data.get("subtasks", {})
        for subtask_id, subtask_data in subtasks.items():
            subtask_name = subtask_data.get("name", f"Subtask {subtask_id}")
            subtask_status = subtask_data.get("status", "pending")
            # Handle both "completion" field and status-based completion
            subtask_completion = subtask_data.get(
                "completion", 100 if subtask_status == "completed" else 0
            )

            # Subtask status icon
            if subtask_status == "completed":
                subtask_icon = "  ✅"
            elif subtask_status == "in_progress":
                subtask_icon = "  🔄"
            else:
                subtask_icon = "  ⏳"

            # Critical path indicator for subtasks
            subtask_critical = (
                "🔴 "
                if show_critical_path and f"{phase_id}_{subtask_id}" in critical_path
                else "    "
            )

            output.append(
                f"{subtask_critical}{subtask_icon} {subtask_name} ({subtask_completion}%)"
            )

        output.append("")

    # Summary
    summary = _generate_wbs_summary(wbs)
    output.append("📊 Summary:")
    output.append(
        f"  Phases: {summary['completed_phases']}/{summary['total_phases']} completed ({summary['phase_completion_pct']:.1f}%)"
    )
    output.append(
        f"  Tasks: {summary['completed_tasks']}/{summary['total_tasks']} completed ({summary['task_completion_pct']:.1f}%)"
    )

    return "\n".join(output)


def _generate_wbs_table(
    wbs: dict, critical_path: list, show_critical_path: bool
) -> str:
    """Generate table format WBS display."""
    output = []
    output.append("📋 Work Breakdown Structure (WBS) - Table Format")
    output.append("=" * 80)
    output.append("")

    # Table header
    header = f"{'Task':<40} {'Status':<12} {'Progress':<10} {'Critical':<8}"
    output.append(header)
    output.append("-" * 80)

    for phase_id, phase_data in wbs.items():
        phase_name = phase_data.get("name", f"Phase {phase_id}")
        status = phase_data.get("status", "pending")

        # Calculate phase completion based on subtasks or explicit percentage
        if "completion_percentage" in phase_data:
            completion_pct = phase_data["completion_percentage"]
        elif status == "completed":
            completion_pct = 100
        elif status == "in_progress":
            # Calculate based on subtask completion
            subtasks = phase_data.get("subtasks", {})
            if subtasks:
                completed_subtasks = sum(
                    1
                    for s in subtasks.values()
                    if s.get("status") == "completed" or s.get("completion", 0) >= 100
                )
                completion_pct = (completed_subtasks / len(subtasks)) * 100
            else:
                completion_pct = 50  # Default for in-progress phases with no subtasks
        else:
            completion_pct = 0

        is_critical = (
            "🔴 Yes" if show_critical_path and phase_id in critical_path else "No"
        )

        # Status formatting
        if status == "completed":
            status_display = "✅ Completed"
        elif status == "in_progress":
            status_display = "🔄 In Progress"
        else:
            status_display = "⏳ Pending"

        output.append(
            f"{phase_name:<40} {status_display:<12} {completion_pct:>6.1f}% {is_critical:<8}"
        )

        # Subtasks
        subtasks = phase_data.get("subtasks", {})
        for subtask_id, subtask_data in subtasks.items():
            subtask_name = f"  └─ {subtask_data.get('name', f'Subtask {subtask_id}')}"
            subtask_status = subtask_data.get("status", "pending")
            # Handle both "completion" field and status-based completion
            subtask_completion = subtask_data.get(
                "completion", 100 if subtask_status == "completed" else 0
            )
            subtask_critical = (
                "🔴 Yes"
                if show_critical_path and f"{phase_id}_{subtask_id}" in critical_path
                else "No"
            )

            # Subtask status formatting
            if subtask_status == "completed":
                subtask_status_display = "✅ Completed"
            elif subtask_status == "in_progress":
                subtask_status_display = "🔄 In Progress"
            else:
                subtask_status_display = "⏳ Pending"

            output.append(
                f"{subtask_name:<40} {subtask_status_display:<12} {subtask_completion:>6.1f}% {subtask_critical:<8}"
            )

    output.append("")

    # Summary
    summary = _generate_wbs_summary(wbs)
    output.append("📊 Summary:")
    output.append(f"  Total Phases: {summary['total_phases']}")
    output.append(
        f"  Completed Phases: {summary['completed_phases']} ({summary['phase_completion_pct']:.1f}%)"
    )
    output.append(f"  In Progress Phases: {summary['in_progress_phases']}")
    output.append(f"  Total Tasks: {summary['total_tasks']}")
    output.append(
        f"  Completed Tasks: {summary['completed_tasks']} ({summary['task_completion_pct']:.1f}%)"
    )

    return "\n".join(output)
