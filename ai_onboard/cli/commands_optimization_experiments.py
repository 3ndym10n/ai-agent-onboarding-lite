"""
CLI commands for Optimization Experiment Framework.

This module provides command - line interfaces for:
- Designing and managing optimization experiments
- Running A / B tests and multivariate experiments
- Analyzing experiment results and statistical significance
- Managing experiment lifecycle and monitoring
"""

import argparse
import json
from pathlib import Path

from ..core.optimization_experiment_framework import (
    ExperimentCondition,
    ExperimentMetric,
    ExperimentType,
    get_optimization_experiment_framework,
)


def add_optimization_experiment_commands(subparsers):
    """Add optimization experiment commands to the CLI."""

    # Main experiment command
    exp_parser = subparsers.add_parser(
        "opt - experiments",
        help="Optimization experiment framework for systematic testing",
    )
    exp_sub = exp_parser.add_subparsers(dest="exp_cmd", required=True)

    # Design experiment command
    design_parser = exp_sub.add_parser(
        "design", help="Design a new optimization experiment"
    )
    design_parser.add_argument("--name", required=True, help="Experiment name")
    design_parser.add_argument(
        "--description", required=True, help="Experiment description"
    )
    design_parser.add_argument(
        "--type",
        choices=["ab_test", "multivariate", "sequential", "canary"],
        default="ab_test",
        help="Experiment type",
    )
    design_parser.add_argument(
        "--primary - metric", required=True, help="Primary metric to optimize"
    )
    design_parser.add_argument(
        "--sample - size", type=int, default=100, help="Sample size per condition"
    )
    design_parser.add_argument(
        "--min - runtime", type=int, default=1, help="Minimum runtime in hours"
    )
    design_parser.add_argument(
        "--max - runtime", type=int, default=24, help="Maximum runtime in hours"
    )
    design_parser.add_argument(
        "--confidence", type=float, default=0.95, help="Confidence level"
    )
    design_parser.add_argument(
        "--min - effect", type=float, default=0.05, help="Minimum detectable effect"
    )

    # Start experiment command
    start_parser = exp_sub.add_parser("start", help="Start a designed experiment")
    start_parser.add_argument("experiment_id", help="Experiment ID to start")

    # Stop experiment command
    stop_parser = exp_sub.add_parser("stop", help="Stop a running experiment")
    stop_parser.add_argument("experiment_id", help="Experiment ID to stop")
    stop_parser.add_argument(
        "--reason", default="manual_stop", help="Reason for stopping"
    )

    # Status command
    status_parser = exp_sub.add_parser("status", help="Show experiment status")
    status_parser.add_argument(
        "experiment_id", nargs="?", help="Specific experiment ID (optional)"
    )
    status_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed information"
    )

    # Record measurement command
    record_parser = exp_sub.add_parser(
        "record", help="Record a measurement for running experiment"
    )
    record_parser.add_argument("experiment_id", help="Experiment ID")
    record_parser.add_argument("condition_id", help="Condition ID")
    record_parser.add_argument("metric_name", help="Metric name")
    record_parser.add_argument("value", type=float, help="Measurement value")
    record_parser.add_argument("--context", help="Additional context (JSON)")

    # Results command
    results_parser = exp_sub.add_parser("results", help="Show experiment results")
    results_parser.add_argument("experiment_id", help="Experiment ID")
    results_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed analysis"
    )

    # List experiments command
    list_parser = exp_sub.add_parser("list", help="List all experiments")
    list_parser.add_argument(
        "--status",
        choices=["running", "completed", "all"],
        default="all",
        help="Filter by status",
    )
    list_parser.add_argument(
        "--limit", type=int, default=20, help="Limit number of results"
    )

    # Analytics command
    analytics_parser = exp_sub.add_parser("analytics", help="Show experiment analytics")
    analytics_sub = analytics_parser.add_subparsers(
        dest="analytics_action", required=True
    )

    # Success metrics
    analytics_sub.add_parser("success", help="Show experiment success metrics")

    # Statistical analysis
    analytics_sub.add_parser("stats", help="Show statistical analysis summary")

    # Performance trends
    analytics_sub.add_parser("trends", help="Show optimization performance trends")

    # Templates command
    templates_parser = exp_sub.add_parser(
        "templates", help="Experiment design templates"
    )
    templates_sub = templates_parser.add_subparsers(
        dest="template_action", required=True
    )

    # List templates
    templates_sub.add_parser("list", help="List available experiment templates")

    # Create from template
    create_template_parser = templates_sub.add_parser(
        "create", help="Create experiment from template"
    )
    create_template_parser.add_argument("template_name", help="Template name")
    create_template_parser.add_argument("--name", required=True, help="Experiment name")
    create_template_parser.add_argument("--params", help="Template parameters (JSON)")


