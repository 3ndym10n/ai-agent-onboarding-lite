"""
Unified User Experience System - Consolidated UX enhancements for AI-Onboard.

This module combines the best features from multiple UX systems into a single,
simplified system that provides:
- Adaptive help and smart suggestions
- Progressive command discovery
- Visual feedback and status display
- Design validation for UI/UX projects
- User preference integration
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .user_preference_learning import get_user_preference_learning_system


class UserExpertiseLevel(Enum):
    """User expertise levels for adaptive interface."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class InterfaceMode(Enum):
    """Interface modes for command display."""

    SIMPLE = "simple"
    STANDARD = "standard"
    COMPLETE = "complete"
    EXPERT = "expert"


class CommandCategory(Enum):
    """Categories for organizing commands."""

    PROJECT = "project"
    DEVELOPMENT = "development"
    QUALITY = "quality"
    AI_INTEGRATION = "ai_integration"
    ADVANCED = "advanced"


@dataclass
class CommandInfo:
    """Information about a CLI command."""

    name: str
    category: CommandCategory
    description: str
    usage_example: str
    expertise_level: UserExpertiseLevel = UserExpertiseLevel.BEGINNER
    tags: List[str] = field(default_factory=list)
    related_commands: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class SmartSuggestion:
    """A contextual suggestion for the user."""

    command: str
    reason: str
    confidence: float
    category: CommandCategory
    next_steps: List[str] = field(default_factory=list)


@dataclass
class DesignValidation:
    """Design validation result."""

    score: float  # 0.0-1.0
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    accessibility_score: float = 0.0
    consistency_score: float = 0.0


