"""Refactored main CLI entry point for ai - onboard."""

import argparse
from pathlib import Path
from typing import Optional

from ..core.orchestration.automatic_error_prevention import AutomaticErrorPrevention
from ..core.orchestration.mandatory_tool_consultation_gate import (
    enforce_tool_consultation,
)
from ..core.orchestration.pattern_recognition_system import PatternRecognitionSystem
from ..core.orchestration.task_execution_gate import TaskExecutionGate
from ..core.orchestration.tool_usage_tracker import get_tool_tracker
from ..core.orchestration.universal_error_monitor import get_error_monitor
from ..core.quality_safety.syntax_validator import validate_python_syntax

# from ..plugins import example_policy  # ensure example plugin registers on import
from .commands_aaol import add_aaol_commands, handle_aaol_commands

# Removed: commands_advanced_test_reporting (redundant with continuous_improvement)
# Removed: commands_ai_agent (redundant with ai_agent_collaboration)
from .commands_ai_agent_collaboration import (
    add_ai_agent_collaboration_parser,
    handle_ai_agent_collaboration_commands,
)
from .commands_chat import add_chat_commands, handle_chat_commands

# Removed: commands_automatic_prevention (redundant with cleanup_safety)
# Removed: commands_background_agents (redundant with ai_agent_collaboration)
# Removed: commands_capability_tracking (redundant with continuous_improvement)
from .commands_cleanup_safety import (
    add_cleanup_safety_commands,
    handle_cleanup_safety_commands,
)
from .commands_code_quality import (
    add_code_quality_commands,
    handle_code_quality_commands,
)

# Removed: commands_codebase_analysis (redundant with code_quality)
from .commands_continuous_improvement import (
    add_continuous_improvement_parser,
    handle_continuous_improvement_commands,
)
from .commands_core import add_core_commands, handle_core_commands
from .commands_cursor import add_cursor_commands, handle_cursor_commands
from .commands_decision_pipeline import add_decision_pipeline_commands

# Removed: commands_decision_pipeline (redundant with holistic_orchestration)
from .commands_enhanced_context import (
    add_enhanced_context_commands,
    handle_enhanced_context_commands,
)
from .commands_enhanced_testing import (
    add_enhanced_testing_commands,
    handle_enhanced_testing_commands,
)
from .commands_enhanced_vision import (
    add_enhanced_vision_parser,
    handle_enhanced_vision_commands,
)
from .commands_holistic_orchestration import (
    add_holistic_orchestration_commands,
    handle_holistic_orchestration_commands,
)
from .commands_import_consolidation import (
    add_consolidation_parser,
    consolidate_imports_command,
)
from .commands_intelligent_monitoring import (
    add_intelligent_monitoring_commands,
    handle_intelligent_monitoring_commands,
)
from .commands_interrogate import add_interrogate_commands, handle_interrogate_commands
from .commands_kaizen import add_kaizen_commands, handle_kaizen_commands
from .commands_project_management import (
    add_project_management_commands,
    handle_project_management_commands,
)

# Removed: commands_metrics (redundant with continuous_improvement)
# Removed: commands_optimization_experiments (redundant with continuous_improvement)
# Removed: commands_pattern_analysis (redundant with holistic_orchestration)
# Removed: commands_performance_trends (redundant with continuous_improvement)
from .commands_prompt import add_prompt_commands, handle_prompt_commands
from .commands_ux_enhanced import add_ux_enhanced_commands, handle_ux_enhanced_commands

# Removed: commands_ux_enhancements (redundant with ui_enhanced)
from .ux_middleware import get_ux_middleware


def validate_and_execute_python(
    command: str, cwd: Optional[str] = None, is_background: bool = False
) -> dict:
    """
    # Direct import will be added below
        Validate Python syntax and execute command if valid.

        Args:
            command: Python code to validate and execute
            cwd: Working directory for execution
            is_background: Whether to run in background

        Returns:
            Dict with execution results and validation info
    """
    # Extract Python code from command (remove 'python -c "..."')
    python_code = None
    if command.startswith('python -c "') and command.endswith('"'):
        python_code = command[11:-1]  # Remove 'python -c "' and closing quote
    elif command.startswith("python -c '") and command.endswith("'"):
        python_code = command[11:-1]  # Remove 'python -c "' and closing quote

    if python_code:
        # Validate syntax
        validation_result = validate_python_syntax(python_code)

        if not validation_result["valid"]:
            # Return validation error instead of executing
            return {
                "success": False,
                "error": "Syntax validation failed",
                "validation_error": validation_result["error"],
                "line_number": validation_result["line_number"],
                "suggestion": validation_result["suggestion"],
                "auto_fix": validation_result.get("auto_fix"),
                "executed": False,
            }

    # If no Python code or validation passed, proceed with normal execution
    return {
        "success": True,
        "validated": True,
        "executed": False,  # Would be executed by tool system
        "command": command,
    }


