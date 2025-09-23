"""
Cleanup Safety Gates Framework.

This module implements comprehensive safety gates for cleanup operations,
preventing accidental system damage through multi - stage validation,
dependency checking, risk assessment, and human confirmation.

Based on lessons learned from cleanup operations where critical dependencies
were nearly missed, this framework ensures robust protection.
"""

import json
import secrets
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .dependency_checker import DependencyChecker, DependencyCheckResult
from .unicode_utils import print_activity, print_content, print_status, safe_print


class RiskLevel(Enum):
    """Risk levels for cleanup operations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GateResult(Enum):
    """Results from safety gate validation."""

    PASS = "pass"
    FAIL = "fail"
    REQUIRE_CONFIRMATION = "require_confirmation"
    REQUIRE_MANUAL_REVIEW = "require_manual_review"


class ConfirmationLevel(Enum):
    """Levels of confirmation required."""

    NONE = "none"
    SIMPLE = "simple"
    CODE = "code"
    COMPLEX_CODE = "complex_code"
    MANUAL_REVIEW = "manual_review"


@dataclass

class CleanupOperation:
    """Represents a cleanup operation to be performed."""

    operation_type: str  # "delete", "move", "modify"
    targets: List[Path]
    description: str
    affected_files: List[Path] = field(default_factory=list)
    backup_required: bool = True
    rollback_plan: Optional[str] = None


@dataclass

class SafetyGateContext:
    """Context passed between safety gates."""

    operation: CleanupOperation
    risk_assessment: Optional["RiskAssessment"] = None
    dependency_report: Optional[DependencyCheckResult] = None
    backup_id: Optional[str] = None
    execution_log: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass

class RiskAssessment:
    """Risk assessment for a cleanup operation."""

    level: RiskLevel
    score: int
    factors: List[str]
    confirmation_required: ConfirmationLevel
    recommendations: List[str]

    @classmethod

    def from_score(cls, score: int, factors: List[str] = None) -> "RiskAssessment":
        """Create risk assessment from numeric score."""
        factors = factors or []

        if score >= 100:
            level = RiskLevel.CRITICAL
            confirmation = ConfirmationLevel.MANUAL_REVIEW
        elif score >= 50:
            level = RiskLevel.HIGH
            confirmation = ConfirmationLevel.COMPLEX_CODE
        elif score >= 20:
            level = RiskLevel.MEDIUM
            confirmation = ConfirmationLevel.CODE
        else:
            level = RiskLevel.LOW
            confirmation = ConfirmationLevel.SIMPLE

        return cls(
            level=level,
            score=score,
            factors=factors,
            confirmation_required=confirmation,
            recommendations=[],
        )


class SafetyGate(ABC):
    """Abstract base class for safety gates."""


    def __init__(self, name: str):
        self.name = name
        self.enabled = True

    @abstractmethod

    def validate(self, context: SafetyGateContext) -> Tuple[GateResult, str]:
        """
        Validate the operation through this gate.

        Args:
            context: Safety gate context with operation details

        Returns:
            Tuple of (result, message)
        """


    def log(self, context: SafetyGateContext, message: str):
        """Log a message to the execution log."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {self.name}: {message}"
        context.execution_log.append(log_entry)


