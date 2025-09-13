"""
Background Agent Manager (T23) - Core system for managing autonomous background AI agents.

This module provides the foundational infrastructure for running AI agents autonomously
in the background while maintaining safety, coordination, and alignment with project goals.
The system extends the existing AAOL to support long - running, autonomous operations.
"""

import json
import signal
import sys
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import psutil

from .ai_agent_orchestration import create_ai_agent_orchestrator
from .unified_metrics_collector import get_unified_metrics_collector
from .user_experience_enhancements import UXEventType, get_ux_enhancement_system


class AgentState(Enum):
    """States of background agents."""

    INACTIVE = "inactive"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    TERMINATED = "terminated"


class AgentPriority(Enum):
    """Priority levels for background agents."""

    CRITICAL = 1  # System - critical agents (monitoring, safety)
    HIGH = 2  # Important agents (health monitoring, alerts)
    MEDIUM = 3  # Standard agents (optimization, learning)
    LOW = 4  # Background agents (cleanup, maintenance)
    IDLE = 5  # Idle - time agents (analytics, reporting)


class ScheduleType(Enum):
    """Types of agent scheduling."""

    CONTINUOUS = "continuous"  # Always running
    INTERVAL = "interval"  # Fixed interval (e.g., every 5 minutes)
    CRON = "cron"  # Cron - style scheduling
    EVENT_DRIVEN = "event_driven"  # Triggered by events
    ON_DEMAND = "on_demand"  # Manual triggering only


@dataclass
class AgentResourceLimits:
    """Resource limits for background agents."""

    max_cpu_percent: float = 10.0  # Maximum CPU usage percentage
    max_memory_mb: float = 512.0  # Maximum memory usage in MB
    max_io_ops_per_sec: int = 100  # Maximum I / O operations per second
    max_network_requests_per_min: int = 50  # Maximum network requests per minute
    max_execution_time_sec: int = 3600  # Maximum execution time in seconds
    max_file_operations: int = 1000  # Maximum file operations

    # Enforcement options
    enforce_cpu_limit: bool = True
    enforce_memory_limit: bool = True
    enforce_io_limit: bool = True
    enforce_network_limit: bool = True
    enforce_time_limit: bool = True


@dataclass
class AgentConfiguration:
    """Configuration for a background agent."""

    agent_id: str
    name: str
    description: str
    agent_class: str

    # Scheduling
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any] = field(default_factory = dict)

    # Priority and resources
    priority: AgentPriority = AgentPriority.MEDIUM
    resource_limits: AgentResourceLimits = field(default_factory = AgentResourceLimits)

    # Safety and permissions
    allowed_operations: List[str] = field(default_factory = list)
    forbidden_operations: List[str] = field(default_factory = list)
    requires_approval: List[str] = field(default_factory = list)

    # Configuration
    enabled: bool = True
    auto_start: bool = False
    restart_on_failure: bool = True
    max_restart_attempts: int = 3

    # Metadata
    created_at: datetime = field(default_factory = datetime.now)
    updated_at: datetime = field(default_factory = datetime.now)
    tags: List[str] = field(default_factory = list)


@dataclass
class AgentStatus:
    """Current status of a background agent."""

    agent_id: str
    state: AgentState

    # Runtime information
    started_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    last_heartbeat: Optional[datetime] = None

    # Performance metrics
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    io_operations: int = 0
    network_requests: int = 0

    # Execution statistics
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    last_execution_duration: float = 0.0
    average_execution_duration: float = 0.0

    # Health and safety
    health_score: float = 1.0  # 0.0 to 1.0
    safety_violations: int = 0
    resource_violations: int = 0

    # Error information
    last_error: Optional[str] = None
    error_count: int = 0
    restart_count: int = 0


@dataclass
class AgentExecution:
    """Record of an agent execution."""

    execution_id: str
    agent_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None

    # Execution details
    trigger: str = "scheduled"  # scheduled, event, manual
    success: bool = False
    duration_ms: float = 0.0

    # Resource usage
    peak_cpu_percent: float = 0.0
    peak_memory_mb: float = 0.0
    io_operations: int = 0
    network_requests: int = 0

    # Results and output
    result_data: Dict[str, Any] = field(default_factory = dict)
    output_summary: str = ""
    error_details: Optional[str] = None

    # Safety and compliance
    safety_violations: List[str] = field(default_factory = list)
    resource_violations: List[str] = field(default_factory = list)


