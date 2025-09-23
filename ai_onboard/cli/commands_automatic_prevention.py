"""
CLI commands for Automatic Error Prevention System.

This module provides command-line interfaces for:
- Analyzing code and commands for potential errors
- Getting prevention recommendations
- Managing prevention rules and patterns
- Reviewing prevention statistics and history
"""

import argparse
from pathlib import Path

from ..core.automatic_error_prevention import AutomaticErrorPrevention
from ..core.pattern_recognition_system import PatternRecognitionSystem


def add_automatic_prevention_commands(subparsers):
    """Add automatic error prevention commands to the CLI."""

    # Main prevention command
    prevention_parser = subparsers.add_parser(
        "prevention",
        help="Automatic error prevention and analysis",
    )
    prevention_sub = prevention_parser.add_subparsers(
        dest="prevention_cmd", required=True
    )

    # Analyze command
    analyze_parser = prevention_sub.add_parser(
        "analyze", help="Analyze content for potential errors"
    )
    analyze_parser.add_argument(
        "--type",
        choices=["code", "command"],
        default="code",
        help="Type of content to analyze",
    )
    analyze_parser.add_argument(
        "--input", required=True, help="File path or command string to analyze"
    )
    analyze_parser.add_argument(
        "--apply-fixes", action="store_true", help="Automatically apply available fixes"
    )

    # Stats command
    stats_parser = prevention_sub.add_parser(
        "stats", help="Show prevention system statistics"
    )

    # Rules command
    rules_parser = prevention_sub.add_parser("rules", help="Manage prevention rules")
    rules_sub = rules_parser.add_subparsers(dest="rules_action", required=True)

    # List rules
    rules_sub.add_parser("list", help="List all prevention rules")

    # Test prevention command
    test_parser = prevention_sub.add_parser(
        "test", help="Test prevention system with sample errors"
    )
    test_parser.add_argument(
        "--error-type",
        choices=["cli", "styling", "import", "type"],
        help="Type of error to test prevention for",
    )


def handle_automatic_prevention_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle automatic error prevention commands."""

    # Initialize systems
    pattern_system = PatternRecognitionSystem(root)
    prevention_system = AutomaticErrorPrevention(root, pattern_system)

    if args.prevention_cmd == "analyze":
        _handle_analyze(args, root, prevention_system)
    elif args.prevention_cmd == "stats":
        _handle_stats(prevention_system)
    elif args.prevention_cmd == "rules":
        _handle_rules(args, prevention_system)
    elif args.prevention_cmd == "test":
        _handle_test(args, root, prevention_system)
    else:
        print(f"Unknown prevention command: {args.prevention_cmd}")


def _handle_analyze(
    args: argparse.Namespace, root: Path, prevention_system: AutomaticErrorPrevention
) -> None:
    """Handle analyze command."""
    print(f"🔍 Analyzing {args.type}: {args.input}")
    print("=" * 50)

    try:
        if args.type == "code":
            # Analyze code file
            file_path = Path(args.input)
            if not file_path.is_absolute():
                file_path = root / args.input

            if not file_path.exists():
                print(f"❌ File not found: {file_path}")
                return

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            result = prevention_system.prevent_code_errors(content, file_path)

        elif args.type == "command":
            # Analyze CLI command
            result = prevention_system.prevent_cli_errors(args.input)

        # Display results
        print("📊 Analysis Results:")
        print(f"Risk Level: {result['risk_level'].upper()}")
        print(f"Confidence: {result['confidence']:.2f}")
        print()

        if result["prevention_applied"]:
            print("🛡️ Applied Preventions:")
            for prevention in result["prevention_applied"]:
                rule = prevention["prevention"]
                print(f"• {rule['action']}: {', '.join(rule['suggestions'])}")
            print()

        if result["recommendations"]:
            print("💡 Recommendations:")
            for rec in result["recommendations"]:
                print(
                    f"• {rec['suggestion']} (confidence: {rec.get('confidence',
                        0):.2f})"
                )
            print()

        # Apply automatic fixes if requested
        if args.apply_fixes and args.type == "code":
            file_path = Path(args.input)
            if not file_path.is_absolute():
                file_path = root / args.input

            fixed_content, applied_fixes = prevention_system.apply_automatic_fixes(
                content, result
            )

            if applied_fixes:
                # Create backup
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Apply fixes
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)

                print("✅ Applied Automatic Fixes:")
                for fix in applied_fixes:
                    print(f"• {fix}")
                print(f"📁 Backup saved to: {backup_path}")
            else:
                print("ℹ️ No automatic fixes available")

    except Exception as e:
        print(f"❌ Analysis failed: {e}")


def _handle_stats(prevention_system: AutomaticErrorPrevention) -> None:
    """Handle stats command."""
    print("📊 Prevention System Statistics")
    print("=" * 40)

    try:
        stats = prevention_system.get_prevention_stats()

        print(f"Preventions Applied: {stats.get('preventions_applied', 0)}")
        print(f"Recommendations Given: {stats.get('recommendations_given', 0)}")
        print(f"High Risk Preventions: {stats.get('high_risk_preventions', 0)}")
        print(f"Auto Fixes Applied: {stats.get('auto_fixes_applied', 0)}")

        if stats.get("error"):
            print(f"❌ Error: {stats['error']}")

    except Exception as e:
        print(f"❌ Failed to get stats: {e}")


def _handle_rules(
    args: argparse.Namespace, prevention_system: AutomaticErrorPrevention
) -> None:
    """Handle rules command."""
    if args.rules_action == "list":
        print("📋 Prevention Rules")
        print("=" * 30)

        for rule in prevention_system.prevention_rules:
            print(f"Rule: {rule.rule_id}")
            print(f"Pattern: {rule.pattern_type}")
            print(f"Priority: {rule.priority}")
            print()


def _handle_test(
    args: argparse.Namespace, root: Path, prevention_system: AutomaticErrorPrevention
) -> None:
    """Handle test command."""
    print("🧪 Testing Prevention System")
    print("=" * 30)

    # Sample test cases
    test_cases = {
        "cli": [
            "python -m ai_onboard --invalid-option",
            "git commit --message",
        ],
        "styling": [
            "def bad_function():  \n    pass   \n",
            "import os\n\n\ndef func():\n\tpass\n",
        ],
        "import": [
            "import nonexistent_module\nprint('hello')",
            "from missing_package import something",
        ],
        "type": [
            "x = None\nprint(x.some_method())",
            "def func():\n    return undefined_variable",
        ],
    }

    if args.error_type:
        test_cases = {args.error_type: test_cases[args.error_type]}

    for error_type, cases in test_cases.items():
        print(f"\nTesting {error_type} prevention:")
        for i, test_case in enumerate(cases, 1):
            print(f"\nTest {i}: {repr(test_case[:50])}...")

            if error_type == "cli":
                result = prevention_system.prevent_cli_errors(test_case)
            else:
                result = prevention_system.prevent_code_errors(test_case)

            risk_icon = (
                "🔴"
                if result["risk_level"] == "high"
                else "🟡" if result["risk_level"] == "medium" else "🟢"
            )
            print(f"  Risk: {risk_icon} {result['risk_level'].upper()}")
            print(f"  Confidence: {result['confidence']:.2f}")

            if result["prevention_applied"]:
                print("  ✅ Preventions applied")
            else:
                print("  ⚠️ No preventions applied")
