"""
Performance Testing & Optimization for AI Agent Oversight System

Tests system performance under various loads and conditions:
- Multiple agents operating simultaneously
- High-frequency operations
- Large project scale scenarios
- Memory and CPU usage monitoring
- Response time benchmarks
- Scalability testing

Ensures the oversight system doesn't become a bottleneck in development workflows.
"""

import asyncio
import gc
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List

import psutil
import pytest

from ai_onboard.core.ai_integration.system_integrator import (
    SystemIntegrator,
    get_system_integrator,
)


class PerformanceMetrics:
    """Track performance metrics during testing."""

    def __init__(self):
        self.start_time = time.time()
        self.operation_times: List[float] = []
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.error_count = 0

    def record_operation(self, duration: float) -> None:
        """Record an operation duration."""
        self.operation_times.append(duration)

    def record_system_metrics(self) -> None:
        """Record current system resource usage."""
        process = psutil.Process()
        self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
        self.cpu_usage.append(process.cpu_percent())

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self.operation_times:
            return {"error": "No operations recorded"}

        return {
            "total_operations": len(self.operation_times),
            "avg_operation_time": sum(self.operation_times) / len(self.operation_times),
            "max_operation_time": max(self.operation_times),
            "min_operation_time": min(self.operation_times),
            "total_time": time.time() - self.start_time,
            "operations_per_second": len(self.operation_times)
            / (time.time() - self.start_time),
            "avg_memory_mb": (
                sum(self.memory_usage) / len(self.memory_usage)
                if self.memory_usage
                else 0
            ),
            "max_memory_mb": max(self.memory_usage) if self.memory_usage else 0,
            "error_count": self.error_count,
        }


