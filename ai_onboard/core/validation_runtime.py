"""Validation runtime for ai-onboard system.

This module provides the core validation functionality that was moved from
monitoring_analytics to maintain backward compatibility.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .monitoring_analytics.validation_runtime import run

# Re-export for backward compatibility
__all__ = ["run"]


