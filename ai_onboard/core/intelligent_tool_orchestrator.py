"""
Intelligent Tool Orchestrator

Provides intelligent orchestration of development tools based on conversation analysis
and context, automatically applying the right tools at the right time.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .code_quality_analyzer import CodeQualityAnalyzer
from .file_organization_analyzer import FileOrganizationAnalyzer
from .risk_assessment_framework import RiskAssessmentFramework
from .structural_recommendation_engine import StructuralRecommendationEngine
from .tool_usage_tracker import get_tool_tracker


class DevelopmentTool:
    """Development tools that can be automatically applied."""

    CODE_QUALITY_ANALYSIS = "code_quality_analysis"
    ORGANIZATION_ANALYSIS = "organization_analysis"
    STRUCTURAL_RECOMMENDATIONS = "structural_recommendations"
    RISK_ASSESSMENT = "risk_assessment"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    DUPLICATE_DETECTION = "duplicate_detection"
    IMPLEMENTATION_PLANNING = "implementation_planning"


@dataclass
class ToolApplicationTrigger:
    """Triggers for automatic tool application."""

    trigger_type: str  # 'keyword', 'context', 'pattern', 'time_based'
    keywords: List[str] = field(default_factory=list)
    contexts: List[str] = field(
        default_factory=list
    )  # 'code_changes', 'refactoring', 'cleanup', 'analysis'
    patterns: List[str] = field(default_factory=list)
    priority: int = 1  # 1-5, higher = more important
    cooldown_minutes: int = 30  # Don't reapply same tool too frequently


@dataclass
class IntelligentToolOrchestrator:
    """
    Intelligent orchestrator that automatically applies development tools based on context.

    This system analyzes conversations and development activities to determine when to
    automatically apply code quality analysis, risk assessment, and other development tools.
    """

    root_path: Path
    tool_tracker: Any = field(init=False)

    # Tool application rules
    tool_triggers: Dict[str, List[ToolApplicationTrigger]] = field(default_factory=dict)

    def __post_init__(self):
        self.tool_tracker = get_tool_tracker(self.root_path)
        self._initialize_tool_triggers()

    def _initialize_tool_triggers(self):
        """Initialize intelligent triggers for automatic tool application."""

        # Code Quality Analysis triggers
        self.tool_triggers[DevelopmentTool.CODE_QUALITY_ANALYSIS] = [
            ToolApplicationTrigger(
                trigger_type="keyword",
                keywords=[
                    "cleanup",
                    "refactor",
                    "quality",
                    "dead code",
                    "unused",
                    "optimize",
                ],
                priority=3,
                cooldown_minutes=60,
            ),
            ToolApplicationTrigger(
                trigger_type="context",
                contexts=["refactoring", "cleanup"],
                priority=4,
                cooldown_minutes=30,
            ),
            ToolApplicationTrigger(
                trigger_type="pattern",
                patterns=["import.*unused", "dead.*code", "function.*never.*used"],
                priority=5,
                cooldown_minutes=15,
            ),
        ]

        # Organization Analysis triggers
        self.tool_triggers[DevelopmentTool.ORGANIZATION_ANALYSIS] = [
            ToolApplicationTrigger(
                trigger_type="keyword",
                keywords=[
                    "organize",
                    "structure",
                    "layout",
                    "reorganize",
                    "move files",
                ],
                priority=3,
                cooldown_minutes=45,
            ),
            ToolApplicationTrigger(
                trigger_type="context",
                contexts=["file_organization", "directory_structure"],
                priority=4,
                cooldown_minutes=30,
            ),
        ]

        # Risk Assessment triggers
        self.tool_triggers[DevelopmentTool.RISK_ASSESSMENT] = [
            ToolApplicationTrigger(
                trigger_type="keyword",
                keywords=["risk", "dangerous", "breaking", "impact", "safety"],
                priority=4,
                cooldown_minutes=20,
            ),
            ToolApplicationTrigger(
                trigger_type="context",
                contexts=["code_changes", "refactoring", "breaking_changes"],
                priority=5,
                cooldown_minutes=10,
            ),
        ]

        # Implementation Planning triggers
        self.tool_triggers[DevelopmentTool.IMPLEMENTATION_PLANNING] = [
            ToolApplicationTrigger(
                trigger_type="keyword",
                keywords=["implement", "plan", "phased", "rollout", "deployment"],
                priority=3,
                cooldown_minutes=60,
            ),
            ToolApplicationTrigger(
                trigger_type="context",
                contexts=["large_changes", "complex_refactoring"],
                priority=4,
                cooldown_minutes=30,
            ),
        ]

    def analyze_conversation_for_tool_application(
        self,
        conversation_history: List[Dict[str, Any]],
        current_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Analyze conversation and context to determine which tools should be automatically applied.

        Returns list of recommended tool applications with confidence scores.
        """

        recommendations = []

        # Analyze conversation content
        full_conversation = " ".join(
            [
                msg.get("content", "")
                for msg in conversation_history[-10:]  # Last 10 messages
            ]
        ).lower()

        # Check each tool's triggers
        for tool, triggers in self.tool_triggers.items():
            tool_confidence = 0
            trigger_matches = []

            for trigger in triggers:
                match_score = 0

                if trigger.trigger_type == "keyword":
                    # Check for keyword matches
                    for keyword in trigger.keywords:
                        if keyword.lower() in full_conversation:
                            match_score += 1

                elif trigger.trigger_type == "context":
                    # Check context matches
                    current_contexts = current_context.get("contexts", [])
                    for ctx in trigger.contexts:
                        if ctx in current_contexts:
                            match_score += 2

                elif trigger.trigger_type == "pattern":
                    # Check pattern matches (simple string matching for now)
                    for pattern in trigger.patterns:
                        if pattern.lower() in full_conversation:
                            match_score += 3

                if match_score > 0:
                    tool_confidence += match_score * trigger.priority
                    trigger_matches.append(
                        {
                            "trigger": trigger.trigger_type,
                            "matches": match_score,
                            "priority": trigger.priority,
                        }
                    )

            # If confidence is high enough, recommend the tool
            if tool_confidence >= 3:  # Threshold for recommendation
                recommendations.append(
                    {
                        "tool": tool,
                        "confidence": min(
                            tool_confidence / 10, 1.0
                        ),  # Normalize to 0-1
                        "triggers": trigger_matches,
                        "reasoning": f"Detected {len(trigger_matches)} trigger matches with confidence {tool_confidence/10:.1f}",
                    }
                )

        # Sort by confidence
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)

        return recommendations

    def execute_automatic_tool_application(
        self, tool_name: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an automatic tool application based on detected triggers.

        Returns execution results and status.
        """

        result = {"tool": tool_name, "executed": False, "results": None, "error": None}

        try:
            if tool_name == "code_quality_analysis":
                analyzer = CodeQualityAnalyzer(self.root_path)
                result["results"] = analyzer.analyze_codebase()
                result["executed"] = True

            elif tool_name == "organization_analysis":
                analyzer = FileOrganizationAnalyzer(self.root_path)
                result["results"] = analyzer.analyze_organization()
                result["executed"] = True

            elif tool_name == "structural_recommendations":
                # First do organization analysis
                org_analyzer = FileOrganizationAnalyzer(self.root_path)
                org_result = org_analyzer.analyze_organization()

                # Then generate recommendations
                engine = StructuralRecommendationEngine(self.root_path)
                result["results"] = engine.generate_recommendations(org_result)
                result["executed"] = True

            elif tool_name == "risk_assessment":
                # Get recommendations first
                org_analyzer = FileOrganizationAnalyzer(self.root_path)
                org_result = org_analyzer.analyze_organization()

                engine = StructuralRecommendationEngine(self.root_path)
                recommendations = engine.generate_recommendations(org_result)

                # Convert to changes for risk assessment
                framework = RiskAssessmentFramework(self.root_path)
                changes = []

                # Convert recommendations to organization changes
                for move in recommendations.file_moves:
                    change = framework.create_change_from_recommendation(
                        move, "file_move"
                    )
                    changes.append(change)

                result["results"] = framework.assess_change_risks(changes)
                result["executed"] = True

            # Track the tool usage
            if result["executed"]:
                self.tool_tracker.track_tool_usage(
                    tool_name=f"auto_applied_{tool_name}",
                    tool_type="automatic_orchestration",
                    parameters={
                        "trigger_context": context,
                        "confidence": context.get("confidence", 0),
                    },
                    result="completed",
                )

        except Exception as e:
            result["error"] = str(e)
            result["executed"] = False

        return result
