"""
CLI commands for Cursor AI integration.

This module provides command - line interfaces for:
- Initializing and configuring Cursor AI integration
- Managing collaboration sessions
- Translating natural language commands
- Getting project context for Cursor AI
"""

import argparse
from pathlib import Path

from ..core.cursor_ai_integration import (
    get_cursor_integration,
    get_cursor_project_context,
    initialize_cursor_integration,
    translate_cursor_command,
)


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
        "--user - id", default="cursor_user", help="User ID for session"
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
    else:
        print(f"Unknown cursor command: {args.cursor_cmd}")


def _handle_cursor_init(args: argparse.Namespace, root: Path) -> None:
    """Handle cursor init command."""
    print("🚀 Initializing Cursor AI integration...")

    try:
        if args.force:
            # Force re - initialization by recreating the integration
            global _cursor_integration
            from ..core.cursor_ai_integration import _cursor_integration

            _cursor_integration = None

        result = initialize_cursor_integration(root)

        if result["success"]:
            print("✅ Cursor AI integration initialized successfully!")
            print("\n📊 Integration Status:")
            status = result["status"]
            print(f"  Agent ID: {status['agent_id']}")
            print(f"  Safety Level: {status['safety_level']}")
            print(f"  Max Autonomous Actions: {status['max_autonomous_actions']}")
            print(f"  Session Timeout: {status['session_timeout']}s")

            print("\n🎯 Next Steps:")
            print("  1. Install the Cursor AI Onboard extension (when available)")
            print("  2. Use 'ai_onboard cursor context' to get project context")
            print(
                "  3. Create a collaboration session with 'ai_onboard cursor session create'"
            )

        else:
            print(
                f"❌ Failed to initialize Cursor AI integration: {result.get('error')}"
            )

    except Exception as e:
        print(f"❌ Initialization error: {e}")


def _handle_cursor_status(args: argparse.Namespace, root: Path) -> None:
    """Handle cursor status command."""
    try:
        integration = get_cursor_integration(root)
        status = integration.get_integration_status()

        print("📊 Cursor AI Integration Status")
        print("=" * 40)
        print(f"Enabled: {'✅' if status['enabled'] else '❌'}")
        print(f"Agent ID: {status['agent_id']}")
        print(f"Safety Level: {status['safety_level']}")
        print(f"Max Autonomous Actions: {status['max_autonomous_actions']}")
        print(f"Session Timeout: {status['session_timeout']}s")
        print(f"API Enabled: {'✅' if status['api_enabled'] else '❌'}")
        if status["api_enabled"]:
            print(f"API Port: {status['api_port']}")
        print(f"Last Initialized: {status['last_initialized']}")

    except Exception as e:
        print(f"❌ Failed to get status: {e}")


def _handle_cursor_context(args: argparse.Namespace, root: Path) -> None:
    """Handle cursor context command."""
    try:
        context = get_cursor_project_context(root)

        if args.format == "json":
            print(json.dumps(context, indent=2, default=str))
        else:  # summary format
            print("🏗️  Project Context Summary")
            print("=" * 40)
            print(f"Project Root: {context.get('project_root', 'Unknown')}")

            if "progress" in context:
                progress = context["progress"]
                print(f"Overall Progress: {progress.get('overall_progress', 0):.1f}%")
                print(
                    f"Completed Tasks: {progress.get('completed_tasks',
                        0)}/{progress.get('total_tasks', 0)}"
                )
                print(f"Current Phase: {progress.get('current_phase', 'Unknown')}")

            if "integration_status" in context:
                integration = context["integration_status"]
                print(
                    f"Integration: {'✅ Active' if integration.get('enabled') else '❌ Disabled'}"
                )

            if "available_commands" in context:
                commands = context["available_commands"]
                print(f"Available Commands: {', '.join(commands)}")

            if "error" in context:
                print(f"❌ Error: {context['error']}")

    except Exception as e:
        print(f"❌ Failed to get context: {e}")


