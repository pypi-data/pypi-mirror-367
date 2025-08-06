#!/usr/bin/env python3
"""
CodeCrew Main Orchestrator
Complete multi-agent development system orchestrator
"""

import os
import sys
import json
import queue
import logging
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

# Configure logging with proper directory creation
def setup_logging():
    """Set up logging with automatic directory creation"""
    log_dir = Path.home() / ".codecrew" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "codecrew.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

# Set up logging immediately
setup_logging()
logger = logging.getLogger(__name__)

class AgentRole(Enum):
    """Agent role definitions"""
    ORCHESTRATOR = "orchestrator"
    PROJECT_MANAGER = "project_manager"
    LEAD_DEVELOPER = "lead_developer"
    DEVELOPER = "developer"
    QA_ENGINEER = "qa_engineer"
    DEVOPS = "devops"
    CODE_REVIEWER = "code_reviewer"
    DOCUMENTATION_WRITER = "documentation_writer"

class AgentStatus(Enum):
    """Agent status definitions"""
    IDLE = "idle"
    WORKING = "working"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class Agent:
    """Agent data structure"""
    id: str
    role: AgentRole
    status: AgentStatus
    task: str
    workspace_dir: Path
    work_directory: Path
    github_context: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    last_checkin: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_checkin is None:
            self.last_checkin = datetime.now()

@dataclass
class Project:
    """Project data structure"""
    name: str
    path: Path
    spec_file: str
    brd_file: str
    prd_file: str
    userstories_file: str
    checklist_file: str
    complexity: str
    created_at: datetime
    github_repo: Optional[str] = None
    current_milestone: Optional[str] = None
    quality_metrics: Dict[str, float] = None

    def __post_init__(self):
        if self.quality_metrics is None:
            self.quality_metrics = {
                "test_coverage": 0.0,
                "code_complexity": 0.0,
                "security_issues": 0,
                "technical_debt_ratio": 0.0,
            }

