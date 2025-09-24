"""
File Organization Analysis Engine

This module provides comprehensive analysis of file organization and placement,
identifying opportunities for better codebase structure and providing
recommendations for optimal file organization.

Author: AI Assistant
"""

import ast
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class FileOrganizationIssue:
    """Represents an organization issue found during analysis."""

    file_path: str
    issue_type: str  # 'wrong_location', 'should_consolidate', 'should_split', etc.
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    recommendation: str
    suggested_location: Optional[str] = None
    related_files: List[str] = field(default_factory=list)


@dataclass
class DirectoryAnalysis:
    """Analysis of a directory's contents and organization."""

    path: str
    file_count: int = 0
    total_lines: int = 0
    file_types: Dict[str, int] = field(default_factory=dict)
    subdirectories: List[str] = field(default_factory=list)
    cohesion_score: float = 0.0  # How related files are within directory
    complexity_score: float = 0.0  # Directory complexity


@dataclass
class FileOrganizationResult:
    """Complete file organization analysis result."""

    directories_analyzed: int = 0
    files_analyzed: int = 0
    total_issues: int = 0
    issues_by_type: Dict[str, int] = field(default_factory=dict)
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    directory_analysis: Dict[str, DirectoryAnalysis] = field(default_factory=dict)
    organization_issues: List[FileOrganizationIssue] = field(default_factory=list)
    consolidation_candidates: List[List[str]] = field(default_factory=list)
    restructuring_recommendations: List[Dict[str, Any]] = field(default_factory=list)


