# AI Onboard - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install
```bash
pip install ai-onboard
```

### Step 2: Initialize Your Project
```bash
cd your-project
ai_onboard init
```

### Step 3: Set Your Project Vision
```bash
# Create project charter (what you're building)
ai_onboard charter create "Build a task management app for teams"

# Create project plan (timeline and phases)
ai_onboard plan create "MVP in 4 weeks with weekly milestones"

# Create work breakdown (specific tasks)
ai_onboard wbs create
```

### Step 4: See Your Dashboard
```bash
ai_onboard dashboard
```

### Step 5: Run Quick Quality Checks
```bash
python scripts/run_checks.py
```
Runs unit tests, type checks, and dependency scans using whatever tooling is
available in your environment (skips steps when tools are missing).

## 🎯 What You Get

**Real-time oversight** of your AI agents:

```
┌─ AGENT OVERSIGHT DASHBOARD ───────────────────────────┐
│ ✅ Integration: 100%    Systems Active: 7  │
│ 🤖 Agent: Cursor AI                                   │
│ 📊 Project: Your Project Name                         │
│ 🎯 Vision: Your project vision                        │
│                                                        │
│ 🔄 Currently: Agent working on feature                 │
│    Progress: 65% complete                             │
│    Alignment: 92% on track                           │
│                                                        │
│ ✅ No pending gates                                    │
│                                                        │
│ 🚫 BLOCKED: 1 action prevented                        │
│    🟡 Add 15 dependencies                             │
│        3min ago, Bloat prevention                     │
│                                                        │
│ 📊 Progress: [██████░░░░░░░░░░░░░░] 45%                │
│    Phase: Core Features                               │
│    Next: User authentication                          │
│    ETA: 12 days                                       │
│                                                        │
│ ✅ Emergency: All agents normal                       │
│                                                        │
│ [PAUSE AGENT] │ [STOP AGENT] │ [EMERGENCY BLOCK] │
└────────────────────────────────────────────────────────┘
```

## 🛡️ How It Protects You

### Automatic Protection
- **Blocks dangerous operations** (deleting files, adding too many dependencies)
- **Detects chaos patterns** (agent creating files too rapidly)
- **Alerts on vision drift** (agent working on unrelated features)
- **Provides emergency controls** (pause/stop agents when needed)

### Daily Workflow
1. **Check dashboard** - See what your agent is doing
2. **Review blocked actions** - Understand what the agent tried
3. **Monitor progress** - Track against your project plan
4. **Respond to alerts** - Approve gates or redirect work

## 🔧 Key Commands

### Project Setup
```bash
ai_onboard charter create "Your project description"
ai_onboard plan create "Timeline and milestones"
ai_onboard wbs create
```

### Daily Monitoring
```bash
ai_onboard dashboard        # See current status
ai_onboard gates list       # Review pending approvals
ai_onboard chaos status     # Check for chaos events
ai_onboard vision status    # Monitor alignment
```

### Agent Control
```bash
ai_onboard emergency pause "agent_name" "Going off-track"
ai_onboard gates approve "gate_id"
ai_onboard blocks list
```

## 📋 Example Scenarios

### Scenario 1: Agent Creates Too Many Files
```
🚨 CHAOS: File creation chaos detected
Agent creating files too rapidly - possible runaway behavior

Your response:
ai_onboard emergency pause "agent_name" "Review file creation pattern"
```

### Scenario 2: Agent Adds Too Many Dependencies
```
🚫 BLOCKED: Add 25 dependencies
Bloat prevention - too many packages for single feature

Your response:
ai_onboard blocks approve "block_id"  # Or reject if inappropriate
```

### Scenario 3: Agent Works on Wrong Feature
```
🎯 Vision Drift: Agent deviating from project vision
Operation 'implement_chat_feature' is 78% off-track

Your response:
ai_onboard gates reject "gate_id"  # Redirect to correct work
```

## 🎉 You're Ready!

**AI Onboard now provides systematic oversight** of your AI development:

- ✅ **Real-time monitoring** of agent activity
- ✅ **Automatic protection** from dangerous operations
- ✅ **Progress tracking** against your project plan
- ✅ **Emergency controls** when needed
- ✅ **Vision alignment** monitoring

**Next Steps:**
1. Run `ai_onboard dashboard` to see your current status
2. Respond to any pending gates or alerts
3. Monitor progress as your agent works
4. Use emergency controls if the agent goes off-track

**That's all you need!** AI Onboard handles the complexity while you maintain control and visibility. 🚀



