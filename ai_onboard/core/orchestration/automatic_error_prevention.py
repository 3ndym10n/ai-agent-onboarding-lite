"""
Automatic Error Prevention System (T4.10) - Proactive error prevention based on learned patterns.

This module provides automatic error prevention that:
- Analyzes code and commands before execution
- Applies learned prevention rules proactively
- Suggests fixes and improvements automatically
- Prevents known error patterns from recurring
- Integrates with validation and linting systems
"""

# Direct import will be added below

import ast
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .pattern_recognition_system import PatternRecognitionSystem


class PreventionRule:
    """A rule for preventing specific types of errors."""

    def __init__(
        self,
        rule_id: str,
        pattern_type: str,
        condition: Callable,
        action: Callable,
        priority: int = 1,
    ):
        self.rule_id = rule_id
        self.pattern_type = pattern_type
        self.condition = condition  # Function that checks if rule applies
        self.action = action  # Function that applies the prevention
        self.priority = priority  # Higher priority rules are checked first


class AutomaticErrorPrevention:
    """System for automatically preventing errors based on learned patterns."""

    def __init__(self, root: Path, pattern_system: PatternRecognitionSystem):
        self.root = root
        self.pattern_system = pattern_system
        self.prevention_dir = root / ".ai_onboard" / "prevention"
        self.prevention_log = self.prevention_dir / "prevention_log.jsonl"

        # Initialize prevention rules
        self.prevention_rules = self._initialize_prevention_rules()

        # Ensure directories exist
        self.prevention_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_prevention_rules(self) -> List[PreventionRule]:
        """Initialize built-in prevention rules."""
        rules = []

        # CLI Error Prevention

        def check_cli_syntax(command: str) -> bool:
            """Check if command has basic CLI syntax issues."""
            # Check for common CLI mistakes
            if "--" in command and "=" not in command and len(command.split()) > 1:
                return True  # Potential argument syntax issue
            return False

        def fix_cli_syntax(command: str) -> Dict[str, Any]:
            """Suggest CLI syntax fixes."""
            suggestions = []
            if "invalid choice" in command.lower():
                suggestions.append("Check command arguments against available options")
            if "unrecognized arguments" in command.lower():
                suggestions.append("Remove or correct invalid command arguments")
            return {
                "action": "cli_syntax_check",
                "suggestions": suggestions,
                "confidence": 0.8,
            }

        rules.append(
            PreventionRule(
                "cli_syntax_check",
                "cli_error",
                check_cli_syntax,
                fix_cli_syntax,
                priority=5,
            )
        )

        # Import Error Prevention

        def check_import_issues(code_content: str) -> bool:
            """Check for potential import issues."""
            try:
                tree = ast.parse(code_content)
                imports: List[str] = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.extend(alias.name for alias in node.names)
                    elif isinstance(node, ast.ImportFrom):
                        imports.append(node.module or "")

                # Check if imports exist in common locations
                missing_imports = []
                for imp in imports:
                    if imp and not self._check_import_exists(imp):
                        missing_imports.append(imp)

                return len(missing_imports) > 0
            except:
                return False

        def fix_import_issues(code_content: str) -> Dict[str, Any]:
            """Suggest import fixes."""
            return {
                "action": "import_validation",
                "suggestions": [
                    "Verify all imports exist in requirements.txt",
                    "Check if virtual environment is activated",
                    "Run 'pip install -r requirements.txt' if needed",
                ],
                "confidence": 0.9,
            }

        rules.append(
            PreventionRule(
                "import_validation",
                "import_error",
                check_import_issues,
                fix_import_issues,
                priority=4,
            )
        )

        # Styling Error Prevention

        def check_styling_issues(code_content: str) -> bool:
            """Check for common styling issues."""
            issues = []

            # Check for trailing whitespace
            lines = code_content.split("\n")
            for i, line in enumerate(lines, 1):
                if line.rstrip() != line:
                    issues.append(f"Line {i}: trailing whitespace")

            # Check for long lines (basic check)
            for i, line in enumerate(lines, 1):
                if len(line) > 120:  # Basic long line check
                    issues.append(f"Line {i}: line too long ({len(line)} chars)")

            return len(issues) > 0

        def fix_styling_issues(code_content: str) -> Dict[str, Any]:
            """Suggest styling fixes."""
            return {
                "action": "code_formatting",
                "suggestions": [
                    "Run code formatter (black, autopep8, etc.)",
                    "Configure editor to trim trailing whitespace",
                    "Set up pre-commit hooks for style checking",
                ],
                "confidence": 0.95,
            }

        rules.append(
            PreventionRule(
                "styling_check",
                "styling_error",
                check_styling_issues,
                fix_styling_issues,
                priority=3,
            )
        )

        # Type Error Prevention

        def check_type_issues(code_content: str) -> bool:
            """Check for potential type issues."""
            try:
                tree = ast.parse(code_content)

                # Basic type checking - look for common patterns
                issues = []

                for node in ast.walk(tree):
                    # Check for None attribute access
                    if isinstance(node, ast.Attribute) and isinstance(
                        node.value, ast.NameConstant
                    ):
                        if node.value.value is None:
                            issues.append("Potential None attribute access")

                    # Check for missing type hints on function parameters (basic)
                    if isinstance(node, ast.FunctionDef):
                        # This is a very basic check - real type checking would be more complex
                        pass

                return len(issues) > 0
            except:
                return False

        def fix_type_issues(code_content: str) -> Dict[str, Any]:
            """Suggest type checking improvements."""
            return {
                "action": "type_safety",
                "suggestions": [
                    "Add type hints to function parameters and return types",
                    "Run mypy or similar type checker",
                    "Use type: ignore comments for intentionally untyped code",
                ],
                "confidence": 0.7,
            }

        rules.append(
            PreventionRule(
                "type_checking",
                "type_error",
                check_type_issues,
                fix_type_issues,
                priority=2,
            )
        )

        # Syntax Error Prevention

        def check_syntax_issues(code_content: str) -> bool:
            """Check for Python syntax issues."""
            try:
                compile(code_content, "<string>", "exec")
                return False  # No syntax errors
            except SyntaxError:
                return True  # Syntax error detected
            except Exception:
                return False  # Other errors don't count as syntax issues

        def fix_syntax_issues(code_content: str) -> Dict[str, Any]:
            """Suggest syntax fixes."""
            try:
                compile(code_content, "<string>", "exec")
            except SyntaxError as e:
                return {
                    "action": "syntax_fix",
                    "suggestions": [
                        f"Fix syntax error: {e.msg}",
                        f"Check line {e.lineno}: {e.text.strip() if e.text else 'N/A'}",
                        "Run python -m py_compile to check syntax",
                        "Use a Python linter like flake8 or pylint",
                    ],
                    "confidence": 0.95,
                }

            return {
                "action": "syntax_check",
                "suggestions": ["Run python -m py_compile to validate syntax"],
                "confidence": 0.8,
            }

        rules.append(
            PreventionRule(
                "syntax_validation",
                "syntax_error",
                check_syntax_issues,
                fix_syntax_issues,
                priority=10,  # High priority - syntax errors prevent execution
            )
        )

        # Runtime Error Prevention (basic)

        def check_runtime_issues(code_content: str) -> bool:
            """Check for potential runtime issues."""
            issues = []

            # Check for common runtime error patterns
            if "int(" in code_content and (
                "str(" not in code_content or "input(" not in code_content
            ):
                # Basic check - int() without input handling
                pass

            # Check for division by zero patterns
            if "/" in code_content or "//" in code_content:
                lines = code_content.split("\n")
                for line in lines:
                    if "/" in line and ("0" in line or "zero" in line.lower()):
                        issues.append("Potential division by zero")

            # Check for None access patterns
            if ".append(" in code_content or ".extend(" in code_content:
                if "None" in code_content and "if " not in code_content:
                    issues.append("Potential None access before list operations")

            return len(issues) > 0

        def fix_runtime_issues(code_content: str) -> Dict[str, Any]:
            """Suggest runtime error fixes."""
            suggestions = [
                "Add error handling with try/except blocks",
                "Validate inputs before operations",
                "Use assertions for critical assumptions",
                "Add logging for debugging runtime issues",
            ]

            return {
                "action": "runtime_safety",
                "suggestions": suggestions,
                "confidence": 0.6,
            }

        rules.append(
            PreventionRule(
                "runtime_safety",
                "runtime_error",
                check_runtime_issues,
                fix_runtime_issues,
                priority=3,
            )
        )

        # File Operation Safety

        def check_file_operation_issues(code_content: str) -> bool:
            """Check for unsafe file operations."""
            issues = []

            # Check for file operations without proper error handling
            file_ops = ["open(", "read(", "write(", ".close("]
            has_file_ops = any(op in code_content for op in file_ops)

            if has_file_ops:
                # Check if there's proper error handling
                has_try = "try:" in code_content
                has_with = "with " in code_content and "open(" in code_content

                if not (has_try or has_with):
                    issues.append("File operations without proper error handling")

            # Check for path traversal vulnerabilities
            if ".." in code_content and (
                "path" in code_content.lower() or "file" in code_content.lower()
            ):
                issues.append("Potential path traversal vulnerability")

            return len(issues) > 0

        def fix_file_operation_issues(code_content: str) -> Dict[str, Any]:
            """Suggest file operation safety fixes."""
            suggestions = [
                "Use 'with' statements for file operations",
                "Add try/except blocks around file operations",
                "Validate file paths before opening",
                "Check file permissions before operations",
                "Use pathlib for path operations",
            ]

            return {
                "action": "file_safety",
                "suggestions": suggestions,
                "confidence": 0.8,
            }

        rules.append(
            PreventionRule(
                "file_safety",
                "file_error",
                check_file_operation_issues,
                fix_file_operation_issues,
                priority=6,
            )
        )

        # Memory/Resource Leak Prevention

        def check_resource_leak_issues(code_content: str) -> bool:
            """Check for potential resource leaks."""
            issues = []

            # Check for opened resources that might not be closed
            opens = code_content.count("open(")
            closes = code_content.count(".close()") + code_content.count("with ")

            if opens > closes + 2:  # Allow some margin
                issues.append("Potential file handle leaks")

            # Check for database connections, sockets, etc.
            resource_indicators = ["connect(", "socket(", "cursor("]
            for indicator in resource_indicators:
                if indicator in code_content and ".close()" not in code_content:
                    issues.append(f"Potential resource leak: {indicator[:-1]}")

            return len(issues) > 0

        def fix_resource_leak_issues(code_content: str) -> Dict[str, Any]:
            """Suggest resource leak fixes."""
            suggestions = [
                "Use context managers (with statements) for resources",
                "Ensure all opened resources are properly closed",
                "Use try/finally blocks for cleanup",
                "Consider using resource management libraries",
            ]

            return {
                "action": "resource_management",
                "suggestions": suggestions,
                "confidence": 0.7,
            }

        rules.append(
            PreventionRule(
                "resource_management",
                "resource_error",
                check_resource_leak_issues,
                fix_resource_leak_issues,
                priority=4,
            )
        )

        return rules

    def _check_import_exists(self, import_name: str) -> bool:
        """Check if an import exists in the current environment."""
        try:
            __import__(import_name)
            return True
        except ImportError:
            return False

    def analyze_and_prevent(
        self,
        content: str,
        content_type: str = "code",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze content and provide prevention recommendations.

        Args:
            content: Content to analyze (code, command, etc.)
            content_type: Type of content ("code", "command", "config", etc.)
            context: Additional context information

        Returns:
            Dictionary with prevention analysis and recommendations
        """
        if context is None:
            context = {}

        result: Dict[str, Any] = {
            "content_type": content_type,
            "prevention_applied": [],
            "recommendations": [],
            "risk_level": "low",
            "confidence": 0.0,
        }

        # Apply built-in prevention rules
        for rule in sorted(
            self.prevention_rules, key=lambda r: r.priority, reverse=True
        ):
            try:
                if rule.condition(content):
                    prevention_result = rule.action(content)
                    result["prevention_applied"].append(
                        {
                            "rule_id": rule.rule_id,
                            "pattern_type": rule.pattern_type,
                            "prevention": prevention_result,
                        }
                    )

                    # Update overall confidence
                    result["confidence"] = max(
                        result["confidence"], prevention_result.get("confidence", 0)
                    )

                    # Record that an error was prevented by this rule
                    try:
                        from pathlib import Path

                        from ..continuous_improvement.learning_persistence import (
                            LearningPersistenceManager,
                        )

                        # Use the pattern system to record error prevention
                        # Since we don't have direct access to pattern system here,
                        # we'll record it directly in the persistence system
                        persistence = LearningPersistenceManager(Path("."))
                        persistence.record_error_prevented(
                            rule.rule_id,
                            rule.pattern_type,
                            {
                                "content_type": content_type,
                                "rule_id": rule.rule_id,
                                "confidence": prevention_result.get("confidence", 0),
                            },
                        )
                    except Exception as e:
                        # Don't fail if recording fails
                        pass

            except Exception as e:
                # Log rule failure but continue
                self._log_prevention_event(
                    "rule_error",
                    {
                        "rule_id": rule.rule_id,
                        "error": str(e),
                        "content_type": content_type,
                    },
                )

        # Apply learned pattern prevention
        pattern_preventions = self._apply_learned_prevention(
            content, content_type, context
        )
        result["recommendations"].extend(pattern_preventions)

        # Determine risk level
        if result["confidence"] > 0.8:
            result["risk_level"] = "high"
        elif result["confidence"] > 0.6:
            result["risk_level"] = "medium"

        # Log the prevention analysis
        self._log_prevention_event(
            "analysis_completed",
            {
                "content_type": content_type,
                "preventions_applied": len(result["prevention_applied"]),
                "recommendations": len(result["recommendations"]),
                "risk_level": result["risk_level"],
                "confidence": result["confidence"],
            },
        )

        return result

    def _apply_learned_prevention(
        self, content: str, content_type: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply prevention based on learned error patterns."""
        recommendations = []

        # Get prevention recommendations from pattern system
        prevention_suggestions = self.pattern_system.get_prevention_recommendations(
            {
                "type": f"prevention_check_{content_type}",
                "message": f"Analyzing {content_type} for potential issues",
                "content": content[:500],  # Limit content size
                "context": context,
            }
        )

        for suggestion in prevention_suggestions:
            recommendations.append(
                {
                    "type": "learned_pattern",
                    "suggestion": suggestion,
                    "source": "pattern_recognition",
                    "confidence": 0.8,
                }
            )

        return recommendations

    def prevent_cli_errors(
        self, command: str, args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Specifically analyze CLI commands for potential errors.

        Args:
            command: The command being executed
            args: Command arguments

        Returns:
            Prevention analysis for CLI command
        """
        if args is None:
            args = []

        full_command = f"{command} {' '.join(args)}"

        return self.analyze_and_prevent(
            full_command,
            content_type="command",
            context={"command": command, "args": args},
        )

    def prevent_code_errors(
        self, code_content: str, file_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Analyze code content for potential errors.

        Args:
            code_content: The code to analyze
            file_path: Path to the file (if applicable)

        Returns:
            Prevention analysis for code
        """
        from .tool_usage_tracker import track_tool_usage

        track_tool_usage(
            "automatic_error_prevention",
            "ai_system",
            {
                "action": "analyze_code",
                "file": str(file_path) if file_path else "unknown",
            },
            "success",
        )

        context = {}
        if file_path:
            context["file_path"] = str(file_path)
            context["file_extension"] = file_path.suffix

        return self.analyze_and_prevent(
            code_content, content_type="code", context=context
        )

    def prevent_command_execution(
        self, command: str, args: Optional[List[str]] = None, cwd: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Analyze a command before execution and provide prevention recommendations.

        Args:
            command: The command to be executed
            args: Command arguments
            cwd: Current working directory for execution

        Returns:
            Prevention analysis with execution recommendations
        """
        from .tool_usage_tracker import track_tool_usage

        track_tool_usage(
            "automatic_error_prevention",
            "ai_system",
            {
                "action": "prevent_command",
                "command": command[:50],
            },
            "success",
        )

        context = {
            "command_type": "execution",
            "working_directory": str(cwd) if cwd else None,
        }

        if args:
            context["args"] = args  # type: ignore[assignment]

        # Analyze the command for potential issues
        analysis = self.analyze_and_prevent(
            command, content_type="command", context=context
        )

        # Add command-specific checks
        command_checks = self._check_command_safety(command, args, cwd)
        analysis["command_checks"] = command_checks

        # Add full command string for analysis
        full_command = command
        if args:
            full_command += " " + " ".join(args)
        analysis["command_checks"]["full_command"] = full_command

        # Determine if command should be blocked
        should_block = self._should_block_command(analysis, command_checks)

        analysis["should_block"] = should_block
        analysis["block_reason"] = (
            self._get_block_reason(analysis, command_checks) if should_block else None
        )

        return analysis

    def _check_command_safety(
        self, command: str, args: Optional[List[str]], cwd: Optional[Path]
    ) -> Dict[str, Any]:
        """Perform safety checks on a command before execution."""
        checks: Dict[str, Any] = {
            "path_safety": True,
            "permission_safety": True,
            "destructive_operations": False,
            "network_operations": False,
            "warnings": [],
        }

        # Check for potentially destructive operations
        destructive_commands = ["rm", "del", "format", "fdisk", "mkfs"]
        if any(cmd in command.lower() for cmd in destructive_commands):
            checks["destructive_operations"] = True
            checks["warnings"].append(
                "Command contains potentially destructive operations"
            )

        # Check for network operations
        network_commands = ["curl", "wget", "ssh", "scp", "ftp"]
        if any(cmd in command.lower() for cmd in network_commands):
            checks["network_operations"] = True

        # Check for path safety (basic check)
        if cwd:
            from pathlib import Path

            cwd_path = Path(cwd)
            if not cwd_path.exists():
                checks["path_safety"] = False
                checks["warnings"].append(f"Working directory does not exist: {cwd}")

        # Check command arguments for suspicious patterns
        full_command = command
        if args:
            full_command += " " + " ".join(args)

        suspicious_patterns = [
            "&&",
            "||",
            "|",
            ">",
            ">>",
            "<",  # Shell operators
            "..",  # Directory traversal
            "*",
            "?",
            "[",
            "]",  # Wildcards
        ]

        for pattern in suspicious_patterns:
            if pattern in full_command and pattern not in [
                "&&",
                "||",
                "|",
            ]:  # Allow basic operators
                checks["warnings"].append(
                    f"Command contains potentially unsafe pattern: {pattern}"
                )

        return checks

    def _should_block_command(
        self, analysis: Dict[str, Any], command_checks: Dict[str, Any]
    ) -> bool:
        """Determine if a command should be blocked based on analysis."""
        # Always block destructive operations with root/system paths
        if command_checks.get("destructive_operations"):
            command_str = analysis.get("command_checks", {}).get("full_command", "")
            # Block rm/del operations on root or system paths
            dangerous_paths = ["/", "C:", "C:\\", "/root", "/etc", "/usr"]
            if any(path in command_str for path in dangerous_paths):
                return True
            # Block if combined with high prevention confidence
            if analysis.get("confidence", 0) > 0.6:
                return True

        # Block if path safety issues
        if not command_checks.get("path_safety", True):
            return True

        # Block if very high prevention confidence (>85%)
        if analysis.get("confidence", 0) > 0.85:
            return True

        # Block commands with many suspicious patterns
        suspicious_count = len(command_checks.get("warnings", []))
        if suspicious_count >= 3:  # 3 or more warnings
            return True

        return False

    def _get_block_reason(
        self, analysis: Dict[str, Any], command_checks: Dict[str, Any]
    ) -> str:
        """Get the reason why a command should be blocked."""
        reasons = []

        if command_checks.get("destructive_operations"):
            reasons.append("Command contains destructive operations")

        if not command_checks.get("path_safety", True):
            reasons.append("Unsafe working directory")

        if analysis.get("confidence", 0) > 0.9:
            reasons.append("High confidence of command failure")

        if analysis.get("prevention_applied"):
            reasons.append(
                f"Prevention rules triggered: {len(analysis['prevention_applied'])}"
            )

        return "; ".join(reasons) if reasons else "Command blocked by safety analysis"

    def apply_automatic_fixes(
        self, content: str, prevention_result: Dict[str, Any]
    ) -> Tuple[str, List[str]]:
        """
        Apply automatic fixes based on prevention analysis.

        Args:
            content: Original content
            prevention_result: Result from analyze_and_prevent

        Returns:
            Tuple of (fixed_content, applied_fixes)
        """
        fixed_content = content
        applied_fixes = []

        # Apply styling fixes automatically
        if prevention_result.get("content_type") == "code":
            for prevention in prevention_result.get("prevention_applied", []):
                if prevention.get("prevention", {}).get("action") == "code_formatting":
                    try:
                        # Basic automatic fixes
                        lines = fixed_content.split("\n")
                        fixed_lines = []

                        for line in lines:
                            # Remove trailing whitespace
                            fixed_line = line.rstrip()
                            fixed_lines.append(fixed_line)

                        fixed_content = "\n".join(fixed_lines)
                        applied_fixes.append("Removed trailing whitespace")
                    except Exception as e:
                        applied_fixes.append(f"Failed to apply styling fixes: {e}")

        return fixed_content, applied_fixes

    def _log_prevention_event(
        self, event_type: str, event_data: Dict[str, Any]
    ) -> None:
        """Log a prevention event."""
        try:
            import time

            log_entry = {
                "timestamp": time.time(),
                "event_type": event_type,
                "event_data": event_data,
            }

            with open(self.prevention_log, "a", encoding="utf-8") as f:
                f.write(f"{log_entry}\n")

        except Exception as e:
            # Don't crash if logging fails
            pass

    def get_prevention_stats(self) -> Dict[str, Any]:
        """Get statistics about prevention activities."""
        try:
            stats = {
                "preventions_applied": 0,
                "recommendations_given": 0,
                "high_risk_preventions": 0,
                "auto_fixes_applied": 0,
            }

            if self.prevention_log.exists():
                with open(self.prevention_log, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            entry = eval(
                                line.strip()
                            )  # Safe since we control the format
                            event_data = entry.get("event_data", {})

                            if entry["event_type"] == "analysis_completed":
                                stats["preventions_applied"] += event_data.get(
                                    "preventions_applied", 0
                                )
                                stats["recommendations_given"] += event_data.get(
                                    "recommendations", 0
                                )

                                if event_data.get("risk_level") == "high":
                                    stats["high_risk_preventions"] += 1

            return stats

        except Exception as e:
            return {"error": f"Failed to load prevention stats: {e}"}
