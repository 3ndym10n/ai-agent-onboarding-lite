"""
CLI commands for Cursor AI integration.

This module provides command - line interfaces for:
- Initializing and configuring Cursor AI integration
- Managing collaboration sessions
- Translating natural language commands
- Getting project context for Cursor AI
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from ..core.ai_integration.cursor_ai_integration import (
    get_cursor_integration,
    get_cursor_project_context,
    initialize_cursor_integration,
    translate_cursor_command,
)
from .console import safe_print


def add_cursor_commands(subparsers):
    """Add Cursor AI integration commands to the CLI."""

    # Main cursor command
    cursor_parser = subparsers.add_parser(
        "cursor", help="Cursor AI integration commands"
    )
    cursor_sub = cursor_parser.add_subparsers(dest="cursor_cmd", required=True)

    # Initialize command
    init_parser = cursor_sub.add_parser("init", help="Initialize Cursor AI integration")
    init_parser.add_argument(
        "--force", action="store_true", help="Force re - initialization"
    )

    # Status command
    cursor_sub.add_parser("status", help="Show Cursor integration status")

    # Context command
    context_parser = cursor_sub.add_parser(
        "context", help="Get project context for Cursor AI"
    )
    context_parser.add_argument(
        "--format", choices=["json", "summary"], default="json", help="Output format"
    )

    # Session command
    session_parser = cursor_sub.add_parser(
        "session", help="Manage collaboration sessions"
    )
    session_sub = session_parser.add_subparsers(dest="session_action", required=True)

    # Session create
    create_parser = session_sub.add_parser(
        "create", help="Create collaboration session"
    )
    create_parser.add_argument(
        "--user-id", default="cursor_user", help="User ID for session"
    )

    # Session list
    session_sub.add_parser("list", help="List active sessions")

    # Session status
    status_parser = session_sub.add_parser("status", help="Get session status")
    status_parser.add_argument("session_id", help="Session ID to check")

    # Session end
    end_parser = session_sub.add_parser("end", help="End a session")
    end_parser.add_argument("session_id", help="Session ID to end")

    # Translate command
    translate_parser = cursor_sub.add_parser(
        "translate", help="Translate natural language to commands"
    )
    translate_parser.add_argument("text", help="Natural language text to translate")
    translate_parser.add_argument(
        "--execute", action="store_true", help="Execute the translated command"
    )

    # Config command
    config_parser = cursor_sub.add_parser("config", help="Configure Cursor integration")
    config_sub = config_parser.add_subparsers(dest="config_action", required=True)

    # Config show
    config_sub.add_parser("show", help="Show current configuration")

    # Config set
    set_parser = config_sub.add_parser("set", help="Set configuration value")
    set_parser.add_argument("key", help="Configuration key")
    set_parser.add_argument("value", help="Configuration value")

    # Guided setup command
    guided_parser = cursor_sub.add_parser(
        "guided-setup",
        help="Guided flow: initialize integration, show context, create a session",
    )
    guided_parser.add_argument(
        "--user-id", default="cursor_user", help="User ID to assign to the session"
    )
    guided_parser.add_argument(
        "--force-init",
        action="store_true",
        help="Force re-initialization even if a session already exists",
    )
    guided_parser.add_argument(
        "--skip-session",
        action="store_true",
        help="Skip automatic session creation (init + context only)",
    )


def handle_cursor_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle Cursor AI integration commands."""

    if args.cursor_cmd == "init":
        _handle_cursor_init(args, root)
    elif args.cursor_cmd == "status":
        _handle_cursor_status(args, root)
    elif args.cursor_cmd == "context":
        _handle_cursor_context(args, root)
    elif args.cursor_cmd == "session":
        _handle_cursor_session(args, root)
    elif args.cursor_cmd == "translate":
        _handle_cursor_translate(args, root)
    elif args.cursor_cmd == "config":
        _handle_cursor_config(args, root)
    elif args.cursor_cmd == "guided-setup":
        _handle_cursor_guided_setup(args, root)
    else:
        safe_print(f"Unknown cursor command: {args.cursor_cmd}")


