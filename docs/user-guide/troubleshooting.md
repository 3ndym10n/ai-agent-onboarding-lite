# Troubleshooting Guide

AI Onboard includes intelligent error handling and recovery systems, but sometimes you need additional guidance. This comprehensive troubleshooting guide covers common issues and their solutions.

## 🚨 Quick Diagnostic Commands

Before diving into specific issues, use these commands to quickly diagnose problems:

```bash
# System health check
python -m ai_onboard status --comprehensive

# Automatic issue analysis
python -m ai_onboard debug analyze

# Configuration validation
python -m ai_onboard validate --report

# User experience diagnostics
python -m ai_onboard ux analytics errors
```

## 🎯 Common Issues & Solutions

### Installation & Setup Issues

#### Issue: `ModuleNotFoundError: No module named 'ai_onboard'`
**Symptoms**: Command not found or import errors
**Cause**: AI Onboard not properly installed

**Solutions**:
```bash
# Verify Python version (3.8+ required)
python --version

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Verify installation
python -m ai_onboard --version
```

#### Issue: Permission denied errors
**Symptoms**: Cannot create files or directories
**Cause**: Insufficient permissions or protected directories

**Solutions**:
```bash
# Check current directory permissions
ls -la

# Use user-specific installation
pip install --user -e .

# Create AI Onboard directory manually
mkdir -p .ai_onboard
chmod 755 .ai_onboard

# Run with appropriate permissions
sudo python -m ai_onboard <command>  # Use sparingly
```

#### Issue: `Command not found: python`
**Symptoms**: Shell cannot find Python
**Cause**: Python not in PATH or using wrong Python version

**Solutions**:
```bash
# Try alternative Python commands
python3 -m ai_onboard --help
py -m ai_onboard --help

# Check Python installation
which python
which python3

# Add Python to PATH (Windows)
set PATH=%PATH%;C:\Python39\Scripts

# Add Python to PATH (Linux/Mac)
export PATH=$PATH:/usr/local/bin/python3
```

### Charter & Planning Issues

#### Issue: Charter creation fails with validation errors
**Symptoms**: Charter rejected with low clarity score
**Cause**: Incomplete or unclear vision definition

**Solutions**:
```bash
# Use AI assistance for charter creation
python -m ai_onboard charter --ai-assist --project-type "your_project_type"

# Start with a template
python -m ai_onboard charter --template software_development

# Get charter guidance
python -m ai_onboard help charter --examples

# Validate charter quality
python -m ai_onboard charter --validate --detailed
```

**Charter Quality Checklist**:
- ✅ Clear problem statement (what specific problem are you solving?)
- ✅ Measurable success criteria (how will you know you succeeded?)
- ✅ Well-defined target users (who will benefit?)
- ✅ Realistic constraints (time, budget, technical limitations)
- ✅ Identified stakeholders (who makes decisions?)

#### Issue: Plan generation produces unrealistic timelines
**Symptoms**: Generated plan too aggressive or conservative
**Cause**: Insufficient context or incorrect project complexity assessment

**Solutions**:
```bash
# Provide more context during planning
python -m ai_onboard plan --project-size medium --team-size 5 --complexity high

# Use scenario planning
python -m ai_onboard plan --scenarios "conservative,balanced,aggressive"

# Adjust plan manually
python -m ai_onboard plan task --estimate T5 --effort "8_days"
python -m ai_onboard plan --add-buffer 0.2  # Add 20% buffer

# Validate plan viability
python -m ai_onboard plan --validate-timeline --validate-resources
```

#### Issue: Alignment check fails consistently
**Symptoms**: Low alignment scores despite good charter and plan
**Cause**: Misalignment between vision and plan structure

**Solutions**:
```bash
# Get detailed alignment analysis
python -m ai_onboard align --detailed --recommendations

# Focus alignment on specific areas
python -m ai_onboard align --focus "timeline,resources,goals"

# Adjust plan to improve alignment
python -m ai_onboard plan --align-to-charter --prioritize-goals

# Manual alignment approval with notes
python -m ai_onboard align --approve --note "Manual review completed"
```

