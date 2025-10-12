# AI Onboard - User Guide for Vibe Coders

## 🎯 The Problem You're Solving

**AI agents are brilliant but chaotic.** They go down rabbit holes, create technical debt, lose focus on your vision, and build endlessly without finishing. You need systematic oversight without micromanagement.

**AI Onboard provides the control you need** to transform chaotic AI behavior into systematic, aligned development.

## 🚀 Quick Start

### 1. Install and Initialize

```bash
pip install ai-onboard
ai_onboard init
```

### 2. Set Your Project Vision

```bash
ai_onboard charter create "Build a task management app"
ai_onboard plan create "MVP in 4 weeks"
ai_onboard wbs create
```

### 3. Monitor Agent Activity

```bash
ai_onboard dashboard
```

That's it! The system now monitors your agents and provides oversight.

## 📊 The Dashboard - Your Control Center

```
┌─ AGENT OVERSIGHT DASHBOARD ───────────────────────────┐
│ ✅ Integration: 100%    Systems Active: 7  │
│ 🤖 Agent: Cursor AI                                   │
│ 📊 Project: AI Onboard - Agent Oversight             │
│ 🎯 Vision: Systematic oversight & guardrails          │
│                                                        │
│ 💤 Status: No active agent session                     │
│                                                        │
│ ✅ No pending gates                                    │
│                                                        │
│ 🚫 BLOCKED: 3 actions prevented      │
│    🚨 Delete 15 test files                │
│        2min ago, Exceeded file deletion li... │
│    🔴 Add 20 new dependencies             │
│        5min ago, Bloat prevention - too ma... │
│    🟡 Refactor 10 core files              │
│        8min ago, Off-track from project vi... │
│                                                        │
│ ✅ No chaos detected                                   │
│                                                        │
│ ✅ No vision drift alerts                             │
│                                                        │
│ 🚨 Alignment: 0.0% on vision      │
│                                                        │
│ 📊 Progress: [██████████░░░░░░░░░░] 53% │
│    Phase: Core Oversight MVP                       │
│    Next: Implement 'monitor' comma                     │
│    ETA: 9 hours                                       │
│                                                        │
│ ✅ Emergency: All agents normal                       │
│                                                        │
│ [PAUSE AGENT] │ [STOP AGENT] │ [EMERGENCY BLOCK] │
└────────────────────────────────────────────────────────┘
```

### Dashboard Sections Explained

**🔄 Current Activity**

- Shows what your AI agent is currently working on
- Displays progress and vision alignment

**🚫 Blocked Actions**

- Lists operations the system prevented
- Helps you understand what the agent tried to do

**📊 Progress Tracking**

- Real-time progress based on your WBS
- Current phase and next tasks
- ETA calculations

**🚨 Emergency Controls**

- **PAUSE AGENT**: Temporarily stop agent for review
- **STOP AGENT**: Completely halt agent operations
- **EMERGENCY BLOCK**: Block specific dangerous operations

## 🛡️ How the System Protects You

### Mandatory Gates (Hard Blocks)

The system **automatically blocks** dangerous operations:

```bash
# ❌ This gets blocked automatically
python -m ai_onboard integrator process cursor_ai "delete_everything" --context '{"reason": "cleanup"}'

# Result: BLOCKED - requires approval
# 🚫 Operation Blocked by Oversight System
# Operation: delete_everything
# Blocked because: Protected files - requires approval
```

### Chaos Detection

The system detects when agents go off-track:

```bash
# Agent starts creating 50 files rapidly
# 🚨 CHAOS: File creation chaos detected
# Agent creating files too rapidly - possible runaway behavior
```

### Vision Drift Alerting

Keeps agents aligned with your project vision:

```bash
# Agent tries to implement unrelated feature
# 🎯 Vision Drift: Agent deviating from project vision
# Operation 'implement_unrelated_feature' is 85% off-track from project goals
```

## 🔧 Common Commands

### Project Management

```bash
# Set project vision
ai_onboard charter create "Build amazing product"

# Create project plan
ai_onboard plan create "MVP in 6 weeks"

# Create work breakdown
ai_onboard wbs create

# Update progress
ai_onboard wbs update "1.1.1" --status completed
```

### Agent Control

```bash
# Check current status
ai_onboard dashboard

# Pause problematic agent
ai_onboard emergency pause "problematic_agent" "Going off-track"

# Resume after review
ai_onboard emergency resume "problematic_agent"

# Block specific operation
ai_onboard emergency block "agent_name" "dangerous_operation" "Too risky"
```

### System Management