class FileOrganizationAnalyzer:
    """
    Comprehensive file organization analysis engine.

    Analyzes file placement patterns and provides recommendations for
    optimal codebase organization, identifying files in wrong locations
    and suggesting better directory structures.
    """

    def __init__(
        self,
        root_path: Path,
        exclude_patterns: Optional[List[str]] = None,
        max_files: int = 10000,
        max_relationship_files: int = 2000,
    ):
        """
        Initialize the file organization analyzer.

        Args:
            root_path: Root directory to analyze
            exclude_patterns: List of glob patterns to exclude
            max_files: Maximum number of files to analyze (default: 10000)
            max_relationship_files: Maximum Python files to analyze for relationships (default: 2000)
        """
        self.root_path = root_path
        self.max_files = max_files
        self.max_relationship_files = max_relationship_files
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
        self.all_files: List[str] = []
        self.file_imports: Dict[str, Set[str]] = defaultdict(set)
        self.file_exports: Dict[str, Set[str]] = defaultdict(set)
        self.file_sizes: Dict[str, int] = {}
        self.file_complexity: Dict[str, float] = {}

    def analyze_organization(self) -> FileOrganizationResult:
        """
        Perform comprehensive file organization analysis.

        Returns:
            FileOrganizationResult with complete analysis
        """
        print("📁 Starting comprehensive file organization analysis...")

        # Phase 1: Discover and categorize all files
        print("📋 Phase 1: Discovering and categorizing files...")
        self._discover_files()
        print(f"📊 Discovered {len(self.all_files)} files")

        # Phase 2: Analyze file relationships and dependencies
        print("🔗 Phase 2: Analyzing file relationships...")
        self._analyze_file_relationships()
        print("✅ Relationship analysis complete")

        # Phase 3: Analyze directory structures
        print("🏗️  Phase 3: Analyzing directory structures...")
        self.directory_analysis = self._analyze_directories()
        print(
            f"✅ Directory analysis complete, "
            f"{len(self.directory_analysis)} directories analyzed"
        )

        # Phase 4: Identify organization issues
        print("🎯 Phase 4: Identifying organization issues...")
        organization_issues = self._identify_organization_issues()
        print(f"📊 Found {len(organization_issues)} organization issues")

        # Phase 5: Find consolidation opportunities
        print("🔗 Phase 5: Finding consolidation opportunities...")
        consolidation_candidates = self._find_consolidation_candidates()
        print(f"📊 Found {len(consolidation_candidates)} consolidation candidates")

        # Phase 6: Generate restructuring recommendations
        print("💡 Phase 6: Generating restructuring recommendations...")
        restructuring_recommendations = self._generate_restructuring_recommendations()

        # Use advanced structural recommendation engine if available
        try:
            from .structural_recommendation_engine import StructuralRecommendationEngine

            # Create a temporary result object for the engine
            temp_result = FileOrganizationResult()
            temp_result.directories_analyzed = len(self.directory_analysis)
            temp_result.files_analyzed = len(self.all_files)
            temp_result.organization_issues = organization_issues
            temp_result.directory_analysis = self.directory_analysis

            engine = StructuralRecommendationEngine(self.root_path)
            advanced_recommendations = engine.generate_recommendations(temp_result)

            # Convert advanced recommendations to simple format for compatibility
            for move in advanced_recommendations.file_moves:
                restructuring_recommendations.append(
                    {
                        "type": "move_file",
                        "description": f"Move {move.file_path} to {move.recommended_location}",
                        "file": move.file_path,
                        "from": move.current_location,
                        "to": move.recommended_location,
                        "rationale": move.rationale,
                        "priority": move.priority,
                    }
                )

            for merge in advanced_recommendations.file_merges:
                restructuring_recommendations.append(
                    {
                        "type": "merge_files",
                        "description": f"Merge {len(merge.source_files)} files into {merge.target_file}",
                        "target": merge.target_file,
                        "sources": merge.source_files,
                        "rationale": merge.rationale,
                        "priority": merge.priority,
                    }
                )

            print(
                f"💡 Generated {len(restructuring_recommendations)} total recommendations (including advanced analysis)"
            )
        except ImportError:
            print(
                f"💡 Generated {len(restructuring_recommendations)} basic recommendations"
            )

        # Compile results
        result = FileOrganizationResult()
        result.directories_analyzed = len(self.directory_analysis)
        result.files_analyzed = len(self.all_files)
        result.total_issues = len(organization_issues)
        result.directory_analysis = self.directory_analysis
        result.organization_issues = organization_issues
        result.consolidation_candidates = consolidation_candidates
        result.restructuring_recommendations = restructuring_recommendations

        # Count issues by type and severity
        for issue in organization_issues:
            result.issues_by_type[issue.issue_type] = (
                result.issues_by_type.get(issue.issue_type, 0) + 1
            )
            result.issues_by_severity[issue.severity] = (
                result.issues_by_severity.get(issue.severity, 0) + 1
            )

        print("✅ File organization analysis complete!")
        return result

    def _discover_files(self) -> None:
        """Discover all relevant files in the codebase."""
        for root, dirs, files in os.walk(self.root_path):
            # Filter out excluded directories early
            dirs[:] = [d for d in dirs if not self._is_excluded(os.path.join(root, d))]

            for file in files:
                if len(self.all_files) >= self.max_files:
                    print(
                        f"ℹ️ Limiting file discovery to {self.max_files} files (configurable via max_files parameter)"
                    )
                    return

                file_path = os.path.join(root, file)
                if not self._is_excluded(file_path):
                    self.all_files.append(file_path)

                    # Get file size
                    try:
                        self.file_sizes[file_path] = os.path.getsize(file_path)
                    except OSError:
                        self.file_sizes[file_path] = 0

                    # Calculate basic complexity for Python files
                    if file.endswith(".py"):
                        self._analyze_file_complexity(file_path)

    def _is_excluded(self, path: str) -> bool:
        """Check if a path should be excluded."""
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

    def _analyze_file_complexity(self, file_path: str) -> None:
        """Calculate basic complexity metrics for a Python file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            non_empty_lines = [line for line in lines if line.strip()]

            # Basic complexity metrics
            complexity = 0
            complexity += len(
                [
                    line
                    for line in non_empty_lines
                    if any(
                        keyword in line
                        for keyword in [
                            "if ",
                            "for ",
                            "while ",
                            "try:",
                            "def ",
                            "class ",
                        ]
                    )
                ]
            )
            complexity += (
                len(
                    [
                        line
                        for line in non_empty_lines
                        if " and " in line or " or " in line
                    ]
                )
                * 0.5
            )
            complexity += (
                len([line for line in non_empty_lines if line.count("(") > 3]) * 0.3
            )

            self.file_complexity[file_path] = complexity

        except Exception:
            self.file_complexity[file_path] = 0

    def _analyze_file_relationships(self) -> None:
        """Analyze relationships between files through imports."""
        processed_count = 0

        for file_path in self.all_files:
            if processed_count >= self.max_relationship_files:
                print(
                    f"ℹ️ Limiting relationship analysis to {self.max_relationship_files} Python files (configurable via max_relationship_files parameter)"
                )
                break

            if file_path.endswith(".py"):
                processed_count += 1

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    tree = ast.parse(content, filename=file_path)
                    file_module = self._file_to_module(file_path)

                    # Extract imports
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imported_module = alias.name.split(".")[0]
                                if imported_module != file_module:
                                    self.file_imports[file_path].add(imported_module)

                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imported_module = node.module.split(".")[0]
                                if imported_module != file_module:
                                    self.file_imports[file_path].add(imported_module)

                    # Extract exports (functions, classes defined)
                    exports = set()
                    for node in ast.walk(tree):
                        if isinstance(
                            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                        ):
                            exports.add(node.name)

                    self.file_exports[file_path] = exports

                except Exception:
                    continue

    def _file_to_module(self, file_path: str) -> str:
        """Convert file path to module name."""
        rel_path = os.path.relpath(file_path, self.root_path)
        if rel_path.endswith(".py"):
            rel_path = rel_path[:-3]
        return rel_path.replace(os.sep, ".")

    def _analyze_directories(self) -> Dict[str, DirectoryAnalysis]:
        """Analyze the organization of each directory."""
        directory_analysis = {}

        # Simple approach: analyze each directory directly
        directories = set()
        for file_path in self.all_files:
            directories.add(os.path.dirname(file_path))

        for dir_path in directories:

            # Get files in this directory only
            dir_files = [f for f in self.all_files if os.path.dirname(f) == dir_path]
            analysis = DirectoryAnalysis(path=dir_path)

            analysis.file_count = len(dir_files)

            # Count file types
            for file_path in dir_files:
                _, ext = os.path.splitext(file_path)
                analysis.file_types[ext] = analysis.file_types.get(ext, 0) + 1

                # Count lines for Python files
                if ext == ".py" and file_path in self.file_sizes:
                    analysis.total_lines += self.file_sizes.get(file_path, 0)

            # Find subdirectories
            try:
                analysis.subdirectories = [
                    d
                    for d in os.listdir(dir_path)
                    if os.path.isdir(os.path.join(dir_path, d))
                ]
            except OSError:
                analysis.subdirectories = []

            # Calculate cohesion (how related files are)
            analysis.cohesion_score = self._calculate_directory_cohesion(dir_files)

            # Calculate complexity
            analysis.complexity_score = (
                len(dir_files) + len(analysis.subdirectories) * 2
            )

            directory_analysis[dir_path] = analysis

        return directory_analysis

    def _calculate_directory_cohesion(self, dir_files: List[str]) -> float:
        """Calculate how cohesive a directory is (0-100)."""
        if not dir_files:
            return 100.0

        # Cohesion based on file type consistency
        file_types = Counter()
        for file_path in dir_files:
            _, ext = os.path.splitext(file_path)
            file_types[ext] += 1

        if not file_types:
            return 100.0

        # Calculate entropy (lower entropy = higher cohesion)
        total_files = sum(file_types.values())
        entropy = 0
        for count in file_types.values():
            p = count / total_files
            if p > 0:
                entropy -= p * (p**0.5)  # Simplified entropy

        # Convert to cohesion score (100 - normalized entropy)
        cohesion = max(0, 100 - (entropy * 50))
        return cohesion

    def _identify_organization_issues(self) -> List[FileOrganizationIssue]:
        """Identify files that are potentially in wrong locations."""
        issues = []

        for file_path in self.all_files:
            file_issues = self._analyze_file_placement(file_path)
            issues.extend(file_issues)

        # Check for directories with organization issues
        dir_issues = self._analyze_directory_issues()
        issues.extend(dir_issues)

        return issues

    def _analyze_file_placement(self, file_path: str) -> List[FileOrganizationIssue]:
        """Analyze if a file is in the right location."""
        issues = []

        # Check for files at root level that should be organized
        if os.path.dirname(file_path) == str(self.root_path):
            basename = os.path.basename(file_path)

            # Configuration files that should be in config/
            config_files = ["mypy.ini", "tox.ini", ".pre-commit-config.yaml"]
            if any(config in basename for config in config_files):
                issues.append(
                    FileOrganizationIssue(
                        file_path=file_path,
                        issue_type="wrong_location",
                        severity="medium",
                        message=f"Configuration file '{basename}' should be in config/ directory",
                        recommendation="Move configuration files to a dedicated config/ directory",
                        suggested_location="config/",
                    )
                )

            # Documentation files that should be in docs/
            if basename.lower() in ["readme.md", "changelog.md", "contributing.md"]:
                issues.append(
                    FileOrganizationIssue(
                        file_path=file_path,
                        issue_type="wrong_location",
                        severity="low",
                        message=f"Documentation file '{basename}' should be in docs/ directory",
                        recommendation="Move documentation files to docs/ directory",
                        suggested_location="docs/",
                    )
                )

        # Check for Python files in wrong locations
        if file_path.endswith(".py"):
            issues.extend(self._analyze_python_file_placement(file_path))

        return issues

    def _analyze_python_file_placement(
        self, file_path: str
    ) -> List[FileOrganizationIssue]:
        """Analyze Python file placement specifically."""
        issues = []

        # Check for test files outside tests/ directory
        if "test_" in os.path.basename(file_path) or "_test" in os.path.basename(
            file_path
        ):
            if "tests" not in file_path:
                issues.append(
                    FileOrganizationIssue(
                        file_path=file_path,
                        issue_type="wrong_location",
                        severity="high",
                        message=f"Test file should be in tests/ directory",
                        recommendation="Move test files to appropriate test directories",
                        suggested_location="tests/",
                    )
                )

        # Check for example files outside examples/ directory
        if any(
            word in os.path.basename(file_path).lower()
            for word in ["example", "demo", "sample"]
        ):
            if "examples" not in file_path and "docs" not in file_path:
                issues.append(
                    FileOrganizationIssue(
                        file_path=file_path,
                        issue_type="wrong_location",
                        severity="medium",
                        message=f"Example file should be in examples/ directory",
                        recommendation="Move example files to examples/ directory",
                        suggested_location="examples/",
                    )
                )

        # Check for script files outside scripts/ directory
        if any(
            word in os.path.basename(file_path).lower()
            for word in ["script", "tool", "util"]
        ):
            if "scripts" not in file_path and "bin" not in file_path:
                issues.append(
                    FileOrganizationIssue(
                        file_path=file_path,
                        issue_type="wrong_location",
                        severity="medium",
                        message=f"Script/utility file should be in scripts/ directory",
                        recommendation="Move utility scripts to scripts/ directory",
                        suggested_location="scripts/",
                    )
                )

        return issues

    def _analyze_directory_issues(self) -> List[FileOrganizationIssue]:
        """Analyze directory-level organization issues."""
        issues = []

        # Check for directories with too many files
        for dir_path, analysis in self.directory_analysis.items():
            if analysis.file_count > 50:
                issues.append(
                    FileOrganizationIssue(
                        file_path=dir_path,
                        issue_type="should_split",
                        severity="high",
                        message=f"Directory contains {analysis.file_count} files - consider splitting",
                        recommendation=(
                            "Split large directories into smaller, more focused modules"
                        ),
                        related_files=[
                            f for f in self.all_files if f.startswith(dir_path)
                        ],
                    )
                )

            # Check for directories with mixed file types
            if len(analysis.file_types) > 3:
                issues.append(
                    FileOrganizationIssue(
                        file_path=dir_path,
                        issue_type="mixed_content",
                        severity="medium",
                        message=f"Directory contains {len(analysis.file_types)} different file types",
                        recommendation="Separate different file types into dedicated directories",
                        related_files=[
                            f for f in self.all_files if f.startswith(dir_path)
                        ],
                    )
                )

        return issues

    def _find_consolidation_candidates(self) -> List[List[str]]:
        """Find files that could be consolidated."""
        consolidation_candidates = []

        # Group files by functionality
        functionality_groups = defaultdict(list)

        for file_path in self.all_files:
            if file_path.endswith(".py"):
                # Simple heuristic: group by common prefixes/suffixes
                basename = os.path.basename(file_path)
                prefix = (
                    basename.split("_")[0]
                    if "_" in basename
                    else basename.split(".")[0]
                )

                # Skip generic names
                if prefix not in ["__init__", "__main__", "utils", "helpers", "common"]:
                    functionality_groups[prefix].append(file_path)

        # Find groups with multiple small files
        for prefix, files in functionality_groups.items():
            if len(files) >= 3:
                total_lines = sum(self.file_sizes.get(f, 0) for f in files)
                avg_lines = total_lines / len(files) if files else 0

                # If files are small and related, suggest consolidation
                if avg_lines < 100 and len(files) >= 3:
                    consolidation_candidates.append(files)

        return consolidation_candidates

    def _generate_restructuring_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations for directory restructuring."""
        recommendations = []

        # Analyze current structure
        root_dirs = set()
        for file_path in self.all_files:
            rel_path = os.path.relpath(file_path, self.root_path)
            top_level = rel_path.split(os.sep)[0] if os.sep in rel_path else rel_path
            if "." not in top_level:  # Skip files
                root_dirs.add(top_level)

        # Check for missing standard directories
        standard_dirs = ["src", "tests", "docs", "scripts", "examples", "config"]
        missing_dirs = [d for d in standard_dirs if d not in root_dirs]

        if missing_dirs:
            recommendations.append(
                {
                    "type": "create_directories",
                    "description": f"Create standard directories: {', '.join(missing_dirs)}",
                    "directories": missing_dirs,
                    "rationale": "Following Python project conventions for better organization",
                }
            )

        # Check for overly complex directory structures
        deep_paths = [f for f in self.all_files if f.count(os.sep) > 4]
        if deep_paths:
            recommendations.append(
                {
                    "type": "flatten_structure",
                    "description": f"Found {len(deep_paths)} files in deep directory structures",
                    "affected_files": deep_paths[:5],  # Show first 5
                    "rationale": "Reduce directory depth for better navigability",
                }
            )

        return recommendations

    def generate_organization_report(
        self, result: FileOrganizationResult, output_path: Optional[str] = None
    ) -> str:
        """Generate a comprehensive file organization analysis report."""
        report_lines = []

        report_lines.append("=" * 80)
        report_lines.append("📁 FILE ORGANIZATION ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")

        report_lines.append("📊 OVERVIEW:")
        report_lines.append(f"   Directories Analyzed: {result.directories_analyzed}")
        report_lines.append(f"   Files Analyzed: {result.files_analyzed}")
        report_lines.append(f"   Organization Issues: {result.total_issues}")
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

        # Top organization issues
        if result.organization_issues:
            report_lines.append("🎯 ORGANIZATION ISSUES:")
            # Sort by severity
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            sorted_issues = sorted(
                result.organization_issues,
                key=lambda x: severity_order.get(x.severity, 4),
            )[:15]

            for i, issue in enumerate(sorted_issues, 1):
                severity_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢",
                }.get(issue.severity, "⚪")
                report_lines.append(f"   {i}. {severity_emoji} {issue.file_path}")
                report_lines.append(f"      {issue.message}")
                report_lines.append(f"      💡 {issue.recommendation}")
                if issue.suggested_location:
                    report_lines.append(
                        f"      📂 Suggested: {issue.suggested_location}"
                    )
                report_lines.append("")

        # Consolidation candidates
        if result.consolidation_candidates:
            report_lines.append("🔗 CONSOLIDATION CANDIDATES:")
            for i, files in enumerate(result.consolidation_candidates[:5], 1):
                report_lines.append(f"   {i}. {len(files)} related files:")
                for file_path in files[:3]:  # Show first 3
                    report_lines.append(f"      • {os.path.basename(file_path)}")
                if len(files) > 3:
                    report_lines.append(f"      ... and {len(files) - 3} more")
                report_lines.append("")

        # Restructuring recommendations
        if result.restructuring_recommendations:
            report_lines.append("🏗️  RESTRUCTURING RECOMMENDATIONS:")
            for i, rec in enumerate(result.restructuring_recommendations, 1):
                report_lines.append(f"   {i}. {rec['description']}")
                report_lines.append(f"      💡 {rec['rationale']}")
                report_lines.append("")

        # Directory analysis summary
        if result.directory_analysis:
            # Find most complex directories
            complex_dirs = sorted(
                result.directory_analysis.items(),
                key=lambda x: x[1].complexity_score,
                reverse=True,
            )[:5]

            report_lines.append("🏗️  MOST COMPLEX DIRECTORIES:")
            for dir_path, analysis in complex_dirs:
                report_lines.append(
                    f"   • {os.path.basename(dir_path)}: {analysis.file_count} files"
                )
            report_lines.append("")

        report_lines.append("=" * 80)

        report = "\n".join(report_lines)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"📄 Organization report saved to: {output_path}")

        return report


def main():
    """CLI entry point for file organization analysis."""
    import argparse

    parser = argparse.ArgumentParser(description="File Organization Analysis Engine")
    parser.add_argument("--path", default=".", help="Path to analyze")
    parser.add_argument("--output", help="Output report file")
    parser.add_argument("--exclude", nargs="*", help="Additional patterns to exclude")

    args = parser.parse_args()

    root_path = Path(args.path)
    analyzer = FileOrganizationAnalyzer(root_path, args.exclude)

    try:
        result = analyzer.analyze_organization()
        report = analyzer.generate_organization_report(result, args.output)

        print(report)

    except Exception as e:
        print(f"❌ Error during organization analysis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
