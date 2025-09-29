"""
CLI commands for Prime Directive Cascade system.

This module provides CLI commands to generate, update, and manage
the Prime Directive Cascade files that control AI agent behavior.
"""

import argparse
from pathlib import Path

from ..core.project_management.directive_generator import get_directive_generator


def add_directive_commands(subparsers):
    """Add directive management commands to CLI."""

    # Main directive command
    directive_parser = subparsers.add_parser(
        "directives",
        help="Manage Prime Directive Cascade system",
        description="Generate and manage AI agent directive files",
    )

    directive_subparsers = directive_parser.add_subparsers(
        dest="directive_cmd", help="Directive management commands"
    )

    # Generate directives
    generate_parser = directive_subparsers.add_parser(
        "generate",
        help="Generate all directive files",
        description="Generate all Prime Directive Cascade files with current "
        "system state",
    )
    generate_parser.add_argument(
        "--force", action="store_true", help="Force regeneration even if files exist"
    )
    generate_parser.set_defaults(func=_handle_generate_directives)

    # Update directives
    update_parser = directive_subparsers.add_parser(
        "update",
        help="Update directive files with current system state",
        description="Update existing directive files with current system data",
    )
    update_parser.set_defaults(func=_handle_update_directives)

    # List directives
    list_parser = directive_subparsers.add_parser(
        "list",
        help="List all directive files",
        description="List all directive files in the cascade",
    )
    list_parser.set_defaults(func=_handle_list_directives)

    # Show directive
    show_parser = directive_subparsers.add_parser(
        "show",
        help="Show content of a specific directive file",
        description="Display the content of a specific directive file",
    )
    show_parser.add_argument(
        "directive_name",
        help="Name of the directive file to show (e.g., 'prime', 'persona', "
        "'integration')",
    )
    show_parser.set_defaults(func=_handle_show_directive)

    # Test cascade
    test_parser = directive_subparsers.add_parser(
        "test",
        help="Test the directive cascade",
        description="Test the directive cascade system",
    )
    test_parser.add_argument(
        "--simulate",
        action="store_true",
        help="Simulate AI agent following the cascade",
    )
    test_parser.set_defaults(func=_handle_test_cascade)

    # Master prompt
    master_parser = directive_subparsers.add_parser(
        "master",
        help="Show the master prompt",
        description="Display the master prompt that initiates the cascade",
    )
    master_parser.set_defaults(func=_handle_master_prompt)


def _handle_generate_directives(args: argparse.Namespace, root: Path) -> None:
    """Handle generate directives command."""

    print("🚀 GENERATING PRIME DIRECTIVE CASCADE")
    print("=" * 50)

    try:
        generator = get_directive_generator(root)

        # Check if files exist
        directives_dir = root / ".ai-directives"
        if directives_dir.exists() and not args.force:
            existing_files = list(directives_dir.glob("*.md"))
            if existing_files:
                print(f"⚠️  Found {len(existing_files)} existing directive files")
                print("   Use --force to regenerate all files")
                return

        # Generate all directives
        results = generator.generate_all_directives()

        print(f"✅ Generated {len(results)} directive files:")
        for directive_name in results.keys():
            print(f"   📄 {directive_name.upper()}.md")

        print()
        print("🎯 DIRECTIVE CASCADE READY")
        print("   To use: Ask any AI agent to read the .ai-directives/ directory")
        print("   Master prompt: .ai-directives/MASTER_PROMPT.md")

    except Exception as e:
        print(f"❌ Error generating directives: {e}")


def _handle_update_directives(args: argparse.Namespace, root: Path) -> None:
    """Handle update directives command."""

    print("🔄 UPDATING PRIME DIRECTIVE CASCADE")
    print("=" * 50)

    try:
        generator = get_directive_generator(root)

        # Update directives with current system state
        results = generator.update_directives()

        print(f"✅ Updated {results['updated']} directive files:")
        for file_name in results["files"]:
            print(f"   📄 {file_name.upper()}.md")

        print()
        print("🎯 DIRECTIVE CASCADE UPDATED")
        print("   All directives now reflect current system state")

    except Exception as e:
        print(f"❌ Error updating directives: {e}")


