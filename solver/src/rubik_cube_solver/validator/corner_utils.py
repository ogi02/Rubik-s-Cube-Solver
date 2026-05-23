# Project imports
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer


def get_corner_colors() -> list[set[Color]]:
    """
    Get the standard corner color combinations for a Rubik's Cube.

    :return: A list of sets, each representing the color combination of a corner piece.
    """

    return [
        {Color.WHITE, Color.ORANGE, Color.BLUE},
        {Color.WHITE, Color.RED, Color.BLUE},
        {Color.WHITE, Color.ORANGE, Color.GREEN},
        {Color.WHITE, Color.RED, Color.GREEN},
        {Color.YELLOW, Color.ORANGE, Color.BLUE},
        {Color.YELLOW, Color.RED, Color.BLUE},
        {Color.YELLOW, Color.ORANGE, Color.GREEN},
        {Color.YELLOW, Color.RED, Color.GREEN},
    ]


def get_corner_positions(cube_size: int) -> list[dict[Layer, tuple[int, int]]]:
    """
    Get the positions of all corner pieces on a Rubik's Cube.

    :param cube_size: The size of the cube (e.g., 2 for 2x2x2, 3 for 3x3x3)
    :return: A list of dictionaries, each representing the position of a corner piece
             with Layer keys and their corresponding indices with modulo for the orientation.
    """

    def top_left_index() -> int:
        """
        Get the index of the top-left corner piece.

        :return: The index of the top-left corner piece
        """

        return 0

    def top_right_index(cs) -> int:
        """
        Get the index of the top-right corner piece.

        :param cs: The size of the cube
        :return: The index of the top-right corner piece
        """

        return cs - 1

    def bottom_left_index(cs: int) -> int:
        """
        Get the index of the bottom-left corner piece.

        :param cs: The size of the cube
        :return: The index of the bottom-left corner piece
        """

        return (cs - 1) * cs

    def bottom_right_index(cs: int) -> int:
        """
        Get the index of the bottom-right corner piece.

        :param cs: The size of the cube
        :return: The index of the bottom-right corner piece
        """

        return cs * cs - 1

    return [
        {
            Layer.UP: (top_left_index(), 0),
            Layer.BACK: (top_right_index(cube_size), 2),
            Layer.LEFT: (top_left_index(), 1),
        },
        {
            Layer.UP: (top_right_index(cube_size), 0),
            Layer.BACK: (top_left_index(), 1),
            Layer.RIGHT: (top_right_index(cube_size), 2),
        },
        {
            Layer.UP: (bottom_left_index(cube_size), 0),
            Layer.FRONT: (top_left_index(), 1),
            Layer.LEFT: (top_right_index(cube_size), 2),
        },
        {
            Layer.UP: (bottom_right_index(cube_size), 0),
            Layer.FRONT: (top_right_index(cube_size), 2),
            Layer.RIGHT: (top_left_index(), 1),
        },
        {
            Layer.DOWN: (bottom_left_index(cube_size), 0),
            Layer.BACK: (bottom_right_index(cube_size), 1),
            Layer.LEFT: (bottom_left_index(cube_size), 2),
        },
        {
            Layer.DOWN: (bottom_right_index(cube_size), 0),
            Layer.BACK: (bottom_left_index(cube_size), 2),
            Layer.RIGHT: (bottom_right_index(cube_size), 1),
        },
        {
            Layer.DOWN: (top_left_index(), 0),
            Layer.FRONT: (bottom_left_index(cube_size), 2),
            Layer.LEFT: (bottom_right_index(cube_size), 1),
        },
        {
            Layer.DOWN: (top_right_index(cube_size), 0),
            Layer.FRONT: (bottom_right_index(cube_size), 1),
            Layer.RIGHT: (bottom_left_index(cube_size), 2),
        },
    ]
