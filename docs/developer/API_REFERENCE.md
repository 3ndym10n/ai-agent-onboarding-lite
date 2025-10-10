# AI Onboard - Developer API Reference

## 🔧 Core Components

### SystemIntegrator

The main entry point for integrating with the oversight system.

```python
from ai_onboard.core.ai_integration.system_integrator import get_system_integrator

# Initialize
integrator = get_system_integrator(project_root)

# Process agent operation
result = integrator.process_agent_operation(
    agent_id="cursor_ai",
    operation="create_files",
    context={
        "file_count": 5,
        "purpose": "unit tests",
        "files": ["test_1.py", "test_2.py"]
    }
)

# Check result
if result.approved:
    print("Operation approved")
    print(f"Vision alignment: {result.vision_alignment:.1%}")
else:
    print("Operation blocked")
    print(f"Reasons: {result.blocking_reasons}")
```

### AgentOversightDashboard

Real-time dashboard for monitoring agent activity.

```python
from ai_onboard.core.ai_integration.agent_oversight_dashboard import AgentOversightDashboard

# Create dashboard
dashboard = AgentOversightDashboard(project_root)

# Get current display
display = dashboard.create_dashboard_display()
print(display)

# Get specific data
activity = dashboard.get_agent_activity()
gates = dashboard.get_pending_gates()
blocks = dashboard.get_blocked_actions()
```

## 📊 Data Models

### AgentOversightContext

Returned by `process_agent_operation()`.

```python
@dataclass
class AgentOversightContext:
    agent_id: str
    operation: str
    context: Dict[str, Any]
    timestamp: float
    gate_status: Optional[str]
    chaos_detected: bool
    vision_alignment: float  # 0.0 to 1.0
    limits_exceeded: bool
    emergency_triggered: bool
    approved: bool
    blocking_reasons: List[str]
    corrective_actions: List[str]
```

### System Health

Returned by `get_integrated_status()`.

```python
{
    "integrated_mode": true,
    "health_monitoring_active": true,
    "system_health": {
        "activity_monitor": {"active": true, "health_score": 1.0},
        "decision_enforcer": {"active": true, "health_score": 1.0},
        "hard_gate_enforcer": {"active": true, "health_score": 1.0},
        "hard_limits_enforcer": {"active": true, "health_score": 1.0},
        "chaos_detector": {"active": true, "health_score": 1.0},
        "vision_drift_alerting": {"active": true, "health_score": 1.0},
        "emergency_control": {"active": true, "health_score": 1.0},
    },
    "recent_activity": {
        "total_agents": 2,
        "total_actions": 45,
        "agents_active": 1,
    },
    "emergency_status": {
        "agents_in_emergency": 0,
        "paused_agents": 0,
        "stopped_agents": 0,
    }
}
```

## 🎯 Integration Points

### Before Major Operations

**Always check with the oversight system** before:
- Creating 5+ files in one session
- Deleting 3+ files in one operation
- Modifying 10+ files in one session
- Refactoring 3+ files at once
- Adding any new dependencies
- Major architectural changes

```python
# Pattern for integration
result = integrator.process_agent_operation(
    agent_id="cursor_ai",
    operation="create_files",
    context={
        "description": "Creating test files for new feature",
        "files_affected": 8,
        "reason": "Unit tests for authentication module"
    }
)

if not result.approved:
    print(f"Operation blocked: {result.blocking_reasons}")
    # Handle blocked operation
    for action in result.corrective_actions:
        print(f"Suggested action: {action}")
```

### Real-time Monitoring

**Monitor agent activity continuously**:

```python
import time

while True:
    status = integrator.get_integrated_status()

    if status["recent_activity"]["total_actions"] > 0:
        print(f"Active agents: {status['recent_activity']['total_agents']}")

    if status["emergency_status"]["agents_in_emergency"] > 0:
        print("🚨 Emergency situation detected!")
        break

    time.sleep(30)  # Check every 30 seconds
```

### Emergency Response

**Handle emergency situations programmatically**:

```python
# Check for emergencies
status = integrator.get_integrated_status()

if status["emergency_status"]["agents_in_emergency"] > 0:
    # Pause all agents in emergency
    for agent_id in get_agents_in_emergency():
        integrator.emergency_control.pause_agent(
            agent_id,
            "Emergency pause - review required",
            "system"
        )

    # Alert human operator
    send_alert("Multiple agents in emergency state - manual review required")
```

## 🔧 Configuration

### Project Configuration

```python
# Configure limits
from ai_onboard.core.ai_integration.hard_limits_enforcer import get_hard_limits_enforcer

limits_enforcer = get_hard_limits_enforcer(project_root)
limits_enforcer.configure_limits({
    "max_files_created_per_hour": 50,
    "max_changes_per_minute": 10,
    "max_files_in_refactor": 5,
})
```

### Agent-Specific Settings

```python
# Set agent-specific limits
agent_limits = {
    "max_files_created_per_hour": 20,  # Lower for this agent
    "monitoring_level": "strict"       # Higher monitoring
}

integrator.configure_agent_limits("special_agent", agent_limits)
```

