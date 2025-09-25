# 🎯 **MyPy Error Resolution Plan**

## 📊 **Executive Summary**

**Current State**: 480 mypy errors across the AI-Onboard codebase
**Goal**: Achieve clean mypy type checking with zero errors
**Timeline**: 4-phase approach over multiple sessions
**Strategy**: Systematic error categorization and resolution

## 🔍 **Error Analysis**

### **Error Categories (480 total)**:
1. **Missing Imports** (~80 errors) - `[name-defined]`
2. **Type Annotations** (~120 errors) - `[var-annotated]`, `[arg-type]` 
3. **Attribute Errors** (~90 errors) - `[attr-defined]`
4. **Assignment Issues** (~70 errors) - `[assignment]`
5. **Function Signatures** (~50 errors) - `[call-arg]`, `[call-overload]`
6. **Unreachable Code** (~30 errors) - `[unreachable]`
7. **Miscellaneous** (~30 errors) - `[misc]`, `[operator]`

### **Most Problematic Files**:
1. `unified_tool_orchestrator.py` - 45+ errors
2. `code_cleanup_automation.py` - 35+ errors  
3. `mandatory_tool_consultation_gate.py` - 25+ errors
4. `kaizen_automation.py` - 20+ errors
5. `advanced_agent_decision_pipeline.py` - 15+ errors

## 📋 **Phase 1: Critical Infrastructure (Priority 1)**
**Target**: ~150 errors | **Timeline**: Session 1

### **1.1 Missing Imports (80 errors)**
**Files**: Multiple core modules
**Errors**: `[name-defined]` - json, ast, sys, os, subprocess, etc.
**Solution**:
```python
# Add missing standard library imports
import json
import ast
import sys
import os
import subprocess
import re
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, field
```

### **1.2 Core Type Infrastructure**
**Files**: `unified_tool_orchestrator.py`, `mandatory_tool_consultation_gate.py`
**Focus**: Fix type assignment and conditional function variants
**Solution**:
- Fix optional dependency handling patterns
- Resolve type assignment conflicts  
- Add proper type annotations for core classes

### **1.3 Data Structure Fixes**
**Files**: `code_cleanup_automation.py`
**Focus**: Fix dataclass and type definition issues
**Solution**:
- Add proper dataclass imports and decorators
- Fix ImportStatement constructor calls
- Add missing type annotations

**Expected Result**: ~150 errors resolved, core infrastructure stable

## 📋 **Phase 2: Type Annotations (Priority 2)**
**Target**: ~120 errors | **Timeline**: Session 2

### **2.1 Variable Type Annotations**
**Error Type**: `[var-annotated]`
**Files**: Multiple modules with untyped variables
**Solution**:
```python
# Before
categorized = {}
tool_analysis = {}

# After  
categorized: Dict[str, List[Any]] = {}
tool_analysis: Dict[str, Any] = {}
```

### **2.2 Function Argument Types**
**Error Type**: `[arg-type]`
**Files**: Core orchestration and PM modules
**Solution**:
- Add proper type hints to function parameters
- Fix incompatible argument types
- Resolve Union type issues

### **2.3 Return Type Annotations**
**Files**: Functions missing return type hints
**Solution**:
```python
# Before
def get_status(self):

# After
def get_status(self) -> Dict[str, Any]:
```

**Expected Result**: ~120 errors resolved, better IDE support

## 📋 **Phase 3: Attribute & Method Resolution (Priority 3)**
**Target**: ~90 errors | **Timeline**: Session 3

### **3.1 Missing Attributes**
**Error Type**: `[attr-defined]`
**Files**: Orchestration compatibility, PM modules
**Issues**: Methods called on wrong classes after consolidation
**Solution**:
- Update method calls to use correct unified APIs
- Fix compatibility layer method signatures
- Add missing attributes to classes

### **3.2 Method Signature Fixes**
**Error Type**: `[call-arg]`, `[call-overload]`
**Solution**:
- Fix function call signatures
- Update deprecated method calls
- Resolve overload conflicts

### **3.3 Legacy Code Updates**
**Files**: Compatibility shims and deprecated modules
**Solution**:
- Update calls to consolidated systems
- Fix attribute access patterns
- Resolve inheritance issues

**Expected Result**: ~90 errors resolved, method calls working correctly

## 📋 **Phase 4: Assignment & Logic Cleanup (Priority 4)**
**Target**: ~120 errors | **Timeline**: Session 4

### **4.1 Assignment Compatibility**
**Error Type**: `[assignment]`
**Solution**:
- Fix type mismatches in assignments
- Resolve Union type conflicts
- Update variable type declarations

### **4.2 Unreachable Code Removal**
**Error Type**: `[unreachable]`
**Solution**:
- Remove dead code paths
- Fix conditional logic issues
- Clean up redundant statements

### **4.3 Operator & Misc Issues**
**Error Type**: `[operator]`, `[misc]`
**Solution**:
- Fix operator type compatibility
- Resolve miscellaneous type issues
- Clean up remaining edge cases

**Expected Result**: All remaining errors resolved

## 🔧 **Implementation Strategy**

### **Session Structure**:
1. **Pre-Analysis** (5 min): Run mypy, categorize current errors
2. **Batch Fixes** (20 min): Systematic error resolution by category  
3. **Validation** (10 min): Re-run mypy, verify progress
4. **Documentation** (5 min): Update plan with results

### **Quality Gates**:
- ✅ No new errors introduced
- ✅ All tests continue passing
- ✅ Core functionality preserved
- ✅ Progressive error count reduction

### **Tools & Commands**:
```bash
# Error analysis
python -m mypy ai_onboard/ --show-error-codes --no-error-summary

# Specific file checking  
python -m mypy ai_onboard/core/unified_tool_orchestrator.py

# Error counting
python -c "import subprocess; result = subprocess.run(['python', '-m', 'mypy', 'ai_onboard/', '--show-error-codes', '--no-error-summary'], capture_output=True, text=True); print('Total mypy errors:', result.stdout.count('error:'))"
```

## 📈 **Success Metrics**

### **Phase Targets**:
- **Phase 1**: 480 → 330 errors (-150)
- **Phase 2**: 330 → 210 errors (-120) 
- **Phase 3**: 210 → 120 errors (-90)
- **Phase 4**: 120 → 0 errors (-120)

### **Final Goals**:
- ✅ **0 mypy errors**
- ✅ **Full type coverage** for core modules
- ✅ **Enhanced IDE support** with proper type hints
- ✅ **Maintained functionality** throughout process

## 🚨 **Risk Mitigation**

### **Backup Strategy**:
- Work on feature branch: `feature/mypy-resolution`
- Regular commits after each major fix batch
- Automated testing after each phase

### **Rollback Plan**:
- Keep original code in comments during major changes
- Test suite must pass after each phase
- Immediate rollback if core functionality breaks

## 📝 **Phase 1 Execution Checklist**

### **Immediate Actions**:
- [ ] Create feature branch
- [ ] Run baseline mypy analysis  
- [ ] Fix missing imports in top 5 problematic files
- [ ] Resolve critical type infrastructure issues
- [ ] Validate with test suite
- [ ] Document progress and update plan

### **Ready to Execute**: ✅
**Estimated Time**: 40 minutes
**Expected Reduction**: 150 errors (480 → 330)

