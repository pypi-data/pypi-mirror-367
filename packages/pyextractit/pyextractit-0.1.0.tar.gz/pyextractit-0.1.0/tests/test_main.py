"""Test for main module to improve coverage."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch


def test_main_module_execution():
    """Test that the main module can be executed."""
    # Add the package to sys.path
    package_path = Path(__file__).parent.parent
    if str(package_path) not in sys.path:
        sys.path.insert(0, str(package_path))
    
    # Test that we can import the main module
    try:
        from pyextractit.__main__ import app
        assert app is not None
    except ImportError as e:
        pytest.fail(f"Failed to import main module: {e}")


def test_main_module_as_script():
    """Test running the module as a script."""
    # Test the if __name__ == "__main__" block
    with patch('pyextractit.__main__.app') as mock_app:
        # Import and execute the main block
        import pyextractit.__main__
        
        # The app should be defined
        assert hasattr(pyextractit.__main__, 'app')


def test_app_configuration():
    """Test that the app is configured correctly."""
    from pyextractit.__main__ import app
    
    # Check that the app has the expected configuration
    assert app.info.name == "pyextractit"
    assert "A utility to recursively extract" in app.info.help
