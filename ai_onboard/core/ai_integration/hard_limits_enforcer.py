"""
Hard Limits Enforcer - Prevents excessive file operations and refactoring.

This module enforces hard limits on agent activities to prevent chaos and technical debt:
- File operation limits (creates, deletes, modifies per time window)
- Refactoring limits (number of files, complexity thresholds)
- Change rate limits to prevent rapid uncoordinated changes

The enforcer works by monitoring agent activities and blocking operations
that would exceed configured limits.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ..base import utils
from .agent_activity_monitor import AgentActivityMonitor
from .user_preference_learning import (
    PreferenceCategory,
    get_user_preference_learning_system,
)


class LimitType(Enum):
    """Types of limits that can be enforced."""

    FILE_CREATION = "file_creation"  # Too many files created
    FILE_DELETION = "file_deletion"  # Too many files deleted
    FILE_MODIFICATION = "file_modification"  # Too many files modified
    REFACTORING_SCALE = "refactoring_scale"  # Too many files in one refactor
    CHANGE_RATE = "change_rate"  # Changes happening too fast
    DEPENDENCY_ADDITION = "dependency_addition"  # Too many new dependencies


class LimitSeverity(Enum):
    """Severity levels for limit violations."""

    WARNING = "warning"  # Approaching limit, monitor closely
    BLOCKED = "blocked"  # Operation blocked due to limit
    CRITICAL = "critical"  # System-level limit exceeded


@dataclass
class LimitViolation:
    """Represents a limit violation event."""

    violation_id: str
    limit_type: LimitType
    severity: LimitSeverity
    agent_id: str
    description: str
    violated_at: float
    current_count: int
    limit_threshold: int
    time_window_minutes: int

    # Context
    operation_type: str
    affected_files: List[str] = field(default_factory=list)
    blocking_reason: str = ""

    # Resolution
    resolved: bool = False
    resolved_at: Optional[float] = None
    override_granted: bool = False


@dataclass
class ActivityLimits:
    """Configuration for activity limits."""

    # File operation limits (per hour)
    max_files_created_per_hour: int = 20
    max_files_deleted_per_hour: int = 10
    max_files_modified_per_hour: int = 50

    # Refactoring limits
    max_files_in_refactor: int = 15
    max_refactor_complexity: int = 100  # Abstract complexity score

    # Change rate limits
    max_changes_per_minute: int = 5
    max_changes_per_hour: int = 100

    # Dependency limits
    max_dependencies_added_per_hour: int = 5

    # Time windows for enforcement (minutes)
    file_operation_window: int = 60  # 1 hour
    change_rate_window: int = 5  # 5 minutes
    refactoring_window: int = 120  # 2 hours


@dataclass
class AgentActivityTracker:
    """Tracks agent activity for limit enforcement."""

    agent_id: str
    limits: ActivityLimits

    # Activity counters with timestamps
    files_created: List[float] = field(default_factory=list)  # Timestamps
    files_deleted: List[float] = field(default_factory=list)
    files_modified: List[float] = field(default_factory=list)
    changes_made: List[float] = field(default_factory=list)
    dependencies_added: List[float] = field(default_factory=list)

    # Current operations
    active_refactor_files: Set[str] = field(default_factory=set)
    current_refactor_complexity: int = 0

    # Violations
    violations: List[LimitViolation] = field(default_factory=list)


class HardLimitsEnforcer:
    """
    Enforces hard limits on agent activities to prevent chaos and technical debt.

    Monitors agent file operations, refactoring activities, and change rates to
    block operations that would exceed configured safety limits.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ai_onboard_dir = project_root / ".ai_onboard"

        # Core systems
        self.activity_monitor = AgentActivityMonitor(project_root)

        # Configuration
        self.default_limits = ActivityLimits()
        self.agent_trackers: Dict[str, AgentActivityTracker] = {}

        # State
        self.violations: List[LimitViolation] = []
        self.monitoring_active = False

        # Load configuration
        self._load_limits_config()

        # Ensure directories exist
        self.ai_onboard_dir.mkdir(exist_ok=True)

        # Start monitoring
        self.start_monitoring()

    def start_monitoring(self) -> None:
        """Start limit enforcement monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        print("🛡️ Hard Limits Enforcer started")
        # Note: Could add background monitoring thread here if needed

    def stop_monitoring(self) -> None:
        """Stop limit enforcement monitoring."""
        self.monitoring_active = False
        self._save_violations()
        print("⏹️ Hard Limits Enforcer stopped")

    def check_operation_allowed(
        self, agent_id: str, operation_type: str, context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[LimitViolation]]:
        """
        Check if an operation is allowed under current limits.

        Returns: (allowed, block_reason, violation)
        """
        if not self.monitoring_active:
            return True, None, None

        # Check for cleanup preferences for temp file operations
        if operation_type == "file_creation" and self._is_temp_file_operation(context):
            cleanup_allowed, cleanup_reason = self._check_cleanup_preferences(context)
            if not cleanup_allowed:
                violation = self._create_violation(
                    agent_id,
                    LimitType.FILE_CREATION,
                    LimitSeverity.BLOCKED,
                    cleanup_reason,
                    1,  # Current count
                    0,  # No limit for cleanup violations
                    60,  # 1 hour window
                )
                return False, cleanup_reason, violation

        # Get or create tracker for this agent
        tracker = self._get_or_create_tracker(agent_id)

        # Update activity tracking
        self._update_activity_tracking(agent_id, operation_type, context)

        # Check specific limits based on operation type
        if operation_type == "file_create":
            return self._check_file_creation_limit(tracker)
        elif operation_type == "file_delete":
            return self._check_file_deletion_limit(tracker)
        elif operation_type == "file_modify":
            return self._check_file_modification_limit(tracker)
        elif operation_type == "refactor":
            return self._check_refactoring_limit(tracker, context)
        elif operation_type == "dependency_add":
            return self._check_dependency_limit(tracker)
        elif operation_type == "bulk_operation":
            return self._check_bulk_operation_limit(tracker, context)

        # Unknown operation type - allow by default
        return True, None, None

    def _is_temp_file_operation(self, context: Dict[str, Any]) -> bool:
        """Check if this is a temporary file operation that should respect cleanup preferences."""
        file_path = context.get("file_path", "")
        if not file_path:
            return False

        # Check if this looks like a temp file
        temp_indicators = ["temp", "tmp", "_temp", "analysis", "debug", "cache"]
        file_name = Path(file_path).name.lower()

        return any(indicator in file_name for indicator in temp_indicators)

    def _check_cleanup_preferences(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if operation violates user's cleanup preferences."""
        try:
            preference_system = get_user_preference_learning_system(self.project_root)
            user_id = context.get("user_id", "vibe_coder")

            # Check for organization focus preferences
            org_prefs = preference_system.get_user_preferences(
                user_id=user_id, category=PreferenceCategory.ORGANIZATION_PREFERENCE
            )

            # Look for lean directory preferences
            for pref_id, pref in org_prefs.items():
                if pref.preference_key == "root_directory_cleanliness":
                    pref_value = str(pref.preference_value).lower()
                    if pref_value == "lean" and context.get("user_prefers_lean"):
                        return (
                            False,
                            "Blocked: User prefers lean root directory, use cache directory instead",
                        )

            # Check explicit cleanup preferences in context
            if context.get("user_prefers_lean") and self._is_temp_file_operation(
                context
            ):
                return (
                    False,
                    "Blocked: Temporary file creation in root directory violates user cleanup preferences",
                )

        except Exception:
            # If preference check fails, allow operation to continue
            pass

        return True, ""

    def get_limit_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current limit enforcement status."""
        status = {
            "monitoring_active": self.monitoring_active,
            "total_violations": len(self.violations),
            "agents_tracked": len(self.agent_trackers),
            "default_limits": self._limits_to_dict(self.default_limits),
        }

        if agent_id and agent_id in self.agent_trackers:
            tracker = self.agent_trackers[agent_id]
            status["agent_status"] = {
                "files_created_recently": len(tracker.files_created),
                "files_deleted_recently": len(tracker.files_deleted),
                "files_modified_recently": len(tracker.files_modified),
                "active_violations": len(
                    [v for v in tracker.violations if not v.resolved]
                ),
                "refactor_files_active": len(tracker.active_refactor_files),
            }

        return status

    def grant_limit_override(
        self, agent_id: str, violation_id: str, granted_by: str = "system"
    ) -> bool:
        """Grant an override for a specific limit violation."""
        for violation in self.violations:
            if (
                violation.violation_id == violation_id
                and violation.agent_id == agent_id
            ):
                violation.override_granted = True
                violation.resolved = True
                violation.resolved_at = time.time()
                print(f"🛡️ Limit override granted for {violation_id} by {granted_by}")
                return True

        return False

    def _get_or_create_tracker(self, agent_id: str) -> AgentActivityTracker:
        """Get or create an activity tracker for an agent."""
        if agent_id not in self.agent_trackers:
            self.agent_trackers[agent_id] = AgentActivityTracker(
                agent_id=agent_id, limits=self.default_limits
            )
        return self.agent_trackers[agent_id]

    def _update_activity_tracking(
        self, agent_id: str, operation_type: str, context: Dict[str, Any]
    ) -> None:
        """Update activity tracking for an agent."""
        tracker = self._get_or_create_tracker(agent_id)
        current_time = time.time()

        # Clean old timestamps (keep only within relevant windows)
        max_window = (
            max(
                tracker.limits.file_operation_window,
                tracker.limits.change_rate_window,
                tracker.limits.refactoring_window,
            )
            * 60
        )  # Convert to seconds

        cutoff_time = current_time - max_window
        self._clean_old_timestamps(tracker, cutoff_time)

        # Record the operation
        if operation_type == "file_create":
            tracker.files_created.append(current_time)
        elif operation_type == "file_delete":
            tracker.files_deleted.append(current_time)
        elif operation_type == "file_modify":
            tracker.files_modified.append(current_time)
            tracker.changes_made.append(current_time)
        elif operation_type == "dependency_add":
            tracker.dependencies_added.append(current_time)

    def _check_file_creation_limit(
        self, tracker: AgentActivityTracker
    ) -> Tuple[bool, Optional[str], Optional[LimitViolation]]:
        """Check if file creation is within limits."""
        current_count = len(tracker.files_created)
        limit = tracker.limits.max_files_created_per_hour

        if current_count >= limit:
            violation = self._create_violation(
                tracker.agent_id,
                LimitType.FILE_CREATION,
                LimitSeverity.BLOCKED,
                f"File creation limit exceeded: {current_count}/{limit} files per hour",
                current_count,
                limit,
                tracker.limits.file_operation_window,
            )
            return (
                False,
                f"File creation blocked: limit of {limit} files per hour exceeded",
                violation,
            )

        return True, None, None

    def _check_file_deletion_limit(
        self, tracker: AgentActivityTracker
    ) -> Tuple[bool, Optional[str], Optional[LimitViolation]]:
        """Check if file deletion is within limits."""
        current_count = len(tracker.files_deleted)
        limit = tracker.limits.max_files_deleted_per_hour

        if current_count >= limit:
            violation = self._create_violation(
                tracker.agent_id,
                LimitType.FILE_DELETION,
                LimitSeverity.BLOCKED,
                f"File deletion limit exceeded: {current_count}/{limit} files per hour",
                current_count,
                limit,
                tracker.limits.file_operation_window,
            )
            return (
                False,
                f"File deletion blocked: limit of {limit} files per hour exceeded",
                violation,
            )

        return True, None, None

    def _check_file_modification_limit(
        self, tracker: AgentActivityTracker
    ) -> Tuple[bool, Optional[str], Optional[LimitViolation]]:
        """Check if file modification is within limits."""
        current_count = len(tracker.files_modified)
        limit = tracker.limits.max_files_modified_per_hour

        if current_count >= limit:
            violation = self._create_violation(
                tracker.agent_id,
                LimitType.FILE_MODIFICATION,
                LimitSeverity.BLOCKED,
                f"File modification limit exceeded: {current_count}/{limit} files per hour",
                current_count,
                limit,
                tracker.limits.file_operation_window,
            )
            return (
                False,
                f"File modification blocked: limit of {limit} files per hour exceeded",
                violation,
            )

        return True, None, None

    def _check_refactoring_limit(
        self, tracker: AgentActivityTracker, context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[LimitViolation]]:
        """Check if refactoring operation is within limits."""
        files_affected = context.get("files_affected", [])
        complexity_score = context.get("complexity_score", 0)

        # Check number of files in refactor
        if len(files_affected) > tracker.limits.max_files_in_refactor:
            violation = self._create_violation(
                tracker.agent_id,
                LimitType.REFACTORING_SCALE,
                LimitSeverity.BLOCKED,
                f"Refactoring scale limit exceeded: {len(files_affected)}/{tracker.limits.max_files_in_refactor} files",
                len(files_affected),
                tracker.limits.max_files_in_refactor,
                tracker.limits.refactoring_window,
            )
            return (
                False,
                f"Refactoring blocked: too many files ({len(files_affected)})",
                violation,
            )

        # Check complexity
        if complexity_score > tracker.limits.max_refactor_complexity:
            violation = self._create_violation(
                tracker.agent_id,
                LimitType.REFACTORING_SCALE,
                LimitSeverity.BLOCKED,
                f"Refactoring complexity limit exceeded: {complexity_score}/{tracker.limits.max_refactor_complexity}",
                complexity_score,
                tracker.limits.max_refactor_complexity,
                tracker.limits.refactoring_window,
            )
            return (
                False,
                f"Refactoring blocked: complexity too high ({complexity_score})",
                violation,
            )

        return True, None, None

    def _check_dependency_limit(
        self, tracker: AgentActivityTracker
    ) -> Tuple[bool, Optional[str], Optional[LimitViolation]]:
        """Check if dependency addition is within limits."""
        current_count = len(tracker.dependencies_added)
        limit = tracker.limits.max_dependencies_added_per_hour

        if current_count >= limit:
            violation = self._create_violation(
                tracker.agent_id,
                LimitType.DEPENDENCY_ADDITION,
                LimitSeverity.BLOCKED,
                f"Dependency addition limit exceeded: {current_count}/{limit} per hour",
                current_count,
                limit,
                tracker.limits.file_operation_window,
            )
            return (
                False,
                f"Dependency addition blocked: limit of {limit} per hour exceeded",
                violation,
            )

        return True, None, None

    def _check_bulk_operation_limit(
        self, tracker: AgentActivityTracker, context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[LimitViolation]]:
        """Check bulk operations for rate limits."""
        operations_count = context.get("operations_count", 0)
        time_window_minutes = context.get(
            "time_window_minutes", tracker.limits.change_rate_window
        )

        # Check change rate
        recent_changes = len(
            [
                t
                for t in tracker.changes_made
                if time.time() - t < (time_window_minutes * 60)
            ]
        )

        max_changes = tracker.limits.max_changes_per_minute * time_window_minutes
        if recent_changes + operations_count > max_changes:
            violation = self._create_violation(
                tracker.agent_id,
                LimitType.CHANGE_RATE,
                LimitSeverity.BLOCKED,
                (
                    f"Change rate limit exceeded: {recent_changes + operations_count}/"
                    f"{max_changes} in {time_window_minutes}min"
                ),
                recent_changes + operations_count,
                max_changes,
                time_window_minutes,
            )
            return False, f"Bulk operation blocked: change rate too high", violation

        return True, None, None

    def _create_violation(
        self,
        agent_id: str,
        limit_type: LimitType,
        severity: LimitSeverity,
        description: str,
        current_count: int,
        limit_threshold: int,
        time_window: int,
    ) -> LimitViolation:
        """Create a limit violation record."""
        violation = LimitViolation(
            violation_id=f"{limit_type.value}_{agent_id}_{int(time.time())}",
            limit_type=limit_type,
            severity=severity,
            agent_id=agent_id,
            description=description,
            violated_at=time.time(),
            current_count=current_count,
            limit_threshold=limit_threshold,
            time_window_minutes=time_window,
            operation_type=limit_type.value,
        )

        self.violations.append(violation)

        # Also add to agent tracker
        tracker = self._get_or_create_tracker(agent_id)
        tracker.violations.append(violation)

        # Log the violation
        print(f"🛡️ LIMIT VIOLATION: {description}")

        return violation

    def _clean_old_timestamps(
        self, tracker: AgentActivityTracker, cutoff_time: float
    ) -> None:
        """Remove timestamps older than cutoff time."""
        tracker.files_created = [t for t in tracker.files_created if t > cutoff_time]
        tracker.files_deleted = [t for t in tracker.files_deleted if t > cutoff_time]
        tracker.files_modified = [t for t in tracker.files_modified if t > cutoff_time]
        tracker.changes_made = [t for t in tracker.changes_made if t > cutoff_time]
        tracker.dependencies_added = [
            t for t in tracker.dependencies_added if t > cutoff_time
        ]

    def _load_limits_config(self) -> None:
        """Load limits configuration from storage."""
        try:
            config_file = self.ai_onboard_dir / "hard_limits_config.json"
            if config_file.exists():
                config_data = utils.read_json(config_file)
                self.default_limits = ActivityLimits(**config_data)
        except Exception as e:
            print(f"Warning: Could not load hard limits config: {e}")

    def _save_violations(self) -> None:
        """Save violations to storage."""
        try:
            violations_data = []
            for violation in self.violations[-200:]:  # Keep last 200 violations
                violation_dict = {
                    "violation_id": violation.violation_id,
                    "limit_type": violation.limit_type.value,
                    "severity": violation.severity.value,
                    "agent_id": violation.agent_id,
                    "description": violation.description,
                    "violated_at": violation.violated_at,
                    "current_count": violation.current_count,
                    "limit_threshold": violation.limit_threshold,
                    "time_window_minutes": violation.time_window_minutes,
                    "operation_type": violation.operation_type,
                    "affected_files": violation.affected_files,
                    "blocking_reason": violation.blocking_reason,
                    "resolved": violation.resolved,
                    "resolved_at": violation.resolved_at,
                    "override_granted": violation.override_granted,
                }
                violations_data.append(violation_dict)

            violations_file = self.ai_onboard_dir / "hard_limits_violations.json"
            utils.write_json(violations_file, violations_data)

        except Exception as e:
            print(f"Warning: Could not save hard limits violations: {e}")

    def _limits_to_dict(self, limits: ActivityLimits) -> Dict[str, Any]:
        """Convert limits object to dictionary."""
        return {
            "max_files_created_per_hour": limits.max_files_created_per_hour,
            "max_files_deleted_per_hour": limits.max_files_deleted_per_hour,
            "max_files_modified_per_hour": limits.max_files_modified_per_hour,
            "max_files_in_refactor": limits.max_files_in_refactor,
            "max_refactor_complexity": limits.max_refactor_complexity,
            "max_changes_per_minute": limits.max_changes_per_minute,
            "max_changes_per_hour": limits.max_changes_per_hour,
            "max_dependencies_added_per_hour": limits.max_dependencies_added_per_hour,
            "file_operation_window": limits.file_operation_window,
            "change_rate_window": limits.change_rate_window,
            "refactoring_window": limits.refactoring_window,
        }


def get_hard_limits_enforcer(project_root: Path) -> HardLimitsEnforcer:
    """Get or create hard limits enforcer for the project."""
    return HardLimitsEnforcer(project_root)
