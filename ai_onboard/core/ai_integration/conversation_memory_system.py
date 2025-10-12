"""
Conversation Memory System - Advanced memory management for long conversations.

This module provides sophisticated conversation memory management that prevents
context window drift by maintaining critical information across long AI agent
conversations. It implements sliding window memory, importance-based retention,
and progressive context building.
"""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base import utils
from ..base.shared_types import MemorySegment


# Note: MemorySegment now imported from shared_types
@dataclass
class ConversationContext:
    """Enhanced conversation context with memory management."""

    conversation_id: str
    user_id: str
    session_id: str
    created_at: float
    last_updated: float

    # Core conversation state
    current_topic: str
    conversation_stage: str  # discovery, planning, implementation, review
    user_intent_summary: str
    project_context: Dict[str, Any]

    # Memory management
    memory_segments: List[MemorySegment] = field(default_factory=list)
    active_memory_window: List[str] = field(
        default_factory=list
    )  # Current context window
    critical_memory_items: List[str] = field(default_factory=list)  # Never forget items

    # Conversation flow
    clarification_questions_asked: List[str] = field(default_factory=list)
    user_responses_received: List[str] = field(default_factory=list)
    decisions_recorded: List[Dict[str, Any]] = field(default_factory=list)

    # Performance tracking
    message_count: int = 0
    context_switches: int = 0

    # Stage transitions tracking
    stage_transitions: List[Dict[str, Any]] = field(default_factory=list)
    memory_accesses: int = 0


