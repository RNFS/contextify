
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
