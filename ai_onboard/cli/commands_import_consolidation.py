#!/usr/bin/env python3
"""
Import Consolidation CLI Commands - Integration with existing CLI system.

This module provides CLI commands for the import consolidation system,
integrating with the existing ai_onboard CLI framework.
"""
from pathlib import Path

from ai_onboard.core.common_imports import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Add scripts directory to path
scripts_dir = project_root / "scripts"
sys.path.insert(0, str(scripts_dir))

from analysis.validate_import_equivalence import ImportEquivalenceValidator
from maintenance.monitor_import_changes import ImportChangeMonitor
from migration.import_consolidation_migrator import ImportConsolidationMigrator
from migration.integrated_import_consolidation import IntegratedImportConsolidation

from ai_onboard.core.utils import read_json, write_json


def consolidate_imports_command(args):
    """Main command for import consolidation."""
    print("🔧 Import Consolidation System")
    print("=" * 50)

    # Initialize the integrated system
    root = Path.cwd()
    consolidation = IntegratedImportConsolidation(root)

    if args.subcommand == "analyze":
        _handle_analyze_command(consolidation, args)
    elif args.subcommand == "plan":
        _handle_plan_command(consolidation, args)
    elif args.subcommand == "execute":
        _handle_execute_command(consolidation, args)
    elif args.subcommand == "monitor":
        _handle_monitor_command(consolidation, args)
    elif args.subcommand == "validate":
        _handle_validate_command(consolidation, args)
    elif args.subcommand == "status":
        _handle_status_command(consolidation, args)
    elif args.subcommand == "rollback":
        _handle_rollback_command(consolidation, args)
    else:
        print("❌ Unknown subcommand. Use --help for available options.")


def _handle_analyze_command(consolidation: IntegratedImportConsolidation, args):
    """Handle analyze subcommand."""
    print("🔍 Analyzing consolidation opportunities...")

    migrator = consolidation.migrator
    analysis = migrator.analyze_consolidation_opportunities()

    print(f"\n📊 Analysis Results:")
    print(f"  Total files: {analysis['total_files']}")
    print(f"  Total imports: {analysis['total_imports']}")
    print(f"  Consolidation opportunities: {len(analysis['consolidation_potential'])}")

    # Show per-target summary with unique files vs occurrences
    if analysis.get("consolidation_potential"):
        print(f"\n📁 Target Summaries:")
        for name, meta in analysis["consolidation_potential"].items():
            files_affected = meta.get("files_affected", 0)
            occurrence_count = meta.get("occurrence_count", meta.get("import_count", 0))
            percent = meta.get("percent_of_codebase", 0.0)
            print(
                f"  {name}: {files_affected} unique files ({percent:.1f}%), "
                f"{occurrence_count} total occurrences, "
                f"~{int(meta.get('potential_reduction', 0))} reduction potential"
            )

    if analysis["recommendations"]:
        print(f"\n💡 Recommendations:")
        for rec in analysis["recommendations"]:
            print(f"  • {rec}")

    # Save analysis results
    analysis_file = consolidation.root / ".ai_onboard" / "consolidation_analysis.json"
    write_json(analysis_file, analysis)
    print(f"\n💾 Analysis saved to: {analysis_file}")


def _handle_plan_command(consolidation: IntegratedImportConsolidation, args):
    """Handle plan subcommand."""
    if not args.targets:
        print("❌ Error: Must specify consolidation targets")
        return

    print(f"📋 Creating migration plan for targets: {', '.join(args.targets)}")

    try:
        migrator = consolidation.migrator
        plan = migrator.create_migration_plan(args.targets)

        print(f"\n✅ Migration plan created:")
        print(f"  Plan ID: {plan.backup_id}")
        print(f"  Targets: {', '.join(args.targets)}")
        print(f"  Risk level: {plan.risk_assessment['overall_risk']}")
        print(f"  Estimated duration: {plan.estimated_duration} minutes")

        # Save plan (already saved by migrator)
        plan_file = consolidation.root / ".ai_onboard" / "migration_plan.json"
        print(f"📄 Plan saved to: {plan_file}")

    except Exception as e:
        print(f"❌ Error creating plan: {e}")


