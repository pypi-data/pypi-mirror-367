# PyExtractIt

A utility to recursively extract from deeply nested compressed archives until finding files matching the target filename pattern (regexp). Files are renamed with sequential numbering (prefix_filename_sn1, prefix_filename_sn2, etc.). This is especially useful when your target data is buried deep within multiple layers of compressed archives.

## Features

- 🔄 **Deep recursive extraction**: Automatically extracts nested archives regardless of depth to find target files
- 🎯 **Filename pattern matching**: Uses regular expressions to match filenames (not paths) 
- 📦 **Multiple formats**: Supports ZIP, TAR, TAR.GZ, TAR.BZ2, TAR.XZ formats
- 🏷️ **Sequential file renaming**: Renames matched files with customizable prefix and sequential numbering (prefix_filename_sn1, prefix_filename_sn2, etc.)
- 🌊 **Unlimited depth**: Extracts target files no matter how deeply nested in compressed archives
- 📁 **Structure preservation**: Option to maintain directory structure
- ⚡ **Performance**: Efficient extraction with progress indicators
- 🛡️ **Error handling**: Robust error handling and logging

## Installation

```bash
# Install from PyPI (when published)
pip install pyextractit

# Install from source
git clone https://github.com/fxyzbtc/pyextractit.git
cd pyextractit
pip install -e .
```

## Quick Start

### Command Line Usage

```bash
# Extract all .txt files from an archive (renamed as extracted_filename_sn1.txt, extracted_filename_sn2.txt, etc.)
pyextractit archive.zip ".*\.txt$" --prefix "extracted_"

# Extract config files with specific naming pattern from deeply nested archives
pyextractit nested.tar.gz "config.*\.json$" --output ./configs

# Preserve directory structure during extraction
pyextractit data.zip ".*\.csv$" --preserve-structure

# Limit archive extraction depth (but target files are still extracted regardless of depth)
pyextractit deep.zip ".*\.log$" --max-depth 3

# Disable unlimited depth for target files (apply depth limit to target extraction too)
pyextractit archive.tar.gz ".*\.txt$" --limited-depth --max-depth 5

# Overwrite existing files
pyextractit archive.tar.gz ".*\.txt$" --overwrite

# Verbose output
pyextractit archive.zip ".*\.txt$" --verbose
```

### Python API Usage

```python
from pyextractit import RecursiveExtractor, ExtractorConfig
from pathlib import Path

# Create configuration
config = ExtractorConfig(
    target_pattern=r".*\.txt$",  # Matches filename only, not full path
    prefix="extracted_",
    max_depth=50,  # For archive extraction depth
    output_dir=Path("./output"),
    preserve_structure=False,
    overwrite_existing=False,
    unlimited_depth=True  # Extract target files regardless of depth
)

# Create extractor and run
extractor = RecursiveExtractor(config)
result = extractor.extract_from_archive(Path("archive.zip"))

# Check results
if result.success:
    print(f"Found {len(result.matched_files)} matching files")
    for match in result.matched_files:
        print(f"Extracted: {match.final_path}")  # e.g., extracted_config_sn1.txt, extracted_data_sn2.csv
else:
    print(f"Extraction failed: {result.error_message}")
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `target_pattern` | str | - | Regular expression pattern to match target filenames (not full paths) |
| `prefix` | str | `"extracted_"` | Prefix to add to matched files (files renamed as prefix_filename_sn1, prefix_filename_sn2, etc.) |
| `max_depth` | int | `50` | Maximum depth for recursive archive extraction (1-200) |
| `output_dir` | Path | `None` | Output directory (default: `./extracted`) |
| `preserve_structure` | bool | `False` | Preserve directory structure |
| `overwrite_existing` | bool | `False` | Overwrite existing files |
| `temp_dir` | Path | `None` | Custom temporary directory |
| `unlimited_depth` | bool | `True` | Extract target files regardless of depth |

## Supported Archive Formats

- `.zip` - ZIP archives
- `.tar` - TAR archives  
- `.tar.gz`, `.tgz` - Gzip-compressed TAR archives
- `.tar.bz2` - Bzip2-compressed TAR archives
- `.tar.xz` - XZ-compressed TAR archives

## Common Use Cases

### 1. Extract Configuration Files

```bash
# Find all config files in nested archives (renamed as backup_config_sn1.json, backup_config_sn2.yaml, etc.)
pyextractit app-backup.zip "config.*\.(json|yaml|yml)$" --prefix "backup_"
```

### 2. Data Mining from Deep Archives

```bash
# Extract CSV data files from deeply nested structure (unlimited depth)
pyextractit dataset.tar.gz ".*\.csv$" --max-depth 10 --preserve-structure
```

### 3. Log File Extraction

```bash
# Extract log files with date pattern (renamed as extracted_app_2024_sn1.log, extracted_system_2024_sn2.log, etc.)
pyextractit logs.zip ".*_2024.*\.log$" --output ./logs --overwrite
```

### 4. Backup File Recovery

```bash
# Find and extract specific backup files (renamed as recovered_backup_db_sn1.sql, recovered_backup_logs_sn2.sql, etc.)
pyextractit backup.tar.gz "backup_.*\.sql$" --prefix "recovered_"
```

## Exit Codes

- `0`: Success
- `1`: Error (configuration error, extraction failure, etc.)

## Logging

PyExtractIt uses structured logging with the following levels:

- **ERROR**: Critical errors that cause extraction to fail
- **WARNING**: Non-critical issues (corrupted files, permission errors)
- **INFO**: General extraction progress and results
- **DEBUG**: Detailed extraction process information

Logs are written to:
- Console (configurable verbosity)
- `pyextractit.log` file (rotated, 30 days retention)

## Examples

### Complex Nested Structure

```
archive.zip
├── data/
│   ├── config.json ✓ (matches pattern)
│   └── nested.zip
│       ├── inner_config.json ✓ (matches pattern)
│       └── deeper.tar.gz
│           └── deep_config.json ✓ (matches pattern)
└── README.txt
```

```bash
pyextractit archive.zip ".*config\.json$" --prefix "found_"
```

**Result:**
```
./extracted/
├── found_config_sn1.json
├── found_inner_config_sn2.json
└── found_deep_config_sn3.json
```

### Archive Detection

If matched files are themselves archives, PyExtractIt will indicate this:

```bash
pyextractit outer.zip "backup_.*\.zip$" --verbose
```

**Output:**
```
✅ Extraction completed successfully!
📁 Extracted to: ./extracted
🎯 Found 2 matching files
📦 Total files extracted: 15
🔍 Maximum depth reached: 2
⏱️  Time taken: 1.34 seconds

