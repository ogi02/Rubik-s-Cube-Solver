# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.center_search import search_center

# Whole-cube rotation, keyed by the face whose fixed center carries the color being built, that
# brings that face to UP. Only an odd cube has fixed centers, so only an odd cube needs orienting:
# on an even cube no face carries a color yet and the center is built on whichever face is UP.
FIRST_CENTERS_ORIENTATION_TABLE: dict[Layer, str] = {
    Layer.UP: "",
    Layer.DOWN: "x2",
    Layer.FRONT: "x",
    Layer.BACK: "x'",
    Layer.LEFT: "z",
    Layer.RIGHT: "z'",
}

# The three faces a center piece can be fetched from. FRONT is the staging face and is therefore
# not a source: a piece already on it is pushed onto a side face first.
FIRST_CENTERS_SOURCE_LAYERS: tuple[Layer, ...] = (Layer.LEFT, Layer.RIGHT, Layer.BACK)

# Direction of the row slice that brings a source face's row onto the FRONT face.
FIRST_CENTERS_TO_FRONT_TABLE: dict[Layer, str] = {
    Layer.RIGHT: "",
    Layer.LEFT: "'",
    Layer.BACK: "2",
}

# Direction of the row slice that pushes a source face's row onto a different side face, used to
# split two pieces that share a face so they can be lined up one at a time.
FIRST_CENTERS_PUSH_TABLE: dict[Layer, str] = {
    Layer.LEFT: "",
    Layer.RIGHT: "'",
    Layer.BACK: "",
}

# The face turn of every face a piece is repositioned on. Turning a face permutes its own center
# pieces and nothing else, so it is always safe for the face being built.
FIRST_CENTERS_FACE_TURN_TABLE: dict[Layer, str] = {
    Layer.LEFT: "L",
    Layer.RIGHT: "R",
    Layer.BACK: "B",
    Layer.FRONT: "F",
}

# The face on the other side of the cube, used to reach a layer that lies deeper than half the
# cube: turning it from the far side needs fewer layers than the move notation allows.
FIRST_CENTERS_OPPOSITE_TABLE: dict[Layer, Layer] = {
    Layer.UP: Layer.DOWN,
    Layer.DOWN: Layer.UP,
    Layer.LEFT: Layer.RIGHT,
    Layer.RIGHT: Layer.LEFT,
    Layer.FRONT: Layer.BACK,
    Layer.BACK: Layer.FRONT,
}

# Whole-cube rotation that turns every layer the way the face itself turns.
FIRST_CENTERS_ROTATION_TABLE: dict[Layer, str] = {
    Layer.UP: "y",
    Layer.DOWN: "y'",
    Layer.RIGHT: "x",
    Layer.LEFT: "x'",
}

# The direction that undoes a direction.
FIRST_CENTERS_INVERSE_TABLE: dict[str, str] = {"": "'", "'": "", "2": "2"}


def wide_turn(layer: Layer, depth: int, direction: str) -> str:
    """
    Returns the notation of a turn of the `depth` layers closest to a face.

    :param layer: The face to turn
    :param depth: The amount of layers to turn, from 1 up to half the cube
    :param direction: The direction of the turn, one of "", "'" and "2"
    :return: The notation of the turn
    """

    match depth:
        case 1:
            return f"{layer.value}{direction}"
        case 2:
            return f"{layer.value}w{direction}"
        case _:
            return f"{depth}{layer.value}w{direction}"


def rotation_turn(layer: Layer, direction: str) -> str:
    """
    Returns the notation of the whole-cube rotation that turns every layer the way `layer` turns.

    :param layer: The face whose direction the rotation follows
    :param direction: The direction of the turn, one of "", "'" and "2"
    :return: The notation of the rotation
    """

    rotation = FIRST_CENTERS_ROTATION_TABLE[layer]

    if rotation.endswith("'"):
        return f"{rotation[0]}{FIRST_CENTERS_INVERSE_TABLE[direction]}"

    return f"{rotation}{direction}"


