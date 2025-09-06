"""
Vision Interrogator: Ensures clear vision definition before AI agent work begins.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from . import utils, charter, vision_guardian


class VisionInterrogator:
    """Comprehensive vision interrogation system."""
    
    def __init__(self, root: Path):
        self.root = root
        self.charter_path = root / ".ai_onboard" / "charter.json"
        self.interrogation_path = root / ".ai_onboard" / "vision_interrogation.json"
        
    def check_vision_readiness(self) -> Dict[str, Any]:
        """Check if vision is ready for AI agent work."""
        charter_data = utils.read_json(self.charter_path, default={})
        interrogation_data = utils.read_json(self.interrogation_path, default={})
        
        # Check if interrogation completed
        interrogation_complete = interrogation_data.get("status") == "completed"
        
        # Calculate vision clarity
        vision_clarity = self._calculate_vision_clarity(charter_data, interrogation_data)
        
        # Determine readiness
        ready_for_agents = (
            interrogation_complete and 
            vision_clarity["score"] >= 0.8
        )
        
        return {
            "ready_for_agents": ready_for_agents,
            "interrogation_complete": interrogation_complete,
            "vision_clarity": vision_clarity,
            "blocking_issues": self._identify_blocking_issues(charter_data, interrogation_data)
        }
    
    def start_interrogation(self) -> Dict[str, Any]:
        """Start vision interrogation process."""
        interrogation_data = utils.read_json(self.interrogation_path, default={})
        
        if interrogation_data.get("status") == "in_progress":
            return {"status": "already_in_progress"}
        
        # Initialize interrogation
        interrogation = {
            "status": "in_progress",
            "started_at": utils.now_iso(),
            "current_phase": "vision_core",
            "responses": {},
            "insights": [],
            "ambiguities": []
        }
        
        utils.write_json(self.interrogation_path, interrogation)
        
        return {
            "status": "interrogation_started",
            "current_phase": "vision_core",
            "next_questions": self._get_phase_questions("vision_core")
        }
    
    def submit_response(self, phase: str, question_id: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Submit response to interrogation question."""
        interrogation_data = utils.read_json(self.interrogation_path, default={})
        
        if interrogation_data.get("status") != "in_progress":
            return {"status": "error", "message": "No interrogation in progress"}
        
        # Validate response
        validation = self._validate_response(phase, question_id, response)
        if not validation["valid"]:
            return {
                "status": "validation_error",
                "errors": validation["errors"]
            }
        
        # Store response
        if "responses" not in interrogation_data:
            interrogation_data["responses"] = {}
        if phase not in interrogation_data["responses"]:
            interrogation_data["responses"][phase] = {}
        
        interrogation_data["responses"][phase][question_id] = {
            "response": response,
            "submitted_at": utils.now_iso(),
            "confidence": response.get("confidence", 0.5)
        }
        
        # Analyze response for insights and ambiguities
        insights = self._analyze_response(phase, question_id, response)
        ambiguities = self._identify_ambiguities(phase, question_id, response)
        
        interrogation_data["insights"].extend(insights)
        interrogation_data["ambiguities"].extend(ambiguities)
        
        # Check if phase complete
        if self._is_phase_complete(interrogation_data, phase):
            self._complete_phase(interrogation_data, phase)
        
        utils.write_json(self.interrogation_path, interrogation_data)
        
        return {
            "status": "response_accepted",
            "insights_generated": len(insights),
            "ambiguities_identified": len(ambiguities),
            "phase_complete": self._is_phase_complete(interrogation_data, phase)
        }
    
    def _calculate_vision_clarity(self, charter_data: Dict[str, Any], interrogation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate vision clarity score."""
        score = 0.0
        
        # Check vision statement
        if charter_data.get("vision") and len(charter_data["vision"]) > 20:
            score += 0.4
        
        # Check objectives
        if charter_data.get("objectives") and len(charter_data["objectives"]) >= 2:
            score += 0.3
        
        # Check interrogation completion
        if interrogation_data.get("status") == "completed":
            score += 0.3
        
        return {
            "score": min(score, 1.0),
            "level": "high" if score >= 0.8 else "medium" if score >= 0.6 else "low"
        }
    
    def _identify_blocking_issues(self, charter_data: Dict[str, Any], interrogation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify issues blocking AI agent work."""
        issues = []
        
        if interrogation_data.get("status") != "completed":
            issues.append({
                "type": "interrogation_incomplete",
                "severity": "critical",
                "description": "Vision interrogation must be completed"
            })
        
        vision_clarity = self._calculate_vision_clarity(charter_data, interrogation_data)
        if vision_clarity["score"] < 0.8:
            issues.append({
                "type": "vision_unclear",
                "severity": "high", 
                "description": f"Vision clarity score is {vision_clarity['score']:.2f}, needs >= 0.8"
            })
        
        return issues
    
    def _get_phase_questions(self, phase: str) -> List[Dict[str, Any]]:
        """Get questions for interrogation phase."""
        questions = {
            "vision_core": [
                {
                    "id": "vc_01",
                    "question": "What is the core problem this project addresses?",
                    "required": True
                },
                {
                    "id": "vc_02",
                    "question": "What is your vision for the ideal outcome?",
                    "required": True
                },
                {
                    "id": "vc_03", 
                    "question": "Who are the primary users or beneficiaries?",
                    "required": True
                }
            ],
            "stakeholders": [
                {
                    "id": "sg_01",
                    "question": "Who are the key stakeholders and decision makers?",
                    "required": True
                },
                {
                    "id": "sg_02",
                    "question": "What are the primary goals for each stakeholder?",
                    "required": True
                },
                {
                    "id": "sg_03",
                    "question": "Are there any conflicting stakeholder interests?",
                    "required": False
                }
            ],
            "scope": [
                {
                    "id": "sb_01",
                    "question": "What is definitely IN scope for this project?",
                    "required": True
                },
                {
                    "id": "sb_02",
                    "question": "What is definitely OUT of scope?",
                    "required": True
                },
                {
                    "id": "sb_03",
                    "question": "What is in the 'maybe' or 'future' category?",
                    "required": False
                }
            ],
            "success": [
                {
                    "id": "sc_01",
                    "question": "How will you measure success?",
                    "required": True
                },
                {
                    "id": "sc_02",
                    "question": "What are the minimum viable outcomes?",
                    "required": True
                },
                {
                    "id": "sc_03",
                    "question": "What would indicate failure?",
                    "required": False
                }
            ]
        }
        return questions.get(phase, [])
    
    def _is_phase_complete(self, interrogation_data: Dict[str, Any], phase: str) -> bool:
        """Check if phase is complete."""
        phase_questions = self._get_phase_questions(phase)
        phase_responses = interrogation_data.get("responses", {}).get(phase, {})
        
        required_questions = [q for q in phase_questions if q.get("required", True)]
        answered_required = sum(1 for q in required_questions if q["id"] in phase_responses)
        
        return answered_required == len(required_questions)
    
    def _complete_phase(self, interrogation_data: Dict[str, Any], phase: str) -> None:
        """Complete a phase and move to next or finish."""
        phases = ["vision_core", "stakeholders", "scope", "success"]
        current_index = phases.index(phase)
        
        if current_index + 1 < len(phases):
            interrogation_data["current_phase"] = phases[current_index + 1]
        else:
            interrogation_data["status"] = "completed"
            interrogation_data["completed_at"] = utils.now_iso()
            
            # Auto-sync to charter when interrogation is completed
            try:
                from .interrogation_to_charter import auto_sync_on_completion
                if auto_sync_on_completion(self.root):
                    print("[OK] Vision interrogation data synced to charter.json")
                else:
                    print("⚠️ Could not sync interrogation data to charter")
            except Exception as e:
                print(f"⚠️ Error syncing to charter: {e}")
    
    def get_current_questions(self) -> Dict[str, Any]:
        """Get current questions for the active phase."""
        interrogation_data = utils.read_json(self.interrogation_path, default={})
        
        if interrogation_data.get("status") != "in_progress":
            return {
                "status": "no_interrogation",
                "message": "No interrogation in progress"
            }
        
        current_phase = interrogation_data.get("current_phase", "vision_core")
        questions = self._get_phase_questions(current_phase)
        
        # Filter out already answered questions
        answered_questions = set()
        if current_phase in interrogation_data.get("responses", {}):
            answered_questions = set(interrogation_data["responses"][current_phase].keys())
        
        remaining_questions = [
            q for q in questions 
            if q["id"] not in answered_questions
        ]
        
        return {
            "status": "questions_available",
            "current_phase": current_phase,
            "questions": remaining_questions,
            "progress": self._calculate_progress(interrogation_data),
            "answered_count": len(answered_questions),
            "total_count": len(questions)
        }
    
    def get_interrogation_summary(self) -> Dict[str, Any]:
        """Get summary of the interrogation process."""
        interrogation_data = utils.read_json(self.interrogation_path, default={})
        charter_data = utils.read_json(self.charter_path, default={})
        
        if not interrogation_data:
            return {
                "status": "no_interrogation",
                "message": "No interrogation data found"
            }
        
        # Calculate completion metrics
        total_questions = sum(len(self._get_phase_questions(phase)) for phase in ["vision_core", "stakeholders", "scope", "success"])
        answered_questions = sum(
            len(interrogation_data.get("responses", {}).get(phase, {}))
            for phase in ["vision_core", "stakeholders", "scope", "success"]
        )
        
        return {
            "status": interrogation_data.get("status", "unknown"),
            "progress": self._calculate_progress(interrogation_data),
            "current_phase": interrogation_data.get("current_phase", "unknown"),
            "started_at": interrogation_data.get("started_at"),
            "completed_at": interrogation_data.get("completed_at"),
            "completion_metrics": {
                "total_questions": total_questions,
                "answered_questions": answered_questions,
                "completion_rate": answered_questions / max(total_questions, 1)
            },
            "insights_count": len(interrogation_data.get("insights", [])),
            "ambiguities_count": len(interrogation_data.get("ambiguities", []))
        }
    
    def force_complete_interrogation(self) -> Dict[str, Any]:
        """Force complete the interrogation (use with caution)."""
        interrogation_data = utils.read_json(self.interrogation_path, default={})
        
        if interrogation_data.get("status") == "completed":
            return {
                "status": "already_completed",
                "message": "Interrogation already completed"
            }
        
        # Mark as completed
        interrogation_data["status"] = "completed"
        interrogation_data["completed_at"] = utils.now_iso()
        interrogation_data["force_completed"] = True
        
        # Update charter with basic vision if not present
        charter_data = utils.read_json(self.charter_path, default={})
        if not charter_data.get("vision"):
            charter_data["vision"] = "Vision defined through interrogation process"
        if not charter_data.get("objectives"):
            charter_data["objectives"] = ["Complete project objectives"]
        
        utils.write_json(self.charter_path, charter_data)
        utils.write_json(self.interrogation_path, interrogation_data)
        
        return {
            "status": "force_completed",
            "message": "Interrogation force completed",
            "charter_updated": True
        }
    
    def _calculate_progress(self, interrogation_data: Dict[str, Any]) -> float:
        """Calculate overall progress through interrogation."""
        total_questions = 0
        answered_questions = 0
        
        for phase in ["vision_core", "stakeholders", "scope", "success"]:
            phase_questions = self._get_phase_questions(phase)
            total_questions += len(phase_questions)
            
            phase_responses = interrogation_data.get("responses", {}).get(phase, {})
            answered_questions += len(phase_responses)
        
        return (answered_questions / max(total_questions, 1)) * 100
    
    def _validate_response(self, phase: str, question_id: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a response to an interrogation question."""
        errors = []
        
        # Check required fields
        if not response.get("answer"):
            errors.append("Answer is required")
        
        # Check confidence level
        confidence = response.get("confidence", 0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            errors.append("Confidence must be a number between 0 and 1")
        
        # Check response length
        answer = response.get("answer", "")
        if len(answer.strip()) < 20:
            errors.append("Answer must be at least 20 characters long")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _analyze_response(self, phase: str, question_id: str, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze a response for insights."""
        insights = []
        answer = response.get("answer", "").lower()
        
        # Analyze for common patterns
        if "user" in answer and "experience" in answer:
            insights.append({
                "type": "user_focus",
                "category": "user_experience",
                "description": "Response indicates user experience focus",
                "confidence": 0.8
            })
        
        if "data" in answer and ("analytics" in answer or "metrics" in answer):
            insights.append({
                "type": "data_driven",
                "category": "measurement",
                "description": "Response indicates data-driven approach",
                "confidence": 0.7
            })
        
        if "security" in answer or "privacy" in answer:
            insights.append({
                "type": "security_conscious",
                "category": "security",
                "description": "Response indicates security/privacy awareness",
                "confidence": 0.9
            })
        
        # Check for ambiguity indicators
        if response.get("confidence", 1) < 0.7:
            insights.append({
                "type": "low_confidence",
                "category": "ambiguity",
                "description": "Low confidence indicates potential ambiguity",
                "confidence": 0.6
            })
        
        return insights
    
    def _identify_ambiguities(self, phase: str, question_id: str, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify ambiguities in a response."""
        ambiguities = []
        answer = response.get("answer", "").lower()
        
        # Check for ambiguity indicators
        ambiguity_indicators = [
            "maybe", "possibly", "perhaps", "not sure", "uncertain",
            "depends", "it depends", "we'll see", "tbd", "to be determined"
        ]
        
        for indicator in ambiguity_indicators:
            if indicator in answer:
                ambiguities.append({
                    "type": "uncertainty",
                    "priority": "medium",
                    "description": f"Response contains uncertainty indicator: '{indicator}'",
                    "question_id": question_id,
                    "phase": phase,
                    "resolved": False
                })
        
        # Check for low confidence
        if response.get("confidence", 1) < 0.5:
            ambiguities.append({
                "type": "low_confidence",
                "priority": "high",
                "description": "Very low confidence in response",
                "question_id": question_id,
                "phase": phase,
                "resolved": False
            })
        
        # Check for missing critical information
        if phase == "vision_core" and question_id == "vc_01" and len(answer) < 30:
            ambiguities.append({
                "type": "insufficient_detail",
                "priority": "critical",
                "description": "Problem definition lacks sufficient detail",
                "question_id": question_id,
                "phase": phase,
                "resolved": False
            })
        
        return ambiguities


def get_vision_interrogator(root: Path) -> VisionInterrogator:
    """Get vision interrogator instance."""
    return VisionInterrogator(root)



