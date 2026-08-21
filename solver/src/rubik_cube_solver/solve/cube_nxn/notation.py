# Project imports
from rubik_cube_solver.enums.Layer import Layer

# The face on the other side of the cube, used to reach a layer that lies deeper than half the
# cube: turning it from the far side needs fewer layers than the move notation allows.
NOTATION_OPPOSITE_TABLE: dict[Layer, Layer] = {
    Layer.UP: Layer.DOWN,
    Layer.DOWN: Layer.UP,
    Layer.LEFT: Layer.RIGHT,
    Layer.RIGHT: Layer.LEFT,
    Layer.FRONT: Layer.BACK,
    Layer.BACK: Layer.FRONT,
}

# Whole-cube rotation that turns every layer the way the face itself turns.
NOTATION_ROTATION_TABLE: dict[Layer, str] = {
    Layer.UP: "y",
    Layer.DOWN: "y'",
    Layer.RIGHT: "x",
    Layer.LEFT: "x'",
    Layer.FRONT: "z",
    Layer.BACK: "z'",
}

# The direction that undoes a direction.
NOTATION_INVERSE_TABLE: dict[str, str] = {"": "'", "'": "", "2": "2"}


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

    rotation = NOTATION_ROTATION_TABLE[layer]

    if rotation.endswith("'"):
        return f"{rotation[0]}{NOTATION_INVERSE_TABLE[direction]}"

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

    far_side = wide_turn(NOTATION_OPPOSITE_TABLE[layer], size - depth, direction)

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

    inner = block_turn(size, layer, depth - 1, NOTATION_INVERSE_TABLE[direction])

    return f"{block_turn(size, layer, depth, direction)} {inner}".strip()


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


def column_slice(size: int, col: int, direction: str) -> str:
    """
    Returns the notation of the turn of the layer holding a column of the FRONT face.

    The layer is turned the way the RIGHT face turns, so it carries the FRONT column onto UP, the
    UP column onto BACK, the BACK column onto DOWN and the DOWN column onto FRONT. It never touches
    a center piece of LEFT or RIGHT.

    :param size: The size of the cube
    :param col: The column of the FRONT face
    :param direction: The direction of the turn, one of "", "'" and "2"
    :return: The notation of the turn
    """

    return layer_turn(size, Layer.RIGHT, size - col, direction)


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
