# Project imports
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.CornerSlot import CornerSlot

# The side colors of the four DOWN-layer corners, in the order a `y` rotation brings them to the
# front-right slot. A 2x2 has no centers, so nothing on the cube says which face is which: the
# first layer is built in the fixed color scheme of a solved cube instead, yellow on DOWN with
# green on FRONT and red on RIGHT. Solving the pairs in this order and rotating with `y` after
# each one leaves every corner in its home slot once the four rotations add up to a full turn.
FIRST_LAYER_CORNER_COLORS: tuple[tuple[Color, Color], ...] = (
    (Color.GREEN, Color.RED),
    (Color.RED, Color.BLUE),
    (Color.BLUE, Color.ORANGE),
    (Color.ORANGE, Color.GREEN),
)

# Algorithm that lifts a corner out of the DOWN layer and into the UP layer. Each one turns a side
# layer, moves the corner away with U, and turns the side layer back, so every other corner of that
# layer - the already-solved ones among them - returns to where it started. The four UP slots have
# no entry: a corner already in the UP layer needs no extraction.
FIRST_LAYER_EXTRACTION_TABLE: dict[CornerSlot, str] = {
    CornerSlot.DFR: "R U R'",
    CornerSlot.DFL: "L' U' L",
    CornerSlot.DBR: "R' U R",
    CornerSlot.DBL: "L U L'",
}

# Algorithm that brings a UP-layer corner to UFR, above the slot being solved.
FIRST_LAYER_ALIGNMENT_TABLE: dict[CornerSlot, str] = {
    CornerSlot.UFR: "",
    CornerSlot.UFL: "U'",
    CornerSlot.UBL: "U2",
    CornerSlot.UBR: "U",
}

# Algorithm that inserts the corner at UFR into DFR with its yellow sticker on DOWN, keyed by the
# corner's orientation at UFR - the index within its clockwise sticker triple at which the yellow
# sticker lies, so 0 is yellow on UP, 1 is yellow on RIGHT and 2 is yellow on FRONT. Every entry is
# a shortest <U, R> solution, and the R layer's two DOWN corners are the only ones it can touch, so
# an insertion can only disturb the UP layer and the slot it is filling.
FIRST_LAYER_INSERTION_TABLE: dict[int, str] = {
    0: "R2 U R2 U' R2",
    1: "R U R'",
    2: "U R U' R'",
}