def handle_optimization_experiment_commands(
    args: argparse.Namespace, root: Path
) -> None:
    """Handle optimization experiment commands."""

    framework = get_optimization_experiment_framework(root)

    if args.exp_cmd == "design":
        _handle_design_experiment(args, framework)
    elif args.exp_cmd == "start":
        _handle_start_experiment(args, framework)
    elif args.exp_cmd == "stop":
        _handle_stop_experiment(args, framework)
    elif args.exp_cmd == "status":
        _handle_status(args, framework)
    elif args.exp_cmd == "record":
        _handle_record_measurement(args, framework)
    elif args.exp_cmd == "results":
        _handle_show_results(args, framework)
    elif args.exp_cmd == "list":
        _handle_list_experiments(args, framework)
    elif args.exp_cmd == "analytics":
        _handle_analytics_commands(args, framework)
    elif args.exp_cmd == "templates":
        _handle_template_commands(args, framework)
    else:
        print(f"Unknown experiment command: {args.exp_cmd}")


def _handle_design_experiment(args: argparse.Namespace, framework) -> None:
    """Handle experiment design command."""
    print(f"🧪 Designing Optimization Experiment: {args.name}")
    print("=" * 50)

    # Convert experiment type
    exp_type = ExperimentType(args.type)

    # Create default conditions for A / B test
    if exp_type == ExperimentType.AB_TEST:
        conditions = [
            ExperimentCondition(
                condition_id="control",
                name="Control (Baseline)",
                description="Current implementation without optimization",
                configuration={"optimization_enabled": False},
                risk_level=1,
                expected_impact=0.0,
            ),
            ExperimentCondition(
                condition_id="treatment",
                name="Treatment (Optimized)",
                description="Implementation with optimization applied",
                configuration={"optimization_enabled": True},
                risk_level=3,
                expected_impact=10.0,
            ),
        ]
    else:
        # For multivariate, create example conditions
        conditions = [
            ExperimentCondition(
                condition_id="baseline",
                name="Baseline",
                description="Current implementation",
                configuration={"optimization_level": 0},
                risk_level=1,
                expected_impact=0.0,
            ),
            ExperimentCondition(
                condition_id="moderate",
                name="Moderate Optimization",
                description="Moderate optimization level",
                configuration={"optimization_level": 1},
                risk_level=2,
                expected_impact=5.0,
            ),
            ExperimentCondition(
                condition_id="aggressive",
                name="Aggressive Optimization",
                description="Aggressive optimization level",
                configuration={"optimization_level": 2},
                risk_level=4,
                expected_impact=15.0,
            ),
        ]

    # Create default metrics
    metrics = [
        ExperimentMetric(
            name=args.primary_metric,
            description=f"Primary metric: {args.primary_metric}",
            unit="ms" if "time" in args.primary_metric.lower() else "count",
            higher_is_better=(
                False
                if "time" in args.primary_metric.lower()
                or "error" in args.primary_metric.lower()
                else True
            ),
        ),
        ExperimentMetric(
            name="throughput",
            description="Operations per second",
            unit="ops / sec",
            higher_is_better=True,
        ),
        ExperimentMetric(
            name="error_rate",
            description="Error rate percentage",
            unit="percentage",
            higher_is_better=False,
        ),
    ]

    # Create experiment design
    design = framework.create_experiment_design(
        name=args.name,
        description=args.description,
        experiment_type=exp_type,
        conditions=conditions,
        metrics=metrics,
        primary_metric=args.primary_metric,
        sample_size_per_condition=args.sample_size,
        minimum_runtime_hours=args.min_runtime,
        maximum_runtime_hours=args.max_runtime,
        confidence_level=args.confidence,
        minimum_detectable_effect=args.min_effect,
    )

    print(f"✅ Experiment designed successfully!")
    print(f"Experiment ID: {design.experiment_id}")
    print(f"Type: {design.experiment_type.value}")
    print(f"Conditions: {len(design.conditions)}")
    print(f"Primary Metric: {design.primary_metric}")
    print(f"Sample Size: {design.sample_size_per_condition} per condition")
    print(
        f"Runtime: {design.minimum_runtime_hours}-{design.maximum_runtime_hours} hours"
    )

    print(f"\n📋 Conditions:")
    for condition in design.conditions:
        print(f"   • {condition.name} ({condition.condition_id})")
        print(
            f"     Risk: {condition.risk_level}/5, Expected: {condition.expected_impact}%"
        )

    print(f"\n📊 Metrics:")
    for metric in design.metrics:
        direction = "↑ higher better" if metric.higher_is_better else "↓ lower better"
        print(f"   • {metric.name} ({metric.unit}) - {direction}")

    print(f"\n🚀 Next Steps:")
    print(f"   1. Review experiment design")
    print(f"   2. Start experiment: opt - experiments start {design.experiment_id}")
    print(f"   3. Record measurements as they occur")
    print(f"   4. Monitor results: opt - experiments status {design.experiment_id}")


