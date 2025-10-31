"""
contextify: A CLI tool to concatenate project source files for AI context.

This package provides a command-line utility to recursively traverse your
project directory, collect source code files, and aggregate them into a single
file suitable for sharing with AI agents for analysis or assistance.

Example:
    >>> import subprocess
    >>> subprocess.run(["contextify", "--help"])

Attributes:
    __version__ (str): The version of the contextify package.
    __author__ (str): The author of the package.
"""

__version__ = "0.1.0"
__author__ = "Radwan"
__email__ = "radwanfaris13@gmail.com"
__license__ = "MIT"

__all__ = ["__version__", "__author__", "__email__", "__license__"]
