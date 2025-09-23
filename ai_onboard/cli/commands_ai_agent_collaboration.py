"""
AI Agent Collaboration CLI Commands.

This module provides CLI commands for managing AI agent collaboration,
including agent registration, session management, and guidance.
"""

# Direct import will be added below

import argparse
from pathlib import Path

from ..core.ai_agent_collaboration_protocol import (
    AgentCapability,
    AgentProfile,
    CollaborationMode,
    SafetyLevel,
    get_collaboration_protocol,
)
from ..core.ai_agent_guidance import (
    GuidanceLevel,
    GuidanceType,
    get_ai_agent_guidance_system,
)


def handle_ai_agent_collaboration_commands(
    args: argparse.Namespace, root: Path
) -> None:
    """Handle AI agent collaboration commands."""
    if args.collaboration_cmd == "register":
        _handle_register_agent(args, root)
    elif args.collaboration_cmd == "session":
        _handle_session_management(args, root)
    elif args.collaboration_cmd == "guidance":
        _handle_guidance_commands(args, root)
    elif args.collaboration_cmd == "status":
        _handle_collaboration_status(args, root)
    elif args.collaboration_cmd == "test":
        _handle_test_collaboration(args, root)
    else:
        print(f"Unknown collaboration command: {args.collaboration_cmd}")


def _handle_register_agent(args: argparse.Namespace, root: Path) -> None:
    """Handle agent registration."""
    protocol = get_collaboration_protocol(root)

    # Parse capabilities
    capabilities = []
    if args.capabilities:
        for cap_str in args.capabilities:
            try:
                capabilities.append(AgentCapability(cap_str))
            except ValueError:
                print(f"Invalid capability: {cap_str}")
                print(
                    f"Available capabilities: {', '.join([cap.value for cap in AgentCapability])}"
                )
                return

    # Parse collaboration mode
    try:
        collaboration_mode = CollaborationMode(args.collaboration_mode)
    except ValueError:
        print(f"Invalid collaboration mode: {args.collaboration_mode}")
        print(
            f"Available modes: {', '.join([mode.value for mode in CollaborationMode])}"
        )
        return

    # Parse safety level
    try:
        safety_level = SafetyLevel(args.safety_level)
    except ValueError:
        print(f"Invalid safety level: {args.safety_level}")
        print(f"Available levels: {', '.join([level.value for level in SafetyLevel])}")
        return

    # Create agent profile
    agent_profile = AgentProfile(
        agent_id=args.agent_id,
        name=args.name,
        version=args.version or "1.0.0",
        capabilities=capabilities,
        collaboration_mode=collaboration_mode,
        safety_level=safety_level,
        max_autonomous_actions=args.max_actions or 10,
        requires_confirmation_for=args.require_confirmation or [],
        allowed_commands=args.allowed_commands or [],
        blocked_commands=args.blocked_commands or [],
        session_timeout=args.session_timeout or 3600,
    )

    # Register agent
    result = protocol.register_agent(agent_profile)

    if result["status"] == "success":
        print("🤖 Agent Registered Successfully!")
        print(f"Agent ID: {result['agent_id']}")
        print(f"Name: {args.name}")
        print(f"Capabilities: {', '.join([cap.value for cap in capabilities])}")
        print(f"Collaboration Mode: {collaboration_mode.value}")
        print(f"Safety Level: {safety_level.value}")
        print(f"Max Autonomous Actions: {args.max_actions or 10}")
        print(f"Session Timeout: {args.session_timeout or 3600} seconds")
    else:
        print(f"❌ Registration failed: {result['message']}")
        if "errors" in result:
            for error in result["errors"]:
                print(f"  - {error}")


def _handle_session_management(args: argparse.Namespace, root: Path) -> None:
    """Handle session management commands."""
    protocol = get_collaboration_protocol(root)

    if args.session_action == "start":
        _handle_start_session(args, protocol)
    elif args.session_action == "status":
        _handle_session_status(args, protocol)
    elif args.session_action == "end":
        _handle_end_session(args, protocol)
    elif args.session_action == "list":
        _handle_list_sessions(args, protocol)
    else:
        print(f"Unknown session action: {args.session_action}")


def _handle_start_session(args: argparse.Namespace, protocol) -> None:
    """Handle starting a collaboration session."""
    result = protocol.start_collaboration_session(args.agent_id)

    if result["status"] == "success":
        print("🚀 Collaboration Session Started!")
        print(f"Session ID: {result['session_id']}")
        print(f"Agent: {result['agent_profile']['name']}")
        print(f"Capabilities: {', '.join(result['agent_profile']['capabilities'])}")
        print(f"Collaboration Mode: {result['agent_profile']['collaboration_mode']}")
        print(f"Safety Level: {result['agent_profile']['safety_level']}")
        print()
        print("Session Context:")
        context = result.get("context", {})
        for key, value in context.items():
            print(f"  {key}: {value}")
    else:
        print(f"❌ Failed to start session: {result['message']}")


