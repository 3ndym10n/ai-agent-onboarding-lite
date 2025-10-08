# Test Coverage Plan: CURRENT STATUS UNKNOWN → TARGET 80% 🚀

## Current Status

- **Status:** Needs assessment after recent refactoring
- **Last Known:** ~30% coverage (pre-refactoring)
- **Import Issues:** Several test files have import errors that need fixing
- **Structure:** Many modules reorganized, some may have been moved/renamed

## Coverage Gap Analysis

### Zero Coverage Modules (High Priority) - **NEEDS ASSESSMENT**

| Module | Status | Location | Priority |
|--------|--------|----------|----------|
| `policy_engine.py` | ✅ EXISTS | `ai_onboard/core/quality_safety/policy_engine.py` | 🔥 Critical |
| `checkpoints.py` | ✅ EXISTS | `ai_onboard/core/base/checkpoints.py` | 🔥 Critical |
| `runlog.py` | ✅ EXISTS | `ai_onboard/core/base/runlog.py` | 🔴 High |
| `planning.py` | ❌ MISSING | May be distributed across multiple modules | 🔍 Investigate |
| CLI Commands | ~3,000+ | Command interfaces | ⚪ Skip |

### Low Coverage Modules (20-40%) - **NEEDS ASSESSMENT**

| Module | Status | Location | Priority |
|--------|--------|----------|----------|
| `code_quality_analyzer.py` | ✅ EXISTS | `ai_onboard/core/quality_safety/code_quality_analyzer.py` | Medium |
| `file_organization_analyzer.py` | ✅ EXISTS | `ai_onboard/core/monitoring_analytics/file_organization_analyzer.py` | Medium |
| `duplicate_detector.py` | ✅ EXISTS | `ai_onboard/core/quality_safety/duplicate_detector.py` | Medium |
| `risk_assessment_framework.py` | ✅ EXISTS | `ai_onboard/core/quality_safety/risk_assessment_framework.py` | Medium |
| `critical_path_engine.py` | ✅ EXISTS | `ai_onboard/core/project_management/critical_path_engine.py` | High |
| `vision_web_interface.py` | ❌ MISSING | May have been removed/renamed | 🔍 Investigate |

## Target Strategy

### Phase 1: Critical Core Modules (Week 1)

**Goal:** +15% coverage (45% total)
**Target Modules:** 4 critical zero-coverage modules

1. **`planning.py`** - Vision planning system
   - Mock dependencies, test planning logic
   - **Impact:** +4% coverage

2. **`policy_engine.py`** - Policy evaluation engine
   - Test policy loading, evaluation, enforcement
   - **Impact:** +2% coverage

3. **`checkpoints.py`** - Checkpoint management
   - Test save/load, validation, recovery
   - **Impact:** +3% coverage

4. **`runlog.py`** - Run logging system
   - Test logging, retrieval, formatting
   - **Impact:** +1% coverage

### Phase 2: Quality & Analysis Systems (Week 2)

**Goal:** +20% coverage (65% total)
**Target Modules:** 6 medium-impact modules

1. **`code_quality_analyzer.py`** (16% → 80%)
   - Test code analysis, quality metrics, reporting
   - **Impact:** +8% coverage

2. **`file_organization_analyzer.py`** (15% → 80%)
   - Test file analysis, organization detection, recommendations
   - **Impact:** +9% coverage

3. **`duplicate_detector.py`** (15% → 80%)
   - Test duplicate detection, analysis, reporting
   - **Impact:** +9% coverage

### Phase 3: Business Logic Completion (Week 3)

**Goal:** +15% coverage (80% total)
**Target Modules:** Remaining high-value modules

1. **`vision_web_interface.py`** (14% → 70%)
   - Test web server setup, request handling, responses
   - **Impact:** +4% coverage

2. **`risk_assessment_framework.py`** (27% → 80%)
   - Test risk calculation, assessment, mitigation
   - **Impact:** +6% coverage

3. **`critical_path_engine.py`** (9% → 70%)
   - Test path analysis, bottleneck detection, reporting
   - **Impact:** +5% coverage

## Implementation Approach

### Phase 0: Fix Test Infrastructure (Week 0)

**Goal:** Fix import errors and get accurate coverage baseline

- Fix import errors in test files (6+ files with ModuleNotFoundError)
- Update test imports to match current module structure
- Get accurate coverage baseline

### Test Structure (After Fixes)

```text
tests/unit/
├── test_policy_engine.py         # NEW: ai_onboard/core/quality_safety/policy_engine.py
├── test_checkpoints.py           # NEW: ai_onboard/core/base/checkpoints.py
├── test_runlog.py                # NEW: ai_onboard/core/base/runlog.py
├── test_code_quality_analyzer.py # ENHANCE: ai_onboard/core/quality_safety/code_quality_analyzer.py
├── test_file_analyzer.py         # NEW: ai_onboard/core/monitoring_analytics/file_organization_analyzer.py
├── test_duplicate_detector.py    # ENHANCE: ai_onboard/core/quality_safety/duplicate_detector.py
└── test_critical_path.py         # ENHANCE: ai_onboard/core/project_management/critical_path_engine.py

tests/integration/
├── test_risk_assessment.py       # ENHANCE: ai_onboard/core/quality_safety/risk_assessment_framework.py
└── test_planning_integration.py  # NEW: Planning functionality across modules
```text

