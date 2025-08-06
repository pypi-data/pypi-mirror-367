"""Final comprehensive tests to reach 80% coverage."""

import pytest
import tempfile
import zipfile
import tarfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

from pyextractit.extractor import RecursiveExtractor, ExtractorConfig
from pyextractit.models import ExtractionResult, FileMatch
from pyextractit import utils
from typer.testing import CliRunner
from pyextractit.__main__ import app


class TestFinalCoverage:
    """Final tests to achieve 80% coverage target."""
    
    def test_cli_main_execution(self):
        """Test CLI main execution paths."""
        runner = CliRunner()
        
        # Test main help
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        
        # Test version
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "PyExtractIt version" in result.stdout
        
        # Test list-supported
        result = runner.invoke(app, ["list-supported"])
        assert result.exit_code == 0
        assert "Supported archive formats" in result.stdout
    
    def test_extractor_logging_setup(self):
        """Test extractor logging setup."""
        config = ExtractorConfig(target_pattern=r".*\.txt$")
        
        with patch('pyextractit.extractor.logger') as mock_logger:
            extractor = RecursiveExtractor(config)
            # Logging should be configured during initialization
            mock_logger.add.assert_called()
    
    def test_utils_all_functions(self, temp_dir: Path):
        """Test all utility functions for coverage."""
        
        # Test calculate_file_hash
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content for hash")
        
        sha256_hash = utils.calculate_file_hash(test_file, "sha256")
        assert len(sha256_hash) == 64
        
        md5_hash = utils.calculate_file_hash(test_file, "md5")
        assert len(md5_hash) == 32
        
        # Test get_file_type
        json_file = temp_dir / "test.json"
        json_file.write_text('{"test": true}')
        mime_type = utils.get_file_type(json_file)
        assert mime_type is not None
        
        # Test sanitize_filename
        safe_name = utils.sanitize_filename("normal_file.txt")
        assert safe_name == "normal_file.txt"
        
        unsafe_name = utils.sanitize_filename("bad<>file.txt")
        assert "<" not in unsafe_name and ">" not in unsafe_name
        
        # Test find_files_by_pattern
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.py").write_text("content2")
        
        txt_files = utils.find_files_by_pattern(temp_dir, "*.txt")
        assert len(txt_files) >= 1
        
        # Test get_human_readable_size
        assert utils.get_human_readable_size(1024) == "1.0 KB"
        assert utils.get_human_readable_size(1024*1024) == "1.0 MB"
        assert utils.get_human_readable_size(500) == "500.0 B"
    
    def test_extractor_edge_cases(self, temp_dir: Path):
        """Test extractor edge cases for coverage."""
        
        # Test with various configuration options
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="edge_",
            max_depth=2,
            output_dir=temp_dir / "output",
            preserve_structure=True,
            overwrite_existing=True,
            temp_dir=temp_dir / "temp"
        )
        
        extractor = RecursiveExtractor(config)
        
        # Test archive format detection
        assert extractor._is_archive(Path("test.zip")) is True
        assert extractor._is_archive(Path("test.tar.gz")) is True
        assert extractor._is_archive(Path("test.txt")) is False
        
        # Test with empty archive
        empty_zip = temp_dir / "empty.zip"
        with zipfile.ZipFile(empty_zip, 'w') as zf:
            pass  # Empty archive
        
        result = extractor.extract_from_archive(empty_zip)
        assert result.success is True
        assert len(result.matched_files) == 0
    
    def test_extraction_with_all_tar_formats(self, temp_dir: Path):
        """Test extraction with all supported TAR formats."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="tar_test_"
        )
        extractor = RecursiveExtractor(config)
        
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("tar test content")
        
        # Test different TAR formats
        tar_formats = [
            ("test.tar", "w"),
            ("test.tar.gz", "w:gz"),
            ("test.tar.bz2", "w:bz2"),
        ]
        
        for filename, mode in tar_formats:
            tar_path = temp_dir / filename
            
            with tarfile.open(tar_path, mode) as tf:
                tf.add(test_file, arcname="test.txt")
            
            # Test TAR extraction method directly
            extract_dir = temp_dir / f"extract_{filename.replace('.', '_')}"
            extract_dir.mkdir(exist_ok=True)
            
            extracted = extractor._extract_tar(tar_path, extract_dir)
            assert len(extracted) >= 1
    
    def test_cli_error_handling(self, temp_dir: Path):
        """Test CLI error handling scenarios."""
        runner = CliRunner()
        
        # Test with non-existent file
        result = runner.invoke(app, [
            "extract",
            "nonexistent.zip",
            ".*\\.txt$"
        ])
        assert result.exit_code == 2  # Typer file validation error
        
        # Test with invalid pattern
        dummy_file = temp_dir / "dummy.txt"
        dummy_file.write_text("dummy")
        
        result = runner.invoke(app, [
            "extract",
            str(dummy_file),
            "[invalid"  # Invalid regex
        ])
        assert result.exit_code == 1  # Configuration error
    
    def test_model_edge_cases(self, temp_dir: Path):
        """Test model edge cases."""
        
        # Test FileMatch with all fields
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        
        match = FileMatch(
            original_path=test_file,
            extracted_path=test_file,
            final_path=temp_dir / "final.txt",
            size=4,
            is_archive=True
        )
        
        assert match.original_path == test_file
        assert match.is_archive is True
        
        # Test ExtractionResult with all fields
        result = ExtractionResult(
            source_archive=temp_dir / "source.zip",
            extraction_dir=temp_dir / "output",
            matched_files=[match],
            total_extracted=5,
            depth_reached=3,
            extraction_time=2.5,
            success=True,
            error_message=None
        )
        
        assert len(result.matched_files) == 1
        assert result.success is True
        assert result.error_message is None
    
    def test_file_processing_with_conflicts(self, temp_dir: Path):
        """Test file processing with various conflict scenarios."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="conflict_",
            output_dir=temp_dir / "output",
            overwrite_existing=False
        )
        extractor = RecursiveExtractor(config)
        
        # Create output directory
        config.output_dir.mkdir(exist_ok=True)
        
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        # Create existing file to cause conflict
        existing = config.output_dir / "conflict_test.txt"
        existing.write_text("existing")
        
        # Process file (should create numbered version)
        match = extractor._process_matching_file(test_file, config.output_dir)
        
        assert match.final_path is not None
        assert match.final_path != existing  # Should be different due to conflict
    
    def test_deeply_nested_processing(self, temp_dir: Path):
        """Test processing of deeply nested archives."""
        
        # Create a 3-level nested structure
        level3_file = temp_dir / "level3.txt"
        level3_file.write_text("deepest content")
        
        level3_zip = temp_dir / "level3.zip"
        with zipfile.ZipFile(level3_zip, 'w') as zf:
            zf.write(level3_file, "level3.txt")
        
        level2_zip = temp_dir / "level2.zip"
        with zipfile.ZipFile(level2_zip, 'w') as zf:
            zf.write(level3_zip, "level3.zip")
            zf.writestr("level2.txt", "middle content")
        
        level1_zip = temp_dir / "level1.zip"
        with zipfile.ZipFile(level1_zip, 'w') as zf:
            zf.write(level2_zip, "level2.zip")
            zf.writestr("level1.txt", "top content")
        
        # Test with max depth
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="deep_",
            max_depth=3,
            output_dir=temp_dir / "output"
        )
        extractor = RecursiveExtractor(config)
        
        result = extractor.extract_from_archive(level1_zip)
        
        assert result.success is True
        assert result.depth_reached >= 1
        # Should find multiple txt files from different levels
        assert len(result.matched_files) >= 1
    
    def test_extraction_failure_recovery(self, temp_dir: Path):
        """Test extraction failure scenarios and recovery."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="fail_"
        )
        extractor = RecursiveExtractor(config)
        
        # Test with corrupted archive
        corrupted = temp_dir / "corrupted.zip"
        corrupted.write_bytes(b"This is not a real ZIP file")
        
        result = extractor.extract_from_archive(corrupted)
        assert result.success is False
        assert result.error_message is not None
        assert len(result.error_message) > 0
