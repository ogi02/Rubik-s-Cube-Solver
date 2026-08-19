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

Create a simple client that connects to the server, sends a message, and then closes the connection:

```python
import asyncio
from rubik_cube_websocket_client.client import WebSocketClient


async def main():
    # Connect to the server via WebSocket
    client = WebSocketClient(
        host="127.0.0.1",
        port=8080,
        secure=False,
        api_key="your_api_key_here"
    )

    # Authenticate with the server (HTTP request with API key)
    client.authenticate()

    # Start the WebSocket connection
    task = asyncio.create_task(client.run())

    # Send a message to the server
    await client.send_message({"message": "Hello, Server!"})

    # Close the connection after some time
    await asyncio.sleep(5)
    await client.close()
    
    # Wait for the run task to finish
    await task

asyncio.run(main())
```

Create a simple client with custom message handling:

```python
import asyncio
from rubik_cube_websocket_client.client import WebSocketClient

def custom_message_handler(message: dict):
    print("Custom handler received message:", message)

async def main():
    # Connect to the server via WebSocket
    client = WebSocketClient(
        host="127.0.0.1",
        port=8080,
        secure=False,
        api_key="your_api_key_here",
        message_handler=custom_message_handler
    )

    # Authenticate with the server (HTTP request with API key)
    client.authenticate()

    # Start the WebSocket connection
    task = asyncio.create_task(client.run())

    # Close the connection after some time
    await asyncio.sleep(5)
    await client.close()

    # Wait for the run task to finish
    await task

asyncio.run(main())
```

Create a simple client with asynchronous message handling:

```python
import asyncio
from rubik_cube_websocket_client.client import WebSocketClient

async def custom_message_handler(message: dict):
    # Simulate asynchronous processing
    print("Async custom handler received message:", message)
    await asyncio.sleep(1)
    print("Async processing done.")

async def main():
    # Connect to the server via WebSocket
    client = WebSocketClient(
        host="127.0.0.1",
        port=8080,
        secure=False,
        api_key="your_api_key_here",
        message_handler=custom_message_handler
    )

    # Authenticate with the server (HTTP request with API key)
    client.authenticate()

    # Start the WebSocket connection
    task = asyncio.create_task(client.run())

    # Close the connection after some time
    await asyncio.sleep(5)
    await client.close()

    # Wait for the run task to finish
    await task

asyncio.run(main())
```

## Messages

Every message exchanged over the WebSocket connection is a `{"type": ..., "data": ...}` envelope. The `rubik_cube_websocket_client.messages` module provides builders for every message type so a caller never hand-writes the envelope. The visualizer is receive-only — it only ever sends `disconnect` — and the server validates every relayed message against the contract, dropping anything that does not match it.

### `cube_state`

Sent from the solver to the visualizer to describe the full state of the cube.

- `dimensions` (`int`, >= 2) — the size of the cube, e.g. `3` for a 3x3x3 cube
- `state` (`dict[str, list[str]]`) — maps each of `UP`, `DOWN`, `LEFT`, `RIGHT`, `FRONT`, `BACK` to a list of exactly `dimensions * dimensions` sticker colors

### `apply_moves`

Sent from the solver to the visualizer to animate a sequence of moves.

- `moves` (`list[str]`) — the moves to apply, in cube notation

### `disconnect`

Sent by either client to the server to signal a graceful disconnect. It is never relayed to the other client.

Example usage with `send_message`:

```python
from rubik_cube_websocket_client import messages

await client.send_message(messages.cube_state(
    dimensions=3,
    state={
        "UP": ["white"] * 9,
        "DOWN": ["yellow"] * 9,
        "LEFT": ["orange"] * 9,
        "RIGHT": ["red"] * 9,
        "FRONT": ["green"] * 9,
        "BACK": ["blue"] * 9,
    },
))

await client.send_message(messages.apply_moves(["R", "U", "R'"]))

await client.send_message(messages.disconnect())
```

## Development Setup
Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/ogi02/Rubik-s-Cube-Solver.git
cd Rubik-s-Cube-Solver/client
```

Install the development dependencies, which cover testing, linting, formatting and building:

```bash
pip install -r dev-requirements.txt
```

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

## Building and Publishing
Raise the `version` field in `pyproject.toml` before publishing, since Test PyPI rejects a version that already exists.

Build the package:

```bash
pip install --upgrade build
python -m build
```

Publish to Test PyPI:

```bash
pip install --upgrade twine
python -m twine upload --repository testpypi dist/*
```

## Contact
Author: [Ognian Baruh](https://github.com/ogi02)  
Email: [ognian@baruh.net](mailto:ognian@baruh.net)