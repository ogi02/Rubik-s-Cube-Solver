# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.center_search import CenterSearchResult, search_center
from rubik_cube_solver.solve.cube_nxn.pieces import in_first_half, orbit_cells

# The faces a column slice of FRONT visits, in the order one clockwise turn of it (as seen from
# RIGHT) carries them.
CENTERS_COLUMN_SLICE_CYCLE: tuple[Layer, ...] = (Layer.FRONT, Layer.UP, Layer.BACK, Layer.DOWN)

# The index into `orbit_cells` of the cell a column slice collects from on BACK. BACK is entered
# half a turn round from UP and DOWN, so its collecting cell is the one opposite the FRONT cell.
CENTERS_BACK_OFFSET: int = 2


def trial(cube: Cube, notation: str) -> Cube:
    """
    Returns a copy of the cube with an algorithm applied, leaving the cube itself untouched.

    :param cube: The cube
    :param notation: The algorithm, in standard notation
    :return: The copy, turned
    """

    result = Cube(cube.size, {layer: list(stickers) for layer, stickers in cube.layers.items()})
    Rotator(result).apply(Algorithm.from_str(notation))

    return result


def inverse_of(notation: str) -> str:
    """
    Returns the algorithm that undoes an algorithm.

    Example:

        >>> inverse_of("3Rw Rw' F")
        "F' Rw 3Rw'"

    :param notation: The algorithm, in standard notation
    :return: The inverse, in standard notation
    """

    return str(Algorithm.from_str(notation).inverse())


def quarter_direction(quarters: int) -> Direction:
    """
    Returns the direction that turns a face by a number of clockwise quarter turns.

    :param quarters: The number of clockwise quarter turns, not a multiple of 4
    :return: The direction that performs them
    """

    match quarters % 4:
        case 1:
            return Direction.CW
        case 2:
            return Direction.DOUBLE
        case 3:
            return Direction.CCW
        case _:
            raise ValueError(f"Invalid value {quarters} for a number of quarter turns")


def column_slice(size: int, col: int, direction: Direction) -> str:
    """
    Returns the turn of the single layer holding the inner column `col` of FRONT, reached from the
    nearer side.

    The block ending at the layer is turned and the block in front of it is turned back. The two
    turns share an axis, so only the one layer moves: no other column of FRONT, and not the center
    on RIGHT or LEFT. The direction is as seen from RIGHT, so it is inverted when the layer is
    reached from LEFT.

    Example, on a 6x6:

        >>> column_slice(6, 4, Direction.CW)
        "Rw R'"
        >>> column_slice(6, 2, Direction.CW)
        "3Lw' Lw"
        >>> column_slice(6, 1, Direction.DOUBLE)
        'Lw2 L2'

    :param size: The size of the cube
    :param col: The column of FRONT, from 1 to `size - 2`
    :param direction: The direction of the turn, as seen from RIGHT
    :return: The turn, in standard notation
    """

    if in_first_half(size, col):
        face, depth, direction = Layer.LEFT, col + 1, direction.inverse()
    else:
        face, depth = Layer.RIGHT, size - col

    return f"{Move(face, direction, depth)} {Move(face, direction.inverse(), depth - 1)}"


def align_turn(size: int, cell: tuple[int, int], piece: CenterSearchResult) -> str:
    """
    Returns the turn of the source face that stands a piece where the column slice for `cell` will
    collect it.

    The slice collects from the first cell of the orbit on UP and DOWN and from the third on BACK, so
    the turn is the difference between that index and the piece's own.

    Example, on a 6x6, filling FRONT (3, 2), whose orbit is (3, 2), (2, 2), (2, 3), (3, 3). The slice
    collects from UP (3, 2) and from BACK (2, 3):

        >>> align_turn(6, (3, 2), CenterSearchResult(Layer.UP, 2, 2))
        "U'"
        >>> align_turn(6, (3, 2), CenterSearchResult(Layer.BACK, 3, 2))
        'B2'
        >>> align_turn(6, (3, 2), CenterSearchResult(Layer.BACK, 2, 3))
        ''

    :param size: The size of the cube
    :param cell: The FRONT cell being filled
    :param piece: The piece, on UP, BACK or DOWN
    :return: The turn, or an empty string if the piece already stands there
    """

    offset = CENTERS_BACK_OFFSET if piece.layer is Layer.BACK else 0
    quarters = (offset - orbit_cells(size, cell).index((piece.row, piece.col))) % 4

    if not quarters:
        return ""

    return str(Move(piece.layer, quarter_direction(quarters), 1))


