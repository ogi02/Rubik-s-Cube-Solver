# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.move_cancellation import combine
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


def deep_move(size: int, face: Layer, direction: Direction, depth: int) -> str:
    """
    Returns the turn of the block of `depth` layers from a face, at any depth.

    A block of at most half the cube is an ordinary wide move. A deeper one cannot be written as
    one move, so it is written as the whole-cube rotation that turns like the face, followed by the
    block of the opposite face that stays behind, turned the same way to undo the rotation there.
    This is how the middle slice of an odd cube is turned.

    Example, on a 5x5:

        >>> deep_move(5, Layer.RIGHT, Direction.CW, 2)
        'Rw'
        >>> deep_move(5, Layer.RIGHT, Direction.CW, 3)
        'x Lw'
        >>> deep_move(5, Layer.DOWN, Direction.CCW, 3)
        "y Uw'"

    :param size: The size of the cube
    :param face: The face the block is reached from
    :param direction: The direction of the turn, as seen from the face
    :param depth: The number of layers in the block, from 1 to `size - 1`
    :return: The turn, in standard notation
    """

    if depth <= size // 2:
        return str(Move(face, direction, depth))

    rotation = Move(face.axis(), direction if face.turns_with_axis() else direction.inverse(), 1)

    return f"{rotation} {Move(face.opposite(), direction, size - depth)}"


def column_slice(size: int, col: int, direction: Direction) -> str:
    """
    Returns the turn of the single layer holding the inner column `col` of FRONT, reached from the
    nearer side.

    The block ending at the layer is turned and the block in front of it is turned back. The two
    turns share an axis, so only the one layer moves: no other column of FRONT, and not the center
    on RIGHT or LEFT. The direction is as seen from RIGHT, so it is inverted when the layer is
    reached from LEFT. The middle column of an odd cube is reached from RIGHT with a `deep_move`,
    and it carries the fixed centers of FRONT, UP, BACK and DOWN with it.

    Example, on a 6x6 and on a 5x5:

        >>> column_slice(6, 4, Direction.CW)
        "Rw R'"
        >>> column_slice(6, 2, Direction.CW)
        "3Lw' Lw"
        >>> column_slice(6, 1, Direction.DOUBLE)
        'Lw2 L2'
        >>> column_slice(5, 2, Direction.CW)
        "x Lw Rw'"

    :param size: The size of the cube
    :param col: The column of FRONT, from 1 to `size - 2`
    :param direction: The direction of the turn, as seen from RIGHT
    :return: The turn, in standard notation
    """

    if in_first_half(size, col):
        face, depth, direction = Layer.LEFT, col + 1, direction.inverse()
    else:
        face, depth = Layer.RIGHT, size - col

    return f"{deep_move(size, face, direction, depth)} {Move(face, direction.inverse(), depth - 1)}"


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


def extraction(size: int, side: Layer, row: int, over: Direction) -> str:
    """
    Returns the conjugate that moves a piece from LEFT or RIGHT onto BACK.

    The block reaching in from the nearer of UP and DOWN carries the piece round to BACK, a turn of
    BACK takes it out of the block, and the block goes back. Only BACK and the side face the piece
    came from are changed. A half turn keeps a piece in the middle row of an odd cube inside the
    block, so that piece needs a quarter turn of BACK; the middle row itself is reached from DOWN
    with a `deep_move`.

    Example, on a 6x6 and on a 5x5:

        >>> extraction(6, Layer.LEFT, 1, Direction.DOUBLE)
        "Uw B2 Uw'"
        >>> extraction(6, Layer.RIGHT, 3, Direction.DOUBLE)
        "3Dw B2 3Dw'"
        >>> extraction(5, Layer.LEFT, 2, Direction.CW)
        "y Uw' B Uw y'"

    :param size: The size of the cube
    :param side: The face the piece is on, LEFT or RIGHT
    :param row: The row the piece is in
    :param over: The direction BACK is turned
    :return: The conjugate, in standard notation
    """

    top = in_first_half(size, row)
    pole = Layer.UP if top else Layer.DOWN
    depth = row + 1 if top else size - row
    direction = Direction.CW if (side is Layer.LEFT) == top else Direction.CCW

    there = deep_move(size, pole, direction, depth)

    return f"{there} {Move(Layer.BACK, over, 1)} {inverse_of(there)}"