### Command Execution Issues

#### Issue: Commands hang or run indefinitely
**Symptoms**: Commands don't complete or respond
**Cause**: Resource constraints, network issues, or infinite loops

**Solutions**:
```bash
# Check system resources
top
htop
ps aux | grep python

# Kill hanging processes
pkill -f "ai_onboard"
killall python

# Run with timeout
timeout 300 python -m ai_onboard <command>  # 5 minute timeout

# Use verbose mode for debugging
python -m ai_onboard <command> --verbose --debug
```

#### Issue: `JSONDecodeError` when running commands
**Symptoms**: Invalid JSON error messages
**Cause**: Corrupted configuration or data files

**Solutions**:
```bash
# Validate JSON configuration files
python -c "import json; print(json.load(open('.ai_onboard/config.json')))"

# Reset configuration
python -m ai_onboard config reset --confirm

# Backup and recreate data directory
mv .ai_onboard .ai_onboard.backup
python -m ai_onboard charter  # Recreates directory

# Check for file corruption
python -m ai_onboard debug analyze --check-files
```

#### Issue: `AttributeError: 'Namespace' object has no attribute`
**Symptoms**: CLI argument parsing errors
**Cause**: Command syntax errors or version mismatches

**Solutions**:
```bash
# Check command syntax
python -m ai_onboard help <command>

# Use correct argument names
python -m ai_onboard ux feedback --score 4 --context "test"  # Correct
# Not: python -m ai_onboard ux feedback --rating 4 --situation "test"

# Update to latest version
git pull origin main
pip install -e .

# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### Performance Issues

#### Issue: Commands run slowly
**Symptoms**: Long execution times for simple commands
**Cause**: Resource constraints, large data files, or inefficient operations

**Solutions**:
```bash
# Profile command performance
python -m ai_onboard debug profile <command>

# Clean up large data files
python -m ai_onboard cleanup --cache --logs --temp

# Optimize configuration
python -m ai_onboard config optimize --performance

# Use lightweight operations
python -m ai_onboard dashboard --quick
python -m ai_onboard status --brief
```

#### Issue: High memory usage
**Symptoms**: System becomes slow, out of memory errors
**Cause**: Memory leaks or processing large datasets

**Solutions**:
```bash
# Monitor memory usage
python -m ai_onboard debug memory --monitor

# Clear caches and temporary data
python -m ai_onboard cleanup --aggressive

# Use streaming operations for large datasets
python -m ai_onboard unified-metrics query --stream

# Restart AI Onboard services
python -m ai_onboard api stop
python -m ai_onboard api start
```

### Integration Issues

#### Issue: Cursor AI integration not working
**Symptoms**: Cursor commands fail or don't connect
**Cause**: Configuration issues or Cursor not installed

**Solutions**:
```bash
# Check Cursor installation
cursor --version

# Reinitialize Cursor integration
python -m ai_onboard cursor init --force

# Test connection
python -m ai_onboard cursor status --test-connection

# Update Cursor configuration
python -m ai_onboard cursor config --reset
python -m ai_onboard cursor config --agent-profile "developer"
```

#### Issue: API server won't start
**Symptoms**: API commands fail, port conflicts
**Cause**: Port already in use or permission issues

**Solutions**:
```bash
# Check port availability
netstat -an | grep 8000
lsof -i :8000

# Use different port
python -m ai_onboard api start --port 8001

# Kill existing processes on port
sudo kill -9 $(lsof -t -i:8000)

# Check API configuration
python -m ai_onboard api config show
python -m ai_onboard api test --local
```

#### Issue: Metrics collection not working
**Symptoms**: No metrics data, empty dashboards
**Cause**: Metrics system not initialized or permission issues

**Solutions**:
```bash
# Initialize metrics system
python -m ai_onboard unified-metrics setup --force

# Check metrics configuration
python -m ai_onboard unified-metrics config show

# Test metrics collection
python -m ai_onboard unified-metrics test --collect-sample

