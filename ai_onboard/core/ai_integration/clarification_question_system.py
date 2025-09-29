"""
Clarification Question System - Intelligent question generation when user intent is unclear.

This module provides sophisticated question generation that helps clarify ambiguous
user requests by asking the right questions at the right time. It uses context awareness,
user expertise assessment, and progressive questioning strategies to gather missing
information without overwhelming users.
"""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set

from ..base.shared_types import QuestionComplexity, QuestionType, UserExpertiseLevel
from .user_preference_learning import get_user_preference_learning_system


@dataclass
class ClarificationQuestion:
    """A clarification question with metadata."""

    question_id: str
    question_text: str
    question_type: QuestionType
    complexity: QuestionComplexity
    category: str

    # Context and relevance
    context_keywords: List[str] = field(default_factory=list)
    required_for_understanding: bool = False
    prerequisite_questions: List[str] = field(default_factory=list)

    # User experience
    user_friendly_alternatives: List[str] = field(default_factory=list)
    expected_answer_format: str = "text"  # text, choice, number, boolean
    suggested_answers: List[str] = field(default_factory=list)

    # Priority and timing
    priority_score: float = 0.5
    ask_early: bool = False
    ask_only_if_confused: bool = False

    # Usage tracking
    times_asked: int = 0
    times_answered: int = 0
    average_response_quality: float = 0.5


