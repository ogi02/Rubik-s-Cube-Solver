import asyncio
import pytest
from unittest.mock import call, patch, AsyncMock, MagicMock

from typing import Callable, Awaitable

import websockets
from requests import HTTPError

from rubik_cube_websocket_client.client import WebSocketClient


def test_authenticate_success(client: WebSocketClient) -> None:
    """
    Tests successful authentication and token retrieval.

    :param client: The WebSocketClient instance
    """

    with patch("requests.get") as mock_get:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {"token": "jwt-token"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Call authenticate
        client.authenticate()

        # Assert
        assert client.token == "jwt-token"


def test_authenticate_get_request_exception(client: WebSocketClient) -> None:
    """
    Tests authentication failure due to a GET request exception.
    """

    with patch("requests.get") as mock_get:
        # Mock request exception
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = HTTPError("401 Client Error: Unauthorized")
        mock_get.return_value = mock_response

        # Call authenticate
        client.authenticate()

        # Assert
        assert client.token is None


def test_authenticate_json_parsing_exception(client: WebSocketClient) -> None:
    """
    Tests authentication failure due to an exception.
    """

    with patch("requests.get") as mock_get:
        # Mock invalid JSON response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("No JSON object could be decoded")
        mock_get.return_value = mock_response

        # Call authenticate
        client.authenticate()

        # Assert
        assert client.token is None


def test_authenticate_token_missing_exception(client: WebSocketClient) -> None:
    """
    Tests authentication failure due to missing token in response.
    """

    with patch("requests.get") as mock_get:
        # Mock response without token
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        # Call authenticate
        client.authenticate()

        # Assert
        assert client.token is None


@pytest.mark.asyncio
async def test_connect_success(client: WebSocketClient) -> None:
    """
    Tests successful WebSocket connection.

    :param client: The WebSocketClient instance
    """

    client.token = "jwt-token"
    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        # Mock WebSocket connection
        mock_ws = AsyncMock()
        mock_connect.return_value = mock_ws

        # Call _connect
        await client._connect()

        # Assert
        assert client.ws == mock_ws


@pytest.mark.asyncio
async def test_connect_no_token_exception(client: WebSocketClient) -> None:
    """
    Tests WebSocket connection failure due to missing token.

    :param client: The WebSocketClient instance
    """

    client.token = None

    with pytest.raises(ValueError) as exc_info:
        await client._connect()

    assert str(exc_info.value) == "Token is required before connecting"


@pytest.mark.asyncio
async def test_receiver_no_message_handler_success(client: WebSocketClient) -> None:
    """
    Tests the _receiver method for handling incoming messages without a dedicated handler method.

    :param client: The WebSocketClient instance
    """

    with patch("logging.info") as mock_log_info:
        # Mock WebSocket to return a JSON message
        client.ws = AsyncMock()
        client.ws.recv = AsyncMock(side_effect=["{}", asyncio.CancelledError()])

        # Call _receiver
        await client._receiver()

        # Assert
        assert mock_log_info.call_count == 3
        mock_log_info.assert_has_calls([
            call("Received: {}"), call("Received message: {}"), call("Receiver task cancelled")
        ])


@pytest.mark.asyncio
async def test_receiver_with_message_handler_success(
    client: WebSocketClient,
    message_handler: Callable[[dict], None]
) -> None:
    """
    Tests the _receiver method for handling incoming messages with a dedicated handler method.

    :param client: The WebSocketClient instance
    :param message_handler: The synchronous message handler function
    """

    client.message_handler = message_handler

    with patch("logging.info") as mock_log_info:
        # Mock WebSocket to return a JSON message
        client.ws = AsyncMock()
        client.ws.recv = AsyncMock(side_effect=["{}", asyncio.CancelledError()])

        # Call _receiver
        await client._receiver()

        # Assert
        assert mock_log_info.call_count == 3
        mock_log_info.assert_has_calls([
            call("Received: {}"), call("Message handler called with: {}"), call("Receiver task cancelled")
        ])


@pytest.mark.asyncio
async def test_receiver_with_async_message_handler_success(
    client: WebSocketClient,
    async_message_handler: Callable[[dict], Awaitable[None]]
) -> None:
    """
    Tests the _receiver method for handling incoming messages with an asynchronous handler method.

    :param client: The WebSocketClient instance
    :param async_message_handler: The asynchronous message handler function
    """

    client.message_handler = async_message_handler

    with patch("logging.info") as mock_log_info:
        # Mock WebSocket to return a JSON message
        client.ws = AsyncMock()
        client.ws.recv = AsyncMock(side_effect=["{}", asyncio.CancelledError()])

        # Call _receiver
        await client._receiver()

        # Assert
        assert mock_log_info.call_count == 3
        mock_log_info.assert_has_calls([
            call("Received: {}"), call("Async message handler called with: {}"), call("Receiver task cancelled")
        ])


@pytest.mark.asyncio
async def test_receiver_with_non_json_message_success(client: WebSocketClient) -> None:
    """
    Tests the _receiver method for handling incoming non-JSON messages.

    :param client: The WebSocketClient instance
    """

    with patch("logging.info") as mock_log_info:
        # Mock WebSocket to return a non-JSON message
        client.ws = AsyncMock()
        client.ws.recv = AsyncMock(side_effect=["Non-JSON message", asyncio.CancelledError()])

        # Call _receiver
        await client._receiver()

        # Assert
        assert mock_log_info.call_count == 3
        mock_log_info.assert_has_calls([
            call("Non-JSON message received: Non-JSON message"),
            call("Received message: Non-JSON message"),
            call("Receiver task cancelled")
        ])


@pytest.mark.asyncio
async def test_receiver_connection_closed_success(client: WebSocketClient) -> None:
    """
    Tests the _receiver method for handling ConnectionClosed exception.

    :param client: The WebSocketClient instance
    """

    with patch("logging.info") as mock_log_info:
        # Mock WebSocket to raise ConnectionClosed
        client.ws = AsyncMock()
        client.ws.recv = AsyncMock(side_effect=websockets.exceptions.ConnectionClosed(None, None))

        # Call _receiver
        await client._receiver()

        # Assert
        mock_log_info.assert_called_once_with("Connection closed during receive")


@pytest.mark.asyncio
async def test_receiver_asyncio_cancelled_success(client: WebSocketClient) -> None:
    """
    Tests the _receiver method for handling cancel from asyncio.

    :param client: The WebSocketClient instance
    """

    with patch("logging.info") as mock_log_info:
        # Mock WebSocket to raise ConnectionClosed
        client.ws = AsyncMock()
        client.ws.recv = AsyncMock(side_effect=asyncio.CancelledError())

        # Call _receiver
        await client._receiver()

        # Assert
        mock_log_info.assert_called_once_with("Receiver task cancelled")


@pytest.mark.asyncio
async def test_sender_success(client: WebSocketClient) -> None:
    """
    Tests the _sender method for sending messages.

    :param client: The WebSocketClient instance
    """

    with patch("logging.info") as mock_log_info:
        # Mock WebSocket
        client.ws = AsyncMock()
        client.ws.send = AsyncMock()

        # Put messages in send queue
        await client.send_queue.put({"key": "value"})
        await client.send_queue.put(None)

        # Call _sender
        await client._sender()

        # Assert
        client.ws.send.assert_called_once_with('{"key": "value"}')
        mock_log_info.assert_not_called()


@pytest.mark.asyncio
async def test_sender_connection_closed_success(client: WebSocketClient) -> None:
    """
    Tests the _sender method for handling ConnectionClosed exception.

    :param client: The WebSocketClient instance
    """

    with patch("logging.info") as mock_log_info:
        # Mock WebSocket to raise ConnectionClosed
        client.ws = AsyncMock()
        client.ws.send = AsyncMock(side_effect=websockets.exceptions.ConnectionClosed(None, None))

        # Put a message in send queue
        await client.send_queue.put({"key": "value"})

        # Call _sender
        await client._sender()

        # Assert
        mock_log_info.assert_called_once_with("Connection closed during send")


@pytest.mark.asyncio
async def test_sender_asyncio_cancelled_success(client: WebSocketClient) -> None:
    """
    Tests the _sender method for handling cancel from asyncio.

    :param client: The WebSocketClient instance
    """

    with patch("logging.info") as mock_log_info:
        # Mock WebSocket to raise ConnectionClosed
        client.ws = AsyncMock()
        client.ws.send = AsyncMock(side_effect=asyncio.CancelledError())

        # Put a message in send queue
        await client.send_queue.put({"key": "value"})

        # Call _sender
        await client._sender()

        # Assert
        mock_log_info.assert_called_once_with("Sender task cancelled")


@pytest.mark.asyncio
async def test_pinger_success(client: WebSocketClient) -> None:
    """
    Tests the _pinger method for sending pings.

    :param client: The WebSocketClient instance
    """

    with (
        patch("logging.info") as mock_log_info,
        patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep
    ):
        # Mock WebSocket
        client.ws = AsyncMock()
        future = asyncio.Future()
        future.set_result(None)
        client.ws.ping = AsyncMock(side_effect=[future, asyncio.CancelledError()])

        # Mock sleep to avoid actual delay
        mock_sleep.return_value = None

        # Call _pinger (run only one iteration)
        await client._pinger()

        # Assert
        assert mock_log_info.call_count == 2
        mock_log_info.assert_has_calls([
            call("Ping successful"), call("Ping task cancelled")
        ])


@pytest.mark.asyncio
async def test_pinger_connection_closed_success(client: WebSocketClient) -> None:
    """
    Tests the _pinger method for handling ConnectionClosed exception.

    :param client: The WebSocketClient instance
    """

    with (
        patch("logging.info") as mock_log_info,
        patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep
    ):
        # Mock WebSocket to raise ConnectionClosed
        client.ws = AsyncMock()
        client.ws.ping = AsyncMock(side_effect=websockets.exceptions.ConnectionClosed(None, None))

        # Mock sleep to avoid actual delay
        mock_sleep.return_value = None

        # Call _pinger
        await client._pinger()

        # Assert
        mock_log_info.assert_called_once_with("Connection closed during ping")


@pytest.mark.asyncio
async def test_pinger_asyncio_cancelled_success(client: WebSocketClient) -> None:
    """
    Tests the _pinger method for handling cancel from asyncio.

    :param client: The WebSocketClient instance
    """

    with (
        patch("logging.info") as mock_log_info,
        patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep
    ):
        # Mock WebSocket to raise ConnectionClosed
        client.ws = AsyncMock()
        client.ws.ping = AsyncMock(side_effect=asyncio.CancelledError())

        # Mock sleep to avoid actual delay
        mock_sleep.return_value = None

        # Call _pinger
        await client._pinger()

        # Assert
        mock_log_info.assert_called_once_with("Ping task cancelled")


@pytest.mark.asyncio
async def test_run_success(client: WebSocketClient) -> None:
    """
    Tests the run method for running the client.

    :param client: The WebSocketClient instance
    """

    with (
        patch.object(client, "_connect", new_callable=AsyncMock) as mock_connect,
        patch.object(client, "_receiver", new_callable=AsyncMock) as mock_receiver,
        patch.object(client, "_sender", new_callable=AsyncMock) as mock_sender,
        patch.object(client, "_pinger", new_callable=AsyncMock) as mock_pinger,
        patch("logging.info") as mock_log_info
    ):
        # Mock WebSocket
        client.ws = AsyncMock()
        client.ws.close = AsyncMock()

        # Mock one task to complete immediately
        mock_receiver.side_effect = asyncio.CancelledError()

        # Call run
        await client.run()

        # Assert
        mock_connect.assert_awaited_once()
        mock_receiver.assert_awaited_once()
        mock_sender.assert_awaited_once()
        mock_pinger.assert_awaited_once()
        client.ws.close.assert_awaited_once()
        mock_log_info.assert_called_once_with("Disconnected")


@pytest.mark.asyncio
async def test_send_message(client: WebSocketClient) -> None:
    """
    Tests the send_message method for enqueuing messages.

    :param client: The WebSocketClient instance
    """

    # Initialize send queue
    client.send_queue = asyncio.Queue()

    # Call send_message
    await client.send_message({"foo": "bar"})

    # Assert
    msg = await client.send_queue.get()
    assert msg == {"foo": "bar"}


@pytest.mark.asyncio
async def test_close(client: WebSocketClient) -> None:
    """
    Tests the close method for closing the client.

    :param client: The WebSocketClient instance
    """

    # Initialize send queue
    client.send_queue = asyncio.Queue()

    # Call close
    await client.close()

    # Assert
    msg = await client.send_queue.get()
    assert msg is None
