"""Tests for PyExtractIt utility functions."""

import pytest
from pathlib import Path

from pyextractit.utils import (
    calculate_file_hash,
    get_file_type,
    sanitize_filename,
    find_files_by_pattern,
    get_human_readable_size
)


class TestCalculateFileHash:
    """Test cases for calculate_file_hash function."""
    
    def test_sha256_hash(self, temp_dir: Path):
        """Test SHA256 hash calculation."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!", encoding='utf-8')
        
        hash_value = calculate_file_hash(test_file, "sha256")
        
        # Known SHA256 hash for "Hello, World!"
        expected = "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
        assert hash_value == expected
    
    def test_md5_hash(self, temp_dir: Path):
        """Test MD5 hash calculation."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!", encoding='utf-8')
        
        hash_value = calculate_file_hash(test_file, "md5")
        
        # Known MD5 hash for "Hello, World!"
        expected = "65a8e27d8879283831b664bd8b7f0ad4"
        assert hash_value == expected
    
    def test_empty_file_hash(self, temp_dir: Path):
        """Test hash of empty file."""
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("", encoding='utf-8')
        
        hash_value = calculate_file_hash(empty_file, "sha256")
        
        # SHA256 hash of empty string
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert hash_value == expected
    
    def test_binary_file_hash(self, temp_dir: Path):
        """Test hash of binary file."""
        binary_file = temp_dir / "binary.bin"
        binary_file.write_bytes(b'\x00\x01\x02\x03\xff')
        
        hash_value = calculate_file_hash(binary_file, "sha256")
        
        # This should not raise an error and should produce a valid hash
        assert len(hash_value) == 64  # SHA256 produces 64 character hex string
        assert all(c in '0123456789abcdef' for c in hash_value)


class TestGetFileType:
    """Test cases for get_file_type function."""
    
    def test_text_file_type(self, temp_dir: Path):
        """Test MIME type detection for text files."""
        text_file = temp_dir / "test.txt"
        text_file.write_text("test content")
        
        mime_type = get_file_type(text_file)
        
        assert mime_type == "text/plain"
    
    def test_json_file_type(self, temp_dir: Path):
        """Test MIME type detection for JSON files."""
        json_file = temp_dir / "test.json"
        json_file.write_text('{"key": "value"}')
        
        mime_type = get_file_type(json_file)
        
        assert mime_type == "application/json"
    
    def test_unknown_file_type(self, temp_dir: Path):
        """Test MIME type detection for unknown file types."""
        unknown_file = temp_dir / "test.unknownext"
        unknown_file.write_text("some content")
        
        mime_type = get_file_type(unknown_file)
        
        assert mime_type is None
    
    def test_zip_file_type(self, temp_dir: Path):
        """Test MIME type detection for ZIP files."""
        zip_file = temp_dir / "test.zip"
        zip_file.write_bytes(b"fake zip content")
        
        mime_type = get_file_type(zip_file)
        
        # ZIP MIME type can vary between systems
        assert mime_type in ["application/zip", "application/x-zip-compressed"]


class TestSanitizeFilename:
    """Test cases for sanitize_filename function."""
    
    def test_safe_filename(self):
        """Test that safe filenames are unchanged."""
        safe_name = "normal_file_name.txt"
        result = sanitize_filename(safe_name)
        assert result == safe_name
    
    def test_unsafe_characters(self):
        """Test removal of unsafe characters."""
        unsafe_name = 'file<>:"/\\|?*name.txt'
        result = sanitize_filename(unsafe_name)
        expected = "file_________name.txt"
        assert result == expected
    
    def test_leading_trailing_spaces_dots(self):
        """Test removal of leading/trailing spaces and dots."""
        test_cases = [
            ("  filename.txt  ", "filename.txt"),
            ("..filename.txt..", "filename.txt"),
            (". .filename.txt. .", "filename.txt"),
        ]
        
        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            assert result == expected
    
    def test_empty_filename(self):
        """Test handling of empty filename."""
        result = sanitize_filename("")
        assert result == "unnamed_file"
        
        result = sanitize_filename("   ")
        assert result == "unnamed_file"
        
        result = sanitize_filename("...")
        assert result == "unnamed_file"


class TestFindFilesByPattern:
    """Test cases for find_files_by_pattern function."""
    
    def test_find_text_files(self, temp_dir: Path):
        """Test finding files by pattern."""
        # Create some files
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.txt").write_text("content2")
        (temp_dir / "file3.py").write_text("content3")
        
        # Create subdirectory with more files
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "file4.txt").write_text("content4")
        
        # Find all .txt files
        txt_files = find_files_by_pattern(temp_dir, "*.txt")
        
        assert len(txt_files) == 3
        txt_names = {f.name for f in txt_files}
        assert txt_names == {"file1.txt", "file2.txt", "file4.txt"}
    
    def test_find_no_matches(self, temp_dir: Path):
        """Test finding files with no matches."""
        (temp_dir / "file1.txt").write_text("content1")
        
        # Look for files that don't exist
        py_files = find_files_by_pattern(temp_dir, "*.py")
        
        assert len(py_files) == 0
    
    def test_complex_pattern(self, temp_dir: Path):
        """Test finding files with complex patterns."""
        # Create files with various names
        files_to_create = [
            "config_dev.json",
            "config_prod.json",
            "settings.json",
            "data.txt",
            "config_test.xml"
        ]
        
        for filename in files_to_create:
            (temp_dir / filename).write_text("content")
        
        # Find config_*.json files
        config_files = find_files_by_pattern(temp_dir, "config_*.json")
        
        assert len(config_files) == 2
        config_names = {f.name for f in config_files}
        assert config_names == {"config_dev.json", "config_prod.json"}


class TestGetHumanReadableSize:
    """Test cases for get_human_readable_size function."""
    
    def test_bytes(self):
        """Test byte size formatting."""
        assert get_human_readable_size(512) == "512.0 B"
        assert get_human_readable_size(0) == "0.0 B"
        assert get_human_readable_size(1) == "1.0 B"
    
    def test_kilobytes(self):
        """Test kilobyte size formatting."""
        assert get_human_readable_size(1024) == "1.0 KB"
        assert get_human_readable_size(1536) == "1.5 KB"  # 1.5 * 1024
        assert get_human_readable_size(2048) == "2.0 KB"
    
    def test_megabytes(self):
        """Test megabyte size formatting."""
        assert get_human_readable_size(1024 * 1024) == "1.0 MB"
        assert get_human_readable_size(int(1.5 * 1024 * 1024)) == "1.5 MB"
    
    def test_gigabytes(self):
        """Test gigabyte size formatting."""
        assert get_human_readable_size(1024 * 1024 * 1024) == "1.0 GB"
        assert get_human_readable_size(int(2.5 * 1024 * 1024 * 1024)) == "2.5 GB"
    
    def test_terabytes(self):
        """Test terabyte size formatting."""
        tb_size = 1024 * 1024 * 1024 * 1024
        assert get_human_readable_size(tb_size) == "1.0 TB"
    
    def test_petabytes(self):
        """Test petabyte size formatting."""
        pb_size = 1024 * 1024 * 1024 * 1024 * 1024
        assert get_human_readable_size(pb_size) == "1.0 PB"
