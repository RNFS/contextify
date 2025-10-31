
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