def direct_route(size: int, cell: tuple[int, int], piece: CenterSearchResult, restore: bool) -> str:
    """
    Returns the route that brings a piece on UP, BACK or DOWN into the bar.

    The source face is turned to stand the piece where the column slice collects, and the slice
    carries it into the bar. The slice crosses the bar in this one cell, so the rest of the bar
    stays put. With `restore` the slice is also turned back, with FRONT turned out of its way and
    back again, so that the other faces it carried return - all but the source face.

    The slice turns the opposite way to the number of steps the source is along the slice cycle, so a
    piece on UP comes down with the slice turning like `R'`, one on BACK with a half turn and one on
    DOWN with the slice turning like `R`.

    Example, on a 6x6, filling FRONT (3, 2), whose column is reached from LEFT:

        >>> direct_route(6, (3, 2), CenterSearchResult(Layer.UP, 2, 2), False)
        "U' 3Lw Lw'"
        >>> direct_route(6, (3, 2), CenterSearchResult(Layer.UP, 2, 2), True)
        "U' 3Lw Lw' F' Lw 3Lw' F"
        >>> direct_route(6, (3, 2), CenterSearchResult(Layer.BACK, 2, 3), False)
        '3Lw2 Lw2'
        >>> direct_route(6, (3, 2), CenterSearchResult(Layer.DOWN, 3, 2), False)
        "3Lw' Lw"

    :param size: The size of the cube
    :param cell: The FRONT cell being filled
    :param piece: The piece, on UP, BACK or DOWN
    :param restore: Whether to turn the slice back
    :return: The route, in standard notation
    """

    _, col = cell
    toward_front = quarter_direction(CENTERS_COLUMN_SLICE_CYCLE.index(piece.layer)).inverse()
    turn = column_slice(size, col, toward_front)
    align = align_turn(size, cell, piece)
    parts = [align, turn]

    if restore:
        stand = str(Move(Layer.FRONT, Direction.CCW if in_first_half(size, col) else Direction.CW, 1))
        parts += [stand, inverse_of(turn), inverse_of(stand)]

    return " ".join(part for part in parts if part)


def extraction(size: int, side: Layer, row: int) -> str:
    """
    Returns the conjugate that moves a piece from LEFT or RIGHT onto BACK.

    The block reaching in from the nearer of UP and DOWN carries the piece round to BACK, a half turn
    of BACK takes it out of the block, and the block goes back. Only BACK and the side face the piece
    came from are changed.

    Example, on a 6x6:

        >>> extraction(6, Layer.LEFT, 1)
        "Uw B2 Uw'"
        >>> extraction(6, Layer.RIGHT, 3)
        "3Dw B2 3Dw'"

    :param size: The size of the cube
    :param side: The face the piece is on, LEFT or RIGHT
    :param row: The row the piece is in
    :return: The conjugate, in standard notation
    """

    top = in_first_half(size, row)
    pole = Layer.UP if top else Layer.DOWN
    depth = row + 1 if top else size - row
    direction = Direction.CW if (side is Layer.LEFT) == top else Direction.CCW

    over = Move(Layer.BACK, Direction.DOUBLE, 1)

    return f"{Move(pole, direction, depth)} {over} {Move(pole, direction.inverse(), depth)}"


def across_routes(cube: Cube, color: Color, cell: tuple[int, int], piece: CenterSearchResult) -> list[str]:
    """
    Returns the routes that bring a piece on LEFT or RIGHT into the bar.

    The piece is moved onto BACK with `extraction` and brought in from there with a bare
    `direct_route`, one route for each piece of the colour on BACK. Where the piece lands on BACK is
    read off the cube rather than worked out.

    Example, on a 4x4 turned with `z' Dw`, filling FRONT (2, 1) from RIGHT (1, 1):

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("z' Dw"))
        >>> across_routes(cube, Color.YELLOW, (2, 1), CenterSearchResult(Layer.RIGHT, 1, 1))
        ["Uw' B2 Uw B2 Lw2 L2", "Uw' B2 Uw B' Lw2 L2"]

    :param cube: The cube
    :param color: The colour being built
    :param cell: The FRONT cell being filled
    :param piece: The piece, on LEFT or RIGHT
    :return: The candidate routes, in standard notation
    """

    moved = extraction(cube.size, piece.layer, piece.row)
    parked = trial(cube, moved)

    return [
        f"{moved} {direct_route(cube.size, cell, back, False)}"
        for back in search_center(parked, color, *cell)
        if back.layer is Layer.BACK
    ]


def lift(size: int, col: int) -> str:
    """
    Returns the conjugate that moves a piece from DOWN onto UP.

    The block reaching in from the nearer of LEFT and RIGHT is turned twice, UP is turned twice and
    the block is turned twice again. The block turns cancel on every face except UP and DOWN.

    Example, on a 6x6:

        >>> lift(6, 1)
        'Lw2 U2 Lw2'
        >>> lift(6, 3)
        '3Rw2 U2 3Rw2'

    :param size: The size of the cube
    :param col: The column of DOWN the piece is in
    :return: The conjugate, in standard notation
    """

    if in_first_half(size, col):
        block = Move(Layer.LEFT, Direction.DOUBLE, col + 1)
    else:
        block = Move(Layer.RIGHT, Direction.DOUBLE, size - col)

    return f"{block} {Move(Layer.UP, Direction.DOUBLE, 1)} {block}"