```bash
# Check system health
ai_onboard limits status

# View blocked operations
ai_onboard blocks list

# Override a block (use carefully!)
ai_onboard blocks approve "block_id"
```

## 📋 Real-World Examples

### Example 1: Agent Goes Rogue

**Scenario**: Your AI agent starts creating hundreds of files and dependencies.

**What happens**:

1. **Hard Limits** block excessive file creation
2. **Chaos Detection** identifies rapid file creation pattern
3. **Emergency Controls** pause the agent automatically
4. **Dashboard** shows what happened and why

**Your response**:

```bash
# Review what happened
ai_onboard dashboard

# See the chaos event
ai_onboard chaos status

# Decide what to do
ai_onboard emergency resume "agent_name"  # Or keep paused
```

### Example 2: Agent Loses Focus

**Scenario**: Agent starts implementing features not in your project scope.

**What happens**:

1. **Vision Drift Detection** identifies off-track work
2. **Gate System** requires approval for major changes
3. **Dashboard** shows alignment percentage

**Your response**:

```bash
# Check vision alignment
ai_onboard vision status

# Review pending gates
ai_onboard gates list

# Approve or redirect work
ai_onboard gates approve "gate_id"  # or reject
```

### Example 3: Emergency Situation

**Scenario**: Agent starts deleting important files or making breaking changes.

**What happens**:

1. **Emergency Controls** detect dangerous patterns
2. **System** automatically pauses agent
3. **Dashboard** shows emergency status

**Your response**:

```bash
# Immediate response
ai_onboard dashboard  # See what's happening

# Take control
ai_onboard emergency stop "dangerous_agent" "Critical files at risk"

# Investigate
ai_onboard blocks list  # See what was blocked

# Resume when safe
ai_onboard emergency resume "agent_name"
```

## 🎛️ Configuration

### Project Setup

```bash
# Initialize project
ai_onboard init

# Set preferences
ai_onboard preferences set "root_directory_cleanliness" "always_observed"

# Configure limits
ai_onboard limits config --max-files-per-hour 50
```

### Agent Integration

```bash
# Add to your .cursorrules
# MANDATORY OVERSIGHT CHECKS (HARD LIMITS)
# Before executing ANY of the following operations, you MUST check with the oversight system first:
#
# python -m ai_onboard integrator process cursor_ai "<operation_name>" --context '{"description": "what you plan to do"}'
```

## 🚨 When Things Go Wrong

### Dashboard Shows Problems

1. **Check System Health**: `ai_onboard limits status`
2. **Review Recent Activity**: `ai_onboard dashboard`
3. **Check for Chaos Events**: `ai_onboard chaos status`

### Agent Won't Respond

1. **Check Emergency Status**: `ai_onboard emergency status`
2. **Resume if Paused**: `ai_onboard emergency resume "agent_name"`
3. **Check System Integration**: `ai_onboard integrator status`

### Performance Issues

1. **Monitor Resource Usage**: `ai_onboard limits status`
2. **Check Background Tasks**: `ai_onboard dashboard`
3. **Review Operation History**: Look for patterns

## 📈 Best Practices

### For Daily Use

1. **Check dashboard** at least once per development session
2. **Review blocked actions** to understand agent behavior
3. **Monitor progress** against your WBS
4. **Address chaos alerts** promptly

### For Project Management

1. **Keep WBS updated** with completed work
2. **Set realistic limits** based on your project scale
3. **Review vision alignment** regularly
4. **Use emergency controls** proactively, not reactively

### For Agent Integration

1. **Follow the mandatory checks** in `.cursorrules`
2. **Provide clear context** for operations
3. **Respond to gates** promptly
4. **Monitor agent behavior** patterns

## 🆘 Getting Help

### Common Issues

- **Dashboard not updating**: Check system integration status
- **Operations always blocked**: Review your limits configuration
- **Performance slow**: Check resource monitoring

### Support Commands

```bash
# System status
ai_onboard status

# Help with any command
ai_onboard help <command>

# System diagnostics
ai_onboard diagnose
```

## 🎉 Success Metrics

When AI Onboard is working well, you should see:

- ✅ **Dashboard shows real activity** (not "no active session")
- ✅ **Progress bar reflects actual work** (not 0%)
- ✅ **Blocked actions are legitimate** (agent trying dangerous operations)
- ✅ **Vision alignment stays high** (agent focused on your goals)
- ✅ **Emergency controls rarely needed** (agent behaves well)

---

**AI Onboard transforms chaotic AI development into systematic, controlled progress.** Use the dashboard, respond to alerts, and maintain oversight - that's all you need for successful AI-driven development! 🚀





