"""
Dependency Checker for Safe Cleanup Operations.

This module provides comprehensive dependency checking to prevent accidental
deletion of files that are referenced by other parts of the system.
Learned from the README consolidation incident where 19 dependencies
were nearly broken.
"""

import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .unicode_utils import print_content, print_status, safe_print


class DependencyType(Enum):
    """Types of dependencies that can be detected."""

    PYTHON_IMPORT = "python_import"
    FILE_REFERENCE = "file_reference"
    CONFIG_REFERENCE = "config_reference"
    DOCUMENTATION_LINK = "documentation_link"
    CLI_REFERENCE = "cli_reference"
    TEST_REFERENCE = "test_reference"
    BUILD_REFERENCE = "build_reference"
    GIT_REFERENCE = "git_reference"


@dataclass
class Dependency:
    """Represents a dependency relationship."""

    source_file: Path
    target_file: Path
    dependency_type: DependencyType
    line_number: Optional[int] = None
    context: Optional[str] = None
    severity: str = "high"  # high, medium, low


@dataclass
class DependencyCheckResult:
    """Results of dependency checking."""

    target_file: Path
    dependencies: List[Dependency]
    is_safe_to_delete: bool
    risk_level: str
    warnings: List[str]
    recommendations: List[str]


class DependencyChecker:
    """Comprehensive dependency checker for safe cleanup operations."""

    def __init__(self, root: Path):
        """
        Initialize the dependency checker.

        Args:
            root: Root directory of the project
        """
        self.root = Path(root)
        self.dependency_cache = {}

        # File patterns to scan for dependencies
        self.scannable_patterns = [
            "**/*.py",  # Python files
            "**/*.json",  # JSON config files
            "**/*.yaml",  # YAML config files
            "**/*.yml",  # YAML config files
            "**/*.toml",  # TOML config files
            "**/*.md",  # Markdown files
            "**/*.rst",  # ReStructuredText files
            "**/*.txt",  # Text files
            "**/*.sh",  # Shell scripts
            "**/*.bat",  # Batch files
            "**/*.ps1",  # PowerShell scripts
        ]

        # Critical files that should never be deleted
        self.critical_files = {
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "requirements.txt",
            "README.md",
            "AGENTS.md",
            "LICENSE",
            "__init__.py",
            "__main__.py",
        }

    def check_dependencies(
        self, target_files: List[Path]
    ) -> List[DependencyCheckResult]:
        """
        Check dependencies for a list of target files.

        Args:
            target_files: Files to check for dependencies

        Returns:
            List of dependency check results
        """
        results = []

        print_content(
            f"Checking dependencies for {len(target_files)} files...", "search"
        )

        for target_file in target_files:
            result = self._check_single_file_dependencies(target_file)
            results.append(result)

            if not result.is_safe_to_delete:
                print_status(
                    f"⚠️ {target_file.name} has {len(result.dependencies)} dependencies",
                    "warning",
                )

        return results

    def _check_single_file_dependencies(
        self, target_file: Path
    ) -> DependencyCheckResult:
        """Check dependencies for a single file."""
        dependencies = []
        warnings = []
        recommendations = []

        # Check if it's a critical file
        if target_file.name in self.critical_files:
            warnings.append(f"File '{target_file.name}' is marked as critical")
            recommendations.append("Consider if this file is truly safe to delete")

        # Scan all files in the project for references
        for pattern in self.scannable_patterns:
            for source_file in self.root.glob(pattern):
                if source_file == target_file or not source_file.is_file():
                    continue

                file_dependencies = self._scan_file_for_references(
                    source_file, target_file
                )
                dependencies.extend(file_dependencies)

        # Determine risk level and safety
        risk_level, is_safe = self._assess_risk(dependencies, target_file)

        if not is_safe:
            recommendations.append(
                f"Update {len(dependencies)} dependencies before deletion"
            )
            recommendations.append("Consider refactoring to remove dependencies")

        return DependencyCheckResult(
            target_file = target_file,
            dependencies = dependencies,
            is_safe_to_delete = is_safe,
            risk_level = risk_level,
            warnings = warnings,
            recommendations = recommendations,
        )

    def _scan_file_for_references(
        self, source_file: Path, target_file: Path
    ) -> List[Dependency]:
        """Scan a source file for references to the target file."""
        dependencies = []

        try:
            content = source_file.read_text(encoding="utf - 8", errors="ignore")

            # Check different types of references based on file type
            if source_file.suffix == ".py":
                dependencies.extend(
                    self._scan_python_file(source_file, target_file, content)
                )
            elif source_file.suffix in [".json", ".yaml", ".yml", ".toml"]:
                dependencies.extend(
                    self._scan_config_file(source_file, target_file, content)
                )
            elif source_file.suffix in [".md", ".rst", ".txt"]:
                dependencies.extend(
                    self._scan_documentation_file(source_file, target_file, content)
                )
            else:
                dependencies.extend(
                    self._scan_generic_file(source_file, target_file, content)
                )

        except Exception:
            # Skip files that can't be read
            pass

        return dependencies

    def _scan_python_file(
        self, source_file: Path, target_file: Path, content: str
    ) -> List[Dependency]:
        """Scan Python file for imports and references."""
        dependencies = []

        # Check for direct file path references
        target_patterns = [
            str(target_file),
            (
                str(target_file.relative_to(self.root))
                if target_file.is_relative_to(self.root)
                else None
            ),
            target_file.name,
            target_file.stem,  # filename without extension
        ]

        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            for pattern in target_patterns:
                if pattern and pattern in line:
                    # Determine the type of reference
                    if "import" in line or "from" in line:
                        dep_type = DependencyType.PYTHON_IMPORT
                    elif any(
                        keyword in line.lower()
                        for keyword in ["read", "open", "path", "file"]
                    ):
                        dep_type = DependencyType.FILE_REFERENCE
                    else:
                        dep_type = DependencyType.FILE_REFERENCE

                    dependencies.append(
                        Dependency(
                            source_file = source_file,
                            target_file = target_file,
                            dependency_type = dep_type,
                            line_number = line_num,
                            context = line.strip(),
                            severity=(
                                "high"
                                if dep_type == DependencyType.PYTHON_IMPORT
                                else "medium"
                            ),
                        )
                    )

        # Additional Python - specific checks using AST
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if self._matches_target(alias.name, target_file):
                            dependencies.append(
                                Dependency(
                                    source_file = source_file,
                                    target_file = target_file,
                                    dependency_type = DependencyType.PYTHON_IMPORT,
                                    line_number = node.lineno,
                                    context = f"import {alias.name}",
                                    severity="high",
                                )
                            )
                elif isinstance(node, ast.ImportFrom):
                    if node.module and self._matches_target(node.module, target_file):
                        dependencies.append(
                            Dependency(
                                source_file = source_file,
                                target_file = target_file,
                                dependency_type = DependencyType.PYTHON_IMPORT,
                                line_number = node.lineno,
                                context = f"from {node.module} import ...",
                                severity="high",
                            )
                        )
        except:
            # If AST parsing fails, skip advanced analysis
            pass

        return dependencies

    def _scan_config_file(
        self, source_file: Path, target_file: Path, content: str
    ) -> List[Dependency]:
        """Scan configuration files for references."""
        dependencies = []

        target_patterns = [
            str(target_file),
            (
                str(target_file.relative_to(self.root))
                if target_file.is_relative_to(self.root)
                else None
            ),
            target_file.name,
        ]

        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            for pattern in target_patterns:
                if pattern and pattern in line:
                    dependencies.append(
                        Dependency(
                            source_file = source_file,
                            target_file = target_file,
                            dependency_type = DependencyType.CONFIG_REFERENCE,
                            line_number = line_num,
                            context = line.strip(),
                            severity="high",
                        )
                    )

        return dependencies

    def _scan_documentation_file(
        self, source_file: Path, target_file: Path, content: str
    ) -> List[Dependency]:
        """Scan documentation files for links and references."""
        dependencies = []

        # Look for markdown links, file references, etc.
        target_patterns = [
            (
                str(target_file.relative_to(self.root))
                if target_file.is_relative_to(self.root)
                else None
            ),
            target_file.name,
        ]

        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            for pattern in target_patterns:
                if pattern and pattern in line:
                    # Check if it's a markdown link
                    if "[" in line and "](" in line and pattern in line:
                        dep_type = DependencyType.DOCUMENTATION_LINK
                        severity = "medium"
                    else:
                        dep_type = DependencyType.FILE_REFERENCE
                        severity = "low"

                    dependencies.append(
                        Dependency(
                            source_file = source_file,
                            target_file = target_file,
                            dependency_type = dep_type,
                            line_number = line_num,
                            context = line.strip(),
                            severity = severity,
                        )
                    )

        return dependencies

    def _scan_generic_file(
        self, source_file: Path, target_file: Path, content: str
    ) -> List[Dependency]:
        """Scan generic files for any references."""
        dependencies = []

        target_name = target_file.name
        if target_name in content:
            # Count occurrences to avoid false positives
            occurrences = content.count(target_name)
            if occurrences <= 10:  # Reasonable threshold
                lines = content.split("\n")
                for line_num, line in enumerate(lines, 1):
                    if target_name in line:
                        dependencies.append(
                            Dependency(
                                source_file = source_file,
                                target_file = target_file,
                                dependency_type = DependencyType.FILE_REFERENCE,
                                line_number = line_num,
                                context = line.strip(),
                                severity="low",
                            )
                        )

        return dependencies

    def _matches_target(self, module_name: str, target_file: Path) -> bool:
        """Check if a module name matches the target file."""
        if not module_name:
            return False

        # Convert file path to module path
        if target_file.suffix == ".py":
            # Convert path to module notation
            relative_path = (
                target_file.relative_to(self.root)
                if target_file.is_relative_to(self.root)
                else target_file
            )
            module_path = (
                str(relative_path.with_suffix("")).replace("/", ".").replace("\\", ".")
            )

            return module_name == module_path or module_name.endswith(
                "." + target_file.stem
            )

        return False

    def _assess_risk(
        self, dependencies: List[Dependency], target_file: Path
    ) -> Tuple[str, bool]:
        """Assess the risk level and safety of deleting the target file."""
        if not dependencies:
            return "low", True

        # Count dependencies by severity
        high_severity = sum(1 for dep in dependencies if dep.severity == "high")
        medium_severity = sum(1 for dep in dependencies if dep.severity == "medium")

        if high_severity > 0:
            return "high", False
        elif medium_severity > 3:
            return "medium", False
        elif len(dependencies) > 10:
            return "medium", False
        else:
            return "low", True

    def generate_dependency_report(self, results: List[DependencyCheckResult]) -> str:
        """Generate a comprehensive dependency report."""
        report = []
        report.append("🔍 DEPENDENCY CHECK REPORT")
        report.append("=" * 50)

        total_files = len(results)
        safe_files = sum(1 for r in results if r.is_safe_to_delete)
        unsafe_files = total_files - safe_files

        report.append(f"\n📊 SUMMARY:")
        report.append(f"   Total files checked: {total_files}")
        report.append(f"   Safe to delete: {safe_files}")
        report.append(f"   Has dependencies: {unsafe_files}")

        if unsafe_files > 0:
            report.append(f"\n⚠️  FILES WITH DEPENDENCIES:")

            for result in results:
                if not result.is_safe_to_delete:
                    report.append(f"\n📄 {result.target_file.name}")
                    report.append(f"   Risk Level: {result.risk_level.upper()}")
                    report.append(f"   Dependencies: {len(result.dependencies)}")

                    if result.dependencies:
                        report.append(f"   Referenced by:")
                        for dep in result.dependencies[:5]:  # Show first 5
                            report.append(
                                f"     - {dep.source_file.name}:{dep.line_number} ({dep.dependency_type.value})"
                            )

                        if len(result.dependencies) > 5:
                            report.append(
                                f"     ... and {len(result.dependencies) - 5} more"
                            )

                    if result.recommendations:
                        report.append(f"   Recommendations:")
                        for rec in result.recommendations:
                            report.append(f"     • {rec}")

        report.append(f"\n✅ SAFE FILES:")
        for result in results:
            if result.is_safe_to_delete:
                report.append(f"   ✓ {result.target_file.name}")

        return "\n".join(report)

    def create_dependency_fix_plan(
        self, results: List[DependencyCheckResult]
    ) -> Dict[str, Any]:
        """Create a plan for fixing dependencies before deletion."""
        plan = {
            "files_to_update": {},
            "files_to_delete": [],
            "manual_review_needed": [],
            "estimated_changes": 0,
        }

        for result in results:
            if result.is_safe_to_delete:
                plan["files_to_delete"].append(str(result.target_file))
            else:
                # Group by source file for efficient updates
                for dep in result.dependencies:
                    source_file_str = str(dep.source_file)
                    if source_file_str not in plan["files_to_update"]:
                        plan["files_to_update"][source_file_str] = []

                    plan["files_to_update"][source_file_str].append(
                        {
                            "line": dep.line_number,
                            "context": dep.context,
                            "target": str(dep.target_file),
                            "type": dep.dependency_type.value,
                            "severity": dep.severity,
                        }
                    )
                    plan["estimated_changes"] += 1

                if result.risk_level == "high":
                    plan["manual_review_needed"].append(str(result.target_file))

        return plan


