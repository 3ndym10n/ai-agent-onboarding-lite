"""
Smart Debugger: Self-improving debugging system that learns from past issues.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
import re
from datetime import datetime, timedelta
from . import utils, telemetry, error_resolver


class SmartDebugger:
    """Self-improving debugging system that learns from past issues."""
    
    def __init__(self, root: Path):
        self.root = root
        self.debug_log_path = root / ".ai_onboard" / "debug_log.jsonl"
        self.patterns_path = root / ".ai_onboard" / "debug_patterns.json"
        self.solutions_path = root / ".ai_onboard" / "debug_solutions.json"
        self.learning_path = root / ".ai_onboard" / "debug_learning.json"
        
    def analyze_error(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an error and provide smart debugging insights."""
        # Extract error information
        error_type = error_data.get("type", "unknown")
        error_message = error_data.get("message", "")
        error_context = error_data.get("context", {})
        
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
            "prevention_tips": self._generate_prevention_tips(error_data)
        }
    
    def improve_patterns(self) -> Dict[str, Any]:
        """Improve debugging patterns based on learning data."""
        learning_data = self._load_learning_data()
        patterns = self._load_patterns()
        
        improvements = []
        
        # Analyze successful solutions
        successful_sessions = [
            session for session in learning_data.get("sessions", [])
            if session.get("success", False) and session.get("approach") == "generated"
        ]
        
        for session in successful_sessions:
            # Extract patterns from successful solutions
            new_pattern = self._extract_pattern(session["error_data"], session["solution"])
            if new_pattern:
                pattern_id = self._add_pattern(new_pattern)
                improvements.append({
                    "type": "new_pattern",
                    "pattern_id": pattern_id,
                    "confidence": session.get("confidence", 0.5)
                })
        
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
            "success_rate": self._calculate_success_rate(learning_data)
        }
    
    def get_debugging_stats(self) -> Dict[str, Any]:
        """Get debugging system statistics and performance metrics."""
        learning_data = self._load_learning_data()
        patterns = self._load_patterns()
        
        # Calculate success rates
        total_sessions = len(learning_data.get("sessions", []))
        successful_sessions = len([
            s for s in learning_data.get("sessions", [])
            if s.get("success", False)
        ])
        
        # Pattern effectiveness
        pattern_success_rate = self._calculate_pattern_success_rate(learning_data)
        
        # Recent performance
        recent_sessions = self._get_recent_sessions(learning_data, days=7)
        recent_success_rate = len([
            s for s in recent_sessions if s.get("success", False)
        ]) / max(len(recent_sessions), 1)
        
        return {
            "total_sessions": total_sessions,
            "successful_sessions": successful_sessions,
            "overall_success_rate": successful_sessions / max(total_sessions, 1),
            "recent_success_rate": recent_success_rate,
            "total_patterns": len(patterns.get("patterns", [])),
            "pattern_success_rate": pattern_success_rate,
            "learning_improvements": len(learning_data.get("improvements", [])),
            "last_improvement": learning_data.get("last_improvement")
        }
    
    def _find_pattern_match(self, error_type: str, error_message: str) -> Optional[Dict[str, Any]]:
        """Find a matching pattern for the error."""
        patterns = self._load_patterns()
        
        best_match = None
        best_confidence = 0.0
        
        for pattern in patterns.get("patterns", []):
            confidence = self._calculate_pattern_confidence(pattern, error_type, error_message)
            if confidence > best_confidence and confidence > 0.7:  # Threshold
                best_confidence = confidence
                best_match = {
                    "pattern_id": pattern["id"],
                    "confidence": confidence,
                    "pattern": pattern
                }
        
        return best_match
    
    def _calculate_pattern_confidence(self, pattern: Dict[str, Any], error_type: str, error_message: str) -> float:
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
        return solutions.get("solutions", {}).get(pattern_id, {
            "description": "No solution available",
            "steps": [],
            "type": "unknown"
        })
    
    def _generate_analysis(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate new analysis for an error."""
        error_type = error_data.get("type", "unknown")
        error_message = error_data.get("message", "")
        
        # Basic analysis based on error type
        if "import" in error_type.lower() or "module" in error_message.lower():
            solution = {
                "description": "Import/module error detected",
                "steps": [
                    "Check if required module is installed",
                    "Verify import statements",
                    "Check Python path configuration"
                ],
                "type": "import_error"
            }
            confidence = 0.6
        elif "syntax" in error_type.lower():
            solution = {
                "description": "Syntax error detected",
                "steps": [
                    "Check for missing parentheses, brackets, or quotes",
                    "Verify indentation",
                    "Look for typos in keywords"
                ],
                "type": "syntax_error"
            }
            confidence = 0.7
        elif "permission" in error_type.lower() or "access" in error_message.lower():
            solution = {
                "description": "Permission/access error detected",
                "steps": [
                    "Check file permissions",
                    "Verify user has required access",
                    "Check if file is locked by another process"
                ],
                "type": "permission_error"
            },
            confidence = 0.8
        else:
            solution = {
                "description": "Generic error analysis",
                "steps": [
                    "Review error message carefully",
                    "Check error context and stack trace",
                    "Search for similar issues online"
                ],
                "type": "generic"
            }
            confidence = 0.3
        
        return {
            "solution": solution,
            "confidence": confidence
        }
    
    def _generate_debugging_steps(self, error_data: Dict[str, Any], solution: Dict[str, Any]) -> List[str]:
        """Generate specific debugging steps for the error."""
        steps = solution.get("steps", []).copy()
        
        # Add context-specific steps
        context = error_data.get("context", {})
        if context.get("file_path"):
            steps.insert(0, f"Check file: {context['file_path']}")
        
        if context.get("line_number"):
            steps.insert(1, f"Review code around line {context['line_number']}")
        
        return steps
    
    def _generate_prevention_tips(self, error_data: Dict[str, Any]) -> List[str]:
        """Generate tips to prevent similar errors in the future."""
        error_type = error_data.get("type", "unknown")
        
        tips = []
        
        if "import" in error_type.lower():
            tips.extend([
                "Use virtual environments for dependency management",
                "Keep requirements.txt updated",
                "Use absolute imports when possible"
            ])
        elif "syntax" in error_type.lower():
            tips.extend([
                "Use a linter to catch syntax errors early",
                "Enable syntax highlighting in your editor",
                "Review code before running"
            ])
        elif "permission" in error_type.lower():
            tips.extend([
                "Set appropriate file permissions",
                "Use proper user accounts for different operations",
                "Check file locks before operations"
            ])
        
        return tips
    
    def _log_debug_session(self, error_data: Dict[str, Any], solution: Dict[str, Any], 
                          confidence: float, approach: str) -> None:
        """Log a debugging session for learning."""
        utils.ensure_dir(self.debug_log_path.parent)
        entry = {
            "ts": utils.now_iso(),
            "error_data": error_data,
            "solution": solution,
            "confidence": confidence,
            "approach": approach,
            "success": None  # Will be updated later
        }
        with open(self.debug_log_path, "a", encoding="utf-8") as f:
            json.dump(entry, f)
            f.write("\n")
    
    def _learn_from_session(self, error_data: Dict[str, Any], solution: Dict[str, Any], 
                           confidence: float) -> None:
        """Learn from a debugging session."""
        learning_data = self._load_learning_data()
        
        session = {
            "ts": utils.now_iso(),
            "error_data": error_data,
            "solution": solution,
            "confidence": confidence,
            "success": None  # Will be updated when user provides feedback
        }
        
        if "sessions" not in learning_data:
            learning_data["sessions"] = []
        
        learning_data["sessions"].append(session)
        self._save_learning_data(learning_data)
    
    def _extract_pattern(self, error_data: Dict[str, Any], solution: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract a pattern from successful error-solution pair."""
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
            "usage_count": 1
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
            r"FileNotFoundError: \[Errno 2\] No such file or directory"
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
    
    def _improve_pattern(self, pattern: Dict[str, Any], learning_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Improve an existing pattern based on learning data."""
        # Find sessions that used this pattern
        pattern_sessions = [
            s for s in learning_data.get("sessions", [])
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
            "new_success_rate": new_success_rate
        }
    
    def _calculate_success_rate(self, learning_data: Dict[str, Any]) -> float:
        """Calculate overall success rate."""
        sessions = learning_data.get("sessions", [])
        if not sessions:
            return 0.0
        
        successful = len([s for s in sessions if s.get("success", False)])
        return successful / len(sessions)
    
    def _calculate_pattern_success_rate(self, learning_data: Dict[str, Any]) -> float:
        """Calculate success rate for pattern-based solutions."""
        pattern_sessions = [
            s for s in learning_data.get("sessions", [])
            if s.get("approach") == "pattern_match"
        ]
        
        if not pattern_sessions:
            return 0.0
        
        successful = len([s for s in pattern_sessions if s.get("success", False)])
        return successful / len(pattern_sessions)
    
    def _get_recent_sessions(self, learning_data: Dict[str, Any], days: int = 7) -> List[Dict[str, Any]]:
        """Get recent debugging sessions."""
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_iso = cutoff.isoformat()
        
        return [
            s for s in learning_data.get("sessions", [])
            if s.get("ts", "") > cutoff_iso
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
        return utils.read_json(self.learning_path, default={"sessions": [], "improvements": []})
    
    def _save_learning_data(self, learning_data: Dict[str, Any]) -> None:
        """Save learning data."""
        utils.write_json(self.learning_path, learning_data)


def get_smart_debugger(root: Path) -> SmartDebugger:
    """Get smart debugger instance for the project."""
    return SmartDebugger(root)
