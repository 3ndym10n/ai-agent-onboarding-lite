"""
Derive a simple roadmap from analysis.json + optional goal text.
"""

import json
from pathlib import Path
from typing import Any, Dict


def build(root: Path, goal: str = "") -> Dict[str, Any]:
    ai_dir = root / ".ai_onboard"
    ai_dir.mkdir(parents=True, exist_ok=True)
    analysis_path = ai_dir / "analysis.json"
    analysis: Dict[str, Any] = {}
    if analysis_path.exists():
        analysis = json.loads(analysis_path.read_text(encoding="utf - 8"))

    tasks: List[Dict[str, Any]] = []

    # Seed tasks from quick wins
    for qw in analysis.get("quick_wins", []):
        tasks.append(
            {
                "id": f"qw-{len(tasks) + 1}",
                "title": qw,
                "type": "quick_win",
                "refs": ["analysis.quick_wins"],
                "status": "pending",
            }
        )

    # Basic hygiene tasks
    if (root / "README.md").exists() is False:
        tasks.append(
            {
                "id": f"doc-{len(tasks) + 1}",
                "title": "Create README.md with setup and run steps",
                "type": "doc",
                "refs": ["files.README.md"],
                "status": "pending",
            }
        )

    roadmap = {
        "goal": goal,
        "generated_from": "analysis_lite",
        "tasks": tasks,
    }

    (ai_dir / "roadmap.json").write_text(
        json.dumps(roadmap, indent=2), encoding="utf - 8"
    )
    return roadmap
