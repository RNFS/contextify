# README.md
project-context-builder/
│
├── src/
│   └── context_builder/
│       ├── __init__.py
│       ├── main.py         # CLI entry point and orchestration
│       ├── core.py         # Traversal and aggregation logic
│       ├── patterns.py     # Ignore strategies and pattern matching
│       └── logger.py       # Logging configuration
│
├── pyproject.toml          # Project metadata and dependencies
└── README.md




# main.py
def main():
    print("Hello from contextify!")


if __name__ == "__main__":
    main()


# pyproject.toml
[project]
name = "contextify"
version = "0.1.0"
description = "A CLI tool to concatenate project files for AI context."
requires-python = ">=3.9"
authors = [{name = "Radwan Faris", email = "radwanfaris13@gmail.com"}]

[project.scripts]
contextify = "contextify.main:main"

[tool.uv]
# Configuration for uv can go here if needed


# src/contextify/__init__.py


# src/contextify/core.py

from collections.abc import Set

from pathlib import Path
import sys
from typing import List

from .logger import logger
from .patterns import PatternMatcher

class DirectoryTraverser:
    """Recursively traverses a directory to find files matching criteria."""

    def __init__(self, root_dir: Path, matcher: PatternMatcher, extensions: Set[str]):
        self.root_dir = root_dir
        self.matcher = matcher
        self.extensions = extensions

    def traverse(self) -> List[Path]:
        """
        Performs a recursive traversal to find valid files.

        Returns:
            A sorted list of absolute file paths to include.
        """
        logger.info("Starting directory traversal...")
        included_files = []
        
        for path_object in self.root_dir.rglob("*"):
            relative_path = path_object.relative_to(self.root_dir)
            
            # Check if the path or any of its parents should be ignored
            if self._is_path_ignored(relative_path):
                logger.debug(f"Ignoring path: {relative_path} (due to parent or self match)")
                continue

            if path_object.is_file() and path_object.suffix in self.extensions:
                logger.debug(f"Including file: {relative_path}")
                included_files.append(path_object)

        logger.info(f"Traversal complete. Found {len(included_files)} files to include.")
        return sorted(included_files)
    
    def _is_path_ignored(self, path: Path) -> bool:
        """Check if the path itself or any of its parents are ignored."""
        if self.matcher.is_match(path):
            return True
        for parent in path.parents:
            if self.matcher.is_match(parent):
                return True
        return False


class FileAggregator:
    """Reads and concatenates file contents into a single string."""

    def __init__(self, root_dir: Path, output_file: Path):
        self.root_dir = root_dir
        self.output_file = output_file

    def aggregate_and_write(self, file_paths: List[Path]):
        """
        Reads files, formats them with headers, and writes to the output file.

        Args:
            file_paths: A list of absolute file paths to process.
        """
        logger.info(f"Aggregating content of {len(file_paths)} files to {self.output_file}...")
        
        try:
            with self.output_file.open("w", encoding="utf-8") as f_out:
                for file_path in file_paths:
                    relative_path = file_path.relative_to(self.root_dir)
                    header = f"# {relative_path}\n"
                    
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        f_out.write(header)
                        f_out.write(content)
                        f_out.write("\n\n")
                    except (IOError, UnicodeDecodeError) as e:
                        logger.warning(f"Could not read file {relative_path}: {e}")
            
            logger.info(f"Successfully wrote aggregated content to {self.output_file}")
        except IOError as e:
            logger.error(f"Failed to write to output file {self.output_file}: {e}")
            sys.exit(1)


# src/contextify/logger.py
import logging
import logging.config



LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}

def setup_logging(verbose: bool = False):
    """
    Configures logging based on verbosity.

    Args:
        verbose: If True, set the root logger level to DEBUG.
    """
    if verbose:
        LOGGING_CONFIG["root"]["level"] = "DEBUG"
    logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)


# src/contextify/main.py
import argparse
from pathlib import Path
from typing import List

from .logger import logger, setup_logging
from .patterns import DefaultIgnoreStrategy, FileIgnoreStrategy, IgnoreRuleManager, IgnoreStrategy
from .core import DirectoryTraverser, FileAggregator

