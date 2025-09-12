"""
UX Middleware - Automatic user experience enhancements for all CLI interactions.

This middleware automatically:
- Records UX events for all command executions
- Provides intelligent error handling and recovery
- Shows helpful interventions at appropriate times
- Tracks user satisfaction and journey progress
- Delivers personalized assistance and guidance
"""

import time
import traceback
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..core.user_experience_enhancements import get_ux_enhancement_system, UXEventType
from ..core.ui_enhancement_system import get_ui_enhancement_system
from ..core.system_capability_tracker import (
    get_system_capability_tracker,
    UsageContext,
    UsagePattern,
)
from .visual_components import create_status_indicator


class UXMiddleware:
    """Middleware for automatic UX enhancements."""

    def __init__(self, root: Path):
        self.root = root
        self.ux_system = None  # Lazy loaded
        self.ui_system = None  # Lazy loaded
        self.capability_tracker = None  # Lazy loaded
        self.status = None  # Lazy loaded

    def _get_systems(self, user_id: str = "default"):
        """Lazy load systems to avoid circular imports."""
        if self.ux_system is None:
            self.ux_system = get_ux_enhancement_system(self.root)
        if self.ui_system is None:
            self.ui_system = get_ui_enhancement_system(self.root)
        if self.capability_tracker is None:
            self.capability_tracker = get_system_capability_tracker(self.root)
        if self.status is None:
            self.status = create_status_indicator(self.root, user_id)
        return self.ux_system, self.ui_system, self.capability_tracker, self.status

    @contextmanager
    def enhanced_command_execution(self, command: str, user_id: str = "default"):
        """Context manager for enhanced command execution."""
        start_time = time.time()
        success = True
        error_details = None

        try:
            # Pre-execution: Show pending interventions
            self._show_pending_interventions(user_id)

            # Execute command (yield control)
            yield

        except Exception as e:
            success = False
            error_details = str(e)

            # Handle error with UX enhancements
            self._handle_command_error(e, command, user_id)

            # Re-raise the exception
            raise

        finally:
            # Post-execution: Record UX event
            duration_ms = (time.time() - start_time) * 1000
            self._record_command_execution(
                command, user_id, success, error_details, duration_ms
            )

            # Post-execution: Check for new interventions
            if success:
                self._check_post_execution_interventions(command, user_id)

    def _show_pending_interventions(self, user_id: str):
        """Show pending interventions before command execution."""
        try:
            ux_system, ui_system, status = self._get_systems(user_id)

            interventions = ux_system.get_pending_interventions(user_id)

            # Show high priority interventions immediately
            high_priority = [i for i in interventions if i.priority >= 4]

            for intervention in high_priority[:1]:  # Show max 1 high priority
                message = ux_system.deliver_intervention(intervention.intervention_id)
                if message:
                    print()
                    print(
                        ui_system.format_output(
                            "🔔 Helpful Assistance", "info", user_id
                        )
                    )
                    print(message)
                    print()

                    # Auto-dismiss after showing
                    ux_system.dismiss_intervention(intervention.intervention_id, False)

        except Exception:
            # Silently fail to avoid disrupting main command
            pass

    def _handle_command_error(self, error: Exception, command: str, user_id: str):
        """Handle command errors with UX enhancements."""
        try:
            ux_system, ui_system, status = self._get_systems(user_id)

            # Create error context
            error_context = {
                "error_type": type(error).__name__,
                "command": command,
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now().isoformat(),
            }

            # Record error event
            ux_system.record_ux_event(
                UXEventType.ERROR_ENCOUNTER,
                user_id,
                context=error_context,
                command=command,
                success=False,
                error_details=str(error),
            )

            # Get error recovery intervention
            intervention = ux_system.error_handler.handle_error(
                error, error_context, user_id
            )

            # Show error recovery guidance
            print()
            print(
                ui_system.format_output(
                    "🚨 Error Recovery Assistance", "error", user_id
                )
            )
            message = ux_system.deliver_intervention(intervention.intervention_id)
            if message:
                print(message)
            print()

            # Auto-dismiss intervention
            ux_system.dismiss_intervention(intervention.intervention_id, False)

        except Exception:
            # Silently fail to avoid cascading errors
            pass

    def _record_command_execution(
        self,
        command: str,
        user_id: str,
        success: bool,
        error_details: Optional[str],
        duration_ms: float,
    ):
        """Record command execution event."""
        try:
            ux_system, ui_system, capability_tracker, status = self._get_systems(
                user_id
            )

            # Record in UI system for usage tracking
            ui_system.record_command_usage(user_id, command, success)

            # Record UX event
            ux_system.record_ux_event(
                UXEventType.COMMAND_EXECUTION,
                user_id,
                context={
                    "duration_ms": duration_ms,
                    "success": success,
                    "error_details": error_details,
                },
                command=command,
                success=success,
                error_details=error_details,
                duration_ms=duration_ms,
            )

            # Record capability usage
            context = UsageContext.INTERACTIVE_CLI
            pattern = UsagePattern.SINGLE_USE

            # Determine pattern based on recent usage
            user_profile = ui_system.get_user_profile(user_id)
            recent_commands = user_profile.last_used_commands[:5]

            if len(recent_commands) >= 3:
                # Check for workflow patterns
                common_workflows = ["charter", "plan", "align", "validate"]
                if any(cmd in common_workflows for cmd in recent_commands):
                    pattern = UsagePattern.WORKFLOW_SEQUENCE
                elif recent_commands.count(command) > 1:
                    pattern = UsagePattern.REPEATED_USE

            # Determine context based on command type
            if command in ["help", "discover", "suggest"]:
                context = UsageContext.ONBOARDING
            elif command in ["debug", "validate", "status"]:
                context = UsageContext.TROUBLESHOOTING

            capability_tracker.record_capability_usage(
                capability_name=command,
                user_id=user_id,
                context=context,
                pattern=pattern,
                success=success,
                duration_ms=duration_ms,
                error_details=error_details,
                user_expertise=user_profile.expertise_level.value,
                preceding_commands=recent_commands,
            )

            # Update user journey
            ux_system.update_journey_progress(user_id, command, success)

        except Exception:
            # Silently fail to avoid disrupting main command
            pass

    def _check_post_execution_interventions(self, command: str, user_id: str):
        """Check for interventions after successful command execution."""
        try:
            ux_system, ui_system, capability_tracker, status = self._get_systems(
                user_id
            )

            # Check for workflow guidance (low priority, shown after command)
            interventions = ux_system.get_pending_interventions(user_id)
            workflow_interventions = [
                i
                for i in interventions
                if i.intervention_type.value == "workflow_guidance" and i.priority <= 2
            ]

            # Show one workflow intervention if available
            if workflow_interventions:
                intervention = workflow_interventions[0]
                message = ux_system.deliver_intervention(intervention.intervention_id)
                if message:
                    print()
                    print(
                        ui_system.format_output(
                            "💡 Workflow Suggestion", "secondary", user_id
                        )
                    )
                    print(message)
                    print()

                    # Auto-dismiss after showing
                    ux_system.dismiss_intervention(intervention.intervention_id, False)

            # Check for satisfaction requests (very low priority)
            satisfaction_interventions = [
                i
                for i in interventions
                if i.intervention_type.value == "satisfaction_check"
            ]

            if (
                satisfaction_interventions and len(interventions) <= 1
            ):  # Only if no other interventions
                intervention = satisfaction_interventions[0]
                message = ux_system.deliver_intervention(intervention.intervention_id)
                if message:
                    print()
                    print(ui_system.format_output("📝 Quick Feedback", "info", user_id))
                    print(message)
                    print("💡 Use 'ux feedback --score <1-5>' to share your experience")
                    print()

                    # Auto-dismiss after showing
                    ux_system.dismiss_intervention(intervention.intervention_id, False)

        except Exception:
            # Silently fail to avoid disrupting main command
            pass

    def show_welcome_message(self, user_id: str = "default"):
        """Show welcome message for new users."""
        try:
            ux_system, ui_system, status = self._get_systems(user_id)

            user_profile = ui_system.get_user_profile(user_id)
            total_usage = sum(user_profile.command_usage_count.values())

            # Show welcome for first-time users
            if total_usage == 0:
                print()
                print(
                    ui_system.format_output(
                        "🎉 Welcome to AI Onboard!", "primary", user_id
                    )
                )
                print("Your intelligent project coach is ready to help.")
                print()
                print("💡 Quick start:")
                print("   • Use 'help' for personalized guidance")
                print("   • Try 'dashboard' to see your project status")
                print("   • Run 'suggest' for recommendations")
                print()

                # Record onboarding event
                ux_system.record_ux_event(UXEventType.USER_ONBOARDING, user_id)

            # Show returning user message
            elif total_usage < 5:
                print()
                print(
                    status.info(
                        f"Welcome back! You've used {total_usage} commands so far."
                    )
                )
                print("💡 Try 'suggest' to discover new features")
                print()

        except Exception:
            # Silently fail to avoid disrupting startup
            pass

    def show_completion_celebration(self, user_id: str = "default"):
        """Show celebration for command completion milestones."""
        try:
            ux_system, ui_system, status = self._get_systems(user_id)

            user_profile = ui_system.get_user_profile(user_id)
            total_usage = sum(user_profile.command_usage_count.values())

            # Celebrate milestones
            milestones = [5, 10, 25, 50, 100]

            if total_usage in milestones:
                print()
                print(
                    status.completed(
                        f"🎉 Milestone reached: {total_usage} commands executed!"
                    )
                )

                if total_usage == 5:
                    print(
                        "You're getting familiar with AI Onboard. Try 'help --tutorial' for advanced features."
                    )
                elif total_usage == 10:
                    print(
                        "Great progress! Explore 'kaizen' for continuous improvement features."
                    )
                elif total_usage == 25:
                    print(
                        "You're becoming an AI Onboard expert! Check out 'opt-experiments' for advanced optimization."
                    )
                elif total_usage >= 50:
                    print(
                        "Outstanding! You're a power user. Consider 'ux feedback --score 5' to share your experience."
                    )

                print()

        except Exception:
            # Silently fail
            pass


# Global middleware instance
_ux_middleware: Optional[UXMiddleware] = None


def get_ux_middleware(root: Path) -> UXMiddleware:
    """Get the global UX middleware."""
    global _ux_middleware
    if _ux_middleware is None:
        _ux_middleware = UXMiddleware(root)
    return _ux_middleware


def with_ux_enhancements(root: Path, command: str, user_id: str = "default"):
    """Context manager for UX-enhanced command execution."""
    middleware = get_ux_middleware(root)
    return middleware.enhanced_command_execution(command, user_id)
