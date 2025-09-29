"""
CLI commands for cleanup safety gate management.

This module provides commands to manage cleanup safety gates,
view backups, perform rollbacks, and configure safety settings.
"""

import json
from pathlib import Path
from typing import Any

from ..core.quality_safety.cleanup_safety_gates import (
    CleanupOperation,
    CleanupSafetyGateFramework,
    safe_cleanup_operation,
)
from ..core.quality_safety.ultra_safe_cleanup import (
    CleanupOperation as UltraCleanupOperation,
)
from ..core.quality_safety.ultra_safe_cleanup import (
    UltraSafeCleanupEngine,
    execute_ultra_safe_cleanup,
    present_cleanup_proposal,
    propose_cleanup_operation,
    scan_cleanup_targets,
)
from ..core.utilities.unicode_utils import (
    print_activity,
    print_content,
    print_status,
    safe_print,
)


def add_cleanup_safety_commands(subparsers):
    """Add cleanup safety commands to the CLI."""

    # Main cleanup - safety command
    safety_parser = subparsers.add_parser(
        "cleanup - safety",
        help="Cleanup safety gate management",
        description="Manage cleanup safety gates, backups, and rollback operations",
    )
    safety_subparsers = safety_parser.add_subparsers(
        dest="safety_action", help="Safety actions"
    )

    # Test safety gates
    test_parser = safety_subparsers.add_parser(
        "test", help="Test safety gates with a file"
    )
    test_parser.add_argument("files", nargs="+", help="Files to test safety gates with")
    test_parser.add_argument(
        "--operation",
        choices=["delete", "move", "modify"],
        default="delete",
        help="Type of operation to test",
    )
    test_parser.add_argument(
        "--dry - run",
        action="store_true",
        help="Show what would happen without executing",
    )

    # List backups
    list_parser = safety_subparsers.add_parser(
        "list - backups", help="List available backups"
    )
    list_parser.add_argument(
        "--limit", type=int, default=10, help="Maximum number of backups to show"
    )

    # Rollback operation
    rollback_parser = safety_subparsers.add_parser(
        "rollback", help="Rollback a previous operation"
    )
    rollback_parser.add_argument("backup_id", help="Backup ID to rollback to")
    rollback_parser.add_argument(
        "--confirm", action="store_true", help="Skip confirmation prompt"
    )

    # Clean old backups
    clean_parser = safety_subparsers.add_parser(
        "clean - backups", help="Clean old backup files"
    )
    clean_parser.add_argument(
        "--days", type=int, default=30, help="Delete backups older than N days"
    )
    clean_parser.add_argument(
        "--dry - run",
        action="store_true",
        help="Show what would be deleted without deleting",
    )

    # Configure safety gates
    config_parser = safety_subparsers.add_parser(
        "config", help="Configure safety gate settings"
    )
    config_parser.add_argument(
        "--strict - mode",
        choices=["on", "off"],
        help="Enable / disable strict safety mode",
    )
    config_parser.add_argument(
        "--auto - rollback",
        choices=["on", "off"],
        help="Enable / disable automatic rollback on failure",
    )
    config_parser.add_argument(
        "--show", action="store_true", help="Show current configuration"
    )

    # Status command
    status_parser = safety_subparsers.add_parser(
        "status", help="Show safety gate status"
    )

    # Ultra-safe cleanup commands
    ultra_parser = safety_subparsers.add_parser(
        "ultra-cleanup",
        help="Ultra-safe incremental cleanup with zero-tolerance safety",
        description="Perform cleanup operations with maximum safety and \
            human oversight",
    )
    ultra_subparsers = ultra_parser.add_subparsers(
        dest="ultra_action", help="Ultra-safe cleanup actions"
    )

    # Scan for cleanup targets
    scan_parser = ultra_subparsers.add_parser(
        "scan", help="Scan project for potential cleanup targets"
    )
    scan_parser.add_argument(
        "--max-files",
        type=int,
        default=50,
        help="Maximum number of files to show (default: 50)",
    )

    # Propose cleanup operation
    propose_parser = ultra_subparsers.add_parser(
        "propose", help="Create and present cleanup proposal"
    )
    propose_parser.add_argument(
        "--risk-level",
        choices=["safe", "low", "medium"],
        default="safe",
        help="Maximum risk level to include (default: safe)",
    )
    propose_parser.add_argument(
        "--max-size-mb",
        type=float,
        default=100.0,
        help="Maximum total size in MB (default: 100)",
    )

    # Execute cleanup operation
    execute_parser = ultra_subparsers.add_parser(
        "execute", help="Execute approved cleanup operation"
    )
    execute_parser.add_argument("operation_id", help="Operation ID from proposal")
    execute_parser.add_argument(
        "--confirmed-by", help="Name/email of person confirming operation"
    )


