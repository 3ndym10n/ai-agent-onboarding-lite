#!/usr/bin/env python3
"""
AI Onboard System Health and Integrity Check

This script performs comprehensive health checks on the AI Onboard system
to identify errors, redundancy, and other issues that could impact
system reliability and maintainability.
"""

import ast
import importlib
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


class SystemHealthChecker:
    """Comprehensive system health and integrity checker."""

    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.ai_onboard_path = self.root_path / "ai_onboard"
        self.issues: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []

        # Analysis results
        self.import_graph: Dict[str, Set[str]] = defaultdict(set)
        self.function_usage: Counter = Counter()
        self.file_sizes: Dict[str, int] = {}
        self.duplicate_code: List[Tuple[str, str, float]] = []
        self.missing_imports: Set[str] = set()

    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive report."""
        print("AI ONBOARD SYSTEM HEALTH CHECK")
        print("=" * 60)

        # Core checks
        self.check_file_structure()
        self.check_imports_and_dependencies()
        self.check_code_redundancy()
        self.check_naming_consistency()
        self.check_function_usage()
        self.check_error_patterns()
        self.check_configuration_integrity()

        # Generate report
        report = self.generate_health_report()

        # Display summary
        self.display_summary(report)

        return report

    def check_file_structure(self):
        """Check file and directory structure for issues."""
        print("\n[FILE] CHECKING FILE STRUCTURE...")

        # Check for __init__.py files
        missing_init = []
        for dir_path in self.ai_onboard_path.rglob("*"):
            if dir_path.is_dir() and not (dir_path / "__init__.py").exists():
                # Skip common directories that don't need __init__.py
                if not any(
                    skip in str(dir_path)
                    for skip in ["__pycache__", ".git", "node_modules"]
                ):
                    missing_init.append(str(dir_path.relative_to(self.ai_onboard_path)))

        if missing_init:
            self.issues.append(
                {
                    "type": "missing_init_files",
                    "severity": "warning",
                    "description": f"Missing __init__.py files in {len(missing_init)} directories",
                    "details": missing_init[:5],  # Show first 5
                    "impact": "May cause import issues in some contexts",
                }
            )

        # Check for very large files
        large_files = []
        for file_path in self.ai_onboard_path.rglob("*.py"):
            size = file_path.stat().st_size
            if size > 10000:  # 10KB threshold
                large_files.append(
                    (str(file_path.relative_to(self.ai_onboard_path)), size)
                )

        if large_files:
            self.warnings.append(
                {
                    "type": "large_files",
                    "severity": "info",
                    "description": f"Found {len(large_files)} large files (>10KB)",
                    "details": [
                        (f, s // 1024) for f, s in large_files[:3]
                    ],  # Show largest 3
                    "impact": "Consider breaking large files into smaller modules",
                }
            )

        print(
            f"  [OK] File structure checked ({len(missing_init)} issues, {len(large_files)} large files)"
        )

    def check_imports_and_dependencies(self):
        """Check for import errors and dependency issues."""
        print("\n[LINK] CHECKING IMPORTS AND DEPENDENCIES...")

        # Build import graph
        self._build_import_graph()

        # Check for circular imports
        cycles = self._detect_circular_imports()
        if cycles:
            self.issues.append(
                {
                    "type": "circular_imports",
                    "severity": "high",
                    "description": f"Found {len(cycles)} circular import cycles",
                    "details": cycles[:3],  # Show first 3 cycles
                    "impact": "Can cause runtime errors and import failures",
                }
            )

        # Check for missing imports
        missing = self._find_missing_imports()
        if missing:
            self.issues.append(
                {
                    "type": "missing_imports",
                    "severity": "high",
                    "description": f"Found {len(missing)} missing imports",
                    "details": list(missing)[:5],
                    "impact": "Will cause ImportError at runtime",
                }
            )

        print(
            f"  [OK] Imports checked ({len(cycles)} circular, {len(missing)} missing)"
        )

    def check_code_redundancy(self):
        """Check for code duplication and redundancy."""
        print("\n[SYNC] CHECKING CODE REDUNDANCY...")

        # Find similar functions
        similar_functions = self._find_similar_functions()
        if similar_functions:
            self.warnings.append(
                {
                    "type": "similar_functions",
                    "severity": "medium",
                    "description": f"Found {len(similar_functions)} potentially similar functions",
                    "details": similar_functions[:3],
                    "impact": "May indicate code duplication that could be refactored",
                }
            )

        # Check for duplicate class definitions
        duplicate_classes = self._find_duplicate_classes()
        if duplicate_classes:
            self.issues.append(
                {
                    "type": "duplicate_classes",
                    "severity": "medium",
                    "description": f"Found {len(duplicate_classes)} duplicate class definitions",
                    "details": duplicate_classes,
                    "impact": "Can cause conflicts and confusion",
                }
            )

        print(
            f"  [OK] Redundancy checked ({len(similar_functions)} similar functions, {len(duplicate_classes)} duplicates)"
        )

    def check_naming_consistency(self):
        """Check for consistent naming patterns."""
        print("\n[DOC] CHECKING NAMING CONSISTENCY...")

        # Check function naming patterns
        inconsistent_functions = self._check_function_naming()
        if inconsistent_functions:
            self.warnings.append(
                {
                    "type": "inconsistent_function_names",
                    "severity": "low",
                    "description": f"Found {len(inconsistent_functions)} inconsistent function names",
                    "details": inconsistent_functions[:5],
                    "impact": "Reduces code readability and consistency",
                }
            )

        # Check class naming patterns
        inconsistent_classes = self._check_class_naming()
        if inconsistent_classes:
            self.warnings.append(
                {
                    "type": "inconsistent_class_names",
                    "severity": "low",
                    "description": f"Found {len(inconsistent_classes)} inconsistent class names",
                    "details": inconsistent_classes[:5],
                    "impact": "Reduces code readability and consistency",
                }
            )

        print(
            f"  [OK] Naming checked ({len(inconsistent_functions)} function issues, {len(inconsistent_classes)} class issues)"
        )

    def check_function_usage(self):
        """Check for unused functions and dead code."""
        print("\n[SEARCH] CHECKING FUNCTION USAGE...")

        # Find unused functions
        unused_functions = self._find_unused_functions()
        if unused_functions:
            self.warnings.append(
                {
                    "type": "unused_functions",
                    "severity": "low",
                    "description": f"Found {len(unused_functions)} potentially unused functions",
                    "details": unused_functions[:10],  # Show first 10
                    "impact": "May indicate dead code that can be removed",
                }
            )

        print(
            f"  [OK] Usage checked ({len(unused_functions)} potentially unused functions)"
        )

    def check_error_patterns(self):
        """Check for common error patterns and anti-patterns."""
        print("\n[ALERT] CHECKING ERROR PATTERNS...")

        # Check for broad exception handling
        broad_exceptions = self._find_broad_exceptions()
        if broad_exceptions:
            self.warnings.append(
                {
                    "type": "broad_exception_handling",
                    "severity": "medium",
                    "description": f"Found {len(broad_exceptions)} instances of broad exception handling",
                    "details": broad_exceptions[:5],
                    "impact": "Can mask important errors and make debugging difficult",
                }
            )

        # Check for missing docstrings
        missing_docs = self._find_missing_docstrings()
        if missing_docs:
            self.warnings.append(
                {
                    "type": "missing_docstrings",
                    "severity": "low",
                    "description": f"Found {len(missing_docs)} functions/classes without docstrings",
                    "details": missing_docs[:10],
                    "impact": "Reduces code maintainability and documentation",
                }
            )

        print(
            f"  [OK] Error patterns checked ({len(broad_exceptions)} broad exceptions, {len(missing_docs)} missing docs)"
        )

    def check_configuration_integrity(self):
        """Check configuration files and settings."""
        print("\n[GEAR] CHECKING CONFIGURATION INTEGRITY...")

        # Check pyproject.toml for issues
        config_issues = self._check_pyproject_config()
        if config_issues:
            self.warnings.append(
                {
                    "type": "config_issues",
                    "severity": "medium",
                    "description": f"Found {len(config_issues)} configuration issues",
                    "details": config_issues,
                    "impact": "May cause build or runtime issues",
                }
            )

        print(f"  [OK] Configuration checked ({len(config_issues)} issues)")

    def _build_import_graph(self):
        """Build a graph of all imports in the codebase."""
        for py_file in self.ai_onboard_path.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse imports
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module = alias.name.split(".")[0]
                            self.import_graph[
                                str(py_file.relative_to(self.ai_onboard_path))
                            ].add(module)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module = node.module.split(".")[0]
                            self.import_graph[
                                str(py_file.relative_to(self.ai_onboard_path))
                            ].add(module)

            except Exception as e:
                self.warnings.append(
                    {
                        "type": "parse_error",
                        "severity": "low",
                        "description": f"Could not parse {py_file}",
                        "details": str(e),
                        "impact": "May indicate syntax errors",
                    }
                )

    def _detect_circular_imports(self) -> List[List[str]]:
        """Detect circular import dependencies."""
        cycles = []

        # Simple cycle detection using DFS
        visited = set()
        path = []

        def dfs(node):
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return

            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for neighbor in self.import_graph.get(node, set()):
                if neighbor in self.import_graph:
                    dfs(neighbor)

            path.pop()

        for node in self.import_graph:
            if node not in visited:
                dfs(node)

        return cycles

    def _find_missing_imports(self) -> Set[str]:
        """Find imports that cannot be resolved."""
        missing = set()

        # Common modules that should exist
        required_modules = {
            "ai_onboard.core.base",
            "ai_onboard.core.ai_integration",
            "ai_onboard.core.legacy_cleanup",
            "ai_onboard.core.orchestration",
            "ai_onboard.core.project_management",
            "ai_onboard.core.quality_safety",
            "ai_onboard.core.utilities",
            "ai_onboard.core.vision",
        }

        for file_imports in self.import_graph.values():
            for module in file_imports:
                if module.startswith("ai_onboard") and module not in required_modules:
                    # Check if this is a valid module path
                    module_path = self.ai_onboard_path / module.replace(".", "/")
                    if module_path.exists():
                        required_modules.add(module)

        # Check for missing __init__.py files in required modules
        for module in required_modules:
            module_path = self.ai_onboard_path / module.replace(".", "/")
            init_file = module_path / "__init__.py"
            if module_path.exists() and not init_file.exists():
                missing.add(f"Missing __init__.py for {module}")

        return missing

    def _find_similar_functions(self) -> List[Tuple[str, str, float]]:
        """Find functions with similar names or implementations."""
        similar = []

        # Simple heuristic: functions with similar names
        function_names = []
        for py_file in self.ai_onboard_path.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract function definitions
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        function_names.append(
                            (node.name, str(py_file.relative_to(self.ai_onboard_path)))
                        )

            except:
                pass

        # Find similar names
        names = [name for name, _ in function_names]
        for i, (name1, file1) in enumerate(function_names):
            for j, (name2, file2) in enumerate(function_names[i + 1 :], i + 1):
                if file1 != file2 and self._names_similar(name1, name2):
                    similar.append((name1, name2, 0.8))  # High similarity threshold

        return similar

    def _find_duplicate_classes(self) -> List[str]:
        """Find duplicate class definitions."""
        class_names = []
        duplicates = []

        for py_file in self.ai_onboard_path.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_names.append(
                            (node.name, str(py_file.relative_to(self.ai_onboard_path)))
                        )

            except:
                pass

        # Find duplicates
        seen = set()
        for name, file_path in class_names:
            if name in seen:
                duplicates.append(f"{name} in {file_path}")
            seen.add(name)

        return duplicates

    def _check_function_naming(self) -> List[str]:
        """Check for consistent function naming patterns."""
        issues = []

        # Check for snake_case vs camelCase inconsistency
        snake_case_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        camel_case_pattern = re.compile(r"^[a-z][a-zA-Z0-9]*$")

        for py_file in self.ai_onboard_path.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        name = node.name

                        # Check if it follows snake_case (preferred for functions)
                        if not snake_case_pattern.match(name) and not name.startswith(
                            "_"
                        ):
                            if camel_case_pattern.match(name):
                                issues.append(
                                    f"{name} in {py_file.relative_to(self.ai_onboard_path)} (should be snake_case)"
                                )

            except:
                pass

        return issues

    def _check_class_naming(self) -> List[str]:
        """Check for consistent class naming patterns."""
        issues = []

        # Check for PascalCase (preferred for classes)
        pascal_pattern = re.compile(r"^[A-Z][a-zA-Z0-9]*$")

        for py_file in self.ai_onboard_path.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        name = node.name

                        if not pascal_pattern.match(name) and not name.startswith("_"):
                            issues.append(
                                f"{name} in {py_file.relative_to(self.ai_onboard_path)} (should be PascalCase)"
                            )

            except:
                pass

        return issues

    def _find_unused_functions(self) -> List[str]:
        """Find potentially unused functions."""
        unused = []

        # This is a simplified check - in practice would need more sophisticated analysis
        for py_file in self.ai_onboard_path.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        name = node.name

                        # Simple heuristic: functions with "test_" prefix might be unused
                        if name.startswith("test_") and "def test_" in content:
                            unused.append(
                                f"{name} in {py_file.relative_to(self.ai_onboard_path)}"
                            )

            except:
                pass

        return unused

    def _find_broad_exceptions(self) -> List[str]:
        """Find broad exception handling patterns."""
        broad = []

        for py_file in self.ai_onboard_path.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Look for bare except clauses
                if "except:" in content or "except Exception:" in content:
                    broad.append(str(py_file.relative_to(self.ai_onboard_path)))

            except:
                pass

        return broad

    def _find_missing_docstrings(self) -> List[str]:
        """Find functions and classes without docstrings."""
        missing = []

        for py_file in self.ai_onboard_path.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if not ast.get_docstring(node):
                            missing.append(
                                f"{node.name} in {py_file.relative_to(self.ai_onboard_path)}"
                            )

            except:
                pass

        return missing[:20]  # Limit to first 20

    def _check_pyproject_config(self) -> List[str]:
        """Check pyproject.toml for configuration issues."""
        issues = []

        pyproject_path = self.root_path / "pyproject.toml"
        if not pyproject_path.exists():
            return ["pyproject.toml not found"]

        try:
            with open(pyproject_path, "r") as f:
                content = f.read()

            # Check for common issues
            if 'python = ">=3.8"' not in content:
                issues.append("Python version requirement not specified")

            if "dependencies" not in content:
                issues.append("No dependencies section found")

        except Exception as e:
            issues.append(f"Could not parse pyproject.toml: {e}")

        return issues

    def _names_similar(self, name1: str, name2: str) -> bool:
        """Check if two names are similar."""
        # Simple similarity check
        return name1.lower() == name2.lower() or abs(len(name1) - len(name2)) <= 2

    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        return {
            "timestamp": self._get_timestamp(),
            "summary": {
                "total_issues": len(self.issues),
                "total_warnings": len(self.warnings),
                "high_severity_issues": len(
                    [i for i in self.issues if i["severity"] == "high"]
                ),
                "medium_severity_issues": len(
                    [i for i in self.issues if i["severity"] == "medium"]
                ),
            },
            "issues": self.issues,
            "warnings": self.warnings,
            "recommendations": self._generate_recommendations(),
        }

    def display_summary(self, report: Dict[str, Any]):
        """Display a summary of the health check results."""
        summary = report["summary"]

        print("\n" + "=" * 60)
        print("HEALTH CHECK SUMMARY")
        print("=" * 60)

        print(f"High Severity Issues: {summary['high_severity_issues']}")
        print(f"Medium Severity Issues: {summary['medium_severity_issues']}")
        print(
            f"Low Severity Issues: {summary['total_issues'] - summary['high_severity_issues'] - summary['medium_severity_issues']}"
        )
        print(f"Total Warnings: {summary['total_warnings']}")

        if summary["high_severity_issues"] == 0:
            print("\n[OK] SYSTEM HEALTH: GOOD")
            print("No critical issues found. System appears healthy.")
        elif summary["high_severity_issues"] <= 2:
            print("\n[WARNING] SYSTEM HEALTH: NEEDS ATTENTION")
            print("Some issues found that should be addressed.")
        else:
            print("\n[ERROR] SYSTEM HEALTH: REQUIRES IMMEDIATE ATTENTION")
            print("Multiple critical issues found that need immediate resolution.")

        print("\n[LIST] DETAILED REPORT:")
        for issue in self.issues[:5]:  # Show first 5 issues
            severity_icon = {
                "high": "[RED]",
                "medium": "[YELLOW]",
                "low": "[BLUE]",
            }.get(issue["severity"], "[WHITE]")
            print(f"  {severity_icon} {issue['type'].upper()}: {issue['description']}")

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations = []

        if any(i["type"] == "circular_imports" for i in self.issues):
            recommendations.append(
                "Fix circular import dependencies by restructuring modules"
            )

        if any(i["type"] == "missing_imports" for i in self.issues):
            recommendations.append("Add missing __init__.py files or fix import paths")

        if any(i["type"] == "broad_exception_handling" for i in self.warnings):
            recommendations.append(
                "Replace broad exception handling with specific exception types"
            )

        if any(i["type"] == "large_files" for i in self.warnings):
            recommendations.append(
                "Consider breaking large files into smaller, focused modules"
            )

        if any(i["type"] == "unused_functions" for i in self.warnings):
            recommendations.append(
                "Review and remove unused functions to reduce code complexity"
            )

        if not recommendations:
            recommendations.append(
                "System appears healthy - continue with regular maintenance"
            )

        return recommendations

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime

        return datetime.now().isoformat()


def main():
    """Run the system health check."""
    import sys

    # Get project root (assuming script is in project root)
    project_root = Path(__file__).parent

    checker = SystemHealthChecker(project_root)
    report = checker.run_comprehensive_check()

    # Save report to file
    report_path = (
        project_root
        / ".ai_onboard"
        / "health_reports"
        / f"health_check_{int(time.time())}.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n[FILE] Detailed report saved to: {report_path}")

    # Exit with appropriate code based on health
    summary = report["summary"]
    if summary["high_severity_issues"] > 0:
        sys.exit(1)  # Unhealthy
    elif summary["medium_severity_issues"] > 3:
        sys.exit(1)  # Needs attention
    else:
        sys.exit(0)  # Healthy


if __name__ == "__main__":
    main()
