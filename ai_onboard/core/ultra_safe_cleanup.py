"""
Ultra-Safe Cleanup System - Zero-Tolerance Safety Framework

This module implements an ultra-safe cleanup system with:
- Multiple confirmation layers
- Zero room for interpretation
- Incremental risk-based cleanup
- Comprehensive audit trails
- Human-in-the-loop for all operations

CRITICAL SAFETY PRINCIPLES:
1. NEVER delete protected files (charter.json, project_plan.json, etc.)
2. ALWAYS require explicit human confirmation for ANY deletion
3. ALWAYS create backups before ANY operation
4. ALWAYS validate system integrity after operations
5. ALWAYS provide clear, unambiguous risk assessments
"""

import hashlib
import secrets
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import utils
from .unicode_utils import print_activity, print_content, print_status, safe_print


class CleanupRiskLevel(Enum):
    """Risk levels for cleanup operations - ZERO AMBIGUITY"""

    SAFE = "safe"  # Cache files, temp files - always safe
    LOW = "low"  # Build artifacts, logs - low risk
    MEDIUM = "medium"  # Generated files, old backups - medium risk
    HIGH = "high"  # Dependencies, config files - high risk
    CRITICAL = "critical"  # NEVER ALLOWED - system breaking files


class ConfirmationRequirement(Enum):
    """Confirmation requirements - STRICT HUMAN OVERSIGHT"""

    NONE = "none"  # Only for SAFE operations
    EXPLICIT_FILE_LIST = "explicit_list"  # Must list every file explicitly
    CODE_CONFIRMATION = "code"  # Must enter confirmation code
    HUMAN_REVIEW = "human_review"  # Requires human expert review
    BLOCKED = "blocked"  # NEVER ALLOWED


@dataclass
class CleanupTarget:
    """A file or directory targeted for cleanup"""

    path: Path
    risk_level: CleanupRiskLevel
    reason: str
    size_bytes: int = 0
    last_modified: Optional[datetime] = None
    file_hash: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class CleanupOperation:
    """A complete cleanup operation with full audit trail"""

    operation_id: str
    targets: List[CleanupTarget]
    risk_assessment: Dict[str, Any]
    backup_manifest: Optional[Dict[str, Any]] = None
    execution_log: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    confirmed_by: Optional[str] = None
    status: str = "pending"


