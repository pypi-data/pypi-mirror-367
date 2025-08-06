"""Configuration and main extractor class for PyExtractIt."""

import re
import shutil
import tempfile
import time
import zipfile
import tarfile
from pathlib import Path
from typing import List, Optional, Set, Pattern, Union
from pydantic import BaseModel, Field, validator
from loguru import logger
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential

from .models import ExtractionResult, FileMatch


class ExtractorConfig(BaseModel):
    """Configuration for the recursive extractor."""
    
    target_pattern: str = Field(description="Regex pattern to match target filenames (filename only, not path)")
    prefix: str = Field(default="extracted_", description="Prefix to add to matched files")
    max_depth: int = Field(default=10, description="Maximum depth for recursive extraction (only for archive extraction)")
    output_dir: Optional[Path] = Field(default=None, description="Output directory for extracted files")
    preserve_structure: bool = Field(default=False, description="Whether to preserve directory structure")
    overwrite_existing: bool = Field(default=False, description="Whether to overwrite existing files")
    temp_dir: Optional[Path] = Field(default=None, description="Custom temporary directory")
    unlimited_depth: bool = Field(default=True, description="Extract target files regardless of depth")
    
    class Config:
        arbitrary_types_allowed = True
    
    @validator('target_pattern')
    def validate_pattern(cls, v):
        """Validate that the pattern is a valid regex."""
        try:
            re.compile(v)
            return v
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
    
    @validator('max_depth')
    def validate_max_depth(cls, v):
        """Validate max depth is reasonable."""
        if v < 1 or v > 50:
            raise ValueError("Max depth must be between 1 and 50")
        return v