## 📈 Monitoring and Metrics

### Activity Monitoring

```python
from ai_onboard.core.ai_integration.agent_activity_monitor import get_agent_activity_monitor

monitor = get_agent_activity_monitor(project_root)

# Get activity summary
summary = monitor.get_activity_summary(hours=24)
print(f"Total actions: {summary['total_events']}")
print(f"Active agents: {summary['active_agents']}")

# Get agent-specific data
agent_data = summary['agent_details']
for agent_id, data in agent_data.items():
    print(f"Agent {agent_id}: {data['events_count']} actions")
```

### Performance Monitoring

```python
# Monitor system performance
import psutil
import time

start_time = time.time()
initial_memory = psutil.Process().memory_info().rss

# Run operations
result = integrator.process_agent_operation("test_agent", "test_op", {})

end_time = time.time()
final_memory = psutil.Process().memory_info().rss

duration = end_time - start_time
memory_growth = (final_memory - initial_memory) / 1024 / 1024  # MB

print(f"Operation time: {duration*1000:.1f}ms")
print(f"Memory growth: {memory_growth:.1f}MB")
```

## 🚨 Error Handling

### Integration Errors

```python
try:
    result = integrator.process_agent_operation(
        agent_id="cursor_ai",
        operation="problematic_operation",
        context={"data": "test"}
    )
except Exception as e:
    print(f"Integration error: {e}")
    # Fallback to manual operation
    proceed_with_manual_operation()
```

### System Health Issues

```python
status = integrator.get_integrated_status()

# Check for system issues
for system_name, health in status["system_health"].items():
    if not health["active"]:
        print(f"System {system_name} is down")
        # Handle degraded operation
        operate_in_degraded_mode()

    if health["health_score"] < 0.8:
        print(f"System {system_name} has issues: {health['issues']}")
```

## 🔄 Event Handling

### Custom Event Listeners

```python
class CustomEventHandler:
    def __init__(self, integrator):
        self.integrator = integrator

    def on_chaos_detected(self, chaos_event):
        print(f"Chaos detected: {chaos_event.description}")
        # Custom response logic

    def on_vision_drift(self, drift_alert):
        print(f"Vision drift: {drift_alert.description}")
        # Custom alignment logic

    def on_emergency(self, emergency_event):
        print(f"Emergency: {emergency_event.description}")
        # Custom emergency response

# Register event handlers
handler = CustomEventHandler(integrator)
integrator.register_event_handler("chaos", handler.on_chaos_detected)
integrator.register_event_handler("vision_drift", handler.on_vision_drift)
integrator.register_event_handler("emergency", handler.on_emergency)
```

## 📋 CLI Integration

### Programmatic CLI Usage

```python
import subprocess
import json

def check_operation_with_cli(agent_id: str, operation: str, context: dict) -> dict:
    """Use CLI for operation checking."""
    cmd = [
        "python", "-m", "ai_onboard", "integrator", "process",
        agent_id, operation, "--context", json.dumps(context)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        # Parse result
        return json.loads(result.stdout)
    else:
        print(f"CLI error: {result.stderr}")
        return {"approved": False, "error": result.stderr}
```

### Batch Operations

```python
def process_batch_operations(operations: List[dict]) -> List[dict]:
    """Process multiple operations in batch."""
    results = []

    for op in operations:
        result = integrator.process_agent_operation(
            agent_id=op["agent_id"],
            operation=op["operation"],
            context=op["context"]
        )
        results.append(result)

    return results
```

## 🔒 Security Considerations

### Input Validation

```python
def validate_operation_context(context: dict) -> bool:
    """Validate operation context before processing."""
    required_fields = ["description", "reason"]

    for field in required_fields:
        if field not in context:
            return False

    # Validate field types and lengths
    if len(context["description"]) > 500:
        return False

    return True

# Use in integration
if not validate_operation_context(context):
    raise ValueError("Invalid operation context")

result = integrator.process_agent_operation(agent_id, operation, context)
```

### Audit Logging

```python
import logging

# Set up audit logging
audit_logger = logging.getLogger("ai_onboard_audit")
audit_logger.setLevel(logging.INFO)

# Log all operations
result = integrator.process_agent_operation(agent_id, operation, context)

audit_logger.info(
    f"Operation: {operation}, Agent: {agent_id}, "
    f"Approved: {result.approved}, Alignment: {result.vision_alignment}"
)
```

## 🚀 Best Practices

### Integration Patterns

1. **Always check before major operations**
2. **Provide clear, detailed context**
3. **Handle both approved and blocked results**
4. **Monitor system health regularly**
5. **Log operations for audit trails**

### Error Handling

1. **Graceful degradation** when systems are unavailable
2. **Clear error messages** for users
3. **Fallback procedures** for critical operations
4. **Proper logging** for debugging

### Performance

1. **Batch operations** when possible
2. **Cache results** for repeated similar operations
3. **Monitor resource usage** continuously
4. **Profile bottlenecks** regularly

---

**This API reference provides everything needed to integrate AI Onboard's oversight capabilities into your development tools and workflows.** Use these patterns to build systematic control over chaotic AI agents! 🔧




