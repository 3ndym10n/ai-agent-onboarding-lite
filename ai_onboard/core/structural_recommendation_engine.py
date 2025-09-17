"""
Structural Recommendation Engine for AI Agent Onboarding

This module provides intelligent recommendations for file organization,
directory restructuring, and code consolidation based on comprehensive
analysis of codebase structure and relationships.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class FileMoveRecommendation:
    """Recommendation for moving a file to a better location."""

    file_path: str
    current_location: str
    recommended_location: str
    rationale: str
    priority: str  # "high", "medium", "low"
    confidence: float  # 0.0 to 1.0


@dataclass
class FileMergeRecommendation:
    """Recommendation for merging files."""

    target_file: str
    source_files: List[str]
    rationale: str
    priority: str
    confidence: float
    estimated_effort: str  # "low", "medium", "high"


@dataclass
class DirectoryRestructuringPlan:
    """Comprehensive plan for directory restructuring."""

    plan_name: str
    description: str
    actions: List[Dict[str, Any]]
    benefits: List[str]
    risks: List[str]
    priority: str
    estimated_effort: str


@dataclass
class StructuralRecommendationResult:
    """Complete set of structural recommendations."""

    file_moves: List[FileMoveRecommendation] = field(default_factory=list)
    file_merges: List[FileMergeRecommendation] = field(default_factory=list)
    directory_plans: List[DirectoryRestructuringPlan] = field(default_factory=list)
    summary_stats: Dict[str, Any] = field(default_factory=dict)


class StructuralRecommendationEngine:
    """
    Engine for generating intelligent structural recommendations.

    Analyzes organization issues, file relationships, and directory structures
    to provide actionable recommendations for codebase restructuring.
    """

    def __init__(self, root_path: Path):
        """
        Initialize the structural recommendation engine.

        Args:
            root_path: Root directory of the project
        """
        self.root_path = root_path

        # Standard Python project structure
        self.standard_dirs = {
            "src": "Source code directory",
            "tests": "Test files and test utilities",
            "docs": "Documentation files",
            "scripts": "Utility scripts and tools",
            "examples": "Example usage and demos",
            "config": "Configuration files",
            "data": "Data files and datasets",
            "notebooks": "Jupyter notebooks",
            "requirements": "Dependency specifications",
        }

        # File type to directory mapping
        self.file_type_mapping = {
            ".py": ["src", "tests", "scripts"],
            ".md": ["docs", "."],
            ".txt": ["docs", "."],
            ".rst": ["docs", "."],
            ".yml": ["config", "."],
            ".yaml": ["config", "."],
            ".json": ["config", "."],
            ".ini": ["config", "."],
            ".cfg": ["config", "."],
            ".toml": ["config", "."],
            ".sh": ["scripts", "."],
            ".bat": ["scripts", "."],
            ".ps1": ["scripts", "."],
            ".ipynb": ["notebooks", "."],
            ".csv": ["data", "."],
            ".xlsx": ["data", "."],
            ".sql": ["data", "."],
        }

    def generate_recommendations(
        self,
        organization_result: Any,  # FileOrganizationResult from analyzer
        dependency_result: Optional[Any] = None,  # DependencyAnalysisResult
        quality_result: Optional[Any] = None,  # CodeQualityAnalysisResult
    ) -> StructuralRecommendationResult:
        """
        Generate comprehensive structural recommendations.

        Args:
            organization_result: Results from file organization analysis
            dependency_result: Optional dependency analysis results
            quality_result: Optional code quality analysis results

        Returns:
            Complete set of structural recommendations
        """
        result = StructuralRecommendationResult()

        print("🔧 Generating structural recommendations...")

        # Generate file move recommendations
        result.file_moves = self._generate_file_move_recommendations(
            organization_result
        )

        # Generate file merge recommendations
        result.file_merges = self._generate_file_merge_recommendations(
            organization_result, quality_result
        )

        # Generate directory restructuring plans
        result.directory_plans = self._generate_directory_plans(organization_result)

        # Calculate summary statistics
        result.summary_stats = self._calculate_summary_stats(result)

        print(f"✅ Generated {len(result.file_moves)} file move recommendations")
        print(f"✅ Generated {len(result.file_merges)} file merge recommendations")
        print(
            f"✅ Generated {len(result.directory_plans)} directory restructuring plans"
        )

        return result

    def _generate_file_move_recommendations(
        self, org_result: Any
    ) -> List[FileMoveRecommendation]:
        """Generate recommendations for moving files to better locations."""
        recommendations = []

        for issue in getattr(org_result, "organization_issues", []):
            if hasattr(issue, "issue_type") and issue.issue_type == "wrong_location":
                rec = self._analyze_wrong_location_issue(issue)
                if rec:
                    recommendations.append(rec)

        # Additional analysis for configuration files
        config_files = self._find_config_files(org_result)
        for file_path in config_files:
            if not self._is_in_config_directory(file_path):
                recommendations.append(
                    FileMoveRecommendation(
                        file_path=file_path,
                        current_location=str(Path(file_path).parent),
                        recommended_location="config/",
                        rationale="Configuration files should be in a dedicated config directory",
                        priority="medium",
                        confidence=0.8,
                    )
                )

        # Documentation files
        doc_files = self._find_documentation_files(org_result)
        for file_path in doc_files:
            if not self._is_in_docs_directory(file_path):
                recommendations.append(
                    FileMoveRecommendation(
                        file_path=file_path,
                        current_location=str(Path(file_path).parent),
                        recommended_location="docs/",
                        rationale="Documentation files should be in docs directory",
                        priority="low",
                        confidence=0.7,
                    )
                )

        return recommendations

    def _generate_file_merge_recommendations(
        self, org_result: Any, quality_result: Optional[Any] = None
    ) -> List[FileMergeRecommendation]:
        """Generate recommendations for merging similar files."""
        recommendations = []

        # Look for small files that could be consolidated
        if hasattr(org_result, "files_analyzed"):
            small_files = self._find_small_related_files(org_result)

            # Group by functionality
            merge_candidates = self._group_files_by_functionality(small_files)

            for functionality, files in merge_candidates.items():
                if len(files) >= 3:  # Only suggest merges for 3+ files
                    recommendations.append(
                        FileMergeRecommendation(
                            target_file=f"{functionality}.py",
                            source_files=[f["path"] for f in files],
                            rationale=f"Consolidate {len(files)} small {functionality} files into a single module",
                            priority="low",
                            confidence=0.6,
                            estimated_effort="medium",
                        )
                    )

        # Look for duplicate functionality based on quality analysis
        if quality_result:
            duplicate_functions = self._find_duplicate_functionality(quality_result)
            for dup in duplicate_functions:
                recommendations.append(
                    FileMergeRecommendation(
                        target_file=dup["target_file"],
                        source_files=dup["source_files"],
                        rationale=dup["rationale"],
                        priority="high",
                        confidence=0.8,
                        estimated_effort="high",
                    )
                )

        return recommendations

    def _generate_directory_plans(
        self, org_result: Any
    ) -> List[DirectoryRestructuringPlan]:
        """Generate comprehensive directory restructuring plans."""
        plans = []

        # Plan 1: Standard Python Project Structure
        standard_plan = self._create_standard_structure_plan(org_result)
        if standard_plan:
            plans.append(standard_plan)

        # Plan 2: Feature-Based Organization
        feature_plan = self._create_feature_based_plan(org_result)
        if feature_plan:
            plans.append(feature_plan)

        # Plan 3: Layered Architecture
        layered_plan = self._create_layered_architecture_plan(org_result)
        if layered_plan:
            plans.append(layered_plan)

        return plans

    def _analyze_wrong_location_issue(
        self, issue: Any
    ) -> Optional[FileMoveRecommendation]:
        """Analyze a wrong location issue and create recommendation."""
        file_path = getattr(issue, "file_path", "")
        if not file_path:
            return None

        # Determine recommended location based on file type
        file_ext = Path(file_path).suffix.lower()
        recommended_dirs = self.file_type_mapping.get(file_ext, ["."])

        # Choose the best directory based on current structure
        recommended_dir = self._choose_best_directory(file_path, recommended_dirs)

        if recommended_dir and recommended_dir != str(Path(file_path).parent):
            return FileMoveRecommendation(
                file_path=file_path,
                current_location=str(Path(file_path).parent),
                recommended_location=recommended_dir,
                rationale=getattr(issue, "message", "File in suboptimal location"),
                priority=getattr(issue, "severity", "medium"),
                confidence=0.75,
            )

        return None

    def _find_config_files(self, org_result: Any) -> List[str]:
        """Find configuration files in the codebase."""
        config_files = []
        config_extensions = [".yml", ".yaml", ".json", ".ini", ".cfg", ".toml", ".conf"]

        if hasattr(org_result, "files_analyzed"):
            # This would need to be implemented based on the actual structure
            # For now, return empty list
            pass

        return config_files

    def _find_documentation_files(self, org_result: Any) -> List[str]:
        """Find documentation files."""
        doc_files = []
        doc_patterns = ["README", "CHANGELOG", "CONTRIBUTING", "LICENSE"]

        if hasattr(org_result, "files_analyzed"):
            # Implementation would go here
            pass

        return doc_files

    def _is_in_config_directory(self, file_path: str) -> bool:
        """Check if file is in a config directory."""
        path_parts = Path(file_path).parts
        return "config" in path_parts

    def _is_in_docs_directory(self, file_path: str) -> bool:
        """Check if file is in a docs directory."""
        path_parts = Path(file_path).parts
        return "docs" in path_parts

    def _choose_best_directory(self, file_path: str, candidates: List[str]) -> str:
        """Choose the best directory from candidates."""
        # Simple logic: prefer existing directories
        for candidate in candidates:
            candidate_path = self.root_path / candidate
            if candidate_path.exists() and candidate_path.is_dir():
                return candidate

        # Fallback to first candidate
        return candidates[0] if candidates else "."

    def _find_small_related_files(self, org_result: Any) -> List[Dict[str, Any]]:
        """Find small files that could potentially be merged."""
        small_files = []

        # This would analyze file sizes and relationships
        # For now, return empty list as implementation depends on org_result structure

        return small_files

    def _group_files_by_functionality(
        self, files: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group files by their functionality."""
        groups = {}

        # Implementation would analyze file names and content
        # to group related functionality

        return groups

    def _find_duplicate_functionality(
        self, quality_result: Any
    ) -> List[Dict[str, Any]]:
        """Find duplicate functionality across files."""
        duplicates = []

        # This would analyze quality results for duplicate functions/methods

        return duplicates

    def _create_standard_structure_plan(
        self, org_result: Any
    ) -> Optional[DirectoryRestructuringPlan]:
        """Create a plan for standard Python project structure."""
        actions = []

        # Check for missing standard directories
        existing_dirs = set()
        if hasattr(org_result, "directory_analysis"):
            existing_dirs = set(org_result.directory_analysis.keys())

        missing_dirs = []
        for std_dir in self.standard_dirs:
            if std_dir not in existing_dirs:
                missing_dirs.append(std_dir)

        if missing_dirs:
            actions.append(
                {
                    "type": "create_directories",
                    "directories": missing_dirs,
                    "description": f"Create standard directories: {', '.join(missing_dirs)}",
                }
            )

        # Check for files that should be moved to standard directories
        move_actions = self._generate_standard_structure_moves(org_result)
        actions.extend(move_actions)

        if actions:
            return DirectoryRestructuringPlan(
                plan_name="Standard Python Project Structure",
                description="Restructure project to follow standard Python conventions",
                actions=actions,
                benefits=[
                    "Improved project navigability",
                    "Standardized structure for developers",
                    "Better separation of concerns",
                    "Easier CI/CD integration",
                ],
                risks=[
                    "May require updating import statements",
                    "Could break existing scripts or tools",
                ],
                priority="high",
                estimated_effort="medium",
            )

        return None

    def _create_feature_based_plan(
        self, org_result: Any
    ) -> Optional[DirectoryRestructuringPlan]:
        """Create a plan for feature-based organization."""
        # This would analyze the codebase to identify features
        # and suggest organizing by feature rather than by type

        # For now, return None as this is more complex
        return None

    def _create_layered_architecture_plan(
        self, org_result: Any
    ) -> Optional[DirectoryRestructuringPlan]:
        """Create a plan for layered architecture organization."""
        # This would suggest organizing by architectural layers
        # (presentation, business logic, data access, etc.)

        # For now, return None as this is very application-specific
        return None

    def _generate_standard_structure_moves(
        self, org_result: Any
    ) -> List[Dict[str, Any]]:
        """Generate move actions for standard structure."""
        actions = []

        # Implementation would analyze files and suggest moves to standard directories

        return actions

    def _calculate_summary_stats(
        self, result: StructuralRecommendationResult
    ) -> Dict[str, Any]:
        """Calculate summary statistics for recommendations."""
        return {
            "total_recommendations": len(result.file_moves)
            + len(result.file_merges)
            + len(result.directory_plans),
            "file_moves": len(result.file_moves),
            "file_merges": len(result.file_merges),
            "directory_plans": len(result.directory_plans),
            "high_priority_moves": len(
                [r for r in result.file_moves if r.priority == "high"]
            ),
            "high_priority_merges": len(
                [r for r in result.file_merges if r.priority == "high"]
            ),
            "high_priority_plans": len(
                [p for p in result.directory_plans if p.priority == "high"]
            ),
        }
