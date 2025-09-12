# AI Agent Onboarding Development Container
# This Dockerfile creates a standardized development environment that eliminates
# Windows/Linux differences and provides all necessary tools for development.

FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

# Set the shell to bash with error handling
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    # Build tools
    build-essential \
    gcc \
    g++ \
    make \
    cmake \

    # System utilities
    curl \
    wget \
    unzip \
    zip \
    tree \
    htop \
    jq \

    # Development tools
    vim \
    nano \
    less \
    grep \
    sed \
    awk \

    # Network tools
    net-tools \
    iputils-ping \
    telnet \
    netcat \

    # Process monitoring
    procps \
    psmisc \

    # File system tools
    file \
    findutils \
    rsync \

    # Compression tools
    gzip \
    tar \
    bzip2 \
    xz-utils \

    # SSL/TLS tools
    ca-certificates \
    openssl \

    # Database clients (for potential integrations)
    sqlite3 \

    # Additional development dependencies
    pkg-config \
    libffi-dev \
    libssl-dev \

    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Upgrade pip and install essential Python packages
RUN python -m pip install --upgrade pip setuptools wheel

# Install development and testing tools
RUN python -m pip install \
    # Code formatting and linting
    black==23.12.1 \
    flake8==7.0.0 \
    mypy==1.8.0 \
    isort==5.13.2 \

    # Testing frameworks
    pytest==7.4.4 \
    pytest-cov==4.1.0 \
    pytest-xdist==3.5.0 \
    pytest-mock==3.12.0 \

    # Development tools
    ipython==8.20.0 \
    ipdb==0.13.13 \

    # Documentation
    sphinx==7.2.6 \
    sphinx-rtd-theme==2.0.0 \

    # Performance and profiling
    memory-profiler==0.61.0 \
    line-profiler==4.1.2 \

    # HTTP and API tools
    requests==2.31.0 \
    httpx==0.26.0 \

    # Data processing
    pydantic==2.5.3 \

    # System monitoring
    psutil==5.9.7 \

    # Development utilities
    python-dotenv==1.0.0 \
    rich==13.7.0 \
    typer==0.9.0

# Create workspace directory
WORKDIR /workspace

# Set up git configuration for the container user
USER vscode

# Configure git with safe directory
RUN git config --global --add safe.directory /workspace

# Set up shell environment
RUN echo 'export PS1="\[\e[32m\]ai-onboard-dev\[\e[m\] \[\e[36m\]\w\[\e[m\] \[\e[33m\]\$\[\e[m\] "' >> ~/.bashrc \
    && echo 'export PYTHONPATH="/workspace:$PYTHONPATH"' >> ~/.bashrc \
    && echo 'export AI_ONBOARD_ENV=development' >> ~/.bashrc \
    && echo 'export AI_ONBOARD_DEBUG=true' >> ~/.bashrc

# Add helpful aliases
RUN echo 'alias ll="ls -alF"' >> ~/.bashrc \
    && echo 'alias la="ls -A"' >> ~/.bashrc \
    && echo 'alias l="ls -CF"' >> ~/.bashrc \
    && echo 'alias ..="cd .."' >> ~/.bashrc \
    && echo 'alias ...="cd ../.."' >> ~/.bashrc \
    && echo 'alias grep="grep --color=auto"' >> ~/.bashrc \
    && echo 'alias fgrep="fgrep --color=auto"' >> ~/.bashrc \
    && echo 'alias egrep="egrep --color=auto"' >> ~/.bashrc

# Add AI Onboard specific aliases
RUN echo '# AI Onboard Development Aliases' >> ~/.bashrc \
    && echo 'alias aio="python -m ai_onboard"' >> ~/.bashrc \
    && echo 'alias aio-test="python -m pytest tests/"' >> ~/.bashrc \
    && echo 'alias aio-lint="flake8 ai_onboard/ tests/"' >> ~/.bashrc \
    && echo 'alias aio-format="black ai_onboard/ tests/ && isort ai_onboard/ tests/"' >> ~/.bashrc \
    && echo 'alias aio-type="mypy ai_onboard/"' >> ~/.bashrc \
    && echo 'alias aio-dev="python -m ai_onboard --debug"' >> ~/.bashrc \
    && echo 'alias aio-status="python -m ai_onboard status --comprehensive"' >> ~/.bashrc \
    && echo 'alias aio-validate="python -m ai_onboard validate --report"' >> ~/.bashrc

# Create common development directories
RUN mkdir -p ~/.local/bin \
    && mkdir -p ~/.cache/pip \
    && mkdir -p ~/.vscode-server/extensions

# Set up development environment indicator
RUN echo '#!/bin/bash' > ~/.local/bin/dev-env-info \
    && echo 'echo "🐳 AI Onboard Development Container"' >> ~/.local/bin/dev-env-info \
    && echo 'echo "📍 Python: $(python --version)"' >> ~/.local/bin/dev-env-info \
    && echo 'echo "📁 Workspace: /workspace"' >> ~/.local/bin/dev-env-info \
    && echo 'echo "🔧 Environment: development"' >> ~/.local/bin/dev-env-info \
    && echo 'echo ""' >> ~/.local/bin/dev-env-info \
    && echo 'echo "Quick commands:"' >> ~/.local/bin/dev-env-info \
    && echo 'echo "  aio --help     - AI Onboard help"' >> ~/.local/bin/dev-env-info \
    && echo 'echo "  aio-test       - Run tests"' >> ~/.local/bin/dev-env-info \
    && echo 'echo "  aio-lint       - Run linting"' >> ~/.local/bin/dev-env-info \
    && echo 'echo "  aio-format     - Format code"' >> ~/.local/bin/dev-env-info \
    && echo 'echo "  aio-status     - System status"' >> ~/.local/bin/dev-env-info \
    && chmod +x ~/.local/bin/dev-env-info

# Add development info to shell startup
RUN echo '# Show development environment info on login' >> ~/.bashrc \
    && echo 'if [ -t 1 ]; then' >> ~/.bashrc \
    && echo '    ~/.local/bin/dev-env-info' >> ~/.bashrc \
    && echo 'fi' >> ~/.bashrc

# Switch back to root for final container setup
USER root

# Install additional system tools that might be needed
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    # Additional utilities that might be needed
    strace \
    lsof \

    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Set up proper permissions
RUN chown -R vscode:vscode /home/vscode/.local \
    && chmod -R 755 /home/vscode/.local/bin

# Switch back to vscode user for development
USER vscode

# Set the default working directory
WORKDIR /workspace

# Default command
CMD ["/bin/bash"]