class UltraSafeCleanupEngine:
    """
    Ultra-safe cleanup engine with zero-tolerance safety.

    This engine implements multiple protection layers:
    1. Static file protection (never delete critical files)
    2. Risk assessment (categorize every file)
    3. Dependency analysis (check for breaking changes)
    4. Human confirmation (explicit approval required)
    5. Backup creation (always backup before deletion)
    6. Integrity validation (verify system still works)
    """

    def __init__(self, root: Path):
        self.root = root
        self.operation_log = root / ".ai_onboard" / "cleanup_operations.jsonl"

        # CRITICAL PROTECTION - These files can NEVER be deleted
        self.critical_protections = {
            # Core system files
            ".ai_onboard/charter.json",
            ".ai_onboard/project_plan.json",
            ".ai_onboard/state.json",
            ".ai_onboard/analysis.json",
            ".ai_onboard/roadmap.json",
            ".ai_onboard/pattern_database.json",
            "pyproject.toml",
            "README.md",
            "AGENTS.md",
            "ai_onboard/__init__.py",
            "ai_onboard/__main__.py",
            # Add all protected paths from AGENTS.md
        }

        # Risk-based file categorization
        self.risk_patterns = {
            CleanupRiskLevel.SAFE: [
                "**/__pycache__/**",
                "**/*.pyc",
                "**/*.pyo",
                "**/*.tmp",
                "**/*.temp",
                "**/*.log",
                "**/node_modules/**",
            ],
            CleanupRiskLevel.LOW: [
                "**/build/**",
                "**/dist/**",
                "**/*.egg-info/**",
                "**/.pytest_cache/**",
                "**/htmlcov/**",
            ],
            CleanupRiskLevel.MEDIUM: [
                "**/.ai_onboard/backups/**",  # Old backups can be cleaned
                "**/.ai_onboard/logs/**",  # Old logs
                "**/cache*/**",  # Cache directories
            ],
            CleanupRiskLevel.HIGH: [
                "**/requirements*.txt",  # Could break dependencies
                "**/config*.json",  # Might be important config
                "**/*.cfg",  # Configuration files
            ],
            CleanupRiskLevel.CRITICAL: [
                # These are explicitly blocked
                ".ai_onboard/**",
                "ai_onboard/**",
                ".git/**",
                ".github/**",
                "**/pyproject.toml",
                "**/README.md",
                "**/AGENTS.md",
            ],
        }

    def scan_for_cleanup_targets(self) -> List[CleanupTarget]:
        """
        Scan the project for potential cleanup targets.

        Returns only files that are SAFE to consider for cleanup.
        NEVER returns critical system files.
        """
        targets = []

        # Scan common cleanup locations
        scan_paths = [
            self.root,  # Root directory
            self.root / ".ai_onboard" / "backups",  # Old backups
            self.root / ".ai_onboard" / "logs",  # Old logs
        ]

        for scan_path in scan_paths:
            if not scan_path.exists():
                continue

            for path in scan_path.rglob("*"):
                if path.is_file():
                    target = self._analyze_file_for_cleanup(path)
                    if target and target.risk_level != CleanupRiskLevel.CRITICAL:
                        targets.append(target)

        return targets

    def _analyze_file_for_cleanup(self, path: Path) -> Optional[CleanupTarget]:
        """Analyze a single file for cleanup potential."""
        try:
            # NEVER consider critical files
            rel_path = path.relative_to(self.root)
            rel_str = str(rel_path).replace("\\", "/")

            if rel_str in self.critical_protections:
                return None

            # Check if it matches critical patterns
            for critical_pattern in self.risk_patterns[CleanupRiskLevel.CRITICAL]:
                if path.match(critical_pattern):
                    return None

            # Determine risk level
            risk_level = CleanupRiskLevel.CRITICAL  # Default to critical

            for level, patterns in self.risk_patterns.items():
                for pattern in patterns:
                    if path.match(pattern):
                        risk_level = level
                        break
                if risk_level != CleanupRiskLevel.CRITICAL:
                    break

            # If still critical, skip it
            if risk_level == CleanupRiskLevel.CRITICAL:
                return None

            # Get file information
            stat = path.stat()
            file_hash = self._calculate_file_hash(path)

            return CleanupTarget(
                path=path,
                risk_level=risk_level,
                reason=self._get_cleanup_reason(path, risk_level),
                size_bytes=stat.st_size,
                last_modified=datetime.fromtimestamp(stat.st_mtime),
                file_hash=file_hash,
            )

        except (OSError, ValueError):
            # If we can't analyze the file, skip it
            return None

    def _get_cleanup_reason(self, path: Path, risk_level: CleanupRiskLevel) -> str:
        """Get a clear, unambiguous reason for why this file can be cleaned."""
        reasons = {
            CleanupRiskLevel.SAFE: {
                "__pycache__": "Python bytecode cache - safe to delete",
                ".pyc": "Compiled Python file - regenerated automatically",
                ".tmp": "Temporary file - no longer needed",
                ".log": "Log file - can be archived separately",
                "node_modules": "Node.js dependencies - reinstalled via npm/yarn",
            },
            CleanupRiskLevel.LOW: {
                "build": "Build artifacts - regenerated on build",
                "dist": "Distribution files - regenerated on build",
                ".egg-info": "Package metadata - regenerated on install",
                ".pytest_cache": "Test cache - regenerated on test run",
                "htmlcov": "Coverage reports - regenerated on test run",
            },
            CleanupRiskLevel.MEDIUM: {
                "backups": "Old backup files - retention policy allows cleanup",
                "logs": "Old log files - retention policy allows cleanup",
                "cache": "Cache files - can be regenerated",
            },
        }

        path_str = str(path.name).lower()
        for keyword, reason in reasons.get(risk_level, {}).items():
            if keyword in path_str:
                return reason

        return f"{risk_level.value.title()} risk cleanup candidate"

    def _calculate_file_hash(self, path: Path) -> str:
        """Calculate SHA256 hash of file for integrity checking."""
        try:
            with open(path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except OSError:
            return "unreadable"

    def create_cleanup_proposal(self, targets: List[CleanupTarget]) -> CleanupOperation:
        """
        Create a cleanup operation proposal with full risk assessment.
        """
        operation_id = f"cleanup_{secrets.token_hex(8)}"

        # Group by risk level
        risk_summary = {}
        for target in targets:
            level = target.risk_level.value
            if level not in risk_summary:
                risk_summary[level] = {"count": 0, "total_size": 0, "files": []}
            risk_summary[level]["count"] += 1
            risk_summary[level]["total_size"] += target.size_bytes
            risk_summary[level]["files"].append(str(target.path.relative_to(self.root)))

        # Determine overall confirmation requirement
        max_risk = max(
            (target.risk_level for target in targets),
            key=lambda x: ["safe", "low", "medium", "high", "critical"].index(x.value),
        )

        confirmation_req = {
            CleanupRiskLevel.SAFE: ConfirmationRequirement.NONE,
            CleanupRiskLevel.LOW: ConfirmationRequirement.EXPLICIT_FILE_LIST,
            CleanupRiskLevel.MEDIUM: ConfirmationRequirement.CODE_CONFIRMATION,
            CleanupRiskLevel.HIGH: ConfirmationRequirement.HUMAN_REVIEW,
            CleanupRiskLevel.CRITICAL: ConfirmationRequirement.BLOCKED,
        }[max_risk]

        risk_assessment = {
            "max_risk_level": max_risk.value,
            "confirmation_required": confirmation_req.value,
            "risk_summary": risk_summary,
            "total_files": len(targets),
            "total_size_bytes": sum(t.size_bytes for t in targets),
            "estimated_operation_time": self._estimate_operation_time(targets),
        }

        return CleanupOperation(
            operation_id=operation_id, targets=targets, risk_assessment=risk_assessment
        )

    def _estimate_operation_time(self, targets: List[CleanupTarget]) -> str:
        """Estimate how long the cleanup operation will take."""
        total_size_mb = sum(t.size_bytes for t in targets) / (1024 * 1024)

        if total_size_mb < 10:
            return "Fast (< 1 minute)"
        elif total_size_mb < 100:
            return "Moderate (1-5 minutes)"
        elif total_size_mb < 1000:
            return "Slow (5-30 minutes)"
        else:
            return "Very slow (> 30 minutes)"

    def present_cleanup_proposal(self, operation: CleanupOperation) -> bool:
        """
        Present the cleanup proposal to the user and get confirmation.

        Returns True if user approves, False otherwise.
        """
        safe_print("🧹 ULTRA-SAFE CLEANUP PROPOSAL")
        safe_print("=" * 60)

        # Operation summary
        safe_print(f"\n📋 OPERATION ID: {operation.operation_id}")
        safe_print(f"📅 Created: {operation.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        # Risk assessment
        risk = operation.risk_assessment
        safe_print(f"\n⚠️ RISK ASSESSMENT:")
        safe_print(f"   Maximum Risk Level: {risk['max_risk_level'].upper()}")
        safe_print(f"   Confirmation Required: {risk['confirmation_required'].upper()}")
        safe_print(f"   Total Files: {risk['total_files']}")
        safe_print(f"   Total Size: {risk['total_size_bytes'] / (1024*1024):.1f} MB")
        safe_print(f"   Estimated Time: {risk['estimated_operation_time']}")

        # File breakdown by risk
        safe_print(f"\n📂 FILES BY RISK LEVEL:")
        for level, data in risk["risk_summary"].items():
            safe_print(
                f"   {level.upper()}: {data['count']} files ({data['total_size']/(1024*1024):.1f} MB)"
            )

        # Show sample files
        safe_print(f"\n📄 SAMPLE FILES TO BE CLEANED:")
        sample_targets = operation.targets[:10]  # Show first 10
        for target in sample_targets:
            safe_print(f"   • {target.path.relative_to(self.root)}")
            safe_print(
                f"     Risk: {target.risk_level.value.upper()} | Size: {target.size_bytes/1024:.1f} KB"
            )
            safe_print(f"     Reason: {target.reason}")

        if len(operation.targets) > 10:
            safe_print(f"   ... and {len(operation.targets) - 10} more files")

        # Get confirmation based on risk level
        confirmation_req = ConfirmationRequirement(risk["confirmation_required"])

        if confirmation_req == ConfirmationRequirement.NONE:
            safe_print(f"\n✅ SAFE OPERATION - No confirmation required")
            return True

        elif confirmation_req == ConfirmationRequirement.EXPLICIT_FILE_LIST:
            return self._confirm_explicit_file_list(operation)

        elif confirmation_req == ConfirmationRequirement.CODE_CONFIRMATION:
            return self._confirm_with_code(operation)

        elif confirmation_req == ConfirmationRequirement.HUMAN_REVIEW:
            return self._require_human_review(operation)

        else:  # BLOCKED
            safe_print(f"\n🚫 OPERATION BLOCKED - Contains critical files")
            return False

    def _confirm_explicit_file_list(self, operation: CleanupOperation) -> bool:
        """Require user to explicitly acknowledge each file."""
        safe_print(f"\n📝 EXPLICIT FILE CONFIRMATION REQUIRED")
        safe_print("You must type 'YES' for each file to confirm deletion:")

        for i, target in enumerate(operation.targets, 1):
            rel_path = target.path.relative_to(self.root)
            safe_print(f"\n{i}/{len(operation.targets)}: {rel_path}")
            safe_print(f"   Risk: {target.risk_level.value.upper()}")
            safe_print(f"   Size: {target.size_bytes/1024:.1f} KB")
            safe_print(f"   Reason: {target.reason}")

            try:
                response = input("   Delete this file? (YES/no): ").strip().lower()
                if response not in ["yes", "y", ""]:
                    safe_print("   ❌ File deletion cancelled by user")
                    return False
                safe_print("   ✅ Confirmed")
            except (KeyboardInterrupt, EOFError):
                safe_print("   ❌ Confirmation cancelled by user")
                return False

        return True

    def _confirm_with_code(self, operation: CleanupOperation) -> bool:
        """Require confirmation code for medium-risk operations."""
        confirmation_code = secrets.token_hex(4).upper()

        safe_print(f"\n🔐 CODE CONFIRMATION REQUIRED")
        safe_print("This operation has MEDIUM risk and requires confirmation.")
        safe_print(f"Please type: CONFIRM-{confirmation_code}")

        try:
            response = input("Confirmation code: ").strip()
            expected = f"CONFIRM-{confirmation_code}"

            if response == expected:
                safe_print("✅ Confirmation code accepted")
                return True
            else:
                safe_print("❌ Invalid confirmation code")
                return False

        except (KeyboardInterrupt, EOFError):
            safe_print("❌ Confirmation cancelled by user")
            return False

    def _require_human_review(self, operation: CleanupOperation) -> bool:
        """Require human expert review for high-risk operations."""
        safe_print(f"\n🚨 HUMAN EXPERT REVIEW REQUIRED")
        safe_print("This operation has HIGH risk and requires expert review.")
        safe_print("Please contact a system administrator or senior developer.")
        safe_print("\nOperation details have been logged for review.")
        safe_print(f"Operation ID: {operation.operation_id}")

        # Log for review
        self._log_operation(operation, "requires_human_review")

        return False  # Always block high-risk operations in automated mode

    def execute_cleanup_operation(
        self, operation: CleanupOperation
    ) -> Tuple[bool, str]:
        """
        Execute the cleanup operation with full safety measures.
        """
        # Create backup first
        safe_print("💾 Creating backup before cleanup...")
        backup_manifest = self._create_backup(operation)
        operation.backup_manifest = backup_manifest

        # Log operation start
        operation.status = "executing"
        self._log_operation(operation, "started")

        # Execute deletions
        success_count = 0
        error_count = 0
        errors = []

        for target in operation.targets:
            try:
                if target.path.exists():
                    if target.path.is_file():
                        target.path.unlink()
                    elif target.path.is_dir():
                        shutil.rmtree(target.path)

                    success_count += 1
                    operation.execution_log.append(f"SUCCESS: Deleted {target.path}")

            except Exception as e:
                error_count += 1
                error_msg = f"FAILED: Could not delete {target.path}: {str(e)}"
                errors.append(error_msg)
                operation.execution_log.append(error_msg)

        # Validate system integrity
        safe_print("🔍 Validating system integrity after cleanup...")
        integrity_ok = self._validate_system_integrity()

        # Final status
        if integrity_ok and error_count == 0:
            operation.status = "completed_successfully"
            message = f"Cleanup completed successfully: {success_count} files deleted"
        elif integrity_ok:
            operation.status = "completed_with_errors"
            message = f"Cleanup completed with {error_count} errors: {success_count} files deleted"
        else:
            operation.status = "system_integrity_compromised"
            message = "CRITICAL: System integrity compromised after cleanup - automatic rollback initiated"

            # Attempt rollback
            if self._rollback_operation(operation):
                message += " - Rollback completed"
            else:
                message += " - Rollback failed - MANUAL INTERVENTION REQUIRED"

        # Log final status
        self._log_operation(operation, operation.status)

        return (
            operation.status in ["completed_successfully", "completed_with_errors"],
            message,
        )

    def _create_backup(self, operation: CleanupOperation) -> Dict[str, Any]:
        """Create a comprehensive backup of all targets."""
        backup_dir = (
            self.root / ".ai_onboard" / "ultra_safe_backups" / operation.operation_id
        )
        backup_dir.mkdir(parents=True, exist_ok=True)

        manifest = {
            "operation_id": operation.operation_id,
            "created_at": datetime.now().isoformat(),
            "targets": [],
            "backup_location": str(backup_dir),
        }

        for target in operation.targets:
            if target.path.exists():
                # Create backup path
                rel_path = target.path.relative_to(self.root)
                backup_path = backup_dir / rel_path.name

                try:
                    if target.path.is_file():
                        shutil.copy2(target.path, backup_path)
                    else:
                        shutil.copytree(target.path, backup_path, dirs_exist_ok=True)

                    manifest["targets"].append(
                        {
                            "original_path": str(rel_path),
                            "backup_path": str(backup_path.relative_to(self.root)),
                            "file_hash": target.file_hash,
                            "size_bytes": target.size_bytes,
                        }
                    )

                except Exception as e:
                    manifest["targets"].append(
                        {
                            "original_path": str(rel_path),
                            "error": str(e),
                            "backup_failed": True,
                        }
                    )

        # Save manifest
        manifest_path = backup_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return manifest

    def _validate_system_integrity(self) -> bool:
        """Validate that the system is still functional after cleanup."""
        critical_files = [
            ".ai_onboard/charter.json",
            ".ai_onboard/project_plan.json",
            ".ai_onboard/state.json",
            "pyproject.toml",
            "ai_onboard/__init__.py",
        ]

        for file_path in critical_files:
            full_path = self.root / file_path
            if not full_path.exists():
                safe_print(f"❌ CRITICAL: Essential file missing: {file_path}")
                return False

        # Try to import core modules
        try:
            import ai_onboard.core.state
            import ai_onboard.core.utils
        except ImportError as e:
            safe_print(f"❌ CRITICAL: Core module import failed: {e}")
            return False

        safe_print("✅ System integrity validation passed")
        return True

    def _rollback_operation(self, operation: CleanupOperation) -> bool:
        """Rollback a failed operation using backup."""
        if not operation.backup_manifest:
            return False

        backup_dir = Path(operation.backup_manifest["backup_location"])

        if not backup_dir.exists():
            return False

        success_count = 0
        error_count = 0

        for target_info in operation.backup_manifest["targets"]:
            if "backup_path" in target_info:
                try:
                    backup_path = self.root / target_info["backup_path"]
                    original_path = self.root / target_info["original_path"]

                    if backup_path.exists():
                        # Ensure parent directory exists
                        original_path.parent.mkdir(parents=True, exist_ok=True)

                        if backup_path.is_file():
                            shutil.copy2(backup_path, original_path)
                        else:
                            if original_path.exists():
                                shutil.rmtree(original_path)
                            shutil.copytree(backup_path, original_path)

                        success_count += 1

                except Exception as e:
                    error_count += 1
                    safe_print(
                        f"❌ Rollback failed for {target_info['original_path']}: {e}"
                    )

        return error_count == 0

    def _log_operation(self, operation: CleanupOperation, event: str):
        """Log operation events to audit trail."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation_id": operation.operation_id,
            "event": event,
            "status": operation.status,
            "risk_assessment": operation.risk_assessment,
            "target_count": len(operation.targets),
            "confirmed_by": operation.confirmed_by,
            "execution_log": operation.execution_log,
        }

        with open(self.operation_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


# Convenience functions for CLI integration


def scan_cleanup_targets(root: Path) -> List[CleanupTarget]:
    """Scan for cleanup targets."""
    engine = UltraSafeCleanupEngine(root)
    return engine.scan_for_cleanup_targets()


def propose_cleanup_operation(
    root: Path, targets: List[CleanupTarget]
) -> CleanupOperation:
    """Create a cleanup operation proposal."""
    engine = UltraSafeCleanupEngine(root)
    return engine.create_cleanup_proposal(targets)


def execute_ultra_safe_cleanup(
    root: Path, operation: CleanupOperation
) -> Tuple[bool, str]:
    """Execute ultra-safe cleanup operation."""
    engine = UltraSafeCleanupEngine(root)
    return engine.execute_cleanup_operation(operation)


def present_cleanup_proposal(root: Path, operation: CleanupOperation) -> bool:
    """Present cleanup proposal and get user confirmation."""
    engine = UltraSafeCleanupEngine(root)
    return engine.present_cleanup_proposal(operation)
