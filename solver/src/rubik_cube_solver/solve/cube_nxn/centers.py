# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.center_search import CenterSearchResult, search_center
from rubik_cube_solver.solve.cube_nxn.notation import (
    NOTATION_INVERSE_TABLE,
    center_cells,
    center_positions,
    column_slice,
    row_slice,
)

# Whole-cube rotation that brings the face carrying the white fixed center to UP. Only an odd cube
# has fixed centers, so only an odd cube is oriented: on an even cube no face has a color yet.
CENTERS_WHITE_UP_TABLE: dict[Layer, str] = {
    Layer.UP: "",
    Layer.DOWN: "x2",
    Layer.LEFT: "z",
    Layer.RIGHT: "z'",
    Layer.FRONT: "x",
    Layer.BACK: "x'",
}

# Whole-cube rotation that brings the face carrying the green fixed center to FRONT, once white is
# already on UP. Only a turn around the vertical axis is allowed here, or white would leave UP.
CENTERS_GREEN_FRONT_TABLE: dict[Layer, str] = {
    Layer.FRONT: "",
    Layer.LEFT: "y'",
    Layer.BACK: "y2",
    Layer.RIGHT: "y",
}

# The four centers in the order they are built: the color, the rotation that brings the cube into
# the frame that center is built in, and the face it is built on. The rotations add up to `x2 x2 y'
# y`, so the cube ends in the orientation the orientation tables put it in.
CENTERS_BUILD_TABLE: tuple[tuple[Color, str, Layer], ...] = (
    (Color.WHITE, "x2", Layer.DOWN),
    (Color.YELLOW, "x2", Layer.DOWN),
    (Color.GREEN, "y'", Layer.RIGHT),
    (Color.RED, "y", Layer.RIGHT),
)

# The notation of one, two and three clockwise turns of a face.
CENTERS_QUARTER_TABLE: dict[int, str] = {1: "", 2: "2", 3: "'"}

# The face the bar is assembled on, and the face a piece that cannot be imported is routed through.
CENTERS_STAGING_LAYER: Layer = Layer.BACK
CENTERS_SOURCE_LAYER: Layer = Layer.LEFT

# The direction of the slice that hands a face's row straight to the staging face, keyed by the face
# the row comes from. A row slice cycles FRONT, LEFT, BACK and RIGHT, so LEFT and RIGHT reach the
# staging face in one slice either way round and FRONT reaches it with a half one. A piece on any of
# the three therefore goes into the bar in a single algorithm, rather than being walked around the
# cube one face at a time first.
CENTERS_IMPORT_TABLE: dict[Layer, str] = {
    Layer.LEFT: "",
    Layer.RIGHT: "'",
    Layer.FRONT: "2",
}

# How many algorithms a piece is away from the bar, keyed by the face it lies on. A piece on the
# staging face itself has to leave it before it can be imported back into the bar, and one on the
# face being built is farther still, since fetching it off costs an extraction first.
CENTERS_FETCH_RANK: dict[Layer, int] = {
    Layer.LEFT: 0,
    Layer.FRONT: 0,
    Layer.RIGHT: 0,
    Layer.BACK: 1,
    Layer.DOWN: 2,
    Layer.UP: 2,
}


def turn_notation(layer: Layer, turns: int) -> str:
    """
    Returns the notation of a number of clockwise turns of a face.

    :param layer: The face to turn
    :param turns: The amount of clockwise quarter turns
    :return: The notation of the turn, empty when the face ends where it started
    """

    if turns % 4 == 0:
        return ""

    return f"{layer.value}{CENTERS_QUARTER_TABLE[turns % 4]}"


def cell_color(cube: Cube, layer: Layer, row: int, col: int) -> Color:
    """
    Returns the color of the sticker at a cell of a face.

    :param cube: The Cube instance to read
    :param layer: The face to read
    :param row: The row of the cell
    :param col: The column of the cell
    :return: The color of the sticker
    """

    return cube.layers[layer][row * cube.size + col]


