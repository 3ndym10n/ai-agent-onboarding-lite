"""
Auto Gate System - Automatically handles gates for AI agents.

This system provides a simple function that AI agents can call to 
automatically detect and handle any active gates.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional


def auto_handle_gates(project_root: Path = None) -> bool:
    """
    Automatically detect and handle any active gates.
    
    Returns:
        True if a gate was handled, False if no gates were active
    """
    if project_root is None:
        project_root = Path.cwd()
    
    gates_dir = project_root / ".ai_onboard" / "gates"
    current_gate_file = gates_dir / "current_gate.md"
    
    if not current_gate_file.exists():
        return False
    
    print("🚨 ACTIVE GATE DETECTED!")
    print("[ROBOT] Auto-handling gate for AI agent...")
    
    # Read the gate file
    gate_content = current_gate_file.read_text(encoding='utf-8')
    
    # Extract questions
    questions = _extract_questions(gate_content)
    
    # Display the gate information
    print("\n" + "="*60)
    print("[ROBOT] AI AGENT COLLABORATION GATE")
    print("="*60)
    print(f"[FOLDER] Gate File: {current_gate_file}")
    print("\n🎯 QUESTIONS FOR USER:")
    
    for i, question in enumerate(questions, 1):
        print(f"   {i}. {question}")
    
    print("\n🚨 INSTRUCTIONS FOR AI AGENT:")
    print("   1. ASK the user these questions in the chat")
    print("   2. WAIT for their responses")
    print("   3. CALL submit_gate_response() with their answers")
    print("   4. DO NOT proceed until gate is resolved")
    
    print("\n[CLOCK] Gate is ACTIVE - waiting for AI agent to ask questions...")
    print("="*60)
    
    return True


def submit_gate_response(user_responses: List[str], user_decision: str, additional_context: str = "", project_root: Path = None):
    """
    Submit the user's responses to resolve the active gate.
    
    Args:
        user_responses: List of user's answers to the gate questions
        user_decision: "proceed", "modify", or "stop"
        additional_context: Any additional context from the user
        project_root: Project root path (defaults to current directory)
    """
    if project_root is None:
        project_root = Path.cwd()
    
    gates_dir = project_root / ".ai_onboard" / "gates"
    response_file = gates_dir / "gate_response.json"
    
    response_data = {
        "user_responses": user_responses,
        "user_decision": user_decision,
        "additional_context": additional_context,
        "timestamp": time.time()
    }
    
    response_file.write_text(json.dumps(response_data, indent=2), encoding='utf-8')
    
    print("[OK] Gate response submitted!")
    print(f"[FOLDER] Response saved to: {response_file}")
    
    # Integrate response into vision system
    try:
        from .gate_vision_integration import integrate_latest_gate_response
        if integrate_latest_gate_response(project_root):
            print("🎯 Gate responses integrated into vision system!")
        else:
            print("⚠️ Could not integrate gate responses into vision system")
    except Exception as e:
        print(f"⚠️ Error integrating gate responses: {e}")
    
    print("🎉 System will now continue with user input!")


def _extract_questions(gate_content: str) -> List[str]:
    """Extract questions from gate content."""
    lines = gate_content.split('\n')
    questions = []
    in_questions_section = False
    
    for line in lines:
        if "### Questions for User:" in line:
            in_questions_section = True
            continue
        elif in_questions_section and line.strip().startswith(('1.', '2.', '3.', '4.')):
            question = line.split('.', 1)[1].strip()
            questions.append(question)
        elif in_questions_section and line.startswith('###'):
            break
    
    return questions


# Convenience function for quick gate handling
def handle_gate_now(project_root: Path = None) -> bool:
    """Quick function to handle any active gates immediately."""
    return auto_handle_gates(project_root)