def _handle_session_status(args: argparse.Namespace, protocol) -> None:
    """Handle getting session status."""
    result = protocol.get_session_status(args.session_id)

    if result["status"] == "success":
        print("📊 Session Status")
        print("=" * 30)
        print(f"Session ID: {result['session_id']}")
        print(f"Agent: {result['agent_profile']['name']}")
        print(f"Status: {result['session_info']['status']}")
        print(f"Started: {result['session_info']['started_at']}")
        print(f"Last Activity: {result['session_info']['last_activity']}")
        print(f"Actions Taken: {result['session_info']['actions_taken']}")
        print(f"Safety Violations: {result['session_info']['safety_violations']}")
        print(f"User Interactions: {result['session_info']['user_interactions']}")

        if result.get("recent_actions"):
            print("\nRecent Actions:")
            for action in result["recent_actions"]:
                print(
                    f"  - {action['timestamp']}: {action['action'].get('type', 'unknown')}"
                )

        if result.get("recent_violations"):
            print("\nRecent Safety Violations:")
            for violation in result["recent_violations"]:
                print(f"  - {violation['timestamp']}: {violation['violation']}")
    else:
        print(f"❌ Failed to get session status: {result['message']}")


def _handle_end_session(args: argparse.Namespace, protocol) -> None:
    """Handle ending a collaboration session."""
    reason = args.reason or "completed"
    result = protocol.end_collaboration_session(args.session_id, reason)

    if result["status"] == "success":
        print("🏁 Session Ended Successfully!")
        print(f"Session ID: {args.session_id}")
        print(f"Reason: {reason}")

        summary = result.get("summary", {})
        if summary:
            print("\nSession Summary:")
            print(f"  Duration: {summary.get('duration', 0):.1f} seconds")
            print(f"  Actions Taken: {summary.get('actions_taken', 0)}")
            print(f"  Safety Violations: {summary.get('safety_violations', 0)}")
            print(f"  User Interactions: {summary.get('user_interactions', 0)}")
    else:
        print(f"❌ Failed to end session: {result['message']}")


def _handle_list_sessions(args: argparse.Namespace, protocol) -> None:
    """Handle listing active sessions."""
    # This would need to be implemented in the protocol
    print("📋 Active Sessions")
    print("=" * 20)
    print("Session listing not yet implemented in the protocol.")


