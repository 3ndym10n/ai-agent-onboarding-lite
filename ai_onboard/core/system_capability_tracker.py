"""
System Capability Usage Tracker (T21) - Track usage patterns of system capabilities.

This module provides comprehensive tracking of how different system capabilities
are being used, helping optimize system performance and user experience by
understanding usage patterns, identifying popular features, and detecting
underutilized capabilities.
"""

import json
import time
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .unified_metrics_collector import get_unified_metrics_collector


class CapabilityCategory(Enum):
    """Categories of system capabilities."""

    PROJECT_MANAGEMENT = "project_management"  # charter, plan, align, validate
    AI_COLLABORATION = "ai_collaboration"  # cursor, ai - agent, aaol, context
    OPTIMIZATION = "optimization"  # kaizen, experiments, metrics
    USER_EXPERIENCE = "user_experience"  # ux, help, suggestions, dashboard
    DEVELOPMENT_TOOLS = "development_tools"  # api, debug, cleanup, checkpoint
    ANALYTICS = "analytics"  # prompt, status, unified - metrics
    LEARNING = "learning"  # user - prefs, continuous - improvement
    ADVANCED_FEATURES = "advanced_features"  # decision - pipeline, enhanced - context


class UsageContext(Enum):
    """Context in which capabilities are used."""

    INTERACTIVE_CLI = "interactive_cli"  # Direct CLI usage
    API_INTEGRATION = "api_integration"  # Via API calls
    AUTOMATED_WORKFLOW = "automated_workflow"  # Automated / scripted usage
    BACKGROUND_PROCESS = "background_process"  # Background / daemon processes
    TESTING = "testing"  # During testing / validation
    ONBOARDING = "onboarding"  # During user onboarding
    TROUBLESHOOTING = "troubleshooting"  # During problem resolution


class UsagePattern(Enum):
    """Common usage patterns."""

    SINGLE_USE = "single_use"  # One - off command execution
    WORKFLOW_SEQUENCE = "workflow_sequence"  # Part of multi - step workflow
    REPEATED_USE = "repeated_use"  # Frequent repeated usage
    EXPLORATION = "exploration"  # Feature discovery / learning
    POWER_USER = "power_user"  # Advanced / expert usage
    AUTOMATION = "automation"  # Automated / scripted usage

@dataclass

class CapabilityUsageEvent:
    """A single capability usage event."""

    event_id: str
    capability_name: str
    category: CapabilityCategory
    user_id: str
    timestamp: datetime

    # Usage context
    context: UsageContext
    pattern: UsagePattern
    session_id: Optional[str] = None

    # Execution details
    success: bool = True
    duration_ms: float = 0.0
    parameters: Dict[str, Any] = field(default_factory=dict)
    output_size: int = 0
    error_details: Optional[str] = None

    # User context
    user_expertise: Optional[str] = None
    workflow_step: Optional[str] = None
    preceding_commands: List[str] = field(default_factory=list)

    # Performance metrics
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None

@dataclass

class CapabilityMetrics:
    """Metrics for a specific capability."""

    capability_name: str
    category: CapabilityCategory

    # Usage statistics
    total_uses: int = 0
    unique_users: int = 0
    success_rate: float = 0.0

    # Performance metrics
    avg_duration_ms: float = 0.0
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0

    # Usage patterns
    common_contexts: Dict[str, int] = field(default_factory=dict)
    common_patterns: Dict[str, int] = field(default_factory=dict)
    peak_usage_hours: Dict[int, int] = field(default_factory=dict)

    # Trends
    daily_usage: Dict[str, int] = field(default_factory=dict)
    weekly_growth: float = 0.0
    user_retention: float = 0.0

    # Quality metrics
    error_rate: float = 0.0
    common_errors: Dict[str, int] = field(default_factory=dict)
    user_satisfaction: float = 0.0

@dataclass

class SystemCapabilityReport:
    """Comprehensive system capability usage report."""

    report_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime

    # Overall statistics
    total_capability_uses: int
    unique_capabilities_used: int
    unique_users: int

    # Top capabilities
    most_used_capabilities: List[Dict[str, Any]]
    fastest_growing_capabilities: List[Dict[str, Any]]
    highest_satisfaction_capabilities: List[Dict[str, Any]]

    # Usage patterns
    common_workflows: List[Dict[str, Any]]
    peak_usage_times: Dict[str, int]
    user_behavior_patterns: Dict[str, Any]

    # Performance insights
    performance_leaders: List[Dict[str, Any]]
    performance_concerns: List[Dict[str, Any]]
    optimization_opportunities: List[Dict[str, Any]]

    # Recommendations
    feature_promotion_recommendations: List[str]
    optimization_recommendations: List[str]
    user_experience_improvements: List[str]


