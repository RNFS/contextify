# Contributing to contextify

Thank you for your interest in contributing to **contextify**! We welcome contributions from the community. This document outlines how to get started.

## Code of Conduct

Please be respectful, inclusive, and professional in all interactions. We're committed to providing a welcoming environment for everyone.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/contextify.git
cd contextify
```

### 2. Set Up Development Environment

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
uv pip install -e ".[dev]"
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Code Quality Standards

All contributions must adhere to:

- **PEP 8** via `ruff check`
- **Type hints** for all function signatures
- **Comprehensive docstrings** (Google style)
- **SOLID principles** in design
- **Specific error handling** (no bare `except:`)

### Linting and Formatting

Before committing, ensure your code passes quality checks:

```bash
# Check code style
ruff check src/

# Format code
ruff format src/

# Check type hints
mypy src/contextify/
```

### Running Tests

```bash
pytest
pytest --cov=src/contextify  # With coverage
```

### Testing Locally

Test the CLI from within the project:

```bash
python -m contextify.main --help
python -m contextify.main --verbose --output ./test_context.md
```

## Submitting Changes

### 1. Write Clear Commit Messages

```
[category] Brief summary (50 chars max)

Detailed explanation if needed. Reference issues with #123.
```

Examples:
- `[feature] Add support for .aicontextignore custom files`
- `[fix] Handle Unicode encoding errors in file reading`
- `[docs] Update README with examples`

### 2. Create a Pull Request

- Push your branch to your fork
- Create a PR against the main repository
- Provide a clear title and description
- Reference any related issues

### 3. Code Review

- Respond to reviewer feedback respectfully
- Make requested changes in new commits
- Re-request review when ready

## Areas for Contribution

### Code

- **Bug fixes**: Fix issues reported in [GitHub Issues](https://github.com/yourusername/contextify/issues)
- **Features**: Implement new features or improve existing ones
- **Performance**: Optimize directory traversal or pattern matching
- **Tests**: Improve test coverage and add edge case tests

### Documentation

- Improve README and docstrings
- Add usage examples
- Create tutorials for specific use cases

### Community

- Answer questions in Issues
- Share contextify with others
- Provide feedback and suggestions

## Architecture and Design Principles

Before making significant changes, familiarize yourself with:

- **Layered Architecture**: CLI → Configuration → Traversal → Output
- **Strategy Pattern**: Used for flexible ignore rule sources
- **SOLID Principles**: Applied throughout the codebase
- **Dependency Inversion**: Components depend on abstractions, not concrete implementations

See the main README for more details on system design.

## Reporting Issues

When reporting bugs, please include:

- **Description**: What went wrong?
- **Steps to Reproduce**: How can we reproduce it?
- **Expected Behavior**: What should have happened?
- **Actual Behavior**: What actually happened?
- **Environment**: Python version, OS, uv version, etc.

Example issue:

```
Title: contextify ignores hidden directories incorrectly

Description:
contextify is including files from .vscode/ even though it's in the default ignore list.

Steps:
1. Create .vscode/settings.json
2. Run contextify --verbose
3. Look at the output

Expected: .vscode files should be excluded
Actual: .vscode files are included

Environment: Python 3.11, macOS 13, uv 0.1.0
```

## Questions?

- Open a [discussion](https://github.com/yourusername/contextify/discussions) for general questions
- Check existing [issues](https://github.com/yourusername/contextify/issues) before asking
- Read the [README](README.md) for usage questions

---

Thank you for contributing to contextify! 🙏
