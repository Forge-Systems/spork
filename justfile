# Justfile for spork development commands

# Install spork with development dependencies
install:
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -e ".[dev]"
    @echo "✓ Installation complete. Activate with: source .venv/bin/activate"

# Run linter (ruff)
lint:
    .venv/bin/ruff check .

# Run type checker (mypy)
typecheck:
    .venv/bin/mypy spork

# Run all tests
test:
    .venv/bin/pytest

# Run specific test file
test-file FILE:
    .venv/bin/pytest {{FILE}}

# Run tests with coverage
test-coverage:
    .venv/bin/pytest --cov=spork --cov-report=term-missing

# Run all checks (lint, typecheck, test)
check: lint typecheck test

# Clean build artifacts and cache
clean:
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info
    rm -rf .pytest_cache
    rm -rf .mypy_cache
    rm -rf .ruff_cache
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Format code with ruff
fmt:
    .venv/bin/ruff format .

# Run ruff in fix mode
fix:
    .venv/bin/ruff check --fix .
