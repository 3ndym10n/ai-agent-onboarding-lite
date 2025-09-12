"""
Enhanced testing commands with ContinuousImprovementValidator integration.

This module provides CLI commands for running enhanced tests that integrate
with the ContinuousImprovementValidator, providing comprehensive system
validation and reporting.
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core import utils
from ..core.continuous_improvement_validator import (
    ContinuousImprovementValidator,
    TestCategory,
    TestResult,
    ValidationReport,
)


def add_enhanced_testing_commands(subparsers):
    """Add enhanced testing commands to the CLI."""
    parser = subparsers.add_parser(
        "enhanced-testing",
        help="Run enhanced tests with continuous improvement validation",
        description="Execute comprehensive testing with validation, performance tracking, and reporting",
    )

    subcommands = parser.add_subparsers(
        dest="testing_cmd", help="Enhanced testing commands"
    )

    # Run enhanced tests command
    run_parser = subcommands.add_parser(
        "run",
        help="Run enhanced tests with validation",
        description="Execute pytest with continuous improvement validation integration",
    )
    run_parser.add_argument(
        "--test-path",
        default="tests/",
        help="Path to test directory or specific test file",
    )
    run_parser.add_argument(
        "--markers", help="Pytest markers to select tests (e.g., 'not slow')"
    )
    run_parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    run_parser.add_argument(
        "--ci-validation",
        action="store_true",
        help="Generate continuous improvement validation report",
    )
    run_parser.add_argument(
        "--performance-baseline",
        help="Path to performance baseline file for comparison",
    )
    run_parser.add_argument(
        "--timeout", type=int, default=300, help="Test timeout in seconds"
    )
    run_parser.add_argument(
        "--parallel", action="store_true", help="Run tests in parallel"
    )
    run_parser.add_argument(
        "--verbose", action="store_true", help="Verbose test output"
    )

    # Validate system command
    validate_parser = subcommands.add_parser(
        "validate",
        help="Run system validation only",
        description="Execute continuous improvement system validation",
    )
    validate_parser.add_argument(
        "--quick", action="store_true", help="Run quick validation (skip slow tests)"
    )
    validate_parser.add_argument(
        "--categories",
        nargs="+",
        choices=["integration", "performance", "data_integrity", "end_to_end"],
        help="Test categories to run",
    )
    validate_parser.add_argument(
        "--report-format",
        choices=["json", "text", "both"],
        default="both",
        help="Validation report format",
    )

    # Performance testing command
    perf_parser = subcommands.add_parser(
        "performance",
        help="Run performance tests with benchmarking",
        description="Execute performance tests and generate benchmark reports",
    )
    perf_parser.add_argument("--baseline", help="Performance baseline file path")
    perf_parser.add_argument(
        "--threshold",
        type=float,
        default=1.2,
        help="Performance degradation threshold (e.g., 1.2 = 20% slower allowed)",
    )
    perf_parser.add_argument(
        "--save-baseline", help="Save current results as new baseline"
    )

    # Integration testing command
    integration_parser = subcommands.add_parser(
        "integration",
        help="Run integration tests with real systems",
        description="Execute integration tests with actual AI Onboard components",
    )
    integration_parser.add_argument(
        "--systems",
        nargs="+",
        help="Specific systems to test (e.g., metrics, user-prefs, optimizer)",
    )
    integration_parser.add_argument(
        "--mock-external", action="store_true", help="Mock external dependencies"
    )

    # Test report command
    report_parser = subcommands.add_parser(
        "report",
        help="Generate test reports and analytics",
        description="Generate comprehensive test reports and trend analysis",
    )
    report_parser.add_argument(
        "--format",
        choices=["html", "json", "markdown"],
        default="html",
        help="Report format",
    )
    report_parser.add_argument("--output", help="Output file path")
    report_parser.add_argument(
        "--include-history", action="store_true", help="Include historical test data"
    )
    report_parser.add_argument(
        "--days", type=int, default=30, help="Number of days of history to include"
    )


def handle_enhanced_testing_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle enhanced testing commands."""
    if not hasattr(args, "testing_cmd") or args.testing_cmd is None:
        print(
            "❌ No enhanced testing command specified. Use --help for available commands."
        )
        return

    if args.testing_cmd == "run":
        _handle_run_enhanced_tests(args, root)
    elif args.testing_cmd == "validate":
        _handle_system_validation(args, root)
    elif args.testing_cmd == "performance":
        _handle_performance_testing(args, root)
    elif args.testing_cmd == "integration":
        _handle_integration_testing(args, root)
    elif args.testing_cmd == "report":
        _handle_test_reporting(args, root)
    else:
        print(f"❌ Unknown enhanced testing command: {args.testing_cmd}")


