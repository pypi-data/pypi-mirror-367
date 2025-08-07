# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kintu is a generic multi-provider LLM library written in Python. The project is in early development stages.

## Development Environment

This project uses `uv` as the Python package manager and `Flit` as the build backend. Python 3.10+ is required.

## Common Commands

### Development Setup
```bash
# Install dependencies
uv sync

# Install package in development mode
invoke dev
```

### Running Code
```bash
# Run the main module
python -m kintu.main

# Run hello.py
python hello.py
```

### Build and Deploy
```bash
# Clean build artifacts
invoke clean

# Build distribution packages
invoke build

# Check distribution packages
invoke check-dist

# Deploy to TestPyPI (for testing)
invoke test-deploy

# Deploy to PyPI (for production release)
invoke release

# Deploy with custom options
invoke deploy --repository=testpypi --skip-existing
```

### Available Invoke Tasks
- `invoke clean` - Remove build artifacts
- `invoke build` - Build distribution packages using Flit (wheel and sdist)
- `invoke check-dist` - Validate distribution packages with twine
- `invoke deploy` - Deploy to PyPI or TestPyPI with options
- `invoke test-deploy` - Build and deploy to TestPyPI
- `invoke release` - Build and deploy to PyPI
- `invoke dev` - Install package in development mode using Flit symlink
- `invoke lint` - Run linters (placeholder for future setup)
- `invoke test` - Run tests (placeholder for future setup)

## Project Structure

The project has a simple structure:
- `kintu/` - Main package directory
  - `main.py` - Entry point with a simple hello world function
- `hello.py` - Standalone hello world script
- `pyproject.toml` - Project configuration using modern Python packaging standards
- `uv.lock` - Dependency lock file managed by uv