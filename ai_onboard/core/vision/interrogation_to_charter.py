"""
Interrogation to Charter Converter: Transform vision interrogation responses into charter format.

This module converts the structured responses from the enhanced vision interrogation
system into a properly formatted charter.json file that can be used for project planning.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base import utils


def convert_interrogation_to_charter(
    interrogation_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert vision interrogation responses to charter format.

    Args:
        interrogation_data: The complete interrogation session data

    Returns:
        Charter data in the expected format
    """
    responses = interrogation_data.get("responses", {})

    # Extract core vision information
    core_problem = _extract_core_problem(responses)
    vision_statement = _extract_vision_statement(responses)
    primary_users = _extract_primary_users(responses)

    # Extract stakeholders and goals
    stakeholders = _extract_stakeholders(responses)
    objectives = _extract_objectives(responses)

    # Extract scope and boundaries
    in_scope = _extract_in_scope(responses)
    out_of_scope = _extract_out_of_scope(responses)
    non_goals = _extract_non_goals(responses)

    # Extract success criteria
    success_metrics = _extract_success_metrics(responses)
    minimum_viable_outcomes = _extract_minimum_viable_outcomes(responses)

    # Extract constraints and context
    constraints = _extract_constraints(responses)
    assumptions = _extract_assumptions(responses)

    # Build the charter
    charter = {
        "version": 1,
        "project_name": _extract_project_name(responses, interrogation_data),
        "vision": vision_statement,
        "objectives": objectives,
        "non_goals": non_goals,
        "stakeholders": stakeholders,
        "constraints": constraints,
        "assumptions": assumptions,
        "success_metrics": success_metrics,
        "risk_appetite": _extract_risk_appetite(responses),
        "delivery_horizon_days": _extract_delivery_horizon(responses),
        "team_size": _extract_team_size(responses),
        "preferred_methodology": _extract_methodology(responses),
        "vision_confirmed": True,  # Mark as confirmed since user completed interrogation
        "interrogation_session_id": interrogation_data.get("session_id"),
        "vision_quality_score": interrogation_data.get("vision_quality_score", 0.0),
    }

    return charter


def _extract_core_problem(responses: Dict[str, Any]) -> str:
    """Extract the core problem statement from responses."""
    # Look for Phase 1 responses about core problem
    phase1 = responses.get("phase_1", {})
    return phase1.get("core_problem", "Problem definition needs clarification")


def _extract_vision_statement(responses: Dict[str, Any]) -> str:
    """Extract the vision statement from responses."""
    phase1 = responses.get("phase_1", {})
    return phase1.get("vision_statement", "Vision statement needs definition")


def _extract_primary_users(responses: Dict[str, Any]) -> List[str]:
    """Extract primary users from responses."""
    phase1 = responses.get("phase_1", {})
    users = phase1.get("primary_users", "")
    if isinstance(users, str):
        return [u.strip() for u in users.split(",") if u.strip()]
    return users if isinstance(users, list) else []


