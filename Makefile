
.PHONY: help setup train run run-docker test test-unit test-bdd lint format clean build push deploy

# Variables
IMAGE_NAME = iris-classifier-api
IMAGE_TAG ?= latest
DOCKER_REGISTRY ?= docker.io
KUBERNETES_NAMESPACE ?= ml-models
MODEL_VERSION ?= ""

# Help
help:
	@echo "Available commands:"
	@echo "  help        - Show this help message"
	@echo "  setup       - Set up the development environment"
	@echo "  train       - Train the ML model"
	@echo "  run         - Run the API locally"
	@echo "  test        - Run all tests"
	@echo "  test-bdd    - Run BDD tests"
	@echo "  lint        - Run code linting"
	@echo "  format      - Format code"
	@echo "  build   	 - Build container image"
	@echo "  clean       - Clean build artifacts"

# Setup
setup:
	@echo "Setting up development environment..."
	@pip install poetry
	@poetry install
	@mkdir -p artifacts
	@mkdir -p data

# Train model
train: setup
	@echo "Training ML model..."
	@poetry run python -m model.train --model-version=$(MODEL_VERSION)

# Run locally
run: train
	@echo "Running API locally..."
	@poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test
test: test-bdd

test-bdd:
	@echo "Running BDD tests..."
	@poetry run pytest tests/features/ -v

# Lint
lint:
	@echo "Running linters..."
	@poetry run flake8 app model tests
	@poetry run mypy app model

# Format
format:
	@echo "Formatting code..."
	@poetry run black app model tests
	@poetry run isort app model tests

# Container
build: train
	@echo "Building container image"
	@docker build -t $(DOCKER_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG) .

# Clean
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf dist
	@rm -rf build
	@rm -rf *.egg-info
	@rm -rf .pytest_cache
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