class UserExperienceSystem:
    """Unified system for user experience enhancements."""

    def __init__(self, root: Path):
        self.root = root
        self.data_dir = root / ".ai_onboard" / "ux_system"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Integration with existing systems
        self.preference_system = get_user_preference_learning_system(root)

        # Core components
        self.command_registry: Dict[str, CommandInfo] = {}
        self.user_usage_patterns: Dict[str, Dict[str, Any]] = {}

        # Configuration
        self.config = self._load_config()

        # Initialize
        self._initialize_command_registry()

    def _load_config(self) -> Dict[str, Any]:
        """Load simplified UX configuration."""
        config_file = self.data_dir / "ux_config.json"

        default_config = {
            "enable_smart_suggestions": True,
            "enable_adaptive_help": True,
            "enable_design_validation": True,
            "suggestion_confidence_threshold": 0.7,
            "max_suggestions": 3,
            "auto_detect_expertise": True,
        }

        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception:
                pass

        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def _initialize_command_registry(self):
        """Initialize registry of core commands with their metadata."""
        commands = [
            # Core Project Commands
            CommandInfo(
                name="charter",
                category=CommandCategory.PROJECT,
                description="Create project charter and vision",
                usage_example="python -m ai_onboard charter",
                expertise_level=UserExpertiseLevel.BEGINNER,
                tags=["project", "planning", "vision"],
            ),
            CommandInfo(
                name="plan",
                category=CommandCategory.PROJECT,
                description="Generate project plan from charter",
                usage_example="python -m ai_onboard plan",
                expertise_level=UserExpertiseLevel.BEGINNER,
                related_commands=["charter", "align"],
                prerequisites=["charter"],
                tags=["project", "planning"],
            ),
            CommandInfo(
                name="align",
                category=CommandCategory.PROJECT,
                description="Check alignment with project vision",
                usage_example="python -m ai_onboard align",
                expertise_level=UserExpertiseLevel.INTERMEDIATE,
                prerequisites=["charter", "plan"],
                tags=["project", "alignment", "validation"],
            ),
            CommandInfo(
                name="validate",
                category=CommandCategory.QUALITY,
                description="Validate project progress and quality",
                usage_example="python -m ai_onboard validate",
                expertise_level=UserExpertiseLevel.INTERMEDIATE,
                prerequisites=["plan"],
                tags=["validation", "quality"],
            ),
            # Development Commands
            CommandInfo(
                name="cleanup",
                category=CommandCategory.DEVELOPMENT,
                description="Safely clean up non-critical files",
                usage_example="python -m ai_onboard cleanup --dry-run",
                expertise_level=UserExpertiseLevel.INTERMEDIATE,
                tags=["cleanup", "maintenance"],
            ),
            CommandInfo(
                name="code-quality",
                category=CommandCategory.QUALITY,
                description="Analyze and validate code quality",
                usage_example="python -m ai_onboard code-quality syntax",
                expertise_level=UserExpertiseLevel.INTERMEDIATE,
                tags=["quality", "analysis"],
            ),
            # AI Integration Commands
            CommandInfo(
                name="cursor",
                category=CommandCategory.AI_INTEGRATION,
                description="Cursor AI integration tools",
                usage_example="python -m ai_onboard cursor setup",
                expertise_level=UserExpertiseLevel.ADVANCED,
                tags=["ai", "integration", "cursor"],
            ),
            CommandInfo(
                name="ai-collaboration",
                category=CommandCategory.AI_INTEGRATION,
                description="AI agent collaboration management",
                usage_example="python -m ai_onboard ai-collaboration register",
                expertise_level=UserExpertiseLevel.ADVANCED,
                tags=["ai", "collaboration"],
            ),
        ]

        for cmd in commands:
            self.command_registry[cmd.name] = cmd

    def get_smart_suggestions(
        self, user_id: str, context: str = ""
    ) -> List[SmartSuggestion]:
        """Get contextual command suggestions for the user."""
        if not self.config["enable_smart_suggestions"]:
            return []

        # Get user patterns from preference system
        user_prefs = self.preference_system.get_user_preferences(user_id)
        expertise_level = self._detect_user_expertise(user_id)

        suggestions = []

        # Suggest next logical steps based on completed commands
        recent_commands = user_prefs.get("recent_commands", [])

        if "charter" in recent_commands and "plan" not in recent_commands:
            suggestions.append(
                SmartSuggestion(
                    command="plan",
                    reason="You've created a charter - next step is generating a plan",
                    confidence=0.9,
                    category=CommandCategory.PROJECT,
                    next_steps=["python -m ai_onboard plan"],
                )
            )

        if "plan" in recent_commands and "align" not in recent_commands:
            suggestions.append(
                SmartSuggestion(
                    command="align",
                    reason="Check if your plan aligns with your charter",
                    confidence=0.8,
                    category=CommandCategory.PROJECT,
                    next_steps=["python -m ai_onboard align"],
                )
            )

        # Suggest quality checks for active development
        if any(cmd in recent_commands for cmd in ["analyze", "plan"]):
            suggestions.append(
                SmartSuggestion(
                    command="validate",
                    reason="Run validation to ensure quality standards",
                    confidence=0.7,
                    category=CommandCategory.QUALITY,
                    next_steps=["python -m ai_onboard validate"],
                )
            )

        # Filter by confidence threshold and limit
        suggestions = [
            s
            for s in suggestions
            if s.confidence >= self.config["suggestion_confidence_threshold"]
        ]
        return suggestions[: self.config["max_suggestions"]]

    def get_adaptive_help(self, command: str, user_id: str) -> Dict[str, Any]:
        """Get adaptive help content based on user expertise."""
        if not self.config["enable_adaptive_help"]:
            return {"help": f"Help for {command}", "examples": []}

        expertise = self._detect_user_expertise(user_id)
        cmd_info = self.command_registry.get(command)

        if not cmd_info:
            return {"help": f"Command '{command}' not found", "examples": []}

        help_content = {
            "description": cmd_info.description,
            "usage": cmd_info.usage_example,
            "category": cmd_info.category.value,
            "expertise_required": cmd_info.expertise_level.value,
        }

        # Add expertise-appropriate content
        if expertise in [UserExpertiseLevel.BEGINNER, UserExpertiseLevel.INTERMEDIATE]:
            help_content["prerequisites"] = cmd_info.prerequisites
            help_content["related_commands"] = cmd_info.related_commands

        if expertise == UserExpertiseLevel.BEGINNER:
            help_content["getting_started"] = self._get_getting_started_guidance(
                command
            )

        return help_content

    def validate_design(
        self, description: str, screenshot_path: Optional[Path] = None
    ) -> DesignValidation:
        """Validate design decisions for UI/UX projects."""
        if not self.config["enable_design_validation"]:
            return DesignValidation(score=0.5, issues=["Design validation disabled"])

        # Basic design validation logic
        issues = []
        recommendations = []
        score = 0.8  # Default reasonable score

        # Check for common design issues in description
        if "color" in description.lower():
            if "contrast" not in description.lower():
                issues.append("Consider color contrast for accessibility")
                recommendations.append(
                    "Ensure color contrast meets WCAG guidelines (4.5:1 minimum)"
                )

        if "font" in description.lower() or "text" in description.lower():
            if "readable" not in description.lower():
                issues.append("Ensure text readability")
                recommendations.append("Use readable font sizes (16px+ for body text)")

        if "navigation" in description.lower():
            recommendations.append("Ensure navigation is intuitive and consistent")

        # Adjust score based on issues
        score -= len(issues) * 0.1
        score = max(0.0, min(1.0, score))

        return DesignValidation(
            score=score,
            issues=issues,
            recommendations=recommendations,
            accessibility_score=0.8 if not issues else 0.6,
            consistency_score=0.8,
        )

    def _detect_user_expertise(self, user_id: str) -> UserExpertiseLevel:
        """Detect user expertise level from usage patterns."""
        if not self.config["auto_detect_expertise"]:
            return UserExpertiseLevel.INTERMEDIATE

        user_prefs = self.preference_system.get_user_preferences(user_id)
        command_count = len(user_prefs.get("recent_commands", []))
        advanced_commands = user_prefs.get("advanced_commands_used", 0)

        if command_count < 5:
            return UserExpertiseLevel.BEGINNER
        elif command_count < 20 or advanced_commands < 3:
            return UserExpertiseLevel.INTERMEDIATE
        elif advanced_commands < 10:
            return UserExpertiseLevel.ADVANCED
        else:
            return UserExpertiseLevel.EXPERT

    def _get_getting_started_guidance(self, command: str) -> List[str]:
        """Get getting started guidance for beginners."""
        guidance_map = {
            "charter": [
                "Start by defining what problem your project solves",
                "Identify your target users and their needs",
                "Set clear, measurable success criteria",
            ],
            "plan": [
                "Break down your project into manageable tasks",
                "Identify dependencies between tasks",
                "Set realistic timelines for completion",
            ],
            "align": [
                "Review your plan against your charter",
                "Check if your current work matches your vision",
                "Make adjustments if needed",
            ],
        }
        return guidance_map.get(command, ["Run the command to get started"])

    def record_command_usage(self, user_id: str, command: str, success: bool):
        """Record command usage for learning user patterns."""
        # Delegate to preference learning system
        from .user_preference_learning import InteractionType

        context = {
            "command": command,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }
        self.preference_system.record_user_interaction(
            user_id,
            InteractionType.COMMAND_EXECUTION,
            context,
            satisfaction_score=1.0 if success else 0.5,
        )

    def get_project_status(self, user_id: str) -> Dict[str, Any]:
        """Get simplified project status for dashboard."""
        # Check for key project files
        charter_exists = (self.root / ".ai_onboard" / "charter.json").exists()
        plan_exists = (self.root / ".ai_onboard" / "plan.json").exists()

        user_prefs = self.preference_system.get_user_preferences(user_id)
        recent_commands = user_prefs.get("recent_commands", [])

        status = {
            "project_setup": {
                "charter": "✅" if charter_exists else "❌",
                "plan": "✅" if plan_exists else "❌",
            },
            "recent_activity": recent_commands[-5:] if recent_commands else [],
            "suggestions": self.get_smart_suggestions(user_id),
            "expertise_level": self._detect_user_expertise(user_id).value,
        }

        return status


# Global instance
_user_experience_system: Optional[UserExperienceSystem] = None


def get_user_experience_system(root: Path) -> UserExperienceSystem:
    """Get the global user experience system instance."""
    global _user_experience_system
    if _user_experience_system is None:
        _user_experience_system = UserExperienceSystem(root)
    return _user_experience_system
