Title: System Turnover Document for the AI Onboard (Drop-in) Repository

Authors: <Your Name>, <Team/Org>
Version: 1.0
Date: <YYYY-MM-DD>
Repository: `ai-agent-onboarding/ai-agent-onboarding`

Abstract
This document provides a comprehensive turnover package for the AI Onboard (Drop-in) project. It is written in an academic style to enable thorough peer review, reproducibility, and responsible maintenance. It covers system purpose, architecture, operational constraints, development workflows, risk posture, testing and validation, deployment considerations, and an explicit handover checklist. The document emphasizes the repository’s design goal to enforce disciplined change management for AI coding agents and human contributors alike.

1. Introduction
1.1 Objective
The purpose of this document is to summarize the current state of the repository and define procedures to maintain, extend, and safely evolve the system. The document supports new maintainers by describing the project’s constraints and governance model, with specific attention to minimal diffs, policy enforcement, and protected paths.

1.2 Scope
This turnover addresses: repository layout, branching and CI policies, dependency management, core runtime components, policy/schema assets, and local/CI protections. It excludes deep refactors and product roadmap decisions, which should be captured in separate design notes or RFCs if needed.

1.3 Success Criteria
- The project remains compatible with Python 3.8+.
- Public APIs and behavior are preserved unless explicitly approved.
- Protected paths remain intact; any changes are intentional and reviewed.
- Changes are minimal, well-documented, and tested.

2. System Overview
2.1 Purpose and Philosophy
The repository functions both as a utility and as a proving ground for disciplined AI-assisted development. Its constraints (e.g., protected paths, minimal diffs) are integral to the product goal of enforcing thoughtful, reviewable change.

2.2 High-Level Components
- Core package: `ai_onboard/` including runtime modules, CLI, plugins, policies, overlays, and schemas.
- Tooling and configuration: `pyproject.toml`, `requirements.txt`, `.github/workflows/`, `scripts/`.
- Docs and guidance: `README.md`, `AGENTS.md`.

2.3 Execution Environment
- Target OS: Windows 10+ (PowerShell), but generally platform-independent Python.
- Python: 3.8+; virtual environment typically present as `venv/`.

3. Repository Structure and Protected Assets
3.1 Key Directories and Files
- `ai_onboard/`: core runtime, CLI, plugins, policies, schemas.
- `.github/` and workflows: CI enforcement.
- `scripts/`: protection and validation utilities.
- `pyproject.toml`, `README.md`, `AGENTS.md`, `ai_onboard/VERSION`.

3.1.1 Directory Model (canonical)
- `ai_onboard/`            # package: runtime, CLI, plugins, canonical policies, schemas
  - `cli/`
  - `core/`
  - `plugins/`
  - `policies/`            # e.g., base.yaml (+ versioned variants)
  - `schemas/`             # JSON Schemas for policies & telemetry
- `.ai_onboard/`           # artifacts (NEVER committed): logs, telemetry, snapshots, local overlays
  - `logs/`                # JSONL run logs
  - `telemetry/`
  - `snapshots/`
  - `overlays/`            # local policy overrides, e.g., policy.yaml

3.2 Protection Model
CI and local hooks enforce the presence and integrity of critical files and directories. Diff-based guards (e.g., `scripts/protected_paths_diff.py`) block overly broad or unsafe edits. For local development, contributors can enable `git config core.hooksPath .githooks` and override deliberately only when justified.

4. Development Workflow
4.1 Branching Strategy
- Create short-lived feature branches from `main` (e.g., `feature/<topic>`).
- Keep changes atomic and minimal; avoid unrelated refactors.

4.2 Commit and PR Standards
- Use descriptive commit messages with clear rationale.
- Reference applicable docs or issues and indicate any user-facing impact.
- For PRs, explicitly confirm compliance with AGENTS.md guidance and the protected-paths policy.

