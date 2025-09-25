#!/usr/bin/env python3
"""
Comprehensive Tool Testing System for ai-onboard.

This script tests all discovered tools to ensure they work correctly,
providing comprehensive validation of the entire tool ecosystem.
"""

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_onboard.core.comprehensive_tool_discovery import ComprehensiveToolDiscovery
from ai_onboard.core.mandatory_tool_consultation_gate import get_mandatory_gate
from ai_onboard.core.unified_tool_orchestrator import UnifiedToolOrchestrator


@dataclass
class ToolTestResult:
    """Result of testing a single tool."""

    tool_name: str
    tool_class: str
    category: str
    executed: bool
    duration_ms: float
    error: Optional[str] = None
    results_summary: Optional[str] = None
    insights: Optional[str] = None


@dataclass
class ComprehensiveToolTestReport:
    """Comprehensive report of all tool tests."""

    total_tools: int
    tested_tools: int
    successful_tools: int
    failed_tools: int
    test_duration_ms: float
    tool_results: List[ToolTestResult] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


class ComprehensiveToolTester:
    """Comprehensive tool testing system."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.discovery = ComprehensiveToolDiscovery(root_path)
        self.orchestrator = UnifiedToolOrchestrator(root_path)
        self.consultation_gate = get_mandatory_gate(root_path)

    def run_comprehensive_tool_tests(self) -> ComprehensiveToolTestReport:
        """Run comprehensive tests on all discovered tools."""
        print("🧪 Starting Comprehensive Tool Testing System")
        print("=" * 60)

        start_time = time.time()

        # Discover all tools
        print("\n🔍 Discovering all tools...")
        discovery_result = self.discovery.discover_all_tools()

        print(f"📊 Found {discovery_result.total_tools} total tools")
        print(
            f"📂 Tools by category: {len(discovery_result.tools_by_category)} categories"
        )

        # Filter out CLI tools (they're command-line functions, not standalone tools)
        cli_tools = {
            name
            for name, meta in discovery_result.all_tools.items()
            if name.startswith("cli_") or "cli_" in name
        }
        core_tools = {
            name: meta
            for name, meta in discovery_result.all_tools.items()
            if not (name.startswith("cli_") or "cli_" in name)
        }

        print(f"📋 Filtered out {len(cli_tools)} CLI tools (command-line functions)")
        print(f"🔧 Testing {len(core_tools)} core analysis tools...")

        # Test each core tool
        tool_results = []
        successful_tools = 0
        failed_tools = 0

        print("\n🚀 Testing core analysis tools...")
        for tool_name, tool_metadata in core_tools.items():
            print(f"\n  🔧 Testing: {tool_name}")

            test_result = self._test_single_tool(tool_name, tool_metadata)
            tool_results.append(test_result)

            if test_result.executed:
                successful_tools += 1
                print(f"    ✅ {tool_name} - SUCCESS ({test_result.duration_ms:.1f}ms)")
                if test_result.results_summary:
                    print(f"       📊 {test_result.results_summary}")
                if test_result.insights:
                    print(f"       💡 {test_result.insights}")
            else:
                failed_tools += 1
                print(f"    ❌ {tool_name} - FAILED ({test_result.duration_ms:.1f}ms)")
                if test_result.error:
                    print(f"       💥 {test_result.error}")

        # Generate summary
        total_duration = (time.time() - start_time) * 1000

        # Categorize results by category
        results_by_category = {}
        for result in tool_results:
            category = result.category
            if category not in results_by_category:
                results_by_category[category] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                }
            results_by_category[category]["total"] += 1
            if result.executed:
                results_by_category[category]["successful"] += 1
            else:
                results_by_category[category]["failed"] += 1

        summary = {
            "total_tools_discovered": len(discovery_result.all_tools),
            "cli_tools_filtered": len(cli_tools),
            "core_tools_tested": len(core_tools),
            "tested_tools": len(tool_results),
            "successful_tools": successful_tools,
            "failed_tools": failed_tools,
            "success_rate": (
                (successful_tools / len(tool_results)) * 100 if tool_results else 0
            ),
            "results_by_category": results_by_category,
            "test_duration_seconds": total_duration / 1000,
        }

        # Print final report
        self._print_final_report(summary, tool_results)

        return ComprehensiveToolTestReport(
            total_tools=len(core_tools),
            tested_tools=len(tool_results),
            successful_tools=successful_tools,
            failed_tools=failed_tools,
            test_duration_ms=total_duration,
            tool_results=tool_results,
            summary=summary,
        )

    def _test_single_tool(self, tool_name: str, tool_metadata) -> ToolTestResult:
        """Test a single tool."""
        start_time = time.time()

        result = ToolTestResult(
            tool_name=tool_name,
            tool_class=tool_metadata.class_name or "Unknown",
            category=tool_metadata.category.value,
            executed=False,
            duration_ms=0.0,
        )

        try:
            # Test through the tool orchestrator
            context = {
                "user_request": f"Test {tool_name} functionality",
                "test_mode": True,
                "consultation_time": time.time(),
            }

            execution_result = self.orchestrator.execute_automatic_tool_application(
                tool_name, context
            )

            result.executed = execution_result.get("executed", False)
            result.error = execution_result.get("error")

            # Extract insights if available (don't fail the tool if insight extraction fails)
            if result.executed and execution_result.get("results"):
                try:
                    result.insights = self._extract_tool_insights(
                        tool_name, execution_result["results"]
                    )
                    result.results_summary = self._summarize_tool_results(
                        tool_name, execution_result["results"]
                    )
                except Exception as e:
                    # Insight extraction failed, but tool executed successfully
                    result.insights = (
                        f"Tool executed successfully but insight extraction failed: {e}"
                    )
                    result.results_summary = "Tool execution successful"

        except Exception as e:
            result.error = str(e)

        result.duration_ms = (time.time() - start_time) * 1000
        return result

    def _extract_tool_insights(self, tool_name: str, results: Any) -> Optional[str]:
        """Extract insights from tool results."""
        try:
            # Use the same logic as the consultation gate
            if tool_name == "dependency_mapper":
                if hasattr(results, "circular_dependencies"):
                    return f"{len(results.circular_dependencies)} circular dependencies detected, {results.modules_analyzed} modules analyzed"
            elif tool_name == "code_quality_analyzer":
                if hasattr(results, "total_issues"):
                    return f"{results.total_issues} quality issues found"
            elif tool_name == "file_organization_analyzer":
                if hasattr(results, "issues"):
                    return f"{len(results.issues)} organization issues found"
            elif tool_name == "duplicate_detector":
                if hasattr(results, "duplicate_groups"):
                    return f"{len(results.duplicate_groups)} duplicate groups found"

            elif tool_name == "vision_guardian":
                if isinstance(results, dict):
                    objectives = len(results.get("objectives", []))
                    return f"Vision context loaded with {objectives} objectives"

            elif tool_name == "gate_system":
                if isinstance(results, dict):
                    active = results.get("gate_active", False)
                    status = "active" if active else "inactive"
                    return f"Gate system {status}"

            elif tool_name == "ultra_safe_cleanup":
                if isinstance(results, dict):
                    targets = results.get("targets_found", 0)
                    size_mb = results.get("total_size_mb", 0)
                    return f"Cleanup scan complete: {targets} targets found ({size_mb:.1f} MB)"

            elif tool_name == "charter_management":
                if isinstance(results, dict):
                    project = results.get("project_name", "Unknown")
                    objectives = results.get("objectives_count", 0)
                    team_size = results.get("team_size", 0)
                    return f"Charter loaded: {project} with {objectives} objectives, team size {team_size}"

            elif tool_name == "automatic_error_prevention":
                if isinstance(results, dict):
                    prevented = results.get("errors_prevented", 0)
                    patterns = results.get("patterns_learned", 0)
                    return f"Error prevention active: {prevented} errors prevented, {patterns} patterns learned"

            elif tool_name == "pattern_recognition_system":
                if isinstance(results, dict):
                    patterns = results.get("total_patterns", 0)
                    matches = results.get("successful_matches", 0)
                    return f"Pattern system active: {patterns} patterns, {matches} successful matches"

            elif tool_name == "task_execution_gate":
                if isinstance(results, dict):
                    pending = results.get("pending_tasks", 0)
                    completed = results.get("completed_tasks", 0)
                    return f"Task gate status: {pending} pending tasks, {completed} completed"

            elif tool_name == "interrogation_system":
                if isinstance(results, dict):
                    sessions = results.get("active_sessions", 0)
                    questions = results.get("total_questions_asked", 0)
                    return f"Interrogation active: {sessions} sessions, {questions} questions asked"

            elif tool_name == "conversation_analysis":
                if isinstance(results, dict):
                    sessions = results.get("total_sessions", 0)
                    continuity = results.get("continuity_score", 0)
                    return f"Conversation analysis: {sessions} sessions, continuity score {continuity:.1f}"

            elif tool_name == "ui_enhancement":
                if isinstance(results, dict):
                    interventions = results.get("pending_interventions", 0)
                    satisfaction = results.get("current_satisfaction", 0)
                    return f"UX enhancements: {interventions} pending interventions, satisfaction {satisfaction:.1f}"

            elif tool_name == "wbs_management":
                if isinstance(results, dict):
                    consistency = results.get("overall_consistency", 0)
                    issues = results.get("total_issues", 0)
                    return f"WBS management: {consistency:.1f}% consistency, {issues} issues found"

            elif tool_name == "ai_agent_orchestration":
                if isinstance(results, dict):
                    active = results.get("is_active", False)
                    tools = results.get("available_tools", 0)
                    return f"AI orchestration {'active' if active else 'inactive'}: {tools} tools available"

            elif tool_name == "decision_pipeline":
                if isinstance(results, dict):
                    active = results.get("pipeline_active", False)
                    capabilities = len(results.get("decision_capabilities", []))
                    return f"Decision pipeline {'active' if active else 'inactive'}: {capabilities} capabilities"

            elif tool_name == "intelligent_monitoring":
                if isinstance(results, dict):
                    triggers = results.get("active_triggers", 0)
                    alerts = results.get("pending_alerts", 0)
                    return f"Intelligent monitoring: {triggers} triggers, {alerts} pending alerts"

            elif tool_name == "user_preference_learning_system":
                if isinstance(results, dict):
                    preferences = results.get("total_preferences", 0)
                    confidence = results.get("avg_confidence", 0)
                    return f"User preferences: {preferences} learned, {confidence:.1f} avg confidence"

            elif tool_name == "automated_health_monitoring":
                if isinstance(results, dict):
                    status = results.get("overall_status", "unknown")
                    healthy = results.get("summary", {}).get("healthy_tools", 0)
                    total = results.get("summary", {}).get("total_tools", 0)
                    return f"Health monitoring: {healthy}/{total} tools healthy, status {status}"

        except Exception:
            pass
        return None

    def _summarize_tool_results(self, tool_name: str, results: Any) -> Optional[str]:
        """Create a summary of tool results."""
        try:
            if hasattr(results, "__dict__"):
                # Get key metrics from the results object
                attrs = [
                    attr
                    for attr in dir(results)
                    if not attr.startswith("_") and not callable(getattr(results, attr))
                ]
                key_attrs = []
                for attr in attrs[:3]:  # Show first 3 attributes
                    value = getattr(results, attr)
                    if isinstance(value, (int, float, str)):
                        key_attrs.append(f"{attr}: {value}")
                return ", ".join(key_attrs) if key_attrs else None
            elif isinstance(results, dict):
                # Get key metrics from dict
                key_items = list(results.items())[:3]  # Show first 3 items
                return ", ".join([f"{k}: {v}" for k, v in key_items])
        except Exception:
            pass
        return None

    def _print_final_report(
        self, summary: Dict[str, Any], tool_results: List[ToolTestResult]
    ):
        """Print the final comprehensive report."""
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE TOOL TESTING REPORT")
        print("=" * 60)

        print(f"📊 Total Tools Discovered: {summary['total_tools_discovered']}")
        print(f"📋 CLI Tools Filtered: {summary['cli_tools_filtered']}")
        print(f"🔧 Core Tools Tested: {summary['core_tools_tested']}")
        print(f"✅ Successful: {summary['successful_tools']}")
        print(f"❌ Failed: {summary['failed_tools']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"⏱️  Test Duration: {summary['test_duration_seconds']:.2f}s")
        print("\n📂 Results by Category:")
        for category, stats in summary["results_by_category"].items():
            success_rate = (
                (stats["successful"] / stats["total"]) * 100
                if stats["total"] > 0
                else 0
            )
            print(
                f"  {category}: {stats['successful']}/{stats['total']} ({success_rate:.1f}%)"
            )

        if summary["failed_tools"] > 0:
            print(f"\n❌ Failed Tools:")
            for result in tool_results:
                if not result.executed:
                    print(f"  • {result.tool_name}: {result.error or 'Unknown error'}")

        print("\n🎉 Tool testing completed!")
        print("=" * 60)


def main():
    """Main entry point."""
    root_path = Path.cwd()

    tester = ComprehensiveToolTester(root_path)
    report = tester.run_comprehensive_tool_tests()

    # Save detailed report
    report_file = root_path / ".ai_onboard" / "tool_test_report.json"
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, "w") as f:
        json.dump(
            {
                "summary": report.summary,
                "tool_results": [
                    {
                        "tool_name": r.tool_name,
                        "tool_class": r.tool_class,
                        "category": r.category,
                        "executed": r.executed,
                        "duration_ms": r.duration_ms,
                        "error": r.error,
                        "results_summary": r.results_summary,
                        "insights": r.insights,
                    }
                    for r in report.tool_results
                ],
            },
            f,
            indent=2,
        )

    print(f"\n📄 Detailed report saved to: {report_file}")

    # Return appropriate exit code
    if report.failed_tools > 0:
        print(f"\n⚠️  {report.failed_tools} tools failed testing")
        return 1
    else:
        print("\n🎉 All tools passed testing!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
