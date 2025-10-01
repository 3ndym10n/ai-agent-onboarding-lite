# API Reference Guide

AI Onboard provides comprehensive APIs for programmatic access, integration, and automation. This guide covers all available APIs, their usage patterns, and integration examples.

## 🎯 API Overview

### Available API Categories

#### 🚀 Core APIs

- **Project Management API** - Charter, plan, and progress management
- **Analytics API** - Metrics collection and analysis
- **User Experience API** - UX tracking and personalization
- **Validation API** - Project health and quality validation

#### 🔗 Integration APIs

- **Webhook API** - Real-time event notifications
- **Plugin API** - Custom plugin development
- **External Tool API** - Third-party integrations

## 📋 Core API Reference

### Project Management API

#### Charter API

```python
from ai_onboard.api import charter

# Create new charter
charter_data = {
    "project_name": "My Project",
    "vision_statement": "Transform team collaboration",
    "success_criteria": ["satisfaction >4.5", "80% adoption"]
}
result = charter.create(charter_data)

# Update existing charter
charter.update("project-id", {"vision_statement": "New vision"})

# Validate charter
validation = charter.validate("project-id")
```

#### Plan API

```python
from ai_onboard.api import plan

# Generate project plan
plan_config = {
    "project_size": "medium",
    "team_size": 5,
    "timeline_weeks": 12,
    "risk_level": "moderate"
}
project_plan = plan.generate(charter_id, plan_config)

# Update task progress
plan.update_task("task-id", {"status": "completed", "notes": "Task completed ahead of schedule"})

# Get critical path
critical_path = plan.get_critical_path("project-id")
```

#### Progress API

```python
from ai_onboard.api import progress

# Get project dashboard data
dashboard = progress.get_dashboard("project-id")

# Update milestone status
progress.update_milestone("milestone-id", {"status": "completed", "completion_date": "2025-01-15"})

# Generate progress report
report = progress.generate_report("project-id", {"format": "pdf", "include_charts": True})
```

### Analytics API

#### Metrics API

```python
from ai_onboard.api import metrics

# Collect custom metrics
metrics.record("velocity", {"team": "backend", "value": 1.2, "unit": "tasks/day"})

# Query metrics with filters
velocity_data = metrics.query({
    "metric": "velocity",
    "team": "backend",
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
})

# Set up metric alerts
metrics.alert("velocity", {"threshold": 0.8, "condition": "below", "notification": "email"})
```

#### Trend Analysis API

```python
from ai_onboard.api import trends

# Analyze performance trends
trend_analysis = trends.analyze("velocity", {"period": "30_days", "granularity": "daily"})

# Predict future performance
prediction = trends.predict("velocity", {"future_periods": 14, "confidence_level": 0.95})

# Identify patterns
patterns = trends.identify_patterns("quality_metrics", {"min_confidence": 0.8})
```

### User Experience API

#### UX Analytics API

```python
from ai_onboard.api import ux_analytics

# Track user interactions
ux_analytics.track_interaction("command_executed", {"command": "charter", "duration_ms": 1500})

# Analyze user journey
journey = ux_analytics.analyze_journey("user-id", {"timeframe": "7_days"})

# Get satisfaction metrics
satisfaction = ux_analytics.get_satisfaction_metrics("project-id")
```

#### Personalization API

```python
from ai_onboard.api import personalization

# Update user preferences
personalization.update_preferences("user-id", {
    "expertise_level": "expert",
    "interface_mode": "streamlined",
    "theme": "dark"
})

# Get personalized recommendations
recommendations = personalization.get_recommendations("user-id", {"context": "project_setup"})
```

## 🔗 Integration APIs

### Webhook API

#### Register Webhooks

```python
from ai_onboard.api import webhooks

# Register project milestone webhook
webhook_config = {
    "url": "https://your-system.com/webhooks/ai-onboard",
    "events": ["milestone_completed", "task_blocked", "charter_updated"],
    "secret": "your-webhook-secret"
}
webhook_id = webhooks.register(webhook_config)

# Test webhook
webhooks.test(webhook_id, {"event": "milestone_completed", "data": {"milestone_id": "M1"}})
```

#### Webhook Payload Examples

```json
// Milestone completed event
{
  "event": "milestone_completed",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "milestone_id": "M1",
    "project_id": "project-123",
    "completion_date": "2025-01-15",
    "tasks_completed": 8,
    "next_milestone": "M2"
  }
}

// Task blocked event
{
  "event": "task_blocked",
  "timestamp": "2025-01-15T14:20:00Z",
  "data": {
    "task_id": "T5",
    "project_id": "project-123",
    "reason": "waiting_for_approval",
    "blocked_by": "stakeholder_review"
  }
}
```

### Plugin API

#### Create Custom Plugin

```python
from ai_onboard.api import plugins

class MyCustomPlugin:
    def __init__(self):
        self.name = "my_custom_plugin"
        self.version = "1.0.0"
        self.description = "Custom functionality for my workflow"

    def execute(self, context):
        """Main plugin execution logic"""
        # Custom business logic here
        return {"status": "success", "result": "custom_result"}

# Register plugin
plugin = MyCustomPlugin()
plugins.register(plugin)
```

#### Plugin Hooks

