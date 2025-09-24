"""
Approval Workflow System

Handles user approval for system changes with course correction capabilities.
This addresses the user's need to approve suggestions and provide guidance when needed.
"""

# Import read_json, write_json from utils.py module
import importlib.util
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

_utils_path = Path(__file__).parent / "utils.py"
_utils_spec = importlib.util.spec_from_file_location("utils_module", _utils_path)
_utils_module = importlib.util.module_from_spec(_utils_spec)
_utils_spec.loader.exec_module(_utils_module)
read_json = _utils_module.read_json
write_json = _utils_module.write_json


class ApprovalStatus(Enum):
    """Status of approval requests."""

    PENDING = "pending"  # Waiting for user input
    APPROVED = "approved"  # User approved
    REJECTED = "rejected"  # User rejected
    MODIFIED = "modified"  # User provided modifications
    EXPIRED = "expired"  # Request expired


class ChangeType(Enum):
    """Types of changes requiring approval."""

    FILE_DELETION = "file_deletion"
    MAJOR_REFACTOR = "major_refactor"
    SYSTEM_CHANGE = "system_change"
    HIGH_RISK_OPERATION = "high_risk_operation"
    TOOL_INTEGRATION = "tool_integration"
    CONFIGURATION_CHANGE = "configuration_change"
    DEPENDENCY_CHANGE = "dependency_change"


@dataclass
class ProposedAction:
    """A proposed action for user approval."""

    action_id: str
    change_type: ChangeType
    description: str
    rationale: str
    risk_level: str
    impact_analysis: Dict[str, Any]
    proposed_steps: List[str]
    alternatives: List[str] = field(default_factory=list)
    estimated_time: str = "unknown"
    rollback_plan: str = "none"


@dataclass
class ApprovalRequest:
    """An approval request for user review."""

    request_id: str
    timestamp: float
    proposed_actions: List[ProposedAction]
    context: str
    urgency: str = "normal"  # low, normal, high, critical
    status: ApprovalStatus = ApprovalStatus.PENDING
    user_feedback: str = ""
    modifications: List[str] = field(default_factory=list)
    expires_at: Optional[float] = None


