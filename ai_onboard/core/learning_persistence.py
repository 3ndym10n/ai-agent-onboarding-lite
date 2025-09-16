"""
Learning Persistence System (T4.9) - Persistent storage and retrieval of learned patterns.

This module provides persistent storage for learned patterns that:
- Saves error patterns and prevention rules to disk
- Loads learned patterns on system startup
- Maintains learning history across sessions
- Provides APIs for pattern retrieval and updates
- Ensures learning continuity between AI agent sessions
"""

import json
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from . import utils

if TYPE_CHECKING:
    from .pattern_recognition_system import PatternRecognitionSystem  # noqa: F401


class LearningPersistenceManager:
    """Manages persistence of learned patterns and knowledge."""

    def __init__(self, root: Path):
        self.root = root
        self.learning_dir = root / ".ai_onboard" / "learning"
        self.patterns_backup_file = self.learning_dir / "patterns_backup.json"
        self.learning_history_file = self.learning_dir / "learning_history.jsonl"
        self.learning_stats_file = self.learning_dir / "learning_stats.json"

        # Learning statistics
        self.stats = {
            "patterns_learned": 0,
            "patterns_applied": 0,
            "errors_prevented": 0,
            "learning_sessions": 0,
            "last_learning_update": 0,
            "total_learning_events": 0,
        }

        self._ensure_directories()
        self._load_stats()

    def _ensure_directories(self) -> None:
        """Ensure learning directories exist."""
        self.learning_dir.mkdir(parents=True, exist_ok=True)

    def _load_stats(self) -> None:
        """Load learning statistics from disk."""
        try:
            if self.learning_stats_file.exists():
                loaded_stats = utils.read_json(self.learning_stats_file, default={})
                self.stats.update(loaded_stats)
        except Exception:
            # Start with default stats if loading fails
            pass

    def _save_stats(self) -> None:
        """Save learning statistics to disk."""
        try:
            utils.write_json(self.learning_stats_file, self.stats)
        except Exception as e:
            print(f"Warning: Failed to save learning stats: {e}")

    def save_pattern_backup(self, pattern_system) -> bool:
        """
        Save a backup of all learned patterns.

        Args:
            pattern_system: The pattern recognition system to backup

        Returns:
            True if backup successful, False otherwise
        """
        try:
            # Get all patterns as serializable data
            patterns_data = {}
            for pattern_id, pattern in pattern_system.patterns.items():
                patterns_data[pattern_id] = {
                    "pattern_id": pattern.pattern_id,
                    "pattern_type": pattern.pattern_type,
                    "signature": pattern.signature,
                    "description": pattern.description,
                    "examples": pattern.examples[-5:],  # Keep only recent examples
                    "frequency": pattern.frequency,
                    "first_seen": pattern.first_seen,
                    "last_seen": pattern.last_seen,
                    "confidence": pattern.confidence,
                    "prevention_rules": pattern.prevention_rules,
                    "related_patterns": list(pattern.related_patterns),
                }

            backup_data = {
                "timestamp": time.time(),
                "pattern_count": len(patterns_data),
                "patterns": patterns_data,
                "stats": self.stats.copy(),
            }

            utils.write_json(self.patterns_backup_file, backup_data)

            # Update stats
            self.stats["last_learning_update"] = time.time()
            self._save_stats()

            return True

        except Exception as e:
            print(f"Error saving pattern backup: {e}")
            return False

    def load_pattern_backup(self, pattern_system) -> bool:
        """
        Load patterns from backup.

        Args:
            pattern_system: The pattern recognition system to restore to

        Returns:
            True if restore successful, False otherwise
        """
        try:
            if not self.patterns_backup_file.exists():
                return False

            backup_data = utils.read_json(self.patterns_backup_file, default={})

            if "patterns" not in backup_data:
                return False

            # Restore patterns
            patterns_restored = 0
            for pattern_id, pattern_data in backup_data["patterns"].items():
                from .pattern_recognition_system import ErrorPattern

                pattern = ErrorPattern(**pattern_data)
                pattern_system.patterns[pattern_id] = pattern
                patterns_restored += 1

            # Restore stats if available
            if "stats" in backup_data:
                self.stats.update(backup_data["stats"])
                self._save_stats()

            print(f"Restored {patterns_restored} patterns from backup")
            return True

        except Exception as e:
            print(f"Error loading pattern backup: {e}")
            return False

    def record_learning_event(
        self, event_type: str, event_data: Dict[str, Any]
    ) -> None:
        """
        Record a learning event to the history log.

        Args:
            event_type: Type of learning event ("pattern_learned", "pattern_applied", etc.)
            event_data: Event-specific data
        """
        try:
            event_record = {
                "timestamp": time.time(),
                "event_type": event_type,
                "event_data": event_data,
            }

            # Append to history file
            with open(self.learning_history_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event_record, ensure_ascii=False) + "\n")

            # Update stats
            self.stats["total_learning_events"] += 1
            if event_type == "pattern_learned":
                self.stats["patterns_learned"] += 1
            elif event_type == "pattern_applied":
                self.stats["patterns_applied"] += 1
            elif event_type == "error_prevented":
                self.stats["errors_prevented"] += 1

            self._save_stats()

        except Exception as e:
            print(f"Warning: Failed to record learning event: {e}")

    def get_learning_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent learning history.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of learning events (newest first)
        """
        try:
            events = []
            if self.learning_history_file.exists():
                with open(self.learning_history_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            events.append(json.loads(line.strip()))

            # Sort by timestamp (newest first) and limit
            events.sort(key=lambda x: x["timestamp"], reverse=True)
            return events[:limit]

        except Exception as e:
            print(f"Warning: Failed to load learning history: {e}")
            return []

    def get_learning_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive learning statistics.

        Returns:
            Dictionary with learning statistics
        """
        stats = self.stats.copy()

        # Add computed stats
        total_patterns = stats["patterns_learned"]
        total_applied = stats["patterns_applied"]
        total_prevented = stats["errors_prevented"]

        if total_patterns > 0:
            stats["pattern_utilization_rate"] = total_applied / total_patterns
        else:
            stats["pattern_utilization_rate"] = 0.0

        if total_applied > 0:
            stats["prevention_effectiveness"] = total_prevented / total_applied
        else:
            stats["prevention_effectiveness"] = 0.0

        # Add learning history summary
        history = self.get_learning_history(1000)  # Get last 1000 events
        event_types = {}
        for event in history:
            event_type = event["event_type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1

        stats["event_type_distribution"] = event_types
        stats["recent_activity"] = len(
            [e for e in history if e["timestamp"] > time.time() - 86400]
        )  # Last 24h

        return stats

    def export_learning_data(self, export_path: Path) -> bool:
        """
        Export all learning data for backup or analysis.

        Args:
            export_path: Path to export learning data to

        Returns:
            True if export successful, False otherwise
        """
        try:
            export_data = {
                "export_timestamp": time.time(),
                "learning_stats": self.get_learning_stats(),
                "learning_history": self.get_learning_history(
                    5000
                ),  # Export last 5000 events
            }

            # Include pattern backup if available
            if self.patterns_backup_file.exists():
                export_data["pattern_backup"] = utils.read_json(
                    self.patterns_backup_file, default={}
                )

            utils.write_json(export_path, export_data)
            return True

        except Exception as e:
            print(f"Error exporting learning data: {e}")
            return False

    def import_learning_data(self, import_path: Path) -> bool:
        """
        Import learning data from backup.

        Args:
            import_path: Path to import learning data from

        Returns:
            True if import successful, False otherwise
        """
        try:
            import_data = utils.read_json(import_path, default={})

            # Import stats
            if "learning_stats" in import_data:
                # Merge imported stats with current stats
                imported_stats = import_data["learning_stats"]
                for key, value in imported_stats.items():
                    if key not in [
                        "event_type_distribution",
                        "recent_activity",
                        "pattern_utilization_rate",
                        "prevention_effectiveness",
                    ]:
                        self.stats[key] = value

            # Import history events
            if "learning_history" in import_data:
                with open(self.learning_history_file, "a", encoding="utf-8") as f:
                    for event in import_data["learning_history"]:
                        f.write(json.dumps(event, ensure_ascii=False) + "\n")

            self._save_stats()
            return True

        except Exception as e:
            print(f"Error importing learning data: {e}")
            return False

    def cleanup_old_data(self, max_age_days: int = 90) -> int:
        """
        Clean up old learning data to prevent disk bloat.

        Args:
            max_age_days: Maximum age of data to keep

        Returns:
            Number of old records cleaned up
        """
        try:
            cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
            cleaned_count = 0

            # Clean up learning history
            if self.learning_history_file.exists():
                temp_file = self.learning_history_file.with_suffix(".tmp")

                with open(self.learning_history_file, "r", encoding="utf-8") as f_in:
                    with open(temp_file, "w", encoding="utf-8") as f_out:
                        for line in f_in:
                            if line.strip():
                                event = json.loads(line.strip())
                                if event["timestamp"] > cutoff_time:
                                    f_out.write(line)
                                else:
                                    cleaned_count += 1

                # Replace original file
                temp_file.replace(self.learning_history_file)

            return cleaned_count

        except Exception as e:
            print(f"Error cleaning up old learning data: {e}")
            return 0
