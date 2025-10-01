# CLI Reference - Quick Command Guide

This is a comprehensive quick reference for AI Onboard CLI commands organized by category. For detailed documentation, see [Command Reference](commands/README.md).

## 🎯 Quick Start Commands

```bash
# Project setup (first 5 minutes)
python -m ai_onboard charter                    # Create project vision
python -m ai_onboard plan                       # Generate project roadmap
python -m ai_onboard align                      # Verify vision-plan alignment
python -m ai_onboard validate                   # Health check
python -m ai_onboard dashboard                  # Visual progress overview

# Daily workflow (2-5 minutes)
python -m ai_onboard dashboard                  # Quick status check
python -m ai_onboard suggest                    # Get AI recommendations
python -m ai_onboard status                     # System health check
```

## 🏗️ Project Management

### Core Project Commands

```bash
# Project lifecycle
python -m ai_onboard charter                    # Create/update project charter
python -m ai_onboard plan                       # Generate project roadmap
python -m ai_onboard align                      # Check vision alignment
python -m ai_onboard validate                   # Project health validation
python -m ai_onboard dashboard                  # Visual progress tracking

# Project operations
python -m ai_onboard project critical-path      # Analyze critical path
python -m ai_onboard project progress           # Unified progress dashboard
python -m ai_onboard project task-completion    # Detect completed tasks
python -m ai_onboard project prioritize         # Task prioritization
python -m ai_onboard project wbs               # WBS status inspection
```

### Advanced Project Commands

```bash
# Project analysis
python -m ai_onboard prompt progress            # Detailed progress analysis
python -m ai_onboard prompt summary             # Project summary for AI agents
python -m ai_onboard prompt rules               # Preflight validation rules

# Project optimization
python -m ai_onboard plan --optimize-velocity   # Velocity optimization
python -m ai_onboard plan --scenarios           # Scenario planning
python -m ai_onboard plan milestone --next      # Next milestone planning
```

## ⚡ Optimization & Improvement

### Continuous Improvement

```bash
# Kaizen cycles
python -m ai_onboard kaizen                     # Run improvement cycle
python -m ai_onboard kaizen-auto start          # Automated Kaizen
python -m ai_onboard kaizen opportunities       # Find improvement opportunities
python -m ai_onboard kaizen analytics           # Improvement analytics

# Optimization experiments
python -m ai_onboard opt-experiments design     # Design A/B experiments
python -m ai_onboard opt-experiments run        # Execute experiments
python -m ai_onboard opt-experiments analyze    # Analyze results
```

### Performance & Metrics

```bash
# System metrics
python -m ai_onboard unified-metrics report     # Comprehensive metrics
python -m ai_onboard unified-metrics trend      # Trend analysis
python -m ai_onboard unified-metrics alert      # Set up metric alerts

# Performance optimization
python -m ai_onboard config optimize            # Optimize configuration
python -m ai_onboard cleanup --routine          # Routine maintenance
python -m ai_onboard debug analyze              # Performance analysis
```

## 🤖 AI Systems & Collaboration

### AI Agent Management

```bash
# Agent operations
python -m ai_onboard ai-agent register          # Register new AI agent
python -m ai_onboard ai-agent configure         # Configure agent capabilities
python -m ai_onboard ai-agent team create       # Create agent teams
python -m ai_onboard ai-agent workflow run      # Run multi-agent workflows

# Agent analytics
python -m ai_onboard ai-agent analytics         # Agent performance metrics
python -m ai_onboard ai-agent status            # Agent status overview
```

### Cursor AI Integration

```bash
# Cursor integration
python -m ai_onboard cursor init                # Initialize Cursor integration
python -m ai_onboard cursor status              # Check integration status
python -m ai_onboard cursor context share       # Share project context
python -m ai_onboard cursor translate           # Natural language translation

# Advanced Cursor features
python -m ai_onboard cursor session start       # Start collaborative session
python -m ai_onboard cursor context optimize    # Optimize context sharing
python -m ai_onboard cursor config              # Configure Cursor settings
```

## 🛠️ Development Integration

### Debugging & Analysis

```bash
# Debug operations
python -m ai_onboard debug analyze              # Comprehensive analysis
python -m ai_onboard debug profile              # Performance profiling
python -m ai_onboard debug memory               # Memory usage analysis
python -m ai_onboard debug logs                 # Log analysis

# System diagnostics
python -m ai_onboard status --comprehensive     # Full system status
python -m ai_onboard doctor --full-check        # Complete system check
python -m ai_onboard validate --report          # Detailed validation report
```

### Cleanup & Maintenance

```bash
# Safe cleanup operations
python -m ai_onboard cleanup --dry-run          # Preview cleanup
python -m ai_onboard cleanup --backup           # Cleanup with backup
python -m ai_onboard cleanup --cache            # Clear caches only
python -m ai_onboard cleanup --logs             # Clear old logs

# Checkpoint management
python -m ai_onboard checkpoint create          # Create project checkpoint
python -m ai_onboard checkpoint list            # List available checkpoints
python -m ai_onboard checkpoint restore         # Restore from checkpoint
```

