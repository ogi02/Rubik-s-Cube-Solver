# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.CornerSlot import CornerSlot
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.cube_3x3.cross import face_center_color

# The three (face, flat sticker index) pairs of each UP-layer corner, in the canonical clockwise
# face-sequence order `get_corners` uses. Reading a corner in that order is what lets its
# orientation be measured the same way `search_corner` measures it.
OLL_UP_CORNER_STICKERS: dict[CornerSlot, tuple[tuple[Layer, int], ...]] = {
    CornerSlot.UFR: ((Layer.UP, 8), (Layer.RIGHT, 0), (Layer.FRONT, 2)),
    CornerSlot.UBR: ((Layer.UP, 2), (Layer.BACK, 0), (Layer.RIGHT, 2)),
    CornerSlot.UBL: ((Layer.UP, 0), (Layer.LEFT, 0), (Layer.BACK, 2)),
    CornerSlot.UFL: ((Layer.UP, 6), (Layer.FRONT, 0), (Layer.LEFT, 2)),
}

# The index of a UP-layer edge's sticker on the UP face of a 3x3.
OLL_UP_EDGE_STICKERS: dict[EdgeSlot, int] = {
    EdgeSlot.UF: 7,
    EdgeSlot.UR: 5,
    EdgeSlot.UB: 1,
    EdgeSlot.UL: 3,
}

