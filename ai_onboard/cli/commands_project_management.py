"""CLI commands for project management tools."""

import argparse
from pathlib import Path

from ..core.approval_workflow import get_approval_workflow
from ..core.pm_compatibility import (
    get_legacy_progress_dashboard,
    get_legacy_task_completion_detector,
    get_legacy_task_prioritization_engine,
    get_legacy_wbs_sync_engine,
)
from ..core.unicode_utils import print_activity, print_header, print_status


def add_project_management_commands(subparsers):
    """Add project management commands."""

    # Project Management parent parser
    pm_parser = subparsers.add_parser(
        "project",
        help="Project management and tracking tools",
        description=(
            "Comprehensive project management tools including critical path analysis, "
            "progress tracking, and task management."
        ),
    )
    pm_subparsers = pm_parser.add_subparsers(
        dest="project_cmd", help="Project management commands"
    )

    # Critical path analysis
    critical_parser = pm_subparsers.add_parser(
        "critical-path",
        help="Analyze project critical path and dependencies",
        description=(
            "Analyze project timeline, identify critical path, and optimize project schedule."
        ),
    )
    critical_parser.set_defaults(func=handle_critical_path)

    # Progress dashboard
    progress_parser = pm_subparsers.add_parser(
        "progress",
        help="View project progress dashboard",
        description=(
            "Display comprehensive project progress, milestones, and status metrics."
        ),
    )
    progress_parser.set_defaults(func=handle_progress_dashboard)

    # Task completion detection
    completion_parser = pm_subparsers.add_parser(
        "task-completion",
        help="Detect and update completed tasks",
        description="Automatically scan for completed tasks and update project status.",
    )
    completion_parser.set_defaults(func=handle_task_completion)

    # Task prioritization
    priority_parser = pm_subparsers.add_parser(
        "prioritize",
        help="Analyze and prioritize project tasks",
        description=(
            "Automatically prioritize tasks based on urgency, impact, and dependencies."
        ),
    )
    priority_parser.set_defaults(func=handle_task_prioritization)

    # WBS management
    wbs_parser = pm_subparsers.add_parser(
        "wbs",
        help="Work Breakdown Structure management",
        description="Manage and synchronize Work Breakdown Structure elements.",
    )
    wbs_parser.set_defaults(func=handle_wbs_management)

    # Approval workflow
    approval_parser = pm_subparsers.add_parser(
        "approvals",
        help="Manage approval workflows",
        description="View and manage pending approval requests for project changes.",
    )
    approval_parser.set_defaults(func=handle_approval_workflow)


def handle_critical_path(args):
    """Handle critical path analysis."""
    print_header("PROJECT CRITICAL PATH ANALYSIS")

    try:
        print_activity("Analyzing project critical path...")
        engine = get_legacy_task_prioritization_engine(Path("."))
        analysis = engine._engine.analytics.get_project_status()

        print_header("CRITICAL PATH RESULTS")

        critical_path = analysis.get("critical_path", [])
        project_duration = analysis.get("project_duration", 0)
        bottlenecks = analysis.get("bottlenecks", [])

        print(f"🎯 Critical Path Length: {len(critical_path)} tasks")
        print(f"⏱️  Project Duration: {project_duration} days")
        print(f"🚧 Bottlenecks Identified: {len(bottlenecks)}")

        if critical_path:
            print_header("CRITICAL PATH TASKS")
            for i, task_id in enumerate(critical_path[:10]):  # Show first 10
                print(f"{i+1}. {task_id}")
            if len(critical_path) > 10:
                print(f"... and {len(critical_path) - 10} more critical tasks")

        if bottlenecks:
            print_header("PROJECT BOTTLENECKS")
            for bottleneck in bottlenecks[:5]:  # Show first 5
                print(f"⚠️  {bottleneck.get('description', 'Unknown bottleneck')}")

        slack_tasks = analysis.get("slack_analysis", [])
        if slack_tasks:
            flexible_tasks = [t for t in slack_tasks if t.get("slack_days", 0) > 0]
            if flexible_tasks:
                print_header("TASKS WITH FLEXIBILITY")
                for task in flexible_tasks[:3]:  # Show first 3
                    print(
                        f"🔄 {task.get('task_id', 'Unknown')}: {task.get('slack_days', 0)} days slack"
                    )

        print_status("Critical path analysis completed", "success")

    except Exception as e:
        print_status(f"Critical path analysis failed: {e}", "error")


