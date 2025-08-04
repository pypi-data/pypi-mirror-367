"""Core markdown generation functionality."""

import glob
from pathlib import Path
from typing import List, Optional

from .config import Config


class MarkdownGenerator:
    """Generates markdown from source files based on configuration."""

    def __init__(self, config: Config) -> None:
        """Initialize with configuration."""
        self.config = config

    def generate_header(self) -> str:
        """Generate the header section."""
        parts = []

        if self.config.header.include_file:
            include_path = Path(self.config.header.include_file)
            if include_path.exists():
                with open(include_path, encoding="utf-8") as f:
                    parts.append(f.read().rstrip())

        if self.config.header.custom_text:
            parts.append(self.config.header.custom_text.rstrip())

        if parts:
            return "\n\n".join(parts) + "\n\n"
        return ""

    def format_file_content(self, file_path: Path, language: str) -> str:
        """Format a single file as markdown."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError):
            return f"### file: {file_path}\n\n*Could not read file*\n\n"

        if self.config.output.include_paths:
            header = f"### file: {file_path}\n\n"
        else:
            header = ""

        return f"{header}```{language}\n{content}\n```\n\n"

    def load_gitignore_patterns(self) -> List[str]:
        """Load patterns from .gitignore file if it exists."""
        gitignore_path = Path(".gitignore")
        if not gitignore_path.exists():
            return []

        patterns = []
        try:
            with open(gitignore_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith("#"):
                        # Convert gitignore patterns to glob patterns
                        if line.endswith("/"):
                            # Directory patterns
                            patterns.append(f"**/{line}**")
                            patterns.append(f"{line}**")
                        elif "/" not in line:
                            # File patterns that should match anywhere
                            patterns.append(f"**/{line}")
                        else:
                            # Path patterns
                            patterns.append(line)
        except (OSError, UnicodeDecodeError):
            # If we can't read .gitignore, just skip it
            pass

        return patterns

    def should_ignore_file(self, file_path: Path) -> bool:
        """Check if a file should be ignored based on ignore patterns."""
        file_str = str(file_path)

        # Check configured ignore patterns
        for ignore_pattern in self.config.ignore:
            if glob.fnmatch.fnmatch(file_str, ignore_pattern):
                return True

        # Check .gitignore patterns if enabled
        if self.config.output.respect_gitignore:
            gitignore_patterns = self.load_gitignore_patterns()
            for pattern in gitignore_patterns:
                if glob.fnmatch.fnmatch(file_str, pattern):
                    return True

        return False

    def collect_files(self) -> List[tuple[Path, str]]:
        """Collect all files matching the configured patterns."""
        files = []

        for pattern_config in self.config.patterns:
            matched_files = glob.glob(pattern_config.pattern, recursive=True)
            for file_path_str in matched_files:
                file_path = Path(file_path_str)
                if file_path.is_file() and not self.should_ignore_file(file_path):
                    files.append((file_path, pattern_config.language))

        if self.config.output.sort_files:
            files.sort(key=lambda x: str(x[0]))

        return files

    def generate(self) -> str:
        """Generate the complete markdown output."""
        output_parts = []

        header = self.generate_header()
        if header:
            output_parts.append(header)

        files = self.collect_files()
        for file_path, language in files:
            file_content = self.format_file_content(file_path, language)
            output_parts.append(file_content)

        return "".join(output_parts)

    def generate_to_file(self, output_path: Optional[Path] = None) -> None:
        """Generate markdown and write to file or stdout."""
        content = self.generate()

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            print(content, end="")