def _handle_cursor_init(args: argparse.Namespace, root: Path) -> None:
    """Handle cursor init command."""
    safe_print("🚀 Initializing Cursor AI integration...")

    try:
        if args.force:
            # Force re-initialization by resetting the global instance
            # Import the module and reset the global variable
            from ai_onboard.core.ai_integration import cursor_ai_integration as cai

            cai._cursor_integration = None

        result = initialize_cursor_integration(root)

        if result["success"]:
            safe_print("✅ Cursor AI integration initialized successfully!")
            safe_print("\n📊 Integration Status:")
            status = result["status"]
            safe_print(f"  Agent ID: {status['agent_id']}")
            safe_print(f"  Safety Level: {status['safety_level']}")
            safe_print(f"  Max Autonomous Actions: {status['max_autonomous_actions']}")
            safe_print(f"  Session Timeout: {status['session_timeout']}s")

            safe_print("\n🎯 Next Steps:")
            safe_print("  1. Install the Cursor AI Onboard extension (when available)")
            safe_print("  2. Use 'ai_onboard cursor context' to get project context")
            safe_print(
                "  3. Create a collaboration session with 'ai_onboard cursor session create'"
            )

        else:
            safe_print(
                f"❌ Failed to initialize Cursor AI integration: {result.get('error')}"
            )

    except Exception as e:
        safe_print(f"❌ Initialization error: {e}")


def _handle_cursor_status(args: argparse.Namespace, root: Path) -> None:
    """Handle cursor status command."""
    try:
        integration = get_cursor_integration(root)
        status = integration.get_integration_status()

        safe_print("📊 Cursor AI Integration Status")
        safe_print("=" * 40)
        safe_print(f"Enabled: {'✅' if status['enabled'] else '❌'}")
        safe_print(f"Agent ID: {status['agent_id']}")
        safe_print(f"Safety Level: {status['safety_level']}")
        safe_print(f"Max Autonomous Actions: {status['max_autonomous_actions']}")
        safe_print(f"Session Timeout: {status['session_timeout']}s")
        safe_print(f"API Enabled: {'✅' if status['api_enabled'] else '❌'}")
        if status["api_enabled"]:
            safe_print(f"API Port: {status['api_port']}")
        safe_print(f"Last Initialized: {status['last_initialized']}")

    except Exception as e:
        safe_print(f"❌ Failed to get status: {e}")


def _handle_cursor_context(args: argparse.Namespace, root: Path) -> None:
    """Handle cursor context command."""
    try:
        context = get_cursor_project_context(root)

        if args.format == "json":
            safe_print(json.dumps(context, indent=2, default=str))
        else:  # summary format
            safe_print("🏗️  Project Context Summary")
            safe_print("=" * 40)
            safe_print(f"Project Root: {context.get('project_root', 'Unknown')}")

            if "progress" in context:
                progress = context["progress"]
                safe_print(f"Overall Progress: {progress.get('overall_progress', 0):.1f}%")
                safe_print(
                    f"Completed Tasks: {progress.get('completed_tasks', 0)}/"
                    f"{progress.get('total_tasks', 0)}"
                )
                safe_print(f"Current Phase: {progress.get('current_phase', 'Unknown')}")

            if "integration_status" in context:
                integration = context["integration_status"]
                safe_print(
                    f"Integration: {'✅ Active' if integration.get('enabled') else '❌ Disabled'}"
                )

            if "available_commands" in context:
                commands = context["available_commands"]
                safe_print(f"Available Commands: {', '.join(commands)}")

            if "error" in context:
                safe_print(f"❌ Error: {context['error']}")

    except Exception as e:
        safe_print(f"❌ Failed to get context: {e}")