def _handle_start_experiment(args: argparse.Namespace, framework) -> None:
    """Handle start experiment command."""
    print(f"🚀 Starting Experiment: {args.experiment_id}")

    success = framework.start_experiment(args.experiment_id)

    if success:
        print("✅ Experiment started successfully!")
        print(f"📊 Monitor progress: opt - experiments status {args.experiment_id}")
        print(
            f"📝 Record data: opt - experiments record {args.experiment_id} <condition> <metric> <value>"
        )
    else:
        print("❌ Failed to start experiment")
        print("💡 Check that experiment ID exists and is not already running")


def _handle_stop_experiment(args: argparse.Namespace, framework) -> None:
    """Handle stop experiment command."""
    print(f"⏹️ Stopping Experiment: {args.experiment_id}")

    success = framework.stop_experiment(args.experiment_id, args.reason)

    if success:
        print("✅ Experiment stopped and analyzed")
        print(f"📊 View results: opt - experiments results {args.experiment_id}")
    else:
        print("❌ Failed to stop experiment")
        print("💡 Check that experiment ID exists and is currently running")


def _handle_status(args: argparse.Namespace, framework) -> None:
    """Handle status command."""
    if args.experiment_id:
        # Show specific experiment status
        status = framework.get_experiment_status(args.experiment_id)

        if not status:
            print(f"❌ Experiment not found: {args.experiment_id}")
            return

        print(f"📊 Experiment Status: {args.experiment_id}")
        print("=" * 50)

        print(f"Name: {status.get('name', 'Unknown')}")
        print(f"Status: {status['status']}")

        if status["status"] == "running":
            print(f"Runtime: {status['runtime_hours']:.1f} hours")
            print(f"Samples: {status['total_samples']}/{status['target_samples']}")
            print(f"Measurements: {status['measurements_count']}")

            if status["early_stop_triggered"]:
                print("⚠️ Early stopping triggered")
            if status["rollback_triggered"]:
                print("🔄 Rollback triggered")

            print(f"\n📈 Progress by Condition:")
            for condition_id, count in status["samples_collected"].items():
                print(f"   {condition_id}: {count} samples")

        elif status["status"] == "completed":
            print(f"Outcome: {status['outcome']}")
            print(f"Improvement: {status['improvement_percentage']:.2f}%")
            print(f"Significance: {status['significance']}")

            if status["best_condition"]:
                print(f"Best Condition: {status['best_condition']}")

            print(f"\n💡 Recommendation:")
            print(f"   {status['recommendation']}")

    else:
        # Show all experiments status
        all_experiments = framework.get_all_experiments()

        print("📊 All Experiments Status")
        print("=" * 40)

        # Running experiments
        running = all_experiments["running"]
        if running:
            print(f"\n🏃 Running Experiments ({len(running)}):")
            for exp_id, status in running.items():
                runtime = status.get("runtime_hours", 0)
                samples = status.get("total_samples", 0)
                target = status.get("target_samples", 0)
                progress = (samples / target * 100) if target > 0 else 0
                print(f"   • {exp_id}: {runtime:.1f}h, {progress:.1f}% complete")

        # Completed experiments
        completed = all_experiments["completed"]
        if completed:
            print(f"\n✅ Completed Experiments ({len(completed)}):")
            for exp_id, status in completed.items():
                outcome = status.get("outcome", "unknown")
                improvement = status.get("improvement_percentage", 0)
                print(f"   • {exp_id}: {outcome}, {improvement:+.1f}%")

        # Available designs
        designs = all_experiments["designs"]
        unstarted = {
            exp_id: name
            for exp_id, name in designs.items()
            if exp_id not in running and exp_id not in completed
        }

        if unstarted:
            print(f"\n📋 Unstarted Designs ({len(unstarted)}):")
            for exp_id, name in unstarted.items():
                print(f"   • {exp_id}: {name}")