4.3 Local Environment
- Use a Python virtual environment; install dependencies via `requirements.txt` or `pyproject.toml` managed tools.
- Place generated artifacts (reports, logs) under `.ai_onboard/` and do not commit them.

5. Architecture and Components
5.1 Core Runtime Modules (Overview)
- Utilities and State: foundational helpers and state management supporting runtime behavior.
- Telemetry: optional observability hooks for diagnostics.
- Validation Runtime and Policy Engine: enforce and evaluate policies defined under `ai_onboard/policies/` and overlays.
- Registry: component discovery/registration for plugins and policies.
- CLI (`ai_onboard/cli/commands.py`): entry points for developer workflows.

5.2 Policies, Schemas, and Overlays
- Canonical policy: `ai_onboard/policies/base.yaml` (YAML; schema at `ai_onboard/schemas/policy.schema.json`).
- Local overlay (optional): `.ai_onboard/overlays/policy.yaml`.
- Merge semantics: overlay overrides base by key. For `rules`, concatenate then de‑dupe by `id` (overlay wins).
- Maintainers MUST update canonical policies; agents/tools may ONLY write overlays.

5.3 Backward Compatibility Contracts
Public APIs and canonical policy behavior must not change without prior approval and documentation. Additive, non-breaking changes are preferred; when breaking changes are unavoidable, provide migration notes and versioning as appropriate.

6. Dependency and Build Management
6.1 Source of Truth
Prefer a single authoritative source for dependency versions. If both `pyproject.toml` and `requirements.txt` are used, keep them synchronized (automate generation if possible).

6.2 Python Compatibility
Ensure Python 3.8+ compatibility; avoid language or library features that break older minor versions.

6.3 Reproducibility
Pin versions where feasible; record environmental details when producing artifacts. Store local baselines under `.ai_onboard/` (excluded from VCS).

7. Testing and Validation
7.1 Levels of Testing
- Unit tests for core modules (e.g., utils, state, telemetry, validation, policy engine, registry).
- Integration tests for CLI flows, plugin discovery, and policy execution.
- Regression checks against baseline policy and overlays.

7.2 Acceptance Criteria
- All tests green locally and in CI.
- No new linter errors.
- Protected paths untouched except for intentional, reviewed changes.

7.3 Evidence Capture
Record test summaries and environment snapshots in `.ai_onboard/` for traceability; exclude from commit history.

8. Risk Assessment and Controls
8.1 Key Risks
- Unintended modification of protected assets.
- Dependency drift or incompatible upgrades.
- Overly broad changes that obscure root-cause fixes.

8.2 Mitigations
- Scripts and CI guards for protected paths.
- Incremental, minimal diffs with clear justification.
- Dependency updates limited to patch/minor unless approved, with rollback steps.

9. Operations, CI/CD, and Release
9.1 CI Enforcement
Workflows validate presence of critical files and prevent unsafe diffs. Use pre-push hooks locally to catch issues earlier.

9.2 Release and Tagging
If tags/releases are used, document release notes, highlight compatibility, and provide upgrade guidance.

9.3 Rollback Strategy
- Revert PRs that introduce regressions.
- Maintain prior dependency snapshots to restore quickly.
- Keep changes isolated per branch to limit blast radius.

9.4 Agent Gates (Stop/Go)
- Gate A (Pre-edit): emit a brief summary and attach to PR: `python -m ai_onboard prompt summary --level brief`.
- Gate B (Safety): checkpoint if `files>10` OR `lines>500`: `python -m ai_onboard checkpoint create --scope "." --reason "pre-change"`.
- Gate C (Guard): propose planned action and evaluate; require non-blocking decision (e.g., `allow` or `warn`): `python -m ai_onboard prompt propose --diff '{"files_changed":[],"lines_deleted":0}'`. Any `block` fails CI.
- Gate D (Post-op): run validation and log hints: `python -m ai_onboard validate --report`; block merge if high‑risk issues are detected.

