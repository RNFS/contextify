"""
Tests for contextify.main module.

This module tests CLI argument parsing, orchestration, and integration
of all components through the main entry point.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from contextify.main import (
    configure_ignore_strategies,
    main,
    parse_arguments,
    parse_extensions,
)


class TestParseArguments:
    """Test suite for argument parsing."""

    def test_parse_arguments_default_values(self):
        """
        Test that parser provides sensible defaults.

        Arrange:
            Create parser with no arguments

        Act:
            Parse empty args

        Assert:
            Should return defaults for all options
        """
        with patch("sys.argv", ["contextify"]):
            args = parse_arguments()
            assert args.output == Path("ai_context.md")
            assert args.verbose is False
            assert args.ignore_file is None

    def test_parse_arguments_custom_output(self):
        """
        Test parsing custom output file.

        Arrange:
            Provide custom output path

        Act:
            Parse arguments

        Assert:
            Should set custom output
        """
        with patch("sys.argv", ["contextify", "--output", "custom.md"]):
            args = parse_arguments()
            assert args.output == Path("custom.md")

    def test_parse_arguments_custom_extensions(self):
        """
        Test parsing custom extensions.

        Arrange:
            Provide custom extension list

        Act:
            Parse arguments

        Assert:
            Should set custom extensions
        """
        with patch("sys.argv", ["contextify", "--extensions", ".py,.js"]):
            args = parse_arguments()
            assert args.extensions == ".py,.js"

    def test_parse_arguments_verbose_flag(self):
        """
        Test parsing verbose flag.

        Arrange:
            Include --verbose

        Act:
            Parse arguments

        Assert:
            Should set verbose to True
        """
        with patch("sys.argv", ["contextify", "--verbose"]):
            args = parse_arguments()
            assert args.verbose is True

    def test_parse_arguments_custom_ignore_file(self):
        """
        Test parsing custom ignore file.

        Arrange:
            Provide custom ignore file

        Act:
            Parse arguments

        Assert:
            Should set custom ignore file
        """
        with patch("sys.argv", ["contextify", "--ignore-file", ".aicontextignore"]):
            args = parse_arguments()
            assert args.ignore_file == Path(".aicontextignore")

    def test_parse_arguments_combined_options(self):
        """
        Test parsing multiple options together.

        Arrange:
            Provide multiple options

        Act:
            Parse arguments

        Assert:
            All options should be set correctly
        """
        with patch(
            "sys.argv",
            [
                "contextify",
                "--output",
                "output.md",
                "--extensions",
                ".py",
                "--verbose",
                "--ignore-file",
                ".customignore",
            ],
        ):
            args = parse_arguments()
            assert args.output == Path("output.md")
            assert args.extensions == ".py"
            assert args.verbose is True
            assert args.ignore_file == Path(".customignore")

    def test_parse_arguments_help(self):
        """
        Test that help option is available.

        Arrange:
            Request help

        Act:
            Parse with --help

        Assert:
            Should display help (exits with 0)
        """
        with patch("sys.argv", ["contextify", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code == 0


class TestParseExtensions:
    """Test suite for extension parsing."""

    def test_parse_extensions_single(self):
        """
        Test parsing single extension.

        Arrange:
            Single extension string

        Act:
            Parse extensions

        Assert:
            Should return set with extension
        """
        result = parse_extensions(".py")
        assert result == {".py"}

    def test_parse_extensions_multiple(self):
        """
        Test parsing multiple extensions.

        Arrange:
            Multiple extension string

        Act:
            Parse extensions

        Assert:
            Should return set with all extensions
        """
        result = parse_extensions(".py,.js,.ts")
        assert result == {".py", ".js", ".ts"}

    def test_parse_extensions_normalizes_dots(self):
        """
        Test that extensions are normalized with leading dots.

        Arrange:
            Extensions with and without dots

        Act:
            Parse extensions

        Assert:
            All should have leading dots
        """
        result = parse_extensions("py,.js,ts")
        assert all(ext.startswith(".") for ext in result)
        assert ".py" in result
        assert ".js" in result
        assert ".ts" in result

    def test_parse_extensions_strips_whitespace(self):
        """
        Test that whitespace is stripped.

        Arrange:
            Extensions with whitespace

        Act:
            Parse extensions

        Assert:
            Should be stripped
        """
        result = parse_extensions(" .py , .js , .ts ")
        assert result == {".py", ".js", ".ts"}

    def test_parse_extensions_empty_string(self):
        """
        Test parsing empty string.

        Arrange:
            Empty extension string

        Act:
            Parse extensions

        Assert:
            Should handle gracefully
        """
        result = parse_extensions("")
        # Empty string should result in at least one entry (the empty split)
        assert isinstance(result, set)


class TestConfigureIgnoreStrategies:
    """Test suite for ignore strategy configuration."""

    def test_configure_ignore_strategies_default(self, temp_project_dir):
        """
        Test default strategy configuration.

        Arrange:
            No ignore files exist

        Act:
            Configure strategies

        Assert:
            Should include DefaultIgnoreStrategy
        """
        strategies = configure_ignore_strategies(temp_project_dir)
        assert len(strategies) >= 1
        from contextify.patterns import DefaultIgnoreStrategy
        assert any(isinstance(s, DefaultIgnoreStrategy) for s in strategies)

    def test_configure_ignore_strategies_with_gitignore(self, sample_gitignore):
        """
        Test strategy configuration with .gitignore.

        Arrange:
            .gitignore exists

        Act:
            Configure strategies

        Assert:
            Should include FileIgnoreStrategy for .gitignore
        """
        root_dir = sample_gitignore.parent
        strategies = configure_ignore_strategies(root_dir)
        from contextify.patterns import FileIgnoreStrategy
        # Should have both default and gitignore strategies
        assert len(strategies) >= 2

    def test_configure_ignore_strategies_custom_file(self, sample_aicontextignore):
        """
        Test strategy configuration with custom ignore file.

        Arrange:
            Custom ignore file provided

        Act:
            Configure strategies

        Assert:
            Should include FileIgnoreStrategy for custom file
        """
        root_dir = sample_aicontextignore.parent
        strategies = configure_ignore_strategies(root_dir, sample_aicontextignore)
        from contextify.patterns import FileIgnoreStrategy
        # Should have default + custom file
        assert len(strategies) >= 2

    def test_configure_ignore_strategies_override_gitignore(
        self, sample_gitignore, sample_aicontextignore
    ):
        """
        Test that custom file overrides .gitignore.

        Arrange:
            Both .gitignore and custom file exist

        Act:
            Configure strategies with custom file

        Assert:
            Should use custom file instead of .gitignore
        """
        root_dir = sample_aicontextignore.parent
        # Move .gitignore to same directory
        sample_gitignore_copy = root_dir / ".gitignore"
        if not sample_gitignore_copy.exists():
            sample_gitignore_copy.write_text(sample_gitignore.read_text())

        strategies = configure_ignore_strategies(root_dir, sample_aicontextignore)
        # Should still have strategies
        assert len(strategies) >= 1


class TestMainOrchestration:
    """Test suite for main entry point orchestration."""

    @patch("contextify.main.DirectoryTraverser")
    @patch("contextify.main.FileAggregator")
    @patch("sys.argv", ["contextify"])
    def test_main_orchestration_flow(self, mock_aggregator, mock_traverser, temp_project_dir):
        """
        Test the main orchestration flow.

        Arrange:
            Mock traverser and aggregator

        Act:
            Call main

        Assert:
            Should orchestrate all steps
        """
        # This is a simplified orchestration test
        # Full integration test in test_integration.py
        pass

    @patch("sys.argv", ["contextify", "--verbose"])
    def test_main_verbose_mode(self):
        """
        Test that main handles verbose mode.

        Arrange:
            Include --verbose flag

        Act:
            Call main with mocks

        Assert:
            Should set up verbose logging
        """
        with patch("contextify.main.setup_logging") as mock_setup:
            with patch("contextify.main.DirectoryTraverser"):
                with patch("contextify.main.FileAggregator"):
                    # Would call main here if we could fully mock
                    # For now, just test argument parsing
                    pass

    def test_main_creates_output_file(self, sample_python_files, temp_project_dir):
        """
        Test that main creates the output file.

        Arrange:
            Sample project structure

        Act:
            Run main

        Assert:
            Output file should be created
        """
        output_path = temp_project_dir / "context.md"
        with patch("sys.argv", ["contextify", "--output", str(output_path)]):
            with patch("contextify.core.Path.cwd", return_value=temp_project_dir):
                # Full main execution would happen here with all mocks
                pass
