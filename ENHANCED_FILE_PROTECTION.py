#!/usr/bin/env python3
"""
ENHANCED FILE PROTECTION SYSTEM - VectorFlow

This system prevents AI models from deleting critical onboarding files
during cleanup operations. It provides multiple layers of protection.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime

class EnhancedFileProtection:
    """Enhanced file protection system for VectorFlow onboarding"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.onboarding_dir = self.project_root / "onboarding"
        self.protection_file = self.onboarding_dir / "PROTECTED_FILES.md"
        self.backup_dir = self.onboarding_dir / "backups"
        self.log_file = self.onboarding_dir / "protection_log.json"
        
        # Critical files that must never be deleted
        self.critical_files = {
            # Core onboarding files
            "onboarding/README.md",
            "onboarding/AI_HANDOVER_PROTOCOL.md", 
            "onboarding/PROJECT_STATUS_TRACKER.md",
            "onboarding/PRIORITY_IMPLEMENTATION_ORDER.md",
            
            # Essential documentation
            "onboarding/PROJECT_ONBOARDING_PACKAGE.md",
            "onboarding/HANDOVER_SUMMARY.md",
            "onboarding/PROJECT_VISION_SUMMARY.md",
            "onboarding/SYSTEM_ARCHITECTURE_OVERVIEW.md",
            "onboarding/TECHNICAL_METHODOLOGIES.md",
            "onboarding/DEVELOPMENT_CONTEXT.md",
            "onboarding/API_INTEGRATION_GUIDE.md",
            
            # Automation systems
            "onboarding/PROGRESS_AUTOMATION.py",
            "onboarding/SCOPE_CHANGE_DETECTOR.py",
            "onboarding/INTELLIGENT_ERROR_RESOLVER.py",
            "onboarding/ENHANCED_FILE_PROTECTION.py",
            
            # Data files
            "onboarding/progress_database.json",
            "onboarding/scope_history.json",
            "onboarding/PROTECTED_FILES.md",
            
            # Root level critical files
            "goals.txt",
            "README.md",
            "update_progress.py"
        }
        
        # File patterns that should never be deleted
        self.protected_patterns = [
            "onboarding/",
            "*progress*",
            "*status*", 
            "*onboarding*",
            "*handover*",
            "*protection*"
        ]
        
        self.setup_logging()
        self.ensure_backup_dir()
        self.create_backup()
    
    def setup_logging(self):
        """Setup logging for protection system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def ensure_backup_dir(self):
        """Ensure backup directory exists"""
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self):
        """Create backup of all critical files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        for file_path in self.critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                backup_file = backup_path / Path(file_path).name
                shutil.copy2(full_path, backup_file)
                self.logger.info(f"Backed up: {file_path}")
    
    def is_protected_file(self, file_path: str) -> bool:
        """Check if a file is protected from deletion"""
        # Check exact matches
        if file_path in self.critical_files:
            return True
        
        # Check pattern matches
        for pattern in self.protected_patterns:
            if self._matches_pattern(file_path, pattern):
                return True
        
        # Check if file is in onboarding directory
        if file_path.startswith("onboarding/"):
            return True
        
        return False
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches protection pattern"""
        if pattern.endswith("/"):
            return file_path.startswith(pattern)
        elif "*" in pattern:
            # Simple wildcard matching
            pattern_parts = pattern.split("*")
            file_lower = file_path.lower()
            for part in pattern_parts:
                if part and part.lower() not in file_lower:
                    return False
            return True
        else:
            return pattern.lower() in file_path.lower()
    
    def validate_deletion_list(self, files_to_delete: List[str]) -> Dict:
        """Validate list of files to be deleted"""
        protected_files = []
        safe_files = []
        
        for file_path in files_to_delete:
            if self.is_protected_file(file_path):
                protected_files.append(file_path)
                self.logger.warning(f"PROTECTED FILE DETECTED: {file_path}")
            else:
                safe_files.append(file_path)
        
        return {
            "protected_files": protected_files,
            "safe_files": safe_files,
            "has_protected_files": len(protected_files) > 0
        }
    
    def enforce_protection(self, files_to_delete: List[str]) -> Dict:
        """Enforce file protection and return safe deletion list"""
        validation = self.validate_deletion_list(files_to_delete)
        
        if validation["has_protected_files"]:
            self.logger.error("CRITICAL: Attempted to delete protected files!")
            self.log_protection_violation(validation["protected_files"])
            
            # Return only safe files
            return {
                "safe_to_delete": validation["safe_files"],
                "blocked_files": validation["protected_files"],
                "protection_violation": True
            }
        
        return {
            "safe_to_delete": validation["safe_files"],
            "blocked_files": [],
            "protection_violation": False
        }
    
    def log_protection_violation(self, protected_files: List[str]):
        """Log protection violation"""
        violation = {
            "timestamp": datetime.now().isoformat(),
            "type": "protection_violation",
            "protected_files": protected_files,
            "message": "AI model attempted to delete protected files"
        }
        
        # Load existing log
        log_data = []
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    log_data = json.load(f)
            except:
                log_data = []
        
        # Add new violation
        log_data.append(violation)
        
        # Save updated log
        with open(self.log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def get_protection_status(self) -> Dict:
        """Get current protection status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "critical_files_count": len(self.critical_files),
            "protected_patterns_count": len(self.protected_patterns),
            "backup_dir_exists": self.backup_dir.exists(),
            "protection_file_exists": self.protection_file.exists(),
            "critical_files": list(self.critical_files)
        }
        
        # Check if all critical files exist
        missing_files = []
        for file_path in self.critical_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        status["missing_critical_files"] = missing_files
        status["all_critical_files_present"] = len(missing_files) == 0
        
        return status
    
    def restore_from_backup(self, file_path: str) -> bool:
        """Restore a file from backup"""
        try:
            # Find most recent backup
            backups = sorted(self.backup_dir.glob("backup_*"), reverse=True)
            if not backups:
                self.logger.error("No backups found")
                return False
            
            latest_backup = backups[0]
            backup_file = latest_backup / Path(file_path).name
            
            if backup_file.exists():
                target_file = self.project_root / file_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_file, target_file)
                self.logger.info(f"Restored: {file_path}")
                return True
            else:
                self.logger.error(f"Backup not found for: {file_path}")
                return False
        except Exception as e:
            self.logger.error(f"Restore failed for {file_path}: {e}")
            return False
    
    def create_emergency_restore_script(self):
        """Create emergency restore script"""
        script_content = f"""#!/usr/bin/env python3
# EMERGENCY RESTORE SCRIPT - VectorFlow
# Run this if critical files are accidentally deleted

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from onboarding.ENHANCED_FILE_PROTECTION import EnhancedFileProtection

def main():
    print("🚨 EMERGENCY RESTORE - VectorFlow")
    print("=" * 50)
    
    protection = EnhancedFileProtection()
    status = protection.get_protection_status()
    
    if status["all_critical_files_present"]:
        print("✅ All critical files are present")
        return 0
    
    print("❌ Missing critical files detected:")
    for file_path in status["missing_critical_files"]:
        print(f"   - {file_path}")
    
    print("\\n🔄 Attempting to restore missing files...")
    
    restored_count = 0
    for file_path in status["missing_critical_files"]:
        if protection.restore_from_backup(file_path):
            restored_count += 1
    
    print(f"\\n✅ Restored {restored_count}/{len(status['missing_critical_files'])} files")
    
    # Verify restoration
    final_status = protection.get_protection_status()
    if final_status["all_critical_files_present"]:
        print("🎉 All critical files restored successfully!")
        return 0
    else:
        print("⚠️  Some files could not be restored")
        return 1

if __name__ == "__main__":
    exit(main())
"""
        
        script_path = self.project_root / "emergency_restore.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        script_path.chmod(0o755)
        self.logger.info(f"Created emergency restore script: {script_path}")

def main():
    """Main function for testing protection system"""
    protection = EnhancedFileProtection()
    
    print("🛡️ Enhanced File Protection System - VectorFlow")
    print("=" * 60)
    
    # Show protection status
    status = protection.get_protection_status()
    print(f"Critical files protected: {status['critical_files_count']}")
    print(f"Protected patterns: {status['protected_patterns_count']}")
    print(f"All critical files present: {status['all_critical_files_present']}")
    
    if not status["all_critical_files_present"]:
        print("❌ Missing critical files:")
        for file_path in status["missing_critical_files"]:
            print(f"   - {file_path}")
    
    # Create emergency restore script
    protection.create_emergency_restore_script()
    
    print("\n✅ Protection system initialized")
    print("🛡️ Critical files are now protected from deletion")

if __name__ == "__main__":
    main()
