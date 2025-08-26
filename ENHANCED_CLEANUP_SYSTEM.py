#!/usr/bin/env python3
"""
ENHANCED CLEANUP SYSTEM - VectorFlow

This system cleans up the repository while ensuring critical onboarding files
are never deleted. It integrates with the Enhanced File Protection system.
"""

import os
import shutil
import time
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

# Import enhanced file protection
try:
    from onboarding.ENHANCED_FILE_PROTECTION import EnhancedFileProtection
    PROTECTION_AVAILABLE = True
except ImportError:
    PROTECTION_AVAILABLE = False
    print("⚠️  Enhanced file protection not available")

class EnhancedCleanupSystem:
    """Enhanced repository cleanup system with file protection"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.cleanup_report_file = self.project_root / "onboarding" / "CLEANUP_REPORT.md"
        
        # Initialize file protection if available
        if PROTECTION_AVAILABLE:
            self.protection = EnhancedFileProtection(project_root)
            print("🛡️  File protection system active")
        else:
            self.protection = None
            print("⚠️  File protection system not available")
        
        # Files and directories to clean up
        self.cleanup_targets = {
            "debug_files": [
                "*.log",
                "*.tmp",
                "*.cache",
                "*.pyc",
                "__pycache__",
                ".pytest_cache",
                ".coverage",
                "htmlcov"
            ],
            "local_database_files": [
                "*.db",
                "*.sqlite",
                "*.sqlite3",
                "vectorflow.db",
                "test.db"
            ],
            "temporary_directories": [
                "temp",
                "tmp",
                "temp_tests",
                "sandbox",
                "test_output"
            ],
            "integration_files": [
                "integration_dissection_*.md",
                "test_*.py",
                "debug_*.py"
            ],
            "duplicate_directories": [
                "old_*",
                "backup_*",
                "archive_*"
            ]
        }
    
    def scan_for_cleanup(self) -> Dict:
        """Scan repository for files that can be cleaned up"""
        cleanup_items = {
            "debug_files": [],
            "local_database_files": [],
            "temporary_directories": [],
            "integration_files": [],
            "duplicate_directories": [],
            "total_size": 0
        }
        
        for category, patterns in self.cleanup_targets.items():
            for pattern in patterns:
                items = self._find_matching_items(pattern)
                for item in items:
                    # Check if item is protected
                    if self._is_protected(item):
                        print(f"🛡️  PROTECTED: {item}")
                        continue
                    
                    cleanup_items[category].append({
                        "path": str(item),
                        "size": self._get_size(item),
                        "type": "file" if item.is_file() else "directory"
                    })
                    cleanup_items["total_size"] += self._get_size(item)
        
        return cleanup_items
    
    def _find_matching_items(self, pattern: str) -> List[Path]:
        """Find items matching the pattern"""
        items = []
        
        if "*" in pattern:
            # Handle wildcard patterns
            for item in self.project_root.rglob(pattern):
                if item.is_file() or item.is_dir():
                    items.append(item)
        else:
            # Handle exact matches
            item_path = self.project_root / pattern
            if item_path.exists():
                items.append(item_path)
        
        return items
    
    def _is_protected(self, item_path: Path) -> bool:
        """Check if item is protected from deletion"""
        if self.protection:
            return self.protection.is_protected_file(str(item_path.relative_to(self.project_root)))
        else:
            # Basic protection without enhanced system
            item_str = str(item_path.relative_to(self.project_root))
            return (
                item_str.startswith("onboarding/") or
                "progress" in item_str.lower() or
                "status" in item_str.lower() or
                "protection" in item_str.lower()
            )
    
    def _get_size(self, item_path: Path) -> int:
        """Get size of file or directory"""
        try:
            if item_path.is_file():
                return item_path.stat().st_size
            elif item_path.is_dir():
                total_size = 0
                for file_path in item_path.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                return total_size
            return 0
        except:
            return 0
    
    def execute_cleanup(self, dry_run: bool = True, max_retries: int = 3) -> Dict:
        """Execute cleanup with protection"""
        print(f"🧹 {'DRY RUN' if dry_run else 'EXECUTING'} CLEANUP - VectorFlow")
        print("=" * 60)
        
        # Scan for cleanup items
        cleanup_items = self.scan_for_cleanup()
        
        # Validate with protection system
        if self.protection:
            all_files = []
            for category in cleanup_items:
                if category != "total_size":
                    for item in cleanup_items[category]:
                        all_files.append(item["path"])
            
            protection_result = self.protection.enforce_protection(all_files)
            
            if protection_result["protection_violation"]:
                print("🚨 PROTECTION VIOLATION DETECTED!")
                print("Blocked files:")
                for file_path in protection_result["blocked_files"]:
                    print(f"   - {file_path}")
                
                # Only proceed with safe files
                safe_files = protection_result["safe_to_delete"]
                cleanup_items = self._filter_cleanup_items(cleanup_items, safe_files)
        
        # Execute cleanup
        results = {
            "successful": [],
            "failed": [],
            "skipped": [],
            "total_cleaned": 0,
            "total_size_freed": 0
        }
        
        for category in cleanup_items:
            if category == "total_size":
                continue
                
            print(f"\n📁 Processing {category}:")
            for item in cleanup_items[category]:
                item_path = Path(item["path"])
                
                if dry_run:
                    print(f"   📄 Would remove: {item_path} ({self._format_size(item['size'])})")
                    results["skipped"].append(str(item_path))
                else:
                    success = self._remove_item(item_path, max_retries)
                    if success:
                        print(f"   ✅ Removed: {item_path}")
                        results["successful"].append(str(item_path))
                        results["total_cleaned"] += 1
                        results["total_size_freed"] += item["size"]
                    else:
                        print(f"   ❌ Failed: {item_path}")
                        results["failed"].append(str(item_path))
        
        # Generate report
        self._generate_cleanup_report(cleanup_items, results, dry_run)
        
        return results
    
    def _filter_cleanup_items(self, cleanup_items: Dict, safe_files: List[str]) -> Dict:
        """Filter cleanup items to only include safe files"""
        filtered_items = {
            "debug_files": [],
            "local_database_files": [],
            "temporary_directories": [],
            "integration_files": [],
            "duplicate_directories": [],
            "total_size": 0
        }
        
        safe_files_set = set(safe_files)
        
        for category in cleanup_items:
            if category == "total_size":
                continue
                
            for item in cleanup_items[category]:
                if item["path"] in safe_files_set:
                    filtered_items[category].append(item)
                    filtered_items["total_size"] += item["size"]
        
        return filtered_items
    
    def _remove_item(self, item_path: Path, max_retries: int) -> bool:
        """Remove item with retry logic"""
        for attempt in range(max_retries):
            try:
                if item_path.is_file():
                    item_path.unlink()
                elif item_path.is_dir():
                    shutil.rmtree(item_path)
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.1)  # Brief delay before retry
                    continue
                else:
                    print(f"      Failed after {max_retries} attempts: {e}")
                    return False
        return False
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def _generate_cleanup_report(self, cleanup_items: Dict, results: Dict, dry_run: bool):
        """Generate cleanup report"""
        report_content = f"""# 🧹 VectorFlow Cleanup Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Mode:** {'DRY RUN' if dry_run else 'EXECUTED'}

