"""
Continuous Improvement CLI Commands - Main Entry Point.

This module provides the main CLI interface for continuous improvement commands,
delegating to specialized sub-modules for specific functionality.
"""

import argparse
import base64
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from ai_onboard.core import utils
from ai_onboard.core.ai_integration.user_preference_learning import InteractionType
from ai_onboard.core.continuous_improvement.adaptive_config_manager import (
    AdaptationTrigger,
    get_adaptive_config_manager,
)
from ai_onboard.core.continuous_improvement.continuous_improvement_analytics import (
    AlertLevel,
    MetricType,
    ReportType,
    get_continuous_improvement_analytics,
)
from ai_onboard.core.continuous_improvement.continuous_improvement_system import (
    LearningType,
    get_continuous_improvement_system,
)
from ai_onboard.core.continuous_improvement.continuous_improvement_validator import (
    get_continuous_improvement_validator,
)
from ai_onboard.core.continuous_improvement.knowledge_base_evolution import (
    KnowledgeQuality,
    KnowledgeSource,
    KnowledgeStatus,
    KnowledgeType,
    get_knowledge_base_evolution,
)
from ai_onboard.core.continuous_improvement.performance_optimizer import (
    get_performance_optimizer,
)
from ai_onboard.core.continuous_improvement.system_health_monitor import (
    get_system_health_monitor,
)

# These imports are used by the main CLI parser but not in this function


def handle_continuous_improvement_commands(
    args: argparse.Namespace, root: Path, unknown: Optional[List[str]] = None
) -> None:
    """Handle continuous improvement commands."""
    # Handle user - prefs as top - level command (quick - path routing)
    if args.cmd == "user - prefs":
        _handle_user_preference_commands(args, root)
        return

    # Check for approval responses in the command line
    if len(sys.argv) >= 4 and sys.argv[2] in ["approve", "reject", "show"]:
        _handle_approval_response(sys.argv[3:], root)
        return

    # Check for review command
    if len(sys.argv) >= 3 and sys.argv[2] == "review":
        _handle_review_command(root)
        return


def _handle_approval_response(args_list: List[str], root: Path) -> None:
    """Handle approval/rejection responses from the chat."""
    system = get_continuous_improvement_system(root)
    action = args_list[0] if args_list else None
    recommendation_id = args_list[1] if len(args_list) > 1 else None

    if action == "approve":
        if recommendation_id == "all":
            # Implement all pending recommendations
            for rec in system.get_improvement_recommendations(
                status="pending", limit=1000
            ):
                result = system.implement_recommendation(rec.recommendation_id)
                if result.get("success", False):
                    print(f"[OK] Approved and implemented: {rec.description}")
                else:
                    print(
                        f"[ERROR] Failed to approve {rec.description}: {result.get('message', 'Unknown error')}"
                    )
        elif recommendation_id:
            result = system.implement_recommendation(recommendation_id)
            if result.get("success", False):
                print(
                    f"[OK] Approved and implemented recommendation '{recommendation_id}'"
                )
            else:
                print(
                    f"[ERROR] Failed to approve recommendation '{recommendation_id}': {result.get('message', 'Unknown error')}"
                )
        else:
            print("Error: Missing recommendation ID for 'approve' command.")
    elif action == "reject":
        if recommendation_id:
            # Find and mark the recommendation as rejected
            found = False
            for rec in system.improvement_recommendations:
                if rec.recommendation_id == recommendation_id:
                    rec.status = "rejected"
                    system._save_improvement_recommendations()
                    print(f"[OK] Rejected recommendation '{recommendation_id}'")
                    found = True
                    break
            if not found:
                print(f"Error: Recommendation '{recommendation_id}' not found.")
        else:
            print("Error: Missing recommendation ID for 'reject' command.")
    elif action == "show":
        if recommendation_id:
            from .commands_continuous_improvement_recommendations import (
                _handle_show_recommendation,
            )

            # Create a dummy args object for _handle_show_recommendation
            temp_args = argparse.Namespace(recommendation_id=recommendation_id)
            _handle_show_recommendation(temp_args, system)
        else:
            print("Error: Missing recommendation ID for 'show' command.")
    else:
        print(f"Error: Unknown approval action: {action}")


def _handle_review_command(root: Path) -> None:
    """Handle the 'review' command to list pending recommendations."""
    system = get_continuous_improvement_system(root)
    pending_recs = system.get_improvement_recommendations(status="pending", limit=1000)

    if not pending_recs:
        print("[INFO] No pending recommendations to review.")
        return

    print("\n=== PENDING IMPROVEMENT RECOMMENDATIONS FOR REVIEW ===")
    for i, rec in enumerate(pending_recs):
        print(f"\n[{i + 1}/{len(pending_recs)}] ID: {rec.recommendation_id}")
        print(f"  Description: {rec.description}")
        print(f"  Rationale: {rec.rationale}")
        print(
            f"  Priority: {rec.priority}/10, Impact: {rec.expected_impact:.1%}, Confidence: {rec.confidence:.1%}"
        )
        print(f"  Action Type: {rec.action_type.value}")
        print(f"  Status: {rec.status}")
    print("\n--- To approve/reject ---")
    print("  Approve: ai_onboard continuous-improvement approve <ID>")
    print("  Reject:  ai_onboard continuous-improvement reject <ID> [--reason '...']")
    print("  Approve All: ai_onboard continuous-improvement approve all")

    # For continuous improvement commands, parse arguments manually from sys.argv
    # This is more reliable than relying on the complex argparse subparser logic
    full_args = sys.argv[1:]  # Skip script name

    if len(full_args) < 2:
        print("Error: No continuous improvement subcommand provided")
        return

    improvement_cmd = full_args[1]  # The subcommand (recommendations, status, etc.)

    args = argparse.Namespace()
    args.improvement_cmd = improvement_cmd

    # Parse the arguments based on the subcommand
    if improvement_cmd == "recommendations":
        if len(full_args) > 2:
            sub_cmd = full_args[2]
            if sub_cmd in ["list", "show", "approve", "reject"]:
                setattr(args, "recommendations_cmd", sub_cmd)
                if len(full_args) > 3:
                    setattr(args, "recommendation_id", full_args[3])
            else:
                # Treat as recommendation_id for show command
                setattr(args, "recommendation_id", sub_cmd)
                setattr(args, "recommendations_cmd", "show")
        else:
            setattr(args, "recommendations_cmd", "list")

    elif improvement_cmd == "status":
        if len(full_args) > 2:
            status_cmd = full_args[2]
            if status_cmd in ["system", "health", "analytics", "validate"]:
                setattr(args, "status_cmd", status_cmd)
            else:
                setattr(args, "status_cmd", "system")  # Default

    # Delegate to modular sub-modules
    if args.improvement_cmd == "learning":
        from .commands_continuous_improvement_learning import _handle_learning_commands

        _handle_learning_commands(args, root)
    elif args.improvement_cmd == "recommendations":
        from .commands_continuous_improvement_recommendations import (
            _handle_recommendations_commands,
        )

        _handle_recommendations_commands(args, root)
    elif args.improvement_cmd == "performance":
        from .commands_continuous_improvement_performance import (
            _handle_performance_commands,
        )

        _handle_performance_commands(args, root)
    elif args.improvement_cmd == "status":
        from .commands_continuous_improvement_status import _handle_status_commands

        _handle_status_commands(args, root)
    elif args.improvement_cmd == "implementation":
        from .commands_continuous_improvement_implementation import (
            _handle_implementation_commands,
        )

        _handle_implementation_commands(args, root)
    else:
        print(f"Error: Unknown continuous improvement command: {args.improvement_cmd}")
        return


def _handle_simple_status(root: Path) -> None:
    """Simple status check that shows the current state of continuous improvement data."""

    print("AI Onboard Continuous Improvement Status")
    print("=" * 50)

    ci_data_dir = root / ".ai_onboard"

    if ci_data_dir.exists():
        print("Continuous Improvement Data Directory: Found")

        # Check for various data files
        files_to_check = [
            "learning_events.jsonl",
            "improvement_recommendations.json",
            "user_profiles.json",
            "system_health.jsonl",
            "performance_data.jsonl",
        ]

        for file_name in files_to_check:
            file_path = ci_data_dir / file_name
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"  {file_name}: {size:,}", "bytes")
            else:
                print(f"  {file_name}: Missing")
    else:
        print("Continuous Improvement Data Directory: Missing")
        print("   Run 'python -m ai_onboard validate' to initialize")

    print("\nSystem Information:")
    print(f"  Root Directory: {root}")
    print(f"  Python Version: {__import__('sys').version}")
    print(f"  Platform: {__import__('sys').platform}")


def _handle_user_preference_commands(
    args: argparse.Namespace, root: Path
) -> Dict[str, Any]:
    """Handle user preference commands."""
    from ..core.ai_integration.user_preference_learning import (
        get_user_preference_learning_system,
    )

    psys = get_user_preference_learning_system(root)
    pcmd = getattr(args, "prefs_cmd", None)

    if pcmd == "record":
        try:
            context = json.loads(getattr(args, "context", "") or "{}")
        except Exception:
            print('{"error":"invalid context JSON"}')
            return {"error": "invalid context JSON"}

        try:
            outcome = json.loads(getattr(args, "outcome", "") or "{}")
        except Exception:
            print('{"error":"invalid outcome JSON"}')
            return {}

        interaction_id = psys.record_user_interaction(
            user_id=args.user,
            interaction_type=args.type,
            context=context,
            duration=getattr(args, "duration", None),
            outcome=outcome,
            satisfaction_score=getattr(args, "satisfaction", None),
            feedback=getattr(args, "feedback", None),
        )
        print(json.dumps({"interaction_id": interaction_id}))
        return {"interaction_id": interaction_id}
    elif pcmd == "summary":
        print(json.dumps(psys.get_user_profile_summary(args.user)))
        return psys.get_user_profile_summary(args.user)
    else:
        print('{"error":"unknown user - prefs subcommand"}')
        return {"error": "unknown user - prefs subcommand"}


def _coerce_scalar(value: str) -> Union[bool, int, float, str]:
    """Coerce a string scalar to bool / int / float when possible,
    else return as - is.
    """
    lower = value.strip().lower()
    if lower in ("true", "false"):
        return lower == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _parse_kv_pairs(text: str) -> Dict[str, Any]:
    """Parse simple key =         value[,key = value] pairs into a dict with light type coercion."""
    result: Dict[str, Any] = {}
    if not text:
        return result
    for pair in text.split(","):
        if not pair:
            continue
        if "=" not in pair:
            # Skip malformed segment
            continue
        key, val = pair.split("=", 1)
        result[key.strip()] = _coerce_scalar(val.strip())
    return result


def _parse_json_source(
    raw: Optional[str] = None,
    file: Optional[str] = None,
    b64: Optional[str] = None,
    allow_kv: bool = True,
) -> Dict[str, Any]:
    """Parse structured input from one of: file, base64, raw JSON string, or key =         value pairs.

    Precedence: file > base64 > raw.
    Returns an empty dict when no input provided.
    """
    try:
        if file:
            p = Path(file)
            if not p.exists():
                print(f"❌ File not found: {file}")
                return {}
            return cast(Dict[str, Any], json.loads(p.read_text(encoding="utf - 8")))

        if b64:
            decoded = base64.b64decode(b64).decode("utf - 8")
            return cast(Dict[str, Any], json.loads(decoded))

        if raw:
            raw = raw.strip()
            if raw.startswith("{") and raw.endswith("}"):
                return cast(Dict[str, Any], json.loads(raw))
            if allow_kv:
                return _parse_kv_pairs(raw)
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return {}
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error: {e}")
        return {}


