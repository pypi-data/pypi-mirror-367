"""Basic tests for CodeCrew package."""

import pytest
from pathlib import Path


def test_package_import():
    """Test that the package can be imported."""
    import codecrew
    assert codecrew.__version__
    assert codecrew.__author__


def test_main_import():
    """Test that main components can be imported."""
    from codecrew import CodeCrewOrchestrator
    assert CodeCrewOrchestrator


def test_cli_import():
    """Test that CLI can be imported."""
    from codecrew import cli_main
    assert cli_main


def test_templates_import():
    """Test that templates can be imported."""
    from codecrew.templates import CodeCrewTemplates
    assert CodeCrewTemplates


def test_orchestrator_creation():
    """Test that orchestrator can be created."""
    from codecrew.main import CodeCrewOrchestrator
    
    orchestrator = CodeCrewOrchestrator()
    assert orchestrator is not None
    assert orchestrator.root_path == Path.cwd()


def test_templates_creation():
    """Test that templates can be created."""
    from codecrew.templates import CodeCrewTemplates
    
    templates = CodeCrewTemplates(Path.cwd())
    assert templates is not None
    assert templates.project_path == Path.cwd()
