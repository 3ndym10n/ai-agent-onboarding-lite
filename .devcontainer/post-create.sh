#!/bin/bash

# AI Onboard Development Container - Post-Create Setup Script
# This script runs after the development container is created to set up the
# development environment and install the AI Onboard package.

set -e  # Exit on any error

echo "🚀 Setting up AI Onboard development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Are we in the right directory?"
    exit 1
fi

print_status "Installing AI Onboard in development mode..."

# Install the package in development mode with all dependencies
pip install -e ".[dev]" || {
    print_error "Failed to install AI Onboard in development mode"
    exit 1
}

print_success "AI Onboard installed successfully"

# Verify installation
print_status "Verifying installation..."
python -m ai_onboard --version || {
    print_error "AI Onboard installation verification failed"
    exit 1
}

print_success "Installation verified"

# Set up pre-commit hooks if available
if [ -f ".pre-commit-config.yaml" ]; then
    print_status "Setting up pre-commit hooks..."
    pip install pre-commit
    pre-commit install || {
        print_warning "Failed to install pre-commit hooks (non-critical)"
    }
    print_success "Pre-commit hooks installed"
fi

# Create development directories
print_status "Creating development directories..."
mkdir -p .ai_onboard/logs
mkdir -p .ai_onboard/cache
mkdir -p .ai_onboard/temp
mkdir -p tests/data
print_success "Development directories created"

# Set up development configuration
print_status "Setting up development configuration..."

# Create development environment file if it doesn't exist
if [ ! -f ".env.development" ]; then
    cat > .env.development << EOF
# AI Onboard Development Environment Configuration
AI_ONBOARD_ENV=development
AI_ONBOARD_DEBUG=true
AI_ONBOARD_LOG_LEVEL=DEBUG
AI_ONBOARD_CONFIG=dev-config.yaml

# Disable gates for development
AI_ONBOARD_GATES_ENABLED=false

# Development paths
AI_ONBOARD_DATA_DIR=.ai_onboard
AI_ONBOARD_LOGS_DIR=.ai_onboard/logs
AI_ONBOARD_CACHE_DIR=.ai_onboard/cache
AI_ONBOARD_TEMP_DIR=.ai_onboard/temp

# API server settings
AI_ONBOARD_API_HOST=0.0.0.0
AI_ONBOARD_API_PORT=8000

# Testing configuration
AI_ONBOARD_TEST_MODE=true
AI_ONBOARD_MOCK_SERVICES=true
EOF
    print_success "Development environment file created"
else
    print_status "Development environment file already exists"
fi

# Run initial system validation
print_status "Running initial system validation..."
python -m ai_onboard validate --quick || {
    print_warning "System validation had warnings (this is normal for a fresh setup)"
}

# Run a quick test to ensure everything works
print_status "Running quick functionality test..."
python -m ai_onboard status --brief || {
    print_warning "Status check had issues (this might be normal for a fresh setup)"
}

# Set up git configuration if not already configured
if [ -z "$(git config --global user.name)" ]; then
    print_status "Git user not configured. Please set up git:"
    echo "  git config --global user.name 'Your Name'"
    echo "  git config --global user.email 'your.email@example.com'"
fi

# Display development environment information
echo ""
echo "🎉 AI Onboard Development Environment Setup Complete!"
echo ""
echo "📋 Quick Start Guide:"
echo "  • Run tests:           aio-test"
echo "  • Check code quality:  aio-lint"
echo "  • Format code:         aio-format"
echo "  • Type checking:       aio-type"
echo "  • System status:       aio-status"
echo "  • Full validation:     aio-validate"
echo "  • Help:                aio --help"
echo ""
echo "🔧 Development Tools Available:"
echo "  • Python $(python --version | cut -d' ' -f2)"
echo "  • pip $(pip --version | cut -d' ' -f2)"
echo "  • pytest $(pytest --version | head -n1)"
echo "  • black $(black --version | head -n1)"
echo "  • flake8 $(flake8 --version)"
echo "  • mypy $(mypy --version)"
echo ""
echo "📁 Project Structure:"
echo "  • Source code:         ai_onboard/"
echo "  • Tests:               tests/"
echo "  • Documentation:       docs/"
echo "  • Development data:    .ai_onboard/"
echo "  • Configuration:       dev-config.yaml"
echo ""
echo "🐳 Container Features:"
echo "  • Standardized Python environment"
echo "  • Pre-installed development tools"
echo "  • Consistent cross-platform behavior"
echo "  • Persistent volumes for caches and history"
echo "  • VS Code integration with extensions"
echo ""

# Check for any additional setup that might be needed
print_status "Checking for additional setup requirements..."

# Check if there are any specific project requirements
if [ -f "scripts/validate_dev_env.py" ]; then
    print_status "Running development environment validation..."
    python scripts/validate_dev_env.py || {
        print_warning "Development environment validation had issues"
    }
fi

# Final status check
print_status "Final environment check..."
echo "Environment variables:"
echo "  PYTHONPATH: $PYTHONPATH"
echo "  AI_ONBOARD_ENV: $AI_ONBOARD_ENV"
echo "  AI_ONBOARD_DEBUG: $AI_ONBOARD_DEBUG"
echo ""

print_success "🎯 Development environment is ready for AI Onboard development!"
print_status "Happy coding! 🚀"

