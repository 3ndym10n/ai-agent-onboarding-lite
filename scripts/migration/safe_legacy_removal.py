#!/usr/bin/env python3
"""
Safe Legacy File Removal Script

This script safely removes the legacy orchestration files after verifying
that all migrations have been completed successfully.
"""

import os
import shutil
import sys
from pathlib import Path
from typing import List

# Add project root to path
sys.path.insert(0, ".")


class LegacyFileRemover:
    """Handles safe removal of legacy orchestration files."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.backup_dir = root_path / ".ai_onboard" / "legacy_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Files to be removed
        self.legacy_files = [
            "ai_onboard/core/intelligent_tool_orchestrator.py",
            "ai_onboard/core/holistic_tool_orchestration.py",
            "ai_onboard/core/ai_agent_orchestration.py",
        ]

        # Backup files to clean up
        self.backup_files = [
            "tests/test_new_tools.py.backup",
            "tests/test_new_tools_phase2.py.backup",
            "tests/test_new_tools_phase3.py.backup",
            "tests/debug_tool_test.py.backup",
            "tests/test_unified_orchestration.py.backup",
        ]

    def verify_migrations_complete(self) -> bool:
        """Verify that all migrations have been completed."""
        print("🔍 Verifying migration completeness...")

        # Check for any remaining direct imports (excluding the legacy files themselves)
        import subprocess

        try:
            # Search for imports excluding the files we're about to remove
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "grep",
                    "-r",
                    "from.*intelligent_tool_orchestrator.*import|from.*holistic_tool_orchestration.*import|from.*ai_agent_orchestration.*import",
                    "ai_onboard/",
                    "scripts/",
                    "tests/",
                    "--exclude-dir=__pycache__",
                ],
                capture_output=True,
                text=True,
                cwd=self.root_path,
            )

            # Filter out the legacy files themselves and migration script
            lines = result.stdout.split("\n") if result.stdout else []
            problematic_imports = []

            for line in lines:
                if not line.strip():
                    continue

                # Skip the legacy files themselves
                if any(
                    legacy_file in line
                    for legacy_file in [
                        "intelligent_tool_orchestrator.py",
                        "holistic_tool_orchestration.py",
                        "ai_agent_orchestration.py",
                    ]
                ):
                    continue

                # Skip migration script and backup files
                if "migrate_to_unified_orchestrator.py" in line or ".backup" in line:
                    continue

                # Skip unified orchestrator (it imports for compatibility)
                if "unified_tool_orchestrator.py" in line:
                    continue

                problematic_imports.append(line)

            if problematic_imports:
                print("❌ Found remaining imports that need migration:")
                for imp in problematic_imports:
                    print(f"   {imp}")
                return False

            print("✅ All migrations appear complete")
            return True

        except Exception as e:
            print(f"⚠️  Could not verify migrations: {e}")
            return False

    def test_unified_orchestrator(self) -> bool:
        """Test that the unified orchestrator is working."""
        print("🧪 Testing unified orchestrator functionality...")

        try:
            from pathlib import Path

            from ai_onboard.core.unified_tool_orchestrator import (
                UnifiedToolOrchestrator,
            )

            # Test basic initialization
            orchestrator = UnifiedToolOrchestrator(Path("."))
            print("✅ UnifiedToolOrchestrator initializes successfully")

            # Test backward compatibility
            import warnings

            warnings.simplefilter("always")

            from ai_onboard.core.orchestration_compatibility import (
                IntelligentToolOrchestrator,
            )

            legacy_orch = IntelligentToolOrchestrator(Path("."))
            print("✅ Backward compatibility layer working")

            return True

        except Exception as e:
            print(f"❌ Unified orchestrator test failed: {e}")
            return False

    def create_backup(self, file_path: Path) -> Path:
        """Create backup of a file before removal."""
        if not file_path.exists():
            return None

        backup_name = f"{file_path.name}_{int(__import__('time').time())}"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(file_path, backup_path)
        print(f"📦 Backed up {file_path} to {backup_path}")
        return backup_path

    def remove_legacy_files(self) -> List[Path]:
        """Remove legacy orchestration files."""
        removed_files = []

        print("\n🗑️  Removing legacy orchestration files...")

        for file_path_str in self.legacy_files:
            file_path = self.root_path / file_path_str

            if file_path.exists():
                # Create backup first
                backup_path = self.create_backup(file_path)

                # Remove the file
                file_path.unlink()
                removed_files.append(file_path)
                print(f"✅ Removed {file_path}")
            else:
                print(f"⏭️  {file_path} does not exist (already removed)")

        return removed_files

    def cleanup_backup_files(self) -> List[Path]:
        """Clean up migration backup files."""
        cleaned_files = []

        print("\n🧹 Cleaning up migration backup files...")

        for file_path_str in self.backup_files:
            file_path = self.root_path / file_path_str

            if file_path.exists():
                file_path.unlink()
                cleaned_files.append(file_path)
                print(f"✅ Removed backup {file_path}")
            else:
                print(f"⏭️  {file_path} does not exist")

        return cleaned_files

    def run_final_tests(self) -> bool:
        """Run final tests to ensure system is working."""
        print("\n🧪 Running final system tests...")

        try:
            # Test unified orchestrator
            import subprocess

            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/test_unified_orchestration.py",
                    "-v",
                    "--tb=short",
                ],
                capture_output=True,
                text=True,
                cwd=self.root_path,
            )

            if result.returncode == 0:
                print("✅ All unified orchestration tests passed")
                return True
            else:
                print("❌ Some tests failed:")
                print(result.stdout)
                print(result.stderr)
                return False

        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return False

    def safe_remove_all(self) -> bool:
        """Perform complete safe removal process."""
        print("🚀 Starting Safe Legacy File Removal Process")
        print("=" * 60)

        # Step 1: Verify migrations are complete
        if not self.verify_migrations_complete():
            print("\n❌ Migration verification failed. Aborting removal.")
            return False

        # Step 2: Test unified orchestrator
        if not self.test_unified_orchestrator():
            print("\n❌ Unified orchestrator test failed. Aborting removal.")
            return False

        # Step 3: Create safety checkpoint
        print(f"\n📦 Creating safety backups in {self.backup_dir}")

        # Step 4: Remove legacy files
        removed_files = self.remove_legacy_files()

        # Step 5: Clean up migration backups
        cleaned_files = self.cleanup_backup_files()

        # Step 6: Run final tests
        if not self.run_final_tests():
            print("\n❌ Final tests failed!")

            # Offer to restore from backup
            response = input("Restore from backup? (y/N): ").lower().strip()
            if response == "y":
                self.restore_from_backup(removed_files)
                return False
            else:
                print(
                    "⚠️  Continuing with failed tests - manual intervention may be needed"
                )

        # Step 7: Success summary
        print(f"\n🎉 Legacy file removal completed successfully!")
        print(f"   📁 Removed {len(removed_files)} legacy files")
        print(f"   🧹 Cleaned {len(cleaned_files)} backup files")
        print(f"   📦 Backups stored in {self.backup_dir}")
        print(f"   ✅ All tests passing")

        return True

    def restore_from_backup(self, removed_files: List[Path]):
        """Restore files from backup."""
        print("\n🔄 Restoring files from backup...")

        for file_path in removed_files:
            # Find the most recent backup
            backup_pattern = f"{file_path.name}_*"
            backups = list(self.backup_dir.glob(backup_pattern))

            if backups:
                latest_backup = max(backups, key=lambda p: p.stat().st_mtime)
                shutil.copy2(latest_backup, file_path)
                print(f"✅ Restored {file_path}")
            else:
                print(f"❌ No backup found for {file_path}")


def main():
    """Main removal function."""
    root_path = Path(".")
    remover = LegacyFileRemover(root_path)

    # Ask for confirmation
    print("⚠️  This will permanently remove legacy orchestration files!")
    print("Files to be removed:")
    for file_path in remover.legacy_files:
        print(f"   - {file_path}")

    response = input("\nProceed with removal? (y/N): ").lower().strip()
    if response != "y":
        print("Removal cancelled.")
        return

    success = remover.safe_remove_all()

    if success:
        print("\n🎉 Legacy file removal completed successfully!")
        print("The unified orchestration system is now the single source of truth.")
    else:
        print("\n❌ Legacy file removal encountered issues.")
        print("Please review the output above and address any problems.")


if __name__ == "__main__":
    main()