def _handle_learning_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle learning - related commands."""
    system = get_continuous_improvement_system(root)

    if args.learning_action == "record":
        _handle_record_learning(args, system)
    elif args.learning_action == "summary":
        _handle_learning_summary(args, system)
    elif args.learning_action == "events":
        _handle_learning_events(args, system)
    else:
        print(f"Unknown learning action: {args.learning_action}")


def _handle_record_learning(args: argparse.Namespace, system) -> None:
    """Handle recording a learning event."""
    try:
        learning_type = LearningType(args.learning_type)
    except ValueError:
        print(f"Invalid learning type: {args.learning_type}")
        print(f"Available types: {', '.join([lt.value for lt in LearningType])}")
        return

    # Parse context and outcome from flexible inputs
    context = _parse_json_source(
        raw=getattr(args, "context", None),
        file=getattr(args, "context_file", None),
        b64=getattr(args, "context_b64", None),
        allow_kv=True,
    )
    outcome = _parse_json_source(
        raw=getattr(args, "outcome", None),
        file=getattr(args, "outcome_file", None),
        b64=getattr(args, "outcome_b64", None),
        allow_kv=True,
    )

    # Record the learning event
    event_id = system.record_learning_event(
        learning_type=learning_type,
        context=context,
        outcome=outcome,
        confidence=args.confidence or 0.8,
        impact_score=args.impact or 0.5,
        source=args.source or "manual",
    )

    print(f"✅ Learning event recorded: {event_id}")
    print(f"Type: {learning_type.value}")
    print(f"Confidence: {args.confidence or 0.8}")
    print(f"Impact Score: {args.impact or 0.5}")


def _handle_learning_summary(args: argparse.Namespace, system) -> None:
    """Handle learning summary command."""
    days = args.days or 7
    summary = system.get_learning_summary(days)

    if summary["status"] == "no_data":
        print(f"📊 No learning events found for the last {days} days")
        return

    print(f"📊 Learning Summary (Last {days} days)")
    print("=" * 40)
    print(f"Total Events: {summary['total_events']}")
    print(f"Average Confidence: {summary['avg_confidence']:.2f}")
    print(f"Average Impact Score: {summary['avg_impact_score']:.2f}")

    print("\nEvents by Type:")
    for event_type, count in summary["events_by_type"].items():
        print(f"  {event_type}: {count}")

    print("\nTop Sources:")
    for source_info in summary["top_sources"][:5]:
        print(f"  {source_info['source']}: {source_info['count']} events")

    if summary.get("recent_events"):
        print("\nRecent Events:")
        for event in summary["recent_events"][-3:]:
            print(
                f"  {event['timestamp']}: {event['learning_type']} (confidence: {event['confidence']:.2f})"
            )


def _handle_learning_events(args: argparse.Namespace, system) -> None:
    """Handle listing learning events."""
    # This would read and display learning events from the JSONL file
    print("📋 Learning Events")
    print("=" * 20)
    print("Learning events listing not yet implemented in detail.")


def _handle_recommendations_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle recommendations - related commands."""
    system = get_continuous_improvement_system(root)

    if args.recommendations_action == "list":
        _handle_list_recommendations(args, system)
    elif args.recommendations_action == "show":
        _handle_show_recommendation(args, system)
    elif args.recommendations_action == "approve":
        _handle_approve_recommendation(args, system)
    elif args.recommendations_action == "reject":
        _handle_reject_recommendation(args, system)
    else:
        print(f"Unknown recommendations action: {args.recommendations_action}")


def _handle_list_recommendations(args: argparse.Namespace, system) -> None:
    """Handle listing improvement recommendations."""
    limit = getattr(args, "limit", None) or 10
    priority_threshold = getattr(args, "priority", None) or 5
    status = getattr(args, "status", None) or "pending"

    recommendations = system.get_improvement_recommendations(
        limit=limit, priority_threshold=priority_threshold, status=status
    )

    if not recommendations:
        print(
            f"📋 No {status} recommendations found with priority >= {priority_threshold}"
        )
        return

    print(f"📋 Improvement Recommendations ({status})")
    print("=" * 50)

    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec.description}")
        print(f"   Action: {rec.action_type.value}")
        print(f"   Priority: {rec.priority}/10")
        print(f"   Expected Impact: {rec.expected_impact:.2f}")
        print(f"   Confidence: {rec.confidence:.2f}")
        print(f"   Effort: {rec.implementation_effort}/10")
        print(f"   ID: {rec.recommendation_id}")
        print()


def _handle_show_recommendation(args: argparse.Namespace, system) -> None:
    """Handle showing a specific recommendation."""
    recommendation_id = args.recommendation_id

    # Find the recommendation
    recommendation = None
    for rec in system.improvement_recommendations:
        if rec.recommendation_id == recommendation_id:
            recommendation = rec
            break

    if not recommendation:
        print(f"❌ Recommendation {recommendation_id} not found")
        return

    print(f"📋 Recommendation: {recommendation_id}")
    print("=" * 50)
    print(f"Description: {recommendation.description}")
    print(f"Action Type: {recommendation.action_type.value}")
    print(f"Rationale: {recommendation.rationale}")
    print(f"Priority: {recommendation.priority}/10")
    print(f"Expected Impact: {recommendation.expected_impact:.2f}")
    print(f"Confidence: {recommendation.confidence:.2f}")
    print(f"Implementation Effort: {recommendation.implementation_effort}/10")
    print(f"Status: {recommendation.status}")
    print(f"Created: {recommendation.created_at}")

    if recommendation.dependencies:
        print(f"Dependencies: {', '.join(recommendation.dependencies)}")


def _handle_approve_recommendation(args: argparse.Namespace, system) -> None:
    """Handle approving a recommendation."""
    recommendation_id = args.recommendation_id

    # Find and update the recommendation
    for rec in system.improvement_recommendations:
        if rec.recommendation_id == recommendation_id:
            rec.status = "approved"
            system._save_improvement_recommendations()
            print(f"✅ Recommendation {recommendation_id} approved")
            return

    print(f"❌ Recommendation {recommendation_id} not found")


def _handle_reject_recommendation(args: argparse.Namespace, system) -> None:
    """Handle rejecting a recommendation."""
    recommendation_id = args.recommendation_id

    # Find and update the recommendation
    for rec in system.improvement_recommendations:
        if rec.recommendation_id == recommendation_id:
            rec.status = "rejected"
            system._save_improvement_recommendations()
            print(f"❌ Recommendation {recommendation_id} rejected")
            return

    print(f"❌ Recommendation {recommendation_id} not found")


def _handle_implement_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle implementation commands."""
    system = get_continuous_improvement_system(root)

    recommendation_id = args.recommendation_id
    result = system.implement_recommendation(recommendation_id)

    if result["status"] == "error":
        print(f"❌ Implementation failed: {result['message']}")
    else:
        print(f"✅ Implementation successful: {result['message']}")


def _handle_status_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle status commands."""
    system = get_continuous_improvement_system(root)

    print("📊 Continuous Improvement System Status")
    print("=" * 45)

    # Get learning summary
    learning_summary = system.get_learning_summary(7)
    if learning_summary["status"] == "success":
        print(f"Learning Events (7 days): {learning_summary['total_events']}")
        print(f"Average Confidence: {learning_summary['avg_confidence']:.2f}")
    else:
        print("Learning Events (7 days): No data")

    # Get health summary
    health_summary = system.get_system_health_summary(7)
    if health_summary["status"] == "success":
        print(f"System Health Score: {health_summary['avg_performance_score']:.2f}")
        print(f"User Satisfaction: {health_summary['avg_user_satisfaction']:.2f}")
    else:
        print("System Health: No data")

    # Get recommendations count
    pending_recs = len(
        [r for r in system.improvement_recommendations if r.status == "pending"]
    )
    approved_recs = len(
        [r for r in system.improvement_recommendations if r.status == "approved"]
    )
    implemented_recs = len(
        [r for r in system.improvement_recommendations if r.status == "implemented"]
    )

    print(
        f"Recommendations: {pending_recs} pending, "
        f"{approved_recs} approved, {implemented_recs} implemented"
    )

    # Get user profiles count
    print(f"User Profiles: {len(system.user_profiles)}")


def _handle_performance_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle performance optimization commands."""
    optimizer = get_performance_optimizer(root)

    if args.performance_action == "monitor":
        _handle_performance_monitor(args, optimizer)
    elif args.performance_action == "opportunities":
        _handle_performance_opportunities(args, optimizer)
    elif args.performance_action == "optimize":
        _handle_performance_optimize(args, optimizer)
    elif args.performance_action == "summary":
        _handle_performance_summary(args, optimizer)
    elif args.performance_action == "profiles":
        _handle_performance_profiles(args, optimizer)
    else:
        print(f"Unknown performance action: {args.performance_action}")


def _handle_performance_monitor(args: argparse.Namespace, optimizer) -> None:
    """Handle performance monitoring commands."""
    if args.monitor_action == "start":
        optimizer.start_monitoring()
        print("✅ Performance monitoring started")
    elif args.monitor_action == "stop":
        optimizer.stop_monitoring()
        print("✅ Performance monitoring stopped")
    elif args.monitor_action == "status":
        status = "active" if optimizer.monitoring_active else "inactive"
        print(f"📊 Performance monitoring status: {status}")
        print(f"Snapshots collected: {len(optimizer.performance_snapshots)}")
        print(
            f"Optimization opportunities: {len(optimizer.optimization_opportunities)}"
        )


def _handle_performance_opportunities(args: argparse.Namespace, optimizer) -> None:
    """Handle performance optimization opportunities."""
    limit = args.limit or 10
    min_confidence = args.confidence or 0.5
    max_risk = args.risk or 7

    opportunities = optimizer.get_optimization_opportunities(
        limit=limit, min_confidence=min_confidence, max_risk=max_risk
    )

    if not opportunities:
        print(
            f"📋 No optimization opportunities found with confidence >= {min_confidence} and \
                risk <= {max_risk}"
        )
        return

    print(f"📋 Performance Optimization Opportunities")
    print("=" * 50)

    for i, opp in enumerate(opportunities, 1):
        print(f"{i}. {opp.description}")
        print(f"   Type: {opp.optimization_type.value}")
        print(f"   Expected Improvement: {opp.expected_improvement:.1%}")
        print(f"   Confidence: {opp.confidence:.2f}")
        print(f"   Implementation Effort: {opp.implementation_effort}/10")
        print(f"   Risk Level: {opp.risk_level}/10")
        print(f"   ID: {opp.opportunity_id}")
        print()


def _handle_performance_optimize(args: argparse.Namespace, optimizer) -> None:
    """Handle performance optimization implementation."""
    opportunity_id = args.opportunity_id

    try:
        result = optimizer.implement_optimization(opportunity_id)

        if result.success:
            print(f"✅ Optimization implemented successfully!")
            print(f"Improvement: {result.improvement_percentage:.1f}%")
            print(f"Implementation Time: {result.implementation_time:.2f}s")
        else:
            print(f"❌ Optimization implementation failed")

    except ValueError as e:
        print(f"❌ {str(e)}")


def _handle_performance_summary(args: argparse.Namespace, optimizer) -> None:
    """Handle performance summary."""
    hours = args.hours or 24

    summary = optimizer.get_performance_summary(hours)

    if summary["status"] == "no_data":
        print(f"📊 No performance data found for the last {hours} hours")
        return

    print(f"📊 Performance Summary (Last {hours} hours)")
    print("=" * 40)
    print(f"Total Snapshots: {summary['total_snapshots']}")

    print("\nMetrics:")
    for metric_name, metric_data in summary["metrics"].items():
        print(f"  {metric_name}:")
        print(f"    Average: {metric_data['average']:.2f}")
        print(f"    Min: {metric_data['min']:.2f}")
        print(f"    Max: {metric_data['max']:.2f}")
        print(
            f"    Trend: {metric_data['trend']['direction']} (severity: {metric_data['trend']['severity']:.2f})"
        )

    # Get optimization effectiveness
    effectiveness = optimizer.get_optimization_effectiveness(7)
    if effectiveness["status"] == "success":
        print(f"\nOptimization Effectiveness (7 days):")
        print(f"  Total Optimizations: {effectiveness['total_optimizations']}")
        print(f"  Success Rate: {effectiveness['success_rate']:.1%}")
        print(f"  Average Improvement: {effectiveness['average_improvement']:.1f}%")


def _handle_performance_profiles(args: argparse.Namespace, optimizer) -> None:
    """Handle performance profiles."""
    if args.profiles_action == "list":
        print("📋 Performance Profiles")
        print("=" * 25)

        if not optimizer.performance_profiles:
            print("No performance profiles found")
            return

        for profile_id, profile in optimizer.performance_profiles.items():
            print(f"Profile: {profile.operation_name}")
            print(f"  ID: {profile_id}")
            print(f"  Last Updated: {profile.last_updated}")
            print(f"  Current Metrics:")
            for metric, value in profile.current_metrics.items():
                print(f"    {metric.value}: {value:.2f}")
            print()

    elif args.profiles_action == "show":
        profile_id = args.profile_id

        if profile_id not in optimizer.performance_profiles:
            print(f"❌ Profile {profile_id} not found")
            return

        profile = optimizer.performance_profiles[profile_id]

        print(f"📋 Performance Profile: {profile.operation_name}")
        print("=" * 40)
        print(f"Profile ID: {profile_id}")
        print(f"Last Updated: {profile.last_updated}")

        print("\nBaseline Metrics:")
        for metric, value in profile.baseline_metrics.items():
            print(f"  {metric.value}: {value:.2f}")

        print("\nCurrent Metrics:")
        for metric, value in profile.current_metrics.items():
            print(f"  {metric.value}: {value:.2f}")

        print("\nPerformance Trends:")
        for metric, values in profile.performance_trends.items():
            if values:
                trend = optimizer._calculate_trend(values)
                print(
                    f"  {metric.value}: {trend['direction']} (severity: {trend['severity']:.2f})"
                )


def _handle_config_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle adaptive configuration commands."""
    config_manager = get_adaptive_config_manager(root)

    if args.config_action == "get":
        _handle_config_get(args, config_manager)
    elif args.config_action == "set":
        _handle_config_set(args, config_manager)
    elif args.config_action == "list":
        _handle_config_list(args, config_manager)
    elif args.config_action == "adapt":
        _handle_config_adapt(args, config_manager)
    elif args.config_action == "profiles":
        _handle_config_profiles(args, config_manager)
    elif args.config_action == "analytics":
        _handle_config_analytics(args, config_manager)
    else:
        print(f"Unknown config action: {args.config_action}")


