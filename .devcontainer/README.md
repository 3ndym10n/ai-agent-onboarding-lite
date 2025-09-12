# AI Onboard Development Container

This directory contains the development container configuration for AI Agent Onboarding. The development container provides a standardized, reproducible development environment that eliminates differences between Windows, Linux, and macOS development setups.

## 🎯 Features

### Standardized Environment
- **Consistent Python 3.11** environment across all platforms
- **Pre-installed development tools** (black, flake8, mypy, pytest, etc.)
- **VS Code integration** with recommended extensions
- **Git configuration** and SSH key mounting
- **Persistent volumes** for caches and command history

### Development Tools
- **Code formatting**: black, isort
- **Linting**: flake8, mypy
- **Testing**: pytest with coverage
- **Debugging**: ipdb, ipython
- **Documentation**: sphinx
- **Performance**: memory-profiler, line-profiler

### AI Onboard Specific
- **Pre-configured aliases** for common commands
- **Development environment variables**
- **Automatic package installation** in development mode
- **System validation** on container creation
- **Quick access commands** (aio-test, aio-lint, etc.)

## 🚀 Quick Start

### Prerequisites
- **Docker Desktop** installed and running
- **VS Code** with the Remote-Containers extension

### Using the Development Container

1. **Open in VS Code**:
   ```bash
   code .
   ```

2. **Open in Container**:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Remote-Containers: Reopen in Container"
   - Select the command and wait for the container to build

3. **Verify Setup**:
   ```bash
   # The container will automatically show environment info
   # You can also run:
   aio --help
   aio-status
   ```

### Alternative: Docker Compose

For advanced development with additional services:

```bash
# Build and start all services
docker-compose -f .devcontainer/docker-compose.yml up -d

# Access the development container
docker-compose -f .devcontainer/docker-compose.yml exec ai-onboard-dev bash
```

## 🔧 Configuration

### Container Configuration
- **Base Image**: `mcr.microsoft.com/devcontainers/python:1-3.11-bullseye`
- **User**: `vscode` (non-root for security)
- **Working Directory**: `/workspace`
- **Python Path**: `/workspace` (automatically configured)

### VS Code Extensions
The container automatically installs:
- **Python development**: Python, Black, Flake8, MyPy, isort
- **Testing**: pytest, Test Explorer
- **Git**: GitLens, GitHub integration
- **Documentation**: Markdown tools
- **AI assistance**: GitHub Copilot (if available)

### Environment Variables
```bash
AI_ONBOARD_ENV=development
AI_ONBOARD_DEBUG=true
PYTHONPATH=/workspace
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
```

## 🛠️ Development Workflow

### Common Commands
```bash
# AI Onboard commands (using aliases)
aio --help              # Show help
aio-status             # System status
aio-validate           # Full validation
aio-dev                # Run with debug mode

# Development commands
aio-test               # Run tests
aio-lint               # Run linting
aio-format             # Format code
aio-type               # Type checking

# Direct commands
python -m ai_onboard status
python -m pytest tests/
flake8 ai_onboard/ tests/
black ai_onboard/ tests/
mypy ai_onboard/
```

### Testing
```bash
# Run all tests
aio-test

# Run specific test file
python -m pytest tests/test_specific.py

# Run with coverage
python -m pytest tests/ --cov=ai_onboard --cov-report=html

# Run tests in parallel
python -m pytest tests/ -n auto
```

### Code Quality
```bash
# Format code
aio-format

# Check linting
aio-lint

# Type checking
aio-type

# All quality checks
aio-format && aio-lint && aio-type
```

## 📁 Directory Structure

```
.devcontainer/
├── devcontainer.json      # Main container configuration
├── Dockerfile            # Container image definition
├── docker-compose.yml    # Multi-service development setup
├── post-create.sh        # Post-creation setup script
├── README.md            # This file
└── wiremock/            # Mock service configurations
```

## 🔌 Ports and Services

### Forwarded Ports
- **8000**: AI Onboard API server
- **8080**: Alternative API port
- **3000**: Development server
- **5000**: Debug server

### Additional Services (Docker Compose)
- **Redis** (6379): Caching and message queuing
- **PostgreSQL** (5432): Database for testing
- **WireMock** (8090): Mock external services

## 🎨 Customization

### Adding Extensions
Edit `.devcontainer/devcontainer.json`:
```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        "your.extension.id"
      ]
    }
  }
}
```

### Environment Variables
Add to `containerEnv` in `devcontainer.json`:
```json
{
  "containerEnv": {
    "YOUR_VAR": "value"
  }
}
```

### System Packages
Add to `Dockerfile`:
```dockerfile
RUN apt-get update && apt-get install -y \
    your-package \
    && apt-get clean
```

### Python Packages
Add to `Dockerfile` or use `requirements-dev.txt`:
```dockerfile
RUN pip install your-package
```

## 🐛 Troubleshooting

### Container Won't Start
1. **Check Docker**: Ensure Docker Desktop is running
2. **Check Resources**: Ensure sufficient memory/disk space
3. **Rebuild Container**: `Ctrl+Shift+P` → "Remote-Containers: Rebuild Container"

### Package Installation Issues
```bash
# Reinstall in development mode
pip install -e ".[dev]"

# Clear pip cache
pip cache purge

# Upgrade pip
python -m pip install --upgrade pip
```

### Permission Issues
```bash
# Fix ownership (run as root if needed)
chown -R vscode:vscode /workspace/.ai_onboard

# Check current user
whoami
id
```

### VS Code Extension Issues
```bash
# Reinstall extensions
code --list-extensions
code --uninstall-extension extension.id
code --install-extension extension.id
```

### Git Configuration
```bash
# Configure git in container
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Check git config
git config --list
```

## 🔒 Security

### Non-Root User
The container runs as the `vscode` user (non-root) for security.

### Volume Mounts
- Git credentials are mounted read-only
- SSH keys are mounted read-only
- Workspace is mounted with cached consistency

### Network Security
- Services are isolated in a Docker network
- Only necessary ports are exposed

## 📊 Performance

### Optimizations
- **Multi-stage builds** for smaller images
- **Cached mounts** for better performance
- **Persistent volumes** for caches
- **Parallel test execution** support

### Resource Usage
- **Memory**: ~2GB recommended
- **Disk**: ~5GB for full environment
- **CPU**: 2+ cores recommended

## 🚀 Advanced Usage

### Multiple Containers
```bash
# Run multiple development environments
docker-compose -f .devcontainer/docker-compose.yml up --scale ai-onboard-dev=2
```

### Custom Services
Add services to `docker-compose.yml` for:
- **Message queues** (RabbitMQ, Apache Kafka)
- **Databases** (MongoDB, InfluxDB)
- **External APIs** (mock services)
- **Monitoring** (Prometheus, Grafana)

### CI/CD Integration
The container configuration can be used in CI/CD:
```yaml
# GitHub Actions example
- name: Setup Development Container
  run: |
    docker build -f .devcontainer/Dockerfile .
    docker run --rm -v $PWD:/workspace ai-onboard-dev aio-test
```

## 📚 Resources

- [VS Code Remote-Containers](https://code.visualstudio.com/docs/remote/containers)
- [Development Containers Specification](https://containers.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [AI Onboard Documentation](../docs/)

---

This development container provides a consistent, powerful development environment for AI Agent Onboarding that works the same way across all platforms and eliminates "works on my machine" issues.

