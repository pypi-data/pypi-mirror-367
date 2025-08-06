#!/usr/bin/env python3
"""Debug sanitize filename."""

import sys
from pathlib import Path

# Add the project to path
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))

from pyextractit import utils

def test_sanitize():
    test_string = '<>:"/\\|?*'
    print(f"Input string: {repr(test_string)}")
    print(f"Length: {len(test_string)}")
    
    result = utils.sanitize_filename(test_string)
    print(f"Result: {repr(result)}")
    print(f"Result length: {len(result)}")
    
    print("Characters:")
    for i, char in enumerate(test_string):
        print(f"  {i+1}: {repr(char)}")

if __name__ == "__main__":
    test_sanitize()
