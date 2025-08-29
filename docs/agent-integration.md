# AI Agent Integration: Design Notes

This document proposes a minimal, composable way to make AI Onboard truly useful for autonomous and semi-autonomous agents (Cursor, Codex, GPTs, Claude, etc.) without breaking existing behavior.

Goals:
- Shared project memory agents can query and trust
- Safety rails before file operations
- Nonlinear work support (checkpoints, rollback, branch comparison)
- Cross-agent telemetry and context summarization
- Thin APIs with small surface area and no new deps

## 1) Prompt-Level API (thin surface)

Expose just enough for agents to self-serve context and guardrails. Two modes are useful: CLI and Python.

CLI (proposed):
- `python -m ai_onboard prompt state` → JSON state summary (manifest, last metrics)
- `python -m ai_onboard prompt rules --path <file> --change <summary>` → relevant policy checks to review
- `python -m ai_onboard prompt summary --level {brief,full}` → summarized context for small/large models

Python (proposed package API):
- `ai_onboard.agent.state(root) -> dict`  (manifest + last metrics + top issues)
- `ai_onboard.agent.preflight(root, path, change_summary) -> list[dict]`  (rules likely to apply)
- `ai_onboard.agent.summary(root, level='brief') -> dict` (summaries cached under `.ai_onboard/`)

Notes:
- The CLI can be implemented as thin wrappers around existing readers (`telemetry.read_metrics`, manifest loader) plus small summarizers.
- Keep outputs stable and concise so agents can rely on them.

## 2) Checkpoints & Rollback (agent-aware)

Lightweight snapshots to support retries/branching without requiring Git.

Layout:
- `.ai_onboard/checkpoints/<id>/` → file snapshots (selected scope; not the entire repo by default)
- `.ai_onboard/checkpoints/index.jsonl` → append-only metadata

Checkpoint metadata (JSONL per record):
```json
{
  "ts": "2025-01-01T12:34:56Z",
  "id": "ckpt_00023",
  "agent_id": "cursor",
  "task_id": "refactor-utils",
  "scope": ["src/utils.py", "tests/test_utils.py"],
  "reason": "before-lint-refactor",
  "metrics": {"errors": 3, "failures": 0}
}
```

CLI (proposed):
- `python -m ai_onboard checkpoint create --scope <glob>... --reason <str>`
- `python -m ai_onboard checkpoint list`
- `python -m ai_onboard checkpoint restore --id <ckpt>` (safe restore with confirmation)

Design principles:
- Default to “small scope” snapshots; allow opt-in full snapshot.
- Rollback requests require explicit `--force` or interactive confirmation.
- Never touch protected paths during snapshot/restore.

## 3) Cross-Agent Telemetry (unified JSONL)

Add a separate, additive stream so we don’t break existing `metrics.jsonl`:
- File: `.ai_onboard/agents.jsonl`

Schema (append-only):
```json
{
  "ts": "2025-01-01T12:34:56Z",
  "agent_id": "cursor",
  "model": "gpt-4o",
  "role": "coder|planner|reviewer",
  "task_id": "implement-foo",
  "action": "edit|refactor|test|run|revert",
  "target": ["src/foo.py"],
  "outcome": "success|failure|partial",
  "errors": 1,
  "checkpoint_id": "ckpt_00023",
  "branch": "approach-A",
  "notes": "optional short context"
}
```

Usage:
- Agents append small records; human-readable and merge-friendly.
- Allows comparing approaches (e.g., fewer errors on branch A vs. B).

## 4) Context Summarization (for small windows)

Outputs:
- `.ai_onboard/summaries/brief.json` → compact project state, top issues, last run
- `.ai_onboard/summaries/full.json` → detailed components, relevant rules, hot files

Generation:
- `python -m ai_onboard prompt summary --level brief`
- Summaries should be idempotent and fast to compute; cache where useful.

## 5) Meta-Policy for Agent Behavior

Beyond file validation, add policies about the size and risk of changes:

Examples:
- "Don’t delete > X lines without related tests."
- "Don’t refactor > N files per run."
- "Pause for confirmation when modifying protected folders."
- "Require a plan update for subsystem-wide changes."

Implementation approach:
- Extend existing policy engine with a new category `agent_behavior`.
- Each rule returns a severity and recommended action: `allow|warn|pause|block`.

## 6) Minimal Implementation Plan (non-breaking)

1. Add CLI `prompt` group with `state|rules|summary` commands (thin wrappers)
2. Add `agents.jsonl` writer (separate from `metrics.jsonl`)
3. Add checkpoint create/list/restore with protected path awareness
4. Add `agent_behavior` policy category and 2–3 default rules
5. Document usage in README with examples and short JSON snippets

All of the above can be added incrementally without changing current behavior. Start with read-only surfaces (`prompt state`, summaries), then layer on writes (checkpoints) and behavior policies.

## Feature Flags

Controlled via `ai_onboard.json` (all default to true for backward compatibility):
```json
{
  "features": {
    "prompt_bridge": true,
    "intent_checks": true,
    "checkpoints": true
  },
  "metaPolicies": {
    "MAX_DELETE_LINES": 200,
    "MAX_REFACTOR_FILES": 12,
    "REQUIRES_TEST_COVERAGE": true
  }
}
```
