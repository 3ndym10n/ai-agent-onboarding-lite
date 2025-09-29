"""
Prompt-Based Journey Mapper - Uses AI prompts to determine appropriate development workflows.

This replaces hardcoded journey mapping with intelligent prompt-based analysis
that can adapt to different project types and user contexts.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PromptBasedJourneyStep:
    """A journey step defined by AI prompts."""

    step_id: str
    title: str
    description: str
    complexity: str
    estimated_time_minutes: int
    stage: str
    prerequisites: List[str] = field(default_factory=list)
    help_text: str = ""
    success_indicators: List[str] = field(default_factory=list)


@dataclass
class PromptBasedJourney:
    """A development journey created by AI prompts."""

    journey_id: str
    name: str
    description: str
    steps: Dict[str, PromptBasedJourneyStep] = field(default_factory=dict)
    step_order: List[str] = field(default_factory=list)
    reasoning: str = ""
    confidence_score: float = 0.0
    alternative_journeys: List[str] = field(default_factory=list)


class PromptBasedJourneyMapper:
    """Uses AI prompts to map user needs to appropriate development journeys."""

    def __init__(self, root: Path):
        self.root = root
        self.cache: Dict[str, PromptBasedJourney] = {}

    def get_recommended_journey(
        self,
        user_request: str,
        user_id: str,
        project_context: Optional[Dict[str, Any]] = None,
    ) -> Optional[PromptBasedJourney]:
        """Get AI-recommended journey for user request."""

        # Check cache first
        cache_key = f"{user_request}:{user_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Create journey analysis prompt
        analysis_prompt = self._create_journey_analysis_prompt(
            user_request, user_id, project_context
        )

        # Get AI analysis (placeholder - would call actual LLM)
        analysis_result = self._get_ai_journey_analysis(analysis_prompt, user_request)

        # Parse structured journey
        journey = self._parse_journey_result(user_request, analysis_result)

        # Cache result
        self.cache[cache_key] = journey

        return journey

    def _create_journey_analysis_prompt(
        self, user_request: str, user_id: str, context: Dict[str, Any]
    ) -> str:
        """Create a prompt for analyzing appropriate development journey."""

        context_str = ""
        if context:
            context_str = f"\nProject Context: {context}"

        return f"""
You are an expert software project consultant. Based on this user request, recommend the most appropriate development journey:

USER REQUEST: "{user_request}"{context_str}

Please provide a detailed journey recommendation in this exact JSON format:

{{
    "journey_id": "unique_journey_id",
    "journey_name": "Descriptive journey name",
    "journey_description": "Brief description of this development approach",
    "confidence_score": 0.0-1.0,
    "reasoning": "Explain why this journey is recommended",
    "steps": [
        {{
            "step_id": "step_1",
            "title": "Clear step title",
            "description": "What needs to be done",
            "complexity": "simple|moderate|complex",
            "estimated_time_minutes": 30,
            "stage": "discovery|planning|setup|development|testing|deployment",
            "prerequisites": ["step_0"],
            "help_text": "Guidance for this step",
            "success_indicators": ["What shows this step is complete"]
        }}
    ],
    "alternative_journeys": ["alternative_1", "alternative_2"],
    "estimated_total_time": 240,
    "risk_factors": ["factor1", "factor2"]
}}

Consider:
- What type of project is this?
- What's the user's expertise level?
- What's the project complexity?
- What are the key milestones?
- What dependencies exist?

