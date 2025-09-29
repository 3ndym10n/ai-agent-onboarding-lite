# CI/CD Configuration Guide

This document outlines the comprehensive CI/CD pipeline for AI-Onboard.

## Workflows Overview

### 1. CI/CD Pipeline (`ci.yml`)
**Triggers:** Push, PR, Manual
- **Environment Validation:** Protected paths, dev env setup
- **Quality Checks:** Pre-commit, Bandit, Safety, Code formatting
- **Smoke Tests:** Basic functionality verification
- **Unit Tests:** Comprehensive unit test suite with coverage
- **Integration Tests:** End-to-end system integration
- **Test Reporting:** Combined results and PR comments

### 2. Performance Testing (`performance.yml`)
**Triggers:** Scheduled (daily), Manual
- **Baseline Benchmarks:** Performance regression detection
- **Load Testing:** Concurrent user simulation
- **Performance Comparison:** Trend analysis and alerts

### 3. Security Scanning (`security.yml`)
**Triggers:** Scheduled (weekly), Push/PR, Manual
- **Vulnerability Scanning:** Safety, Bandit, Semgrep, Trivy
- **Dependency Analysis:** Outdated packages, security issues
- **Automated Reports:** Security posture tracking

### 4. Deployment (`deploy.yml`)
**Triggers:** Release, Manual
- **Staging Deployment:** Pre-production validation
- **Production Deployment:** Full test suite + PyPI publishing
- **Environment-Specific:** Configurable deployment targets

### 5. Test Reporting (`test-reporting.yml`)
**Triggers:** Post-CI workflow runs (CI pipeline), Manual
- **Metrics Collection:** Summarises CI test artifacts for quick review
- **Quality Metrics:** Captures code complexity and maintainability snapshots
- **Dashboard Generation:** Publishes markdown summaries to GitHub Pages
- **Availability:** Artifacts retained for historical comparison

## Test Environments

### Development
- **Python:** 3.11, 3.13
- **Dependencies:** dev, test extras
- **Coverage:** Full coverage reporting
- **Parallel:** Multi-core test execution

### Staging
- **Python:** 3.11
- **Dependencies:** prod extras
- **Testing:** Integration + smoke tests
- **Deployment:** Rolling updates

### Production
- **Python:** 3.11
- **Dependencies:** prod extras
- **Testing:** Full test suite
- **Deployment:** Blue-green strategy

## Quality Gates

### Code Quality
- ✅ Black formatting
- ✅ isort import sorting
- ✅ flake8 linting (88 char limit)
- ✅ mypy type checking
- ✅ pre-commit hooks

### Testing
- ✅ 70+ unit tests (22% coverage)
- ✅ 68 integration tests (29% total coverage)
- ✅ Smoke tests (75% pass rate)
- ✅ Parallel test execution
- ✅ Coverage reporting

### Security
- ✅ Bandit security scanning
- ✅ Safety vulnerability checks
- ✅ Dependency analysis
- ✅ Container security scanning

### Performance
- ✅ Benchmark regression detection
- ✅ Load testing capabilities
- ✅ Performance trend analysis

## Deployment Strategy

### Staging Deployment
1. **Pre-deployment validation**
   - Smoke tests pass
   - Integration tests pass
   - Security scans clean

2. **Rolling deployment**
   - Zero-downtime updates
   - Health checks
   - Rollback capability

### Production Deployment
1. **Full validation**
   - Complete test suite
   - Performance benchmarks
   - Security audit

2. **Blue-green deployment**
   - Traffic switching
   - Monitoring and alerts
   - Automated rollback

## Monitoring & Alerts

### Test Results
- PR comments with test status
- Coverage trend alerts
- Performance regression alerts

### Quality Metrics
- Code complexity monitoring
- Maintainability index tracking
- Security vulnerability alerts

### Deployment Status
- Deployment success/failure notifications
- Performance monitoring
- Error rate tracking

## Configuration Files

- `pyproject.toml`: Python package configuration
- `config/mypy.ini`: Type checking configuration
- `config/pylint.ini`: Code analysis configuration
- `.pre-commit-config.yaml`: Pre-commit hooks
- `requirements.txt`: Core dependencies
- `config/ci/environment.yaml`: CI environment settings

## Manual Triggers

All workflows support manual execution with configurable parameters:

- **CI Pipeline:** Test level selection (smoke/unit/integration/full)
- **Performance:** Duration, concurrency, benchmark-only mode
- **Security:** Full scan or targeted analysis
- **Deployment:** Environment selection (staging/production)

## Integration Points

### GitHub Integration
- **Issues:** Test failure tracking
- **Pull Requests:** Automated review comments
- **Releases:** Automated deployment
- **Pages:** Quality dashboard hosting

### External Services
- **PyPI:** Automated package publishing
- **Docker Hub:** Container image publishing
- **Monitoring:** External monitoring integration

## Maintenance

### Regular Tasks
- **Weekly:** Security scans
- **Daily:** Performance benchmarks
- **On-demand:** Full pipeline execution

### Configuration Updates
- Update Python versions annually
- Review and update security tools quarterly
- Monitor test execution times and optimize

### Troubleshooting
- **Failed tests:** Check CI logs and rerun manually
- **Security alerts:** Immediate investigation and patching
- **Performance regression:** Benchmark comparison and optimization


