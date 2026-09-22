# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation
from rubik_cube_solver.solve.cube_nxn.centers import first_route
from rubik_cube_solver.solve.cube_nxn.pieces import Sticker, in_first_half
from rubik_cube_solver.solve.cube_nxn.routes import quarter_direction, trial

# The whole-cube rotation from the grip the centers end in, white on LEFT, to white on UP and yellow on
# DOWN. The edges are paired in this grip, with the free slice turning about the UP/DOWN axis.
EDGES_REGRIP: str = "z"

# The edge slots between the side faces, in the order a clockwise turn of UP carries them. A clockwise
# turn of DOWN carries them the other way round.
EDGES_MIDDLE_CYCLE: tuple[EdgeSlot, ...] = (EdgeSlot.FR, EdgeSlot.FL, EdgeSlot.BL, EdgeSlot.BR)

# The edge slots of UP and of DOWN, each in the order a clockwise turn of its own face carries them.
EDGES_UP_CYCLE: tuple[EdgeSlot, ...] = (EdgeSlot.UF, EdgeSlot.UL, EdgeSlot.UB, EdgeSlot.UR)
EDGES_DOWN_CYCLE: tuple[EdgeSlot, ...] = (EdgeSlot.DF, EdgeSlot.DR, EdgeSlot.DB, EdgeSlot.DL)

# The side faces in the order a clockwise turn of UP carries their rows.
EDGES_SIDE_FACES: tuple[Layer, ...] = (Layer.FRONT, Layer.LEFT, Layer.BACK, Layer.RIGHT)

# Flips the edge in FR in place, so the wing in each row trades places with the wing in the mirrored
# row. Of the other edges, only UP's are moved.
EDGES_FLIP: str = "R U R' F R' F' R"

# Bring an edge of UP into FR: from UF keeping the sticker on UP facing FRONT, from UR turning it over.
EDGES_UP_ENTRIES: tuple[tuple[EdgeSlot, str], ...] = ((EdgeSlot.UF, "R U' R'"), (EdgeSlot.UR, "F' U F"))

# Bring an edge of DOWN into FR: from DF keeping the sticker on DOWN facing FRONT, from DR turning it
# over.
EDGES_DOWN_ENTRIES: tuple[tuple[EdgeSlot, str], ...] = ((EdgeSlot.DF, "R' D R"), (EdgeSlot.DR, "F D' F'"))

# Store the finished edge in FL on UP or DOWN, bringing the edge in UF or DF into FL in its place.
EDGES_UP_STORE: str = "L' U L"
EDGES_DOWN_STORE: str = "L D' L'"


def wing_cells(size: int, slot: EdgeSlot, index: int) -> tuple[tuple[Layer, int, int], tuple[Layer, int, int]]:
    """
    Returns the two cells of a wing of an edge slot, each as (face, row, column).

    The first cell is on the face named first in the slot. The wings of the slots between the side faces
    are indexed by their row, so a wing keeps its index when UP or DOWN turns it into another slot.

    Example, on a 5x5:

        >>> wing_cells(5, EdgeSlot.FL, 1)
        ((<Layer.FRONT: 'F'>, 1, 0), (<Layer.LEFT: 'L'>, 1, 4))
        >>> wing_cells(5, EdgeSlot.UB, 1)
        ((<Layer.UP: 'U'>, 0, 3), (<Layer.BACK: 'B'>, 0, 1))

    :param size: The size of the cube
    :param slot: The edge slot
    :param index: The wing, from 1 to `size - 2`
    :return: The cell on each of the slot's two faces
    """

    last = size - 1

    match slot:
        case EdgeSlot.UF:
            return (Layer.UP, last, index), (Layer.FRONT, 0, index)
        case EdgeSlot.UB:
            return (Layer.UP, 0, last - index), (Layer.BACK, 0, index)
        case EdgeSlot.UL:
            return (Layer.UP, index, 0), (Layer.LEFT, 0, index)
        case EdgeSlot.UR:
            return (Layer.UP, last - index, last), (Layer.RIGHT, 0, index)
        case EdgeSlot.DF:
            return (Layer.DOWN, 0, index), (Layer.FRONT, last, index)
        case EdgeSlot.DB:
            return (Layer.DOWN, last, last - index), (Layer.BACK, last, index)
        case EdgeSlot.DL:
            return (Layer.DOWN, last - index, 0), (Layer.LEFT, last, index)
        case EdgeSlot.DR:
            return (Layer.DOWN, index, last), (Layer.RIGHT, last, index)
        case EdgeSlot.FL:
            return (Layer.FRONT, index, 0), (Layer.LEFT, index, last)
        case EdgeSlot.FR:
            return (Layer.FRONT, index, last), (Layer.RIGHT, index, 0)
        case EdgeSlot.BL:
            return (Layer.BACK, index, last), (Layer.LEFT, index, 0)
        case _:
            return (Layer.BACK, index, 0), (Layer.RIGHT, index, last)


