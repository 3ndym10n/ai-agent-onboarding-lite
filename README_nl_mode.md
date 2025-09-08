# Natural-Language (NL) Mode

Prompt-first workflow for Cursor/LLM agents. No CLI required.

Key pieces:
- `ai_onboard/core/cursor_rules.py`: system prompt + logging helpers
- `.ai_onboard/agent_profile.json`: focus include/exclude for the agent
- Logs: `.ai_onboard/conversation.jsonl`, `.ai_onboard/decisions.jsonl`, `.ai_onboard/obs/*.md`

Quick start:
1) Print system prompt for your agent
```bash
python examples/cursor_prompt_loop.py --print-prompt
```
2) Log an observation and a decision
```bash
python examples/cursor_prompt_loop.py --observe "Found README with goals A/B" --rule readme
python examples/cursor_prompt_loop.py --decide allow --why "docs sufficient to proceed"
```
3) Check status/checklist
```bash
python examples/cursor_prompt_loop.py --status
```

Agent profile (optional):
- Edit `.ai_onboard/agent_profile.json` to constrain what the agent reads.
- The system prompt embeds Include/Exclude lists to reduce distraction.

Safety:
- The NL system only writes under `.ai_onboard/`.
- Use `README_ai_onboard.md` and `AGENTS.md` for repo rules/guardrails.



