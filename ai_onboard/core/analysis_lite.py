"""
Lightweight repository analysis.

Produces .ai_onboard / analysis.json with:
- summary: counts, languages, important files
- risks: coarse heuristics
- quick_wins: simple actionable suggestions
"""

import json
from pathlib import Path
from typing import Any, Dict, List

LANG_EXT = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
}


def _list_files(root: Path) -> List[Path]:
    ignore_dirs = {
        ".git",
        "node_modules",
        "venv",
        ".venv",
        "dist",
        "build",
        "__pycache__",
    }
    files: List[Path] = []
    for p in root.rglob("*"):
        if p.is_dir():
            if p.name in ignore_dirs:
                # skip subtree
                continue
            else:
                continue
        files.append(p)
    return files


def run(root: Path) -> Dict[str, Any]:
    files = _list_files(root)
    counts: Dict[str, int] = {}
    lang_counts: Dict[str, int] = {}
    important: List[str] = []

    for f in files:
        suffix = f.suffix.lower()
        counts[suffix] = counts.get(suffix, 0) + 1
        if suffix in LANG_EXT:
            lang = LANG_EXT[suffix]
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

        if f.name in {
            "pyproject.toml",
            "package.json",
            "requirements.txt",
            "Dockerfile",
            "README.md",
        }:
            important.append(str(f.relative_to(root)))

    risks: List[str] = []
    if "python" in lang_counts and "pyproject.toml" not in {
        Path(p).name for p in important
    }:
        risks.append("Python project missing pyproject.toml")
    if (
        "javascript" in lang_counts
        and counts.get(".ts", 0) + counts.get(".tsx", 0) == 0
    ):
        risks.append("JS code without TypeScript")

    quick_wins: List[str] = []
    if (root / "README.md").exists() is False:
        quick_wins.append("Add README.md with setup and run instructions")
    if (root / ".gitignore").exists() is False:
        quick_wins.append("Add .gitignore appropriate for the stack")

    out: Dict[str, Any] = {
        "summary": {
            "total_files": len(files),
            "languages": lang_counts,
            "important_files": important,
        },
        "counts": counts,
        "risks": risks,
        "quick_wins": quick_wins,
    }

    ai_dir = root / ".ai_onboard"
    ai_dir.mkdir(parents=True, exist_ok=True)
    (ai_dir / "analysis.json").write_text(json.dumps(out, indent=2), encoding="utf - 8")
    return out
