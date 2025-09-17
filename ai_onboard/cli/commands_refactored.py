"""Refactored main CLI entry point for ai - onboard."""

import argparse
from pathlib import Path

from ..core.automatic_error_prevention import AutomaticErrorPrevention
from ..core.pattern_recognition_system import PatternRecognitionSystem
from ..core.syntax_validator import validate_python_syntax
from ..core.task_execution_gate import TaskExecutionGate
from ..core.tool_usage_tracker import get_tool_tracker
from ..core.universal_error_monitor import get_error_monitor

# from ..plugins import example_policy  # ensure example plugin registers on import
from .commands_aaol import add_aaol_commands, handle_aaol_commands
from .commands_advanced_test_reporting import (
    add_advanced_test_reporting_commands,
    handle_advanced_test_reporting_commands,
)
from .commands_ai_agent import add_ai_agent_commands, handle_ai_agent_commands
from .commands_ai_agent_collaboration import (
    add_ai_agent_collaboration_parser,
    handle_ai_agent_collaboration_commands,
)
from .commands_api import add_api_commands, handle_api_commands
from .commands_automatic_prevention import (
    add_automatic_prevention_commands,
    handle_automatic_prevention_commands,
)
from .commands_background_agents import (
    add_background_agent_commands,
    handle_background_agent_commands,
)
from .commands_capability_tracking import (
    add_capability_tracking_commands,
    handle_capability_tracking_commands,
)
from .commands_cleanup_safety import (
    add_cleanup_safety_commands,
    handle_cleanup_safety_commands,
)
from .commands_codebase_analysis import (
    add_codebase_analysis_commands,
    handle_codebase_analysis_commands,
)
from .commands_continuous_improvement import (
    add_continuous_improvement_parser,
    handle_continuous_improvement_commands,
)
from .commands_core import add_core_commands, handle_core_commands
from .commands_cursor import add_cursor_commands, handle_cursor_commands
from .commands_decision_pipeline import (
    add_decision_pipeline_commands,
    handle_decision_pipeline_commands,
)
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
from .commands_interrogate import add_interrogate_commands, handle_interrogate_commands
from .commands_kaizen import add_kaizen_commands, handle_kaizen_commands
from .commands_metrics import add_metrics_commands, handle_metrics_commands
from .commands_optimization_experiments import (
    add_optimization_experiment_commands,
    handle_optimization_experiment_commands,
)
from .commands_pattern_analysis import (
    add_pattern_analysis_commands,
    handle_pattern_analysis_commands,
)
from .commands_performance_trends import (
    add_performance_trend_commands,
    handle_performance_trend_commands,
)
from .commands_prompt import add_prompt_commands, handle_prompt_commands
from .commands_ui_enhanced import add_ui_enhanced_commands, handle_ui_enhanced_commands
from .commands_ux_enhancements import (
    add_ux_enhancement_commands,
    handle_ux_enhancement_commands,
)
from .ux_middleware import get_ux_middleware


