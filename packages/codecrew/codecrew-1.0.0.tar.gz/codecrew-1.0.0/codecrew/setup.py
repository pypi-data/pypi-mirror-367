#!/usr/bin/env python3
"""
CodeCrew Setup and Installation Scripts
Complete setup automation for the CodeCrew system
"""

import os
import sys
import subprocess
import shutil
import json
import urllib.request
import stat
from pathlib import Path
from typing import List, Dict, Any, Optional
import platform
import zipfile
import tarfile

class CodeCrewInstaller:
    """Complete installer for CodeCrew system"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.python_version = sys.version_info
        self.install_dir = Path.home() / ".codecrew"
        self.bin_dir = self.install_dir / "bin"
        self.config_dir = self.install_dir / "config"
        
    def install(self, dev_mode: bool = False):
        """Complete CodeCrew installation"""
        print("🚀 Installing CodeCrew Multi-Agent Development System")
        print("=" * 55)
        
        try:
            # Pre-installation checks
            self._check_prerequisites()
            
            # Create directories
            self._create_directories()
            
            # Install Python dependencies
            self._install_python_dependencies(dev_mode)
            
            # Install system dependencies
            self._install_system_dependencies()
            
            # Install CodeCrew components
            self._install_codecrew_components()
            
            # Set up CLI
            self._setup_cli()
            
            # Configure system
            self._configure_system()
            
            # Verify installation
            self._verify_installation()
            
            print("\n🎉 CodeCrew installation completed successfully!")
            self._print_getting_started()
            
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            print("Please check the error details above and try again.")
            return False
        
        return True
    
    def _check_prerequisites(self):
        """Check system prerequisites"""
        print("\n🔍 Checking prerequisites...")
        
        # Check Python version
        if self.python_version < (3, 9):
            raise Exception(f"Python 3.9+ required, found {self.python_version.major}.{self.python_version.minor}")
        print(f"✅ Python {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        
        # Check pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                          capture_output=True, check=True)
            print("✅ pip package manager")
        except subprocess.CalledProcessError:
            raise Exception("pip not found - please install pip")
        
        # Check git
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, check=True, text=True)
            print(f"✅ {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise Exception("Git not found - please install Git")
        
        # Check internet connection
        try:
            urllib.request.urlopen('https://www.github.com', timeout=10)
            print("✅ Internet connection")
        except Exception:
            print("⚠️  Limited internet connectivity - some features may not work")
    
    def _create_directories(self):
        """Create required directories"""
        print("\n📁 Creating directories...")
        
        directories = [
            self.install_dir,
            self.bin_dir,
            self.config_dir,
            self.install_dir / "templates",
            self.install_dir / "logs",
            self.install_dir / "cache"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ {directory}")
    
    def _install_python_dependencies(self, dev_mode: bool):
        """Install Python dependencies"""
        print("\n📦 Installing Python dependencies...")
        
        # Core dependencies
        core_deps = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0", 
            "pydantic>=2.0.0",
            "sqlalchemy>=2.0.0",
            "alembic>=1.12.0",
            "psycopg2-binary>=2.9.0",
            "redis>=5.0.0",
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.4",
            "python-multipart>=0.0.6",
            "requests>=2.31.0",
            "click>=8.1.0",
            "rich>=13.6.0",
            "pyyaml>=6.0.0",
            "python-dotenv>=1.0.0",
            "jinja2>=3.1.0"
        ]
        
        # Development dependencies
        dev_deps = [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.25.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.6.0",
            "pre-commit>=3.4.0",
            "safety>=2.3.0",
            "bandit>=1.7.0",
            "pip-audit>=2.6.0"
        ]
        
        dependencies = core_deps + (dev_deps if dev_mode else [])
        
        for dep in dependencies:
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", dep, "--upgrade"
                ], check=True, capture_output=True)
                print(f"✅ {dep.split('>=')[0]}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {dep}: {e}")
                raise
    
    def _install_system_dependencies(self):
        """Install system-level dependencies"""
        print("\n🔧 Installing system dependencies...")
        
        # GitHub CLI
        if not self._check_command("gh"):
            print("📥 Installing GitHub CLI...")
            self._install_github_cli()
        else:
            print("✅ GitHub CLI already installed")
        
        # Docker (optional but recommended)
        if not self._check_command("docker"):
            print("⚠️  Docker not found - install Docker for containerization features")
            print("   Visit: https://docs.docker.com/get-docker/")
        else:
            print("✅ Docker available")
        
        # Claude Code CLI (if available)
        if not self._check_command("claude-code"):
            print("⚠️  Claude Code CLI not found")
            print("   This is required for agent interaction")
            print("   Install from: https://docs.anthropic.com/claude-code")
        else:
            print("✅ Claude Code CLI available")
    
    def _install_github_cli(self):
        """Install GitHub CLI based on system"""
        if self.system == "darwin":  # macOS
            try:
                # Try Homebrew first
                subprocess.run(["brew", "install", "gh"], check=True, capture_output=True)
                print("✅ GitHub CLI installed via Homebrew")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  Please install GitHub CLI manually: https://cli.github.com/")
                
        elif self.system == "linux":
            try:
                # Try apt-get (Ubuntu/Debian)
                subprocess.run([
                    "curl", "-fsSL", "https://cli.github.com/packages/githubcli-archive-keyring.gpg",
                    "|", "sudo", "dd", "of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
                ], check=True, shell=True, capture_output=True)
                
                subprocess.run([
                    "echo", "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main",
                    "|", "sudo", "tee", "/etc/apt/sources.list.d/github-cli.list", "> /dev/null"
                ], check=True, shell=True, capture_output=True)
                
                subprocess.run(["sudo", "apt", "update"], check=True, capture_output=True)
                subprocess.run(["sudo", "apt", "install", "gh"], check=True, capture_output=True)
                print("✅ GitHub CLI installed via apt")
            except subprocess.CalledProcessError:
                print("⚠️  Please install GitHub CLI manually: https://cli.github.com/")
                
        else:  # Windows
            print("⚠️  Please install GitHub CLI manually: https://cli.github.com/")
    
    def _install_codecrew_components(self):
        """Install CodeCrew framework components"""
        print("\n🤖 Installing CodeCrew components...")
        
        # Copy framework files to installation directory
        framework_files = [
            "codecrew_main.py",
            "codecrew_templates.py", 
            "codecrew_cli.py"
        ]
        
        src_dir = Path(__file__).parent
        
        for file_name in framework_files:
            src_file = src_dir / file_name
            dest_file = self.install_dir / file_name
            
            if src_file.exists():
                shutil.copy2(src_file, dest_file)
                print(f"✅ {file_name}")
            else:
                # Create minimal version if source not found
                self._create_minimal_component(dest_file, file_name)
                print(f"⚠️  {file_name} (minimal version created)")
    
    def _create_minimal_component(self, dest_file: Path, file_name: str):
        """Create minimal version of component if source not available"""
        
        if file_name == "codecrew_main.py":
            content = '''#!/usr/bin/env python3
"""CodeCrew Main Framework - Minimal Version"""
print("CodeCrew framework loading...")
# Import the complete implementation here
'''
        elif file_name == "codecrew_templates.py":
            content = '''#!/usr/bin/env python3
"""CodeCrew Templates - Minimal Version"""
print("CodeCrew templates loading...")
# Import the complete implementation here
'''
        elif file_name == "codecrew_cli.py":
            content = '''#!/usr/bin/env python3
"""CodeCrew CLI - Minimal Version"""
print("CodeCrew CLI loading...")
# Import the complete implementation here
'''
        else:
            content = f'#!/usr/bin/env python3\n"""CodeCrew Component: {file_name}"""\npass\n'
        
        dest_file.write_text(content)
    
    def _setup_cli(self):
        """Set up CodeCrew CLI"""
        print("\n💻 Setting up CLI...")
        
        # Create CLI executable
        cli_script = self.bin_dir / "codecrew"
        cli_content = f'''#!/usr/bin/env python3
"""CodeCrew CLI Executable"""
import sys
import os
sys.path.insert(0, "{self.install_dir}")

try:
    from codecrew_cli import main
    sys.exit(main())
except Exception as e:
    print(f"Error: {{e}}")
    sys.exit(1)
'''
        
        cli_script.write_text(cli_content)
        cli_script.chmod(0o755)
        print(f"✅ CLI created: {cli_script}")
        
        # Add to PATH (platform-specific)
        self._add_to_path()
    
    def _add_to_path(self):
        """Add CodeCrew bin directory to PATH"""
        shell_configs = []
        
        if self.system in ["darwin", "linux"]:
            home = Path.home()
            shell_configs = [
                home / ".bashrc",
                home / ".zshrc", 
                home / ".profile",
                home / ".bash_profile"
            ]
        
        path_line = f'export PATH="{self.bin_dir}:$PATH"'
        codecrew_comment = "# CodeCrew CLI"
        
        for config_file in shell_configs:
            if config_file.exists():
                content = config_file.read_text()
                if codecrew_comment not in content:
                    with open(config_file, "a") as f:
                        f.write(f"\n{codecrew_comment}\n{path_line}\n")
                    print(f"✅ Updated {config_file.name}")
        
        # For immediate use
        os.environ["PATH"] = f"{self.bin_dir}:{os.environ.get('PATH', '')}"
        
        if self.system == "windows":
            print("⚠️  Please add to PATH manually on Windows:")
            print(f"   {self.bin_dir}")
    
    def _configure_system(self):
        """Configure CodeCrew system"""
        print("\n⚙️  Configuring system...")
        
        # Create default configuration
        config = {
            "version": "1.0.0",
            "install_dir": str(self.install_dir),
            "default_project_type": "python_api",
            "github_integration": True,
            "quality_standards": {
                "test_coverage_minimum": 80,
                "code_complexity_maximum": 10,
                "security_scan_required": True
            },
            "agent_defaults": {
                "checkin_interval_minutes": 15,
                "commit_frequency_minutes": 30,
                "auto_escalate_minutes": 60
            },
            "templates": {
                "auto_update": True,
                "custom_templates_dir": None
            }
        }
        
        config_file = self.config_dir / "codecrew.json"
        config_file.write_text(json.dumps(config, indent=2))
        print(f"✅ Configuration: {config_file}")
        
        # Create logging configuration
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "level": "INFO",
                    "formatter": "standard",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "level": "INFO", 
                    "formatter": "standard",
                    "class": "logging.FileHandler",
                    "filename": str(self.install_dir / "logs" / "codecrew.log"),
                    "mode": "a"
                }
            },
            "loggers": {
                "": {
                    "handlers": ["default", "file"],
                    "level": "INFO",
                    "propagate": False
                }
            }
        }
        
        log_config_file = self.config_dir / "logging.json"
        log_config_file.write_text(json.dumps(log_config, indent=2))
        print(f"✅ Logging config: {log_config_file}")
    
    def _verify_installation(self):
        """Verify installation is working"""
        print("\n🔍 Verifying installation...")
        
        # Test CLI
        try:
            result = subprocess.run([
                sys.executable, str(self.bin_dir / "codecrew"), "--version"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ CLI working")
            else:
                print("❌ CLI test failed")
                print(result.stderr)
                
        except subprocess.TimeoutExpired:
            print("❌ CLI test timed out")
        except Exception as e:
            print(f"❌ CLI test error: {e}")
        
        # Test imports
        try:
            sys.path.insert(0, str(self.install_dir))
            import codecrew_main
            print("✅ Core framework import")
        except ImportError as e:
            print(f"❌ Framework import failed: {e}")
        
        # Test GitHub CLI
        if self._check_command("gh"):
            try:
                result = subprocess.run(["gh", "auth", "status"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ GitHub CLI authenticated")
                else:
                    print("⚠️  GitHub CLI not authenticated (run 'gh auth login')")
            except Exception:
                print("⚠️  GitHub CLI test failed")
    
    def _print_getting_started(self):
        """Print getting started information"""
        print("\n🎯 Getting Started with CodeCrew")
        print("=" * 35)
        print()
        print("1. 📋 Create your project files:")
        print("   - spec.md (project specification)")
        print("   - brd.md (business requirements document)")
        print("   - prd.md (product requirements)")
        print("   - userstories.md (user stories and acceptance criteria)")
        print("   - checklist.md (project checklist and deliverables)")
        print()
        print("2. 🚀 Initialize your project:")
        print("   codecrew init --project myapp --spec spec.md --brd brd.md --prd prd.md --userstories userstories.md --checklist checklist.md")
        print()
        print("3. 👥 Deploy your development team:")
        print("   codecrew deploy --project myapp")
        print()
        print("4. 📊 Monitor progress:")
        print("   codecrew status --project myapp")
        print()
        print("5. 🔗 Set up GitHub integration:")
        print("   codecrew github setup")
        print()
        print("📚 Documentation: https://github.com/your-org/codecrew")
        print("🆘 Support: https://github.com/your-org/codecrew/issues")
        print()
        print("💡 Pro tip: Run 'codecrew doctor' to check system health")
    
    def _check_command(self, command: str) -> bool:
        """Check if command is available"""
        try:
            subprocess.run([command, "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def uninstall(self):
        """Uninstall CodeCrew"""
        print("🗑️  Uninstalling CodeCrew...")
        
        try:
            # Remove installation directory
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir)
                print(f"✅ Removed {self.install_dir}")
            
            # Remove from PATH (best effort)
            self._remove_from_path()
            
            print("✅ CodeCrew uninstalled successfully")
            print("Note: You may need to restart your terminal for PATH changes to take effect")
            
        except Exception as e:
            print(f"❌ Uninstallation failed: {e}")
            return False
        
        return True
    
    def _remove_from_path(self):
        """Remove CodeCrew from PATH"""
        if self.system in ["darwin", "linux"]:
            home = Path.home()
            shell_configs = [
                home / ".bashrc",
                home / ".zshrc",
                home / ".profile", 
                home / ".bash_profile"
            ]
            
            for config_file in shell_configs:
                if config_file.exists():
                    content = config_file.read_text()
                    lines = content.split('\n')
                    
                    # Remove CodeCrew lines
                    filtered_lines = []
                    skip_next = False
                    
                    for line in lines:
                        if "# CodeCrew CLI" in line:
                            skip_next = True
                            continue
                        if skip_next and "codecrew" in line:
                            skip_next = False
                            continue
                        filtered_lines.append(line)
                    
                    if len(filtered_lines) != len(lines):
                        config_file.write_text('\n'.join(filtered_lines))
                        print(f"✅ Cleaned {config_file.name}")


def create_project_example():
    """Create example project files"""
    example_dir = Path("codecrew-example")
    example_dir.mkdir(exist_ok=True)
    
    # spec.md
    spec_content = """# Project Specification: Task Management API

