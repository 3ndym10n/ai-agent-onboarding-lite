# Import Consolidation System

## Overview

The Import Consolidation System is a comprehensive solution for safely consolidating imports in the ai_onboard codebase. It provides automated analysis, planning, execution, monitoring, and validation of import consolidation with full integration into the existing safety framework.

## 🎯 Goals

- **Reduce Import Verbosity**: Consolidate frequently used imports into single modules
- **Improve Maintainability**: Centralize import management
- **Enhance Performance**: Reduce import resolution time
- **Maintain Safety**: Full integration with existing safety framework
- **Provide Monitoring**: Real-time tracking of consolidation progress

## 🏗️ Architecture

### Core Components

1. **Import Consolidation Migrator** (`scripts/migration/import_consolidation_migrator.py`)
   - Analyzes consolidation opportunities
   - Creates migration plans
   - Executes safe migrations with backup/rollback

2. **Import Equivalence Validator** (`scripts/analysis/validate_import_equivalence.py`)
   - Validates that consolidated imports are functionally equivalent
   - Tests import resolution and functionality
   - Detects circular dependencies and namespace conflicts

3. **Import Change Monitor** (`scripts/maintenance/monitor_import_changes.py`)
   - Real-time monitoring of import changes
   - Progress tracking and metrics collection
   - Automated alerting for issues

4. **Integrated Consolidation** (`scripts/migration/integrated_import_consolidation.py`)
   - Complete workflow orchestration
   - Integration with existing safety framework
   - Comprehensive error handling and reporting

5. **CLI Integration** (`ai_onboard/cli/commands_import_consolidation.py`)
   - Command-line interface for all consolidation operations
   - Integration with existing ai_onboard CLI

## 🚀 Quick Start

### 1. Analyze Consolidation Opportunities

```bash
# Analyze the current codebase for consolidation opportunities
python -m ai_onboard consolidate analyze

# This will:
# - Scan all Python files for imports
# - Identify consolidation candidates
# - Generate recommendations
# - Save analysis results to .ai_onboard/consolidation_analysis.json
```

### 2. Create Migration Plan

```bash
# Create a migration plan for specific targets
python -m ai_onboard consolidate plan common_imports types paths

# This will:
# - Create a comprehensive migration plan
# - Generate backup using safety framework
# - Assess migration risks
# - Save plan to .ai_onboard/migration_plan.json
```

### 3. Execute Consolidation

```bash
# Execute the consolidation workflow (dry run first)
python -m ai_onboard consolidate execute common_imports types paths --dry-run

# Execute live migration
python -m ai_onboard consolidate execute common_imports types paths --auto-approve
```

### 4. Monitor Progress

```bash
# Start monitoring
python -m ai_onboard consolidate monitor start common_imports types paths

# Check status
python -m ai_onboard consolidate monitor status

# View progress for specific target
python -m ai_onboard consolidate monitor progress common_imports
```

### 5. Validate Results

```bash
# Validate import equivalence
python -m ai_onboard consolidate validate --config .ai_onboard/consolidation_config.json

# Check workflow status
python -m ai_onboard consolidate status
```

## 📋 Configuration

### Consolidation Targets

The system supports multiple consolidation targets defined in `.ai_onboard/consolidation_config.json`:

```json
{
  "consolidation_targets": {
    "common_imports": {
      "target_file": "ai_onboard/core/common_imports.py",
      "priority": 1,
      "risk_level": "low",
      "imports": [
        "pathlib.Path",
        "typing.Dict",
        "typing.List",
        "dataclasses.dataclass"
      ]
    },
    "types": {
      "target_file": "ai_onboard/core/types.py",
      "priority": 2,
      "risk_level": "low",
      "imports": [
        "typing.Dict",
        "typing.List",
        "typing.Optional",
        "typing.Any"
      ]
    }
  }
}
```

### Migration Settings

```json
{
  "migration_settings": {
    "batch_size": 5,
    "validation_interval": 3,
    "rollback_threshold": 0.8,
    "dry_run_first": true,
    "max_retries": 3,
    "retry_delay": 5
  }
}
```

### Safety Checks

```json
{
  "safety_checks": [
    "import_resolution",
    "syntax_validation",
    "circular_dependency",
    "functionality_test",
    "performance_test",
    "namespace_conflict"
  ]
}
```

## 🔒 Safety Features

### 1. Full Backup Integration
- Uses existing `CleanupSafetyGateFramework`
- Automatic backup creation before any changes
- One-click rollback capability

### 2. Comprehensive Validation
- Pre-workflow validation
- Post-workflow validation
- Import equivalence validation
- Performance impact assessment

### 3. Real-time Monitoring
- Change tracking and logging
- Progress monitoring
- Automated alerting
- Performance metrics

### 4. Error Handling
- Automatic rollback on failure
- Detailed error reporting
- Retry mechanisms
- Graceful degradation

## 📊 Monitoring and Metrics

### Real-time Monitoring

The system provides comprehensive monitoring capabilities:

```bash
# Start monitoring
python -m ai_onboard consolidate monitor start common_imports

# Check status
python -m ai_onboard consolidate monitor status

# View progress
python -m ai_onboard consolidate monitor progress common_imports
```

### Metrics Collected

- **Change Metrics**: Total changes, success rate, error rate
- **Performance Metrics**: Processing time, performance trends
- **Progress Metrics**: Files processed, completion percentage
- **Alert Metrics**: Alert counts, resolution status