def across_routes(cube: Cube, color: Color, cell: tuple[int, int], piece: CenterSearchResult) -> list[str]:
    """
    Returns the routes that bring a piece on LEFT or RIGHT into the bar.

    The piece is moved onto BACK with `extraction`, with a half turn of BACK first and then the
    quarter turns, and brought in from there with `direct_route`, bare and restoring, one pair of
    routes for each piece of the colour on BACK. Where the piece lands on BACK is read off the cube
    rather than worked out.

    Example, on a 4x4 turned with `z' Dw`, filling FRONT (2, 1) from RIGHT (1, 1). The first two
    routes are the bare and restoring ones from the first piece on BACK after `Uw' B2 Uw`:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("z' Dw"))
        >>> routes = across_routes(cube, Color.YELLOW, (2, 1), CenterSearchResult(Layer.RIGHT, 1, 1))
        >>> len(routes), routes[:2]
        (12, ["Uw' B2 Uw B2 Lw2 L2", "Uw' B2 Uw B2 Lw2 L2 F' L2 Lw2 F"])

    :param cube: The cube
    :param color: The colour being built
    :param cell: The FRONT cell being filled
    :param piece: The piece, on LEFT or RIGHT
    :return: The candidate routes, in standard notation
    """

    routes = []

    for over in (Direction.DOUBLE, Direction.CW, Direction.CCW):
        moved = extraction(cube.size, piece.layer, piece.row, over)
        parked = trial(cube, moved)
        routes += [
            f"{moved} {direct_route(cube.size, cell, back, restore)}"
            for back in search_center(parked, color, *cell)
            if back.layer is Layer.BACK
            for restore in (False, True)
        ]

    return routes


def lift(size: int, col: int, over: Direction) -> str:
    """
    Returns the conjugate that moves a piece from DOWN onto UP.

    The block reaching in from the nearer of LEFT and RIGHT is turned twice, UP is turned and the
    block is turned twice again. The block turns cancel on every face except UP and DOWN. A half turn
    of UP keeps a piece in the middle column of an odd cube inside the block, so that piece needs a
    quarter turn; the middle column itself is reached from RIGHT with a `deep_move`.

    Example, on a 6x6 and on a 5x5:

        >>> lift(6, 1, Direction.DOUBLE)
        'Lw2 U2 Lw2'
        >>> lift(6, 3, Direction.DOUBLE)
        '3Rw2 U2 3Rw2'
        >>> lift(5, 2, Direction.CW)
        'x2 Lw2 U x2 Lw2'

    :param size: The size of the cube
    :param col: The column of DOWN the piece is in
    :param over: The direction UP is turned
    :return: The conjugate, in standard notation
    """

    if in_first_half(size, col):
        block = deep_move(size, Layer.LEFT, Direction.DOUBLE, col + 1)
    else:
        block = deep_move(size, Layer.RIGHT, Direction.DOUBLE, size - col)

    return f"{block} {Move(Layer.UP, over, 1)} {block}"


def target_routes(cube: Cube, color: Color, cell: tuple[int, int], piece: CenterSearchResult) -> list[str]:
    """
    Returns the routes that bring a piece on DOWN into the bar while the center is built on DOWN.

    A column slice fetching from DOWN would take a column of the center being built, so the piece is
    first moved onto UP with `lift`, with a half turn of UP first and then the quarter turns, and
    brought in from there with `direct_route`, bare and restoring. Where it lands on UP is read off
    the cube rather than worked out.

    :param cube: The cube
    :param color: The colour being built
    :param cell: The FRONT cell being filled
    :param piece: The piece, on DOWN
    :return: The candidate routes, in standard notation
    """

    routes = []

    for over in (Direction.DOUBLE, Direction.CW, Direction.CCW):
        moved = lift(cube.size, piece.col, over)
        lifted = trial(cube, moved)
        routes += [
            f"{moved} {direct_route(cube.size, cell, up, restore)}"
            for up in search_center(lifted, color, *cell)
            if up.layer is Layer.UP
            for restore in (False, True)
        ]

    return routes


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


