# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.CornerSlot import CornerSlot
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.corner_search import search_corner
from rubik_cube_solver.solve.cross import face_center_color
from rubik_cube_solver.solve.edge_search import search_edge

# The index of a UP-layer edge's sticker on the UP face of a 3x3.
F2L_UP_EDGE_STICKERS: dict[EdgeSlot, int] = {
    EdgeSlot.UF: 7,
    EdgeSlot.UR: 5,
    EdgeSlot.UB: 1,
    EdgeSlot.UL: 3,
}

# The index of the FR edge's sticker on the FRONT face of a 3x3.
F2L_FRONT_RIGHT_EDGE_STICKER: int = 5

# Algorithm that lifts a corner out of the DOWN layer and into the UP layer. Each one turns a side
# layer, moves the corner away with U, and turns the side layer back, so every other piece of that
# layer - the cross edges and the already-solved pairs among them - returns to where it started.
# The four UP slots have no entry: a corner already in the UP layer needs no extraction.
F2L_CORNER_EXTRACTION_TABLE: dict[CornerSlot, str] = {
    CornerSlot.DFR: "R U R'",
    CornerSlot.DFL: "L' U' L",
    CornerSlot.DBR: "R' U R",
    CornerSlot.DBL: "L U L'",
}

# Algorithm that brings a UP-layer corner to UFR, above the slot being solved.
F2L_CORNER_ALIGNMENT_TABLE: dict[CornerSlot, str] = {
    CornerSlot.UFR: "",
    CornerSlot.UFL: "U'",
    CornerSlot.UBL: "U2",
    CornerSlot.UBR: "U",
}

# Algorithm that lifts an edge out of the equatorial layer and into the UP layer. Every entry leaves
# a corner sitting at UFR in the UP layer, which is what lets the corner be aligned there first.
# The four UP slots have no entry, and the four DOWN slots cannot occur: they hold the cross.
F2L_EDGE_EXTRACTION_TABLE: dict[EdgeSlot, str] = {
    EdgeSlot.FR: "R U' R'",
    EdgeSlot.FL: "L' U' L",
    EdgeSlot.BR: "R' U R",
    EdgeSlot.BL: "L U' L'",
}

# Algorithm that inserts the pair into the front-right slot, keyed by the corner's orientation at
# UFR, the UP slot holding the edge, and whether the edge's UP sticker is the FRONT color. Every
# entry is a shortest <U, R, F> solution, so it can only disturb the UP layer on the way.
F2L_PAIR_INSERTION_TABLE: dict[tuple[int, EdgeSlot, bool], str] = {
    (0, EdgeSlot.UF, True): "U2 R2 U2 R' U' R U' R2",
    (0, EdgeSlot.UF, False): "F' U2 F U F' U' F",
    (0, EdgeSlot.UR, True): "R U2 R' U' R U R'",
    (0, EdgeSlot.UR, False): "U2 F2 U2 F U F' U F2",
    (0, EdgeSlot.UB, True): "U R U2 R2 F R F'",
    (0, EdgeSlot.UB, False): "U2 R U R' F' U' F",
    (0, EdgeSlot.UL, True): "U2 R U R2 F R F'",
    (0, EdgeSlot.UL, False): "U' F' U2 F2 R' F' R",
    (1, EdgeSlot.UF, True): "R' U2 R2 U R2 U R",
    (1, EdgeSlot.UF, False): "F R' F' R",
    (1, EdgeSlot.UR, True): "U' R U' R' U R U R'",
    (1, EdgeSlot.UR, False): "R U' R' U2 F' U' F",
    (1, EdgeSlot.UB, True): "R U R'",
    (1, EdgeSlot.UB, False): "R2 U2 F R2 F' U2 R2",
    (1, EdgeSlot.UL, True): "U F' U F U' R U R'",
    (1, EdgeSlot.UL, False): "U F' U' F U2 F' U F",
    (2, EdgeSlot.UF, True): "F' U F U2 R U R'",
    (2, EdgeSlot.UF, False): "U F' U F U' F' U' F",
    (2, EdgeSlot.UR, True): "U R U' R'",
    (2, EdgeSlot.UR, False): "F U2 F2 U' F2 U' F'",
    (2, EdgeSlot.UB, True): "U R2 U2 F R' F' U2 R2",
    (2, EdgeSlot.UB, False): "U R U R' U2 F' U' F",
    (2, EdgeSlot.UL, True): "F2 U2 R' F2 R U2 F2",
    (2, EdgeSlot.UL, False): "F' U' F",
}


def front_color_on_up(cube: Cube, slot: EdgeSlot) -> bool:
    """
    Returns whether the UP sticker of the edge in a UP-layer slot has the FRONT center's color.

    The pair's edge carries the FRONT and the RIGHT color, so this is what tells the two apart.
    The orientation flag of `search_edge` cannot: it is measured against the green/blue axis, which
    is the FRONT color for only two of the four sides.

    :param cube: The Cube instance to read
    :param slot: The UP-layer slot holding the edge
    :return: Whether the edge's UP sticker has the FRONT center's color
    """

    return cube.layers[Layer.UP][F2L_UP_EDGE_STICKERS[slot]] == face_center_color(cube, Layer.FRONT)


def is_pair_solved(cube: Cube, front_color: Color, right_color: Color) -> bool:
    """
    Returns whether the pair of the given two colors already fills the front-right slot.

    :param cube: The Cube instance to search
    :param front_color: The color of the FRONT center
    :param right_color: The color of the RIGHT center
    :return: Whether the corner sits oriented in DFR and the edge sits oriented in FR
    """

    corner_slot, orientation = search_corner(cube, Color.YELLOW, front_color, right_color)
    edge_slot, _ = search_edge(cube, front_color, right_color)

    return (
        corner_slot is CornerSlot.DFR
        and orientation == 0
        and edge_slot is EdgeSlot.FR
        and cube.layers[Layer.FRONT][F2L_FRONT_RIGHT_EDGE_STICKER] == front_color
    )
