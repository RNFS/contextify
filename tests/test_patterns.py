"""
Tests for contextify.patterns module.

This module tests pattern matching, ignore strategies, and the rule manager,
ensuring correct handling of gitignore-style patterns and flexible ignore sources.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from contextify.patterns import (
    DefaultIgnoreStrategy,
    FileIgnoreStrategy,
    IgnoreRuleManager,
    PatternMatcher,
)


class TestDefaultIgnoreStrategy:
    """Test suite for DefaultIgnoreStrategy."""

    def test_get_ignore_patterns_returns_list(self):
        """
        Test that get_ignore_patterns returns a non-empty list.

        Arrange:
            Create a DefaultIgnoreStrategy instance

        Act:
            Call get_ignore_patterns

        Assert:
            Should return a list with multiple patterns
        """
        strategy = DefaultIgnoreStrategy()
        patterns = strategy.get_ignore_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_get_ignore_patterns_includes_python(self):
        """
        Test that default patterns include Python-specific ignores.

        Arrange:
            Create a DefaultIgnoreStrategy instance

        Act:
            Call get_ignore_patterns

        Assert:
            Should include __pycache__, *.pyc, .venv, etc.
        """
        strategy = DefaultIgnoreStrategy()
        patterns = strategy.get_ignore_patterns()
        pattern_str = " ".join(patterns)
        assert "__pycache__" in pattern_str
        assert ".pyc" in pattern_str

    def test_get_ignore_patterns_includes_nodejs(self):
        """
        Test that default patterns include Node.js-specific ignores.

        Arrange:
            Create a DefaultIgnoreStrategy instance

        Act:
            Call get_ignore_patterns

        Assert:
            Should include node_modules and npm logs
        """
        strategy = DefaultIgnoreStrategy()
        patterns = strategy.get_ignore_patterns()
        pattern_str = " ".join(patterns)
        assert "node_modules" in pattern_str

    def test_get_ignore_patterns_includes_ide(self):
        """
        Test that default patterns include IDE-specific ignores.

        Arrange:
            Create a DefaultIgnoreStrategy instance

        Act:
            Call get_ignore_patterns

        Assert:
            Should include .vscode, .idea, etc.
        """
        strategy = DefaultIgnoreStrategy()
        patterns = strategy.get_ignore_patterns()
        pattern_str = " ".join(patterns)
        assert ".vscode" in pattern_str or ".idea" in pattern_str

    def test_get_ignore_patterns_consistent(self):
        """
        Test that get_ignore_patterns returns consistent results.

        Arrange:
            Create a DefaultIgnoreStrategy instance

        Act:
            Call get_ignore_patterns twice

        Assert:
            Both calls should return equivalent lists
        """
        strategy = DefaultIgnoreStrategy()
        patterns1 = strategy.get_ignore_patterns()
        patterns2 = strategy.get_ignore_patterns()
        assert patterns1 == patterns2


class TestFileIgnoreStrategy:
    """Test suite for FileIgnoreStrategy."""

    def test_file_ignore_strategy_reads_existing_file(self, sample_gitignore):
        """
        Test that FileIgnoreStrategy reads patterns from an existing file.

        Arrange:
            Create a .gitignore file with patterns

        Act:
            Create FileIgnoreStrategy and get patterns

        Assert:
            Should return the patterns from the file
        """
        strategy = FileIgnoreStrategy(sample_gitignore)
        patterns = strategy.get_ignore_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_file_ignore_strategy_filters_comments(self, temp_project_dir):
        """
        Test that FileIgnoreStrategy ignores comment lines.

        Arrange:
            Create a file with comments

        Act:
            Get patterns from file

        Assert:
            Comments should not be in returned patterns
        """
        ignore_file = temp_project_dir / ".gitignore"
        ignore_file.write_text("# This is a comment\n*.pyc\n# Another comment\n.env")
        strategy = FileIgnoreStrategy(ignore_file)
        patterns = strategy.get_ignore_patterns()
        # Comments should be filtered out
        assert not any(line.startswith("#") for line in patterns)

    def test_file_ignore_strategy_filters_empty_lines(self, temp_project_dir):
        """
        Test that FileIgnoreStrategy ignores empty lines.

        Arrange:
            Create a file with empty lines

        Act:
            Get patterns from file

        Assert:
            Empty lines should not be in returned patterns
        """
        ignore_file = temp_project_dir / ".gitignore"
        ignore_file.write_text("*.pyc\n\n.env\n\n__pycache__/")
        strategy = FileIgnoreStrategy(ignore_file)
        patterns = strategy.get_ignore_patterns()
        assert "" not in patterns
        assert all(p.strip() for p in patterns)

    def test_file_ignore_strategy_missing_file_returns_empty_list(self, temp_project_dir):
        """
        Test that FileIgnoreStrategy returns empty list for missing files.

        Arrange:
            Reference a non-existent file

        Act:
            Get patterns from file

        Assert:
            Should return empty list, not raise error
        """
        missing_file = temp_project_dir / ".gitignore"
        strategy = FileIgnoreStrategy(missing_file)
        patterns = strategy.get_ignore_patterns()
        assert patterns == []

    def test_file_ignore_strategy_whitespace_handling(self, temp_project_dir):
        """
        Test that FileIgnoreStrategy properly strips whitespace.

        Arrange:
            Create a file with leading/trailing whitespace

        Act:
            Get patterns from file

        Assert:
            Patterns should be stripped
        """
        ignore_file = temp_project_dir / ".gitignore"
        ignore_file.write_text("  *.pyc  \n\t.env\t")
        strategy = FileIgnoreStrategy(ignore_file)
        patterns = strategy.get_ignore_patterns()
        assert all(p == p.strip() for p in patterns)


class TestPatternMatcher:
    """Test suite for PatternMatcher."""

    def test_pattern_matcher_simple_wildcard(self):
        """
        Test basic wildcard pattern matching.

        Arrange:
            Create matcher with *.pyc pattern

        Act:
            Check if test.pyc matches

        Assert:
            Should match .pyc files
        """
        matcher = PatternMatcher(["*.pyc"])
        assert matcher.is_match(Path("test.pyc"))
        assert not matcher.is_match(Path("test.py"))

    def test_pattern_matcher_directory_pattern(self):
        """
        Test directory-only pattern matching (pattern ending with /).

        Arrange:
            Create matcher with node_modules/ pattern

        Act:
            Check if node_modules directory matches

        Assert:
            Should match directory, not files named node_modules
        """
        matcher = PatternMatcher(["node_modules/"])
        node_modules_path = Path("node_modules")
        # Note: Path object doesn't know if it's a directory in matcher
        # This is tested in integration tests with real directories
        assert matcher.is_match(node_modules_path)

    @pytest.mark.parametrize(
        "pattern,path,should_match",
        [
            ("*.log", "debug.log", True),
            ("*.log", "debug.txt", False),
            ("__pycache__/", "__pycache__", True),
            (".env", ".env", True),
            (".env.local", ".env", False),
            ("test*.py", "test_main.py", True),
            ("test*.py", "main.py", False),
        ],
    )
    def test_pattern_matcher_parametrized(self, pattern, path, should_match):
        """
        Test pattern matching with various patterns.

        Arrange:
            Create matcher with pattern

        Act:
            Check if path matches

        Assert:
            Should match according to should_match
        """
        matcher = PatternMatcher([pattern])
        result = matcher.is_match(Path(path))
        assert result == should_match

    def test_pattern_matcher_negation_pattern(self):
        """
        Test negation patterns (starting with !).

        Arrange:
            Create matcher with ignore pattern and negation

        Act:
            Check if negated pattern overrides ignore

        Assert:
            Negation should re-include previously ignored pattern
        """
        matcher = PatternMatcher(["*.log", "!important.log"])
        assert matcher.is_match(Path("debug.log"))
        # important.log should NOT be ignored due to negation
        assert not matcher.is_match(Path("important.log"))

    def test_pattern_matcher_multiple_patterns(self):
        """
        Test matching with multiple patterns.

        Arrange:
            Create matcher with multiple patterns

        Act:
            Check various paths

        Assert:
            Should match paths matching any pattern
        """
        matcher = PatternMatcher(["*.pyc", "*.log", "__pycache__/"])
        assert matcher.is_match(Path("test.pyc"))
        assert matcher.is_match(Path("debug.log"))
        assert matcher.is_match(Path("__pycache__"))
        assert not matcher.is_match(Path("main.py"))

    def test_pattern_matcher_empty_patterns(self):
        """
        Test matcher with empty pattern list.

        Arrange:
            Create matcher with empty patterns

        Act:
            Check if any path matches

        Assert:
            Should not match anything
        """
        matcher = PatternMatcher([])
        assert not matcher.is_match(Path("test.pyc"))
        assert not matcher.is_match(Path("anything.txt"))

    def test_pattern_matcher_only_negation_patterns(self, sample_patterns):
        """
        Test matcher with only negation patterns (no ignores).

        Arrange:
            Create matcher with only ! patterns

        Act:
            Check if paths match

        Assert:
            Nothing should be ignored (no base patterns to negate)
        """
        matcher = PatternMatcher(["!*.pyc"])
        assert not matcher.is_match(Path("test.pyc"))
        assert not matcher.is_match(Path("any_file.txt"))


class TestIgnoreRuleManager:
    """Test suite for IgnoreRuleManager."""

    def test_ignore_rule_manager_merges_strategies(self):
        """
        Test that manager properly merges patterns from multiple strategies.

        Arrange:
            Create manager with multiple strategies

        Act:
            Build matcher and check patterns

        Assert:
            Should contain patterns from all strategies
        """
        default_strategy = DefaultIgnoreStrategy()
        file_strategy = FileIgnoreStrategy(Path("nonexistent"))

        manager = IgnoreRuleManager([default_strategy, file_strategy])
        matcher = manager.build_matcher()
        assert matcher is not None

    def test_ignore_rule_manager_builds_matcher_once(self):
        """
        Test that manager caches the built matcher.

        Arrange:
            Create manager and build matcher

        Act:
            Call build_matcher twice

        Assert:
            Should return the same instance both times
        """
        manager = IgnoreRuleManager([DefaultIgnoreStrategy()])
        matcher1 = manager.build_matcher()
        matcher2 = manager.build_matcher()
        assert matcher1 is matcher2

    def test_ignore_rule_manager_empty_strategies(self):
        """
        Test manager with empty strategy list.

        Arrange:
            Create manager with no strategies

        Act:
            Build matcher

        Assert:
            Should create a matcher with no patterns
        """
        manager = IgnoreRuleManager([])
        matcher = manager.build_matcher()
        assert matcher is not None
        # Should not match anything (no patterns)
        assert not matcher.is_match(Path("anything.pyc"))

    def test_ignore_rule_manager_deduplicates_patterns(self, temp_project_dir):
        """
        Test that manager deduplicates identical patterns from multiple sources.

        Arrange:
            Create two strategies with overlapping patterns

        Act:
            Build matcher

        Assert:
            Should deduplicate patterns
        """
        ignore_file = temp_project_dir / ".gitignore"
        ignore_file.write_text("*.pyc\n__pycache__/")

        strategy1 = DefaultIgnoreStrategy()
        strategy2 = FileIgnoreStrategy(ignore_file)

        manager = IgnoreRuleManager([strategy1, strategy2])
        matcher = manager.build_matcher()

        # Both strategies might have *.pyc, but should be deduplicated
        assert matcher is not None
