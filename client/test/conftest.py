# Python imports
import logging
from typing import Awaitable, Callable

import pytest

# Project imports
from rubik_cube_websocket_client.client import WebSocketClient


@pytest.fixture
def client():
    """
    Fixture that provides a WebSocketClient instance for testing.
    """

    return WebSocketClient(host="localhost", port=8000, secure=False, api_key="test-key")


@pytest.fixture
def message_handler() -> Callable[[dict], None]:
    """
    Fixture that provides a synchronous message handler for testing.
    """

    def _message_handler(msg: dict) -> None:
        """
        Synchronous message handler for testing.

        :param msg: The incoming message
        """

        logging.info(f"Message handler called with: {msg}")

    return _message_handler


@pytest.fixture
def async_message_handler() -> Callable[[dict], Awaitable[None]]:
    """
    Fixture that provides an asynchronous message handler for testing.
    """

    async def _async_message_handler(msg: dict) -> None:
        """
        Asynchronous message handler for testing.

        :param msg: The incoming message
        """

        logging.info(f"Async message handler called with: {msg}")

    return _async_message_handler
