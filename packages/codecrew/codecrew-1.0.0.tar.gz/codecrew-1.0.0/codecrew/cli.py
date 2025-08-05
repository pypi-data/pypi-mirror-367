#!/usr/bin/env python3
"""
CodeCrew CLI - Complete Command Line Interface
Main entry point for the CodeCrew multi-agent development system
"""

import sys
import os
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from .main import CodeCrewOrchestrator, AgentRole, ProjectComplexity
    from codecrew_templates import CodeCrewTemplates
except ImportError as e:
    print(f"Error importing CodeCrew modules: {e}")
    print("Make sure you're running from the CodeCrew project directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodeCrewCLI:
    """Complete CLI interface for CodeCrew system"""
    
    def __init__(self):
        self.orchestrator = None
        self.current_dir = Path.cwd()
        
    def setup_orchestrator(self, project_root: Optional[Path] = None):
        """Initialize orchestrator if not already set up"""
        if self.orchestrator is None:
            root_path = project_root or self.current_dir
            self.orchestrator = CodeCrewOrchestrator(root_path)
        return self.orchestrator
    
    def cmd_init(self, args):
        """Initialize a new CodeCrew project"""
        print("🚀 Initializing CodeCrew project...")
        
        # Validate required arguments
        if not all([args.project, args.spec, args.brd, args.prd, args.userstories, args.checklist]):
            print("❌ Error: --project, --spec, --brd, --prd, --userstories, and --checklist are required")
            return 1
        
        # Validate files exist
        spec_file = Path(args.spec)
        brd_file = Path(args.brd)
        prd_file = Path(args.prd)
        userstories_file = Path(args.userstories)
        checklist_file = Path(args.checklist)

        missing_files = []
        for file_path, name in [(spec_file, "spec"), (brd_file, "BRD"), (prd_file, "PRD"),
                               (userstories_file, "user stories"), (checklist_file, "checklist")]:
            if not file_path.exists():
                missing_files.append(f"{name}: {file_path}")
        
        if missing_files:
            print("❌ Required files not found:")
            for file_info in missing_files:
                print(f"   - {file_info}")
            return 1
        
        # Set up orchestrator
        orchestrator = self.setup_orchestrator(Path(args.path) if args.path else None)
        
        try:
            # Initialize project
            project = orchestrator.initialize_project(
                project_name=args.project,
                project_path=Path(args.path) if args.path else self.current_dir,
                spec_file=spec_file,
                brd_file=brd_file,
                prd_file=prd_file,
                userstories_file=userstories_file,
                checklist_file=checklist_file
            )
            
            print(f"✅ Project '{args.project}' initialized successfully!")
            print(f"📁 Project path: {project.path}")
            print(f"🏗️  Complexity: {project.complexity.value}")
            
            if project.github_repo:
                print(f"🔗 GitHub repository: {project.github_repo}")
                print(f"🎯 Current milestone: {project.current_milestone or 'None'}")
            
            # Display next steps
            print("\n📋 Next steps:")
            print("1. Review the created project structure and templates")
            print("2. Configure your .env file with appropriate settings")
            print("3. Deploy your development team with: codecrew deploy --project", args.project)
            print("4. Start development with GitHub workflow integration")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error initializing project: {e}")
            logger.error(f"Project initialization failed: {e}", exc_info=True)
            return 1
    
    def cmd_deploy(self, args):
        """Deploy development team for a project"""
        print("👥 Deploying development team...")
        
        if not args.project:
            print("❌ Error: --project is required")
            return 1
        
        orchestrator = self.setup_orchestrator()
        
        try:
            # Deploy team
            agents = orchestrator.deploy_development_team(args.project)
            
            print(f"✅ Deployed {len(agents)} agents for project '{args.project}'")
            print("\n👥 Team composition:")
            
            for agent in agents:
                status_icon = "🟢" if agent.status.value == "initializing" else "🔴"
                print(f"   {status_icon} {agent.role.value.title()}: {agent.id}")
                print(f"      Task: {agent.current_task}")
                print(f"      Workspace: {agent.workspace_dir}")
                print(f"      Launch: {agent.workspace_dir}/launch_claude_code.sh")
                print()
            
            # Display launch instructions
            print("🚀 How to start working:")
            print("1. Each agent has a dedicated workspace with:")
            print("   - Complete briefing and instructions")
            print("   - Claude Code launcher script")
            print("   - Status tracking and communication files")
            print()
            print("2. Launch Claude Code for each agent:")
            for agent in agents:
                print(f"   {agent.role.value}: {agent.workspace_dir}/launch_claude_code.sh")
            print()
            print("3. Monitor progress with: codecrew status --project", args.project)
            
            return 0
            
        except Exception as e:
            print(f"❌ Error deploying team: {e}")
            logger.error(f"Team deployment failed: {e}", exc_info=True)
            return 1
    
    def cmd_status(self, args):
        """Show project and agent status"""
        orchestrator = self.setup_orchestrator()
        
        if args.project:
            # Show specific project status
            try:
                status = orchestrator.get_project_status(args.project)
                
                if "error" in status:
                    print(f"❌ {status['error']}")
                    return 1
                
                self._display_project_status(args.project, status, args.detailed)
                return 0
                
            except Exception as e:
                print(f"❌ Error getting project status: {e}")
                return 1
        else:
            # Show all projects status
            try:
                print("📊 CodeCrew System Status")
                print("=" * 50)
                
                if not orchestrator.projects:
                    print("No projects found. Use 'codecrew init' to create a project.")
                    return 0
                
                for project_name in orchestrator.projects:
                    status = orchestrator.get_project_status(project_name)
                    self._display_project_status(project_name, status, brief=not args.detailed)
                    print()
                
                return 0
                
            except Exception as e:
                print(f"❌ Error getting system status: {e}")
                return 1
    
    def _display_project_status(self, project_name: str, status: Dict[str, Any], detailed: bool = False, brief: bool = False):
        """Display formatted project status"""
        
        project_info = status.get("project", {})
        agents_info = status.get("agents", {})
        github_info = status.get("github", {})
        summary = status.get("summary", {})
        
        # Project header
        print(f"📁 Project: {project_name}")
        print(f"   Complexity: {project_info.get('complexity', 'unknown')}")
        print(f"   Created: {project_info.get('created_at', 'unknown')[:10]}")
        
        if project_info.get('github_repo'):
            print(f"   GitHub: {project_info['github_repo']}")
            
        if project_info.get('current_milestone'):
            print(f"   Milestone: {project_info['current_milestone']}")
        
        # Summary metrics
        print(f"   Agents: {summary.get('total_agents', 0)} total, "
              f"{summary.get('active_agents', 0)} active, "
              f"{summary.get('blocked_agents', 0)} blocked")
        
        if brief:
            return
        
        # Agent details
        if agents_info:
            print("\n👥 Team Status:")
            for agent_id, agent_info in agents_info.items():
                status_icons = {
                    "working": "🟢",
                    "blocked": "🔴", 
                    "idle": "🟡",
                    "initializing": "🔵",
                    "completed": "✅"
                }
                
                status_icon = status_icons.get(agent_info.get('status', 'unknown'), "❓")
                role = agent_info.get('role', 'unknown').replace('_', ' ').title()
                
                print(f"   {status_icon} {role}")
                print(f"      Status: {agent_info.get('status', 'unknown')}")
                print(f"      Task: {agent_info.get('current_task', 'None')}")
                print(f"      Issues: {agent_info.get('assigned_issues', 0)}")
                print(f"      Blockers: {agent_info.get('blockers', 0)}")
                print(f"      Last Check-in: {agent_info.get('last_checkin', 'Never')[:16]}")
                
                if detailed:
                    metrics = agent_info.get('metrics', {})
                    print(f"      Metrics:")
                    print(f"        Issues Completed: {metrics.get('issues_completed', 0)}")
                    print(f"        PRs Created: {metrics.get('prs_created', 0)}")
                    print(f"        Commits: {metrics.get('commits_made', 0)}")
                print()
        
        # GitHub status
        if github_info and not github_info.get('error'):
            print("🔗 GitHub Status:")
            repo_info = github_info.get('repo_info', {})
            if repo_info:
                print(f"   Repository: {repo_info.get('owner', {}).get('login', '')}/{repo_info.get('name', '')}")
                print(f"   Default Branch: {repo_info.get('defaultBranchRef', {}).get('name', 'main')}")
            
            print(f"   Open Issues: {github_info.get('open_issues', 0)}")
            print(f"   Open PRs: {github_info.get('open_prs', 0)}")
            print(f"   Recent Commits: {github_info.get('recent_commits', 0)} (last week)")
        
        # Quality metrics
        quality_info = status.get("quality", {})
        if quality_info and detailed:
            print("\n📊 Quality Metrics:")
            for metric, value in quality_info.items():
                if isinstance(value, (int, float)):
                    print(f"   {metric.replace('_', ' ').title()}: {value}")
    
    def cmd_schedule(self, args):
        """Schedule a check-in or task"""
        orchestrator = self.setup_orchestrator()
        
        try:
            note = args.note or "Scheduled check-in"
            orchestrator.schedule_checkin(
                minutes=args.minutes,
                note=note,
                agent_id=args.agent,
                recurring=args.recurring
            )
            
            print(f"⏰ Scheduled task in {args.minutes} minutes: {note}")
            if args.agent:
                print(f"   Target agent: {args.agent}")
            if args.recurring:
                print(f"   Recurring: Every {args.minutes} minutes")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error scheduling task: {e}")
            return 1
    
    def cmd_templates(self, args):
        """Manage project templates"""
        
        if args.template_command == "setup":
            print("🔧 Setting up project templates...")
            templates = CodeCrewTemplates(Path(args.path) if args.path else self.current_dir)
            
            try:
                templates.setup_all_templates(args.project_type)
                print(f"✅ Templates set up for project type: {args.project_type}")
                return 0
            except Exception as e:
                print(f"❌ Error setting up templates: {e}")
                return 1
                
        elif args.template_command == "list":
            print("📋 Available templates:")
            templates = CodeCrewTemplates(Path(args.path) if args.path else self.current_dir)
            
            template_categories = [
                ("GitHub Workflows", ".github/workflows"),
                ("Issue Templates", ".github/ISSUE_TEMPLATE"),
                ("Agent Briefings", ".codecrew/templates/agents"),
                ("Communication", ".codecrew/templates/communication"),
                ("Quality Standards", ".codecrew/templates/quality"),
                ("Documentation", ".codecrew/templates/documentation"),
                ("Configuration", ".codecrew/templates/configuration")
            ]
            
            for category, path in template_categories:
                full_path = templates.project_path / path
                if full_path.exists():
                    print(f"\n🗂️  {category}:")
                    for template_file in full_path.glob("*"):
                        if template_file.is_file():
                            print(f"   - {template_file.name}")
                else:
                    print(f"\n❌ {category}: Not found (run 'templates setup' first)")
            
            return 0
            
        elif args.template_command == "validate":
            print("🔍 Validating template completeness...")
            templates = CodeCrewTemplates(Path(args.path) if args.path else self.current_dir)
            
            required_templates = [
                ".github/workflows/ci.yml",
                ".github/ISSUE_TEMPLATE/feature_request.md",
                ".github/PULL_REQUEST_TEMPLATE.md",
                ".codecrew/templates/agents/project_manager_briefing.md",
                ".codecrew/templates/agents/developer_briefing.md",
                ".codecrew/templates/communication/status_update.md",
                ".codecrew/templates/quality/quality_checklist.md"
            ]
            
            all_present = True
            for template_path in required_templates:
                full_path = templates.project_path / template_path
                if full_path.exists():
                    print(f"✅ {template_path}")
                else:
                    print(f"❌ {template_path} - MISSING")
                    all_present = False
            
            if all_present:
                print("\n🎉 All required templates are present!")
                return 0
            else:
                print("\n⚠️  Some templates are missing. Run 'codecrew templates setup' to create them.")
                return 1
    
    def cmd_agents(self, args):
        """Manage agents"""
        orchestrator = self.setup_orchestrator()
        
        if args.agent_command == "list":
            print("👥 Active Agents:")
            
            if not orchestrator.agents:
                print("No agents found. Use 'codecrew deploy' to create agents.")
                return 0
            
            for agent_id, agent in orchestrator.agents.items():
                status_icons = {
                    "working": "🟢",
                    "blocked": "🔴",
                    "idle": "🟡", 
                    "initializing": "🔵",
                    "completed": "✅"
                }
                
                status_icon = status_icons.get(agent.status.value, "❓")
                role = agent.role.value.replace('_', ' ').title()
                
                print(f"\n{status_icon} {role} ({agent_id})")
                print(f"   Status: {agent.status.value}")
                print(f"   Task: {agent.current_task}")
                print(f"   Directory: {agent.work_directory}")
                print(f"   Workspace: {agent.workspace_dir}")
                print(f"   Created: {agent.created_at.isoformat()[:16]}")
                print(f"   Last Check-in: {agent.last_checkin.isoformat()[:16]}")
                
                if agent.assigned_issues:
                    print(f"   Issues: {', '.join(agent.assigned_issues)}")
                
                if agent.blockers:
                    print(f"   Blockers: {len(agent.blockers)}")
                
                if args.detailed:
                    metrics = agent.metrics
                    print(f"   Metrics:")
                    print(f"     Issues Completed: {metrics.get('issues_completed', 0)}")
                    print(f"     PRs Created: {metrics.get('prs_created', 0)}")
                    print(f"     PRs Reviewed: {metrics.get('prs_reviewed', 0)}")
                    print(f"     Commits Made: {metrics.get('commits_made', 0)}")
            
            return 0
            
        elif args.agent_command == "launch":
            if not args.agent_id:
                print("❌ Error: --agent-id is required for launch command")
                return 1
            
            agent = orchestrator.agents.get(args.agent_id)
            if not agent:
                print(f"❌ Agent {args.agent_id} not found")
                return 1
            
            launch_script = agent.workspace_dir / "launch_claude_code.sh"
            if not launch_script.exists():
                print(f"❌ Launch script not found: {launch_script}")
                return 1
            
            print(f"🚀 Launching Claude Code for {agent.role.value}...")
            print(f"Agent: {agent_id}")
            print(f"Script: {launch_script}")
            
            # Make script executable and run it
            try:
                launch_script.chmod(0o755)
                subprocess.run([str(launch_script)], check=True)
                return 0
            except subprocess.CalledProcessError as e:
                print(f"❌ Error launching Claude Code: {e}")
                return 1
    
    def cmd_github(self, args):
        """GitHub integration commands"""
        
        if args.github_command == "status":
            print("🔗 GitHub Integration Status:")
            
            # Check GitHub CLI
            try:
                result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ GitHub CLI installed")
                    version = result.stdout.split('\n')[0]
                    print(f"   Version: {version}")
                else:
                    print("❌ GitHub CLI not working properly")
                    return 1
            except FileNotFoundError:
                print("❌ GitHub CLI not installed")
                print("   Install from: https://cli.github.com/")
                return 1
            
            # Check authentication
            try:
                result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ GitHub CLI authenticated")
                    print("   " + result.stdout.strip().split('\n')[0])
                else:
                    print("❌ GitHub CLI not authenticated")
                    print("   Run: gh auth login")
                    return 1
            except Exception as e:
                print(f"❌ Error checking GitHub auth: {e}")
                return 1
            
            # Check repository
            try:
                result = subprocess.run(["gh", "repo", "view", "--json", "name,owner"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    repo_info = json.loads(result.stdout)
                    print("✅ GitHub repository detected")
                    print(f"   Repository: {repo_info['owner']['login']}/{repo_info['name']}")
                else:
                    print("❌ Not in a GitHub repository")
                    print("   Initialize with: gh repo create")
            except Exception as e:
                print(f"⚠️  Could not detect repository: {e}")
            
            return 0
            
        elif args.github_command == "setup":
            print("🔧 Setting up GitHub integration...")
            
            # Verify we're in a git repo
            if not (Path.cwd() / ".git").exists():
                print("❌ Not in a Git repository. Initialize with: git init")
                return 1
            
            try:
                # Create GitHub repository if it doesn't exist
                result = subprocess.run(["gh", "repo", "view"], capture_output=True)
                if result.returncode != 0:
                    print("📁 Creating GitHub repository...")
                    repo_name = Path.cwd().name
                    result = subprocess.run([
                        "gh", "repo", "create", repo_name, 
                        "--private", "--push", "--source", "."
                    ], check=True)
                    print("✅ GitHub repository created")
                
                # Set up branch protection
                print("🛡️  Setting up branch protection...")
                try:
                    subprocess.run([
                        "gh", "api", "repos/:owner/:repo/branches/main/protection",
                        "--method", "PUT",
                        "--field", "required_status_checks={\"strict\":true,\"contexts\":[]}",
                        "--field", "enforce_admins=true", 
                        "--field", "required_pull_request_reviews={\"required_approving_review_count\":1}"
                    ], check=True, capture_output=True)
                    print("✅ Branch protection enabled")
                except subprocess.CalledProcessError:
                    print("⚠️  Could not set branch protection (may require admin access)")
                
                # Create standard labels
                print("🏷️  Creating standard labels...")
                labels = [
                    ("type:feature", "0052cc", "New feature or enhancement"),
                    ("type:bug", "d73a4a", "Something isn't working"),
                    ("priority:high", "b60205", "High priority"),
                    ("status:in-progress", "ff9500", "Currently being worked on")
                ]
                
                for label, color, description in labels:
                    try:
                        subprocess.run([
                            "gh", "label", "create", label,
                            "--color", color, "--description", description
                        ], capture_output=True)
                    except subprocess.CalledProcessError:
                        pass  # Label might already exist
                
                print("✅ GitHub integration setup complete")
                return 0
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Error setting up GitHub integration: {e}")
                return 1
    
    def cmd_quality(self, args):
        """Quality assurance commands"""
        
        if args.quality_command == "check":
            print("🔍 Running quality checks...")
            
            checks_passed = 0
            total_checks = 0
            
            # Check if we're in a Python project
            if not Path("pyproject.toml").exists() and not Path("setup.py").exists():
                print("❌ Not a Python project (no pyproject.toml or setup.py found)")
                return 1
            
            # Test coverage check
            total_checks += 1
            print("\n📊 Checking test coverage...")
            try:
                result = subprocess.run([
                    "python", "-m", "pytest", "--cov=src", "--cov-report=term-missing", 
                    "--tb=no", "-q"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Tests passing")
                    # Extract coverage percentage
                    for line in result.stdout.split('\n'):
                        if "TOTAL" in line and "%" in line:
                            coverage = line.split()[-1].replace('%', '')
                            if float(coverage) >= 80:
                                print(f"✅ Test coverage: {coverage}% (≥80% required)")
                                checks_passed += 1
                            else:
                                print(f"❌ Test coverage: {coverage}% (<80% required)")
                            break
                    else:
                        print("⚠️  Could not determine coverage percentage")
                else:
                    print("❌ Tests failing")
                    if args.verbose:
                        print(result.stdout)
                        print(result.stderr)
            except FileNotFoundError:
                print("❌ pytest not found (install with: pip install pytest pytest-cov)")
            
            # Code style check
            total_checks += 1
            print("\n🎨 Checking code style...")
            try:
                result = subprocess.run(["black", "--check", "src/", "tests/"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Code formatting (Black)")
                    checks_passed += 1
                else:
                    print("❌ Code formatting issues found")
                    if args.verbose:
                        print(result.stdout)
            except FileNotFoundError:
                print("❌ Black not found (install with: pip install black)")
            
            # Linting check
            total_checks += 1
            print("\n🔍 Checking code linting...")
            try:
                result = subprocess.run(["flake8", "src/", "tests/"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Code linting (flake8)")
                    checks_passed += 1
                else:
                    print("❌ Linting issues found")
                    if args.verbose:
                        print(result.stdout)
            except FileNotFoundError:
                print("❌ flake8 not found (install with: pip install flake8)")
            
            # Type checking
            total_checks += 1
            print("\n🔬 Checking types...")
            try:
                result = subprocess.run(["mypy", "src/"], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Type checking (mypy)")
                    checks_passed += 1
                else:
                    print("❌ Type checking issues found")
                    if args.verbose:
                        print(result.stdout)
            except FileNotFoundError:
                print("❌ mypy not found (install with: pip install mypy)")
            
            # Security check
            total_checks += 1
            print("\n🔒 Security scan...")
            try:
                result = subprocess.run(["safety", "check"], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Security scan (safety)")
                    checks_passed += 1
                else:
                    print("❌ Security vulnerabilities found")
                    if args.verbose:
                        print(result.stdout)
            except FileNotFoundError:
                print("❌ safety not found (install with: pip install safety)")
            
            # Summary
            print(f"\n📊 Quality Check Summary: {checks_passed}/{total_checks} checks passed")
            
            if checks_passed == total_checks:
                print("🎉 All quality checks passed!")
                return 0
            else:
                print("⚠️  Some quality checks failed. Please address the issues above.")
                return 1
        
        elif args.quality_command == "fix":
            print("🔧 Auto-fixing code quality issues...")
            
            fixes_applied = 0
            
            # Auto-format with Black
            print("\n🎨 Auto-formatting code...")
            try:
                result = subprocess.run(["black", "src/", "tests/"], capture_output=True)
                if result.returncode == 0:
                    print("✅ Code formatted with Black")
                    fixes_applied += 1
                else:
                    print("❌ Error formatting code")
            except FileNotFoundError:
                print("❌ Black not found")
            
            # Fix import order
            print("\n📦 Sorting imports...")
            try:
                result = subprocess.run(["isort", "src/", "tests/", "--profile", "black"], 
                                      capture_output=True)
                if result.returncode == 0:
                    print("✅ Imports sorted with isort")
                    fixes_applied += 1
                else:
                    print("❌ Error sorting imports")
            except FileNotFoundError:
                print("❌ isort not found")
            
            print(f"\n🔧 Applied {fixes_applied} automatic fixes")
            print("💡 Run 'codecrew quality check' to verify remaining issues")
            
            return 0
    
    def cmd_doctor(self, args):
        """System health check and diagnostics"""
        print("🏥 CodeCrew System Health Check")
        print("=" * 40)
        
        issues_found = 0
        
        # Check Python version
        print("\n🐍 Python Environment:")
        python_version = sys.version_info
        if python_version >= (3, 9):
            print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            print(f"❌ Python {python_version.major}.{python_version.minor} (≥3.9 required)")
            issues_found += 1
        
        # Check required tools
        print("\n🔧 Required Tools:")
        tools = [
            ("git", "Git version control"),
            ("gh", "GitHub CLI"),
            ("docker", "Docker containerization"),
            ("claude-code", "Claude Code CLI")
        ]
        
        for tool, description in tools:
            try:
                result = subprocess.run([tool, "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.split('\n')[0]
                    print(f"✅ {tool}: {version}")
                else:
                    print(f"❌ {tool}: Not working properly")
                    issues_found += 1
            except FileNotFoundError:
                print(f"❌ {tool}: Not installed ({description})")
                issues_found += 1
        
        # Check Python packages
        print("\n📦 Python Packages:")
        required_packages = [
            "fastapi", "uvicorn", "pydantic", "sqlalchemy", 
            "pytest", "black", "flake8", "mypy"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package}: Not installed")
                issues_found += 1
        
        # Check CodeCrew state
        print("\n🤖 CodeCrew State:")
        codecrew_dir = Path.cwd() / ".codecrew"
        if codecrew_dir.exists():
            print("✅ CodeCrew directory exists")
            
            # Check for agents
            agents_dir = codecrew_dir / "agents"
            if agents_dir.exists():
                agent_count = len(list(agents_dir.glob("*")))
                print(f"✅ Agent workspaces: {agent_count}")
            else:
                print("ℹ️  No agent workspaces found")
            
            # Check for templates
            templates_dir = codecrew_dir / "templates"
            if templates_dir.exists():
                print("✅ Templates directory exists")
            else:
                print("⚠️  Templates directory missing (run 'codecrew templates setup')")
                issues_found += 1
        else:
            print("ℹ️  CodeCrew not initialized in this directory")
        
        # Check GitHub integration
        print("\n🔗 GitHub Integration:")
        try:
            result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ GitHub CLI authenticated")
                
                # Check if in repo
                result = subprocess.run(["gh", "repo", "view", "--json", "name"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    repo_info = json.loads(result.stdout)
                    print(f"✅ GitHub repository: {repo_info['name']}")
                else:
                    print("ℹ️  Not in a GitHub repository")
            else:
                print("❌ GitHub CLI not authenticated")
                issues_found += 1
        except Exception:
            print("❌ GitHub CLI not available")
            issues_found += 1
        
        # Summary
        print(f"\n📊 Health Check Summary:")
        if issues_found == 0:
            print("🎉 All systems operational! CodeCrew is ready to use.")
            return 0
        else:
            print(f"⚠️  Found {issues_found} issues that need attention.")
            print("\n💡 Recommended actions:")
            print("1. Install missing tools and dependencies")
            print("2. Run 'codecrew templates setup' if templates are missing")
            print("3. Authenticate with GitHub CLI: 'gh auth login'")
            print("4. Initialize CodeCrew in your project: 'codecrew init'")
            return 1


def create_parser():
    """Create the argument parser for CodeCrew CLI"""
    
    parser = argparse.ArgumentParser(
        description="CodeCrew Multi-Agent Development System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codecrew init --project myapp --spec spec.md --brd brd.md --prd prd.md --userstories userstories.md --checklist checklist.md
  codecrew deploy --project myapp
  codecrew status --project myapp --detailed
  codecrew agents list --detailed
  codecrew templates setup --project-type python_api
  codecrew github setup
  codecrew quality check --verbose
  codecrew doctor

For more information, visit: https://github.com/your-org/codecrew
        """
    )
    
    parser.add_argument("--version", action="version", version="CodeCrew 1.0.0")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet output")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new CodeCrew project")
    init_parser.add_argument("--project", required=True, help="Project name")
    init_parser.add_argument("--spec", required=True, help="Specification file path")
    init_parser.add_argument("--brd", required=True, help="Business Requirements Document file path")
    init_parser.add_argument("--prd", required=True, help="PRD file path")
    init_parser.add_argument("--userstories", required=True, help="User Stories file path")
    init_parser.add_argument("--checklist", required=True, help="Checklist file path")
    init_parser.add_argument("--path", help="Project directory path (default: current)")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy development team")
    deploy_parser.add_argument("--project", required=True, help="Project name")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show project and agent status")
    status_parser.add_argument("--project", help="Specific project name")
    status_parser.add_argument("--detailed", action="store_true", help="Show detailed status")
    
    # Schedule command
    schedule_parser = subparsers.add_parser("schedule", help="Schedule a check-in or task")
    schedule_parser.add_argument("--minutes", type=int, default=15, help="Minutes until execution")
    schedule_parser.add_argument("--note", help="Note for the scheduled task")
    schedule_parser.add_argument("--agent", help="Target agent ID")
    schedule_parser.add_argument("--recurring", action="store_true", help="Recurring task")
    
    # Templates command
    templates_parser = subparsers.add_parser("templates", help="Manage project templates")
    templates_subparsers = templates_parser.add_subparsers(dest="template_command")
    
    templates_setup_parser = templates_subparsers.add_parser("setup", help="Set up templates")
    templates_setup_parser.add_argument("--project-type", default="python_api",
                                       choices=["python_api", "ml_project", "web_app"])
    templates_setup_parser.add_argument("--path", help="Project path")
    
    templates_list_parser = templates_subparsers.add_parser("list", help="List available templates")
    templates_list_parser.add_argument("--path", help="Project path")
    
    templates_validate_parser = templates_subparsers.add_parser("validate", help="Validate templates")
    templates_validate_parser.add_argument("--path", help="Project path")
    
    # Agents command
    agents_parser = subparsers.add_parser("agents", help="Manage agents")
    agents_subparsers = agents_parser.add_subparsers(dest="agent_command")
    
    agents_list_parser = agents_subparsers.add_parser("list", help="List all agents")
    agents_list_parser.add_argument("--detailed", action="store_true", help="Show detailed info")
    
    agents_launch_parser = agents_subparsers.add_parser("launch", help="Launch Claude Code for agent")
    agents_launch_parser.add_argument("--agent-id", required=True, help="Agent ID to launch")
    
    # GitHub command
    github_parser = subparsers.add_parser("github", help="GitHub integration")
    github_subparsers = github_parser.add_subparsers(dest="github_command")
    
    github_status_parser = github_subparsers.add_parser("status", help="Check GitHub integration status")
    github_setup_parser = github_subparsers.add_parser("setup", help="Set up GitHub integration")
    
    # Quality command
    quality_parser = subparsers.add_parser("quality", help="Quality assurance tools")
    quality_subparsers = quality_parser.add_subparsers(dest="quality_command")
    
    quality_check_parser = quality_subparsers.add_parser("check", help="Run quality checks")
    quality_check_parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    
    quality_fix_parser = quality_subparsers.add_parser("fix", help="Auto-fix quality issues")
    
    # Doctor command
    doctor_parser = subparsers.add_parser("doctor", help="System health check and diagnostics")
    
    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Configure logging based on verbosity
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create CLI instance
    cli = CodeCrewCLI()
    
    # Route to appropriate command
    try:
        if args.command is None:
            parser.print_help()
            return 0
        
        command_methods = {
            "init": cli.cmd_init,
            "deploy": cli.cmd_deploy, 
            "status": cli.cmd_status,
            "schedule": cli.cmd_schedule,
            "templates": cli.cmd_templates,
            "agents": cli.cmd_agents,
            "github": cli.cmd_github,
            "quality": cli.cmd_quality,
            "doctor": cli.cmd_doctor
        }
        
        if args.command in command_methods:
            return command_methods[args.command](args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
