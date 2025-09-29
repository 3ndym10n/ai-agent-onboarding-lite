# 🛡️ Cleanup Safety Gates Design

## Overview

This document outlines the design for robust cleanup safety gates that prevent accidental system damage during file cleanup and reorganization operations. The design is based on lessons learned from actual cleanup operations where critical dependencies were nearly missed.

## 🎯 Design Goals

### Primary Goals
1. **Prevent System Breakage**: Never allow deletion/moving of files with unresolved dependencies
2. **Human-Agent Alignment**: Require explicit human approval for potentially dangerous operations
3. **Comprehensive Dependency Detection**: Detect ALL types of file dependencies before operations
4. **Rollback Capability**: Provide absolute rollback for any cleanup operation
5. **Progressive Safety**: Multiple safety checkpoints with increasing confirmation requirements

### Secondary Goals
- **Performance**: Fast dependency scanning even for large codebases
- **Usability**: Clear, actionable error messages and recommendations
- **Extensibility**: Easy to add new dependency detection patterns
- **Auditability**: Complete logging of all cleanup operations and decisions

## 🏗️ Architecture Overview

```
Cleanup Safety Gates Architecture
═════════════════════════════════

User Request
     ↓
┌─────────────────┐
│   Gate 1:       │ ← Basic validation (file exists, permissions)
│   Pre-Flight    │
│   Validation    │
└─────────────────┘
     ↓
┌─────────────────┐
│   Gate 2:       │ ← Comprehensive dependency analysis
│   Dependency    │
│   Analysis      │
└─────────────────┘
     ↓
┌─────────────────┐
│   Gate 3:       │ ← Risk assessment and classification
│   Risk          │
│   Assessment    │
└─────────────────┘
     ↓
┌─────────────────┐
│   Gate 4:       │ ← Human confirmation with detailed report
│   Human         │
│   Confirmation  │
└─────────────────┘
     ↓
┌─────────────────┐
│   Gate 5:       │ ← Backup creation and operation logging
│   Backup &      │
│   Execute       │
└─────────────────┘
     ↓
┌─────────────────┐
│   Gate 6:       │ ← Post-operation validation and rollback option
│   Post-Op       │
│   Validation    │
└─────────────────┘
```

## 🔍 Gate Specifications

### Gate 1: Pre-Flight Validation
**Purpose**: Basic sanity checks before expensive operations

**Checks**:
- File/directory existence verification
- Permission checks (read/write/delete)
- Path validation (no invalid characters, length limits)
- Protected path enforcement (never allow deletion of critical system files)
- Disk space availability

**Failure Action**: Immediate abort with clear error message

**Implementation**:
```python
class PreFlightGate:
    def validate(self, targets: List[Path]) -> GateResult:
        for target in targets:
            if not target.exists():
                return GateResult.fail(f"Path does not exist: {target}")

            if target in PROTECTED_PATHS:
                return GateResult.fail(f"Protected path cannot be modified: {target}")

            if not self._check_permissions(target):
                return GateResult.fail(f"Insufficient permissions: {target}")

        return GateResult.pass_()
```

### Gate 2: Dependency Analysis
**Purpose**: Comprehensive detection of all file dependencies

**Dependency Types Detected**:
1. **Python Imports**: `import`, `from ... import`, dynamic imports
2. **Configuration References**: JSON/YAML/TOML file paths
3. **Documentation Links**: Markdown links, file references
4. **Build System References**: Setup files, CI/CD configurations
5. **CLI Command References**: Command-line tool configurations
6. **Test Dependencies**: Test files, fixtures, data files
7. **Generic Text References**: Any text file mentioning the target

**Advanced Features**:
- **AST Parsing**: Accurate Python import analysis
- **Regex Patterns**: Flexible pattern matching for different file types
- **Context Analysis**: Understanding the type and criticality of each reference
- **Cache Filtering**: Distinguish between real dependencies and cache/build artifacts

**Implementation**:
```python
class DependencyAnalysisGate:
    def __init__(self):
        self.checkers = [
            PythonImportChecker(),
            ConfigurationChecker(),
            DocumentationChecker(),
            BuildSystemChecker(),
            GenericTextChecker()
        ]

    def analyze(self, targets: List[Path]) -> DependencyReport:
        all_dependencies = []

        for target in targets:
            target_deps = []
            for checker in self.checkers:
                deps = checker.find_dependencies(target)
                target_deps.extend(deps)

            all_dependencies.append(TargetDependencies(target, target_deps))

        return DependencyReport(all_dependencies)
```

### Gate 3: Risk Assessment
**Purpose**: Classify operations by risk level and determine required approval level

**Risk Levels**:
- **🟢 LOW**: No dependencies, non-critical files, easy rollback
- **🟡 MEDIUM**: Few dependencies, can be automatically fixed, moderate impact
- **🟠 HIGH**: Many dependencies, requires manual fixes, significant impact
- **🔴 CRITICAL**: Core system files, breaking changes, requires expert review

