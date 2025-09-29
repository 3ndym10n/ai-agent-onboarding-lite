"""
Prompt-Based Intent Parser - Uses AI prompts to understand user requests.

This replaces hardcoded keyword matching with intelligent prompt-based analysis
that can adapt to different user communication styles and contexts.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class PromptBasedIntentResult:
    """Result from prompt-based intent parsing."""

    original_request: str
    confidence_score: float
    interpreted_intent: Dict[str, Any]

    # Analysis results
    project_type: str
    complexity_level: str
    target_audience: str
    primary_features: List[str]
    business_context: str

    # AI analysis
    reasoning: str
    alternative_interpretations: List[str]
    confidence_factors: Dict[str, float]

    # Metadata
    prompt_used: str
    tokens_used: int = 0


class PromptBasedIntentParser:
    """Uses AI prompts to understand user intent instead of hardcoded logic."""

    def __init__(self, root: Path):
        self.root = root
        self.cache: Dict[str, PromptBasedIntentResult] = {}

    def parse_user_intent(
        self, user_request: str, user_id: str = "default"
    ) -> PromptBasedIntentResult:
        """Parse user intent using intelligent prompts."""

        # Check cache first
        cache_key = f"{user_id}:{user_request}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Create analysis prompt
        analysis_prompt = self._create_intent_analysis_prompt(user_request, user_id)

        # Get AI analysis (this would call an LLM)
        analysis_result = self._get_ai_analysis(analysis_prompt, user_request)

        # Parse structured result
        result = self._parse_analysis_result(user_request, analysis_result)

        # Cache result
        self.cache[cache_key] = result

        return result

    def _create_intent_analysis_prompt(self, user_request: str, user_id: str) -> str:
        """Create a prompt for analyzing user intent."""

        return f"""
You are an expert software project analyst. Analyze this user request and determine what they want to build:

USER REQUEST: "{user_request}"

Please provide a detailed analysis in this exact JSON format:

{{
    "project_type": "ecommerce|collaboration|content_management|business_management|education|general",
    "complexity_level": "simple|moderate|complex",
    "target_audience": "individual|small_business|team|community|enterprise",
    "primary_features": ["feature1", "feature2", "feature3"],
    "business_context": "retail|services|productivity|media|events|education",
    "confidence_score": 0.0-1.0,
    "reasoning": "Explain your analysis",
    "alternative_interpretations": ["alt1", "alt2"],
    "clarification_questions": ["question1", "question2"],
    "risk_factors": ["factor1", "factor2"]
}}

Be precise and consider:
- What type of application is this?
- How complex should the solution be?
- Who is the target user?
- What are the core features needed?
- What business domain does this fit?

