"""
AI Agent Gate System - File-based collaboration between ai-onboard and AI agents.

This system enables real collaboration by:
1. Detecting when ai-onboard needs user input
2. Writing structured prompts for AI agents to read
3. Waiting for AI agent responses via file communication
4. Continuing execution with user input
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class GateType(Enum):
    """Types of gates that require user collaboration."""
    CLARIFICATION_NEEDED = "clarification_needed"
    SCOPE_CHECK = "scope_check"
    ALIGNMENT_CHECK = "alignment_check"
    CONFIRMATION_REQUIRED = "confirmation_required"
    VISION_MISSING = "vision_missing"


@dataclass
class GateRequest:
    """Data structure for gate requests."""
    gate_type: GateType
    title: str
    description: str
    context: Dict[str, Any]
    questions: list[str]
    confidence: Optional[float] = None
    issues: Optional[list[str]] = None


class GateSystem:
    """Manages file-based communication between ai-onboard and AI agents."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.gates_dir = project_root / ".ai_onboard" / "gates"
        self.gates_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths for communication
        self.current_gate_file = self.gates_dir / "current_gate.md"
        self.response_file = self.gates_dir / "gate_response.json"
        self.status_file = self.gates_dir / "gate_status.json"
    
    def create_gate(self, gate_request: GateRequest) -> Dict[str, Any]:
        """Create a gate that requires AI agent collaboration."""
        
        # Generate gate prompt
        gate_prompt = self._generate_gate_prompt(gate_request)
        
        # Write gate prompt file
        self.current_gate_file.write_text(gate_prompt, encoding='utf-8')
        
        # Write gate status
        status = {
            "gate_active": True,
            "gate_type": gate_request.gate_type.value,
            "created_at": time.time(),
            "waiting_for_response": True
        }
        self.status_file.write_text(json.dumps(status, indent=2), encoding='utf-8')
        
        # Clean up any existing response
        if self.response_file.exists():
            self.response_file.unlink()
        
        # Tell AI agent to check the gate
        print(f"\n🤖 AI AGENT GATE ACTIVATED")
        print(f"📁 Please check: {self.current_gate_file}")
        print(f"📋 Follow the instructions in the file to collaborate")
        print(f"⏳ Waiting for your response...")
        
        # Wait for AI agent response
        response = self._wait_for_response()
        
        # Clean up gate files
        self._cleanup_gate()
        
        return response
    
    def _generate_gate_prompt(self, gate_request: GateRequest) -> str:
        """Generate a structured prompt for the AI agent."""
        
        prompt = f"""# 🤖 AI Agent Collaboration Gate

## Gate Type: {gate_request.gate_type.value.replace('_', ' ').title()}

### {gate_request.title}

{gate_request.description}

"""
        
        # Add context if available
        if gate_request.context:
            prompt += "### Current Context:\n"
            for key, value in gate_request.context.items():
                prompt += f"- **{key}**: {value}\n"
            prompt += "\n"
        
        # Add confidence score if available
        if gate_request.confidence is not None:
            prompt += f"### System Confidence: {gate_request.confidence:.2f}\n\n"
        
        # Add issues if available
        if gate_request.issues:
            prompt += "### Issues Detected:\n"
            for issue in gate_request.issues:
                prompt += f"- ❌ {issue}\n"
            prompt += "\n"
        
        # Add questions for the user
        prompt += "### Questions for User:\n"
        for i, question in enumerate(gate_request.questions, 1):
            prompt += f"{i}. {question}\n"
        prompt += "\n"
        
        # Add instructions for AI agent
        prompt += """### 🎯 Instructions for AI Agent:

1. **ASK THE USER** these questions in Cursor chat
2. **WAIT FOR THEIR RESPONSE** - Do not generate fake responses
3. **WRITE THEIR ACTUAL RESPONSE** to the response file
4. **BE COLLABORATIVE** - This is the whole point of the system

### Response Format:
Create a JSON file at `.ai_onboard/gates/gate_response.json` with this structure:

```json
{
  "user_responses": [
    "User's answer to question 1",
    "User's answer to question 2"
  ],
  "user_decision": "proceed|modify|stop",
  "additional_context": "Any additional context from user",
  "timestamp": "current timestamp"
}
```

### 🚨 IMPORTANT:
- Do NOT generate fake responses for the user
- Do NOT bypass this gate by making assumptions
- This is a COLLABORATION point - work WITH the user
- The user's input is REQUIRED to continue

**Status: WAITING_FOR_USER_INPUT**
"""
        
        return prompt
    
    def _wait_for_response(self, timeout_seconds: int = 300) -> Dict[str, Any]:
        """Wait for AI agent to provide user response."""
        
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            if self.response_file.exists():
                try:
                    response_text = self.response_file.read_text(encoding='utf-8')
                    response = json.loads(response_text)
                    
                    # Validate response structure
                    if self._validate_response(response):
                        print(f"✅ Received user response via AI agent")
                        return response
                    else:
                        print(f"❌ Invalid response format, waiting...")
                        self.response_file.unlink()  # Remove invalid response
                
                except (json.JSONDecodeError, Exception) as e:
                    print(f"❌ Error reading response: {e}")
                    if self.response_file.exists():
                        self.response_file.unlink()
            
            time.sleep(1)  # Check every second
        
        # Timeout - return default response
        print(f"⏰ Gate timeout after {timeout_seconds} seconds")
        return {
            "user_responses": ["timeout"],
            "user_decision": "proceed",
            "additional_context": "Gate timed out",
            "timestamp": time.time()
        }
    
    def _validate_response(self, response: Dict[str, Any]) -> bool:
        """Validate the structure of the AI agent response."""
        required_fields = ["user_responses", "user_decision", "timestamp"]
        return all(field in response for field in required_fields)
    
    def _cleanup_gate(self):
        """Clean up gate files after successful collaboration."""
        files_to_clean = [self.current_gate_file, self.response_file, self.status_file]
        
        for file_path in files_to_clean:
            if file_path.exists():
                file_path.unlink()
    
    def is_gate_active(self) -> bool:
        """Check if there's currently an active gate."""
        if not self.status_file.exists():
            return False
        
        try:
            status = json.loads(self.status_file.read_text())
            return status.get("gate_active", False)
        except:
            return False