def _extract_stakeholders(responses: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract stakeholders from responses."""
    phase2 = responses.get("phase_2", {})
    stakeholders_data = phase2.get("stakeholders", [])

    if isinstance(stakeholders_data, str):
        # Parse string format if needed
        stakeholders = []
        for line in stakeholders_data.split("\n"):
            if ":" in line:
                name, role = line.split(":", 1)
                stakeholders.append(
                    {
                        "name": name.strip(),
                        "role": role.strip(),
                        "decider": "decision" in role.lower() or "lead" in role.lower(),
                    }
                )
        return stakeholders

    return stakeholders_data if isinstance(stakeholders_data, list) else []


def _extract_objectives(responses: Dict[str, Any]) -> List[str]:
    """Extract objectives from responses."""
    phase2 = responses.get("phase_2", {})
    objectives_data = phase2.get("objectives", [])

    if isinstance(objectives_data, str):
        return [obj.strip() for obj in objectives_data.split("\n") if obj.strip()]

    return objectives_data if isinstance(objectives_data, list) else []


def _extract_in_scope(responses: Dict[str, Any]) -> List[str]:
    """Extract what's in scope from responses."""
    phase3 = responses.get("phase_3", {})
    in_scope_data = phase3.get("in_scope", [])

    if isinstance(in_scope_data, str):
        return [item.strip() for item in in_scope_data.split("\n") if item.strip()]

    return in_scope_data if isinstance(in_scope_data, list) else []


def _extract_out_of_scope(responses: Dict[str, Any]) -> List[str]:
    """Extract what's out of scope from responses."""
    phase3 = responses.get("phase_3", {})
    out_of_scope_data = phase3.get("out_of_scope", [])

    if isinstance(out_of_scope_data, str):
        return [item.strip() for item in out_of_scope_data.split("\n") if item.strip()]

    return out_of_scope_data if isinstance(out_of_scope_data, list) else []


def _extract_non_goals(responses: Dict[str, Any]) -> List[str]:
    """Extract non-goals from responses."""
    phase3 = responses.get("phase_3", {})
    non_goals_data = phase3.get("non_goals", [])

    if isinstance(non_goals_data, str):
        return [item.strip() for item in non_goals_data.split("\n") if item.strip()]

    return non_goals_data if isinstance(non_goals_data, list) else []


def _extract_success_metrics(responses: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract success metrics from responses."""
    phase4 = responses.get("phase_4", {})
    success_criteria = phase4.get("success_criteria", [])

    if isinstance(success_criteria, str):
        # Convert string to structured format
        metrics = []
        for line in success_criteria.split("\n"):
            if ":" in line:
                name, target = line.split(":", 1)
                metrics.append({"name": name.strip(), "target": target.strip()})
        return metrics

    return success_criteria if isinstance(success_criteria, list) else []


def _extract_minimum_viable_outcomes(responses: Dict[str, Any]) -> List[str]:
    """Extract minimum viable outcomes from responses."""
    phase4 = responses.get("phase_4", {})
    mvo_data = phase4.get("minimum_viable_outcomes", [])

    if isinstance(mvo_data, str):
        return [item.strip() for item in mvo_data.split("\n") if item.strip()]

    return mvo_data if isinstance(mvo_data, list) else []


def _extract_constraints(responses: Dict[str, Any]) -> Dict[str, Any]:
    """Extract constraints from responses."""
    constraints = {}

    # Look for time constraints
    phase2 = responses.get("phase_2", {})
    if phase2.get("time_constraints"):
        constraints["time"] = phase2["time_constraints"]

    # Look for budget constraints
    if phase2.get("budget_constraints"):
        constraints["budget"] = phase2["budget_constraints"]

    # Look for compliance requirements
    compliance = []
    if phase2.get("compliance_requirements"):
        compliance.extend(phase2["compliance_requirements"])
    if responses.get("phase_3", {}).get("compliance_requirements"):
        compliance.extend(responses["phase_3"]["compliance_requirements"])

    if compliance:
        constraints["compliance"] = compliance

    return constraints


def _extract_assumptions(responses: Dict[str, Any]) -> List[str]:
    """Extract assumptions from responses."""
    assumptions = []

    # Look for explicit assumptions
    phase3 = responses.get("phase_3", {})
    if phase3.get("assumptions"):
        if isinstance(phase3["assumptions"], str):
            assumptions.extend(
                [a.strip() for a in phase3["assumptions"].split("\n") if a.strip()]
            )
        else:
            assumptions.extend(phase3["assumptions"])

    return assumptions


def _extract_risk_appetite(responses: Dict[str, Any]) -> str:
    """Extract risk appetite from responses."""
    phase2 = responses.get("phase_2", {})
    return phase2.get("risk_appetite", "medium")


def _extract_delivery_horizon(responses: Dict[str, Any]) -> int:
    """Extract delivery horizon from responses."""
    phase2 = responses.get("phase_2", {})
    horizon = phase2.get("delivery_horizon_days", 30)
    try:
        return int(horizon)
    except (ValueError, TypeError):
        return 30


def _extract_team_size(responses: Dict[str, Any]) -> int:
    """Extract team size from responses."""
    phase2 = responses.get("phase_2", {})
    size = phase2.get("team_size", 3)
    try:
        return int(size)
    except (ValueError, TypeError):
        return 3


def _extract_methodology(responses: Dict[str, Any]) -> str:
    """Extract preferred methodology from responses."""
    phase2 = responses.get("phase_2", {})
    return phase2.get("preferred_methodology", "auto")


def _extract_project_name(
    responses: Dict[str, Any], interrogation_data: Dict[str, Any]
) -> str:
    """Extract or infer project name from responses."""
    # Look for explicit project name
    phase1 = responses.get("phase_1", {})
    project_name = phase1.get("project_name")

    if project_name:
        return project_name

    # Try to infer from vision statement
    vision = phase1.get("vision_statement", "")
    if vision and len(vision) > 10:
        # Extract first few meaningful words
        words = vision.split()[:3]
        return " ".join(words).title()

    # Fall back to session ID or default
    return f"Project-{interrogation_data.get('session_id', 'Unknown')[:8]}"


def create_charter_from_interrogation(
    root: Path, interrogation_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Create a charter from completed interrogation data.

    Args:
        root: Project root directory
        interrogation_path: Path to interrogation file (optional)

    Returns:
        Created charter data
    """
    if interrogation_path is None:
        interrogation_path = root / ".ai_onboard" / "vision_interrogation.json"

    # Load interrogation data
    interrogation_data = utils.read_json(interrogation_path, default={})

    if not interrogation_data or interrogation_data.get("status") != "completed":
        raise ValueError("Interrogation not completed or data not found")

    # Convert to charter format
    charter = convert_interrogation_to_charter(interrogation_data)

    # Save to charter file
    charter_path = root / ".ai_onboard" / "charter.json"
    utils.write_json(charter_path, charter)

    return charter
