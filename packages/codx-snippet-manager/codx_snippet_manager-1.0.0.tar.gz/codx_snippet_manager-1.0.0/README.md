# CODX - Code Snippet Manager

A powerful command-line code snippet library manager with an interactive Text User Interface (TUI).

## Features

- **CLI Commands**: Add, find, get, run, edit, and manage code snippets
- **Interactive TUI**: Browse and search snippets with a beautiful terminal interface
- **Variable Substitution**: Use placeholders in snippets with default values
- **Multi-language Support**: Support for Python, JavaScript, Bash, Ruby, PHP, Perl, and more
- **Fuzzy Search**: Find snippets quickly with intelligent search
- **Clipboard Integration**: Copy snippets to clipboard with one command
- **Tag System**: Organize snippets with tags for better categorization

## Installation

### From PyPI (Recommended)

```bash
pip install codx-snippet-manager
```

### From Source

```bash
cd codx_package
pip install -e .
```

### Dependencies

All dependencies are automatically installed with the package:
- typer>=0.9.0
- rich>=13.0.0
- textual>=0.41.0
- pyperclip>=1.8.0
- fuzzywuzzy>=0.18.0
- python-levenshtein>=0.20.0

## Development

### Project Structure

The project follows modern Python packaging standards:

```
codx_package/
├── pyproject.toml          # Modern Python project configuration
├── README.md
├── src/
│   └── codx/              # Main package
│       ├── __init__.py
│       ├── cli/           # Command-line interface
│       ├── core/          # Database and models
│       │   └── schema.sql # Database schema
│       ├── tui/           # Text User Interface
│       └── utils/         # Utility functions
└── tests/                 # Test suite
```

### Building and Publishing

1. **Install build tools**:
   ```bash
   pip install build twine
   ```

2. **Build the package**:
   ```bash
   python -m build
   ```
   This creates `dist/` directory with wheel and source distributions.

3. **Test on TestPyPI** (optional):
   ```bash
   twine upload --repository testpypi dist/*
   ```

4. **Publish to PyPI**:
   ```bash
   twine upload dist/*
   ```

### Running Tests

```bash
python -m pytest tests/ -v
```

## Usage

### Initialize Database

```bash
codx init
```

### Add a Snippet

```bash
# Add from file
codx add --file script.py --description "My Python script"

# Add interactively
codx add --description "Quick command" --language bash
```

### Find Snippets

```bash
# Interactive TUI mode
codx find

# Search with filters
codx find --query "python" --language python --tags "web,api"
```

### Get a Snippet

```bash
# Copy snippet to clipboard
codx get 1
```

### Run a Snippet

```bash
# Execute snippet with variable substitution
codx run 1
```

### Edit a Snippet

```bash
# Edit snippet details
codx edit 1
```

## Variable Substitution

Snippets can contain variables using the `{{variable_name}}` or `{{variable_name:default_value}}` syntax:

```python
print("Hello, {{name:World}}!")
print("Your age is {{age}}")
```

When running the snippet, you'll be prompted to provide values for these variables.

## TUI Navigation

- **Search**: Type to filter snippets
- **Navigate**: Use arrow keys to select snippets
- **Actions**:
  - `Enter/c`: Copy snippet to clipboard
  - `v`: View snippet details
  - `e`: Edit snippet
  - `r`: Run snippet
  - `d`: Delete snippet
  - `q/Escape`: Quit

## Project Structure

```
codx_package/
├── codx/
│   ├── __init__.py
│   ├── main.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── commands.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   ├── tui/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   └── screens.py
│   └── utils/
│       ├── __init__.py
│       ├── execution.py
│       ├── search.py
│       └── variables.py
├── requirements.txt
├── setup.py
└── README.md
```

## License

MIT License