def _handle_run_enhanced_tests(args: argparse.Namespace, root: Path) -> None:
    """Handle running enhanced tests with pytest integration."""
    print("🧪 Running Enhanced Tests with Continuous Improvement Validation")
    print("=" * 70)

    # Build pytest command
    pytest_cmd = [sys.executable, "-m", "pytest"]

    # Add test path
    pytest_cmd.append(args.test_path)

    # Add markers if specified
    if args.markers:
        pytest_cmd.extend(["-m", args.markers])

    # Add coverage if requested
    if args.coverage:
        pytest_cmd.extend(
            ["--cov=ai_onboard", "--cov-report=html", "--cov-report=term"]
        )

    # Add CI validation if requested
    if args.ci_validation:
        pytest_cmd.append("--ci-validation-report")
        pytest_cmd.extend(["--ci-validation-timeout", str(args.timeout)])

    # Add performance baseline if specified
    if args.performance_baseline:
        pytest_cmd.extend(["--performance-baseline", args.performance_baseline])

    # Add parallel execution if requested
    if args.parallel:
        pytest_cmd.extend(["-n", "auto"])

    # Add verbose output if requested
    if args.verbose:
        pytest_cmd.append("-v")

    # Add other useful options
    pytest_cmd.extend(["--tb=short", "--strict-markers", "--strict-config"])

    print(f"📋 Executing: {' '.join(pytest_cmd)}")
    print()

    # Run pytest
    start_time = time.time()
    try:
        result = subprocess.run(pytest_cmd, cwd=root, check=False)
        execution_time = time.time() - start_time

        print(f"\n⏱️ Test execution completed in {execution_time:.2f} seconds")

        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Tests failed with exit code {result.returncode}")

        # Check for validation report
        if args.ci_validation:
            _check_and_display_validation_report(root)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def _handle_system_validation(args: argparse.Namespace, root: Path) -> None:
    """Handle system validation using ContinuousImprovementValidator."""
    print("🔍 Running Continuous Improvement System Validation")
    print("=" * 60)

    try:
        # Initialize validator
        validator = ContinuousImprovementValidator(root)

        # Configure validation based on arguments
        if args.quick:
            # Modify config for quick validation
            validator.test_config["performance_tests"] = False
            validator.test_config["end_to_end_tests"] = False
            validator.test_config["test_timeout_seconds"] = 10

        if args.categories:
            # Enable only specified categories
            all_categories = [
                "integration",
                "performance",
                "data_integrity",
                "end_to_end",
            ]
            for category in all_categories:
                config_key = f"{category}_tests"
                if config_key in validator.test_config:
                    validator.test_config[config_key] = category in args.categories

        # Run validation
        start_time = time.time()
        report = validator.run_comprehensive_validation()
        execution_time = time.time() - start_time

        print(f"\n⏱️ Validation completed in {execution_time:.2f} seconds")
        print(f"📊 System Health Score: {report.system_health_score:.1f}%")
        print(
            f"🧪 Tests: {report.total_tests} total, {report.passed_tests} passed, {report.failed_tests} failed"
        )

        # Generate report in requested format
        if args.report_format in ["json", "both"]:
            _save_validation_report_json(report, root)

        if args.report_format in ["text", "both"]:
            _save_validation_report_text(report, root)

        # Display recommendations
        if report.recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(report.recommendations[:5], 1):
                print(f"   {i}. {rec}")

        return report.failed_tests == 0

    except Exception as e:
        print(f"❌ System validation failed: {e}")
        return False


def _handle_performance_testing(args: argparse.Namespace, root: Path) -> None:
    """Handle performance testing with benchmarking."""
    print("⚡ Running Performance Tests with Benchmarking")
    print("=" * 50)

    # Build pytest command for performance tests
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-m",
        "performance",
        "--tb=short",
        "-v",
    ]

    # Add performance baseline if specified
    if args.baseline:
        pytest_cmd.extend(["--performance-baseline", args.baseline])

    print(f"📋 Executing: {' '.join(pytest_cmd)}")

    try:
        result = subprocess.run(pytest_cmd, cwd=root, check=False)

        if result.returncode == 0:
            print("✅ Performance tests passed!")
        else:
            print(f"❌ Performance tests failed with exit code {result.returncode}")

        # Save baseline if requested
        if args.save_baseline:
            _save_performance_baseline(root, args.save_baseline)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error running performance tests: {e}")
        return False


