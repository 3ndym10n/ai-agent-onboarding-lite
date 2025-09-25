# CI/CD Workflows Documentation

## Overview

This document describes the comprehensive CI/CD (Continuous Integration/Continuous Deployment) workflows and processes for the ai-onboard project. The system includes automated testing, quality gates, security scanning, and deployment automation.

## Workflow Structure

### 1. CI/CD Pipeline (`.github/workflows/ci.yml`)

The main CI/CD pipeline runs on multiple triggers and includes several jobs:

#### Triggers
- **Push events**: All feature branches (`feature/*`, `feat/*`, `bugfix/*`, `hotfix/*`, `release/*`, `fix/*`)
- **Pull requests**: To `main` and `develop` branches
- **Manual dispatch**: Via GitHub Actions UI

#### Jobs

##### Test Job
- **Matrix testing**: Python 3.8, 3.9, 3.10, 3.11, 3.12
- **Dependencies**: Installs project and development dependencies
- **Pre-commit hooks**: Runs all pre-commit checks
- **System tests**: Comprehensive system integration tests
- **Unit tests**: Pytest with coverage reporting
- **AI Agent tests**: Tests the AI Agent Collaboration Protocol
- **Vision system tests**: Tests the Enhanced Vision Interrogation System
- **Environment validation**: Validates development environment setup

##### Quality Job
- **Code formatting**: Black and isort checks
- **Linting**: Flake8 with docstring checks
- **Type checking**: MyPy type validation
- **Code complexity**: Radon complexity and maintainability checks
- **Security scanning**: Bandit and Safety checks

##### Security Job
- **Dependency scanning**: Safety check for known vulnerabilities
- **Code security**: Bandit security analysis
- **Report generation**: JSON reports for security findings

##### Build Job
- **Package building**: Creates distribution packages
- **Package validation**: Twine check for package integrity
- **Artifact upload**: Stores build artifacts

##### Deploy Job
- **PyPI publishing**: Automatically publishes to PyPI on main branch
- **Release creation**: Creates GitHub releases with changelog

##### Release Job
- **Changelog generation**: Automated changelog from git commits
- **Release tagging**: Creates version tags
- **Release notes**: Generates release notes

## Quality Gates

### Pre-commit Hooks (`.pre-commit-config.yaml`)

The pre-commit configuration includes:

#### Standard Hooks
- **Trailing whitespace**: Removes trailing whitespace
- **End of file**: Ensures files end with newline
- **YAML validation**: Validates YAML files
- **Large files**: Prevents large files from being committed
- **Merge conflicts**: Detects merge conflict markers
- **Debug statements**: Removes debug statements
- **Docstring first**: Ensures docstrings are first

#### Code Quality Hooks
- **Black**: Python code formatting
- **isort**: Import sorting with Black profile
- **Flake8**: Linting with docstring checks
- **MyPy**: Type checking with missing import ignore
- **Protected paths**: Custom hook for protected file validation

### Protected Paths

The system includes protection for critical files:
- `.ai_onboard/policies/` - System policies
- `.ai_onboard/charter.json` - Project charter
- `pyproject.toml` - Project configuration
- `README.md` - System documentation
- `AGENTS.md` - Agent guidelines

## Testing Strategy

### Unit Tests
- **Framework**: Pytest
- **Coverage**: Comprehensive coverage reporting
- **Location**: `tests/` directory
- **Reports**: XML and HTML coverage reports

### System Tests
- **Integration tests**: `scripts/testing/test_system.py`
- **Environment validation**: `scripts/maintenance/validate_dev_env.py`
- **AI Agent tests**: `ai_onboard ai-collaboration test`
- **Vision system tests**: `ai_onboard enhanced-vision status`

### Quality Tests
- **Code formatting**: Black and isort
- **Linting**: Flake8 with docstring checks
- **Type checking**: MyPy
- **Security**: Bandit and Safety
- **Complexity**: Radon analysis

## Security Measures

### Dependency Scanning
- **Safety**: Checks for known vulnerabilities in dependencies
- **Automated**: Runs on every build
- **Reporting**: JSON reports for tracking

### Code Security
- **Bandit**: Static analysis for security issues
- **Configuration**: Custom rules for the project
- **Integration**: Part of CI/CD pipeline

### Protected Files
- **Validation**: Pre-commit hooks prevent modification
- **Branch protection**: Feature branches can modify, main cannot
- **Audit trail**: All changes are logged

## Release Management

### Versioning
- **Strategy**: Semantic versioning
- **Automation**: Automated version bumping
- **Tagging**: Git tags for releases

### Changelog Generation
- **Script**: `scripts/maintenance/generate_changelog.py`
- **Format**: Conventional commit messages
- **Categories**: Features, fixes, docs, refactoring, tests
- **Automation**: Generated during release process