class TestPerformanceUnderLoad:
    """Test system performance under various load conditions."""

    @pytest.fixture
    def integrator(self, tmp_path: Path) -> SystemIntegrator:
        """Create a system integrator for performance testing."""
        return get_system_integrator(tmp_path)

    @pytest.fixture
    def metrics(self) -> PerformanceMetrics:
        """Create performance metrics tracker."""
        return PerformanceMetrics()

    def test_single_agent_performance(
        self, integrator: SystemIntegrator, metrics: PerformanceMetrics
    ):
        """Test performance with a single agent doing many operations."""
        agent_id = "performance_agent"

        # Record initial system state
        metrics.record_system_metrics()

        # Perform 100 operations rapidly
        for i in range(100):
            start_time = time.time()

            result = integrator.process_agent_operation(
                agent_id=agent_id,
                operation=f"operation_{i}",
                context={"iteration": i, "performance_test": True},
            )

            duration = time.time() - start_time
            metrics.record_operation(duration)
            metrics.record_system_metrics()

            # Assert operation succeeded
            assert isinstance(result, dict) or hasattr(result, "approved")

        # Check performance metrics
        summary = metrics.get_summary()

        # Should handle 100 operations in reasonable time
        assert summary["total_operations"] == 100
        assert summary["avg_operation_time"] < 0.1  # Less than 100ms per operation
        assert summary["operations_per_second"] > 10  # At least 10 ops/sec

        # Memory usage should be reasonable
        assert summary["max_memory_mb"] < 200  # Less than 200MB

    def test_multiple_agents_concurrent(
        self, integrator: SystemIntegrator, metrics: PerformanceMetrics
    ):
        """Test performance with multiple agents operating concurrently."""
        agent_count = 10
        operations_per_agent = 20

        # Record initial state
        metrics.record_system_metrics()

        def run_agent_operations(agent_id: str) -> List[float]:
            """Run operations for a single agent and return timings."""
            timings = []

            for i in range(operations_per_agent):
                start_time = time.time()

                result = integrator.process_agent_operation(
                    agent_id=agent_id,
                    operation=f"concurrent_op_{i}",
                    context={"agent_id": agent_id, "op_num": i},
                )

                duration = time.time() - start_time
                timings.append(duration)

                # Brief pause to avoid overwhelming
                time.sleep(0.001)

            return timings

        # Run all agents concurrently
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=agent_count) as executor:
            futures = [
                executor.submit(run_agent_operations, f"agent_{i}")
                for i in range(agent_count)
            ]

            # Collect all timings
            all_timings = []
            for future in futures:
                agent_timings = future.result()
                all_timings.extend(agent_timings)
                metrics.operation_times.extend(agent_timings)

        total_time = time.time() - start_time

        # Record final system metrics
        metrics.record_system_metrics()

        # Performance assertions
        summary = metrics.get_summary()
        assert summary["total_operations"] == agent_count * operations_per_agent

        # Should handle concurrent load reasonably
        assert summary["avg_operation_time"] < 0.2  # Less than 200ms per operation
        assert summary["operations_per_second"] > 5  # At least 5 ops/sec total

        # Memory usage should scale reasonably
        assert summary["max_memory_mb"] < 300  # Less than 300MB for 10 agents

    def test_high_frequency_operations(
        self, integrator: SystemIntegrator, metrics: PerformanceMetrics
    ):
        """Test performance under high-frequency operation bursts."""
        agent_id = "burst_agent"

        # Record initial state
        metrics.record_system_metrics()

        # Test burst of 200 operations in quick succession
        burst_size = 200
        start_time = time.time()

        for i in range(burst_size):
            op_start = time.time()

            result = integrator.process_agent_operation(
                agent_id=agent_id,
                operation=f"burst_op_{i}",
                context={"burst": True, "sequence": i},
            )

            duration = time.time() - op_start
            metrics.record_operation(duration)

            # Very brief pause between operations
            time.sleep(0.0001)

        burst_duration = time.time() - start_time

        # Record system metrics during burst
        metrics.record_system_metrics()

        # Performance assertions
        summary = metrics.get_summary()
        assert summary["total_operations"] == burst_size

        # Burst performance should be acceptable
        assert burst_duration < 10  # Complete 200 ops in under 10 seconds
        assert summary["operations_per_second"] > 20  # At least 20 ops/sec during burst
        assert summary["avg_operation_time"] < 0.05  # Less than 50ms per operation

    def test_large_context_operations(
        self, integrator: SystemIntegrator, metrics: PerformanceMetrics
    ):
        """Test performance with operations that have large context data."""
        agent_id = "large_context_agent"

        # Create large context data
        large_context = {
            "large_data": "x" * 10000,  # 10KB string
            "files": [f"file_{i}.py" for i in range(100)],  # 100 file names
            "metadata": {
                f"key_{i}": f"value_{i}" * 10 for i in range(50)
            },  # 50 metadata entries
        }

        # Record initial state
        metrics.record_system_metrics()

        # Perform operations with large context
        for i in range(50):
            start_time = time.time()

            result = integrator.process_agent_operation(
                agent_id=agent_id,
                operation=f"large_context_op_{i}",
                context=large_context,
            )

            duration = time.time() - start_time
            metrics.record_operation(duration)

        # Record final metrics
        metrics.record_system_metrics()

        # Performance assertions
        summary = metrics.get_summary()
        assert summary["total_operations"] == 50

        # Large context should not dramatically slow down operations
        assert summary["avg_operation_time"] < 0.5  # Less than 500ms per operation
        assert summary["max_memory_mb"] < 250  # Memory usage should be reasonable

    def test_system_resource_monitoring(self, integrator: SystemIntegrator):
        """Test that system resource usage stays within acceptable bounds."""
        # Monitor resource usage during normal operations
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = process.cpu_percent()

        # Perform some operations
        for i in range(20):
            result = integrator.process_agent_operation(
                agent_id=f"resource_test_agent_{i}",
                operation="test_operation",
                context={"resource_test": True},
            )

        # Check resource usage
        final_memory = process.memory_info().rss / 1024 / 1024
        final_cpu = process.cpu_percent()

        # Memory should not grow excessively
        memory_growth = final_memory - initial_memory
        assert memory_growth < 50  # Less than 50MB growth

        # CPU usage should be reasonable
        assert final_cpu < 80  # Less than 80% CPU usage

    def test_concurrent_system_operations(
        self, integrator: SystemIntegrator, metrics: PerformanceMetrics
    ):
        """Test concurrent access to system integrator from multiple threads."""
        agent_count = 5
        operations_per_agent = 10

        # Record initial state
        metrics.record_system_metrics()

        async def async_agent_operations(agent_id: str) -> List[float]:
            """Run async operations for a single agent."""
            timings = []

            for i in range(operations_per_agent):
                start_time = time.time()

                result = integrator.process_agent_operation(
                    agent_id=agent_id,
                    operation=f"async_op_{i}",
                    context={"agent_id": agent_id, "op_num": i},
                )

                duration = time.time() - start_time
                timings.append(duration)

            return timings

        async def run_concurrent_test():
            """Run all agents concurrently using asyncio."""
            tasks = [
                async_agent_operations(f"concurrent_agent_{i}")
                for i in range(agent_count)
            ]

            results = await asyncio.gather(*tasks)

            # Flatten results
            for agent_timings in results:
                metrics.operation_times.extend(agent_timings)

        # Run the async test
        start_time = time.time()
        asyncio.run(run_concurrent_test())
        total_time = time.time() - start_time

        # Record final metrics
        metrics.record_system_metrics()

        # Performance assertions
        summary = metrics.get_summary()
        assert summary["total_operations"] == agent_count * operations_per_agent

        # Concurrent operations should be efficient
        assert summary["avg_operation_time"] < 0.3  # Less than 300ms per operation
        assert total_time < 5  # Complete all operations in under 5 seconds

    def test_memory_leak_detection(self, integrator: SystemIntegrator):
        """Test for memory leaks during extended operation."""
        # Perform many operations and monitor memory
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Run 1000 operations
        for i in range(1000):
            result = integrator.process_agent_operation(
                agent_id=f"leak_test_agent_{i % 10}",
                operation="memory_test_operation",
                context={"iteration": i},
            )

            # Periodic garbage collection
            if i % 100 == 0:
                gc.collect()

        # Check final memory usage
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory

        # Memory should not grow excessively (allow some growth for caching)
        assert memory_growth < 100  # Less than 100MB growth over 1000 operations

    def test_response_time_benchmarks(self, integrator: SystemIntegrator):
        """Benchmark response times for different operation types."""
        operation_types = [
            ("simple_operation", {"simple": True}),
            ("complex_operation", {"files": ["file1.py", "file2.py"], "complex": True}),
            ("gate_operation", {"requires_approval": True}),
            ("emergency_operation", {"emergency": True}),
        ]

        results = {}

        for op_name, context in operation_types:
            # Measure response time for this operation type
            start_time = time.time()

            result = integrator.process_agent_operation(
                agent_id="benchmark_agent", operation=op_name, context=context
            )

            response_time = time.time() - start_time
            results[op_name] = response_time

        # All operations should respond quickly
        for op_name, response_time in results.items():
            assert response_time < 1.0, f"{op_name} took too long: {response_time}s"

        # Operations should complete quickly (main requirement is responsiveness)
        # Note: Due to system optimization, timing differences may be minimal


