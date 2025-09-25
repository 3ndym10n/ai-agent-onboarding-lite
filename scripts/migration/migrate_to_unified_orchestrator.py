#!/usr/bin/env python3
"""
Automated Migration Script for Unified Tool Orchestrator

This script automatically migrates files from legacy orchestrators to the unified system.
It handles import statements, class instantiations, and method calls.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
sys.path.insert(0, ".")


class OrchestrationMigrator:
    """Handles migration from legacy orchestrators to unified system."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.migration_patterns = self._setup_migration_patterns()
        self.migrated_files = []
        self.backup_files = []

    def _setup_migration_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """Setup regex patterns for migration."""
        return {
            # Import statement migrations
            "imports": [
                (
                    r"from\s+\.\.?core\.intelligent_tool_orchestrator\s+import\s+IntelligentToolOrchestrator",
                    "from ..core.unified_tool_orchestrator import UnifiedToolOrchestrator",
                ),
                (
                    r"from\s+\.core\.intelligent_tool_orchestrator\s+import\s+IntelligentToolOrchestrator",
                    "from .unified_tool_orchestrator import UnifiedToolOrchestrator",
                ),
                (
                    r"from\s+ai_onboard\.core\.intelligent_tool_orchestrator\s+import\s+IntelligentToolOrchestrator",
                    "from ai_onboard.core.unified_tool_orchestrator import UnifiedToolOrchestrator",
                ),
                (
                    r"from\s+\.\.?core\.holistic_tool_orchestration\s+import\s+.*HolisticToolOrchestrator",
                    "from ..core.unified_tool_orchestrator import UnifiedToolOrchestrator",
                ),
                (
                    r"from\s+\.core\.holistic_tool_orchestration\s+import\s+.*HolisticToolOrchestrator",
                    "from .unified_tool_orchestrator import UnifiedToolOrchestrator",
                ),
                (
                    r"from\s+ai_onboard\.core\.holistic_tool_orchestration\s+import\s+.*HolisticToolOrchestrator",
                    "from ai_onboard.core.unified_tool_orchestrator import UnifiedToolOrchestrator",
                ),
                (
                    r"from\s+\.\.?core\.ai_agent_orchestration\s+import\s+AIAgentOrchestrationLayer",
                    "from ..core.unified_tool_orchestrator import UnifiedToolOrchestrator",
                ),
                (
                    r"from\s+\.core\.ai_agent_orchestration\s+import\s+AIAgentOrchestrationLayer",
                    "from .unified_tool_orchestrator import UnifiedToolOrchestrator",
                ),
                (
                    r"from\s+ai_onboard\.core\.ai_agent_orchestration\s+import\s+AIAgentOrchestrationLayer",
                    "from ai_onboard.core.unified_tool_orchestrator import UnifiedToolOrchestrator",
                ),
            ],
            # Class instantiation migrations
            "instantiations": [
                (r"IntelligentToolOrchestrator\(", "UnifiedToolOrchestrator("),
                (r"HolisticToolOrchestrator\(", "UnifiedToolOrchestrator("),
                (r"AIAgentOrchestrationLayer\(", "UnifiedToolOrchestrator("),
            ],
            # Method call migrations (some methods have different signatures)
            "method_calls": [
                (
                    r"\.analyze_conversation_for_tool_application\(",
                    ".orchestrate_tools(",
                ),
                (r"\.execute_automatic_tool_application\(", "._execute_tool_safely("),
                (r"\.orchestrate_tools_for_request\(", ".orchestrate_tools("),
                (r"\.process_conversation\(", ".orchestrate_tools("),
            ],
        }

    def create_backup(self, file_path: Path) -> Path:
        """Create backup of file before migration."""
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        backup_path.write_text(file_path.read_text(), encoding="utf-8")
        self.backup_files.append(backup_path)
        return backup_path

    def migrate_file(self, file_path: Path) -> bool:
        """Migrate a single file to use unified orchestrator."""
        try:
            # Try different encodings
            for encoding in ["utf-8", "latin1", "cp1252"]:
                try:
                    content = file_path.read_text(encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print(f"❌ Could not decode {file_path} with any encoding")
                return False

            original_content = content

            # Apply migration patterns
            for pattern_type, patterns in self.migration_patterns.items():
                for old_pattern, new_pattern in patterns:
                    content = re.sub(old_pattern, new_pattern, content)

            # Only write if changes were made
            if content != original_content:
                self.create_backup(file_path)
                file_path.write_text(content, encoding="utf-8")
                self.migrated_files.append(file_path)
                print(f"✅ Migrated: {file_path}")
                return True
            else:
                print(f"⏭️  No changes needed: {file_path}")
                return False

        except Exception as e:
            print(f"❌ Failed to migrate {file_path}: {e}")
            return False

    def find_files_to_migrate(self) -> List[Path]:
        """Find all files that need migration."""
        files_to_migrate = []

        # Search patterns for files that likely use legacy orchestrators
        search_patterns = [
            "IntelligentToolOrchestrator",
            "HolisticToolOrchestrator",
            "AIAgentOrchestrationLayer",
        ]

        # Search in key directories
        search_dirs = [
            self.root_path / "ai_onboard" / "core",
            self.root_path / "ai_onboard" / "cli",
            self.root_path / "scripts",
            self.root_path / "tests",
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for py_file in search_dir.rglob("*.py"):
                # Skip the legacy files themselves and unified orchestrator
                if py_file.name in [
                    "intelligent_tool_orchestrator.py",
                    "holistic_tool_orchestration.py",
                    "ai_agent_orchestration.py",
                    "unified_tool_orchestrator.py",
                    "orchestration_compatibility.py",
                ]:
                    continue

                try:
                    content = py_file.read_text(encoding="utf-8")
                    if any(pattern in content for pattern in search_patterns):
                        files_to_migrate.append(py_file)
                except Exception:
                    continue

        return files_to_migrate

    def migrate_all(self) -> Dict[str, int]:
        """Migrate all files that need updating."""
        files_to_migrate = self.find_files_to_migrate()

        print(f"🔍 Found {len(files_to_migrate)} files to migrate:")
        for file_path in files_to_migrate:
            print(f"   - {file_path}")
        print()

        results = {
            "total": len(files_to_migrate),
            "migrated": 0,
            "skipped": 0,
            "failed": 0,
        }

        for file_path in files_to_migrate:
            try:
                if self.migrate_file(file_path):
                    results["migrated"] += 1
                else:
                    results["skipped"] += 1
            except Exception as e:
                print(f"❌ Error migrating {file_path}: {e}")
                results["failed"] += 1

        return results

    def rollback_migration(self):
        """Rollback all migrations using backup files."""
        print("🔄 Rolling back migration...")

        for backup_path in self.backup_files:
            try:
                original_path = backup_path.with_suffix("")
                original_path.write_text(backup_path.read_text(), encoding="utf-8")
                backup_path.unlink()  # Remove backup
                print(f"✅ Rolled back: {original_path}")
            except Exception as e:
                print(f"❌ Failed to rollback {backup_path}: {e}")

    def cleanup_backups(self):
        """Remove backup files after successful migration."""
        print("🧹 Cleaning up backup files...")

        for backup_path in self.backup_files:
            try:
                backup_path.unlink()
                print(f"✅ Removed backup: {backup_path}")
            except Exception as e:
                print(f"❌ Failed to remove backup {backup_path}: {e}")


def main():
    """Main migration function."""
    root_path = Path(".")
    migrator = OrchestrationMigrator(root_path)

    print("🚀 Starting Orchestration Migration to Unified System")
    print("=" * 60)

    try:
        # Perform migration
        results = migrator.migrate_all()

        print("\n📊 Migration Results:")
        print(f"   Total files processed: {results['total']}")
        print(f"   ✅ Successfully migrated: {results['migrated']}")
        print(f"   ⏭️  Skipped (no changes): {results['skipped']}")
        print(f"   ❌ Failed: {results['failed']}")

        if results["migrated"] > 0:
            print(f"\n🎉 Migration completed successfully!")
            print(
                f"   {results['migrated']} files have been updated to use UnifiedToolOrchestrator"
            )
            print(f"   Backup files created for safety (use --cleanup to remove)")

            # Ask user if they want to cleanup backups
            response = input("\nCleanup backup files? (y/N): ").lower().strip()
            if response == "y":
                migrator.cleanup_backups()
        else:
            print("\n✅ No migration needed - all files are up to date!")

    except KeyboardInterrupt:
        print("\n⚠️  Migration interrupted by user")
        response = input("Rollback changes? (y/N): ").lower().strip()
        if response == "y":
            migrator.rollback_migration()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Rolling back changes...")
        migrator.rollback_migration()


if __name__ == "__main__":
    main()
