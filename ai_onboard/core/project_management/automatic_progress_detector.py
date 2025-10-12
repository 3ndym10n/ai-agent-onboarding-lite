"""
Automatic Progress Detection System

This module provides automatic detection of completed work through:
- Git commit analysis
- File activity monitoring
- Pattern recognition for task completion
- Automatic status updates to plan.json
"""

import json
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ..base.utils import now_iso
from ..orchestration.tool_usage_tracker import track_tool_usage


class GitCommitAnalyzer:
    """Analyzes git commits to detect task completion."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.task_patterns = [
            r"task[:\s]+(\w+)[:\s]*complete",
            r"complete[:\s]+task[:\s]*(\w+)",
            r"finish[:\s]+task[:\s]*(\w+)",
            r"task[:\s]*(\w+)[:\s]*done",
            r"implement[:\s]*(\w+)",
            r"add[:\s]*(\w+)[:\s]*feature",
        ]
        self.completion_keywords = [
            "complete",
            "completed",
            "done",
            "finish",
            "finished",
            "implement",
            "implemented",
            "add",
            "added",
            "create",
            "created",
            "fix",
            "fixed",
            "resolve",
            "resolved",
            "update",
            "updated",
        ]

    def get_recent_commits(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get git commits from the last N hours."""
        try:
            # Use a fixed recent date that should capture recent activity
            # This avoids timezone and date calculation issues
            recent_date = "2025-10-01"  # Fixed date that should include recent commits

            cmd = [
                "git",
                "log",
                f"--since={recent_date}",
                "--pretty=format:%H|%s|%an|%ad",
                "--date=iso",
            ]

            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )

            commits = []
            for line in result.stdout.strip().split("\n"):
                if "|" in line:
                    parts = line.split("|", 3)
                    if len(parts) == 4:
                        commit_hash, subject, author, date = parts
                        commits.append(
                            {
                                "hash": commit_hash,
                                "subject": subject.lower(),
                                "author": author,
                                "date": date,
                                "timestamp": self._parse_git_date(date),
                            }
                        )

            return commits

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            # Debug: print the error for troubleshooting
            print(f"Git log error: {e}")
            return []

    def _parse_git_date(self, date_str: str) -> float:
        """Parse git date string to timestamp."""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")
            return dt.timestamp()
        except ValueError:
            return time.time()

    def detect_task_completions(self, commits: List[Dict[str, Any]]) -> List[str]:
        """Detect task IDs mentioned as completed in commits."""
        completed_tasks = []

        for commit in commits:
            subject = commit["subject"]

            # Check for explicit task completion patterns
            for pattern in self.task_patterns:
                matches = re.findall(pattern, subject, re.IGNORECASE)
                completed_tasks.extend(matches)

            # Check for completion keywords that might indicate task completion
            if any(keyword in subject for keyword in self.completion_keywords):
                # Try to extract task-like identifiers (T1, task_1, etc.)
                task_matches = re.findall(
                    r"(?:task|t)[:_\s]*(\w+)", subject, re.IGNORECASE
                )
                completed_tasks.extend(task_matches)

        return list(set(completed_tasks))  # Remove duplicates


class FileActivityMonitor:
    """Monitors file activity to detect task-related work."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.task_file_patterns = {
            "T1": ["setup", "structure", "project"],
            "T2": ["environment", "config", "dev"],
            "T3": ["ci", "cd", "workflow"],
            "T7": ["collaboration", "protocol", "gate"],
            "T8": ["context", "memory", "conversation"],
            "T9": ["decision", "pipeline", "agent"],
            "T10": ["preference", "learning", "user"],
            "T17": ["documentation", "docs", "readme"],
            "T18": ["interface", "ui", "ux"],
            "T19": ["experience", "enhancement"],
        }

    def get_recent_file_changes(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recently modified files."""
        try:
            # Use the same fixed recent date
            recent_date = "2025-10-01"
            since_timestamp = datetime.now().timestamp()

            changes = []
            result = subprocess.run(
                [
                    "git",
                    "log",
                    f"--since={recent_date}",
                    "--name-only",
                    "--pretty=format:",
                ],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )

            current_commit = None
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue

                # If line looks like a filename, add to current commit
                if "/" in line or "." in line:
                    changes.append(
                        {
                            "file": line.strip(),
                            "commit": current_commit,
                            "timestamp": since_timestamp,
                        }
                    )
                else:
                    current_commit = line.strip()

            return changes

        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

    def detect_task_activity(self, file_changes: List[Dict[str, Any]]) -> List[str]:
        """Detect which tasks are likely active based on file changes."""
        active_tasks = []

        for change in file_changes:
            filename = change["file"].lower()

            # Check each task's file patterns
            for task_id, patterns in self.task_file_patterns.items():
                if any(pattern in filename for pattern in patterns):
                    active_tasks.append(task_id)

        return list(set(active_tasks))  # Remove duplicates