class CodeCrewOrchestrator:
    """Main orchestrator for CodeCrew multi-agent system"""
    
    def __init__(self, root_path: Path = None):
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.state_dir = Path.home() / ".codecrew"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # State files
        self.projects_file = self.state_dir / "projects.json"
        self.agents_file = self.state_dir / "agents.json"
        self.config_file = self.state_dir / "config.json"
        
        # Load existing state
        self.config = self._load_config()
        self.projects: Dict[str, Project] = self._load_projects()
        self.agents: Dict[str, Agent] = self._load_agents()
        self.message_queue = queue.Queue()
        
        # GitHub integration
        self.github_available = self._check_github_cli()
        if not self.github_available:
            logger.warning("GitHub CLI not available. Some features will be limited.")
    
    def init_project(self, project_name: str, spec_file: str, brd_file: str, 
                    prd_file: str, userstories_file: str, checklist_file: str,
                    project_path: Path = None) -> Project:
        """Initialize a new CodeCrew project"""
        
        if project_path is None:
            project_path = self.root_path / project_name
        else:
            project_path = Path(project_path)
        
        logger.info(f"Initializing CodeCrew project: {project_name}")
        
        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)
        
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
        
        # Set up project templates and structure
        from .templates import CodeCrewTemplates
        templates = CodeCrewTemplates(project_path)
        templates.setup_all_templates("python_api")
        
        # Save project state
        self.projects[project_name] = project
        self._save_projects()
        
        logger.info(f"Project {project_name} initialized successfully")
        return project
    
    def deploy_agents(self, project_name: str) -> List[Agent]:
        """Deploy development team for project"""
        
        if project_name not in self.projects:
            raise ValueError(f"Project {project_name} not found")
        
        project = self.projects[project_name]
        logger.info(f"Deploying agents for project: {project_name}")
        
        # Determine agent team based on project complexity
        agent_roles = self._determine_agent_team(project.complexity)
        
        deployed_agents = []
        for role in agent_roles:
            agent = self._create_agent(project, role, f"Working on {project_name}")
            deployed_agents.append(agent)
        
        logger.info(f"Deployed {len(deployed_agents)} agents for {project_name}")
        return deployed_agents

    async def start_development(self, project_name: str) -> bool:
        """Start development work for a project"""

        if project_name not in self.projects:
            raise ValueError(f"Project {project_name} not found")

        project = self.projects[project_name]

        # Get agents for this project
        project_agents = [a for a in self.agents.values()
                         if a.id.startswith(f"{project_name}_")]

        if not project_agents:
            raise ValueError(f"No agents deployed for project {project_name}")

        logger.info(f"Starting development for project {project_name} with {len(project_agents)} agents")

        # Import here to avoid circular imports
        from .orchestrator import DevelopmentOrchestrator

        # Create orchestrator and start development
        orchestrator = DevelopmentOrchestrator(project, project_agents)
        success = await orchestrator.start_development()

        if success:
            logger.info(f"Development completed successfully for {project_name}")
        else:
            logger.error(f"Development failed for {project_name}")

        return success

    def get_development_status(self, project_name: str) -> Dict[str, Any]:
        """Get development status for a project"""

        if project_name not in self.projects:
            return {"error": f"Project {project_name} not found"}

        project = self.projects[project_name]
        project_agents = [a for a in self.agents.values()
                         if a.id.startswith(f"{project_name}_")]

        if not project_agents:
            return {"error": f"No agents deployed for project {project_name}"}

        # Check if there's an active development session
        session_file = project.path / ".codecrew" / "session.json"
        if session_file.exists():
            try:
                from .orchestrator import DevelopmentOrchestrator
                orchestrator = DevelopmentOrchestrator(project, project_agents)
                return orchestrator.get_development_status()
            except Exception as e:
                logger.warning(f"Could not get development status: {e}")

        return {
            "status": "ready",
            "message": "Agents deployed and ready to start development"
        }
    
    def get_project_status(self, project_name: str = None) -> Dict[str, Any]:
        """Get comprehensive project status"""
        
        if project_name:
            if project_name not in self.projects:
                return {"error": f"Project {project_name} not found"}
            
            project = self.projects[project_name]
            project_agents = [a for a in self.agents.values()
                            if a.id.startswith(f"{project_name}_")]
            
            return {
                "project": asdict(project),
                "agents": [asdict(a) for a in project_agents],
                "github_status": self._get_github_status(project.path) if self.github_available else None
            }
        else:
            return {
                "projects": {name: asdict(proj) for name, proj in self.projects.items()},
                "total_agents": len(self.agents),
                "github_available": self.github_available
            }
    
    def _analyze_project_complexity(self, project_path: Path) -> str:
        """Analyze project complexity"""
        # Simple heuristic - can be enhanced
        if not project_path.exists():
            return "nascent"
        
        file_count = len(list(project_path.rglob("*.py")))
        if file_count == 0:
            return "nascent"
        elif file_count < 10:
            return "simple"
        elif file_count < 50:
            return "moderate"
        else:
            return "complex"
    
    def _determine_agent_team(self, complexity: str) -> List[AgentRole]:
        """Determine required agent team based on complexity"""
        base_team = [AgentRole.PROJECT_MANAGER, AgentRole.DEVELOPER]
        
        if complexity in ["moderate", "complex"]:
            base_team.extend([AgentRole.QA_ENGINEER, AgentRole.CODE_REVIEWER])
        
        if complexity == "complex":
            base_team.extend([AgentRole.LEAD_DEVELOPER, AgentRole.DEVOPS])
        
        return base_team
    
    def _create_agent(self, project: Project, role: AgentRole, task: str) -> Agent:
        """Create and configure an agent"""
        agent_id = f"{project.name}_{role.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        workspace_dir = project.path / ".codecrew" / "agents" / agent_id
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        agent = Agent(
            id=agent_id,
            role=role,
            status=AgentStatus.IDLE,
            task=task,
            workspace_dir=workspace_dir,
            work_directory=project.path
        )
        
        # Save agent
        self.agents[agent_id] = agent
        self._save_agents()
        
        logger.info(f"Created agent: {agent_id} ({role.value})")
        return agent
    
    def _ensure_git_repo(self, project_path: Path):
        """Ensure Git repository exists"""
        git_dir = project_path / ".git"
        if not git_dir.exists():
            try:
                subprocess.run(["git", "init"], cwd=project_path, check=True, capture_output=True)
                logger.info(f"Initialized Git repository in {project_path}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to initialize Git repository: {e}")
    
    def _check_github_cli(self) -> bool:
        """Check if GitHub CLI is available"""
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _get_github_status(self, project_path: Path) -> Dict[str, Any]:
        """Get GitHub repository status"""
        try:
            # Get repository info
            result = subprocess.run(
                ["gh", "repo", "view", "--json", "name,owner,url"],
                cwd=project_path, capture_output=True, text=True, check=True
            )
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return {"error": "Unable to get GitHub status"}
    
    def _load_config(self) -> Dict[str, Any]:
        """Load orchestrator configuration"""
        default_config = {
            "version": "1.0.0",
            "project_templates": ["python_api", "ml_project", "web_app"],
            "quality_thresholds": {
                "test_coverage_minimum": 80.0,
                "code_complexity_maximum": 10,
                "security_issues_maximum": 0
            }
        }
        
        if not self.config_file.exists():
            self.config_file.write_text(json.dumps(default_config, indent=2))
            return default_config
        
        try:
            return json.loads(self.config_file.read_text())
        except json.JSONDecodeError:
            logger.warning("Invalid config file, using defaults")
            return default_config
    
    def _load_projects(self) -> Dict[str, Project]:
        """Load projects from state file"""
        if not self.projects_file.exists():
            return {}
        
        try:
            data = json.loads(self.projects_file.read_text())
            projects = {}
            for name, proj_data in data.items():
                proj_data['path'] = Path(proj_data['path'])
                proj_data['created_at'] = datetime.fromisoformat(proj_data['created_at'])
                projects[name] = Project(**proj_data)
            return projects
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Error loading projects: {e}")
            return {}
    
    def _load_agents(self) -> Dict[str, Agent]:
        """Load agents from state file"""
        if not self.agents_file.exists():
            return {}
        
        try:
            data = json.loads(self.agents_file.read_text())
            agents = {}
            for agent_id, agent_data in data.items():
                agent_data['role'] = AgentRole(agent_data['role'])
                agent_data['status'] = AgentStatus(agent_data['status'])
                agent_data['workspace_dir'] = Path(agent_data['workspace_dir'])
                agent_data['work_directory'] = Path(agent_data['work_directory'])
                agent_data['created_at'] = datetime.fromisoformat(agent_data['created_at'])
                agent_data['last_checkin'] = datetime.fromisoformat(agent_data['last_checkin'])
                agents[agent_id] = Agent(**agent_data)
            return agents
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            logger.warning(f"Error loading agents: {e}")
            return {}
    
    def _save_projects(self):
        """Save projects to state file"""
        data = {}
        for name, project in self.projects.items():
            proj_dict = asdict(project)
            proj_dict['path'] = str(proj_dict['path'])
            proj_dict['created_at'] = proj_dict['created_at'].isoformat()
            data[name] = proj_dict
        
        self.projects_file.write_text(json.dumps(data, indent=2))
    
    def _save_agents(self):
        """Save agents to state file"""
        data = {}
        for agent_id, agent in self.agents.items():
            agent_dict = asdict(agent)
            agent_dict['role'] = agent_dict['role'].value
            agent_dict['status'] = agent_dict['status'].value
            agent_dict['workspace_dir'] = str(agent_dict['workspace_dir'])
            agent_dict['work_directory'] = str(agent_dict['work_directory'])
            agent_dict['created_at'] = agent_dict['created_at'].isoformat()
            agent_dict['last_checkin'] = agent_dict['last_checkin'].isoformat()
            data[agent_id] = agent_dict
        
        self.agents_file.write_text(json.dumps(data, indent=2))
