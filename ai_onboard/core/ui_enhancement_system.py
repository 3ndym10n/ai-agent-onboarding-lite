"""
UI Enhancement System (T18) - Comprehensive user interface and experience improvements.

This module provides intelligent UI enhancements that:
- Implement progressive disclosure for complex functionality
- Provide contextual guidance and smart suggestions
- Create intuitive command discovery and organization
- Enhance visual feedback and progress indication
- Personalize the interface based on user preferences and expertise
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


class CommandCategory(Enum):
    """Categories for organizing commands."""

    PROJECT = "project"  # charter, plan, align, validate, progress
    OPTIMIZATION = "optimization"  # kaizen, experiments, performance
    AI_SYSTEMS = "ai_systems"  # agent, collaboration, context, decision - pipeline
    DEVELOPMENT = "development"  # cursor, api, debug, metrics
    LEARNING = "learning"  # user - prefs, continuous - improvement, knowledge
    CORE = "core"  # Basic functionality
    ADVANCED = "advanced"  # Advanced / experimental features


class InterfaceMode(Enum):
    """Interface complexity modes."""

    SIMPLE = "simple"  # Essential commands only
    STANDARD = "standard"  # Most common commands
    COMPLETE = "complete"  # All commands visible
    EXPERT = "expert"  # Advanced shortcuts and power features


@dataclass
class CommandInfo:
    """Information about a CLI command."""

    name: str
    category: CommandCategory
    description: str
    usage_example: str
    expertise_level: UserExpertiseLevel
    frequency_score: float = 0.0  # How often users actually use this
    success_rate: float = 1.0  # How often it works without errors
    common_errors: List[str] = field(default_factory=list)
    related_commands: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class UserProfile:
    """Profile of user interface preferences and expertise."""

    user_id: str
    expertise_level: UserExpertiseLevel
    preferred_mode: InterfaceMode

    # Usage patterns
    command_usage_count: Dict[str, int] = field(default_factory=dict)
    last_used_commands: List[str] = field(default_factory=list)
    favorite_workflows: List[List[str]] = field(default_factory=list)

    # Preferences
    show_examples: bool = True
    show_progress_bars: bool = True
    use_colors: bool = True
    preferred_verbosity: str = "normal"  # quiet, normal, verbose

    # Learning
    completed_tutorials: Set[str] = field(default_factory=set)
    known_shortcuts: Set[str] = field(default_factory=set)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class CommandSuggestion:
    """A suggested command for the user."""

    command: str
    reason: str
    confidence: float
    context: str
    example: str


@dataclass
class UITheme:
    """Visual theme for the interface."""

    name: str
    primary_color: str
    secondary_color: str
    success_color: str
    warning_color: str
    error_color: str
    info_color: str

    # Icons (using Unicode)
    success_icon: str = "✅"
    warning_icon: str = "⚠️"
    error_icon: str = "❌"
    info_icon: str = "ℹ️"
    progress_icon: str = "🔄"
    completed_icon: str = "✨"


class UIEnhancementSystem:
    """Main system for UI enhancements and user experience improvements."""

    def __init__(self, root: Path):
        self.root = root
        self.data_dir = root / ".ai_onboard" / "ui_enhancements"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Components
        self.preference_system = get_user_preference_learning_system(root)

        # State
        self.user_profiles: Dict[str, UserProfile] = {}
        self.command_registry: Dict[str, CommandInfo] = {}
        self.ui_themes: Dict[str, UITheme] = {}

        # Configuration
        self.config = self._load_ui_config()

        # Initialize system
        self._initialize_command_registry()
        self._initialize_themes()
        self._load_user_profiles()

    def _load_ui_config(self) -> Dict[str, Any]:
        """Load UI configuration."""
        config_file = self.data_dir / "ui_config.json"

        default_config = {
            "default_theme": "modern",
            "enable_colors": True,
            "enable_progress_bars": True,
            "enable_suggestions": True,
            "enable_tutorials": True,
            "auto_detect_expertise": True,
            "suggestion_confidence_threshold": 0.7,
            "max_suggestions": 3,
            "command_history_limit": 50,
            "tutorial_completion_tracking": True,
        }

        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception:
                pass

        # Save default config
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def _initialize_command_registry(self):
        """Initialize the registry of available commands."""
        commands = [
            # Project Management
            CommandInfo(
                name="charter",
                category=CommandCategory.PROJECT,
                description="Create project charter and vision",
                usage_example="ai_onboard charter",
                expertise_level=UserExpertiseLevel.BEGINNER,
                tags=["project", "planning", "vision"],
            ),
            CommandInfo(
                name="plan",
                category=CommandCategory.PROJECT,
                description="Generate and manage project plans",
                usage_example="ai_onboard plan",
                expertise_level=UserExpertiseLevel.BEGINNER,
                related_commands=["charter", "align", "validate"],
                tags=["project", "planning", "tasks"],
            ),
            CommandInfo(
                name="align",
                category=CommandCategory.PROJECT,
                description="Align project with vision and goals",
                usage_example="ai_onboard align",
                expertise_level=UserExpertiseLevel.INTERMEDIATE,
                prerequisites=["charter", "plan"],
                tags=["project", "alignment", "validation"],
            ),
            CommandInfo(
                name="validate",
                category=CommandCategory.PROJECT,
                description="Validate project progress and quality",
                usage_example="ai_onboard validate",
                expertise_level=UserExpertiseLevel.INTERMEDIATE,
                prerequisites=["plan"],
                tags=["project", "validation", "quality"],
            ),
            CommandInfo(
                name="prompt",
                category=CommandCategory.PROJECT,
                description="Get project insights and progress",
                usage_example="ai_onboard prompt progress",
                expertise_level=UserExpertiseLevel.BEGINNER,
                tags=["project", "status", "insights"],
            ),
            # Optimization
            CommandInfo(
                name="kaizen",
                category=CommandCategory.OPTIMIZATION,
                description="Run manual improvement cycle",
                usage_example="ai_onboard kaizen",
                expertise_level=UserExpertiseLevel.INTERMEDIATE,
                tags=["optimization", "improvement", "manual"],
            ),
            CommandInfo(
                name="kaizen - auto",
                category=CommandCategory.OPTIMIZATION,
                description="Automated continuous improvement system",
                usage_example="ai_onboard kaizen - auto start",
                expertise_level=UserExpertiseLevel.ADVANCED,
                related_commands=["kaizen", "opt - experiments"],
                tags=["optimization", "automation", "continuous"],
            ),
            CommandInfo(
                name="opt - experiments",
                category=CommandCategory.OPTIMIZATION,
                description="Design and run optimization experiments",
                usage_example="ai_onboard opt - experiments design --name 'Performance Test'",
                expertise_level=UserExpertiseLevel.ADVANCED,
                related_commands=["kaizen - auto"],
                tags=["optimization", "experiments", "testing"],
            ),
            # AI Systems
            CommandInfo(
                name="ai - agent",
                category=CommandCategory.AI_SYSTEMS,
                description="AI agent collaboration and management",
                usage_example="ai_onboard ai - agent status",
                expertise_level=UserExpertiseLevel.INTERMEDIATE,
                tags=["ai", "agent", "collaboration"],
            ),
            CommandInfo(
                name="aaol",
                category=CommandCategory.AI_SYSTEMS,
                description="AI Agent Orchestration Layer",
                usage_example="ai_onboard aaol session create",
                expertise_level=UserExpertiseLevel.ADVANCED,
                related_commands=["ai - agent", "enhanced - context"],
                tags=["ai", "orchestration", "advanced"],
            ),
            CommandInfo(
                name="enhanced - context",
                category=CommandCategory.AI_SYSTEMS,
                description="Advanced conversation context management",
                usage_example="ai_onboard enhanced - context enhance",
                expertise_level=UserExpertiseLevel.ADVANCED,
                related_commands=["aaol", "decision - pipeline"],
                tags=["ai", "context", "conversation"],
            ),
            CommandInfo(
                name="decision - pipeline",
                category=CommandCategory.AI_SYSTEMS,
                description="Advanced agent decision processing",
                usage_example="ai_onboard decision - pipeline test",
                expertise_level=UserExpertiseLevel.EXPERT,
                related_commands=["enhanced - context", "aaol"],
                tags=["ai", "decision", "pipeline", "advanced"],
            ),
            # Development
            CommandInfo(
                name="cursor",
                category=CommandCategory.DEVELOPMENT,
                description="Cursor AI integration",
                usage_example="ai_onboard cursor init",
                expertise_level=UserExpertiseLevel.INTERMEDIATE,
                tags=["development", "cursor", "integration"],
            ),
            CommandInfo(
                name="api",
                category=CommandCategory.DEVELOPMENT,
                description="API server management",
                usage_example="ai_onboard api start",
                expertise_level=UserExpertiseLevel.ADVANCED,
                related_commands=["cursor"],
                tags=["development", "api", "server"],
            ),
            CommandInfo(
                name="unified - metrics",
                category=CommandCategory.DEVELOPMENT,
                description="Comprehensive metrics collection",
                usage_example="ai_onboard unified - metrics query",
                expertise_level=UserExpertiseLevel.ADVANCED,
                tags=["development", "metrics", "monitoring"],
            ),
            # Learning
            CommandInfo(
                name="user - prefs",
                category=CommandCategory.LEARNING,
                description="User preference learning and adaptation",
                usage_example="ai_onboard user - prefs summary --user me",
                expertise_level=UserExpertiseLevel.INTERMEDIATE,
                tags=["learning", "preferences", "personalization"],
            ),
            CommandInfo(
                name="continuous - improvement",
                category=CommandCategory.LEARNING,
                description="System learning and improvement",
                usage_example="ai_onboard continuous - improvement status",
                expertise_level=UserExpertiseLevel.ADVANCED,
                related_commands=["kaizen - auto", "user - prefs"],
                tags=["learning", "improvement", "system"],
            ),
        ]

        for cmd in commands:
            self.command_registry[cmd.name] = cmd

    def _initialize_themes(self):
        """Initialize UI themes."""
        themes = {
            "modern": UITheme(
                name="modern",
                primary_color="\033[94m",  # Blue
                secondary_color="\033[96m",  # Cyan
                success_color="\033[92m",  # Green
                warning_color="\033[93m",  # Yellow
                error_color="\033[91m",  # Red
                info_color="\033[95m",  # Magenta
            ),
            "classic": UITheme(
                name="classic",
                primary_color="\033[34m",  # Dark Blue
                secondary_color="\033[36m",  # Dark Cyan
                success_color="\033[32m",  # Dark Green
                warning_color="\033[33m",  # Dark Yellow
                error_color="\033[31m",  # Dark Red
                info_color="\033[35m",  # Dark Magenta
            ),
            "minimal": UITheme(
                name="minimal",
                primary_color="",  # No colors
                secondary_color="",
                success_color="",
                warning_color="",
                error_color="",
                info_color="",
                success_icon="[OK]",
                warning_icon="[WARN]",
                error_icon="[ERROR]",
                info_icon="[INFO]",
                progress_icon="[...]",
                completed_icon="[DONE]",
            ),
        }

        self.ui_themes = themes

    def _load_user_profiles(self):
        """Load user profiles from storage."""
        profiles_file = self.data_dir / "user_profiles.json"

        if profiles_file.exists():
            try:
                with open(profiles_file, "r") as f:
                    data = json.load(f)

                for user_id, profile_data in data.items():
                    # Convert back to dataclass
                    profile_data["expertise_level"] = UserExpertiseLevel(
                        profile_data["expertise_level"]
                    )
                    profile_data["preferred_mode"] = InterfaceMode(
                        profile_data["preferred_mode"]
                    )
                    profile_data["completed_tutorials"] = set(
                        profile_data.get("completed_tutorials", [])
                    )
                    profile_data["known_shortcuts"] = set(
                        profile_data.get("known_shortcuts", [])
                    )
                    profile_data["created_at"] = datetime.fromisoformat(
                        profile_data["created_at"]
                    )
                    profile_data["last_updated"] = datetime.fromisoformat(
                        profile_data["last_updated"]
                    )

                    self.user_profiles[user_id] = UserProfile(**profile_data)
            except Exception as e:
                print(f"Warning: Failed to load user profiles: {e}")

    def _save_user_profiles(self):
        """Save user profiles to storage."""
        try:
            profiles_data = {}
            for user_id, profile in self.user_profiles.items():
                profile_dict = {
                    "user_id": profile.user_id,
                    "expertise_level": profile.expertise_level.value,
                    "preferred_mode": profile.preferred_mode.value,
                    "command_usage_count": profile.command_usage_count,
                    "last_used_commands": profile.last_used_commands,
                    "favorite_workflows": profile.favorite_workflows,
                    "show_examples": profile.show_examples,
                    "show_progress_bars": profile.show_progress_bars,
                    "use_colors": profile.use_colors,
                    "preferred_verbosity": profile.preferred_verbosity,
                    "completed_tutorials": list(profile.completed_tutorials),
                    "known_shortcuts": list(profile.known_shortcuts),
                    "created_at": profile.created_at.isoformat(),
                    "last_updated": profile.last_updated.isoformat(),
                }
                profiles_data[user_id] = profile_dict

            with open(self.data_dir / "user_profiles.json", "w") as f:
                json.dump(profiles_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save user profiles: {e}")

    def get_user_profile(self, user_id: str = "default") -> UserProfile:
        """Get or create user profile."""
        if user_id not in self.user_profiles:
            # Create new profile with auto - detected expertise
            expertise = self._detect_user_expertise(user_id)

            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                expertise_level=expertise,
                preferred_mode=self._get_default_mode_for_expertise(expertise),
            )

            self._save_user_profiles()

        return self.user_profiles[user_id]

    def _detect_user_expertise(self, user_id: str) -> UserExpertiseLevel:
        """Auto - detect user expertise level based on usage patterns."""
        if not self.config.get("auto_detect_expertise", True):
            return UserExpertiseLevel.BEGINNER

        try:
            # Get user interaction history from preference system
            patterns = self.preference_system.get_user_patterns(user_id)

            if not patterns:
                return UserExpertiseLevel.BEGINNER

            # Simple heuristics for expertise detection
            total_commands = patterns.get("total_interactions", 0)
            unique_commands = len(patterns.get("command_usage", {}))
            error_rate = patterns.get("error_rate", 1.0)

            if total_commands > 100 and unique_commands > 15 and error_rate < 0.1:
                return UserExpertiseLevel.EXPERT
            elif total_commands > 50 and unique_commands > 10 and error_rate < 0.2:
                return UserExpertiseLevel.ADVANCED
            elif total_commands > 20 and unique_commands > 5 and error_rate < 0.3:
                return UserExpertiseLevel.INTERMEDIATE
            else:
                return UserExpertiseLevel.BEGINNER

        except Exception:
            return UserExpertiseLevel.BEGINNER

    def _get_default_mode_for_expertise(
        self, expertise: UserExpertiseLevel
    ) -> InterfaceMode:
        """Get default interface mode for expertise level."""
        mapping = {
            UserExpertiseLevel.BEGINNER: InterfaceMode.SIMPLE,
            UserExpertiseLevel.INTERMEDIATE: InterfaceMode.STANDARD,
            UserExpertiseLevel.ADVANCED: InterfaceMode.COMPLETE,
            UserExpertiseLevel.EXPERT: InterfaceMode.EXPERT,
        }
        return mapping.get(expertise, InterfaceMode.STANDARD)

    def record_command_usage(self, user_id: str, command: str, success: bool = True):
        """Record command usage for learning."""
        profile = self.get_user_profile(user_id)

        # Update usage count
        profile.command_usage_count[command] = (
            profile.command_usage_count.get(command, 0) + 1
        )

        # Update recent commands
        if command in profile.last_used_commands:
            profile.last_used_commands.remove(command)
        profile.last_used_commands.insert(0, command)
        profile.last_used_commands = profile.last_used_commands[
            : self.config.get("command_history_limit", 50)
        ]

        # Update command registry statistics
        if command in self.command_registry:
            cmd_info = self.command_registry[command]
            cmd_info.frequency_score += 1

            if not success:
                # Update success rate (simple moving average)
                cmd_info.success_rate = (cmd_info.success_rate * 0.9) + (0.0 * 0.1)

        profile.last_updated = datetime.now()
        self._save_user_profiles()

    def get_command_suggestions(
        self, user_id: str, context: str = ""
    ) -> List[CommandSuggestion]:
        """Get intelligent command suggestions for the user."""
        profile = self.get_user_profile(user_id)
        suggestions = []

        # Context - based suggestions
        if context:
            suggestions.extend(self._get_context_suggestions(context, profile))

        # Usage pattern suggestions
        suggestions.extend(self._get_usage_pattern_suggestions(profile))

        # Expertise - based suggestions
        suggestions.extend(self._get_expertise_suggestions(profile))

        # Filter by confidence threshold
        threshold = self.config.get("suggestion_confidence_threshold", 0.7)
        filtered_suggestions = [s for s in suggestions if s.confidence >= threshold]

        # Sort by confidence and limit
        filtered_suggestions.sort(key=lambda x: x.confidence, reverse=True)
        max_suggestions = self.config.get("max_suggestions", 3)

        return filtered_suggestions[:max_suggestions]

    def _get_context_suggestions(
        self, context: str, profile: UserProfile
    ) -> List[CommandSuggestion]:
        """Get suggestions based on current context."""
        suggestions = []
        context_lower = context.lower()

        # Context keywords to commands mapping
        context_mappings = {
            "project": ["charter", "plan", "align", "validate"],
            "planning": ["charter", "plan", "prompt"],
            "optimization": ["kaizen", "kaizen - auto", "opt - experiments"],
            "performance": ["kaizen", "opt - experiments", "unified - metrics"],
            "ai": ["ai - agent", "aaol", "enhanced - context"],
            "error": ["validate", "debug", "continuous - improvement"],
            "development": ["cursor", "api", "unified - metrics"],
            "learning": ["user - prefs", "continuous - improvement"],
            "experiment": ["opt - experiments", "kaizen - auto"],
            "metrics": ["unified - metrics", "prompt"],
        }

        for keyword, commands in context_mappings.items():
            if keyword in context_lower:
                for cmd in commands:
                    if cmd in self.command_registry:
                        cmd_info = self.command_registry[cmd]
                        if self._is_command_appropriate_for_user(cmd_info, profile):
                            suggestions.append(
                                CommandSuggestion(
                                    command=cmd,
                                    reason=f"Relevant to '{keyword}' context",
                                    confidence=0.8,
                                    context=context,
                                    example=cmd_info.usage_example,
                                )
                            )

        return suggestions

    def _get_usage_pattern_suggestions(
        self, profile: UserProfile
    ) -> List[CommandSuggestion]:
        """Get suggestions based on user's usage patterns."""
        suggestions = []

        # Suggest related commands to frequently used ones
        for cmd, count in profile.command_usage_count.items():
            if count > 5 and cmd in self.command_registry:  # Frequently used
                cmd_info = self.command_registry[cmd]
                for related_cmd in cmd_info.related_commands:
                    if related_cmd in self.command_registry:
                        related_info = self.command_registry[related_cmd]
                        if self._is_command_appropriate_for_user(related_info, profile):
                            suggestions.append(
                                CommandSuggestion(
                                    command=related_cmd,
                                    reason=f"Related to frequently used '{cmd}'",
                                    confidence=0.7,
                                    context="usage_pattern",
                                    example=related_info.usage_example,
                                )
                            )

        return suggestions

    def _get_expertise_suggestions(
        self, profile: UserProfile
    ) -> List[CommandSuggestion]:
        """Get suggestions based on user's expertise level."""
        suggestions = []

        # Suggest commands appropriate for next expertise level
        next_level_map = {
            UserExpertiseLevel.BEGINNER: UserExpertiseLevel.INTERMEDIATE,
            UserExpertiseLevel.INTERMEDIATE: UserExpertiseLevel.ADVANCED,
            UserExpertiseLevel.ADVANCED: UserExpertiseLevel.EXPERT,
            UserExpertiseLevel.EXPERT: UserExpertiseLevel.EXPERT,
        }

        next_level = next_level_map.get(
            profile.expertise_level, UserExpertiseLevel.INTERMEDIATE
        )

        for cmd_info in self.command_registry.values():
            if cmd_info.expertise_level == next_level:
                # Check if prerequisites are met
                if self._are_prerequisites_met(cmd_info, profile):
                    suggestions.append(
                        CommandSuggestion(
                            command=cmd_info.name,
                            reason=f"Ready to learn {next_level.value} level commands",
                            confidence=0.6,
                            context="expertise_growth",
                            example=cmd_info.usage_example,
                        )
                    )

        return suggestions

    def _is_command_appropriate_for_user(
        self, cmd_info: CommandInfo, profile: UserProfile
    ) -> bool:
        """Check if a command is appropriate for the user's current level."""
        expertise_order = [
            UserExpertiseLevel.BEGINNER,
            UserExpertiseLevel.INTERMEDIATE,
            UserExpertiseLevel.ADVANCED,
            UserExpertiseLevel.EXPERT,
        ]

        user_level_index = expertise_order.index(profile.expertise_level)
        cmd_level_index = expertise_order.index(cmd_info.expertise_level)

        # Allow commands up to one level above user's current level
        return cmd_level_index <= user_level_index + 1

    def _are_prerequisites_met(
        self, cmd_info: CommandInfo, profile: UserProfile
    ) -> bool:
        """Check if command prerequisites are met."""
        for prereq in cmd_info.prerequisites:
            if profile.command_usage_count.get(prereq, 0) == 0:
                return False
        return True

    def get_filtered_commands(
        self, user_id: str, category: Optional[CommandCategory] = None
    ) -> List[CommandInfo]:
        """Get commands filtered by user's interface mode and expertise."""
        profile = self.get_user_profile(user_id)
        commands = []

        for cmd_info in self.command_registry.values():
            # Filter by category if specified
            if category and cmd_info.category != category:
                continue

            # Filter by interface mode
            if not self._should_show_command_in_mode(cmd_info, profile.preferred_mode):
                continue

            # Filter by expertise appropriateness
            if not self._is_command_appropriate_for_user(cmd_info, profile):
                continue

            commands.append(cmd_info)

        # Sort by frequency and relevance
        commands.sort(
            key=lambda x: (
                profile.command_usage_count.get(x.name, 0),  # Usage frequency
                x.frequency_score,  # Global frequency
                -len(x.prerequisites),  # Fewer prerequisites first
            ),
            reverse=True,
        )

        return commands

    def _should_show_command_in_mode(
        self, cmd_info: CommandInfo, mode: InterfaceMode
    ) -> bool:
        """Determine if command should be shown in the given interface mode."""
        if mode == InterfaceMode.SIMPLE:
            return cmd_info.expertise_level == UserExpertiseLevel.BEGINNER
        elif mode == InterfaceMode.STANDARD:
            return cmd_info.expertise_level in [
                UserExpertiseLevel.BEGINNER,
                UserExpertiseLevel.INTERMEDIATE,
            ]
        elif mode == InterfaceMode.COMPLETE:
            return cmd_info.expertise_level != UserExpertiseLevel.EXPERT
        else:  # EXPERT
            return True

    def format_output(
        self, text: str, style: str = "info", user_id: str = "default"
    ) -> str:
        """Format output with appropriate styling."""
        profile = self.get_user_profile(user_id)

        if not profile.use_colors or not self.config.get("enable_colors", True):
            return text

        theme_name = self.config.get("default_theme", "modern")
        theme = self.ui_themes.get(theme_name, self.ui_themes["modern"])

        color_map = {
            "primary": theme.primary_color,
            "secondary": theme.secondary_color,
            "success": theme.success_color,
            "warning": theme.warning_color,
            "error": theme.error_color,
            "info": theme.info_color,
        }

        reset = "\033[0m" if profile.use_colors else ""
        color = color_map.get(style, "")

        return f"{color}{text}{reset}"

    def get_progress_bar(
        self, current: int, total: int, width: int = 20, user_id: str = "default"
    ) -> str:
        """Generate a progress bar."""
        profile = self.get_user_profile(user_id)

        if not profile.show_progress_bars or not self.config.get(
            "enable_progress_bars", True
        ):
            return f"{current}/{total} ({current / total * 100:.1f}%)"

        filled = int(width * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (width - filled)
        percentage = (current / total * 100) if total > 0 else 0

        return self.format_output(f"{bar} {percentage:.1f}%", "primary", user_id)

    def create_command_help(self, command: str, user_id: str = "default") -> str:
        """Create enhanced help text for a command."""
        profile = self.get_user_profile(user_id)

        if command not in self.command_registry:
            return f"Command '{command}' not found."

        cmd_info = self.command_registry[command]
        help_text = []

        # Basic info
        help_text.append(
            self.format_output(f"Command: {cmd_info.name}", "primary", user_id)
        )
        help_text.append(f"Description: {cmd_info.description}")
        help_text.append(f"Category: {cmd_info.category.value}")
        help_text.append(f"Expertise Level: {cmd_info.expertise_level.value}")

        # Usage example
        if profile.show_examples:
            help_text.append(f"\nExample:")
            help_text.append(f"  {cmd_info.usage_example}")

        # Prerequisites
        if cmd_info.prerequisites:
            help_text.append(f"\nPrerequisites:")
            for prereq in cmd_info.prerequisites:
                status = "✓" if profile.command_usage_count.get(prereq, 0) > 0 else "○"
                help_text.append(f"  {status} {prereq}")

        # Related commands
        if cmd_info.related_commands:
            help_text.append(f"\nRelated commands:")
            for related in cmd_info.related_commands:
                help_text.append(f"  • {related}")

        # Usage stats
        usage_count = profile.command_usage_count.get(command, 0)
        if usage_count > 0:
            help_text.append(f"\nYour usage: {usage_count} times")

        return "\n".join(help_text)

    def get_dashboard_summary(self, user_id: str = "default") -> str:
        """Create a dashboard summary for the user."""
        profile = self.get_user_profile(user_id)
        dashboard = []

        # Header
        dashboard.append(
            self.format_output("🚀 AI Onboard Dashboard", "primary", user_id)
        )
        dashboard.append("=" * 40)

        # User info
        dashboard.append(f"User: {profile.user_id}")
        dashboard.append(f"Expertise Level: {profile.expertise_level.value}")
        dashboard.append(f"Interface Mode: {profile.preferred_mode.value}")

        # Usage stats
        total_usage = sum(profile.command_usage_count.values())
        unique_commands = len(profile.command_usage_count)

        dashboard.append(f"\n📊 Usage Statistics:")
        dashboard.append(f"Total Commands: {total_usage}")
        dashboard.append(f"Unique Commands: {unique_commands}")

        # Most used commands
        if profile.command_usage_count:
            dashboard.append(f"\n🔥 Most Used Commands:")
            sorted_commands = sorted(
                profile.command_usage_count.items(), key=lambda x: x[1], reverse=True
            )
            for cmd, count in sorted_commands[:5]:
                dashboard.append(f"  {cmd}: {count} times")

        # Suggestions
        suggestions = self.get_command_suggestions(user_id)
        if suggestions:
            dashboard.append(f"\n💡 Suggestions:")
            for suggestion in suggestions:
                dashboard.append(f"  • {suggestion.command}: {suggestion.reason}")

        # Available categories
        dashboard.append(f"\n📂 Available Categories:")
        for category in CommandCategory:
            cmd_count = len(
                [
                    cmd
                    for cmd in self.command_registry.values()
                    if cmd.category == category
                ]
            )
            dashboard.append(f"  {category.value}: {cmd_count} commands")

        return "\n".join(dashboard)


# Global instance
_ui_enhancement_system: Optional[UIEnhancementSystem] = None


def get_ui_enhancement_system(root: Path) -> UIEnhancementSystem:
    """Get the global UI enhancement system."""
    global _ui_enhancement_system
    if _ui_enhancement_system is None:
        _ui_enhancement_system = UIEnhancementSystem(root)
    return _ui_enhancement_system