class ClarificationQuestionEngine:
    """Engine for generating intelligent clarification questions."""

    def __init__(self, root: Path):
        self.root = root
        self.preference_system = get_user_preference_learning_system(root)

        # Question library
        self.question_library: Dict[str, ClarificationQuestion] = {}

        # User interaction tracking
        self.user_confusion_indicators: Set[str] = set()
        self.clarification_history: Dict[str, List[Dict[str, Any]]] = {}

        # Question generation rules
        self.question_generation_rules = self._load_question_rules()

        # Initialize with default questions
        self._initialize_default_questions()

    def generate_clarification_questions(
        self,
        user_request: str,
        user_id: str,
        current_context: Dict[str, Any],
        max_questions: int = 3,
    ) -> List[ClarificationQuestion]:
        """
        Generate clarification questions for an ambiguous user request.

        Args:
            user_request: The user's request
            user_id: User identifier
            current_context: Current conversation context
            max_questions: Maximum number of questions to generate

        Returns:
            List of clarification questions
        """
        user_expertise = self._get_user_expertise(user_id)
        confusion_level = self._assess_confusion_level(user_request, user_id)

        # Get appropriate questions based on context and expertise
        candidate_questions = self._get_candidate_questions(
            user_request, current_context, user_expertise
        )

        # Filter and prioritize questions
        relevant_questions = self._filter_and_prioritize_questions(
            candidate_questions, confusion_level, user_expertise, user_id
        )

        # Limit to maximum questions
        return relevant_questions[:max_questions]

    def record_question_response(
        self, user_id: str, question_id: str, response: str, response_quality: float
    ) -> None:
        """
        Record a user's response to a clarification question.

        Args:
            user_id: User identifier
            question_id: Question that was asked
            response: User's response
            response_quality: Quality of response (0-1)
        """
        if question_id not in self.question_library:
            return

        question = self.question_library[question_id]
        question.times_answered += 1
        question.average_response_quality = (
            (question.average_response_quality * (question.times_answered - 1))
            + response_quality
        ) / question.times_answered

        # Track in user history
        if user_id not in self.clarification_history:
            self.clarification_history[user_id] = []

        self.clarification_history[user_id].append(
            {
                "question_id": question_id,
                "response": response,
                "response_quality": response_quality,
                "timestamp": time.time(),
            }
        )

    def get_contextual_help_questions(
        self, user_id: str, current_action: str, difficulty_indicators: List[str]
    ) -> List[ClarificationQuestion]:
        """
        Get help questions based on current action and difficulty indicators.

        Args:
            user_id: User identifier
            current_action: What the user is trying to do
            difficulty_indicators: Signs that the user is struggling

        Returns:
            List of helpful clarification questions
        """
        user_expertise = self._get_user_expertise(user_id)

        # Get questions appropriate for current difficulty
        help_questions = []

        for indicator in difficulty_indicators:
            questions = self._get_questions_for_difficulty_indicator(
                indicator, current_action, user_expertise
            )
            help_questions.extend(questions)

        # Remove duplicates and prioritize
        unique_questions = []
        seen_ids = set()

        for question in help_questions:
            if question.question_id not in seen_ids:
                unique_questions.append(question)
                seen_ids.add(question.question_id)

        # Sort by priority
        unique_questions.sort(key=lambda q: q.priority_score, reverse=True)

        return unique_questions[:3]  # Limit to 3 questions

    def _assess_confusion_level(self, user_request: str, user_id: str) -> float:
        """Assess how confused the system is about the user's request."""
        confusion_score = 0.0

        # Length-based confusion (very short or very long requests)
        word_count = len(user_request.split())
        if word_count < 3:
            confusion_score += 0.3  # Too vague
        elif word_count > 50:
            confusion_score += 0.2  # Too complex

        # Ambiguity indicators
        ambiguity_keywords = [
            "something",
            "thing",
            "stuff",
            "whatever",
            "kinda",
            "sorta",
            "maybe",
            "perhaps",
            "not sure",
            "don't know",
        ]

        for keyword in ambiguity_keywords:
            if keyword in user_request.lower():
                confusion_score += 0.1

        # Check user history for confusion patterns
        if user_id in self.clarification_history:
            recent_responses = self.clarification_history[user_id][
                -5:
            ]  # Last 5 responses

            poor_responses = sum(
                1 for r in recent_responses if r["response_quality"] < 0.5
            )
            confusion_score += poor_responses * 0.1

        return min(confusion_score, 1.0)

    def _get_candidate_questions(
        self,
        user_request: str,
        context: Dict[str, Any],
        user_expertise: UserExpertiseLevel,
    ) -> List[ClarificationQuestion]:
        """Get candidate questions based on request analysis."""
        candidates = []

        # Analyze request for missing information
        missing_info = self._analyze_missing_information(user_request, context)

        # Get questions for each missing information type
        for info_type in missing_info:
            questions = self._get_questions_for_missing_info(
                info_type, user_request, user_expertise
            )
            candidates.extend(questions)

        return candidates

    def _analyze_missing_information(
        self, user_request: str, context: Dict[str, Any]
    ) -> List[str]:
        """Analyze what information is missing from the user request."""
        missing_info = []

        # Check for missing project scope
        if not any(
            word in user_request.lower()
            for word in ["small", "simple", "basic", "minimal"]
        ):
            if not any(
                word in user_request.lower()
                for word in ["large", "complex", "enterprise", "comprehensive"]
            ):
                missing_info.append("scope")

        # Check for missing timeline
        if not any(
            word in user_request.lower()
            for word in ["time", "deadline", "when", "soon", "quick"]
        ):
            missing_info.append("timeline")

        # Check for missing budget
        if not any(
            word in user_request.lower()
            for word in ["budget", "cost", "price", "money", "free"]
        ):
            missing_info.append("budget")

        # Check for missing technical requirements
        if not any(
            word in user_request.lower()
            for word in ["technology", "tech", "platform", "database"]
        ):
            missing_info.append("technical")

        # Check for missing target audience
        if not any(
            word in user_request.lower()
            for word in ["user", "customer", "audience", "people"]
        ):
            missing_info.append("audience")

        return missing_info

    def _get_questions_for_missing_info(
        self, info_type: str, user_request: str, user_expertise: UserExpertiseLevel
    ) -> List[ClarificationQuestion]:
        """Get questions for a specific type of missing information."""
        questions = []

        question_templates = {
            "scope": [
                ClarificationQuestion(
                    question_id=f"scope_{len(self.question_library)}",
                    question_text="How complex would you like this project to be?",
                    question_type=QuestionType.SPECIFYING,
                    complexity=QuestionComplexity.SIMPLE,
                    category="scope",
                    context_keywords=["project", "complexity", "size"],
                    expected_answer_format="choice",
                    suggested_answers=[
                        "Simple (basic features)",
                        "Moderate (standard features)",
                        "Complex (advanced features)",
                    ],
                    priority_score=0.8,
                )
            ],
            "timeline": [
                ClarificationQuestion(
                    question_id=f"timeline_{len(self.question_library)}",
                    question_text="When would you like this completed?",
                    question_type=QuestionType.SPECIFYING,
                    complexity=QuestionComplexity.SIMPLE,
                    category="timeline",
                    context_keywords=["time", "deadline", "when"],
                    expected_answer_format="choice",
                    suggested_answers=[
                        "ASAP (1-2 weeks)",
                        "Soon (1-2 months)",
                        "No rush (3+ months)",
                    ],
                    priority_score=0.7,
                )
            ],
            "budget": [
                ClarificationQuestion(
                    question_id=f"budget_{len(self.question_library)}",
                    question_text="What's your budget range for this project?",
                    question_type=QuestionType.SPECIFYING,
                    complexity=QuestionComplexity.SIMPLE,
                    category="budget",
                    context_keywords=["cost", "budget", "price"],
                    expected_answer_format="choice",
                    suggested_answers=[
                        "Under $1,000",
                        "$1,000-$5,000",
                        "$5,000-$20,000",
                        "Over $20,000",
                    ],
                    priority_score=0.6,
                )
            ],
            "technical": [
                ClarificationQuestion(
                    question_id=f"technical_{len(self.question_library)}",
                    question_text="Do you have any technology preferences or requirements?",
                    question_type=QuestionType.EXPLORING,
                    complexity=QuestionComplexity.MODERATE,
                    category="technical",
                    context_keywords=["technology", "platform", "database"],
                    priority_score=0.5,
                )
            ],
            "audience": [
                ClarificationQuestion(
                    question_id=f"audience_{len(self.question_library)}",
                    question_text="Who will be using this application?",
                    question_type=QuestionType.SPECIFYING,
                    complexity=QuestionComplexity.SIMPLE,
                    category="audience",
                    context_keywords=["user", "customer", "audience"],
                    expected_answer_format="text",
                    priority_score=0.6,
                )
            ],
        }

        return question_templates.get(info_type, [])

    def _filter_and_prioritize_questions(
        self,
        questions: List[ClarificationQuestion],
        confusion_level: float,
        user_expertise: UserExpertiseLevel,
        user_id: str,
    ) -> List[ClarificationQuestion]:
        """Filter and prioritize questions based on context and user."""
        filtered_questions = []

        for question in questions:
            # Skip if user expertise doesn't match question complexity
            if not self._question_appropriate_for_expertise(question, user_expertise):
                continue

            # Skip if we've asked this question too many times recently
            if self._question_asked_too_recently(question, user_id):
                continue

            # Adjust priority based on confusion level
            adjusted_priority = question.priority_score
            if confusion_level > 0.7:
                adjusted_priority += 0.2  # Higher priority when very confused

            question.priority_score = adjusted_priority
            filtered_questions.append(question)

        # Sort by priority
        filtered_questions.sort(key=lambda q: q.priority_score, reverse=True)

        return filtered_questions

    def _question_appropriate_for_expertise(
        self, question: ClarificationQuestion, user_expertise: UserExpertiseLevel
    ) -> bool:
        """Check if question complexity matches user expertise."""
        expertise_complexity_map = {
            UserExpertiseLevel.BEGINNER: [QuestionComplexity.SIMPLE],
            UserExpertiseLevel.INTERMEDIATE: [
                QuestionComplexity.SIMPLE,
                QuestionComplexity.MODERATE,
            ],
            UserExpertiseLevel.ADVANCED: [
                QuestionComplexity.SIMPLE,
                QuestionComplexity.MODERATE,
                QuestionComplexity.COMPLEX,
            ],
            UserExpertiseLevel.EXPERT: [
                QuestionComplexity.SIMPLE,
                QuestionComplexity.MODERATE,
                QuestionComplexity.COMPLEX,
                QuestionComplexity.TECHNICAL,
            ],
        }

        allowed_complexities = expertise_complexity_map.get(
            user_expertise, [QuestionComplexity.SIMPLE]
        )
        return question.complexity in allowed_complexities

    def _question_asked_too_recently(
        self, question: ClarificationQuestion, user_id: str
    ) -> bool:
        """Check if this question has been asked too recently to the same user."""
        if user_id not in self.clarification_history:
            return False

        recent_questions = self.clarification_history[user_id][
            -10:
        ]  # Last 10 interactions

        # Check if same question asked in last 5 interactions
        for interaction in recent_questions[-5:]:
            if interaction["question_id"] == question.question_id:
                return True

        return False

    def _get_questions_for_difficulty_indicator(
        self, indicator: str, current_action: str, user_expertise: UserExpertiseLevel
    ) -> List[ClarificationQuestion]:
        """Get questions for a specific difficulty indicator."""
        questions = []

        difficulty_question_map = {
            "too_many_options": [
                ClarificationQuestion(
                    question_id=f"too_many_options_{len(self.question_library)}",
                    question_text="Are there too many options to choose from?",
                    question_type=QuestionType.VALIDATING,
                    complexity=QuestionComplexity.SIMPLE,
                    category="usability",
                    expected_answer_format="boolean",
                )
            ],
            "unclear_next_step": [
                ClarificationQuestion(
                    question_id=f"unclear_next_{len(self.question_library)}",
                    question_text="What would you like to do next?",
                    question_type=QuestionType.EXPLORING,
                    complexity=QuestionComplexity.SIMPLE,
                    category="guidance",
                    expected_answer_format="choice",
                    suggested_answers=[
                        "Continue with current task",
                        "Get help",
                        "Start over",
                    ],
                )
            ],
            "technical_jargon": [
                ClarificationQuestion(
                    question_id=f"technical_jargon_{len(self.question_library)}",
                    question_text="Would you like me to explain the technical terms?",
                    question_type=QuestionType.CLARIFYING,
                    complexity=QuestionComplexity.SIMPLE,
                    category="terminology",
                    expected_answer_format="boolean",
                )
            ],
        }

        return difficulty_question_map.get(indicator, [])

    def _get_user_expertise(self, user_id: str) -> UserExpertiseLevel:
        """Get user's expertise level."""
        try:
            user_prefs = self.preference_system.get_user_preferences(user_id)
            expertise_str = user_prefs.get("expertise_level", "intermediate")
            return UserExpertiseLevel(expertise_str)
        except:
            return UserExpertiseLevel.INTERMEDIATE

    def _load_question_rules(self) -> Dict[str, Any]:
        """Load question generation rules."""
        return {
            "max_questions_per_session": 5,
            "question_spacing": 3,  # Ask questions every 3 messages
            "repeat_question_threshold": 2,  # Don't repeat questions more than twice
            "context_aware_questioning": True,
        }

    def _initialize_default_questions(self) -> None:
        """Initialize with default clarification questions."""
        default_questions = [
            # Scope-related questions
            ClarificationQuestion(
                question_id="scope_simple",
                question_text="How complex should this project be?",
                question_type=QuestionType.SPECIFYING,
                complexity=QuestionComplexity.SIMPLE,
                category="scope",
                context_keywords=["project", "complexity", "features"],
                expected_answer_format="choice",
                suggested_answers=["Simple", "Moderate", "Complex"],
                priority_score=0.8,
            ),
            # Timeline questions
            ClarificationQuestion(
                question_id="timeline_urgency",
                question_text="When do you need this completed?",
                question_type=QuestionType.SPECIFYING,
                complexity=QuestionComplexity.SIMPLE,
                category="timeline",
                context_keywords=["time", "deadline", "urgent"],
                expected_answer_format="choice",
                suggested_answers=["ASAP", "Soon", "No rush"],
                priority_score=0.7,
            ),
            # Technical questions
            ClarificationQuestion(
                question_id="tech_preferences",
                question_text="Any technology preferences?",
                question_type=QuestionType.EXPLORING,
                complexity=QuestionComplexity.MODERATE,
                category="technical",
                context_keywords=["technology", "platform", "tools"],
                priority_score=0.5,
            ),
            # Budget questions
            ClarificationQuestion(
                question_id="budget_range",
                question_text="What's your budget for this project?",
                question_type=QuestionType.SPECIFYING,
                complexity=QuestionComplexity.SIMPLE,
                category="budget",
                context_keywords=["cost", "budget", "price"],
                expected_answer_format="choice",
                suggested_answers=["Under $1K", "$1K-$5K", "$5K-$20K", "Over $20K"],
                priority_score=0.6,
            ),
            # Audience questions
            ClarificationQuestion(
                question_id="target_audience",
                question_text="Who will use this application?",
                question_type=QuestionType.SPECIFYING,
                complexity=QuestionComplexity.SIMPLE,
                category="audience",
                context_keywords=["user", "customer", "audience"],
                priority_score=0.6,
            ),
        ]

        for question in default_questions:
            self.question_library[question.question_id] = question

    def get_question_suggestions(self, user_id: str, context: str) -> List[str]:
        """Get suggested questions for a given context."""
        if user_id not in self.clarification_history:
            return ["What would you like to build?", "How can I help you?"]

        # Analyze user's previous responses to suggest better questions
        recent_responses = self.clarification_history[user_id][-5:]

        if not recent_responses:
            return ["What would you like to build?"]

        # Look for patterns in responses
        categories_asked = set()
        for response in recent_responses:
            question_id = response["question_id"]
            if question_id in self.question_library:
                categories_asked.add(self.question_library[question_id].category)

        # Suggest questions from categories not recently asked
        available_categories = ["scope", "timeline", "budget", "technical", "audience"]
        unasked_categories = [
            cat for cat in available_categories if cat not in categories_asked
        ]

        suggestions = []
        for category in unasked_categories[:2]:  # Suggest 2 categories
            questions = [
                q for q in self.question_library.values() if q.category == category
            ]
            if questions:
                suggestions.append(questions[0].question_text)

        return suggestions if suggestions else ["What would you like to build?"]


def get_clarification_question_engine(root: Path) -> ClarificationQuestionEngine:
    """Get clarification question engine instance."""
    return ClarificationQuestionEngine(root)
