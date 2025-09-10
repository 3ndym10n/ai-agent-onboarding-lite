# Current System State: Technical Turnover Document

**Repository**: `ai-agent-onboarding/ai-agent-onboarding`
**Version**: 0.2.0 (pyproject.toml) / 0.2.0 (ai_onboard/__init__.py)
**Analysis Date**: 2024-12-19
**Status**: Alpha Development (Development Status :: 3 - Alpha)

## Executive Summary

The `ai-onboard` system is a **drop-in project coach** that provides charter + plan + align + validate + kaizen capabilities. It's designed as a self-contained Python package with minimal external dependencies, focusing on AI-assisted development governance and validation.

### Current Architecture State
- **Core Package**: `ai_onboard/` with 25+ runtime modules
- **CLI Interface**: Comprehensive command structure with 12+ subcommands
- **Policy Engine**: YAML-based rules with overlay support
- **Protected Paths**: CI-enforced critical file/directory preservation
- **Dependencies**: Standard library only (no external deps)
- **Python Support**: 3.8+ compatibility

## 1. Current Implementation Status

### 1.1 Package Structure (ACTUAL)

- ai_onboard/
  - __init__.py (v0.2.0)
  - __main__.py (CLI entry point)
  - VERSION
  - cli/ (commands and subcommands)
  - core/ (alignment, cache, charter, checkpoints, cleanup, discovery, error_resolver, intent_checks, issue, meta_policy, methodology, optimizer, optimizer_state, planning, policy_engine, profiler, progress_tracker, prompt_bridge, registry, scheduler, state, summarizer, telemetry, utils, validation_runtime, versioning, schema_validate)
  - policies/
    - base.yaml (canonical policy)
  - plugins/
    - example_policy.py (example plugin)
    - conventions/, library_module/, ui_frontend/
  - schemas/
    - policy.schema.json### 1.2 CLI Commands (IMPLEMENTED)
```bash
# Core workflow commands
python -m ai_onboard analyze [--allowExec]
python -m ai_onboard charter [--interactive]
python -m ai_onboard plan
python -m ai_onboard align [--checkpoint PlanGate] [--approve] [--note]
python -m ai_onboard validate [--report]
python -m ai_onboard kaizen [--once]
python -m ai_onboard optimize [--budget 5m]

# Utility commands
python -m ai_onboard version [--bump major|minor|patch] [--set 1.2.3]
python -m ai_onboard metrics
python -m ai_onboard cleanup [--dry-run] [--force] [--backup]

# Checkpoint management
python -m ai_onboard checkpoint create [--scope .] [--reason]
python -m ai_onboard checkpoint list
python -m ai_onboard checkpoint restore --id <id>

# Agent-facing APIs (feature-flagged)
python -m ai_onboard prompt state
python -m ai_onboard prompt rules [--path .] [--change]
python -m ai_onboard prompt summary [--level brief|full]
python -m ai_onboard prompt propose [--diff JSON]
```

### 1.3 Current Policy Rules (base.yaml)
```yaml
rules:
  - id: risky-env-delete
    conditions:
      any:
        - deletes_globs: ["**/.env", "**/*.env", "**/secrets/**", "**/*.pem", "**/id_rsa*"]
    action: block
    message: "Deleting env/secret/credential files is blocked."

  - id: big-change-requires-approval
    conditions:
      any:
        - files_gt: 10
        - lines_gt: 500
    action: require_approval
    message: "Large refactor detected. Take checkpoint and run tests."

  - id: refactor-needs-tests
    conditions:
      all:
        - touches_lang_any: ["py", "ts", "tsx", "js"]
        - files_gt: 3
    action: warn
    message: "Run tests before/after multi-file refactor."
```

## 2. Dependencies and Build State

### 2.1 Current Dependencies
```toml
# pyproject.toml - NO EXTERNAL DEPS
dependencies = [
    # Currently uses only standard library modules
    # Add external dependencies here as needed
]

# requirements.txt - DEV DEPS ONLY
pytest>=7.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
```

### 2.2 Build Configuration
- **Build System**: setuptools >= 61.0
- **Entry Point**: `ai-onboard = "ai_onboard.__main__:main"`
- **Package Discovery**: `ai_onboard*` patterns
- **Python Targets**: 3.8, 3.9, 3.10, 3.11, 3.12

## 3. Protected Assets (ENFORCED)

### 3.1 Required Files (scripts/protected_paths.py)
```python
REQUIRED_FILES = [
    # Top-level project metadata
    "pyproject.toml",
    "README_ai_onboard.md",
    "AGENTS.md",

    # Package identity
    "ai_onboard/__init__.py",
    "ai_onboard/__main__.py",
    "ai_onboard/VERSION",

    # CLI entry
    "ai_onboard/cli/__init__.py",
    "ai_onboard/cli/commands.py",

    # Core runtime (minimum viable)
    "ai_onboard/core/__init__.py",
    "ai_onboard/core/utils.py",
    "ai_onboard/core/state.py",
    "ai_onboard/core/telemetry.py",
    "ai_onboard/core/validation_runtime.py",
    "ai_onboard/core/policy_engine.py",
    "ai_onboard/core/registry.py",

    # Policies (baseline)
    "ai_onboard/policies/]
```

