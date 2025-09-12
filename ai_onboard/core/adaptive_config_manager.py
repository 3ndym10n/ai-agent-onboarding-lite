"""
Adaptive Configuration Manager - Intelligent configuration adaptation system.

This module provides adaptive configuration management that:
- Learns from user preferences and system performance
- Automatically adjusts configuration based on usage patterns
- Adapts to different project types and user workflows
- Provides configuration recommendations and optimizations
- Maintains configuration history and rollback capabilities
"""

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import continuous_improvement_system, utils


class ConfigurationCategory(Enum):
    """Categories of configuration settings."""

    SYSTEM_PERFORMANCE = "system_performance"
    USER_INTERFACE = "user_interface"
    AI_AGENT_BEHAVIOR = "ai_agent_behavior"
    SAFETY_AND_SECURITY = "safety_and_security"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    PROJECT_SPECIFIC = "project_specific"


class AdaptationTrigger(Enum):
    """Triggers for configuration adaptation."""

    USER_PREFERENCE_CHANGE = "user_preference_change"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    PROJECT_TYPE_CHANGE = "project_type_change"
    USAGE_PATTERN_CHANGE = "usage_pattern_change"
    ERROR_PATTERN_DETECTED = "error_pattern_detected"
    SYSTEM_HEALTH_ISSUE = "system_health_issue"
    MANUAL_OVERRIDE = "manual_override"


@dataclass
class ConfigurationSetting:
    """A single configuration setting with metadata."""

    key: str
    value: Any
    category: ConfigurationCategory
    description: str
    default_value: Any
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    allowed_values: Optional[List[Any]] = None
    adaptive: bool = True
    sensitive: bool = False
    last_modified: datetime = field(default_factory=datetime.now)
    modified_by: str = "system"


@dataclass
class ConfigurationProfile:
    """A configuration profile for a specific context."""

    profile_id: str
    name: str
    description: str
    context: Dict[str, Any]  # Project type, user preferences, etc.
    settings: Dict[str, ConfigurationSetting] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    effectiveness_score: float = 0.0


@dataclass
class ConfigurationChange:
    """Record of a configuration change."""

    change_id: str
    setting_key: str
    old_value: Any
    new_value: Any
    reason: str
    trigger: AdaptationTrigger
    confidence: float
    expected_impact: float
    timestamp: datetime = field(default_factory=datetime.now)
    reverted: bool = False
    reversion_reason: Optional[str] = None


@dataclass
class AdaptationRule:
    """Rule for automatic configuration adaptation."""

    rule_id: str
    name: str
    description: str
    condition: Dict[str, Any]  # Conditions that trigger the rule
    action: Dict[str, Any]  # Configuration changes to apply
    priority: int  # 1-10, higher is more important
    enabled: bool = True
    success_rate: float = 0.0
    usage_count: int = 0
    last_triggered: Optional[datetime] = None


