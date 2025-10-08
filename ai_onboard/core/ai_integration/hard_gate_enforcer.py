"""
Hard Gate Enforcer - Provides mandatory blocking enforcement for critical decisions.

This module implements hard enforcement where AI agents are completely blocked
from proceeding with certain operations until explicit approval is granted.
"""

import json
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..base import utils
from .ai_gate_mediator import get_ai_gate_mediator


class EnforcementLevel(Enum):
    """Levels of enforcement strictness."""

    SOFT = "soft"  # Just create gate, agent can continue
    MEDIUM = "medium"  # Agent waits for approval but can timeout
    HARD = "hard"  # Agent completely blocked until approval


class BlockReason(Enum):
    """Reasons why operations are blocked."""

    LOW_CONFIDENCE = "low_confidence"
    CRITICAL_DECISION = "critical_decision"
    VIOLATES_VISION = "violates_vision"
    EXCEEDS_LIMITS = "exceeds_limits"
    REQUIRES_APPROVAL = "requires_approval"


@dataclass
class BlockRule:
    """Rule for blocking operations."""

    operation_pattern: str  # Pattern to match operation names
    enforcement_level: EnforcementLevel
    block_reason: BlockReason
    timeout_seconds: int = 300  # 5 minutes default
    requires_approval: bool = True


@dataclass
class ActiveBlock:
    """Currently active block on an operation."""

    block_id: str
    agent_id: str
    operation: str
    block_reason: BlockReason
    enforcement_level: EnforcementLevel
    created_at: float
    timeout_at: float
    approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[float] = None


