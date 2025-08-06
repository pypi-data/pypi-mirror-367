"""Tests for extractor validator methods to improve coverage."""

import pytest
from pydantic import ValidationError

from pyextractit.extractor import ExtractorConfig
from pyextractit.models import FileMatch, ExtractionResult
from pathlib import Path


class TestExtractorValidation:
    """Test ExtractorConfig validation methods."""
    
    def test_valid_regex_patterns(self):
        """Test various valid regex patterns."""
        valid_patterns = [
            r".*\.txt$",
            r"config_.*\.json$",
            r"[a-zA-Z0-9_]+\.log$",
            r"(file1|file2)\.dat$",
            r"^backup_\d{4}-\d{2}-\d{2}\.sql$"
        ]
        
        for pattern in valid_patterns:
            config = ExtractorConfig(target_pattern=pattern)
            assert config.target_pattern == pattern
    
    def test_invalid_regex_patterns(self):
        """Test invalid regex patterns."""
        invalid_patterns = [
            r"[unclosed",
            r"(?P<unclosed",
            r"*invalid",
            r"(?invalid)",
        ]
        
        for pattern in invalid_patterns:
            with pytest.raises(ValidationError) as exc_info:
                ExtractorConfig(target_pattern=pattern)
            assert "Invalid regex pattern" in str(exc_info.value)
    
    def test_max_depth_validation(self):
        """Test max_depth validation."""
        # Valid depths
        for depth in [1, 5, 10, 25, 50]:
            config = ExtractorConfig(target_pattern=r".*\.txt$", max_depth=depth)
            assert config.max_depth == depth
        
        # Invalid depths
        invalid_depths = [0, -1, 51, 100]
        for depth in invalid_depths:
            with pytest.raises(ValidationError) as exc_info:
                ExtractorConfig(target_pattern=r".*\.txt$", max_depth=depth)
            assert "Max depth must be between 1 and 50" in str(exc_info.value)
    
    def test_config_with_all_defaults(self):
        """Test config creation with default values."""
        config = ExtractorConfig(target_pattern=r".*\.txt$")
        
        assert config.target_pattern == r".*\.txt$"
        assert config.prefix == "extracted_"
        assert config.max_depth == 10
        assert config.output_dir is None
        assert config.preserve_structure is False
        assert config.overwrite_existing is False
        assert config.temp_dir is None
    
    def test_config_with_custom_values(self, temp_dir: Path):
        """Test config with all custom values."""
        output_dir = temp_dir / "output"
        temp_custom_dir = temp_dir / "temp"
        
        config = ExtractorConfig(
            target_pattern=r"custom_.*\.log$",
            prefix="custom_prefix_",
            max_depth=15,
            output_dir=output_dir,
            preserve_structure=True,
            overwrite_existing=True,
            temp_dir=temp_custom_dir
        )
        
        assert config.target_pattern == r"custom_.*\.log$"
        assert config.prefix == "custom_prefix_"
        assert config.max_depth == 15
        assert config.output_dir == output_dir
        assert config.preserve_structure is True
        assert config.overwrite_existing is True
        assert config.temp_dir == temp_custom_dir


class TestModelValidation:
    """Test model validation methods."""
    
    def test_file_match_size_validation(self, temp_dir: Path):
        """Test FileMatch size validation."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        # Valid sizes
        for size in [0, 1, 100, 1024, 999999]:
            match = FileMatch(
                original_path=test_file,
                extracted_path=test_file,
                size=size
            )
            assert match.size == size
        
        # Invalid size (negative)
        with pytest.raises(ValidationError) as exc_info:
            FileMatch(
                original_path=test_file,
                extracted_path=test_file,
                size=-1
            )
        assert "File size cannot be negative" in str(exc_info.value)
    
    def test_file_match_archive_flag(self, temp_dir: Path):
        """Test FileMatch is_archive flag."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        # Test with archive flag True
        match = FileMatch(
            original_path=test_file,
            extracted_path=test_file,
            size=100,
            is_archive=True
        )
        assert match.is_archive is True
        
        # Test with archive flag False (default)
        match = FileMatch(
            original_path=test_file,
            extracted_path=test_file,
            size=100
        )
        assert match.is_archive is False
    
    def test_extraction_result_timestamp(self, temp_dir: Path):
        """Test ExtractionResult timestamp field."""
        from datetime import datetime
        
        before = datetime.now()
        
        result = ExtractionResult(
            source_archive=temp_dir / "test.zip",
            extraction_dir=temp_dir / "output",
            extraction_time=1.0
        )
        
        after = datetime.now()
        
        # Timestamp should be automatically set to current time
        assert before <= result.timestamp <= after
    
    def test_extraction_result_with_custom_timestamp(self, temp_dir: Path):
        """Test ExtractionResult with custom timestamp."""
        from datetime import datetime
        
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        
        result = ExtractionResult(
            source_archive=temp_dir / "test.zip",
            extraction_dir=temp_dir / "output",
            extraction_time=1.0,
            timestamp=custom_time
        )
        
        assert result.timestamp == custom_time