def face_turns(face: Layer) -> list[Move | None]:
    """
    Returns the ways a face can be turned before a wide move: not at all, or by one of the three
    turns.

    Example:

        >>> [str(turn) for turn in face_turns(Layer.RIGHT)]
        ['None', 'R', "R'", 'R2']

    :param face: The face
    :return: None for no turn, then the three turns of the face
    """

    return [None] + [Move(face, direction, 1) for direction in Direction]


def wide_depth(size: int, cell: tuple[int, int]) -> int:
    """
    Returns the depth of the block that reaches a cell of the middle line from the nearer side, and
    no deeper.

    The block never reaches the middle of the face, so it leaves the fixed center and the far half of
    the line alone, and an inner cell's block leaves the outer cells beyond it free.

    Example, on a 7x7, the inner cells of a horizontal and a vertical line, then an outer one:

        >>> [wide_depth(7, cell) for cell in [(3, 2), (3, 4), (4, 3), (3, 1)]]
        [3, 3, 3, 2]

    :param size: The size of the cube, odd
    :param cell: The cell of the middle line
    :return: The depth of the block
    """

    middle = size // 2

    return middle + 1 - abs(cell[0] - middle) - abs(cell[1] - middle)


def wide_moves(size: int, cell: tuple[int, int], target: Layer, source: Layer | None) -> list[str]:
    """
    Returns the wide moves that can carry a piece into a cell of the target's middle line.

    Only the faces off the target's axis carry anything onto the target, and a piece on another face
    is carried only by the faces off that face's axis too. Every block is as deep as `wide_depth`.

    Example, on a 5x5, filling RIGHT (2, 1) from FRONT, and from RIGHT itself:

        >>> wide_moves(5, (2, 1), Layer.RIGHT, Layer.FRONT)
        ['Uw', "Uw'", 'Uw2', 'Dw', "Dw'", 'Dw2']
        >>> len(wide_moves(5, (2, 1), Layer.RIGHT, None))
        12

    :param size: The size of the cube, odd
    :param cell: The cell of the middle line
    :param target: The face the center is built on
    :param source: The face the piece is on, or None for a piece on the target
    :return: The wide moves, in standard notation
    """

    axes = {target, target.opposite()}

    if source is not None:
        axes |= {source, source.opposite()}

    depth = wide_depth(size, cell)

    return [str(Move(face, direction, depth)) for face in Layer if face not in axes for direction in Direction]


def line_routes(size: int, cell: tuple[int, int], piece: CenterSearchResult, target: Layer) -> list[str]:
    """
    Returns the routes that bring a piece on another face into a cell of the target's middle line.

    Every route turns the target to stand the cell in the block, turns the source face to stand the
    piece in the block too, and makes the wide move. A bare route then turns the target back. A
    restoring route first turns the target to lift the line out of the block and undoes the wide
    move, so that every face the block carried returns, and then turns the target back to the line's
    orientation. The source face is never turned back: it holds nothing built yet.

    The bare routes come first, since they are shorter. Which one fills the cell without breaking
    anything is left to the cube.

    Example, on a 5x5, filling RIGHT (2, 1) from FRONT (1, 2):

        >>> routes = line_routes(5, (2, 1), CenterSearchResult(Layer.FRONT, 1, 2), Layer.RIGHT)
        >>> len(routes), routes[0], routes[-1]
        (384, 'Uw', 'R2 F2 Dw2 R2 Dw2')

    :param size: The size of the cube, odd
    :param cell: The cell of the middle line
    :param piece: The piece, on a face other than the target
    :param target: The face the center is built on
    :return: The candidate routes, in standard notation
    """

    wides = wide_moves(size, cell, target, piece.layer)
    bare, restoring = [], []

    for stand in face_turns(target):
        for collect in face_turns(piece.layer):
            for wide in wides:
                opening = [str(turn) for turn in (stand, collect) if turn] + [wide]
                bare.append(" ".join(opening + ([str(stand.inverse())] if stand else [])))

                for lift_turn in Direction:
                    raised = Move(target, lift_turn, 1)
                    settled = combine(stand, raised) if stand else raised
                    back = [str(settled.inverse())] if settled else []
                    restoring.append(" ".join(opening + [str(raised), inverse_of(wide)] + back))

    return bare + restoring


