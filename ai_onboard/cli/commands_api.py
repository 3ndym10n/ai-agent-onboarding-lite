"""
CLI commands for API server management.

This module provides command - line interfaces for:
- Starting and stopping the API server
- Managing API configuration
- Testing API endpoints
- Monitoring API health and performance
"""

import argparse
import json
from pathlib import Path

from ..core.unicode_utils import print_activity, print_content, print_status

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


def add_api_commands(subparsers):
    """Add API server management commands to the CLI."""

    # Main API command
    api_parser = subparsers.add_parser("api", help="API server management commands")
    api_sub = api_parser.add_subparsers(dest="api_cmd", required = True)

    # Start server command
    start_parser = api_sub.add_parser("start", help="Start the API server")
    start_parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    start_parser.add_argument("--port", type = int, default = 8080, help="Port to bind to")
    start_parser.add_argument(
        "--reload", action="store_true", help="Enable auto - reload for development"
    )
    start_parser.add_argument(
        "--background", action="store_true", help="Run in background"
    )

    # Stop server command
    api_sub.add_parser("stop", help="Stop the API server")

    # Status command
    status_parser = api_sub.add_parser("status", help="Check API server status")
    status_parser.add_argument("--url", help="API server URL to check")

    # Test command
    test_parser = api_sub.add_parser("test", help="Test API endpoints")
    test_parser.add_argument("--endpoint", help="Specific endpoint to test")
    test_parser.add_argument(
        "--url", default="http://127.0.0.1:8080", help="API server URL"
    )

    # Config command
    config_parser = api_sub.add_parser("config", help="Manage API configuration")
    config_sub = config_parser.add_subparsers(dest="config_action", required = True)

    # Config show
    config_sub.add_parser("show", help="Show current API configuration")

    # Config set
    set_parser = config_sub.add_parser("set", help="Set configuration value")
    set_parser.add_argument("key", help="Configuration key")
    set_parser.add_argument("value", help="Configuration value")

    # Docs command
    docs_parser = api_sub.add_parser("docs", help="Open API documentation")
    docs_parser.add_argument(
        "--url", default="http://127.0.0.1:8080", help="API server URL"
    )


