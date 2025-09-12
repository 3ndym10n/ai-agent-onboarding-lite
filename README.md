# AI Onboard - AI Agent Alignment Tool

**AI Onboard** is a drop-in tool that helps developers create real working projects more efficiently by providing AI agent alignment, vision tracking, and continuous improvement capabilities.

## 🎯 What It Does

AI Onboard prevents AI agent drift and maintains alignment with your vision through:

- **Vision Alignment**: Keeps AI agents focused on your project goals
- **Smart Validation**: Pre-flight checks before making changes
- **Continuous Improvement**: Self-correcting system that gets better over time
- **Safe Operations**: Protected paths and rollback capabilities
- **Agent Collaboration**: Structured workflow for AI agents working together

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

### Essential Commands

```bash
# Core workflow commands
python -m ai_onboard analyze      # Analyze current project state
python -m ai_onboard charter      # Create or update project charter
python -m ai_onboard plan         # Generate development roadmap
python -m ai_onboard align        # Check alignment with project vision
python -m ai_onboard validate     # Pre-flight validation of changes
python -m ai_onboard kaizen       # Continuous improvement cycle
python -m ai_onboard metrics      # View project metrics and progress

# Safe cleanup
python -m ai_onboard cleanup --dry-run  # See what would be cleaned

# Agent-facing commands (feature-flagged)
python -m ai_onboard prompt state|rules|summary|propose
python -m ai_onboard checkpoint create|list|restore
```

## 📋 Core Commands

### Project Management
- `analyze` - Analyze current project state
- `charter` - Create or update project charter
- `plan` - Generate development roadmap
- `align` - Check alignment with project vision
- `dashboard` - Visual project status overview

### Development Workflow
- `validate` - Pre-flight validation of changes
- `kaizen` - Continuous improvement cycle
- `metrics` - View project metrics and progress
- `cleanup` - Safe cleanup of non-critical files

### AI Agent Features
- `prompt` - Get state, rules, and summaries for AI agents
- `checkpoint` - Create and manage project checkpoints
- `ai-agent` - AI agent collaboration tools
- `enhanced-vision` - Advanced vision interrogation
- `cursor` - Cursor AI integration commands

## 🤖 AI Agent Integration

AI Onboard is designed to work seamlessly with AI coding agents like Cursor, providing shared context, safety rails, and structured improvement loops.

### Prompt Bridge
```bash
# Get current project state for AI agents
python -m ai_onboard prompt state

# Check rules for a specific path
python -m ai_onboard prompt rules --path src/

# Propose an action and get decision
python -m ai_onboard prompt propose --diff '{"files_changed":["a.py","b.py"]}'

# Get project summary
python -m ai_onboard prompt summary
```

### Checkpoints
```bash
# Create a checkpoint before major changes
python -m ai_onboard checkpoint create --scope "src/**/*.py" --reason "pre-refactor"

# List available checkpoints
python -m ai_onboard checkpoint list

# Restore from checkpoint
python -m ai_onboard checkpoint restore <checkpoint-id>
```

### Natural Language Mode

For Cursor/LLM agents, use the prompt-first workflow with no CLI required:

**Key Components:**
- `ai_onboard/core/cursor_rules.py` - System prompt + logging helpers
- `.ai_onboard/agent_profile.json` - Focus include/exclude for the agent
- Logs: `.ai_onboard/conversation.jsonl`, `.ai_onboard/decisions.jsonl`, `.ai_onboard/obs/*.md`

**Quick Start:**
```bash
# 1. Print system prompt for your agent
python examples/cursor_prompt_loop.py --print-prompt

# 2. Log observations and decisions
python examples/cursor_prompt_loop.py --observe "Found README with goals A/B" --rule readme
python examples/cursor_prompt_loop.py --decide allow --why "docs sufficient to proceed"

# 3. Check status/checklist
python examples/cursor_prompt_loop.py --status
```

**Agent Profile (Optional):**
- Edit `.ai_onboard/agent_profile.json` to constrain what the agent reads
- The system prompt embeds Include/Exclude lists to reduce distraction

**Safety:**
- The NL system only writes under `.ai_onboard/`
- Use `AGENTS.md` for repo rules/guardrails

