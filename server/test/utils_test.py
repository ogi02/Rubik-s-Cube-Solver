# Python imports
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Callable

import pytest
from dummy_websocket import DummyWebSocket
from fastapi import HTTPException

# Project imports
import utils
from role import Role


# fmt: off
@pytest.mark.parametrize(
    "api_key_name, api_key_value, expected_role", [
        ("SOLVER_API_KEY",     "solver_key",     Role.SOLVER),
        ("VISUALIZER_API_KEY", "visualizer_key", Role.VISUALIZER),
    ]
)
# fmt: on
def test_generate_and_verify_jwt_token_success(
    update_env_variable: Callable[[pytest.MonkeyPatch, str, str], None],
    api_key_name: str,
    api_key_value: str,
    expected_role: Role,
) -> None:
    """
    Tests that generate_jwt returns a token containing the expected role claim.

    :param update_env_variable: Fixture to update environment variables
    :param api_key_name: The name of the API key to update
    :param api_key_value: The value of the API key to set
    :param expected_role: The expected Role encoded in the token
    """

    with pytest.MonkeyPatch.context() as monkeypatch:
        # Update the API key in the utils module
        update_env_variable(monkeypatch, api_key_name, api_key_value)

        # Generate the JWT token
        token = utils.generate_jwt(api_key_value)

        # Verify the token
        payload = utils.verify_jwt(token)

    # Assert
    assert isinstance(token, str)
    assert payload["role"] == expected_role.value
    assert payload["sub"] == f"CLIENT_{expected_role.value}"
    assert isinstance(payload["exp"], int)


def test_generate_jwt_invalid_key_exception() -> None:
    """
    Tests that generate_jwt raises HTTPException for invalid API keys.
    """

    with pytest.raises(HTTPException):
        utils.generate_jwt("bad-key")


def test_generate_jwt_invalid_key_not_logged(caplog: pytest.LogCaptureFixture) -> None:
    """
    Tests that generate_jwt's rejection log does not contain the supplied invalid API key.

    :param caplog: Fixture to capture log records
    """

    bad_key = "super-secret-bad-key"

    with caplog.at_level(logging.ERROR):
        with pytest.raises(HTTPException):
            utils.generate_jwt(bad_key)

    # Assert the log does not leak the supplied key
    assert bad_key not in caplog.text


def test_generate_jwt_token_expiry_seconds(solver_api_key: str) -> None:
    """
    Tests that generate_jwt issues a token whose expiry is JWT_LIFETIME (60 seconds) after generation.

    :param solver_api_key: Fixture providing the test solver API key
    """

    before = int(datetime.now(timezone.utc).timestamp())
    token = utils.generate_jwt(solver_api_key)
    after = int(datetime.now(timezone.utc).timestamp())

    payload = utils.verify_jwt(token)

    # Assert the configured lifetime is 60 seconds
    assert utils.JWT_LIFETIME == timedelta(seconds=60)

    # Assert the expiry claim is exactly JWT_LIFETIME after generation
    assert before + int(utils.JWT_LIFETIME.total_seconds()) <= payload["exp"]
    assert payload["exp"] <= after + int(utils.JWT_LIFETIME.total_seconds())


def test_verify_jwt_invalid_token_exception() -> None:
    """
    Tests that verify_jwt raises HTTPException for invalid tokens.
    """

    with pytest.raises(HTTPException):
        utils.verify_jwt("not-a-token")


@pytest.mark.asyncio
@pytest.mark.parametrize("role", [Role.SOLVER, Role.VISUALIZER])
async def test_register_client_success(
    empty_known_clients: dict[Role, DummyWebSocket], websocket: DummyWebSocket, role: Role
) -> None:
    """
    Tests that register_client adds the websocket to known_clients.

    :param empty_known_clients: Fixture providing an empty known_clients mapping
    :param websocket: Fixture providing a DummyWebSocket
    :param role: The role to register
    """

    # Create lock
    clients_lock = asyncio.Lock()

    # Register the client
    await utils.register_client(role, websocket, empty_known_clients, clients_lock)

    # Assert
    assert role in empty_known_clients
    assert empty_known_clients[role] is websocket


