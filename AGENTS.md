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
- Files: `pyproject.toml`, `README_ai_onboard.md`, `AGENTS.md`, `ai_onboard/__init__.py`, `ai_onboard/__main__.py`, `ai_onboard/VERSION`, `ai_onboard/cli/commands.py`, core runtime modules (`utils.py`, `state.py`, `telemetry.py`, `validation_runtime.py`, `policy_engine.py`, `registry.py`), and baseline policy `ai_onboard/policies/base.json`.

CI enforces presence via `scripts/protected_paths.py`. If a cleanup removes any of
the above, CI fails. For local bulk changes, keep deletions restricted to caches
and build artifacts (e.g., `.ai_onboard/`, `__pycache__/`, `*.egg-info/`, `dist/`, `build/`).
