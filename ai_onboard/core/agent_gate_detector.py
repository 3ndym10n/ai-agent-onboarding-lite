"""
AI Agent Gate Detection System - Forces AI agents to follow gate protocols.

This system automatically detects when gates are active and guides AI agents
through the collaboration process.
"""

import json
import time
from pathlib import Path
from typing import Optional


class AIAgentGateDetector:
    """Detects and handles active gates for AI agents."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.gates_dir = project_root / ".ai_onboard" / "gates"
        self.current_gate_file = self.gates_dir / "current_gate.md"
        self.response_file = self.gates_dir / "gate_response.json"

    def check_for_active_gate(self) -> Optional[str]:
        """Check if there's an active gate that needs attention."""
        if self.current_gate_file.exists():
            return self.current_gate_file.read_text(encoding="utf - 8")
        return None

    def extract_questions_from_gate(self, gate_content: str) -> list:
        """Extract questions from the gate file."""
        lines = gate_content.split("\n")
        questions = []
        in_questions_section = False

        for line in lines:
            if "### Questions for User:" in line:
                in_questions_section = True
                continue
            elif in_questions_section and line.startswith(("1.", "2.", "3.", "4.")):
                question = line.split(".", 1)[1].strip()
                questions.append(question)
            elif in_questions_section and line.startswith("###"):
                break

        return questions

    def create_response_file(
        self, user_responses: list, user_decision: str, additional_context: str = ""
    ):
        """Create the response file with user's answers."""
        response_data = {
            "user_responses": user_responses,
            "user_decision": user_decision,
            "additional_context": additional_context,
            "timestamp": time.time(),
        }

        self.response_file.write_text(
            json.dumps(response_data, indent = 2), encoding="utf - 8"
        )
        print(f"[OK] Response file created: {self.response_file}")

    def generate_agent_prompt(self, gate_content: str) -> str:
        """Generate a prompt that forces the AI agent to follow gate protocol."""
        questions = self.extract_questions_from_gate(gate_content)

        prompt = f"""
🚨 **MANDATORY AI AGENT GATE PROTOCOL** 🚨

An active gate has been detected. You MUST follow this protocol:

1. **ASK THE USER** these questions in the chat:
"""

        for i, question in enumerate(questions, 1):
            prompt += f"   {i}. {question}\n"

        prompt += f"""
2. **WAIT FOR USER RESPONSES** - Do NOT generate fake answers
3. **CALL create_gate_response()** with their actual answers
4. **DO NOT PROCEED** until the gate is resolved

**Gate File Location**: {self.current_gate_file}
**Response File**: {self.response_file}

**This is MANDATORY collaboration - the system is waiting for user input!**
"""
        return prompt


def create_gate_response(
    user_responses: list,
    user_decision: str,
    additional_context: str = "",
    project_root: Path = None,
):
    """Helper function for AI agents to create gate responses."""
    if project_root is None:
        project_root = Path.cwd()

    detector = AIAgentGateDetector(project_root)
    detector.create_response_file(user_responses, user_decision, additional_context)
    print("🎉 Gate response submitted! The system will now continue.")


def check_active_gates(project_root: Path = None) -> Optional[str]:
    """Check for active gates and return instructions for AI agents."""
    if project_root is None:
        project_root = Path.cwd()

    detector = AIAgentGateDetector(project_root)
    gate_content = detector.check_for_active_gate()

    if gate_content:
        return detector.generate_agent_prompt(gate_content)

    return None
