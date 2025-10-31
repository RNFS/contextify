"""
CLI interface and orchestration for contextify.

This module provides the command-line interface and orchestrates the workflow
of ignore rule configuration, directory traversal, and file aggregation.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Set

from contextify.core import DirectoryTraverser, FileAggregator
from contextify.logger import get_logger, setup_logging
from contextify.patterns import (
    DefaultIgnoreStrategy,
    FileIgnoreStrategy,
    IgnoreRuleManager,
)

logger = get_logger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse and return command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        prog="contextify",
        description="A CLI tool to concatenate project source files for AI context sharing",
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
        default=".py,.js,.ts,.jsx,.tsx,.html,.css,.scss,.md,.json,.toml,.yaml,.yml,.xml,.sql,.sh,.bash",
        help="Comma-separated list of file extensions to include (without leading dot).",
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

    return parser.parse_args()


def configure_ignore_strategies(
    root_dir: Path, custom_ignore_file: Path = None
) -> List[object]:
    """
    Configure ignore strategies based on available files and arguments.

    The strategy list includes:
    1. DefaultIgnoreStrategy (always included as safety net)
    2. FileIgnoreStrategy(.gitignore) if it exists
    3. FileIgnoreStrategy(custom_ignore_file) if provided

    Args:
        root_dir (Path): The project root directory.
        custom_ignore_file (Path, optional): Path to a custom ignore file.

    Returns:
        List: List of configured IgnoreStrategy instances.
    """
    strategies = [DefaultIgnoreStrategy()]

    if custom_ignore_file:
        strategies.append(FileIgnoreStrategy(custom_ignore_file))
        logger.info(f"Using custom ignore file: {custom_ignore_file}")
    else:
        gitignore_path = root_dir / ".gitignore"
        if gitignore_path.exists():
            strategies.append(FileIgnoreStrategy(gitignore_path))
            logger.info("Using .gitignore for exclusion rules.")
        else:
            logger.warning(
                "No .gitignore found. Using default ignore patterns as safety net."
            )

    return strategies


def parse_extensions(extensions_str: str) -> Set[str]:
    """
    Parse a comma-separated string of extensions into a set.

    Each extension is normalized to include a leading dot.

    Args:
        extensions_str (str): Comma-separated file extensions.

    Returns:
        Set[str]: Set of normalized file extensions (with leading dot).
    """
    return {f".{ext.strip().lstrip('.')}" for ext in extensions_str.split(",")}


def main() -> None:
    """
    Main entry point for the contextify CLI application.

    Orchestrates the complete workflow:
    1. Parse command-line arguments
    2. Setup logging
    3. Configure ignore rules
    4. Traverse directories
    5. Aggregate and write output
    """
    args = parse_arguments()

    # Setup logging
    setup_logging(args.verbose)

    # Get root directory
    root_dir = Path.cwd()
    logger.info(f"Starting contextify in root directory: {root_dir}")

    # Configure ignore strategies
    strategies = configure_ignore_strategies(root_dir, args.ignore_file)
    rule_manager = IgnoreRuleManager(strategies)
    matcher = rule_manager.build_matcher()

    # Parse and normalize extensions
    extensions_to_include = parse_extensions(args.extensions)
    logger.debug(f"Including file extensions: {extensions_to_include}")

    # Traverse directories
    traverser = DirectoryTraverser(root_dir, matcher, extensions_to_include)
    files_to_include = traverser.traverse()

    if not files_to_include:
        logger.warning("No files found matching the criteria. Output file will be empty.")

    # Aggregate and write output
    aggregator = FileAggregator(root_dir, args.output)
    aggregator.aggregate_and_write(files_to_include)

    # Success message
    print(f"\n✅ Done! Project context written to: {args.output}")


if __name__ == "__main__":
    main()
