# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.cube_nxn.edges import pivot_row, wing_colors
from rubik_cube_solver.solve.cube_nxn.routes import trial
from rubik_cube_solver.validator.validator_constants import (
    CORNER_SLOT_LAYERS,
    EDGE_CANONICAL_ORIENTATION,
    EDGE_SLOT_LAYERS,
)
from rubik_cube_solver.validator.validator_utils import (
    get_canonical_pieces,
    get_corners,
    get_edges,
    permutation_parity,
)

# Brings the twelfth edge from FR into UF, where the parity algorithms work on it.
PARITY_SETUP: str = "F'"


def oll_parity(size: int, depth: int) -> str:
    """
    Returns the OLL parity algorithm with wide turns of a given depth, which flips the wings of UF in
    the rows the wide turns reach past the outer layer, and the rows mirroring them.

    Every other edge stays paired and every center stays built; only the corners are moved.

    Example, on a 5x5, flipping the outer wings of UF, and on a 4x4, flipping the whole edge:

        >>> oll_parity(5, 2)
        "Rw U2 x Rw U2 Rw U2 Rw' U2 Lw U2 x' Lw' U2 Rw U2 Rw' U2 Rw'"
        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str(oll_parity(4, 2)))
        >>> wing_colors(cube, EdgeSlot.UF, 1)
        (<Color.GREEN: 'G'>, <Color.WHITE: 'W'>)

    :param size: The size of the cube
    :param depth: The number of layers of the wide turns, from 2 to `size // 2`
    :return: The algorithm, in standard notation
    """

    right = Move(Layer.RIGHT, Direction.CW, depth)
    left = Move(Layer.LEFT, Direction.CW, depth)

    return (
        f"{right} U2 x {right} U2 {right} U2 {right.inverse()} U2 {left} U2 x' {left.inverse()} U2 "
        f"{right} U2 {right.inverse()} U2 {right.inverse()}"
    )


def pll_parity(size: int) -> str:
    """
    Returns the PLL parity algorithm of an even cube, which swaps two edges without swapping two corners.

    Every edge stays paired and every center stays built.

    Example:

        >>> pll_parity(4)
        'Rw2 R2 U2 Rw2 R2 Uw2 Rw2 R2 Uw2'
        >>> pll_parity(6)
        '3Rw2 R2 U2 3Rw2 R2 3Uw2 3Rw2 R2 3Uw2'

    :param size: The size of the cube, an even number
    :return: The algorithm, in standard notation
    """

    inner = Move(Layer.RIGHT, Direction.DOUBLE, size // 2)
    block = Move(Layer.UP, Direction.DOUBLE, size // 2)

    return f"{inner} R2 U2 {inner} R2 {block} {inner} R2 {block}"


def flipped_edges(cube: Cube) -> int:
    """
    Returns how many edges of a cube whose edges are all paired are flipped, by the edge orientation
    of `EDGE_CANONICAL_ORIENTATION`.

    Example, on a 4x4 whose UF edge is flipped by the OLL parity algorithm:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str(oll_parity(4, 2)))
        >>> flipped_edges(Cube(4)), flipped_edges(cube)
        (0, 1)

    :param cube: The cube, with every edge paired
    :return: The number of flipped edges
    """

    return sum(edge[0] != EDGE_CANONICAL_ORIENTATION[frozenset(edge)] for edge in get_edges(cube))


def permutation_parities_differ(cube: Cube) -> bool:
    """
    Returns whether the corners and the edges of a cube whose edges are all paired are permuted with
    different parities, measured against the slots the cube's centers give each piece.

    Example, on a 4x4 before and after the PLL parity algorithm:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str(pll_parity(4)))
        >>> permutation_parities_differ(Cube(4)), permutation_parities_differ(cube)
        (False, True)

    :param cube: The cube, with every edge paired and every center built
    :return: Whether the two parities differ
    """

    corner_slots = get_canonical_pieces(cube, CORNER_SLOT_LAYERS)
    edge_slots = get_canonical_pieces(cube, EDGE_SLOT_LAYERS)

    corners = [corner_slots.index(frozenset(corner)) for corner in get_corners(cube)]
    edges = [edge_slots.index(frozenset(edge)) for edge in get_edges(cube)]

    return permutation_parity(corners) != permutation_parity(edges)


def pair_last_edge(cube: Cube) -> tuple[list[str], Cube]:
    """
    Returns the algorithms that pair the edge in UF, whose wings all hold its two colours, and the cube
    they leave.

    The wings are compared with the pivot's, from the middle of the edge outwards. A wing that is the
    other way round is flipped with the OLL parity algorithm reaching its row, which flips every wing
    outside it as well, so the rows further out are compared after it.

    Example, on a 5x5 whose outer wings of UF are flipped:

        >>> cube = Cube(5)
        >>> Rotator(cube).apply(Algorithm.from_str(oll_parity(5, 2)))
        >>> moves, cube = pair_last_edge(cube)
        >>> moves
        ["Rw U2 x Rw U2 Rw U2 Rw' U2 Lw U2 x' Lw' U2 Rw U2 Rw' U2 Rw'"]

    :param cube: The cube, with every other edge paired and every center built
    :return: The algorithms, in the order they are applied, and the cube they leave
    """

    moves = []
    pivot = wing_colors(cube, EdgeSlot.UF, pivot_row(cube.size))

    for row in range(pivot_row(cube.size) - 1, 0, -1):
        if wing_colors(cube, EdgeSlot.UF, row) != pivot:
            flip = oll_parity(cube.size, row + 1)
            moves.append(flip)
            cube = trial(cube, flip)

    return moves, cube


def build_parity(cube: Cube) -> list[str]:
    """
    Returns the algorithms that fix the parities of a big cube whose centers are built and whose edges
    are paired but the one in FR, which holds all its wings, so the cube can be solved as a 3x3.

    `PARITY_SETUP` brings the edge into UF, where `pair_last_edge` pairs it. An odd cube is then reduced.
    An even cube has no fixed middle wing, so it can still hold an odd number of flipped edges, fixed by
    flipping the edge in UF whole, and corners and edges permuted with different parities, fixed by the
    PLL parity algorithm.

    Example, on a 4x4 whose edge in FR is flipped:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str(f"{oll_parity(4, 2)} F"))
        >>> build_parity(cube)
        ["F'", "Rw U2 x Rw U2 Rw U2 Rw' U2 Lw U2 x' Lw' U2 Rw U2 Rw' U2 Rw'"]

    :param cube: The cube, of size 4 or more, with every edge but FR's paired and every center built
    :return: The algorithms, in the order they are applied
    """

    size = cube.size
    cube = trial(cube, PARITY_SETUP)
    moves, cube = pair_last_edge(cube)
    moves = [PARITY_SETUP] + moves

    if size % 2 == 1:
        return moves

    if flipped_edges(cube) % 2 == 1:
        flip = oll_parity(size, size // 2)
        moves.append(flip)
        cube = trial(cube, flip)

    if permutation_parities_differ(cube):
        moves.append(pll_parity(size))

    return moves
