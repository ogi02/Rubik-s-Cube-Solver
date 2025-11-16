# Python imports
import asyncio
import json
import logging
from typing import Any, Awaitable, Callable, Union

import requests
import websockets

logging.basicConfig(
    level=logging.INFO,
    format="[Client] %(asctime)s [%(levelname)s] %(filename)s:%(lineno)d — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

MessageHandler = Union[Callable[[dict], Any], Callable[[dict], Awaitable[Any]]]


class WebSocketClient:
    def __init__(self, host: str, port: int, secure: bool, api_key: str, message_handler: MessageHandler = None):
        """
        Initialize the WebSocket client.

        :param host: The server host.
        :param port: The server port.
        :param secure: Whether to use secure connection (https/wss).
        :param api_key: The API key for authentication.
        :param message_handler: Optional callable to handle incoming messages.
        """

        # Client configuration
        self.host = host
        self.port = port
        self.secure = secure
        self.http_url = f"http{'s' if secure else ''}://{host}:{port}"
        self.ws_url = f"ws{'s' if secure else ''}://{host}:{port}/ws"

        # Authentication
        self.api_key = api_key
        self.token: str | None = None

        # WebSocket connection and tasks
        self.ws: websockets.ClientConnection | None = None
        self.tasks: set[asyncio.Task] = set()
        self.send_queue: asyncio.Queue = asyncio.Queue()
        self.message_handler = message_handler or (lambda msg: logging.info(f"Received message: {msg}"))

    def authenticate(self):
        """
        Authenticate with the server to obtain a JWT token.
        """

        try:
            response = requests.get(f"{self.http_url}/token", headers={"x-api-key": self.api_key}, timeout=5)
            response.raise_for_status()
            response_json = response.json()
            self.token = response_json["token"]
        except requests.RequestException as e:
            logging.error(f"Failed to get token from server: {e}")
        except (ValueError, KeyError) as e:
            logging.error(f"Invalid response from server when requesting token: {e}")

    async def _connect(self):
        """
        Connect to the WebSocket server using the JWT token.
        """

        if not self.token:
            raise ValueError("Token is required before connecting")

        self.ws = await websockets.connect(f"{self.ws_url}?token={self.token}")
        logging.info("Connected")

    async def _receiver(self):
        """
        Receive messages from the WebSocket server.
        Handles incoming messages and logs them.
        Handles connection closure.
        Handles asyncio task cancellation.
        """

        try:
            while True:
                msg = await self.ws.recv()
                try:
                    data = json.loads(msg)
                    logging.info(f"Received: {data}")
                except json.JSONDecodeError:
                    data = msg
                    logging.info(f"Non-JSON message received: {data}")
                # Call the message handler if provided
                if asyncio.iscoroutinefunction(self.message_handler):
                    await self.message_handler(data)
                else:
                    self.message_handler(data)
        except websockets.ConnectionClosed:
            logging.info("Connection closed during receive")
        except asyncio.CancelledError:
            logging.info("Receiver task cancelled")

    async def _sender(self):
        """
        Send messages to the WebSocket server from the send queue.
        Handles connection closure.
        Handles asyncio task cancellation.
        """

        try:
            while True:
                msg = await self.send_queue.get()
                # Sentinel to stop the sender
                if msg is None:
                    break
                await self.ws.send(json.dumps(msg))
        except websockets.ConnectionClosed:
            logging.info("Connection closed during send")
        except asyncio.CancelledError:
            logging.info("Sender task cancelled")

    async def _pinger(self):
        """
        Send periodic pings to keep the WebSocket connection alive.
        Logs the success of each ping.
        Handles connection closure.
        Handles asyncio task cancellation.
        """

        try:
            while True:
                await asyncio.sleep(30)
                pong = await self.ws.ping()
                await pong
                logging.info("Ping successful")
        except websockets.ConnectionClosed:
            logging.info("Connection closed during ping")
        except asyncio.CancelledError:
            logging.info("Ping task cancelled")

    async def run(self):
        """
        Run the WebSocket client by connecting and starting receiver, sender, and pinger tasks.
        Waits until any task completes, then cancels the others and closes the connection.
        """

        await self._connect()

        # Start tasks
        self.tasks = {
            asyncio.create_task(self._receiver()),
            asyncio.create_task(self._sender()),
            asyncio.create_task(self._pinger()),
        }

        # Wait until any task completes
        done, pending = await asyncio.wait(self.tasks, return_when=asyncio.FIRST_COMPLETED)

        # Cancel remaining tasks
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)

        # Close websocket
        await self.ws.close()
        logging.info("Disconnected")

    async def send_message(self, msg: dict):
        """
        External method to enqueue a message to send.

        :param msg: The message dictionary to send.
        """

        await self.send_queue.put(msg)

    async def close(self):
        """
        Gracefully stop the sender by sending a sentinel.
        """

        await self.send_queue.put(None)
