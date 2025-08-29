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

