# Core Commands Directives

Guidelines for executing the fundamental ai-onboard commands: `charter`, `plan`, `align`, and `validate`.

---

## 🎯 Charter Command

### When to Use

- Starting a new project
- Defining or updating project vision
- After completing vision interrogation

### Decision Tree

```
Does charter.json exist?
├─ NO → Suggest vision interrogation for comprehensive charter
│   └─ "I can create a charter in two ways:
│       1. Simple template (quick): python -m ai_onboard charter
│       2. Guided interrogation (thorough): python -m ai_onboard interrogate start
│       Which would you prefer?"
│
└─ YES → User wants to update
    └─ Use: python -m ai_onboard charter --interactive
```

### Commands

```bash
# Simple charter (quick start)
python -m ai_onboard charter

# Interactive charter (update existing)
python -m ai_onboard charter --interactive

# Intelligent charter (from interrogation - RECOMMENDED for new projects)
python -m ai_onboard interrogate start
# Then follow the interrogation workflow
```

### Best Practice

⭐ **For new projects with unclear vision**: Always suggest vision interrogation first
⭐ **For quick prototypes**: Simple charter is fine
⭐ **For production projects**: Vision interrogation creates better alignment

---

## 📋 Plan Command

### When to Use

- After charter is created or updated
- When project scope/objectives change
- To generate Work Breakdown Structure (WBS)

### Decision Tree

```
Is this an existing project with code?
├─ YES (has Python/JS/etc files) → Use --analyze-codebase
│   └─ "I see you have an existing codebase. 
│       I'll use --analyze-codebase to create a plan 
│       that matches your actual project structure."
│
└─ NO (new/empty project) → Use simple plan
    └─ "Creating a charter-based plan for your new project."
```

### How to Detect "Existing Project"

Check for:

- More than 10 source files (.py, .js, .ts, etc.)
- Existing package files (requirements.txt, package.json, pyproject.toml)
- Directory structure (src/, lib/, tests/)

### Commands

```bash
# Simple plan (charter-only)
python -m ai_onboard plan

# Intelligent plan (RECOMMENDED for existing projects)
python -m ai_onboard plan --analyze-codebase
```

### Intelligent Planning Benefits

When using `--analyze-codebase`, the system:

- ✅ Detects languages and frameworks
- ✅ Analyzes test coverage gaps
- ✅ Identifies architectural complexity
- ✅ Creates context-aware WBS
- ✅ Suggests relevant infrastructure tasks

### Example Flow

```
User: "Create a project plan"

Agent checks:
1. Charter exists? ✓
2. Codebase exists? ✓ (sees 50+ .py files)
3. Uses: python -m ai_onboard plan --analyze-codebase

Agent explains:
"I've analyzed your Python codebase and noticed:
- 3.9% test coverage → I've added testing infrastructure to the plan
- Multi-module architecture → I've included architecture planning tasks
- Django framework detected → I've added Django-specific setup tasks"
```

---

## ✅ Align Command

### When to Use

- Before making significant changes
- When vision/requirements have drifted
- Periodic alignment checks (weekly/milestone-based)

### Commands

```bash
# Create alignment checkpoint
python -m ai_onboard align

# Review existing checkpoint
python -m ai_onboard align --review
```

### Best Practice

⭐ Create checkpoints BEFORE major refactors
⭐ Use alignment to prevent scope creep
⭐ Reference alignment when making architectural decisions

---

## 🔍 Validate Command

### When to Use

- After completing implementation
- Before merging to main
- During code reviews
- When system behavior seems off

### Commands

```bash
# Run full validation
python -m ai_onboard validate

# Validation with custom report
python -m ai_onboard validate --report alignment_report.json
```

### What It Checks

- Vision alignment
- Charter compliance
- Policy adherence
- Anti-drift measures
- System health

---

## 🔄 Typical Workflow

### New Project

```
1. python -m ai_onboard interrogate start    # Intelligent charter
2. python -m ai_onboard plan                  # Generate initial plan
3. python -m ai_onboard align                 # Create baseline checkpoint
```

### Existing Project

```
1. python -m ai_onboard charter --interactive # Update/create charter
2. python -m ai_onboard plan --analyze-codebase # Intelligent planning
3. python -m ai_onboard validate              # Check current state
```

### Major Change

```
1. python -m ai_onboard align                 # Checkpoint before change
2. [Make changes]
3. python -m ai_onboard validate              # Verify alignment
4. python -m ai_onboard plan --analyze-codebase # Update plan if needed
```

---

## 💡 Agent Tips

### Always Suggest the Intelligent Path

❌ **Bad**: "Running plan command..." → Silently uses simple mode
✅ **Good**: "I'll use --analyze-codebase since you have an existing Python project"

### Explain Your Choices

❌ **Bad**: *Just runs command*
✅ **Good**: "I'm using vision interrogation because it creates more comprehensive charters for production projects"

### Detect Opportunities

When you see:

- Low test coverage → Suggest test infrastructure in plan
- Missing charter → Suggest vision interrogation
- Outdated plan → Suggest re-planning with codebase analysis
- Scope drift → Suggest alignment check

---

## 🚨 Common Mistakes to Avoid

1. **Using simple plan for existing projects**
   - Always check if codebase exists first

2. **Skipping vision interrogation for new production projects**
   - Simple charter is for prototypes, not production

3. **Not explaining why you chose a specific command**
   - Users should understand your reasoning

4. **Forgetting to validate after major changes**
   - Always suggest validation after significant work

---

## 📚 Related Directives

- See `planning_workflow.md` for detailed planning guidance
- See `vision_interrogation.md` for interrogation best practices
- See `gate_system.md` for handling system gates











