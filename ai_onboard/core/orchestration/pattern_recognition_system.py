"""
Pattern Recognition System (T4.8) - Advanced error pattern detection and learning.

This module provides intelligent pattern recognition that:
- Analyzes error logs and user interactions for recurring patterns
- Identifies root causes and common failure modes
- Learns from successful vs unsuccessful patterns
- Learns from repeated errors and user behavior patterns
- Provides proactive error prevention recommendations
- Integrates with learning persistence and automatic error prevention
- Discovers patterns in CLI usage and command sequences
"""

import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..base import utils
from ..continuous_improvement.learning_persistence import LearningPersistenceManager
from .tool_usage_tracker import track_tool_usage


@dataclass
class ErrorPattern:
    """Represents a recognized error pattern."""

    pattern_id: str
    pattern_type: str  # "cli_error", "styling_error", "import_error", etc.
    signature: str  # Unique identifier for this pattern
    description: str
    examples: List[Dict[str, Any]] = field(default_factory=list)
    frequency: int = 0
    first_seen: float = 0
    last_seen: float = 0
    confidence: float = 0.0
    prevention_rules: List[str] = field(default_factory=list)
    related_patterns: Set[str] = field(default_factory=set)


@dataclass
class CLIPattern:
    """Represents a learned CLI usage pattern."""

    pattern_id: str
    command_sequence: List[str]  # Sequence of commands that work well together
    success_rate: float  # Percentage of successful executions
    frequency: int  # How often this pattern occurs
    context: Dict[str, Any]  # Context when this pattern works (time, user, etc.)
    first_seen: float
    last_seen: float
    recommendations: List[str] = field(default_factory=list)


@dataclass
class BehaviorPattern:
    """Represents a learned user behavior pattern."""

    pattern_id: str
    pattern_type: str  # "error_recovery", "successful_workflow", "preference_pattern"
    description: str
    frequency: int
    confidence: float
    triggers: List[str]  # What triggers this behavior
    outcomes: List[str]  # What typically happens
    recommendations: List[str] = field(default_factory=list)
    first_seen: float = 0
    last_seen: float = 0


@dataclass
class PatternMatch:
    """A match of an error pattern."""

    pattern_id: str
    confidence: float
    matched_elements: Dict[str, Any]
    prevention_suggestions: List[str]
    timestamp: float


