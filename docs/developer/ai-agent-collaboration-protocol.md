# AI Agent Collaboration Protocol

## Overview

The AI Agent Collaboration Protocol is a comprehensive system that enables AI agents to safely and effectively collaborate with the ai-onboard system. It provides structured communication, safety mechanisms, guidance systems, and integration points for seamless AI agent operation.

## Key Features

- **Agent Registration**: Register AI agents with capabilities and safety profiles
- **Session Management**: Manage collaboration sessions with timeouts and limits
- **Safety Mechanisms**: Multi-level safety checks and violation tracking
- **Guidance System**: Comprehensive onboarding and best practices guidance
- **Integration Points**: Seamless integration with vision interrogation, gates, and planning
- **Error Monitoring**: Universal error interception and capability tracking
- **CLI Interface**: Full command-line interface for protocol management

## Architecture

### Core Components

1. **AIAgentCollaborationProtocol**: Main protocol orchestrator
2. **AIAgentGuidanceSystem**: Guidance and onboarding system
3. **AgentProfile**: Agent capability and constraint definitions
4. **CollaborationSession**: Active session management
5. **Safety Mechanisms**: Multi-level safety validation
6. **CLI Commands**: Command-line interface for protocol management

### Integration Points

- **Vision Interrogation**: Enhanced vision interrogation system
- **Gate System**: Intelligent Alignment System gates
- **Planning System**: Charter-aware project planning
- **Error Monitoring**: Universal error interception
- **Telemetry**: Usage tracking and analytics

## Quick Start

### 1. Register an AI Agent

```python
from ai_onboard.core.ai_agent_collaboration_protocol import (
    get_collaboration_protocol,
    AgentProfile,
    CollaborationMode,
    AgentCapability,
    SafetyLevel
)

# Create agent profile
agent_profile = AgentProfile(
    agent_id="my_ai_agent",
    name="My AI Assistant",
    version="1.0.0",
    capabilities=[
        AgentCapability.CODE_GENERATION,
        AgentCapability.PLANNING,
        AgentCapability.DEBUGGING
    ],
    collaboration_mode=CollaborationMode.COLLABORATIVE,
    safety_level=SafetyLevel.MEDIUM,
    max_autonomous_actions=10,
    requires_confirmation_for=["file_operation", "command_execution"],
    session_timeout=3600
)

# Register agent
protocol = get_collaboration_protocol(project_root)
result = protocol.register_agent(agent_profile)
```

### 2. Start a Collaboration Session

```python
# Start session
session_result = protocol.start_collaboration_session(agent_profile.agent_id)
session_id = session_result["session_id"]

# Get session context
context = session_result["context"]
print(f"Vision confirmed: {context.get('vision_confirmed', False)}")
print(f"Active gates: {context.get('active_gates', False)}")
```

### 3. Execute Actions

```python
# Example: Start vision interrogation
action = {
    "type": "vision_interrogation",
    "subtype": "start_interrogation",
    "project_type": "web_application"
}
result = protocol.execute_agent_action(session_id, action)

# Example: Read a file
action = {
    "type": "file_operation",
    "operation": "read",
    "file_path": "src/main.py"
}
result = protocol.execute_agent_action(session_id, action)
```

### 4. Handle User Interactions

```python
# Handle user approval
interaction = {
    "type": "approval",
    "action_id": "file_creation_001",
    "message": "User approved file creation"
}
result = protocol.handle_user_interaction(session_id, interaction)
```

### 5. End Session

```python
# End session
result = protocol.end_collaboration_session(session_id, "completed")
```

## CLI Commands

### Agent Registration

```bash
# Register an AI agent
ai_onboard ai-collaboration register my_agent "My AI Assistant" \
    --capabilities code_generation planning debugging \
    --collaboration-mode collaborative \
    --safety-level medium \
    --max-actions 10 \
    --require-confirmation file_operation command_execution
```

### Session Management

```bash
# Start a collaboration session
ai_onboard ai-collaboration session start my_agent

# Get session status
ai_onboard ai-collaboration session status session_1234567890_abcdef12

# End a session
ai_onboard ai-collaboration session end session_1234567890_abcdef12 --reason completed
```

### Guidance System

```bash
# Get guidance for an agent
ai_onboard ai-collaboration guidance get my_agent

# Show specific guidance
ai_onboard ai-collaboration guidance show onboarding_001 my_agent

# Mark guidance as completed
ai_onboard ai-collaboration guidance complete my_agent onboarding_001

# Get agent progress
ai_onboard ai-collaboration guidance progress my_agent

# Get contextual guidance
ai_onboard ai-collaboration guidance contextual my_agent
```

