# Python imports
from functools import partial

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.move_cancellation import combine
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.cube_nxn.edges import (
    EDGES_DOWN_STORE,
    EDGES_FLIP,
    EDGES_UP_STORE,
    build_edge,
    flip,
    slice_turn,
)
from rubik_cube_solver.solve.cube_nxn.routes import inverse_of, trial

# Brings the edges of BL and BR into UF and DF, so the four edges left to pair are in FL, FR, UF and DF,
# and BL and BR hold paired edges.
LAST_EDGES_SETUP: str = "B' U2 D2"

# Flips the edge in FR in place and turns UP back, so every other edge is left in its slot.
LAST_EDGES_FLIP: str = f"{EDGES_FLIP} U'"

# Bring the edge of UF or DF into FR, keeping the sticker on UP or DOWN facing FRONT and turning it over,
# and send the edge of FR back to the same slot.
LAST_EDGES_ENTRIES: tuple[tuple[EdgeSlot, str, str], ...] = (
    (EdgeSlot.UF, "R U' R' U2", "U' F' U F U'"),
    (EdgeSlot.DF, "R' D R D2", "D F D' F' D"),
)

# Bring the edge stored on UB or DB back into FL, sending the edge of FL to UF or DF.
LAST_EDGES_UP_RETURN: str = "U2 L' U L U2"
LAST_EDGES_DOWN_RETURN: str = "D2 L D' L' D2"


def right_insertion(size: int, row: int, helper: Layer) -> str:
    """
    Returns the algorithm that carries the wing in a row of FR into the same row of FL, keeping BL and BR.

    The row is turned into FL, and the edge of FL is stored on the helper face in place of the edge in
    its front slot, which comes into FL. The row is turned back, taking that edge's wing into FR, and the
    stored edge is brought back into FL. If the turn of the row also turned the helper face, the face is
    turned back before the edge is stored.

    Example, on a 5x5, with the helper edge on UP:

        >>> right_insertion(5, 1, Layer.UP)
        "Uw U' L' U L Uw' U' L' U L U2"

    and for the lower row, whose turn leaves UP alone:

        >>> right_insertion(5, 3, Layer.UP)
        "Dw' L' U L Dw U2 L' U L U2"

    :param size: The size of the cube
    :param row: The row, from 1 to `size - 2`, outside the middle of an odd cube
    :param helper: The face whose front slot holds the unpaired edge, UP or DOWN
    :return: The algorithm, in standard notation
    """

    turn = slice_turn(size, row, EdgeSlot.FR, EdgeSlot.FL)
    block = Move.from_str(turn)

    if helper is Layer.UP:
        store, bring = EDGES_UP_STORE, LAST_EDGES_UP_RETURN
    else:
        store, bring = EDGES_DOWN_STORE, LAST_EDGES_DOWN_RETURN

    if block.layer is not helper:
        return f"{turn} {store} {inverse_of(turn)} {bring}"

    align = Move(helper, block.direction.inverse(), 1)
    half_turn, rest = bring.split(" ", 1)
    realign = combine(align.inverse(), Move.from_str(half_turn))

    return f"{turn} {align} {store} {inverse_of(turn)} {realign} {rest}"


def middle_routes(size: int, row: int, slot: EdgeSlot, index: int, helper: Layer) -> list[str]:
    """
    Returns the routes that bring a wing into FL's row while BL and BR hold paired edges, with the
    unpaired edge of the helper face in its front slot.

    - On FL, in the mirrored row: the mirrored row is turned into FR, flipped, and turned back, which
      leaves the wing in FR's row, where it is inserted with `right_insertion`.
    - On FR, in the row: it is inserted. In the mirrored row, the edge is flipped first.
    - On UF or DF: the edge is brought into FR, keeping or turning over its sticker, and inserted. Which
      of the two puts the wing in the row depends on the wing, so both are returned.

    A wing already in FL's row, or anywhere else, gives no route.

    Example, on a 5x5, for the upper row, with the helper edge on UP:

        >>> middle_routes(5, 1, EdgeSlot.FR, 3, Layer.UP)
        ["R U R' F R' F' R U' Uw U' L' U L Uw' U' L' U L U2"]

    :param size: The size of the cube
    :param row: The row of FL being filled
    :param slot: The slot the wing is in
    :param index: The wing's index in the slot
    :param helper: The face whose front slot holds the unpaired edge, UP or DOWN
    :return: The routes, in standard notation
    """

    insert = right_insertion(size, row, helper)

    if slot is EdgeSlot.FL:
        if index == row:
            return []
        mirror = size - 1 - row
        return [
            f"{slice_turn(size, mirror, EdgeSlot.FL, EdgeSlot.FR)} {LAST_EDGES_FLIP} "
            f"{slice_turn(size, mirror, EdgeSlot.FR, EdgeSlot.FL)} {insert}"
        ]

    if slot is EdgeSlot.FR:
        return [insert] if index == row else [f"{LAST_EDGES_FLIP} {insert}"]

    return [f"{entry} {insert}" for front, good, bad in LAST_EDGES_ENTRIES if slot is front for entry in (good, bad)]


