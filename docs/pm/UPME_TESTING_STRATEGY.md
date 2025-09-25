# 🧪 Unified Project Management Engine Testing Strategy

## 1. Objectives
- Guarantee behavioral parity between legacy PM tooling and UPME
- Validate canonical data gateway operations (read/write, backup, schema enforcement)
- Ensure compatibility adapters emit warnings and delegate correctly
- Provide regression coverage for CLI and script use cases

## 2. Test Layers

### Unit Tests
- `project_data_gateway` schema validation, caching, backup hooks
- `TaskLifecycleService` prioritization/completion/updates
- `WBSSynchronizationService` conflict resolution, delta application
- `ProgressAnalyticsService` metrics generation, critical path computation
- Compatibility wrappers (`pm_compatibility.py`) with warnings captured via `pytest.warns`

### Integration Tests
- End-to-end CLI commands (`project critical-path`, `project progress`, `project task-completion`, `project wbs`, `project approvals`)
- Legacy entry points (e.g., `get_wbs_sync_engine`) using compatibility layer while asserting warning emission
- Data mutation flows ensuring backups and learning events are triggered
- Safety gate interactions (mock Gate C/D to confirm enforcement)

### Regression Coverage
- Golden sample project plan fixtures for comparisons
- Snapshot tests for dashboard outputs / analytics summaries
- Migration script dry-runs against canonical fixtures

## 3. Tooling & Fixtures
- `tests/fixtures/project_plan_v2.json` (canonical schema)
- `tests/fixtures/project_plan_legacy.json` (legacy format) for conversion tests
- Mock telemetry/logging to capture events without hitting disk
- Utility helpers for resetting gateway cache between tests

## 4. Validation Commands
- `pytest tests/project_management -v`
- `pytest tests/integration/test_project_management.py -v`
- `python -m ai_onboard validate --report` (Gate D)
- Optional: `python -m ai_onboard tools recommend --task "pm_consolidation"` to ensure tool discovery intact

## 5. Coverage Goals
- ≥90% branch coverage for new UPME modules
- 100% coverage on compatibility wrappers, including deprecation warnings
- Integration tests covering all CLI subcommands and major workflows

## 6. CI Integration
- Add dedicated job `ci_upme_tests` running unit + integration suites
- Upload schema diff reports on failure
- Enforce warnings-as-errors in CI for compatibility layer tests

## 7. Risk Mitigation Tests
- Stress tests for concurrent access (future enhancement)
- Failure mode simulation (corrupt JSON, missing files) to verify rollback/backup
- Performance benchmarks to ensure no regression relative to legacy modules

## 8. Outstanding Items
- Determine final location for fixtures (shared vs pm-specific)
- Decide whether to integrate contract tests with external consumers (if any)
- Evaluate using hypothesis/ property-based testing for data gateway

