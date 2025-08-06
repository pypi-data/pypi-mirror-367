#!/usr/bin/env python3
"""
CodeCrew Agent Execution Engine
Handles the actual execution of development tasks by AI agents
"""

import os
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from .main import Agent, AgentRole, AgentStatus, Project

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Task:
    """Individual development task"""
    id: str
    title: str
    description: str
    agent_role: AgentRole
    status: TaskStatus
    priority: TaskPriority
    dependencies: List[str]  # Task IDs this task depends on
    estimated_hours: float
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_agent_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class WorkSession:
    """Agent work session tracking"""
    agent_id: str
    task_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    claude_interactions: List[Dict[str, Any]] = None
    files_modified: List[str] = None
    commands_executed: List[str] = None
    
    def __post_init__(self):
        if self.claude_interactions is None:
            self.claude_interactions = []
        if self.files_modified is None:
            self.files_modified = []
        if self.commands_executed is None:
            self.commands_executed = []

class ClaudeCodeInterface:
    """Interface for interacting with Claude Code CLI"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.claude_available = self._check_claude_cli()
        
    def _check_claude_cli(self) -> bool:
        """Check if Claude CLI is available"""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    async def execute_task(self, task: Task, agent: Agent, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a development task using Claude CLI"""
        if not self.claude_available:
            raise RuntimeError("Claude CLI not available")
        
        # Prepare context for Claude
        claude_context = self._prepare_claude_context(task, agent, context)
        
        # Execute via Claude Code CLI
        result = await self._call_claude_code(claude_context)
        
        return result
    
    def _prepare_claude_context(self, task: Task, agent: Agent, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context information for Claude Code CLI"""
        return {
            "task": asdict(task),
            "agent": {
                "id": agent.id,
                "role": agent.role.value,
                "workspace": str(agent.workspace_dir),
                "work_directory": str(agent.work_directory)
            },
            "project": context.get("project", {}),
            "requirements": context.get("requirements", {}),
            "codebase_state": context.get("codebase_state", {})
        }
    
    async def _call_claude_code(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make actual call to Claude Code CLI"""
        try:
            # Create a prompt for Claude based on the task context
            prompt = self._create_claude_prompt(context)

            # Prepare Claude CLI command
            cmd = [
                "claude",
                "--print",
                "--output-format", "text",
                "--add-dir", str(self.project_path),
                prompt
            ]

            # Execute Claude CLI
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_path
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                # Parse Claude's response
                claude_output = stdout.decode()

                # Try to extract JSON from Claude's response if it contains structured data
                try:
                    # Look for JSON blocks in the response
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', claude_output, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group(1))
                        return {
                            "success": True,
                            "files_created": result.get("files_created", []),
                            "files_modified": result.get("files_modified", []),
                            "commands_executed": result.get("commands_executed", []),
                            "output": claude_output,
                            "next_steps": result.get("next_steps", [])
                        }
                except (json.JSONDecodeError, AttributeError):
                    pass

                # Fallback - return the raw output
                return {
                    "success": True,
                    "files_created": [],
                    "files_modified": [],
                    "commands_executed": [],
                    "output": claude_output,
                    "next_steps": []
                }
            else:
                error_msg = stderr.decode() if stderr else "Claude CLI failed"
                logger.error(f"Claude CLI error: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "files_created": [],
                    "files_modified": [],
                    "commands_executed": [],
                    "output": "",
                    "next_steps": []
                }

        except Exception as e:
            logger.error(f"Error calling Claude CLI: {e}")
            return {
                "success": False,
                "error": str(e),
                "files_created": [],
                "files_modified": [],
                "commands_executed": [],
                "output": "",
                "next_steps": []
            }

    def _create_claude_prompt(self, context: Dict[str, Any]) -> str:
        """Create a detailed prompt for Claude based on the task context"""
        task = context["task"]
        agent = context["agent"]
        project = context.get("project", {})
        requirements = context.get("requirements", {})

        prompt = f"""# CodeCrew Development Task

## Agent Information
- **Role**: {agent["role"]}
- **Agent ID**: {agent["id"]}
- **Workspace**: {agent["workspace"]}
- **Work Directory**: {agent["work_directory"]}

## Task Details
- **Title**: {task["title"]}
- **Description**: {task["description"]}
- **Priority**: {task["priority"]}
- **Estimated Hours**: {task["estimated_hours"]}

## Project Context
- **Project Name**: {project.get("name", "Unknown")}
- **Project Path**: {project.get("path", "Unknown")}
- **Complexity**: {project.get("complexity", "Unknown")}

## Requirements
"""

        # Add requirements sections
        for req_type, content in requirements.items():
            if content and content.strip():
                prompt += f"\n### {req_type.upper()}\n{content}\n"

        prompt += f"""

## Instructions
As a {agent["role"]} agent, please complete the following task: "{task["title"]}"

{task["description"]}

Please:
1. Analyze the requirements and task description
2. Create or modify the necessary files
3. Follow best practices for {agent["role"]} work
4. Ensure code quality and documentation
5. Provide a summary of what was accomplished

## Output Format
Please provide your response in JSON format with the following structure:
```json
{{
    "files_created": ["list of files created"],
    "files_modified": ["list of files modified"],
    "commands_executed": ["list of commands run"],
    "output": "Summary of work completed",
    "next_steps": ["suggested next steps"]
}}
```

Begin your development work now.
"""

        return prompt

class TaskManager:
    """Manages task creation, assignment, and execution"""
    
    def __init__(self, project: Project):
        self.project = project
        self.tasks: Dict[str, Task] = {}
        self.task_dependencies: Dict[str, List[str]] = {}
        self.tasks_file = project.path / ".codecrew" / "tasks.json"
        self._load_tasks()
    
    def create_tasks_from_requirements(self, requirements: Dict[str, Any]) -> List[Task]:
        """Create development tasks from project requirements"""
        tasks = []

        # Analyze requirements to create intelligent task breakdown
        task_templates = self._analyze_requirements_for_tasks(requirements)

        for i, task_data in enumerate(task_templates):
            task = Task(
                id=f"task_{i+1:03d}",
                title=task_data["title"],
                description=task_data["description"],
                agent_role=task_data["agent_role"],
                status=TaskStatus.PENDING,
                priority=task_data["priority"],
                dependencies=task_data.get("dependencies", []),
                estimated_hours=task_data["estimated_hours"],
                created_at=datetime.now()
            )
            tasks.append(task)
            self.tasks[task.id] = task

        self._save_tasks()
        return tasks

    def _analyze_requirements_for_tasks(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze requirements and create intelligent task breakdown"""

        # Start with foundational tasks
        base_tasks = [
            {
                "title": "Project Planning and Architecture",
                "description": "Analyze requirements and create project architecture plan",
                "agent_role": AgentRole.PROJECT_MANAGER,
                "priority": TaskPriority.CRITICAL,
                "estimated_hours": 2.0
            },
            {
                "title": "Set up project structure",
                "description": "Create basic project structure, configuration files, and development environment",
                "agent_role": AgentRole.DEVELOPER,
                "priority": TaskPriority.HIGH,
                "estimated_hours": 2.0,
                "dependencies": ["task_001"]
            }
        ]

        # Analyze requirements content to add specific tasks
        spec_content = requirements.get("spec", "").lower()
        prd_content = requirements.get("prd", "").lower()
        userstories_content = requirements.get("userstories", "").lower()

        # Add API-related tasks if mentioned
        if any(keyword in spec_content + prd_content for keyword in ["api", "rest", "endpoint", "fastapi"]):
            base_tasks.extend([
                {
                    "title": "Implement API endpoints",
                    "description": "Create REST API endpoints based on specifications",
                    "agent_role": AgentRole.DEVELOPER,
                    "priority": TaskPriority.HIGH,
                    "estimated_hours": 6.0,
                    "dependencies": ["task_002"]
                },
                {
                    "title": "API documentation",
                    "description": "Create comprehensive API documentation",
                    "agent_role": AgentRole.DOCUMENTATION_WRITER,
                    "priority": TaskPriority.MEDIUM,
                    "estimated_hours": 3.0,
                    "dependencies": ["task_003"]
                }
            ])

        # Add database tasks if mentioned
        if any(keyword in spec_content + prd_content for keyword in ["database", "db", "sql", "postgres", "mysql"]):
            base_tasks.append({
                "title": "Database setup and models",
                "description": "Set up database schema and implement data models",
                "agent_role": AgentRole.DEVELOPER,
                "priority": TaskPriority.HIGH,
                "estimated_hours": 4.0,
                "dependencies": ["task_002"]
            })

        # Add authentication tasks if mentioned
        if any(keyword in spec_content + prd_content for keyword in ["auth", "login", "user", "security"]):
            base_tasks.append({
                "title": "User authentication system",
                "description": "Implement user authentication and authorization",
                "agent_role": AgentRole.DEVELOPER,
                "priority": TaskPriority.HIGH,
                "estimated_hours": 5.0,
                "dependencies": ["task_002"]
            })

        # Add testing tasks
        base_tasks.extend([
            {
                "title": "Unit tests",
                "description": "Create comprehensive unit test suite",
                "agent_role": AgentRole.QA_ENGINEER,
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 4.0,
                "dependencies": ["task_002"]
            },
            {
                "title": "Integration tests",
                "description": "Create integration tests for API endpoints",
                "agent_role": AgentRole.QA_ENGINEER,
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 3.0,
                "dependencies": ["task_002"]
            }
        ])

        # Add deployment tasks
        base_tasks.extend([
            {
                "title": "Deployment configuration",
                "description": "Set up deployment scripts and CI/CD pipeline",
                "agent_role": AgentRole.DEVOPS,
                "priority": TaskPriority.LOW,
                "estimated_hours": 3.0,
                "dependencies": ["task_002"]
            },
            {
                "title": "Code review and quality check",
                "description": "Review code quality, security, and best practices",
                "agent_role": AgentRole.CODE_REVIEWER,
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 2.0,
                "dependencies": ["task_002"]
            }
        ])

        return base_tasks
    
    def get_next_task_for_agent(self, agent: Agent) -> Optional[Task]:
        """Get the next available task for an agent"""
        # Handle both enum and string comparisons
        agent_role_value = agent.role.value if hasattr(agent.role, 'value') else str(agent.role)

        logger.debug(f"Looking for tasks for agent {agent.id} with role {agent_role_value}")
        logger.debug(f"Available tasks: {list(self.tasks.keys())}")

        available_tasks = []
        for task in self.tasks.values():
            logger.debug(f"Checking task {task.id}: status={task.status}, role={task.agent_role}, deps_met={self._are_dependencies_met(task)}")

            role_match = (task.agent_role == agent.role or
                         (hasattr(task.agent_role, 'value') and task.agent_role.value == agent_role_value) or
                         str(task.agent_role) == agent_role_value)

            if (task.status == TaskStatus.PENDING and role_match and self._are_dependencies_met(task)):
                available_tasks.append(task)
                logger.debug(f"Task {task.id} is available for agent {agent.id}")

        logger.debug(f"Found {len(available_tasks)} available tasks for agent {agent.id}")
        
        if not available_tasks:
            return None
        
        # Sort by priority and return highest priority task
        available_tasks.sort(key=lambda t: (t.priority.value, t.created_at))
        return available_tasks[0]
    
    def _are_dependencies_met(self, task: Task) -> bool:
        """Check if all task dependencies are completed"""
        for dep_id in task.dependencies:
            if dep_id in self.tasks:
                if self.tasks[dep_id].status != TaskStatus.COMPLETED:
                    return False
        return True
    
    def assign_task(self, task: Task, agent: Agent) -> bool:
        """Assign a task to an agent"""
        if task.status != TaskStatus.PENDING:
            return False
        
        task.assigned_agent_id = agent.id
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        self._save_tasks()
        return True
    
    def complete_task(self, task: Task, result: Dict[str, Any]) -> bool:
        """Mark a task as completed"""
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.result = result
        
        self._save_tasks()
        return True
    
    def fail_task(self, task: Task, error_message: str) -> bool:
        """Mark a task as failed"""
        task.status = TaskStatus.FAILED
        task.error_message = error_message
        
        self._save_tasks()
        return True
    
    def _load_tasks(self):
        """Load tasks from file"""
        if not self.tasks_file.exists():
            return
        
        try:
            with open(self.tasks_file, 'r') as f:
                data = json.load(f)
                for task_id, task_data in data.items():
                    task_data['agent_role'] = AgentRole(task_data['agent_role'])
                    task_data['status'] = TaskStatus(task_data['status'])
                    task_data['priority'] = TaskPriority(task_data['priority'])
                    task_data['created_at'] = datetime.fromisoformat(task_data['created_at'])
                    
                    if task_data.get('started_at'):
                        task_data['started_at'] = datetime.fromisoformat(task_data['started_at'])
                    if task_data.get('completed_at'):
                        task_data['completed_at'] = datetime.fromisoformat(task_data['completed_at'])
                    
                    self.tasks[task_id] = Task(**task_data)
        except Exception as e:
            logger.warning(f"Error loading tasks: {e}")
    
    def _save_tasks(self):
        """Save tasks to file"""
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {}
        for task_id, task in self.tasks.items():
            task_dict = asdict(task)
            task_dict['agent_role'] = task_dict['agent_role'].value
            task_dict['status'] = task_dict['status'].value
            task_dict['priority'] = task_dict['priority'].value
            task_dict['created_at'] = task_dict['created_at'].isoformat()
            
            if task_dict.get('started_at'):
                task_dict['started_at'] = task_dict['started_at'].isoformat()
            if task_dict.get('completed_at'):
                task_dict['completed_at'] = task_dict['completed_at'].isoformat()
            
            data[task_id] = task_dict
        
        with open(self.tasks_file, 'w') as f:
            json.dump(data, f, indent=2)

class AgentExecutor:
    """Executes individual agent work sessions"""

    def __init__(self, agent: Agent, project: Project, task_manager: TaskManager = None):
        self.agent = agent
        self.project = project
        self.claude_interface = ClaudeCodeInterface(project.path)
        self.task_manager = task_manager or TaskManager(project)
        self.current_session: Optional[WorkSession] = None
    
    async def start_work_session(self) -> bool:
        """Start a work session for the agent"""
        if self.current_session is not None:
            logger.warning(f"Agent {self.agent.id} already has active session")
            return False
        
        # Get next task for this agent
        next_task = self.task_manager.get_next_task_for_agent(self.agent)
        if not next_task:
            logger.info(f"No tasks available for agent {self.agent.id}")
            return False
        
        # Assign task to agent
        if not self.task_manager.assign_task(next_task, self.agent):
            logger.error(f"Failed to assign task {next_task.id} to agent {self.agent.id}")
            return False
        
        # Start work session
        self.current_session = WorkSession(
            agent_id=self.agent.id,
            task_id=next_task.id,
            started_at=datetime.now()
        )
        
        # Update agent status
        self.agent.status = AgentStatus.WORKING
        self.agent.task = next_task.title
        self.agent.last_checkin = datetime.now()
        
        logger.info(f"Started work session for agent {self.agent.id} on task {next_task.id}")
        return True
    
    async def execute_current_task(self) -> bool:
        """Execute the current task"""
        if not self.current_session:
            return False
        
        task = self.task_manager.tasks.get(self.current_session.task_id)
        if not task:
            return False
        
        try:
            # Prepare context for task execution
            context = self._prepare_execution_context(task)
            
            # Execute task via Claude Code CLI
            result = await self.claude_interface.execute_task(task, self.agent, context)
            
            # Update session with results
            self.current_session.claude_interactions.append(result)
            self.current_session.files_modified.extend(result.get('files_modified', []))
            self.current_session.commands_executed.extend(result.get('commands_executed', []))
            
            # Complete the task
            self.task_manager.complete_task(task, result)
            
            # End work session
            self.current_session.ended_at = datetime.now()
            self.current_session = None
            
            # Update agent status
            self.agent.status = AgentStatus.IDLE
            self.agent.last_checkin = datetime.now()
            
            logger.info(f"Completed task {task.id} for agent {self.agent.id}")
            return True
            
        except Exception as e:
            logger.error(f"Task execution failed for agent {self.agent.id}: {e}")
            
            # Fail the task
            self.task_manager.fail_task(task, str(e))
            
            # End work session
            if self.current_session:
                self.current_session.ended_at = datetime.now()
                self.current_session = None
            
            # Update agent status
            self.agent.status = AgentStatus.ERROR
            self.agent.last_checkin = datetime.now()
            
            return False
    
    def _prepare_execution_context(self, task: Task) -> Dict[str, Any]:
        """Prepare context for task execution"""
        # Read project requirements
        requirements = self._read_project_requirements()
        
        # Get current codebase state
        codebase_state = self._analyze_codebase_state()
        
        return {
            "project": asdict(self.project),
            "requirements": requirements,
            "codebase_state": codebase_state,
            "agent_briefing": self._get_agent_briefing()
        }
    
    def _read_project_requirements(self) -> Dict[str, Any]:
        """Read and parse project requirement documents"""
        requirements = {}
        
        req_files = {
            "spec": self.project.spec_file,
            "brd": self.project.brd_file,
            "prd": self.project.prd_file,
            "userstories": self.project.userstories_file,
            "checklist": self.project.checklist_file
        }
        
        for req_type, filename in req_files.items():
            file_path = self.project.path / filename
            if file_path.exists():
                try:
                    requirements[req_type] = file_path.read_text()
                except Exception as e:
                    logger.warning(f"Could not read {filename}: {e}")
                    requirements[req_type] = ""
            else:
                requirements[req_type] = ""
        
        return requirements
    
    def _analyze_codebase_state(self) -> Dict[str, Any]:
        """Analyze current state of the codebase"""
        # This would analyze the current codebase structure, files, etc.
        return {
            "files_count": len(list(self.project.path.rglob("*.py"))),
            "last_modified": datetime.now().isoformat(),
            "git_status": "clean"  # Would check actual git status
        }
    
    def _get_agent_briefing(self) -> str:
        """Get the briefing for this agent's role"""
        from .templates import CodeCrewTemplates
        templates = CodeCrewTemplates(self.project.path)
        return templates.get_agent_briefing(self.agent.role.value)
