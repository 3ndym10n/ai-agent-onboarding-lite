"""Onboarding convenience commands (quickstart & doctor)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from ..core.base import utils
from ..core.onboarding import BootstrapGuard
from ..core.utilities.unicode_utils import ensure_unicode_safe


def add_onboarding_commands(subparsers) -> None:
    """Expose onboarding helpers on the CLI."""
    p_quick = subparsers.add_parser(
        "quickstart",
        help="Bootstrap a minimal .ai_onboard/ setup (charter, state, plan).",
        description="Create starter charter/state/plan files so you can begin aligning work immediately.",
    )
    p_quick.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing onboarding files if they already exist.",
    )

    p_doc = subparsers.add_parser(
        "doctor",
        help="Inspect onboarding status and recommended next steps.",
        description="Report which onboarding artifacts exist and the next recommended command.",
    )
    p_doc.add_argument(
        "--json",
        action="store_true",
        help="Output diagnostics as JSON (suitable for tooling).",
    )


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #
def quickstart_project(project_root: Path, *, force: bool = False) -> Dict[str, bool]:
    """Create minimal charter/state/plan files if they are missing."""
    root = Path(project_root).resolve()
    base = root / ".ai_onboard"
    base.mkdir(parents=True, exist_ok=True)

    status = {
        "charter_created": False,
        "state_created": False,
        "plan_created": False,
    }

    # Charter
    charter_path = base / "charter.json"
    if force or not charter_path.exists():
        project_name = root.name or "my-project"
        utils.write_json(
            charter_path,
            {
                "project_name": project_name,
                "description": "Describe your project vision here.",
                "objectives": [
                    "Document core goals",
                    "Define success criteria",
                    "Agree scope boundaries",
                ],
                "technologies": [],
                "max_complexity": "simple",
            },
        )
        status["charter_created"] = True

    # State
    state_path = base / "state.json"
    if force or not state_path.exists():
        utils.write_json(
            state_path,
            {
                "phase": "planning",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "notes": "Initial state scaffolded by `ai_onboard quickstart`.",
            },
        )
        status["state_created"] = True

    # Plan
    plan_path = base / "project_plan.json"
    legacy_plan_path = base / "plan.json"
    plan_target = plan_path if force or not plan_path.exists() else legacy_plan_path
    if force or not plan_path.exists():
        utils.write_json(
            plan_target,
            {
                "workflow": {
                    "current_phase": "planning",
                    "phases": [
                        {
                            "id": "planning",
                            "name": "Planning",
                            "description": "Refine requirements and confirm feasibility.",
                        }
                    ],
                },
                "work_breakdown_structure": {
                    "planning": {
                        "name": "Planning",
                        "description": "Capture requirements and produce initial backlog.",
                        "subtasks": {
                            "charter_review": {
                                "name": "Review charter",
                                "description": "Confirm the project vision before proceeding.",
                            },
                            "state_analysis": {
                                "name": "Run project analyze",
                                "description": "Capture repository state and existing artifacts.",
                            },
                        },
                    }
                },
            },
        )
        status["plan_created"] = True

    return status


def doctor_report(project_root: Path) -> Dict[str, object]:
    """Return onboarding diagnostics for the given project."""
    guard = BootstrapGuard(project_root)
    stage = guard.get_stage()
    status = guard.get_requirements_status()
    guidance = guard.get_guidance(stage)
    return {
        "stage": stage.value,
        "requirements": status,
        "message": guidance.message,
        "next_command": guidance.next_command,
    }


# --------------------------------------------------------------------------- #
# CLI handlers
# --------------------------------------------------------------------------- #
def handle_onboarding_commands(args, root: Path) -> None:
    """Dispatch onboarding helper commands."""
    if args.cmd == "quickstart":
        results = quickstart_project(root, force=getattr(args, "force", False))
        ensure_unicode_safe("[ok] Quickstart complete.")
        for key, value in results.items():
            mark = "[created]" if value else "[exists]"
            ensure_unicode_safe(f"  {mark} {key.replace('_', ' ')}")
        guidance = BootstrapGuard(root).get_guidance()
        if guidance.message:
            ensure_unicode_safe(f"\nNext step: {guidance.message}")
        return

    if args.cmd == "doctor":
        report = doctor_report(root)
        if getattr(args, "json", False):
            print(json.dumps(report, indent=2))
            return

        ensure_unicode_safe(f"Onboarding stage: {report['stage']}")
        for requirement, present in report["requirements"].items():
            mark = "[ok]" if present else "[missing]"
            ensure_unicode_safe(f"  {mark} {requirement}")
        if report["message"]:
            ensure_unicode_safe(f"\n{report['message']}")
        return

    raise ValueError(f"Unhandled onboarding command: {args.cmd}")