class BackgroundAgent(ABC):
    """Abstract base class for background agents."""

    def __init__(self, agent_id: str, config: AgentConfiguration, root: Path):
        self.agent_id = agent_id
        self.config = config
        self.root = root

        # Runtime state
        self.state = AgentState.INACTIVE
        self.started_at: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None

        # Resources and monitoring
        self.resource_monitor = ResourceMonitor(config.resource_limits)
        self.execution_context: Optional[Dict[str, Any]] = None

        # Safety and intervention
        self.safety_monitor = AgentSafetyMonitor(self)
        self.intervention_callbacks: List[Callable] = []

        # Communication
        self.message_queue: List[Dict[str, Any]] = []
        self.event_handlers: Dict[str, Callable] = {}

        # Metrics and logging
        self.metrics_collector = get_unified_metrics_collector(root)
        self.ux_system = get_ux_enhancement_system(root)

        # Initialize agent - specific components
        self._initialize_agent()

    @abstractmethod
    def _initialize_agent(self):
        """Initialize agent - specific components."""

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main functionality."""

    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Get the agent's health status."""

    def start(self) -> bool:
        """Start the background agent."""
        if self.state != AgentState.INACTIVE:
            return False

        try:
            self.state = AgentState.STARTING
            self.started_at = datetime.now()

            # Initialize resources and safety
            self.resource_monitor.start()
            self.safety_monitor.start()

            # Agent - specific startup
            if self._startup():
                self.state = AgentState.RUNNING
                self.last_activity = datetime.now()
                return True
            else:
                self.state = AgentState.ERROR
                return False

        except Exception as e:
            self.state = AgentState.ERROR
            self._handle_error(f"Startup failed: {e}")
            return False

    def stop(self) -> bool:
        """Stop the background agent."""
        if self.state not in [AgentState.RUNNING, AgentState.PAUSED]:
            return False

        try:
            self.state = AgentState.STOPPING

            # Agent - specific shutdown
            self._shutdown()

            # Cleanup resources
            self.resource_monitor.stop()
            self.safety_monitor.stop()

            self.state = AgentState.STOPPED
            return True

        except Exception as e:
            self.state = AgentState.ERROR
            self._handle_error(f"Shutdown failed: {e}")
            return False

    def pause(self) -> bool:
        """Pause the background agent."""
        if self.state != AgentState.RUNNING:
            return False

        self.state = AgentState.PAUSED
        self._on_pause()
        return True

    def resume(self) -> bool:
        """Resume the background agent."""
        if self.state != AgentState.PAUSED:
            return False

        self.state = AgentState.RUNNING
        self.last_activity = datetime.now()
        self._on_resume()
        return True

    def send_message(self, recipient: str, message: Dict[str, Any]):
        """Send a message to another agent."""
        message["sender"] = self.agent_id
        message["timestamp"] = datetime.now().isoformat()
        # Implementation would route through BackgroundAgentManager

    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler."""
        self.event_handlers[event_type] = handler

    def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event."""
        event = {
            "type": event_type,
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        # Implementation would route through BackgroundAgentManager

    def _startup(self) -> bool:
        """Agent - specific startup logic."""
        return True

    def _shutdown(self):
        """Agent - specific shutdown logic."""

    def _on_pause(self):
        """Called when agent is paused."""

    def _on_resume(self):
        """Called when agent is resumed."""

    def _handle_error(self, error: str):
        """Handle agent errors."""
        print(f"Agent {self.agent_id} error: {error}")

        # Record error in UX system
        try:
            self.ux_system.record_ux_event(
                UXEventType.ERROR_ENCOUNTER,
                "background_agent",
                context={"agent_id": self.agent_id, "error": error},
            )
        except Exception:
            pass

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now()


class ResourceMonitor:
    """Monitors resource usage for background agents."""

    def __init__(self, limits: AgentResourceLimits):
        self.limits = limits
        self.monitoring = False
        self.violations: List[str] = []

        # Resource tracking
        self.cpu_samples: List[float] = []
        self.memory_samples: List[float] = []
        self.io_counter = 0
        self.network_counter = 0
        self.start_time: Optional[datetime] = None

    def start(self):
        """Start resource monitoring."""
        self.monitoring = True
        self.start_time = datetime.now()
        # Start monitoring thread
        self._start_monitoring_thread()

    def stop(self):
        """Stop resource monitoring."""
        self.monitoring = False

    def _start_monitoring_thread(self):
        """Start the resource monitoring thread."""

        def monitor():
            while self.monitoring:
                try:
                    # Get current process
                    process = psutil.Process()

                    # Monitor CPU usage
                    if self.limits.enforce_cpu_limit:
                        cpu_percent = process.cpu_percent()
                        self.cpu_samples.append(cpu_percent)
                        if cpu_percent > self.limits.max_cpu_percent:
                            self.violations.append(
                                f"CPU usage exceeded: {cpu_percent}%"
                            )

                    # Monitor memory usage
                    if self.limits.enforce_memory_limit:
                        memory_mb = process.memory_info().rss / 1024 / 1024
                        self.memory_samples.append(memory_mb)
                        if memory_mb > self.limits.max_memory_mb:
                            self.violations.append(
                                f"Memory usage exceeded: {memory_mb}MB"
                            )

                    # Monitor execution time
                    if self.limits.enforce_time_limit and self.start_time:
                        elapsed = (datetime.now() - self.start_time).total_seconds()
                        if elapsed > self.limits.max_execution_time_sec:
                            self.violations.append(
                                f"Execution time exceeded: {elapsed}s"
                            )
                            break

                    time.sleep(1)  # Sample every second

                except Exception:
                    break

        thread = threading.Thread(target = monitor, daemon = True)
        thread.start()

    def get_current_usage(self) -> Dict[str, float]:
        """Get current resource usage."""
        try:
            process = psutil.Process()
            return {
                "cpu_percent": process.cpu_percent(),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "io_operations": self.io_counter,
                "network_requests": self.network_counter,
            }
        except Exception:
            return {
                "cpu_percent": 0,
                "memory_mb": 0,
                "io_operations": 0,
                "network_requests": 0,
            }


class AgentSafetyMonitor:
    """Safety monitoring for background agents."""

    def __init__(self, agent: BackgroundAgent):
        self.agent = agent
        self.monitoring = False
        self.violations: List[str] = []
        self.intervention_triggered = False

    def start(self):
        """Start safety monitoring."""
        self.monitoring = True

    def stop(self):
        """Stop safety monitoring."""
        self.monitoring = False

    def check_safety_violation(self, operation: str, context: Dict[str, Any]) -> bool:
        """Check if an operation would violate safety policies."""
        config = self.agent.config

        # Check forbidden operations
        if operation in config.forbidden_operations:
            self.violations.append(f"Forbidden operation attempted: {operation}")
            return True

        # Check if operation requires approval
        if operation in config.requires_approval:
            # For now, block operations requiring approval
            self.violations.append(f"Operation requires approval: {operation}")
            return True

        return False

    def trigger_intervention(self, reason: str):
        """Trigger safety intervention."""
        if not self.intervention_triggered:
            self.intervention_triggered = True
            self.violations.append(f"Safety intervention: {reason}")

            # Stop the agent
            self.agent.stop()

            # Notify safety system
            self._notify_safety_system(reason)

    def _notify_safety_system(self, reason: str):
        """Notify the safety system of intervention."""
        try:
            self.agent.ux_system.record_ux_event(
                UXEventType.ERROR_ENCOUNTER,
                "safety_system",
                context={
                    "agent_id": self.agent.agent_id,
                    "intervention_reason": reason,
                    "safety_violations": self.violations,
                },
            )
        except Exception:
            pass


class BackgroundAgentManager:
    """Central manager for all background agents."""

    def __init__(self, root: Path):
        self.root = root
        self.data_dir = root / ".ai_onboard" / "background_agents"
        self.data_dir.mkdir(parents = True, exist_ok = True)

        # Agent registry and status
        self.agents: Dict[str, BackgroundAgent] = {}
        self.agent_configs: Dict[str, AgentConfiguration] = {}
        self.agent_statuses: Dict[str, AgentStatus] = {}

        # Execution tracking
        self.executions: Dict[str, AgentExecution] = {}
        self.execution_history: List[AgentExecution] = []

        # Scheduling and coordination
        self.scheduler = AgentScheduler(self)
        self.coordinator = AgentCoordinator(self)

        # Safety and monitoring
        self.safety_system = BackgroundAgentSafetySystem(self)
        self.resource_manager = SharedResourceManager(self)

        # Communication
        self.message_bus = AgentMessageBus(self)
        self.event_dispatcher = AgentEventDispatcher(self)

        # Integration with existing systems
        self.aaol = create_ai_agent_orchestrator(root)
        self.metrics_collector = get_unified_metrics_collector(root)
        self.ux_system = get_ux_enhancement_system(root)

        # Configuration
        self.config = self._load_manager_config()

        # Initialize
        self._load_agent_configurations()
        self._setup_signal_handlers()

    def _load_manager_config(self) -> Dict[str, Any]:
        """Load background agent manager configuration."""
        config_file = self.data_dir / "manager_config.json"

        default_config = {
            "max_concurrent_agents": 10,
            "resource_monitoring_interval": 1.0,
            "safety_check_interval": 5.0,
            "heartbeat_interval": 30.0,
            "execution_timeout": 3600,
            "auto_restart_failed_agents": True,
            "log_level": "INFO",
            "enable_safety_monitoring": True,
            "enable_resource_limits": True,
        }

        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception:
                pass

        # Save default config
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent = 2)

        return default_config

    def _load_agent_configurations(self):
        """Load agent configurations from storage."""
        config_dir = self.data_dir / "configs"
        config_dir.mkdir(exist_ok = True)

        for config_file in config_dir.glob("*.json"):
            try:
                with open(config_file, "r") as f:
                    config_data = json.load(f)

                config = AgentConfiguration(
                    agent_id = config_data["agent_id"],
                    name = config_data["name"],
                    description = config_data["description"],
                    agent_class = config_data["agent_class"],
                    schedule_type = ScheduleType(config_data["schedule_type"]),
                    schedule_config = config_data.get("schedule_config", {}),
                    priority = AgentPriority(config_data.get("priority", 3)),
                    enabled = config_data.get("enabled", True),
                    auto_start = config_data.get("auto_start", False),
                )

                self.agent_configs[config.agent_id] = config

            except Exception as e:
                print(f"Failed to load agent config {config_file}: {e}")

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            print("Received shutdown signal, stopping all agents...")
            self.stop_all_agents()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def register_agent_class(self, agent_class: type, agent_type: str):
        """Register a new agent class."""
        # Implementation for dynamic agent registration

    def create_agent(self, config: AgentConfiguration) -> bool:
        """Create a new background agent."""
        try:
            # Save configuration
            self.agent_configs[config.agent_id] = config
            self._save_agent_config(config)

            # Initialize status
            status = AgentStatus(agent_id = config.agent_id, state = AgentState.INACTIVE)
            self.agent_statuses[config.agent_id] = status

            return True

        except Exception as e:
            print(f"Failed to create agent {config.agent_id}: {e}")
            return False

    def start_agent(self, agent_id: str) -> bool:
        """Start a background agent."""
        if agent_id not in self.agent_configs:
            return False

        if (
            agent_id in self.agents
            and self.agents[agent_id].state == AgentState.RUNNING
        ):
            return True  # Already running

        try:
            config = self.agent_configs[agent_id]

            # Create agent instance (simplified - would use factory pattern)
            if config.agent_class == "ProjectHealthMonitor":
                agent = ProjectHealthMonitor(agent_id, config, self.root)
            elif config.agent_class == "PerformanceMonitor":
                agent = PerformanceMonitor(agent_id, config, self.root)
            else:
                print(f"Unknown agent class: {config.agent_class}")
                return False

            # Start the agent
            if agent.start():
                self.agents[agent_id] = agent
                self.agent_statuses[agent_id].state = AgentState.RUNNING
                self.agent_statuses[agent_id].started_at = datetime.now()

                # Schedule the agent
                self.scheduler.schedule_agent(agent_id)

                return True
            else:
                return False

        except Exception as e:
            print(f"Failed to start agent {agent_id}: {e}")
            return False

    def stop_agent(self, agent_id: str) -> bool:
        """Stop a background agent."""
        if agent_id not in self.agents:
            return False

        try:
            agent = self.agents[agent_id]

            # Unschedule the agent
            self.scheduler.unschedule_agent(agent_id)

            # Stop the agent
            if agent.stop():
                self.agent_statuses[agent_id].state = AgentState.STOPPED
                del self.agents[agent_id]
                return True
            else:
                return False

        except Exception as e:
            print(f"Failed to stop agent {agent_id}: {e}")
            return False

    def get_agent_status(self, agent_id: str) -> Optional[AgentStatus]:
        """Get the status of a background agent."""
        return self.agent_statuses.get(agent_id)

    def list_agents(self) -> List[str]:
        """List all registered agents."""
        return list(self.agent_configs.keys())

    def list_running_agents(self) -> List[str]:
        """List all currently running agents."""
        return [
            agent_id
            for agent_id, status in self.agent_statuses.items()
            if status.state == AgentState.RUNNING
        ]

    def stop_all_agents(self):
        """Stop all running agents."""
        for agent_id in list(self.agents.keys()):
            self.stop_agent(agent_id)

    def _save_agent_config(self, config: AgentConfiguration):
        """Save agent configuration to storage."""
        config_file = self.data_dir / "configs" / f"{config.agent_id}.json"
        config_file.parent.mkdir(exist_ok = True)

        try:
            config_data = {
                "agent_id": config.agent_id,
                "name": config.name,
                "description": config.description,
                "agent_class": config.agent_class,
                "schedule_type": config.schedule_type.value,
                "schedule_config": config.schedule_config,
                "priority": config.priority.value,
                "enabled": config.enabled,
                "auto_start": config.auto_start,
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat(),
                "tags": config.tags,
            }

            with open(config_file, "w") as f:
                json.dump(config_data, f, indent = 2)

        except Exception as e:
            print(f"Failed to save agent config {config.agent_id}: {e}")


