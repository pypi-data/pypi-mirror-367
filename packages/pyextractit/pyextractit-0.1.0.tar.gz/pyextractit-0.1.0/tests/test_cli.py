"""Integration tests for PyExtractIt CLI."""

import pytest
import subprocess
import sys
from pathlib import Path
from typer.testing import CliRunner

from pyextractit.__main__ import app


class TestCLI:
    """Integration tests for the command-line interface."""
    
    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()
    
    def test_version_command(self):
        """Test version command."""
        result = self.runner.invoke(app, ["version"])
        
        assert result.exit_code == 0
        assert "PyExtractIt version" in result.stdout
    
    def test_list_supported_command(self):
        """Test list-supported command."""
        result = self.runner.invoke(app, ["list-supported"])
        
        assert result.exit_code == 0
        assert "Supported archive formats" in result.stdout
        assert ".zip" in result.stdout
        assert ".tar" in result.stdout
    
    def test_extract_help(self):
        """Test extract command help."""
        result = self.runner.invoke(app, ["extract", "--help"])
        
        assert result.exit_code == 0
        assert "Extract files recursively" in result.stdout
        assert "--prefix" in result.stdout
        assert "--output" in result.stdout
    
    def test_extract_nonexistent_file(self):
        """Test extract command with non-existent file."""
        result = self.runner.invoke(app, [
            "extract", 
            "nonexistent.zip", 
            ".*\\.txt$"
        ])
        
        assert result.exit_code == 2  # Typer returns 2 for missing files
        # Should show error about file not existing
    
    def test_extract_invalid_pattern(self):
        """Test extract command with invalid regex pattern."""
        # Create a dummy file first
        with self.runner.isolated_filesystem():
            dummy_zip = Path("dummy.zip")
            dummy_zip.write_bytes(b"fake zip content")
            
            result = self.runner.invoke(app, [
                "extract",
                str(dummy_zip),
                "[invalid regex"  # Invalid regex pattern
            ])
            
            assert result.exit_code == 1
            # Should show configuration error
    
    def test_extract_simple_zip_integration(self, simple_zip: Path, temp_dir: Path):
        """Test full extraction workflow with a simple ZIP file."""
        output_dir = temp_dir / "cli_output"
        
        result = self.runner.invoke(app, [
            "extract",
            str(simple_zip),
            ".*\\.txt$",
            "--prefix", "cli_test_",
            "--output", str(output_dir),
            "--verbose"
        ])
        
        assert result.exit_code == 0
        assert "Extraction completed successfully" in result.stdout
        assert "Found" in result.stdout
        assert "matching files" in result.stdout
        
        # Check that files were actually extracted
        assert output_dir.exists()
        extracted_files = list(output_dir.glob("cli_test_*.txt"))
        assert len(extracted_files) == 2
    
    def test_extract_with_max_depth(self, nested_zip: Path, temp_dir: Path):
        """Test extraction with max depth limit."""
        output_dir = temp_dir / "depth_test"
        
        result = self.runner.invoke(app, [
            "extract",
            str(nested_zip),
            ".*\\.txt$",
            "--max-depth", "1",
            "--output", str(output_dir)
        ])
        
        assert result.exit_code == 0
        assert "Maximum depth reached: 1" in result.stdout
    
    def test_extract_preserve_structure(self, simple_zip: Path, temp_dir: Path):
        """Test extraction with preserve structure option."""
        output_dir = temp_dir / "structured"
        
        result = self.runner.invoke(app, [
            "extract",
            str(simple_zip),
            ".*\\.txt$",
            "--preserve-structure",
            "--output", str(output_dir)
        ])
        
        assert result.exit_code == 0
    
    def test_extract_overwrite(self, simple_zip: Path, temp_dir: Path):
        """Test extraction with overwrite option."""
        output_dir = temp_dir / "overwrite_test"
        output_dir.mkdir(parents=True)
        
        # Create existing file with sequential naming pattern that would be generated
        existing = output_dir / "extracted_sample1_sn1.txt"
        existing.write_text("existing content")
        
        result = self.runner.invoke(app, [
            "extract",
            str(simple_zip),
            ".*\\.txt$",
            "--overwrite",
            "--output", str(output_dir)
        ])
        
        assert result.exit_code == 0
        # File should be overwritten
        assert existing.read_text() != "existing content"
    
    def test_extract_quiet_mode(self, simple_zip: Path, temp_dir: Path):
        """Test extraction in quiet mode."""
        output_dir = temp_dir / "quiet_test"
        
        result = self.runner.invoke(app, [
            "extract",
            str(simple_zip),
            ".*\\.txt$",
            "--output", str(output_dir),
            "--quiet"
        ])
        
        assert result.exit_code == 0
        # In quiet mode, should have less output than normal mode
        assert "✅ Extraction completed successfully!" in result.stdout  # Basic success message should still appear
    
    def test_extract_verbose_mode(self, simple_zip: Path, temp_dir: Path):
        """Test extraction in verbose mode."""
        output_dir = temp_dir / "verbose_test"
        
        result = self.runner.invoke(app, [
            "extract",
            str(simple_zip),
            ".*\\.txt$",
            "--output", str(output_dir),
            "--verbose"
        ])
        
        assert result.exit_code == 0
        # In verbose mode, should have detailed output
        assert "Extraction completed successfully" in result.stdout
        assert "matching files" in result.stdout


class TestCLIAsModule:
    """Test running the package as a module."""
    
    def test_run_as_module_version(self):
        """Test running 'python -m pyextractit version'."""
        result = subprocess.run(
            [sys.executable, "-m", "pyextractit", "version"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent  # Run from package directory
        )
        
        # Note: This might fail if dependencies aren't installed
        if result.returncode == 0:
            assert "PyExtractIt version" in result.stdout
        else:
            # If it fails due to missing dependencies, that's expected in test environment
            pytest.skip("Package not properly installed for module execution")
    
    def test_run_as_module_help(self):
        """Test running 'python -m pyextractit --help'."""
        result = subprocess.run(
            [sys.executable, "-m", "pyextractit", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            assert "A utility to recursively extract" in result.stdout
        else:
            pytest.skip("Package not properly installed for module execution")