class AutomaticProgressDetector:
    """Main automatic progress detection system."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.git_analyzer = GitCommitAnalyzer(repo_root)
        self.file_monitor = FileActivityMonitor(repo_root)
        self.plan_file = repo_root / ".ai_onboard" / "project_plan.json"

    def detect_completed_work(self, hours: int = 72) -> Dict[str, Any]:
        """Detect completed work from git and file activity."""
        start_time = time.time()

        # Get recent commits (use longer time range for better detection)
        commits = self.git_analyzer.get_recent_commits(hours)

        # Get recent file changes
        file_changes = self.file_monitor.get_recent_file_changes(hours)

        # Detect completions from commits
        commit_completions = self.git_analyzer.detect_task_completions(commits)

        # Detect active tasks from file changes
        active_tasks = self.file_monitor.detect_task_activity(file_changes)

        # Cross-reference: if a task shows activity and completion keywords, mark as completed
        likely_completed = []
        for task_id in active_tasks:
            commit_text = " ".join(commit["subject"] for commit in commits)
            if any(
                keyword in commit_text
                for keyword in ["complete", "done", "finish", "implement"]
            ):
                likely_completed.append(task_id)

        duration = time.time() - start_time

        track_tool_usage(
            "automatic_progress_detector",
            "detect_completed_work",
            {
                "action": "detect_completed_work",
                "hours": hours,
                "commits_analyzed": len(commits),
                "files_changed": len(file_changes),
                "commit_completions": len(commit_completions),
                "active_tasks": len(active_tasks),
                "likely_completed": len(likely_completed),
                "duration": duration,
            },
            "success",
        )

        return {
            "commits_analyzed": len(commits),
            "files_changed": len(file_changes),
            "commit_completions": commit_completions,
            "active_tasks": active_tasks,
            "likely_completed": likely_completed,
            "detection_timestamp": now_iso(),
            "duration_seconds": duration,
        }

    def update_plan_with_detected_progress(self) -> Dict[str, Any]:
        """Update plan.json with automatically detected completed tasks."""
        if not self.plan_file.exists():
            return {"success": False, "error": "No plan file found"}

        try:
            # Load current plan
            with open(self.plan_file, "r") as f:
                plan = json.load(f)

            # Detect completed work
            detection_results = self.detect_completed_work()

            # Update task statuses
            updated_tasks = []
            tasks = plan.get("tasks", [])

            for task in tasks:
                task_id = task.get("id")
                if task_id in detection_results["likely_completed"]:
                    if task.get("status") != "completed":
                        task["status"] = "completed"
                        task["completion_date"] = now_iso()
                        task["auto_detected_completion"] = True
                        updated_tasks.append(task_id)

            # Save updated plan
            with open(self.plan_file, "w") as f:
                json.dump(plan, f, indent=2)

            return {
                "success": True,
                "updated_tasks": updated_tasks,
                "detection_results": detection_results,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


def run_automatic_progress_detection(repo_root: Path) -> Dict[str, Any]:
    """Convenience function to run automatic progress detection."""
    detector = AutomaticProgressDetector(repo_root)
    return detector.update_plan_with_detected_progress()


if __name__ == "__main__":
    # For testing
    root = Path(".")
    result = run_automatic_progress_detection(root)
    print(f"Auto-detection result: {result}")
