#!/usr/bin/env python3
"""
CodeCrew CLI Interface
Complete command-line interface for CodeCrew system
"""

import sys
import argparse
import json
import subprocess
import asyncio
from pathlib import Path
from typing import Optional
import logging

from .main import CodeCrewOrchestrator

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
        print(f"🚀 Initializing CodeCrew project: {args.project}")
        
        orchestrator = self.setup_orchestrator()
        
        try:
            project_path = Path(args.path) if args.path else None
            project = orchestrator.init_project(
                project_name=args.project,
                spec_file=args.spec,
                brd_file=args.brd,
                prd_file=args.prd,
                userstories_file=args.userstories,
                checklist_file=args.checklist,
                project_path=project_path
            )
            
            print(f"✅ Project '{args.project}' initialized successfully!")
            print(f"📁 Project path: {project.path}")
            print(f"📊 Complexity: {project.complexity}")
            print(f"\n🎯 Next steps:")
            print(f"1. codecrew deploy --project {args.project}")
            print(f"2. codecrew status --project {args.project}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error initializing project: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1

    def cmd_deploy(self, args):
        """Deploy development team"""
        print(f"🚀 Deploying development team for: {args.project}")
        
        orchestrator = self.setup_orchestrator()
        
        try:
            agents = orchestrator.deploy_agents(args.project)
            
            print(f"✅ Deployed {len(agents)} agents:")
            for agent in agents:
                print(f"  🤖 {agent.role.value} ({agent.id})")
            
            print(f"\n🎯 Team is ready! Use 'codecrew start --project {args.project}' to begin development.")
            return 0

        except Exception as e:
            print(f"❌ Error deploying team: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1

    def cmd_start(self, args):
        """Start development work for a project"""
        print(f"🚀 Starting development for project: {args.project}")

        orchestrator = self.setup_orchestrator()

        try:
            # Run the async start_development method
            success = asyncio.run(orchestrator.start_development(args.project))

            if success:
                print(f"✅ Development completed successfully for project '{args.project}'!")
                print(f"\n🎯 Next steps:")
                print(f"1. Review the generated code")
                print(f"2. Run tests: pytest")
                print(f"3. Check git status: git status")
            else:
                print(f"❌ Development failed for project '{args.project}'")
                print(f"Check logs for details: ~/.codecrew/logs/codecrew.log")
                return 1

            return 0

        except Exception as e:
            print(f"❌ Error starting development: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1

    def cmd_status(self, args):
        """Show project and agent status"""
        orchestrator = self.setup_orchestrator()
        
        try:
            if args.project:
                print(f"📊 Status for project: {args.project}")
                status = orchestrator.get_project_status(args.project)
                
                if "error" in status:
                    print(f"❌ {status['error']}")
                    return 1
                
                # Project info
                project = status["project"]
                project_path = Path(project['path'])
                print(f"\n📁 Project: {project['name']}")
                print(f"   Path: {project['path']}")
                print(f"   Complexity: {project['complexity']}")
                print(f"   Created: {project['created_at']}")

                # Development status
                dev_status = orchestrator.get_development_status(args.project)
                if dev_status.get("status") == "active":
                    session = dev_status["session"]
                    print(f"\n🚀 Development Session:")
                    print(f"   Phase: {session['current_phase']}")
                    print(f"   Progress: {session['progress_percent']}% ({session['completed_tasks']}/{session['total_tasks']} tasks)")
                    print(f"   Started: {session['started_at']}")
                    if session['active_agents']:
                        print(f"   Active agents: {len(session['active_agents'])}")

                # Agents info
                agents = status["agents"]
                if agents:
                    print(f"\n🤖 Agents ({len(agents)}):")
                    for agent in agents:
                        status_emoji = {
                            "idle": "⏸️",
                            "working": "🔄",
                            "blocked": "🚫",
                            "completed": "✅",
                            "error": "❌"
                        }.get(agent["status"], "❓")

                        print(f"   {status_emoji} {agent['role']} - {agent['status']}")
                        if args.detailed:
                            print(f"      Task: {agent['task']}")
                            print(f"      Last check-in: {agent['last_checkin']}")
                else:
                    print("\n🤖 No agents deployed yet. Run 'codecrew deploy' to deploy team.")

                # Task breakdown (if development is active)
                if dev_status.get("status") == "active" and args.detailed:
                    tasks = dev_status.get("tasks", {})
                    if tasks:
                        print(f"\n📋 Task Breakdown:")
                        for task_status, count in tasks.items():
                            if count > 0:
                                emoji = {
                                    "pending": "⏳",
                                    "in_progress": "🔄",
                                    "completed": "✅",
                                    "failed": "❌",
                                    "blocked": "🚫"
                                }.get(task_status, "❓")
                                print(f"   {emoji} {task_status.replace('_', ' ').title()}: {count}")

                # Communication summary (if detailed)
                if args.detailed:
                    try:
                        from .communication import AgentCommunicationHub
                        comm_hub = AgentCommunicationHub(project_path)
                        comm_summary = comm_hub.get_communication_summary()

                        if comm_summary["total_messages"] > 0:
                            print(f"\n💬 Communication:")
                            print(f"   Total messages: {comm_summary['total_messages']}")
                            if comm_summary["unread_messages"] > 0:
                                print(f"   Unread: {comm_summary['unread_messages']}")
                            print(f"   Recent (24h): {comm_summary['recent_messages_24h']}")
                    except Exception as e:
                        logger.debug(f"Could not load communication summary: {e}")
                
                # GitHub status
                if status.get("github_status"):
                    gh_status = status["github_status"]
                    if "error" not in gh_status:
                        print(f"\n🐙 GitHub: {gh_status.get('owner', {}).get('login', 'unknown')}/{gh_status.get('name', 'unknown')}")
                        print(f"   URL: {gh_status.get('url', 'unknown')}")
                
            else:
                print("📊 CodeCrew System Status")
                status = orchestrator.get_project_status()
                
                projects = status["projects"]
                if projects:
                    print(f"\n📁 Projects ({len(projects)}):")
                    for name, project in projects.items():
                        print(f"   📂 {name} ({project['complexity']})")
                        if args.detailed:
                            print(f"      Path: {project['path']}")
                            print(f"      Created: {project['created_at']}")
                else:
                    print("\n📁 No projects found. Run 'codecrew init' to create a project.")
                
                print(f"\n🤖 Total agents: {status['total_agents']}")
                print(f"🐙 GitHub CLI: {'✅ Available' if status['github_available'] else '❌ Not available'}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1

    def cmd_doctor(self, args):
        """System health check and diagnostics"""
        print("🏥 CodeCrew System Health Check")
        print("=" * 40)
        
        issues_found = 0
        
        # Python environment
        print(f"\n🐍 Python Environment:")
        print(f"✅ Python {sys.version.split()[0]}")
        
        # Required tools
        print(f"\n🔧 Required Tools:")
        tools = [
            ("git", "Version control"),
            ("gh", "GitHub CLI"),
            ("docker", "Docker containerization"),
            ("claude", "Claude CLI")
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
        
        # Python packages
        print(f"\n📦 Python Packages:")
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
        
        # CodeCrew state
        print(f"\n🤖 CodeCrew State:")
        codecrew_dir = Path.home() / ".codecrew"
        if codecrew_dir.exists():
            print(f"✅ CodeCrew directory exists")
            
            # Check for agent workspaces
            agents_dir = codecrew_dir / "agents"
            if agents_dir.exists() and list(agents_dir.iterdir()):
                agent_count = len(list(agents_dir.iterdir()))
                print(f"✅ {agent_count} agent workspace(s) found")
            else:
                print(f"ℹ️  No agent workspaces found")
            
            # Check templates
            templates_dir = codecrew_dir / "templates"
            if templates_dir.exists():
                print(f"✅ Templates directory exists")
            else:
                print(f"⚠️  Templates directory missing (run 'codecrew templates setup')")
                issues_found += 1
        else:
            print(f"⚠️  CodeCrew directory missing")
            issues_found += 1
        
        # GitHub integration
        print(f"\n🔗 GitHub Integration:")
        try:
            result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ GitHub CLI authenticated")
            else:
                print(f"⚠️  GitHub CLI not authenticated")
                issues_found += 1
        except FileNotFoundError:
            print(f"❌ GitHub CLI not available")
            issues_found += 1
        
        # Summary
        print(f"\n📊 Health Check Summary:")
        if issues_found == 0:
            print(f"🎉 All systems operational!")
            return 0
        else:
            print(f"⚠️  Found {issues_found} issues that need attention.")
            
            print(f"\n💡 Recommended actions:")
            print(f"1. Install missing tools and dependencies")
            print(f"2. Run 'codecrew templates setup' if templates are missing")
            print(f"3. Authenticate with GitHub CLI: 'gh auth login'")
            print(f"4. Initialize CodeCrew in your project: 'codecrew init'")
            
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
  codecrew start --project myapp
  codecrew status --project myapp --detailed
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

    # Start command
    start_parser = subparsers.add_parser("start", help="Start development work")
    start_parser.add_argument("--project", required=True, help="Project name")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show project and agent status")
    status_parser.add_argument("--project", help="Project name (show all if not specified)")
    status_parser.add_argument("--detailed", action="store_true", help="Show detailed information")

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

    # Enable debug logging for start command
    if hasattr(args, 'command') and args.command == 'start':
        logging.getLogger('codecrew.execution').setLevel(logging.DEBUG)
    
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
            "start": cli.cmd_start,
            "status": cli.cmd_status,
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
