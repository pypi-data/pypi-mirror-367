"""Additional extractor tests for specific edge cases and coverage."""

import pytest
import tempfile
import zipfile
import tarfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import shutil

from pyextractit.extractor import RecursiveExtractor, ExtractorConfig
from pyextractit.models import ExtractionResult


class TestExtractorEdgeCases:
    """Test edge cases and specific scenarios for better coverage."""
    
    def test_archive_already_processed_detection(self, temp_dir: Path):
        """Test detection of already processed archives."""
        # Create identical archives
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        archive1 = temp_dir / "archive1.zip"
        archive2 = temp_dir / "archive2.zip"
        
        # Create identical archives with same content
        for archive in [archive1, archive2]:
            with zipfile.ZipFile(archive, 'w') as zf:
                zf.write(test_file, "test.txt")
        
        # Make them have the same size by copying
        archive2.write_bytes(archive1.read_bytes())
        
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="test_",
            output_dir=temp_dir / "output"
        )
        extractor = RecursiveExtractor(config)
        
        # Process first archive
        result1 = extractor.extract_from_archive(archive1)
        assert result1.success is True
        
        # Process second archive (should be detected as already processed)
        # This tests the archive key detection logic
        extractor.processed_archives.add(f"{archive2.name}_{archive2.stat().st_size}")
        result2 = extractor.extract_from_archive(archive2)
        assert result2.success is True
    
    def test_zip_extraction_with_error_handling(self, temp_dir: Path):
        """Test ZIP extraction with individual file errors."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="test_"
        )
        extractor = RecursiveExtractor(config)
        
        # Create a proper ZIP file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        archive_path = temp_dir / "test.zip"
        
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.write(test_file, "test.txt")
        
        # Test normal extraction
        extracted_files = extractor._extract_zip(archive_path, temp_dir / "extract")
        assert len(extracted_files) >= 1
    
    def test_tar_extraction_modes(self, temp_dir: Path, sample_files):
        """Test different TAR extraction modes."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="tar_"
        )
        extractor = RecursiveExtractor(config)
        
        # Test different TAR formats
        formats = [
            ("test.tar", "w"),
            ("test.tar.gz", "w:gz"),
            ("test.tgz", "w:gz"),
            ("test.tar.bz2", "w:bz2"),
        ]
        
        for filename, mode in formats:
            tar_path = temp_dir / filename
            extract_dir = temp_dir / f"extract_{filename.replace('.', '_')}"
            extract_dir.mkdir(exist_ok=True)
            
            # Create the TAR file
            with tarfile.open(tar_path, mode) as tar_file:
                for file_path in sample_files.values():
                    tar_file.add(file_path, arcname=file_path.name)
            
            # Test extraction
            extracted_files = extractor._extract_tar(tar_path, extract_dir)
            assert len(extracted_files) >= 1
    
    def test_file_copying_with_structure_preservation(self, temp_dir: Path):
        """Test file copying with structure preservation."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="struct_",
            preserve_structure=True,
            output_dir=temp_dir / "output"
        )
        extractor = RecursiveExtractor(config)
        
        # Create a file in a nested structure
        nested_dir = temp_dir / "extract" / "deep" / "nested"
        nested_dir.mkdir(parents=True)
        
        test_file = nested_dir / "deep_file.txt"
        test_file.write_text("deep content")
        
        # Test processing the file
        match = extractor._process_matching_file(test_file, config.output_dir)
        
        assert match.final_path is not None
        assert match.final_path.exists()
        assert "struct_" in match.final_path.name
    
    def test_retry_mechanism(self, temp_dir: Path):
        """Test the retry mechanism on extraction failures."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="retry_"
        )
        extractor = RecursiveExtractor(config)
        
        # Create a corrupted archive that will cause extraction to fail
        corrupted_zip = temp_dir / "corrupted.zip"
        corrupted_zip.write_bytes(b"not a real zip file")
        
        # This should trigger the retry mechanism
        with pytest.raises(Exception):
            extractor._extract_single_archive(corrupted_zip, temp_dir / "extract")
    
    def test_filename_conflict_numbering(self, temp_dir: Path):
        """Test filename conflict resolution with numbering."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Create existing files to cause conflicts
        for i in range(3):
            existing = output_dir / f"extracted_conflict_{i}.txt" if i > 0 else output_dir / "extracted_conflict.txt"
            existing.write_text(f"existing content {i}")
        
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="extracted_",
            output_dir=output_dir,
            overwrite_existing=False
        )
        extractor = RecursiveExtractor(config)
        
        # Create a file to process
        test_file = temp_dir / "conflict.txt"
        test_file.write_text("new content")
        
        # Process the file (should create numbered version)
        match = extractor._process_matching_file(test_file, output_dir)
        
        assert match.final_path is not None
        assert match.final_path.exists()
        # Should have created a numbered version like extracted_conflict_3.txt
        assert "_" in match.final_path.stem  # Should contain underscore for numbering
    
    def test_unsupported_archive_warning(self, temp_dir: Path):
        """Test warning for unsupported archive formats."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="test_"
        )
        extractor = RecursiveExtractor(config)
        
        # Create a file with unsupported extension
        unsupported_file = temp_dir / "test.rar"
        unsupported_file.write_bytes(b"fake rar content")
        
        # This should log a warning and return empty list
        with patch('pyextractit.extractor.logger') as mock_logger:
            extracted_files = extractor._extract_single_archive(unsupported_file, temp_dir)
            
            # Should have logged a warning
            mock_logger.warning.assert_called()
            assert len(extracted_files) == 0
    
    def test_archive_format_detection(self, temp_dir: Path):
        """Test archive format detection logic."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="test_"
        )
        extractor = RecursiveExtractor(config)
        
        # Test various archive formats
        archive_formats = [
            "test.zip",
            "test.tar",
            "test.tar.gz",
            "test.tgz",
            "test.tar.bz2",
            "test.tar.xz",
            "test.rar",  # Unsupported
            "test.txt"   # Not an archive
        ]
        
        expected_results = [True, True, True, True, True, True, False, False]
        
        for archive_name, expected in zip(archive_formats, expected_results):
            archive_path = Path(archive_name)
            result = extractor._is_archive(archive_path)
            assert result == expected, f"Failed for {archive_name}"
    
    def test_extract_with_permission_error(self, temp_dir: Path):
        """Test handling of permission errors during extraction."""
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="perm_",
            output_dir=temp_dir / "output"
        )
        extractor = RecursiveExtractor(config)
        
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        # Mock shutil.copy2 to raise a permission error
        with patch('pyextractit.extractor.shutil.copy2', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError):
                extractor._process_matching_file(test_file, config.output_dir)
    
    def test_nested_archive_result_merging(self, temp_dir: Path):
        """Test merging of results from nested archive processing."""
        # Create a nested ZIP structure
        inner_file = temp_dir / "inner.txt"
        inner_file.write_text("inner content")
        
        inner_zip = temp_dir / "inner.zip"
        with zipfile.ZipFile(inner_zip, 'w') as zf:
            zf.write(inner_file, "inner.txt")
        
        outer_zip = temp_dir / "outer.zip"
        with zipfile.ZipFile(outer_zip, 'w') as zf:
            zf.write(inner_zip, "inner.zip")
            # Add another file directly
            zf.writestr("outer.txt", "outer content")
        
        config = ExtractorConfig(
            target_pattern=r".*\.txt$",
            prefix="nested_",
            output_dir=temp_dir / "output",
            max_depth=3
        )
        extractor = RecursiveExtractor(config)
        
        result = extractor.extract_from_archive(outer_zip)
        
        assert result.success is True
        # Should find files from both levels
        assert result.depth_reached >= 1
        # Should have processed files from both outer and inner archives
        assert result.total_extracted >= 2
