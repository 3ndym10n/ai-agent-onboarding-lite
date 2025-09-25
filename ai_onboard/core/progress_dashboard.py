"""Progress dashboard compatibility shim."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .pm_compatibility import get_legacy_progress_dashboard


class ProgressDashboard:
    """Deprecated facade delegating to unified project management analytics."""

    def __init__(self, project_root: Path):
        self._delegate = get_legacy_progress_dashboard(project_root)

    def generate_dashboard(self) -> Dict[str, Any]:
        return self._delegate.generate_dashboard()