class HardGateEnforcer:
    """
    Hard gate enforcer that provides mandatory blocking for critical operations.

    Unlike soft gates that just create approval requests, this system actually
    blocks agent execution until approval is granted.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ai_onboard_dir = project_root / ".ai_onboard"
        self.blocks_dir = self.ai_onboard_dir / "active_blocks"

        # Ensure directories exist
        self.ai_onboard_dir.mkdir(exist_ok=True)
        self.blocks_dir.mkdir(exist_ok=True)

        # Core systems
        self.gate_mediator = get_ai_gate_mediator(project_root)
        # Decision enforcer will be initialized lazily to avoid circular imports

        # Active blocks tracking
        self.active_blocks: Dict[str, ActiveBlock] = {}
        self.block_rules: List[BlockRule] = []

        # Monitoring and cleanup
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.scan_interval = 10.0  # seconds

        # Load existing blocks
        self._load_active_blocks()

        # Setup default block rules
        self._setup_default_rules()

        # Start monitoring
        self.start_monitoring()

    def start_monitoring(self) -> None:
        """Start monitoring for expired blocks and cleanup."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop monitoring."""
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)

        self._save_active_blocks()

    def should_block_operation(
        self, agent_id: str, operation: str, context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[BlockReason]]:
        """
        Check if an operation should be blocked.

        Returns:
            (should_block, block_id, reason)
        """
        # Check existing active blocks for this agent/operation
        for block_id, block in self.active_blocks.items():
            if (
                block.agent_id == agent_id
                and block.operation == operation
                and not block.approved
                and time.time() < block.timeout_at
            ):
                return True, block_id, block.block_reason

        # Check block rules
        for rule in self.block_rules:
            if rule.operation_pattern.lower() in operation.lower():
                block_id = f"block_{agent_id}_{operation}_{int(time.time())}"

                # Create active block
                active_block = ActiveBlock(
                    block_id=block_id,
                    agent_id=agent_id,
                    operation=operation,
                    block_reason=rule.block_reason,
                    enforcement_level=rule.enforcement_level,
                    created_at=time.time(),
                    timeout_at=time.time() + rule.timeout_seconds,
                )

                self.active_blocks[block_id] = active_block
                self._save_active_blocks()

                # Log the block
                self._log_blocked_operation(active_block)

                return True, block_id, rule.block_reason

        return False, None, None

    def approve_block(self, block_id: str, approver: str = "vibe_coder") -> bool:
        """Approve a blocked operation."""
        if block_id not in self.active_blocks:
            return False

        block = self.active_blocks[block_id]
        block.approved = True
        block.approved_by = approver
        block.approved_at = time.time()

        # Log approval
        self._log_approval(block, approver)

        # Save state
        self._save_active_blocks()

        return True

    def reject_block(self, block_id: str, rejector: str = "vibe_coder") -> bool:
        """Reject a blocked operation (permanent block)."""
        if block_id not in self.active_blocks:
            return False

        block = self.active_blocks[block_id]
        block.approved = False  # Permanent rejection
        block.approved_by = rejector
        block.approved_at = time.time()

        # Log rejection
        self._log_rejection(block, rejector)

        # Save state
        self._save_active_blocks()

        return True

    def get_active_blocks(self, agent_id: Optional[str] = None) -> List[ActiveBlock]:
        """Get all active blocks, optionally filtered by agent."""
        current_time = time.time()

        # Clean up expired blocks
        expired_blocks = []
        for block_id, block in self.active_blocks.items():
            if current_time > block.timeout_at and not block.approved:
                expired_blocks.append(block_id)

        for block_id in expired_blocks:
            del self.active_blocks[block_id]

        # Filter by agent if specified
        if agent_id:
            return [
                block
                for block in self.active_blocks.values()
                if block.agent_id == agent_id and not block.approved
            ]

        return [block for block in self.active_blocks.values() if not block.approved]

    def get_block_status(self, block_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific block."""
        if block_id not in self.active_blocks:
            return None

        block = self.active_blocks[block_id]
        current_time = time.time()

        return {
            "block_id": block.block_id,
            "agent_id": block.agent_id,
            "operation": block.operation,
            "block_reason": block.block_reason.value,
            "enforcement_level": block.enforcement_level.value,
            "created_at": block.created_at,
            "timeout_at": block.timeout_at,
            "approved": block.approved,
            "approved_by": block.approved_by,
            "approved_at": block.approved_at,
            "time_remaining": max(0, block.timeout_at - current_time),
            "is_expired": current_time > block.timeout_at,
        }

    def add_block_rule(
        self,
        operation_pattern: str,
        enforcement_level: EnforcementLevel,
        block_reason: BlockReason,
        timeout_seconds: int = 300,
    ) -> None:
        """Add a new block rule."""
        rule = BlockRule(
            operation_pattern=operation_pattern,
            enforcement_level=enforcement_level,
            block_reason=block_reason,
            timeout_seconds=timeout_seconds,
        )

        self.block_rules.append(rule)

    def remove_block_rule(self, operation_pattern: str) -> bool:
        """Remove a block rule."""
        for i, rule in enumerate(self.block_rules):
            if rule.operation_pattern == operation_pattern:
                del self.block_rules[i]
                return True
        return False

    def _setup_default_rules(self) -> None:
        """Setup default block rules for common dangerous operations."""
        default_rules = [
            # Critical file operations
            BlockRule(
                operation_pattern="delete.*file",
                enforcement_level=EnforcementLevel.HARD,
                block_reason=BlockReason.CRITICAL_DECISION,
                timeout_seconds=600,  # 10 minutes
            ),
            BlockRule(
                operation_pattern="refactor.*file",
                enforcement_level=EnforcementLevel.HARD,
                block_reason=BlockReason.EXCEEDS_LIMITS,
                timeout_seconds=300,
            ),
            # Dependency management
            BlockRule(
                operation_pattern="add.*depend",
                enforcement_level=EnforcementLevel.MEDIUM,
                block_reason=BlockReason.VIOLATES_VISION,
                timeout_seconds=180,
            ),
            # Architecture decisions
            BlockRule(
                operation_pattern="choose.*framework",
                enforcement_level=EnforcementLevel.HARD,
                block_reason=BlockReason.CRITICAL_DECISION,
                timeout_seconds=600,
            ),
            BlockRule(
                operation_pattern="database.*design",
                enforcement_level=EnforcementLevel.HARD,
                block_reason=BlockReason.CRITICAL_DECISION,
                timeout_seconds=600,
            ),
            # Large scale operations
            BlockRule(
                operation_pattern=".*10.*file",
                enforcement_level=EnforcementLevel.MEDIUM,
                block_reason=BlockReason.EXCEEDS_LIMITS,
                timeout_seconds=300,
            ),
        ]

        self.block_rules.extend(default_rules)

    def _monitoring_loop(self) -> None:
        """Monitor for expired blocks and cleanup."""
        while self.monitoring_active:
            try:
                current_time = time.time()

                # Clean up expired blocks
                expired_blocks = []
                for block_id, block in self.active_blocks.items():
                    if (
                        current_time > block.timeout_at
                        and not block.approved
                        and block.enforcement_level != EnforcementLevel.HARD
                    ):
                        expired_blocks.append(block_id)

                        # Log timeout
                        self._log_timeout(block)

                # Remove expired blocks
                for block_id in expired_blocks:
                    del self.active_blocks[block_id]

                # Save state periodically
                if expired_blocks:
                    self._save_active_blocks()

                time.sleep(self.scan_interval)

            except Exception as e:
                print(f"Warning: Block monitoring error: {e}")
                time.sleep(self.scan_interval)

    def _log_blocked_operation(self, block: ActiveBlock) -> None:
        """Log a blocked operation."""
        try:
            # Log to dashboard
            from .agent_oversight_dashboard import AgentOversightDashboard

            dashboard = AgentOversightDashboard(self.project_root)
            dashboard.log_blocked_action(
                agent_id=block.agent_id,
                action_type=f"Blocked: {block.operation}",
                reason=f"Hard enforcement: {block.block_reason.value}",
                severity="error",
            )

            # Also log to session log
            log_entry = {
                "timestamp": time.time(),
                "type": "hard_block",
                "block_id": block.block_id,
                "agent_id": block.agent_id,
                "operation": block.operation,
                "reason": block.block_reason.value,
                "enforcement_level": block.enforcement_level.value,
            }

            session_log_path = self.ai_onboard_dir / "session_log.jsonl"
            with open(session_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            print(f"Warning: Failed to log blocked operation: {e}")

    def _log_approval(self, block: ActiveBlock, approver: str) -> None:
        """Log an approval."""
        try:
            log_entry = {
                "timestamp": time.time(),
                "type": "block_approved",
                "block_id": block.block_id,
                "agent_id": block.agent_id,
                "operation": block.operation,
                "approved_by": approver,
                "approval_time": block.approved_at,
            }

            session_log_path = self.ai_onboard_dir / "session_log.jsonl"
            with open(session_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            print(f"Warning: Failed to log approval: {e}")

    def _log_rejection(self, block: ActiveBlock, rejector: str) -> None:
        """Log a rejection."""
        try:
            log_entry = {
                "timestamp": time.time(),
                "type": "block_rejected",
                "block_id": block.block_id,
                "agent_id": block.agent_id,
                "operation": block.operation,
                "rejected_by": rejector,
                "rejection_time": block.approved_at,
            }

            session_log_path = self.ai_onboard_dir / "session_log.jsonl"
            with open(session_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            print(f"Warning: Failed to log rejection: {e}")

    def _log_timeout(self, block: ActiveBlock) -> None:
        """Log a block timeout."""
        try:
            log_entry = {
                "timestamp": time.time(),
                "type": "block_timeout",
                "block_id": block.block_id,
                "agent_id": block.agent_id,
                "operation": block.operation,
                "timeout_at": block.timeout_at,
            }

            session_log_path = self.ai_onboard_dir / "session_log.jsonl"
            with open(session_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            print(f"Warning: Failed to log timeout: {e}")

    def _load_active_blocks(self) -> None:
        """Load active blocks from storage."""
        try:
            blocks_file = self.blocks_dir / "active_blocks.json"
            if blocks_file.exists():
                blocks_data = utils.read_json(blocks_file)

                for block_id, block_data in blocks_data.items():
                    # Convert back to ActiveBlock
                    block = ActiveBlock(
                        block_id=block_data["block_id"],
                        agent_id=block_data["agent_id"],
                        operation=block_data["operation"],
                        block_reason=BlockReason(block_data["block_reason"]),
                        enforcement_level=EnforcementLevel(
                            block_data["enforcement_level"]
                        ),
                        created_at=block_data["created_at"],
                        timeout_at=block_data["timeout_at"],
                        approved=block_data.get("approved", False),
                        approved_by=block_data.get("approved_by"),
                        approved_at=block_data.get("approved_at"),
                    )

                    self.active_blocks[block_id] = block

        except Exception as e:
            print(f"Warning: Could not load active blocks: {e}")

    def _save_active_blocks(self) -> None:
        """Save active blocks to storage."""
        try:
            blocks_data = {}
            for block_id, block in self.active_blocks.items():
                blocks_data[block_id] = {
                    "block_id": block.block_id,
                    "agent_id": block.agent_id,
                    "operation": block.operation,
                    "block_reason": block.block_reason.value,
                    "enforcement_level": block.enforcement_level.value,
                    "created_at": block.created_at,
                    "timeout_at": block.timeout_at,
                    "approved": block.approved,
                    "approved_by": block.approved_by,
                    "approved_at": block.approved_at,
                }

            blocks_file = self.blocks_dir / "active_blocks.json"
            utils.write_json(blocks_file, blocks_data)

        except Exception as e:
            print(f"Warning: Could not save active blocks: {e}")

    def get_enforcement_status(self) -> Dict[str, Any]:
        """Get current enforcement status."""
        current_time = time.time()

        active_blocks = len(self.active_blocks)
        expired_blocks = sum(
            1
            for block in self.active_blocks.values()
            if current_time > block.timeout_at and not block.approved
        )

        return {
            "enforcement_active": self.monitoring_active,
            "total_active_blocks": active_blocks,
            "expired_blocks": expired_blocks,
            "total_block_rules": len(self.block_rules),
            "monitoring_uptime": time.time() - (self._get_start_time() or time.time()),
        }

    def _get_start_time(self) -> Optional[float]:
        """Get approximate start time from oldest block."""
        if not self.active_blocks:
            return None

        oldest_block = min(self.active_blocks.values(), key=lambda b: b.created_at)
        return oldest_block.created_at


def get_hard_gate_enforcer(project_root: Path) -> HardGateEnforcer:
    """Get or create hard gate enforcer for the project."""
    return HardGateEnforcer(project_root)
