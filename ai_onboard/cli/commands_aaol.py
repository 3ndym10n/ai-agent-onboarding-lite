"""CLI commands for AI Agent Orchestration Layer (AAOL)."""

import json
import time
from pathlib import Path

from ..core.ai_agent_orchestration import create_ai_agent_orchestrator


def add_aaol_commands(subparsers):
    """Add AAOL command parsers."""

    # AAOL main command
    s_aaol = subparsers.add_parser(
        "aaol", help="AI Agent Orchestration Layer - Revolutionary collaborative system"
    )
    aaol_sub = s_aaol.add_subparsers(dest="aaol_cmd", required=True)

    # Create session
    s_create = aaol_sub.add_parser(
        "create-session", help="Create new AI agent conversation session"
    )
    s_create.add_argument("--user-id", default="default", help="User identifier")

    # Process conversation
    s_converse = aaol_sub.add_parser(
        "converse", help="Process conversation through decision pipeline"
    )
    s_converse.add_argument("--session-id", required=True, help="Session identifier")
    s_converse.add_argument("--message", required=True, help="User message/input")

    # Execute plan
    s_execute = aaol_sub.add_parser(
        "execute", help="Execute planned commands for session"
    )
    s_execute.add_argument("--session-id", required=True, help="Session identifier")

    # Session status
    s_status = aaol_sub.add_parser("status", help="Get session status and details")
    s_status.add_argument("--session-id", required=True, help="Session identifier")

    # List sessions
    s_list = aaol_sub.add_parser("list-sessions", help="List all available sessions")
    s_list.add_argument("--user-id", help="Filter sessions by user ID")

    # Delete session
    s_delete = aaol_sub.add_parser("delete-session", help="Delete a session")
    s_delete.add_argument("--session-id", required=True, help="Session identifier")

    # Cleanup expired sessions
    s_cleanup = aaol_sub.add_parser("cleanup", help="Clean up expired sessions")

    # Demo conversation
    s_demo = aaol_sub.add_parser("demo", help="Run interactive demo of AAOL system")


