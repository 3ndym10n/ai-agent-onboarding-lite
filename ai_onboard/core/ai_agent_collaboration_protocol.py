"""
AI Agent Collaboration Protocol - Comprehensive protocol for AI agent integration.

This module defines the complete protocol for how AI agents should interact with
the ai - onboard system, including communication standards, safety mechanisms,
integration points, and best practices.
"""

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import utils

# from .ai_agent_wrapper import AIAgentIASWrapper, IASGuardrails
from .enhanced_vision_interrogator import ProjectType, get_enhanced_vision_interrogator

# from .gate_system import GateRequest, GateType
from .universal_error_monitor import get_error_monitor


class CollaborationMode(Enum):
    """Modes of AI agent collaboration."""

    ASSISTIVE = "assistive"  # AI agent assists user with ai - onboard
    AUTONOMOUS = "autonomous"  # AI agent operates independently with oversight
    COLLABORATIVE = "collaborative"  # AI agent and user work together
    SUPERVISED = "supervised"  # AI agent works under human supervision


class AgentCapability(Enum):
    """Capabilities that AI agents can have."""

    VISION_DEFINITION = "vision_definition"
    PROJECT_ANALYSIS = "project_analysis"
    PLANNING = "planning"
    CODE_GENERATION = "code_generation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DEBUGGING = "debugging"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"


class SafetyLevel(Enum):
    """Safety levels for AI agent operations."""

    LOW = "low"  # Basic safety checks
    MEDIUM = "medium"  # Standard safety checks
    HIGH = "high"  # Enhanced safety checks
    CRITICAL = "critical"  # Maximum safety checks

@dataclass

class AgentProfile:
    """Profile of an AI agent's capabilities and constraints."""

    agent_id: str
    name: str
    version: str
    capabilities: List[AgentCapability]
    collaboration_mode: CollaborationMode
    safety_level: SafetyLevel
    max_autonomous_actions: int = 10
    requires_confirmation_for: List[str] = field(default_factory=list)
    allowed_commands: List[str] = field(default_factory=list)
    blocked_commands: List[str] = field(default_factory=list)
    session_timeout: int = 3600  # 1 hour
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

@dataclass

class CollaborationSession:
    """Active collaboration session between AI agent and ai - onboard."""

    session_id: str
    agent_profile: AgentProfile
    project_root: Path
    started_at: datetime
    last_activity: datetime
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    safety_violations: List[Dict[str, Any]] = field(default_factory=list)
    user_interactions: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "active"
    context: Dict[str, Any] = field(default_factory=dict)