def _handle_config_get(args: argparse.Namespace, config_manager) -> None:
    """Handle getting configuration values."""
    if args.setting_key:
        value = config_manager.get_setting(args.setting_key)
        if value is not None:
            print(f"📋 {args.setting_key}: {value}")
        else:
            print(f"❌ Setting '{args.setting_key}' not found")
    else:
        print("❌ Setting key is required")


def _handle_config_set(args: argparse.Namespace, config_manager) -> None:
    """Handle setting configuration values."""
    if not args.setting_key or args.value is None:
        print("❌ Setting key and value are required")
        return

    # Convert value to appropriate type
    value = args.value
    if args.setting_key in config_manager.current_config:
        setting = config_manager.current_config[args.setting_key]
        if isinstance(setting.default_value, int):
            try:
                value = int(args.value)
            except ValueError:
                print(f"❌ Value must be an integer for {args.setting_key}")
                return
        elif isinstance(setting.default_value, bool):
            if args.value.lower() in ["true", "1", "yes", "on"]:
                value = True
            elif args.value.lower() in ["false", "0", "no", "off"]:
                value = False
            else:
                print(f"❌ Value must be true / false for {args.setting_key}")
                return

    success = config_manager.set_setting(
        args.setting_key,
        value,
        reason=args.reason or "Manual configuration change",
        trigger=AdaptationTrigger.MANUAL_OVERRIDE,
        confidence=1.0,
        expected_impact=0.5,
    )

    if success:
        print(f"✅ Set {args.setting_key} = {value}")
    else:
        print(f"❌ Failed to set {args.setting_key} = {value}")


def _handle_config_list(args: argparse.Namespace, config_manager) -> None:
    """Handle listing configuration settings."""
    category_filter = args.category

    print("📋 Configuration Settings")
    print("=" * 30)

    for key, setting in config_manager.current_config.items():
        if category_filter and setting.category.value != category_filter:
            continue

        print(f"{key}: {setting.value}")
        print(f"  Category: {setting.category.value}")
        print(f"  Description: {setting.description}")
        print(f"  Adaptive: {setting.adaptive}")
        print(f"  Last Modified: {setting.last_modified}")
        print()


def _handle_config_adapt(args: argparse.Namespace, config_manager) -> None:
    """Handle configuration adaptation."""
    # Parse context (flexible sources)
    context = _parse_json_source(
        raw=getattr(args, "context", None),
        file=getattr(args, "context_file", None),
        b64=getattr(args, "context_b64", None),
        allow_kv=True,
    )

    # Apply default context if none provided
    if not context:
        context = {
            "user_satisfaction": 0.8,
            "interaction_frequency": 15,
            "avg_response_time": 3.0,
            "error_rate": 0.05,
            "project_type": "generic",
        }

    changes = config_manager.adapt_configuration(
        context, trigger=AdaptationTrigger.USAGE_PATTERN_CHANGE
    )

    if changes:
        print(f"✅ Applied {len(changes)} configuration adaptations:")
        for change in changes:
            print(f"  {change.setting_key}: {change.old_value} → {change.new_value}")
            print(f"    Reason: {change.reason}")
    else:
        print("📋 No configuration adaptations applied")


def _handle_config_profiles(args: argparse.Namespace, config_manager) -> None:
    """Handle configuration profiles."""
    if args.profiles_action == "list":
        print("📋 Configuration Profiles")
        print("=" * 25)

        if not config_manager.config_profiles:
            print("No configuration profiles found")
            return

        for profile_id, profile in config_manager.config_profiles.items():
            print(f"Profile: {profile.name}")
            print(f"  ID: {profile_id}")
            print(f"  Description: {profile.description}")
            print(f"  Usage Count: {profile.usage_count}")
            print(f"  Last Used: {profile.last_used}")
            print()

    elif args.profiles_action == "create":
        name = args.profile_name
        description = args.profile_description or f"Profile for {name}"

        # Parse context (flexible sources)
        context = _parse_json_source(
            raw=getattr(args, "context", None),
            file=getattr(args, "context_file", None),
            b64=getattr(args, "context_b64", None),
            allow_kv=True,
        )

        profile_id = config_manager.create_configuration_profile(
            name, description, context
        )
        print(f"✅ Created configuration profile: {profile_id}")

    elif args.profiles_action == "apply":
        profile_id = args.profile_id

        success = config_manager.apply_configuration_profile(profile_id)
        if success:
            print(f"✅ Applied configuration profile: {profile_id}")
        else:
            print(f"❌ Profile {profile_id} not found")


def _handle_config_analytics(args: argparse.Namespace, config_manager) -> None:
    """Handle configuration analytics."""
    days = args.days or 7

    analytics = config_manager.get_configuration_analytics(days)

    if analytics["status"] == "no_data":
        print(f"📊 No configuration changes found for the last {days} days")
        return

    print(f"📊 Configuration Analytics (Last {days} days)")
    print("=" * 45)
    print(f"Total Changes: {analytics['total_changes']}")
    print(f"Reverted Changes: {analytics['reverted_changes']}")
    print(f"Reversion Rate: {analytics['reversion_rate']:.1%}")

    print("\nChanges by Trigger:")
    for trigger, count in analytics["changes_by_trigger"].items():
        print(f"  {trigger}: {count}")

    print("\nMost Changed Settings:")
    for setting, count in analytics["most_changed_settings"]:
        print(f"  {setting}: {count} changes")


def _handle_record_interaction(args: argparse.Namespace, preference_system) -> None:
    """Handle recording user interactions."""
    try:
        interaction_type = InteractionType(args.type)
    except ValueError:
        print(f"Invalid interaction type: {args.type}")
        print(f"Available types: {', '.join([it.value for it in InteractionType])}")
        return

    # Parse context / outcome (flexible sources)
    context = _parse_json_source(
        raw=getattr(args, "context", None),
        file=getattr(args, "context_file", None),
        b64=getattr(args, "context_b64", None),
        allow_kv=True,
    )
    outcome_obj = _parse_json_source(
        raw=getattr(args, "outcome", None),
        file=getattr(args, "outcome_file", None),
        b64=getattr(args, "outcome_b64", None),
        allow_kv=True,
    )
    outcome = outcome_obj if outcome_obj else None

    # Record the interaction
    interaction_id = preference_system.record_user_interaction(
        user_id=args.user,
        interaction_type=interaction_type,
        context=context,
        duration=args.duration,
        outcome=outcome,
        satisfaction_score=args.satisfaction,
        feedback=args.feedback,
    )

    print(f"✅ User interaction recorded: {interaction_id}")
    print(f"User: {args.user}")
    print(f"Type: {interaction_type.value}")
    if args.satisfaction is not None:
        print(f"Satisfaction: {args.satisfaction}")


def _handle_user_summary(args: argparse.Namespace, preference_system) -> None:
    """Handle user summary command."""
    user_id = args.user

    # Get user profile summary
    try:
        summary = preference_system.get_user_profile_summary(user_id)
        print(f"📊 User Profile Summary for {user_id}")
        print("=" * 50)
        print(summary)
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error: {e}")


def _handle_user_recommendations(args: argparse.Namespace, preference_system) -> None:
    """Handle user recommendations command."""
    user_id = args.user

    # Get user recommendations
    try:
        recommendations = preference_system.get_user_recommendations(user_id)
        print(f"🎯 Recommendations for {user_id}")
        print("=" * 50)
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print(
                "No recommendations available yet. Record more interactions to get personalized suggestions."
            )
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error: {e}")


def _handle_user_preferences(args: argparse.Namespace, preference_system) -> None:
    """Handle user preferences commands."""
    if args.prefs_action == "list":
        _handle_list_preferences(args, preference_system)
    elif args.prefs_action == "get":
        _handle_get_preference(args, preference_system)
    else:
        print(f"Unknown preferences action: {args.prefs_action}")


def _handle_list_preferences(args: argparse.Namespace, preference_system) -> None:
    """Handle listing user preferences."""
    user_id = args.user_id
    category_filter = args.category

    preferences = preference_system.get_user_preferences(user_id)

    if not preferences:
        print(f"📋 No preferences found for user {user_id}")
        return

    print(f"📋 User Preferences: {user_id}")
    print("=" * 30)

    for pref_key, preference in preferences.items():
        if category_filter and preference.category.value != category_filter:
            continue

        print(f"{preference.preference_key}: {preference.preference_value}")
        print(f"  Category: {preference.category.value}")
        print(f"  Confidence: {preference.confidence:.2f}")
        print(f"  Evidence Count: {preference.evidence_count}")
        print(f"  Last Updated: {preference.last_updated}")
        print()


def _handle_get_preference(args: argparse.Namespace, preference_system) -> None:
    """Handle getting a specific user preference."""
    user_id = args.user_id
    preference_key = args.preference_key

    preferences = preference_system.get_user_preferences(user_id)

    # Find the preference
    preference = None
    for pref in preferences.values():
        if pref.preference_key == preference_key:
            preference = pref
            break

    if not preference:
        print(f"❌ Preference '{preference_key}' not found for user {user_id}")
        return

    print(f"📋 User Preference: {user_id}")
    print("=" * 25)
    print(f"Key: {preference.preference_key}")
    print(f"Value: {preference.preference_value}")
    print(f"Category: {preference.category.value}")
    print(f"Confidence: {preference.confidence:.2f}")
    print(f"Evidence Count: {preference.evidence_count}")
    print(f"Last Updated: {preference.last_updated}")
    print(f"Sources: {', '.join(preference.sources)}")


def _handle_user_profile(args: argparse.Namespace, preference_system) -> None:
    """Handle user profile commands."""
    user_id = args.user_id

    summary = preference_system.get_user_profile_summary(user_id)

    if summary["status"] == "not_found":
        print(f"❌ User profile not found: {user_id}")
        return

    print(f"📋 User Profile: {user_id}")
    print("=" * 25)
    print(f"Experience Level: {summary['experience_level']}")
    print(f"Total Interactions: {summary['total_interactions']}")
    print(f"Average Satisfaction: {summary['average_satisfaction']:.2f}")
    print(f"Error Rate: {summary['error_rate']:.2f}")
    print(f"Last Activity: {summary['last_activity']}")
    print(f"Preferences Count: {summary['preferences_count']}")
    print(f"Behavior Patterns Count: {summary['behavior_patterns_count']}")
    print(f"Feedback Count: {summary['feedback_count']}")

    if summary["top_preferences"]:
        print("\nTop Preferences:")
        for pref in summary["top_preferences"]:
            print(
                f"  {pref['key']}: {pref['value']} (confidence: {pref['confidence']:.2f})"
            )

    if summary["recent_patterns"]:
        print("\nRecent Behavior Patterns:")
        for pattern in summary["recent_patterns"]:
            print(f"  {pattern['type']}: {pattern['description']}")
            print(
                f"    Confidence: {pattern['confidence']:.2f}, "
                f"Frequency: {pattern['frequency']:.2f}"
            )


def _handle_behavior_patterns(args: argparse.Namespace, preference_system) -> None:
    """Handle behavior patterns commands."""
    user_id = args.user_id

    if user_id not in preference_system.user_profiles:
        print(f"❌ User profile not found: {user_id}")
        return

    profile = preference_system.user_profiles[user_id]

    if not profile.behavior_patterns:
        print(f"📋 No behavior patterns found for user {user_id}")
        return

    print(f"📋 Behavior Patterns: {user_id}")
    print("=" * 30)

    for i, pattern in enumerate(profile.behavior_patterns, 1):
        print(f"{i}. {pattern.pattern_type}")
        print(f"   Description: {pattern.description}")
        print(f"   Frequency: {pattern.frequency:.2f}")
        print(f"   Confidence: {pattern.confidence:.2f}")
        print(f"   Detected: {pattern.detected_at}")

        if pattern.implications:
            print(f"   Implications: {', '.join(pattern.implications)}")

        if pattern.recommendations:
            print(f"   Recommendations: {', '.join(pattern.recommendations)}")
        print()