def handle_progress_dashboard(args):
    """Handle project progress dashboard."""
    print_header("PROJECT PROGRESS DASHBOARD")

    try:
        print_activity("Loading progress dashboard...")
        dashboard = get_legacy_progress_dashboard(Path("."))
        status = dashboard.generate_dashboard()

        print_header("PROJECT STATUS OVERVIEW")

        project_name = status.get("project_name", "Unknown Project")
        completion_pct = status.get("completion_percentage", 0)
        total_tasks = status.get("total_tasks", 0)
        completed_tasks = status.get("completed_tasks", 0)
        active_milestones = status.get("active_milestones", 0)

        print(f"📋 Project: {project_name}")
        completion_pct = status.get("completion_percentage", 0)
        print(f"📈 Completion: {completion_pct:.1f}%")
        print(f"✅ Tasks Completed: {completed_tasks}/{total_tasks}")
        print(f"🎯 Active Milestones: {active_milestones}")

        # Show milestone progress
        milestones = status.get("milestones", [])
        if milestones:
            print_header("MILESTONE PROGRESS")
            for milestone in milestones[:5]:  # Show first 5
                name = milestone.get("name", "Unknown")
                progress = milestone.get("progress_percentage", 0)
                status_icon = (
                    "✅" if progress >= 100 else "🔄" if progress > 0 else "⏳"
                )
                print(f"    {status_icon} {name}: {progress:.1f}%")
        # Show recent activity
        recent_activity = status.get("recent_activity", [])
        if recent_activity:
            print_header("RECENT ACTIVITY")
            for activity in recent_activity[:5]:  # Show last 5
                print(f"📝 {activity.get('description', 'Unknown activity')}")

        # Show upcoming deadlines
        upcoming = status.get("upcoming_deadlines", [])
        if upcoming:
            print_header("UPCOMING DEADLINES")
            for deadline in upcoming[:3]:  # Show next 3
                print(
                    f"⏰ {deadline.get('description', 'Unknown deadline')} - {deadline.get('days_remaining', 0)} days"
                )

        print_status("Progress dashboard loaded successfully", "success")

    except Exception as e:
        print_status(f"Progress dashboard failed: {e}", "error")


def handle_task_completion(args):
    """Handle automatic task completion detection."""
    print_header("TASK COMPLETION DETECTION")

    try:
        print_activity("Scanning for completed tasks...")
        detector = get_legacy_task_completion_detector(Path("."))
        scan_results = detector.detect_completed_tasks()

        print_header("COMPLETION SCAN RESULTS")

        total_tasks = scan_results.get("total_tasks", 0)
        completed_tasks = scan_results.get("completed_tasks", 0)
        newly_completed = scan_results.get("newly_completed", 0)

        print(f"📊 Total Tasks: {total_tasks}")
        print(f"✅ Completed Tasks: {completed_tasks}")
        print(f"🆕 Newly Completed: {newly_completed}")

        if newly_completed > 0:
            print_header("NEWLY COMPLETED TASKS")
            new_tasks = scan_results.get("new_completions", [])
            for task in new_tasks[:5]:  # Show first 5
                print(
                    f"✅ {task.get('task_id', 'Unknown')} - {task.get('completion_reason', 'Auto-detected')}"
                )

        # Show completion statistics
        completion_rate = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        )
        print(f"📊 Completion Rate: {completion_rate:.1f}%")
        # Show tasks by category
        by_category = scan_results.get("completion_by_category", {})
        if by_category:
            print_header("COMPLETION BY CATEGORY")
            for category, stats in by_category.items():
                cat_completed = stats.get("completed", 0)
                cat_total = stats.get("total", 0)
                if cat_total > 0:
                    cat_rate = cat_completed / cat_total * 100
                    print(f"  📈 {category}: {cat_rate:.1f}%")
        if newly_completed > 0:
            print_status(
                f"Successfully detected {newly_completed} newly completed tasks!",
                "success",
            )
        else:
            print_status("No new task completions detected", "info")

    except Exception as e:
        print_status(f"Task completion detection failed: {e}", "error")


def handle_task_prioritization(args):
    """Handle automatic task prioritization."""
    print_header("TASK PRIORITIZATION ANALYSIS")

    try:
        print_activity("Analyzing task priorities...")
        engine = get_legacy_task_prioritization_engine(Path("."))
        result = engine.prioritize_all_tasks()
        priorities = result

        print_header("PRIORITY ANALYSIS RESULTS")

        total_tasks = priorities.get("total_tasks", 0)
        high_priority = priorities.get("high_priority_count", 0)
        medium_priority = priorities.get("medium_priority_count", 0)
        low_priority = priorities.get("low_priority_count", 0)

        print(f"📊 Total Tasks: {total_tasks}")
        print(f"🔴 High Priority: {high_priority}")
        print(f"🟠 Medium Priority: {medium_priority}")
        print(f"🟢 Low Priority: {low_priority}")

        # Show priority breakdown
        priority_breakdown = priorities.get("priority_breakdown", {})
        if priority_breakdown:
            print_header("PRIORITY BREAKDOWN")
            for priority_level, tasks in priority_breakdown.items():
                print(f"\n{priority_level.upper()} PRIORITY TASKS:")
                for task in tasks[:3]:  # Show first 3 per priority
                    task_id = task.get("task_id", "Unknown")
                    urgency = task.get("urgency_score", 0)
                    impact = task.get("impact_score", 0)
                    print(f"    {task_id}: urgency={urgency:.1f}, impact={impact:.1f}")
                if len(tasks) > 3:
                    print(
                        f"    ... and \
                            {len(tasks) - 3} more {priority_level} priority tasks"
                    )

        # Show prioritization factors
        factors = priorities.get("prioritization_factors", {})
        if factors:
            print_header("PRIORITIZATION FACTORS")
            for factor, weight in factors.items():
                print(f"  {factor}: {weight:.2f}")
        print_status("Task prioritization analysis completed", "success")

    except Exception as e:
        print_status(f"Task prioritization failed: {e}", "error")


