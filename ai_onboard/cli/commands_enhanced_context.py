"""
CLI commands for Enhanced Conversation Context Management.

This module provides command - line interfaces for:
- Managing conversation context memories
- Cross - session context tracking
- Context sharing between AI agents
- Context continuity analysis
"""

import argparse
import time
from pathlib import Path
from typing import Any

from ..core.ai_integration.enhanced_conversation_context import (
    get_enhanced_context_manager,
)


def add_enhanced_context_commands(subparsers):
    """Add enhanced conversation context commands to the CLI."""

    # Main enhanced context command
    context_parser = subparsers.add_parser(
        "enhanced - context",
        help="Enhanced conversation context management for AI agents",
    )
    context_sub = context_parser.add_subparsers(dest="context_cmd", required=True)

    # Enhance session command
    enhance_parser = context_sub.add_parser(
        "enhance", help="Enhance a session with cross - session context and memories"
    )
    enhance_parser.add_argument(
        "--session - id", required=True, help="Session ID to enhance"
    )

    # Create memory command
    memory_parser = context_sub.add_parser("memory", help="Context memory management")
    memory_sub = memory_parser.add_subparsers(dest="memory_action", required=True)

    # Create memory
    create_memory_parser = memory_sub.add_parser(
        "create", help="Create a new context memory"
    )
    create_memory_parser.add_argument(
        "--session - id", required=True, help="Session ID"
    )
    create_memory_parser.add_argument("--user - id", required=True, help="User ID")
    create_memory_parser.add_argument("--topic", required=True, help="Memory topic")
    create_memory_parser.add_argument(
        "--facts", nargs="+", required=True, help="Key facts"
    )
    create_memory_parser.add_argument(
        "--importance",
        choices=["low", "normal", "high", "critical"],
        default="normal",
        help="Memory importance level",
    )

    # List memories
    list_memory_parser = memory_sub.add_parser("list", help="List context memories")
    list_memory_parser.add_argument("--user - id", help="Filter by user ID")
    list_memory_parser.add_argument("--topic", help="Filter by topic")
    list_memory_parser.add_argument(
        "--limit", type=int, default=20, help="Limit results"
    )

    # Share context command
    share_parser = context_sub.add_parser(
        "share", help="Share context with another AI agent"
    )
    share_parser.add_argument(
        "--session - id", required=True, help="Session ID to share"
    )
    share_parser.add_argument("--target - agent", required=True, help="Target agent ID")
    share_parser.add_argument(
        "--context - types",
        nargs="+",
        choices=[
            "conversation_history",
            "user_preferences",
            "project_context",
            "error_patterns",
        ],
        default=["conversation_history", "project_context"],
        help="Types of context to share",
    )

    # Continuity command
    continuity_parser = context_sub.add_parser(
        "continuity", help="Get context continuity summary"
    )
    continuity_parser.add_argument("--user - id", required=True, help="User ID")

    # Context graph command
    graph_parser = context_sub.add_parser("graph", help="Context relationship analysis")
    graph_sub = graph_parser.add_subparsers(dest="graph_action", required=True)

    # Show relationships
    graph_sub.add_parser("show", help="Show context relationship graph")

    # Find patterns
    patterns_parser = graph_sub.add_parser(
        "patterns", help="Find conversation patterns"
    )
    patterns_parser.add_argument("--user - id", help="Filter by user ID")
    patterns_parser.add_argument("--days", type=int, default=7, help="Days to analyze")

    # Analytics command
    analytics_parser = context_sub.add_parser(
        "analytics", help="Context analytics and insights"
    )
    analytics_sub = analytics_parser.add_subparsers(
        dest="analytics_action", required=True
    )

    # User insights
    insights_parser = analytics_sub.add_parser(
        "insights", help="Get user behavior insights"
    )
    insights_parser.add_argument("--user - id", required=True, help="User ID")

    # System stats
    analytics_sub.add_parser("stats", help="Get system - wide context statistics")

    # Cleanup command
    cleanup_parser = context_sub.add_parser("cleanup", help="Clean up old context data")
    cleanup_parser.add_argument(
        "--days", type=int, default=30, help="Keep data newer than N days"
    )
    cleanup_parser.add_argument(
        "--dry - run", action="store_true", help="Show what would be cleaned up"
    )


