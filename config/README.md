# Configuration Directory

This directory contains all configuration files for the AI Onboard Lite project.

## Structure

`
config/
 mypy.ini                    # Type checking configuration
 pre-commit-config.yaml      # Pre-commit hooks configuration
 tox.ini                     # Testing configuration
 dev/                        # Development environment configs
    dev-config.yaml         # Original development config
    environment.yaml        # Development environment settings
 ci/                         # CI/CD environment configs
    environment.yaml        # CI environment settings
 prod/                       # Production environment configs
     environment.yaml        # Production environment settings
`

## Environment Configuration

Each environment directory contains an environment.yaml file with environment-specific settings:

- **dev/**: Development environment with debug features enabled
- **ci/**: CI/CD environment optimized for testing
- **prod/**: Production environment with security and monitoring features

## Usage

The application can load environment-specific configuration based on the ENVIRONMENT variable:

`ash
# Development
export ENVIRONMENT=dev
python -m ai_onboard ...

# CI/CD
export ENVIRONMENT=ci
python -m ai_onboard ...

# Production
export ENVIRONMENT=prod
python -m ai_onboard ...
`

## Adding New Environments

To add a new environment:

1. Create a new directory under config/
2. Add an environment.yaml file with environment-specific settings
3. Update any environment detection logic in the application code

## Configuration Loading

The configuration system loads files in this order:
1. Base configuration (hardcoded defaults)
2. Environment-specific configuration (config/{env}/environment.yaml)
3. Local overrides (.env files, not committed to git)
