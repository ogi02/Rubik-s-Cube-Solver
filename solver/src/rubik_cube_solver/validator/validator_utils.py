# Project imports
from math import ceil

from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.validator.validator_constants import WING_EDGES_LAYER_PAIRS


def get_corners(cube: Cube) -> list[tuple[Color, Color, Color]]:
    """
    Returns a list of 8 corner tuples, one per corner, each containing the 3 sticker
    colors in the canonical clockwise face-sequence order.

    :param cube: The Cube instance
    :return: List of 8 corner color tuples
    """

    n = cube.size
    layers = cube.layers
    # Each entry: (face1_color, face2_color, face3_color) in CW order
    return [
        # UFL
        (layers[Layer.UP][n * (n - 1)], layers[Layer.FRONT][0], layers[Layer.LEFT][n - 1]),
        # UFR
        (layers[Layer.UP][n * n - 1], layers[Layer.RIGHT][0], layers[Layer.FRONT][n - 1]),
        # UBL
        (layers[Layer.UP][0], layers[Layer.LEFT][0], layers[Layer.BACK][n - 1]),
        # UBR
        (layers[Layer.UP][n - 1], layers[Layer.BACK][0], layers[Layer.RIGHT][n - 1]),
        # DFL
        (layers[Layer.DOWN][0], layers[Layer.LEFT][n * n - 1], layers[Layer.FRONT][n * (n - 1)]),
        # DFR
        (layers[Layer.DOWN][n - 1], layers[Layer.FRONT][n * n - 1], layers[Layer.RIGHT][n * (n - 1)]),
        # DBL
        (layers[Layer.DOWN][n * (n - 1)], layers[Layer.BACK][n * n - 1], layers[Layer.LEFT][n * (n - 1)]),
        # DBR
        (layers[Layer.DOWN][n * n - 1], layers[Layer.RIGHT][n * n - 1], layers[Layer.BACK][n * (n - 1)]),
    ]


def get_index_formulas(n: int, row: int, col: int) -> list[int]:
    """
    Returns the 4 sticker indices corresponding to the center pieces of the same type as the piece at (row, col)
    in the inner grid of a face of size n.

    :param n: Size of the cube
    :param row: Row index of the center piece in the inner grid (1-indexed)
    :param col: Column index of the center piece in the inner grid (1-indexed)
    :return: List of 4 sticker indices for the center pieces of the same type
    """

    return [
        n * row + col,
        n * col + n - row - 1,
        n * n - n * col - n + row,
        n * n - n * row - col - 1,
    ]


def get_centers(cube: Cube) -> list[tuple[Color, int, int]]:
    """
    Returns all center sticker data for a big cube (N >= 4).
    For each face, iterates over the inner grid positions that are centers
    (not corners, not edges). For odd N, excludes the absolute center sticker.

    Returns a list of (color, row_offset, col_offset) tuples, where (row_offset, col_offset)
    is the position relative to the face center (absolute center is (0, 0)).

    The following 4 mathematical formulas get all center pieces of the same type
    and are applicable regardless of the starting center piece:

    1. n * row + col
    2. n * col + n - row - 1
    3. n ^ 2 - n * col - n + row
    4. n ^ 2 - n * row - col - 1

    Layout of a 6x6 cube:
     0  1  2  3  4  5
     6  7  8  9 10 11
    12 13 14 15 16 17
    18 19 20 21 22 23
    24 25 26 27 28 29
    30 31 32 33 34 35

    Example 1: row = 1, col = 1
    1. n * row + col = 6 * 1 + 1 = 7
    2. n * col + n - row - 1 = 6 * 1 + 6 - 1 - 1 = 10
    3. n ^ 2 - n * col - n + row = 36 - 6 * 1 - 6 + 1 = 25
    4. n ^ 2 - n * row - col - 1 = 36 - 6 * 1 - 1 - 1 = 28

    Example 2: row = 2, col = 1
    1. n * row + col = 6 * 2 + 1 = 13
    2. n * col + n - row - 1 = 6 * 1 + 6 - 2 - 1 = 9
    3. n ^ 2 - n * col - n + row = 36 - 6 * 1 - 6 + 2 = 26
    4. n ^ 2 - n * row - col - 1 = 36 - 6 * 2 - 1 - 1 = 22

    When looking at the center pieces:
     7  8  9 10
    13 14 15 16
    19 20 21 22
    25 26 27 28

    Taking the pieces from the second quadrant will iterate through all the pieces after the formulas are applied.

    :param cube: The Cube instance
    :return: List of (Color, row_offset, col_offset) tuples
    """

    n = cube.size
    layers = cube.layers
    centers: list[tuple[Color, int, int]] = []

    for face in Layer:
        face_stickers = layers[face]
        for row in range(1, ceil(n / 2)):
            for col in range(1, ceil(n / 2)):
                # Skip absolute center piece of odd sized cubes
                if n % 2 == 1 and row == n // 2 and col == n // 2:
                    continue
                # Calculate the 4 formulas to take the 4 center pieces of this type
                index_formulas = get_index_formulas(n, row, col)
                for index in index_formulas:
                    centers.append((face_stickers[index], row, col))

    return centers