def handle_enhanced_context_commands(args: argparse.Namespace, root: Path) -> None:
    """Handle enhanced conversation context commands."""

    context_manager = get_enhanced_context_manager(root)

    if args.context_cmd == "enhance":
        _handle_enhance_session(args, context_manager)
    elif args.context_cmd == "memory":
        _handle_memory_commands(args, context_manager)
    elif args.context_cmd == "share":
        _handle_share_context(args, context_manager)
    elif args.context_cmd == "continuity":
        _handle_continuity_summary(args, context_manager)
    elif args.context_cmd == "graph":
        _handle_graph_commands(args, context_manager)
    elif args.context_cmd == "analytics":
        _handle_analytics_commands(args, context_manager)
    elif args.context_cmd == "cleanup":
        _handle_cleanup(args, context_manager)
    else:
        print(f"Unknown enhanced context command: {args.context_cmd}")


def _handle_enhance_session(args: argparse.Namespace, context_manager) -> None:
    """Handle session enhancement command."""
    print(f"🔍 Enhancing session context: {args.session_id}")

    result = context_manager.enhance_session_context(args.session_id)

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    print("✅ Session enhanced successfully!")
    print("\n📊 Enhanced Context Summary:")
    print("=" * 50)

    # Base session info
    base = result["base_session"]
    print(f"Session ID: {base['session_id']}")
    print(f"User ID: {base['user_id']}")
    print(f"State: {base['state']}")
    print(f"Conversation Rounds: {base['conversation_rounds']}")

    # Cross - session insights
    insights = result["cross_session_insights"]
    print(f"\n🧠 Cross - Session Insights:")
    print(f"Communication Style: {insights['communication_style']}")
    expertise = (
        ", ".join(insights["expertise_areas"])
        if insights["expertise_areas"]
        else "None identified"
    )
    print(f"Expertise Areas: {expertise}")

    if insights["preferred_commands"]:
        print(
            f"Top Commands: {', '.join(list(insights['preferred_commands'].keys())[:5])}"
        )

    # Relevant memories
    memories = result["relevant_memories"]
    print(f"\n💭 Relevant Memories: {len(memories)}")
    for memory in memories[:3]:  # Show top 3
        print(f"  • {memory['topic']} (relevance: {memory['relevance_score']:.2f})")
        print(f"    Facts: {', '.join(memory['key_facts'][:2])}")

    # Related sessions
    related = result["related_sessions"]
    print(f"\n🔗 Related Sessions: {len(related)}")
    for session in related[:3]:  # Show top 3
        print(f"  • {session['session_id']} ({session['conversation_rounds']} rounds)")

    # Context quality
    quality = result["context_quality"]
    print(f"\n📈 Context Quality:")
    print(f"Memory Count: {quality['memory_count']}")
    print(f"Related Sessions: {quality['related_sessions_count']}")
    print(f"User Experience: {quality.get('user_experience_level', 'unknown')}")


def _handle_memory_commands(args: argparse.Namespace, context_manager) -> None:
    """Handle memory management commands."""

    if args.memory_action == "create":
        print(f"💭 Creating context memory...")

        memory_id = context_manager.create_context_memory(
            session_id=args.session_id,
            user_id=args.user_id,
            topic=args.topic,
            key_facts=args.facts,
            importance=args.importance,
        )

        if memory_id:
            print(f"✅ Context memory created: {memory_id}")
            print(f"Topic: {args.topic}")
            print(f"Facts: {', '.join(args.facts)}")
            print(f"Importance: {args.importance}")
        else:
            print("❌ Failed to create context memory")

    elif args.memory_action == "list":
        print("📋 Context Memories:")
        print("=" * 40)

        # Get all memories
        memories = list(context_manager.memories.values())

        # Apply filters
        if args.user_id:
            memories = [m for m in memories if m.user_id == args.user_id]
        if args.topic:
            memories = [m for m in memories if args.topic.lower() in m.topic.lower()]

        # Sort by creation time (newest first)
        memories.sort(key=lambda m: m.created_at, reverse=True)

        # Apply limit
        memories = memories[: args.limit]

        if not memories:
            print("No memories found matching criteria")
            return

        for memory in memories:
            age_hours = (time.time() - memory.created_at) / 3600
            print(f"\n💭 {memory.memory_id}")
            print(f"   Topic: {memory.topic}")
            print(f"   User: {memory.user_id}")
            print(f"   Facts: {', '.join(memory.key_facts[:3])}")
            print(f"   Importance: {memory.importance_level}")
            print(f"   Age: {age_hours:.1f} hours")
            print(f"   Accessed: {memory.access_count} times")