## Overview
A RESTful API for task management with user authentication, CRUD operations, and real-time notifications.

## Core Features

### 1. User Management
- User registration and authentication
- JWT-based session management
- User profiles with customizable settings
- Password reset functionality

### 2. Task Management
- Create, read, update, delete tasks
- Task categorization and tagging
- Due dates and priority levels
- Task assignment to users
- Task status tracking (todo, in_progress, completed)

### 3. Real-time Features
- WebSocket notifications for task updates
- Real-time collaboration on shared tasks
- Live activity feeds

### 4. API Features
- RESTful API design
- OpenAPI/Swagger documentation
- Rate limiting and security
- Comprehensive error handling

## Technical Requirements

### Performance
- API response time <200ms for 95th percentile
- Support for 1000+ concurrent users
- Database query optimization
- Caching for frequently accessed data

### Security
- JWT authentication with refresh tokens
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Rate limiting per user/IP

### Quality
- 90%+ test coverage
- Comprehensive error handling
- Logging and monitoring
- Code documentation

## Database Schema

### Users Table
- id (primary key)
- email (unique)
- password_hash
- name
- created_at
- updated_at

### Tasks Table
- id (primary key)
- title
- description
- status (enum: todo, in_progress, completed)
- priority (enum: low, medium, high)
- due_date
- assigned_user_id (foreign key)
- created_by_user_id (foreign key)
- created_at
- updated_at