## 📊 Summary

- **Total items found:** {sum(len(cleanup_items[cat]) for cat in cleanup_items if cat != 'total_size')}
- **Total size:** {self._format_size(cleanup_items['total_size'])}
- **Items processed:** {len(results['successful']) + len(results['failed']) + len(results['skipped'])}

## 📁 Cleanup Categories

"""
        
        for category, items in cleanup_items.items():
            if category == "total_size":
                continue
                
            category_size = sum(item["size"] for item in items)
            report_content += f"### {category.replace('_', ' ').title()}\n"
            report_content += f"- **Items:** {len(items)}\n"
            report_content += f"- **Size:** {self._format_size(category_size)}\n\n"
            
            for item in items:
                report_content += f"- `{item['path']}` ({self._format_size(item['size'])})\n"
            report_content += "\n"
        
        # Add protection status
        if self.protection:
            protection_status = self.protection.get_protection_status()
            report_content += f"""## 🛡️ Protection Status

- **Critical files protected:** {protection_status['critical_files_count']}
- **All critical files present:** {protection_status['all_critical_files_present']}
- **Backup directory exists:** {protection_status['backup_dir_exists']}

"""
        
        # Add results
        if not dry_run:
            report_content += f"""## ✅ Results

- **Successfully removed:** {len(results['successful'])}
- **Failed to remove:** {len(results['failed'])}
- **Total size freed:** {self._format_size(results['total_size_freed'])}

### Failed Items
"""
            for item in results['failed']:
                report_content += f"- `{item}`\n"
        
        # Write report
        with open(self.cleanup_report_file, 'w') as f:
            f.write(report_content)
        
        print(f"\n📋 Cleanup report generated: {self.cleanup_report_file}")

def main():
    """Main function for testing cleanup system"""
    cleanup = EnhancedCleanupSystem()
    
    print("🧹 Enhanced Cleanup System - VectorFlow")
    print("=" * 60)
    
    # Run dry run first
    print("\n🔍 Running dry run...")
    dry_run_results = cleanup.execute_cleanup(dry_run=True)
    
    # Ask for confirmation
    print(f"\n📊 Dry run found {sum(len(dry_run_results[cat]) for cat in dry_run_results if cat not in ['successful', 'failed', 'skipped', 'total_cleaned', 'total_size_freed'])} items to clean")
    print(f"📏 Total size: {cleanup._format_size(dry_run_results.get('total_size', 0))}")
    
    response = input("\n❓ Proceed with cleanup? (y/N): ").strip().lower()
    
    if response == 'y':
        print("\n🚀 Executing cleanup...")
        actual_results = cleanup.execute_cleanup(dry_run=False)
        print(f"\n✅ Cleanup completed!")
        print(f"📏 Freed: {cleanup._format_size(actual_results['total_size_freed'])}")
    else:
        print("\n❌ Cleanup cancelled")

if __name__ == "__main__":
    main()
