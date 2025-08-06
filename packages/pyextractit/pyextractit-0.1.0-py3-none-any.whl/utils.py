"""Utility functions for PyExtractIt."""

import hashlib
import mimetypes
from pathlib import Path
from typing import List, Optional


def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """
    Calculate hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (sha256, md5, etc.)
        
    Returns:
        Hexadecimal hash string
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def get_file_type(file_path: Path) -> Optional[str]:
    """
    Get MIME type of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME type string or None if unknown
    """
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for filesystem.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Replace problematic characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure it's not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename


def find_files_by_pattern(directory: Path, pattern: str) -> List[Path]:
    """
    Find files in a directory matching a pattern.
    
    Args:
        directory: Directory to search in
        pattern: Glob pattern to match
        
    Returns:
        List of matching file paths
    """
    return list(directory.rglob(pattern))


def get_human_readable_size(size_bytes: int) -> str:
    """
    Convert bytes to human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human readable size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
