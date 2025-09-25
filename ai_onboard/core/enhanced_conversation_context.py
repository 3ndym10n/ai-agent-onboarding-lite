"""
Enhanced Conversation Context Management (T8) - Advanced context tracking for AI agents.

This module provides enhanced conversation context management capabilities specifically
designed for seamless AI agent collaboration,
    including context sharing, memory persistence,
and cross - session continuity.
"""

import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import utils
from .session_storage import SessionStorageManager
from .unified_metrics_collector import (
    MetricCategory,
    MetricEvent,
    MetricSource,
    get_unified_metrics_collector,
)


@dataclass
class ContextMemory:
    """Enhanced memory structure for conversation context."""

    memory_id: str
    session_id: str
    user_id: str
    created_at: float
    last_accessed: float

    # Memory content
    topic: str
    key_facts: List[str]
    user_preferences: Dict[str, Any]
    resolved_issues: List[str]
    successful_patterns: List[str]

    # Context links
    related_sessions: List[str] = field(default_factory=list)
    project_context: Dict[str, Any] = field(default_factory=dict)

    # Usage tracking
    access_count: int = 0
    relevance_score: float = 1.0
    importance_level: str = "normal"  # low, normal, high, critical


@dataclass
class CrossSessionContext:
    """Context that persists across multiple sessions."""

    user_id: str
    project_root: str
    created_at: float
    last_updated: float

    # User behavior patterns
    preferred_commands: Dict[str, int] = field(default_factory=dict)
    successful_workflows: List[Dict[str, Any]] = field(default_factory=list)
    common_issues: List[Dict[str, Any]] = field(default_factory=list)

    # Project understanding
    project_insights: Dict[str, Any] = field(default_factory=dict)
    recurring_topics: List[str] = field(default_factory=list)
    expertise_areas: List[str] = field(default_factory=list)

    # Collaboration preferences
    preferred_collaboration_mode: str = "collaborative"
    safety_preferences: Dict[str, Any] = field(default_factory=dict)
    communication_style: str = "detailed"  # brief, detailed, technical


@dataclass
class ContextSharingProfile:
    """Profile for sharing context between AI agents."""

    agent_id: str
    sharing_permissions: Dict[str, bool] = field(
        default_factory=lambda: {
            "conversation_history": True,
            "user_preferences": True,
            "project_context": True,
            "error_patterns": True,
            "successful_workflows": False,  # More sensitive
            "personal_insights": False,  # Most sensitive
        }
    )

    # Context filtering
    sensitive_topics: List[str] = field(default_factory=list)
    allowed_context_types: List[str] = field(
        default_factory=lambda: ["technical", "workflow", "project_structure"]
    )

    # Sharing constraints
    max_history_depth: int = 10
    max_context_age_hours: int = 24
    require_user_approval: bool = False


