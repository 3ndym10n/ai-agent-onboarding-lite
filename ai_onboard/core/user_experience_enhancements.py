"""
User Experience Enhancements (T19) - Core UX improvements and intelligent user interactions.

This module implements comprehensive user experience enhancements that:
- Provide intelligent error handling and recovery guidance
- Implement adaptive workflows based on user patterns
- Create seamless onboarding and progressive feature discovery
- Enhance feedback loops and user satisfaction tracking
- Integrate smart assistance and contextual help
- Implement user journey optimization and flow improvements
"""

import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import utils
from .ui_enhancement_system import get_ui_enhancement_system
from .user_preference_learning import get_user_preference_learning_system


class UXEventType(Enum):
    """Types of UX events to track."""

    USER_ONBOARDING = "user_onboarding"
    COMMAND_EXECUTION = "command_execution"
    ERROR_ENCOUNTER = "error_encounter"
    HELP_REQUEST = "help_request"
    WORKFLOW_COMPLETION = "workflow_completion"
    FEATURE_DISCOVERY = "feature_discovery"
    SATISFACTION_FEEDBACK = "satisfaction_feedback"
    ABANDONMENT = "abandonment"


class UXInterventionType(Enum):
    """Types of UX interventions."""

    PROACTIVE_HELP = "proactive_help"
    ERROR_RECOVERY = "error_recovery"
    WORKFLOW_GUIDANCE = "workflow_guidance"
    FEATURE_INTRODUCTION = "feature_introduction"
    SATISFACTION_CHECK = "satisfaction_check"
    ONBOARDING_ASSISTANCE = "onboarding_assistance"


class UXSatisfactionLevel(Enum):
    """User satisfaction levels."""

    VERY_DISSATISFIED = 1
    DISSATISFIED = 2
    NEUTRAL = 3
    SATISFIED = 4
    VERY_SATISFIED = 5


@dataclass
class UXEvent:
    """A user experience event."""

    event_id: str
    event_type: UXEventType
    user_id: str
    timestamp: datetime

    # Event details
    context: Dict[str, Any] = field(default_factory=dict)
    command: Optional[str] = None
    success: bool = True
    error_details: Optional[str] = None
    duration_ms: float = 0.0

    # User state
    user_expertise: Optional[str] = None
    session_id: Optional[str] = None
    workflow_step: Optional[str] = None


@dataclass
class UXIntervention:
    """A UX intervention to help the user."""

    intervention_id: str
    intervention_type: UXInterventionType
    user_id: str
    trigger_event: str

    # Intervention details
    message: str
    suggested_actions: List[str] = field(default_factory=list)
    help_content: Optional[str] = None
    priority: int = 1  # 1 - 5 scale

    # Timing and delivery
    created_at: datetime = field(default_factory=datetime.now)
    delivered_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None

    # Effectiveness
    user_followed_suggestion: bool = False
    satisfaction_improvement: Optional[float] = None


@dataclass
class UserJourney:
    """A user's journey through the system."""

    journey_id: str
    user_id: str
    started_at: datetime
    goal: str

    # Journey progress
    current_step: str = "started"
    steps_completed: List[str] = field(default_factory=list)
    steps_failed: List[str] = field(default_factory=list)

    # Journey metrics
    total_commands: int = 0
    successful_commands: int = 0
    errors_encountered: int = 0
    help_requests: int = 0

    # Journey outcome
    completed_at: Optional[datetime] = None
    success: bool = False
    satisfaction_score: Optional[float] = None
    lessons_learned: List[str] = field(default_factory=list)