10. Security and Compliance
10.1 Dependencies
Monitor for CVEs and upgrade promptly within compatibility bounds.

10.2 Secrets Management
Ensure no secrets are committed. Validate that logs and artifacts exclude sensitive data.

11. Documentation Policy
11.1 User-Facing Docs
Update `README.md` for any user-visible changes. Provide minimal, high-signal diffs.

11.2 Change Records
Document rationale in PRs; if adopting a CHANGELOG, keep entries concise and factual.

12. Onboarding and Handover Checklist
- Access to repository and CI is confirmed.
- Local environment set up (Python 3.8+, venv, dependencies installed).
- Protected paths and policies understood; hooks enabled (`git config core.hooksPath .githooks`).
- Test suite runs green locally.
- Operational scripts reviewed (`scripts/`), especially protected-path checks.
- Open issues and pending PRs reviewed.
- Ownership and escalation paths identified.

Appendix A: Suggested Runbooks
A.1 New Feature or Fix
1. Create a feature branch from `main`.
2. Implement minimal, targeted edits.
3. Run tests and linters locally.
4. Document user-facing changes.
5. Open a PR; ensure protected paths are respected.

A.2 Dependency Update
1. Propose updated versions with changelog notes.
2. Update the single source of truth (lockfile or requirements).
3. Run tests and validate key flows.
4. Provide rollback plan and evidence in the PR.

A.3 Emergency Rollback
1. Revert the offending commit(s).
2. Restore prior dependency snapshot if relevant.
3. Re-run tests; confirm parity with prior state.

Appendix B: Glossary
- Protected Paths: Files/directories guarded by scripts and CI.
- Baseline Policy: Canonical policy constraints in `ai_onboard/policies/base.yaml`.
- Minimal Diff: Small, targeted change that addresses a specific root cause.

End of Document.


Appendix C: Technical Methodologies and Examples

C.1 Environment Setup and Reproducibility
- Create and activate a virtual environment (PowerShell on Windows):
```bash
python -m venv .\venv
.\venv\Scripts\Activate.ps1
```
- Install dependencies from `requirements.txt`:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
- Capture a dependency snapshot (not committed):
```bash
mkdir -Force .ai_onboard 2>$null
pip freeze > .ai_onboard\baseline_freeze.txt
```

C.2 Branching, Commit Hygiene, and Protected Paths
- Create a feature branch for upgrades or fixes:
```bash
git checkout -b feature/system-upgrade-implementation
```
- Enable local hooks for protected paths:
```bash
git config core.hooksPath .githooks
```
- Pre-flight check (diff against main):
```bash
python .\scripts\protected_paths_diff.py origin\main
```

C.3 Minimal Dependency Upgrade Workflow
1. Propose target versions based on changelogs and CVEs.
2. Update the single source of truth (e.g., edit `requirements.txt`).
3. Reinstall and validate:
```bash
pip install -r requirements.txt
pytest -q
```
4. If regression occurs, restore baseline:
```bash
pip install -r .ai_onboard\baseline_freeze.txt
```

C.4 CLI Integration Test Example
Assuming the project exposes a CLI via `ai_onboard/cli/commands.py` and an entry point `python -m ai_onboard`:
```bash
python -m ai_onboard --help
python -m ai_onboard prompt summary --level brief
python -m ai_onboard validate --report
```

C.5 Programmatic Policy Validation Example (YAML)
The following example shows loading a YAML policy (illustrative; adapt to current runtime APIs).
```python
from pathlib import Path
import yaml

def load_policy() -> dict:
    base = Path("ai_onboard/policies/base.yaml")
    return yaml.safe_load(base.read_text(encoding="utf-8"))

def run_validation(policy: dict, target_config_path: str) -> bool:
    # placeholder: wire to your runtime
    return bool(policy) and Path(target_config_path).exists()

if __name__ == "__main__":
    ok = run_validation(load_policy(), "path/to/config.yaml")
    print("PASS" if ok else "FAIL")
```

