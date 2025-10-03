# Vision Interrogation Directive

Guidelines for using the enhanced vision interrogation system to create comprehensive project charters.

---

## 🎯 Purpose

Vision interrogation is an **intelligent guided process** that helps users define clear, complete project visions through structured questions. It replaces the simple template-based charter with a conversation-driven approach.

---

## 🔄 Simple vs Intelligent Charter Creation

### Simple Charter (Template-Based)

**Command**: `python -m ai_onboard charter`

**When to use:**
- Quick prototypes
- Internal tools
- User knows exactly what they want
- Time-constrained situations

**What you get:**
- Basic charter.json with minimal fields
- User fills in blanks manually
- Fast but potentially incomplete

---

### Intelligent Charter (Interrogation-Based)

**Command**: `python -m ai_onboard interrogate start`

**When to use:**
- Production projects
- Projects with multiple stakeholders
- Unclear or evolving vision
- Need comprehensive planning
- **RECOMMENDED for serious projects**

**What you get:**
- Rich, detailed charter.json
- Structured through guided questions
- Covers scope, boundaries, success metrics
- Higher vision quality score
- Better alignment foundation

---

## 📋 The Interrogation Flow

### Phase 1: Core Vision & Problem
Questions about:
- Core problem being solved
- Primary users/beneficiaries
- Vision statement
- Project name

**Example:**
```
Q: "What core problem are you trying to solve?"
Q: "Who are the primary users or beneficiaries?"
Q: "What is your vision statement for this project?"
```

### Phase 2: Stakeholders & Goals
Questions about:
- Key stakeholders and their roles
- Project objectives
- Risk appetite
- Delivery timeline
- Team size
- Methodology preferences

**Example:**
```
Q: "Who are the key stakeholders and their roles?"
Q: "What are your main project objectives?"
Q: "What is your risk appetite? (low/medium/high)"
```

