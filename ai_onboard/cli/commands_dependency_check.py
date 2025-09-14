"""
CLI commands for dependency checking.

This module provides commands to check dependencies before cleanup operations
or file modifications. Prevents accidental breakage of system dependencies.
"""

from pathlib import Path
from typing import List

from ..core.dependency_checker import DependencyChecker, check_cleanup_dependencies
from ..core.unicode_utils import print_content, print_status, safe_print


def add_dependency_check_commands(subparsers):
    """Add dependency check commands to the CLI."""

    # Main dependency check command
    dep_parser = subparsers.add_parser(
        "dependency - check",
        help="Check file dependencies before cleanup or modification",
        description="Analyze file dependencies to prevent accidental system breakage",
    )
    dep_subparsers = dep_parser.add_subparsers(
        dest="dep_action", help="Dependency check actions"
    )

    # Check specific files
    check_parser = dep_subparsers.add_parser(
        "check", help="Check dependencies for specific files"
    )
    check_parser.add_argument(
        "files", nargs="+", help="Files to check for dependencies"
    )
    check_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed dependency information"
    )
    check_parser.add_argument(
        "--report", action="store_true", help="Generate comprehensive report"
    )

    # Scan for all dependencies in project
    scan_parser = dep_subparsers.add_parser(
        "scan", help="Scan entire project for dependency relationships"
    )
    scan_parser.add_argument(
        "--pattern", help="File pattern to scan (e.g., '*.py', '*.md')"
    )
    scan_parser.add_argument("--output", help="Save results to file")

    # Validate cleanup safety
    validate_parser = dep_subparsers.add_parser(
        "validate - cleanup", help="Validate that cleanup operations are safe"
    )
    validate_parser.add_argument(
        "--dry - run", action="store_true", help="Show what would be checked"
    )


def handle_dependency_check_commands(args, root: Path):
    """Handle dependency check commands."""
    if not hasattr(args, "dep_action") or not args.dep_action:
        print_status(
            "No dependency check action specified. Use --help for options.", "error"
        )
        return

    if args.dep_action == "check":
        _handle_check_files(args, root)
    elif args.dep_action == "scan":
        _handle_scan_project(args, root)
    elif args.dep_action == "validate - cleanup":
        _handle_validate_cleanup(args, root)
    else:
        print_status(f"Unknown dependency check action: {args.dep_action}", "error")


def _handle_check_files(args, root: Path):
    """Handle checking specific files for dependencies."""
    print_content("Checking file dependencies...", "search")

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
        print_status("No valid files to check", "error")
        return

    # Run dependency check
    checker = DependencyChecker(root)
    results = checker.check_dependencies(target_files)

    # Display results
    if args.detailed or args.report:
        report = checker.generate_dependency_report(results)
        safe_print(report)
    else:
        # Simple summary
        safe_files = sum(1 for r in results if r.is_safe_to_delete)
        unsafe_files = len(results) - safe_files

        print_content(f"Dependency Check Results:", "stats")
        safe_print(f"  Total files checked: {len(results)}")
        safe_print(f"  Safe to delete: {safe_files}")
        safe_print(f"  Has dependencies: {unsafe_files}")

        if unsafe_files > 0:
            safe_print(f"\n  Files with dependencies:")
            for result in results:
                if not result.is_safe_to_delete:
                    safe_print(
                        f"    ⚠️ {result.target_file.name} ({len(result.dependencies)} deps)"
                    )

    # Generate fix plan if there are dependencies
    unsafe_results = [r for r in results if not r.is_safe_to_delete]
    if unsafe_results:
        fix_plan = checker.create_dependency_fix_plan(results)

        safe_print(f"\n🔧 Fix Plan:")
        safe_print(f"   Files needing updates: {len(fix_plan['files_to_update'])}")
        safe_print(f"   Estimated changes: {fix_plan['estimated_changes']}")

        if fix_plan["manual_review_needed"]:
            safe_print(
                f"   Manual review needed: {len(fix_plan['manual_review_needed'])}"
            )
            for file_path in fix_plan["manual_review_needed"][:3]:
                safe_print(f"     - {Path(file_path).name}")


