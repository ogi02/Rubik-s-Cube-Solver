# Rubik's Cube WebSocket Client

[![Lint](https://img.shields.io/github/actions/workflow/status/ogi02/Rubik-s-Cube-Solver/client-lint.yml?branch=main&label=Lint)](https://github.com/ogi02/Rubik-s-Cube-Solver/actions)
[![Pytest](https://img.shields.io/github/actions/workflow/status/ogi02/Rubik-s-Cube-Solver/client-test.yml?branch=main&label=Pytest)](https://github.com/ogi02/Rubik-s-Cube-Solver/actions)
[![Coverage](https://codecov.io/gh/ogi02/Rubik-s-Cube-Solver/branch/main/graph/badge.svg)](https://codecov.io/gh/ogi02/Rubik-s-Cube-Solver)

A Python client for communication with the Rubik's Cube Solver WebSocket server.

The client allows connecting to the server, sending and receiving messages, and handling ping/pong messages to keep the connection alive.

---

## Installation

The package is located in the [Test PyPI repository](https://test.pypi.org/project/rubik-cube-websocket-client/). You can install it using pip:

```bash
pip install -i https://test.pypi.org/simple/ rubik-cube-websocket-client
```

## Examples



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

## Contact
Author: [Ognian Baruh](https://github.com/ogi02)  
Email: [ognian@baruh.net](mailto:ognian@baruh.net)