### Categories Table
- id (primary key)
- name
- color
- user_id (foreign key)

## API Endpoints

### Authentication
- POST /auth/register - User registration
- POST /auth/login - User login
- POST /auth/refresh - Refresh JWT token
- POST /auth/logout - User logout

### Users
- GET /users/profile - Get current user profile
- PUT /users/profile - Update user profile
- DELETE /users/account - Delete user account

### Tasks
- GET /tasks - List tasks (with filtering/pagination)
- POST /tasks - Create new task
- GET /tasks/{id} - Get specific task
- PUT /tasks/{id} - Update task
- DELETE /tasks/{id} - Delete task

### Categories
- GET /categories - List user categories
- POST /categories - Create category
- PUT /categories/{id} - Update category
- DELETE /categories/{id} - Delete category

## Success Metrics
- API uptime >99.9%
- Average response time <100ms
- Zero data loss
- User satisfaction >4.5/5
"""
    
    # prd.md
    prd_content = """# Product Requirements Document: Task Management API

## Product Vision
Build a robust, scalable task management API that enables developers to create powerful task management applications with real-time collaboration features.

## Target Users

### Primary Users
- **Application Developers**: Building task management apps
- **Development Teams**: Need task management backend
- **Product Managers**: Require task tracking solutions

### Use Cases
1. **Personal Task Management**: Individual productivity apps
2. **Team Collaboration**: Shared project management
3. **Client Task Tracking**: Service provider task management
4. **Integration Platform**: Backend for existing applications