def _handle_scan_project(args, root: Path):
    """Handle scanning the entire project for dependencies."""
    print_content("Scanning project for dependency relationships...", "search")

    checker = DependencyChecker(root)

    # Determine files to scan
    if args.pattern:
        scan_files = list(root.glob(args.pattern))
    else:
        # Scan all files matching the checker's patterns
        scan_files = []
        for pattern in checker.scannable_patterns:
            scan_files.extend(root.glob(pattern))

    # Remove duplicates
    scan_files = list(set(scan_files))

    print_content(f"Found {len(scan_files)} files to analyze", "stats")

    # For scanning, we'll check each file to see what depends on it
    dependency_map = {}

    for target_file in scan_files[:50]:  # Limit to prevent overwhelming output
        results = checker.check_dependencies([target_file])
        if results and results[0].dependencies:
            dependency_map[str(target_file)] = len(results[0].dependencies)

    # Display results
    safe_print(f"\n📊 Project Dependency Analysis:")
    safe_print(f"   Files scanned: {len(scan_files)}")
    safe_print(f"   Files with dependencies: {len(dependency_map)}")

    if dependency_map:
        safe_print(f"\n   Most referenced files:")
        sorted_deps = sorted(dependency_map.items(), key=lambda x: x[1], reverse=True)
        for file_path, dep_count in sorted_deps[:10]:
            file_name = Path(file_path).name
            safe_print(f"     {file_name}: {dep_count} dependencies")

    # Save results if requested
    if args.output:
        output_path = Path(args.output)
        import json

        output_data = {
            "scan_date": str(Path().cwd()),
            "files_scanned": len(scan_files),
            "dependency_map": dependency_map,
            "top_dependencies": dict(
                sorted(dependency_map.items(), key=lambda x: x[1], reverse=True)[:20]
            ),
        }

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)

        print_status(f"Results saved to {output_path}", "success")


def _handle_validate_cleanup(args, root: Path):
    """Handle validating cleanup operations."""
    print_content("Validating cleanup safety...", "search")

    # Import cleanup module to get files that would be deleted
    try:
        from ..core.cleanup import scan_for_cleanup

        scan_result = scan_for_cleanup(root)
        non_critical_files = scan_result["non_critical"]

        if not non_critical_files:
            print_status("No files found for cleanup", "info")
            return

        print_content(
            f"Found {len(non_critical_files)} files that would be deleted", "stats"
        )

        if args.dry_run:
            safe_print("\nFiles that would be checked:")
            for file_path in non_critical_files[:10]:
                safe_print(f"  - {file_path.relative_to(root)}")
            if len(non_critical_files) > 10:
                safe_print(f"  ... and {len(non_critical_files) - 10} more")
            return

        # Run dependency check
        is_safe = check_cleanup_dependencies(root, non_critical_files)

        if is_safe:
            print_status(
                "✅ Cleanup validation passed - all files are safe to delete", "success"
            )
        else:
            print_status(
                "❌ Cleanup validation failed - some files have dependencies", "error"
            )
            safe_print("\nRecommendation: Fix dependencies before running cleanup")
            safe_print(
                "Or use 'ai_onboard dependency - check check <file>' for detailed analysis"
            )

    except ImportError as e:
        print_status(f"Could not import cleanup module: {e}", "error")


# Convenience function for programmatic use
def check_file_dependencies(
    root: Path, files: List[str], detailed: bool = False
) -> bool:
    """
    Programmatically check file dependencies.

    Args:
        root: Project root directory
        files: List of file paths to check
        detailed: Whether to show detailed output

    Returns:
        bool: True if all files are safe to delete, False otherwise
    """
    target_files = []
    for file_str in files:
        file_path = Path(file_str)
        if not file_path.is_absolute():
            file_path = root / file_path

        if file_path.exists():
            target_files.append(file_path)

    if not target_files:
        return True  # No files to check

    return check_cleanup_dependencies(root, target_files)
