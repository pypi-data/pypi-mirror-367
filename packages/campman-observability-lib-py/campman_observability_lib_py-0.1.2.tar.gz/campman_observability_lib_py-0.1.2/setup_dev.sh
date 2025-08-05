#!/bin/bash
# Development setup script for campman-observability-lib-py

set -e

echo "Setting up development environment for campman-observability-lib-py..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Warning: You're not in a virtual environment. Consider creating one:"
    echo "python -m venv venv"
    echo "source venv/bin/activate  # On Linux/Mac"
    echo "# or"
    echo "venv\\Scripts\\activate  # On Windows"
    echo ""
fi

# Install the package in development mode
echo "Installing package in development mode..."
pip install -e .[dev]

echo "Installing additional development tools..."
pip install -r requirements-dev.txt

echo ""
echo "Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  pytest                    # Run tests"
echo "  pytest --cov             # Run tests with coverage"
echo "  black .                   # Format code"
echo "  flake8 campman_observability tests  # Lint code"
echo "  mypy campman_observability           # Type check"
echo "  python -m build           # Build package"
echo "  twine check dist/*        # Check built package"
echo ""
