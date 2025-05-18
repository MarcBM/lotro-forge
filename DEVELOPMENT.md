# Development Guide

This guide explains how to set up and work with the LOTRO Forge development environment.

## Initial Setup

### Prerequisites
- Python 3.9 or higher
- Git
- Bash shell (for setup script)

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/MarcBM/lotro_forge.git
   cd lotro_forge
   ```

2. Make the setup script executable:
   ```bash
   chmod +x scripts/setup_dev.sh
   ```

3. Run the setup script:
   ```bash
   ./scripts/setup_dev.sh
   ```
   This script will:
   - Create a virtual environment
   - Install all dependencies
   - Install the package in development mode

4. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
   You'll know it's activated when you see `(venv)` at the start of your prompt.

## Working with the Development Environment

### Activating the Environment
- Always activate the virtual environment before working on the project:
  ```bash
  source venv/bin/activate
  ```

### Deactivating the Environment
- When you're done working, deactivate the environment:
  ```bash
  deactivate
  ```

### Managing Dependencies

1. Installing new packages:
   ```bash
   pip install <package-name>
   ```

2. Updating requirements.txt:
   ```bash
   pip freeze > requirements.txt
   ```

3. Installing development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Tests

1. Run all tests:
   ```bash
   pytest
   ```

2. Run tests with coverage:
   ```bash
   pytest --cov=lotro_forge
   ```

3. Generate coverage report:
   ```bash
   coverage report
   ```

4. View HTML coverage report:
   ```bash
   coverage html
   # Then open htmlcov/index.html in your browser
   ```

## Project Structure

```
lotro_forge/
├── .github/              # GitHub Actions workflows
├── lotro_forge/         # Main package code
│   ├── models/          # Data models
│   ├── parsers/         # XML parsers
│   └── tests/           # Test suite
├── scripts/             # Development scripts
├── .gitignore          # Git ignore rules
├── DEVELOPMENT.md      # This file
├── README.md           # Project documentation
├── requirements.txt    # Project dependencies
└── setup.py           # Package setup file
```

## Best Practices

1. **Virtual Environment**
   - Always work within the virtual environment
   - Never commit the virtual environment directory
   - Use `requirements.txt` for dependency management

2. **Code Quality**
   - Write tests for new features
   - Maintain test coverage above 90%
   - Follow PEP 8 style guidelines
   - Document your code with docstrings

3. **Version Control**
   - Create feature branches for new work
   - Write clear commit messages
   - Keep commits focused and atomic
   - Update tests and documentation with code changes

4. **Testing**
   - Run tests before committing
   - Ensure all tests pass before pushing
   - Add tests for new features
   - Update tests when modifying existing features

## Common Issues and Solutions

1. **Virtual Environment Issues**
   - If you get "command not found" for python/pip:
     - Ensure the virtual environment is activated
     - Check that the setup script ran successfully
   - If packages aren't found:
     - Ensure you're in the virtual environment
     - Try reinstalling dependencies: `pip install -r requirements.txt`

2. **Test Issues**
   - If tests fail with import errors:
     - Ensure the package is installed in development mode
     - Check that you're in the virtual environment
   - If coverage is low:
     - Run `coverage report` to see which files need more tests
     - Add tests for uncovered code paths

## Getting Help

- Check the [GitHub Issues](https://github.com/MarcBM/lotro_forge/issues)
- Review the [RULES.md](RULES.md) file for project guidelines
- Check the test suite for examples of expected behavior 