def block_turn(size: int, layer: Layer, depth: int, direction: str) -> str:
    """
    Returns the notation of a turn of the `depth` layers closest to a face, at any depth.

    A move may name at most half of the cube's layers, so a deeper block is written as a whole-cube
    rotation with the layers on the far side turned back.

    :param size: The size of the cube
    :param layer: The face to turn
    :param depth: The amount of layers to turn, from 0 (nothing) up to the whole cube
    :param direction: The direction of the turn, one of "", "'" and "2"
    :return: The notation of the turn
    """

    if depth <= 0:
        return ""

    if depth <= size // 2:
        return wide_turn(layer, depth, direction)

    if depth >= size:
        return rotation_turn(layer, direction)

    far_side = wide_turn(FIRST_CENTERS_OPPOSITE_TABLE[layer], size - depth, direction)

    return f"{rotation_turn(layer, direction)} {far_side}"


def layer_turn(size: int, layer: Layer, depth: int, direction: str) -> str:
    """
    Returns the notation of a turn of the single layer at `depth`, counted from a face.

    The layer is turned by turning the block that ends at it and turning the block in front of it
    back. The two blocks share an axis, so they commute and the order they are written in does not
    matter.

    :param size: The size of the cube
    :param layer: The face the depth is counted from
    :param depth: The depth of the layer, 1 being the face itself and `size` the opposite face
    :param direction: The direction of the turn, one of "", "'" and "2"
    :return: The notation of the turn
    """

    inner = block_turn(size, layer, depth - 1, FIRST_CENTERS_INVERSE_TABLE[direction])

    return f"{block_turn(size, layer, depth, direction)} {inner}".strip()


def column_slice(size: int, col: int, direction: str) -> str:
    """
    Returns the notation of the turn of the layer holding a column of the FRONT face.

    The layer is turned the way the RIGHT face turns, so it carries the FRONT column onto UP, the
    UP column onto BACK, the BACK column onto DOWN and the DOWN column onto FRONT.

    :param size: The size of the cube
    :param col: The column of the FRONT face
    :param direction: The direction of the turn, one of "", "'" and "2"
    :return: The notation of the turn
    """

    return layer_turn(size, Layer.RIGHT, size - col, direction)


def row_slice(size: int, row: int, direction: str) -> str:
    """
    Returns the notation of the turn of the layer holding a row of the side faces.

    The layer is turned the way the UP face turns, so it carries the FRONT row onto LEFT, the LEFT
    row onto BACK, the BACK row onto RIGHT and the RIGHT row onto FRONT, each at the same row and
    column. It never touches a center piece of UP or DOWN.

    :param size: The size of the cube
    :param row: The row of the side faces
    :param direction: The direction of the turn, one of "", "'" and "2"
    :return: The notation of the turn
    """

    return layer_turn(size, Layer.UP, row + 1, direction)


def center_positions(size: int, row: int, col: int) -> list[tuple[int, int]]:
    """
    Returns the four cells of the position type of a cell, in the order a face turn cycles them.

    The order is what makes the number of face turns between two cells readable: the piece at the
    cell of index `i` is at the cell of index `i + 1` after one clockwise turn of its face.

    :param size: The size of the cube
    :param row: The row of the cell
    :param col: The column of the cell
    :return: The four cells of the position type, in clockwise order
    """

    cells = [(row, col)]

    for _ in range(3):
        row, col = col, size - 1 - row
        cells.append((row, col))

    return cells


def center_cells(size: int) -> list[tuple[int, int]]:
    """
    Returns every cell of a face that holds a center piece.

    The fixed center of an odd cube is not one of them: it never leaves its face.

    :param size: The size of the cube
    :return: The cells of a face that hold a center piece
    """

    middle = size // 2

    return [
        (row, col)
        for row in range(1, size - 1)
        for col in range(1, size - 1)
        if not (size % 2 and row == middle and col == middle)
    ]


def center_color(cube: Cube, layer: Layer, row: int, col: int) -> Color:
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


