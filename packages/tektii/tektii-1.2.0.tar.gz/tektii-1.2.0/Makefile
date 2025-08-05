.PHONY: help proto clean install install-dev test format lint type-check check build docs serve-docs

# Default target
help:
	@echo "Available commands:"
	@echo "  make proto        - Generate Python code from protobuf definitions"
	@echo "  make clean        - Clean generated files and caches"
	@echo "  make install      - Install the package"
	@echo "  make install-dev  - Install with development dependencies"
	@echo "  make test         - Run tests with coverage"
	@echo "  make format       - Format code with black and isort"
	@echo "  make lint         - Run linters (flake8, bandit)"
	@echo "  make type-check   - Run mypy type checking"
	@echo "  make check        - Run all quality checks"
	@echo "  make build        - Build distribution packages"
	@echo "  make docs         - Build documentation"
	@echo "  make serve-docs   - Serve documentation locally"

# Generate Python code from protobuf definitions
proto:
	@echo "Pulling latest proto files..."
	@python3 proto/pull_proto.py
	@echo "Generating Python code from proto files..."
	@mkdir -p tektii/strategy/grpc
	@touch tektii/strategy/grpc/__init__.py
	python -m grpc_tools.protoc \
		-I./proto \
		--python_out=./tektii/strategy/grpc \
		--grpc_python_out=./tektii/strategy/grpc \
		--pyi_out=./tektii/strategy/grpc \
		proto/trading/v1/*.proto
	@echo "Moving generated files to correct location..."
	@mv tektii/strategy/grpc/trading/v1/* tektii/strategy/grpc/ 2>/dev/null || true
	@rm -rf tektii/strategy/grpc/trading
	@echo "Fixing imports in generated files..."
	@# Fix imports in all generated files
	@for file in tektii/strategy/grpc/*_pb2*.py; do \
		if [ -f "$$file" ]; then \
			sed -i.bak 's/from trading\.v1 import/from . import/g' "$$file" && rm -f "$$file.bak"; \
			sed -i.bak 's/import trading\.v1\./from . import /g' "$$file" && rm -f "$$file.bak"; \
		fi; \
	done
	@echo "Proto generation complete!"

# Clean generated files and caches
clean:
	@echo "Cleaning generated files and caches..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*~" -delete
	@find . -type f -name ".coverage" -delete
	@rm -rf build/ dist/ htmlcov/ .coverage* coverage.xml
	@echo "Clean complete!"

# Install the package
install:
	@echo "Installing dependencies..."
	pip install -e .

# Install with development dependencies
install-dev:
	@echo "Installing development dependencies..."
	pip install -e ".[dev,docs]"
	@echo "Installing pre-commit hooks..."
	pre-commit install

# Run tests with coverage
test:
	@echo "Running tests with coverage..."
	pytest

# Test execution targets
test-unit:
	@echo "Running unit tests..."
	pytest tests/unit/ -v --cov=tektii --cov-report=xml --cov-report=term-missing

test-integration:
	@echo "Running integration tests..."
	pytest tests/integration/ -v --disable-warnings

test-e2e:
	@echo "Running end-to-end tests..."
	pytest tests/e2e/ -v --tb=short

test-performance:
	@echo "Running performance tests..."
	pytest tests/performance/ -v --benchmark-only

test-security:
	@echo "Running security tests..."
	bandit -r tektii/
	pytest tests/security/ -v

test-all:
	@echo "Running all tests..."
	pytest tests/ -v --cov=tektii --cov-report=html --cov-report=term-missing

test-fast:
	@echo "Running fast unit tests..."
	pytest tests/unit/ -x -v --tb=short -m "not slow"

# Security scan
security-scan:
	@echo "Running security scan with bandit..."
	bandit -r tektii/ -ll

# Format code with black and isort
format:
	@echo "Formatting code with black..."
	black tektii tests examples
	@echo "Sorting imports with isort..."
	isort tektii tests examples

# Run linters
lint:
	@echo "Running flake8..."
	flake8 tektii tests
	@echo "Running bandit security checks..."
	bandit -r tektii -ll

# Run mypy type checking
type-check:
	@echo "Running mypy type checking..."
	mypy tektii

# Run all quality checks
check: lint type-check test
	@echo "All quality checks passed!"

# Build distribution packages
build: clean
	@echo "Building distribution packages..."
	python -m build
	@echo "Build complete! Packages in dist/"

# Build documentation
docs:
	@echo "Building documentation..."
	@cd docs && make clean html
	@echo "Documentation built in docs/_build/html/"

# Serve documentation locally
serve-docs: docs
	@echo "Serving documentation at http://localhost:8000"
	@cd docs/_build/html && python -m http.server 8000

# Setup for first-time developers
setup:
	@# Create virtual environment if it doesn't exist
	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv .venv; \
	fi
	@# Activate virtual environment
	@echo "Activating virtual environment..."
	@. .venv/bin/activate || . .venv/Scripts/activate 2>/dev/null || true
	@# Upgrade pip
	@echo "Upgrading pip..."
	@.venv/bin/pip install --upgrade pip
	@# Install dev dependencies using venv pip
	@echo "Installing development dependencies..."
	@.venv/bin/pip install -e ".[dev,docs]"
	@echo "Installing pre-commit hooks..."
	@.venv/bin/pre-commit install
	@# Generate proto files
	@echo "Pulling latest proto files..."
	@.venv/bin/python proto/pull_proto.py
	@echo "Generating Python code from proto files..."
	@mkdir -p tektii/strategy/grpc
	@touch tektii/strategy/grpc/__init__.py
	@.venv/bin/python -m grpc_tools.protoc \
		-I./proto \
		--python_out=./tektii/strategy/grpc \
		--grpc_python_out=./tektii/strategy/grpc \
		--pyi_out=./tektii/strategy/grpc \
		proto/trading/v1/*.proto
	@echo "Fixing imports in generated files..."
	@# Fix imports for all generated grpc files
	@for file in tektii/strategy/grpc/*_pb2_grpc.py; do \
		if [ -f "$$file" ]; then \
			base=$$(basename "$$file" _pb2_grpc.py); \
			sed -i.bak "s/import $${base}_pb2/from . import $${base}_pb2/g" "$$file" && rm -f "$$file.bak"; \
		fi; \
	done
	@echo "Proto generation complete!"
	@echo "Setup complete! You can now start developing."
	@echo "Then run 'make check' to ensure everything is working."
