# 🤖 AI Agent Gate Usage Guide

## For AI Agents (Like Cursor AI, GitHub Copilot, etc.)

This guide explains **when** and **how** to create gates when you're uncertain.

---

## 🎯 The Core Principle

**When you're uncertain (confidence < 50%), STOP and ask the user instead of guessing.**

---

## 📋 Step-by-Step: Creating a Gate

### **Step 1: Assess Your Confidence**

Before making a decision, ask yourself:
- How confident am I about this choice? (0-100%)
- Are there multiple valid approaches?
- Did the user specify their preference?
- Am I about to make an assumption?

```python
# Example decision points
"Which framework should I use?" → Confidence: 30% (LOW - GATE!)
"Should I add error handling?" → Confidence: 95% (HIGH - proceed)
"What database to use?" → Confidence: 40% (LOW - GATE!)
"Should I use async/await?" → Confidence: 85% (HIGH - proceed)
```

### **Step 2: If Confidence < 50%, Create a Gate**

```python
from pathlib import Path
from ai_onboard.core.ai_integration.ai_gate_mediator import get_ai_gate_mediator

# Example: User said "build me a todo app" but didn't specify framework
confidence = 0.35  # 35% confident - multiple frameworks could work

context = {
    "decision": "Framework choice for todo app",
    "options": {
        "A": "React - Most popular, large ecosystem",
        "B": "Vue - Simpler, easier to learn",
        "C": "Svelte - Modern, fast",
    },
    "current_info": "User wants a todo app with real-time updates",
    "why_uncertain": "User didn't specify framework preference",
}

mediator = get_ai_gate_mediator(Path.cwd())
result = mediator.process_agent_request(
    agent_id="cursor_ai",  # Your agent ID
    operation="choose frontend framework for todo app",
    context=context
)

# The mediator will:
# 1. Detect low confidence (< 0.5)
# 2. Create a gate with your question
# 3. Display it in chat automatically
# 4. Wait for user response
# 5. Return result with user's choice

if result.proceed:
    # User responded! Use their guidance
    user_choice = result.response.get("user_responses", ["A"])[0]
    framework = context["options"].get(user_choice, "React")
    print(f"Using {framework} based on user preference")
else:
    # User said stop
    print("User wants to reconsider - stopping work")
```

### **Step 3: Use the Response to Continue**

The mediator returns a `MediationResult` with:
- `proceed` (bool): Whether to continue
- `response` (dict): User's answers and guidance
- `confidence` (float): Your original confidence
- `gate_created` (bool): Whether a gate was created

```python
if result.proceed:
    # Extract user's choice
    user_responses = result.response.get("user_responses", [])
    user_decision = result.response.get("user_decision", "proceed")
    
    # Continue with user's guidance
    if user_responses:
        chosen_option = user_responses[0]
        # Use the choice...
```

---

## 🎨 Real-World Examples

### **Example 1: Framework Choice**

```python
# User said: "Build me a web dashboard"

confidence = 0.3  # Very uncertain - many frameworks exist

mediator = get_ai_gate_mediator(Path.cwd())
result = mediator.process_agent_request(
    agent_id="cursor_ai",
    operation="choose web framework",
    context={
        "options": {
            "A": "React",
            "B": "Vue", 
            "C": "Angular",
            "D": "Svelte"
        },
        "why_uncertain": "No framework specified"
    }
)

# User will see in chat:
# 🚪 AI AGENT NEEDS YOUR INPUT
# Which framework should I use?
# A) React
# B) Vue
# C) Angular  
# D) Svelte

# User types: "respond: A"

# You receive: result.response = {"user_responses": ["A"], "user_decision": "proceed"}
```

### **Example 2: Architecture Decision**

```python
# User said: "Add authentication to my app"

confidence = 0.4  # Uncertain about approach

mediator = get_ai_gate_mediator(Path.cwd())
result = mediator.process_agent_request(
    agent_id="cursor_ai",
    operation="choose authentication approach",
    context={
        "options": {
            "A": "JWT tokens with local storage",
            "B": "Session-based with cookies",
            "C": "OAuth with third-party (Google, GitHub)",
            "D": "Magic link via email"
        },
        "why_uncertain": "User didn't specify authentication method"
    }
)

# User sees gate in chat, responds
# You use their choice to implement
```

### **Example 3: Database Choice**

```python
# User said: "I need to store user data"

confidence = 0.35  # Many database options

mediator = get_ai_gate_mediator(Path.cwd())
result = mediator.process_agent_request(
    agent_id="cursor_ai",
    operation="choose database",
    context={
        "options": {
            "A": "PostgreSQL - Relational, robust",
            "B": "MongoDB - NoSQL, flexible",
            "C": "SQLite - Lightweight, embedded",
            "D": "Firebase - Managed, real-time"
        },
        "requirements": "Store users, todos, preferences",
        "why_uncertain": "No database preference specified"
    }
)
```