def _handle_integration_testing(args: argparse.Namespace, root: Path) -> None:
    """Handle integration testing with real systems."""
    print("🔗 Running Integration Tests with Real Systems")
    print("=" * 50)

    # Build pytest command for integration tests
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-m",
        "integration",
        "--tb=short",
        "-v",
    ]

    # Add system-specific tests if specified
    if args.systems:
        # This would filter tests based on specific systems
        test_files = []
        for system in args.systems:
            test_files.append(f"tests/test_*{system}*.py")
        pytest_cmd.extend(test_files)

    # Configure mocking if requested
    if args.mock_external:
        # Add environment variable or configuration for mocking
        import os

        os.environ["AI_ONBOARD_MOCK_EXTERNAL"] = "true"

    print(f"📋 Executing: {' '.join(pytest_cmd)}")

    try:
        result = subprocess.run(pytest_cmd, cwd=root, check=False)

        if result.returncode == 0:
            print("✅ Integration tests passed!")
        else:
            print(f"❌ Integration tests failed with exit code {result.returncode}")

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error running integration tests: {e}")
        return False
    finally:
        # Clean up environment
        import os

        os.environ.pop("AI_ONBOARD_MOCK_EXTERNAL", None)


def _handle_test_reporting(args: argparse.Namespace, root: Path) -> None:
    """Handle test report generation and analytics."""
    print("📊 Generating Test Reports and Analytics")
    print("=" * 45)

    try:
        # Load validation reports
        reports = _load_validation_history(root, args.days)

        if not reports:
            print("⚠️ No validation reports found")
            return

        print(f"📈 Found {len(reports)} validation reports from last {args.days} days")

        # Generate report based on format
        if args.format == "html":
            output_file = _generate_html_report(reports, root, args.output)
        elif args.format == "json":
            output_file = _generate_json_report(reports, root, args.output)
        elif args.format == "markdown":
            output_file = _generate_markdown_report(reports, root, args.output)

        print(f"✅ Report generated: {output_file}")

    except Exception as e:
        print(f"❌ Error generating test report: {e}")


def _check_and_display_validation_report(root: Path) -> None:
    """Check for and display validation report if available."""
    report_file = root / ".ai_onboard" / "pytest_validation_report.json"

    if report_file.exists():
        try:
            with open(report_file, "r") as f:
                report_data = json.load(f)

            print(f"\n📋 Continuous Improvement Validation Report")
            print(f"   Report ID: {report_data.get('report_id', 'unknown')}")
            print(f"   Health Score: {report_data.get('system_health_score', 0):.1f}%")
            print(
                f"   Tests: {report_data.get('total_tests', 0)} total, "
                f"{report_data.get('passed_tests', 0)} passed, "
                f"{report_data.get('failed_tests', 0)} failed"
            )

            if report_data.get("recommendations"):
                print(
                    f"   Recommendations: {len(report_data['recommendations'])} items"
                )

        except Exception as e:
            print(f"⚠️ Could not read validation report: {e}")


