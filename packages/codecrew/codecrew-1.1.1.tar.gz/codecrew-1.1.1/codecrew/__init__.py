"""
CodeCrew Multi-Agent Development System

A comprehensive multi-agent development system that automates software development
workflows using AI agents for project management, development, testing, and deployment.
"""

__version__ = "1.1.1"
__author__ = "Derek Vitrano"
__email__ = "derek@example.com"
__description__ = "CodeCrew Multi-Agent Development System"

from .main import CodeCrewOrchestrator
from .cli import main as cli_main

__all__ = [
    "CodeCrewOrchestrator",
    "cli_main",
    "__version__",
]
