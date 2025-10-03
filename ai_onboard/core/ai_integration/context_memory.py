"""
Context Memory System - Preserve conversation and project state between sessions.

This module enables true continuity for vibe coders:
- Remember what you were working on
- Resume conversations seamlessly
- No starting from scratch each session
- Context preserved across AI agent handovers
"""

import json
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional

from ..base import utils


@dataclass
class SessionContext:
    """Complete context for a user session."""

    user_id: str
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Conversation history
    conversation: Deque[Dict[str, str]] = field(default_factory=lambda: deque(maxlen=50))
    
    # Project state
    project_name: Optional[str] = None
    current_phase: Optional[str] = None
    current_task_id: Optional[str] = None
    current_intent: Optional[str] = None
    
    # Recent decisions and context
    recent_decisions: List[Dict[str, Any]] = field(default_factory=list)
    active_gates: List[str] = field(default_factory=list)
    work_in_progress: Dict[str, Any] = field(default_factory=dict)
    
    # Preferences applied this session
    preferences_used: List[str] = field(default_factory=list)


class ContextMemorySystem:
    """
    Manage conversation and project context across sessions.
    
    This is the "memory" that prevents vibe coders from starting
    over each time they open a new chat session.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.context_dir = project_root / ".ai_onboard" / "context"
        self.context_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_session: Optional[SessionContext] = None

    def start_session(self, user_id: str = "vibe_coder") -> SessionContext:
        """Start a new session, loading previous context if it exists."""
        
        # Load previous session if exists
        previous_context = self.load_latest_context(user_id)
        
        # Create new session
        session_id = f"session_{int(datetime.now().timestamp())}"
        self.current_session = SessionContext(
            user_id=user_id,
            session_id=session_id
        )
        
        # If previous session exists, seed with recent context
        if previous_context:
            self._seed_from_previous(previous_context)
        
        return self.current_session

    def _seed_from_previous(self, previous: SessionContext):
        """Seed current session with relevant context from previous session."""
        if not self.current_session:
            return
        
        # Copy project state
        self.current_session.project_name = previous.project_name
        self.current_session.current_phase = previous.current_phase
        self.current_session.current_task_id = previous.current_task_id
        
        # Copy last few conversation messages for context
        if previous.conversation:
            recent_messages = list(previous.conversation)[-10:]  # Last 10 messages
            for msg in recent_messages:
                self.current_session.conversation.append(msg)
        
        # Copy work in progress
        self.current_session.work_in_progress = previous.work_in_progress.copy()

    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        if not self.current_session:
            return
        
        self.current_session.conversation.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def update_project_state(
        self,
        project_name: Optional[str] = None,
        current_phase: Optional[str] = None,
        current_task_id: Optional[str] = None,
        current_intent: Optional[str] = None
    ):
        """Update the current project state."""
        if not self.current_session:
            return
        
        if project_name:
            self.current_session.project_name = project_name
        if current_phase:
            self.current_session.current_phase = current_phase
        if current_task_id:
            self.current_session.current_task_id = current_task_id
        if current_intent:
            self.current_session.current_intent = current_intent

    def add_decision(self, decision: Dict[str, Any]):
        """Record a decision made during this session."""
        if not self.current_session:
            return
        
        self.current_session.recent_decisions.append({
            **decision,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 20 decisions
        if len(self.current_session.recent_decisions) > 20:
            self.current_session.recent_decisions = (
                self.current_session.recent_decisions[-20:]
            )

    def add_preference_used(self, preference_key: str, preference_value: str):
        """Track that a learned preference was used."""
        if not self.current_session:
            return
        
        self.current_session.preferences_used.append(
            f"{preference_key}={preference_value}"
        )

    def save_context(self):
        """Save current session context to disk."""
        if not self.current_session:
            return
        
        context_file = (
            self.context_dir / 
            f"{self.current_session.user_id}_{self.current_session.session_id}.json"
        )
        
        # Convert to JSON-serializable format
        context_data = {
            "user_id": self.current_session.user_id,
            "session_id": self.current_session.session_id,
            "timestamp": self.current_session.timestamp.isoformat(),
            "conversation": list(self.current_session.conversation),
            "project_name": self.current_session.project_name,
            "current_phase": self.current_session.current_phase,
            "current_task_id": self.current_session.current_task_id,
            "current_intent": self.current_session.current_intent,
            "recent_decisions": self.current_session.recent_decisions,
            "active_gates": self.current_session.active_gates,
            "work_in_progress": self.current_session.work_in_progress,
            "preferences_used": self.current_session.preferences_used
        }
        
        utils.write_json(context_file, context_data)

    def load_latest_context(self, user_id: str) -> Optional[SessionContext]:
        """Load the most recent session context for a user."""
        
        # Find all context files for this user
        pattern = f"{user_id}_session_*.json"
        context_files = list(self.context_dir.glob(pattern))
        
        if not context_files:
            return None
        
        # Get the most recent one
        latest_file = max(context_files, key=lambda p: p.stat().st_mtime)
        
        # Load and reconstruct
        data = utils.read_json(latest_file, default={})
        if not data:
            return None
        
        context = SessionContext(
            user_id=data["user_id"],
            session_id=data["session_id"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
        
        # Restore conversation
        for msg in data.get("conversation", []):
            context.conversation.append(msg)
        
        # Restore project state
        context.project_name = data.get("project_name")
        context.current_phase = data.get("current_phase")
        context.current_task_id = data.get("current_task_id")
        context.current_intent = data.get("current_intent")
        
        # Restore decisions and work
        context.recent_decisions = data.get("recent_decisions", [])
        context.active_gates = data.get("active_gates", [])
        context.work_in_progress = data.get("work_in_progress", {})
        context.preferences_used = data.get("preferences_used", [])
        
        return context

    def get_continuation_summary(self) -> str:
        """Get a human-readable summary for continuing where we left off."""
        if not self.current_session:
            return "Starting fresh - no previous session found."
        
        # If no previous conversation, this is a fresh start
        if not self.current_session.conversation:
            return "Starting fresh."
        
        summary_parts = []
        
        # Time since last session
        if self.current_session.timestamp:
            time_diff = datetime.now() - self.current_session.timestamp
            if time_diff.days > 0:
                summary_parts.append(f"Last session: {time_diff.days} days ago")
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                summary_parts.append(f"Last session: {hours} hours ago")
            else:
                summary_parts.append("Continuing from recent session")
        
        # Project context
        if self.current_session.project_name:
            summary_parts.append(f"Project: {self.current_session.project_name}")
        
        if self.current_session.current_phase:
            summary_parts.append(f"Phase: {self.current_session.current_phase}")
        
        if self.current_session.current_intent:
            summary_parts.append(f"You were: {self.current_session.current_intent}")
        
        # Recent conversation
        if self.current_session.conversation:
            last_messages = list(self.current_session.conversation)[-3:]
            if last_messages:
                summary_parts.append("\nRecent conversation:")
                for msg in last_messages:
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")[:80]  # First 80 chars
                    summary_parts.append(f"  {role}: {content}...")
        
        # Preferences used
        if self.current_session.preferences_used:
            summary_parts.append(
                f"\nUsing your preferences: {', '.join(self.current_session.preferences_used[:3])}"
            )
        
        return "\n".join(summary_parts)

    def get_context_for_ai(self) -> str:
        """Get context formatted for AI agent consumption."""
        if not self.current_session:
            return "No previous context."
        
        context_parts = []
        
        # Project state
        if self.current_session.project_name:
            context_parts.append(f"PROJECT: {self.current_session.project_name}")
        
        if self.current_session.current_phase:
            context_parts.append(f"PHASE: {self.current_session.current_phase}")
        
        if self.current_session.current_task_id:
            context_parts.append(f"CURRENT_TASK: {self.current_session.current_task_id}")
        
        # Recent conversation for context
        if self.current_session.conversation:
            recent = list(self.current_session.conversation)[-5:]
            if recent:
                context_parts.append("\nRECENT_CONVERSATION:")
                for msg in recent:
                    context_parts.append(f"  {msg.get('role')}: {msg.get('content')}")
        
        # Recent decisions
        if self.current_session.recent_decisions:
            context_parts.append("\nRECENT_DECISIONS:")
            for decision in self.current_session.recent_decisions[-3:]:
                context_parts.append(f"  - {decision}")
        
        return "\n".join(context_parts)


def get_context_memory_system(project_root: Path) -> ContextMemorySystem:
    """Get or create the context memory system."""
    return ContextMemorySystem(project_root)