# Reset metrics database
python -m ai_onboard unified-metrics reset --confirm
```

### UX & Interface Issues

#### Issue: No UX interventions appearing
**Symptoms**: No helpful suggestions or error recovery
**Cause**: UX system disabled or misconfigured

**Solutions**:
```bash
# Check UX configuration
python -m ai_onboard ux config show

# Enable UX enhancements
python -m ai_onboard ux config update \
  --enable-proactive-help true \
  --enable-error-recovery true

# Test UX system
python -m ai_onboard ux test --trigger-error
python -m ai_onboard ux interventions list

# Reset UX system
python -m ai_onboard ux config reset --confirm
```

#### Issue: Dashboard not displaying correctly
**Symptoms**: Broken layout, missing widgets, formatting issues
**Cause**: Terminal compatibility or configuration issues

**Solutions**:
```bash
# Check terminal compatibility
echo $TERM
tput colors

# Use simple dashboard mode
python -m ai_onboard dashboard --simple

# Reset dashboard configuration
python -m ai_onboard dashboard config reset

# Use alternative output format
python -m ai_onboard dashboard --format json
python -m ai_onboard dashboard --export-html > dashboard.html
```

## 🔧 Advanced Troubleshooting

### Debugging Mode

#### Enable Comprehensive Debugging
```bash
# Enable debug mode globally
export AI_ONBOARD_DEBUG=1

# Run commands with verbose output
python -m ai_onboard <command> --verbose --debug

# Enable trace logging
python -m ai_onboard debug trace --enable
python -m ai_onboard <command>
python -m ai_onboard debug trace --show
```

#### Log Analysis
```bash
# View recent logs
python -m ai_onboard debug logs --recent

# Search logs for specific errors
python -m ai_onboard debug logs --search "AttributeError"

# Export logs for analysis
python -m ai_onboard debug logs --export debug_logs.txt

# Clear old logs
python -m ai_onboard debug logs --clear --older-than 7d
```

### Configuration Debugging

#### Configuration Validation
```bash
# Validate all configuration files
python -m ai_onboard config validate --all

# Show configuration hierarchy
python -m ai_onboard config show --hierarchy

# Check for configuration conflicts
python -m ai_onboard config conflicts --resolve

# Export configuration for analysis
python -m ai_onboard config export --format yaml > config_backup.yaml
```

#### Reset Configuration
```bash
# Reset specific components
python -m ai_onboard config reset --component ux
python -m ai_onboard config reset --component metrics
python -m ai_onboard config reset --component cursor

# Full system reset (use carefully)
python -m ai_onboard config reset --all --confirm

# Restore from backup
python -m ai_onboard config restore config_backup.yaml
```

### Data Recovery

#### Backup and Restore
```bash
# Create full backup
python -m ai_onboard backup create --name "before_troubleshooting"

# List available backups
python -m ai_onboard backup list

# Restore from backup
python -m ai_onboard backup restore --name "before_troubleshooting"

# Export project data
python -m ai_onboard export --format json --output project_data.json
```

#### Data Validation and Repair
```bash
# Validate data integrity
python -m ai_onboard validate --data-integrity

# Repair corrupted data
python -m ai_onboard repair --auto-fix --backup-first

# Rebuild indexes and caches
python -m ai_onboard rebuild --indexes --caches

# Migrate data format (if needed)
python -m ai_onboard migrate --from-version 0.1.0 --to-version 0.2.0
```

## 🆘 Getting Additional Help

### Built-in Help Resources
```bash
# Context-aware help system
python -m ai_onboard help --context troubleshooting

# Error-specific help
python -m ai_onboard help --error "JSONDecodeError"

# Interactive troubleshooting wizard
python -m ai_onboard wizard troubleshoot

# System health recommendations
python -m ai_onboard suggest --focus health
```

### Self-Diagnosis Tools
```bash
# Comprehensive system check
python -m ai_onboard doctor --full-check

# Performance analysis
python -m ai_onboard doctor --performance

# Security audit
python -m ai_onboard doctor --security