## 🛡️ Safety Features

### Protected Paths
The system automatically protects critical files and directories:
- `ai_onboard/` - The system itself
- `.ai_onboard/` - Project data
- `.git/` - Version control
- Configuration files (`pyproject.toml`, `requirements.txt`)
- Documentation (`README*`, `AGENTS.md`)
- CI/CD files (`.github/`)

### Safe Cleanup
```bash
# See what would be deleted (safe)
python -m ai_onboard cleanup --dry-run

# Actually clean up (with confirmation)
python -m ai_onboard cleanup

# Force cleanup without confirmation
python -m ai_onboard cleanup --force

# Create backup before cleanup
python -m ai_onboard cleanup --backup
```

## 📊 Alignment System

### Preview Changes
Use the intelligent alignment preview to assess confidence before executing:

```bash
python -m ai_onboard align --preview
# -> prints JSON and writes .ai_onboard/alignment_report.json
```

This generates a report with:
- `confidence` (0-1 scale)
- `decision` (proceed|quick_confirm|clarify)
- Component scores
- Detected ambiguities

Thresholds are configured in `ai_onboard/policies/alignment_rules.yaml`.

### Configuration
Set feature flags in `ai_onboard.json`:
```json
{
  "features": {
    "prompt_bridge": true,
    "intent_checks": true,
    "checkpoints": true
  },
  "metaPolicies": {
    "MAX_DELETE_LINES": 200,
    "MAX_REFACTOR_FILES": 12,
    "REQUIRES_TEST_COVERAGE": true
  }
}
```

## 📁 Project Structure

```
ai-agent-onboarding-lite/
├── ai_onboard/           # Core system
│   ├── cli/             # Command-line interface
│   ├── core/            # Core functionality
│   ├── plugins/         # Extensible plugins
│   ├── policies/        # Configuration policies
│   └── schemas/         # Data schemas
├── .ai_onboard/         # Project data (auto-generated)
├── docs/                # Documentation
├── examples/            # Usage examples
├── scripts/             # Utility scripts
└── tests/               # Test suite
```

## 🔧 Development

### Setup Development Environment
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black ai_onboard/
isort ai_onboard/

# Type checking
mypy ai_onboard/

# Linting
flake8 ai_onboard/
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_onboard

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Only integration tests
```

## 🚀 AI Agent Capabilities

This project acts as a meta-tool for AI coding agents (Cursor, Codex, GPTs, etc.) by providing:

**Where it fits well:**
- **Memory**: `ai_onboard.json` + JSONL telemetry gives agents persistent state across runs
- **Safety**: Protected paths + safe cleanup reduce destructive actions
- **Guardrails**: Policy engine + validation runtime enforce pre-flight sanity checks
- **Kaizen**: Plan/Do/Check/Act loop scaffolds self-correction instead of blind retries

**Advanced Features:**
- **Intent checks**: Meta-policy for "should the agent do this task now?"
- **Prompt feedback**: Feed telemetry/state back into agent prompts, not just logs
- **Nonlinear work**: Lightweight checkpoints/rollback and branch comparison for approaches
- **Cross-model context**: Shared memory usable by different models/context windows

**PowerShell Tip:**
```powershell
# Assign JSON to variable to avoid quoting issues
$diff = '{"files_changed":["a.py","b.py"],"lines_deleted":200,"has_tests":false,"subsystems":["core","ui"]}'
python -m ai_onboard prompt propose --diff $diff
```

## 📈 Roadmap

### Current Version (v0.2.0)
- ✅ Prompt bridge for AI agents
- ✅ Intent checks and meta-policy thresholds
- ✅ Checkpoint system
- ✅ Cross-agent telemetry
- ✅ Model-aware summarization

### Upcoming Features
- Enhanced vision interrogation system
- Advanced AI agent collaboration protocols
- Continuous improvement analytics
- UI/UX enhancements
- Background agent integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

See `AGENTS.md` for guidance on AI agent contributions.

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- Check the documentation in `docs/`
- Review examples in `examples/`
- Open an issue for bugs or feature requests
- See `AGENTS.md` for AI agent integration guidance

---

**AI Onboard** - Making AI agents work better, together. 🚀