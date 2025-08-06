#!/usr/bin/env python3
"""
CodeCrew Development Orchestrator
Coordinates multiple agents working on a project
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .main import Agent, AgentRole, AgentStatus, Project
from .execution import AgentExecutor, TaskManager, Task, TaskStatus

logger = logging.getLogger(__name__)

class ProjectPhase(Enum):
    """Development project phases"""
    PLANNING = "planning"
    DEVELOPMENT = "development"
    TESTING = "testing"
    REVIEW = "review"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"

@dataclass
class DevelopmentSession:
    """Represents an active development session"""
    project_name: str
    started_at: datetime
    current_phase: ProjectPhase
    active_agents: Set[str]
    completed_tasks: int
    total_tasks: int
    estimated_completion: Optional[datetime] = None
    
class DevelopmentOrchestrator:
    """Orchestrates multi-agent development workflow"""
    
    def __init__(self, project: Project, agents: List[Agent]):
        self.project = project
        self.agents = {agent.id: agent for agent in agents}
        self.task_manager = TaskManager(project)
        self.agent_executors = {
            agent.id: AgentExecutor(agent, project, self.task_manager)
            for agent in agents
        }
        self.current_session: Optional[DevelopmentSession] = None
        self.session_file = project.path / ".codecrew" / "session.json"
        
    async def start_development(self) -> bool:
        """Start the development process"""
        logger.info(f"Starting development for project {self.project.name}")
        
        # Initialize tasks from project requirements
        await self._initialize_development_tasks()
        
        # Start development session
        self.current_session = DevelopmentSession(
            project_name=self.project.name,
            started_at=datetime.now(),
            current_phase=ProjectPhase.PLANNING,
            active_agents=set(),
            completed_tasks=0,
            total_tasks=len(self.task_manager.tasks)
        )
        
        # Start the orchestration loop
        success = await self._orchestration_loop()
        
        if success:
            logger.info(f"Development completed for project {self.project.name}")
        else:
            logger.error(f"Development failed for project {self.project.name}")
        
        return success
    
    async def _initialize_development_tasks(self):
        """Initialize development tasks from project requirements"""
        logger.info("Analyzing project requirements and creating tasks...")
        
        # Read project requirements
        requirements = self._read_project_requirements()
        
        # Create tasks based on requirements
        tasks = self.task_manager.create_tasks_from_requirements(requirements)
        
        logger.info(f"Created {len(tasks)} development tasks")
        
        # Log task summary
        for task in tasks:
            logger.info(f"  - {task.title} ({task.agent_role.value}, {task.priority.value})")
    
    async def _orchestration_loop(self) -> bool:
        """Main orchestration loop"""
        max_iterations = 100  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Check if all tasks are completed
            if self._all_tasks_completed():
                logger.info("All tasks completed successfully!")
                return True
            
            # Update project phase based on progress
            self._update_project_phase()
            
            # Assign work to available agents
            assignments_made = await self._assign_work_to_agents()
            
            # Execute work for active agents
            await self._execute_agent_work()
            
            # Check for blocked or failed agents
            await self._handle_agent_issues()
            
            # If no assignments were made and no agents are working, we might be stuck
            if not assignments_made and not self._any_agents_working():
                logger.warning("No progress possible - checking for blockers")
                if not await self._resolve_blockers():
                    logger.error("Unable to resolve blockers - development stalled")
                    return False
            
            # Brief pause between iterations
            await asyncio.sleep(1)
        
        logger.error("Maximum iterations reached - development may be stuck")
        return False
    
    def _all_tasks_completed(self) -> bool:
        """Check if all tasks are completed"""
        return all(
            task.status == TaskStatus.COMPLETED 
            for task in self.task_manager.tasks.values()
        )
    
    def _update_project_phase(self):
        """Update the current project phase based on task progress"""
        if not self.current_session:
            return
        
        completed_tasks = sum(
            1 for task in self.task_manager.tasks.values()
            if task.status == TaskStatus.COMPLETED
        )
        
        total_tasks = len(self.task_manager.tasks)
        progress = completed_tasks / total_tasks if total_tasks > 0 else 0
        
        # Update session stats
        self.current_session.completed_tasks = completed_tasks
        self.current_session.total_tasks = total_tasks
        
        # Determine phase based on progress and task types
        if progress < 0.3:
            self.current_session.current_phase = ProjectPhase.DEVELOPMENT
        elif progress < 0.7:
            self.current_session.current_phase = ProjectPhase.TESTING
        elif progress < 0.9:
            self.current_session.current_phase = ProjectPhase.REVIEW
        else:
            self.current_session.current_phase = ProjectPhase.DEPLOYMENT
    
    async def _assign_work_to_agents(self) -> bool:
        """Assign work to available agents"""
        assignments_made = False
        
        for agent_id, agent in self.agents.items():
            if agent.status == AgentStatus.IDLE:
                executor = self.agent_executors[agent_id]
                
                # Try to start a work session for this agent
                if await executor.start_work_session():
                    logger.info(f"Assigned work to agent {agent_id}")
                    if self.current_session:
                        self.current_session.active_agents.add(agent_id)
                    assignments_made = True
        
        return assignments_made
    
    async def _execute_agent_work(self):
        """Execute work for all active agents"""
        working_agents = [
            agent_id for agent_id, agent in self.agents.items()
            if agent.status == AgentStatus.WORKING
        ]
        
        if not working_agents:
            return
        
        # Execute work for all working agents concurrently
        tasks = []
        for agent_id in working_agents:
            executor = self.agent_executors[agent_id]
            tasks.append(executor.execute_current_task())
        
        # Wait for all agents to complete their current tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for agent_id, result in zip(working_agents, results):
            if isinstance(result, Exception):
                logger.error(f"Agent {agent_id} encountered error: {result}")
                self.agents[agent_id].status = AgentStatus.ERROR
            elif result:
                logger.info(f"Agent {agent_id} completed task successfully")
                if self.current_session and agent_id in self.current_session.active_agents:
                    self.current_session.active_agents.remove(agent_id)
            else:
                logger.warning(f"Agent {agent_id} failed to complete task")
    
    async def _handle_agent_issues(self):
        """Handle agents that are blocked or in error state"""
        for agent_id, agent in self.agents.items():
            if agent.status == AgentStatus.BLOCKED:
                logger.warning(f"Agent {agent_id} is blocked: {agent.task}")
                # Try to resolve the blocker
                await self._resolve_agent_blocker(agent_id)
            
            elif agent.status == AgentStatus.ERROR:
                logger.error(f"Agent {agent_id} is in error state: {agent.task}")
                # Reset agent to idle after logging the error
                agent.status = AgentStatus.IDLE
                agent.task = "Ready for new assignment"
    
    async def _resolve_agent_blocker(self, agent_id: str) -> bool:
        """Try to resolve a blocker for a specific agent"""
        # This would implement blocker resolution logic
        # For now, just reset the agent to idle
        agent = self.agents[agent_id]
        agent.status = AgentStatus.IDLE
        agent.task = "Blocker resolved - ready for new assignment"
        logger.info(f"Reset blocked agent {agent_id} to idle")
        return True
    
    async def _resolve_blockers(self) -> bool:
        """Try to resolve system-wide blockers"""
        # Check for dependency issues
        pending_tasks = [
            task for task in self.task_manager.tasks.values()
            if task.status == TaskStatus.PENDING
        ]
        
        # Look for tasks with unmet dependencies
        for task in pending_tasks:
            if not self.task_manager._are_dependencies_met(task):
                logger.info(f"Task {task.id} waiting for dependencies: {task.dependencies}")
                continue
            
            # Check if we have an agent available for this task
            available_agents = [
                agent for agent in self.agents.values()
                if agent.role == task.agent_role and agent.status == AgentStatus.IDLE
            ]
            
            if not available_agents:
                logger.warning(f"No available {task.agent_role.value} agents for task {task.id}")
                continue
        
        # If we get here, there might be a fundamental issue
        return False
    
    def _any_agents_working(self) -> bool:
        """Check if any agents are currently working"""
        return any(
            agent.status == AgentStatus.WORKING 
            for agent in self.agents.values()
        )
    
    def _read_project_requirements(self) -> Dict[str, str]:
        """Read project requirement documents"""
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
                logger.warning(f"Requirements file not found: {filename}")
                requirements[req_type] = ""
        
        return requirements
    
    def get_development_status(self) -> Dict[str, any]:
        """Get current development status"""
        if not self.current_session:
            return {"status": "not_started"}
        
        # Calculate progress
        completed = self.current_session.completed_tasks
        total = self.current_session.total_tasks
        progress = (completed / total * 100) if total > 0 else 0
        
        # Get agent statuses
        agent_statuses = {
            agent_id: {
                "role": agent.role.value,
                "status": agent.status.value,
                "current_task": agent.task,
                "last_checkin": agent.last_checkin.isoformat() if agent.last_checkin else None
            }
            for agent_id, agent in self.agents.items()
        }
        
        # Get task breakdown
        task_breakdown = {}
        for status in TaskStatus:
            task_breakdown[status.value] = sum(
                1 for task in self.task_manager.tasks.values()
                if task.status == status
            )
        
        return {
            "status": "active",
            "session": {
                "started_at": self.current_session.started_at.isoformat(),
                "current_phase": self.current_session.current_phase.value,
                "progress_percent": round(progress, 1),
                "completed_tasks": completed,
                "total_tasks": total,
                "active_agents": list(self.current_session.active_agents)
            },
            "agents": agent_statuses,
            "tasks": task_breakdown
        }
    
    async def stop_development(self):
        """Stop the development process"""
        logger.info("Stopping development session...")
        
        # Stop all agent work sessions
        for executor in self.agent_executors.values():
            if executor.current_session:
                executor.current_session.ended_at = datetime.now()
                executor.current_session = None
        
        # Reset all agents to idle
        for agent in self.agents.values():
            if agent.status == AgentStatus.WORKING:
                agent.status = AgentStatus.IDLE
                agent.task = "Development session stopped"
        
        self.current_session = None
        logger.info("Development session stopped")