class RecursiveExtractor:
    """Main class for recursively extracting files from archives."""
    
    SUPPORTED_EXTENSIONS = {'.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tar.xz'}
    
    def __init__(self, config: ExtractorConfig):
        self.config = config
        self.pattern = re.compile(config.target_pattern, re.IGNORECASE)
        self.processed_archives: Set[str] = set()
        self.current_depth = 0
        self.file_counter = 0  # For sequential numbering
        
        # Setup logging
        logger.add(
            "pyextractit.log",
            rotation="10 MB",
            retention="30 days",
            level="INFO"
        )
    
    def extract_from_archive(self, archive_path: Path) -> ExtractionResult:
        """
        Extract files from an archive recursively until finding target files.
        
        Args:
            archive_path: Path to the archive file to extract from
            
        Returns:
            ExtractionResult containing information about the extraction
        """
        start_time = time.time()
        
        if not archive_path.exists():
            return ExtractionResult(
                source_archive=archive_path,
                extraction_dir=Path(),
                extraction_time=0,
                success=False,
                error_message=f"Archive file does not exist: {archive_path}"
            )
        
        # Create output directory
        output_dir = self.config.output_dir or Path.cwd() / "extracted"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create temporary extraction directory
        temp_base = self.config.temp_dir or Path(tempfile.gettempdir())
        # Ensure the custom temp directory exists
        if self.config.temp_dir:
            temp_base.mkdir(parents=True, exist_ok=True)
        
        with tempfile.TemporaryDirectory(dir=temp_base, prefix="pyextractit_") as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                result = self._extract_recursive(
                    archive_path=archive_path,
                    temp_dir=temp_path,
                    output_dir=output_dir,
                    depth=0
                )
                
                result.extraction_time = time.time() - start_time
                logger.info(f"Extraction completed in {result.extraction_time:.2f} seconds")
                
                return result
                
            except Exception as e:
                logger.error(f"Extraction failed: {e}")
                return ExtractionResult(
                    source_archive=archive_path,
                    extraction_dir=output_dir,
                    extraction_time=time.time() - start_time,
                    success=False,
                    error_message=str(e)
                )
    
    def _extract_recursive(
        self, 
        archive_path: Path, 
        temp_dir: Path, 
        output_dir: Path, 
        depth: int
    ) -> ExtractionResult:
        """Recursively extract archives and find matching files."""
        
        # Only check depth limit for archive extraction, not for target file extraction
        if depth > self.config.max_depth and not self.config.unlimited_depth:
            logger.warning(f"Maximum depth {self.config.max_depth} reached for archive extraction")
            return ExtractionResult(
                source_archive=archive_path,
                extraction_dir=output_dir,
                depth_reached=depth,
                extraction_time=0.0
            )
        
        # Check if we've already processed this archive
        archive_key = f"{archive_path.name}_{archive_path.stat().st_size}"
        if archive_key in self.processed_archives:
            logger.info(f"Archive already processed: {archive_path.name}")
            return ExtractionResult(
                source_archive=archive_path,
                extraction_dir=output_dir,
                depth_reached=depth,
                extraction_time=0.0
            )
        
        self.processed_archives.add(archive_key)
        logger.info(f"Processing archive at depth {depth}: {archive_path.name}")
        
        # Extract the current archive
        current_extract_dir = temp_dir / f"depth_{depth}_{archive_path.stem}"
        current_extract_dir.mkdir(parents=True, exist_ok=True)
        
        extracted_files = self._extract_single_archive(archive_path, current_extract_dir)
        
        result = ExtractionResult(
            source_archive=archive_path,
            extraction_dir=output_dir,
            depth_reached=depth,
            total_extracted=len(extracted_files),
            extraction_time=0.0  # Will be set later
        )
        
        # Process extracted files
        nested_archives = []
        
        for file_path in tqdm(extracted_files, desc=f"Processing files at depth {depth}"):
            # Check if file matches target pattern (filename only, not full path)
            if self.pattern.search(file_path.name):
                match = self._process_matching_file(file_path, output_dir)
                result.matched_files.append(match)
                logger.info(f"Found matching file: {file_path.name}")
            
            # Check if file is an archive that needs further extraction
            if self._is_archive(file_path):
                nested_archives.append(file_path)
        
        # Process nested archives
        for nested_archive in nested_archives:
            # Check depth limit for nested archive processing when unlimited_depth is False
            if not self.config.unlimited_depth and depth >= self.config.max_depth:
                logger.warning(f"Skipping nested archive {nested_archive.name} due to depth limit")
                continue
                
            logger.info(f"Found nested archive: {nested_archive.name}")
            nested_result = self._extract_recursive(
                nested_archive, temp_dir, output_dir, depth + 1
            )
            
            # Merge results
            result.matched_files.extend(nested_result.matched_files)
            result.total_extracted += nested_result.total_extracted
            result.depth_reached = max(result.depth_reached, nested_result.depth_reached)
            
            if not nested_result.success:
                result.success = False
                result.error_message = nested_result.error_message
        
        return result
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _extract_single_archive(self, archive_path: Path, extract_dir: Path) -> List[Path]:
        """Extract a single archive file and return list of extracted files."""
        
        extracted_files = []
        
        try:
            archive_name_lower = archive_path.name.lower()
            
            if archive_path.suffix.lower() == '.zip':
                extracted_files = self._extract_zip(archive_path, extract_dir)
            elif (archive_name_lower.endswith('.tar') or 
                  archive_name_lower.endswith('.tar.gz') or 
                  archive_name_lower.endswith('.tgz') or 
                  archive_name_lower.endswith('.tar.bz2') or 
                  archive_name_lower.endswith('.tar.xz')):
                extracted_files = self._extract_tar(archive_path, extract_dir)
            else:
                logger.warning(f"Unsupported archive format: {archive_path.name}")
                
        except Exception as e:
            logger.error(f"Failed to extract {archive_path.name}: {e}")
            raise
        
        return extracted_files
    
    def _extract_zip(self, zip_path: Path, extract_dir: Path) -> List[Path]:
        """Extract a ZIP file."""
        extracted_files = []
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get list of files to extract
            file_list = zip_ref.namelist()
            
            for file_info in tqdm(file_list, desc=f"Extracting {zip_path.name}"):
                try:
                    zip_ref.extract(file_info, extract_dir)
                    extracted_path = extract_dir / file_info
                    
                    if extracted_path.is_file():
                        extracted_files.append(extracted_path)
                        
                except Exception as e:
                    logger.warning(f"Failed to extract {file_info}: {e}")
        
        return extracted_files
    
    def _extract_tar(self, tar_path: Path, extract_dir: Path) -> List[Path]:
        """Extract a TAR file (including compressed variants)."""
        extracted_files = []
        
        # Determine the correct mode for opening based on filename
        tar_name_lower = tar_path.name.lower()
        
        if tar_name_lower.endswith('.tar'):
            mode = 'r'
        elif tar_name_lower.endswith('.tar.gz') or tar_name_lower.endswith('.tgz'):
            mode = 'r:gz'
        elif tar_name_lower.endswith('.tar.bz2'):
            mode = 'r:bz2'
        elif tar_name_lower.endswith('.tar.xz'):
            mode = 'r:xz'
        else:
            mode = 'r'
        
        with tarfile.open(tar_path, mode) as tar_ref:
            # Get list of members to extract
            members = tar_ref.getmembers()
            
            for member in tqdm(members, desc=f"Extracting {tar_path.name}"):
                if member.isfile():
                    try:
                        tar_ref.extract(member, extract_dir)
                        extracted_path = extract_dir / member.name
                        extracted_files.append(extracted_path)
                        
                    except Exception as e:
                        logger.warning(f"Failed to extract {member.name}: {e}")
        
        return extracted_files
    
    def _is_archive(self, file_path: Path) -> bool:
        """Check if a file is a supported archive format."""
        return any(
            str(file_path).lower().endswith(ext.lower()) 
            for ext in self.SUPPORTED_EXTENSIONS
        )
    
    def _process_matching_file(self, file_path: Path, output_dir: Path) -> FileMatch:
        """Process a file that matches the target pattern."""
        
        # Increment counter for sequential numbering
        self.file_counter += 1
        
        # Generate the final filename with prefix and sequential number
        file_stem = file_path.stem
        file_suffix = file_path.suffix
        final_filename = f"{self.config.prefix}{file_stem}_sn{self.file_counter}{file_suffix}"
        final_path = output_dir / final_filename
        
        # If overwrite is disabled, find a unique filename
        counter = 1
        while final_path.exists() and not self.config.overwrite_existing:
            final_filename = f"{self.config.prefix}{file_stem}_sn{self.file_counter}_{counter}{file_suffix}"
            final_path = output_dir / final_filename
            counter += 1
        
        # Copy the file to the final location
        try:
            if self.config.preserve_structure:
                # Preserve the directory structure relative to the extraction root
                # For structure preservation, we need the relative path from the temp extraction root
                # This is handled by the caller, so for now we just use the final filename
                final_path = output_dir / final_filename
                final_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(file_path, final_path)
            logger.info(f"Copied {file_path.name} to {final_path}")
            
            # Check if the matched file is also an archive
            is_archive = self._is_archive(file_path)
            
            return FileMatch(
                original_path=file_path,
                extracted_path=file_path,
                final_path=final_path,
                size=file_path.stat().st_size,
                is_archive=is_archive
            )
            
        except Exception as e:
            logger.error(f"Failed to copy {file_path.name}: {e}")
            raise
