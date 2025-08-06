# Publishing Guide

This guide explains how to publish the `campman-observability-lib-py` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both [Test PyPI](https://test.pypi.org) and [PyPI](https://pypi.org)
2. **API Tokens**: Generate API tokens for both Test PyPI and PyPI
3. **Development Environment**: Set up your development environment

## Setup Development Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd campman-observability-lib-py

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows

# Run development setup
./setup_dev.sh
# or manually:
pip install -e .[dev]
```

## Pre-publishing Checklist

1. **Update Version**: Update version in `pyproject.toml` and `campman_observability/__init__.py`
2. **Update Metadata**: Ensure all metadata (author, email, URLs) are correct
3. **Run Tests**: Ensure all tests pass
4. **Check Code Quality**: Run linting and type checking
5. **Update Documentation**: Update README.md and any other documentation

```bash
# Run the full test suite
pytest --cov=campman_observability

# Check code quality
black --check .
flake8 campman_observability tests
mypy campman_observability

# Build package
python -m build

# Check the built package
twine check dist/*
```

## Publishing to Test PyPI

First, publish to Test PyPI to ensure everything works:

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*
# You'll be prompted for your Test PyPI API token

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ campman-observability-lib-py
```

## Publishing to PyPI

Once you've verified everything works on Test PyPI:

```bash
# Upload to PyPI
twine upload dist/*
# You'll be prompted for your PyPI API token

# Test installation from PyPI
pip install campman-observability-lib-py
```

## Automated Publishing with GitHub Actions

The repository includes GitHub Actions workflows for automated testing and publishing:

1. **CI Workflow** (`.github/workflows/ci.yml`): Runs tests on every push/PR
2. **Publish Workflow** (`.github/workflows/publish.yml`): Publishes to PyPI on release

### Setting up GitHub Actions

1. Add your PyPI API token as a secret in your GitHub repository:
   - Go to your repository settings
   - Click on "Secrets and variables" → "Actions"
   - Add a new secret named `PYPI_API_TOKEN` with your PyPI API token

2. Create a release on GitHub:
   - Go to your repository
   - Click on "Releases" → "Create a new release"
   - Tag version should match your package version (e.g., `v0.1.0`)
   - This will trigger the publish workflow automatically

## Version Management

Follow semantic versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Update version in:

1. `pyproject.toml` (line 7)
2. `campman_observability/__init__.py` (line 12)

## Package Structure

```text
campman-observability-lib-py/
├── campman_observability/          # Main package
│   ├── __init__.py                # Package initialization
│   └── observability.py          # Main module
├── tests/                         # Test files
├── .github/workflows/             # GitHub Actions
├── requirements.txt               # Runtime dependencies
├── requirements-dev.txt           # Development dependencies
├── pyproject.toml                # Modern Python packaging
├── MANIFEST.in                   # Include additional files
├── README.md                     # Package documentation
├── LICENSE                       # License file
└── .gitignore                    # Git ignore rules
```

## Common Issues and Solutions

### Import Errors

- Ensure all imports in `__init__.py` are correct
- Check that the module structure matches the imports

### Missing Dependencies

- Verify all dependencies are listed in `pyproject.toml` or `requirements.txt`
- Test installation in a clean environment

### Build Failures

- Check that all required files are included in `MANIFEST.in`
- Ensure `pyproject.toml` configuration is correct

### Version Conflicts

- Make sure version numbers are consistent across all files
- Follow semantic versioning guidelines

## Support and Maintenance

After publishing:

1. Monitor PyPI download statistics
2. Respond to issues and bug reports
3. Keep dependencies up to date
4. Release security patches promptly
5. Maintain backward compatibility when possible
