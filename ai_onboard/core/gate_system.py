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
from typing import Dict, Any, Optional, List
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
    questions: List[str]
    confidence: Optional[float] = None
    issues: Optional[List[str]] = None


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
        # In-memory confirmation token for the current gate confirmation step
        self._confirmation_code: Optional[str] = None
    
    def create_gate(self, gate_request: GateRequest) -> Dict[str, Any]:
        """Create a gate that requires AI agent collaboration.

        This is now a mandatory two-step process:
        1) Collect user's answers
        2) Present a confirmation summary requiring an explicit approval code
        """
        
        # Generate gate prompt (step 1)
        gate_prompt = self._generate_gate_prompt(gate_request)
        
        # Write gate prompt file
        self.current_gate_file.write_text(gate_prompt, encoding='utf-8')
        
        # Write gate status
        status = {
            "gate_active": True,
            "gate_type": gate_request.gate_type.value,
            "created_at": time.time(),
            "phase": "collect",
            "waiting_for_response": True
        }
        self.status_file.write_text(json.dumps(status, indent=2), encoding='utf-8')
        
        # Clean up any existing response
        if self.response_file.exists():
            self.response_file.unlink()
        
        # Tell AI agent to check the gate
        print(f"\n[ROBOT] AI AGENT GATE ACTIVATED")
        print(f"[FOLDER] Gate file created: {self.current_gate_file}")
        print(f"[CLIPBOARD] AI Agent: Read the gate file and follow the instructions")
        print(f"[CLOCK] Waiting for AI agent to ask user questions...")
        print(f"[INFO] If you're an AI agent, check: {self.current_gate_file}")
        print(f"[INFO] If you're a human, tell the AI agent: 'Please read the gate file and ask me the questions'")
        
        # Wait for initial responses (step 1)
        initial_response = self._wait_for_response(timeout_seconds=30)

        # If first step timed out or user decided to stop/modify, honor it immediately
        if initial_response.get("user_decision") != "proceed":
            self._cleanup_gate()
            return initial_response

        # Step 2: Confirmation gate with one-time code
        self._confirmation_code = self._generate_confirmation_code()
        confirm_prompt = self._generate_confirmation_prompt(gate_request, initial_response, self._confirmation_code)
        self.current_gate_file.write_text(confirm_prompt, encoding='utf-8')

        status = {
            "gate_active": True,
            "gate_type": gate_request.gate_type.value,
            "created_at": time.time(),
            "phase": "confirm",
            "waiting_for_response": True,
            "confirmation_code_hint": f"{self._confirmation_code[:2]}***"  # small hint for UX
        }
        self.status_file.write_text(json.dumps(status, indent=2), encoding='utf-8')

        # Ensure we do not read the previous response again
        if self.response_file.exists():
            self.response_file.unlink()

        print("[INFO] Awaiting explicit USER CONFIRMATION to proceed...")
        confirmation_response = self._wait_for_response(timeout_seconds=45, expected_confirmation_code=self._confirmation_code, require_proceed=True)

        # Clean up gate files
        self._cleanup_gate()
        
        return confirmation_response
    
    def _generate_gate_prompt(self, gate_request: GateRequest) -> str:
        """Generate a structured prompt for the AI agent."""
        
        prompt = f"""# [ROBOT] AI Agent Collaboration Gate

## 🚨 CRITICAL: DO NOT ANSWER QUESTIONS YOURSELF 🚨

**YOU MUST ASK THE USER THESE QUESTIONS - DO NOT ANSWER THEM YOURSELF**

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
                prompt += f"- [X] {issue}\n"
            prompt += "\n"
        
        # Add questions for the user
        prompt += "### Questions for User:\n"
        for i, question in enumerate(gate_request.questions, 1):
            prompt += f"{i}. {question}\n"
        prompt += "\n"
        
        # Add instructions for AI agent
        prompt += """### [TARGET] Instructions for AI Agent:

**STEP 1: DETECT THIS GATE**
- You are reading this because a gate is active
- The gate file is at: `.ai_onboard/gates/current_gate.md`
- You MUST handle this gate before proceeding

**STEP 2: ASK THE USER**
- Copy the questions below and ask them in the chat
- Wait for the user's actual responses
- Do NOT generate fake responses

**STEP 3: WRITE RESPONSE FILE**
- Create `.ai_onboard/gates/gate_response.json` with user's answers
- Use the exact format shown below

**STEP 4: CONTINUE**
- Once the response file is created, the system will continue automatically

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

### [WARNING] CRITICAL RULES - READ CAREFULLY:
- Do NOT generate fake responses for the user
- Do NOT answer the questions yourself
- Do NOT make up user responses
- Do NOT bypass this gate by making assumptions
- Do NOT proceed without user input
- This is a COLLABORATION point - work WITH the user
- The user's input is REQUIRED to continue

### [ERROR] COMMON MISTAKES TO AVOID:
- ❌ "Based on the context, I'll assume the user wants..."
- ❌ "The user likely wants to proceed with..."
- ❌ "I'll answer these questions for the user..."
- ❌ "Given the project context, the responses should be..."

### [SUCCESS] CORRECT APPROACH:
- ✅ "I need to ask you some questions before proceeding..."
- ✅ "The system is asking for your input on..."
- ✅ "Please answer these questions so we can continue..."

### [INFO] What happens if you ignore this gate:
- The system will timeout after 5 seconds
- The command will fail with "stop" decision
- The user will be confused and frustrated
- You will have failed to collaborate properly