def fixed_center_layer(cube: Cube, color: Color) -> Layer:
    """
    Returns the face whose fixed center carries the given color.

    :param cube: The Cube instance to search
    :param color: The color of the fixed center
    :return: The face whose fixed center carries the color
    """

    for layer in Layer:
        if cube.layers[layer][cube.size * cube.size // 2] == color:
            return layer

    raise ValueError(f"No face has a {color.name.lower()} fixed center.")


def bar_rows(size: int, col: int) -> list[int]:
    """
    Returns the rows of the staging column that a bar is assembled in.

    The fixed center of an odd cube is skipped: it never leaves the staging face, and the cell it
    would fill on the face being built is that face's own fixed center, which is already right.

    :param size: The size of the cube
    :param col: The staging column
    :return: The rows of the staging column that hold a bar piece
    """

    middle = size // 2

    return [row for row in range(1, size - 1) if not (size % 2 and row == middle and col == middle)]


def target_line(size: int, target: Layer, line: int) -> list[tuple[int, int]]:
    """
    Returns the cells of one line of the face being built.

    A bar is inserted into a row of the RIGHT face and into a column of the DOWN face, because the
    slice family that reaches each of them runs a different way around the cube.

    :param size: The size of the cube
    :param target: The face being built
    :param line: The index of the line
    :return: The cells of the line
    """

    if target is Layer.RIGHT:
        return [(line, index) for index in range(1, size - 1)]

    return [(index, line) for index in range(1, size - 1)]


def solved_lines(cube: Cube, color: Color, target: Layer) -> list[int]:
    """
    Returns the lines of the face being built that already carry the color throughout.

    :param cube: The Cube instance to read
    :param color: The color of the center being built
    :param target: The face being built
    :return: The indices of the solved lines
    """

    return [
        line
        for line in range(1, cube.size - 1)
        if all(cell_color(cube, target, row, col) == color for row, col in target_line(cube.size, target, line))
    ]


def center_is_solved(cube: Cube, color: Color, target: Layer) -> bool:
    """
    Returns whether every center cell of a face carries the given color.

    :param cube: The Cube instance to read
    :param color: The color of the center being built
    :param target: The face being built
    :return: Whether the center is solved
    """

    return all(cell_color(cube, target, row, col) == color for row, col in center_cells(cube.size))


def preserved_line(size: int, solved: list[int]) -> int | None:
    """
    Returns the line of the face being built that the next insertion leaves where it is.

    An insertion keeps one line, fills the line opposite it and swaps every other line with its
    opposite, so the line to keep is one whose opposite is not solved yet. A line that is already
    solved is preferred, since keeping it costs nothing, and the middle line of an odd cube is its
    own opposite and cannot be filled this way at all.

    :param size: The size of the cube
    :param solved: The indices of the lines that already carry the color throughout
    :return: The line the next insertion keeps, or None when only the middle line is left
    """

    candidates = [line for line in range(1, size - 1) if size - 1 - line not in solved and line != size - 1 - line]

    if not candidates:
        return None

    return next((line for line in candidates if line in solved), candidates[0])


def bar_column(size: int, target: Layer, preserved: int) -> int:
    """
    Returns the column of the staging face the bar for an insertion is assembled in.

    :param size: The size of the cube
    :param target: The face being built
    :param preserved: The line the insertion keeps
    :return: The staging column
    """

    if target is Layer.RIGHT:
        return preserved

    return size - 1 - preserved


def row_transfer(size: int, receiver: Layer, row: int, direction: str, evict: str) -> str:
    """
    Returns the algorithm handing one row of a side face over to the next one around the cube.

    The slice carries the giving face's row onto the receiving face, the receiving face is turned
    so the arrived row is put away, and the slice is undone. Undoing it takes the row that the turn
    moved into place back to the giving face, and restores the two faces the slice only passed
    through, so the algorithm touches exactly two faces and never a center piece of UP or DOWN.

    :param size: The size of the cube
    :param receiver: The face the row is handed to
    :param row: The row of the side faces
    :param direction: The direction of the slice, "" or "'", which picks the giving face
    :param evict: The turn of the receiving face between the slices, one of "", "'" and "2"
    :return: The algorithm of the transfer
    """

    forward = row_slice(size, row, direction)
    backward = row_slice(size, row, NOTATION_INVERSE_TABLE[direction])

    return f"{forward} {receiver.value}{evict} {backward} {receiver.value}{NOTATION_INVERSE_TABLE[evict]}"


def column_transfer(size: int, receiver: Layer, col: int, direction: str, evict: str) -> str:
    """
    Returns the algorithm handing one column over to the next face around the cube the other way.

    It is the row transfer of the other slice family, the one that runs FRONT, UP, BACK and DOWN,
    and is what reaches the two faces a row slice never touches.

    :param size: The size of the cube
    :param receiver: The face the column is handed to
    :param col: The column of the FRONT face
    :param direction: The direction of the slice, "" or "'", which picks the giving face
    :param evict: The turn of the receiving face between the slices, one of "", "'" and "2"
    :return: The algorithm of the transfer
    """

    forward = column_slice(size, col, direction)
    backward = column_slice(size, col, NOTATION_INVERSE_TABLE[direction])

    return f"{forward} {receiver.value}{evict} {backward} {receiver.value}{NOTATION_INVERSE_TABLE[evict]}"


def line_insertion(size: int, target: Layer, preserved: int) -> str:
    """
    Returns the algorithm inserting a finished bar into the face being built.

    The bar is assembled in a column of the staging face and the slice that reaches the face being
    built carries rows, so the staging face is turned a quarter first when the two run across each
    other. The half turn between the slices is what makes the insertion cost exactly one line: it
    puts the arrived bar in the line opposite the one the slice came back to, so the only line that
    loses its pieces is the one the bar takes over.

    :param size: The size of the cube
    :param target: The face being built
    :param preserved: The line the insertion keeps
    :return: The algorithm of the insertion
    """

    if target is Layer.RIGHT:
        quarter = turn_notation(CENTERS_STAGING_LAYER, 1)
        forward = row_slice(size, preserved, "")
        backward = row_slice(size, preserved, "'")
    else:
        quarter = ""
        forward = column_slice(size, preserved, "")
        backward = column_slice(size, preserved, "'")

    return f"{quarter} {forward} {target.value}2 {backward}".strip()


def middle_completion(size: int, target: Layer) -> str:
    """
    Returns the algorithm filling the middle line of an odd cube.

    The middle line is its own opposite, so the insertion that fills the line opposite the one it
    keeps does nothing there. The face being built is turned a quarter first instead, which lays
    the finished lines across the middle one, and a quarter turn of it between the slices then puts
    the bar into the middle line running the other way, which is the only line left.

    :param size: The size of the cube
    :param target: The face being built
    :return: The algorithm of the completion
    """

    middle = size // 2

    if target is Layer.RIGHT:
        quarter = turn_notation(CENTERS_STAGING_LAYER, 1)
        forward, backward = row_slice(size, middle, ""), row_slice(size, middle, "'")
    else:
        quarter = ""
        forward, backward = column_slice(size, middle, ""), column_slice(size, middle, "'")

    return f"{quarter} {forward} {target.value} {backward}".strip()


def pole_eviction(cube: Cube, color: Color) -> str:
    """
    Returns the next algorithm taking a center piece of the color off the UP face.

    Every algorithm of the build restores UP, so a piece left there is a piece the bar can never
    fetch. The column is carried onto FRONT, one of its cells is left behind there and the rest is
    returned, so the face loses exactly one piece per algorithm. The RIGHT face is turned first, so
    that the sticker left behind is not of the color being built. Only the first center needs this:
    after it, UP carries a color of its own.

    The row slice in the middle is the only move of the build that is not undone, so on an odd cube
    the UP face is turned until the piece leaves the middle row. A middle row slice carries the
    fixed centers of the four side faces around with it, and those decide which color every face
    ends up with.

    :param cube: The Cube instance to read
    :param color: The color of the center being built
    :return: The algorithm, or an empty string when the UP face holds no piece of that color
    """

    size = cube.size
    middle = size // 2
    cells = [cell for cell in center_cells(size) if cell_color(cube, Layer.UP, *cell) == color]

    if not cells:
        return ""

    positions = center_positions(size, *cells[0])
    up_turns = next(turn for turn in range(4) if not (size % 2 and positions[turn][0] == middle))
    row, col = positions[up_turns]
    arrivals = center_positions(size, row, col)
    turns = next(turn for turn in range(4) if cell_color(cube, Layer.RIGHT, *arrivals[-turn]) != color)

    moves = [
        turn_notation(Layer.UP, up_turns),
        turn_notation(Layer.RIGHT, turns),
        column_slice(size, col, "'"),
        row_slice(size, row, ""),
        column_slice(size, col, ""),
    ]

    return " ".join(move for move in moves if move)


def bar_import(size: int, row: int, bar_col: int, result: CenterSearchResult) -> str:
    """
    Returns the algorithm putting a piece into the bar, straight off the face it lies on.

    That face is turned until the piece sits on the very cell of it the bar cell is waiting for, and
    the row it lies in is then handed to the staging face. Which slice does the handing depends on
    where the face is around the cube, and the half turn that fetches from FRONT restores LEFT and
    RIGHT just as the quarter ones restore the two faces they pass through. The turn of the staging
    face is chosen so that the row it displaces leaves along a column, which crosses the bar
    nowhere, rather than along the row that would take a bar piece with it.

    :param size: The size of the cube
    :param row: The row of the bar cell being filled
    :param bar_col: The staging column the bar is assembled in
    :param result: The location of the piece
    :return: The algorithm of the import
    """

    turns = center_positions(size, result.row, result.col).index((row, bar_col))
    evict = "" if row != bar_col else "'"
    direction = CENTERS_IMPORT_TABLE[result.layer]
    moves = [
        turn_notation(result.layer, turns),
        row_transfer(size, CENTERS_STAGING_LAYER, row, direction, evict),
    ]

    return " ".join(move for move in moves if move)


def unturned_line(size: int, line: tuple[str, int], turns: int) -> tuple[str, int]:
    """
    Returns the line of a face that a turn of it brings onto the given line.

    A quarter turn takes rows to columns and columns to rows, and a half turn takes every line to
    the one opposite it, so where an algorithm writes on a face depends on how the face was turned
    before it ran.

    :param size: The size of the cube
    :param line: The line written to, as its kind - "row" or "col" - and its index
    :param turns: The amount of clockwise quarter turns the face was turned by
    :return: The line the written one came from
    """

    kind, index = line

    match turns % 4:
        case 0:
            return line
        case 1:
            return ("col", index) if kind == "row" else ("row", size - 1 - index)
        case 2:
            return kind, size - 1 - index
        case _:
            return ("col", size - 1 - index) if kind == "row" else ("row", index)


def extraction_lines(size: int, row: int, evict: str, turns: int) -> list[tuple[str, int]]:
    """
    Returns the lines of the staging face that an extraction overwrites.

    One takes the row fetched off the face being built and the other takes what that row displaced,
    and which lines they are depends on the turn between the slices and on the quarter turns the
    extraction is conjugated with.

    :param size: The size of the cube
    :param row: The row of the side faces the extraction runs on
    :param evict: The turn of the staging face between the slices, one of "", "'" and "2"
    :param turns: The amount of clockwise quarter turns the extraction is conjugated with
    :return: The lines the extraction overwrites
    """

    displaced = {"": ("col", row), "'": ("col", size - 1 - row), "2": ("row", size - 1 - row)}[evict]

    return [unturned_line(size, ("row", row), turns), unturned_line(size, displaced, turns)]


def bar_cost(cube: Cube, color: Color, bar_col: int, line: tuple[str, int]) -> int:
    """
    Returns how many pieces the bar loses when a line of the staging face is overwritten.

    A column other than the bar's crosses it nowhere and costs nothing. A row crosses it in one
    cell, and the bar's own column costs every piece it holds. Nothing is lost for good either way,
    since the pieces stay on the cube and are fetched again, but a move that costs the bar pieces
    is the last one to reach for.

    :param cube: The Cube instance to read
    :param color: The color of the center being built
    :param bar_col: The staging column the bar is assembled in
    :param line: The line to be overwritten, as its kind - "row" or "col" - and its index
    :return: The amount of bar pieces the line holds
    """

    kind, index = line

    if kind == "col":
        if index != bar_col:
            return 0

        return line_pieces(cube, CENTERS_STAGING_LAYER, color, line)

    return int(cell_color(cube, CENTERS_STAGING_LAYER, index, bar_col) == color)


def target_extraction(
    cube: Cube, color: Color, target: Layer, bar_col: int, result: CenterSearchResult
) -> tuple[int, str]:
    """
    Returns what taking a piece off the face being built costs the bar, and the algorithm doing it.

    The face being built holds pieces of its own color that the bar still needs, and the insertion
    only ever writes to it, so they are fetched out of it here. The form for the DOWN face swaps a
    column with the FRONT face and never touches the staging face at all, so it is free. The one
    for the RIGHT face has to go through the staging face, so it is conjugated by a turn of it and
    the cheapest turn is taken - usually one that costs nothing, and never more than it must. The
    line that receives what the fetched row displaced is written last, so a turn whose line crosses
    the cell the piece lands on would send it straight back and is not among the choices.

    :param cube: The Cube instance to read
    :param color: The color of the center being built
    :param target: The face being built
    :param bar_col: The staging column the bar is assembled in
    :param result: The location of the piece on the face being built
    :return: The amount of bar pieces the extraction costs, and its algorithm
    """

    size = cube.size

    if target is Layer.DOWN:
        positions = center_positions(size, result.row, result.col)
        turns = next(turn for turn in range(1, 4) if positions[turn][1] != result.col)
        forward, backward = column_slice(size, result.col, ""), column_slice(size, result.col, "'")

        return 0, f"{forward} {turn_notation(Layer.FRONT, turns)} {backward}"

    candidates = []
    for turns in range(4):
        arrival = center_positions(size, result.row, result.col)[-turns % 4]
        for evict in CENTERS_QUARTER_TABLE.values():
            lines = extraction_lines(size, result.row, evict, turns)
            if len(set(lines)) == 2 and arrival not in line_cells(size, lines[1]):
                candidates.append((sum(bar_cost(cube, color, bar_col, line) for line in lines), turns, evict))

    cost, turns, evict = min(candidates)
    moves = [
        turn_notation(CENTERS_STAGING_LAYER, turns),
        row_transfer(size, CENTERS_STAGING_LAYER, result.row, "'", evict),
        turn_notation(CENTERS_STAGING_LAYER, -turns),
    ]

    return cost, " ".join(move for move in moves if move)


def displaced_line(size: int, row: int, evict: str) -> tuple[str, int]:
    """
    Returns the line of the receiving face that a transfer sends back to the giving one.

    :param size: The size of the cube
    :param row: The row of the side faces the transfer runs on
    :param evict: The turn of the receiving face between the slices, one of "", "'" and "2"
    :return: The displaced line, as its kind - "row" or "col" - and its index
    """

    return {"": ("col", row), "'": ("col", size - 1 - row), "2": ("row", size - 1 - row)}[evict]


def line_cells(size: int, line: tuple[str, int]) -> list[tuple[int, int]]:
    """
    Returns the center cells of one line of a face.

    :param size: The size of the cube
    :param line: The line to read, as its kind - "row" or "col" - and its index
    :return: The cells of the line
    """

    kind, index = line

    if kind == "col":
        return [(other, index) for other in range(1, size - 1)]

    return [(index, other) for other in range(1, size - 1)]


def line_pieces(cube: Cube, layer: Layer, color: Color, line: tuple[str, int]) -> int:
    """
    Returns how many center pieces of the color a line of a face holds.

    :param cube: The Cube instance to read
    :param layer: The face to read
    :param color: The color to count
    :param line: The line to read, as its kind - "row" or "col" - and its index
    :return: The amount of pieces of that color in the line
    """

    return sum(cell_color(cube, layer, row, col) == color for row, col in line_cells(cube.size, line))


def hop_evict(cube: Cube, receiver: Layer, color: Color, arrival: tuple[int, int]) -> str:
    """
    Returns the turn of a hop that hands the fewest pieces of the color back where they came from.

    A transfer takes a row and gives a line back, so a hop that returns a line full of the color
    being built puts a piece back on the face the last one was fetched off and gets nowhere. The
    line it gives back is written after the row arrives, so a turn whose line crosses the cell the
    piece being hopped lands on would send that very piece straight back, and is not offered.

    :param cube: The Cube instance to read
    :param receiver: The face the row is handed to
    :param color: The color of the center being built
    :param arrival: The cell of the receiving face the hopped piece lands on
    :return: The turn of the receiving face, one of "", "'" and "2"
    """

    turns = [
        evict
        for evict in CENTERS_QUARTER_TABLE.values()
        if arrival not in line_cells(cube.size, displaced_line(cube.size, arrival[0], evict))
    ]

    return min(
        turns, key=lambda evict: line_pieces(cube, receiver, color, displaced_line(cube.size, arrival[0], evict))
    )


def staging_hop(cube: Cube, color: Color, bar_col: int, result: CenterSearchResult) -> str:
    """
    Returns the algorithm moving a piece off the staging face and onto the source face.

    Every other face hands a piece straight to the bar, but the staging face cannot hand one to
    itself, so a piece already lying on it is put out to the source face and imported back from
    there. The transfer is turned a quarter first, so the row it overwrites is a column of the bar's
    face and the pieces already in the bar stay where they are.

    :param cube: The Cube instance to read
    :param color: The color of the center being built
    :param bar_col: The staging column the bar is assembled in
    :param result: The location of the piece on the staging face
    :return: The algorithm of the hop, or an empty string when the piece is in the bar's own column
    """

    size = cube.size

    if result.col == bar_col:
        return ""

    arrival = (result.col, size - 1 - result.row)
    evict = hop_evict(cube, CENTERS_SOURCE_LAYER, color, arrival)
    transfer = row_transfer(size, CENTERS_SOURCE_LAYER, result.col, "'", evict)

    return f"{turn_notation(CENTERS_STAGING_LAYER, 1)} {transfer} {turn_notation(CENTERS_STAGING_LAYER, 3)}"


def finished_kind(size: int, target: Layer, bar_col: int) -> str:
    """
    Returns which way the finished lines of the face being built run.

    An insertion fills a row of the RIGHT face and a column of the DOWN face. The middle line is
    filled after the face has been turned a quarter, though, so while that bar is assembled the
    finished lines lie the other way around.

    :param size: The size of the cube
    :param target: The face being built
    :param bar_col: The staging column the bar is assembled in
    :return: The kind of the finished lines, "row" or "col"
    """

    across = size % 2 and bar_col == size // 2

    if target is Layer.RIGHT:
        return "col" if across else "row"

    return "row" if across else "col"


def is_placed(cube: Cube, color: Color, target: Layer, result: CenterSearchResult, kind: str) -> bool:
    """
    Returns whether a piece is already part of a finished line of the face being built.

    Such a piece is not a piece the bar is short of - it is one of the pieces the bar has already
    delivered - so it is left where it is rather than fetched back out.

    :param cube: The Cube instance to read
    :param color: The color of the center being built
    :param target: The face being built
    :param result: The location of the piece
    :param kind: The kind of the finished lines, "row" or "col"
    :return: Whether the piece is already placed
    """

    if result.layer is not target:
        return False

    index = result.row if kind == "row" else result.col

    return line_pieces(cube, target, color, (kind, index)) == cube.size - 2


def bar_move(cube: Cube, color: Color, target: Layer, bar_col: int) -> str:
    """
    Returns the next algorithm bringing a center piece of the color into the bar.

    Three of the six faces hand a row straight to the staging face, so a piece on any of them goes
    into the bar in one algorithm and those are looked at first. A piece on the staging face itself
    is put out to the source face and imported back from there. Only when nothing else is left is
    one fetched off the face being built, and then the one whose extraction costs the bar the least.
    The cube is searched afresh every time, since the previous locations are stale as soon as an
    algorithm has run.

    :param cube: The Cube instance to read
    :param color: The color of the center being built
    :param target: The face being built
    :param bar_col: The staging column the bar is assembled in
    :return: The algorithm, or an empty string once the bar is complete
    """

    size = cube.size
    missing = [row for row in bar_rows(size, bar_col) if cell_color(cube, CENTERS_STAGING_LAYER, row, bar_col) != color]

    if not missing:
        return ""

    kind = finished_kind(size, target, bar_col)
    wanted = [
        (row, result)
        for row in missing
        for result in search_center(cube, color, row, bar_col)
        if not is_placed(cube, color, target, result, kind)
    ]
    wanted.sort(key=lambda entry: CENTERS_FETCH_RANK[entry[1].layer])

    for row, result in wanted:
        if result.layer in CENTERS_IMPORT_TABLE and result.layer is not target:
            return bar_import(size, row, bar_col, result)

        if result.layer is CENTERS_STAGING_LAYER:
            algorithm = staging_hop(cube, color, bar_col, result)

            if algorithm:
                return algorithm

    extractions = [
        target_extraction(cube, color, target, bar_col, result) for _, result in wanted if result.layer is target
    ]

    if not extractions:
        raise ValueError(f"No {color.name.lower()} center piece can be brought into the bar.")

    return min(extractions)[1]
