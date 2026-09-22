# Python imports
from typing import NamedTuple

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.center_search import CenterSearchResult, search_center
from rubik_cube_solver.solve.cube_nxn.pieces import (
    Sticker,
    bar_rows,
    built_cells,
    fill_order,
    finished_centers,
    fixed_centers,
    line_cells,
    protected,
    rank_candidates,
)
from rubik_cube_solver.solve.cube_nxn.routes import (
    across_routes,
    direct_route,
    insertion,
    line_routes,
    line_target_routes,
    staging_routes,
    target_routes,
    trial,
)
from rubik_cube_solver.solve.cube_nxn.view import held_in_view


class CenterPlan(NamedTuple):
    """
    How one center is built: its colour, the face it is built on, the whole-cube rotation made before
    it, the faces its pieces are fetched from, grouped into tiers from most to least preferred, and
    whether an odd cube's middle line runs down the face rather than across it.
    """

    color: Color
    target: Layer
    regrip: str
    priority: tuple[tuple[Layer, ...], ...]
    vertical_line: bool


# The first four centers, in the order they are built, with FRONT always the staging face. Yellow and
# white go to RIGHT and LEFT, which no column slice reaches. Green is then built on DOWN, and `x'`
# carries it to BACK before red is built on DOWN too.
#
# The first tier is the faces on the column slice, imported straight. The second is the faces that
# need a conjugate first: the side faces for yellow and white, moved onto BACK, and the target DOWN
# for green and red, moved onto UP. The last is FRONT itself. A face holding a finished center is
# left out.
#
# On an odd cube the middle line is held across the face for yellow and white and down it for green
# and red, the way the bars arrive on each face.
CENTERS_PLAN: tuple[CenterPlan, ...] = (
    CenterPlan(
        Color.YELLOW,
        Layer.RIGHT,
        "z'",
        ((Layer.UP, Layer.BACK, Layer.DOWN), (Layer.LEFT, Layer.RIGHT), (Layer.FRONT,)),
        False,
    ),
    CenterPlan(Color.WHITE, Layer.LEFT, "", ((Layer.UP, Layer.BACK, Layer.DOWN), (Layer.LEFT,), (Layer.FRONT,)), False),
    CenterPlan(Color.GREEN, Layer.DOWN, "x'", ((Layer.BACK, Layer.UP), (Layer.DOWN,), (Layer.FRONT,)), True),
    CenterPlan(Color.RED, Layer.DOWN, "x'", ((Layer.UP,), (Layer.DOWN,), (Layer.FRONT,)), True),
)


def fetch(
    cube: Cube,
    color: Color,
    cell: tuple[int, int],
    piece: CenterSearchResult,
    target: Layer,
    protect: list[Sticker],
) -> tuple[str, Cube] | None:
    """
    Brings a piece into the FRONT cell, by the first route that leaves everything protected intact.

    The face the piece is on decides which routes exist: a piece on FRONT is moved within the face,
    one on LEFT or RIGHT is extracted onto BACK first, one on the target DOWN is lifted onto UP first,
    and one on UP, BACK or DOWN is brought in straight. Each route is tried on a copy of the cube, in
    the order it is generated.

    Example, on a 4x4 turned with `z' Dw`, filling FRONT (2, 1) from BACK (2, 1). `B2` stands the
    piece where the slice collects and `Lw2 L2` turns the slice:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("z' Dw"))
        >>> route, result = fetch(cube, Color.YELLOW, (2, 1), CenterSearchResult(Layer.BACK, 2, 1), Layer.RIGHT, [])
        >>> route
        'B2 Lw2 L2'

    :param cube: The cube
    :param color: The colour being built
    :param cell: The FRONT cell being filled, as (row, column)
    :param piece: The piece to bring in
    :param target: The face the center is being built on
    :param protect: The cells that must still hold their colour afterwards
    :return: The route and the cube after it, or None if no route fills the cell
    """

    size = cube.size

    match piece.layer:
        case Layer.FRONT:
            routes = staging_routes(size)
        case Layer.LEFT | Layer.RIGHT:
            routes = across_routes(cube, color, cell, piece)
        case Layer.DOWN if target is Layer.DOWN:
            routes = target_routes(cube, color, cell, piece)
        case _:
            routes = [direct_route(size, cell, piece, restore) for restore in (False, True)]

    return first_route(cube, routes, Sticker(Layer.FRONT, *cell, color), protect)


