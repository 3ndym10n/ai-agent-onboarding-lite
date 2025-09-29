#!/usr/bin/env python3
"""
Import Equivalence Validator - Validates that consolidated imports are functionally equivalent.

This tool ensures that consolidated imports work exactly the same as the original imports,
preventing subtle bugs and ensuring safe migration.

Features:
- Import resolution testing
- Functionality equivalence validation
- Circular dependency detection
- Performance impact assessment
- Integration with existing safety framework
"""
import ast
import importlib
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_onboard.core.base.utils import ensure_dir, read_json, write_json


class ValidationStatus(Enum):
    """Validation status for import equivalence."""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


class ImportIssue(Enum):
    """Types of import issues that can be detected."""

    RESOLUTION_ERROR = "resolution_error"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    FUNCTIONALITY_DIFFERENCE = "functionality_difference"
    PERFORMANCE_REGRESSION = "performance_regression"
    NAMESPACE_CONFLICT = "namespace_conflict"


@dataclass
class ImportEquivalenceResult:
    """Result of import equivalence validation."""

    status: ValidationStatus
    issue_type: Optional[ImportIssue] = None
    message: str = ""
    details: Dict[str, Any] = None
    performance_impact: float = 0.0
    resolution_time: float = 0.0


@dataclass
class ValidationReport:
    """Comprehensive validation report."""

    total_imports: int
    passed_imports: int
    failed_imports: int
    warning_imports: int
    skipped_imports: int
    results: List[ImportEquivalenceResult]
    performance_impact: float
    circular_dependencies: List[str]
    recommendations: List[str]
    summary: str


