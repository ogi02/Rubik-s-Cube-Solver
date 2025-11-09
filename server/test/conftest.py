# Python imports
import importlib
from typing import Callable

import pytest
from starlette.websockets import WebSocket

# Project imports
from role import Role


async def dummy_receive() -> dict:
    """
    A dummy receive function for the DummyWebSocket
    """

    return {"type": "websocket.connect"}


async def dummy_send(data) -> None:
    """
    A dummy send function for the DummyWebSocket

    :param data: The data to send
    """

    pass


class DummyWebSocket(WebSocket):
    """
    A minimal websocket stub that records sent json payloads.
    """

    def __init__(self) -> None:
        """
        Initializes the DummyWebSocket.
        """
        scope = {
            "type": "websocket",
            "asgi": {"version": "3.0"},
            "scheme": "ws",
            "path": "/",
            "headers": [],
            "query_string": b"",
            "client": ("testclient", 12345),
            "server": ("testserver", 80),
            "subprotocols": [],
        }
        super().__init__(scope=scope, receive=dummy_receive, send=dummy_send)
        self.sent: list = []

    async def send_json(self, data, mode: str = "test", **kwargs) -> None:
        """
        Records the JSON data.

        :param data: The JSON data to record.
        :param mode: The mode of sending (default is "test").
        :param kwargs: Additional keyword arguments.
        """
        self.sent.append(data)


@pytest.fixture
def websocket() -> DummyWebSocket:
    """
    Provides a fresh DummyWebSocket for tests.
    """

    return DummyWebSocket()


@pytest.fixture
def known_clients() -> dict[Role, DummyWebSocket]:
    """
    Provides a mapping for all roles to DummyWebSocket.
    """

    return {Role.SOLVER: DummyWebSocket(), Role.VISUALIZER: DummyWebSocket()}


@pytest.fixture
def empty_known_clients() -> dict[Role, DummyWebSocket]:
    """
    Provides an empty mapping for known clients.
    """

    return {}


@pytest.fixture(autouse=True)
def set_up_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Sets up required environment variables for tests.

    :param monkeypatch: The pytest monkeypatch fixture.
    """

    # Set required environment variables
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret")
    monkeypatch.setenv("SOLVER_API_KEY", "test-solver-api-key")
    monkeypatch.setenv("VISUALIZER_API_KEY", "test-visualizer-api-key")

    # Reload config module to pick up the patched environment variables
    import config as _config

    importlib.reload(_config)


@pytest.fixture
def update_env_variable() -> Callable[[pytest.MonkeyPatch, str, str], None]:
    """
    Returns a method to monkey patch an environmental variable in the utils module for testing.

    :return: The callable method
    """

    def _update(monkeypatch, name: str, value: str | None) -> None:
        """
        Monkey patches an environmental variable in the utils module for testing.

        :param monkeypatch: The pytest monkeypatch fixture.
        :param name: The name of the environment variable to set.
        :param value: The value to set SOLVER_API_KEY to.
        """

        # Set the requested variable
        monkeypatch.setenv(name, value)

        # Reload modules that read environment variables at import time so they pick up the patched values
        import config as _config

        importlib.reload(_config)
        import utils as _utils

        importlib.reload(_utils)

    return _update