### 3.2 Required Directories
```python
REQUIRED_DIRS = [
    ".github",
    ".github/workflows",
    "ai_onboard",
    "ai_onboard/cli",
    "ai_onboard/core",
    "ai_onboard/plugins",
    "ai_onboard/plugins/conventions",
    "ai_onboard/plugins/library_module",
    "ai_onboard/plugins/ui_frontend",
    "ai_onboard/policies",
    "ai_onboard/policies/overlays",
    "ai_onboard/schemas",
]
```

## 4. CI/CD Pipeline (ACTIVE)

### 4.1 GitHub Actions (.github/workflows/ci.yml)
```yaml
name: CI
on: [pull_request, push]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - checkout@v4
      - setup-python@v5 (3.11)
      - python scripts/protected_paths.py
      - pip install -e .
      - python -m ai_onboard analyze
      - python -m ai_onboard charter
      - python -m ai_onboard plan
      - python -m ai_onboard align --approve
      - python -m ai_onboard validate --report
```

### 4.2 Agent Operations (.github/workflows/agentops.yml)
- Diff-based protected path enforcement
- Agent gate validation

## 5. Core Runtime Modules (IMPLEMENTED)

### 5.1 Validation Runtime (validation_runtime.py)
- **Purpose**: Orchestrates policy evaluation across components
- **Key Features**:
  - Plugin registry integration
  - Optimizer state management
  - Profiling and scheduling
  - Error fingerprinting and resolution
  - Scoring algorithm with configurable weights

### 5.2 State Management (state.py)
- **Purpose**: Project state persistence and advancement
- **Key Features**:
  - JSON-based state storage
  - Workflow stage tracking
  - State transitions

### 5.3 Telemetry (telemetry.py)
- **Purpose**: Structured logging and metrics collection
- **Key Features**:
  - JSONL output format
  - Event categorization
  - Performance tracking

### 5.4 Policy Engine (policy_engine.py)
- **Purpose**: YAML policy loading and evaluation
- **Key Features**:
  - Base policy + overlay merge
  - Rule condition evaluation
  - Action enforcement

## 6. Current Limitations and Technical Debt

### 6.1 Missing Components
- **Plugins Directory**: Empty (no actual plugins implemented)
- **Schemas Directory**: Empty (no JSON schemas defined)
- **Tests Directory**: Not present (no test suite)
- **Documentation**: Limited inline docs

### 6.2 Version Inconsistencies
- `pyproject.toml`: 0.1.1
- `ai_onboard/__init__.py`: 0.1.0
- `ai_onboard/VERSION`: 7 bytes (likely 0.1.0)

### 6.3 Build Artifacts (SHOULD BE IGNORED)
- `venv/` (committed - should be in .gitignore)
- `ai_onboard.egg-info/` (committed - should be in .gitignore)
- `__pycache__/` directories (committed - should be in .gitignore)

## 7. Immediate Technical Actions Required

### 7.1 Critical Fixes
1. **Version Alignment**: Sync all version references to 0.1.1
2. **Gitignore Updates**: Add `venv/`, `*.egg-info/`, `__pycache__/`
3. **Test Suite**: Create basic `tests/` directory and pytest setup
4. **Schema Definitions**: Implement JSON schemas for policies

### 7.2 Recommended Improvements
1. **Plugin Examples**: Create sample plugins in `ai_onboard/plugins/`
2. **Documentation**: Add docstrings to core modules
3. **Error Handling**: Improve exception handling in CLI commands
4. **Logging**: Standardize logging across modules

## 8. Development Workflow (CURRENT)

### 8.1 Local Setup
```bash
# Current working setup
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -e .
python -m ai_onboard --help
```

### 8.2 Validation Pipeline
```bash
# Current CI workflow
python scripts/protected_paths.py
python -m ai_onboard analyze
python -m ai_onboard charter
python -m ai_onboard plan
python -m ai_onboard align --approve
python -m ai_onboard validate --report
```

## 9. Handover Checklist

### 9.1 Environment Verification
- [ ] Python 3.8+ available
- [ ] Virtual environment working
- [ ] Package installs successfully
- [ ] CLI commands respond
- [ ] Protected paths script runs

### 9.2 Critical Files Present
- [ ] All required files from `scripts/protected_paths.py`
- [ ] All required directories exist
- [ ] Version consistency across files

### 9.3 CI Pipeline Status
- [ ] GitHub Actions workflows functional
- [ ] Protected paths enforcement working
- [ ] Agent operations validation passing

### 9.4 Known Issues
- [ ] Version inconsistencies documented
- [ ] Missing test suite noted
- [ ] Build artifacts cleanup needed
- [ ] Plugin system incomplete

## 10. Next Steps for Maintainers

1. **Immediate**: Fix version inconsistencies and gitignore
2. **Short-term**: Implement basic test suite
3. **Medium-term**: Add plugin examples and schemas
4. **Long-term**: Expand documentation and error handling

---

**Document Status**: Current as of 2024-12-19
**Maintainer**: [Your Name]
**Next Review**: [Date]
