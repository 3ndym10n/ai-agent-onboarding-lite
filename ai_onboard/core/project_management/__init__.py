"""
Project Management components for AI Onboard.

This module contains project management, WBS, approval workflows,
and project planning systems.
"""

# Explicit imports to avoid F403/F405 linter errors
from .approval_workflow import ApprovalWorkflow, get_approval_workflow
from .critical_path_engine import CriticalPathEngine
from .phased_implementation_strategy import PhasedImplementationStrategy
from .unified_project_management import (
    UnifiedProjectManagementEngine,
    get_unified_project_management_engine,
)
from .wbs_auto_update_engine import WBSAutoUpdateEngine
from .wbs_synchronization_engine import WBSSynchronizationEngine
from .wbs_update_engine import WBSUpdateEngine

# Import ProjectType from vision module since it's used in the codebase
from ..vision.enhanced_vision_interrogator import ProjectType

__all__ = [
    # Project Management Core
    "UnifiedProjectManagementEngine",
    "get_unified_project_management_engine",
    # WBS Management
    "WBSAutoUpdateEngine",
    "WBSSynchronizationEngine",
    "WBSUpdateEngine",
    # Approval Workflows
    "ApprovalWorkflow",
    "get_approval_workflow",
    # Planning & Strategy
    "CriticalPathEngine",
    "PhasedImplementationStrategy",
    # Project Types and Status
    "ProjectType",
]