class SmartErrorHandler:
    """Intelligent error handling with recovery guidance."""

    def __init__(self, root: Path):
        self.root = root
        self.error_patterns = self._load_error_patterns()
        self.recovery_strategies = self._load_recovery_strategies()

    def _load_error_patterns(self) -> Dict[str, Any]:
        """Load known error patterns and their solutions."""
        return {
            "AttributeError": {
                "common_causes": [
                    "Accessing non - existent attribute",
                    "Object not initialized properly",
                    "Module not imported correctly",
                ],
                "recovery_actions": [
                    "Check object initialization",
                    "Verify attribute name spelling",
                    "Check import statements",
                ],
            },
            "FileNotFoundError": {
                "common_causes": [
                    "File path incorrect",
                    "File doesn't exist",
                    "Permission issues",
                ],
                "recovery_actions": [
                    "Check file path spelling",
                    "Verify file exists",
                    "Check file permissions",
                ],
            },
            "JSONDecodeError": {
                "common_causes": [
                    "Invalid JSON syntax",
                    "Empty or corrupted file",
                    "Incorrect parameter format",
                ],
                "recovery_actions": [
                    "Validate JSON syntax",
                    "Check parameter format",
                    "Use simple key = value format instead",
                ],
            },
            "CommandError": {
                "common_causes": [
                    "Incorrect command syntax",
                    "Missing required parameters",
                    "Command not available",
                ],
                "recovery_actions": [
                    "Check command spelling",
                    "Use 'help <command>' for syntax",
                    "Try 'suggest' for alternatives",
                ],
            },
        }

    def _load_recovery_strategies(self) -> Dict[str, List[str]]:
        """Load recovery strategies for different error types."""
        return {
            "first_time_user": [
                "Don't worry! This is common for new users.",
                "Try the getting started tutorial: help --tutorial getting_started",
                "Use 'suggest' to get personalized recommendations",
            ],
            "experienced_user": [
                "This error pattern suggests a configuration issue.",
                "Check your recent changes with 'config show'",
                "Try 'validate' to check system health",
            ],
            "complex_command": [
                "Complex commands can be tricky. Let's break it down.",
                "Try the interactive wizard: wizard <workflow - type>",
                "Use 'help <command> --examples' for detailed examples",
            ],
        }

    def handle_error(
        self, error: Exception, context: Dict[str, Any], user_id: str
    ) -> UXIntervention:
        """Handle an error with intelligent recovery guidance."""
        error_type = type(error).__name__
        error_message = str(error)

        # Get user profile for personalized response
        ui_system = get_ui_enhancement_system(self.root)
        user_profile = ui_system.get_user_profile(user_id)

        # Determine user experience level
        if user_profile.expertise_level.value == "beginner":
            strategy_key = "first_time_user"
        elif user_profile.expertise_level.value in ["advanced", "expert"]:
            strategy_key = "experienced_user"
        else:
            strategy_key = "complex_command"

        # Get error pattern information
        pattern_info = self.error_patterns.get(error_type, {})
        recovery_actions = pattern_info.get("recovery_actions", [])

        # Get recovery strategy
        recovery_strategy = self.recovery_strategies.get(strategy_key, [])

        # Create helpful error message
        message_parts = []
        message_parts.append(f"❌ {error_type}: {error_message}")
        message_parts.append("")

        if pattern_info.get("common_causes"):
            message_parts.append("🔍 Common causes:")
            for cause in pattern_info["common_causes"]:
                message_parts.append(f"  • {cause}")
            message_parts.append("")

        message_parts.append("💡 Suggested recovery:")
        for strategy in recovery_strategy[:2]:  # Show top 2 strategies
            message_parts.append(f"  • {strategy}")

        # Combine recovery actions
        all_actions = recovery_actions + recovery_strategy

        intervention = UXIntervention(
            intervention_id=f"error_recovery_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            intervention_type=UXInterventionType.ERROR_RECOVERY,
            user_id=user_id,
            trigger_event=f"error_{error_type}",
            message="\n".join(message_parts),
            suggested_actions=all_actions[:5],  # Top 5 actions
            priority=4,  # High priority for errors
        )

        return intervention