def target_routes(cube: Cube, color: Color, cell: tuple[int, int], piece: CenterSearchResult) -> list[str]:
    """
    Returns the routes that bring a piece on DOWN into the bar while the center is built on DOWN.

    A column slice fetching from DOWN would take a column of the center being built, so the piece is
    first moved onto UP with `lift` and brought in from there with `direct_route`, bare and
    restoring. Where it lands on UP is read off the cube rather than worked out.

    :param cube: The cube
    :param color: The colour being built
    :param cell: The FRONT cell being filled
    :param piece: The piece, on DOWN
    :return: The candidate routes, in standard notation
    """

    moved = lift(cube.size, piece.col)
    lifted = trial(cube, moved)

    return [
        f"{moved} {direct_route(cube.size, cell, up, restore)}"
        for up in search_center(lifted, color, *cell)
        if up.layer is Layer.UP
        for restore in (False, True)
    ]


def staging_routes(size: int) -> list[str]:
    """
    Returns the routes that can bring a piece already on FRONT into another cell of the bar.

    No slice carries a FRONT center to another FRONT cell, so every route turns FRONT itself. There
    are two shapes:

    - a commutator on a single-layer column slice, `F slice F' slice'`, which changes only FRONT and
      the faces the slice visits;
    - a long form, `F x U' x' F y F y' F`, which changes no center outside FRONT and UP.

    The commutators come first, since they are shorter. Every direction, column and depth is listed;
    which route fills the cell without breaking anything is left to the cube.

    Example, on a 6x6:

        >>> len(staging_routes(6))
        45
        >>> staging_routes(6)[0], staging_routes(6)[-1]
        ("F Lw' L F' L' Lw", "F 3Rw U' 3Rw' F 3Lw F 3Lw' F")

    :param size: The size of the cube
    :return: The candidate routes, in standard notation
    """

    front = {direction: str(Move(Layer.FRONT, direction, 1)) for direction in Direction}
    up = {direction: str(Move(Layer.UP, direction, 1)) for direction in Direction}
    routes = []

    for col in range(1, size - 1):
        for turn in Direction:
            cut = column_slice(size, col, turn)
            routes += [f"{front[over]} {cut} {front[over.inverse()]} {inverse_of(cut)}" for over in Direction]

    turn = front[Direction.CW]
    for right in range(1, size // 2 + 1):
        for left in range(1, size // 2 + 1):
            x, x_back = Move(Layer.RIGHT, Direction.CW, right), Move(Layer.RIGHT, Direction.CCW, right)
            y, y_back = Move(Layer.LEFT, Direction.CW, left), Move(Layer.LEFT, Direction.CCW, left)
            routes.append(f"{turn} {x} {up[Direction.CCW]} {x_back} {turn} {y} {turn} {y_back} {turn}")

    return routes


def insertion(size: int, row: int, target: Layer) -> str:
    """
    Returns the algorithm that moves a finished bar from FRONT into the center being built.

    A block reaching as far as the bar carries it onto the target, the target is turned twice, the
    block goes back and the target is turned twice again. The bar already on the target is carried
    to the mirror line by the two half turns, so two bars staged in one row fill two lines. LEFT and
    RIGHT receive the bar as a row; DOWN is off the bar's axis, so the bar is first stood up with
    `F'` and arrives as a column. Only FRONT and the target are changed.

    Example, on a 6x6:

        >>> insertion(6, 3, Layer.RIGHT)
        "3Dw R2 3Dw' R2"
        >>> insertion(6, 3, Layer.LEFT)
        "3Dw' L2 3Dw L2"
        >>> insertion(6, 4, Layer.DOWN)
        "F' Rw' D2 Rw D2"

    :param size: The size of the cube
    :param row: The row of FRONT holding the bar
    :param target: The face the center is being built on: LEFT, RIGHT or DOWN
    :return: The algorithm, in standard notation
    """

    depth = size - row
    over = Move(target, Direction.DOUBLE, 1)

    match target:
        case Layer.RIGHT:
            stand, block, carry = [], Layer.DOWN, Direction.CW
        case Layer.LEFT:
            stand, block, carry = [], Layer.DOWN, Direction.CCW
        case Layer.DOWN:
            stand, block, carry = [Move(Layer.FRONT, Direction.CCW, 1)], Layer.RIGHT, Direction.CCW
        case _:
            raise ValueError(f"Invalid value {target} for the face a center is built on")

    moves = stand + [Move(block, carry, depth), over, Move(block, carry.inverse(), depth), over]

    return " ".join(str(move) for move in moves)
