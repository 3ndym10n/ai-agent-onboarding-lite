"""
Comprehensive Tool Discovery System

Discovers and catalogs ALL available tools in the ai_onboard system,
integrating them into the prime directive for holistic assistance.
"""

import importlib
import inspect
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from .tool_usage_tracker import get_tool_tracker


class ToolCategory(Enum):
    """Categories of tools available in the system."""

    # Core Analysis Tools
    CODE_QUALITY = "code_quality"
    FILE_ORGANIZATION = "file_organization"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    DUPLICATE_DETECTION = "duplicate_detection"

    # Vision & Alignment Tools
    VISION_ALIGNMENT = "vision_alignment"
    CHARTER_MANAGEMENT = "charter_management"
    INTERROGATION = "interrogation"
    ALIGNMENT_CHECK = "alignment_check"

    # User Experience Tools
    USER_PREFERENCES = "user_preferences"
    CONVERSATION_ANALYSIS = "conversation_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"

    # Safety & Validation Tools
    GATE_SYSTEM = "gate_system"
    SAFETY_CHECKS = "safety_checks"
    ERROR_PREVENTION = "error_prevention"

    # Project Management Tools
    WBS_MANAGEMENT = "wbs_management"
    TASK_EXECUTION = "task_execution"
    METRICS_ANALYSIS = "metrics_analysis"

    # Development Workflow Tools
    CLEANUP_SAFETY = "cleanup_safety"
    CONTINUOUS_IMPROVEMENT = "continuous_improvement"
    OPTIMIZATION = "optimization"
    TESTING_ENHANCEMENT = "testing_enhancement"

    # AI Agent Tools
    AI_AGENT_ORCHESTRATION = "ai_agent_orchestration"
    DECISION_PIPELINE = "decision_pipeline"
    INTELLIGENT_MONITORING = "intelligent_monitoring"
    BACKGROUND_AGENTS = "background_agents"

    # Communication & UI Tools
    UI_ENHANCEMENT = "ui_enhancement"
    UX_MIDDLEWARE = "ux_middleware"
    VISUAL_COMPONENTS = "visual_components"
    API_SERVER = "api_server"

    # Advanced Features
    CURSOR_INTEGRATION = "cursor_integration"
    CAPABILITY_TRACKING = "capability_tracking"
    PERFORMANCE_TRENDS = "performance_trends"
    ENHANCED_TESTING = "enhanced_testing"


@dataclass
class ToolMetadata:
    """Metadata for a discovered tool."""

    name: str
    category: ToolCategory
    module_path: str
    class_name: Optional[str] = None
    function_name: Optional[str] = None
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    contexts: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    gate_requirements: List[str] = field(default_factory=list)
    user_preference_sensitive: bool = False
    vision_alignment_required: bool = False
    risk_level: str = "low"  # low, medium, high, critical


@dataclass
class ToolDiscoveryResult:
    """Result of comprehensive tool discovery."""

    total_tools: int = 0
    tools_by_category: Dict[ToolCategory, List[ToolMetadata]] = field(
        default_factory=dict
    )
    all_tools: Dict[str, ToolMetadata] = field(default_factory=dict)
    missing_dependencies: List[str] = field(default_factory=list)
    discovery_errors: List[str] = field(default_factory=list)