def last_pair_routes(size: int, row: int, slot: EdgeSlot, index: int) -> list[str]:
    """
    Returns the routes that bring a wing into FL's row when FL and FR hold the only unpaired edges.

    Every route turns rows of the side faces and turns them back, so the paired edges of BL and BR are
    kept.

    - On FL, in the mirrored row: the row and the mirrored row are both turned into FR, FR is flipped,
      and both are turned back.
    - On FR, in the row: `R2` takes the edge to BR, the row is turned into BR, BR is flipped, the row is
      turned back and `R2` is undone.
    - On FR, in the mirrored row: the row is turned into FR, FR is flipped, and the row is turned back.

    A wing already in FL's row, or anywhere else, gives no route.

    Example, on a 5x5, for the upper row:

        >>> last_pair_routes(5, 1, EdgeSlot.FR, 3)
        ["Uw' R U R' F R' F' R U' Uw"]
        >>> last_pair_routes(5, 1, EdgeSlot.FR, 1)
        ["R2 Uw2 y R U R' F R' F' R y' Uw2 R2"]

    :param size: The size of the cube
    :param row: The row of FL being filled
    :param slot: The slot the wing is in
    :param index: The wing's index in the slot
    :return: The routes, in standard notation
    """

    out = slice_turn(size, row, EdgeSlot.FL, EdgeSlot.FR)
    mirror = size - 1 - row

    if slot is EdgeSlot.FL and index == mirror:
        out_mirror = slice_turn(size, mirror, EdgeSlot.FL, EdgeSlot.FR)
        return [f"{out} {out_mirror} {LAST_EDGES_FLIP} {inverse_of(out_mirror)} {inverse_of(out)}"]

    if slot is not EdgeSlot.FR:
        return []

    if index == row:
        across = slice_turn(size, row, EdgeSlot.FL, EdgeSlot.BR)
        return [f"R2 {across} {flip(EdgeSlot.BR)} {inverse_of(across)} R2"]

    return [f"{out} {LAST_EDGES_FLIP} {inverse_of(out)}"]


def build_last_four_edges(cube: Cube) -> list[str]:
    """
    Returns the algorithms that pair the last four edges of a big cube whose centers are built and whose
    other eight edges are paired on UP and DOWN, white on UP.

    `LAST_EDGES_SETUP` brings two of the four into UF and DF. The edge in FL is paired with the edge in
    UF as the helper, and stored on UP in its place, which brings that edge into FL. It is paired with
    the edge in DF as the helper, and stored on DOWN, which brings that edge into FL. The edge in FL is
    then paired with `last_pair_routes`, which leaves the last edge, in FR, with its wings but not
    necessarily paired.

    Example, on a 4x4 turned with `Uw`, whose four split edges are all between the side faces. The
    second edge is already paired when it comes into FL, so it is stored straight away:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("Uw"))
        >>> build_last_four_edges(cube)
        ["B' U2 D2", "Dw' L' U L Dw U2 L' U L U2", "L' U L", "L D' L'", "Dw R U R' F R' F' R U' Dw'"]

    :param cube: The cube, of size 4 or more, held with white on UP
    :return: The algorithms, in the order they are applied
    """

    moves = [LAST_EDGES_SETUP]
    cube = trial(cube, LAST_EDGES_SETUP)

    for helper, store in ((Layer.UP, EDGES_UP_STORE), (Layer.DOWN, EDGES_DOWN_STORE)):
        edge_moves, cube = build_edge(cube, partial(middle_routes, helper=helper))
        moves += edge_moves + [store]
        cube = trial(cube, store)

    edge_moves, cube = build_edge(cube, last_pair_routes)

    return moves + edge_moves
