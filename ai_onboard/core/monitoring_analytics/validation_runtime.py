"""Legacy validation runtime compatibility shim."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..base import telemetry
from ..legacy_cleanup.charter import load_charter

# Imports moved to vision package
from ..legacy_cleanup.pm_compatibility import get_legacy_progress_dashboard
from ..project_management.unified_project_management import (
    get_unified_project_management_engine,
)
from ..vision.alignment import preview


def run(root: Path) -> Dict[str, Any]:
    """Run validation, delegating to unified project management engine."""
    engine = get_unified_project_management_engine(root)

    try:
        alignment_state = preview(root)
    except Exception:
        alignment_state = {}
    charter_data = load_charter(root)
    project_status = engine.analytics.get_project_status()
    wbs_status = engine.wbs.get_status()
    progress = get_legacy_progress_dashboard(root).generate_dashboard()

    report: Dict[str, Any] = {
        "alignment": alignment_state,
        "charter": charter_data,
        "project_status": project_status,
        "wbs_status": wbs_status,
        "progress": progress,
        "results": [
            {
                "component": "self_improvement",
                "prevention_analysis": {"status": "compatibility_mode", "details": []},
            }
        ],
    }
    telemetry.record_run(root, report)
    return report
