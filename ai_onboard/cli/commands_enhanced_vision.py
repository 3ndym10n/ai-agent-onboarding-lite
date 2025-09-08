"""
Enhanced Vision Interrogation CLI Commands.

This module provides CLI commands for the enhanced vision interrogation system,
including web interface management and advanced interrogation features.
"""

import argparse
from pathlib import Path
from typing import Dict, Any, List

from ..core.enhanced_vision_interrogator import (
    get_enhanced_vision_interrogator,
    ProjectType
)
from ..core.vision_web_interface import start_vision_web_interface
from ..core import utils


def handle_enhanced_vision_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle enhanced vision interrogation commands."""
    if args.enhanced_vision_cmd == "start":
        _handle_start_enhanced_interrogation(args, root)
    elif args.enhanced_vision_cmd == "web":
        _handle_web_interface(args, root)
    elif args.enhanced_vision_cmd == "status":
        _handle_enhanced_status(args, root)
    elif args.enhanced_vision_cmd == "analyze":
        _handle_analyze_responses(args, root)
    elif args.enhanced_vision_cmd == "export":
        _handle_export_results(args, root)
    elif args.enhanced_vision_cmd == "templates":
        _handle_manage_templates(args, root)
    else:
        print(f"Unknown enhanced vision command: {args.enhanced_vision_cmd}")


def _handle_start_enhanced_interrogation(args: argparse.Namespace, root: Path) -> None:
    """Start enhanced vision interrogation."""
    interrogator = get_enhanced_vision_interrogator(root)
    
    # Determine project type
    project_type = ProjectType.GENERIC
    if args.project_type:
        try:
            project_type = ProjectType(args.project_type)
        except ValueError:
            print(f"Invalid project type: {args.project_type}")
            print(f"Available types: {', '.join([pt.value for pt in ProjectType])}")
            return
    
    # Start interrogation
    result = interrogator.start_enhanced_interrogation(project_type)
    
    if result["status"] == "enhanced_interrogation_started":
        print("🎯 Enhanced Vision Interrogation Started!")
        print(f"Project Type: {result['project_type']}")
        print(f"Current Phase: {result['current_phase']}")
        print(f"Session ID: {result['session_id']}")
        print()
        print("Next Steps:")
        print("1. Run 'ai_onboard enhanced-vision web' to open the web interface")
        print("2. Or use 'ai_onboard enhanced-vision status' to check progress")
    else:
        print(f"Failed to start interrogation: {result.get('message', 'Unknown error')}")


def _handle_web_interface(args: argparse.Namespace, root: Path) -> None:
    """Start the web interface for vision interrogation."""
    port = args.port or 8080
    
    print(f"🌐 Starting Vision Interrogation Web Interface on port {port}...")
    
    result = start_vision_web_interface(root, port)
    
    if result["status"] == "success":
        print(f"✅ Web interface started successfully!")
        print(f"URL: {result['url']}")
        print()
        print("The web interface should open automatically in your browser.")
        print("If it doesn't, please open the URL manually.")
        print()
        print("Press Ctrl+C to stop the web interface.")
        
        try:
            # Keep the server running
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Web interface stopped.")
    else:
        print(f"❌ Failed to start web interface: {result['message']}")


def _handle_enhanced_status(args: argparse.Namespace, root: Path) -> None:
    """Show enhanced interrogation status."""
    interrogator = get_enhanced_vision_interrogator(root)
    
    status = interrogator.get_enhanced_interrogation_status()
    
    if status["status"] == "no_interrogation":
        print("📋 No enhanced vision interrogation found.")
        print("Run 'ai_onboard enhanced-vision start' to begin.")
        return
    
    print("📊 Enhanced Vision Interrogation Status")
    print("=" * 50)
    print(f"Status: {status['status']}")
    print(f"Project Type: {status['project_type']}")
    print(f"Current Phase: {status['current_phase']}")
    print(f"Vision Quality Score: {status['vision_quality_score']:.1%}")
    print(f"Session ID: {status['session_id']}")
    
    if status['started_at']:
        print(f"Started: {status['started_at']}")
    
    if status['completed_at']:
        print(f"Completed: {status['completed_at']}")
    
    print(f"Phases Completed: {', '.join(status['phases_completed']) if status['phases_completed'] else 'None'}")
    print(f"Insights Generated: {status['insights_count']}")
    print(f"Ambiguities Identified: {status['ambiguities_count']}")
    print(f"Adaptive Questions: {status['adaptive_questions_count']}")
    
    # Show final quality report if available
    if status.get('final_quality_report'):
        report = status['final_quality_report']
        print()
        print("📈 Final Vision Quality Report")
        print("-" * 30)
        print(f"Overall Score: {report['overall_score']:.1%}")
        print(f"Total Insights: {report['insight_summary']['total_insights']}")
        print(f"Actionable Insights: {report['insight_summary']['actionable_insights']}")
        print(f"Total Ambiguities: {report['ambiguity_summary']['total_ambiguities']}")
        print(f"Unresolved Ambiguities: {report['ambiguity_summary']['unresolved']}")
        
        if report.get('recommendations'):
            print()
            print("💡 Recommendations:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")


def _handle_analyze_responses(args: argparse.Namespace, root: Path) -> None:
    """Analyze responses and generate insights."""
    interrogator = get_enhanced_vision_interrogator(root)
    
    # Read interrogation data
    interrogation_data = utils.read_json(interrogator.interrogation_path, default={})
    
    if not interrogation_data:
        print("❌ No interrogation data found.")
        return
    
    print("🔍 Response Analysis")
    print("=" * 30)
    
    responses = interrogation_data.get("responses", {})
    insights = interrogation_data.get("insights", [])
    ambiguities = interrogation_data.get("ambiguities", [])
    
    # Analyze by phase
    for phase, phase_responses in responses.items():
        print(f"\n📋 Phase: {phase.replace('_', ' ').title()}")
        print("-" * 20)
        
        for question_id, response_data in phase_responses.items():
            response = response_data.get("response", {})
            confidence = response.get("confidence", 0.5)
            answer = response.get("answer", "")
            
            print(f"Question: {question_id}")
            print(f"Confidence: {confidence:.1%}")
            print(f"Answer Length: {len(answer)} characters")
            
            # Show metadata if available
            metadata = response_data.get("analysis_metadata", {})
            if metadata:
                print(f"Word Count: {metadata.get('word_count', 0)}")
                print(f"Technical Terms: {'Yes' if metadata.get('contains_technical_terms') else 'No'}")
                print(f"Business Terms: {'Yes' if metadata.get('contains_business_terms') else 'No'}")
                print(f"User Terms: {'Yes' if metadata.get('contains_user_terms') else 'No'}")
            
            print()
    
    # Show insights summary
    if insights:
        print("💡 Insights Summary")
        print("-" * 20)
        
        insight_categories = {}
        for insight in insights:
            category = insight.get("category", "other")
            if category not in insight_categories:
                insight_categories[category] = []
            insight_categories[category].append(insight)
        
        for category, category_insights in insight_categories.items():
            print(f"\n{category.replace('_', ' ').title()}: {len(category_insights)} insights")
            for insight in category_insights[:3]:  # Show first 3
                print(f"  • {insight.get('description', 'No description')}")
    
    # Show ambiguities summary
    if ambiguities:
        print("\n⚠️ Ambiguities Summary")
        print("-" * 20)
        
        ambiguity_priorities = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for ambiguity in ambiguities:
            priority = ambiguity.get("priority", "medium")
            ambiguity_priorities[priority] += 1
        
        for priority, count in ambiguity_priorities.items():
            if count > 0:
                print(f"{priority.title()}: {count} ambiguities")


def _handle_export_results(args: argparse.Namespace, root: Path) -> None:
    """Export interrogation results."""
    interrogator = get_enhanced_vision_interrogator(root)
    
    # Read interrogation data
    interrogation_data = utils.read_json(interrogator.interrogation_path, default={})
    
    if not interrogation_data:
        print("❌ No interrogation data found.")
        return
    
    # Determine output format
    output_format = args.format or "json"
    output_file = args.output or f"vision_interrogation_results.{output_format}"
    
    if output_format == "json":
        utils.write_json(Path(output_file), interrogation_data)
    elif output_format == "markdown":
        _export_to_markdown(interrogation_data, Path(output_file))
    elif output_format == "html":
        _export_to_html(interrogation_data, Path(output_file))
    else:
        print(f"❌ Unsupported format: {output_format}")
        return
    
    print(f"✅ Results exported to: {output_file}")


def _handle_manage_templates(args: argparse.Namespace, root: Path) -> None:
    """Manage question templates."""
    if args.template_action == "list":
        _list_templates()
    elif args.template_action == "show":
        _show_template(args.template_name)
    elif args.template_action == "create":
        _create_template(args.template_name, args.template_file)
    else:
        print(f"Unknown template action: {args.template_action}")


def _list_templates():
    """List available question templates."""
    print("📋 Available Question Templates")
    print("=" * 35)
    
    from ..core.enhanced_vision_interrogator import ProjectType
    
    for project_type in ProjectType:
        print(f"• {project_type.value.replace('_', ' ').title()}")
    
    print()
    print("Use 'ai_onboard enhanced-vision templates show <template_name>' to view details.")


def _show_template(template_name: str):
    """Show details of a specific template."""
    try:
        project_type = ProjectType(template_name)
        interrogator = get_enhanced_vision_interrogator(Path.cwd())
        
        print(f"📋 Template: {template_name.replace('_', ' ').title()}")
        print("=" * 40)
        
        template = interrogator.question_templates.get(project_type, {})
        
        for phase, questions in template.items():
            print(f"\n📌 Phase: {phase.replace('_', ' ').title()}")
            print("-" * 25)
            
            for question in questions:
                print(f"• {question.text}")
                print(f"  Type: {question.question_type.value}")
                print(f"  Required: {'Yes' if question.required else 'No'}")
                print(f"  Category: {question.category}")
                if question.insight_triggers:
                    print(f"  Insight Triggers: {', '.join(question.insight_triggers)}")
                print()
    
    except ValueError:
        print(f"❌ Invalid template name: {template_name}")
        print("Use 'ai_onboard enhanced-vision templates list' to see available templates.")


def _create_template(template_name: str, template_file: str):
    """Create a new question template from file."""
    print(f"Creating template '{template_name}' from file '{template_file}'...")
    # Implementation would go here
    print("Template creation not yet implemented.")


def _export_to_markdown(interrogation_data: Dict[str, Any], output_file: Path) -> None:
    """Export interrogation results to Markdown format."""
    markdown_content = []
    
    # Header
    markdown_content.append("# Vision Interrogation Results")
    markdown_content.append("")
    markdown_content.append(f"**Project Type:** {interrogation_data.get('project_type', 'Unknown')}")
    markdown_content.append(f"**Status:** {interrogation_data.get('status', 'Unknown')}")
    markdown_content.append(f"**Vision Quality Score:** {interrogation_data.get('vision_quality_score', 0):.1%}")
    markdown_content.append("")
    
    # Responses
    responses = interrogation_data.get("responses", {})
    for phase, phase_responses in responses.items():
        markdown_content.append(f"## {phase.replace('_', ' ').title()}")
        markdown_content.append("")
        
        for question_id, response_data in phase_responses.items():
            response = response_data.get("response", {})
            answer = response.get("answer", "")
            confidence = response.get("confidence", 0.5)
            
            markdown_content.append(f"### {question_id}")
            markdown_content.append(f"**Confidence:** {confidence:.1%}")
            markdown_content.append("")
            markdown_content.append(answer)
            markdown_content.append("")
    
    # Insights
    insights = interrogation_data.get("insights", [])
    if insights:
        markdown_content.append("## Insights")
        markdown_content.append("")
        
        for insight in insights:
            markdown_content.append(f"### {insight.get('type', 'Unknown')}")
            markdown_content.append(f"**Category:** {insight.get('category', 'Unknown')}")
            markdown_content.append(f"**Confidence:** {insight.get('confidence', 0):.1%}")
            markdown_content.append("")
            markdown_content.append(insight.get('description', ''))
            markdown_content.append("")
    
    # Write to file
    output_file.write_text("\n".join(markdown_content))


def _export_to_html(interrogation_data: Dict[str, Any], output_file: Path) -> None:
    """Export interrogation results to HTML format."""
    html_content = []
    
    # HTML header
    html_content.append("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vision Interrogation Results</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #4f46e5; }
        h2 { color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
        h3 { color: #374151; }
        .metadata { background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .response { background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
        .confidence { font-weight: bold; color: #059669; }
        .insight { background: #ecfdf5; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #10b981; }
    </style>
</head>
<body>
    """)
    
    # Title and metadata
    html_content.append("<h1>🎯 Vision Interrogation Results</h1>")
    html_content.append('<div class="metadata">')
    html_content.append(f"<p><strong>Project Type:</strong> {interrogation_data.get('project_type', 'Unknown')}</p>")
    html_content.append(f"<p><strong>Status:</strong> {interrogation_data.get('status', 'Unknown')}</p>")
    html_content.append(f"<p><strong>Vision Quality Score:</strong> {interrogation_data.get('vision_quality_score', 0):.1%}</p>")
    html_content.append("</div>")
    
    # Responses
    responses = interrogation_data.get("responses", {})
    for phase, phase_responses in responses.items():
        html_content.append(f"<h2>{phase.replace('_', ' ').title()}</h2>")
        
        for question_id, response_data in phase_responses.items():
            response = response_data.get("response", {})
            answer = response.get("answer", "")
            confidence = response.get("confidence", 0.5)
            
            html_content.append('<div class="response">')
            html_content.append(f"<h3>{question_id}</h3>")
            html_content.append(f'<p class="confidence">Confidence: {confidence:.1%}</p>')
            html_content.append(f"<p>{answer}</p>")
            html_content.append("</div>")
    
    # Insights
    insights = interrogation_data.get("insights", [])
    if insights:
        html_content.append("<h2>💡 Insights</h2>")
        
        for insight in insights:
            html_content.append('<div class="insight">')
            html_content.append(f"<h3>{insight.get('type', 'Unknown')}</h3>")
            html_content.append(f"<p><strong>Category:</strong> {insight.get('category', 'Unknown')}</p>")
            html_content.append(f"<p><strong>Confidence:</strong> {insight.get('confidence', 0):.1%}</p>")
            html_content.append(f"<p>{insight.get('description', '')}</p>")
            html_content.append("</div>")
    
    # HTML footer
    html_content.append("</body></html>")
    
    # Write to file
    output_file.write_text("\n".join(html_content))