def _handle_list_directives(args: argparse.Namespace, root: Path) -> None:
    """Handle list directives command."""

    print("📋 PRIME DIRECTIVE CASCADE FILES")
    print("=" * 50)

    directives_dir = root / ".ai-directives"

    if not directives_dir.exists():
        print("❌ No directive files found")
        print("   Run: python -m ai_onboard directives generate")
        return

    # List all directive files
    directive_files = sorted(directives_dir.glob("*.md"))

    if not directive_files:
        print("❌ No directive files found")
        return

    print(f"Found {len(directive_files)} directive files:")
    print()

    for file_path in directive_files:
        file_name = file_path.name
        file_size = file_path.stat().st_size

        # Determine file type
        if file_name == "MASTER_PROMPT.md":
            file_type = "🚀 Master Prompt"
        elif file_name.startswith("00_"):
            file_type = "🚨 Prime Directive"
        elif file_name.startswith("01_"):
            file_type = "🤖 AI Agent Persona"
        elif file_name.startswith("02_"):
            file_type = "🔧 System Integration"
        elif file_name.startswith("03_"):
            file_type = "🎯 Vision Alignment"
        elif file_name.startswith("04_"):
            file_type = "🛠️ Tool Consultation"
        elif file_name.startswith("05_"):
            file_type = "🧠 Pattern Application"
        elif file_name.startswith("06_"):
            file_type = "🛡️ Safety Checks"
        elif file_name.startswith("07_"):
            file_type = "✅ Confirmation"
        else:
            file_type = "📄 Directive File"

        print(f"   {file_type}: {file_name} ({file_size} bytes)")

    print()
    print("🎯 CASCADE WORKFLOW:")
    print("   1. Read MASTER_PROMPT.md to start")
    print("   2. Follow numerical sequence (00_ → 01_ → 02_ → ...)")
    print("   3. Confirm compliance with each directive")
    print("   4. Apply directives to all work")


def _handle_show_directive(args: argparse.Namespace, root: Path) -> None:
    """Handle show directive command."""

    directive_name = args.directive_name.lower()

    print(f"📄 SHOWING DIRECTIVE: {directive_name.upper()}")
    print("=" * 50)

    directives_dir = root / ".ai-directives"

    if not directives_dir.exists():
        print("❌ No directive files found")
        print("   Run: python -m ai_onboard directives generate")
        return

    # Map directive names to file names
    directive_mapping = {
        "prime": "00_PRIME_DIRECTIVE.md",
        "persona": "01_AI_AGENT_PERSONA.md",
        "integration": "02_SYSTEM_INTEGRATION.md",
        "vision": "03_VISION_ALIGNMENT.md",
        "tools": "04_TOOL_CONSULTATION.md",
        "patterns": "05_PATTERN_APPLICATION.md",
        "safety": "06_SAFETY_CHECKS.md",
        "confirmation": "07_CONFIRMATION.md",
        "master": "MASTER_PROMPT.md",
    }

    file_name = directive_mapping.get(directive_name)
    if not file_name:
        print(f"❌ Unknown directive: {directive_name}")
        print("   Available directives: " + ", ".join(directive_mapping.keys()))
        return

    file_path = directives_dir / file_name

    if not file_path.exists():
        print(f"❌ Directive file not found: {file_name}")
        print("   Run: python -m ai_onboard directives generate")
        return

    # Show file content
    content = file_path.read_text(encoding="utf-8")
    print(content)


