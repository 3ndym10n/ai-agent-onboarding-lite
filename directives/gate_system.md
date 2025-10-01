# AI Agent Gate System Directive

**CRITICAL**: Guidelines for properly handling AI agent collaboration gates.

---

## 🚨 What is a Gate?

A **gate** is a **mandatory pause point** where the system needs human input before proceeding. It's like a checkpoint that ensures AI agents collaborate with users rather than acting autonomously.

---

## 🎯 Gate Philosophy

### Core Principles

1. **Collaboration, Not Automation**: Gates enforce human-AI partnership
2. **User Authority**: User decisions guide the system
3. **Safety First**: Prevents AI from making assumptions
4. **Transparency**: Users always know when input is needed

### Why Gates Exist

❌ **Without Gates:**
```
System: "I need to know the project timeline"
AI: "Based on context, I'll assume 3 months"
System: *Proceeds with wrong assumption*
User: "Wait, what? I wanted 6 months!"
```

✅ **With Gates:**
```
System: *Activates gate*
AI: *Reads gate, asks user*
AI: "What is your desired project timeline?"
User: "6 months"
AI: *Submits response to gate*
System: *Proceeds with correct information*
```

---

## 📋 How Gates Work

### 1. Gate Activation

When system confidence is low or critical decisions are needed:

```
System creates: .ai_onboard/gates/current_gate.md
```

This file contains:
- **Gate type** (clarification, approval, decision)
- **Context** (what triggered the gate)
- **Questions** (what user needs to answer)
- **Instructions** (how AI should handle it)

### 2. Gate Detection

**YOUR RESPONSIBILITY**: Check for active gates!

```python
if file_exists(".ai_onboard/gates/current_gate.md"):
    read_and_handle_gate()
```

### 3. Gate Handling Process

```
Step 1: Read current_gate.md
Step 2: Extract "Questions for User"
Step 3: Ask user these questions in chat
Step 4: Wait for user's actual responses
Step 5: Create gate_response.json with answers
Step 6: System continues automatically
```

---

## 🔴 CRITICAL RULES

### ❌ NEVER Do This

1. **DON'T answer questions yourself**
   ```
   Gate: "What is the user's priority?"
   Agent: "Based on context, priority is performance" ❌
   ```

2. **DON'T fabricate responses**
   ```
   Agent creates gate_response.json with made-up answers ❌
   ```

3. **DON'T bypass gates**
   ```
   Agent ignores current_gate.md and proceeds ❌
   ```

4. **DON'T assume user intent**
   ```
   Agent: "User probably wants X, so I'll proceed" ❌
   ```

### ✅ ALWAYS Do This

1. **ASK the user directly**
   ```
   Agent: "I need to ask you some questions before proceeding:
           1. What is your desired timeline?
           2. What's your top priority?"
   ```

2. **WAIT for actual responses**
   ```
   Agent: *Pauses for user input*
   User: "Timeline is 3 months, priority is reliability"
   Agent: "Thank you!"
   ```

3. **CREATE gate_response.json with user's words**
   ```json
   {
     "user_responses": [
       "Timeline is 3 months",
       "Priority is reliability"
     ],
     "user_decision": "proceed"
   }
   ```

4. **CONFIRM understanding**
   ```
   Agent: "Got it! Timeline: 3 months, Priority: reliability.
           Creating response file..."
   ```

---

## 📝 Gate Response Format

### Required Structure

```json
{
  "user_responses": [
    "User's answer to question 1",
    "User's answer to question 2",
    "User's answer to question 3"
  ],
  "user_decision": "proceed|modify|stop",
  "additional_context": "Any extra context from user",
  "timestamp": "2025-10-01T00:00:00Z"
}
```

### Field Descriptions

- **user_responses**: Array of user's actual answers (in order of questions)
- **user_decision**: 
  - `"proceed"` - Continue with the operation
  - `"modify"` - User wants to change approach
  - `"stop"` - User wants to cancel
- **additional_context**: Any extra information user provided
- **timestamp**: Current ISO timestamp

---

## 💬 Communication Template

### When You Detect a Gate

```
"I see the system has activated a collaboration gate and needs your input 
before proceeding.

Questions:
1. [Question 1 from gate]
2. [Question 2 from gate]
3. [Question 3 from gate]

Please answer these questions so we can continue."
```

### After Receiving Answers

```
"Thank you! Let me confirm:

1. [User's answer 1]
2. [User's answer 2]
3. [User's answer 3]

Is this correct? Should I proceed with these responses?"
```

### After Creating Response

```
"✅ Gate response submitted. The system will continue now..."
```

---

## 🎯 Gate Types

### Clarification Gate

**Trigger**: System confidence < 0.8

**Questions**: Context-specific clarifications

**Example**:
```
Q: "What is the most important outcome you're hoping for?"
Q: "Are there specific areas to focus on first?"
Q: "Any must-haves for this command?"
Q: "Anything you don't want me to do?"
```

### Approval Gate

**Trigger**: Risky operation (deletion, major refactor)