### Phase 3: Scope & Boundaries
Questions about:
- What's in scope
- What's explicitly out of scope
- Non-goals (what you won't do)
- Assumptions
- Constraints
- Compliance requirements

**Example:**
```
Q: "What is explicitly IN scope for this project?"
Q: "What is explicitly OUT of scope?"
Q: "What are you NOT trying to achieve?"
```

### Phase 4: Success Criteria
Questions about:
- How success will be measured
- Specific metrics and targets
- Minimum viable outcomes
- Definition of done

**Example:**
```
Q: "How will you measure success?"
Q: "What are the minimum viable outcomes?"
Q: "What metrics will you track?"
```

---

## 🤖 Agent Workflow

### Step 1: Detect When to Suggest Interrogation

```python
if user_wants_charter():
    if is_new_production_project() or vision_unclear():
        suggest_interrogation()
    else:
        suggest_simple_charter()
```

### Step 2: Suggest Appropriately

**Good suggestion:**
```
"I can create a charter in two ways:

1. 📝 Simple template (5 min) - Good for prototypes
   Command: python -m ai_onboard charter

2. 🎯 Guided interrogation (15-20 min) - Recommended for production
   Command: python -m ai_onboard interrogate start
   Benefits:
   - Comprehensive vision definition
   - Structured through guided questions
   - Covers scope, boundaries, success criteria
   - Creates better foundation for planning

Which would you prefer?"
```

### Step 3: Manage the Interrogation Process

**Not Your Job**: Don't answer the questions yourself!

The interrogation system will:
1. Ask questions to the user
2. Collect responses
3. Generate charter from responses

**Your Job**: 
- Guide the user to start the process
- Explain what interrogation does
- Help if they get stuck
- Suggest interrogation when appropriate

### Step 4: After Interrogation Completes

```python
if interrogation_complete():
    explain("Vision interrogation complete!")
    show_vision_quality_score()
    suggest_next_step("python -m ai_onboard plan --analyze-codebase")
```

---

## 📊 Commands Reference

### Check Interrogation Status

```bash
python -m ai_onboard interrogate check
```

**Shows:**
- Current interrogation state
- Vision quality score
- Whether ready to generate charter

### Start New Interrogation

```bash
python -m ai_onboard interrogate start
```

**Begins:**
- Interactive question flow
- Phase-by-phase vision definition
- Automatic charter generation on completion

### View Questions

```bash
python -m ai_onboard interrogate questions
```

**Returns:**
- All questions for current phase
- Question types (text, choice, boolean)
- Help text for each question

### Get Summary

```bash
python -m ai_onboard interrogate summary
```

**Shows:**
- Collected responses so far
- Vision quality assessment
- Completeness metrics

---

## 🎯 Vision Quality Score

The system calculates a quality score (0.0 - 1.0) based on:
- **Completeness**: All required fields filled
- **Clarity**: Specific, unambiguous responses
- **Scope Definition**: Clear boundaries set
- **Success Metrics**: Measurable outcomes defined

**Interpretation:**
- `0.9 - 1.0`: Excellent vision, ready for complex planning
- `0.7 - 0.9`: Good vision, minor gaps
- `0.5 - 0.7`: Adequate vision, could be more specific
- `< 0.5`: Incomplete, needs more definition

---

## 💬 Communication Templates

### Suggesting Interrogation for New Project

```
"For production projects, I recommend using the vision interrogation system 
instead of a simple charter. It takes about 15-20 minutes but creates a much 
more comprehensive foundation:

✅ Structured questions guide you through vision definition
✅ Covers scope, boundaries, success criteria systematically  
✅ Generates detailed charter with vision quality scoring
✅ Creates better alignment for planning and execution

Would you like to use the guided interrogation?
If so, run: python -m ai_onboard interrogate start"
```

### When Simple Charter is Better

```
"For quick prototypes or internal tools, the simple charter template 
works well:

python -m ai_onboard charter

If you later need more detail, you can always switch to interrogation mode."
```

### After Interrogation Completes

```
"✅ Vision interrogation complete!

Your charter has been generated with:
- Vision Quality Score: 0.85/1.0 (Good!)
- All phases completed
- Scope boundaries defined
- Success metrics established

📋 Next recommended step:
python -m ai_onboard plan --analyze-codebase

This will create a project plan that combines your vision with 
analysis of your existing codebase (if any)."
```

---

## 🔗 Integration with Planning

### Optimal Workflow

```
Step 1: Vision Interrogation
→ python -m ai_onboard interrogate start
→ Complete all phases
→ Charter generated with high quality score

Step 2: Intelligent Planning  
→ python -m ai_onboard plan --analyze-codebase
→ Combines charter vision with codebase reality
→ Creates context-aware WBS and tasks

Step 3: Alignment Baseline
→ python -m ai_onboard align
→ Creates checkpoint with comprehensive vision
→ Tracks drift over time
```

---

## 🚨 Common Mistakes

### ❌ Mistake 1: Always Using Simple Charter

```
Agent: "I'll create a charter for you"
Runs: python -m ai_onboard charter
```

**Problem**: User misses comprehensive vision definition

**Fix**: Ask about project type, suggest interrogation for production

---

### ❌ Mistake 2: Answering Interrogation Questions Yourself

```
Interrogation: "What is your risk appetite?"
Agent: "Based on context, I'll answer 'medium'..."
```

**Problem**: Violates user collaboration - these are USER'S questions!

**Fix**: Let the interrogation system ask the user directly

---

### ❌ Mistake 3: Not Explaining the Options

```
Agent: "Run python -m ai_onboard charter"
```

**Problem**: User doesn't know interrogation exists

**Fix**: Present both options, explain trade-offs

---

### ❌ Mistake 4: Skipping Quality Assessment

```
Agent: *Interrogation completes*
Agent: "Charter created."
```

**Problem**: Doesn't share vision quality score

**Fix**: Report score and what it means

---

## 🎓 Best Practices

### ✅ Do This

1. **Assess project type** before suggesting charter method
2. **Explain both options** (simple vs interrogation)
3. **Let interrogation system** handle the questions
4. **Report quality score** after completion
5. **Suggest next step** (planning) after charter is ready

### ❌ Don't Do This

1. **Force interrogation** on simple prototypes
2. **Skip suggesting interrogation** for production projects
3. **Answer questions** on behalf of user
4. **Ignore quality score** warnings
5. **Create charter and stop** - suggest planning next

---

## 📈 Success Indicators

You're using interrogation correctly when:

✅ Production projects get interrogation suggestions
✅ Users understand the trade-off between methods
✅ Interrogation completes with high quality scores (>0.7)
✅ Generated charters lead to better plans
✅ Users feel their vision is comprehensively captured

---

## 📚 Technical Details

### File Locations

- **Interrogation State**: `.ai_onboard/vision_interrogation.json`
- **Generated Charter**: `.ai_onboard/charter.json`
- **Interrogation Module**: `ai_onboard/core/vision/enhanced_vision_interrogator.py`
- **Conversion Logic**: `ai_onboard/core/vision/interrogation_to_charter.py`

### Data Flow

```
User responses 
  → Vision interrogation system
  → Structured data collection
  → Quality scoring
  → Charter generation
  → charter.json
  → Planning input
```

---

## 🔄 Related Directives

- See `core_commands.md` for charter command basics
- See `planning_workflow.md` for using charter in planning
- See `best_practices.md` for overall workflow guidance