def _handle_test_cascade(args: argparse.Namespace, root: Path) -> None:
    """Handle test cascade command."""

    print("🧪 TESTING PRIME DIRECTIVE CASCADE")
    print("=" * 50)

    directives_dir = root / ".ai-directives"

    if not directives_dir.exists():
        print("❌ No directive files found")
        print("   Run: python -m ai_onboard directives generate")
        return

    # Test cascade structure
    required_files = [
        "MASTER_PROMPT.md",
        "00_PRIME_DIRECTIVE.md",
        "01_AI_AGENT_PERSONA.md",
        "02_SYSTEM_INTEGRATION.md",
        "03_VISION_ALIGNMENT.md",
        "04_TOOL_CONSULTATION.md",
        "05_PATTERN_APPLICATION.md",
        "06_SAFETY_CHECKS.md",
        "07_CONFIRMATION.md",
    ]

    print("🔍 Checking cascade structure...")

    missing_files = []
    for file_name in required_files:
        file_path = directives_dir / file_name
        if file_path.exists():
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name} (missing)")
            missing_files.append(file_name)

    if missing_files:
        print()
        print(f"❌ Cascade incomplete: {len(missing_files)} files missing")
        print("   Run: python -m ai_onboard directives generate")
        return

    print()
    print("✅ Cascade structure is complete")

    if args.simulate:
        print()
        print("🤖 SIMULATING AI AGENT CASCADE FOLLOWING")
        print("=" * 50)

        # Simulate AI agent following the cascade
        print("1. 🚀 Reading MASTER_PROMPT.md...")
        print("   → Agent: 'I will read the .ai-directives/ directory'")
        print()

        print("2. 🚨 Reading 00_PRIME_DIRECTIVE.md...")
        print("   → Agent: 'I must read all directive files in order'")
        print()

        print("3. 🤖 Reading 01_AI_AGENT_PERSONA.md...")
        print("   → Agent: 'IDENTITY_ASSUMED - I am a bound development agent'")
        print()

        print("4. 🔧 Reading 02_SYSTEM_INTEGRATION.md...")
        print("   → Agent: 'SYSTEM_INTEGRATED - I will use ai-onboard tools'")
        print()

        print("5. 🎯 Reading 03_VISION_ALIGNMENT.md...")
        print("   → Agent: 'VISION_ALIGNED - I will follow project vision'")
        print()

        print("6. 🛠️ Reading 04_TOOL_CONSULTATION.md...")
        print("   → Agent: 'TOOLS_CONSULTED - I will consult system tools'")
        print()

        print("7. 🧠 Reading 05_PATTERN_APPLICATION.md...")
        print("   → Agent: 'PATTERNS_APPLIED - I will apply learned patterns'")
        print()

        print("8. 🛡️ Reading 06_SAFETY_CHECKS.md...")
        print("   → Agent: 'SAFETY_VALIDATED - I will perform safety checks'")
        print()

        print("9. ✅ Reading 07_CONFIRMATION.md...")
        print("   → Agent: 'ALL_DIRECTIVES_CONFIRMED - I am ready to work'")
        print()

        print("🎯 CASCADE SIMULATION COMPLETE")
        print("   The agent should now follow the established workflow")

    print()
    print("🎯 CASCADE TEST COMPLETE")
    print("   The Prime Directive Cascade is ready for use")


def _handle_directive_command(args: argparse.Namespace, root: Path) -> None:
    """Handle directive command routing."""

    directive_cmd = getattr(args, "directive_cmd", None)
    if not directive_cmd:
        print("❌ No directive command specified")
        print("   Available commands: generate, update, list, show, test, master")
        return

    # Route to appropriate handler
    if directive_cmd == "generate":
        _handle_generate_directives(args, root)
    elif directive_cmd == "update":
        _handle_update_directives(args, root)
    elif directive_cmd == "list":
        _handle_list_directives(args, root)
    elif directive_cmd == "show":
        _handle_show_directive(args, root)
    elif directive_cmd == "test":
        _handle_test_cascade(args, root)
    elif directive_cmd == "master":
        _handle_master_prompt(args, root)
    else:
        print(f"❌ Unknown directive command: {directive_cmd}")
        print("   Available commands: generate, update, list, show, test, master")


def _handle_master_prompt(args: argparse.Namespace, root: Path) -> None:
    """Handle master prompt command."""

    print("🚀 MASTER PROMPT - PRIME DIRECTIVE CASCADE INITIATOR")
    print("=" * 50)

    directives_dir = root / ".ai-directives"
    master_file = directives_dir / "MASTER_PROMPT.md"

    if not master_file.exists():
        print("❌ Master prompt file not found")
        print("   Run: python -m ai_onboard directives generate")
        return

    # Show master prompt content
    content = master_file.read_text(encoding="utf-8")
    print(content)

    print()
    print("🎯 USAGE INSTRUCTIONS:")
    print("   1. Copy the master prompt above")
    print("   2. Send it to any AI agent (Grok, ChatGPT, etc.)")
    print("   3. The agent will be forced to follow the cascade")
    print("   4. The agent will use the ai-onboard system tools")
    print("   5. The agent will apply learned patterns and safety checks")
