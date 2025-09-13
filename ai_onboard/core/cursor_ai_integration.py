"""
Cursor AI Integration Module - Core integration points for Cursor AI collaboration.

This module provides the foundational infrastructure for integrating Cursor AI
with the AI Agent Onboarding system, including agent registration, session management,
and command translation capabilities.
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import utils
from .ai_agent_collaboration_protocol import (
    AgentCapability,
    AgentProfile,
    CollaborationMode,
    SafetyLevel,
    get_collaboration_protocol,
)
from .unified_metrics_collector import (
    MetricCategory,
    MetricEvent,
    MetricSource,
    get_unified_metrics_collector,
)


@dataclass
class CursorIntegrationConfig:
    """Configuration for Cursor AI integration."""

    enabled: bool = True
    auto_analyze: bool = True
    show_status_bar: bool = True
    show_sidebar: bool = True
    agent_id: str = "cursor_ai"
    safety_level: str = "medium"
    max_autonomous_actions: int = 5
    require_confirmation: List[str] = field(
        default_factory=lambda: ["file_modifications", "system_commands"]
    )
    session_timeout: int = 7200  # 2 hours
    api_enabled: bool = False
    api_port: int = 8080


class CursorAIIntegration:
    """Main integration class for Cursor AI collaboration."""

    def __init__(self, root: Path):
        self.root = root
        self.config = self._load_config()
        self.collaboration_protocol = get_collaboration_protocol(root)
        self.metrics_collector = get_unified_metrics_collector(root)

        # Initialize if enabled
        if self.config.enabled:
            self._initialize_integration()

    def _load_config(self) -> CursorIntegrationConfig:
        """Load Cursor integration configuration."""
        config_path = self.root / ".ai_onboard" / "cursor_config.json"

        if config_path.exists():
            data = utils.read_json(config_path)
            return CursorIntegrationConfig(**data)

        # Create default config
        config = CursorIntegrationConfig()
        self._save_config(config)
        return config

    def _save_config(self, config: CursorIntegrationConfig):
        """Save Cursor integration configuration."""
        config_path = self.root / ".ai_onboard" / "cursor_config.json"
        utils.ensure_dir(config_path.parent)

        data = {
            "enabled": config.enabled,
            "auto_analyze": config.auto_analyze,
            "show_status_bar": config.show_status_bar,
            "show_sidebar": config.show_sidebar,
            "agent_id": config.agent_id,
            "safety_level": config.safety_level,
            "max_autonomous_actions": config.max_autonomous_actions,
            "require_confirmation": config.require_confirmation,
            "session_timeout": config.session_timeout,
            "api_enabled": config.api_enabled,
            "api_port": config.api_port,
        }

        utils.write_json(config_path, data)

    def _initialize_integration(self):
        """Initialize Cursor AI integration."""
        try:
            # Register Cursor AI agent
            agent_profile = self._create_cursor_agent_profile()
            result = self.collaboration_protocol.register_agent(agent_profile)

            if result.get("status") == "success":
                self._record_metric("cursor_integration_initialized", 1)
                print("✅ Cursor AI integration initialized successfully")
                print(f"   Agent ID: {result.get('agent_id')}")
                print(f"   Message: {result.get('message')}")
            else:
                self._record_metric("cursor_integration_error", 1)
                print(
                    f"❌ Failed to initialize Cursor AI integration: {result.get('message', 'Unknown error')}"
                )

        except Exception as e:
            self._record_metric("cursor_integration_error", 1)
            print(f"❌ Cursor AI integration initialization error: {e}")

    def _create_cursor_agent_profile(self) -> AgentProfile:
        """Create agent profile for Cursor AI."""
        safety_level_map = {
            "low": SafetyLevel.LOW,
            "medium": SafetyLevel.MEDIUM,
            "high": SafetyLevel.HIGH,
            "critical": SafetyLevel.CRITICAL,
        }

        return AgentProfile(
            agent_id=self.config.agent_id,
            name="Cursor AI Assistant",
            version="1.0.0",
            capabilities=[
                AgentCapability.CODE_GENERATION,
                AgentCapability.PLANNING,
                AgentCapability.DEBUGGING,
                AgentCapability.DOCUMENTATION,
                AgentCapability.PROJECT_ANALYSIS,
            ],
            collaboration_mode=CollaborationMode.COLLABORATIVE,
            safety_level=safety_level_map.get(
                self.config.safety_level, SafetyLevel.MEDIUM
            ),
            max_autonomous_actions=self.config.max_autonomous_actions,
            requires_confirmation_for=self.config.require_confirmation,
            session_timeout=self.config.session_timeout,
        )

    def create_collaboration_session(
        self, user_id: str = "cursor_user"
    ) -> Dict[str, Any]:
        """Create a new collaboration session for Cursor AI."""
        try:
            session_result = self.collaboration_protocol.start_collaboration_session(
                agent_id=self.config.agent_id, project_root=self.root
            )

            if session_result.get("status") == "success":
                self._record_metric("cursor_session_created", 1)
                return {
                    "success": True,
                    "session_id": session_result["session_id"],
                    "message": session_result.get(
                        "message", "Collaboration session created successfully"
                    ),
                    "agent_profile": session_result.get("agent_profile", {}),
                    "session_limits": session_result.get("session_limits", {}),
                    "context": session_result.get("context", {}),
                }
            else:
                self._record_metric("cursor_session_error", 1)
                return {
                    "success": False,
                    "error": session_result.get("message", "Unknown error"),
                }

        except Exception as e:
            self._record_metric("cursor_session_error", 1)
            return {"success": False, "error": str(e)}

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get the status of a collaboration session."""
        try:
            session_status = self.collaboration_protocol.get_session_status(session_id)
            return {
                "success": session_status.get("status") == "success",
                "session_status": session_status,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_active_sessions(self) -> Dict[str, Any]:
        """List all active Cursor AI sessions."""
        try:
            # Access sessions directly from the collaboration protocol
            all_sessions = self.collaboration_protocol.sessions
            cursor_sessions = []

            for session_id, session in all_sessions.items():
                if session.agent_profile.agent_id == self.config.agent_id:
                    cursor_sessions.append(
                        {
                            "session_id": session_id,
                            "agent_id": session.agent_profile.agent_id,
                            "status": session.status,
                            "started_at": session.started_at.isoformat(),
                            "last_activity": session.last_activity.isoformat(),
                            "actions_count": len(session.actions_taken),
                            "safety_violations": len(session.safety_violations),
                        }
                    )

            return {
                "success": True,
                "sessions": cursor_sessions,
                "count": len(cursor_sessions),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a collaboration session."""
        try:
            result = self.collaboration_protocol.end_collaboration_session(session_id)
            return {
                "success": result.get("status") == "success",
                "message": result.get("message", "Session ended"),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def translate_natural_language_command(
        self, natural_language: str
    ) -> Dict[str, Any]:
        """Translate natural language to AI Onboard commands."""
        # Simple rule-based translation (can be enhanced with ML)
        command_mappings = {
            "analyze": ["analyze", "scan", "examine", "inspect"],
            "charter": ["charter", "vision", "goals", "objectives"],
            "plan": ["plan", "roadmap", "schedule", "timeline"],
            "validate": ["validate", "check", "verify", "test"],
            "align": ["align", "gate", "checkpoint", "review"],
            "kaizen": ["kaizen", "improve", "optimize", "enhance"],
        }

        text_lower = natural_language.lower()

        for command, keywords in command_mappings.items():
            if any(keyword in text_lower for keyword in keywords):
                return {
                    "success": True,
                    "command": command,
                    "confidence": 0.8,
                    "suggested_args": self._suggest_command_args(command, text_lower),
                }

        return {
            "success": False,
            "error": "Could not translate natural language to command",
            "suggestions": list(command_mappings.keys()),
        }

    def _suggest_command_args(self, command: str, text: str) -> List[str]:
        """Suggest command arguments based on natural language context."""
        args = []

        if command == "analyze":
            if "exec" in text or "external" in text:
                args.append("--allowExec")
        elif command == "charter":
            if "interactive" in text:
                args.append("--interactive")
        elif command == "validate":
            if "report" in text:
                args.append("--report")
        elif command == "align":
            if "approve" in text:
                args.append("--approve")
            if "preview" in text:
                args.append("--preview")

        return args

    def get_project_context_for_cursor(self) -> Dict[str, Any]:
        """Get project context formatted for Cursor AI consumption."""
        try:
            # Load project state
            from . import state, telemetry

            project_state = state.load(self.root)
            latest_metrics = telemetry.last_run(self.root)

            # Get progress information
            progress_info = self._get_progress_summary()

            context = {
                "project_root": str(self.root),
                "project_state": project_state,
                "latest_metrics": latest_metrics,
                "progress": progress_info,
                "integration_status": {
                    "enabled": self.config.enabled,
                    "agent_registered": True,
                    "last_updated": datetime.now().isoformat(),
                },
                "available_commands": [
                    "analyze",
                    "charter",
                    "plan",
                    "validate",
                    "align",
                    "kaizen",
                ],
            }

            self._record_metric("cursor_context_requested", 1)
            return context

        except Exception as e:
            self._record_metric("cursor_context_error", 1)
            return {
                "error": str(e),
                "project_root": str(self.root),
                "integration_status": {"enabled": False, "error": str(e)},
            }

    def _get_progress_summary(self) -> Dict[str, Any]:
        """Get project progress summary."""
        try:
            from .progress_utils import compute_overall_progress

            progress = compute_overall_progress(self.root)
            return {
                "overall_progress": progress["completion_percentage"],
                "completed_tasks": progress["completed_tasks"],
                "total_tasks": progress["total_tasks"],
                "current_phase": "development",  # Can be enhanced
            }
        except Exception:
            return {
                "overall_progress": 0,
                "completed_tasks": 0,
                "total_tasks": 0,
                "current_phase": "unknown",
            }

    def _record_metric(self, name: str, value: float, **dimensions):
        """Record integration metric."""
        try:
            metric = MetricEvent(
                name=f"cursor_integration_{name}",
                value=value,
                source=MetricSource.SYSTEM,
                category=MetricCategory.ADOPTION,
                dimensions={
                    "integration_type": "cursor_ai",
                    "agent_id": self.config.agent_id,
                    **dimensions,
                },
            )
            self.metrics_collector.collect_metric(metric)
        except Exception:
            # Don't let metric collection errors break integration
            pass

    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        return {
            "enabled": self.config.enabled,
            "auto_analyze": self.config.auto_analyze,
            "show_status_bar": self.config.show_status_bar,
            "show_sidebar": self.config.show_sidebar,
            "agent_id": self.config.agent_id,
            "safety_level": self.config.safety_level,
            "max_autonomous_actions": self.config.max_autonomous_actions,
            "require_confirmation": self.config.require_confirmation,
            "session_timeout": self.config.session_timeout,
            "api_enabled": self.config.api_enabled,
            "api_port": self.config.api_port,
        }

    def create_agent_profile(
        self, user_id: str, profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an agent profile for a user."""
        try:
            # Create agent profile using collaboration protocol
            agent_profile = AgentProfile(
                agent_id=f"{user_id}_{profile_data.get('name', 'agent').lower().replace(' ', '_')}",
                name=profile_data.get("name", "Cursor Agent"),
                version="1.0.0",
                capabilities=[
                    AgentCapability(cap) for cap in profile_data.get("capabilities", [])
                ],
                collaboration_mode=CollaborationMode(
                    profile_data.get("collaboration_style", "collaborative")
                ),
                safety_level=SafetyLevel(profile_data.get("safety_level", "medium")),
            )

            # Register with collaboration protocol
            result = self.collaboration_protocol.register_agent(agent_profile)

            if result.get("status") == "success":
                self._record_metric("agent_profile_created", 1)
                return {
                    "agent_id": agent_profile.agent_id,
                    "name": agent_profile.name,
                    "user_id": user_id,
                    "status": "created",
                    "created_at": datetime.now().isoformat(),
                }
            else:
                raise Exception(
                    f"Failed to register agent: {result.get('message', 'Unknown error')}"
                )

        except Exception as e:
            self._record_metric("agent_profile_creation_error", 1)
            raise Exception(f"Failed to create agent profile: {e}")

    def get_agent_profile(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get an agent profile by ID."""
        try:
            # This would typically query the collaboration protocol
            # For now, return a basic profile structure
            return {
                "agent_id": agent_id,
                "name": f"Agent {agent_id}",
                "status": "active",
                "retrieved_at": datetime.now().isoformat(),
            }
        except Exception as e:
            self._record_metric("agent_profile_retrieval_error", 1)
            return None

    def create_session(
        self, user_id: str, project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new collaboration session."""
        try:
            session_id = f"session_{user_id}_{int(time.time())}"

            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "project_context": project_context,
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "timeout": self.config.session_timeout,
            }

            # Store session data (in a real implementation, this would be persisted)
            session_path = self.root / ".ai_onboard" / "sessions" / f"{session_id}.json"
            utils.ensure_dir(session_path.parent)
            utils.write_json(session_path, session_data)

            self._record_metric("session_created", 1)
            return session_data

        except Exception as e:
            self._record_metric("session_creation_error", 1)
            raise Exception(f"Failed to create session: {e}")

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID."""
        try:
            session_path = self.root / ".ai_onboard" / "sessions" / f"{session_id}.json"
            if session_path.exists():
                session_data = utils.read_json(session_path)
                self._record_metric("session_retrieved", 1)
                return session_data
            else:
                return None
        except Exception as e:
            self._record_metric("session_retrieval_error", 1)
            return None

    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status."""
        return {
            "enabled": self.config.enabled,
            "agent_id": self.config.agent_id,
            "safety_level": self.config.safety_level,
            "max_autonomous_actions": self.config.max_autonomous_actions,
            "session_timeout": self.config.session_timeout,
            "api_enabled": self.config.api_enabled,
            "api_port": self.config.api_port if self.config.api_enabled else None,
            "last_initialized": datetime.now().isoformat(),
        }


# Global instance
_cursor_integration: Optional[CursorAIIntegration] = None


def get_cursor_integration(root: Path) -> CursorAIIntegration:
    """Get the global Cursor AI integration instance."""
    global _cursor_integration
    if _cursor_integration is None:
        _cursor_integration = CursorAIIntegration(root)
    return _cursor_integration


# Convenience functions for CLI and API usage
def initialize_cursor_integration(root: Path) -> Dict[str, Any]:
    """Initialize Cursor AI integration."""
    integration = get_cursor_integration(root)
    return {"success": True, "status": integration.get_integration_status()}


def get_cursor_project_context(root: Path) -> Dict[str, Any]:
    """Get project context for Cursor AI."""
    integration = get_cursor_integration(root)
    return integration.get_project_context_for_cursor()


def translate_cursor_command(natural_language: str, root: Path) -> Dict[str, Any]:
    """Translate natural language command for Cursor AI."""
    integration = get_cursor_integration(root)
    return integration.translate_natural_language_command(natural_language)
