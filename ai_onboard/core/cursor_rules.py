"""
Cursor Rule System: prompt-first workflow for Cursor/LLM agents.

Goals
- Provide a simple, NL-first checklist and guardrails as a single system prompt.
- Log observations and decisions to .ai_onboard/ as JSONL and human-readable files.
- Offer lightweight "next steps" based on what has been logged so far.

No external deps. Python 3.8+.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import alignment, prompt_bridge, utils

CONVO_FILE = ".ai_onboard/conversation.jsonl"
DECISIONS_FILE = ".ai_onboard/decisions.jsonl"
OBS_DIR = ".ai_onboard/obs"


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    utils.ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        f.write(utils.dumps_json(record) + "\n")


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    lines: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            lines.append(json.loads(line))
        except Exception:
            # If a line is malformed, skip it rather than failing the flow
            continue
    return lines


def record_observation(
    root: Path, rule_id: str, text: str, tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Record a free-form observation for a rule, both JSONL and a plain .md note."""
    rec: Dict[str, Any] = {
        "ts": utils.now_iso(),
        "rule": rule_id,
        "text": text,
        "tags": tags or [],
    }
    _append_jsonl(root / CONVO_FILE, {"type": "observation", **rec})
    # Also write a rolling markdown note for human browsing
    safe_rule = rule_id.replace("/", "-")
    md_path = root / OBS_DIR / f"{safe_rule}.md"
    utils.ensure_dir(md_path.parent)
    with md_path.open("a", encoding="utf-8") as f:
        f.write(f"[{rec['ts']}] {text}\n")
    return rec