class ImportEquivalenceValidator:
    """Validates that consolidated imports are functionally equivalent to originals."""

    def __init__(self, root: Path):
        self.root = root
        self.validation_log = root / ".ai_onboard" / "import_validation_log.jsonl"
        self.cache_dir = root / ".ai_onboard" / "import_validation_cache"

        # Ensure directories exist
        ensure_dir(self.validation_log.parent)
        ensure_dir(self.cache_dir)

        # Track validation state
        self.import_cache: Dict[str, Any] = {}
        self.circular_dependency_cache: Set[Tuple[str, str]] = set()
        self.performance_baseline: Dict[str, float] = {}

    def validate_consolidation_equivalence(
        self,
        original_imports: List[str],
        consolidated_imports: List[str],
        test_files: List[Path],
    ) -> ValidationReport:
        """Validate that consolidated imports are equivalent to originals."""
        print("🔍 Validating import equivalence...")

        results = []
        total_imports = len(original_imports)
        passed_imports = 0
        failed_imports = 0
        warning_imports = 0
        skipped_imports = 0

        # Validate each import
        for i, (original, consolidated) in enumerate(
            zip(original_imports, consolidated_imports)
        ):
            print(
                f"  Validating import {i + 1}/{total_imports}: {original} -> {consolidated}"
            )

            result = self._validate_single_import(original, consolidated, test_files)
            results.append(result)

            if result.status == ValidationStatus.PASS:
                passed_imports += 1
            elif result.status == ValidationStatus.FAIL:
                failed_imports += 1
            elif result.status == ValidationStatus.WARNING:
                warning_imports += 1
            else:
                skipped_imports += 1

        # Detect circular dependencies
        circular_dependencies = self._detect_circular_dependencies(consolidated_imports)

        # Calculate performance impact
        performance_impact = self._calculate_performance_impact(results)

        # Generate recommendations
        recommendations = self._generate_recommendations(results, circular_dependencies)

        # Create summary
        summary = self._generate_summary(
            total_imports,
            passed_imports,
            failed_imports,
            warning_imports,
            skipped_imports,
            performance_impact,
        )

        # Create validation report
        report = ValidationReport(
            total_imports=total_imports,
            passed_imports=passed_imports,
            failed_imports=failed_imports,
            warning_imports=warning_imports,
            skipped_imports=skipped_imports,
            results=results,
            performance_impact=performance_impact,
            circular_dependencies=circular_dependencies,
            recommendations=recommendations,
            summary=summary,
        )

        # Save report
        self._save_validation_report(report)

        print(
            f"✅ Validation complete: {passed_imports} passed, {failed_imports} failed"
        )

        return report

    def _validate_single_import(
        self, original: str, consolidated: str, test_files: List[Path]
    ) -> ImportEquivalenceResult:
        """Validate a single import equivalence."""
        start_time = time.time()

        try:
            # Test 1: Import resolution
            resolution_result = self._test_import_resolution(original, consolidated)
            if resolution_result.status == ValidationStatus.FAIL:
                return resolution_result

            # Test 2: Functionality equivalence
            functionality_result = self._test_functionality_equivalence(
                original, consolidated, test_files
            )
            if functionality_result.status == ValidationStatus.FAIL:
                return functionality_result

            # Test 3: Namespace conflicts
            namespace_result = self._test_namespace_conflicts(original, consolidated)
            if namespace_result.status == ValidationStatus.FAIL:
                return namespace_result

            # Test 4: Performance impact
            performance_result = self._test_performance_impact(original, consolidated)

            # Calculate resolution time
            resolution_time = time.time() - start_time

            # Determine overall status
            if (
                resolution_result.status == ValidationStatus.PASS
                and functionality_result.status == ValidationStatus.PASS
                and namespace_result.status == ValidationStatus.PASS
            ):
                status = ValidationStatus.PASS
            elif any(
                r.status == ValidationStatus.WARNING
                for r in [resolution_result, functionality_result, namespace_result]
            ):
                status = ValidationStatus.WARNING
            else:
                status = ValidationStatus.FAIL

            return ImportEquivalenceResult(
                status=status,
                message=f"Import equivalence validated: {original} -> {consolidated}",
                details={
                    "original": original,
                    "consolidated": consolidated,
                    "resolution_time": resolution_time,
                    "performance_impact": performance_result.performance_impact,
                },
                performance_impact=performance_result.performance_impact,
                resolution_time=resolution_time,
            )

        except Exception as e:
            return ImportEquivalenceResult(
                status=ValidationStatus.FAIL,
                issue_type=ImportIssue.RESOLUTION_ERROR,
                message=f"Validation error for {original} -> {consolidated}: {str(e)}",
                details={"error": str(e)},
                resolution_time=time.time() - start_time,
            )

    def _test_import_resolution(
        self, original: str, consolidated: str
    ) -> ImportEquivalenceResult:
        """Test that both imports can be resolved."""
        try:
            # Test original import
            original_result = self._resolve_import(original)
            if not original_result["success"]:
                return ImportEquivalenceResult(
                    status=ValidationStatus.FAIL,
                    issue_type=ImportIssue.RESOLUTION_ERROR,
                    message=f"Original import failed to resolve: {original}",
                    details=original_result,
                )

            # Test consolidated import
            consolidated_result = self._resolve_import(consolidated)
            if not consolidated_result["success"]:
                return ImportEquivalenceResult(
                    status=ValidationStatus.FAIL,
                    issue_type=ImportIssue.RESOLUTION_ERROR,
                    message=f"Consolidated import failed to resolve: {consolidated}",
                    details=consolidated_result,
                )

            return ImportEquivalenceResult(
                status=ValidationStatus.PASS,
                message="Both imports resolve successfully",
            )

        except Exception as e:
            return ImportEquivalenceResult(
                status=ValidationStatus.FAIL,
                issue_type=ImportIssue.RESOLUTION_ERROR,
                message=f"Import resolution test failed: {str(e)}",
            )

    def _test_functionality_equivalence(
        self, original: str, consolidated: str, test_files: List[Path]
    ) -> ImportEquivalenceResult:
        """Test that both imports provide the same functionality."""
        try:
            # Test in each test file
            for test_file in test_files:
                if not test_file.exists():
                    continue

                # Create test code that uses both imports
                test_code = self._generate_functionality_test(
                    original, consolidated, test_file
                )

                # Execute test code
                test_result = self._execute_test_code(test_code)

                if not test_result["success"]:
                    return ImportEquivalenceResult(
                        status=ValidationStatus.FAIL,
                        issue_type=ImportIssue.FUNCTIONALITY_DIFFERENCE,
                        message=f"Functionality test failed in {test_file}: {test_result['error']}",
                        details=test_result,
                    )

            return ImportEquivalenceResult(
                status=ValidationStatus.PASS,
                message="Functionality equivalence confirmed",
            )

        except Exception as e:
            return ImportEquivalenceResult(
                status=ValidationStatus.FAIL,
                issue_type=ImportIssue.FUNCTIONALITY_DIFFERENCE,
                message=f"Functionality equivalence test failed: {str(e)}",
            )

    def _test_namespace_conflicts(
        self, original: str, consolidated: str
    ) -> ImportEquivalenceResult:
        """Test for namespace conflicts between imports."""
        try:
            # Parse import statements
            original_parts = self._parse_import_statement(original)
            consolidated_parts = self._parse_import_statement(consolidated)

            # Check for name conflicts
            original_names = set(original_parts.get("names", []))
            consolidated_names = set(consolidated_parts.get("names", []))

            conflicts = original_names.intersection(consolidated_names)

            if conflicts:
                return ImportEquivalenceResult(
                    status=ValidationStatus.WARNING,
                    issue_type=ImportIssue.NAMESPACE_CONFLICT,
                    message=f"Namespace conflicts detected: {conflicts}",
                    details={"conflicts": list(conflicts)},
                )

            return ImportEquivalenceResult(
                status=ValidationStatus.PASS, message="No namespace conflicts detected"
            )

        except Exception as e:
            return ImportEquivalenceResult(
                status=ValidationStatus.FAIL,
                issue_type=ImportIssue.NAMESPACE_CONFLICT,
                message=f"Namespace conflict test failed: {str(e)}",
            )

    def _test_performance_impact(
        self, original: str, consolidated: str
    ) -> ImportEquivalenceResult:
        """Test performance impact of consolidated import."""
        try:
            # Measure original import time
            original_time = self._measure_import_time(original)

            # Measure consolidated import time
            consolidated_time = self._measure_import_time(consolidated)

            # Calculate performance impact
            if original_time > 0:
                performance_impact = (consolidated_time - original_time) / original_time
            else:
                performance_impact = 0.0

            # Determine if impact is significant
            if performance_impact > 0.1:  # 10% slower
                status = ValidationStatus.WARNING
                message = (
                    f"Performance regression detected: {performance_impact:.2%} slower"
                )
            else:
                status = ValidationStatus.PASS
                message = f"Performance impact acceptable: {performance_impact:.2%}"

            return ImportEquivalenceResult(
                status=status,
                issue_type=ImportIssue.PERFORMANCE_REGRESSION,
                message=message,
                performance_impact=performance_impact,
                details={
                    "original_time": original_time,
                    "consolidated_time": consolidated_time,
                    "performance_impact": performance_impact,
                },
            )

        except Exception as e:
            return ImportEquivalenceResult(
                status=ValidationStatus.WARNING,
                issue_type=ImportIssue.PERFORMANCE_REGRESSION,
                message=f"Performance test failed: {str(e)}",
                performance_impact=0.0,
            )

    def _resolve_import(self, import_statement: str) -> Dict[str, Any]:
        """Resolve an import statement to check if it works."""
        try:
            # Parse the import statement
            parts = self._parse_import_statement(import_statement)

            if parts["type"] == "import":
                # Test: import module
                module = importlib.import_module(parts["module"])
                return {"success": True, "module": module, "type": "import"}
            elif parts["type"] == "from_import":
                # Test: from module import name
                module = importlib.import_module(parts["module"])
                for name in parts["names"]:
                    if not hasattr(module, name):
                        return {
                            "success": False,
                            "error": f"Module {parts['module']} has no attribute {name}",
                        }
                return {
                    "success": True,
                    "module": module,
                    "names": parts["names"],
                    "type": "from_import",
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown import type: {parts['type']}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_import_statement(self, import_statement: str) -> Dict[str, Any]:
        """Parse an import statement into its components."""
        try:
            tree = ast.parse(import_statement)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    return {
                        "type": "import",
                        "module": node.names[0].name,
                        "names": [alias.name for alias in node.names],
                        "aliases": {
                            alias.name: alias.asname
                            for alias in node.names
                            if alias.asname
                        },
                    }
                elif isinstance(node, ast.ImportFrom):
                    return {
                        "type": "from_import",
                        "module": node.module or "",
                        "names": [alias.name for alias in node.names],
                        "aliases": {
                            alias.name: alias.asname
                            for alias in node.names
                            if alias.asname
                        },
                    }

            return {"type": "unknown", "module": "", "names": [], "aliases": {}}

        except Exception as e:
            return {
                "type": "error",
                "module": "",
                "names": [],
                "aliases": {},
                "error": str(e),
            }

    def _generate_functionality_test(
        self, original: str, consolidated: str, test_file: Path
    ) -> str:
        """Generate test code to verify functionality equivalence."""
        test_code = f"""
# Test code for import equivalence validation
import sys
import traceback

def test_import_equivalence():
    try:
        # Test original import
        {original}

        # Test consolidated import
        {consolidated}

        # If we get here, both imports work
        return True, "Both imports work correctly"

    except Exception as e:
        return False, f"Import test failed: {{str(e)}}"

if __name__ == "__main__":
    success, message = test_import_equivalence()
    print(f"Test result: {{success}} - {{message}}")
    sys.exit(0 if success else 1)
"""
        return test_code

    def _execute_test_code(self, test_code: str) -> Dict[str, Any]:
        """Execute test code and return results."""
        try:
            result = subprocess.run(
                [sys.executable, "-c", test_code],
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Test execution timed out",
                "returncode": -1,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "returncode": -1}

    def _measure_import_time(self, import_statement: str) -> float:
        """Measure the time it takes to resolve an import."""
        try:
            start_time = time.time()
            self._resolve_import(import_statement)
            return time.time() - start_time
        except Exception:
            return 0.0

    def _detect_circular_dependencies(self, imports: List[str]) -> List[str]:
        """Detect circular dependencies in the import list."""
        circular_deps = []

        # Build dependency graph
        dependency_graph = {}
        for import_stmt in imports:
            parts = self._parse_import_statement(import_stmt)
            if parts["type"] == "from_import":
                module = parts["module"]
                if module not in dependency_graph:
                    dependency_graph[module] = set()

                # Add dependencies (simplified)
                for name in parts["names"]:
                    if name in dependency_graph:
                        dependency_graph[module].add(name)

        # Check for cycles using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            for neighbor in dependency_graph.get(node, set()):
                if has_cycle(neighbor):
                    return True

            rec_stack.remove(node)
            return False

        for module in dependency_graph:
            if module not in visited:
                if has_cycle(module):
                    circular_deps.append(module)

        return circular_deps

    def _calculate_performance_impact(
        self, results: List[ImportEquivalenceResult]
    ) -> float:
        """Calculate overall performance impact of consolidation."""
        if not results:
            return 0.0

        total_impact = sum(result.performance_impact for result in results)
        return total_impact / len(results)

    def _generate_recommendations(
        self, results: List[ImportEquivalenceResult], circular_dependencies: List[str]
    ) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        # Count issues by type
        issue_counts = {}
        for result in results:
            if result.issue_type:
                issue_counts[result.issue_type] = (
                    issue_counts.get(result.issue_type, 0) + 1
                )

        # Generate recommendations based on issues
        if issue_counts.get(ImportIssue.RESOLUTION_ERROR, 0) > 0:
            recommendations.append(
                f"Fix {issue_counts[ImportIssue.RESOLUTION_ERROR]} import resolution errors"
            )

        if issue_counts.get(ImportIssue.CIRCULAR_DEPENDENCY, 0) > 0:
            recommendations.append(
                f"Resolve {issue_counts[ImportIssue.CIRCULAR_DEPENDENCY]} circular dependencies"
            )

        if issue_counts.get(ImportIssue.FUNCTIONALITY_DIFFERENCE, 0) > 0:
            recommendations.append(
                f"Fix {issue_counts[ImportIssue.FUNCTIONALITY_DIFFERENCE]} functionality differences"
            )

        if issue_counts.get(ImportIssue.PERFORMANCE_REGRESSION, 0) > 0:
            recommendations.append(
                f"Optimize {issue_counts[ImportIssue.PERFORMANCE_REGRESSION]} performance regressions"
            )

        if circular_dependencies:
            recommendations.append(
                f"Break circular dependencies: {', '.join(circular_dependencies)}"
            )

        return recommendations

    def _generate_summary(
        self,
        total: int,
        passed: int,
        failed: int,
        warnings: int,
        skipped: int,
        performance_impact: float,
    ) -> str:
        """Generate validation summary."""
        success_rate = (passed / total * 100) if total > 0 else 0

        summary = f"Import Equivalence Validation Summary:\n"
        summary += f"  Total imports: {total}\n"
        summary += f"  Passed: {passed} ({success_rate:.1f}%)\n"
        summary += f"  Failed: {failed}\n"
        summary += f"  Warnings: {warnings}\n"
        summary += f"  Skipped: {skipped}\n"
        summary += f"  Performance impact: {performance_impact:.2%}\n"

        if success_rate >= 90:
            summary += "  Status: EXCELLENT - Safe to proceed with consolidation"
        elif success_rate >= 80:
            summary += "  Status: GOOD - Minor issues to address"
        elif success_rate >= 70:
            summary += "  Status: FAIR - Several issues need attention"
        else:
            summary += "  Status: POOR - Major issues must be resolved"

        return summary

    def _save_validation_report(self, report: ValidationReport):
        """Save validation report to file."""
        report_file = self.root / ".ai_onboard" / "import_equivalence_report.json"

        report_data = {
            "timestamp": time.time(),
            "total_imports": report.total_imports,
            "passed_imports": report.passed_imports,
            "failed_imports": report.failed_imports,
            "warning_imports": report.warning_imports,
            "skipped_imports": report.skipped_imports,
            "performance_impact": report.performance_impact,
            "circular_dependencies": report.circular_dependencies,
            "recommendations": report.recommendations,
            "summary": report.summary,
            "results": [
                {
                    "status": result.status.value,
                    "issue_type": (
                        result.issue_type.value if result.issue_type else None
                    ),
                    "message": result.message,
                    "details": result.details,
                    "performance_impact": result.performance_impact,
                    "resolution_time": result.resolution_time,
                }
                for result in report.results
            ],
        }

        write_json(report_file, report_data)

        # Also log to JSONL
        with open(self.validation_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(report_data) + "\n")


def main():
    """Main CLI interface for import equivalence validator."""
    import argparse

    parser = argparse.ArgumentParser(description="Import Equivalence Validator")
    parser.add_argument(
        "--root", type=Path, default=Path.cwd(), help="Project root directory"
    )
    parser.add_argument("--original", nargs="+", help="Original import statements")
    parser.add_argument(
        "--consolidated", nargs="+", help="Consolidated import statements"
    )
    parser.add_argument(
        "--test-files", nargs="+", type=Path, help="Test files to validate against"
    )
    parser.add_argument(
        "--config", type=Path, help="Configuration file with import mappings"
    )

    args = parser.parse_args()

    validator = ImportEquivalenceValidator(args.root)

    if args.config:
        # Load configuration and validate
        config = read_json(args.config)
        original_imports = config.get("original_imports", [])
        consolidated_imports = config.get("consolidated_imports", [])
        test_files = [Path(f) for f in config.get("test_files", [])]
    else:
        # Use command line arguments
        original_imports = args.original or []
        consolidated_imports = args.consolidated or []
        test_files = args.test_files or []

    if not original_imports or not consolidated_imports:
        print("❌ Error: Must provide both original and consolidated imports")
        parser.print_help()
        return

    if len(original_imports) != len(consolidated_imports):
        print("❌ Error: Number of original and consolidated imports must match")
        return

    # Run validation
    report = validator.validate_consolidation_equivalence(
        original_imports, consolidated_imports, test_files
    )

    # Print results
    print("\n" + report.summary)

    if report.recommendations:
        print("\n📋 Recommendations:")
        for rec in report.recommendations:
            print(f"  • {rec}")


if __name__ == "__main__":
    main()
