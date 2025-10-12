"""
Vision Clarity Scoring System: Evaluates the clarity and completeness of project vision.

This system provides detailed clarity scoring for:
- Problem definition clarity
- Vision statement completeness
- User/beneficiary identification
- Objective definition
- Scope boundary clarity

The clarity score is used to determine if a project vision is ready for AI agent work.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class ClarityMetric(Enum):
    """Different aspects of vision clarity to evaluate."""

    PROBLEM_DEFINITION = "problem_definition"
    VISION_STATEMENT = "vision_statement"
    USER_IDENTIFICATION = "user_identification"
    OBJECTIVE_DEFINITION = "objective_definition"
    SCOPE_BOUNDARIES = "scope_boundaries"


@dataclass
class ClarityScore:
    """Detailed clarity score for a specific metric."""

    metric: ClarityMetric
    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    issues: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class VisionClarityReport:
    """Complete clarity assessment report."""

    overall_score: float  # 0.0 to 1.0
    is_ready_for_ai: bool  # True if score >= 0.8
    detailed_scores: Dict[ClarityMetric, ClarityScore] = field(default_factory=dict)
    critical_issues: List[str] = field(default_factory=list)
    summary: str = ""


class VisionClarityScorer:
    """Advanced vision clarity scoring system."""

    def __init__(self):
        # Quality indicators for each metric
        self.problem_indicators = [
            r"problem",
            r"issue",
            r"challenge",
            r"difficulty",
            r"pain",
            r"frustration",
            r"inefficiency",
            r"bottleneck",
            r"obstacle",
        ]

        self.vision_indicators = [
            r"vision",
            r"goal",
            r"objective",
            r"aim",
            r"purpose",
            r"mission",
            r"target",
            r"outcome",
            r"result",
            r"achievement",
        ]

        self.user_indicators = [
            r"user",
            r"customer",
            r"client",
            r"stakeholder",
            r"beneficiary",
            r"audience",
            r"recipient",
            r"consumer",
            r"end-user",
            r"person",
        ]

        self.objective_indicators = [
            r"objective",
            r"goal",
            r"target",
            r"metric",
            r"measure",
            r"success",
            r"criteria",
            r"outcome",
            r"deliverable",
            r"result",
        ]

        self.scope_indicators = [
            r"scope",
            r"boundary",
            r"limit",
            r"constraint",
            r"include",
            r"exclude",
            r"focus",
            r"range",
            r"extent",
            r"coverage",
        ]

    def evaluate_problem_definition(self, responses: Dict[str, Any]) -> ClarityScore:
        """Evaluate clarity of problem definition."""
        score = 0.0
        confidence = 0.0
        issues: List[str] = []
        strengths: List[str] = []
        recommendations: List[str] = []

        # Get relevant responses
        core_problem = responses.get("vc_01", "").lower()
        vision_statement = responses.get("vc_02", "").lower()

        if not core_problem.strip():
            issues.append("No core problem statement provided")
            return ClarityScore(
                ClarityMetric.PROBLEM_DEFINITION,
                0.0,
                0.0,
                issues,
                strengths,
                recommendations,
            )

        # Check for problem indicators
        problem_matches = sum(
            1 for indicator in self.problem_indicators if indicator in core_problem
        )

        # Check for specific problem details
        specific_indicators = [
            "what",
            "who",
            "when",
            "where",
            "why",
            "how",
            "specific",
            "particular",
            "exact",
            "precise",
        ]

        specific_matches = sum(
            1 for indicator in specific_indicators if indicator in core_problem
        )

        # Calculate score based on indicators
        if problem_matches >= 2:
            score += 0.4
            strengths.append("Clear problem indicators identified")
        elif problem_matches >= 1:
            score += 0.2
            issues.append("Limited problem indicators found")
        else:
            issues.append("No clear problem indicators")

        if specific_matches >= 2:
            score += 0.3
            strengths.append("Specific problem details provided")
        elif specific_matches >= 1:
            score += 0.15
        else:
            issues.append("Problem description lacks specificity")

        # Check for quantification
        if any(char.isdigit() for char in core_problem):
            score += 0.1
            strengths.append("Quantitative problem details included")
        else:
            recommendations.append(
                "Consider adding quantitative details to problem statement"
            )

        # Check length and detail
        if len(core_problem) >= 50:
            score += 0.2
            strengths.append("Detailed problem description provided")
        elif len(core_problem) >= 20:
            score += 0.1
        else:
            issues.append("Problem description too brief")
            recommendations.append("Provide more detailed problem description")

        confidence = min(score, 1.0)

        return ClarityScore(
            ClarityMetric.PROBLEM_DEFINITION,
            score,
            confidence,
            issues,
            strengths,
            recommendations,
        )

    def evaluate_vision_statement(self, responses: Dict[str, Any]) -> ClarityScore:
        """Evaluate clarity of vision statement."""
        score = 0.0
        confidence = 0.0
        issues: List[str] = []
        strengths: List[str] = []
        recommendations: List[str] = []

        # Get relevant responses
        vision_statement = responses.get("vc_02", "").lower()

        if not vision_statement.strip():
            issues.append("No vision statement provided")
            return ClarityScore(
                ClarityMetric.VISION_STATEMENT,
                0.0,
                0.0,
                issues,
                strengths,
                recommendations,
            )

        # Check for vision indicators
        vision_matches = sum(
            1 for indicator in self.vision_indicators if indicator in vision_statement
        )

        # Check for action-oriented language
        action_indicators = [
            "will",
            "can",
            "able",
            "provide",
            "deliver",
            "create",
            "build",
            "develop",
            "achieve",
            "enable",
            "allow",
        ]

        action_matches = sum(
            1 for indicator in action_indicators if indicator in vision_statement
        )

        # Check for measurable outcomes
        measurable_indicators = [
            "better",
            "faster",
            "easier",
            "more",
            "less",
            "reduce",
            "increase",
            "improve",
            "enhance",
            "optimize",
            "streamline",
        ]

        measurable_matches = sum(
            1 for indicator in measurable_indicators if indicator in vision_statement
        )

        # Calculate score
        if vision_matches >= 2:
            score += 0.3
            strengths.append("Clear vision indicators present")
        elif vision_matches >= 1:
            score += 0.15
        else:
            issues.append("Vision statement lacks clear vision indicators")

        if action_matches >= 2:
            score += 0.25
            strengths.append("Action-oriented vision statement")
        elif action_matches >= 1:
            score += 0.12
        else:
            issues.append("Vision statement lacks action-oriented language")

        if measurable_matches >= 2:
            score += 0.25
            strengths.append("Measurable outcomes specified")
        elif measurable_matches >= 1:
            score += 0.12
        else:
            recommendations.append(
                "Consider adding measurable outcomes to vision statement"
            )

        # Check length and specificity
        if len(vision_statement) >= 100:
            score += 0.2
            strengths.append("Comprehensive vision statement")
        elif len(vision_statement) >= 50:
            score += 0.1
        else:
            issues.append("Vision statement too brief")
            recommendations.append("Provide more detailed vision statement")

        confidence = min(score, 1.0)

        return ClarityScore(
            ClarityMetric.VISION_STATEMENT,
            score,
            confidence,
            issues,
            strengths,
            recommendations,
        )

    def evaluate_user_identification(self, responses: Dict[str, Any]) -> ClarityScore:
        """Evaluate clarity of user/beneficiary identification."""
        score = 0.0
        confidence = 0.0
        issues: List[str] = []
        strengths: List[str] = []
        recommendations: List[str] = []

        # Get relevant responses
        user_statement = responses.get("vc_03", "").lower()

        if not user_statement.strip():
            issues.append("No user identification provided")
            return ClarityScore(
                ClarityMetric.USER_IDENTIFICATION,
                0.0,
                0.0,
                issues,
                strengths,
                recommendations,
            )

        # Check for user indicators
        user_matches = sum(
            1 for indicator in self.user_indicators if indicator in user_statement
        )

        # Check for specific user characteristics
        characteristic_indicators = [
            "developer",
            "manager",
            "student",
            "business",
            "technical",
            "non-technical",
            "beginner",
            "expert",
            "enterprise",
            "startup",
        ]

        characteristic_matches = sum(
            1 for indicator in characteristic_indicators if indicator in user_statement
        )

        # Check for user needs/goals
        need_indicators = [
            "need",
            "want",
            "require",
            "expect",
            "desire",
            "goal",
            "objective",
            "benefit",
            "advantage",
            "value",
        ]

        need_matches = sum(
            1 for indicator in need_indicators if indicator in user_statement
        )

        # Calculate score
        if user_matches >= 2:
            score += 0.3
            strengths.append("Clear user indicators present")
        elif user_matches >= 1:
            score += 0.15
        else:
            issues.append("User identification lacks clear user indicators")

        if characteristic_matches >= 2:
            score += 0.25
            strengths.append("Specific user characteristics identified")
        elif characteristic_matches >= 1:
            score += 0.12
        else:
            recommendations.append("Consider specifying user characteristics and roles")

        if need_matches >= 2:
            score += 0.25
            strengths.append("User needs and goals clearly stated")
        elif need_matches >= 1:
            score += 0.12
        else:
            issues.append("User needs and goals not clearly defined")

        # Check for multiple user types
        if "," in user_statement or "and" in user_statement:
            score += 0.2
            strengths.append("Multiple user types identified")
        else:
            recommendations.append("Consider if multiple user types exist")

        confidence = min(score, 1.0)

        return ClarityScore(
            ClarityMetric.USER_IDENTIFICATION,
            score,
            confidence,
            issues,
            strengths,
            recommendations,
        )

    def evaluate_objective_definition(self, responses: Dict[str, Any]) -> ClarityScore:
        """Evaluate clarity of objective definition."""
        score = 0.0
        confidence = 0.0
        issues: List[str] = []
        strengths: List[str] = []
        recommendations: List[str] = []

        # Get relevant responses from success criteria phase
        success_criteria = responses.get("sc_01", "").lower()

        if not success_criteria.strip():
            issues.append("No success criteria defined")
            return ClarityScore(
                ClarityMetric.OBJECTIVE_DEFINITION,
                0.0,
                0.0,
                issues,
                strengths,
                recommendations,
            )

        # Check for objective indicators
        objective_matches = sum(
            1
            for indicator in self.objective_indicators
            if indicator in success_criteria
        )

        # Check for measurable elements
        measurable_indicators = [
            "measure",
            "metric",
            "count",
            "percentage",
            "time",
            "number",
            "quantity",
            "rate",
            "speed",
            "accuracy",
        ]

        measurable_matches = sum(
            1 for indicator in measurable_indicators if indicator in success_criteria
        )

        # Check for specific targets
        target_indicators = [
            "target",
            "goal",
            "aim",
            "objective",
            "standard",
            "benchmark",
            "threshold",
            "requirement",
        ]

        target_matches = sum(
            1 for indicator in target_indicators if indicator in success_criteria
        )

        # Calculate score
        if objective_matches >= 2:
            score += 0.25
            strengths.append("Clear objective indicators present")
        elif objective_matches >= 1:
            score += 0.12
        else:
            issues.append("Success criteria lack clear objective indicators")

        if measurable_matches >= 2:
            score += 0.3
            strengths.append("Measurable success criteria defined")
        elif measurable_matches >= 1:
            score += 0.15
        else:
            issues.append("Success criteria not measurable")
            recommendations.append("Define measurable success criteria")

        if target_matches >= 1:
            score += 0.2
            strengths.append("Specific targets identified")
        else:
            recommendations.append("Specify clear targets for success criteria")

        # Check for time-based criteria
        time_indicators = ["time", "deadline", "schedule", "timeline", "duration"]
        time_matches = sum(
            1 for indicator in time_indicators if indicator in success_criteria
        )

        if time_matches >= 1:
            score += 0.15
            strengths.append("Time-based criteria included")
        else:
            recommendations.append("Consider adding time-based success criteria")

        # Check for quality criteria
        quality_indicators = ["quality", "standard", "requirement", "specification"]
        quality_matches = sum(
            1 for indicator in quality_indicators if indicator in success_criteria
        )

        if quality_matches >= 1:
            score += 0.1
            strengths.append("Quality criteria defined")
        else:
            recommendations.append("Consider adding quality standards")

        confidence = min(score, 1.0)

        return ClarityScore(
            ClarityMetric.OBJECTIVE_DEFINITION,
            score,
            confidence,
            issues,
            strengths,
            recommendations,
        )

    def evaluate_scope_boundaries(self, responses: Dict[str, Any]) -> ClarityScore:
        """Evaluate clarity of scope boundaries."""
        score = 0.0
        confidence = 0.0
        issues: List[str] = []
        strengths: List[str] = []
        recommendations: List[str] = []

        # Get relevant responses from scope phase
        in_scope = responses.get("sb_01", "").lower()
        out_of_scope = responses.get("sb_02", "").lower()

        if not in_scope.strip() and not out_of_scope.strip():
            issues.append("No scope boundaries defined")
            return ClarityScore(
                ClarityMetric.SCOPE_BOUNDARIES,
                0.0,
                0.0,
                issues,
                strengths,
                recommendations,
            )

        # Check for scope indicators
        scope_matches = sum(
            1
            for indicator in self.scope_indicators
            if indicator in in_scope or indicator in out_of_scope
        )

        # Check for specific inclusions
        inclusion_indicators = [
            "include",
            "feature",
            "functionality",
            "capability",
            "component",
            "module",
            "service",
            "integration",
            "support",
        ]

        inclusion_matches = sum(
            1 for indicator in inclusion_indicators if indicator in in_scope
        )

        # Check for specific exclusions
        exclusion_indicators = [
            "exclude",
            "not include",
            "out of scope",
            "not part of",
            "separate",
            "future",
            "phase 2",
            "later",
        ]

        exclusion_matches = sum(
            1 for indicator in exclusion_indicators if indicator in out_of_scope
        )

        # Calculate score
        if scope_matches >= 2:
            score += 0.2
            strengths.append("Clear scope indicators present")
        elif scope_matches >= 1:
            score += 0.1
        else:
            issues.append("Scope boundaries lack clear scope indicators")

        if inclusion_matches >= 2:
            score += 0.3
            strengths.append("Specific inclusions clearly defined")
        elif inclusion_matches >= 1:
            score += 0.15
        else:
            issues.append("In-scope items not clearly defined")

        if exclusion_matches >= 2:
            score += 0.3
            strengths.append("Clear exclusions specified")
        elif exclusion_matches >= 1:
            score += 0.15
        else:
            recommendations.append("Consider explicitly stating what's out of scope")

        # Check for rationale
        if "because" in in_scope or "because" in out_of_scope:
            score += 0.1
            strengths.append("Scope rationale provided")
        else:
            recommendations.append("Consider explaining rationale for scope decisions")

        # Check for priority/phase information
        phase_indicators = ["priority", "phase", "version", "release", "mvp"]
        phase_matches = sum(
            1
            for indicator in phase_indicators
            if indicator in in_scope or indicator in out_of_scope
        )

        if phase_matches >= 1:
            score += 0.1
            strengths.append("Scope prioritization indicated")
        else:
            recommendations.append(
                "Consider indicating priorities or phases for scope items"
            )

        confidence = min(score, 1.0)

        return ClarityScore(
            ClarityMetric.SCOPE_BOUNDARIES,
            score,
            confidence,
            issues,
            strengths,
            recommendations,
        )

    def score_vision_clarity(self, responses: Dict[str, Any]) -> VisionClarityReport:
        """Score overall vision clarity across all metrics."""

        # Evaluate each clarity metric
        problem_score = self.evaluate_problem_definition(responses)
        vision_score = self.evaluate_vision_statement(responses)
        user_score = self.evaluate_user_identification(responses)
        objective_score = self.evaluate_objective_definition(responses)
        scope_score = self.evaluate_scope_boundaries(responses)

        # Calculate overall score (weighted average)
        scores = [problem_score, vision_score, user_score, objective_score, scope_score]
        overall_score = sum(score.score for score in scores) / len(scores)

        # Collect all detailed scores
        detailed_scores = {
            ClarityMetric.PROBLEM_DEFINITION: problem_score,
            ClarityMetric.VISION_STATEMENT: vision_score,
            ClarityMetric.USER_IDENTIFICATION: user_score,
            ClarityMetric.OBJECTIVE_DEFINITION: objective_score,
            ClarityMetric.SCOPE_BOUNDARIES: scope_score,
        }

        # Collect critical issues (score < 0.6 for any metric)
        critical_issues = []
        for score in scores:
            if score.score < 0.6:
                critical_issues.extend(score.issues)

        # Determine readiness for AI work
        is_ready_for_ai = (
            overall_score >= 0.8
            and all(score.score >= 0.6 for score in scores)
            and len(critical_issues) == 0
        )

        # Generate summary
        if is_ready_for_ai:
            summary = f"Vision clarity score: {overall_score:.2f} - Ready for AI work"
        elif overall_score >= 0.6:
            summary = f"Vision clarity score: {overall_score:.2f} - Nearly ready, minor issues to address"
        else:
            summary = f"Vision clarity score: {overall_score:.2f} - Significant clarity issues need resolution"

        return VisionClarityReport(
            overall_score=overall_score,
            is_ready_for_ai=is_ready_for_ai,
            detailed_scores=detailed_scores,
            critical_issues=critical_issues,
            summary=summary,
        )


def score_vision_clarity(responses: Dict[str, Any]) -> VisionClarityReport:
    """Convenience function to score vision clarity."""
    scorer = VisionClarityScorer()
    return scorer.score_vision_clarity(responses)