def _handle_health_monitor_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle system health monitoring commands."""
    health_monitor = get_system_health_monitor(root)

    if args.health_action == "monitor":
        _handle_health_monitor_control(args, health_monitor)
    elif args.health_action == "status":
        _handle_health_status(args, health_monitor)
    elif args.health_action == "issues":
        _handle_health_issues(args, health_monitor)
    elif args.health_action == "healing":
        _handle_self_healing(args, health_monitor)
    elif args.health_action == "summary":
        _handle_health_summary(args, health_monitor)
    else:
        print(f"Unknown health action: {args.health_action}")


def _handle_health_monitor_control(args: argparse.Namespace, health_monitor) -> None:
    """Handle health monitoring control commands."""
    if args.monitor_action == "start":
        health_monitor.start_monitoring()
        print("✅ System health monitoring started")
    elif args.monitor_action == "stop":
        health_monitor.stop_monitoring()
        print("✅ System health monitoring stopped")
    elif args.monitor_action == "status":
        status = "active" if health_monitor.monitoring_active else "inactive"
        print(f"📊 Health monitoring status: {status}")
        print(f"Health snapshots: {len(health_monitor.health_snapshots)}")
        print(
            f"Active issues: {len([i for i in health_monitor.active_issues if not i.resolved_at])}"
        )
        print(f"Self - healing actions: {len(health_monitor.self_healing_actions)}")


def _handle_health_status(args: argparse.Namespace, health_monitor) -> None:
    """Handle health status commands."""
    if args.status_action == "current":
        _handle_current_health_status(health_monitor)
    elif args.status_action == "metrics":
        _handle_health_metrics(health_monitor)
    else:
        print(f"Unknown status action: {args.status_action}")


def _handle_current_health_status(health_monitor) -> None:
    """Handle current health status display."""
    if not health_monitor.health_snapshots:
        print("📊 No health data available")
        return

    latest_snapshot = health_monitor.health_snapshots[-1]

    print("📊 Current System Health Status")
    print("=" * 35)
    print(f"Overall Status: {latest_snapshot.overall_status.value.upper()}")
    print(f"Health Score: {latest_snapshot.health_score:.1f}/100")
    print(f"Timestamp: {latest_snapshot.timestamp}")
    print(f"Active Issues: {len(latest_snapshot.active_issues)}")

    if latest_snapshot.recommendations:
        print("\nRecommendations:")
        for i, rec in enumerate(latest_snapshot.recommendations, 1):
            print(f"  {i}. {rec}")


def _handle_health_metrics(health_monitor) -> None:
    """Handle health metrics display."""
    if not health_monitor.health_snapshots:
        print("📊 No health metrics available")
        return

    latest_snapshot = health_monitor.health_snapshots[-1]

    print("📊 Health Metrics")
    print("=" * 20)

    for metric, metric_value in latest_snapshot.metrics.items():
        status_icon = (
            "🟢"
            if metric_value.value <= metric_value.threshold_warning
            else "🟡" if metric_value.value <= metric_value.threshold_critical else "🔴"
        )
        print(
            f"{status_icon} {metric.value}: {metric_value.value:.1f}{metric_value.unit}"
        )
        print(
            f"   Warning: {metric_value.threshold_warning}{metric_value.unit}, "
            f"Critical: {metric_value.threshold_critical}{metric_value.unit}"
        )


def _handle_health_issues(args: argparse.Namespace, health_monitor) -> None:
    """Handle health issues commands."""
    if args.issues_action == "list":
        _handle_list_health_issues(health_monitor)
    elif args.issues_action == "show":
        _handle_show_health_issue(args, health_monitor)
    else:
        print(f"Unknown issues action: {args.issues_action}")


def _handle_list_health_issues(health_monitor) -> None:
    """Handle listing health issues."""
    active_issues = health_monitor.get_active_issues()

    if not active_issues:
        print("📊 No active health issues")
        return

    print("📊 Active Health Issues")
    print("=" * 25)

    for i, issue in enumerate(active_issues, 1):
        severity_icon = {"warning": "🟡", "critical": "🔴", "failed": "💀"}.get(
            issue["severity"], "⚪"
        )

        print(f"{i}. {severity_icon} {issue['issue_type']}")
        print(f"   Severity: {issue['severity']}")
        print(f"   Description: {issue['description']}")
        print(f"   Duration: {issue['duration_minutes']:.1f} minutes")
        print(f"   Components: {', '.join(issue['affected_components'])}")
        print()


def _handle_show_health_issue(args: argparse.Namespace, health_monitor) -> None:
    """Handle showing specific health issue."""
    issue_id = args.issue_id

    active_issues = health_monitor.get_active_issues()
    issue = None

    for i in active_issues:
        if i["issue_id"] == issue_id:
            issue = i
            break

    if not issue:
        print(f"❌ Health issue {issue_id} not found")
        return

    print(f"📊 Health Issue: {issue_id}")
    print("=" * 30)
    print(f"Issue Type: {issue['issue_type']}")
    print(f"Severity: {issue['severity']}")
    print(f"Description: {issue['description']}")
    print(f"Detected At: {issue['detected_at']}")
    print(f"Duration: {issue['duration_minutes']:.1f} minutes")
    print(f"Affected Components: {', '.join(issue['affected_components'])}")

    if issue["metrics"]:
        print("\nMetrics:")
        for metric, value in issue["metrics"].items():
            print(f"  {metric}: {value}")


def _handle_self_healing(args: argparse.Namespace, health_monitor) -> None:
    """Handle self - healing commands."""
    if args.healing_action == "history":
        _handle_healing_history(args, health_monitor)
    elif args.healing_action == "stats":
        _handle_healing_stats(health_monitor)
    else:
        print(f"Unknown healing action: {args.healing_action}")


def _handle_healing_history(args: argparse.Namespace, health_monitor) -> None:
    """Handle self - healing history display."""
    days = args.days or 7

    history = health_monitor.get_self_healing_history(days)

    if not history:
        print(f"📊 No self - healing actions in the last {days} days")
        return

    print(f"📊 Self - Healing History (Last {days} days)")
    print("=" * 40)

    for i, action in enumerate(history, 1):
        status_icon = "✅" if action["success"] else "❌"
        print(f"{i}. {status_icon} {action['action_type']}")
        print(f"   Issue: {action['issue_id']}")
        print(f"   Description: {action['description']}")
        print(f"   Executed: {action['executed_at']}")
        print(f"   Duration: {action['duration']:.2f}s")
        if action["result"]:
            print(f"   Result: {action['result']}")
        print()


def _handle_healing_stats(health_monitor) -> None:
    """Handle self - healing statistics display."""
    history = health_monitor.get_self_healing_history(7)

    if not history:
        print("📊 No self - healing actions in the last 7 days")
        return

    total_actions = len(history)
    successful_actions = sum(1 for action in history if action["success"])
    success_rate = (
        (successful_actions / total_actions) * 100 if total_actions > 0 else 0
    )

    # Action type statistics
    action_types: Dict[str, Any] = {}
    for action in history:
        action_type = action["action_type"]
        if action_type not in action_types:
            action_types[action_type] = {"total": 0, "successful": 0}
        action_types[action_type]["total"] += 1
        if action["success"]:
            action_types[action_type]["successful"] += 1

    print("📊 Self - Healing Statistics (Last 7 days)")
    print("=" * 40)
    print(f"Total Actions: {total_actions}")
    print(f"Successful Actions: {successful_actions}")
    print(f"Success Rate: {success_rate:.1f}%")

    print("\nAction Type Breakdown:")
    for action_type, stats in action_types.items():
        type_success_rate = (
            (stats["successful"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        )
        print(
            f"  {action_type}: {stats['successful']}/{stats['total']} ({type_success_rate:.1f}%)"
        )


def _handle_health_summary(args: argparse.Namespace, health_monitor) -> None:
    """Handle health summary display."""
    hours = args.hours or 24

    summary = health_monitor.get_health_summary(hours)

    if summary["status"] == "no_data":
        print(f"📊 No health data for the last {hours} hours")
        return

    print(f"📊 System Health Summary (Last {hours} hours)")
    print("=" * 45)
    print(f"Total Snapshots: {summary['total_snapshots']}")
    print(f"Average Health Score: {summary['avg_health_score']:.1f}")
    print(f"Min Health Score: {summary['min_health_score']:.1f}")
    print(f"Max Health Score: {summary['max_health_score']:.1f}")
    print(f"Current Health Score: {summary['current_health_score']:.1f}")
    print(f"Current Status: {summary['current_status']}")

    print(f"\nStatus Distribution:")
    for status, count in summary["status_distribution"].items():
        print(f"  {status}: {count}")

    print(f"\nIssues:")
    print(f"  Total Issues: {summary['total_issues']}")
    print(f"  Resolved Issues: {summary['resolved_issues']}")

    print(f"\nSelf - Healing:")
    print(f"  Actions Taken: {summary['self_healing_actions']}")
    print(f"  Successful Actions: {summary['successful_healing_actions']}")
    print(f"  Success Rate: {summary['healing_success_rate']:.1%}")


def _handle_knowledge_base_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle knowledge base evolution commands."""
    knowledge_base = get_knowledge_base_evolution(root)

    if args.knowledge_action == "add":
        _handle_add_knowledge(args, knowledge_base)
    elif args.knowledge_action == "search":
        _handle_search_knowledge(args, knowledge_base)
    elif args.knowledge_action == "list":
        _handle_list_knowledge(args, knowledge_base)
    elif args.knowledge_action == "show":
        _handle_show_knowledge(args, knowledge_base)
    elif args.knowledge_action == "patterns":
        _handle_knowledge_patterns(args, knowledge_base)
    elif args.knowledge_action == "recommendations":
        _handle_knowledge_recommendations(args, knowledge_base)
    elif args.knowledge_action == "stats":
        _handle_knowledge_stats(knowledge_base)
    elif args.knowledge_action == "discover":
        _handle_discover_patterns(knowledge_base)
    else:
        print(f"Unknown knowledge action: {args.knowledge_action}")


def _handle_add_knowledge(args: argparse.Namespace, knowledge_base) -> None:
    """Handle adding knowledge to the system."""
    knowledge_type = KnowledgeType(args.knowledge_type)
    source = KnowledgeSource(args.source)
    quality = (
        KnowledgeQuality(args.quality) if args.quality else KnowledgeQuality.MEDIUM
    )

    tags = args.tags.split(",") if args.tags else []
    # Parse metadata (flexible sources)
    metadata = _parse_json_source(
        raw=getattr(args, "metadata", None),
        file=getattr(args, "metadata_file", None),
        b64=getattr(args, "metadata_b64", None),
        allow_kv=True,
    )

    knowledge_id = knowledge_base.add_knowledge(
        knowledge_type=knowledge_type,
        title=args.title,
        content=args.content,
        source=source,
        quality=quality,
        tags=tags,
        metadata=metadata,
        confidence_score=args.confidence or 0.5,
    )

    print(f"✅ Knowledge added successfully")
    print(f"Knowledge ID: {knowledge_id}")
    print(f"Type: {knowledge_type.value}")
    print(f"Source: {source.value}")
    print(f"Quality: {quality.value}")


def _handle_search_knowledge(args: argparse.Namespace, knowledge_base) -> None:
    """Handle searching knowledge."""
    knowledge_types = (
        [KnowledgeType(t) for t in args.types.split(",")] if args.types else None
    )
    tags = args.tags.split(",") if args.tags else None

    results = knowledge_base.search_knowledge(
        query=args.query,
        knowledge_types=knowledge_types,
        tags=tags,
        quality_threshold=args.quality_threshold or 0.0,
        limit=args.limit or 10,
    )

    if not results:
        print("📚 No knowledge found matching your search")
        return

    print(f"📚 Knowledge Search Results ({len(results)} found)")
    print("=" * 40)

    for i, item in enumerate(results, 1):
        print(f"{i}. {item.title}")
        print(f"   Type: {item.knowledge_type.value}")
        print(f"   Quality: {item.quality.value}")
        print(f"   Confidence: {item.confidence_score:.2f}")
        print(f"   Relevance: {item.relevance_score:.2f}")
        print(f"   Tags: {', '.join(item.tags)}")
        print(f"   Content: {item.content[:100]}...")
        print()


def _handle_list_knowledge(args: argparse.Namespace, knowledge_base) -> None:
    """Handle listing knowledge items."""
    knowledge_type = KnowledgeType(args.knowledge_type) if args.knowledge_type else None
    status = KnowledgeStatus(args.status) if args.status else None

    items = []
    for item in knowledge_base.knowledge_items.values():
        if knowledge_type and item.knowledge_type != knowledge_type:
            continue
        if status and item.status != status:
            continue
        items.append(item)

    # Sort by relevance or confidence
    sort_key = args.sort or "relevance"
    if sort_key == "confidence":
        items.sort(key=lambda x: x.confidence_score, reverse=True)
    else:
        items.sort(key=lambda x: x.relevance_score, reverse=True)

    limit = args.limit or 20
    items = items[:limit]

    if not items:
        print("📚 No knowledge items found")
        return

    print(f"📚 Knowledge Items ({len(items)} shown)")
    print("=" * 30)

    for i, item in enumerate(items, 1):
        print(f"{i}. {item.title}")
        print(f"   ID: {item.knowledge_id}")
        print(f"   Type: {item.knowledge_type.value}")
        print(f"   Status: {item.status.value}")
        print(f"   Quality: {item.quality.value}")
        print(f"   Confidence: {item.confidence_score:.2f}")
        print(f"   Created: {item.created_at.strftime('%Y -% m -% d %H:%M')}")
        print(f"   Tags: {', '.join(item.tags)}")
        print()


