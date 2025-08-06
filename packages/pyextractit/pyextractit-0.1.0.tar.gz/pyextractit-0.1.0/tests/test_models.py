"""Tests for PyExtractIt models."""

import pytest
from datetime import datetime
from pathlib import Path

from pyextractit.models import FileMatch, ExtractionResult


class TestFileMatch:
    """Test cases for FileMatch model."""
    
    def test_file_match_creation(self, temp_dir: Path):
        """Test creating a FileMatch instance."""
        original_path = temp_dir / "original.txt"
        extracted_path = temp_dir / "extracted.txt"
        final_path = temp_dir / "final.txt"
        
        # Create the files
        original_path.write_text("test content")
        extracted_path.write_text("test content")
        final_path.write_text("test content")
        
        match = FileMatch(
            original_path=original_path,
            extracted_path=extracted_path,
            final_path=final_path,
            size=12,
            is_archive=False
        )
        
        assert match.original_path == original_path
        assert match.extracted_path == extracted_path
        assert match.final_path == final_path
        assert match.size == 12
        assert match.is_archive is False
    
    def test_file_match_with_archive(self, temp_dir: Path):
        """Test FileMatch for an archive file."""
        archive_path = temp_dir / "archive.zip"
        archive_path.write_bytes(b"fake zip content")
        
        match = FileMatch(
            original_path=archive_path,
            extracted_path=archive_path,
            size=16,
            is_archive=True
        )
        
        assert match.is_archive is True
        assert match.final_path is None  # Optional field
    
    def test_file_match_validation(self):
        """Test FileMatch field validation."""
        with pytest.raises(ValueError):
            # Size cannot be negative
            FileMatch(
                original_path=Path("test.txt"),
                extracted_path=Path("test.txt"),
                size=-1
            )


class TestExtractionResult:
    """Test cases for ExtractionResult model."""
    
    def test_extraction_result_creation(self, temp_dir: Path):
        """Test creating an ExtractionResult instance."""
        source_archive = temp_dir / "source.zip"
        extraction_dir = temp_dir / "extracted"
        
        result = ExtractionResult(
            source_archive=source_archive,
            extraction_dir=extraction_dir,
            extraction_time=1.5
        )
        
        assert result.source_archive == source_archive
        assert result.extraction_dir == extraction_dir
        assert result.extraction_time == 1.5
        assert result.success is True  # Default value
        assert result.total_extracted == 0  # Default value
        assert result.depth_reached == 0  # Default value
        assert isinstance(result.timestamp, datetime)
        assert len(result.matched_files) == 0  # Default empty list
    
    def test_extraction_result_with_matches(self, temp_dir: Path):
        """Test ExtractionResult with file matches."""
        source_archive = temp_dir / "source.zip"
        extraction_dir = temp_dir / "extracted"
        
        # Create some file matches
        match1 = FileMatch(
            original_path=temp_dir / "file1.txt",
            extracted_path=temp_dir / "file1.txt",
            size=100
        )
        match2 = FileMatch(
            original_path=temp_dir / "file2.txt",
            extracted_path=temp_dir / "file2.txt",
            size=200
        )
        
        result = ExtractionResult(
            source_archive=source_archive,
            extraction_dir=extraction_dir,
            matched_files=[match1, match2],
            total_extracted=5,
            depth_reached=2,
            extraction_time=2.5
        )
        
        assert len(result.matched_files) == 2
        assert result.total_extracted == 5
        assert result.depth_reached == 2
        assert result.extraction_time == 2.5
    
    def test_extraction_result_failure(self, temp_dir: Path):
        """Test ExtractionResult for failed extraction."""
        source_archive = temp_dir / "source.zip"
        extraction_dir = temp_dir / "extracted"
        
        result = ExtractionResult(
            source_archive=source_archive,
            extraction_dir=extraction_dir,
            extraction_time=0.1,
            success=False,
            error_message="Archive corrupted"
        )
        
        assert result.success is False
        assert result.error_message == "Archive corrupted"
    
    def test_extraction_result_timestamp_auto(self, temp_dir: Path):
        """Test that timestamp is automatically set."""
        before = datetime.now()
        
        result = ExtractionResult(
            source_archive=temp_dir / "source.zip",
            extraction_dir=temp_dir / "extracted",
            extraction_time=1.0
        )
        
        after = datetime.now()
        
        assert before <= result.timestamp <= after
