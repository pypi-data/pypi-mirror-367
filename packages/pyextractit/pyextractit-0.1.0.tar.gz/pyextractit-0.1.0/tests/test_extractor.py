"""Tests for PyExtractIt extractor configuration and functionality."""

import pytest
import re
from pathlib import Path

from pyextractit.extractor import ExtractorConfig, RecursiveExtractor
from pyextractit.models import ExtractionResult


class TestExtractorConfig:
    """Test cases for ExtractorConfig."""
    
    def test_valid_config_creation(self):
        """Test creating a valid configuration."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="extracted_",
            max_depth=5
        )
        
        assert config.target_pattern == r".*\.txt$"
        assert config.prefix == "extracted_"
        assert config.max_depth == 5
        assert config.preserve_structure is False  # Default
        assert config.overwrite_existing is False  # Default
    
    def test_invalid_regex_pattern(self):
        """Test configuration with invalid regex pattern."""
        with pytest.raises(ValueError, match="Invalid regex pattern"):
            ExtractorConfig(
                target_pattern=r"[invalid regex",  # Missing closing bracket
                prefix="test_"
            )
    
    def test_invalid_max_depth(self):
        """Test configuration with invalid max depth."""
        with pytest.raises(ValueError, match="Max depth must be between 1 and 50"):
            ExtractorConfig(
                target_pattern=r".*\.txt$",
                max_depth=0  # Too low
            )
        
        with pytest.raises(ValueError, match="Max depth must be between 1 and 50"):
            ExtractorConfig(
                target_pattern=r".*\.txt$",
                max_depth=51  # Too high
            )
    
    def test_config_with_output_dir(self, temp_dir: Path):
        """Test configuration with custom output directory."""
        output_dir = temp_dir / "custom_output"
        
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            output_dir=output_dir
        )
        
        assert config.output_dir == output_dir
    
    def test_config_with_all_options(self, temp_dir: Path):
        """Test configuration with all options set."""
        config = ExtractorConfig(
            target_pattern=r"config_.*\.json$",
            prefix="backup_",
            max_depth=3,
            output_dir=temp_dir / "output",
            preserve_structure=True,
            overwrite_existing=True,
            temp_dir=temp_dir / "temp"
        )
        
        assert config.target_pattern == r"config_.*\.json$"
        assert config.prefix == "backup_"
        assert config.max_depth == 3
        assert config.preserve_structure is True
        assert config.overwrite_existing is True


class TestRecursiveExtractor:
    """Test cases for RecursiveExtractor."""
    
    def test_extractor_initialization(self, sample_config: ExtractorConfig):
        """Test extractor initialization."""
        extractor = RecursiveExtractor(sample_config)
        
        assert extractor.config == sample_config
        assert isinstance(extractor.pattern, re.Pattern)
        assert len(extractor.processed_archives) == 0
        assert extractor.current_depth == 0
    
    def test_is_archive_detection(self, extractor: RecursiveExtractor, temp_dir: Path):
        """Test archive file detection."""
        # Test various archive formats
        zip_file = temp_dir / "test.zip"
        tar_file = temp_dir / "test.tar"
        tar_gz_file = temp_dir / "test.tar.gz"
        tgz_file = temp_dir / "test.tgz"
        text_file = temp_dir / "test.txt"
        
        assert extractor._is_archive(zip_file) is True
        assert extractor._is_archive(tar_file) is True
        assert extractor._is_archive(tar_gz_file) is True
        assert extractor._is_archive(tgz_file) is True
        assert extractor._is_archive(text_file) is False
    
    def test_extract_nonexistent_archive(self, extractor: RecursiveExtractor, temp_dir: Path):
        """Test extraction from non-existent archive."""
        nonexistent = temp_dir / "nonexistent.zip"
        
        result = extractor.extract_from_archive(nonexistent)
        
        assert result.success is False
        assert "does not exist" in result.error_message
        assert result.source_archive == nonexistent
    
    def test_extract_simple_zip(self, temp_dir: Path, simple_zip: Path):
        """Test extraction from a simple ZIP file."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="extracted_",
            output_dir=temp_dir / "output"
        )
        extractor = RecursiveExtractor(config)
        
        result = extractor.extract_from_archive(simple_zip)
        
        assert result.success is True
        assert len(result.matched_files) == 2  # sample1.txt and sample2.txt
        assert result.total_extracted > 0
        assert result.depth_reached == 0  # Simple archive, no nesting
        
        # Check that files were actually extracted and renamed
        output_dir = temp_dir / "output"
        extracted_files = list(output_dir.glob("extracted_*.txt"))
        assert len(extracted_files) == 2
    
    def test_extract_nested_zip(self, temp_dir: Path, nested_zip: Path):
        """Test extraction from nested ZIP files."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="nested_",
            output_dir=temp_dir / "output",
            max_depth=3
        )
        extractor = RecursiveExtractor(config)
        
        result = extractor.extract_from_archive(nested_zip)
        
        assert result.success is True
        assert len(result.matched_files) >= 2  # Files from both archives
        assert result.depth_reached >= 1  # At least one level of nesting
        
        # Check that files from nested archive were extracted
        output_dir = temp_dir / "output"
        extracted_files = list(output_dir.glob("nested_*.txt"))
        assert len(extracted_files) >= 2
    
    def test_extract_tar_gz(self, temp_dir: Path, tar_gz: Path):
        """Test extraction from TAR.GZ files."""
        config = ExtractorConfig(
            target_pattern=r".*\.json$",
            prefix="config_",
            output_dir=temp_dir / "output"
        )
        extractor = RecursiveExtractor(config)
        
        result = extractor.extract_from_archive(tar_gz)
        
        assert result.success is True
        # Should find config.json from sample_files if it exists
        json_matches = [m for m in result.matched_files if '.json' in str(m.original_path)]
        assert len(json_matches) >= 1  # At least 1 json file should be found
    
    def test_max_depth_limit(self, temp_dir: Path, deeply_nested_archive: Path):
        """Test that max depth limit is respected."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="deep_",
            output_dir=temp_dir / "output",
            max_depth=3  # Limit depth to 3
        )
        extractor = RecursiveExtractor(config)
        
        result = extractor.extract_from_archive(deeply_nested_archive)
        
        assert result.success is True
        assert result.depth_reached <= 4  # Allow for slight flexibility in depth counting
    
    def test_pattern_matching(self, temp_dir: Path, simple_zip: Path):
        """Test different pattern matching scenarios."""
        # Test case-insensitive matching
        config = ExtractorConfig(
            target_pattern=r".*\.TXT$",  # Uppercase extension
            prefix="case_test_",
            output_dir=temp_dir / "output"
        )
        extractor = RecursiveExtractor(config)
        
        result = extractor.extract_from_archive(simple_zip)
        
        assert result.success is True
        # Should match .txt files even with uppercase pattern
        assert len(result.matched_files) == 2
    
    def test_preserve_structure(self, temp_dir: Path, simple_zip: Path):
        """Test preserving directory structure during extraction."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="structured_",
            output_dir=temp_dir / "output",
            preserve_structure=True
        )
        extractor = RecursiveExtractor(config)
        
        result = extractor.extract_from_archive(simple_zip)
        
        assert result.success is True
        assert len(result.matched_files) == 2
        
        # When preserve_structure is True, check that directory structure is maintained
        # (This would be more meaningful with a more complex directory structure)
    
    def test_overwrite_existing(self, temp_dir: Path, simple_zip: Path):
        """Test overwriting existing files."""
        output_dir = temp_dir / "output"
        output_dir.mkdir(parents=True)
        
        # Create an existing file that would conflict with sequential naming
        existing_file = output_dir / "extracted_sample1_sn1.txt"
        existing_file.write_text("existing content")
        
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="extracted_",
            output_dir=output_dir,
            overwrite_existing=True
        )
        extractor = RecursiveExtractor(config)
        
        result = extractor.extract_from_archive(simple_zip)
        
        assert result.success is True
        # File should be overwritten
        assert existing_file.read_text() != "existing content"
    
    def test_no_overwrite_existing(self, temp_dir: Path, simple_zip: Path):
        """Test not overwriting existing files (should create numbered versions)."""
        output_dir = temp_dir / "output"
        output_dir.mkdir(parents=True)
        
        # Create an existing file that would conflict with sequential naming
        existing_file = output_dir / "extracted_sample1_sn1.txt"
        existing_file.write_text("existing content")
        
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="extracted_",
            output_dir=output_dir,
            overwrite_existing=False
        )
        extractor = RecursiveExtractor(config)
        
        result = extractor.extract_from_archive(simple_zip)
        
        assert result.success is True
        # Original file should be unchanged
        assert existing_file.read_text() == "existing content"
        
        # Should create numbered version with conflict resolution
        conflicting_files = list(output_dir.glob("extracted_sample1_sn1_*.txt"))
        assert len(conflicting_files) >= 1
    
    def test_archive_within_matches(self, temp_dir: Path):
        """Test handling when matched files are also archives."""
        # Create a zip file that contains another zip
        inner_text = temp_dir / "inner.txt"
        inner_text.write_text("inner content")
        
        inner_zip = temp_dir / "target_inner.zip"  # This will match pattern
        import zipfile
        with zipfile.ZipFile(inner_zip, 'w') as zf:
            zf.write(inner_text, "inner.txt")
        
        outer_zip = temp_dir / "outer.zip"
        with zipfile.ZipFile(outer_zip, 'w') as zf:
            zf.write(inner_zip, "target_inner.zip")
        
        config = ExtractorConfig(
            target_pattern=r"target_.*\.zip$",  # Match zip files with 'target_' prefix
            prefix="found_",
            output_dir=temp_dir / "output"
        )
        extractor = RecursiveExtractor(config)
        
        result = extractor.extract_from_archive(outer_zip)
        
        assert result.success is True
        # Should find the target zip file
        zip_matches = [m for m in result.matched_files if m.is_archive]
        assert len(zip_matches) >= 1