### Testing

```bash
# Test collaboration functionality
ai_onboard ai-collaboration test
```

## Agent Capabilities

### Available Capabilities

- `vision_definition`: Define and refine project vision
- `project_analysis`: Analyze project structure and requirements
- `planning`: Create and manage project plans
- `code_generation`: Generate and modify code
- `testing`: Create and run tests
- `documentation`: Generate documentation
- `debugging`: Debug and troubleshoot issues
- `deployment`: Deploy applications
- `maintenance`: Maintain and update systems

### Collaboration Modes

- `assistive`: AI agent assists user with ai-onboard
- `autonomous`: AI agent operates independently with oversight
- `collaborative`: AI agent and user work together
- `supervised`: AI agent works under human supervision

### Safety Levels

- `low`: Basic safety checks
- `medium`: Standard safety checks (default)
- `high`: Enhanced safety checks
- `critical`: Maximum safety checks

## Safety Mechanisms

### Protected Files and Directories

The following files and directories are protected from modification without explicit user permission:

- `.ai_onboard/policies/` - System policies
- `.ai_onboard/charter.json` - Project charter
- `pyproject.toml` - Project configuration
- `README.md` - System documentation
- `AGENTS.md` - Agent guidelines

### Dangerous Commands

The following command patterns are blocked:

- `rm -rf` or `del /s` - Recursive deletion
- `format` or `mkfs` - Disk formatting
- `dd if=` - Direct disk operations
- `curl | sh` or `wget | sh` - Piping to shell

### Safety Violations

When safety violations occur:

1. Action is blocked
2. Violation is logged
3. User notification is sent
4. Session may be suspended if critical

## Guidance System

### Guidance Types

- `onboarding`: Getting started guidance
- `best_practices`: Best practices and recommendations
- `safety_guidelines`: Safety rules and guidelines
- `workflow_guidance`: Workflow and process guidance
- `troubleshooting`: Problem-solving guidance
- `examples`: Code examples and use cases
- `integration_help`: Platform integration help

### Guidance Levels

- `basic`: Entry-level guidance
- `intermediate`: Intermediate-level guidance
- `advanced`: Advanced-level guidance
- `expert`: Expert-level guidance

### Agent Progression

Agents progress through guidance levels based on completed items:

- **Basic → Intermediate**: 10 completed items
- **Intermediate → Advanced**: 25 completed items
- **Advanced → Expert**: 50 completed items

## Integration Examples

### Cursor AI Integration

```python
# For Cursor AI agents
import os
from pathlib import Path

# Get project root from Cursor context
project_root = Path(os.getcwd())

# Initialize collaboration protocol
protocol = get_collaboration_protocol(project_root)

# Register as Cursor AI agent
agent_profile = AgentProfile(
    agent_id="cursor_ai_agent",
    name="Cursor AI Assistant",
    capabilities=[
        AgentCapability.CODE_GENERATION,
        AgentCapability.DEBUGGING,
        AgentCapability.DOCUMENTATION
    ],
    collaboration_mode=CollaborationMode.COLLABORATIVE,
    safety_level=SafetyLevel.MEDIUM
)

# Register and start session
protocol.register_agent(agent_profile)
session_result = protocol.start_collaboration_session(agent_profile.agent_id)
```

### GitHub Copilot Integration

```python
# For GitHub Copilot
agent_profile = AgentProfile(
    agent_id="copilot_agent",
    name="GitHub Copilot",
    capabilities=[
        AgentCapability.CODE_GENERATION,
        AgentCapability.DOCUMENTATION
    ],
    collaboration_mode=CollaborationMode.ASSISTIVE,
    safety_level=SafetyLevel.HIGH
)
```

### Custom AI Agent Integration

```python
# For custom AI agents
agent_profile = AgentProfile(
    agent_id="custom_agent_001",
    name="Custom AI Agent",
    capabilities=[
        AgentCapability.PROJECT_ANALYSIS,
        AgentCapability.PLANNING,
        AgentCapability.TESTING
    ],
    collaboration_mode=CollaborationMode.AUTONOMOUS,
    safety_level=SafetyLevel.CRITICAL,
    max_autonomous_actions=5,
    requires_confirmation_for=["file_operation", "command_execution"]
)
```