# Placeholder classes for scheduler, coordinator, etc.
class AgentScheduler:
    def __init__(self, manager):
        self.manager = manager

    def schedule_agent(self, agent_id: str):
        pass

    def unschedule_agent(self, agent_id: str):
        pass


class AgentCoordinator:
    def __init__(self, manager):
        self.manager = manager


class BackgroundAgentSafetySystem:
    def __init__(self, manager):
        self.manager = manager


class SharedResourceManager:
    def __init__(self, manager):
        self.manager = manager


class AgentMessageBus:
    def __init__(self, manager):
        self.manager = manager


class AgentEventDispatcher:
    def __init__(self, manager):
        self.manager = manager


# Example agent implementations
class ProjectHealthMonitor(BackgroundAgent):
    """Monitors project health metrics continuously."""

    def _initialize_agent(self):
        """Initialize project health monitoring."""
        self.last_health_check = None
        self.health_metrics = {}

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute health monitoring."""
        try:
            # Monitor project progress
            # Monitor code quality
            # Check for potential issues
            # Generate health report

            health_data = {
                "timestamp": datetime.now().isoformat(),
                "overall_health": 0.85,
                "progress_health": 0.90,
                "quality_health": 0.80,
                "risk_indicators": [],
            }

            self.health_metrics = health_data
            return {"success": True, "data": health_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_health_status(self) -> Dict[str, Any]:
        """Get agent health status."""
        return {
            "agent_health": 1.0,
            "last_execution": self.last_activity,
            "metrics_collected": len(self.health_metrics),
        }


class PerformanceMonitor(BackgroundAgent):
    """Monitors system performance and optimization opportunities."""

    def _initialize_agent(self):
        """Initialize performance monitoring."""
        self.performance_baseline = {}
        self.optimization_opportunities = []

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute performance monitoring."""
        try:
            # Monitor system performance
            # Identify bottlenecks
            # Suggest optimizations

            performance_data = {
                "timestamp": datetime.now().isoformat(),
                "cpu_usage": 15.2,
                "memory_usage": 342.5,
                "disk_io": 45.8,
                "optimization_score": 0.75,
            }

            return {"success": True, "data": performance_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_health_status(self) -> Dict[str, Any]:
        """Get agent health status."""
        return {
            "agent_health": 1.0,
            "last_execution": self.last_activity,
            "opportunities_found": len(self.optimization_opportunities),
        }


# Global instance
_background_agent_manager: Optional[BackgroundAgentManager] = None


def get_background_agent_manager(root: Path) -> BackgroundAgentManager:
    """Get the global background agent manager."""
    global _background_agent_manager
    if _background_agent_manager is None:
        _background_agent_manager = BackgroundAgentManager(root)
    return _background_agent_manager