def _handle_guidance_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle guidance commands."""
    guidance_system = get_ai_agent_guidance_system(root)

    if args.guidance_action == "get":
        _handle_get_guidance(args, guidance_system)
    elif args.guidance_action == "show":
        _handle_show_guidance(args, guidance_system)
    elif args.guidance_action == "complete":
        _handle_complete_guidance(args, guidance_system)
    elif args.guidance_action == "progress":
        _handle_guidance_progress(args, guidance_system)
    elif args.guidance_action == "contextual":
        _handle_contextual_guidance(args, guidance_system)
    else:
        print(f"Unknown guidance action: {args.guidance_action}")


def _handle_get_guidance(args: argparse.Namespace, guidance_system) -> None:
    """Handle getting guidance for an agent."""
    guidance_type = None
    if hasattr(args, "type") and args.type:
        try:
            guidance_type = GuidanceType(args.type)
        except ValueError:
            print(f"Invalid guidance type: {args.type}")
            print(f"Available types: {', '.join([gt.value for gt in GuidanceType])}")
            return

    level = None
    if hasattr(args, "level") and args.level:
        try:
            level = GuidanceLevel(args.level)
        except ValueError:
            print(f"Invalid guidance level: {args.level}")
            print(f"Available levels: {', '.join([gl.value for gl in GuidanceLevel])}")
            return

    result = guidance_system.get_guidance_for_agent(args.agent_id, guidance_type, level)

    if result["status"] == "success":
        print(f"📚 Guidance for Agent: {args.agent_id}")
        print(f"Experience Level: {result['experience_level']}")
        print(f"Total Available: {result['total_available']}")
        print()

        for item in result["guidance_items"]:
            print(f"📖 {item['title']}")
            print(f"   Type: {item['type']}")
            print(f"   Level: {item['level']}")
            print(f"   Tags: {', '.join(item['tags'])}")
            print(f"   ID: {item['id']}")
            print()
    else:
        print(f"❌ Failed to get guidance: {result['message']}")


def _handle_show_guidance(args: argparse.Namespace, guidance_system) -> None:
    """Handle showing specific guidance."""
    result = guidance_system.get_specific_guidance(args.guidance_id, args.agent_id)

    if result["status"] == "success":
        item = result["guidance_item"]
        print(f"📖 {item['title']}")
        print("=" * len(item["title"]))
        print(f"Type: {item['type']}")
        print(f"Level: {item['level']}")
        print(f"Tags: {', '.join(item['tags'])}")
        print()
        print(item["content"])

        if item.get("examples"):
            print("\nExamples:")
            for example in item["examples"]:
                print(f"  - {example}")

        if item.get("prerequisites"):
            print("\nPrerequisites:")
            for prereq in item["prerequisites"]:
                print(f"  - {prereq}")

        if item.get("related_items"):
            print("\nRelated Items:")
            for related in item["related_items"]:
                print(f"  - {related}")
    else:
        print(f"❌ Failed to show guidance: {result['message']}")


def _handle_complete_guidance(args: argparse.Namespace, guidance_system) -> None:
    """Handle marking guidance as completed."""
    result = guidance_system.mark_guidance_completed(args.agent_id, args.guidance_id)

    if result["status"] == "success":
        print("✅ Guidance Marked as Completed!")
        print(f"Agent: {args.agent_id}")
        print(f"Guidance: {args.guidance_id}")
        print(f"Total Completed: {result['completed_count']}")
    else:
        print(f"❌ Failed to mark guidance as completed: {result['message']}")


def _handle_guidance_progress(args: argparse.Namespace, guidance_system) -> None:
    """Handle getting guidance progress."""
    result = guidance_system.get_agent_progress(args.agent_id)

    if result["status"] == "success":
        print(f"📊 Guidance Progress for Agent: {args.agent_id}")
        print("=" * 40)
        print(f"Experience Level: {result['experience_level']}")

        progress = result["progress"]
        print(f"Total Guidance Items: {progress['total_guidance_items']}")
        print(f"Completed Items: {progress['completed_items']}")
        print(f"Completion Rate: {progress['completion_rate']:.1f}%")

        if progress.get("guidance_by_type"):
            print("\nCompleted by Type:")
            for guidance_type, count in progress["guidance_by_type"].items():
                print(f"  {guidance_type}: {count}")

        if result.get("recent_activity"):
            print("\nRecent Activity:")
            for activity in result["recent_activity"]:
                print(f"  {activity['accessed_at']}: {activity['title']}")
    else:
        print(f"❌ Failed to get progress: {result['message']}")


def _handle_contextual_guidance(args: argparse.Namespace, guidance_system) -> None:
    """Handle getting contextual guidance."""
    # This would need context from the current session
    context = {"safety_violations": 0, "vision_confirmed": False, "actions_taken": 0}

    result = guidance_system.generate_contextual_guidance(args.agent_id, context)

    if result["status"] == "success":
        print(f"🎯 Contextual Guidance for Agent: {args.agent_id}")
        print("=" * 45)

        analysis = result["context_analysis"]
        print("Context Analysis:")
        print(f"  Safety Violations: {analysis['safety_violations']}")
        print(f"  Vision Confirmed: {analysis['vision_confirmed']}")
        print(f"  Actions Taken: {analysis['actions_taken']}")
        print()

        for item in result["contextual_guidance"]:
            print(f"📖 {item['title']}")
            print(f"   Type: {item['type']}")
            print(f"   Level: {item['level']}")
            print(f"   ID: {item['id']}")
            print()
    else:
        print(f"❌ Failed to get contextual guidance: {result['message']}")


def _handle_collaboration_status(args: argparse.Namespace, root: Path) -> None:
    """Handle getting overall collaboration status."""
    get_collaboration_protocol(root)

    print("🤖 AI Agent Collaboration Status")
    print("=" * 35)

    # This would need to be implemented in the protocol
    print("Overall collaboration status not yet implemented in the protocol.")


def _handle_test_collaboration(args: argparse.Namespace, root: Path) -> None:
    """Handle testing collaboration functionality."""
    print("🧪 Testing AI Agent Collaboration")
    print("=" * 35)

    # Test agent registration
    print("1. Testing agent registration...")
    protocol = get_collaboration_protocol(root)

    test_agent = AgentProfile(
        agent_id="test_agent_001",
        name="Test AI Agent",
        version="1.0.0",
        capabilities=[AgentCapability.CODE_GENERATION, AgentCapability.PLANNING],
        collaboration_mode=CollaborationMode.COLLABORATIVE,
        safety_level=SafetyLevel.MEDIUM,
    )

    result = protocol.register_agent(test_agent)
    if result["status"] == "success":
        print("   ✅ Agent registration successful")
    else:
        print(f"   ❌ Agent registration failed: {result['message']}")
        return

    # Test session start
    print("2. Testing session start...")
    session_result = protocol.start_collaboration_session(test_agent.agent_id)
    if session_result["status"] == "success":
        print("   ✅ Session start successful")
        session_id = session_result["session_id"]
    else:
        print(f"   ❌ Session start failed: {session_result['message']}")
        return

    # Test action execution
    print("3. Testing action execution...")
    action = {"type": "vision_interrogation", "subtype": "get_status"}
    action_result = protocol.execute_agent_action(session_id, action)
    if action_result["status"] == "success":
        print("   ✅ Action execution successful")
    else:
        print(f"   ❌ Action execution failed: {action_result['message']}")

    # Test session end
    print("4. Testing session end...")
    end_result = protocol.end_collaboration_session(session_id, "test_completed")
    if end_result["status"] == "success":
        print("   ✅ Session end successful")
    else:
        print(f"   ❌ Session end failed: {end_result['message']}")

    print("\n🎉 Collaboration testing completed!")


def add_ai_agent_collaboration_parser(subparsers) -> None:
    """Add AI agent collaboration commands to the argument parser."""
    collaboration_parser = subparsers.add_parser(
        "ai - collaboration", help="AI agent collaboration management"
    )

    collaboration_subparsers = collaboration_parser.add_subparsers(
        dest="collaboration_cmd", help="Collaboration commands"
    )

    # Register command
    register_parser = collaboration_subparsers.add_parser(
        "register", help="Register an AI agent"
    )
    register_parser.add_argument("agent_id", help="Unique agent identifier")
    register_parser.add_argument("name", help="Agent name")
    register_parser.add_argument("--version", help="Agent version")
    register_parser.add_argument(
        "--capabilities",
        nargs="+",
        choices=[cap.value for cap in AgentCapability],
        help="Agent capabilities",
    )
    register_parser.add_argument(
        "--collaboration - mode",
        choices=[mode.value for mode in CollaborationMode],
        default="collaborative",
        help="Collaboration mode",
    )
    register_parser.add_argument(
        "--safety - level",
        choices=[level.value for level in SafetyLevel],
        default="medium",
        help="Safety level",
    )
    register_parser.add_argument(
        "--max - actions", type=int, help="Maximum autonomous actions"
    )
    register_parser.add_argument(
        "--require - confirmation", nargs="+", help="Actions requiring confirmation"
    )
    register_parser.add_argument(
        "--allowed - commands", nargs="+", help="Allowed commands"
    )
    register_parser.add_argument(
        "--blocked - commands", nargs="+", help="Blocked commands"
    )
    register_parser.add_argument(
        "--session - timeout", type=int, help="Session timeout in seconds"
    )

    # Session management
    session_parser = collaboration_subparsers.add_parser(
        "session", help="Manage collaboration sessions"
    )
    session_subparsers = session_parser.add_subparsers(
        dest="session_action", help="Session actions"
    )

    start_parser = session_subparsers.add_parser(
        "start", help="Start a collaboration session"
    )
    start_parser.add_argument("agent_id", help="Agent ID")

    status_parser = session_subparsers.add_parser("status", help="Get session status")
    status_parser.add_argument("session_id", help="Session ID")

    end_parser = session_subparsers.add_parser(
        "end", help="End a collaboration session"
    )
    end_parser.add_argument("session_id", help="Session ID")
    end_parser.add_argument("--reason", help="End reason")

    session_subparsers.add_parser("list", help="List active sessions")

    # Guidance commands
    guidance_parser = collaboration_subparsers.add_parser(
        "guidance", help="Manage AI agent guidance"
    )
    guidance_subparsers = guidance_parser.add_subparsers(
        dest="guidance_action", help="Guidance actions"
    )

    get_parser = guidance_subparsers.add_parser("get", help="Get guidance for an agent")
    get_parser.add_argument("agent_id", help="Agent ID")
    get_parser.add_argument(
        "--type", choices=[gt.value for gt in GuidanceType], help="Guidance type filter"
    )
    get_parser.add_argument(
        "--level",
        choices=[gl.value for gl in GuidanceLevel],
        help="Guidance level filter",
    )

    show_parser = guidance_subparsers.add_parser("show", help="Show specific guidance")
    show_parser.add_argument("guidance_id", help="Guidance ID")
    show_parser.add_argument("agent_id", help="Agent ID")

    complete_parser = guidance_subparsers.add_parser(
        "complete", help="Mark guidance as completed"
    )
    complete_parser.add_argument("agent_id", help="Agent ID")
    complete_parser.add_argument("guidance_id", help="Guidance ID")

    progress_parser = guidance_subparsers.add_parser(
        "progress", help="Get agent guidance progress"
    )
    progress_parser.add_argument("agent_id", help="Agent ID")

    contextual_parser = guidance_subparsers.add_parser(
        "contextual", help="Get contextual guidance"
    )
    contextual_parser.add_argument("agent_id", help="Agent ID")

    # Status command
    collaboration_subparsers.add_parser(
        "status", help="Get overall collaboration status"
    )

    # Test command
    collaboration_subparsers.add_parser("test", help="Test collaboration functionality")