📋 Matched files:
  📦 found_backup_2024_sn1.zip (archive)
    ⚠️  This file is an archive and can be processed further
  📦 found_backup_legacy_sn2.zip (archive)
    ⚠️  This file is an archive and can be processed further
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/fxyzbtc/pyextractit.git
cd pyextractit
pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests with coverage
pytest --cov=pyextractit --cov-report=html

# Run specific test file
pytest tests/test_extractor.py -v

# Run with verbose output
pytest -v -s
```

### Code Quality

```bash
# Format code
ruff format pyextractit tests

# Lint code
ruff check pyextractit tests

# Type checking (if mypy is installed)
mypy pyextractit
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v0.1.0 (2024-08-05)
- Initial release
- Recursive archive extraction
- Pattern-based file matching
- Multiple archive format support
- Command-line interface
- Python API
- Comprehensive test suite

## Links

- **Homepage**: https://github.com/fxyzbtc/pyextractit
- **Documentation**: https://deepwiki.com/fxyzbtc/pyextractit
- **Issues**: https://github.com/fxyzbtc/pyextractit/issues
- **PyPI**: https://pypi.org/project/pyextractit/ (when published)

## Support

If you encounter any issues or have questions:

1. Check the [documentation](https://deepwiki.com/fxyzbtc/pyextractit)
2. Search [existing issues](https://github.com/fxyzbtc/pyextractit/issues)
3. Create a [new issue](https://github.com/fxyzbtc/pyextractit/issues/new) with:
   - Python version
   - Archive type and structure
   - Command used
   - Error messages
   - Expected vs actual behavior

This repository serves as a template for creating new Python projects. It provides a basic structure and configuration to get started quickly.

## Purpose

This template aims to streamline the setup process for new Python projects by providing a standardized layout, dependency management configuration, and basic example files. It helps avoid the repetitive setup tasks involved in starting a new project.

## Using the Template
0.  **Fine-tune**
    *   Review the copilot instructions if you also use microsoft copilot
    *   The instruction is extreme personal favor
1.  **Clone or Copy:**
    *   Use this repository as a template on GitHub (click "Use this template").
    *   Alternatively, clone or download the repository and manually copy the files to your new project directory.
2.  **Rename Project:**
    *   Rename the `pyprojectname` directory to your actual project's name.
    *   Update the project name in `pyproject.toml`.
3.  **Install Dependencies:**
    ```bash
    uv pip install -e .[dev]
    ```
4.  **Start Developing:** Begin adding your project's code and tests.

## Development Guide (Using This Template)

*   **Dependencies:** Manage dependencies using `uv` and `pyproject.toml`. Add runtime dependencies under `[project.dependencies]` and development dependencies under `[project.optional-dependencies]`.
*   **Structure:** Place your library code within the main project directory (e.g., `your_project_name/`). Write tests in the `tests/` directory.
*   **Entry Points:** Configure command-line scripts or module execution (`python -m your_project_name`) in `pyproject.toml` under `[project.scripts]` or `[project.entry-points."console_scripts"]`.
*   **Testing:** Run tests using `pytest`. Ensure good test coverage.
*   **Linting/Formatting:** Use `ruff` or `black` to maintain code style.

## Links

*   **Homepage:** [https://github.com/fxyzbtc/mypytemplate]
*   **Wiki:** [https://deepwiki.com/fxyzbtc/mypytemplate]
*   **Issues:** [Link to GitHub Issues Page]
