#!/usr/bin/env python3
"""
CodeCrew: Complete Multi-Agent Collaboration Framework for Claude Code
Full implementation replicating tmux orchestration patterns
"""

import os
import json
import subprocess
import time
import threading
import queue
import signal
import sys
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import yaml
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.codecrew/logs/codecrew.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentRole(Enum):
    ORCHESTRATOR = "orchestrator"
    PROJECT_MANAGER = "project_manager"
    LEAD_DEVELOPER = "lead_developer"
    DEVELOPER = "developer"
    QA_ENGINEER = "qa_engineer"
    DEVOPS = "devops"
    CODE_REVIEWER = "code_reviewer"
    DOCUMENTATION_WRITER = "documentation_writer"

class AgentStatus(Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    WORKING = "working"
    BLOCKED = "blocked"
    WAITING_REVIEW = "waiting_review"
    COMPLETED = "completed"
    ERROR = "error"

class ProjectComplexity(Enum):
    NASCENT = "nascent"        # < 50 commits, minimal issues
    DEVELOPING = "developing"  # < 200 commits, < 20 issues
    ESTABLISHED = "established" # 200+ commits, 20+ issues
    COMPLEX = "complex"        # 500+ commits, 50+ issues

@dataclass
class GitHubContext:
    repo_name: str
    repo_owner: str
    current_branch: str
    default_branch: str
    milestone: Optional[str] = None
    assigned_issues: List[str] = field(default_factory=list)
    open_prs: List[str] = field(default_factory=list)
    last_commit: str = ""
    has_protection: bool = False
    has_issues: bool = True
    has_projects: bool = True

@dataclass
class Agent:
    id: str
    role: AgentRole
    status: AgentStatus
    current_task: Optional[str]
    github_context: Optional[GitHubContext]
    work_directory: Path
    last_checkin: datetime
    created_at: datetime
    workspace_dir: Optional[Path] = None
    claude_code_session: Optional[str] = None
    assigned_issues: List[str] = field(default_factory=list)
    completed_tasks: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Project:
    name: str
    path: Path
    spec_file: Path
    brd_file: Path
    prd_file: Path
    userstories_file: Path
    checklist_file: Path
    github_repo: Optional[str] = None
    current_milestone: Optional[str] = None
    agents: Dict[str, Agent] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    complexity: ProjectComplexity = ProjectComplexity.NASCENT
    quality_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScheduledTask:
    id: str
    run_time: datetime
    note: str
    agent_id: Optional[str] = None
    task_type: str = "checkin"
    recurring: bool = False
    interval_minutes: Optional[int] = None

class CodeCrewOrchestrator:
    """Main orchestrator for multi-agent collaboration system"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.state_dir = self.project_root / ".codecrew"
        self.logs_dir = self.state_dir / "logs"
        self.agents_dir = self.state_dir / "agents"
        self.templates_dir = self.state_dir / "templates"
        
        # Create required directories
        for directory in [self.state_dir, self.logs_dir, self.agents_dir, self.templates_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # State files
        self.projects_file = self.state_dir / "projects.json"
        self.agents_file = self.state_dir / "agents.json"
        self.config_file = self.state_dir / "config.json"
        self.quality_metrics_file = self.state_dir / "quality_metrics.json"
        
        # Load existing state
        self.config = self._load_config()
        self.projects: Dict[str, Project] = self._load_projects()
        self.agents: Dict[str, Agent] = self._load_agents()
        self.scheduled_tasks: List[ScheduledTask] = []
        self.message_queue = queue.Queue()
        
        # GitHub integration
        self.github_available = self._check_github_cli()
        if not self.github_available:
            logger.warning("GitHub CLI not available. Some features will be limited.")
        
        # Scheduler
        self.scheduler_thread = None
        self.scheduler_running = False
        
        # Quality monitoring
        self.quality_monitor_thread = None
        self.quality_monitoring_active = False
        
        logger.info(f"CodeCrew Orchestrator initialized in {self.project_root}")
    
    def initialize_project(self, project_name: str, project_path: Path,
                          spec_file: Path, brd_file: Path, prd_file: Path,
                          userstories_file: Path, checklist_file: Path) -> Project:
        """Initialize a new greenfield Python project with full setup"""
        
        logger.info(f"Initializing project: {project_name}")
        
        project_path = Path(project_path).resolve()
        
        # Verify required files exist
        required_files = [spec_file, brd_file, prd_file, userstories_file, checklist_file]
        for file_path in required_files:
            if not file_path.exists():
                raise FileNotFoundError(f"Required file not found: {file_path}")
        
        # Analyze project complexity
        complexity = self._analyze_project_complexity(project_path)
        
        # Create project structure
        project = Project(
            name=project_name,
            path=project_path,
            spec_file=spec_file,
            brd_file=brd_file,
            prd_file=prd_file,
            userstories_file=userstories_file,
            checklist_file=checklist_file,
            complexity=complexity,
            created_at=datetime.now()
        )
        
        # Initialize Git repository if not exists
        self._ensure_git_repo(project_path)
        
        # Detect/setup GitHub repository
        github_repo = self._detect_github_repo(project_path)
        if github_repo:
            project.github_repo = github_repo
            project.current_milestone = self._get_current_milestone(project_path)
            self._setup_github_workflow(project_path)
        
        # Set up project templates and structure
        from .templates import CodeCrewTemplates
        templates = CodeCrewTemplates(project_path)
        templates.setup_all_templates("python_api")
        
        # Initialize quality monitoring
        self._initialize_quality_metrics(project)
        
        # Create project manager first (replicates tmux PM-first pattern)
        pm_agent = self._create_agent(
            project=project,
            role=AgentRole.PROJECT_MANAGER,
            task="Initialize project management and GitHub workflow setup"
        )
        
        # Save project state
        self.projects[project_name] = project
        self._save_projects()
        
        logger.info(f"Project {project_name} initialized successfully")
        return project
    
    def deploy_development_team(self, project_name: str) -> List[Agent]:
        """Deploy development team based on project complexity analysis"""
        
        if project_name not in self.projects:
            raise ValueError(f"Project {project_name} not found")
        
        project = self.projects[project_name]
        logger.info(f"Deploying development team for {project_name} (complexity: {project.complexity.value})")
        
        agents = []
        
        # Deploy team based on complexity (from original tmux patterns)
        if project.complexity == ProjectComplexity.NASCENT:
            # Simple project: 1 Developer + existing PM
            dev_agent = self._create_agent(
                project=project,
                role=AgentRole.DEVELOPER,
                task="Implement core functionality from specification"
            )
            agents.append(dev_agent)
            
        elif project.complexity == ProjectComplexity.DEVELOPING:
            # Medium project: Lead Dev + Developer + existing PM
            lead_dev = self._create_agent(
                project=project,
                role=AgentRole.LEAD_DEVELOPER,
                task="Architecture implementation and technical leadership"
            )
            dev_agent = self._create_agent(
                project=project,
                role=AgentRole.DEVELOPER,
                task="Feature implementation and testing"
            )
            agents.extend([lead_dev, dev_agent])
            
        elif project.complexity == ProjectComplexity.ESTABLISHED:
            # Large project: Lead + 2 Devs + QA + existing PM
            lead_dev = self._create_agent(
                project=project,
                role=AgentRole.LEAD_DEVELOPER,
                task="Technical leadership and architecture decisions"
            )
            dev1 = self._create_agent(
                project=project,
                role=AgentRole.DEVELOPER,
                task="Core feature development"
            )
            dev2 = self._create_agent(
                project=project,
                role=AgentRole.DEVELOPER,
                task="API and integration development"
            )
            qa_agent = self._create_agent(
                project=project,
                role=AgentRole.QA_ENGINEER,
                task="Testing and quality assurance"
            )
            agents.extend([lead_dev, dev1, dev2, qa_agent])
            
        else:  # COMPLEX
            # Full team: Lead + 3 Devs + QA + DevOps + Docs + existing PM
            lead_dev = self._create_agent(
                project=project,
                role=AgentRole.LEAD_DEVELOPER,
                task="Technical leadership and system architecture"
            )
            dev1 = self._create_agent(
                project=project,
                role=AgentRole.DEVELOPER,
                task="Core API development"
            )
            dev2 = self._create_agent(
                project=project,
                role=AgentRole.DEVELOPER,
                task="Frontend and integration"
            )
            dev3 = self._create_agent(
                project=project,
                role=AgentRole.DEVELOPER,
                task="Database and backend services"
            )
            qa_agent = self._create_agent(
                project=project,
                role=AgentRole.QA_ENGINEER,
                task="Comprehensive testing and quality gates"
            )
            devops_agent = self._create_agent(
                project=project,
                role=AgentRole.DEVOPS,
                task="CI/CD and infrastructure management"
            )
            docs_agent = self._create_agent(
                project=project,
                role=AgentRole.DOCUMENTATION_WRITER,
                task="Technical documentation and API docs"
            )
            agents.extend([lead_dev, dev1, dev2, dev3, qa_agent, devops_agent, docs_agent])
        
        # Initialize agent workspaces and briefings
        for agent in agents:
            self._initialize_agent_workspace(agent)
            self._create_agent_briefing_files(agent)
        
        # Start quality monitoring for the project
        self._start_quality_monitoring(project)
        
        # Schedule initial team coordination
        self.schedule_checkin(15, f"Initial team coordination for {project_name}", None)
        
        logger.info(f"Deployed {len(agents)} agents for project {project_name}")
        return agents
    
    def _create_agent(self, project: Project, role: AgentRole, task: str) -> Agent:
        """Create a new agent with complete setup"""
        
        agent_id = f"{project.name}_{role.value}_{int(time.time())}"
        workspace_dir = self.agents_dir / agent_id
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Get GitHub context for the agent
        github_context = None
        if project.github_repo:
            github_context = self._get_github_context(project.path)
        
        # Create agent
        agent = Agent(
            id=agent_id,
            role=role,
            status=AgentStatus.INITIALIZING,
            current_task=task,
            github_context=github_context,
            work_directory=project.path,
            workspace_dir=workspace_dir,
            last_checkin=datetime.now(),
            created_at=datetime.now()
        )
        
        # Initialize agent metrics
        agent.metrics = {
            "issues_completed": 0,
            "prs_created": 0,
            "prs_reviewed": 0,
            "commits_made": 0,
            "lines_added": 0,
            "lines_removed": 0,
            "blockers_encountered": 0,
            "average_task_completion_hours": 0.0
        }
        
        # Add to project and global agent tracking
        project.agents[agent_id] = agent
        self.agents[agent_id] = agent
        
        # Save state
        self._save_agents()
        self._save_projects()
        
        logger.info(f"Created agent: {agent_id} ({role.value})")
        return agent
    
    def _initialize_agent_workspace(self, agent: Agent):
        """Initialize complete agent workspace"""
        
        workspace = agent.workspace_dir
        
        # Create workspace structure
        directories = [
            workspace / "briefings",
            workspace / "progress",
            workspace / "communication",
            workspace / "scripts"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create agent status file
        status_file = workspace / "status.json"
        status_data = {
            "agent_id": agent.id,
            "role": agent.role.value,
            "status": agent.status.value,
            "current_task": agent.current_task,
            "last_update": datetime.now().isoformat(),
            "work_directory": str(agent.work_directory),
            "assigned_issues": agent.assigned_issues,
            "blockers": agent.blockers,
            "metrics": agent.metrics
        }
        status_file.write_text(json.dumps(status_data, indent=2))
        
        # Create progress tracking file
        progress_file = workspace / "progress" / "current.md"
        progress_template = f"""# Progress Report - {agent.role.value.title()}

## Current Status: {agent.status.value}
- **Agent ID**: {agent.id}
- **Task**: {agent.current_task}
- **Started**: {agent.created_at.isoformat()}
- **Last Update**: {datetime.now().isoformat()}

## Today's Work
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Completed
- [ ] Previous completed items

## Blockers
- None currently

## Notes
Agent initialized and ready for work.
"""
        progress_file.write_text(progress_template)
        
        # Create blockers file
        blockers_file = workspace / "blockers.md"
        blockers_file.write_text("# Current Blockers\n\nNo blockers reported.\n")
        
        # Create Claude Code launch script
        self._create_claude_code_launcher(agent)
        
        logger.info(f"Initialized workspace for agent {agent.id}")
    
    def _create_claude_code_launcher(self, agent: Agent):
        """Create Claude Code launcher script for agent"""
        
        launch_script = agent.workspace_dir / "launch_claude_code.sh"
        
        # Load templates for agent briefing
        from .templates import CodeCrewTemplates
        templates = CodeCrewTemplates(agent.work_directory)
        
        # Get GitHub context for briefing
        github_info = ""
        if agent.github_context:
            github_info = f"""
## GitHub Context
- Repository: {agent.github_context.repo_owner}/{agent.github_context.repo_name}
- Current Branch: {agent.github_context.current_branch}
- Default Branch: {agent.github_context.default_branch}
- Active Milestone: {agent.github_context.milestone or "No active milestone"}
- Has Branch Protection: {'Yes' if agent.github_context.has_protection else 'No'}
"""
        
        script_content = f"""#!/bin/bash
# Claude Code Launcher for {agent.role.value.title()}
# Agent ID: {agent.id}

echo "🚀 Starting Claude Code session for {agent.role.value.title()}"
echo "Agent ID: {agent.id}"
echo "Task: {agent.current_task}"
echo "Workspace: {agent.workspace_dir}"
echo "Project: {agent.work_directory}"
echo ""

# Change to project directory
cd "{agent.work_directory}"

# Display briefing information
echo "📋 AGENT BRIEFING"
echo "=================="
echo "Role: {agent.role.value.title()}"
echo "Responsibility: {agent.current_task}"
{github_info}
echo ""
echo "📁 Important Files:"
echo "- Briefing: {agent.workspace_dir}/briefings/role_briefing.md"
echo "- Status: {agent.workspace_dir}/status.json"
echo "- Progress: {agent.workspace_dir}/progress/current.md"
echo "- Blockers: {agent.workspace_dir}/blockers.md"
echo ""
echo "🔗 GitHub Commands:"
echo "- gh issue list --assignee @me  # Your assigned issues"
echo "- gh pr list --author @me       # Your PRs"
echo "- gh repo view                  # Repository info"
echo ""
echo "⚡ Quick Start:"
echo "1. Read your briefing file"
echo "2. Check assigned GitHub issues"
echo "3. Update your status in status.json"
echo "4. Begin work following GitHub workflow"
echo ""

# Launch Claude Code
echo "Starting Claude Code..."
claude-code

# Update last access time
echo "{{\\"last_access\\": \\"{datetime.now().isoformat()}\\", \\"session_type\\": \\"claude_code\\"}}" > "{agent.workspace_dir}/last_session.json"
"""
        
        launch_script.write_text(script_content)
        launch_script.chmod(0o755)
        
        logger.info(f"Created Claude Code launcher: {launch_script}")
    
    def _create_agent_briefing_files(self, agent: Agent):
        """Create comprehensive agent briefing files"""
        
        from .templates import CodeCrewTemplates
        templates = CodeCrewTemplates(agent.work_directory)
        
        # Get role-specific briefing
        briefing_content = templates.get_agent_briefing(
            agent.role.value,
            agent_id=agent.id,
            project_name=agent.work_directory.name,
            current_task=agent.current_task,
            github_repo=agent.github_context.repo_name if agent.github_context else "Not connected",
            current_branch=agent.github_context.current_branch if agent.github_context else "unknown",
            milestone=agent.github_context.milestone if agent.github_context else "No milestone"
        )
        
        # Save role briefing
        role_briefing_file = agent.workspace_dir / "briefings" / "role_briefing.md"
        role_briefing_file.write_text(briefing_content)
        
        # Create GitHub workflow guide
        github_guide = f"""# GitHub Workflow Guide for {agent.role.value.title()}

## Repository Information
- Repository: {agent.github_context.repo_name if agent.github_context else "Not connected"}
- Your Role: {agent.role.value.title()}
- Current Branch: {agent.github_context.current_branch if agent.github_context else "unknown"}

## Essential GitHub Commands

### Check Your Work
```bash
# See your assigned issues
gh issue list --assignee @me

# See your open PRs  
gh pr list --author @me

# See PRs awaiting your review
gh pr list --review-requested @me
```

### Create New Work
```bash
# Create feature branch
git checkout -b feature/[issue-number]-[description]

# Make commits with conventional format
git commit -m "feat(scope): description

Details about the change

Refs: #[issue-number]"

# Create PR
gh pr create --title "Title" --body "Description

Closes #[issue-number]"
```

### Quality Standards
- Commit every 30 minutes maximum
- Reference issue numbers in commits
- Use conventional commit format
- Test coverage ≥80%
- All CI checks must pass
- Get code review approval before merge

## Communication Protocol
- Update status.json every 30 minutes
- Document progress in progress/current.md
- Report blockers in blockers.md immediately
- Don't stay blocked longer than 10 minutes
"""
        
        github_guide_file = agent.workspace_dir / "briefings" / "github_workflow.md"
        github_guide_file.write_text(github_guide)
        
        # Create quality checklist
        quality_checklist = f"""# Quality Checklist for {agent.role.value.title()}

## Before Starting Work
- [ ] Read project specification files
- [ ] Check assigned GitHub issues
- [ ] Understand current milestone goals
- [ ] Update status to 'working'

## During Development
- [ ] Follow conventional commit format
- [ ] Commit every 30 minutes maximum
- [ ] Reference issue numbers in commits
- [ ] Write tests for new functionality
- [ ] Update documentation as needed

## Before Creating PR
- [ ] All tests pass locally
- [ ] Code coverage ≥80%
- [ ] Linting passes without errors
- [ ] Security checks pass
- [ ] Documentation updated

## PR Creation
- [ ] Use PR template completely
- [ ] Link to related issues
- [ ] Request appropriate reviewers
- [ ] Verify CI passes

## Code Review
- [ ] Address all review comments
- [ ] Update PR description if needed
- [ ] Resolve all conversations
- [ ] Verify final CI passes

## After Merge
- [ ] Update issue status
- [ ] Delete feature branch
- [ ] Update project board
- [ ] Document lessons learned
"""
        
        quality_checklist_file = agent.workspace_dir / "briefings" / "quality_checklist.md"
        quality_checklist_file.write_text(quality_checklist)
        
        logger.info(f"Created briefing files for agent {agent.id}")
    
    def schedule_checkin(self, minutes: int, note: str, agent_id: Optional[str] = None, 
                        recurring: bool = False):
        """Schedule a check-in (replicates tmux scheduling)"""
        
        run_time = datetime.now() + timedelta(minutes=minutes)
        
        task_id = f"checkin_{int(time.time())}_{hashlib.md5(note.encode()).hexdigest()[:8]}"
        scheduled_task = ScheduledTask(
            id=task_id,
            run_time=run_time,
            note=note,
            agent_id=agent_id,
            task_type="checkin",
            recurring=recurring,
            interval_minutes=minutes if recurring else None
        )
        
        self.scheduled_tasks.append(scheduled_task)
        
        # Start scheduler if not running
        if not self.scheduler_thread or not self.scheduler_thread.is_alive():
            self._start_scheduler()
        
        logger.info(f"Scheduled check-in in {minutes} minutes: {note}")
        
        # Save scheduled tasks
        self._save_scheduled_tasks()
    
    def _start_scheduler(self):
        """Start the scheduling system"""
        
        if self.scheduler_running:
            return
        
        self.scheduler_running = True
        
        def scheduler_loop():
            logger.info("Scheduler started")
            while self.scheduler_running:
                try:
                    current_time = datetime.now()
                    
                    # Find tasks ready to run
                    tasks_to_run = [
                        task for task in self.scheduled_tasks 
                        if task.run_time <= current_time
                    ]
                    
                    for task in tasks_to_run:
                        try:
                            self._execute_scheduled_task(task)
                            
                            # Handle recurring tasks
                            if task.recurring and task.interval_minutes:
                                task.run_time = current_time + timedelta(minutes=task.interval_minutes)
                            else:
                                self.scheduled_tasks.remove(task)
                                
                        except Exception as e:
                            logger.error(f"Error executing scheduled task {task.id}: {e}")
                            self.scheduled_tasks.remove(task)
                    
                    # Save updated scheduled tasks
                    if tasks_to_run:
                        self._save_scheduled_tasks()
                    
                    time.sleep(10)  # Check every 10 seconds
                    
                except Exception as e:
                    logger.error(f"Scheduler error: {e}")
                    time.sleep(30)  # Back off on errors
        
        self.scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.scheduler_thread.start()
    
    def _execute_scheduled_task(self, task: ScheduledTask):
        """Execute a scheduled task"""
        
        logger.info(f"🔔 EXECUTING SCHEDULED TASK: {task.note}")
        
        if task.agent_id:
            # Agent-specific check
            agent = self.agents.get(task.agent_id)
            if agent:
                self._check_agent_status(agent)
                self._update_agent_metrics(agent)
            else:
                logger.warning(f"Agent {task.agent_id} not found for scheduled task")
        else:
            # General orchestrator check
            self._orchestrator_checkin()
        
        # Log the execution
        execution_log = {
            "task_id": task.id,
            "executed_at": datetime.now().isoformat(),
            "note": task.note,
            "agent_id": task.agent_id,
            "type": task.task_type
        }
        
        log_file = self.logs_dir / "scheduled_tasks.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(execution_log) + "\n")
    
    def _check_agent_status(self, agent: Agent):
        """Check agent status and detect issues"""
        
        try:
            # Read current status from workspace
            status_file = agent.workspace_dir / "status.json"
            if status_file.exists():
                status_data = json.loads(status_file.read_text())
                last_update = datetime.fromisoformat(status_data["last_update"])
                
                # Check for inactivity
                inactive_time = datetime.now() - last_update
                if inactive_time > timedelta(hours=1):
                    logger.warning(f"⚠️  Agent {agent.id} inactive for {inactive_time}")
                    self._escalate_inactive_agent(agent)
                
                # Update agent status
                agent.status = AgentStatus(status_data.get("status", "idle"))
                agent.last_checkin = last_update
                agent.assigned_issues = status_data.get("assigned_issues", [])
                agent.blockers = status_data.get("blockers", [])
                
            # Check for blockers
            blockers_file = agent.workspace_dir / "blockers.md"
            if blockers_file.exists():
                blockers_content = blockers_file.read_text()
                if len(blockers_content.strip()) > 50:  # More than just header
                    logger.warning(f"🚧 Agent {agent.id} has reported blockers")
                    self._handle_agent_blockers(agent)
            
            # Check GitHub activity
            if agent.github_context:
                self._check_agent_github_activity(agent)
                
        except Exception as e:
            logger.error(f"Error checking agent {agent.id} status: {e}")
    
    def _escalate_inactive_agent(self, agent: Agent):
        """Handle inactive agent escalation"""
        
        escalation_log = {
            "agent_id": agent.id,
            "escalation_type": "inactivity",
            "timestamp": datetime.now().isoformat(),
            "last_checkin": agent.last_checkin.isoformat(),
            "inactive_duration_hours": (datetime.now() - agent.last_checkin).total_seconds() / 3600
        }
        
        # Log escalation
        escalation_file = self.logs_dir / "escalations.jsonl"
        with open(escalation_file, "a") as f:
            f.write(json.dumps(escalation_log) + "\n")
        
        # Create escalation notice
        escalation_notice = f"""# ESCALATION NOTICE - Agent Inactivity

**Agent**: {agent.id} ({agent.role.value})
**Last Check-in**: {agent.last_checkin.isoformat()}
**Inactive Duration**: {(datetime.now() - agent.last_checkin).total_seconds() / 3600:.1f} hours

## Actions Required:
1. Check agent workspace: {agent.workspace_dir}
2. Review last known status and blockers
3. Determine if agent replacement needed
4. Update project timeline if necessary

## Agent Details:
- Current Task: {agent.current_task}
- Status: {agent.status.value}
- Assigned Issues: {', '.join(agent.assigned_issues) if agent.assigned_issues else 'None'}
"""
        
        escalation_file = agent.workspace_dir / "ESCALATION_NOTICE.md"
        escalation_file.write_text(escalation_notice)
        
        logger.error(f"🚨 ESCALATION: Agent {agent.id} inactive for >1 hour")
    
    def _handle_agent_blockers(self, agent: Agent):
        """Handle reported agent blockers"""
        
        try:
            blockers_file = agent.workspace_dir / "blockers.md"
            blockers_content = blockers_file.read_text()
            
            # Parse blockers (simple implementation)
            blockers = []
            lines = blockers_content.split('\n')
            for line in lines:
                if line.strip().startswith('-') or line.strip().startswith('*'):
                    blockers.append(line.strip()[1:].strip())
            
            if blockers:
                # Update agent blockers
                agent.blockers = blockers
                
                # Create blocker resolution notice
                resolution_notice = f"""# BLOCKER RESOLUTION REQUIRED

**Agent**: {agent.id} ({agent.role.value})
**Reported**: {datetime.now().isoformat()}

## Reported Blockers:
{chr(10).join([f"- {blocker}" for blocker in blockers])}

## Resolution Actions:
1. Assign blocker to appropriate team member
2. Escalate to PM if complex dependency
3. Provide alternative work if blocked >10 minutes
4. Update project timeline if necessary

## Agent Status:
- Current Task: {agent.current_task}
- Last Check-in: {agent.last_checkin.isoformat()}
"""
                
                resolution_file = agent.workspace_dir / "BLOCKER_RESOLUTION.md"
                resolution_file.write_text(resolution_notice)
                
                logger.warning(f"🚧 Agent {agent.id} has {len(blockers)} blockers requiring resolution")
                
        except Exception as e:
            logger.error(f"Error handling blockers for agent {agent.id}: {e}")
    
    def _check_agent_github_activity(self, agent: Agent):
        """Check agent's GitHub activity"""
        
        if not self.github_available or not agent.github_context:
            return
        
        try:
            # Change to project directory for GitHub commands
            original_cwd = os.getcwd()
            os.chdir(agent.work_directory)
            
            # Check for recent commits by agent (simplified - would need proper git user mapping)
            result = subprocess.run([
                "git", "log", "--author", "agent", "--since", "1 day ago", "--oneline"
            ], capture_output=True, text=True)
            
            recent_commits = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            agent.metrics["commits_made"] = agent.metrics.get("commits_made", 0) + recent_commits
            
            # Check assigned issues
            result = subprocess.run([
                "gh", "issue", "list", "--assignee", "@me", "--json", "number,title"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                issues = json.loads(result.stdout)
                agent.assigned_issues = [f"#{issue['number']}" for issue in issues]
            
            os.chdir(original_cwd)
            
        except Exception as e:
            logger.error(f"Error checking GitHub activity for agent {agent.id}: {e}")
        finally:
            if 'original_cwd' in locals():
                os.chdir(original_cwd)
    
    def _orchestrator_checkin(self):
        """Perform comprehensive orchestrator check-in"""
        
        logger.info("🎯 Orchestrator Check-in Starting")
        
        checkin_report = {
            "timestamp": datetime.now().isoformat(),
            "projects": {},
            "agents": {},
            "system_health": {},
            "actions_needed": []
        }
        
        # Check each project
        for project_name, project in self.projects.items():
            project_status = {
                "complexity": project.complexity.value,
                "agent_count": len(project.agents),
                "active_agents": 0,
                "blocked_agents": 0,
                "github_status": {}
            }
            
            # Check agents in project
            for agent_id, agent in project.agents.items():
                if agent.status == AgentStatus.WORKING:
                    project_status["active_agents"] += 1
                elif agent.status == AgentStatus.BLOCKED:
                    project_status["blocked_agents"] += 1
                    checkin_report["actions_needed"].append(f"Resolve blockers for agent {agent_id}")
            
            # Check GitHub status if available
            if project.github_repo and self.github_available:
                github_status = self._check_github_status(project.path)
                project_status["github_status"] = github_status
            
            checkin_report["projects"][project_name] = project_status
            
            logger.info(f"Project {project_name}: {project_status['active_agents']} active, "
                       f"{project_status['blocked_agents']} blocked agents")
        
        # System health checks
        checkin_report["system_health"] = {
            "github_cli_available": self.github_available,
            "scheduler_running": self.scheduler_running,
            "total_agents": len(self.agents),
            "scheduled_tasks": len(self.scheduled_tasks)
        }
        
        # Save checkin report
        checkin_file = self.logs_dir / f"orchestrator_checkin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        checkin_file.write_text(json.dumps(checkin_report, indent=2))
        
        # Print summary
        total_active = sum(p["active_agents"] for p in checkin_report["projects"].values())
        total_blocked = sum(p["blocked_agents"] for p in checkin_report["projects"].values())
        
        logger.info(f"🎯 Orchestrator Check-in Complete: {total_active} active agents, "
                   f"{total_blocked} blocked agents across {len(self.projects)} projects")
        
        if checkin_report["actions_needed"]:
            logger.warning(f"⚠️  Actions needed: {len(checkin_report['actions_needed'])}")
            for action in checkin_report["actions_needed"]:
                logger.warning(f"   - {action}")
    
    def _check_github_status(self, project_path: Path) -> Dict[str, Any]:
        """Check GitHub repository status"""
        
        if not self.github_available:
            return {"error": "GitHub CLI not available"}
        
        try:
            original_cwd = os.getcwd()
            os.chdir(project_path)
            
            status = {}
            
            # Get repository info
            result = subprocess.run([
                "gh", "repo", "view", "--json", "name,owner,defaultBranchRef,hasIssuesEnabled"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                repo_info = json.loads(result.stdout)
                status["repo_info"] = repo_info
            
            # Get open issues count
            result = subprocess.run([
                "gh", "issue", "list", "--limit", "1000", "--json", "number"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                issues = json.loads(result.stdout)
                status["open_issues"] = len(issues)
            
            # Get open PRs count
            result = subprocess.run([
                "gh", "pr", "list", "--limit", "1000", "--json", "number"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                prs = json.loads(result.stdout)
                status["open_prs"] = len(prs)
            
            # Get recent activity
            result = subprocess.run([
                "git", "log", "--oneline", "--since", "1 week ago"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
                status["recent_commits"] = len(commits)
            
            os.chdir(original_cwd)
            return status
            
        except Exception as e:
            logger.error(f"Error checking GitHub status: {e}")
            return {"error": str(e)}
        finally:
            if 'original_cwd' in locals():
                os.chdir(original_cwd)
    
    def _update_agent_metrics(self, agent: Agent):
        """Update agent performance metrics"""
        
        try:
            # Update metrics based on current data
            if agent.github_context and self.github_available:
                original_cwd = os.getcwd()
                os.chdir(agent.work_directory)
                
                # Count completed issues (simplified)
                result = subprocess.run([
                    "gh", "issue", "list", "--author", "@me", "--state", "closed", 
                    "--created", ">=1 week ago", "--json", "number"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    closed_issues = json.loads(result.stdout)
                    agent.metrics["issues_completed"] = len(closed_issues)
                
                os.chdir(original_cwd)
            
            # Update status file with new metrics
            self._update_agent_status_file(agent)
            
        except Exception as e:
            logger.error(f"Error updating metrics for agent {agent.id}: {e}")
    
    def _update_agent_status_file(self, agent: Agent):
        """Update agent's status file"""
        
        status_file = agent.workspace_dir / "status.json"
        status_data = {
            "agent_id": agent.id,
            "role": agent.role.value,
            "status": agent.status.value,
            "current_task": agent.current_task,
            "last_update": datetime.now().isoformat(),
            "work_directory": str(agent.work_directory),
            "assigned_issues": agent.assigned_issues,
            "blockers": agent.blockers,
            "metrics": agent.metrics,
            "github_context": asdict(agent.github_context) if agent.github_context else None
        }
        
        status_file.write_text(json.dumps(status_data, indent=2))
    
    # Helper methods for setup and state management
    def _analyze_project_complexity(self, project_path: Path) -> ProjectComplexity:
        """Analyze project complexity to determine team size"""
        
        try:
            if not project_path.exists():
                return ProjectComplexity.NASCENT
            
            # Count commits if git repo exists
            commit_count = 0
            if (project_path / ".git").exists():
                result = subprocess.run([
                    "git", "rev-list", "--count", "HEAD"
                ], cwd=project_path, capture_output=True, text=True)
                
                if result.returncode == 0:
                    commit_count = int(result.stdout.strip())
            
            # Count issues if GitHub repo
            issue_count = 0
            if self.github_available:
                result = subprocess.run([
                    "gh", "issue", "list", "--limit", "1000", "--json", "number"
                ], cwd=project_path, capture_output=True, text=True)
                
                if result.returncode == 0:
                    issues = json.loads(result.stdout)
                    issue_count = len(issues)
            
            # Determine complexity
            if commit_count < 50 and issue_count < 5:
                return ProjectComplexity.NASCENT
            elif commit_count < 200 and issue_count < 20:
                return ProjectComplexity.DEVELOPING
            elif commit_count < 500 and issue_count < 50:
                return ProjectComplexity.ESTABLISHED
            else:
                return ProjectComplexity.COMPLEX
                
        except Exception as e:
            logger.error(f"Error analyzing project complexity: {e}")
            return ProjectComplexity.NASCENT
    
    def _ensure_git_repo(self, project_path: Path):
        """Ensure Git repository is initialized"""
        
        git_dir = project_path / ".git"
        if not git_dir.exists():
            logger.info(f"Initializing Git repository in {project_path}")
            
            try:
                subprocess.run(["git", "init"], cwd=project_path, check=True)
                subprocess.run(["git", "add", "."], cwd=project_path, check=True)
                subprocess.run([
                    "git", "commit", "-m", "Initial commit - CodeCrew project setup"
                ], cwd=project_path, check=True)
                
                logger.info("Git repository initialized successfully")
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Error initializing Git repository: {e}")
    
    def _detect_github_repo(self, project_path: Path) -> Optional[str]:
        """Detect if project is connected to GitHub repository"""
        
        if not self.github_available:
            return None
        
        try:
            result = subprocess.run([
                "gh", "repo", "view", "--json", "nameWithOwner"
            ], cwd=project_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                repo_info = json.loads(result.stdout)
                return repo_info["nameWithOwner"]
                
        except Exception as e:
            logger.error(f"Error detecting GitHub repository: {e}")
        
        return None
    
    def _get_current_milestone(self, project_path: Path) -> Optional[str]:
        """Get current active milestone"""
        
        if not self.github_available:
            return None
        
        try:
            result = subprocess.run([
                "gh", "api", "repos/:owner/:repo/milestones", 
                "--jq", ".[0].title // null"
            ], cwd=project_path, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip() != "null":
                return result.stdout.strip().strip('"')
                
        except Exception as e:
            logger.error(f"Error getting current milestone: {e}")
        
        return None
    
    def _get_github_context(self, project_path: Path) -> Optional[GitHubContext]:
        """Get comprehensive GitHub context for project"""
        
        if not self.github_available:
            return None
        
        try:
            original_cwd = os.getcwd()
            os.chdir(project_path)
            
            # Get repository info
            result = subprocess.run([
                "gh", "repo", "view", "--json", 
                "name,owner,defaultBranchRef,hasIssuesEnabled,hasProjectsEnabled"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return None
            
            repo_info = json.loads(result.stdout)
            
            # Get current branch
            result = subprocess.run([
                "git", "branch", "--show-current"
            ], capture_output=True, text=True)
            
            current_branch = result.stdout.strip() if result.returncode == 0 else "main"
            
            # Check branch protection
            has_protection = False
            result = subprocess.run([
                "gh", "api", f"repos/{repo_info['owner']['login']}/{repo_info['name']}/branches/{repo_info['defaultBranchRef']['name']}/protection"
            ], capture_output=True, text=True)
            
            has_protection = result.returncode == 0
            
            # Get last commit
            result = subprocess.run([
                "git", "log", "-1", "--oneline"
            ], capture_output=True, text=True)
            
            last_commit = result.stdout.strip() if result.returncode == 0 else ""
            
            github_context = GitHubContext(
                repo_name=repo_info["name"],
                repo_owner=repo_info["owner"]["login"],
                current_branch=current_branch,
                default_branch=repo_info["defaultBranchRef"]["name"],
                milestone=self._get_current_milestone(project_path),
                last_commit=last_commit,
                has_protection=has_protection,
                has_issues=repo_info["hasIssuesEnabled"],
                has_projects=repo_info["hasProjectsEnabled"]
            )
            
            os.chdir(original_cwd)
            return github_context
            
        except Exception as e:
            logger.error(f"Error getting GitHub context: {e}")
            return None
        finally:
            if 'original_cwd' in locals():
                os.chdir(original_cwd)
    
    def _setup_github_workflow(self, project_path: Path):
        """Set up GitHub workflow components"""
        
        if not self.github_available:
            logger.warning("GitHub CLI not available, skipping workflow setup")
            return
        
        try:
            original_cwd = os.getcwd()
            os.chdir(project_path)
            
            # Setup branch protection (requires admin access)
            try:
                subprocess.run([
                    "gh", "api", "repos/:owner/:repo/branches/main/protection",
                    "--method", "PUT",
                    "--field", "required_status_checks={\"strict\":true,\"contexts\":[\"continuous-integration\"]}",
                    "--field", "enforce_admins=true",
                    "--field", "required_pull_request_reviews={\"required_approving_review_count\":1,\"dismiss_stale_reviews\":true}"
                ], capture_output=True, text=True)
                
                logger.info("Branch protection configured")
                
            except subprocess.CalledProcessError:
                logger.warning("Could not set up branch protection (may require admin access)")
            
            # Create standard labels
            standard_labels = [
                ("type:feature", "0052cc", "New feature or enhancement"),
                ("type:bug", "d73a4a", "Something isn't working"),
                ("type:chore", "fef2c0", "Maintenance tasks"),
                ("priority:high", "b60205", "High priority"),
                ("priority:medium", "fbca04", "Medium priority"),
                ("priority:low", "0e8a16", "Low priority"),
                ("status:in-progress", "ff9500", "Currently being worked on"),
                ("status:review", "purple", "Ready for review")
            ]
            
            for label, color, description in standard_labels:
                try:
                    subprocess.run([
                        "gh", "label", "create", label, 
                        "--color", color, "--description", description
                    ], capture_output=True, text=True)
                except subprocess.CalledProcessError:
                    pass  # Label might already exist
            
            logger.info("GitHub workflow setup completed")
            os.chdir(original_cwd)
            
        except Exception as e:
            logger.error(f"Error setting up GitHub workflow: {e}")
        finally:
            if 'original_cwd' in locals():
                os.chdir(original_cwd)
    
    def _initialize_quality_metrics(self, project: Project):
        """Initialize quality metrics tracking for project"""
        
        project.quality_metrics = {
            "test_coverage": 0.0,
            "code_complexity": 0.0,
            "security_issues": 0,
            "technical_debt_ratio": 0.0,
            "pr_review_time_avg": 0.0,
            "issue_resolution_time_avg": 0.0,
            "deployment_success_rate": 0.0,
            "uptime": 0.0
        }
    
    def _start_quality_monitoring(self, project: Project):
        """Start quality monitoring for project"""
        
        if self.quality_monitoring_active:
            return
        
        self.quality_monitoring_active = True
        
        def quality_monitor_loop():
            logger.info("Quality monitoring started")
            while self.quality_monitoring_active:
                try:
                    for project_name, proj in self.projects.items():
                        self._update_project_quality_metrics(proj)
                    
                    time.sleep(300)  # Check every 5 minutes
                    
                except Exception as e:
                    logger.error(f"Quality monitoring error: {e}")
                    time.sleep(60)
        
        self.quality_monitor_thread = threading.Thread(target=quality_monitor_loop, daemon=True)
        self.quality_monitor_thread.start()
    
    def _update_project_quality_metrics(self, project: Project):
        """Update project quality metrics"""
        
        try:
            if not project.path.exists():
                return
            
            # Basic quality checks (would be expanded with actual tools)
            metrics = project.quality_metrics
            
            # Check test coverage (if pytest available)
            if (project.path / "requirements-dev.txt").exists():
                try:
                    result = subprocess.run([
                        "python", "-m", "pytest", "--cov=src", "--cov-report=json"
                    ], cwd=project.path, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        # Would parse coverage report
                        metrics["test_coverage"] = 85.0  # Placeholder
                        
                except subprocess.CalledProcessError:
                    pass
            
            # Update timestamp
            metrics["last_updated"] = datetime.now().isoformat()
            
            # Save metrics
            self._save_quality_metrics()
            
        except Exception as e:
            logger.error(f"Error updating quality metrics for {project.name}: {e}")
    
    def _check_github_cli(self) -> bool:
        """Check if GitHub CLI is available and authenticated"""
        
        try:
            # Check if gh command exists
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            # Check authentication
            result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
            return result.returncode == 0
            
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error checking GitHub CLI: {e}")
            return False
    
    # State management methods
    def _load_config(self) -> Dict[str, Any]:
        """Load orchestrator configuration"""
        
        default_config = {
            "version": "1.0.0",
            "project_templates": ["python_api", "ml_project", "web_app"],
            "quality_thresholds": {
                "test_coverage_minimum": 80.0,
                "code_complexity_maximum": 10,
                "security_issues_maximum": 0
            },
            "scheduling": {
                "default_checkin_interval": 15,
                "agent_checkin_interval": 30,
                "quality_check_interval": 300
            },
            "github": {
                "required_reviewers": 1,
                "auto_merge_enabled": False,
                "branch_protection_enabled": True
            }
        }
        
        if not self.config_file.exists():
            self.config_file.write_text(json.dumps(default_config, indent=2))
            return default_config
        
        try:
            return json.loads(self.config_file.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return default_config
    
    def _load_projects(self) -> Dict[str, Project]:
        """Load projects from state file"""
        
        if not self.projects_file.exists():
            return {}
        
        try:
            data = json.loads(self.projects_file.read_text())
            projects = {}
            
            for name, project_data in data.items():
                # Convert data back to Project object
                project = Project(
                    name=project_data["name"],
                    path=Path(project_data["path"]),
                    spec_file=Path(project_data["spec_file"]),
                    brd_file=Path(project_data["brd_file"]),
                    prd_file=Path(project_data["prd_file"]),
                    userstories_file=Path(project_data["userstories_file"]),
                    checklist_file=Path(project_data["checklist_file"]),
                    github_repo=project_data.get("github_repo"),
                    current_milestone=project_data.get("current_milestone"),
                    created_at=datetime.fromisoformat(project_data["created_at"]),
                    complexity=ProjectComplexity(project_data.get("complexity", "nascent")),
                    quality_metrics=project_data.get("quality_metrics", {})
                )
                projects[name] = project
            
            return projects
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error loading projects: {e}")
            return {}
    
    def _save_projects(self):
        """Save projects to state file"""
        
        try:
            data = {}
            for name, project in self.projects.items():
                data[name] = {
                    "name": project.name,
                    "path": str(project.path),
                    "spec_file": str(project.spec_file),
                    "prd_file": str(project.prd_file),
                    "architecture_file": str(project.architecture_file),
                    "github_repo": project.github_repo,
                    "current_milestone": project.current_milestone,
                    "created_at": project.created_at.isoformat(),
                    "complexity": project.complexity.value,
                    "quality_metrics": project.quality_metrics
                }
            
            self.projects_file.write_text(json.dumps(data, indent=2))
            
        except Exception as e:
            logger.error(f"Error saving projects: {e}")
    
    def _load_agents(self) -> Dict[str, Agent]:
        """Load agents from state file"""
        
        if not self.agents_file.exists():
            return {}
        
        try:
            data = json.loads(self.agents_file.read_text())
            agents = {}
            
            for agent_id, agent_data in data.items():
                # Convert GitHub context
                github_context = None
                if agent_data.get("github_context"):
                    gc_data = agent_data["github_context"]
                    github_context = GitHubContext(
                        repo_name=gc_data["repo_name"],
                        repo_owner=gc_data["repo_owner"],
                        current_branch=gc_data["current_branch"],
                        default_branch=gc_data["default_branch"],
                        milestone=gc_data.get("milestone"),
                        assigned_issues=gc_data.get("assigned_issues", []),
                        open_prs=gc_data.get("open_prs", []),
                        last_commit=gc_data.get("last_commit", ""),
                        has_protection=gc_data.get("has_protection", False),
                        has_issues=gc_data.get("has_issues", True),
                        has_projects=gc_data.get("has_projects", True)
                    )
                
                # Convert agent
                agent = Agent(
                    id=agent_data["id"],
                    role=AgentRole(agent_data["role"]),
                    status=AgentStatus(agent_data["status"]),
                    current_task=agent_data.get("current_task"),
                    github_context=github_context,
                    work_directory=Path(agent_data["work_directory"]),
                    workspace_dir=Path(agent_data["workspace_dir"]) if agent_data.get("workspace_dir") else None,
                    last_checkin=datetime.fromisoformat(agent_data["last_checkin"]),
                    created_at=datetime.fromisoformat(agent_data["created_at"]),
                    claude_code_session=agent_data.get("claude_code_session"),
                    assigned_issues=agent_data.get("assigned_issues", []),
                    completed_tasks=agent_data.get("completed_tasks", []),
                    blockers=agent_data.get("blockers", []),
                    metrics=agent_data.get("metrics", {})
                )
                
                agents[agent_id] = agent
            
            return agents
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error loading agents: {e}")
            return {}
    
    def _save_agents(self):
        """Save agents to state file"""
        
        try:
            data = {}
            for agent_id, agent in self.agents.items():
                github_context_data = None
                if agent.github_context:
                    github_context_data = asdict(agent.github_context)
                
                data[agent_id] = {
                    "id": agent.id,
                    "role": agent.role.value,
                    "status": agent.status.value,
                    "current_task": agent.current_task,
                    "github_context": github_context_data,
                    "work_directory": str(agent.work_directory),
                    "workspace_dir": str(agent.workspace_dir) if agent.workspace_dir else None,
                    "last_checkin": agent.last_checkin.isoformat(),
                    "created_at": agent.created_at.isoformat(),
                    "claude_code_session": agent.claude_code_session,
                    "assigned_issues": agent.assigned_issues,
                    "completed_tasks": agent.completed_tasks,
                    "blockers": agent.blockers,
                    "metrics": agent.metrics
                }
            
            self.agents_file.write_text(json.dumps(data, indent=2))
            
        except Exception as e:
            logger.error(f"Error saving agents: {e}")
    
    def _save_scheduled_tasks(self):
        """Save scheduled tasks to state file"""
        
        try:
            tasks_file = self.state_dir / "scheduled_tasks.json"
            data = []
            
            for task in self.scheduled_tasks:
                data.append({
                    "id": task.id,
                    "run_time": task.run_time.isoformat(),
                    "note": task.note,
                    "agent_id": task.agent_id,
                    "task_type": task.task_type,
                    "recurring": task.recurring,
                    "interval_minutes": task.interval_minutes
                })
            
            tasks_file.write_text(json.dumps(data, indent=2))
            
        except Exception as e:
            logger.error(f"Error saving scheduled tasks: {e}")
    
    def _save_quality_metrics(self):
        """Save quality metrics to state file"""
        
        try:
            data = {}
            for project_name, project in self.projects.items():
                data[project_name] = project.quality_metrics
            
            self.quality_metrics_file.write_text(json.dumps(data, indent=2))
            
        except Exception as e:
            logger.error(f"Error saving quality metrics: {e}")
    
    def get_project_status(self, project_name: str) -> Dict[str, Any]:
        """Get comprehensive project status"""
        
        if project_name not in self.projects:
            return {"error": f"Project {project_name} not found"}
        
        project = self.projects[project_name]
        
        status = {
            "project": {
                "name": project.name,
                "complexity": project.complexity.value,
                "created_at": project.created_at.isoformat(),
                "github_repo": project.github_repo,
                "current_milestone": project.current_milestone
            },
            "agents": {},
            "github": {},
            "quality": project.quality_metrics,
            "summary": {
                "total_agents": len(project.agents),
                "active_agents": 0,
                "blocked_agents": 0,
                "completed_tasks": 0
            }
        }
        
        # Agent status
        for agent_id, agent in project.agents.items():
            agent_status = {
                "role": agent.role.value,
                "status": agent.status.value,
                "current_task": agent.current_task,
                "last_checkin": agent.last_checkin.isoformat(),
                "assigned_issues": len(agent.assigned_issues),
                "blockers": len(agent.blockers),
                "metrics": agent.metrics
            }
            
            status["agents"][agent_id] = agent_status
            
            if agent.status == AgentStatus.WORKING:
                status["summary"]["active_agents"] += 1
            elif agent.status == AgentStatus.BLOCKED:
                status["summary"]["blocked_agents"] += 1
            
            status["summary"]["completed_tasks"] += len(agent.completed_tasks)
        
        # GitHub status
        if project.github_repo and self.github_available:
            status["github"] = self._check_github_status(project.path)
        
        return status
    
    def shutdown(self):
        """Shutdown orchestrator and cleanup"""
        
        logger.info("Shutting down CodeCrew Orchestrator")
        
        # Stop scheduler
        self.scheduler_running = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        # Stop quality monitoring
        self.quality_monitoring_active = False
        if self.quality_monitor_thread and self.quality_monitor_thread.is_alive():
            self.quality_monitor_thread.join(timeout=5)
        
        # Save final state
        self._save_projects()
        self._save_agents()
        self._save_scheduled_tasks()
        self._save_quality_metrics()
        
        logger.info("CodeCrew Orchestrator shutdown complete")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
