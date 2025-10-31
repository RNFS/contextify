"""
Integration tests for contextify.

This module contains end-to-end tests that verify the complete workflow
of the contextify tool, combining all components together.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from contextify.core import DirectoryTraverser, FileAggregator
from contextify.main import (
    configure_ignore_strategies,
    parse_extensions,
)
from contextify.patterns import IgnoreRuleManager


class TestEndToEndWorkflow:
    """Test suite for complete end-to-end workflows."""

    def test_integration_basic_workflow(self, sample_python_files, temp_project_dir):
        """
        Test basic end-to-end workflow.

        Arrange:
            Create sample Python project

        Act:
            Run complete workflow (configure -> traverse -> aggregate)

        Assert:
            Should produce valid context file
        """
        # Configure ignore rules
        strategies = configure_ignore_strategies(temp_project_dir)
        rule_manager = IgnoreRuleManager(strategies)
        matcher = rule_manager.build_matcher()

        # Parse extensions
        extensions = parse_extensions(".py")

        # Traverse
        traverser = DirectoryTraverser(temp_project_dir, matcher, extensions)
        files = traverser.traverse()

        assert len(files) >= 2
        assert all(f.suffix == ".py" for f in files)

        # Aggregate
        output_file = temp_project_dir / "context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write(files)

        assert output_file.exists()
        content = output_file.read_text()
        assert len(content) > 0
        assert "def " in content or "#" in content

    def test_integration_respects_gitignore(self, sample_gitignore, sample_python_files, temp_project_dir):
        """
        Test that complete workflow respects .gitignore.

        Arrange:
            Create .gitignore and project files

        Act:
            Run complete workflow

        Assert:
            Should exclude .gitignore'd files
        """
        # Create __pycache__ directory (should be ignored by .gitignore)
        pycache = temp_project_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "cached.pyc").write_text("compiled")

        # Configure with .gitignore
        strategies = configure_ignore_strategies(temp_project_dir)
        rule_manager = IgnoreRuleManager(strategies)
        matcher = rule_manager.build_matcher()

        # Traverse
        extensions = parse_extensions(".py,.pyc")
        traverser = DirectoryTraverser(temp_project_dir, matcher, extensions)
        files = traverser.traverse()

        # Should not include __pycache__
        assert not any("__pycache__" in str(f) for f in files)

    def test_integration_mixed_file_types(self, sample_mixed_files, temp_project_dir):
        """
        Test workflow with mixed file types.

        Arrange:
            Create mixed file types

        Act:
            Configure for multiple extensions and aggregate

        Assert:
            Should include all specified types
        """
        # Configure
        strategies = configure_ignore_strategies(temp_project_dir)
        rule_manager = IgnoreRuleManager(strategies)
        matcher = rule_manager.build_matcher()

        # Parse multiple extensions
        extensions = parse_extensions(".py,.js,.md")

        # Traverse
        traverser = DirectoryTraverser(temp_project_dir, matcher, extensions)
        files = traverser.traverse()

        # Should find files of different types
        assert len(files) >= 3

        # Aggregate
        output_file = temp_project_dir / "mixed_context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write(files)

        content = output_file.read_text()
        # Should have content from different file types
        assert len(content) > 100

    def test_integration_nested_structures(self, temp_project_dir):
        """
        Test workflow with complex nested directory structure.

        Arrange:
            Create nested structure

        Act:
            Run complete workflow

        Assert:
            Should traverse all levels
        """
        # Create nested structure
        (temp_project_dir / "src").mkdir()
        (temp_project_dir / "src" / "main.py").write_text("# Main")
        (temp_project_dir / "src" / "utils").mkdir()
        (temp_project_dir / "src" / "utils" / "helper.py").write_text("# Helper")
        (temp_project_dir / "tests").mkdir()
        (temp_project_dir / "tests" / "test_main.py").write_text("# Tests")

        # Configure
        strategies = configure_ignore_strategies(temp_project_dir)
        rule_manager = IgnoreRuleManager(strategies)
        matcher = rule_manager.build_matcher()

        # Traverse
        extensions = parse_extensions(".py")
        traverser = DirectoryTraverser(temp_project_dir, matcher, extensions)
        files = traverser.traverse()

        assert len(files) >= 3

        # Aggregate
        output_file = temp_project_dir / "nested_context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write(files)

        content = output_file.read_text()
        # Should contain references to all nested files
        assert "main.py" in content or "Main" in content

    def test_integration_custom_ignore_file(
        self, sample_aicontextignore, temp_project_dir
    ):
        """
        Test workflow with custom .aicontextignore file.

        Arrange:
            Create .aicontextignore with custom rules

        Act:
            Run workflow with custom ignore file

        Assert:
            Should respect custom patterns
        """
        # Create files to be ignored by custom file
        (temp_project_dir / "test_file.py").write_text("# Test")
        (temp_project_dir / "secret.py").write_text("# Secret")  # Will be ignored

        # Configure with custom ignore file
        strategies = configure_ignore_strategies(temp_project_dir, sample_aicontextignore)
        rule_manager = IgnoreRuleManager(strategies)
        matcher = rule_manager.build_matcher()

        # Traverse
        extensions = parse_extensions(".py")
        traverser = DirectoryTraverser(temp_project_dir, matcher, extensions)
        files = traverser.traverse()

        # Aggregate
        output_file = temp_project_dir / "custom_context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write(files)

        content = output_file.read_text()
        assert len(content) > 0

    def test_integration_empty_project(self, temp_project_dir):
        """
        Test workflow with empty project.

        Arrange:
            Empty project directory

        Act:
            Run complete workflow

        Assert:
            Should handle gracefully with empty output
        """
        # Configure
        strategies = configure_ignore_strategies(temp_project_dir)
        rule_manager = IgnoreRuleManager(strategies)
        matcher = rule_manager.build_matcher()

        # Traverse
        extensions = parse_extensions(".py")
        traverser = DirectoryTraverser(temp_project_dir, matcher, extensions)
        files = traverser.traverse()

        assert files == []

        # Aggregate
        output_file = temp_project_dir / "empty_context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write(files)

        assert output_file.exists()

    def test_integration_unicode_handling(self, unicode_content, temp_project_dir):
        """
        Test workflow with unicode content.

        Arrange:
            Create files with unicode content

        Act:
            Run complete workflow

        Assert:
            Should preserve unicode
        """
        # Create file with unicode
        unicode_file = temp_project_dir / "unicode.py"
        unicode_file.write_text(unicode_content, encoding="utf-8")

        # Configure
        strategies = configure_ignore_strategies(temp_project_dir)
        rule_manager = IgnoreRuleManager(strategies)
        matcher = rule_manager.build_matcher()

        # Traverse
        extensions = parse_extensions(".py")
        traverser = DirectoryTraverser(temp_project_dir, matcher, extensions)
        files = traverser.traverse()

        # Aggregate
        output_file = temp_project_dir / "unicode_context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write(files)

        content = output_file.read_text(encoding="utf-8")
        # Unicode should be preserved
        assert len(content) > len(unicode_content) * 0.8

    def test_integration_large_file_count(self, temp_project_dir):
        """
        Test workflow with many files.

        Arrange:
            Create many Python files

        Act:
            Run workflow

        Assert:
            Should handle large number of files
        """
        # Create 50 Python files
        for i in range(50):
            (temp_project_dir / f"file_{i:03d}.py").write_text(f"# File {i}")

        # Configure
        strategies = configure_ignore_strategies(temp_project_dir)
        rule_manager = IgnoreRuleManager(strategies)
        matcher = rule_manager.build_matcher()

        # Traverse
        extensions = parse_extensions(".py")
        traverser = DirectoryTraverser(temp_project_dir, matcher, extensions)
        files = traverser.traverse()

        assert len(files) == 50

        # Aggregate
        output_file = temp_project_dir / "large_context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write(files)

        assert output_file.exists()
        content = output_file.read_text()
        # All files should be in context
        assert "File 0" in content
        assert "File 49" in content

    def test_integration_real_world_project_structure(self, temp_project_dir):
        """
        Test workflow with realistic project structure.

        Arrange:
            Create realistic project layout

        Act:
            Run complete workflow

        Assert:
            Should correctly aggregate
        """
        # Create realistic structure
        (temp_project_dir / "src").mkdir()
        (temp_project_dir / "src" / "__init__.py").write_text("")
        (temp_project_dir / "src" / "app.py").write_text("def run():\n    pass")
        (temp_project_dir / "src" / "config.py").write_text("DEBUG = True")

        (temp_project_dir / "tests").mkdir()
        (temp_project_dir / "tests" / "test_app.py").write_text("def test():\n    pass")

        (temp_project_dir / "docs").mkdir()
        (temp_project_dir / "docs" / "README.md").write_text("# Docs")

        (temp_project_dir / ".gitignore").write_text("__pycache__/\n.pytest_cache/")

        # Configure
        strategies = configure_ignore_strategies(temp_project_dir)
        rule_manager = IgnoreRuleManager(strategies)
        matcher = rule_manager.build_matcher()

        # Traverse for Python and Markdown
        extensions = parse_extensions(".py,.md")
        traverser = DirectoryTraverser(temp_project_dir, matcher, extensions)
        files = traverser.traverse()

        # Should find source, tests, and docs
        assert len(files) >= 4

        # Aggregate
        output_file = temp_project_dir / "project_context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write(files)

        content = output_file.read_text()
        assert "def run" in content or "app" in content
        assert "def test" in content or "test_app" in content
        assert "Docs" in content or "README" in content
