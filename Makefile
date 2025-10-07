.PHONY: install dev test lint format clean run example-basic example-advanced

# Install package
install:
	pip install -e .

# Install with dev dependencies
dev:
	pip install -e ".[dev]"

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ --cov=unified_server --cov-report=html --cov-report=term

# Lint code
lint:
	ruff check src/ tests/
	mypy src/

# Format code
format:
	black src/ tests/ examples/
	ruff check --fix src/ tests/

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run basic example
example-basic:
	python examples/basic_example.py

# Run advanced example
example-advanced:
	python examples/advanced_example.py

# Run server directly
run:
	python -m unified_server

# Build distribution
build:
	python -m build

# Install from source
install-local:
	pip install -e .

# Help
help:
	@echo "Available commands:"
	@echo "  make install          - Install package"
	@echo "  make dev              - Install with dev dependencies"
	@echo "  make test             - Run tests"
	@echo "  make test-cov         - Run tests with coverage"
	@echo "  make lint             - Lint code"
	@echo "  make format           - Format code"
	@echo "  make clean            - Clean build artifacts"
	@echo "  make example-basic    - Run basic example"
	@echo "  make example-advanced - Run advanced example"
	@echo "  make run              - Run server"
	@echo "  make build            - Build distribution"