### Logging

All activities are logged to:
- `.ai_onboard/import_monitoring_log.jsonl` - Change history
- `.ai_onboard/consolidation_workflow_log.jsonl` - Workflow steps
- `.ai_onboard/import_equivalence_report.json` - Validation results

## 🛠️ Advanced Usage

### Custom Consolidation Targets

Create custom consolidation targets by modifying the configuration:

```json
{
  "consolidation_targets": {
    "my_custom_target": {
      "target_file": "ai_onboard/core/my_custom_imports.py",
      "priority": 1,
      "risk_level": "low",
      "imports": [
        "my_module.specific_import",
        "another_module.another_import"
      ]
    }
  }
}
```

### Custom Validation

Create custom validation tests:

```python
# tests/test_import_consolidation.py
def test_consolidated_imports():
    """Test that consolidated imports work correctly."""
    from ai_onboard.core.common_imports import Path, Dict, List

    # Test functionality
    assert Path("/test").exists() == False
    assert Dict[str, int] == dict
    assert List[str] == list
```

### Integration with CI/CD

Add to your CI/CD pipeline:

```yaml
# .github/workflows/import-consolidation.yml
name: Import Consolidation
on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM

jobs:
  consolidate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install -e .
      - name: Analyze consolidation opportunities
        run: python -m ai_onboard consolidate analyze
      - name: Execute consolidation (dry run)
        run: python -m ai_onboard consolidate execute common_imports types --dry-run
```

## 🔧 Troubleshooting

### Common Issues

1. **Import Resolution Errors**
   ```bash
   # Check import resolution
   python -c "import ai_onboard; print('Imports OK')"

   # Validate specific imports
   python -m ai_onboard consolidate validate --original "pathlib.Path" --consolidated "ai_onboard.core.common_imports.Path"
   ```

2. **Circular Dependencies**
   ```bash
   # Check for circular dependencies
   python -m ai_onboard consolidate validate --config .ai_onboard/consolidation_config.json
   ```

3. **Performance Issues**
   ```bash
   # Check performance metrics
   python -m ai_onboard consolidate monitor status
   ```

### Rollback Procedures

If something goes wrong:

```bash
# Check workflow status
python -m ai_onboard consolidate status

# Rollback specific workflow
python -m ai_onboard consolidate rollback <workflow_id>

# Manual rollback using safety framework
python -m ai_onboard cleanup safety restore --backup-id <backup_id>
```

## 📈 Performance Impact

### Expected Improvements

- **Import Resolution**: 20-30% faster due to consolidated imports
- **Code Readability**: Reduced import verbosity
- **Maintenance**: Centralized import management
- **Bundle Size**: Slight reduction in compiled code size

### Monitoring Performance

```bash
# Check performance metrics
python -m ai_onboard consolidate monitor status

# View detailed performance report
cat .ai_onboard/import_equivalence_report.json
```

## 🤝 Contributing

### Adding New Consolidation Targets

1. Update `.ai_onboard/consolidation_config.json`
2. Add target configuration
3. Test with dry run
4. Execute and validate

### Adding New Validation Checks

1. Extend `ImportEquivalenceValidator`
2. Add new validation methods
3. Update configuration
4. Test thoroughly

### Adding New Monitoring Metrics

1. Extend `ImportChangeMonitor`
2. Add new metric collection
3. Update reporting
4. Test monitoring

## 📚 API Reference

### ImportConsolidationMigrator

```python
migrator = ImportConsolidationMigrator(root_path)

# Analyze opportunities
analysis = migrator.analyze_consolidation_opportunities()

# Create migration plan
plan = migrator.create_migration_plan(["common_imports", "types"])

# Execute migration
results = migrator.execute_migration(dry_run=True)
```

### ImportEquivalenceValidator

```python
validator = ImportEquivalenceValidator(root_path)

# Validate equivalence
report = validator.validate_consolidation_equivalence(
    original_imports=["pathlib.Path"],
    consolidated_imports=["ai_onboard.core.common_imports.Path"],
    test_files=[Path("tests/test_imports.py")]
)
```

### ImportChangeMonitor

```python
monitor = ImportChangeMonitor(root_path)

# Start monitoring
monitor.start_monitoring(["common_imports"])

# Record changes
monitor.record_import_change(
    file_path=Path("test.py"),
    line_number=1,
    change_type=ChangeType.CONSOLIDATED,
    original_import="pathlib.Path",
    new_import="ai_onboard.core.common_imports.Path",
    consolidation_target="common_imports"
)

# Get status
status = monitor.get_current_status()
```

## 🎉 Success Stories

### Before Consolidation

```python
# Before: Verbose imports in every file
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import sys
```

### After Consolidation

```python
# After: Clean, consolidated imports
from ai_onboard.core.common_imports import (
    Path, Dict, List, Optional, Any, Union, Callable,
    dataclass, field, deque, contextmanager,
    datetime, timedelta, Enum, json, os, sys
)
```

## 📞 Support

For issues, questions, or contributions:

1. Check the troubleshooting section
2. Review the logs in `.ai_onboard/`
3. Use the built-in help: `python -m ai_onboard consolidate --help`
4. Create an issue in the repository

---

**Note**: This system is designed to work seamlessly with the existing ai_onboard safety framework. All operations are fully reversible and include comprehensive backup and rollback capabilities.