@pytest.mark.asyncio
@pytest.mark.parametrize("role", [Role.SOLVER, Role.VISUALIZER])
async def test_register_client_already_registered_exception(
    known_clients: dict[Role, DummyWebSocket], websocket: DummyWebSocket, role: Role
) -> None:
    """
    Tests that register_client raises HTTPException if the role is already registered.

    :param known_clients: Fixture providing a known_clients mapping with both roles registered
    :param websocket: Fixture providing a DummyWebSocket
    :param role: The role to attempt to register again
    """

    # Create lock
    clients_lock = asyncio.Lock()

    # Attempt to register the client again
    with pytest.raises(HTTPException):
        await utils.register_client(role, websocket, known_clients, clients_lock)


@pytest.mark.asyncio
@pytest.mark.parametrize("role", [Role.SOLVER, Role.VISUALIZER])
async def test_unregister_client_success(known_clients: dict[Role, DummyWebSocket], role: Role) -> None:
    """
    Tests that unregister_client removes the websocket from known_clients.

    :param known_clients: Fixture providing a known_clients mapping with both roles registered
    :param role: The role to unregister
    """

    # Create lock
    clients_lock = asyncio.Lock()

    # Unregister the client
    await utils.unregister_client(role, known_clients, clients_lock)

    # Assert
    assert role not in known_clients


# fmt: off
@pytest.mark.parametrize(
    "message", [
        {"type": "apply_moves", "data": {"moves": ["R", "U", "R'", "U'"]}},
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
                    "BACK": ["B", "B", "B", "B"],
                },
            },
        },
    ]
)
# fmt: on
@pytest.mark.asyncio
async def test_handle_message_success(message: dict, known_clients: dict[Role, DummyWebSocket]) -> None:
    """
    Tests that handle_message routes a valid solver message to the visualizer.

    :param message: A valid solver message
    :param known_clients: Fixture mapping roles to websocket stubs
    """

    # Handle the message
    await utils.handle_message(message, known_clients, Role.SOLVER)

    # Assert the visualizer received the message
    assert known_clients[Role.VISUALIZER].sent == [message]

    # Assert the solver did not receive any message
    assert known_clients[Role.SOLVER].sent == []


@pytest.mark.asyncio
async def test_handle_message_no_recipient_success(known_clients: dict[Role, DummyWebSocket]) -> None:
    """
    Tests that handle_message does not route the message if the visualizer is not connected.

    :param known_clients: Fixture mapping roles to websocket stubs
    """

    message = {"type": "apply_moves", "data": {"moves": []}}

    # Remove the visualizer to simulate it not being connected
    del known_clients[Role.VISUALIZER]

    # Handle the message from the solver
    await utils.handle_message(message, known_clients, Role.SOLVER)

    # Assert no messages were sent
    assert known_clients[Role.SOLVER].sent == []


@pytest.mark.asyncio
async def test_handle_message_invalid_sender_dropped_success(
    caplog: pytest.LogCaptureFixture, known_clients: dict[Role, DummyWebSocket]
) -> None:
    """
    Tests that handle_message drops a message from a non-solver sender, keeping the connection
    open (no exception raised) and logging a warning naming the sender role.

    :param caplog: Fixture to capture log records
    :param known_clients: Fixture mapping roles to websocket stubs
    """

    message = {"type": "apply_moves", "data": {"moves": []}}

    with caplog.at_level(logging.WARNING):
        # Handle the message from the visualizer, which is not permitted to send apply_moves
        await utils.handle_message(message, known_clients, Role.VISUALIZER)

    # Assert no messages were sent
    assert known_clients[Role.SOLVER].sent == []
    assert known_clients[Role.VISUALIZER].sent == []

    # Assert a warning was logged naming the sender role
    assert any("VISUALIZER" in record.message for record in caplog.records)


@pytest.mark.asyncio
async def test_handle_message_invalid_payload_dropped_success(
    caplog: pytest.LogCaptureFixture, known_clients: dict[Role, DummyWebSocket]
) -> None:
    """
    Tests that handle_message drops a malformed solver message, keeping the connection open
    (no exception raised) so nothing invalid reaches the visualizer.

    :param caplog: Fixture to capture log records
    :param known_clients: Fixture mapping roles to websocket stubs
    """

    message = {"type": "apply_moves", "data": {"moves": "not-a-list"}}

    with caplog.at_level(logging.WARNING):
        # Handle the malformed message from the solver
        await utils.handle_message(message, known_clients, Role.SOLVER)

    # Assert no messages were sent
    assert known_clients[Role.SOLVER].sent == []
    assert known_clients[Role.VISUALIZER].sent == []

    # Assert a warning was logged naming the sender role
    assert any("SOLVER" in record.message for record in caplog.records)
