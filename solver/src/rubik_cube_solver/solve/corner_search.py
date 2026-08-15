# Python imports
from typing import NamedTuple

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.CornerSlot import CornerSlot
from rubik_cube_solver.validator.validator_constants import VALID_CORNER_COLOR_SETS
from rubik_cube_solver.validator.validator_utils import get_corners

# The slots in the same order as the corners returned by get_corners.
# Each corner tuple's stickers are given in the canonical clockwise face-sequence order
# for the slot's three faces.
UP_DOWN_COLORS: frozenset[Color] = frozenset({Color.WHITE, Color.YELLOW})

CORNER_SLOTS: tuple[CornerSlot, ...] = (
    CornerSlot.UFL,
    CornerSlot.UFR,
    CornerSlot.UBL,
    CornerSlot.UBR,
    CornerSlot.DFL,
    CornerSlot.DFR,
    CornerSlot.DBL,
    CornerSlot.DBR,
)


class CornerSearchResult(NamedTuple):
    """
    The result of searching for a corner piece: the slot it occupies and its orientation.
    """

    slot: CornerSlot
    orientation: int


def search_corner(cube: Cube, first_color: Color, second_color: Color, third_color: Color) -> CornerSearchResult:
    """
    Searches a cube of any size for the corner piece with the given three colors.

    The orientation is the index within the slot's corner tuple at which the piece's UP/DOWN
    color - white or yellow - lies, the same convention the validator's corner orientation check
    uses. An orientation of 0 means the piece is correctly oriented, with the white or yellow
    sticker on the UP or DOWN face; 1 and 2 are the two twisted states.

    :param cube: The Cube instance to search
    :param first_color: The first color of the corner piece
    :param second_color: The second color of the corner piece
    :param third_color: The third color of the corner piece
    :return: The slot of the corner piece and its orientation
    """

    corner_colors = frozenset({first_color, second_color, third_color})
    if corner_colors not in VALID_CORNER_COLOR_SETS:
        raise ValueError(f"Invalid corner piece: {corner_colors}.")

    for slot, corner in zip(CORNER_SLOTS, get_corners(cube)):
        if frozenset(corner) == corner_colors:
            first_sticker, second_sticker, _ = corner
            if first_sticker in UP_DOWN_COLORS:
                return CornerSearchResult(slot, 0)
            elif second_sticker in UP_DOWN_COLORS:
                return CornerSearchResult(slot, 1)
            else:
                return CornerSearchResult(slot, 2)

    raise ValueError(f"Corner piece not found: {corner_colors}.")
