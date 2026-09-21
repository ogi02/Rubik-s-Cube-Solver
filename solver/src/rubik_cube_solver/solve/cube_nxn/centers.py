# Python imports
from typing import NamedTuple

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.center_search import CenterSearchResult
from rubik_cube_solver.solve.cube_nxn.pieces import (
    CenterSticker,
    bar_rows,
    built_cells,
    fill_order,
    finished_centers,
    protected,
    rank_candidates,
)
from rubik_cube_solver.solve.cube_nxn.routes import (
    across_routes,
    direct_route,
    insertion,
    staging_routes,
    target_routes,
    trial,
)


class CenterPlan(NamedTuple):
    """
    How one center is built: its colour, the face it is built on, the whole-cube rotation made before
    it, and the faces its pieces are fetched from, grouped into tiers from most to least preferred.
    """

    color: Color
    target: Layer
    regrip: str
    priority: tuple[tuple[Layer, ...], ...]


# The first four centers, in the order they are built, with FRONT always the staging face. Yellow and
# white go to RIGHT and LEFT, which no column slice reaches. Green is then built on DOWN, and `x'`
# carries it to BACK before red is built on DOWN too.
#
# The first tier is the faces on the column slice, imported straight. The second is the faces that
# need a conjugate first: the side faces for yellow and white, moved onto BACK, and the target DOWN
# for green and red, moved onto UP. The last is FRONT itself. A face holding a finished center is
# left out.
CENTERS_PLAN: tuple[CenterPlan, ...] = (
    CenterPlan(
        Color.YELLOW,
        Layer.RIGHT,
        "z'",
        ((Layer.UP, Layer.BACK, Layer.DOWN), (Layer.LEFT, Layer.RIGHT), (Layer.FRONT,)),
    ),
    CenterPlan(Color.WHITE, Layer.LEFT, "", ((Layer.UP, Layer.BACK, Layer.DOWN), (Layer.LEFT,), (Layer.FRONT,))),
    CenterPlan(Color.GREEN, Layer.DOWN, "x'", ((Layer.BACK, Layer.UP), (Layer.DOWN,), (Layer.FRONT,))),
    CenterPlan(Color.RED, Layer.DOWN, "x'", ((Layer.UP,), (Layer.DOWN,), (Layer.FRONT,))),
)


def fetch(
    cube: Cube,
    color: Color,
    cell: tuple[int, int],
    piece: CenterSearchResult,
    target: Layer,
    protect: list[CenterSticker],
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

    for route in routes:
        result = trial(cube, route)
        filled = result.layers[Layer.FRONT][cell[0] * size + cell[1]] is color
        kept = all(
            result.layers[sticker.layer][sticker.row * size + sticker.col] is sticker.color for sticker in protect
        )

        if filled and kept:
            return route, result

    return None


def build_bar(
    cube: Cube,
    color: Color,
    row: int,
    priority: tuple[tuple[Layer, ...], ...],
    target: Layer,
    inserted: list[int],
    keep: list[CenterSticker],
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


def build_center(
    cube: Cube,
    color: Color,
    target: Layer,
    priority: tuple[tuple[Layer, ...], ...],
    keep: list[CenterSticker],
) -> tuple[list[str], Cube]:
    """
    Builds one center on the target face, one bar at a time.

    Each bar is filled in a row of FRONT and moved onto the target with `insertion`.

    Example, on a 4x4 turned with `z' Dw`. The first bar is filled from BACK and inserted, and the
    insertion's half turns of RIGHT bring the rest of yellow into the bar row, so the second bar
    only needs inserting:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("z' Dw"))
        >>> build_center(cube, Color.YELLOW, Layer.RIGHT, CENTERS_PLAN[0].priority, [])[0]
        ['B2 Lw2 L2', 'Rw2 R2', "Dw R2 Dw' R2", "Dw R2 Dw' R2"]

    :param cube: The cube
    :param color: The colour being built
    :param target: The face the center is built on
    :param priority: The source faces, grouped into tiers from most to least preferred
    :param keep: The cells of the finished centers
    :return: The algorithms used and the cube with the center built
    """

    rows = bar_rows(cube.size)
    moves: list[str] = []

    for index, row in enumerate(rows):
        bar_moves, cube = build_bar(cube, color, row, priority, target, rows[:index], keep)
        placed = insertion(cube.size, row, target)
        cube = trial(cube, placed)
        moves += bar_moves + [placed]

    return moves, cube


def build_first_four_centers(cube: Cube) -> list[str]:
    """
    Returns the algorithms that build the yellow, white, green and red centers of an even cube.

    The centers are built in the order of `CENTERS_PLAN`, each after its regrip, and every center
    already finished is protected while the next one is built. The cube itself is not turned.

    Example, on a 4x4 scrambled with `Rw U2 Lw' F Dw`. The list opens with yellow's regrip, the one
    fetch its first bar needs, that bar's insertion, and the first fetch of the second bar:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("Rw U2 Lw' F Dw"))
        >>> moves = build_first_four_centers(cube)
        >>> len(moves), moves[:4]
        (22, ["z'", "U Rw' R", "Dw R2 Dw' R2", "Lw L'"])

    :param cube: The cube, of even size 4 or more
    :return: The algorithms, in the order they are applied, including the regrips
    """

    moves: list[str] = []
    done: list[Color] = []

    for plan in CENTERS_PLAN:
        if plan.regrip:
            cube = trial(cube, plan.regrip)
            moves.append(plan.regrip)

        center_moves, cube = build_center(cube, plan.color, plan.target, plan.priority, finished_centers(cube, done))
        moves += center_moves
        done.append(plan.color)

    return moves
