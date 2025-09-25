"""Legacy validation runtime compatibility shim."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from . import alignment, charter, telemetry
from .pm_compatibility import get_legacy_progress_dashboard
from .unified_project_management import get_unified_project_management_engine


def run(root: Path) -> Dict[str, Any]:
    """Run validation, delegating to unified project management engine."""
    engine = get_unified_project_management_engine(root)

    preview_fn = getattr(alignment, 'preview', None)
    if preview_fn is not None:
        try:
            alignment_state = preview_fn(root)
        except Exception:
            alignment_state = {}
    else:
        alignment_state = {}
    charter_data = charter.load_charter(root)
    project_status = engine.analytics.get_project_status()
    wbs_status = engine.wbs.get_status()
    progress = get_legacy_progress_dashboard(root).generate_dashboard()

    report = {
        "alignment": alignment_state,
        "charter": charter_data,
        "project_status": project_status,
        "wbs_status": wbs_status,
        "progress": progress,
    }
    report.setdefault("results", [
        {
            "component": "self_improvement",
            "prevention_analysis": {"status": "compatibility_mode", "details": []},
        }
    ])
    telemetry.record_run(root, report)
    return report

