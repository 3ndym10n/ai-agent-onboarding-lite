# 🧠 Unified Project Management Engine (UPME) Architecture

## 1. Objectives
- Provide a single, authoritative API for all project-management workflows
- Centralize data access to project artifacts (`plan.json`, `project_plan.json`, `roadmap.json`, `pending_tasks.json`, learning logs)
- Consolidate task lifecycle, WBS synchronization, and progress analytics into modular services
- Preserve legacy behavior via a compatibility layer while emitting deprecation guidance
- Enable safety instrumentation, telemetry, and learning integration across PM operations

## 2. High-Level Architecture
```
┌──────────────────────────┐
│ UnifiedProjectManagement │
│         Engine           │
├──────────┬───────────────┤
│ Data     │ Service Layer │
│ Gateway  │ (pluggable)   │
├──────────┴───────────────┤
│ Compatibility Adapters   │
└──────────┬───────────────┘
           │
      Legacy Consumers
```

### Core Modules
1. **ProjectDataGateway**
   - Canonical schema loader/writer
   - Caching + validation (JSON schema, structural integrity)
   - Change journaling & backup hooks

2. **TaskLifecycleService**
   - Task discovery, prioritization, completion syncing
   - Integrates existing detection logic (deduplicated)
   - Publishes lifecycle events for telemetry/learning

3. **WBSSynchronizationService**
   - Manages WBS hierarchy, conflict resolution, delta application
   - Harmonizes former sync/auto-update/update modules

4. **ProgressAnalyticsService**
   - Generates dashboards, critical path metrics, milestone status
   - Single source for CLI/UI reporting

5. **Approval & Safety Integrations**
   - Hooks into approval workflow, gate systems, safety validation
   - Enforces safety gates before state mutations

## 3. Data Gateway Design
- **Source Artifacts**: `plan.json`, `project_plan.json`, `roadmap.json`, `pending_tasks.json`, `learning_events.jsonl`
- **Canonical Schema**: Merge plan/project_plan into `project_plan.v2`
  - WBS hierarchy, milestones, critical path, metadata
  - Derived views for dashboard/roadmap consumers
- **Access Patterns**:
  - Read-through cache with 5-minute TTL & manual invalidation
  - Write API enforces schema validation + audit log entry
  - Change notifications broadcast via event bus (in-memory pub/sub initially)
- **Backups**: Automatic snapshot to `.ai_onboard/wbs_backups` before mutations

## 4. Compatibility Layer
- `pm_compatibility.py`
  - Functions/classes mirroring legacy signatures (`get_wbs_sync_engine`, `TaskCompletionDetector`, etc.)
  - Delegates to UPME services
  - Emits `DeprecationWarning` with migration hints
- **Feature Flags**
  - `legacy_mode=True` by default; toggled off after Phase 3
  - Environment/config switch for gradual rollout

## 5. Public API Sketch
```python
engine = UnifiedProjectManagementEngine(root_path)

summary = engine.analytics.get_project_status()
priorities = engine.tasks.prioritize(criteria={"include_risk": True})
completion = engine.tasks.detect_completions(force_scan=False)
engine.wbs.apply_update(task_id="1.4", status="completed")

legacy_adapter = get_wbs_sync_engine(root_path)  # returns compatibility wrapper
```

## 6. Testing Strategy
- **Unit Tests**: Service modules, data gateway validation, compatibility shims
- **Integration Tests**: CLI command flows using UPME, regression for existing behaviors
- **Fixture Data**: Canonical sample plan & derived artifacts
- **Safety Tests**: Ensure backups & validation triggered on write operations

## 7. Implementation Sequencing
1. Implement ProjectDataGateway with schema validators & caching
2. Migrate WBS services onto gateway-backed storage
3. Consolidate task completion/prioritization into TaskLifecycleService
4. Refactor progress analytics to consume consolidated data
5. Wire compatibility layer; update CLI & scripts
6. Remove legacy modules after validation window

## 8. Open Questions
- Final canonical schema location (`docs/schemas/project_plan_v2.json`?)
- Eventing mechanism (in-memory vs persistent queue)
- Safety Gate C upgrade to reference UPME APIs
- Migration tooling to update external scripts (if any)

## 9. Next Actions (Phase 2)
- Draft JSON schema v2 for consolidated project plan
- Prototype data gateway with read-only mode to verify consumers
- Design compatibility wrapper interfaces & logging strategy
- Author detailed testing matrix (unit + integration coverage)