## 🎓 User Experience & Learning

### User Experience

```bash
# UX analytics
python -m ai_onboard ux analytics user          # User behavior analytics
python -m ai_onboard ux analytics satisfaction  # Satisfaction tracking
python -m ai_onboard ux analytics errors        # Error pattern analysis
python -m ai_onboard ux feedback                # Provide feedback

# UX configuration
python -m ai_onboard ux config show             # Show UX settings
python -m ai_onboard ux config update           # Update UX preferences
python -m ai_onboard ux interventions list      # View UX interventions
```

### Help & Discovery

```bash
# Help system
python -m ai_onboard help                       # Context-aware help
python -m ai_onboard help <command>             # Command-specific help
python -m ai_onboard help --tutorial            # Interactive tutorials

# Feature discovery
python -m ai_onboard discover                   # Discover new features
python -m ai_onboard discover --category        # Explore by category
python -m ai_onboard suggest                    # Personalized suggestions
```

## 🔧 Configuration & Setup

### Configuration Management

```bash
# Basic configuration
python -m ai_onboard config show                # View current config
python -m ai_onboard config update              # Update settings
python -m ai_onboard config validate            # Validate configuration
python -m ai_onboard config reset               # Reset to defaults

# Advanced configuration
python -m ai_onboard config export              # Export configuration
python -m ai_onboard config import              # Import configuration
python -m ai_onboard config optimize            # Optimize settings
python -m ai_onboard config backup              # Backup configuration
```

### Integration Setup

```bash
# Tool integrations
python -m ai_onboard config integrations git    # Git integration
python -m ai_onboard config integrations jira   # Jira integration
python -m ai_onboard config integrations slack  # Slack integration

# API and webhooks
python -m ai_onboard config api                 # API configuration
python -m ai_onboard config webhooks            # Webhook setup
python -m ai_onboard config auth                # Authentication setup
```

## 🚨 Agent-Facing Commands

### State and Context

```bash
# AI agent context
python -m ai_onboard prompt state               # Get current state JSON
python -m ai_onboard prompt rules               # Get validation rules
python -m ai_onboard prompt summary             # Get project summary

# Alignment preview (dry run)
python -m ai_onboard align --preview            # Preview alignment check
python -m ai_onboard prompt propose             # Propose actions for approval
```

### Checkpoint Management

```bash
# Project checkpoints
python -m ai_onboard checkpoint create --scope "." --reason "pre-change"
python -m ai_onboard checkpoint list
python -m ai_onboard checkpoint restore --name "checkpoint-name"

# Scoped checkpoints
python -m ai_onboard checkpoint create --scope "src/**/*.py" --reason "refactor"
python -m ai_onboard checkpoint create --scope "tests/" --reason "test-updates"
```

## 💡 PowerShell Tips

### JSON Handling

```powershell
# Assign JSON to variable to avoid quoting issues
$diff = '{"files_changed":["a.py","b.py"],"lines_deleted":200,"has_tests":false,"subsystems":["core","ui"]}'
python -m ai_onboard prompt propose --diff $diff

# Multi-line JSON
$config = @"
{
  "features": {
    "prompt_bridge": true,
    "intent_checks": true,
    "checkpoints": true
  }
}
"@
python -m ai_onboard config import --format json --input $config
```

## ⚙️ Feature Flags & Configuration

### Feature Flags

Set in `.ai_onboard/config.json` (defaults are true):
```json
{
  "features": {
    "prompt_bridge": true,
    "intent_checks": true,
    "checkpoints": true,
    "ai_collaboration": true,
    "optimization": true,
    "ux_enhancements": true
  },
  "metaPolicies": {
    "MAX_DELETE_LINES": 200,
    "MAX_REFACTOR_FILES": 12,
    "REQUIRES_TEST_COVERAGE": true,
    "ALIGNMENT_THRESHOLD": 0.8
  }
}
```

### Environment Variables

```bash
# Set environment variables for configuration
export AI_ONBOARD_DEBUG=1
export AI_ONBOARD_CONFIG_PATH="/path/to/custom/config.json"
export AI_ONBOARD_LOG_LEVEL=DEBUG

# Run with custom configuration
python -m ai_onboard dashboard
```

---

## 🎯 Command Categories Summary

| Category | Primary Commands | Use Case |
|----------|------------------|----------|
| **Project** | `charter`, `plan`, `dashboard` | Project lifecycle management |
| **Optimization** | `kaizen`, `opt-experiments` | Continuous improvement |
| **AI Systems** | `ai-agent`, `cursor` | AI collaboration |
| **Development** | `debug`, `cleanup`, `checkpoint` | Development workflow |
| **UX** | `ux`, `help`, `suggest` | User experience |
| **Configuration** | `config`, `status`, `validate` | System management |

For complete documentation, see [Command Reference](commands/README.md) or [Getting Started Guide](getting-started.md).
