#!/usr/bin/env python3
"""Debug sanitize filename cases."""

import sys
from pathlib import Path

# Add the project to path
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))

from pyextractit import utils

def test_cases():
    test_cases = [
        "file<name>.txt",
        "file<n>ame.txt" 
    ]
    
    for case in test_cases:
        result = utils.sanitize_filename(case)
        print(f"Input: {repr(case)} -> Output: {repr(result)}")

if __name__ == "__main__":
    test_cases()