def handle_aaol_commands(args, root: Path):
    """Handle AAOL command execution."""

    orchestrator = create_ai_agent_orchestrator(root)

    # Windows-safe output: replace emojis with ASCII fallbacks
    def _ascii_safe(text: str) -> str:
        mapping = {
            "🤖": "[AI]",
            "📊": "[INFO]",
            "🚀": "[RUN]",
            "💬": "[CHAT]",
            "✅": "[OK]",
            "🤔": "[CONFIRM]",
            "❓": "[CLARIFY]",
            "❌": "[FAIL]",
            "🔄": "[ROLLBACK]",
            "⚠️": "[WARN]",
            "📝": "[NOTE]",
            "🎯": "[DONE]",
        }
        out = text or ""
        for k, v in mapping.items():
            out = out.replace(k, v)
        return out

    if args.aaol_cmd == "create-session":
        # Create new session
        session_id = orchestrator.create_session(args.user_id)

        result = {
            "action": "session_created",
            "session_id": session_id,
            "user_id": args.user_id,
            "message": "New AI agent conversation session created",
        }

        print(json.dumps(result, indent=2))
        return True

    elif args.aaol_cmd == "converse":
        # Process conversation
        result = orchestrator.process_conversation(args.session_id, args.message)

        print(_ascii_safe("🤖 AI Agent Orchestration Layer Response:"))
        print(_ascii_safe("=" * 60))

        # Show AI agent response
        if result.get("ai_agent_response"):
            print("[AI] " + _ascii_safe(str(result["ai_agent_response"])))

        # Show pipeline details
        if result.get("pipeline_stages"):
            print(_ascii_safe("\n📊 Decision Pipeline Results:"))
            for stage, details in result["pipeline_stages"].items():
                print(_ascii_safe(f"   {stage}: {details}"))

        # Show execution readiness
        if result.get("ready_to_execute"):
            print(_ascii_safe("\n🚀 Ready to Execute!"))
            print(
                _ascii_safe(
                    f"   Commands: {result.get('execution_plan', {}).get('commands', [])}"
                )
            )
            print(
                _ascii_safe(
                    f"   Run: ai_onboard aaol execute --session-id {args.session_id}"
                )
            )
        else:
            print(_ascii_safe(f"\n💬 Waiting for more input..."))

        return True

    elif args.aaol_cmd == "execute":
        # Execute planned commands
        result = orchestrator.execute_plan(args.session_id)

        print(_ascii_safe("🚀 Execution Results:"))
        print(_ascii_safe("=" * 40))

        if result.get("success"):
            print(_ascii_safe("✅ All commands executed successfully!"))
            print(_ascii_safe(f"   Executed: {result.get('executed_commands', [])}"))
        else:
            print(_ascii_safe("❌ Execution failed!"))
            print(_ascii_safe(f"   Failed command: {result.get('failed_command')}"))
            print(_ascii_safe(f"   Error: {result.get('error_details')}"))

            if result.get("rollback_performed"):
                print(
                    _ascii_safe(
                        "🔄 Automatic rollback performed - system restored to previous state"
                    )
                )
            else:
                print(
                    _ascii_safe(
                        "⚠️  Rollback failed - manual intervention may be required"
                    )
                )

        return True

    elif args.aaol_cmd == "status":
        # Get session status
        status = orchestrator.get_session_status(args.session_id)

        print(_ascii_safe("📊 Session Status:"))
        print(_ascii_safe("=" * 30))
        print(_ascii_safe(json.dumps(status, indent=2, default=str)))

        return True

    elif args.aaol_cmd == "list-sessions":
        # List all sessions
        sessions = orchestrator.list_sessions(
            args.user_id if hasattr(args, "user_id") else None
        )

        print(_ascii_safe("📋 Available Sessions:"))
        print(_ascii_safe("=" * 40))

        if not sessions:
            print(_ascii_safe("No sessions found."))
        else:
            for session in sessions:
                print(_ascii_safe(f"  Session ID: {session['session_id']}"))
                print(_ascii_safe(f"  User: {session['user_id']}"))
                print(_ascii_safe(f"  State: {session['state']}"))
                print(_ascii_safe(f"  Created: {time.ctime(session['created_at'])}"))
                print(
                    _ascii_safe(
                        f"  Last Activity: {time.ctime(session['last_activity'])}"
                    )
                )
                print(_ascii_safe("  " + "-" * 40))

        return True

    elif args.aaol_cmd == "delete-session":
        # Delete a session
        if orchestrator.delete_session(args.session_id):
            print(_ascii_safe("✅ Session deleted successfully"))
        else:
            print(_ascii_safe("❌ Failed to delete session"))

        return True

    elif args.aaol_cmd == "cleanup":
        # Clean up expired sessions
        deleted_count = orchestrator.cleanup_expired_sessions()
        print(_ascii_safe(f"🧹 Cleaned up {deleted_count} expired sessions"))

        return True

    elif args.aaol_cmd == "demo":
        # Interactive demo
        print(_ascii_safe("🚀 AI Agent Orchestration Layer (AAOL) Demo"))
        print(_ascii_safe("=" * 50))
        print(
            _ascii_safe(
                "This demo shows how AI agents can have collaborative conversations"
            )
        )
        print(_ascii_safe("with advanced decision-making and safety monitoring.\n"))

        # Create demo session
        session_id = orchestrator.create_session("demo_user")
        print(_ascii_safe(f"✅ Created demo session: {session_id}\n"))

        # Demo conversation scenarios
        demo_scenarios = [
            "I want to analyze my project and understand what it does",
            "Actually, I want to focus on real-time orderflow visualizations",
            "Can you add features for chart visualizations and data streaming?",
            "Yes, proceed with the plan",
        ]

        for i, scenario in enumerate(demo_scenarios, 1):
            print(_ascii_safe(f"📝 Demo Scenario {i}: {scenario}"))
            result = orchestrator.process_conversation(session_id, scenario)

            if result.get("ai_agent_response"):
                print("[AI] " + _ascii_safe(str(result["ai_agent_response"])))

            if result.get("ready_to_execute"):
                print(
                    _ascii_safe(
                        f"🚀 Ready to execute: {result.get('execution_plan', {}).get('commands', [])}"
                    )
                )

                # In real demo, would ask user if they want to execute
                print(_ascii_safe("   [Demo mode - not executing actual commands]\n"))
            else:
                print(_ascii_safe("   [Continuing conversation...]\n"))

        print(_ascii_safe("🎯 Demo completed! The AAOL system provides:"))
        print(_ascii_safe("✅ Natural conversation processing"))
        print(_ascii_safe("✅ Multi-stage decision pipeline"))
        print(_ascii_safe("✅ Real-time safety monitoring"))
        print(_ascii_safe("✅ Command orchestration with rollback"))
        print(_ascii_safe("✅ Session-based context management"))

        return True

    return False