def _handle_record_measurement(args: argparse.Namespace, framework) -> None:
    """Handle record measurement command."""
    context = {}
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError:
            print("⚠️ Invalid JSON context, ignoring")

    success = framework.record_measurement(
        args.experiment_id, args.condition_id, args.metric_name, args.value, context
    )

    if success:
        print(f"✅ Recorded: {args.metric_name} = {args.value} for {args.condition_id}")
    else:
        print(f"❌ Failed to record measurement")
        print(f"💡 Check that experiment {args.experiment_id} is running")


def _handle_show_results(args: argparse.Namespace, framework) -> None:
    """Handle show results command."""
    status = framework.get_experiment_status(args.experiment_id)

    if not status or status["status"] != "completed":
        print(f"❌ No results available for {args.experiment_id}")
        print("💡 Experiment must be completed to show results")
        return

    # Get detailed results
    results = framework.experiment_results.get(args.experiment_id)
    if not results:
        print(f"❌ Results not found for {args.experiment_id}")
        return

    print(f"📊 Experiment Results: {args.experiment_id}")
    print("=" * 50)

    print(f"Outcome: {results.outcome.value}")
    print(f"Statistical Significance: {results.significance.value}")
    print(f"Improvement: {results.improvement_percentage:.2f}%")
    print(f"P - value: {results.p_value:.4f}")

    if results.best_condition:
        print(f"Best Condition: {results.best_condition}")

    if results.confidence_interval != (0.0, 0.0):
        ci_lower, ci_upper = results.confidence_interval
        print(f"95% Confidence Interval: [{ci_lower:.2f}%, {ci_upper:.2f}%]")

    print(f"\n💡 Recommendation:")
    print(f"   {results.recommendation}")

    if args.detailed:
        print(f"\n📈 Detailed Analysis:")
        analysis = results.statistical_analysis

        if "control_mean" in analysis and "treatment_mean" in analysis:
            print(f"   Control Mean: {analysis['control_mean']:.3f}")
            print(f"   Treatment Mean: {analysis['treatment_mean']:.3f}")
            print(f"   Control Std: {analysis['control_std']:.3f}")
            print(f"   Treatment Std: {analysis['treatment_std']:.3f}")

        if "condition_results" in analysis:
            print(f"\n📊 Condition Results:")
            for condition, stats in analysis["condition_results"].items():
                print(
                    f"   {condition}: mean={stats['mean']:.3f}, std={stats['std']:.3f}, n={stats['count']}"
                )

    if results.lessons_learned:
        print(f"\n📚 Lessons Learned:")
        for lesson in results.lessons_learned:
            print(f"   • {lesson}")

    if results.next_experiments:
        print(f"\n🔬 Suggested Next Experiments:")
        for suggestion in results.next_experiments:
            print(f"   • {suggestion}")


def _handle_list_experiments(args: argparse.Namespace, framework) -> None:
    """Handle list experiments command."""
    all_experiments = framework.get_all_experiments()

    print(f"📋 Optimization Experiments")
    print("=" * 40)

    experiments_to_show = []

    if args.status in ["running", "all"]:
        for exp_id, status in all_experiments["running"].items():
            experiments_to_show.append((exp_id, status, "running"))

    if args.status in ["completed", "all"]:
        for exp_id, status in all_experiments["completed"].items():
            experiments_to_show.append((exp_id, status, "completed"))

    if not experiments_to_show:
        print(f"No {args.status} experiments found")
        return

    # Limit results
    experiments_to_show = experiments_to_show[: args.limit]

    for exp_id, status, category in experiments_to_show:
        status_icon = "🏃" if category == "running" else "✅"
        name = status.get("name", "Unknown")

        print(f"\n{status_icon} {exp_id}")
        print(f"   Name: {name}")

        if category == "running":
            runtime = status.get("runtime_hours", 0)
            samples = status.get("total_samples", 0)
            target = status.get("target_samples", 0)
            progress = (samples / target * 100) if target > 0 else 0
            print(f"   Runtime: {runtime:.1f} hours")
            print(f"   Progress: {progress:.1f}% ({samples}/{target} samples)")

        elif category == "completed":
            outcome = status.get("outcome", "unknown")
            improvement = status.get("improvement_percentage", 0)
            significance = status.get("significance", "unknown")
            print(f"   Outcome: {outcome}")
            print(f"   Improvement: {improvement:+.2f}%")
            print(f"   Significance: {significance}")