C.6 Plugin Registration Pattern (Python)
If the project supports plugins via a registry, a clean pattern is to expose registration through an explicit API.
```python
from ai_onboard.registry import PluginRegistry  # example path

class ExamplePolicyPlugin:
    name = "example-policy"

    def evaluate(self, document):
        # implement evaluation returning structured result
        return {"ok": True, "details": []}

def register_example_plugin(registry: PluginRegistry) -> None:
    registry.register("policy", ExamplePolicyPlugin.name, ExamplePolicyPlugin())

if __name__ == "__main__":
    registry = PluginRegistry()
    register_example_plugin(registry)
    print("Registered:", registry.list_plugins(kind="policy"))
```

C.7 Telemetry and Logging Best Practices (Python)
Structured logging improves diagnosability without breaking compatibility.
```python
import json
import logging

logger = logging.getLogger("ai_onboard")
logger.setLevel(logging.INFO)

def log_event(event_name: str, **fields) -> None:
    payload = {"event": event_name, **fields}
    logger.info(json.dumps(payload))

def run_with_logging(task_name: str) -> None:
    try:
        log_event("task_start", task=task_name)
        # ... perform task ...
        log_event("task_success", task=task_name)
    except Exception as exc:
        log_event("task_error", task=task_name, error=str(exc))
        raise
```

C.8 Schema Evolution Methodology
- Prefer additive changes (new fields, defaults) over breaking modifications.
- Version schemas if removal/rename is unavoidable; provide a migration adapter.
- Validate examples against both prior and current schemas during transition.
```python
from jsonschema import validate

def is_backward_compatible(instance: dict, old_schema: dict, new_schema: dict) -> bool:
    try:
        validate(instance=instance, schema=old_schema)
        validate(instance=instance, schema=new_schema)
        return True
    except Exception:
        return False
```

C.9 Windows-Friendly Automation Notes
- Avoid pagers in CI: prefer commands that print directly (or pipe to `cat`/`Out-Host`).
- Use PowerShell-safe paths and escaping; prefer `Join-Path` in scripts.
- Ensure scripts fail fast with non-zero exit codes for CI visibility.

C.10 Release and Tag Example (Git)
```bash
git checkout main
git pull --ff-only
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

C.11 PR Template Cue (to include in description)
- Purpose and scope of change
- Impact on public APIs and protected paths: none / describe
- Test evidence: unit, integration, manual
- Risk and rollback plan
- Docs updated: yes/no (files)


Appendix D: Overlay Merge Algorithm (Reference)

D.1 Goals
- Deterministic, minimal-diff merges of `.ai_onboard/overlays/policy.yaml` onto `ai_onboard/policies/base.yaml`.
- Overlay wins on scalar/object keys. For `rules` arrays, concatenate, then de-duplicate by `id` with overlay taking precedence.

D.2 Pseudocode
```python
from __future__ import annotations
from typing import Dict, Any, List

def deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, overlay_value in overlay.items():
        if key == "rules" and isinstance(overlay_value, list):
            result[key] = merge_rules(base.get("rules", []), overlay_value)
        elif isinstance(overlay_value, dict) and isinstance(base.get(key), dict):
            result[key] = deep_merge(base[key], overlay_value)
        else:
            result[key] = overlay_value
    return result

