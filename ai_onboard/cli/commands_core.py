"""Core CLI commands for ai - onboard."""

import argparse
import os
from pathlib import Path

from ..core import (
    alignment,
    telemetry,
    versioning,
)
from ..core.gate_system import create_clarification_gate, create_confirmation_gate


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

    # Compute preview (no user - bypass flags honored)
    report = alignment.preview(root)
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

        import json
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

    # Allow a safe, read - only preview to bypass the IAS gate so users can
    # inspect the recommendation before deciding to proceed.
    if args.cmd == "align" and getattr(args, "preview", False):
        from ..core import alignment, utils

        out = alignment.preview(root)
        print(utils.dumps_json(out))
        return

    if args.cmd in {
        "analyze",
        "charter",
        "plan",
        "align",
        "validate",
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
        from ..core import discovery, utils

        manifest = discovery.run(root, allow_exec=args.allowExec)
        utils.write_json(root / "ai_onboard.json", manifest)
        print("Wrote ai_onboard.json (draft).")
    elif args.cmd == "charter":
        # Create or update project charter
        from ..core import charter, state

        charter.ensure(root, interactive=args.interactive)

        # Mark vision as confirmed if run interactively
        if args.interactive:
            charter_data = charter.load_charter(root)
            charter_data["vision_confirmed"] = True
            charter.save_charter(root, charter_data)
            print("✅ Vision confirmed in charter")

        state.advance(root, state.load(root), "chartered")
        print("Charter ready at .ai_onboard / charter.json")
    elif args.cmd == "plan":
        # Build project plan from charter
        from ..core import planning, state

        planning.build(root)
        state.advance(root, state.load(root), "planned")
        print("Plan ready at .ai_onboard / plan.json")
    elif args.cmd == "roadmap":
        # Build lightweight roadmap from analysis
        from ..core import roadmap_lite

        goal = ""
        rm = roadmap_lite.build(root, goal)
        print(utils.dumps_json(rm))
    elif args.cmd == "work":
        # Show next task and log it
        import json

        from ..core import runlog

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
        from ..core import alignment, prompt_bridge, state

        if args.preview:
            res = alignment.preview(root)
            print(prompt_bridge.dumps_json(res))
        elif args.approve:
            alignment.record_decision(root, "ALIGN", args.checkpoint, True, args.note)
            state.advance(root, state.load(root), "aligned")
            print(f"Alignment approved for {args.checkpoint}.")
        else:
            alignment.open_checkpoint(root, args.checkpoint)
            print(f"Opened alignment checkpoint {args.checkpoint}.")
    elif args.cmd == "validate":
        # Run validation and write report
        from ..core import (
            alignment,
            charter,
            progress_tracker,
            telemetry,
            validation_runtime,
        )

        alignment.require_state(root, "aligned")

        # Check if vision is confirmed before allowing validation
        charter_data = charter.load_charter(root)
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
            progress_tracker.write_report(root, res)
            print("Wrote .ai_onboard / report.md (+ versioned copy).")
        telemetry.record_run(root, res)
        print("Validation complete.")
    elif args.cmd == "kaizen":
        # Run a kaizen cycle (metrics - driven nudges)
        from ..core import optimizer

        optimizer.nudge_from_metrics(root)
        print("Kaizen cycle complete.")
    elif args.cmd == "optimize":
        # Run quick optimization experiments
        from ..core import optimizer

        optimizer.quick_optimize(root)
        print("Optimization complete.")
    elif args.cmd == "version":
        # Show the actual package version, not project version
        import ai_onboard

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
        # Show package version, not project version
        print(f"ai - onboard package version: {ai_onboard.__version__}")
        # Also show project version if it exists
        try:
            project_version = versioning.get_version(root)
            if project_version != "0.1.0":  # Only show if it's not the fallback
                print(f"Project version: {project_version}")
        except Exception:
            pass  # Ignore project version errors
        return
    elif args.cmd == "metrics":
        # Show project metrics
        from ..core import telemetry

        items = telemetry.read_metrics(root)
        if not items:
            print("No metrics available. Run 'validate' to collect metrics.")
        else:
            print(f"Found {len(items)} metric records:")
            for i, item in enumerate(items[-3:], 1):  # Show last 3
                print(
                    f"  {i}. {item.get('ts', 'unknown')} - pass={item.get('pass')} - components: {len(item.get('components', []))}"
                )
        print("Metrics display complete.")
    elif args.cmd == "cleanup":
        # Safe cleanup functionality
        from ..core import cleanup

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
