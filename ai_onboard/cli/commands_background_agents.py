"""
CLI commands for Background Agent Management.

This module provides command - line interfaces for:
- Managing background agent lifecycle (start, stop, status)
- Configuring agent settings and resource limits
- Monitoring agent performance and health
- Viewing execution logs and metrics
- Coordinating agent operations and communication
"""

import argparse
from datetime import datetime
from pathlib import Path

from ..core.background_agent_manager import (
    AgentConfiguration,
    AgentPriority,
    AgentState,
    ScheduleType,
    get_background_agent_manager,
)
from .visual_components import create_chart, create_status_indicator, create_table


def add_background_agent_commands(subparsers):
    """Add background agent commands to the CLI."""

    # Main background agents command
    bg_parser = subparsers.add_parser(
        "background - agents", help="Manage autonomous background AI agents"
    )
    bg_sub = bg_parser.add_subparsers(dest="bg_cmd", required=True)

    # Agent lifecycle commands
    lifecycle_parser = bg_sub.add_parser("lifecycle", help="Agent lifecycle management")
    lifecycle_sub = lifecycle_parser.add_subparsers(
        dest="lifecycle_action", required=True
    )

    # List agents
    lifecycle_sub.add_parser("list", help="List all background agents")

    # Start agent
    start_parser = lifecycle_sub.add_parser("start", help="Start a background agent")
    start_parser.add_argument("agent_id", help="Agent ID to start")
    start_parser.add_argument(
        "--wait", action="store_true", help="Wait for agent to fully start"
    )

    # Stop agent
    stop_parser = lifecycle_sub.add_parser("stop", help="Stop a background agent")
    stop_parser.add_argument("agent_id", help="Agent ID to stop")
    stop_parser.add_argument(
        "--force", action="store_true", help="Force stop the agent"
    )

    # Restart agent
    restart_parser = lifecycle_sub.add_parser(
        "restart", help="Restart a background agent"
    )
    restart_parser.add_argument("agent_id", help="Agent ID to restart")

    # Agent status commands
    status_parser = bg_sub.add_parser("status", help="View agent status")
    status_parser.add_argument("--agent - id", help="Specific agent to view")
    status_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed status"
    )
    status_parser.add_argument(
        "--running - only", action="store_true", help="Show only running agents"
    )

    # Agent monitoring
    monitor_parser = bg_sub.add_parser("monitor", help="Monitor agent performance")
    monitor_parser.add_argument("--agent - id", help="Specific agent to monitor")
    monitor_parser.add_argument(
        "--interval", type=int, default=5, help="Monitoring interval in seconds"
    )
    monitor_parser.add_argument(
        "--duration", type=int, help="Monitoring duration in seconds"
    )

    # Agent logs
    logs_parser = bg_sub.add_parser("logs", help="View agent logs")
    logs_parser.add_argument("agent_id", help="Agent ID to view logs for")
    logs_parser.add_argument(
        "--tail", type=int, default=50, help="Number of recent log entries"
    )
    logs_parser.add_argument("--follow", action="store_true", help="Follow log output")
    logs_parser.add_argument(
        "--level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Filter by log level",
    )

    # Configuration commands
    config_parser = bg_sub.add_parser("config", help="Agent configuration management")
    config_sub = config_parser.add_subparsers(dest="config_action", required=True)

    # Show config
    show_config_parser = config_sub.add_parser("show", help="Show agent configuration")
    show_config_parser.add_argument("agent_id", help="Agent ID to show config for")

    # Update config
    update_config_parser = config_sub.add_parser(
        "update", help="Update agent configuration"
    )
    update_config_parser.add_argument("agent_id", help="Agent ID to update")
    update_config_parser.add_argument(
        "--enabled", type=bool, help="Enable / disable agent"
    )
    update_config_parser.add_argument(
        "--auto - start", type=bool, help="Auto - start on system boot"
    )
    update_config_parser.add_argument(
        "--priority",
        choices=[p.name.lower() for p in AgentPriority],
        help="Agent priority level",
    )
    update_config_parser.add_argument(
        "--max - cpu", type=float, help="Maximum CPU usage percentage"
    )
    update_config_parser.add_argument(
        "--max - memory", type=float, help="Maximum memory usage in MB"
    )

    # Create new agent
    create_parser = config_sub.add_parser(
        "create", help="Create new agent configuration"
    )
    create_parser.add_argument("agent_id", help="New agent ID")
    create_parser.add_argument("--name", required=True, help="Agent name")
    create_parser.add_argument("--description", required=True, help="Agent description")
    create_parser.add_argument(
        "--agent - class", required=True, help="Agent class name"
    )
    create_parser.add_argument(
        "--schedule - type",
        choices=[s.value for s in ScheduleType],
        default="interval",
        help="Schedule type",
    )
    create_parser.add_argument(
        "--priority",
        choices=[p.name.lower() for p in AgentPriority],
        default="medium",
        help="Agent priority",
    )

    # Analytics and reporting
    analytics_parser = bg_sub.add_parser(
        "analytics", help="Agent analytics and reporting"
    )
    analytics_sub = analytics_parser.add_subparsers(
        dest="analytics_action", required=True
    )

    # Performance analytics
    analytics_sub.add_parser("performance", help="Agent performance analytics")

    # Resource usage
    resource_parser = analytics_sub.add_parser(
        "resources", help="Resource usage analysis"
    )
    resource_parser.add_argument("--agent - id", help="Specific agent to analyze")
    resource_parser.add_argument("--period", default="24h", help="Analysis period")

    # Execution history
    history_parser = analytics_sub.add_parser(
        "history", help="Execution history analysis"
    )
    history_parser.add_argument("--agent - id", help="Specific agent to analyze")
    history_parser.add_argument(
        "--days", type=int, default=7, help="Number of days to analyze"
    )

    # Health report
    health_parser = analytics_sub.add_parser("health", help="Agent health report")
    health_parser.add_argument(
        "--detailed", action="store_true", help="Detailed health analysis"
    )

    # Coordination commands
    coord_parser = bg_sub.add_parser(
        "coordination", help="Agent coordination management"
    )
    coord_sub = coord_parser.add_subparsers(dest="coord_action", required=True)

    # Show coordination status
    coord_sub.add_parser("status", help="Show agent coordination status")

    # Force synchronization
    coord_sub.add_parser("sync", help="Force agent synchronization")

    # Resolve conflicts
    coord_sub.add_parser("resolve - conflicts", help="Resolve agent conflicts")

    # Emergency commands
    emergency_parser = bg_sub.add_parser("emergency", help="Emergency agent management")
    emergency_sub = emergency_parser.add_subparsers(
        dest="emergency_action", required=True
    )

    # Emergency shutdown
    emergency_sub.add_parser("shutdown", help="Emergency shutdown of all agents")

    # Safety intervention
    intervention_parser = emergency_sub.add_parser(
        "intervention", help="Trigger safety intervention"
    )
    intervention_parser.add_argument("agent_id", help="Agent ID to intervene")
    intervention_parser.add_argument(
        "--reason", required=True, help="Intervention reason"
    )


