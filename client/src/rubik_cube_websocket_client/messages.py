CUBE_STATE_TYPE = "cube_state"
APPLY_MOVES_TYPE = "apply_moves"
DISCONNECT_TYPE = "disconnect"


def cube_state(dimensions: int, state: dict[str, list[str]]) -> dict:
    """
    Build a "cube_state" message envelope.

    :param dimensions: The size of the cube, e.g. 3 for a 3x3x3 cube
    :param state: The cube state, mapping each side name to a list of sticker colors
    :return: The "cube_state" message envelope
    """

    return {"type": CUBE_STATE_TYPE, "data": {"dimensions": dimensions, "state": state}}


def apply_moves(moves: list[str]) -> dict:
    """
    Build an "apply_moves" message envelope.

    :param moves: The list of moves to apply, in cube notation
    :return: The "apply_moves" message envelope
    """

    return {"type": APPLY_MOVES_TYPE, "data": {"moves": moves}}


def disconnect() -> dict:
    """
    Build a "disconnect" message envelope.

    :return: The "disconnect" message envelope
    """

    return {"type": DISCONNECT_TYPE}
