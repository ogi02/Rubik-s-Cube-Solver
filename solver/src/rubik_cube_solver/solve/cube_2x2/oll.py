# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.CornerSlot import CornerSlot
from rubik_cube_solver.enums.Layer import Layer

# The three (face, flat sticker index) pairs of each UP-layer corner of a 2x2, in the canonical
# clockwise face-sequence order `get_corners` uses. Reading a corner in that order is what lets its
# orientation be measured the same way `search_corner` measures it.
OLL_UP_CORNER_STICKERS: dict[CornerSlot, tuple[tuple[Layer, int], ...]] = {
    CornerSlot.UFR: ((Layer.UP, 3), (Layer.RIGHT, 0), (Layer.FRONT, 1)),
    CornerSlot.UBR: ((Layer.UP, 1), (Layer.BACK, 0), (Layer.RIGHT, 1)),
    CornerSlot.UBL: ((Layer.UP, 0), (Layer.LEFT, 0), (Layer.BACK, 1)),
    CornerSlot.UFL: ((Layer.UP, 2), (Layer.FRONT, 0), (Layer.LEFT, 1)),
}

# Algorithm that orients the whole last layer at once, keyed by the orientation of the four UP
# corners in the slot order of the sticker table above. Orientation is all that keys it: which
# corner sits in which slot does not matter to this step, and the twist an algorithm adds belongs to
# the slot rather than to the piece in it, so one entry solves its case in every permutation. Of the
# 81 patterns four corners can show, the 27 whose twists sum to a multiple of three are the
# reachable ones. The U turn that aligns the case is already at the front of every entry, so the
# table is looked up once and applied as it stands, with no rotation logic in the step itself.
OLL_TABLE: dict[tuple[int, ...], str] = {
    (0, 0, 0, 0): "",
    (0, 0, 1, 2): "F R U R' U' F'",
    (0, 0, 2, 1): "R U' R' U2 F' U2 F",
    (0, 1, 0, 2): "R' U R U F R' F'",
    (0, 1, 1, 1): "R' F R F' R U R'",
    (0, 1, 2, 0): "R U F R' F' R'",
    (0, 2, 0, 1): "R' F R U F U' F'",
    (0, 2, 1, 0): "R U R' U' F' U' F",
    (0, 2, 2, 2): "R' U2 R U R' U R",
    (1, 0, 0, 2): "R F U' F' U' R' F",
    (1, 0, 1, 1): "R U2 R' U' R U' R'",
    (1, 0, 2, 0): "R F' U' R' U' R F",
    (1, 1, 0, 1): "R' U R F' U F R'",
    (1, 1, 1, 0): "R F2 R' F' U F' R'",
    (1, 1, 2, 2): "R2 U2 F R U2 R F2 R F",
    (1, 2, 0, 0): "F U R U' R' F'",
    (1, 2, 1, 2): "F2 U2 F U2 F2",
    (1, 2, 2, 1): "R U2 F' R2 F R2 F U2 R'",
    (2, 0, 0, 1): "R F R F' U' R'",
    (2, 0, 1, 0): "R U' R' U' F' U F",
    (2, 0, 2, 2): "R F U' F R F2 R'",
    (2, 1, 0, 0): "R F' U' R2 F' R2 F",
    (2, 1, 1, 2): "R U' R2 U R2 U R2 U' R",
    (2, 1, 2, 1): "R2 U2 R U2 R2",
    (2, 2, 0, 2): "R' F2 R U R' F R",
    (2, 2, 1, 1): "R2 U2 F U F2 U R2 U F",
    (2, 2, 2, 0): "R U R' U R U2 R'",
}


def up_corner_orientations(cube: Cube) -> tuple[int, ...]:
    """
    Returns the orientation of each UP-layer corner, in the slot order of OLL_UP_CORNER_STICKERS.

    An orientation is the index within the corner's clockwise sticker triple at which the white
    sticker lies, the same convention `search_corner` uses: 0 means the corner is already oriented,
    1 and 2 are the two twisted states. A 2x2 has no centers, so white is the UP color by the color
    scheme the first layer was built in rather than by anything read off the cube.

    :param cube: The Cube instance to read
    :return: The orientation of each UP-layer corner
    """

    return tuple(
        next(index for index, (layer, sticker) in enumerate(stickers) if cube.layers[layer][sticker] == Color.WHITE)
        for stickers in OLL_UP_CORNER_STICKERS.values()
    )
