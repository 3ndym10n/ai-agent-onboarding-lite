"""
Smart Debugger: Self - improving debugging system that learns from past issues.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import utils


class SmartDebugger:
    """Self - improving debugging system that learns from past issues."""

    def __init__(self, root: Path):
        self.root = root
        self.debug_log_path = root / ".ai_onboard" / "debug_log.jsonl"
        self.patterns_path = root / ".ai_onboard" / "debug_patterns.json"
        self.solutions_path = root / ".ai_onboard" / "debug_solutions.json"
        self.learning_path = root / ".ai_onboard" / "debug_learning.json"
        self.pattern_database_path = root / ".ai_onboard" / "pattern_database.json"
        self.confidence_model_path = root / ".ai_onboard" / "confidence_model.json"

        # Initialize enhanced debugging components
        self._initialize_enhanced_debugging()

    def analyze_error(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an error and provide smart debugging insights."""
        # Extract error information
        error_type = error_data.get("type", "unknown")
        error_message = error_data.get("message", "")
        error_data.get("context", {})

        # Check for known patterns
        pattern_match = self._find_pattern_match(error_type, error_message)

        if pattern_match:
            # Use known solution
            solution = self._get_solution(pattern_match["pattern_id"])
            confidence = pattern_match["confidence"]
            approach = "pattern_match"
        else:
            # Generate new analysis
            analysis = self._generate_analysis(error_data)
            solution = analysis["solution"]
            confidence = analysis["confidence"]
            approach = "generated"

        # Log the debugging session
        self._log_debug_session(error_data, solution, confidence, approach)

        # Learn from this session
        self._learn_from_session(error_data, solution, confidence)

        return {
            "solution": solution,
            "confidence": confidence,
            "approach": approach,
            "pattern_id": pattern_match["pattern_id"] if pattern_match else None,
            "debugging_steps": self._generate_debugging_steps(error_data, solution),
            "prevention_tips": self._generate_prevention_tips(error_data),
            "enhanced_analysis": self._perform_enhanced_analysis(error_data),
            "alternative_solutions": self._generate_alternative_solutions(
                error_data, solution
            ),
            "contextual_insights": self._extract_contextual_insights(error_data),
        }

    def improve_patterns(self) -> Dict[str, Any]:
        """Improve debugging patterns based on learning data."""
        learning_data = self._load_learning_data()
        patterns = self._load_patterns()

        improvements = []

        # Analyze successful solutions
        successful_sessions = [
            session
            for session in learning_data.get("sessions", [])
            if session.get("success", False) and session.get("approach") == "generated"
        ]

        for session in successful_sessions:
            # Extract patterns from successful solutions
            new_pattern = self._extract_pattern(
                session["error_data"], session["solution"]
            )
            if new_pattern:
                pattern_id = self._add_pattern(new_pattern)
                improvements.append(
                    {
                        "type": "new_pattern",
                        "pattern_id": pattern_id,
                        "confidence": session.get("confidence", 0.5),
                    }
                )

        # Improve existing patterns
        for pattern in patterns.get("patterns", []):
            improvement = self._improve_pattern(pattern, learning_data)
            if improvement:
                improvements.append(improvement)

        # Update patterns
        self._save_patterns(patterns)

        return {
            "improvements_made": len(improvements),
            "improvements": improvements,
            "total_patterns": len(patterns.get("patterns", [])),
            "success_rate": self._calculate_success_rate(learning_data),
        }

    def get_debugging_stats(self) -> Dict[str, Any]:
        """Get debugging system statistics and performance metrics."""
        learning_data = self._load_learning_data()
        patterns = self._load_patterns()

        # Calculate success rates
        total_sessions = len(learning_data.get("sessions", []))
        successful_sessions = len(
            [s for s in learning_data.get("sessions", []) if s.get("success", False)]
        )

        # Pattern effectiveness
        pattern_success_rate = self._calculate_pattern_success_rate(learning_data)

        # Recent performance
        recent_sessions = self._get_recent_sessions(learning_data, days=7)
        recent_success_rate = len(
            [s for s in recent_sessions if s.get("success", False)]
        ) / max(len(recent_sessions), 1)

        return {
            "total_sessions": total_sessions,
            "successful_sessions": successful_sessions,
            "overall_success_rate": successful_sessions / max(total_sessions, 1),
            "recent_success_rate": recent_success_rate,
            "total_patterns": len(patterns.get("patterns", [])),
            "pattern_success_rate": pattern_success_rate,
            "learning_improvements": len(learning_data.get("improvements", [])),
            "last_improvement": learning_data.get("last_improvement"),
        }

    def _find_pattern_match(
        self, error_type: str, error_message: str
    ) -> Optional[Dict[str, Any]]:
        """Find a matching pattern for the error."""
        patterns = self._load_patterns()

        best_match = None
        best_confidence = 0.0

        for pattern in patterns.get("patterns", []):
            confidence = self._calculate_pattern_confidence(
                pattern, error_type, error_message
            )
            if confidence > best_confidence and confidence > 0.7:  # Threshold
                best_confidence = confidence
                best_match = {
                    "pattern_id": pattern["id"],
                    "confidence": confidence,
                    "pattern": pattern,
                }

        return best_match

    def _calculate_pattern_confidence(
        self, pattern: Dict[str, Any], error_type: str, error_message: str
    ) -> float:
        """Calculate confidence score for pattern match."""
        confidence = 0.0

        # Type matching
        if pattern.get("error_type") == error_type:
            confidence += 0.4

        # Message pattern matching
        message_patterns = pattern.get("message_patterns", [])
        for msg_pattern in message_patterns:
            if re.search(msg_pattern, error_message, re.IGNORECASE):
                confidence += 0.3
                break

        # Context matching
        context_patterns = pattern.get("context_patterns", [])
        for ctx_pattern in context_patterns:
            if re.search(ctx_pattern, str(error_message), re.IGNORECASE):
                confidence += 0.2
                break

        # Historical success rate
        success_rate = pattern.get("success_rate", 0.5)
        confidence += success_rate * 0.1

        return min(confidence, 1.0)

    def _get_solution(self, pattern_id: str) -> Dict[str, Any]:
        """Get solution for a pattern."""
        solutions = self._load_solutions()
        solution_list = solutions.get("solutions", [])

        # Find solution by ID
        for solution in solution_list:
            if solution.get("id") == pattern_id:
                return solution

        # Default if not found
        return {"description": "No solution available", "steps": [], "type": "unknown"}

    def _generate_analysis(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate new analysis for an error."""
        error_type = error_data.get("type", "unknown")
        error_message = error_data.get("message", "")

        # Basic analysis based on error type
        if "import" in error_type.lower() or "module" in error_message.lower():
            solution = {
                "description": "Import / module error detected",
                "steps": [
                    "Check if required module is installed",
                    "Verify import statements",
                    "Check Python path configuration",
                ],
                "type": "import_error",
            }
            confidence = 0.6
        elif "syntax" in error_type.lower():
            solution = {
                "description": "Syntax error detected",
                "steps": [
                    "Check for missing parentheses, brackets, or quotes",
                    "Verify indentation",
                    "Look for typos in keywords",
                ],
                "type": "syntax_error",
            }
            confidence = 0.7
        elif "permission" in error_type.lower() or "access" in error_message.lower():
            solution = {
                "description": "Permission / access error detected",
                "steps": [
                    "Check file permissions",
                    "Verify user has required access",
                    "Check if file is locked by another process",
                ],
                "type": "permission_error",
            }
            confidence = 0.8
        else:
            solution = {
                "description": "Generic error analysis",
                "steps": [
                    "Review error message carefully",
                    "Check error context and stack trace",
                    "Search for similar issues online",
                ],
                "type": "generic",
            }
            confidence = 0.3

        return {"solution": solution, "confidence": confidence}

    def _generate_debugging_steps(
        self, error_data: Dict[str, Any], solution: Dict[str, Any]
    ) -> List[str]:
        """Generate specific debugging steps for the error."""
        steps = solution.get("steps", []).copy()

        # Add context - specific steps
        context = error_data.get("context", {})
        if isinstance(context, dict):
            if context.get("file_path"):
                steps.insert(0, f"Check file: {context['file_path']}")

            if context.get("line_number"):
                steps.insert(1, f"Review code around line {context['line_number']}")
        elif isinstance(context, str):
            steps.insert(0, f"Context: {context}")

        return steps

    def _generate_prevention_tips(self, error_data: Dict[str, Any]) -> List[str]:
        """Generate tips to prevent similar errors in the future."""
        error_type = error_data.get("type", "unknown")

        tips = []

        if "import" in error_type.lower():
            tips.extend(
                [
                    "Use virtual environments for dependency management",
                    "Keep requirements.txt updated",
                    "Use absolute imports when possible",
                ]
            )
        elif "syntax" in error_type.lower():
            tips.extend(
                [
                    "Use a linter to catch syntax errors early",
                    "Enable syntax highlighting in your editor",
                    "Review code before running",
                ]
            )
        elif "permission" in error_type.lower():
            tips.extend(
                [
                    "Set appropriate file permissions",
                    "Use proper user accounts for different operations",
                    "Check file locks before operations",
                ]
            )

        return tips

    def _log_debug_session(
        self,
        error_data: Dict[str, Any],
        solution: Dict[str, Any],
        confidence: float,
        approach: str,
    ) -> None:
        """Log a debugging session for learning."""
        utils.ensure_dir(self.debug_log_path.parent)
        entry = {
            "ts": utils.now_iso(),
            "error_data": error_data,
            "solution": solution,
            "confidence": confidence,
            "approach": approach,
            "success": None,  # Will be updated later
        }
        with open(self.debug_log_path, "a", encoding="utf-8") as f:
            json.dump(entry, f)
            f.write("\n")

    def _learn_from_session(
        self, error_data: Dict[str, Any], solution: Dict[str, Any], confidence: float
    ) -> None:
        """Learn from a debugging session."""
        learning_data = self._load_learning_data()

        session = {
            "ts": utils.now_iso(),
            "error_data": error_data,
            "solution": solution,
            "confidence": confidence,
            "success": None,  # Will be updated when user provides feedback
        }

        if "sessions" not in learning_data:
            learning_data["sessions"] = []

        learning_data["sessions"].append(session)
        self._save_learning_data(learning_data)

    def _extract_pattern(
        self, error_data: Dict[str, Any], solution: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Extract a pattern from successful error - solution pair."""
        error_type = error_data.get("type", "")
        error_message = error_data.get("message", "")

        # Extract key phrases from error message
        key_phrases = self._extract_key_phrases(error_message)

        if not key_phrases:
            return None

        return {
            "error_type": error_type,
            "message_patterns": key_phrases,
            "context_patterns": [],
            "solution_id": solution.get("id"),
            "success_rate": 1.0,
            "usage_count": 1,
        }

    def _extract_key_phrases(self, message: str) -> List[str]:
        """Extract key phrases from error message for pattern matching."""
        # Simple extraction - can be enhanced with NLP
        phrases = []

        # Common error patterns
        patterns = [
            r"ModuleNotFoundError: No module named '(\w+)'",
            r"ImportError: cannot import name '(\w+)'",
            r"SyntaxError: invalid syntax",
            r"PermissionError: \[Errno 13\] Permission denied",
            r"FileNotFoundError: \[Errno 2\] No such file or directory",
        ]

        for pattern in patterns:
            if re.search(pattern, message):
                phrases.append(pattern)

        return phrases

    def _add_pattern(self, pattern: Dict[str, Any]) -> str:
        """Add a new pattern to the pattern database."""
        patterns = self._load_patterns()

        if "patterns" not in patterns:
            patterns["patterns"] = []

        pattern_id = f"pattern_{len(patterns['patterns']) + 1}"
        pattern["id"] = pattern_id
        pattern["created_at"] = utils.now_iso()

        patterns["patterns"].append(pattern)
        self._save_patterns(patterns)

        return pattern_id

    def _improve_pattern(
        self, pattern: Dict[str, Any], learning_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Improve an existing pattern based on learning data."""
        # Find sessions that used this pattern
        pattern_sessions = [
            s
            for s in learning_data.get("sessions", [])
            if s.get("pattern_id") == pattern["id"]
        ]

        if not pattern_sessions:
            return None

        # Calculate new success rate
        successful = len([s for s in pattern_sessions if s.get("success", False)])
        total = len(pattern_sessions)
        new_success_rate = successful / total

        # Update pattern
        pattern["success_rate"] = new_success_rate
        pattern["usage_count"] = total
        pattern["last_updated"] = utils.now_iso()

        return {
            "type": "pattern_improved",
            "pattern_id": pattern["id"],
            "old_success_rate": pattern.get("success_rate", 0.5),
            "new_success_rate": new_success_rate,
        }

    def _calculate_success_rate(self, learning_data: Dict[str, Any]) -> float:
        """Calculate overall success rate."""
        sessions = learning_data.get("sessions", [])
        if not sessions:
            return 0.0

        successful = len([s for s in sessions if s.get("success", False)])
        return successful / len(sessions)

    def _calculate_pattern_success_rate(self, learning_data: Dict[str, Any]) -> float:
        """Calculate success rate for pattern - based solutions."""
        pattern_sessions = [
            s
            for s in learning_data.get("sessions", [])
            if s.get("approach") == "pattern_match"
        ]

        if not pattern_sessions:
            return 0.0

        successful = len([s for s in pattern_sessions if s.get("success", False)])
        return successful / len(pattern_sessions)

    def _get_recent_sessions(
        self, learning_data: Dict[str, Any], days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get recent debugging sessions."""
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_iso = cutoff.isoformat()

        return [
            s for s in learning_data.get("sessions", []) if s.get("ts", "") > cutoff_iso
        ]

    def _load_patterns(self) -> Dict[str, Any]:
        """Load debugging patterns."""
        return utils.read_json(self.patterns_path, default={"patterns": []})

    def _save_patterns(self, patterns: Dict[str, Any]) -> None:
        """Save debugging patterns."""
        utils.write_json(self.patterns_path, patterns)

    def _load_solutions(self) -> Dict[str, Any]:
        """Load debugging solutions."""
        return utils.read_json(self.solutions_path, default={"solutions": {}})

    def _load_learning_data(self) -> Dict[str, Any]:
        """Load learning data."""
        return utils.read_json(
            self.learning_path, default={"sessions": [], "improvements": []}
        )

    def _save_learning_data(self, learning_data: Dict[str, Any]) -> None:
        """Save learning data."""
        utils.write_json(self.learning_path, learning_data)

    def _initialize_enhanced_debugging(self) -> None:
        """Initialize enhanced debugging components."""
        # Ensure directories exist
        for path in [
            self.pattern_database_path.parent,
            self.confidence_model_path.parent,
        ]:
            utils.ensure_dir(path)

        # Initialize pattern database if it doesn't exist
        if not self.pattern_database_path.exists():
            initial_patterns = self._create_initial_pattern_database()
            utils.write_json(self.pattern_database_path, initial_patterns)

        # Initialize confidence model if it doesn't exist
        if not self.confidence_model_path.exists():
            initial_model = self._create_initial_confidence_model()
            utils.write_json(self.confidence_model_path, initial_model)

    def _create_initial_pattern_database(self) -> Dict[str, Any]:
        """Create initial pattern database with common error patterns."""
        return {
            "version": "2.0",
            "last_updated": utils.now_iso(),
            "patterns": {
                "import_errors": {
                    "patterns": [
                        r"ImportError.*No module named",
                        r"ModuleNotFoundError.*No module named",
                    ],
                    "solutions": [
                        "Install missing package: pip install <package_name>",
                        "Check if package is in requirements.txt",
                        "Verify virtual environment is activated",
                        "Check Python path configuration",
                    ],
                    "confidence_base": 0.85,
                    "category": "import",
                },
                "attribute_errors": {
                    "patterns": [
                        r"AttributeError.*has no attribute",
                        r"AttributeError.*object has no attribute",
                    ],
                    "solutions": [
                        "Check object type and available attributes",
                        "Verify method/variable name spelling",
                        "Check if object is properly initialized",
                        "Use hasattr() to check attribute existence",
                    ],
                    "confidence_base": 0.8,
                    "category": "attribute",
                },
                "type_errors": {
                    "patterns": [
                        r"TypeError.*unsupported operand type",
                        r"TypeError.*expected.*got",
                    ],
                    "solutions": [
                        "Check data types of operands",
                        "Use type() or isinstance() for type checking",
                        "Convert types explicitly when needed",
                        "Review function signatures and parameter types",
                    ],
                    "confidence_base": 0.75,
                    "category": "type",
                },
                "file_errors": {
                    "patterns": [
                        r"FileNotFoundError",
                        r"IsADirectoryError",
                        r"PermissionError",
                    ],
                    "solutions": [
                        "Check if file/directory exists: os.path.exists()",
                        "Verify file permissions: os.access()",
                        "Check if file is locked by another process",
                        "Use absolute paths when possible",
                        "Handle file operations in try-except blocks",
                    ],
                    "confidence_base": 0.9,
                    "category": "file",
                },
                "network_errors": {
                    "patterns": [
                        r"ConnectionError",
                        r"TimeoutError",
                        r"URLError",
                        r"requests\.exceptions",
                    ],
                    "solutions": [
                        "Check network connectivity",
                        "Verify URL/host is accessible",
                        "Implement retry logic with exponential backoff",
                        "Add timeout handling",
                        "Check proxy/firewall settings",
                    ],
                    "confidence_base": 0.7,
                    "category": "network",
                },
                "syntax_errors": {
                    "patterns": [
                        r"SyntaxError",
                        r"IndentationError",
                        r"TabError",
                    ],
                    "solutions": [
                        "Check for missing parentheses, brackets, or quotes",
                        "Verify consistent indentation (spaces vs tabs)",
                        "Look for typos in keywords and variable names",
                        "Use a linter to catch syntax errors early",
                        "Review code around the error line",
                    ],
                    "confidence_base": 0.95,
                    "category": "syntax",
                },
            },
            "learning_stats": {
                "total_patterns_used": 0,
                "successful_solutions": 0,
                "failed_solutions": 0,
                "pattern_effectiveness": {},
            },
        }

    def _create_initial_confidence_model(self) -> Dict[str, Any]:
        """Create initial confidence scoring model."""
        return {
            "version": "2.0",
            "last_updated": utils.now_iso(),
            "confidence_factors": {
                "pattern_match_quality": {
                    "exact_match": 1.0,
                    "partial_match": 0.7,
                    "weak_match": 0.4,
                    "no_match": 0.1,
                },
                "error_type_frequency": {
                    "very_common": 1.0,  # > 50 occurrences
                    "common": 0.8,  # 20-50 occurrences
                    "uncommon": 0.6,  # 5-20 occurrences
                    "rare": 0.3,  # 1-5 occurrences
                    "unknown": 0.1,  # 0 occurrences
                },
                "context_relevance": {
                    "high": 1.0,  # Strong context match
                    "medium": 0.7,  # Partial context match
                    "low": 0.4,  # Weak context match
                    "none": 0.1,  # No context match
                },
                "solution_success_history": {
                    "excellent": 1.0,  # > 90% success rate
                    "good": 0.8,  # 70-90% success rate
                    "fair": 0.6,  # 50-70% success rate
                    "poor": 0.3,  # 30-50% success rate
                    "unknown": 0.5,  # No history
                },
            },
            "learning_weights": {
                "pattern_match": 0.4,
                "error_frequency": 0.2,
                "context_relevance": 0.2,
                "success_history": 0.2,
            },
            "adaptation_stats": {
                "total_predictions": 0,
                "correct_predictions": 0,
                "weight_adjustments": 0,
                "last_adaptation": None,
            },
        }

    def _perform_enhanced_analysis(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform enhanced analysis with advanced debugging techniques."""
        error_type = error_data.get("type", "")
        error_message = error_data.get("message", "")
        context = error_data.get("context", {})

        enhanced_analysis = {
            "code_analysis": self._analyze_error_code(error_data),
            "stack_trace_insights": self._analyze_stack_trace(error_data),
            "context_patterns": self._analyze_error_context(context),
            "severity_assessment": self._assess_error_severity(error_data),
            "likely_root_causes": self._identify_root_causes(error_data),
        }

        return enhanced_analysis

    def _analyze_error_code(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the error in the context of the code where it occurred."""
        context = error_data.get("context", {})
        enriched_context = error_data.get("enriched_context", {})

        analysis: Dict[str, Any] = {
            "code_location": {},
            "variable_analysis": {},
            "logic_flow": {},
            "potential_fixes": [],
        }

        # Ensure logic_flow is treated as a dict
        logic_flow: Dict[str, Any] = analysis["logic_flow"]

        # Extract code location information
        if enriched_context.get("stack_analysis", {}).get("stack_frames"):
            stack_frames = enriched_context["stack_analysis"]["stack_frames"]
            if stack_frames:
                latest_frame = stack_frames[0]  # Most recent frame
                analysis["code_location"] = {
                    "file": latest_frame.get("filename", "unknown"),
                    "line": latest_frame.get("line_number", "unknown"),
                    "function": latest_frame.get("function", "unknown"),
                    "code_context": latest_frame.get("code_context", ""),
                }

        # Analyze variables if available
        if enriched_context.get("stack_analysis", {}).get("local_variables"):
            local_vars = enriched_context["stack_analysis"]["local_variables"]
            analysis["variable_analysis"] = {
                "variable_count": len(local_vars),
                "variable_types": {k: type(v).__name__ for k, v in local_vars.items()},
                "potential_null_values": [
                    k for k, v in local_vars.items() if v is None
                ],
            }

        # Analyze logic flow patterns
        error_type = error_data.get("type", "")
        if "AttributeError" in error_type:
            logic_flow["issue_type"] = "attribute_access"
            logic_flow["suggestions"] = [
                "Check if object is properly initialized",
                "Verify attribute name spelling",
                "Consider using getattr() with default",
            ]
        elif "TypeError" in error_type:
            logic_flow["issue_type"] = "type_mismatch"
            logic_flow["suggestions"] = [
                "Verify operand types",
                "Check function parameter types",
                "Consider type conversion or validation",
            ]

        return analysis

    def _analyze_stack_trace(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stack trace for debugging insights."""
        enriched_context = error_data.get("enriched_context", {})
        stack_analysis = enriched_context.get("stack_analysis", {})

        insights: Dict[str, Any] = {
            "call_depth": 0,
            "error_origin": {},
            "call_chain_analysis": {},
            "suspicious_patterns": [],
        }

        if stack_analysis.get("stack_frames"):
            stack_frames = stack_analysis["stack_frames"]
            insights["call_depth"] = len(stack_frames)

            # Analyze error origin
            if stack_frames:
                origin_frame = stack_frames[-1]  # Original call
                insights["error_origin"] = {
                    "file": origin_frame.get("filename", "unknown"),
                    "function": origin_frame.get("function", "unknown"),
                    "line": origin_frame.get("line_number", "unknown"),
                }

            # Analyze call chain
            insights["call_chain_analysis"] = {
                "unique_files": len(set(f.get("filename", "") for f in stack_frames)),
                "unique_functions": len(
                    set(f.get("function", "") for f in stack_frames)
                ),
                "framework_calls": sum(
                    1
                    for f in stack_frames
                    if "framework" in f.get("filename", "").lower()
                ),
            }

        # Look for suspicious patterns
        error_message = error_data.get("message", "").lower()
        if "recursion" in error_message:
            insights["suspicious_patterns"].append("potential_infinite_recursion")
        if "memory" in error_message:
            insights["suspicious_patterns"].append("memory_issue")
        if "timeout" in error_message:
            insights["suspicious_patterns"].append("timeout_issue")

        return insights

    def _analyze_error_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze error context for patterns and insights."""
        if not isinstance(context, dict):
            return {"analysis": "invalid_context", "insights": []}

        analysis: Dict[str, Any] = {
            "context_completeness": {},
            "pattern_matches": [],
            "risk_factors": [],
        }

        # Analyze context completeness
        important_keys = ["agent_type", "command", "session_id", "user_id"]
        analysis["context_completeness"] = {
            "total_keys": len(context),
            "important_keys_present": sum(
                1 for key in important_keys if key in context
            ),
            "completeness_score": len([k for k in important_keys if k in context])
            / len(important_keys),
        }

        # Look for context patterns
        if context.get("agent_type") == "background" and context.get("command"):
            analysis["pattern_matches"].append("background_processing_error")

        if "timeout" in str(context.get("command", "")).lower():
            analysis["pattern_matches"].append("timeout_related_operation")

        if context.get("session_id") and len(str(context["session_id"])) < 5:
            analysis["risk_factors"].append("short_session_id_may_indicate_test")

        return analysis

    def _assess_error_severity(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the severity of the error."""
        error_type = error_data.get("type", "")
        error_message = error_data.get("message", "")
        context = error_data.get("context", {})

        severity_score = 0.5  # Default medium severity
        severity_factors = []

        # Error type severity
        if any(term in error_type for term in ["SystemExit", "KeyboardInterrupt"]):
            severity_score = 0.2
            severity_factors.append("system_level_interruption")
        elif any(term in error_type for term in ["ImportError", "ModuleNotFoundError"]):
            severity_score = 0.8
            severity_factors.append("dependency_issue")
        elif any(term in error_type for term in ["MemoryError", "RecursionError"]):
            severity_score = 0.9
            severity_factors.append("resource_exhaustion")
        elif any(term in error_type for term in ["SyntaxError", "IndentationError"]):
            severity_score = 0.3
            severity_factors.append("code_quality_issue")

        # Context-based severity adjustments
        if context.get("agent_type") == "background":
            severity_score *= 0.8  # Background errors are less critical
            severity_factors.append("background_operation")

        if "test" in str(context.get("command", "")).lower():
            severity_score *= 0.6  # Test errors are less critical
            severity_factors.append("test_environment")

        return {
            "severity_score": severity_score,
            "severity_level": (
                "low"
                if severity_score < 0.4
                else "medium" if severity_score < 0.7 else "high"
            ),
            "severity_factors": severity_factors,
            "requires_immediate_attention": severity_score > 0.8,
        }

    def _identify_root_causes(self, error_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential root causes of the error."""
        error_type = error_data.get("type", "")
        error_message = error_data.get("message", "")
        context = error_data.get("context", {})

        root_causes = []

        # Type-based root cause analysis
        if "AttributeError" in error_type:
            root_causes.extend(
                [
                    {
                        "cause": "Object not properly initialized",
                        "confidence": 0.6,
                        "evidence": "AttributeError suggests object state issue",
                    },
                    {
                        "cause": "Method/attribute name misspelled",
                        "confidence": 0.7,
                        "evidence": "AttributeError with 'has no attribute' message",
                    },
                    {
                        "cause": "Wrong object type used",
                        "confidence": 0.5,
                        "evidence": "Type mismatch in attribute access",
                    },
                ]
            )

        elif "ImportError" in error_type:
            root_causes.extend(
                [
                    {
                        "cause": "Package not installed",
                        "confidence": 0.9,
                        "evidence": "ImportError indicates missing dependency",
                    },
                    {
                        "cause": "Incorrect module path",
                        "confidence": 0.7,
                        "evidence": "ImportError with module name in message",
                    },
                ]
            )

        elif "TypeError" in error_type:
            root_causes.extend(
                [
                    {
                        "cause": "Incompatible operand types",
                        "confidence": 0.8,
                        "evidence": "TypeError with operand type message",
                    },
                    {
                        "cause": "Incorrect function call signature",
                        "confidence": 0.6,
                        "evidence": "TypeError with argument-related message",
                    },
                ]
            )

        # Context-based root causes
        if context.get("command"):
            command = str(context["command"]).lower()
            if "network" in command or "http" in command:
                root_causes.append(
                    {
                        "cause": "Network connectivity issue",
                        "confidence": 0.7,
                        "evidence": "Command suggests network operation",
                    }
                )

        # Return top 3 most likely root causes
        return sorted(root_causes, key=lambda x: x["confidence"], reverse=True)[:3]

    def _generate_alternative_solutions(
        self, error_data: Dict[str, Any], primary_solution: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate alternative solutions for the error."""
        error_type = error_data.get("type", "")
        error_message = error_data.get("message", "")

        alternatives = []

        # Generate alternatives based on error type
        if "AttributeError" in error_type:
            alternatives.extend(
                [
                    {
                        "description": "Use hasattr() to check attribute existence",
                        "code_example": "if hasattr(obj, 'attribute'): value =                             obj.attribute",
                        "confidence": 0.8,
                    },
                    {
                        "description": "Use getattr() with default value",
                        "code_example": "value =                             getattr(obj, 'attribute', default_value)",
                        "confidence": 0.9,
                    },
                    {
                        "description": "Check object type before attribute access",
                        "code_example": "if isinstance(obj, ExpectedClass): value =                             obj.attribute",
                        "confidence": 0.7,
                    },
                ]
            )

        elif "ImportError" in error_type:
            alternatives.extend(
                [
                    {
                        "description": "Use try-except import pattern",
                        "code_example": (
                            "try:\n    import optional_module\n"
                            "except ImportError:\n    optional_module = None"
                        ),
                        "confidence": 0.8,
                    },
                    {
                        "description": "Use importlib for dynamic imports",
                        "code_example": "import importlib\nmodule =                             importlib.import_module('module_name')",
                        "confidence": 0.6,
                    },
                ]
            )

        elif "KeyError" in error_type:
            alternatives.extend(
                [
                    {
                        "description": "Use dict.get() method",
                        "code_example": "value = my_dict.get('key', default_value)",
                        "confidence": 0.9,
                    },
                    {
                        "description": "Check key existence first",
                        "code_example": "if 'key' in my_dict: value = my_dict['key']",
                        "confidence": 0.8,
                    },
                    {
                        "description": "Use try-except block",
                        "code_example": "try:\n    value =                             my_dict['key']\nexcept KeyError:\n    value = default_value",
                        "confidence": 0.7,
                    },
                ]
            )

        # Return top 2 alternatives
        return sorted(alternatives, key=lambda x: x["confidence"], reverse=True)[:2]

    def _extract_contextual_insights(
        self, error_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract contextual insights from error data."""
        context = error_data.get("context", {})
        enriched_context = error_data.get("enriched_context", {})

        insights = {
            "temporal_patterns": {},
            "environmental_factors": {},
            "usage_patterns": {},
            "system_health_indicators": {},
        }

        # Temporal patterns
        if enriched_context.get("recent_activity", {}).get("recent_capability_usage"):
            recent_usage = enriched_context["recent_activity"][
                "recent_capability_usage"
            ]
            if recent_usage:
                # Analyze usage patterns
                capability_counts: dict[str, Any] = {}
                for usage in recent_usage:
                    cap = usage.get("capability", "unknown")
                    capability_counts[cap] = capability_counts.get(cap, 0) + 1

                insights["temporal_patterns"] = {
                    "most_recent_capability": recent_usage[0].get(
                        "capability", "unknown"
                    ),
                    "capability_frequency": capability_counts,
                    "usage_trend": "increasing" if len(recent_usage) > 2 else "stable",
                }

        # Environmental factors
        if enriched_context.get("environment"):
            env = enriched_context["environment"]
            insights["environmental_factors"] = {
                "working_directory_stability": (
                    "stable" if env.get("working_directory") else "unknown"
                ),
                "path_complexity": (
                    "complex" if len(env.get("path", "")) > 100 else "simple"
                ),
            }

        # System health indicators
        if enriched_context.get("resource_usage"):
            resources = enriched_context["resource_usage"]
            memory_percent = resources.get("system_memory", {}).get("percent_used", 0)
            insights["system_health_indicators"] = {
                "memory_pressure": "high" if memory_percent > 80 else "normal",
                "process_health": (
                    "good"
                    if resources.get("process_cpu_percent", 0) < 50
                    else "stressed"
                ),
            }

        return insights

    def update_confidence_model(
        self, error_data: Dict[str, Any], was_successful: bool
    ) -> None:
        """Update the confidence model based on debugging outcome."""
        model = utils.read_json(self.confidence_model_path, default={})

        # Update adaptation statistics
        if "adaptation_stats" not in model:
            model["adaptation_stats"] = {
                "total_predictions": 0,
                "correct_predictions": 0,
                "weight_adjustments": 0,
                "last_adaptation": None,
            }

        stats = model["adaptation_stats"]
        stats["total_predictions"] += 1

        if was_successful:
            stats["correct_predictions"] += 1

        # Update learning weights based on performance
        accuracy = stats["correct_predictions"] / stats["total_predictions"]
        weights = model.get("learning_weights", {})

        # Adjust weights based on accuracy trends
        if accuracy > 0.8:
            # High accuracy - maintain current weights
            pass
        elif accuracy > 0.6:
            # Moderate accuracy - slight adjustments
            weights["pattern_match"] = min(
                0.5, weights.get("pattern_match", 0.4) + 0.05
            )
        else:
            # Low accuracy - significant adjustments needed
            weights["success_history"] = min(
                0.4, weights.get("success_history", 0.2) + 0.1
            )
            stats["weight_adjustments"] += 1

        stats["last_adaptation"] = utils.now_iso()
        utils.write_json(self.confidence_model_path, model)

    def get_enhanced_debugging_stats(self) -> Dict[str, Any]:
        """Get enhanced debugging statistics including new metrics."""
        base_stats = self.get_debugging_stats()

        # Add enhanced metrics
        pattern_db = utils.read_json(self.pattern_database_path, default={})
        confidence_model = utils.read_json(self.confidence_model_path, default={})

        enhanced_stats = {
            "pattern_database_metrics": {
                "total_stored_patterns": len(pattern_db.get("patterns", {})),
                "pattern_categories": list(pattern_db.get("patterns", {}).keys()),
                "learning_stats": pattern_db.get("learning_stats", {}),
            },
            "confidence_model_metrics": {
                "model_version": confidence_model.get("version", "unknown"),
                "last_updated": confidence_model.get("last_updated", "unknown"),
                "adaptation_stats": confidence_model.get("adaptation_stats", {}),
                "learning_weights": confidence_model.get("learning_weights", {}),
            },
            "enhanced_features_usage": {
                "alternative_solutions_generated": 0,  # Would track in real usage
                "contextual_insights_extracted": 0,
                "root_cause_analysis_performed": 0,
            },
        }

        # Merge with base stats
        base_stats.update(enhanced_stats)
        return base_stats


def get_smart_debugger(root: Path) -> SmartDebugger:
    """Get smart debugger instance for the project."""
    return SmartDebugger(root)
