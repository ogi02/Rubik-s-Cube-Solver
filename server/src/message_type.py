# Python imports
from enum import Enum


class MessageType(Enum):
    """
    Enum representing different WebSocket message types in the system.
    """

    CUBE_STATE = "cube_state"
    APPLY_MOVES = "apply_moves"
    DISCONNECT = "disconnect"

    @staticmethod
    def from_str(label: str) -> "MessageType":
        """
        Convert a string to a MessageType enum member.

        :param label: The string representation of the message type.
        :return: The corresponding MessageType enum member.
        :raise ValueError: If the label does not correspond to any MessageType.
        """
        if not isinstance(label, str):
            raise ValueError(f"Unknown message type: {label}")
        match label:
            case "cube_state":
                return MessageType.CUBE_STATE
            case "apply_moves":
                return MessageType.APPLY_MOVES
            case "disconnect":
                return MessageType.DISCONNECT
            case _:
                raise ValueError(f"Unknown message type: {label}")
