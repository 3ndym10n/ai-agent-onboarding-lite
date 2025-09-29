"""
User Journey Mapping - Guide users through complex workflows simply.

This module provides intelligent user journey mapping that breaks down complex
development workflows into simple, manageable steps tailored to the user's
expertise level. It prevents users from feeling overwhelmed while ensuring
they complete all necessary steps.
"""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base.shared_types import JourneyStage, StepComplexity, UserExpertiseLevel
from .user_preference_learning import get_user_preference_learning_system

# Note: UserExpertiseLevel, JourneyStage, StepComplexity now imported from shared_types


@dataclass
class JourneyStep:
    """A single step in a user journey."""

    step_id: str
    title: str
    description: str
    complexity: StepComplexity
    estimated_time_minutes: int

    # Journey flow
    stage: JourneyStage
    order: int
    prerequisites: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)

    # User experience
    beginner_friendly: bool = True
    requires_clarification: bool = False
    can_be_skipped: bool = False

    # Help and guidance
    help_text: str = ""
    common_mistakes: List[str] = field(default_factory=list)
    success_indicators: List[str] = field(default_factory=list)

    # Progress tracking
    completion_criteria: List[str] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)


class UserJourney:
    """A complete user journey with adaptive steps."""

    def __init__(self, journey_id: str, name: str, description: str):
        self.journey_id = journey_id
        self.name = name
        self.description = description
        self.steps: Dict[str, JourneyStep] = {}
        self.step_order: List[str] = []

    def add_step(self, step: JourneyStep) -> None:
        """Add a step to the journey."""
        self.steps[step.step_id] = step
        self.step_order.append(step.step_id)

        # Sort by order
        self.step_order.sort(key=lambda sid: self.steps[sid].order)

    def get_steps_for_user(
        self, user_expertise: UserExpertiseLevel
    ) -> List[JourneyStep]:
        """Get journey steps appropriate for the user's expertise level."""
        appropriate_steps = []

        for step_id in self.step_order:
            step = self.steps[step_id]

            # Filter based on expertise
            if self._step_appropriate_for_expertise(step, user_expertise):
                appropriate_steps.append(step)

        return appropriate_steps

    def _step_appropriate_for_expertise(
        self, step: JourneyStep, user_expertise: UserExpertiseLevel
    ) -> bool:
        """Check if step is appropriate for user's expertise level."""
        expertise_complexity_map = {
            UserExpertiseLevel.BEGINNER: [
                StepComplexity.TRIVIAL,
                StepComplexity.SIMPLE,
            ],
            UserExpertiseLevel.INTERMEDIATE: [
                StepComplexity.TRIVIAL,
                StepComplexity.SIMPLE,
                StepComplexity.MODERATE,
            ],
            UserExpertiseLevel.ADVANCED: [
                StepComplexity.TRIVIAL,
                StepComplexity.SIMPLE,
                StepComplexity.MODERATE,
                StepComplexity.COMPLEX,
            ],
            UserExpertiseLevel.EXPERT: [
                StepComplexity.TRIVIAL,
                StepComplexity.SIMPLE,
                StepComplexity.MODERATE,
                StepComplexity.COMPLEX,
                StepComplexity.TECHNICAL,
            ],
        }

        allowed_complexities = expertise_complexity_map.get(
            user_expertise, [StepComplexity.TRIVIAL, StepComplexity.SIMPLE]
        )
        return step.complexity in allowed_complexities


