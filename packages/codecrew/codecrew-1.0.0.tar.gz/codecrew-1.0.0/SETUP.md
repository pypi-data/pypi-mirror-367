# CodeCrew Setup Guide

Welcome to CodeCrew! This guide will help you set up the CodeCrew Multi-Agent Development System after cloning the repository.

## 🚀 Quick Start

```bash
# 1. Clone the repository (if not already done)
git clone <repository-url>
cd CodeCrew

# 2. Run the automated installer
python codecrew_setup.py install

# 3. Create an example project
python codecrew_setup.py example

# 4. Initialize your first project
codecrew init --project myapp --spec codecrew-example/spec.md --brd codecrew-example/brd.md --prd codecrew-example/prd.md --userstories codecrew-example/userstories.md --checklist codecrew-example/checklist.md
```

## 📋 Prerequisites

Before installing CodeCrew, ensure you have the following:

### Required Software
- **Python 3.9+** (Python 3.10+ recommended)
- **Git** (latest version)
- **pip** package manager
- **Internet connection** (for downloading dependencies)

### Optional but Recommended
- **GitHub CLI** (`gh`) - For GitHub integration
- **Claude Code CLI** - For agent interaction
- **Docker** - For containerized development
- **PostgreSQL** - For database projects
- **Redis** - For caching and session management

### System Requirements
- **Operating System**: macOS, Linux, or Windows
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Stable internet connection

## 🔧 Installation Methods

### Method 1: Automated Installation (Recommended)

The automated installer handles all dependencies and configuration:

```bash
# Standard installation
python codecrew_setup.py install

# Development installation (includes testing tools)
python codecrew_setup.py install --dev

# Force reinstallation
python codecrew_setup.py install --force
```

### Method 2: Manual Installation

If you prefer manual control:

```bash
# 1. Install core Python dependencies
pip install fastapi>=0.104.0 uvicorn[standard]>=0.24.0 pydantic>=2.0.0
pip install sqlalchemy>=2.0.0 alembic>=1.12.0 psycopg2-binary>=2.9.0
pip install redis>=5.0.0 python-jose[cryptography]>=3.3.0
pip install click>=8.1.0 rich>=13.6.0 pyyaml>=6.0.0

# 2. Install development tools (optional)
pip install pytest>=7.4.0 pytest-cov>=4.1.0 black>=23.0.0 isort>=5.12.0

# 3. Set up CodeCrew CLI
python codecrew_setup.py install --dev
```

## 🏗️ Post-Installation Setup

### 1. Verify Installation

```bash
# Check system health
codecrew doctor

# Verify CLI is working
codecrew --help

# Check installed components
codecrew status
```

### 2. Configure GitHub Integration (Optional)

```bash
# Install GitHub CLI (if not already installed)
# macOS: brew install gh
# Ubuntu: sudo apt install gh
# Windows: winget install GitHub.cli

# Set up GitHub integration
codecrew github setup

# Verify GitHub connection
codecrew github status
```

### 3. Set up Claude Code (Optional)

1. Install Claude Code CLI from [Anthropic's documentation](https://docs.anthropic.com/claude-code)
2. Authenticate with your Anthropic account
3. Verify integration: `claude-code --version`

## 📁 Directory Structure

After installation, CodeCrew creates the following structure:

```
~/.codecrew/                 # Main installation directory
├── bin/                     # CLI executables
├── templates/               # Project templates
├── config/                  # Configuration files
├── logs/                    # System logs
└── cache/                   # Temporary files

./codecrew-example/          # Example project (created with 'example' command)
├── spec.md                  # Technical specification
├── brd.md                   # Business Requirements Document
├── prd.md                   # Product requirements
├── userstories.md           # User stories and acceptance criteria
├── checklist.md             # Project checklist and deliverables
└── README.md                # Project documentation
```

## 🎯 Creating Your First Project

### 1. Prepare Project Documents

Create five essential documents:

- **`spec.md`** - Technical specification with requirements and API design
- **`brd.md`** - Business Requirements Document with business context and objectives
- **`prd.md`** - Product requirements with business goals and success metrics
- **`userstories.md`** - User stories and acceptance criteria
- **`checklist.md`** - Project checklist and deliverables tracking

*Tip: Use the example files in `codecrew-example/` as templates*

### 2. Initialize Project

```bash
codecrew init --project "my-awesome-app" \
  --spec spec.md \
  --prd prd.md \
  --arch architecture.md
```

### 3. Deploy Development Team

```bash
# Deploy agents for your project
codecrew deploy --project "my-awesome-app"

# Check deployment status
codecrew status --project "my-awesome-app" --detailed
```

### 4. Launch Agents

```bash
# List available agents
codecrew agents list

# Launch Claude Code for specific agent
codecrew agents launch --agent-id my-awesome-app_developer_1234567890
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in your project directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/dbname
DATABASE_POOL_SIZE=5

# Redis Configuration  
REDIS_URL=redis://localhost:6379
REDIS_TTL=3600

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# GitHub Integration
GITHUB_TOKEN=your-github-token
GITHUB_REPO=your-org/your-repo

# Claude Code Integration
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### CodeCrew Configuration

The system creates a default configuration at `~/.codecrew/config/codecrew.yaml`:

```yaml
version: "1.0.0"
default_project_type: "python_api"
github_integration: true

quality_standards:
  test_coverage_minimum: 80
  code_complexity_maximum: 10
  security_scan_required: true

agent_defaults:
  checkin_interval_minutes: 15
  commit_frequency_minutes: 30
  auto_escalate_minutes: 60
```

## 🚨 Troubleshooting

### Common Issues

**Installation fails with permission errors:**
```bash
# Try with user installation
python codecrew_setup.py install --user

# Or use virtual environment
python -m venv codecrew-env
source codecrew-env/bin/activate  # On Windows: codecrew-env\Scripts\activate
python codecrew_setup.py install
```

**GitHub CLI not found:**
```bash
# Install GitHub CLI
# macOS: brew install gh
# Ubuntu: sudo apt install gh  
# Windows: winget install GitHub.cli

# Then run setup again
codecrew github setup
```

**Python version too old:**
```bash
# Check Python version
python --version

# Install Python 3.9+ from python.org
# Or use pyenv to manage versions
```

### Getting Help

```bash
# Run system diagnostics
codecrew doctor

# Check detailed status
codecrew status --detailed

# View logs
tail -f ~/.codecrew/logs/codecrew.log
```

## 📚 Next Steps

1. **Read the Documentation**: Check out `codecrew_usage_guide.md` for detailed usage instructions
2. **Explore Templates**: Review `template_requirements_summary.md` for available project templates
3. **Set up GitHub Workflow**: Configure your repository with `codecrew github setup`
4. **Launch Your First Agent**: Use `codecrew agents launch` to start development
5. **Monitor Progress**: Use `codecrew status` to track your project's progress

## 🆘 Support

- **Documentation**: Check the included markdown files for detailed guides
- **System Health**: Run `codecrew doctor` for diagnostics
- **GitHub Issues**: Report bugs and feature requests in the repository
- **Community**: Join discussions and get help from other users

---

**Happy coding with CodeCrew! 🚀**

*For more detailed information, see the complete usage guide in `codecrew_usage_guide.md`*
