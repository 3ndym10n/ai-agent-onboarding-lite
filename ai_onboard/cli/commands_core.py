"""Core CLI commands for ai-onboard."""

import argparse
from pathlib import Path
from ..core import (
    charter,
    planning,
    discovery,
    alignment,
    state,
    utils,
    validation_runtime,
    progress_tracker,
    telemetry,
    optimizer,
    versioning,
    cleanup,
)


def add_core_commands(subparsers):
    """Add core command parsers."""
    
    # Global IAS flags via parent parser
    ias_parent = argparse.ArgumentParser(add_help=False)
    ias_parent.add_argument("--yes", action="store_true", help="Proceed without IAS confirmation (non-interactive)")
    ias_parent.add_argument("--assume", choices=["proceed", "quick_confirm", "clarify"], help="Assume IAS decision for this run")

    # Analyze
    s_an = subparsers.add_parser("analyze", parents=[ias_parent], help="Scan repo and draft ai_onboard.json manifest")
    s_an.add_argument("--allowExec", action="store_true", help="Permit safe external probes (off by default)")

    # Charter
    s_ch = subparsers.add_parser("charter", parents=[ias_parent], help="Create or update project charter")
    s_ch.add_argument("--interactive", action="store_true")

    # Plan
    subparsers.add_parser("plan", parents=[ias_parent], help="Build plan.json from charter")

    # Align
    s_al = subparsers.add_parser("align", parents=[ias_parent], help="Open or approve an alignment checkpoint")
    s_al.add_argument("--checkpoint", default="PlanGate")
    s_al.add_argument("--approve", action="store_true")
    s_al.add_argument("--note", default="", help="Optional note to store with approval")
    s_al.add_argument("--preview", action="store_true", help="Compute dry-run alignment report (no edits)")

    # Validate
    s_v = subparsers.add_parser("validate", parents=[ias_parent], help="Run validation and write report")
    s_v.add_argument("--report", action="store_true", help="Write .ai_onboard/report.md and versioned copy")

    # Kaizen
    s_k = subparsers.add_parser("kaizen", parents=[ias_parent], help="Run a kaizen cycle (metrics-driven nudges)")
    s_k.add_argument("--once", action="store_true")

    # Optimize
    s_o = subparsers.add_parser("optimize", parents=[ias_parent], help="Run quick optimization experiments")
    s_o.add_argument("--budget", default="5m", help="Time budget (e.g., 5m)")

    # Version
    s_ver = subparsers.add_parser("version", help="Show or bump ai_onboard version")
    s_ver.add_argument("--bump", choices=["major", "minor", "patch"])
    s_ver.add_argument("--set", help="Set explicit version (e.g., 1.2.3)")

    # Metrics
    subparsers.add_parser("metrics", parents=[ias_parent], help="Show last validation run summary from telemetry")

    # Cleanup
    s_clean = subparsers.add_parser("cleanup", parents=[ias_parent], help="Safely remove non-critical files (build artifacts, cache, etc.)")
    s_clean.add_argument("--dry-run", action="store_true", help="Show what would be deleted without actually deleting")
    s_clean.add_argument("--force", action="store_true", help="Skip confirmation prompts")
    s_clean.add_argument("--backup", action="store_true", help="Create backup before cleanup")


def _ias_gate(args, root: Path) -> bool:
    """Run IAS alignment preview and enforce collaborative gates.

    Returns True if execution may proceed, False if it should stop for clarification.
    """
    # Bypass for explicit approval or non-interactive runs
    assume = getattr(args, "assume", None)
    if getattr(args, "yes", False) or assume == "proceed":
        return True

    # Compute preview
    report = alignment.preview(root)
    decision = assume or report.get("decision", "clarify")

    if decision == "proceed":
        # Quietly allow
        return True

    if decision == "quick_confirm":
        # Require a lightweight confirmation unless --yes supplied
        print(utils.dumps_json({
            "ias": {
                "decision": decision,
                "confidence": report.get("confidence"),
                "report_path": report.get("report_path"),
                "next_action": "confirm or rerun with --yes/--assume proceed"
            }
        }))
        return False

    # Clarify: block and surface reasons/components
    print(utils.dumps_json({
        "ias": {
            "decision": decision,
            "confidence": report.get("confidence"),
            "components": report.get("components"),
            "ambiguities": report.get("ambiguities"),
            "report_path": report.get("report_path"),
            "message": "IAS requests clarification before proceeding. Rerun after addressing items or pass --assume quick_confirm/proceed."
        }
    }))
    return False


def handle_core_commands(args, root: Path):
    """Handle core command execution."""
    
    if args.cmd in {"analyze","charter","plan","align","validate","kaizen","optimize","metrics","cleanup"}:
        if not _ias_gate(args, root):
            return
    
    if args.cmd == "analyze":
        # Implementation for analyze command
        pass
    elif args.cmd == "charter":
        # Implementation for charter command
        pass
    elif args.cmd == "plan":
        # Implementation for plan command
        pass
    elif args.cmd == "align":
        # Wire preview
        if getattr(args, "preview", False):
            out = alignment.preview(root)
            print(utils.dumps_json(out))
            return
        # Implementation for align command
        pass
    elif args.cmd == "validate":
        # Implementation for validate command
        pass
    elif args.cmd == "kaizen":
        # Implementation for kaizen command
        pass
    elif args.cmd == "optimize":
        # Implementation for optimize command
        pass
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
        print(f"ai-onboard package version: {ai_onboard.__version__}")
        # Also show project version if it exists
        try:
            project_version = versioning.get_version(root)
            if project_version != "0.1.0":  # Only show if it's not the fallback
                print(f"Project version: {project_version}")
        except Exception:
            pass  # Ignore project version errors
        return
    elif args.cmd == "metrics":
        # Implementation for metrics command
        pass
    elif args.cmd == "cleanup":
        # Implementation for cleanup command
        pass
