# Python imports
from typing import Any

# Project imports
from message_type import MessageType
from role import Role

CUBE_SIDES = ("UP", "DOWN", "LEFT", "RIGHT", "FRONT", "BACK")


def validate_message(message: dict, sender_role: Role) -> MessageType:
    """
    Validate an incoming WebSocket message against the canonical message contract.

    :param message: The raw message payload.
    :param sender_role: The Role of the client that sent the message.
    :return: The resolved MessageType of the message.
    :raise ValueError: If the message violates the message contract.
    """

    # Resolve the message type
    message_type = MessageType.from_str(message.get("type"))

    # Disconnect messages are consumed by the endpoint and must never be relayed
    if message_type == MessageType.DISCONNECT:
        raise ValueError("Message type disconnect must not be relayed")

    # Only the solver may send a relayable message type
    if sender_role != Role.SOLVER:
        raise ValueError(f"Sender role {sender_role.value} is not permitted to send message type {message_type.value}")

    # Validate the payload for the resolved message type
    PAYLOAD_VALIDATORS[message_type](message.get("data"))

    return message_type


def _validate_cube_state_data(data: Any) -> None:
    """
    Validate the data payload of a cube_state message.

    :param data: The data field of the message.
    :raise ValueError: If the payload violates the cube_state contract.
    """

    if not isinstance(data, dict):
        raise ValueError(f"cube_state data must be a dict, got {data!r}")

    dimensions = data.get("dimensions")
    if not isinstance(dimensions, int) or isinstance(dimensions, bool):
        raise ValueError(f"cube_state dimensions must be an int, got {dimensions!r}")
    if dimensions < 2:
        raise ValueError(f"cube_state dimensions must be >= 2, got {dimensions!r}")

    state = data.get("state")
    if not isinstance(state, dict):
        raise ValueError(f"cube_state state must be a dict, got {state!r}")
    if set(state.keys()) != set(CUBE_SIDES):
        raise ValueError(f"cube_state state keys must be exactly {CUBE_SIDES}, got {tuple(state.keys())!r}")

    expected_length = dimensions**2
    for side in CUBE_SIDES:
        side_value = state[side]
        if not isinstance(side_value, list) or not all(isinstance(sticker, str) for sticker in side_value):
            raise ValueError(f"cube_state state[{side!r}] must be a list of str, got {side_value!r}")
        if len(side_value) != expected_length:
            raise ValueError(f"cube_state state[{side!r}] must have length {expected_length}, got {len(side_value)}")


def _validate_apply_moves_data(data: Any) -> None:
    """
    Validate the data payload of an apply_moves message.

    :param data: The data field of the message.
    :raise ValueError: If the payload violates the apply_moves contract.
    """

    if not isinstance(data, dict):
        raise ValueError(f"apply_moves data must be a dict, got {data!r}")

    moves = data.get("moves")
    if not isinstance(moves, list) or not all(isinstance(move, str) for move in moves):
        raise ValueError(f"apply_moves moves must be a list of str, got {moves!r}")


# Payload validator per relayable message type
PAYLOAD_VALIDATORS = {
    MessageType.CUBE_STATE: _validate_cube_state_data,
    MessageType.APPLY_MOVES: _validate_apply_moves_data,
}
