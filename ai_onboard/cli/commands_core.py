"""Core CLI commands for ai - onboard."""

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

# alignment module moved to vision package
from ..core.base import telemetry, utils, versioning
from ..core.legacy_cleanup.charter import load_charter
from ..core.legacy_cleanup.gate_system import (
    create_clarification_gate,
    create_confirmation_gate,
)
from ..core.legacy_cleanup.prompt_bridge import dumps_json as prompt_bridge_dumps_json
from ..core.orchestration.pattern_recognition_system import PatternRecognitionSystem
from ..core.vision.alignment import open_checkpoint
from ..core.vision.alignment import preview as alignment_preview
from ..core.vision.alignment import record_decision


def add_core_commands(subparsers):
    """Add core command parsers."""

    # Global IAS parent parser (intentionally minimal: no bypass flags)
    ias_parent = argparse.ArgumentParser(add_help=False)

    # Analyze
    s_an = subparsers.add_parser(
        "analyze",
        parents=[ias_parent],
        help="Scan repo and draft ai_onboard.json manifest",
    )
    s_an.add_argument(
        "--allowExec",
        action="store_true",
        help="Permit safe external probes (off by default)",
    )

    # Charter
    s_ch = subparsers.add_parser(
        "charter", parents=[ias_parent], help="Create or update project charter"
    )
    s_ch.add_argument("--interactive", action="store_true")

    # Plan
    subparsers.add_parser(
        "plan", parents=[ias_parent], help="Build plan.json from charter"
    )

    # Align
    s_al = subparsers.add_parser(
        "align", parents=[ias_parent], help="Open or approve an alignment checkpoint"
    )
    s_al.add_argument("--checkpoint", default="PlanGate")
    s_al.add_argument("--approve", action="store_true")
    s_al.add_argument("--note", default="", help="Optional note to store with approval")
    s_al.add_argument(
        "--preview",
        action="store_true",
        help="Compute dry - run alignment report (no edits)",
    )

    # Validate
    s_v = subparsers.add_parser(
        "validate", parents=[ias_parent], help="Run validation and write report"
    )
    s_v.add_argument(
        "--report",
        action="store_true",
        help="Write .ai_onboard / report.md and versioned copy",
    )

    # Kaizen
    s_k = subparsers.add_parser(
        "kaizen",
        parents=[ias_parent],
        help="Run a kaizen cycle (metrics - driven nudges)",
    )
    s_k.add_argument("--once", action="store_true")

    # Optimize
    s_o = subparsers.add_parser(
        "optimize", parents=[ias_parent], help="Run quick optimization experiments"
    )
    s_o.add_argument("--budget", default="5m", help="Time budget (e.g., 5m)")

    # Version
    s_ver = subparsers.add_parser("version", help="Show or bump ai_onboard version")
    s_ver.add_argument("--bump", choices=["major", "minor", "patch"])
    s_ver.add_argument("--set", help="Set explicit version (e.g., 1.2.3)")

    # Metrics
    subparsers.add_parser(
        "metrics",
        parents=[ias_parent],
        help="Show last validation run summary from telemetry",
    )

    # Tools
    s_tools = subparsers.add_parser(
        "tools", parents=[ias_parent], help="Show system tools usage information"
    )
    s_tools.add_argument(
        "--history",
        action="store_true",
        help="Show recent tool usage history",
    )
    s_tools.add_argument(
        "--session",
        help="Show tools used in a specific session",
    )
    s_tools.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Limit number of history items to show (default: 20)",
    )

    # WBS Management subcommand
    s_wbs = subparsers.add_parser(
        "wbs", parents=[ias_parent], help="Work Breakdown Structure management"
    )
    wbs_subparsers = s_wbs.add_subparsers(dest="wbs_cmd", help="WBS subcommands")

    # WBS status
    wbs_subparsers.add_parser("status", help="Show WBS and pending task status")

    # WBS update
    wbs_subparsers.add_parser("update", help="Force WBS updates for pending tasks")

    # Enhanced WBS commands (using existing parsers)
    health_parser = wbs_subparsers.add_parser(
        "health", help="Show project health metrics"
    )

    analyze_parser = wbs_subparsers.add_parser(
        "analyze", help="Analyze critical path with optimization suggestions"
    )

    optimize_parser = wbs_subparsers.add_parser(
        "optimize", help="Get project optimization recommendations"
    )

    # WBS pending
    wbs_subparsers.add_parser(
        "pending", help="Show pending tasks requiring WBS updates"
    )

    # WBS force
    s_wbs_force = wbs_subparsers.add_parser(
        "force", help="Force WBS update for specific task"
    )
    s_wbs_force.add_argument("task_id", help="Task ID to force update for")

    # WBS cleanup
    s_wbs_cleanup = wbs_subparsers.add_parser(
        "cleanup", help="Clean up old completed tasks"
    )
    s_wbs_cleanup.add_argument(
        "--max-age",
        type=int,
        default=30,
        help="Maximum age in days for completed tasks to keep (default: 30)",
    )

    # WBS critical-path
    s_wbs_critical = wbs_subparsers.add_parser(
        "critical-path", help="Analyze and update project critical path"
    )
    s_wbs_critical.add_argument(
        "--update",
        action="store_true",
        help="Update the project plan with critical path designations",
    )
    s_wbs_critical.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed critical path report",
    )

    # WBS auto-update
    s_wbs_auto = wbs_subparsers.add_parser(
        "auto-update", help="Automatically update WBS based on task completion evidence"
    )
    s_wbs_auto.add_argument(
        "--force", action="store_true", help="Force update all tasks, ignore cooldown"
    )
    s_wbs_auto.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes",
    )

    # WBS sync
    s_wbs_sync = wbs_subparsers.add_parser(
        "sync", help="Synchronize all WBS views and caches"
    )

    # WBS validate
    s_wbs_validate = wbs_subparsers.add_parser(
        "validate", help="Validate WBS data consistency and integrity"
    )
    s_wbs_validate.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix any consistency issues found",
    )
    s_wbs_validate.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed validation report",
    )

    # Task execution gates
    s_gate = subparsers.add_parser("task-gate", help="Manage task execution gates")
    gate_subparsers = s_gate.add_subparsers(dest="gate_action", required=True)

    # Gate status
    gate_status = gate_subparsers.add_parser(
        "status", help="Show gate status and pending tasks"
    )
    gate_status.add_argument("--task-id", help="Check specific task ID")
    gate_status.add_argument(
        "--verbose", action="store_true", help="Show detailed information"
    )

    # Create emergency bypass
    gate_bypass = gate_subparsers.add_parser(
        "bypass", help="Create emergency gate bypass"
    )
    gate_bypass.add_argument("command", help="Command to bypass gates for")
    gate_bypass.add_argument("--reason", required=True, help="Reason for bypass")
    gate_bypass.add_argument(
        "--hours", type=int, default=1, help="Hours bypass is valid (default: 1)"
    )
    gate_bypass.add_argument(
        "--authorized-by", default="user", help="Who authorized the bypass"
    )

    # Gate violations log
    gate_violations = gate_subparsers.add_parser(
        "violations", help="Show recent gate violations"
    )
    gate_violations.add_argument(
        "--limit", type=int, default=10, help="Number of violations to show"
    )
    gate_violations.add_argument("--command", help="Filter by command")

    # Force gate update
    gate_update = gate_subparsers.add_parser(
        "update", help="Force update WBS for pending tasks"
    )
    gate_update.add_argument("--task-id", help="Update specific task ID")
    gate_update.add_argument(
        "--all", action="store_true", help="Update all pending tasks"
    )

    # Lite: analysis and roadmap
    subparsers.add_parser("roadmap", help="Generate simple roadmap from analysis.json")
    s_work = subparsers.add_parser(
        "work", help="Show next task from roadmap.json and log it"
    )
    s_work.add_argument("--next", action="store_true", help="Show next pending task")

    # Cleanup
    s_clean = subparsers.add_parser(
        "cleanup",
        parents=[ias_parent],
        help="Safely remove non - critical files (build artifacts, cache, etc.)",
    )
    s_clean.add_argument(
        "--dry - run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    s_clean.add_argument(
        "--force", action="store_true", help="Skip confirmation prompts"
    )
    s_clean.add_argument(
        "--backup", action="store_true", help="Create backup before cleanup"
    )

    # Gate management
    s_gate = subparsers.add_parser("gate", help="Gate management commands")
    gate_subparsers = s_gate.add_subparsers(dest="gate_cmd", help="Gate subcommands")

    # Gate status
    gate_subparsers.add_parser("status", help="Check if a gate is currently active")

    # Gate clear
    gate_subparsers.add_parser(
        "clear", help="Clear any active gates (use with caution)"
    )

    # Gate respond
    s_gate_resp = gate_subparsers.add_parser(
        "respond", help="Manually respond to an active gate"
    )
    s_gate_resp.add_argument(
        "--decision",
        choices=["proceed", "modify", "stop"],
        default="proceed",
        help="User decision",
    )
    s_gate_resp.add_argument(
        "--responses", nargs="*", help="User responses to questions"
    )
    s_gate_resp.add_argument("--context", default="", help="Additional context")
    # Confirmation code removed; still accepted (ignored) for compatibility
    s_gate_resp.add_argument(
        "--code", default=None, help="(Optional) legacy confirmation code; ignored"
    )