def merge_rules(base_rules: List[Dict[str, Any]], overlay_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_id: Dict[str, Dict[str, Any]] = {}
    for rule in base_rules:
        rule_id = rule.get("id")
        if rule_id is not None:
            by_id[rule_id] = rule
    for rule in overlay_rules:
        rule_id = rule.get("id")
        if rule_id is not None:
            by_id[rule_id] = rule  # overlay wins
    # Preserve stable order: base ids first then overlay-only
    seen = set()
    merged: List[Dict[str, Any]] = []
    for rule in base_rules:
        rid = rule.get("id")
        if rid is not None and rid in by_id and rid not in seen:
            merged.append(by_id[rid]); seen.add(rid)
    for rule in overlay_rules:
        rid = rule.get("id")
        if rid is not None and rid not in seen:
            merged.append(by_id[rid]); seen.add(rid)
    return merged
```

D.3 Example
Base (`ai_onboard/policies/base.yaml`):
```yaml
rules:
  - id: no-large-diff
    action: warn
  - id: keep-protected-paths
    action: block
thresholds:
  max_files: 10
```

Overlay (`.ai_onboard/overlays/policy.yaml`):
```yaml
rules:
  - id: no-large-diff
    action: block
thresholds:
  max_files: 5
```

Merged (effective policy):
```yaml
rules:
  - id: no-large-diff
    action: block
  - id: keep-protected-paths
    action: block
thresholds:
  max_files: 5
```


Appendix E: Policy Schema Example (JSON Schema)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ai_onboard/schemas/policy.schema.json",
  "type": "object",
  "properties": {
    "rules": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "action"],
        "properties": {
          "id": {"type": "string", "minLength": 1},
          "action": {"type": "string", "enum": ["allow", "warn", "require_approval", "block"]},
          "message": {"type": "string"}
        },
        "additionalProperties": true
      }
    },
    "thresholds": {
      "type": "object",
      "properties": {
        "max_files": {"type": "integer", "minimum": 0},
        "max_lines": {"type": "integer", "minimum": 0}
      },
      "additionalProperties": true
    }
  },
  "additionalProperties": true
}
```


Appendix F: Pytest Examples
`tests/test_policy_merge.py`
```python
import yaml
from your_module.merge import deep_merge  # adapt import

def test_overlay_wins_scalar():
    base = yaml.safe_load("""
thresholds:
  max_files: 10
""")
    overlay = yaml.safe_load("""
thresholds:
  max_files: 5
""")
    merged = deep_merge(base, overlay)
    assert merged["thresholds"]["max_files"] == 5

def test_rules_dedupe_by_id():
    base = yaml.safe_load("""
rules:
  - id: a
    action: warn
  - id: b
    action: block
""")
    overlay = yaml.safe_load("""
rules:
  - id: a
    action: block
  - id: c
    action: allow
""")
    merged = deep_merge(base, overlay)
    ids = [r["id"] for r in merged["rules"]]
    assert ids == ["a", "b", "c"]
    assert next(r for r in merged["rules"] if r["id"] == "a")["action"] == "block"
```


Appendix G: GitHub Actions CI Snippet (Policy Guard)
`.github/workflows/policy-guard.yml`
```yaml
name: policy-guard
on:
  pull_request:
    branches: [ main ]
jobs:
  guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.8'
      - name: Install
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt || true
      - name: Run agent gates
        run: |
          python -m ai_onboard prompt summary --level brief || true
          python -m ai_onboard validate --report
```


Appendix H: PowerShell Helpers (Windows)
`scripts/utils.ps1`
```powershell
function Invoke-WithoutPager {
    param([Parameter(Mandatory=$true)][string]$Command)
    $env:LESS = 'FRX'
    $env:PAGER = ''
    Invoke-Expression $Command | Out-Host
}

function Save-DependencySnapshot {
    param([string]$Path = '.ai_onboard/baseline_freeze.txt')
    if (-not (Test-Path '.ai_onboard')) { New-Item -ItemType Directory -Path '.ai_onboard' | Out-Null }
    pip freeze | Set-Content -Encoding UTF8 $Path
}
```

10.3 Telemetry JSONL (per action)
Agents and humans should read the same JSONL facts for decisions and audits.
```
{"ts":"2025-08-29T10:22:11Z","agent":"cursor:gpt-4o","cmd":"guard","decision":"warn","rules":["big-change-requires-approval"],"files":12,"lines":680}
```

Appendix I: Unified Project Management Engine Migration Guide