class CapabilityRegistry:
    """Registry of all system capabilities."""


    def __init__(self):
        self.capabilities = self._initialize_capabilities()


    def _initialize_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the registry of system capabilities."""
        return {
            # Project Management
            "charter": {
                "category": CapabilityCategory.PROJECT_MANAGEMENT,
                "description": "Create and manage project charters",
                "complexity": "medium",
                "user_level": "beginner",
            },
            "plan": {
                "category": CapabilityCategory.PROJECT_MANAGEMENT,
                "description": "Generate and manage project plans",
                "complexity": "high",
                "user_level": "beginner",
            },
            "align": {
                "category": CapabilityCategory.PROJECT_MANAGEMENT,
                "description": "Check project alignment with vision",
                "complexity": "medium",
                "user_level": "intermediate",
            },
            "validate": {
                "category": CapabilityCategory.PROJECT_MANAGEMENT,
                "description": "Validate project health and quality",
                "complexity": "medium",
                "user_level": "intermediate",
            },
            "dashboard": {
                "category": CapabilityCategory.PROJECT_MANAGEMENT,
                "description": "Visual project status dashboard",
                "complexity": "low",
                "user_level": "beginner",
            },
            # AI Collaboration
            "cursor": {
                "category": CapabilityCategory.AI_COLLABORATION,
                "description": "Cursor AI integration and workflows",
                "complexity": "high",
                "user_level": "intermediate",
            },
            "ai - agent": {
                "category": CapabilityCategory.AI_COLLABORATION,
                "description": "AI agent management and collaboration",
                "complexity": "high",
                "user_level": "advanced",
            },
            "aaol": {
                "category": CapabilityCategory.AI_COLLABORATION,
                "description": "AI Agent Orchestration Layer",
                "complexity": "very_high",
                "user_level": "expert",
            },
            "enhanced - context": {
                "category": CapabilityCategory.AI_COLLABORATION,
                "description": "Advanced conversation context management",
                "complexity": "high",
                "user_level": "advanced",
            },
            "decision - pipeline": {
                "category": CapabilityCategory.AI_COLLABORATION,
                "description": "Multi - stage decision processing",
                "complexity": "very_high",
                "user_level": "expert",
            },
            # Optimization
            "kaizen": {
                "category": CapabilityCategory.OPTIMIZATION,
                "description": "Continuous improvement cycles",
                "complexity": "medium",
                "user_level": "intermediate",
            },
            "kaizen - auto": {
                "category": CapabilityCategory.OPTIMIZATION,
                "description": "Automated Kaizen cycle management",
                "complexity": "high",
                "user_level": "advanced",
            },
            "opt - experiments": {
                "category": CapabilityCategory.OPTIMIZATION,
                "description": "Optimization experiment framework",
                "complexity": "high",
                "user_level": "advanced",
            },
            # User Experience
            "ux": {
                "category": CapabilityCategory.USER_EXPERIENCE,
                "description": "User experience enhancements and analytics",
                "complexity": "medium",
                "user_level": "intermediate",
            },
            "help": {
                "category": CapabilityCategory.USER_EXPERIENCE,
                "description": "Context - aware help system",
                "complexity": "low",
                "user_level": "beginner",
            },
            "suggest": {
                "category": CapabilityCategory.USER_EXPERIENCE,
                "description": "Personalized recommendations",
                "complexity": "medium",
                "user_level": "beginner",
            },
            "discover": {
                "category": CapabilityCategory.USER_EXPERIENCE,
                "description": "Feature discovery and exploration",
                "complexity": "low",
                "user_level": "beginner",
            },
            # Development Tools
            "api": {
                "category": CapabilityCategory.DEVELOPMENT_TOOLS,
                "description": "REST API server for integrations",
                "complexity": "high",
                "user_level": "advanced",
            },
            "debug": {
                "category": CapabilityCategory.DEVELOPMENT_TOOLS,
                "description": "Smart debugging and error analysis",
                "complexity": "medium",
                "user_level": "intermediate",
            },
            "cleanup": {
                "category": CapabilityCategory.DEVELOPMENT_TOOLS,
                "description": "Safe project cleanup",
                "complexity": "low",
                "user_level": "beginner",
            },
            "checkpoint": {
                "category": CapabilityCategory.DEVELOPMENT_TOOLS,
                "description": "Project state management",
                "complexity": "medium",
                "user_level": "intermediate",
            },
            # Analytics
            "prompt": {
                "category": CapabilityCategory.ANALYTICS,
                "description": "State summaries and AI context",
                "complexity": "low",
                "user_level": "beginner",
            },
            "status": {
                "category": CapabilityCategory.ANALYTICS,
                "description": "System health and status",
                "complexity": "low",
                "user_level": "beginner",
            },
            "unified - metrics": {
                "category": CapabilityCategory.ANALYTICS,
                "description": "Comprehensive metrics collection",
                "complexity": "high",
                "user_level": "advanced",
            },
            # Learning
            "user - prefs": {
                "category": CapabilityCategory.LEARNING,
                "description": "User preference learning system",
                "complexity": "medium",
                "user_level": "intermediate",
            },
            "continuous - improvement": {
                "category": CapabilityCategory.LEARNING,
                "description": "Continuous improvement automation",
                "complexity": "high",
                "user_level": "advanced",
            },
        }


    def get_capability_info(self, capability_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a capability."""
        return self.capabilities.get(capability_name)


    def get_capabilities_by_category(self, category: CapabilityCategory) -> List[str]:
        """Get all capabilities in a specific category."""
        return [
            name
            for name, info in self.capabilities.items()
            if info["category"] == category
        ]


    def get_capabilities_by_user_level(self, user_level: str) -> List[str]:
        """Get capabilities appropriate for a user level."""
        return [
            name
            for name, info in self.capabilities.items()
            if info["user_level"] == user_level
        ]