# Algorithm that orients the whole last layer at once, keyed by the orientation of the four UP
# corners followed by the orientation of the four UP edges, each in the slot order of the sticker
# table above. Orientation is all that keys it: which piece sits in which slot does not matter to
# this step, so the 27 corner states and the 8 edge states give 216 entries between them. The U
# turn that aligns the case is already at the front of every entry, so the table is looked up once
# and applied as it stands, with no rotation logic in the step itself.
OLL_TABLE: dict[tuple[tuple[int, ...], tuple[bool, ...]], str] = {
    ((0, 0, 0, 0), (False, False, False, False)): "B U L U' L' B' R' U' R' F R F' U R",
    ((0, 0, 0, 0), (False, False, True, True)): "F R U R' U' F2 L' U' L U F",
    ((0, 0, 0, 0), (False, True, False, True)): "F R' F' R2 U' R' F' U' F R U R'",
    ((0, 0, 0, 0), (False, True, True, False)): "F U R U' R' F2 U' L' U L F",
    ((0, 0, 0, 0), (True, False, False, True)): "R' U' F' U F R2 U B U' B' R'",
    ((0, 0, 0, 0), (True, False, True, False)): "B U L U' L' B' F U R U' R' F'",
    ((0, 0, 0, 0), (True, True, False, False)): "F' L' U' L U F B U L U' L' B'",
    ((0, 0, 0, 0), (True, True, True, True)): "",
    ((0, 0, 1, 2), (False, False, False, False)): "R' U' F' U F2 R U R' F' R F U' F'",
    ((0, 0, 1, 2), (False, False, True, True)): "U' R' U' R U' R' U2 R F R U R' U' F'",
    ((0, 0, 1, 2), (False, True, False, True)): "F R U R' U' F'",
    ((0, 0, 1, 2), (False, True, True, False)): "F' U' L' U L F",
    ((0, 0, 1, 2), (True, False, False, True)): "U R U R' U R U2 R' F R U R' U' F'",
    ((0, 0, 1, 2), (True, False, True, False)): "U2 R' U' R' F R F' U R",
    ((0, 0, 1, 2), (True, True, False, False)): "B U L U' L' B'",
    ((0, 0, 1, 2), (True, True, True, True)): "U R2 D' R U2 R' D R U2 R",
    ((0, 0, 2, 1), (False, False, False, False)): "R' U' F' U F2 R U R' U' F' U R",
    ((0, 0, 2, 1), (False, False, True, True)): "R U R' U' R U' R' F' U' F R U R'",
    ((0, 0, 2, 1), (False, True, False, True)): "R U R' U' R' F R F'",
    ((0, 0, 2, 1), (False, True, True, False)): "R' U' F U R U' R' F' R",
    ((0, 0, 2, 1), (True, False, False, True)): "U F R' F R2 U' R' U' R U R' F2",
    ((0, 0, 2, 1), (True, False, True, False)): "U R U R2 U' R' F R U R U' F'",
    ((0, 0, 2, 1), (True, True, False, False)): "U2 L U F' U' L' U L F L'",
    ((0, 0, 2, 1), (True, True, True, True)): "R U2 R' U2 R' F R U R U' R' F'",
    ((0, 1, 0, 2), (False, False, False, False)): "R U R' U R' F R F' U2 R' F R F'",
    ((0, 1, 0, 2), (False, False, True, True)): "U2 R U2 R2 F R F' R U2 R'",
    ((0, 1, 0, 2), (False, True, False, True)): "R' F R U R' U' F' U R",
    ((0, 1, 0, 2), (False, True, True, False)): "L' U' L U' L' U L U L F' L' F",
    ((0, 1, 0, 2), (True, False, False, True)): "U R U R' U R U' R' U' R' F R F'",
    ((0, 1, 0, 2), (True, False, True, False)): "U L F' L' U' L U F U' L'",
    ((0, 1, 0, 2), (True, True, False, False)): "U2 F R' F' R U R U' R'",
    ((0, 1, 0, 2), (True, True, True, True)): "U2 R' F R B' R' F' R B",
    ((0, 1, 1, 1), (False, False, False, False)): "R U B U' B' R' F R U R' U' F'",
    ((0, 1, 1, 1), (False, False, True, True)): "R U R' U' R' F R2 U R' U' F'",
    ((0, 1, 1, 1), (False, True, False, True)): "R' F R U R' F' R F U' F'",
    ((0, 1, 1, 1), (False, True, True, False)): "R U2 R' U2 R' F R F'",
    ((0, 1, 1, 1), (True, False, False, True)): "U' F R U R' U' F' U F R U R' U' F'",
    ((0, 1, 1, 1), (True, False, True, False)): "U2 L U2 L' U' L F' U' L' U L F L'",
    ((0, 1, 1, 1), (True, True, False, False)): "U R B2 L' B' L B' R'",
    ((0, 1, 1, 1), (True, True, True, True)): "L' U' L U' L' U2 L",
    ((0, 1, 2, 0), (False, False, False, False)): "U R B2 L' B' L B' R2 U' F' U F R",
    ((0, 1, 2, 0), (False, False, True, True)): "R U R' U R U2 R' F R U R' U' F'",
    ((0, 1, 2, 0), (False, True, False, True)): "U R' U' R' F R F' U R",
    ((0, 1, 2, 0), (False, True, True, False)): "U2 R' U' R U' R' U2 R F R U R' U' F'",
    ((0, 1, 2, 0), (True, False, False, True)): "R U B U' B' R'",
    ((0, 1, 2, 0), (True, False, True, False)): "U F' L' U' L U F",
    ((0, 1, 2, 0), (True, True, False, False)): "U' F' U' L' U L F",
    ((0, 1, 2, 0), (True, True, True, True)): "R2 D' R U2 R' D R U2 R",
    ((0, 2, 0, 1), (False, False, False, False)): "U2 R U R' U R' F R F' U2 R' F R F'",
    ((0, 2, 0, 1), (False, False, True, True)): "F R' F' R U R U' R'",
    ((0, 2, 0, 1), (False, True, False, True)): "U2 R' F R U R' U' F' U R",
    ((0, 2, 0, 1), (False, True, True, False)): "U' R U R' U R U' R' U' R' F R F'",
    ((0, 2, 0, 1), (True, False, False, True)): "U2 L' U' L U' L' U L U L F' L' F",
    ((0, 2, 0, 1), (True, False, True, False)): "U' L F' L' U' L U F U' L'",
    ((0, 2, 0, 1), (True, True, False, False)): "R U2 R2 F R F' R U2 R'",
    ((0, 2, 0, 1), (True, True, True, True)): "R' F R B' R' F' R B",
    ((0, 2, 1, 0), (False, False, False, False)): "L F2 R' F' R F' L2 B2 R B R' B L",
    ((0, 2, 1, 0), (False, False, True, True)): "F R' F R2 U' R' U' R U R' F2",
    ((0, 2, 1, 0), (False, True, False, True)): "R U R2 U' R' F R U R U' F'",
    ((0, 2, 1, 0), (False, True, True, False)): "U' R U R' U' R U' R' F' U' F R U R'",
    ((0, 2, 1, 0), (True, False, False, True)): "U L U F' U' L' U L F L'",
    ((0, 2, 1, 0), (True, False, True, False)): "U' R U R' U' R' F R F'",
    ((0, 2, 1, 0), (True, True, False, False)): "U' R' U' F U R U' R' F' R",
    ((0, 2, 1, 0), (True, True, True, True)): "U R' U' R' F R U R U' R' F' R",
    ((0, 2, 2, 2), (False, False, False, False)): "B U L U' L' B' U F' L' U' L U F",
    ((0, 2, 2, 2), (False, False, True, True)): "U' R U R' U R' F R F' R U2 R'",
    ((0, 2, 2, 2), (False, True, False, True)): "L F' L' U' L U F L' U L U2 L'",
    ((0, 2, 2, 2), (False, True, True, False)): "F U R U' R' F' U' L F R' F R F2 L'",
    ((0, 2, 2, 2), (True, False, False, True)): "U L F R' F R F2 L'",
    ((0, 2, 2, 2), (True, False, True, False)): "U F U R U' R2 F' R U R U' R'",
    ((0, 2, 2, 2), (True, True, False, False)): "L' B2 R B R' B L",
    ((0, 2, 2, 2), (True, True, True, True)): "U R U R' U R U2 R'",
    ((1, 0, 0, 2), (False, False, False, False)): "L' B2 R B R' B L2 F2 R' F' R F' L'",
    ((1, 0, 0, 2), (False, False, True, True)): "U R' U' F U R U' R' F' R",
    ((1, 0, 0, 2), (False, True, False, True)): "U2 R U R2 U' R' F R U R U' F'",
    ((1, 0, 0, 2), (False, True, True, False)): "U' L U F' U' L' U L F L'",
    ((1, 0, 0, 2), (True, False, False, True)): "U R U R' U' R U' R' F' U' F R U R'",
    ((1, 0, 0, 2), (True, False, True, False)): "U R U R' U' R' F R F'",
    ((1, 0, 0, 2), (True, True, False, False)): "U2 F R' F R2 U' R' U' R U R' F2",
    ((1, 0, 0, 2), (True, True, True, True)): "F R U R' U' R' F' R U R U' R'",
    ((1, 0, 1, 1), (False, False, False, False)): "B U L U' L' B' U F R U R' U' F'",
    ((1, 0, 1, 1), (False, False, True, True)): "U R U2 R' U2 R' F R F'",
    ((1, 0, 1, 1), (False, True, False, True)): "F' L' U' L U F L U2 L' U' L U' L'",
    ((1, 0, 1, 1), (False, True, True, False)): "L F2 R' F' R F' L'",
    ((1, 0, 1, 1), (True, False, False, True)): "U R U R' U' R' F R2 U R' U' F'",
    ((1, 0, 1, 1), (True, False, True, False)): "U R' F R U R' F' R F U' F'",
    ((1, 0, 1, 1), (True, True, False, False)): "F R U R' U' F' U F R U R' U' F'",
    ((1, 0, 1, 1), (True, True, True, True)): "R U2 R' U' R U' R'",
    ((1, 0, 2, 0), (False, False, False, False)): "U' R U R' U R' F R F' U2 R' F R F'",
    ((1, 0, 2, 0), (False, False, True, True)): "R U R' U R U' R' U' R' F R F'",
    ((1, 0, 2, 0), (False, True, False, True)): "L F' L' U' L U F U' L'",
    ((1, 0, 2, 0), (False, True, True, False)): "U R U2 R2 F R F' R U2 R'",
    ((1, 0, 2, 0), (True, False, False, True)): "U F R' F' R U R U' R'",
    ((1, 0, 2, 0), (True, False, True, False)): "U' R' F R U R' U' F' U R",
    ((1, 0, 2, 0), (True, True, False, False)): "U' L' U' L U' L' U L U L F' L' F",
    ((1, 0, 2, 0), (True, True, True, True)): "U R' F R B' R' F' R B",
    ((1, 1, 0, 1), (False, False, False, False)): "R' U' F' U F R F' L' U' L U F",
    ((1, 1, 0, 1), (False, False, True, True)): "U L F2 R' F' R F' L'",
    ((1, 1, 0, 1), (False, True, False, True)): "U2 R' F R U R' F' R F U' F'",
    ((1, 1, 0, 1), (False, True, True, False)): "U F R U R' U' F' U F R U R' U' F'",
    ((1, 1, 0, 1), (True, False, False, True)): "U2 R U2 R' U2 R' F R F'",
    ((1, 1, 0, 1), (True, False, True, False)): "L U2 L' U' L F' U' L' U L F L'",
    ((1, 1, 0, 1), (True, True, False, False)): "U2 R U R' U' R' F R2 U R' U' F'",
    ((1, 1, 0, 1), (True, True, True, True)): "U R U2 R' U' R U' R'",
    ((1, 1, 1, 0), (False, False, False, False)): "F' L' U' L U F R U B U' B' R'",
    ((1, 1, 1, 0), (False, False, True, True)): "U2 F R U R' U' F' U F R U R' U' F'",
    ((1, 1, 1, 0), (False, True, False, True)): "F R U R' U' F' R U2 R' U' R U' R'",
    ((1, 1, 1, 0), (False, True, True, False)): "U' R U R' U' R' F R2 U R' U' F'",
    ((1, 1, 1, 0), (True, False, False, True)): "R B2 L' B' L B' R'",
    ((1, 1, 1, 0), (True, False, True, False)): "U' R' F R U R' F' R F U' F'",
    ((1, 1, 1, 0), (True, True, False, False)): "U' R U2 R' U2 R' F R F'",
    ((1, 1, 1, 0), (True, True, True, True)): "L U2 L' U' L U' L'",
    ((1, 1, 2, 2), (False, False, False, False)): "L' B2 R B R' B L F' U' L' U L F",
    ((1, 1, 2, 2), (False, False, True, True)): "U F' L' U' L U L' U' L U F",
    ((1, 1, 2, 2), (False, True, False, True)): "U R U R' U R U' B U' B' R'",
    ((1, 1, 2, 2), (False, True, True, False)): "U' F R U R' U' R U R' U' F'",
    ((1, 1, 2, 2), (True, False, False, True)): "U R' F R2 B' R2 F' R2 B R'",
    ((1, 1, 2, 2), (True, False, True, False)): "U F U R U' R' U R U' R' F'",
    ((1, 1, 2, 2), (True, True, False, False)): "U R B' R2 F R2 B R2 F' R",
    ((1, 1, 2, 2), (True, True, True, True)): "U' R U2 R2 U' R2 U' R2 U2 R",
    ((1, 2, 0, 0), (False, False, False, False)): "R B2 L' B' L B' R2 U' F' U F R",
    ((1, 2, 0, 0), (False, False, True, True)): "F U R U' R' F'",
    ((1, 2, 0, 0), (False, True, False, True)): "F' L' U' L U F",
    ((1, 2, 0, 0), (False, True, True, False)): "U' R U R' U R U2 R' F R U R' U' F'",
    ((1, 2, 0, 0), (True, False, False, True)): "U R' U' F' U F R",
    ((1, 2, 0, 0), (True, False, True, False)): "R' U' R' F R F' U R",
    ((1, 2, 0, 0), (True, True, False, False)): "U R' U' R U' R' U2 R F R U R' U' F'",
    ((1, 2, 0, 0), (True, True, True, True)): "U' R2 D' R U2 R' D R U2 R",
    ((1, 2, 1, 2), (False, False, False, False)): "R U2 R2 F R F' U2 R' F R F'",
    ((1, 2, 1, 2), (False, False, True, True)): "U R' F2 L F L' F' L F L' F R",
    ((1, 2, 1, 2), (False, True, False, True)): "B U2 B2 U' B2 U' B2 U2 B R U B U' B' R'",
    ((1, 2, 1, 2), (False, True, True, False)): "L F R' F R F' R' F R F2 L'",
    ((1, 2, 1, 2), (True, False, False, True)): "U L F2 R' F' R F R' F' R F' L'",
    ((1, 2, 1, 2), (True, False, True, False)): "R U2 R2 U' R U' R' U2 F R F'",
    ((1, 2, 1, 2), (True, True, False, False)): "U L' B2 R B R' B' R B R' B L",
    ((1, 2, 1, 2), (True, True, True, True)): "U R U2 R' U' R U R' U' R U' R'",
    ((1, 2, 2, 1), (False, False, False, False)): "F' L' U' L U F U R' U' F' U F R",
    ((1, 2, 2, 1), (False, False, True, True)): "R' F R2 B' R2 F' R2 B R'",
    ((1, 2, 2, 1), (False, True, False, True)): "F U R U' R' U R U' R' F'",
    ((1, 2, 2, 1), (False, True, True, False)): "F' L' U' L U L' U' L U F",
    ((1, 2, 2, 1), (True, False, False, True)): "R B' R2 F R2 B R2 F' R",
    ((1, 2, 2, 1), (True, False, True, False)): "R U R' U R U' B U' B' R'",
    ((1, 2, 2, 1), (True, True, False, False)): "U2 F R U R' U' R U R' U' F'",
    ((1, 2, 2, 1), (True, True, True, True)): "U B U2 B2 U' B2 U' B2 U2 B",
    ((2, 0, 0, 1), (False, False, False, False)): "U' R B2 L' B' L B' R2 U' F' U F R",
    ((2, 0, 0, 1), (False, False, True, True)): "R' U' F' U F R",
    ((2, 0, 0, 1), (False, True, False, True)): "U' R' U' R' F R F' U R",
    ((2, 0, 0, 1), (False, True, True, False)): "U B U L U' L' B'",
    ((2, 0, 0, 1), (True, False, False, True)): "R' U' R U' R' U2 R F R U R' U' F'",
    ((2, 0, 0, 1), (True, False, True, False)): "U F R U R' U' F'",
    ((2, 0, 0, 1), (True, True, False, False)): "U2 R U R' U R U2 R' F R U R' U' F'",
    ((2, 0, 0, 1), (True, True, True, True)): "U2 R2 D' R U2 R' D R U2 R",
    ((2, 0, 1, 0), (False, False, False, False)): "U R U R' U R' F R F' U2 R' F R F'",
    ((2, 0, 1, 0), (False, False, True, True)): "U L' U' L U' L' U L U L F' L' F",
    ((2, 0, 1, 0), (False, True, False, True)): "U2 L F' L' U' L U F U' L'",
    ((2, 0, 1, 0), (False, True, True, False)): "U' F R' F' R U R U' R'",
    ((2, 0, 1, 0), (True, False, False, True)): "U' R U2 R2 F R F' R U2 R'",
    ((2, 0, 1, 0), (True, False, True, False)): "U R' F R U R' U' F' U R",
    ((2, 0, 1, 0), (True, True, False, False)): "U2 R U R' U R U' R' U' R' F R F'",
    ((2, 0, 1, 0), (True, True, True, True)): "U' R' F R B' R' F' R B",
    ((2, 0, 2, 2), (False, False, False, False)): "R' U' F' U F R F R U R' U' F'",
    ((2, 0, 2, 2), (False, False, True, True)): "R U B U' B' R' L F R' F R F2 L'",
    ((2, 0, 2, 2), (False, True, False, True)): "U2 F U R U' R2 F' R U R U' R'",
    ((2, 0, 2, 2), (False, True, True, False)): "U L' B2 R B R' B L",
    ((2, 0, 2, 2), (True, False, False, True)): "R U R' U R' F R F' R U2 R'",
    ((2, 0, 2, 2), (True, False, True, False)): "R' U' F U R U' R' F' U' F' U F R",
    ((2, 0, 2, 2), (True, True, False, False)): "U2 L F R' F R F2 L'",
    ((2, 0, 2, 2), (True, True, True, True)): "L U L' U L U2 L'",
    ((2, 1, 0, 0), (False, False, False, False)): "U2 R' U' F' U F2 R U R' U' F' U R",
    ((2, 1, 0, 0), (False, False, True, True)): "L U F' U' L' U L F L'",
    ((2, 1, 0, 0), (False, True, False, True)): "U2 R U R' U' R' F R F'",
    ((2, 1, 0, 0), (False, True, True, False)): "U' F R' F R2 U' R' U' R U R' F2",
    ((2, 1, 0, 0), (True, False, False, True)): "U2 R' U' F U R U' R' F' R",
    ((2, 1, 0, 0), (True, False, True, False)): "U' R U R2 U' R' F R U R U' F'",
    ((2, 1, 0, 0), (True, True, False, False)): "U2 R U R' U' R U' R' F' U' F R U R'",
    ((2, 1, 0, 0), (True, True, True, True)): "R' U' R' F R U R U' R' F' R",
    ((2, 1, 1, 2), (False, False, False, False)): "F R U R' U' F' B U L U' L' B'",
    ((2, 1, 1, 2), (False, False, True, True)): "F R U R' U' R U R' U' F'",
    ((2, 1, 1, 2), (False, True, False, True)): "U2 F U R U' R' U R U' R' F'",
    ((2, 1, 1, 2), (False, True, True, False)): "U2 R B' R2 F R2 B R2 F' R",
    ((2, 1, 1, 2), (True, False, False, True)): "B' R' U' R U R' U' R U B",
    ((2, 1, 1, 2), (True, False, True, False)): "U2 R U R' U R U' B U' B' R'",
    ((2, 1, 1, 2), (True, True, False, False)): "U2 R' F R2 B' R2 F' R2 B R'",
    ((2, 1, 1, 2), (True, True, True, True)): "R U2 R2 U' R2 U' R2 U2 R",
    ((2, 1, 2, 1), (False, False, False, False)): "U R U2 R2 F R F' U2 R' F R F'",
    ((2, 1, 2, 1), (False, False, True, True)): "L F2 R' F' R F R' F' R F' L'",
    ((2, 1, 2, 1), (False, True, False, True)): "U R U2 R2 U' R U' R' U2 F R F'",
    ((2, 1, 2, 1), (False, True, True, False)): "R' F2 L F L' F' L F L' F R",
    ((2, 1, 2, 1), (True, False, False, True)): "L' B2 R B R' B' R B R' B L",
    ((2, 1, 2, 1), (True, False, True, False)): "F R' F' R U2 R U2 R2 U' R' F R F' U R",
    ((2, 1, 2, 1), (True, True, False, False)): "R B2 L' B' L B L' B' L B' R'",
    ((2, 1, 2, 1), (True, True, True, True)): "R U2 R' U' R U R' U' R U' R'",
    ((2, 2, 0, 2), (False, False, False, False)): "F R U R' U' F' L' B2 R B R' B L",
    ((2, 2, 0, 2), (False, False, True, True)): "R' F2 L F L' F R",
    ((2, 2, 0, 2), (False, True, False, True)): "F U R U' R' F' R' U' F' U F R",
    ((2, 2, 0, 2), (False, True, True, False)): "U' L F R' F R F2 L'",
    ((2, 2, 0, 2), (True, False, False, True)): "F' L' U' L U F U F R U R' U' F'",
    ((2, 2, 0, 2), (True, False, True, False)): "U' F U R U' R2 F' R U R U' R'",
    ((2, 2, 0, 2), (True, True, False, False)): "U R U R' U R' F R F' R U2 R'",
    ((2, 2, 0, 2), (True, True, True, True)): "L' U2 L U L' U L",
    ((2, 2, 1, 1), (False, False, False, False)): "L F2 R' F' R F' L' B U L U' L' B'",
    ((2, 2, 1, 1), (False, False, True, True)): "U' R B' R2 F R2 B R2 F' R",
    ((2, 2, 1, 1), (False, True, False, True)): "U' R U R' U R U' B U' B' R'",
    ((2, 2, 1, 1), (False, True, True, False)): "U' R' F R2 B' R2 F' R2 B R'",
    ((2, 2, 1, 1), (True, False, False, True)): "U F R U R' U' R U R' U' F'",
    ((2, 2, 1, 1), (True, False, True, False)): "U' F U R U' R' U R U' R' F'",
    ((2, 2, 1, 1), (True, True, False, False)): "U B' R' U' R U R' U' R U B",
    ((2, 2, 1, 1), (True, True, True, True)): "B U2 B2 U' B2 U' B2 U2 B",
    ((2, 2, 2, 0), (False, False, False, False)): "R U B U' B' R' F' L' U' L U F",
    ((2, 2, 2, 0), (False, False, True, True)): "L F R' F R F2 L'",
    ((2, 2, 2, 0), (False, True, False, True)): "F U R U' R2 F' R U R U' R'",
    ((2, 2, 2, 0), (False, True, True, False)): "U2 R U R' U R' F R F' R U2 R'",
    ((2, 2, 2, 0), (True, False, False, True)): "U R' F2 L F L' F R",
    ((2, 2, 2, 0), (True, False, True, False)): "R U B U' B' R' U R' U' F' U F R",
    ((2, 2, 2, 0), (True, True, False, False)): "U F' L' U' L U F U F R U R' U' F'",
    ((2, 2, 2, 0), (True, True, True, True)): "R U R' U R U2 R'",
}