class OnboardingAssistant:
    """Intelligent onboarding assistance for new users."""

    def __init__(self, root: Path):
        self.root = root
        self.onboarding_flows = self._create_onboarding_flows()

    def _create_onboarding_flows(self) -> Dict[str, Dict[str, Any]]:
        """Create onboarding flows for different user types."""
        return {
            "first_time_user": {
                "name": "First Time User Onboarding",
                "steps": [
                    {
                        "step": "welcome",
                        "title": "Welcome to AI Onboard!",
                        "message": "Let's get you started with your first project.",
                        "actions": ["help --tutorial getting_started", "charter"],
                    },
                    {
                        "step": "create_charter",
                        "title": "Define Your Project Vision",
                        "message": "Every great project starts with a clear vision.",
                        "actions": ["charter", "help charter"],
                    },
                    {
                        "step": "create_plan",
                        "title": "Generate Your Project Plan",
                        "message": "Now let's create a detailed plan for your project.",
                        "actions": ["plan", "help plan"],
                    },
                    {
                        "step": "check_progress",
                        "title": "Monitor Your Progress",
                        "message": "See how your project is progressing.",
                        "actions": ["dashboard", "prompt progress"],
                    },
                ],
            },
            "experienced_developer": {
                "name": "Experienced Developer Onboarding",
                "steps": [
                    {
                        "step": "power_features",
                        "title": "Explore Advanced Features",
                        "message": "Discover powerful automation and AI features.",
                        "actions": ["kaizen - auto status", "opt - experiments --help"],
                    },
                    {
                        "step": "integration",
                        "title": "Set Up Integrations",
                        "message": "Connect with your existing development workflow.",
                        "actions": ["cursor init", "api start"],
                    },
                ],
            },
        }

    def get_onboarding_step(
        self, user_id: str, user_type: str = "first_time_user"
    ) -> Optional[Dict[str, Any]]:
        """Get the next onboarding step for a user."""
        ui_system = get_ui_enhancement_system(self.root)
        user_profile = ui_system.get_user_profile(user_id)

        # Determine which flow to use
        total_usage = sum(user_profile.command_usage_count.values())

        if total_usage == 0:
            flow_key = "first_time_user"
        elif user_profile.expertise_level.value in ["advanced", "expert"]:
            flow_key = "experienced_developer"
        else:
            flow_key = "first_time_user"

        flow = self.onboarding_flows.get(flow_key, {})
        steps = flow.get("steps", [])

        if not steps:
            return None

        # Find the next step based on user progress
        for step in steps:
            step_actions = step.get("actions", [])

            # Check if user has completed this step
            completed = False
            for action in step_actions:
                command = action.split()[0]  # Get first word (command name)
                if user_profile.command_usage_count.get(command, 0) > 0:
                    completed = True
                    break

            if not completed:
                return step

        # All steps completed
        return None

    def create_onboarding_intervention(self, user_id: str) -> Optional[UXIntervention]:
        """Create an onboarding intervention for a user."""
        next_step = self.get_onboarding_step(user_id)

        if not next_step:
            return None

        intervention = UXIntervention(
            intervention_id=f"onboarding_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            intervention_type=UXInterventionType.ONBOARDING_ASSISTANCE,
            user_id=user_id,
            trigger_event="onboarding_check",
            message=f"📚 {next_step['title']}\n\n{next_step['message']}",
            suggested_actions=next_step.get("actions", []),
            priority=3,  # Medium - high priority
        )

        return intervention