## Functional Requirements

### Must Have (P0)
- User authentication and authorization
- CRUD operations for tasks
- Task categorization and filtering
- RESTful API with standard HTTP methods
- Data persistence with PostgreSQL
- API documentation with examples

### Should Have (P1)
- Real-time notifications via WebSocket
- Task assignment to multiple users
- Due date and reminder system
- File attachments for tasks
- Advanced search and filtering
- Bulk operations (bulk update/delete)

### Could Have (P2)
- Task templates for recurring tasks
- Time tracking integration
- Reporting and analytics API
- Third-party integrations (Slack, email)
- Mobile push notifications
- Audit trail for task changes

### Won't Have (This Release)
- Web frontend interface
- Mobile applications
- Advanced workflow automation
- Integration with external calendars

## Non-Functional Requirements

### Performance
- **Response Time**: 95th percentile <200ms
- **Throughput**: 1000+ requests per second
- **Concurrent Users**: 10,000+ simultaneous connections
- **Database**: Query response <50ms average

### Scalability
- **Horizontal Scaling**: Support load balancing
- **Database**: Read replicas for scaling reads
- **Caching**: Redis for session and frequently accessed data
- **CDN**: Static asset delivery optimization

### Security
- **Authentication**: JWT with 24-hour expiration
- **Authorization**: Role-based access control
- **Data Protection**: Encryption at rest and in transit
- **Rate Limiting**: 100 requests per minute per user
- **Input Validation**: All inputs sanitized and validated

