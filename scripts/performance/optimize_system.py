#!/usr/bin/env python3
"""
System Performance Optimization Script

Analyzes system performance and identifies optimization opportunities.
Provides recommendations for improving response times and resource usage.
"""

import gc
import time
from pathlib import Path
from typing import Any, Dict, List

from ai_onboard.core.ai_integration.system_integrator import get_system_integrator


def analyze_performance_bottlenecks() -> Dict[str, Any]:
    """Analyze system performance and identify bottlenecks."""
    print("🔍 Analyzing system performance...")

    # Initialize system
    integrator = get_system_integrator(Path.cwd())

    # Test various operation types
    operation_types = [
        ("simple", {"data": "simple"}),
        ("medium", {"files": ["file1.py", "file2.py"]}),
        ("complex", {"files": ["file1.py"] * 20, "dependencies": ["dep1"] * 10}),
    ]

    results = {}

    for op_name, context in operation_types:
        print(f"   Testing {op_name} operations...")

        # Ensure context is properly typed as Dict[str, Any]
        typed_context: Dict[str, Any] = context  # type: ignore

        # Warm up
        for _ in range(5):
            integrator.process_agent_operation(
                "warmup_agent", f"{op_name}_warmup", typed_context
            )

        # Measure performance
        times = []
        for i in range(20):
            start_time = time.time()
            result = integrator.process_agent_operation(
                "benchmark_agent", f"{op_name}_op_{i}", typed_context
            )
            duration = time.time() - start_time
            times.append(duration)

        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)

        results[op_name] = {
            "avg_time": avg_time,
            "max_time": max_time,
            "min_time": min_time,
            "operations_per_second": 1.0 / avg_time if avg_time > 0 else float("inf"),
        }

        avg_ms = avg_time * 1000
        max_ms = max_time * 1000
        print(f"     Avg: {avg_ms:.1f}ms, Max: {max_ms:.1f}ms")

    return results


def check_memory_usage() -> Dict[str, Any]:
    """Check system memory usage patterns."""
    print("🧠 Analyzing memory usage...")

    import os

    import psutil

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Create integrator and run some operations
    integrator = get_system_integrator(Path.cwd())

    # Run memory-intensive operations
    for i in range(100):
        large_context = {
            "data": "x" * 10000,  # 10KB per operation
            "metadata": {f"key_{j}": f"value_{j}" for j in range(20)},
        }

        integrator.process_agent_operation(
            f"memory_agent_{i}", "memory_test_operation", large_context  # type: ignore
        )

    # Force garbage collection
    gc.collect()

    final_memory = process.memory_info().rss / 1024 / 1024
    memory_growth = final_memory - initial_memory

    return {
        "initial_memory_mb": initial_memory,
        "final_memory_mb": final_memory,
        "memory_growth_mb": memory_growth,
        "memory_efficient": memory_growth < 50,  # Less than 50MB growth
    }


def analyze_concurrent_performance() -> Dict[int, Any]:
    """Analyze performance under concurrent load."""
    print("⚡ Testing concurrent performance...")

    from concurrent.futures import ThreadPoolExecutor

    integrator = get_system_integrator(Path.cwd())

    def run_agent_operations(agent_id: str, operation_count: int) -> List[float]:
        """Run operations for a single agent."""
        times = []
        context = {"agent_id": agent_id, "op_num": 0}  # type: ignore
        for i in range(operation_count):
            start_time = time.time()
            context["op_num"] = i  # Update operation number
            integrator.process_agent_operation(agent_id, f"concurrent_op_{i}", context)
            duration = time.time() - start_time
            times.append(duration)
        return times

    # Test with increasing concurrency
    results = {}
    for agent_count in [1, 5, 10]:
        print(f"   Testing {agent_count} concurrent agents...")

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=agent_count) as executor:
            futures = [
                executor.submit(run_agent_operations, f"agent_{i}", 20)
                for i in range(agent_count)
            ]

            all_times = []
            for future in futures:
                agent_times = future.result()
                all_times.extend(agent_times)

        total_time = time.time() - start_time
        ops_per_second = (agent_count * 20) / total_time
        avg_time = sum(all_times) / len(all_times)

        results[agent_count] = {
            "total_operations": agent_count * 20,
            "total_time": total_time,
            "operations_per_second": ops_per_second,
            "avg_operation_time": avg_time,
        }

        avg_ms = avg_time * 1000
        print(f"     {ops_per_second:.1f} ops/sec, avg {avg_ms:.1f}ms per operation")

    return results


def generate_optimization_recommendations(
    performance_data: Dict[str, Any],
) -> List[str]:
    """Generate optimization recommendations based on performance analysis."""
    recommendations = []

    # Check operation performance
    if "simple" in performance_data:
        simple_perf = performance_data["simple"]
        if simple_perf["avg_time"] > 0.1:  # Slower than 100ms
            recommendations.append(
                "Consider optimizing simple operations - currently >100ms average"
            )

    # Check memory usage
    memory_data = performance_data.get("memory_usage", {})
    if memory_data.get("memory_growth_mb", 0) > 100:
        recommendations.append(
            "High memory growth detected - consider implementing object pooling or caching limits"
        )

    # Check concurrent performance
    concurrent_data = performance_data.get("concurrent", {})
    if 10 in concurrent_data:
        ten_agent_perf = concurrent_data[10]
        if ten_agent_perf["operations_per_second"] < 5:
            recommendations.append(
                "Concurrent performance could be improved - consider async optimization"
            )

    # General recommendations
    recommendations.extend(
        [
            "Monitor system performance regularly to catch regressions",
            "Consider implementing operation result caching for repeated similar requests",
            "Profile individual system components to identify specific bottlenecks",
            "Implement background task throttling to reduce resource contention",
        ]
    )

    return recommendations


def main():
    """Main performance analysis and optimization function."""
    print("🚀 AI Onboard Performance Analysis & Optimization")
    print("=" * 60)

    # Analyze performance
    performance_data = {}

    # Test basic performance
    performance_data["operations"] = analyze_performance_bottlenecks()

    # Check memory usage
    performance_data["memory_usage"] = check_memory_usage()

    # Test concurrent performance
    performance_data["concurrent"] = analyze_concurrent_performance()

    print("\n📊 Performance Summary:")
    print("-" * 40)

    # Display results
    if "operations" in performance_data:
        print("Operation Performance:")
        for op_type, data in performance_data["operations"].items():
            ops_per_sec = data["operations_per_second"]
        print(f"  {op_type.capitalize()}: {ops_per_sec:.1f} ops/sec")

    if "memory_usage" in performance_data:
        mem = performance_data["memory_usage"]
        print("\nMemory Usage:")
        growth_mb = mem["memory_growth_mb"]
        print(f"  Growth: {growth_mb:.1f}MB")
        print(f"  Efficient: {'✅' if mem['memory_efficient'] else '❌'}")

    if "concurrent" in performance_data:
        print("\nConcurrent Performance:")
        for agents, data in performance_data["concurrent"].items():
            ops_per_sec = data["operations_per_second"]
            print(f"  {agents} agents: {ops_per_sec:.1f} ops/sec")

    # Generate recommendations
    recommendations = generate_optimization_recommendations(performance_data)

    print("\n💡 Optimization Recommendations:")
    print("-" * 40)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")

    print(
        f"\n✅ Performance analysis complete - {len(recommendations)} recommendations generated"
    )


if __name__ == "__main__":
    main()
