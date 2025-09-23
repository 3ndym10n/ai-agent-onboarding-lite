"""CLI commands for code quality analysis tools."""

import argparse
from pathlib import Path

from ..core.codebase_analysis import CodebaseAnalyzer
from ..core.dependency_checker import check_cleanup_dependencies
from ..core.syntax_validator import validate_python_syntax
from ..core.unicode_utils import print_activity, print_header, print_status


def add_code_quality_commands(subparsers):
    """Add code quality analysis commands."""

    # Code Quality parent parser
    code_quality_parser = subparsers.add_parser(
        "code-quality",
        help="Code quality analysis and validation tools",
        description="Comprehensive code quality analysis tools including syntax validation, "
        "dependency checking, and codebase analysis.",
    )
    code_quality_subparsers = code_quality_parser.add_subparsers(
        dest="code_quality_cmd", help="Code quality commands"
    )

    # Codebase analysis command
    codebase_parser = code_quality_subparsers.add_parser(
        "analyze",
        help="Perform comprehensive codebase analysis",
        description="Analyze the entire codebase for organization, "
        "dependencies, and quality metrics.",
    )
    codebase_parser.set_defaults(func=handle_codebase_analysis)

    # Syntax validation command
    syntax_parser = code_quality_subparsers.add_parser(
        "syntax",
        help="Validate Python syntax across all files",
        description="Check Python syntax and \
            import validity across the entire codebase.",
    )
    syntax_parser.set_defaults(func=handle_syntax_validation)

    # Dependency check command
    dep_parser = code_quality_subparsers.add_parser(
        "dependencies",
        help="Check dependencies for safe file removal",
        description="Analyze dependencies before cleanup operations to ensure safe file removal.",
    )
    dep_parser.add_argument(
        "--targets",
        nargs="+",
        help="Specific files to check dependencies for (default: scan for common cleanup targets)",
    )
    dep_parser.set_defaults(func=handle_dependency_check)


def handle_codebase_analysis(args):
    """Handle comprehensive codebase analysis."""
    print_header("COMPREHENSIVE CODEBASE ANALYSIS")

    try:
        print_activity("Initializing codebase analyzer...")
        analyzer = CodebaseAnalyzer(Path("."))

        print_activity("Analyzing codebase structure...")
        result = analyzer.analyze_codebase()

        # Display results
        print_header("ANALYSIS RESULTS")

        print(f"📊 Files Analyzed: {result.get('files_analyzed', 0)}")
        print(f"📁 Directories Analyzed: {result.get('directories_analyzed', 0)}")
        print(f"🔗 Total Dependencies: {result.get('total_dependencies', 0)}")
        print(f"⚠️  Organization Issues: {result.get('total_issues', 0)}")
        print(
            f"🔄 Circular Dependencies: {len(result.get('circular_dependencies',
            []))}"
        )
        print(f"📦 Duplicate Groups: {len(result.get('consolidation_candidates', []))}")

        # Show top issues
        issues = result.get("organization_issues", [])
        if issues:
            print_header("TOP ORGANIZATION ISSUES")
            for i, issue in enumerate(issues[:5]):  # Show top 5
                severity_icon = (
                    "🔴"
                    if issue.get("severity") == "critical"
                    else "🟠" if issue.get("severity") == "high" else "🟡"
                )
                print(f"{i+1}. {severity_icon} {issue.get('message', 'Unknown issue')}")

        # Show circular dependencies
        circular = result.get("circular_dependencies", [])
        if circular:
            print_header("CIRCULAR DEPENDENCIES DETECTED")
            for i, cycle in enumerate(circular[:3]):  # Show first 3
                print(f"{i+1}. {' → '.join(cycle)}")

        print_status("Codebase analysis completed successfully", "success")

    except Exception as e:
        print_status(f"Codebase analysis failed: {e}", "error")