def handle_cleanup_safety_commands(args, root: Path):
    """Handle cleanup safety commands."""
    if not hasattr(args, "safety_action") or not args.safety_action:
        print_status("No safety action specified. Use --help for options.", "error")
        return

    if args.safety_action == "test":
        _handle_test_safety_gates(args, root)
    elif args.safety_action == "list - backups":
        _handle_list_backups(args, root)
    elif args.safety_action == "rollback":
        _handle_rollback(args, root)
    elif args.safety_action == "clean - backups":
        _handle_clean_backups(args, root)
    elif args.safety_action == "config":
        _handle_config(args, root)
    elif args.safety_action == "status":
        _handle_status(args, root)
    elif args.safety_action == "ultra-cleanup":
        _handle_ultra_cleanup(args, root)
    else:
        print_status(f"Unknown safety action: {args.safety_action}", "error")


def _handle_test_safety_gates(args, root: Path):
    """Handle testing safety gates."""
    print_content("Testing cleanup safety gates...", "search")

    # Convert file arguments to Path objects
    target_files = []
    for file_arg in args.files:
        file_path = Path(file_arg)
        if not file_path.is_absolute():
            file_path = root / file_path

        if not file_path.exists():
            print_status(f"File not found: {file_path}", "warning")
            continue

        target_files.append(file_path)

    if not target_files:
        print_status("No valid files to test", "error")
        return

    if args.dry_run:
        print_content("DRY RUN MODE - No actual operations will be performed", "info")

        # Create framework and show what would happen
        framework = CleanupSafetyGateFramework(root)
        operation = CleanupOperation(
            operation_type=args.operation,
            targets=target_files,
            description=f"Test {args.operation} operation on {len(target_files)} files",
        )

        safe_print(f"\n📋 OPERATION PREVIEW:")
        safe_print(f"   Type: {operation.operation_type.upper()}")
        safe_print(f"   Targets: {len(operation.targets)} files")
        safe_print(f"   Files:")
        for target in operation.targets:
            safe_print(f"     - {target.relative_to(root)}")

        safe_print(f"\n🛡️ SAFETY GATES THAT WOULD RUN:")
        for i, gate in enumerate(framework.gates, 1):
            status = "✅ Enabled" if gate.enabled else "❌ Disabled"
            safe_print(f"   {i}. {gate.name}: {status}")

        safe_print(f"\n💡 To run actual test: remove --dry - run flag")
        return

    # Run actual test
    success, message = safe_cleanup_operation(
        root=root,
        operation_type=args.operation,
        targets=target_files,
        description=f"Safety gate test: {args.operation} {len(target_files)} files",
    )

    if success:
        print_status(f"✅ Safety gate test completed: {message}", "success")
    else:
        print_status(f"❌ Safety gate test failed: {message}", "error")


def _handle_list_backups(args, root: Path):
    """Handle listing available backups."""
    print_content("Listing available backups...", "search")

    framework = CleanupSafetyGateFramework(root)
    backups = framework.get_available_backups()

    if not backups:
        print_status("No backups found", "info")
        return

    safe_print(f"\n📦 AVAILABLE BACKUPS ({len(backups)} total):")
    safe_print("=" * 60)

    for i, backup in enumerate(backups[: args.limit]):
        safe_print(f"\n{i + 1}. Backup ID: {backup['backup_id']}")
        safe_print(f"   Timestamp: {backup['timestamp']}")
        safe_print(f"   Operation: {backup['operation']['type'].upper()}")
        safe_print(f"   Description: {backup['operation']['description']}")
        safe_print(f"   Files: {len(backup['files'])} backed up")

        if backup["operation"]["targets"]:
            safe_print(f"   Targets:")
            for target in backup["operation"]["targets"][:3]:
                safe_print(f"     - {Path(target).name}")
            if len(backup["operation"]["targets"]) > 3:
                safe_print(
                    f"     ... and {len(backup['operation']['targets']) - 3} more"
                )

    if len(backups) > args.limit:
        safe_print(f"\n... and {len(backups) - args.limit} more backups")
        safe_print(f"Use --limit {len(backups)} to see all backups")

    safe_print(f"\n💡 To rollback: ai_onboard cleanup - safety rollback <backup_id>")


