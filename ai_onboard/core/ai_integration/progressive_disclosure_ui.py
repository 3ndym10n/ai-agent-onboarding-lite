"""
Progressive Disclosure UI - Adaptive interface that hides complexity from non-technical users.

This module provides intelligent progressive disclosure that shows users only what they
need to see based on their expertise level and current context. It prevents
overwhelming "vibe coders" with technical complexity while providing power users
with advanced options when needed.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..base.shared_types import DisclosureLevel, UIComplexityLevel, UserExpertiseLevel
from .user_preference_learning import get_user_preference_learning_system

# Note: UserExpertiseLevel, DisclosureLevel, UIComplexityLevel now imported from shared_types


@dataclass
class UIElement:
    """Represents a UI element with complexity metadata."""

    element_id: str
    display_name: str
    description: str
    complexity_level: UIComplexityLevel
    expertise_required: UserExpertiseLevel
    category: str

    # Progressive disclosure settings
    default_visibility: bool = True
    can_be_hidden: bool = True
    requires_confirmation: bool = False

    # Dependencies
    prerequisite_elements: List[str] = field(default_factory=list)
    conflicting_elements: List[str] = field(default_factory=list)

    # Metadata
    usage_frequency: float = 0.0
    user_satisfaction: float = 0.5


class ProgressiveDisclosureEngine:
    """Engine for managing progressive disclosure based on user expertise and context."""

    def __init__(self, root: Path):
        self.root = root
        self.preference_system = get_user_preference_learning_system(root)

        # UI element registry
        self.ui_elements: Dict[str, UIElement] = {}
        self.element_categories: Dict[str, List[str]] = {}

        # User context tracking
        self.user_expertise_cache: Dict[str, UserExpertiseLevel] = {}
        self.user_preferences_cache: Dict[str, Set[str]] = {}

        # Progressive disclosure rules
        self.disclosure_rules = self._load_disclosure_rules()

        # Initialize with default UI elements
        self._initialize_default_elements()

    def register_ui_element(self, element: UIElement) -> None:
        """Register a UI element for progressive disclosure management."""
        self.ui_elements[element.element_id] = element

        # Update category index
        if element.category not in self.element_categories:
            self.element_categories[element.category] = []

        self.element_categories[element.category].append(element.element_id)

    def get_visible_elements(
        self, user_id: str, context: str = "general", max_elements: Optional[int] = None
    ) -> List[UIElement]:
        """
        Get UI elements that should be visible to a user based on their expertise and context.

        Args:
            user_id: User identifier
            context: Current context (e.g., "project_setup", "development")
            max_elements: Optional limit on number of elements

        Returns:
            List of UI elements that should be visible
        """
        user_expertise = self._get_user_expertise(user_id)
        user_preferences = self._get_user_preferences(user_id)

        visible_elements = []

        for element in self.ui_elements.values():
            if self._should_show_element(
                element, user_expertise, context, user_preferences
            ):
                visible_elements.append(element)

        # Sort by relevance and limit if needed
        visible_elements.sort(
            key=lambda e: self._calculate_element_relevance(e, user_expertise, context),
            reverse=True,
        )

        if max_elements:
            visible_elements = visible_elements[:max_elements]

        return visible_elements

    def get_simplified_interface(
        self, user_id: str, context: str = "general", max_options: int = 5
    ) -> Dict[str, Any]:
        """
        Get a simplified interface configuration for non-technical users.

        Args:
            user_id: User identifier
            context: Current context
            max_options: Maximum number of options to show

        Returns:
            Simplified interface configuration
        """
        user_expertise = self._get_user_expertise(user_id)

        # For beginners, show only simple elements
        if user_expertise == UserExpertiseLevel.BEGINNER:
            disclosure_level = DisclosureLevel.MINIMAL
        elif user_expertise == UserExpertiseLevel.INTERMEDIATE:
            disclosure_level = DisclosureLevel.BASIC
        else:
            disclosure_level = DisclosureLevel.INTERMEDIATE

        # Get elements appropriate for disclosure level
        appropriate_elements = self._get_elements_for_disclosure_level(
            disclosure_level, context
        )

        # Simplify element names and descriptions for beginners
        simplified_elements = []
        for element in appropriate_elements[:max_options]:
            simplified = self._simplify_element_for_user(element, user_expertise)
            simplified_elements.append(simplified)

        return {
            "user_expertise": user_expertise.value,
            "disclosure_level": disclosure_level.value,
            "context": context,
            "elements": simplified_elements,
            "total_available": len(appropriate_elements),
            "can_show_more": len(appropriate_elements) > max_options,
        }

    def get_progressive_help(
        self, user_id: str, current_action: str, difficulty_level: str = "normal"
    ) -> Dict[str, Any]:
        """
        Get progressive help that adapts to user expertise and current difficulty.

        Args:
            user_id: User identifier
            current_action: What the user is trying to do
            difficulty_level: Current difficulty level

        Returns:
            Progressive help configuration
        """
        user_expertise = self._get_user_expertise(user_id)

        # Determine help level needed
        help_config = self._determine_help_level(
            user_expertise, difficulty_level, current_action
        )

        return {
            "help_level": help_config["level"],
            "show_tips": help_config["show_tips"],
            "show_examples": help_config["show_examples"],
            "show_advanced": help_config["show_advanced"],
            "simplified_language": user_expertise in [UserExpertiseLevel.BEGINNER],
            "step_by_step": user_expertise == UserExpertiseLevel.BEGINNER,
        }

    def update_user_feedback(
        self,
        user_id: str,
        element_id: str,
        action: str,
        success: bool,
        difficulty_rating: Optional[int] = None,
    ) -> None:
        """
        Update user feedback to improve progressive disclosure.

        Args:
            user_id: User identifier
            element_id: UI element that was used
            action: Action performed
            success: Whether the action was successful
            difficulty_rating: User's difficulty rating (1-5)
        """
        if element_id not in self.ui_elements:
            return

        element = self.ui_elements[element_id]

        # Update usage frequency
        element.usage_frequency = min(1.0, element.usage_frequency + 0.1)

        # Update satisfaction based on success
        if success:
            element.user_satisfaction = min(1.0, element.user_satisfaction + 0.1)
        else:
            element.user_satisfaction = max(0.0, element.user_satisfaction - 0.1)

        # Store user preference for this element
        user_prefs = self._get_user_preferences(user_id)
        if success:
            user_prefs.add(element_id)
        else:
            user_prefs.discard(element_id)

        # Update expertise assessment if difficulty rating provided
        if difficulty_rating:
            self._update_expertise_assessment(user_id, element, difficulty_rating)

    def _should_show_element(
        self,
        element: UIElement,
        user_expertise: UserExpertiseLevel,
        context: str,
        user_preferences: Set[str],
    ) -> bool:
        """Determine if an element should be shown to the user."""
        # Check expertise requirement
        if not self._meets_expertise_requirement(element, user_expertise):
            return False

        # Check user preferences
        if element.element_id in user_preferences:
            return True

        # Check context relevance
        if not self._is_relevant_to_context(element, context):
            return False

        # Check dependencies
        if not self._dependencies_satisfied(element, user_preferences):
            return False

        # Check conflicts
        if self._has_conflicts(element, user_preferences):
            return False

        return True

    def _meets_expertise_requirement(
        self, element: UIElement, user_expertise: UserExpertiseLevel
    ) -> bool:
        """Check if user meets the expertise requirement for an element."""
        expertise_hierarchy = {
            UserExpertiseLevel.BEGINNER: 1,
            UserExpertiseLevel.INTERMEDIATE: 2,
            UserExpertiseLevel.ADVANCED: 3,
            UserExpertiseLevel.EXPERT: 4,
        }

        user_level = expertise_hierarchy.get(user_expertise, 1)
        required_level = expertise_hierarchy.get(element.expertise_required, 1)

        return user_level >= required_level

    def _is_relevant_to_context(self, element: UIElement, context: str) -> bool:
        """Check if element is relevant to current context."""
        # Simple context matching - could be enhanced with ML
        context_keywords = context.lower().split("_")

        for keyword in context_keywords:
            if (
                keyword in element.category.lower()
                or keyword in element.display_name.lower()
            ):
                return True

        return False

    def _dependencies_satisfied(
        self, element: UIElement, user_preferences: Set[str]
    ) -> bool:
        """Check if all prerequisite elements are satisfied."""
        for prereq in element.prerequisite_elements:
            if prereq not in user_preferences:
                return False
        return True

    def _has_conflicts(self, element: UIElement, user_preferences: Set[str]) -> bool:
        """Check if element conflicts with currently visible elements."""
        for conflict in element.conflicting_elements:
            if conflict in user_preferences:
                return True
        return False

    def _calculate_element_relevance(
        self, element: UIElement, user_expertise: UserExpertiseLevel, context: str
    ) -> float:
        """Calculate how relevant an element is to the current user and context."""
        relevance = 0.5  # Base relevance

        # Boost for matching expertise level
        if element.expertise_required == user_expertise:
            relevance += 0.2

        # Boost for context relevance
        if self._is_relevant_to_context(element, context):
            relevance += 0.2

        # Boost for high usage frequency
        relevance += element.usage_frequency * 0.1

        # Boost for high user satisfaction
        relevance += element.user_satisfaction * 0.1

        return min(relevance, 1.0)

    def _get_elements_for_disclosure_level(
        self, disclosure_level: DisclosureLevel, context: str
    ) -> List[UIElement]:
        """Get elements appropriate for a disclosure level."""
        appropriate_elements = []

        for element in self.ui_elements.values():
            if self._is_appropriate_for_disclosure_level(element, disclosure_level):
                if self._is_relevant_to_context(element, context):
                    appropriate_elements.append(element)

        return appropriate_elements

    def _is_appropriate_for_disclosure_level(
        self, element: UIElement, disclosure_level: DisclosureLevel
    ) -> bool:
        """Check if element is appropriate for the disclosure level."""
        level_requirements = {
            DisclosureLevel.MINIMAL: [UIComplexityLevel.SIMPLE],
            DisclosureLevel.BASIC: [
                UIComplexityLevel.SIMPLE,
                UIComplexityLevel.MODERATE,
            ],
            DisclosureLevel.INTERMEDIATE: [
                UIComplexityLevel.SIMPLE,
                UIComplexityLevel.MODERATE,
                UIComplexityLevel.COMPLEX,
            ],
            DisclosureLevel.ADVANCED: [
                UIComplexityLevel.SIMPLE,
                UIComplexityLevel.MODERATE,
                UIComplexityLevel.COMPLEX,
                UIComplexityLevel.TECHNICAL,
            ],
            DisclosureLevel.EXPERT: [
                UIComplexityLevel.SIMPLE,
                UIComplexityLevel.MODERATE,
                UIComplexityLevel.COMPLEX,
                UIComplexityLevel.TECHNICAL,
            ],
        }

        required_levels = level_requirements.get(disclosure_level, [])
        return element.complexity_level in required_levels

    def _simplify_element_for_user(
        self, element: UIElement, user_expertise: UserExpertiseLevel
    ) -> Dict[str, Any]:
        """Simplify UI element presentation for the user's expertise level."""
        simplified = {
            "id": element.element_id,
            "name": element.display_name,
            "description": element.description,
            "category": element.category,
            "complexity": element.complexity_level.value,
        }

        # Simplify for beginners
        if user_expertise == UserExpertiseLevel.BEGINNER:
            # Use simpler language
            simplified["description"] = self._simplify_description(element.description)
            simplified["show_help"] = True

        # Add usage hints for beginners
        if user_expertise == UserExpertiseLevel.BEGINNER:
            simplified["usage_tip"] = self._get_usage_tip(element)

        return simplified

    def _simplify_description(self, description: str) -> str:
        """Simplify a description for beginner users."""
        # Remove technical jargon
        simple_description = description

        technical_terms = [
            "configuration",
            "parameter",
            "integration",
            "deployment",
            "architecture",
        ]
        simple_terms = ["setup", "setting", "connection", "launch", "structure"]

        for tech, simple in zip(technical_terms, simple_terms):
            simple_description = simple_description.replace(tech, simple)

        return simple_description

    def _get_usage_tip(self, element: UIElement) -> str:
        """Get a usage tip for an element."""
        tips = {
            "project_setup": "Start here to create your project plan",
            "code_analysis": "Check your code quality and find improvements",
            "testing": "Make sure your code works as expected",
            "deployment": "Get your project ready for users",
        }

        return tips.get(element.category, "Click to get started")

    def _determine_help_level(
        self,
        user_expertise: UserExpertiseLevel,
        difficulty_level: str,
        current_action: str,
    ) -> Dict[str, Any]:
        """Determine the appropriate help level for the user."""
        help_config = {
            "level": "basic",
            "show_tips": True,
            "show_examples": False,
            "show_advanced": False,
        }

        # Beginners need more help
        if user_expertise == UserExpertiseLevel.BEGINNER:
            help_config.update(
                {
                    "level": "comprehensive",
                    "show_tips": True,
                    "show_examples": True,
                    "show_advanced": False,
                }
            )

        # Advanced users need less help
        elif user_expertise in [UserExpertiseLevel.ADVANCED, UserExpertiseLevel.EXPERT]:
            help_config.update(
                {
                    "level": "minimal",
                    "show_tips": difficulty_level == "high",
                    "show_examples": False,
                    "show_advanced": True,
                }
            )

        # Adjust based on difficulty
        if difficulty_level == "high":
            help_config["show_examples"] = True
            help_config["show_tips"] = True

        return help_config

    def _get_user_expertise(self, user_id: str) -> UserExpertiseLevel:
        """Get user's expertise level."""
        if user_id in self.user_expertise_cache:
            return self.user_expertise_cache[user_id]

        # Try to get from preference system
        try:
            user_prefs = self.preference_system.get_user_preferences(user_id)
            expertise_str = user_prefs.get("expertise_level", "intermediate")
            expertise = UserExpertiseLevel(expertise_str)
            self.user_expertise_cache[user_id] = expertise
            return expertise
        except:
            # Default to intermediate
            return UserExpertiseLevel.INTERMEDIATE

    def _get_user_preferences(self, user_id: str) -> Set[str]:
        """Get user's UI element preferences."""
        if user_id in self.user_preferences_cache:
            return self.user_preferences_cache[user_id]

        # Default empty preferences
        return set()

    def _update_expertise_assessment(
        self, user_id: str, element: UIElement, difficulty_rating: int
    ) -> None:
        """Update expertise assessment based on user feedback."""
        # Simple expertise adjustment based on difficulty ratings
        # This could be enhanced with more sophisticated ML

        current_expertise = self._get_user_expertise(user_id)

        # If user found a complex element easy, they might be more advanced
        if (
            element.complexity_level
            in [UIComplexityLevel.COMPLEX, UIComplexityLevel.TECHNICAL]
            and difficulty_rating <= 2
        ):
            # User handled complex element easily - upgrade expertise
            if current_expertise == UserExpertiseLevel.INTERMEDIATE:
                self.user_expertise_cache[user_id] = UserExpertiseLevel.ADVANCED

        # If user found a simple element difficult, they might be less advanced
        elif (
            element.complexity_level == UIComplexityLevel.SIMPLE
            and difficulty_rating >= 4
        ):
            # User found simple element difficult - downgrade expertise
            if current_expertise == UserExpertiseLevel.ADVANCED:
                self.user_expertise_cache[user_id] = UserExpertiseLevel.INTERMEDIATE

    def _load_disclosure_rules(self) -> Dict[str, Any]:
        """Load progressive disclosure rules."""
        # Default rules - could be loaded from config file
        return {
            "beginner_max_elements": 5,
            "intermediate_max_elements": 10,
            "advanced_max_elements": 15,
            "show_technical_details": False,
            "simplify_language": True,
        }

    def _initialize_default_elements(self) -> None:
        """Initialize default UI elements."""
        default_elements = [
            UIElement(
                element_id="project_charter",
                display_name="Create Project Plan",
                description="Set up your project goals and requirements",
                complexity_level=UIComplexityLevel.SIMPLE,
                expertise_required=UserExpertiseLevel.BEGINNER,
                category="project_setup",
            ),
            UIElement(
                element_id="code_analysis",
                display_name="Check Code Quality",
                description="Analyze your code for improvements and issues",
                complexity_level=UIComplexityLevel.MODERATE,
                expertise_required=UserExpertiseLevel.INTERMEDIATE,
                category="development",
            ),
            UIElement(
                element_id="testing_suite",
                display_name="Run Tests",
                description="Test your code to ensure it works correctly",
                complexity_level=UIComplexityLevel.MODERATE,
                expertise_required=UserExpertiseLevel.INTERMEDIATE,
                category="testing",
            ),
            UIElement(
                element_id="deployment_config",
                display_name="Deploy Project",
                description="Set up deployment configuration and launch",
                complexity_level=UIComplexityLevel.COMPLEX,
                expertise_required=UserExpertiseLevel.ADVANCED,
                category="deployment",
            ),
            UIElement(
                element_id="advanced_analysis",
                display_name="Deep Code Analysis",
                description="Advanced analysis with custom rules and metrics",
                complexity_level=UIComplexityLevel.TECHNICAL,
                expertise_required=UserExpertiseLevel.EXPERT,
                category="development",
            ),
        ]

        for element in default_elements:
            self.register_ui_element(element)

    def get_interface_recommendations(
        self, user_id: str, context: str
    ) -> Dict[str, Any]:
        """
        Get interface recommendations for optimal user experience.

        Args:
            user_id: User identifier
            context: Current context

        Returns:
            Interface recommendations
        """
        user_expertise = self._get_user_expertise(user_id)

        recommendations = {
            "recommended_layout": (
                "simple"
                if user_expertise == UserExpertiseLevel.BEGINNER
                else "standard"
            ),
            "show_help": user_expertise
            in [UserExpertiseLevel.BEGINNER, UserExpertiseLevel.INTERMEDIATE],
            "show_advanced_options": user_expertise
            in [UserExpertiseLevel.ADVANCED, UserExpertiseLevel.EXPERT],
            "group_related_elements": True,
            "highlight_primary_actions": True,
            "context": context,
        }

        return recommendations


def get_progressive_disclosure_engine(root: Path) -> ProgressiveDisclosureEngine:
    """Get progressive disclosure engine instance."""
    return ProgressiveDisclosureEngine(root)
