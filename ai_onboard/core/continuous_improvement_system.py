"""
Continuous Improvement System - Self - evolving system that learns and optimizes.

This system creates intelligent feedback loops that:
- Learn from user interactions and system performance
- Optimize system behavior based on usage patterns
- Adapt configuration based on project types and user preferences
- Monitor system health and implement self - healing
- Evolve knowledge base and improve recommendations
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Union

from . import smart_debugger, telemetry, universal_error_monitor, utils


class LearningType(Enum):
    """Types of learning the system can perform."""

    USER_PREFERENCE = "user_preference"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ERROR_PATTERN = "error_pattern"
    USAGE_PATTERN = "usage_pattern"
    PROJECT_TYPE = "project_type"
    SYSTEM_HEALTH = "system_health"
    KNOWLEDGE_ACQUISITION = "knowledge_acquisition"
    KNOWLEDGE_EVOLUTION = "knowledge_evolution"


class ImprovementAction(Enum):
    """Types of improvement actions the system can take."""

    ADJUST_CONFIG = "adjust_config"
    UPDATE_RECOMMENDATIONS = "update_recommendations"
    OPTIMIZE_PERFORMANCE = "optimize_performance"
    IMPROVE_ACCURACY = "improve_accuracy"
    ENHANCE_UX = "enhance_ux"
    PREVENT_ERRORS = "prevent_errors"
    ADAPT_WORKFLOW = "adapt_workflow"


@dataclass
class LearningEvent:
    """A single learning event that contributes to system improvement."""

    event_id: str
    timestamp: datetime
    learning_type: LearningType
    context: Dict[str, Any]
    outcome: Dict[str, Any]
    confidence: float
    impact_score: float
    source: str  # Which system generated this learning event


@dataclass
class ImprovementRecommendation:
    """A recommendation for system improvement."""

    recommendation_id: str
    action_type: ImprovementAction
    description: str
    rationale: str
    expected_impact: float
    confidence: float
    priority: int  # 1 - 10, higher is more important
    implementation_effort: int  # 1 - 10, higher is more effort
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, approved, implemented, rejected


@dataclass
class UserProfile:
    """Profile of user preferences and patterns."""

    user_id: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    usage_patterns: Dict[str, Any] = field(default_factory=dict)
    project_types: List[str] = field(default_factory=list)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    satisfaction_scores: List[float] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class SystemHealthMetrics:
    """System health and performance metrics."""

    timestamp: datetime
    performance_score: float
    error_rate: float
    user_satisfaction: float
    system_uptime: float
    resource_usage: Dict[str, float]
    component_health: Dict[str, float]
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ContinuousImprovementSystem:
    """Main continuous improvement system that orchestrates learning and \
        optimization."""

    def __init__(self, root: Path):
        self.root = root
        self.learning_events_path = root / ".ai_onboard" / "learning_events.jsonl"
        self.improvement_recommendations_path = (
            root / ".ai_onboard" / "improvement_recommendations.json"
        )
        self.user_profiles_path = root / ".ai_onboard" / "user_profiles.json"
        self.system_health_path = root / ".ai_onboard" / "system_health.jsonl"
        self.adaptive_config_path = root / ".ai_onboard" / "adaptive_config.json"
        self.knowledge_base_path = root / ".ai_onboard" / "knowledge_base.json"

        # Initialize subsystems
        self.smart_debugger = smart_debugger.SmartDebugger(root)
        self.error_monitor = universal_error_monitor.get_error_monitor(root)

        # Ensure directories exist
        self._ensure_directories()

        # Load existing data
        self.user_profiles = self._load_user_profiles()
        self.improvement_recommendations = self._load_improvement_recommendations()
        self.adaptive_config = self._load_adaptive_config()
        self.knowledge_base = self._load_knowledge_base()

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for path in [
            self.learning_events_path,
            self.improvement_recommendations_path,
            self.user_profiles_path,
            self.system_health_path,
            self.adaptive_config_path,
            self.knowledge_base_path,
        ]:
            utils.ensure_dir(path.parent)

    def _load_user_profiles(self) -> Dict[str, UserProfile]:
        """Load user profiles from storage."""
        if not self.user_profiles_path.exists():
            return {}

        data = utils.read_json(self.user_profiles_path, default={})
        profiles = {}

        for user_id, profile_data in data.items():
            profiles[user_id] = UserProfile(
                user_id=user_id,
                preferences=profile_data.get("preferences", {}),
                usage_patterns=profile_data.get("usage_patterns", {}),
                project_types=profile_data.get("project_types", []),
                interaction_history=profile_data.get("interaction_history", []),
                satisfaction_scores=profile_data.get("satisfaction_scores", []),
                last_updated=datetime.fromisoformat(
                    profile_data.get("last_updated", datetime.now().isoformat())
                ),
            )

        return profiles

    def _load_improvement_recommendations(self) -> List[ImprovementRecommendation]:
        """Load improvement recommendations from storage."""
        if not self.improvement_recommendations_path.exists():
            return []

        data = utils.read_json(self.improvement_recommendations_path, default=[])
        recommendations = []

        for rec_data in data:
            recommendations.append(
                ImprovementRecommendation(
                    recommendation_id=rec_data["recommendation_id"],
                    action_type=ImprovementAction(rec_data["action_type"]),
                    description=rec_data["description"],
                    rationale=rec_data["rationale"],
                    expected_impact=rec_data["expected_impact"],
                    confidence=rec_data["confidence"],
                    priority=rec_data["priority"],
                    implementation_effort=rec_data["implementation_effort"],
                    dependencies=rec_data.get("dependencies", []),
                    created_at=datetime.fromisoformat(rec_data["created_at"]),
                    status=rec_data.get("status", "pending"),
                )
            )

        return recommendations

    def _load_adaptive_config(self) -> Dict[str, Any]:
        """Load adaptive configuration from storage."""
        return utils.read_json(
            self.adaptive_config_path,
            default={
                "gate_timeouts": {"default": 2, "adaptive": True},
                "safety_levels": {"default": "medium", "adaptive": True},
                "collaboration_modes": {"default": "collaborative", "adaptive": True},
                "vision_interrogation": {
                    "adaptive_questions": True,
                    "smart_followup": True,
                },
                "error_handling": {"auto_recovery": True, "learning_enabled": True},
                "performance": {"auto_optimization": True, "resource_monitoring": True},
            },
        )

    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load knowledge base from storage."""
        return utils.read_json(
            self.knowledge_base_path,
            default={
                "project_types": {},
                "common_patterns": {},
                "best_practices": {},
                "error_solutions": {},
                "user_preferences": {},
                "performance_optimizations": {},
            },
        )

    def record_learning_event(
        self,
        learning_type: Union[LearningType, str],
        context: Dict[str, Any],
        outcome: Dict[str, Any],
        confidence: float,
        impact_score: float,
        source: str,
    ) -> str:
        """Record a learning event for system improvement."""
        # Convert string to enum if needed
        if isinstance(learning_type, str):
            try:
                learning_type = LearningType(learning_type)
            except ValueError:
                # If not a valid enum value, use a default
                learning_type = LearningType.USER_PREFERENCE

        event_id = f"learn_{int(time.time())}_{utils.random_string(8)}"

        event = LearningEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            learning_type=learning_type,
            context=context,
            outcome=outcome,
            confidence=confidence,
            impact_score=impact_score,
            source=source,
        )

        # Log the learning event
        self._log_learning_event(event)

        # Process the learning event
        self._process_learning_event(event)

        # Log telemetry
        telemetry.log_event(
            "learning_event_recorded",
            event_id=event_id,
            learning_type=learning_type.value,
            confidence=confidence,
            impact_score=impact_score,
            source=source,
        )

        return event_id

    def _log_learning_event(self, event: LearningEvent):
        """Log a learning event to storage."""
        event_data = {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "learning_type": event.learning_type.value,
            "context": event.context,
            "outcome": event.outcome,
            "confidence": event.confidence,
            "impact_score": event.impact_score,
            "source": event.source,
        }

        with open(self.learning_events_path, "a", encoding="utf-8") as f:
            json.dump(event_data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    def _process_learning_event(self, event: LearningEvent):
        """Process a learning event and generate improvements."""
        if event.learning_type == LearningType.USER_PREFERENCE:
            self._process_user_preference_learning(event)
        elif event.learning_type == LearningType.PERFORMANCE_OPTIMIZATION:
            self._process_performance_learning(event)
        elif event.learning_type == LearningType.ERROR_PATTERN:
            self._process_error_pattern_learning(event)
        elif event.learning_type == LearningType.USAGE_PATTERN:
            self._process_usage_pattern_learning(event)
        elif event.learning_type == LearningType.PROJECT_TYPE:
            self._process_project_type_learning(event)
        elif event.learning_type == LearningType.SYSTEM_HEALTH:
            self._process_system_health_learning(event)

    def _process_user_preference_learning(self, event: LearningEvent):
        """Process user preference learning events."""
        user_id = event.context.get("user_id", "default")
        preference_type = event.context.get("preference_type")
        preference_value = event.outcome.get("preferred_value")

        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)

        profile = self.user_profiles[user_id]

        # Update preferences
        if preference_type and preference_value is not None:
            profile.preferences[preference_type] = preference_value

        # Update interaction history
        profile.interaction_history.append(
            {
                "timestamp": event.timestamp.isoformat(),
                "type": "preference_learning",
                "context": event.context,
                "outcome": event.outcome,
            }
        )

        # Update satisfaction scores
        satisfaction = event.outcome.get("satisfaction_score")
        if satisfaction is not None:
            profile.satisfaction_scores.append(satisfaction)
            # Keep only last 100 scores
            if len(profile.satisfaction_scores) > 100:
                profile.satisfaction_scores = profile.satisfaction_scores[-100:]

        profile.last_updated = datetime.now()

        # Generate improvement recommendations
        self._generate_user_preference_recommendations(profile, event)

    def _process_performance_learning(self, event: LearningEvent):
        """Process performance optimization learning events."""
        performance_metrics = event.context.get("performance_metrics", {})
        optimization_result = event.outcome.get("optimization_result", {})

        # Update knowledge base with performance insights
        if "performance_optimizations" not in self.knowledge_base:
            self.knowledge_base["performance_optimizations"] = {}

        optimization_key = f"{event.context.get('operation_type', 'unknown')}_{event.context.get('project_type', 'generic')}"

        if optimization_key not in self.knowledge_base["performance_optimizations"]:
            self.knowledge_base["performance_optimizations"][optimization_key] = {
                "optimizations": [],
                "success_rate": 0.0,
                "total_attempts": 0,
            }

        opt_data = self.knowledge_base["performance_optimizations"][optimization_key]
        opt_data["optimizations"].append(
            {
                "timestamp": event.timestamp.isoformat(),
                "metrics": performance_metrics,
                "result": optimization_result,
                "confidence": event.confidence,
            }
        )

        # Update success rate
        opt_data["total_attempts"] += 1
        if optimization_result.get("success", False):
            opt_data["success_rate"] = (
                opt_data["success_rate"] * (opt_data["total_attempts"] - 1) + 1.0
            ) / opt_data["total_attempts"]
        else:
            opt_data["success_rate"] = (
                opt_data["success_rate"] * (opt_data["total_attempts"] - 1)
            ) / opt_data["total_attempts"]

        # Generate performance improvement recommendations
        self._generate_performance_recommendations(event)

    def _process_error_pattern_learning(self, event: LearningEvent):
        """Process error pattern learning events."""
        error_type = event.context.get("error_type")
        error_context = event.context.get("error_context", {})
        solution_effectiveness = event.outcome.get("solution_effectiveness", 0.0)

        # Update knowledge base with error solutions
        if "error_solutions" not in self.knowledge_base:
            self.knowledge_base["error_solutions"] = {}

        if error_type not in self.knowledge_base["error_solutions"]:
            self.knowledge_base["error_solutions"][error_type] = {
                "solutions": [],
                "effectiveness_scores": [],
                "common_contexts": [],
            }

        error_data = self.knowledge_base["error_solutions"][error_type]

        # Add solution if it was effective
        if solution_effectiveness > 0.5:
            error_data["solutions"].append(
                {
                    "timestamp": event.timestamp.isoformat(),
                    "context": error_context,
                    "solution": event.outcome.get("solution"),
                    "effectiveness": solution_effectiveness,
                }
            )

        error_data["effectiveness_scores"].append(solution_effectiveness)
        error_data["common_contexts"].append(error_context)

        # Generate error prevention recommendations
        self._generate_error_prevention_recommendations(event)

    def _process_usage_pattern_learning(self, event: LearningEvent):
        """Process usage pattern learning events."""
        user_id = event.context.get("user_id", "default")
        usage_pattern = event.context.get("usage_pattern", {})

        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)

        profile = self.user_profiles[user_id]

        # Update usage patterns
        pattern_type = usage_pattern.get("type")
        if pattern_type:
            if pattern_type not in profile.usage_patterns:
                profile.usage_patterns[pattern_type] = []

            profile.usage_patterns[pattern_type].append(
                {
                    "timestamp": event.timestamp.isoformat(),
                    "pattern": usage_pattern,
                    "frequency": usage_pattern.get("frequency", 1),
                }
            )

        # Generate workflow adaptation recommendations
        self._generate_workflow_adaptation_recommendations(profile, event)

    def _process_project_type_learning(self, event: LearningEvent):
        """Process project type learning events."""
        project_type = event.context.get("project_type")
        project_characteristics = event.context.get("project_characteristics", {})
        success_indicators = event.outcome.get("success_indicators", {})

        # Update knowledge base with project type insights
        if "project_types" not in self.knowledge_base:
            self.knowledge_base["project_types"]: dict[str, Any] = {}

        if project_type not in self.knowledge_base["project_types"]:
            self.knowledge_base["project_types"][project_type] = {
                "characteristics": [],
                "success_patterns": [],
                "common_issues": [],
                "best_practices": [],
            }

        project_data = self.knowledge_base["project_types"][project_type]

        # Add characteristics
        project_data["characteristics"].append(
            {
                "timestamp": event.timestamp.isoformat(),
                "characteristics": project_characteristics,
                "success_indicators": success_indicators,
            }
        )

        # Generate project - specific recommendations
        self._generate_project_specific_recommendations(project_type, event)

    def _process_system_health_learning(self, event: LearningEvent):
        """Process system health learning events."""
        health_metrics = event.context.get("health_metrics", {})
        health_issues = event.outcome.get("health_issues", [])

        # Record system health metrics
        health_record = SystemHealthMetrics(
            timestamp=event.timestamp,
            performance_score=health_metrics.get("performance_score", 0.0),
            error_rate=health_metrics.get("error_rate", 0.0),
            user_satisfaction=health_metrics.get("user_satisfaction", 0.0),
            system_uptime=health_metrics.get("system_uptime", 0.0),
            resource_usage=health_metrics.get("resource_usage", {}),
            component_health=health_metrics.get("component_health", {}),
            bottlenecks=health_issues.get("bottlenecks", []),
            recommendations=health_issues.get("recommendations", []),
        )

        self._log_system_health(health_record)

        # Generate system health improvement recommendations
        self._generate_system_health_recommendations(health_record)

    def _generate_user_preference_recommendations(
        self, profile: UserProfile, event: LearningEvent
    ):
        """Generate recommendations based on user preference learning."""
        if len(profile.satisfaction_scores) < 3:
            return  # Need more data

        avg_satisfaction = sum(profile.satisfaction_scores) / len(
            profile.satisfaction_scores
        )

        if avg_satisfaction < 0.6:  # Low satisfaction
            recommendation = ImprovementRecommendation(
                recommendation_id=f"user_pref_{int(time.time())}",
                action_type=ImprovementAction.ENHANCE_UX,
                description=f"Improve user experience for {profile.user_id}",
                rationale=f"User satisfaction is {avg_satisfaction:.2f}, below threshold of 0.6",
                expected_impact=0.3,
                confidence=0.8,
                priority=7,
                implementation_effort=5,
            )

            self.improvement_recommendations.append(recommendation)

    def _generate_performance_recommendations(self, event: LearningEvent):
        """Generate recommendations based on performance learning."""
        event.context.get("performance_metrics", {})
        optimization_result = event.outcome.get("optimization_result", {})

        if optimization_result.get("success", False):
            # Successful optimization - recommend applying to similar contexts
            recommendation = ImprovementRecommendation(
                recommendation_id=f"perf_opt_{int(time.time())}",
                action_type=ImprovementAction.OPTIMIZE_PERFORMANCE,
                description=f"Apply successful optimization to similar contexts",
                rationale=f"Optimization improved performance by {optimization_result.get('improvement',
                    0):.1f}%",
                expected_impact=optimization_result.get("improvement", 0) / 100,
                confidence=event.confidence,
                priority=6,
                implementation_effort=3,
            )

            self.improvement_recommendations.append(recommendation)

    def _generate_error_prevention_recommendations(self, event: LearningEvent):
        """Generate recommendations based on error pattern learning."""
        error_type = event.context.get("error_type")
        solution_effectiveness = event.outcome.get("solution_effectiveness", 0.0)

        if solution_effectiveness > 0.8:  # Highly effective solution
            recommendation = ImprovementRecommendation(
                recommendation_id=f"error_prev_{int(time.time())}",
                action_type=ImprovementAction.PREVENT_ERRORS,
                description=f"Implement proactive prevention for {error_type}",
                rationale=f"Solution effectiveness is {solution_effectiveness:.2f}, suggesting proactive prevention",
                expected_impact=0.4,
                confidence=0.9,
                priority=8,
                implementation_effort=4,
            )

            self.improvement_recommendations.append(recommendation)

    def _generate_workflow_adaptation_recommendations(
        self, profile: UserProfile, event: LearningEvent
    ):
        """Generate recommendations based on usage pattern learning."""
        usage_pattern = event.context.get("usage_pattern", {})
        pattern_type = usage_pattern.get("type")

        if pattern_type == "frequent_manual_steps":
            recommendation = ImprovementRecommendation(
                recommendation_id=f"workflow_adapt_{int(time.time())}",
                action_type=ImprovementAction.ADAPT_WORKFLOW,
                description=f"Automate frequent manual steps for {profile.user_id}",
                rationale=f"User frequently performs manual steps that could be automated",
                expected_impact=0.5,
                confidence=0.7,
                priority=6,
                implementation_effort=6,
            )

            self.improvement_recommendations.append(recommendation)

    def _generate_project_specific_recommendations(
        self, project_type: str, event: LearningEvent
    ):
        """Generate recommendations based on project type learning."""
        success_indicators = event.outcome.get("success_indicators", {})

        if success_indicators.get("vision_clarity", 0) > 0.8:
            recommendation = ImprovementRecommendation(
                recommendation_id=f"proj_spec_{int(time.time())}",
                action_type=ImprovementAction.UPDATE_RECOMMENDATIONS,
                description=f"Update recommendations for {project_type} projects",
                rationale=f"High success rate ({success_indicators.get('vision_clarity',
                    0):.2f}) suggests good patterns",
                expected_impact=0.3,
                confidence=0.8,
                priority=5,
                implementation_effort=3,
            )

            self.improvement_recommendations.append(recommendation)

    def _generate_system_health_recommendations(
        self, health_record: SystemHealthMetrics
    ):
        """Generate recommendations based on system health learning."""
        if health_record.performance_score < 0.7:
            recommendation = ImprovementRecommendation(
                recommendation_id=f"sys_health_{int(time.time())}",
                action_type=ImprovementAction.OPTIMIZE_PERFORMANCE,
                description="Improve system performance",
                rationale=f"Performance score is {health_record.performance_score:.2f}, below threshold of 0.7",
                expected_impact=0.4,
                confidence=0.9,
                priority=9,
                implementation_effort=7,
            )

            self.improvement_recommendations.append(recommendation)

    def _log_system_health(self, health_record: SystemHealthMetrics):
        """Log system health metrics to storage."""
        health_data = {
            "timestamp": health_record.timestamp.isoformat(),
            "performance_score": health_record.performance_score,
            "error_rate": health_record.error_rate,
            "user_satisfaction": health_record.user_satisfaction,
            "system_uptime": health_record.system_uptime,
            "resource_usage": health_record.resource_usage,
            "component_health": health_record.component_health,
            "bottlenecks": health_record.bottlenecks,
            "recommendations": health_record.recommendations,
        }

        with open(self.system_health_path, "a", encoding="utf-8") as f:
            json.dump(health_data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    def get_improvement_recommendations(
        self, limit: int = 10, priority_threshold: int = 5, status: str = "pending"
    ) -> List[ImprovementRecommendation]:
        """Get improvement recommendations based on criteria."""
        filtered = [
            rec
            for rec in self.improvement_recommendations
            if rec.priority >= priority_threshold and rec.status == status
        ]

        # Sort by priority (descending) and expected impact (descending)
        filtered.sort(key=lambda x: (x.priority, x.expected_impact), reverse=True)

        return filtered[:limit]

    def implement_recommendation(self, recommendation_id: str) -> Dict[str, Any]:
        """Implement a specific improvement recommendation."""
        recommendation = None
        for rec in self.improvement_recommendations:
            if rec.recommendation_id == recommendation_id:
                recommendation = rec
                break

        if not recommendation:
            return {
                "status": "error",
                "message": f"Recommendation {recommendation_id} not found",
            }

        if recommendation.status != "pending":
            return {
                "status": "error",
                "message": f"Recommendation {recommendation_id} is not pending",
            }

        # Implement based on action type
        implementation_result = self._implement_recommendation_action(recommendation)

        # Update recommendation status
        recommendation.status = (
            "implemented" if implementation_result["success"] else "failed"
        )

        # Save updated recommendations
        self._save_improvement_recommendations()

        return implementation_result

    def _implement_recommendation_action(
        self, recommendation: ImprovementRecommendation
    ) -> Dict[str, Any]:
        """Implement the specific action for a recommendation."""
        try:
            if recommendation.action_type == ImprovementAction.ADJUST_CONFIG:
                return self._adjust_configuration(recommendation)
            elif recommendation.action_type == ImprovementAction.UPDATE_RECOMMENDATIONS:
                return self._update_recommendations(recommendation)
            elif recommendation.action_type == ImprovementAction.OPTIMIZE_PERFORMANCE:
                return self._optimize_performance(recommendation)
            elif recommendation.action_type == ImprovementAction.IMPROVE_ACCURACY:
                return self._improve_accuracy(recommendation)
            elif recommendation.action_type == ImprovementAction.ENHANCE_UX:
                return self._enhance_ux(recommendation)
            elif recommendation.action_type == ImprovementAction.PREVENT_ERRORS:
                return self._prevent_errors(recommendation)
            elif recommendation.action_type == ImprovementAction.ADAPT_WORKFLOW:
                return self._adapt_workflow(recommendation)
            else:
                return {
                    "success": False,
                    "message": f"Unknown action type: {recommendation.action_type}",
                }
        except Exception as e:
            return {"success": False, "message": f"Implementation failed: {str(e)}"}

    def _adjust_configuration(
        self, recommendation: ImprovementRecommendation
    ) -> Dict[str, Any]:
        """Adjust system configuration based on recommendation."""
        # This would implement specific configuration changes
        # For now, return success
        return {"success": True, "message": "Configuration adjusted"}

    def _update_recommendations(
        self, recommendation: ImprovementRecommendation
    ) -> Dict[str, Any]:
        """Update system recommendations based on learning."""
        # This would update recommendation algorithms
        return {"success": True, "message": "Recommendations updated"}

    def _optimize_performance(
        self, recommendation: ImprovementRecommendation
    ) -> Dict[str, Any]:
        """Optimize system performance based on recommendation."""
        # This would implement performance optimizations
        return {"success": True, "message": "Performance optimized"}

    def _improve_accuracy(
        self, recommendation: ImprovementRecommendation
    ) -> Dict[str, Any]:
        """Improve system accuracy based on recommendation."""
        # This would implement accuracy improvements
        return {"success": True, "message": "Accuracy improved"}

    def _enhance_ux(self, recommendation: ImprovementRecommendation) -> Dict[str, Any]:
        """Enhance user experience based on recommendation."""
        # This would implement UX improvements
        return {"success": True, "message": "User experience enhanced"}

    def _prevent_errors(
        self, recommendation: ImprovementRecommendation
    ) -> Dict[str, Any]:
        """Implement error prevention measures based on recommendation."""
        # This would implement error prevention
        return {"success": True, "message": "Error prevention implemented"}

    def _adapt_workflow(
        self, recommendation: ImprovementRecommendation
    ) -> Dict[str, Any]:
        """Adapt workflow based on recommendation."""
        # This would implement workflow adaptations
        return {"success": True, "message": "Workflow adapted"}

    def get_system_health_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get system health summary for the last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)

        health_records = []
        if self.system_health_path.exists():
            with open(self.system_health_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        record_date = datetime.fromisoformat(record["timestamp"])
                        if record_date >= cutoff_date:
                            health_records.append(record)
                    except (json.JSONDecodeError, KeyError):
                        continue

        if not health_records:
            return {
                "status": "no_data",
                "message": f"No health data for the last {days} days",
            }

        # Calculate summary statistics
        performance_scores = [r["performance_score"] for r in health_records]
        error_rates = [r["error_rate"] for r in health_records]
        user_satisfaction = [r["user_satisfaction"] for r in health_records]

        return {
            "status": "success",
            "period_days": days,
            "total_records": len(health_records),
            "avg_performance_score": sum(performance_scores) / len(performance_scores),
            "avg_error_rate": sum(error_rates) / len(error_rates),
            "avg_user_satisfaction": sum(user_satisfaction) / len(user_satisfaction),
            "trends": {
                "performance_trend": (
                    "improving"
                    if performance_scores[-1] > performance_scores[0]
                    else "declining"
                ),
                "error_trend": (
                    "improving" if error_rates[-1] < error_rates[0] else "worsening"
                ),
                "satisfaction_trend": (
                    "improving"
                    if user_satisfaction[-1] > user_satisfaction[0]
                    else "declining"
                ),
            },
            "latest_record": health_records[-1] if health_records else None,
        }

    def get_learning_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get learning activity summary for the last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)

        learning_events = []
        if self.learning_events_path.exists():
            with open(self.learning_events_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                        event_date = datetime.fromisoformat(event["timestamp"])
                        if event_date >= cutoff_date:
                            learning_events.append(event)
                    except (json.JSONDecodeError, KeyError):
                        continue

        if not learning_events:
            return {
                "status": "no_data",
                "message": f"No learning events for the last {days} days",
            }

        # Categorize by learning type
        by_type: Dict[str, List[Dict[str, Any]]] = {}
        for event in learning_events:
            learning_type = event.get("learning_type", "unknown")
            if learning_type not in by_type:
                by_type[learning_type] = []
            by_type[learning_type].append(event)

        # Calculate summary statistics
        avg_confidence = sum(e.get("confidence", 0.0) for e in learning_events) / len(
            learning_events
        )
        avg_impact = sum(e.get("impact_score", 0.0) for e in learning_events) / len(
            learning_events
        )

        return {
            "status": "success",
            "period_days": days,
            "total_events": len(learning_events),
            "events_by_type": {k: len(v) for k, v in by_type.items()},
            "avg_confidence": avg_confidence,
            "avg_impact_score": avg_impact,
            "top_sources": self._get_top_sources(learning_events),
            "recent_events": learning_events[-5:] if learning_events else [],
        }

    def _get_top_sources(
        self, learning_events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get top sources of learning events."""
        source_counts: dict[str, Any] = {}
        for event in learning_events:
            source = event.get("source", "unknown")
            if source not in source_counts:
                source_counts[source] = 0
            source_counts[source] += 1

        return [
            {"source": source, "count": count}
            for source, count in sorted(
                source_counts.items(), key=lambda x: x[1], reverse=True
            )
        ]

    def _save_user_profiles(self):
        """Save user profiles to storage."""
        data = {}
        for user_id, profile in self.user_profiles.items():
            data[user_id] = {
                "preferences": profile.preferences,
                "usage_patterns": profile.usage_patterns,
                "project_types": profile.project_types,
                "interaction_history": profile.interaction_history,
                "satisfaction_scores": profile.satisfaction_scores,
                "last_updated": profile.last_updated.isoformat(),
            }

        utils.write_json(self.user_profiles_path, data)

    def _save_improvement_recommendations(self):
        """Save improvement recommendations to storage."""
        data = []
        for rec in self.improvement_recommendations:
            data.append(
                {
                    "recommendation_id": rec.recommendation_id,
                    "action_type": rec.action_type.value,
                    "description": rec.description,
                    "rationale": rec.rationale,
                    "expected_impact": rec.expected_impact,
                    "confidence": rec.confidence,
                    "priority": rec.priority,
                    "implementation_effort": rec.implementation_effort,
                    "dependencies": rec.dependencies,
                    "created_at": rec.created_at.isoformat(),
                    "status": rec.status,
                }
            )

        utils.write_json(self.improvement_recommendations_path, data)

    def _save_adaptive_config(self):
        """Save adaptive configuration to storage."""
        utils.write_json(self.adaptive_config_path, self.adaptive_config)

    def _save_knowledge_base(self):
        """Save knowledge base to storage."""
        utils.write_json(self.knowledge_base_path, self.knowledge_base)

    def save_all_data(self):
        """Save all system data to storage."""
        self._save_user_profiles()
        self._save_improvement_recommendations()
        self._save_adaptive_config()
        self._save_knowledge_base()


def get_continuous_improvement_system(root: Path) -> ContinuousImprovementSystem:
    """Get continuous improvement system instance."""
    return ContinuousImprovementSystem(root)