def validate_and_execute_python(
    command: str, cwd: str = None, is_background: bool = False
) -> dict:
    """
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
    command: str, is_background: bool = False, root: Path = None
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
        command, [], cwd=str(root)
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

    # Add core commands
    add_core_commands(sub)

    # Add cleanup safety commands
    add_cleanup_safety_commands(sub)

    # Add interrogate commands
    add_interrogate_commands(sub)

    # Add prompt commands
    add_prompt_commands(sub)

    # Add AI agent commands
    add_ai_agent_commands(sub)

    # Add AAOL commands
    add_aaol_commands(sub)

    # Add enhanced vision commands
    add_enhanced_vision_parser(sub)

    # Add AI agent collaboration commands
    add_ai_agent_collaboration_parser(sub)

    # Add continuous improvement commands
    add_continuous_improvement_parser(sub)

    # Add metrics commands
    add_metrics_commands(sub)

    # Add Cursor AI integration commands
    add_cursor_commands(sub)

    # Add API server commands
    add_api_commands(sub)

    # Add enhanced conversation context commands
    add_enhanced_context_commands(sub)

    # Add advanced decision pipeline commands
    add_decision_pipeline_commands(sub)

    # Add Kaizen automation commands
    add_kaizen_commands(sub)

    # Add optimization experiment commands
    add_optimization_experiment_commands(sub)

    # Add pattern analysis commands
    add_pattern_analysis_commands(sub)

    # Add UI - enhanced commands
    add_ui_enhanced_commands(sub)

    # Add UX enhancement commands
    add_ux_enhancement_commands(sub)

    # Add capability tracking commands
    add_capability_tracking_commands(sub)

    # Add background agent commands
    add_background_agent_commands(sub)

    # Add enhanced testing commands
    add_enhanced_testing_commands(sub)

    # Add performance trend commands
    add_performance_trend_commands(sub)

    # Add advanced test reporting commands
    add_advanced_test_reporting_commands(sub)

    # Add automatic prevention commands
    add_automatic_prevention_commands(sub)

    # Add codebase analysis commands
    add_codebase_analysis_commands(sub)

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

    # Initialize UX middleware only for interactive commands
    if args.cmd not in ["status"]:
        ux_middleware = get_ux_middleware(root)
        user_id = "default"  # Could be extracted from environment or config
        ux_middleware.show_welcome_message(user_id)
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
            print(
                f"📋 WBS Auto-Update: {wbs_update_result['updated']} tasks integrated, {wbs_update_result['failed']} failed"
            )

        # Check if this is a critical operation requiring enhanced safety
        is_critical = is_critical_operation(args.cmd, vars(args))

        # Check command safety before execution
        pattern_system = PatternRecognitionSystem(root)
        prevention_system = AutomaticErrorPrevention(root, pattern_system)

        prevention_result = prevention_system.prevent_command_execution(
            args.cmd, vars(args), cwd=str(root)
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
                    print("✅ Operation cancelled by user.")
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

    # Handle AI agent commands with error monitoring
    if args.cmd == "ai - agent":
        with error_monitor.monitor_command_execution(
            "ai - agent", "foreground", "cli_session"
        ):
            if handle_ai_agent_commands(args, root):
                return

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

    # Handle unified metrics commands with error monitoring
    if args.cmd == "unified - metrics":
        with error_monitor.monitor_command_execution(
            "unified - metrics", "foreground", "cli_session"
        ):
            handle_metrics_commands(args, root)
            return

    # Handle Cursor AI integration commands with error monitoring
    if args.cmd == "cursor":
        with error_monitor.monitor_command_execution(
            "cursor", "foreground", "cli_session"
        ):
            handle_cursor_commands(args, root)
            return

    # Handle API server commands with error monitoring
    if args.cmd == "api":
        with error_monitor.monitor_command_execution(
            "api", "foreground", "cli_session"
        ):
            handle_api_commands(args, root)
            return

    # Handle enhanced conversation context commands with error monitoring
    if args.cmd == "enhanced - context":
        with error_monitor.monitor_command_execution(
            "enhanced - context", "foreground", "cli_session"
        ):
            handle_enhanced_context_commands(args, root)
            return

    # Handle advanced decision pipeline commands with error monitoring
    if args.cmd == "decision - pipeline":
        with error_monitor.monitor_command_execution(
            "decision - pipeline", "foreground", "cli_session"
        ):
            handle_decision_pipeline_commands(args, root)
            return

    # Handle Kaizen automation commands with error monitoring
    if args.cmd == "kaizen - auto":
        with error_monitor.monitor_command_execution(
            "kaizen - auto", "foreground", "cli_session"
        ):
            handle_kaizen_commands(args, root)
            return

    # Handle optimization experiment commands with error monitoring
    if args.cmd == "opt - experiments":
        with error_monitor.monitor_command_execution(
            "opt - experiments", "foreground", "cli_session"
        ):
            handle_optimization_experiment_commands(args, root)
            return

    # Handle pattern analysis commands with error monitoring
    if args.cmd == "patterns":
        with error_monitor.monitor_command_execution(
            "patterns", "foreground", "cli_session"
        ):
            tool_tracker = get_tool_tracker(root)
            tool_tracker.start_task_session("pattern_analysis")
            if handle_pattern_analysis_commands(args, root):
                session_summary = tool_tracker.end_task_session("completed")
                tool_tracker.display_tools_summary(session_summary)
                return

    # Handle UI - enhanced commands with error monitoring
    if args.cmd in [
        "help",
        "dashboard",
        "suggest",
        "discover",
        "config",
        "wizard",
        "status",
    ]:
        with error_monitor.monitor_command_execution(
            args.cmd, "foreground", "cli_session"
        ):
            handle_ui_enhanced_commands(args, root)
            return

    # Handle UX enhancement commands with error monitoring
    if args.cmd == "ux":
        with error_monitor.monitor_command_execution("ux", "foreground", "cli_session"):
            handle_ux_enhancement_commands(args, root)
            return

    # Handle capability tracking commands with error monitoring
    if args.cmd == "capability - tracking":
        with error_monitor.monitor_command_execution(
            "capability - tracking", "foreground", "cli_session"
        ):
            handle_capability_tracking_commands(args, root)
            return

    # Handle enhanced testing commands with error monitoring
    if args.cmd == "enhanced - testing":
        with error_monitor.monitor_command_execution(
            "enhanced - testing", "foreground", "cli_session"
        ):
            handle_enhanced_testing_commands(args, root)
            return

    # Handle performance trend commands with error monitoring
    if args.cmd == "perf - trends":
        with error_monitor.monitor_command_execution(
            "perf - trends", "foreground", "cli_session"
        ):
            handle_performance_trend_commands(args, root)
            return

    # Handle advanced test reporting commands with error monitoring
    if args.cmd == "test - reports":
        with error_monitor.monitor_command_execution(
            "test - reports", "foreground", "cli_session"
        ):
            handle_advanced_test_reporting_commands(args, root)
            return

    # Handle automatic prevention commands with error monitoring
    if args.cmd == "prevention":
        with error_monitor.monitor_command_execution(
            "prevention", "foreground", "cli_session"
        ):
            handle_automatic_prevention_commands(args, root)
            return

    # Handle codebase analysis commands with error monitoring
    if args.cmd == "codebase":
        tool_tracker = get_tool_tracker(root)
        session_id = tool_tracker.start_task_session(
            "codebase_analysis", "core_command"
        )

        try:
            with error_monitor.monitor_command_execution(
                "codebase", "foreground", "cli_session"
            ):
                result = handle_codebase_analysis_commands(args, root)
                session_summary = tool_tracker.end_task_session(
                    final_status="completed",
                    summary="Codebase analysis completed successfully",
                )
                tool_tracker.display_tools_summary(session_summary)
                return result
        except Exception as e:
            session_summary = tool_tracker.end_task_session(
                final_status="failed", summary=f"Codebase analysis failed: {str(e)}"
            )
            tool_tracker.display_tools_summary(session_summary)
            raise

    # Handle background agent commands with error monitoring
    if args.cmd == "background - agents":
        with error_monitor.monitor_command_execution(
            "background - agents", "foreground", "cli_session"
        ):
            handle_background_agent_commands(args, root)
            return

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
