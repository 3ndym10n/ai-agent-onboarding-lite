"""
Code Quality Analysis Engine

This module provides comprehensive code quality analysis including:
- Unused import detection
- Dead code detection (unused functions, classes, methods)
- Code complexity analysis
- Code quality metrics and scoring

Author: AI Assistant
"""

import ast
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ..core.utils import read_json, write_json
from .tool_usage_tracker import get_tool_tracker


@dataclass

class CodeQualityIssue:
    """Represents a code quality issue found during analysis."""

    file_path: str
    line_number: int
    issue_type: str  # 'unused_import', 'dead_code', 'complexity', etc.
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    suggestion: Optional[str] = None
    context: Optional[str] = None


@dataclass

class CodeQualityMetrics:
    """Code quality metrics for a file or module."""

    file_path: str
    lines_of_code: int = 0
    complexity_score: float = 0.0
    import_count: int = 0
    function_count: int = 0
    class_count: int = 0
    unused_imports: int = 0
    dead_code_count: int = 0
    quality_score: float = 0.0  # 0-100 scale


@dataclass

class CodeQualityAnalysisResult:
    """Complete analysis result for the codebase."""

    files_analyzed: int = 0
    total_issues: int = 0
    issues_by_type: Dict[str, int] = field(default_factory=dict)
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    file_metrics: Dict[str, CodeQualityMetrics] = field(default_factory=dict)
    issues: List[CodeQualityIssue] = field(default_factory=list)
    overall_quality_score: float = 0.0


