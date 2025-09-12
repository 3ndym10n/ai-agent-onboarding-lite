# CLI Reference - Quick Command Guide

This is a quick reference for AI Onboard CLI commands, extracted from the main README for easy access.

## Core Commands

```bash
# Essential workflow
python -m ai_onboard analyze      # Analyze current project state
python -m ai_onboard charter      # Create or update project charter
python -m ai_onboard plan         # Generate development roadmap
python -m ai_onboard align        # Check alignment with project vision
python -m ai_onboard validate     # Pre-flight validation of changes
python -m ai_onboard kaizen       # Continuous improvement cycle
python -m ai_onboard metrics      # View project metrics and progress

# Safe cleanup
python -m ai_onboard cleanup --dry-run  # See what would be cleaned
python -m ai_onboard cleanup            # Clean with confirmation
python -m ai_onboard cleanup --force    # Force cleanup without confirmation
python -m ai_onboard cleanup --backup   # Create backup before cleanup

# Agent-facing commands (feature-flagged)
python -m ai_onboard prompt state|rules|summary|propose
python -m ai_onboard checkpoint create|list|restore
```

## Alignment Preview (Dry Run)

Use the intelligent alignment preview to assess confidence and ambiguities before executing changes. This is read-only and writes a small report.

```bash
python -m ai_onboard align --preview
# -> prints JSON and writes .ai_onboard/alignment_report.json
```

The report includes: `confidence` (0-1), `decision` (proceed|quick_confirm|clarify), component scores, and detected ambiguities. Thresholds are configured in `ai_onboard/policies/alignment_rules.yaml`.

## Advanced AI Agent Commands

```bash
# Get state JSON for prompts
python -m ai_onboard prompt state

# Preflight rules for a path
python -m ai_onboard prompt rules --path src/ --change '{"lines_deleted":120}'

# Propose an action and get decision
python -m ai_onboard prompt propose --diff '{"files_changed":["a.py","b.py"],"lines_deleted":200,"has_tests":false,"subsystems":["core","ui"]}'

# Create scoped checkpoint
python -m ai_onboard checkpoint create --scope "src/**/*.py" --reason "pre-refactor"
```

## PowerShell Tips

Assign JSON to a variable to avoid quoting issues:
```powershell
$diff = '{"files_changed":["a.py","b.py"],"lines_deleted":200,"has_tests":false,"subsystems":["core","ui"]}'
python -m ai_onboard prompt propose --diff $diff
```

## Feature Flags

Set in `ai_onboard.json` (defaults are true):
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

For complete documentation, see the main [README.md](../README.md) or [docs/user-guide/](user-guide/).
