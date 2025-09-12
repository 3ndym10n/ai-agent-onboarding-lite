# Development Guide for ai-onboard

This guide covers everything you need to know to develop, test, and contribute to the ai-onboard project.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package installer)

### Setup Development Environment

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-onboard-lite
   ```

2. **Run the automated setup:**
   ```bash
   python scripts/setup_dev_env.py
   ```

3. **Activate the virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

4. **Verify installation:**
   ```bash
   python -m ai_onboard --help
   python scripts/test_system.py
   ```

## 🛠️ Development Tools

### Code Quality

- **Black**: Code formatting
- **Flake8**: Linting and style checking
- **MyPy**: Type checking
- **isort**: Import sorting
- **Pre-commit**: Git hooks for code quality

### Testing

- **pytest**: Test framework
- **Coverage**: Code coverage reporting
- **System Tests**: End-to-end system validation

### IDE Configuration

- **VS Code**: Settings in `.vscode/settings.json`
- **PyCharm**: Configuration in `.idea/`

## 📁 Project Structure

```
ai-onboard-lite/
├── ai_onboard/                 # Main package
│   ├── cli/                   # Command-line interface
│   ├── core/                  # Core functionality
│   ├── plugins/               # Plugin system
│   ├── policies/              # Policy definitions
│   └── schemas/               # Data schemas
├── docs/                      # Documentation
├── examples/                  # Usage examples
├── scripts/                   # Development scripts
├── tests/                     # Test suite
├── .github/workflows/         # CI/CD configuration
├── .pre-commit-config.yaml    # Pre-commit hooks
├── config/
│   └── dev-config.yaml       # Development configuration
└── pyproject.toml            # Project configuration
```

## 🔧 Development Workflow

### 1. Code Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Run pre-commit hooks:**
   ```bash
   pre-commit run --all-files
   ```

4. **Run tests:**
   ```bash
   python scripts/test_system.py
   pytest tests/ -v
   ```

### 2. Testing

#### System Tests
```bash
python scripts/test_system.py
```

#### Unit Tests
```bash
pytest tests/ -v --cov=ai_onboard
```

#### Specific Test Categories
```bash
# Test CLI commands
pytest tests/test_cli_smoke.py -v

# Test with coverage
pytest tests/ --cov=ai_onboard --cov-report=html
```

### 3. Code Quality

#### Format Code
```bash
black ai_onboard/ tests/ scripts/
```

#### Check Linting
```bash
flake8 ai_onboard/ tests/ scripts/
```

#### Type Checking
```bash
mypy ai_onboard/
```

#### Sort Imports
```bash
isort ai_onboard/ tests/ scripts/
```

## 🧪 Testing Strategy

### Test Types

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **System Tests**: End-to-end functionality validation
4. **Smoke Tests**: Basic functionality verification

### Test Data

- Test data is stored in `tests/data/`
- Mock configurations in `tests/fixtures/`
- Test charters in `tests/charters/`

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_cli_smoke.py -v

# With coverage
pytest tests/ --cov=ai_onboard --cov-report=html

# System tests
python scripts/test_system.py
```

## 🔒 Security

### Security Checks

- **Safety**: Check for known security vulnerabilities
- **Bandit**: Security linting for Python code
- **Protected Paths**: Prevent accidental deletion of critical files

### Running Security Checks

```bash
# Safety check
safety check

# Bandit security scan
bandit -r ai_onboard/

# Protected paths check
python scripts/protected_paths_diff.py
```

## 📦 Building and Packaging

### Build Package

```bash
python -m build
```

### Check Package

```bash
twine check dist/*
```

### Install from Source

```bash
pip install -e .
```

## 🚀 Deployment

### CI/CD Pipeline

The project uses GitHub Actions for CI/CD:

1. **Test**: Run tests on multiple Python versions
2. **Security**: Run security checks
3. **Build**: Build the package
4. **Deploy**: Deploy to PyPI (on main branch)

### Manual Deployment

```bash
# Build
python -m build

# Upload to PyPI
twine upload dist/*
```

## 🐛 Debugging

### Debug Mode

Enable debug mode in `config/dev-config.yaml`:

```yaml
development:
  debug: true
  logging:
    level: DEBUG
```

### Debug Tools

- **Smart Debugger**: `ai_onboard.core.smart_debugger`
- **Error Monitor**: `ai_onboard.core.universal_error_monitor`
- **System Profiler**: `ai_onboard.core.profiler`

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Permission Errors**: Check file permissions and paths
3. **Gate Timeouts**: Adjust timeout in `config/dev-config.yaml`

## 📚 Documentation

### Code Documentation

- Use docstrings for all public functions and classes
- Follow Google docstring format
- Include type hints for all parameters and return values

### API Documentation

- API documentation is generated from docstrings
- Use `sphinx` for comprehensive documentation
- Include examples in docstrings

## 🤝 Contributing

### Contribution Guidelines

1. **Fork the repository**
2. **Create a feature branch**
3. **Follow coding standards**
4. **Write tests for new features**
5. **Update documentation**
6. **Submit a pull request**

### Code Review Process

1. **Automated checks** (CI/CD pipeline)
2. **Code review** by maintainers
3. **Testing** in development environment
4. **Approval** and merge

## 🔧 Configuration

### Development Configuration

The `config/dev-config.yaml` file contains development-specific settings:

- **Debug mode**: Enable/disable debug features
- **Logging**: Configure log levels and handlers
- **Testing**: Test mode and mock settings
- **Tools**: Development tool configurations
- **Overrides**: Development-specific overrides

### Environment Variables

- `AI_ONBOARD_DEBUG`: Enable debug mode
- `AI_ONBOARD_CONFIG`: Path to configuration file
- `AI_ONBOARD_LOG_LEVEL`: Logging level

## 📞 Support

### Getting Help

1. **Check the documentation** in `docs/`
2. **Run system tests** to identify issues
3. **Check the issue tracker** for known problems
4. **Create an issue** for new problems

### Development Support

- **System Health**: `python scripts/test_system.py`
- **Debug Mode**: Set `debug: true` in `config/dev-config.yaml`
- **Error Logs**: Check `.ai_onboard/logs/`
- **System Status**: `python -m ai_onboard validate`

## 🎯 Best Practices

### Code Quality

1. **Follow PEP 8** style guidelines
2. **Use type hints** for all functions
3. **Write comprehensive tests**
4. **Document all public APIs**
5. **Use meaningful variable names**

### Development

1. **Test early and often**
2. **Use version control** effectively
3. **Keep commits small and focused**
4. **Write descriptive commit messages**
5. **Review code before submitting**

### Performance

1. **Profile code** for performance bottlenecks
2. **Use appropriate data structures**
3. **Optimize critical paths**
4. **Monitor memory usage**
5. **Test with realistic data sizes**

---

For more information, see the main [README](README.md) or check the [documentation](docs/) directory.
