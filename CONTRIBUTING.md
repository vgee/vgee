# Contributing to VGEE

Thank you for your interest in contributing to the VGEE project! This document provides guidelines for contributing code, tests, and documentation.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Pull Request Guidelines](#pull-request-guidelines)

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   ```bash
   git clone https://github.com/yourusername/vgee.git
   cd vgee
   ```

3. **Create a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Development Workflow

### Creating a Feature Branch

1. Create a new branch for your feature or bugfix:

   ```bash
   git checkout -b feature-name
   ```

2. Make your changes to the code

3. Run tests to ensure nothing is broken:

   ```bash
   pytest
   ```

4. Commit your changes with descriptive messages:

   ```bash
   git commit -m "Add feature: description of changes"
   ```

5. Push to your fork:

   ```bash
   git push origin feature-name
   ```

6. Create a Pull Request on GitHub

## Code Style

We follow Python best practices and PEP 8 standards:

### General Guidelines

- **Indentation**: Use 4 spaces (not tabs)
- **Line Length**: Maximum 100 characters
- **Naming**: Use `snake_case` for functions/variables, `PascalCase` for classes
- **Type Hints**: All functions should include type annotations
- **Docstrings**: Use Google-style docstrings for modules, classes, and public methods

### Example Function

```python
def send_message(chat_id: int, text: str, *, timeout: float = 10.0) -> None:
    """
    Sends a message to a Telegram chat.

    Args:
        chat_id (int): Target chat ID.
        text (str): Message text (max 4096 characters).
        timeout (float): Request timeout in seconds. Default 10.0.

    Raises:
        ValueError: If chat_id or text is invalid.
        requests.exceptions.RequestException: If the API request fails.
    """
```

### Comments

- Use comments only for complex logic that isn't self-documenting
- Avoid obvious comments like `# increment counter`
- Keep comments up-to-date when modifying code

## Testing Requirements

All code changes must include appropriate tests:

### Writing Tests

1. Place tests in appropriate test files (e.g., `test_huu.py`)
2. Follow the naming convention: `test_<function_name>`
3. Use descriptive test names that explain what is being tested

### Example Test

```python
def test_send_message_empty_text(self):
    """Test that empty message text raises ValueError."""
    bot = Bot(token='validtoken1234', allow_interactive=False)
    with self.assertRaises(ValueError):
        bot.send_message(123, "")
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest test_huu.py -v

# Run specific test
pytest test_huu.py::TestBot::test_send_message_success -v
```

### Test Coverage Expectations

- All public methods should have test coverage
- Include both positive and negative test cases
- Test edge cases and boundary conditions
- Aim for at least 80% code coverage

## Documentation

Documentation is as important as code. Please update relevant documentation when making changes:

### Files to Update

1. **README.md** - For user-facing features and usage examples
2. **Module Docstrings** - For technical details about classes and functions
3. **CHANGELOG.md** - For all significant changes
4. **Code Comments** - For complex logic

### Documentation Style

- Use clear, concise language
- Provide code examples for new features
- Include docstrings with Args, Returns, and Raises sections
- Keep examples runnable and up-to-date

## Pull Request Guidelines

### Before Submitting

1. ✅ **Run tests**: `pytest` (all tests must pass)
2. ✅ **Check code style**: Follow PEP 8 and guidelines above
3. ✅ **Update documentation**: README, docstrings, and CHANGELOG
4. ✅ **Add tests**: Include tests for all new functionality
5. ✅ **Update type hints**: All functions should have type annotations

### PR Title and Description

Use a clear, descriptive PR title:

- ✅ Good: "Add get_user() method for retrieving Telegram user info"
- ❌ Bad: "Fix bug" or "Update code"

Include a detailed description:

```markdown
## Description
Brief explanation of what this PR does.

## Changes
- Added get_user() method
- Added comprehensive tests for user retrieval
- Updated README with usage examples

## Testing
All 30+ tests pass. Added 5 new tests for user retrieval.

## Checklist
- [x] Tests pass
- [x] Documentation updated
- [x] Type hints included
- [x] Code follows PEP 8
```

### Review Process

1. At least one maintainer must review your PR
2. Address any requested changes
3. Update your branch if there are conflicts
4. Once approved, your PR will be merged

## Common Issues and Solutions

### Import Errors

If you see import errors, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Test Failures

If tests fail:

1. Read the error message carefully
2. Run the specific failing test: `pytest test_name.py -v`
3. Check if it's related to your changes
4. Verify your code doesn't break existing functionality

### Type Checking

For type checking, you can use `mypy`:

```bash
pip install mypy
mypy huu.py
```

## Questions?

If you have questions:

- Check existing GitHub issues
- Look at the README and documentation
- Open a new issue with a clear description
- Contact <support@example.com>

## Thank You

Thank you for contributing to VGEE! Your help makes this project better.
