# AI Onboard - Practical Examples

## 🎯 Real-World Scenarios

### Example 1: Agent Goes on File Creation Spree

**Scenario**: Your AI agent starts creating hundreds of test files, cluttering your project.

**What happens**:
```
🔧 Initializing integrated oversight systems...
🛡️ Hard Limits Enforcer started
🚨 CHAOS: File creation chaos detected
Agent creating files too rapidly - possible runaway behavior
```

**Dashboard shows**:
```
┌─ AGENT OVERSIGHT DASHBOARD ───────────────────────────┐
│ 🚨 CHAOS: 1 active chaos event                        │
│    🟡 File creation chaos                             │
│       Agent creating 50+ files in 2 minutes           │
│                                                        │
│ 🚫 BLOCKED: 12 actions prevented                      │
│    🚨 Create 25 test files                            │
│        1min ago, Exceeded file creation limit         │
│    🟡 Create 30 more test files                       │
│        30sec ago, Chaos prevention                    │
│                                                        │
│ 📊 Progress: [████░░░░░░░░░░░░░░░░] 25%                │
│                                                        │
│ 🚨 Emergency: Agent paused automatically              │
│                                                        │
│ [RESUME AGENT] │ [STOP AGENT] │ [EMERGENCY BLOCK]    │
└────────────────────────────────────────────────────────┘
```

**Your response**:
```bash
# Review the situation
ai_onboard dashboard

# Check chaos details
ai_onboard chaos status

# Decide what to do
ai_onboard emergency resume "agent_name"  # Resume with limits
# OR
ai_onboard emergency stop "agent_name"    # Stop if too problematic
```

### Example 2: Agent Adds Too Many Dependencies

**Scenario**: Agent tries to add 20+ packages for a simple feature.

**What happens**:
```
🚫 BLOCKED: Add 25 dependencies
Bloat prevention - too many packages for single feature
```

**Dashboard shows**:
```
┌─ AGENT OVERSIGHT DASHBOARD ───────────────────────────┐
│ 🚫 BLOCKED: 1 action prevented                        │
│    🔴 Add 25 dependencies                             │
│        2min ago, Bloat prevention - too many packages │
│                                                        │
│ 📊 Progress: [██████░░░░░░░░░░░░░░] 35%                │
│                                                        │
│ 🎯 Vision Alignment: 88% on track                     │
└────────────────────────────────────────────────────────┘
```

**Your response**:
```bash
# Review blocked operation
ai_onboard blocks list

# Check if this is legitimate
ai_onboard blocks status "block_id"

# Approve if needed
ai_onboard blocks approve "block_id"

# Or reject and redirect
ai_onboard blocks reject "block_id"
```

### Example 3: Agent Works on Wrong Feature

**Scenario**: Agent starts implementing a chat feature when you need user authentication.

**What happens**:
```
🎯 Vision Drift: Agent deviating from project vision
Operation 'implement_chat_feature' is 78% off-track from project goals
```

**Dashboard shows**:
```
┌─ AGENT OVERSIGHT DASHBOARD ───────────────────────────┐
│ 🎯 Vision Drift: 1 active alert                        │
│    🟡 Chat feature implementation                     │
│       78% off-track from project vision               │
│                                                        │
│ ✅ No pending gates                                    │
│                                                        │
│ 🚨 Alignment: 78% on vision                           │
│                                                        │
│ 📊 Progress: [█████░░░░░░░░░░░░░░░] 28%                │
└────────────────────────────────────────────────────────┘
```

**Your response**:
```bash
# Check vision status
ai_onboard vision status

# Review current gates
ai_onboard gates list

# Redirect agent to correct work
ai_onboard gates reject "current_gate"
ai_onboard gates create "implement_user_authentication"
```

### Example 4: Emergency Situation

**Scenario**: Agent starts deleting important files or making breaking changes.

**What happens**:
```
🚨 EMERGENCY: Agent paused automatically
Critical file operations detected - review required
```

**Dashboard shows**:
```
┌─ AGENT OVERSIGHT DASHBOARD ───────────────────────────┐
│ 🚨 EMERGENCY: 1 agent in emergency                    │
│    ⏸️ Agent paused: Critical file operations          │
│                                                        │
│ 🚫 BLOCKED: 3 actions prevented                       │
│    🚨 Delete core files                               │
│        1min ago, Critical files - manual review       │
│    🔴 Modify shared components                        │
│        45sec ago, Breaking changes detected           │
│                                                        │
│ 📊 Progress: [██░░░░░░░░░░░░░░░░░░] 15%                │
│                                                        │
│ 🚨 Emergency: Agent paused automatically              │
│                                                        │
│ [RESUME AGENT] │ [STOP AGENT] │ [EMERGENCY BLOCK]    │
└────────────────────────────────────────────────────────┘
```

**Your response**:
```bash
# Immediate assessment
ai_onboard dashboard

# Review blocked operations
ai_onboard blocks list

# Take appropriate action
ai_onboard emergency stop "dangerous_agent" "Critical files at risk"
# OR
ai_onboard emergency resume "agent_name"  # If situation is understood
```

## 🔧 Integration Examples

### Cursor AI Integration

