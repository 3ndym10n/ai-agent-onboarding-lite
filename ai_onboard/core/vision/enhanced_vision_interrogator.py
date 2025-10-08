"""
Enhanced Vision Interrogator: Advanced vision definition system with adaptive questioning.

This enhanced system provides:
- Adaptive questioning based on responses
- Intelligent insight analysis using NLP patterns
- Dynamic phase progression
- Vision quality scoring
- Template - based questioning for different project types
- Integration with AI agent collaboration
"""

import json
import re
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base import utils
from .vision_clarity_scorer import score_vision_clarity, VisionClarityReport


class QuestionType(Enum):
    """Types of questions in the interrogation system."""

    OPEN_ENDED = "open_ended"
    MULTIPLE_CHOICE = "multiple_choice"
    RATING = "rating"
    PRIORITY_RANKING = "priority_ranking"
    YES_NO = "yes_no"


class ProjectType(Enum):
    """Types of projects for template - based questioning."""

    WEB_APPLICATION = "web_application"
    MOBILE_APP = "mobile_app"
    DATA_SCIENCE = "data_science"
    API_SERVICE = "api_service"
    DESKTOP_APP = "desktop_app"
    LIBRARY_PACKAGE = "library_package"
    AI_ML_PROJECT = "ai_ml_project"
    GAME = "game"
    ECOMMERCE = "ecommerce"
    ENTERPRISE_SOFTWARE = "enterprise_software"
    GENERIC = "generic"


@dataclass
class Question:
    """Enhanced question structure."""

    id: str
    text: str
    question_type: QuestionType
    required: bool = True
    follow_up_questions: List[str] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    insight_triggers: List[str] = field(default_factory=list)
    ambiguity_indicators: List[str] = field(default_factory=list)
    category: str = "general"
    priority: int = 1


@dataclass
class Insight:
    """Structured insight from response analysis."""

    id: str
    type: str
    category: str
    description: str
    confidence: float
    source_question: str
    source_phase: str
    actionable: bool = False
    recommendations: List[str] = field(default_factory=list)


@dataclass
class Ambiguity:
    """Identified ambiguity in responses."""

    id: str
    type: str
    priority: str
    description: str
    source_question: str
    source_phase: str
    suggested_clarifications: List[str] = field(default_factory=list)
    resolved: bool = False