def main():
    """Main entry point for the CLI utility."""
    parser = argparse.ArgumentParser(
        description="A CLI tool to concatenate project files for AI context.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("ai_context.md"),
        help="Path to the output file.",
    )
    parser.add_argument(
        "--extensions",
        type=str,
        default=".py,.js,.ts,.jsx,.tsx,.html,.css,.scss,.md,.json,.toml,.yaml,.yml",
        help="Comma-separated list of file extensions to include.",
    )
    parser.add_argument(
        "--ignore-file",
        type=Path,
        help="Path to a custom ignore file (e.g., .aicontextignore). Overrides .gitignore.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose DEBUG logging.",
    )
    
    args = parser.parse_args()
    
    # 1. Setup
    setup_logging(args.verbose)
    root_dir = Path.cwd()
    logger.info(f"Starting context builder in root directory: {root_dir}")
    
    # 2. Configure Ignore Strategies
    strategies: List[IgnoreStrategy] = [DefaultIgnoreStrategy()]
    if args.ignore_file:
        strategies.append(FileIgnoreStrategy(args.ignore_file))
        logger.info(f"Using custom ignore file: {args.ignore_file}")
    else:
        gitignore_path = root_dir / ".gitignore"
        if gitignore_path.exists():
            strategies.append(FileIgnoreStrategy(gitignore_path))
            logger.info("Using .gitignore for exclusion rules.")

    rule_manager = IgnoreRuleManager(strategies)
    matcher = rule_manager.build_matcher()

    # 3. Traverse Directories
    extensions_to_include = {f".{ext.strip().lstrip('.')}" for ext in args.extensions.split(',')}
    traverser = DirectoryTraverser(root_dir, matcher, extensions_to_include)
    files_to_include = traverser.traverse()

    # 4. Aggregate and Write Output
    aggregator = FileAggregator(root_dir, args.output)
    aggregator.aggregate_and_write(files_to_include)
    
    print(f"\n✅ Done. Project context has been written to: {args.output}")

if __name__ == "__main__":
    main()



# src/contextify/patterns.py

from abc import ABC

from abc import abstractmethod
from pathlib import Path
from typing import List, Optional, Set

from .logger import logger

class IgnoreStrategy(ABC):
    """Abstract base class for different ignore rule strategies."""

    @abstractmethod
    def get_ignore_patterns(self) -> List[str]:
        """Returns a list of gitignore-style patterns."""
        pass

class DefaultIgnoreStrategy(IgnoreStrategy):
    """Provides a default set of hardcoded ignore patterns."""

    def get_ignore_patterns(self) -> List[str]:
        """Returns sensible default patterns."""
        logger.debug("Using DefaultIgnoreStrategy.")
        return [
            # Git
            ".git/",
            # Python
            "__pycache__/",
            "*.pyc",
            ".venv/",
            "venv/",
            "env/",
            # Node.js
            "node_modules/",
            # Build artifacts
            "build/",
            "dist/",
            # IDE/OS files
            ".vscode/",
            ".idea/",
            ".DS_Store",
            # Logs and environment
            "*.log",
            ".env",
        ]

class FileIgnoreStrategy(IgnoreStrategy):
    """Reads ignore patterns from a specified file (e.g., .gitignore)."""

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def get_ignore_patterns(self) -> List[str]:
        """
        Reads patterns from the file if it exists.

        Returns:
            A list of patterns, or an empty list if the file is not found.
        """
        if not self.file_path.is_file():
            logger.debug(f"Ignore file not found at: {self.file_path}")
            return []
        
        logger.debug(f"Reading ignore patterns from: {self.file_path}")
        with self.file_path.open("r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]

class PatternMatcher:
    """
    Matches file paths against a set of gitignore-style patterns.
    
    This implementation handles basic glob patterns and directory matching.
    It respects that patterns ending with '/' match directories.
    Negation patterns (`!`) are applied after all ignore patterns.
    """
    def __init__(self, patterns: List[str]):
        self.ignore_patterns = [p for p in patterns if not p.startswith("!")]
        self.negate_patterns = [p[1:] for p in patterns if p.startswith("!")]

    def is_match(self, path: Path) -> bool:
        """
        Checks if a path should be ignored. Exclusion wins.

        Args:
            path: The Path object to check.

        Returns:
            True if the path should be ignored, False otherwise.
        """
        is_dir = path.is_dir()
        path_str = str(path)

        # Check ignore patterns
        should_ignore = False
        for pattern in self.ignore_patterns:
            # Handle directory-only patterns (e.g., 'node_modules/')
            if pattern.endswith('/'):
                if is_dir and path.match(pattern.rstrip('/')):
                    should_ignore = True
                    break
                # Match if a directory's name is part of the path
                if f"/{pattern.rstrip('/')}/" in f"/{path_str}/":
                    should_ignore = True
                    break
            # Handle file/directory patterns
            elif path.match(pattern):
                should_ignore = True
                break

        if not should_ignore:
            return False

        # Check negation patterns (if ignored, see if it should be re-included)
        for pattern in self.negate_patterns:
            if path.match(pattern):
                # A negation pattern matches, so we should NOT ignore it.
                return False
        
        return True

class IgnoreRuleManager:
    """Merges multiple ignore strategies and provides a single PatternMatcher."""
    
    def __init__(self, strategies: List[IgnoreStrategy]):
        self.strategies = strategies
        self.matcher: Optional[PatternMatcher] = None

    def build_matcher(self) -> PatternMatcher:
        """
        Collects and merges patterns from all strategies to create a matcher.
        """
        if self.matcher:
            return self.matcher

        all_patterns: Set[str] = set()
        logger.debug(f"Building matcher from {len(self.strategies)} strategies.")
        for strategy in self.strategies:
            patterns = strategy.get_ignore_patterns()
            logger.debug(f"Loaded {len(patterns)} patterns from {strategy.__class__.__name__}")
            all_patterns.update(patterns)
        
        self.matcher = PatternMatcher(list(all_patterns))
        logger.info(f"Built pattern matcher with {len(all_patterns)} unique patterns.")
        return self.matcher