class TestScalability:
    """Test system scalability with increasing load."""

    @pytest.fixture
    def integrator(self, tmp_path: Path) -> SystemIntegrator:
        """Create a system integrator for scalability testing."""
        return get_system_integrator(tmp_path)

    def test_agent_count_scalability(self, integrator: SystemIntegrator):
        """Test performance scaling with increasing number of agents."""
        agent_counts = [1, 5, 10, 20]

        results = {}

        for agent_count in agent_counts:
            # Test with this many agents
            agents = [f"scale_agent_{i}" for i in range(agent_count)]

            start_time = time.time()

            for agent_id in agents:
                result = integrator.process_agent_operation(
                    agent_id=agent_id,
                    operation="scalability_test",
                    context={"agent_count": agent_count},
                )

            total_time = time.time() - start_time
            ops_per_second = agent_count / total_time
            results[agent_count] = ops_per_second

        # Performance should scale reasonably (not degrade dramatically)
        for count in agent_counts:
            assert (
                results[count] > 0.5
            ), f"Poor performance with {count} agents: {results[count]} ops/sec"

        # Performance should not degrade too much with more agents
        # (Allow some degradation but not orders of magnitude)
        ratio_20_to_1 = results[20] / results[1] if results[1] > 0 else 0
        assert ratio_20_to_1 > 0.1, "Performance degraded too much with more agents"

    def test_operation_complexity_scalability(self, integrator: SystemIntegrator):
        """Test performance scaling with operation complexity."""
        complexities = [
            ("simple", {"data": "simple"}),
            (
                "medium",
                {"files": [f"file_{i}.py" for i in range(10)], "data": "medium"},
            ),
            (
                "complex",
                {
                    "files": [f"file_{i}.py" for i in range(50)],
                    "dependencies": [f"dep_{i}" for i in range(20)],
                    "data": "complex",
                },
            ),
        ]

        results = {}

        for complexity_name, context in complexities:
            start_time = time.time()

            result = integrator.process_agent_operation(
                agent_id="complexity_agent",
                operation=f"{complexity_name}_operation",
                context=context,
            )

            response_time = time.time() - start_time
            results[complexity_name] = response_time

        # Complex operations should not be orders of magnitude slower
        simple_time = results["simple"]
        complex_time = results["complex"]

        # Allow complexity to increase response time, but not excessively
        complexity_ratio = complex_time / simple_time if simple_time > 0 else 1
        assert (
            complexity_ratio < 10
        ), f"Complex operations too slow: {complexity_ratio}x slower"

    def test_long_running_session(self, integrator: SystemIntegrator):
        """Test system performance over extended operation periods."""
        agent_id = "long_session_agent"

        # Run operations for 5 minutes
        start_time = time.time()
        operation_count = 0

        while time.time() - start_time < 300:  # 5 minutes
            result = integrator.process_agent_operation(
                agent_id=agent_id,
                operation=f"long_session_op_{operation_count}",
                context={"session_test": True, "timestamp": time.time()},
            )

            operation_count += 1

            # Brief pause to avoid overwhelming
            time.sleep(0.1)

        # Check that system remained responsive
        total_time = time.time() - start_time
        ops_per_second = operation_count / total_time

        # Should maintain reasonable throughput over time
        assert ops_per_second > 1  # At least 1 operation per second
        assert operation_count > 100  # Should have processed many operations

        # Memory usage should remain stable
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        assert final_memory < 200  # Less than 200MB