class ComprehensiveToolDiscovery:
    """Discovers and catalogs all available tools in the ai_onboard system."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.tool_tracker = get_tool_tracker(root_path)

        # Tool discovery patterns
        self.analysis_patterns = [
            r"analyze.*",
            r"analysis.*",
            r"check.*",
            r"validate.*",
            r"detect.*",
            r"find.*",
            r"scan.*",
            r"inspect.*",
        ]

        self.management_patterns = [
            r"manage.*",
            r"update.*",
            r"sync.*",
            r"track.*",
            r"monitor.*",
            r"control.*",
            r"execute.*",
            r"run.*",
        ]

        self.safety_patterns = [
            r"safe.*",
            r"secure.*",
            r"protect.*",
            r"guard.*",
            r"prevent.*",
            r"block.*",
            r"gate.*",
            r"checkpoint.*",
        ]

        self.vision_patterns = [
            r"vision.*",
            r"charter.*",
            r"align.*",
            r"interrogate.*",
            r"goal.*",
            r"objective.*",
            r"mission.*",
            r"purpose.*",
        ]

    def discover_all_tools(self) -> ToolDiscoveryResult:
        """Discover all available tools in the system."""

        result = ToolDiscoveryResult()

        # Track tool discovery
        self.tool_tracker.track_tool_usage(
            "comprehensive_tool_discovery",
            "Tool_Discovery",
            {"scope": "full_system_scan"},
            "started",
        )

        try:
            # Discover CLI command tools
            cli_tools = self._discover_cli_tools()
            result.all_tools.update(cli_tools)

            # Discover core analysis tools
            core_tools = self._discover_core_tools()
            result.all_tools.update(core_tools)

            # Discover vision and alignment tools
            vision_tools = self._discover_vision_tools()
            result.all_tools.update(vision_tools)

            # Discover safety and validation tools
            safety_tools = self._discover_safety_tools()
            result.all_tools.update(safety_tools)

            # Discover user experience tools
            ux_tools = self._discover_ux_tools()
            result.all_tools.update(ux_tools)

            # Discover project management tools
            pm_tools = self._discover_project_management_tools()
            result.all_tools.update(pm_tools)

            # Discover AI agent tools
            ai_tools = self._discover_ai_agent_tools()
            result.all_tools.update(ai_tools)

            # Categorize tools
            result.tools_by_category = self._categorize_tools(result.all_tools)
            result.total_tools = len(result.all_tools)

            # Track completion
            self.tool_tracker.track_tool_usage(
                "comprehensive_tool_discovery",
                "Tool_Discovery",
                {
                    "total_tools": result.total_tools,
                    "categories": len(result.tools_by_category),
                    "errors": len(result.discovery_errors),
                },
                "completed",
            )

        except Exception as e:
            result.discovery_errors.append(f"Tool discovery failed: {str(e)}")
            self.tool_tracker.track_tool_usage(
                "comprehensive_tool_discovery",
                "Tool_Discovery",
                {"error": str(e)},
                "failed",
            )

        return result

    def _discover_cli_tools(self) -> Dict[str, ToolMetadata]:
        """Discover CLI command tools."""

        tools: Dict[str, ToolMetadata] = {}
        cli_path = self.root_path / "ai_onboard" / "cli"

        if not cli_path.exists():
            return tools

        for cmd_file in cli_path.glob("commands_*.py"):
            try:
                module_name = f"ai_onboard.cli.{cmd_file.stem}"
                module = importlib.import_module(module_name)

                # Look for command functions
                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isfunction(obj)
                        and name.startswith(("add_", "handle_"))
                        and "command" in name.lower()
                    ):

                        tool_name = f"cli_{name}"
                        category = self._determine_cli_category(name, obj)

                        tools[tool_name] = ToolMetadata(
                            name=tool_name,
                            category=category,
                            module_path=module_name,
                            function_name=name,
                            description=f"CLI command: {name}",
                            keywords=self._extract_cli_keywords(name, obj),
                            contexts=["cli_interface", "command_execution"],
                            patterns=self._extract_cli_patterns(name),
                            gate_requirements=self._determine_cli_gates(name),
                            user_preference_sensitive=True,
                            vision_alignment_required=self._requires_vision_alignment(
                                name
                            ),
                        )

            except Exception as e:
                print(f"Warning: Could not analyze CLI module {cmd_file}: {e}")

        return tools

    def _discover_core_tools(self) -> Dict[str, ToolMetadata]:
        """Discover core analysis and utility tools."""

        tools: Dict[str, ToolMetadata] = {}
        core_path = self.root_path / "ai_onboard" / "core"

        if not core_path.exists():
            return tools

        # Known core tools
        core_tool_mappings = {
            "code_quality_analyzer.py": {
                "class": "CodeQualityAnalyzer",
                "category": ToolCategory.CODE_QUALITY,
                "keywords": [
                    "quality",
                    "analysis",
                    "unused",
                    "dead_code",
                    "complexity",
                ],
                "contexts": ["code_review", "refactoring", "cleanup"],
                "vision_alignment_required": False,
            },
            "file_organization_analyzer.py": {
                "class": "FileOrganizationAnalyzer",
                "category": ToolCategory.FILE_ORGANIZATION,
                "keywords": ["organization", "structure", "files", "directories"],
                "contexts": ["file_management", "project_structure"],
                "vision_alignment_required": False,
            },
            "dependency_mapper.py": {
                "class": "DependencyMapper",
                "category": ToolCategory.DEPENDENCY_ANALYSIS,
                "keywords": ["dependencies", "imports", "modules", "circular"],
                "contexts": ["dependency_analysis", "architecture"],
                "vision_alignment_required": False,
            },
            "duplicate_detector.py": {
                "class": "DuplicateDetector",
                "category": ToolCategory.DUPLICATE_DETECTION,
                "keywords": ["duplicates", "similarity", "code_reuse"],
                "contexts": ["code_analysis", "refactoring"],
                "vision_alignment_required": False,
            },
            "user_preference_learning.py": {
                "class": "UserPreferenceLearningSystem",
                "category": ToolCategory.USER_PREFERENCES,
                "keywords": ["preferences", "learning", "user_behavior"],
                "contexts": ["user_experience", "personalization"],
                "user_preference_sensitive": True,
                "vision_alignment_required": False,
            },
            "pattern_recognition_system.py": {
                "class": "PatternRecognitionSystem",
                "category": ToolCategory.PATTERN_RECOGNITION,
                "keywords": ["patterns", "recognition", "learning", "behavior"],
                "contexts": ["pattern_analysis", "learning"],
                "user_preference_sensitive": True,
                "vision_alignment_required": False,
            },
        }

        for file_name, config in core_tool_mappings.items():
            file_path = core_path / file_name
            if file_path.exists():
                # Convert CamelCase class name to snake_case tool name
                class_name: str = config["class"]  # type: ignore[assignment]
                tool_name = ""
                for i, char in enumerate(class_name):
                    # char is automatically typed as str from enumerate(string)
                    if char.isupper() and i > 0:
                        tool_name += "_"
                    tool_name += char.lower()
                tools[tool_name] = ToolMetadata(
                    name=tool_name,
                    category=config["category"],  # type: ignore[arg-type]
                    module_path=f"ai_onboard.core.{file_path.stem}",
                    class_name=config["class"],  # type: ignore[arg-type]
                    description=f"Core tool: {config['class']}",
                    keywords=config["keywords"],  # type: ignore[arg-type]
                    contexts=config["contexts"],  # type: ignore[arg-type]
                    patterns=self._generate_patterns_from_keywords(config["keywords"]),  # type: ignore[arg-type]
                    user_preference_sensitive=config.get(
                        "user_preference_sensitive", False
                    ),  # type: ignore[arg-type]
                    vision_alignment_required=config.get(
                        "vision_alignment_required", False
                    ),  # type: ignore[arg-type]
                )

        return tools

    def _discover_vision_tools(self) -> Dict[str, ToolMetadata]:
        """Discover vision and alignment tools."""

        tools = {}

        # Vision-related tools
        vision_tools = {
            "vision_guardian": {
                "category": ToolCategory.VISION_ALIGNMENT,
                "keywords": ["vision", "alignment", "guardian", "validation"],
                "contexts": ["vision_management", "alignment_check"],
                "vision_alignment_required": True,
                "gate_requirements": ["vision_check", "alignment_gate"],
            },
            "charter_management": {
                "category": ToolCategory.CHARTER_MANAGEMENT,
                "keywords": ["charter", "project", "goals", "objectives"],
                "contexts": ["project_management", "charter_creation"],
                "vision_alignment_required": True,
                "gate_requirements": ["charter_gate"],
            },
            "interrogation_system": {
                "category": ToolCategory.INTERROGATION,
                "keywords": ["interrogate", "questions", "clarification"],
                "contexts": ["vision_clarification", "requirement_gathering"],
                "vision_alignment_required": True,
                "gate_requirements": ["interrogation_gate"],
            },
        }

        for tool_name, config in vision_tools.items():
            tools[tool_name] = ToolMetadata(
                name=tool_name,
                category=config["category"],  # type: ignore[arg-type]
                module_path=f"ai_onboard.core.{tool_name}",
                description=f"Vision tool: {tool_name}",
                keywords=config["keywords"],  # type: ignore[arg-type]
                contexts=config["contexts"],  # type: ignore[arg-type]
                patterns=self._generate_patterns_from_keywords(config["keywords"]),  # type: ignore[arg-type]
                gate_requirements=config.get("gate_requirements", []),  # type: ignore[arg-type]
                vision_alignment_required=config.get(
                    "vision_alignment_required", False
                ),  # type: ignore[arg-type]
            )

        return tools

    def _discover_safety_tools(self) -> Dict[str, ToolMetadata]:
        """Discover safety and validation tools."""

        tools = {}

        safety_tools = {
            "gate_system": {
                "category": ToolCategory.GATE_SYSTEM,
                "keywords": ["gate", "safety", "validation", "checkpoint"],
                "contexts": ["safety_checks", "validation"],
                "gate_requirements": ["safety_gate"],
                "risk_level": "critical",
            },
            "automatic_error_prevention": {
                "category": ToolCategory.ERROR_PREVENTION,
                "keywords": ["error", "prevention", "automatic", "safety"],
                "contexts": ["error_prevention", "safety"],
                "user_preference_sensitive": True,
            },
            "ultra_safe_cleanup": {
                "category": ToolCategory.CLEANUP_SAFETY,
                "keywords": ["cleanup", "safe", "ultra_safe", "deletion"],
                "contexts": ["cleanup", "file_management"],
                "gate_requirements": ["cleanup_gate"],
                "risk_level": "high",
            },
        }

        for tool_name, config in safety_tools.items():
            tools[tool_name] = ToolMetadata(
                name=tool_name,
                category=config["category"],  # type: ignore[arg-type]
                module_path=f"ai_onboard.core.{tool_name}",
                description=f"Safety tool: {tool_name}",
                keywords=config["keywords"],  # type: ignore[arg-type]
                contexts=config["contexts"],  # type: ignore[arg-type]
                patterns=self._generate_patterns_from_keywords(config["keywords"]),  # type: ignore[arg-type]
                gate_requirements=config.get("gate_requirements", []),  # type: ignore[arg-type]
                user_preference_sensitive=config.get(
                    "user_preference_sensitive", False
                ),  # type: ignore[arg-type]
                risk_level=config.get("risk_level", "low"),  # type: ignore[arg-type]
            )

        return tools

    def _discover_ux_tools(self) -> Dict[str, ToolMetadata]:
        """Discover user experience tools."""

        tools = {}

        ux_tools = {
            "conversation_analysis": {
                "category": ToolCategory.CONVERSATION_ANALYSIS,
                "keywords": ["conversation", "analysis", "patterns", "behavior"],
                "contexts": ["conversation_analysis", "user_behavior"],
                "user_preference_sensitive": True,
            },
            "ui_enhancement": {
                "category": ToolCategory.UI_ENHANCEMENT,
                "keywords": ["ui", "enhancement", "interface", "user_interface"],
                "contexts": ["ui_development", "user_experience"],
                "user_preference_sensitive": True,
            },
        }

        for tool_name, config in ux_tools.items():
            tools[tool_name] = ToolMetadata(
                name=tool_name,
                category=config["category"],  # type: ignore[arg-type]
                module_path=f"ai_onboard.core.{tool_name}",
                description=f"UX tool: {tool_name}",
                keywords=config["keywords"],  # type: ignore[arg-type]
                contexts=config["contexts"],  # type: ignore[arg-type]
                patterns=self._generate_patterns_from_keywords(config["keywords"]),  # type: ignore[arg-type]
                user_preference_sensitive=config.get(
                    "user_preference_sensitive", False
                ),  # type: ignore[arg-type]
            )

        return tools

    def _discover_project_management_tools(self) -> Dict[str, ToolMetadata]:
        """Discover project management tools."""

        tools = {}

        pm_tools = {
            "wbs_management": {
                "category": ToolCategory.WBS_MANAGEMENT,
                "keywords": ["wbs", "work_breakdown", "tasks", "project_plan"],
                "contexts": ["project_management", "task_management"],
                "vision_alignment_required": True,
            },
            "task_execution_gate": {
                "category": ToolCategory.TASK_EXECUTION,
                "keywords": ["task", "execution", "gate", "workflow"],
                "contexts": ["task_execution", "workflow_management"],
                "gate_requirements": ["task_gate"],
            },
        }

        for tool_name, config in pm_tools.items():
            tools[tool_name] = ToolMetadata(
                name=tool_name,
                category=config["category"],  # type: ignore[arg-type]
                module_path=f"ai_onboard.core.{tool_name}",
                description=f"PM tool: {tool_name}",
                keywords=config["keywords"],  # type: ignore[arg-type]
                contexts=config["contexts"],  # type: ignore[arg-type]
                patterns=self._generate_patterns_from_keywords(config["keywords"]),  # type: ignore[arg-type]
                gate_requirements=config.get("gate_requirements", []),  # type: ignore[arg-type]
                user_preference_sensitive=config.get(
                    "user_preference_sensitive", False
                ),  # type: ignore[arg-type]
                vision_alignment_required=config.get(
                    "vision_alignment_required", False
                ),  # type: ignore[arg-type]
            )

        return tools

    def _discover_ai_agent_tools(self) -> Dict[str, ToolMetadata]:
        """Discover AI agent orchestration tools."""

        tools = {}

        ai_tools = {
            "ai_agent_orchestration": {
                "category": ToolCategory.AI_AGENT_ORCHESTRATION,
                "keywords": [
                    "ai_agent",
                    "orchestration",
                    "coordination",
                    "collaboration",
                ],
                "contexts": ["ai_agent_management", "orchestration"],
                "vision_alignment_required": True,
                "gate_requirements": ["ai_agent_gate"],
            },
            "decision_pipeline": {
                "category": ToolCategory.DECISION_PIPELINE,
                "keywords": ["decision", "pipeline", "workflow", "process"],
                "contexts": ["decision_making", "workflow"],
                "vision_alignment_required": True,
            },
            "intelligent_monitoring": {
                "category": ToolCategory.INTELLIGENT_MONITORING,
                "keywords": ["monitoring", "intelligent", "proactive", "surveillance"],
                "contexts": ["monitoring", "proactive_analysis"],
                "user_preference_sensitive": True,
            },
        }

        for tool_name, config in ai_tools.items():
            tools[tool_name] = ToolMetadata(
                name=tool_name,
                category=config["category"],  # type: ignore[arg-type]
                module_path=f"ai_onboard.core.{tool_name}",
                description=f"AI tool: {tool_name}",
                keywords=config["keywords"],  # type: ignore[arg-type]
                contexts=config["contexts"],  # type: ignore[arg-type]
                patterns=self._generate_patterns_from_keywords(config["keywords"]),  # type: ignore[arg-type]
                gate_requirements=config.get("gate_requirements", []),  # type: ignore[arg-type]
                user_preference_sensitive=config.get(
                    "user_preference_sensitive", False
                ),  # type: ignore[arg-type]
                vision_alignment_required=config.get(
                    "vision_alignment_required", False
                ),  # type: ignore[arg-type]
            )

        return tools

    def _categorize_tools(
        self, tools: Dict[str, ToolMetadata]
    ) -> Dict[ToolCategory, List[ToolMetadata]]:
        """Categorize tools by their categories."""

        categorized: Dict[ToolCategory, List[ToolMetadata]] = {}
        for tool in tools.values():
            if tool.category not in categorized:
                categorized[tool.category] = []
            categorized[tool.category].append(tool)

        return categorized

    def _determine_cli_category(self, name: str, obj: Any) -> ToolCategory:
        """Determine the category of a CLI command."""

        name_lower = name.lower()

        if any(
            pattern in name_lower
            for pattern in ["vision", "charter", "align", "interrogate"]
        ):
            return ToolCategory.VISION_ALIGNMENT
        elif any(pattern in name_lower for pattern in ["cleanup", "safe", "gate"]):
            return ToolCategory.SAFETY_CHECKS
        elif any(pattern in name_lower for pattern in ["wbs", "task", "progress"]):
            return ToolCategory.METRICS_ANALYSIS
        elif any(pattern in name_lower for pattern in ["ui", "ux", "visual"]):
            return ToolCategory.UI_ENHANCEMENT
        elif any(pattern in name_lower for pattern in ["ai_agent", "orchestration"]):
            return ToolCategory.AI_AGENT_ORCHESTRATION
        else:
            return ToolCategory.CODE_QUALITY  # Default category

    def _extract_cli_keywords(self, name: str, obj: Any) -> List[str]:
        """Extract keywords from CLI command name and function."""

        keywords = []
        name_lower = name.lower()

        # Extract from name
        if "add_" in name_lower:
            keywords.append("add")
        if "handle_" in name_lower:
            keywords.append("handle")
        if "command" in name_lower:
            keywords.append("command")

        # Extract from function docstring if available
        if hasattr(obj, "__doc__") and obj.__doc__:
            doc_lower = obj.__doc__.lower()
            for word in ["analyze", "manage", "track", "monitor", "validate", "check"]:
                if word in doc_lower:
                    keywords.append(word)

        return keywords

    def _extract_cli_patterns(self, name: str) -> List[str]:
        """Extract patterns from CLI command name."""

        patterns = []
        name_lower = name.lower()

        # Generate patterns based on name structure
        if "add_" in name_lower:
            patterns.append(f"add.*{name_lower.replace('add_', '')}")
        if "handle_" in name_lower:
            patterns.append(f"handle.*{name_lower.replace('handle_', '')}")

        return patterns

    def _determine_cli_gates(self, name: str) -> List[str]:
        """Determine required gates for CLI commands."""

        gates = []
        name_lower = name.lower()

        if any(pattern in name_lower for pattern in ["cleanup", "delete", "remove"]):
            gates.append("cleanup_gate")
        if any(pattern in name_lower for pattern in ["vision", "charter", "align"]):
            gates.append("vision_gate")
        if any(pattern in name_lower for pattern in ["ai_agent", "orchestration"]):
            gates.append("ai_agent_gate")

        return gates

    def _requires_vision_alignment(self, name: str) -> bool:
        """Determine if CLI command requires vision alignment."""

        name_lower = name.lower()
        vision_keywords = ["vision", "charter", "align", "interrogate", "plan", "goal"]

        return any(keyword in name_lower for keyword in vision_keywords)

    def _generate_patterns_from_keywords(self, keywords: List[str]) -> List[str]:
        """Generate regex patterns from keywords."""

        patterns = []
        for keyword in keywords:
            # Create pattern variations
            patterns.append(f".*{keyword}.*")
            patterns.append(f"{keyword}.*")
            patterns.append(f".*{keyword}")

        return patterns


def get_comprehensive_tool_discovery(root_path: Path) -> ComprehensiveToolDiscovery:
    """Get singleton instance of comprehensive tool discovery."""
    if not hasattr(get_comprehensive_tool_discovery, "_instance"):
        get_comprehensive_tool_discovery._instance = ComprehensiveToolDiscovery(root_path)  # type: ignore[attr-defined]
    return cast(ComprehensiveToolDiscovery, get_comprehensive_tool_discovery._instance)  # type: ignore[attr-defined]
