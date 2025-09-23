"""
Project State Management

Manages the lifecycle state of AI Onboard projects through defined phases.
Ensures proper progression and gates between project states.
"""

from pathlib import Path
from typing import Any, Dict

from . import utils


class StateError(Exception):
    """Raised when an action requires a higher project state."""


# Project state progression order
STATE_ORDER = [
    "unchartered",  # Initial state, no charter defined
    "chartered",  # Charter created
    "planned",  # Implementation plan created
    "aligned",  # Vision alignment confirmed
    "executing",  # Active development/execution
    "kaizen_cycle",  # Continuous improvement phase
]


def load(root: Path) -> Dict[str, Any]:
    """
    Load the current project state from disk.

    Args:
        root: Project root directory

    Returns:
        State dictionary with at least a 'state' key
    """
    return utils.read_json_cached(
        root / ".ai_onboard" / "state.json", default={"state": "unchartered"}
    )


def save(root: Path, state: Dict[str, Any]) -> None:
    """
    Save the project state to disk.

    Args:
        root: Project root directory
        state: State dictionary to save
    """
    utils.write_json(root / ".ai_onboard" / "state.json", state)


def advance(root: Path, state: Dict[str, Any], target: str) -> None:
    """
    Advance the project state to a new phase.

    Only allows forward progression in the state order.
    Will not move backward to earlier states.

    Args:
        root: Project root directory
        state: Current state dictionary (modified in-place)
        target: Target state to advance to
    """
    current_state = state.get("state", "unchartered")

    # Only allow forward progression
    if STATE_ORDER.index(target) <= STATE_ORDER.index(current_state):
        return

    state["state"] = target
    save(root, state)


def require_gate(root: Path, required_state: str) -> None:
    """
    Check if the current project state meets the required minimum state.

    Raises StateError if the current state is below the required threshold.

    Args:
        root: Project root directory
        required_state: Minimum required state

    Raises:
        StateError: If current state is below requirement
    """
    current_state_data = load(root)
    current_state = current_state_data.get("state", "unchartered")

    if STATE_ORDER.index(current_state) < STATE_ORDER.index(required_state):
        raise StateError(
            f"Blocked: state must be at least {required_state} "
            f"(current: {current_state})"
        )
