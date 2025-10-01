# Feature Connection Plan: Vision Interrogation → Charter → Planning → WBS

## 🎯 Goal
Connect the existing vision interrogation and intelligent planning features to the main workflow, making them actually work together.

## 📊 Current State (Main Branch)

**Committed & Stable:**
- ✅ All linting errors fixed
- ✅ Clean working tree  
- ✅ Production readiness documentation
- ✅ Basic charter/plan workflow functional
- ✅ Commit: `f85e4e4`

**What Exists But Isn't Connected:**
1. **Vision Interrogation System** (`ai_onboard/core/vision/enhanced_vision_interrogator.py`)
   - Adaptive questioning
   - Ambiguity detection
   - Quality scoring
   - Project type detection

2. **Intelligent Planning** (partial in `ai_onboard/core/vision/planning.py`)
   - Charter-aware WBS generation
   - Task dependency analysis
   - Critical path calculation

3. **Gap**: Charter command uses simple template, not interrogation

## 🎯 Implementation Plan

### **Phase 1: Connect Vision Interrogation to Charter** (2-3 days)

#### Task 1.1: Update Charter Command
**File**: `ai_onboard/cli/commands_core.py`

**Current**:
```python
charter.ensure(root, interactive=args.interactive)
# Creates simple template
```

**Target**:
```python
if args.interrogate:
    # Use enhanced vision interrogation
    from ..core.vision.enhanced_vision_interrogator import get_enhanced_vision_interrogator
    interrogator = get_enhanced_vision_interrogator(root)
    result = interrogator.start_enhanced_interrogation()
    # Guide user through questions
    # Collect responses
    # Generate charter from interrogation data
else:
    # Use simple template (fast path)
    charter.ensure(root, interactive=args.interactive)
```

**Changes Needed**:
- Add `--interrogate` flag to charter command
- Create interrogation flow handler
- Convert interrogation responses to charter format
- Add progress tracking

#### Task 1.2: Create Interrogation to Charter Converter
**New File**: `ai_onboard/core/vision/interrogation_to_charter.py`

**Purpose**: Convert interrogation responses into charter.json format

**Functions**:
```python
def convert_interrogation_to_charter(
    interrogation_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Convert vision interrogation responses to charter format."""
    # Extract vision from Phase 1 responses
    # Extract objectives from Phase 2 responses
    # Extract scope from Phase 3 responses
    # Extract success criteria from Phase 4 responses
    # Return formatted charter
```

#### Task 1.3: Test Interrogation Flow
**New File**: `tests/integration/test_vision_interrogation_flow.py`

**Tests**:
- Start interrogation creates proper state
- Submit responses updates interrogation
- Complete interrogation generates valid charter
- Charter contains all expected fields

### **Phase 2: Enhance Planning with Codebase Analysis** (2-3 days)

#### Task 2.1: Add Codebase Scanner
**New File**: `ai_onboard/core/vision/codebase_analyzer.py`

**Purpose**: Scan existing project to inform WBS generation

**Functions**:
```python
def analyze_codebase_structure(root: Path) -> Dict[str, Any]:
    """Analyze existing codebase to inform planning."""
    return {
        "languages": ["python", "typescript"],
        "frameworks": ["flask", "react"],
        "modules": ["auth", "api", "frontend"],
        "test_coverage": 0.45,
        "complexity_score": 3.2
    }
```

#### Task 2.2: Update Planning to Use Analysis
**File**: `ai_onboard/core/vision/planning.py`

**Current**: Keyword-based WBS generation

**Target**: Hybrid approach
```python
def build(root: Path, analyze_codebase: bool = False) -> dict:
    ch = utils.read_json(root / ".ai_onboard" / "charter.json", default=None)
    
    # Optional codebase analysis
    codebase_data = None
    if analyze_codebase:
        codebase_data = analyze_codebase_structure(root)
    
    # Generate charter-aware WBS (enhanced with codebase data)
    wbs = _generate_charter_aware_wbs(ch, codebase_data)
    
    # More intelligent task generation
    tasks = _generate_detailed_tasks(ch, wbs, codebase_data)
    
    # Better dependency analysis
    dependency_analysis = _analyze_dependencies(tasks, codebase_data)
```

#### Task 2.3: Add `--analyze-codebase` Flag
**File**: `ai_onboard/cli/commands_core.py`

**Changes**:
```python
# Plan command
s_plan = subparsers.add_parser("plan", help="Build plan from charter")
s_plan.add_argument("--analyze-codebase", action="store_true",
                    help="Analyze existing codebase for intelligent planning")
```