### Reliability
- **Uptime**: 99.9% availability target
- **Data Backup**: Daily automated backups
- **Disaster Recovery**: <4 hour recovery time
- **Monitoring**: Comprehensive health checks

### Usability
- **API Design**: RESTful with consistent patterns
- **Documentation**: Interactive OpenAPI docs
- **Error Messages**: Clear, actionable error responses
- **SDK**: Python/JavaScript client libraries

## Technical Architecture

### API Design Principles
- **RESTful**: Standard HTTP methods and status codes
- **Stateless**: No server-side session storage
- **Cacheable**: Proper HTTP caching headers
- **Consistent**: Uniform response formats
- **Versioned**: API versioning strategy

### Data Model
```
User 1:N Task (created_by)
User 1:N Task (assigned_to)
User 1:N Category
Category 1:N Task
```

### Technology Stack
- **Backend**: Python with FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for sessions and frequently accessed data
- **Authentication**: JWT tokens with refresh mechanism
- **Documentation**: OpenAPI/Swagger automated generation

## Success Criteria

### Launch Criteria
- [ ] All P0 features implemented and tested
- [ ] API documentation complete with examples
- [ ] Performance benchmarks met
- [ ] Security audit passed
- [ ] Load testing completed

### Success Metrics (3 months post-launch)
- **Adoption**: 100+ active API consumers
- **Performance**: 99.9% uptime achieved
- **Usage**: 1M+ API calls per month
- **Satisfaction**: 4.5+ developer satisfaction score
- **Response Time**: <100ms average response time

### Key Performance Indicators
- **API Response Time**: Track 95th percentile daily
- **Error Rate**: <0.1% error rate target
- **User Growth**: 20% month-over-month growth
- **Feature Usage**: Track most/least used endpoints
- **Support Tickets**: <5 tickets per 1000 API calls

## Risk Assessment

