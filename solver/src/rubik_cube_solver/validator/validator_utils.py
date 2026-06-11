# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer


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