def _handle_show_knowledge(args: argparse.Namespace, knowledge_base) -> None:
    """Handle showing specific knowledge item."""
    knowledge_id = args.knowledge_id

    if knowledge_id not in knowledge_base.knowledge_items:
        print(f"❌ Knowledge item {knowledge_id} not found")
        return

    item = knowledge_base.knowledge_items[knowledge_id]

    print(f"📚 Knowledge Item: {knowledge_id}")
    print("=" * 40)
    print(f"Title: {item.title}")
    print(f"Type: {item.knowledge_type.value}")
    print(f"Source: {item.source.value}")
    print(f"Quality: {item.quality.value}")
    print(f"Status: {item.status.value}")
    print(f"Confidence: {item.confidence_score:.2f}")
    print(f"Relevance: {item.relevance_score:.2f}")
    print(f"Created: {item.created_at}")
    print(f"Updated: {item.updated_at}")
    print(f"Access Count: {item.access_count}")

    if item.tags:
        print(f"Tags: {', '.join(item.tags)}")

    if item.metadata:
        print(f"Metadata: {json.dumps(item.metadata, indent=2)}")

    if item.related_knowledge:
        print(f"Related Knowledge: {', '.join(item.related_knowledge)}")

    print(f"\nContent:")
    print(item.content)


def _handle_knowledge_patterns(args: argparse.Namespace, knowledge_base) -> None:
    """Handle knowledge patterns commands."""
    if args.patterns_action == "list":
        _handle_list_patterns(knowledge_base)
    elif args.patterns_action == "show":
        _handle_show_pattern(args, knowledge_base)
    else:
        print(f"Unknown patterns action: {args.patterns_action}")


def _handle_list_patterns(knowledge_base) -> None:
    """Handle listing knowledge patterns."""
    patterns = list(knowledge_base.knowledge_patterns.values())

    if not patterns:
        print("📚 No knowledge patterns discovered")
        return

    # Sort by confidence
    patterns.sort(key=lambda x: x.confidence, reverse=True)

    print(f"📚 Knowledge Patterns ({len(patterns)} found)")
    print("=" * 35)

    for i, pattern in enumerate(patterns, 1):
        print(f"{i}. {pattern.description}")
        print(f"   Type: {pattern.pattern_type}")
        print(f"   Frequency: {pattern.frequency}")
        print(f"   Confidence: {pattern.confidence:.2f}")
        print(f"   Success Rate: {pattern.success_rate:.2f}")
        print(f"   Discovered: {pattern.discovered_at.strftime('%Y -% m -% d')}")
        print(f"   Examples: {len(pattern.examples)}")
        print()


def _handle_show_pattern(args: argparse.Namespace, knowledge_base) -> None:
    """Handle showing specific knowledge pattern."""
    pattern_id = args.pattern_id

    if pattern_id not in knowledge_base.knowledge_patterns:
        print(f"❌ Knowledge pattern {pattern_id} not found")
        return

    pattern = knowledge_base.knowledge_patterns[pattern_id]

    print(f"📚 Knowledge Pattern: {pattern_id}")
    print("=" * 40)
    print(f"Description: {pattern.description}")
    print(f"Type: {pattern.pattern_type}")
    print(f"Frequency: {pattern.frequency}")
    print(f"Confidence: {pattern.confidence:.2f}")
    print(f"Success Rate: {pattern.success_rate:.2f}")
    print(f"Validation Count: {pattern.validation_count}")
    print(f"Discovered: {pattern.discovered_at}")
    print(f"Last Updated: {pattern.last_updated}")

    print(f"\nConditions:")
    for key, value in pattern.conditions.items():
        print(f"  {key}: {value}")

    print(f"\nOutcomes:")
    for key, value in pattern.outcomes.items():
        print(f"  {key}: {value}")

    print(f"\nExamples ({len(pattern.examples)}):")
    for example_id in pattern.examples[:5]:  # Show first 5
        if example_id in knowledge_base.knowledge_items:
            item = knowledge_base.knowledge_items[example_id]
            print(f"  - {item.title}")


def _handle_knowledge_recommendations(args: argparse.Namespace, knowledge_base) -> None:
    """Handle knowledge recommendations commands."""
    if args.recommendations_action == "get":
        _handle_get_recommendations(args, knowledge_base)
    elif args.recommendations_action == "list":
        _handle_list_knowledge_recommendations(knowledge_base)
    else:
        print(f"Unknown recommendations action: {args.recommendations_action}")


def _handle_get_recommendations(args: argparse.Namespace, knowledge_base) -> None:
    """Handle getting knowledge recommendations."""
    context = json.loads(args.context) if args.context else {}

    recommendations = knowledge_base.get_knowledge_recommendations(
        context=context, limit=args.limit or 5
    )

    if not recommendations:
        print("📚 No knowledge recommendations available")
        return

    print(f"📚 Knowledge Recommendations ({len(recommendations)} found)")
    print("=" * 45)

    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec.title}")
        print(f"   Type: {rec.recommendation_type}")
        print(f"   Confidence: {rec.confidence:.2f}")
        print(f"   Relevance: {rec.relevance_score:.2f}")
        print(f"   Knowledge ID: {rec.knowledge_item_id}")
        print(f"   Description: {rec.description}")
        print()


def _handle_list_knowledge_recommendations(knowledge_base) -> None:
    """Handle listing knowledge recommendations."""
    recommendations = knowledge_base.knowledge_recommendations

    if not recommendations:
        print("📚 No knowledge recommendations available")
        return

    # Filter active recommendations
    active_recommendations = [
        rec
        for rec in recommendations
        if not rec.expires_at or rec.expires_at > datetime.now()
    ]

    print(f"📚 Knowledge Recommendations ({len(active_recommendations)} active)")
    print("=" * 50)

    for i, rec in enumerate(active_recommendations, 1):
        print(f"{i}. {rec.title}")
        print(f"   Type: {rec.recommendation_type}")
        print(f"   Confidence: {rec.confidence:.2f}")
        print(f"   Usage Count: {rec.usage_count}")
        print(f"   Feedback Score: {rec.feedback_score:.2f}")
        print(f"   Created: {rec.created_at.strftime('%Y -% m -% d %H:%M')}")
        print()


def _handle_knowledge_stats(knowledge_base) -> None:
    """Handle knowledge base statistics."""
    stats = knowledge_base.get_knowledge_statistics()

    print("📚 Knowledge Base Statistics")
    print("=" * 30)
    print(f"Total Knowledge Items: {stats['total_knowledge_items']}")
    print(f"Active Knowledge Items: {stats['active_knowledge_items']}")
    print(f"Draft Knowledge Items: {stats['draft_knowledge_items']}")
    print(f"Average Confidence Score: {stats['average_confidence_score']:.2f}")
    print(f"Average Relevance Score: {stats['average_relevance_score']:.2f}")

    print(f"\nKnowledge Type Distribution:")
    for ktype, count in stats["knowledge_type_distribution"].items():
        print(f"  {ktype}: {count}")

    print(f"\nQuality Distribution:")
    for quality, count in stats["quality_distribution"].items():
        print(f"  {quality}: {count}")

    print(f"\nSource Distribution:")
    for source, count in stats["source_distribution"].items():
        print(f"  {source}: {count}")

    print(f"\nPatterns:")
    print(f"  Total Patterns: {stats['total_patterns']}")
    print(f"  Average Pattern Confidence: {stats['average_pattern_confidence']:.2f}")

    print(f"\nRecommendations:")
    print(f"  Total Recommendations: {stats['total_recommendations']}")
    print(f"  Active Recommendations: {stats['active_recommendations']}")

    print(f"\nIndex Information:")
    print(f"  Knowledge Index Size: {stats['knowledge_index_size']}")
    print(f"  Knowledge Graph Size: {stats['knowledge_graph_size']}")


def _handle_discover_patterns(knowledge_base) -> None:
    """Handle discovering new patterns."""
    print("🔍 Discovering knowledge patterns...")

    patterns = knowledge_base.discover_patterns()

    if not patterns:
        print("📚 No new patterns discovered")
        return

    print(f"✅ Discovered {len(patterns)} new patterns")

    for i, pattern in enumerate(patterns, 1):
        print(f"{i}. {pattern.description}")
        print(f"   Type: {pattern.pattern_type}")
        print(f"   Frequency: {pattern.frequency}")
        print(f"   Confidence: {pattern.confidence:.2f}")
        print()


