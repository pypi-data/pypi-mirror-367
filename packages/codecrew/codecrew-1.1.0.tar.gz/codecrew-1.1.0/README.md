# CodeCrew Multi-Agent Development System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CodeCrew is a comprehensive multi-agent development system that automates software development workflows using AI agents for project management, development, testing, and deployment.

## 🚀 Quick Start

### Installation

```bash
# Install from local directory
uv tool install .

# Or install in development mode
uv sync --extra dev
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
git clone <repository-url>
cd CodeCrew

# Install with uv
uv sync --extra dev

# Run tests
uv run pytest

# Test the CLI
uv run codecrew --help
```

## 📖 Usage

### Basic Commands

```bash
# Initialize a project
codecrew init --project <name> --spec <spec-file> --brd <brd-file> --prd <prd-file> --userstories <stories-file> --checklist <checklist-file>

# Deploy agents
codecrew deploy --project <name>

# Check status
codecrew status [--project <name>] [--detailed]

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
- **Lead Developer**: Handles technical leadership
- **Developer**: Manages feature implementation
- **QA Engineer**: Handles testing and quality assurance
- **DevOps Engineer**: Manages deployment and infrastructure
- **Code Reviewer**: Ensures code quality
- **Documentation Writer**: Maintains documentation

## 📄 License

This project is licensed under the MIT License.

## 🔗 Links

- [Documentation](https://github.com/dscv101/codecrew#readme)
- [Issues](https://github.com/dscv101/codecrew/issues)