class ConversationMemoryManager:
    """Advanced memory management for long conversations."""

    def __init__(self, root: Path):
        self.root = root

        # Memory configuration
        self.max_memory_segments = 50
        self.max_context_window_size = 20
        self.critical_memory_threshold = 0.8
        self.memory_expiry_hours = 24

        # Storage systems
        self.storage_dir = root / ".ai_onboard" / "conversation_memory"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Active conversations
        self.active_conversations: Dict[str, ConversationContext] = {}

        # Memory cache for performance
        self._memory_cache: Dict[str, List[MemorySegment]] = {}

    def start_conversation(
        self, user_id: str, initial_request: str, session_id: Optional[str] = None
    ) -> str:
        """
        Start a new conversation with memory management.

        Args:
            user_id: User identifier
            initial_request: The user's initial request
            session_id: Optional session identifier

        Returns:
            Conversation ID
        """
        conversation_id = session_id or f"conv_{int(time.time())}_{user_id[:8]}"

        # Create conversation context
        conversation = ConversationContext(
            conversation_id=conversation_id,
            user_id=user_id,
            session_id=session_id or conversation_id,
            created_at=time.time(),
            last_updated=time.time(),
            current_topic="initial_request",
            conversation_stage="discovery",
            user_intent_summary=self._summarize_initial_intent(initial_request),
            project_context={},
        )

        self.active_conversations[conversation_id] = conversation

        # Create initial memory segment
        initial_segment = MemorySegment(
            segment_id=f"{conversation_id}_initial",
            session_id=conversation.session_id,
            user_id=user_id,
            timestamp=time.time(),
            start_message_index=0,
            end_message_index=0,
            key_topics=self._extract_key_topics(initial_request),
            important_facts=[initial_request],
            decisions_made=[],
            user_preferences_expressed={},
            importance_score=1.0,
            relevance_to_current_context=1.0,
            retention_priority="critical",
        )

        conversation.memory_segments.append(initial_segment)
        conversation.critical_memory_items.append(initial_request)

        # Save to persistent storage
        self._save_conversation_context(conversation)

        return conversation_id

    def add_message_to_conversation(
        self,
        conversation_id: str,
        message: str,
        message_type: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a message to an active conversation with memory management.

        Args:
            conversation_id: Conversation identifier
            message: The message content
            message_type: Type of message (user, assistant, system)
            metadata: Additional message metadata
        """
        if conversation_id not in self.active_conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        conversation = self.active_conversations[conversation_id]
        conversation.message_count += 1
        conversation.last_updated = time.time()

        # Update conversation stage based on message content
        conversation.conversation_stage = self._determine_conversation_stage(
            message, conversation.conversation_stage
        )

        # Extract memory-relevant information
        key_topics = self._extract_key_topics(message)
        important_facts = self._extract_important_facts(message)
        decisions = self._extract_decisions(message)
        preferences = self._extract_user_preferences(message)

        # Create memory segment for this message
        segment = MemorySegment(
            segment_id=f"{conversation_id}_msg_{conversation.message_count}",
            session_id=conversation.session_id,
            user_id=conversation.user_id,
            timestamp=time.time(),
            start_message_index=conversation.message_count,
            end_message_index=conversation.message_count,
            key_topics=key_topics,
            important_facts=important_facts,
            decisions_made=decisions,
            user_preferences_expressed=preferences,
            importance_score=self._calculate_importance_score(message, conversation),
            relevance_to_current_context=self._calculate_relevance_score(
                message, conversation
            ),
            retention_priority=self._determine_retention_priority(
                message, conversation
            ),
        )

        conversation.memory_segments.append(segment)

        # Update context window
        self._update_context_window(conversation)

        # Manage memory retention
        self._manage_memory_retention(conversation)

        # Save updates
        self._save_conversation_context(conversation)

    def get_conversation_context(
        self, conversation_id: str, max_segments: int = 10
    ) -> Dict[str, Any]:
        """
        Get the current context for a conversation with memory management.

        Args:
            conversation_id: Conversation identifier
            max_segments: Maximum number of memory segments to include

        Returns:
            Dictionary with conversation context and relevant memory
        """
        if conversation_id not in self.active_conversations:
            return {"error": "Conversation not found"}

        conversation = self.active_conversations[conversation_id]
        conversation.memory_accesses += 1

        # Get most relevant memory segments
        relevant_segments = self._get_most_relevant_segments(conversation, max_segments)

        # Build context summary
        context_summary = {
            "conversation_id": conversation_id,
            "current_stage": conversation.conversation_stage,
            "message_count": conversation.message_count,
            "user_intent": conversation.user_intent_summary,
            "current_topic": conversation.current_topic,
            "project_context": conversation.project_context,
            "critical_memory": conversation.critical_memory_items,
            "recent_memory": [
                seg.important_facts for seg in relevant_segments[-3:]
            ],  # Last 3 segments
            "clarification_questions": conversation.clarification_questions_asked,
            "decisions_made": conversation.decisions_recorded,
        }

        # Update access tracking
        for segment in relevant_segments:
            segment.access_count += 1
            segment.last_accessed = time.time()

        return context_summary

    def update_conversation_stage(
        self, conversation_id: str, new_stage: str, reason: str = ""
    ) -> None:
        """
        Update the conversation stage and record the transition.

        Args:
            conversation_id: Conversation identifier
            new_stage: New conversation stage
            reason: Reason for stage change
        """
        if conversation_id not in self.active_conversations:
            return

        conversation = self.active_conversations[conversation_id]
        old_stage = conversation.conversation_stage
        conversation.conversation_stage = new_stage
        conversation.context_switches += 1

        # Record the stage transition
        transition_record = {
            "from_stage": old_stage,
            "to_stage": new_stage,
            "timestamp": time.time(),
            "reason": reason,
        }

        if not hasattr(conversation, "stage_transitions"):
            conversation.stage_transitions = []

        conversation.stage_transitions.append(transition_record)

        self._save_conversation_context(conversation)

    def _update_context_window(self, conversation: ConversationContext) -> None:
        """Update the active context window with most relevant information."""
        # Get segments sorted by relevance and recency
        sorted_segments = sorted(
            conversation.memory_segments,
            key=lambda s: (s.relevance_to_current_context, s.last_accessed),
            reverse=True,
        )

        # Build context window from most relevant segments
        context_window = []
        for segment in sorted_segments[: self.max_context_window_size]:
            # Add important facts from this segment
            context_window.extend(segment.important_facts)
            context_window.extend(segment.key_topics)

        # Add critical memory items
        context_window.extend(conversation.critical_memory_items)

        # Remove duplicates and limit size
        conversation.active_memory_window = list(set(context_window))[
            : self.max_context_window_size
        ]

    def _manage_memory_retention(self, conversation: ConversationContext) -> None:
        """Manage memory retention based on importance and age."""
        current_time = time.time()

        # Remove expired segments
        active_segments: List[MemorySegment] = []
        for segment in conversation.memory_segments:
            if segment.expires_at and current_time > segment.expires_at:
                continue  # Expired, don't retain

            if len(active_segments) < self.max_memory_segments:
                active_segments.append(segment)
            else:
                # Keep only the most important segments
                active_segments.sort(key=lambda s: s.importance_score, reverse=True)
                if segment.importance_score > active_segments[-1].importance_score:
                    active_segments[-1] = segment

        conversation.memory_segments = active_segments

    def _get_most_relevant_segments(
        self, conversation: ConversationContext, max_segments: int
    ) -> List[MemorySegment]:
        """Get the most relevant memory segments for current context."""
        # Score segments based on multiple factors
        scored_segments = []
        for segment in conversation.memory_segments:
            # Base relevance score
            relevance = segment.relevance_to_current_context

            # Boost for recent segments
            time_boost = min(
                1.0, (time.time() - segment.timestamp) / 3600
            )  # Last hour gets full boost

            # Boost for frequently accessed segments
            access_boost = min(1.0, segment.access_count / 10)  # Up to 10 accesses

            # Boost for high importance segments
            importance_boost = segment.importance_score

            total_score = (
                (relevance * 0.4)
                + (time_boost * 0.2)
                + (access_boost * 0.2)
                + (importance_boost * 0.2)
            )
            scored_segments.append((total_score, segment))

        # Return top segments
        scored_segments.sort(key=lambda x: x[0], reverse=True)
        return [segment for _, segment in scored_segments[:max_segments]]

    def _calculate_importance_score(
        self, message: str, conversation: ConversationContext
    ) -> float:
        """Calculate importance score for a message."""
        score = 0.5  # Base score

        # Boost for messages containing decisions
        decision_keywords = ["decide", "choose", "select", "go with", "settle on"]
        if any(keyword in message.lower() for keyword in decision_keywords):
            score += 0.3

        # Boost for messages containing preferences
        preference_keywords = ["prefer", "like", "want", "need", "must have"]
        if any(keyword in message.lower() for keyword in preference_keywords):
            score += 0.2

        # Boost for messages containing technical requirements
        technical_keywords = [
            "technology",
            "platform",
            "database",
            "api",
            "integration",
        ]
        if any(keyword in message.lower() for keyword in technical_keywords):
            score += 0.2

        # Boost based on conversation stage
        if conversation.conversation_stage in ["planning", "implementation"]:
            score += 0.1

        return min(score, 1.0)

    def _calculate_relevance_score(
        self, message: str, conversation: ConversationContext
    ) -> float:
        """Calculate relevance score for a message to current context."""
        # Simple relevance based on topic overlap with current conversation
        message_words = set(message.lower().split())
        context_words = set(conversation.current_topic.lower().split())

        if not context_words:
            return 0.5

        overlap = len(message_words & context_words)
        return min(overlap / len(context_words), 1.0)

    def _determine_retention_priority(
        self, message: str, conversation: ConversationContext
    ) -> str:
        """Determine retention priority for a message."""
        # Critical messages
        if any(
            keyword in message.lower()
            for keyword in ["must", "critical", "essential", "never forget"]
        ):
            return "critical"

        # High priority messages
        if any(
            keyword in message.lower()
            for keyword in ["important", "key", "main", "primary"]
        ):
            return "high"

        # Normal priority (default)
        return "normal"

    def _extract_key_topics(self, message: str) -> List[str]:
        """Extract key topics from a message."""
        # Simple keyword extraction
        topic_keywords = [
            "project",
            "feature",
            "design",
            "technology",
            "user",
            "data",
            "security",
            "performance",
            "budget",
            "timeline",
            "scope",
        ]

        topics = []
        message_lower = message.lower()

        for keyword in topic_keywords:
            if keyword in message_lower:
                topics.append(keyword)

        return topics

    def _extract_important_facts(self, message: str) -> List[str]:
        """Extract important facts from a message."""
        facts = []

        # Look for factual statements
        sentences = message.split(".")

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Substantial sentences
                # Check for factual indicators
                if any(
                    indicator in sentence.lower()
                    for indicator in ["is", "are", "will", "should", "must"]
                ):
                    facts.append(sentence)

        return facts[:3]  # Limit to 3 facts

    def _extract_decisions(self, message: str) -> List[str]:
        """Extract decisions made in a message."""
        decisions = []

        decision_indicators = [
            "decide",
            "choose",
            "select",
            "go with",
            "settle on",
            "agree to",
        ]
        message_lower = message.lower()

        for indicator in decision_indicators:
            if indicator in message_lower:
                # Extract the decision part
                sentences = message.split(".")
                for sentence in sentences:
                    if indicator in sentence.lower():
                        decisions.append(sentence.strip())

        return decisions

    def _extract_user_preferences(self, message: str) -> Dict[str, Any]:
        """Extract user preferences from a message."""
        preferences = {}

        preference_indicators = [
            "prefer",
            "like",
            "want",
            "need",
            "would like",
            "should be",
        ]
        message_lower = message.lower()

        for indicator in preference_indicators:
            if indicator in message_lower:
                # Simple extraction - could be enhanced with NLP
                preferences[indicator] = True

        return preferences

    def _determine_conversation_stage(self, message: str, current_stage: str) -> str:
        """Determine the current conversation stage based on message content."""
        message_lower = message.lower()

        # Stage progression indicators
        stage_indicators = {
            "planning": ["plan", "design", "architecture", "structure"],
            "implementation": ["build", "create", "develop", "code", "implement"],
            "review": ["review", "test", "check", "validate", "feedback"],
            "completion": ["done", "finished", "complete", "ready", "launch"],
        }

        for stage, keywords in stage_indicators.items():
            if any(keyword in message_lower for keyword in keywords):
                return stage

        return current_stage

    def _summarize_initial_intent(self, request: str) -> str:
        """Create a summary of the user's initial intent."""
        # Simple summarization - extract key nouns and verbs
        words = request.split()
        key_words = [word for word in words if len(word) > 4]

        if key_words:
            return f"User wants to {key_words[0]} {key_words[1] if len(key_words) > 1 else 'something'}"
        else:
            return "User has a project request"

    def _save_conversation_context(self, conversation: ConversationContext) -> None:
        """Save conversation context to persistent storage."""
        try:
            # Save to simple file storage
            context_file = self.storage_dir / f"{conversation.conversation_id}.json"

            context_data = {
                "conversation_id": conversation.conversation_id,
                "user_id": conversation.user_id,
                "session_id": conversation.session_id,
                "created_at": conversation.created_at,
                "last_updated": conversation.last_updated,
                "current_stage": conversation.conversation_stage,
                "user_intent": conversation.user_intent_summary,
                "project_context": conversation.project_context,
                "memory_segments": [
                    {
                        "segment_id": seg.segment_id,
                        "timestamp": seg.timestamp,
                        "key_topics": seg.key_topics,
                        "important_facts": seg.important_facts,
                        "decisions": seg.decisions_made,
                        "importance": seg.importance_score,
                        "retention_priority": seg.retention_priority,
                    }
                    for seg in conversation.memory_segments[-5:]  # Save last 5 segments
                ],
                "critical_memory": conversation.critical_memory_items,
                "clarification_questions": conversation.clarification_questions_asked,
            }

            utils.write_json(context_file, context_data)
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Warning: Failed to save conversation context: {e}")

    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get a summary of the conversation with memory statistics."""
        if conversation_id not in self.active_conversations:
            return {"error": "Conversation not found"}

        conversation = self.active_conversations[conversation_id]

        return {
            "conversation_id": conversation_id,
            "message_count": conversation.message_count,
            "current_stage": conversation.conversation_stage,
            "memory_segments": len(conversation.memory_segments),
            "context_window_size": len(conversation.active_memory_window),
            "critical_memory_items": len(conversation.critical_memory_items),
            "context_switches": conversation.context_switches,
            "memory_accesses": conversation.memory_accesses,
            "clarification_questions_asked": len(
                conversation.clarification_questions_asked
            ),
            "decisions_recorded": len(conversation.decisions_recorded),
        }

    def cleanup_expired_conversations(self, max_age_hours: int = 48) -> int:
        """Clean up conversations that have exceeded the maximum age."""
        current_time = time.time()
        expired_conversations = []

        for conversation_id, conversation in self.active_conversations.items():
            age_hours = (current_time - conversation.created_at) / 3600
            if age_hours > max_age_hours:
                expired_conversations.append(conversation_id)

        # Remove expired conversations
        for conversation_id in expired_conversations:
            del self.active_conversations[conversation_id]

        return len(expired_conversations)


def get_conversation_memory_manager(root: Path) -> ConversationMemoryManager:
    """Get conversation memory manager instance."""
    return ConversationMemoryManager(root)
