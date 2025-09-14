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

    # progress (canonical progress snapshot)
    sp_sub.add_parser("progress", help="Show canonical project progress from plan.json")

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
        # Canonical progress snapshot via progress_utils
        try:
            from ..core import progress_utils

            plan = progress_utils.load_plan(root)
            overall = progress_utils.compute_overall_progress(plan)
            milestones = progress_utils.compute_milestone_progress(plan)
            out = {"overall": overall, "milestones": milestones}
            print(prompt_bridge.dumps_json(out))
        except Exception as e:
            print(f'{"error":"failed to compute progress: {str(e)}"}')
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

    print('{"error":"unknown prompt subcommand"}')
    return True
