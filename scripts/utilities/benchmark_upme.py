#!/usr/bin/env python3
"""
UPME Benchmarking Script

Runs multiple iterations of UPME operations to gather telemetry data
and measure performance characteristics.
"""

import json
import sys
import time
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_onboard.core.unified_project_management import (
    get_unified_project_management_engine,
)


def benchmark_upme_operations(root: Path, iterations: int = 5):
    """
    Benchmark UPME operations and collect timing data.

    Args:
        root: Project root path
        iterations: Number of iterations to run for each operation
    """
    print(f"🔬 Benchmarking UPME operations ({iterations} iterations each)...")

    upme = get_unified_project_management_engine(root)
    results = {
        "benchmark_timestamp": time.time(),
        "iterations": iterations,
        "operations": {},
    }

    operations = [
        ("task_prioritization", lambda: upme.tasks.prioritize_tasks()),
        ("task_completion", lambda: upme.tasks.detect_completions()),
        ("wbs_status", lambda: upme.wbs.get_status()),
        ("progress_analytics", lambda: upme.analytics.get_project_status()),
    ]

    for op_name, op_func in operations:
        print(f"  📊 Benchmarking {op_name}...")
        timings = []

        for i in range(iterations):
            start_time = time.perf_counter()
            try:
                result = op_func()
                end_time = time.perf_counter()
                duration = end_time - start_time
                timings.append(duration)
                print(f"    Iteration {i+1}: {duration:.4f}s")
            except Exception as e:
                print(f"    Iteration {i+1}: ERROR - {e}")
                timings.append(None)

        # Calculate statistics
        valid_timings = [t for t in timings if t is not None]
        if valid_timings:
            avg_time = sum(valid_timings) / len(valid_timings)
            min_time = min(valid_timings)
            max_time = max(valid_timings)

            results["operations"][op_name] = {
                "timings": timings,
                "avg_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "success_rate": len(valid_timings) / iterations,
            }

            print(
                f"    📈 {op_name}: avg={avg_time:.4f}s, min={min_time:.4f}s, max={max_time:.4f}s"
            )
        else:
            results["operations"][op_name] = {
                "timings": timings,
                "success_rate": 0.0,
                "error": "All iterations failed",
            }
            print(f"    ❌ {op_name}: All iterations failed")

    return results


def check_telemetry_logs(root: Path):
    """Check if telemetry data is being recorded."""
    telemetry_files = [
        root / ".ai_onboard" / "tool_usage.jsonl",
        root / ".ai_onboard" / "telemetry.jsonl",
        root / ".ai_onboard" / "learning" / "learning_history.jsonl",
    ]

    print("\n📋 Checking telemetry logs...")
    for file_path in telemetry_files:
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                print(f"  ✅ {file_path.name}: {len(lines)} entries")

                # Check for recent UPME entries
                recent_upme_entries = 0
                for line in lines[-10:]:  # Check last 10 entries
                    try:
                        entry = json.loads(line.strip())
                        if "unified_project_management" in str(entry):
                            recent_upme_entries += 1
                    except:
                        continue

                if recent_upme_entries > 0:
                    print(
                        f"    📊 Found {recent_upme_entries} recent UPME telemetry entries"
                    )
                else:
                    print(f"    ⚠️  No recent UPME telemetry entries found")

            except Exception as e:
                print(f"  ❌ {file_path.name}: Error reading - {e}")
        else:
            print(f"  ⚪ {file_path.name}: Not found")


def main():
    """Main benchmarking function."""
    root = Path.cwd()

    print("🚀 UPME Performance Benchmark")
    print("=" * 50)

    # Run benchmarks
    benchmark_results = benchmark_upme_operations(root, iterations=3)

    # Check telemetry
    check_telemetry_logs(root)

    # Save benchmark results
    benchmark_file = root / ".ai_onboard" / "upme_benchmark.json"
    benchmark_file.parent.mkdir(exist_ok=True)

    with open(benchmark_file, "w", encoding="utf-8") as f:
        json.dump(benchmark_results, f, indent=2)

    print(f"\n💾 Benchmark results saved to: {benchmark_file}")

    # Summary
    print("\n📊 Performance Summary:")
    for op_name, op_data in benchmark_results["operations"].items():
        if "avg_time" in op_data:
            print(
                f"  {op_name}: {op_data['avg_time']:.4f}s avg ({op_data['success_rate']:.1%} success)"
            )
        else:
            print(f"  {op_name}: Failed ({op_data.get('error', 'Unknown error')})")

    print("\n✅ Benchmarking complete!")


if __name__ == "__main__":
    main()