def _handle_analytics_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle analytics and reporting commands."""
    analytics = get_continuous_improvement_analytics(root)

    if args.analytics_action == "metrics":
        _handle_metrics_commands(args, analytics)
    elif args.analytics_action == "kpis":
        _handle_kpis_commands(args, analytics)
    elif args.analytics_action == "reports":
        _handle_reports_commands(args, analytics)
    elif args.analytics_action == "alerts":
        _handle_alerts_commands(args, analytics)
    elif args.analytics_action == "dashboard":
        _handle_dashboard_commands(args, analytics)
    elif args.analytics_action == "export":
        _handle_export_commands(args, analytics)
    else:
        print(f"Unknown analytics action: {args.analytics_action}")


def _handle_metrics_commands(args: argparse.Namespace, analytics) -> None:
    """Handle metrics commands."""
    if args.metrics_action == "record":
        _handle_record_metric(args, analytics)
    elif args.metrics_action == "list":
        _handle_list_metrics(args, analytics)
    else:
        print(f"Unknown metrics action: {args.metrics_action}")


def _handle_record_metric(args: argparse.Namespace, analytics) -> None:
    """Handle recording a metric."""
    import json

    metric_type = MetricType(args.metric_type) if args.metric_type else MetricType.GAUGE
    tags = json.loads(args.tags) if args.tags else {}
    metadata = json.loads(args.metadata) if args.metadata else {}

    metric_id = analytics.collect_metric(
        name=args.name,
        value=args.value,
        metric_type=metric_type,
        tags=tags,
        metadata=metadata,
    )

    print(f"✅ Metric recorded successfully")
    print(f"Metric ID: {metric_id}")
    print(f"Name: {args.name}")
    print(f"Value: {args.value}")
    print(f"Type: {metric_type.value}")


def _handle_list_metrics(args: argparse.Namespace, analytics) -> None:
    """Handle listing metrics."""
    limit = args.limit or 20

    # Filter metrics by name if specified
    metrics = analytics.metrics
    if args.name_filter:
        metrics = [m for m in metrics if args.name_filter.lower() in m.name.lower()]

    # Sort by timestamp (most recent first)
    metrics.sort(key=lambda x: x.timestamp, reverse=True)
    metrics = metrics[:limit]

    if not metrics:
        print("📊 No metrics found")
        return

    print(f"📊 Recent Metrics ({len(metrics)} shown)")
    print("=" * 35)

    for i, metric in enumerate(metrics, 1):
        print(f"{i}. {metric.name}")
        print(f"   Value: {metric.value}")
        print(f"   Type: {metric.metric_type.value}")
        print(f"   Timestamp: {metric.timestamp.strftime('%Y -% m -% d %H:%M:%S')}")
        if metric.tags:
            print(f"   Tags: {', '.join(f'{k}={v}' for k, v in metric.tags.items())}")
        print()


def _handle_kpis_commands(args: argparse.Namespace, analytics) -> None:
    """Handle KPIs commands."""
    if args.kpis_action == "list":
        _handle_list_kpis(analytics)
    elif args.kpis_action == "show":
        _handle_show_kpi(args, analytics)
    else:
        print(f"Unknown KPIs action: {args.kpis_action}")


def _handle_list_kpis(analytics) -> None:
    """Handle listing KPIs."""
    if not analytics.kpis:
        print("📊 No KPIs available")
        return

    print("📊 Key Performance Indicators")
    print("=" * 35)

    for kpi_id, kpi in analytics.kpis.items():
        status_icon = (
            "🟢"
            if kpi.current_value >= kpi.target_value
            else "🟡" if kpi.current_value >= kpi.target_value * 0.8 else "🔴"
        )
        trend_icon = "📈" if kpi.trend == "up" else "📉" if kpi.trend == "down" else "➡️"

        print(f"{status_icon} {kpi.name}")
        print(f"   Current: {kpi.current_value:.2f} {kpi.unit}")
        print(f"   Target: {kpi.target_value:.2f} {kpi.unit}")
        print(f"   Trend: {trend_icon} {kpi.trend}")
        print(f"   Last Updated: {kpi.last_updated.strftime('%Y -% m -% d %H:%M')}")
        print()


def _handle_show_kpi(args: argparse.Namespace, analytics) -> None:
    """Handle showing specific KPI."""
    kpi_id = args.kpi_id

    if kpi_id not in analytics.kpis:
        print(f"❌ KPI {kpi_id} not found")
        return

    kpi = analytics.kpis[kpi_id]

    print(f"📊 KPI: {kpi.name}")
    print("=" * 30)
    print(f"Description: {kpi.description}")
    print(f"Current Value: {kpi.current_value:.2f} {kpi.unit}")
    print(f"Target Value: {kpi.target_value:.2f} {kpi.unit}")
    print(f"Trend: {kpi.trend}")
    print(f"Last Updated: {kpi.last_updated}")

    if kpi.historical_values:
        print(f"\nHistorical Values (last 5):")
        for timestamp, value in kpi.historical_values[-5:]:
            print(
                f"  {timestamp.strftime('%Y -% m -% d %H:%M')}: {value:.2f} {kpi.unit}"
            )


def _handle_reports_commands(args: argparse.Namespace, analytics) -> None:
    """Handle reports commands."""
    if args.reports_action == "generate":
        _handle_generate_report(args, analytics)
    elif args.reports_action == "list":
        _handle_list_reports(args, analytics)
    elif args.reports_action == "show":
        _handle_show_report(args, analytics)
    else:
        print(f"Unknown reports action: {args.reports_action}")


def _handle_generate_report(args: argparse.Namespace, analytics) -> None:
    """Handle generating a report."""
    report_type = ReportType(args.report_type)

    # Calculate period
    if args.period == "day":
        period_end = datetime.now()
        period_start = period_end - timedelta(days=1)
    elif args.period == "week":
        period_end = datetime.now()
        period_start = period_end - timedelta(weeks=1)
    elif args.period == "month":
        period_end = datetime.now()
        period_start = period_end - timedelta(days=30)
    else:
        # Custom period
        period_start = datetime.fromisoformat(args.period_start)
        period_end = datetime.fromisoformat(args.period_end)

    report_id = analytics.generate_report(
        report_type=report_type,
        period_start=period_start,
        period_end=period_end,
        title=args.title,
        description=args.description,
    )

    print(f"✅ Report generated successfully")
    print(f"Report ID: {report_id}")
    print(f"Type: {report_type.value}")
    print(
        f"Period: {period_start.strftime('%Y -% m -% d')} to {period_end.strftime('%Y -% m -% d')}"
    )


def _handle_list_reports(args: argparse.Namespace, analytics) -> None:
    """Handle listing reports."""
    limit = args.limit or 10

    # Sort by generation time (most recent first)
    reports = sorted(analytics.reports, key=lambda x: x.generated_at, reverse=True)
    reports = reports[:limit]

    if not reports:
        print("📊 No reports available")
        return

    print(f"📊 Recent Reports ({len(reports)} shown)")
    print("=" * 35)

    for i, report in enumerate(reports, 1):
        print(f"{i}. {report.title}")
        print(f"   Type: {report.report_type.value}")
        print(f"   Generated: {report.generated_at.strftime('%Y -% m -% d %H:%M')}")
        print(
            f"   Period: {report.period_start.strftime('%Y -% m -% d')} to {report.period_end.strftime('%Y -% m -% d')}"
        )
        print(f"   ID: {report.report_id}")
        print()


def _handle_show_report(args: argparse.Namespace, analytics) -> None:
    """Handle showing specific report."""
    report_id = args.report_id

    # Find the report
    report = None
    for r in analytics.reports:
        if r.report_id == report_id:
            report = r
            break

    if not report:
        print(f"❌ Report {report_id} not found")
        return

    print(f"📊 Report: {report.title}")
    print("=" * 40)
    print(f"Type: {report.report_type.value}")
    print(f"Generated: {report.generated_at}")
    print(f"Period: {report.period_start} to {report.period_end}")
    print(f"Description: {report.description}")

    print(f"\nSummary:")
    print(report.summary)

    if report.recommendations:
        print(f"\nRecommendations:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")


def _handle_alerts_commands(args: argparse.Namespace, analytics) -> None:
    """Handle alerts commands."""
    if args.alerts_action == "list":
        _handle_list_alerts(args, analytics)
    elif args.alerts_action == "acknowledge":
        _handle_acknowledge_alert(args, analytics)
    else:
        print(f"Unknown alerts action: {args.alerts_action}")


def _handle_list_alerts(args: argparse.Namespace, analytics) -> None:
    """Handle listing alerts."""
    limit = args.limit or 20

    # Filter alerts
    alerts = analytics.alerts
    if args.level:
        alerts = [a for a in alerts if a.alert_level.value == args.level]
    if args.active_only:
        alerts = [a for a in alerts if not a.resolved_at]

    # Sort by trigger time (most recent first)
    alerts.sort(key=lambda x: x.triggered_at, reverse=True)
    alerts = alerts[:limit]

    if not alerts:
        print("📊 No alerts found")
        return

    print(f"📊 Alerts ({len(alerts)} shown)")
    print("=" * 25)

    for i, alert in enumerate(alerts, 1):
        level_icon = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨",
            "emergency": "💀",
        }.get(alert.alert_level.value, "❓")

        status = "Active" if not alert.resolved_at else "Resolved"
        acknowledged = "Acknowledged" if alert.acknowledged else "Unacknowledged"

        print(f"{i}. {level_icon} {alert.title}")
        print(f"   Level: {alert.alert_level.value}")
        print(f"   Status: {status}")
        print(f"   Acknowledged: {acknowledged}")
        print(f"   Triggered: {alert.triggered_at.strftime('%Y -% m -% d %H:%M')}")
        print(f"   Metric: {alert.metric_name} ({alert.current_value:.2f})")
        print(f"   Threshold: {alert.threshold_value:.2f}")
        print()


def _handle_acknowledge_alert(args: argparse.Namespace, analytics) -> None:
    """Handle acknowledging an alert."""
    alert_id = args.alert_id

    # Find and acknowledge the alert
    for alert in analytics.alerts:
        if alert.alert_id == alert_id:
            alert.acknowledged = True
            print(f"✅ Alert {alert_id} acknowledged")
            return

    print(f"❌ Alert {alert_id} not found")


def _handle_dashboard_commands(args: argparse.Namespace, analytics) -> None:
    """Handle dashboard commands."""
    if args.dashboard_action == "data":
        _handle_dashboard_data(analytics)
    elif args.dashboard_action == "summary":
        _handle_dashboard_summary(analytics)
    else:
        print(f"Unknown dashboard action: {args.dashboard_action}")


def _handle_dashboard_data(analytics) -> None:
    """Handle getting dashboard data."""
    data = analytics.get_dashboard_data()

    print("📊 Dashboard Data")
    print("=" * 20)

    # System status
    status = data["system_status"]
    print(f"System Status:")
    print(f"  Total Metrics: {status['total_metrics']}")
    print(f"  Active KPIs: {status['active_kpis']}")
    print(f"  Total Reports: {status['total_reports']}")
    print(f"  Active Alerts: {status['active_alerts']}")

    # KPIs
    print(f"\nKey Performance Indicators:")
    for kpi_id, kpi_data in data["kpis"].items():
        status_icon = (
            "🟢" if kpi_data["current_value"] >= kpi_data["target_value"] else "🟡"
        )
        print(
            f"  {status_icon} {kpi_data['name']}: {kpi_data['current_value']:.2f} {kpi_data['unit']} (target: {kpi_data['target_value']:.2f})"
        )

    # Recent alerts
    if data["recent_alerts"]:
        print(f"\nRecent Alerts:")
        for alert in data["recent_alerts"][:5]:
            level_icon = {
                "info": "ℹ️",
                "warning": "⚠️",
                "critical": "🚨",
                "emergency": "💀",
            }.get(alert["level"], "❓")
            print(f"  {level_icon} {alert['title']} ({alert['level']})")


def _handle_dashboard_summary(analytics) -> None:
    """Handle getting dashboard summary."""
    summary = analytics.get_analytics_summary()

    print("📊 Analytics Summary")
    print("=" * 25)

    # Metrics summary
    metrics = summary["metrics"]
    print(f"Metrics:")
    print(f"  Total: {metrics['total']}")
    print(f"  Recent (24h): {metrics['recent_count']}")
    print(f"  By Type: {', '.join(f'{k}={v}' for k, v in metrics['by_type'].items())}")

    # KPIs summary
    kpis = summary["kpis"]
    print(f"\nKPIs:")
    print(f"  Total: {kpis['total']}")
    print(f"  On Target: {kpis['on_target']}")
    print(f"  Trending Up: {kpis['trending_up']}")
    print(f"  Trending Down: {kpis['trending_down']}")

    # Reports summary
    reports = summary["reports"]
    print(f"\nReports:")
    print(f"  Total: {reports['total']}")
    print(f"  Recent (7d): {reports['recent']}")

    # Alerts summary
    alerts = summary["alerts"]
    print(f"\nAlerts:")
    print(f"  Total: {alerts['total']}")
    print(f"  Active: {alerts['active']}")
    print(f"  By Level: {', '.join(f'{k}={v}' for k, v in alerts['by_level'].items())}")


def _handle_export_commands(args: argparse.Namespace, analytics) -> None:
    """Handle export commands."""
    if args.export_action == "report":
        _handle_export_report(args, analytics)
    else:
        print(f"Unknown export action: {args.export_action}")


def _handle_export_report(args: argparse.Namespace, analytics) -> None:
    """Handle exporting a report."""
    report_id = args.report_id
    format = args.format or "json"

    try:
        exported_data = analytics.export_report(report_id, format)

        if args.output_file:
            with open(args.output_file, "w", encoding="utf - 8") as f:
                f.write(exported_data)
            print(f"✅ Report exported to {args.output_file}")
        else:
            print(f"✅ Report exported in {format} format:")
            print(exported_data)

    except ValueError as e:
        print(f"❌ Export failed: {e}")


def _handle_test_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle test commands."""
    system = get_continuous_improvement_system(root)

    print("🧪 Testing Continuous Improvement System")
    print("=" * 40)

    # Test 1: Record a learning event
    print("1. Testing learning event recording...")
    event_id = system.record_learning_event(
        learning_type=LearningType.USER_PREFERENCE,
        context={"user_id": "test_user", "preference_type": "gate_timeout", "value": 2},
        outcome={"preferred_value": 2, "satisfaction_score": 0.8},
        confidence=0.9,
        impact_score=0.6,
        source="test",
    )
    print(f"   ✅ Learning event recorded: {event_id}")

    # Test 2: Get learning summary
    print("2. Testing learning summary...")
    summary = system.get_learning_summary(1)
    if summary["status"] == "success":
        print(f"   ✅ Learning summary retrieved: {summary['total_events']} events")
    else:
        print("   ❌ Learning summary failed")

    # Test 3: Get recommendations
    print("3. Testing recommendations...")
    recommendations = system.get_improvement_recommendations(limit=5)
    print(f"   ✅ Found {len(recommendations)} recommendations")

    # Test 4: System health
    print("4. Testing system health...")
    health = system.get_system_health_summary(1)
    print(f"   ✅ System health summary: {health['status']}")

    print("\n🎉 Continuous improvement system testing completed!")


