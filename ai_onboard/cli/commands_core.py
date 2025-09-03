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
    
    # Analyze
    s_an = subparsers.add_parser("analyze", help="Scan repo and draft ai_onboard.json manifest")
    s_an.add_argument("--allowExec", action="store_true", help="Permit safe external probes (off by default)")

    # Charter
    s_ch = subparsers.add_parser("charter", help="Create or update project charter")
    s_ch.add_argument("--interactive", action="store_true")

    # Plan
    subparsers.add_parser("plan", help="Build plan.json from charter")

    # Align
    s_al = subparsers.add_parser("align", help="Open or approve an alignment checkpoint")
    s_al.add_argument("--checkpoint", default="PlanGate")
    s_al.add_argument("--approve", action="store_true")
    s_al.add_argument("--note", default="", help="Optional note to store with approval")
    s_al.add_argument("--preview", action="store_true", help="Compute dry-run alignment report (no edits)")

    # Validate
    s_v = subparsers.add_parser("validate", help="Run validation and write report")
    s_v.add_argument("--report", action="store_true", help="Write .ai_onboard/report.md and versioned copy")

    # Kaizen
    s_k = subparsers.add_parser("kaizen", help="Run a kaizen cycle (metrics-driven nudges)")
    s_k.add_argument("--once", action="store_true")

    # Optimize
    s_o = subparsers.add_parser("optimize", help="Run quick optimization experiments")
    s_o.add_argument("--budget", default="5m", help="Time budget (e.g., 5m)")

    # Version
    s_ver = subparsers.add_parser("version", help="Show or bump ai_onboard version")
    s_ver.add_argument("--bump", choices=["major", "minor", "patch"])
    s_ver.add_argument("--set", help="Set explicit version (e.g., 1.2.3)")

    # Metrics
    subparsers.add_parser("metrics", help="Show last validation run summary from telemetry")

    # Cleanup
    s_clean = subparsers.add_parser("cleanup", help="Safely remove non-critical files (build artifacts, cache, etc.)")
    s_clean.add_argument("--dry-run", action="store_true", help="Show what would be deleted without actually deleting")
    s_clean.add_argument("--force", action="store_true", help="Skip confirmation prompts")
    s_clean.add_argument("--backup", action="store_true", help="Create backup before cleanup")


def handle_core_commands(args, root: Path):
    """Handle core command execution."""
    
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
        # Implementation for version command
        pass
    elif args.cmd == "metrics":
        # Implementation for metrics command
        pass
    elif args.cmd == "cleanup":
        # Implementation for cleanup command
        pass
