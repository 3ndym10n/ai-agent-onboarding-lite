"""
Codebase Analysis & Organization System

This module provides comprehensive analysis of codebase structure, organization,
and quality. It identifies organizational improvements, structural issues,
and provides actionable recommendations.

Key Components:
- File Organization Analysis: Analyzes current file placement and suggests optimal structure
- Structural Recommendations: Recommends file moves, merges, and directory restructuring
- Code Quality Analysis: Detects unused imports, dead code, and quality metrics
- Dependency Mapping: Analyzes module relationships and usage patterns
- Duplicate Detection: Identifies code duplication across the codebase
"""

import ast
import hashlib
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from . import utils
from .tool_usage_tracker import track_tool_usage
from .unicode_utils import print_activity, print_status, safe_print


@dataclass
class FileOrganizationIssue:
    """Represents an issue with file organization."""

    file_path: Path
    issue_type: str  # 'wrong_directory', 'should_merge', 'should_split', 'naming_issue'
    severity: str  # 'low', 'medium', 'high'
    description: str
    suggestion: str
    confidence: float  # 0.0 to 1.0


@dataclass
class CodeQualityIssue:
    """Represents a code quality issue."""

    file_path: Path
    line_number: Optional[int]
    issue_type: str  # 'unused_import', 'dead_code', 'complex_function', etc.
    severity: str
    description: str
    suggestion: str
    confidence: float


@dataclass
class DependencyInfo:
    """Information about module dependencies."""

    module_name: str
    file_path: Path
    imports: Set[str] = field(default_factory=set)
    imported_by: Set[str] = field(default_factory=set)
    functions_defined: Set[str] = field(default_factory=set)
    classes_defined: Set[str] = field(default_factory=set)
    functions_used: Set[str] = field(default_factory=set)
    classes_used: Set[str] = field(default_factory=set)


@dataclass
class DuplicateCodeBlock:
    """Represents a block of duplicate code."""

    hash_value: str
    files: List[Tuple[Path, int, int]]  # (file_path, start_line, end_line)
    line_count: int
    code_snippet: str
    similarity_score: float