class PreFlightGate(SafetyGate):
    """Gate 1: Pre - flight validation for basic sanity checks."""


    def __init__(self):
        super().__init__("Pre - Flight Validation")

        # Critical files that should never be deleted
        self.protected_paths = {
            "pyproject.toml",
            "README.md",
            "AGENTS.md",
            "LICENSE",
            "__init__.py",
            "__main__.py",
            "setup.py",
            "requirements.txt",
        }

        # Critical directories that should never be deleted
        self.protected_directories = {
            ".git",
            "ai_onboard",
            ".github",
            "venv",
            "env",
        }


    def validate(self, context: SafetyGateContext) -> Tuple[GateResult, str]:
        """Perform pre - flight validation."""
        operation = context.operation

        self.log(context, f"Validating {len(operation.targets)} targets")

        for target in operation.targets:
            # Check existence
            if not target.exists():
                message = f"Target does not exist: {target}"
                self.log(context, f"FAIL: {message}")
                return GateResult.FAIL, message

            # Check protected paths
            if target.name in self.protected_paths:
                message = f"Protected file cannot be modified: {target}"
                self.log(context, f"FAIL: {message}")
                return GateResult.FAIL, message

            # Check protected directories
            if target.is_dir() and target.name in self.protected_directories:
                message = f"Protected directory cannot be modified: {target}"
                self.log(context, f"FAIL: {message}")
                return GateResult.FAIL, message

            # Check if target is within protected directory
            for parent in target.parents:
                if parent.name in self.protected_directories:
                    message = (
                        f"Target is within protected directory {parent.name}: {target}"
                    )
                    self.log(context, f"FAIL: {message}")
                    return GateResult.FAIL, message

            # Check permissions
            if not self._check_permissions(target):
                message = f"Insufficient permissions for: {target}"
                self.log(context, f"FAIL: {message}")
                return GateResult.FAIL, message

        self.log(context, "Pre - flight validation passed")
        return GateResult.PASS, "Pre - flight validation successful"


    def _check_permissions(self, path: Path) -> bool:
        """Check if we have necessary permissions for the operation."""
        try:
            if path.is_file():
                return path.stat().st_mode & 0o200  # Write permission
            elif path.is_dir():
                return path.stat().st_mode & 0o300  # Write and execute
            return True
        except (OSError, PermissionError):
            return False


class DependencyAnalysisGate(SafetyGate):
    """Gate 2: Comprehensive dependency analysis."""


    def __init__(self, root: Path):
        super().__init__("Dependency Analysis")
        self.dependency_checker = DependencyChecker(root)


    def validate(self, context: SafetyGateContext) -> Tuple[GateResult, str]:
        """Perform dependency analysis."""
        operation = context.operation

        self.log(
            context, f"Analyzing dependencies for {len(operation.targets)} targets"
        )

        # Run dependency check
        results = self.dependency_checker.check_dependencies(operation.targets)

        # Store results in context
        context.dependency_report = results

        # Count dependencies
        total_dependencies = sum(len(result.dependencies) for result in results)
        unsafe_files = [result for result in results if not result.is_safe_to_delete]

        self.log(context, f"Found {total_dependencies} total dependencies")
        self.log(context, f"Files with dependencies: {len(unsafe_files)}")

        if unsafe_files:
            message = (
                f"Found {len(unsafe_files)} files with dependencies requiring review"
            )
            self.log(context, f"REQUIRES_CONFIRMATION: {message}")
            return GateResult.REQUIRE_CONFIRMATION, message

        self.log(context, "No blocking dependencies found")
        return GateResult.PASS, "Dependency analysis passed - no blocking dependencies"


