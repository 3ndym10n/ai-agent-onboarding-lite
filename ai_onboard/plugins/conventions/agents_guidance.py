import os
from typing import Any, Dict, List

from ...core.issue import Issue
from ...core.registry import register


class AgentsGuidancePresent:
    name = "repo.agents_guidance_present"

    def run(self, paths: List[str], ctx: Dict[str, Any]):
        root = ctx["root"]
        issues: List[Issue] = []

        agents_md = os.path.join(root, "AGENTS.md")
        readme_md = os.path.join(root, "README.md")
        cursorrules = os.path.join(root, ".cursorrules")

        if not os.path.exists(agents_md):
            issues.append(
                Issue(
                    "AGENTS_GUIDE_MISSING",
                    "warn",
                    "AGENTS.md missing (add guidance for AI coding agents)",
                    agents_md,
                    confidence=0.9,
                )
            )

        # Ensure README references AGENTS.md so humans / agents see it early
        try:
            readme_text = open(readme_md, "r", encoding="utf - 8").read()
        except Exception:
            readme_text = ""
        if "AGENTS.md" not in readme_text:
            issues.append(
                Issue(
                    "AGENTS_GUIDE_UNREFERENCED",
                    "info",
                    "README should link to AGENTS.md",
                    readme_md,
                    confidence=0.7,
                )
            )

        # Optional: nudge to add Cursor rule file if using Cursor
        if not os.path.exists(cursorrules):
            issues.append(
                Issue(
                    "CURSOR_RULES_ABSENT",
                    "info",
                    "Optional: add .cursorrules for Cursor users to ingest policies",
                    cursorrules,
                    confidence=0.4,
                )
            )

        return issues


def _register():
    register("library_module", "python", AgentsGuidancePresent())


_register()
