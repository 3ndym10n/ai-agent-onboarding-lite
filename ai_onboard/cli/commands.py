import argparse
import json
from pathlib import Path

from ..core import (
    alignment,
    charter,
    cleanup,
    context_continuity,
    design_system,
    discovery,
    dynamic_planner,
    optimizer,
    planning,
    progress_tracker,
    prompt_bridge,
    smart_debugger,
    state,
    task_completion_detector,
    telemetry,
    utils,
    validation_runtime,
    versioning,
    vision_guardian,
    vision_interrogator,
    visual_design,
)
from ..core.unicode_utils import print_activity, print_content, print_status, safe_print

# Import CLI command modules
from .commands_cleanup_safety import (
    add_cleanup_safety_commands,
    handle_cleanup_safety_commands,
)

# from ..plugins import example_policy  # ensure example plugin registers on import


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="ai_onboard",
        description=(
            "AI Onboard: drop-in project coach "
            "(charter + plan + align + validate + kaizen)"
        ),
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s_an = sub.add_parser(
        "analyze", help="Scan repo and draft ai_onboard.json manifest"
    )
    s_an.add_argument(
        "--allowExec",
        action="store_true",
        help="Permit safe external probes (off by default)",
    )

    s_ch = sub.add_parser("charter", help="Create or update project charter")
    s_ch.add_argument("--interactive", action="store_true")

    sub.add_parser("plan", help="Build plan.json from charter")

    s_al = sub.add_parser("align", help="Open or approve an alignment checkpoint")
    s_al.add_argument("--checkpoint", default="PlanGate")
    s_al.add_argument("--approve", action="store_true")
    s_al.add_argument("--note", default="", help="Optional note to store with approval")
    s_al.add_argument(
        "--preview",
        action="store_true",
        help="Compute dry-run alignment report (no edits)",
    )

    s_v = sub.add_parser("validate", help="Run validation and write report")
    s_v.add_argument(
        "--report",
        action="store_true",
        help="Write .ai_onboard/report.md and versioned copy",
    )

    s_k = sub.add_parser("kaizen", help="Run a kaizen cycle (metrics-driven nudges)")
    s_k.add_argument("--once", action="store_true")

    s_o = sub.add_parser("optimize", help="Optimization Strategist (MVP)")
    so_sub = s_o.add_subparsers(dest="opt_cmd", required=False)
    s_o.add_argument("--budget", default="5m", help="Time budget (e.g., 5m)")
    so_sub.add_parser("propose", help="Generate optimization proposals and open gate")
    s_sbx = so_sub.add_parser(
        "sandbox", help="Create sandbox plan for a proposal and open gate"
    )
    s_sbx.add_argument(
        "--proposal-id",
        default="",
        help="Proposal ID (optional; defaults to top proposal)",
    )

    s_ver = sub.add_parser("version", help="Show or bump ai_onboard version")
    s_ver.add_argument("--bump", choices=["major", "minor", "patch"])
    s_ver.add_argument("--set", help="Set explicit version (e.g., 1.2.3)")

    sub.add_parser("metrics", help="Show last validation run summary from telemetry")

    s_clean = sub.add_parser(
        "cleanup",
        help="Safely remove non-critical files (build artifacts, cache, etc.)",
    )
    s_clean.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    s_clean.add_argument(
        "--force", action="store_true", help="Skip confirmation prompts"
    )
    s_clean.add_argument(
        "--backup", action="store_true", help="Create backup before cleanup"
    )

    # Cleanup Safety Gates
    add_cleanup_safety_commands(sub)

    # Checkpoints (agent-aware snapshots)
    s_ck = sub.add_parser("checkpoint", help="Manage lightweight checkpoints")
    ck_sub = s_ck.add_subparsers(dest="ck_cmd", required=True)
    ck_create = ck_sub.add_parser(
        "create", help="Create checkpoint for given scope globs"
    )
    ck_create.add_argument("--scope", nargs="+", default=["."])
    ck_create.add_argument("--reason", default="")
    ck_sub.add_parser("list", help="List checkpoints")
    ck_restore = ck_sub.add_parser("restore", help="Restore by id")
    ck_restore.add_argument("--id", required=True)

    # Agent-facing prompt bridge (read-mostly, feature-flagged)
    s_prompt = sub.add_parser(
        "prompt", help="Agent context APIs: state|rules|summary|propose"
    )
    sp = s_prompt.add_subparsers(dest="prompt_cmd", required=True)
    sp.add_parser("state", help="Emit compact project state JSON")
    sp_rules = sp.add_parser(
        "rules", help="Applicable meta-policy rules for a target path"
    )
    sp_rules.add_argument("--path", default=".")
    sp_rules.add_argument(
        "--change", default="", help="Optional change summary (free-text or JSON)"
    )
    sp_summary = sp.add_parser("summary", help="Model-aware summary: brief|full")
    sp_summary.add_argument("--level", choices=["brief", "full"], default="brief")
    sp_propose = sp.add_parser(
        "propose", help="Propose action; returns decision and rationale"
    )
    sp_propose.add_argument(
        "--diff",
        default="",
        help="JSON {files_changed, lines_deleted, has_tests, subsystems}",
    )

    # Progress tracking command
    sub.add_parser(
        "progress-scan",
        help="Scan for completed tasks and update plan with gate confirmation",
    )

    # Vision and planning commands
    s_vision = sub.add_parser("vision", help="Vision alignment and scope management")
    sv_sub = s_vision.add_subparsers(dest="vision_cmd", required=True)
    validate_parser = sv_sub.add_parser(
        "validate", help="Validate decision alignment with project vision"
    )
    validate_parser.add_argument("--decision", help="Decision data (JSON)")

    scope_parser = sv_sub.add_parser(
        "scope-change", help="Propose scope change with user validation"
    )
    scope_parser.add_argument("--change", help="Scope change data (JSON)")

    update_parser = sv_sub.add_parser("update", help="Update vision documents")
    update_parser.add_argument("--update", help="Update data (JSON)")

    # UI/UX Design commands
    s_design = sub.add_parser("design", help="UI/UX design validation and management")
    sd_sub = s_design.add_subparsers(dest="design_cmd", required=True)

    analyze_parser = sd_sub.add_parser(
        "analyze", help="Analyze UI design from screenshot"
    )
    analyze_parser.add_argument(
        "--screenshot", required=True, help="Path to screenshot file"
    )

    validate_parser = sd_sub.add_parser("validate", help="Validate design decision")
    validate_parser.add_argument(
        "--description", required=True, help="Design description"
    )

    consistency_parser = sd_sub.add_parser(
        "consistency", help="Check design consistency"
    )
    consistency_parser.add_argument(
        "--description", required=True, help="Design description"
    )

    system_parser = sd_sub.add_parser("system", help="Design system management")
    system_sub = system_parser.add_subparsers(dest="system_cmd", required=True)
    system_sub.add_parser("summary", help="Show design system summary")
    system_sub.add_parser("tokens", help="List design tokens")
    system_sub.add_parser("components", help="List design components")
    system_sub.add_parser("patterns", help="List design patterns")

    # Dynamic planning commands
    s_planning = sub.add_parser("planning", help="Dynamic project planning")
    sp_sub = s_planning.add_subparsers(dest="planning_cmd", required=True)
    milestone_parser = sp_sub.add_parser("milestone", help="Mark milestone complete")
    milestone_parser.add_argument("--name", help="Milestone name")
    milestone_parser.add_argument("--completion", help="Completion data (JSON)")

    progress_parser = sp_sub.add_parser("progress", help="Update activity progress")
    progress_parser.add_argument("--activity-id", help="Activity ID")
    progress_parser.add_argument("--progress", help="Progress data (JSON)")

    sp_sub.add_parser("auto-update", help="Auto-update plan based on progress")
    sp_sub.add_parser(
        "progress-scan",
        help="Scan for completed tasks and update plan with gate confirmation",
    )

    add_milestone_parser = sp_sub.add_parser(
        "add-milestone", help="Add new milestone to plan"
    )
    add_milestone_parser.add_argument("--milestone", help="Milestone data (JSON)")

    # Smart debugging commands
    s_debug = sub.add_parser("debug", help="Smart debugging system")
    sd_sub = s_debug.add_subparsers(dest="debug_cmd", required=True)
    analyze_parser = sd_sub.add_parser(
        "analyze", help="Analyze error and provide smart insights"
    )
    analyze_parser.add_argument("--error", help="Error data (JSON)")

    sd_sub.add_parser("improve", help="Improve debugging patterns")
    sd_sub.add_parser("stats", help="Show debugging system statistics")

    # Context continuity commands
    s_context = sub.add_parser("context", help="Context continuity management")
    sc_sub = s_context.add_subparsers(dest="context_cmd", required=True)
    summary_parser = sc_sub.add_parser("summary", help="Get context summary")
    summary_parser.add_argument(
        "--level", default="brief", help="Summary level (brief/full)"
    )

    sc_sub.add_parser("drift", help="Check for context drift")

    resolve_parser = sc_sub.add_parser("resolve", help="Resolve context drift")
    resolve_parser.add_argument("--drift-type", help="Drift type")
    resolve_parser.add_argument("--resolution", help="Resolution data (JSON)")

    # Vision interrogation commands
    # User preference learning commands
    s_prefs = sub.add_parser("user-prefs", help="User preference learning commands")
    sprefs = s_prefs.add_subparsers(dest="prefs_cmd", required=True)
    rec_parser = sprefs.add_parser(
        "record", help="Record a user interaction for learning"
    )
    rec_parser.add_argument("--user", required=True, help="User ID")
    rec_parser.add_argument(
        "--type", required=True, help="Interaction type (enum value)"
    )
    rec_parser.add_argument("--context", default="{}", help="Context JSON")
    rec_parser.add_argument("--duration", type=float)
    rec_parser.add_argument("--outcome", default="{}", help="Outcome JSON")
    rec_parser.add_argument("--satisfaction", type=float)
    rec_parser.add_argument("--feedback", default="")
    sprefs.add_parser("summary", help="Show user profile summary").add_argument(
        "--user", required=True
    )
    sprefs.add_parser("recommend", help="Get user recommendations").add_argument(
        "--user", required=True
    )
    s_interrogate = sub.add_parser("interrogate", help="Vision interrogation system")
    si_sub = s_interrogate.add_subparsers(dest="interrogate_cmd", required=True)
    si_sub.add_parser("check", help="Check if vision is ready for AI agents")
    si_sub.add_parser("start", help="Start vision interrogation process")
    submit_parser = si_sub.add_parser(
        "submit", help="Submit response to interrogation question"
    )
    submit_parser.add_argument("--phase", help="Interrogation phase")
    submit_parser.add_argument("--question-id", help="Question ID")
    submit_parser.add_argument("--response", help="Response data (JSON)")
    si_sub.add_parser("questions", help="Get current interrogation questions")
    si_sub.add_parser("summary", help="Get interrogation summary")
    si_sub.add_parser(
        "force-complete", help="Force complete interrogation (use with caution)"
    )

    args = p.parse_args(argv)
    root = Path.cwd()
    st = state.load(root)

    try:
        if args.cmd == "analyze":
            manifest = discovery.run(root, allow_exec=args.allowExec)
            utils.write_json(root / "ai_onboard.json", manifest)
            print("Wrote ai_onboard.json (draft).")
            return

        if args.cmd == "charter":
            charter.ensure(root, interactive=args.interactive)
            state.advance(root, st, "chartered")
            print("Charter ready at .ai_onboard/charter.json")
            return

        if args.cmd == "plan":
            charter.require_gate(root, "chartered")
            planning.build(root)
            state.advance(root, st, "planned")
            print("Plan ready at .ai_onboard/plan.json")
            return

        if args.cmd == "align":
            # Non-invasive preview mode
            if getattr(args, "preview", False):
                res = alignment.preview(root)
                print(prompt_bridge.dumps_json(res))
                return
            cp = args.checkpoint
            if args.approve:
                alignment.record_decision(root, "ALIGN", cp, True, args.note)
                state.advance(root, st, "aligned")
                print(f"Alignment approved for {cp}.")
            else:
                alignment.open_checkpoint(root, cp)
                print(f"Opened alignment checkpoint {cp}.")
            return

        if args.cmd == "validate":
            alignment.require_state(root, "aligned")
            res = validation_runtime.run(root)
            if args.report:
                progress_tracker.write_report(root, res)
                print("Wrote .ai_onboard/report.md (+ versioned copy).")
            telemetry.record_run(root, res)
            return

        if args.cmd == "kaizen":
            print(
                "Kaizen: ingesting telemetry and nudging schedules/bounds (lightweight)."
            )
            optimizer.nudge_from_metrics(root)
            return

        if args.cmd == "optimize":
            # Subcommands
            ocmd = getattr(args, "opt_cmd", None)
            if ocmd == "propose":
                from ..core.gate_system import GateRequest, GateSystem, GateType

                budget_seconds = optimizer.parse_budget(args.budget)
                proposals = optimizer.generate_optimization_proposals(
                    root, budget_seconds
                )

                # Build executive summary
                summary_lines = []
                for pz in proposals.get("proposals", [])[:5]:
                    summary_lines.append(
                        f"• {pz['id']} → {pz['title']} (risk={pz['risk']}, est_gain={pz['estimated_gain']}, conf={pz['confidence']})"
                    )

                questions = [
                    "Approve pursuing selected optimization proposals?",
                    f"Default experiment budget is {args.budget}. Allow override per run?",
                    "Proceed on separate branches for high-risk/low-confidence items?",
                ]

                gate_system = GateSystem(root)
                gate_request = GateRequest(
                    gate_type=GateType.CONFIRMATION_REQUIRED,
                    title="Optimization Strategist Proposals",
                    description="Review and approve optimization proposals grounded in latest evidence.",
                    context={
                        "executive_summary": {
                            "total_proposals": len(proposals.get("proposals", [])),
                            "new_progress_percentage": "N/A",
                            "task_descriptions": summary_lines,
                            "categories": {"proposals": len(summary_lines)},
                        },
                        "evidence": proposals.get("evidence_summary", {}),
                    },
                    questions=questions,
                )
                gate_system.create_gate(gate_request)
                print_content(
                    "Gate created for Optimization Strategist proposals: .ai_onboard/gates/current_gate.md",
                    "status",
                )
                print("Run 'ai_onboard gate respond' after answering the questions")
                return

            if ocmd == "sandbox":
                from ..core.gate_system import GateRequest, GateSystem, GateType

                budget_seconds = optimizer.parse_budget(args.budget)
                plan = optimizer.create_sandbox_plan(
                    root, getattr(args, "proposal_id", "") or None, budget_seconds
                )

                selected = plan.get("selected_proposal", {})
                sel_line = (
                    f"• {selected.get('id','?')} → {selected.get('title','?')} (risk={selected.get('risk','?')}, est_gain={selected.get('estimated_gain','?')}, conf={selected.get('confidence','?')})"
                    if selected
                    else "• No proposal selected"
                )

                questions = [
                    f"Approve sandboxing proposal '{selected.get('id','?')}' on branch {plan.get('branch','?')}?",
                    f"Use budget {args.budget} (override allowed)?",
                    "Proceed only if tests pass and gains are measurable?",
                ]

                gate_system = GateSystem(root)
                gate_request = GateRequest(
                    gate_type=GateType.CONFIRMATION_REQUIRED,
                    title="Optimization Sandbox Plan",
                    description="Approve sandbox plan (branch + steps) for selected optimization proposal.",
                    context={
                        "executive_summary": {
                            "total_proposals": 1 if selected else 0,
                            "task_descriptions": [sel_line]
                            + [f"  - {s}" for s in plan.get("steps", [])],
                            "categories": {"steps": len(plan.get("steps", []))},
                        },
                        "evidence": plan.get("evidence", {}),
                        "branch": plan.get("branch"),
                    },
                    questions=questions,
                )
                gate_system.create_gate(gate_request)
                print_content(
                    "Gate created for Optimization Sandbox Plan: .ai_onboard/gates/current_gate.md",
                    "status",
                )
                print("Run 'ai_onboard gate respond' after answering the questions")
                return

            # Default quick optimize stub
            optimizer.quick_optimize(root, args.budget)
            return

        if args.cmd == "version":
            if args.set:
                versioning.set_version(root, args.set)
                print(f"Version set to {args.set}")
                return
            if args.bump:
                current = versioning.get_version(root)
                newv = versioning.bump(current, args.bump)
                versioning.set_version(root, newv)
                print(f"Bumped {args.bump}: {current} -> {newv}")
                return
            print(versioning.get_version(root))
            return

        if args.cmd == "metrics":
            last = telemetry.last_run(root)
            if not last:
                print("No telemetry yet. Run: python -m ai_onboard validate --report")
                return
            comps = last.get("components", [])
            comp_lines = [
                f"- {c.get('name','?')}: score={c.get('score','n/a')} issues={c.get('issue_count',0)}"
                for c in comps
            ]
            print("Last validation run:")
            print(f"- ts: {last.get('ts')}")
            print(f"- pass: {last.get('pass')}")
            print("- components:")
            for line in comp_lines:
                print(line)
            return

        # Clean, early handler for cleanup to avoid legacy garbled prints below
        if args.cmd == "cleanup":
            print_activity("Scanning for files to clean up...", "search")

            # Always start with dry-run to show what would be deleted
            result = cleanup.safe_cleanup(root, dry_run=True)

            print("\nScan Results:")
            print(f"  Protected (critical): {result['protected']} files")
            print(f"  Would delete: {result['would_delete']} files")
            print(f"  Unknown: {result['unknown']} files")

            if result["would_delete"] == 0:
                print("\nNo files to clean up!")
                return

            if args.dry_run:
                print("\nDRY RUN MODE - No files will be deleted")
                print("Files that would be deleted:")
                for path in result["scan_result"]["non_critical"][:10]:  # Show first 10
                    print(f"  - {path.relative_to(root)}")
                if len(result["scan_result"]["non_critical"]) > 10:
                    print(
                        f"  ... and {len(result['scan_result']['non_critical']) - 10} more"
                    )
                return

            # Real cleanup mode
            if not args.force:
                response = input(
                    f"\nAre you sure you want to delete {result['would_delete']} files? (y/N): "
                )
                if response.lower() != "y":
                    print("Cleanup cancelled.")
                    return

            # Create backup if requested
            if args.backup:
                print("Creating backup...")
                backup_dir = cleanup.create_backup(root)
                print(f"Backup created at: {backup_dir}")

            print("Performing cleanup...")
            result = cleanup.safe_cleanup(root, dry_run=False)

            print("\nCleanup completed!")
            print(f"  Deleted: {result['deleted_count']} files")
            if result["errors"]:
                print(f"  Errors: {len(result['errors'])} files failed to delete")
                for error in result["errors"][:5]:
                    print(f"    - {error}")
            return

        # Cleanup Safety Gates
        if args.cmd == "cleanup-safety":
            handle_cleanup_safety_commands(args, root)
            return

        if args.cmd == "checkpoint":
            manifest = utils.read_json(root / "ai_onboard.json", default={}) or {}
            ff = manifest.get("features") or {}
            if ff.get("checkpoints", True) is False:
                print('{"error":"checkpoints disabled"}')
                return
            subcmd = getattr(args, "ck_cmd", None)
            from ..core import checkpoints

            if subcmd == "create":
                rec = checkpoints.create(root, scope=args.scope, reason=args.reason)
                print(prompt_bridge.dumps_json({"created": rec}))
                return
            if subcmd == "list":
                items = checkpoints.list(root)
                print(prompt_bridge.dumps_json({"items": items}))
                return
            if subcmd == "restore":
                res = checkpoints.restore(root, ckpt_id=args.id)
                print(prompt_bridge.dumps_json(res))
                return
            print('{"error":"unknown checkpoint subcommand"}')
            return

        if args.cmd == "prompt":
            manifest = utils.read_json(root / "ai_onboard.json", default={}) or {}
            ff = manifest.get("features") or {}
            if ff.get("prompt_bridge", True) is False:
                print('{"error":"prompt_bridge disabled"}')
                return
            pcmd = getattr(args, "prompt_cmd", None)
            if pcmd == "state":
                out = prompt_bridge.get_project_state(root)
                print(prompt_bridge.dumps_json(out))
                return
            if pcmd == "rules":
                out = prompt_bridge.get_applicable_rules(
                    root, target_path=args.path, change_summary=args.change
                )
                print(prompt_bridge.dumps_json(out))
                return
            if pcmd == "summary":
                out = prompt_bridge.summary(root, level=args.level)
                print(prompt_bridge.dumps_json(out))
                return
            if pcmd == "propose":
                out = prompt_bridge.propose_action(root, diff_json=args.diff)
                print(prompt_bridge.dumps_json(out))
                return
            print('{"error":"unknown prompt subcommand"}')
            return

        # Progress scanning command
        if args.cmd == "progress-scan":
            # Scan for completed tasks with gate confirmation
            from ..core.gate_system import GateSystem
            from ..core.task_completion_detector import run_task_completion_scan

            # Run task completion scan
            scan_results = run_task_completion_scan(root)

            if scan_results["scan_results"]["completed_tasks_detected"] > 0:
                print(
                    f"🎯 Found {scan_results['scan_results']['completed_tasks_detected']} completed tasks!"
                )

                # Use gate system for user confirmation
                gate_system = GateSystem(root)
                gate_id = "progress_scan_confirmation"

                # Create executive-level task descriptions function
                def get_task_descriptions(task_ids):
                    """Convert task IDs to executive-level descriptions."""
                    task_descriptions = {
                        # Core Infrastructure (T1-T7)
                        "T1": "Project Structure & Setup - Basic project foundation and directory structure",
                        "T2": "Development Environment Configuration - Python virtual environment and dependency management",
                        "T3": "CI/CD Pipeline Setup - GitHub Actions workflows for automated testing and deployment",
                        "T4": "Vision System Design - Core AI agent vision and alignment framework architecture",
                        "T5": "Vision Validation Logic - Quality scoring and validation for AI agent vision",
                        "T6": "Vision Implementation - Complete vision interrogation system deployment",
                        "T7": "AI Agent Collaboration - Multi-agent communication and orchestration protocols",
                        # System Robustness & Quality (T20-T24)
                        "T20": "Error Handling System - Automatic error interception and intelligent debugging",
                        "T22": "Learning Feedback Loops - Continuous improvement through system learning",
                        "T24": "Code Quality Standards - Black formatting and pre-commit hooks enforcement",
                        # Enhanced Testing Foundation (T29-T32)
                        "T29": "Advanced Test Metrics - Enhanced performance monitoring and confidence scoring",
                        "T30": "Intelligent Test Integration - SmartDebugger integration for error analysis",
                        "T31": "Performance Monitoring - Baseline monitoring and degradation alerts",
                        "T32": "Comprehensive Reporting - JSON/HTML reports with trend analysis",
                    }

                    descriptions = []
                    for task_id in task_ids:
                        if task_id in task_descriptions:
                            descriptions.append(
                                f"• {task_id}: {task_descriptions[task_id]}"
                            )
                        else:
                            descriptions.append(
                                f"• {task_id}: Task details not available"
                            )

                    return descriptions

                # Get executive-level task descriptions
                task_descriptions = get_task_descriptions(
                    scan_results["scan_results"]["completed_task_ids"]
                )

                questions = [
                    f"Confirm updating project plan with {scan_results['scan_results']['completed_tasks_detected']} detected task completions?",
                    f"This will update progress to ~{scan_results['progress_report']['overall_progress']['completion_percentage']:.1f}% completion.",
                    "Review the executive summary of completed work below:",
                ]

                # Use gate system for user confirmation
                from ..core.gate_system import GateRequest, GateType

                # Create GateRequest object for user confirmation
                gate_request = GateRequest(
                    gate_type=GateType.CONFIRMATION_REQUIRED,
                    title="Project Plan Update Confirmation",
                    description=f"Update project plan with {scan_results['scan_results']['completed_tasks_detected']} detected task completions",
                    context={
                        "scan_results": scan_results["scan_results"],
                        "progress_report": scan_results["progress_report"],
                        "completed_task_ids": scan_results["scan_results"][
                            "completed_task_ids"
                        ],
                        "executive_summary": {
                            "total_tasks_completed": scan_results["scan_results"][
                                "completed_tasks_detected"
                            ],
                            "new_progress_percentage": f"{scan_results['progress_report']['overall_progress']['completion_percentage']:.1f}%",
                            "task_descriptions": task_descriptions,
                            "categories": {
                                "infrastructure": len(
                                    [
                                        t
                                        for t in scan_results["scan_results"][
                                            "completed_task_ids"
                                        ]
                                        if t in ["T1", "T2", "T3"]
                                    ]
                                ),
                                "vision_system": len(
                                    [
                                        t
                                        for t in scan_results["scan_results"][
                                            "completed_task_ids"
                                        ]
                                        if t in ["T4", "T5", "T6", "T7"]
                                    ]
                                ),
                                "system_robustness": len(
                                    [
                                        t
                                        for t in scan_results["scan_results"][
                                            "completed_task_ids"
                                        ]
                                        if t in ["T20", "T22", "T24"]
                                    ]
                                ),
                                "testing_foundation": len(
                                    [
                                        t
                                        for t in scan_results["scan_results"][
                                            "completed_task_ids"
                                        ]
                                        if t in ["T29", "T30", "T31", "T32"]
                                    ]
                                ),
                            },
                        },
                    },
                    questions=questions,
                )

                gate_result = gate_system.create_gate(gate_request)
                print_content(
                    f"Gate created for user confirmation: {gate_id}", "status"
                )
                print("Please check .ai_onboard/gates/current_gate.md for questions")
                print("Run 'ai_onboard gate respond' after answering the questions")

            else:
                print_status("No new completed tasks detected", "success")

            return

        # Vision alignment commands
        if args.cmd == "vision":
            vcmd = getattr(args, "vision_cmd", None)
            if vcmd == "validate":
                # Validate decision alignment
                if hasattr(args, "decision") and args.decision:
                    decision_data = args.decision
                else:
                    decision_data = input("Enter decision data (JSON): ")
                try:
                    decision = json.loads(decision_data)
                    guardian = vision_guardian.get_vision_guardian(root)
                    result = guardian.validate_decision_alignment(decision)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print('{"error":"invalid JSON"}')
                return
            elif vcmd == "scope-change":
                # Propose scope change
                if hasattr(args, "change") and args.change:
                    change_data = args.change
                else:
                    change_data = input("Enter scope change request (JSON): ")
                try:
                    change_request = json.loads(change_data)
                    guardian = vision_guardian.get_vision_guardian(root)
                    result = guardian.propose_scope_change(change_request)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print('{"error":"invalid JSON"}')
                return
            elif vcmd == "update":
                # Update vision documents
                if hasattr(args, "update") and args.update:
                    updates_data = args.update
                else:
                    updates_data = input("Enter vision updates (JSON): ")
                try:
                    updates = json.loads(updates_data)
                    guardian = vision_guardian.get_vision_guardian(root)
                    result = guardian.update_vision_documents(updates)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print('{"error":"invalid JSON"}')
                return
            print('{"error":"unknown vision subcommand"}')
            return

        # Dynamic planning commands
        if args.cmd == "planning":
            pcmd = getattr(args, "planning_cmd", None)
            planner = dynamic_planner.get_dynamic_planner(root)

            if pcmd == "milestone":
                # Mark milestone complete
                if hasattr(args, "name") and args.name:
                    milestone_name = args.name
                else:
                    milestone_name = input("Enter milestone name: ")

                if hasattr(args, "completion") and args.completion:
                    completion_data = args.completion
                else:
                    completion_data = input("Enter completion data (JSON): ")

                try:
                    completion = json.loads(completion_data) if completion_data else {}
                    result = planner.mark_milestone_complete(milestone_name, completion)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print('{"error":"invalid JSON"}')
                return
            elif pcmd == "progress":
                # Update activity progress
                if hasattr(args, "activity_id") and args.activity_id:
                    activity_id = args.activity_id
                else:
                    activity_id = input("Enter activity ID: ")

                if hasattr(args, "progress") and args.progress:
                    progress_data = args.progress
                else:
                    progress_data = input("Enter progress data (JSON): ")

                try:
                    progress = json.loads(progress_data)
                    result = planner.update_activity_progress(activity_id, progress)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print('{"error":"invalid JSON"}')
                return
            elif pcmd == "auto-update":
                # Auto-update plan
                result = planner.auto_update_plan()
                print(prompt_bridge.dumps_json(result))
                return
            elif pcmd == "progress-scan":
                # Scan for completed tasks with gate confirmation
                from ..core.gate_system import GateSystem
                from ..core.task_completion_detector import run_task_completion_scan

                # Run task completion scan
                scan_results = run_task_completion_scan(root)

                if scan_results["scan_results"]["completed_tasks_detected"] > 0:
                    print(
                        f"🎯 Found {scan_results['scan_results']['completed_tasks_detected']} completed tasks!"
                    )

                    # Use gate system for user confirmation
                    gate_system = GateSystem(root)
                    gate_id = "progress_scan_confirmation"

                    questions = [
                        f"Confirm updating project plan with {scan_results['scan_results']['completed_tasks_detected']} detected task completions?",
                        "This will change progress from 0% to ~20.8% completion.",
                        "Review the detected completions before proceeding?",
                    ]

                    # Create gate for user confirmation
                    gate_data = {
                        "gate_id": gate_id,
                        "questions": questions,
                        "context": {
                            "scan_results": scan_results["scan_results"],
                            "progress_report": scan_results["progress_report"],
                            "completed_task_ids": scan_results["scan_results"][
                                "completed_task_ids"
                            ],
                        },
                    }

                    # Submit gate for user confirmation
                    gate_result = gate_system.submit_gate(gate_data)
                    print(f"📋 Gate created for user confirmation: {gate_id}")
                    print(
                        "Please check .ai_onboard/gates/current_gate.md for questions"
                    )
                    print("Run 'ai_onboard gate respond' after answering the questions")

                else:
                    print_status("No new completed tasks detected", "success")

                return
            elif pcmd == "add-milestone":
                # Add new milestone
                if hasattr(args, "milestone") and args.milestone:
                    milestone_data = args.milestone
                else:
                    milestone_data = input("Enter milestone data (JSON): ")
                try:
                    milestone = json.loads(milestone_data)
                    result = planner.add_new_milestone(milestone)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print('{"error":"invalid JSON"}')
                return
            print('{"error":"unknown planning subcommand"}')
            return

        # Smart debugging commands
        if args.cmd == "debug":
            dcmd = getattr(args, "debug_cmd", None)
            debugger = smart_debugger.get_smart_debugger(root)

            if dcmd == "analyze":
                # Analyze error
                if hasattr(args, "error") and args.error:
                    error_data = args.error
                else:
                    error_data = input("Enter error data (JSON): ")
                try:
                    error = json.loads(error_data)
                    result = debugger.analyze_error(error)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print('{"error":"invalid JSON"}')
                return
            elif dcmd == "improve":
                # Improve patterns
                result = debugger.improve_patterns()
                print(prompt_bridge.dumps_json(result))
                return
            elif dcmd == "stats":
                # Show statistics
                result = debugger.get_debugging_stats()
                print(prompt_bridge.dumps_json(result))
                return
            print('{"error":"unknown debug subcommand"}')
            return

        # Context continuity commands
        if args.cmd == "context":
            ccmd = getattr(args, "context_cmd", None)
            context_manager = context_continuity.get_context_continuity_manager(root)

            if ccmd == "summary":
                # Get context summary
                if hasattr(args, "level") and args.level:
                    level = args.level
                else:
                    level = (
                        input("Enter summary level (brief/full): ").strip() or "brief"
                    )
                result = context_manager.get_context_summary(level)
                print(prompt_bridge.dumps_json(result))
                return
            elif ccmd == "drift":
                # Check for drift
                result = context_manager.check_context_drift()
                print(prompt_bridge.dumps_json(result))
                return
            elif ccmd == "resolve":
                # Resolve drift
                if hasattr(args, "drift_type") and args.drift_type:
                    drift_type = args.drift_type
                else:
                    drift_type = input("Enter drift type: ")

                if hasattr(args, "resolution") and args.resolution:
                    resolution_data = args.resolution
                else:
                    resolution_data = input("Enter resolution data (JSON): ")

                try:
                    resolution = json.loads(resolution_data) if resolution_data else {}
                    result = context_manager.resolve_context_drift(
                        drift_type, resolution
                    )
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print('{"error":"invalid JSON"}')
                return
            print('{"error":"unknown context subcommand"}')
            return

        # Vision interrogation commands
        if args.cmd == "interrogate":
            icmd = getattr(args, "interrogate_cmd", None)
            interrogator = vision_interrogator.get_vision_interrogator(root)

            if icmd == "check":
                # Check vision readiness
                result = interrogator.check_vision_readiness()
                print(prompt_bridge.dumps_json(result))
                return
            elif icmd == "start":
                # Start interrogation
                result = interrogator.start_interrogation()
                print(prompt_bridge.dumps_json(result))
                return
            elif icmd == "submit":
                # Submit response
                if (
                    hasattr(args, "phase")
                    and hasattr(args, "question_id")
                    and hasattr(args, "response")
                ):
                    # Use command line arguments if provided
                    phase = args.phase
                    question_id = args.question_id
                    response_data = args.response
                else:
                    # Fall back to interactive input
                    phase = input("Enter phase: ")
                    question_id = input("Enter question ID: ")
                    response_data = input("Enter response (JSON): ")

                try:
                    response = json.loads(response_data)
                    result = interrogator.submit_response(phase, question_id, response)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print('{"error":"invalid JSON"}')
                return
            elif icmd == "questions":
                # Get current questions
                result = interrogator.get_current_questions()
                print(prompt_bridge.dumps_json(result))
                return
            elif icmd == "summary":
                # Get interrogation summary
                result = interrogator.get_interrogation_summary()
                print(prompt_bridge.dumps_json(result))
                return
            elif icmd == "force-complete":
                # Force complete interrogation
                result = interrogator.force_complete_interrogation()
                print(prompt_bridge.dumps_json(result))
                return
            print('{"error":"unknown interrogate subcommand"}')
            return

        # User preference learning commands
        if args.cmd == "user-prefs":
            from ..core import user_preference_learning as upl

            psys = upl.get_user_preference_learning_system(root)
            pcmd = getattr(args, "prefs_cmd", None)

            if pcmd == "record":
                user_id = args.user
                interaction_type = args.type
                try:
                    context = json.loads(args.context) if args.context else {}
                except json.JSONDecodeError:
                    print('{"error":"invalid context JSON"}')
                    return
                try:
                    outcome = json.loads(args.outcome) if args.outcome else {}
                except json.JSONDecodeError:
                    print('{"error":"invalid outcome JSON"}')
                    return
                interaction_id = psys.record_user_interaction(
                    user_id=user_id,
                    interaction_type=interaction_type,
                    context=context,
                    duration=getattr(args, "duration", None),
                    outcome=outcome,
                    satisfaction_score=getattr(args, "satisfaction", None),
                    feedback=getattr(args, "feedback", None),
                )
                print(prompt_bridge.dumps_json({"interaction_id": interaction_id}))
                return
            elif pcmd == "summary":
                user_id = args.user
                out = psys.get_user_profile_summary(user_id)
                print(prompt_bridge.dumps_json(out))
                return
            elif pcmd == "recommend":
                user_id = args.user
                recs = psys.get_user_recommendations(user_id)
                print(prompt_bridge.dumps_json({"recommendations": recs}))
                return
            print('{"error":"unknown user-prefs subcommand"}')
            return

        # UI/UX Design commands
        if args.cmd == "design":
            dcmd = getattr(args, "design_cmd", None)

            if dcmd == "analyze":
                # Analyze UI design from screenshot
                screenshot_path = args.screenshot
                project_context = charter.load_charter(root)
                result = visual_design.analyze_ui_design(
                    screenshot_path, project_context
                )
                print(prompt_bridge.dumps_json(result))
                return
            elif dcmd == "validate":
                # Validate design decision
                description = args.description
                project_context = charter.load_charter(root)
                result = visual_design.validate_design_decision(
                    description, project_context
                )
                print(prompt_bridge.dumps_json(result))
                return
            elif dcmd == "consistency":
                # Check design consistency
                description = args.description
                result = design_system.validate_design_consistency(
                    description, str(root)
                )
                print(prompt_bridge.dumps_json(result))
                return
            elif dcmd == "system":
                # Design system management
                scmd = getattr(args, "system_cmd", None)

                if scmd == "summary":
                    result = design_system.get_design_system_summary(str(root))
                    print(prompt_bridge.dumps_json(result))
                    return
                elif scmd == "tokens":
                    # TODO: Implement token listing
                    print('{"message":"Token listing not yet implemented"}')
                    return
                elif scmd == "components":
                    # TODO: Implement component listing
                    print('{"message":"Component listing not yet implemented"}')
                    return
                elif scmd == "patterns":
                    # TODO: Implement pattern listing
                    print('{"message":"Pattern listing not yet implemented"}')
                    return
                print('{"error":"unknown system subcommand"}')
                return
            print('{"error":"unknown design subcommand"}')
            return

        if args.cmd == "cleanup":
            print_activity("Scanning for files to clean up...", "search")

            # Always start with dry-run to show what would be deleted
            result = cleanup.safe_cleanup(root, dry_run=True)

            print_content("Scan Results:", "stats")
            safe_print(
                f"  [PROTECTED] Protected (critical): {result['protected']} files"
            )
            safe_print(f"  [DELETE] Would delete: {result['would_delete']} files")
            safe_print(f"  [UNKNOWN] Unknown: {result['unknown']} files")

            if result["would_delete"] == 0:
                print("\n✨ No files to clean up!")
                return

            if args.dry_run:
                print_activity("DRY RUN MODE - No files will be deleted", "search")
                print("Files that would be deleted:")
                for path in result["scan_result"]["non_critical"][:10]:  # Show first 10
                    print(f"  - {path.relative_to(root)}")
                if len(result["scan_result"]["non_critical"]) > 10:
                    print(
                        f"  ... and {len(result['scan_result']['non_critical']) - 10} more"
                    )
                return

            # Real cleanup mode
            if not args.force:
                response = input(
                    f"\n⚠️  Are you sure you want to delete {result['would_delete']} files? (y/N): "
                )
                if response.lower() != "y":
                    print_status("Cleanup cancelled.", "error")
                    return

            # Create backup if requested
            if args.backup:
                print("💾 Creating backup...")
                backup_dir = cleanup.create_backup(root)
                print_status(f"Backup created at: {backup_dir}", "success")

            print("🧹 Performing cleanup...")
            result = cleanup.safe_cleanup(root, dry_run=False)

            print_status("Cleanup completed!", "success")
            safe_print(f"  [DELETED] Deleted: {result['deleted_count']} files")
            if result["errors"]:
                safe_print(
                    f"  [WARN] Errors: {len(result['errors'])} files failed to delete"
                )
                for error in result["errors"][:5]:
                    safe_print(f"    - {error}")
            return

        # Cleanup Safety Gates
        if args.cmd == "cleanup-safety":
            handle_cleanup_safety_commands(args, root)
            return

    except state.StateError as e:
        print(e)
        return
    except Exception as e:
        # Catch-all to avoid stack traces surfacing to users for known flows
        print(e)
        return