def _handle_cursor_guided_setup(args: argparse.Namespace, root: Path) -> None:
    """Run a guided setup that strings together init, context, and session creation."""

    safe_print("")
    safe_print("=== Cursor Guided Setup ===")
    safe_print("This walkthrough initializes Cursor, shows current status, and spins up a session.")

    # Step 1: initialization (optional force)
    safe_print("\n[1/4] Initializing Cursor integration...")
    _handle_cursor_init(argparse.Namespace(force=args.force_init), root)

    # Step 2: current integration status overview
    safe_print("\n[2/4] Checking integration status...")
    _handle_cursor_status(argparse.Namespace(), root)

    # Step 3: project context summary
    safe_print("\n[3/4] Reviewing project context summary...")
    _handle_cursor_context(argparse.Namespace(format="summary"), root)

    if args.skip_session:
        safe_print(
            "\nSkipping session creation (use 'ai_onboard cursor session create' when ready)."
        )
        safe_print("Guided setup complete.")
        return

    # Step 4: create a collaboration session
    safe_print("\n[4/4] Creating a collaboration session...")
    create_args = argparse.Namespace(session_action="create", user_id=args.user_id)
    session_result = _handle_cursor_session(create_args, root)

    session_id = (
        session_result.get("session_id")
        if isinstance(session_result, dict)
        else None
    )

    if session_id:
        safe_print("\nSession created successfully. Performing quick status check...")
        status_args = argparse.Namespace(session_action="status", session_id=session_id)
        _handle_cursor_session(status_args, root)
        safe_print("\nGuided setup complete. Happy collaborating!")
    else:
        safe_print(
            "\nGuided setup finished, but session creation reported an issue. "
            "Run 'ai_onboard cursor session list' or '... session create' for details."
        )


def _handle_cursor_session(args: argparse.Namespace, root: Path) -> Dict[str, Any]:
    """Handle cursor session commands and return the resulting payload."""
    integration = get_cursor_integration(root)

    if args.session_action == "create":
        try:
            result = integration.create_collaboration_session(args.user_id)

            if result["success"]:
                safe_print("✅ Collaboration session created successfully!")
                safe_print(f"   Session ID: {result['session_id']}")
                safe_print(f"   User ID: {args.user_id}")
                safe_print(f"   Message: {result['message']}")

                # Show session details if available
                if result.get("agent_profile"):
                    profile = result["agent_profile"]
                    safe_print(f"\n🤖 Agent Profile:")
                    safe_print(f"   Name: {profile.get('name')}")
                    safe_print(
                        f"   Capabilities: {', '.join(profile.get('capabilities', []))}"
                    )
                    safe_print(f"   Safety Level: {profile.get('safety_level')}")

                if result.get("session_limits"):
                    limits = result["session_limits"]
                    safe_print(f"\n⚙️  Session Limits:")
                    safe_print(
                        f"   Max Autonomous Actions: {limits.get('max_autonomous_actions')}"
                    )
                    safe_print(f"   Session Timeout: {limits.get('session_timeout')}s")

                safe_print("\n🤝 Session is ready for Cursor AI collaboration!")
                safe_print(
                    "Use 'ai_onboard cursor session status <session_id>' to check session status."
                )
            else:
                safe_print(f"❌ Failed to create session: {result['error']}")

        except Exception as e:
            safe_print(f"❌ Session creation error: {e}")
            result = {"success": False, "error": str(e)}

        return result

    elif args.session_action == "list":
        try:
            result = integration.list_active_sessions()

            if result["success"]:
                sessions = result["sessions"]
                safe_print(f"📋 Active Cursor AI Sessions ({result['count']})")
                safe_print("=" * 50)

                if sessions:
                    for session in sessions:
                        safe_print(f"Session ID: {session.get('session_id')}")
                        safe_print(f"  Status: {session.get('status')}")
                        safe_print(f"  Started: {session.get('started_at')}")
                        safe_print(f"  Last Activity: {session.get('last_activity')}")
                        safe_print()
                else:
                    safe_print("No active sessions found.")
            else:
                safe_print(f"❌ Failed to list sessions: {result['error']}")

        except Exception as e:
            safe_print(f"❌ Session listing error: {e}")
            result = {"success": False, "error": str(e)}

        return result

    elif args.session_action == "status":
        try:
            result = integration.get_session_status(args.session_id)

            if result["success"]:
                status = result["session_status"]
                safe_print(f"📊 Session Status: {args.session_id}")
                safe_print("=" * 40)
                safe_print(f"Status: {status.get('status')}")
                safe_print(f"Message: {status.get('message', 'N / A')}")

                if status.get("session_info"):
                    info = status["session_info"]
                    safe_print(f"Agent ID: {info.get('agent_id')}")
                    safe_print(f"Started At: {info.get('started_at')}")
                    safe_print(f"Last Activity: {info.get('last_activity')}")
            else:
                safe_print(f"❌ Failed to get session status: {result['error']}")

        except Exception as e:
            safe_print(f"❌ Session status error: {e}")
            result = {"success": False, "error": str(e)}

        return result

    elif args.session_action == "end":
        try:
            result = integration.end_session(args.session_id)

            if result["success"]:
                safe_print(f"✅ Session ended successfully: {args.session_id}")
                safe_print(f"   Message: {result['message']}")
            else:
                safe_print(f"❌ Failed to end session: {result['error']}")

        except Exception as e:
            safe_print(f"❌ Session end error: {e}")
            result = {"success": False, "error": str(e)}

        return result

    else:
        safe_print(f"Unknown session action: {args.session_action}")
        safe_print("Available actions: create, list, status, end")
        return {"success": False, "error": "unknown_action"}


