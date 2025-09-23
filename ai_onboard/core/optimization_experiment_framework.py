"""
Optimization Experiment Framework (T13) - Systematic optimization testing and \
    validation.

This module provides a comprehensive framework for:
- Designing and running optimization experiments
- A / B testing different optimization strategies
- Statistical analysis of optimization effectiveness
- Automated rollback of failed experiments
- Learning from experiment results to improve future optimizations
"""

import math
import statistics
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .performance_optimizer import get_performance_optimizer
from .unified_metrics_collector import get_unified_metrics_collector


class ExperimentType(Enum):
    """Types of optimization experiments."""

    AB_TEST = "ab_test"  # A / B test between two approaches
    MULTIVARIATE = "multivariate"  # Test multiple variables simultaneously
    SEQUENTIAL = "sequential"  # Sequential testing of improvements
    CANARY = "canary"  # Gradual rollout experiment
    CHAMPION_CHALLENGER = "champion_challenger"  # Challenge existing approach
    FACTORIAL = "factorial"  # Full factorial design
    REGRESSION = "regression"  # Regression testing for performance


class ExperimentStatus(Enum):
    """Status of optimization experiments."""

    DESIGNED = "designed"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class ExperimentOutcome(Enum):
    """Possible experiment outcomes."""

    SUCCESS = "success"  # Improvement confirmed
    FAILURE = "failure"  # No improvement or regression
    INCONCLUSIVE = "inconclusive"  # Not enough data or mixed results
    HARMFUL = "harmful"  # Caused performance regression
    NEUTRAL = "neutral"  # No significant change


class StatisticalSignificance(Enum):
    """Statistical significance levels."""

    NOT_SIGNIFICANT = "not_significant"  # p > 0.05
    MARGINALLY_SIGNIFICANT = "marginally_significant"  # 0.01 < p <= 0.05
    SIGNIFICANT = "significant"  # 0.001 < p <= 0.01
    HIGHLY_SIGNIFICANT = "highly_significant"  # p <= 0.001

@dataclass

class ExperimentMetric:
    """A metric to measure during experiments."""

    name: str
    description: str
    unit: str
    higher_is_better: bool = True
    baseline_value: Optional[float] = None
    target_improvement: Optional[float] = None  # Percentage improvement expected
    measurement_function: Optional[str] = None  # Function name to call for measurement

@dataclass

class ExperimentCondition:
    """A specific condition / treatment in an experiment."""

    condition_id: str
    name: str
    description: str
    configuration: Dict[str, Any]
    implementation_function: Optional[str] = None
    rollback_function: Optional[str] = None
    risk_level: int = 1  # 1 - 5 scale
    expected_impact: float = 0.0  # Expected improvement percentage

@dataclass

class ExperimentDesign:
    """Design specification for an optimization experiment."""

    experiment_id: str
    name: str
    description: str
    experiment_type: ExperimentType

    # Conditions and metrics
    conditions: List[ExperimentCondition]
    metrics: List[ExperimentMetric]
    primary_metric: str  # Name of primary metric

    # Experimental design parameters
    sample_size_per_condition: int = 100
    minimum_runtime_hours: int = 1
    maximum_runtime_hours: int = 24
    confidence_level: float = 0.95
    minimum_detectable_effect: float = 0.05  # 5% minimum improvement to detect

    # Safety parameters
    max_regression_threshold: float = 0.10  # 10% max allowed regression
    early_stopping_enabled: bool = True
    rollback_threshold: float = 0.05  # 5% regression triggers rollback

    # Metadata
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

@dataclass

class ExperimentMeasurement:
    """A single measurement during an experiment."""

    measurement_id: str
    condition_id: str
    metric_name: str
    value: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass

class ExperimentResults:
    """Results of a completed experiment."""

    experiment_id: str
    condition_results: Dict[str, Dict[str, Any]]  # condition_id -> metric results
    statistical_analysis: Dict[str, Any]
    outcome: ExperimentOutcome
    significance: StatisticalSignificance

    # Performance analysis
    best_condition: Optional[str] = None
    improvement_percentage: float = 0.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    p_value: float = 1.0

    # Recommendations
    recommendation: str = ""
    next_experiments: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)