def line_target_routes(size: int, cell: tuple[int, int], target: Layer) -> list[str]:
    """
    Returns the routes that move a piece already on the target into a cell of its middle line.

    The target is turned to stand the piece on the cell, the wide move carries it off, the target is
    turned back, and the wide move is undone, bringing the piece back onto the cell. The piece must
    be of the cell's position type, since only a turn of the target moves it.

    Example, on a 5x5, filling RIGHT (2, 1):

        >>> line_target_routes(5, (2, 1), Layer.RIGHT)[:3]
        ["R Uw R' Uw'", "R Uw' R' Uw", "R Uw2 R' Uw2"]

    :param size: The size of the cube, odd
    :param cell: The cell of the middle line
    :param target: The face the center is built on
    :return: The candidate routes, in standard notation
    """

    return [
        f"{stand} {wide} {stand.inverse()} {inverse_of(wide)}"
        for stand in face_turns(target)[1:]
        for wide in wide_moves(size, cell, target, None)
    ]


def line_lift_routes(size: int, cell: tuple[int, int], piece: CenterSearchResult) -> list[str]:
    """
    Returns the routes that bring a piece on UP into a cell of FRONT's middle row.

    UP is turned to stand the piece above the cell, the column slice through the cell carries it
    down, FRONT is turned to lift the middle row out of the slice's column, the slice goes back and
    FRONT is turned back. Only FRONT and UP change, and the cells of the middle row filled before
    stay put. FRONT is turned both ways, and which one fills the cell is left to the cube.

    Example, on a 5x5, filling FRONT (2, 1) from UP (1, 2):

        >>> line_lift_routes(5, (2, 1), CenterSearchResult(Layer.UP, 1, 2))
        ["U' Lw L' F L Lw' F'", "U' Lw L' F' L Lw' F"]

    :param size: The size of the cube, odd
    :param cell: The cell of FRONT's middle row
    :param piece: The piece, on UP
    :return: The candidate routes, in standard notation
    """

    down = column_slice(size, cell[1], Direction.CCW)
    align = align_turn(size, cell, piece)
    routes = []

    for over in (Direction.CW, Direction.CCW):
        turn = Move(Layer.FRONT, over, 1)
        parts = [align, down, str(turn), inverse_of(down), str(turn.inverse())]
        routes.append(" ".join(part for part in parts if part))

    return routes


def staging_middle_routes(size: int, cell: tuple[int, int], piece: CenterSearchResult) -> list[str]:
    """
    Returns the route that brings a piece into the middle cell of a bar staged on UP.

    A piece on UP only needs UP turned. A piece on FRONT is raised by the block reaching in from the
    nearer of LEFT and RIGHT as far as the piece's column: the block carries it up, a quarter turn of
    UP takes it out of the block onto the middle cell, and the block goes back. The block ends before
    FRONT's middle column, so the middle line stays put.

    Example, on a 5x5, filling UP (3, 2) from UP (1, 2), from FRONT (2, 1) and from FRONT (2, 3):

        >>> staging_middle_routes(5, (3, 2), CenterSearchResult(Layer.UP, 1, 2))
        ['U2']
        >>> staging_middle_routes(5, (3, 2), CenterSearchResult(Layer.FRONT, 2, 1))
        ["Lw' U' Lw"]
        >>> staging_middle_routes(5, (3, 2), CenterSearchResult(Layer.FRONT, 2, 3))
        ["Rw U Rw'"]

    :param size: The size of the cube, odd
    :param cell: The middle cell of the staging row on UP
    :param piece: The piece, on UP or FRONT
    :return: The candidate routes, in standard notation
    """

    if piece.layer is Layer.UP:
        return [align_turn(size, cell, piece)]

    if in_first_half(size, piece.col):
        block, over = deep_move(size, Layer.LEFT, Direction.CCW, piece.col + 1), Direction.CCW
    else:
        block, over = deep_move(size, Layer.RIGHT, Direction.CW, size - piece.col), Direction.CW

    return [f"{block} {Move(Layer.UP, over, 1)} {inverse_of(block)}"]