class UserJourneyMapper:
    """Maps user needs to appropriate development journeys."""

    def __init__(self, root: Path):
        self.root = root
        self.preference_system = get_user_preference_learning_system(root)

        # Journey library
        self.journeys: Dict[str, UserJourney] = {}

        # User progress tracking
        self.user_journeys: Dict[str, Dict[str, Any]] = {}

        # Initialize default journeys
        self._initialize_default_journeys()

    def get_recommended_journey(
        self, user_request: str, user_id: str, project_context: Dict[str, Any] = None
    ) -> Optional[UserJourney]:
        """
        Get the most appropriate journey for a user's request.

        Args:
            user_request: The user's request
            user_id: User identifier
            project_context: Additional context about the project

        Returns:
            Recommended journey or None if no suitable journey found
        """
        user_expertise = self._get_user_expertise(user_id)

        # Analyze request to determine journey type
        journey_type = self._determine_journey_type(user_request, project_context)

        # Get appropriate journey
        journey = self.journeys.get(journey_type)
        if not journey:
            return None

        # Customize journey for user expertise
        customized_journey = self._customize_journey_for_user(
            journey, user_expertise, user_id
        )

        # Track journey start
        self._track_journey_start(user_id, journey.journey_id)

        return customized_journey

    def get_current_step(self, user_id: str, journey_id: str) -> Optional[JourneyStep]:
        """
        Get the current step in a user's journey.

        Args:
            user_id: User identifier
            journey_id: Journey identifier

        Returns:
            Current journey step or None if journey not found
        """
        if user_id not in self.user_journeys:
            return None

        user_journey = self.user_journeys[user_id]
        if journey_id not in user_journey:
            return None

        journey_data = user_journey[journey_id]
        current_step_index = journey_data.get("current_step_index", 0)
        completed_steps = journey_data.get("completed_steps", [])

        # Get journey
        journey = self.journeys.get(journey_id)
        if not journey:
            return None

        # Find next incomplete step
        for step_id in journey.step_order:
            if step_id not in completed_steps:
                return journey.steps[step_id]

        return None  # All steps completed

    def mark_step_complete(
        self, user_id: str, journey_id: str, step_id: str, success: bool = True
    ) -> None:
        """
        Mark a journey step as complete.

        Args:
            user_id: User identifier
            journey_id: Journey identifier
            step_id: Step identifier
            success: Whether the step was completed successfully
        """
        if user_id not in self.user_journeys:
            self.user_journeys[user_id] = {}

        if journey_id not in self.user_journeys[user_id]:
            self.user_journeys[user_id][journey_id] = {
                "started_at": time.time(),
                "completed_steps": [],
                "current_step_index": 0,
            }

        journey_data = self.user_journeys[user_id][journey_id]

        if step_id not in journey_data["completed_steps"]:
            journey_data["completed_steps"].append(step_id)

        # Update current step
        journey = self.journeys.get(journey_id)
        if journey:
            current_index = journey.step_order.index(step_id)
            journey_data["current_step_index"] = min(
                current_index + 1, len(journey.step_order) - 1
            )

        # Track completion
        self._track_step_completion(user_id, journey_id, step_id, success)

    def get_journey_progress(self, user_id: str, journey_id: str) -> Dict[str, Any]:
        """
        Get progress information for a user's journey.

        Args:
            user_id: User identifier
            journey_id: Journey identifier

        Returns:
            Progress information
        """
        if (
            user_id not in self.user_journeys
            or journey_id not in self.user_journeys[user_id]
        ):
            return {"error": "Journey not found"}

        journey_data = self.user_journeys[user_id][journey_id]
        journey = self.journeys.get(journey_id)

        if not journey:
            return {"error": "Journey definition not found"}

        completed_steps = journey_data.get("completed_steps", [])
        total_steps = len(journey.step_order)

        progress_percentage = (len(completed_steps) / total_steps) * 100

        current_step = None
        for step_id in journey.step_order:
            if step_id not in completed_steps:
                current_step = journey.steps[step_id]
                break

        return {
            "journey_id": journey_id,
            "journey_name": journey.name,
            "progress_percentage": progress_percentage,
            "completed_steps": len(completed_steps),
            "total_steps": total_steps,
            "current_step": current_step.title if current_step else "Complete",
            "started_at": journey_data.get("started_at"),
            "estimated_time_remaining": self._estimate_remaining_time(
                completed_steps, journey
            ),
        }

    def _determine_journey_type(
        self, user_request: str, project_context: Dict[str, Any] = None
    ) -> str:
        """Determine the appropriate journey type for a request."""
        request_lower = user_request.lower()

        # Simple keyword-based journey mapping
        if any(word in request_lower for word in ["website", "web app", "webpage"]):
            return "web_development"
        elif any(word in request_lower for word in ["mobile", "app", "phone"]):
            return "mobile_development"
        elif any(word in request_lower for word in ["data", "database", "api"]):
            return "data_application"
        elif any(word in request_lower for word in ["learn", "tutorial", "education"]):
            return "learning_platform"
        elif any(word in request_lower for word in ["shop", "store", "sell", "buy"]):
            return "ecommerce"
        else:
            return "general_development"

    def _customize_journey_for_user(
        self, journey: UserJourney, user_expertise: UserExpertiseLevel, user_id: str
    ) -> UserJourney:
        """Customize a journey for a specific user's expertise level."""
        # Create a copy of the journey
        customized = UserJourney(journey.journey_id, journey.name, journey.description)

        # Add only appropriate steps
        user_steps = journey.get_steps_for_user(user_expertise)
        for step in user_steps:
            customized.add_step(step)

        return customized

    def _get_user_expertise(self, user_id: str) -> UserExpertiseLevel:
        """Get user's expertise level."""
        try:
            user_prefs = self.preference_system.get_user_preferences(user_id)
            expertise_str = user_prefs.get("expertise_level", "intermediate")
            return UserExpertiseLevel(expertise_str)
        except:
            return UserExpertiseLevel.INTERMEDIATE

    def _track_journey_start(self, user_id: str, journey_id: str) -> None:
        """Track when a user starts a journey."""
        if user_id not in self.user_journeys:
            self.user_journeys[user_id] = {}

        self.user_journeys[user_id][journey_id] = {
            "started_at": time.time(),
            "completed_steps": [],
            "current_step_index": 0,
        }

    def _track_step_completion(
        self, user_id: str, journey_id: str, step_id: str, success: bool
    ) -> None:
        """Track step completion for analytics."""
        # Could be extended to track detailed analytics
        pass

    def _estimate_remaining_time(
        self, completed_steps: List[str], journey: UserJourney
    ) -> int:
        """Estimate remaining time for a journey."""
        remaining_steps = []

        for step_id in journey.step_order:
            if step_id not in completed_steps:
                remaining_steps.append(journey.steps[step_id])

        if not remaining_steps:
            return 0

        # Simple estimation based on step complexity
        time_mapping = {
            StepComplexity.TRIVIAL: 2,
            StepComplexity.SIMPLE: 5,
            StepComplexity.MODERATE: 15,
            StepComplexity.COMPLEX: 30,
            StepComplexity.TECHNICAL: 45,
        }

        total_time = sum(
            time_mapping.get(step.complexity, 15) for step in remaining_steps
        )
        return total_time

    def _initialize_default_journeys(self) -> None:
        """Initialize default user journeys."""

        # Web Development Journey
        web_journey = UserJourney(
            "web_development",
            "Web Application Development",
            "Complete journey for building a web application",
        )

        web_steps = [
            JourneyStep(
                step_id="web_1",
                title="Define Your Project",
                description="Clearly define what you want to build",
                complexity=StepComplexity.SIMPLE,
                estimated_time_minutes=10,
                stage=JourneyStage.DISCOVERY,
                order=1,
                help_text="Think about what problem you're solving and who will use your app",
                success_indicators=[
                    "Clear project description",
                    "Identified target users",
                ],
            ),
            JourneyStep(
                step_id="web_2",
                title="Plan Your Features",
                description="Decide what features your app needs",
                complexity=StepComplexity.MODERATE,
                estimated_time_minutes=20,
                stage=JourneyStage.PLANNING,
                order=2,
                prerequisites=["web_1"],
                help_text="Start with core features and add nice-to-have features later",
                success_indicators=["Feature list created", "Priorities set"],
            ),
            JourneyStep(
                step_id="web_3",
                title="Choose Technology Stack",
                description="Select the right tools and technologies",
                complexity=StepComplexity.MODERATE,
                estimated_time_minutes=15,
                stage=JourneyStage.PLANNING,
                order=3,
                prerequisites=["web_2"],
                help_text="We'll suggest technologies based on your project needs",
                success_indicators=[
                    "Technology stack selected",
                    "Dependencies identified",
                ],
            ),
            JourneyStep(
                step_id="web_4",
                title="Set Up Development Environment",
                description="Get your development tools ready",
                complexity=StepComplexity.MODERATE,
                estimated_time_minutes=30,
                stage=JourneyStage.SETUP,
                order=4,
                prerequisites=["web_3"],
                help_text="Install necessary software and set up your project structure",
                success_indicators=[
                    "Development environment working",
                    "Project structure created",
                ],
            ),
            JourneyStep(
                step_id="web_5",
                title="Build Core Features",
                description="Implement the main functionality",
                complexity=StepComplexity.COMPLEX,
                estimated_time_minutes=120,
                stage=JourneyStage.DEVELOPMENT,
                order=5,
                prerequisites=["web_4"],
                help_text="Focus on getting the core features working first",
                success_indicators=[
                    "Core features implemented",
                    "Basic functionality working",
                ],
            ),
            JourneyStep(
                step_id="web_6",
                title="Test Your Application",
                description="Make sure everything works correctly",
                complexity=StepComplexity.MODERATE,
                estimated_time_minutes=45,
                stage=JourneyStage.TESTING,
                order=6,
                prerequisites=["web_5"],
                help_text="Test all features and fix any issues",
                success_indicators=["Tests pass", "No critical bugs found"],
            ),
            JourneyStep(
                step_id="web_7",
                title="Deploy Your Application",
                description="Make your app available to users",
                complexity=StepComplexity.MODERATE,
                estimated_time_minutes=30,
                stage=JourneyStage.DEPLOYMENT,
                order=7,
                prerequisites=["web_6"],
                help_text="Set up hosting and make your app live",
                success_indicators=["App deployed successfully", "Users can access it"],
            ),
        ]

        for step in web_steps:
            web_journey.add_step(step)

        self.journeys["web_development"] = web_journey

        # Simple Project Journey (for beginners)
        simple_journey = UserJourney(
            "simple_project",
            "Simple Project Development",
            "Simplified journey for basic projects",
        )

        simple_steps = [
            JourneyStep(
                step_id="simple_1",
                title="Tell Us What You Want",
                description="Describe your project in simple terms",
                complexity=StepComplexity.TRIVIAL,
                estimated_time_minutes=5,
                stage=JourneyStage.DISCOVERY,
                order=1,
                beginner_friendly=True,
                help_text="Just tell us what you want to build - we'll figure out the details",
            ),
            JourneyStep(
                step_id="simple_2",
                title="Review Our Plan",
                description="Check that our plan matches what you want",
                complexity=StepComplexity.SIMPLE,
                estimated_time_minutes=10,
                stage=JourneyStage.PLANNING,
                order=2,
                prerequisites=["simple_1"],
                beginner_friendly=True,
                help_text="We'll show you our plan - just say if it looks right",
            ),
            JourneyStep(
                step_id="simple_3",
                title="Build It",
                description="We'll build your project while you watch",
                complexity=StepComplexity.SIMPLE,
                estimated_time_minutes=60,
                stage=JourneyStage.DEVELOPMENT,
                order=3,
                prerequisites=["simple_2"],
                beginner_friendly=True,
                help_text="We'll do the technical work - you just need to approve decisions",
            ),
            JourneyStep(
                step_id="simple_4",
                title="Test It",
                description="Make sure everything works",
                complexity=StepComplexity.SIMPLE,
                estimated_time_minutes=15,
                stage=JourneyStage.TESTING,
                order=4,
                prerequisites=["simple_3"],
                beginner_friendly=True,
                help_text="We'll test it together and fix any issues",
            ),
        ]

        for step in simple_steps:
            simple_journey.add_step(step)

        self.journeys["simple_project"] = simple_journey

    def get_available_journeys(
        self, user_expertise: UserExpertiseLevel
    ) -> List[Dict[str, Any]]:
        """Get available journeys appropriate for user's expertise level."""
        available = []

        for journey in self.journeys.values():
            # Count steps appropriate for user
            user_steps = journey.get_steps_for_user(user_expertise)
            total_time = sum(step.estimated_time_minutes for step in user_steps)

            if user_steps:  # Only include if there are steps for this expertise level
                available.append(
                    {
                        "journey_id": journey.journey_id,
                        "name": journey.name,
                        "description": journey.description,
                        "step_count": len(user_steps),
                        "estimated_time_minutes": total_time,
                        "suitable_for_expertise": user_expertise.value,
                    }
                )

        return available

    def get_journey_recommendations(
        self, user_request: str, user_expertise: UserExpertiseLevel
    ) -> List[Dict[str, Any]]:
        """
        Get journey recommendations based on user request and expertise.

        Args:
            user_request: The user's request
            user_expertise: User's expertise level

        Returns:
            List of recommended journeys with explanations
        """
        journey_type = self._determine_journey_type(user_request)

        recommendations = []

        # Primary recommendation
        if journey_type in self.journeys:
            journey = self.journeys[journey_type]
            user_steps = journey.get_steps_for_user(user_expertise)
            total_time = sum(step.estimated_time_minutes for step in user_steps)

            recommendations.append(
                {
                    "journey_id": journey.journey_id,
                    "name": journey.name,
                    "description": journey.description,
                    "match_reason": f"Best match for '{user_request}'",
                    "step_count": len(user_steps),
                    "estimated_time_minutes": total_time,
                    "confidence": 0.9,
                    "recommended": True,
                }
            )

        # Alternative recommendations
        alternatives = [
            j for j in self.journeys.values() if j.journey_id != journey_type
        ]
        for journey in alternatives[:2]:  # Show top 2 alternatives
            user_steps = journey.get_steps_for_user(user_expertise)
            if user_steps:
                total_time = sum(step.estimated_time_minutes for step in user_steps)

                recommendations.append(
                    {
                        "journey_id": journey.journey_id,
                        "name": journey.name,
                        "description": journey.description,
                        "match_reason": "Alternative approach",
                        "step_count": len(user_steps),
                        "estimated_time_minutes": total_time,
                        "confidence": 0.5,
                        "recommended": False,
                    }
                )

        return recommendations


def get_user_journey_mapper(root: Path) -> UserJourneyMapper:
    """Get user journey mapper instance."""
    return UserJourneyMapper(root)
