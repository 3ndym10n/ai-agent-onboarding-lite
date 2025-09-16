"""
Pattern Recognition System (T4.8) - Advanced error pattern detection and learning.

This module provides intelligent pattern recognition that:
- Analyzes error logs and user interactions for recurring patterns
- Identifies root causes and common failure modes
- Learns from successful vs unsuccessful patterns
- Provides proactive error prevention recommendations
- Integrates with learning persistence and automatic error prevention
"""

import re
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from . import utils
from .learning_persistence import LearningPersistenceManager


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
    prevention_rules: List[Dict[str, Any]] = field(default_factory=list)
    related_patterns: Set[str] = field(default_factory=set)


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
        self.patterns: Dict[str, ErrorPattern] = {}
        self.persistence = LearningPersistenceManager(root)

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
                "keywords": ["whitespace", "indentation", "newline", "length", "style"],
                "prevention": [
                    "Run code formatting tools",
                    "Configure editor auto-format",
                ],
            },
            "import_error": {
                "regex": r"(?i)(import error|module not found|no module named)",
                "keywords": ["import", "module", "not found", "error"],
                "prevention": ["Check requirements.txt", "Verify virtual environment"],
            },
            "type_error": {
                "regex": r"(?i)(type error|attribute error|none type)",
                "keywords": ["type", "attribute", "none", "error"],
                "prevention": ["Add type hints", "Use type checking tools"],
            },
        }

        self._load_patterns()

    def _load_patterns(self) -> None:
        """Load persisted error patterns."""
        try:
            # Try to load from persistence manager backup first
            if not self.persistence.load_pattern_backup(self):
                # Fallback to direct file loading
                if self.patterns_file.exists():
                    data = utils.read_json(self.patterns_file, default={})
                    for pattern_id, pattern_data in data.items():
                        pattern = ErrorPattern(**pattern_data)
                        self.patterns[pattern_id] = pattern
        except Exception as e:
            # If loading fails, start with empty patterns
            self.patterns = {}

        # Ensure patterns directory exists
        self.patterns_dir.mkdir(parents=True, exist_ok=True)

    def _save_patterns(self) -> None:
        """Save error patterns to disk."""
        try:
            # Save backup through persistence manager
            self.persistence.save_pattern_backup(self)

            # Also save directly for backward compatibility
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
        except Exception as e:
            # Log error but don't crash
            print(f"Warning: Failed to save patterns: {e}")

    def analyze_error(self, error_data: Dict[str, Any]) -> PatternMatch:
        """
        Analyze an error and find matching patterns.

        Args:
            error_data: Error information from error monitor

        Returns:
            PatternMatch with best matching pattern and suggestions
        """
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

        # If no good match found, try to create new pattern
        if best_confidence < 0.6:
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

                best_match = new_pattern
                best_confidence = 0.7  # New patterns get moderate confidence

        if best_match:
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

        # Check signature similarity
        if pattern.signature.lower() in error_text.lower():
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
        if regex_pattern and re.search(regex_pattern, error_text, re.IGNORECASE):
            confidence += 0.3

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
        prevention_rules = template.get(
            "prevention", ["Review error and implement appropriate fixes"]
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
            if regex and re.search(regex, error_text, re.IGNORECASE):
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