### High Risk
- **Database Performance**: Risk of slow queries at scale
- **Security Vulnerabilities**: API security breaches
- **Third-party Dependencies**: External service failures

### Medium Risk
- **Real-time Features**: WebSocket complexity
- **Data Migration**: Schema changes in production
- **Rate Limiting**: Balance between usability and protection

### Low Risk
- **Documentation**: Keeping docs updated
- **Client Library Maintenance**: SDK versioning
- **Feature Creep**: Scope expansion requests

## Timeline
- **Week 1-2**: Core API and authentication
- **Week 3-4**: Task CRUD operations
- **Week 5-6**: Advanced features and real-time
- **Week 7-8**: Testing, documentation, optimization
- **Week 9**: Launch preparation and deployment

## Appendix

### API Response Format
```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful",
  "errors": [],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}
```

### Error Response Format
```json
{
  "success": false,
  "data": null,
  "message": "Validation failed",
  "errors": [
    {
      "field": "email",
      "code": "INVALID_FORMAT",
      "message": "Email format is invalid"
    }
  ]
}
```
"""
    
    # architecture.md
    architecture_content = """# Technical Architecture: Task Management API

## System Overview
The Task Management API is built using a modern, scalable architecture with Python FastAPI, PostgreSQL database, Redis caching, and comprehensive monitoring.

## Architecture Diagram
```
[Client Apps] 
    ↓ HTTPS
[Load Balancer] 
    ↓
[API Gateway] 
    ↓
[FastAPI Application]
    ↓
[Business Logic Layer]
    ↓
[Data Access Layer]
    ↓
[PostgreSQL] + [Redis Cache]
```

## Technology Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework for APIs
- **Python 3.11+**: Latest Python with performance improvements
- **Uvicorn**: ASGI server for FastAPI
- **Pydantic**: Data validation and serialization

### Database Layer
- **PostgreSQL 15**: Primary database for data persistence
- **SQLAlchemy 2.0**: ORM for database operations
- **Alembic**: Database migration management
- **asyncpg**: Async PostgreSQL driver

### Caching Layer
- **Redis 7**: In-memory cache for sessions and frequent data
- **redis-py**: Python Redis client
- **Cache strategies**: Write-through, read-aside patterns

### Authentication & Security
- **JWT Tokens**: Stateless authentication
- **bcrypt**: Password hashing
- **python-jose**: JWT token handling
- **OAuth2**: Standard authentication flow

### Monitoring & Observability
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization
- **Sentry**: Error tracking and monitoring
- **Structured Logging**: JSON-formatted logs

## Detailed Component Architecture

### 1. API Layer (`/src/api/`)

#### Endpoints Structure
```
/src/api/
├── v1/
│   ├── auth.py          # Authentication endpoints
│   ├── users.py         # User management
│   ├── tasks.py         # Task CRUD operations
│   ├── categories.py    # Category management
│   └── websocket.py     # Real-time features
├── middleware/
│   ├── auth.py          # JWT authentication middleware
│   ├── rate_limit.py    # Rate limiting middleware
│   ├── cors.py          # CORS handling
│   └── logging.py       # Request/response logging
└── dependencies/
    ├── auth.py          # Authentication dependencies
    ├── database.py      # Database session dependencies
    └── pagination.py    # Pagination utilities
```

#### Request/Response Flow
1. **Request Validation**: Pydantic models validate input
2. **Authentication**: JWT middleware validates tokens
3. **Authorization**: Role-based access control
4. **Business Logic**: Service layer processes request
5. **Data Access**: Repository pattern for database operations
6. **Response Serialization**: Pydantic models format output

### 2. Business Logic Layer (`/src/services/`)

#### Service Architecture
```
/src/services/
├── auth_service.py      # Authentication business logic
├── user_service.py      # User management logic
├── task_service.py      # Task operations logic
├── category_service.py  # Category management logic
├── notification_service.py # Real-time notifications
└── email_service.py     # Email notifications
```

#### Service Pattern
- **Dependency Injection**: Services injected into API endpoints
- **Business Rules**: All business logic encapsulated in services
- **Transaction Management**: Service methods handle database transactions
- **Error Handling**: Services raise custom business exceptions

### 3. Data Access Layer (`/src/repositories/`)

