"""
API Models - Pydantic models for request / response schemas.

This module defines the data models used by the AI Onboard API for
request validation, response serialization, and documentation generation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BaseAPIResponse(BaseModel):
    """Base API response model."""

    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ProjectAnalysisRequest(BaseModel):
    """Request model for project analysis."""

    allow_exec: bool = Field(default=False, description="Allow external probes")
    target_path: Optional[str] = Field(
        default=None, description="Specific path to analyze"
    )


class ProjectAnalysisResponse(BaseModel):
    """Response model for project analysis."""

    project_type: str
    languages: List[str]
    frameworks: List[str]
    components: List[Dict[str, Any]]
    recommendations: List[str]
    confidence_score: float = Field(ge=0, le=1)
    analysis_timestamp: datetime


class CharterRequest(BaseModel):
    """Request model for charter creation."""

    vision: str = Field(description="Project vision statement")
    goals: List[str] = Field(description="Project goals")
    success_criteria: List[str] = Field(description="Success criteria")
    constraints: Optional[List[str]] = Field(
        default=None, description="Project constraints"
    )
    stakeholders: Optional[List[str]] = Field(
        default=None, description="Key stakeholders"
    )
    interactive: bool = Field(default=False, description="Interactive charter creation")


class CharterResponse(BaseModel):
    """Response model for charter creation."""

    charter_id: str
    vision: str
    goals: List[str]
    success_criteria: List[str]
    constraints: List[str]
    stakeholders: List[str]
    created_at: datetime
    status: str


class PlanRequest(BaseModel):
    """Request model for plan generation."""

    charter_id: Optional[str] = Field(
        default=None, description="Charter to base plan on"
    )
    methodology: str = Field(default="agile", description="Planning methodology")
    timeline_weeks: Optional[int] = Field(default=None, description="Target timeline")


class PlanResponse(BaseModel):
    """Response model for plan generation."""

    plan_id: str
    methodology: str
    total_tasks: int
    milestones: List[Dict[str, Any]]
    critical_path: List[str]
    estimated_duration: int
    created_at: datetime


class ValidationRequest(BaseModel):
    """Request model for validation."""

    generate_report: bool = Field(
        default=True, description="Generate validation report"
    )
    components: Optional[List[str]] = Field(
        default=None, description="Specific components to validate"
    )


class ValidationResponse(BaseModel):
    """Response model for validation."""

    validation_id: str
    overall_score: float = Field(ge=0, le=1)
    components: List[Dict[str, Any]]
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    report_path: Optional[str] = None
    validated_at: datetime


class ProjectStatus(BaseModel):
    """Project status model."""

    project_root: str
    current_phase: str
    overall_progress: float = Field(ge=0, le=100)
    completed_tasks: int
    total_tasks: int
    active_milestones: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    health_status: str
    last_updated: datetime


class AgentRegistrationRequest(BaseModel):
    """Request model for agent registration."""

    agent_id: str = Field(description="Unique agent identifier")
    name: str = Field(description="Human - readable agent name")
    version: str = Field(description="Agent version")
    capabilities: List[str] = Field(description="Agent capabilities")
    collaboration_mode: str = Field(description="Collaboration mode")
    safety_level: str = Field(description="Safety level")
    max_autonomous_actions: int = Field(default=5, description="Max autonomous actions")
    requires_confirmation_for: List[str] = Field(
        default=[], description="Actions requiring confirmation"
    )


class AgentRegistrationResponse(BaseModel):
    """Response model for agent registration."""

    agent_id: str
    registration_token: str
    session_timeout: int
    allowed_commands: List[str]
    safety_constraints: Dict[str, Any]
    registered_at: datetime


class SessionCreateRequest(BaseModel):
    """Request model for session creation."""

    agent_id: str
    user_id: str = Field(default="api_user")
    session_context: Optional[Dict[str, Any]] = Field(default=None)


class SessionCreateResponse(BaseModel):
    """Response model for session creation."""

    session_id: str
    agent_id: str
    user_id: str
    expires_at: datetime
    collaboration_mode: str
    safety_level: str
    created_at: datetime


class CommandExecutionRequest(BaseModel):
    """Request model for command execution."""

    command: str = Field(description="Command to execute")
    args: Optional[List[str]] = Field(default=None, description="Command arguments")
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Execution context"
    )
    require_confirmation: bool = Field(
        default=False, description="Require user confirmation"
    )


class CommandExecutionResponse(BaseModel):
    """Response model for command execution."""

    execution_id: str
    command: str
    status: str  # pending, running, completed, failed, requires_confirmation
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    confirmation_required: bool = False
    confirmation_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class NaturalLanguageRequest(BaseModel):
    """Request model for natural language command translation."""

    text: str = Field(description="Natural language text")
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional context"
    )


class NaturalLanguageResponse(BaseModel):
    """Response model for natural language translation."""

    original_text: str
    translated_command: Optional[str] = None
    suggested_args: List[str] = []
    confidence: float = Field(ge=0, le=1)
    alternatives: List[Dict[str, Any]] = []
    requires_clarification: bool = False
    clarification_questions: List[str] = []


class MetricsQuery(BaseModel):
    """Request model for metrics queries."""

    metric_name: Optional[str] = Field(default=None, description="Specific metric name")
    source: Optional[str] = Field(default=None, description="Metric source")
    category: Optional[str] = Field(default=None, description="Metric category")
    start_time: Optional[datetime] = Field(
        default=None, description="Start time filter"
    )
    end_time: Optional[datetime] = Field(default=None, description="End time filter")
    limit: int = Field(default=100, description="Maximum results")
    aggregation: Optional[str] = Field(default=None, description="Aggregation function")


class MetricsResponse(BaseModel):
    """Response model for metrics queries."""

    total_count: int
    metrics: List[Dict[str, Any]]
    aggregated_value: Optional[float] = None
    query_time_ms: float
    next_cursor: Optional[str] = None


class WebSocketMessage(BaseModel):
    """WebSocket message model."""

    type: str = Field(description="Message type")
    data: Dict[str, Any] = Field(description="Message data")
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: Optional[str] = Field(default=None, description="Session ID")


class ProgressUpdate(BaseModel):
    """Progress update model for WebSocket."""

    operation_id: str
    operation_type: str
    progress_percentage: float = Field(ge=0, le=100)
    current_step: str
    total_steps: int
    completed_steps: int
    estimated_remaining_seconds: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class AlertNotification(BaseModel):
    """Alert notification model for WebSocket."""

    alert_id: str
    severity: str  # low, medium, high, critical
    title: str
    message: str
    source: str
    requires_action: bool = False
    suggested_actions: List[str] = []
    expires_at: Optional[datetime] = None


class SystemStatus(BaseModel):
    """System status model."""

    status: str  # healthy, degraded, critical
    uptime_seconds: int
    active_sessions: int
    active_operations: int
    system_load: Dict[str, float]
    last_health_check: datetime
    components: Dict[str, str]  # component_name -> status


class ErrorDetail(BaseModel):
    """Error detail model for API responses."""

    error_code: str
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    suggested_resolution: Optional[str] = None


# Enums for validation


class CollaborationMode(str, Enum):
    ASSISTIVE = "assistive"
    AUTONOMOUS = "autonomous"
    COLLABORATIVE = "collaborative"
    SUPERVISED = "supervised"


class SafetyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentCapability(str, Enum):
    VISION_DEFINITION = "vision_definition"
    PROJECT_ANALYSIS = "project_analysis"
    PLANNING = "planning"
    CODE_GENERATION = "code_generation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DEBUGGING = "debugging"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"


class CommandStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    CANCELLED = "cancelled"


class WebSocketMessageType(str, Enum):
    PROGRESS_UPDATE = "progress_update"
    ALERT_NOTIFICATION = "alert_notification"
    SYSTEM_STATUS = "system_status"
    SESSION_UPDATE = "session_update"
    COMMAND_RESULT = "command_result"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