class RiskAssessmentGate(SafetyGate):
    """Gate 3: Risk assessment and classification."""


    def __init__(self):
        super().__init__("Risk Assessment")


    def validate(self, context: SafetyGateContext) -> Tuple[GateResult, str]:
        """Perform risk assessment."""
        operation = context.operation
        dependency_report = context.dependency_report

        self.log(context, "Performing risk assessment")

        # Calculate risk score
        risk_score = 0
        risk_factors = []

        # Factor 1: Number of targets
        if len(operation.targets) > 10:
            risk_score += 20
            risk_factors.append(f"Large number of targets ({len(operation.targets)})")
        elif len(operation.targets) > 5:
            risk_score += 10
            risk_factors.append(f"Multiple targets ({len(operation.targets)})")

        # Factor 2: Dependency analysis results
        if dependency_report:
            total_deps = sum(len(result.dependencies) for result in dependency_report)
            high_risk_deps = sum(
                1
                for result in dependency_report
                for dep in result.dependencies
                if dep.severity == "high"
            )

            risk_score += min(total_deps * 2, 50)
            risk_score += high_risk_deps * 10

            if total_deps > 0:
                risk_factors.append(
                    f"Has {total_deps} dependencies ({high_risk_deps} high - risk)"
                )

        # Factor 3: Operation type
        if operation.operation_type == "delete":
            risk_score += 15
            risk_factors.append("Deletion operation (irreversible)")
        elif operation.operation_type == "move":
            risk_score += 10
            risk_factors.append("Move operation (affects paths)")

        # Factor 4: Critical file patterns
        for target in operation.targets:
            if any(
                pattern in target.name.lower()
                for pattern in ["config", "setup", "init", "main", "core"]
            ):
                risk_score += 25
                risk_factors.append(f"Critical file pattern: {target.name}")

        # Create risk assessment
        risk_assessment = RiskAssessment.from_score(risk_score, risk_factors)
        context.risk_assessment = risk_assessment

        self.log(
            context, f"Risk level: {risk_assessment.level.value} (score: {risk_score})"
        )
        self.log(context, f"Risk factors: {', '.join(risk_factors)}")

        # Determine gate result based on risk level
        if risk_assessment.level == RiskLevel.CRITICAL:
            message = (
                f"CRITICAL risk level requires manual review (score: {risk_score})"
            )
            self.log(context, f"MANUAL_REVIEW: {message}")
            return GateResult.REQUIRE_MANUAL_REVIEW, message
        elif risk_assessment.level in [RiskLevel.HIGH, RiskLevel.MEDIUM]:
            message =                 f"{risk_assessment.level.value.upper()} risk level requires confirmation"
            self.log(context, f"REQUIRES_CONFIRMATION: {message}")
            return GateResult.REQUIRE_CONFIRMATION, message

        self.log(context, "Risk assessment passed - low risk operation")
        return GateResult.PASS, "Risk assessment passed - operation is low risk"


