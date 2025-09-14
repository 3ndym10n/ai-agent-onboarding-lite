"""
AI Onboard API Server - FastAPI server for external integrations.

This module provides a REST API server that allows external tools like Cursor AI
to integrate with the AI Agent Onboarding system programmatically.
"""

import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from fastapi import (
        BackgroundTasks,
        FastAPI,
        HTTPException,
        WebSocket,
        WebSocketDisconnect,
    )
    from fastapi.middleware.cors import CORSMiddleware

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from ..core import (
    analysis_lite,
    charter,
    planning,
    validation_runtime,
)
from ..core.ai_agent_collaboration_protocol import get_collaboration_protocol
from ..core.cursor_ai_integration import get_cursor_integration
from ..core.unified_metrics_collector import get_unified_metrics_collector
from .models import (
    AgentRegistrationRequest,
    AgentRegistrationResponse,
    APIResponse,
    CharterRequest,
    CommandExecutionRequest,
    CommandExecutionResponse,
    CommandStatus,
    MetricsQuery,
    MetricsResponse,
    NaturalLanguageRequest,
    NaturalLanguageResponse,
    PlanRequest,
    ProjectAnalysisRequest,
    ProjectStatus,
    SessionCreateRequest,
    SessionCreateResponse,
    SystemStatus,
    ValidationRequest,
    WebSocketMessageType,
)