class AIAgentCollaborationProtocol:
    """Main protocol for AI agent collaboration with ai - onboard."""


    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.sessions: Dict[str, CollaborationSession] = {}
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self.protocol_config = self._load_protocol_config()
        self.error_monitor = get_error_monitor(project_root)
        self.vision_interrogator = get_enhanced_vision_interrogator(project_root)


    def _load_protocol_config(self) -> Dict[str, Any]:
        """Load protocol configuration."""
        config_path = self.project_root / ".ai_onboard" / "collaboration_config.json"
        if config_path.exists():
            return utils.read_json(config_path, default={})

        # Default configuration
        default_config = {
            "max_concurrent_sessions": 3,
            "default_safety_level": "medium",
            "auto_timeout_sessions": True,
            "require_agent_registration": True,
            "enable_safety_monitoring": True,
            "log_all_interactions": True,
            "allowed_collaboration_modes": ["assistive", "collaborative", "supervised"],
            "blocked_collaboration_modes": ["autonomous"],  # Require explicit approval
            "safety_checkpoints": [
                "before_file_modifications",
                "before_system_commands",
                "before_external_calls",
                "before_data_access",
            ],
        }

        utils.write_json(config_path, default_config)
        return default_config


    def register_agent(self, agent_profile: AgentProfile) -> Dict[str, Any]:
        """Register an AI agent for collaboration."""
        try:
            # Validate agent profile
            validation_result = self._validate_agent_profile(agent_profile)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": "Agent profile validation failed",
                    "errors": validation_result["errors"],
                }

            # Check if agent is already registered
            if agent_profile.agent_id in self.agent_profiles:
                return {
                    "status": "error",
                    "message": f"Agent {agent_profile.agent_id} is already registered",
                }

            # Check collaboration mode restrictions
            if agent_profile.collaboration_mode.value in self.protocol_config.get(
                "blocked_collaboration_modes", []
            ):
                return {
                    "status": "error",
                    "message": f"Collaboration mode '{agent_profile.collaboration_mode.value}' is blocked",
                }

            # Register agent
            self.agent_profiles[agent_profile.agent_id] = agent_profile

            # Save to persistent storage
            self._save_agent_profiles()

            # Log registration
            self.error_monitor.track_capability_usage(
                "agent_registration",
                {
                    "agent_id": agent_profile.agent_id,
                    "name": agent_profile.name,
                    "capabilities": [cap.value for cap in agent_profile.capabilities],
                    "collaboration_mode": agent_profile.collaboration_mode.value,
                    "safety_level": agent_profile.safety_level.value,
                },
            )

            return {
                "status": "success",
                "message": f"Agent {agent_profile.name} registered successfully",
                "agent_id": agent_profile.agent_id,
                "session_limits": {
                    "max_autonomous_actions": agent_profile.max_autonomous_actions,
                    "session_timeout": agent_profile.session_timeout,
                },
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to register agent: {str(e)}"}


    def start_collaboration_session(
        self, agent_id: str, project_root: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Start a new collaboration session."""
        try:
            # Validate agent is registered
            if agent_id not in self.agent_profiles:
                return {
                    "status": "error",
                    "message": f"Agent {agent_id} is not registered",
                }

            # Check session limits
            active_sessions = len(
                [s for s in self.sessions.values() if s.status == "active"]
            )
            max_sessions = self.protocol_config.get("max_concurrent_sessions", 3)

            if active_sessions >= max_sessions:
                return {
                    "status": "error",
                    "message": f"Maximum concurrent sessions ({max_sessions}) reached",
                }

            # Create session
            session_id = f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            agent_profile = self.agent_profiles[agent_id]

            session = CollaborationSession(
                session_id=session_id,
                agent_profile=agent_profile,
                project_root=project_root or self.project_root,
                started_at=datetime.now(),
                last_activity=datetime.now(),
            )

            self.sessions[session_id] = session

            # Initialize session context
            session.context = self._initialize_session_context(session)

            # Log session start
            self.error_monitor.track_capability_usage(
                "collaboration_session_start",
                {
                    "session_id": session_id,
                    "agent_id": agent_id,
                    "collaboration_mode": agent_profile.collaboration_mode.value,
                    "safety_level": agent_profile.safety_level.value,
                },
            )

            return {
                "status": "success",
                "message": "Collaboration session started",
                "session_id": session_id,
                "agent_profile": {
                    "name": agent_profile.name,
                    "capabilities": [cap.value for cap in agent_profile.capabilities],
                    "collaboration_mode": agent_profile.collaboration_mode.value,
                    "safety_level": agent_profile.safety_level.value,
                },
                "session_limits": {
                    "max_autonomous_actions": agent_profile.max_autonomous_actions,
                    "session_timeout": agent_profile.session_timeout,
                },
                "context": session.context,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to start collaboration session: {str(e)}",
            }


    def execute_agent_action(
        self, session_id: str, action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an action requested by an AI agent."""
        try:
            # Validate session
            if session_id not in self.sessions:
                return {"status": "error", "message": f"Session {session_id} not found"}

            session = self.sessions[session_id]

            # Check session status
            if session.status != "active":
                return {
                    "status": "error",
                    "message": f"Session {session_id} is not active",
                }

            # Update last activity
            session.last_activity = datetime.now()

            # Safety checks
            safety_result = self._perform_safety_checks(session, action)
            if not safety_result["safe"]:
                session.safety_violations.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "action": action,
                        "violation": safety_result["violation"],
                        "severity": safety_result["severity"],
                    }
                )

                return {
                    "status": "safety_violation",
                    "message": f"Safety violation: {safety_result['violation']}",
                    "severity": safety_result["severity"],
                    "requires_user_approval": safety_result.get(
                        "requires_user_approval", False
                    ),
                }

            # Execute action based on type
            action_type = action.get("type")

            if action_type == "vision_interrogation":
                result = self._execute_vision_interrogation_action(session, action)
            elif action_type == "project_analysis":
                result = self._execute_project_analysis_action(session, action)
            elif action_type == "planning":
                result = self._execute_planning_action(session, action)
            elif action_type == "gate_interaction":
                result = self._execute_gate_interaction_action(session, action)
            elif action_type == "file_operation":
                result = self._execute_file_operation_action(session, action)
            elif action_type == "command_execution":
                result = self._execute_command_action(session, action)
            else:
                result = {
                    "status": "error",
                    "message": f"Unknown action type: {action_type}",
                }

            # Record action
            session.actions_taken.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "action": action,
                    "result": result,
                }
            )

            # Check for session limits
            if (
                len(session.actions_taken)
                >= session.agent_profile.max_autonomous_actions
            ):
                session.status = "limit_reached"
                result["session_status"] = "limit_reached"
                result["message"] = "Maximum autonomous actions reached"

            return result

        except Exception as e:
            return {"status": "error", "message": f"Failed to execute action: {str(e)}"}


    def handle_user_interaction(
        self, session_id: str, interaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle user interaction with the collaboration session."""
        try:
            if session_id not in self.sessions:
                return {"status": "error", "message": f"Session {session_id} not found"}

            session = self.sessions[session_id]
            session.last_activity = datetime.now()

            # Record user interaction
            session.user_interactions.append(
                {"timestamp": datetime.now().isoformat(), "interaction": interaction}
            )

            # Process interaction based on type
            interaction_type = interaction.get("type")

            if interaction_type == "approval":
                return self._handle_approval_interaction(session, interaction)
            elif interaction_type == "rejection":
                return self._handle_rejection_interaction(session, interaction)
            elif interaction_type == "clarification":
                return self._handle_clarification_interaction(session, interaction)
            elif interaction_type == "guidance":
                return self._handle_guidance_interaction(session, interaction)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown interaction type: {interaction_type}",
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to handle user interaction: {str(e)}",
            }


    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a collaboration session."""
        if session_id not in self.sessions:
            return {"status": "error", "message": f"Session {session_id} not found"}

        session = self.sessions[session_id]

        return {
            "status": "success",
            "session_id": session_id,
            "agent_profile": {
                "name": session.agent_profile.name,
                "capabilities": [
                    cap.value for cap in session.agent_profile.capabilities
                ],
                "collaboration_mode": session.agent_profile.collaboration_mode.value,
                "safety_level": session.agent_profile.safety_level.value,
            },
            "session_info": {
                "status": session.status,
                "started_at": session.started_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "actions_taken": len(session.actions_taken),
                "safety_violations": len(session.safety_violations),
                "user_interactions": len(session.user_interactions),
            },
            "context": session.context,
            "recent_actions": (
                session.actions_taken[-5:] if session.actions_taken else []
            ),
            "recent_violations": (
                session.safety_violations[-3:] if session.safety_violations else []
            ),
        }


    def end_collaboration_session(
        self, session_id: str, reason: str = "completed"
    ) -> Dict[str, Any]:
        """End a collaboration session."""
        try:
            if session_id not in self.sessions:
                return {"status": "error", "message": f"Session {session_id} not found"}

            session = self.sessions[session_id]
            session.status = "ended"
            session.last_activity = datetime.now()

            # Generate session summary
            summary = self._generate_session_summary(session, reason)

            # Log session end
            self.error_monitor.track_capability_usage(
                "collaboration_session_end",
                {
                    "session_id": session_id,
                    "agent_id": session.agent_profile.agent_id,
                    "reason": reason,
                    "actions_taken": len(session.actions_taken),
                    "safety_violations": len(session.safety_violations),
                    "user_interactions": len(session.user_interactions),
                },
            )

            return {
                "status": "success",
                "message": f"Session {session_id} ended: {reason}",
                "summary": summary,
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to end session: {str(e)}"}


    def _validate_agent_profile(self, profile: AgentProfile) -> Dict[str, Any]:
        """Validate an agent profile."""
        errors = []

        # Check required fields
        if not profile.agent_id:
            errors.append("Agent ID is required")

        if not profile.name:
            errors.append("Agent name is required")

        if not profile.capabilities:
            errors.append("At least one capability is required")

        # Check capability validity
        valid_capabilities = [cap.value for cap in AgentCapability]
        for cap in profile.capabilities:
            if cap.value not in valid_capabilities:
                errors.append(f"Invalid capability: {cap.value}")

        # Check safety level
        valid_safety_levels = [level.value for level in SafetyLevel]
        if profile.safety_level.value not in valid_safety_levels:
            errors.append(f"Invalid safety level: {profile.safety_level.value}")

        # Check collaboration mode
        valid_modes = [mode.value for mode in CollaborationMode]
        if profile.collaboration_mode.value not in valid_modes:
            errors.append(
                f"Invalid collaboration mode: {profile.collaboration_mode.value}"
            )

        return {"valid": len(errors) == 0, "errors": errors}


    def _initialize_session_context(
        self, session: CollaborationSession
    ) -> Dict[str, Any]:
        """Initialize context for a collaboration session."""
        context = {
            "project_root": str(session.project_root),
            "agent_capabilities": [
                cap.value for cap in session.agent_profile.capabilities
            ],
            "collaboration_mode": session.agent_profile.collaboration_mode.value,
            "safety_level": session.agent_profile.safety_level.value,
            "session_start": session.started_at.isoformat(),
        }

        # Add project - specific context
        try:
            # Check if vision interrogation is complete
            vision_status = self.vision_interrogator.check_vision_readiness()
            context["vision_status"] = vision_status

            # Check for active gates
            gates_dir = session.project_root / ".ai_onboard" / "gates"
            current_gate_file = gates_dir / "current_gate.md"
            context["active_gates"] = current_gate_file.exists()

            # Check project type
            charter_path = session.project_root / ".ai_onboard" / "charter.json"
            if charter_path.exists():
                charter_data = utils.read_json(charter_path, default={})
                context["project_type"] = charter_data.get("project_type", "unknown")
                context["vision_confirmed"] = charter_data.get(
                    "vision_confirmed", False
                )

        except Exception as e:
            context["context_errors"] = [str(e)]

        return context


    def _perform_safety_checks(
        self, session: CollaborationSession, action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform safety checks on an action."""
        safety_level = session.agent_profile.safety_level
        action_type = action.get("type")

        # Basic safety checks for all actions
        if not action_type:
            return {
                "safe": False,
                "violation": "Action type is required",
                "severity": "high",
            }

        # Check if action is allowed for this agent
        if (
            session.agent_profile.blocked_commands
            and action_type in session.agent_profile.blocked_commands
        ):
            return {
                "safe": False,
                "violation": f"Action type '{action_type}' is blocked for this agent",
                "severity": "high",
            }

        # Check if action requires confirmation
        if action_type in session.agent_profile.requires_confirmation_for:
            return {
                "safe": False,
                "violation": f"Action type '{action_type}' requires user confirmation",
                "severity": "medium",
                "requires_user_approval": True,
            }

        # Enhanced safety checks for higher safety levels
        if safety_level in [SafetyLevel.HIGH, SafetyLevel.CRITICAL]:
            # Check for file modification actions
            if action_type == "file_operation":
                file_path = action.get("file_path")
                if file_path and self._is_protected_file(file_path):
                    return {
                        "safe": False,
                        "violation": f"Attempted to modify protected file: {file_path}",
                        "severity": "critical",
                        "requires_user_approval": True,
                    }

            # Check for system commands
            if action_type == "command_execution":
                command = action.get("command")
                if command and self._is_dangerous_command(command):
                    return {
                        "safe": False,
                        "violation": f"Dangerous command detected: {command}",
                        "severity": "critical",
                        "requires_user_approval": True,
                    }

        return {"safe": True}


    def _is_protected_file(self, file_path: str) -> bool:
        """Check if a file is protected from modification."""
        protected_patterns = [
            ".ai_onboard / policies/",
            ".ai_onboard / charter.json",
            "pyproject.toml",
            "README.md",
            "AGENTS.md",
        ]

        for pattern in protected_patterns:
            if pattern in file_path:
                return True

        return False


    def _is_dangerous_command(self, command: str) -> bool:
        """Check if a command is potentially dangerous."""
        dangerous_patterns = [
            "rm -rf",
            "del /s",
            "format",
            "fdisk",
            "mkfs",
            "dd if=",
            "curl | sh",
            "wget | sh",
        ]

        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return True

        return False


    def _execute_vision_interrogation_action(
        self, session: CollaborationSession, action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute vision interrogation related action."""
        action_subtype = action.get("subtype")

        if action_subtype == "start_interrogation":
            project_type = action.get("project_type", "generic")
            try:
                project_type_enum = ProjectType(project_type)
                result = self.vision_interrogator.start_enhanced_interrogation(
                    project_type_enum
                )
                return {
                    "status": "success",
                    "action": "vision_interrogation_started",
                    "result": result,
                }
            except ValueError:
                return {
                    "status": "error",
                    "message": f"Invalid project type: {project_type}",
                }

        elif action_subtype == "get_status":
            result = self.vision_interrogator.get_enhanced_interrogation_status()
            return {
                "status": "success",
                "action": "vision_interrogation_status",
                "result": result,
            }

        else:
            return {
                "status": "error",
                "message": f"Unknown vision interrogation action: {action_subtype}",
            }


    def _execute_project_analysis_action(
        self, session: CollaborationSession, action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute project analysis related action."""
        # This would integrate with the existing analysis system
        return {
            "status": "success",
            "action": "project_analysis",
            "message": "Project analysis action executed",
        }


    def _execute_planning_action(
        self, session: CollaborationSession, action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute planning related action."""
        # This would integrate with the existing planning system
        return {
            "status": "success",
            "action": "planning",
            "message": "Planning action executed",
        }


    def _execute_gate_interaction_action(
        self, session: CollaborationSession, action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute gate interaction action."""
        # This would integrate with the existing gate system
        return {
            "status": "success",
            "action": "gate_interaction",
            "message": "Gate interaction action executed",
        }


    def _execute_file_operation_action(
        self, session: CollaborationSession, action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute file operation action."""
        operation = action.get("operation")
        file_path = action.get("file_path")
        content = action.get("content")

        if operation == "read":
            try:
                file_content = (session.project_root / file_path).read_text(
                    encoding="utf - 8"
                )
                return {
                    "status": "success",
                    "action": "file_read",
                    "content": file_content,
                }
            except Exception as e:
                return {"status": "error", "message": f"Failed to read file: {str(e)}"}

        elif operation == "write":
            try:
                (session.project_root / file_path).write_text(
                    content, encoding="utf - 8"
                )
                return {
                    "status": "success",
                    "action": "file_written",
                    "file_path": file_path,
                }
            except Exception as e:
                return {"status": "error", "message": f"Failed to write file: {str(e)}"}

        else:
            return {
                "status": "error",
                "message": f"Unknown file operation: {operation}",
            }


    def _execute_command_action(
        self, session: CollaborationSession, action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute command action."""
        command = action.get("command")
        args = action.get("args", [])

        # This would integrate with the existing command execution system
        return {
            "status": "success",
            "action": "command_executed",
            "command": command,
            "args": args,
        }


    def _handle_approval_interaction(
        self, session: CollaborationSession, interaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle user approval interaction."""
        return {
            "status": "success",
            "action": "user_approval_received",
            "message": "User approval processed",
        }


    def _handle_rejection_interaction(
        self, session: CollaborationSession, interaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle user rejection interaction."""
        return {
            "status": "success",
            "action": "user_rejection_received",
            "message": "User rejection processed",
        }


    def _handle_clarification_interaction(
        self, session: CollaborationSession, interaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle user clarification interaction."""
        return {
            "status": "success",
            "action": "user_clarification_received",
            "message": "User clarification processed",
        }


    def _handle_guidance_interaction(
        self, session: CollaborationSession, interaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle user guidance interaction."""
        return {
            "status": "success",
            "action": "user_guidance_received",
            "message": "User guidance processed",
        }


    def _generate_session_summary(
        self, session: CollaborationSession, reason: str
    ) -> Dict[str, Any]:
        """Generate summary of a collaboration session."""
        return {
            "session_id": session.session_id,
            "agent_name": session.agent_profile.name,
            "collaboration_mode": session.agent_profile.collaboration_mode.value,
            "safety_level": session.agent_profile.safety_level.value,
            "duration": (session.last_activity - session.started_at).total_seconds(),
            "actions_taken": len(session.actions_taken),
            "safety_violations": len(session.safety_violations),
            "user_interactions": len(session.user_interactions),
            "end_reason": reason,
            "capabilities_used": [
                cap.value for cap in session.agent_profile.capabilities
            ],
        }


    def _save_agent_profiles(self):
        """Save agent profiles to persistent storage."""
        profiles_path = self.project_root / ".ai_onboard" / "agent_profiles.json"
        profiles_data = {}

        for agent_id, profile in self.agent_profiles.items():
            profiles_data[agent_id] = {
                "agent_id": profile.agent_id,
                "name": profile.name,
                "version": profile.version,
                "capabilities": [cap.value for cap in profile.capabilities],
                "collaboration_mode": profile.collaboration_mode.value,
                "safety_level": profile.safety_level.value,
                "max_autonomous_actions": profile.max_autonomous_actions,
                "requires_confirmation_for": profile.requires_confirmation_for,
                "allowed_commands": profile.allowed_commands,
                "blocked_commands": profile.blocked_commands,
                "session_timeout": profile.session_timeout,
                "created_at": profile.created_at.isoformat(),
                "last_activity": profile.last_activity.isoformat(),
            }

        utils.write_json(profiles_path, profiles_data)


def get_collaboration_protocol(project_root: Path) -> AIAgentCollaborationProtocol:
    """Get collaboration protocol instance."""
    return AIAgentCollaborationProtocol(project_root)
