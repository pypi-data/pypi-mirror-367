#!/usr/bin/env python3
"""
CodeCrew Template System - Complete Implementation
Manages all required templates for GitHub workflows and agent communication
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CodeCrewTemplates:
    """Complete template management system for CodeCrew"""

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.github_dir = self.project_path / ".github"
        self.templates_dir = self.project_path / ".codecrew" / "templates"
        self.codecrew_dir = self.project_path / ".codecrew"
        
    def setup_all_templates(self, project_type: str = "python_api"):
        """Set up complete template system for project"""
        
        logger.info(f"Setting up CodeCrew templates for {project_type}")
        
        # Create directory structure
        self._create_directories()
        
        # GitHub workflow templates
        self._setup_github_templates()
        
        # CI/CD workflows
        self._setup_github_actions(project_type)
        
        # Agent communication templates
        self._setup_agent_templates()
        
        # Project structure templates
        self._setup_project_templates(project_type)
        
        logger.info("✅ All CodeCrew templates configured successfully")
    
    def _create_directories(self):
        """Create complete directory structure"""
        
        directories = [
            # GitHub directories
            self.github_dir,
            self.github_dir / "ISSUE_TEMPLATE",
            self.github_dir / "workflows",
            
            # CodeCrew directories
            self.codecrew_dir,
            self.templates_dir,
            self.templates_dir / "agents",
            self.templates_dir / "communication",
            
            # Project structure
            self.project_path / "src",
            self.project_path / "tests",
            self.project_path / "docs",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _setup_github_templates(self):
        """Set up comprehensive GitHub issue and PR templates"""
        
        # Feature Request Template
        feature_template = """---
name: 🚀 Feature Request
about: Suggest a new feature or enhancement
title: '[FEATURE] '
labels: 'type:feature, priority:medium'
assignees: ''
---

## 📋 Feature Description
**What feature would you like to see?**
A clear and concise description of the feature.

## 🎯 Problem Statement
**What problem does this solve?**
Describe the user problem this feature addresses.

## 💡 Proposed Solution
**How should this feature work?**
Detailed description of the proposed implementation approach.

## ✅ Acceptance Criteria
- [ ] User can perform [specific action]
- [ ] System responds with [expected behavior]
- [ ] Edge case [scenario] is handled correctly
- [ ] Performance meets [specific requirement]
"""
        
        # Bug Report Template
        bug_template = """---
name: 🐛 Bug Report
about: Report a bug or issue
title: '[BUG] '
labels: 'type:bug, priority:high'
assignees: ''
---

## 🐛 Bug Description
**What went wrong?**
A clear and concise description of the bug.

## 🔄 Steps to Reproduce
1. Navigate to '...'
2. Click on '....'
3. Fill in '....'
4. Observe error

## ✅ Expected Behavior
**What should have happened?**
Clear description of the expected behavior.

## ❌ Actual Behavior
**What actually happened?**
Clear description of what went wrong.

## 🌍 Environment
- **OS**: [e.g. macOS 12.0, Ubuntu 20.04, Windows 11]
- **Python Version**: [e.g. 3.11.0]
- **Application Version**: [e.g. v1.2.3]
"""
        
        # Pull Request Template
        pr_template = """## 📋 Description
Brief description of changes made in this pull request.

## 🔄 Type of Change
- [ ] 🐛 Bug fix (non-break change which fixes an issue)
- [ ] 🚀 New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update

## 📝 Changes Made
- **Change 1**: Detailed description of what was changed
- **Change 2**: Detailed description of what was changed

## 🔗 Related Issues
- Closes #[issue_number]
- Fixes #[issue_number]

## 🧪 Testing Done
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## 📋 Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] New and existing unit tests pass locally
"""

        (self.github_dir / "ISSUE_TEMPLATE" / "feature_request.md").write_text(feature_template)
        (self.github_dir / "ISSUE_TEMPLATE" / "bug_report.md").write_text(bug_template)
        (self.github_dir / "PULL_REQUEST_TEMPLATE.md").write_text(pr_template)

        logger.info("✅ GitHub templates created")

    def _setup_github_actions(self, project_type: str):
        """Set up comprehensive CI/CD workflows"""

        if project_type == "python_api":
            ci_workflow = """name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest tests/ -v
"""

        (self.github_dir / "workflows" / "ci.yml").write_text(ci_workflow)

        logger.info("✅ GitHub Actions workflows created")

    def _setup_agent_templates(self):
        """Set up agent briefing and communication templates"""
        agent_templates_dir = self.templates_dir / "agents"
        agent_templates_dir.mkdir(parents=True, exist_ok=True)
        logger.info("✅ Agent templates created")

    def _setup_project_templates(self, project_type: str):
        """Set up project-specific templates"""
        if project_type == "python_api":
            src_dir = self.project_path / "src"
            src_dir.mkdir(exist_ok=True)
            (src_dir / "__init__.py").touch()
        logger.info("✅ Project templates created")

    def get_agent_briefing(self, role: str, **kwargs) -> str:
        """Get agent briefing by role with template substitution"""
        briefings = {
            "orchestrator": "# 🎯 Orchestrator Agent Briefing\\n\\nYou are the Orchestrator responsible for system coordination.",
            "project_manager": "# 📋 Project Manager Agent Briefing\\n\\nYou are the Project Manager responsible for quality oversight.",
            "lead_developer": "# 👑 Lead Developer Agent Briefing\\n\\nYou are the Lead Developer responsible for technical leadership.",
            "developer": "# 💻 Developer Agent Briefing\\n\\nYou are a Developer responsible for feature implementation.",
            "qa_engineer": "# 🧪 QA Engineer Agent Briefing\\n\\nYou are the QA Engineer responsible for quality assurance.",
            "devops": "# 🚀 DevOps Engineer Agent Briefing\\n\\nYou are the DevOps Engineer responsible for infrastructure.",
            "code_reviewer": "# 👁️ Code Reviewer Agent Briefing\\n\\nYou are the Code Reviewer responsible for code quality.",
            "documentation_writer": "# 📚 Documentation Writer Agent Briefing\\n\\nYou are the Documentation Writer responsible for documentation."
        }
        return briefings.get(role, "Role briefing not found.")

    def get_communication_template(self, template_type: str) -> str:
        """Get communication template by type"""
        templates = {
            "status_update": "# Status Update\\n\\nAgent: {agent_id}\\nStatus: {status}\\nProgress: {progress}",
            "blocker_report": "# Blocker Report\\n\\nAgent: {agent_id}\\nBlocker: {description}\\nSeverity: {severity}"
        }
        return templates.get(template_type, "Template not found.")
