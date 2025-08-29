# AI Onboard (Drop-in)

Run:
    python -m ai_onboard analyze
    python -m ai_onboard charter
    python -m ai_onboard plan
    python -m ai_onboard align
    python -m ai_onboard validate
    python -m ai_onboard kaizen
    python -m ai_onboard metrics
    python -m ai_onboard cleanup --dry-run
    # Agent-facing (feature-flagged):
    python -m ai_onboard prompt state|rules|summary|propose
    python -m ai_onboard checkpoint create|list|restore

## Safe Cleanup

The `cleanup` command safely removes non-critical files while never touching:
- `ai_onboard/` directory (the system itself)
- `.ai_onboard/` directory (project data)
- `.git/` directory (version control)
- Configuration files (`pyproject.toml`, `requirements.txt`, etc.)
- Documentation (`README*`, `AGENTS.md`, etc.)
- CI/CD files (`.github/`, etc.)

Usage:
```
# See what would be deleted (safe)
python -m ai_onboard cleanup --dry-run

# Actually clean up (with confirmation)
python -m ai_onboard cleanup

# Force cleanup without confirmation
python -m ai_onboard cleanup --force

# Create backup before cleanup
python -m ai_onboard cleanup --backup
```

Guidance for AI coding agents: see `AGENTS.md`.

## AI Agents: Fit & Roadmap

This project can act as a meta-tool for AI coding agents (Cursor, Codex, GPTs, etc.) by providing shared context, safety rails, and a structured improvement loop.

- Where it fits well:
  - Memory: `ai_onboard.json` + JSONL telemetry gives agents persistent state across runs.
  - Safety: Protected paths + safe cleanup reduce destructive actions.
  - Guardrails: Policy engine + validation runtime enforce pre-flight sanity checks.
  - Kaizen: Plan/Do/Check/Act loop scaffolds self-correction instead of blind retries.

- Gaps to close for agents:
  - Intent checks: Meta-policy for "should the agent do this task now?".
  - Prompt feedback: Feed telemetry/state back into agent prompts, not just logs.
  - Nonlinear work: Lightweight checkpoints/rollback and branch comparison for approaches.
  - Cross-model context: Shared memory usable by different models/context windows.

- Roadmap highlights:
  - Prompt API: Thin interface to query current state and preflight rules before edits.
  - Checkpoints: Snapshot/rollback hooks with simple metadata and safety triggers.
  - Cross-agent telemetry: Unified JSONL schema with `agent_id`, `model`, `task`, `outcome`.
  - Summarization: Brief vs. full context views for small/large context models.
  - Meta-policy: Rules like 'pause if touching >N files' or 'require tests for big diffs'.

See `docs/agent-integration.md` for a concrete proposal with schemas and suggested commands.

Quick examples:
- Get state JSON for prompts: `python -m ai_onboard prompt state`
- Preflight rules for a path: `python -m ai_onboard prompt rules --path src/ --change "{\"lines_deleted\":120}"`
- Propose an action and get decision: `python -m ai_onboard prompt propose --diff "{\"files_changed\":[\"a.py\",\"b.py\"],\"lines_deleted\":200,\"has_tests\":false,\"subsystems\":[\"core\",\"ui\"]}"`
- Create scoped checkpoint: `python -m ai_onboard checkpoint create --scope "src/**/*.py" --reason "pre-refactor"`

PowerShell tip: assign JSON to a variable to avoid quoting issues.
```
$diff = '{"files_changed":["a.py","b.py"],"lines_deleted":200,"has_tests":false,"subsystems":["core","ui"]}'
python -m ai_onboard prompt propose --diff $diff
```

### Feature Flags

Set in `ai_onboard.json` (defaults are true):
```
{
  "features": {"prompt_bridge": true, "intent_checks": true, "checkpoints": true},
  "metaPolicies": {"MAX_DELETE_LINES": 200, "MAX_REFACTOR_FILES": 12, "REQUIRES_TEST_COVERAGE": true}
}
```

## Changelog

- v0.2.0
  - feat(agent): Prompt bridge (state|rules|summary|propose)
  - feat(agent): Intent checks + meta-policy thresholds
  - feat(agent): Checkpoints (create/list/restore)
  - feat(agent): Cross-agent telemetry stream
  - feat(agent): Model-aware summarization outputs
  - fix(cli): Cleanup output readability
  - docs: Agent integration design + examples

- v0.1.3
  - feat(kaizen): Learn per-rule fault yield and average time from telemetry
  - feat(kaizen): Use learned stats to order rules and skip stable ones
  - docs: Document Kaizen learning behavior

- v0.1.2
  - feat(cleanup): Add safe cleanup system that never deletes critical files
  - feat(cleanup): Add dry-run mode and backup capabilities
  - feat(cleanup): Comprehensive protection of ai_onboard system and project files

- v0.1.1
  - feat(core): Harden telemetry, add readers, wire optimizer to metrics
  - fix(report): Correct formatting and robustness in progress tracker
  - chore(cli): Clean CLI description strings and version bump output
  - chore: Add .gitignore; ignore build artifacts and untrack egg-info

- v0.1.0
  - Initial version

