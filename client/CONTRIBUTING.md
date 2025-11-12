# Contributing to Rubik's Cube WebSocket Client

Thank you for your interest in contributing! Please follow these guidelines to help us maintain code quality and reliability.

---

## Development Setup

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/ogi02/Rubik-s-Cube-Solver.git
cd Rubik-s-Cube-Solver/client
```

Install the development dependencies:

```bash
pip install -r dev-requirements.txt
```

The development requirements include tools for testing, linting, code formatting and building.

Optionally, install the client in editable mode:

```bash
pip install -e .
```

## Testing

Run all tests with coverage:

```bash
pip install -r dev-requirements.txt
pytest --cov=src --cov-branch --cov-report=xml
```

## Code Quality

All code formatting, linting, and import sorting are handled with pre-commit hooks.

Install pre-commit and enable hooks:

```bash
pip install -r dev-requirements.txt
pre-commit install
pre-commit run --all-files
```

## Build and Publish Instructions

Build the Package:

```bash
pip install --upgrade build
python -m build
```

Publish to Test PyPI:

```bash
pip install --upgrade twine
twine upload --repository testpypi dist/*
```

## Submitting Changes

Please follow these steps to contribute your changes:

```text
1. Fork the repository and create a new branch for your feature or bug fix.
2. Make your changes and ensure all tests pass.
3. Commit your changes with clear messages.
4. Push your branch to your forked repository.
5. Open a pull request against the main repository.
6. Describe your changes and link any relevant issues.
7. Wait for code review and address any feedback.
8. Once approved, your changes will be merged.
9. Delete your branch after the pull request is merged.
10. Celebrate your contribution!
```

## Contact
For questions, open an issue or contact [Ognian Baruh](mailto:ognian@baruh.net).