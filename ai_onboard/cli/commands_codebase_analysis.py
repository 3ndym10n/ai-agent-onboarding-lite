"""
CLI commands for codebase analysis and organization.

Provides commands to analyze codebase structure, identify organizational
improvements, and generate recommendations for better code organization.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from ..core import utils
from ..core.codebase_analysis import CodebaseAnalyzer
from ..core.unicode_utils import print_activity, print_content, print_status, safe_print


def add_codebase_analysis_commands(subparsers):
    """Add codebase analysis commands to the argument parser."""

    # Main codebase command
    codebase_parser = subparsers.add_parser(
        "codebase", help="Analyze and organize codebase structure"
    )

    # Subcommands
    subparsers_codebase = codebase_parser.add_subparsers(
        dest="codebase_cmd", help="Codebase analysis subcommands"
    )

    # Analyze command
    analyze_parser = subparsers_codebase.add_parser(
        "analyze", help="Perform comprehensive codebase analysis"
    )
    analyze_parser.add_argument(
        "--focus",
        type=str,
        choices=["organization", "quality", "dependencies", "duplicates", "all"],
        default="all",
        help="Focus analysis on specific aspect",
    )
    analyze_parser.add_argument(
        "--output",
        type=str,
        choices=["json", "text", "summary"],
        default="text",
        help="Output format (default: text)",
    )
    analyze_parser.add_argument(
        "--save-report",
        action="store_true",
        help="Save detailed report to .ai_onboard/",
    )

    # Report command
    report_parser = subparsers_codebase.add_parser(
        "report", help="Generate analysis report"
    )
    report_parser.add_argument(
        "--type",
        type=str,
        choices=["summary", "detailed", "recommendations"],
        default="summary",
        help="Type of report to generate",
    )

    # Organize command
    organize_parser = subparsers_codebase.add_parser(
        "organize", help="Apply organizational recommendations"
    )
    organize_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    organize_parser.add_argument(
        "--auto-apply",
        action="store_true",
        help="Automatically apply safe recommendations",
    )

    # Quality analysis command
    quality_parser = subparsers_codebase.add_parser(
        "quality", help="Analyze code quality, unused imports, and dead code"
    )
    quality_parser.add_argument(
        "--output",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    quality_parser.add_argument(
        "--save-report",
        type=str,
        help="Save quality report to specified file",
    )
    quality_parser.add_argument(
        "--exclude",
        nargs="*",
        help="Additional patterns to exclude from analysis",
    )

    # Dependency analysis command
    dependency_parser = subparsers_codebase.add_parser(
        "dependencies", help="Analyze module dependencies and relationships"
    )
    dependency_parser.add_argument(
        "--output",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    dependency_parser.add_argument(
        "--save-report",
        type=str,
        help="Save dependency report to specified file",
    )
    dependency_parser.add_argument(
        "--exclude",
        nargs="*",
        help="Additional patterns to exclude from analysis",
    )

    # Duplicate detection command
    duplicate_parser = subparsers_codebase.add_parser(
        "duplicates", help="Analyze code for duplicate blocks and patterns"
    )
    duplicate_parser.add_argument(
        "--output",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    duplicate_parser.add_argument(
        "--save-report",
        type=str,
        help="Save duplicate report to specified file",
    )
    duplicate_parser.add_argument(
        "--exclude",
        nargs="*",
        help="Additional patterns to exclude from analysis",
    )
    duplicate_parser.add_argument(
        "--min-size",
        type=int,
        default=6,
        help="Minimum block size in lines (default: 6)",
    )

    # Organization analysis command
    organization_parser = subparsers_codebase.add_parser(
        "organization", help="Analyze file organization and suggest improvements"
    )
    organization_parser.add_argument(
        "--output",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    organization_parser.add_argument(
        "--save-report",
        type=str,
        help="Save organization report to specified file",
    )
    organization_parser.add_argument(
        "--exclude",
        nargs="*",
        help="Additional patterns to exclude from analysis",
    )
    organization_parser.add_argument(
        "--max-files",
        type=int,
        default=10000,
        help="Maximum number of files to analyze (default: 10000)",
    )
    organization_parser.add_argument(
        "--max-relationship-files",
        type=int,
        default=2000,
        help="Maximum Python files to analyze for relationships (default: 2000)",
    )

    # Structural recommendations command
    recommend_parser = subparsers_codebase.add_parser(
        "recommend",
        help="Generate structural recommendations for codebase organization",
    )
    recommend_parser.add_argument(
        "--output",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    recommend_parser.add_argument(
        "--save-report",
        type=str,
        help="Save recommendations report to specified file",
    )
    recommend_parser.add_argument(
        "--exclude",
        nargs="*",
        help="Additional patterns to exclude from analysis",
    )
    recommend_parser.add_argument(
        "--max-files",
        type=int,
        default=10000,
        help="Maximum number of files to analyze (default: 10000)",
    )

    return codebase_parser


def handle_codebase_analysis_commands(args, root: Path):
    """Handle codebase analysis commands."""

    if not hasattr(args, "codebase_cmd") or not args.codebase_cmd:
        # Default to analyze all
        args.codebase_cmd = "analyze"
        args.focus = "all"

    try:
        from ..core.codebase_analysis import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer(root)

        if args.codebase_cmd == "analyze":
            results = analyzer.analyze_codebase()

            if args.focus != "all":
                results = _filter_results_by_focus(results, args.focus)

            _display_analysis_results(results, args.output)

            if args.save_report:
                _save_analysis_report(results, root)

        elif args.codebase_cmd == "report":
            import json

            from ..core.codebase_analysis import CodebaseAnalyzer

            # Load previous analysis or run new one
            report_path = root / ".ai_onboard" / "codebase_analysis.json"
            if report_path.exists():
                with open(report_path, "r") as f:
                    results = json.load(f)
                print_status("📊 Loaded previous analysis report")
            else:
                print_status("📊 No previous report found, running new analysis...")
                analyzer = CodebaseAnalyzer(root)
                results = analyzer.analyze_codebase()
                _save_analysis_report(results, root)

            _display_report(results, args.type)

        elif args.codebase_cmd == "organize":
            import json

            from ..core.codebase_analysis import CodebaseAnalyzer

            # Load analysis results
            report_path = root / ".ai_onboard" / "codebase_analysis.json"
            if not report_path.exists():
                print_status("📊 Running analysis first...")
                analyzer = CodebaseAnalyzer(root)
                results = analyzer.analyze_codebase()
                _save_analysis_report(results, root)
            else:
                with open(report_path, "r") as f:
                    results = json.load(f)

            _handle_organization(results, args.dry_run, args.auto_apply)

        elif args.codebase_cmd == "quality":
            from ..core.code_quality_analyzer import CodeQualityAnalyzer

            # Create analyzer with custom excludes if provided
            exclude_patterns = getattr(args, "exclude", None)
            analyzer = CodeQualityAnalyzer(root, exclude_patterns)

            print_status("🔍 Analyzing code quality...")
            results = analyzer.analyze_codebase()

            if args.output == "json":
                print(json.dumps(_serialize_quality_results(results), indent=2))
            else:
                report = analyzer.generate_report(results)
                print(report)

            if args.save_report:
                analyzer.generate_report(results, args.save_report)
                print_status(f"📄 Quality report saved to: {args.save_report}")

        elif args.codebase_cmd == "dependencies":
            from ..core.dependency_mapper import DependencyMapper

            # Create mapper with custom excludes if provided
            exclude_patterns = getattr(args, "exclude", None)
            mapper = DependencyMapper(root, exclude_patterns)

            print_status("🔗 Analyzing module dependencies...")
            results = mapper.analyze_dependencies()

            if args.output == "json":
                print(json.dumps(_serialize_dependency_results(results), indent=2))
            else:
                report = mapper.generate_dependency_report(results)
                print(report)

            if args.save_report:
                mapper.generate_dependency_report(results, args.save_report)
                print_status(f"📄 Dependency report saved to: {args.save_report}")

        elif args.codebase_cmd == "duplicates":
            from ..core.duplicate_detector import DuplicateDetector

            # Create detector with custom settings
            exclude_patterns = getattr(args, "exclude", None)
            min_size = getattr(args, "min_size", 6)
            detector = DuplicateDetector(root, exclude_patterns, min_size)

            print_status("🔍 Analyzing code for duplicates...")
            results = detector.analyze_duplicates()

            if args.output == "json":
                print(json.dumps(_serialize_duplicate_results(results), indent=2))
            else:
                report = detector.generate_duplicate_report(results)
                print(report)

            if args.save_report:
                detector.generate_duplicate_report(results, args.save_report)
                print_status(f"📄 Duplicate report saved to: {args.save_report}")

        elif args.codebase_cmd == "organization":
            from ..core.file_organization_analyzer import FileOrganizationAnalyzer

            # Create analyzer with custom excludes and limits if provided
            exclude_patterns = getattr(args, "exclude", None)
            max_files = getattr(args, "max_files", 10000)
            max_relationship_files = getattr(args, "max_relationship_files", 2000)
            analyzer = FileOrganizationAnalyzer(
                root, exclude_patterns, max_files, max_relationship_files
            )

            print_status("📁 Analyzing file organization...")
            results = analyzer.analyze_organization()

            if args.output == "json":
                print(json.dumps(_serialize_organization_results(results), indent=2))
            else:
                report = analyzer.generate_organization_report(results)
                print(report)

            if args.save_report:
                analyzer.generate_organization_report(results, args.save_report)
                print_status(f"📄 Organization report saved to: {args.save_report}")

        elif args.codebase_cmd == "recommend":
            from ..core.file_organization_analyzer import FileOrganizationAnalyzer
            from ..core.structural_recommendation_engine import (
                StructuralRecommendationEngine,
            )

            # First run organization analysis
            exclude_patterns = getattr(args, "exclude", None)
            max_files = getattr(args, "max_files", 10000)

            org_analyzer = FileOrganizationAnalyzer(root, exclude_patterns, max_files)
            print_status("📁 Analyzing file organization for recommendations...")
            org_result = org_analyzer.analyze_organization()

            # Generate structural recommendations
            engine = StructuralRecommendationEngine(root)
            recommendations = engine.generate_recommendations(org_result)

            if args.output == "json":
                import json

                output_data = {
                    "file_moves": [
                        {
                            "file": r.file_path,
                            "from": r.current_location,
                            "to": r.recommended_location,
                            "rationale": r.rationale,
                            "priority": r.priority,
                            "confidence": r.confidence,
                        }
                        for r in recommendations.file_moves
                    ],
                    "file_merges": [
                        {
                            "target": r.target_file,
                            "sources": r.source_files,
                            "rationale": r.rationale,
                            "priority": r.priority,
                            "confidence": r.confidence,
                            "effort": r.estimated_effort,
                        }
                        for r in recommendations.file_merges
                    ],
                    "directory_plans": [
                        {
                            "name": p.plan_name,
                            "description": p.description,
                            "actions": p.actions,
                            "benefits": p.benefits,
                            "risks": p.risks,
                            "priority": p.priority,
                            "effort": p.estimated_effort,
                        }
                        for p in recommendations.directory_plans
                    ],
                    "summary": recommendations.summary_stats,
                }

                if args.save_report:
                    with open(args.save_report, "w") as f:
                        json.dump(output_data, f, indent=2)
                    print_status(f"📄 Recommendations saved to: {args.save_report}")
                else:
                    print(json.dumps(output_data, indent=2))

            else:  # text output
                print("\n" + "=" * 80)
                print("🏗️  STRUCTURAL RECOMMENDATIONS REPORT")
                print("=" * 80)

                # Summary
                summary = recommendations.summary_stats
                print("\n📊 SUMMARY:")
                print(f"   File Move Recommendations: {summary.get('file_moves', 0)}")
                print(f"   File Merge Recommendations: {summary.get('file_merges', 0)}")
                print(
                    f"   Directory Restructuring Plans: {summary.get('directory_plans', 0)}"
                )
                print(
                    f"   High Priority Items: {summary.get('high_priority_moves', 0) + summary.get('high_priority_merges', 0) + summary.get('high_priority_plans', 0)}"
                )

                # File moves
                if recommendations.file_moves:
                    print("\n📁 FILE MOVE RECOMMENDATIONS:")
                    for i, move in enumerate(recommendations.file_moves, 1):
                        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                            move.priority, "⚪"
                        )
                        print(f"   {i}. {priority_icon} Move '{move.file_path}'")
                        print(f"      From: {move.current_location}")
                        print(f"      To: {move.recommended_location}")
                        print(f"      Rationale: {move.rationale}")
                        print(f"      Confidence: {move.confidence:.1%}")
                        print()

                # File merges
                if recommendations.file_merges:
                    print("\n🔗 FILE MERGE RECOMMENDATIONS:")
                    for i, merge in enumerate(recommendations.file_merges, 1):
                        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                            merge.priority, "⚪"
                        )
                        print(
                            f"   {i}. {priority_icon} Merge {len(merge.source_files)} files into '{merge.target_file}'"
                        )
                        print(f"      Files: {', '.join(merge.source_files)}")
                        print(f"      Rationale: {merge.rationale}")
                        print(f"      Confidence: {merge.confidence:.1%}")
                        print(f"      Estimated Effort: {merge.estimated_effort}")
                        print()

                # Directory plans
                if recommendations.directory_plans:
                    print("\n🏗️  DIRECTORY RESTRUCTURING PLANS:")
                    for i, plan in enumerate(recommendations.directory_plans, 1):
                        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                            plan.priority, "⚪"
                        )
                        print(f"   {i}. {priority_icon} {plan.plan_name}")
                        print(f"      Description: {plan.description}")
                        print(f"      Estimated Effort: {plan.estimated_effort}")
                        print(f"      Actions: {len(plan.actions)}")

                        if plan.benefits:
                            print("      Benefits:")
                            for benefit in plan.benefits:
                                print(f"        • {benefit}")

                        if plan.risks:
                            print("      Risks:")
                            for risk in plan.risks:
                                print(f"        ⚠️  {risk}")

                        print()

                if args.save_report:
                    # Save text report
                    import datetime

                    report_content = []
                    report_content.append("STRUCTURAL RECOMMENDATIONS REPORT")
                    report_content.append("=" * 50)
                    report_content.append(
                        f"Generated: {datetime.datetime.now().isoformat()}"
                    )
                    report_content.append("")
                    report_content.append(
                        f"File Move Recommendations: {summary.get('file_moves', 0)}"
                    )
                    report_content.append(
                        f"File Merge Recommendations: {summary.get('file_merges', 0)}"
                    )
                    report_content.append(
                        f"Directory Restructuring Plans: {summary.get('directory_plans', 0)}"
                    )
                    report_content.append("")

                    # Add details...
                    if recommendations.file_moves:
                        report_content.append("FILE MOVE RECOMMENDATIONS:")
                        for move in recommendations.file_moves:
                            report_content.append(
                                f"- Move '{move.file_path}' from {move.current_location} to {move.recommended_location}"
                            )
                            report_content.append(f"  Rationale: {move.rationale}")
                            report_content.append("")

                    with open(args.save_report, "w") as f:
                        f.write("\n".join(report_content))
                    print_status(f"📄 Recommendations saved to: {args.save_report}")

                print("=" * 80)

    except Exception as e:
        print_status(f"❌ Error during codebase analysis: {e}")
        return False

    return True


def _serialize_quality_results(result) -> Dict[str, Any]:
    """Serialize code quality analysis results for JSON output."""
    return {
        "files_analyzed": result.files_analyzed,
        "total_issues": result.total_issues,
        "issues_by_type": dict(result.issues_by_type),
        "issues_by_severity": dict(result.issues_by_severity),
        "overall_quality_score": result.overall_quality_score,
        "issues": [
            {
                "file_path": issue.file_path,
                "line_number": issue.line_number,
                "issue_type": issue.issue_type,
                "severity": issue.severity,
                "message": issue.message,
                "suggestion": issue.suggestion,
                "context": issue.context,
            }
            for issue in result.issues
        ],
        "file_metrics": {
            file_path: {
                "lines_of_code": metrics.lines_of_code,
                "complexity_score": metrics.complexity_score,
                "import_count": metrics.import_count,
                "function_count": metrics.function_count,
                "class_count": metrics.class_count,
                "unused_imports": metrics.unused_imports,
                "dead_code_count": metrics.dead_code_count,
                "quality_score": metrics.quality_score,
            }
            for file_path, metrics in result.file_metrics.items()
        },
    }


def _serialize_dependency_results(result) -> Dict[str, Any]:
    """Serialize dependency analysis results for JSON output."""
    return {
        "modules_analyzed": result.modules_analyzed,
        "total_dependencies": result.total_dependencies,
        "circular_dependencies": result.circular_dependencies,
        "dependency_graph": result.dependency_graph,
        "reverse_dependencies": result.reverse_dependencies,
        "strongly_connected_components": result.strongly_connected_components,
        "dependency_depths": result.dependency_depths,
        "module_metrics": {
            module_name: {
                "name": metrics.name,
                "file_path": metrics.file_path,
                "lines_of_code": metrics.lines_of_code,
                "incoming_deps": metrics.incoming_deps,
                "outgoing_deps": metrics.outgoing_deps,
                "complexity_score": metrics.complexity_score,
                "cohesion_score": metrics.cohesion_score,
                "coupling_score": metrics.coupling_score,
            }
            for module_name, metrics in result.module_metrics.items()
        },
    }


def _serialize_duplicate_results(result) -> Dict[str, Any]:
    """Serialize duplicate code analysis results for JSON output."""
    return {
        "files_analyzed": result.files_analyzed,
        "total_blocks": result.total_blocks,
        "exact_duplicates": result.exact_duplicates,
        "near_duplicates": result.near_duplicates,
        "structural_duplicates": result.structural_duplicates,
        "total_duplicate_lines": result.total_duplicate_lines,
        "duplicate_groups": [
            {
                "duplicate_type": group.duplicate_type,
                "similarity_score": group.similarity_score,
                "block_count": len(group.blocks),
                "blocks": [
                    {
                        "file_path": block.file_path,
                        "start_line": block.start_line,
                        "end_line": block.end_line,
                        "content_hash": block.content_hash,
                        "content_preview": (
                            block.content[:100] + "..."
                            if len(block.content) > 100
                            else block.content
                        ),
                    }
                    for block in group.blocks
                ],
            }
            for group in result.duplicate_groups
        ],
    }


def _serialize_organization_results(result) -> Dict[str, Any]:
    """Serialize file organization analysis results for JSON output."""
    return {
        "directories_analyzed": result.directories_analyzed,
        "files_analyzed": result.files_analyzed,
        "total_issues": result.total_issues,
        "issues_by_type": dict(result.issues_by_type),
        "issues_by_severity": dict(result.issues_by_severity),
        "organization_issues": [
            {
                "file_path": issue.file_path,
                "issue_type": issue.issue_type,
                "severity": issue.severity,
                "message": issue.message,
                "recommendation": issue.recommendation,
                "suggested_location": issue.suggested_location,
                "related_files": issue.related_files,
            }
            for issue in result.organization_issues
        ],
        "consolidation_candidates": result.consolidation_candidates,
        "restructuring_recommendations": result.restructuring_recommendations,
        "directory_analysis": {
            dir_path: {
                "file_count": analysis.file_count,
                "total_lines": analysis.total_lines,
                "file_types": dict(analysis.file_types),
                "subdirectories": analysis.subdirectories,
                "cohesion_score": analysis.cohesion_score,
                "complexity_score": analysis.complexity_score,
            }
            for dir_path, analysis in result.directory_analysis.items()
        },
    }


def _filter_results_by_focus(results: Dict[str, Any], focus: str) -> Dict[str, Any]:
    """Filter analysis results based on focus area."""
    if focus == "organization":
        return {
            "organization_issues": results.get("organization_issues", []),
            "recommendations": results.get("recommendations", {}),
            "summary": {
                "organization_issues_count": len(results.get("organization_issues", []))
            },
        }
    elif focus == "quality":
        return {
            "quality_issues": results.get("quality_issues", []),
            "summary": {"quality_issues_count": len(results.get("quality_issues", []))},
        }
    elif focus == "dependencies":
        return {
            "dependency_map": results.get("dependency_map", {}),
            "summary": {"total_modules": len(results.get("dependency_map", {}))},
        }
    elif focus == "duplicates":
        return {
            "duplicates": results.get("duplicates", []),
            "summary": {"duplicate_blocks_count": len(results.get("duplicates", []))},
        }
    else:
        return results


def _display_analysis_results(results: Dict[str, Any], output_format: str):
    """Display analysis results in the requested format."""

    if output_format == "json":
        safe_print(json.dumps(results, indent=2, default=str))
        return

    if output_format == "summary":
        _display_summary(results)
        return

    # Default text format
    print_activity("📊 CODEBASE ANALYSIS RESULTS")
    print_content("=" * 50)

    # Summary
    summary = results.get("summary", {})
    print_content(f"📈 SUMMARY:")
    print_content(f"   • Total modules analyzed: {summary.get('total_modules', 0)}")
    print_content(
        f"   • Organization issues: {summary.get('organization_issues_count', 0)}"
    )
    print_content(f"   • Code quality issues: {summary.get('quality_issues_count', 0)}")
    print_content(
        f"   • Duplicate code blocks: {summary.get('duplicate_blocks_count', 0)}"
    )
    print_content("")

    # Organization issues
    org_issues = results.get("organization_issues", [])
    if org_issues:
        print_content(f"📁 ORGANIZATION ISSUES ({len(org_issues)}):")
        for i, issue in enumerate(org_issues[:10], 1):  # Show first 10
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                issue.severity, "⚪"
            )
            print_content(
                f"   {i}. {severity_icon} {issue.file_path} - {issue.description}"
            )
            print_content(f"      💡 {issue.suggestion}")
        if len(org_issues) > 10:
            print_content(f"      ... and {len(org_issues) - 10} more issues")
        print_content("")

    # Quality issues
    quality_issues = results.get("quality_issues", [])
    if quality_issues:
        print_content(f"🔍 CODE QUALITY ISSUES ({len(quality_issues)}):")
        for i, issue in enumerate(quality_issues[:10], 1):  # Show first 10
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                issue.severity, "⚪"
            )
            file_name = (
                str(issue.file_path).split("/")[-1] if issue.file_path else "unknown"
            )
            line_info = f":{issue.line_number}" if issue.line_number else ""
            print_content(
                f"   {i}. {severity_icon} {file_name}{line_info} - {issue.description}"
            )
            print_content(f"      💡 {issue.suggestion}")
        if len(quality_issues) > 10:
            print_content(f"      ... and {len(quality_issues) - 10} more issues")
        print_content("")

    # Duplicates
    duplicates = results.get("duplicates", [])
    if duplicates:
        print_content(f"🔄 DUPLICATE CODE BLOCKS ({len(duplicates)}):")
        for i, dup in enumerate(duplicates[:5], 1):  # Show first 5
            print_content(
                f"   {i}. {dup.line_count}-line block found in {len(dup.files)} files:"
            )
            for file_info in dup.files[:3]:  # Show first 3 files
                file_path, start, end = file_info
                file_name = str(file_path).split("/")[-1] if file_path else "unknown"
                print_content(f"      • {file_name}:{start}-{end}")
            if len(dup.files) > 3:
                print_content(f"      ... and {len(dup.files) - 3} more files")
        if len(duplicates) > 5:
            print_content(f"      ... and {len(duplicates) - 5} more duplicate blocks")
        print_content("")

    # Recommendations
    recommendations = results.get("recommendations", {})
    if recommendations:
        print_content("💡 STRUCTURAL RECOMMENDATIONS:")
        for category, recs in recommendations.items():
            if recs:
                print_content(
                    f"   • {category.replace('_', ' ').title()}: {len(recs)} suggestions"
                )
        print_content("")


def _display_summary(results: Dict[str, Any]):
    """Display a concise summary of results."""
    summary = results.get("summary", {})

    print_activity("📊 CODEBASE ANALYSIS SUMMARY")
    print_content("=" * 40)
    print_content(f"Modules analyzed:     {summary.get('total_modules', 0)}")
    print_content(
        f"Organization issues:  {summary.get('organization_issues_count', 0)}"
    )
    print_content(f"Quality issues:       {summary.get('quality_issues_count', 0)}")
    print_content(f"Duplicate blocks:     {summary.get('duplicate_blocks_count', 0)}")

    severity = summary.get("severity_breakdown", {})
    if severity:
        print_content("")
        print_content("Severity breakdown:")
        org_sev = severity.get("organization", {})
        if org_sev:
            print_content(f"  Organization: {dict(org_sev)}")
        qual_sev = severity.get("quality", {})
        if qual_sev:
            print_content(f"  Quality:      {dict(qual_sev)}")


def _display_report(results: Dict[str, Any], report_type: str):
    """Display specific type of report."""

    if report_type == "summary":
        _display_summary(results)

    elif report_type == "detailed":
        _display_analysis_results(results, "text")

    elif report_type == "recommendations":
        recommendations = results.get("recommendations", {})
        print_activity("💡 STRUCTURAL RECOMMENDATIONS REPORT")
        print_content("=" * 50)

        if not recommendations:
            print_content("No recommendations available. Run analysis first.")
            return

        for category, recs in recommendations.items():
            if recs:
                print_content(f"📋 {category.replace('_', ' ').title()}:")
                for i, rec in enumerate(recs, 1):
                    print_content(
                        f"   {i}. {rec.get('issue', rec.get('suggestion', str(rec)))}"
                    )
                    if "suggestion" in rec and rec["suggestion"] != rec.get("issue"):
                        print_content(f"      💡 {rec['suggestion']}")
                print_content("")


def _handle_organization(results: Dict[str, Any], dry_run: bool, auto_apply: bool):
    """Handle organization recommendations."""

    print_activity("🔧 CODEBASE ORGANIZATION")
    print_content("=" * 40)

    if dry_run:
        print_status("🔍 DRY RUN MODE - No changes will be made")

    recommendations = results.get("recommendations", {})

    if not recommendations:
        print_content("No organization recommendations available.")
        return

    # Display recommendations
    total_suggestions = sum(len(recs) for recs in recommendations.values())
    print_content(f"Found {total_suggestions} organization suggestions")

    for category, recs in recommendations.items():
        if recs:
            print_content(
                f"\n📋 {category.replace('_', ' ').title()} ({len(recs)} suggestions):"
            )
            for i, rec in enumerate(recs, 1):
                print_content(
                    f"   {i}. {rec.get('issue', rec.get('suggestion', str(rec)))}"
                )

                if auto_apply and not dry_run:
                    # For now, just log that we would apply
                    print_content(
                        f"      ✅ Would apply: {rec.get('suggestion', 'N/A')}"
                    )
                elif dry_run:
                    print_content(
                        f"      🔍 Would apply: {rec.get('suggestion', 'N/A')}"
                    )

    if auto_apply and not dry_run:
        print_status("✅ Organization complete")
    elif dry_run:
        print_status("🔍 Dry run complete - use --auto-apply to make changes")


def _save_analysis_report(results: Dict[str, Any], root: Path):
    """Save analysis results to a JSON file."""
    report_dir = root / ".ai_onboard"
    report_dir.mkdir(exist_ok=True)

    report_path = report_dir / "codebase_analysis.json"

    # Convert Path objects and dataclasses to serializable format
    def serialize_results(obj):
        if isinstance(obj, Path):
            return str(obj)
        # Handle dataclasses by converting to dict
        if hasattr(obj, "__dataclass_fields__"):
            result = {}
            for k, v in obj.__dict__.items():
                try:
                    result[k] = serialize_results(v)
                except TypeError:
                    # If serialization fails for any field, convert to string
                    result[k] = str(v)
            return result
        # Handle other types
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        if isinstance(obj, (list, tuple)):
            return [serialize_results(item) for item in obj]
        if isinstance(obj, dict):
            return {k: serialize_results(v) for k, v in obj.items()}
        # For any other type, convert to string
        return str(obj)

    try:
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2, default=serialize_results)
        print_status(f"💾 Report saved to {report_path}")
    except Exception as e:
        print_status(f"❌ Failed to save report: {e}")
