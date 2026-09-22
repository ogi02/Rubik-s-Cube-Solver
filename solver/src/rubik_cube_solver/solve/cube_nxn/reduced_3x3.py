# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Layer import Layer


def as_3x3(cube: Cube) -> Cube:
    """
    Returns the 3x3 a reduced big cube stands for, built from its corners, the outer wing of each edge and
    a center sticker of each face.

    Once every center is built and every edge is paired, those stickers speak for the whole piece, so the
    3x3 turns exactly as the big cube does under outer-face turns and whole-cube rotations. A solution
    found for the 3x3 therefore solves the big cube when applied to it unchanged.

    Example, on a 5x5 turned only by its outer faces, which stands for the 3x3 turned the same way:

        >>> big = Cube(5)
        >>> Rotator(big).apply(Algorithm.from_str("R U F' L2"))
        >>> small = Cube(3)
        >>> Rotator(small).apply(Algorithm.from_str("R U F' L2"))
        >>> as_3x3(big).layers == small.layers
        True

    :param cube: The big cube, with every center built and every edge paired
    :return: The 3x3
    """

    size = cube.size
    cells = (0, 1, size - 1)

    return Cube(3, {face: [cube.layers[face][row * size + col] for row in cells for col in cells] for face in Layer})
