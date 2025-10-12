"""
Natural Language Intent Parser - Advanced understanding of user intent from vague requests.

This module provides sophisticated natural language processing to understand what
non-technical users actually want when they make vague requests like:
- "I want to make a website where people can buy my handmade stuff"
- "Build me an app for my small business to track customers"

The parser identifies project type, complexity level, target audience, and key features
from natural language input, enabling the system to provide appropriate guidance.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .user_preference_learning import get_user_preference_learning_system


@dataclass
class IntentParsingResult:
    """Result of parsing user intent from natural language."""

    original_request: str
    confidence_score: float
    interpreted_intent: Dict[str, Any]

    # Core project elements
    project_type: str
    complexity_level: str
    target_audience: str
    primary_features: List[str]
    secondary_features: List[str]

    # Business context
    business_domain: str
    user_expertise_level: str
    budget_indicators: List[str]
    timeline_indicators: List[str]

    # Technical requirements
    technology_preferences: List[str]
    platform_requirements: List[str]
    integration_needs: List[str]

    # Risk and scope
    risk_level: str
    scope_complexity: str
    clarification_questions: List[str] = field(default_factory=list)

    # Metadata
    parsing_method: str = "keyword_heuristic"
    processing_time_ms: float = 0.0


class IntentKeywordLibrary:
    """Library of keywords for intent parsing."""

    # Project type keywords
    PROJECT_TYPES = {
        "ecommerce": [
            "buy",
            "sell",
            "purchase",
            "shop",
            "store",
            "marketplace",
            "product",
            "catalog",
            "inventory",
            "payment",
            "checkout",
            "handmade",
            "crafts",
            "artwork",
            "merchandise",
        ],
        "business_management": [
            "manage",
            "track",
            "organize",
            "database",
            "crm",
            "customer",
            "inventory",
            "orders",
            "clients",
            "contacts",
            "records",
        ],
        "collaboration": [
            "share",
            "work together",
            "team",
            "collaborate",
            "group",
            "document",
            "file sharing",
            "communication",
            "workspace",
        ],
        "content_management": [
            "blog",
            "content",
            "website",
            "cms",
            "publishing",
            "articles",
            "posts",
            "media",
            "portfolio",
        ],
        "event_management": [
            "events",
            "calendar",
            "schedule",
            "meetings",
            "bookings",
            "registration",
            "attendees",
            "organize",
            "club",
        ],
        "education": [
            "learn",
            "teach",
            "course",
            "training",
            "education",
            "tutorial",
            "knowledge",
            "skill",
            "study",
        ],
    }

    # Complexity indicators
    COMPLEXITY_KEYWORDS = {
        "simple": [
            "simple",
            "basic",
            "easy",
            "minimal",
            "straightforward",
            "quick",
            "small",
            "beginner",
            "starter",
        ],
        "moderate": [
            "medium",
            "moderate",
            "standard",
            "typical",
            "normal",
            "reasonable",
            "balanced",
            "intermediate",
        ],
        "complex": [
            "advanced",
            "complex",
            "sophisticated",
            "enterprise",
            "professional",
            "comprehensive",
            "full-featured",
        ],
    }

    # Target audience keywords
    AUDIENCE_KEYWORDS = {
        "individual": ["personal", "individual", "myself", "my own"],
        "small_business": ["small business", "startup", "solo", "freelance"],
        "team": ["team", "group", "organization", "company", "business"],
        "community": ["community", "club", "group", "members", "users"],
        "enterprise": ["enterprise", "corporate", "large", "organization"],
    }

    # Feature keywords by category
    FEATURE_KEYWORDS = {
        "user_management": ["user", "login", "authentication", "profile", "account"],
        "content": ["content", "blog", "articles", "posts", "media", "images"],
        "commerce": [
            "payment",
            "checkout",
            "cart",
            "buying",
            "selling",
            "orders",
            "buy",
            "sell",
            "purchase",
            "shop",
            "store",
            "marketplace",
            "handmade",
            "artwork",
        ],
        "communication": ["chat", "messages", "email", "notifications", "comments"],
        "data": ["database", "storage", "analytics", "reports", "tracking"],
        "integration": ["api", "webhook", "integration", "sync", "connect"],
        "admin": ["admin", "dashboard", "management", "control", "settings"],
    }


class NaturalLanguageIntentParser:
    """Advanced parser for understanding user intent from natural language."""

    def __init__(self, root: Path):
        self.root = root
        self.keyword_library = IntentKeywordLibrary()

        # Load user preferences for context
        self.user_preferences = get_user_preference_learning_system(root)

        # Cache for performance
        self._parsing_cache: Dict[str, IntentParsingResult] = {}

    def parse_user_intent(
        self, user_request: str, user_id: str = "default"
    ) -> IntentParsingResult:
        """
        Parse user intent from natural language request.

        Args:
            user_request: The user's natural language request
            user_id: User identifier for personalization

        Returns:
            IntentParsingResult with structured interpretation
        """
        import time

        start_time = time.time()

        # Check cache first
        cache_key = f"{user_id}:{user_request}"
        if cache_key in self._parsing_cache:
            result = self._parsing_cache[cache_key]
            result.processing_time_ms = (time.time() - start_time) * 1000
            return result

        # Parse the request
        result = self._perform_intent_parsing(user_request, user_id)

        # Cache the result
        self._parsing_cache[cache_key] = result

        # Update processing time
        result.processing_time_ms = (time.time() - start_time) * 1000

        return result

    def _perform_intent_parsing(
        self, user_request: str, user_id: str
    ) -> IntentParsingResult:
        """Perform the actual intent parsing."""
        # Normalize the request
        normalized_request = self._normalize_request(user_request)

        # Extract project type
        project_type = self._identify_project_type(normalized_request)

        # Determine complexity
        complexity_level = self._assess_complexity(normalized_request)

        # Identify target audience
        target_audience = self._identify_target_audience(normalized_request)

        # Extract features
        primary_features, secondary_features = self._extract_features(
            normalized_request
        )

        # Determine business context
        business_domain = self._identify_business_domain(
            normalized_request, project_type
        )

        # Assess user expertise
        user_expertise_level = self._assess_user_expertise(normalized_request, user_id)

        # Extract technical requirements
        technology_preferences = self._extract_technology_preferences(
            normalized_request
        )
        platform_requirements = self._extract_platform_requirements(normalized_request)
        integration_needs = self._extract_integration_needs(normalized_request)

        # Assess risk and scope
        risk_level = self._assess_risk_level(normalized_request, complexity_level)
        scope_complexity = self._assess_scope_complexity(
            normalized_request, primary_features
        )

        # Generate clarification questions
        clarification_questions = self._generate_clarification_questions(
            normalized_request, project_type, primary_features
        )

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            normalized_request, project_type, complexity_level, primary_features
        )

        # Build interpreted intent
        interpreted_intent = {
            "project_name": self._generate_project_name(
                normalized_request, project_type
            ),
            "description": normalized_request,
            "objectives": self._generate_objectives(
                normalized_request, primary_features
            ),
            "technologies": technology_preferences,
            "target_audience": target_audience,
            "business_domain": business_domain,
            "complexity_level": complexity_level,
            "risk_level": risk_level,
            "scope": scope_complexity,
        }

        return IntentParsingResult(
            original_request=user_request,
            confidence_score=confidence_score,
            interpreted_intent=interpreted_intent,
            project_type=project_type,
            complexity_level=complexity_level,
            target_audience=target_audience,
            primary_features=primary_features,
            secondary_features=secondary_features,
            business_domain=business_domain,
            user_expertise_level=user_expertise_level,
            budget_indicators=self._extract_budget_indicators(normalized_request),
            timeline_indicators=self._extract_timeline_indicators(normalized_request),
            technology_preferences=technology_preferences,
            platform_requirements=platform_requirements,
            integration_needs=integration_needs,
            risk_level=risk_level,
            scope_complexity=scope_complexity,
            clarification_questions=clarification_questions,
        )

    def _normalize_request(self, request: str) -> str:
        """Normalize the user request for parsing."""
        # Convert to lowercase
        normalized = request.lower()

        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized)

        # Remove punctuation except for important separators
        normalized = re.sub(r"[^\w\s\-/]", "", normalized)

        return normalized.strip()

    def _identify_project_type(self, request: str) -> str:
        """Identify the type of project from the request."""
        project_scores = {}

        for project_type, keywords in self.keyword_library.PROJECT_TYPES.items():
            score = sum(1 for keyword in keywords if keyword in request)
            if score > 0:
                project_scores[project_type] = score

        if not project_scores:
            return "general"

        # Return the project type with the highest score
        return max(project_scores.items(), key=lambda x: x[1])[0]

    def _assess_complexity(self, request: str) -> str:
        """Assess the complexity level of the request."""
        complexity_scores = {"simple": 0, "moderate": 0, "complex": 0}

        for level, keywords in self.keyword_library.COMPLEXITY_KEYWORDS.items():
            complexity_scores[level] = sum(
                1 for keyword in keywords if keyword in request
            )

        # If no complexity keywords found, default to moderate
        if sum(complexity_scores.values()) == 0:
            return "moderate"

        return max(complexity_scores.items(), key=lambda x: x[1])[0]

    def _identify_target_audience(self, request: str) -> str:
        """Identify the target audience from the request."""
        audience_scores = {}

        for audience, keywords in self.keyword_library.AUDIENCE_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in request)
            if score > 0:
                audience_scores[audience] = score

        if not audience_scores:
            return "individual"

        return max(audience_scores.items(), key=lambda x: x[1])[0]

    def _extract_features(self, request: str) -> Tuple[List[str], List[str]]:
        """Extract primary and secondary features from the request."""
        primary_features: List[str] = []
        secondary_features: List[str] = []

        request_lower = request.lower()

        def add_features(features: List[str]) -> None:
            for feature in features:
                if feature not in primary_features:
                    primary_features.append(feature)

        # Ecommerce style requests
        if any(
            word in request_lower
            for word in ["buy", "sell", "shop", "store", "cart", "checkout", "payment", "marketplace"]
        ):
            base_features = ["product catalog", "shopping cart", "payment"]
            if "art" in request_lower or "handmade" in request_lower:
                base_features = ["artwork gallery", "online sales", "payment"]
            add_features(base_features)

        # Customer tracking / CRM
        if any(
            word in request_lower for word in ["customer", "clients", "track", "crm", "database"]
        ):
            add_features(["customer database", "contact management"])

        # Collaboration signals
        if any(
            phrase in request_lower
            for phrase in ["share", "documents", "team", "collaborate", "work together", "communication"]
        ):
            add_features(["document sharing", "communication", "team coordination"])

        # Event / club organization
        if any(word in request_lower for word in ["event", "organize", "club", "schedule", "calendar"]):
            add_features(["event calendar", "member communication", "organization tools"])

        # Fallback: use keyword categories for additional hints
        for category, keywords in self.keyword_library.FEATURE_KEYWORDS.items():
            matches = [keyword for keyword in keywords if keyword in request_lower]
            if not matches:
                continue

            if category == "commerce" and not primary_features:
                add_features(["product catalog", "shopping cart", "payment"])
            elif category == "data":
                secondary_features.extend([m for m in matches if m not in primary_features])
            else:
                label = category.replace("_", " ")
                if label not in primary_features:
                    primary_features.append(label)

        return primary_features, secondary_features

    def _identify_business_domain(self, request: str, project_type: str) -> str:
        """Identify the business domain based on request and project type."""
        # Simple mapping based on project type and keywords
        domain_mapping = {
            "ecommerce": "retail",
            "business_management": "services",
            "collaboration": "productivity",
            "content_management": "media",
            "event_management": "events",
            "education": "education",
        }

        base_domain = domain_mapping.get(project_type, "general")

        # Refine based on specific keywords
        if any(
            word in request for word in ["handmade", "crafts", "artwork", "creative"]
        ):
            return f"{base_domain}_creative"
        elif any(word in request for word in ["food", "restaurant", "cafe"]):
            return f"{base_domain}_food"
        elif any(word in request for word in ["health", "medical", "fitness"]):
            return f"{base_domain}_health"

        return base_domain

    def _assess_user_expertise(self, request: str, user_id: str) -> str:
        """Assess the user's technical expertise level."""
        # Check user preferences first
        try:
            user_prefs = self.user_preferences.get_user_preferences(user_id)
            if user_prefs and "expertise_level" in user_prefs:
                return user_prefs["expertise_level"]
        except (FileNotFoundError, PermissionError, OSError):
            # Handle common file system errors
            pass
        # Infer from request language
        beginner_indicators = ["simple", "easy", "basic", "help", "new to"]
        expert_indicators = [
            "advanced",
            "complex",
            "professional",
            "enterprise",
            "custom",
        ]

        beginner_count = sum(1 for word in beginner_indicators if word in request)
        expert_count = sum(1 for word in expert_indicators if word in request)

        if expert_count > beginner_count:
            return "advanced"
        elif beginner_count > 0:
            return "beginner"
        else:
            return "intermediate"

    def _extract_technology_preferences(self, request: str) -> List[str]:
        """Extract technology preferences from the request."""
        technologies = []

        tech_keywords = {
            "python": ["python", "django", "flask", "fastapi"],
            "javascript": ["javascript", "js", "node", "react", "vue", "angular"],
            "mobile": ["mobile", "app", "ios", "android", "react native"],
            "web": ["website", "web app", "html", "css"],
            "database": ["database", "sql", "mysql", "postgresql", "mongodb"],
        }

        for tech, keywords in tech_keywords.items():
            if any(keyword in request for keyword in keywords):
                technologies.append(tech)

        return technologies

    def _extract_platform_requirements(self, request: str) -> List[str]:
        """Extract platform requirements from the request."""
        platforms = []

        platform_keywords = {
            "web": ["web", "website", "browser", "online"],
            "mobile": ["mobile", "phone", "app", "ios", "android"],
            "desktop": ["desktop", "computer", "windows", "mac", "linux"],
            "cloud": ["cloud", "saas", "online service"],
        }

        for platform, keywords in platform_keywords.items():
            if any(keyword in request for keyword in keywords):
                platforms.append(platform)

        return platforms if platforms else ["web"]  # Default to web

    def _extract_integration_needs(self, request: str) -> List[str]:
        """Extract integration requirements from the request."""
        integrations = []

        integration_keywords = [
            "api",
            "integration",
            "connect",
            "sync",
            "import",
            "export",
            "webhook",
            "third-party",
            "external",
            "social media",
        ]

        for keyword in integration_keywords:
            if keyword in request:
                integrations.append(keyword)

        return integrations

    def _assess_risk_level(self, request: str, complexity: str) -> str:
        """Assess the risk level of the project."""
        risk_indicators = {
            "low": ["simple", "basic", "personal", "small"],
            "medium": ["business", "moderate", "standard"],
            "high": ["complex", "enterprise", "critical", "mission-critical"],
        }

        # Base risk on complexity
        if complexity == "simple":
            base_risk = "low"
        elif complexity == "complex":
            base_risk = "high"
        else:
            base_risk = "medium"

        # Adjust based on specific indicators
        for level, keywords in risk_indicators.items():
            if any(keyword in request for keyword in keywords):
                if level == "high" or (level == "medium" and base_risk == "low"):
                    return level

        return base_risk

    def _assess_scope_complexity(self, request: str, features: List[str]) -> str:
        """Assess the overall scope complexity."""
        # Simple heuristic based on feature count and keywords
        if len(features) <= 2:
            return "minimal"
        elif len(features) <= 5:
            return "moderate"
        else:
            return "comprehensive"

    def _generate_clarification_questions(
        self, request: str, project_type: str, features: List[str]
    ) -> List[str]:
        """Generate questions to clarify ambiguous aspects."""
        questions = []

        # Ask about missing key elements
        if not any(word in request for word in ["budget", "cost", "price", "money"]):
            questions.append("What's your budget range for this project?")

        if not any(
            word in request for word in ["time", "deadline", "when", "timeline"]
        ):
            questions.append("When would you like this completed?")

        if not any(word in request for word in ["technology", "tech", "platform"]):
            questions.append("Do you have any technology preferences or requirements?")

        # Project-specific questions
        if project_type == "ecommerce" and not any(
            word in request for word in ["payment", "checkout"]
        ):
            questions.append("How do you want to handle payments and checkout?")

        if len(features) == 0:
            questions.append("What are the main features you need?")

        return questions[:3]  # Limit to 3 questions

    def _calculate_confidence_score(
        self, request: str, project_type: str, complexity: str, features: List[str]
    ) -> float:
        """Calculate confidence in the parsing result."""
        confidence_factors = []

        # Length factor - longer requests usually clearer
        if len(request.split()) > 10:
            confidence_factors.append(0.9)
        elif len(request.split()) > 5:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.4)

        # Project type confidence
        if project_type != "general":
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.3)

        # Feature richness
        if len(features) > 0:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.4)

        # Complexity clarity
        if complexity != "moderate":  # If we could determine complexity
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)

        # Average the factors
        return sum(confidence_factors) / len(confidence_factors)

    def _generate_project_name(self, request: str, project_type: str) -> str:
        """Generate a suggested project name."""
        # Extract key nouns from the request
        words = request.split()
        key_words = [
            word
            for word in words
            if len(word) > 3 and word not in ["want", "make", "build", "create", "need"]
        ]

        if key_words:
            return f"{key_words[0].title()} {project_type.title()}"
        else:
            return f"New {project_type.title()} Project"

    def _generate_objectives(self, request: str, features: List[str]) -> List[str]:
        """Generate project objectives from the request."""
        objectives = []

        # Add feature-based objectives
        for feature in features[:3]:  # Limit to 3
            objectives.append(f"Implement {feature} functionality")

        # Add general objectives based on request
        if any(word in request for word in ["easy", "simple", "basic"]):
            objectives.append("Keep the solution simple and user-friendly")

        if any(word in request for word in ["fast", "quick", "rapid"]):
            objectives.append("Deliver a fast-loading, responsive solution")

        return objectives

    def _extract_budget_indicators(self, request: str) -> List[str]:
        """Extract budget-related indicators."""
        indicators = []

        budget_keywords = [
            "budget",
            "cost",
            "price",
            "expensive",
            "cheap",
            "free",
            "money",
        ]
        for keyword in budget_keywords:
            if keyword in request:
                indicators.append(keyword)

        return indicators

    def _extract_timeline_indicators(self, request: str) -> List[str]:
        """Extract timeline-related indicators."""
        indicators = []

        timeline_keywords = [
            "time",
            "deadline",
            "when",
            "soon",
            "quick",
            "fast",
            "urgent",
            "asap",
        ]
        for keyword in timeline_keywords:
            if keyword in request:
                indicators.append(keyword)

        return indicators


def get_natural_language_intent_parser(root: Path) -> NaturalLanguageIntentParser:
    """Get natural language intent parser instance."""
    return NaturalLanguageIntentParser(root)
