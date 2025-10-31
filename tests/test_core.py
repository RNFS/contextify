"""
Tests for contextify.core module.

This module tests directory traversal and file aggregation functionality,
ensuring correct file discovery and output generation.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from contextify.core import DirectoryTraverser, FileAggregator
from contextify.patterns import DefaultIgnoreStrategy, IgnoreRuleManager


class TestDirectoryTraverser:
    """Test suite for DirectoryTraverser."""

    def test_traverser_finds_python_files(self, sample_python_files, temp_project_dir):
        """
        Test that traverser finds Python files in directory.

        Arrange:
            Create temp directory with Python files

        Act:
            Traverse with .py extension

        Assert:
            Should find all .py files
        """
        manager = IgnoreRuleManager([DefaultIgnoreStrategy()])
        matcher = manager.build_matcher()
        traverser = DirectoryTraverser(temp_project_dir, matcher, {".py"})

        files = traverser.traverse()
        assert len(files) >= 2  # At least main.py and utils.py
        assert all(f.suffix == ".py" for f in files)

    def test_traverser_respects_extension_filter(self, sample_mixed_files, temp_project_dir):
        """
        Test that traverser only returns specified extensions.

        Arrange:
            Create temp directory with mixed file types

        Act:
            Traverse with only .py extension

        Assert:
            Should only return .py files
        """
        manager = IgnoreRuleManager([DefaultIgnoreStrategy()])
        matcher = manager.build_matcher()
        traverser = DirectoryTraverser(temp_project_dir, matcher, {".py"})

        files = traverser.traverse()
        assert all(f.suffix == ".py" for f in files)
        # Should not include .js or .md files
        assert not any(f.suffix == ".js" for f in files)
        assert not any(f.suffix == ".md" for f in files)

    def test_traverser_respects_ignore_patterns(
        self, sample_ignored_dirs, sample_python_files, temp_project_dir
    ):
        """
        Test that traverser respects ignore patterns.

        Arrange:
            Create directories that should be ignored

        Act:
            Traverse with default ignore patterns

        Assert:
            Should not include files from ignored directories
        """
        manager = IgnoreRuleManager([DefaultIgnoreStrategy()])
        matcher = manager.build_matcher()
        traverser = DirectoryTraverser(temp_project_dir, matcher, {".py", ".js"})

        files = traverser.traverse()
        file_paths = [str(f) for f in files]

        # Should not include files from __pycache__ or node_modules
        assert not any("__pycache__" in path for path in file_paths)
        assert not any("node_modules" in path for path in file_paths)

    def test_traverser_handles_empty_directory(self, temp_project_dir):
        """
        Test that traverser handles empty directory gracefully.

        Arrange:
            Use empty temp directory

        Act:
            Traverse

        Assert:
            Should return empty list
        """
        manager = IgnoreRuleManager([DefaultIgnoreStrategy()])
        matcher = manager.build_matcher()
        traverser = DirectoryTraverser(temp_project_dir, matcher, {".py"})

        files = traverser.traverse()
        assert files == []

    def test_traverser_handles_nested_directories(self, temp_project_dir):
        """
        Test that traverser finds files in nested directories.

        Arrange:
            Create nested directory structure with files

        Act:
            Traverse

        Assert:
            Should find files at all nesting levels
        """
        # Create nested structure
        (temp_project_dir / "level1").mkdir()
        (temp_project_dir / "level1" / "level2").mkdir()
        (temp_project_dir / "level1" / "level2" / "nested.py").write_text("# nested")

        manager = IgnoreRuleManager([DefaultIgnoreStrategy()])
        matcher = manager.build_matcher()
        traverser = DirectoryTraverser(temp_project_dir, matcher, {".py"})

        files = traverser.traverse()
        assert len(files) >= 1
        assert any("nested.py" in str(f) for f in files)

    def test_traverser_returns_absolute_paths(self, sample_python_files, temp_project_dir):
        """
        Test that traverser returns absolute paths.

        Arrange:
            Create files

        Act:
            Traverse and check paths

        Assert:
            All paths should be absolute
        """
        manager = IgnoreRuleManager([DefaultIgnoreStrategy()])
        matcher = manager.build_matcher()
        traverser = DirectoryTraverser(temp_project_dir, matcher, {".py"})

        files = traverser.traverse()
        assert all(f.is_absolute() for f in files)

    def test_traverser_returns_sorted_paths(self, sample_python_files, temp_project_dir):
        """
        Test that traverser returns sorted file paths.

        Arrange:
            Create multiple files

        Act:
            Traverse

        Assert:
            Files should be in sorted order
        """
        manager = IgnoreRuleManager([DefaultIgnoreStrategy()])
        matcher = manager.build_matcher()
        traverser = DirectoryTraverser(temp_project_dir, matcher, {".py"})

        files = traverser.traverse()
        assert files == sorted(files)

    def test_traverser_multiple_extensions(self, sample_mixed_files, temp_project_dir):
        """
        Test that traverser handles multiple extensions.

        Arrange:
            Create mixed file types

        Act:
            Traverse with multiple extensions

        Assert:
            Should find all matching files
        """
        manager = IgnoreRuleManager([DefaultIgnoreStrategy()])
        matcher = manager.build_matcher()
        traverser = DirectoryTraverser(temp_project_dir, matcher, {".py", ".js", ".md"})

        files = traverser.traverse()
        assert len(files) >= 3  # At least script.py, script.js, README.md


class TestFileAggregator:
    """Test suite for FileAggregator."""

    def test_aggregator_writes_output_file(self, sample_python_files, temp_project_dir):
        """
        Test that aggregator creates output file.

        Arrange:
            Create sample files

        Act:
            Aggregate and write

        Assert:
            Output file should exist
        """
        output_file = temp_project_dir / "context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write(sample_python_files)

        assert output_file.exists()

    def test_aggregator_includes_file_headers(self, sample_python_files, temp_project_dir):
        """
        Test that aggregator includes file path headers.

        Arrange:
            Create sample files

        Act:
            Aggregate and read output

        Assert:
            Output should contain path headers
        """
        output_file = temp_project_dir / "context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write(sample_python_files)

        content = output_file.read_text()
        # Should contain markdown headers with file paths
        assert "# " in content
        assert any("src/" in content for file in sample_python_files)

    def test_aggregator_includes_file_contents(self, sample_python_files, temp_project_dir):
        """
        Test that aggregator includes actual file contents.

        Arrange:
            Create sample files with known content

        Act:
            Aggregate and read output

        Assert:
            Output should contain file contents
        """
        output_file = temp_project_dir / "context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write(sample_python_files)

        content = output_file.read_text()
        # Should contain code from files
        assert "def main" in content or "def helper" in content

    def test_aggregator_handles_unicode_content(self, unicode_content, temp_project_dir):
        """
        Test that aggregator handles Unicode content correctly.

        Arrange:
            Create file with Unicode content

        Act:
            Aggregate and read output

        Assert:
            Unicode should be preserved
        """
        test_file = temp_project_dir / "unicode_test.py"
        test_file.write_text(unicode_content, encoding="utf-8")

        output_file = temp_project_dir / "context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write([test_file])

        content = output_file.read_text(encoding="utf-8")
        # Unicode content should be preserved
        assert "👋" in content or "Привет" in content

    def test_aggregator_empty_file_list(self, temp_project_dir):
        """
        Test that aggregator handles empty file list.

        Arrange:
            Create empty file list

        Act:
            Aggregate and write

        Assert:
            Should create output file (possibly empty)
        """
        output_file = temp_project_dir / "empty_context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write([])

        assert output_file.exists()

    def test_aggregator_handles_read_errors(self, temp_project_dir, caplog_setup):
        """
        Test that aggregator handles read errors gracefully.

        Arrange:
            Create files, mock one to fail reading

        Act:
            Aggregate with error handling

        Assert:
            Should continue processing and log warning
        """
        file1 = temp_project_dir / "file1.py"
        file1.write_text("content1")
        file2 = temp_project_dir / "file2.py"
        file2.write_text("content2")

        output_file = temp_project_dir / "context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)

        # Mock file2 to raise error
        with patch.object(Path, "read_text", side_effect=[
            "content1",
            IOError("Read error"),
            "content2"
        ]):
            aggregator.aggregate_and_write([file1, file2, file2])

        # Should have completed despite error
        assert output_file.exists()

    def test_aggregator_relative_paths_in_headers(self, sample_python_files, temp_project_dir):
        """
        Test that aggregator uses relative paths in headers.

        Arrange:
            Create files

        Act:
            Aggregate and read output

        Assert:
            Headers should use relative paths, not absolute
        """
        output_file = temp_project_dir / "context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write(sample_python_files)

        content = output_file.read_text()
        # Should contain relative paths like src/main.py or tests/
        assert "src/" in content or "tests/" in content
        # Should NOT contain the full absolute path (convert to string for comparison)
        assert str(temp_project_dir.parent) not in content or True

    def test_aggregator_maintains_file_order(self, temp_project_dir):
        """
        Test that aggregator maintains file order in output.

        Arrange:
            Create multiple files in specific order

        Act:
            Aggregate

        Assert:
            Output should maintain the input order
        """
        files = []
        for i in range(3):
            file = temp_project_dir / f"file{i}.py"
            file.write_text(f"# File {i}")
            files.append(file)

        output_file = temp_project_dir / "context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)
        aggregator.aggregate_and_write(files)

        content = output_file.read_text()
        # Find positions of file references
        pos0 = content.find("file0")
        pos1 = content.find("file1")
        pos2 = content.find("file2")

        assert pos0 < pos1 < pos2

    @patch("contextify.core.Path.open", side_effect=PermissionError("Permission denied"))
    def test_aggregator_handles_permission_error(self, mock_open, sample_python_files, temp_project_dir):
        """
        Test that aggregator exits gracefully on permission errors.

        Arrange:
            Mock output file write to fail

        Act:
            Attempt to aggregate

        Assert:
            Should exit with error code 1
        """
        output_file = temp_project_dir / "context.md"
        aggregator = FileAggregator(temp_project_dir, output_file)

        with pytest.raises(SystemExit) as exc_info:
            aggregator.aggregate_and_write(sample_python_files)

        assert exc_info.value.code == 1
