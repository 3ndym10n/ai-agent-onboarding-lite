"""
CLI commands for User Experience Enhancements.

This module provides command - line interfaces for:
- Managing UX interventions and assistance
- Tracking user satisfaction and feedback
- Analyzing user journeys and experience metrics
- Configuring UX enhancement settings
"""

import argparse
from pathlib import Path

from ..core.ui_enhancement_system import get_ui_enhancement_system
from ..core.user_experience_enhancements import UXEventType, get_ux_enhancement_system
from .visual_components import create_chart, create_status_indicator


def add_ux_enhancement_commands(subparsers):
    """Add UX enhancement commands to the CLI."""

    # Main UX command
    ux_parser = subparsers.add_parser(
        "ux", help="User experience enhancements and analytics"
    )
    ux_sub = ux_parser.add_subparsers(dest="ux_cmd", required=True)

    # Interventions command
    interventions_parser = ux_sub.add_parser(
        "interventions", help="Manage UX interventions"
    )
    int_sub = interventions_parser.add_subparsers(dest="int_action", required=True)

    # List interventions
    int_sub.add_parser("list", help="List pending interventions")

    # Show intervention
    show_int_parser = int_sub.add_parser("show", help="Show intervention details")
    show_int_parser.add_argument("intervention_id", help="Intervention ID")

    # Dismiss intervention
    dismiss_parser = int_sub.add_parser("dismiss", help="Dismiss intervention")
    dismiss_parser.add_argument("intervention_id", help="Intervention ID")
    dismiss_parser.add_argument(
        "--followed", action="store_true", help="Mark as followed"
    )

    # Feedback command
    feedback_parser = ux_sub.add_parser(
        "feedback", help="Provide satisfaction feedback"
    )
    feedback_parser.add_argument(
        "--score",
        type=int,
        choices=[1, 2, 3, 4, 5],
        required=True,
        help="Satisfaction score (1 = very dissatisfied, 5 = very satisfied)",
    )
    feedback_parser.add_argument(
        "--context", default="general", help="Feedback context"
    )
    feedback_parser.add_argument("--message", help="Additional feedback message")

    # Journey command
    journey_parser = ux_sub.add_parser("journey", help="User journey tracking")
    journey_sub = journey_parser.add_subparsers(dest="journey_action", required=True)

    # Show journey
    show_journey_parser = journey_sub.add_parser("show", help="Show current journey")
    show_journey_parser.add_argument(
        "--goal", default="general_usage", help="Journey goal"
    )

    # Journey analytics
    journey_sub.add_parser("analytics", help="Journey analytics and insights")

    # Analytics command
    analytics_parser = ux_sub.add_parser("analytics", help="UX analytics and metrics")
    analytics_sub = analytics_parser.add_subparsers(
        dest="analytics_action", required=True
    )

    # User analytics
    user_analytics_parser = analytics_sub.add_parser(
        "user", help="User experience analytics"
    )
    user_analytics_parser.add_argument(
        "--detailed", action="store_true", help="Detailed analytics"
    )

    # Satisfaction analytics
    analytics_sub.add_parser("satisfaction", help="Satisfaction trends and analysis")

    # Error analytics
    analytics_sub.add_parser("errors", help="Error pattern analysis")

    # Config command
    config_parser = ux_sub.add_parser("config", help="Configure UX enhancements")
    config_sub = config_parser.add_subparsers(dest="config_action", required=True)

    # Show config
    config_sub.add_parser("show", help="Show UX configuration")

    # Update config
    update_parser = config_sub.add_parser("update", help="Update UX configuration")
    update_parser.add_argument(
        "--enable - proactive - help", type=bool, help="Enable proactive help"
    )
    update_parser.add_argument(
        "--enable - error - recovery", type=bool, help="Enable error recovery"
    )
    update_parser.add_argument(
        "--enable - workflow - optimization",
        type=bool,
        help="Enable workflow optimization",
    )
    update_parser.add_argument(
        "--satisfaction - frequency",
        choices=["milestone", "periodic", "never"],
        help="Satisfaction request frequency",
    )

    # Test command (for development)
    test_parser = ux_sub.add_parser("test", help="Test UX enhancements")
    test_parser.add_argument(
        "--trigger - error", action="store_true", help="Trigger test error"
    )
    test_parser.add_argument(
        "--trigger - onboarding", action="store_true", help="Trigger onboarding"
    )
    test_parser.add_argument(
        "--trigger - workflow", help="Trigger workflow optimization"
    )


