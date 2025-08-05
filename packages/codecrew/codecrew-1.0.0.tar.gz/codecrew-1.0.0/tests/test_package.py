"""Test package imports and basic functionality."""

import pytest


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


def test_version_format():
    """Test that version follows semantic versioning."""
    import codecrew
    import re
    
    # Check semantic versioning pattern (major.minor.patch)
    version_pattern = r'^\d+\.\d+\.\d+$'
    assert re.match(version_pattern, codecrew.__version__)
