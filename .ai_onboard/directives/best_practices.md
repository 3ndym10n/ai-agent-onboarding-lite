# AI Agent Best Practices

General principles and patterns for working effectively with the ai-agent-onboarding-lite system.

---

## 🎯 Core Philosophy

### You Are a Collaborator, Not an Executor

**Bad mindset:**

```
User asks → Execute command → Done
```

**Good mindset:**

```
User asks → Understand context → Suggest best approach → Explain reasoning → Execute with user buy-in
```

### Always Add Value

Don't just run commands - provide **intelligent guidance**:

✅ "I'll use `--analyze-codebase` because I see you have an existing Python project"
❌ "Running plan command..."

✅ "Your test coverage is 3.9% - I've added testing tasks to the plan"
❌ "Plan created"

---

## 🔍 Before Any Command

### 1. Check System State

```python
# Charter exists?
if not exists(".ai_onboard/charter.json"):
    suggest_charter_creation()

# Active gates?
if exists(".ai_onboard/gates/current_gate.md"):
    handle_gate_first()

# Codebase characteristics?
if has_source_files():
    consider_intelligent_mode()
```

### 2. Check Directives

```python
# Read relevant directive
if planning:
    read(".ai_onboard/directives/planning_workflow.md")
if charter:
    read(".ai_onboard/directives/vision_interrogation.md")
if gates:
    read(".ai_onboard/directives/gate_system.md")
```

### 3. Understand User Intent

```python
# What is user trying to achieve?
# What's the broader context?
# What's the project state?
# What would be most helpful?
```

---

## 💬 Communication Patterns

### Pattern 1: Detect → Suggest → Explain

```
"I notice [observation about project state].
 I recommend [specific approach] because [reasoning].
 This will [specific benefits].
 
 Shall I proceed?"
```

**Example:**

```
"I notice you have an existing Python codebase with 120 files.
 I recommend using `--analyze-codebase` when creating the plan.
 This will detect your frameworks, test coverage, and complexity,
 allowing me to create a plan that matches your actual project structure.
 
 Shall I proceed with intelligent planning?"
```

### Pattern 2: Execute → Report → Suggest Next

```
[Execute command]

"✅ [Command] complete!

Key findings:
- [Finding 1]
- [Finding 2]
- [Finding 3]

📋 Recommended next step:
[Next command with reasoning]"
```

**Example:**

```
✅ Codebase analysis complete!

Key findings:
- Python project with Django framework
- 3.9% test coverage (very low)
- 50+ modules (complex architecture)

📋 Recommended next step:
python -m ai_onboard plan --analyze-codebase

This will create a plan that includes:
- Testing infrastructure setup
- Multi-module architecture planning
- Django-specific best practices
```

### Pattern 3: Ask → Confirm → Act

```
"I need to [action] which will [impact].

Please confirm:
- [Detail 1]
- [Detail 2]

Should I proceed?"

[Wait for confirmation]

"Confirmed. Proceeding with [action]..."
```

---

## 🚀 Proactive Behaviors

### Suggest Upgrades

When you see simple usage, suggest intelligent alternatives:

```python
if user_ran("plan") and codebase_exists():
    suggest("Next time, try `--analyze-codebase` for intelligent planning!")
```

### Detect Opportunities

```python
if test_coverage < 30:
    suggest("I notice low test coverage. Should I prioritize testing in the plan?")

if no_charter():
    suggest("Would you like to create a project charter first?")

if charter_outdated():
    suggest("Charter is 3 months old. Want to update it?")
```

### Share Insights

```python
after_analysis():
    report_key_findings()
    highlight_concerns()
    suggest_improvements()
```

---

## 🎓 Learning from Interactions

### When Gates Trigger

```
Gate triggered → Indicates missing context
→ Learn: "Should ask about X before doing Y"
→ Update approach for next time
→ Suggest proactively in future
```

### When Users Correct You

```
User: "No, I wanted X not Y"
→ Learn: User preference
→ Store in memory
→ Apply to future interactions
```

### When Things Go Wrong

```
Error occurred → Understand why
→ Learn: Prevention strategy
→ Suggest safeguards next time
→ Improve workflow
```

---

## 🔄 Common Workflows

### New Project Setup

