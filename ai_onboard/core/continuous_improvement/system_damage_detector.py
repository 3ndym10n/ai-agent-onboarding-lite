"""
System Damage Risk Detector

Detects actions that could break the system or cause real damage.
This addresses the user's need to be warned about high-risk operations.
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base.utils import read_json, write_json


class DamageLevel(Enum):
    """Levels of potential system damage."""

    NONE = "none"  # No risk of damage
    LOW = "low"  # Minor risk, easily recoverable
    MEDIUM = "medium"  # Moderate risk, may require intervention
    HIGH = "high"  # Significant risk, likely to cause issues
    CRITICAL = "critical"  # Severe risk, could break the system


class DamageType(Enum):
    """Types of potential system damage."""

    FILE_DELETION = "file_deletion"
    CONFIGURATION_CORRUPTION = "configuration_corruption"
    DEPENDENCY_BREAKAGE = "dependency_breakage"
    DATA_LOSS = "data_loss"
    SYSTEM_INSTABILITY = "system_instability"
    SECURITY_VULNERABILITY = "security_vulnerability"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    INTEGRATION_FAILURE = "integration_failure"


@dataclass
class DamageRisk:
    """Assessment of potential system damage."""

    timestamp: float
    action_description: str
    damage_level: DamageLevel
    damage_types: List[DamageType] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    rollback_plan: str = ""
    confidence: float = 0.0  # 0-1 confidence in the assessment
    requires_immediate_attention: bool = False


@dataclass
class SystemComponent:
    """Represents a critical system component."""

    name: str
    path: str
    importance: str  # critical, high, medium, low
    backup_available: bool = True
    dependencies: List[str] = field(default_factory=list)
    last_modified: float = 0.0


class SystemDamageDetector:
    """
    Detects actions that could cause system damage.

    This system ensures:
    1. High-risk operations are flagged
    2. Critical system components are protected
    3. Damage mitigation strategies are provided
    4. Rollback plans are available
    5. User is warned before dangerous operations
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.components_path = root_path / ".ai_onboard" / "system_components.json"
        self.damage_log_path = root_path / ".ai_onboard" / "damage_assessments.jsonl"

        # Ensure directories exist
        self.components_path.parent.mkdir(parents=True, exist_ok=True)

        # Load critical system components
        self.critical_components = self._load_critical_components()

        # Damage assessment history
        self.recent_assessments: List[DamageRisk] = []

    def _load_critical_components(self) -> List[SystemComponent]:
        """Load critical system components."""
        try:
            data = read_json(self.components_path, default={})
            components = []
            for comp_data in data.get("components", []):
                component = SystemComponent(
                    name=comp_data["name"],
                    path=comp_data["path"],
                    importance=comp_data["importance"],
                    backup_available=comp_data.get("backup_available", True),
                    dependencies=comp_data.get("dependencies", []),
                    last_modified=comp_data.get("last_modified", 0.0),
                )
                components.append(component)
            return components
        except Exception:
            # Default critical components
            return [
                SystemComponent(
                    name="ai_onboard_core",
                    path="ai_onboard/core",
                    importance="critical",
                    dependencies=["python", "pathlib"],
                ),
                SystemComponent(
                    name="cli_commands",
                    path="ai_onboard/cli",
                    importance="high",
                    dependencies=["ai_onboard_core"],
                ),
                SystemComponent(
                    name="policies",
                    path="ai_onboard/policies",
                    importance="high",
                    dependencies=["ai_onboard_core"],
                ),
                SystemComponent(
                    name="project_config",
                    path="ai_onboard.json",
                    importance="critical",
                    backup_available=True,
                ),
            ]

    def _save_critical_components(self):
        """Save critical system components."""
        try:
            data = {
                "components": [
                    {
                        "name": comp.name,
                        "path": comp.path,
                        "importance": comp.importance,
                        "backup_available": comp.backup_available,
                        "dependencies": comp.dependencies,
                        "last_modified": comp.last_modified,
                    }
                    for comp in self.critical_components
                ]
            }
            write_json(self.components_path, data)
        except (ValueError, TypeError, AttributeError) as e:
            print(f"Error: {e}")

    def assess_damage_risk(
        self,
        action_description: str,
        action_type: str,
        target_paths: Optional[List[str]] = None,
        system_impact: str = "unknown",
    ) -> DamageRisk:
        """
        Assess the potential for system damage from an action.

        Returns a DamageRisk assessment with mitigation strategies.
        """

        if target_paths is None:
            target_paths = []

        # Initialize damage risk assessment
        risk = DamageRisk(
            timestamp=time.time(),
            action_description=action_description,
            damage_level=DamageLevel.NONE,
            confidence=0.0,
        )

        # Analyze risk factors
        risk_factors = []
        damage_types = []
        mitigation_strategies = []

        # 1. Check for file deletion risks
        if action_type in ["delete", "remove", "cleanup"]:
            for target_path in target_paths:
                for component in self.critical_components:
                    if target_path.startswith(component.path):
                        risk_factors.append(
                            f"Deleting critical component: {component.name}"
                        )
                        damage_types.append(DamageType.FILE_DELETION)
                        if component.importance == "critical":
                            risk.damage_level = DamageLevel.CRITICAL
                            risk.requires_immediate_attention = True
                        elif component.importance == "high":
                            risk.damage_level = DamageLevel.HIGH

        # 2. Check for configuration corruption risks
        if action_type in ["modify", "update", "change"]:
            config_files = [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"]
            for target_path in target_paths:
                if any(target_path.endswith(ext) for ext in config_files):
                    risk_factors.append(f"Modifying configuration file: {target_path}")
                    damage_types.append(DamageType.CONFIGURATION_CORRUPTION)
                    if risk.damage_level == DamageLevel.NONE:
                        risk.damage_level = DamageLevel.MEDIUM

        # 3. Check for dependency breakage risks
        if action_type in ["refactor", "restructure", "move"]:
            for target_path in target_paths:
                for component in self.critical_components:
                    if target_path.startswith(component.path):
                        risk_factors.append(
                            f"Modifying component with dependencies: {component.name}"
                        )
                        damage_types.append(DamageType.DEPENDENCY_BREAKAGE)
                        if len(component.dependencies) > 3:
                            risk.damage_level = DamageLevel.HIGH

        # 4. Check for data loss risks
        if action_type in ["clear", "reset", "wipe"]:
            risk_factors.append("Clearing or resetting data")
            damage_types.append(DamageType.DATA_LOSS)
            risk.damage_level = DamageLevel.HIGH

        # 5. Check for system instability risks
        if system_impact in ["high", "critical"]:
            risk_factors.append("High system impact operation")
            damage_types.append(DamageType.SYSTEM_INSTABILITY)
            if risk.damage_level == DamageLevel.NONE:
                risk.damage_level = DamageLevel.MEDIUM

        # 6. Check for performance degradation risks
        if action_type in ["optimize", "refactor", "restructure"]:
            if len(target_paths) > 10:  # Large-scale changes
                risk_factors.append("Large-scale system changes")
                damage_types.append(DamageType.PERFORMANCE_DEGRADATION)
                if risk.damage_level == DamageLevel.NONE:
                    risk.damage_level = DamageLevel.MEDIUM

        # Generate mitigation strategies based on risk level
        if risk.damage_level == DamageLevel.CRITICAL:
            mitigation_strategies.extend(
                [
                    "Create full system backup before proceeding",
                    "Test changes in isolated environment first",
                    "Implement staged rollout with rollback points",
                    "Monitor system health continuously",
                ]
            )
            risk.rollback_plan = "Full system restore from backup"

        elif risk.damage_level == DamageLevel.HIGH:
            mitigation_strategies.extend(
                [
                    "Create targeted backup of affected components",
                    "Implement incremental changes with validation",
                    "Set up monitoring and alerting",
                    "Prepare rollback procedures",
                ]
            )
            risk.rollback_plan = "Restore affected components from backup"

        elif risk.damage_level == DamageLevel.MEDIUM:
            mitigation_strategies.extend(
                [
                    "Create backup of critical files",
                    "Test changes in development environment",
                    "Implement validation checks",
                ]
            )
            risk.rollback_plan = "Restore modified files from backup"

        elif risk.damage_level == DamageLevel.LOW:
            mitigation_strategies.extend(["Create basic backup", "Monitor for issues"])
            risk.rollback_plan = "Manual file restoration"

        # Set risk factors and damage types
        risk.risk_factors = risk_factors
        risk.damage_types = damage_types
        risk.mitigation_strategies = mitigation_strategies

        # Calculate confidence based on available information
        confidence_factors = 0
        if target_paths:
            confidence_factors += 1
        if system_impact != "unknown":
            confidence_factors += 1
        if risk_factors:
            confidence_factors += 1

        risk.confidence = min(confidence_factors / 3.0, 1.0)

        # Add to recent assessments
        self.recent_assessments.append(risk)

        # Keep only last 50 assessments
        if len(self.recent_assessments) > 50:
            self.recent_assessments = self.recent_assessments[-50:]

        # Save to persistent storage
        self._save_damage_assessment(risk)

        return risk

    def _save_damage_assessment(self, risk: DamageRisk):
        """Save damage assessment to persistent storage."""
        try:
            risk_data = {
                "timestamp": risk.timestamp,
                "action_description": risk.action_description,
                "damage_level": risk.damage_level.value,
                "damage_types": [dt.value for dt in risk.damage_types],
                "risk_factors": risk.risk_factors,
                "mitigation_strategies": risk.mitigation_strategies,
                "rollback_plan": risk.rollback_plan,
                "confidence": risk.confidence,
                "requires_immediate_attention": risk.requires_immediate_attention,
            }

            with open(self.damage_log_path, "a", encoding="utf-8") as f:

                f.write(json.dumps(risk_data) + "\n")
        except (ValueError, TypeError, AttributeError) as e:
            print(f"Error: {e}")

    def display_damage_assessment(self, risk: DamageRisk):
        """Display damage assessment to the user."""

        # Damage level emoji mapping
        damage_emoji = {
            DamageLevel.NONE: "✅",
            DamageLevel.LOW: "🟡",
            DamageLevel.MEDIUM: "🟠",
            DamageLevel.HIGH: "🔴",
            DamageLevel.CRITICAL: "💥",
        }

        print(f"\n⚠️ SYSTEM DAMAGE RISK ASSESSMENT")
        print(f"=" * 60)
        print(f"📝 Action: {risk.action_description}")
        print(
            f"{damage_emoji[risk.damage_level]} Risk Level: {risk.damage_level.value.upper()}"
        )
        print(f"🎯 Confidence: {risk.confidence:.1%}")

        if risk.requires_immediate_attention:
            print(f"🚨 REQUIRES IMMEDIATE ATTENTION")

        if risk.risk_factors:
            print(f"\n⚠️ Risk Factors:")
            for factor in risk.risk_factors:
                print(f"   • {factor}")

        if risk.damage_types:
            print(f"\n💥 Potential Damage Types:")
            for damage_type in risk.damage_types:
                print(f"   • {damage_type.value}")

        if risk.mitigation_strategies:
            print(f"\n🛡️ Mitigation Strategies:")
            for strategy in risk.mitigation_strategies:
                print(f"   • {strategy}")

        if risk.rollback_plan:
            print(f"\n🔙 Rollback Plan: {risk.rollback_plan}")

        if risk.damage_level in [DamageLevel.HIGH, DamageLevel.CRITICAL]:
            print(f"\n🚨 HIGH RISK OPERATION DETECTED")
            print(f"   Consider requesting user approval before proceeding")

        print(f"=" * 60)

    def get_damage_summary(self) -> Dict[str, Any]:
        """Get summary of recent damage assessments."""
        if not self.recent_assessments:
            return {"message": "No damage assessments performed"}

        total_assessments = len(self.recent_assessments)
        critical_count = len(
            [
                r
                for r in self.recent_assessments
                if r.damage_level == DamageLevel.CRITICAL
            ]
        )
        high_count = len(
            [r for r in self.recent_assessments if r.damage_level == DamageLevel.HIGH]
        )
        medium_count = len(
            [r for r in self.recent_assessments if r.damage_level == DamageLevel.MEDIUM]
        )
        low_count = len(
            [r for r in self.recent_assessments if r.damage_level == DamageLevel.LOW]
        )
        none_count = len(
            [r for r in self.recent_assessments if r.damage_level == DamageLevel.NONE]
        )

        return {
            "total_assessments": total_assessments,
            "critical_risks": critical_count,
            "high_risks": high_count,
            "medium_risks": medium_count,
            "low_risks": low_count,
            "no_risks": none_count,
            "overall_risk_score": (
                (
                    (
                        critical_count * 100
                        + high_count * 80
                        + medium_count * 60
                        + low_count * 30
                    )
                    / total_assessments
                )
                if total_assessments > 0
                else 0
            ),
            "recent_high_risks": [
                {
                    "action": r.action_description,
                    "level": r.damage_level.value,
                    "timestamp": r.timestamp,
                }
                for r in self.recent_assessments[-10:]
                if r.damage_level in [DamageLevel.HIGH, DamageLevel.CRITICAL]
            ],
        }

    def add_critical_component(self, name: str, path: str, importance: str = "medium"):
        """Add a critical system component to monitor."""
        component = SystemComponent(
            name=name, path=path, importance=importance, last_modified=time.time()
        )
        self.critical_components.append(component)
        self._save_critical_components()
        print(f"✅ Added critical component: {name} ({importance})")

    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health based on recent assessments."""
        summary = self.get_damage_summary()

        health_score = 100 - summary.get("overall_risk_score", 0)

        if health_score >= 90:
            health_status = "excellent"
        elif health_score >= 75:
            health_status = "good"
        elif health_score >= 50:
            health_status = "fair"
        elif health_score >= 25:
            health_status = "poor"
        else:
            health_status = "critical"

        return {
            "health_score": health_score,
            "health_status": health_status,
            "summary": summary,
            "recommendations": self._get_health_recommendations(health_score),
        }

    def _get_health_recommendations(self, health_score: float) -> List[str]:
        """Get health improvement recommendations."""
        recommendations = []

        if health_score < 50:
            recommendations.extend(
                [
                    "Consider implementing more safety checks",
                    "Review recent high-risk operations",
                    "Implement automated backup procedures",
                    "Add more validation before system changes",
                ]
            )
        elif health_score < 75:
            recommendations.extend(
                [
                    "Monitor system changes more closely",
                    "Implement staged rollouts for major changes",
                    "Add rollback procedures for critical operations",
                ]
            )

        return recommendations


def get_system_damage_detector(root_path: Path) -> SystemDamageDetector:
    """Get the global system damage detector instance."""
    global _damage_detector_instance
    if _damage_detector_instance is None:
        _damage_detector_instance = SystemDamageDetector(root_path)
    return _damage_detector_instance


# Global instance
_damage_detector_instance: Optional[SystemDamageDetector] = None