**Questions**: Approval and safety checks

**Example**:
```
Q: "This will delete 15 files. Are you sure?"
Q: "Have you backed up important data?"
Q: "Type CONFIRM to proceed"
```

### Decision Gate

**Trigger**: Multiple valid paths

**Questions**: User preference on approach

**Example**:
```
Q: "Approach A: Fast but risky. Approach B: Slow but safe. Which?"
Q: "Would you like me to create a backup first?"
```

---

## 🔄 Gate Workflow Example

### Scenario: User asks to create a plan

```
Step 1: Command Execution Begins
→ python -m ai_onboard plan --analyze-codebase

Step 2: System Activates Gate (Low Confidence)
→ Creates .ai_onboard/gates/current_gate.md
→ Questions: "What's your priority?", "Focus areas?", "Must-haves?", "Don't do?"

Step 3: Agent Detects Gate ✅
→ Reads current_gate.md
→ Sees 4 questions

Step 4: Agent Asks User ✅
→ "The system needs clarification before proceeding:
    1. What's your most important outcome?
    2. Any specific areas to focus on?
    3. Any must-haves?
    4. Anything to avoid?"

Step 5: User Responds ✅
→ "1. I want intelligent planning with codebase analysis
    2. Focus on connecting vision and planning
    3. Must integrate with existing tools
    4. Don't redesign everything"

Step 6: Agent Creates Response ✅
→ Creates .ai_onboard/gates/gate_response.json
→ Includes user's actual answers
→ Sets decision: "proceed"

Step 7: System Continues ✅
→ Reads gate_response.json
→ Uses user's input to guide execution
→ Completes command with proper context
```

---

## 🚨 Common Pitfalls

### ❌ Pitfall 1: Ignoring Gates

```
Agent: *Sees gate file*
Agent: *Ignores it and runs command anyway*
System: ⚠️ Gate timeout, command fails
```

**Fix**: Always check for and handle gates

---

### ❌ Pitfall 2: Self-Answering

```
Gate: "What is user's priority?"
Agent: "Based on the codebase, I'll assume priority is testing"
Creates gate_response.json: {"user_responses": ["testing"]}
```

**Fix**: Ask the user, use their actual words

---

### ❌ Pitfall 3: Incomplete Responses

```
Gate has 4 questions
Agent only answers 2
```

**Fix**: Answer ALL questions in order

---

### ❌ Pitfall 4: Not Confirming Understanding

```
Agent: *Silently creates response file*
User: "Wait, what did you submit?"
```

**Fix**: Show user what you're submitting, get confirmation

---

## 📊 Gate File Locations

### Active Gate
```
.ai_onboard/gates/current_gate.md
```

### Your Response
```
.ai_onboard/gates/gate_response.json
```

### Status Files
```
.ai_onboard/gates/gate_status.json
.ai_onboard/gates/gate_ready.flag
```

---

## 🎓 Best Practices

### ✅ Do This

1. **Check for gates** before any major command
2. **Read the entire gate file** to understand context
3. **Ask questions exactly as written** in the gate
4. **Use user's actual words** in responses
5. **Confirm understanding** before submitting
6. **Explain what happened** after gate resolves

### ❌ Don't Do This

1. **Assume gates don't apply** to you
2. **Paraphrase or modify** gate questions
3. **Generate fake responses** for efficiency
4. **Skip confirmation** step
5. **Leave users confused** about gate process

---

## 💡 Pro Tips

### Tip 1: Pre-Check for Gates

Before running any `ai_onboard` command:
```python
if gate_active():
    handle_gate_first()
else:
    run_command()
```

### Tip 2: Make It Conversational

Don't just dump questions. Make it natural:
```
"Before I create the plan, I need to understand your priorities better.
 Let me ask you a few questions:
 
 1. What's the most important outcome for you?
 [wait for response]
 
 2. Any specific areas you want me to focus on first?
 [wait for response]
 
 Great! Let me confirm what I heard..."
```

### Tip 3: Summarize Before Submitting

```
"Let me make sure I have this right:

✓ Priority: Intelligent planning with codebase analysis  
✓ Focus: Connect vision and planning features
✓ Must-have: Integration with existing tools
✓ Avoid: Complete system redesign

Should I proceed with these responses?"
```

---

## 🔗 Related Systems

### Memory Integration

Gate responses can update agent memory:
```
User says: "Always use --analyze-codebase for planning"
→ Gate captures this preference
→ Agent memory stores it
→ Future planning uses it automatically
```

### Learning System

Gate interactions improve agent behavior:
```
Gate triggered because agent didn't ask first
→ System learns: "Should ask about X before doing Y"
→ Future agents prompt proactively
→ Fewer gates needed over time
```

---

## 📚 References

- **Gate Implementation**: `ai_onboard/core/ai_integration/ai_agent_gate_enforcer.py`
- **Gate Detection**: Check `.ai_onboard/gates/` directory
- **Repo Rules**: See `AGENTS.md` for gate contract

