# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.CornerSlot import CornerSlot
from rubik_cube_solver.enums.Layer import Layer

# The two side (non-UP) stickers of each UP-layer corner of a 2x2, as (face, flat sticker index)
# pairs. Once the last layer is oriented those two stickers hold the corner's other two colors,
# which identify the piece.
PLL_UP_CORNER_STICKERS: dict[CornerSlot, tuple[tuple[Layer, int], ...]] = {
    CornerSlot.UFR: ((Layer.FRONT, 1), (Layer.RIGHT, 0)),
    CornerSlot.UBR: ((Layer.RIGHT, 1), (Layer.BACK, 0)),
    CornerSlot.UBL: ((Layer.BACK, 1), (Layer.LEFT, 0)),
    CornerSlot.UFL: ((Layer.LEFT, 1), (Layer.FRONT, 0)),
}

# The two side colors of the corner that belongs in each UP slot. On a 3x3 these would be read off
# the two centers the slot lies between, but a 2x2 has no centers, so the fixed color scheme the
# first layer was built in is the reference here as well - white on UP, green on FRONT, red on
# RIGHT, blue on BACK and orange on LEFT.
PLL_UP_CORNER_COLORS: dict[CornerSlot, frozenset[Color]] = {
    CornerSlot.UFR: frozenset({Color.GREEN, Color.RED}),
    CornerSlot.UBR: frozenset({Color.RED, Color.BLUE}),
    CornerSlot.UBL: frozenset({Color.BLUE, Color.ORANGE}),
    CornerSlot.UFL: frozenset({Color.ORANGE, Color.GREEN}),
}

# Algorithm that permutes the whole last layer into place at once, keyed by the permutation of the
# four UP corners in the slot order of the sticker table above. Only permutation keys it: the layer
# is already oriented when this step runs, so its 24 permutations are the whole case set. Both the U
# turn that aligns the case and the one that finishes the layer are already part of every entry, so
# the table is looked up once and applied as it stands, with no rotation logic in the step itself.
PLL_TABLE: dict[tuple[int, ...], str] = {
    (0, 1, 2, 3): "",
    (0, 1, 3, 2): "U R F' U F2 U' F R F2 R2",
    (0, 2, 1, 3): "U R2 F2 R F R' F2 R U' R",
    (0, 2, 3, 1): "R U' R F2 R' U R F2 R2",
    (0, 3, 1, 2): "R2 F2 R' U' R F2 R' U R'",
    (0, 3, 2, 1): "R' U R U F2 U F' R' F U' F2",
    (1, 0, 2, 3): "U R U' R F2 R' U R F2 R2",
    (1, 0, 3, 2): "R2 U R' F U F2 R' U F U2 F'",
    (1, 2, 0, 3): "R2 F2 R U R' F2 R F' R",
    (1, 2, 3, 0): "U'",
    (1, 3, 0, 2): "U R2 F2 R' F' U F2 U' F R'",
    (1, 3, 2, 0): "R F' U F2 U' F R F2 R2",
    (2, 0, 1, 3): "R' F R' F2 R U' R' F2 R2",
    (2, 0, 3, 1): "U R2 F2 R' U' R F2 R' U R'",
    (2, 1, 0, 3): "R U' R' U' F2 U' R U R' U F2",
    (2, 1, 3, 0): "R2 F2 R F R' F2 R U' R",
    (2, 3, 0, 1): "U2",
    (2, 3, 1, 0): "U R' U R' F2 R F' R' F2 R2",
    (3, 0, 1, 2): "U",
    (3, 0, 2, 1): "R2 F2 R' F' U F2 U' F R'",
    (3, 1, 0, 2): "R' U R' F2 R F' R' F2 R2",
    (3, 1, 2, 0): "U R2 F2 R U R' F2 R F' R",
    (3, 2, 0, 1): "U R' F R' F2 R U' R' F2 R2",
    (3, 2, 1, 0): "R U2 R' U' F U2 R' F' R U' F2",
}


def up_corner_permutation(cube: Cube) -> tuple[int, ...]:
    """
    Returns where each UP-layer corner belongs, in the slot order of PLL_UP_CORNER_STICKERS.

    Each corner is identified by the pair of colors on its two side stickers, and the slot it
    belongs in is the one PLL_UP_CORNER_COLORS gives that pair to. The entry for a slot is therefore
    the index of the home slot of the corner sitting in it, and a solved last layer reads as
    (0, 1, 2, 3).

    :param cube: The Cube instance to read
    :return: The index of the home slot of the corner in each slot
    """

    home_colors = list(PLL_UP_CORNER_COLORS.values())

    return tuple(
        home_colors.index(frozenset(cube.layers[layer][sticker] for layer, sticker in stickers))
        for stickers in PLL_UP_CORNER_STICKERS.values()
    )
