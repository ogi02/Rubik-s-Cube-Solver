# Python imports
from typing import NamedTuple

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.validator.validator_utils import get_index_formulas


class CenterSearchResult(NamedTuple):
    """
    The location of a center piece: the face it lies on and its row and column within that face.
    """

    layer: Layer
    row: int
    col: int


def search_center(cube: Cube, color: Color, row: int, col: int) -> list[CenterSearchResult]:
    """
    Searches a big cube (N >= 4) for every center piece of the given color and position type.

    A center piece is identified by its color and its position relative to the face it lies on,
    because the four center pieces of one type on one face are interchangeable. The position type
    is the set of four cells a piece can occupy on a face - the ones that map onto each other when
    the face is turned - so any of those four cells names the same type: on a 5x5 cube (1, 1) and
    (3, 3) both mean an x center, while (1, 2) and (2, 1) both mean a + center.

    A solved big cube has exactly four pieces of every color and position type, spread over the six
    faces of a scrambled one. The pieces move as soon as the cube is turned, so a returned location
    is only valid until the next algorithm is applied.

    :param cube: The Cube instance to search
    :param color: The color of the center pieces
    :param row: The row of a cell of the searched position type, in range(1, size - 1)
    :param col: The column of a cell of the searched position type, in range(1, size - 1)
    :return: The location of every center piece of that color and position type, in face order
    """

    size = cube.size

    if size < 4:
        raise ValueError(f"Center search is supported only on big cubes, got size {size}")

    if not 1 <= row <= size - 2 or not 1 <= col <= size - 2:
        raise ValueError(f"Invalid center piece position: row {row}, col {col}.")

    if size % 2 == 1 and row == size // 2 and col == size // 2:
        raise ValueError(f"Fixed center piece position: row {row}, col {col}.")

    indices = sorted(get_index_formulas(size, row, col))

    return [
        CenterSearchResult(layer, index // size, index % size)
        for layer in Layer
        for index in indices
        if cube.layers[layer][index] == color
    ]
