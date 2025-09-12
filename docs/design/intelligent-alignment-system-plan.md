## Intelligent Alignment System (IAS)

Purpose: Make the agent collaborative instead of robotic by aligning on vision/goals before execution, using confidence-based gates and ambiguity detection.

### Goals
- Keep velocity high while preventing unintended work
- Ask for input when confidence is low or ambiguity is present
- Separate “vision/feature choices” (human-led) from “implementation details” (agent-led)

### Principles
- Propose → Confirm → Execute
- Confidence-scored decisions with thresholds
- Holistic project assessment and benchmarking
- Minimal, targeted prompts (no dialog spam)

### Confidence Model (v1)
- Confidence ∈ [0,1] computed as a weighted blend:
  - Charter/vision completeness (w=0.25)
  - Policy alignment and prior confirmations (w=0.25)
  - Project context fit vs. similar projects (w=0.20)
  - Ambiguity/Conflict score inverted (w=0.20)
  - Change impact (scope/size) (w=0.10)
- Thresholds:
  - proceed ≥ 0.90 → execute
  - quick_confirm ∈ [0.75, 0.89] → single confirmation prompt
  - clarify < 0.75 → ask alignment questions before proceeding

### Gates (when to check-in)
- Discovery/vision parsed or changed
- New feature request or UI scope change
- Plan generation/update
- Structural edits (≥5 files or ≥200 LOC)
- Adding external dependency or making API/contract changes

### Ambiguity & Conflict Detection
- Missing required intent fields (targets, users, top outcomes)
- Conflicting priorities or mutually exclusive goals
- Unclear UI intent (e.g., “modern look” without tokens or patterns)
- Divergence between discovered code patterns and proposed architecture

### Outputs
- Alignment report: `.ai_onboard/alignment_report.json`
  - assumptions, detected conflicts/ambiguities, confidence, gates triggered, next actions

### CLI Preview (read-only)
- Command: `ai_onboard align preview`
- Behavior: compute confidence + produce alignment report; never edits code
- Optional flags: `--explain`, `--open-report`, `--format json|table`

### Collaboration Flow
1) Agent drafts assumptions and plan deltas
2) If confidence < proceed threshold, present a concise checklist for confirmation
3) Apply user feedback; recompute
4) Execute with guardrails; re-check when a gate is triggered

### Non-Goals (v1)
- No heavy ML; use rule- and score-based heuristics
- No automatic dependency installation without confirmation

### Rollback/Safety
- Default to PR or staged diff for edits touching gated areas
- Respect repository protected paths; refuse unsafe operations

### Future Work
- Learn user preferences over time
- Richer benchmarking catalog by domain
- UI assistant for multi-select confirmations
