# CodeCrew Multi-Agent Development System

[![PyPI version](https://badge.fury.io/py/codecrew.svg)](https://badge.fury.io/py/codecrew)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CodeCrew is a comprehensive multi-agent development system that automates software development workflows using AI agents for project management, development, testing, and deployment.

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install codecrew

# Or install with pipx for CLI usage
pipx install codecrew
```

### Initialize a New Project

```bash
# Initialize a new project
codecrew init --project myapp --spec spec.md --brd brd.md --prd prd.md --userstories userstories.md --checklist checklist.md

# Deploy development team
codecrew deploy --project myapp

# Check project status
codecrew status --project myapp
```

## 📋 Features

- **Multi-Agent Architecture**: Specialized AI agents for different development roles
- **Project Management**: Automated project initialization and management
- **GitHub Integration**: Seamless integration with GitHub workflows
- **Quality Assurance**: Built-in code quality checks and testing
- **Template System**: Pre-configured project templates
- **CLI Interface**: Comprehensive command-line interface

## 🛠️ Development

### Prerequisites

- Python 3.11+
- Git
- GitHub CLI (optional, for GitHub integration)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/dscv101/codecrew.git
cd codecrew

# Install with Hatch
pip install hatch

# Create development environment
hatch env create

# Install pre-commit hooks
hatch run dev:install-hooks

# Run tests
hatch run test

# Run linting and formatting
hatch run lint:all

# Run quality checks
hatch run dev:quality-check
```

### Available Hatch Environments

- **default**: Basic testing environment
- **dev**: Full development environment with all tools
- **lint**: Linting and formatting tools
- **docs**: Documentation building tools

### Hatch Scripts

```bash
# Testing
hatch run test                    # Run tests
hatch run test-cov               # Run tests with coverage
hatch run cov-report             # Generate coverage report

# Code Quality
hatch run lint:style             # Check code style
hatch run lint:fmt               # Format code
hatch run lint:typing            # Type checking
hatch run lint:security          # Security checks
hatch run lint:all               # Run all checks

# Development
hatch run dev:quality-check      # Full quality check
hatch run dev:security-check     # Security audit

# Documentation
hatch run docs:build             # Build documentation
hatch run docs:serve             # Serve documentation locally
```

## 📖 Usage

### Basic Commands

```bash
# Initialize a project
codecrew init --project <name> --spec <spec-file> [options]

# Deploy agents
codecrew deploy --project <name>

# Check status
codecrew status [--project <name>] [--detailed]

# Manage agents
codecrew agents list [--detailed]
codecrew agents launch --agent-id <id>

# GitHub integration
codecrew github setup
codecrew github status

# Quality checks
codecrew quality check [--verbose]

# System diagnostics
codecrew doctor
```

### Project Templates

CodeCrew supports various project templates:

- `python_api`: FastAPI-based REST API
- `ml_project`: Machine Learning project
- `web_app`: Web application

## 🏗️ Architecture

CodeCrew uses a multi-agent architecture with specialized agents:

- **Project Manager**: Oversees project coordination
- **Backend Developer**: Handles server-side development
- **Frontend Developer**: Manages client-side development
- **DevOps Engineer**: Handles deployment and infrastructure
- **QA Engineer**: Manages testing and quality assurance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run quality checks (`hatch run dev:quality-check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Documentation](https://github.com/dscv101/codecrew#readme)
- [Issues](https://github.com/dscv101/codecrew/issues)
- [PyPI Package](https://pypi.org/project/codecrew/)

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Package management with [Hatch](https://hatch.pypa.io/)
- AI integration with various LLM providers