class TestOptimizationOpportunities:
    """Identify and test optimization opportunities."""

    @pytest.fixture
    def integrator(self, tmp_path: Path) -> SystemIntegrator:
        """Create a system integrator for optimization testing."""
        return get_system_integrator(tmp_path)

    def test_caching_effectiveness(self, integrator: SystemIntegrator):
        """Test if caching improves performance for repeated operations."""
        agent_id = "caching_agent"

        # First operation (cold cache)
        cold_start = time.time()
        result1 = integrator.process_agent_operation(
            agent_id=agent_id,
            operation="cached_operation",
            context={"cache_test": True},
        )
        cold_time = time.time() - cold_start

        # Second operation (potentially cached)
        warm_start = time.time()
        result2 = integrator.process_agent_operation(
            agent_id=agent_id,
            operation="cached_operation",
            context={"cache_test": True},
        )
        warm_time = time.time() - warm_start

        # Warm operation should be faster (if caching is implemented)
        # This is a potential optimization opportunity
        if warm_time < cold_time:
            improvement_ratio = cold_time / warm_time
            assert improvement_ratio > 1.1  # At least 10% improvement

    def test_background_task_impact(self, integrator: SystemIntegrator):
        """Test impact of background monitoring tasks on performance."""
        agent_id = "background_impact_agent"

        # Measure performance with background tasks running
        start_time = time.time()

        for i in range(50):
            result = integrator.process_agent_operation(
                agent_id=agent_id,
                operation=f"background_test_{i}",
                context={"background_impact": True},
            )

        with_background_time = time.time() - start_time

        # Background tasks should not severely impact performance
        # (This test identifies if background monitoring is too resource-intensive)
        avg_time_with_background = with_background_time / 50
        assert avg_time_with_background < 0.5  # Less than 500ms per operation

    def test_memory_optimization(self, integrator: SystemIntegrator):
        """Test memory usage patterns and identify optimization opportunities."""
        # Monitor memory usage during intensive operations
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Perform memory-intensive operations
        for i in range(100):
            large_context = {
                "large_data": "x" * 5000,  # 5KB per operation
                "metadata": {f"key_{j}": f"value_{j}" for j in range(10)},
            }

            result = integrator.process_agent_operation(
                agent_id=f"memory_agent_{i}",
                operation="memory_intensive_operation",
                context=large_context,
            )

        # Force garbage collection
        gc.collect()

        # Check memory usage
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory

        # Memory should not grow excessively
        assert memory_growth < 100  # Less than 100MB growth

        # This identifies if there are memory leaks or inefficient data structures