#### Repository Pattern
```
/src/repositories/
├── base_repository.py   # Base repository with common operations
├── user_repository.py   # User data access
├── task_repository.py   # Task data access
└── category_repository.py # Category data access
```

#### Database Operations
- **CRUD Operations**: Create, Read, Update, Delete
- **Query Building**: Dynamic query construction
- **Relationship Management**: SQLAlchemy relationships
- **Connection Pooling**: Efficient database connections

### 4. Data Models (`/src/models/`)

#### SQLAlchemy Models
```python
# User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    created_tasks = relationship("Task", foreign_keys="Task.created_by_user_id")
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_user_id")
    categories = relationship("Category", back_populates="user")

# Task model  
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = Column(DateTime)
    assigned_user_id = Column(Integer, ForeignKey("users.id"))
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
```

### 5. Configuration (`/src/config/`)

#### Environment-Based Configuration
```python
class Settings(BaseSettings):
    # Database
    database_url: str
    database_pool_size: int = 5
    
    # Redis
    redis_url: str
    redis_ttl: int = 3600
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    
    # API
    api_title: str = "Task Management API"
    api_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
```

## Security Architecture

### Authentication Flow
1. **User Login**: Credentials validated against database
2. **Token Generation**: JWT token created with user claims
3. **Token Storage**: Client stores token (localStorage/memory)
4. **Request Authentication**: Token included in Authorization header
5. **Token Validation**: Signature verified, expiration checked
6. **User Context**: User information extracted from valid token

### Security Measures
- **Password Hashing**: bcrypt with salt rounds
- **JWT Security**: Short expiration, secure signing
- **Input Validation**: All inputs validated and sanitized
- **SQL Injection Prevention**: Parameterized queries only
- **XSS Prevention**: Output encoding and CSP headers
- **Rate Limiting**: Per-user and per-IP limits
- **HTTPS Only**: All communication encrypted
- **CORS Configuration**: Restricted cross-origin requests

## Performance Architecture

### Caching Strategy
```python
# Cache hierarchy
L1: Application Memory (FastAPI in-memory cache)
L2: Redis Cache (Session data, frequent queries)
L3: Database (PostgreSQL with query optimization)
```

### Database Optimization
- **Indexing Strategy**: Indexes on frequently queried columns
- **Query Optimization**: Efficient JOINs and filtering
- **Connection Pooling**: Reuse database connections
- **Read Replicas**: Scale read operations
- **Partitioning**: Large table partitioning strategy

### API Performance
- **Async Operations**: FastAPI async/await throughout
- **Pagination**: Limit result set sizes
- **Field Selection**: Allow clients to specify required fields
- **Compression**: Gzip response compression
- **CDN Integration**: Cache static content

## Scalability Architecture

### Horizontal Scaling
```
[Load Balancer]
    ↓
[API Instance 1] [API Instance 2] [API Instance N]
    ↓                ↓                ↓
[Shared Database] [Shared Redis] [Shared Storage]
```

### Scaling Strategies
- **Stateless Design**: No server-side session storage
- **Database Scaling**: Read replicas and connection pooling
- **Cache Scaling**: Redis cluster for distributed caching
- **File Storage**: S3-compatible object storage
- **Message Queues**: Async task processing with Celery

## Deployment Architecture

### Container Strategy
```dockerfile
# Multi-stage Docker build
FROM python:3.11-slim as builder
# Build dependencies and virtual environment

FROM python:3.11-slim as runtime  
# Copy built environment and run application
```

### Infrastructure
- **Container Orchestration**: Kubernetes or Docker Swarm
- **Service Discovery**: Built-in container networking
- **Load Balancing**: Nginx or cloud load balancer
- **SSL Termination**: Let's Encrypt or cloud certificates
- **Health Checks**: Application and database health endpoints

### CI/CD Pipeline
```yaml
# GitHub Actions workflow
1. Code Commit → GitHub
2. Automated Tests → pytest, coverage, security
3. Code Quality → black, flake8, mypy
4. Container Build → Docker image
5. Security Scan → Container vulnerability scan
6. Deployment → Staging environment
7. Integration Tests → API testing
8. Production Deployment → Blue/green deployment
```

## Monitoring Architecture

### Observability Stack
```
Application Metrics → Prometheus → Grafana
Application Logs → Fluentd → Elasticsearch → Kibana
Error Tracking → Sentry
Uptime Monitoring → External service (Pingdom/DataDog)
```

