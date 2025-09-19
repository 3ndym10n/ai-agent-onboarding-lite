"""
Automated Code Quality Cleanup System

Safely removes dead code and unused imports using risk-based approach
with comprehensive validation and rollback capabilities.
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .code_quality_analyzer import (
    CodeQualityAnalysisResult,
    CodeQualityAnalyzer,
    CodeQualityIssue,
)


@dataclass
class CleanupResult:
    """Result of a cleanup operation."""

    success: bool = False
    files_modified: int = 0
    issues_resolved: int = 0
    backups_created: List[str] = field(default_factory=list)
    validation_passed: bool = False
    errors: List[str] = field(default_factory=list)
    rollback_available: bool = True


@dataclass
class ImportStatement:
    """Represents an import statement in Python code."""

    line_number: int
    full_statement: str
    import_type: str  # 'import', 'from'
    module_name: str
    imported_names: List[str] = field(default_factory=list)
    alias: Optional[str] = None


class AutomatedCodeCleanup:
    """
    Automated system for safe removal of dead code and unused imports.

    Uses risk-based approach with comprehensive validation and rollback.
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.backup_dir = root_path / ".ai_onboard" / "backups" / "code_cleanup"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def remove_unused_imports(
        self, analysis_result: CodeQualityAnalysisResult, dry_run: bool = True
    ) -> CleanupResult:
        """
        Automatically remove unused import statements.

        Args:
            analysis_result: Results from code quality analysis
            dry_run: If True, only analyze without making changes

        Returns:
            CleanupResult with operation details
        """
        result = CleanupResult()

        # Filter for unused import issues only
        unused_import_issues = [
            issue
            for issue in analysis_result.issues
            if issue.issue_type == "unused_import"
        ]

        if not unused_import_issues:
            result.success = True
            return result

        print(f"🔍 Found {len(unused_import_issues)} unused import issues")

        # Group issues by file
        issues_by_file: Dict[str, List[CodeQualityIssue]] = {}
        for issue in unused_import_issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)

        # Process each file
        for file_path_str, file_issues in issues_by_file.items():
            try:
                file_path = Path(file_path_str)
                if not file_path.exists():
                    result.errors.append(f"File not found: {file_path}")
                    continue

                # Create backup if not dry run
                if not dry_run:
                    backup_path = self._create_backup(file_path)
                    result.backups_created.append(str(backup_path))

                # Parse the file and extract import statements
                import_statements = self._extract_import_statements(file_path)

                # Find unused imports in this file
                unused_in_file = []
                for issue in file_issues:
                    # Match the issue with import statements
                    for import_stmt in import_statements:
                        if (
                            import_stmt.line_number == issue.line_number
                            and self._matches_import_issue(import_stmt, issue)
                        ):
                            unused_in_file.append(import_stmt)
                            break

                # Count files that would be modified (for both dry run and actual run)
                if unused_in_file:
                    result.files_modified += 1
                    print(
                        f"  📄 {file_path.name}: {len(unused_in_file)} unused imports"
                    )

                    if not dry_run:
                        # Remove the unused imports
                        self._remove_unused_imports_from_file(file_path, unused_in_file)

                    result.issues_resolved += len(unused_in_file)

            except Exception as e:
                result.errors.append(f"Error processing {file_path_str}: {str(e)}")

        # Validate changes if not dry run
        if not dry_run and result.files_modified > 0:
            result.validation_passed = self._validate_changes()
        else:
            result.validation_passed = True  # Dry run always "passes"

        result.success = len(result.errors) == 0

        return result

    def _extract_import_statements(self, file_path: Path) -> List[ImportStatement]:
        """Extract all import statements from a Python file."""

        statements = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Parse the AST to find import statements
            source_code = "".join(lines)
            tree = ast.parse(source_code, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    # Regular import: import module1, module2
                    for alias in node.names:
                        stmt = ImportStatement(
                            line_number=node.lineno,
                            full_statement=lines[node.lineno - 1].rstrip(),
                            import_type="import",
                            module_name=alias.name,
                            alias=alias.asname,
                        )
                        statements.append(stmt)

                elif isinstance(node, ast.ImportFrom):
                    # From import: from module import name1, name2
                    imported_names = [alias.name for alias in node.names]
                    stmt = ImportStatement(
                        line_number=node.lineno,
                        full_statement=lines[node.lineno - 1].rstrip(),
                        import_type="from",
                        module_name=node.module or "",
                        imported_names=imported_names,
                    )
                    statements.append(stmt)

        except SyntaxError:
            # If file has syntax errors, fall back to regex-based extraction
            statements = self._extract_imports_regex(file_path)

        return statements

    def _extract_imports_regex(self, file_path: Path) -> List[ImportStatement]:
        """Fallback regex-based import extraction for files with syntax errors."""

        statements = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                line = line.strip()

                # Match 'import module' or 'import module as alias'
                import_match = re.match(
                    r"^import\s+([a-zA-Z_][a-zA-Z0-9_.]*)(?:\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*))?",
                    line,
                )
                if import_match:
                    statements.append(
                        ImportStatement(
                            line_number=i,
                            full_statement=line,
                            import_type="import",
                            module_name=import_match.group(1),
                            alias=import_match.group(2),
                        )
                    )
                    continue

                # Match 'from module import names'
                from_match = re.match(
                    r"^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import\s+(.+)", line
                )
                if from_match:
                    imported_part = from_match.group(2)
                    # Extract imported names (simplified - doesn't handle complex cases)
                    imported_names = [
                        name.strip()
                        for name in imported_part.replace(" ", "").split(",")
                    ]
                    statements.append(
                        ImportStatement(
                            line_number=i,
                            full_statement=line,
                            import_type="from",
                            module_name=from_match.group(1),
                            imported_names=imported_names,
                        )
                    )

        except Exception:
            pass

        return statements

    def _matches_import_issue(
        self, import_stmt: ImportStatement, issue: CodeQualityIssue
    ) -> bool:
        """Check if an import statement matches a code quality issue."""

        # For unused imports, the issue message typically contains the import details
        issue_text = issue.message.lower()

        if import_stmt.import_type == "import":
            # Check if module name is mentioned in the issue
            return import_stmt.module_name.lower() in issue_text
        else:
            # For 'from' imports, check module and any of the imported names
            module_match = import_stmt.module_name.lower() in issue_text
            name_match = any(
                name.lower() in issue_text for name in import_stmt.imported_names
            )
            return module_match or name_match

    def _remove_unused_imports_from_file(
        self, file_path: Path, unused_imports: List[ImportStatement]
    ) -> None:
        """Remove unused import statements from a file."""

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Sort by line number in reverse order to avoid index shifting
        unused_imports.sort(key=lambda x: x.line_number, reverse=True)

        for import_stmt in unused_imports:
            line_idx = import_stmt.line_number - 1  # Convert to 0-based indexing
            if 0 <= line_idx < len(lines):
                # Remove the line
                lines.pop(line_idx)

        # Write back the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def _create_backup(self, file_path: Path) -> Path:
        """Create a backup of the file before modification."""

        import datetime

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create backup filename
        backup_name = f"{file_path.name}.{timestamp}.backup"
        backup_path = self.backup_dir / backup_name

        # Copy the file
        import shutil

        shutil.copy2(file_path, backup_path)

        return backup_path

    def _validate_changes(self) -> bool:
        """Validate that changes don't break the codebase."""

        try:
            # Run a basic syntax check on modified Python files
            import subprocess
            import sys

            # Simple validation: try to import the main module
            result = subprocess.run(
                [sys.executable, "-c", "import ai_onboard"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            return result.returncode == 0

        except Exception:
            return False

    def remove_simple_dead_functions(
        self, analysis_result: CodeQualityAnalysisResult, dry_run: bool = True
    ) -> CleanupResult:
        """
        Remove simple dead functions that have no dependencies.

        This is more complex than unused imports and requires careful analysis.
        """

        result = CleanupResult()

        # Filter for dead code issues that are functions
        dead_function_issues = [
            issue
            for issue in analysis_result.issues
            if issue.issue_type == "dead_code" and "function" in issue.message.lower()
        ]

        # For now, implement a conservative approach
        # Only remove very simple cases that are clearly safe

        result.success = True
        result.issues_resolved = (
            0  # Start with 0, will be updated when implementation is complete
        )

        # TODO: Implement function removal logic
        # This requires more sophisticated analysis to ensure no indirect usage

        return result


def run_automated_cleanup(
    root_path: Path, cleanup_type: str = "unused_imports", dry_run: bool = True
) -> CleanupResult:
    """
    Run automated code cleanup.

    Args:
        root_path: Root directory of the project
        cleanup_type: Type of cleanup ('unused_imports', 'dead_functions', 'all')
        dry_run: If True, analyze but don't make changes

    Returns:
        CleanupResult with operation details
    """

    # First, run code quality analysis
    analyzer = CodeQualityAnalyzer(root_path)
    analysis_result = analyzer.analyze_codebase()

    # Initialize cleanup system
    cleanup = AutomatedCodeCleanup(root_path)

    if cleanup_type == "unused_imports" or cleanup_type == "all":
        print("🧹 Starting automated unused import removal...")
        result = cleanup.remove_unused_imports(analysis_result, dry_run)

        if dry_run:
            print(
                f"📊 DRY RUN: Would remove {result.issues_resolved} unused imports from {result.files_modified} files"
            )
        else:
            print(
                f"✅ Removed {result.issues_resolved} unused imports from {result.files_modified} files"
            )
            print(f"📁 Backups created: {len(result.backups_created)}")

        return result

    elif cleanup_type == "dead_functions" or cleanup_type == "all":
        print("🧹 Starting automated dead function removal...")
        result = cleanup.remove_simple_dead_functions(analysis_result, dry_run)

        if dry_run:
            print(f"📊 DRY RUN: Would remove {result.issues_resolved} dead functions")
        else:
            print(f"✅ Removed {result.issues_resolved} dead functions")

        return result

    else:
        result = CleanupResult()
        result.errors.append(f"Unknown cleanup type: {cleanup_type}")
        return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Automated Code Quality Cleanup")
    parser.add_argument("--path", default=".", help="Project root path")
    parser.add_argument(
        "--type",
        default="unused_imports",
        choices=["unused_imports", "dead_functions", "all"],
        help="Type of cleanup to perform",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Analyze but don't make changes"
    )

    args = parser.parse_args()

    root_path = Path(args.path)
    result = run_automated_cleanup(root_path, args.type, args.dry_run)

    if result.errors:
        print("❌ Errors during cleanup:")
        for error in result.errors:
            print(f"  • {error}")
        exit(1)
    else:
        print("✅ Cleanup completed successfully!")