class ApprovalWorkflow:
    """
    Manages approval workflow for system changes.

    This system ensures:
    1. User sees proposed actions before execution
    2. User can approve, reject, or modify proposals
    3. Course corrections can be provided
    4. High-risk changes are flagged
    5. Approval history is maintained
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.requests_path = root_path / ".ai_onboard" / "approval_requests.jsonl"
        self.active_requests: Dict[str, ApprovalRequest] = {}

        # Ensure directories exist
        self.requests_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing requests
        self._load_existing_requests()

    def _load_existing_requests(self):
        """Load existing approval requests from storage."""
        try:
            if self.requests_path.exists():
                with open(self.requests_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():

                            data = json.loads(line)
                            request = self._deserialize_request(data)
                            if request.status == ApprovalStatus.PENDING:
                                self.active_requests[request.request_id] = request
        except Exception as e:
            print(f"⚠️ Failed to load approval requests: {e}")

    def _deserialize_request(self, data: Dict[str, Any]) -> ApprovalRequest:
        """Deserialize approval request from JSON data."""
        actions = []
        for action_data in data.get("proposed_actions", []):
            action = ProposedAction(
                action_id=action_data["action_id"],
                change_type=ChangeType(action_data["change_type"]),
                description=action_data["description"],
                rationale=action_data["rationale"],
                risk_level=action_data["risk_level"],
                impact_analysis=action_data["impact_analysis"],
                proposed_steps=action_data["proposed_steps"],
                alternatives=action_data.get("alternatives", []),
                estimated_time=action_data.get("estimated_time", "unknown"),
                rollback_plan=action_data.get("rollback_plan", "none"),
            )
            actions.append(action)

        return ApprovalRequest(
            request_id=data["request_id"],
            timestamp=data["timestamp"],
            proposed_actions=actions,
            context=data["context"],
            urgency=data.get("urgency", "normal"),
            status=ApprovalStatus(data.get("status", "pending")),
            user_feedback=data.get("user_feedback", ""),
            modifications=data.get("modifications", []),
            expires_at=data.get("expires_at"),
        )

    def create_approval_request(
        self,
        proposed_actions: List[ProposedAction],
        context: str,
        urgency: str = "normal",
    ) -> ApprovalRequest:
        """Create a new approval request."""

        request_id = f"req_{int(time.time())}_{len(self.active_requests)}"

        # Set expiration based on urgency
        expires_at = None
        if urgency == "critical":
            expires_at = time.time() + 300  # 5 minutes
        elif urgency == "high":
            expires_at = time.time() + 1800  # 30 minutes
        elif urgency == "normal":
            expires_at = time.time() + 3600  # 1 hour

        request = ApprovalRequest(
            request_id=request_id,
            timestamp=time.time(),
            proposed_actions=proposed_actions,
            context=context,
            urgency=urgency,
            expires_at=expires_at,
        )

        self.active_requests[request_id] = request
        self._save_request(request)

        return request

    def _save_request(self, request: ApprovalRequest):
        """Save approval request to storage."""
        try:
            request_data = {
                "request_id": request.request_id,
                "timestamp": request.timestamp,
                "proposed_actions": [
                    {
                        "action_id": action.action_id,
                        "change_type": action.change_type.value,
                        "description": action.description,
                        "rationale": action.rationale,
                        "risk_level": action.risk_level,
                        "impact_analysis": action.impact_analysis,
                        "proposed_steps": action.proposed_steps,
                        "alternatives": action.alternatives,
                        "estimated_time": action.estimated_time,
                        "rollback_plan": action.rollback_plan,
                    }
                    for action in request.proposed_actions
                ],
                "context": request.context,
                "urgency": request.urgency,
                "status": request.status.value,
                "user_feedback": request.user_feedback,
                "modifications": request.modifications,
                "expires_at": request.expires_at,
            }

            with open(self.requests_path, "a", encoding="utf-8") as f:

                f.write(json.dumps(request_data) + "\n")
        except Exception as e:
            print(f"⚠️ Failed to save approval request: {e}")

    def display_approval_request(self, request: ApprovalRequest):
        """Display approval request to the user."""

        # Urgency emoji mapping
        urgency_emoji = {
            "low": "🟢",
            "normal": "🟡",
            "high": "🟠",
            "critical": "🔴",
        }

        print(f"\n📋 APPROVAL REQUEST")
        print(f"=" * 60)
        print(f"🆔 Request ID: {request.request_id}")
        print(
            f"{urgency_emoji.get(request.urgency, '🟡')} Urgency: {request.urgency.upper()}"
        )
        print(f"📝 Context: {request.context}")

        if request.expires_at:
            time_left = request.expires_at - time.time()
            if time_left > 0:
                print(f"⏰ Expires in: {int(time_left/60)} minutes")
            else:
                print(f"⏰ EXPIRED")

        print(f"\n🎯 PROPOSED ACTIONS:")

        for i, action in enumerate(request.proposed_actions, 1):
            print(f"\n   {i}. {action.description}")
            print(f"      📂 Type: {action.change_type.value}")
            print(f"      ⚠️ Risk: {action.risk_level}")
            print(f"      💭 Rationale: {action.rationale}")
            print(f"      ⏱️ Estimated Time: {action.estimated_time}")

            if action.proposed_steps:
                print(f"      📋 Steps:")
                for step in action.proposed_steps:
                    print(f"         • {step}")

            if action.alternatives:
                print(f"      🔄 Alternatives:")
                for alt in action.alternatives:
                    print(f"         • {alt}")

            if action.rollback_plan != "none":
                print(f"      🔙 Rollback: {action.rollback_plan}")

        print(f"\n" + "=" * 60)
        print(f"Please respond with:")
        print(f"  ✅ APPROVE - Execute all proposed actions")
        print(f"  ❌ REJECT - Cancel all proposed actions")
        print(f"  ✏️ MODIFY - Provide modifications (describe changes)")
        print(f"  ⏰ WAIT - Defer decision (if not urgent)")
        print(f"=" * 60)

    def process_user_response(
        self, request_id: str, response: str, modifications: List[str] = None
    ) -> Dict[str, Any]:
        """Process user response to approval request."""

        if request_id not in self.active_requests:
            return {"error": "Request not found"}

        request = self.active_requests[request_id]

        # Check if request has expired
        if request.expires_at and time.time() > request.expires_at:
            request.status = ApprovalStatus.EXPIRED
            return {"error": "Request has expired"}

        # Process response
        response_lower = response.lower().strip()

        if response_lower in ["approve", "yes", "y", "✅"]:
            request.status = ApprovalStatus.APPROVED
            request.user_feedback = response
            result = {"status": "approved", "message": "Actions approved for execution"}

        elif response_lower in ["reject", "no", "n", "❌"]:
            request.status = ApprovalStatus.REJECTED
            request.user_feedback = response
            result = {"status": "rejected", "message": "Actions rejected"}

        elif response_lower in ["modify", "✏️"] or "modify" in response_lower:
            request.status = ApprovalStatus.MODIFIED
            request.user_feedback = response
            if modifications:
                request.modifications = modifications
            result = {
                "status": "modified",
                "message": "Actions modified based on user feedback",
                "modifications": modifications or [],
            }

        elif response_lower in ["wait", "defer", "⏰"]:
            # Keep as pending, extend expiration
            request.expires_at = time.time() + 3600  # Extend by 1 hour
            result = {"status": "deferred", "message": "Decision deferred"}

        else:
            return {
                "error": (
                    "Invalid response. Please use: approve, reject, modify, or wait"
                )
            }

        # Update request
        self._save_request(request)

        # Remove from active requests if not pending
        if request.status != ApprovalStatus.PENDING:
            del self.active_requests[request_id]

        return result

    def get_pending_requests(self) -> List[ApprovalRequest]:
        """Get all pending approval requests."""
        return [
            req
            for req in self.active_requests.values()
            if req.status == ApprovalStatus.PENDING
        ]

    def check_expired_requests(self):
        """Check for and handle expired requests."""
        current_time = time.time()
        expired_requests = []

        for request_id, request in self.active_requests.items():
            if request.expires_at and current_time > request.expires_at:
                request.status = ApprovalStatus.EXPIRED
                expired_requests.append(request_id)

        # Remove expired requests
        for request_id in expired_requests:
            del self.active_requests[request_id]

        return expired_requests

    def create_quick_approval_request(
        self, action_description: str, risk_level: str = "medium", context: str = ""
    ) -> ApprovalRequest:
        """Create a quick approval request for simple actions."""

        action = ProposedAction(
            action_id=f"quick_{int(time.time())}",
            change_type=ChangeType.SYSTEM_CHANGE,
            description=action_description,
            rationale="User requested action",
            risk_level=risk_level,
            impact_analysis={"impact": "unknown", "scope": "limited"},
            proposed_steps=[action_description],
            estimated_time="unknown",
            rollback_plan="manual",
        )

        return self.create_approval_request(
            proposed_actions=[action],
            context=context or "Quick approval request",
            urgency="normal",
        )

    def get_approval_summary(self) -> Dict[str, Any]:
        """Get summary of approval requests."""
        pending_count = len(self.get_pending_requests())
        total_requests = len(self.active_requests)

        return {
            "pending_requests": pending_count,
            "total_active_requests": total_requests,
            "expired_requests": len(self.check_expired_requests()),
            "recent_requests": [
                {
                    "id": req.request_id,
                    "context": req.context,
                    "urgency": req.urgency,
                    "status": req.status.value,
                    "actions_count": len(req.proposed_actions),
                }
                for req in list(self.active_requests.values())[-5:]
            ],
        }


def get_approval_workflow(root_path: Path) -> ApprovalWorkflow:
    """Get the global approval workflow instance."""
    global _approval_workflow_instance
    if _approval_workflow_instance is None:
        _approval_workflow_instance = ApprovalWorkflow(root_path)
    return _approval_workflow_instance


# Global instance
_approval_workflow_instance: Optional[ApprovalWorkflow] = None