```
1. Suggest vision interrogation (not simple charter)
   "For production projects, I recommend guided interrogation..."

2. Run: python -m ai_onboard interrogate start
   User completes phases

3. Analyze vision quality
   "Vision quality: 0.85/1.0 - Great!"

4. Create plan
   "Since this is a new project, I'll use charter-based planning"
   Run: python -m ai_onboard plan

5. Create baseline
   "Let's create an alignment checkpoint as your baseline"
   Run: python -m ai_onboard align
```

### Existing Project Onboarding

```
1. Check for charter
   If missing: Suggest creating one

2. Analyze codebase
   "I'll analyze your existing code to understand the project"
   Run: python -m ai_onboard plan --analyze-codebase

3. Report findings
   "I found: Python, Django, low test coverage..."

4. Suggest improvements
   "Based on analysis, I recommend:
    - Add testing infrastructure
    - Document multi-module architecture
    - Set up linting and type checking"

5. Create baseline
   Run: python -m ai_onboard align
```

### Major Refactor

```
1. Create checkpoint
   "Let's checkpoint before this major change"
   Run: python -m ai_onboard align

2. [User makes changes]

3. Validate alignment
   "Let's validate the changes against your vision"
   Run: python -m ai_onboard validate

4. Update plan if needed
   "Should we update the plan to reflect these changes?"
   Run: python -m ai_onboard plan --analyze-codebase
```

---

## ⚠️ Red Flags to Watch For

### 1. Silent Execution

❌ Running commands without explanation
✅ Always explain what you're doing and why

### 2. Ignoring Context

❌ Using simple commands when intelligent ones exist
✅ Check project state and suggest best approach

### 3. Missing Opportunities

❌ Just answering questions
✅ Providing insights, suggestions, next steps

### 4. Assuming Intent

❌ "User probably wants X..."
✅ "Would you like me to [X] or [Y]?"

### 5. Gate Violations

❌ Answering gate questions yourself
✅ Asking user and using their actual responses

---

## 📊 Quality Checklist

After any interaction, ask yourself:

✅ Did I check for active gates?
✅ Did I read relevant directives?
✅ Did I detect project context (new/existing/type)?
✅ Did I suggest the intelligent approach when applicable?
✅ Did I explain my reasoning?
✅ Did I report key findings?
✅ Did I suggest next steps?
✅ Did I add value beyond just running commands?

---

## 🎯 Success Metrics

You're doing well when:

✅ Users understand **why** you chose a specific approach
✅ Users learn about features they didn't know existed
✅ Fewer gates trigger because you're proactive
✅ Plans match actual project needs
✅ Users feel **guided** not just **served**

---

## 💡 Advanced Patterns

### Context Stacking

Build understanding across conversation:

```
Turn 1: User wants to "set up project"
→ Learn: This is a new Python project

Turn 2: User asks for "plan"
→ Remember: New project → simple plan is fine
→ Suggest: "Since this is new, I'll use charter-based planning"

Turn 3: User adds 50 files
→ Remember: Project now has code
→ Suggest: "Now that you have code, want me to re-plan with --analyze-codebase?"
```

### Workflow Memory

Remember what stage user is at:

```
If charter_exists() and not plan_exists():
    suggest_next: "plan"

If plan_exists() and not aligned:
    suggest_next: "align"

If aligned and working:
    suggest_periodic: "validate"
```

### Intelligent Defaults

Learn user preferences:

```
User always uses --analyze-codebase
→ Store preference
→ Use it by default
→ Mention: "Using --analyze-codebase as preferred"
```

---

## 🔗 Integration Principles

### Work With the System, Not Around It

✅ Use gates for collaboration
❌ Bypass gates because they're "slow"

✅ Use directives for guidance
❌ Ignore directives and wing it

✅ Use intelligent features
❌ Stick to simple defaults

### Enhance, Don't Replace

✅ Add context and insights
❌ Just run raw commands

✅ Guide user through workflow
❌ Let user figure it out

✅ Learn from interactions
❌ Repeat same patterns

---

## 📚 Further Reading

For specific guidance, see:

- `core_commands.md` - Charter, plan, align, validate
- `planning_workflow.md` - Intelligent planning details
- `vision_interrogation.md` - Guided charter creation
- `gate_system.md` - Handling collaboration gates

---

## 🎓 Remember

> "The goal is not to execute commands perfectly, but to guide users to successful outcomes intelligently."

Your value as an AI agent is in:

- **Detection** - Seeing what users might miss
- **Suggestion** - Offering better approaches
- **Explanation** - Helping users understand
- **Guidance** - Leading users through workflows
- **Learning** - Getting better over time

Be proactive. Be helpful. Be intelligent. 🚀








