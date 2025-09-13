# AI Onboard Development Makefile

.PHONY: help install dev-install test lint format security ci-local clean

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install package dependencies
	pip install -e .

dev-install:  ## Install development dependencies
	pip install -e .[dev]
	python scripts/setup_local_ci.py

test:  ## Run all tests
	python -m pytest tests/ -v

test-unit:  ## Run unit tests only
	python -m pytest tests/unit/ -v

test-integration:  ## Run integration tests only
	python -m pytest tests/integration/ -v

test-smoke:  ## Run smoke tests only
	python -m pytest tests/smoke/ -v

lint:  ## Run linting checks
	python -m flake8 ai_onboard/ tests/ scripts/
	python -m mypy --config-file=config/mypy.ini ai_onboard/

format:  ## Format code
	python -m black ai_onboard/ tests/ scripts/
	python -m isort ai_onboard/ tests/ scripts/

format-check:  ## Check code formatting
	python -m black --check ai_onboard/ tests/ scripts/
	python -m isort --check-only ai_onboard/ tests/ scripts/

security:  ## Run security checks
	python -m bandit -r ai_onboard/
	python -m safety check

ci-local:  ## Run full local CI validation
	python scripts/local_ci_validation.py

ci-fast:  ## Run fast local CI validation
	python scripts/local_ci_validation.py --step quality

validate-env:  ## Validate development environment
	python scripts/validate_dev_env.py

validate-structure:  ## Validate project structure
	python scripts/validate_project_structure.py

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

pre-commit-run:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

pre-commit-update:  ## Update pre-commit hooks
	pre-commit autoupdate
