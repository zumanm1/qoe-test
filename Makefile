# QoE Tool - Testing and Quality Makefile
# =====================================

# Variables
PYTHON = python3
PIP = pip3
VENV = venv
VENV_ACTIVATE = $(VENV)/bin/activate
APP_DIR = app
TEST_DIR = tests

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help install test test-python test-js lint format quality-check coverage clean

# Default target
help: ## Show this help message
	@echo "$(BLUE)QoE Tool - Testing and Quality Commands$(NC)"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Setup and Installation
install: ## Install all dependencies
	@echo "$(YELLOW)Installing Python dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(YELLOW)Installing Node.js dependencies...$(NC)"
	npm install
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

venv: ## Create virtual environment
	@echo "$(YELLOW)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)Virtual environment created. Activate with: source $(VENV_ACTIVATE)$(NC)"

# Testing
test: test-python test-js ## Run all tests (Python and JavaScript)

test-python: ## Run Python tests with pytest
	@echo "$(YELLOW)Running Python tests...$(NC)"
	pytest -v --tb=short
	@echo "$(GREEN)Python tests completed!$(NC)"

test-python-cov: ## Run Python tests with coverage
	@echo "$(YELLOW)Running Python tests with coverage...$(NC)"
	pytest --cov=$(APP_DIR) --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)Python tests with coverage completed!$(NC)"
	@echo "$(BLUE)Coverage report generated in htmlcov/index.html$(NC)"

test-js: ## Run JavaScript/Puppeteer tests
	@echo "$(YELLOW)Running JavaScript E2E tests...$(NC)"
	npm test
	@echo "$(GREEN)JavaScript tests completed!$(NC)"

test-single: ## Run a single test file (usage: make test-single FILE=test_file.py)
	@echo "$(YELLOW)Running single test: $(FILE)$(NC)"
	pytest -v $(FILE)

# Code Quality and Linting
lint: lint-python lint-js ## Run all linting checks

lint-python: ## Run Python linting with flake8
	@echo "$(YELLOW)Running Python linting (flake8)...$(NC)"
	flake8 $(APP_DIR) *.py
	@echo "$(GREEN)Python linting completed!$(NC)"

lint-js: ## Run JavaScript linting (if configured)
	@echo "$(YELLOW)JavaScript linting not configured yet$(NC)"

# Code Formatting
format: format-python ## Format all code

format-python: ## Format Python code with black
	@echo "$(YELLOW)Formatting Python code with black...$(NC)"
	black $(APP_DIR) *.py
	@echo "$(GREEN)Python code formatted!$(NC)"

format-imports: ## Sort Python imports with isort
	@echo "$(YELLOW)Sorting Python imports with isort...$(NC)"
	isort $(APP_DIR) *.py
	@echo "$(GREEN)Python imports sorted!$(NC)"

# Comprehensive Quality Check
quality-check: lint format test-python-cov ## Run comprehensive quality check
	@echo "$(GREEN)Quality check completed!$(NC)"

# Coverage
coverage: ## Generate coverage report
	@echo "$(YELLOW)Generating coverage report...$(NC)"
	pytest --cov=$(APP_DIR) --cov-report=html --cov-report=xml --cov-report=term
	@echo "$(GREEN)Coverage report generated!$(NC)"
	@echo "$(BLUE)HTML report: htmlcov/index.html$(NC)"
	@echo "$(BLUE)XML report: coverage.xml$(NC)"

coverage-open: coverage ## Generate and open coverage report
	@echo "$(YELLOW)Opening coverage report...$(NC)"
	open htmlcov/index.html || xdg-open htmlcov/index.html

# Performance Testing
test-perf: ## Run performance tests
	@echo "$(YELLOW)Running performance tests...$(NC)"
	pytest -v -m "not slow" --durations=10
	@echo "$(GREEN)Performance tests completed!$(NC)"

# Integration Testing
test-integration: ## Run integration tests
	@echo "$(YELLOW)Running integration tests...$(NC)"
	pytest -v -m integration
	@echo "$(GREEN)Integration tests completed!$(NC)"

# Security Checks
security-check: ## Run security checks with bandit
	@echo "$(YELLOW)Running security checks...$(NC)"
	bandit -r $(APP_DIR) -f json -o security-report.json || true
	bandit -r $(APP_DIR)
	@echo "$(GREEN)Security check completed!$(NC)"

# Database Testing
test-db: ## Run database-related tests
	@echo "$(YELLOW)Running database tests...$(NC)"
	pytest -v -k "test_database or test_model"
	@echo "$(GREEN)Database tests completed!$(NC)"

# Clean up
clean: ## Clean up generated files
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f coverage.xml
	rm -f security-report.json
	rm -f *.png  # Remove test screenshots
	@echo "$(GREEN)Cleanup completed!$(NC)"

# Development helpers
check: ## Quick development check (lint + basic tests)
	@echo "$(YELLOW)Running quick development check...$(NC)"
	flake8 $(APP_DIR) --count --select=E9,F63,F7,F82 --show-source --statistics
	pytest --tb=line --maxfail=5 -q

watch-tests: ## Watch for file changes and run tests
	@echo "$(YELLOW)Watching for changes... (Press Ctrl+C to stop)$(NC)"
	while true; do \
		inotifywait -e modify,create,delete -r $(APP_DIR) $(TEST_DIR) 2>/dev/null; \
		clear; \
		make check; \
		sleep 1; \
	done

# CI/CD helpers
ci-test: ## Run tests in CI environment
	@echo "$(YELLOW)Running CI tests...$(NC)"
	pytest --cov=$(APP_DIR) --cov-report=xml --cov-fail-under=80 --tb=short

ci-quality: ## Run quality checks for CI
	@echo "$(YELLOW)Running CI quality checks...$(NC)"
	flake8 $(APP_DIR) *.py
	black --check $(APP_DIR) *.py
	isort --check-only $(APP_DIR) *.py

# Documentation
docs: ## Generate documentation
	@echo "$(YELLOW)Documentation generation not configured yet$(NC)"

# Version information
info: ## Show tool versions
	@echo "$(BLUE)Tool Versions:$(NC)"
	@echo "Python: $$(python3 --version)"
	@echo "Pip: $$(pip3 --version)"
	@echo "Pytest: $$(pytest --version 2>/dev/null || echo 'Not installed')"
	@echo "Flake8: $$(flake8 --version 2>/dev/null || echo 'Not installed')"
	@echo "Black: $$(black --version 2>/dev/null || echo 'Not installed')"
	@echo "Coverage: $$(coverage --version 2>/dev/null || echo 'Not installed')"
	@echo "Node.js: $$(node --version 2>/dev/null || echo 'Not installed')"
	@echo "NPM: $$(npm --version 2>/dev/null || echo 'Not installed')"
	@echo "Jest: $$(npx jest --version 2>/dev/null || echo 'Not installed')"