class CodebaseAnalyzer:
    """
    Comprehensive codebase analysis engine.

    Analyzes:
    - File organization and structure
    - Code quality metrics
    - Dependencies and imports
    - Code duplication
    - Structural recommendations
    """

    def __init__(self, root: Path):
        self.root = root
        self.dependency_map: Dict[str, DependencyInfo] = {}
        self.organization_issues: List[FileOrganizationIssue] = []
        self.quality_issues: List[CodeQualityIssue] = []
        self.duplicates: List[DuplicateCodeBlock] = []

        # Analysis configuration
        self.min_duplicate_lines = 6
        self.max_complexity = 15
        self.ignore_patterns = [
            "__pycache__",
            ".git",
            "venv",
            "node_modules",
            ".ai_onboard",
            "*.pyc",
            "*.pyo",
            "*.egg-info",
        ]

    def analyze_codebase(self) -> Dict[str, Any]:
        """
        Perform comprehensive codebase analysis.

        Returns:
            Dict containing all analysis results
        """
        track_tool_usage(
            "codebase_analyzer",
            "analyze_codebase",
            "Starting comprehensive codebase analysis",
        )
        print_activity("🔍 Starting comprehensive codebase analysis...")

        # Build dependency map
        self._build_dependency_map()

        # Analyze file organization
        self._analyze_file_organization()

        # Analyze code quality
        self._analyze_code_quality()

        # Detect duplicates
        self._detect_duplicates()

        # Generate structural recommendations
        recommendations = self._generate_structural_recommendations()

        results = {
            "dependency_map": self.dependency_map,
            "organization_issues": self.organization_issues,
            "quality_issues": self.quality_issues,
            "duplicates": self.duplicates,
            "recommendations": recommendations,
            "summary": self._generate_summary(),
        }

        print_status(
            f"✅ Analysis complete - found {len(self.organization_issues)} org issues, "
            f"{len(self.quality_issues)} quality issues, {len(self.duplicates)} duplicates"
        )

        return results

    def _build_dependency_map(self):
        """Build comprehensive dependency map of all Python modules."""
        track_tool_usage(
            "codebase_analyzer",
            "build_dependency_map",
            f"Building dependency map for {len(self._find_python_files())} Python files",
        )
        print_activity("📊 Building dependency map...")

        python_files = self._find_python_files()

        for py_file in python_files:
            try:
                module_name = self._get_module_name(py_file)
                dep_info = self._analyze_file_dependencies(py_file)
                self.dependency_map[module_name] = dep_info

            except Exception as e:
                print_status(f"⚠️ Error analyzing {py_file}: {e}")

        # Cross-reference imports
        self._cross_reference_imports()
        track_tool_usage(
            "codebase_analyzer",
            "cross_reference_imports",
            f"Cross-referenced imports for {len(self.dependency_map)} modules",
        )

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the codebase."""
        python_files = []

        for root_dir, dirs, files in os.walk(self.root):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(Path(root_dir) / d)]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root_dir) / file
                    if not self._should_ignore(file_path):
                        python_files.append(file_path)

        return python_files

    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        path_str = str(path)

        for pattern in self.ignore_patterns:
            if "*" in pattern:
                # Simple glob matching
                if pattern.startswith("*"):
                    if path_str.endswith(pattern[1:]):
                        return True
                elif pattern.endswith("*"):
                    if path_str.startswith(pattern[:-1]):
                        return True
            else:
                if pattern in path_str:
                    return True

        return False

    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path."""
        rel_path = file_path.relative_to(self.root)
        return str(rel_path.with_suffix("")).replace(os.sep, ".")

    def _analyze_file_dependencies(self, file_path: Path) -> DependencyInfo:
        """Analyze dependencies in a single Python file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            dep_info = DependencyInfo(
                module_name=self._get_module_name(file_path), file_path=file_path
            )

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dep_info.imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dep_info.imports.add(node.module)

                # Extract function definitions
                elif isinstance(node, ast.FunctionDef):
                    dep_info.functions_defined.add(node.name)

                # Extract class definitions
                elif isinstance(node, ast.ClassDef):
                    dep_info.classes_defined.add(node.name)

            # Simple heuristic for usage detection
            dep_info.functions_used = self._extract_function_usage(content)
            dep_info.classes_used = self._extract_class_usage(content)

            return dep_info

        except Exception as e:
            # Return minimal info on error
            return DependencyInfo(
                module_name=self._get_module_name(file_path), file_path=file_path
            )

    def _extract_function_usage(self, content: str) -> Set[str]:
        """Extract function calls from content (heuristic)."""
        functions = set()

        # Look for function calls (very basic heuristic)
        lines = content.split("\n")
        for line in lines:
            # Match function calls like: func(), module.func(), self.func()
            matches = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", line)
            for match in matches:
                if not match.startswith(("if", "for", "while", "def", "class")):
                    functions.add(match)

        return functions

    def _extract_class_usage(self, content: str) -> Set[str]:
        """Extract class instantiations from content (heuristic)."""
        classes = set()

        # Look for class instantiations (very basic)
        lines = content.split("\n")
        for line in lines:
            # Match ClassName() patterns
            matches = re.findall(r"\b([A-Z][a-zA-Z0-9_]*)\s*\(", line)
            classes.update(matches)

        return classes

    def _cross_reference_imports(self):
        """Cross-reference imports to build imported_by relationships."""
        for module_name, dep_info in self.dependency_map.items():
            for imported_module in dep_info.imports:
                if imported_module in self.dependency_map:
                    self.dependency_map[imported_module].imported_by.add(module_name)

    def _analyze_file_organization(self):
        """Analyze file organization and identify issues."""
        track_tool_usage(
            "codebase_analyzer",
            "analyze_file_organization",
            f"Analyzing organization for {len(self.dependency_map)} modules",
        )
        print_activity("📁 Analyzing file organization...")

        for module_name, dep_info in self.dependency_map.items():
            issues = self._check_file_organization(dep_info)
            self.organization_issues.extend(issues)

    def _check_file_organization(
        self, dep_info: DependencyInfo
    ) -> List[FileOrganizationIssue]:
        """Check organization of a single file."""
        issues = []

        # Check if file is in appropriate directory
        expected_dir = self._suggest_directory(dep_info)
        actual_dir = dep_info.file_path.parent.relative_to(self.root)

        if expected_dir != actual_dir:
            confidence = self._calculate_directory_confidence(
                dep_info, expected_dir, actual_dir
            )

            if confidence > 0.7:
                issues.append(
                    FileOrganizationIssue(
                        file_path=dep_info.file_path,
                        issue_type="wrong_directory",
                        severity="medium",
                        description=f"File appears to be in wrong directory",
                        suggestion=f"Consider moving to {expected_dir}/",
                        confidence=confidence,
                    )
                )

        # Check for files that might benefit from merging
        merge_candidates = self._check_merge_candidates(dep_info)
        issues.extend(merge_candidates)

        # Check naming conventions
        naming_issues = self._check_naming_conventions(dep_info)
        issues.extend(naming_issues)

        return issues

    def _suggest_directory(self, dep_info: DependencyInfo) -> Path:
        """Suggest appropriate directory for a file based on its content."""
        # Simple heuristic based on module name and content
        parts = dep_info.module_name.split(".")

        # If it's in ai_onboard package
        if parts[0] == "ai_onboard":
            if len(parts) > 1:
                # Suggest subdirectory based on functionality
                category = self._categorize_module(dep_info)
                return Path("ai_onboard") / category
            else:
                return Path("ai_onboard")

        return dep_info.file_path.parent.relative_to(self.root)

    def _categorize_module(self, dep_info: DependencyInfo) -> str:
        """Categorize module based on its content and name."""
        name = dep_info.module_name.lower()

        if "cli" in name or "command" in name:
            return "cli"
        elif "core" in name or "engine" in name:
            return "core"
        elif "policy" in name or "rule" in name:
            return "policies"
        elif "plugin" in name:
            return "plugins"
        elif "test" in name:
            return "tests"
        else:
            return "core"  # default

    def _calculate_directory_confidence(
        self, dep_info: DependencyInfo, expected: Path, actual: Path
    ) -> float:
        """Calculate confidence in directory suggestion."""
        # Simple confidence based on naming patterns
        expected_str = str(expected).lower()
        actual_str = str(actual).lower()

        # If expected directory name appears in module name, higher confidence
        if expected_str.split("/")[-1] in dep_info.module_name.lower():
            return 0.8
        else:
            return 0.6

    def _check_merge_candidates(
        self, dep_info: DependencyInfo
    ) -> List[FileOrganizationIssue]:
        """Check if file should be merged with others."""
        issues = []

        # Look for small files that might be better merged
        if dep_info.file_path.stat().st_size < 1024:  # Less than 1KB
            # Check if there are related files in same directory
            related_files = self._find_related_files(dep_info)

            if len(related_files) > 0:
                issues.append(
                    FileOrganizationIssue(
                        file_path=dep_info.file_path,
                        issue_type="should_merge",
                        severity="low",
                        description=f"Small file ({dep_info.file_path.stat().st_size} bytes) might benefit from merging",
                        suggestion=f"Consider merging with: {', '.join(str(f) for f in related_files[:3])}",
                        confidence=0.5,
                    )
                )

        return issues

    def _find_related_files(self, dep_info: DependencyInfo) -> List[Path]:
        """Find files related to the given dependency info."""
        related = []

        # Simple heuristic: files in same directory with similar names
        dir_files = list(dep_info.file_path.parent.glob("*.py"))

        for file_path in dir_files:
            if file_path != dep_info.file_path:
                # Check if names are similar
                name1 = dep_info.file_path.stem
                name2 = file_path.stem

                # Simple similarity check
                if len(set(name1) & set(name2)) > 3:  # Share at least 4 characters
                    related.append(file_path)

        return related

    def _check_naming_conventions(
        self, dep_info: DependencyInfo
    ) -> List[FileOrganizationIssue]:
        """Check if file follows naming conventions."""
        issues = []

        filename = dep_info.file_path.stem

        # Check for snake_case vs camelCase
        if "_" in filename and any(c.isupper() for c in filename):
            issues.append(
                FileOrganizationIssue(
                    file_path=dep_info.file_path,
                    issue_type="naming_issue",
                    severity="low",
                    description="Filename mixes snake_case and camelCase",
                    suggestion="Use consistent naming: either snake_case or camelCase",
                    confidence=0.9,
                )
            )

        return issues

    def _analyze_code_quality(self):
        """Analyze code quality across all files."""
        track_tool_usage(
            "codebase_analyzer",
            "analyze_code_quality",
            f"Analyzing code quality for {len(self.dependency_map)} modules",
        )
        print_activity("🔍 Analyzing code quality...")

        for module_name, dep_info in self.dependency_map.items():
            try:
                issues = self._analyze_single_file_quality(dep_info)
                self.quality_issues.extend(issues)
            except Exception as e:
                print_status(f"⚠️ Error analyzing quality for {dep_info.file_path}: {e}")

    def _analyze_single_file_quality(
        self, dep_info: DependencyInfo
    ) -> List[CodeQualityIssue]:
        """Analyze code quality for a single file."""
        issues = []

        try:
            with open(dep_info.file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            lines = content.split("\n")

            # Check for unused imports
            unused_imports = self._find_unused_imports(tree, dep_info)
            for unused in unused_imports:
                issues.append(
                    CodeQualityIssue(
                        file_path=dep_info.file_path,
                        line_number=None,  # Could enhance to find line numbers
                        issue_type="unused_import",
                        severity="low",
                        description=f"Unused import: {unused}",
                        suggestion=f"Remove unused import '{unused}'",
                        confidence=0.8,
                    )
                )

            # Check function complexity
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    if complexity > self.max_complexity:
                        issues.append(
                            CodeQualityIssue(
                                file_path=dep_info.file_path,
                                line_number=node.lineno,
                                issue_type="complex_function",
                                severity="medium",
                                description=f"Function '{node.name}' has high complexity ({complexity})",
                                suggestion=f"Consider breaking down function '{node.name}' into smaller functions",
                                confidence=0.9,
                            )
                        )

        except Exception as e:
            print_status(f"⚠️ Quality analysis failed for {dep_info.file_path}: {e}")

        return issues

    def _find_unused_imports(
        self, tree: ast.AST, dep_info: DependencyInfo
    ) -> List[str]:
        """Find unused imports in the AST."""
        # This is a simplified version - a full implementation would need
        # more sophisticated analysis
        unused = []

        # Get all names imported
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)

        # Check which ones are actually used (simplified)
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)

        # Find unused imports (this is very basic)
        for name in imported_names:
            if name not in used_names and name not in [
                "os",
                "sys",
                "pathlib",
            ]:  # Common false positives
                unused.append(name)

        return unused

    def _calculate_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity

        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.Try):
                complexity += 1

        return complexity

    def _detect_duplicates(self):
        """Detect duplicate code blocks across the codebase."""
        track_tool_usage(
            "codebase_analyzer",
            "detect_duplicates",
            f"Detecting duplicate code blocks across {len(self.dependency_map)} modules",
        )
        print_activity("🔄 Detecting code duplicates...")

        code_blocks = []

        # Extract code blocks from all files
        for module_name, dep_info in self.dependency_map.items():
            try:
                blocks = self._extract_code_blocks(dep_info.file_path)
                code_blocks.extend([(dep_info.file_path, block) for block in blocks])
            except Exception as e:
                print_status(
                    f"⚠️ Error extracting blocks from {dep_info.file_path}: {e}"
                )

        # Group by hash
        hash_groups = defaultdict(list)
        for file_path, (start_line, end_line, code_hash, snippet) in code_blocks:
            hash_groups[code_hash].append((file_path, start_line, end_line, snippet))

        # Find duplicates
        for code_hash, occurrences in hash_groups.items():
            if len(occurrences) > 1:
                # Calculate line count from first occurrence
                _, start_line, end_line, snippet = occurrences[0]
                line_count = end_line - start_line + 1

                if line_count >= self.min_duplicate_lines:
                    self.duplicates.append(
                        DuplicateCodeBlock(
                            hash_value=code_hash,
                            files=[(fp, sl, el) for fp, sl, el, _ in occurrences],
                            line_count=line_count,
                            code_snippet=snippet,
                            similarity_score=1.0,  # Exact matches
                        )
                    )
        track_tool_usage(
            "codebase_analyzer",
            "duplicate_detection_complete",
            f"Found {len(self.duplicates)} duplicate code blocks",
        )

    def _extract_code_blocks(self, file_path: Path) -> List[Tuple[int, int, str, str]]:
        """Extract code blocks from a file for duplicate detection."""
        blocks = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Extract blocks of consecutive non-empty lines
            current_block = []
            start_line = 0

            for i, line in enumerate(lines, 1):
                line = line.strip()

                if line and not line.startswith("#"):  # Non-empty, non-comment
                    if not current_block:
                        start_line = i
                    current_block.append(line)
                else:
                    # End of block
                    if len(current_block) >= self.min_duplicate_lines:
                        block_text = "\n".join(current_block)
                        block_hash = hashlib.md5(block_text.encode()).hexdigest()
                        snippet = (
                            "\n".join(current_block[:3]) + "\n..."
                        )  # First 3 lines
                        blocks.append((start_line, i - 1, block_hash, snippet))

                    current_block = []

            # Handle last block
            if len(current_block) >= self.min_duplicate_lines:
                block_text = "\n".join(current_block)
                block_hash = hashlib.md5(block_text.encode()).hexdigest()
                snippet = "\n".join(current_block[:3]) + "\n..."
                blocks.append((start_line, len(lines), block_hash, snippet))

        except Exception as e:
            print_status(f"⚠️ Error extracting blocks from {file_path}: {e}")

        return blocks

    def _generate_structural_recommendations(self) -> Dict[str, Any]:
        """Generate structural recommendations based on analysis."""
        recommendations = {
            "directory_reorganization": [],
            "file_merges": [],
            "file_splits": [],
            "naming_standardization": [],
        }

        # Directory reorganization recommendations
        dir_usage = self._analyze_directory_usage()
        for dir_path, stats in dir_usage.items():
            if stats["file_count"] > 20:  # Large directory
                recommendations["directory_reorganization"].append(
                    {
                        "directory": str(dir_path),
                        "issue": f"Large directory with {stats['file_count']} files",
                        "suggestion": "Consider splitting into subdirectories by functionality",
                    }
                )

        # File merge recommendations
        for issue in self.organization_issues:
            if issue.issue_type == "should_merge":
                recommendations["file_merges"].append(
                    {"file": str(issue.file_path), "suggestion": issue.suggestion}
                )

        return recommendations

    def _analyze_directory_usage(self) -> Dict[Path, Dict[str, int]]:
        """Analyze file distribution across directories."""
        dir_stats = defaultdict(lambda: {"file_count": 0, "total_size": 0})

        for module_name, dep_info in self.dependency_map.items():
            rel_dir = dep_info.file_path.parent.relative_to(self.root)
            dir_stats[rel_dir]["file_count"] += 1
            dir_stats[rel_dir]["total_size"] += dep_info.file_path.stat().st_size

        return dict(dir_stats)

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary of analysis results."""
        return {
            "total_modules": len(self.dependency_map),
            "organization_issues_count": len(self.organization_issues),
            "quality_issues_count": len(self.quality_issues),
            "duplicate_blocks_count": len(self.duplicates),
            "severity_breakdown": {
                "organization": Counter(
                    issue.severity for issue in self.organization_issues
                ),
                "quality": Counter(issue.severity for issue in self.quality_issues),
            },
        }
