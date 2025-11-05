# Copilot Instructions for VGEE Project

Welcome to the VGEE (Very Good Example Environment) project! This document provides essential guidelines for AI coding agents to be productive in this codebase.

## Project Overview
VGEE is a sample project designed to demonstrate coding practices and testing strategies. The project includes a bot implementation (`main.py`), utility modules (`utils/`), and test cases (`tests/`).

### Key Components
- **`main.py`**: Entry point for the bot. Handles initialization and user interaction.
- **`utils/`**: Contains utility modules:
  - `auth.py`: Handles authentication logic.
  - `decorators.py`: Provides reusable decorators for the project.
- **`tests/`**: Contains test cases for the project:
  - `test_bot.py`: Tests bot functionality.
  - `test_config.py`: Tests configuration logic.
  - `test_huu.py`: Tests specific logic in `huu.py`.
- **`config.py`**: Centralized configuration file for the project.

## Developer Workflows

### Installation
To set up the project, install dependencies using:
```sh
pip install -r requirements.txt
```

### Running the Project
To run the bot:
```sh
python main.py
```
Follow the instructions to enter the token.

### Testing
Run all tests using:
```sh
pytest
```

### Debugging
Use print statements or a debugger (e.g., `pdb`) to debug issues. Key files to debug include `main.py` and modules in `utils/`.

## Project-Specific Conventions
- **Authentication**: Implemented in `utils/auth.py`. Ensure tokens are securely handled.
- **Decorators**: Reusable patterns are defined in `utils/decorators.py`.
- **Testing**: Tests are located in the `tests/` directory. Follow the structure of existing test files.

## Integration Points
- **External Dependencies**: The project relies on `requests` and `pydantic-core`. Ensure these are installed.
- **Cross-Component Communication**: Utility modules (`utils/`) are imported and used in `main.py`.

## Examples
- **Adding a New Utility**:
  1. Create a new file in `utils/`.
  2. Define the required functions/classes.
  3. Import and use the utility in `main.py`.
- **Writing a New Test**:
  1. Add a new test file in `tests/`.
  2. Follow the structure of existing test files.
  3. Use `pytest` to validate the tests.

For further details, refer to the `README.md` file or contact the support team.