def add_continuous_improvement_parser(subparsers) -> None:
    """Add continuous improvement commands to the argument parser."""
    improvement_parser = subparsers.add_parser(
        "continuous - improvement", help="Continuous improvement system management"
    )

    improvement_subparsers = improvement_parser.add_subparsers(
        dest="improvement_cmd", help="Improvement commands"
    )

    # Learning commands
    learn_parser = improvement_subparsers.add_parser(
        "learn", help="Learning event management"
    )
    learn_subparsers = learn_parser.add_subparsers(
        dest="learning_action", help="Learning actions"
    )

    record_parser = learn_subparsers.add_parser(
        "record", help="Record a learning event"
    )
    record_parser.add_argument("learning_type", help="Type of learning event")
    # Flexible context / outcome inputs
    record_parser.add_argument("--context", help="Context (JSON or key = value pairs)")
    record_parser.add_argument(
        "--context - file", dest="context_file", help="Path to JSON file for context"
    )
    record_parser.add_argument(
        "--context - b64", dest="context_b64", help="Base64 - encoded JSON for context"
    )
    record_parser.add_argument("--outcome", help="Outcome (JSON or key = value pairs)")
    record_parser.add_argument(
        "--outcome - file", dest="outcome_file", help="Path to JSON file for outcome"
    )
    record_parser.add_argument(
        "--outcome - b64", dest="outcome_b64", help="Base64 - encoded JSON for outcome"
    )
    record_parser.add_argument(
        "--confidence", type=float, help="Confidence score (0 - 1)"
    )
    record_parser.add_argument("--impact", type=float, help="Impact score (0 - 1)")
    record_parser.add_argument("--source", help="Source of the learning event")

    learn_subparsers.add_parser("summary", help="Get learning summary").add_argument(
        "--days", type=int, help="Number of days to look back"
    )

    learn_subparsers.add_parser("events", help="List learning events")

    # Recommendations commands
    rec_parser = improvement_subparsers.add_parser(
        "recommendations", help="Improvement recommendations management"
    )
    rec_subparsers = rec_parser.add_subparsers(
        dest="recommendations_action", help="Recommendation actions"
    )

    list_parser = rec_subparsers.add_parser("list", help="List recommendations")
    list_parser.add_argument("--limit", type=int, help="Maximum number to show")
    list_parser.add_argument("--priority", type=int, help="Minimum priority threshold")
    list_parser.add_argument("--status", help="Filter by status")

    show_parser = rec_subparsers.add_parser("show", help="Show specific recommendation")
    show_parser.add_argument("recommendation_id", help="Recommendation ID")

    approve_parser = rec_subparsers.add_parser(
        "approve", help="Approve a recommendation"
    )
    approve_parser.add_argument("recommendation_id", help="Recommendation ID")

    reject_parser = rec_subparsers.add_parser("reject", help="Reject a recommendation")
    reject_parser.add_argument("recommendation_id", help="Recommendation ID")

    # Health commands
    health_parser = improvement_subparsers.add_parser(
        "health", help="System health monitoring"
    )
    health_subparsers = health_parser.add_subparsers(
        dest="health_action", help="Health actions"
    )

    # Health monitor control
    health_monitor_parser = health_subparsers.add_parser(
        "monitor", help="Health monitoring control"
    )
    health_monitor_subparsers = health_monitor_parser.add_subparsers(
        dest="monitor_action", help="Monitor actions"
    )
    health_monitor_subparsers.add_parser("start", help="Start health monitoring")
    health_monitor_subparsers.add_parser("stop", help="Stop health monitoring")
    health_monitor_subparsers.add_parser("status", help="Show monitoring status")

    # Health status
    health_status_parser = health_subparsers.add_parser(
        "status", help="Health status commands"
    )
    health_status_subparsers = health_status_parser.add_subparsers(
        dest="status_action", help="Status actions"
    )
    health_status_subparsers.add_parser("current", help="Show current health status")
    health_status_subparsers.add_parser("metrics", help="Show health metrics")

    # Health issues
    health_issues_parser = health_subparsers.add_parser(
        "issues", help="Health issues commands"
    )
    health_issues_subparsers = health_issues_parser.add_subparsers(
        dest="issues_action", help="Issues actions"
    )
    health_issues_subparsers.add_parser("list", help="List active health issues")

    # User preference learning (quick path exposure)
    prefs_parser = subparsers.add_parser(
        "user - prefs", help="User preference learning commands"
    )
    prefs_sub = prefs_parser.add_subparsers(dest="prefs_cmd", required=True)
    pref_rec = prefs_sub.add_parser(
        "record", help="Record a user interaction for learning"
    )
    pref_rec.add_argument("--user", required=True)
    pref_rec.add_argument("--type", required=True)
    pref_rec.add_argument("--context", default="{}")
    pref_rec.add_argument("--duration", type=float)
    pref_rec.add_argument("--outcome", default="{}")
    pref_rec.add_argument("--satisfaction", type=float)
    pref_rec.add_argument("--feedback", default="")
    prefs_sub.add_parser("summary", help="Show user profile summary").add_argument(
        "--user", required=True
    )
    prefs_sub.add_parser("recommend", help="Get user recommendations").add_argument(
        "--user", required=True
    )

    health_issues_show_parser = health_issues_subparsers.add_parser(
        "show", help="Show specific health issue"
    )
    health_issues_show_parser.add_argument("issue_id", help="Health issue ID")

    # Self - healing
    health_healing_parser = health_subparsers.add_parser(
        "healing", help="Self - healing commands"
    )
    health_healing_subparsers = health_healing_parser.add_subparsers(
        dest="healing_action", help="Healing actions"
    )

    health_healing_history_parser = health_healing_subparsers.add_parser(
        "history", help="Show self - healing history"
    )
    health_healing_history_parser.add_argument(
        "--days", type=int, default=7, help="Number of days to show (default: 7)"
    )

    health_healing_subparsers.add_parser("stats", help="Show self - healing statistics")

    # Health summary
    health_summary_parser = health_subparsers.add_parser(
        "summary", help="Show health summary"
    )
    health_summary_parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Number of hours to summarize (default: 24)",
    )

    # Knowledge base subcommands
    knowledge_parser = improvement_subparsers.add_parser(
        "knowledge", help="Knowledge base evolution management"
    )
    knowledge_subparsers = knowledge_parser.add_subparsers(
        dest="knowledge_action", help="Knowledge actions"
    )

    # Add knowledge
    add_knowledge_parser = knowledge_subparsers.add_parser(
        "add", help="Add knowledge to the system"
    )
    add_knowledge_parser.add_argument("title", help="Knowledge title")
    add_knowledge_parser.add_argument("content", help="Knowledge content")
    add_knowledge_parser.add_argument(
        "knowledge_type",
        choices=[kt.value for kt in KnowledgeType],
        help="Knowledge type",
    )
    add_knowledge_parser.add_argument(
        "source", choices=[ks.value for ks in KnowledgeSource], help="Knowledge source"
    )
    add_knowledge_parser.add_argument(
        "--quality",
        choices=[kq.value for kq in KnowledgeQuality],
        help="Knowledge quality",
    )
    add_knowledge_parser.add_argument("--tags", help="Comma - separated tags")
    add_knowledge_parser.add_argument(
        "--metadata", help="Metadata (JSON or key = value pairs)"
    )
    add_knowledge_parser.add_argument(
        "--metadata - file", dest="metadata_file", help="Path to JSON file for metadata"
    )
    add_knowledge_parser.add_argument(
        "--metadata - b64",
        dest="metadata_b64",
        help="Base64 - encoded JSON for metadata",
    )
    add_knowledge_parser.add_argument(
        "--confidence", type=float, help="Confidence score (0 - 1)"
    )

    # Search knowledge
    search_knowledge_parser = knowledge_subparsers.add_parser(
        "search", help="Search knowledge items"
    )
    search_knowledge_parser.add_argument("query", help="Search query")
    search_knowledge_parser.add_argument(
        "--types", help="Comma - separated knowledge types"
    )
    search_knowledge_parser.add_argument("--tags", help="Comma - separated tags")
    search_knowledge_parser.add_argument(
        "--quality - threshold", type=float, help="Minimum quality threshold"
    )
    search_knowledge_parser.add_argument(
        "--limit", type=int, help="Maximum results to return"
    )

    # List knowledge
    list_knowledge_parser = knowledge_subparsers.add_parser(
        "list", help="List knowledge items"
    )
    list_knowledge_parser.add_argument(
        "--knowledge - type",
        choices=[kt.value for kt in KnowledgeType],
        help="Filter by knowledge type",
    )
    list_knowledge_parser.add_argument(
        "--status",
        choices=[ks.value for ks in KnowledgeStatus],
        help="Filter by status",
    )
    list_knowledge_parser.add_argument(
        "--sort", choices=["relevance", "confidence"], help="Sort order"
    )
    list_knowledge_parser.add_argument(
        "--limit", type=int, help="Maximum items to show"
    )

    # Show knowledge
    show_knowledge_parser = knowledge_subparsers.add_parser(
        "show", help="Show specific knowledge item"
    )
    show_knowledge_parser.add_argument("knowledge_id", help="Knowledge item ID")

    # Knowledge patterns
    patterns_parser = knowledge_subparsers.add_parser(
        "patterns", help="Knowledge patterns management"
    )
    patterns_subparsers = patterns_parser.add_subparsers(
        dest="patterns_action", help="Pattern actions"
    )
    patterns_subparsers.add_parser("list", help="List knowledge patterns")

    show_pattern_parser = patterns_subparsers.add_parser(
        "show", help="Show specific knowledge pattern"
    )
    show_pattern_parser.add_argument("pattern_id", help="Pattern ID")

    # Knowledge recommendations
    recommendations_parser = knowledge_subparsers.add_parser(
        "recommendations", help="Knowledge recommendations management"
    )
    recommendations_subparsers = recommendations_parser.add_subparsers(
        dest="recommendations_action", help="Recommendation actions"
    )

    get_recommendations_parser = recommendations_subparsers.add_parser(
        "get", help="Get knowledge recommendations"
    )
    get_recommendations_parser.add_argument("--context", help="Context JSON")
    get_recommendations_parser.add_argument(
        "--limit", type=int, help="Maximum recommendations"
    )

    recommendations_subparsers.add_parser("list", help="List knowledge recommendations")

    # Knowledge statistics
    knowledge_subparsers.add_parser("stats", help="Show knowledge base statistics")

    # Discover patterns
    knowledge_subparsers.add_parser("discover", help="Discover new knowledge patterns")

    # Analytics subcommands
    analytics_parser = improvement_subparsers.add_parser(
        "analytics", help="Analytics and reporting management"
    )
    analytics_subparsers = analytics_parser.add_subparsers(
        dest="analytics_action", help="Analytics actions"
    )

    # Metrics commands
    metrics_parser = analytics_subparsers.add_parser(
        "metrics", help="Metrics management"
    )
    metrics_subparsers = metrics_parser.add_subparsers(
        dest="metrics_action", help="Metrics actions"
    )

    record_metric_parser = metrics_subparsers.add_parser(
        "record", help="Record a metric"
    )
    record_metric_parser.add_argument("name", help="Metric name")
    record_metric_parser.add_argument("value", type=float, help="Metric value")
    record_metric_parser.add_argument(
        "--metric - type", choices=[mt.value for mt in MetricType], help="Metric type"
    )
    record_metric_parser.add_argument("--tags", help="Tags JSON")
    record_metric_parser.add_argument("--metadata", help="Metadata JSON")

    list_metrics_parser = metrics_subparsers.add_parser("list", help="List metrics")
    list_metrics_parser.add_argument("--name - filter", help="Filter by metric name")
    list_metrics_parser.add_argument(
        "--limit", type=int, help="Maximum metrics to show"
    )

    # KPIs commands
    kpis_parser = analytics_subparsers.add_parser(
        "kpis", help="Key Performance Indicators management"
    )
    kpis_subparsers = kpis_parser.add_subparsers(
        dest="kpis_action", help="KPIs actions"
    )
    kpis_subparsers.add_parser("list", help="List KPIs")

    show_kpi_parser = kpis_subparsers.add_parser("show", help="Show specific KPI")
    show_kpi_parser.add_argument("kpi_id", help="KPI ID")

    # Reports commands
    reports_parser = analytics_subparsers.add_parser(
        "reports", help="Reports management"
    )
    reports_subparsers = reports_parser.add_subparsers(
        dest="reports_action", help="Reports actions"
    )

    generate_report_parser = reports_subparsers.add_parser(
        "generate", help="Generate a report"
    )
    generate_report_parser.add_argument(
        "report_type", choices=[rt.value for rt in ReportType], help="Report type"
    )
    generate_report_parser.add_argument(
        "--period",
        choices=["day", "week", "month", "custom"],
        default="week",
        help="Report period",
    )
    generate_report_parser.add_argument(
        "--period - start", help="Custom period start (ISO format)"
    )
    generate_report_parser.add_argument(
        "--period - end", help="Custom period end (ISO format)"
    )
    generate_report_parser.add_argument("--title", help="Report title")
    generate_report_parser.add_argument("--description", help="Report description")

    list_reports_parser = reports_subparsers.add_parser("list", help="List reports")
    list_reports_parser.add_argument(
        "--limit", type=int, help="Maximum reports to show"
    )

    show_report_parser = reports_subparsers.add_parser(
        "show", help="Show specific report"
    )
    show_report_parser.add_argument("report_id", help="Report ID")

    # Alerts commands
    alerts_parser = analytics_subparsers.add_parser("alerts", help="Alerts management")
    alerts_subparsers = alerts_parser.add_subparsers(
        dest="alerts_action", help="Alerts actions"
    )

    list_alerts_parser = alerts_subparsers.add_parser("list", help="List alerts")
    list_alerts_parser.add_argument(
        "--level", choices=[al.value for al in AlertLevel], help="Filter by alert level"
    )
    list_alerts_parser.add_argument(
        "--active - only", action="store_true", help="Show only active alerts"
    )
    list_alerts_parser.add_argument("--limit", type=int, help="Maximum alerts to show")

    acknowledge_alert_parser = alerts_subparsers.add_parser(
        "acknowledge", help="Acknowledge an alert"
    )
    acknowledge_alert_parser.add_argument("alert_id", help="Alert ID")

    # Dashboard commands
    dashboard_parser = analytics_subparsers.add_parser(
        "dashboard", help="Dashboard data"
    )
    dashboard_subparsers = dashboard_parser.add_subparsers(
        dest="dashboard_action", help="Dashboard actions"
    )
    dashboard_subparsers.add_parser("data", help="Get dashboard data")
    dashboard_subparsers.add_parser("summary", help="Get dashboard summary")

    # Export commands
    export_parser = analytics_subparsers.add_parser("export", help="Export data")
    export_subparsers = export_parser.add_subparsers(
        dest="export_action", help="Export actions"
    )

    export_report_parser = export_subparsers.add_parser(
        "report", help="Export a report"
    )
    export_report_parser.add_argument("report_id", help="Report ID")
    export_report_parser.add_argument(
        "--format",
        choices=["json", "csv", "html"],
        default="json",
        help="Export format",
    )
    export_report_parser.add_argument("--output - file", help="Output file path")

    # Implement commands
    implement_parser = improvement_subparsers.add_parser(
        "implement", help="Implement a recommendation"
    )
    implement_parser.add_argument(
        "recommendation_id", help="Recommendation ID to implement"
    )

    # Status command
    improvement_subparsers.add_parser("status", help="Get system status")

    # Performance commands
    performance_parser = improvement_subparsers.add_parser(
        "performance", help="Performance optimization management"
    )
    performance_subparsers = performance_parser.add_subparsers(
        dest="performance_action", help="Performance actions"
    )

    # Performance monitoring
    monitor_parser = performance_subparsers.add_parser(
        "monitor", help="Performance monitoring"
    )
    monitor_subparsers = monitor_parser.add_subparsers(
        dest="monitor_action", help="Monitor actions"
    )
    monitor_subparsers.add_parser("start", help="Start performance monitoring")
    monitor_subparsers.add_parser("stop", help="Stop performance monitoring")
    monitor_subparsers.add_parser("status", help="Get monitoring status")

    # Performance opportunities
    opportunities_parser = performance_subparsers.add_parser(
        "opportunities", help="List optimization opportunities"
    )
    opportunities_parser.add_argument(
        "--limit", type=int, help="Maximum number to show"
    )
    opportunities_parser.add_argument(
        "--confidence", type=float, help="Minimum confidence threshold"
    )
    opportunities_parser.add_argument("--risk", type=int, help="Maximum risk level")

    # Performance optimization
    optimize_parser = performance_subparsers.add_parser(
        "optimize", help="Implement an optimization"
    )
    optimize_parser.add_argument("opportunity_id", help="Opportunity ID to implement")

    # Performance summary
    summary_parser = performance_subparsers.add_parser(
        "summary", help="Get performance summary"
    )
    summary_parser.add_argument(
        "--hours", type=int, help="Number of hours to look back"
    )

    # Performance profiles
    profiles_parser = performance_subparsers.add_parser(
        "profiles", help="Performance profiles management"
    )
    profiles_subparsers = profiles_parser.add_subparsers(
        dest="profiles_action", help="Profile actions"
    )
    profiles_subparsers.add_parser("list", help="List performance profiles")
    show_parser = profiles_subparsers.add_parser("show", help="Show specific profile")
    show_parser.add_argument("profile_id", help="Profile ID to show")

    # Configuration commands
    config_parser = improvement_subparsers.add_parser(
        "config", help="Adaptive configuration management"
    )
    config_subparsers = config_parser.add_subparsers(
        dest="config_action", help="Configuration actions"
    )

    # Get configuration
    get_parser = config_subparsers.add_parser("get", help="Get configuration value")
    get_parser.add_argument("setting_key", help="Configuration setting key")

    # Set configuration
    set_parser = config_subparsers.add_parser("set", help="Set configuration value")
    set_parser.add_argument("setting_key", help="Configuration setting key")
    set_parser.add_argument("value", help="New value")
    set_parser.add_argument("--reason", help="Reason for change")

    # List configuration
    list_parser = config_subparsers.add_parser(
        "list", help="List configuration settings"
    )
    list_parser.add_argument("--category", help="Filter by category")

    # Adapt configuration
    adapt_parser = config_subparsers.add_parser(
        "adapt", help="Adapt configuration based on context"
    )
    adapt_parser.add_argument("--context", help="Context (JSON or key = value pairs)")
    adapt_parser.add_argument(
        "--context - file", dest="context_file", help="Path to JSON file for context"
    )
    adapt_parser.add_argument(
        "--context - b64", dest="context_b64", help="Base64 - encoded JSON for context"
    )

    # Configuration profiles
    profiles_parser = config_subparsers.add_parser(
        "profiles", help="Configuration profiles management"
    )
    profiles_subparsers = profiles_parser.add_subparsers(
        dest="profiles_action", help="Profile actions"
    )
    profiles_subparsers.add_parser("list", help="List configuration profiles")

    create_parser = profiles_subparsers.add_parser(
        "create", help="Create configuration profile"
    )
    create_parser.add_argument("profile_name", help="Profile name")
    create_parser.add_argument("--description", help="Profile description")
    create_parser.add_argument("--context", help="Context (JSON or key = value pairs)")
    create_parser.add_argument(
        "--context - file", dest="context_file", help="Path to JSON file for context"
    )
    create_parser.add_argument(
        "--context - b64", dest="context_b64", help="Base64 - encoded JSON for context"
    )

    apply_parser = profiles_subparsers.add_parser(
        "apply", help="Apply configuration profile"
    )
    apply_parser.add_argument("profile_id", help="Profile ID to apply")

    # Configuration analytics
    analytics_parser = config_subparsers.add_parser(
        "analytics", help="Configuration analytics"
    )
    analytics_parser.add_argument(
        "--days", type=int, help="Number of days to look back"
    )

    # User preference commands
    user_pref_parser = improvement_subparsers.add_parser(
        "user - preferences", help="User preference learning management"
    )
    user_pref_subparsers = user_pref_parser.add_subparsers(
        dest="user_pref_action", help="User preference actions"
    )

    # Record interaction
    record_parser = user_pref_subparsers.add_parser(
        "record", help="Record user interaction"
    )
    record_parser.add_argument("user_id", help="User ID")
    record_parser.add_argument("interaction_type", help="Type of interaction")
    # Flexible context / outcome inputs
    record_parser.add_argument("--context", help="Context (JSON or key = value pairs)")
    record_parser.add_argument(
        "--context - file", dest="context_file", help="Path to JSON file for context"
    )
    record_parser.add_argument(
        "--context - b64", dest="context_b64", help="Base64 - encoded JSON for context"
    )
    record_parser.add_argument(
        "--duration", type=float, help="Interaction duration in seconds"
    )
    record_parser.add_argument("--outcome", help="Outcome (JSON or key = value pairs)")
    record_parser.add_argument(
        "--outcome - file", dest="outcome_file", help="Path to JSON file for outcome"
    )
    record_parser.add_argument(
        "--outcome - b64", dest="outcome_b64", help="Base64 - encoded JSON for outcome"
    )
    record_parser.add_argument(
        "--satisfaction", type=float, help="Satisfaction score (0 - 1)"
    )
    record_parser.add_argument("--feedback", help="User feedback")

    # User preferences
    prefs_parser = user_pref_subparsers.add_parser(
        "preferences", help="User preferences management"
    )
    prefs_subparsers = prefs_parser.add_subparsers(
        dest="prefs_action", help="Preferences actions"
    )

    list_prefs_parser = prefs_subparsers.add_parser(
        "list", help="List user preferences"
    )
    list_prefs_parser.add_argument("user_id", help="User ID")
    list_prefs_parser.add_argument("--category", help="Filter by category")

    get_pref_parser = prefs_subparsers.add_parser(
        "get", help="Get specific user preference"
    )
    get_pref_parser.add_argument("user_id", help="User ID")
    get_pref_parser.add_argument("preference_key", help="Preference key")

    # User profile
    profile_parser = user_pref_subparsers.add_parser(
        "profile", help="Get user profile summary"
    )
    profile_parser.add_argument("user_id", help="User ID")

    # User recommendations
    rec_parser = user_pref_subparsers.add_parser(
        "recommendations", help="Get user recommendations"
    )
    rec_parser.add_argument("user_id", help="User ID")

    # Behavior patterns
    patterns_parser = user_pref_subparsers.add_parser(
        "patterns", help="Get user behavior patterns"
    )
    patterns_parser.add_argument("user_id", help="User ID")

    # Test command
    improvement_subparsers.add_parser(
        "test", help="Test the continuous improvement system"
    )

    # Validation command
    validate_parser = improvement_subparsers.add_parser(
        "validate", help="Validate the continuous improvement system"
    )
    validate_subparsers = validate_parser.add_subparsers(
        dest="validation_action", help="Validation actions"
    )

    # Run comprehensive validation
    validate_subparsers.add_parser("run", help="Run comprehensive validation")

    # View validation reports
    reports_parser = validate_subparsers.add_parser(
        "reports", help="View validation reports"
    )
    reports_subparsers = reports_parser.add_subparsers(
        dest="reports_action", help="Report actions"
    )

    reports_subparsers.add_parser("list", help="List validation reports")

    view_parser = reports_subparsers.add_parser(
        "view", help="View specific validation report"
    )
    view_parser.add_argument("report_id", help="Report ID to view")

    # Test configuration
    config_parser = validate_subparsers.add_parser(
        "config", help="Manage test configuration"
    )
    config_subparsers = config_parser.add_subparsers(
        dest="config_action", help="Configuration actions"
    )

    config_subparsers.add_parser("show", help="Show test configuration")

    set_parser = config_subparsers.add_parser("set", help="Set test configuration")
    set_parser.add_argument("key", help="Configuration key")
    set_parser.add_argument("value", help="Configuration value")


