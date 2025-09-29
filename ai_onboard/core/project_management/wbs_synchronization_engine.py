"""
WBS Synchronization Engine (T4.14) - Ensures all WBS views stay synchronized.

This module provides a centralized synchronization framework for WBS data access,
ensuring consistency across dashboard views, CLI displays, critical path analysis,
and all other WBS-dependent components.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Set
from warnings import warn

# Import moved to function level to avoid circular import


@dataclass
class SynchronizationEvent:
    """Represents a WBS synchronization event."""

    event_type: str  # 'load', 'update', 'invalidate', 'sync'
    timestamp: float
    source: str  # Component that triggered the event
    data: Dict[str, Any] = field(default_factory=dict)
    affected_views: Set[str] = field(default_factory=set)


@dataclass
class ViewCache:
    """Cache for a specific WBS view."""

    view_name: str
    data: Dict[str, Any]
    timestamp: float
    ttl: int = 300  # 5 minutes default TTL


class WBSSynchronizationEngine:
    """Deprecated shim delegating to unified PM engine."""

    def __init__(self, root: Path):
        warn(
            "WBSSynchronizationEngine is deprecated; use pm_compatibility.get_legacy_wbs_sync_engine",
            DeprecationWarning,
            stacklevel=2,
        )
        from ..legacy_cleanup.pm_compatibility import get_legacy_wbs_sync_engine

        self._delegate = get_legacy_wbs_sync_engine(root)

    def get_data_consistency_report(self) -> Dict[str, Any]:
        warn(
            "WBSSynchronizationEngine.get_data_consistency_report is deprecated",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._delegate.get_wbs_status()


def get_wbs_sync_engine(root: Optional[Path] = None) -> WBSSynchronizationEngine:
    return WBSSynchronizationEngine(root or Path("."))
