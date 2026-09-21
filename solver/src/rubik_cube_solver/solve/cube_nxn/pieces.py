# Python imports
from typing import NamedTuple

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.center_search import CenterSearchResult, search_center


class CenterSticker(NamedTuple):
    """
    A center cell of one face, together with the colour it has to hold.
    """

    layer: Layer
    row: int
    col: int
    color: Color


def in_first_half(size: int, index: int) -> bool:
    """
    Returns whether a row or column index lies in the first half of a face - the upper rows or the
    left columns.

    :param size: The size of the cube
    :param index: The row or column index
    :return: Whether the index lies before the middle of the face
    """

    return 2 * index < size - 1


def orbit_cells(size: int, cell: tuple[int, int]) -> list[tuple[int, int]]:
    """
    Returns the four cells a center piece in `cell` can occupy on any face, in clockwise order.

    A center piece never changes its position type, so these four cells are the only places it can
    go. The clockwise order makes the index difference between two cells the number of clockwise
    quarter turns of the face that carries a piece from one to the other.

    Example, on a 6x6:

        >>> orbit_cells(6, (1, 2))
        [(1, 2), (2, 4), (4, 3), (3, 1)]

    :param size: The size of the cube
    :param cell: The cell, as (row, column)
    :return: The four cells of the position type, starting at `cell`
    """

    row, col = cell
    cells = [(row, col)]

    for _ in range(3):
        row, col = col, size - 1 - row
        cells.append((row, col))

    return cells


def fill_order(size: int) -> list[int]:
    """
    Returns the columns of a bar in the order they are filled: inner to outer, left to right.

    Example:

        >>> fill_order(6)
        [2, 3, 1, 4]
        >>> fill_order(8)
        [3, 4, 2, 5, 1, 6]

    :param size: The size of the cube
    :return: The inner columns of FRONT, in filling order
    """

    return sorted(range(1, size - 1), key=lambda col: (-min(col - 1, size - 2 - col), col))