def record_decision(
    root: Path, decision: str, rationale: str, meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Record a decision with rationale (allow/deny/clarify/quick_confirm/custom)."""
    rec: Dict[str, Any] = {
        "ts": utils.now_iso(),
        "decision": decision,
        "rationale": rationale,
        "meta": meta or {},
    }
    _append_jsonl(root / DECISIONS_FILE, rec)
    _append_jsonl(root / CONVO_FILE, {"type": "decision", **rec})
    return rec


@dataclass
class ChecklistItem:
    id: str
    label: str
    done: bool = False


def _compute_checklist(root: Path) -> List[ChecklistItem]:
    """Derive a checklist based on current repo state and recent decisions.

    This uses prompt_bridge summaries (read-only) and whether a manifest exists.
    """
    manifest_present = (root / "ai_onboard.json").exists()
    state = prompt_bridge.get_project_state(root)

    items: List[ChecklistItem] = [
        ChecklistItem("readme", "Scan README*, AGENTS.md, and project docs for intent"),
        ChecklistItem(
            "guardrails", "Confirm protected paths and safety policies are present"
        ),
        ChecklistItem("manifest", "Create or update ai_onboard.json (only if missing)"),
        ChecklistItem("summary", "Emit brief project summary for the model context"),
        ChecklistItem("ambiguities", "List ambiguities and top outcomes to clarify"),
        ChecklistItem("alignment_preview", "Run alignment preview (dry) and reflect"),
    ]

    # Mark as done based on current state
    if state.get("manifest_present"):
        for it in items:
            if it.id == "manifest":
                it.done = True
                break
    return items


def next_checklist(root: Path) -> List[Dict[str, Any]]:
    """Return the actionable checklist with done flags for consumers."""
    return [it.__dict__ for it in _compute_checklist(root)]


def load_agent_profile(root: Path) -> Dict[str, Any]:
    """Load optional agent profile that constrains what the agent focuses on.

    Format (.ai_onboard/agent_profile.json):
    {"include": ["paths..."], "exclude": ["globs..."]}
    """
    prof = utils.read_json(root / ".ai_onboard/agent_profile.json", default={}) or {}
    include = [p for p in (prof.get("include") or []) if isinstance(p, str)]
    exclude = [p for p in (prof.get("exclude") or []) if isinstance(p, str)]
    return {"include": include, "exclude": exclude}


def generate_system_prompt(root: Path) -> str:
    """Generate a single, compact system prompt for Cursor agents.

    The prompt asks the agent to:
    - Follow a fixed checklist
    - Log observations as JSONL and short Markdown notes
    - Avoid destructive actions; only write under .ai_onboard/
    - Summarize next steps after each turn
    """
    items = _compute_checklist(root)
    profile = load_agent_profile(root)
    checklist_lines = "\n".join(
        [f"- [{ 'x' if it.done else ' ' }] {it.label}" for it in items]
    )
    include_lines = (
        "\n".join([f"  - {p}" for p in profile.get("include", [])]) or "  - (none)"
    )
    exclude_lines = (
        "\n".join([f"  - {p}" for p in profile.get("exclude", [])]) or "  - (none)"
    )

    prompt = f"""
You are a repository guide operating in a prompt-only workflow. Do not run CLI commands.
Work strictly through reading files and writing logs under .ai_onboard/.

Operating rules:
- Never modify or delete protected paths; only write inside .ai_onboard/.
- For each step, write an observation via record_observation(). Keep notes short.
- When you believe a step is satisfied, write a decision with rationale.

Focus scope (agent_profile):
- Only open or summarize files that match Include patterns; ignore Exclude patterns.
- Include patterns:\n{include_lines}
- Exclude patterns:\n{exclude_lines}

Checklist:
{checklist_lines}

What to log per step:
- Scan docs: list key goals, constraints, unknowns (bullets)
- Guardrails: note presence of AGENTS.md, protected paths, meta-policies
- Manifest: if missing, propose minimal fields (name, topOutcomes) as JSON in notes
- Summary: produce a brief summary using prompt_bridge.summary logic (NL-only paraphrase)
- Ambiguities: enumerate concrete questions to unblock work
- Alignment preview: read .ai_onboard/alignment_report.json if present; otherwise infer risk areas

Output policy:
- After each action, update the checklist status in natural language and suggest the single next step.
- Keep each observation < 20 lines. Prefer bullets.
""".strip()
    return prompt


def status(root: Path) -> Dict[str, Any]:
    """Return compact status summary for UI or agents."""
    return {
        "ts": utils.now_iso(),
        "checklist": next_checklist(root),
        "manifest_present": (root / "ai_onboard.json").exists(),
        "last_metrics": prompt_bridge.get_project_state(root).get("last_metrics", {}),
        "suggested_next_actions": suggest_next_actions(root),
    }


def suggest_next_actions(root: Path) -> List[Dict[str, Any]]:
    """Compute minimal, non-invasive next actions the agent can take.

    Returns a small list of suggestions with rationale. Does not perform any action.
    """
    suggestions: List[Dict[str, Any]] = []

    # 1) Interrogation: if alignment confidence is low or many ambiguities
    prev = _read_json_safe(root / ".ai_onboard/alignment_report.json")
    conf = float(prev.get("confidence", 0.0)) if isinstance(prev, dict) else 0.0
    ambiguities = prev.get("ambiguities", []) if isinstance(prev, dict) else []
    if conf < 0.6 or (isinstance(ambiguities, list) and len(ambiguities) >= 2):
        suggestions.append(
            {
                "id": "interrogate",
                "label": "Start targeted interrogation to resolve key ambiguities",
                "why": f"confidence={conf} ambiguities={len(ambiguities)}",
            }
        )

    # 2) Alignment drift check: if no recent preview or time gap
    # Lightweight check: if report missing, suggest preview
    if not (root / ".ai_onboard/alignment_report.json").exists():
        suggestions.append(
            {
                "id": "alignment_preview",
                "label": "Run alignment preview (dry) and reflect",
                "why": "no prior alignment report",
            }
        )

    # 3) Plan update: if alignment is proceed/approved but plan missing
    plan_path = root / ".ai_onboard/plan.json"
    decision_log = root / ".ai_onboard/decision_log.jsonl"
    proceed = False
    if prev and isinstance(prev, dict) and prev.get("decision") == "proceed":
        proceed = True
    if decision_log.exists():
        for line in decision_log.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
            except Exception:
                continue
            if entry.get("decision") == "ALIGN" and entry.get("approved") is True:
                proceed = True
                break
    if proceed and not plan_path.exists():
        suggestions.append(
            {
                "id": "plan",
                "label": "Draft plan from charter and decisions",
                "why": "alignment indicates proceed but no plan.json",
            }
        )

    return suggestions


def _read_json_safe(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception:
        return {}
