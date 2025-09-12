"""
Session Storage Manager for AAOL - Persists sessions across CLI invocations.

This module provides persistent storage for AI Agent Orchestration Layer sessions,
allowing them to survive across different CLI command executions.
"""

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .ai_agent_orchestration import ConversationContext


@dataclass
class StoredSession:
    """Serializable session data for storage."""

    session_id: str
    user_id: str
    project_root: str  # Store as string for JSON serialization
    created_at: float
    last_activity: float
    state: str  # Store enum value as string

    # Conversation data
    conversation_rounds: List[Dict[str, Any]]
    resolved_intents: List[str]
    user_corrections: List[str]

    # Decision pipeline state
    current_stage: str  # Store enum value as string
    stage_results: Dict[str, Any]
    confidence_scores: Dict[str, float]
    risk_factors: List[str]

    # Execution context
    planned_commands: List[Dict[str, Any]]
    executed_commands: List[Dict[str, Any]]
    rollback_plan: Optional[Dict[str, Any]]

    # Safety monitoring
    safety_violations: List[str]
    intervention_triggers: List[str]


class SessionStorageManager:
    """Manages persistent storage of AAOL sessions."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.sessions_dir = project_root / ".ai_onboard" / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # Create a sessions index file for quick lookups
        self.index_file = self.sessions_dir / "sessions_index.json"
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """Ensure the sessions index file exists."""
        if not self.index_file.exists():
            self._save_index({})

    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """Load the sessions index."""
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_index(self, index: Dict[str, Dict[str, Any]]):
        """Save the sessions index."""
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, default=str)

    def _get_session_file(self, session_id: str) -> Path:
        """Get the file path for a specific session."""
        return self.sessions_dir / f"{session_id}.json"

    def save_session(self, context: "ConversationContext") -> bool:
        """Save a session to disk."""
        try:
            # Convert to serializable format
            stored_session = StoredSession(
                session_id=context.session_id,
                user_id=context.user_id,
                project_root=str(context.project_root),
                created_at=context.created_at,
                last_activity=context.last_activity,
                state=context.state.value,
                conversation_rounds=context.conversation_rounds,
                resolved_intents=context.resolved_intents,
                user_corrections=context.user_corrections,
                current_stage=context.current_stage.value,
                stage_results=context.stage_results,
                confidence_scores=context.confidence_scores,
                risk_factors=context.risk_factors,
                planned_commands=context.planned_commands,
                executed_commands=context.executed_commands,
                rollback_plan=context.rollback_plan,
                safety_violations=context.safety_violations,
                intervention_triggers=context.intervention_triggers,
            )

            # Save session file
            session_file = self._get_session_file(context.session_id)
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(asdict(stored_session), f, indent=2, default=str)

            # Update index
            index = self._load_index()
            index[context.session_id] = {
                "user_id": context.user_id,
                "created_at": context.created_at,
                "last_activity": context.last_activity,
                "state": context.state.value,
                "project_root": str(context.project_root),
            }
            self._save_index(index)

            return True

        except Exception as e:
            print(f"Error saving session {context.session_id}: {e}")
            return False

    def load_session(self, session_id: str) -> Optional["ConversationContext"]:
        """Load a session from disk."""
        try:
            session_file = self._get_session_file(session_id)
            if not session_file.exists():
                return None

            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Import here to avoid circular import
            from .ai_agent_orchestration import (
                ConversationContext,
                ConversationState,
                DecisionStage,
            )

            # Convert back to ConversationContext
            context = ConversationContext(
                session_id=data["session_id"],
                user_id=data["user_id"],
                project_root=Path(data["project_root"]),
                created_at=data["created_at"],
                last_activity=data["last_activity"],
                state=ConversationState(data["state"]),
                conversation_rounds=data["conversation_rounds"],
                resolved_intents=data["resolved_intents"],
                user_corrections=data["user_corrections"],
                current_stage=DecisionStage(data["current_stage"]),
                stage_results=data["stage_results"],
                confidence_scores=data["confidence_scores"],
                risk_factors=data["risk_factors"],
                planned_commands=data["planned_commands"],
                executed_commands=data["executed_commands"],
                rollback_plan=data["rollback_plan"],
                safety_violations=data["safety_violations"],
                intervention_triggers=data["intervention_triggers"],
            )

            return context

        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def list_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all sessions, optionally filtered by user."""
        index = self._load_index()
        sessions = []

        for session_id, info in index.items():
            if user_id is None or info["user_id"] == user_id:
                sessions.append({"session_id": session_id, **info})

        return sessions

    def get_user_sessions(self, user_id: str) -> List[Any]:
        """Get all sessions for a specific user as ConversationContext objects."""
        from .ai_agent_orchestration import ConversationContext
        
        index = self._load_index()
        sessions = []
        
        for session_id, info in index.items():
            if info["user_id"] == user_id:
                session = self.load_session(session_id)
                if session:
                    sessions.append(session)
        
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete a session from disk."""
        try:
            # Remove session file
            session_file = self._get_session_file(session_id)
            if session_file.exists():
                session_file.unlink()

            # Remove from index
            index = self._load_index()
            if session_id in index:
                del index[session_id]
                self._save_index(index)

            return True

        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False

    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up sessions older than specified age. Returns count of deleted sessions."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        index = self._load_index()
        deleted_count = 0

        expired_sessions = [
            session_id
            for session_id, info in index.items()
            if info["last_activity"] < cutoff_time
        ]

        for session_id in expired_sessions:
            if self.delete_session(session_id):
                deleted_count += 1

        return deleted_count

    def update_session_activity(self, session_id: str) -> bool:
        """Update the last activity timestamp for a session."""
        try:
            index = self._load_index()
            if session_id in index:
                index[session_id]["last_activity"] = time.time()
                self._save_index(index)
                return True
            return False
        except Exception:
            return False
