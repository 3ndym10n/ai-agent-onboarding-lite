#!/usr / bin / env python3
"""
Comprehensive Test Report Generator

Generates detailed HTML and JSON reports from enhanced test runs,
including trend analysis, performance insights, and actionable recommendations.

This is part of Phase 1: Enhanced Testing Foundation (T32)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class ComprehensiveTestReporter:
    """Generate comprehensive test reports with trends and insights."""

    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_comprehensive_report(
        self, current_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a comprehensive report with historical trends."""
        # Load historical reports
        historical_reports = self._load_historical_reports()

        # Analyze trends
        trend_analysis = self._analyze_trends(historical_reports + [current_report])

        # Generate insights
        insights = self._generate_comprehensive_insights(current_report, trend_analysis)

        # Create comprehensive report
        comprehensive_report = {
            "generated_at": datetime.now().isoformat(),
            "report_type": "comprehensive_test_report",
            "current_run": current_report,
            "historical_analysis": trend_analysis,
            "insights": insights,
            "recommendations": self._generate_recommendations(
                current_report, trend_analysis
            ),
            "visualizations": self._generate_visualizations(
                current_report, historical_reports
            ),
            "metadata": {
                "total_historical_reports": len(historical_reports),
                "analysis_period_days": self._calculate_analysis_period(
                    historical_reports
                ),
                "report_version": "1.0",
            },
        }

        return comprehensive_report

    def _load_historical_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Load recent historical test reports."""
        reports = []

        if not self.reports_dir.exists():
            return reports

        # Find all enhanced test reports
        report_files = list(self.reports_dir.glob("enhanced_test_report_*.json"))
        report_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        for report_file in report_files[:limit]:
            try:
                with open(report_file, "r") as f:
                    report_data = json.load(f)
                    # Add file metadata
                    report_data["_file_path"] = str(report_file)
                    report_data["_timestamp"] = datetime.fromtimestamp(
                        report_file.stat().st_mtime
                    ).isoformat()
                    reports.append(report_data)
            except:
                continue

        return reports

    def _analyze_trends(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends across multiple test reports."""
        if len(reports) < 2:
            return {"note": "Need at least 2 reports for trend analysis"}

        # Extract metrics over time
        timeline_data = []
        for report in reports:
            summary = report.get("summary", {})
            timestamp = report.get("_timestamp", datetime.now().isoformat())

            timeline_data.append(
                {
                    "timestamp": timestamp,
                    "success_rate": summary.get("success_rate", 0),
                    "total_tests": summary.get("total_tests", 0),
                    "passed_tests": summary.get("passed_tests", 0),
                }
            )

        # Sort by timestamp
        timeline_data.sort(key=lambda x: x["timestamp"])

        # Calculate trends
        trends = {
            "success_rate_trend": self._calculate_trend(
                [d["success_rate"] for d in timeline_data]
            ),
            "test_count_trend": self._calculate_trend(
                [d["total_tests"] for d in timeline_data]
            ),
            "timeline_data": timeline_data,
            "analysis_period": f"{len(timeline_data)} test runs",
        }

        return trends

    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and magnitude."""
        if len(values) < 2:
            return {"direction": "insufficient_data", "magnitude": 0.0}

        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))
        y = values

        # Calculate slope
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
        denominator = sum((xi - x_mean) ** 2 for xi in x)

        if denominator == 0:
            slope = 0.0
        else:
            slope = numerator / denominator

        # Determine direction and magnitude
        if abs(slope) < 0.1:
            direction = "stable"
            magnitude = abs(slope) * 10  # Scale for percentage
        elif slope > 0:
            direction = "improving"
            magnitude = slope
        else:
            direction = "degrading"
            magnitude = abs(slope)

        return {
            "direction": direction,
            "magnitude": round(magnitude, 3),
            "slope": round(slope, 3),
            "start_value": round(values[0], 2),
            "end_value": round(values[-1], 2),
            "change": round(values[-1] - values[0], 2),
        }

    def _generate_comprehensive_insights(
        self, current_report: Dict[str, Any], trends: Dict[str, Any]
    ) -> List[str]:
        """Generate comprehensive insights from current report and trends."""
        insights = []

        # Current performance insights
        summary = current_report.get("summary", {})
        success_rate = summary.get("success_rate", 0)

        if success_rate == 100:
            insights.append(
                "🎯 PERFECT: All tests passing - system operating at peak performance"
            )
        elif success_rate >= 90:
            insights.append(
                "✅ EXCELLENT: High test success rate indicates robust system health"
            )
        elif success_rate >= 75:
            insights.append("⚠️ GOOD: Acceptable performance with room for improvement")
        else:
            insights.append("❌ CONCERNS: Test success rate needs attention")

        # Trend insights
        success_trend = trends.get("success_rate_trend", {})
        if success_trend.get("direction") == "improving":
            insights.append(".1f")
        elif success_trend.get("direction") == "degrading":
            insights.append(".1f")
        elif success_trend.get("direction") == "stable":
            insights.append("📊 STABLE: Test performance consistent over time")

        # Performance insights
        perf_analysis = current_report.get("smart_debugger_analysis", {})
        if perf_analysis:
            avg_confidence = perf_analysis.get("average_confidence_score", 0)
            if avg_confidence >= 0.8:
                insights.append(
                    "🤖 EXCELLENT: SmartDebugger confidence indicates strong error analysis"
                )
            elif avg_confidence >= 0.6:
                insights.append("🤖 GOOD: SmartDebugger performing adequately")
            else:
                insights.append(
                    "🤖 IMPROVEMENT NEEDED: SmartDebugger confidence could be higher"
                )

        # Test coverage insights
        total_tests = summary.get("total_tests", 0)
        if total_tests >= 10:
            insights.append(
                "📊 COMPREHENSIVE: Good test coverage across system components"
            )
        elif total_tests >= 5:
            insights.append("📊 MODERATE: Basic test coverage in place")
        else:
            insights.append("📊 LIMITED: Consider expanding test coverage")

        return insights

    def _generate_recommendations(
        self, current_report: Dict[str, Any], trends: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        summary = current_report.get("summary", {})
        success_rate = summary.get("success_rate", 0)

        # Based on current performance
        if success_rate < 90:
            recommendations.append("Investigate failing tests and address root causes")
        elif success_rate < 100:
            recommendations.append(
                "Review remaining test failures for potential improvements"
            )

        # Based on trends
        success_trend = trends.get("success_rate_trend", {})
        if success_trend.get("direction") == "degrading":
            recommendations.append(
                "Monitor performance degradation and identify contributing factors"
            )

        # SmartDebugger recommendations
        smart_analysis = current_report.get("smart_debugger_analysis", {})
        if smart_analysis:
            avg_confidence = smart_analysis.get("average_confidence_score", 0)
            if avg_confidence < 0.7:
                recommendations.append(
                    "Consider enhancing SmartDebugger training data for better accuracy"
                )

        # Test coverage recommendations
        total_tests = summary.get("total_tests", 0)
        if total_tests < 8:
            recommendations.append(
                "Expand test coverage to include more system components"
            )

        # Performance recommendations
        if not recommendations:  # If no issues found
            recommendations.append(
                "Continue monitoring system performance and test reliability"
            )
            recommendations.append("Consider adding performance regression tests")

        return recommendations

    def _generate_visualizations(
        self, current_report: Dict[str, Any], historical_reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate text - based visualizations."""
        visualizations = {
            "performance_chart": self._generate_performance_chart(current_report),
            "trend_chart": self._generate_trend_chart(historical_reports),
            "health_gauge": self._generate_health_gauge(current_report),
            "test_distribution": self._generate_test_distribution(current_report),
        }

        return visualizations

    def _generate_performance_chart(self, report: Dict[str, Any]) -> str:
        """Generate a simple ASCII performance chart."""
        summary = report.get("summary", {})
        success_rate = summary.get("success_rate", 0)

        # Create a simple bar chart
        width = 20
        filled = int(width * success_rate / 100)
        bar = "█" * filled + "░" * (width - filled)

        return f"""
Performance Overview:
Success Rate: {success_rate:.1f}%
[{bar}] {success_rate:.1f}%
        """.strip()

    def _generate_trend_chart(self, historical_reports: List[Dict[str, Any]]) -> str:
        """Generate a trend chart from historical data."""
        if len(historical_reports) < 2:
            return "Insufficient historical data for trend analysis"

        # Extract success rates
        success_rates = []
        for report in historical_reports[-5:]:  # Last 5 reports
            summary = report.get("summary", {})
            success_rates.append(summary.get("success_rate", 0))

        if not success_rates:
            return "No trend data available"

        # Create simple trend line
        chart_lines = ["Recent Test Success Trends:"]
        chart_lines.append("Run | Success Rate")
        chart_lines.append("----|-------------")

        for i, rate in enumerate(success_rates, 1):
            chart_lines.append("2d")

        return "\n".join(chart_lines)

    def _generate_health_gauge(self, report: Dict[str, Any]) -> str:
        """Generate a health gauge visualization."""
        summary = report.get("summary", {})
        success_rate = summary.get("success_rate", 0)

        # Determine health status
        if success_rate >= 95:
            status = "EXCELLENT"
            gauge = "██████████"
        elif success_rate >= 85:
            status = "GOOD"
            gauge = "████████░░"
        elif success_rate >= 75:
            status = "FAIR"
            gauge = "██████░░░░"
        else:
            status = "NEEDS WORK"
            gauge = "███░░░░░░░"

        return f"""
System Health: {status}
[{gauge}] {success_rate:.1f}%
        """.strip()

    def _generate_test_distribution(self, report: Dict[str, Any]) -> str:
        """Generate test distribution visualization."""
        summary = report.get("summary", {})
        total_tests = summary.get("total_tests", 0)
        passed_tests = summary.get("passed_tests", 0)
        failed_tests = total_tests - passed_tests

        if total_tests == 0:
            return "No test data available"

        passed_pct = (passed_tests / total_tests) * 100
        failed_pct = (failed_tests / total_tests) * 100

        # Create distribution bars
        width = 20
        passed_width = int(width * passed_pct / 100)
        failed_width = width - passed_width

        passed_bar = "█" * passed_width
        failed_bar = "█" * failed_width

        return f"""
Test Distribution:
Passed:  {passed_bar} {passed_pct:.1f}% ({passed_tests})
Failed:  {failed_bar} {failed_pct:.1f}% ({failed_tests})
Total:   {'█' * width} 100.0% ({total_tests})
        """.strip()

    def _calculate_analysis_period(self, reports: List[Dict[str, Any]]) -> int:
        """Calculate the analysis period in days."""
        if not reports:
            return 0

        timestamps = []
        for report in reports:
            timestamp = report.get("_timestamp")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamps.append(dt)
                except:
                    continue

        if len(timestamps) < 2:
            return 0

        date_range = max(timestamps) - min(timestamps)
        return max(1, date_range.days)

    def generate_html_report(
        self, comprehensive_report: Dict[str, Any], output_path: Path
    ) -> None:
        """Generate an HTML report from the comprehensive data."""
        html_content = self._generate_html_content(comprehensive_report)

        with open(output_path, "w", encoding="utf - 8") as f:
            f.write(html_content)

    def _generate_html_content(self, report: Dict[str, Any]) -> str:
        """Generate HTML content for the report."""
        current = report["current_run"]
        summary = current.get("summary", {})

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title > AI Onboarding System - Comprehensive Test Report </ title>
    <style>
        body {{ font - family: Arial, sans - serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border - radius: 5px; }}
        .summary {{ background: #ecf0f1; padding: 15px; margin: 10px 0; border - radius: 5px; }}
        .success {{ color: #27ae60; }}
        .warning {{ color: #f39c12; }}
        .error {{ color: #e74c3c; }}
        .metric {{ display: inline - block; margin: 10px; padding: 10px; background: white; border - radius: 5px; }}
        .insights {{ background: #f8f9fa; padding: 15px; margin: 10px 0; }}
        .recommendations {{ background: #d4edda; padding: 15px; margin: 10px 0; border - left: 4px solid #27ae60; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 AI Onboarding System - Comprehensive Test Report </ h1>
        <p > Generated: {report['generated_at']}</p>
        <p > Report Version: {report['metadata']['report_version']}</p>
    </div>

    <div class="summary">
        <h2>📊 Executive Summary </ h2>
        <div class="metric">
            <strong > Success Rate:</strong> <span class="success">{summary.get('success_rate', 0):.1f}%</span>
        </div>
        <div class="metric">
            <strong > Total Tests:</strong> {summary.get('total_tests', 0)}
        </div>
        <div class="metric">
            <strong > Passed:</strong> {summary.get('passed_tests', 0)}
        </div>
        <div class="metric">
            <strong > Failed:</strong> {summary.get('total_tests', 0) - summary.get('passed_tests', 0)}
        </div>
    </div>

    <div class="insights">
        <h3>💡 Key Insights </ h3>
        <ul>
"""

        for insight in report.get("insights", []):
            html += f"            <li>{insight}</li>\n"

        html += "        </ul>\n    </div>\n"

        # Add recommendations
        html += """
    <div class="recommendations">
        <h3>🎯 Recommendations </ h3>
        <ul>
"""

        for rec in report.get("recommendations", []):
            html += f"            <li>{rec}</li>\n"

        html += """
        </ul>
    </div>

    <div class="summary">
        <h3>📈 Trend Analysis </ h3>
        <pre>
"""

        # Add trend chart
        trend_chart = report.get("visualizations", {}).get(
            "trend_chart", "No trend data"
        )
        html += trend_chart

        html += """
        </pre>
    </div>

    <div class="summary">
        <h3>🏥 System Health </ h3>
        <pre>
"""

        # Add health gauge
        health_gauge = report.get("visualizations", {}).get(
            "health_gauge", "No health data"
        )
        html += health_gauge

        html += """
        </pre>
    </div>
</body>
</html>
"""

        return html


def generate_comprehensive_test_report(
    reports_dir: Path, output_dir: Path = None
) -> Dict[str, Any]:
    """
    Generate a comprehensive test report from the latest test run.

    Args:
        reports_dir: Directory containing test reports
        output_dir: Directory to save comprehensive reports

    Returns:
        Dict containing the comprehensive report
    """
    if output_dir is None:
        output_dir = reports_dir

    # Load the most recent test report
    reporter = ComprehensiveTestReporter(reports_dir)
    report_files = list(reports_dir.glob("enhanced_test_report_*.json"))

    if not report_files:
        return {"error": "No test reports found"}

    # Get the most recent report
    latest_report = max(report_files, key=lambda x: x.stat().st_mtime)

    with open(latest_report, "r") as f:
        current_report = json.load(f)

    # Generate comprehensive report
    comprehensive_report = reporter.generate_comprehensive_report(current_report)

    # Save comprehensive report
    timestamp = datetime.now().strftime("%Y % m % d_ % H % M % S")
    json_output = output_dir / f"comprehensive_test_report_{timestamp}.json"
    html_output = output_dir / f"comprehensive_test_report_{timestamp}.html"

    # Save JSON report
    with open(json_output, "w") as f:
        json.dump(comprehensive_report, f, indent=2)

    # Generate and save HTML report
    reporter.generate_html_report(comprehensive_report, html_output)

    comprehensive_report["file_paths"] = {
        "json_report": str(json_output),
        "html_report": str(html_output),
    }

    return comprehensive_report


if __name__ == "__main__":
    # Generate comprehensive test report
    project_root = Path(__file__).parent.parent
    reports_dir = project_root / ".ai_onboard" / "test_reports"

    print("📊 Generating Comprehensive Test Report...")
    print("=" * 60)

    comprehensive_report = generate_comprehensive_test_report(reports_dir)

    if "error" in comprehensive_report:
        print(f"❌ Error: {comprehensive_report['error']}")
        sys.exit(1)

    # Display key metrics
    current = comprehensive_report["current_run"]
    summary = current.get("summary", {})

    print("\n📈 CURRENT RUN SUMMARY:")
    print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
    print(f"   ✅ Passed: {summary.get('passed_tests', 0)}")
    print(
        f"   ❌ Failed: {summary.get('total_tests', 0) - summary.get('passed_tests', 0)}"
    )

    print("\n💡 KEY INSIGHTS:")
    for insight in comprehensive_report.get("insights", [])[:3]:
        print(f"   {insight}")

    print("\n🎯 RECOMMENDATIONS:")
    for rec in comprehensive_report.get("recommendations", [])[:3]:
        print(f"   • {rec}")

    # Display file paths
    files = comprehensive_report.get("file_paths", {})
    print("\n📄 REPORTS GENERATED:")
    if "json_report" in files:
        print(f"   📋 JSON: {files['json_report']}")
    if "html_report" in files:
        print(f"   🌐 HTML: {files['html_report']}")

    print("\n🎉 Comprehensive test reporting complete!")
    print("Phase 1 of Enhanced Testing Foundation: FULLY COMPLETED ✅")