def wing_colors(cube: Cube, slot: EdgeSlot, index: int) -> tuple[Color, Color]:
    """
    Returns the colours of a wing of an edge slot, in the order of `wing_cells`.

    Example, on a solved 4x4:

        >>> wing_colors(Cube(4), EdgeSlot.FL, 1)
        (<Color.GREEN: 'G'>, <Color.ORANGE: 'O'>)

    :param cube: The cube
    :param slot: The edge slot
    :param index: The wing, from 1 to `cube.size - 2`
    :return: The colour of each of the wing's two stickers
    """

    first, second = (
        cube.layers[layer][row * cube.size + col] for layer, row, col in wing_cells(cube.size, slot, index)
    )

    return first, second


def pivot_row(size: int) -> int:
    """
    Returns the row of the wing every edge is built around: the middle row of an odd cube, and the
    upper of the two middle rows of an even one.

    Example:

        >>> pivot_row(5), pivot_row(6)
        (2, 2)

    :param size: The size of the cube
    :return: The pivot's row
    """

    return (size - 1) // 2


def edge_rows(size: int) -> list[int]:
    """
    Returns the rows of an edge after the pivot, in the order they are filled: from the middle out,
    the upper row of each pair before the lower one.

    On an even cube the pivot is the upper middle row, so the lower middle row comes first.

    Example:

        >>> edge_rows(7)
        [2, 4, 1, 5]
        >>> edge_rows(6)
        [3, 1, 4]

    :param size: The size of the cube
    :return: The rows, in fill order
    """

    pivot = pivot_row(size)

    return sorted((row for row in range(1, size - 1) if row != pivot), key=lambda row: (abs(2 * row - size + 1), row))


def is_paired(cube: Cube, slot: EdgeSlot) -> bool:
    """
    Returns whether every wing of an edge slot shows the same two colours on the same two faces.

    Example, on a 4x4 turned with `Uw`, which splits the edges between the side faces:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("Uw"))
        >>> is_paired(cube, EdgeSlot.UF), is_paired(cube, EdgeSlot.FL)
        (True, False)

    :param cube: The cube
    :param slot: The edge slot
    :return: Whether the edge in the slot is paired
    """

    return len({wing_colors(cube, slot, index) for index in range(1, cube.size - 1)}) == 1


def find_wings(cube: Cube, colors: set[Color], row: int) -> list[tuple[EdgeSlot, int]]:
    """
    Returns every wing of two colours in the row or its mirror, as (slot, index), in `EdgeSlot` order.

    A row and its mirror hold the same kind of wing, so the two wings of a colour pair that can fill a
    row are both found. Only one of them fits the row the right way round.

    Example, on a 4x4 turned with `Uw`, looking for the green and orange wings of the lower row:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("Uw"))
        >>> find_wings(cube, {Color.GREEN, Color.ORANGE}, 2)
        [(<EdgeSlot.FL: 'FL'>, 2), (<EdgeSlot.BL: 'BL'>, 1)]

    :param cube: The cube
    :param colors: The two colours of the wing
    :param row: The row of the edge being filled
    :return: The slot and index of each wing found
    """

    indices = {row, cube.size - 1 - row}

    return [
        (slot, index) for slot in EdgeSlot for index in sorted(indices) if set(wing_colors(cube, slot, index)) == colors
    ]


def block_turn(size: int, row: int, direction: Direction) -> str:
    """
    Returns the wide turn that reaches a row of the side faces from the nearer of UP and DOWN.

    The block ends at the row, so it never reaches the rows nearer the middle of the cube.

    Example, on a 6x6:

        >>> block_turn(6, 1, Direction.CW), block_turn(6, 3, Direction.CCW)
        ('Uw', "3Dw'")

    :param size: The size of the cube
    :param row: The row of the side faces, from 1 to `size - 2`
    :param direction: The direction of the turn, as seen from the face it is reached from
    :return: The turn, in standard notation
    """

    if in_first_half(size, row):
        return str(Move(Layer.UP, direction, row + 1))

    return str(Move(Layer.DOWN, direction, size - row))


