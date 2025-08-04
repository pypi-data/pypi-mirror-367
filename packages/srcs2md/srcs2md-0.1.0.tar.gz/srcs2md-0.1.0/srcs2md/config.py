"""Configuration handling for srcs2md."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class PatternConfig:
    """Configuration for a file pattern."""

    pattern: str
    language: str
    description: Optional[str] = None


@dataclass
class HeaderConfig:
    """Configuration for the header section."""

    include_file: Optional[str] = None
    custom_text: Optional[str] = None


@dataclass
class OutputConfig:
    """Configuration for output formatting."""

    file: Optional[str] = None
    include_paths: bool = True
    sort_files: bool = True
    respect_gitignore: bool = True


@dataclass
class Config:
    """Main configuration class."""

    header: HeaderConfig = field(default_factory=HeaderConfig)
    patterns: List[PatternConfig] = field(default_factory=list)
    ignore: List[str] = field(default_factory=list)
    output: OutputConfig = field(default_factory=OutputConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create Config from dictionary."""
        header_data = data.get("header", {})
        header = HeaderConfig(
            include_file=header_data.get("include_file"),
            custom_text=header_data.get("custom_text"),
        )

        patterns_data = data.get("patterns", [])
        patterns = [
            PatternConfig(
                pattern=p["pattern"],
                language=p["language"],
                description=p.get("description"),
            )
            for p in patterns_data
        ]

        output_data = data.get("output", {})
        output = OutputConfig(
            file=output_data.get("file"),
            include_paths=output_data.get("include_paths", True),
            sort_files=output_data.get("sort_files", True),
            respect_gitignore=output_data.get("respect_gitignore", True),
        )

        return cls(
            header=header,
            patterns=patterns,
            ignore=data.get("ignore", []),
            output=output,
        )

    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from YAML file."""
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    @classmethod
    def default_config_path(cls) -> Path:
        """Return the default configuration file path."""
        return Path("srcs2md.yaml")