### Deployment
- **PyPI**: Automatic publishing to PyPI
- **GitHub Releases**: Automatic release creation
- **Artifacts**: Build artifacts stored for download

## Branch Strategy

### Branch Types
- **main**: Production-ready code
- **develop**: Integration branch
- **feature/***: Feature development
- **feat/***: Feature development (alternative)
- **bugfix/***: Bug fixes
- **hotfix/***: Critical fixes
- **release/***: Release preparation
- **fix/***: General fixes

### Protection Rules
- **main branch**: Protected from direct pushes
- **Feature branches**: Can modify protected files
- **Pull requests**: Required for main branch
- **Status checks**: All CI jobs must pass

## Development Workflow

### Local Development
1. **Setup**: Run `scripts/setup_dev_env.py`
2. **Pre-commit**: Install pre-commit hooks
3. **Development**: Work on feature branch
4. **Testing**: Run `scripts/ci/run_ci_tests.py`
5. **Commit**: Pre-commit hooks run automatically
6. **Push**: Push to feature branch

### CI/CD Process
1. **Trigger**: Push to feature branch
2. **Testing**: All test jobs run in parallel
3. **Quality**: Code quality checks
4. **Security**: Security scanning
5. **Build**: Package building
6. **Deploy**: Automatic deployment on main

### Release Process
1. **Merge**: Merge feature branch to main
2. **Build**: Package building and validation
3. **Deploy**: PyPI publishing
4. **Release**: GitHub release creation
5. **Changelog**: Automated changelog generation

## Monitoring and Reporting

### Test Results
- **Coverage**: Code coverage reports
- **Quality**: Code quality metrics
- **Security**: Security scan results
- **Performance**: Build and test performance

### Notifications
- **GitHub**: Status checks and PR comments
- **Codecov**: Coverage reports
- **PyPI**: Package publication status
- **GitHub Releases**: Release notifications

## Troubleshooting

### Common Issues

#### Pre-commit Hook Failures
```bash
# Fix formatting issues
black ai_onboard/ tests/ scripts/
isort ai_onboard/ tests/ scripts/

# Fix linting issues
flake8 ai_onboard/ tests/ scripts/
```

#### Test Failures
```bash
# Run specific tests
pytest tests/test_specific.py -v

# Run with coverage
pytest tests/ --cov=ai_onboard --cov-report=html
```

#### Security Issues
```bash
# Check dependencies
safety check

# Scan code
bandit -r ai_onboard/
```

#### Build Issues
```bash
# Clean build
rm -rf dist/ build/ *.egg-info/
python -m build

# Validate package
twine check dist/*
```

### Debug Commands

#### Local CI Testing
```bash
# Run all CI tests locally
python scripts/ci/run_ci_tests.py

# Run specific test categories
python scripts/testing/test_system.py
python scripts/maintenance/validate_dev_env.py
```

#### Git Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

## Best Practices

### Commit Messages
- **Format**: Conventional commit format
- **Types**: feat, fix, docs, style, refactor, test, chore
- **Examples**:
  - `feat: add AI agent collaboration protocol`
  - `fix: resolve gate timeout issue`
  - `docs: update CI/CD documentation`

### Code Quality
- **Formatting**: Use Black for consistent formatting
- **Imports**: Use isort for import organization
- **Linting**: Fix all Flake8 warnings
- **Types**: Add type hints with MyPy
- **Docstrings**: Use Google-style docstrings

### Testing
- **Coverage**: Maintain high test coverage
- **Integration**: Test system integration
- **Security**: Regular security scans
- **Performance**: Monitor build times

### Security
- **Dependencies**: Keep dependencies updated
- **Scanning**: Regular security scans
- **Protected files**: Never modify without review
- **Secrets**: Use GitHub secrets for sensitive data

## Future Enhancements

### Planned Features
- **Multi-environment**: Staging and production environments
- **Performance testing**: Automated performance benchmarks
- **Security scanning**: Enhanced security analysis
- **Dependency updates**: Automated dependency updates
- **Release automation**: More sophisticated release management

### Integration Opportunities
- **Slack notifications**: Team notifications
- **JIRA integration**: Issue tracking
- **SonarQube**: Advanced code quality analysis
- **Docker**: Containerized builds and tests

## Conclusion

The CI/CD system provides comprehensive automation for testing, quality assurance, security scanning, and deployment. It ensures code quality, prevents regressions, and automates the release process while maintaining security and reliability.

For more information, see the [Development Guide](DEVELOPMENT.md) and [AI Agent Collaboration Protocol](ai-agent-collaboration-protocol.md).