def staging_rows(size: int, col: int) -> list[int]:
    """
    Returns the rows of the FRONT column a line is staged in.

    The fixed center of an odd cube is skipped, since it cannot be staged and is already the color
    of the face it belongs to.

    :param size: The size of the cube
    :param col: The staging column
    :return: The rows a piece is staged in
    """

    middle = size // 2

    return [row for row in range(1, size - 1) if not (size % 2 and row == middle and col == middle)]


def fill_schedule(size: int) -> list[tuple[int, str, str]]:
    """
    Returns the staging column, U turn and follow-up rotation of every line the face is built from.

    An insertion parks the staging column and moves everything else on the face by its U turn, so a
    `U2` insertion fills the partner column of the staging column and can only overwrite that one.
    The columns are therefore built in pairs that map onto each other, each filled from the other.

    An odd cube has a middle column that is its own partner, so a `U2` insertion there would eject
    exactly what it inserted. It is filled first instead, with a `U` insertion that lays the pieces
    into the middle row and a `y` rotation that turns the row into the column, both of which happen
    while the rest of the face is still unsolved.

    :param size: The size of the cube
    :return: The staging column, U turn direction and follow-up rotation of every line
    """

    schedule = []

    if size % 2:
        schedule.append((size // 2, "", "y"))

    for first in range(1, (size - 1) // 2 + 1):
        second = size - 1 - first
        if first >= second:
            break
        schedule.append((first, "2", ""))
        schedule.append((second, "2", ""))

    return schedule


def line_insertion(size: int, col: int, turn: str) -> str:
    """
    Returns the algorithm inserting the staged FRONT column into the face being built.

    The first slice carries the staged column onto UP and parks the column it lands on behind it on
    BACK, the U turn moves the staged pieces off that column, and the second slice brings the parked
    column back. The DOWN column the first slice pulls onto FRONT is returned by the second one, so
    every center piece of the DOWN face ends where it started and the center built on it survives.
    Only the DOWN layer's edge piece in that column, which the U turn reaches while it waits on the
    FRONT face, is left somewhere else - the edges are not solved yet at this point.

    :param size: The size of the cube
    :param col: The staging column
    :param turn: The direction of the U turn between the slices, one of "", "'" and "2"
    :return: The algorithm of the insertion
    """

    forward = column_slice(size, col, "")
    backward = column_slice(size, col, "'")

    return f"{forward} U{turn} {backward}"


def down_extraction(cube: Cube, color: Color) -> str:
    """
    Returns the algorithm taking one center piece of `color` off the DOWN face.

    Only a slice that moves the DOWN face can empty it, and every such slice moves the UP face as
    well, so the pieces are taken off before anything is built. The piece is carried onto FRONT, a
    row slice moves it on to LEFT, and the second column slice returns the rest of the DOWN column,
    which is why the face loses exactly one piece per algorithm. The RIGHT face is turned first so
    that the sticker the row slice leaves behind on FRONT, and with it on DOWN, is not of `color`.

    :param cube: The Cube instance to read
    :param color: The color of the center being built
    :return: The algorithm, or an empty string when the DOWN face holds no piece of that color
    """

    size = cube.size
    cells = [cell for cell in center_cells(size) if center_color(cube, Layer.DOWN, *cell) == color]

    if not cells:
        return ""

    row, col = cells[0]
    positions = center_positions(size, row, col)
    turns = next(turn for turn in range(4) if center_color(cube, Layer.RIGHT, *positions[-turn]) != color)
    moves = ["R"] * turns

    moves.append(column_slice(size, col, ""))
    moves.append(row_slice(size, row, ""))
    moves.append(column_slice(size, col, "'"))

    return " ".join(moves)


def front_column_clearing(cube: Cube, color: Color, col: int) -> str:
    """
    Returns the algorithm moving one piece of `color` out of a column of the FRONT face.

    The row slice hands the cell over to the RIGHT face, so the RIGHT face is turned first until the
    sticker it hands over is of another color and the column is one piece emptier than before.

    :param cube: The Cube instance to read
    :param color: The color of the center being built
    :param col: The column to clear
    :return: The algorithm, or an empty string when the column holds no piece of that color
    """

    size = cube.size
    rows = [row for row in staging_rows(size, col) if center_color(cube, Layer.FRONT, row, col) == color]

    if not rows:
        return ""

    row = rows[0]
    positions = center_positions(size, row, col)
    turns = next(turn for turn in range(4) if center_color(cube, Layer.RIGHT, *positions[-turn]) != color)

    return " ".join(["R"] * turns + [row_slice(size, row, "")])


def up_eviction(cube: Cube, color: Color) -> str:
    """
    Returns the next algorithm taking a center piece of `color` off the UP face.

    A line is staged and inserted in one go, so a piece of the color already lying on the face would
    be a piece the staging cannot reach. The face is therefore emptied first, by inserting a staging
    column cleared of that color into the line the piece sits on.

    :param cube: The Cube instance to read
    :param color: The color of the center being built
    :return: The algorithm, or an empty string when the UP face holds no piece of that color
    """

    size = cube.size
    cells = [cell for cell in center_cells(size) if center_color(cube, Layer.UP, *cell) == color]

    if not cells:
        return ""

    row, col = cells[0]

    # A `U2` insertion ejects the partner column of the staging column, which is the middle column
    # itself on an odd cube - a column that insertion cannot empty. A `U` insertion ejects a row.
    if size % 2 and col == size // 2:
        staging_col, turn = size - 1 - row, ""
    else:
        staging_col, turn = size - 1 - col, "2"

    clearing = front_column_clearing(cube, color, staging_col)

    return clearing or line_insertion(size, staging_col, turn)


def wanted_pieces(
    cube: Cube, color: Color, col: int, missing: list[int], source: Layer
) -> list[tuple[int, tuple[int, int]]]:
    """
    Returns the pieces on a source face the staging cells of a line are waiting for.

    :param cube: The Cube instance to search
    :param color: The color of the center being built
    :param col: The staging column
    :param missing: The rows of the staging column that hold no piece of that color yet
    :param source: The face to look at
    :return: The row each piece is wanted in, together with the cell the piece lies on
    """

    return [
        (row, (result.row, result.col))
        for row in missing
        for result in search_center(cube, color, row, col)
        if result.layer is source
    ]


def alignment(
    cube: Cube, color: Color, col: int, missing: list[int], source: Layer, turns: int
) -> tuple[list[int], list[tuple[int, int]]]:
    """
    Returns what turning a source face by `turns` would achieve for the staging column.

    A piece is lined up when the turn leaves it on the cell of the staging column it is wanted in,
    since the row slice that fetches it then carries it straight onto that cell. That slice carries
    the whole row of the source face with it, so a piece the turn leaves in a row that is about to
    be fetched is dragged onto a cell of FRONT the staging cannot reach again.

    :param cube: The Cube instance to search
    :param color: The color of the center being built
    :param col: The staging column
    :param missing: The rows of the staging column that hold no piece of that color yet
    :param source: The face to turn
    :param turns: The amount of clockwise turns of that face
    :return: The rows the turn lines up, and the cells of the pieces it would drag along
    """

    size = cube.size
    pieces = wanted_pieces(cube, color, col, missing, source)
    aligned: dict[int, tuple[int, int]] = {}

    for row, cell in pieces:
        if center_positions(size, *cell)[turns] == (row, col) and cell not in aligned.values():
            aligned.setdefault(row, cell)

    dragged = {
        cell
        for _, cell in pieces
        if cell not in aligned.values() and center_positions(size, *cell)[turns][0] in aligned
    }

    return list(aligned), sorted(dragged)


def relocation(cube: Cube, col: int, source: Layer, cell: tuple[int, int], others: list[tuple[int, int]]) -> str:
    """
    Returns the algorithm pushing a piece onto another side face, leaving the staging column intact.

    Two pieces the same line is waiting for can share a row of a face, and then no turn lines up one
    without dragging the other. Pushing one of them onto another face separates them, but the row
    slice that does it would take the staged cell of that row with it. The slice is therefore
    conjugated by a turn of the FRONT face, which lays the staged pieces in a row of their own and
    leaves every other row free to move, and the face is turned first so the pushed piece is neither
    in that row nor in a row shared with a piece staying behind.

    :param cube: The Cube instance to read
    :param col: The staging column
    :param source: The face the piece lies on
    :param cell: The cell of the piece to push away
    :param others: The cells of the pieces that stay behind
    :return: The algorithm of the relocation
    """

    size = cube.size
    positions = center_positions(size, *cell)
    free = [
        turn
        for turn in range(4)
        if positions[turn][0] != col
        and all(center_positions(size, *other)[turn][0] != positions[turn][0] for other in others)
    ]
    turns = free[0] if free else next(turn for turn in range(4) if positions[turn][0] != col)

    moves = ["F"] + [FIRST_CENTERS_FACE_TURN_TABLE[source]] * turns
    moves.append(row_slice(size, positions[turns][0], FIRST_CENTERS_PUSH_TABLE[source]))
    moves.append("F'")

    return " ".join(moves)


def front_release(cube: Cube, color: Color, col: int, missing: list[int]) -> str:
    """
    Returns the algorithm pushing a wanted piece off the FRONT face and onto the LEFT face.

    Only a source face can be turned to line a piece up with the cell it is wanted in, so a piece
    that ends up on the staging face has to leave it first. A piece in a row that is still waiting
    for its own piece is pushed off by a plain row slice; one in a row that is already staged would
    take that staged piece with it, so the slice is conjugated by a turn of the FRONT face, which
    lays the staged pieces in a row the slice does not touch.

    :param cube: The Cube instance to search
    :param color: The color of the center being built
    :param col: The staging column
    :param missing: The rows of the staging column that hold no piece of that color yet
    :return: The algorithm, or an empty string when no wanted piece lies on the FRONT face
    """

    size = cube.size

    for row in missing:
        for result in search_center(cube, color, row, col):
            if result.layer is not Layer.FRONT or (result.col == col and result.row not in missing):
                continue

            if result.row in missing:
                return row_slice(size, result.row, "")

            return f"F {row_slice(size, result.col, '')} F'"

    return ""


def staging_move(cube: Cube, color: Color, col: int) -> str:
    """
    Returns the next algorithm bringing a center piece of `color` into the staging column.

    Every face turn of a source face is tried, and the one that lines up the most pieces without
    dragging others out of reach is fetched with a row slice per lined up piece. When the best turn
    would lose more than it gains, a piece is pushed onto another face or off the FRONT face first,
    so the next turn has a piece it can line up on its own.

    :param cube: The Cube instance to read
    :param color: The color of the center being built
    :param col: The staging column
    :return: The algorithm, or an empty string once the whole column is staged
    """

    size = cube.size
    missing = [row for row in staging_rows(size, col) if center_color(cube, Layer.FRONT, row, col) != color]

    if not missing:
        return ""

    best: tuple[int, list[int], list[tuple[int, int]], Layer, int] | None = None
    for source in FIRST_CENTERS_SOURCE_LAYERS:
        for turns in range(4):
            aligned, dragged = alignment(cube, color, col, missing, source, turns)
            if aligned and (best is None or len(aligned) - len(dragged) > best[0]):
                best = (len(aligned) - len(dragged), aligned, dragged, source, turns)

    if best is None:
        return front_release(cube, color, col, missing)

    score, aligned, dragged, source, turns = best

    if score <= 0:
        others = [cell for _, cell in wanted_pieces(cube, color, col, missing, source) if cell != dragged[0]]
        return relocation(cube, col, source, dragged[0], sorted(set(others)))

    moves = [FIRST_CENTERS_FACE_TURN_TABLE[source]] * turns
    moves.extend(row_slice(size, row, FIRST_CENTERS_TO_FRONT_TABLE[source]) for row in aligned)

    return " ".join(moves)