**Risk Factors**:
1. **Dependency Count**: More dependencies = higher risk
2. **Dependency Types**: Import dependencies more critical than documentation
3. **File Criticality**: Core system files vs temporary files
4. **Rollback Complexity**: How easy is it to undo the operation
5. **Impact Scope**: How many system components affected

**Implementation**:
```python
class RiskAssessmentGate:
    def assess_risk(self, dependency_report: DependencyReport) -> RiskAssessment:
        risk_scores = []

        for target_deps in dependency_report.targets:
            score = 0

            # Dependency count factor
            score += min(len(target_deps.dependencies) * 2, 50)

            # Dependency type factor
            for dep in target_deps.dependencies:
                if dep.type == DependencyType.PYTHON_IMPORT:
                    score += 20
                elif dep.type == DependencyType.CONFIG_REFERENCE:
                    score += 15
                elif dep.type == DependencyType.DOCUMENTATION_LINK:
                    score += 5

            # File criticality factor
            if target_deps.target.name in CRITICAL_FILES:
                score += 100

            risk_scores.append(score)

        max_score = max(risk_scores) if risk_scores else 0
        return RiskAssessment.from_score(max_score)
```

### Gate 4: Human Confirmation
**Purpose**: Require explicit human approval with full information disclosure

**Confirmation Levels**:
- **🟢 LOW**: Automatic approval or simple "y/n" confirmation
- **🟡 MEDIUM**: Detailed report + "CONFIRM: [code]" requirement
- **🟠 HIGH**: Detailed report + fix plan + "CONFIRM: [complex-code]" requirement
- **🔴 CRITICAL**: Manual expert review required, no automatic approval

**Information Provided**:
1. **Operation Summary**: What will be done
2. **Risk Assessment**: Risk level and reasoning
3. **Dependency Report**: Complete list of affected files
4. **Fix Plan**: Specific steps to resolve dependencies
5. **Rollback Plan**: How to undo the operation if needed
6. **Confirmation Code**: Unique code to prevent accidental approval

**Implementation**:
```python
class HumanConfirmationGate:
    def request_confirmation(self, operation: CleanupOperation,
                           risk: RiskAssessment,
                           dependencies: DependencyReport) -> ConfirmationResult:

        # Generate detailed report
        report = self._generate_report(operation, risk, dependencies)

        # Generate confirmation code based on risk level
        if risk.level == RiskLevel.CRITICAL:
            return ConfirmationResult.require_manual_review()

        confirmation_code = self._generate_confirmation_code(risk.level)

        # Display report and request confirmation
        self._display_report(report)
        self._display_confirmation_request(confirmation_code)

        user_input = input("Please confirm: ")

        if user_input.strip() == f"CONFIRM: {confirmation_code}":
            return ConfirmationResult.approved()
        else:
            return ConfirmationResult.denied()
```

### Gate 5: Backup & Execute
**Purpose**: Create comprehensive backups before execution and log all operations

**Backup Strategy**:
1. **Full State Backup**: Git checkpoint or full directory backup
2. **Incremental Backup**: Only affected files and their dependencies
3. **Metadata Backup**: File permissions, timestamps, symbolic links
4. **Database Backup**: Any database state that might be affected

**Execution Logging**:
- **Pre-execution State**: Complete system state snapshot
- **Operation Log**: Every file operation with timestamps
- **Dependency Changes**: All dependency updates made
- **Post-execution State**: Final system state
- **Rollback Instructions**: Exact steps to undo the operation

**Implementation**:
```python
class BackupExecuteGate:
    def execute_with_backup(self, operation: CleanupOperation) -> ExecutionResult:
        # Create backup
        backup_id = self._create_backup(operation.affected_files)

        # Log operation start
        self._log_operation_start(operation, backup_id)

        try:
            # Execute operation with detailed logging
            for step in operation.steps:
                self._log_step_start(step)
                result = self._execute_step(step)
                self._log_step_result(step, result)

                if not result.success:
                    # Immediate rollback on failure
                    self._rollback(backup_id)
                    return ExecutionResult.failed(result.error)

            # Log successful completion
            self._log_operation_success(operation, backup_id)
            return ExecutionResult.success(backup_id)

        except Exception as e:
            # Emergency rollback
            self._emergency_rollback(backup_id)
            return ExecutionResult.failed(str(e))
```

### Gate 6: Post-Operation Validation
**Purpose**: Verify system integrity after operation and provide rollback option

**Validation Checks**:
1. **System Functionality**: Run basic system tests
2. **Dependency Integrity**: Verify no broken dependencies remain
3. **File System Integrity**: Check for orphaned files or broken links
4. **Configuration Validity**: Validate all configuration files
5. **Import Validation**: Test that all Python imports still work

