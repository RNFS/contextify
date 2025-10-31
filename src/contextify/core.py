"""
Core logic for directory traversal and file aggregation.

This module provides the business logic for recursively traversing directories
and aggregating file contents into a single formatted output.
"""

import logging
import sys
from pathlib import Path
from typing import List, Set

from contextify.patterns import PatternMatcher

logger = logging.getLogger(__name__)


class DirectoryTraverser:
    """
    Recursively traverses a directory to find files matching criteria.

    This class is responsible for walking the file system and filtering files
    based on extension and ignore patterns. It follows the Single Responsibility
    Principle: its only concern is directory traversal and filtering.
    """

    def __init__(
        self, root_dir: Path, matcher: PatternMatcher, extensions: Set[str]
    ) -> None:
        """
        Initialize the traverser.

        Args:
            root_dir (Path): The root directory to traverse.
            matcher (PatternMatcher): The pattern matcher for filtering.
            extensions (Set[str]): Set of file extensions to include (e.g., {'.py', '.js'}).
        """
        self.root_dir = root_dir
        self.matcher = matcher
        self.extensions = extensions

    def traverse(self) -> List[Path]:
        """
        Perform recursive traversal and return filtered file paths.

        Returns:
            List[Path]: A sorted list of absolute file paths to include.
        """
        logger.info("Starting directory traversal...")
        included_files = []

        for path_object in self.root_dir.rglob("*"):
            relative_path = path_object.relative_to(self.root_dir)

            # Check if the path or any of its parents should be ignored
            if self._is_path_ignored(relative_path):
                logger.debug(
                    f"Ignoring path: {relative_path} (due to parent or self match)"
                )
                continue

            if path_object.is_file() and path_object.suffix in self.extensions:
                logger.debug(f"Including file: {relative_path}")
                included_files.append(path_object)

        logger.info(f"Traversal complete. Found {len(included_files)} files to include.")
        return sorted(included_files)

    def _is_path_ignored(self, path: Path) -> bool:
        """
        Check if the path itself or any of its parent directories are ignored.

        Args:
            path (Path): The relative path to check.

        Returns:
            bool: True if the path or any parent is ignored, False otherwise.
        """
        if self.matcher.is_match(path):
            return True
        for parent in path.parents:
            if self.matcher.is_match(parent):
                return True
        return False


class FileAggregator:
    """
    Aggregates file contents into a single formatted output file.

    This class is responsible for reading files, formatting them with path
    headers, and writing the aggregated content to disk. It follows the
    Single Responsibility Principle: its only concern is file reading and writing.
    """

    def __init__(self, root_dir: Path, output_file: Path) -> None:
        """
        Initialize the aggregator.

        Args:
            root_dir (Path): The project root directory (for relative path calculation).
            output_file (Path): The path where the aggregated output will be written.
        """
        self.root_dir = root_dir
        self.output_file = output_file

    def aggregate_and_write(self, file_paths: List[Path]) -> None:
        """
        Read files and write aggregated content to output file.

        Each file is preceded by a Markdown header showing its relative path.
        If an individual file cannot be read, a warning is logged and the
        process continues with the next file.

        Args:
            file_paths (List[Path]): List of absolute file paths to aggregate.

        Returns:
            None
        """
        logger.info(
            f"Aggregating content of {len(file_paths)} files to {self.output_file}..."
        )

        try:
            with self.output_file.open("w", encoding="utf-8") as f_out:
                for file_path in file_paths:
                    relative_path = file_path.relative_to(self.root_dir)
                    header = f"# {relative_path}\n\n"

                    try:
                        content = file_path.read_text(encoding="utf-8")
                        f_out.write(header)
                        f_out.write(content)
                        f_out.write("\n\n")
                    except (IOError, UnicodeDecodeError) as e:
                        logger.warning(
                            f"Could not read file {relative_path}: {e}. Skipping."
                        )

            logger.info(f"Successfully wrote aggregated content to {self.output_file}")
        except IOError as e:
            logger.error(f"Failed to write to output file {self.output_file}: {e}")
            sys.exit(1)
