"""AI Agent Wrapper for IAS - Provides collaborative conversation interface with guardrails."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from . import alignment

@dataclass

class IASGuardrails:
    """Guardrails to prevent AI agent drift from core processes."""

    # NON - NEGOTIABLE: These cannot be changed by AI agents
    REQUIRED_WORKFLOW_STEPS = ["analyze", "charter", "plan", "validate"]
    MIN_CONFIDENCE_THRESHOLDS = {"proceed": 0.8, "quick_confirm": 0.6}
    MANDATORY_CONFIRMATIONS = ["vision_alignment", "priority_agreement"]

    # CONVERSATION BOUNDARIES: What AI agents can discuss
    ALLOWED_CONVERSATION_AREAS = [
        "clarify_requirements",
        "adjust_priorities",
        "explain_technical_choices",
        "suggest_alternatives",
        "resolve_ambiguities",
    ]

    # LOCKED DECISIONS: What AI agents cannot change
    LOCKED_DECISIONS = [
        "core_workflow_steps",
        "validation_requirements",
        "safety_checks",
        "telemetry_collection",
    ]

    # CONVERSATION LIMITS: Prevent endless loops
    MAX_CONVERSATION_ROUNDS = 3
    MAX_AMBIGUITY_RESOLUTION_ATTEMPTS = 2


class AIAgentIASWrapper:
    """Wrapper that allows AI agents to interact with IAS collaboratively."""


    def __init__(self, root: Path):
        self.root = root
        self.guardrails = IASGuardrails()
        self.conversation_rounds = 0
        self.resolved_ambiguities: Set[str] = set()


    def get_alignment_preview(self) -> Dict[str, Any]:
        """Get alignment data without running commands (safe preview)."""
        try:
            return alignment.preview(self.root)
        except Exception as e:
            return {
                "error": f"Failed to get alignment preview: {str(e)}",
                "decision": "clarify",
                "confidence": 0.0,
            }


    def can_discuss_topic(self, topic: str) -> bool:
        """Check if a topic is within conversation boundaries."""
        return topic in self.guardrails.ALLOWED_CONVERSATION_AREAS


    def can_change_decision(self, decision_type: str) -> bool:
        """Check if a decision type can be modified."""
        return decision_type not in self.guardrails.LOCKED_DECISIONS


    def validate_conversation_boundaries(self, user_input: str) -> Tuple[bool, str]:
        """Validate that user input stays within allowed conversation areas."""
        # Simple keyword - based validation - can be enhanced
        input_lower = user_input.lower()

        # Check for attempts to change locked decisions
        for locked in self.guardrails.LOCKED_DECISIONS:
            if locked.replace("_", " ") in input_lower:
                return (
                    False,
                    f"Cannot discuss changing {locked} - it's a locked decision",
                )

        # Check for attempts to skip required steps
        for step in self.guardrails.REQUIRED_WORKFLOW_STEPS:
            if f"skip {step}" in input_lower or f"ignore {step}" in input_lower:
                return False, f"Cannot skip required step: {step}"

        return True, "Input within conversation boundaries"


    def generate_conversation_prompt(self, alignment_data: Dict[str, Any]) -> str:
        """Generate a natural conversation prompt based on alignment data."""
        decision = alignment_data.get("decision", "clarify")
        confidence = alignment_data.get("confidence", 0.0)

        if decision == "proceed":
            return f"✅ High confidence ({confidence:.2f}) - I'm ready to proceed with the analysis. Should I continue?"

        elif decision == "quick_confirm":
            return f"🤔 Medium confidence ({confidence:.2f}) - I have a good understanding but want to confirm. Here's what I think:\n\n{self._format_quick_confirm_content(alignment_data)}\n\nDoes this sound right to you?"

        else:  # clarify
            return f"❓ Low confidence ({confidence:.2f}) - I need some clarification before proceeding. Here's what I found:\n\n{self._format_clarify_content(alignment_data)}\n\nCan you help me understand what I'm missing or correct my assumptions?"


    def _format_quick_confirm_content(self, data: Dict[str, Any]) -> str:
        """Format content for quick confirm prompts."""
        content = []

        if data.get("components"):
            content.append("**Project Analysis:**")
            for key, value in data["components"].items():
                content.append(f"  • {key}: {value}")

        if data.get("report_path"):
            content.append(f"\n ** Report saved to:** {data['report_path']}")

        return "\n".join(content)


    def _format_clarify_content(self, data: Dict[str, Any]) -> str:
        """Format content for clarification prompts."""
        content = []

        if data.get("components"):
            content.append("**What I Found:**")
            for key, value in data["components"].items():
                content.append(f"  • {key}: {value}")

        if data.get("ambiguities"):
            content.append("\n ** What I'm Unsure About:**")
            for issue in data["ambiguities"]:
                content.append(f"  ❌ {issue}")

        if data.get("report_path"):
            content.append(f"\n ** Detailed report:** {data['report_path']}")

        return "\n".join(content)


    def process_user_response(
        self, user_input: str, alignment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process user response and determine next action."""
        self.conversation_rounds += 1

        # Check conversation limits
        if self.conversation_rounds > self.guardrails.MAX_CONVERSATION_ROUNDS:
            return {
                "action": "limit_reached",
                "message": "Maximum conversation rounds reached. Please use --assume proceed or address issues manually.",
                "can_proceed": False,
            }

        # Validate input boundaries
        is_valid, message = self.validate_conversation_boundaries(user_input)
        if not is_valid:
            return {
                "action": "boundary_violation",
                "message": message,
                "can_proceed": False,
            }

        # Analyze user response
        input_lower = user_input.lower()

        # Check for confirmation
        if any(
            word in input_lower
            for word in ["yes", "correct", "right", "proceed", "continue", "good"]
        ):
            return {
                "action": "confirmed",
                "message": "User confirmed - proceeding with execution",
                "can_proceed": True,
                "flags": ["--yes"],
            }

        # Check for rejection
        elif any(
            word in input_lower
            for word in ["no", "wrong", "incorrect", "stop", "cancel"]
        ):
            return {
                "action": "rejected",
                "message": "User rejected - stopping execution",
                "can_proceed": False,
            }

        # Check for clarification
        elif any(
            word in input_lower for word in ["clarify", "explain", "what", "how", "why"]
        ):
            return {
                "action": "needs_clarification",
                "message": "User needs more information",
                "can_proceed": False,
                "needs_response": True,
            }

        # Check for corrections
        elif any(
            word in input_lower
            for word in ["actually", "but", "however", "instead", "rather"]
        ):
            return {
                "action": "correction_provided",
                "message": "User provided corrections - updating understanding",
                "can_proceed": False,
                "needs_update": True,
                "user_corrections": user_input,
            }

        # Default: treat as clarification request
        return {
            "action": "unclear_response",
            "message": "Response unclear - please clarify",
            "can_proceed": False,
            "needs_response": True,
        }


    def execute_command_with_flags(
        self, command: str, flags: List[str] = None
    ) -> Dict[str, Any]:
        """Execute a command with proper flags (with guardrails)."""
        if flags is None:
            flags = []

        # Validate command is allowed
        if command not in self.guardrails.REQUIRED_WORKFLOW_STEPS:
            return {
                "success": False,
                "error": f"Command '{command}' not in allowed workflow steps",
            }

        # Build command with flags
        cmd_parts = ["python", "-m", "ai_onboard", command] + flags

        try:
            result = subprocess.run(
                cmd_parts,
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": " ".join(cmd_parts),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 5 minutes",
                "command": " ".join(cmd_parts),
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Command execution failed: {str(e)}",
                "command": " ".join(cmd_parts),
            }


    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of the conversation for context."""
        return {
            "conversation_rounds": self.conversation_rounds,
            "resolved_ambiguities": list(self.resolved_ambiguities),
            "guardrails_active": True,
            "max_rounds": self.guardrails.MAX_CONVERSATION_ROUNDS,
        }


def create_ai_agent_wrapper(root: Path) -> AIAgentIASWrapper:
    """Factory function to create an AI agent wrapper."""
    return AIAgentIASWrapper(root)