class EnhancedConversationContextManager:
    """Enhanced conversation context management for AI agent collaboration."""

    def __init__(self, project_root: Path):
        self.root = project_root
        self.context_dir = project_root / ".ai_onboard" / "enhanced_context"
        self.context_dir.mkdir(parents=True, exist_ok=True)

        # Storage files
        self.memories_file = self.context_dir / "context_memories.json"
        self.cross_session_file = self.context_dir / "cross_session_context.json"
        self.sharing_profiles_file = self.context_dir / "sharing_profiles.json"
        self.context_graph_file = self.context_dir / "context_graph.json"

        # In - memory caches
        self.memories: Dict[str, ContextMemory] = {}
        self.cross_session_contexts: Dict[str, CrossSessionContext] = {}
        self.sharing_profiles: Dict[str, ContextSharingProfile] = {}
        self.context_graph: Dict[str, List[str]] = (
            {}
        )  # session_id -> related_session_ids

        # Components
        self.session_storage = SessionStorageManager(project_root)
        self.metrics_collector = get_unified_metrics_collector(project_root)

        # Load existing data
        self._load_persistent_data()

    def _load_persistent_data(self):
        """Load persistent context data from storage."""
        try:
            # Load memories
            if self.memories_file.exists():
                data = utils.read_json(self.memories_file, default={})
                for memory_id, memory_data in data.items():
                    self.memories[memory_id] = ContextMemory(**memory_data)

            # Load cross - session contexts
            if self.cross_session_file.exists():
                data = utils.read_json(self.cross_session_file, default={})
                for user_id, context_data in data.items():
                    self.cross_session_contexts[user_id] = CrossSessionContext(
                        **context_data
                    )

            # Load sharing profiles
            if self.sharing_profiles_file.exists():
                data = utils.read_json(self.sharing_profiles_file, default={})
                for agent_id, profile_data in data.items():
                    self.sharing_profiles[agent_id] = ContextSharingProfile(
                        **profile_data
                    )

            # Load context graph
            if self.context_graph_file.exists():
                self.context_graph = utils.read_json(
                    self.context_graph_file, default={}
                )

        except Exception as e:
            print(f"Warning: Failed to load persistent context data: {e}")

    def _save_persistent_data(self):
        """Save persistent context data to storage."""
        try:
            # Save memories
            memories_data = {}
            for memory_id, memory in self.memories.items():
                memories_data[memory_id] = asdict(memory)
            utils.write_json(self.memories_file, memories_data)

            # Save cross - session contexts
            cross_session_data = {}
            for user_id, context in self.cross_session_contexts.items():
                cross_session_data[user_id] = asdict(context)
            utils.write_json(self.cross_session_file, cross_session_data)

            # Save sharing profiles
            profiles_data = {}
            for agent_id, profile in self.sharing_profiles.items():
                profiles_data[agent_id] = asdict(profile)
            utils.write_json(self.sharing_profiles_file, profiles_data)

            # Save context graph
            utils.write_json(self.context_graph_file, self.context_graph)

        except Exception as e:
            print(f"Warning: Failed to save persistent context data: {e}")

    def enhance_session_context(self, session_id: str) -> Dict[str, Any]:
        """Enhance a session with cross - session context and memories."""
        try:
            # Load base session
            session = self.session_storage.load_session(session_id)
            if not session:
                return {"error": "Session not found"}

            user_id = session.user_id

            # Get cross - session context
            cross_context = self._get_or_create_cross_session_context(user_id)

            # Get relevant memories
            relevant_memories = self._get_relevant_memories(session_id, user_id)

            # Get related sessions
            related_sessions = self._find_related_sessions(session_id)

            # Build enhanced context
            enhanced_context = {
                "base_session": {
                    "session_id": session_id,
                    "user_id": user_id,
                    "state": session.state,
                    "conversation_rounds": len(session.conversation_rounds),
                    "last_activity": session.last_activity,
                },
                "cross_session_insights": {
                    "preferred_commands": cross_context.preferred_commands,
                    "successful_workflows": cross_context.successful_workflows[
                        -5:
                    ],  # Last 5
                    "expertise_areas": cross_context.expertise_areas,
                    "communication_style": cross_context.communication_style,
                },
                "relevant_memories": [
                    {
                        "topic": memory.topic,
                        "key_facts": memory.key_facts,
                        "relevance_score": memory.relevance_score,
                        "last_accessed": memory.last_accessed,
                    }
                    for memory in relevant_memories
                ],
                "related_sessions": related_sessions,
                "context_quality": {
                    "memory_count": len(relevant_memories),
                    "related_sessions_count": len(related_sessions),
                    "user_experience_level": self._assess_user_experience(
                        cross_context
                    ),
                },
            }

            # Record metrics
            self._record_metric(
                "context_enhanced",
                1,
                {
                    "session_id": session_id,
                    "memory_count": len(relevant_memories),
                    "related_sessions": len(related_sessions),
                },
            )

            return enhanced_context

        except Exception as e:
            self._record_metric("context_enhancement_error", 1)
            return {"error": str(e)}

    def create_context_memory(
        self,
        session_id: str,
        user_id: str,
        topic: str,
        key_facts: List[str],
        importance: str = "normal",
    ) -> str:
        """Create a new context memory from conversation insights."""
        try:
            memory_id = f"mem_{int(time.time())}_{uuid.uuid4().hex[:8]}"

            # Load session for project context
            session = self.session_storage.load_session(session_id)
            project_context = {}
            if session:
                project_context = {
                    "project_root": str(session.project_root),
                    "resolved_intents": session.resolved_intents,
                    "successful_commands": [
                        cmd
                        for cmd in session.executed_commands
                        if cmd.get("status") == "success"
                    ],
                }

            memory = ContextMemory(
                memory_id=memory_id,
                session_id=session_id,
                user_id=user_id,
                created_at=time.time(),
                last_accessed=time.time(),
                topic=topic,
                key_facts=key_facts,
                user_preferences={},
                resolved_issues=[],
                successful_patterns=[],
                project_context=project_context,
                importance_level=importance,
            )

            self.memories[memory_id] = memory
            self._save_persistent_data()

            # Update cross - session context
            self._update_cross_session_context(user_id, session_id, topic, key_facts)

            self._record_metric(
                "context_memory_created",
                1,
                {
                    "topic": topic,
                    "importance": importance,
                    "facts_count": len(key_facts),
                },
            )

            return memory_id

        except Exception:
            self._record_metric("context_memory_error", 1)
            return ""

    def share_context_with_agent(
        self, session_id: str, target_agent_id: str, context_types: List[str]
    ) -> Dict[str, Any]:
        """Share conversation context with another AI agent."""
        try:
            # Get sharing profile for target agent
            sharing_profile = self.sharing_profiles.get(
                target_agent_id, ContextSharingProfile(agent_id=target_agent_id)
            )

            # Load session
            session = self.session_storage.load_session(session_id)
            if not session:
                return {"error": "Session not found"}

            # Filter context based on sharing permissions
            shared_context: Dict[str, Any] = {}

            if (
                "conversation_history" in context_types
                and sharing_profile.sharing_permissions.get(
                    "conversation_history", False
                )
            ):
                # Share filtered conversation history
                history = session.conversation_rounds[
                    -sharing_profile.max_history_depth :
                ]
                shared_context["conversation_history"] = self._filter_sensitive_content(
                    history, sharing_profile.sensitive_topics
                )

            if (
                "user_preferences" in context_types
                and sharing_profile.sharing_permissions.get("user_preferences", False)
            ):
                cross_context = self.cross_session_contexts.get(session.user_id)
                if cross_context:
                    shared_context["user_preferences"] = {
                        "preferred_commands": cross_context.preferred_commands,
                        "communication_style": cross_context.communication_style,
                        "collaboration_mode": cross_context.preferred_collaboration_mode,
                    }

            if (
                "project_context" in context_types
                and sharing_profile.sharing_permissions.get("project_context", False)
            ):
                shared_context["project_context"] = {
                    "project_root": str(session.project_root),
                    "resolved_intents": session.resolved_intents,
                    "current_stage": (
                        getattr(session.current_stage, "value", session.current_stage)
                    ),
                }

            if (
                "error_patterns" in context_types
                and sharing_profile.sharing_permissions.get("error_patterns", False)
            ):
                shared_context["error_patterns"] = {
                    "safety_violations": session.safety_violations,
                    "risk_factors": session.risk_factors,
                }

            # Record sharing event
            self._record_metric(
                "context_shared",
                1,
                {
                    "target_agent": target_agent_id,
                    "context_types": context_types,
                    "shared_items": len(shared_context),
                },
            )

            return {
                "success": True,
                "shared_context": shared_context,
                "sharing_metadata": {
                    "agent_id": target_agent_id,
                    "session_id": session_id,
                    "shared_at": time.time(),
                    "context_types": context_types,
                    "filtered_items": self._count_filtered_items(shared_context),
                },
            }

        except Exception as e:
            self._record_metric("context_sharing_error", 1)
            return {"error": str(e)}

    def get_context_continuity_summary(self, user_id: str) -> Dict[str, Any]:
        """Get a summary of context continuity for a user across sessions."""
        try:
            # Get cross - session context
            cross_context = self.cross_session_contexts.get(user_id)
            if not cross_context:
                return {"error": "No cross - session context found"}

            # Get user's memories
            user_memories = [
                memory for memory in self.memories.values() if memory.user_id == user_id
            ]

            # Get user's sessions
            user_sessions = self.session_storage.get_user_sessions(user_id)

            # Calculate continuity metrics
            total_sessions = len(user_sessions)
            total_memories = len(user_memories)
            avg_session_length = sum(
                len(session.conversation_rounds) for session in user_sessions
            ) / max(total_sessions, 1)

            # Recent activity
            recent_sessions = [
                session
                for session in user_sessions
                if time.time() - session.last_activity < 86400  # Last 24 hours
            ]

            summary = {
                "user_id": user_id,
                "continuity_metrics": {
                    "total_sessions": total_sessions,
                    "recent_sessions": len(recent_sessions),
                    "total_memories": total_memories,
                    "avg_session_length": round(avg_session_length, 2),
                    "expertise_areas": cross_context.expertise_areas,
                    "preferred_commands": dict(
                        sorted(
                            cross_context.preferred_commands.items(),
                            key=lambda x: x[1],
                            reverse=True,
                        )[:5]
                    ),  # Top 5 commands
                },
                "user_profile": {
                    "communication_style": cross_context.communication_style,
                    "collaboration_mode": cross_context.preferred_collaboration_mode,
                    "experience_level": self._assess_user_experience(cross_context),
                },
                "recent_insights": [
                    {
                        "topic": memory.topic,
                        "key_facts": memory.key_facts[:3],  # Top 3 facts
                        "created_at": memory.created_at,
                    }
                    for memory in sorted(
                        user_memories, key=lambda m: m.created_at, reverse=True
                    )[:5]
                ],
            }

            return summary

        except Exception as e:
            return {"error": str(e)}

    def _get_or_create_cross_session_context(self, user_id: str) -> CrossSessionContext:
        """Get or create cross - session context for a user."""
        if user_id not in self.cross_session_contexts:
            self.cross_session_contexts[user_id] = CrossSessionContext(
                user_id=user_id,
                project_root=str(self.root),
                created_at=time.time(),
                last_updated=time.time(),
            )
            self._save_persistent_data()

        return self.cross_session_contexts[user_id]

    def _get_relevant_memories(
        self, session_id: str, user_id: str
    ) -> List[ContextMemory]:
        """Get memories relevant to the current session."""
        # Get current session context
        session = self.session_storage.load_session(session_id)
        if not session:
            return []

        relevant_memories = []
        current_intents = set(session.resolved_intents)

        for memory in self.memories.values():
            if memory.user_id != user_id:
                continue

            # Calculate relevance score based on various factors
            relevance = 0.0

            # Project context match
            if memory.project_context.get("project_root") == str(session.project_root):
                relevance += 0.3

            # Intent overlap
            memory_intents = set(memory.project_context.get("resolved_intents", []))
            if current_intents & memory_intents:
                relevance += 0.4

            # Recency bonus
            age_hours = (time.time() - memory.created_at) / 3600
            if age_hours < 24:
                relevance += 0.2
            elif age_hours < 168:  # 1 week
                relevance += 0.1

            # Importance bonus
            if memory.importance_level == "critical":
                relevance += 0.3
            elif memory.importance_level == "high":
                relevance += 0.2

            memory.relevance_score = relevance
            memory.last_accessed = time.time()

            if relevance > 0.3:  # Threshold for relevance
                relevant_memories.append(memory)

        # Sort by relevance and return top memories
        relevant_memories.sort(key=lambda m: m.relevance_score, reverse=True)
        return relevant_memories[:10]  # Top 10 most relevant

    def _find_related_sessions(self, session_id: str) -> List[Dict[str, Any]]:
        """Find sessions related to the current one."""
        related = []

        # Check context graph
        if session_id in self.context_graph:
            for related_id in self.context_graph[session_id]:
                related_session = self.session_storage.load_session(related_id)
                if related_session:
                    related.append(
                        {
                            "session_id": related_id,
                            "user_id": related_session.user_id,
                            "created_at": related_session.created_at,
                            "conversation_rounds": len(
                                related_session.conversation_rounds
                            ),
                            "resolved_intents": related_session.resolved_intents,
                        }
                    )

        return related

    def _update_cross_session_context(
        self, user_id: str, session_id: str, topic: str, key_facts: List[str]
    ):
        """Update cross - session context with new insights."""
        cross_context = self._get_or_create_cross_session_context(user_id)

        # Update recurring topics
        if topic not in cross_context.recurring_topics:
            cross_context.recurring_topics.append(topic)

        # Update project insights
        if topic not in cross_context.project_insights:
            cross_context.project_insights[topic] = []
        cross_context.project_insights[topic].extend(key_facts)

        # Keep only unique insights
        cross_context.project_insights[topic] = list(
            set(cross_context.project_insights[topic])
        )

        cross_context.last_updated = time.time()
        self._save_persistent_data()

    def _filter_sensitive_content(
        self, content: List[Dict[str, Any]], sensitive_topics: List[str]
    ) -> List[Dict[str, Any]]:
        """Filter sensitive content from shared context."""
        if not sensitive_topics:
            return content

        filtered = []
        for item in content:
            # Simple keyword - based filtering
            item_text = str(item).lower()
            if not any(topic.lower() in item_text for topic in sensitive_topics):
                filtered.append(item)

        return filtered

    def _count_filtered_items(self, shared_context: Dict[str, Any]) -> int:
        """Count filtered items in shared context."""
        count = 0
        for key, value in shared_context.items():
            if isinstance(value, list):
                count += len(value)
            elif isinstance(value, dict):
                count += len(value)
            else:
                count += 1
        return count

    def _assess_user_experience(self, cross_context: CrossSessionContext) -> str:
        """Assess user experience level based on cross - session context."""
        total_commands = sum(cross_context.preferred_commands.values())
        unique_commands = len(cross_context.preferred_commands)
        workflows = len(cross_context.successful_workflows)

        if total_commands > 50 and unique_commands > 10 and workflows > 5:
            return "expert"
        elif total_commands > 20 and unique_commands > 5 and workflows > 2:
            return "intermediate"
        elif total_commands > 5:
            return "beginner"
        else:
            return "new"

    def _record_metric(
        self, name: str, value: float, dimensions: Optional[Dict[str, Any]] = None
    ):
        """Record a metric for enhanced context management."""
        try:
            event = MetricEvent(
                name=name,
                value=value,
                source=MetricSource.SYSTEM,
                category=MetricCategory.RESOURCE,
                dimensions=dimensions or {},
                unit="count",
            )
            self.metrics_collector.collect_metric(event)
        except Exception:
            pass  # Don't fail on metric errors


# Global instance
_enhanced_context_manager: Optional[EnhancedConversationContextManager] = None


def get_enhanced_context_manager(root: Path) -> EnhancedConversationContextManager:
    """Get the global enhanced conversation context manager."""
    global _enhanced_context_manager
    if _enhanced_context_manager is None:
        _enhanced_context_manager = EnhancedConversationContextManager(root)
    return _enhanced_context_manager
