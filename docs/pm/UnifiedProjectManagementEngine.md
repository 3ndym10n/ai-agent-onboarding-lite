# Unified Project Management Engine (UPME)

## Overview
The Unified Project Management Engine consolidates task lifecycle management, WBS synchronization, and progress analytics into a single service. It supersedes legacy modules such as `task_completion_detector.py`, `task_prioritization_engine.py`, and `wbs_*` engines while preserving backward compatibility through `pm_compatibility.py`.

## Key Capabilities
- **Task Lifecycle**: Prioritization and completion detection across phases/subtasks
- **WBS Synchronization**: Status reporting, updates, and auto-refresh logic
- **Progress Analytics**: Dashboard metrics, milestone status, critical path summaries

## API Entry Points
```python
from ai_onboard.core.unified_project_management import get_unified_project_management_engine

engine = get_unified_project_management_engine(project_root)
engine.tasks.prioritize_tasks()
engine.tasks.detect_completions()
engine.wbs.get_status()
engine.analytics.get_project_status()
```

## Compatibility Layer
Legacy imports continue to work via `ai_onboard.core.pm_compatibility`:
- `get_legacy_task_completion_detector`
- `get_legacy_task_prioritization_engine`
- `get_legacy_wbs_sync_engine`
- `get_legacy_progress_dashboard`

These wrappers emit `DeprecationWarning` and delegate to UPME.

## CLI Integration
The `project` command family (`python -m ai_onboard project ...`) routes through UPME services:
- `project critical-path`
- `project progress`
- `project task-completion`
- `project prioritize`
- `project wbs`

## Migration Guidance
1. Replace direct imports of legacy modules with `get_unified_project_management_engine`.
2. Update tests to use UPME APIs or the compatibility shims.
3. Monitor deprecation warnings to identify remaining legacy usage.
4. After phase 3 cleanup, remove reliance on `pm_compatibility` where possible.

## Validation & Gates
- Run `pytest tests/integration/test_project_management.py` for regression coverage.
- Summaries via `python -m ai_onboard prompt summary --level brief`.
- Full validation via `python -m ai_onboard validate --report` (requires aligned project state).