def up_corner_orientations(cube: Cube) -> tuple[int, ...]:
    """
    Returns the orientation of each UP-layer corner, in the slot order of OLL_UP_CORNER_STICKERS.

    An orientation is the index within the corner's clockwise sticker triple at which the UP
    center's color lies, the same convention `search_corner` uses: 0 means the corner is already
    oriented, 1 and 2 are the two twisted states.

    :param cube: The Cube instance to read
    :return: The orientation of each UP-layer corner
    """

    up_color = face_center_color(cube, Layer.UP)

    return tuple(
        next(index for index, (layer, sticker) in enumerate(stickers) if cube.layers[layer][sticker] == up_color)
        for stickers in OLL_UP_CORNER_STICKERS.values()
    )


def up_edge_orientations(cube: Cube) -> tuple[bool, ...]:
    """
    Returns whether each UP-layer edge is oriented, in the slot order of OLL_UP_EDGE_STICKERS.

    An edge is oriented when the sticker it shows on the UP face has the UP center's color.

    :param cube: The Cube instance to read
    :return: Whether each UP-layer edge is oriented
    """

    up_color = face_center_color(cube, Layer.UP)

    return tuple(cube.layers[Layer.UP][sticker] == up_color for sticker in OLL_UP_EDGE_STICKERS.values())
