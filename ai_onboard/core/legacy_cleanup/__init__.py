"""
Legacy Cleanup and Compatibility components for AI Onboard.

This module contains legacy systems, cleanup utilities, compatibility layers,
and transitional components that support the evolution of the system.
"""

from .charter import *
from .cleanup import *
from .code_cleanup_automation import *
from .discovery import *
from .dynamic_planner import *
from .gate_system import *
from .interrogation_to_charter import *
from .pm_compatibility import *
from .prompt_bridge import *
from .smart_debugger import *

__all__ = [
    # Core Systems
    "Charter",
    "load_charter",
    # Cleanup Systems
    "Cleanup",
    "CodeCleanupAutomation",
    # Discovery & Planning
    "Discovery",
    "get_comprehensive_tool_discovery",
    "DynamicPlanner",
    # Gate & Compatibility
    "GateSystem",
    "PMCompatibility",
    "get_legacy_wbs_sync_engine",
    # Interrogation & Bridge
    "InterrogationToCharter",
    "PromptBridge",
    "SmartDebugger",
]
