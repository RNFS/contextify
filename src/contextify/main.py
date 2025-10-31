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

