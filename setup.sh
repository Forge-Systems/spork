#!/usr/bin/env bash
# Setup script for spork - installs all dependencies and the tool

set -e  # Exit on error

echo "🚀 Setting up spork..."
echo ""

# Check if Python 3.9+ is installed
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "   Please install Python 3.9 or later from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION or later is required"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION found"
echo ""

# Check if git is installed
echo "Checking for git..."
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed"
    echo "   Please install git from https://git-scm.com/downloads"
    exit 1
fi
echo "✓ git found"
echo ""

# Check if just is installed (optional but recommended)
echo "Checking for just (optional)..."
if ! command -v just &> /dev/null; then
    echo "⚠️  just command runner not found (optional)"
    echo "   Install with: brew install just (macOS) or cargo install just"
    echo "   Or see: https://github.com/casey/just#installation"
    echo ""
else
    echo "✓ just found"
    echo ""
fi

# Create virtual environment
echo "Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "⚠️  .venv directory already exists, removing..."
    rm -rf .venv
fi

python3 -m venv .venv
echo "✓ Virtual environment created"
echo ""

# Upgrade pip
echo "Upgrading pip..."
.venv/bin/pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install spork with dev dependencies
echo "Installing spork with development dependencies..."
.venv/bin/pip install -e ".[dev]" --quiet
echo "✓ spork installed"
echo ""

# Verify installation
echo "Verifying installation..."
if .venv/bin/spork --help &> /dev/null; then
    echo "✓ spork command works"
else
    echo "❌ Error: spork command failed"
    exit 1
fi
echo ""

echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "Then you can use spork commands:"
echo "  spork \"your-feature-request\""
echo ""
if command -v just &> /dev/null; then
    echo "Available just commands:"
    echo "  just lint       - Run linter"
    echo "  just typecheck  - Run type checker"
    echo "  just test       - Run tests"
    echo "  just check      - Run all checks"
    echo ""
fi