class AdaptiveConfigManager:
    """Intelligent adaptive configuration management system."""

    def __init__(self, root: Path):
        self.root = root
        self.config_path = root / ".ai_onboard" / "adaptive_config.json"
        self.config_history_path = root / ".ai_onboard" / "config_history.jsonl"
        self.config_profiles_path = root / ".ai_onboard" / "config_profiles.json"
        self.adaptation_rules_path = root / ".ai_onboard" / "adaptation_rules.json"
        self.config_analytics_path = root / ".ai_onboard" / "config_analytics.json"

        # Initialize logger
        self.logger = logging.getLogger(__name__)

        # Initialize subsystems
        self.continuous_improvement = (
            continuous_improvement_system.get_continuous_improvement_system(root)
        )

        # Configuration state
        self.current_config: Dict[str, ConfigurationSetting] = {}
        self.config_profiles: Dict[str, ConfigurationProfile] = {}
        self.adaptation_rules: List[AdaptationRule] = []
        self.config_history: List[ConfigurationChange] = []

        # Ensure directories exist
        self._ensure_directories()

        # Load existing data
        self._load_current_config()
        self._load_config_profiles()
        self._load_adaptation_rules()
        self._load_config_history()

        # Initialize default configuration if none exists
        if not self.current_config:
            self._initialize_default_config()

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for path in [
            self.config_path,
            self.config_history_path,
            self.config_profiles_path,
            self.adaptation_rules_path,
            self.config_analytics_path,
        ]:
            utils.ensure_dir(path.parent)

    def _initialize_default_config(self):
        """Initialize default configuration settings."""
        default_settings = {
            "gate_timeout": ConfigurationSetting(
                key="gate_timeout",
                value=2,
                category=ConfigurationCategory.AI_AGENT_BEHAVIOR,
                description="Timeout for gate system interactions (seconds)",
                default_value=2,
                min_value=1,
                max_value=30,
                adaptive=True,
            ),
            "safety_level": ConfigurationSetting(
                key="safety_level",
                value="medium",
                category=ConfigurationCategory.SAFETY_AND_SECURITY,
                description="Safety level for AI agent operations",
                default_value="medium",
                allowed_values=["low", "medium", "high", "strict"],
                adaptive=True,
            ),
            "collaboration_mode": ConfigurationSetting(
                key="collaboration_mode",
                value="collaborative",
                category=ConfigurationCategory.AI_AGENT_BEHAVIOR,
                description="Mode for AI agent collaboration",
                default_value="collaborative",
                allowed_values=["autonomous", "collaborative", "supervised"],
                adaptive=True,
            ),
            "vision_interrogation_adaptive": ConfigurationSetting(
                key="vision_interrogation_adaptive",
                value=True,
                category=ConfigurationCategory.WORKFLOW_OPTIMIZATION,
                description="Enable adaptive vision interrogation questions",
                default_value=True,
                adaptive=True,
            ),
            "error_handling_auto_recovery": ConfigurationSetting(
                key="error_handling_auto_recovery",
                value=True,
                category=ConfigurationCategory.SYSTEM_PERFORMANCE,
                description="Enable automatic error recovery",
                default_value=True,
                adaptive=True,
            ),
            "performance_monitoring_enabled": ConfigurationSetting(
                key="performance_monitoring_enabled",
                value=True,
                category=ConfigurationCategory.SYSTEM_PERFORMANCE,
                description="Enable performance monitoring",
                default_value=True,
                adaptive=True,
            ),
            "learning_enabled": ConfigurationSetting(
                key="learning_enabled",
                value=True,
                category=ConfigurationCategory.SYSTEM_PERFORMANCE,
                description="Enable continuous learning",
                default_value=True,
                adaptive=True,
            ),
            "ui_theme": ConfigurationSetting(
                key="ui_theme",
                value="auto",
                category=ConfigurationCategory.USER_INTERFACE,
                description="User interface theme",
                default_value="auto",
                allowed_values=["light", "dark", "auto"],
                adaptive=True,
            ),
            "notification_level": ConfigurationSetting(
                key="notification_level",
                value="medium",
                category=ConfigurationCategory.USER_INTERFACE,
                description="Level of notifications to show",
                default_value="medium",
                allowed_values=["low", "medium", "high"],
                adaptive=True,
            ),
            "auto_save_interval": ConfigurationSetting(
                key="auto_save_interval",
                value=30,
                category=ConfigurationCategory.SYSTEM_PERFORMANCE,
                description="Auto-save interval in seconds",
                default_value=30,
                min_value=5,
                max_value=300,
                adaptive=True,
            ),
        }

        self.current_config = default_settings
        self._save_current_config()

    def _load_current_config(self):
        """Load current configuration from storage."""
        if not self.config_path.exists():
            return

        data = utils.read_json(self.config_path, default={})

        for key, setting_data in data.items():
            self.current_config[key] = ConfigurationSetting(
                key=key,
                value=setting_data["value"],
                category=ConfigurationCategory(setting_data["category"]),
                description=setting_data["description"],
                default_value=setting_data["default_value"],
                min_value=setting_data.get("min_value"),
                max_value=setting_data.get("max_value"),
                allowed_values=setting_data.get("allowed_values"),
                adaptive=setting_data.get("adaptive", True),
                sensitive=setting_data.get("sensitive", False),
                last_modified=datetime.fromisoformat(setting_data["last_modified"]),
                modified_by=setting_data.get("modified_by", "system"),
            )

    def _load_config_profiles(self):
        """Load configuration profiles from storage."""
        if not self.config_profiles_path.exists():
            return

        data = utils.read_json(self.config_profiles_path, default={})

        for profile_id, profile_data in data.items():
            settings = {}
            for key, setting_data in profile_data["settings"].items():
                settings[key] = ConfigurationSetting(
                    key=key,
                    value=setting_data["value"],
                    category=ConfigurationCategory(setting_data["category"]),
                    description=setting_data["description"],
                    default_value=setting_data["default_value"],
                    min_value=setting_data.get("min_value"),
                    max_value=setting_data.get("max_value"),
                    allowed_values=setting_data.get("allowed_values"),
                    adaptive=setting_data.get("adaptive", True),
                    sensitive=setting_data.get("sensitive", False),
                    last_modified=datetime.fromisoformat(setting_data["last_modified"]),
                    modified_by=setting_data.get("modified_by", "system"),
                )

            self.config_profiles[profile_id] = ConfigurationProfile(
                profile_id=profile_id,
                name=profile_data["name"],
                description=profile_data["description"],
                context=profile_data["context"],
                settings=settings,
                created_at=datetime.fromisoformat(profile_data["created_at"]),
                last_used=datetime.fromisoformat(profile_data["last_used"]),
                usage_count=profile_data.get("usage_count", 0),
                effectiveness_score=profile_data.get("effectiveness_score", 0.0),
            )

    def _load_adaptation_rules(self):
        """Load adaptation rules from storage."""
        if not self.adaptation_rules_path.exists():
            self._initialize_default_rules()
            return

        data = utils.read_json(self.adaptation_rules_path, default=[])

        for rule_data in data:
            self.adaptation_rules.append(
                AdaptationRule(
                    rule_id=rule_data["rule_id"],
                    name=rule_data["name"],
                    description=rule_data["description"],
                    condition=rule_data["condition"],
                    action=rule_data["action"],
                    priority=rule_data["priority"],
                    enabled=rule_data.get("enabled", True),
                    success_rate=rule_data.get("success_rate", 0.0),
                    usage_count=rule_data.get("usage_count", 0),
                    last_triggered=(
                        datetime.fromisoformat(rule_data["last_triggered"])
                        if rule_data.get("last_triggered")
                        else None
                    ),
                )
            )

    def _load_config_history(self):
        """Load configuration change history."""
        if not self.config_history_path.exists():
            return

        with open(self.config_history_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    change_data = json.loads(line)
                    self.config_history.append(
                        ConfigurationChange(
                            change_id=change_data["change_id"],
                            setting_key=change_data["setting_key"],
                            old_value=change_data["old_value"],
                            new_value=change_data["new_value"],
                            reason=change_data["reason"],
                            trigger=AdaptationTrigger(change_data["trigger"]),
                            confidence=change_data["confidence"],
                            expected_impact=change_data["expected_impact"],
                            timestamp=datetime.fromisoformat(change_data["timestamp"]),
                            reverted=change_data.get("reverted", False),
                            reversion_reason=change_data.get("reversion_reason"),
                        )
                    )
                except (json.JSONDecodeError, KeyError):
                    continue

    def _initialize_default_rules(self):
        """Initialize default adaptation rules."""
        default_rules = [
            AdaptationRule(
                rule_id="rule_001",
                name="Reduce gate timeout for experienced users",
                description="Reduce gate timeout when user shows high satisfaction with quick interactions",
                condition={
                    "user_satisfaction": {"min": 0.8},
                    "interaction_frequency": {"min": 10},
                    "avg_response_time": {"max": 5.0},
                },
                action={
                    "gate_timeout": {
                        "value": 1,
                        "reason": "User prefers quick interactions",
                    }
                },
                priority=7,
            ),
            AdaptationRule(
                rule_id="rule_002",
                name="Increase safety level for new users",
                description="Increase safety level for new or uncertain users",
                condition={
                    "user_experience_level": {"max": 0.3},
                    "error_rate": {"min": 0.1},
                },
                action={
                    "safety_level": {
                        "value": "high",
                        "reason": "New user needs more guidance",
                    }
                },
                priority=8,
            ),
            AdaptationRule(
                rule_id="rule_003",
                name="Enable autonomous mode for experienced users",
                description="Enable autonomous mode for users with high confidence and low error rates",
                condition={
                    "user_confidence": {"min": 0.9},
                    "error_rate": {"max": 0.05},
                    "usage_frequency": {"min": 20},
                },
                action={
                    "collaboration_mode": {
                        "value": "autonomous",
                        "reason": "User is highly experienced",
                    }
                },
                priority=6,
            ),
            AdaptationRule(
                rule_id="rule_004",
                name="Optimize performance monitoring",
                description="Adjust performance monitoring based on system load",
                condition={
                    "system_load": {"min": 0.8},
                    "performance_score": {"max": 0.7},
                },
                action={
                    "performance_monitoring_enabled": {
                        "value": True,
                        "reason": "System needs monitoring",
                    },
                    "auto_save_interval": {
                        "value": 15,
                        "reason": "Reduce save interval for better performance",
                    },
                },
                priority=5,
            ),
            AdaptationRule(
                rule_id="rule_005",
                name="Adapt to project type",
                description="Adapt configuration based on project type",
                condition={
                    "project_type": {
                        "in": ["web_application", "data_science", "mobile_app"]
                    }
                },
                action={
                    "vision_interrogation_adaptive": {
                        "value": True,
                        "reason": "Project-specific questions needed",
                    }
                },
                priority=4,
            ),
        ]

        self.adaptation_rules = default_rules
        self._save_adaptation_rules()

    def get_all_configurations(self) -> List[Dict[str, Any]]:
        """Get all current configurations."""
        try:
            configurations = []

            for key, setting in self.current_config.items():
                configurations.append(
                    {
                        "name": key,
                        "value": setting.value,
                        "type": type(setting.value).__name__,
                        "last_updated": datetime.now().isoformat(),
                    }
                )

            return configurations

        except Exception as e:
            self.logger.error(f"Failed to get all configurations: {e}")
            return []

    def get_configuration_profiles(self) -> List[Dict[str, Any]]:
        """Get all configuration profiles."""
        try:
            profiles = []

            for name, profile in self.config_profiles.items():
                profiles.append(
                    {
                        "name": name,
                        "description": profile.description,
                        "settings_count": len(profile.settings),
                        "created_at": profile.created_at.isoformat(),
                        "last_used": (
                            profile.last_used.isoformat() if profile.last_used else None
                        ),
                    }
                )

            return profiles

        except Exception as e:
            self.logger.error(f"Failed to get configuration profiles: {e}")
            return []

    def get_setting(self, key: str) -> Any:
        """Get a configuration setting value."""
        if key in self.current_config:
            return self.current_config[key].value
        return None

    def set_setting(
        self,
        key: str,
        value: Any,
        reason: str = "manual_change",
        trigger: AdaptationTrigger = AdaptationTrigger.MANUAL_OVERRIDE,
        confidence: float = 1.0,
        expected_impact: float = 0.0,
    ) -> bool:
        """Set a configuration setting value."""
        if key not in self.current_config:
            return False

        setting = self.current_config[key]
        old_value = setting.value

        # Validate the new value
        if not self._validate_setting_value(setting, value):
            return False

        # Update the setting
        setting.value = value
        setting.last_modified = datetime.now()
        setting.modified_by = (
            "user" if trigger == AdaptationTrigger.MANUAL_OVERRIDE else "system"
        )

        # Record the change
        change = ConfigurationChange(
            change_id=f"change_{int(time.time())}_{utils.random_string(8)}",
            setting_key=key,
            old_value=old_value,
            new_value=value,
            reason=reason,
            trigger=trigger,
            confidence=confidence,
            expected_impact=expected_impact,
        )

        self.config_history.append(change)
        self._log_configuration_change(change)

        # Save configuration
        self._save_current_config()

        # Record learning event
        self.continuous_improvement.record_learning_event(
            learning_type=continuous_improvement_system.LearningType.USER_PREFERENCE,
            context={
                "setting_key": key,
                "old_value": old_value,
                "new_value": value,
                "trigger": trigger.value,
            },
            outcome={
                "configuration_change": True,
                "user_satisfaction": expected_impact,
            },
            confidence=confidence,
            impact_score=expected_impact,
            source="adaptive_config_manager",
        )

        return True

    def _validate_setting_value(
        self, setting: ConfigurationSetting, value: Any
    ) -> bool:
        """Validate a setting value against its constraints."""
        # Check type compatibility
        if type(value) != type(setting.default_value):
            return False

        # Check allowed values
        if setting.allowed_values and value not in setting.allowed_values:
            return False

        # Check min/max values for numeric types
        if isinstance(value, (int, float)):
            if setting.min_value is not None and value < setting.min_value:
                return False
            if setting.max_value is not None and value > setting.max_value:
                return False

        return True

    def adapt_configuration(
        self,
        context: Dict[str, Any],
        trigger: AdaptationTrigger = AdaptationTrigger.USAGE_PATTERN_CHANGE,
    ) -> List[ConfigurationChange]:
        """Adapt configuration based on context and rules."""
        applied_changes = []

        for rule in self.adaptation_rules:
            if not rule.enabled:
                continue

            if self._evaluate_rule_condition(rule.condition, context):
                changes = self._apply_rule_action(rule, context, trigger)
                applied_changes.extend(changes)

                # Update rule statistics
                rule.usage_count += 1
                rule.last_triggered = datetime.now()

        # Save updated rules
        self._save_adaptation_rules()

        return applied_changes

    def _evaluate_rule_condition(
        self, condition: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        """Evaluate if a rule condition is met."""
        for key, constraint in condition.items():
            if key not in context:
                return False

            context_value = context[key]

            if isinstance(constraint, dict):
                if "min" in constraint and context_value < constraint["min"]:
                    return False
                if "max" in constraint and context_value > constraint["max"]:
                    return False
                if "in" in constraint and context_value not in constraint["in"]:
                    return False
                if "equals" in constraint and context_value != constraint["equals"]:
                    return False
            else:
                if context_value != constraint:
                    return False

        return True

    def _apply_rule_action(
        self, rule: AdaptationRule, context: Dict[str, Any], trigger: AdaptationTrigger
    ) -> List[ConfigurationChange]:
        """Apply a rule's action to the configuration."""
        changes = []

        for setting_key, action_data in rule.action.items():
            if setting_key not in self.current_config:
                continue

            new_value = action_data["value"]
            reason = action_data.get("reason", f"Applied rule: {rule.name}")

            if self.set_setting(setting_key, new_value, reason, trigger, 0.8, 0.5):
                changes.append(self.config_history[-1])  # Get the last change

        return changes

    def create_configuration_profile(
        self,
        name: str,
        description: str,
        context: Dict[str, Any],
        settings_override: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new configuration profile."""
        profile_id = f"profile_{int(time.time())}_{utils.random_string(8)}"

        # Start with current configuration
        profile_settings = {}
        for key, setting in self.current_config.items():
            profile_settings[key] = ConfigurationSetting(
                key=setting.key,
                value=setting.value,
                category=setting.category,
                description=setting.description,
                default_value=setting.default_value,
                min_value=setting.min_value,
                max_value=setting.max_value,
                allowed_values=setting.allowed_values,
                adaptive=setting.adaptive,
                sensitive=setting.sensitive,
                last_modified=setting.last_modified,
                modified_by=setting.modified_by,
            )

        # Apply any overrides
        if settings_override:
            for key, value in settings_override.items():
                if key in profile_settings:
                    profile_settings[key].value = value
                    profile_settings[key].last_modified = datetime.now()
                    profile_settings[key].modified_by = "profile_creation"

        profile = ConfigurationProfile(
            profile_id=profile_id,
            name=name,
            description=description,
            context=context,
            settings=profile_settings,
        )

        self.config_profiles[profile_id] = profile
        self._save_config_profiles()

        return profile_id

    def apply_configuration_profile(self, profile_id: str) -> bool:
        """Apply a configuration profile."""
        if profile_id not in self.config_profiles:
            return False

        profile = self.config_profiles[profile_id]

        # Apply profile settings
        for key, setting in profile.settings.items():
            if key in self.current_config:
                self.set_setting(
                    key,
                    setting.value,
                    f"Applied profile: {profile.name}",
                    AdaptationTrigger.MANUAL_OVERRIDE,
                    0.9,
                    0.7,
                )

        # Update profile usage
        profile.last_used = datetime.now()
        profile.usage_count += 1
        self._save_config_profiles()

        return True

    def get_configuration_recommendations(
        self, context: Dict[str, Any], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get configuration recommendations based on context."""
        recommendations = []

        # Analyze current configuration against context
        for key, setting in self.current_config.items():
            if not setting.adaptive:
                continue

            recommendation = self._analyze_setting_for_recommendation(setting, context)
            if recommendation:
                recommendations.append(recommendation)

        # Sort by expected impact
        recommendations.sort(key=lambda x: x["expected_impact"], reverse=True)

        return recommendations[:limit]

    def _analyze_setting_for_recommendation(
        self, setting: ConfigurationSetting, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Analyze a setting for potential recommendations."""
        # This would implement intelligent analysis based on context
        # For now, return a simple recommendation structure
        return {
            "setting_key": setting.key,
            "current_value": setting.value,
            "recommended_value": setting.default_value,
            "reason": "Reset to default for better performance",
            "expected_impact": 0.3,
            "confidence": 0.7,
        }

    def get_configuration_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get configuration analytics for the last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)

        # Filter recent changes
        recent_changes = [
            change for change in self.config_history if change.timestamp >= cutoff_date
        ]

        if not recent_changes:
            return {
                "status": "no_data",
                "message": f"No configuration changes for the last {days} days",
            }

        # Calculate analytics
        changes_by_trigger = {}
        changes_by_setting = {}
        reverted_changes = 0

        for change in recent_changes:
            trigger = change.trigger.value
            if trigger not in changes_by_trigger:
                changes_by_trigger[trigger] = 0
            changes_by_trigger[trigger] += 1

            if change.setting_key not in changes_by_setting:
                changes_by_setting[change.setting_key] = 0
            changes_by_setting[change.setting_key] += 1

            if change.reverted:
                reverted_changes += 1

        return {
            "status": "success",
            "period_days": days,
            "total_changes": len(recent_changes),
            "reverted_changes": reverted_changes,
            "reversion_rate": (
                reverted_changes / len(recent_changes) if recent_changes else 0
            ),
            "changes_by_trigger": changes_by_trigger,
            "changes_by_setting": changes_by_setting,
            "most_changed_settings": sorted(
                changes_by_setting.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }

    def _log_configuration_change(self, change: ConfigurationChange):
        """Log a configuration change to storage."""
        change_data = {
            "change_id": change.change_id,
            "setting_key": change.setting_key,
            "old_value": change.old_value,
            "new_value": change.new_value,
            "reason": change.reason,
            "trigger": change.trigger.value,
            "confidence": change.confidence,
            "expected_impact": change.expected_impact,
            "timestamp": change.timestamp.isoformat(),
            "reverted": change.reverted,
            "reversion_reason": change.reversion_reason,
        }

        with open(self.config_history_path, "a", encoding="utf-8") as f:
            json.dump(change_data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    def _save_current_config(self):
        """Save current configuration to storage."""
        data = {}
        for key, setting in self.current_config.items():
            data[key] = {
                "value": setting.value,
                "category": setting.category.value,
                "description": setting.description,
                "default_value": setting.default_value,
                "min_value": setting.min_value,
                "max_value": setting.max_value,
                "allowed_values": setting.allowed_values,
                "adaptive": setting.adaptive,
                "sensitive": setting.sensitive,
                "last_modified": setting.last_modified.isoformat(),
                "modified_by": setting.modified_by,
            }

        utils.write_json(self.config_path, data)

    def _save_config_profiles(self):
        """Save configuration profiles to storage."""
        data = {}
        for profile_id, profile in self.config_profiles.items():
            settings_data = {}
            for key, setting in profile.settings.items():
                settings_data[key] = {
                    "value": setting.value,
                    "category": setting.category.value,
                    "description": setting.description,
                    "default_value": setting.default_value,
                    "min_value": setting.min_value,
                    "max_value": setting.max_value,
                    "allowed_values": setting.allowed_values,
                    "adaptive": setting.adaptive,
                    "sensitive": setting.sensitive,
                    "last_modified": setting.last_modified.isoformat(),
                    "modified_by": setting.modified_by,
                }

            data[profile_id] = {
                "name": profile.name,
                "description": profile.description,
                "context": profile.context,
                "settings": settings_data,
                "created_at": profile.created_at.isoformat(),
                "last_used": profile.last_used.isoformat(),
                "usage_count": profile.usage_count,
                "effectiveness_score": profile.effectiveness_score,
            }

        utils.write_json(self.config_profiles_path, data)

    def _save_adaptation_rules(self):
        """Save adaptation rules to storage."""
        data = []
        for rule in self.adaptation_rules:
            data.append(
                {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "description": rule.description,
                    "condition": rule.condition,
                    "action": rule.action,
                    "priority": rule.priority,
                    "enabled": rule.enabled,
                    "success_rate": rule.success_rate,
                    "usage_count": rule.usage_count,
                    "last_triggered": (
                        rule.last_triggered.isoformat() if rule.last_triggered else None
                    ),
                }
            )

        utils.write_json(self.adaptation_rules_path, data)


def get_adaptive_config_manager(root: Path) -> AdaptiveConfigManager:
    """Get adaptive configuration manager instance."""
    return AdaptiveConfigManager(root)