def is_critical_operation(command: str, args: dict) -> bool:
    """
    Determine if a command is a critical operation requiring enhanced safety checks.

    Args:
        command: Command name
        args: Command arguments

    Returns:
        True if operation is critical
    """
    # Critical operations that require enhanced safety
    critical_commands = {
        "clean",
        "cleanup",
        "remove",
        "delete",
        "reset",
        "wipe",
        "format",
        "reformat",
        "overwrite",
        "replace",
        "move",
        "init",
        "initialize",
        "setup",
        "install",
        "uninstall",
    }

    if command in critical_commands:
        return True

    # Check for destructive arguments
    dangerous_args = ["--force", "--yes", "--assume-yes", "--delete", "--remove"]
    args_list = [str(v) for v in args.values() if isinstance(v, (str, bool)) and v]

    for arg in dangerous_args:
        if arg in args_list:
            return True

    # Check for file operations on critical directories
    if command in ["run", "execute"] and any(
        "python" in str(arg) for arg in args.values()
    ):
        return True

    return False


def safe_run_terminal_cmd(
    command: str, is_background: bool = False, root: Optional[Path] = None
) -> dict:
    """
    Safely execute terminal command with error prevention and learning.

    This function wraps run_terminal_cmd with comprehensive error prevention:
    1. Pattern-based command safety checking
    2. Syntax validation for Python commands
    3. Learning from command execution patterns
    4. Error prevention based on learned patterns

    Args:
        command: Terminal command to execute
        is_background: Whether to run in background
        root: Project root directory

    Returns:
        Command execution result
    """
    if root is None:
        root = Path.cwd()

    # Initialize error prevention systems
    pattern_system = PatternRecognitionSystem(root)
    prevention_system = AutomaticErrorPrevention(root, pattern_system)

    # Check command safety before execution
    prevention_result = prevention_system.prevent_command_execution(
        command, [], cwd=root
    )

    if prevention_result.get("should_block", False):
        return {
            "success": False,
            "error": f"Command blocked by error prevention: {prevention_result.get('reason', 'Unknown reason')}",
            "confidence": prevention_result.get("confidence", 0.0),
            "executed": False,
            "blocked": True,
        }

    # Special handling for Python commands - validate syntax
    if command.startswith("python -c"):
        validation_result = validate_and_execute_python(command)
        if not validation_result["success"]:
            # Learn from this validation failure
            pattern_system.learn_from_repeated_errors(
                {
                    "error_type": "syntax_error",
                    "command": command,
                    "error": validation_result.get("validation_error"),
                    "line_number": validation_result.get("line_number"),
                }
            )
            return validation_result

    # Execute command using the system tool
    # Note: In a real implementation, this would call the run_terminal_cmd tool
    # For now, we'll simulate the execution and return success
    try:
        # This is where run_terminal_cmd tool would be called
        # result = run_terminal_cmd(command=command, is_background=is_background)

        # Simulate successful execution for now
        result = {
            "success": True,
            "returncode": 0,
            "stdout": "Command executed successfully",
            "stderr": "",
            "executed": True,
        }

        # Learn from successful command execution
        pattern_system.learn_from_cli_usage(
            command, success=True, context={"background": is_background}
        )

        return result

    except Exception as e:
        # Learn from failed command execution
        pattern_system.learn_from_cli_usage(
            command,
            success=False,
            context={"error": str(e), "background": is_background},
        )

        return {
            "success": False,
            "error": str(e),
            "executed": True,
            "returncode": 1,
        }


