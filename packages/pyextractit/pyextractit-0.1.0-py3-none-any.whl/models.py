"""Data models for PyExtractIt."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class FileMatch(BaseModel):
    """Represents a matched file found during extraction."""
    
    original_path: Path = Field(description="Original path of the file in the archive")
    extracted_path: Path = Field(description="Path where the file was extracted")
    final_path: Optional[Path] = Field(default=None, description="Final path after renaming")
    size: int = Field(description="File size in bytes")
    is_archive: bool = Field(default=False, description="Whether this file is also an archive")
    
    @field_validator('size')
    @classmethod
    def validate_size(cls, v):
        """Validate that file size is non-negative."""
        if v < 0:
            raise ValueError("File size cannot be negative")
        return v
    
    class Config:
        arbitrary_types_allowed = True


class ExtractionResult(BaseModel):
    """Result of the extraction process."""
    
    source_archive: Path = Field(description="The original archive file")
    extraction_dir: Path = Field(description="Directory where files were extracted")
    matched_files: List[FileMatch] = Field(default_factory=list, description="Files that matched the pattern")
    total_extracted: int = Field(default=0, description="Total number of files extracted")
    depth_reached: int = Field(default=0, description="Maximum depth of nested archives processed")
    extraction_time: float = Field(description="Time taken for extraction in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the extraction was performed")
    success: bool = Field(default=True, description="Whether the extraction was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if extraction failed")
    
    class Config:
        arbitrary_types_allowed = True
