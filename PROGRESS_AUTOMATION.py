#!/usr/bin/env python3
"""
VectorFlow Progress Automation System

This script automatically tracks project progress and prevents new AI models
from working on completed tasks. It scans the codebase and updates status
based on actual file existence and implementation completeness.
"""

import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re


class ProgressTracker:
    """
    Automated progress tracking for VectorFlow project.
    Prevents AI confusion by tracking what's actually completed.
    """
    
    def __init__(self, project_root: str = ".."):
        self.project_root = Path(project_root).resolve()
        self.status_file = self.project_root / "onboarding" / "PROJECT_STATUS_TRACKER.md"
        self.progress_db = self.project_root / "onboarding" / "progress_database.json"
        
        # Define component expectations
        self.expected_components = {
            "infrastructure": {
                "unified_data_service": {
                    "file": "data_pipeline/unified_data_service_v2.py",
                    "required_classes": ["UnifiedDataServiceV2"],
                    "required_methods": ["start", "stop", "collect_data"]
                },
                "unified_analytics_service": {
                    "file": "analytics/unified_analytics_service.py", 
                    "required_classes": ["UnifiedAnalyticsService"],
                    "required_methods": ["process_data", "get_signals"]
                },
                "database_pool": {
                    "file": "utils/database_pool.py",
                    "required_classes": ["DatabasePool"],
                    "required_methods": ["execute", "batch_insert"]
                },
                "config_management": {
                    "file": "config/config.yaml",
                    "required_keys": ["exchanges", "symbols", "analytics"]
                }
            },
            
            "analytics_modules": {
                "tpo_analyzer": {
                    "file": "analytics/tpo_market_profile.py",
                    "required_classes": ["TPOMarketProfile"],
                    "required_methods": ["analyze", "detect_anomalies"]
                },
                "regime_detector": {
                    "file": "analytics/regime_detector.py",
                    "required_classes": ["RegimeDetector"],
                    "required_methods": ["detect_regime", "get_confidence"]
                },
                "trap_detector": {
                    "file": "analytics/advanced_trap_spoof_detector.py",
                    "required_classes": ["AdvancedTrapSpoofDetector"],
                    "required_methods": ["detect_traps", "calculate_confidence"]
                },
                "supply_demand": {
                    "file": "analytics/multi_timeframe_supply_demand.py",
                    "required_classes": ["MultiTimeframeSupplyDemand"],
                    "required_methods": ["detect_zones", "get_strength"]
                }
            },
            
            "critical_missing": {
                "oi_5s_aggregator": {
                    "file": "analytics/oi_5s_aggregator.py",
                    "required_classes": ["OI5sAggregator"],
                    "required_methods": ["aggregate_oi", "detect_spikes", "check_whole_numbers"],
                    "status": "NOT_STARTED"
                },
                "signal_fusion_engine": {
                    "file": "analytics/signal_fusion_engine.py",
                    "required_classes": ["SignalFusionEngine"],
                    "required_methods": ["fuse_signals", "calculate_holistic_score", "generate_reasons"],
                    "status": "NOT_STARTED"
                },
                "ai_playbook_generator": {
                    "file": "analytics/ai_playbook_generator.py",
                    "required_classes": ["AIPlaybookGenerator"],
                    "required_methods": ["generate_playbooks", "query_grok", "fallback_generation"],
                    "status": "NOT_STARTED"
                },
                "dashboard_mvp": {
                    "file": "dashboard/streamlit_mvp.py",
                    "required_functions": ["main", "render_chart", "render_terminal"],
                    "status": "NOT_STARTED"
                }
            }
        }
    
    def scan_codebase(self) -> Dict[str, Dict]:
        """Scan codebase and determine actual completion status"""
        results = {
            "infrastructure": {},
            "analytics_modules": {},
            "critical_missing": {},
            "scan_timestamp": datetime.now().isoformat()
        }
        
        for category, components in self.expected_components.items():
            results[category] = {}
            
            for component_name, config in components.items():
                file_path = self.project_root / config["file"]
                completion_status = self._check_component_completion(file_path, config)
                
                results[category][component_name] = {
                    "file_path": config["file"],
                    "exists": file_path.exists(),
                    "completion_percentage": completion_status["percentage"],
                    "missing_elements": completion_status["missing"],
                    "status": completion_status["status"],
                    "last_modified": self._get_file_timestamp(file_path)
                }
        
        return results
    
    def _check_component_completion(self, file_path: Path, config: Dict) -> Dict:
        """Check completion status of a specific component"""
        if not file_path.exists():
            return {
                "percentage": 0,
                "missing": ["File does not exist"],
                "status": "NOT_STARTED"
            }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            missing_elements = []
            total_elements = 0
            found_elements = 0
            
            # Check for required classes
            if "required_classes" in config:
                for class_name in config["required_classes"]:
                    total_elements += 1
                    if f"class {class_name}" in content:
                        found_elements += 1
                    else:
                        missing_elements.append(f"Class: {class_name}")
            
            # Check for required methods
            if "required_methods" in config:
                for method_name in config["required_methods"]:
                    total_elements += 1
                    if f"def {method_name}" in content:
                        found_elements += 1
                    else:
                        missing_elements.append(f"Method: {method_name}")
            
            # Check for required functions (for non-class files)
            if "required_functions" in config:
                for func_name in config["required_functions"]:
                    total_elements += 1
                    if f"def {func_name}" in content:
                        found_elements += 1
                    else:
                        missing_elements.append(f"Function: {func_name}")
            
            # Check for required keys (for config files)
            if "required_keys" in config and file_path.suffix in ['.yaml', '.yml']:
                try:
                    yaml_content = yaml.safe_load(content)
                    for key in config["required_keys"]:
                        total_elements += 1
                        if key in yaml_content:
                            found_elements += 1
                        else:
                            missing_elements.append(f"Config key: {key}")
                except yaml.YAMLError:
                    missing_elements.append("Invalid YAML format")
            
            if total_elements == 0:
                percentage = 100  # File exists with content
                status = "COMPLETED"
            else:
                percentage = (found_elements / total_elements) * 100
                if percentage == 100:
                    status = "COMPLETED"
                elif percentage > 50:
                    status = "IN_PROGRESS"
                else:
                    status = "STARTED"
            
            return {
                "percentage": round(percentage, 1),
                "missing": missing_elements,
                "status": status
            }
            
        except Exception as e:
            return {
                "percentage": 0,
                "missing": [f"Error reading file: {str(e)}"],
                "status": "ERROR"
            }
    
    def _get_file_timestamp(self, file_path: Path) -> Optional[str]:
        """Get last modification timestamp of file"""
        if file_path.exists():
            timestamp = file_path.stat().st_mtime
            return datetime.fromtimestamp(timestamp).isoformat()
        return None
    
    def generate_status_report(self) -> str:
        """Generate comprehensive status report"""
        scan_results = self.scan_codebase()
        
        report = f"""# 🤖 AUTOMATED PROJECT STATUS REPORT

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Scanner:** VectorFlow Progress Automation System  

---

## 🎯 COMPLETION OVERVIEW

"""
        
        # Calculate overall progress
        total_components = 0
        completed_components = 0
        
        for category, components in scan_results.items():
            if category == "scan_timestamp":
                continue
                
            category_total = len(components)
            category_completed = sum(1 for comp in components.values() 
                                   if comp["completion_percentage"] == 100)
            
            total_components += category_total
            completed_components += category_completed
            
            completion_rate = (category_completed / category_total) * 100 if category_total > 0 else 0
            
            report += f"""### {category.replace('_', ' ').title()}
- **Progress:** {completion_rate:.1f}% ({category_completed}/{category_total} components)
- **Status:** {'✅ COMPLETE' if completion_rate == 100 else '🔄 IN PROGRESS' if completion_rate > 0 else '❌ NOT STARTED'}

"""
        
        overall_progress = (completed_components / total_components) * 100 if total_components > 0 else 0
        
        report += f"""---

## 📊 OVERALL PROJECT STATUS

**Total Progress:** {overall_progress:.1f}% ({completed_components}/{total_components} components complete)

"""
        
        # Detailed component status
        report += """---

## 📋 DETAILED COMPONENT STATUS

"""
        
        for category, components in scan_results.items():
            if category == "scan_timestamp":
                continue
                
            report += f"""### {category.replace('_', ' ').title()}

"""
            
            for comp_name, details in components.items():
                status_emoji = {
                    "COMPLETED": "✅",
                    "IN_PROGRESS": "🔄", 
                    "STARTED": "🟡",
                    "NOT_STARTED": "❌",
                    "ERROR": "💥"
                }.get(details["status"], "❓")
                
                report += f"""#### {status_emoji} {comp_name.replace('_', ' ').title()}
- **File:** `{details['file_path']}`
- **Status:** {details['status']} ({details['completion_percentage']:.1f}% complete)
- **Exists:** {'Yes' if details['exists'] else 'No'}
"""
                
                if details["missing_elements"]:
                    report += f"- **Missing:** {', '.join(details['missing_elements'])}\n"
                
                if details["last_modified"]:
                    report += f"- **Last Modified:** {details['last_modified']}\n"
                
                report += "\n"
        
        # Critical next steps
        report += """---

## 🚨 CRITICAL NEXT STEPS FOR NEW AI

### Immediate Priorities (Start Here)
"""
        
        critical_missing = scan_results.get("critical_missing", {})
        for comp_name, details in critical_missing.items():
            if details["status"] == "NOT_STARTED":
                report += f"""
**{comp_name.replace('_', ' ').title()}**
- 📁 Create: `{details['file_path']}`
- 🎯 Priority: HIGH (Core system component)
- ⚠️ Blocker: Required for system functionality
"""
        
        # Warnings section
        report += """

### ⚠️ WARNINGS - DO NOT DUPLICATE WORK

"""
        
        completed_infrastructure = [name for name, details in scan_results.get("infrastructure", {}).items() 
                                   if details["completion_percentage"] == 100]
        completed_analytics = [name for name, details in scan_results.get("analytics_modules", {}).items() 
                              if details["completion_percentage"] == 100]
        
        if completed_infrastructure:
            report += f"**✅ Infrastructure Complete:** {', '.join(completed_infrastructure)}\n"
        
        if completed_analytics:
            report += f"**✅ Analytics Modules Complete:** {', '.join(completed_analytics)}\n"
        
        report += """
**❌ DO NOT:** Rebuild completed components  
**✅ DO:** Focus on missing critical components  
**🎯 GOAL:** Complete the signal fusion and AI integration

---

*This report is automatically generated. Update by running: `python onboarding/PROGRESS_AUTOMATION.py`*
"""
        
        return report
    
    def save_progress_database(self):
        """Save detailed progress data for future reference"""
        scan_results = self.scan_codebase()
        
        # Add metadata
        scan_results["metadata"] = {
            "project_root": str(self.project_root),
            "scan_timestamp": datetime.now().isoformat(),
            "scanner_version": "1.0.0"
        }
        
        # Ensure directory exists
        self.progress_db.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.progress_db, 'w') as f:
            json.dump(scan_results, f, indent=2)
        
        print(f"Progress database saved to: {self.progress_db}")
    
    def update_status_tracker(self):
        """Update the PROJECT_STATUS_TRACKER.md file with current status"""
        report = self.generate_status_report()
        
        with open(self.status_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Status tracker updated: {self.status_file}")
    
    def check_for_new_work(self, last_scan_file: str = None) -> List[str]:
        """Check for newly completed work since last scan"""
        if not last_scan_file or not Path(last_scan_file).exists():
            return ["First scan - no comparison available"]
        
        try:
            with open(last_scan_file, 'r') as f:
                previous_scan = json.load(f)
            
            current_scan = self.scan_codebase()
            changes = []
            
            for category in ["infrastructure", "analytics_modules", "critical_missing"]:
                if category in previous_scan and category in current_scan:
                    for comp_name in current_scan[category]:
                        if comp_name in previous_scan[category]:
                            old_status = previous_scan[category][comp_name]["status"]
                            new_status = current_scan[category][comp_name]["status"]
                            
                            if old_status != new_status:
                                changes.append(f"{comp_name}: {old_status} → {new_status}")
            
            return changes
            
        except Exception as e:
            return [f"Error comparing scans: {str(e)}"]


def main():
    """Run the progress automation system"""
    print("VectorFlow Progress Automation System")
    print("=" * 50)
    
    try:
        # Initialize tracker
        tracker = ProgressTracker()
        
        # Check for changes since last scan
        previous_db = tracker.progress_db
        if previous_db.exists():
            changes = tracker.check_for_new_work(str(previous_db))
            if changes and changes[0] != "First scan - no comparison available":
                print("\nRecent Changes Detected:")
                for change in changes:
                    print(f"  • {change}")
                print()
        
        # Generate current status
        print("Scanning codebase...")
        tracker.save_progress_database()
        
        print("Updating status tracker...")
        tracker.update_status_tracker()
        
        print("\nAutomation complete!")
        print(f"View status: onboarding/PROJECT_STATUS_TRACKER.md")
        print(f"Raw data: onboarding/progress_database.json")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
