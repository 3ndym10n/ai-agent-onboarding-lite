#!/usr/bin/env python3
"""
Simple VectorFlow Cleanup System

Replaces complex 358-line cleanup system with simple, safe cleanup.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from protect import SimpleProtection

class SimpleCleanup:
    """Simple and safe repository cleanup system"""

    def __init__(self, project_root: str = ".."):
        self.project_root = Path(project_root).resolve()
        self.protection = SimpleProtection(project_root)
        self.log_file = self.project_root / "onboarding" / "cleanup_log.txt"

        # Cleanup targets
        self.cleanup_patterns = [
            "*.log",
            "*.tmp",
            "*.cache",
            "*.pyc",
            "__pycache__",
            ".pytest_cache",
            ".coverage",
            "htmlcov",
            "*.db",
            "*.sqlite*",
            "test.db",
            "temp",
            "tmp",
            "temp_tests",
            "sandbox",
            "test_output",
            "integration_dissection_*.md",
            "test_*.py",
            "debug_*.py",
            "old_*",
            "backup_*",
            "archive_*"
        ]

    def scan_for_cleanup(self, dry_run: bool = True) -> Dict:
        """Scan repository for files that can be cleaned up"""
        cleanup_items = {
            "files": [],
            "directories": [],
            "total_size": 0
        }

        # Scan files
        for pattern in self.cleanup_patterns:
            for item in self.project_root.rglob(pattern):
                if item.exists():
                    # Check protection
                    if self.protection.is_protected(str(item.relative_to(self.project_root))):
                        continue

                    item_info = {
                        "path": str(item.relative_to(self.project_root)),
                        "size": self._get_size(item),
                        "type": "directory" if item.is_dir() else "file"
                    }

                    if item.is_dir():
                        cleanup_items["directories"].append(item_info)
                    else:
                        cleanup_items["files"].append(item_info)

                    cleanup_items["total_size"] += item_info["size"]

        if dry_run:
            self._print_scan_results(cleanup_items)
        else:
            self._perform_cleanup(cleanup_items)

        return cleanup_items

    def _get_size(self, path: Path) -> int:
        """Get size of file or directory"""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        return 0

    def _print_scan_results(self, items: Dict):
        """Print cleanup scan results"""
        print(f"\n🧹 Cleanup Scan Results ({self.project_root})")
        print("=" * 50)

        if not items["files"] and not items["directories"]:
            print("✅ No files found for cleanup")
            return

        if items["files"]:
            print(f"\n📄 Files ({len(items['files'])}):")
            for item in items["files"][:10]:  # Show first 10
                size_mb = item["size"] / (1024 * 1024)
                print(".1f"            if len(items["files"]) > 10:
                print(f"   ... and {len(items['files']) - 10} more files")

        if items["directories"]:
            print(f"\n📁 Directories ({len(items['directories'])}):")
            for item in items["directories"][:5]:  # Show first 5
                size_mb = item["size"] / (1024 * 1024)
                print(".1f"            if len(items["directories"]) > 5:
                print(f"   ... and {len(items['directories']) - 5} more directories")

        total_mb = items["total_size"] / (1024 * 1024)
        print(".1f"        print("\n💡 Run with --clean to perform cleanup")

    def _perform_cleanup(self, items: Dict):
        """Perform the actual cleanup"""
        print(f"\n🧹 Performing cleanup in {self.project_root}")
        print("=" * 50)

        cleaned_files = 0
        cleaned_dirs = 0
        total_size = 0

        # Clean files
        for item in items["files"]:
            file_path = self.project_root / item["path"]
            try:
                file_path.unlink()
                cleaned_files += 1
                total_size += item["size"]
                print(f"🗑️  Deleted: {item['path']}")
            except Exception as e:
                print(f"❌ Failed to delete {item['path']}: {e}")

        # Clean directories
        for item in items["directories"]:
            dir_path = self.project_root / item["path"]
            try:
                shutil.rmtree(dir_path)
                cleaned_dirs += 1
                total_size += item["size"]
                print(f"🗑️  Removed: {item['path']}/")
            except Exception as e:
                print(f"❌ Failed to remove {item['path']}: {e}")

        # Log cleanup
        self._log_cleanup(cleaned_files, cleaned_dirs, total_size)

        total_mb = total_size / (1024 * 1024)
        print("
✅ Cleanup complete!"        print(f"📄 Files deleted: {cleaned_files}")
        print(f"📁 Directories removed: {cleaned_dirs}")
        print(".1f"
    def _log_cleanup(self, files: int, dirs: int, size: int):
        """Log cleanup operation"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Cleanup: {files} files, {dirs} dirs, {size} bytes\n"

        with open(self.log_file, 'a') as f:
            f.write(log_entry)


def main():
    """Command line interface for cleanup system"""
    import sys

    dry_run = "--clean" not in sys.argv
    cleanup = SimpleCleanup()

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be deleted")
        print("💡 Add --clean flag to perform actual cleanup\n")
    else:
        print("🧹 CLEANUP MODE - Files will be permanently deleted!")
        confirm = input("Are you sure? (type 'yes' to continue): ")
        if confirm != 'yes':
            print("❌ Cleanup cancelled")
            return

    cleanup.scan_for_cleanup(dry_run=dry_run)


if __name__ == "__main__":
    main()