def _handle_cursor_session(args: argparse.Namespace, root: Path) -> None:
    """Handle cursor session commands."""
    integration = get_cursor_integration(root)

    if args.session_action == "create":
        try:
            result = integration.create_collaboration_session(args.user_id)

            if result["success"]:
                print(f"✅ Collaboration session created successfully!")
                print(f"   Session ID: {result['session_id']}")
                print(f"   User ID: {args.user_id}")
                print(f"   Message: {result['message']}")

                # Show session details if available
                if result.get("agent_profile"):
                    profile = result["agent_profile"]
                    print(f"\n🤖 Agent Profile:")
                    print(f"   Name: {profile.get('name')}")
                    print(
                        f"   Capabilities: {', '.join(profile.get('capabilities', []))}"
                    )
                    print(f"   Safety Level: {profile.get('safety_level')}")

                if result.get("session_limits"):
                    limits = result["session_limits"]
                    print(f"\n⚙️  Session Limits:")
                    print(
                        f"   Max Autonomous Actions: {limits.get('max_autonomous_actions')}"
                    )
                    print(f"   Session Timeout: {limits.get('session_timeout')}s")

                print("\n🤝 Session is ready for Cursor AI collaboration!")
                print(
                    "Use 'ai_onboard cursor session status <session_id>' to check session status."
                )
            else:
                print(f"❌ Failed to create session: {result['error']}")

        except Exception as e:
            print(f"❌ Session creation error: {e}")

    elif args.session_action == "list":
        try:
            result = integration.list_active_sessions()

            if result["success"]:
                sessions = result["sessions"]
                print(f"📋 Active Cursor AI Sessions ({result['count']})")
                print("=" * 50)

                if sessions:
                    for session in sessions:
                        print(f"Session ID: {session.get('session_id')}")
                        print(f"  Status: {session.get('status')}")
                        print(f"  Started: {session.get('started_at')}")
                        print(f"  Last Activity: {session.get('last_activity')}")
                        print()
                else:
                    print("No active sessions found.")
            else:
                print(f"❌ Failed to list sessions: {result['error']}")

        except Exception as e:
            print(f"❌ Session listing error: {e}")

    elif args.session_action == "status":
        try:
            result = integration.get_session_status(args.session_id)

            if result["success"]:
                status = result["session_status"]
                print(f"📊 Session Status: {args.session_id}")
                print("=" * 40)
                print(f"Status: {status.get('status')}")
                print(f"Message: {status.get('message', 'N / A')}")

                if status.get("session_info"):
                    info = status["session_info"]
                    print(f"Agent ID: {info.get('agent_id')}")
                    print(f"Started At: {info.get('started_at')}")
                    print(f"Last Activity: {info.get('last_activity')}")
            else:
                print(f"❌ Failed to get session status: {result['error']}")

        except Exception as e:
            print(f"❌ Session status error: {e}")

    elif args.session_action == "end":
        try:
            result = integration.end_session(args.session_id)

            if result["success"]:
                print(f"✅ Session ended successfully: {args.session_id}")
                print(f"   Message: {result['message']}")
            else:
                print(f"❌ Failed to end session: {result['error']}")

        except Exception as e:
            print(f"❌ Session end error: {e}")

    else:
        print(f"Unknown session action: {args.session_action}")
        print("Available actions: create, list, status, end")


def _handle_cursor_translate(args: argparse.Namespace, root: Path) -> None:
    """Handle cursor translate command."""
    try:
        result = translate_cursor_command(args.text, root)

        if result["success"]:
            print(f"🔤 Translation Result:")
            print(f"  Input: '{args.text}'")
            print(f"  Command: ai_onboard {result['command']}")
            print(f"  Confidence: {result['confidence']:.1%}")

            if result.get("suggested_args"):
                args_str = " " + " ".join(result["suggested_args"])
                print(f"  Full Command: ai_onboard {result['command']}{args_str}")

            if args.execute:
                print(f"\n⚡ Executing: ai_onboard {result['command']}")
                # Here you would execute the actual command
                # For now, just show what would be executed
                print("(Command execution not implemented in this demo)")
        else:
            print(f"❌ Translation failed: {result['error']}")
            if "suggestions" in result:
                print(f"💡 Available commands: {', '.join(result['suggestions'])}")

    except Exception as e:
        print(f"❌ Translation error: {e}")


def _handle_cursor_config(args: argparse.Namespace, root: Path) -> None:
    """Handle cursor config commands."""
    if args.config_action == "show":
        try:
            integration = get_cursor_integration(root)
            config = integration.config

            print("⚙️  Cursor AI Integration Configuration")
            print("=" * 45)
            print(f"Enabled: {config.enabled}")
            print(f"Auto Analyze: {config.auto_analyze}")
            print(f"Show Status Bar: {config.show_status_bar}")
            print(f"Show Sidebar: {config.show_sidebar}")
            print(f"Agent ID: {config.agent_id}")
            print(f"Safety Level: {config.safety_level}")
            print(f"Max Autonomous Actions: {config.max_autonomous_actions}")
            print(f"Require Confirmation: {', '.join(config.require_confirmation)}")
            print(f"Session Timeout: {config.session_timeout}s")
            print(f"API Enabled: {config.api_enabled}")
            if config.api_enabled:
                print(f"API Port: {config.api_port}")

        except Exception as e:
            print(f"❌ Failed to show config: {e}")

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
                print(f"❌ Invalid configuration key: {args.key}")
                print(f"Valid keys: {', '.join(valid_keys.keys())}")
                return

            # Convert value to appropriate type
            value_type = valid_keys[args.key]
            if value_type == bool:
                value = args.value.lower() in ("true", "yes", "1", "on")
            elif value_type == int:
                value = int(args.value)
            else:
                value = args.value

            # Set the configuration value
            setattr(integration.config, args.key, value)
            integration._save_config(integration.config)

            print(f"✅ Configuration updated: {args.key} = {value}")
            print("💡 Restart may be required for some changes to take effect")

        except ValueError:
            print(f"❌ Invalid value for {args.key}: {args.value}")
        except Exception as e:
            print(f"❌ Failed to set config: {e}")
    else:
        print(f"Unknown config action: {args.config_action}")