def cycle_quarters(cycle: tuple[EdgeSlot, ...], start: EdgeSlot, end: EdgeSlot) -> int:
    """
    Returns how many clockwise quarter turns carry a slot to another along a cycle of slots.

    Example:

        >>> cycle_quarters(EDGES_MIDDLE_CYCLE, EdgeSlot.BR, EdgeSlot.FL)
        2

    :param cycle: The slots, in the order a clockwise turn carries them
    :param start: The slot turned from
    :param end: The slot turned to
    :return: The number of clockwise quarter turns, from 0 to 3
    """

    return (cycle.index(end) - cycle.index(start)) % 4


def slice_turn(size: int, row: int, start: EdgeSlot, end: EdgeSlot) -> str:
    """
    Returns the wide turn that carries a row of one slot between the side faces into another.

    Example, on a 5x5. The upper row is reached from UP, the lower one from DOWN, which turns the slots
    the other way:

        >>> slice_turn(5, 1, EdgeSlot.FR, EdgeSlot.FL), slice_turn(5, 3, EdgeSlot.FR, EdgeSlot.FL)
        ('Uw', "Dw'")

    :param size: The size of the cube
    :param row: The row, from 1 to `size - 2`, outside the middle of an odd cube
    :param start: The slot the row is carried from
    :param end: The slot the row is carried to, other than `start`
    :return: The turn, in standard notation
    """

    quarters = cycle_quarters(EDGES_MIDDLE_CYCLE, start, end)

    if not in_first_half(size, row):
        quarters = -quarters

    return block_turn(size, row, quarter_direction(quarters))


def face_turn(face: Layer, cycle: tuple[EdgeSlot, ...], start: EdgeSlot, end: EdgeSlot) -> str:
    """
    Returns the turn of a face that carries one of its edge slots to another, or nothing if they are
    the same slot.

    Example:

        >>> face_turn(Layer.UP, EDGES_UP_CYCLE, EdgeSlot.UB, EdgeSlot.UF)
        'U2'
        >>> face_turn(Layer.UP, EDGES_UP_CYCLE, EdgeSlot.UF, EdgeSlot.UF)
        ''

    :param face: The face turned
    :param cycle: The face's edge slots, in the order a clockwise turn carries them
    :param start: The slot the edge is in
    :param end: The slot the edge is carried to
    :return: The turn, in standard notation, or an empty string
    """

    quarters = cycle_quarters(cycle, start, end)

    return str(Move(face, quarter_direction(quarters), 1)) if quarters else ""


def flip(slot: EdgeSlot) -> str:
    """
    Returns the algorithm that flips the edge in a slot between the side faces in place.

    The cube is turned so the slot is in FR, `EDGES_FLIP` is applied, and the cube is turned back. Only
    UP's edges are moved besides it, so FL is left intact from any other slot.

    Example:

        >>> flip(EdgeSlot.FR), flip(EdgeSlot.BR)
        ("R U R' F R' F' R", "y R U R' F R' F' R y'")

    :param slot: The slot between the side faces
    :return: The algorithm, in standard notation
    """

    quarters = cycle_quarters(EDGES_MIDDLE_CYCLE, slot, EdgeSlot.FR)

    if not quarters:
        return EDGES_FLIP

    rotation = Move(Rotation.Y, quarter_direction(quarters), 1)

    return f"{rotation} {EDGES_FLIP} {rotation.inverse()}"