**Add to your `.cursorrules`**:
```markdown
# MANDATORY OVERSIGHT CHECKS (HARD LIMITS)
# Before executing ANY of the following operations, you MUST check with the oversight system first:

# python -m ai_onboard integrator process cursor_ai "<operation_name>" --context '{"description": "what you plan to do"}'

# Examples:
# python -m ai_onboard integrator process cursor_ai "create_files" --context '{"count": 10, "purpose": "new feature"}'
# python -m ai_onboard integrator process cursor_ai "add_dependency" --context '{"package": "requests", "reason": "HTTP client needed"}'
```

### Workflow Integration

**Daily development workflow**:
```bash
# 1. Check current status
ai_onboard dashboard

# 2. Review any pending approvals
ai_onboard gates list

# 3. Respond to alerts
ai_onboard chaos status
ai_onboard vision status

# 4. Update progress
ai_onboard wbs update "current_task_id" --status in_progress

# 5. Monitor agent work
ai_onboard dashboard  # Check periodically
```

### Project Management Integration

**Weekly project review**:
```bash
# 1. Check overall progress
ai_onboard dashboard

# 2. Review completed work
ai_onboard wbs list --status completed

# 3. Plan next week
ai_onboard wbs list --status pending

# 4. Update project plan if needed
ai_onboard plan update "phase_1" --status completed
```

## 📊 Monitoring Examples

### Progress Tracking
```bash
# View current progress
ai_onboard dashboard

# Detailed progress breakdown
ai_onboard wbs status

# Update task status
ai_onboard wbs update "1.1.1" --status completed
```

### Agent Activity Monitoring
```bash
# See what agent is doing now
ai_onboard dashboard

# Historical activity
ai_onboard activity history --hours 24

# Agent performance metrics
ai_onboard metrics agent "agent_name"
```

### System Health Monitoring
```bash
# Overall system status
ai_onboard limits status

# Emergency controls status
ai_onboard emergency status

# Integration health
ai_onboard integrator status
```

## 🚨 Troubleshooting Examples

### Dashboard Not Updating
```bash
# Check system integration
ai_onboard integrator status

# Restart if needed
ai_onboard integrator restart

# Check agent activity
ai_onboard activity status
```

### Operations Always Blocked
```bash
# Review current limits
ai_onboard limits status

# Check if limits are too restrictive
ai_onboard limits config --max-files-per-hour 100

# Review recent blocks
ai_onboard blocks list --recent
```

### Performance Issues
```bash
# Monitor resource usage
ai_onboard limits status

# Check for chaos events
ai_onboard chaos status

# Review background tasks
ai_onboard dashboard
```

## 🎉 Success Examples

### Good Dashboard State
```
┌─ AGENT OVERSIGHT DASHBOARD ───────────────────────────┐
│ ✅ Integration: 100%    Systems Active: 7  │
│ 🤖 Agent: Cursor AI                                   │
│ 📊 Project: Task Management App                       │
│ 🎯 Vision: Build MVP in 4 weeks                       │
│                                                        │
│ 🔄 Currently: Implementing user authentication         │
│    Progress: 75% complete                             │
│    Alignment: 95% on track                           │
│                                                        │
│ ✅ No pending gates                                    │
│                                                        │
│ 🚫 BLOCKED: 0 actions prevented                       │
│                                                        │
│ ✅ No chaos detected                                   │
│                                                        │
│ ✅ No vision drift alerts                             │
│                                                        │
│ 🚨 Alignment: 95% on vision                           │
│                                                        │
│ 📊 Progress: [██████████████░░░░░░] 75%                │
│    Phase: Core Features                               │
│    Next: Testing and deployment                       │
│    ETA: 5 days                                        │
│                                                        │
│ ✅ Emergency: All agents normal                       │
│                                                        │
│ [PAUSE AGENT] │ [STOP AGENT] │ [EMERGENCY BLOCK] │
└────────────────────────────────────────────────────────┘
```

**This shows**: Healthy agent behavior, good progress, no issues requiring attention.

### Problem Dashboard State
```
┌─ AGENT OVERSIGHT DASHBOARD ───────────────────────────┐
│ 🚨 CHAOS: 3 active chaos events                       │
│ 🚫 BLOCKED: 15 actions prevented                      │
│ 🎯 Vision Drift: 2 active alerts                       │
│                                                        │
│ 🚨 Emergency: 2 agents in emergency                   │
│                                                        │
│ 📊 Progress: [██░░░░░░░░░░░░░░░░░░] 10%                │
│                                                        │
│ [RESUME AGENTS] │ [STOP AGENTS] │ [EMERGENCY BLOCK]   │
└────────────────────────────────────────────────────────┘
```

**This shows**: Major problems requiring immediate attention - agents are out of control.

## 🔄 Integration Patterns

### Development Workflow Integration
```bash
# Before starting work
ai_onboard dashboard

# During development
ai_onboard gates respond  # Respond to any gates

# After completing work
ai_onboard wbs update "current_task" --status completed

# End of day
ai_onboard dashboard  # Final status check
```

### CI/CD Integration
```bash
# In your CI pipeline
ai_onboard validate --report  # Check system health

# Before deployment
ai_onboard gates approve-all  # Approve any pending gates

# After deployment
ai_onboard wbs update "deployment_task" --status completed
```

### Team Collaboration
```bash
# Project manager checks
ai_onboard dashboard
ai_onboard wbs status

# Developer responds to gates
ai_onboard gates list
ai_onboard gates respond "gate_id"

# Tech lead monitors alignment
ai_onboard vision status
ai_onboard chaos status
```

---

**These examples show how AI Onboard transforms chaotic AI development into systematic, controlled progress.** Use them as patterns for integrating oversight into your development workflow! 🚀