class CodeQualityAnalyzer:
    """
    Main code quality analysis engine.

    Provides static analysis of Python codebases to identify:
    - Unused imports
    - Dead code (unused functions, classes, variables)
    - Code complexity issues
    - Code quality metrics
    """


    def __init__(self, root_path: Path, exclude_patterns: Optional[List[str]] = None):
        """
        Initialize the code quality analyzer.

        Args:
            root_path: Root directory to analyze
            exclude_patterns: List of glob patterns to exclude from analysis
        """
        self.root_path = root_path
        self.exclude_patterns = exclude_patterns or [
            "__pycache__",
            "*.pyc",
            ".git",
            ".ai_onboard",
            "build",
            "dist",
            "*.egg-info",
            "node_modules",
            "venv",
            ".venv",
            "env",
            ".env",
        ]

        # Analysis state
        self.import_usage: Dict[str, Set[str]] = defaultdict(
            set
        )  # import_name -> files_using_it
        self.function_definitions: Dict[str, Set[str]] = defaultdict(
            set
        )  # func_name -> files_defining_it
        self.function_usage: Dict[str, Set[str]] = defaultdict(
            set
        )  # func_name -> files_using_it
        self.class_definitions: Dict[str, Set[str]] = defaultdict(
            set
        )  # class_name -> files_defining_it
        self.class_usage: Dict[str, Set[str]] = defaultdict(
            set
        )  # class_name -> files_using_it
        self.variable_definitions: Dict[str, Set[str]] = defaultdict(
            set
        )  # var_name -> files_defining_it
        self.variable_usage: Dict[str, Set[str]] = defaultdict(
            set
        )  # var_name -> files_using_it


    def analyze_codebase(self) -> CodeQualityAnalysisResult:
        """
        Perform complete codebase analysis.

        Returns:
            CodeQualityAnalysisResult with comprehensive analysis
        """
        print("🔍 Starting comprehensive code quality analysis...")

        # Track tool usage
        tracker = get_tool_tracker(self.root_path)

        # Phase 1: Collect all definitions and imports
        print("📊 Phase 1: Collecting code definitions and imports...")
        python_files = self._find_python_files()
        print(f"   Found {len(python_files)} Python files to analyze")

        for file_path in python_files:
            try:
                self._analyze_file_definitions(file_path)
            except Exception as e:
                print(f"   ⚠️  Error analyzing {file_path}: {e}")

        tracker.track_tool_usage(
            tool_name="code_quality_analyzer_definitions",
            tool_type="analysis",
            parameters={"files_processed": len(python_files)},
            result="completed",
        )

        # Phase 2: Analyze usage patterns
        print("🔗 Phase 2: Analyzing usage patterns...")
        for file_path in python_files:
            try:
                self._analyze_file_usage(file_path)
            except Exception as e:
                print(f"   ⚠️  Error analyzing usage in {file_path}: {e}")

        tracker.track_tool_usage(
            tool_name="code_quality_analyzer_usage",
            tool_type="analysis",
            parameters={"files_processed": len(python_files)},
            result="completed",
        )

        # Phase 3: Detect issues
        print("🎯 Phase 3: Detecting quality issues...")
        result = CodeQualityAnalysisResult()

        for file_path in python_files:
            try:
                file_issues, file_metrics = self._analyze_file_quality(file_path)
                result.issues.extend(file_issues)
                result.file_metrics[file_path] = file_metrics
                result.files_analyzed += 1
            except Exception as e:
                print(f"   ⚠️  Error analyzing quality in {file_path}: {e}")

        tracker.track_tool_usage(
            tool_name="code_quality_analyzer_issues",
            tool_type="analysis",
            parameters={
                "files_analyzed": result.files_analyzed,
                "issues_found": len(result.issues),
            },
            result="completed",
        )

        # Phase 4: Calculate aggregate metrics
        print("📈 Phase 4: Calculating aggregate metrics...")
        result.total_issues = len(result.issues)

        # Count issues by type and severity
        for issue in result.issues:
            result.issues_by_type[issue.issue_type] = (
                result.issues_by_type.get(issue.issue_type, 0) + 1
            )
            result.issues_by_severity[issue.severity] = (
                result.issues_by_severity.get(issue.severity, 0) + 1
            )

        # Calculate overall quality score
        if result.files_analyzed > 0:
            total_score = sum(
                metrics.quality_score for metrics in result.file_metrics.values()
            )
            result.overall_quality_score = total_score / result.files_analyzed

        print("✅ Code quality analysis complete!")

        # Final tracking
        tracker.track_tool_usage(
            tool_name="code_quality_analyzer_complete",
            tool_type="analysis",
            parameters={
                "total_files": result.files_analyzed,
                "total_issues": result.total_issues,
                "quality_score": round(result.overall_quality_score, 1),
            },
            result="completed",
        )

        return result


    def _find_python_files(self) -> List[str]:
        """Find all Python files in the codebase, respecting exclude patterns."""
        python_files = []

        for root, dirs, files in os.walk(self.root_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not self._is_excluded(os.path.join(root, d))]

            for file in files:
                if file.endswith(".py") and not self._is_excluded(
                    os.path.join(root, file)
                ):
                    python_files.append(os.path.join(root, file))

        return python_files


    def _is_excluded(self, path: str) -> bool:
        """Check if a path should be excluded from analysis."""
        path_str = str(path)

        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return True

            # Handle glob-like patterns
            if "*" in pattern:
                import fnmatch

                if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(
                    os.path.basename(path_str), pattern
                ):
                    return True

        return False


    def _analyze_file_definitions(self, file_path: str) -> None:
        """Analyze a file to extract definitions and imports."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_name = alias.name.split(".")[0]  # Get root module name
                        self.import_usage[import_name].add(file_path)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        import_name = node.module.split(".")[0]
                        self.import_usage[import_name].add(file_path)

                # Extract function definitions
                elif isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    self.function_definitions[func_name].add(file_path)

                # Extract class definitions
                elif isinstance(node, ast.ClassDef):
                    class_name = node.name
                    self.class_definitions[class_name].add(file_path)

                # Extract variable assignments (simple case)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            # Only track if it's likely a module-level variable
                            if not any(
                                isinstance(
                                    parent,
                                    (
                                        ast.FunctionDef,
                                        ast.ClassDef,
                                        ast.AsyncFunctionDef,
                                    ),
                                )
                                for parent in self._get_parents(tree, target)
                            ):
                                self.variable_definitions[var_name].add(file_path)

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"   ⚠️  Error parsing {file_path}: {e}")


    def _analyze_file_usage(self, file_path: str) -> None:
        """Analyze a file to extract usage patterns."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)

            # Extract function calls, attribute access, etc.
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Function/method calls
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        self.function_usage[func_name].add(file_path)
                    elif isinstance(node.func, ast.Attribute):
                        # Could be method call - analyze later
                        pass

                elif isinstance(node, ast.Name):
                    # Variable usage
                    var_name = node.id
                    if isinstance(node.ctx, (ast.Load, ast.AugLoad)):
                        self.variable_usage[var_name].add(file_path)

                elif isinstance(node, ast.Attribute):
                    # Could be class attribute access
                    if isinstance(node.value, ast.Name):
                        class_name = node.value.id
                        self.class_usage[class_name].add(file_path)

        except SyntaxError:
            pass
        except Exception as e:
            print(f"   ⚠️  Error analyzing usage in {file_path}: {e}")


    def _analyze_file_quality(
        self, file_path: str
    ) -> Tuple[List[CodeQualityIssue], CodeQualityMetrics]:
        """Analyze quality of a specific file."""
        issues = []
        metrics = CodeQualityMetrics(file_path=file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                content = "".join(lines)

            metrics.lines_of_code = len([line for line in lines if line.strip()])

            tree = ast.parse(content, filename=file_path)

            # Analyze imports
            import_lines = self._extract_imports_from_file(content)
            metrics.import_count = len(import_lines)

            # Check for unused imports
            unused_imports = self._find_unused_imports(file_path, import_lines)
            for import_name, line_num in unused_imports:
                issues.append(
                    CodeQualityIssue(
                        file_path=file_path,
                        line_number=line_num,
                        issue_type="unused_import",
                        severity="medium",
                        message=f"Unused import: {import_name}",
                        suggestion="Remove unused import to clean up the code",
                    )
                )
                metrics.unused_imports += 1

            # Count functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics.function_count += 1
                elif isinstance(node, ast.ClassDef):
                    metrics.class_count += 1

            # Check for dead code (unused functions)
            dead_functions = self._find_dead_functions(file_path)
            for func_name in dead_functions:
                # Find line number
                func_line = self._find_function_line(content, func_name)
                if func_line:
                    issues.append(
                        CodeQualityIssue(
                            file_path=file_path,
                            line_number=func_line,
                            issue_type="dead_code",
                            severity="high",
                            message=f"Dead code: Function '{func_name}' is never used",
                            suggestion="Consider removing unused function or adding '# noqa' if intentionally unused",
                        )
                    )
                    metrics.dead_code_count += 1

            # Calculate complexity
            metrics.complexity_score = self._calculate_complexity(tree)

            # Calculate overall quality score
            metrics.quality_score = self._calculate_quality_score(metrics, issues)

        except SyntaxError:
            issues.append(
                CodeQualityIssue(
                    file_path=file_path,
                    line_number=1,
                    issue_type="syntax_error",
                    severity="critical",
                    message="File contains syntax errors",
                    suggestion="Fix syntax errors before analysis",
                )
            )
        except Exception as e:
            issues.append(
                CodeQualityIssue(
                    file_path=file_path,
                    line_number=1,
                    issue_type="analysis_error",
                    severity="medium",
                    message=f"Error during analysis: {e}",
                    suggestion="Check file for issues",
                )
            )

        return issues, metrics


    def _extract_imports_from_file(self, content: str) -> List[Tuple[str, int]]:
        """Extract imports and their line numbers from file content."""
        imports = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                # Simple extraction - could be improved
                if "import " in line:
                    parts = line.split("import ")[1].split(",")
                    for part in parts:
                        import_name = part.split(" as ")[0].strip()
                        imports.append((import_name.split(".")[0], i))
                elif "from " in line:
                    module_part = line.split("from ")[1].split(" import ")[0]
                    imports.append((module_part.split(".")[0], i))

        return imports


    def _find_unused_imports(
        self, file_path: str, imports: List[Tuple[str, int]]
    ) -> List[Tuple[str, int]]:
        """Find unused imports in a file."""
        unused = []

        for import_name, line_num in imports:
            # Check if this import is used anywhere in the codebase
            used_files = self.import_usage.get(import_name, set())
            if file_path not in used_files:
                # Also check if it's a standard library import that might be used indirectly
                if not self._is_standard_library_import(import_name):
                    unused.append((import_name, line_num))

        return unused


    def _find_dead_functions(self, file_path: str) -> List[str]:
        """Find unused functions defined in a file."""
        dead_functions = []

        for func_name, defining_files in self.function_definitions.items():
            if file_path in defining_files:
                # Check if this function is used anywhere
                used_files = self.function_usage.get(func_name, set())
                if not used_files:
                    # Also check if it's a special method or main function
                    if not (func_name.startswith("_") or func_name == "main"):
                        dead_functions.append(func_name)

        return dead_functions


    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate code complexity score."""
        complexity = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1  # AND/OR chains
            elif isinstance(node, ast.FunctionDef):
                # Nested functions increase complexity
                complexity += 1

        return complexity


    def _calculate_quality_score(
        self, metrics: CodeQualityMetrics, issues: List[CodeQualityIssue]
    ) -> float:
        """Calculate overall quality score (0-100)."""
        score = 100.0

        # Count issues by severity
        critical_count = sum(1 for issue in issues if issue.severity == "critical")
        high_count = sum(1 for issue in issues if issue.severity == "high")
        medium_count = sum(1 for issue in issues if issue.severity == "medium")
        low_count = sum(1 for issue in issues if issue.severity == "low")

        # Deduct points for issues (scaled down for complex codebases)
        score -= min(30, critical_count * 10)  # Max 30 points for critical
        score -= min(25, high_count * 3)  # Max 25 points for high
        score -= min(20, medium_count * 1)  # Max 20 points for medium
        score -= min(10, low_count * 0.5)  # Max 10 points for low

        # Deduct points for complexity (gentler scaling)
        if metrics.complexity_score > 15:
            score -= min(15, (metrics.complexity_score - 15) * 0.5)

        # Deduct points for unused imports (capped and scaled)
        if metrics.unused_imports > 5:
            score -= min(10, (metrics.unused_imports - 5) * 0.5)

        # Deduct points for dead code (capped and scaled)
        if metrics.dead_code_count > 3:
            score -= min(15, (metrics.dead_code_count - 3) * 1.5)

        # Bonus for good practices
        if metrics.lines_of_code > 0:
            # Reward reasonable file sizes (not too big, not too small)
            if 50 <= metrics.lines_of_code <= 1000:
                score += 5

        return max(0.0, min(100.0, score))


    def _is_standard_library_import(self, import_name: str) -> bool:
        """Check if an import is from Python's standard library."""
        import pathlib
        import re

        # Common standard library modules
        stdlib_modules = {
            "sys",
            "os",
            "re",
            "json",
            "pathlib",
            "collections",
            "itertools",
            "functools",
            "operator",
            "datetime",
            "time",
            "math",
            "random",
            "string",
            "io",
            "typing",
            "enum",
            "dataclasses",
            "abc",
            "ast",
            "inspect",
            "importlib",
            "pkgutil",
            "linecache",
            "pickle",
            "copyreg",
            "copy",
            "pprint",
            "reprlib",
            "enum",
            "numbers",
            "cmath",
            "decimal",
            "fractions",
            "statistics",
            "zlib",
            "gzip",
            "bz2",
            "lzma",
            "zipfile",
            "tarfile",
            "csv",
            "configparser",
            "netrc",
            "xdrlib",
            "plistlib",
            "hashlib",
            "hmac",
            "secrets",
            "ssl",
            "socket",
            "mmap",
            "contextvars",
            "concurrent",
            "threading",
            "multiprocessing",
            "subprocess",
            "sched",
            "queue",
            "_thread",
            "dummy_thread",
            "io",
            "codecs",
            "unicodedata",
            "stringprep",
            "re",
            "difflib",
            "textwrap",
            "unicodedata",
            "stringprep",
            "re",
            "locale",
            "gettext",
            "argparse",
            "optparse",
            "getopt",
            "readline",
            "rlcompleter",
            "shutil",
            "glob",
            "fnmatch",
            "linecache",
            "tokenize",
            "token",
            "keyword",
            "ast",
            "symtable",
            "symbol",
            "tokenize",
            "tabnanny",
            "pyclbr",
            "py_compile",
            "compileall",
            "dis",
            "pickletools",
            "platform",
            "errno",
            "ctypes",
            "msvcrt",
            "winreg",
            "winsound",
            "posix",
            "pwd",
            "spwd",
            "grp",
            "crypt",
            "termios",
            "tty",
            "pty",
            "fcntl",
            "pipes",
            "resource",
            "nis",
            "syslog",
            "optparse",
            "nntplib",
            "poplib",
            "imaplib",
            "smtplib",
            "smtpd",
            "telnetlib",
            "uuid",
            "socketserver",
            "http",
            "ftplib",
            "poplib",
            "imaplib",
            "nntplib",
            "smtplib",
            "smtpd",
            "telnetlib",
            "uuid",
            "urllib",
            "urllib2",
            "urlparse",
            "cookielib",
            "Cookie",
            "BaseHTTPServer",
            "SimpleHTTPServer",
            "CGIHTTPServer",
            "wsgiref",
            "webbrowser",
            "cgi",
            "cgitb",
            "wsgiref",
            "xdrlib",
            "plistlib",
        }

        return import_name in stdlib_modules


    def _find_function_line(self, content: str, func_name: str) -> Optional[int]:
        """Find the line number where a function is defined."""
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if f"def {func_name}(" in line:
                return i
        return None


    def _get_parents(self, tree: ast.AST, node: ast.AST) -> List[ast.AST]:
        """Get all parent nodes of a given node in the AST."""
        parents = []


        def find_parents(current, target):
            for child in ast.iter_child_nodes(current):
                if child == target:
                    parents.append(current)
                    return True
                if find_parents(child, target):
                    parents.append(current)
                    return True
            return False

        find_parents(tree, node)
        return parents


    def generate_report(
        self, result: CodeQualityAnalysisResult, output_path: Optional[str] = None
    ) -> str:
        """Generate a detailed quality report."""
        report_lines = []

        report_lines.append("=" * 80)
        report_lines.append("🔍 CODE QUALITY ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")

        report_lines.append(f"📊 OVERVIEW:")
        report_lines.append(f"   Files Analyzed: {result.files_analyzed}")
        report_lines.append(f"   Total Issues: {result.total_issues}")
        report_lines.append(
            f"   Overall Quality Score: {result.overall_quality_score:.1f}"
        )
        report_lines.append("")

        if result.issues_by_type:
            report_lines.append("📈 ISSUES BY TYPE:")
            for issue_type, count in sorted(result.issues_by_type.items()):
                report_lines.append(f"   {issue_type}: {count}")
            report_lines.append("")

        if result.issues_by_severity:
            report_lines.append("🚨 ISSUES BY SEVERITY:")
            for severity, count in sorted(result.issues_by_severity.items()):
                report_lines.append(f"   {severity}: {count}")
            report_lines.append("")

        report_lines.append("🎯 TOP ISSUES:")
        # Sort issues by severity and type
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_issues = sorted(
            result.issues,
            key=lambda x: (severity_order.get(x.severity, 4), x.issue_type),
        )[:20]

        for i, issue in enumerate(sorted_issues, 1):
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
            }.get(issue.severity, "⚪")
            report_lines.append(
                f"   {i}. {severity_emoji} {issue.file_path}:{issue.line_number}"
            )
            report_lines.append(f"      {issue.message}")
            if issue.suggestion:
                report_lines.append(f"      💡 {issue.suggestion}")
            report_lines.append("")

        if result.file_metrics:
            report_lines.append("📁 FILE QUALITY SCORES:")
            # Sort by quality score (worst first)
            sorted_files = sorted(
                result.file_metrics.items(), key=lambda x: x[1].quality_score
            )[:10]

            for file_path, metrics in sorted_files:
                score_emoji = (
                    "🟢"
                    if metrics.quality_score >= 80
                    else "🟡" if metrics.quality_score >= 60 else "🔴"
                )
                report_lines.append(f"      Score: {metrics.quality_score:.1f}")
                report_lines.append(
                    f"      Issues: {metrics.unused_imports + metrics.dead_code_count}"
                )
                report_lines.append("")

        report_lines.append("=" * 80)

        report = "\n".join(report_lines)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"📄 Report saved to: {output_path}")

        return report


def main():
    """CLI entry point for code quality analysis."""
    import argparse

    parser = argparse.ArgumentParser(description="Code Quality Analysis Engine")
    parser.add_argument("--path", default=".", help="Path to analyze")
    parser.add_argument("--output", help="Output report file")
    parser.add_argument("--exclude", nargs="*", help="Additional exclude patterns")

    args = parser.parse_args()

    root_path = Path(args.path)
    analyzer = CodeQualityAnalyzer(root_path, args.exclude)

    try:
        result = analyzer.analyze_codebase()
        report = analyzer.generate_report(result, args.output)

        print(report)

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