def wing_routes(size: int, row: int, slot: EdgeSlot, index: int) -> list[str]:
    """
    Returns the routes that bring a wing into FL's row, one per way it may be turned.

    - On FL, in the mirrored row: the mirrored row is turned into FR, flipped, and turned back.
    - On FR, BR or BL, in the row: the row is turned straight into FL. In the mirrored row, the edge is
      flipped in place first.
    - On UP or DOWN: the edge is turned to the front, or to the right, and brought into FR from there,
      and its row turned into FL. Which of the two keeps the wing the right way round depends on the
      wing, so both are returned.

    A wing already in FL's row gives no route.

    Example, on a 5x5, for the upper row:

        >>> wing_routes(5, 1, EdgeSlot.FL, 3)
        ["Dw R U R' F R' F' R Uw"]
        >>> wing_routes(5, 1, EdgeSlot.BL, 3)
        ["y2 R U R' F R' F' R y2 Uw'"]
        >>> wing_routes(5, 1, EdgeSlot.UB, 1)
        ["U2 R U' R' Uw", "U F' U F Uw"]

    :param size: The size of the cube
    :param row: The row of FL being filled
    :param slot: The slot the wing is in
    :param index: The wing's index in the slot
    :return: The routes, in standard notation
    """

    insert = slice_turn(size, row, EdgeSlot.FR, EdgeSlot.FL)

    if slot in EDGES_UP_CYCLE:
        entries = [(face_turn(Layer.UP, EDGES_UP_CYCLE, slot, end), entry) for end, entry in EDGES_UP_ENTRIES]
    elif slot in EDGES_DOWN_CYCLE:
        entries = [(face_turn(Layer.DOWN, EDGES_DOWN_CYCLE, slot, end), entry) for end, entry in EDGES_DOWN_ENTRIES]
    elif slot is EdgeSlot.FL:
        if index == row:
            return []
        mirror = size - 1 - row
        return [f"{slice_turn(size, mirror, EdgeSlot.FL, EdgeSlot.FR)} {EDGES_FLIP} {insert}"]
    elif index == row:
        return [slice_turn(size, row, slot, EdgeSlot.FL)]
    else:
        return [f"{flip(slot)} {slice_turn(size, row, slot, EdgeSlot.FL)}"]

    return [" ".join(part for part in (turn, entry, insert) if part) for turn, entry in entries]


def front_left_stickers(size: int, row: int, front: Color, left: Color) -> tuple[Sticker, Sticker]:
    """
    Returns the two stickers of a wing of FL, with the colours they have to hold.

    Example, on a 4x4:

        >>> front, left = front_left_stickers(4, 2, Color.GREEN, Color.ORANGE)
        >>> front
        Sticker(layer=<Layer.FRONT: 'F'>, row=2, col=0, color=<Color.GREEN: 'G'>)
        >>> left
        Sticker(layer=<Layer.LEFT: 'L'>, row=2, col=3, color=<Color.ORANGE: 'O'>)

    :param size: The size of the cube
    :param row: The wing's row
    :param front: The colour of the sticker on FRONT
    :param left: The colour of the sticker on LEFT
    :return: The sticker on FRONT and the sticker on LEFT
    """

    (front_layer, front_row, front_col), (left_layer, left_row, left_col) = wing_cells(size, EdgeSlot.FL, row)

    return Sticker(front_layer, front_row, front_col, front), Sticker(left_layer, left_row, left_col, left)


def build_edge(cube: Cube, routes: Callable[[int, int, EdgeSlot, int], list[str]]) -> tuple[list[str], Cube]:
    """
    Pairs every wing of the edge in FL with its pivot, one row at a time in `edge_rows` order.

    For each row, both wings of the pivot's colours that could fill it are found, and the first of the
    routes given for them that fills it the pivot's way round while keeping the pivot and the rows
    before it is taken. Each route is tried on a copy of the cube.

    Example, on a 4x4 turned with `Uw`. The pivot is the wing `Uw` carried into FL from FR, so the lower
    wing of FR is brought after it:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("Uw"))
        >>> build_edge(cube, wing_routes)[0]
        ["Dw'"]

    :param cube: The cube
    :param routes: Returns the routes that bring a wing into FL's row, as `wing_routes` does, from the
        size of the cube, the row, and the slot and index of the wing
    :return: The routes used and the cube with the edge in FL paired
    """

    size = cube.size
    pivot = pivot_row(size)
    front, left = wing_colors(cube, EdgeSlot.FL, pivot)
    built = [pivot]
    moves: list[str] = []

    for row in edge_rows(size):
        if wing_colors(cube, EdgeSlot.FL, row) != (front, left):
            goal, second = front_left_stickers(size, row, front, left)
            keep = [second] + [sticker for done in built for sticker in front_left_stickers(size, done, front, left)]
            fetched = None

            for slot, index in find_wings(cube, {front, left}, row):
                if fetched := first_route(cube, routes(size, row, slot, index), goal, keep):
                    break

            if fetched is None:
                raise ValueError(f"No route fills row {row} of the {front.name}-{left.name} edge")

            route, cube = fetched
            moves.append(route)

        built.append(row)

    return moves, cube


