# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.center_search import search_center
from rubik_cube_solver.solve.cube_nxn.centers import CENTERS_PLAN, first_route
from rubik_cube_solver.solve.cube_nxn.pieces import (
    CenterSticker,
    bar_columns,
    fill_order,
    finished_centers,
    fixed_centers,
    line_cells,
    right_cells,
)
from rubik_cube_solver.solve.cube_nxn.routes import (
    commutator_routes,
    cycle_routes,
    front_insertion,
    line_lift_routes,
    staging_middle_routes,
    trial,
)


def build_front_line(cube: Cube, color: Color, keep: list[CenterSticker]) -> tuple[list[str], Cube]:
    """
    Fills the middle row of an odd cube's FRONT, one cell at a time in `line_cells` order.

    With four centers finished, every piece of a line cell's position type that is not on FRONT is
    on UP, so each empty cell is filled from UP with `line_lift_routes`. The cells filled before, and
    the cells in `keep`, are protected.

    Example, on a 5x5 turned with `Lw' L U`. The column slice carried the left cell of FRONT's middle
    row up to UP and `U` turned it away, so UP is turned back and the piece is brought down:

        >>> cube = Cube(5)
        >>> Rotator(cube).apply(Algorithm.from_str("Lw' L U"))
        >>> build_front_line(cube, Color.GREEN, [])[0]
        ["U' Lw L' F L Lw' F'"]

    :param cube: The cube, of odd size
    :param color: The colour being built
    :param keep: The cells that must survive, such as finished centers and fixed centers
    :return: The routes used and the cube with the line filled
    """

    size = cube.size
    built: list[tuple[int, int]] = []
    moves: list[str] = []

    for cell in line_cells(size, False):
        if cube.layers[Layer.FRONT][cell[0] * size + cell[1]] is not color:
            protect = [CenterSticker(Layer.FRONT, row, col, color) for row, col in built] + keep
            goal = CenterSticker(Layer.FRONT, *cell, color)
            fetched = None

            for piece in search_center(cube, color, *cell):
                if piece.layer is not Layer.UP:
                    continue
                if fetched := first_route(cube, line_lift_routes(size, cell, piece), goal, protect):
                    break

            if fetched is None:
                raise ValueError(f"No route fills FRONT {cell} of the {color.name} middle line")

            route, cube = fetched
            moves.append(route)

        built.append(cell)

    return moves, cube


def fill_staging_cell(
    cube: Cube, color: Color, cell: tuple[int, int], protect: list[CenterSticker]
) -> tuple[str, Cube]:
    """
    Fills a cell of the bar staged on UP by the first commutator that leaves everything protected
    intact.

    The commutators of `commutator_routes` are tried first. When none of them fills the cell, each of
    them that keeps everything protected is tried as a first step, followed by any of them that then
    fills the cell.

    Example, on a 5x5 turned with the commutator `Rw R' U2 R Rw' U2`, which takes the white piece
    out of UP (3, 1). A commutator on the left column brings another one in:

        >>> cube = Cube(5)
        >>> Rotator(cube).apply(Algorithm.from_str("Rw R' U2 R Rw' U2"))
        >>> fill_staging_cell(cube, Color.WHITE, (3, 1), [])[0]
        "Lw' L U L' Lw U'"

    :param cube: The cube
    :param color: The colour being built
    :param cell: The cell of the staging row on UP
    :param protect: The cells that must still hold their colour afterwards
    :return: The route and the cube after it
    """

    size = cube.size
    goal = CenterSticker(Layer.UP, *cell, color)
    routes = commutator_routes(size, cell)

    if fetched := first_route(cube, routes, goal, protect):
        return fetched

    for opening in routes:
        opened = trial(cube, opening)

        if not all(opened.layers[kept.layer][kept.row * size + kept.col] is kept.color for kept in protect):
            continue

        if fetched := first_route(opened, routes, goal, protect):
            return f"{opening} {fetched[0]}", fetched[1]

    raise ValueError(f"No route fills UP {cell} of the {color.name} bar")


