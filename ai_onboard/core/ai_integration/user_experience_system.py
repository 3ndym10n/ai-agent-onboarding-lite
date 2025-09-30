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
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from ..base.shared_types import (
    CommandInfo,
    DesignValidation,
    SmartSuggestion,
    UserExpertiseLevel,
)
from .clarification_question_system import get_clarification_question_engine
from .conversation_memory_system import get_conversation_memory_manager
from .natural_language_intent_parser import get_natural_language_intent_parser
from .progressive_disclosure_ui import get_progressive_disclosure_engine
from .user_journey_mapper import get_user_journey_mapper
from .user_preference_learning import get_user_preference_learning_system

# Note: UserExpertiseLevel, CommandInfo, SmartSuggestion now imported from shared_types


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
    OPTIMIZATION = "optimization"
    AI_SYSTEMS = "ai_systems"
    LEARNING = "learning"
    CORE = "core"


class UserExperienceSystem:
    """Unified system for user experience enhancements."""

    def __init__(self, root: Path):
        self.root = root
        self.data_dir = root / ".ai_onboard" / "ux_system"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Integration with existing systems
        self.preference_system = get_user_preference_learning_system(root)

        # New anti-drift components
        self.intent_parser = get_natural_language_intent_parser(root)
        self.memory_manager = get_conversation_memory_manager(root)
        self.disclosure_engine = get_progressive_disclosure_engine(root)
        self.question_engine = get_clarification_question_engine(root)
        self.journey_mapper = get_user_journey_mapper(root)

        # Core components
        self.command_registry: Dict[str, CommandInfo] = {}
        self.user_usage_patterns: Dict[str, Dict[str, Any]] = {}

        # Configuration
        self.config = self._load_config()

        # Initialize
        self._initialize_command_registry()

    def _load_config(self) -> Any:
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
            except (ValueError, TypeError, AttributeError):
                # Handle common runtime errors
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

        # Get user profile from preference system
        if user_id not in self.preference_system.user_profiles:
            return []
        profile = self.preference_system.user_profiles[user_id]

        expertise_level = self._detect_user_expertise(user_id)

        suggestions = []

        # Extract recent commands from interaction history
        recent_commands = []
        for interaction in list(profile.interaction_history)[
            -10:
        ]:  # Last 10 interactions
            # Check if this is a command execution interaction
            from .user_preference_learning import InteractionType

            if (
                hasattr(interaction, "interaction_type")
                and interaction.interaction_type == InteractionType.COMMAND_EXECUTION
            ):
                # Extract command from context
                if hasattr(interaction, "context") and isinstance(
                    interaction.context, dict
                ):
                    command = interaction.context.get("command")
                    if command and command not in recent_commands:
                        recent_commands.append(command)

        if "charter" in recent_commands and "plan" not in recent_commands:
            suggestions.append(
                SmartSuggestion(
                    command="plan",
                    reason="You've created a charter - next step is generating a plan",
                    confidence=0.9,
                    category=CommandCategory.PROJECT.value,
                    next_steps=["python -m ai_onboard plan"],
                )
            )

        if "plan" in recent_commands and "align" not in recent_commands:
            suggestions.append(
                SmartSuggestion(
                    command="align",
                    reason="Check if your plan aligns with your charter",
                    confidence=0.8,
                    category=CommandCategory.PROJECT.value,
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
                    category=CommandCategory.QUALITY.value,
                    next_steps=["python -m ai_onboard validate"],
                )
            )

        # Suggest simpler alternatives when complex commands fail
        complex_commands = [cmd for cmd in recent_commands if "complex" in cmd.lower()]
        if complex_commands and any(
            cmd for cmd in recent_commands if "simple" in cmd.lower()
        ):
            suggestions.append(
                SmartSuggestion(
                    command="simple_validate",
                    reason="Consider simpler validation approaches after complex command failures",
                    confidence=0.8,
                    category=CommandCategory.QUALITY.value,
                    next_steps=["python -m ai_onboard validate --simple"],
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
            "category": cmd_info.category,
            "expertise_required": cmd_info.expertise_level.value,
        }

        # Add expertise-appropriate content
        if expertise in [UserExpertiseLevel.BEGINNER, UserExpertiseLevel.INTERMEDIATE]:
            help_content["prerequisites"] = cmd_info.prerequisites  # type: ignore[assignment]
            help_content["related_commands"] = cmd_info.related_commands  # type: ignore[assignment]

        if expertise == UserExpertiseLevel.BEGINNER:
            help_content["getting_started"] = self._get_getting_started_guidance(  # type: ignore[assignment]
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
        recent_commands_raw: Union[List[str], Any] = user_prefs.get(
            "recent_commands", []
        )
        recent_commands: List[str] = (
            recent_commands_raw if isinstance(recent_commands_raw, list) else []
        )
        command_count = len(recent_commands) if isinstance(recent_commands, list) else 0  # type: ignore[arg-type]
        advanced_commands = user_prefs.get("advanced_commands_used", 0)

        if command_count < 5:
            return UserExpertiseLevel.BEGINNER
        elif command_count < 20 or (
            isinstance(advanced_commands, (int, float)) and advanced_commands < 3
        ):  # type: ignore[operator]
            return UserExpertiseLevel.INTERMEDIATE
        elif isinstance(advanced_commands, (int, float)) and advanced_commands < 10:
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

    def record_command_usage(
        self,
        user_id: str,
        command: str,
        success: bool,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Record command usage for learning user patterns."""
        # Delegate to preference learning system
        from .user_preference_learning import InteractionType

        base_context = {
            "command": command,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }
        if context:
            base_context.update(context)
        self.preference_system.record_user_interaction(
            user_id,
            InteractionType.COMMAND_EXECUTION,
            base_context,
            satisfaction_score=1.0 if success else 0.5,
        )

    def get_project_status(self, user_id: str) -> Dict[str, Any]:
        """Get simplified project status for dashboard."""
        # Check for key project files
        charter_exists = (self.root / ".ai_onboard" / "charter.json").exists()
        plan_exists = (self.root / ".ai_onboard" / "plan.json").exists()

        user_prefs = self.preference_system.get_user_preferences(user_id)
        recent_commands: List[str] = user_prefs.get("recent_commands", [])  # type: ignore[assignment]

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

    def format_output(
        self, text: str, style: str = "default", user_id: str = "default"
    ) -> str:
        """Format text output with styling."""
        # Simple text formatting - can be enhanced with actual colors later
        style_map = {
            "primary": "🔵",
            "secondary": "⚪",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "info": "ℹ️",
            "default": "",
        }
        prefix = style_map.get(style, "")
        return f"{prefix} {text}" if prefix else text

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information."""
        return self.preference_system.get_user_preferences(user_id)

    def get_filtered_commands(
        self, user_id: str, category: Optional[Union[str, CommandCategory]] = None
    ) -> List[CommandInfo]:
        """Get filtered command list based on user preferences and category."""
        all_commands = list(self.command_registry.values())

        if category:
            # Convert CommandCategory to string if needed
            category_str = (
                category.value if isinstance(category, CommandCategory) else category
            )
            # Filter by category if specified
            filtered = [cmd for cmd in all_commands if cmd.category == category_str]
        else:
            filtered = all_commands

        # Sort by user preferences/recent usage
        user_prefs = self.preference_system.get_user_preferences(user_id)
        recent_commands_raw: Union[List[str], Any] = user_prefs.get(
            "recent_commands", []
        )
        recent_commands: Set[str] = (
            set(recent_commands_raw) if isinstance(recent_commands_raw, list) else set()
        )

        # Boost recently used commands
        def sort_key(cmd):
            name = cmd.name
            return (0 if name in recent_commands else 1, name)

        return sorted(filtered, key=sort_key)

    def get_command_suggestions(
        self, user_id: str, context: str = ""
    ) -> List[SmartSuggestion]:
        """Get smart command suggestions for the user."""
        return self.get_smart_suggestions(user_id)

    def create_command_help(self, command: str, user_id: str) -> str:
        """Create formatted help text for a command."""
        cmd_info = self.command_registry.get(command)
        if not cmd_info:
            return f"Command '{command}' not found."

        help_text = f"Help for '{command}':\n"
        help_text += f"Description: {cmd_info.description}\n"

        help_text += f"Usage: {cmd_info.usage_example}\n"

        if cmd_info.tags:
            help_text += f"Tags: {', '.join(cmd_info.tags)}\n"

        return help_text

    def get_progress_bar(
        self, current: int, total: int, width: int = 40, user_id: str = "default"
    ) -> str:
        """Create a progress bar string representation."""
        # Calculate percentage
        percentage = (current / total * 100) if total > 0 else 0

        # Create progress bar
        filled = int(width * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (width - filled)

        return f"{bar} {percentage:.1f}%"

    def parse_user_intent(
        self, user_request: str, user_id: str = "default"
    ) -> Dict[str, Any]:
        """Parse user intent using the natural language intent parser."""
        try:
            result = self.intent_parser.parse_user_intent(user_request, user_id)
            return {
                "success": True,
                "project_type": result.project_type,
                "complexity_level": result.complexity_level,
                "target_audience": result.target_audience,
                "primary_features": result.primary_features,
                "confidence": result.confidence_score,
                "clarification_questions": result.clarification_questions,
                "interpreted_intent": result.interpreted_intent,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "clarification_questions": [
                    "Could you provide more details about what you want to build?"
                ],
            }

    def get_simplified_interface(
        self, user_id: str, context: str = "general"
    ) -> Dict[str, Any]:
        """Get a simplified interface configuration for the user."""
        try:
            return self.disclosure_engine.get_simplified_interface(user_id, context)
        except Exception as e:
            return {
                "error": str(e),
                "elements": [],
                "user_expertise": "intermediate",
            }

    def get_clarification_questions(
        self, user_request: str, user_id: str, context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Get clarification questions for ambiguous requests."""
        try:
            questions = self.question_engine.generate_clarification_questions(
                user_request, user_id, context or {}
            )
            return [q.question_text for q in questions]
        except Exception as e:
            return ["Could you provide more details about your project?"]

    def get_recommended_journey(
        self, user_request: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a recommended user journey for the request."""
        try:
            journey = self.journey_mapper.get_recommended_journey(user_request, user_id)
            if journey:
                return {
                    "journey_id": journey.journey_id,
                    "name": journey.name,
                    "description": journey.description,
                    "steps": [
                        {
                            "title": step.title,
                            "description": step.description,
                            "estimated_time": step.estimated_time_minutes,
                            "complexity": step.complexity.value,
                        }
                        for step in journey.get_steps_for_user(
                            self._detect_user_expertise(user_id)
                        )
                    ],
                }
        except Exception as e:
            pass
        return None

    def start_conversation_memory(self, user_id: str, initial_request: str) -> str:
        """Start a conversation with memory management."""
        try:
            return self.memory_manager.start_conversation(user_id, initial_request)
        except Exception as e:
            return f"conv_{int(time.time())}_{user_id[:8]}"  # Fallback

    def get_conversation_context(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation context with memory."""
        try:
            return self.memory_manager.get_conversation_context(conversation_id)
        except Exception as e:
            return {"error": str(e)}

    def get_progressive_help(self, user_id: str, current_action: str) -> Dict[str, Any]:
        """Get progressive help adapted to user expertise."""
        try:
            return self.disclosure_engine.get_progressive_help(user_id, current_action)
        except Exception as e:
            return {
                "help_level": "basic",
                "show_tips": True,
                "show_examples": False,
                "show_advanced": False,
            }

    def update_user_feedback(
        self,
        user_id: str,
        element_id: str,
        success: bool,
        difficulty_rating: Optional[int] = None,
    ) -> None:
        """Update user feedback for continuous improvement."""
        try:
            self.disclosure_engine.update_user_feedback(
                user_id, element_id, "interaction", success, difficulty_rating
            )
        except Exception:
            pass  # Don't fail on feedback errors


# Global instance
_user_experience_system: Optional[UserExperienceSystem] = None


def get_user_experience_system(root: Path) -> UserExperienceSystem:
    """Get the global user experience system instance."""
    global _user_experience_system
    if _user_experience_system is None:
        _user_experience_system = UserExperienceSystem(root)
    return _user_experience_system