```python
# Available plugin hooks
hooks = {
    "pre_command": "before_command_execution",
    "post_command": "after_command_execution",
    "on_error": "when_command_fails",
    "on_milestone": "when_milestone_reached",
    "on_validation": "during_validation_process"
}

# Register hook handler
plugins.register_hook("post_command", my_handler_function)
```

## 🚀 Quick Start Examples

### Basic API Usage

```python
#!/usr/bin/env python3
"""Basic AI Onboard API usage example"""

import ai_onboard as aio

def main():
    # Initialize connection
    aio.init()

    # Create a project charter
    charter = aio.charter.create({
        "project_name": "API Demo Project",
        "vision_statement": "Demonstrate AI Onboard API capabilities",
        "success_criteria": ["complete_api_examples", "document_use_cases"]
    })

    # Generate project plan
    plan = aio.plan.generate(charter["id"], {
        "project_size": "small",
        "timeline_weeks": 4
    })

    # Set up progress tracking
    dashboard = aio.progress.get_dashboard(charter["id"])

    # Record metrics
    aio.metrics.record("api_usage", {"count": 1, "success": True})

    print(f"Project created: {charter['project_name']}")
    print(f"Tasks generated: {len(plan['tasks'])}")

if __name__ == "__main__":
    main()
```

### Integration Example

```python
#!/usr/bin/env python3
"""AI Onboard integration with external project management tool"""

import ai_onboard as aio
import requests

def sync_with_jira(project_id):
    """Sync AI Onboard project with Jira"""

    # Get AI Onboard project data
    charter = aio.charter.get(project_id)
    plan = aio.plan.get(project_id)

    # Create Jira project
    jira_project = create_jira_project(charter)

    # Sync tasks
    for task in plan["tasks"]:
        create_jira_issue(jira_project["key"], task)

    # Set up webhook for progress updates
    aio.webhooks.register({
        "url": f"https://your-jira.com/rest/webhooks/ai-onboard/{project_id}",
        "events": ["task_completed", "milestone_reached"]
    })

def create_jira_project(charter):
    """Create corresponding Jira project"""
    # Implementation for Jira API integration
    pass

def create_jira_issue(project_key, task):
    """Create Jira issue from AI Onboard task"""
    # Implementation for Jira API integration
    pass
```

## 🔧 Advanced Configuration

### API Settings

```python
from ai_onboard.api import config

# Configure API behavior
config.update({
    "timeout": 30,
    "retry_attempts": 3,
    "rate_limiting": True,
    "logging_level": "INFO"
})

# Authentication settings
config.auth({
    "type": "api_key",
    "key": "your-api-key",
    "secret": "your-api-secret"
})
```

### Rate Limiting

```python
# Check rate limits
limits = config.get_rate_limits()

# Handle rate limiting
if limits["remaining"] < 10:
    print("Approaching rate limit, consider batching requests")
```

## 🛡️ Error Handling

### Standard Error Responses

```python
from ai_onboard.api.exceptions import (
    ValidationError,
    NotFoundError,
    RateLimitError,
    AuthenticationError
)

try:
    result = aio.charter.create(charter_data)
except ValidationError as e:
    print(f"Invalid charter data: {e.details}")
except RateLimitError:
    print("Rate limit exceeded, retry later")
except AuthenticationError:
    print("Invalid API credentials")
except NotFoundError as e:
    print(f"Resource not found: {e.resource_id}")
```

### Error Recovery Patterns

```python
import time
from ai_onboard.api.exceptions import APIError

def robust_api_call(api_function, *args, **kwargs):
    """Robust API call with retry logic"""
    max_retries = 3
    backoff_seconds = 1

    for attempt in range(max_retries):
        try:
            return api_function(*args, **kwargs)
        except APIError as e:
            if attempt == max_retries - 1:
                raise e

            print(f"API call failed (attempt {attempt + 1}), retrying in {backoff_seconds}s...")
            time.sleep(backoff_seconds)
            backoff_seconds *= 2

    raise RuntimeError("All retry attempts failed")
```

## 📚 API Best Practices

### Performance Optimization

1. **Batch Operations**: Use batch APIs for multiple operations
2. **Caching**: Cache frequently accessed data locally
3. **Async Operations**: Use asynchronous APIs for non-blocking operations
4. **Pagination**: Handle large result sets with pagination

### Security Considerations

1. **Secure Credentials**: Store API keys securely, never in code
2. **Rate Limiting**: Implement proper rate limiting to avoid throttling
3. **Input Validation**: Always validate API inputs before sending
4. **Error Handling**: Implement comprehensive error handling

### Monitoring & Logging

```python
import logging

# Configure API logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_onboard_api")

# Log API operations
try:
    result = aio.charter.create(charter_data)
    logger.info(f"Charter created successfully: {result['id']}")
except Exception as e:
    logger.error(f"Failed to create charter: {str(e)}")
```

---

**🚀 Ready to integrate?** Start with the [Core APIs](#core-apis) and explore [Integration APIs](#integration-apis) for advanced use cases!

**❓ Need specific API help?** Check the [Plugin API](#plugin-api) or [Webhook API](#webhook-api) sections.

**🔧 Want to extend functionality?** Explore the [Plugin Development Guide](../advanced/plugin-development.md)