# Convenience functions for common gate types
def create_clarification_gate(project_root: Path, confidence: float, issues: list[str], context: Dict[str, Any]) -> Dict[str, Any]:
    """Create a clarification gate for low confidence situations."""
    gate_system = GateSystem(project_root)
    
    questions = [
        "What are the most important outcomes you want from this project?",
        "Are there any specific areas you want me to focus on first?",
        "What should I know about your constraints or requirements?"
    ]
    
    if confidence < 0.5:
        questions.append("Should I proceed with the current plan, or would you like to modify it?")
    
    gate_request = GateRequest(
        gate_type=GateType.CLARIFICATION_NEEDED,
        title="System Needs Clarification",
        description=f"The system has low confidence ({confidence:.2f}) and needs your input to proceed effectively.",
        context=context,
        questions=questions,
        confidence=confidence,
        issues=issues
    )
    
    return gate_system.create_gate(gate_request)


def create_scope_check_gate(project_root: Path, current_plan: list[str], context: Dict[str, Any]) -> Dict[str, Any]:
    """Create a scope check gate to prevent scope drift."""
    gate_system = GateSystem(project_root)
    
    questions = [
        "Does this plan align with your vision for the project?",
        "Are there any parts of this plan that seem off-track?",
        "Should I modify the approach or continue as planned?"
    ]
    
    gate_request = GateRequest(
        gate_type=GateType.SCOPE_CHECK,
        title="Scope Alignment Check",
        description="Let's make sure we're on the right track before proceeding.",
        context={**context, "current_plan": current_plan},
        questions=questions
    )
    
    return gate_system.create_gate(gate_request)


def create_confirmation_gate(project_root: Path, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Create a confirmation gate for important actions."""
    gate_system = GateSystem(project_root)
    
    questions = [
        f"Should I proceed with: {action}?",
        "Are there any modifications you'd like me to make first?"
    ]
    
    gate_request = GateRequest(
        gate_type=GateType.CONFIRMATION_REQUIRED,
        title="Confirmation Required",
        description=f"The system wants to {action}. Please confirm before proceeding.",
        context=context,
        questions=questions
    )
    
    return gate_system.create_gate(gate_request)