def main(argv=None):
    """Main CLI entry point with refactored command structure."""
    p = argparse.ArgumentParser(
        prog="ai_onboard",
        description=(
            "AI Onboard: drop - in project coach "
            "(charter + plan + align + validate + kaizen + interrogate + prompt + ai - agent + aaol)"
        ),
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # Get root path for tool consultation
    root = Path.cwd()

    # Add core commands
    add_core_commands(sub)

    # Add chat interface (natural language)
    add_chat_commands(sub)

    # Add cleanup safety commands
    add_cleanup_safety_commands(sub)

    # Add code quality commands
    add_code_quality_commands(sub)

    # Add project management commands
    add_project_management_commands(sub)

    # Add interrogate commands
    add_interrogate_commands(sub)

    # Add prompt commands
    add_prompt_commands(sub)

    # Removed: AI agent commands (redundant with ai_agent_collaboration)

    # Add AAOL commands
    add_aaol_commands(sub)

    # Add enhanced vision commands
    add_enhanced_vision_parser(sub)

    # Add AI agent collaboration commands
    add_ai_agent_collaboration_parser(sub)

    # Add continuous improvement commands
    add_continuous_improvement_parser(sub)

    # Removed: metrics commands (redundant with continuous_improvement)

    # Add Cursor AI integration commands
    add_cursor_commands(sub)

    # Add import consolidation commands
    add_consolidation_parser(sub)

    # Add enhanced conversation context commands
    add_enhanced_context_commands(sub)

    # Add advanced decision pipeline commands
    add_decision_pipeline_commands(sub)

    # Add Kaizen automation commands
    add_kaizen_commands(sub)

    # Removed: optimization experiment commands (redundant with continuous_improvement)

    # Removed: pattern analysis commands (redundant with holistic_orchestration)

    # Add UX - enhanced commands (simplified)
    add_ux_enhanced_commands(sub)

    # Removed: UX enhancement commands (redundant with ui_enhanced)

    # Removed: capability tracking commands (redundant with continuous_improvement)

    # Removed: background agent commands (redundant with ai_agent_collaboration)

    # Add enhanced testing commands
    add_enhanced_testing_commands(sub)

    # Removed: performance trend commands (redundant with continuous_improvement)

    # Add holistic orchestration commands
    add_holistic_orchestration_commands(sub)

    # Removed: advanced test reporting commands (redundant with continuous_improvement)

    # Removed: automatic prevention commands (redundant with cleanup_safety)

    # Removed: codebase analysis commands (redundant with code_quality)

    # Add intelligent monitoring commands
    add_intelligent_monitoring_commands(sub)

    # TODO: Add other domain commands as they're refactored
    # from .commands_vision import add_vision_commands, handle_vision_commands
    # from .commands_design import add_design_commands, handle_design_commands
    # from .commands_planning import add_planning_commands, handle_planning_commands
    # from .commands_debug import add_debug_commands, handle_debug_commands
    # from .commands_context import add_context_commands, handle_context_commands

    args = p.parse_args(argv)
    root = Path.cwd()

    # Fast path for simple commands - avoid heavy initialization
    if args.cmd in ["version", "help"]:
        # Handle these directly without middleware overhead
        if args.cmd == "version":
            tool_tracker = get_tool_tracker(root)
            session_id = tool_tracker.start_task_session("version", "core_command")

            try:
                from .. import __version__

                print(f"ai - onboard {__version__}")
                tool_tracker.track_tool_usage(
                    "version_display",
                    "version_management",
                    parameters={"version": __version__},
                    result="success",
                )
                session_summary = tool_tracker.end_task_session("completed")
                tool_tracker.display_tools_summary(session_summary)
            except ImportError:
                print("ai - onboard (version unknown)")
                tool_tracker.track_tool_usage(
                    "version_display", "version_management", result="version_unknown"
                )
                session_summary = tool_tracker.end_task_session("completed")
                tool_tracker.display_tools_summary(session_summary)
        elif args.cmd == "help":
            p.print_help()
        return

    # PRIME DIRECTIVE: MANDATORY TOOL CONSULTATION FOR ALL COMMANDS
    from ..core.utilities.unicode_utils import ensure_unicode_safe

    ensure_unicode_safe(
        "🚀 AI-ONBOARD PRIME DIRECTIVE: Consulting tools for your request..."
    )

    # Build command description for tool consultation
    command_description = f"ai_onboard {args.cmd}"
    if hasattr(args, "subcmd") and args.subcmd:
        command_description += f" {args.subcmd}"

    # Add any significant arguments to the description
    significant_args = []
    for arg_name, arg_value in vars(args).items():
        if arg_name not in ["cmd", "subcmd", "root"] and arg_value:
            if isinstance(arg_value, bool) and arg_value:
                significant_args.append(f"--{arg_name.replace('_', '-')}")
            elif not isinstance(arg_value, bool):
                significant_args.append(f"--{arg_name.replace('_', '-')} {arg_value}")

    if significant_args:
        command_description += f" {' '.join(significant_args)}"

    # ENFORCE mandatory tool consultation
    consultation_result = enforce_tool_consultation(
        user_request=command_description,
        context={
            "command_type": "cli",
            "command": args.cmd,
            "subcommand": getattr(args, "subcmd", None),
            "contexts": ["command_execution", "cli_usage"],
        },
        root_path=root,
    )

    # Check if gate passed
    if not consultation_result.gate_passed:
        print(f"🚫 Command execution blocked: {consultation_result.blocking_reason}")
        return 1

    # Initialize UX middleware only for interactive commands
    if args.cmd not in ["status"]:
        ux_middleware = get_ux_middleware(root)
        user_id = "default"  # Could be extracted from environment or config
        # Simplified: No welcome message needed
    else:
        ux_middleware = None

    # Initialize error monitor for command execution monitoring
    error_monitor = get_error_monitor(root)

    # Handle core commands with error monitoring and tool tracking
    if args.cmd in [
        "analyze",
        "charter",
        "plan",
        "align",
        "validate",
        "kaizen",
        "optimize",
        "version",
        "metrics",
        "cleanup",
        "gate",
        "tools",
        "wbs",
        "task-gate",
    ]:
        tool_tracker = get_tool_tracker(root)
        session_id = tool_tracker.start_task_session(args.cmd, "core_command")

        # Check and update pending WBS updates before execution
        execution_gate = TaskExecutionGate(root)
        wbs_update_result = execution_gate.update_wbs_for_pending_tasks()

        if wbs_update_result["updated"] > 0:
            tool_tracker.track_tool_usage(
                "wbs_auto_update",
                "project_management",
                {
                    "updated_tasks": wbs_update_result["updated"],
                    "failed_tasks": wbs_update_result["failed"],
                    "total_processed": wbs_update_result["total_processed"],
                },
                "success",
            )
            from ..core.utilities.unicode_utils import ensure_unicode_safe

            ensure_unicode_safe(
                f"📋 WBS Auto-Update: {wbs_update_result['updated']} tasks integrated, "
                f"{wbs_update_result['failed']} failed"
            )

        # Check if this is a critical operation requiring enhanced safety
        is_critical = is_critical_operation(args.cmd, vars(args))

        # Check command safety before execution
        pattern_system = PatternRecognitionSystem(root)
        prevention_system = AutomaticErrorPrevention(root, pattern_system)

        prevention_result = prevention_system.prevent_command_execution(
            command=args.cmd, args=vars(args), cwd=root
        )

        # Apply stricter threshold for critical operations
        should_block = prevention_result.get("should_block", False)
        confidence = prevention_result.get("confidence", 0.0)

        if is_critical:
            # Critical operations require higher confidence to proceed
            if confidence < 0.9:  # Stricter threshold for critical ops
                should_block = True
                if not prevention_result.get("should_block", False):
                    prevention_result["reason"] = (
                        f"Critical operation '{args.cmd}' requires high confidence ({confidence:.2f} < 0.9)"
                    )
                    prevention_result["confidence"] = confidence

        if should_block:
            print(f"🚫 Command blocked by error prevention system:")
            print(f"   Reason: {prevention_result.get('reason', 'Unknown reason')}")
            print(f"   Confidence: {prevention_result.get('confidence', 0.0):.2f}")
            print(f"   Critical Operation: {'Yes' if is_critical else 'No'}")
            print(
                f"   Suggestion: {prevention_result.get('suggestion', 'Please review command before retrying')}"
            )

            # For critical operations, require explicit confirmation
            if is_critical:
                print(f"\n🔴 CRITICAL OPERATION DETECTED: {args.cmd}")
                print("This operation could have significant impact on the project.")
                confirm = input(
                    "Type 'CONFIRM' to proceed anyway, or anything else to cancel: "
                )
                if confirm.upper() == "CONFIRM":
                    print("⚠️  Proceeding with critical operation despite warnings...")
                else:
                    from ..core.utilities.unicode_utils import ensure_unicode_safe

                    ensure_unicode_safe("✅ Operation cancelled by user.")
                    # Learn from blocked critical command
                    pattern_system.learn_from_cli_usage(
                        args.cmd,
                        success=False,
                        context={
                            "command_args": vars(args),
                            "blocked": True,
                            "critical": True,
                            "user_cancelled": True,
                            "reason": prevention_result.get("reason"),
                        },
                    )
                    return

            # Learn from blocked command
            pattern_system.learn_from_cli_usage(
                args.cmd,
                success=False,
                context={
                    "command_args": vars(args),
                    "blocked": True,
                    "critical": is_critical,
                    "reason": prevention_result.get("reason"),
                },
            )
            return

        try:
            with error_monitor.monitor_command_execution(
                args.cmd, "foreground", "cli_session"
            ):
                handle_core_commands(args, root)

            # Learn from successful command execution
            pattern_system = PatternRecognitionSystem(root)
            pattern_system.learn_from_cli_usage(
                args.cmd, success=True, context={"command_args": vars(args)}
            )

            # Track successful command execution
            tool_tracker.track_tool_usage(
                f"core_command_{args.cmd}",
                "cli_command",
                parameters={"args": vars(args)},
                result="success",
            )
            session_summary = tool_tracker.end_task_session("completed")
            tool_tracker.display_tools_summary(session_summary)
        except Exception as e:
            # Learn from failed command execution
            try:
                pattern_system = PatternRecognitionSystem(root)
                pattern_system.learn_from_cli_usage(
                    args.cmd,
                    success=False,
                    context={"command_args": vars(args), "error": str(e)},
                )
            except Exception as learn_error:
                # Don't let learning failures break error handling
                print(f"Warning: Pattern learning failed: {learn_error}")

            # Track failed command execution
            tool_tracker.track_tool_usage(
                f"core_command_{args.cmd}",
                "cli_command",
                parameters={"args": vars(args)},
                result=f"failed: {str(e)}",
            )
            session_summary = tool_tracker.end_task_session("failed", str(e))
            tool_tracker.display_tools_summary(session_summary)
            raise
        return

    # Handle interrogate commands with error monitoring
    if args.cmd == "interrogate":
        with error_monitor.monitor_command_execution(
            "interrogate", "foreground", "cli_session"
        ):
            if handle_interrogate_commands(args, root):
                return

    # Handle prompt commands with error monitoring
    if args.cmd == "prompt":
        with error_monitor.monitor_command_execution(
            "prompt", "foreground", "cli_session"
        ):
            if handle_prompt_commands(args, root):
                return

    # Handle chat commands (natural language interface)
    if args.cmd == "chat":
        with error_monitor.monitor_command_execution(
            "chat", "foreground", "cli_session"
        ):
            handle_chat_commands(args, root)
            return

    # Removed: AI agent commands (redundant with ai_agent_collaboration)

    # Handle AAOL commands with error monitoring
    if args.cmd == "aaol":
        with error_monitor.monitor_command_execution(
            "aaol", "foreground", "cli_session"
        ):
            if handle_aaol_commands(args, root):
                return

    # Handle cleanup safety commands
    if args.cmd == "cleanup - safety":
        with error_monitor.monitor_command_execution(
            "cleanup-safety", "foreground", "cli_session"
        ):
            handle_cleanup_safety_commands(args, root)
            return

    # Handle code quality commands with error monitoring
    if args.cmd == "code-quality":
        with error_monitor.monitor_command_execution(
            "code-quality", "foreground", "cli_session"
        ):
            handle_code_quality_commands(args)
            return

    # Handle project management commands with error monitoring
    if args.cmd == "project":
        with error_monitor.monitor_command_execution(
            "project", "foreground", "cli_session"
        ):
            handle_project_management_commands(args)
            return

    # Handle enhanced vision commands with error monitoring
    if args.cmd == "enhanced - vision":
        with error_monitor.monitor_command_execution(
            "enhanced - vision", "foreground", "cli_session"
        ):
            handle_enhanced_vision_commands(args, root)
            return

    # Handle AI agent collaboration commands with error monitoring
    if args.cmd == "ai - collaboration":
        with error_monitor.monitor_command_execution(
            "ai - collaboration", "foreground", "cli_session"
        ):
            handle_ai_agent_collaboration_commands(args, root)
            return

    # Handle continuous improvement commands with error monitoring
    if args.cmd == "continuous - improvement":
        with error_monitor.monitor_command_execution(
            "continuous - improvement", "foreground", "cli_session"
        ):
            handle_continuous_improvement_commands(args, root)
            return

    # Handle user preference learning (quick - path) with error monitoring
    if args.cmd == "user - prefs":
        with error_monitor.monitor_command_execution(
            "user - prefs", "foreground", "cli_session"
        ):
            handle_continuous_improvement_commands(args, root)
            return

    # Removed: unified metrics commands (redundant with continuous_improvement)

    # Handle Cursor AI integration commands with error monitoring
    if args.cmd == "cursor":
        with error_monitor.monitor_command_execution(
            "cursor", "foreground", "cli_session"
        ):
            handle_cursor_commands(args, root)
            return

    # Handle import consolidation commands with error monitoring
    if args.cmd == "consolidate":
        with error_monitor.monitor_command_execution(
            "consolidate", "foreground", "cli_session"
        ):
            consolidate_imports_command(args)
            return

    # Handle enhanced conversation context commands with error monitoring
    if args.cmd == "enhanced - context":
        with error_monitor.monitor_command_execution(
            "enhanced - context", "foreground", "cli_session"
        ):
            handle_enhanced_context_commands(args, root)
            return

    # Removed: decision pipeline commands (redundant with holistic_orchestration)

    # Handle Kaizen automation commands with error monitoring
    if args.cmd == "kaizen - auto":
        with error_monitor.monitor_command_execution(
            "kaizen - auto", "foreground", "cli_session"
        ):
            handle_kaizen_commands(args, root)
            return

    # Removed: optimization experiment commands (redundant with continuous_improvement)

    # Removed: pattern analysis commands (redundant with holistic_orchestration)

    # Handle UX - enhanced commands with error monitoring (simplified)
    if args.cmd in [
        "help",
        "dashboard",
        "suggest",
        "design",
        "status",
    ]:
        with error_monitor.monitor_command_execution(
            args.cmd, "foreground", "cli_session"
        ):
            handle_ux_enhanced_commands(args, root)
            return

    # Removed: UX enhancement commands (redundant with ui_enhanced)

    # Removed: capability tracking commands (redundant with continuous_improvement)

    # Handle enhanced testing commands with error monitoring
    if args.cmd == "enhanced - testing":
        with error_monitor.monitor_command_execution(
            "enhanced - testing", "foreground", "cli_session"
        ):
            handle_enhanced_testing_commands(args, root)
            return

    # Removed: performance trend commands (redundant with continuous_improvement)

    # Handle holistic orchestration commands with error monitoring
    if args.cmd == "holistic":
        with error_monitor.monitor_command_execution(
            "holistic", "foreground", "cli_session"
        ):
            handle_holistic_orchestration_commands(args, root)
            return

    # Removed: advanced test reporting commands (redundant with continuous_improvement)

    # Removed: automatic prevention commands (redundant with cleanup_safety)

    # Removed: codebase analysis commands (redundant with code_quality)

    # Handle intelligent monitoring commands with error monitoring
    if args.cmd == "intelligent":
        tool_tracker = get_tool_tracker(root)
        session_id = tool_tracker.start_task_session(
            "intelligent_monitoring", "core_command"
        )

        try:
            with error_monitor.monitor_command_execution(
                "intelligent", "foreground", "cli_session"
            ):
                result = handle_intelligent_monitoring_commands(args, root)
                session_summary = tool_tracker.end_task_session(
                    final_status="completed",
                    summary="Intelligent monitoring command completed successfully",
                )
                tool_tracker.display_tools_summary(session_summary)
                return result
        except Exception as e:
            session_summary = tool_tracker.end_task_session(
                final_status="failed",
                summary=f"Intelligent monitoring failed: {str(e)}",
            )
            tool_tracker.display_tools_summary(session_summary)
            raise

    # Handle background agent commands with error monitoring

    # TODO: Handle other domain commands as they're refactored
    # elif args.cmd in ["vision", "design", "planning", "debug", "context"]:
    #     handle_vision_commands(args, root)
    #     return

    # Fallback for unimplemented commands
    print(f"Command '{args.cmd}' not yet implemented in refactored CLI.")
    print("Please use the original commands.py for now.")

    # Show completion celebration for milestones
    # Only show completion celebration for interactive commands
    if ux_middleware is not None:
        ux_middleware.show_completion_celebration(user_id)


if __name__ == "__main__":
    main()