**Rollback Options**:
- **Automatic Rollback**: If validation fails, automatically rollback
- **Manual Rollback**: User-initiated rollback with confirmation
- **Partial Rollback**: Rollback specific files while keeping others
- **Forward Fix**: Apply additional fixes instead of rolling back

**Implementation**:
```python
class PostOperationGate:
    def validate_and_offer_rollback(self, execution_result: ExecutionResult) -> ValidationResult:
        # Run validation checks
        validation_results = []

        for validator in self.validators:
            result = validator.validate()
            validation_results.append(result)

        # Check for failures
        failures = [r for r in validation_results if not r.success]

        if failures:
            # Offer rollback options
            self._display_validation_failures(failures)
            rollback_choice = self._prompt_rollback_options(execution_result.backup_id)

            if rollback_choice == RollbackChoice.AUTO:
                self._perform_rollback(execution_result.backup_id)
                return ValidationResult.rolled_back()

        return ValidationResult.success()
```

## 🔧 Implementation Strategy

### Phase 1: Core Infrastructure (T24)
1. **Gate Framework**: Base classes and interfaces
2. **Dependency Detection**: Enhanced dependency checker
3. **Risk Assessment**: Risk calculation algorithms
4. **Backup System**: Comprehensive backup mechanisms

### Phase 2: Safety Gates Implementation (T25)
1. **Gate 1-3**: Pre-flight, dependency, and risk assessment
2. **Gate 4**: Human confirmation system with codes
3. **Gate 5**: Backup and execution with logging
4. **Gate 6**: Post-operation validation and rollback

### Phase 3: Integration & Testing (T26)
1. **CLI Integration**: Add safety gates to all cleanup commands
2. **Configuration**: Make gates configurable for different scenarios
3. **Testing**: Comprehensive test suite for all gate scenarios
4. **Documentation**: User guides and troubleshooting

## 🎛️ Configuration Options

### Safety Levels
```yaml
cleanup_safety:
  level: "strict"  # strict, moderate, permissive

  gates:
    pre_flight: true
    dependency_analysis: true
    risk_assessment: true
    human_confirmation: true
    backup_execution: true
    post_validation: true

  confirmation:
    low_risk_auto_approve: false
    medium_risk_require_code: true
    high_risk_require_complex_code: true
    critical_risk_require_manual_review: true

  backup:
    create_git_checkpoint: true
    create_file_backup: true
    backup_retention_days: 30
```

### Dependency Detection
```yaml
dependency_detection:
  python_imports: true
  config_references: true
  documentation_links: true
  build_system_refs: true
  generic_text_refs: true

  exclusions:
    - "**/.git/**"
    - "**/__pycache__/**"
    - "**/*.pyc"
    - "**/node_modules/**"

  cache_files:
    - "**/*cache*.json"
    - "**/SOURCES.txt"
```

## 🚨 Emergency Procedures

### Immediate Rollback
If any gate fails catastrophically:
1. **STOP** all operations immediately
2. **ROLLBACK** to last known good state
3. **LOG** the failure with full context
4. **NOTIFY** human operators
5. **PRESERVE** all evidence for debugging

### Manual Override
For emergency situations:
1. **EMERGENCY_OVERRIDE** environment variable
2. **Requires** explicit confirmation with admin password
3. **Logs** all override actions
4. **Creates** emergency backup before proceeding
5. **Sends** alert notifications

## 📊 Success Metrics

### Safety Metrics
- **Zero Incidents**: No system breakage due to cleanup operations
- **Dependency Detection Rate**: >99% of dependencies caught
- **False Positive Rate**: <5% of safe operations blocked
- **Rollback Success Rate**: 100% successful rollbacks when needed

### Usability Metrics
- **Confirmation Time**: Average time for human confirmation <2 minutes
- **Operation Success Rate**: >95% of approved operations complete successfully
- **User Satisfaction**: Clear, actionable error messages and recommendations

## 🔮 Future Enhancements

### AI-Powered Risk Assessment
- **Machine Learning**: Learn from past operations to improve risk assessment
- **Pattern Recognition**: Automatically detect new types of dependencies
- **Predictive Analysis**: Predict likely issues before they occur

### Advanced Rollback
- **Selective Rollback**: Rollback specific changes while keeping others
- **Time-based Rollback**: Rollback to any point in time
- **Dependency-aware Rollback**: Rollback related changes automatically

### Integration Enhancements
- **IDE Integration**: Safety gates directly in development environments
- **CI/CD Integration**: Automated safety checks in deployment pipelines
- **Team Coordination**: Multi-user approval workflows for critical operations

---

This design provides comprehensive safety for cleanup operations while maintaining usability and performance. The multi-gate approach ensures that dangerous operations are caught at multiple levels, and the human confirmation system ensures proper alignment between AI agents and human operators.