def bar_rows(size: int) -> list[int]:
    """
    Returns the rows of FRONT a bar is staged in, in the order the bars are built.

    Bars are staged in the lower half of FRONT, innermost row first, and every row is used twice: an
    insertion carries the bar already on the target to the mirror line before laying the new one
    down, so two bars from one row fill two lines of the target. Only even cubes are built this way;
    an odd cube's middle line cannot be staged as a bar.

    Example:

        >>> bar_rows(4)
        [2, 2]
        >>> bar_rows(6)
        [3, 3, 4, 4]
        >>> bar_rows(5)
        Traceback (most recent call last):
        ValueError: Bars are staged only on even cubes of size 4 or more, got size 5

    :param size: The size of the cube, even and at least 4
    :return: The staging rows, one per bar
    """

    if size < 4 or size % 2:
        raise ValueError(f"Bars are staged only on even cubes of size 4 or more, got size {size}")

    return [row for row in range(size // 2, size - 1) for _ in (0, 1)]


def built_cells(size: int, target: Layer, inserted: list[int]) -> set[tuple[int, int]]:
    """
    Returns the cells of the target center that belong to a bar already inserted.

    A bar lands on the line of the target with the same index as the row it was staged in, and the
    next insertion from that row moves it to the mirror line `size - 1 - row`. A row staged once has
    therefore filled its own line, and a row staged twice has filled that line and its mirror. A
    bar arrives on LEFT and RIGHT as a row and on DOWN as a column.

    The cells are worked out from the insertions rather than read off the face: a line that holds
    the colour by chance is not finished, and a later bar is free to replace it.

    Example, on a 6x6:

        >>> sorted(built_cells(6, Layer.RIGHT, [3]))
        [(3, 1), (3, 2), (3, 3), (3, 4)]
        >>> sorted(built_cells(6, Layer.DOWN, [3, 3]))
        [(1, 2), (1, 3), (2, 2), (2, 3), (3, 2), (3, 3), (4, 2), (4, 3)]

    :param size: The size of the cube
    :param target: The face the center is being built on
    :param inserted: The staging rows of the bars inserted so far, in order
    :return: The cells of the target that hold a finished bar
    """

    inner = range(1, size - 1)
    lines = set(inserted) | {size - 1 - row for row in inserted if inserted.count(row) > 1}

    if target is Layer.DOWN:
        return {(row, line) for line in lines for row in inner}

    return {(line, col) for line in lines for col in inner}


def rank_candidates(
    cube: Cube,
    color: Color,
    cell: tuple[int, int],
    priority: tuple[tuple[Layer, ...], ...],
    target: Layer,
    finished: set[tuple[int, int]],
) -> list[CenterSearchResult]:
    """
    Returns the pieces that can fill a cell of FRONT, in the order they should be tried.

    Pieces are ordered by their face's place in `priority` - tier by tier, and within a tier in the
    order listed - then by their cell. A piece on a face missing from `priority` is not a candidate,
    and neither is a piece in a finished cell of the target.

    Example, on a 4x4 turned with `z' Dw`, which leaves yellow's upper half on RIGHT and carries its
    lower half to BACK. The two BACK pieces come first, since BACK is in the first tier:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("z' Dw"))
        >>> rank_candidates(cube, Color.YELLOW, (2, 1), CENTERS_PLAN[0].priority, Layer.RIGHT, set())
        [CenterSearchResult(layer=<Layer.BACK: 'B'>, row=2, col=1),
         CenterSearchResult(layer=<Layer.BACK: 'B'>, row=2, col=2),
         CenterSearchResult(layer=<Layer.RIGHT: 'R'>, row=1, col=1),
         CenterSearchResult(layer=<Layer.RIGHT: 'R'>, row=1, col=2)]

    :param cube: The cube
    :param color: The colour being built
    :param cell: The FRONT cell to fill, as (row, column)
    :param priority: The source faces, grouped into tiers from most to least preferred
    :param target: The face the center is being built on
    :param finished: The cells of the target that hold a finished bar
    :return: The candidate pieces, best first
    """

    order = [layer for tier in priority for layer in tier]
    candidates = [
        piece
        for piece in search_center(cube, color, *cell)
        if piece.layer in order and not (piece.layer is target and (piece.row, piece.col) in finished)
    ]

    return sorted(candidates, key=lambda piece: (order.index(piece.layer), piece.row, piece.col))


def protected(
    cube: Cube,
    color: Color,
    cell: tuple[int, int],
    target: Layer,
    inserted: list[int],
    keep: list[CenterSticker],
) -> list[CenterSticker]:
    """
    Returns every position that must still hold its colour after a FRONT cell is filled.

    These are the bar cells filled before this one, the cells of the target holding a finished bar,
    and the finished centers in `keep`. A bar cell that holds the colour but comes later in the fill
    order is not protected: it is filled in its own turn, and keeping it would only rule out routes.

    Example, on a solved 6x6, filling FRONT (3, 1) with one bar from row 3 already on RIGHT. Columns
    2 and 3 come before column 1 in the fill order, and row 3 of RIGHT holds the inserted bar:

        >>> protected(Cube(6), Color.GREEN, (3, 1), Layer.RIGHT, [3], [])
        [CenterSticker(layer=<Layer.FRONT: 'F'>, row=3, col=2, color=<Color.GREEN: 'G'>),
         CenterSticker(layer=<Layer.FRONT: 'F'>, row=3, col=3, color=<Color.GREEN: 'G'>),
         CenterSticker(layer=<Layer.RIGHT: 'R'>, row=3, col=1, color=<Color.GREEN: 'G'>),
         CenterSticker(layer=<Layer.RIGHT: 'R'>, row=3, col=2, color=<Color.GREEN: 'G'>),
         CenterSticker(layer=<Layer.RIGHT: 'R'>, row=3, col=3, color=<Color.GREEN: 'G'>),
         CenterSticker(layer=<Layer.RIGHT: 'R'>, row=3, col=4, color=<Color.GREEN: 'G'>)]

    :param cube: The cube
    :param color: The colour being built
    :param cell: The FRONT cell being filled, as (row, column)
    :param target: The face the center is being built on
    :param inserted: The staging rows of the bars inserted so far, in order
    :param keep: The cells of the finished centers
    :return: The cells to keep, each with the colour it must hold
    """

    size = cube.size
    row, col = cell
    order = fill_order(size)
    bar = [
        CenterSticker(Layer.FRONT, row, earlier, color)
        for earlier in order[: order.index(col)]
        if cube.layers[Layer.FRONT][row * size + earlier] is color
    ]
    built = [CenterSticker(target, r, c, color) for r, c in sorted(built_cells(size, target, inserted))]

    return bar + built + list(keep)


def finished_centers(cube: Cube, done: list[Color]) -> list[CenterSticker]:
    """
    Returns every cell of the centers already built, tagged with the colour it has to keep.

    A face counts when its whole center is one of the colours in `done`. FRONT is never counted: it
    is the staging face, every route turns it, and a center that comes up there by chance is not a
    finished one.

    Example, on a solved 4x4 once yellow is built:

        >>> finished_centers(Cube(4), [Color.YELLOW])
        [CenterSticker(layer=<Layer.DOWN: 'D'>, row=1, col=1, color=<Color.YELLOW: 'Y'>),
         CenterSticker(layer=<Layer.DOWN: 'D'>, row=1, col=2, color=<Color.YELLOW: 'Y'>),
         CenterSticker(layer=<Layer.DOWN: 'D'>, row=2, col=1, color=<Color.YELLOW: 'Y'>),
         CenterSticker(layer=<Layer.DOWN: 'D'>, row=2, col=2, color=<Color.YELLOW: 'Y'>)]

    :param cube: The cube
    :param done: The colours whose centers are finished
    :return: The cells to keep, each with its colour
    """

    size = cube.size
    cells = [(row, col) for row in range(1, size - 1) for col in range(1, size - 1)]
    keep = []

    for face in Layer:
        if face is Layer.FRONT:
            continue

        colors = {cube.layers[face][row * size + col] for row, col in cells}

        if len(colors) == 1 and (color := colors.pop()) in done:
            keep += [CenterSticker(face, row, col, color) for row, col in cells]

    return keep