def _handle_validation_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle validation commands."""
    validator = get_continuous_improvement_validator(root)

    if args.validation_action == "run":
        _handle_run_validation(args, validator)
    elif args.validation_action == "reports":
        _handle_validation_reports(args, validator)
    elif args.validation_action == "config":
        _handle_validation_config(args, validator)
    else:
        print(f"Unknown validation action: {args.validation_action}")


def _handle_run_validation(args: argparse.Namespace, validator) -> None:
    """Handle run validation command."""
    print("🧪 Running Comprehensive Continuous Improvement System Validation...")

    try:
        report = validator.run_comprehensive_validation()

        print(f"\n✅ Validation completed successfully!")
        print(f"Report ID: {report.report_id}")
        print(f"System Health Score: {report.system_health_score:.1f}%")

        if report.failed_tests > 0:
            print(f"\n⚠️ {report.failed_tests} tests failed - review recommendations")
        elif report.warning_tests > 0:
            print(
                f"\n⚠️ {report.warning_tests} tests have warnings - consider improvements"
            )
        else:
            print(f"\n🎉 All tests passed! System is healthy.")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error: {e}")


def _handle_validation_reports(args: argparse.Namespace, validator) -> None:
    """Handle validation reports commands."""
    if args.reports_action == "list":
        _handle_list_validation_reports(args, validator)
    elif args.reports_action == "view":
        _handle_view_validation_report(args, validator)
    else:
        print(f"Unknown reports action: {args.reports_action}")


def _handle_list_validation_reports(args: argparse.Namespace, validator) -> None:
    """Handle list validation reports command."""
    try:
        reports_path = validator.validation_path

        if not reports_path.exists():
            print("No validation reports found.")
            return

        print("📋 Validation Reports:")
        print("-" * 50)

        with open(reports_path, "r", encoding="utf - 8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    report_data = json.loads(line.strip())
                    print(f"{line_num}. {report_data['report_id']}")
                    print(f"   Generated: {report_data['generated_at']}")
                    print(f"   Health Score: {report_data['system_health_score']:.1f}%")
                    print(
                        f"   Tests: {report_data['passed_tests']}/{report_data['total_tests']} passed"
                    )
                    print()
                except json.JSONDecodeError:
                    print(f"   Line {line_num}: Invalid JSON format")
                    continue

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error: {e}")


def _handle_view_validation_report(args: argparse.Namespace, validator) -> None:
    """Handle view validation report command."""
    try:
        reports_path = validator.validation_path

        if not reports_path.exists():
            print("No validation reports found.")
            return

        report_id = args.report_id
        found_report = None

        with open(reports_path, "r", encoding="utf - 8") as f:
            for line in f:
                try:
                    report_data = json.loads(line.strip())
                    if report_data["report_id"] == report_id:
                        found_report = report_data
                        break
                except json.JSONDecodeError:
                    continue

        if not found_report:
            print(f"❌ Report not found: {report_id}")
            return

        print(f"📊 Validation Report: {report_id}")
        print("=" * 60)
        print(f"Generated: {found_report['generated_at']}")
        print(f"Total Tests: {found_report['total_tests']}")
        print(f"Passed: {found_report['passed_tests']} ✅")
        print(f"Failed: {found_report['failed_tests']} ❌")
        print(f"Warnings: {found_report['warning_tests']} ⚠️")
        print(f"Skipped: {found_report['skipped_tests']} ⏭️")
        print(f"System Health Score: {found_report['system_health_score']:.1f}%")

        print(f"\n📋 Test Results:")
        for test in found_report["test_results"]:
            status_icon = (
                "✅"
                if test["result"] == "pass"
                else (
                    "❌"
                    if test["result"] == "fail"
                    else "⚠️" if test["result"] == "warning" else "⏭️"
                )
            )
            print(
                f"  {status_icon} {test['name']} ({test['category']}) - {test['duration']:.3f}s"
            )
            if test.get("error_message"):
                print(f"    Error: {test['error_message']}")

        if found_report["recommendations"]:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(found_report["recommendations"], 1):
                print(f"  {i}. {rec}")

        print(f"\n📝 Summary: {found_report['summary']}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error: {e}")


def _handle_validation_config(args: argparse.Namespace, validator) -> None:
    """Handle validation config commands."""
    if args.config_action == "show":
        _handle_show_validation_config(args, validator)
    elif args.config_action == "set":
        _handle_set_validation_config(args, validator)
    else:
        print(f"Unknown config action: {args.config_action}")


def _handle_show_validation_config(args: argparse.Namespace, validator) -> None:
    """Handle show validation config command."""
    try:
        config = validator.test_config

        print("⚙️ Test Configuration:")
        print("-" * 30)

        for key, value in config.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error: {e}")


def _handle_set_validation_config(args: argparse.Namespace, validator) -> None:
    """Handle set validation config command."""
    try:
        key = args.key
        value = args.value

        # Convert value to appropriate type
        if value.lower() in ("true", "false"):
            value = value.lower() == "true"
        elif value.isdigit():
            value = int(value)
        elif value.replace(".", "").isdigit():
            value = float(value)

        # Update configuration
        validator.test_config[key] = value

        # Save configuration
        utils.write_json(validator.test_config_path, validator.test_config)

        print(f"✅ Set {key} = {value}")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error: {e}")
