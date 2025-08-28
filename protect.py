#!/usr/bin/env python3
"""
Simple VectorFlow File Protection System

Replaces complex 328-line protection system with simple, reliable checks.
"""

import os
from pathlib import Path
from typing import List, Set

class SimpleProtection:
    """Simple file protection system for VectorFlow"""

    def __init__(self, project_root: str = ".."):
        self.project_root = Path(project_root).resolve()
        self.protect_file = self.project_root / "onboarding" / ".protect"
        self.protected_files: Set[str] = set()

        self._load_protection_rules()

    def _load_protection_rules(self):
        """Load protection rules from .protect file"""
        if not self.protect_file.exists():
            print("⚠️  Protection file not found")
            return

        with open(self.protect_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    self.protected_files.add(line)

    def is_protected(self, file_path: str) -> bool:
        """Check if file is protected from deletion"""
        file_path = str(file_path)

        # Direct file match
        if file_path in self.protected_files:
            return True

        # Pattern matching
        for pattern in self.protected_files:
            if '*' in pattern:
                # Simple wildcard matching
                if self._matches_pattern(file_path, pattern):
                    return True

        return False

    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Simple pattern matching for wildcards"""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)

    def get_protected_files(self) -> List[str]:
        """Get list of all protected files"""
        return sorted(list(self.protected_files))

    def validate_deletion(self, file_path: str) -> bool:
        """Validate if file can be safely deleted"""
        if self.is_protected(file_path):
            print(f"🛡️  PROTECTED: Cannot delete {file_path}")
            return False
        return True

    def backup_critical_files(self):
        """Create simple backup of critical files"""
        import shutil
        from datetime import datetime

        backup_dir = self.project_root / "onboarding" / "backups"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)

        backed_up = 0
        for file_path in self.protected_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                backup_file = backup_path / full_path.name
                shutil.copy2(full_path, backup_file)
                backed_up += 1

        print(f"✅ Backed up {backed_up} critical files")
        return backup_path


def main():
    """Command line interface for protection system"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python protect.py [command] [file]")
        print("Commands: check, backup, list")
        return

    command = sys.argv[1]
    protection = SimpleProtection()

    if command == "check" and len(sys.argv) > 2:
        file_path = sys.argv[2]
        if protection.is_protected(file_path):
            print(f"🛡️  {file_path} is PROTECTED")
        else:
            print(f"✅ {file_path} can be deleted")

    elif command == "backup":
        backup_path = protection.backup_critical_files()
        print(f"📁 Backup created at: {backup_path}")

    elif command == "list":
        print("🛡️  Protected files:")
        for file in protection.get_protected_files():
            print(f"  - {file}")

    else:
        print("Unknown command. Use: check, backup, or list")


if __name__ == "__main__":
    main()