def _handle_cursor_translate(args: argparse.Namespace, root: Path) -> None:
    """Handle cursor translate command."""
    try:
        result = translate_cursor_command(args.text, root)

        if result["success"]:
            safe_print(f"🔤 Translation Result:")
            safe_print(f"  Input: '{args.text}'")
            safe_print(f"  Command: ai_onboard {result['command']}")
            safe_print(f"  Confidence: {result['confidence']:.1%}")

            if result.get("suggested_args"):
                args_str = " " + " ".join(result["suggested_args"])
                safe_print(f"  Full Command: ai_onboard {result['command']}{args_str}")

            if args.execute:
                safe_print(f"\n⚡ Executing: ai_onboard {result['command']}")
                # Here you would execute the actual command
                # For now, just show what would be executed
                safe_print("(Command execution not implemented in this demo)")
        else:
            safe_print(f"❌ Translation failed: {result['error']}")
            if "suggestions" in result:
                safe_print(f"💡 Available commands: {', '.join(result['suggestions'])}")

    except Exception as e:
        safe_print(f"❌ Translation error: {e}")


def _handle_cursor_config(args: argparse.Namespace, root: Path) -> None:
    """Handle cursor config commands."""
    if args.config_action == "show":
        try:
            integration = get_cursor_integration(root)
            config = integration.config

            safe_print("⚙️  Cursor AI Integration Configuration")
            safe_print("=" * 45)
            safe_print(f"Enabled: {config.enabled}")
            safe_print(f"Auto Analyze: {config.auto_analyze}")
            safe_print(f"Show Status Bar: {config.show_status_bar}")
            safe_print(f"Show Sidebar: {config.show_sidebar}")
            safe_print(f"Agent ID: {config.agent_id}")
            safe_print(f"Safety Level: {config.safety_level}")
            safe_print(f"Max Autonomous Actions: {config.max_autonomous_actions}")
            safe_print(f"Require Confirmation: {', '.join(config.require_confirmation)}")
            safe_print(f"Session Timeout: {config.session_timeout}s")
            safe_print(f"API Enabled: {config.api_enabled}")
            if config.api_enabled:
                safe_print(f"API Port: {config.api_port}")

        except Exception as e:
            safe_print(f"❌ Failed to show config: {e}")

    elif args.config_action == "set":
        try:
            integration = get_cursor_integration(root)

            # Simple configuration setting (can be enhanced)
            valid_keys = {
                "enabled": bool,
                "auto_analyze": bool,
                "show_status_bar": bool,
                "show_sidebar": bool,
                "safety_level": str,
                "max_autonomous_actions": int,
                "session_timeout": int,
                "api_enabled": bool,
                "api_port": int,
            }

            if args.key not in valid_keys:
                safe_print(f"❌ Invalid configuration key: {args.key}")
                safe_print(f"Valid keys: {', '.join(valid_keys.keys())}")
                return

            # Convert value to appropriate type
            value_type = valid_keys[args.key]
            value: Any  # Type can vary based on value_type
            if value_type == bool:
                value = args.value.lower() in ("true", "yes", "1", "on")
            elif value_type == int:
                value = int(args.value)
            else:
                value = args.value

            # Set the configuration value
            setattr(integration.config, args.key, value)
            integration._save_config(integration.config)

            safe_print(f"✅ Configuration updated: {args.key} = {value}")
            safe_print("💡 Restart may be required for some changes to take effect")

        except ValueError:
            safe_print(f"❌ Invalid value for {args.key}: {args.value}")
        except Exception as e:
            safe_print(f"❌ Failed to set config: {e}")
    else:
        safe_print(f"Unknown config action: {args.config_action}")