def first_route(cube: Cube, routes: list[str], goal: Sticker, protect: list[Sticker]) -> tuple[str, Cube] | None:
    """
    Returns the first route that puts the colour on the goal cell and leaves everything protected
    intact, together with the cube after it.

    Each route is tried on a copy of the cube, in the order given.

    Example, on a 4x4 turned with `Lw L'`, filling FRONT (2, 1) with green. `F2` alone fills it but
    breaks the protected cell (1, 2), so the second route is taken:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("Lw L'"))
        >>> goal = Sticker(Layer.FRONT, 2, 1, Color.GREEN)
        >>> first_route(cube, ["F2", "Lw' L"], goal, [Sticker(Layer.FRONT, 1, 2, Color.GREEN)])[0]
        "Lw' L"

    :param cube: The cube
    :param routes: The candidate routes, in standard notation
    :param goal: The cell to fill, with the colour it must hold afterwards
    :param protect: The cells that must still hold their colour afterwards
    :return: The route and the cube after it, or None if no route fills the cell
    """

    size = cube.size

    for route in routes:
        result = trial(cube, route)
        kept = all(
            result.layers[sticker.layer][sticker.row * size + sticker.col] is sticker.color
            for sticker in [goal] + protect
        )

        if kept:
            return route, result

    return None


def fetch_line_piece(
    cube: Cube,
    color: Color,
    cell: tuple[int, int],
    piece: CenterSearchResult,
    target: Layer,
    protect: list[Sticker],
) -> tuple[str, Cube] | None:
    """
    Brings a piece into a cell of the target's middle line, by the first route that leaves everything
    protected intact.

    A piece on the target is moved within it with `line_target_routes`; a piece on any other face is
    carried in with `line_routes`.

    Example, on a 5x5 turned with `z' Fw D`: `z'` puts the yellow center on RIGHT, `Fw` carries the
    left cell of its middle line to DOWN and `D` turns it away. `D'` stands it back in the block and
    `Fw'` carries it in:

        >>> cube = Cube(5)
        >>> Rotator(cube).apply(Algorithm.from_str("z' Fw D"))
        >>> piece = CenterSearchResult(Layer.DOWN, 2, 3)
        >>> fetch_line_piece(cube, Color.YELLOW, (2, 1), piece, Layer.RIGHT, [])[0]
        "D' Fw'"

    :param cube: The cube, of odd size
    :param color: The colour being built
    :param cell: The cell of the middle line being filled
    :param piece: The piece to bring in
    :param target: The face the center is being built on
    :param protect: The cells that must still hold their colour afterwards
    :return: The route and the cube after it, or None if no route fills the cell
    """

    size = cube.size

    if piece.layer is target:
        routes = line_target_routes(size, cell, target)
    else:
        routes = line_routes(size, cell, piece, target)

    return first_route(cube, routes, Sticker(target, *cell, color), protect)


def build_middle_line(
    cube: Cube, color: Color, target: Layer, vertical: bool, keep: list[Sticker]
) -> tuple[list[str], Cube]:
    """
    Fills the middle line of an odd cube's target face, one cell at a time in `line_cells` order.

    A cell already in the colour is left as it is. Otherwise its candidates are the pieces of its
    position type, those on other faces before those on the target, and not those in cells of the
    line already filled; they are tried in order until one has a route. The cells filled before, and
    the cells in `keep`, are protected.

    Example, on a 5x5 turned with `z' Uw R`, which leaves one yellow piece of the line's type on
    FRONT and the left cell of the line empty. RIGHT is turned to stand the cell in the block of `Dw`,
    FRONT to stand the piece in it, and RIGHT is turned back after the wide move:

        >>> cube = Cube(5)
        >>> Rotator(cube).apply(Algorithm.from_str("z' Uw R"))
        >>> build_middle_line(cube, Color.YELLOW, Layer.RIGHT, False, [])[0]
        ["R F2 Dw R'"]

    :param cube: The cube, of odd size
    :param color: The colour being built
    :param target: The face the center is being built on
    :param vertical: Whether the line runs down the face rather than across it
    :param keep: The cells that must survive, such as finished centers and fixed centers
    :return: The routes used and the cube with the line filled
    """

    size = cube.size
    built: list[tuple[int, int]] = []
    moves: list[str] = []

    for cell in line_cells(size, vertical):
        if cube.layers[target][cell[0] * size + cell[1]] is not color:
            protect = [Sticker(target, row, col, color) for row, col in built] + keep
            candidates = [
                piece
                for piece in search_center(cube, color, *cell)
                if not (piece.layer is target and (piece.row, piece.col) in built)
            ]
            fetched = None

            for piece in sorted(candidates, key=lambda candidate: candidate.layer is target):
                if fetched := fetch_line_piece(cube, color, cell, piece, target, protect):
                    break

            if fetched is None:
                raise ValueError(f"No route fills {target.name} {cell} of the {color.name} middle line")

            route, cube = fetched
            moves.append(route)

        built.append(cell)

    return moves, cube