def handle_api_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle API server management commands."""

    if args.api_cmd == "start":
        _handle_api_start(args, root)
    elif args.api_cmd == "stop":
        _handle_api_stop(args, root)
    elif args.api_cmd == "status":
        _handle_api_status(args, root)
    elif args.api_cmd == "test":
        _handle_api_test(args, root)
    elif args.api_cmd == "config":
        _handle_api_config(args, root)
    elif args.api_cmd == "docs":
        _handle_api_docs(args, root)
    else:
        print(f"Unknown API command: {args.api_cmd}")


def _handle_api_start(args: argparse.Namespace, root: Path) -> None:
    """Handle API server start command."""
    try:
        from ..api.server import get_api_server

        print_activity(f"Starting AI Onboard API server...", "start")
        print(f"   Host: {args.host}")
        print(f"   Port: {args.port}")
        print(f"   Project: {root}")

        # Create server instance
        server = get_api_server(root, args.host, args.port)

        if args.background:
            print_status("Background mode not yet implemented", "error")
            print("Use a process manager like PM2 or systemd for production deployment")
            return

        # Server configuration (don't include host / port since they're already set in constructor)
        server_config = {}

        if args.reload:
            server_config["reload"] = True
            print_activity("Auto - reload enabled (development mode)", "sync")

        print_content("\nAPI Documentation will be available at:", "docs")
        print(f"   Swagger UI: http://{args.host}:{args.port}/docs")
        print(f"   ReDoc: http://{args.host}:{args.port}/redoc")

        print_content("\nKey Endpoints:", "link")
        print(f"   Health Check: http://{args.host}:{args.port}/health")
        print(
            f"   Project Status: http://{args.host}:{args.port}/api / v1 / project / status"
        )
        print(f"   WebSocket: ws://{args.host}:{args.port}/api / v1 / ws/{{client_id}}")

        print_content(f"\nReady for Cursor AI integration!", "target")
        print("Press Ctrl + C to stop the server\n")

        # Run the server
        server.run(**server_config)

    except ImportError as e:
        print("❌ Missing dependencies for API server")
        print("📦 Install required packages:")
        print("   pip install fastapi uvicorn")
        print(f"   Error: {e}")
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")


def _handle_api_stop(args: argparse.Namespace, root: Path) -> None:
    """Handle API server stop command."""
    print("🛑 API server stop command")
    print("💡 Use Ctrl + C to stop a running server, or kill the process")
    print("   For production deployments, use your process manager's stop command")


def _handle_api_status(args: argparse.Namespace, root: Path) -> None:
    """Handle API server status command."""
    if not REQUESTS_AVAILABLE:
        print("❌ requests library required for status checks")
        print("📦 Install with: pip install requests")
        return

    url = args.url or "http://127.0.0.1:8080"
    health_url = f"{url}/health"

    print(f"🔍 Checking API server status: {url}")

    try:
        # Check health endpoint
        response = requests.get(health_url, timeout = 5)

        if response.status_code == 200:
            health_data = response.json()

            print("✅ API server is running")
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Uptime: {health_data.get('uptime_seconds', 0)}s")
            print(f"   Active Sessions: {health_data.get('active_sessions', 0)}")
            print(f"   Active Operations: {health_data.get('active_operations', 0)}")

            # Check project status
            try:
                status_response = requests.get(
                    f"{url}/api / v1 / project / status", timeout = 5
                )
                if status_response.status_code == 200:
                    project_data = status_response.json()
                    print(
                        f"   Project Progress: {project_data.get('overall_progress', 0):.1f}%"
                    )
                    print(
                        f"   Current Phase: {project_data.get('current_phase', 'unknown')}"
                    )
            except:
                pass

        else:
            print(f"❌ API server returned status {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("❌ API server is not running or not accessible")
        print(f"   Tried to connect to: {health_url}")
    except requests.exceptions.Timeout:
        print("❌ API server is not responding (timeout)")
    except Exception as e:
        print(f"❌ Error checking API status: {e}")


def _handle_api_test(args: argparse.Namespace, root: Path) -> None:
    """Handle API endpoint testing."""
    if not REQUESTS_AVAILABLE:
        print("❌ requests library required for API testing")
        print("📦 Install with: pip install requests")
        return

    base_url = args.url

    print(f"🧪 Testing AI Onboard API: {base_url}")

    # Test endpoints to check
    test_endpoints = [
        ("GET", "/health", "Health Check"),
        ("GET", "/api / v1 / project / status", "Project Status"),
        ("POST", "/api / v1 / translate", "Natural Language Translation"),
    ]

    if args.endpoint:
        # Test specific endpoint
        print(f"🎯 Testing specific endpoint: {args.endpoint}")
        test_endpoints = [("GET", args.endpoint, "Custom Endpoint")]

    results = []

    for method, endpoint, description in test_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 Testing {description}: {method} {endpoint}")

        try:
            if method == "GET":
                response = requests.get(url, timeout = 10)
            elif method == "POST":
                if endpoint == "/api / v1 / translate":
                    # Test natural language translation
                    test_data = {"text": "analyze this project"}
                    response = requests.post(url, json = test_data, timeout = 10)
                else:
                    response = requests.post(url, json={}, timeout = 10)

            # Check response
            if response.status_code == 200:
                print(f"   ✅ Success ({response.status_code})")

                # Show response preview for key endpoints
                if endpoint in ["/health", "/api / v1 / project / status"]:
                    data = response.json()
                    if isinstance(data, dict):
                        for key, value in list(data.items())[:3]:
                            print(f"   📊 {key}: {value}")

                results.append(("✅", description, response.status_code))
            else:
                print(f"   ❌ Failed ({response.status_code})")
                results.append(("❌", description, response.status_code))

        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed")
            results.append(("❌", description, "Connection Error"))
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout")
            results.append(("❌", description, "Timeout"))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append(("❌", description, str(e)))

    # Summary
    print(f"\n📊 Test Results Summary:")
    print("=" * 50)

    success_count = sum(1 for status, _, _ in results if status == "✅")
    total_count = len(results)

    for status, description, code in results:
        print(f"   {status} {description}: {code}")

    print(
        f"\n🎯 Success Rate: {success_count}/{total_count} ({success_count / total_count * 100:.1f}%)"
    )

    if success_count == total_count:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check server logs for details.")


def _handle_api_config(args: argparse.Namespace, root: Path) -> None:
    """Handle API configuration management."""
    config_path = root / ".ai_onboard" / "api_config.json"

    if args.config_action == "show":
        try:
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)

                print("⚙️  API Server Configuration")
                print("=" * 35)

                for key, value in config.items():
                    print(f"{key}: {value}")
            else:
                print("📝 No API configuration found")
                print("💡 Configuration will be created when you start the API server")

        except Exception as e:
            print(f"❌ Failed to read configuration: {e}")

    elif args.config_action == "set":
        try:
            # Load existing config or create new
            config = {}
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)

            # Convert value to appropriate type
            value = args.value
            if value.lower() in ("true", "false"):
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
            elif "." in value and value.replace(".", "").isdigit():
                value = float(value)

            # Set the value
            config[args.key] = value

            # Ensure directory exists
            config_path.parent.mkdir(parents = True, exist_ok = True)

            # Save configuration
            with open(config_path, "w") as f:
                json.dump(config, f, indent = 2)

            print(f"✅ Configuration updated: {args.key} = {value}")

        except Exception as e:
            print(f"❌ Failed to set configuration: {e}")


def _handle_api_docs(args: argparse.Namespace, root: Path) -> None:
    """Handle opening API documentation."""
    base_url = args.url
    docs_url = f"{base_url}/docs"
    redoc_url = f"{base_url}/redoc"

    print(f"📚 AI Onboard API Documentation")
    print("=" * 40)
    print(f"Swagger UI: {docs_url}")
    print(f"ReDoc: {redoc_url}")

    # Try to open in browser
    try:
        import webbrowser

        print(f"\n🌐 Opening documentation in browser...")
        webbrowser.open(docs_url)
        print("✅ Documentation opened in your default browser")

    except ImportError:
        print("\n💡 Copy the URL above and paste it into your browser")
    except Exception as e:
        print(f"\n❌ Failed to open browser: {e}")
        print("💡 Copy the URL above and paste it into your browser")
