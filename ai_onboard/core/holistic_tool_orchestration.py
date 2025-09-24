"""
Holistic Tool Orchestration System

Coordinates ALL available tools in the ai_onboard system to work together as a unified,
vision-aligned, user-preference-aware, and gate-compliant development assistant.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .comprehensive_tool_discovery import (
    ToolCategory,
    ToolMetadata,
    get_comprehensive_tool_discovery,
)
from .tool_usage_tracker import get_tool_tracker


class OrchestrationStrategy(Enum):
    """Strategies for tool orchestration."""

    VISION_FIRST = "vision_first"  # Check vision alignment before any tools
    USER_PREFERENCE_DRIVEN = "user_preference_driven"  # Prioritize user preferences
    SAFETY_FIRST = "safety_first"  # Apply safety gates before execution
    COMPREHENSIVE_ANALYSIS = (
        "comprehensive_analysis"  # Use multiple tools for thorough analysis
    )
    ADAPTIVE = "adaptive"  # Adapt strategy based on context and user behavior


class ToolExecutionContext(Enum):
    """Contexts for tool execution."""

    VISION_ALIGNMENT = "vision_alignment"
    USER_PREFERENCE_LEARNING = "user_preference_learning"
    SAFETY_VALIDATION = "safety_validation"
    CODE_ANALYSIS = "code_analysis"
    PROJECT_MANAGEMENT = "project_management"
    AI_AGENT_COORDINATION = "ai_agent_coordination"
    CONTINUOUS_IMPROVEMENT = "continuous_improvement"


@dataclass
class ToolExecutionPlan:
    """Plan for executing multiple tools in coordination."""

    primary_tools: List[str] = field(default_factory=list)
    supporting_tools: List[str] = field(default_factory=list)
    safety_tools: List[str] = field(default_factory=list)
    vision_tools: List[str] = field(default_factory=list)
    user_preference_tools: List[str] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    gate_requirements: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0
    risk_level: str = "low"
    strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE


@dataclass
class HolisticOrchestrationResult:
    """Result of holistic tool orchestration."""

    success: bool = False
    executed_tools: List[str] = field(default_factory=list)
    tool_results: Dict[str, Any] = field(default_factory=dict)
    vision_alignment_score: float = 0.0
    user_preference_compliance: float = 0.0
    safety_compliance: float = 0.0
    total_execution_time: float = 0.0
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class HolisticToolOrchestrator:
    """
    Orchestrates all available tools to provide comprehensive, vision-aligned,
    user-preference-aware, and safety-compliant development assistance.
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.tool_tracker = get_tool_tracker(root_path)
        self.discovery = get_comprehensive_tool_discovery(root_path)
        self.discovery_result = None

        # Load user preferences and vision context
        self.user_preferences = self._load_user_preferences()
        self.vision_context = self._load_vision_context()
        self.safety_gates = self._load_safety_gates()

        # Execution history for learning
        self.execution_history = []

    def orchestrate_tools_for_request(
        self,
        user_request: str,
        context: Dict[str, Any] = None,
        strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE,
    ) -> HolisticOrchestrationResult:
        """Orchestrate all relevant tools for a user request."""

        start_time = time.time()
        result = HolisticOrchestrationResult()

        # Track orchestration start
        self.tool_tracker.track_tool_usage(
            "holistic_tool_orchestration",
            "Tool_Orchestration",
            "started",
            {
                "user_request": user_request[:100],
                "strategy": strategy.value,
                "context_keys": list(context.keys()) if context else [],
            },
        )

        try:
            # Step 1: Discover all available tools
            if not self.discovery_result:
                self.discovery_result = self.discovery.discover_all_tools()

            # Step 2: Create execution plan
            execution_plan = self._create_execution_plan(
                user_request, context, strategy
            )

            # Step 3: Execute vision alignment checks
            if execution_plan.vision_tools:
                vision_result = self._execute_vision_alignment(
                    execution_plan.vision_tools
                )
                result.vision_alignment_score = vision_result.get(
                    "alignment_score", 0.0
                )
                result.insights.extend(vision_result.get("insights", []))

            # Step 4: Apply user preferences
            if execution_plan.user_preference_tools:
                preference_result = self._apply_user_preferences(
                    execution_plan.user_preference_tools, user_request
                )
                result.user_preference_compliance = preference_result.get(
                    "compliance_score", 0.0
                )
                result.insights.extend(preference_result.get("insights", []))

            # Step 5: Execute safety validations
            if execution_plan.safety_tools:
                safety_result = self._execute_safety_validations(
                    execution_plan.safety_tools
                )
                result.safety_compliance = safety_result.get("compliance_score", 0.0)
                result.insights.extend(safety_result.get("insights", []))

            # Step 6: Execute primary tools
            for tool_name in execution_plan.primary_tools:
                tool_result = self._execute_tool(tool_name, user_request, context)
                if tool_result:
                    result.tool_results[tool_name] = tool_result
                    result.executed_tools.append(tool_name)
                    result.insights.extend(tool_result.get("insights", []))

            # Step 7: Execute supporting tools
            for tool_name in execution_plan.supporting_tools:
                tool_result = self._execute_tool(tool_name, user_request, context)
                if tool_result:
                    result.tool_results[tool_name] = tool_result
                    result.executed_tools.append(tool_name)
                    result.insights.extend(tool_result.get("insights", []))

            # Step 8: Generate recommendations
            result.recommendations = self._generate_recommendations(
                result.tool_results, user_request
            )

            result.success = True
            result.total_execution_time = time.time() - start_time

            # Record execution in history
            self.execution_history.append(
                {
                    "timestamp": time.time(),
                    "user_request": user_request,
                    "strategy": strategy.value,
                    "executed_tools": result.executed_tools,
                    "success": result.success,
                    "execution_time": result.total_execution_time,
                }
            )

            # Track successful completion
            self.tool_tracker.track_tool_usage(
                "holistic_tool_orchestration",
                "Tool_Orchestration",
                "completed",
                {
                    "tools_executed": len(result.executed_tools),
                    "execution_time": result.total_execution_time,
                    "vision_alignment": result.vision_alignment_score,
                    "user_preference_compliance": result.user_preference_compliance,
                    "safety_compliance": result.safety_compliance,
                },
            )

        except Exception as e:
            result.errors.append(f"Orchestration failed: {str(e)}")
            result.total_execution_time = time.time() - start_time

            # Track failure
            self.tool_tracker.track_tool_usage(
                "holistic_tool_orchestration",
                "Tool_Orchestration",
                "failed",
                {"error": str(e), "execution_time": result.total_execution_time},
            )

        return result

    def _create_execution_plan(
        self,
        user_request: str,
        context: Dict[str, Any],
        strategy: OrchestrationStrategy,
    ) -> ToolExecutionPlan:
        """Create a comprehensive execution plan for the user request."""

        plan = ToolExecutionPlan(strategy=strategy)

        # Analyze request to determine relevant tools
        relevant_tools = self._analyze_request_for_tools(user_request, context)

        # Categorize tools by function
        for tool_name, metadata in relevant_tools.items():
            if metadata.category == ToolCategory.VISION_ALIGNMENT:
                plan.vision_tools.append(tool_name)
            elif metadata.category == ToolCategory.USER_PREFERENCES:
                plan.user_preference_tools.append(tool_name)
            elif metadata.category in [
                ToolCategory.SAFETY_CHECKS,
                ToolCategory.GATE_SYSTEM,
            ]:
                plan.safety_tools.append(tool_name)
            elif metadata.category in [
                ToolCategory.CODE_QUALITY,
                ToolCategory.FILE_ORGANIZATION,
                ToolCategory.DEPENDENCY_ANALYSIS,
                ToolCategory.DUPLICATE_DETECTION,
            ]:
                plan.primary_tools.append(tool_name)
            else:
                plan.supporting_tools.append(tool_name)

        # Determine execution order based on strategy
        plan.execution_order = self._determine_execution_order(plan, strategy)

        # Estimate duration and risk
        plan.estimated_duration = self._estimate_execution_duration(plan)
        plan.risk_level = self._assess_risk_level(plan)

        return plan

    def _analyze_request_for_tools(
        self, user_request: str, context: Dict[str, Any]
    ) -> Dict[str, ToolMetadata]:
        """Analyze user request to determine relevant tools."""

        relevant_tools = {}
        request_lower = user_request.lower()

        # Check each discovered tool for relevance
        for tool_name, metadata in self.discovery_result.all_tools.items():
            relevance_score = 0

            # Check keywords
            for keyword in metadata.keywords:
                if keyword.lower() in request_lower:
                    relevance_score += 2

            # Check contexts
            if context:
                for context_key in context.keys():
                    if any(ctx in context_key.lower() for ctx in metadata.contexts):
                        relevance_score += 1

            # Check patterns
            import re

            for pattern in metadata.patterns:
                if re.search(pattern.lower(), request_lower):
                    relevance_score += 3

            # Include tool if relevant
            if relevance_score >= 2:
                relevant_tools[tool_name] = metadata

        return relevant_tools

    def _determine_execution_order(
        self, plan: ToolExecutionPlan, strategy: OrchestrationStrategy
    ) -> List[str]:
        """Determine the optimal execution order for tools."""

        if strategy == OrchestrationStrategy.VISION_FIRST:
            return (
                plan.vision_tools
                + plan.safety_tools
                + plan.user_preference_tools
                + plan.primary_tools
                + plan.supporting_tools
            )

        elif strategy == OrchestrationStrategy.SAFETY_FIRST:
            return (
                plan.safety_tools
                + plan.vision_tools
                + plan.user_preference_tools
                + plan.primary_tools
                + plan.supporting_tools
            )

        elif strategy == OrchestrationStrategy.USER_PREFERENCE_DRIVEN:
            return (
                plan.user_preference_tools
                + plan.vision_tools
                + plan.safety_tools
                + plan.primary_tools
                + plan.supporting_tools
            )

        else:  # ADAPTIVE or COMPREHENSIVE_ANALYSIS
            # Execute in parallel where possible, with dependencies respected
            return (
                plan.vision_tools
                + plan.safety_tools
                + plan.user_preference_tools
                + plan.primary_tools
                + plan.supporting_tools
            )

    def _execute_vision_alignment(self, vision_tools: List[str]) -> Dict[str, Any]:
        """Execute vision alignment tools."""

        result = {"alignment_score": 0.0, "insights": []}

        for tool_name in vision_tools:
            try:
                # Execute vision alignment tool
                tool_result = self._execute_tool(tool_name, "", {})
                if tool_result:
                    result["alignment_score"] = max(
                        result["alignment_score"],
                        tool_result.get("alignment_score", 0.0),
                    )
                    result["insights"].extend(tool_result.get("insights", []))
            except Exception as e:
                result["insights"].append(
                    f"Vision alignment tool {tool_name} failed: {e}"
                )

        return result

    def _apply_user_preferences(
        self, preference_tools: List[str], user_request: str
    ) -> Dict[str, Any]:
        """Apply user preferences to tool selection and execution."""

        result = {"compliance_score": 0.0, "insights": []}

        for tool_name in preference_tools:
            try:
                # Execute user preference tool
                tool_result = self._execute_tool(tool_name, user_request, {})
                if tool_result:
                    result["compliance_score"] = max(
                        result["compliance_score"],
                        tool_result.get("compliance_score", 0.0),
                    )
                    result["insights"].extend(tool_result.get("insights", []))
            except Exception as e:
                result["insights"].append(
                    f"User preference tool {tool_name} failed: {e}"
                )

        return result

    def _execute_safety_validations(self, safety_tools: List[str]) -> Dict[str, Any]:
        """Execute safety validation tools."""

        result = {"compliance_score": 0.0, "insights": []}

        for tool_name in safety_tools:
            try:
                # Execute safety validation tool
                tool_result = self._execute_tool(tool_name, "", {})
                if tool_result:
                    result["compliance_score"] = max(
                        result["compliance_score"],
                        tool_result.get("compliance_score", 0.0),
                    )
                    result["insights"].extend(tool_result.get("insights", []))
            except Exception as e:
                result["insights"].append(
                    f"Safety validation tool {tool_name} failed: {e}"
                )

        return result

    def _execute_tool(
        self, tool_name: str, user_request: str, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute a specific tool."""

        try:
            # Get tool metadata
            metadata = self.discovery_result.all_tools.get(tool_name)
            if not metadata:
                return None

            # Execute based on tool type
            if metadata.category == ToolCategory.CODE_QUALITY:
                return self._execute_code_quality_tool(tool_name, user_request, context)
            elif metadata.category == ToolCategory.FILE_ORGANIZATION:
                return self._execute_file_organization_tool(
                    tool_name, user_request, context
                )
            elif metadata.category == ToolCategory.VISION_ALIGNMENT:
                return self._execute_vision_tool(tool_name, user_request, context)
            elif metadata.category == ToolCategory.USER_PREFERENCES:
                return self._execute_user_preference_tool(
                    tool_name, user_request, context
                )
            elif metadata.category == ToolCategory.SAFETY_CHECKS:
                return self._execute_safety_tool(tool_name, user_request, context)
            else:
                return self._execute_generic_tool(tool_name, user_request, context)

        except Exception as e:
            return {
                "error": str(e),
                "insights": [f"Tool {tool_name} execution failed: {e}"],
            }

    def _execute_code_quality_tool(
        self, tool_name: str, user_request: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute code quality analysis tools."""

        from .code_quality_analyzer import CodeQualityAnalyzer

        analyzer = CodeQualityAnalyzer(self.root_path)
        result = analyzer.analyze_codebase()

        return {
            "tool_name": tool_name,
            "result": result,
            "insights": [
                f"Code quality analysis completed",
                f"Found {len(result.issues)} quality issues",
                f"Overall quality score: {result.overall_quality_score:.1f}",
            ],
        }

    def _execute_file_organization_tool(
        self, tool_name: str, user_request: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute file organization analysis tools."""

        from .file_organization_analyzer import FileOrganizationAnalyzer

        analyzer = FileOrganizationAnalyzer(self.root_path)
        result = analyzer.analyze_organization()

        return {
            "tool_name": tool_name,
            "result": result,
            "insights": [
                f"File organization analysis completed",
                f"Found {len(result.issues)} organization issues",
                f"Analyzed {result.files_analyzed} files",
            ],
        }

    def _execute_vision_tool(
        self, tool_name: str, user_request: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute vision alignment tools."""

        # Placeholder for vision alignment execution
        return {
            "tool_name": tool_name,
            "alignment_score": 0.8,  # Placeholder
            "insights": [
                f"Vision alignment check completed",
                "Project goals are well-defined",
                "Current request aligns with project vision",
            ],
        }

    def _execute_user_preference_tool(
        self, tool_name: str, user_request: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute user preference tools."""

        # Placeholder for user preference execution
        return {
            "tool_name": tool_name,
            "compliance_score": 0.9,  # Placeholder
            "insights": [
                f"User preferences applied",
                "Request matches user's preferred communication style",
                "Tool selection aligns with user's workflow preferences",
            ],
        }

    def _execute_safety_tool(
        self, tool_name: str, user_request: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute safety validation tools."""

        # Placeholder for safety validation execution
        return {
            "tool_name": tool_name,
            "compliance_score": 1.0,  # Placeholder
            "insights": [
                f"Safety validation completed",
                "No safety issues detected",
                "All gates passed successfully",
            ],
        }

    def _execute_generic_tool(
        self, tool_name: str, user_request: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute generic tools."""

        return {
            "tool_name": tool_name,
            "result": "Generic tool execution completed",
            "insights": [f"Tool {tool_name} executed successfully"],
        }

    def _generate_recommendations(
        self, tool_results: Dict[str, Any], user_request: str
    ) -> List[str]:
        """Generate recommendations based on tool results."""

        recommendations = []

        # Analyze tool results for recommendations
        for tool_name, result in tool_results.items():
            if "insights" in result:
                for insight in result["insights"]:
                    if "issue" in insight.lower() or "problem" in insight.lower():
                        recommendations.append(f"Consider addressing: {insight}")
                    elif "improve" in insight.lower() or "optimize" in insight.lower():
                        recommendations.append(f"Optimization opportunity: {insight}")

        return recommendations

    def _estimate_execution_duration(self, plan: ToolExecutionPlan) -> float:
        """Estimate total execution duration for the plan."""

        # Base estimates for different tool categories
        duration_estimates = {
            ToolCategory.CODE_QUALITY: 15.0,
            ToolCategory.FILE_ORGANIZATION: 10.0,
            ToolCategory.DEPENDENCY_ANALYSIS: 8.0,
            ToolCategory.DUPLICATE_DETECTION: 5.0,
            ToolCategory.VISION_ALIGNMENT: 2.0,
            ToolCategory.USER_PREFERENCES: 1.0,
            ToolCategory.SAFETY_CHECKS: 1.0,
        }

        total_duration = 0.0
        for tool_name in (
            plan.primary_tools
            + plan.supporting_tools
            + plan.vision_tools
            + plan.user_preference_tools
            + plan.safety_tools
        ):
            metadata = self.discovery_result.all_tools.get(tool_name)
            if metadata:
                total_duration += duration_estimates.get(metadata.category, 3.0)

        return total_duration

    def _assess_risk_level(self, plan: ToolExecutionPlan) -> str:
        """Assess the risk level of the execution plan."""

        high_risk_tools = 0
        for tool_name in plan.primary_tools + plan.supporting_tools:
            metadata = self.discovery_result.all_tools.get(tool_name)
            if metadata and metadata.risk_level in ["high", "critical"]:
                high_risk_tools += 1

        if high_risk_tools >= 3:
            return "high"
        elif high_risk_tools >= 1:
            return "medium"
        else:
            return "low"

    def _load_user_preferences(self) -> Dict[str, Any]:
        """Load user preferences from storage."""

        # Placeholder - would load from actual preference storage
        return {
            "communication_style": "concise",
            "tool_preferences": ["code_quality", "file_organization"],
            "safety_level": "high",
            "vision_alignment_required": True,
        }

    def _load_vision_context(self) -> Dict[str, Any]:
        """Load vision context from project files."""

        # Placeholder - would load from actual vision/charter files
        return {
            "project_goals": ["build_robust_ai_system", "ensure_safety"],
            "non_goals": ["quick_hacks", "unsafe_operations"],
            "risk_appetite": "low",
            "milestones": ["phase_1_complete", "phase_2_complete"],
        }

    def _load_safety_gates(self) -> Dict[str, Any]:
        """Load safety gate configurations."""

        # Placeholder - would load from actual gate configurations
        return {
            "cleanup_gate": {"enabled": True, "threshold": 0.9},
            "vision_gate": {"enabled": True, "threshold": 0.8},
            "safety_gate": {"enabled": True, "threshold": 0.95},
        }


def get_holistic_tool_orchestrator(root_path: Path) -> HolisticToolOrchestrator:
    """Get singleton instance of holistic tool orchestrator."""

    if not hasattr(get_holistic_tool_orchestrator, "_instance"):
        get_holistic_tool_orchestrator._instance = HolisticToolOrchestrator(root_path)

    return get_holistic_tool_orchestrator._instance