def _handle_rollback(args, root: Path):
    """Handle rollback operation."""
    print_content(f"Preparing rollback for backup: {args.backup_id}", "search")

    framework = CleanupSafetyGateFramework(root)

    # Find the backup
    backups = framework.get_available_backups()
    target_backup = None

    for backup in backups:
        if backup["backup_id"] == args.backup_id:
            target_backup = backup
            break

    if not target_backup:
        print_status(f"Backup not found: {args.backup_id}", "error")
        print_content("Available backups:", "info")
        for backup in backups[:5]:
            safe_print(f"  - {backup['backup_id']} ({backup['timestamp']})")
        return

    # Show rollback details
    safe_print(f"\n🔄 ROLLBACK OPERATION DETAILS:")
    safe_print("=" * 50)
    safe_print(f"Backup ID: {target_backup['backup_id']}")
    safe_print(f"Timestamp: {target_backup['timestamp']}")
    safe_print(f"Original Operation: {target_backup['operation']['type'].upper()}")
    safe_print(f"Description: {target_backup['operation']['description']}")
    safe_print(f"Files to restore: {len(target_backup['files'])}")

    if target_backup["files"]:
        safe_print(f"\nFiles that will be restored:")
        for file_info in target_backup["files"][:5]:
            safe_print(f"  - {Path(file_info['original']).name}")
        if len(target_backup["files"]) > 5:
            safe_print(f"  ... and {len(target_backup['files']) - 5} more")

    # Confirm rollback
    if not args.confirm:
        safe_print(
            f"\n⚠️ WARNING: This will overwrite current files with backup versions!"
        )

        try:
            confirmation = input(f"\nType 'ROLLBACK' to confirm: ").strip()
            if confirmation != "ROLLBACK":
                print_status("Rollback cancelled", "info")
                return
        except (KeyboardInterrupt, EOFError):
            print_status("Rollback cancelled", "info")
            return

    # Perform rollback
    print_activity("Performing rollback...")

    success, message = framework.rollback_operation(args.backup_id)

    if success:
        print_status(f"✅ Rollback completed: {message}", "success")
    else:
        print_status(f"❌ Rollback failed: {message}", "error")


def _handle_clean_backups(args, root: Path):
    """Handle cleaning old backups."""
    print_content(f"Cleaning backups older than {args.days} days...", "search")

    CleanupSafetyGateFramework(root)
    backups_dir = root / ".ai_onboard" / "backups"

    if not backups_dir.exists():
        print_status("No backups directory found", "info")
        return

    # Find old backups
    import datetime

    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=args.days)

    old_backups = []
    total_size = 0

    for backup_dir in backups_dir.iterdir():
        if backup_dir.is_dir():
            try:
                # Parse timestamp from backup ID
                timestamp_str = (
                    backup_dir.name.split("_")[2] + "_" + backup_dir.name.split("_")[3]
                )
                backup_date = datetime.datetime.strptime(
                    timestamp_str, "%Y % m % d_ % H % M % S"
                )

                if backup_date < cutoff_date:
                    # Calculate size
                    size = sum(
                        f.stat().st_size for f in backup_dir.rglob("*") if f.is_file()
                    )
                    old_backups.append((backup_dir, backup_date, size))
                    total_size += size

            except (ValueError, IndexError):
                # Skip backups with invalid names
                continue

    if not old_backups:
        print_status(f"No backups older than {args.days} days found", "info")
        return

    # Show what will be cleaned
    safe_print(f"\n🧹 BACKUP CLEANUP SUMMARY:")
    safe_print("=" * 40)
    safe_print(f"Backups to clean: {len(old_backups)}")
    safe_print(f"Total size: {total_size / (1024 * 1024):.1f} MB")
    safe_print(f"Age cutoff: {args.days} days")

    if args.dry_run:
        safe_print(f"\nBackups that would be deleted:")
        for backup_dir, backup_date, size in old_backups:
            age_days = (datetime.datetime.now() - backup_date).days
            safe_print(
                f"  - {backup_dir.name} ({age_days} days old, "
                f"{size / (1024 * 1024):.1f} MB)"
            )

        safe_print(f"\n💡 Remove --dry - run to actually delete these backups")
        return

    # Confirm deletion
    try:
        confirmation = (
            input(f"\nDelete {len(old_backups)} old backups? (y / N): ").strip().lower()
        )
        if confirmation not in ["y", "yes"]:
            print_status("Cleanup cancelled", "info")
            return
    except (KeyboardInterrupt, EOFError):
        print_status("Cleanup cancelled", "info")
        return

    # Delete old backups
    deleted_count = 0
    deleted_size = 0

    for backup_dir, backup_date, size in old_backups:
        try:
            import shutil

            shutil.rmtree(backup_dir)
            deleted_count += 1
            deleted_size += size
            safe_print(f"  ✅ Deleted {backup_dir.name}")
        except Exception as e:
            safe_print(f"  ❌ Failed to delete {backup_dir.name}: {e}")

    print_status(
        f"Cleanup completed: {deleted_count} backups deleted, "
        f"{deleted_size / (1024 * 1024):.1f} MB freed",
        "success",
    )


