# AI Onboard Performance Testing

Comprehensive performance testing suite for the AI Onboard system including load testing and performance regression detection.

## Overview

This performance testing suite includes:

- **Load Testing**: Simulates multiple concurrent users performing AI onboard operations
- **Performance Regression Testing**: Benchmarks critical operations to detect performance degradation
- **Automated Reporting**: Generates comprehensive performance reports and trends

## Components

### Load Testing (Locust)

The `locustfile.py` simulates real-world usage patterns:

- **AIAgentUser**: Simulates AI agents performing code analysis, organization checks, and user interactions
- **ProjectManagerUser**: Simulates project managers coordinating analysis and generating reports

### Performance Regression Testing (pytest-benchmark)

The `test_performance_regression.py` includes benchmarks for:

- Code quality analysis performance
- File organization analysis performance
- Duplicate detection performance
- User experience system operations
- Orchestrator coordination performance
- Memory usage stability

## Running Performance Tests

### Prerequisites

```bash
# Install performance testing dependencies
pip install -e .[test]
```

### Quick Start

```bash
# Run the complete performance test suite
python scripts/performance/run_performance_tests.py

# Run only regression tests
python -m pytest tests/performance/test_performance_regression.py -v

# Run load tests only (requires running API server)
python scripts/performance/run_performance_tests.py --skip-regression-tests
```

### Advanced Options

```bash
# Load testing with custom parameters
python scripts/performance/run_performance_tests.py \
    --users 50 \
    --spawn-rate 5.0 \
    --duration 120 \
    --host http://localhost:8080

# Save current results as performance baseline
python scripts/performance/run_performance_tests.py --save-baseline

# Run only regression tests
python scripts/performance/run_performance_tests.py --skip-load-tests
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
- name: Run Performance Tests
  run: |
    python scripts/performance/run_performance_tests.py \
      --users 20 \
      --duration 30

- name: Archive Performance Results
  uses: actions/upload-artifact@v3
  with:
    name: performance-results
    path: performance_results/
```

## Performance Metrics

### Load Testing Metrics

- **Response Time**: Average time for operations to complete
- **Requests Per Second (RPS)**: System throughput
- **Error Rate**: Percentage of failed requests
- **Concurrent Users**: Number of simultaneous users supported

### Performance Regression Metrics

- **Code Quality Analysis**: Time to analyze Python codebases
- **File Organization**: Time to analyze project structure
- **Duplicate Detection**: Time to find code duplicates
- **User Experience**: Time for UX system operations
- **Memory Usage**: RAM consumption stability

## Interpreting Results

### Load Test Results

```
✅ Load tests completed successfully
- Total Requests: 1,247
- Average Response Time: 245.67ms
- Requests per Second: 20.78
- Error Rate: 0.08%
```

**Good indicators:**
- RPS > 10 for basic operations
- Error rate < 5%
- Response time < 2 seconds for complex operations

### Regression Test Results

```
test_code_quality_analysis_performance
  Median: 0.1234s ± 0.0123s
  Change: -5.67% (improvement)

test_file_organization_analysis_performance
  Median: 0.0891s ± 0.0045s
  Change: +2.34% (minor regression)
```

**Performance thresholds:**
- 🟢 **Improvement**: > 5% faster
- 🟡 **Acceptable**: ±5% change
- 🔴 **Regression**: > 5% slower

## Performance Baselines

Baselines are stored in `tests/performance/baseline.json` and automatically updated when `--save-baseline` is used.

## Troubleshooting

### Common Issues

1. **Locust can't connect to host**
   - Ensure the API server is running
   - Check the `--host` parameter

2. **Memory usage spikes**
   - Reduce concurrent users for memory-constrained environments
   - Check for memory leaks in the code

3. **Inconsistent benchmark results**
   - Run tests multiple times to account for system variability
   - Use `--benchmark-min-rounds=10` for more stable results

### Performance Optimization Tips

1. **Database Operations**: Ensure efficient queries and proper indexing
2. **File I/O**: Minimize disk access, use caching where appropriate
3. **Memory Management**: Avoid loading large files into memory unnecessarily
4. **Algorithm Complexity**: Review O(n²) operations that may not scale

## Architecture

### Test Structure

```
tests/performance/
├── locustfile.py              # Load testing scenarios
├── test_performance_regression.py  # Performance regression tests
├── conftest.py               # Shared test configuration
├── baseline.json            # Performance baselines
└── README.md                # This documentation

scripts/performance/
└── run_performance_tests.py # Test runner and reporting
```

### Key Classes

- **AIAgentUser**: Simulates AI agent interactions
- **ProjectManagerUser**: Simulates project management operations
- **PerformanceTestRunner**: Orchestrates all performance tests
- **conftest.py**: Provides shared fixtures and monitoring

## Contributing

When adding new performance tests:

1. Add realistic test data and scenarios
2. Include appropriate assertions
3. Update documentation
4. Consider performance impact of new tests

## Performance Goals

**Target Performance Metrics:**

- **Code Analysis**: < 500ms for typical projects
- **File Organization**: < 200ms for standard structures
- **Concurrent Users**: Support 50+ simultaneous users
- **Memory Usage**: < 100MB increase during normal operations
- **Error Rate**: < 1% under normal load



