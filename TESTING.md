# Testing Guide for contextify

Comprehensive guide to running, writing, and maintaining tests for the contextify project.

## Quick Start

### Installation

First, install development dependencies:

```bash
cd contextify
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
uv pip install -e ".[dev]"
```

### Running All Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/contextify --cov-report=html

# Run with verbose output
pytest -v

# Run tests in parallel (faster)
pytest -n auto
```

## Test Structure

The test suite is organized into logical modules:

```
tests/
├── __init__.py                # Test package marker
├── conftest.py                # Shared fixtures and configuration
├── test_logger.py             # Logging configuration tests (14 tests)
├── test_patterns.py           # Pattern matching tests (18 tests)
├── test_core.py               # Traversal and aggregation tests (14 tests)
├── test_main.py               # CLI argument parsing tests (12 tests)
└── test_integration.py        # End-to-end workflow tests (9 tests)
```

**Total: ~80 tests covering all major components**

## Running Specific Tests

### Run a single test file

```bash
pytest tests/test_patterns.py
```

### Run a single test class

```bash
pytest tests/test_patterns.py::TestPatternMatcher
```

### Run a single test

```bash
pytest tests/test_patterns.py::TestPatternMatcher::test_pattern_matcher_simple_wildcard
```

### Run tests matching a pattern

```bash
pytest -k "pattern_matcher"
```

### Run only integration tests

```bash
pytest tests/test_integration.py
```

## Test Categories

### Unit Tests (65 tests)

**Purpose:** Test individual components in isolation

**File:** `tests/test_logger.py`, `tests/test_patterns.py`, `tests/test_core.py`, `tests/test_main.py`

**Example:**
```python
def test_pattern_matcher_simple_wildcard(self):
    """Test basic wildcard pattern matching."""
    matcher = PatternMatcher(["*.pyc"])
    assert matcher.is_match(Path("test.pyc"))
    assert not matcher.is_match(Path("test.py"))
```

### Integration Tests (9 tests)

**Purpose:** Test complete workflows combining multiple components

**File:** `tests/test_integration.py`

**Example:**
```python
def test_integration_basic_workflow(self, sample_python_files, temp_project_dir):
    """Test basic end-to-end workflow."""
    strategies = configure_ignore_strategies(temp_project_dir)
    rule_manager = IgnoreRuleManager(strategies)
    matcher = rule_manager.build_matcher()
    # ... continue workflow
```

## Fixtures (Available in All Tests)

### Directory Fixtures

```python
@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """Isolated temporary directory for file system tests."""

@pytest.fixture
def sample_python_files(temp_project_dir: Path) -> List[Path]:
    """Create sample Python files in temporary directory."""

@pytest.fixture
def sample_mixed_files(temp_project_dir: Path) -> List[Path]:
    """Create mixed file types (Python, JavaScript, Markdown)."""

@pytest.fixture
def sample_ignored_dirs(temp_project_dir: Path) -> Path:
    """Create common ignored directories."""
```

### Configuration Fixtures

```python
@pytest.fixture
def sample_gitignore(temp_project_dir: Path) -> Path:
    """Create a .gitignore file with common patterns."""

@pytest.fixture
def sample_aicontextignore(temp_project_dir: Path) -> Path:
    """Create a .aicontextignore file for custom patterns."""
```

### Data Fixtures

```python
@pytest.fixture
def sample_patterns() -> List[str]:
    """Standard list of ignore patterns for testing."""

@pytest.fixture
def complex_patterns() -> List[str]:
    """Complex patterns including negations and directory rules."""

@pytest.fixture
def unicode_content() -> str:
    """Unicode-heavy content for encoding tests."""
```

### Logging Fixtures

```python
@pytest.fixture
def caplog_setup(caplog):
    """Configure caplog for structured logging assertions."""
```

## Coverage Report

Generate HTML coverage report:

```bash
pytest --cov=src/contextify --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

**Target coverage:** 85%+

View coverage in terminal:

```bash
pytest --cov=src/contextify --cov-report=term-missing
```

## Writing New Tests

### Test Structure (AAA Pattern)

Every test should follow Arrange-Act-Assert:

```python
def test_something_specific(self, fixture):
    """
    Clear description of what is being tested.

    Arrange:
        Set up test data and conditions

    Act:
        Execute the code being tested

    Assert:
        Verify the results
    """
    # Arrange
    test_data = fixture

    # Act
    result = some_function(test_data)

    # Assert
    assert result == expected_value
```

### Naming Convention

- Class names: `Test<ComponentName>` (e.g., `TestPatternMatcher`)
- Test method names: `test_<class>_<method>_<scenario>` (e.g., `test_pattern_matcher_is_match_ignores_directory`)

### Using Parametrization

For testing multiple scenarios:

```python
@pytest.mark.parametrize(
    "pattern,path,should_match",
    [
        ("*.log", "debug.log", True),
        ("*.log", "debug.txt", False),
        ("__pycache__/", "__pycache__", True),
    ],
)
def test_pattern_matcher_parametrized(self, pattern, path, should_match):
    """Test pattern matching with various patterns."""
    matcher = PatternMatcher([pattern])
    assert matcher.is_match(Path(path)) == should_match
```

### Using Mocks

Mock external dependencies:

```python
from unittest.mock import patch, MagicMock

@patch("contextify.patterns.Path.read_text")
def test_file_ignore_strategy_reads_file(mock_read, sample_patterns):
    """Test file reading."""
    mock_read.return_value = "\n".join(sample_patterns)
    # ... rest of test
```

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, "3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest --cov=src/contextify
      - run: ruff check src/
```

## Best Practices

### ✅ Do

- ✅ Write one assertion per test (or related assertions)
- ✅ Use descriptive test names
- ✅ Use fixtures for setup
- ✅ Mock external dependencies
- ✅ Test error conditions
- ✅ Use parametrization for multiple scenarios
- ✅ Keep tests fast
- ✅ Test public APIs

### ❌ Don't

- ❌ Use bare `except:` in tests
- ❌ Create external files outside of temp directories
- ❌ Test implementation details
- ❌ Make tests dependent on execution order
- ❌ Skip error handling tests
- ❌ Create tests that are slower than necessary
- ❌ Mix concerns in a single test

## Debugging Tests

### Run with detailed output

```bash
pytest -vv tests/test_patterns.py::TestPatternMatcher::test_pattern_matcher_simple_wildcard
```

### Stop on first failure

```bash
pytest -x
```

### Drop into debugger on failure

```bash
pytest --pdb tests/test_patterns.py
```

### Show local variables on failure

```bash
pytest -l
```

### Run with logging output

```bash
pytest -o log_cli=true -o log_cli_level=DEBUG
```

## Common Issues

### "No virtual environment found"

Ensure virtual environment is activated:

```bash
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

### "Module not found" errors

Reinstall the package in editable mode:

```bash
uv pip install -e .
```

### Tests run slowly

Use parallel execution:

```bash
pytest -n auto
```

Install pytest-xdist:

```bash
uv pip install pytest-xdist
```

### Permission errors on temp files

This is usually handled by pytest's tmp_path fixture. If you create custom temp files, ensure they're cleaned up:

```python
def test_something(tmp_path):
    test_file = tmp_path / "file.txt"
    # pytest automatically cleans up tmp_path after test
```

## Adding New Test Modules

1. Create `tests/test_<module>.py`
2. Import the module to test
3. Create a test class `Test<Module>`
4. Add test methods following naming convention
5. Use shared fixtures from `conftest.py`
6. Document the test with docstrings

Example:

```python
"""Tests for contextify.<module>."""

import pytest
from contextify.<module> import SomeClass

class TestSomeClass:
    """Test suite for SomeClass."""

    def test_something(self, sample_pattern):
        """Test description in docstring."""
        # AAA pattern
        pass
```

## Test Maintenance

### Regular Tasks

- **Weekly:** Run tests locally before pushing
- **Before PR:** Run full test suite with coverage
- **After merge:** Verify CI/CD tests pass
- **Quarterly:** Review coverage report for gaps

### Updating Tests

When modifying source code:

1. Run affected tests: `pytest tests/test_<module>.py`
2. Run full suite: `pytest`
3. Check coverage: `pytest --cov=src/contextify`
4. Update tests if behavior changes

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

**Questions?** Open an issue or discussion on GitHub.
