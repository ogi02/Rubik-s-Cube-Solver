# Project imports
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.enums.Direction import Direction

# Maps a Direction to the number of quarter turns it represents.
QUARTER_TURNS_MAP: dict[Direction, int] = {
    Direction.CW: 1,
    Direction.DOUBLE: 2,
    Direction.CCW: 3,
}

# Maps a number of quarter turns to the Direction that represents it. There is no entry for 0,
# since that many quarter turns cancel out completely and have no corresponding Direction.
DIRECTION_MAP: dict[int, Direction] = {
    quarter_turns: direction for direction, quarter_turns in QUARTER_TURNS_MAP.items()
}


def can_combine(first: Move, second: Move) -> bool:
    """
    Checks whether two moves can be combined into a single move.

    Two moves combine only when they name the same layer (or rotation axis) and, for layer
    turns, the same layer amount. `R` and `Rw'` therefore do not combine, since they turn a
    different amount of layers, even though they name the same face.

    :param first: The first move
    :param second: The second move
    :return: True if the moves can be combined, False otherwise
    """

    return first.layer == second.layer and first.layer_amount == second.layer_amount


def combine(first: Move, second: Move) -> Move | None:
    """
    Combines two moves into the single move equivalent to performing them one after the other.

    Must only be called when `can_combine(first, second)` is True.

    Directions are added as quarter turns modulo 4 (CW=1, DOUBLE=2, CCW=3). A sum of 0 means the
    two moves cancel each other out completely, in which case there is no equivalent move.

    :param first: The first move
    :param second: The second move
    :return: The single move equivalent to `first` followed by `second`, or None if they cancel out
    """

    quarter_turns = (QUARTER_TURNS_MAP[first.direction] + QUARTER_TURNS_MAP[second.direction]) % 4
    if quarter_turns == 0:
        return None

    return Move(first.layer, DIRECTION_MAP[quarter_turns], first.layer_amount)