**Status: WAITING_FOR_USER_INPUT**
"""
        
        return prompt
    
    def _wait_for_response(self, timeout_seconds: int = 30, expected_confirmation_code: Optional[str] = None, require_proceed: bool = False) -> Dict[str, Any]:
        """Wait for AI agent to provide user response.

        If expected_confirmation_code is provided, the response must include a matching
        "confirmation_code" field. If require_proceed is True, any non-"proceed" decision
        will be treated as a STOP for safety.
        """
        
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            if self.response_file.exists():
                try:
                    response_text = self.response_file.read_text(encoding='utf-8')
                    response = json.loads(response_text)
                    
                    # Validate response structure
                    if self._validate_response(response, expected_confirmation_code=expected_confirmation_code):
                        if require_proceed and response.get("user_decision") != "proceed":
                            print("[WARNING] Confirmation did not approve proceed. Stopping for safety.")
                            return {
                                "user_responses": response.get("user_responses", []),
                                "user_decision": "stop",
                                "additional_context": "Confirmation denied or modified",
                                "timestamp": time.time()
                            }
                        print(f"[OK] Received user response via AI agent")
                        return response
                    else:
                        print(f"[X] Invalid response format, waiting...")
                        self.response_file.unlink()  # Remove invalid response
                
                except (json.JSONDecodeError, Exception) as e:
                    print(f"[X] Error reading response: {e}")
                    if self.response_file.exists():
                        self.response_file.unlink()
            
            time.sleep(1)  # Check every second
        
        # Timeout - return safe default response
        print(f"\n[ALARM] Gate timeout after {timeout_seconds} seconds")
        print(f"[WARNING] The AI agent did not handle the gate properly")
        print(f"[INFO] Gate file is still available at: {self.current_gate_file}")
        print(f"[INFO] To manually respond, create: {self.response_file}")
        print(f"[WARNING] Safety: Defaulting to STOP due to timeout - user input required")
        return {
            "user_responses": ["timeout"],
            "user_decision": "stop",
            "additional_context": "Gate timed out - no user response received",
            "timestamp": time.time()
        }
    
    def _validate_response(self, response: Dict[str, Any], expected_confirmation_code: Optional[str] = None) -> bool:
        """Validate the structure of the AI agent response and detect fake responses.

        If expected_confirmation_code is provided, ensure response contains a matching
        "confirmation_code" field.
        """
        required_fields = ["user_responses", "user_decision", "timestamp"]
        if not all(field in response for field in required_fields):
            return False
        
        # Check for common fake response patterns
        user_responses = response.get("user_responses", [])
        if not user_responses:
            return False
        
        # Basic content checks: require some substance in answers
        has_substance = False
        for r in user_responses:
            if isinstance(r, str) and len(r.strip()) >= 3:
                has_substance = True
                break
        if not has_substance:
            return False

        # If a confirmation code is expected, enforce a match
        if expected_confirmation_code is not None:
            code = response.get("confirmation_code")
            if not isinstance(code, str) or code != expected_confirmation_code:
                print("[WARNING] Missing or invalid confirmation code in response")
                return False

        # Detect AI-generated responses
        fake_patterns = [
            "based on the context",
            "i'll assume",
            "the user likely",
            "given the project",
            "i'll answer",
            "proceeding with",
            "assuming the user"
        ]
        
        for response_text in user_responses:
            if isinstance(response_text, str):
                response_lower = response_text.lower()
                for pattern in fake_patterns:
                    if pattern in response_lower:
                        print(f"[WARNING] Detected potential fake response: '{response_text}'")
                        print(f"[WARNING] This looks like an AI-generated response, not user input")
                        return False
        
        return True
    
    def _generate_confirmation_code(self) -> str:
        """Generate a short, hard-to-guess confirmation code."""
        import random
        import string
        alphabet = string.ascii_uppercase + string.digits
        return "".join(random.choice(alphabet) for _ in range(6))

    def _generate_confirmation_prompt(self, gate_request: GateRequest, initial_response: Dict[str, Any], code: str) -> str:
        """Generate a confirmation gate prompt summarizing proposed answers."""
        lines = [
            "# [ROBOT] Confirmation Required",
            "",
            "[WARNING] The AI agent has proposed the following answers. Please REVIEW and CONFIRM.",
            "",
            f"## Gate Type: {gate_request.gate_type.value.replace('_', ' ').title()}",
            f"### {gate_request.title}",
            "",
            "### Proposed Answers:",
        ]
        for i, ans in enumerate(initial_response.get("user_responses", []), 1):
            lines.append(f"{i}. {ans}")
        lines.extend([
            "",
            "### What you need to do:",
            "- If these are correct, reply with decision 'proceed' and include the CONFIRMATION CODE below.",
            "- If anything is wrong, reply with decision 'modify' and updated answers.",
            "- If you want to stop, reply with decision 'stop'.",
            "",
            "### CONFIRMATION CODE (must be included in your response):",
            f"- CODE: {code}",
            "",
            "### Response Format (JSON in .ai_onboard/gates/gate_response.json):",
            "{",
            "  \"user_responses\": [\"...\"],",
            "  \"user_decision\": \"proceed|modify|stop\",",
            "  \"additional_context\": \"...\",",
            "  \"confirmation_code\": \"" + code + "\"",
            "}",
            "",
            "[INFO] The system will ONLY proceed if the code matches and decision == 'proceed'.",
        ])
        return "\n".join(lines)

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
def create_clarification_gate(project_root: Path, confidence: float, issues: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
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


def create_scope_check_gate(project_root: Path, current_plan: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
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
