"""
Pattern matching and ignore rule strategies for contextify.

This module provides the core logic for determining which files and directories
to include in the context aggregation. It implements the Strategy pattern
to allow flexible, composable ignore rule sources.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Set, Optional

logger = logging.getLogger(__name__)


class IgnoreStrategy(ABC):
    """
    Abstract base class for different ignore rule strategies.

    This follows the Strategy pattern, allowing different sources of ignore
    rules (e.g., .gitignore, .aicontextignore, hardcoded defaults) to be
    plugged in interchangeably.
    """

    @abstractmethod
    def get_ignore_patterns(self) -> List[str]:
        """
        Return a list of gitignore-style patterns.

        Returns:
            List[str]: A list of pattern strings.
        """
        pass


class DefaultIgnoreStrategy(IgnoreStrategy):
    """Provides sensible default ignore patterns for common development artifacts."""

    def get_ignore_patterns(self) -> List[str]:
        """
        Return a comprehensive list of default ignore patterns.

        These patterns cover common build artifacts, cache directories, IDE
        configuration files, and environment-specific files that should not
        be included in the AI context.

        Returns:
            List[str]: Default ignore patterns.
        """
        logger.debug("Using DefaultIgnoreStrategy.")
        return [
            # Version control
            ".git/",
            ".gitignore",
            # Python
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            ".venv/",
            "venv/",
            "env/",
            ".Python",
            "*.egg-info/",
            "dist/",
            "build/",
            # Node.js
            "node_modules/",
            "npm-debug.log",
            "yarn-error.log",
            # IDE/Editor
            ".vscode/",
            ".idea/",
            "*.sublime-project",
            "*.sublime-workspace",
            # OS
            ".DS_Store",
            "Thumbs.db",
            # Environment and Logs
            "*.log",
            ".env",
            ".env.local",
            ".env.*.local",
            # Build artifacts
            "dist/",
            "build/",
            ".tox/",
            ".coverage",
            ".pytest_cache/",
        ]


class FileIgnoreStrategy(IgnoreStrategy):
    """Reads and parses ignore patterns from a file (e.g., .gitignore)."""

    def __init__(self, file_path: Path) -> None:
        """
        Initialize the strategy with a path to an ignore file.

        Args:
            file_path (Path): Path to the ignore file to read.
        """
        self.file_path = file_path

    def get_ignore_patterns(self) -> List[str]:
        """
        Read and return patterns from the configured file.

        If the file does not exist, an empty list is returned. Comments
        (lines starting with #) are ignored.

        Returns:
            List[str]: Patterns from the file, or empty list if not found.
        """
        if not self.file_path.is_file():
            logger.debug(f"Ignore file not found at: {self.file_path}")
            return []

        logger.debug(f"Reading ignore patterns from: {self.file_path}")
        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
            logger.debug(f"Loaded {len(patterns)} patterns from {self.file_path.name}")
            return patterns
        except IOError as e:
            logger.warning(f"Failed to read ignore file {self.file_path}: {e}")
            return []


class PatternMatcher:
    """
    Matches file paths against gitignore-style patterns.

    This class handles pattern matching logic including wildcards, directory-only
    patterns (ending with /), and negation patterns (starting with !).
    Exclusion patterns always take precedence over negation patterns (fail-safe).
    """

    def __init__(self, patterns: List[str]) -> None:
        """
        Initialize the matcher with a list of patterns.

        Patterns starting with ! are negation patterns (re-inclusion rules).
        All other patterns are treated as ignore patterns.

        Args:
            patterns (List[str]): List of gitignore-style patterns.
        """
        self.ignore_patterns: List[str] = [
            p for p in patterns if not p.startswith("!")
        ]
        self.negate_patterns: List[str] = [p[1:] for p in patterns if p.startswith("!")]
        logger.debug(
            f"PatternMatcher initialized with {len(self.ignore_patterns)} ignore patterns "
            f"and {len(self.negate_patterns)} negation patterns."
        )

    def is_match(self, path: Path) -> bool:
        """
        Determine if a path should be ignored based on configured patterns.

        Exclusion patterns take precedence over negation patterns (fail-safe).
        A path is ignored if it matches any ignore pattern and does not match
        any negation pattern (unless already ignored).

        Args:
            path (Path): The path to check.

        Returns:
            bool: True if the path should be ignored, False otherwise.
        """
        is_dir = path.is_dir()
        path_str = str(path)

        # Check ignore patterns
        should_ignore = False
        for pattern in self.ignore_patterns:
            # Handle directory-only patterns (e.g., 'node_modules/')
            if pattern.endswith("/"):
                if is_dir and path.match(pattern.rstrip("/")):
                    should_ignore = True
                    break
                # Check if a directory name appears in the path components
                if f"/{pattern.rstrip('/')}/" in f"/{path_str}/":
                    should_ignore = True
                    break
            # Handle file/directory patterns
            elif path.match(pattern):
                should_ignore = True
                break

        if not should_ignore:
            return False

        # Check negation patterns (re-inclusion)
        for pattern in self.negate_patterns:
            if path.match(pattern):
                # A negation pattern matches, so do not ignore it
                return False

        return True


class IgnoreRuleManager:
    """
    Manages multiple ignore strategies and provides a unified pattern matcher.

    This class composes multiple IgnoreStrategy implementations and merges their
    patterns into a single PatternMatcher, adhering to the Dependency Inversion
    Principle.
    """

    def __init__(self, strategies: List[IgnoreStrategy]) -> None:
        """
        Initialize the manager with a list of strategies.

        Args:
            strategies (List[IgnoreStrategy]): List of ignore strategies to merge.
        """
        self.strategies = strategies
        self.matcher: Optional[PatternMatcher] = None

    def build_matcher(self) -> PatternMatcher:
        """
        Build and cache a PatternMatcher from all configured strategies.

        Patterns from all strategies are merged. If a matcher has already been
        built, it is returned from cache.

        Returns:
            PatternMatcher: A unified pattern matcher with all patterns.
        """
        if self.matcher:
            return self.matcher

        all_patterns: Set[str] = set()
        logger.debug(f"Building matcher from {len(self.strategies)} strategies.")
        for strategy in self.strategies:
            patterns = strategy.get_ignore_patterns()
            logger.debug(
                f"Loaded {len(patterns)} patterns from {strategy.__class__.__name__}"
            )
            all_patterns.update(patterns)

        self.matcher = PatternMatcher(list(all_patterns))
        logger.info(f"Built pattern matcher with {len(all_patterns)} unique patterns.")
        return self.matcher
