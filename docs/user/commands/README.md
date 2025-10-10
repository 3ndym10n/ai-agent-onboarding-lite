# Command Reference Guide

AI Onboard provides a comprehensive set of intelligent commands organized by functionality. This guide covers every command with examples, use cases, and best practices.

## 🎯 Command Categories

### 🏗️ Project Management Commands

Core commands for project setup, planning, and tracking:

- `charter` - Create and manage project vision and goals
- `plan` - Generate and manage intelligent project plans
- `align` - Verify alignment between vision and execution
- `validate` - Comprehensive project health validation
- `dashboard` - Visual project status and progress overview
- `project` - Unified project-management engine (critical path, WBS, prioritization)

### ⚡ Optimization & Improvement Commands

Commands for continuous improvement and performance optimization:

- [`kaizen`](#kaizen) - Continuous improvement automation
- [`kaizen-auto`](#kaizen-auto) - Automated Kaizen cycle management
- [`opt-experiments`](#opt-experiments) - Optimization experiment framework
- [`unified-metrics`](#unified-metrics) - Comprehensive metrics collection and analysis

### 🤖 AI Systems & Collaboration Commands  

Advanced AI integration and collaboration features:

- [`ai-agent`](#ai-agent) - AI agent management and collaboration
- [`aaol`](#aaol) - AI Agent Orchestration Layer
- [`cursor`](#cursor) - Cursor AI integration and workflow
- [`enhanced-context`](#enhanced-context) - Advanced conversation context management
- [`decision-pipeline`](#decision-pipeline) - Multi-stage decision processes
- [`chat`](#chat) - Natural-language assistant with vision guardrails

### `chat`

**Purpose**: Converse with AI Onboard using natural language instead of direct CLI flags.

#### Automatic Alignment Guardrails
- Every chat request runs the project's vision alignment detector automatically.
- Requests flagged as `block` are stopped with the detected guardrail reasons.
- `review` results post a heads-up before the assistant continues with the response.

#### Basic Usage

```bash
python -m ai_onboard chat "Add email validation to the contact form"
```

### 🛠️ Development & Integration Commands

Tools for development workflow integration and system management:

- [`debug`](#debug) - Smart debugging and error analysis
- [`cleanup`](#cleanup) - Safe project cleanup and maintenance
- [`checkpoint`](#checkpoint) - Project state management and rollback

### 🎓 Learning & User Experience Commands

Commands for personalization, learning, and user experience optimization:

- [`user-prefs`](#user-prefs) - User preference learning and personalization
- [`ux`](#ux) - User experience enhancements and analytics
- [`help`](#help) - Context-aware help and tutorial system
- [`suggest`](#suggest) - Personalized recommendations and feature discovery

### 📊 Analytics & Insights Commands

Commands for understanding project patterns and performance:

- [`prompt`](#prompt) - State summaries and AI agent context
- [`status`](#status) - System health and operational status
- [`discover`](#discover) - Feature discovery and capability exploration

## 📋 Core Commands Reference

### `charter`

**Purpose**: Create and manage project vision, goals, and foundational documentation.

#### Basic Usage

```bash
# Interactive charter creation
python -m ai_onboard charter

# Create charter from template
python -m ai_onboard charter --template software_development

# Update existing charter
python -m ai_onboard charter --update

# Validate charter quality
python -m ai_onboard charter --validate
```

#### Advanced Options

```bash
# Charter with AI assistance
python -m ai_onboard charter --ai-assist --project-type "saas_platform"

# Generate from existing documentation
python -m ai_onboard charter --from-docs "docs/requirements/"

# Export charter formats
python -m ai_onboard charter --export-pdf --export-markdown

# Team collaborative charter
python -m ai_onboard charter --collaborative --stakeholders "team@company.com"
```

#### Use Cases

- **New Project Setup**: Define clear vision and success criteria
- **Project Restart**: Realign team around refreshed vision
- **Stakeholder Alignment**: Create shared understanding of project goals
- **Scope Management**: Establish boundaries and constraints

#### Success Patterns

```bash
# The "Vision-First" Pattern
python -m ai_onboard charter
python -m ai_onboard plan
python -m ai_onboard align
python -m ai_onboard validate
```

---

### `plan`

**Purpose**: Generate, manage, and optimize intelligent project plans with AI-powered insights.

#### Plan Basic Usage

```bash
# Generate project plan
python -m ai_onboard plan

# View current plan
python -m ai_onboard plan --show

# Update plan progress
python -m ai_onboard plan task --complete T5

# Manage milestones
python -m ai_onboard plan milestone --complete M1
```

#### Advanced Planning

```bash
# AI-optimized planning
python -m ai_onboard plan --optimize-velocity --risk-level conservative

# Scenario planning
python -m ai_onboard plan --scenarios "aggressive,balanced,conservative"

# Resource-constrained planning
python -m ai_onboard plan --resources "2_developers,1_designer" --timeline "12_weeks"

# Critical path analysis
python -m ai_onboard plan critical-path --optimize
```

#### Task Management

```bash
# Task operations
python -m ai_onboard plan task --list --status pending
python -m ai_onboard plan task --assign T7 --to "developer@team.com"
python -m ai_onboard plan task --block T8 --reason "waiting_for_approval"
python -m ai_onboard plan task --estimate T9 --effort "5_days"

# Dependency management
python -m ai_onboard plan deps --show T10
python -m ai_onboard plan deps --add T11 --depends-on T10
python -m ai_onboard plan deps --validate --fix-conflicts
```

#### Milestone Management

```bash
# Milestone operations
python -m ai_onboard plan milestone --list --upcoming
python -m ai_onboard plan milestone --progress M2
python -m ai_onboard plan milestone --forecast --confidence 0.8
python -m ai_onboard plan milestone --report M1 --stakeholders
```

---

### `dashboard`

**Purpose**: Visual project status overview with intelligent insights and progress tracking.

#### Dashboard Basic Usage

```bash
# Show project dashboard
python -m ai_onboard dashboard

# Detailed dashboard
python -m ai_onboard dashboard --detailed

# Team-focused dashboard
python -m ai_onboard dashboard --team

# Executive summary dashboard
python -m ai_onboard dashboard --executive
```

#### Dashboard Customization

```bash
# Configure dashboard widgets
python -m ai_onboard dashboard config \
  --widgets "progress,velocity,quality,risks" \
  --refresh-rate "5_minutes"

# Custom dashboard themes
python -m ai_onboard dashboard theme --set "professional"
python -m ai_onboard dashboard theme --customize --colors "blue,green,red"

# Export dashboard
python -m ai_onboard dashboard --export-pdf --email "stakeholders@company.com"
```

#### Real-time Monitoring

```bash
# Live dashboard (auto-refresh)
python -m ai_onboard dashboard --live --refresh 30

# Alert configuration
python -m ai_onboard dashboard alerts \
  --velocity-drop 0.8 \
  --quality-gate 0.9 \
  --timeline-risk 0.7
```

---

### `project`

**Purpose**: Access the unified project-management engine for critical path analysis, WBS status, task prioritization, and completion detection.

#### Project Basic Usage

```bash
# Analyze critical path
python -m ai_onboard project critical-path

# View progress dashboard (unified analytics)
python -m ai_onboard project progress

# Detect completed tasks using UPME
python -m ai_onboard project task-completion

# Prioritize tasks across the plan
python -m ai_onboard project prioritize

# Inspect WBS synchronization status
python -m ai_onboard project wbs
```

#### Implementation Notes

- Powered by `UnifiedProjectManagementEngine` (UPME)
- Legacy modules (`task_completion_detector`, `task_prioritization_engine`, WBS engines) now route through compatibility shims
- Deprecation warnings appear when using legacy APIs; migrate to unified engine calls where possible

#### Best Practices

- Run the critical path and prioritization commands after major plan updates
- Use the WBS command to confirm consistency before validation
- Rerun `task-completion` after committing code changes to keep the plan in sync

---

### `kaizen`

**Purpose**: Continuous improvement automation with intelligent optimization cycles.

#### Kaizen Basic Usage

```bash
# Run improvement cycle
python -m ai_onboard kaizen

# Automated continuous improvement
python -m ai_onboard kaizen-auto start

# View improvement opportunities
python -m ai_onboard kaizen opportunities

# Improvement history and analytics
python -m ai_onboard kaizen analytics
```

#### Advanced Kaizen Features

```bash
# Multi-category analysis
python -m ai_onboard kaizen run-cycle \
  --categories "performance,ux,reliability,security"

# Custom improvement focus
python -m ai_onboard kaizen focus \
  --area "team_velocity" \
  --target 1.2 \
  --timeline "2_weeks"

# Automated experimentation
python -m ai_onboard kaizen experiment \
  --hypothesis "parallel_testing_improves_velocity" \
  --duration "1_week"
```

---

### `cursor`

**Purpose**: Seamless integration with Cursor AI for enhanced development workflows.

#### Cursor Basic Usage

```bash
# Initialize Cursor integration
python -m ai_onboard cursor init

# Check integration status
python -m ai_onboard cursor status

# Share project context with Cursor
python -m ai_onboard cursor context --share

# Manage Cursor sessions
python -m ai_onboard cursor session --list
```

#### Advanced Cursor Features

```bash
# AI-powered command translation
python -m ai_onboard cursor translate "create a user authentication system"

# Project context optimization
python -m ai_onboard cursor context --optimize --focus "current_sprint"

# Collaborative AI sessions
python -m ai_onboard cursor session --collaborate --team "dev_team"

# Custom Cursor configuration
python -m ai_onboard cursor config \
  --agent-profile "senior_developer" \
  --collaboration-mode "pair_programming"
```

---

### `ux`

**Purpose**: User experience enhancements, analytics, and satisfaction tracking.

#### UX Basic Usage

```bash
# View UX analytics
python -m ai_onboard ux analytics user

# Provide satisfaction feedback
python -m ai_onboard ux feedback --score 4 --context "daily_workflow"

# View user journey
python -m ai_onboard ux journey show

# Manage UX interventions
python -m ai_onboard ux interventions list
```

#### Advanced UX Features

```bash
# Detailed UX analytics
python -m ai_onboard ux analytics user --detailed
python -m ai_onboard ux analytics satisfaction
python -m ai_onboard ux analytics errors

# UX configuration
python -m ai_onboard ux config show
python -m ai_onboard ux config update \
  --enable-proactive-help true \
  --satisfaction-frequency milestone

# UX testing and development
python -m ai_onboard ux test --trigger-error
python -m ai_onboard ux test --trigger-onboarding
```

---

## 🎯 Command Patterns & Workflows

### Quick Reference Patterns

#### Daily Workflow Pattern

```bash
# Morning check-in (2 minutes)
python -m ai_onboard dashboard
python -m ai_onboard suggest
python -m ai_onboard status

# End-of-day review (3 minutes)  
python -m ai_onboard prompt progress
python -m ai_onboard ux feedback --score <1-5>
```

#### Weekly Review Pattern

```bash
# Weekly planning and optimization (15 minutes)
python -m ai_onboard ux analytics user
python -m ai_onboard kaizen opportunities
python -m ai_onboard plan milestone --next
python -m ai_onboard validate --comprehensive
```

#### Project Setup Pattern

```bash
# Complete project foundation (20 minutes)
python -m ai_onboard charter
python -m ai_onboard plan
python -m ai_onboard align
python -m ai_onboard validate
python -m ai_onboard dashboard --setup
```

#### Optimization Cycle Pattern

```bash
# Continuous improvement cycle (30 minutes)
python -m ai_onboard kaizen run-cycle
python -m ai_onboard opt-experiments design --name "velocity_improvement"
python -m ai_onboard unified-metrics trend --category performance
python -m ai_onboard cursor config --optimize
```

### Advanced Command Combinations

#### AI Collaboration Setup

```bash
# Complete AI workflow setup (25 minutes)
python -m ai_onboard ai-agent register --capabilities "code_generation,planning"
python -m ai_onboard cursor init --integration-level advanced
python -m ai_onboard enhanced-context setup --team-sharing
python -m ai_onboard decision-pipeline config --multi-stage
```

#### Comprehensive Analytics

```bash
# Full project analytics suite (15 minutes)
python -m ai_onboard unified-metrics report --comprehensive
python -m ai_onboard ux analytics user --detailed
python -m ai_onboard kaizen analytics --recommendations
python -m ai_onboard prompt progress --milestone-analysis
```

## 🔧 Command Customization

### Global Configuration

```bash
# Set user preferences
python -m ai_onboard config user \
  --expertise-level intermediate \
  --interface-mode streamlined \
  --theme professional

# Configure default behaviors
python -m ai_onboard config defaults \
  --auto-save true \
  --progress-notifications enabled \
  --optimization-suggestions proactive
```

### Team Configuration

```bash
# Team-wide settings
python -m ai_onboard config team \
  --shared-workflows enabled \
  --collaboration-mode structured \
  --reporting-frequency weekly

# Workspace configuration
python -m ai_onboard config workspace \
  --project-templates "software,product,research" \
  --quality-gates "coverage:90,performance:95"
```

### Integration Configuration

```bash
# External tool integration
python -m ai_onboard config integrations \
  --git-provider github \
  --pm-tool jira \
  --communication slack

# API and webhook configuration
python -m ai_onboard config api \
  --webhook-url "https://your-system.com/webhooks" \
  --auth-token-file ".env"
```

## 🆘 Command Help & Discovery

### Built-in Help System

```bash
# Context-aware help
python -m ai_onboard help

# Command-specific help
python -m ai_onboard help charter
python -m ai_onboard help plan --examples

# Interactive tutorials
python -m ai_onboard help --tutorial getting_started
python -m ai_onboard help --tutorial optimization_workflows
```

### Feature Discovery

```bash
# Discover relevant commands
python -m ai_onboard discover

# Explore command categories
python -m ai_onboard discover --category ai_systems
python -m ai_onboard discover --expertise-level advanced

# Find commands by use case
python -m ai_onboard discover --use-case "project_optimization"
python -m ai_onboard discover --use-case "team_collaboration"
```

### Smart Suggestions

```bash
# Get personalized recommendations
python -m ai_onboard suggest

# Context-specific suggestions
python -m ai_onboard suggest --context "project_setup"
python -m ai_onboard suggest --context "optimization"

# Feature-specific suggestions
python -m ai_onboard suggest --focus "productivity"
python -m ai_onboard suggest --focus "quality"
```

## 🎯 Command Mastery Tips

### Efficiency Shortcuts

1. **Use Tab Completion**: Enable bash/zsh completion for faster command entry
2. **Alias Common Patterns**: Create aliases for frequently used command combinations
3. **Batch Operations**: Use command chaining for related operations
4. **Configuration Presets**: Set up configuration presets for different project types

### Advanced Usage Patterns

1. **Pipeline Integration**: Use commands in CI/CD pipelines for automated project management
2. **Scripting**: Create scripts that combine multiple commands for complex workflows
3. **Monitoring**: Set up automated command execution for continuous monitoring
4. **Integration**: Connect commands to external systems via API and webhooks

### Troubleshooting Commands

```bash
# System diagnostics
python -m ai_onboard debug analyze
python -m ai_onboard status --comprehensive
python -m ai_onboard validate --report

# Configuration debugging
python -m ai_onboard config show --all
python -m ai_onboard config validate
python -m ai_onboard config reset --component <component>
```

---

## 🎓 Learning Path

### Beginner Commands (Week 1)

Start with these essential commands:

- `charter`, `plan`, `dashboard`, `help`, `status`

### Intermediate Commands (Week 2-3)

Add optimization and AI features:

- `kaizen`, `cursor`, `ux`, `suggest`, `validate`

### Advanced Commands (Week 4+)

Master the full system:

- `opt-experiments`, `enhanced-context`, `decision-pipeline`, `api`, `unified-metrics`

---

**🚀 Ready to master AI Onboard commands?** Start with the [Getting Started Guide](../getting-started.md) and gradually explore more advanced features as you become comfortable with the basics!
