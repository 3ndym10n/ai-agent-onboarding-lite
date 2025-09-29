"""
Simplified UX Middleware - Lightweight user experience enhancements.

This module provides simplified UX enhancements that integrate with the
unified user experience system without complex intervention logic.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from ..core.ai_integration.user_experience_system import (
    UserExperienceSystem,
    get_user_experience_system,
)
from .visual_components import create_status_indicator


class UXMiddleware:
    """Simplified middleware for UX enhancements."""

    def __init__(self, root: Path):
        self.root = root
        self.ux_system: Optional[UserExperienceSystem] = None  # Lazy loaded
        self.status = None  # Lazy loaded

    def _get_systems(self, user_id: str = "default"):
        """Lazy load systems to avoid circular imports."""
        if self.ux_system is None:
            self.ux_system = get_user_experience_system(self.root)
        if self.status is None:
            self.status = create_status_indicator(self.root, user_id)
        return self.ux_system, self.status

    @contextmanager
    def enhanced_command_execution(self, command: str, user_id: str = "default"):
        """Context manager for enhanced command execution."""
        success = True

        try:
            # Execute command (yield control)
            yield

        except Exception as e:
            success = False
            # Re-raise the exception
            raise

        finally:
            # Post-execution: Record command usage for learning
            ux_system, _ = self._get_systems(user_id)
            ux_system.record_command_usage(user_id, command, success)


# Global instance
_ux_middleware: Optional[UXMiddleware] = None


def get_ux_middleware(root: Path) -> UXMiddleware:
    """Get the global UX middleware instance."""
    global _ux_middleware
    if _ux_middleware is None:
        _ux_middleware = UXMiddleware(root)
    return _ux_middleware


def with_ux_enhancements(root: Path, command: str, user_id: str = "default"):
    """Context manager for UX-enhanced command execution."""
    middleware = get_ux_middleware(root)
    return middleware.enhanced_command_execution(command, user_id)
