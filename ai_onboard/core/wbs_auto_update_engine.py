"""
WBS Auto-Update Engine (T4.11) - Automatically updates WBS when tasks complete.

This module provides automatic detection and updating of task completion status
in the Work Breakdown Structure (WBS), ensuring the project plan stays current
without manual intervention.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from . import utils
from .tool_usage_tracker import track_tool_usage
from .wbs_synchronization_engine import get_wbs_sync_engine


class WBSAutoUpdateEngine:
    """
    Engine for automatically updating WBS task completion status.

    This engine monitors various sources of task completion evidence and
    automatically updates the WBS to reflect current project status.
    """

    def __init__(self, root: Path):
        self.root = root
        self.project_plan_path = root / ".ai_onboard" / "project_plan.json"
        self.completion_log_path = root / ".ai_onboard" / "wbs_auto_updates.jsonl"
        self.backup_dir = root / ".ai_onboard" / "wbs_backups"

        # Ensure directories exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Enhanced completion detection sources
        self.completion_sources = [
            self._check_git_commits,  # NEW: Git commit analysis
            self._check_code_quality_metrics,  # NEW: Quality metrics integration
            self._check_code_implementation,
            self._check_test_coverage,
            self._check_documentation,
            self._check_cli_commands,
            self._check_module_structure,
            self._check_continuous_improvement,  # NEW: CI system integration
        ]

        # Track recently updated tasks to avoid redundant checks
        self.recent_updates: Set[str] = set()
        self.update_cooldown = 300  # 5 minutes cooldown between checks

    def auto_update_wbs(self, force: bool = False) -> Dict[str, Any]:
        """
        Automatically scan for completed tasks and update WBS.

        Args:
            force: If True, ignore cooldown and check all tasks

        Returns:
            Update results with statistics
        """
        track_tool_usage(
            "wbs_auto_update_engine",
            "project_management",
            {"action": "auto_update_wbs", "force": force},
            "success",
        )

        start_time = time.time()

        # Load current WBS
        wbs_data = self._load_wbs()
        if not wbs_data:
            return {
                "success": False,
                "error": "Could not load WBS data",
                "updated_tasks": 0,
                "duration": time.time() - start_time,
            }

        # Get all tasks that might need updating
        candidate_tasks = self._get_candidate_tasks(wbs_data, force)
        updated_count = 0
        checked_count = 0
        results = []

        for task_id, task_data in candidate_tasks.items():
            checked_count += 1

            # Check if task appears to be completed
            completion_result = self._assess_task_completion(task_id, task_data)

            if completion_result["completed"]:
                # Update the task status in WBS
                update_result = self._update_task_completion(
                    wbs_data, task_id, task_data, completion_result
                )

                if update_result["success"]:
                    updated_count += 1
                    results.append(
                        {
                            "task_id": task_id,
                            "status": "updated",
                            "evidence": completion_result["evidence"],
                            "confidence": completion_result["confidence"],
                        }
                    )

                    # Record the update
                    self._record_update_event(
                        {
                            "task_id": task_id,
                            "action": "auto_completed",
                            "evidence": completion_result["evidence"],
                            "confidence": completion_result["confidence"],
                            "timestamp": time.time(),
                        }
                    )
                else:
                    results.append(
                        {
                            "task_id": task_id,
                            "status": "update_failed",
                            "error": update_result.get("error"),
                        }
                    )

        # Save updated WBS if any changes were made
        if updated_count > 0:
            save_result = self._save_wbs(wbs_data)
            if not save_result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to save WBS: {save_result.get('error')}",
                    "updated_tasks": 0,
                    "checked_tasks": checked_count,
                    "duration": time.time() - start_time,
                }

        return {
            "success": True,
            "updated_tasks": updated_count,
            "checked_tasks": checked_count,
            "results": results,
            "duration": time.time() - start_time,
        }

    def _get_candidate_tasks(
        self, wbs_data: Dict[str, Any], force: bool = False
    ) -> Dict[str, Dict]:
        """Get tasks that are candidates for auto-completion checking."""
        candidates = {}

        for phase_key, phase_data in wbs_data.get(
            "work_breakdown_structure", {}
        ).items():
            if not phase_key.endswith(".0"):  # Skip main phase entries
                continue

            subtasks = phase_data.get("subtasks", {})
            for subtask_key, subtask_data in subtasks.items():
                task_id = subtask_key  # e.g., "4.11"

                # Skip if already completed
                if subtask_data.get("status") == "completed":
                    continue

                # Skip recently updated tasks unless forced
                if not force and self._is_recently_updated(task_id):
                    continue

                candidates[task_id] = subtask_data

        return candidates

    def _assess_task_completion(
        self, task_id: str, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess whether a task appears to be completed based on multiple evidence sources.
        """
        task_name = task_data.get("name", "")
        description = task_data.get("description", "")

        total_confidence = 0.0
        evidence_sources = []
        completion_reasons = []

        # Check each completion source
        for check_func in self.completion_sources:
            try:
                result = check_func(task_id, task_name, description)
                if result["confidence"] > 0:
                    total_confidence += result["confidence"]
                    evidence_sources.append(result["source"])
                    if result.get("reason"):
                        completion_reasons.append(result["reason"])
            except Exception as e:
                # Log but don't fail the assessment
                print(f"Warning: Completion check failed for {task_id}: {e}")

        # Normalize confidence (average of contributing sources)
        final_confidence = total_confidence / max(len(evidence_sources), 1)

        # Require high confidence and multiple evidence sources for auto-completion
        is_completed = (
            final_confidence >= 0.8  # High confidence threshold
            and len(evidence_sources) >= 2  # Multiple evidence sources
        )

        return {
            "completed": is_completed,
            "confidence": final_confidence,
            "evidence": evidence_sources,
            "reasons": completion_reasons,
        }

    def _check_code_implementation(
        self, task_id: str, task_name: str, description: str
    ) -> Dict[str, Any]:
        """Check for code implementation evidence."""
        confidence = 0.0
        reason = None

        # Look for implementation patterns in task name/description
        impl_indicators = [
            "implement",
            "create",
            "build",
            "develop",
            "add",
            "module",
            "class",
            "function",
        ]

        text_to_check = f"{task_name} {description}".lower()

        if any(indicator in text_to_check for indicator in impl_indicators):
            # Check if corresponding code files exist
            if self._check_implementation_files(task_name):
                confidence = 0.6
                reason = "Implementation files found"

        return {
            "source": "code_implementation",
            "confidence": confidence,
            "reason": reason,
        }

    def _check_test_coverage(
        self, task_id: str, task_name: str, description: str
    ) -> Dict[str, Any]:
        """Check for test coverage evidence."""
        confidence = 0.0
        reason = None

        # Look for test-related keywords
        test_indicators = ["test", "testing", "coverage", "validate", "verify"]

        text_to_check = f"{task_name} {description}".lower()

        if any(indicator in text_to_check for indicator in test_indicators):
            # Check if tests exist for this functionality
            if self._check_test_files(task_name):
                confidence = 0.5
                reason = "Test files found"

        return {"source": "test_coverage", "confidence": confidence, "reason": reason}

    def _check_documentation(
        self, task_id: str, task_name: str, description: str
    ) -> Dict[str, Any]:
        """Check for documentation evidence."""
        confidence = 0.0
        reason = None

        # Look for documentation keywords
        doc_indicators = ["document", "guide", "tutorial", "readme", "api"]

        text_to_check = f"{task_name} {description}".lower()

        if any(indicator in text_to_check for indicator in doc_indicators):
            # Check if documentation files exist
            if self._check_documentation_files(task_name):
                confidence = 0.7
                reason = "Documentation files found"

        return {"source": "documentation", "confidence": confidence, "reason": reason}

    def _check_cli_commands(
        self, task_id: str, task_name: str, description: str
    ) -> Dict[str, Any]:
        """Check for CLI command implementation evidence."""
        confidence = 0.0
        reason = None

        # Look for CLI-related keywords
        cli_indicators = ["cli", "command", "subcommand", "parser", "argparse"]

        text_to_check = f"{task_name} {description}".lower()

        if any(indicator in text_to_check for indicator in cli_indicators):
            # Check if CLI code exists
            if self._check_cli_implementation(task_name):
                confidence = 0.6
                reason = "CLI implementation found"

        return {"source": "cli_commands", "confidence": confidence, "reason": reason}

    def _check_module_structure(
        self, task_id: str, task_name: str, description: str
    ) -> Dict[str, Any]:
        """Check for module/file structure evidence."""
        confidence = 0.0
        reason = None

        # Look for structural keywords
        struct_indicators = ["module", "structure", "organization", "file", "directory"]

        text_to_check = f"{task_name} {description}".lower()

        if any(indicator in text_to_check for indicator in struct_indicators):
            # Check if structural changes exist
            if self._check_structural_changes(task_name):
                confidence = 0.4
                reason = "Structural changes detected"

        return {
            "source": "module_structure",
            "confidence": confidence,
            "reason": reason,
        }

    def _check_git_commits(
        self, task_id: str, task_name: str, description: str
    ) -> Dict[str, Any]:
        """Check git commits for task completion evidence."""
        confidence = 0.0
        reason = None

        try:
            import subprocess

            # Extract key words from task name for commit message analysis
            task_words = [word.lower() for word in task_name.split() if len(word) > 3]

            if not task_words:
                return {"source": "git_commits", "confidence": 0.0, "reason": None}

            # Get recent commit messages (last 20 commits)
            result = subprocess.run(
                ["git", "log", "--oneline", "-20", "--no-merges"],
                capture_output=True,
                text=True,
                cwd=self.root,
                timeout=10,
            )

            if result.returncode == 0:
                commit_messages = result.stdout.lower()

                # Check if task keywords appear in recent commits
                matching_commits = 0
                for word in task_words:
                    if word in commit_messages:
                        matching_commits += 1

                if matching_commits > 0:
                    # Higher confidence for more matching words
                    confidence = min(0.8, matching_commits * 0.3)
                    reason = f"Found {matching_commits} related commits"

                    # Bonus confidence for completion keywords in commits
                    completion_keywords = [
                        "complete",
                        "finish",
                        "done",
                        "implement",
                        "add",
                        "fix",
                    ]
                    for keyword in completion_keywords:
                        if keyword in commit_messages:
                            confidence = min(0.9, confidence + 0.1)
                            break

        except Exception as e:
            # Git not available or other error - don't fail the assessment
            pass

        return {"source": "git_commits", "confidence": confidence, "reason": reason}

    def _check_code_quality_metrics(
        self, task_id: str, task_name: str, description: str
    ) -> Dict[str, Any]:
        """Check code quality metrics for task completion evidence."""
        confidence = 0.0
        reason = None

        try:
            # Try to get quality metrics from continuous improvement system
            from .continuous_improvement_system import get_continuous_improvement_system

            ci_system = get_continuous_improvement_system(self.root)
            quality_data = ci_system.get_latest_quality_metrics()

            if quality_data and quality_data.get("success"):
                metrics = quality_data.get("metrics", {})

                # Check if quality metrics indicate task completion
                code_quality_score = metrics.get("code_quality_score", 0)
                test_coverage = metrics.get("test_coverage", 0)

                # Higher quality scores suggest task completion
                if code_quality_score > 0.7:
                    confidence += 0.4
                if test_coverage > 0.6:
                    confidence += 0.3

                if confidence > 0:
                    reason = f"Quality metrics: {code_quality_score:.1f} quality, {test_coverage:.1f} coverage"

        except Exception:
            # CI system not available - try alternative quality checks
            try:
                # Check for recent quality improvements in validation reports
                validation_path = self.root / ".ai_onboard" / "validation_report.json"
                if validation_path.exists():
                    validation_data = utils.read_json(validation_path, default={})

                    issues = validation_data.get("issues", [])
                    high_issues = [i for i in issues if i.get("severity") == "high"]

                    # Fewer high-severity issues suggests task completion
                    if len(issues) > 0:
                        issue_ratio = len(high_issues) / len(issues)
                        if issue_ratio < 0.2:  # Less than 20% high-severity issues
                            confidence = 0.5
                            reason = f"Low issue ratio: {len(high_issues)}/{len(issues)} high-severity"

            except Exception:
                pass

        return {
            "source": "code_quality_metrics",
            "confidence": confidence,
            "reason": reason,
        }

    def _check_continuous_improvement(
        self, task_id: str, task_name: str, description: str
    ) -> Dict[str, Any]:
        """Check continuous improvement system for task completion evidence."""
        confidence = 0.0
        reason = None

        try:
            from .continuous_improvement_system import get_continuous_improvement_system

            ci_system = get_continuous_improvement_system(self.root)

            # Check if task appears in recent improvement cycles
            improvement_data = ci_system.get_recent_improvements(limit=10)

            if improvement_data:
                task_words = [
                    word.lower() for word in task_name.split() if len(word) > 3
                ]

                for improvement in improvement_data:
                    improvement_text = str(improvement).lower()

                    matching_words = sum(
                        1 for word in task_words if word in improvement_text
                    )
                    if matching_words > 0:
                        confidence += min(0.6, matching_words * 0.2)
                        reason = f"Found in {matching_words} improvement entries"
                        break

        except Exception:
            # CI system not available - check for kaizen logs
            try:
                kaizen_path = self.root / ".ai_onboard" / "kaizen_history.jsonl"
                if kaizen_path.exists():
                    with open(kaizen_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()[-10:]  # Check last 10 entries

                    task_words = [
                        word.lower() for word in task_name.split() if len(word) > 3
                    ]

                    for line in lines:
                        try:
                            entry = json.loads(line.strip())
                            entry_text = str(entry).lower()

                            matching_words = sum(
                                1 for word in task_words if word in entry_text
                            )
                            if matching_words > 0:
                                confidence = min(0.5, matching_words * 0.2)
                                reason = f"Found in kaizen history"
                                break
                        except:
                            pass

            except Exception:
                pass

        return {
            "source": "continuous_improvement",
            "confidence": confidence,
            "reason": reason,
        }

    def _check_implementation_files(self, task_name: str) -> bool:
        """Check if implementation files exist for the given task."""
        # Simple heuristic: look for files that might correspond to the task
        task_words = task_name.lower().split()
        key_words = [word for word in task_words if len(word) > 3]

        if not key_words:
            return False

        # Check if any Python files contain these keywords in their names
        try:
            for py_file in self.root.rglob("*.py"):
                file_name = py_file.name.lower()
                if any(keyword in file_name for keyword in key_words):
                    return True
        except Exception:
            pass

        return False

    def _check_test_files(self, task_name: str) -> bool:
        """Check if test files exist for the given task."""
        # Look for test files that might correspond to the task
        task_words = task_name.lower().split()
        key_words = [word for word in task_words if len(word) > 3]

        try:
            for test_file in self.root.rglob("test_*.py"):
                file_name = test_file.name.lower()
                if any(keyword in file_name for keyword in key_words):
                    return True
        except Exception:
            pass

        return False

    def _check_documentation_files(self, task_name: str) -> bool:
        """Check if documentation files exist for the given task."""
        # Look for documentation files
        doc_files = ["README.md", "docs", "guides", "tutorials"]
        doc_patterns = ["README", "GUIDE", "DOC", "TUTORIAL"]

        try:
            for doc_file in self.root.rglob("*"):
                if doc_file.is_file():
                    file_name = doc_file.name.upper()
                    if any(pattern in file_name for pattern in doc_patterns):
                        return True
        except Exception:
            pass

        return False

    def _check_cli_implementation(self, task_name: str) -> bool:
        """Check if CLI implementation exists for the given task."""
        # Look for CLI-related files and code
        cli_files = ["commands", "cli", "argparse", "subparser"]

        try:
            for py_file in self.root.rglob("*.py"):
                file_name = py_file.name.lower()
                if any(cli_word in file_name for cli_word in cli_files):
                    return True
        except Exception:
            pass

        return False

    def _check_structural_changes(self, task_name: str) -> bool:
        """Check if structural changes exist for the given task."""
        # This is a basic check - look for recent file changes
        # In a real implementation, this would check git history or file timestamps
        return True  # Placeholder - assume structural changes exist

    def _update_task_completion(
        self,
        wbs_data: Dict[str, Any],
        task_id: str,
        task_data: Dict[str, Any],
        completion_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a task's completion status in the WBS."""
        try:
            # Get synchronization engine
            sync_engine = get_wbs_sync_engine(self.root)

            # Find the task in WBS and prepare update
            phase_id = f"{task_id.split('.')[0]}.0"

            if phase_id in wbs_data.get("work_breakdown_structure", {}):
                phase = wbs_data["work_breakdown_structure"][phase_id]
                if "subtasks" in phase and task_id in phase["subtasks"]:
                    # Prepare the update for synchronization
                    updates = {
                        "work_breakdown_structure": {
                            phase_id: {
                                "subtasks": {
                                    task_id: {
                                        "status": "completed",
                                        "completed_at": time.time(),
                                        "completion_evidence": completion_result[
                                            "evidence"
                                        ],
                                        "completion_confidence": completion_result[
                                            "confidence"
                                        ],
                                    }
                                }
                            }
                        }
                    }

                    # Apply update through sync engine
                    sync_result = sync_engine.update_wbs_data(
                        updates, "wbs_auto_update_engine"
                    )

                    if sync_result["success"]:
                        # NEW: Trigger dependency cascade updates
                        cascade_result = self._trigger_dependency_cascade(task_id)

                        return {
                            "success": True,
                            "affected_views": sync_result.get("affected_views", []),
                            "cascade_updates": cascade_result.get(
                                "triggered_tasks", []
                            ),
                        }

                    return {
                        "success": False,
                        "error": f"Sync update failed: {sync_result.get('error')}",
                    }

            return {"success": False, "error": f"Task {task_id} not found in WBS"}

        except Exception as e:
            return {"success": False, "error": f"Failed to update task: {str(e)}"}

    def _load_wbs(self) -> Optional[Dict[str, Any]]:
        """Load the current WBS data."""
        try:
            if self.project_plan_path.exists():
                return utils.read_json(self.project_plan_path, default=None)
        except Exception as e:
            print(f"Warning: Failed to load WBS: {e}")
        return None

    def _save_wbs(self, wbs_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save updated WBS data with backup."""
        try:
            # Create backup
            backup_path = self.backup_dir / f"wbs_backup_{int(time.time())}.json"
            if self.project_plan_path.exists():
                import shutil

                shutil.copy2(self.project_plan_path, backup_path)

            # Save updated WBS
            utils.write_json(self.project_plan_path, wbs_data)

            return {"success": True}

        except Exception as e:
            return {"success": False, "error": f"Failed to save WBS: {str(e)}"}

    def _record_update_event(self, event_data: Dict[str, Any]) -> None:
        """Record an auto-update event to the log."""
        try:
            with open(self.completion_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event_data, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Warning: Failed to record update event: {e}")

    def _is_recently_updated(self, task_id: str) -> bool:
        """Check if a task was recently updated to avoid redundant checks."""
        if task_id in self.recent_updates:
            return True

        # Check recent log entries
        try:
            if self.completion_log_path.exists():
                with open(self.completion_log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-10:]  # Check last 10 updates

                cutoff_time = time.time() - self.update_cooldown
                for line in lines:
                    try:
                        event = json.loads(line.strip())
                        if (
                            event.get("task_id") == task_id
                            and event.get("timestamp", 0) > cutoff_time
                        ):
                            self.recent_updates.add(task_id)
                            return True
                    except:
                        pass
        except Exception:
            pass

        return False

    def _trigger_dependency_cascade(self, completed_task_id: str) -> Dict[str, Any]:
        """Trigger updates for tasks that depend on the completed task."""
        triggered_tasks = []

        try:
            # Load current project plan to check dependencies
            wbs_data = self._load_wbs()
            if not wbs_data:
                return {"triggered_tasks": []}

            # Look for tasks that have this task as a dependency
            dependencies = wbs_data.get("dependencies", [])
            dependent_tasks = [
                dep["to"]
                for dep in dependencies
                if dep.get("from") == completed_task_id
            ]

            # For each dependent task, check if all its dependencies are now complete
            for task_id in dependent_tasks:
                if self._all_dependencies_complete(task_id, wbs_data):
                    # Mark task as ready to start
                    self._update_task_status(task_id, "ready", wbs_data)
                    triggered_tasks.append(
                        {
                            "task_id": task_id,
                            "status": "ready",
                            "reason": f"All dependencies complete (including {completed_task_id})",
                        }
                    )

                    # Send notification through user experience system
                    self._send_task_ready_notification(task_id)

            return {"triggered_tasks": triggered_tasks}

        except Exception as e:
            print(f"Warning: Dependency cascade failed: {e}")
            return {"triggered_tasks": []}

    def _all_dependencies_complete(
        self, task_id: str, wbs_data: Dict[str, Any]
    ) -> bool:
        """Check if all dependencies for a task are completed."""
        try:
            dependencies = wbs_data.get("dependencies", [])
            task_deps = [
                dep["from"] for dep in dependencies if dep.get("to") == task_id
            ]

            if not task_deps:
                return True  # No dependencies

            # Check each dependency
            for dep_task_id in task_deps:
                if not self._is_task_completed(dep_task_id, wbs_data):
                    return False

            return True

        except Exception:
            return False

    def _is_task_completed(self, task_id: str, wbs_data: Dict[str, Any]) -> bool:
        """Check if a specific task is completed."""
        try:
            phase_id = f"{task_id.split('.')[0]}.0"
            phase = wbs_data.get("work_breakdown_structure", {}).get(phase_id, {})
            subtasks = phase.get("subtasks", {})

            if task_id in subtasks:
                return subtasks[task_id].get("status") == "completed"

        except Exception:
            pass
        return False

    def _update_task_status(
        self, task_id: str, status: str, wbs_data: Dict[str, Any]
    ) -> None:
        """Update a task's status in the WBS data."""
        try:
            phase_id = f"{task_id.split('.')[0]}.0"
            if phase_id in wbs_data.get("work_breakdown_structure", {}):
                phase = wbs_data["work_breakdown_structure"][phase_id]
                if "subtasks" in phase and task_id in phase["subtasks"]:
                    phase["subtasks"][task_id]["status"] = status
                    if status == "ready":
                        phase["subtasks"][task_id]["ready_at"] = time.time()
        except Exception as e:
            print(f"Warning: Failed to update task status: {e}")

    def _send_task_ready_notification(self, task_id: str) -> None:
        """Send notification that a task is ready to start."""
        try:
            from .user_experience_system import get_user_experience_system

            ux_system = get_user_experience_system(self.root)

            # Record this as a smart suggestion
            suggestion_data = {
                "type": "task_ready",
                "task_id": task_id,
                "message": f"Task {task_id} is ready to start - all dependencies completed",
                "priority": "high",
                "timestamp": time.time(),
            }

            # This would integrate with your UX system's notification mechanism
            # For now, we'll log it for visibility
            self._record_update_event(
                {
                    "action": "task_ready_notification",
                    "task_id": task_id,
                    "timestamp": time.time(),
                }
            )

        except Exception as e:
            print(f"Warning: Failed to send task ready notification: {e}")

    def get_project_health_score(self) -> Dict[str, Any]:
        """Calculate overall project health based on WBS status."""
        try:
            wbs_data = self._load_wbs()
            if not wbs_data:
                return {"health_score": 0.0, "status": "unknown"}

            wbs = wbs_data.get("work_breakdown_structure", {})
            total_tasks = 0
            completed_tasks = 0
            ready_tasks = 0
            blocked_tasks = 0

            for phase_key, phase_data in wbs.items():
                if not phase_key.endswith(".0"):
                    continue

                subtasks = phase_data.get("subtasks", {})
                for task_id, task_data in subtasks.items():
                    total_tasks += 1
                    status = task_data.get("status", "pending")

                    if status == "completed":
                        completed_tasks += 1
                    elif status == "ready":
                        ready_tasks += 1
                    elif status == "blocked":
                        blocked_tasks += 1

            if total_tasks == 0:
                return {"health_score": 1.0, "status": "no_tasks"}

            completion_rate = completed_tasks / total_tasks
            readiness_rate = ready_tasks / total_tasks
            block_rate = blocked_tasks / total_tasks

            # Calculate health score (0.0 to 1.0)
            health_score = (
                completion_rate * 0.6  # 60% weight for completion
                + readiness_rate * 0.3  # 30% weight for readiness
                + (1 - block_rate) * 0.1  # 10% weight for low blocks
            )

            return {
                "health_score": round(health_score, 2),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "ready_tasks": ready_tasks,
                "blocked_tasks": blocked_tasks,
                "completion_rate": round(completion_rate, 2),
                "status": (
                    "healthy"
                    if health_score > 0.7
                    else "needs_attention" if health_score > 0.4 else "critical"
                ),
            }

        except Exception as e:
            return {"health_score": 0.0, "status": "error", "error": str(e)}

    def get_update_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent auto-update history."""
        try:
            if not self.completion_log_path.exists():
                return []

            with open(self.completion_log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            events = []
            for line in lines[-limit:]:  # Get last N events
                try:
                    events.append(json.loads(line.strip()))
                except:
                    pass

            return events

        except Exception as e:
            print(f"Warning: Failed to read update history: {e}")
            return []


def run_wbs_auto_update(root: Path = None, force: bool = False) -> Dict[str, Any]:
    """
    Convenience function to run WBS auto-update.

    Args:
        root: Project root directory
        force: Force update all tasks regardless of cooldown

    Returns:
        Update results
    """
    if root is None:
        root = Path.cwd()

    engine = WBSAutoUpdateEngine(root)
    return engine.auto_update_wbs(force=force)