### Testing Patterns

#### For Zero-Coverage Modules

```python
import pytest
from ai_onboard.core.{module} import {MainClass}

class TestMainClass:
    def test_initialization(self):
        """Test basic initialization."""
        obj = MainClass()
        assert obj is not None

    def test_core_functionality(self):
        """Test primary business logic."""
        # Arrange
        obj = MainClass()

        # Act
        result = obj.core_method(input_data)

        # Assert
        assert result == expected_output

    def test_error_handling(self):
        """Test error conditions."""
        obj = MainClass()

        with pytest.raises(ExpectedException):
            obj.method(invalid_input)
```python

#### For Low-Coverage Modules

```python
# Focus on untested methods
def test_untested_method_one(self):
    """Test method with missing coverage."""

def test_untested_method_two(self):
    """Test another untested method."""

# Add edge cases
def test_edge_case_scenarios(self):
    """Test boundary conditions."""

# Integration scenarios
def test_integration_with_dependencies(self):
    """Test interaction with other components."""
```python

### Coverage Targets by Week

| Week | Target Coverage | Modules Added | Tests Added | Cumulative Impact |
|------|----------------|---------------|-------------|-------------------|
| 0 | Baseline | Fix test infrastructure | ~10 fixes | Stable foundation |
| 1 | 45% | 4 zero-coverage | ~40 tests | +15% |
| 2 | 65% | 3 enhanced + 3 new | ~60 tests | +35% |
| 3 | 80% | 3 enhanced | ~50 tests | +50% |

### Quality Standards

#### Test Quality Checklist

- ✅ **Isolation:** Each test independent, no side effects
- ✅ **Readability:** Clear test names, documentation
- ✅ **Coverage:** Every test covers new lines (avoid redundancy)
- ✅ **Edge Cases:** Boundary conditions, error scenarios
- ✅ **Mocking:** External dependencies properly mocked
- ✅ **Assertions:** Meaningful assertions with clear failure messages

#### Coverage Quality Metrics

- **Line Coverage:** Primary metric (target: 80%)
- **Branch Coverage:** Secondary metric (target: 70%)
- **Function Coverage:** Ensure all public APIs tested
- **Integration Coverage:** Critical user journeys tested

## Success Criteria

### Week 0 Success

- ✅ All test import errors resolved
- ✅ Test suite runs without ModuleNotFoundError
- ✅ Accurate coverage baseline established
- ✅ Test infrastructure stable

### Week 1 Success

- ✅ 4 critical modules have >70% coverage
- ✅ Overall coverage: 45%
- ✅ All new tests pass consistently
- ✅ No regressions in existing tests

### Week 2 Success

- ✅ Quality analysis modules >80% coverage
- ✅ Overall coverage: 65%
- ✅ Test suite runs <5 minutes
- ✅ Clear test organization and naming

### Week 3 Success

- ✅ Overall coverage: 80%+
- ✅ All core business logic tested
- ✅ Test suite reliable and maintainable
- ✅ Coverage reports automated in CI/CD

## Risk Mitigation

### Technical Risks

- **Complex Dependencies:** Use extensive mocking for external services
- **State Management:** Ensure proper test isolation and cleanup
- **Performance:** Keep test execution time reasonable (<10 min)

### Quality Risks

- **Test Fragility:** Avoid brittle tests that break with minor changes
- **Maintenance Burden:** Keep tests simple and focused
- **False Confidence:** Ensure tests actually validate functionality

### Timeline Risks

- **Scope Creep:** Stick to coverage targets, not feature additions
- **Debugging Time:** Allocate time for test debugging and fixes
- **Integration Issues:** Test components work together properly

## Tools & Resources

### Testing Tools

- **pytest:** Test framework with fixtures and parametrization
- **pytest-cov:** Coverage reporting and analysis
- **pytest-mock:** Mocking and patching utilities
- **responses:** HTTP request mocking for web interfaces

### Development Tools

- **Coverage.py:** Detailed coverage analysis
- **HTML Coverage Reports:** Visual coverage inspection
- **CI/CD Integration:** Automated coverage checking

### Best Practices

- **Test-Driven Development:** Write tests before/parallel with code
- **Behavior-Driven Testing:** Focus on user behavior, not implementation
- **Continuous Integration:** Run tests on every change
- **Code Review:** Peer review of test quality and coverage

---

**Total Effort Estimate:** 12 days
**Coverage Increase:** +50 percentage points
**New Tests:** ~150 comprehensive tests
**Business Impact:** Enterprise-grade test coverage and reliability