def _handle_config(args, root: Path):
    """Handle safety gate configuration."""
    config_file = root / ".ai_onboard" / "safety_config.json"

    # Load current config
    default_config = {
        "strict_mode": True,
        "auto_rollback_on_failure": True,
        "backup_retention_days": 30,
        "require_confirmation_for_medium_risk": True,
        "enabled_gates": [
            "PreFlightGate",
            "DependencyAnalysisGate",
            "RiskAssessmentGate",
            "HumanConfirmationGate",
            "BackupExecuteGate",
            "PostOperationGate",
        ],
    }

    if config_file.exists():
        try:

            with open(config_file, "r") as f:
                config = json.load(f)
        except Exception:
            config = default_config.copy()
    else:
        config = default_config.copy()

    # Handle configuration changes
    changed = False

    if args.strict_mode:
        config["strict_mode"] = args.strict_mode == "on"
        changed = True
        print_status(
            f"Strict mode: {'enabled' if config['strict_mode'] else 'disabled'}", "info"
        )

    if args.auto_rollback:
        config["auto_rollback_on_failure"] = args.auto_rollback == "on"
        changed = True
        print_status(
            f"Auto rollback: {'enabled' if config['auto_rollback_on_failure'] else 'disabled'}",
            "info",
        )

    # Save config if changed
    if changed:
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w") as f:

            json.dump(config, f, indent=2)
        print_status("Configuration saved", "success")

    # Show current configuration
    if args.show or not changed:
        safe_print(f"\n🔧 CLEANUP SAFETY CONFIGURATION:")
        safe_print("=" * 40)
        safe_print(
            f"Strict mode: {'✅ Enabled' if config['strict_mode'] else '❌ Disabled'}"
        )
        safe_print(
            f"Auto rollback: {'✅ Enabled' if config['auto_rollback_on_failure'] else '❌ Disabled'}"
        )
        safe_print(f"Backup retention: {config['backup_retention_days']} days")
        confirmation = (
            "✅ Required"
            if config["require_confirmation_for_medium_risk"]
            else "❌ Not required"
        )
        safe_print(f"Medium risk confirmation: {confirmation}")

        safe_print(f"\nEnabled safety gates:")
        for gate in config["enabled_gates"]:
            safe_print(f"  ✅ {gate}")


def _handle_status(args, root: Path):
    """Handle safety gate status display."""
    print_content("Checking cleanup safety gate status...", "search")

    framework = CleanupSafetyGateFramework(root)

    safe_print(f"\n🛡️ CLEANUP SAFETY GATE STATUS:")
    safe_print("=" * 50)

    # Show framework status
    safe_print(f"Framework: ✅ Initialized")
    safe_print(f"Root directory: {root}")
    safe_print(f"Total gates: {len(framework.gates)}")

    # Show individual gate status
    safe_print(f"\nSafety Gates:")
    for i, gate in enumerate(framework.gates, 1):
        status = "✅ Enabled" if gate.enabled else "❌ Disabled"
        safe_print(f"  {i}. {gate.name}: {status}")

    # Show backup information
    backups = framework.get_available_backups()
    safe_print(f"\nBackup Status:")
    safe_print(f"  Available backups: {len(backups)}")

    if backups:
        latest_backup = backups[0]
        safe_print(f"  Latest backup: {latest_backup['backup_id']}")
        safe_print(f"  Latest timestamp: {latest_backup['timestamp']}")

    # Show configuration
    config_file = root / ".ai_onboard" / "safety_config.json"
    if config_file.exists():
        safe_print(f"  Configuration: ✅ Custom config loaded")
    else:
        safe_print(f"  Configuration: ⚠️ Using defaults")