def build_bar(
    cube: Cube,
    color: Color,
    row: int,
    priority: tuple[tuple[Layer, ...], ...],
    target: Layer,
    inserted: list[int],
    keep: list[Sticker],
) -> tuple[list[str], Cube]:
    """
    Fills one row of FRONT with the colour, one cell at a time in `fill_order`.

    For each cell the candidates are ranked again, since filling a cell can move the pieces of the
    next one, and tried in order until one has a route. The routes within FRONT do not depend on
    which FRONT piece is meant, so they are tried for the first FRONT candidate only.

    Example, on a 4x4 turned with `z' Dw`, which carries yellow's lower half to BACK. Column 1 needs
    BACK turned before its slice collects the piece; column 2 does not:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("z' Dw"))
        >>> build_bar(cube, Color.YELLOW, 2, CENTERS_PLAN[0].priority, Layer.RIGHT, [], [])[0]
        ['B2 Lw2 L2', 'Rw2 R2']

    :param cube: The cube
    :param color: The colour being built
    :param row: The row of FRONT to fill
    :param priority: The source faces, grouped into tiers from most to least preferred
    :param target: The face the center is being built on
    :param inserted: The staging rows of the bars already inserted, in order
    :param keep: The cells of the finished centers
    :return: The routes used and the cube with the bar filled
    """

    size = cube.size
    finished = built_cells(size, target, inserted)
    moves: list[str] = []

    for col in fill_order(size):
        cell = (row, col)

        if cube.layers[Layer.FRONT][row * size + col] is color:
            continue

        protect = protected(cube, color, cell, target, inserted, keep)
        candidates = rank_candidates(cube, color, cell, priority, target, finished)
        fetched = None
        tried_front = False

        for piece in candidates:
            if piece.layer is Layer.FRONT:
                if tried_front:
                    continue
                tried_front = True

            if fetched := fetch(cube, color, cell, piece, target, protect):
                break

        if fetched is None:
            raise ValueError(f"No route fills FRONT {cell} of the {color.name} bar")

        route, cube = fetched
        moves.append(route)

    return moves, cube


def build_center(cube: Cube, plan: CenterPlan, keep: list[Sticker]) -> tuple[list[str], Cube]:
    """
    Builds one center on the target face of its plan.

    On an odd cube the middle line is built first, with `build_middle_line`, and every fixed center
    and then the line are protected from there on. The rest of the center is built one bar at a
    time: each bar is filled in a row of FRONT and moved onto the target with `insertion`.

    Example, on a 4x4 turned with `z' Dw`. The first bar is filled from BACK and inserted, and the
    insertion's half turns of RIGHT bring the rest of yellow into the bar row, so the second bar
    only needs inserting:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("z' Dw"))
        >>> build_center(cube, CENTERS_PLAN[0], [])[0]
        ['B2 Lw2 L2', 'Rw2 R2', "Dw R2 Dw' R2", "Dw R2 Dw' R2"]

    :param cube: The cube, of size 4 or more
    :param plan: The plan of the center
    :param keep: The cells of the finished centers
    :return: The algorithms used and the cube with the center built
    """

    size = cube.size
    moves: list[str] = []

    if size % 2:
        keep = keep + fixed_centers(cube)
        moves, cube = build_middle_line(cube, plan.color, plan.target, plan.vertical_line, keep)
        keep = keep + [Sticker(plan.target, row, col, plan.color) for row, col in line_cells(size, plan.vertical_line)]

    rows = bar_rows(size)

    for index, row in enumerate(rows):
        bar_moves, cube = build_bar(cube, plan.color, row, plan.priority, plan.target, rows[:index], keep)
        placed = insertion(size, row, plan.target)
        cube = trial(cube, placed)
        moves += bar_moves + [placed]

    return moves, cube


def build_first_four_centers(cube: Cube, in_view: bool = False) -> list[str]:
    """
    Returns the algorithms that build the yellow, white, green and red centers of a big cube.

    The centers are built in the order of `CENTERS_PLAN`, each after its regrip, and every center
    already finished is protected while the next one is built. The cube itself is not turned.

    Built in view, each center whose face points away from a viewer is instead built with the cube
    turned so that face comes forward, and turned back afterwards. The work and its result are the
    same either way, so the two forms differ only in whether the cube is held to be watched.

    Example, on a 4x4 scrambled with `Rw U2 Lw' F Dw`. The list opens with yellow's regrip, the one
    fetch its first bar needs, that bar's insertion, and the first fetch of the second bar:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("Rw U2 Lw' F Dw"))
        >>> moves = build_first_four_centers(cube)
        >>> len(moves), moves[:4]
        (22, ["z'", "U Rw' R", "Dw R2 Dw' R2", "Lw L'"])

    :param cube: The cube, of size 4 or more
    :param in_view: Whether to hold the cube so the face each center is built on can be seen
    :return: The algorithms, in the order they are applied, including the regrips
    """

    moves: list[str] = []
    done: list[Color] = []

    for plan in CENTERS_PLAN:
        if plan.regrip:
            cube = trial(cube, plan.regrip)
            moves.append(plan.regrip)

        center_moves, cube = build_center(cube, plan, finished_centers(cube, done))
        moves += held_in_view(center_moves, plan.target) if in_view else center_moves
        done.append(plan.color)

    return moves
