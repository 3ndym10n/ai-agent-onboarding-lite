"""
Risk Assessment Framework for Codebase Organization Changes

This module provides comprehensive risk assessment capabilities for evaluating
the safety and impact of codebase organization changes before implementation.
"""

import ast
import os
from pathlib import Path
from typing import Any, Dict, List, Set

from ..base.common_imports import Any, Dict, Enum, List, Path, dataclass, field

# Import moved to function level to avoid circular imports


class RiskLevel(Enum):
    """Risk level classifications."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ImpactLevel(Enum):
    """Impact level classifications."""

    MINIMAL = "minimal"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"


class LikelihoodLevel(Enum):
    """Likelihood level classifications."""

    VERY_UNLIKELY = "very_unlikely"
    UNLIKELY = "unlikely"
    POSSIBLE = "possible"
    LIKELY = "likely"
    VERY_LIKELY = "very_likely"


@dataclass
class RiskFactor:
    """Individual risk factor assessment."""

    name: str
    description: str
    impact: ImpactLevel
    likelihood: LikelihoodLevel
    detection_difficulty: int  # 1-3 (1=easy, 3=hard)
    mitigation_strength: float  # 0.5-2.0 (0.5=strong mitigation, 2.0=weak)


@dataclass
class OrganizationChange:
    """Represents a proposed organization change."""

    change_id: str
    change_type: str  # 'file_move', 'file_merge', 'directory_create', etc.
    description: str
    affected_files: List[str]
    risk_factors: List[RiskFactor] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)


@dataclass
class RiskAssessmentResult:
    """Complete risk assessment for a change."""

    change: OrganizationChange
    overall_risk_score: float
    risk_level: RiskLevel
    confidence_score: float  # 0.0-1.0
    impact_analysis: Dict[str, Any]
    dependency_analysis: Dict[str, Any]
    mitigation_effectiveness: float  # 0.0-1.0
    recommended_actions: List[str]
    safety_rating: str  # 'safe', 'caution', 'dangerous'


class RiskAssessmentFramework:
    """
    Comprehensive framework for assessing risks of codebase organization changes.

    Provides quantitative risk scoring, impact analysis, dependency mapping,
    and safety recommendations for organization changes.
    """

    def __init__(self, root_path: Path):
        """
        Initialize the risk assessment framework.

        Args:
            root_path: Root directory of the project
        """
        self.root_path = root_path

        # Risk scoring weights
        self.impact_weights = {
            ImpactLevel.MINIMAL: 1,
            ImpactLevel.MODERATE: 2,
            ImpactLevel.SIGNIFICANT: 3,
            ImpactLevel.SEVERE: 4,
            ImpactLevel.CATASTROPHIC: 5,
        }

        self.likelihood_weights = {
            LikelihoodLevel.VERY_UNLIKELY: 1,
            LikelihoodLevel.UNLIKELY: 2,
            LikelihoodLevel.POSSIBLE: 3,
            LikelihoodLevel.LIKELY: 4,
            LikelihoodLevel.VERY_LIKELY: 5,
        }

        # Import analysis cache
        self._import_cache: Dict[str, Set[str]] = {}
        self._reverse_import_cache: Dict[str, Set[str]] = {}

    def assess_change_risks(
        self,
        changes: List[OrganizationChange],
        include_dependencies: bool = True,
        include_impact_analysis: bool = True,
    ) -> List[RiskAssessmentResult]:
        """
        Assess risks for a list of organization changes.

        Args:
            changes: List of organization changes to assess
            include_dependencies: Whether to analyze dependencies
            include_impact_analysis: Whether to perform impact analysis

        Returns:
            List of risk assessment results
        """
        results = []

        print(f"🔍 Assessing risks for {len(changes)} organization changes...")

        # Track tool usage
        from ..orchestration.tool_usage_tracker import get_tool_tracker

        tracker = get_tool_tracker(self.root_path)

        for change in changes:
            result = self._assess_single_change(
                change, include_dependencies, include_impact_analysis
            )
            results.append(result)

            # Track individual change assessment
            tracker.track_tool_usage(
                tool_name="risk_assessment_engine",
                tool_type="analysis",
                parameters={
                    "change_type": change.change_type,
                    "affected_files": len(change.affected_files),
                },
                result="completed",
            )

        # Sort by risk score (highest first)
        results.sort(key=lambda x: x.overall_risk_score, reverse=True)

        print(f"✅ Risk assessment complete - {len(results)} changes evaluated")

        # Track overall assessment completion
        tracker.track_tool_usage(
            tool_name="comprehensive_risk_assessment",
            tool_type="analysis",
            parameters={
                "changes_assessed": len(results),
                "high_risk_count": len(
                    [r for r in results if r.risk_level.value in ["critical", "high"]]
                ),
            },
            result="completed",
        )

        return results

    def _assess_single_change(
        self,
        change: OrganizationChange,
        include_dependencies: bool,
        include_impact_analysis: bool,
    ) -> RiskAssessmentResult:
        """Assess risk for a single organization change."""

        # Calculate base risk score
        base_risk_score = self._calculate_risk_score(change.risk_factors)

        # Perform dependency analysis if requested
        dependency_analysis = {}
        if include_dependencies:
            dependency_analysis = self._analyze_dependencies(change)

        # Perform impact analysis if requested
        impact_analysis = {}
        if include_impact_analysis:
            impact_analysis = self._analyze_impact(change)

        # Calculate mitigation effectiveness
        mitigation_effectiveness = self._calculate_mitigation_effectiveness(change)

        # Apply mitigation factor to risk score
        adjusted_risk_score = base_risk_score * (2.0 - mitigation_effectiveness)

        # Determine risk level
        risk_level = self._determine_risk_level(adjusted_risk_score)

        # Calculate confidence score based on analysis completeness
        confidence_score = self._calculate_confidence_score(
            change, dependency_analysis, impact_analysis
        )

        # Determine safety rating
        safety_rating = self._determine_safety_rating(risk_level, confidence_score)

        # Generate recommended actions
        recommended_actions = self._generate_recommended_actions(
            change, risk_level, dependency_analysis, impact_analysis
        )

        return RiskAssessmentResult(
            change=change,
            overall_risk_score=adjusted_risk_score,
            risk_level=risk_level,
            confidence_score=confidence_score,
            impact_analysis=impact_analysis,
            dependency_analysis=dependency_analysis,
            mitigation_effectiveness=mitigation_effectiveness,
            recommended_actions=recommended_actions,
            safety_rating=safety_rating,
        )

    def _calculate_risk_score(self, risk_factors: List[RiskFactor]) -> float:
        """Calculate overall risk score from risk factors."""
        if not risk_factors:
            return 0.0

        total_score = 0.0
        for factor in risk_factors:
            impact_score = self.impact_weights[factor.impact]
            likelihood_score = self.likelihood_weights[factor.likelihood]

            # Base risk = Impact × Likelihood × Detection_Difficulty
            base_risk = impact_score * likelihood_score * factor.detection_difficulty

            # Apply mitigation factor
            mitigated_risk = base_risk * factor.mitigation_strength

            total_score += mitigated_risk

        return total_score / len(risk_factors)  # Average risk score

    def _analyze_dependencies(self, change: OrganizationChange) -> Dict[str, Any]:
        """Analyze dependencies affected by the change."""
        analysis: Dict[str, Any] = {
            "import_dependencies": [],
            "reverse_dependencies": [],
            "external_dependencies": [],
            "critical_paths": [],
        }

        for file_path in change.affected_files:
            if file_path.endswith(".py"):
                # Analyze imports in this file
                imports = self._analyze_file_imports(file_path)
                analysis["import_dependencies"].extend(imports)

                # Find files that import this file
                reverse_deps = self._find_reverse_dependencies(file_path)
                analysis["reverse_dependencies"].extend(reverse_deps)

        # Remove duplicates
        analysis["import_dependencies"] = list(set(analysis["import_dependencies"]))
        analysis["reverse_dependencies"] = list(set(analysis["reverse_dependencies"]))

        # Identify critical paths (files with many dependencies)
        critical_threshold = 5
        critical_files = [
            dep
            for dep in analysis["reverse_dependencies"]
            if len(self._find_reverse_dependencies(dep)) > critical_threshold
        ]
        analysis["critical_paths"] = list(set(critical_files))

        return analysis

    def _analyze_impact(self, change: OrganizationChange) -> Dict[str, Any]:
        """Analyze the impact of the change."""
        impact: Dict[str, Any] = {
            "affected_import_statements": 0,
            "affected_test_files": 0,
            "affected_config_files": 0,
            "breaking_change_potential": "low",
            "recovery_complexity": "low",
        }

        # Count affected imports
        dependency_analysis = self._analyze_dependencies(change)
        impact["affected_import_statements"] = len(
            dependency_analysis["import_dependencies"]
        )

        # Count affected test files
        test_files_affected = [
            dep
            for dep in dependency_analysis["reverse_dependencies"]
            if "test" in dep.lower() or dep.endswith("_test.py")
        ]
        impact["affected_test_files"] = len(test_files_affected)

        # Assess breaking change potential
        if impact["affected_import_statements"] > 20:
            impact["breaking_change_potential"] = "high"
        elif impact["affected_import_statements"] > 5:
            impact["breaking_change_potential"] = "medium"
        else:
            impact["breaking_change_potential"] = "low"

        # Assess recovery complexity
        total_affected = (
            impact["affected_import_statements"]
            + impact["affected_test_files"]
            + len(dependency_analysis["critical_paths"])
        )

        if total_affected > 50:
            impact["recovery_complexity"] = "high"
        elif total_affected > 10:
            impact["recovery_complexity"] = "medium"
        else:
            impact["recovery_complexity"] = "low"

        return impact

    def _analyze_file_imports(self, file_path: str) -> List[str]:
        """Analyze import statements in a Python file."""
        if file_path in self._import_cache:
            return list(self._import_cache[file_path])

        imports = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split(".")[0])

        except Exception:
            pass  # Skip files that can't be parsed

        # Cache the results
        self._import_cache[file_path] = set(imports)

        return imports

    def _find_reverse_dependencies(self, file_path: str) -> List[str]:
        """Find files that import the given file."""
        if file_path in self._reverse_import_cache:
            return list(self._reverse_import_cache[file_path])

        reverse_deps = []
        module_name = self._file_to_module_name(file_path)

        # Walk through all Python files
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    if full_path != file_path:  # Don't check self-imports
                        imports = self._analyze_file_imports(full_path)
                        if module_name in imports:
                            reverse_deps.append(full_path)

        # Cache the results
        self._reverse_import_cache[file_path] = set(reverse_deps)

        return reverse_deps

    def _file_to_module_name(self, file_path: str) -> str:
        """Convert file path to Python module name."""
        rel_path = os.path.relpath(file_path, self.root_path)
        if rel_path.endswith(".py"):
            rel_path = rel_path[:-3]
        return rel_path.replace(os.sep, ".")

    def _calculate_mitigation_effectiveness(self, change: OrganizationChange) -> float:
        """Calculate how effective the mitigation strategies are."""
        if not change.mitigation_strategies:
            return 0.3  # Low effectiveness with no mitigation

        # Count different types of mitigation strategies
        has_automated_testing = any(
            "test" in strategy.lower() for strategy in change.mitigation_strategies
        )
        has_backup_plan = any(
            "backup" in strategy.lower() or "rollback" in strategy.lower()
            for strategy in change.mitigation_strategies
        )
        has_validation = any(
            "valid" in strategy.lower() for strategy in change.mitigation_strategies
        )

        effectiveness = 0.5  # Base effectiveness

        if has_automated_testing:
            effectiveness += 0.2
        if has_backup_plan:
            effectiveness += 0.2
        if has_validation:
            effectiveness += 0.1

        return min(1.0, effectiveness)

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from risk score."""
        if risk_score >= 20.0:
            return RiskLevel.CRITICAL
        elif risk_score >= 10.0:
            return RiskLevel.HIGH
        elif risk_score >= 5.0:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _calculate_confidence_score(
        self,
        change: OrganizationChange,
        dependency_analysis: Dict[str, Any],
        impact_analysis: Dict[str, Any],
    ) -> float:
        """Calculate confidence score for the risk assessment."""
        confidence = 0.5  # Base confidence

        # Increase confidence based on analysis completeness
        if dependency_analysis:
            confidence += 0.2
        if impact_analysis:
            confidence += 0.2
        if change.risk_factors:
            confidence += 0.1

        # Decrease confidence for complex changes
        if len(change.affected_files) > 10:
            confidence -= 0.1
        if len(dependency_analysis.get("critical_paths", [])) > 0:
            confidence -= 0.1

        return max(0.1, min(1.0, confidence))

    def _determine_safety_rating(
        self, risk_level: RiskLevel, confidence_score: float
    ) -> str:
        """Determine safety rating based on risk level and confidence."""
        if risk_level == RiskLevel.CRITICAL:
            return "dangerous"
        elif risk_level == RiskLevel.HIGH:
            if confidence_score > 0.7:
                return "caution"
            else:
                return "dangerous"
        elif risk_level == RiskLevel.MEDIUM:
            return "caution"
        else:
            return "safe"

    def _generate_recommended_actions(
        self,
        change: OrganizationChange,
        risk_level: RiskLevel,
        dependency_analysis: Dict[str, Any],
        impact_analysis: Dict[str, Any],
    ) -> List[str]:
        """Generate recommended actions based on risk assessment."""
        actions = []

        if risk_level == RiskLevel.CRITICAL:
            actions.extend(
                [
                    "🚨 REQUIRE APPROVAL: This change requires senior developer approval",
                    "🧪 REQUIRE TESTING: Comprehensive testing required before implementation",
                    "📋 REQUIRE REVIEW: Peer code review mandatory",
                    "🔄 REQUIRE ROLLBACK: Automated rollback plan required",
                ]
            )

        elif risk_level == RiskLevel.HIGH:
            actions.extend(
                [
                    "🧪 REQUIRE TESTING: Automated testing required",
                    "📋 REQUIRE REVIEW: Code review recommended",
                    "🔄 PLAN ROLLBACK: Prepare rollback procedures",
                ]
            )

        elif risk_level == RiskLevel.MEDIUM:
            actions.extend(
                [
                    "🧪 RECOMMEND TESTING: Consider automated testing",
                    "📝 DOCUMENT CHANGE: Document the change for team knowledge",
                ]
            )

        # Add specific actions based on impact analysis
        if impact_analysis.get("affected_import_statements", 0) > 0:
            actions.append(
                f"🔧 UPDATE IMPORTS: {impact_analysis['affected_import_statements']} import statements may need updates"
            )

        if impact_analysis.get("affected_test_files", 0) > 0:
            actions.append(
                f"🧪 UPDATE TESTS: {impact_analysis['affected_test_files']} test files may need updates"
            )

        # Add dependency-specific actions
        if dependency_analysis.get("critical_paths"):
            actions.append(
                f"⚠️ CRITICAL PATHS: {len(dependency_analysis['critical_paths'])} "
                "critical files identified - extra caution required"
            )

        return actions

    def create_change_from_recommendation(
        self, recommendation: Any, change_type: str  # FileMoveRecommendation, etc.
    ) -> OrganizationChange:
        """
        Create an OrganizationChange from a recommendation.

        Args:
            recommendation: Recommendation object from structural analysis
            change_type: Type of change ('file_move', 'file_merge', etc.)

        Returns:
            OrganizationChange with risk factors
        """
        if hasattr(recommendation, "file_path"):
            # File move recommendation
            change = OrganizationChange(
                change_id=f"move_{recommendation.file_path.replace('/', '_').replace('.', '_')}",
                change_type="file_move",
                description=getattr(recommendation, "rationale", ""),
                affected_files=[recommendation.file_path],
            )

            # Add risk factors based on file type and impact
            risk_factors = self._assess_file_move_risks(recommendation)
            change.risk_factors = risk_factors

            # Add mitigation strategies
            change.mitigation_strategies = self._generate_file_move_mitigations(
                recommendation
            )

        elif hasattr(recommendation, "target_file"):
            # File merge recommendation
            change = OrganizationChange(
                change_id=f"merge_{recommendation.target_file.replace('/', '_').replace('.', '_')}",
                change_type="file_merge",
                description=getattr(recommendation, "rationale", ""),
                affected_files=[recommendation.target_file]
                + getattr(recommendation, "source_files", []),
            )

            # File merges are generally high risk
            change.risk_factors = [
                RiskFactor(
                    name="functionality_merge_risk",
                    description="Merging files may introduce functionality conflicts",
                    impact=ImpactLevel.SEVERE,
                    likelihood=LikelihoodLevel.POSSIBLE,
                    detection_difficulty=2,
                    mitigation_strength=1.5,
                )
            ]

            change.mitigation_strategies = [
                "Automated testing of merged functionality",
                "Code review by multiple developers",
                "Gradual rollout with feature flags",
            ]

        else:
            # Generic change
            change = OrganizationChange(
                change_id=f"generic_{change_type}",
                change_type=change_type,
                description="Generic organization change",
                affected_files=[],
            )

        return change

    def _assess_file_move_risks(self, recommendation: Any) -> List[RiskFactor]:
        """Assess risks for a file move recommendation."""
        risk_factors = []

        file_path = getattr(recommendation, "file_path", "")
        target_location = getattr(recommendation, "recommended_location", "")

        # Base risk depends on file type
        if file_path.endswith((".py", ".pyi")):
            # Python files are high risk due to imports
            risk_factors.append(
                RiskFactor(
                    name="import_path_risk",
                    description="Moving Python files can break import statements",
                    impact=ImpactLevel.SEVERE,
                    likelihood=LikelihoodLevel.LIKELY,
                    detection_difficulty=2,
                    mitigation_strength=1.0,
                )
            )

        elif file_path.endswith((".yml", ".yaml", ".json", ".ini", ".cfg")):
            # Config files are medium risk
            risk_factors.append(
                RiskFactor(
                    name="configuration_access_risk",
                    description="Moving config files may break application configuration",
                    impact=ImpactLevel.MODERATE,
                    likelihood=LikelihoodLevel.POSSIBLE,
                    detection_difficulty=1,
                    mitigation_strength=0.8,
                )
            )

        elif file_path.endswith(".md"):
            # Documentation files are low risk
            risk_factors.append(
                RiskFactor(
                    name="documentation_access_risk",
                    description="Moving documentation may affect discoverability",
                    impact=ImpactLevel.MINIMAL,
                    likelihood=LikelihoodLevel.UNLIKELY,
                    detection_difficulty=1,
                    mitigation_strength=0.5,
                )
            )

        return risk_factors

    def _generate_file_move_mitigations(self, recommendation: Any) -> List[str]:
        """Generate mitigation strategies for file moves."""
        mitigations = [
            "Automated import path updating",
            "Comprehensive testing before deployment",
            "Gradual rollout with monitoring",
        ]

        file_path = getattr(recommendation, "file_path", "")
        if file_path.endswith((".py", ".pyi")):
            mitigations.extend(
                [
                    "Static import analysis",
                    "Automated refactoring tools",
                    "IDE integration for path updates",
                ]
            )

        return mitigations
