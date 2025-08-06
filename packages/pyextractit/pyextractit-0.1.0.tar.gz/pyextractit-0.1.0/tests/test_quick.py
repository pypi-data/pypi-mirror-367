#!/usr/bin/env python3
"""
Quick test script to verify PyExtractIt functionality.
Creates a simple test archive and extracts files from it.
"""

import tempfile
import zipfile
from pathlib import Path
import sys
import os

# Add the package to the path for testing
sys.path.insert(0, str(Path(__file__).parent))

try:
    from pyextractit import RecursiveExtractor, ExtractorConfig
    print("✅ Successfully imported PyExtractIt modules")
except ImportError as e:
    print(f"❌ Failed to import PyExtractIt: {e}")
    sys.exit(1)


def test_basic_functionality():
    """Test basic extraction functionality."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        test_files = {
            "config.json": '{"app": "test", "version": "1.0"}',
            "readme.txt": "This is a test readme file.",
            "data.csv": "name,value\ntest,123\n",
            "image.png": "fake png content"
        }
        
        # Create test archive
        archive_path = temp_path / "test.zip"
        with zipfile.ZipFile(archive_path, 'w') as zf:
            for filename, content in test_files.items():
                zf.writestr(filename, content)
        
        print(f"📦 Created test archive: {archive_path}")
        
        # Test configuration and extraction
        config = ExtractorConfig(
            target_pattern=r".*\.(json|txt)$",
            prefix="extracted_",
            max_depth=3,
            output_dir=temp_path / "output"
        )
        
        extractor = RecursiveExtractor(config)
        result = extractor.extract_from_archive(archive_path)
        
        # Check results
        if result.success:
            print("✅ Extraction completed successfully!")
            print(f"📁 Output directory: {result.extraction_dir}")
            print(f"🎯 Found {len(result.matched_files)} matching files")
            print(f"📦 Total files extracted: {result.total_extracted}")
            print(f"⏱️  Time taken: {result.extraction_time:.2f} seconds")
            
            # List extracted files
            output_files = list(result.extraction_dir.glob("extracted_*"))
            print(f"\n📋 Extracted files:")
            for file_path in output_files:
                print(f"  📄 {file_path.name} ({file_path.stat().st_size} bytes)")
            
            # Verify expected files exist
            expected_files = {"extracted_config.json", "extracted_readme.txt"}
            actual_files = {f.name for f in output_files}
            
            if expected_files.issubset(actual_files):
                print("✅ All expected files were extracted correctly!")
                return True
            else:
                missing = expected_files - actual_files
                print(f"❌ Missing expected files: {missing}")
                return False
        else:
            print(f"❌ Extraction failed: {result.error_message}")
            return False


def test_cli_import():
    """Test that CLI components can be imported."""
    try:
        from pyextractit.__main__ import app
        print("✅ CLI module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import CLI: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing PyExtractIt functionality...")
    print("=" * 50)
    
    # Test imports
    cli_test = test_cli_import()
    
    # Test basic functionality
    basic_test = test_basic_functionality()
    
    print("\n" + "=" * 50)
    if basic_test and cli_test:
        print("🎉 All tests passed! PyExtractIt is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
