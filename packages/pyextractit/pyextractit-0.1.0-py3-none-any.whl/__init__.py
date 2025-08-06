"""
PyExtractIt - A utility to recursively extract files from archives.

This package provides functionality to extract files from nested archives
(zip, tar, tar.gz) until finding files that match a target pattern,
then rename them with a specified prefix.
"""

__version__ = "0.1.0"
__author__ = "fxyzbtc"
__email__ = "fxyzbtc@gmail.com"

from .extractor import ExtractorConfig, RecursiveExtractor
from .models import ExtractionResult, FileMatch

__all__ = [
    "ExtractorConfig",
    "RecursiveExtractor", 
    "ExtractionResult",
    "FileMatch",
]