class WorkflowOptimizer:
    """Optimizes user workflows based on usage patterns."""

    def __init__(self, root: Path):
        self.root = root
        self.common_workflows = self._define_common_workflows()

    def _define_common_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Define common user workflows."""
        return {
            "project_setup": {
                "name": "Project Setup Workflow",
                "steps": ["charter", "plan", "align", "validate"],
                "description": "Complete project setup from vision to validation",
                "estimated_time": "15 - 30 minutes",
            },
            "optimization_cycle": {
                "name": "Optimization Workflow",
                "steps": ["validate", "kaizen", "opt - experiments", "validate"],
                "description": "Identify and implement optimizations",
                "estimated_time": "30 - 60 minutes",
            },
            "ai_collaboration": {
                "name": "AI Collaboration Setup",
                "steps": ["ai - agent", "aaol", "enhanced - context"],
                "description": "Set up advanced AI collaboration features",
                "estimated_time": "20 - 40 minutes",
            },
            "development_integration": {
                "name": "Development Integration",
                "steps": ["cursor", "api", "unified - metrics"],
                "description": "Integrate with development tools",
                "estimated_time": "25 - 45 minutes",
            },
        }

    def detect_workflow_intent(
        self, user_id: str, recent_commands: List[str]
    ) -> Optional[str]:
        """Detect if user is following a known workflow."""
        # Analyze recent command sequence
        for workflow_id, workflow in self.common_workflows.items():
            workflow_steps = workflow["steps"]

            # Check if recent commands match workflow pattern
            matches = 0
            for cmd in recent_commands:
                if cmd in workflow_steps:
                    matches += 1

            # If user has used multiple commands from a workflow
            if matches >= 2:
                return workflow_id

        return None

    def suggest_workflow_continuation(
        self, user_id: str, workflow_id: str
    ) -> Optional[UXIntervention]:
        """Suggest next steps in a workflow."""
        workflow = self.common_workflows.get(workflow_id)
        if not workflow:
            return None

        ui_system = get_ui_enhancement_system(self.root)
        user_profile = ui_system.get_user_profile(user_id)

        # Find next step in workflow
        workflow_steps = workflow["steps"]
        completed_steps = []

        for step in workflow_steps:
            if user_profile.command_usage_count.get(step, 0) > 0:
                completed_steps.append(step)

        # Find next uncompleted step
        next_steps = []
        for step in workflow_steps:
            if step not in completed_steps:
                next_steps.append(step)

        if not next_steps:
            return None  # Workflow completed

        next_step = next_steps[0]
        progress = len(completed_steps) / len(workflow_steps) * 100

        message = f"🔄 {workflow['name']} ({progress:.0f}% complete)\n\n"
        message += f"Next step: {next_step}\n"
        message += f"Estimated time remaining: {workflow['estimated_time']}"

        intervention = UXIntervention(
            intervention_id=f"workflow_{workflow_id}_{int(time.time())}",
            intervention_type=UXInterventionType.WORKFLOW_GUIDANCE,
            user_id=user_id,
            trigger_event=f"workflow_detected_{workflow_id}",
            message=message,
            suggested_actions=[next_step, f"help {next_step}"],
            priority=2,  # Medium priority
        )

        return intervention


class SatisfactionTracker:
    """Tracks and improves user satisfaction."""

    def __init__(self, root: Path):
        self.root = root
        self.satisfaction_data_file = root / ".ai_onboard" / "satisfaction_data.jsonl"
        utils.ensure_dir(self.satisfaction_data_file.parent)

    def record_satisfaction(
        self, user_id: str, context: str, score: float, feedback: str = ""
    ):
        """Record user satisfaction score."""
        satisfaction_record = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "context": context,
            "score": score,
            "feedback": feedback,
        }

        with open(self.satisfaction_data_file, "a") as f:
            f.write(json.dumps(satisfaction_record) + "\n")

    def get_satisfaction_trend(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get satisfaction trend for a user."""
        if not self.satisfaction_data_file.exists():
            return {"average": 0, "trend": "no_data", "recent_scores": []}

        cutoff_date = datetime.now() - timedelta(days=days)
        scores = []

        try:
            with open(self.satisfaction_data_file, "r") as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if record.get("user_id") == user_id:
                            record_date = datetime.fromisoformat(record["timestamp"])
                            if record_date >= cutoff_date:
                                scores.append(record["score"])
                    except (json.JSONDecodeError, ValueError):
                        continue
        except Exception:
            return {"average": 0, "trend": "error", "recent_scores": []}

        if not scores:
            return {"average": 0, "trend": "no_data", "recent_scores": []}

        average = sum(scores) / len(scores)

        # Determine trend
        if len(scores) >= 3:
            recent_avg = sum(scores[-3:]) / 3
            older_avg = (
                sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else average
            )

            if recent_avg > older_avg + 0.5:
                trend = "improving"
            elif recent_avg < older_avg - 0.5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "average": average,
            "trend": trend,
            "recent_scores": scores[-10:],  # Last 10 scores
            "total_responses": len(scores),
        }

    def should_request_feedback(self, user_id: str) -> bool:
        """Determine if we should request feedback from user."""
        ui_system = get_ui_enhancement_system(self.root)
        user_profile = ui_system.get_user_profile(user_id)

        total_usage = sum(user_profile.command_usage_count.values())

        # Request feedback after certain milestones
        feedback_milestones = [5, 15, 50, 100]

        return total_usage in feedback_milestones


