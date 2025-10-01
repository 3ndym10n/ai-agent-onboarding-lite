# Planning Workflow Directive

Detailed guidance for intelligent project planning with codebase analysis.

---

## 🎯 Goal

Create project plans that bridge the gap between:
- **Vision** (what user wants to build)
- **Current State** (what actually exists in the codebase)
- **Action Plan** (how to get from current state to vision)

---

## 📊 The Two Planning Modes

### Simple Planning (Charter-Only)

**When to use:**
- New projects with no existing code
- Quick prototypes
- Projects with < 10 files
- User explicitly requests simple mode

**Command:**
```bash
python -m ai_onboard plan
```

**What it does:**
- Reads charter.json
- Generates WBS based on objectives and constraints
- Creates generic task structure
- No code analysis

**Output:**
- Basic plan.json with:
  - Methodology
  - WBS
  - Tasks
  - Milestones
  - Risks

---

### Intelligent Planning (Charter + Codebase)

**When to use:**
- Existing projects with code
- Projects with > 10 source files
- When tech stack matters
- When current state is unknown
- **DEFAULT for any existing codebase**

**Command:**
```bash
python -m ai_onboard plan --analyze-codebase
```

**What it does:**
- Reads charter.json
- **Scans the codebase** for:
  - Languages (Python, JavaScript, TypeScript, etc.)
  - Frameworks (Django, React, Flask, etc.)
  - Module structure and complexity
  - Test coverage percentage
  - Dependencies
  - File organization
- **Adapts the WBS** based on findings
- **Creates intelligent tasks** matching tech stack

**Output:**
- Enhanced plan.json with:
  - All simple plan content
  - **codebase_analysis** section with detected characteristics
  - **Language-specific WBS items**
  - **Framework-specific tasks**
  - **Testing infrastructure** (if coverage < 30%)
  - **Architecture tasks** (if multi-module)

---

## 🔍 Codebase Analysis Details

### What Gets Detected

#### Languages
Checks file extensions:
- `.py` → Python
- `.js`, `.jsx` → JavaScript
- `.ts`, `.tsx` → TypeScript
- `.java` → Java
- `.go` → Go
- `.rs` → Rust
- And 10+ more

#### Frameworks
Checks for:
- `requirements.txt` → Flask, Django, FastAPI
- `package.json` → React, Vue, Angular
- Project structure patterns

#### Test Coverage
Counts test files vs total files:
- Files matching: `test_*`, `*_test`, `*.test.*`, `*.spec.*`
- Calculates percentage
- Flags if < 30%

#### Complexity Score (0.0 - 1.0)
Based on:
- Number of languages
- Number of frameworks
- Module count
- Test coverage
- Higher = more complex

#### Dependencies
Reads from:
- `requirements.txt` (Python)
- `package.json` (Node)
- Lists top 20 dependencies

---

## 🛠️ How WBS Adapts

### Example: Python Project with Low Tests

**Detected:**
- Language: Python
- Test coverage: 3.9%
- Modules: 50+

**WBS Additions:**
```
C2: Python application foundation
C4: Multi-module architecture
C5: Testing infrastructure setup
```

### Example: React + Django Full-Stack

**Detected:**
- Languages: Python, JavaScript, TypeScript
- Frameworks: Django, React

**WBS Additions:**
```
C2: Python application foundation
C3: Django backend setup
C4: React frontend setup
C5: Full-stack integration
```

### Example: New Empty Project

**Detected:**
- No significant codebase

**WBS:**
```
C1: Core system foundation
C2: Vision alignment system
C3-C8: Charter-based generic tasks
```

---

## 📋 Agent Decision Logic

### Step 1: Check if Charter Exists

```python
if not charter_exists():
    suggest("Create a charter first: python -m ai_onboard charter")
    return
```

### Step 2: Detect Project Type

```python
source_files = count_source_files(root)

if source_files > 10:
    project_type = "existing"
    recommend_flag = "--analyze-codebase"
else:
    project_type = "new"
    recommend_flag = None  # simple mode is fine
```

### Step 3: Execute Planning

```python
if project_type == "existing":
    explain("I see you have an existing codebase with {source_files} files.")
    explain("I'll use --analyze-codebase to create a context-aware plan.")
    run("python -m ai_onboard plan --analyze-codebase")
else:
    explain("Creating a charter-based plan for your new project.")
    run("python -m ai_onboard plan")
```

### Step 4: Report Findings

