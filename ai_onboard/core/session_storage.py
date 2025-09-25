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
    from .orchestration_compatibility import ConversationContext


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

    @staticmethod
    def _enum_value(value: Any) -> str:
        """Return a string representation for enum-like values."""
        raw = getattr(value, "value", value)
        return str(raw) if raw is not None else ""

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
                state=self._enum_value(context.state),
                conversation_rounds=context.conversation_rounds,
                resolved_intents=context.resolved_intents,
                user_corrections=context.user_corrections,
                current_stage=self._enum_value(context.current_stage),
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
                "state": self._enum_value(context.state),
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
            from .orchestration_compatibility import ConversationContext

            # Convert back to ConversationContext
            state_value = data.get("state")
            stage_value = data.get("current_stage")
            context = ConversationContext(
                session_id=data["session_id"],
                user_id=data["user_id"],
                project_root=Path(data["project_root"]),
                created_at=data.get("created_at"),
                last_activity=data.get("last_activity"),
                state=state_value,
                conversation_rounds=data.get("conversation_rounds", []),
                resolved_intents=data.get("resolved_intents", []),
                user_corrections=data.get("user_corrections", []),
                current_stage=stage_value,
                stage_results=data.get("stage_results", {}),
                confidence_scores=data.get("confidence_scores", {}),
                risk_factors=data.get("risk_factors", []),
                planned_commands=data.get("planned_commands", []),
                executed_commands=data.get("executed_commands", []),
                rollback_plan=data.get("rollback_plan"),
                safety_violations=data.get("safety_violations", []),
                intervention_triggers=data.get("intervention_triggers", []),
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

        index = self._load_index()
        sessions = []

        for session_id, info in index.items():
            if info["user_id"] == user_id:
                session = self.load_session(session_id)
                if session:
                    sessions.append(session)

        return sessions

    def create_session_context(
        self,
        session_id: str,
        user_id: str,
        project_root: Path,
        *,
        created_at: Optional[float] = None,
        last_activity: Optional[float] = None,
        state: Any = None,
        conversation_rounds: Optional[List[Dict[str, Any]]] = None,
        resolved_intents: Optional[List[str]] = None,
        user_corrections: Optional[List[str]] = None,
        current_stage: Any = None,
        stage_results: Optional[Dict[str, Any]] = None,
        confidence_scores: Optional[Dict[str, float]] = None,
        risk_factors: Optional[List[str]] = None,
        planned_commands: Optional[List[Dict[str, Any]]] = None,
        executed_commands: Optional[List[Dict[str, Any]]] = None,
        rollback_plan: Optional[Dict[str, Any]] = None,
        safety_violations: Optional[List[str]] = None,
        intervention_triggers: Optional[List[str]] = None,
        save: bool = False,
    ) -> "ConversationContext":
        """Create a ConversationContext instance with sensible defaults."""
        from .orchestration_compatibility import (
            ConversationContext,
            ConversationState,
            DecisionStage,
        )

        project_root_path = Path(project_root)
        timestamp = time.time()
        effective_created_at = created_at if created_at is not None else timestamp
        effective_last_activity = (
            last_activity if last_activity is not None else effective_created_at
        )

        context = ConversationContext(
            session_id,
            user_id,
            project_root_path,
            created_at=effective_created_at,
            last_activity=effective_last_activity,
            state=state or ConversationState.ACTIVE,
            conversation_rounds=list(conversation_rounds or []),
            resolved_intents=list(resolved_intents or []),
            user_corrections=list(user_corrections or []),
            current_stage=current_stage or DecisionStage.ANALYSIS,
            stage_results=dict(stage_results or {}),
            confidence_scores=dict(confidence_scores or {}),
            risk_factors=list(risk_factors or []),
            planned_commands=list(planned_commands or []),
            executed_commands=list(executed_commands or []),
            rollback_plan=rollback_plan,
            safety_violations=list(safety_violations or []),
            intervention_triggers=list(intervention_triggers or []),
        )

        if save:
            self.save_session(context)

        return context

    def create_session(
        self,
        session_id: str,
        user_id: str,
        project_root: Path,
        **kwargs: Any,
    ) -> "ConversationContext":
        """Create and persist a ConversationContext for compatibility helpers."""
        kwargs.pop("save", None)
        return self.create_session_context(
            session_id=session_id,
            user_id=user_id,
            project_root=project_root,
            save=True,
            **kwargs,
        )

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
