#!/usr/bin/env python3
"""
Performance Test Runner for AI Onboard System

Runs comprehensive performance tests including load testing with Locust
and performance regression testing with pytest-benchmark.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


class PerformanceTestRunner:
    """Comprehensive performance test runner."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results_dir = project_root / "performance_results"
        self.results_dir.mkdir(exist_ok=True)

    def run_load_tests(
        self,
        users: int = 10,
        spawn_rate: float = 2.0,
        duration: int = 60,
        host: str = "http://localhost:8080",
    ) -> Dict[str, Any]:
        """Run Locust load tests."""
        print(
            f"🚀 Starting load tests: {users} users, {spawn_rate} spawn rate, {duration}s duration"
        )

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"load_test_{timestamp}.json"

        # Run locust in headless mode
        cmd = [
            sys.executable,
            "-m",
            "locust",
            "--locustfile",
            str(self.project_root / "tests" / "performance" / "locustfile.py"),
            "--host",
            host,
            "--users",
            str(users),
            "--spawn-rate",
            str(spawn_rate),
            "--run-time",
            f"{duration}s",
            "--headless",
            "--json",
            str(results_file),
            "--loglevel",
            "INFO",
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode == 0:
                print("✅ Load tests completed successfully")

                # Load and return results
                if results_file.exists():
                    with open(results_file, "r") as f:
                        return json.load(f)
                else:
                    return {"status": "completed", "error": "No results file generated"}
            else:
                print(f"❌ Load tests failed: {result.stderr}")
                return {"status": "failed", "error": result.stderr}

        except Exception as e:
            print(f"❌ Load test execution failed: {e}")
            return {"status": "error", "error": str(e)}

    def run_regression_tests(self, save_baseline: bool = False) -> Dict[str, Any]:
        """Run performance regression tests using pytest-benchmark."""
        print("📊 Running performance regression tests")

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"regression_test_{timestamp}.json"

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/performance/test_performance_regression.py",
            "--benchmark-json",
            str(results_file),
            "--benchmark-save=latest",
            "--benchmark-compare",
            "-v",
            "--tb=short",
        ]

        if save_baseline:
            cmd.extend(["--benchmark-save=baseline"])

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode == 0:
                print("✅ Regression tests completed successfully")
            else:
                print(f"⚠️  Regression tests completed with warnings: {result.stdout}")

            # Load and return results
            if results_file.exists():
                with open(results_file, "r") as f:
                    return json.load(f)
            else:
                return {"status": "completed", "error": "No benchmark results"}

        except Exception as e:
            print(f"❌ Regression test execution failed: {e}")
            return {"status": "error", "error": str(e)}

    def generate_performance_report(
        self, load_results: Dict[str, Any], regression_results: Dict[str, Any]
    ) -> str:
        """Generate comprehensive performance report."""
        report = []
        report.append("# AI Onboard Performance Test Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Load Test Results
        report.append("## Load Testing Results")
        if load_results.get("status") == "completed":
            stats = load_results.get("stats", {})
            report.append("✅ Load tests completed successfully")
            report.append(f"- Total Requests: {stats.get('num_requests', 0)}")
            report.append(
                f"- Average Response Time: {stats.get('avg_response_time', 0):.2f}ms"
            )
            report.append(f"- Requests per Second: {stats.get('total_rps', 0):.2f}")
            report.append(f"- Error Rate: {stats.get('fail_ratio', 0)*100:.2f}%")
        else:
            report.append("❌ Load tests failed or incomplete")
        report.append("")

        # Regression Test Results
        report.append("## Performance Regression Results")
        if "benchmarks" in regression_results:
            benchmarks = regression_results["benchmarks"]
            report.append(f"Total Benchmarks: {len(benchmarks)}")

            for benchmark in benchmarks:
                name = benchmark.get("name", "Unknown")
                median = benchmark.get("stats", {}).get("median", 0)
                change = benchmark.get("stats", {}).get("change", 0)

                status = "➡️"
                if change < -0.1:  # 10% improvement
                    status = "📈 IMPROVED"
                elif change > 0.1:  # 10% regression
                    status = "📉 REGRESSED"

                report.append(f"- {name}: {median:.4f}s {status}")
        else:
            report.append("No regression test results available")

        report.append("")
        report.append("## Recommendations")
        report.append("")

        # Analyze results and provide recommendations
        if load_results.get("status") == "completed":
            stats = load_results.get("stats", {})
            rps = stats.get("total_rps", 0)
            error_rate = stats.get("fail_ratio", 0)

            if rps < 10:
                report.append("- Consider optimizing slow operations")
            if error_rate > 0.05:  # 5% error rate
                report.append("- Investigate high error rates in load tests")
            if rps > 50:
                report.append("- Excellent performance under load!")

        report.append("")
        report.append("---")
        report.append("Performance tests completed.")

        return "\n".join(report)

    def save_report(self, report_content: str) -> Path:
        """Save performance report to file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = self.results_dir / f"performance_report_{timestamp}.md"

        with open(report_file, "w") as f:
            f.write(report_content)

        print(f"📄 Report saved to: {report_file}")
        return report_file


def main():
    """Main entry point for performance testing."""
    parser = argparse.ArgumentParser(description="AI Onboard Performance Test Runner")
    parser.add_argument(
        "--users",
        type=int,
        default=10,
        help="Number of concurrent users for load testing",
    )
    parser.add_argument(
        "--spawn-rate", type=float, default=2.0, help="User spawn rate for load testing"
    )
    parser.add_argument(
        "--duration", type=int, default=60, help="Test duration in seconds"
    )
    parser.add_argument(
        "--host", default="http://localhost:8080", help="Target host for load testing"
    )
    parser.add_argument(
        "--save-baseline",
        action="store_true",
        help="Save current results as performance baseline",
    )
    parser.add_argument(
        "--skip-load-tests", action="store_true", help="Skip load testing"
    )
    parser.add_argument(
        "--skip-regression-tests", action="store_true", help="Skip regression testing"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    runner = PerformanceTestRunner(project_root)

    print("🏃‍♂️ AI Onboard Performance Test Suite")
    print("=" * 50)

    load_results = {}
    regression_results = {}

    # Run load tests
    if not args.skip_load_tests:
        load_results = runner.run_load_tests(
            users=args.users,
            spawn_rate=args.spawn_rate,
            duration=args.duration,
            host=args.host,
        )
        print()

    # Run regression tests
    if not args.skip_regression_tests:
        regression_results = runner.run_regression_tests(
            save_baseline=args.save_baseline
        )
        print()

    # Generate and save report
    report = runner.generate_performance_report(load_results, regression_results)
    report_file = runner.save_report(report)

    print("\n📊 Performance Testing Summary:")
    print("-" * 30)
    print(report)

    # Exit with appropriate code
    load_success = load_results.get("status") in ["completed", None]
    regression_success = (
        "benchmarks" in regression_results or args.skip_regression_tests
    )

    if load_success and regression_success:
        print("\n✅ All performance tests completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Some performance tests had issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
