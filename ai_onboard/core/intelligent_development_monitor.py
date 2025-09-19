"""
Intelligent Development Monitor

Proactively monitors development activities and automatically applies appropriate tools
based on detected patterns, changes, and development context.
"""

import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .intelligent_tool_orchestrator import IntelligentToolOrchestrator
from .tool_usage_tracker import get_tool_tracker


@dataclass
class DevelopmentActivity:
    """Represents a detected development activity."""

    activity_type: (
        str  # 'file_change', 'git_commit', 'test_run', 'build', 'conversation'
    )
    timestamp: float
    details: Dict[str, Any]
    confidence: float
    triggered_tools: List[str] = field(default_factory=list)


@dataclass
class ProactiveTriggerRule:
    """Rules for automatically triggering tool application."""

    rule_name: str
    activity_pattern: str
    context_conditions: Dict[str, Any]
    required_tools: List[str]
    confidence_threshold: float
    cooldown_seconds: int
    last_triggered: Optional[float] = None


class IntelligentDevelopmentMonitor:
    """
    Monitors development activities and proactively applies tools.

    This system runs continuously and automatically applies development tools
    based on detected activities, context, and patterns.
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.tool_orchestrator = IntelligentToolOrchestrator(root_path)
        self.tool_tracker = get_tool_tracker(root_path)

        # Activity monitoring
        self.activity_history: List[DevelopmentActivity] = []
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Proactive trigger rules
        self.trigger_rules = self._initialize_trigger_rules()

        # Callbacks for different activity types
        self.activity_callbacks: Dict[str, List[Callable]] = {
            "file_change": [],
            "git_operation": [],
            "test_execution": [],
            "build_process": [],
            "conversation": [],
            "command_execution": [],
        }

    def _initialize_trigger_rules(self) -> List[ProactiveTriggerRule]:
        """Initialize proactive trigger rules."""

        return [
            # Code Quality Triggers
            ProactiveTriggerRule(
                rule_name="code_quality_after_changes",
                activity_pattern="file_change",
                context_conditions={
                    "file_types": [".py"],
                    "change_types": ["modify", "create"],
                    "min_changes": 5,
                },
                required_tools=["code_quality_analysis"],
                confidence_threshold=0.8,
                cooldown_seconds=300,  # 5 minutes
            ),
            # Organization Triggers
            ProactiveTriggerRule(
                rule_name="organization_check_new_files",
                activity_pattern="file_change",
                context_conditions={
                    "file_types": ["any"],
                    "change_types": ["create"],
                    "min_files": 3,
                },
                required_tools=["organization_analysis"],
                confidence_threshold=0.7,
                cooldown_seconds=600,  # 10 minutes
            ),
            # Risk Assessment Triggers
            ProactiveTriggerRule(
                rule_name="risk_before_commit",
                activity_pattern="git_operation",
                context_conditions={"operation": "commit", "staged_changes": True},
                required_tools=["risk_assessment"],
                confidence_threshold=0.9,
                cooldown_seconds=60,  # 1 minute
            ),
            # Test Failure Triggers
            ProactiveTriggerRule(
                rule_name="analysis_after_test_failure",
                activity_pattern="test_execution",
                context_conditions={"result": "failed", "failure_rate": ">0.1"},
                required_tools=["code_quality_analysis", "dependency_analysis"],
                confidence_threshold=0.8,
                cooldown_seconds=120,  # 2 minutes
            ),
            # Conversation-Based Triggers
            ProactiveTriggerRule(
                rule_name="comprehensive_analysis_request",
                activity_pattern="conversation",
                context_conditions={
                    "keywords": ["analyze", "review", "check", "quality"],
                    "confidence": ">0.7",
                },
                required_tools=[
                    "code_quality_analysis",
                    "organization_analysis",
                    "risk_assessment",
                ],
                confidence_threshold=0.8,
                cooldown_seconds=1800,  # 30 minutes
            ),
        ]

    def start_monitoring(self):
        """Start the intelligent development monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        print("🧠 Intelligent Development Monitor started")
        print("   📊 Monitoring for automatic tool application...")

    def stop_monitoring(self):
        """Stop the intelligent development monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        print("🧠 Intelligent Development Monitor stopped")

    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Check for new activities
                activities = self._detect_activities()

                for activity in activities:
                    self._process_activity(activity)

                # Clean up old activities (keep last 24 hours)
                cutoff_time = time.time() - (24 * 3600)
                self.activity_history = [
                    act for act in self.activity_history if act.timestamp > cutoff_time
                ]

            except Exception as e:
                print(f"⚠️ Development monitor error: {e}")

            # Check every 30 seconds
            time.sleep(30)

    def _detect_activities(self) -> List[DevelopmentActivity]:
        """Detect new development activities."""
        activities = []

        # Check for file changes
        file_activities = self._detect_file_changes()
        activities.extend(file_activities)

        # Check for git operations
        git_activities = self._detect_git_operations()
        activities.extend(git_activities)

        # Check for test executions
        test_activities = self._detect_test_activities()
        activities.extend(test_activities)

        return activities

    def _detect_file_changes(self) -> List[DevelopmentActivity]:
        """Detect recent file changes."""
        # This would integrate with file system monitoring
        # For now, return empty list as we need to implement file watching
        return []

    def _detect_git_operations(self) -> List[DevelopmentActivity]:
        """Detect git operations."""
        # This would check git status, recent commits, etc.
        return []

    def _detect_test_activities(self) -> List[DevelopmentActivity]:
        """Detect test execution activities."""
        # This would monitor test execution
        return []

    def _process_activity(self, activity: DevelopmentActivity):
        """Process a detected activity and apply tools if triggered."""

        # Add to history
        self.activity_history.append(activity)

        # Check trigger rules
        triggered_rules = []
        for rule in self.trigger_rules:
            if self._rule_matches_activity(rule, activity):
                triggered_rules.append(rule)

        # Apply triggered tools
        for rule in triggered_rules:
            if self._should_trigger_rule(rule):
                self._execute_trigger_rule(rule, activity)
                rule.last_triggered = time.time()

        # Notify callbacks
        for callback in self.activity_callbacks.get(activity.activity_type, []):
            try:
                callback(activity)
            except Exception as e:
                print(f"⚠️ Activity callback error: {e}")

    def _rule_matches_activity(
        self, rule: ProactiveTriggerRule, activity: DevelopmentActivity
    ) -> bool:
        """Check if a rule matches an activity."""

        # Check activity pattern
        if activity.activity_type != rule.activity_pattern:
            return False

        # Check context conditions
        for condition_key, condition_value in rule.context_conditions.items():
            activity_value = activity.details.get(condition_key)

            if condition_key == "file_types":
                if isinstance(condition_value, list) and "any" not in condition_value:
                    if activity_value not in condition_value:
                        return False

            elif condition_key == "change_types":
                if activity_value not in condition_value:
                    return False

            elif condition_key == "min_changes":
                if activity_value < condition_value:
                    return False

            elif condition_key == "min_files":
                if activity_value < condition_value:
                    return False

            elif condition_key.startswith(">"):
                threshold = float(condition_key[1:])
                if activity_value <= threshold:
                    return False

        return True

    def _should_trigger_rule(self, rule: ProactiveTriggerRule) -> bool:
        """Check if a rule should be triggered based on cooldown."""

        if rule.last_triggered is None:
            return True

        time_since_last = time.time() - rule.last_triggered
        return time_since_last >= rule.cooldown_seconds

    def _execute_trigger_rule(
        self, rule: ProactiveTriggerRule, activity: DevelopmentActivity
    ):
        """Execute a triggered rule by applying the required tools."""

        print(
            f"🚀 AUTO-TRIGGER: {rule.rule_name} activated by {activity.activity_type}"
        )

        for tool_name in rule.required_tools:
            print(f"🤖 Applying {tool_name}...")

            # Create context for tool application
            tool_context = {
                "trigger_rule": rule.rule_name,
                "activity_type": activity.activity_type,
                "activity_details": activity.details,
                "confidence": rule.confidence_threshold,
            }

            # Execute the tool
            result = self.tool_orchestrator.execute_automatic_tool_application(
                tool_name, tool_context
            )

            if result["executed"]:
                activity.triggered_tools.append(tool_name)
                print(f"✅ {tool_name} completed successfully")

                # Track the proactive tool usage
                self.tool_tracker.track_tool_usage(
                    tool_name=f"proactive_{tool_name}",
                    tool_type="automatic_monitoring",
                    parameters={
                        "trigger_rule": rule.rule_name,
                        "activity_type": activity.activity_type,
                        "confidence": rule.confidence_threshold,
                    },
                    result="completed",
                )
            else:
                print(f"❌ {tool_name} failed: {result.get('error', 'Unknown error')}")

    def register_activity_callback(self, activity_type: str, callback: Callable):
        """Register a callback for specific activity types."""
        if activity_type in self.activity_callbacks:
            self.activity_callbacks[activity_type].append(callback)

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        return {
            "monitoring_active": self.monitoring_active,
            "activities_detected": len(self.activity_history),
            "rules_active": len(self.trigger_rules),
            "recent_activities": [
                {
                    "type": act.activity_type,
                    "timestamp": act.timestamp,
                    "tools_triggered": act.triggered_tools,
                }
                for act in self.activity_history[-10:]  # Last 10 activities
            ],
        }

    def manually_trigger_analysis(
        self, analysis_type: str, context: Dict[str, Any] = None
    ):
        """Manually trigger a specific type of analysis."""
        if context is None:
            context = {}

        context.update({"manual_trigger": True, "analysis_type": analysis_type})

        print(f"🔍 Manually triggering {analysis_type} analysis...")

        if analysis_type == "code_quality":
            result = self.tool_orchestrator.execute_automatic_tool_application(
                "code_quality_analysis", context
            )
        elif analysis_type == "organization":
            result = self.tool_orchestrator.execute_automatic_tool_application(
                "organization_analysis", context
            )
        elif analysis_type == "risk":
            result = self.tool_orchestrator.execute_automatic_tool_application(
                "risk_assessment", context
            )
        elif analysis_type == "comprehensive":
            # Run all tools
            tools = [
                "code_quality_analysis",
                "organization_analysis",
                "risk_assessment",
            ]
            for tool in tools:
                result = self.tool_orchestrator.execute_automatic_tool_application(
                    tool, context
                )
                if result["executed"]:
                    print(f"✅ {tool} completed")
                else:
                    print(f"❌ {tool} failed")

        print("🔍 Manual analysis trigger completed")


# Global monitor instance
_monitor_instance: Optional[IntelligentDevelopmentMonitor] = None


def get_development_monitor(root_path: Path) -> IntelligentDevelopmentMonitor:
    """Get the global development monitor instance."""
    global _monitor_instance
    if _monitor_instance is None or _monitor_instance.root_path != root_path:
        _monitor_instance = IntelligentDevelopmentMonitor(root_path)
    return _monitor_instance


def start_intelligent_monitoring(root_path: Path):
    """Start intelligent development monitoring."""
    monitor = get_development_monitor(root_path)
    monitor.start_monitoring()


def stop_intelligent_monitoring():
    """Stop intelligent development monitoring."""
    global _monitor_instance
    if _monitor_instance:
        _monitor_instance.stop_monitoring()
        _monitor_instance = None