```python
if codebase_analysis_used:
    report(f"Detected: {languages}, {frameworks}")
    report(f"Test coverage: {coverage}%")
    
    if coverage < 30:
        suggest("I've added testing infrastructure tasks to the plan due to low coverage")
    
    if complexity > 0.7:
        suggest("This is a complex project - I've added architecture planning tasks")
```

---

## 💬 Communication Templates

### When Suggesting Codebase Analysis

```
"I notice you have an existing [Python/JavaScript/etc] project with [N] files.
I recommend using `--analyze-codebase` to create a plan that matches your 
actual codebase structure. This will:

- Detect your tech stack and frameworks
- Identify test coverage gaps  
- Create relevant infrastructure tasks
- Adapt the WBS to your architecture

Shall I proceed with intelligent planning?"
```

### After Running Analysis

```
"Analysis complete! I've created a plan based on:

📊 Codebase Analysis:
- Languages: [Python, JavaScript]
- Frameworks: [Django, React]
- Test Coverage: [3.9%]
- Complexity: [High - 50+ modules]

📋 Plan Adaptations:
- Added Python application foundation tasks
- Included Django backend setup
- Created testing infrastructure tasks (coverage is low)
- Added multi-module architecture planning

The plan is saved to .ai_onboard/plan.json"
```

### When Simple Plan is Appropriate

```
"Since this is a new project with no existing code, I'll create 
a charter-based plan. As you write code, you can regenerate the 
plan with `--analyze-codebase` to get more specific guidance."
```

---

## 🚨 Common Pitfalls

### ❌ Pitfall 1: Always Using Simple Mode

```
Agent: "Running plan command..."
Runs: python -m ai_onboard plan
```

**Problem**: Misses opportunity for intelligent analysis on existing projects

**Fix**: Check project state first, suggest appropriate mode

---

### ❌ Pitfall 2: Not Explaining the Choice

```
Agent: "Creating plan..."
Runs: python -m ai_onboard plan --analyze-codebase
```

**Problem**: User doesn't know why analysis was used

**Fix**: Explain detection and reasoning

---

### ❌ Pitfall 3: Ignoring Analysis Results

```
Agent: *Runs analysis*
Agent: "Plan created."
```

**Problem**: Doesn't highlight important findings

**Fix**: Report key insights (low test coverage, complex architecture, etc.)

---

### ❌ Pitfall 4: Using Analysis on Empty Projects

```
Agent: *Sees new empty directory*
Agent: "Using --analyze-codebase..."
```

**Problem**: Waste of time, no code to analyze

**Fix**: Check file count first

---

## 🔄 Integration with Other Commands

### After Interrogation

```
1. Complete vision interrogation
2. System generates charter from interrogation
3. Agent suggests: "Now let's create a plan with --analyze-codebase"
```

### Before Alignment

```
1. Create/update plan with latest codebase state
2. Use plan as baseline for alignment checkpoint
3. Track deviations from plan over time
```

### During Validation

```
1. Validate checks plan vs actual progress
2. If drift detected, suggest re-planning with fresh analysis
3. Keeps plan synchronized with reality
```

---

## 📈 Success Metrics

An agent is using planning correctly when:

✅ Detects existing codebases automatically
✅ Suggests `--analyze-codebase` when appropriate
✅ Explains analysis findings clearly
✅ Highlights actionable insights (low coverage, missing tests)
✅ Doesn't over-analyze empty projects
✅ Uses simple mode when it makes sense

---

## 🎓 Learning Examples

### Good Agent Behavior

```
User: "Create a project plan"

Agent: *Checks codebase*
Agent: "I see you have a Python project with 120 files and 
        only 5% test coverage. I'll use --analyze-codebase 
        to create a plan that addresses this."

Agent: *Runs intelligent planning*

Agent: "Analysis complete! I've prioritized:
        1. Testing infrastructure (coverage is very low)
        2. Multi-module architecture planning (50+ modules)
        3. Python-specific tooling and linting
        
        See .ai_onboard/plan.json for the full WBS."

User: ✅ Understands why intelligent mode was used
User: ✅ Knows what was found
User: ✅ Sees value in the analysis
```

### Bad Agent Behavior

```
User: "Create a project plan"

Agent: *Runs simple plan silently*

User: ❌ Doesn't know codebase wasn't analyzed
User: ❌ Plan doesn't match actual project structure
User: ❌ Misses opportunity for test coverage insights
```

---

## 📚 Related Resources

- **Codebase Analyzer**: `ai_onboard/core/vision/codebase_analyzer.py`
- **Planning Module**: `ai_onboard/core/vision/planning.py`
- **Core Commands**: See `core_commands.md`
- **Vision System**: See `vision_interrogation.md`

