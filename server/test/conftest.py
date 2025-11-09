# Python imports
import importlib
from typing import Callable

import pytest
from dummy_websocket import DisconnectingWebSocket, DummyWebSocket, RaisingWebSocket, RecordingWebSocket

# Project imports
from role import Role


@pytest.fixture
def websocket() -> DummyWebSocket:
    """
    Provides a fresh DummyWebSocket for tests.
    """

    return DummyWebSocket()


@pytest.fixture
def recording_websocket() -> RecordingWebSocket:
    """
    Provides a fresh RecordingWebSocket for tests.
    """

    return RecordingWebSocket()


@pytest.fixture
def disconnecting_websocket() -> DisconnectingWebSocket:
    """
    Provides a fresh DisconnectingWebSocket for tests.
    """

    return DisconnectingWebSocket()


@pytest.fixture
def raising_websocket() -> RaisingWebSocket:
    """
    Provides a fresh RaisingWebSocket for tests.
    """

    return RaisingWebSocket()


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


@pytest.fixture
def jwt_secret() -> str:
    """
    Provides a test JWT secret.
    """

    return "test-jwt-secret"


@pytest.fixture
def solver_api_key() -> str:
    """
    Provides a test solver API key.
    """

    return "test-solver-api-key"


@pytest.fixture
def visualizer_api_key() -> str:
    """
    Provides a test visualizer API key.
    """

    return "test-visualizer-api-key"


@pytest.fixture(autouse=True)
def set_up_environment(
    monkeypatch: pytest.MonkeyPatch, jwt_secret: str, solver_api_key: str, visualizer_api_key: str
) -> None:
    """
    Sets up required environment variables for tests.

    :param monkeypatch: The pytest monkeypatch fixture.
    :param jwt_secret: The test JWT secret.
    :param solver_api_key: The test solver API key.
    :param visualizer_api_key: The test visualizer API key.
    """

    # Set required environment variables
    monkeypatch.setenv("JWT_SECRET", jwt_secret)
    monkeypatch.setenv("SOLVER_API_KEY", solver_api_key)
    monkeypatch.setenv("VISUALIZER_API_KEY", visualizer_api_key)

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