def _handle_share_context(args: argparse.Namespace, context_manager) -> None:
    """Handle context sharing command."""
    print(f"🤝 Sharing context with agent: {args.target_agent}")

    result = context_manager.share_context_with_agent(
        session_id=args.session_id,
        target_agent_id=args.target_agent,
        context_types=args.context_types,
    )

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    print("✅ Context shared successfully!")

    metadata = result["sharing_metadata"]
    print(f"\n📊 Sharing Summary:")
    print(f"Target Agent: {metadata['agent_id']}")
    print(f"Session ID: {metadata['session_id']}")
    print(f"Context Types: {', '.join(metadata['context_types'])}")
    print(f"Shared Items: {metadata['filtered_items']}")
    print(f"Shared At: {time.ctime(metadata['shared_at'])}")

    # Show shared context summary
    shared_context = result["shared_context"]
    print(f"\n🔗 Shared Context:")
    for context_type, data in shared_context.items():
        if isinstance(data, list):
            print(f"  {context_type}: {len(data)} items")
        elif isinstance(data, dict):
            print(f"  {context_type}: {len(data)} properties")
        else:
            print(f"  {context_type}: {type(data).__name__}")


def _handle_continuity_summary(args: argparse.Namespace, context_manager) -> None:
    """Handle context continuity summary command."""
    print(f"📈 Context Continuity Summary for: {args.user_id}")

    result = context_manager.get_context_continuity_summary(args.user_id)

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    print("=" * 50)

    # Continuity metrics
    metrics = result["continuity_metrics"]
    print(f"📊 Continuity Metrics:")
    print(f"  Total Sessions: {metrics['total_sessions']}")
    print(f"  Recent Sessions (24h): {metrics['recent_sessions']}")
    print(f"  Total Memories: {metrics['total_memories']}")
    print(f"  Avg Session Length: {metrics['avg_session_length']} rounds")

    # User profile
    profile = result["user_profile"]
    print(f"\n👤 User Profile:")
    print(f"  Communication Style: {profile['communication_style']}")
    print(f"  Collaboration Mode: {profile['collaboration_mode']}")
    print(f"  Experience Level: {profile['experience_level']}")

    # Expertise areas
    if metrics["expertise_areas"]:
        print(f"  Expertise Areas: {', '.join(metrics['expertise_areas'])}")

    # Preferred commands
    if metrics["preferred_commands"]:
        print(f"\n🔧 Top Commands:")
        for cmd, count in metrics["preferred_commands"].items():
            print(f"  • {cmd}: {count} times")

    # Recent insights
    insights = result["recent_insights"]
    if insights:
        print(f"\n💡 Recent Insights:")
        for insight in insights:
            print(f"  • {insight['topic']}")
            print(f"    Facts: {', '.join(insight['key_facts'])}")
            print(f"    Created: {time.ctime(insight['created_at'])}")


def _handle_graph_commands(args: argparse.Namespace, context_manager) -> None:
    """Handle context graph commands."""

    if args.graph_action == "show":
        print("🕸️ Context Relationship Graph:")
        print("=" * 40)

        if not context_manager.context_graph:
            print("No context relationships found")
            return

        for session_id, related_ids in context_manager.context_graph.items():
            print(f"\n📍 {session_id}")
            for related_id in related_ids:
                print(f"  └─ {related_id}")

    elif args.graph_action == "patterns":
        print("🔍 Conversation Patterns Analysis:")
        print("=" * 40)

        # This would implement pattern analysis
        # For now, show a placeholder
        print("Pattern analysis coming soon...")
        print("This will analyze:")
        print("• Common conversation flows")
        print("• Recurring topics and themes")
        print("• User behavior patterns")
        print("• Success / failure patterns")


