# Python imports
from typing import NamedTuple

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.validator.validator_constants import EDGE_CANONICAL_ORIENTATION, VALID_EDGE_COLOR_SETS
from rubik_cube_solver.validator.validator_utils import get_edges

# The slots in the same order as the edges returned by get_edges.
# The first sticker of every edge tuple lies on the reference face of its slot -
# the UP/DOWN face for the eight U/D slots and the FRONT/BACK face for the four equatorial ones.
EDGE_SLOTS: tuple[EdgeSlot, ...] = (
    EdgeSlot.UF,
    EdgeSlot.UB,
    EdgeSlot.UL,
    EdgeSlot.UR,
    EdgeSlot.DF,
    EdgeSlot.DB,
    EdgeSlot.DL,
    EdgeSlot.DR,
    EdgeSlot.FL,
    EdgeSlot.FR,
    EdgeSlot.BL,
    EdgeSlot.BR,
)


class EdgeSearchResult(NamedTuple):
    """
    The result of searching for an edge piece: the slot it occupies and whether it is oriented.
    """

    slot: EdgeSlot
    is_good: bool


def search_edge(cube: Cube, first_color: Color, second_color: Color) -> EdgeSearchResult:
    """
    Searches an odd-sized cube for the middle edge piece with the given two colors.

    The edge is good when its primary color - white or yellow when the piece has one, green or blue
    otherwise - lies on the reference face of the slot it occupies. That is the UP or DOWN face for
    the eight U/D slots and the FRONT or BACK face for the four equatorial slots, which makes the flag
    the standard edge orientation with respect to the FRONT/BACK axis.

    :param cube: The Cube instance to search
    :param first_color: The first color of the edge piece
    :param second_color: The second color of the edge piece
    :return: The slot of the edge piece and whether it is oriented
    """

    if cube.size % 2 == 0:
        raise ValueError(f"Edge search is supported only on odd-sized cubes, got size {cube.size}")

    edge_colors = frozenset({first_color, second_color})
    if edge_colors not in VALID_EDGE_COLOR_SETS:
        raise ValueError(f"Invalid edge piece: {edge_colors}.")

    primary_color = EDGE_CANONICAL_ORIENTATION[edge_colors]

    for slot, (reference_color, other_color) in zip(EDGE_SLOTS, get_edges(cube)):
        if frozenset({reference_color, other_color}) == edge_colors:
            return EdgeSearchResult(slot, reference_color == primary_color)

    raise ValueError(f"Edge piece not found: {edge_colors}.")