def handle_syntax_validation(args):
    """Handle Python syntax validation across all files."""
    print_header("PYTHON SYNTAX VALIDATION")

    try:
        import os

        print_activity("Scanning for Python files...")
        python_files = []
        for root, dirs, files in os.walk("."):
            # Skip common non-code directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["__pycache__", "node_modules", "venv", ".git"]
            ]
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))

        print(f"📁 Found {len(python_files)} Python files to validate")

        results = []
        valid_count = 0
        error_count = 0

        print_activity("Validating syntax...")
        for i, filepath in enumerate(python_files):
            if (i + 1) % 50 == 0 or i + 1 == len(python_files):
                print_activity(f"Validated {i+1}/{len(python_files)} files...")

            try:
                status = validate_python_syntax(filepath)
                is_valid = status == "valid"
                results.append({"file": filepath, "valid": is_valid, "status": status})

                if is_valid:
                    valid_count += 1
                else:
                    error_count += 1

            except Exception as e:
                results.append({"file": filepath, "valid": False, "error": str(e)})
                error_count += 1

        # Display results
        print_header("VALIDATION RESULTS")

        print(f"✅ Valid Files: {valid_count}")
        print(f"❌ Invalid Files: {error_count}")
        print(f"📊 Total Files: {len(results)}")
        success_rate = (valid_count / len(results) * 100) if results else 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
        # Show errors if any
        if error_count > 0:
            print_header("FILES WITH SYNTAX ERRORS")
            error_files = [r for r in results if not r["valid"]]
            for error_file in error_files[:10]:  # Show first 10
                status = error_file.get(
                    "status", error_file.get("error", "Unknown error")
                )
                print(f"❌ {error_file['file']}: {status}")

            if error_count > 10:
                print(f"... and {error_count - 10} more files with errors")

        if error_count == 0:
            print_status("All Python files have valid syntax!", "success")
        else:
            print_status(f"Found {error_count} files with syntax errors", "warning")

    except Exception as e:
        print_status(f"Syntax validation failed: {e}", "error")


def handle_dependency_check(args):
    """Handle dependency checking for safe file removal."""
    print_header("DEPENDENCY ANALYSIS FOR CLEANUP")

    try:
        # Determine target files
        if args.targets:
            target_files = [Path(target) for target in args.targets]
            print(
                f"🔍 Checking dependencies for {len(target_files)} specified files..."
            )
        else:
            # Scan for common cleanup targets
            print_activity("Scanning for common cleanup targets...")
            import os

            target_files = []
            cleanup_patterns = ["*.pyc", "*.pyo", "__pycache__", "*.tmp", "*.bak"]

            for root, dirs, files in os.walk("."):
                for file in files:
                    filepath = os.path.join(root, file)
                    if any(
                        file.endswith(pattern.lstrip("*"))
                        for pattern in cleanup_patterns
                        if not pattern.startswith("__")
                    ):
                        target_files.append(Path(filepath))
                    elif "__pycache__" in filepath:
                        target_files.append(Path(filepath))

            print(f"🎯 Found {len(target_files)} potential cleanup targets")

        if not target_files:
            print_status("No cleanup targets found", "info")
            return

        # Check dependencies
        print_activity("Analyzing dependencies...")
        results = check_cleanup_dependencies(Path("."), target_files)

        # Display results
        print_header("DEPENDENCY ANALYSIS RESULTS")

        safe_count = 0
        unsafe_count = 0

        for result in results:
            if result.is_safe_to_delete:
                safe_count += 1
            else:
                unsafe_count += 1

        print(f"✅ Safe to Remove: {safe_count}")
        print(f"⚠️  Dependencies Found: {unsafe_count}")
        print(f"📁 Total Targets: {len(results)}")

        # Show unsafe files with their dependencies
        unsafe_files = [r for r in results if not r.is_safe_to_delete]
        if unsafe_files:
            print_header("FILES WITH DEPENDENCIES (UNSAFE TO REMOVE)")
            for result in unsafe_files[:5]:  # Show first 5
                print(f"⚠️  {result.target_file}")
                for dep in result.dependencies[:3]:  # Show first 3 dependencies
                    print(f"    └─ Referenced by: {dep.source_file}:{dep.line_number}")
                if len(result.dependencies) > 3:
                    print(
                        f"    └─ ... and \
                        {len(result.dependencies) - 3} more references"
                    )

        # Show safe files
        safe_files = [r for r in results if r.is_safe_to_delete]
        if safe_files:
            print_header("FILES SAFE TO REMOVE")
            for result in safe_files[:10]:  # Show first 10
                print(f"✅ {result.target_file}")
            if len(safe_files) > 10:
                print(f"... and {len(safe_files) - 10} more safe files")

        if safe_count == len(results):
            print_status("All target files are safe to remove!", "success")
        elif unsafe_count > 0:
            print_status(
                f"Found {unsafe_count} files with dependencies - use caution!",
                "warning",
            )

    except Exception as e:
        print_status(f"Dependency check failed: {e}", "error")


def handle_code_quality_commands(args):
    """Handle code quality command routing."""
    if hasattr(args, "func"):
        args.func(args)
    else:
        print("No code quality command specified. Use --help for available commands.")
