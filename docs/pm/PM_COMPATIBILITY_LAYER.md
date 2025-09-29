# 🛡️ Project Management Compatibility Layer Design

## Goals
- Preserve existing APIs for project-management modules during UPME rollout
- Provide drop-in replacements that delegate to the UnifiedProjectManagementEngine (UPME)
- Emit deprecation warnings with migration guidance
- Allow gradual rollout via feature flags (`legacy_mode`)
- Maintain safety instrumentation and telemetry

## Target Legacy Entry Points
- `get_wbs_sync_engine(root)` → returns wrapper over `engine.wbs`
- `WBSAutoUpdateEngine`, `WBSUpdateEngine`, `WBSSynchronizationEngine`
- `TaskCompletionDetector`, `TaskPrioritizationEngine`, `TaskExecutionGate`
- CLI helper functions in `commands_project_management.py`
- Utility helpers (e.g., `progress_utils`, `critical_path_engine`)

## Adapter Strategy
```python
from ai_onboard.core.unified_project_management import UnifiedProjectManagementEngine

_engine_singletons = {}

def get_upme(root):
    if root not in _engine_singletons:
        _engine_singletons[root] = UnifiedProjectManagementEngine(root)
    return _engine_singletons[root]

class LegacyWBSSynchronizationEngine:
    def __init__(self, root):
        self._engine = get_upme(root)

    def get_wbs_status(self):
        warnings.warn(
            "Legacy WBSSynchronizationEngine is deprecated; use engine.wbs API",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._engine.wbs.status()
```

### Deprecation Messaging
- Include migration target (`engine.wbs`, `engine.tasks`, `engine.analytics`)
- Provide link to documentation (`docs/pm/UPME_MIGRATION.md` TBD)
- Use `DeprecationWarning`; ensure tests exercise warnings via `pytest.warns`

### Feature Flag Handling
- `UPMEConfig(legacy_mode=True)` by default
- Compatibility wrappers respect `legacy_mode`; can short-circuit to legacy behavior if necessary
- Gradually disable `legacy_mode` in Phase 3

## Safety & Telemetry
- Adapters invoke UPME methods that already handle backups and validation
- Legacy logging redirected to UPME telemetry streams
- Maintain existing tool usage tracking (calls forwarded to new tracker hooks)

## Rollout Checklist
1. Implement compatibility wrappers in `ai_onboard/core/pm_compatibility.py`
2. Update modules to import from compatibility layer instead of legacy classes
3. Add unit tests ensuring wrappers call UPME methods
4. Confirm deprecation warnings emitted and captured in regression suite
5. Document migration paths for developers and scripts

## Open Items
- Decide whether to keep constructor signatures identical or introduce kwargs for new options
- Determine timeline for disabling `legacy_mode`
- Ensure CLI command help text references UPME after rollout