Return only valid JSON.
"""

    def _get_ai_journey_analysis(
        self, prompt: str, user_request: str
    ) -> Dict[str, Any]:
        """Get journey analysis from AI model (placeholder - would call actual LLM)."""

        # This is where you'd call an actual LLM like GPT, Claude, etc.
        # For now, simulate intelligent journey mapping

        analysis = {
            "journey_id": "prompt_based_journey_001",
            "journey_name": self._determine_journey_name(user_request),
            "journey_description": self._generate_journey_description(user_request),
            "confidence_score": 0.85,
            "reasoning": self._generate_journey_reasoning(user_request),
            "steps": self._generate_journey_steps(user_request),
            "alternative_journeys": self._get_alternative_journeys(user_request),
            "estimated_total_time": self._estimate_total_time(user_request),
            "risk_factors": self._get_risk_factors(user_request),
        }

        return analysis

    def _parse_journey_result(
        self, user_request: str, analysis: Dict[str, Any]
    ) -> PromptBasedJourney:
        """Parse AI analysis into structured journey."""

        journey = PromptBasedJourney(
            journey_id=analysis["journey_id"],
            name=analysis["journey_name"],
            description=analysis["journey_description"],
            reasoning=analysis["reasoning"],
            confidence_score=analysis["confidence_score"],
            alternative_journeys=analysis["alternative_journeys"],
        )

        # Add steps
        for step_data in analysis["steps"]:
            step = PromptBasedJourneyStep(
                step_id=step_data["step_id"],
                title=step_data["title"],
                description=step_data["description"],
                complexity=step_data["complexity"],
                estimated_time_minutes=step_data["estimated_time_minutes"],
                stage=step_data["stage"],
                prerequisites=step_data.get("prerequisites", []),
                help_text=step_data.get("help_text", ""),
                success_indicators=step_data.get("success_indicators", []),
            )
            journey.steps[step.step_id] = step
            journey.step_order.append(step.step_id)

        return journey

    def _determine_journey_name(self, request: str) -> str:
        """Determine journey name from request."""
        request_lower = request.lower()

        if "website" in request_lower and "buy" in request_lower:
            return "E-commerce Website Development"
        elif "app" in request_lower:
            return "Mobile Application Development"
        elif "data" in request_lower or "database" in request_lower:
            return "Data-Driven Application Development"
        else:
            return "Custom Software Development"

    def _generate_journey_description(self, request: str) -> str:
        """Generate journey description."""
        return f"Comprehensive development approach for: {request[:50]}..."

    def _generate_journey_reasoning(self, request: str) -> str:
        """Generate reasoning for journey recommendation."""
        return f"Based on the request '{request}', this journey provides a structured approach to building the requested application with appropriate complexity and user guidance."

    def _generate_journey_steps(self, request: str) -> List[Dict[str, Any]]:
        """Generate journey steps using AI logic."""

        # This would be much more sophisticated with actual AI
        steps = [
            {
                "step_id": "analyze_requirements",
                "title": "Analyze Requirements",
                "description": "Understand what the user actually needs",
                "complexity": "simple",
                "estimated_time_minutes": 15,
                "stage": "discovery",
                "help_text": "Clarify the core problem being solved",
                "success_indicators": ["Requirements documented", "Scope defined"],
            },
            {
                "step_id": "plan_architecture",
                "title": "Plan Architecture",
                "description": "Design the overall system structure",
                "complexity": "moderate",
                "estimated_time_minutes": 30,
                "stage": "planning",
                "prerequisites": ["analyze_requirements"],
                "help_text": "Choose appropriate technologies and structure",
                "success_indicators": ["Architecture decided", "Tech stack chosen"],
            },
            {
                "step_id": "setup_environment",
                "title": "Set Up Development Environment",
                "description": "Prepare tools and development setup",
                "complexity": "moderate",
                "estimated_time_minutes": 45,
                "stage": "setup",
                "prerequisites": ["plan_architecture"],
                "help_text": "Install dependencies and configure development tools",
                "success_indicators": ["Environment working", "Dependencies installed"],
            },
            {
                "step_id": "build_core_features",
                "title": "Build Core Features",
                "description": "Implement the main application functionality",
                "complexity": "complex",
                "estimated_time_minutes": 120,
                "stage": "development",
                "prerequisites": ["setup_environment"],
                "help_text": "Focus on core features first, add advanced features later",
                "success_indicators": [
                    "Core features working",
                    "Basic functionality complete",
                ],
            },
            {
                "step_id": "test_and_validate",
                "title": "Test and Validate",
                "description": "Ensure quality and fix any issues",
                "complexity": "moderate",
                "estimated_time_minutes": 60,
                "stage": "testing",
                "prerequisites": ["build_core_features"],
                "help_text": "Test thoroughly and fix any bugs",
                "success_indicators": ["Tests pass", "No critical issues"],
            },
        ]

        return steps

    def _get_alternative_journeys(self, request: str) -> List[str]:
        """Get alternative journey suggestions."""
        return ["rapid_prototyping", "full_stack_development", "microservices_approach"]

    def _estimate_total_time(self, request: str) -> int:
        """Estimate total journey time."""
        # Simple estimation - would be more sophisticated with AI
        return 270  # 4.5 hours

    def _get_risk_factors(self, request: str) -> List[str]:
        """Get risk factors for the journey."""
        return ["medium_complexity", "timeline_pressure"]


def get_prompt_based_journey_mapper(root: Path) -> PromptBasedJourneyMapper:
    """Get prompt-based journey mapper instance."""
    return PromptBasedJourneyMapper(root)
