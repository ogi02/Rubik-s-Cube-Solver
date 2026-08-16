# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer

# Whole-cube rotation, keyed by the face whose center sticker is yellow, that brings that face
# to DOWN. A yellow center already on DOWN needs no rotation.
ORIENTATION_TABLE: dict[Layer, str] = {
    Layer.DOWN: "",
    Layer.UP: "x2",
    Layer.FRONT: "x'",
    Layer.BACK: "x",
    Layer.LEFT: "z'",
    Layer.RIGHT: "z",
}

# Algorithm that extracts a cross edge out of the DOWN layer or the equatorial layer and into the
# UP layer, without disturbing any other DOWN-layer edge. The four UP slots have no entry: an edge
# already in the UP layer needs no extraction.
EXTRACTION_TABLE: dict[EdgeSlot, str] = {
    EdgeSlot.DF: "F2",
    EdgeSlot.DR: "R2",
    EdgeSlot.DL: "L2",
    EdgeSlot.DB: "B2",
    EdgeSlot.FR: "R U R'",
    EdgeSlot.FL: "L' U' L",
    EdgeSlot.BR: "R' U R",
    EdgeSlot.BL: "L U' L'",
}

# Algorithm that brings a UP-layer edge to UF.
ALIGNMENT_TABLE: dict[EdgeSlot, str] = {
    EdgeSlot.UF: "",
    EdgeSlot.UR: "U",
    EdgeSlot.UB: "U2",
    EdgeSlot.UL: "U'",
}

# Algorithm that inserts a UF edge into DF, keyed by whether it is already oriented (yellow on UP)
# or flipped (yellow on FRONT).
INSERTION_TABLE: dict[bool, str] = {
    True: "F2",
    False: "U' R' F R",
}


def face_center_color(cube: Cube, layer: Layer) -> Color:
    """
    Returns the color of a face's center sticker.

    :param cube: The Cube instance to read
    :param layer: The face to read the center sticker of
    :return: The center sticker's color
    """

    return cube.layers[layer][cube.size * cube.size // 2]


def find_yellow_center_layer(cube: Cube) -> Layer:
    """
    Finds the face whose center sticker is yellow.

    :param cube: The Cube instance to search
    :return: The layer whose center sticker is yellow
    """

    for layer in Layer:
        if face_center_color(cube, layer) == Color.YELLOW:
            return layer

    raise ValueError("No face has a yellow center sticker.")
