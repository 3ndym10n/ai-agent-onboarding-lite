# 🚀 VectorFlow Onboarding Directory

**Essential information for AI models taking over VectorFlow development**

## 📋 **QUICK START (15 minutes)**

### **Step 1: Core Understanding (5 minutes)**
1. **`../goals.txt`** - Original project vision
2. **`SYSTEM_ARCHITECTURE_OVERVIEW.md`** - High-level system design
3. **`PROJECT_STATUS_TRACKER.md`** - Current project status

### **Step 2: Implementation Focus (10 minutes)**
4. **`PRIORITY_IMPLEMENTATION_ORDER.md`** - What to work on next
5. **`DEVELOPMENT_CONTEXT.md`** - Coding standards and patterns

---

## 🎯 **KEY CONCEPTS**

### **VectorFlow is NOT a trading bot**
- **Trading Intelligence System** - enhances human decision-making
- **Manual Execution Required** - trader maintains final authority
- **Statistical Validation** - quantifies instinctive patterns

### **Performance Requirements**
- **<100ms** signal generation latency
- **80-90%** accuracy on regime detection
- **>60%** hit rate on AI playbook suggestions
- **50+ coins** simultaneous processing

### **Technology Stack**
- **Python async/await** architecture
- **PostgreSQL + Redis** for data persistence
- **Multi-exchange WebSocket** streams
- **Streamlit** dashboard (70% chart, 30% terminal)
- **Grok AI** for playbook suggestions

---

## 🚨 **CRITICAL RULES**

### **NEVER DELETE:**
- Any file in `onboarding/` directory
- Files containing "onboarding", "progress", or "status"
- Core system files (database, config, etc.)

### **ALWAYS DO:**
- Check `PROJECT_STATUS_TRACKER.md` before starting work
- Focus on missing components only (avoid duplication)
- Update status after completing components
- Test integration with existing systems

### **FILE PROTECTION:**
- Use `python onboarding/protect.py check <file>` to verify deletion safety
- Use `python onboarding/cleanup.py` for safe repository cleanup
- Protected files listed in `onboarding/.protect`

### **SUCCESS CRITERIA:**
A trader sees BTC approach $65,000 and VectorFlow instantly provides:
```
🔥 SELL | Score: 0.85 | Confidence: 82%
📍 Reasons: OI spike +7% at $65,000 | TPO poor high | Book suppression 0.73
📚 Playbooks: "Trap Reversal", "Poor High Fade", "Range Bounce"
```

**Total Onboarding Time: ~15 minutes** (reduced from 45 minutes)