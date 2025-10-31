# contextify

A powerful CLI tool to recursively collect and concatenate source code files from your project into a single, AI-friendly context file.

## Purpose

**contextify** is designed to help you share your project's codebase with AI agents (like ChatGPT, Claude, or Copilot) for analysis, code review, or debugging. Instead of manually copying and pasting files, contextify creates a single, well-organized file containing all relevant source code.

### Key Features

✨ **Recursive Directory Traversal**: Automatically finds all relevant source files in your project.

🎯 **Smart File Filtering**: Include specific file types (Python, JavaScript, TypeScript, etc.) with extensible configuration.

🚫 **Intelligent Exclusion**: Respects `.gitignore` rules and supports custom exclusion patterns via `.aicontextignore`.

🔧 **Zero Configuration**: Works out-of-the-box with sensible defaults for common development artifacts.

📋 **Structured Output**: Generates clean Markdown with file path headers for easy navigation.

🔍 **Verbose Logging**: Understand exactly which files are being processed and why.


## Installation

### Global Installation (Recommended)

Install `contextify` globally from PyPI:

```bash
pip install contextify
```

Or with `uv`:

```bash
uv pip install contextify
```

### Development Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/yourusername/contextify.git
cd contextify
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
uv pip install -e .
```

## Usage

### Basic Usage

From any directory, run:

```bash
contextify
```

This generates `ai_context.md` in the current directory containing all recognized source files.

### Command-Line Options

```bash
contextify --help
```

**Arguments:**

- `--output OUTPUT_FILE` (default: `ai_context.md`)
  - Path where the aggregated context file will be written.

- `--extensions EXTS` (default: `.py,.js,.ts,.jsx,.tsx,.html,.css,.scss,.md,.json,.toml,.yaml,.yml,.xml,.sql,.sh,.bash`)
  - Comma-separated list of file extensions to include.
  - Example: `--extensions ".py,.js,.md"`

- `--ignore-file FILE`
  - Path to a custom ignore file (e.g., `.aicontextignore`).
  - Overrides `.gitignore` if provided.

- `--verbose`
  - Enable verbose DEBUG logging to see detailed processing information.

### Examples

#### Generate context for Python files only

```bash
contextify --extensions ".py" --verbose
```

#### Use a custom ignore file

```bash
contextify --ignore-file .aicontextignore --output ./project_context.md
```

#### Generate context for web project

```bash
contextify --extensions ".js,.jsx,.ts,.tsx,.html,.css,.json" --output ./web_context.md
```

## How It Works

1. **Configuration**: Loads ignore patterns from `.gitignore` and optional `.aicontextignore`.
2. **Traversal**: Recursively walks your project directory.
3. **Filtering**: Includes files matching specified extensions, excludes those matching ignore patterns.
4. **Aggregation**: Reads each file and concatenates contents with path headers.
5. **Output**: Writes formatted Markdown to the specified output file.

### Example Output

```markdown
# src/main.py

def main():
    print("Hello, World!")

# src/utils.js

function greet(name) {
    return `Hello, ${name}!`;
}
```

## Ignore Patterns

### Default Ignored Paths

By default, contextify ignores:

- Version control: `.git/`, `.gitignore`
- Python: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `*.egg-info/`, `dist/`, `build/`
- Node.js: `node_modules/`, `npm-debug.log`
- IDE/Editors: `.vscode/`, `.idea/`, `*.sublime-project`
- OS files: `.DS_Store`, `Thumbs.db`
- Logs and environment: `*.log`, `.env`

### Custom Ignore File (.aicontextignore)

Create a `.aicontextignore` file in your project root with patterns (gitignore format):

```
# Example .aicontextignore
tests/
docs/
*.test.py
secrets/
```

Patterns follow gitignore syntax:
- `dirname/` matches directories
- `*.ext` matches files by extension
- `!pattern` negates a rule (re-inclusion)
- Lines starting with `#` are comments

## For AI Agents

The generated `ai_context.md` is formatted specifically for sharing with AI systems:

- **Clear headers** show file paths for easy reference
- **Raw code** without syntax highlighting for universal compatibility
- **Structured format** aids AI parsing and understanding
- **Minimal metadata** keeps the file focused on actual code

## Development & Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Project Structure

```
contextify/
├── src/contextify/
│   ├── __init__.py
│   ├── main.py          # CLI interface
│   ├── core.py          # Traversal and aggregation logic
│   ├── patterns.py      # Ignore strategies and pattern matching
│   └── logger.py        # Logging configuration
├── tests/               # Unit tests
├── pyproject.toml       # Project metadata and dependencies
└── README.md
```

### Running Tests

```bash
pytest
```

### Code Quality

The project adheres to:

- **PEP 8** via `ruff`
- **Type hints** for all functions and classes
- **SOLID principles** for maintainable architecture
- **Comprehensive docstrings** for all public APIs

## License

MIT License. See LICENSE file for details.

## Author

Created with ❤️ for developers who work with AI agents.

---

**Questions or suggestions?** Open an issue on [GitHub](https://github.com/yourusername/contextify/issues).