def build_front_bar(
    cube: Cube, color: Color, col: int, built: list[tuple[int, int]], keep: list[CenterSticker]
) -> tuple[list[str], Cube]:
    """
    Stages one bar on UP and inserts it into a column of FRONT's left half.

    The bar is staged in row `size - 1 - col` of UP, one cell at a time in `fill_order`, so on an odd
    cube its middle cell comes first. The middle cell is filled with `staging_middle_routes`, from UP
    or from a free cell of FRONT; every other cell with `fill_staging_cell`. The staged cells filled
    before, the cells of FRONT already built and the cells in `keep` are protected. The finished bar
    goes in with `front_insertion`.

    Example, on a 4x4 turned with `Lw' L U2`, which carries FRONT's left column up and turns it to
    the back of UP. Each staged cell takes one commutator, and the bar goes back into column 1:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("Lw' L U2"))
        >>> build_front_bar(cube, Color.GREEN, 1, [], [])[0]
        ["U Lw' L U' L' Lw", "Rw R' U R Rw' U'", "U Lw F2 Lw' F2"]

    :param cube: The cube
    :param color: The colour being built
    :param col: The column of FRONT the bar goes to, in its left half
    :param built: The cells of FRONT already built
    :param keep: The cells that must survive, such as finished centers and fixed centers
    :return: The algorithms used and the cube with the bar inserted
    """

    size = cube.size
    row = size - 1 - col
    front = [CenterSticker(Layer.FRONT, r, c, color) for r, c in built] + keep
    staged: list[CenterSticker] = []
    moves: list[str] = []

    for index in fill_order(size):
        cell = (row, index)

        if cube.layers[Layer.UP][row * size + index] is not color:
            protect = staged + front

            if 2 * index == size - 1:
                goal = CenterSticker(Layer.UP, *cell, color)
                fetched = None

                for piece in search_center(cube, color, *cell):
                    if piece.layer is Layer.FRONT and (piece.row, piece.col) in built:
                        continue
                    if fetched := first_route(cube, staging_middle_routes(size, cell, piece), goal, protect):
                        break

                if fetched is None:
                    raise ValueError(f"No route fills UP {cell} of the {color.name} bar")
            else:
                fetched = fill_staging_cell(cube, color, cell, protect)

            route, cube = fetched
            moves.append(route)

        staged.append(CenterSticker(Layer.UP, *cell, color))

    placed = front_insertion(size, col)

    return moves + [placed], trial(cube, placed)


def fill_right_half(
    cube: Cube, color: Color, built: list[tuple[int, int]], keep: list[CenterSticker]
) -> tuple[list[str], Cube]:
    """
    Fills FRONT's right half one cell at a time, in `right_cells` order, from UP.

    Every cell is filled with `cycle_routes`, which change no other cell of FRONT. With the left half
    built, a piece of each empty cell's position type is always on UP. The cells of FRONT built
    before and the cells in `keep` are protected.

    Example, on a 4x4 turned with `Rw R'`, which carries FRONT's right column up to UP. Each cell is
    brought back down on its own:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("Rw R'"))
        >>> fill_right_half(cube, Color.GREEN, [(1, 1), (2, 1)], [])[0]
        ["Rw' R F' Lw L' F R' Rw F' L Lw' F", "Rw' R F Lw L' F' R' Rw F L Lw' F'"]

    :param cube: The cube
    :param color: The colour being built
    :param built: The cells of FRONT already built
    :param keep: The cells that must survive, such as finished centers and fixed centers
    :return: The routes used and the cube with FRONT's center finished
    """

    size = cube.size
    built = list(built)
    moves: list[str] = []

    for cell in right_cells(size):
        if cube.layers[Layer.FRONT][cell[0] * size + cell[1]] is not color:
            protect = [CenterSticker(Layer.FRONT, row, col, color) for row, col in built] + keep
            goal = CenterSticker(Layer.FRONT, *cell, color)
            fetched = None

            for piece in search_center(cube, color, *cell):
                if piece.layer is not Layer.UP:
                    continue
                if fetched := first_route(cube, cycle_routes(size, cell, piece), goal, protect):
                    break

            if fetched is None:
                raise ValueError(f"No route fills FRONT {cell} of the {color.name} center")

            route, cube = fetched
            moves.append(route)

        built.append(cell)

    return moves, cube


def build_last_two_centers(cube: Cube) -> list[str]:
    """
    Returns the algorithms that build the blue and orange centers of a big cube whose first four
    centers are built.

    The grip `build_first_four_centers` ends in holds blue's face in front and orange's on top. On an
    odd cube the middle row of FRONT is built first with `build_front_line` and turned upright with
    `F`. The bars of FRONT's left half follow, innermost first, with `build_front_bar`, and then its
    right half with `fill_right_half`. Orange is left finished on UP, since every other center is.
    The finished centers, the fixed centers and every cell of FRONT built so far are protected
    throughout. The cube itself is not turned.

    Example, on a 4x4 held in that grip with `y2 z'` and turned with `Lw' L U L' Lw`, which changes
    only FRONT and UP. One commutator and the insertion build the left column, and two cycles the
    right one:

        >>> cube = Cube(4)
        >>> Rotator(cube).apply(Algorithm.from_str("y2 z' Lw' L U L' Lw"))
        >>> build_last_two_centers(cube)
        ["U2 Lw' L U2 L' Lw", "U Lw F2 Lw' F2", "U Rw' R F' Lw L' F R' Rw F' L Lw' F",
         "U Rw' R F Lw L' F' R' Rw F L Lw' F'"]

    :param cube: The cube, of size 4 or more, with its first four centers built
    :return: The algorithms, in the order they are applied
    """

    size = cube.size
    color = Color.BLUE
    keep = finished_centers(cube, [plan.color for plan in CENTERS_PLAN])
    built: list[tuple[int, int]] = []
    moves: list[str] = []

    if size % 2:
        keep = keep + fixed_centers(cube)
        moves, cube = build_front_line(cube, color, keep)
        moves.append("F")
        cube = trial(cube, "F")
        built = line_cells(size, True)

    for col in bar_columns(size):
        bar_moves, cube = build_front_bar(cube, color, col, built, keep)
        moves += bar_moves
        built = built + [(row, col) for row in range(1, size - 1)]

    right_moves, _ = fill_right_half(cube, color, built, keep)

    return moves + right_moves
