# Python imports
import os
from unittest.mock import patch

import pytest
from dummy_websocket import DisconnectingWebSocket, RaisingWebSocket, RecordingWebSocket
from fastapi.testclient import TestClient

# Project imports
import server
import utils
from role import Role

client = TestClient(server.app)


@pytest.mark.parametrize("role", [Role.SOLVER, Role.VISUALIZER])
def test_success_get_token(role: Role) -> None:
    """
    Tests the /token endpoint returns a valid JWT when provided a valid API key.

    :param role: The Role to test
    """

    # Request token
    api_key = os.environ.get(f"{role.value}_API_KEY")
    response = client.get("/token", headers={"x-api-key": api_key})

    # Assert response
    assert response.status_code == 200
    token = response.json().get("token")
    assert isinstance(token, str)

    # Assert token payload
    payload = utils.verify_jwt(token)
    assert payload["role"] == role.value
    assert payload["sub"] == f"CLIENT_{role.value}"


def test_exception_get_token_invalid_api_key() -> None:
    """
    Tests the /token endpoint returns 401 when provided an invalid API key.
    """

    # Request token with invalid API key
    response = client.get("/token", headers={"x-api-key": "invalid-key"})

    # Assert response
    assert response.status_code == 401
    assert response.json().get("detail") == "Invalid API key"


@pytest.mark.asyncio
async def test_exception_websocket_invalid_token(recording_websocket: RecordingWebSocket) -> None:
    """
    Tests websocket endpoint closes with 1008 when an invalid token is presented.

    :param recording_websocket: A RecordingWebSocket instance for testing
    """

    with patch(
        "server.utils.verify_jwt", side_effect=utils.HTTPException(status_code=401, detail="Invalid token")
    ) as _mock_verify_jwt:
        # Use an invalid token
        await server.websocket_endpoint(recording_websocket, "not-a-token")

        # Assert
        assert _mock_verify_jwt.call_count == 1
        assert recording_websocket.closed is True
        assert recording_websocket.closed_code == 1008
        assert recording_websocket.closed_reason == "401: Invalid token"


@pytest.mark.asyncio
async def test_exception_websocket_invalid_role(recording_websocket: RecordingWebSocket) -> None:
    """
    Tests websocket endpoint closes with 1008 when an invalid role is provided.

    :param recording_websocket: A RecordingWebSocket instance for testing
    """

    with (
        patch("server.utils.verify_jwt", return_value={"role": "INVALID_ROLE"}) as _mock_verify_jwt,
        patch("server.Role.from_str", side_effect=ValueError("Invalid role")) as _mock_role_from_str,
    ):
        # Use an invalid token
        await server.websocket_endpoint(recording_websocket, "a-token")

        # Assert
        assert _mock_verify_jwt.call_count == 1
        assert _mock_role_from_str.call_count == 1
        assert recording_websocket.closed is True
        assert recording_websocket.closed_code == 1008
        assert recording_websocket.closed_reason == "Invalid role"


@pytest.mark.asyncio
async def test_exception_websocket_invalid_registration(recording_websocket: RecordingWebSocket) -> None:
    """
    Tests websocket endpoint closes with 1008 when an invalid registration occurs.

    :param recording_websocket: A RecordingWebSocket instance for testing
    """

    with (
        patch("server.utils.verify_jwt", return_value={"role": Role.SOLVER.value}) as _mock_verify_jwt,
        patch(
            "server.utils.register_client", side_effect=utils.HTTPException(status_code=401, detail="Invalid token")
        ) as _mock_register_client,
    ):
        # Use an invalid token
        await server.websocket_endpoint(recording_websocket, "a-token")

        # Assert
        assert _mock_verify_jwt.call_count == 1
        assert _mock_register_client.call_count == 1
        assert recording_websocket.closed is True
        assert recording_websocket.closed_code == 1008
        assert recording_websocket.closed_reason == "401: Invalid token"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", [Role.SOLVER, Role.VISUALIZER])
async def test_exception_websocket_disconnect(disconnecting_websocket: DisconnectingWebSocket, role: Role) -> None:
    """
    Tests that websocket_endpoint handles a disconnect of the websocket.

    :param disconnecting_websocket: A DisconnectingWebSocket instance for testing
    :param role: The Role to test
    """

    # Create a valid token
    api_key = os.environ.get(f"{role.value}_API_KEY")
    token = utils.generate_jwt(api_key)

    with (
        patch("server.utils.verify_jwt", return_value={"role": role.value}) as _mock_verify_jwt,
        patch("server.utils.register_client", return_value=None) as _mock_register_client,
        patch("server.utils.unregister_client", return_value=None) as _mock_unregister_client,
    ):
        # Prepopulate the server's clients mapping to simulate a registered client
        server.clients[role] = disconnecting_websocket

        # Run the websocket endpoint - it should register then unregister on disconnect
        await server.websocket_endpoint(disconnecting_websocket, token)

        # Assert mocks called
        assert _mock_verify_jwt.call_count == 1
        assert _mock_register_client.call_count == 1
        assert _mock_unregister_client.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("role", [Role.SOLVER, Role.VISUALIZER])
async def test_exception_websocket_any_error(raising_websocket: RaisingWebSocket, role: Role) -> None:
    """
    Tests that websocket_endpoint handles any Exception raised by the websocket.

    :param raising_websocket: A RaisingWebSocket instance for testing
    :param role: The Role to test
    """

    # Create a valid token
    api_key = os.environ.get(f"{role.value}_API_KEY")
    token = utils.generate_jwt(api_key)

    with (
        patch("server.utils.verify_jwt", return_value={"role": role.value}) as _mock_verify_jwt,
        patch("server.utils.register_client", return_value=None) as _mock_register_client,
    ):
        # Prepopulate the server's clients mapping to simulate a registered client
        server.clients[role] = raising_websocket

        # Run the websocket endpoint - it should register then unregister on disconnect
        await server.websocket_endpoint(raising_websocket, token)

        # Assert mocks called
        assert _mock_verify_jwt.call_count == 1
        assert _mock_register_client.call_count == 1
        assert raising_websocket.closed is True
        assert raising_websocket.closed_code == 1003