class EnhancedVisionInterrogator:
    """Enhanced vision interrogation system with adaptive questioning."""

    def __init__(self, root: Path):
        self.root = root
        self.charter_path = root / ".ai_onboard" / "charter.json"
        self.interrogation_path = root / ".ai_onboard" / "vision_interrogation.json"
        self.templates_path = root / ".ai_onboard" / "vision_templates.json"

        # Initialize question templates
        self._initialize_question_templates()

    def _initialize_question_templates(self) -> None:
        """Initialize question templates for different project types."""
        self.question_templates = {
            ProjectType.WEB_APPLICATION: self._get_web_app_questions(),
            ProjectType.MOBILE_APP: self._get_mobile_app_questions(),
            ProjectType.DATA_SCIENCE: self._get_data_science_questions(),
            ProjectType.API_SERVICE: self._get_api_service_questions(),
            ProjectType.AI_ML_PROJECT: self._get_ai_ml_questions(),
            ProjectType.GENERIC: self._get_generic_questions(),
        }

    def _load_vision_data(self) -> Optional[Dict[str, Any]]:
        """Load vision interrogation data if it exists."""
        try:
            if self.interrogation_path.exists():
                with open(self.interrogation_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, dict) else None
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return None

    def detect_project_type(self, responses: Dict[str, Any]) -> ProjectType:
        """Detect project type based on responses."""
        # Analyze responses for project type indicators
        all_text = " ".join(
            [
                str(response.get("response", {}).get("answer", ""))
                for phase_responses in responses.values()
                for response in phase_responses.values()
            ]
        ).lower()

        # Project type detection patterns
        type_indicators = {
            ProjectType.WEB_APPLICATION: [
                "website",
                "web app",
                "frontend",
                "backend",
                "user interface",
                "browser",
                "responsive",
                "html",
                "css",
                "javascript",
            ],
            ProjectType.MOBILE_APP: [
                "mobile",
                "app",
                "ios",
                "android",
                "smartphone",
                "tablet",
                "native",
                "react native",
                "flutter",
            ],
            ProjectType.DATA_SCIENCE: [
                "data",
                "analysis",
                "machine learning",
                "ai",
                "model",
                "dataset",
                "analytics",
                "statistics",
                "prediction",
            ],
            ProjectType.API_SERVICE: [
                "api",
                "service",
                "microservice",
                "endpoint",
                "rest",
                "graphql",
                "integration",
                "backend service",
            ],
            ProjectType.AI_ML_PROJECT: [
                "artificial intelligence",
                "machine learning",
                "neural network",
                "deep learning",
                "nlp",
                "computer vision",
                "ai model",
            ],
        }

        scores = {}
        for project_type, indicators in type_indicators.items():
            score = sum(1 for indicator in indicators if indicator in all_text)
            scores[project_type] = score

        # Return project type with highest score, or generic if no clear match
        if scores:
            best_type = max(scores, key=lambda k: scores[k])
            if scores[best_type] > 0:
                return best_type

        return ProjectType.GENERIC

    def start_enhanced_interrogation(
        self, project_type: Optional[ProjectType] = None
    ) -> Dict[str, Any]:
        """Start enhanced vision interrogation process."""
        interrogation_data = utils.read_json(self.interrogation_path, default={})

        if interrogation_data.get("status") == "in_progress":
            return {"status": "already_in_progress"}

        # Detect project type if not provided
        if not project_type:
            project_type = ProjectType.GENERIC

        # Initialize enhanced interrogation
        interrogation: Dict[str, Any] = {
            "status": "in_progress",
            "started_at": utils.now_iso(),
            "project_type": project_type.value,
            "current_phase": "vision_core",
            "phases_completed": [],
            "responses": {},
            "insights": [],
            "ambiguities": [],
            "adaptive_questions": [],
            "vision_quality_score": 0.0,
            "session_id": str(uuid.uuid4()),
        }

        utils.write_json(self.interrogation_path, interrogation)

        # Get initial questions for the project type
        initial_questions = self._get_phase_questions("vision_core", project_type)

        return {
            "status": "enhanced_interrogation_started",
            "project_type": project_type.value,
            "current_phase": "vision_core",
            "next_questions": initial_questions,
            "session_id": interrogation["session_id"],
        }

    def submit_enhanced_response(
        self, phase: str, question_id: str, response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit response with enhanced analysis."""
        interrogation_data = utils.read_json(self.interrogation_path, default={})

        if interrogation_data.get("status") != "in_progress":
            return {"status": "error", "message": "No interrogation in progress"}

        # Enhanced validation
        validation = self._enhanced_validate_response(phase, question_id, response)
        if not validation["valid"]:
            return {
                "status": "validation_error",
                "errors": validation["errors"],
                "suggestions": validation.get("suggestions", []),
            }

        # Store response
        if "responses" not in interrogation_data:
            interrogation_data["responses"] = {}
        if phase not in interrogation_data["responses"]:
            interrogation_data["responses"][phase] = {}

        interrogation_data["responses"][phase][question_id] = {
            "response": response,
            "submitted_at": utils.now_iso(),
            "confidence": response.get("confidence", 0.5),
            "analysis_metadata": self._analyze_response_metadata(response),
        }

        # Enhanced analysis
        insights = self._generate_enhanced_insights(
            phase, question_id, response, interrogation_data
        )
        ambiguities = self._identify_enhanced_ambiguities(
            phase, question_id, response, interrogation_data
        )

        interrogation_data["insights"].extend(insights)
        interrogation_data["ambiguities"].extend(ambiguities)

        # Generate adaptive follow - up questions
        follow_up_questions = self._generate_follow_up_questions(
            phase, question_id, response, interrogation_data
        )
        if follow_up_questions:
            interrogation_data["adaptive_questions"].extend(follow_up_questions)

        # Update vision quality score using new clarity scorer
        responses = self._collect_responses(interrogation_data)
        clarity_report = score_vision_clarity(responses)

        interrogation_data["vision_quality_score"] = clarity_report.overall_score
        interrogation_data["vision_clarity_report"] = {
            "overall_score": clarity_report.overall_score,
            "is_ready_for_ai": clarity_report.is_ready_for_ai,
            "detailed_scores": {
                metric.value: {
                    "score": score.score,
                    "confidence": score.confidence,
                    "issues": score.issues,
                    "strengths": score.strengths,
                    "recommendations": score.recommendations
                }
                for metric, score in clarity_report.detailed_scores.items()
            },
            "critical_issues": clarity_report.critical_issues,
            "summary": clarity_report.summary
        }

        # Check phase completion with enhanced logic
        if self._is_enhanced_phase_complete(interrogation_data, phase):
            self._complete_enhanced_phase(interrogation_data, phase)

        utils.write_json(self.interrogation_path, interrogation_data)

        return {
            "status": "enhanced_response_accepted",
            "insights_generated": len(insights),
            "ambiguities_identified": len(ambiguities),
            "follow_up_questions": len(follow_up_questions),
            "vision_quality_score": interrogation_data["vision_quality_score"],
            "phase_complete": self._is_enhanced_phase_complete(
                interrogation_data, phase
            ),
            "recommendations": self._generate_recommendations(insights, ambiguities),
        }

    def _get_web_app_questions(self) -> Dict[str, List[Question]]:
        """Get questions specific to web applications."""
        return {
            "vision_core": [
                Question(
                    id="wa_vc_01",
                    text="What problem does your web application solve for users?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="problem_definition",
                    insight_triggers=["user problem", "pain point", "solution"],
                    ambiguity_indicators=["maybe", "not sure", "depends"],
                ),
                Question(
                    id="wa_vc_02",
                    text="What is your target user base? (e.g., consumers, businesses, developers)",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    validation_rules={
                        "options": [
                            "consumers",
                            "businesses",
                            "developers",
                            "internal users",
                            "other",
                        ]
                    },
                    category="target_audience",
                ),
                Question(
                    id="wa_vc_03",
                    text="What devices will users primarily access your app from?",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    validation_rules={
                        "options": ["desktop", "mobile", "tablet", "all devices"]
                    },
                    category="platform_requirements",
                ),
            ],
            "scope": [
                Question(
                    id="wa_sc_01",
                    text="What core features must be included in the initial version?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="core_features",
                    insight_triggers=["feature", "functionality", "capability"],
                ),
                Question(
                    id="wa_sc_02",
                    text="What features are nice - to - have but not essential?",
                    question_type=QuestionType.OPEN_ENDED,
                    required=False,
                    category="optional_features",
                ),
            ],
        }

    def _get_mobile_app_questions(self) -> Dict[str, List[Question]]:
        """Get questions specific to mobile applications."""
        return {
            "vision_core": [
                Question(
                    id="ma_vc_01",
                    text="What mobile - specific problem does your app address?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="mobile_problem",
                    insight_triggers=[
                        "mobile",
                        "on - the - go",
                        "location",
                        "camera",
                        "sensors",
                    ],
                ),
                Question(
                    id="ma_vc_02",
                    text="Which mobile platforms do you need to support?",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    validation_rules={
                        "options": ["iOS", "Android", "Both", "Progressive Web App"]
                    },
                    category="platform_support",
                ),
            ]
        }

    def _get_data_science_questions(self) -> Dict[str, List[Question]]:
        """Get questions specific to data science projects."""
        return {
            "vision_core": [
                Question(
                    id="ds_vc_01",
                    text="What data do you have available and \
                        what insights do you want to extract?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="data_insights",
                    insight_triggers=[
                        "data",
                        "analysis",
                        "insights",
                        "patterns",
                        "predictions",
                    ],
                ),
                Question(
                    id="ds_vc_02",
                    text="What type of analysis are you planning?",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    validation_rules={
                        "options": [
                            "descriptive",
                            "predictive",
                            "prescriptive",
                            "exploratory",
                        ]
                    },
                    category="analysis_type",
                ),
            ]
        }

    def _get_api_service_questions(self) -> Dict[str, List[Question]]:
        """Get questions specific to API services."""
        return {
            "vision_core": [
                Question(
                    id="api_vc_01",
                    text="What services or functionality will your API provide?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="api_functionality",
                    insight_triggers=[
                        "service",
                        "endpoint",
                        "integration",
                        "data access",
                    ],
                ),
                Question(
                    id="api_vc_02",
                    text="Who will be the primary consumers of your API?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="api_consumers",
                    insight_triggers=[
                        "developers",
                        "applications",
                        "third - party",
                        "internal",
                    ],
                ),
            ]
        }

    def _get_ai_ml_questions(self) -> Dict[str, List[Question]]:
        """Get questions specific to AI / ML projects."""
        return {
            "vision_core": [
                Question(
                    id="ai_vc_01",
                    text="What AI / ML problem are you trying to solve?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="ai_problem",
                    insight_triggers=[
                        "machine learning",
                        "artificial intelligence",
                        "model",
                        "prediction",
                        "classification",
                    ],
                ),
                Question(
                    id="ai_vc_02",
                    text="What type of AI / ML approach are you considering?",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    validation_rules={
                        "options": [
                            "supervised learning",
                            "unsupervised learning",
                            "reinforcement learning",
                            "deep learning",
                            "NLP",
                            "computer vision",
                        ]
                    },
                    category="ml_approach",
                ),
            ]
        }

    def _get_generic_questions(self) -> Dict[str, List[Question]]:
        """Get generic questions for any project type."""
        return {
            "vision_core": [
                Question(
                    id="gen_vc_01",
                    text="What is the core problem this project addresses?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="problem_definition",
                    insight_triggers=["problem", "challenge", "issue", "need"],
                ),
                Question(
                    id="gen_vc_02",
                    text="What is your vision for the ideal outcome?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="vision_outcome",
                    insight_triggers=["vision", "goal", "outcome", "success"],
                ),
                Question(
                    id="gen_vc_03",
                    text="Who are the primary users or beneficiaries?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="target_users",
                    insight_triggers=[
                        "users",
                        "customers",
                        "beneficiaries",
                        "audience",
                    ],
                ),
            ],
            "stakeholders": [
                Question(
                    id="gen_sg_01",
                    text="Who are the key stakeholders and decision makers?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="stakeholders",
                    insight_triggers=[
                        "stakeholder",
                        "decision maker",
                        "influencer",
                        "sponsor",
                    ],
                ),
                Question(
                    id="gen_sg_02",
                    text="What are the primary goals for each stakeholder?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="stakeholder_goals",
                    insight_triggers=["goal", "objective", "priority", "interest"],
                ),
            ],
            "scope": [
                Question(
                    id="gen_sc_01",
                    text="What is definitely IN scope for this project?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="in_scope",
                    insight_triggers=["scope", "include", "must have", "essential"],
                ),
                Question(
                    id="gen_sc_02",
                    text="What is definitely OUT of scope?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="out_of_scope",
                    insight_triggers=[
                        "out of scope",
                        "exclude",
                        "not included",
                        "future",
                    ],
                ),
            ],
            "success": [
                Question(
                    id="gen_su_01",
                    text="How will you measure success?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="success_metrics",
                    insight_triggers=[
                        "measure",
                        "metric",
                        "kpi",
                        "success",
                        "performance",
                    ],
                ),
                Question(
                    id="gen_su_02",
                    text="What are the minimum viable outcomes?",
                    question_type=QuestionType.OPEN_ENDED,
                    category="mvo",
                    insight_triggers=["minimum", "viable", "essential", "must have"],
                ),
            ],
        }

    def _enhanced_validate_response(
        self, phase: str, question_id: str, response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhanced response validation with suggestions."""
        errors = []
        suggestions = []

        # Basic validation
        if not response.get("answer"):
            errors.append("Answer is required")
            suggestions.append(
                "Please provide a detailed answer to help clarify your vision"
            )

        # Confidence validation
        confidence = response.get("confidence", 0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            errors.append("Confidence must be a number between 0 and 1")
            suggestions.append(
                "Rate your confidence from 0 (not sure) to 1 (very confident)"
            )

        # Length validation with context
        answer = response.get("answer", "")
        if len(answer.strip()) < 20:
            errors.append("Answer must be at least 20 characters long")
            suggestions.append("Please provide more detail to help clarify your vision")
        elif len(answer.strip()) < 50:
            suggestions.append(
                "Consider adding more detail to make your vision clearer"
            )

        # Content quality suggestions
        if answer and len(answer.strip()) > 20:
            if not any(
                word in answer.lower()
                for word in ["problem", "solution", "goal", "outcome", "user", "need"]
            ):
                suggestions.append(
                    "Consider mentioning the problem you're solving or the outcome you want"
                )

        return {"valid": len(errors) == 0, "errors": errors, "suggestions": suggestions}

    def _analyze_response_metadata(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze response for metadata and patterns."""
        answer = response.get("answer", "").lower()

        metadata = {
            "word_count": len(answer.split()),
            "character_count": len(answer),
            "contains_technical_terms": any(
                term in answer
                for term in [
                    "api",
                    "database",
                    "algorithm",
                    "framework",
                    "architecture",
                    "deployment",
                ]
            ),
            "contains_business_terms": any(
                term in answer
                for term in [
                    "revenue",
                    "customer",
                    "market",
                    "business",
                    "roi",
                    "profit",
                ]
            ),
            "contains_user_terms": any(
                term in answer
                for term in ["user", "customer", "experience", "interface", "usability"]
            ),
            "confidence_level": response.get("confidence", 0.5),
            "sentiment_indicators": self._analyze_sentiment(answer),
        }

        return metadata

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Basic sentiment analysis of response text."""
        positive_words = [
            "excited",
            "confident",
            "clear",
            "definite",
            "sure",
            "positive",
        ]
        negative_words = [
            "uncertain",
            "confused",
            "unclear",
            "maybe",
            "possibly",
            "not sure",
        ]

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
        }

    def _generate_enhanced_insights(
        self,
        phase: str,
        question_id: str,
        response: Dict[str, Any],
        interrogation_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate enhanced insights from response analysis."""
        insights = []
        metadata = response.get("analysis_metadata", {})

        # Technical focus insight
        if metadata.get("contains_technical_terms"):
            insights.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "technical_focus",
                    "category": "project_approach",
                    "description": "Response indicates strong technical focus",
                    "confidence": 0.8,
                    "source_question": question_id,
                    "source_phase": phase,
                    "actionable": True,
                    "recommendations": [
                        "Consider documenting technical requirements early",
                        "Plan for technical architecture discussions",
                        "Identify potential technical risks",
                    ],
                }
            )

        # Business focus insight
        if metadata.get("contains_business_terms"):
            insights.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "business_focus",
                    "category": "project_approach",
                    "description": "Response indicates business - oriented approach",
                    "confidence": 0.8,
                    "source_question": question_id,
                    "source_phase": phase,
                    "actionable": True,
                    "recommendations": [
                        "Define business metrics and KPIs",
                        "Consider stakeholder communication strategy",
                        "Plan for business value demonstration",
                    ],
                }
            )

        # User focus insight
        if metadata.get("contains_user_terms"):
            insights.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "user_focus",
                    "category": "project_approach",
                    "description": "Response indicates user - centered approach",
                    "confidence": 0.8,
                    "source_question": question_id,
                    "source_phase": phase,
                    "actionable": True,
                    "recommendations": [
                        "Plan user research and testing",
                        "Define user personas and journeys",
                        "Consider usability and accessibility requirements",
                    ],
                }
            )

        # Confidence insight
        confidence = response.get("confidence", 0.5)
        if confidence < 0.5:
            insights.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "low_confidence",
                    "category": "ambiguity",
                    "description": "Low confidence indicates potential uncertainty",
                    "confidence": 0.9,
                    "source_question": question_id,
                    "source_phase": phase,
                    "actionable": True,
                    "recommendations": [
                        "Consider additional research or stakeholder input",
                        "Break down complex aspects into smaller parts",
                        "Schedule follow - up discussions",
                    ],
                }
            )

        return insights

    def _identify_enhanced_ambiguities(
        self,
        phase: str,
        question_id: str,
        response: Dict[str, Any],
        interrogation_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Identify enhanced ambiguities with suggested clarifications."""
        ambiguities = []
        answer = response.get("answer", "").lower()

        # Uncertainty indicators
        uncertainty_patterns = [
            r"\b(maybe|possibly|perhaps|not sure|uncertain|depends|it depends)\b",
            r"\b(we'll see|tbd|to be determined|not decided)\b",
            r"\b(somehow|somewhat|kind of|sort of)\b",
        ]

        for pattern in uncertainty_patterns:
            if re.search(pattern, answer):
                ambiguities.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "uncertainty",
                        "priority": "medium",
                        "description": "Response contains uncertainty indicators",
                        "source_question": question_id,
                        "source_phase": phase,
                        "suggested_clarifications": [
                            "Can you provide more specific details?",
                            "What factors would influence this decision?",
                            "What additional information would help clarify this?",
                        ],
                        "resolved": False,
                    }
                )
                break

        # Vague language detection
        vague_patterns = [
            r"\b(things|stuff|various|several|many|some)\b",
            r"\b(good|better|nice|great|awesome)\b",
        ]

        for pattern in vague_patterns:
            if re.search(pattern, answer):
                ambiguities.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "vague_language",
                        "priority": "low",
                        "description": "Response contains vague or non - specific language",
                        "source_question": question_id,
                        "source_phase": phase,
                        "suggested_clarifications": [
                            "Can you be more specific about what you mean?",
                            "What are some concrete examples?",
                            "How would you measure or define this?",
                        ],
                        "resolved": False,
                    }
                )
                break

        return ambiguities

    def _generate_follow_up_questions(
        self,
        phase: str,
        question_id: str,
        response: Dict[str, Any],
        interrogation_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate adaptive follow - up questions based on responses."""
        follow_ups = []
        answer = response.get("answer", "").lower()

        # Generate follow - ups based on content analysis
        if "user" in answer and "experience" in answer:
            follow_ups.append(
                {
                    "id": f"{question_id}_followup_ux",
                    "text": "What specific aspects of user experience are most important to you?",
                    "question_type": QuestionType.OPEN_ENDED,
                    "category": "user_experience_detail",
                    "triggered_by": question_id,
                }
            )

        if "data" in answer and ("analysis" in answer or "insights" in answer):
            follow_ups.append(
                {
                    "id": f"{question_id}_followup_data",
                    "text": "What types of data insights would be most valuable?",
                    "question_type": QuestionType.OPEN_ENDED,
                    "category": "data_insights",
                    "triggered_by": question_id,
                }
            )

        if "security" in answer or "privacy" in answer:
            follow_ups.append(
                {
                    "id": f"{question_id}_followup_security",
                    "text": "What are your main security and privacy concerns?",
                    "question_type": QuestionType.OPEN_ENDED,
                    "category": "security_requirements",
                    "triggered_by": question_id,
                }
            )

        return follow_ups

    def _calculate_enhanced_vision_quality(
        self, interrogation_data: Dict[str, Any]
    ) -> float:
        """Calculate enhanced vision quality score."""
        score = 0.0
        responses = interrogation_data.get("responses", {})

        # Base score from completion
        total_questions = 0
        answered_questions = 0

        for phase, phase_responses in responses.items():
            answered_questions += len(phase_responses)
            # Count total questions for this phase (simplified)
            total_questions += 10  # Approximate

        if total_questions > 0:
            completion_score = (answered_questions / total_questions) * 0.4
            score += completion_score

        # Quality score from insights
        insights = interrogation_data.get("insights", [])
        if insights:
            quality_insights = len(
                [i for i in insights if i.get("confidence", 0) > 0.7]
            )
            insight_score = min(quality_insights / 5.0, 0.3)  # Max 0.3 points
            score += insight_score

        # Confidence score
        all_confidences = []
        for phase_responses in responses.values():
            for response in phase_responses.values():
                all_confidences.append(response.get("confidence", 0.5))

        if all_confidences:
            avg_confidence = sum(all_confidences) / len(all_confidences)
            confidence_score = avg_confidence * 0.3  # Max 0.3 points
            score += confidence_score

        return min(score, 1.0)

    def _collect_responses(self, interrogation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect all responses for clarity scoring."""
        responses = {}

        # Collect responses from all phases
        all_responses = interrogation_data.get("responses", {})

        # Flatten responses into a simple dictionary for scoring
        for phase, phase_responses in all_responses.items():
            for question_id, response_data in phase_responses.items():
                if isinstance(response_data, dict):
                    response_text = response_data.get("response", "")
                else:
                    response_text = str(response_data)
                responses[question_id] = response_text

        return responses

    def _is_enhanced_phase_complete(
        self, interrogation_data: Dict[str, Any], phase: str
    ) -> bool:
        """Enhanced phase completion logic."""
        responses = interrogation_data.get("responses", {}).get(phase, {})

        # Get project type and questions
        project_type = ProjectType(interrogation_data.get("project_type", "generic"))
        phase_questions = self._get_phase_questions(phase, project_type)

        # Check required questions
        required_questions = [q for q in phase_questions if q.required]
        answered_required = sum(1 for q in required_questions if q.id in responses)

        # Enhanced completion criteria
        required_complete = answered_required == len(required_questions)

        # Check for high - priority ambiguities that need resolution
        phase_ambiguities = [
            a
            for a in interrogation_data.get("ambiguities", [])
            if a.get("source_phase") == phase and a.get("priority") == "critical"
        ]

        critical_ambiguities_resolved = all(
            a.get("resolved", False) for a in phase_ambiguities
        )

        return required_complete and critical_ambiguities_resolved

    def _complete_enhanced_phase(
        self, interrogation_data: Dict[str, Any], phase: str
    ) -> None:
        """Complete enhanced phase with additional processing."""
        phases = ["vision_core", "stakeholders", "scope", "success"]
        current_index = phases.index(phase)

        # Mark phase as completed
        if "phases_completed" not in interrogation_data:
            interrogation_data["phases_completed"] = []
        interrogation_data["phases_completed"].append(phase)

        # Move to next phase or complete
        if current_index + 1 < len(phases):
            interrogation_data["current_phase"] = phases[current_index + 1]
        else:
            interrogation_data["status"] = "completed"
            interrogation_data["completed_at"] = utils.now_iso()

            # Generate final vision quality report
            interrogation_data["final_vision_quality"] = (
                self._generate_vision_quality_report(interrogation_data)
            )

            # Auto - sync to charter
            try:
                from ..legacy_cleanup.interrogation_to_charter import (
                    auto_sync_on_completion,
                )

                if auto_sync_on_completion(self.root):
                    print(
                        "[OK] Enhanced vision interrogation data synced to charter.json"
                    )
            except Exception as e:
                print(f"[WARNING] Error syncing to charter: {e}")

    def _generate_vision_quality_report(
        self, interrogation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive vision quality report."""
        insights = interrogation_data.get("insights", [])
        ambiguities = interrogation_data.get("ambiguities", [])

        # Categorize insights
        insight_categories: Dict[str, List[str]] = {}
        for insight in insights:
            category = insight.get("category", "other")
            if category not in insight_categories:
                insight_categories[category] = []
            insight_categories[category].append(insight)

        # Categorize ambiguities
        ambiguity_priorities = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for ambiguity in ambiguities:
            priority = ambiguity.get("priority", "medium")
            ambiguity_priorities[priority] += 1

        return {
            "overall_score": interrogation_data.get("vision_quality_score", 0.0),
            "insight_summary": {
                "total_insights": len(insights),
                "categories": insight_categories,
                "actionable_insights": len(
                    [i for i in insights if i.get("actionable", False)]
                ),
            },
            "ambiguity_summary": {
                "total_ambiguities": len(ambiguities),
                "by_priority": ambiguity_priorities,
                "unresolved": len(
                    [a for a in ambiguities if not a.get("resolved", False)]
                ),
            },
            "recommendations": self._generate_final_recommendations(
                insights, ambiguities
            ),
        }

    def _generate_final_recommendations(
        self, insights: List[Dict[str, Any]], ambiguities: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate final recommendations based on analysis."""
        recommendations = []

        # Recommendations based on insights
        if any(i.get("type") == "technical_focus" for i in insights):
            recommendations.append("Consider early technical architecture planning")

        if any(i.get("type") == "business_focus" for i in insights):
            recommendations.append("Define clear business metrics and success criteria")

        if any(i.get("type") == "user_focus" for i in insights):
            recommendations.append("Plan user research and testing activities")

        # Recommendations based on ambiguities
        critical_ambiguities = [
            a for a in ambiguities if a.get("priority") == "critical"
        ]
        if critical_ambiguities:
            recommendations.append(
                "Address critical ambiguities before proceeding with development"
            )

        high_ambiguities = [a for a in ambiguities if a.get("priority") == "high"]
        if len(high_ambiguities) > 3:
            recommendations.append(
                "Consider additional stakeholder discussions to clarify high - priority ambiguities"
            )

        return recommendations

    def _generate_recommendations(
        self, insights: List[Dict[str, Any]], ambiguities: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate immediate recommendations based on new insights and ambiguities."""
        recommendations = []

        for insight in insights:
            if insight.get("actionable") and insight.get("recommendations"):
                recommendations.extend(insight["recommendations"])

        for ambiguity in ambiguities:
            if ambiguity.get("priority") in ["critical", "high"]:
                recommendations.append(f"Clarify: {ambiguity.get('description', '')}")

        return list(set(recommendations))  # Remove duplicates

    def _get_phase_questions(
        self, phase: str, project_type: ProjectType
    ) -> List[Question]:
        """Get questions for a specific phase and project type."""
        template = self.question_templates.get(
            project_type, self.question_templates[ProjectType.GENERIC]
        )
        return template.get(phase, [])

    def get_enhanced_interrogation_status(self) -> Dict[str, Any]:
        """Get comprehensive status of enhanced interrogation."""
        interrogation_data = utils.read_json(self.interrogation_path, default={})

        if not interrogation_data:
            return {
                "status": "no_interrogation",
                "message": "No interrogation data found",
            }

        return {
            "status": interrogation_data.get("status", "unknown"),
            "project_type": interrogation_data.get("project_type", "generic"),
            "current_phase": interrogation_data.get("current_phase", "unknown"),
            "phases_completed": interrogation_data.get("phases_completed", []),
            "vision_quality_score": interrogation_data.get("vision_quality_score", 0.0),
            "session_id": interrogation_data.get("session_id"),
            "started_at": interrogation_data.get("started_at"),
            "completed_at": interrogation_data.get("completed_at"),
            "insights_count": len(interrogation_data.get("insights", [])),
            "ambiguities_count": len(interrogation_data.get("ambiguities", [])),
            "adaptive_questions_count": len(
                interrogation_data.get("adaptive_questions", [])
            ),
            "final_quality_report": interrogation_data.get("final_vision_quality"),
        }

    def check_vision_alignment(
        self,
        action_description: str,
        action_type: str = "general",
        risk_level: str = "medium",
    ) -> Dict[str, Any]:
        """
        Check if an action aligns with the established vision.

        Args:
            action_description: Description of the action to check
            action_type: Type of action (feature_add, refactor, etc.)
            risk_level: Risk level of the action (low, medium, high)

        Returns:
            Dict with alignment assessment and recommendations
        """
        # Get current vision context
        vision_data = utils.read_json(self.interrogation_path, default={})
        charter_data = utils.read_json(self.charter_path, default={})

        if not vision_data or not charter_data:
            return {
                "alignment_score": 0.0,
                "action": "unknown",
                "reason": "No vision or charter data available",
                "confidence": 0.0,
            }

        # Calculate alignment score
        alignment_score = self._calculate_alignment_score(
            action_description, action_type, risk_level, vision_data, charter_data
        )

        # Determine action based on score
        if alignment_score >= 0.8:
            action = "allow"
            reason = "Action strongly aligns with project vision"
        elif alignment_score >= 0.6:
            action = "allow_with_review"
            reason = "Action mostly aligns, minor review recommended"
        elif alignment_score >= 0.4:
            action = "require_approval"
            reason = "Action needs vision alignment review"
        else:
            action = "block"
            reason = "Action significantly misaligned with project vision"

        return {
            "alignment_score": alignment_score,
            "action": action,
            "reason": reason,
            "confidence": min(alignment_score + 0.2, 1.0),  # Add some confidence buffer
            "vision_context": {
                "project_type": vision_data.get("project_type", "unknown"),
                "key_objectives": charter_data.get("objectives", []),
                "risk_tolerance": charter_data.get("risk_appetite", "medium"),
            },
        }

    def _calculate_alignment_score(
        self,
        action_description: str,
        action_type: str,
        risk_level: str,
        vision_data: Dict[str, Any],
        charter_data: Dict[str, Any],
    ) -> float:
        """Calculate alignment score for an action."""
        score = 0.5  # Start with neutral score

        # Check against objectives
        objectives = charter_data.get("objectives", [])
        for objective in objectives:
            obj_desc = objective.get("description", "").lower()
            if obj_desc and obj_desc in action_description.lower():
                score += 0.2
                break

        # Check risk alignment
        risk_appetite = charter_data.get("risk_appetite", "medium")
        if risk_level == "low" or (
            risk_level == "medium" and risk_appetite in ["medium", "high"]
        ):
            score += 0.1
        elif risk_level == "high" and risk_appetite == "low":
            score -= 0.3

        # Check action type alignment
        project_type = vision_data.get("project_type", "generic")
        if action_type == "feature_add" and "feature" in action_description.lower():
            score += 0.1
        elif action_type == "refactor" and "improve" in action_description.lower():
            score += 0.1

        return max(0.0, min(1.0, score))  # Clamp between 0 and 1

    def get_current_questions(self) -> Dict[str, Any]:
        """Get questions for the current interrogation phase (for compatibility)."""
        interrogation_data = utils.read_json(self.interrogation_path, default={})

        if not interrogation_data:
            return {"questions": []}

        current_phase = interrogation_data.get("current_phase", "vision_core")
        project_type_str = interrogation_data.get("project_type", "generic")
        try:
            project_type = ProjectType(project_type_str)
        except ValueError:
            project_type = ProjectType.GENERIC

        questions = self._get_phase_questions(current_phase, project_type)

        # Convert Question objects to dictionaries for compatibility
        question_dicts = []
        for q in questions:
            question_dicts.append(
                {
                    "id": q.id,
                    "text": q.text,
                    "type": q.question_type.value,
                    "required": q.required,
                    "options": q.options if hasattr(q, "options") else [],
                    "help_text": q.help_text if hasattr(q, "help_text") else "",
                }
            )

        return {"questions": question_dicts}

    def check_vision_readiness(self) -> Dict[str, Any]:
        """
        Check if the vision interrogation system is ready.

        Returns:
            Dict with readiness status and any issues
        """
        try:
            # Check if charter exists
            charter_file = self.root / ".ai_onboard" / "charter.json"
            charter_exists = charter_file.exists()

            # Check if plan exists
            plan_file = self.root / ".ai_onboard" / "plan.json"
            plan_exists = plan_file.exists()

            # Check vision data
            vision_data = self._load_vision_data()

            return {
                "ready": charter_exists and plan_exists,
                "charter_exists": charter_exists,
                "plan_exists": plan_exists,
                "vision_data_loaded": vision_data is not None,
                "issues": [
                    msg
                    for msg in [
                        "Missing charter.json" if not charter_exists else None,
                        "Missing plan.json" if not plan_exists else None,
                    ]
                    if msg is not None
                ],
            }

        except Exception as e:
            return {"ready": False, "error": str(e), "issues": ["Vision system error"]}

    def get_interrogation_summary(self) -> Dict[str, Any]:
        """Get summary of current interrogation status."""
        return self.get_enhanced_interrogation_status()

    def force_complete_interrogation(self) -> Dict[str, Any]:
        """Force complete the current interrogation."""
        # Load current data
        interrogation_data = self._load_vision_data()
        if not interrogation_data:
            return {"error": "No active interrogation to complete"}

        # Mark as completed
        interrogation_data["status"] = "completed"
        interrogation_data["completed_at"] = utils.now_iso()
        interrogation_data["force_completed"] = True

        # Save updated data
        utils.write_json(
            self.root / ".ai_onboard" / "vision_data.json", interrogation_data
        )

        return {
            "status": "completed",
            "force_completed": True,
            "completed_at": interrogation_data["completed_at"],
        }

    def complete_from_charter(self) -> Dict[str, Any]:
        """Complete interrogation using existing project charter."""
        try:
            charter_path = self.root / ".ai_onboard" / "project_charter.json"
            if not charter_path.exists():
                return {"error": "No project charter found"}

            charter_data = utils.read_json(charter_path)

            # Create basic interrogation data from charter
            interrogation_data = {
                "status": "completed",
                "completed_at": utils.now_iso(),
                "completed_from_charter": True,
                "project_type": charter_data.get("project_type", "unknown"),
                "responses": {},
                "phases_completed": [
                    "vision_core",
                    "technical_details",
                    "implementation_plan",
                ],
            }

            # Save interrogation data
            utils.write_json(
                self.root / ".ai_onboard" / "vision_data.json", interrogation_data
            )

            return {
                "status": "completed",
                "completed_from_charter": True,
                "project_type": interrogation_data["project_type"],
            }

        except Exception as e:
            return {"error": f"Failed to complete from charter: {str(e)}"}


def get_enhanced_vision_interrogator(root: Path) -> EnhancedVisionInterrogator:
    """Get enhanced vision interrogator instance."""
    return EnhancedVisionInterrogator(root)