def _handle_ultra_cleanup(args, root: Path):
    """Handle ultra-safe cleanup commands."""
    if not hasattr(args, "ultra_action") or not args.ultra_action:
        print_status(
            "No ultra-cleanup action specified. Use --help for options.", "error"
        )
        return

    if args.ultra_action == "scan":
        _handle_ultra_scan(args, root)
    elif args.ultra_action == "propose":
        _handle_ultra_propose(args, root)
    elif args.ultra_action == "execute":
        _handle_ultra_execute(args, root)
    else:
        print_status(f"Unknown ultra-cleanup action: {args.ultra_action}", "error")


def _handle_ultra_scan(args, root: Path):
    """Handle ultra-safe cleanup scanning."""
    print_content("🔍 Scanning for ultra-safe cleanup targets...", "search")

    try:
        targets = scan_cleanup_targets(root)

        if not targets:
            print_status("No cleanup targets found that meet safety criteria.", "info")
            return

        safe_print(f"\n🧹 CLEANUP TARGETS FOUND: {len(targets)} files")
        safe_print("=" * 60)

        # Group by risk level
        risk_groups: dict[str, Any] = {}
        total_size = 0

        for target in targets:
            level = target.risk_level.value
            if level not in risk_groups:
                risk_groups[level] = []
            risk_groups[level].append(target)
            total_size += target.size_bytes

        # Show summary
        safe_print(f"\n📊 SUMMARY:")
        safe_print(f"   Total files: {len(targets)}")
        safe_print(f"   Total size: {total_size / (1024 * 1024):.1f} MB")

        for level in ["safe", "low", "medium"]:
            if level in risk_groups:
                count = len(risk_groups[level])
                size_mb = sum(t.size_bytes for t in risk_groups[level]) / (1024 * 1024)
                safe_print(f"   {level.upper()}: {count} files ({size_mb:.1f} MB)")

        # Show sample files
        safe_print(f"\n📄 SAMPLE FILES (first {min(args.max_files, len(targets))}):")
        for i, target in enumerate(targets[: args.max_files]):
            rel_path = target.path.relative_to(root)
            size_kb = target.size_bytes / 1024
            safe_print(f"   {i + 1}. {rel_path}")
            safe_print(f"      Risk: {target.risk_level.value.upper()}")
            safe_print(f"      Size: {size_kb:.1f} KB")
            safe_print(f"      Reason: {target.reason}")

        if len(targets) > args.max_files:
            safe_print(f"   ... and {len(targets) - args.max_files} more files")

        safe_print(f"\n💡 Next steps:")
        safe_print(
            f"   • Propose cleanup: ai_onboard cleanup-safety ultra-cleanup propose"
        )
        safe_print(
            f"   • Safe only: ai_onboard cleanup-safety ultra-cleanup propose --risk-level safe"
        )

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error: {e}")