def open_slot(cube: Cube) -> EdgeSlot | None:
    """
    Returns the first slot of UP, or failing that of DOWN, whose edge is not paired.

    Example, on a 4x4 turned with `Uw`, which pairs every edge of UP and DOWN:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("Uw"))
        >>> open_slot(cube) is None
        True
        >>> Rotator(cube).apply(Algorithm.from_str("L' U L"))
        >>> open_slot(cube)
        <EdgeSlot.UB: 'UB'>

    :param cube: The cube
    :return: The slot, or None if every edge of UP and DOWN is paired
    """

    return next((slot for slot in EDGES_UP_CYCLE + EDGES_DOWN_CYCLE if not is_paired(cube, slot)), None)


def store_route(slot: EdgeSlot) -> str:
    """
    Returns the algorithm that stores the edge in FL on UP or DOWN, in place of the edge in a slot of
    that face, which comes into FL.

    Example:

        >>> store_route(EdgeSlot.UB), store_route(EdgeSlot.DF)
        ("U2 L' U L", "L D' L'")

    :param slot: A slot of UP or DOWN
    :return: The algorithm, in standard notation
    """

    if slot in EDGES_UP_CYCLE:
        turn, store = face_turn(Layer.UP, EDGES_UP_CYCLE, slot, EdgeSlot.UF), EDGES_UP_STORE
    else:
        turn, store = face_turn(Layer.DOWN, EDGES_DOWN_CYCLE, slot, EdgeSlot.DF), EDGES_DOWN_STORE

    return f"{turn} {store}".strip()


def lined_up(cube: Cube, row: int) -> bool:
    """
    Returns whether a row of the side faces' centers shows, on every side face, the colour of the
    pivot's row.

    Example, on a 4x4 turned with `Dw`, which turns the lower middle row but not the pivot's:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("Dw"))
        >>> lined_up(cube, 1), lined_up(cube, 2)
        (True, False)

    :param cube: The cube
    :param row: The row of the side faces, from 1 to `cube.size - 2`
    :return: Whether the row matches the pivot's row on every side face
    """

    size = cube.size
    pivot = pivot_row(size)

    return all(cube.layers[face][row * size + 1] is cube.layers[face][pivot * size + 1] for face in EDGES_SIDE_FACES)


def fix_free_slice(cube: Cube) -> list[str]:
    """
    Returns the wide turns that line the center rows of the side faces back up with the pivot's row,
    in `edge_rows` order.

    Pairing the edges turns every row of the side faces but the pivot's about the UP/DOWN axis. Each
    row is turned back with a block that ends at it, so the rows fixed before it, nearer the middle,
    are not moved again.

    Example, on a 4x4 turned with `Dw`, which turns the lower middle row out of line:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("Dw"))
        >>> fix_free_slice(cube)
        ["Dw'"]

    :param cube: The cube, with the side faces' centers solved row by row
    :return: The turns, in the order they are applied
    """

    moves: list[str] = []

    for row in edge_rows(cube.size):
        if lined_up(cube, row):
            continue

        turns = [block_turn(cube.size, row, direction) for direction in Direction]
        turn = next(turn for turn in turns if lined_up(trial(cube, turn), row))
        moves.append(turn)
        cube = trial(cube, turn)

    return moves


def build_first_eight_edges(cube: Cube) -> list[str]:
    """
    Returns the algorithms that pair eight edges of a big cube whose centers are built, and store them
    on UP and DOWN.

    The cube is turned with `EDGES_REGRIP` to hold white on UP and yellow on DOWN. The edge in FL is
    paired with `build_edge`, then stored with `store_route` in the first slot `open_slot` finds, which
    brings the next edge into FL. When every edge of UP and DOWN is paired, the rows of the side faces'
    centers that the pairing turned are put back with `fix_free_slice`.

    Example, on a 4x4 turned with `Uw L' U L Uw'`, which leaves a split edge on UP, and held in the
    grip the centers end in with `z'`. The split edge is paired in FL and stored, and the last route
    lines the side faces' centers back up:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("Uw L' U L Uw' z'"))
        >>> build_first_eight_edges(cube)
        ['z', "U2 F' U F Dw'", "U' L' U L", 'Dw']

    :param cube: The cube, of size 4 or more, with its centers built
    :return: The algorithms, in the order they are applied
    """

    moves = [EDGES_REGRIP]
    cube = trial(cube, EDGES_REGRIP)

    while open_slot(cube) is not None:
        edge_moves, cube = build_edge(cube, wing_routes)
        moves += edge_moves

        if (slot := open_slot(cube)) is not None:
            store = store_route(slot)
            moves.append(store)
            cube = trial(cube, store)

    return moves + fix_free_slice(cube)
