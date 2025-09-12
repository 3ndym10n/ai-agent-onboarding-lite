"""
Enhanced Help System - Intelligent, contextual help and guidance.

This module provides:
- Context-aware help that adapts to user expertise
- Interactive help with examples and tutorials
- Command discovery and suggestion system
- Progressive disclosure of functionality
- Visual and accessible help formatting
"""

import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..core.ui_enhancement_system import (
    CommandCategory,
    InterfaceMode,
    UserExpertiseLevel,
    get_ui_enhancement_system,
)


class HelpSystem:
    """Enhanced help system with intelligent guidance."""

    def __init__(self, root: Path):
        self.root = root
        self.ui_system = get_ui_enhancement_system(root)
        self.terminal_width = self._get_terminal_width()

    def _get_terminal_width(self) -> int:
        """Get terminal width for formatting."""
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return 80

    def show_main_help(
        self, user_id: str = "default", mode: Optional[str] = None
    ) -> str:
        """Show main help with user-appropriate commands."""
        profile = self.ui_system.get_user_profile(user_id)

        if mode:
            # Override interface mode temporarily
            if mode == "simple":
                interface_mode = InterfaceMode.SIMPLE
            elif mode == "complete":
                interface_mode = InterfaceMode.COMPLETE
            elif mode == "expert":
                interface_mode = InterfaceMode.EXPERT
            else:
                interface_mode = profile.preferred_mode
        else:
            interface_mode = profile.preferred_mode

        help_text = []

        # Header
        help_text.append(
            self.ui_system.format_output(
                "🚀 AI Onboard - Intelligent Project Coach", "primary", user_id
            )
        )
        help_text.append("=" * min(50, self.terminal_width))

        # User context
        help_text.append(
            f"Mode: {interface_mode.value} | Expertise: {profile.expertise_level.value}"
        )
        help_text.append("")

        # Quick actions (always shown)
        help_text.append(
            self.ui_system.format_output("⚡ Quick Actions:", "info", user_id)
        )
        quick_actions = [
            ("dashboard", "Show project dashboard and status"),
            ("suggest", "Get personalized command suggestions"),
            ("help --interactive", "Interactive help and tutorials"),
            ("help --categories", "Browse commands by category"),
        ]

        for action, desc in quick_actions:
            help_text.append(f"  ai_onboard {action:<20} {desc}")
        help_text.append("")

        # Commands by category
        help_text.append(
            self.ui_system.format_output("📂 Available Commands:", "info", user_id)
        )

        # Get commands for current interface mode
        temp_profile = profile
        temp_profile.preferred_mode = interface_mode

        categories_shown = set()
        for category in CommandCategory:
            commands = self.ui_system.get_filtered_commands(user_id, category)
            if not commands:
                continue

            categories_shown.add(category)
            help_text.append(f"\n{self._format_category_header(category, user_id)}:")

            for cmd in commands[: self._get_max_commands_for_mode(interface_mode)]:
                # Show usage count if user has used it
                usage_indicator = ""
                usage_count = profile.command_usage_count.get(cmd.name, 0)
                if usage_count > 0:
                    usage_indicator = f" ({usage_count}x)"
                elif cmd.name in profile.last_used_commands[:5]:
                    usage_indicator = " (recent)"

                help_text.append(f"  {cmd.name:<20} {cmd.description}{usage_indicator}")

        # Footer with tips
        help_text.append("")
        help_text.append(self.ui_system.format_output("💡 Tips:", "secondary", user_id))

        tips = self._get_contextual_tips(profile, interface_mode)
        for tip in tips[:3]:  # Show max 3 tips
            help_text.append(f"  • {tip}")

        # Mode switching info
        if interface_mode != InterfaceMode.COMPLETE:
            help_text.append(
                f"\n  • Use 'help --mode complete' to see all {len(self.ui_system.command_registry)} commands"
            )

        if profile.expertise_level == UserExpertiseLevel.BEGINNER:
            help_text.append("  • Try 'help --tutorial' for guided learning")

        return "\n".join(help_text)

    def _format_category_header(self, category: CommandCategory, user_id: str) -> str:
        """Format category header with appropriate styling."""
        category_icons = {
            CommandCategory.PROJECT: "📋",
            CommandCategory.OPTIMIZATION: "⚡",
            CommandCategory.AI_SYSTEMS: "🤖",
            CommandCategory.DEVELOPMENT: "💻",
            CommandCategory.LEARNING: "📚",
            CommandCategory.CORE: "🔧",
            CommandCategory.ADVANCED: "🚀",
        }

        icon = category_icons.get(category, "📁")
        title = category.value.replace("_", " ").title()

        return self.ui_system.format_output(f"{icon} {title}", "secondary", user_id)

    def _get_max_commands_for_mode(self, mode: InterfaceMode) -> int:
        """Get maximum commands to show per category based on mode."""
        if mode == InterfaceMode.SIMPLE:
            return 3
        elif mode == InterfaceMode.STANDARD:
            return 5
        elif mode == InterfaceMode.COMPLETE:
            return 10
        else:  # EXPERT
            return 20

    def _get_contextual_tips(self, profile, mode: InterfaceMode) -> List[str]:
        """Get contextual tips based on user profile and mode."""
        tips = []

        # Expertise-based tips
        if profile.expertise_level == UserExpertiseLevel.BEGINNER:
            tips.extend(
                [
                    "Start with 'charter' to define your project vision",
                    "Use 'prompt progress' to see your current status",
                    "Try 'help <command>' for detailed command information",
                ]
            )
        elif profile.expertise_level == UserExpertiseLevel.INTERMEDIATE:
            tips.extend(
                [
                    "Explore 'kaizen' for continuous improvement",
                    "Use 'validate' regularly to ensure quality",
                    "Try 'user-prefs summary --user you' to see your patterns",
                ]
            )
        elif profile.expertise_level == UserExpertiseLevel.ADVANCED:
            tips.extend(
                [
                    "Set up 'kaizen-auto start' for automated improvements",
                    "Design experiments with 'opt-experiments'",
                    "Use 'aaol' for advanced AI collaboration",
                ]
            )
        else:  # EXPERT
            tips.extend(
                [
                    "Create custom workflows with 'decision-pipeline'",
                    "Use 'api start' to integrate with external tools",
                    "Explore 'enhanced-context' for advanced AI features",
                ]
            )

        # Usage-based tips
        total_usage = sum(profile.command_usage_count.values())
        if total_usage == 0:
            tips.append("New here? Try 'help --tutorial' for a guided introduction")
        elif total_usage < 10:
            tips.append("Use 'suggest' to discover commands relevant to your workflow")
        elif len(profile.command_usage_count) < 5:
            tips.append(
                "You're using few commands - explore other categories to expand your toolkit"
            )

        # Mode-based tips
        if (
            mode == InterfaceMode.SIMPLE
            and profile.expertise_level != UserExpertiseLevel.BEGINNER
        ):
            tips.append(
                "Switch to 'standard' mode with 'config set interface_mode standard'"
            )

        return tips

    def show_category_help(self, category_name: str, user_id: str = "default") -> str:
        """Show help for a specific category."""
        # Map category names to enum
        category_map = {
            "project": CommandCategory.PROJECT,
            "optimization": CommandCategory.OPTIMIZATION,
            "ai": CommandCategory.AI_SYSTEMS,
            "ai-systems": CommandCategory.AI_SYSTEMS,
            "development": CommandCategory.DEVELOPMENT,
            "dev": CommandCategory.DEVELOPMENT,
            "learning": CommandCategory.LEARNING,
            "core": CommandCategory.CORE,
            "advanced": CommandCategory.ADVANCED,
        }

        category = category_map.get(category_name.lower())
        if not category:
            return f"Unknown category: {category_name}. Available: {', '.join(category_map.keys())}"

        commands = self.ui_system.get_filtered_commands(user_id, category)
        if not commands:
            return f"No commands available in category: {category.value}"

        help_text = []

        # Header
        header = self._format_category_header(category, user_id)
        help_text.append(f"{header} Commands")
        help_text.append("=" * min(40, self.terminal_width))
        help_text.append("")

        # Category description
        descriptions = {
            CommandCategory.PROJECT: "Core project management and planning commands",
            CommandCategory.OPTIMIZATION: "Performance optimization and improvement tools",
            CommandCategory.AI_SYSTEMS: "AI agent collaboration and orchestration",
            CommandCategory.DEVELOPMENT: "Development tools and integrations",
            CommandCategory.LEARNING: "User preference learning and system improvement",
            CommandCategory.CORE: "Essential system functionality",
            CommandCategory.ADVANCED: "Advanced and experimental features",
        }

        help_text.append(descriptions.get(category, "Commands in this category"))
        help_text.append("")

        # Commands with detailed info
        profile = self.ui_system.get_user_profile(user_id)

        for cmd in commands:
            help_text.append(
                self.ui_system.format_output(f"• {cmd.name}", "primary", user_id)
            )
            help_text.append(f"  {cmd.description}")
            help_text.append(f"  Example: {cmd.usage_example}")

            # Usage info
            usage_count = profile.command_usage_count.get(cmd.name, 0)
            if usage_count > 0:
                help_text.append(f"  Your usage: {usage_count} times")
            elif cmd.name in profile.last_used_commands:
                help_text.append("  Recently used")

            # Prerequisites
            if cmd.prerequisites:
                prereq_status = []
                for prereq in cmd.prerequisites:
                    if profile.command_usage_count.get(prereq, 0) > 0:
                        prereq_status.append(f"✓ {prereq}")
                    else:
                        prereq_status.append(f"○ {prereq}")
                help_text.append(f"  Prerequisites: {', '.join(prereq_status)}")

            help_text.append("")

        return "\n".join(help_text)

    def show_command_help(
        self, command: str, user_id: str = "default", detailed: bool = False
    ) -> str:
        """Show detailed help for a specific command."""
        return self.ui_system.create_command_help(command, user_id)

    def show_interactive_help(self, user_id: str = "default") -> str:
        """Show interactive help menu."""
        help_text = []

        help_text.append(
            self.ui_system.format_output(
                "🎯 Interactive Help System", "primary", user_id
            )
        )
        help_text.append("=" * min(40, self.terminal_width))
        help_text.append("")

        profile = self.ui_system.get_user_profile(user_id)

        # Personalized welcome
        total_usage = sum(profile.command_usage_count.values())
        if total_usage == 0:
            help_text.append("Welcome to AI Onboard! Let's get you started.")
        elif total_usage < 10:
            help_text.append(
                "You're getting familiar with AI Onboard. Here's what you can explore:"
            )
        else:
            help_text.append(
                "You're an experienced user! Here are some advanced options:"
            )

        help_text.append("")

        # Interactive options
        options = []

        if total_usage == 0:
            options.extend(
                [
                    ("tutorial", "Start guided tutorial"),
                    ("suggest", "Get personalized suggestions"),
                    ("dashboard", "View project dashboard"),
                ]
            )
        else:
            options.extend(
                [
                    ("suggest", "Get command suggestions"),
                    ("dashboard", "View dashboard"),
                    ("help --categories", "Browse by category"),
                    ("config", "Customize interface"),
                ]
            )

        help_text.append(
            self.ui_system.format_output("📋 Available Options:", "info", user_id)
        )
        for i, (cmd, desc) in enumerate(options, 1):
            help_text.append(f"  {i}. ai_onboard {cmd:<15} - {desc}")

        help_text.append("")

        # Quick reference
        help_text.append(
            self.ui_system.format_output("🔍 Quick Reference:", "secondary", user_id)
        )
        quick_ref = [
            ("help <command>", "Detailed help for specific command"),
            ("help --mode simple", "Show only essential commands"),
            ("help --mode complete", "Show all available commands"),
            ("suggest --context <topic>", "Get suggestions for specific topic"),
        ]

        for cmd, desc in quick_ref:
            help_text.append(f"  ai_onboard {cmd:<25} - {desc}")

        return "\n".join(help_text)

    def show_tutorial(
        self, topic: str = "getting_started", user_id: str = "default"
    ) -> str:
        """Show tutorial content."""
        tutorials = {
            "getting_started": self._create_getting_started_tutorial(user_id),
            "project_setup": self._create_project_setup_tutorial(user_id),
            "optimization": self._create_optimization_tutorial(user_id),
            "ai_features": self._create_ai_features_tutorial(user_id),
        }

        if topic not in tutorials:
            available = ", ".join(tutorials.keys())
            return f"Tutorial '{topic}' not found. Available: {available}"

        return tutorials[topic]

    def _create_getting_started_tutorial(self, user_id: str) -> str:
        """Create getting started tutorial."""
        tutorial = []

        tutorial.append(
            self.ui_system.format_output(
                "🎓 Getting Started Tutorial", "primary", user_id
            )
        )
        tutorial.append("=" * min(40, self.terminal_width))
        tutorial.append("")

        tutorial.append(
            "Welcome to AI Onboard! This tutorial will guide you through the essential commands."
        )
        tutorial.append("")

        steps = [
            (
                "Step 1: Create Project Vision",
                "ai_onboard charter",
                "Define your project's goals and vision",
            ),
            (
                "Step 2: Generate Project Plan",
                "ai_onboard plan",
                "Create a detailed project plan with tasks and milestones",
            ),
            (
                "Step 3: Check Alignment",
                "ai_onboard align",
                "Ensure your project aligns with your vision",
            ),
            (
                "Step 4: Monitor Progress",
                "ai_onboard prompt progress",
                "Check your current project status",
            ),
            (
                "Step 5: Validate Quality",
                "ai_onboard validate",
                "Run quality checks and validation",
            ),
        ]

        for step_name, command, description in steps:
            tutorial.append(self.ui_system.format_output(step_name, "info", user_id))
            tutorial.append(f"Command: {command}")
            tutorial.append(f"Purpose: {description}")
            tutorial.append("")

        tutorial.append(
            self.ui_system.format_output("🎯 Next Steps:", "secondary", user_id)
        )
        tutorial.append("• Try each command in order")
        tutorial.append("• Use 'help <command>' for detailed information")
        tutorial.append("• Run 'suggest' to discover more features")

        return "\n".join(tutorial)

    def _create_project_setup_tutorial(self, user_id: str) -> str:
        """Create project setup tutorial."""
        tutorial = []

        tutorial.append(
            self.ui_system.format_output("🏗️ Project Setup Tutorial", "primary", user_id)
        )
        tutorial.append("=" * min(40, self.terminal_width))
        tutorial.append("")

        tutorial.append("Learn how to set up a new project with AI Onboard.")
        tutorial.append("")

        # Add project setup steps...
        tutorial.append("Coming soon: Detailed project setup guide")

        return "\n".join(tutorial)

    def _create_optimization_tutorial(self, user_id: str) -> str:
        """Create optimization tutorial."""
        tutorial = []

        tutorial.append(
            self.ui_system.format_output("⚡ Optimization Tutorial", "primary", user_id)
        )
        tutorial.append("=" * min(40, self.terminal_width))
        tutorial.append("")

        tutorial.append("Learn how to optimize your project with AI Onboard.")
        tutorial.append("")

        # Add optimization steps...
        tutorial.append("Coming soon: Detailed optimization guide")

        return "\n".join(tutorial)

    def _create_ai_features_tutorial(self, user_id: str) -> str:
        """Create AI features tutorial."""
        tutorial = []

        tutorial.append(
            self.ui_system.format_output("🤖 AI Features Tutorial", "primary", user_id)
        )
        tutorial.append("=" * min(40, self.terminal_width))
        tutorial.append("")

        tutorial.append("Explore advanced AI collaboration features.")
        tutorial.append("")

        # Add AI features steps...
        tutorial.append("Coming soon: Detailed AI features guide")

        return "\n".join(tutorial)

    def show_suggestions(self, user_id: str = "default", context: str = "") -> str:
        """Show personalized command suggestions."""
        suggestions = self.ui_system.get_command_suggestions(user_id, context)

        if not suggestions:
            return "No suggestions available at this time. Try using more commands to build your profile!"

        help_text = []

        help_text.append(
            self.ui_system.format_output(
                "💡 Personalized Suggestions", "primary", user_id
            )
        )
        help_text.append("=" * min(40, self.terminal_width))
        help_text.append("")

        if context:
            help_text.append(f"Context: {context}")
            help_text.append("")

        for i, suggestion in enumerate(suggestions, 1):
            confidence_bar = "█" * int(suggestion.confidence * 10) + "░" * (
                10 - int(suggestion.confidence * 10)
            )

            help_text.append(
                self.ui_system.format_output(
                    f"{i}. {suggestion.command}", "info", user_id
                )
            )
            help_text.append(f"   Reason: {suggestion.reason}")
            help_text.append(
                f"   Confidence: {confidence_bar} {suggestion.confidence:.0%}"
            )
            help_text.append(f"   Example: {suggestion.example}")
            help_text.append("")

        help_text.append(
            self.ui_system.format_output(
                "🎯 Try these commands to expand your toolkit!", "secondary", user_id
            )
        )

        return "\n".join(help_text)


# Global instance
_help_system: Optional[HelpSystem] = None


def get_help_system(root: Path) -> HelpSystem:
    """Get the global help system."""
    global _help_system
    if _help_system is None:
        _help_system = HelpSystem(root)
    return _help_system