class PatternRecognitionSystem:
    """Advanced pattern recognition for error analysis and prevention."""

    def __init__(self, root: Path):
        self.root = root
        self.patterns_dir = root / ".ai_onboard" / "patterns"
        self.patterns_file = self.patterns_dir / "error_patterns.json"
        self.cli_patterns_file = self.patterns_dir / "cli_patterns.json"
        self.behavior_patterns_file = self.patterns_dir / "behavior_patterns.json"

        # Pattern collections
        self.patterns: Dict[str, ErrorPattern] = {}
        self.cli_patterns: Dict[str, CLIPattern] = {}
        self.behavior_patterns: Dict[str, BehaviorPattern] = {}

        # Pattern learning state
        self.command_history: List[Dict[str, Any]] = []
        self.error_clusters: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.success_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        self.persistence = LearningPersistenceManager(root)
        # Increment learning sessions counter on initialization
        self.persistence.increment_learning_sessions()
        track_tool_usage(
            "learning_persistence", "ai_system", {"action": "initialize"}, "success"
        )

        # Pattern templates for common error types
        self.pattern_templates = {
            "cli_error": {
                "regex": r"(?i)(invalid choice|unrecognized arguments|error:|command not found)",
                "keywords": ["invalid", "unrecognized", "error", "failed", "not found"],
                "prevention": [
                    "Validate command arguments before execution",
                    "Check CLI syntax",
                ],
            },
            "styling_error": {
                "regex": r"(?i)(trailing whitespace|line too long|missing newline|indentation)",
                "keywords": [
                    "whitespace",
                    "indentation",
                    "newline",
                    "length",
                    "style",
                    "line",
                    "long",
                ],
                "prevention": [
                    "Run code formatting tools",
                    "Configure editor auto-format",
                ],
            },
            "import_error": {
                "regex": r"(?i)(import error|module not found|no module named)",
                "keywords": ["import", "module", "not found", "error"],
                "prevention": [
                    "Check import paths",
                    "Verify package installation",
                    "Update requirements.txt",
                ],
            },
            "type_error": {
                "regex": r"(?i)(type error|attribute error|none type)",
                "keywords": ["type", "attribute", "none", "error"],
                "prevention": ["Add type hints", "Use type checking tools"],
            },
        }

        self._load_patterns()

    def _load_patterns(self) -> None:
        """Load persisted patterns (error, CLI, and behavior patterns)."""
        try:
            # Try to load from persistence manager backup first
            backup_loaded = self.persistence.load_pattern_backup(self)

            # Always load individual pattern files as fallback/supplement
            # (backup might not contain all pattern types)
            self._load_error_patterns()
            self._load_cli_patterns()
            self._load_behavior_patterns()

            if backup_loaded:
                track_tool_usage(
                    "learning_persistence",
                    "ai_system",
                    {"action": "load_backup", "result": "success"},
                    "success",
                )
            else:
                track_tool_usage(
                    "learning_persistence",
                    "ai_system",
                    {"action": "load_backup", "result": "fallback_to_files"},
                    "success",
                )
        except Exception as e:
            # If loading fails, start with empty patterns
            self.patterns = {}
            self.cli_patterns = {}
            self.behavior_patterns = {}

        # Ensure patterns directory exists
        self.patterns_dir.mkdir(parents=True, exist_ok=True)

    def _load_error_patterns(self) -> None:
        """Load error patterns from file."""
        if self.patterns_file.exists():
            data = utils.read_json(self.patterns_file, default={})
            for pattern_id, pattern_data in data.items():
                pattern = ErrorPattern(**pattern_data)
                self.patterns[pattern_id] = pattern

    def _load_cli_patterns(self) -> None:
        """Load CLI patterns from file."""
        if self.cli_patterns_file.exists():
            data = utils.read_json(self.cli_patterns_file, default={})
            for pattern_id, pattern_data in data.items():
                pattern = CLIPattern(**pattern_data)
                self.cli_patterns[pattern_id] = pattern

    def _load_behavior_patterns(self) -> None:
        """Load behavior patterns from file."""
        if self.behavior_patterns_file.exists():
            data = utils.read_json(self.behavior_patterns_file, default={})
            for pattern_id, pattern_data in data.items():
                pattern = BehaviorPattern(**pattern_data)
                self.behavior_patterns[pattern_id] = pattern

    def _save_patterns(self) -> None:
        """Save all patterns (error, CLI, behavior) to disk."""
        try:
            # Save backup through persistence manager
            self.persistence.save_pattern_backup(self)
            track_tool_usage(
                "learning_persistence",
                "ai_system",
                {"action": "save_backup", "patterns_count": len(self.patterns)},
                "success",
            )

            # Save error patterns
            self._save_error_patterns()
            # Save CLI patterns
            self._save_cli_patterns()
            # Save behavior patterns
            self._save_behavior_patterns()

        except Exception as e:
            # Log error but don't crash
            print(f"Warning: Failed to save patterns: {e}")

    def _save_error_patterns(self) -> None:
        """Save error patterns to disk."""
        patterns_data = {}
        for pattern_id, pattern in self.patterns.items():
            patterns_data[pattern_id] = {
                "pattern_id": pattern.pattern_id,
                "pattern_type": pattern.pattern_type,
                "signature": pattern.signature,
                "description": pattern.description,
                "examples": pattern.examples[-10:],  # Keep last 10 examples
                "frequency": pattern.frequency,
                "first_seen": pattern.first_seen,
                "last_seen": pattern.last_seen,
                "confidence": pattern.confidence,
                "prevention_rules": pattern.prevention_rules,
                "related_patterns": list(pattern.related_patterns),
            }
        utils.write_json(self.patterns_file, patterns_data)

    def _save_cli_patterns(self) -> None:
        """Save CLI patterns to disk."""
        patterns_data = {}
        for pattern_id, pattern in self.cli_patterns.items():
            patterns_data[pattern_id] = {
                "pattern_id": pattern.pattern_id,
                "command_sequence": pattern.command_sequence,
                "success_rate": pattern.success_rate,
                "frequency": pattern.frequency,
                "context": pattern.context,
                "first_seen": pattern.first_seen,
                "last_seen": pattern.last_seen,
                "recommendations": pattern.recommendations,
            }
        utils.write_json(self.cli_patterns_file, patterns_data)

    def _save_behavior_patterns(self) -> None:
        """Save behavior patterns to disk."""
        patterns_data = {}
        for pattern_id, pattern in self.behavior_patterns.items():
            patterns_data[pattern_id] = {
                "pattern_id": pattern.pattern_id,
                "pattern_type": pattern.pattern_type,
                "description": pattern.description,
                "frequency": pattern.frequency,
                "confidence": pattern.confidence,
                "triggers": pattern.triggers,
                "outcomes": pattern.outcomes,
                "recommendations": pattern.recommendations,
                "first_seen": pattern.first_seen,
                "last_seen": pattern.last_seen,
            }
        utils.write_json(self.behavior_patterns_file, patterns_data)

    def analyze_error(self, error_data: Dict[str, Any]) -> PatternMatch:
        """
        Analyze an error and find matching patterns.

        Args:
            error_data: Error information from error monitor

        Returns:
            PatternMatch with best matching pattern and suggestions
        """
        track_tool_usage(
            "pattern_recognition_system",
            "ai_system",
            {"action": "analyze_error", "error_type": error_data.get("type")},
            "success",
        )

        error_type = error_data.get("type", "")
        error_message = error_data.get("message", "")
        error_traceback = error_data.get("traceback", "")

        # Combine all error text for analysis
        error_text = f"{error_type} {error_message} {error_traceback}"

        best_match = None
        best_confidence = 0.0

        # Check against existing patterns
        for pattern in self.patterns.values():
            confidence = self._calculate_pattern_match(pattern, error_text, error_data)
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = pattern

        # If good match found, update the existing pattern
        if best_confidence >= 0.6 and best_match:
            self.update_pattern(best_match.pattern_id, error_data)

        # If no good match found, try to create new pattern
        elif best_confidence < 0.6:
            new_pattern = self._create_pattern_from_error(error_data)
            if new_pattern:
                self.patterns[new_pattern.pattern_id] = new_pattern
                self._save_patterns()

                # Record learning event
                self.persistence.record_learning_event(
                    "pattern_learned",
                    {
                        "pattern_id": new_pattern.pattern_id,
                        "pattern_type": new_pattern.pattern_type,
                        "signature": new_pattern.signature,
                        "confidence": new_pattern.confidence,
                        "error_type": error_data.get("type", "unknown"),
                        "error_message": error_data.get("message", "")[:100],
                    },
                )
                track_tool_usage(
                    "learning_persistence",
                    "ai_system",
                    {
                        "action": "record_learning_event",
                        "event_type": "pattern_learned",
                        "pattern_id": new_pattern.pattern_id,
                    },
                    "success",
                )

                best_match = new_pattern
                best_confidence = 0.7  # New patterns get moderate confidence

        if best_match:
            # Record that this pattern was applied
            self.persistence.record_pattern_applied(
                best_match.pattern_id,
                {"confidence": best_confidence, "error_type": error_type},
            )

            return PatternMatch(
                pattern_id=best_match.pattern_id,
                confidence=best_confidence,
                matched_elements={
                    "pattern_type": best_match.pattern_type,
                    "signature": best_match.signature,
                    "frequency": best_match.frequency,
                },
                prevention_suggestions=best_match.prevention_rules,
                timestamp=time.time(),
            )

        # Fallback for unmatched errors
        return PatternMatch(
            pattern_id="unknown_error",
            confidence=0.0,
            matched_elements={},
            prevention_suggestions=[
                "Review error details and add appropriate error handling"
            ],
            timestamp=time.time(),
        )

    def _calculate_pattern_match(
        self, pattern: ErrorPattern, error_text: str, error_data: Dict[str, Any]
    ) -> float:
        """Calculate how well an error matches a pattern."""
        confidence = 0.0

        # Check signature similarity - normalize both strings
        normalized_signature = pattern.signature.lower().replace(":", " ").strip()
        normalized_error = error_text.lower().strip()
        # More flexible matching - check if key parts match
        sig_parts = normalized_signature.split()
        error_parts = normalized_error.split()
        matching_parts = sum(1 for part in sig_parts if part in error_parts)
        if matching_parts >= len(sig_parts) * 0.8:  # 80% of signature parts match
            confidence += 0.4

        # Check keywords
        error_lower = error_text.lower()
        keyword_matches = 0
        template = self.pattern_templates.get(pattern.pattern_type, {})
        keywords = template.get("keywords", [])

        for keyword in keywords:
            if keyword.lower() in error_lower:
                keyword_matches += 1

        if keywords:
            confidence += 0.3 * (keyword_matches / len(keywords))

        # Check regex pattern
        regex_pattern = template.get("regex", "")
        if (
            regex_pattern
            and isinstance(regex_pattern, str)
            and re.search(regex_pattern, error_text, re.IGNORECASE)
        ):
            confidence += 0.3

        # Debug: print confidence calculation
        # print(f"DEBUG: confidence={confidence}, sig_match={normalized_signature in normalized_error}, "
        #       f"keywords={keyword_matches}/{len(keywords)}, "
        #       f"regex={bool(re.search(regex_pattern, error_text, re.IGNORECASE) if regex_pattern else False)}")

        return min(confidence, 1.0)

    def _create_pattern_from_error(
        self, error_data: Dict[str, Any]
    ) -> Optional[ErrorPattern]:
        """Create a new error pattern from an unrecognized error."""
        error_type = error_data.get("type", "")
        error_message = error_data.get("message", "")

        # Try to categorize the error
        pattern_type = self._categorize_error(error_type, error_message)

        if not pattern_type:
            return None

        # Create signature from error details
        signature = f"{error_type}: {error_message[:100]}"

        # Generate pattern ID
        pattern_id = f"pattern_{int(time.time())}_{hash(signature) % 10000}"

        # Get prevention rules from template
        template = self.pattern_templates.get(pattern_type, {})
        prevention_rules = list(
            template.get("prevention", ["Review error and implement appropriate fixes"])
        )

        pattern = ErrorPattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            signature=signature,
            description=f"Automatically detected {pattern_type} pattern",
            examples=[error_data],
            frequency=1,
            first_seen=time.time(),
            last_seen=time.time(),
            confidence=0.5,  # Start with moderate confidence
            prevention_rules=prevention_rules,
        )

        return pattern

    def _categorize_error(self, error_type: str, error_message: str) -> Optional[str]:
        """Categorize an error based on its type and message."""
        error_text = f"{error_type} {error_message}".lower()

        # Check against pattern templates
        for pattern_type, template in self.pattern_templates.items():
            regex = template.get("regex", "")
            keywords = template.get("keywords", [])

            # Check regex
            if (
                regex
                and isinstance(regex, str)
                and re.search(regex, error_text, re.IGNORECASE)
            ):
                return pattern_type

            # Check keywords
            keyword_matches = sum(1 for keyword in keywords if keyword in error_text)
            if keyword_matches >= len(keywords) * 0.5:  # 50% keyword match
                return pattern_type

        # Fallback categorization
        if "import" in error_text or "module" in error_text:
            return "import_error"
        elif "cli" in error_text or "command" in error_text or "argument" in error_text:
            return "cli_error"
        elif "style" in error_text or "format" in error_text:
            return "styling_error"
        elif "type" in error_text or "attribute" in error_text:
            return "type_error"

        return "unknown_error"

    def update_pattern(self, pattern_id: str, error_data: Dict[str, Any]) -> None:
        """Update an existing pattern with new error data."""
        track_tool_usage(
            "pattern_recognition_system",
            "ai_system",
            {"action": "update_pattern", "pattern_id": pattern_id},
            "success",
        )

        if pattern_id not in self.patterns:
            return

        pattern = self.patterns[pattern_id]

        # Update frequency and timestamps
        pattern.frequency += 1
        pattern.last_seen = time.time()

        # Add example (keep only recent ones)
        pattern.examples.append(error_data)
        pattern.examples = pattern.examples[-20:]  # Keep last 20 examples

        # Increase confidence with more occurrences
        old_confidence = pattern.confidence
        pattern.confidence = min(pattern.confidence + 0.05, 0.95)

        self._save_patterns()

        # Record learning event if confidence increased significantly
        if pattern.confidence - old_confidence > 0.01:
            self.persistence.record_learning_event(
                "pattern_strengthened",
                {
                    "pattern_id": pattern_id,
                    "pattern_type": pattern.pattern_type,
                    "old_confidence": old_confidence,
                    "new_confidence": pattern.confidence,
                    "frequency": pattern.frequency,
                    "error_type": error_data.get("type", "unknown"),
                },
            )
            track_tool_usage(
                "learning_persistence",
                "ai_system",
                {
                    "action": "record_learning_event",
                    "event_type": "pattern_strengthened",
                    "pattern_id": pattern_id,
                    "confidence_increase": pattern.confidence - old_confidence,
                },
                "success",
            )

    def get_all_patterns(self) -> List[Any]:
        """Get all patterns from all categories."""
        all_patterns: List[Any] = []
        all_patterns.extend(self.patterns.values())
        all_patterns.extend(self.cli_patterns.values())
        all_patterns.extend(self.behavior_patterns.values())
        return all_patterns

    def analyze_codebase_patterns(self, root: Path) -> Dict[str, Any]:
        """Analyze the entire codebase for error patterns."""

        # Find all Python files
        pattern = "*.py"
        python_files = []
        for file_path in root.rglob(pattern):
            if file_path.is_file() and not any(
                excl in str(file_path)
                for excl in ["__pycache__", ".git", "node_modules"]
            ):
                python_files.append(file_path)

        # Analyze each file for patterns
        analysis_results = {
            "files_analyzed": len(python_files),
            "patterns_found": 0,
            "pattern_types": {},
            "recommendations": [],
        }

        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Simple pattern analysis - look for common issues
                lines = content.split("\n")
                for line_num, line in enumerate(lines, 1):
                    # Check for long lines
                    if len(line) > 100:
                        error_data = {
                            "error_type": "styling_error",
                            "file": str(file_path.relative_to(root)),
                            "line": line_num,
                            "message": f"Line too long ({len(line)} characters)",
                        }
                        match = self.analyze_error(error_data)
                        if hasattr(match, "confidence") and match.confidence > 0.3:
                            patterns_found = analysis_results.get("patterns_found", 0)
                            if isinstance(patterns_found, int):
                                analysis_results["patterns_found"] = patterns_found + 1  # type: ignore[assignment]

            except Exception as e:
                continue  # Skip files that can't be read

        # Generate recommendations based on findings
        patterns_found = analysis_results.get("patterns_found", 0)
        if isinstance(patterns_found, int) and patterns_found > 0:
            recommendations = analysis_results.get("recommendations", [])
            if isinstance(recommendations, list):
                recommendations.append("Consider running code formatting tools")
                recommendations.append("Review coding standards compliance")

        return analysis_results

    def get_pattern_stats(self) -> Dict[str, Any]:
        """Get statistics about learned patterns."""
        total_patterns = len(self.patterns)
        pattern_types = Counter(p.pattern_type for p in self.patterns.values())
        total_frequency = sum(p.frequency for p in self.patterns.values())

        return {
            "total_patterns": total_patterns,
            "pattern_types": dict(pattern_types),
            "total_frequency": total_frequency,
            "most_common_type": (
                pattern_types.most_common(1)[0][0] if pattern_types else None
            ),
            "avg_confidence": (
                (sum(p.confidence for p in self.patterns.values()) / total_patterns)
                if total_patterns > 0
                else 0
            ),
        }

    def get_prevention_recommendations(self, error_data: Dict[str, Any]) -> List[str]:
        """Get prevention recommendations for an error."""
        match = self.analyze_error(error_data)

        if match.pattern_id == "unknown_error":
            return [
                "Implement comprehensive error handling",
                "Add logging for debugging",
            ]

        # Return prevention rules from the matched pattern
        pattern = self.patterns.get(match.pattern_id)
        if pattern:
            return pattern.prevention_rules

        return ["Review error patterns and implement appropriate safeguards"]

    # ===== NEW LEARNING METHODS =====

    def learn_from_cli_usage(
        self, command: str, success: bool, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Learn from CLI command usage patterns.

        Args:
            command: The CLI command that was executed
            success: Whether the command succeeded
            context: Additional context (user, time, etc.)
        """
        track_tool_usage(
            "pattern_recognition_system",
            "ai_system",
            {"action": "learn_from_cli", "command": command[:50], "success": success},
            "success",
        )

        # Add to command history
        cmd_entry = {
            "command": command,
            "success": success,
            "timestamp": time.time(),
            "context": context or {},
        }
        self.command_history.append(cmd_entry)
        self.command_history = self.command_history[-100:]  # Keep last 100 commands

        # Update CLI patterns
        self._update_cli_patterns(command, success, context)

        # Learn behavior patterns
        self._learn_behavior_from_cli(command, success, context)

        self._save_patterns()

    def _update_cli_patterns(
        self, command: str, success: bool, context: Optional[Dict[str, Any]]
    ) -> None:
        """Update CLI usage patterns based on command execution."""
        # Find or create pattern for this command sequence
        cmd_parts = command.split()
        if not cmd_parts:
            return

        base_cmd = cmd_parts[0]

        # Look for existing pattern
        pattern_id = None
        for pid, pattern in self.cli_patterns.items():
            if pattern.command_sequence and pattern.command_sequence[0] == base_cmd:
                pattern_id = pid
                break

        if pattern_id:
            # Update existing pattern
            pattern = self.cli_patterns[pattern_id]
            pattern.frequency += 1
            pattern.last_seen = time.time()

            # Update success rate
            total_attempts = pattern.frequency
            successful_attempts = int(pattern.success_rate * (total_attempts - 1) / 100)
            if success:
                successful_attempts += 1
            pattern.success_rate = (successful_attempts / total_attempts) * 100

            # Add recommendations based on success/failure patterns
            if pattern.success_rate > 80:
                pattern.recommendations.append(
                    f"Command '{base_cmd}' has high success rate"
                )
                pattern.recommendations = list(set(pattern.recommendations))  # Unique
        else:
            # Create new pattern
            pattern_id = f"cli_{int(time.time())}_{hash(command) % 10000}"
            pattern = CLIPattern(
                pattern_id=pattern_id,
                command_sequence=[base_cmd],
                success_rate=100.0 if success else 0.0,
                frequency=1,
                context=context or {},
                first_seen=time.time(),
                last_seen=time.time(),
                recommendations=[],
            )
            self.cli_patterns[pattern_id] = pattern

    def _learn_behavior_from_cli(
        self, command: str, success: bool, context: Optional[Dict[str, Any]]
    ) -> None:
        """Learn user behavior patterns from CLI usage."""
        # Analyze command patterns and create behavior insights

        # Pattern 1: Error recovery behavior
        if not success and "fix" in command.lower() or "repair" in command.lower():
            pattern_id = "error_recovery_pattern"
            if pattern_id not in self.behavior_patterns:
                self.behavior_patterns[pattern_id] = BehaviorPattern(
                    pattern_id=pattern_id,
                    pattern_type="error_recovery",
                    description="User tends to run fix/repair commands after errors",
                    frequency=0,
                    confidence=0.0,
                    triggers=["command_failure"],
                    outcomes=["runs_fix_commands"],
                    recommendations=["Automate common fix patterns"],
                    first_seen=time.time(),
                    last_seen=time.time(),
                )

            pattern = self.behavior_patterns[pattern_id]
            pattern.frequency += 1
            pattern.last_seen = time.time()
            pattern.confidence = min(pattern.confidence + 0.1, 0.9)

        # Pattern 2: Validation-first behavior
        elif success and ("validate" in command.lower() or "check" in command.lower()):
            pattern_id = "validation_first_pattern"
            if pattern_id not in self.behavior_patterns:
                self.behavior_patterns[pattern_id] = BehaviorPattern(
                    pattern_id=pattern_id,
                    pattern_type="successful_workflow",
                    description="User validates before major changes",
                    frequency=0,
                    confidence=0.0,
                    triggers=["before_changes"],
                    outcomes=["validation_success"],
                    recommendations=["Continue validation-first approach"],
                    first_seen=time.time(),
                    last_seen=time.time(),
                )

            pattern = self.behavior_patterns[pattern_id]
            pattern.frequency += 1
            pattern.last_seen = time.time()
            pattern.confidence = min(pattern.confidence + 0.1, 0.9)

    def learn_from_repeated_errors(self, error_data: Dict[str, Any]) -> None:
        """
        Learn from repeated error patterns to improve prevention.

        Args:
            error_data: Error information from error monitor
        """
        track_tool_usage(
            "pattern_recognition_system",
            "ai_system",
            {
                "action": "learn_from_repeated_errors",
                "error_type": error_data.get("type"),
            },
            "success",
        )

        error_signature = self._generate_error_signature(error_data)

        # Add to error clusters for pattern discovery
        self.error_clusters[error_signature].append(error_data)

        # If we have enough examples, create or strengthen patterns
        cluster = self.error_clusters[error_signature]
        if len(cluster) >= 3:  # Need at least 3 occurrences
            self._create_repeated_error_pattern(error_signature, cluster)

        # Learn from error context and timing
        self._learn_error_timing_patterns(error_data)

        self._save_patterns()

    def _generate_error_signature(self, error_data: Dict[str, Any]) -> str:
        """Generate a signature for error clustering."""
        error_type = error_data.get("type", "")
        error_message = error_data.get("message", "")
        error_file = error_data.get("file", "")

        # Create a normalized signature
        signature_parts = [error_type, error_file]
        if error_message:
            # Extract key error words
            words = re.findall(r"\b\w+\b", error_message.lower())
            key_words = [w for w in words if len(w) > 3][:5]  # Top 5 long words
            signature_parts.extend(key_words)

        return "_".join(signature_parts)

    def _create_repeated_error_pattern(
        self, signature: str, error_cluster: List[Dict[str, Any]]
    ) -> None:
        """Create a pattern from repeated errors."""
        if not error_cluster:
            return

        # Use first error to determine pattern type
        first_error = error_cluster[0]
        error_type = (
            self._categorize_error(
                first_error.get("type", ""), first_error.get("message", "")
            )
            or "repeated_error"
        )

        pattern_id = f"repeated_{signature}_{int(time.time())}"

        # Analyze common prevention strategies
        prevention_rules = []
        if error_type == "styling_error":
            prevention_rules.extend(
                [
                    "Run automated code formatting before commits",
                    "Configure editor to highlight style issues",
                    "Set up pre-commit hooks for style checking",
                ]
            )
        elif error_type == "import_error":
            prevention_rules.extend(
                [
                    "Keep requirements.txt synchronized",
                    "Use virtual environments consistently",
                    "Test imports after dependency changes",
                ]
            )
        elif error_type == "cli_error":
            prevention_rules.extend(
                [
                    "Validate command syntax before execution",
                    "Use command completion features",
                    "Test commands in safe environments first",
                ]
            )

        pattern = ErrorPattern(
            pattern_id=pattern_id,
            pattern_type=error_type,
            signature=f"Repeated {error_type}: {signature}",
            description=f"Pattern of repeated {error_type} errors ({len(error_cluster)} occurrences)",
            examples=error_cluster[-10:],  # Keep last 10 examples
            frequency=len(error_cluster),
            first_seen=min(e.get("timestamp", time.time()) for e in error_cluster),
            last_seen=max(e.get("timestamp", time.time()) for e in error_cluster),
            confidence=min(
                0.3 + (len(error_cluster) * 0.1), 0.9
            ),  # Higher confidence with more occurrences
            prevention_rules=prevention_rules,
        )

        self.patterns[pattern_id] = pattern

        # Record learning event
        self.persistence.record_learning_event(
            "repeated_error_pattern_learned",
            {
                "pattern_id": pattern_id,
                "error_type": error_type,
                "occurrences": len(error_cluster),
                "signature": signature,
                "confidence": pattern.confidence,
            },
        )

    def _learn_error_timing_patterns(self, error_data: Dict[str, Any]) -> None:
        """Learn patterns related to when errors occur."""
        # This could analyze time-of-day, day-of-week patterns, etc.
        # For now, just track basic timing

    def get_cli_recommendations(
        self, current_command: Optional[str] = None
    ) -> List[str]:
        """
        Get CLI usage recommendations based on learned patterns.

        Args:
            current_command: Current command being considered

        Returns:
            List of recommendations
        """
        recommendations = []

        # Find successful command patterns
        successful_patterns = [
            p
            for p in self.cli_patterns.values()
            if p.success_rate > 80 and p.frequency >= 3
        ]

        if successful_patterns:
            top_pattern = max(successful_patterns, key=lambda p: p.success_rate)
            recommendations.append(
                f"Consider using '{top_pattern.command_sequence[0]}' commands "
                f"(success rate: {top_pattern.success_rate:.1f}%)"
            )

        # Check behavior patterns
        for pattern in self.behavior_patterns.values():
            if pattern.confidence > 0.7:
                recommendations.extend(
                    pattern.recommendations[:2]
                )  # Top 2 recommendations

        return recommendations[:5]  # Limit to 5 recommendations

    def get_behavior_insights(self) -> List[Dict[str, Any]]:
        """
        Get insights about user behavior patterns.

        Returns:
            List of behavior insights
        """
        insights = []

        for pattern in self.behavior_patterns.values():
            if pattern.confidence > 0.6 and pattern.frequency >= 2:
                insights.append(
                    {
                        "pattern_type": pattern.pattern_type,
                        "description": pattern.description,
                        "frequency": pattern.frequency,
                        "confidence": pattern.confidence,
                        "recommendations": pattern.recommendations,
                    }
                )

        return insights