## Best Practices

### Communication

1. **Be Clear and Concise**: Explain what you're doing and why
2. **Ask for Clarification**: When uncertain, ask rather than assume
3. **Provide Context**: Explain your reasoning and alternatives considered
4. **Document Decisions**: Record important decisions and their rationale

### Safety

1. **Respect Boundaries**: Never modify protected files without permission
2. **Check Before Acting**: Verify safety before executing potentially risky operations
3. **Escalate When Needed**: Ask for human input when safety is uncertain
4. **Learn from Mistakes**: Update your behavior based on safety violations

### Efficiency

1. **Batch Operations**: Group related operations when possible
2. **Use Appropriate Tools**: Choose the right tool for each task
3. **Minimize Interruptions**: Complete tasks before asking for new input
4. **Provide Progress Updates**: Keep users informed of your progress

### Collaboration

1. **Understand User Intent**: Focus on what the user wants to achieve
2. **Suggest Improvements**: Offer better approaches when you see them
3. **Explain Trade-offs**: Help users understand the implications of choices
4. **Be Proactive**: Anticipate needs and suggest next steps

## Error Handling

### Graceful Degradation

```python
try:
    result = protocol.execute_agent_action(session_id, action)
    if result["status"] == "success":
        # Process successful result
        pass
    elif result["status"] == "safety_violation":
        # Handle safety violation
        print(f"Safety violation: {result['violation']}")
        if result.get("requires_user_approval"):
            # Ask user for permission
            pass
    else:
        # Handle other errors
        print(f"Error: {result['message']}")
except Exception as e:
    # Handle unexpected errors
    print(f"Unexpected error: {str(e)}")
```

### Recovery Strategies

1. **Retry with Backoff**: Retry failed operations with exponential backoff
2. **Fallback Actions**: Have alternative approaches for common failures
3. **User Notification**: Inform users of errors and recovery attempts
4. **Session Recovery**: Recover from session interruptions

## Monitoring and Analytics

### Usage Tracking

The protocol automatically tracks:

- Agent registrations and capabilities
- Session duration and activity
- Actions taken and their outcomes
- Safety violations and resolutions
- User interactions and feedback
- Guidance completion and progression

### Error Monitoring

All errors are automatically:

- Logged with context
- Analyzed by the Smart Debugger
- Tracked for patterns and trends
- Used to improve system reliability

### Performance Metrics

Key metrics include:

- Session success rates
- Action execution times
- Safety violation frequencies
- User satisfaction scores
- Guidance completion rates

## Troubleshooting

### Common Issues

1. **Agent Registration Fails**
   - Check agent ID uniqueness
   - Verify capability values
   - Ensure collaboration mode is allowed

2. **Session Start Fails**
   - Check agent is registered
   - Verify session limits
   - Ensure project root is valid

3. **Action Execution Fails**
   - Check safety constraints
   - Verify action format
   - Ensure session is active

4. **Safety Violations**
   - Review protected file patterns
   - Check dangerous command patterns
   - Verify safety level settings

### Debug Commands

```bash
# Test collaboration functionality
ai_onboard ai-collaboration test

# Get session status
ai_onboard ai-collaboration session status <session_id>

# Get agent progress
ai_onboard ai-collaboration guidance progress <agent_id>

# Get contextual guidance
ai_onboard ai-collaboration guidance contextual <agent_id>
```

## Future Enhancements

### Planned Features

1. **Multi-Agent Coordination**: Support for multiple AI agents working together
2. **Advanced Analytics**: Detailed performance and usage analytics
3. **Custom Safety Rules**: User-defined safety rules and constraints
4. **Integration APIs**: REST and GraphQL APIs for external integration
5. **Real-time Collaboration**: WebSocket-based real-time collaboration
6. **Machine Learning**: AI-powered guidance and safety recommendations

### Extension Points

1. **Custom Capabilities**: Define new agent capabilities
2. **Custom Safety Checks**: Implement custom safety validation
3. **Custom Guidance**: Add domain-specific guidance content
4. **Custom Integration**: Create platform-specific integrations

## Conclusion

The AI Agent Collaboration Protocol provides a comprehensive, safe, and effective way for AI agents to collaborate with the ai-onboard system. It balances autonomy with safety, provides clear guidance and best practices, and integrates seamlessly with existing systems.

For more information, see the [API Reference](api-reference.md) and [Examples](examples.md) documentation.