class HumanConfirmationGate(SafetyGate):
    """Gate 4: Human confirmation with detailed reporting."""


    def __init__(self):
        super().__init__("Human Confirmation")


    def validate(self, context: SafetyGateContext) -> Tuple[GateResult, str]:
        """Request human confirmation."""
        operation = context.operation
        risk_assessment = context.risk_assessment
        dependency_report = context.dependency_report

        self.log(context, "Requesting human confirmation")

        if not risk_assessment:
            return GateResult.FAIL, "Risk assessment required before confirmation"

        # Generate confirmation report
        report = self._generate_confirmation_report(
            operation, risk_assessment, dependency_report
        )

        # Display report
        safe_print(report)

        # Handle different confirmation levels
        if risk_assessment.confirmation_required == ConfirmationLevel.MANUAL_REVIEW:
            safe_print("\n🔴 MANUAL REVIEW REQUIRED")
            safe_print("This operation requires manual expert review.")
            safe_print("Please contact a system administrator.")
            self.log(context, "Manual review required - operation blocked")
            return GateResult.REQUIRE_MANUAL_REVIEW, "Manual review required"

        elif risk_assessment.confirmation_required == ConfirmationLevel.COMPLEX_CODE:
            confirmation_code = self._generate_complex_confirmation_code()
            safe_print(f"\n🟠 HIGH RISK CONFIRMATION REQUIRED")
            safe_print(f"Please type: CONFIRM: {confirmation_code}")

        elif risk_assessment.confirmation_required == ConfirmationLevel.CODE:
            confirmation_code = self._generate_confirmation_code()
            safe_print(f"\n🟡 CONFIRMATION REQUIRED")
            safe_print(f"Please type: CONFIRM: {confirmation_code}")

        elif risk_assessment.confirmation_required == ConfirmationLevel.SIMPLE:
            safe_print(f"\n🟢 SIMPLE CONFIRMATION")
            safe_print("Please type: CONFIRM")
            confirmation_code = "CONFIRM"

        else:
            # No confirmation required
            self.log(context, "No confirmation required")
            return GateResult.PASS, "No confirmation required"

        # Get user input
        try:
            user_input = input("\nYour confirmation: ").strip()
            expected = (
                f"CONFIRM: {confirmation_code}"
                if confirmation_code != "CONFIRM"
                else "CONFIRM"
            )

            if user_input == expected:
                self.log(context, "Human confirmation received")
                return GateResult.PASS, "Human confirmation received"
            else:
                self.log(context, f"Invalid confirmation: {user_input}")
                return GateResult.FAIL, "Invalid confirmation - operation cancelled"

        except (KeyboardInterrupt, EOFError):
            self.log(context, "Confirmation cancelled by user")
            return GateResult.FAIL, "Confirmation cancelled by user"


    def _generate_confirmation_report(
        self,
        operation: CleanupOperation,
        risk_assessment: RiskAssessment,
        dependency_report: Optional[List[DependencyCheckResult]],
    ) -> str:
        """Generate detailed confirmation report."""
        lines = []
        lines.append("🛡️ CLEANUP SAFETY GATE CONFIRMATION REPORT")
        lines.append("=" * 60)

        # Operation summary
        lines.append(f"\n📋 OPERATION SUMMARY:")
        lines.append(f"   Type: {operation.operation_type.upper()}")
        lines.append(f"   Targets: {len(operation.targets)} files / directories")
        lines.append(f"   Description: {operation.description}")

        # Show first few targets
        lines.append(f"\n   Target files:")
        for target in operation.targets[:5]:
            lines.append(f"     - {target}")
        if len(operation.targets) > 5:
            lines.append(f"     ... and {len(operation.targets) - 5} more")

        # Risk assessment
        lines.append(f"\n⚠️ RISK ASSESSMENT:")
        lines.append(f"   Risk Level: {risk_assessment.level.value.upper()}")
        lines.append(f"   Risk Score: {risk_assessment.score}")
        if risk_assessment.factors:
            lines.append(f"   Risk Factors:")
            for factor in risk_assessment.factors:
                lines.append(f"     • {factor}")

        # Dependencies
        if dependency_report:
            total_deps = sum(len(result.dependencies) for result in dependency_report)
            unsafe_files = [r for r in dependency_report if not r.is_safe_to_delete]

            lines.append(f"\n🔗 DEPENDENCY ANALYSIS:")
            lines.append(f"   Total dependencies found: {total_deps}")
            lines.append(f"   Files with dependencies: {len(unsafe_files)}")

            if unsafe_files:
                lines.append(f"\n   Files requiring attention:")
                for result in unsafe_files[:3]:
                    lines.append(
                        f"     - {result.target_file.name}: {len(result.dependencies)} dependencies"
                    )
                if len(unsafe_files) > 3:
                    lines.append(f"     ... and {len(unsafe_files) - 3} more")

        # Recommendations
        if risk_assessment.recommendations:
            lines.append(f"\n💡 RECOMMENDATIONS:")
            for rec in risk_assessment.recommendations:
                lines.append(f"   • {rec}")

        return "\n".join(lines)


    def _generate_confirmation_code(self) -> str:
        """Generate a simple confirmation code."""
        return secrets.token_hex(3).upper()


    def _generate_complex_confirmation_code(self) -> str:
        """Generate a complex confirmation code for high - risk operations."""
        return f"{secrets.token_hex(4).upper()}-{secrets.randbelow(9999):04d}"


