"""
Integration tests for cleanup safety gates.

Tests the complete safety gate framework end - to - end,
ensuring all gates work together to prevent system damage.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from ai_onboard.core.quality_safety.cleanup_safety_gates import (
    BackupExecuteGate,
    CleanupOperation,
    CleanupSafetyGateFramework,
    DependencyAnalysisGate,
    HumanConfirmationGate,
    PostOperationGate,
    PreFlightGate,
    RiskAssessmentGate,
    RiskLevel,
    safe_cleanup_operation,
)


class TestCleanupSafetyGatesIntegration(unittest.TestCase):
    """Integration tests for the complete safety gate framework."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.framework = CleanupSafetyGateFramework(self.test_dir)

        # Create test files
        self.test_file = self.test_dir / "test_file.txt"
        self.test_file.write_text("Test content")

        self.protected_file = self.test_dir / "pyproject.toml"
        self.protected_file.write_text("[build - system]\nrequires = ['setuptools']")

        # Create a file with dependencies
        self.dependent_file = self.test_dir / "config.py"
        self.dependent_file.write_text("CONFIG_FILE = 'test_file.txt'")

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_safe_file_deletion_passes_all_gates(self):
        """Test that deleting a safe file passes all gates."""
        # Create a truly safe file (no dependencies)
        safe_file = self.test_dir / "safe_temp.log"
        safe_file.write_text("Temporary log content")

        operation = CleanupOperation(
            operation_type="delete",
            targets=[safe_file],
            description="Delete safe temporary file",
        )

        # Mock human confirmation to auto - approve
        with patch("builtins.input", return_value="CONFIRM"):
            success, message = self.framework.execute_cleanup_operation(operation)

        self.assertTrue(success, f"Safe file deletion should succeed: {message}")
        self.assertFalse(safe_file.exists(), "Safe file should be deleted")

    def test_protected_file_deletion_blocked_by_preflight(self):
        """Test that protected files are blocked by pre - flight gate."""
        operation = CleanupOperation(
            operation_type="delete",
            targets=[self.protected_file],
            description="Attempt to delete protected file",
        )

        success, message = self.framework.execute_cleanup_operation(operation)

        self.assertFalse(success, "Protected file deletion should fail")
        self.assertIn("Protected file", message)
        self.assertTrue(
            self.protected_file.exists(), "Protected file should still exist"
        )

    def test_file_with_dependencies_requires_confirmation(self):
        """Test that files with dependencies require human confirmation."""
        operation = CleanupOperation(
            operation_type="delete",
            targets=[self.test_file],  # This file is referenced in dependent_file
            description="Delete file with dependencies",
        )

        # Mock human confirmation to deny
        with patch("builtins.input", return_value="CANCEL"):
            success, message = self.framework.execute_cleanup_operation(operation)

        self.assertFalse(
            success, "File with dependencies should fail without proper confirmation"
        )
        self.assertTrue(
            self.test_file.exists(), "File should still exist after denied confirmation"
        )

    def test_risk_assessment_escalation(self):
        """Test that high - risk operations require complex confirmation."""
        # Create multiple files to increase risk score
        risk_files = []
        for i in range(15):  # Large number of targets increases risk
            risk_file = self.test_dir / f"risk_file_{i}.py"
            risk_file.write_text(f"import important_module_{i}")
            risk_files.append(risk_file)

        operation = CleanupOperation(
            operation_type="delete",
            targets=risk_files,
            description="Delete many files (high risk)",
        )

        # Test that this generates a high risk assessment
        context = Mock()
        context.operation = operation
        context.dependency_report = []
        context.execution_log = []

        risk_gate = RiskAssessmentGate()
        result, message = risk_gate.validate(context)

        self.assertIn("risk", message.lower())
        self.assertIsNotNone(context.risk_assessment)
        # 15 files should generate at least MEDIUM risk, possibly HIGH
        self.assertIn(
            context.risk_assessment.level,
            [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL],
        )

    def test_backup_and_rollback_functionality(self):
        """Test that backup creation and rollback work correctly."""
        # Create test content
        original_content = "Original content"
        test_file = self.test_dir / "backup_test.txt"
        test_file.write_text(original_content)

        # Create backup manually to test rollback
        backup_gate = BackupExecuteGate(self.test_dir)
        operation = CleanupOperation(
            operation_type="delete",
            targets=[test_file],
            description="Test backup and rollback",
        )

        backup_id = backup_gate._create_backup(operation)

        # Verify backup was created
        backups = self.framework.get_available_backups()
        self.assertTrue(any(b["backup_id"] == backup_id for b in backups))

        # Delete the file
        test_file.unlink()
        self.assertFalse(test_file.exists())

        # Perform rollback
        success, message = self.framework.rollback_operation(backup_id)

        self.assertTrue(success, f"Rollback should succeed: {message}")
        self.assertTrue(test_file.exists(), "File should be restored after rollback")
        self.assertEqual(
            test_file.read_text(), original_content, "Content should be restored"
        )

    def test_post_operation_validation_with_failure(self):
        """Test post - operation validation and automatic rollback."""
        # Create a scenario that will fail post - validation
        test_file = self.test_dir / "validation_test.py"
        test_file.write_text("import ai_onboard")

        operation = CleanupOperation(
            operation_type="delete",
            targets=[test_file],
            description="Test validation failure",
        )

        # Mock post - validation to fail with correct return format
        from ai_onboard.core.quality_safety.cleanup_safety_gates import GateResult

        with patch.object(PostOperationGate, "validate") as mock_validate:
            mock_validate.return_value = (
                GateResult.FAIL,
                "Post - validation failed - test scenario",
            )

            # Mock human confirmation
            with patch("builtins.input", return_value="CONFIRM"):
                success, message = self.framework.execute_cleanup_operation(operation)

        # The operation should fail due to post - validation failure
        self.assertFalse(
            success, "Operation should fail due to post - validation failure"
        )
        self.assertIn("failed", message.lower())

    def test_emergency_rollback_on_exception(self):
        """Test that exceptions during execution trigger emergency rollback."""
        test_file = self.test_dir / "exception_test.txt"
        test_file.write_text("Test content")

        operation = CleanupOperation(
            operation_type="delete",
            targets=[test_file],
            description="Test exception handling",
        )

        # Mock execution to raise an exception
        with patch.object(
            BackupExecuteGate,
            "_execute_operation",
            side_effect=Exception("Test exception"),
        ):
            with patch("builtins.input", return_value="CONFIRM"):
                success, message = self.framework.execute_cleanup_operation(operation)

        self.assertFalse(success, "Operation should fail due to exception")
        self.assertIn("exception", message.lower())
        # File should still exist due to rollback
        self.assertTrue(
            test_file.exists(), "File should be restored after exception rollback"
        )

    def test_configuration_affects_gate_behavior(self):
        """Test that configuration changes affect gate behavior."""
        # Test strict mode configuration
        original_config = self.framework.config.copy()

        # Enable strict mode
        self.framework.config["strict_mode"] = True
        self.framework.config["require_confirmation_for_medium_risk"] = True

        # Create medium - risk operation
        medium_risk_file = self.test_dir / "medium_risk.txt"
        medium_risk_file.write_text("Some content")

        operation = CleanupOperation(
            operation_type="delete",
            targets=[medium_risk_file],
            description="Medium risk operation",
        )

        # Should require confirmation in strict mode
        with patch("builtins.input", return_value="CANCEL"):
            success, message = self.framework.execute_cleanup_operation(operation)

        # Restore original config
        self.framework.config = original_config

        self.assertFalse(
            success, "Strict mode should require confirmation for medium risk"
        )

    def test_multiple_file_operations_with_mixed_risks(self):
        """Test operations involving multiple files with different risk levels."""
        # Create files with different risk profiles
        safe_file = self.test_dir / "safe.log"
        safe_file.write_text("Log content")

        risky_file = self.test_dir / "core_config.py"
        risky_file.write_text("IMPORTANT_SETTING = True")

        # Create a dependency on risky_file
        dependent = self.test_dir / "main.py"
        dependent.write_text("from core_config import IMPORTANT_SETTING")

        operation = CleanupOperation(
            operation_type="delete",
            targets=[safe_file, risky_file],
            description="Mixed risk file deletion",
        )

        # Should be blocked due to high - risk file with dependencies
        success, message = self.framework.execute_cleanup_operation(operation)

        self.assertFalse(
            success, "Mixed risk operation should be blocked by highest risk"
        )
        self.assertTrue(
            safe_file.exists(), "Safe file should remain due to batch failure"
        )
        self.assertTrue(
            risky_file.exists(), "Risky file should remain due to dependencies"
        )

    def test_convenience_function_integration(self):
        """Test the convenience function for safe cleanup operations."""
        safe_file = self.test_dir / "convenience_test.tmp"
        safe_file.write_text("Temporary content")

        # Mock human confirmation
        with patch("builtins.input", return_value="CONFIRM"):
            success, message = safe_cleanup_operation(
                root=self.test_dir,
                operation_type="delete",
                targets=[safe_file],
                description="Convenience function test",
            )

        self.assertTrue(success, f"Convenience function should work: {message}")
        self.assertFalse(
            safe_file.exists(), "File should be deleted via convenience function"
        )

    def test_backup_retention_and_cleanup(self):
        """Test backup creation and old backup cleanup."""
        # Create multiple backups
        backup_ids = []
        for i in range(3):
            test_file = self.test_dir / f"backup_test_{i}.txt"
            test_file.write_text(f"Content {i}")

            operation = CleanupOperation(
                operation_type="delete",
                targets=[test_file],
                description=f"Test backup {i}",
            )

            backup_gate = BackupExecuteGate(self.test_dir)
            backup_id = backup_gate._create_backup(operation)
            backup_ids.append(backup_id)

        # Verify all backups exist
        backups = self.framework.get_available_backups()
        self.assertEqual(len(backups), 3, "Should have 3 backups")

        # Test backup listing
        for backup_id in backup_ids:
            self.assertTrue(any(b["backup_id"] == backup_id for b in backups))


