"""
Gate - Vision Integration - Connects gate responses to vision interrogation system.

This module ensures that when users provide responses through gates,
those responses are automatically integrated into the vision interrogation data.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class GateVisionIntegrator:
    """Integrates gate responses into the vision interrogation system."""


    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.vision_file = project_root / ".ai_onboard" / "vision_interrogation.json"
        self.gate_response_file = (
            project_root / ".ai_onboard" / "gates" / "gate_response.json"
        )


    def integrate_gate_response(self) -> bool:
        """
        Integrate the latest gate response into vision interrogation data.

        Returns:
            True if integration was successful, False otherwise
        """
        if not self.gate_response_file.exists():
            return False

        try:
            # Read gate response
            gate_response = json.loads(
                self.gate_response_file.read_text(encoding="utf - 8")
            )

            # Read or create vision data
            vision_data = self._load_vision_data()

            # Integrate the responses
            self._integrate_responses(gate_response, vision_data)

            # Save updated vision data
            self._save_vision_data(vision_data)

            print("[OK] Gate responses integrated into vision interrogation system")
            return True

        except Exception as e:
            print(f"[X] Error integrating gate response: {e}")
            return False


    def _load_vision_data(self) -> Dict[str, Any]:
        """Load existing vision interrogation data or create new structure."""
        if self.vision_file.exists():
            try:
                return json.loads(self.vision_file.read_text(encoding="utf - 8"))
            except (json.JSONDecodeError, FileNotFoundError, OSError):
                pass

        # Create new vision data structure
        return {
            "status": "in_progress",
            "started_at": datetime.now().isoformat() + "Z",
            "current_phase": "vision_core",
            "responses": {"vision_core": {}, "gate_responses": {}},
            "insights": [],
            "ambiguities": [],
        }


    def _integrate_responses(
        self, gate_response: Dict[str, Any], vision_data: Dict[str, Any]
    ):
        """Integrate gate responses into vision data."""
        timestamp = datetime.now().isoformat() + "Z"

        # Extract user responses
        user_responses = gate_response.get("user_responses", [])
        user_decision = gate_response.get("user_decision", "unknown")
        additional_context = gate_response.get("additional_context", "")

        # Create gate response entry
        gate_entry = {
            "responses": user_responses,
            "decision": user_decision,
            "context": additional_context,
            "timestamp": timestamp,
            "source": "gate_collaboration",
        }

        # Add to vision data
        if "gate_responses" not in vision_data["responses"]:
            vision_data["responses"]["gate_responses"] = {}

        # Use timestamp as key for gate response
        vision_data["responses"]["gate_responses"][timestamp] = gate_entry

        # Extract insights from responses
        insights = self._extract_insights(user_responses)
        vision_data["insights"].extend(insights)

        # Update status based on decision
        if user_decision == "proceed":
            vision_data["status"] = "proceeding"
        elif user_decision == "modify":
            vision_data["status"] = "modifying"
        elif user_decision == "stop":
            vision_data["status"] = "paused"


    def _extract_insights(self, responses: List[str]) -> List[str]:
        """Extract key insights from user responses."""
        insights = []

        for response in responses:
            # Look for key phrases that indicate important insights
            response_lower = response.lower()

            if "domain agnostic" in response_lower:
                insights.append("User wants a domain - agnostic tool")

            if "vibe coding" in response_lower:
                insights.append("Target audience: vibe coders")

            if "scope drift" in response_lower:
                insights.append("Key problem to solve: scope drift")

            if "context window" in response_lower:
                insights.append("Key problem to solve: context window issues")

            if "collaborative" in response_lower:
                insights.append("Core requirement: collaborative interface")

            if "low cost" in response_lower or "free" in response_lower:
                insights.append("Constraint: very low cost requirement")

            if "programming background" in response_lower:
                insights.append("User constraint: limited programming knowledge")

        return insights


    def _save_vision_data(self, vision_data: Dict[str, Any]):
        """Save vision data to file."""
        self.vision_file.write_text(
            json.dumps(vision_data, indent=2), encoding="utf - 8"
        )


def integrate_latest_gate_response(project_root: Path = None) -> bool:
    """
    Convenience function to integrate the latest gate response.

    Args:
        project_root: Project root path (defaults to current directory)

    Returns:
        True if integration was successful
    """
    if project_root is None:
        project_root = Path.cwd()

    integrator = GateVisionIntegrator(project_root)
    return integrator.integrate_gate_response()