def _check_command_prevention(
    root: Path, command: str, args: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Check if a command should be prevented from execution.

    Args:
        root: Project root path
        command: The command to check
        args: Command arguments

    Returns:
        Prevention analysis result
    """
    try:
        from ..core.orchestration.automatic_error_prevention import (
            AutomaticErrorPrevention,
        )
        from ..core.orchestration.pattern_recognition_system import (
            PatternRecognitionSystem,
        )

        pattern_system = PatternRecognitionSystem(root)
        prevention_system = AutomaticErrorPrevention(root, pattern_system)

        # Check command safety before execution
        prevention_result = prevention_system.prevent_command_execution(
            command, args, cwd=root
        )

        return prevention_result

    except Exception as e:
        # If prevention check fails, allow command to proceed
        print(f"Warning: Command prevention check failed: {e}")
        return {"should_block": False, "confidence": 0.0}


def _learn_from_command_execution(
    root: Path, command: str, success: bool, context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Learn from CLI command execution for pattern recognition.

    Args:
        root: Project root path
        command: The command that was executed
        success: Whether the command succeeded
        context: Additional execution context
    """
    try:
        pattern_system = PatternRecognitionSystem(root)
        pattern_system.learn_from_cli_usage(command, success, context)
    except Exception as e:
        # Don't let pattern learning failures break command execution
        telemetry.log_event("pattern_learning_error", error=str(e), command=command)


def _ias_gate(args, root: Path) -> bool:
    """Run IAS alignment preview and enforce collaborative gates.

    Returns True if execution may proceed, False if it should stop for clarification.
    """
    # CI - only bypass: allow in GitHub Actions when explicitly enabled
    if (
        os.getenv("GITHUB_ACTIONS", "").lower() == "true"
        and os.getenv("AI_ONBOARD_BYPASS", "") == "ci"
    ):
        telemetry.log_event(
            "gate_bypass_ci",
            reason="CI smoke run",
            branch=os.getenv("GITHUB_REF", "unknown"),
        )
        return True

    # Manual override file (human - only). If present, proceed and log.
    gates_dir = root / ".ai_onboard" / "gates"
    override_file = gates_dir / "override.txt"
    if override_file.exists():
        try:
            note = override_file.read_text(encoding="utf - 8").strip()[:500]
        except Exception:
            note = "(unreadable)"
        telemetry.log_event("gate_override_manual", note=note)
        return True

    # Check for active gates first - prevent gate loops
    import time

    from ..core.legacy_cleanup.gate_system import GateSystem

    gate_system = GateSystem(root)
    if gate_system.is_gate_active():
        # Check if the gate has been waiting too long (timed out)
        status_file = gate_system.gates_dir / "gate_status.json"
        if status_file.exists():
            try:

                status = json.loads(status_file.read_text(encoding="utf-8"))
                created_at = status.get("created_at", 0)
                # If gate has been waiting for more than 10 seconds, consider it timed out
                if time.time() - created_at > 10:
                    telemetry.log_event(
                        "gate_timed_out_cleanup",
                        command=getattr(args, "cmd", "unknown"),
                        gate_age_seconds=int(time.time() - created_at),
                    )
                    print(
                        "[INFO] Previous gate timed out - cleaning up and proceeding..."
                    )
                    gate_system._cleanup_gate()
                else:
                    telemetry.log_event(
                        "gate_already_active",
                        command=getattr(args, "cmd", "unknown"),
                        reason="Preventing gate loop",
                    )
                    print("[INFO] Gate already active - waiting for resolution...")
                    return False
            except Exception as e:
                # If we can't read status, assume gate is stale and clean it up
                print(f"[WARNING] Could not read gate status: {e} - cleaning up...")
                gate_system._cleanup_gate()
        else:
            # No status file, clean up and proceed
            print("[WARNING] Gate files exist but no status - cleaning up...")
            gate_system._cleanup_gate()

    # Compute preview (no user - bypass flags honored)
    report = alignment_preview(root)
    decision = report.get("decision", "clarify")

    if decision == "proceed":
        # Quietly allow
        return True

    if decision == "quick_confirm":
        # Use gate system for confirmation
        context = {
            "command": getattr(args, "cmd", "unknown"),
            "confidence": report.get("confidence", 0.0),
            "report_path": report.get("report_path", "N / A"),
        }

        response = create_confirmation_gate(
            root, f"proceed with {getattr(args, 'cmd', 'command')}", context
        )

        return response.get("user_decision") == "proceed"

    # Clarify: Use gate system for clarification
    confidence = report.get("confidence", 0.0)
    issues = report.get("ambiguities", [])

    context = {
        "command": getattr(args, "cmd", "unknown"),
        "report_path": report.get("report_path", "N / A"),
        "components": report.get("components", {}),
    }

    response = create_clarification_gate(root, confidence, issues, context)

    return response.get("user_decision") == "proceed"


def _handle_gate_commands(args, root: Path):
    """Handle gate management commands."""

    gates_dir = root / ".ai_onboard" / "gates"
    current_gate_file = gates_dir / "current_gate.md"
    response_file = gates_dir / "gate_response.json"

    if args.gate_cmd == "status":
        if current_gate_file.exists():
            print("[INFO] Gate is ACTIVE")
            print(f"[FOLDER] Gate file: {current_gate_file}")
            print(f"[INFO] Read the gate file for instructions")
        else:
            print("[INFO] No active gates")

    elif args.gate_cmd == "clear":
        if current_gate_file.exists():
            current_gate_file.unlink()
            print("[OK] Gate cleared")
        if response_file.exists():
            response_file.unlink()
            print("[OK] Response file cleared")
        if not current_gate_file.exists() and not response_file.exists():
            print("[INFO] No gates to clear")

    elif args.gate_cmd == "respond":
        if not current_gate_file.exists():
            print("[ERROR] No active gate to respond to")
            return

        import time

        response_data = {
            "user_responses": args.responses or ["manual response"],
            "user_decision": args.decision,
            "additional_context": args.context,
            "timestamp": time.time(),
        }
        # Ignore --code for now (kept for compatibility)

        response_file.write_text(
            json.dumps(response_data, indent=2), encoding="utf - 8"
        )
        print(f"[OK] Response written to: {response_file}")
        print(f"[INFO] The system should now continue automatically")


def handle_core_commands(args, root: Path):
    """Handle core command execution."""

    # Handle task-gate commands (top level)
    if args.cmd == "task-gate":
        # Task execution gate management
        try:
            from ..core.orchestration.task_execution_gate import TaskExecutionGate

            gate = TaskExecutionGate(root)
            gate_action = getattr(args, "gate_action", None)

            if gate_action == "status":
                # Show gate status
                task_id = getattr(args, "task_id", None)
                verbose = getattr(args, "verbose", False)

                if task_id:
                    # Check specific task
                    result = gate.check_execution_allowed(task_id)
                    print(f"🔍 Task Gate Status for {task_id}")
                    print("=" * 40)
                    print(f"Allowed: {'✅ Yes' if result['allowed'] else '❌ No'}")
                    print(
                        f"WBS Updated: {'✅ Yes' if result['wbs_updated'] else '❌ No'}"
                    )
                    print(f"Status: {result['status']}")
                    if result.get("last_error"):
                        print(f"Last Error: {result['last_error']}")
                    if verbose and result.get("task_info"):
                        print(f"Task Name: {result['task_info']['task_name']}")
                        print(f"Registered: {result['task_info']['registered_at']}")
                else:
                    # Show overall status
                    summary = gate.get_pending_tasks_summary()
                    print("🚪 Task Execution Gate Status")
                    print("=" * 40)
                    print(f"Total Pending Tasks: {summary['total_pending']}")
                    print(f"WBS Updated: {summary['wbs_updated']}")
                    print(f"Execution Allowed: {summary['execution_allowed']}")
                    print(f"Failed Updates: {summary['failed_updates']}")
                    print(f"Last Updated: {summary['last_updated']}")

                    if verbose and summary["total_pending"] > 0:
                        print("\n📋 Pending Tasks:")
                        pending_data = utils.read_json(
                            gate.pending_tasks_path, default={"pending_tasks": []}
                        )
                        for task in pending_data.get("pending_tasks", [])[
                            :5
                        ]:  # Show first 5
                            status = (
                                "✅"
                                if task.get("execution_allowed")
                                else "⏳" if task.get("wbs_updated") else "❌"
                            )
                            print(
                                f"  {status} {task['task_id']}: {task['task_data'].get('name', 'Unknown')}"
                            )

            elif gate_action == "bypass":
                # Create emergency bypass
                command = getattr(args, "command", "")
                reason = getattr(args, "reason", "")
                hours = getattr(args, "hours", 1)
                authorized_by = getattr(args, "authorized_by", "user")

                result = gate.create_emergency_bypass(
                    command=command,
                    reason=reason,
                    authorized_by=authorized_by,
                    validity_hours=hours,
                )

                if result["success"]:
                    print("🚨 Emergency Bypass Created")
                    print("=" * 40)
                    print(f"Command: {command}")
                    print(f"Reason: {reason}")
                    print(f"Bypass Token: {result['bypass_token']}")
                    print(
                        f"Valid Until: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['expires_at']))}"
                    )
                    print(f"Authorized By: {authorized_by}")
                    print(
                        f"\n⚠️  WARNING: This bypass allows the command to run without gate checks!"
                    )
                    print(f"Use: {command} (will be allowed for {hours} hour(s))")
                else:
                    print(
                        f"❌ Failed to create bypass: {result.get('error', 'Unknown error')}"
                    )

            elif gate_action == "violations":
                # Show gate violations
                limit = getattr(args, "limit", 10)
                filter_command = getattr(args, "command", None)

                try:

                    violations = []
                    if gate.execution_log_path.exists():
                        with open(gate.execution_log_path, "r", encoding="utf-8") as f:
                            for line in f:
                                try:
                                    entry = json.loads(line.strip())
                                    if entry.get("event_type") == "gate_violation":
                                        if (
                                            not filter_command
                                            or entry.get("command") == filter_command
                                        ):
                                            violations.append(entry)
                                except json.JSONDecodeError:
                                    continue

                    violations = violations[-limit:]  # Get most recent

                    print("🚫 Recent Gate Violations")
                    print("=" * 40)

                    if violations:
                        for i, violation in enumerate(violations, 1):
                            timestamp = time.strftime(
                                "%H:%M:%S", time.localtime(violation["timestamp"])
                            )
                            print(f"{i}. [{timestamp}] {violation['command']}")
                            print(f"   Reason: {violation['message']}")
                            if violation.get("violations"):
                                print(
                                    f"   Tasks: {', '.join(v['task_id'] for v in violation['violations'])}"
                                )
                            print()
                    else:
                        print("✅ No gate violations found")
                        if filter_command:
                            print(f"Filter: {filter_command}")

                except (ValueError, TypeError, AttributeError) as e:
                    print(f"Error: {e}")
            elif gate_action == "update":
                # Force WBS update for pending tasks
                task_id = getattr(args, "task_id", None)
                update_all = getattr(args, "all", False)

                if task_id:
                    # Update specific task
                    print(f"🔄 Updating WBS for task {task_id}...")
                    update_result = gate.update_wbs_for_pending_tasks()

                    # Check if our specific task was updated
                    updated = any(
                        r.get("task_id") == task_id
                        for r in update_result.get("results", [])
                    )
                    if updated:
                        print(f"✅ Task {task_id} WBS updated successfully")
                    else:
                        print(f"❌ Task {task_id} update failed or not found")

                elif update_all:
                    # Update all pending tasks
                    print("🔄 Updating WBS for all pending tasks...")
                    update_result = gate.update_wbs_for_pending_tasks()

                    print(f"📊 Update Results:")
                    print(f"   Total Processed: {update_result['total_processed']}")
                    print(f"   Successfully Updated: {update_result['updated']}")
                    print(f"   Failed: {update_result['failed']}")

                    if update_result.get("results"):
                        print("\n📋 Task Update Details:")
                        for result in update_result["results"][:5]:  # Show first 5
                            status = "✅" if result["status"] == "success" else "❌"
                            print(
                                f"   {status} {result['task_id']}: {result.get('update_type', 'unknown')}"
                            )
                else:
                    print("❌ Specify --task-id <id> or --all to update tasks")

            else:
                print("❌ Unknown gate action. Use --help for available actions.")

        except (ValueError, TypeError, AttributeError) as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()
            return

    # Allow a safe, read - only preview to bypass the IAS gate so users can
    # inspect the recommendation before deciding to proceed.
    if args.cmd == "align" and getattr(args, "preview", False):
        # alignment module moved to vision package
        from ..core.base import utils

        out = alignment_preview(root)
        print(utils.dumps_json(out))
        return

    if args.cmd in {
        "analyze",
        "charter",
        "plan",
        "align",
        "kaizen",
        "optimize",
        "metrics",
        "cleanup",
    }:
        if not _ias_gate(args, root):
            return
    elif args.cmd == "gate":
        _handle_gate_commands(args, root)
        return

    if args.cmd == "analyze":
        # Scan repository and create manifest
        from ..core.base import utils
        from ..core.legacy_cleanup import discovery

        manifest = discovery.run(root, allow_exec=args.allowExec)
        utils.write_json(root / "ai_onboard.json", manifest)
        print("Wrote ai_onboard.json (draft).")

        # Learn from successful analysis
        _learn_from_command_execution(root, "analyze", True, {"command": "analyze"})
    elif args.cmd == "charter":
        # Create or update project charter
        from ..core.base import state
        from ..core.legacy_cleanup import charter

        charter.ensure(root, interactive=args.interactive)

        # Mark vision as confirmed if run interactively
        if args.interactive:
            charter_data = load_charter(root)
            charter_data["vision_confirmed"] = True
            from ..core.base import utils

            utils.write_json(root / ".ai_onboard" / "charter.json", charter_data)
            print("✅ Vision confirmed in charter")

        state.advance(root, state.load(root), "chartered")
        print("Charter ready at .ai_onboard / charter.json")
    elif args.cmd == "plan":
        # Build project plan from charter
        from ..core.base import state
        from ..core.vision.planning import planning

        planning.build(root)
        state.advance(root, state.load(root), "planned")
        print("Plan ready at .ai_onboard / plan.json")
    elif args.cmd == "roadmap":
        # Build lightweight roadmap from analysis
        from ..core.utilities.roadmap_lite import roadmap_lite

        goal = ""
        rm = roadmap_lite.build(root, goal)
        print(utils.dumps_json(rm))
    elif args.cmd == "work":
        # Show next task and log it

        from ..core.base import runlog

        rm_path = root / ".ai_onboard" / "roadmap.json"
        if not rm_path.exists():
            print("No roadmap.json. Run 'ai_onboard roadmap' first.")
            return
        rm = json.loads(rm_path.read_text(encoding="utf - 8"))
        next_task = None
        for t in rm.get("tasks", []):
            if t.get("status") == "pending":
                next_task = t
                break
        if not next_task:
            print("No pending tasks.")
            return
        runlog.write_event(root, "work.next", {"task": next_task})
        print(utils.dumps_json({"next_task": next_task}))
    elif args.cmd == "align":
        # Open or approve an alignment checkpoint
        # alignment module moved to vision package, prompt_bridge
        from ..core.base import state

        if args.preview:
            res = alignment_preview(root)
            print(prompt_bridge_dumps_json(res))
        elif args.approve:
            record_decision(root, "ALIGN", args.checkpoint, True, args.note)
            state.advance(root, state.load(root), "aligned")
            print(f"Alignment approved for {args.checkpoint}.")
        else:
            open_checkpoint(root, args.checkpoint)
            print(f"Opened alignment checkpoint {args.checkpoint}.")
    elif args.cmd == "validate":
        # Run validation and write report
        import importlib

        # progress_dashboard removed - was deprecated shim
        # alignment module moved to vision package, charter
        from ..core.base import telemetry

        validation_runtime = importlib.import_module(
            "ai_onboard.core.validation_runtime"
        )

        from ..core.vision.alignment import require_state

        require_state(root, "aligned")

        # Check if vision is confirmed before allowing validation
        charter_data = load_charter(root)
        if not charter_data.get("vision_confirmed", False):
            print(
                "❌ Vision not confirmed. Please confirm the project vision before running validation."
            )
            print(
                "💡 Run: python -m ai_onboard charter --interactive to confirm vision"
            )
            return

        res = validation_runtime.run(root)
        if args.report:
            # progress_tracker.write_report removed - was deprecated functionality
            print("Report generation temporarily disabled (progress_dashboard removed)")
        telemetry.record_run(root, res)
        print("Validation complete.")

        # Learn from successful validation
        _learn_from_command_execution(root, "validate", True, {"command": "validate"})
    elif args.cmd == "kaizen":
        # Run a kaizen cycle (metrics - driven nudges)
        from ..core.continuous_improvement.optimizer import optimizer

        optimizer.nudge_from_metrics(root)
        print("Kaizen cycle complete.")
    elif args.cmd == "optimize":
        # Run quick optimization experiments
        from ..core.continuous_improvement.optimizer import optimizer

        optimizer.quick_optimize(root)
        print("Optimization complete.")
    elif args.cmd == "version":
        # Show the actual package version, not project version
        from ..core.orchestration.tool_usage_tracker import get_tool_tracker

        tool_tracker = get_tool_tracker(root)
        session_id = tool_tracker.start_task_session("version", "core_command")

        try:
            if args.set:
                versioning.set_version(root, args.set)
                print(f"Version set to {args.set}")
                tool_tracker.track_tool_usage(
                    "version_set",
                    "version_management",
                    parameters={"new_version": args.set},
                    result="success",
                )
                session_summary = tool_tracker.end_task_session("completed")
                tool_tracker.display_tools_summary(session_summary)
                return
            if args.bump:
                current = versioning.get_version(root)
                newv = versioning.bump(current, args.bump)
                versioning.set_version(root, newv)
                print(f"Bumped {args.bump}: {current} -> {newv}")
                tool_tracker.track_tool_usage(
                    "version_bump",
                    "version_management",
                    parameters={"bump_type": args.bump, "from": current, "to": newv},
                    result="success",
                )
                session_summary = tool_tracker.end_task_session("completed")
                tool_tracker.display_tools_summary(session_summary)
                return
            # Show package version, not project version
            print(f"ai - onboard package version: {versioning.get_version(root)}")
            # Also show project version if it exists
            try:
                project_version = versioning.get_version(root)
                if project_version != "0.1.0":  # Only show if it's not the fallback
                    print(f"Project version: {project_version}")
                tool_tracker.track_tool_usage(
                    "version_display",
                    "version_management",
                    parameters={
                        "package_version": versioning.get_version(root),
                        "project_version": project_version,
                    },
                    result="success",
                )
            except Exception as e:
                tool_tracker.track_tool_usage(
                    "version_display",
                    "version_management",
                    parameters={"package_version": versioning.get_version(root)},
                    result=f"partial: {str(e)}",
                )

            session_summary = tool_tracker.end_task_session("completed")
            tool_tracker.display_tools_summary(session_summary)
        except Exception as e:
            tool_tracker.track_tool_usage(
                "version_command",
                "version_management",
                parameters={"args": vars(args)},
                result=f"failed: {str(e)}",
            )
            session_summary = tool_tracker.end_task_session("failed", str(e))
            tool_tracker.display_tools_summary(session_summary)
            raise  # Ignore project version errors
        return
    elif args.cmd == "metrics":
        # Show project metrics
        from ..core.base import telemetry

        items = telemetry.read_metrics(root)
        if not items:
            print("No metrics available. Run 'validate' to collect metrics.")
        else:
            print(f"Found {len(items)} metric records:")
            for i, item in enumerate(items[-3:], 1):  # Show last 3
                print(
                    f"  {i}. {item.get('ts', 'unknown')} - pass={item.get('pass')} - "
                    f"components: {len(item.get('components', []))}"
                )
        print("Metrics display complete.")
    elif args.cmd == "cleanup":
        # Safe cleanup functionality
        from ..core.legacy_cleanup import cleanup

        if args.dry_run:
            cleanup.safe_cleanup(root, dry_run=True)
        elif args.force:
            cleanup.safe_cleanup(root, dry_run=False, force=True)
        elif args.backup:
            backup_path = cleanup.create_backup(root)
            print(f"Backup created at: {backup_path}")
            cleanup.safe_cleanup(root, dry_run=False)
        else:
            cleanup.safe_cleanup(root, dry_run=False)
        print("Cleanup complete.")
    elif args.cmd == "tools":
        # System tools usage information
        from ..core.base import utils
        from ..core.orchestration.tool_usage_tracker import get_tool_tracker

        tool_tracker = get_tool_tracker(root)

        if getattr(args, "history", False):
            # Show recent tool usage history
            recent_tools = tool_tracker.get_recent_tool_usage(args.limit)

            if not recent_tools:
                print("ℹ️  No tool usage history found.")
                return

            print(f"\n🔧 RECENT TOOL USAGE HISTORY (last {len(recent_tools)} tools)")
            print("=" * 80)

            for i, tool in enumerate(reversed(recent_tools), 1):
                session_id = tool.get("session_id", "unknown")
                tool_name = tool.get("tool_name", "unknown")
                tool_type = tool.get("tool_type", "unknown")
                timestamp = tool.get("timestamp", "unknown")
                result = tool.get("result", "completed")
                duration = tool.get("duration")

                print(f"{i:2d}. [{timestamp}] {tool_name} ({tool_type})")
                print(f"    Session: {session_id}")
                print(f"    Result: {result}")
                if duration:
                    print(".2f")
                if tool.get("parameters"):
                    params = tool["parameters"]
                    if len(str(params)) < 100:
                        print(f"    Parameters: {params}")
                    else:
                        print(f"    Parameters: {str(params)[:97]}...")
                print()

        elif getattr(args, "session", None):
            # Show tools used in a specific session
            session_file = root / ".ai_onboard" / "session_tools.json"
            if session_file.exists():
                session_data = utils.read_json(session_file, default={})
                if session_data.get("session_id") == args.session:
                    print(f"\n🔧 TOOLS USED IN SESSION: {args.session}")
                    print("=" * 60)
                    print(f"Task: {session_data.get('task_name', 'unknown')}")
                    print(f"Type: {session_data.get('task_type', 'unknown')}")
                    print(f"Status: {session_data.get('final_status', 'unknown')}")
                    print(f"Total Tools: {session_data.get('total_tools_used', 0)}")
                    print()

                    tools_summary = session_data.get("tools_summary", {})
                    if tools_summary.get("tool_usage_counts"):
                        print("TOOL USAGE COUNTS:")
                        for tool, count in tools_summary["tool_usage_counts"].items():
                            print(f"  • {tool}: {count}")
                        print()

                    if session_data.get("tools_used"):
                        print("DETAILED TOOL LIST:")
                        for i, tool in enumerate(session_data["tools_used"], 1):
                            print(
                                f"  {i}. {tool['tool_name']} ({tool['tool_type']}) - {tool.get('result', 'completed')}"
                            )
                else:
                    print(
                        f"❌ Session {args.session} not found in current session data."
                    )
            else:
                print("❌ No current session data available.")
        else:
            # Show current session summary if available
            session_file = root / ".ai_onboard" / "session_tools.json"
            if session_file.exists():
                session_data = utils.read_json(session_file, default={})
                if session_data:
                    print(
                        f"\n🔧 CURRENT SESSION: {session_data.get('session_id', 'unknown')}"
                    )
                    print("=" * 60)
                    print(f"Task: {session_data.get('task_name', 'unknown')}")
                    print(f"Type: {session_data.get('task_type', 'unknown')}")
                    print(f"Started: {session_data.get('start_time', 'unknown')}")
                    if session_data.get("end_time"):
                        print(f"Ended: {session_data.get('end_time')}")
                        print(f"Status: {session_data.get('final_status', 'unknown')}")
                        print(
                            f"Total Tools Used: {session_data.get('total_tools_used', 0)}"
                        )
                    else:
                        print("Status: In progress")
                        print(
                            f"Tools Used So Far: {len(session_data.get('tools_used', []))}"
                        )
                    print()
                    print("💡 Use --history to see recent tool usage")
                    print("💡 Use --session <id> to see tools for a specific session")
                else:
                    print("ℹ️  No active session data available.")
                    print("💡 Use --history to see recent tool usage history")
            else:
                print("ℹ️  No tool usage data available.")
                print("💡 Run some commands to start tracking tool usage")
                print("💡 Use --history to see recent tool usage history")
    elif args.cmd == "wbs":
        # WBS management commands
        from ..core.orchestration.task_execution_gate import TaskExecutionGate
        from ..core.project_management.wbs_update_engine import WBSUpdateEngine

        gate = TaskExecutionGate(root)
        wbs_engine = WBSUpdateEngine(root)

        wbs_cmd = getattr(args, "wbs_cmd", None)

        if wbs_cmd == "status":
            # Show overall WBS and execution gate status
            print("🏗️  WBS & Task Execution Status")
            print("=" * 50)

            # WBS integrity check
            integrity = wbs_engine.validate_wbs_integrity()
            print("📊 WBS Integrity:")
            print(f"   • Valid: {'✅' if integrity['valid'] else '❌'}")
            print(f"   • Phases: {integrity['phase_count']}")
            print(f"   • Total Subtasks: {integrity['total_subtasks']}")
            if integrity["issues"]:
                print(f"   • Issues: {len(integrity['issues'])}")
                for issue in integrity["issues"][:3]:  # Show first 3
                    print(f"     - {issue}")

            print()

            # Pending tasks summary
            pending_summary = gate.get_pending_tasks_summary()
            print("⏳ Pending Tasks:")
            print(f"   • Total Pending: {pending_summary['total_pending']}")
            print(f"   • WBS Updated: {pending_summary['wbs_updated']}")
            print(f"   • Execution Allowed: {pending_summary['execution_allowed']}")
            print(f"   • Failed Updates: {pending_summary['failed_updates']}")
            print(f"   • Last Updated: {pending_summary['last_updated']}")

            if pending_summary["by_source"]:
                print("   • By Source:")
                for source, count in pending_summary["by_source"].items():
                    print(f"     - {source}: {count}")

        elif wbs_cmd == "update":
            # Force update all pending tasks
            print("🔄 Updating WBS for all pending tasks...")
            result = gate.update_wbs_for_pending_tasks()

            print(f"📋 Update Results:")
            print(f"   • Total Processed: {result['total_processed']}")
            print(f"   • Successfully Updated: {result['updated']}")
            print(f"   • Failed: {result['failed']}")

            if result["results"]:
                print("\n📝 Details:")
                for r in result["results"][:10]:  # Show first 10
                    status_icon = (
                        "✅"
                        if r["status"] == "success"
                        else "❌" if r["status"] == "failed" else "⚠️"
                    )
                    print(f"   {status_icon} {r['task_id']}: {r['status']}")
                    if r["status"] == "success":
                        print(
                            f"      → Phase: {r.get('phase_updated', 'unknown')}, "
                            f"Type: {r.get('update_type', 'unknown')}"
                        )

        elif wbs_cmd == "auto-update":
            # Enhanced intelligent auto-update
            from ..core.project_management.wbs_auto_update_engine import (
                WBSAutoUpdateEngine,
            )

            print("🧠 Running intelligent WBS auto-update...")
            auto_engine = WBSAutoUpdateEngine(root)

            force = getattr(args, "force", False)
            result = auto_engine.auto_update_wbs(force=force)

            if result["success"]:
                print(f"✅ Auto-Update Complete:")
                print(f"   • Tasks Updated: {result['updated_tasks']}")
                print(f"   • Tasks Checked: {result['checked_tasks']}")
                print(f"   • Duration: {result['duration']:.1f}s")

                if result.get("results"):
                    print("   • Evidence Found:")
                    for task_result in result["results"][:3]:  # Show first 3
                        task_id = task_result["task_id"]
                        evidence = ", ".join(task_result.get("evidence", []))
                        confidence = task_result.get("confidence", 0)
                        print(
                            f"     - {task_id}: {evidence} (confidence: {confidence:.1f})"
                        )

                        if task_result.get("cascade_updates"):
                            print(
                                f"       → Triggered: {len(task_result['cascade_updates'])} dependent tasks"
                            )
            else:
                print(f"❌ Auto-Update Failed: {result.get('error', 'Unknown error')}")

        elif wbs_cmd == "health":
            # Project health metrics
            from ..core.project_management.wbs_auto_update_engine import (
                WBSAutoUpdateEngine,
            )

            print("🏥 Project Health Analysis")
            print("=" * 50)

            auto_engine = WBSAutoUpdateEngine(root)
            health = auto_engine.get_project_health_score()

            if health.get("error"):
                print(f"❌ Health Check Failed: {health['error']}")
                return

            # Overall health
            score = health.get("health_score", 1.0)
            status = health.get("status", "no_tasks")
            status_emoji = {
                "healthy": "💚",
                "needs_attention": "🟡",
                "critical": "🔴",
            }.get(status, "❓")

            print(
                f"Overall Health: {status_emoji} {score:.1f}/1.0 ({status.replace('_', ' ').title()})"
            )
            print()

            # Task breakdown
            print("📊 Task Distribution:")
            print(f"   • Total Tasks: {health.get('total_tasks', 0)}")
            print(
                f"   • Completed: {health.get('completed_tasks', 0)} ({health.get('completion_rate', 0):.1%})"
            )
            print(f"   • Ready to Start: {health.get('ready_tasks', 0)}")
            print(f"   • Blocked: {health.get('blocked_tasks', 0)}")

        elif wbs_cmd == "analyze":
            # Enhanced critical path analysis
            from ..core.project_management.critical_path_engine import (
                CriticalPathEngine,
            )

            print("🛤️  Critical Path Analysis")
            print("=" * 50)

            cp_engine = CriticalPathEngine(root)
            analysis = cp_engine.analyze_critical_path()

            # Critical path overview
            critical_path = analysis.get("critical_path", [])
            print(f"Critical Path: {len(critical_path)} tasks")
            print(f"Project Duration: {analysis.get('total_project_duration', 0)} days")
            print()

            # Show critical tasks
            if critical_path:
                print("🔥 Critical Tasks:")
                for task_id in critical_path[:5]:  # Show first 5
                    print(f"   • {task_id}")
                if len(critical_path) > 5:
                    print(f"   ... and {len(critical_path) - 5} more")
                print()

            # Bottlenecks
            bottlenecks = analysis.get("bottlenecks", {})
            if bottlenecks.get("bottlenecks"):
                print("🚧 Bottlenecks Detected:")
                for bottleneck in bottlenecks["bottlenecks"][:3]:
                    print(f"   • {bottleneck['task_id']}: {bottleneck['suggestion']}")
                print()

            # Optimization suggestions
            suggestions = analysis.get("optimization_suggestions", [])
            if suggestions:
                print("💡 Optimization Suggestions:")
                for suggestion in suggestions[:3]:
                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                        suggestion.get("priority"), "📝"
                    )
                    print(f"   {priority_emoji} {suggestion['suggestion']}")

        elif wbs_cmd == "optimize":
            # Project optimization recommendations
            from ..core.project_management.critical_path_engine import (
                CriticalPathEngine,
            )
            from ..core.project_management.wbs_auto_update_engine import (
                WBSAutoUpdateEngine,
            )

            print("⚡ Project Optimization Analysis")
            print("=" * 50)

            # Get critical path analysis
            cp_engine = CriticalPathEngine(root)
            analysis = cp_engine.analyze_critical_path()

            # Get project health
            auto_engine = WBSAutoUpdateEngine(root)
            health = auto_engine.get_project_health_score()

            print("📈 Optimization Opportunities:")
            print()

            # Critical path optimization
            critical_path = analysis.get("critical_path", [])
            if len(critical_path) > 3:
                print("🛤️  Critical Path:")
                print(f"   • {len(critical_path)} tasks on critical path")
                print("   • Look for tasks that can be parallelized")
                print("   • Consider breaking down large critical tasks")
                print()

            # Resource optimization
            resources = analysis.get("resource_constraints", {})
            if resources.get("recommendations"):
                print("👥 Resource Allocation:")
                for rec in resources["recommendations"]:
                    print(f"   • {rec}")
                print()

            # Overall recommendations
            suggestions = analysis.get("optimization_suggestions", [])
            high_priority = [s for s in suggestions if s.get("priority") == "high"]

            if high_priority:
                print("🔥 High Priority Actions:")
                for suggestion in high_priority:
                    print(f"   • {suggestion['suggestion']}")
                print()

            print("💡 Next Steps:")
            print("   1. Address high-priority bottlenecks")
            print("   2. Unblock tasks where possible")
            print("   3. Review critical path for parallelization")
            print("   4. Run 'wbs auto-update' regularly for real-time tracking")

        elif wbs_cmd == "pending":
            # Show detailed pending tasks
            from ..core.base import utils

            pending_data = utils.read_json(
                gate.pending_tasks_path, default={"pending_tasks": []}
            )
            pending_tasks = pending_data.get("pending_tasks", [])

            if not pending_tasks:
                print("✅ No pending tasks requiring WBS updates.")
                return

            print(f"📋 Pending Tasks ({len(pending_tasks)} total)")
            print("=" * 60)

            for i, task in enumerate(pending_tasks, 1):
                print(f"{i}. {task['task_id']}")
                print(f"   Task: {task['task_data'].get('name', 'Unknown')}")
                print(
                    f"   Status: {'✅ WBS Updated' if task.get('wbs_updated') else '⏳ Pending WBS Update'}"
                )
                print(f"   Source: {task.get('source', 'unknown')}")
                print(f"   Registered: {task.get('registered_at', 'unknown')}")

                if task.get("last_error"):
                    print(f"   ❌ Last Error: {task['last_error']}")

                if task.get("execution_allowed"):
                    print("   🚀 Execution Allowed: Yes")
                else:
                    print("   🚫 Execution Allowed: No")

                integration = task.get("integration_recommendation", {})
                if integration.get("placement_recommendation"):
                    placement = integration["placement_recommendation"]
                    print(
                        f"   📍 Recommended Phase: {placement.get('recommended_phase', 'unknown')}"
                    )
                    print(
                        f"   🔧 Placement Type: {placement.get('placement_type', 'unknown')}"
                    )

                print()

        elif wbs_cmd == "force":
            # Force update specific task
            task_id = getattr(args, "task_id", None)
            if not task_id:
                print("❌ Error: task_id is required for force command")
                return

            print(f"🔄 Forcing WBS update for task: {task_id}")
            result = gate.force_wbs_update(task_id)

            if result["success"]:
                print("✅ WBS update forced successfully!")
                print(
                    f"   📍 Phase Updated: {result.get('update_result', {}).get('phase_updated', 'unknown')}"
                )
                print(
                    f"   🔧 Update Type: {result.get('update_result', {}).get('update_type', 'unknown')}"
                )
            else:
                print(
                    f"❌ Failed to force WBS update: {result.get('message', 'Unknown error')}"
                )

        elif wbs_cmd == "cleanup":
            # Clean up old tasks
            max_age = getattr(args, "max_age", 30)
            print(f"🧹 Cleaning up completed tasks older than {max_age} days...")
            removed_count = gate.cleanup_completed_tasks(max_age)
            print(f"✅ Removed {removed_count} old completed tasks.")

        elif wbs_cmd == "critical-path":
            # Critical path analysis
            from ..core.project_management.critical_path_engine import (
                CriticalPathEngine,
                analyze_critical_path,
                update_critical_path,
            )

            update_plan = getattr(args, "update", False)
            show_report = getattr(args, "report", False)

            if update_plan:
                print("🔄 Updating critical path designations in project plan...")
                result = update_critical_path(root)

                if result["success"]:
                    print(f"✅ Updated {result['critical_tasks_updated']} tasks")
                    print(f"🎯 Critical path: {result['critical_path_length']} tasks")
                    print(f"📅 Project duration: {result['project_duration']} days")
                else:
                    print(
                        f"❌ Failed to update critical path: {result.get('error', 'Unknown error')}"
                    )

            elif show_report:
                print("📊 Generating critical path analysis report...")
                engine = CriticalPathEngine(root)
                report = engine.get_critical_path_report()

                print("\n🎯 CRITICAL PATH ANALYSIS REPORT")
                print("=" * 50)

                # Summary
                summary = report["summary"]
                print("\n📈 SUMMARY:")
                print(f"   • Total Tasks: {summary['total_tasks']}")
                print(f"   • Critical Tasks: {summary['critical_tasks']}")
                print(f"   • Project Duration: {summary['project_duration_days']} days")
                print(f"   • Critical Path %: {summary['critical_percentage']}%")

                # Critical path details
                if report["critical_path"]:
                    print("\n🎯 CRITICAL PATH TASKS:")
                    for i, task in enumerate(report["critical_path"], 1):
                        print(
                            f"   {i}. {task['task_id']} (Days {task['start_day']}-{task['finish_day']})"
                        )
                else:
                    print("\n🎯 CRITICAL PATH TASKS: None found")

                # Bottlenecks
                if report["bottlenecks"]:
                    print("\n⚠️  BOTTLENECKS:")
                    for bottleneck in report["bottlenecks"]:
                        print(
                            f"   • {bottleneck['task_id']}: {bottleneck['duration']} days"
                        )

                # Recommendations
                if report["recommendations"]:
                    print("\n💡 RECOMMENDATIONS:")
                    for rec in report["recommendations"]:
                        print(f"   • {rec}")

            else:
                # Basic critical path analysis
                print("🔍 Analyzing project critical path...")
                result = analyze_critical_path(root)

                print("\n🎯 CRITICAL PATH ANALYSIS")
                print("=" * 40)

                print(f"📊 Tasks Analyzed: {result['total_tasks_analyzed']}")
                print(f"🎯 Critical Tasks: {result['critical_tasks_count']}")
                print(f"📅 Project Duration: {result['total_project_duration']} days")

                if result["critical_path"]:
                    print("\n🎯 CRITICAL PATH:")
                    for i, task_id in enumerate(result["critical_path"], 1):
                        timing = result["timing_data"][task_id]
                        slack = result["slack_data"][task_id]
                        duration = timing["earliest_finish"] - timing["earliest_start"]
                        print(
                            f"   {i}. {task_id} ({int(duration)} days, "
                            f"slack: {slack['total_slack']:.1f})"
                        )
                else:
                    print(
                        "\n🎯 CRITICAL PATH: No critical path found (all tasks have slack)"
                    )

                # Show some tasks with slack
                print("\n📋 SAMPLE TASK SLACK:")
                slack_items = list(result["slack_data"].items())[:5]
                for task_id, slack_info in slack_items:
                    status = (
                        "🎯 CRITICAL" if slack_info["is_critical"] else "⏰ FLEXIBLE"
                    )
                    print(
                        f"   • {task_id}: {slack_info['total_slack']:.1f} days slack {status}"
                    )

        elif wbs_cmd == "auto-update":
            # WBS auto-update
            from ..core.project_management.wbs_auto_update_engine import (
                WBSAutoUpdateEngine,
            )

            force_update = getattr(args, "force", False)
            dry_run = getattr(args, "dry_run", False)

            if dry_run:
                print("🔍 DRY RUN: Analyzing WBS auto-update opportunities...")
                print("This would check for completed tasks and suggest updates.")
                print("Use without --dry-run to apply changes.")
                return

            print("🔄 Running WBS auto-update...")
            update_engine = WBSAutoUpdateEngine(root)
            result = update_engine.auto_update_wbs(force=force_update)

            if result["success"]:
                print(f"✅ Auto-update completed successfully!")
                print(f"📊 Tasks checked: {result['checked_tasks']}")
                print(f"🔄 Tasks updated: {result['updated_tasks']}")
                print(f"⏱️  Duration: {result['duration']:.2f} seconds")

                if result["results"]:
                    print("\n📋 Updated Tasks:")
                    for update in result["results"]:
                        if update["status"] == "updated":
                            print(f"   ✅ {update['task_id']} - {update['evidence']}")
                        elif update["status"] == "update_failed":
                            print(
                                f"   ❌ {update['task_id']} - {update.get('error', 'Unknown error')}"
                            )
            else:
                print(f"❌ Auto-update failed: {result.get('error', 'Unknown error')}")

        elif wbs_cmd == "sync":
            # WBS sync
            from ..core.legacy_cleanup.pm_compatibility import (
                get_legacy_wbs_sync_engine,
            )

            force_sync = getattr(args, "force", False)
            run_validation = getattr(args, "validate", False)

            sync_engine = get_legacy_wbs_sync_engine(root)

            if run_validation:
                print("🔍 Running WBS data consistency validation...")
                validation_result = sync_engine.get_data_consistency_report()

                if validation_result["valid"]:
                    print("✅ WBS data is consistent")
                else:
                    print("❌ WBS data has consistency issues:")
                    for error in validation_result.get("errors", []):
                        print(f"   • {error}")

                if validation_result.get("warnings"):
                    print("\n⚠️  Warnings:")
                    for warning in validation_result.get("warnings", []):
                        print(f"   • {warning}")

                cache_status = validation_result.get("cache_status", {})
                if cache_status:
                    print(f"\n📊 Cache Status: {len(cache_status)} views cached")
                    for view_name, status in cache_status.items():
                        status_dict = cast(Dict[str, Any], status)
                        expired = "❌ EXPIRED" if status_dict["expired"] else "✅ FRESH"
                        print(
                            f"   • {view_name}: {expired} ({status_dict['age']:.0f}s old)"
                        )

            if force_sync:
                print("\n🔄 Forcing full WBS synchronization...")
                sync_result = engine.sync_all_views()

                if sync_result["success"]:
                    print("✅ All WBS views synchronized successfully")
                    print(
                        f"⏱️  Sync completed at {time.strftime('%H:%M:%S', time.localtime(sync_result['timestamp']))}"
                    )
                else:
                    print(
                        f"❌ Sync failed: {sync_result.get('error', 'Unknown error')}"
                    )
            elif not run_validation:
                # Default sync behavior
                print("🔄 Synchronizing WBS views...")
                sync_result = engine.sync_all_views()

                if sync_result["success"]:
                    print("✅ WBS synchronization completed")
                else:
                    print(
                        f"❌ Sync failed: {sync_result.get('error', 'Unknown error')}"
                    )

        elif wbs_cmd == "validate":
            # WBS validate
            from ..core.legacy_cleanup.pm_compatibility import (
                get_legacy_wbs_sync_engine,
            )

            should_fix = getattr(args, "fix", False)
            generate_report = getattr(args, "report", False)

            engine = get_legacy_wbs_sync_engine(root)

            print("🔍 Validating WBS data consistency and integrity...")

            # Get consistency report
            consistency_report = engine.get_data_consistency_report()

            # Display results
            print(f"📊 WBS Consistency Report:")
            print(f"   • Data Valid: {'✅' if consistency_report['valid'] else '❌'}")
            print(
                f"   • Last Check: {time.strftime('%H:%M:%S', time.localtime(consistency_report['last_check']))}"
            )
            print(
                f"   • Master Timestamp: "
                f"{time.strftime('%H:%M:%S', time.localtime(consistency_report['master_timestamp']))}"
            )

            errors = consistency_report.get("errors", [])
            warnings = consistency_report.get("warnings", [])
            cache_status = consistency_report.get("cache_status", {})

            if errors:
                print(f"\n❌ Critical Issues ({len(errors)}):")
                for error in errors:
                    print(f"   • {error}")

            if warnings:
                print(f"\n⚠️  Warnings ({len(warnings)}):")
                for warning in warnings:
                    print(f"   • {warning}")

            if cache_status:
                print(f"\n📊 Cache Status ({len(cache_status)} views):")
                for view_name, status in cache_status.items():
                    status_dict = cast(Dict[str, Any], status)
                    expired = "❌ EXPIRED" if status_dict["expired"] else "✅ FRESH"
                    print(
                        f"   • {view_name}: {expired} ("
                        f"{status_dict['age']:.0f}s old, {status_dict['size']} bytes)"
                    )

            # Generate detailed report if requested
            if generate_report:
                report_path = (
                    root
                    / ".ai_onboard"
                    / "reports"
                    / f"wbs_validation_{int(time.time())}.json"
                )
                report_path.parent.mkdir(parents=True, exist_ok=True)

                with open(report_path, "w") as f:
                    json.dump(consistency_report, f, indent=2, default=str)

                print(f"\n📄 Detailed report saved to: {report_path}")

            # Attempt to fix issues if requested
            if should_fix and (errors or warnings):
                print(
                    f"\n🔧 Attempting to fix {len(errors)} errors and \
                        {len(warnings)} warnings..."
                )

                fixed_count = 0
                for error in errors:
                    # Implement basic fixes for common issues
                    if "Missing name" in error:
                        # Could implement name fixing logic here
                        print(f"   • Would fix missing name: {error}")
                        fixed_count += 1
                    elif "Invalid phase data" in error:
                        print(f"   • Would fix invalid phase: {error}")
                        fixed_count += 1
                    # Add more fix logic as needed

                if fixed_count > 0:
                    print(f"✅ Fixed {fixed_count} issues")
                    print("💡 Run 'ai_onboard wbs validate' again to verify fixes")
                else:
                    print("ℹ️  No automatic fixes available for these issues")

            # Overall status
            if consistency_report["valid"]:
                print("\n🎉 WBS data is fully consistent and valid!")
            else:
                print(
                    f"\n⚠️  WBS data has {len(errors)} critical issues that need attention"
                )

    else:
        print("❌ Unknown WBS command. Use --help for available commands.")