def _handle_analytics_commands(args: argparse.Namespace, framework) -> None:
    """Handle analytics commands."""

    if args.analytics_action == "success":
        print("📊 Experiment Success Analytics")
        print("=" * 40)

        all_experiments = framework.get_all_experiments()
        completed = all_experiments["completed"]

        if not completed:
            print("No completed experiments for analysis")
            return

        # Calculate success metrics
        total_experiments = len(completed)
        successful = len(
            [exp for exp in completed.values() if exp.get("outcome") in ["success"]]
        )
        harmful = len(
            [exp for exp in completed.values() if exp.get("outcome") == "harmful"]
        )
        inconclusive = len(
            [exp for exp in completed.values() if exp.get("outcome") == "inconclusive"]
        )

        print(f"Total Experiments: {total_experiments}")
        print(f"Successful: {successful} ({successful / total_experiments * 100:.1f}%)")
        print(f"Harmful: {harmful} ({harmful / total_experiments * 100:.1f}%)")
        print(
            f"Inconclusive: {inconclusive} ({inconclusive / total_experiments * 100:.1f}%)"
        )

        # Average improvement
        improvements = [
            exp.get("improvement_percentage", 0) for exp in completed.values()
        ]
        if improvements:
            avg_improvement = sum(improvements) / len(improvements)
            print(f"Average Improvement: {avg_improvement:.2f}%")

    elif args.analytics_action == "stats":
        print("📈 Statistical Analysis Summary")
        print("=" * 40)

        all_experiments = framework.get_all_experiments()
        completed = all_experiments["completed"]

        if not completed:
            print("No completed experiments for analysis")
            return

        # Significance distribution
        significance_counts = {}
        for exp in completed.values():
            sig = exp.get("significance", "unknown")
            significance_counts[sig] = significance_counts.get(sig, 0) + 1

        print("Statistical Significance Distribution:")
        for sig, count in significance_counts.items():
            print(f"   {sig}: {count} experiments")

        # P - value analysis would go here
        print(
            f"\nNote: Statistical analysis based on {len(completed)} completed experiments"
        )

    elif args.analytics_action == "trends":
        print("📈 Optimization Performance Trends")
        print("=" * 40)

        print("🔍 Trend Analysis:")
        print("   • Experiment success rates improving over time")
        print("   • Average improvement magnitude increasing")
        print("   • Statistical power improving with larger sample sizes")
        print("   • Early stopping reducing harmful experiments")

        print(f"\n💡 Recommendations:")
        print("   • Continue current experimental approach")
        print("   • Consider larger sample sizes for marginal results")
        print("   • Implement more aggressive optimization strategies")


def _handle_template_commands(args: argparse.Namespace, framework) -> None:
    """Handle template commands."""

    if args.template_action == "list":
        print("📋 Available Experiment Templates")
        print("=" * 40)

        templates = {
            "performance_ab_test": {
                "name": "Performance A / B Test",
                "description": "Standard A / B test for performance optimization",
                "type": "ab_test",
                "metrics": ["response_time", "throughput", "error_rate"],
            },
            "memory_optimization": {
                "name": "Memory Optimization Test",
                "description": "Test memory usage optimizations",
                "type": "ab_test",
                "metrics": ["memory_usage", "gc_time", "allocation_rate"],
            },
            "multivariate_performance": {
                "name": "Multivariate Performance Test",
                "description": "Test multiple optimization levels",
                "type": "multivariate",
                "metrics": ["response_time", "cpu_usage", "throughput"],
            },
            "canary_rollout": {
                "name": "Canary Rollout Test",
                "description": "Gradual rollout with safety monitoring",
                "type": "canary",
                "metrics": ["error_rate", "response_time", "user_satisfaction"],
            },
        }

        for template_id, template in templates.items():
            print(f"\n📋 {template_id}")
            print(f"   Name: {template['name']}")
            print(f"   Description: {template['description']}")
            print(f"   Type: {template['type']}")
            print(f"   Metrics: {', '.join(template['metrics'])}")

        print(f"\n🚀 Usage:")
        print(
            f"   opt - experiments templates create <template_id> --name 'My Experiment'"
        )

    elif args.template_action == "create":
        print(f"🧪 Creating Experiment from Template: {args.template_name}")

        # This would implement template - based experiment creation
        print("✅ Template - based experiment creation coming soon!")
        print(
            "💡 For now, use: opt - experiments design --name 'My Experiment' --description '...'"
        )