def _handle_execute_command(consolidation: IntegratedImportConsolidation, args):
    """Handle execute subcommand."""
    print(f"⚡ Executing import consolidation...")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"  Auto-approve: {args.auto_approve}")

    if not args.targets:
        print("❌ Error: Must specify consolidation targets")
        return

    try:
        result = consolidation.run_complete_workflow(
            targets=args.targets, dry_run=args.dry_run, auto_approve=args.auto_approve
        )

        print(f"\n🏁 Workflow completed:")
        print(f"  Status: {result['status']}")
        print(f"  Duration: {result.get('duration_seconds', 0):.1f} seconds")

        if result.get("error"):
            print(f"  Error: {result['error']}")

        # Show final report
        if result.get("final_report"):
            report = result["final_report"]
            print(f"\n📊 Final Report:")
            print(
                f"  Successful steps: {report.get('successful_steps',
                    0)}/{report.get('total_steps', 0)}"
            )
            print(f"  Success rate: {report.get('success_rate', 0):.1%}")

    except Exception as e:
        print(f"❌ Error executing workflow: {e}")


def _handle_monitor_command(consolidation: IntegratedImportConsolidation, args):
    """Handle monitor subcommand."""
    monitor = consolidation.monitor

    if args.action == "start":
        if not args.targets:
            print("❌ Error: Must specify targets to monitor")
            return

        monitor.start_monitoring(args.targets)
        print(f"✅ Started monitoring for: {', '.join(args.targets)}")

    elif args.action == "stop":
        monitor.stop_monitoring()
        print("✅ Stopped monitoring")

    elif args.action == "status":
        status = monitor.get_current_status()
        print("📊 Monitoring Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

    elif args.action == "progress":
        if not args.target:
            print("❌ Error: Must specify target for progress")
            return

        progress = monitor.get_consolidation_progress(args.target)
        if progress:
            print(f"📈 Progress for {args.target}:")
            for key, value in progress.items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ No progress found for target: {args.target}")


def _handle_validate_command(consolidation: IntegratedImportConsolidation, args):
    """Handle validate subcommand."""
    print("🧪 Running import equivalence validation...")

    validator = consolidation.equivalence_validator

    if args.config:
        # Load validation configuration
        config = read_json(args.config, {})
        original_imports = config.get("original_imports", [])
        consolidated_imports = config.get("consolidated_imports", [])
        test_files = [Path(f) for f in config.get("test_files", [])]
    else:
        # Use command line arguments
        original_imports = args.original or []
        consolidated_imports = args.consolidated or []
        test_files = [Path(f) for f in (args.test_files or [])]

    if not original_imports or not consolidated_imports:
        print("❌ Error: Must provide both original and consolidated imports")
        return

    try:
        report = validator.validate_consolidation_equivalence(
            original_imports, consolidated_imports, test_files
        )

        print(f"\n📊 Validation Results:")
        print(f"  Total imports: {report.total_imports}")
        print(
            f"  Passed: {report.passed_imports} ({report.passed_imports / report.total_imports * 100:.1f}%)"
        )
        print(f"  Failed: {report.failed_imports}")
        print(f"  Warnings: {report.warning_imports}")
        print(f"  Performance impact: {report.performance_impact:.2%}")

        if report.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in report.recommendations:
                print(f"  • {rec}")

        # Save report
        report_file = (
            consolidation.root / ".ai_onboard" / "import_equivalence_report.json"
        )
        write_json(report_file, report.__dict__)
        print(f"\n💾 Report saved to: {report_file}")

    except Exception as e:
        print(f"❌ Error running validation: {e}")


def _handle_status_command(consolidation: IntegratedImportConsolidation, args):
    """Handle status subcommand."""
    if args.workflow_id:
        status = consolidation.get_workflow_status(args.workflow_id)
        print("📊 Workflow Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
    else:
        status = consolidation.get_workflow_status()
        print("📊 Current Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")


def _handle_rollback_command(consolidation: IntegratedImportConsolidation, args):
    """Handle rollback subcommand."""
    if not args.workflow_id:
        print("❌ Error: Must specify workflow ID to rollback")
        return

    print(f"🔄 Rolling back workflow: {args.workflow_id}")

    try:
        # Get workflow status
        status = consolidation.get_workflow_status(args.workflow_id)

        if status.get("status") == "completed":
            print(
                "⚠️  Warning: Workflow is already completed. Rollback may not be necessary."
            )

        # Attempt rollback
        rollback_result = consolidation._attempt_rollback()

        if rollback_result["success"]:
            print(f"✅ Rollback completed: {rollback_result['message']}")
        else:
            print(f"❌ Rollback failed: {rollback_result['message']}")

    except Exception as e:
        print(f"❌ Error during rollback: {e}")


def add_consolidation_parser(subparsers):
    """Add consolidation commands to the CLI parser."""
    consolidation_parser = subparsers.add_parser(
        "consolidate", help="Import consolidation commands"
    )

    # Create subparsers for consolidation subcommands
    consolidation_subparsers = consolidation_parser.add_subparsers(
        dest="subcommand", help="Available consolidation commands"
    )

    # Analyze command
    analyze_parser = consolidation_subparsers.add_parser(
        "analyze", help="Analyze consolidation opportunities"
    )
    analyze_parser.add_argument("--output", help="Output file for analysis results")

    # Plan command
    plan_parser = consolidation_subparsers.add_parser(
        "plan", help="Create migration plan"
    )
    plan_parser.add_argument("targets", nargs="+", help="Consolidation targets")
    plan_parser.add_argument(
        "--config", help="Configuration file for consolidation targets"
    )

    # Execute command
    execute_parser = consolidation_subparsers.add_parser(
        "execute", help="Execute consolidation workflow"
    )
    execute_parser.add_argument("targets", nargs="+", help="Consolidation targets")
    execute_parser.add_argument(
        "--dry-run", action="store_true", help="Run in dry-run mode"
    )
    execute_parser.add_argument(
        "--auto-approve", action="store_true", help="Auto-approve all prompts"
    )

    # Monitor command
    monitor_parser = consolidation_subparsers.add_parser(
        "monitor", help="Monitor consolidation progress"
    )
    monitor_subparsers = monitor_parser.add_subparsers(
        dest="action", help="Monitor actions"
    )

    # Monitor start
    monitor_start_parser = monitor_subparsers.add_parser(
        "start", help="Start monitoring"
    )
    monitor_start_parser.add_argument("targets", nargs="+", help="Targets to monitor")

    # Monitor stop
    monitor_subparsers.add_parser("stop", help="Stop monitoring")

    # Monitor status
    monitor_subparsers.add_parser("status", help="Show monitoring status")

    # Monitor progress
    monitor_progress_parser = monitor_subparsers.add_parser(
        "progress", help="Show progress for specific target"
    )
    monitor_progress_parser.add_argument("target", help="Target to show progress for")

    # Validate command
    validate_parser = consolidation_subparsers.add_parser(
        "validate", help="Validate import equivalence"
    )
    validate_parser.add_argument(
        "--original", nargs="+", help="Original import statements"
    )
    validate_parser.add_argument(
        "--consolidated", nargs="+", help="Consolidated import statements"
    )
    validate_parser.add_argument(
        "--test-files", nargs="+", help="Test files to validate against"
    )
    validate_parser.add_argument(
        "--config", help="Configuration file with import mappings"
    )

    # Status command
    status_parser = consolidation_subparsers.add_parser(
        "status", help="Show workflow status"
    )
    status_parser.add_argument("--workflow-id", help="Specific workflow ID to check")

    # Rollback command
    rollback_parser = consolidation_subparsers.add_parser(
        "rollback", help="Rollback a workflow"
    )
    rollback_parser.add_argument("workflow_id", help="Workflow ID to rollback")

    # Set the command handler
    consolidation_parser.set_defaults(func=consolidate_imports_command)