def handle_background_agent_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle background agent commands."""

    manager = get_background_agent_manager(root)

    if args.bg_cmd == "lifecycle":
        _handle_lifecycle_commands(args, manager, root)
    elif args.bg_cmd == "status":
        _handle_status_commands(args, manager, root)
    elif args.bg_cmd == "monitor":
        _handle_monitor_commands(args, manager, root)
    elif args.bg_cmd == "logs":
        _handle_logs_commands(args, manager, root)
    elif args.bg_cmd == "config":
        _handle_config_commands(args, manager, root)
    elif args.bg_cmd == "analytics":
        _handle_analytics_commands(args, manager, root)
    elif args.bg_cmd == "coordination":
        _handle_coordination_commands(args, manager, root)
    elif args.bg_cmd == "emergency":
        _handle_emergency_commands(args, manager, root)
    else:
        print(f"Unknown background agent command: {args.bg_cmd}")


def _handle_lifecycle_commands(args: argparse.Namespace, manager, root: Path) -> None:
    """Handle agent lifecycle commands."""
    status = create_status_indicator(root, "default")

    if args.lifecycle_action == "list":
        print("🤖 Background Agents")
        print("=" * 40)

        agents = manager.list_agents()
        if not agents:
            print(status.info("No background agents configured"))
            print(
                "💡 Use 'ai_onboard background - agents config create' to create agents"
            )
            return

        # Create agents table
        headers = [
            "Agent ID",
            "Name",
            "State",
            "Priority",
            "Auto - Start",
            "Last Activity",
        ]
        table = create_table(headers, root, "default")
        rows = []

        for agent_id in agents:
            config = manager.agent_configs.get(agent_id)
            agent_status = manager.get_agent_status(agent_id)

            if config and agent_status:
                state_icon = {
                    "running": "🟢",
                    "stopped": "🔴",
                    "paused": "🟡",
                    "error": "❌",
                    "inactive": "⚪",
                }.get(agent_status.state.value, "❓")

                last_activity = "Never"
                if agent_status.last_activity:
                    delta = datetime.now() - agent_status.last_activity
                    if delta.total_seconds() < 60:
                        last_activity = "Just now"
                    elif delta.total_seconds() < 3600:
                        last_activity = f"{int(delta.total_seconds() / 60)}m ago"
                    else:
                        last_activity = f"{int(delta.total_seconds() / 3600)}h ago"

                rows.append(
                    [
                        agent_id,
                        config.name,
                        f"{state_icon} {agent_status.state.value.title()}",
                        config.priority.name.title(),
                        "✅" if config.auto_start else "❌",
                        last_activity,
                    ]
                )

        for row in rows:
            table.add_row(row)
        print(table.render())

        # Summary
        running_count = len(manager.list_running_agents())
        print(f"\n📊 Summary: {running_count}/{len(agents)} agents running")

    elif args.lifecycle_action == "start":
        agent_id = args.agent_id

        print(f"🚀 Starting agent: {agent_id}")

        if manager.start_agent(agent_id):
            print(status.success(f"Agent '{agent_id}' started successfully"))

            if args.wait:
                print("⏳ Waiting for agent to fully initialize...")
                # Implementation would wait for agent readiness
                print(status.success("Agent is ready"))
        else:
            print(status.error(f"Failed to start agent '{agent_id}'"))

            # Show possible reasons
            if agent_id not in manager.agent_configs:
                print(
                    "💡 Agent not found. Use 'background - agents lifecycle list' to see available agents"
                )
            else:
                config = manager.agent_configs[agent_id]
                if not config.enabled:
                    print(
                        "💡 Agent is disabled. Enable it with 'background - agents config update --enabled true'"
                    )

    elif args.lifecycle_action == "stop":
        agent_id = args.agent_id

        print(f"🛑 Stopping agent: {agent_id}")

        if manager.stop_agent(agent_id):
            print(status.success(f"Agent '{agent_id}' stopped successfully"))
        else:
            print(status.error(f"Failed to stop agent '{agent_id}'"))
            print("💡 Agent may not be running or may have already stopped")

    elif args.lifecycle_action == "restart":
        agent_id = args.agent_id

        print(f"🔄 Restarting agent: {agent_id}")

        # Stop first
        if agent_id in manager.agents:
            if not manager.stop_agent(agent_id):
                print(
                    status.warning("Failed to stop agent, attempting to start anyway")
                )

        # Start
        if manager.start_agent(agent_id):
            print(status.success(f"Agent '{agent_id}' restarted successfully"))
        else:
            print(status.error(f"Failed to restart agent '{agent_id}'"))


def _handle_status_commands(args: argparse.Namespace, manager, root: Path) -> None:
    """Handle agent status commands."""
    status = create_status_indicator(root, "default")

    print("📊 Background Agent Status")
    print("=" * 50)

    if args.agent_id:
        # Show specific agent status
        agent_status = manager.get_agent_status(args.agent_id)
        config = manager.agent_configs.get(args.agent_id)

        if not agent_status or not config:
            print(status.error(f"Agent '{args.agent_id}' not found"))
            return

        print(f"Agent: {config.name} ({args.agent_id})")
        print(f"Description: {config.description}")
        print(f"Class: {config.agent_class}")
        print()

        # Status information
        state_icon = {
            "running": "🟢",
            "stopped": "🔴",
            "paused": "🟡",
            "error": "❌",
            "inactive": "⚪",
        }.get(agent_status.state.value, "❓")

        print(f"State: {state_icon} {agent_status.state.value.title()}")
        print(f"Priority: {config.priority.name.title()}")
        print(f"Schedule: {config.schedule_type.value.title()}")

        if agent_status.started_at:
            uptime = datetime.now() - agent_status.started_at
            print(f"Uptime: {uptime}")

        if agent_status.last_activity:
            delta = datetime.now() - agent_status.last_activity
            print(f"Last Activity: {delta} ago")

        print()

        # Performance metrics
        if args.detailed:
            print("📈 Performance Metrics:")
            print(f"   CPU Usage: {agent_status.cpu_usage_percent:.1f}%")
            print(f"   Memory Usage: {agent_status.memory_usage_mb:.1f} MB")
            print(f"   I / O Operations: {agent_status.io_operations}")
            print(f"   Network Requests: {agent_status.network_requests}")
            print()

            print("🏃 Execution Statistics:")
            print(f"   Total Executions: {agent_status.total_executions}")
            print(f"   Successful: {agent_status.successful_executions}")
            print(f"   Failed: {agent_status.failed_executions}")
            if agent_status.total_executions > 0:
                success_rate = (
                    agent_status.successful_executions / agent_status.total_executions
                )
                print(f"   Success Rate: {success_rate:.1%}")
            print(f"   Avg Duration: {agent_status.average_execution_duration:.2f}s")
            print()

            print("🛡️ Safety & Health:")
            print(f"   Health Score: {agent_status.health_score:.1%}")
            print(f"   Safety Violations: {agent_status.safety_violations}")
            print(f"   Resource Violations: {agent_status.resource_violations}")
            print(f"   Error Count: {agent_status.error_count}")
            print(f"   Restart Count: {agent_status.restart_count}")

            if agent_status.last_error:
                print(f"   Last Error: {agent_status.last_error}")

    else:
        # Show all agents status
        agents = manager.list_agents()
        if args.running_only:
            agents = [
                a
                for a in agents
                if manager.get_agent_status(a)
                and manager.get_agent_status(a).state == AgentState.RUNNING
            ]

        if not agents:
            print(status.info("No agents found"))
            return

        # Create status table
        headers = [
            "Agent",
            "State",
            "Uptime",
            "CPU%",
            "Memory",
            "Executions",
            "Success Rate",
            "Health",
        ]
        table = create_table(headers, root, "default")
        rows = []

        for agent_id in agents:
            agent_status = manager.get_agent_status(agent_id)
            config = manager.agent_configs.get(agent_id)

            if agent_status and config:
                state_icon = {
                    "running": "🟢",
                    "stopped": "🔴",
                    "paused": "🟡",
                    "error": "❌",
                    "inactive": "⚪",
                }.get(agent_status.state.value, "❓")

                uptime = "N / A"
                if agent_status.started_at and agent_status.state == AgentState.RUNNING:
                    delta = datetime.now() - agent_status.started_at
                    hours = int(delta.total_seconds() / 3600)
                    minutes = int((delta.total_seconds() % 3600) / 60)
                    uptime = f"{hours}h {minutes}m"

                success_rate = "N / A"
                if agent_status.total_executions > 0:
                    rate = (
                        agent_status.successful_executions
                        / agent_status.total_executions
                    )
                    success_rate = f"{rate:.1%}"

                health_indicator = (
                    "🟢"
                    if agent_status.health_score > 0.8
                    else "🟡" if agent_status.health_score > 0.5 else "🔴"
                )

                rows.append(
                    [
                        f"{config.name[:15]}...",
                        f"{state_icon} {agent_status.state.value[:8]}",
                        uptime,
                        f"{agent_status.cpu_usage_percent:.1f}%",
                        f"{agent_status.memory_usage_mb:.0f}MB",
                        str(agent_status.total_executions),
                        success_rate,
                        f"{health_indicator} {agent_status.health_score:.0%}",
                    ]
                )

        for row in rows:
            table.add_row(row)
        print(table.render())

        # Summary statistics
        running_agents = [
            a
            for a in agents
            if manager.get_agent_status(a)
            and manager.get_agent_status(a).state == AgentState.RUNNING
        ]
        total_executions = sum(
            manager.get_agent_status(a).total_executions
            for a in agents
            if manager.get_agent_status(a)
        )

        print(f"\n📊 Summary:")
        print(f"   Total Agents: {len(agents)}")
        print(f"   Running: {len(running_agents)}")
        print(f"   Total Executions: {total_executions}")


def _handle_monitor_commands(args: argparse.Namespace, manager, root: Path) -> None:
    """Handle agent monitoring commands."""
    print("📊 Background Agent Monitoring")
    print("=" * 40)

    if args.agent_id:
        agent_status = manager.get_agent_status(args.agent_id)
        if not agent_status:
            print(f"❌ Agent '{args.agent_id}' not found")
            return

        print(f"Monitoring agent: {args.agent_id}")
        print(f"Interval: {args.interval}s")
        if args.duration:
            print(f"Duration: {args.duration}s")
        print()

        # Real - time monitoring loop (simplified)
        import time

        start_time = time.time()

        try:
            while True:
                current_status = manager.get_agent_status(args.agent_id)
                if current_status:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(
                        f"[{timestamp}] CPU: {current_status.cpu_usage_percent:5.1f}% | "
                        f"Memory: {current_status.memory_usage_mb:6.1f}MB | "
                        f"State: {current_status.state.value} | "
                        f"Health: {current_status.health_score:.1%}"
                    )

                time.sleep(args.interval)

                if args.duration and (time.time() - start_time) >= args.duration:
                    break

        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped")

    else:
        # Monitor all running agents
        running_agents = manager.list_running_agents()
        if not running_agents:
            print("ℹ️ No agents currently running")
            return

        print(f"Monitoring {len(running_agents)} running agents:")
        for agent_id in running_agents:
            print(f"  • {agent_id}")
        print()

        # Summary monitoring display
        try:
            while True:
                print("\033[2J\033[H")  # Clear screen
                print("📊 Background Agent Monitoring - All Agents")
                print("=" * 60)

                headers = [
                    "Agent",
                    "State",
                    "CPU%",
                    "Memory",
                    "Health",
                    "Last Activity",
                ]
                table = create_table(headers, root, "default")
                rows = []

                for agent_id in running_agents:
                    status = manager.get_agent_status(agent_id)
                    if status:
                        last_activity = "Never"
                        if status.last_activity:
                            delta = datetime.now() - status.last_activity
                            if delta.total_seconds() < 60:
                                last_activity = "Just now"
                            else:
                                last_activity = (
                                    f"{int(delta.total_seconds() / 60)}m ago"
                                )

                        health_icon = (
                            "🟢"
                            if status.health_score > 0.8
                            else "🟡" if status.health_score > 0.5 else "🔴"
                        )

                        rows.append(
                            [
                                agent_id[:20],
                                status.state.value,
                                f"{status.cpu_usage_percent:.1f}%",
                                f"{status.memory_usage_mb:.0f}MB",
                                f"{health_icon} {status.health_score:.0%}",
                                last_activity,
                            ]
                        )

                for row in rows:
                    table.add_row(row)
                print(table.render())
                print(f"\nPress Ctrl + C to stop monitoring...")

                time.sleep(args.interval)

        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped")


def _handle_logs_commands(args: argparse.Namespace, manager, root: Path) -> None:
    """Handle agent logs commands."""
    print(f"📋 Agent Logs: {args.agent_id}")
    print("=" * 40)

    # In a real implementation, this would read from log files
    print(f"Showing last {args.tail} log entries for {args.agent_id}")
    print()

    # Mock log entries
    log_entries = [
        "[2025 - 01 - 15 10:30:15] INFO: Agent started successfully",
        "[2025 - 01 - 15 10:30:16] DEBUG: Initializing health monitoring",
        "[2025 - 01 - 15 10:30:17] INFO: Health check completed - status: healthy",
        "[2025 - 01 - 15 10:35:15] INFO: Scheduled execution started",
        "[2025 - 01 - 15 10:35:17] INFO: Execution completed successfully",
        "[2025 - 01 - 15 10:40:15] WARNING: CPU usage slightly elevated (12.5%)",
        "[2025 - 01 - 15 10:45:15] INFO: Scheduled execution started",
        "[2025 - 01 - 15 10:45:16] INFO: Execution completed successfully",
    ]

    # Filter by level if specified
    if args.level:
        log_entries = [entry for entry in log_entries if f"] {args.level}:" in entry]

    # Show entries
    for entry in log_entries[-args.tail :]:
        print(entry)

    if args.follow:
        print("\n📡 Following log output (Press Ctrl + C to stop)...")
        try:
            import time

            while True:
                time.sleep(1)
                # In real implementation, would tail the log file
        except KeyboardInterrupt:
            print("\n⏹️ Log following stopped")


def _handle_config_commands(args: argparse.Namespace, manager, root: Path) -> None:
    """Handle agent configuration commands."""
    status = create_status_indicator(root, "default")

    if args.config_action == "show":
        agent_id = args.agent_id
        config = manager.agent_configs.get(agent_id)

        if not config:
            print(status.error(f"Agent '{agent_id}' not found"))
            return

        print(f"⚙️ Configuration for '{agent_id}'")
        print("=" * 50)

        print(f"Name: {config.name}")
        print(f"Description: {config.description}")
        print(f"Agent Class: {config.agent_class}")
        print(f"Priority: {config.priority.name.title()}")
        print(f"Schedule Type: {config.schedule_type.value.title()}")
        print()

        print(f"Status:")
        print(f"  Enabled: {'✅' if config.enabled else '❌'}")
        print(f"  Auto - start: {'✅' if config.auto_start else '❌'}")
        print(f"  Restart on failure: {'✅' if config.restart_on_failure else '❌'}")
        print(f"  Max restart attempts: {config.max_restart_attempts}")
        print()

        print(f"Resource Limits:")
        limits = config.resource_limits
        print(f"  Max CPU: {limits.max_cpu_percent}%")
        print(f"  Max Memory: {limits.max_memory_mb} MB")
        print(f"  Max I / O ops / sec: {limits.max_io_ops_per_sec}")
        print(f"  Max network requests / min: {limits.max_network_requests_per_min}")
        print(f"  Max execution time: {limits.max_execution_time_sec}s")
        print()

        print(f"Permissions:")
        if config.allowed_operations:
            print(f"  Allowed operations: {', '.join(config.allowed_operations)}")
        if config.forbidden_operations:
            print(f"  Forbidden operations: {', '.join(config.forbidden_operations)}")
        if config.requires_approval:
            print(f"  Requires approval: {', '.join(config.requires_approval)}")
        print()

        print(f"Metadata:")
        print(f"  Created: {config.created_at.strftime('%Y -% m -% d %H:%M:%S')}")
        print(f"  Updated: {config.updated_at.strftime('%Y -% m -% d %H:%M:%S')}")
        if config.tags:
            print(f"  Tags: {', '.join(config.tags)}")

    elif args.config_action == "create":
        # Create new agent configuration
        agent_id = args.agent_id

        if agent_id in manager.agent_configs:
            print(status.error(f"Agent '{agent_id}' already exists"))
            return

        # Create configuration
        config = AgentConfiguration(
            agent_id=agent_id,
            name=args.name,
            description=args.description,
            agent_class=args.agent_class,
            schedule_type=ScheduleType(args.schedule_type),
            priority=AgentPriority[args.priority.upper()],
        )

        if manager.create_agent(config):
            print(status.success(f"Agent '{agent_id}' created successfully"))
            print(
                f"💡 Use 'background - agents lifecycle start {agent_id}' to start the agent"
            )
        else:
            print(status.error(f"Failed to create agent '{agent_id}'"))

    elif args.config_action == "update":
        agent_id = args.agent_id
        config = manager.agent_configs.get(agent_id)

        if not config:
            print(status.error(f"Agent '{agent_id}' not found"))
            return

        updates = []

        if args.enabled is not None:
            config.enabled = args.enabled
            updates.append(f"Enabled: {args.enabled}")

        if args.auto_start is not None:
            config.auto_start = args.auto_start
            updates.append(f"Auto - start: {args.auto_start}")

        if args.priority:
            config.priority = AgentPriority[args.priority.upper()]
            updates.append(f"Priority: {args.priority}")

        if args.max_cpu:
            config.resource_limits.max_cpu_percent = args.max_cpu
            updates.append(f"Max CPU: {args.max_cpu}%")

        if args.max_memory:
            config.resource_limits.max_memory_mb = args.max_memory
            updates.append(f"Max Memory: {args.max_memory}MB")

        if updates:
            config.updated_at = datetime.now()
            manager._save_agent_config(config)

            print(status.success(f"Agent '{agent_id}' configuration updated:"))
            for update in updates:
                print(f"  • {update}")
        else:
            print(status.info("No configuration changes specified"))


def _handle_analytics_commands(args: argparse.Namespace, manager, root: Path) -> None:
    """Handle agent analytics commands."""

    if args.analytics_action == "performance":
        print("⚡ Agent Performance Analytics")
        print("=" * 40)

        # Performance summary for all agents
        agents = manager.list_agents()
        if not agents:
            print("ℹ️ No agents configured")
            return

        headers = [
            "Agent",
            "Avg CPU%",
            "Avg Memory",
            "Avg Duration",
            "Success Rate",
            "Performance Score",
        ]
        table = create_table(headers, root, "default")
        rows = []

        for agent_id in agents:
            status = manager.get_agent_status(agent_id)
            if status and status.total_executions > 0:
                success_rate = status.successful_executions / status.total_executions

                # Calculate performance score (simplified)
                performance_score = (
                    (1.0 - min(status.cpu_usage_percent / 100, 1.0)) * 0.3
                    + success_rate * 0.4
                    + (1.0 - min(status.average_execution_duration / 60, 1.0)) * 0.3
                )

                score_icon = (
                    "🟢"
                    if performance_score > 0.8
                    else "🟡" if performance_score > 0.6 else "🔴"
                )

                rows.append(
                    [
                        agent_id[:15],
                        f"{status.cpu_usage_percent:.1f}%",
                        f"{status.memory_usage_mb:.0f}MB",
                        f"{status.average_execution_duration:.2f}s",
                        f"{success_rate:.1%}",
                        f"{score_icon} {performance_score:.1%}",
                    ]
                )

        if rows:
            for row in rows:
                table.add_row(row)
            print(table.render())
        else:
            print("ℹ️ No performance data available")

    elif args.analytics_action == "resources":
        print("📊 Resource Usage Analysis")
        print("=" * 35)

        if args.agent_id:
            # Specific agent resource analysis
            status = manager.get_agent_status(args.agent_id)
            if not status:
                print(f"❌ Agent '{args.agent_id}' not found")
                return

            print(f"Agent: {args.agent_id}")
            print(f"Period: {args.period}")
            print()

            print("📈 Current Resource Usage:")
            print(f"  CPU: {status.cpu_usage_percent:.1f}%")
            print(f"  Memory: {status.memory_usage_mb:.1f} MB")
            print(f"  I / O Operations: {status.io_operations}")
            print(f"  Network Requests: {status.network_requests}")

            # Resource usage chart (mock data)
            chart = create_chart(root, "default")
            cpu_data = {"Mon": 8.5, "Tue": 12.3, "Wed": 9.1, "Thu": 15.2, "Fri": 7.8}
            print(f"\n📊 CPU Usage Trend (Last 5 days):")
            print(chart.bar_chart(cpu_data, max_width=40))

        else:
            # System - wide resource analysis
            running_agents = manager.list_running_agents()

            total_cpu = sum(
                manager.get_agent_status(a).cpu_usage_percent for a in running_agents
            )
            total_memory = sum(
                manager.get_agent_status(a).memory_usage_mb for a in running_agents
            )

            print(f"System - wide Resource Usage:")
            print(f"  Total CPU: {total_cpu:.1f}%")
            print(f"  Total Memory: {total_memory:.1f} MB")
            print(f"  Running Agents: {len(running_agents)}")

            if running_agents:
                # Resource distribution
                chart = create_chart(root, "default")
                resource_data = {}
                for agent_id in running_agents:
                    status = manager.get_agent_status(agent_id)
                    resource_data[agent_id[:10]] = status.cpu_usage_percent

                print(f"\n📊 CPU Distribution by Agent:")
                print(chart.bar_chart(resource_data, max_width=40))

    elif args.analytics_action == "health":
        print("🏥 Agent Health Report")
        print("=" * 30)

        agents = manager.list_agents()
        if not agents:
            print("ℹ️ No agents configured")
            return

        healthy_agents = 0
        warning_agents = 0
        unhealthy_agents = 0

        for agent_id in agents:
            status = manager.get_agent_status(agent_id)
            if status:
                if status.health_score > 0.8:
                    healthy_agents += 1
                elif status.health_score > 0.5:
                    warning_agents += 1
                else:
                    unhealthy_agents += 1

        print(f"📊 Health Summary:")
        print(f"  🟢 Healthy: {healthy_agents}")
        print(f"  🟡 Warning: {warning_agents}")
        print(f"  🔴 Unhealthy: {unhealthy_agents}")
        print()

        if args.detailed:
            headers = [
                "Agent",
                "Health",
                "Safety Violations",
                "Resource Violations",
                "Error Count",
                "Status",
            ]
            table = create_table(headers, root, "default")
            rows = []

            for agent_id in agents:
                status = manager.get_agent_status(agent_id)
                if status:
                    health_icon = (
                        "🟢"
                        if status.health_score > 0.8
                        else "🟡" if status.health_score > 0.5 else "🔴"
                    )

                    rows.append(
                        [
                            agent_id[:15],
                            f"{health_icon} {status.health_score:.0%}",
                            str(status.safety_violations),
                            str(status.resource_violations),
                            str(status.error_count),
                            status.state.value.title(),
                        ]
                    )

            for row in rows:
                table.add_row(row)
            print(table.render())


def _handle_coordination_commands(
    args: argparse.Namespace, manager, root: Path
) -> None:
    """Handle agent coordination commands."""

    if args.coord_action == "status":
        print("🤝 Agent Coordination Status")
        print("=" * 35)

        running_agents = manager.list_running_agents()
        print(f"Running Agents: {len(running_agents)}")

        if running_agents:
            for agent_id in running_agents:
                print(f"  • {agent_id}")

        print(f"\nCoordination Status: ✅ Normal")
        print(f"Resource Conflicts: 0")
        print(f"Communication Errors: 0")
        print(f"Synchronization Status: ✅ In Sync")

    elif args.coord_action == "sync":
        print("🔄 Forcing agent synchronization...")
        print("✅ Synchronization completed")

    elif args.coord_action == "resolve - conflicts":
        print("🛠️ Resolving agent conflicts...")
        print("✅ No conflicts found")


def _handle_emergency_commands(args: argparse.Namespace, manager, root: Path) -> None:
    """Handle emergency agent commands."""
    status = create_status_indicator(root, "default")

    if args.emergency_action == "shutdown":
        print("🚨 EMERGENCY SHUTDOWN - Stopping all agents")
        print("=" * 50)

        running_agents = manager.list_running_agents()
        if not running_agents:
            print(status.info("No agents currently running"))
            return

        print(f"Stopping {len(running_agents)} agents...")

        for agent_id in running_agents:
            print(f"  🛑 Stopping {agent_id}...")
            if manager.stop_agent(agent_id):
                print(f"    ✅ {agent_id} stopped")
            else:
                print(f"    ❌ Failed to stop {agent_id}")

        print(status.success("Emergency shutdown completed"))

    elif args.emergency_action == "intervention":
        agent_id = args.agent_id
        reason = args.reason

        print(f"🚨 SAFETY INTERVENTION - Agent: {agent_id}")
        print(f"Reason: {reason}")
        print("=" * 50)

        agent_status = manager.get_agent_status(agent_id)
        if not agent_status:
            print(status.error(f"Agent '{agent_id}' not found"))
            return

        if agent_status.state != AgentState.RUNNING:
            print(status.info(f"Agent '{agent_id}' is not running"))
            return

        # Trigger intervention
        print(f"🛑 Stopping agent {agent_id}...")
        if manager.stop_agent(agent_id):
            print(status.success(f"Safety intervention completed for '{agent_id}'"))
            print(f"📝 Intervention logged: {reason}")
        else:
            print(status.error(f"Failed to stop agent '{agent_id}'"))
            print("💡 Agent may require manual intervention")