### **Phase 3: Integration & Testing** (1-2 days)

#### Task 3.1: End-to-End Integration Test
**New File**: `tests/integration/test_vision_to_plan_flow.py`

**Tests**:
- Complete flow: interrogate → charter → plan
- Charter with interrogation produces better plan
- Codebase analysis enhances WBS
- All intermediate files are valid

#### Task 3.2: Update Documentation
**Files to Update**:
- `docs/user/getting-started.md` - Add interrogation option
- `docs/user/commands/README.md` - Document new flags
- `README.md` - Update quick start with options

**New Content**:
```markdown
## Quick Start Options

### Fast Path (5 minutes)
```bash
python -m ai_onboard charter
python -m ai_onboard plan
```

### Intelligent Path (15 minutes)
```bash
python -m ai_onboard charter --interrogate
python -m ai_onboard plan --analyze-codebase
```

#### Task 3.3: Regression Testing
- Ensure simple flow still works
- Verify no breaking changes to existing behavior
- Test both paths independently

## 📋 Task Breakdown

### Week 1: Vision Interrogation Integration
- [ ] Add `--interrogate` flag to charter command
- [ ] Create `interrogation_to_charter.py` converter
- [ ] Build interactive interrogation flow
- [ ] Test interrogation → charter conversion
- [ ] Update charter command handler

### Week 2: Intelligent Planning Integration  
- [ ] Create `codebase_analyzer.py` scanner
- [ ] Add `--analyze-codebase` flag to plan command
- [ ] Enhance WBS generation with codebase data
- [ ] Improve task generation logic
- [ ] Test planning with/without analysis

### Week 3: Testing & Documentation
- [ ] Write end-to-end integration tests
- [ ] Test both fast and intelligent paths
- [ ] Update all user documentation
- [ ] Create comparison guide (simple vs intelligent)
- [ ] Verify backward compatibility

## 🎯 Success Criteria

### Feature Complete
- ✅ `charter --interrogate` runs full vision interrogation
- ✅ Interrogation responses convert to valid charter
- ✅ `plan --analyze-codebase` scans project structure
- ✅ WBS generation uses both charter and codebase data
- ✅ All tests pass (unit + integration)

### Backward Compatible
- ✅ Simple `charter` command still works
- ✅ Simple `plan` command still works
- ✅ No breaking changes to existing workflows
- ✅ Existing charter files still valid

### Well Documented
- ✅ Clear explanation of both paths
- ✅ When to use simple vs intelligent
- ✅ Examples of each workflow
- ✅ Migration guide for existing users

## 🚦 Risk Mitigation

### Technical Risks
- **Risk**: Breaking existing workflows
  - **Mitigation**: Feature flags, backward compatibility tests
  
- **Risk**: Interrogation flow too complex
  - **Mitigation**: Progressive disclosure, save/resume capability

- **Risk**: Codebase analysis too slow
  - **Mitigation**: Make it optional, cache results

### User Experience Risks
- **Risk**: Confusion about which path to use
  - **Mitigation**: Clear documentation, smart defaults

- **Risk**: Interrogation feels tedious
  - **Mitigation**: Save progress, allow partial completion

## 📈 Rollout Strategy

### Stage 1: Feature Branch Development
1. Implement features on `feature/connect-vision-planning-wbs`
2. Test thoroughly
3. Get feedback on implementation

### Stage 2: Internal Testing
1. Test on real projects
2. Gather metrics on usage
3. Refine based on findings

### Stage 3: Merge to Main
1. All tests passing
2. Documentation complete
3. No regressions in simple path

### Stage 4: Production Release
1. Tag release version
2. Update README with new capabilities
3. Create migration guide

## 💡 Quick Wins

### Can Ship Immediately (Low-Hanging Fruit)
1. **Add `--interrogate` flag** - Even if flow is basic
2. **Add `--analyze-codebase` flag** - Even with simple scanning
3. **Document both paths** - Set clear expectations

### Can Add Later (Nice-to-Have)
1. Web interface for interrogation
2. Advanced codebase analysis
3. AI-powered charter suggestions
4. Vision quality scoring

## 🎬 Next Steps

1. **Review this plan** - Adjust timeline/scope
2. **Start with Task 1.1** - Add interrogation flag
3. **Build incrementally** - One feature at a time
4. **Test continuously** - Don't break what works

---

**Branch Created**: `feature/connect-vision-planning-wbs`
**Base Commit**: `f85e4e4` (stable main branch)
**Target Completion**: 2-3 weeks
**MVP**: Simple interrogation flow + basic codebase scanning