def add_enhanced_vision_parser(subparsers) -> None:
    """Add enhanced vision interrogation commands to the argument parser."""
    enhanced_vision_parser = subparsers.add_parser(
        "enhanced-vision",
        help="Enhanced vision interrogation system"
    )
    
    enhanced_vision_subparsers = enhanced_vision_parser.add_subparsers(
        dest="enhanced_vision_cmd",
        help="Enhanced vision commands"
    )
    
    # Start command
    start_parser = enhanced_vision_subparsers.add_parser(
        "start",
        help="Start enhanced vision interrogation"
    )
    start_parser.add_argument(
        "--project-type",
        choices=[pt.value for pt in ProjectType],
        help="Project type for template-based questioning"
    )
    
    # Web interface command
    web_parser = enhanced_vision_subparsers.add_parser(
        "web",
        help="Start web interface for vision interrogation"
    )
    web_parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for web interface (default: 8080)"
    )
    
    # Status command
    enhanced_vision_subparsers.add_parser(
        "status",
        help="Show enhanced interrogation status"
    )
    
    # Analyze command
    enhanced_vision_subparsers.add_parser(
        "analyze",
        help="Analyze responses and generate insights"
    )
    
    # Export command
    export_parser = enhanced_vision_subparsers.add_parser(
        "export",
        help="Export interrogation results"
    )
    export_parser.add_argument(
        "--format",
        choices=["json", "markdown", "html"],
        default="json",
        help="Export format (default: json)"
    )
    export_parser.add_argument(
        "--output",
        help="Output file path"
    )
    
    # Templates command
    templates_parser = enhanced_vision_subparsers.add_parser(
        "templates",
        help="Manage question templates"
    )
    templates_subparsers = templates_parser.add_subparsers(
        dest="template_action",
        help="Template actions"
    )
    
    templates_subparsers.add_parser(
        "list",
        help="List available templates"
    )
    
    show_parser = templates_subparsers.add_parser(
        "show",
        help="Show template details"
    )
    show_parser.add_argument(
        "template_name",
        help="Template name to show"
    )
    
    create_parser = templates_subparsers.add_parser(
        "create",
        help="Create new template"
    )
    create_parser.add_argument(
        "template_name",
        help="Name for new template"
    )
    create_parser.add_argument(
        "template_file",
        help="Template definition file"
    )