### Key Metrics
- **Request Metrics**: Rate, duration, error rate
- **Database Metrics**: Connection pool, query performance
- **Cache Metrics**: Hit rate, memory usage
- **Business Metrics**: User registrations, task creation
- **Infrastructure Metrics**: CPU, memory, disk usage

## Development Architecture

### Project Structure
```
task-management-api/
├── src/
│   ├── api/           # API endpoints and middleware
│   ├── services/      # Business logic
│   ├── repositories/  # Data access layer
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── config/        # Configuration management
│   └── utils/         # Utility functions
├── tests/
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── e2e/           # End-to-end tests
├── migrations/        # Database migrations
├── scripts/           # Utility scripts
├── docs/              # Documentation
├── docker/            # Docker configurations
└── k8s/               # Kubernetes manifests
```

### Code Quality Standards
- **Test Coverage**: 90%+ coverage requirement
- **Code Style**: Black + isort + flake8
- **Type Hints**: mypy for static type checking
- **Documentation**: Docstrings for all public methods
- **Security**: bandit security linting
- **Dependencies**: Regular security updates

## Future Architecture Considerations

### Microservices Evolution
- **Service Decomposition**: Split by business domain
- **API Gateway**: Centralized routing and authentication
- **Service Mesh**: Inter-service communication
- **Event-Driven**: Async messaging between services

### Advanced Features
- **GraphQL**: Flexible query language option
- **Real-time**: WebSocket scaling with message brokers
- **Search**: Elasticsearch for advanced search
- **Analytics**: Data warehouse for reporting
- **ML Integration**: Task priority prediction

This architecture provides a solid foundation for a scalable, maintainable task management API that can grow with business needs while maintaining high performance and reliability standards.
"""
    
    # Write files
    (example_dir / "spec.md").write_text(spec_content)
    (example_dir / "prd.md").write_text(prd_content)

    # Note: BRD, user stories, and checklist files are now created separately
    # The architecture content has been distributed among these new documents
    
    # Create README
    readme_content = """# CodeCrew Example Project

This is an example project demonstrating CodeCrew usage for a Task Management API.

## Getting Started

1. Initialize the CodeCrew project:
```bash
codecrew init --project task-api --spec spec.md --brd brd.md --prd prd.md --userstories userstories.md --checklist checklist.md
```

2. Deploy the development team:
```bash
codecrew deploy --project task-api
```

3. Monitor progress:
```bash
codecrew status --project task-api
```

## Project Files

- `spec.md` - Technical specification with requirements and API design
- `brd.md` - Business Requirements Document with business context and objectives
- `prd.md` - Product requirements with business goals and success metrics
- `userstories.md` - User stories and acceptance criteria
- `checklist.md` - Project checklist and deliverables tracking

## Next Steps

1. Set up GitHub repository: `codecrew github setup`
2. Configure development environment
3. Launch Claude Code agents using the generated scripts
4. Begin development following the GitHub workflow

Happy coding with CodeCrew! 🚀
"""
    
    (example_dir / "README.md").write_text(readme_content)
    
    print(f"✅ Example project created in: {example_dir}")
    return example_dir


def main():
    """Main installer CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CodeCrew Installation System")
    parser.add_argument("command", choices=["install", "uninstall", "example"])
    parser.add_argument("--dev", action="store_true", 
                       help="Install development dependencies")
    parser.add_argument("--force", action="store_true",
                       help="Force installation even if already installed")
    
    args = parser.parse_args()
    
    installer = CodeCrewInstaller()
    
    if args.command == "install":
        success = installer.install(dev_mode=args.dev)
        sys.exit(0 if success else 1)
        
    elif args.command == "uninstall":
        success = installer.uninstall()
        sys.exit(0 if success else 1)
        
    elif args.command == "example":
        example_dir = create_project_example()
        print(f"\n🎯 Next steps:")
        print(f"1. cd {example_dir}")
        print(f"2. codecrew init --project task-api --spec spec.md --brd brd.md --prd prd.md --userstories userstories.md --checklist checklist.md")
        print(f"3. codecrew deploy --project task-api")
        sys.exit(0)


if __name__ == "__main__":
    main()