def get_edges(cube: Cube) -> list[tuple[Color, Color]]:
    """
    Returns a list of 12 edge tuples in canonical order (UF, UB, UL, UR, DF, DB, DL, DR, FL, FR, BL, BR).
    Each tuple is (face1_color, face2_color) as defined by the sticker index table.

    :param cube: The Cube instance
    :return: List of 12 edge color tuples
    """

    layers = cube.layers
    size = cube.size

    # Define location of middle edges of an odd sized cube
    top_edge = size // 2
    left_edge = size * (size // 2)
    right_edge = size * (size // 2) + size - 1
    bottom_edge = size * size - size // 2 - 1

    return [
        # UF
        (layers[Layer.UP][bottom_edge], layers[Layer.FRONT][top_edge]),
        # UB
        (layers[Layer.UP][top_edge], layers[Layer.BACK][top_edge]),
        # UL
        (layers[Layer.UP][left_edge], layers[Layer.LEFT][top_edge]),
        # UR
        (layers[Layer.UP][right_edge], layers[Layer.RIGHT][top_edge]),
        # DF
        (layers[Layer.DOWN][top_edge], layers[Layer.FRONT][bottom_edge]),
        # DB
        (layers[Layer.DOWN][bottom_edge], layers[Layer.BACK][bottom_edge]),
        # DL
        (layers[Layer.DOWN][left_edge], layers[Layer.LEFT][bottom_edge]),
        # DR
        (layers[Layer.DOWN][right_edge], layers[Layer.RIGHT][bottom_edge]),
        # FL
        (layers[Layer.FRONT][left_edge], layers[Layer.LEFT][right_edge]),
        # FR
        (layers[Layer.FRONT][right_edge], layers[Layer.RIGHT][left_edge]),
        # BL
        (layers[Layer.BACK][right_edge], layers[Layer.LEFT][left_edge]),
        # BR
        (layers[Layer.BACK][left_edge], layers[Layer.RIGHT][right_edge]),
    ]


def wing_edge_indices(primary_layer: Layer, secondary_layer: Layer, n: int, k: int) -> tuple[int, int]:
    """
    Returns the (primary_face_index, secondary_face_index) for every pair of (primary_layer, secondary_layer)
    at wing slot k (1-indexed) for a cube of size n.

    :param primary_layer: The primary layer
    :param secondary_layer: The secondary layer
    :param n: Cube size
    :param k: Wing slot index in range(1, n // 2)
    :return: Tuple of (primary_face_sticker_index, secondary_face_sticker_index)
    """

    if primary_layer == Layer.UP:
        if secondary_layer == Layer.LEFT:
            return n * k, k
        elif secondary_layer == Layer.RIGHT:
            return n * (n - k) - 1, k
        elif secondary_layer == Layer.FRONT:
            return n * (n - 1) + k, k
        else:
            return n - k - 1, k
    elif primary_layer == Layer.DOWN:
        if secondary_layer == Layer.LEFT:
            return n * k, n * n - k - 1
        elif secondary_layer == Layer.RIGHT:
            return n * (n - k) - 1, n * n - k - 1
        elif secondary_layer == Layer.FRONT:
            return n - k - 1, n * n - k - 1
        else:
            return n * (n - 1) + k, n * n - k - 1
    elif primary_layer == Layer.LEFT:
        if secondary_layer == Layer.UP:
            return n - k - 1, n * (n - k - 1)
        elif secondary_layer == Layer.DOWN:
            return n * (n - 1) + k, n * (n - k - 1)
        elif secondary_layer == Layer.FRONT:
            return n * (n - k) - 1, n * (n - k - 1)
        else:
            return n * k, n * (k + 1) - 1
    elif primary_layer == Layer.RIGHT:
        if secondary_layer == Layer.UP:
            return n - k - 1, n * (k + 1) - 1
        elif secondary_layer == Layer.DOWN:
            return n * (n - 1) + k, n * (k + 1) - 1
        elif secondary_layer == Layer.FRONT:
            return n * k, n * (k + 1) - 1
        else:
            return n * (n - k) - 1, n * (n - k - 1)
    elif primary_layer == Layer.FRONT:
        if secondary_layer == Layer.UP:
            return n - k - 1, n * n - k - 1
        elif secondary_layer == Layer.DOWN:
            return n * (n - 1) + k, k
        elif secondary_layer == Layer.LEFT:
            return n * k, n * (k + 1) - 1
        else:
            return n * (n - k) - 1, n * (n - k - 1)
    else:
        if secondary_layer == Layer.UP:
            return n - k - 1, k
        elif secondary_layer == Layer.DOWN:
            return n * (n - 1) + k, n * n - k - 1
        elif secondary_layer == Layer.LEFT:
            return n * (n - k) - 1, n * (n - k - 1)
        else:
            return n * k, n * (k + 1) - 1


def get_wing_edges(cube: Cube) -> list[tuple[int, Color, Color]]:
    """
    Returns a list of all directed wing edge sticker pairs for a big cube (N >= 4).
    For each of the 12 canonical directed edges and their reverses, and for each wing slot,
    returns the (k, primary_color, secondary_color) pair.

    Total count: 24 * (N // 2 - 1) pairs.

    :param cube: The Cube instance
    :return: List of directed wing edge color pairs
    """

    n = cube.size
    layers = cube.layers
    wing_edges: list[tuple[int, Color, Color]] = []

    for primary_layer, secondary_layers in WING_EDGES_LAYER_PAIRS:
        for secondary_layer in secondary_layers:
            for k in range(1, ceil(n / 2)):
                primary_layer_index, secondary_layer_index = wing_edge_indices(primary_layer, secondary_layer, n, k)
                primary_layer_color = layers[primary_layer][primary_layer_index]
                secondary_layer_color = layers[secondary_layer][secondary_layer_index]
                wing_edges.append((k, primary_layer_color, secondary_layer_color))

    return wing_edges