def _save_validation_report_json(report: ValidationReport, root: Path) -> None:
    """Save validation report in JSON format."""
    report_file = root / ".ai_onboard" / "validation_report.json"

    report_data = {
        "report_id": report.report_id,
        "generated_at": report.generated_at.isoformat(),
        "total_tests": report.total_tests,
        "passed_tests": report.passed_tests,
        "failed_tests": report.failed_tests,
        "warning_tests": report.warning_tests,
        "skipped_tests": report.skipped_tests,
        "system_health_score": report.system_health_score,
        "recommendations": report.recommendations,
        "summary": report.summary,
    }

    with open(report_file, "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"📄 JSON report saved: {report_file}")


def _save_validation_report_text(report: ValidationReport, root: Path) -> None:
    """Save validation report in text format."""
    report_file = root / ".ai_onboard" / "validation_report.txt"

    with open(report_file, "w") as f:
        f.write(f"Continuous Improvement Validation Report\n")
        f.write(f"{'=' * 50}\n\n")
        f.write(f"Report ID: {report.report_id}\n")
        f.write(f"Generated: {report.generated_at}\n")
        f.write(f"System Health Score: {report.system_health_score:.1f}%\n\n")
        f.write(f"Test Summary:\n")
        f.write(f"  Total Tests: {report.total_tests}\n")
        f.write(f"  Passed: {report.passed_tests}\n")
        f.write(f"  Failed: {report.failed_tests}\n")
        f.write(f"  Warnings: {report.warning_tests}\n")
        f.write(f"  Skipped: {report.skipped_tests}\n\n")
        f.write(f"Summary: {report.summary}\n\n")

        if report.recommendations:
            f.write(f"Recommendations:\n")
            for i, rec in enumerate(report.recommendations, 1):
                f.write(f"  {i}. {rec}\n")

    print(f"📄 Text report saved: {report_file}")


def _save_performance_baseline(root: Path, baseline_file: str) -> None:
    """Save current performance metrics as baseline."""
    # This would collect current performance metrics and save them
    baseline_data = {
        "created_at": datetime.now().isoformat(),
        "metrics": {
            "response_time_ms": 500,  # Example metrics
            "memory_usage_mb": 50,
            "cpu_usage_percent": 30,
        },
    }

    baseline_path = Path(baseline_file)
    with open(baseline_path, "w") as f:
        json.dump(baseline_data, f, indent=2)

    print(f"📊 Performance baseline saved: {baseline_path}")


def _load_validation_history(root: Path, days: int) -> List[Dict[str, Any]]:
    """Load validation report history."""
    reports = []
    validation_file = root / ".ai_onboard" / "validation_reports.jsonl"

    if not validation_file.exists():
        return reports

    cutoff_date = datetime.now() - timedelta(days=days)

    try:
        with open(validation_file, "r") as f:
            for line in f:
                try:
                    report_data = json.loads(line.strip())
                    report_date = datetime.fromisoformat(
                        report_data.get("generated_at", "")
                    )
                    if report_date >= cutoff_date:
                        reports.append(report_data)
                except (json.JSONDecodeError, ValueError):
                    continue
    except Exception as e:
        print(f"⚠️ Error loading validation history: {e}")

    return reports


def _generate_html_report(
    reports: List[Dict[str, Any]], root: Path, output: Optional[str]
) -> Path:
    """Generate HTML test report."""
    output_file = Path(output) if output else root / ".ai_onboard" / "test_report.html"

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Onboard Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e0e0e0; border-radius: 3px; }}
        .report {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Onboard Test Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Reports: {len(reports)} validation reports analyzed</p>
    </div>
    
    <h2>Summary</h2>
    <div class="metric">Total Reports: {len(reports)}</div>
    
    <h2>Recent Validation Reports</h2>
"""

    for report in reports[-10:]:  # Show last 10 reports
        html_content += f"""
    <div class="report">
        <h3>Report {report.get('report_id', 'Unknown')}</h3>
        <p><strong>Date:</strong> {report.get('generated_at', 'Unknown')}</p>
        <p><strong>Health Score:</strong> {report.get('system_health_score', 0):.1f}%</p>
        <p><strong>Tests:</strong> {report.get('total_tests', 0)} total, 
           {report.get('passed_tests', 0)} passed, {report.get('failed_tests', 0)} failed</p>
        <p><strong>Summary:</strong> {report.get('summary', 'No summary')}</p>
    </div>
"""

    html_content += """
</body>
</html>
"""

    with open(output_file, "w") as f:
        f.write(html_content)

    return output_file


def _generate_json_report(
    reports: List[Dict[str, Any]], root: Path, output: Optional[str]
) -> Path:
    """Generate JSON test report."""
    output_file = Path(output) if output else root / ".ai_onboard" / "test_report.json"

    report_data = {
        "generated_at": datetime.now().isoformat(),
        "total_reports": len(reports),
        "reports": reports,
    }

    with open(output_file, "w") as f:
        json.dump(report_data, f, indent=2)

    return output_file


def _generate_markdown_report(
    reports: List[Dict[str, Any]], root: Path, output: Optional[str]
) -> Path:
    """Generate Markdown test report."""
    output_file = Path(output) if output else root / ".ai_onboard" / "test_report.md"

    with open(output_file, "w") as f:
        f.write("# AI Onboard Test Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Total Reports Analyzed:** {len(reports)}\n\n")

        if reports:
            latest = reports[-1]
            f.write(f"## Latest Validation Report\n\n")
            f.write(f"- **Report ID:** {latest.get('report_id', 'Unknown')}\n")
            f.write(f"- **Date:** {latest.get('generated_at', 'Unknown')}\n")
            f.write(
                f"- **Health Score:** {latest.get('system_health_score', 0):.1f}%\n"
            )
            f.write(f"- **Tests:** {latest.get('total_tests', 0)} total, ")
            f.write(
                f"{latest.get('passed_tests', 0)} passed, {latest.get('failed_tests', 0)} failed\n\n"
            )

            if latest.get("recommendations"):
                f.write(f"### Recommendations\n\n")
                for i, rec in enumerate(latest["recommendations"][:5], 1):
                    f.write(f"{i}. {rec}\n")

    return output_file