# Generate diagnostic report
python -m ai_onboard doctor --report --output diagnostic_report.txt
```

### Community Resources

#### Documentation & Guides
- [Getting Started Guide](getting-started.md) - Basic setup and usage
- [Command Reference](commands/README.md) - Complete command documentation
- [Workflow Guides](workflows/README.md) - Step-by-step workflow instructions

#### Support Channels
- **GitHub Issues**: Report bugs and request features
- **Community Discussions**: Get help from other users
- **Documentation Updates**: Contribute improvements to guides

## 🎯 Prevention Best Practices

### Regular Maintenance
```bash
# Weekly health check (5 minutes)
python -m ai_onboard status --comprehensive
python -m ai_onboard validate --report
python -m ai_onboard cleanup --routine

# Monthly optimization (15 minutes)
python -m ai_onboard kaizen run-cycle
python -m ai_onboard config optimize
python -m ai_onboard backup create --monthly
```

### Monitoring & Alerts
```bash
# Set up health monitoring
python -m ai_onboard unified-metrics alert \
  --health-check daily \
  --performance-threshold 0.8 \
  --error-rate-threshold 0.05

# Configure proactive notifications
python -m ai_onboard config alerts \
  --disk-space-warning 80% \
  --memory-usage-warning 85% \
  --error-rate-alert 5%
```

### Best Practices Checklist
- ✅ **Regular Backups**: Create backups before major changes
- ✅ **Configuration Validation**: Validate config after changes
- ✅ **Log Monitoring**: Check logs regularly for early warning signs
- ✅ **Performance Monitoring**: Track system performance trends
- ✅ **Update Management**: Keep AI Onboard updated to latest version
- ✅ **Documentation**: Document custom configurations and workflows

## 🔍 Error Code Reference

### Common Error Codes
- **E001**: Configuration file not found or corrupted
- **E002**: Invalid project charter format
- **E003**: Plan generation failed due to insufficient context
- **E004**: Alignment check failed with low score
- **E005**: Validation errors in project structure
- **E010**: API server startup failed
- **E011**: Cursor integration connection failed
- **E012**: Metrics collection system error
- **E020**: UX system initialization failed
- **E021**: User preference system error
- **E030**: Database connection or corruption error

### Error Resolution Quick Reference
```bash
# Configuration errors (E001)
python -m ai_onboard config reset --component <component>

# Charter/Planning errors (E002-E004)
python -m ai_onboard charter --ai-assist --validate
python -m ai_onboard plan --scenarios conservative

# Integration errors (E010-E012)
python -m ai_onboard <service> init --force
python -m ai_onboard <service> status --test

# UX system errors (E020-E021)
python -m ai_onboard ux config reset --confirm
python -m ai_onboard user-prefs reset --user default

# Data errors (E030)
python -m ai_onboard backup restore --latest
python -m ai_onboard repair --data-integrity
```

---

## 🎯 When All Else Fails

### Nuclear Options (Use with Caution)
```bash
# Complete system reset
python -m ai_onboard reset --nuclear --backup-first --confirm

# Fresh installation
rm -rf .ai_onboard
pip uninstall ai-onboard
pip install -e . --force-reinstall

# Start completely over
python -m ai_onboard init --fresh-start --guided-setup
```

### Getting Expert Help
If you're still experiencing issues:

1. **Generate Diagnostic Report**:
   ```bash
   python -m ai_onboard doctor --full-report --output issue_report.txt
   ```

2. **Collect System Information**:
   ```bash
   python -m ai_onboard debug system-info --output system_info.txt
   ```

3. **Create Minimal Reproduction**:
   - Document exact steps to reproduce the issue
   - Include error messages and command output
   - Note your system configuration and environment

4. **Submit Detailed Issue Report**:
   - Include diagnostic report and system information
   - Describe expected vs. actual behavior
   - Provide minimal reproduction steps

---

**💡 Remember**: AI Onboard's intelligent error handling learns from issues to provide better guidance over time. Your troubleshooting experiences help improve the system for everyone!

