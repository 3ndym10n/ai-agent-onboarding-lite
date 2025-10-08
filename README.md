# AI Onboard - Agent Oversight & Guardrails

**Keep chaotic AI agents on track and aligned with your vision.**

AI Onboard is an oversight and guardrail system that gives vibe coders (non-technical users) control over AI coding agents, preventing chaos, bloat, and drift while maintaining systematic progress toward project goals.

## 🎯 The Problem

AI agents are brilliant but chaotic. They:

- 🌀 Go down rabbit holes and build unnecessary features
- 📦 Create bloat and technical debt
- 🎯 Lose sight of original project goals
- 🔄 Build endlessly without finishing
- 🚫 Make you lose control of your own project

**You end up micromanaging instead of building.**

## ✅ The Solution

AI Onboard provides **systematic oversight** - the middle ground between "no control" and "micromanagement":

- 📊 **Real-Time Monitoring** - See exactly what your AI agent is doing
- 🚦 **Mandatory Gates** - Agent must ask before major decisions
- 🛡️ **Chaos Prevention** - Detect and block off-track behavior
- 🎯 **Vision Alignment** - Keep agents focused on your goals
- ⏸️ **Emergency Controls** - Pause, stop, or redirect agents
- 📈 **Progress Tracking** - Systematic execution, not chaos

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai-agent-onboarding-lite

# Install dependencies
pip install -e .

# Or install in development mode
pip install -e ".[dev]"
```

### Monitor Your Agent

```bash
# Start monitoring dashboard
python -m ai_onboard monitor

# View current agent activity
python -m ai_onboard status

# Approve a pending gate
python -m ai_onboard approve <gate-id>

# Reject a gate decision
python -m ai_onboard reject <gate-id> --reason "Not aligned with vision"

# Check vision alignment
python -m ai_onboard align
```

## 🎮 Core Commands

### Oversight & Control

- `monitor` - Real-time dashboard of agent activity
- `status` - Quick status check of what agent is doing
- `approve` - Approve a pending gate decision
- `reject` - Reject a gate decision with reason
- `pause` - Pause agent without losing context
- `stop` - Emergency stop for runaway agents

### Vision & Planning

- `charter` - Define your project vision
- `plan` - Create systematic execution plan
- `align` - Check alignment with vision
- `dashboard` - Visual project overview

### Safety & Guardrails

- `validate` - Pre-flight validation of changes
- `cleanup` - Safe cleanup of agent-created bloat
- `gate` - Manage approval gates

## 📊 How It Works

### 1. Define Your Vision

```bash
python -m ai_onboard charter
```

Tell AI Onboard what you want to build. This becomes the north star that keeps agents aligned.

### 2. Monitor Agent Activity

```bash
python -m ai_onboard monitor
```

See in real-time:

- What agent is currently working on
- Pending decisions waiting for approval
- Actions the system blocked
- Progress toward your vision

### 3. Approve or Reject Decisions

When an agent wants to make a major decision, you get a gate:

```
🚦 GATE: Agent wants to add OAuth authentication
   Vision alignment: 40% (Off-track)
   Reason: Original vision was "simple todo app"
   
   [APPROVE] [REJECT] [MODIFY]