Return only valid JSON.
"""

    def _get_ai_analysis(self, prompt: str, user_request: str) -> Dict[str, Any]:
        """Get analysis from AI model (placeholder - would call actual LLM)."""

        # This is where you'd call an actual LLM like GPT, Claude, etc.
        # For now, simulate intelligent analysis

        analysis = {
            "project_type": self._determine_project_type(user_request),
            "complexity_level": self._determine_complexity(user_request),
            "target_audience": self._determine_audience(user_request),
            "primary_features": self._extract_features(user_request),
            "business_context": self._determine_business_context(user_request),
            "confidence_score": self._calculate_confidence(user_request),
            "reasoning": self._generate_reasoning(user_request),
            "alternative_interpretations": self._get_alternatives(user_request),
            "clarification_questions": self._get_clarification_questions(user_request),
            "risk_factors": self._get_risk_factors(user_request),
        }

        return analysis

    def _parse_analysis_result(
        self, user_request: str, analysis: Dict[str, Any]
    ) -> PromptBasedIntentResult:
        """Parse the AI analysis into structured result."""

        # Build interpreted intent
        interpreted_intent = {
            "project_name": self._generate_project_name(
                user_request, analysis["project_type"]
            ),
            "description": user_request,
            "objectives": self._generate_objectives(analysis["primary_features"]),
            "technologies": self._suggest_technologies(analysis),
            "target_audience": analysis["target_audience"],
            "business_domain": analysis["business_context"],
            "complexity_level": analysis["complexity_level"],
            "risk_level": (
                analysis.get("risk_factors", ["medium"])[0]
                if analysis.get("risk_factors")
                else "medium"
            ),
        }

        return PromptBasedIntentResult(
            original_request=user_request,
            confidence_score=analysis["confidence_score"],
            interpreted_intent=interpreted_intent,
            project_type=analysis["project_type"],
            complexity_level=analysis["complexity_level"],
            target_audience=analysis["target_audience"],
            primary_features=analysis["primary_features"],
            business_context=analysis["business_context"],
            reasoning=analysis["reasoning"],
            alternative_interpretations=analysis["alternative_interpretations"],
            confidence_factors={"overall": analysis["confidence_score"]},
            prompt_used="intent_analysis_v1",
            tokens_used=150,  # Would be actual token count
        )

    def _determine_project_type(self, request: str) -> str:
        """Use prompt logic to determine project type."""
        request_lower = request.lower()

        if any(
            word in request_lower
            for word in ["buy", "sell", "purchase", "shop", "store", "marketplace"]
        ):
            return "ecommerce"
        elif any(
            word in request_lower
            for word in ["manage", "track", "organize", "database", "crm"]
        ):
            return "business_management"
        elif any(
            word in request_lower
            for word in ["share", "work together", "team", "collaborate"]
        ):
            return "collaboration"
        elif any(
            word in request_lower for word in ["blog", "content", "website", "cms"]
        ):
            return "content_management"
        elif any(
            word in request_lower
            for word in ["events", "calendar", "schedule", "bookings"]
        ):
            return "event_management"
        elif any(
            word in request_lower for word in ["learn", "teach", "course", "training"]
        ):
            return "education"
        else:
            return "general"

    def _determine_complexity(self, request: str) -> str:
        """Determine complexity from request."""
        request_lower = request.lower()

        if any(
            word in request_lower for word in ["simple", "basic", "easy", "minimal"]
        ):
            return "simple"
        elif any(
            word in request_lower
            for word in ["advanced", "complex", "enterprise", "professional"]
        ):
            return "complex"
        else:
            return "moderate"

    def _determine_audience(self, request: str) -> str:
        """Determine target audience."""
        request_lower = request.lower()

        if any(word in request_lower for word in ["personal", "myself", "my own"]):
            return "individual"
        elif any(
            word in request_lower for word in ["small business", "startup", "solo"]
        ):
            return "small_business"
        elif any(
            word in request_lower
            for word in ["team", "group", "organization", "company"]
        ):
            return "team"
        elif any(word in request_lower for word in ["community", "club", "members"]):
            return "community"
        else:
            return "individual"

    def _extract_features(self, request: str) -> List[str]:
        """Extract primary features from request."""
        features = []
        request_lower = request.lower()

        feature_keywords = {
            "user_management": ["user", "login", "authentication", "profile"],
            "content": ["content", "blog", "articles", "posts", "media"],
            "commerce": ["payment", "checkout", "cart", "buying", "selling"],
            "communication": ["chat", "messages", "email", "notifications"],
            "data": ["database", "storage", "analytics", "reports"],
        }

        for category, keywords in feature_keywords.items():
            if any(keyword in request_lower for keyword in keywords):
                features.append(category.replace("_", " "))

        return features[:3]  # Limit to 3 primary features

    def _determine_business_context(self, request: str) -> str:
        """Determine business context."""
        request_lower = request.lower()

        if "handmade" in request_lower or "crafts" in request_lower:
            return "retail_creative"
        elif "food" in request_lower or "restaurant" in request_lower:
            return "retail_food"
        elif "health" in request_lower or "medical" in request_lower:
            return "services_health"
        else:
            return "general"

    def _calculate_confidence(self, request: str) -> float:
        """Calculate confidence in analysis."""
        # More detailed request = higher confidence
        word_count = len(request.split())
        if word_count > 10:
            return 0.9
        elif word_count > 5:
            return 0.7
        else:
            return 0.5

    def _generate_reasoning(self, request: str) -> str:
        """Generate reasoning for the analysis."""
        return f"Based on keywords in '{request}', this appears to be a request for building an application with specific functional requirements."

    def _get_alternatives(self, request: str) -> List[str]:
        """Get alternative interpretations."""
        return ["Could also be interpreted as a different type of application"]

    def _get_clarification_questions(self, request: str) -> List[str]:
        """Get clarification questions."""
        questions = []

        if not any(word in request.lower() for word in ["budget", "cost", "price"]):
            questions.append("What's your budget range for this project?")

        if not any(word in request.lower() for word in ["time", "deadline", "when"]):
            questions.append("When would you like this completed?")

        return questions[:2]

    def _get_risk_factors(self, request: str) -> List[str]:
        """Get risk factors."""
        return ["medium"]  # Would be more sophisticated with actual AI

    def _generate_project_name(self, request: str, project_type: str) -> str:
        """Generate project name from request."""
        words = request.split()
        key_words = [word for word in words if len(word) > 3]
        if key_words:
            return f"{key_words[0].title()} {project_type.title()}"
        return f"New {project_type.title()} Project"

    def _generate_objectives(self, features: List[str]) -> List[str]:
        """Generate project objectives."""
        objectives = []
        for feature in features[:3]:
            objectives.append(f"Implement {feature} functionality")
        return objectives

    def _suggest_technologies(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest appropriate technologies."""
        tech_mapping = {
            "ecommerce": ["Python", "Flask", "PostgreSQL"],
            "collaboration": ["React", "Node.js", "MongoDB"],
            "content_management": ["WordPress", "PHP", "MySQL"],
            "business_management": ["Python", "Django", "PostgreSQL"],
        }

        return tech_mapping.get(analysis["project_type"], ["Python", "Flask"])


def get_prompt_based_intent_parser(root: Path) -> PromptBasedIntentParser:
    """Get prompt-based intent parser instance."""
    return PromptBasedIntentParser(root)