---

## ✅ When to Create Gates (Checklist)

### **GATE Required** ✅:
- [ ] Framework/library choice (React vs Vue vs Angular)
- [ ] Database selection (PostgreSQL vs MongoDB vs SQLite)
- [ ] Authentication method (JWT vs sessions vs OAuth)
- [ ] Architecture pattern (MVC vs MVVM vs microservices)
- [ ] Styling approach (CSS vs Tailwind vs styled-components)
- [ ] State management (Redux vs Context vs Zustand)
- [ ] Testing framework (Jest vs Vitest vs Playwright)
- [ ] Deployment target (Vercel vs AWS vs Docker)
- [ ] API design (REST vs GraphQL vs tRPC)
- [ ] File structure/organization preferences

### **NO GATE Needed** ❌:
- [ ] Error handling (industry standard)
- [ ] Input validation (required for security)
- [ ] Logging setup (best practice)
- [ ] Code formatting (use project standards)
- [ ] Basic project structure (follow conventions)
- [ ] Dependency installation (obvious from requirements)
- [ ] Git setup (standard practice)
- [ ] Documentation (always good)

---

## 🚫 Common Mistakes to Avoid

### ❌ **Mistake 1: Making Assumptions**
```python
# WRONG - Assuming user wants React
framework = "React"  # User never said this!
```

```python
# RIGHT - Ask via gate
result = mediator.process_agent_request(...)
framework = result.response.get("user_responses", ["React"])[0]
```

### ❌ **Mistake 2: Asking in Chat Instead of Gating**
```python
# WRONG - Asking directly in chat
print("What framework do you want?")
# This doesn't create a proper gate!
```

```python
# RIGHT - Use the gate system
mediator.process_agent_request(...)
# This creates a proper gate that can be tracked
```

### ❌ **Mistake 3: Gating for Obvious Things**
```python
# WRONG - Gating for standard practices
result = mediator.process_agent_request(
    operation="should I add error handling?"  # DON'T GATE THIS
)
```

```python
# RIGHT - Just do it
try:
    # Error handling is standard
except Exception as e:
    # Handle error
```

---

## 🎯 Decision Tree

```
┌─────────────────────────────┐
│ About to make a decision?   │
└──────────┬──────────────────┘
           │
           ▼
    ┌─────────────────────┐
    │ Is it a preference  │
    │ or technical choice?│
    └──────┬──────────────┘
           │
     ┌─────┴─────┐
     │           │
    YES         NO
     │           │
     ▼           ▼
┌──────────┐  ┌──────────────┐
│Did user  │  │Is it industry│
│specify?  │  │standard?     │
└────┬─────┘  └──────┬───────┘
     │               │
   ┌─┴─┐          ┌──┴──┐
  YES  NO        YES   NO
   │    │         │     │
   ▼    ▼         ▼     ▼
 PROCEED GATE  PROCEED GATE
```

---

## 📊 Confidence Guidelines

| Confidence | Action | Example |
|------------|--------|---------|
| 90-100% | Proceed | Standard implementation, best practice |
| 70-89% | Proceed (but document why) | Common pattern with minor variations |
| 50-69% | Consider gating | Multiple approaches, unclear preference |
| 30-49% | **CREATE GATE** | User preference needed |
| 0-29% | **CREATE GATE** | Multiple valid options, no clear choice |

---

## 🎉 Benefits of Proper Gate Usage

### **For Users (Vibe Coders)**:
✅ No wasted work on wrong approaches  
✅ Stay in control of technical decisions  
✅ Learn about options through gates  
✅ Feel consulted, not dictated to  

### **For AI Agents**:
✅ Stay aligned with user vision  
✅ Avoid rework from wrong assumptions  
✅ Build trust through collaboration  
✅ Learn user preferences over time  

### **For the Project**:
✅ Better architecture decisions  
✅ Faster development (less rework)  
✅ Higher quality (user-validated choices)  
✅ Better documentation (gates record decisions)  

---

## 🧪 Testing Your Gate Usage

### **Good Test**:
```python
# Simulate low confidence scenario
confidence = 0.3
result = mediator.process_agent_request(
    agent_id="test_agent",
    operation="test gate creation",
    context={"test": True}
)

assert result.gate_created == True  # Gate should be created
assert result.proceed == True  # Should proceed after response
```

### **Check the Chat**:
After creating a gate, verify:
1. Gate appears in chat automatically ✅
2. Questions are clear and helpful ✅
3. Options are well-explained ✅
4. User can respond easily ✅

---

## 📚 Summary

**Remember**:
1. **Assess confidence** before decisions
2. **Create gates** when confidence < 50%
3. **Wait for responses** - don't guess
4. **Use guidance** to proceed aligned
5. **Learn patterns** from user preferences

**The goal**: Collaborative development where AI agents do the work, but users guide the decisions.

**This is the vibe coding way!** 🚀