class TestIndividualSafetyGates(unittest.TestCase):
    """Unit tests for individual safety gates."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_preflight_gate_protected_paths(self):
        """Test that pre - flight gate correctly identifies protected paths."""
        gate = PreFlightGate()

        # Test protected file
        protected_file = self.test_dir / "pyproject.toml"
        protected_file.write_text("test")

        context = Mock()
        context.operation = CleanupOperation("delete", [protected_file], "Test")
        context.execution_log = []

        result, message = gate.validate(context)

        self.assertEqual(result.name, "FAIL")
        self.assertIn("Protected file", message)

    def test_dependency_analysis_gate_detection(self):
        """Test dependency analysis gate correctly detects dependencies."""
        gate = DependencyAnalysisGate(self.test_dir)

        # Create files with dependencies
        target_file = self.test_dir / "target.py"
        target_file.write_text("def target_function(): pass")

        dependent_file = self.test_dir / "dependent.py"
        dependent_file.write_text("from target import target_function")

        context = Mock()
        context.operation = CleanupOperation("delete", [target_file], "Test")
        context.execution_log = []

        result, message = gate.validate(context)

        # Should require confirmation due to dependencies
        self.assertEqual(result.name, "REQUIRE_CONFIRMATION")
        self.assertIsNotNone(context.dependency_report)

    def test_risk_assessment_scoring(self):
        """Test risk assessment scoring algorithm."""
        gate = RiskAssessmentGate()

        # Test low - risk operation
        low_risk_file = self.test_dir / "temp.log"
        low_risk_file.write_text("log")

        context = Mock()
        context.operation = CleanupOperation("delete", [low_risk_file], "Test")
        context.dependency_report = []  # No dependencies
        context.execution_log = []

        result, message = gate.validate(context)

        self.assertIsNotNone(context.risk_assessment)
        self.assertEqual(context.risk_assessment.level, RiskLevel.LOW)

    def test_human_confirmation_code_generation(self):
        """Test human confirmation code generation."""
        gate = HumanConfirmationGate()

        # Test simple confirmation code
        simple_code = gate._generate_confirmation_code()
        self.assertIsInstance(simple_code, str)
        self.assertTrue(len(simple_code) > 0)

        # Test complex confirmation code
        complex_code = gate._generate_complex_confirmation_code()
        self.assertIsInstance(complex_code, str)
        self.assertIn("-", complex_code)  # Should have format like "ABC123 - 4567"

    def test_backup_manifest_creation(self):
        """Test backup manifest creation and structure."""
        gate = BackupExecuteGate(self.test_dir)

        # Create test file
        test_file = self.test_dir / "manifest_test.txt"
        test_file.write_text("Test content")

        operation = CleanupOperation(
            operation_type="delete", targets=[test_file], description="Manifest test"
        )

        backup_id = gate._create_backup(operation)

        # Check manifest structure
        backup_dir = self.test_dir / ".ai_onboard" / "backups" / backup_id
        manifest_path = backup_dir / "manifest.json"

        self.assertTrue(manifest_path.exists(), "Manifest should be created")

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        self.assertEqual(manifest["backup_id"], backup_id)
        self.assertIn("timestamp", manifest)
        self.assertIn("operation", manifest)
        self.assertIn("files", manifest)


if __name__ == "__main__":
    # Set test mode to ensure consistent behavior
    import os

    os.environ["AI_ONBOARD_TEST_MODE"] = "1"

    unittest.main()
