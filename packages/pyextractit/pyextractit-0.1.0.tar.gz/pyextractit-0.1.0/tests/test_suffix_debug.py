#!/usr/bin/env python3
"""Debug tar.gz extraction with suffix check."""

import tempfile
import tarfile
from pathlib import Path
import sys

# Add the project to path
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))

from pyextractit.extractor import ExtractorConfig, RecursiveExtractor

def test_suffix_detection():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample files
        files = {}
        files['config'] = temp_path / "config.json"
        files['config'].write_text('{"setting": "value"}', encoding='utf-8')
        
        # Create TAR.GZ file
        tar_gz_path = temp_path / "test.tar.gz"
        with tarfile.open(tar_gz_path, 'w:gz') as tar_file:
            for file_path in files.values():
                tar_file.add(file_path, arcname=file_path.name)
        
        print(f"File path: {tar_gz_path}")
        print(f"Suffix: {tar_gz_path.suffix}")
        print(f"Suffixes: {tar_gz_path.suffixes}")
        print(f"Name: {tar_gz_path.name}")
        
        # Check if it matches the condition
        if tar_gz_path.suffix.lower() in {'.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tar.xz'}:
            print("Matches tar condition")
        else:
            print("Does NOT match tar condition")
        
        # Check if it's detected as archive
        config = ExtractorConfig(target_pattern=r".*\.json$", prefix="test_")
        extractor = RecursiveExtractor(config)
        
        is_archive = extractor._is_archive(tar_gz_path)
        print(f"Detected as archive: {is_archive}")

if __name__ == "__main__":
    test_suffix_detection()
