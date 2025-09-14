"""
AI Agent Guidance System - Provides guidance and onboarding for AI agents.

This module provides comprehensive guidance for AI agents on how to effectively
collaborate with the ai - onboard system, including best practices, examples,
and automated guidance generation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ai_agent_collaboration_protocol import get_collaboration_protocol


class GuidanceType(Enum):
    """Types of guidance that can be provided."""

    ONBOARDING = "onboarding"
    BEST_PRACTICES = "best_practices"
    SAFETY_GUIDELINES = "safety_guidelines"
    WORKFLOW_GUIDANCE = "workflow_guidance"
    TROUBLESHOOTING = "troubleshooting"
    EXAMPLES = "examples"
    INTEGRATION_HELP = "integration_help"


class GuidanceLevel(Enum):
    """Levels of guidance detail."""

    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class GuidanceItem:
    """A single guidance item."""

    id: str
    title: str
    content: str
    guidance_type: GuidanceType
    level: GuidanceLevel
    tags: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    related_items: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentGuidanceProfile:
    """Profile for AI agent guidance."""

    agent_id: str
    experience_level: GuidanceLevel
    preferred_guidance_types: List[GuidanceType]
    completed_guidance: List[str] = field(default_factory=list)
    guidance_history: List[Dict[str, Any]] = field(default_factory=list)
    last_guidance_request: Optional[datetime] = None
    guidance_preferences: Dict[str, Any] = field(default_factory=dict)


class AIAgentGuidanceSystem:
    """Comprehensive guidance system for AI agents."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.collaboration_protocol = get_collaboration_protocol(project_root)
        self.guidance_items: Dict[str, GuidanceItem] = {}
        self.agent_profiles: Dict[str, AgentGuidanceProfile] = {}
        self._initialize_guidance_items()

    def _initialize_guidance_items(self):
        """Initialize the guidance items database."""
        # Onboarding guidance
        self._add_guidance_item(
            GuidanceItem(
                id="onboarding_001",
                title="Getting Started with ai - onboard",
                content="""
# Getting Started with ai - onboard

Welcome to ai - onboard! This system helps you collaborate effectively with users on software projects.

## Key Concepts

1. **Vision Interrogation**: Define project vision through guided questioning
2. **Collaboration Protocol**: Structured way to interact with the system
3. **Safety Mechanisms**: Built - in protections for safe operation
4. **Gate System**: Points where human input is required

## First Steps

1. Register your agent profile
2. Start a collaboration session
3. Begin with vision interrogation if needed
4. Follow the collaboration protocol

## Best Practices

- Always check for active gates before proceeding
- Respect safety boundaries
- Ask for clarification when uncertain
- Document your actions and decisions
            """,
                guidance_type=GuidanceType.ONBOARDING,
                level=GuidanceLevel.BASIC,
                tags=["getting_started", "basics", "onboarding"],
            )
        )

        # Safety guidelines
        self._add_guidance_item(
            GuidanceItem(
                id="safety_001",
                title="Safety Guidelines for AI Agents",
                content="""
# Safety Guidelines for AI Agents

## Protected Files and Directories

Never modify these files without explicit user permission:
- `.ai_onboard / policies/` - System policies
- `.ai_onboard / charter.json` - Project charter
- `pyproject.toml` - Project configuration
- `README.md` - System documentation
- `AGENTS.md` - Agent guidelines

## Dangerous Commands

Avoid these command patterns:
- `rm -rf` or `del /s` - Recursive deletion
- `format` or `mkfs` - Disk formatting
- `dd if=` - Direct disk operations
- `curl | sh` or `wget | sh` - Piping to shell

## Safety Levels

- **LOW**: Basic safety checks
- **MEDIUM**: Standard safety checks (default)
- **HIGH**: Enhanced safety checks
- **CRITICAL**: Maximum safety checks

## When to Ask for Permission

- Modifying protected files
- Running system - level commands
- Installing packages
- Changing project configuration
- Accessing external resources
            """,
                guidance_type=GuidanceType.SAFETY_GUIDELINES,
                level=GuidanceLevel.BASIC,
                tags=["safety", "protection", "guidelines"],
            )
        )

        # Workflow guidance
        self._add_guidance_item(
            GuidanceItem(
                id="workflow_001",
                title="Standard Workflow for AI Agents",
                content="""
# Standard Workflow for AI Agents

## 1. Project Initialization

```python
# Register your agent
agent_profile = AgentProfile(
    agent_id="your_agent_id",
    name="Your Agent Name",
    capabilities=[AgentCapability.CODE_GENERATION, AgentCapability.PLANNING],
    collaboration_mode = CollaborationMode.COLLABORATIVE,
    safety_level = SafetyLevel.MEDIUM
)

protocol = get_collaboration_protocol(project_root)
result = protocol.register_agent(agent_profile)
```

## 2. Start Collaboration Session

```python
# Start a session
session_result = protocol.start_collaboration_session(agent_profile.agent_id)
session_id = session_result["session_id"]
```

## 3. Check Project Status

```python
# Check if vision interrogation is needed
vision_status = protocol.get_session_status(session_id)
if not vision_status["context"]["vision_status"]["ready_for_agents"]:
    # Start vision interrogation
    action = {
        "type": "vision_interrogation",
        "subtype": "start_interrogation",
        "project_type": "web_application"
    }
    result = protocol.execute_agent_action(session_id, action)
```

## 4. Execute Actions

```python
# Example: Read a file
action = {
    "type": "file_operation",
    "operation": "read",
    "file_path": "src / main.py"
}
result = protocol.execute_agent_action(session_id, action)
```

## 5. Handle Gates

```python
# Check for active gates
if vision_status["context"]["active_gates"]:
    # Ask user questions from gate
    # Submit responses
    # Wait for approval
    pass
```
            """,
                guidance_type=GuidanceType.WORKFLOW_GUIDANCE,
                level=GuidanceLevel.INTERMEDIATE,
                tags=["workflow", "process", "steps"],
            )
        )

        # Best practices
        self._add_guidance_item(
            GuidanceItem(
                id="best_practices_001",
                title="Best Practices for AI Agent Collaboration",
                content="""
# Best Practices for AI Agent Collaboration

## Communication

1. **Be Clear and Concise**: Explain what you're doing and why
2. **Ask for Clarification**: When uncertain, ask rather than assume
3. **Provide Context**: Explain your reasoning and alternatives considered
4. **Document Decisions**: Record important decisions and their rationale

## Safety

1. **Respect Boundaries**: Never modify protected files without permission
2. **Check Before Acting**: Verify safety before executing potentially risky operations
3. **Escalate When Needed**: Ask for human input when safety is uncertain
4. **Learn from Mistakes**: Update your behavior based on safety violations

## Efficiency

1. **Batch Operations**: Group related operations when possible
2. **Use Appropriate Tools**: Choose the right tool for each task
3. **Minimize Interruptions**: Complete tasks before asking for new input
4. **Provide Progress Updates**: Keep users informed of your progress

## Collaboration

1. **Understand User Intent**: Focus on what the user wants to achieve
2. **Suggest Improvements**: Offer better approaches when you see them
3. **Explain Trade - offs**: Help users understand the implications of choices
4. **Be Proactive**: Anticipate needs and suggest next steps

## Error Handling

1. **Graceful Degradation**: Handle errors without crashing
2. **Informative Messages**: Provide clear error messages and solutions
3. **Recovery Strategies**: Have fallback plans for common failures
4. **Learn from Errors**: Update your behavior to avoid repeating mistakes
            """,
                guidance_type=GuidanceType.BEST_PRACTICES,
                level=GuidanceLevel.INTERMEDIATE,
                tags=["best_practices", "collaboration", "communication"],
            )
        )

        # Examples
        self._add_guidance_item(
            GuidanceItem(
                id="examples_001",
                title="Common AI Agent Tasks and Examples",
                content="""
# Common AI Agent Tasks and Examples

## 1. Reading Project Files

```python
# Read a source file
action = {
    "type": "file_operation",
    "operation": "read",
    "file_path": "src / main.py"
}
result = protocol.execute_agent_action(session_id, action)
if result["status"] == "success":
    file_content = result["content"]
    # Process the file content
```

## 2. Creating New Files

```python
# Create a new file
action = {
    "type": "file_operation",
    "operation": "write",
    "file_path": "src / new_module.py",
    "content": "# New module\\n\\ndef hello():\\n    print('Hello, World!')"
}
result = protocol.execute_agent_action(session_id, action)
```

## 3. Starting Vision Interrogation

```python
# Start vision interrogation for a web application
action = {
    "type": "vision_interrogation",
    "subtype": "start_interrogation",
    "project_type": "web_application"
}
result = protocol.execute_agent_action(session_id, action)
```

## 4. Checking Session Status

```python
# Get current session status
status = protocol.get_session_status(session_id)
print(f"Actions taken: {status['session_info']['actions_taken']}")
print(f"Safety violations: {status['session_info']['safety_violations']}")
```

## 5. Handling User Interactions

```python
# Handle user approval
interaction = {
    "type": "approval",
    "action_id": "file_creation_001",
    "message": "User approved file creation"
}
result = protocol.handle_user_interaction(session_id, interaction)
```

## 6. Error Handling

```python
# Handle safety violations
if result["status"] == "safety_violation":
    print(f"Safety violation: {result['violation']}")
    if result.get("requires_user_approval"):
        # Ask user for permission
        print("This action requires user approval")
        # Wait for user response
```
            """,
                guidance_type=GuidanceType.EXAMPLES,
                level=GuidanceLevel.INTERMEDIATE,
                tags=["examples", "code", "tasks"],
            )
        )

        # Integration help
        self._add_guidance_item(
            GuidanceItem(
                id="integration_001",
                title="Integrating with Different AI Agent Platforms",
                content="""
# Integrating with Different AI Agent Platforms

## Cursor AI Integration

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
    collaboration_mode = CollaborationMode.COLLABORATIVE,
    safety_level = SafetyLevel.MEDIUM
)

# Register and start session
protocol.register_agent(agent_profile)
session_result = protocol.start_collaboration_session(agent_profile.agent_id)
```

## GitHub Copilot Integration

```python
# For GitHub Copilot
agent_profile = AgentProfile(
    agent_id="copilot_agent",
    name="GitHub Copilot",
    capabilities=[
        AgentCapability.CODE_GENERATION,
        AgentCapability.DOCUMENTATION
    ],
    collaboration_mode = CollaborationMode.ASSISTIVE,
    safety_level = SafetyLevel.HIGH
)
```

## Custom AI Agent Integration

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
    collaboration_mode = CollaborationMode.AUTONOMOUS,
    safety_level = SafetyLevel.CRITICAL,
    max_autonomous_actions = 5,
    requires_confirmation_for=["file_operation", "command_execution"]
)
```

## Environment Variables

Set these environment variables for your AI agent:

```bash
export AI_ONBOARD_PROJECT_ROOT="/path / to / project"
export AI_ONBOARD_AGENT_ID="your_agent_id"
export AI_ONBOARD_SAFETY_LEVEL="medium"
export AI_ONBOARD_COLLABORATION_MODE="collaborative"
```
            """,
                guidance_type=GuidanceType.INTEGRATION_HELP,
                level=GuidanceLevel.ADVANCED,
                tags=["integration", "platforms", "setup"],
            )
        )

    def _add_guidance_item(self, item: GuidanceItem):
        """Add a guidance item to the database."""
        self.guidance_items[item.id] = item

    def get_guidance_for_agent(
        self,
        agent_id: str,
        guidance_type: Optional[GuidanceType] = None,
        level: Optional[GuidanceLevel] = None,
    ) -> Dict[str, Any]:
        """Get guidance for a specific agent."""
        try:
            # Get or create agent profile
            if agent_id not in self.agent_profiles:
                self.agent_profiles[agent_id] = AgentGuidanceProfile(
                    agent_id=agent_id,
                    experience_level=GuidanceLevel.BASIC,
                    preferred_guidance_types=[
                        GuidanceType.ONBOARDING,
                        GuidanceType.BEST_PRACTICES,
                    ],
                )

            agent_profile = self.agent_profiles[agent_id]
            agent_profile.last_guidance_request = datetime.now()

            # Filter guidance items
            filtered_items = []
            for item in self.guidance_items.values():
                # Check type filter
                if guidance_type and item.guidance_type != guidance_type:
                    continue

                # Check level filter
                if level and item.level != level:
                    continue

                # Check if agent can access this level
                if not self._can_access_level(
                    agent_profile.experience_level, item.level
                ):
                    continue

                # Check if already completed
                if item.id in agent_profile.completed_guidance:
                    continue

                filtered_items.append(item)

            # Sort by relevance
            filtered_items.sort(
                key=lambda x: self._calculate_relevance_score(x, agent_profile)
            )

            # Return top items
            return {
                "status": "success",
                "agent_id": agent_id,
                "experience_level": agent_profile.experience_level.value,
                "guidance_items": [
                    {
                        "id": item.id,
                        "title": item.title,
                        "content": item.content,
                        "type": item.guidance_type.value,
                        "level": item.level.value,
                        "tags": item.tags,
                        "examples": item.examples,
                    }
                    for item in filtered_items[:10]  # Top 10 most relevant
                ],
                "total_available": len(filtered_items),
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to get guidance: {str(e)}"}

    def get_specific_guidance(self, guidance_id: str, agent_id: str) -> Dict[str, Any]:
        """Get a specific guidance item."""
        try:
            if guidance_id not in self.guidance_items:
                return {
                    "status": "error",
                    "message": f"Guidance item {guidance_id} not found",
                }

            item = self.guidance_items[guidance_id]

            # Check if agent can access this item
            if agent_id in self.agent_profiles:
                agent_profile = self.agent_profiles[agent_id]
                if not self._can_access_level(
                    agent_profile.experience_level, item.level
                ):
                    return {
                        "status": "error",
                        "message": f"Agent {agent_id} cannot access guidance level {item.level.value}",
                    }

            # Mark as accessed
            if agent_id in self.agent_profiles:
                self.agent_profiles[agent_id].guidance_history.append(
                    {
                        "guidance_id": guidance_id,
                        "accessed_at": datetime.now().isoformat(),
                        "title": item.title,
                    }
                )

            return {
                "status": "success",
                "guidance_item": {
                    "id": item.id,
                    "title": item.title,
                    "content": item.content,
                    "type": item.guidance_type.value,
                    "level": item.level.value,
                    "tags": item.tags,
                    "examples": item.examples,
                    "prerequisites": item.prerequisites,
                    "related_items": item.related_items,
                },
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get specific guidance: {str(e)}",
            }

    def mark_guidance_completed(
        self, agent_id: str, guidance_id: str
    ) -> Dict[str, Any]:
        """Mark a guidance item as completed by an agent."""
        try:
            if agent_id not in self.agent_profiles:
                return {"status": "error", "message": f"Agent {agent_id} not found"}

            if guidance_id not in self.guidance_items:
                return {
                    "status": "error",
                    "message": f"Guidance item {guidance_id} not found",
                }

            agent_profile = self.agent_profiles[agent_id]

            if guidance_id not in agent_profile.completed_guidance:
                agent_profile.completed_guidance.append(guidance_id)

                # Check if agent should level up
                self._check_agent_level_up(agent_profile)

            return {
                "status": "success",
                "message": f"Guidance {guidance_id} marked as completed",
                "completed_count": len(agent_profile.completed_guidance),
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to mark guidance as completed: {str(e)}",
            }

    def get_agent_progress(self, agent_id: str) -> Dict[str, Any]:
        """Get progress summary for an agent."""
        try:
            if agent_id not in self.agent_profiles:
                return {"status": "error", "message": f"Agent {agent_id} not found"}

            agent_profile = self.agent_profiles[agent_id]

            # Calculate progress metrics
            total_guidance = len(self.guidance_items)
            completed_guidance = len(agent_profile.completed_guidance)
            completion_rate = (
                (completed_guidance / total_guidance) * 100 if total_guidance > 0 else 0
            )

            # Get guidance by type
            guidance_by_type = {}
            for item in self.guidance_items.values():
                if item.id in agent_profile.completed_guidance:
                    guidance_type = item.guidance_type.value
                    if guidance_type not in guidance_by_type:
                        guidance_by_type[guidance_type] = 0
                    guidance_by_type[guidance_type] += 1

            return {
                "status": "success",
                "agent_id": agent_id,
                "experience_level": agent_profile.experience_level.value,
                "progress": {
                    "total_guidance_items": total_guidance,
                    "completed_items": completed_guidance,
                    "completion_rate": completion_rate,
                    "guidance_by_type": guidance_by_type,
                },
                "recent_activity": (
                    agent_profile.guidance_history[-10:]
                    if agent_profile.guidance_history
                    else []
                ),
                "last_guidance_request": (
                    agent_profile.last_guidance_request.isoformat()
                    if agent_profile.last_guidance_request
                    else None
                ),
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get agent progress: {str(e)}",
            }

    def generate_contextual_guidance(
        self, agent_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate contextual guidance based on current situation."""
        try:
            # Analyze context to determine relevant guidance
            relevant_guidance = []

            # Check for safety violations
            if context.get("safety_violations", 0) > 0:
                relevant_guidance.append("safety_001")

            # Check for vision interrogation needs
            if not context.get("vision_confirmed", False):
                relevant_guidance.append("onboarding_001")

            # Check for workflow needs
            if context.get("actions_taken", 0) == 0:
                relevant_guidance.append("workflow_001")

            # Get guidance items
            guidance_items = []
            for guidance_id in relevant_guidance:
                if guidance_id in self.guidance_items:
                    item = self.guidance_items[guidance_id]
                    guidance_items.append(
                        {
                            "id": item.id,
                            "title": item.title,
                            "content": item.content,
                            "type": item.guidance_type.value,
                            "level": item.level.value,
                            "tags": item.tags,
                        }
                    )

            return {
                "status": "success",
                "agent_id": agent_id,
                "contextual_guidance": guidance_items,
                "context_analysis": {
                    "safety_violations": context.get("safety_violations", 0),
                    "vision_confirmed": context.get("vision_confirmed", False),
                    "actions_taken": context.get("actions_taken", 0),
                },
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate contextual guidance: {str(e)}",
            }

    def _can_access_level(
        self, agent_level: GuidanceLevel, item_level: GuidanceLevel
    ) -> bool:
        """Check if an agent can access a guidance level."""
        level_hierarchy = {
            GuidanceLevel.BASIC: 1,
            GuidanceLevel.INTERMEDIATE: 2,
            GuidanceLevel.ADVANCED: 3,
            GuidanceLevel.EXPERT: 4,
        }

        return level_hierarchy[agent_level] >= level_hierarchy[item_level]

    def _calculate_relevance_score(
        self, item: GuidanceItem, agent_profile: AgentGuidanceProfile
    ) -> float:
        """Calculate relevance score for a guidance item."""
        score = 0.0

        # Base score
        score += 1.0

        # Preference bonus
        if item.guidance_type in agent_profile.preferred_guidance_types:
            score += 2.0

        # Level appropriateness
        if item.level == agent_profile.experience_level:
            score += 1.5
        elif self._can_access_level(agent_profile.experience_level, item.level):
            score += 1.0

        # Completion penalty
        if item.id in agent_profile.completed_guidance:
            score -= 3.0

        return score

    def _check_agent_level_up(self, agent_profile: AgentGuidanceProfile):
        """Check if an agent should level up based on completed guidance."""
        completed_count = len(agent_profile.completed_guidance)

        if (
            completed_count >= 10
            and agent_profile.experience_level == GuidanceLevel.BASIC
        ):
            agent_profile.experience_level = GuidanceLevel.INTERMEDIATE
        elif (
            completed_count >= 25
            and agent_profile.experience_level == GuidanceLevel.INTERMEDIATE
        ):
            agent_profile.experience_level = GuidanceLevel.ADVANCED
        elif (
            completed_count >= 50
            and agent_profile.experience_level == GuidanceLevel.ADVANCED
        ):
            agent_profile.experience_level = GuidanceLevel.EXPERT


def get_ai_agent_guidance_system(project_root: Path) -> AIAgentGuidanceSystem:
    """Get AI agent guidance system instance."""
    return AIAgentGuidanceSystem(project_root)
