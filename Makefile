
.PHONY: help setup train run run-docker test test-unit test-bdd lint format clean build build-run push deploy uninstall delete-namespace reset install

# Variables
IMAGE_NAME = iris-classifier-api
IMAGE_TAG ?= latest
DOCKER_REGISTRY ?= docker.io
DOCKER_REPO ?= hrishin
KUBERNETES_NAMESPACE ?= ml-models
RELEASE_NAME ?= iris-app
NAMESPACE ?= iris-ns

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
	@poetry run python -m model.train

# Run locally
run:
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
	@docker build -t $(DOCKER_REGISTRY)/$(DOCKER_REPO)/$(IMAGE_NAME):$(IMAGE_TAG) .

build-run: build
	@echo "Running container"
	@docker kill iris-model 2>/dev/null || true
	@docker rm -f iris-model 2>/dev/null || true
	@docker run -d --name iris-model -p 9000:8000 $(DOCKER_REGISTRY)/$(DOCKER_REPO)/$(IMAGE_NAME):$(IMAGE_TAG)
	@echo "Access the serving model http://0.0.0.0:9000/docs"

# Clean
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf dist
	@rm -rf build
	@rm -rf *.egg-info
	@rm -rf .pytest_cache
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

uninstall:
	@echo "Uninstalling Helm release '$(RELEASE_NAME)' in namespace '$(NAMESPACE)'..."
	helm uninstall $(RELEASE_NAME) --namespace $(NAMESPACE) || true

delete-namespace:
	@echo "Deleting namespace '$(NAMESPACE)'..."
	kubectl delete namespace $(NAMESPACE) || true

reset: uninstall delete-namespace
	@echo "Reset complete."

install: reset
	@echo "Installing Helm chart..."
	helm install $(RELEASE_NAME) ./charts/iris-classifier --namespace $(NAMESPACE) --create-namespace --wait