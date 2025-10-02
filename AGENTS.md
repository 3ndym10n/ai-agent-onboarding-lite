# AI Agents Guidance

This repository expects any AI coding agent or assistant to follow these rules:

- Read this file before proposing or applying changes.
- Prefer minimal, targeted diffs that fix root causes.
- Do not reformat or rename files unless explicitly requested.
- Preserve public APIs and behavior unless a breaking change is approved.
- Add or update docs for any user-facing change.
- Avoid adding dependencies without prior approval.

Operational rules:

- Use `.ai_onboard/` for generated artifacts; do not commit them.
- If you add configs (editor, CI, codeowners), keep them small and focused.
- For Python, keep changes compatible with 3.8+.

Acknowledgement checklist for human authors and agents:

- [ ] I reviewed AGENTS.md and followed its guidance.
- [ ] I kept the scope minimal and documented changes.
- [ ] I considered backward compatibility and tests.

## Protected Paths

This repo protects critical directories/files from bulk deletions or "cleanup" runs:

- Directories: `.github/`, `.github/workflows/`, `ai_onboard/`, `ai_onboard/cli/`, `ai_onboard/core/`, `ai_onboard/plugins/`, `ai_onboard/plugins/{conventions,library_module,ui_frontend}`, `ai_onboard/policies/`, `ai_onboard/policies/overlays/`, `ai_onboard/schemas/`
- Files: `pyproject.toml`, `README.md`, `AGENTS.md`, `ai_onboard/__init__.py`, `ai_onboard/__main__.py`, `ai_onboard/VERSION`, `ai_onboard/cli/commands.py`, core runtime modules (`utils.py`, `state.py`, `telemetry.py`, `validation_runtime.py`, `policy_engine.py`, `registry.py`), and baseline policy `ai_onboard/policies/base.json`.

CI enforces presence via `scripts/protected_paths.py`. If a cleanup removes any of
the above, CI fails. For local bulk changes, keep deletions restricted to caches
and build artifacts (e.g., `.ai_onboard/`, `__pycache__/`, `*.egg-info/`, `dist/`, `build/`).

Additional guard (diff-based): `scripts/protected_paths_diff.py` fails if a PR touches sensitive paths. Wired in `.github/workflows/agentops.yml`. For local use, enable the sample pre-push hook:

```bash
git config core.hooksPath .githooks
```

### Local Protection (pre-commit)

Enable the local hook to block accidental deletion of protected files:

```bash
git config core.hooksPath .githooks
```

If you must override for a particular commit:

- Set `BYPASS_PROTECTED_HOOK=1` in the environment for that commit, or
- Use `git commit --no-verify` (note CI and CODEOWNERS may still block the change).

## Agent Gates (Stop/Go)

Agents should follow these gates to stay aligned and safe:

- Gate A (Pre-edit): `python -m ai_onboard prompt summary --level brief` and attach to PR context.
- Gate B (Safety): Use intelligent monitoring `python -m ai_onboard intelligent analyze comprehensive` when `files>10` or `lines>500`.
- Gate C (Guard): Check for active gates with `python -m ai_onboard cursor context` and handle any collaboration gates.
- Gate D (Post-op): `python -m ai_onboard validate --report` and address high-risk findings before merge.

## AI Agent Integration

This repository now includes comprehensive AI agent integration:

### New AI Agent Guidance System
- **Dynamic guidance** that adapts to agent experience and project context
- **Safety mechanisms** with multiple protection levels
- **Collaboration protocols** for structured agent interaction
- **Session management** with limits and monitoring

### Available AI Agent Commands
- `python -m ai_onboard cursor init` - Initialize Cursor AI integration
- `python -m ai_onboard cursor session create` - Create collaboration session
- `python -m ai_onboard intelligent start` - Start intelligent monitoring
- `python -m ai_onboard holistic discover` - Discover available tools
- `python -m ai_onboard holistic orchestrate` - Orchestrate tools for requests

### AI Agent Safety
- **Protected files** are automatically blocked from modification
- **Dangerous commands** are detected and require approval
- **Session limits** prevent runaway agent behavior
- **Collaboration modes** (assistive, collaborative, supervised, autonomous)

## Import Consolidation System

The repository now includes a comprehensive import consolidation system for optimizing Python code structure. When working with imports:

### Available Tools

- **Analysis**: `python -m ai_onboard consolidate analyze` - Identifies consolidation opportunities
- **Planning**: `python -m ai_onboard consolidate plan` - Creates migration plans with safety checks
- **Execution**: `python -m ai_onboard consolidate execute` - Executes consolidation with rollback protection
- **Validation**: `python -m ai_onboard consolidate validate` - Validates import equivalence

### Safety Guidelines

- Always use the built-in safety gates when consolidating imports
- The system automatically creates backups and provides rollback capabilities
- Import consolidation changes are protected by the same safety mechanisms as other operations
- Use `--dry-run` flags to preview changes before execution

### Best Practices

- Consolidate only frequently used imports (appearing in 5+ files)
- Prefer creating new utility modules over modifying existing ones
- Always validate import equivalence after consolidation
- Test thoroughly before committing consolidation changes

For detailed documentation, see [docs/IMPORT_CONSOLIDATION_SYSTEM.md](docs/IMPORT_CONSOLIDATION_SYSTEM.md).
