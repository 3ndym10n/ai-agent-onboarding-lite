"""
Mandatory Tool Consultation Gate

Enforces that every AI interaction must first consult available ai_onboard tools
before proceeding. This implements the "Prime Directive" for tool-first development.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..monitoring_analytics.file_organization_analyzer import FileOrganizationAnalyzer
from ..quality_safety.code_quality_analyzer import CodeQualityAnalyzer
from ..quality_safety.dependency_mapper import DependencyMapper
from ..quality_safety.duplicate_detector import DuplicateDetector
from ..quality_safety.risk_assessment_framework import RiskAssessmentFramework
from ..quality_safety.structural_recommendation_engine import (
    StructuralRecommendationEngine,
)
from .comprehensive_tool_discovery import ToolCategory, get_comprehensive_tool_discovery
from .orchestration_compatibility import HolisticToolOrchestrator, OrchestrationStrategy
from .tool_usage_tracker import get_tool_tracker
from .unified_tool_orchestrator import UnifiedToolOrchestrator


class ToolRelevanceLevel(Enum):
    """Tool relevance levels for user requests."""

    CRITICAL = "critical"  # Must use this tool
    HIGH = "high"  # Should use this tool
    MEDIUM = "medium"  # Could use this tool
    LOW = "low"  # Tool available but not needed
    NONE = "none"  # Tool not relevant


@dataclass
class AvailableTool:
    """Represents an available ai_onboard tool."""

    name: str
    description: str
    tool_class: Any
    keywords: List[str] = field(default_factory=list)
    contexts: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    execution_capability: str = (
        "unknown"  # "executable", "cli_function", "analysis_tool", "utility"
    )
    requires_parameters: bool = False
    can_auto_apply: bool = True


@dataclass
class ToolConsultationResult:
    """Result of mandatory tool consultation."""

    user_request: str
    relevant_tools: Dict[str, ToolRelevanceLevel]
    recommended_tools: List[str]
    tool_analysis: Dict[str, Any]
    consultation_time: float
    gate_passed: bool
    blocking_reason: Optional[str] = None


class MandatoryToolConsultationGate:
    """
    Enforces mandatory tool consultation before any AI interaction.

    This gate ensures that every user request is analyzed for tool relevance
    and appropriate tools are consulted before generating any AI response.
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.tool_tracker = get_tool_tracker(root_path)
        self.tool_orchestrator = UnifiedToolOrchestrator(root_path)
        self.holistic_orchestrator = HolisticToolOrchestrator(root_path)

        # Initialize available tools registry
        self.available_tools = self._initialize_available_tools()

        # Gate configuration
        self.gate_config = {
            "require_critical_tools": True,
            "require_high_relevance_tools": False,
            # Allow passage without high-relevance tools
            "allow_bypass": False,
            "minimum_consultation_time": 0.01,  # seconds (very fast for better UX)
            "max_tools_per_request": 5,
        }

        # Statistics
        self.consultation_stats = {
            "total_consultations": 0,
            "tools_applied": 0,
            "gate_blocks": 0,
            "bypasses": 0,
        }

    def _initialize_available_tools(self) -> Dict[str, AvailableTool]:
        """Initialize registry of available ai_onboard tools using comprehensive discovery."""

        # Use comprehensive tool discovery to find ALL available tools
        tool_discovery = get_comprehensive_tool_discovery(self.root_path)
        discovery_result = tool_discovery.discover_all_tools()

        from ..utilities.unicode_utils import ensure_unicode_safe

        ensure_unicode_safe(f"🔍 DISCOVERED {len(discovery_result.all_tools)} TOOLS:")
        for category, category_tools in discovery_result.tools_by_category.items():
            ensure_unicode_safe(f"   📂 {category.value}: {len(category_tools)} tools")

        # Convert discovered tools to AvailableTool format
        tools: Dict[str, AvailableTool] = {}

        # Automatically convert discovered tools to AvailableTool objects
        for tool_name, tool_metadata in discovery_result.all_tools.items():
            # Determine execution capability based on tool category and name
            execution_capability = self._determine_execution_capability(tool_metadata)

            # Create AvailableTool from discovered metadata
            available_tool = AvailableTool(
                name=tool_name,
                description=tool_metadata.description or f"{tool_name} tool",
                tool_class=None,  # Will be resolved dynamically during execution
                keywords=tool_metadata.keywords,
                contexts=tool_metadata.contexts,
                patterns=tool_metadata.patterns,
                execution_capability=execution_capability,
                requires_parameters=False,  # Assume no parameters needed for auto-application
                can_auto_apply=self._can_tool_auto_apply(tool_metadata),
            )
            tools[tool_name] = available_tool

        # Add any manually defined core tools that may not be discovered
        core_tools = {
            "code_quality_analysis": AvailableTool(
                name="code_quality_analysis",
                description="Analyze code quality, detect unused imports, dead code, complexity",
                tool_class=CodeQualityAnalyzer,
                keywords=[
                    "quality",
                    "cleanup",
                    "refactor",
                    "unused",
                    "dead code",
                    "complexity",
                    "imports",
                    "analyze",
                    "code",
                    "issues",
                    "problems",
                    "fix",
                    "improve",
                ],
                contexts=[
                    "code_review",
                    "refactoring",
                    "cleanup",
                    "optimization",
                    "analysis",
                ],
                patterns=[
                    "import.*unused",
                    "dead.*code",
                    "function.*never.*used",
                    "quality.*issues",
                    "code.*quality",
                    "unused.*imports",
                    "complexity.*analysis",
                ],
                execution_capability="analysis_tool",
                requires_parameters=False,
                can_auto_apply=True,
            ),
            "organization_analysis": AvailableTool(
                name="organization_analysis",
                description="Analyze file organization, directory structure, placement issues",
                tool_class=FileOrganizationAnalyzer,
                keywords=[
                    "organize",
                    "structure",
                    "layout",
                    "directory",
                    "files",
                    "placement",
                    "file.*organization",
                    "directory.*structure",
                    "move.*files",
                ],
                contexts=[
                    "organization",
                    "structure",
                    "file_management",
                    "directory_layout",
                ],
                patterns=[
                    "file.*organization",
                    "directory.*structure",
                    "move.*files",
                    "organize.*files",
                ],
                execution_capability="analysis_tool",
                requires_parameters=False,
                can_auto_apply=True,
            ),
            "structural_recommendations": AvailableTool(
                name="structural_recommendations",
                description="Generate recommendations for file moves, merges, restructuring",
                tool_class=StructuralRecommendationEngine,
                keywords=[
                    "recommend",
                    "suggestions",
                    "restructure",
                    "move",
                    "merge",
                    "improve",
                ],
                contexts=["restructuring", "recommendations", "improvements"],
                patterns=[
                    "recommend.*changes",
                    "suggest.*improvements",
                    "restructur.*plan",
                ],
                execution_capability="analysis_tool",
                requires_parameters=False,
                can_auto_apply=True,
            ),
            "risk_assessment": AvailableTool(
                name="risk_assessment",
                description="Assess risks of code changes, breaking changes, impact analysis",
                tool_class=RiskAssessmentFramework,
                keywords=[
                    "risk",
                    "danger",
                    "breaking",
                    "impact",
                    "safety",
                    "assessment",
                    "safe",
                    "unsafe",
                    "dangerous",
                    "critical",
                    "evaluate",
                ],
                contexts=["risk_analysis", "safety_check", "impact_assessment"],
                patterns=[
                    "risk.*assessment",
                    "breaking.*changes",
                    "impact.*analysis",
                    "assess.*risk",
                ],
                execution_capability="analysis_tool",
                requires_parameters=False,
                can_auto_apply=True,
            ),
            "dependency_analysis": AvailableTool(
                name="dependency_analysis",
                description="Analyze module dependencies, circular dependencies, coupling",
                tool_class=DependencyMapper,
                keywords=[
                    "dependencies",
                    "imports",
                    "modules",
                    "circular",
                    "coupling",
                    "analyze",
                ],
                contexts=["dependency_analysis", "module_analysis", "architecture"],
                patterns=[
                    "circular.*dependencies",
                    "module.*dependencies",
                    "import.*analysis",
                ],
                execution_capability="analysis_tool",
                requires_parameters=False,
                can_auto_apply=True,
            ),
            "duplicate_detection": AvailableTool(
                name="duplicate_detection",
                description="Detect duplicate code blocks, similar functions, redundant code",
                tool_class=DuplicateDetector,
                keywords=[
                    "duplicate",
                    "redundant",
                    "similar",
                    "repeated",
                    "copy",
                    "detect",
                ],
                contexts=["duplicate_detection", "code_deduplication", "refactoring"],
                patterns=["duplicate.*code", "similar.*functions", "repeated.*logic"],
                execution_capability="analysis_tool",
                requires_parameters=False,
                can_auto_apply=True,
            ),
            # Additional Code Quality Tools
            # Removed: codebase_analysis (redundant with code_quality)
            # "codebase_analysis": AvailableTool(
            #     name="codebase_analysis",
            #     description="Comprehensive codebase analysis including file relationships, "
            #     "organization, and quality metrics",
            #     tool_class=None,  # Will be imported dynamically
            #     keywords=[
            #         "codebase",
            #         "analysis",
            #         "structure",
            #         "architecture",
            #         "overview",
            #         "comprehensive",
            #         "relationships",
            #     ],
            #     contexts=["analysis", "code_review", "architecture_review"],
            #     patterns=[
            #         "codebase.*analysis",
            #         "comprehensive.*review",
            #         "architecture.*overview",
            #     ],
            #     execution_capability="analysis_tool",
            #     requires_parameters=False,
            #     can_auto_apply=True,
            # ),
            "syntax_validator": AvailableTool(
                name="syntax_validator",
                description="Validate Python syntax across all files, detect syntax errors and import issues",
                tool_class=None,  # Will be imported dynamically
                keywords=[
                    "syntax",
                    "validate",
                    "check",
                    "errors",
                    "lint",
                    "python",
                    "valid",
                ],
                contexts=["syntax_check", "validation", "error_detection"],
                patterns=["syntax.*error", "import.*error", "validation.*failed"],
                execution_capability="analysis_tool",
                requires_parameters=False,
                can_auto_apply=True,
            ),
            "dependency_checker": AvailableTool(
                name="dependency_checker",
                description="Check dependencies before cleanup operations, ensure safe file removal",
                tool_class=None,  # Will be imported dynamically
                keywords=[
                    "dependencies",
                    "safe",
                    "removal",
                    "cleanup",
                    "delete",
                    "references",
                ],
                contexts=["cleanup", "refactoring", "file_operations"],
                patterns=["safe.*removal", "dependency.*check", "references.*found"],
                execution_capability="analysis_tool",
                requires_parameters=True,  # Needs target files
                can_auto_apply=False,  # Requires user confirmation
            ),
            # Project Management Tools
            "approval_workflow": AvailableTool(
                name="approval_workflow",
                description="Manage approval workflows for code changes and \
                    system modifications",
                tool_class=None,  # Will be imported dynamically
                keywords=[
                    "approve",
                    "approval",
                    "review",
                    "permission",
                    "authorize",
                    "workflow",
                ],
                contexts=["code_changes", "system_changes", "governance"],
                patterns=[
                    "approval.*required",
                    "review.*needed",
                    "authorization.*pending",
                ],
                execution_capability="cli_function",
                requires_parameters=False,
                can_auto_apply=False,  # Requires user interaction
            ),
            "critical_path_engine": AvailableTool(
                name="critical_path_engine",
                description="Analyze project critical paths, dependencies, and timeline optimization",
                tool_class=None,  # Will be imported dynamically
                keywords=[
                    "critical",
                    "path",
                    "timeline",
                    "schedule",
                    "dependencies",
                    "bottleneck",
                ],
                contexts=["project_planning", "deadline", "milestones"],
                patterns=["critical.*path", "timeline.*analysis", "dependency.*chain"],
                execution_capability="analysis_tool",
                requires_parameters=False,
                can_auto_apply=True,
            ),
            "progress_dashboard": AvailableTool(
                name="progress_dashboard",
                description="Project progress dashboard and status reporting",
                tool_class=None,  # Will be imported dynamically
                keywords=[
                    "progress",
                    "status",
                    "dashboard",
                    "report",
                    "summary",
                    "metrics",
                ],
                contexts=["monitoring", "reporting", "status_tracking"],
                patterns=["progress.*report", "status.*dashboard", "project.*metrics"],
                execution_capability="analysis_tool",
                requires_parameters=False,
                can_auto_apply=True,
            ),
            "task_completion_detector": AvailableTool(
                name="task_completion_detector",
                description="Automatically detect completed tasks and \
                    update project status",
                tool_class=None,  # Will be imported dynamically
                keywords=[
                    "complete",
                    "finished",
                    "done",
                    "task",
                    "completion",
                    "achieved",
                ],
                contexts=["task_management", "progress_tracking", "status_updates"],
                patterns=["task.*completed", "milestone.*achieved", "goal.*reached"],
                execution_capability="analysis_tool",
                requires_parameters=False,
                can_auto_apply=True,
            ),
            "task_prioritization_engine": AvailableTool(
                name="task_prioritization_engine",
                description="Automatically prioritize tasks based on urgency, impact, and dependencies",
                tool_class=None,  # Will be imported dynamically
                keywords=[
                    "priority",
                    "important",
                    "urgent",
                    "prioritize",
                    "ranking",
                ],
                contexts=["task_management", "planning", "resource_allocation"],
                patterns=["high.*priority", "urgent.*task", "critical.*item"],
                execution_capability="analysis_tool",
                requires_parameters=False,
                can_auto_apply=True,
            ),
            "wbs_management": AvailableTool(
                name="wbs_management",
                description="Work Breakdown Structure management and synchronization",
                tool_class=None,  # Will be imported dynamically
                keywords=[
                    "wbs",
                    "work",
                    "breakdown",
                    "structure",
                    "hierarchy",
                    "decomposition",
                ],
                contexts=["project_management", "planning", "organization"],
                patterns=["work.*breakdown", "wbs.*structure", "task.*hierarchy"],
                execution_capability="analysis_tool",
                requires_parameters=False,
                can_auto_apply=True,
            ),
        }

        # Add core tools
        tools.update(core_tools)

        # Add discovered tools from relevant categories
        relevant_categories = [
            ToolCategory.CODE_QUALITY,
            ToolCategory.FILE_ORGANIZATION,
            ToolCategory.DEPENDENCY_ANALYSIS,
            ToolCategory.DUPLICATE_DETECTION,
            ToolCategory.SAFETY_CHECKS,
            ToolCategory.ERROR_PREVENTION,
            ToolCategory.GATE_SYSTEM,
            ToolCategory.CLEANUP_SAFETY,
            ToolCategory.AI_AGENT_ORCHESTRATION,
            ToolCategory.DECISION_PIPELINE,
            ToolCategory.INTELLIGENT_MONITORING,
        ]

        for tool_name, tool_metadata in discovery_result.all_tools.items():
            if tool_metadata.category in relevant_categories:
                # Determine execution capability based on tool name and category
                execution_capability = "unknown"
                can_auto_apply = False

                # CLI command functions are not auto-executable
                if tool_name.startswith("cli_"):
                    execution_capability = "cli_function"
                    can_auto_apply = False
                # Analysis tools can be auto-applied
                elif tool_metadata.category in [
                    ToolCategory.CODE_QUALITY,
                    ToolCategory.FILE_ORGANIZATION,
                    ToolCategory.DEPENDENCY_ANALYSIS,
                    ToolCategory.DUPLICATE_DETECTION,
                ]:
                    execution_capability = "analysis_tool"
                    can_auto_apply = True
                # Safety and validation tools can be auto-applied
                elif tool_metadata.category in [
                    ToolCategory.SAFETY_CHECKS,
                    ToolCategory.ERROR_PREVENTION,
                ]:
                    execution_capability = "safety_tool"
                    can_auto_apply = True
                # Other tools are utilities
                else:
                    execution_capability = "utility"
                    can_auto_apply = False

                # Convert tool metadata to AvailableTool
                available_tool = AvailableTool(
                    name=tool_metadata.name,
                    description=tool_metadata.description,
                    tool_class=None,  # Most discovered tools don't have classes
                    keywords=tool_metadata.keywords or [],
                    contexts=tool_metadata.contexts or [],
                    patterns=tool_metadata.patterns or [],
                    execution_capability=execution_capability,
                    requires_parameters=False,
                    can_auto_apply=can_auto_apply,
                )
                tools[tool_metadata.name] = available_tool

        # Display tool categorization summary
        auto_applicable = sum(1 for tool in tools.values() if tool.can_auto_apply)
        cli_functions = sum(
            1 for tool in tools.values() if tool.execution_capability == "cli_function"
        )
        analysis_tools = sum(
            1 for tool in tools.values() if tool.execution_capability == "analysis_tool"
        )

        from ..utilities.unicode_utils import ensure_unicode_safe

        ensure_unicode_safe(f"✅ REGISTERED {len(tools)} TOOLS FOR CONSULTATION")
        ensure_unicode_safe(f"   🔧 Auto-applicable: {auto_applicable}")
        ensure_unicode_safe(f"   📋 CLI functions: {cli_functions}")
        ensure_unicode_safe(f"   🔍 Analysis tools: {analysis_tools}")

        return tools

    def _determine_execution_capability(self, tool_metadata) -> str:
        """Determine execution capability based on tool metadata."""
        tool_name = tool_metadata.name.lower()
        category = (
            tool_metadata.category.value.lower() if tool_metadata.category else ""
        )

        # CLI functions
        if tool_name.startswith("cli_"):
            return "cli_function"

        # Analysis tools
        if any(
            keyword in category
            for keyword in [
                "quality",
                "organization",
                "analysis",
                "detection",
                "assessment",
            ]
        ):
            return "analysis_tool"

        # Executable tools
        if any(
            keyword in tool_name
            for keyword in ["orchestrator", "engine", "analyzer", "detector", "mapper"]
        ):
            return "executable"

        # Utility tools
        return "utility"

    def _can_tool_auto_apply(self, tool_metadata) -> bool:
        """Determine if a tool can be auto-applied based on its metadata."""
        tool_name = tool_metadata.name.lower()
        category = (
            tool_metadata.category.value.lower() if tool_metadata.category else ""
        )

        # Always allow core analysis tools
        if any(
            keyword in category
            for keyword in [
                "code_quality",
                "file_organization",
                "dependency_analysis",
                "duplicate_detection",
            ]
        ):
            return True

        # Allow safety and vision tools
        if any(
            keyword in category
            for keyword in [
                "safety_checks",
                "vision_alignment",
                "gate_system",
                "error_prevention",
            ]
        ):
            return True

        # CLI functions generally should not auto-apply (too many)
        if tool_name.startswith("cli_"):
            return False

        # Be conservative with unknown tools
        return (
            tool_metadata.risk_level in ["low", "medium"]
            if tool_metadata.risk_level
            else False
        )

    def consult_tools_for_request(
        self, user_request: str, context: Optional[Dict[str, Any]] = None
    ) -> ToolConsultationResult:
        """
        Mandatory consultation of tools for user request.

        This is the core gate function that MUST be called before any AI response.
        """

        start_time = time.time()

        if context is None:
            context = {}

        from ..utilities.unicode_utils import ensure_unicode_safe

        ensure_unicode_safe("🔍 MANDATORY TOOL CONSULTATION")
        print("=" * 50)
        from ..utilities.unicode_utils import ensure_unicode_safe

        ensure_unicode_safe(
            f"📝 Request: {user_request[:100]}{'...' if len(user_request) > 100 else ''}"
        )

        # Track the consultation
        self.tool_tracker.track_tool_usage(
            tool_name="mandatory_tool_consultation",
            tool_type="gate_system",
            parameters={
                "request_length": len(user_request),
                "context_keys": list(context.keys()),
            },
            result="started",
        )

        # Analyze tool relevance
        relevant_tools = self._analyze_tool_relevance(user_request, context)

        # Determine recommended tools
        recommended_tools = self._get_recommended_tools(relevant_tools)

        # Apply recommended tools
        tool_analysis = self._apply_recommended_tools(
            recommended_tools, user_request, context
        )

        consultation_time = time.time() - start_time

        # Check if gate passes
        gate_passed, blocking_reason = self._evaluate_gate_passage(
            relevant_tools, recommended_tools, tool_analysis, consultation_time
        )

        result = ToolConsultationResult(
            user_request=user_request,
            relevant_tools=relevant_tools,
            recommended_tools=recommended_tools,
            tool_analysis=tool_analysis,
            consultation_time=consultation_time,
            gate_passed=gate_passed,
            blocking_reason=blocking_reason,
        )

        # Update statistics
        self.consultation_stats["total_consultations"] += 1
        self.consultation_stats["tools_applied"] += len(
            [t for t in tool_analysis.values() if t.get("executed")]
        )
        if not gate_passed:
            self.consultation_stats["gate_blocks"] += 1

        # Display consultation results
        self._display_consultation_results(result)

        # Track completion
        self.tool_tracker.track_tool_usage(
            tool_name="mandatory_tool_consultation",
            tool_type="gate_system",
            parameters={
                "tools_consulted": len(relevant_tools),
                "tools_applied": len(recommended_tools),
                "consultation_time": consultation_time,
                "gate_passed": gate_passed,
            },
            result="completed" if gate_passed else "blocked",
        )

        return result

    def consult_tools_holistically(
        self, user_request: str, context: Optional[Dict[str, Any]] = None
    ) -> ToolConsultationResult:
        """
        Use holistic tool orchestration to consult ALL relevant tools
        with vision alignment, user preferences, and safety gates.
        """

        start_time = time.time()

        # Track holistic consultation
        self.tool_tracker.track_tool_usage(
            "holistic_tool_consultation",
            "Tool_Consultation",
            {"user_request": user_request[:100]},
            "started",
        )

        try:
            # Use holistic orchestration
            orchestration_result = (
                self.holistic_orchestrator.orchestrate_tools_for_request(
                    user_request, context or {}, OrchestrationStrategy.ADAPTIVE
                )
            )

            # Convert to ToolConsultationResult format
            relevant_tools: Dict[str, ToolRelevanceLevel] = {}
            recommended_tools = orchestration_result.executed_tools
            tool_analysis: Dict[str, Any] = {}

            # Build tool analysis from orchestration results
            for tool_name in orchestration_result.executed_tools:
                relevant_tools[tool_name] = ToolRelevanceLevel.HIGH
                tool_analysis[tool_name] = {
                    "executed": True,
                    "results": orchestration_result.tool_results.get(tool_name),
                    "insights": orchestration_result.insights,
                }

            consultation_time = time.time() - start_time

            result = ToolConsultationResult(
                user_request=user_request,
                relevant_tools=relevant_tools,
                recommended_tools=recommended_tools,
                tool_analysis=tool_analysis,
                consultation_time=consultation_time,
                gate_passed=True,  # Holistic orchestration handles gates internally
                blocking_reason=None,
            )

            # Track successful completion
            self.tool_tracker.track_tool_usage(
                "holistic_tool_consultation",
                "Tool_Consultation",
                {
                    "tools_executed": len(orchestration_result.executed_tools),
                    "execution_time": consultation_time,
                    "vision_alignment": orchestration_result.vision_alignment_score,
                    "user_preference_compliance": orchestration_result.user_preference_compliance,
                    "safety_compliance": orchestration_result.safety_compliance,
                },
                "completed",
            )

            return result

        except Exception as e:
            consultation_time = time.time() - start_time

            # Track failure
            self.tool_tracker.track_tool_usage(
                "holistic_tool_consultation",
                "Tool_Consultation",
                {"error": str(e), "execution_time": consultation_time},
                "failed",
            )

            # Return failed result
            return ToolConsultationResult(
                user_request=user_request,
                relevant_tools={},
                recommended_tools=[],
                tool_analysis={},
                consultation_time=consultation_time,
                gate_passed=False,
                blocking_reason=f"Holistic orchestration failed: {str(e)}",
            )

    def _analyze_tool_relevance(
        self, user_request: str, context: Dict[str, Any]
    ) -> Dict[str, ToolRelevanceLevel]:
        """Analyze which tools are relevant to the user request."""

        request_lower = user_request.lower()
        relevant_tools: Dict[str, ToolRelevanceLevel] = {}

        from ..utilities.unicode_utils import ensure_unicode_safe

        ensure_unicode_safe("\n🔍 ANALYZING TOOL RELEVANCE:")

        for tool_name, tool_info in self.available_tools.items():
            relevance_score = 0
            relevance_reasons = []

            # Check keyword matches
            for keyword in tool_info.keywords:
                if keyword.lower() in request_lower:
                    relevance_score += 3
                    relevance_reasons.append(f"keyword: {keyword}")

            # Check context matches
            for ctx in tool_info.contexts:
                if ctx in context.get("contexts", []):
                    relevance_score += 2
                    relevance_reasons.append(f"context: {ctx}")

            # Check pattern matches
            import re

            for pattern in tool_info.patterns:
                if re.search(pattern.lower(), request_lower):
                    relevance_score += 4
                    relevance_reasons.append(f"pattern: {pattern}")

            # Determine relevance level
            if relevance_score >= 8:
                relevance = ToolRelevanceLevel.CRITICAL
            elif relevance_score >= 5:
                relevance = ToolRelevanceLevel.HIGH
            elif relevance_score >= 2:
                relevance = ToolRelevanceLevel.MEDIUM
            elif relevance_score >= 1:
                relevance = ToolRelevanceLevel.LOW
            else:
                relevance = ToolRelevanceLevel.NONE

            relevant_tools[tool_name] = relevance

            # Display relevance analysis
            if relevance != ToolRelevanceLevel.NONE:
                from ..utilities.unicode_utils import ensure_unicode_safe

                ensure_unicode_safe(
                    f"   🎯 {tool_name}: {relevance.value.upper()} ({relevance_score} points)"
                )
                for reason in relevance_reasons:
                    print(f"      • {reason}")

        return relevant_tools

    def _get_recommended_tools(
        self, relevant_tools: Dict[str, ToolRelevanceLevel]
    ) -> List[str]:
        """Get list of tools that should be applied."""

        recommended = []

        # Only recommend tools that can be auto-applied
        for tool_name, relevance in relevant_tools.items():
            tool_info = self.available_tools.get(tool_name)
            if not tool_info or not tool_info.can_auto_apply:
                continue  # Skip tools that can't be auto-applied

            # Always apply critical and high relevance tools
            if relevance in [ToolRelevanceLevel.CRITICAL, ToolRelevanceLevel.HIGH]:
                recommended.append(tool_name)

        # Apply medium relevance tools if not too many
        if len(recommended) < self.gate_config["max_tools_per_request"]:
            for tool_name, relevance in relevant_tools.items():
                tool_info = self.available_tools.get(tool_name)
                if (
                    tool_info
                    and tool_info.can_auto_apply
                    and relevance == ToolRelevanceLevel.MEDIUM
                    and len(recommended) < self.gate_config["max_tools_per_request"]
                ):
                    recommended.append(tool_name)

        return recommended

    def _apply_recommended_tools(
        self, recommended_tools: List[str], user_request: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply the recommended tools and gather results."""

        tool_analysis: Dict[str, Any] = {}

        if not recommended_tools:
            from ..utilities.unicode_utils import ensure_unicode_safe

            ensure_unicode_safe("\n📊 No tools recommended for this request")
            return tool_analysis

        from ..utilities.unicode_utils import ensure_unicode_safe

        ensure_unicode_safe(
            f"\n🚀 APPLYING {len(recommended_tools)} RECOMMENDED TOOLS:"
        )

        for tool_name in recommended_tools:
            ensure_unicode_safe(f"   🤖 Applying {tool_name}...")

            try:
                # Use the intelligent tool orchestrator to apply the tool
                from .unified_tool_orchestrator import ToolExecutionContext

                tool_context = ToolExecutionContext(
                    user_request=user_request,
                    session_id=context.get("session_id", "consultation"),
                    user_id=context.get("user_id", "system"),
                    additional_context={
                        "mandatory_consultation": True,
                        "consultation_time": time.time(),
                        "project_root": self.root_path,
                        **context,
                    },
                )
                orchestration_result = self.tool_orchestrator.orchestrate_tools(
                    user_request=user_request,
                    context=tool_context,
                )
                result = {
                    "executed": len(orchestration_result.executed_tools) > 0,
                    "results": orchestration_result.tool_results.get(tool_name, {}),
                    "error": None,
                }

                tool_analysis[tool_name] = result

                if result["executed"]:
                    from ..utilities.unicode_utils import ensure_unicode_safe

                    ensure_unicode_safe(f"      ✅ {tool_name} completed successfully")

                    # Extract key insights from results
                    insights = self._extract_tool_insights(tool_name, result["results"])
                    if insights:
                        tool_analysis[tool_name]["insights"] = insights
                        from ..utilities.unicode_utils import ensure_unicode_safe

                        ensure_unicode_safe(f"      💡 Key insights: {insights}")
                else:
                    from ..utilities.unicode_utils import ensure_unicode_safe

                    ensure_unicode_safe(
                        f"      ❌ {tool_name} failed: {result.get('error', 'Unknown error')}"
                    )

            except Exception as e:
                from ..utilities.unicode_utils import ensure_unicode_safe

                ensure_unicode_safe(f"      ❌ {tool_name} error: {str(e)}")
                tool_analysis[tool_name] = {"executed": False, "error": str(e)}

        return tool_analysis

    def _extract_tool_insights(self, tool_name: str, results: Any) -> Optional[str]:
        """Extract key insights from tool results for display."""

        if not results:
            return None

        try:
            if tool_name == "code_quality_analyzer":
                if hasattr(results, "total_issues"):
                    return f"{results.total_issues} quality issues found"

            elif tool_name == "file_organization_analyzer":
                if hasattr(results, "issues"):
                    return f"{len(results.issues)} organization issues found"

            elif tool_name == "duplicate_detector":
                if hasattr(results, "duplicate_groups"):
                    return f"{len(results.duplicate_groups)} duplicate groups found"

            elif tool_name == "dependency_mapper":
                if hasattr(results, "circular_dependencies"):
                    return (
                        f"{len(results.circular_dependencies)} circular dependencies detected, "
                        f"{results.modules_analyzed} modules analyzed"
                    )

            elif tool_name == "vision_guardian":
                if isinstance(results, dict):
                    vision = results.get("vision", "")
                    objectives = len(results.get("objectives", []))
                    return f"Vision context loaded with {objectives} objectives"

            elif tool_name == "gate_system":
                if isinstance(results, dict):
                    active = results.get("gate_active", False)
                    status = "active" if active else "inactive"
                    return f"Gate system {status}"

            elif tool_name == "ultra_safe_cleanup":
                if isinstance(results, dict):
                    targets = results.get("targets_found", 0)
                    size_mb = results.get("total_size_mb", 0)
                    return f"Cleanup scan complete: {targets} targets found ({size_mb:.1f} MB)"

            elif tool_name == "charter_management":
                if isinstance(results, dict):
                    project = results.get("project_name", "Unknown")
                    objectives = results.get("objectives_count", 0)
                    team_size = results.get("team_size", 0)
                    return (
                        f"Charter loaded: {project} with {objectives} objectives, "
                        f"team size {team_size}"
                    )

            elif tool_name == "automatic_error_prevention":
                if isinstance(results, dict):
                    prevented = results.get("errors_prevented", 0)
                    patterns = results.get("patterns_learned", 0)
                    return (
                        f"Error prevention active: {prevented} errors prevented, "
                        f"{patterns} patterns learned"
                    )

            elif tool_name == "pattern_recognition_system":
                if isinstance(results, dict):
                    patterns = results.get("total_patterns", 0)
                    matches = results.get("successful_matches", 0)
                    return (
                        f"Pattern system active: {patterns} patterns, "
                        f"{matches} successful matches"
                    )

            elif tool_name == "task_execution_gate":
                if isinstance(results, dict):
                    pending = results.get("pending_tasks", 0)
                    completed = results.get("completed_tasks", 0)
                    return (
                        f"Task gate status: {pending} pending tasks, "
                        f"{completed} completed"
                    )

            elif tool_name == "interrogation_system":
                if isinstance(results, dict):
                    sessions = results.get("active_sessions", 0)
                    questions = results.get("total_questions_asked", 0)
                    return (
                        f"Interrogation active: {sessions} sessions, "
                        f"{questions} questions asked"
                    )

            elif tool_name == "conversation_analysis":
                if isinstance(results, dict):
                    sessions = results.get("total_sessions", 0)
                    continuity = results.get("continuity_score", 0)
                    return (
                        f"Conversation analysis: {sessions} sessions, "
                        f"continuity score {continuity:.1f}"
                    )

            elif tool_name == "ui_enhancement":
                if isinstance(results, dict):
                    interventions = results.get("pending_interventions", 0)
                    satisfaction = results.get("current_satisfaction", 0)
                    return (
                        f"UX enhancements: {interventions} pending interventions, "
                        f"satisfaction {satisfaction:.1f}"
                    )

            elif tool_name == "wbs_management":
                if isinstance(results, dict):
                    consistency = results.get("overall_consistency", 0)
                    issues = results.get("total_issues", 0)
                    return (
                        f"WBS management: {consistency:.1f}% consistency, "
                        f"{issues} issues found"
                    )

            elif tool_name == "ai_agent_orchestration":
                if isinstance(results, dict):
                    active = results.get("is_active", False)
                    tools = results.get("available_tools", 0)
                    return f"AI orchestration {'active' if active else 'inactive'}: {tools} tools available"

            elif tool_name == "decision_pipeline":
                if isinstance(results, dict):
                    active = results.get("pipeline_active", False)
                    capabilities = len(results.get("decision_capabilities", []))
                    return f"Decision pipeline {'active' if active else 'inactive'}: {capabilities} capabilities"

            elif tool_name == "intelligent_monitoring":
                if isinstance(results, dict):
                    triggers = results.get("active_triggers", 0)
                    alerts = results.get("pending_alerts", 0)
                    return (
                        f"Intelligent monitoring: {triggers} triggers, "
                        f"{alerts} pending alerts"
                    )

            elif tool_name == "user_preference_learning_system":
                if isinstance(results, dict):
                    preferences = results.get("total_preferences", 0)
                    confidence = results.get("avg_confidence", 0)
                    return (
                        f"User preferences: {preferences} learned, "
                        f"{confidence:.1f} avg confidence"
                    )

                # Removed: codebase_analysis (redundant with code_quality)
                # elif tool_name == "codebase_analysis":
                if isinstance(results, dict):
                    files = results.get("files_analyzed", 0)
                    issues = results.get("total_issues", 0)
                    return (
                        f"Codebase analysis: {files} files analyzed, "
                        f"{issues} organization issues found"
                    )

            elif tool_name == "syntax_validator":
                if isinstance(results, dict):
                    total = results.get("total_files", 0)
                    valid = results.get("valid_files", 0)
                    invalid = results.get("invalid_files", 0)
                    return (
                        f"Syntax validation: {valid}/{total} files valid, "
                        f"{invalid} syntax errors found"
                    )

            elif tool_name == "dependency_checker":
                if isinstance(results, dict):
                    safe = results.get("safe_to_remove", False)
                    total = results.get("total_targets", 0)
                    checked = results.get("checked_targets", 0)
                    return (
                        f"Dependency check: {checked}/{total} targets analyzed, "
                        f"safe to remove: {safe}"
                    )

            elif tool_name == "approval_workflow":
                if isinstance(results, dict):
                    pending = results.get("pending_requests", 0)
                    return f"Approval workflow: {pending} pending approval requests"

            elif tool_name == "critical_path_engine":
                if isinstance(results, dict):
                    critical_path = results.get("critical_path", [])
                    duration = results.get("project_duration", 0)
                    return (
                        f"Critical path: {len(critical_path)} tasks, "
                        f"{duration} day duration"
                    )

            elif tool_name == "progress_dashboard":
                if isinstance(results, dict):
                    status = results.get("project_status", "unknown")
                    completion = results.get("completion_percentage", 0)
                    return f"Progress dashboard: {status}, {completion:.1f}% complete"

            elif tool_name == "task_completion_detector":
                if isinstance(results, dict):
                    completed = results.get("completed_tasks", 0)
                    total = results.get("total_tasks", 0)
                    return f"Task completion: {completed}/{total} tasks completed"

            elif tool_name == "task_prioritization_engine":
                if isinstance(results, dict):
                    high_priority = results.get("high_priority_tasks", 0)
                    total = results.get("total_tasks", 0)
                    return f"Task prioritization: {high_priority}/{total} high priority tasks identified"

            elif tool_name == "wbs_management":
                if isinstance(results, dict):
                    wbs_elements = results.get("total_elements", 0)
                    consistency = results.get("consistency_score", 0)
                    return (
                        f"WBS management: {wbs_elements} elements, "
                        f"{consistency:.1f}% consistency"
                    )

            elif tool_name == "automated_health_monitoring":
                if isinstance(results, dict):
                    status = results.get("overall_status", "unknown")
                    healthy = results.get("summary", {}).get("healthy_tools", 0)
                    total = results.get("summary", {}).get("total_tools", 0)
                    return (
                        f"Health monitoring: {healthy}/{total} tools healthy, "
                        f"status {status}"
                    )

            # Generic tool recognition handler
            elif isinstance(results, dict) and results.get("status") == "recognized":
                return results.get(
                    "message",
                    f"Tool '{tool_name}' recognized but requires manual invocation",
                )

        except Exception as e:
            # Debug: print the exception
            print(f"DEBUG: Insight extraction failed for {tool_name}: {e}")

        return None

    def _evaluate_gate_passage(
        self,
        relevant_tools: Dict[str, ToolRelevanceLevel],
        recommended_tools: List[str],
        tool_analysis: Dict[str, Any],
        consultation_time: float,
    ) -> tuple[bool, Optional[str]]:
        """Evaluate whether the gate should allow passage."""

        # PRIME DIRECTIVE LOGIC:
        # 1. If no tools are relevant to the request, allow passage (simple commands)
        # 2. If tools are relevant and were consulted/attempted, allow passage
        # 3. Only block if tools were relevant but not consulted at all

        # Fast path: No tools recommended for this request
        if not recommended_tools:
            return True, None

        # Tools were recommended - check if they were actually consulted
        if tool_analysis:
            # Tools were consulted (regardless of success/failure)
            # This satisfies the prime directive requirement
            return True, None

        # Edge case: Tools were recommended but none were attempted
        # This could happen due to errors in the consultation process
        if consultation_time < self.gate_config["minimum_consultation_time"]:
            return (
                False,
                (
                    f"Tools were recommended but consultation failed: "
                    f"{consultation_time:.2f}s < {self.gate_config['minimum_consultation_time']}s"
                ),
            )

        # Gate passes - tools were consulted
        return True, None

    def _display_consultation_results(self, result: ToolConsultationResult):
        """Display the consultation results to the user."""

        from ..utilities.unicode_utils import ensure_unicode_safe

        ensure_unicode_safe(f"\n📊 CONSULTATION SUMMARY:")
        ensure_unicode_safe(f"   ⏱️  Consultation time: {result.consultation_time:.2f}s")
        ensure_unicode_safe(f"   🎯 Tools analyzed: {len(result.relevant_tools)}")
        ensure_unicode_safe(f"   🚀 Tools applied: {len(result.recommended_tools)}")

        # Show applied tools and their insights
        successful_tools = []
        failed_tools = []

        for tool_name, analysis in result.tool_analysis.items():
            if analysis.get("executed"):
                successful_tools.append(tool_name)
                if "insights" in analysis:
                    from ..utilities.unicode_utils import ensure_unicode_safe

                    ensure_unicode_safe(f"      ✅ {tool_name}: {analysis['insights']}")
                else:
                    from ..utilities.unicode_utils import ensure_unicode_safe

                    ensure_unicode_safe(f"      ✅ {tool_name}: completed")
            else:
                failed_tools.append(tool_name)
                from ..utilities.unicode_utils import ensure_unicode_safe

                ensure_unicode_safe(
                    f"      ❌ {tool_name}: {analysis.get('error', 'failed')}"
                )

        # Gate status
        if result.gate_passed:
            from ..utilities.unicode_utils import ensure_unicode_safe

            ensure_unicode_safe(
                "   🟢 GATE STATUS: PASSED - Proceeding with AI response"
            )
        else:
            from ..utilities.unicode_utils import ensure_unicode_safe

            ensure_unicode_safe(
                f"   🔴 GATE STATUS: BLOCKED - {result.blocking_reason}"
            )

        print("=" * 50)

    def get_consultation_stats(self) -> Dict[str, Any]:
        """Get consultation statistics."""
        return {
            **self.consultation_stats,
            "available_tools": len(self.available_tools),
            "gate_config": self.gate_config,
        }

    def bypass_gate(self, reason: str) -> bool:
        """Bypass the gate (emergency use only)."""
        if not self.gate_config["allow_bypass"]:
            return False

        print(f"⚠️ GATE BYPASS: {reason}")
        self.consultation_stats["bypasses"] += 1
        return True


# Global gate instance
_gate_instance: Optional[MandatoryToolConsultationGate] = None


def get_mandatory_gate(root_path: Path) -> MandatoryToolConsultationGate:
    """Get the global mandatory tool consultation gate."""
    global _gate_instance
    if _gate_instance is None or _gate_instance.root_path != root_path:
        _gate_instance = MandatoryToolConsultationGate(root_path)
    return _gate_instance


def enforce_tool_consultation(
    user_request: str,
    context: Optional[Dict[str, Any]] = None,
    root_path: Optional[Path] = None,
) -> ToolConsultationResult:
    """
    Enforce mandatory tool consultation for any user request.

    This is the main entry point that should be called before any AI response.
    """
    if root_path is None:
        root_path = Path.cwd()

    gate = get_mandatory_gate(root_path)
    return gate.consult_tools_for_request(user_request, context)
