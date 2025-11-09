# Python imports
import asyncio
from typing import Callable

import pytest
from conftest import DummyWebSocket
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
def test_success_generate_and_verify_jwt_token(
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


def test_exception_generate_jwt_invalid_key() -> None:
    """
    Tests that generate_jwt raises HTTPException for invalid API keys.
    """

    with pytest.raises(HTTPException):
        utils.generate_jwt("bad-key")


def test_exception_verify_jwt_invalid_token() -> None:
    """
    Tests that verify_jwt raises HTTPException for invalid tokens.
    """

    with pytest.raises(HTTPException):
        utils.verify_jwt("not-a-token")


@pytest.mark.asyncio
@pytest.mark.parametrize("role", [Role.SOLVER, Role.VISUALIZER])
async def test_success_register_client(
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
async def test_exception_register_client_already_registered(
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
async def test_success_unregister_client(known_clients: dict[Role, DummyWebSocket], role: Role) -> None:
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
    "sender_role, recipient_role", [
        (Role.SOLVER,     Role.VISUALIZER),
        (Role.VISUALIZER, Role.SOLVER),
    ]
)
# fmt: on
@pytest.mark.asyncio
async def test_success_handle_message(
        sender_role: Role, recipient_role: Role, known_clients: dict[Role, DummyWebSocket]
) -> None:
    """
    Tests that handle_message routes the message to the opposite role's websocket.

    :param sender_role: The Role enum member sending the message
    :param recipient_role: The Role enum member expected to receive the message
    :param known_clients: Fixture mapping roles to websocket stubs
    """

    message = {"message": "test_message"}

    # Handle the message
    await utils.handle_message(message, known_clients, sender_role)

    # Assert the recipient received the message
    assert known_clients[recipient_role].sent == [message]

    # Assert the sender did not receive any message
    assert known_clients[sender_role].sent == []


# fmt: off
@pytest.mark.parametrize(
    "sender_role, recipient_role", [
        (Role.SOLVER,     Role.VISUALIZER),
        (Role.VISUALIZER, Role.SOLVER),
    ]
)
# fmt: on
@pytest.mark.asyncio
async def test_handle_message_no_recipient(
        sender_role: Role, recipient_role: Role, known_clients: dict[Role, DummyWebSocket]
) -> None:
    """
    Tests that handle_message does not route the message if the recipient is not connected.

    :param sender_role: The Role enum member sending the message
    :param recipient_role: The Role enum member expected to receive the message
    :param known_clients: Fixture mapping roles to websocket stubs
    """

    message = {"message": "test_message"}

    # Remove the visualizer to simulate it not being connected
    del known_clients[Role.VISUALIZER]

    # Handle the message from the solver
    await utils.handle_message(message, known_clients, Role.SOLVER)

    # Assert no messages were sent
    assert known_clients[Role.SOLVER].sent == []


@pytest.mark.asyncio
async def test_invalid_role_handle_message(known_clients: dict[Role, DummyWebSocket]) -> None:
    """
    Tests that handle_message does not route the message for an invalid role.

    :param known_clients: Fixture mapping roles to websocket stubs
    """

    message = {"message": "test_message"}

    # Handle the message from an invalid role
    await utils.handle_message(message, known_clients, "invalid_role")  # type: ignore

    # Assert no messages were sent
    assert known_clients[Role.SOLVER].sent == []
    assert known_clients[Role.VISUALIZER].sent == []