```

### 4. Stay in Control

- ✅ Agent stays aligned with your vision
- ✅ No bloat or technical debt
- ✅ Systematic progress, not chaos
- ✅ You have final say on all major decisions

## 🛡️ Safety Features

### Protected Paths

Critical files are automatically protected:

- `ai_onboard/` - The oversight system itself
- `.ai_onboard/` - Project data and history
- `.git/` - Version control
- Configuration files
- Documentation

### Mandatory Gates

Agents **must** get approval for:

- Creating new files/modules
- Refactoring existing code
- Adding dependencies
- Building features not in plan
- Any action that deviates from vision

### Chaos Detection

System automatically detects and blocks:

- Duplicate utilities
- Unnecessary refactoring
- Off-track features
- Technical debt creation
- Bloat and complexity

### Audit Trail

Complete log of:

- Every agent action
- Every gate decision
- Every blocked attempt
- Full project history

## 🎯 For Vibe Coders

**You don't need to be technical.** AI Onboard gives you simple controls:

### Dashboard View

```
┌─ AGENT OVERSIGHT DASHBOARD ───────────────────────────┐
│ 🤖 Agent: Cursor AI                                   │
│ 📊 Project: Todo App                                  │
│ 🎯 Vision: Simple todo app with auth                  │
│                                                        │
│ ✅ ALIGNED: 85% on track                              │
│                                                        │
│ 🔄 Currently: Building login form                     │
│    Progress: 47% complete (7/15 tasks)                │
│                                                        │
│ ⚠️  PENDING: 2 gates waiting for approval             │
│    1. Add password reset feature                      │
│    2. Implement OAuth providers                       │
│                                                        │
│ 🚫 BLOCKED: Agent tried to:                           │
│    • Add 15 new dependencies ← BLOCKED (bloat)        │
│    • Refactor 20 files ← BLOCKED (off-track)          │
│                                                        │
│ [APPROVE GATES] [VIEW DETAILS] [PAUSE AGENT]          │
└────────────────────────────────────────────────────────┘
```

### Simple Actions

- **Green** = Everything aligned, agent working well
- **Yellow** = Gate waiting, review and approve/reject
- **Red** = Agent blocked, check what was prevented

## 🤖 Works With Your Favorite AI Agents

- ✅ **Cursor AI** - Full integration
- ✅ **GitHub Copilot** - Compatible
- ✅ **Claude Code** - Supported
- ✅ **GPT-based agents** - Works seamlessly

## 📈 What You Get

### Before AI Onboard

- ❌ Agent builds 50 files you didn't ask for
- ❌ Lost track of original goal
- ❌ Massive technical debt
- ❌ Project never finishes
- ❌ You're exhausted from micromanaging

### After AI Onboard

- ✅ Agent stays focused on your vision
- ✅ Clear progress toward goals
- ✅ No bloat or technical debt
- ✅ Projects finish on vision
- ✅ Strategic oversight, not micromanagement

## 🏗️ Current Status

### ✅ Working Now

- Gate system (mandatory approvals)
- Decision enforcement
- Protected paths
- Vision tracking
- Progress monitoring
- Preference learning

### 🚧 In Development (MVP - 4 weeks)

- Real-time monitoring dashboard
- Pending gates UI
- Blocked actions log
- Quick approve/reject workflow

### 🔮 Coming Soon (9 weeks)

- Chaos detection system
- Vision drift alerting
- Emergency controls
- Cursor AI integration
- Full documentation

## 📁 Project Structure

```
ai-agent-onboarding-lite/
├── ai_onboard/           # Core oversight system
│   ├── cli/             # Command-line interface
│   ├── core/            # Gate system, enforcement, monitoring
│   │   ├── ai_integration/      # Agent integration
│   │   ├── legacy_cleanup/      # Gate system
│   │   └── project_management/  # Vision & planning
│   ├── policies/        # Safety rules and policies
│   └── schemas/         # Data schemas
├── .ai_onboard/         # Project data (auto-generated)
│   ├── charter.json     # Your project vision
│   ├── plan.json        # Systematic execution plan
│   ├── wbs.json         # Work breakdown structure
│   └── gates/           # Active gates
├── docs/                # Documentation
└── tests/               # Test suite
```

## 🔧 Development

### For Contributors

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy ai_onboard/

# Linting
flake8 ai_onboard/
```

### For AI Agent Developers

See `AGENTS.md` for:

- How to integrate your agent
- Gate system API
- Safety requirements
- Contribution guidelines

## 🎯 Roadmap

### Phase 1: Core Oversight MVP (Weeks 1-4)

- [x] Gate system
- [x] Protected paths
- [x] Vision tracking
- [ ] Real-time monitoring dashboard
- [ ] Gate approval UI

### Phase 2: Enforcement & Detection (Weeks 5-7)

- [ ] Mandatory gate enforcement
- [ ] Chaos detection
- [ ] Vision drift alerting
- [ ] Comprehensive logging

### Phase 3: Integration & Polish (Weeks 8-9)

- [ ] Emergency controls
- [ ] Cursor AI integration
- [ ] Documentation
- [ ] Early user launch

## 🤝 Contributing

We welcome contributions! Please:

1. Read `AGENTS.md` for guidelines
2. Check existing issues and PRs
3. Keep changes focused on oversight/control
4. Add tests for new features
5. Update documentation

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- 📚 Check `docs/` for detailed documentation
- 💬 Open an issue for bugs or features
- 🤖 See `AGENTS.md` for agent integration

---

## 💡 Philosophy

**AI agents should be powerful assistants, not chaotic wildcards.**

AI Onboard gives you the tools to harness agent power while maintaining control, ensuring your projects:

- Stay aligned with your vision
- Finish on time and on goal
- Avoid bloat and technical debt
- Give you strategic oversight, not micromanagement

**Because you should control your project, not fight to keep up with it.**

---

**AI Onboard** - Keep AI agents aligned, focused, and productive. 🎯
