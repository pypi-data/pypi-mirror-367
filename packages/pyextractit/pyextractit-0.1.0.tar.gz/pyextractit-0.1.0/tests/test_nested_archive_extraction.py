#!/usr/bin/env python3
"""Test nested archive extraction with new PyExtractIt features."""

import pytest
from pathlib import Path
from pyextractit.extractor import ExtractorConfig, RecursiveExtractor
from .create_fixtures import create_nested_archive_fixture


class TestNestedArchiveExtraction:
    """Test cases for nested archive extraction with new features."""
    
    def test_sequential_naming_txt_files(self, temp_dir: Path):
        """Test extracting .txt files with sequential naming."""
        # Create nested archive fixture
        archive_path = create_nested_archive_fixture(temp_dir)
        
        # Configure extractor for .txt files
        config = ExtractorConfig(
            target_pattern=r'.*\.txt$',
            prefix='txt_',
            output_dir=temp_dir / 'extracted_txt',
            unlimited_depth=True
        )
        
        # Extract files
        extractor = RecursiveExtractor(config)
        result = extractor.extract_from_archive(archive_path)
        
        # Assertions
        assert result.success is True
        assert len(result.matched_files) == 1
        assert result.matched_files[0].final_path.name == "txt_foo_sn1.txt"
        assert result.depth_reached >= 2  # Should go through multiple archive levels
    
    def test_sequential_naming_log_files(self, temp_dir: Path):
        """Test extracting .log files with sequential naming."""
        # Create nested archive fixture
        archive_path = create_nested_archive_fixture(temp_dir)
        
        # Configure extractor for .log files
        config = ExtractorConfig(
            target_pattern=r'.*\.log$',
            prefix='log_',
            output_dir=temp_dir / 'extracted_log',
            unlimited_depth=True
        )
        
        # Extract files
        extractor = RecursiveExtractor(config)
        result = extractor.extract_from_archive(archive_path)
        
        # Assertions
        assert result.success is True
        assert len(result.matched_files) == 1
        assert result.matched_files[0].final_path.name == "log_bar_sn1.log"
    
    def test_sequential_naming_multiple_files(self, temp_dir: Path):
        """Test extracting multiple files with sequential naming."""
        # Create nested archive fixture
        archive_path = create_nested_archive_fixture(temp_dir)
        
        # Configure extractor for both .txt and .log files
        config = ExtractorConfig(
            target_pattern=r'.*(\.txt|\.log)$',
            prefix='all_',
            output_dir=temp_dir / 'extracted_all',
            unlimited_depth=True
        )
        
        # Extract files
        extractor = RecursiveExtractor(config)
        result = extractor.extract_from_archive(archive_path)
        
        # Assertions
        assert result.success is True
        assert len(result.matched_files) == 2
        
        # Check sequential naming
        file_names = [match.final_path.name for match in result.matched_files]
        expected_names = ["all_foo_sn1.txt", "all_bar_sn2.log"]
        
        # Sort both lists to ensure consistent comparison
        assert sorted(file_names) == sorted(expected_names)
        
        # Check depth and extraction stats
        assert result.depth_reached >= 2
        assert result.total_extracted >= 2
    
    def test_negative_pattern_no_matches(self, temp_dir: Path):
        """Test pattern that should match nothing."""
        # Create nested archive fixture
        archive_path = create_nested_archive_fixture(temp_dir)
        
        # Configure extractor for .pdf files (should find none)
        config = ExtractorConfig(
            target_pattern=r'.*\.pdf$',
            prefix='pdf_',
            output_dir=temp_dir / 'extracted_pdf',
            unlimited_depth=True
        )
        
        # Extract files
        extractor = RecursiveExtractor(config)
        result = extractor.extract_from_archive(archive_path)
        
        # Assertions
        assert result.success is True
        assert len(result.matched_files) == 0
    
    def test_negative_specific_filename_no_matches(self, temp_dir: Path):
        """Test very specific pattern that should match nothing."""
        # Create nested archive fixture
        archive_path = create_nested_archive_fixture(temp_dir)
        
        # Configure extractor for specific filename that doesn't exist
        config = ExtractorConfig(
            target_pattern=r'^config_backup_2023\.json$',
            prefix='specific_',
            output_dir=temp_dir / 'extracted_specific',
            unlimited_depth=True
        )
        
        # Extract files
        extractor = RecursiveExtractor(config)
        result = extractor.extract_from_archive(archive_path)
        
        # Assertions
        assert result.success is True
        assert len(result.matched_files) == 0
    
    def test_negative_path_based_pattern(self, temp_dir: Path):
        """Test that path-based patterns don't match (filename-only matching)."""
        # Create nested archive fixture
        archive_path = create_nested_archive_fixture(temp_dir)
        
        # Configure extractor with path-based pattern (should find nothing)
        config = ExtractorConfig(
            target_pattern=r'.*/foo\.txt$',
            prefix='path_',
            output_dir=temp_dir / 'extracted_path',
            unlimited_depth=True
        )
        
        # Extract files
        extractor = RecursiveExtractor(config)
        result = extractor.extract_from_archive(archive_path)
        
        # Assertions
        assert result.success is True
        assert len(result.matched_files) == 0  # Should find nothing because we only match filenames
    
    def test_exact_filename_matching(self, temp_dir: Path):
        """Test exact filename matching works correctly."""
        # Create nested archive fixture
        archive_path = create_nested_archive_fixture(temp_dir)
        
        # Configure extractor for exact filename match
        config = ExtractorConfig(
            target_pattern=r'^foo\.txt$',
            prefix='exact_',
            output_dir=temp_dir / 'extracted_exact',
            unlimited_depth=True
        )
        
        # Extract files
        extractor = RecursiveExtractor(config)
        result = extractor.extract_from_archive(archive_path)
        
        # Assertions
        assert result.success is True
        assert len(result.matched_files) == 1
        assert result.matched_files[0].final_path.name == "exact_foo_sn1.txt"
    
    def test_unlimited_depth_extraction(self, temp_dir: Path):
        """Test that unlimited depth extraction works correctly."""
        # Create nested archive fixture
        archive_path = create_nested_archive_fixture(temp_dir)
        
        # Configure extractor with unlimited depth
        config = ExtractorConfig(
            target_pattern=r'.*\.txt$',
            prefix='deep_',
            output_dir=temp_dir / 'extracted_deep',
            unlimited_depth=True,
            max_depth=1  # Low archive depth limit, but unlimited_depth should override for targets
        )
        
        # Extract files
        extractor = RecursiveExtractor(config)
        result = extractor.extract_from_archive(archive_path)
        
        # Assertions
        assert result.success is True
        assert len(result.matched_files) == 1  # Should still find the file despite low archive depth
        assert result.matched_files[0].final_path.name == "deep_foo_sn1.txt"
    
    def test_limited_depth_extraction(self, temp_dir: Path):
        """Test that limited depth extraction respects depth limits."""
        # Create nested archive fixture
        archive_path = create_nested_archive_fixture(temp_dir)
        
        # Configure extractor with limited depth
        config = ExtractorConfig(
            target_pattern=r'.*\.txt$',
            prefix='limited_',
            output_dir=temp_dir / 'extracted_limited',
            unlimited_depth=False,  # Respect depth limits for targets too
            max_depth=1  # Very low depth limit
        )
        
        # Extract files
        extractor = RecursiveExtractor(config)
        result = extractor.extract_from_archive(archive_path)
        
        # Assertions
        assert result.success is True
        # Should find fewer or no files due to depth limit
        assert len(result.matched_files) <= 1
        assert result.depth_reached <= 1
    
    def test_file_content_preservation(self, temp_dir: Path):
        """Test that extracted files contain the correct content."""
        # Create nested archive fixture
        archive_path = create_nested_archive_fixture(temp_dir)
        
        # Configure extractor for .txt files
        config = ExtractorConfig(
            target_pattern=r'.*\.txt$',
            prefix='content_',
            output_dir=temp_dir / 'extracted_content',
            unlimited_depth=True
        )
        
        # Extract files
        extractor = RecursiveExtractor(config)
        result = extractor.extract_from_archive(archive_path)
        
        # Assertions
        assert result.success is True
        assert len(result.matched_files) == 1
        
        extracted_file = result.matched_files[0].final_path
        assert extracted_file.exists()
        
        # Check content matches original
        content = extracted_file.read_text()
        assert "This is the content of foo.txt file." in content
        assert "Important data that should be extracted." in content
    
    def test_multiple_archive_formats(self, temp_dir: Path):
        """Test that the nested archive extraction works through multiple formats."""
        # Create nested archive fixture
        archive_path = create_nested_archive_fixture(temp_dir)
        
        # Configure extractor
        config = ExtractorConfig(
            target_pattern=r'.*(\.txt|\.log)$',
            prefix='format_',
            output_dir=temp_dir / 'extracted_formats',
            unlimited_depth=True
        )
        
        # Extract files
        extractor = RecursiveExtractor(config)
        result = extractor.extract_from_archive(archive_path)
        
        # Assertions
        assert result.success is True
        assert len(result.matched_files) == 2
        assert result.depth_reached >= 2  # Went through ZIP -> TAR -> TAR.GZ
        
        # Verify we went through multiple format layers
        assert result.total_extracted >= 2  # Should have processed multiple archive files


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
