#!/usr / bin / env python3
# mypy: ignore - errors
"""
Generate changelog for releases.

This script generates a changelog based on git commits and conventional commit messages.
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def run_git_command(command: List[str]) -> str:
    """Run a git command and return the output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}")
        return ""


def get_commits_since_last_tag() -> List[Dict[str, str]]:
    """Get commits since the last tag."""
    # Get the last tag
    last_tag = run_git_command(["git", "describe", "--tags", "--abbrev = 0"])

    if not last_tag:
        # If no tags exist, get all commits
        commits = run_git_command(["git", "log", "--oneline", "--no - merges"])
    else:
        # Get commits since last tag
        commits = run_git_command(
            ["git", "log", f"{last_tag}..HEAD", "--oneline", "--no - merges"]
        )

    if not commits:
        return []

    # Parse commits
    commit_list = []
    for line in commits.split("\n"):
        if line.strip():
            parts = line.split(" ", 1)
            if len(parts) == 2:
                commit_list.append({"hash": parts[0], "message": parts[1]})

    return commit_list


def categorize_commits(
    commits: List[Dict[str, str]],
) -> Dict[str, List[Dict[str, str]]]:
    """Categorize commits by type."""
    categories = {
        "feat": [],
        "fix": [],
        "docs": [],
        "style": [],
        "refactor": [],
        "test": [],
        "chore": [],
        "other": [],
    }

    for commit in commits:
        message = commit["message"]

        # Check for conventional commit format
        if ":" in message:
            type_part = message.split(":", 1)[0].lower()
            if type_part in categories:
                categories[type_part].append(commit)
            else:
                categories["other"].append(commit)
        else:
            categories["other"].append(commit)

    return categories


def generate_changelog(categories: Dict[str, List[Dict[str, str]]]) -> str:
    """Generate changelog content."""
    changelog = []

    # Header
    changelog.append("# Changelog")
    changelog.append("")
    changelog.append(f"Generated on {datetime.now().strftime('%Y -% m -% d %H:%M:%S')}")
    changelog.append("")

    # Features
    if categories["feat"]:
        changelog.append("## 🚀 Features")
        changelog.append("")
        for commit in categories["feat"]:
            message = commit["message"]
            if ":" in message:
                message = message.split(":", 1)[1].strip()
            changelog.append(f"- {message}")
        changelog.append("")

    # Bug Fixes
    if categories["fix"]:
        changelog.append("## 🐛 Bug Fixes")
        changelog.append("")
        for commit in categories["fix"]:
            message = commit["message"]
            if ":" in message:
                message = message.split(":", 1)[1].strip()
            changelog.append(f"- {message}")
        changelog.append("")

    # Documentation
    if categories["docs"]:
        changelog.append("## 📚 Documentation")
        changelog.append("")
        for commit in categories["docs"]:
            message = commit["message"]
            if ":" in message:
                message = message.split(":", 1)[1].strip()
            changelog.append(f"- {message}")
        changelog.append("")

    # Refactoring
    if categories["refactor"]:
        changelog.append("## 🔧 Refactoring")
        changelog.append("")
        for commit in categories["refactor"]:
            message = commit["message"]
            if ":" in message:
                message = message.split(":", 1)[1].strip()
            changelog.append(f"- {message}")
        changelog.append("")

    # Tests
    if categories["test"]:
        changelog.append("## 🧪 Tests")
        changelog.append("")
        for commit in categories["test"]:
            message = commit["message"]
            if ":" in message:
                message = message.split(":", 1)[1].strip()
            changelog.append(f"- {message}")
        changelog.append("")

    # Other changes
    if categories["other"]:
        changelog.append("## 📝 Other Changes")
        changelog.append("")
        for commit in categories["other"]:
            changelog.append(f"- {commit['message']}")
        changelog.append("")

    # Footer
    changelog.append("---")
    changelog.append("")
    changelog.append(
        "For more details, see the [full commit history](https://github.com / 3ndym10n / ai - agent - onboarding - lite / commits / main)."
    )

    return "\n".join(changelog)


def main():
    """Main function."""
    print("Generating changelog...")

    # Get commits since last tag
    commits = get_commits_since_last_tag()

    if not commits:
        print("No commits found since last tag.")
        return

    print(f"Found {len(commits)} commits since last tag.")

    # Categorize commits
    categories = categorize_commits(commits)

    # Generate changelog
    changelog_content = generate_changelog(categories)

    # Write to file
    changelog_path = Path("CHANGELOG.md")
    changelog_path.write_text(changelog_content, encoding="utf - 8")

    print(f"Changelog generated: {changelog_path}")
    print(f"Categories: {', '.join([k for k, v in categories.items() if v])}")


if __name__ == "__main__":
    main()