class UserExperienceEnhancementSystem:
    """Main system for user experience enhancements."""

    def __init__(self, root: Path):
        self.root = root
        self.data_dir = root / ".ai_onboard" / "ux_enhancements"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Components
        self.ui_system = get_ui_enhancement_system(root)
        self.preference_system = get_user_preference_learning_system(root)
        self.error_handler = SmartErrorHandler(root)
        self.onboarding_assistant = OnboardingAssistant(root)
        self.workflow_optimizer = WorkflowOptimizer(root)
        self.satisfaction_tracker = SatisfactionTracker(root)

        # State
        self.active_interventions: Dict[str, UXIntervention] = {}
        self.user_journeys: Dict[str, UserJourney] = {}
        self.ux_events: List[UXEvent] = []

        # Configuration
        self.config = self._load_ux_config()

    def _load_ux_config(self) -> Dict[str, Any]:
        """Load UX enhancement configuration."""
        config_file = self.data_dir / "ux_config.json"

        default_config = {
            "enable_proactive_help": True,
            "enable_error_recovery": True,
            "enable_workflow_optimization": True,
            "enable_satisfaction_tracking": True,
            "intervention_cooldown_minutes": 5,
            "max_interventions_per_session": 3,
            "satisfaction_request_frequency": "milestone",  # milestone, periodic, never
            "onboarding_enabled": True,
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

    def record_ux_event(
        self, event_type: UXEventType, user_id: str, **kwargs
    ) -> UXEvent:
        """Record a UX event."""
        event = UXEvent(
            event_id=f"ux_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            user_id=user_id,
            timestamp=datetime.now(),
            **kwargs,
        )

        self.ux_events.append(event)

        # Trigger UX analysis and potential interventions
        self._analyze_event_and_intervene(event)

        return event

    def _analyze_event_and_intervene(self, event: UXEvent):
        """Analyze a UX event and create interventions if needed."""
        if not self.config.get("enable_proactive_help", True):
            return

        user_id = event.user_id
        interventions = []

        # Error recovery
        if event.event_type == UXEventType.ERROR_ENCOUNTER and self.config.get(
            "enable_error_recovery", True
        ):
            if event.error_details:
                try:
                    # Create a mock exception for error handling
                    event.context.get("error_type", "Exception")
                    error_msg = event.error_details

                    # Create error recovery intervention
                    intervention = self.error_handler.handle_error(
                        Exception(error_msg), event.context, user_id
                    )
                    interventions.append(intervention)
                except Exception:
                    pass

        # Onboarding assistance
        if event.event_type == UXEventType.USER_ONBOARDING and self.config.get(
            "onboarding_enabled", True
        ):
            intervention = self.onboarding_assistant.create_onboarding_intervention(
                user_id
            )
            if intervention:
                interventions.append(intervention)

        # Workflow optimization
        if event.event_type == UXEventType.COMMAND_EXECUTION and self.config.get(
            "enable_workflow_optimization", True
        ):
            user_profile = self.ui_system.get_user_profile(user_id)
            recent_commands = user_profile.last_used_commands[:5]

            workflow_id = self.workflow_optimizer.detect_workflow_intent(
                user_id, recent_commands
            )
            if workflow_id:
                intervention = self.workflow_optimizer.suggest_workflow_continuation(
                    user_id, workflow_id
                )
                if intervention:
                    interventions.append(intervention)

        # Satisfaction tracking
        if self.config.get("enable_satisfaction_tracking", True):
            if self.satisfaction_tracker.should_request_feedback(user_id):
                intervention = self._create_satisfaction_intervention(user_id)
                if intervention:
                    interventions.append(intervention)

        # Store interventions
        for intervention in interventions:
            self.active_interventions[intervention.intervention_id] = intervention

    def _create_satisfaction_intervention(self, user_id: str) -> UXIntervention:
        """Create a satisfaction feedback intervention."""
        intervention = UXIntervention(
            intervention_id=f"satisfaction_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            intervention_type=UXInterventionType.SATISFACTION_CHECK,
            user_id=user_id,
            trigger_event="satisfaction_milestone",
            message="📝 How is your experience with AI Onboard so far?\n\nYour feedback helps us improve the system.",
            suggested_actions=[
                "Rate your experience (1 - 5 scale)",
                "Share what's working well",
                "Suggest improvements",
            ],
            priority=1,  # Low priority
        )

        return intervention

    def get_pending_interventions(self, user_id: str) -> List[UXIntervention]:
        """Get pending interventions for a user."""
        user_interventions = []

        for intervention in self.active_interventions.values():
            if (
                intervention.user_id == user_id
                and intervention.delivered_at is None
                and intervention.dismissed_at is None
            ):
                user_interventions.append(intervention)

        # Sort by priority (higher first)
        user_interventions.sort(key=lambda x: x.priority, reverse=True)

        # Limit interventions per session
        max_interventions = self.config.get("max_interventions_per_session", 3)
        return user_interventions[:max_interventions]

    def deliver_intervention(self, intervention_id: str) -> Optional[str]:
        """Deliver an intervention to the user and return formatted message."""
        intervention = self.active_interventions.get(intervention_id)
        if not intervention:
            return None

        intervention.delivered_at = datetime.now()

        # Format intervention message
        message_parts = [intervention.message]

        if intervention.suggested_actions:
            message_parts.append("\n💡 Suggested actions:")
            for i, action in enumerate(intervention.suggested_actions[:3], 1):
                message_parts.append(f"  {i}. {action}")

        return "\n".join(message_parts)

    def dismiss_intervention(self, intervention_id: str, user_followed: bool = False):
        """Dismiss an intervention."""
        intervention = self.active_interventions.get(intervention_id)
        if intervention:
            intervention.dismissed_at = datetime.now()
            intervention.user_followed_suggestion = user_followed

    def get_user_journey(
        self, user_id: str, goal: str = "general_usage"
    ) -> UserJourney:
        """Get or create a user journey."""
        journey_key = f"{user_id}_{goal}"

        if journey_key not in self.user_journeys:
            self.user_journeys[journey_key] = UserJourney(
                journey_id=journey_key,
                user_id=user_id,
                started_at=datetime.now(),
                goal=goal,
            )

        return self.user_journeys[journey_key]

    def update_journey_progress(
        self, user_id: str, step: str, success: bool, goal: str = "general_usage"
    ):
        """Update user journey progress."""
        journey = self.get_user_journey(user_id, goal)

        journey.total_commands += 1

        if success:
            journey.successful_commands += 1
            if step not in journey.steps_completed:
                journey.steps_completed.append(step)
        else:
            journey.errors_encountered += 1
            if step not in journey.steps_failed:
                journey.steps_failed.append(step)

    def get_ux_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get UX analytics for a user."""
        # Get user events
        user_events = [e for e in self.ux_events if e.user_id == user_id]

        # Get satisfaction data
        satisfaction_data = self.satisfaction_tracker.get_satisfaction_trend(user_id)

        # Get user profile
        user_profile = self.ui_system.get_user_profile(user_id)

        # Calculate metrics
        total_commands = sum(user_profile.command_usage_count.values())
        error_events = [
            e for e in user_events if e.event_type == UXEventType.ERROR_ENCOUNTER
        ]
        help_requests = [
            e for e in user_events if e.event_type == UXEventType.HELP_REQUEST
        ]

        error_rate = len(error_events) / total_commands if total_commands > 0 else 0
        help_rate = len(help_requests) / total_commands if total_commands > 0 else 0

        return {
            "user_id": user_id,
            "expertise_level": user_profile.expertise_level.value,
            "total_commands": total_commands,
            "unique_commands": len(user_profile.command_usage_count),
            "error_rate": error_rate,
            "help_request_rate": help_rate,
            "satisfaction": satisfaction_data,
            "recent_events": len(
                [
                    e
                    for e in user_events
                    if e.timestamp >= datetime.now() - timedelta(days=7)
                ]
            ),
            "active_interventions": len(self.get_pending_interventions(user_id)),
        }


# Global instance
_ux_enhancement_system: Optional[UserExperienceEnhancementSystem] = None


def get_ux_enhancement_system(root: Path) -> UserExperienceEnhancementSystem:
    """Get the global UX enhancement system."""
    global _ux_enhancement_system
    if _ux_enhancement_system is None:
        _ux_enhancement_system = UserExperienceEnhancementSystem(root)
    return _ux_enhancement_system