class SystemCapabilityTracker:
    """Main system capability usage tracker."""


    def __init__(self, root: Path):
        self.root = root
        self.data_dir = root / ".ai_onboard" / "capability_tracking"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Components
        self.registry = CapabilityRegistry()
        self.metrics_collector = get_unified_metrics_collector(root)

        # Storage
        self.usage_log_file = self.data_dir / "usage_log.jsonl"
        self.metrics_file = self.data_dir / "capability_metrics.json"
        self.reports_dir = self.data_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)

        # In - memory caches
        self.capability_metrics: Dict[str, CapabilityMetrics] = {}
        self.recent_events: List[CapabilityUsageEvent] = []
        self.session_tracking: Dict[str, List[str]] = defaultdict(list)

        # Configuration
        self.config = self._load_config()

        # Initialize
        self._load_existing_metrics()


    def _load_config(self) -> Dict[str, Any]:
        """Load capability tracking configuration."""
        config_file = self.data_dir / "config.json"

        default_config = {
            "tracking_enabled": True,
            "detailed_tracking": True,
            "performance_tracking": True,
            "max_events_in_memory": 1000,
            "metrics_update_interval": 300,  # 5 minutes
            "report_generation_interval": 86400,  # 24 hours
            "retention_days": 90,
            "privacy_mode": False,
            "excluded_capabilities": [],
            "user_anonymization": False,
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


    def _load_existing_metrics(self):
        """Load existing capability metrics from storage."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, "r") as f:
                    metrics_data = json.load(f)

                for capability_name, data in metrics_data.items():
                    # Convert dict back to CapabilityMetrics
                    metrics = CapabilityMetrics(
                        capability_name=data["capability_name"],
                        category=CapabilityCategory(data["category"]),
                        total_uses=data.get("total_uses", 0),
                        unique_users=data.get("unique_users", 0),
                        success_rate=data.get("success_rate", 0.0),
                        avg_duration_ms=data.get("avg_duration_ms", 0.0),
                        min_duration_ms=data.get("min_duration_ms", float("inf")),
                        max_duration_ms=data.get("max_duration_ms", 0.0),
                        common_contexts=data.get("common_contexts", {}),
                        common_patterns=data.get("common_patterns", {}),
                        peak_usage_hours=data.get("peak_usage_hours", {}),
                        daily_usage=data.get("daily_usage", {}),
                        weekly_growth=data.get("weekly_growth", 0.0),
                        user_retention=data.get("user_retention", 0.0),
                        error_rate=data.get("error_rate", 0.0),
                        common_errors=data.get("common_errors", {}),
                        user_satisfaction=data.get("user_satisfaction", 0.0),
                    )
                    self.capability_metrics[capability_name] = metrics

            except Exception as e:
                print(f"Warning: Failed to load existing metrics: {e}")


    def record_capability_usage(
        self,
        capability_name: str,
        user_id: str,
        context: UsageContext = UsageContext.INTERACTIVE_CLI,
        pattern: UsagePattern = UsagePattern.SINGLE_USE,
        success: bool = True,
        duration_ms: float = 0.0,
        parameters: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        error_details: Optional[str] = None,
        **kwargs,
    ) -> CapabilityUsageEvent:
        """Record a capability usage event."""

        if not self.config.get("tracking_enabled", True):
            return None

        if capability_name in self.config.get("excluded_capabilities", []):
            return None

        # Get capability info
        capability_info = self.registry.get_capability_info(capability_name)
        if not capability_info:
            # Unknown capability, add to registry with defaults
            category = CapabilityCategory.ADVANCED_FEATURES
        else:
            category = capability_info["category"]

        # Create usage event
        event = CapabilityUsageEvent(
            event_id=f"cap_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            capability_name=capability_name,
            category=category,
            user_id=(
                user_id
                if not self.config.get("user_anonymization", False)
                else f"user_{hash(user_id) % 10000}"
            ),
            timestamp=datetime.now(),
            context=context,
            pattern=pattern,
            session_id=session_id,
            success=success,
            duration_ms=duration_ms,
            parameters=parameters or {},
            error_details=error_details,
            **kwargs,
        )

        # Store event
        self._store_usage_event(event)

        # Update in - memory tracking
        self.recent_events.append(event)
        if len(self.recent_events) > self.config.get("max_events_in_memory", 1000):
            self.recent_events = self.recent_events[
                -self.config.get("max_events_in_memory", 1000) :
            ]

        # Update session tracking
        if session_id:
            self.session_tracking[session_id].append(capability_name)

        # Update metrics
        self._update_capability_metrics(event)

        # Record in unified metrics system
        try:
            # Note: Assuming the metrics collector has a record method
            pass  # Implementation depends on actual metrics collector interface
        except Exception:
            pass

        return event


    def _store_usage_event(self, event: CapabilityUsageEvent):
        """Store usage event to persistent storage."""
        try:
            event_data = {
                "event_id": event.event_id,
                "capability_name": event.capability_name,
                "category": event.category.value,
                "user_id": event.user_id,
                "timestamp": event.timestamp.isoformat(),
                "context": event.context.value,
                "pattern": event.pattern.value,
                "session_id": event.session_id,
                "success": event.success,
                "duration_ms": event.duration_ms,
                "parameters": event.parameters,
                "output_size": event.output_size,
                "error_details": event.error_details,
                "user_expertise": event.user_expertise,
                "workflow_step": event.workflow_step,
                "preceding_commands": event.preceding_commands,
                "memory_usage_mb": event.memory_usage_mb,
                "cpu_usage_percent": event.cpu_usage_percent,
            }

            with open(self.usage_log_file, "a") as f:
                f.write(json.dumps(event_data) + "\n")

        except Exception as e:
            print(f"Warning: Failed to store usage event: {e}")


    def _update_capability_metrics(self, event: CapabilityUsageEvent):
        """Update capability metrics based on usage event."""
        capability_name = event.capability_name

        if capability_name not in self.capability_metrics:
            self.capability_metrics[capability_name] = CapabilityMetrics(
                capability_name=capability_name, category=event.category
            )

        metrics = self.capability_metrics[capability_name]

        # Update usage statistics
        metrics.total_uses += 1

        # Update performance metrics
        if event.duration_ms > 0:
            if metrics.avg_duration_ms == 0:
                metrics.avg_duration_ms = event.duration_ms
            else:
                # Running average
                metrics.avg_duration_ms = (
                    metrics.avg_duration_ms * (metrics.total_uses - 1)
                    + event.duration_ms
                ) / metrics.total_uses

            metrics.min_duration_ms = min(metrics.min_duration_ms, event.duration_ms)
            metrics.max_duration_ms = max(metrics.max_duration_ms, event.duration_ms)

        # Update usage patterns
        context_key = event.context.value
        metrics.common_contexts[context_key] = (
            metrics.common_contexts.get(context_key, 0) + 1
        )

        pattern_key = event.pattern.value
        metrics.common_patterns[pattern_key] = (
            metrics.common_patterns.get(pattern_key, 0) + 1
        )

        # Update peak usage hours
        hour = event.timestamp.hour
        metrics.peak_usage_hours[hour] = metrics.peak_usage_hours.get(hour, 0) + 1

        # Update daily usage
        date_key = event.timestamp.date().isoformat()
        metrics.daily_usage[date_key] = metrics.daily_usage.get(date_key, 0) + 1

        # Update success rate
        if event.success:
            success_count = int(metrics.success_rate * (metrics.total_uses - 1)) + 1
        else:
            success_count = int(metrics.success_rate * (metrics.total_uses - 1))

            # Track errors
            if event.error_details:
                error_key = type(
                    Exception()
                ).__name__  # Simplified error classification
                metrics.common_errors[error_key] = (
                    metrics.common_errors.get(error_key, 0) + 1
                )

        metrics.success_rate = success_count / metrics.total_uses
        metrics.error_rate = 1.0 - metrics.success_rate


    def get_capability_metrics(
        self, capability_name: str
    ) -> Optional[CapabilityMetrics]:
        """Get metrics for a specific capability."""
        return self.capability_metrics.get(capability_name)


    def get_category_metrics(
        self, category: CapabilityCategory
    ) -> Dict[str, CapabilityMetrics]:
        """Get metrics for all capabilities in a category."""
        return {
            name: metrics
            for name, metrics in self.capability_metrics.items()
            if metrics.category == category
        }


    def get_usage_trends(self, capability_name: str, days: int = 30) -> Dict[str, Any]:
        """Get usage trends for a capability over time."""
        metrics = self.capability_metrics.get(capability_name)
        if not metrics:
            return {}

        # Calculate trends from daily usage data
        cutoff_date = (datetime.now() - timedelta(days=days)).date()
        recent_usage = {
            date: count
            for date, count in metrics.daily_usage.items()
            if datetime.fromisoformat(date).date() >= cutoff_date
        }

        if not recent_usage:
            return {"trend": "no_data", "recent_usage": {}}

        # Calculate growth trend
        dates = sorted(recent_usage.keys())
        if len(dates) >= 7:
            recent_week = sum(recent_usage[date] for date in dates[-7:])
            previous_week = (
                sum(recent_usage[date] for date in dates[-14:-7])
                if len(dates) >= 14
                else recent_week
            )

            if previous_week > 0:
                growth_rate = (recent_week - previous_week) / previous_week
            else:
                growth_rate = 1.0 if recent_week > 0 else 0.0
        else:
            growth_rate = 0.0

        return {
            "trend": (
                "growing"
                if growth_rate > 0.1
                else "declining" if growth_rate < -0.1 else "stable"
            ),
            "growth_rate": growth_rate,
            "recent_usage": recent_usage,
            "total_recent_uses": sum(recent_usage.values()),
            "avg_daily_uses": (
                sum(recent_usage.values()) / len(recent_usage) if recent_usage else 0
            ),
        }


    def get_user_capability_profile(self, user_id: str) -> Dict[str, Any]:
        """Get capability usage profile for a specific user."""
        # Load recent events for user
        user_events = []

        if self.usage_log_file.exists():
            try:
                with open(self.usage_log_file, "r") as f:
                    for line in f:
                        try:
                            event_data = json.loads(line.strip())
                            if event_data.get("user_id") == user_id:
                                user_events.append(event_data)
                        except json.JSONDecodeError:
                            continue
            except Exception:
                pass

        if not user_events:
            return {"user_id": user_id, "capabilities_used": [], "usage_patterns": {}}

        # Analyze user patterns
        capabilities_used = Counter(event["capability_name"] for event in user_events)
        contexts_used = Counter(event["context"] for event in user_events)
        patterns_used = Counter(event["pattern"] for event in user_events)
        categories_used = Counter(event["category"] for event in user_events)

        # Calculate user expertise indicators
        total_uses = len(user_events)
        unique_capabilities = len(capabilities_used)
        advanced_usage = sum(
            1
            for event in user_events
            if event.get("pattern") in ["power_user", "automation"]
        )

        # Determine user level
        if unique_capabilities >= 15 and advanced_usage / total_uses > 0.3:
            user_level = "expert"
        elif unique_capabilities >= 10 and advanced_usage / total_uses > 0.2:
            user_level = "advanced"
        elif unique_capabilities >= 5:
            user_level = "intermediate"
        else:
            user_level = "beginner"

        return {
            "user_id": user_id,
            "user_level": user_level,
            "total_capability_uses": total_uses,
            "unique_capabilities_used": unique_capabilities,
            "capabilities_used": dict(capabilities_used.most_common(10)),
            "favorite_contexts": dict(contexts_used.most_common(5)),
            "usage_patterns": dict(patterns_used.most_common(5)),
            "category_preferences": dict(categories_used.most_common()),
            "advanced_usage_rate": advanced_usage / total_uses if total_uses > 0 else 0,
            "recent_activity": len(
                [
                    e
                    for e in user_events
                    if datetime.fromisoformat(e["timestamp"])
                    >= datetime.now() - timedelta(days=7)
                ]
            ),
        }


    def generate_system_report(self, days: int = 30) -> SystemCapabilityReport:
        """Generate comprehensive system capability usage report."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Collect statistics
        total_uses = sum(
            metrics.total_uses for metrics in self.capability_metrics.values()
        )
        unique_capabilities = len(self.capability_metrics)

        # Get unique users from recent events
        unique_users = set()
        if self.usage_log_file.exists():
            try:
                with open(self.usage_log_file, "r") as f:
                    for line in f:
                        try:
                            event_data = json.loads(line.strip())
                            event_time = datetime.fromisoformat(event_data["timestamp"])
                            if event_time >= start_date:
                                unique_users.add(event_data["user_id"])
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
            except Exception:
                pass

        # Most used capabilities
        most_used = sorted(
            [
                (name, metrics.total_uses)
                for name, metrics in self.capability_metrics.items()
            ],
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        # Fastest growing capabilities
        growing_caps = []
        for name, metrics in self.capability_metrics.items():
            trends = self.get_usage_trends(name, days)
            if trends.get("growth_rate", 0) > 0:
                growing_caps.append((name, trends["growth_rate"]))
        growing_caps.sort(key=lambda x: x[1], reverse=True)

        # Highest satisfaction (placeholder - would integrate with UX system)
        satisfaction_caps: list[str] = []

        # Common workflows (analyze command sequences)
        common_workflows = self._analyze_common_workflows()

        # Peak usage times
        peak_times: defaultdict[int, int] = defaultdict(int)
        for metrics in self.capability_metrics.values():
            for hour, count in metrics.peak_usage_hours.items():
                peak_times[hour] += count

        # Generate recommendations
        feature_recommendations = self._generate_feature_recommendations()
        optimization_recommendations = self._generate_optimization_recommendations()
        ux_recommendations = self._generate_ux_recommendations()

        report = SystemCapabilityReport(
            report_id=f"cap_report_{int(time.time())}",
            generated_at=end_date,
            period_start=start_date,
            period_end=end_date,
            total_capability_uses=total_uses,
            unique_capabilities_used=unique_capabilities,
            unique_users=len(unique_users),
            most_used_capabilities=[
                {"name": name, "uses": uses} for name, uses in most_used
            ],
            fastest_growing_capabilities=[
                {"name": name, "growth_rate": rate} for name, rate in growing_caps[:5]
            ],
            highest_satisfaction_capabilities=satisfaction_caps,
            common_workflows=common_workflows,
            peak_usage_times=dict(peak_times),
            user_behavior_patterns=self._analyze_user_behavior_patterns(),
            performance_leaders=self._get_performance_leaders(),
            performance_concerns=self._get_performance_concerns(),
            optimization_opportunities=self._get_optimization_opportunities(),
            feature_promotion_recommendations=feature_recommendations,
            optimization_recommendations=optimization_recommendations,
            user_experience_improvements=ux_recommendations,
        )

        # Save report
        report_file = (
            self.reports_dir
            / f"capability_report_{end_date.strftime('%Y % m % d_ % H % M % S')}.json"
        )
        try:
            with open(report_file, "w") as f:
                json.dump(self._serialize_report(report), f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save report: {e}")

        return report


    def _analyze_common_workflows(self) -> List[Dict[str, Any]]:
        """Analyze common command sequences to identify workflows."""
        workflows = []

        # Analyze session tracking data
        for session_id, commands in self.session_tracking.items():
            if len(commands) >= 3:  # Workflows with at least 3 commands
                workflow_pattern = " -> ".join(commands[:5])  # First 5 commands
                workflows.append(
                    {
                        "pattern": workflow_pattern,
                        "frequency": 1,
                        "avg_length": len(commands),
                        "commands": commands,
                    }
                )

        # Group similar workflows
        workflow_groups = defaultdict(list)
        for workflow in workflows:
            # Simple grouping by first 2 commands
            key = " -> ".join(workflow["pattern"].split(" -> ")[:2])
            workflow_groups[key].append(workflow)

        # Aggregate and sort
        common_workflows = []
        for pattern, group in workflow_groups.items():
            if len(group) >= 2:  # At least 2 occurrences
                common_workflows.append(
                    {
                        "pattern": pattern,
                        "frequency": len(group),
                        "avg_length": sum(w["avg_length"] for w in group) / len(group),
                        "variations": len(set(w["pattern"] for w in group)),
                    }
                )

        return sorted(common_workflows, key=lambda x: x["frequency"], reverse=True)[:10]


    def _analyze_user_behavior_patterns(self) -> Dict[str, Any]:
        """Analyze overall user behavior patterns."""
        patterns = {
            "exploration_users": 0,
            "power_users": 0,
            "workflow_users": 0,
            "casual_users": 0,
        }

        # This would analyze user profiles to categorize behavior patterns
        # Simplified implementation
        return patterns


    def _get_performance_leaders(self) -> List[Dict[str, Any]]:
        """Get capabilities with best performance metrics."""
        leaders = []

        for name, metrics in self.capability_metrics.items():
            if metrics.total_uses >= 10:  # Minimum usage for consideration
                leaders.append(
                    {
                        "capability": name,
                        "avg_duration_ms": metrics.avg_duration_ms,
                        "success_rate": metrics.success_rate,
                        "performance_score": metrics.success_rate
                        * (1000 / max(metrics.avg_duration_ms, 1)),
                    }
                )

        return sorted(leaders, key=lambda x: x["performance_score"], reverse=True)[:5]


    def _get_performance_concerns(self) -> List[Dict[str, Any]]:
        """Get capabilities with performance concerns."""
        concerns = []

        for name, metrics in self.capability_metrics.items():
            if metrics.total_uses >= 5:  # Minimum usage for consideration
                if metrics.avg_duration_ms > 5000 or metrics.success_rate < 0.8:
                    concerns.append(
                        {
                            "capability": name,
                            "avg_duration_ms": metrics.avg_duration_ms,
                            "success_rate": metrics.success_rate,
                            "error_rate": metrics.error_rate,
                            "concerns": [],
                        }
                    )

                    if metrics.avg_duration_ms > 5000:
                        concerns[-1]["concerns"].append("slow_performance")
                    if metrics.success_rate < 0.8:
                        concerns[-1]["concerns"].append("low_success_rate")

        return sorted(concerns, key=lambda x: len(x["concerns"]), reverse=True)


    def _get_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Identify optimization opportunities."""
        opportunities: list[dict[str, Any]] = []

        # Underutilized capabilities
        if len(self.capability_metrics) == 0:
            return opportunities

        total_avg_usage = sum(
            m.total_uses for m in self.capability_metrics.values()
        ) / len(self.capability_metrics)

        for name, metrics in self.capability_metrics.items():
            capability_info = self.registry.get_capability_info(name)
            if capability_info and metrics.total_uses < total_avg_usage * 0.3:
                opportunities.append(
                    {
                        "type": "underutilized_capability",
                        "capability": name,
                        "current_usage": metrics.total_uses,
                        "potential": (
                            "high"
                            if capability_info["user_level"] == "beginner"
                            else "medium"
                        ),
                    }
                )

        return opportunities


    def _generate_feature_recommendations(self) -> List[str]:
        """Generate feature promotion recommendations."""
        recommendations = []

        # Find underutilized beginner - friendly features
        for name, metrics in self.capability_metrics.items():
            capability_info = self.registry.get_capability_info(name)
            if (
                capability_info
                and capability_info["user_level"] == "beginner"
                and metrics.total_uses < 50
            ):
                recommendations.append(
                    f"Promote '{name}' feature to new users - highly useful but underutilized"
                )

        return recommendations[:5]


    def _generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []

        # Performance optimization recommendations
        for name, metrics in self.capability_metrics.items():
            if metrics.avg_duration_ms > 3000 and metrics.total_uses > 20:
                recommendations.append(
                    f"Optimize '{name}' performance - average duration {metrics.avg_duration_ms:.0f}ms"
                )

        return recommendations[:5]


    def _generate_ux_recommendations(self) -> List[str]:
        """Generate UX improvement recommendations."""
        recommendations = []

        # Error rate improvements
        for name, metrics in self.capability_metrics.items():
            if metrics.error_rate > 0.1 and metrics.total_uses > 10:
                recommendations.append(
                    f"Improve '{name}' error handling - {metrics.error_rate:.1%} error rate"
                )

        return recommendations[:5]


    def _serialize_report(self, report: SystemCapabilityReport) -> Dict[str, Any]:
        """Serialize report for JSON storage."""
        return {
            "report_id": report.report_id,
            "generated_at": report.generated_at.isoformat(),
            "period_start": report.period_start.isoformat(),
            "period_end": report.period_end.isoformat(),
            "total_capability_uses": report.total_capability_uses,
            "unique_capabilities_used": report.unique_capabilities_used,
            "unique_users": report.unique_users,
            "most_used_capabilities": report.most_used_capabilities,
            "fastest_growing_capabilities": report.fastest_growing_capabilities,
            "highest_satisfaction_capabilities": report.highest_satisfaction_capabilities,
            "common_workflows": report.common_workflows,
            "peak_usage_times": report.peak_usage_times,
            "user_behavior_patterns": report.user_behavior_patterns,
            "performance_leaders": report.performance_leaders,
            "performance_concerns": report.performance_concerns,
            "optimization_opportunities": report.optimization_opportunities,
            "feature_promotion_recommendations": report.feature_promotion_recommendations,
            "optimization_recommendations": report.optimization_recommendations,
            "user_experience_improvements": report.user_experience_improvements,
        }


    def save_metrics(self):
        """Save capability metrics to persistent storage."""
        try:
            metrics_data = {}
            for name, metrics in self.capability_metrics.items():
                metrics_data[name] = {
                    "capability_name": metrics.capability_name,
                    "category": metrics.category.value,
                    "total_uses": metrics.total_uses,
                    "unique_users": metrics.unique_users,
                    "success_rate": metrics.success_rate,
                    "avg_duration_ms": metrics.avg_duration_ms,
                    "min_duration_ms": (
                        metrics.min_duration_ms
                        if metrics.min_duration_ms != float("inf")
                        else 0
                    ),
                    "max_duration_ms": metrics.max_duration_ms,
                    "common_contexts": metrics.common_contexts,
                    "common_patterns": metrics.common_patterns,
                    "peak_usage_hours": metrics.peak_usage_hours,
                    "daily_usage": metrics.daily_usage,
                    "weekly_growth": metrics.weekly_growth,
                    "user_retention": metrics.user_retention,
                    "error_rate": metrics.error_rate,
                    "common_errors": metrics.common_errors,
                    "user_satisfaction": metrics.user_satisfaction,
                }

            with open(self.metrics_file, "w") as f:
                json.dump(metrics_data, f, indent=2)

        except Exception as e:
            print(f"Warning: Failed to save metrics: {e}")

# Global instance
_capability_tracker: Optional[SystemCapabilityTracker] = None


def get_system_capability_tracker(root: Path) -> SystemCapabilityTracker:
    """Get the global system capability tracker."""
    global _capability_tracker
    if _capability_tracker is None:
        _capability_tracker = SystemCapabilityTracker(root)
    return _capability_tracker


def track_capability_usage(
    capability_name: str,
    user_id: str = "default",
    context: UsageContext = UsageContext.INTERACTIVE_CLI,
    pattern: UsagePattern = UsagePattern.SINGLE_USE,
    success: bool = True,
    duration_ms: float = 0.0,
    **kwargs,
):
    """Convenience function to track capability usage."""
    from pathlib import Path

    try:
        root = Path.cwd()
        tracker = get_system_capability_tracker(root)
        return tracker.record_capability_usage(
            capability_name=capability_name,
            user_id=user_id,
            context=context,
            pattern=pattern,
            success=success,
            duration_ms=duration_ms,
            **kwargs,
        )
    except Exception:
        # Fail silently to avoid disrupting main functionality
        return None