class AIOnboardAPIServer:
    """Main API server for AI Onboard integrations."""

    def __init__(self, root: Path, host: str = "127.0.0.1", port: int = 8080):
        if not FASTAPI_AVAILABLE:
            raise ImportError(
                "FastAPI is required for API server. Install with: pip install fastapi uvicorn"
            )

        self.root = root
        self.host = host
        self.port = port

        # Initialize core components
        self.cursor_integration = get_cursor_integration(root)
        self.collaboration_protocol = get_collaboration_protocol(root)
        self.metrics_collector = get_unified_metrics_collector(root)

        # Active operations and WebSocket connections
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}

        # Create FastAPI app
        self.app = self._create_app()

        # Security - Initialize safely with error handling
        try:
            if FASTAPI_AVAILABLE:
                from fastapi.security import HTTPBearer

                self.security = HTTPBearer(auto_error=False)
            else:
                self.security = None
        except Exception as e:
            print(f"Warning: Could not initialize security: {e}")
            self.security = None

    def _get_auth_dependency(self):
        """Get authentication dependency (conditional based on FastAPI availability)."""
        if FASTAPI_AVAILABLE and self.security:
            from fastapi import Depends

            return Depends(self.security)
        else:
            return None

    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        app = FastAPI(
            title="AI Onboard API",
            description="REST API for AI Agent Onboarding system integration",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
        )

        # CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add routes
        self._add_routes(app)

        return app

    def _add_routes(self, app: FastAPI):
        """Add API routes to the FastAPI app."""

        # Health check
        @app.get("/health", response_model=SystemStatus)
        async def health_check():
            """Health check endpoint."""
            return SystemStatus(
                status="healthy",
                uptime_seconds=int(time.time()),
                active_sessions=len(self.websocket_connections),
                active_operations=len(self.active_operations),
                system_load={"cpu": 0.0, "memory": 0.0},  # Can be enhanced
                last_health_check=datetime.now(),
                components={"api": "healthy", "core": "healthy"},
            )

        # Project operations
        @app.post("/api / v1 / project / analyze", response_model=APIResponse)
        async def analyze_project(
            request: ProjectAnalysisRequest,
            background_tasks: BackgroundTasks,
            # auth: Optional[HTTPAuthorizationCredentials] = None  # Disabled for now
        ):
            """Analyze project structure and generate recommendations."""
            operation_id = str(uuid.uuid4())

            try:
                # Start background analysis
                background_tasks.add_task(
                    self._run_analysis,
                    operation_id,
                    request.allow_exec,
                    request.target_path,
                )

                return APIResponse(
                    success=True,
                    message="Project analysis started",
                    data={"operation_id": operation_id, "status": "running"},
                )

            except Exception as e:
                return APIResponse(success=False, error=str(e))

        @app.post("/api / v1 / project / charter", response_model=APIResponse)
        async def create_charter(
            request: CharterRequest,
            background_tasks: BackgroundTasks,
            # auth: Optional[HTTPAuthorizationCredentials] = None  # Disabled for now
        ):
            """Create or update project charter."""
            operation_id = str(uuid.uuid4())

            try:
                background_tasks.add_task(
                    self._run_charter_creation, operation_id, request
                )

                return APIResponse(
                    success=True,
                    message="Charter creation started",
                    data={"operation_id": operation_id, "status": "running"},
                )

            except Exception as e:
                return APIResponse(success=False, error=str(e))

        @app.post("/api / v1 / project / plan", response_model=APIResponse)
        async def create_plan(
            request: PlanRequest,
            background_tasks: BackgroundTasks,
            # auth: Optional[HTTPAuthorizationCredentials] = None  # Disabled for now
        ):
            """Generate project plan from charter."""
            operation_id = str(uuid.uuid4())

            try:
                background_tasks.add_task(
                    self._run_plan_generation, operation_id, request
                )

                return APIResponse(
                    success=True,
                    message="Plan generation started",
                    data={"operation_id": operation_id, "status": "running"},
                )

            except Exception as e:
                return APIResponse(success=False, error=str(e))

        @app.post("/api / v1 / project / validate", response_model=APIResponse)
        async def validate_project(
            request: ValidationRequest,
            background_tasks: BackgroundTasks,
            # auth: Optional[HTTPAuthorizationCredentials] = None  # Disabled for now
        ):
            """Run project validation."""
            operation_id = str(uuid.uuid4())

            try:
                background_tasks.add_task(self._run_validation, operation_id, request)

                return APIResponse(
                    success=True,
                    message="Validation started",
                    data={"operation_id": operation_id, "status": "running"},
                )

            except Exception as e:
                return APIResponse(success=False, error=str(e))

        @app.get("/api / v1 / project / status", response_model=ProjectStatus)
        async def get_project_status():
            """Get current project status and progress."""
            try:
                # Get project context from Cursor integration
                context = self.cursor_integration.get_project_context_for_cursor()

                progress = context.get("progress", {})

                return ProjectStatus(
                    project_root=str(self.root),
                    current_phase=progress.get("current_phase", "unknown"),
                    overall_progress=progress.get("overall_progress", 0),
                    completed_tasks=progress.get("completed_tasks", 0),
                    total_tasks=progress.get("total_tasks", 0),
                    active_milestones=[],  # Can be enhanced
                    recent_activity=[],  # Can be enhanced
                    health_status="healthy",
                    last_updated=datetime.now(),
                )

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Agent collaboration endpoints
        @app.post(
            "/api / v1 / agents / register", response_model=AgentRegistrationResponse
        )
        async def register_agent(request: AgentRegistrationRequest):
            """Register an AI agent for collaboration."""
            try:
                # Create agent profile
                from ..core.ai_agent_collaboration_protocol import (
                    AgentCapability,
                    AgentProfile,
                    CollaborationMode,
                    SafetyLevel,
                )

                # Map string values to enums
                mode_map = {
                    "assistive": CollaborationMode.ASSISTIVE,
                    "autonomous": CollaborationMode.AUTONOMOUS,
                    "collaborative": CollaborationMode.COLLABORATIVE,
                    "supervised": CollaborationMode.SUPERVISED,
                }

                safety_map = {
                    "low": SafetyLevel.LOW,
                    "medium": SafetyLevel.MEDIUM,
                    "high": SafetyLevel.HIGH,
                    "critical": SafetyLevel.CRITICAL,
                }

                capability_map = {
                    "vision_definition": AgentCapability.VISION_DEFINITION,
                    "project_analysis": AgentCapability.PROJECT_ANALYSIS,
                    "planning": AgentCapability.PLANNING,
                    "code_generation": AgentCapability.CODE_GENERATION,
                    "testing": AgentCapability.TESTING,
                    "documentation": AgentCapability.DOCUMENTATION,
                    "debugging": AgentCapability.DEBUGGING,
                    "deployment": AgentCapability.DEPLOYMENT,
                    "maintenance": AgentCapability.MAINTENANCE,
                }

                capabilities = [
                    capability_map.get(cap)
                    for cap in request.capabilities
                    if cap in capability_map
                ]

                agent_profile = AgentProfile(
                    agent_id=request.agent_id,
                    name=request.name,
                    version=request.version,
                    capabilities=capabilities,
                    collaboration_mode=mode_map.get(
                        request.collaboration_mode, CollaborationMode.COLLABORATIVE
                    ),
                    safety_level=safety_map.get(
                        request.safety_level, SafetyLevel.MEDIUM
                    ),
                    max_autonomous_actions=request.max_autonomous_actions,
                    requires_confirmation_for=request.requires_confirmation_for,
                )

                # Register with collaboration protocol
                result = self.collaboration_protocol.register_agent(agent_profile)

                if result.get("success"):
                    return AgentRegistrationResponse(
                        agent_id=request.agent_id,
                        registration_token=str(uuid.uuid4()),  # Generate token
                        session_timeout=agent_profile.session_timeout,
                        allowed_commands=["analyze", "charter", "plan", "validate"],
                        safety_constraints={
                            "max_autonomous_actions": agent_profile.max_autonomous_actions,
                            "requires_confirmation": agent_profile.requires_confirmation_for,
                        },
                        registered_at=datetime.now(),
                    )
                else:
                    raise HTTPException(status_code=400, detail=result.get("error"))

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post(
            "/api / v1 / agents / session / create",
            response_model=SessionCreateResponse,
        )
        async def create_session(request: SessionCreateRequest):
            """Create a collaboration session."""
            try:
                result = self.collaboration_protocol.start_session(
                    agent_id=request.agent_id,
                    user_id=request.user_id,
                    session_context=request.session_context or {},
                )

                if result.get("success"):
                    session = result["session"]
                    return SessionCreateResponse(
                        session_id=result["session_id"],
                        agent_id=request.agent_id,
                        user_id=request.user_id,
                        expires_at=datetime.now(),  # Can be calculated properly
                        collaboration_mode=session.collaboration_mode.value,
                        safety_level=session.safety_level.value,
                        created_at=datetime.now(),
                    )
                else:
                    raise HTTPException(status_code=400, detail=result.get("error"))

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post(
            "/api / v1 / agents / session/{session_id}/command",
            response_model=CommandExecutionResponse,
        )
        async def execute_command(
            session_id: str,
            request: CommandExecutionRequest,
            background_tasks: BackgroundTasks,
        ):
            """Execute a command within a collaboration session."""
            execution_id = str(uuid.uuid4())

            try:
                # Start background command execution
                background_tasks.add_task(
                    self._execute_session_command, execution_id, session_id, request
                )

                return CommandExecutionResponse(
                    execution_id=execution_id,
                    command=request.command,
                    status=CommandStatus.PENDING,
                    started_at=datetime.now(),
                )

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Natural language processing
        @app.post("/api / v1 / translate", response_model=NaturalLanguageResponse)
        async def translate_natural_language(request: NaturalLanguageRequest):
            """Translate natural language to AI Onboard commands."""
            try:
                result = self.cursor_integration.translate_natural_language_command(
                    request.text
                )

                return NaturalLanguageResponse(
                    original_text=request.text,
                    translated_command=result.get("command"),
                    suggested_args=result.get("suggested_args", []),
                    confidence=result.get("confidence", 0.0),
                    alternatives=[],
                    requires_clarification=not result.get("success", False),
                )

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Metrics endpoints
        @app.post("/api / v1 / metrics / query", response_model=MetricsResponse)
        async def query_metrics(request: MetricsQuery):
            """Query collected metrics."""
            try:
                from ..core.unified_metrics_collector import (
                    MetricCategory,
                    MetricQuery,
                    MetricSource,
                )

                # Build metric query
                query = MetricQuery(
                    name_pattern=request.metric_name,
                    start_time=request.start_time,
                    end_time=request.end_time,
                    limit=request.limit,
                    aggregation=request.aggregation,
                )

                if request.source:
                    query.source = MetricSource(request.source)
                if request.category:
                    query.category = MetricCategory(request.category)

                # Execute query
                result = self.metrics_collector.query_metrics(query)

                # Convert metrics to dict format
                metrics_data = []
                for metric in result.metrics:
                    metrics_data.append(
                        {
                            "id": metric.id,
                            "name": metric.name,
                            "value": metric.value,
                            "source": metric.source.value,
                            "category": metric.category.value,
                            "timestamp": metric.timestamp.isoformat(),
                            "unit": metric.unit,
                            "dimensions": metric.dimensions,
                        }
                    )

                return MetricsResponse(
                    total_count=result.total_count,
                    metrics=metrics_data,
                    aggregated_value=result.aggregated_value,
                    query_time_ms=result.query_time_ms,
                )

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # WebSocket endpoint
        @app.websocket("/api / v1 / ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: str):
            """WebSocket endpoint for real-time updates."""
            await websocket.accept()
            self.websocket_connections[client_id] = websocket

            try:
                # Send initial connection confirmation
                await self._send_websocket_message(
                    client_id,
                    {
                        "type": WebSocketMessageType.SYSTEM_STATUS,
                        "data": {"connected": True, "client_id": client_id},
                    },
                )

                # Keep connection alive and handle incoming messages
                while True:
                    try:
                        data = await websocket.receive_text()
                        message = json.loads(data)

                        # Handle incoming WebSocket messages
                        await self._handle_websocket_message(client_id, message)

                    except WebSocketDisconnect:
                        break
                    except json.JSONDecodeError:
                        await self._send_websocket_message(
                            client_id,
                            {
                                "type": WebSocketMessageType.ERROR,
                                "data": {"error": "Invalid JSON message"},
                            },
                        )
                    except Exception as e:
                        await self._send_websocket_message(
                            client_id,
                            {
                                "type": WebSocketMessageType.ERROR,
                                "data": {"error": str(e)},
                            },
                        )

            except WebSocketDisconnect:
                pass
            finally:
                if client_id in self.websocket_connections:
                    del self.websocket_connections[client_id]

    # Background task methods
    async def _run_analysis(
        self, operation_id: str, allow_exec: bool, target_path: Optional[str]
    ):
        """Run project analysis in background."""
        self.active_operations[operation_id] = {
            "type": "analysis",
            "status": "running",
            "started_at": datetime.now(),
        }

        try:
            # Send progress update
            await self._broadcast_progress_update(
                operation_id, "analysis", 10, "Starting project analysis", 1, 5
            )

            # Run analysis
            result = analysis_lite.analyze_project(self.root, allow_exec=allow_exec)

            await self._broadcast_progress_update(
                operation_id, "analysis", 100, "Analysis completed", 5, 5
            )

            # Update operation status
            self.active_operations[operation_id].update(
                {
                    "status": "completed",
                    "result": result,
                    "completed_at": datetime.now(),
                }
            )

        except Exception as e:
            self.active_operations[operation_id].update(
                {"status": "failed", "error": str(e), "completed_at": datetime.now()}
            )

    async def _run_charter_creation(self, operation_id: str, request: CharterRequest):
        """Run charter creation in background."""
        self.active_operations[operation_id] = {
            "type": "charter",
            "status": "running",
            "started_at": datetime.now(),
        }

        try:
            await self._broadcast_progress_update(
                operation_id, "charter", 20, "Creating project charter", 1, 3
            )

            # Create charter data
            charter_data = {
                "vision": request.vision,
                "goals": request.goals,
                "success_criteria": request.success_criteria,
                "constraints": request.constraints or [],
                "stakeholders": request.stakeholders or [],
            }

            # Run charter creation
            result = charter.create_charter(
                self.root, charter_data, interactive=request.interactive
            )

            await self._broadcast_progress_update(
                operation_id, "charter", 100, "Charter created successfully", 3, 3
            )

            self.active_operations[operation_id].update(
                {
                    "status": "completed",
                    "result": result,
                    "completed_at": datetime.now(),
                }
            )

        except Exception as e:
            self.active_operations[operation_id].update(
                {"status": "failed", "error": str(e), "completed_at": datetime.now()}
            )

    async def _run_plan_generation(self, operation_id: str, request: PlanRequest):
        """Run plan generation in background."""
        self.active_operations[operation_id] = {
            "type": "plan",
            "status": "running",
            "started_at": datetime.now(),
        }

        try:
            await self._broadcast_progress_update(
                operation_id, "plan", 30, "Generating project plan", 1, 4
            )

            # Run plan generation
            result = planning.create_plan(self.root)

            await self._broadcast_progress_update(
                operation_id, "plan", 100, "Plan generated successfully", 4, 4
            )

            self.active_operations[operation_id].update(
                {
                    "status": "completed",
                    "result": result,
                    "completed_at": datetime.now(),
                }
            )

        except Exception as e:
            self.active_operations[operation_id].update(
                {"status": "failed", "error": str(e), "completed_at": datetime.now()}
            )

    async def _run_validation(self, operation_id: str, request: ValidationRequest):
        """Run validation in background."""
        self.active_operations[operation_id] = {
            "type": "validation",
            "status": "running",
            "started_at": datetime.now(),
        }

        try:
            await self._broadcast_progress_update(
                operation_id, "validation", 25, "Running project validation", 1, 4
            )

            # Run validation
            result = validation_runtime.validate_project(
                self.root, generate_report=request.generate_report
            )

            await self._broadcast_progress_update(
                operation_id, "validation", 100, "Validation completed", 4, 4
            )

            self.active_operations[operation_id].update(
                {
                    "status": "completed",
                    "result": result,
                    "completed_at": datetime.now(),
                }
            )

        except Exception as e:
            self.active_operations[operation_id].update(
                {"status": "failed", "error": str(e), "completed_at": datetime.now()}
            )

    async def _execute_session_command(
        self, execution_id: str, session_id: str, request: CommandExecutionRequest
    ):
        """Execute command within collaboration session."""
        # This would integrate with the collaboration protocol
        # For now, implement basic command execution
        try:
            # Map command to actual execution
            if request.command == "analyze":
                await self._run_analysis(execution_id, False, None)
            elif request.command == "charter":
                # Would need to extract charter data from context
                pass
            elif request.command == "plan":
                await self._run_plan_generation(execution_id, PlanRequest())
            elif request.command == "validate":
                await self._run_validation(execution_id, ValidationRequest())

        except Exception:
            # Handle execution error
            pass

    # WebSocket helper methods
    async def _send_websocket_message(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific WebSocket client."""
        if client_id in self.websocket_connections:
            websocket = self.websocket_connections[client_id]
            try:
                await websocket.send_text(json.dumps(message, default=str))
            except:
                # Connection closed, remove from active connections
                if client_id in self.websocket_connections:
                    del self.websocket_connections[client_id]

    async def _broadcast_websocket_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSocket clients."""
        disconnected_clients = []

        for client_id, websocket in self.websocket_connections.items():
            try:
                await websocket.send_text(json.dumps(message, default=str))
            except:
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            del self.websocket_connections[client_id]

    async def _broadcast_progress_update(
        self,
        operation_id: str,
        operation_type: str,
        progress: float,
        current_step: str,
        completed_steps: int,
        total_steps: int,
    ):
        """Broadcast progress update to all connected clients."""
        message = {
            "type": WebSocketMessageType.PROGRESS_UPDATE,
            "data": {
                "operation_id": operation_id,
                "operation_type": operation_type,
                "progress_percentage": progress,
                "current_step": current_step,
                "completed_steps": completed_steps,
                "total_steps": total_steps,
                "timestamp": datetime.now().isoformat(),
            },
        }

        await self._broadcast_websocket_message(message)

    async def _handle_websocket_message(self, client_id: str, message: Dict[str, Any]):
        """Handle incoming WebSocket message from client."""
        message_type = message.get("type")

        if message_type == "heartbeat":
            # Respond to heartbeat
            await self._send_websocket_message(
                client_id,
                {
                    "type": "heartbeat_response",
                    "data": {"timestamp": datetime.now().isoformat()},
                },
            )
        elif message_type == "subscribe":
            # Handle subscription to specific updates
            # Can be enhanced to support filtered subscriptions
            pass

    def run(self, **kwargs):
        """Run the API server."""
        try:
            import uvicorn

            # Remove host / port from kwargs if they exist to avoid duplicates
            kwargs.pop("host", None)
            kwargs.pop("port", None)
            uvicorn.run(self.app, host=self.host, port=self.port, **kwargs)
        except ImportError:
            raise ImportError(
                "uvicorn is required to run the API server. Install with: pip install uvicorn"
            )


# Global server instance
_api_server: Optional[AIOnboardAPIServer] = None


def get_api_server(
    root: Path, host: str = "127.0.0.1", port: int = 8080
) -> AIOnboardAPIServer:
    """Get the global API server instance."""
    global _api_server
    if _api_server is None:
        _api_server = AIOnboardAPIServer(root, host, port)
    return _api_server