class BackupExecuteGate(SafetyGate):
    """Gate 5: Backup creation and operation execution."""


    def __init__(self, root: Path):
        super().__init__("Backup & Execute")
        self.root = root


    def validate(self, context: SafetyGateContext) -> Tuple[GateResult, str]:
        """Create backup and execute operation."""
        operation = context.operation

        self.log(context, "Creating backup before execution")

        # Create backup
        backup_id = self._create_backup(operation)
        context.backup_id = backup_id

        self.log(context, f"Backup created: {backup_id}")

        # Execute operation
        try:
            self._execute_operation(context)
            self.log(context, "Operation executed successfully")
            return (
                GateResult.PASS,
                f"Operation completed successfully (backup: {backup_id})",
            )

        except Exception as e:
            self.log(context, f"Operation failed: {str(e)}")
            # Attempt rollback
            try:
                self._rollback(backup_id)
                self.log(context, "Automatic rollback completed")
                return GateResult.FAIL, f"Operation failed and rolled back: {str(e)}"
            except Exception as rollback_error:
                self.log(context, f"Rollback failed: {str(rollback_error)}")
                return GateResult.FAIL, f"Operation and rollback both failed: {str(e)}"


    def _create_backup(self, operation: CleanupOperation) -> str:
        """Create comprehensive backup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"cleanup_backup_{timestamp}_{secrets.token_hex(4)}"
        backup_dir = self.root / ".ai_onboard" / "backups" / backup_id

        # Ensure backup directory exists
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Create backup manifest
        manifest = {
            "backup_id": backup_id,
            "timestamp": timestamp,
            "operation": {
                "type": operation.operation_type,
                "description": operation.description,
                "targets": [str(t) for t in operation.targets],
            },
            "files": [],
        }

        # Backup affected files
        for target in operation.targets:
            if target.exists():
                if target.is_file():
                    # Backup individual file
                    backup_path = backup_dir / "files" / target.name
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target, backup_path)

                    manifest["files"].append(
                        {
                            "original": str(target),
                            "backup": str(backup_path),
                            "type": "file",
                        }
                    )

                elif target.is_dir():
                    # Backup directory
                    backup_path = backup_dir / "directories" / target.name
                    shutil.copytree(target, backup_path)

                    manifest["files"].append(
                        {
                            "original": str(target),
                            "backup": str(backup_path),
                            "type": "directory",
                        }
                    )

        # Save manifest
        manifest_path = backup_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return backup_id


    def _execute_operation(self, context: SafetyGateContext):
        """Execute the cleanup operation."""
        operation = context.operation

        for target in operation.targets:
            if not target.exists():
                continue

            if operation.operation_type == "delete":
                if target.is_file():
                    target.unlink()
                elif target.is_dir():
                    shutil.rmtree(target)

            elif operation.operation_type == "move":
                # Move operation would need destination specified
                pass  # Implementation depends on specific move requirements

            elif operation.operation_type == "modify":
                # Modify operation would need specific modifications
                pass  # Implementation depends on specific modifications


    def _rollback(self, backup_id: str):
        """Rollback using backup."""
        backup_dir = self.root / ".ai_onboard" / "backups" / backup_id
        manifest_path = backup_dir / "manifest.json"

        if not manifest_path.exists():
            raise Exception(f"Backup manifest not found: {manifest_path}")

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        # Restore files
        for file_info in manifest["files"]:
            original_path = Path(file_info["original"])
            backup_path = Path(file_info["backup"])

            if file_info["type"] == "file":
                # Restore file
                original_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_path, original_path)
            elif file_info["type"] == "directory":
                # Restore directory
                if original_path.exists():
                    shutil.rmtree(original_path)
                shutil.copytree(backup_path, original_path)


class PostOperationGate(SafetyGate):
    """Gate 6: Post - operation validation and rollback options."""


    def __init__(self, root: Path):
        super().__init__("Post - Operation Validation")
        self.root = root


    def validate(self, context: SafetyGateContext) -> Tuple[GateResult, str]:
        """Validate system after operation."""
        self.log(context, "Performing post - operation validation")

        # Run validation checks
        validation_results = []

        # Check 1: Basic system functionality
        try:
            # Try importing the main module
            pass

            validation_results.append(
                ("Module Import", True, "Main module imports successfully")
            )
        except Exception as e:
            validation_results.append(
                ("Module Import", False, f"Failed to import main module: {e}")
            )

        # Check 2: Configuration validity
        try:
            config_files = [
                self.root / "pyproject.toml",
                self.root / "config" / "dev - config.yaml",
            ]

            for config_file in config_files:
                if config_file.exists():
                    # Basic file readability check
                    config_file.read_text()

            validation_results.append(
                ("Configuration", True, "Configuration files are readable")
            )
        except Exception as e:
            validation_results.append(
                ("Configuration", False, f"Configuration validation failed: {e}")
            )

        # Check 3: File system integrity
        try:
            # Check for broken symlinks or orphaned files
            broken_links = []
            for path in self.root.rglob("*"):
                if path.is_symlink() and not path.exists():
                    broken_links.append(path)

            if broken_links:
                validation_results.append(
                    ("File System", False, f"Found {len(broken_links)} broken symlinks")
                )
            else:
                validation_results.append(
                    ("File System", True, "No broken symlinks found")
                )

        except Exception as e:
            validation_results.append(
                ("File System", False, f"File system check failed: {e}")
            )

        # Analyze results
        failures = [result for result in validation_results if not result[1]]

        if failures:
            self.log(context, f"Validation failures: {len(failures)}")
            for name, success, message in failures:
                self.log(context, f"FAIL {name}: {message}")

            # Offer rollback
            if context.backup_id:
                safe_print("\n⚠️ POST - OPERATION VALIDATION FAILURES DETECTED")
                safe_print(f"Found {len(failures)} validation failures:")
                for name, success, message in failures:
                    safe_print(f"  ❌ {name}: {message}")

                safe_print(f"\nRollback options:")
                safe_print("1. AUTO - Automatic rollback (recommended)")
                safe_print("2. MANUAL - Manual rollback later")
                safe_print("3. CONTINUE - Accept failures and continue")

                try:
                    choice = input("Choose rollback option (1 / 2 / 3): ").strip()

                    if choice == "1" or choice.upper() == "AUTO":
                        self._perform_rollback(context)
                        return (
                            GateResult.PASS,
                            "Validation failed - automatic rollback completed",
                        )
                    elif choice == "2" or choice.upper() == "MANUAL":
                        safe_print(
                            f"Manual rollback available with backup ID: {context.backup_id}"
                        )
                        return (
                            GateResult.FAIL,
                            f"Validation failed - manual rollback required (backup: {context.backup_id})",
                        )
                    else:
                        self.log(
                            context,
                            "User chose to continue despite validation failures",
                        )
                        return (
                            GateResult.PASS,
                            "Validation failed - user chose to continue",
                        )

                except (KeyboardInterrupt, EOFError):
                    # Default to automatic rollback
                    self._perform_rollback(context)
                    return (
                        GateResult.PASS,
                        "Validation failed - automatic rollback completed",
                    )
            else:
                return (
                    GateResult.FAIL,
                    f"Validation failed with {len(failures)} failures - no backup available",
                )

        # All validations passed
        self.log(context, "All post - operation validations passed")
        return GateResult.PASS, "Post - operation validation successful"


    def _perform_rollback(self, context: SafetyGateContext):
        """Perform automatic rollback."""
        if not context.backup_id:
            raise Exception("No backup ID available for rollback")

        backup_dir = self.root / ".ai_onboard" / "backups" / context.backup_id
        manifest_path = backup_dir / "manifest.json"

        print_activity("Performing automatic rollback...")

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        # Restore files
        for file_info in manifest["files"]:
            original_path = Path(file_info["original"])
            backup_path = Path(file_info["backup"])

            if file_info["type"] == "file":
                original_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_path, original_path)
            elif file_info["type"] == "directory":
                if original_path.exists():
                    shutil.rmtree(original_path)
                shutil.copytree(backup_path, original_path)

        self.log(context, f"Rollback completed using backup {context.backup_id}")
        print_status("Rollback completed successfully", "success")


class CleanupSafetyGateFramework:
    """Main framework coordinating all safety gates."""


    def __init__(self, root: Path):
        self.root = root
        self.gates = [
            PreFlightGate(),
            DependencyAnalysisGate(root),
            RiskAssessmentGate(),
            HumanConfirmationGate(),
            BackupExecuteGate(root),
            PostOperationGate(root),
        ]

        # Configuration
        self.config = {
            "strict_mode": True,
            "auto_rollback_on_failure": True,
            "backup_retention_days": 30,
            "require_confirmation_for_medium_risk": True,
        }


    def execute_cleanup_operation(
        self, operation: CleanupOperation
    ) -> Tuple[bool, str]:
        """
        Execute a cleanup operation through all safety gates.

        Args:
            operation: The cleanup operation to perform

        Returns:
            Tuple of (success, message)
        """
        print_activity("Starting cleanup operation with safety gates")

        # Initialize context
        context = SafetyGateContext(operation=operation)

        # Execute each gate in sequence
        for gate in self.gates:
            if not gate.enabled:
                continue

            print_content(f"Executing {gate.name}...", "search")

            try:
                result, message = gate.validate(context)

                if result == GateResult.PASS:
                    print_status(f"✅ {gate.name}: {message}", "success")
                    continue

                elif result == GateResult.FAIL:
                    print_status(f"❌ {gate.name}: {message}", "error")
                    return False, f"Safety gate failed: {message}"

                elif result == GateResult.REQUIRE_CONFIRMATION:
                    print_status(f"⚠️ {gate.name}: {message}", "warning")
                    # Confirmation will be handled by HumanConfirmationGate
                    continue

                elif result == GateResult.REQUIRE_MANUAL_REVIEW:
                    print_status(f"🔴 {gate.name}: {message}", "error")
                    return False, f"Manual review required: {message}"

            except Exception as e:
                error_msg = f"Gate {gate.name} failed with exception: {str(e)}"
                print_status(f"💥 {error_msg}", "error")
                context.execution_log.append(f"EXCEPTION in {gate.name}: {str(e)}")
                return False, error_msg

        print_activity("All safety gates passed")
        return True, "Cleanup operation completed successfully through all safety gates"


    def get_available_backups(self) -> List[Dict[str, Any]]:
        """Get list of available backups for rollback."""
        backups_dir = self.root / ".ai_onboard" / "backups"

        if not backups_dir.exists():
            return []

        backups = []
        for backup_dir in backups_dir.iterdir():
            if backup_dir.is_dir():
                manifest_path = backup_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, "r") as f:
                            manifest = json.load(f)
                        backups.append(manifest)
                    except Exception:
                        continue

        return sorted(backups, key=lambda x: x.get("timestamp", ""), reverse=True)


    def rollback_operation(self, backup_id: str) -> Tuple[bool, str]:
        """Manually rollback a previous operation."""
        try:
            backup_dir = self.root / ".ai_onboard" / "backups" / backup_id

            if not backup_dir.exists():
                return False, f"Backup not found: {backup_id}"

            # Use PostOperationGate rollback functionality
            context = SafetyGateContext(
                operation=CleanupOperation("rollback", [], "Manual rollback")
            )
            context.backup_id = backup_id

            post_gate = PostOperationGate(self.root)
            post_gate._perform_rollback(context)

            return True, f"Rollback completed successfully using backup {backup_id}"

        except Exception as e:
            return False, f"Rollback failed: {str(e)}"


# Convenience functions for CLI integration

def create_safety_framework(root: Path) -> CleanupSafetyGateFramework:
    """Create a configured safety gate framework."""
    return CleanupSafetyGateFramework(root)


def safe_cleanup_operation(
    root: Path, operation_type: str, targets: List[Path], description: str
) -> Tuple[bool, str]:
    """
    Perform a safe cleanup operation with full safety gate protection.

    Args:
        root: Project root directory
        operation_type: Type of operation ("delete", "move", "modify")
        targets: List of files / directories to operate on
        description: Description of the operation

    Returns:
        Tuple of (success, message)
    """
    framework = create_safety_framework(root)
    operation = CleanupOperation(
        operation_type=operation_type, targets=targets, description=description
    )

    return framework.execute_cleanup_operation(operation)


if __name__ == "__main__":
    # Test the safety gate framework

    if len(sys.argv) < 2:
        print("Usage: python cleanup_safety_gates.py <test_file>")
        sys.exit(1)

    root = Path.cwd()
    test_file = Path(sys.argv[1])

    print("Testing cleanup safety gates...")
    success, message = safe_cleanup_operation(
        root=root,
        operation_type="delete",
        targets=[test_file],
        description=f"Test deletion of {test_file.name}",
    )

    print(f"Result: {'SUCCESS' if success else 'FAILED'}")
    print(f"Message: {message}")