def check_cleanup_dependencies(root: Path, target_files: List[Path]) -> bool:
    """
    Check if files can be safely deleted by analyzing dependencies.

    Args:
        root: Project root directory
        target_files: Files to check for deletion

    Returns:
        bool: True if all files are safe to delete, False otherwise
    """
    checker = DependencyChecker(root)
    results = checker.check_dependencies(target_files)

    # Generate and display report
    report = checker.generate_dependency_report(results)
    safe_print(report)

    # Check if any files have dependencies
    unsafe_files = [r for r in results if not r.is_safe_to_delete]

    if unsafe_files:
        print_status(
            f"❌ {len(unsafe_files)} files have dependencies and cannot be safely deleted",
            "error",
        )

        # Generate fix plan
        fix_plan = checker.create_dependency_fix_plan(results)

        safe_print(f"\n🔧 DEPENDENCY FIX PLAN:")
        safe_print(f"   Files requiring updates: {len(fix_plan['files_to_update'])}")
        safe_print(f"   Total changes needed: {fix_plan['estimated_changes']}")
        safe_print(
            f"   Manual review required: {len(fix_plan['manual_review_needed'])}"
        )

        return False
    else:
        print_status(f"✅ All {len(target_files)} files are safe to delete", "success")
        return True


if __name__ == "__main__":
    # Test the dependency checker
    import sys

    if len(sys.argv) > 1:
        root = Path(sys.argv[1])
        test_files = [Path(f) for f in sys.argv[2:]]
    else:
        root = Path.cwd()
        # Test with some example files
        test_files = [
            root / "README.md",
            root / "pyproject.toml",
        ]

    print("Testing dependency checker...")
    is_safe = check_cleanup_dependencies(root, test_files)
    print(f"Safe to delete: {is_safe}")