@dataclass

class RunningExperiment:
    """State of a currently running experiment."""

    design: ExperimentDesign
    status: ExperimentStatus
    started_at: datetime
    measurements: List[ExperimentMeasurement] = field(default_factory=list)
    current_condition: Optional[str] = None

    # Runtime state
    samples_collected: Dict[str, int] = field(
        default_factory=dict
    )  # condition_id -> count
    last_analysis: Optional[datetime] = None
    early_stop_triggered: bool = False
    rollback_triggered: bool = False

    # Results (populated when completed)
    results: Optional[ExperimentResults] = None


class StatisticalAnalyzer:
    """Statistical analysis for optimization experiments."""


    def __init__(self):
        self.significance_levels = {
            0.001: StatisticalSignificance.HIGHLY_SIGNIFICANT,
            0.01: StatisticalSignificance.SIGNIFICANT,
            0.05: StatisticalSignificance.MARGINALLY_SIGNIFICANT,
            1.0: StatisticalSignificance.NOT_SIGNIFICANT,
        }


    def analyze_ab_test(
        self, control_values: List[float], treatment_values: List[float]
    ) -> Dict[str, Any]:
        """Analyze A / B test results."""
        if not control_values or not treatment_values:
            return {"error": "Insufficient data for analysis"}

        # Basic statistics
        control_mean = statistics.mean(control_values)
        treatment_mean = statistics.mean(treatment_values)
        control_std = statistics.stdev(control_values) if len(control_values) > 1 else 0
        treatment_std = (
            statistics.stdev(treatment_values) if len(treatment_values) > 1 else 0
        )

        # Effect size (percentage improvement)
        improvement = (
            ((treatment_mean - control_mean) / control_mean) * 100
            if control_mean != 0
            else 0
        )

        # Simple t - test approximation (for demonstration)
        n1, n2 = len(control_values), len(treatment_values)

        if n1 < 2 or n2 < 2:
            p_value = 1.0
        else:
            # Pooled standard error
            pooled_se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

            if pooled_se == 0:
                p_value = 0.0 if control_mean != treatment_mean else 1.0
            else:
                # t - statistic
                t_stat = abs(treatment_mean - control_mean) / pooled_se

                # Simplified p - value estimation (proper implementation would use t - distribution)
                if t_stat > 3.0:
                    p_value = 0.001
                elif t_stat > 2.6:
                    p_value = 0.01
                elif t_stat > 1.96:
                    p_value = 0.05
                else:
                    p_value = 0.1

        # Determine significance
        significance = StatisticalSignificance.NOT_SIGNIFICANT
        for threshold, sig_level in self.significance_levels.items():
            if p_value <= threshold:
                significance = sig_level
                break

        # Confidence interval (simplified)
        margin_of_error = 1.96 * pooled_se if pooled_se > 0 else 0
        ci_lower = (
            improvement - (margin_of_error / control_mean * 100)
            if control_mean != 0
            else 0
        )
        ci_upper = (
            improvement + (margin_of_error / control_mean * 100)
            if control_mean != 0
            else 0
        )

        return {
            "control_mean": control_mean,
            "treatment_mean": treatment_mean,
            "control_std": control_std,
            "treatment_std": treatment_std,
            "improvement_percentage": improvement,
            "p_value": p_value,
            "significance": significance,
            "confidence_interval": (ci_lower, ci_upper),
            "sample_sizes": {"control": n1, "treatment": n2},
            "effect_size": abs(improvement),
            "recommendation": self._generate_recommendation(
                improvement, significance, p_value
            ),
        }


    def analyze_multivariate(
        self, condition_data: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """Analyze multivariate experiment results."""
        if len(condition_data) < 2:
            return {"error": "Need at least 2 conditions for analysis"}

        results = {}
        condition_means = {}

        # Calculate statistics for each condition
        for condition, values in condition_data.items():
            if values:
                condition_means[condition] = statistics.mean(values)
                results[condition] = {
                    "mean": condition_means[condition],
                    "std": statistics.stdev(values) if len(values) > 1 else 0,
                    "count": len(values),
                }

        # Find best performing condition
        best_condition = max(condition_means.items(), key=lambda x: x[1])
        baseline_condition = min(condition_means.items(), key=lambda x: x[1])

        # Calculate overall improvement
        improvement = (
            ((best_condition[1] - baseline_condition[1]) / baseline_condition[1]) * 100
            if baseline_condition[1] != 0
            else 0
        )

        return {
            "condition_results": results,
            "best_condition": best_condition[0],
            "best_mean": best_condition[1],
            "baseline_condition": baseline_condition[0],
            "baseline_mean": baseline_condition[1],
            "overall_improvement": improvement,
            "recommendation": f"Condition '{best_condition[0]}' shows best performance with {improvement:.1f}% improvement",
        }


    def _generate_recommendation(
        self, improvement: float, significance: StatisticalSignificance, p_value: float
    ) -> str:
        """Generate recommendation based on analysis results."""
        if significance == StatisticalSignificance.NOT_SIGNIFICANT:
            return "No statistically significant difference detected. Consider running longer or with larger sample size."

        if improvement > 5:
            return f"Strong positive result: {improvement:.1f}% improvement with {significance.value} significance. Recommend implementation."
        elif improvement > 0:
            return f"Positive result: {improvement:.1f}% improvement with {significance.value} significance. Consider implementation."
        elif improvement > -5:
            return f"Neutral result: {improvement:.1f}% change with {significance.value} significance. No action needed."
        else:
            return f"Negative result: {improvement:.1f}% regression with {significance.value} significance. Recommend rollback."


class OptimizationExperimentFramework:
    """Main framework for optimization experiments."""


    def __init__(self, root: Path):
        self.root = root
        self.data_dir = root / ".ai_onboard" / "optimization_experiments"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Components
        self.statistical_analyzer = StatisticalAnalyzer()
        self.metrics_collector = get_unified_metrics_collector(root)
        self.performance_optimizer = get_performance_optimizer(root)

        # State
        self.running_experiments: Dict[str, RunningExperiment] = {}
        self.experiment_designs: Dict[str, ExperimentDesign] = {}
        self.experiment_results: Dict[str, ExperimentResults] = {}

        # Threading
        self._monitoring_thread: Optional[threading.Thread] = None
        self._monitoring_active = False
        self._executor = ThreadPoolExecutor(
            max_workers=3, thread_name_prefix="experiment"
        )

        # Load existing data
        self._load_persistent_data()


    def _load_persistent_data(self):
        """Load persistent experiment data."""
        try:
            # Load experiment designs
            designs_file = self.data_dir / "experiment_designs.json"
            if designs_file.exists():
                with open(designs_file, "r") as f:
                    data = json.load(f)
                    for exp_id, design_data in data.items():
                        # Convert back to dataclasses
                        design_data["experiment_type"] = ExperimentType(
                            design_data["experiment_type"]
                        )
                        design_data["created_at"] = datetime.fromisoformat(
                            design_data["created_at"]
                        )

                        # Convert conditions
                        conditions = []
                        for cond_data in design_data["conditions"]:
                            conditions.append(ExperimentCondition(**cond_data))
                        design_data["conditions"] = conditions

                        # Convert metrics
                        metrics = []
                        for metric_data in design_data["metrics"]:
                            metrics.append(ExperimentMetric(**metric_data))
                        design_data["metrics"] = metrics

                        self.experiment_designs[exp_id] = ExperimentDesign(
                            **design_data
                        )

            # Load experiment results
            results_file = self.data_dir / "experiment_results.json"
            if results_file.exists():
                with open(results_file, "r") as f:
                    data = json.load(f)
                    for exp_id, result_data in data.items():
                        result_data["outcome"] = ExperimentOutcome(
                            result_data["outcome"]
                        )
                        result_data["significance"] = StatisticalSignificance(
                            result_data["significance"]
                        )
                        self.experiment_results[exp_id] = ExperimentResults(
                            **result_data
                        )

        except Exception as e:
            print(f"Warning: Failed to load persistent experiment data: {e}")


    def _save_persistent_data(self):
        """Save persistent experiment data."""
        try:
            # Save experiment designs
            designs_data = {}
            for exp_id, design in self.experiment_designs.items():
                design_dict = {
                    "experiment_id": design.experiment_id,
                    "name": design.name,
                    "description": design.description,
                    "experiment_type": design.experiment_type.value,
                    "conditions": [
                        {
                            "condition_id": c.condition_id,
                            "name": c.name,
                            "description": c.description,
                            "configuration": c.configuration,
                            "implementation_function": c.implementation_function,
                            "rollback_function": c.rollback_function,
                            "risk_level": c.risk_level,
                            "expected_impact": c.expected_impact,
                        }
                        for c in design.conditions
                    ],
                    "metrics": [
                        {
                            "name": m.name,
                            "description": m.description,
                            "unit": m.unit,
                            "higher_is_better": m.higher_is_better,
                            "baseline_value": m.baseline_value,
                            "target_improvement": m.target_improvement,
                            "measurement_function": m.measurement_function,
                        }
                        for m in design.metrics
                    ],
                    "primary_metric": design.primary_metric,
                    "sample_size_per_condition": design.sample_size_per_condition,
                    "minimum_runtime_hours": design.minimum_runtime_hours,
                    "maximum_runtime_hours": design.maximum_runtime_hours,
                    "confidence_level": design.confidence_level,
                    "minimum_detectable_effect": design.minimum_detectable_effect,
                    "max_regression_threshold": design.max_regression_threshold,
                    "early_stopping_enabled": design.early_stopping_enabled,
                    "rollback_threshold": design.rollback_threshold,
                    "created_by": design.created_by,
                    "created_at": design.created_at.isoformat(),
                    "tags": design.tags,
                }
                designs_data[exp_id] = design_dict

            with open(self.data_dir / "experiment_designs.json", "w") as f:
                json.dump(designs_data, f, indent=2)

            # Save experiment results
            results_data = {}
            for exp_id, result in self.experiment_results.items():
                result_dict = {
                    "experiment_id": result.experiment_id,
                    "condition_results": result.condition_results,
                    "statistical_analysis": result.statistical_analysis,
                    "outcome": result.outcome.value,
                    "significance": result.significance.value,
                    "best_condition": result.best_condition,
                    "improvement_percentage": result.improvement_percentage,
                    "confidence_interval": result.confidence_interval,
                    "p_value": result.p_value,
                    "recommendation": result.recommendation,
                    "next_experiments": result.next_experiments,
                    "lessons_learned": result.lessons_learned,
                }
                results_data[exp_id] = result_dict

            with open(self.data_dir / "experiment_results.json", "w") as f:
                json.dump(results_data, f, indent=2)

        except Exception as e:
            print(f"Warning: Failed to save persistent experiment data: {e}")


    def create_experiment_design(
        self,
        name: str,
        description: str,
        experiment_type: ExperimentType,
        conditions: List[ExperimentCondition],
        metrics: List[ExperimentMetric],
        primary_metric: str,
        **kwargs,
    ) -> ExperimentDesign:
        """Create a new experiment design."""

        experiment_id = f"exp_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        design = ExperimentDesign(
            experiment_id=experiment_id,
            name=name,
            description=description,
            experiment_type=experiment_type,
            conditions=conditions,
            metrics=metrics,
            primary_metric=primary_metric,
            **kwargs,
        )

        self.experiment_designs[experiment_id] = design
        self._save_persistent_data()

        return design


    def start_experiment(self, experiment_id: str) -> bool:
        """Start running an experiment."""
        if experiment_id not in self.experiment_designs:
            print(f"Experiment design {experiment_id} not found")
            return False

        if experiment_id in self.running_experiments:
            print(f"Experiment {experiment_id} is already running")
            return False

        design = self.experiment_designs[experiment_id]

        # Create running experiment
        running_exp = RunningExperiment(
            design=design,
            status=ExperimentStatus.RUNNING,
            started_at=datetime.now(),
            samples_collected={cond.condition_id: 0 for cond in design.conditions},
        )

        self.running_experiments[experiment_id] = running_exp

        # Start monitoring if not already active
        if not self._monitoring_active:
            self._start_monitoring()

        print(f"Started experiment: {design.name} ({experiment_id})")
        return True


    def stop_experiment(self, experiment_id: str, reason: str = "manual_stop") -> bool:
        """Stop a running experiment."""
        if experiment_id not in self.running_experiments:
            print(f"Running experiment {experiment_id} not found")
            return False

        running_exp = self.running_experiments[experiment_id]

        # Analyze results
        results = self._analyze_experiment_results(running_exp)
        running_exp.results = results
        running_exp.status = ExperimentStatus.COMPLETED

        # Save results
        self.experiment_results[experiment_id] = results

        # Remove from running experiments
        del self.running_experiments[experiment_id]

        # Stop monitoring if no more experiments
        if not self.running_experiments and self._monitoring_active:
            self._stop_monitoring()

        self._save_persistent_data()

        print(f"Stopped experiment: {running_exp.design.name} - {reason}")
        print(
            f"Outcome: {results.outcome.value},
                Improvement: {results.improvement_percentage:.2f}%"
        )

        return True


    def record_measurement(
        self,
        experiment_id: str,
        condition_id: str,
        metric_name: str,
        value: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Record a measurement for a running experiment."""
        if experiment_id not in self.running_experiments:
            return False

        running_exp = self.running_experiments[experiment_id]

        measurement = ExperimentMeasurement(
            measurement_id=f"meas_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            condition_id=condition_id,
            metric_name=metric_name,
            value=value,
            timestamp=datetime.now(),
            context=context or {},
        )

        running_exp.measurements.append(measurement)
        running_exp.samples_collected[condition_id] = (
            running_exp.samples_collected.get(condition_id, 0) + 1
        )

        # Check for early stopping
        if running_exp.design.early_stopping_enabled:
            self._check_early_stopping(running_exp)

        return True


    def _analyze_experiment_results(
        self, running_exp: RunningExperiment
    ) -> ExperimentResults:
        """Analyze results of a completed experiment."""
        design = running_exp.design

        # Group measurements by condition and metric
        condition_data: dict[str, dict[str, list[float]]] = {}
        for measurement in running_exp.measurements:
            if measurement.condition_id not in condition_data:
                condition_data[measurement.condition_id] = {}

            if measurement.metric_name not in condition_data[measurement.condition_id]:
                condition_data[measurement.condition_id][measurement.metric_name] = []

            condition_data[measurement.condition_id][measurement.metric_name].append(
                measurement.value
            )

        # Analyze primary metric
        primary_metric_data = {}
        for condition_id, metrics in condition_data.items():
            if design.primary_metric in metrics:
                primary_metric_data[condition_id] = metrics[design.primary_metric]

        # Perform statistical analysis based on experiment type
        if (
            design.experiment_type == ExperimentType.AB_TEST
            and len(primary_metric_data) == 2
        ):
            conditions = list(primary_metric_data.keys())
            control_data = primary_metric_data[conditions[0]]
            treatment_data = primary_metric_data[conditions[1]]

            statistical_analysis = self.statistical_analyzer.analyze_ab_test(
                control_data, treatment_data
            )
        else:
            statistical_analysis = self.statistical_analyzer.analyze_multivariate(
                primary_metric_data
            )

        # Determine outcome
        outcome = self._determine_experiment_outcome(statistical_analysis)

        # Extract key results
        improvement = statistical_analysis.get("improvement_percentage", 0)
        best_condition = statistical_analysis.get("best_condition")
        p_value = statistical_analysis.get("p_value", 1.0)
        significance = statistical_analysis.get(
            "significance", StatisticalSignificance.NOT_SIGNIFICANT
        )
        confidence_interval = statistical_analysis.get(
            "confidence_interval", (0.0, 0.0)
        )

        # Generate recommendations
        recommendation = statistical_analysis.get(
            "recommendation", "No specific recommendation"
        )
        lessons_learned = self._extract_lessons_learned(
            running_exp, statistical_analysis
        )
        next_experiments = self._suggest_next_experiments(
            running_exp, statistical_analysis
        )

        results = ExperimentResults(
            experiment_id=running_exp.design.experiment_id,
            condition_results=condition_data,
            statistical_analysis=statistical_analysis,
            outcome=outcome,
            significance=significance,
            best_condition=best_condition,
            improvement_percentage=improvement,
            confidence_interval=confidence_interval,
            p_value=p_value,
            recommendation=recommendation,
            next_experiments=next_experiments,
            lessons_learned=lessons_learned,
        )

        return results


    def _determine_experiment_outcome(
        self, analysis: Dict[str, Any]
    ) -> ExperimentOutcome:
        """Determine the overall outcome of an experiment."""
        improvement = analysis.get("improvement_percentage", 0)
        significance = analysis.get(
            "significance", StatisticalSignificance.NOT_SIGNIFICANT
        )

        if significance == StatisticalSignificance.NOT_SIGNIFICANT:
            return ExperimentOutcome.INCONCLUSIVE

        if improvement > 5:  # >5% improvement
            return ExperimentOutcome.SUCCESS
        elif improvement > 0:
            return ExperimentOutcome.SUCCESS
        elif improvement > -5:  # Small regression
            return ExperimentOutcome.NEUTRAL
        else:  # >5% regression
            return ExperimentOutcome.HARMFUL


    def _extract_lessons_learned(
        self, running_exp: RunningExperiment, analysis: Dict[str, Any]
    ) -> List[str]:
        """Extract lessons learned from experiment results."""
        lessons = []

        improvement = analysis.get("improvement_percentage", 0)
        significance = analysis.get(
            "significance", StatisticalSignificance.NOT_SIGNIFICANT
        )

        if significance != StatisticalSignificance.NOT_SIGNIFICANT:
            if improvement > 0:
                lessons.append(
                    f"Optimization achieved {improvement:.1f}% improvement with {significance.value} significance"
                )
            else:
                lessons.append(
                    f"Optimization caused {abs(improvement):.1f}% regression with {significance.value} significance"
                )
        else:
            lessons.append(
                "No statistically significant difference detected - may need larger sample size or longer runtime"
            )

        # Sample size lessons
        total_samples = sum(running_exp.samples_collected.values())
        if total_samples < running_exp.design.sample_size_per_condition * len(
            running_exp.design.conditions
        ):
            lessons.append(
                "Experiment ended before reaching target sample size - consider longer runtime"
            )

        return lessons


    def _suggest_next_experiments(
        self, running_exp: RunningExperiment, analysis: Dict[str, Any]
    ) -> List[str]:
        """Suggest follow - up experiments based on results."""
        suggestions = []

        outcome = self._determine_experiment_outcome(analysis)

        if outcome == ExperimentOutcome.SUCCESS:
            suggestions.append(
                "Consider testing more aggressive optimization parameters"
            )
            suggestions.append(
                "Test the optimization on different workloads or conditions"
            )
        elif outcome == ExperimentOutcome.INCONCLUSIVE:
            suggestions.append("Rerun experiment with larger sample size")
            suggestions.append("Extend experiment duration for more data collection")
        elif outcome == ExperimentOutcome.HARMFUL:
            suggestions.append("Investigate root cause of performance regression")
            suggestions.append("Test more conservative optimization parameters")

        return suggestions


    def _check_early_stopping(self, running_exp: RunningExperiment):
        """Check if experiment should be stopped early."""
        # Check if minimum samples collected
        min_samples = max(
            30, running_exp.design.sample_size_per_condition // 4
        )  # At least 25% of target

        total_samples = sum(running_exp.samples_collected.values())
        if total_samples < min_samples:
            return

        # Perform interim analysis
        primary_metric_data: dict[str, list[float]] = {}
        for measurement in running_exp.measurements:
            if measurement.metric_name == running_exp.design.primary_metric:
                if measurement.condition_id not in primary_metric_data:
                    primary_metric_data[measurement.condition_id] = []
                primary_metric_data[measurement.condition_id].append(measurement.value)

        if len(primary_metric_data) >= 2:
            if running_exp.design.experiment_type == ExperimentType.AB_TEST:
                conditions = list(primary_metric_data.keys())
                control_data = primary_metric_data[conditions[0]]
                treatment_data = primary_metric_data[conditions[1]]

                interim_analysis = self.statistical_analyzer.analyze_ab_test(
                    control_data, treatment_data
                )
                improvement = interim_analysis.get("improvement_percentage", 0)

                # Check for harmful regression
                if improvement < -running_exp.design.rollback_threshold * 100:
                    running_exp.rollback_triggered = True
                    print(
                        f"Early stopping triggered: {improvement:.1f}% regression detected"
                    )
                    self.stop_experiment(
                        running_exp.design.experiment_id, "harmful_regression_detected"
                    )


    def _start_monitoring(self):
        """Start experiment monitoring thread."""
        if self._monitoring_active:
            return

        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop, name="experiment_monitor", daemon=True
        )
        self._monitoring_thread.start()


    def _stop_monitoring(self):
        """Stop experiment monitoring thread."""
        self._monitoring_active = False
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5)


    def _monitoring_loop(self):
        """Main monitoring loop for running experiments."""
        while self._monitoring_active:
            try:
                current_time = datetime.now()

                # Check each running experiment
                experiments_to_stop = []

                for exp_id, running_exp in self.running_experiments.items():
                    # Check maximum runtime
                    runtime_hours = (
                        current_time - running_exp.started_at
                    ).total_seconds() / 3600

                    if runtime_hours >= running_exp.design.maximum_runtime_hours:
                        experiments_to_stop.append((exp_id, "maximum_runtime_reached"))

                    # Check if target samples reached
                    total_samples = sum(running_exp.samples_collected.values())
                    target_samples = running_exp.design.sample_size_per_condition * len(
                        running_exp.design.conditions
                    )

                    if (
                        total_samples >= target_samples
                        and runtime_hours >= running_exp.design.minimum_runtime_hours
                    ):
                        experiments_to_stop.append((exp_id, "target_samples_reached"))

                # Stop experiments that meet stopping criteria
                for exp_id, reason in experiments_to_stop:
                    self.stop_experiment(exp_id, reason)

                # Sleep before next check
                time.sleep(60)  # Check every minute

            except Exception as e:
                print(f"Error in experiment monitoring loop: {e}")
                time.sleep(60)


    def get_experiment_status(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an experiment."""
        if experiment_id in self.running_experiments:
            running_exp = self.running_experiments[experiment_id]
            runtime_hours = (
                datetime.now() - running_exp.started_at
            ).total_seconds() / 3600

            return {
                "experiment_id": experiment_id,
                "name": running_exp.design.name,
                "status": running_exp.status.value,
                "runtime_hours": runtime_hours,
                "samples_collected": running_exp.samples_collected,
                "total_samples": sum(running_exp.samples_collected.values()),
                "target_samples": running_exp.design.sample_size_per_condition
                * len(running_exp.design.conditions),
                "measurements_count": len(running_exp.measurements),
                "early_stop_triggered": running_exp.early_stop_triggered,
                "rollback_triggered": running_exp.rollback_triggered,
            }

        elif experiment_id in self.experiment_results:
            result = self.experiment_results[experiment_id]
            return {
                "experiment_id": experiment_id,
                "status": "completed",
                "outcome": result.outcome.value,
                "improvement_percentage": result.improvement_percentage,
                "significance": result.significance.value,
                "best_condition": result.best_condition,
                "recommendation": result.recommendation,
            }

        return None


    def get_all_experiments(self) -> Dict[str, Any]:
        """Get status of all experiments."""
        return {
            "running": {
                exp_id: self.get_experiment_status(exp_id)
                for exp_id in self.running_experiments
            },
            "completed": {
                exp_id: self.get_experiment_status(exp_id)
                for exp_id in self.experiment_results
            },
            "designs": {
                exp_id: design.name
                for exp_id, design in self.experiment_designs.items()
            },
        }

# Global instance
_optimization_experiment_framework: Optional[OptimizationExperimentFramework] = None


def get_optimization_experiment_framework(
    root: Path,
) -> OptimizationExperimentFramework:
    """Get the global optimization experiment framework."""
    global _optimization_experiment_framework
    if _optimization_experiment_framework is None:
        _optimization_experiment_framework = OptimizationExperimentFramework(root)
    return _optimization_experiment_framework
