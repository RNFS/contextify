"""
Shared pytest fixtures and configuration for contextify tests.

This module provides reusable fixtures that are available to all test modules,
following the DRY principle and ensuring consistent test setup across the suite.
"""

import logging
from pathlib import Path
from typing import List

import pytest


@pytest.fixture
def caplog_setup(caplog):
    """
    Configure caplog for structured logging assertions.

    Args:
        caplog: pytest's built-in caplog fixture

    Returns:
        caplog: Configured caplog with appropriate level
    """
    caplog.set_level(logging.DEBUG)
    return caplog


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """
    Provide an isolated temporary directory for file system tests.

    This fixture creates a clean temporary directory that mimics a real
    project structure. It's automatically cleaned up after each test.

    Args:
        tmp_path: pytest's built-in temporary path fixture

    Returns:
        Path: Absolute path to the temporary directory
    """
    return tmp_path


@pytest.fixture
def sample_python_files(temp_project_dir: Path) -> List[Path]:
    """
    Create sample Python files in the temporary directory.

    Creates a realistic project structure with nested directories and files.

    Args:
        temp_project_dir: Temporary directory fixture

    Returns:
        List[Path]: List of created file paths
    """
    files = []

    # Create src/main.py
    src_dir = temp_project_dir / "src"
    src_dir.mkdir()
    main_py = src_dir / "main.py"
    main_py.write_text('def main():\n    print("Hello, World!")\n')
    files.append(main_py)

    # Create src/utils.py
    utils_py = src_dir / "utils.py"
    utils_py.write_text('def helper():\n    return 42\n')
    files.append(utils_py)

    # Create tests/test_main.py
    tests_dir = temp_project_dir / "tests"
    tests_dir.mkdir()
    test_main_py = tests_dir / "test_main.py"
    test_main_py.write_text('def test_main():\n    assert True\n')
    files.append(test_main_py)

    return files


@pytest.fixture
def sample_mixed_files(temp_project_dir: Path) -> List[Path]:
    """
    Create mixed file types (Python, JavaScript, Markdown) for testing.

    Args:
        temp_project_dir: Temporary directory fixture

    Returns:
        List[Path]: List of created file paths
    """
    files = []

    # Python file
    py_file = temp_project_dir / "script.py"
    py_file.write_text('#!/usr/bin/env python3\nprint("test")\n')
    files.append(py_file)

    # JavaScript file
    js_file = temp_project_dir / "script.js"
    js_file.write_text('console.log("test");\n')
    files.append(js_file)

    # Markdown file
    md_file = temp_project_dir / "README.md"
    md_file.write_text("# Project\n\nThis is a test project.\n")
    files.append(md_file)

    return files


@pytest.fixture
def sample_ignored_dirs(temp_project_dir: Path) -> Path:
    """
    Create common ignored directories (node_modules, __pycache__, etc.).

    Args:
        temp_project_dir: Temporary directory fixture

    Returns:
        Path: The temporary directory containing ignored subdirectories
    """
    # Create __pycache__
    pycache_dir = temp_project_dir / "__pycache__"
    pycache_dir.mkdir()
    (pycache_dir / "module.cpython-39.pyc").write_text("compiled")

    # Create node_modules
    node_modules_dir = temp_project_dir / "node_modules"
    node_modules_dir.mkdir()
    (node_modules_dir / "package.json").write_text("{}")

    # Create .vscode
    vscode_dir = temp_project_dir / ".vscode"
    vscode_dir.mkdir()
    (vscode_dir / "settings.json").write_text("{}")

    # Create dist
    dist_dir = temp_project_dir / "dist"
    dist_dir.mkdir()
    (dist_dir / "bundle.js").write_text("bundled")

    return temp_project_dir


@pytest.fixture
def sample_gitignore(temp_project_dir: Path) -> Path:
    """
    Create a .gitignore file with common patterns.

    Args:
        temp_project_dir: Temporary directory fixture

    Returns:
        Path: Path to the created .gitignore file
    """
    gitignore = temp_project_dir / ".gitignore"
    content = """
# Python
__pycache__/
*.pyc
.venv/

# Node
node_modules/
npm-debug.log

# IDE
.vscode/
.idea/

# Environment
.env
.env.local
"""
    gitignore.write_text(content)
    return gitignore


@pytest.fixture
def sample_aicontextignore(temp_project_dir: Path) -> Path:
    """
    Create a .aicontextignore file for custom patterns.

    Args:
        temp_project_dir: Temporary directory fixture

    Returns:
        Path: Path to the created .aicontextignore file
    """
    aicontextignore = temp_project_dir / ".aicontextignore"
    content = """
# Custom AI context exclusions
tests/
docs/
*.test.py
secrets/
"""
    aicontextignore.write_text(content)
    return aicontextignore


@pytest.fixture
def sample_patterns() -> List[str]:
    """
    Provide a standard list of ignore patterns for testing.

    Returns:
        List[str]: List of gitignore-style patterns
    """
    return [
        "*.pyc",
        "__pycache__/",
        ".env",
        "node_modules/",
        ".vscode/",
        "*.log",
    ]


@pytest.fixture
def complex_patterns() -> List[str]:
    """
    Provide complex patterns including negations and directory-specific rules.

    Returns:
        List[str]: List of patterns with various complexities
    """
    return [
        "*.log",
        "build/",
        "dist/",
        "__pycache__/",
        ".env",
        "!.env.example",  # Negation pattern
        "*.tmp",
        ".vscode/",
        ".idea/",
    ]


@pytest.fixture
def unicode_content() -> str:
    """
    Provide unicode-heavy content for encoding tests.

    Returns:
        str: String with various unicode characters
    """
    return """
# Multilingual Content
Hello, World! 👋
Привет, Мир! 🇷🇺
你好，世界！ 🇨🇳
مرحبا بالعالم! 🇸🇦

def greet():
    print("Ñoño español")  # Spanish
    print("Café français")  # French
"""
