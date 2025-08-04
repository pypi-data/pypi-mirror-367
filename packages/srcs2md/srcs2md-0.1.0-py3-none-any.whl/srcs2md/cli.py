"""Command-line interface for srcs2md."""

from pathlib import Path
from typing import List, Optional, Tuple

import click

from .config import Config, PatternConfig
from .generator import MarkdownGenerator


def parse_pattern(
    ctx: click.Context, param: click.Parameter, value: Tuple[str, ...]
) -> List[PatternConfig]:
    """Parse pattern arguments in the format 'pattern;language'."""
    patterns = []
    for pattern_str in value:
        if ";" not in pattern_str:
            raise click.BadParameter(
                f"Pattern must be in format 'pattern;language', got: {pattern_str}"
            )

        pattern, language = pattern_str.split(";", 1)
        patterns.append(PatternConfig(pattern=pattern, language=language))

    return patterns


@click.command()
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file (default: srcs2md.yaml)",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    help="Output file path (default: stdout)",
)
@click.option(
    "-p",
    "--pattern",
    multiple=True,
    callback=parse_pattern,
    help="Add file pattern in format 'pattern;language' (can be used multiple times)",
)
@click.option(
    "--no-config",
    is_flag=True,
    help="Skip configuration file entirely, use only command-line options",
)
@click.option(
    "--init",
    is_flag=True,
    help="Create a default configuration file",
)
@click.version_option()
def main(
    config: Optional[Path],
    output: Optional[Path],
    pattern: List[PatternConfig],
    no_config: bool,
    init: bool,
) -> None:
    """Generate markdown from source files using glob patterns.

    This tool reads a configuration file that specifies glob patterns for source
    files and generates a single markdown file containing all the matched files
    formatted as code blocks.

    Examples:

        # Use configuration file
        srcs2md

        # Add patterns from command line
        srcs2md -p "src/**/*.py;python" -p "*.md;markdown"

        # Use only command line patterns (no config file)
        srcs2md -p "src/**/*.rs;rust" -o output.md

        # Skip config file even if it exists
        srcs2md --no-config -p "*.py;python"
    """
    if init:
        create_default_config()
        return

    # Handle no-config mode or patterns-only mode
    if no_config or (pattern and not config):
        if no_config and not pattern:
            click.echo("--no-config requires at least one -p/--pattern", err=True)
            raise click.Abort()
        cfg = Config()
        cfg.patterns = pattern
    else:
        # Determine config file path
        if config is None:
            config = Config.default_config_path()
            if not config.exists() and not pattern:
                click.echo(
                    "No configuration file found. Use --init to create a default one, "
                    "or use -p/--pattern to specify patterns directly.",
                    err=True,
                )
                raise click.Abort()

        if config and config.exists():
            try:
                cfg = Config.from_file(config)
            except Exception as e:
                click.echo(f"Error loading configuration: {e}", err=True)
                raise click.Abort() from e
        else:
            cfg = Config()

        # Add command line patterns to config patterns
        if pattern:
            cfg.patterns.extend(pattern)

    # Override output file if specified via command line
    if output:
        cfg.output.file = str(output)

    try:
        generator = MarkdownGenerator(cfg)
        output_path = Path(cfg.output.file) if cfg.output.file else None
        generator.generate_to_file(output_path)

        if output_path:
            click.echo(f"Generated markdown written to {output_path}", err=True)

    except Exception as e:
        click.echo(f"Error generating markdown: {e}", err=True)
        raise click.Abort() from e


def create_default_config() -> None:
    """Create a default configuration file."""
    default_config = """# srcs2md configuration file
# This file defines what source files to include in the generated markdown

# Optional header configuration
header:
  # Path to a file whose content will be included at the top (e.g., README.md)
  include_file: null
  # Custom header text (will be added after include_file if both are specified)
  custom_text: |
    ## Source codes

    This section contains source code files for LLM context.

# File patterns to include
patterns:
  - pattern: "src/**/*.py"
    language: python
    description: "Python source files"

  - pattern: "src/**/*.rs"
    language: rust
    description: "Rust source files"

  - pattern: "*.md"
    language: markdown
    description: "Documentation files"

# Files and patterns to ignore
ignore:
  - "**/__pycache__/**"
  - "**/.git/**"
  - "**/node_modules/**"
  - "**/*.pyc"
  - "**/target/**"
  - "**/.mypy_cache/**"
  - "**/.pytest_cache/**"
  - "**/.venv/**"
  - "**/venv/**"
  - ".gitignore"
  - "*.log"

# Output configuration
output:
  # If not specified, outputs to stdout
  file: null
  # Whether to include file paths in the output
  include_paths: true
  # Whether to sort files alphabetically
  sort_files: true
  # Whether to respect .gitignore patterns (default: true)
  respect_gitignore: true
"""

    config_path = Config.default_config_path()
    if config_path.exists():
        click.echo(f"Configuration file {config_path} already exists.", err=True)
        return

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(default_config)

    click.echo(f"Created default configuration file: {config_path}")


if __name__ == "__main__":
    main()