def _handle_analytics_commands(args: argparse.Namespace, context_manager) -> None:
    """Handle analytics commands."""

    if args.analytics_action == "insights":
        print(f"🔍 User Behavior Insights: {args.user_id}")

        # Get continuity summary as base for insights
        summary = context_manager.get_context_continuity_summary(args.user_id)

        if "error" in summary:
            print(f"❌ Error: {summary['error']}")
            return

        print("=" * 50)

        metrics = summary["continuity_metrics"]
        profile = summary["user_profile"]

        # Behavioral insights
        print("🧠 Behavioral Insights:")

        if metrics["total_sessions"] > 10:
            print("  • Experienced user with consistent engagement")
        elif metrics["total_sessions"] > 3:
            print("  • Regular user building familiarity")
        else:
            print("  • New user exploring the system")

        if metrics["avg_session_length"] > 5:
            print("  • Tends to have detailed conversations")
        elif metrics["avg_session_length"] > 2:
            print("  • Balanced conversation style")
        else:
            print("  • Prefers brief, focused interactions")

        if profile["experience_level"] == "expert":
            print("  • Expert user with deep system knowledge")
        elif profile["experience_level"] == "intermediate":
            print("  • Intermediate user with growing expertise")
        else:
            print("  • Learning user developing skills")

        # Command preferences
        if metrics["preferred_commands"]:
            top_command = list(metrics["preferred_commands"].keys())[0]
            print(f"  • Most used command: {top_command}")

    elif args.analytics_action == "stats":
        print("📊 System - wide Context Statistics:")
        print("=" * 40)

        total_memories = len(context_manager.memories)
        total_cross_contexts = len(context_manager.cross_session_contexts)
        total_sharing_profiles = len(context_manager.sharing_profiles)

        print(f"Total Memories: {total_memories}")
        print(f"Cross - session Contexts: {total_cross_contexts}")
        print(f"Sharing Profiles: {total_sharing_profiles}")
        print(f"Context Relationships: {len(context_manager.context_graph)}")

        # Memory breakdown by importance
        if total_memories > 0:
            importance_counts: dict[str, Any] = {}
            for memory in context_manager.memories.values():
                importance_counts[memory.importance_level] = (
                    importance_counts.get(memory.importance_level, 0) + 1
                )

            print(f"\nMemory Importance Breakdown:")
            for importance, count in importance_counts.items():
                print(f"  {importance}: {count}")


def _handle_cleanup(args: argparse.Namespace, context_manager) -> None:
    """Handle context cleanup command."""
    print(f"🧹 Context Cleanup (keeping data newer than {args.days} days)")

    cutoff_time = time.time() - (args.days * 24 * 3600)

    # Find old memories
    old_memories = [
        memory
        for memory in context_manager.memories.values()
        if memory.created_at < cutoff_time
    ]

    # Find old cross - session contexts
    old_contexts = [
        context
        for context in context_manager.cross_session_contexts.values()
        if context.created_at < cutoff_time
    ]

    if args.dry_run:
        print("🔍 Dry Run - Items that would be cleaned up:")
        print(f"  Old Memories: {len(old_memories)}")
        print(f"  Old Cross - session Contexts: {len(old_contexts)}")

        if old_memories:
            print("\nOld Memories:")
            for memory in old_memories[:5]:  # Show first 5
                age_days = (time.time() - memory.created_at) / 86400
                print(f"  • {memory.topic} ({age_days:.1f} days old)")
    else:
        # Perform actual cleanup
        cleaned_memories = 0
        cleaned_contexts = 0

        # Remove old memories
        for memory in old_memories:
            if memory.importance_level != "critical":  # Keep critical memories
                del context_manager.memories[memory.memory_id]
                cleaned_memories += 1

        # Remove old contexts (but keep if they have recent activity)
        for context in old_contexts:
            if context.last_updated < cutoff_time:
                del context_manager.cross_session_contexts[context.user_id]
                cleaned_contexts += 1

        # Save changes
        context_manager._save_persistent_data()

        print(f"✅ Cleanup completed:")
        print(f"  Cleaned Memories: {cleaned_memories}")
        print(f"  Cleaned Contexts: {cleaned_contexts}")
        print(f"  Critical memories preserved")
