"""
Syntax Validator - Meta-level error prevention for tool-generated Python code.

This module provides syntax validation for Python code before execution,
preventing common syntax errors in tool calls and providing helpful error messages.
"""

import re
from typing import Dict, List, Optional, Tuple


class SyntaxValidator:
    """Validates Python syntax and provides error correction suggestions."""


    def __init__(self):
        # Common syntax error patterns and their fixes
        self.error_patterns = {
            "unterminated_string": {
                "pattern": r'(?<!\\)"[^"]*$',
                "suggestion": "Add missing closing quote",
                "fix": lambda code: self._fix_unterminated_string(code),
            },
            "unterminated_fstring": {
                "pattern": r'f"[^"]*$|f\'[^\']*$',
                "suggestion": "Add missing closing quote to f-string",
                "fix": lambda code: self._fix_unterminated_fstring(code),
            },
            "mixed_quotes_fstring": {
                "pattern": r'f"[^"]*\'|f\'[^\'"]*"', "suggestion": "Use consistent quotes in f-string", "fix": lambda code: self._fix_mixed_quotes(code),
            },
            "unclosed_parenthesis": {
                "pattern": r"\([^)]*$",
                "suggestion": "Add missing closing parenthesis",
                "fix": lambda code: self._fix_unclosed_paren(code),
            },
            "unclosed_bracket": {
                "pattern": r"\[[^\]]*$",
                "suggestion": "Add missing closing bracket",
                "fix": lambda code: self._fix_unclosed_bracket(code),
            },
            "unclosed_brace": {
                "pattern": r"\{[^}]*$",
                "suggestion": "Add missing closing brace",
                "fix": lambda code: self._fix_unclosed_brace(code),
            },
        }


    def validate_syntax(self, code: str) -> Dict:
        """
        Validate Python syntax and return detailed results.

        Args:
            code: Python code string to validate

        Returns:
            Dict with validation results and suggestions
        """
        result = {
            "valid": False,
            "error": None,
            "line_number": None,
            "error_type": None,
            "suggestion": None,
            "auto_fix": None,
            "confidence": 0.0,
        }

        try:
            # Attempt to compile the code
            compile(code, "<string>", "exec")
            result["valid"] = True
            result["confidence"] = 1.0
            return result

        except SyntaxError as e:
            # Syntax error detected
            result["error"] = str(e)
            result["line_number"] = e.lineno
            result["error_type"] = "syntax_error"

            # Try to identify the specific error pattern
            pattern_match = self._identify_error_pattern(code, str(e))
            if pattern_match:
                result["suggestion"] = pattern_match["suggestion"]
                result["auto_fix"] = pattern_match["fix"](code)
                result["confidence"] = pattern_match["confidence"]
            else:
                result["suggestion"] = "Review syntax around the error location"
                result["confidence"] = 0.5

            return result

        except Exception as e:
            # Other compilation errors
            result["error"] = f"Compilation error: {str(e)}"
            result["error_type"] = "compilation_error"
            result["suggestion"] = "Check for import errors or undefined names"
            result["confidence"] = 0.3
            return result


    def _identify_error_pattern(self, code: str, error_msg: str) -> Optional[Dict]:
        """
        Identify the specific error pattern from code and error message.

        Returns dict with suggestion, fix function, and confidence score.
        """
        # Check for unterminated string literals
        if "unterminated string literal" in error_msg.lower():
            if 'f"' in code or "f'" in code:
                return {
                    "suggestion": "Add missing closing quote to f-string",
                    "fix": self._fix_unterminated_fstring,
                    "confidence": 0.9,
                }
            else:
                return {
                    "suggestion": "Add missing closing quote to string",
                    "fix": self._fix_unterminated_string,
                    "confidence": 0.9,
                }

        # Check for mixed quotes in f-strings
        if 'f"' in code and "'" in code and '"' in code:
            lines = code.split("\n")
            for line in lines:
                if 'f"' in line and ("'" in line or '"' in line):
                    return {
                        "suggestion": "Use consistent quotes in f-string",
                        "fix": self._fix_mixed_quotes,
                        "confidence": 0.8,
                    }

        # Check for common patterns
        for pattern_name, pattern_info in self.error_patterns.items():
            if re.search(pattern_info["pattern"], code):
                return {
                    "suggestion": pattern_info["suggestion"],
                    "fix": pattern_info["fix"],
                    "confidence": 0.7,
                }

        return None


    def _fix_unterminated_string(self, code: str) -> str:
        """Attempt to fix unterminated string literals."""
        # Simple fix: add closing quote at end
        if code.count('"') % 2 == 1:
            return code + '"'
        elif code.count("'") % 2 == 1:
            return code + "'"
        return code


    def _fix_unterminated_fstring(self, code: str) -> str:
        """Attempt to fix unterminated f-strings."""
        # Look for unterminated f-string and add closing quote
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith('f"') and not line.rstrip().endswith('"'):
                lines[i] = line.rstrip() + '"'
                break
            elif line.strip().startswith("f'") and not line.rstrip().endswith("'"):
                lines[i] = line.rstrip() + "'"
                break
        return "\n".join(lines)


    def _fix_mixed_quotes(self, code: str) -> str:
        """Attempt to fix mixed quotes in f-strings."""
        # This is complex - for now, suggest manual fix
        return code  # Return unchanged, manual fix needed


    def _fix_unclosed_paren(self, code: str) -> str:
        """Attempt to fix unclosed parentheses."""
        return code + ")"


    def _fix_unclosed_bracket(self, code: str) -> str:
        """Attempt to fix unclosed brackets."""
        return code + "]"


    def _fix_unclosed_brace(self, code: str) -> str:
        """Attempt to fix unclosed braces."""
        return code + "}"


    def get_error_statistics(self) -> Dict:
        """Get statistics about common syntax errors encountered."""
        # This could be expanded to track error patterns over time
        return {
            "common_errors": [
                "unterminated string literals",
                "mixed quotes in f-strings",
                "unclosed parentheses/brackets",
                "missing colons in control structures",
            ],
            "prevention_rate": 0.8,  # Estimated 80% prevention rate
            "auto_fix_rate": 0.6,  # Estimated 60% can be auto-fixed
        }

# Convenience function for quick validation

def validate_python_syntax(code: str) -> Dict:
    """
    Quick validation function for Python syntax.

    Args:
        code: Python code string to validate

    Returns:
        Validation result dictionary
    """
    validator = SyntaxValidator()
    return validator.validate_syntax(code)

# Function to validate and potentially auto-fix code

def validate_and_fix(code: str) -> Tuple[bool, str, str]:
    """
    Validate code and attempt auto-fix if possible.

    Returns:
        (is_valid, error_message, fixed_code)
    """
    validator = SyntaxValidator()
    result = validator.validate_syntax(code)

    if result["valid"]:
        return True, "", code

    error_msg = result.get("error", "Unknown syntax error")
    if result.get("auto_fix"):
        return False, error_msg, result["auto_fix"]

    return False, error_msg, code
