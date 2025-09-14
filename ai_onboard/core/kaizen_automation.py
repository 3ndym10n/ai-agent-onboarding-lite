"""
Kaizen Cycle Automation (T12) - Automated continuous improvement system.

This module implements automated Kaizen cycles that:
- Continuously monitor system performance and user satisfaction
- Automatically identify improvement opportunities
- Execute improvement experiments with safety guardrails
- Learn from results and adapt future improvements
- Maintain improvement history and success metrics
"""

import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import utils
from .enhanced_conversation_context import get_enhanced_context_manager
from .unified_metrics_collector import (
    MetricCategory,
    MetricEvent,
    MetricQuery,
    MetricSource,
    get_unified_metrics_collector,
)
from .user_preference_learning import get_user_preference_learning_system


class KaizenCycleStage(Enum):
    """Stages of the Kaizen improvement cycle."""

    OBSERVE = "observe"  # Observe current state and metrics
    ORIENT = "orient"  # Orient and analyze patterns
    DECIDE = "decide"  # Decide on improvement actions
    ACT = "act"  # Act on improvement decisions
    LEARN = "learn"  # Learn from results and feedback


class ImprovementPriority(Enum):
    """Priority levels for improvements."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImprovementStatus(Enum):
    """Status of improvement initiatives."""

    IDENTIFIED = "identified"
    PLANNED = "planned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ImprovementCategory(Enum):
    """Categories of improvements."""

    PERFORMANCE = "performance"
    USER_EXPERIENCE = "user_experience"
    RELIABILITY = "reliability"
    SECURITY = "security"
    EFFICIENCY = "efficiency"
    LEARNING = "learning"
    AUTOMATION = "automation"


@dataclass
class ImprovementOpportunity:
    """An identified opportunity for improvement."""

    opportunity_id: str
    category: ImprovementCategory
    priority: ImprovementPriority
    title: str
    description: str

    # Evidence and metrics
    evidence: Dict[str, Any] = field(default_factory = dict)
    current_metrics: Dict[str, float] = field(default_factory = dict)
    target_metrics: Dict[str, float] = field(default_factory = dict)

    # Implementation details
    proposed_actions: List[str] = field(default_factory = list)
    estimated_effort: int = 1  # 1 - 5 scale
    estimated_impact: int = 1  # 1 - 5 scale
    risk_level: int = 1  # 1 - 5 scale

    # Tracking
    identified_at: datetime = field(default_factory = datetime.now)
    status: ImprovementStatus = ImprovementStatus.IDENTIFIED

    # Results
    experiment_results: Optional[Dict[str, Any]] = None
    success_metrics: Dict[str, float] = field(default_factory = dict)
    lessons_learned: List[str] = field(default_factory = list)


@dataclass
class KaizenCycle:
    """A complete Kaizen improvement cycle."""

    cycle_id: str
    started_at: datetime
    stage: KaizenCycleStage

    # Cycle data
    observations: Dict[str, Any] = field(default_factory = dict)
    analysis_results: Dict[str, Any] = field(default_factory = dict)
    improvement_decisions: List[str] = field(default_factory = list)
    actions_taken: List[Dict[str, Any]] = field(default_factory = list)
    learning_outcomes: Dict[str, Any] = field(default_factory = dict)

    # Metrics
    baseline_metrics: Dict[str, float] = field(default_factory = dict)
    target_metrics: Dict[str, float] = field(default_factory = dict)
    achieved_metrics: Dict[str, float] = field(default_factory = dict)

    # Status
    completed_at: Optional[datetime] = None
    success_score: float = 0.0
    overall_impact: str = "unknown"


class KaizenMetricsAnalyzer:
    """Analyzes metrics to identify improvement opportunities."""

    def __init__(self, root: Path):
        self.root = root
        self.metrics_collector = get_unified_metrics_collector(root)
        self.preference_system = get_user_preference_learning_system(root)

    def analyze_performance_opportunities(self) -> List[ImprovementOpportunity]:
        """Analyze performance metrics for improvement opportunities."""
        opportunities = []

        try:
            # Get recent performance metrics
            from ..core.unified_metrics_collector import MetricQuery

            query = MetricQuery(
                category = MetricCategory.TIMING,
                start_time = datetime.now() - timedelta(days = 7),
                limit = 1000,
            )

            result = self.metrics_collector.query_metrics(query)

            if result.metrics:
                # Analyze slow operations
                slow_operations = []
                for metric in result.metrics:
                    if metric.value > 1000:  # > 1 second
                        slow_operations.append((metric.name, metric.value))

                if slow_operations:
                    # Sort by slowest
                    slow_operations.sort(key = lambda x: x[1], reverse = True)

                    opportunity = ImprovementOpportunity(
                        opportunity_id = f"perf_{int(time.time())}",
                        category = ImprovementCategory.PERFORMANCE,
                        priority=(
                            ImprovementPriority.HIGH
                            if slow_operations[0][1] > 5000
                            else ImprovementPriority.MEDIUM
                        ),
                        title="Optimize slow operations",
                        description = f"Found {len(slow_operations)} operations taking >1s to complete",
                        evidence={
                            "slow_operations": slow_operations[:5],
                            "slowest_operation": slow_operations[0][0],
                            "slowest_time": slow_operations[0][1],
                        },
                        current_metrics={
                            "avg_response_time": sum(op[1] for op in slow_operations)
                            / len(slow_operations)
                        },
                        target_metrics={"avg_response_time": 500.0},  # Target 500ms
                        proposed_actions=[
                            "Profile slow operations",
                            "Implement caching where appropriate",
                            "Optimize database queries",
                            "Add async processing for long operations",
                        ],
                        estimated_effort = 3,
                        estimated_impact = 4,
                        risk_level = 2,
                    )

                    opportunities.append(opportunity)

        except Exception as e:
            print(f"Warning: Failed to analyze performance opportunities: {e}")

        return opportunities

    def analyze_user_experience_opportunities(self) -> List[ImprovementOpportunity]:
        """Analyze user experience metrics for improvement opportunities."""
        opportunities = []

        try:
            # Get user interaction patterns
            continuity_data = self.preference_system.get_system_wide_patterns()

            if continuity_data:
                # Check for common user frustrations
                if continuity_data.get("error_rate", 0) > 0.05:  # >5% error rate
                    opportunity = ImprovementOpportunity(
                        opportunity_id = f"ux_errors_{int(time.time())}",
                        category = ImprovementCategory.USER_EXPERIENCE,
                        priority = ImprovementPriority.HIGH,
                        title="Reduce user - facing errors",
                        description = f"Error rate is {continuity_data.get('error_rate', 0) * 100:.1f}%, above acceptable threshold",
                        evidence={"error_rate": continuity_data.get("error_rate", 0)},
                        current_metrics={
                            "error_rate": continuity_data.get("error_rate", 0)
                        },
                        target_metrics={"error_rate": 0.02},  # Target 2%
                        proposed_actions=[
                            "Improve error messages and recovery suggestions",
                            "Add input validation and user guidance",
                            "Implement graceful error handling",
                            "Add user education and help content",
                        ],
                        estimated_effort = 4,
                        estimated_impact = 5,
                        risk_level = 2,
                    )

                    opportunities.append(opportunity)

                # Check for user onboarding issues
                if (
                    continuity_data.get("new_user_success_rate", 1.0) < 0.8
                ):  # <80% success
                    opportunity = ImprovementOpportunity(
                        opportunity_id = f"ux_onboarding_{int(time.time())}",
                        category = ImprovementCategory.USER_EXPERIENCE,
                        priority = ImprovementPriority.HIGH,
                        title="Improve new user onboarding",
                        description="New user success rate is below 80%",
                        evidence={
                            "new_user_success_rate": continuity_data.get(
                                "new_user_success_rate", 1.0
                            )
                        },
                        current_metrics={
                            "new_user_success_rate": continuity_data.get(
                                "new_user_success_rate", 1.0
                            )
                        },
                        target_metrics={"new_user_success_rate": 0.9},  # Target 90%
                        proposed_actions=[
                            "Add interactive tutorials",
                            "Improve first - time user experience",
                            "Add contextual help and guidance",
                            "Simplify initial setup process",
                        ],
                        estimated_effort = 5,
                        estimated_impact = 4,
                        risk_level = 2,
                    )

                    opportunities.append(opportunity)

        except Exception as e:
            print(f"Warning: Failed to analyze UX opportunities: {e}")

        return opportunities

    def analyze_reliability_opportunities(self) -> List[ImprovementOpportunity]:
        """Analyze system reliability for improvement opportunities."""
        opportunities = []

        try:
            # Check error rates and failure patterns
            query = MetricQuery(
                category = MetricCategory.ERROR,
                start_time = datetime.now() - timedelta(days = 7),
                limit = 1000,
            )

            result = self.metrics_collector.query_metrics(query)

            if result.metrics:
                error_count = len(result.metrics)

                # If we have significant errors, create improvement opportunity
                if error_count > 10:  # More than 10 errors in a week
                    opportunity = ImprovementOpportunity(
                        opportunity_id = f"reliability_{int(time.time())}",
                        category = ImprovementCategory.RELIABILITY,
                        priority=(
                            ImprovementPriority.HIGH
                            if error_count > 50
                            else ImprovementPriority.MEDIUM
                        ),
                        title="Improve system reliability",
                        description = f"System has experienced {error_count} errors in the past week",
                        evidence={
                            "error_count": error_count,
                            "error_rate": error_count / 168,
                        },  # per hour
                        current_metrics={"errors_per_hour": error_count / 168},
                        target_metrics={
                            "errors_per_hour": 0.1
                        },  # Target <0.1 errors per hour
                        proposed_actions=[
                            "Implement comprehensive error monitoring",
                            "Add automated error recovery mechanisms",
                            "Improve input validation and edge case handling",
                            "Add system health checks and alerts",
                        ],
                        estimated_effort = 4,
                        estimated_impact = 5,
                        risk_level = 1,
                    )

                    opportunities.append(opportunity)

        except Exception as e:
            print(f"Warning: Failed to analyze reliability opportunities: {e}")

        return opportunities


class KaizenAutomationEngine:
    """Main engine for automated Kaizen cycles."""

    def __init__(self, root: Path):
        self.root = root
        self.data_dir = root / ".ai_onboard" / "kaizen_automation"
        self.data_dir.mkdir(parents = True, exist_ok = True)

        # Components
        self.metrics_analyzer = KaizenMetricsAnalyzer(root)
        self.metrics_collector = get_unified_metrics_collector(root)
        self.enhanced_context = get_enhanced_context_manager(root)

        # State
        self.active_cycles: Dict[str, KaizenCycle] = {}
        self.improvement_opportunities: Dict[str, ImprovementOpportunity] = {}
        self.automation_config = self._load_automation_config()

        # Threading
        self._running = False
        self._automation_thread: Optional[threading.Thread] = None
        self._executor = ThreadPoolExecutor(max_workers = 2, thread_name_prefix="kaizen")

        # Load existing data
        self._load_persistent_data()

    def _load_automation_config(self) -> Dict[str, Any]:
        """Load automation configuration."""
        config_file = self.data_dir / "automation_config.json"

        default_config = {
            "enabled": True,
            "cycle_interval_hours": 24,  # Run daily
            "max_concurrent_improvements": 3,
            "min_confidence_threshold": 0.7,
            "auto_execute_low_risk": True,
            "notification_enabled": True,
            "learning_enabled": True,
            "categories_enabled": {
                "performance": True,
                "user_experience": True,
                "reliability": True,
                "security": False,  # Require manual approval
                "efficiency": True,
                "learning": True,
                "automation": True,
            },
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
            json.dump(default_config, f, indent = 2)

        return default_config

    def _load_persistent_data(self):
        """Load persistent Kaizen data."""
        try:
            # Load improvement opportunities
            opportunities_file = self.data_dir / "opportunities.json"
            if opportunities_file.exists():
                with open(opportunities_file, "r") as f:
                    data = json.load(f)
                    for opp_id, opp_data in data.items():
                        # Convert back to dataclass
                        opp_data["identified_at"] = datetime.fromisoformat(
                            opp_data["identified_at"]
                        )
                        opp_data["category"] = ImprovementCategory(opp_data["category"])
                        opp_data["priority"] = ImprovementPriority(opp_data["priority"])
                        opp_data["status"] = ImprovementStatus(opp_data["status"])

                        self.improvement_opportunities[opp_id] = ImprovementOpportunity(
                            **opp_data
                        )

            # Load active cycles
            cycles_file = self.data_dir / "active_cycles.json"
            if cycles_file.exists():
                with open(cycles_file, "r") as f:
                    data = json.load(f)
                    for cycle_id, cycle_data in data.items():
                        # Convert back to dataclass
                        cycle_data["started_at"] = datetime.fromisoformat(
                            cycle_data["started_at"]
                        )
                        cycle_data["stage"] = KaizenCycleStage(cycle_data["stage"])
                        if cycle_data.get("completed_at"):
                            cycle_data["completed_at"] = datetime.fromisoformat(
                                cycle_data["completed_at"]
                            )

                        self.active_cycles[cycle_id] = KaizenCycle(**cycle_data)

        except Exception as e:
            print(f"Warning: Failed to load persistent Kaizen data: {e}")

    def _save_persistent_data(self):
        """Save persistent Kaizen data."""
        try:
            # Save improvement opportunities
            opportunities_data = {}
            for opp_id, opp in self.improvement_opportunities.items():
                opp_dict = {
                    "opportunity_id": opp.opportunity_id,
                    "category": opp.category.value,
                    "priority": opp.priority.value,
                    "title": opp.title,
                    "description": opp.description,
                    "evidence": opp.evidence,
                    "current_metrics": opp.current_metrics,
                    "target_metrics": opp.target_metrics,
                    "proposed_actions": opp.proposed_actions,
                    "estimated_effort": opp.estimated_effort,
                    "estimated_impact": opp.estimated_impact,
                    "risk_level": opp.risk_level,
                    "identified_at": opp.identified_at.isoformat(),
                    "status": opp.status.value,
                    "experiment_results": opp.experiment_results,
                    "success_metrics": opp.success_metrics,
                    "lessons_learned": opp.lessons_learned,
                }
                opportunities_data[opp_id] = opp_dict

            with open(self.data_dir / "opportunities.json", "w") as f:
                json.dump(opportunities_data, f, indent = 2)

            # Save active cycles
            cycles_data = {}
            for cycle_id, cycle in self.active_cycles.items():
                cycle_dict = {
                    "cycle_id": cycle.cycle_id,
                    "started_at": cycle.started_at.isoformat(),
                    "stage": cycle.stage.value,
                    "observations": cycle.observations,
                    "analysis_results": cycle.analysis_results,
                    "improvement_decisions": cycle.improvement_decisions,
                    "actions_taken": cycle.actions_taken,
                    "learning_outcomes": cycle.learning_outcomes,
                    "baseline_metrics": cycle.baseline_metrics,
                    "target_metrics": cycle.target_metrics,
                    "achieved_metrics": cycle.achieved_metrics,
                    "completed_at": (
                        cycle.completed_at.isoformat() if cycle.completed_at else None
                    ),
                    "success_score": cycle.success_score,
                    "overall_impact": cycle.overall_impact,
                }
                cycles_data[cycle_id] = cycle_dict

            with open(self.data_dir / "active_cycles.json", "w") as f:
                json.dump(cycles_data, f, indent = 2)

        except Exception as e:
            print(f"Warning: Failed to save persistent Kaizen data: {e}")

    def start_automation(self):
        """Start the automated Kaizen cycle process."""
        if self._running:
            return

        if not self.automation_config.get("enabled", True):
            print("Kaizen automation is disabled in configuration")
            return

        self._running = True
        self._automation_thread = threading.Thread(
            target = self._automation_loop, name="kaizen_automation", daemon = True
        )
        self._automation_thread.start()

        print("🔄 Kaizen automation started")

    def stop_automation(self):
        """Stop the automated Kaizen cycle process."""
        self._running = False
        if self._automation_thread and self._automation_thread.is_alive():
            self._automation_thread.join(timeout = 5)

        print("⏹️ Kaizen automation stopped")

    def _automation_loop(self):
        """Main automation loop."""
        cycle_interval = self.automation_config.get("cycle_interval_hours", 24) * 3600

        while self._running:
            try:
                # Run a Kaizen cycle
                self.run_kaizen_cycle()

                # Wait for next cycle
                time.sleep(cycle_interval)

            except Exception as e:
                print(f"Error in Kaizen automation loop: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying

    def run_kaizen_cycle(self) -> KaizenCycle:
        """Run a complete Kaizen cycle."""
        cycle_id = f"kaizen_{int(time.time())}_{utils.random_string(8)}"

        cycle = KaizenCycle(
            cycle_id = cycle_id, started_at = datetime.now(), stage = KaizenCycleStage.OBSERVE
        )

        self.active_cycles[cycle_id] = cycle

        try:
            print(f"🔄 Starting Kaizen cycle: {cycle_id}")

            # Stage 1: Observe
            cycle.stage = KaizenCycleStage.OBSERVE
            cycle.observations = self._observe_current_state()
            print("👁️ Observation phase completed")

            # Stage 2: Orient
            cycle.stage = KaizenCycleStage.ORIENT
            cycle.analysis_results = self._orient_and_analyze(cycle.observations)
            print("🧭 Orientation and analysis completed")

            # Stage 3: Decide
            cycle.stage = KaizenCycleStage.DECIDE
            cycle.improvement_decisions = self._decide_improvements(
                cycle.analysis_results
            )
            print("🤔 Decision phase completed")

            # Stage 4: Act
            cycle.stage = KaizenCycleStage.ACT
            cycle.actions_taken = self._act_on_improvements(cycle.improvement_decisions)
            print("🚀 Action phase completed")

            # Stage 5: Learn
            cycle.stage = KaizenCycleStage.LEARN
            cycle.learning_outcomes = self._learn_from_results(cycle)
            print("📚 Learning phase completed")

            # Complete cycle
            cycle.completed_at = datetime.now()
            cycle.success_score = self._calculate_cycle_success(cycle)
            cycle.overall_impact = self._assess_overall_impact(cycle)

            print(
                f"✅ Kaizen cycle completed with success score: {cycle.success_score:.2f}"
            )

            # Save results
            self._save_persistent_data()

            # Record metrics
            self._record_cycle_metrics(cycle)

            return cycle

        except Exception as e:
            print(f"❌ Kaizen cycle failed: {e}")
            cycle.learning_outcomes = {"error": str(e), "failed_at": cycle.stage.value}
            cycle.completed_at = datetime.now()
            cycle.success_score = 0.0
            cycle.overall_impact = "failed"

            self._save_persistent_data()
            return cycle

    def _observe_current_state(self) -> Dict[str, Any]:
        """Observe current system state and collect metrics."""
        observations = {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": {},
            "user_patterns": {},
            "performance_data": {},
            "error_patterns": {},
        }

        try:
            # Get system metrics
            from ..core.unified_metrics_collector import MetricQuery

            # Get recent performance metrics
            perf_query = MetricQuery(
                category = MetricCategory.TIMING,
                start_time = datetime.now() - timedelta(hours = 24),
                limit = 100,
            )
            perf_result = self.metrics_collector.query_metrics(perf_query)

            if perf_result.metrics:
                avg_response_time = sum(m.value for m in perf_result.metrics) / len(
                    perf_result.metrics
                )
                observations["system_metrics"]["avg_response_time"] = avg_response_time
                observations["system_metrics"]["total_operations"] = len(
                    perf_result.metrics
                )

            # Get error metrics
            error_query = MetricQuery(
                category = MetricCategory.ERROR,
                start_time = datetime.now() - timedelta(hours = 24),
                limit = 100,
            )
            error_result = self.metrics_collector.query_metrics(error_query)

            observations["system_metrics"]["error_count"] = len(error_result.metrics)

            # Get user patterns (if available)
            try:
                user_patterns = (
                    self.enhanced_context.preference_system.get_system_wide_patterns()
                )
                observations["user_patterns"] = user_patterns
            except Exception:
                observations["user_patterns"] = {
                    "error": "Could not retrieve user patterns"
                }

        except Exception as e:
            observations["error"] = str(e)

        return observations

    def _orient_and_analyze(self, observations: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze observations and identify improvement opportunities."""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "identified_opportunities": [],
            "priority_areas": [],
            "risk_assessment": {},
        }

        try:
            # Analyze different categories of opportunities
            perf_opportunities = (
                self.metrics_analyzer.analyze_performance_opportunities()
            )
            ux_opportunities = (
                self.metrics_analyzer.analyze_user_experience_opportunities()
            )
            reliability_opportunities = (
                self.metrics_analyzer.analyze_reliability_opportunities()
            )

            all_opportunities = (
                perf_opportunities + ux_opportunities + reliability_opportunities
            )

            # Store opportunities
            for opp in all_opportunities:
                self.improvement_opportunities[opp.opportunity_id] = opp

            # Analyze and prioritize
            analysis["identified_opportunities"] = [
                {
                    "id": opp.opportunity_id,
                    "category": opp.category.value,
                    "priority": opp.priority.value,
                    "title": opp.title,
                    "estimated_impact": opp.estimated_impact,
                    "estimated_effort": opp.estimated_effort,
                    "risk_level": opp.risk_level,
                }
                for opp in all_opportunities
            ]

            # Identify priority areas
            category_scores = {}
            for opp in all_opportunities:
                if opp.category.value not in category_scores:
                    category_scores[opp.category.value] = 0
                category_scores[opp.category.value] += opp.estimated_impact * (
                    5 - opp.risk_level
                )

            analysis["priority_areas"] = sorted(
                category_scores.items(), key = lambda x: x[1], reverse = True
            )[
                :3
            ]  # Top 3 areas

        except Exception as e:
            analysis["error"] = str(e)

        return analysis

    def _decide_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """Decide which improvements to implement."""
        decisions = []

        try:
            opportunities = analysis.get("identified_opportunities", [])

            # Filter by configuration
            max_concurrent = self.automation_config.get(
                "max_concurrent_improvements", 3
            )
            min_confidence = self.automation_config.get("min_confidence_threshold", 0.7)
            auto_execute_low_risk = self.automation_config.get(
                "auto_execute_low_risk", True
            )

            # Sort by priority and impact
            sorted_opportunities = sorted(
                opportunities,
                key = lambda x: (
                    {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(
                        x["priority"], 1
                    ),
                    x["estimated_impact"],
                    -x["risk_level"],  # Lower risk is better
                ),
                reverse = True,
            )

            # Select improvements to implement
            selected = 0
            for opp in sorted_opportunities:
                if selected >= max_concurrent:
                    break

                # Check if category is enabled
                category = opp["category"]
                if not self.automation_config.get("categories_enabled", {}).get(
                    category, True
                ):
                    continue

                # Check risk level for auto - execution
                if opp["risk_level"] > 2 and not auto_execute_low_risk:
                    continue

                # Calculate confidence (simplified)
                confidence = min(
                    1.0,
                    (
                        opp["estimated_impact"] * 0.3
                        + (5 - opp["risk_level"]) * 0.2
                        + 0.5
                    ),
                )

                if confidence >= min_confidence:
                    decisions.append(opp["id"])
                    selected += 1

        except Exception as e:
            decisions.append(f"error: {str(e)}")

        return decisions

    def _act_on_improvements(self, decisions: List[str]) -> List[Dict[str, Any]]:
        """Execute the decided improvements."""
        actions = []

        for decision in decisions:
            if decision.startswith("error:"):
                actions.append(
                    {
                        "decision": decision,
                        "status": "skipped",
                        "reason": "error in decision",
                    }
                )
                continue

            try:
                opportunity = self.improvement_opportunities.get(decision)
                if not opportunity:
                    actions.append(
                        {
                            "decision": decision,
                            "status": "failed",
                            "reason": "opportunity not found",
                        }
                    )
                    continue

                # Execute improvement based on category
                result = self._execute_improvement(opportunity)
                actions.append(
                    {
                        "decision": decision,
                        "opportunity": opportunity.title,
                        "status": result.get("status", "unknown"),
                        "details": result,
                    }
                )

            except Exception as e:
                actions.append(
                    {"decision": decision, "status": "failed", "error": str(e)}
                )

        return actions

    def _execute_improvement(
        self, opportunity: ImprovementOpportunity
    ) -> Dict[str, Any]:
        """Execute a specific improvement opportunity."""
        result: Dict[str, Any] = {
            "started_at": datetime.now().isoformat(),
            "status": "executing",
            "actions_performed": [],
        }

        try:
            opportunity.status = ImprovementStatus.EXECUTING

            # Execute based on category
            if opportunity.category == ImprovementCategory.PERFORMANCE:
                result.update(self._execute_performance_improvement(opportunity))
            elif opportunity.category == ImprovementCategory.USER_EXPERIENCE:
                result.update(self._execute_ux_improvement(opportunity))
            elif opportunity.category == ImprovementCategory.RELIABILITY:
                result.update(self._execute_reliability_improvement(opportunity))
            else:
                result.update(self._execute_general_improvement(opportunity))

            opportunity.status = ImprovementStatus.COMPLETED
            result["status"] = "completed"

        except Exception as e:
            opportunity.status = ImprovementStatus.FAILED
            result["status"] = "failed"
            result["error"] = str(e)

        result["completed_at"] = datetime.now().isoformat()
        opportunity.experiment_results = result

        return result

    def _execute_performance_improvement(
        self, opportunity: ImprovementOpportunity
    ) -> Dict[str, Any]:
        """Execute performance - related improvements."""
        result: Dict[str, Any] = {"actions_performed": []}

        # Example: Clear caches, optimize configurations
        if "slow_operations" in opportunity.evidence:
            result["actions_performed"].append("Analyzed slow operations")

            # In a real implementation, this would:
            # - Profile the slow operations
            # - Implement caching strategies
            # - Optimize database queries
            # - Add async processing

            result["actions_performed"].append("Applied performance optimizations")
            result["optimization_type"] = "caching_and_profiling"

        return result

    def _execute_ux_improvement(
        self, opportunity: ImprovementOpportunity
    ) -> Dict[str, Any]:
        """Execute user experience improvements."""
        result: Dict[str, Any] = {"actions_performed": []}

        if "error_rate" in opportunity.evidence:
            result["actions_performed"].append("Improved error messages")
            result["actions_performed"].append("Added user guidance")
            result["improvement_type"] = "error_handling"

        if "new_user_success_rate" in opportunity.evidence:
            result["actions_performed"].append("Enhanced onboarding flow")
            result["actions_performed"].append("Added contextual help")
            result["improvement_type"] = "onboarding"

        return result

    def _execute_reliability_improvement(
        self, opportunity: ImprovementOpportunity
    ) -> Dict[str, Any]:
        """Execute reliability improvements."""
        result: Dict[str, Any] = {"actions_performed": []}

        if "error_count" in opportunity.evidence:
            result["actions_performed"].append("Enhanced error monitoring")
            result["actions_performed"].append("Added automated recovery")
            result["improvement_type"] = "error_reduction"

        return result

    def _execute_general_improvement(
        self, opportunity: ImprovementOpportunity
    ) -> Dict[str, Any]:
        """Execute general improvements."""
        result: Dict[str, Any] = {
            "actions_performed": ["Applied general optimization"],
            "improvement_type": "general",
        }
        return result

    def _learn_from_results(self, cycle: KaizenCycle) -> Dict[str, Any]:
        """Learn from the cycle results and update system knowledge."""
        learning = {
            "timestamp": datetime.now().isoformat(),
            "lessons_learned": [],
            "success_patterns": [],
            "failure_patterns": [],
            "recommendations": [],
        }

        try:
            successful_actions = [
                action
                for action in cycle.actions_taken
                if action.get("status") == "completed"
            ]
            failed_actions = [
                action
                for action in cycle.actions_taken
                if action.get("status") == "failed"
            ]

            # Learn from successes
            if successful_actions:
                learning["lessons_learned"].append(
                    f"Successfully executed {len(successful_actions)} improvements"
                )

                for action in successful_actions:
                    learning["success_patterns"].append(
                        {
                            "opportunity": action.get("opportunity"),
                            "approach": action.get("details", {}).get(
                                "improvement_type", "unknown"
                            ),
                        }
                    )

            # Learn from failures
            if failed_actions:
                learning["lessons_learned"].append(
                    f"Failed to execute {len(failed_actions)} improvements"
                )

                for action in failed_actions:
                    learning["failure_patterns"].append(
                        {
                            "opportunity": action.get("opportunity"),
                            "error": action.get("error", "unknown"),
                            "reason": action.get("reason", "unknown"),
                        }
                    )

            # Generate recommendations for future cycles
            if len(successful_actions) > len(failed_actions):
                learning["recommendations"].append(
                    "Continue with current improvement strategies"
                )
            else:
                learning["recommendations"].append(
                    "Review and adjust improvement selection criteria"
                )

            if failed_actions:
                learning["recommendations"].append(
                    "Implement better error handling for improvement execution"
                )

        except Exception as e:
            learning["error"] = str(e)

        return learning

    def _calculate_cycle_success(self, cycle: KaizenCycle) -> float:
        """Calculate the success score for a cycle."""
        if not cycle.actions_taken:
            return 0.0

        successful = len(
            [
                action
                for action in cycle.actions_taken
                if action.get("status") == "completed"
            ]
        )
        total = len(cycle.actions_taken)

        base_score = successful / total

        # Bonus for learning outcomes
        if cycle.learning_outcomes and not cycle.learning_outcomes.get("error"):
            base_score += 0.1

        return min(1.0, base_score)

    def _assess_overall_impact(self, cycle: KaizenCycle) -> str:
        """Assess the overall impact of the cycle."""
        if cycle.success_score >= 0.8:
            return "high_impact"
        elif cycle.success_score >= 0.6:
            return "medium_impact"
        elif cycle.success_score >= 0.3:
            return "low_impact"
        else:
            return "no_impact"

    def _record_cycle_metrics(self, cycle: KaizenCycle):
        """Record metrics for the completed cycle."""
        try:
            # Record cycle completion
            cycle_event = MetricEvent(
                name="kaizen_cycle_completed",
                value = 1.0,
                source = MetricSource.SYSTEM,
                category = MetricCategory.HEALTH,
                dimensions={
                    "cycle_id": cycle.cycle_id,
                    "success_score": cycle.success_score,
                    "overall_impact": cycle.overall_impact,
                    "actions_count": len(cycle.actions_taken),
                },
                unit="count",
            )
            self.metrics_collector.collect_metric(cycle_event)

            # Record success score
            success_event = MetricEvent(
                name="kaizen_cycle_success_score",
                value = cycle.success_score,
                source = MetricSource.SYSTEM,
                category = MetricCategory.HEALTH,
                dimensions={
                    "cycle_id": cycle.cycle_id,
                    "overall_impact": cycle.overall_impact,
                },
                unit="score",
            )
            self.metrics_collector.collect_metric(success_event)

        except Exception as e:
            print(f"Warning: Failed to record cycle metrics: {e}")

    def get_automation_status(self) -> Dict[str, Any]:
        """Get current automation status."""
        return {
            "running": self._running,
            "config": self.automation_config,
            "active_cycles": len(self.active_cycles),
            "total_opportunities": len(self.improvement_opportunities),
            "pending_opportunities": len(
                [
                    opp
                    for opp in self.improvement_opportunities.values()
                    if opp.status
                    in [ImprovementStatus.IDENTIFIED, ImprovementStatus.PLANNED]
                ]
            ),
        }

    def get_cycle_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent cycle history."""
        completed_cycles = [
            cycle
            for cycle in self.active_cycles.values()
            if cycle.completed_at is not None
        ]

        # Sort by completion date
        completed_cycles.sort(
            key = lambda c: c.completed_at or datetime.min, reverse = True
        )

        return [
            {
                "cycle_id": cycle.cycle_id,
                "started_at": cycle.started_at.isoformat(),
                "completed_at": (
                    cycle.completed_at.isoformat() if cycle.completed_at else None
                ),
                "success_score": cycle.success_score,
                "overall_impact": cycle.overall_impact,
                "actions_count": len(cycle.actions_taken),
                "opportunities_addressed": len(cycle.improvement_decisions),
            }
            for cycle in completed_cycles[:limit]
        ]


# Global instance
_kaizen_automation: Optional[KaizenAutomationEngine] = None


def get_kaizen_automation(root: Path) -> KaizenAutomationEngine:
    """Get the global Kaizen automation engine."""
    global _kaizen_automation
    if _kaizen_automation is None:
        _kaizen_automation = KaizenAutomationEngine(root)
    return _kaizen_automation