def handle_wbs_management(args):
    """Handle WBS management and synchronization."""
    print_header("WORK BREAKDOWN STRUCTURE MANAGEMENT")

    try:
        print_activity("Loading WBS management system...")
        wbs_engine = get_legacy_wbs_sync_engine(Path("."))

        # Get WBS status
        status = wbs_engine.get_wbs_status()

        print_header("WBS STATUS OVERVIEW")

        total_elements = status.get("total_elements", 0)
        synchronized = status.get("synchronized_elements", 0)
        conflicts = status.get("conflicts_found", 0)
        consistency_score = status.get("consistency_score", 0)

        print(f"📊 Total WBS Elements: {total_elements}")
        print(f"🔄 Synchronized Elements: {synchronized}")
        print(f"⚠️  Conflicts Found: {conflicts}")
        print(f"🔗 Consistency Score: {consistency_score:.1f}%")
        # Show WBS hierarchy summary
        hierarchy = status.get("hierarchy_summary", {})
        if hierarchy:
            print_header("WBS HIERARCHY SUMMARY")
            for level, count in hierarchy.items():
                print(f"  {level}: {count} elements")

        # Show conflicts if any
        if conflicts > 0:
            conflict_details = status.get("conflict_details", [])
            print_header("WBS CONFLICTS DETECTED")
            for conflict in conflict_details[:3]:  # Show first 3
                print(f"⚠️  {conflict.get('description', 'Unknown conflict')}")

        # Show synchronization recommendations
        recommendations = status.get("sync_recommendations", [])
        if recommendations:
            print_header("SYNCHRONIZATION RECOMMENDATIONS")
            for rec in recommendations[:3]:  # Show first 3
                print(f"💡 {rec}")

        if conflicts == 0 and consistency_score >= 90:
            print_status("WBS is well-synchronized and consistent!", "success")
        elif conflicts > 0:
            print_status(
                f"Found {conflicts} WBS conflicts requiring attention", "warning"
            )
        else:
            print_status("WBS synchronization completed with minor issues", "info")

    except Exception as e:
        print_status(f"WBS management failed: {e}", "error")


def handle_approval_workflow(args):
    """Handle approval workflow management."""
    print_header("APPROVAL WORKFLOW MANAGEMENT")

    try:
        print_activity("Loading approval workflow...")
        workflow = get_approval_workflow(Path("."))
        pending = workflow.get_pending_requests()

        print_header("APPROVAL STATUS OVERVIEW")

        total_pending = len(pending)
        urgent_count = len(
            [r for r in pending if r.urgency == "urgent" or r.urgency == "critical"]
        )
        normal_count = len([r for r in pending if r.urgency == "normal"])
        low_count = len([r for r in pending if r.urgency == "low"])

        print(f"⏳ Total Pending: {total_pending}")
        print(f"🚨 Urgent/Critical: {urgent_count}")
        print(f"📋 Normal Priority: {normal_count}")
        print(f"📝 Low Priority: {low_count}")

        if pending:
            print_header("PENDING APPROVALS")

            # Sort by urgency
            urgent_requests = [
                r for r in pending if r.urgency in ["urgent", "critical"]
            ]
            normal_requests = [r for r in pending if r.urgency == "normal"]
            low_requests = [r for r in pending if r.urgency == "low"]

            # Display urgent first
            for req in urgent_requests[:3]:  # Show first 3 urgent
                print(
                    f"🚨 [{req.urgency.upper()}] {req.proposed_actions[0].description if req.proposed_actions else 'Unknown action'}"
                )
                print(
                    f"    Context: {req.context[:100]}{'...' if len(req.context) > 100 else ''}"
                )

            for req in normal_requests[:2]:  # Show first 2 normal
                print(
                    f"📋 [NORMAL] {req.proposed_actions[0].description if req.proposed_actions else 'Unknown action'}"
                )

            if len(pending) > 5:
                remaining = len(pending) - 5
                print(f"    ... and {remaining} more pending approvals")

        # Show approval statistics
        stats = workflow.get_approval_summary()
        approved_count = stats.get("approved_count", 0)
        rejected_count = stats.get("rejected_count", 0)
        expired_count = stats.get("expired_count", 0)

        print_header("APPROVAL STATISTICS")
        print(f"✅ Approved: {approved_count}")
        print(f"❌ Rejected: {rejected_count}")
        print(f"⏰ Expired: {expired_count}")

        if total_pending > 0:
            print_status(f"{total_pending} approvals pending review", "warning")
        else:
            print_status("No pending approvals - all caught up!", "success")

    except Exception as e:
        print_status(f"Approval workflow management failed: {e}", "error")


def handle_project_management_commands(args):
    """Handle project management command routing."""
    if hasattr(args, "func"):
        args.func(args)
    else:
        print(
            "No project management command specified. Use --help for available commands."
        )