def commutator_routes(size: int, cell: tuple[int, int]) -> list[str]:
    """
    Returns the commutators that can bring a piece into a cell of a bar staged on UP.

    Each is built from a single-layer column slice turning FRONT up into UP and a turn of UP,
    `[slice, turn]` or `[turn, slice]`, and each is then also listed conjugated by a turn of UP. The
    slice goes back, so DOWN and BACK are restored and only FRONT and UP change. The slices are those
    whose column holds a cell of the target's position type on UP; the middle column of an odd cube
    is left out, since it carries the fixed centers. The plain commutators come first, since they
    are shorter. Which one fills the cell without breaking anything is left to the cube.

    Example, on a 7x7, for UP (4, 2), whose position type lies in columns 2 and 4:

        >>> routes = commutator_routes(7, (4, 2))
        >>> len(routes), routes[0], routes[-1]
        (48, "3Lw' Lw U Lw' 3Lw U'", "U2 U2 3Rw Rw' U2 Rw 3Rw' U2")

    :param size: The size of the cube
    :param cell: The cell of the staging row on UP
    :return: The candidate routes, in standard notation
    """

    columns = sorted({index for orbit_cell in orbit_cells(size, cell) for index in orbit_cell})
    middle = size // 2 if size % 2 else None
    turns = [str(Move(Layer.UP, direction, 1)) for direction in Direction]
    plain = []

    for col in columns:
        if col == middle:
            continue

        cut = column_slice(size, col, Direction.CW)
        for turn in turns:
            plain.append(f"{cut} {turn} {inverse_of(cut)} {inverse_of(turn)}")
            plain.append(f"{turn} {cut} {inverse_of(turn)} {inverse_of(cut)}")

    return plain + [f"{turn} {route} {inverse_of(turn)}" for turn in turns for route in plain]


def front_insertion(size: int, col: int) -> str:
    """
    Returns the algorithm that moves the bar staged on UP into a column of FRONT's left half.

    The bar is staged in row `size - 1 - col` of UP, so a turn of UP stands it in column `col`. The
    block reaching in from LEFT as far as the column carries it onto FRONT, a half turn of FRONT parks
    it in the mirror column, out of the block, the block goes back and FRONT is turned back. LEFT,
    DOWN and BACK are restored, and FRONT's columns beyond the block, with the middle line and the bars
    already inserted, come back where they were.

    Example, on a 7x7:

        >>> front_insertion(7, 2)
        "U 3Lw F2 3Lw' F2"

    :param size: The size of the cube
    :param col: The column of FRONT the bar goes to, in its left half
    :return: The algorithm, in standard notation
    """

    block = deep_move(size, Layer.LEFT, Direction.CW, col + 1)

    return f"U {block} F2 {inverse_of(block)} F2"


def cycle_routes(size: int, cell: tuple[int, int], piece: CenterSearchResult) -> list[str]:
    """
    Returns the commutators that bring a piece on UP into a cell of FRONT, changing no other cell of
    FRONT.

    UP is turned to stand the piece above the cell. The commutator is `[slice, F slice' F']` on the
    single-layer column slices through the cell's column and through the column a quarter turn of
    FRONT moves the cell to: the first slice brings the piece down, the quarter turn moves it to the
    second column, the second slice takes it off FRONT, and undoing all of it in order brings it back
    into the cell. Only the cell and two cells of UP change. A quarter turn that leaves the cell in
    its own column cannot be used, so it is skipped.

    Example, on a 7x7, filling FRONT (2, 4) from UP (2, 4). `F` would keep the cell in column 4, so
    only `F'` is used:

        >>> cycle_routes(7, (2, 4), CenterSearchResult(Layer.UP, 2, 4))
        ["3Rw' Rw F' 3Lw Lw' F Rw' 3Rw F' Lw 3Lw' F"]

    :param size: The size of the cube
    :param cell: The cell of FRONT
    :param piece: The piece, on UP
    :return: The candidate routes, in standard notation
    """

    row, col = cell
    align = align_turn(size, cell, piece)
    first = column_slice(size, col, Direction.CCW)
    routes = []

    for over, moved in ((Direction.CW, size - 1 - row), (Direction.CCW, row)):
        if moved == col:
            continue

        turn, back = Move(Layer.FRONT, over, 1), Move(Layer.FRONT, over.inverse(), 1)
        second = column_slice(size, moved, Direction.CCW)
        parts = [
            align,
            first,
            str(turn),
            second,
            str(back),
            inverse_of(first),
            str(turn),
            inverse_of(second),
            str(back),
        ]
        routes.append(" ".join(part for part in parts if part))

    return routes
