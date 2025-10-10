# Vision-First Onboarding Flow

AI Onboard now enforces a three-stage onboarding sequence before full functionality is unlocked. This keeps agents aligned with the project vision and avoids premature tooling runs.

## Stage 1 — Create the Charter

1. Capture the project vision with the guided charter command:
   ```bash
   python -m ai_onboard charter --interrogate
   ```
2. Alternatively, bootstrap placeholder artifacts with:
   ```bash
   python -m ai_onboard quickstart
   ```

Either option produces `.ai_onboard/charter.json`.

## Stage 2 — Analyze the Current State

Generate the baseline repository snapshot:
```bash
python -m ai_onboard analyze
```

This command creates `.ai_onboard/state.json` and unlocks the final stage.

## Stage 3 — Build the Project Plan

Use the plan generator to produce `.ai_onboard/project_plan.json`:
```bash
python -m ai_onboard plan --analyze-codebase
```

Once the plan exists, the CLI, agent adapter, and system integrator will allow the full command set.

## What Happens If You Skip a Stage?

- The CLI blocks disallowed commands and prints the exact next step.
- The agent adapter returns a `block` assessment with onboarding guidance.
- The system integrator marks operations as `pending_onboarding` until the plan is ready.

Use `python -m ai_onboard doctor` at any time to see the current stage and the recommended next command.
