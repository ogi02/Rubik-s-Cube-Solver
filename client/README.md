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
    asyncio.create_task(client.run())

    # Send a message to the server
    await client.send_message({"message": "Hello, Server!"})

    # Close the connection after some time
    await asyncio.sleep(5)
    await client.close()

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
    asyncio.create_task(client.run())

    # Close the connection after some time
    await asyncio.sleep(5)
    await client.close()
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
    asyncio.create_task(client.run())

    # Close the connection after some time
    await asyncio.sleep(5)
    await client.close()
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

## Contact
Author: [Ognian Baruh](https://github.com/ogi02)  
Email: [ognian@baruh.net](mailto:ognian@baruh.net)