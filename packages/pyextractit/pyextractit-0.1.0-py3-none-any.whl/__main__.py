"""Command-line interface for PyExtractIt."""

import sys
from pathlib import Path
from typing import Optional
import typer
from loguru import logger

from .extractor import RecursiveExtractor, ExtractorConfig
from .models import ExtractionResult

app = typer.Typer(
    name="pyextractit",
    help="A utility to recursively extract files from archives until finding target files."
)


@app.command()
def extract(
    archive_path: Path = typer.Argument(
        ...,
        help="Path to the archive file to extract from",
        exists=True,
        file_okay=True,
        dir_okay=False
    ),
    pattern: str = typer.Argument(
        ...,
        help="Regular expression pattern to match target filenames (filename only, not full path)"
    ),
    prefix: str = typer.Option(
        "extracted_",
        "--prefix", "-p",
        help="Prefix to add to matched files (files will be renamed as prefix_filename_sn1, prefix_filename_sn2, etc.)"
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory for extracted files (default: ./extracted)"
    ),
    max_depth: int = typer.Option(
        50,
        "--max-depth", "-d",
        help="Maximum depth for recursive archive extraction (target files extracted regardless of depth)",
        min=1,
        max=200
    ),
    preserve_structure: bool = typer.Option(
        False,
        "--preserve-structure",
        help="Preserve directory structure when extracting"
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing files"
    ),
    temp_dir: Optional[Path] = typer.Option(
        None,
        "--temp-dir",
        help="Custom temporary directory for extraction"
    ),
    unlimited_depth: bool = typer.Option(
        True,
        "--unlimited-depth/--limited-depth",
        help="Extract target files regardless of depth (default: True)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Enable verbose logging"
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet", "-q",
        help="Suppress all output except errors"
    )
):
    """
    Extract files recursively from archives until finding files matching the target pattern.
    
    The pattern matches FILENAME ONLY (not the full path). Files are extracted regardless 
    of how deeply nested they are in compressed archives and renamed with sequential numbering.
    
    Examples:
    
        # Extract all .txt files from archive.zip (renamed as data_filename_sn1.txt, data_filename_sn2.txt, etc.)
        pyextractit archive.zip ".*\\.txt$" --prefix "data_"
        
        # Extract files with specific naming pattern from deeply nested archives
        pyextractit nested.tar.gz "config.*\\.json$" --output ./configs
        
        # Extract CSV files preserving directory structure  
        pyextractit data.zip ".*\\.csv$" --preserve-structure
    """
    
    # Configure logging based on verbosity
    logger.remove()  # Remove default handler
    
    if not quiet:
        if verbose:
            logger.add(sys.stderr, level="DEBUG", format="{time} | {level} | {message}")
        else:
            logger.add(sys.stderr, level="INFO", format="{level} | {message}")
    else:
        logger.add(sys.stderr, level="ERROR", format="ERROR | {message}")
    
    # Create configuration
    try:
        config = ExtractorConfig(
            target_pattern=pattern,
            prefix=prefix,
            max_depth=max_depth,
            output_dir=output_dir,
            preserve_structure=preserve_structure,
            overwrite_existing=overwrite,
            temp_dir=temp_dir,
            unlimited_depth=unlimited_depth
        )
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        raise typer.Exit(1)
    
    # Create extractor and run extraction
    extractor = RecursiveExtractor(config)
    
    logger.info(f"Starting extraction from: {archive_path}")
    logger.info(f"Target pattern: {pattern}")
    logger.info(f"Max depth: {max_depth}")
    
    result = extractor.extract_from_archive(archive_path)
    
    # Display results
    if result.success:
        typer.echo(f"✅ Extraction completed successfully!")
        typer.echo(f"📁 Extracted to: {result.extraction_dir}")
        typer.echo(f"🎯 Found {len(result.matched_files)} matching files")
        typer.echo(f"📦 Total files extracted: {result.total_extracted}")
        typer.echo(f"🔍 Maximum depth reached: {result.depth_reached}")
        typer.echo(f"⏱️  Time taken: {result.extraction_time:.2f} seconds")
        
        if result.matched_files:
            typer.echo("\n📋 Matched files:")
            for match in result.matched_files:
                status = "📦 (archive)" if match.is_archive else "📄"
                typer.echo(f"  {status} {match.final_path.name}")
                
                # If matched file is also an archive, mention it
                if match.is_archive:
                    typer.echo(f"    ⚠️  This file is an archive and can be processed further")
        else:
            typer.echo("⚠️  No files matching the pattern were found")
            
    else:
        typer.echo(f"❌ Extraction failed: {result.error_message}", err=True)
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from . import __version__
    typer.echo(f"PyExtractIt version {__version__}")


@app.command()
def list_supported():
    """List supported archive formats."""
    from .extractor import RecursiveExtractor
    
    typer.echo("📦 Supported archive formats:")
    for ext in sorted(RecursiveExtractor.SUPPORTED_EXTENSIONS):
        typer.echo(f"  • {ext}")


if __name__ == "__main__":
    app()