def _handle_ultra_propose(args, root: Path):
    """Handle ultra-safe cleanup proposal creation."""
    print_content("📋 Creating ultra-safe cleanup proposal...", "search")

    try:
        # Scan for targets
        all_targets = scan_cleanup_targets(root)

        if not all_targets:
            print_status("No cleanup targets found that meet safety criteria.", "info")
            return

        # Filter by risk level and size
        filtered_targets = []
        for target in all_targets:
            # Risk level filter
            if target.risk_level.value not in ["safe", "low", "medium"]:
                continue
            if ["safe", "low", "medium"].index(target.risk_level.value) > [
                "safe",
                "low",
                "medium",
            ].index(args.risk_level):
                continue

            filtered_targets.append(target)

        if not filtered_targets:
            print_status(
                f"No targets found for risk level '{args.risk_level}' or lower.", "info"
            )
            return

        # Size limit filter
        total_size_mb = sum(t.size_bytes for t in filtered_targets) / (1024 * 1024)
        if total_size_mb > args.max_size_mb:
            # Sort by size descending and keep largest files until limit
            filtered_targets.sort(key=lambda t: t.size_bytes, reverse=True)
            cumulative_size = 0.0
            size_limited_targets = []

            for target in filtered_targets:
                if (
                    cumulative_size + (target.size_bytes / (1024 * 1024))
                    <= args.max_size_mb
                ):
                    size_limited_targets.append(target)
                    cumulative_size += target.size_bytes / (1024 * 1024)
                else:
                    break

            filtered_targets = size_limited_targets
            total_size_mb = cumulative_size

        if not filtered_targets:
            print_status(
                f"No targets fit within size limit of {args.max_size_mb} MB.", "info"
            )
            return

        # Create operation proposal
        operation = propose_cleanup_operation(root, filtered_targets)

        safe_print(f"\n✅ CLEANUP PROPOSAL CREATED")
        safe_print(f"   Operation ID: {operation.operation_id}")
        safe_print(f"   Risk Level: {args.risk_level.upper()}")
        safe_print(f"   Files: {len(filtered_targets)}")
        safe_print(f"   Total Size: {total_size_mb:.1f} MB")

        # Present proposal and get confirmation
        user_approved = present_cleanup_proposal(root, operation)

        if user_approved:
            # Save operation for later execution
            operation.status = "approved"
            operation.confirmed_by = getattr(args, "confirmed_by", "user")

            engine = UltraSafeCleanupEngine(root)
            engine._log_operation(operation, "user_approved")

            safe_print(f"\n🎯 OPERATION APPROVED AND SAVED")
            safe_print(f"   Operation ID: {operation.operation_id}")
            safe_print(
                f"   To execute: ai_onboard cleanup-safety ultra-cleanup execute {operation.operation_id}"
            )
        else:
            safe_print(f"\n❌ OPERATION NOT APPROVED")
            operation.status = "rejected"
            engine = UltraSafeCleanupEngine(root)
            engine._log_operation(operation, "user_rejected")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error: {e}")


def _handle_ultra_execute(args, root: Path):
    """Handle ultra-safe cleanup execution."""
    print_content(
        f"⚡ Executing ultra-safe cleanup operation: {args.operation_id}", "search"
    )

    try:
        # For now, create a new operation (in future, load from saved operations)
        # This is a simplified version - production would load from operation log
        safe_print(f"\n⚠️ EXECUTION REQUIRES RECENT APPROVAL")
        safe_print("For safety, you must run 'propose' first to get approval.")
        safe_print("This ensures human confirmation before any deletions.")

        # Check if operation exists in log (simplified check)
        engine = UltraSafeCleanupEngine(root)
        operation_log = root / ".ai_onboard" / "cleanup_operations.jsonl"

        if operation_log.exists():
            recent_operations = []
            with open(operation_log, "r") as f:
                for line in f:
                    try:
                        op = json.loads(line.strip())
                        if op.get("operation_id") == args.operation_id:
                            recent_operations.append(op)
                    except (OSError, IOError, FileNotFoundError):

                        # Handle file system errors

                        continue
            approved_ops = [
                op for op in recent_operations if op.get("event") == "user_approved"
            ]

            if approved_ops:
                latest_approval = max(
                    approved_ops, key=lambda x: x.get("timestamp", "")
                )

                safe_print(f"\n✅ OPERATION FOUND AND APPROVED")
                safe_print(
                    f"   Approved at: {latest_approval.get('timestamp', 'unknown')}"
                )
                safe_print(
                    f"   Risk assessment: {latest_approval.get('risk_assessment', {}).get('max_risk_level', 'unknown')}"
                )

                # Create minimal operation for execution
                # In production, this would reconstruct the full operation from logs
                operation = UltraCleanupOperation(
                    operation_id=args.operation_id,
                    targets=[],  # Would load from approval log
                    risk_assessment={"confirmation_required": "approved"},
                )

                success, message = execute_ultra_safe_cleanup(root, operation)

                if success:
                    print_status(
                        f"✅ Cleanup executed successfully: {message}", "success"
                    )
                else:
                    print_status(f"❌ Cleanup execution failed: {message}", "error")
            else:
                print_status(
                    f"No approved operation found with ID: {args.operation_id}", "error"
                )
                safe_print("   Run 'propose' first to create and approve an operation.")
        else:
            print_status("No operation log found. Run 'propose' first.", "error")

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error: {e}")


# Convenience function for other modules


def is_safety_gates_available(root: Path) -> bool:
    """Check if cleanup safety gates are available and configured."""
    try:
        framework = CleanupSafetyGateFramework(root)
        return len(framework.gates) > 0
    except Exception:
        return False
