#!/usr/bin/env python3
"""
VectorFlow Scope Change Detection System

Automatically detects scope changes in the project and alerts AI models
to prevent confusion and ensure continuity during project evolution.
"""

import os
import json
import yaml
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import subprocess
import re


class ScopeChangeDetector:
    """
    Automated scope change detection for VectorFlow project.
    Monitors project evolution and alerts AI models of significant changes.
    """
    
    def __init__(self, project_root: str = ".."):
        self.project_root = Path(project_root).resolve()
        self.scope_history_file = self.project_root / "onboarding" / "scope_history.json"
        self.scope_report_file = self.project_root / "onboarding" / "SCOPE_CHANGE_REPORT.md"
        self.change_threshold = 0.1  # 10% change triggers alert
        
        # Define scope change categories
        self.scope_categories = {
            "infrastructure": ["data_pipeline/", "utils/", "config/"],
            "analytics": ["analytics/"],
            "dashboard": ["dashboard/", "web_integration/"],
            "documentation": ["docs/", "onboarding/"],
            "deployment": ["deploy/", "render.yaml", "Dockerfile"],
            "testing": ["tests/", "temp_tests/"],
            "scripts": ["scripts/"]
        }
    
    def scan_current_scope(self) -> Dict:
        """Scan current project scope and structure"""
        scope = {
            "timestamp": datetime.now().isoformat(),
            "files": {},
            "directories": {},
            "dependencies": {},
            "configurations": {},
            "metrics": {}
        }
        
        # Scan file structure
        for root, dirs, files in os.walk(self.project_root):
            rel_root = Path(root).relative_to(self.project_root)
            
            for file in files:
                if file.endswith(('.py', '.yaml', '.yml', '.json', '.md')):
                    file_path = rel_root / file
                    try:
                        full_path = Path(root) / file
                        scope["files"][str(file_path)] = {
                            "size": os.path.getsize(full_path),
                            "modified": datetime.fromtimestamp(
                                os.path.getmtime(full_path)
                            ).isoformat(),
                            "category": self._categorize_file(file_path)
                        }
                    except (OSError, ValueError) as e:
                        # Skip files that can't be read
                        continue
        
        # Scan directories
        for category, patterns in self.scope_categories.items():
            scope["directories"][category] = []
            for pattern in patterns:
                pattern_path = self.project_root / pattern
                if pattern_path.exists():
                    scope["directories"][category].append(pattern)
        
        # Scan dependencies
        scope["dependencies"] = self._scan_dependencies()
        
        # Scan configurations
        scope["configurations"] = self._scan_configurations()
        
        # Calculate metrics
        scope["metrics"] = self._calculate_scope_metrics(scope)
        
        return scope
    
    def _categorize_file(self, file_path: Path) -> str:
        """Categorize file based on path and content"""
        for category, patterns in self.scope_categories.items():
            for pattern in patterns:
                if pattern in str(file_path):
                    return category
        
        # Default categorization
        if file_path.suffix == '.py':
            return 'analytics' if 'analytics' in str(file_path) else 'infrastructure'
        elif file_path.suffix in ['.yaml', '.yml']:
            return 'configuration'
        elif file_path.suffix == '.md':
            return 'documentation'
        else:
            return 'other'
    
    def _scan_dependencies(self) -> Dict:
        """Scan project dependencies"""
        dependencies = {}
        
        # Check requirements.txt
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                dependencies["requirements"] = deps
            except Exception as e:
                dependencies["requirements"] = [f"Error reading: {e}"]
        
        # Check for common imports in Python files
        python_files = list(self.project_root.rglob("*.py"))
        imports = set()
        
        for py_file in python_files[:50]:  # Limit to avoid performance issues
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract import statements
                    import_matches = re.findall(r'^(?:from|import)\s+(\w+)', content, re.MULTILINE)
                    imports.update(import_matches)
            except Exception:
                continue
        
        dependencies["imports"] = list(imports)
        return dependencies
    
    def _scan_configurations(self) -> Dict:
        """Scan configuration files"""
        configs = {}
        
        # Check config.yaml
        config_file = self.project_root / "config" / "config.yaml"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    configs["main_config"] = yaml.safe_load(f)
            except Exception as e:
                configs["main_config"] = f"Error reading: {e}"
        
        # Check render.yaml
        render_file = self.project_root / "render.yaml"
        if render_file.exists():
            try:
                with open(render_file, 'r') as f:
                    configs["deployment"] = yaml.safe_load(f)
            except Exception as e:
                configs["deployment"] = f"Error reading: {e}"
        
        return configs
    
    def _calculate_scope_metrics(self, scope: Dict) -> Dict:
        """Calculate scope metrics"""
        metrics = {
            "total_files": len(scope["files"]),
            "file_categories": {},
            "total_size": 0,
            "recent_changes": 0
        }
        
        # Count files by category
        for file_info in scope["files"].values():
            category = file_info["category"]
            metrics["file_categories"][category] = metrics["file_categories"].get(category, 0) + 1
            metrics["total_size"] += file_info["size"]
            
            # Count recent changes (last 24 hours)
            file_time = datetime.fromisoformat(file_info["modified"])
            if (datetime.now() - file_time).days < 1:
                metrics["recent_changes"] += 1
        
        return metrics
    
    def load_historical_scope(self) -> Optional[Dict]:
        """Load historical scope data"""
        if self.scope_history_file.exists():
            try:
                with open(self.scope_history_file, 'r') as f:
                    history = json.load(f)
                    # Return the most recent scope
                    if history and "scopes" in history:
                        return history["scopes"][-1] if history["scopes"] else None
            except Exception as e:
                print(f"Warning: Could not load historical scope: {e}")
        return None
    
    def compare_scopes(self, current: Dict, historical: Optional[Dict]) -> Dict:
        """Compare current scope with historical scope"""
        if not historical:
            return {
                "change_percentage": 0.0,
                "type": "initial_scan",
                "changes": [],
                "impact_level": "none",
                "affected_components": [],
                "recommended_action": "Continue with current scope"
            }
        
        changes = []
        change_score = 0.0
        
        # Compare file structure
        current_files = set(current["files"].keys())
        historical_files = set(historical["files"].keys())
        
        new_files = current_files - historical_files
        deleted_files = historical_files - current_files
        modified_files = []
        
        # Check for modified files
        for file in current_files & historical_files:
            if (current["files"][file]["modified"] != 
                historical["files"][file]["modified"]):
                modified_files.append(file)
        
        # Calculate change score
        total_files = len(current_files | historical_files)
        if total_files > 0:
            change_score = len(new_files | deleted_files | set(modified_files)) / total_files
        
        # Categorize changes
        if new_files:
            changes.append(f"Added {len(new_files)} new files")
        if deleted_files:
            changes.append(f"Removed {len(deleted_files)} files")
        if modified_files:
            changes.append(f"Modified {len(modified_files)} files")
        
        # Compare dependencies
        current_deps = set(current["dependencies"].get("requirements", []) or [])
        historical_deps = set(historical["dependencies"].get("requirements", []) or [])
        
        new_deps = current_deps - historical_deps
        removed_deps = historical_deps - current_deps
        
        if new_deps:
            changes.append(f"Added {len(new_deps)} new dependencies")
        if removed_deps:
            changes.append(f"Removed {len(removed_deps)} dependencies")
        
        # Determine impact level
        if change_score > 0.3:
            impact_level = "high"
        elif change_score > 0.1:
            impact_level = "medium"
        else:
            impact_level = "low"
        
        # Determine change type
        if len(new_files) > len(deleted_files) * 2:
            change_type = "feature_addition"
        elif len(deleted_files) > len(new_files) * 2:
            change_type = "feature_removal"
        elif len(modified_files) > len(new_files | deleted_files):
            change_type = "refactoring"
        else:
            change_type = "mixed"
        
        return {
            "change_percentage": change_score,
            "type": change_type,
            "changes": changes,
            "impact_level": impact_level,
            "affected_components": list(new_files | deleted_files | set(modified_files)),
            "recommended_action": self._get_recommended_action(change_type, impact_level),
            "details": {
                "new_files": list(new_files),
                "deleted_files": list(deleted_files),
                "modified_files": modified_files,
                "new_dependencies": list(new_deps),
                "removed_dependencies": list(removed_deps)
            }
        }
    
    def _get_recommended_action(self, change_type: str, impact_level: str) -> str:
        """Get recommended action based on change type and impact"""
        actions = {
            "feature_addition": {
                "low": "Continue development, integrate new features",
                "medium": "Review new features, update priorities",
                "high": "Major scope change - reassess entire project plan"
            },
            "feature_removal": {
                "low": "Clean up documentation, remove references",
                "medium": "Update affected components, revise architecture",
                "high": "Major simplification - update all documentation"
            },
            "refactoring": {
                "low": "Update affected documentation",
                "medium": "Review refactored components, update interfaces",
                "high": "Major refactoring - validate all integrations"
            },
            "mixed": {
                "low": "Review changes, update documentation",
                "medium": "Assess impact, update priorities",
                "high": "Complex changes - comprehensive review required"
            }
        }
        
        return actions.get(change_type, {}).get(impact_level, "Review changes and update documentation")
    
    def save_scope_history(self, current_scope: Dict):
        """Save current scope to history"""
        history = {
            "last_updated": datetime.now().isoformat(),
            "scopes": []
        }
        
        # Load existing history
        if self.scope_history_file.exists():
            try:
                with open(self.scope_history_file, 'r') as f:
                    history = json.load(f)
            except Exception:
                pass
        
        # Add current scope
        history["scopes"].append(current_scope)
        
        # Keep only last 10 scopes to prevent file bloat
        if len(history["scopes"]) > 10:
            history["scopes"] = history["scopes"][-10:]
        
        # Ensure directory exists
        self.scope_history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save updated history
        with open(self.scope_history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def generate_scope_report(self, changes: Dict):
        """Generate scope change report"""
        report = f"""# 🔄 Scope Change Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Scanner:** VectorFlow Scope Change Detection System

---

## 📊 Change Summary

**Change Type:** {changes['type'].replace('_', ' ').title()}  
**Impact Level:** {changes['impact_level'].upper()}  
**Change Percentage:** {changes['change_percentage']:.1%}  
**Total Changes:** {len(changes['changes'])}

---

## 🎯 Changes Detected

"""
        
        for change in changes['changes']:
            report += f"- {change}\n"
        
        report += f"""

---

## 📁 Affected Components

"""
        
        if changes['details']['new_files']:
            report += "### ✅ New Files\n"
            for file in changes['details']['new_files'][:10]:  # Limit display
                report += f"- `{file}`\n"
            if len(changes['details']['new_files']) > 10:
                report += f"- ... and {len(changes['details']['new_files']) - 10} more\n"
            report += "\n"
        
        if changes['details']['deleted_files']:
            report += "### ❌ Deleted Files\n"
            for file in changes['details']['deleted_files'][:10]:
                report += f"- `{file}`\n"
            if len(changes['details']['deleted_files']) > 10:
                report += f"- ... and {len(changes['details']['deleted_files']) - 10} more\n"
            report += "\n"
        
        if changes['details']['modified_files']:
            report += "### 🔄 Modified Files\n"
            for file in changes['details']['modified_files'][:10]:
                report += f"- `{file}`\n"
            if len(changes['details']['modified_files']) > 10:
                report += f"- ... and {len(changes['details']['modified_files']) - 10} more\n"
            report += "\n"
        
        report += f"""

---

## 🚨 Recommended Action

**{changes['recommended_action']}**

---

## 📋 Next Steps

1. **Review changes** - Understand what was added, removed, or modified
2. **Update documentation** - Ensure PROJECT_STATUS_TRACKER.md reflects changes
3. **Assess impact** - Determine how changes affect current work
4. **Adapt strategy** - Modify implementation approach if needed
5. **Update priorities** - Adjust task priorities based on scope evolution

---

## 🔍 Detailed Analysis

### Dependencies
"""
        
        if changes['details']['new_dependencies']:
            report += "**New Dependencies:**\n"
            for dep in changes['details']['new_dependencies']:
                report += f"- {dep}\n"
            report += "\n"
        
        if changes['details']['removed_dependencies']:
            report += "**Removed Dependencies:**\n"
            for dep in changes['details']['removed_dependencies']:
                report += f"- {dep}\n"
            report += "\n"
        
        report += """---

*This report is automatically generated. Review and act on changes to maintain project continuity.*
"""
        
        with open(self.scope_report_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def trigger_scope_change_alert(self, changes: Dict):
        """Trigger scope change alert for AI models"""
        if changes['change_percentage'] > self.change_threshold:
            alert = f"""
🚨 SCOPE CHANGE DETECTED

**Change Type:** {changes['type'].replace('_', ' ').title()}
**Impact Level:** {changes['impact_level'].upper()}
**Change Percentage:** {changes['change_percentage']:.1%}
**Affected Components:** {len(changes['affected_components'])} files

**IMMEDIATE STEPS:**
1. Review scope change report: onboarding/SCOPE_CHANGE_REPORT.md
2. Update PROJECT_STATUS_TRACKER.md with new scope
3. Assess impact on current work priorities
4. Adapt implementation strategy if needed
5. Update AI_HANDOVER_PROTOCOL.md if handover process changes

**Recommended Action:** {changes['recommended_action']}
"""
            print(alert)
            
            # Update status tracker with scope change warning
            self._update_status_tracker_with_scope_change(changes)
    
    def _update_status_tracker_with_scope_change(self, changes: Dict):
        """Update status tracker to reflect scope changes"""
        status_file = self.project_root / "onboarding" / "PROJECT_STATUS_TRACKER.md"
        
        if status_file.exists():
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add scope change warning at the top
                warning = f"""
## 🚨 SCOPE CHANGE ALERT

**⚠️ SCOPE CHANGE DETECTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**

**Change Type:** {changes['type'].replace('_', ' ').title()}  
**Impact Level:** {changes['impact_level'].upper()}  
**Change Percentage:** {changes['change_percentage']:.1%}

**IMMEDIATE ACTION REQUIRED:**
1. Review `onboarding/SCOPE_CHANGE_REPORT.md` for detailed analysis
2. Update work priorities based on scope evolution
3. Adapt existing implementations to new scope
4. Update documentation to reflect changes

**Recommended Action:** {changes['recommended_action']}

---

"""
                
                # Insert warning after the title
                lines = content.split('\n')
                insert_index = 0
                for i, line in enumerate(lines):
                    if line.startswith('## '):
                        insert_index = i
                        break
                
                lines.insert(insert_index, warning)
                
                with open(status_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                    
            except Exception as e:
                print(f"Warning: Could not update status tracker: {e}")
    
    def detect_and_report(self) -> Dict:
        """Main method to detect scope changes and generate report"""
        print("Scanning for scope changes...")
        
        try:
            # Scan current scope
            current_scope = self.scan_current_scope()
            print("Current scope scanned")
            
            # Load historical scope
            historical_scope = self.load_historical_scope()
            print("Historical scope loaded")
            
            # Compare scopes
            changes = self.compare_scopes(current_scope, historical_scope)
            print("Scopes compared")
            
            # Save current scope to history
            self.save_scope_history(current_scope)
            print("Scope history saved")
            
            # Generate report if changes detected
            if changes['change_percentage'] > 0:
                self.generate_scope_report(changes)
                self.trigger_scope_change_alert(changes)
                print(f"Scope change report generated: {self.scope_report_file}")
            else:
                print("No significant scope changes detected")
            
            return changes
            
        except Exception as e:
            print(f"Error in detect_and_report: {e}")
            import traceback
            traceback.print_exc()
            raise


def main():
    """Run the scope change detection system"""
    print("VectorFlow Scope Change Detection System")
    print("=" * 50)
    
    try:
        detector = ScopeChangeDetector()
        changes = detector.detect_and_report()
        
        if changes['change_percentage'] > 0:
            print(f"\nScope Change Summary:")
            print(f"   Type: {changes['type']}")
            print(f"   Impact: {changes['impact_level']}")
            print(f"   Change: {changes['change_percentage']:.1%}")
            print(f"   Action: {changes['recommended_action']}")
        else:
            print("\nProject scope is stable")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