def handle_ux_enhancement_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle UX enhancement commands."""

    ux_system = get_ux_enhancement_system(root)
    user_id = "default"  # Could be extracted from environment or config

    if args.ux_cmd == "interventions":
        _handle_interventions_commands(args, ux_system, root, user_id)
    elif args.ux_cmd == "feedback":
        _handle_feedback(args, ux_system, root, user_id)
    elif args.ux_cmd == "journey":
        _handle_journey_commands(args, ux_system, root, user_id)
    elif args.ux_cmd == "analytics":
        _handle_analytics_commands(args, ux_system, root, user_id)
    elif args.ux_cmd == "config":
        _handle_config_commands(args, ux_system, root, user_id)
    elif args.ux_cmd == "test":
        _handle_test_commands(args, ux_system, root, user_id)
    else:
        print(f"Unknown UX command: {args.ux_cmd}")


def _handle_interventions_commands(
    args: argparse.Namespace, ux_system, root: Path, user_id: str
) -> None:
    """Handle intervention management commands."""
    status = create_status_indicator(root, user_id)
    ui_system = get_ui_enhancement_system(root)

    if args.int_action == "list":
        print(ui_system.format_output("🔔 Pending Interventions", "primary", user_id))
        print("=" * 40)
        print()

        interventions = ux_system.get_pending_interventions(user_id)

        if not interventions:
            print(status.info("No pending interventions"))
            return

        for i, intervention in enumerate(interventions, 1):
            priority_icons = {1: "🔵", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🚨"}
            priority_icon = priority_icons.get(intervention.priority, "⚪")

            print(f"{priority_icon} {intervention.intervention_id}")
            print(f"   Type: {intervention.intervention_type.value}")
            print(f"   Priority: {intervention.priority}/5")
            print(
                f"   Created: {intervention.created_at.strftime('%Y -% m -% d %H:%M')}"
            )
            print()

            # Show message preview
            message_preview = intervention.message.split("\n")[0][:80]
            if len(intervention.message) > 80:
                message_preview += "..."
            print(f"   Preview: {message_preview}")
            print()

        print("💡 Use 'ux interventions show <id>' for details")

    elif args.int_action == "show":
        intervention = ux_system.active_interventions.get(args.intervention_id)

        if not intervention:
            print(status.error(f"Intervention not found: {args.intervention_id}"))
            return

        print(ui_system.format_output(f"🔔 Intervention Details", "primary", user_id))
        print("=" * 50)
        print()

        print(f"ID: {intervention.intervention_id}")
        print(f"Type: {intervention.intervention_type.value}")
        print(f"Priority: {intervention.priority}/5")
        print(f"Trigger: {intervention.trigger_event}")
        print(f"Created: {intervention.created_at.strftime('%Y -% m -% d %H:%M:%S')}")

        if intervention.delivered_at:
            print(
                f"Delivered: {intervention.delivered_at.strftime('%Y -% m -% d %H:%M:%S')}"
            )

        if intervention.dismissed_at:
            print(
                f"Dismissed: {intervention.dismissed_at.strftime('%Y -% m -% d %H:%M:%S')}"
            )
            print(
                f"User Followed: {'Yes' if intervention.user_followed_suggestion else 'No'}"
            )

        print()
        print(ui_system.format_output("📝 Message:", "info", user_id))
        print(intervention.message)

        if intervention.suggested_actions:
            print()
            print(
                ui_system.format_output("💡 Suggested Actions:", "secondary", user_id)
            )
            for i, action in enumerate(intervention.suggested_actions, 1):
                print(f"  {i}. {action}")

    elif args.int_action == "dismiss":
        intervention = ux_system.active_interventions.get(args.intervention_id)

        if not intervention:
            print(status.error(f"Intervention not found: {args.intervention_id}"))
            return

        ux_system.dismiss_intervention(args.intervention_id, args.followed)

        if args.followed:
            print(status.success("Intervention dismissed and marked as followed"))
        else:
            print(status.success("Intervention dismissed"))


def _handle_feedback(
    args: argparse.Namespace, ux_system, root: Path, user_id: str
) -> None:
    """Handle satisfaction feedback."""
    status = create_status_indicator(root, user_id)

    # Record satisfaction
    ux_system.satisfaction_tracker.record_satisfaction(
        user_id=user_id,
        context=args.context,
        score=args.score,
        feedback=args.message or "",
    )

    # Provide feedback on the feedback
    if args.score >= 4:
        print(
            status.success(
                f"Thank you for the positive feedback! (Score: {args.score}/5)"
            )
        )
        print("💡 Consider sharing what's working well to help us improve further")
    elif args.score == 3:
        print(status.info(f"Thank you for the feedback! (Score: {args.score}/5)"))
        print("💡 Let us know what could make your experience better")
    else:
        print(
            status.warning(f"Thank you for the honest feedback (Score: {args.score}/5)")
        )
        print("💡 We'll work on addressing the issues you've experienced")
        print(
            "💡 Try 'suggest' for personalized recommendations to improve your experience"
        )

    # Record UX event
    ux_system.record_ux_event(
        UXEventType.SATISFACTION_FEEDBACK,
        user_id,
        context={"score": args.score, "feedback_context": args.context},
    )


def _handle_journey_commands(
    args: argparse.Namespace, ux_system, root: Path, user_id: str
) -> None:
    """Handle user journey commands."""
    ui_system = get_ui_enhancement_system(root)

    if args.journey_action == "show":
        journey = ux_system.get_user_journey(user_id, args.goal)

        print(
            ui_system.format_output(f"🗺️ User Journey: {args.goal}", "primary", user_id)
        )
        print("=" * 50)
        print()

        print(f"Journey ID: {journey.journey_id}")
        print(f"Started: {journey.started_at.strftime('%Y -% m -% d %H:%M:%S')}")
        print(f"Current Step: {journey.current_step}")

        if journey.completed_at:
            print(
                f"Completed: {journey.completed_at.strftime('%Y -% m -% d %H:%M:%S')}"
            )
            print(f"Success: {'Yes' if journey.success else 'No'}")

        print()
        print(f"📊 Journey Metrics:")
        print(f"   Total Commands: {journey.total_commands}")
        print(f"   Successful Commands: {journey.successful_commands}")
        print(f"   Errors Encountered: {journey.errors_encountered}")
        print(f"   Help Requests: {journey.help_requests}")

        if journey.total_commands > 0:
            success_rate = journey.successful_commands / journey.total_commands * 100
            print(f"   Success Rate: {success_rate:.1f}%")

        print()
        if journey.steps_completed:
            print(f"✅ Completed Steps:")
            for step in journey.steps_completed:
                print(f"   • {step}")

        if journey.steps_failed:
            print()
            print(f"❌ Failed Steps:")
            for step in journey.steps_failed:
                print(f"   • {step}")

        if journey.lessons_learned:
            print()
            print(f"📚 Lessons Learned:")
            for lesson in journey.lessons_learned:
                print(f"   • {lesson}")

    elif args.journey_action == "analytics":
        print(ui_system.format_output("📈 Journey Analytics", "primary", user_id))
        print("=" * 40)
        print()

        # Get all journeys for user
        user_journeys = [
            j for j in ux_system.user_journeys.values() if j.user_id == user_id
        ]

        if not user_journeys:
            print("No journey data available")
            return

        # Calculate aggregate metrics
        total_journeys = len(user_journeys)
        completed_journeys = len([j for j in user_journeys if j.completed_at])
        successful_journeys = len([j for j in user_journeys if j.success])

        print(f"Total Journeys: {total_journeys}")
        print(f"Completed: {completed_journeys}")
        print(f"Successful: {successful_journeys}")

        if completed_journeys > 0:
            success_rate = successful_journeys / completed_journeys * 100
            print(f"Success Rate: {success_rate:.1f}%")

        # Most common steps
        all_completed_steps = []
        all_failed_steps = []

        for journey in user_journeys:
            all_completed_steps.extend(journey.steps_completed)
            all_failed_steps.extend(journey.steps_failed)

        if all_completed_steps:
            from collections import Counter

            step_counts = Counter(all_completed_steps)

            print(f"\n🏆 Most Completed Steps:")
            for step, count in step_counts.most_common(5):
                print(f"   • {step}: {count} times")

        if all_failed_steps:
            from collections import Counter

            failed_counts = Counter(all_failed_steps)

            print(f"\n⚠️ Most Failed Steps:")
            for step, count in failed_counts.most_common(3):
                print(f"   • {step}: {count} times")


def _handle_analytics_commands(
    args: argparse.Namespace, ux_system, root: Path, user_id: str
) -> None:
    """Handle UX analytics commands."""
    ui_system = get_ui_enhancement_system(root)

    if args.analytics_action == "user":
        analytics = ux_system.get_ux_analytics(user_id)

        print(
            ui_system.format_output("📊 User Experience Analytics", "primary", user_id)
        )
        print("=" * 50)
        print()

        print(f"User ID: {analytics['user_id']}")
        print(f"Expertise Level: {analytics['expertise_level']}")
        print()

        print(f"📈 Usage Metrics:")
        print(f"   Total Commands: {analytics['total_commands']}")
        print(f"   Unique Commands: {analytics['unique_commands']}")
        print(f"   Error Rate: {analytics['error_rate']:.1%}")
        print(f"   Help Request Rate: {analytics['help_request_rate']:.1%}")
        print()

        satisfaction = analytics["satisfaction"]
        print(f"😊 Satisfaction:")
        print(f"   Average Score: {satisfaction['average']:.1f}/5")
        print(f"   Trend: {satisfaction['trend']}")
        print(f"   Total Responses: {satisfaction['total_responses']}")

        if satisfaction["recent_scores"]:
            chart = create_chart(root, user_id)
            scores_dict = {
                f"Response {i + 1}": score
                for i, score in enumerate(satisfaction["recent_scores"][-5:])
            }
            print(f"\n📈 Recent Satisfaction Scores:")
            print(chart.bar_chart(scores_dict, max_width=40))

        print()
        print(f"🔔 Current State:")
        print(f"   Recent Events (7 days): {analytics['recent_events']}")
        print(f"   Active Interventions: {analytics['active_interventions']}")

        if args.detailed:
            print(f"\n🔍 Detailed Insights:")

            if analytics["error_rate"] > 0.1:
                print(
                    f"   ⚠️ High error rate detected - consider additional help resources"
                )

            if analytics["help_request_rate"] > 0.2:
                print(f"   💡 Frequent help requests - user may benefit from tutorials")

            if satisfaction["average"] < 3:
                print(f"   😟 Below average satisfaction - urgent attention needed")
            elif satisfaction["trend"] == "declining":
                print(
                    f"   📉 Declining satisfaction trend - investigate recent changes"
                )

    elif args.analytics_action == "satisfaction":
        print(ui_system.format_output("😊 Satisfaction Analytics", "primary", user_id))
        print("=" * 40)
        print()

        satisfaction_data = ux_system.satisfaction_tracker.get_satisfaction_trend(
            user_id
        )

        if satisfaction_data["trend"] == "no_data":
            print("No satisfaction data available")
            print("💡 Use 'ux feedback --score <1 - 5>' to provide feedback")
            return

        print(f"Average Satisfaction: {satisfaction_data['average']:.1f}/5")
        print(f"Trend: {satisfaction_data['trend']}")
        print(f"Total Responses: {satisfaction_data['total_responses']}")

        if satisfaction_data["recent_scores"]:
            chart = create_chart(root, user_id)

            # Create satisfaction level distribution
            from collections import Counter

            score_counts = Counter(satisfaction_data["recent_scores"])
            score_labels = {
                1: "Very Dissatisfied",
                2: "Dissatisfied",
                3: "Neutral",
                4: "Satisfied",
                5: "Very Satisfied",
            }

            distribution = {}
            for score in range(1, 6):
                count = score_counts.get(score, 0)
                if count > 0:
                    distribution[score_labels[score]] = count

            if distribution:
                print(f"\n📊 Satisfaction Distribution:")
                print(chart.bar_chart(distribution, max_width=50))

    elif args.analytics_action == "errors":
        print(ui_system.format_output("❌ Error Pattern Analysis", "primary", user_id))
        print("=" * 40)
        print()

        # Get error events
        error_events = [
            e
            for e in ux_system.ux_events
            if e.user_id == user_id and e.event_type == UXEventType.ERROR_ENCOUNTER
        ]

        if not error_events:
            print("No error events recorded")
            return

        print(f"Total Error Events: {len(error_events)}")
        print()

        # Analyze error patterns
        from collections import Counter

        error_types = Counter()
        error_commands = Counter()

        for event in error_events:
            error_type = event.context.get("error_type", "Unknown")
            command = event.command or "unknown"

            error_types[error_type] += 1
            error_commands[command] += 1

        if error_types:
            print(f"🔍 Most Common Error Types:")
            for error_type, count in error_types.most_common(5):
                print(f"   • {error_type}: {count} occurrences")

        print()
        if error_commands:
            print(f"⚠️ Commands with Most Errors:")
            for command, count in error_commands.most_common(5):
                print(f"   • {command}: {count} errors")


def _handle_config_commands(
    args: argparse.Namespace, ux_system, root: Path, user_id: str
) -> None:
    """Handle UX configuration commands."""
    ui_system = get_ui_enhancement_system(root)
    status = create_status_indicator(root, user_id)

    if args.config_action == "show":
        print(
            ui_system.format_output(
                "⚙️ UX Enhancement Configuration", "primary", user_id
            )
        )
        print("=" * 50)
        print()

        config = ux_system.config

        print(f"Proactive Help: {'✅' if config['enable_proactive_help'] else '❌'}")
        print(f"Error Recovery: {'✅' if config['enable_error_recovery'] else '❌'}")
        print(
            f"Workflow Optimization: {'✅' if config['enable_workflow_optimization'] else '❌'}"
        )
        print(
            f"Satisfaction Tracking: {'✅' if config['enable_satisfaction_tracking'] else '❌'}"
        )
        print(f"Onboarding: {'✅' if config['onboarding_enabled'] else '❌'}")
        print()

        print(
            f"Intervention Cooldown: {config['intervention_cooldown_minutes']} minutes"
        )
        print(f"Max Interventions / Session: {config['max_interventions_per_session']}")
        print(f"Satisfaction Frequency: {config['satisfaction_request_frequency']}")

    elif args.config_action == "update":
        config = ux_system.config
        updates = []

        if args.enable_proactive_help is not None:
            config["enable_proactive_help"] = args.enable_proactive_help
            updates.append(f"Proactive help: {args.enable_proactive_help}")

        if args.enable_error_recovery is not None:
            config["enable_error_recovery"] = args.enable_error_recovery
            updates.append(f"Error recovery: {args.enable_error_recovery}")

        if args.enable_workflow_optimization is not None:
            config["enable_workflow_optimization"] = args.enable_workflow_optimization
            updates.append(
                f"Workflow optimization: {args.enable_workflow_optimization}"
            )

        if args.satisfaction_frequency:
            config["satisfaction_request_frequency"] = args.satisfaction_frequency
            updates.append(f"Satisfaction frequency: {args.satisfaction_frequency}")

        if updates:
            # Save configuration
            config_file = ux_system.data_dir / "ux_config.json"
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)

            print(status.success("UX configuration updated:"))
            for update in updates:
                print(f"   • {update}")
        else:
            print(status.info("No configuration changes specified"))


def _handle_test_commands(
    args: argparse.Namespace, ux_system, root: Path, user_id: str
) -> None:
    """Handle test commands for development."""
    status = create_status_indicator(root, user_id)

    if args.trigger_error:
        print(status.info("Triggering test error intervention..."))

        # Create test error event
        ux_system.record_ux_event(
            UXEventType.ERROR_ENCOUNTER,
            user_id,
            context={"error_type": "TestError", "test_mode": True},
            command="test - command",
            success=False,
            error_details="This is a test error for UX enhancement testing",
        )

        # Check for interventions
        interventions = ux_system.get_pending_interventions(user_id)
        if interventions:
            print(status.success(f"Created {len(interventions)} intervention(s)"))
            print("💡 Use 'ux interventions list' to see them")
        else:
            print(status.warning("No interventions created"))

    elif args.trigger_onboarding:
        print(status.info("Triggering onboarding intervention..."))

        # Create onboarding event
        ux_system.record_ux_event(
            UXEventType.USER_ONBOARDING, user_id, context={"test_mode": True}
        )

        interventions = ux_system.get_pending_interventions(user_id)
        if interventions:
            print(status.success(f"Created {len(interventions)} intervention(s)"))
        else:
            print(status.warning("No onboarding interventions created"))

    elif args.trigger_workflow:
        print(
            status.info(
                f"Triggering workflow optimization for: {args.trigger_workflow}"
            )
        )

        # Simulate workflow commands
        workflow_commands = {
            "project_setup": ["charter", "plan"],
            "optimization": ["validate", "kaizen"],
            "ai_setup": ["ai - agent", "aaol"],
        }

        commands = workflow_commands.get(
            args.trigger_workflow, ["test - cmd1", "test - cmd2"]
        )

        for cmd in commands:
            ux_system.record_ux_event(
                UXEventType.COMMAND_EXECUTION,
                user_id,
                command=cmd,
                context={"test_mode": True},
            )

        interventions = ux_system.get_pending_interventions(user_id)
        if interventions:
            print(status.success(f"Created {len(interventions)} intervention(s)"))
        else:
            print(status.warning("No workflow interventions created"))

    else:
        print(status.info("Available test options:"))
        print("   --trigger - error: Test error recovery")
        print("   --trigger - onboarding: Test onboarding assistance")
        print("   --trigger - workflow <type>: Test workflow optimization")
