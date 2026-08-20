# Rubik's Cube WebSocket Server

[![Lint](https://img.shields.io/github/actions/workflow/status/ogi02/Rubik-s-Cube-Solver/server-lint.yml?branch=main&label=Lint)](https://github.com/ogi02/Rubik-s-Cube-Solver/actions)
[![Pytest](https://img.shields.io/github/actions/workflow/status/ogi02/Rubik-s-Cube-Solver/server-test.yml?branch=main&label=Pytest)](https://github.com/ogi02/Rubik-s-Cube-Solver/actions)
[![Coverage](https://codecov.io/gh/ogi02/Rubik-s-Cube-Solver/branch/main/graph/badge.svg)](https://codecov.io/gh/ogi02/Rubik-s-Cube-Solver)

A Python server for communication with a Rubik's Cube visualizer application and a Rubik's Cube solving machine.

The server supports 1 visualizer client and 1 solver client simultaneously.

---

## Installation

Clone the repository and install the requirements:

```bash
git clone https://github.com/ogi02/Rubik-s-Cube-Solver.git
cd Rubik-s-Cube-Solver/server
pip install -r requirements.txt
```

Optionally, install the server as an editable package:

```bash
pip install -e .
```

## Run the Server

To start the server, run:

```bash
cd src
python server.py
```

## Server Setup

The server is a FastAPI application, which consists of an HTTP authorization endpoint and a WebSocket communication endpoint.
It keeps track of the connected clients and forwards messages between them.
It supports "ping/pong" messages to keep the connections alive.

## Authorization

Clients must first obtain an authorization token by sending a GET request to the `/token` endpoint with an API key in the request headers.
There are two API keys: one for the visualizer client and one for the solver client.
Based on the provided API key, the server issues a token that identifies the client type.

When connecting to the WebSocket endpoint, clients must provide the obtained token for authentication.

## WebSocket Communication

Clients connect to the WebSocket endpoint at `/ws` using the token obtained from the authorization step.
The server maintains the connection and forwards messages between the visualizer and solver clients.

The server supports ping/pong messages to keep the connection alive.
Every client should periodically send a ping message to the server:
```py
await websocket.ping()
```

### Message Envelope

Every message is a JSON object with a `type` field naming the message and a `data` field holding
its payload:

```json
{
  "type": "message_type",
  "data": {}
}
```

The server validates every message it is asked to relay against the specification below.
An invalid message is logged and dropped — the connection is kept open, but the message never
reaches the visualizer. The visualizer is receive-only: it never sends any message type other
than `disconnect`.

### `cube_state`

- **Direction:** solver -> visualizer
- **When:** sent by the solver whenever it wants the visualizer to display a full cube state.
- **Payload fields:**
  - `dimensions` (`int`, `>= 2`): the size of the cube, e.g. `3` for a 3x3x3 cube.
  - `state` (`dict`): maps each of the six side names `UP`, `DOWN`, `LEFT`, `RIGHT`, `FRONT`,
    `BACK` to a list of `str` stickers. Every list must have exactly `dimensions * dimensions`
    entries, and no side may be missing or extra.

```json
{
  "type": "cube_state",
  "data": {
    "dimensions": 2,
    "state": {
      "UP": ["W", "W", "W", "W"],
      "DOWN": ["Y", "Y", "Y", "Y"],
      "LEFT": ["O", "O", "O", "O"],
      "RIGHT": ["R", "R", "R", "R"],
      "FRONT": ["G", "G", "G", "G"],
      "BACK": ["B", "B", "B", "B"]
    }
  }
}
```

### `apply_moves`

- **Direction:** solver -> visualizer
- **When:** sent by the solver to instruct the visualizer to animate a sequence of moves.
- **Payload fields:**
  - `moves` (`list` of `str`): the moves to apply, in order. An empty list is valid.

```json
{
  "type": "apply_moves",
  "data": {
    "moves": ["R", "U", "R'", "U'"]
  }
}
```

### `disconnect`

- **Direction:** solver or visualizer -> server
- **When:** sent by either client to notify the server it is disconnecting.
- **Payload fields:** none. This message is consumed by the server and is never relayed to the
  other client.

```json
{
  "type": "disconnect"
}
```

## Client Example

Obtain token:

```python
import requests

SERVER_URL = "http://localhost:8000"
API_KEY = "your_api_key_here"

response = requests.get(f"{SERVER_URL}/token", headers={"x-api-key": API_KEY})
token = response.json()["token"]
```

Connect to WebSocket:

```python
import websockets

WEBSOCKET_URL = "ws://localhost:8000/ws"
token = "your_obtained_token_here"

async with websockets.connect(f"{WEBSOCKET_URL}?token={token}") as ws:
    pass
```

Send messages:

```python
import asyncio
import json
from websockets import ClientConnection

PROMPT = "Enter message (type 'exit' to quit):\n"

ws: ClientConnection 
async def sender():
    """
    Send messages to the WebSocket server based on user input.
    Handles 'exit' command to terminate the connection.
    """

    while True:
        msg = await asyncio.to_thread(input, PROMPT)
        if msg.lower() == "exit":
            break
        await ws.send(json.dumps(msg))
```

Receive messages:

```python
import json
from websockets import ClientConnection, ConnectionClosed

ws: ClientConnection 
async def receiver():
    """
    Receive messages from the WebSocket server.
    Handles incoming messages and logs them. Handles connection closure.
    """

    while True:
        try:
            msg = await ws.recv()
            try:
                data = json.loads(msg)
                print(data)
            except json.JSONDecodeError as e:
                pass
        except ConnectionClosed:
            break
```

Ping the server:

```python
import asyncio
from websockets import ClientConnection, ConnectionClosed

ws: ClientConnection
async def pinger():
    """
    Send periodic pings to keep the WebSocket connection alive.
    Logs the success of each ping.
    """

    while True:
        await asyncio.sleep(30)
        try:
            pong = await ws.ping()
            await pong
        except ConnectionClosed:
            break
```

A full example client can be found in the `src/example_client.py` file.

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