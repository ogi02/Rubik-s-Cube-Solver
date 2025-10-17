from collections import defaultdict

from src.solver.cube import Cube
from src.solver.enums.Color import Color
from src.solver.enums.Direction import Direction
from src.solver.enums.EdgePosition import EdgePosition
from src.solver.enums.Layer import Layer


# Maps for adjacent faces for each face rotation and the edge location
ADJACENT_FACES = {
    Layer.UP:    [(Layer.BACK,  EdgePosition.TOP),    (Layer.RIGHT, EdgePosition.TOP),
                  (Layer.FRONT, EdgePosition.TOP),    (Layer.LEFT,  EdgePosition.TOP)],
    Layer.DOWN:  [(Layer.FRONT, EdgePosition.BOTTOM), (Layer.RIGHT, EdgePosition.BOTTOM),
                  (Layer.BACK,  EdgePosition.BOTTOM), (Layer.LEFT,  EdgePosition.BOTTOM)],
    Layer.FRONT: [(Layer.UP,    EdgePosition.BOTTOM), (Layer.RIGHT, EdgePosition.LEFT),
                  (Layer.DOWN,  EdgePosition.TOP),    (Layer.LEFT,  EdgePosition.RIGHT)],
    Layer.BACK:  [(Layer.UP,    EdgePosition.TOP),    (Layer.LEFT,  EdgePosition.LEFT),
                  (Layer.DOWN,  EdgePosition.BOTTOM), (Layer.RIGHT, EdgePosition.RIGHT)],
    Layer.LEFT:  [(Layer.UP,    EdgePosition.LEFT),   (Layer.FRONT, EdgePosition.LEFT),
                  (Layer.DOWN,  EdgePosition.LEFT),   (Layer.BACK,  EdgePosition.RIGHT)],
    Layer.RIGHT: [(Layer.UP,    EdgePosition.RIGHT),  (Layer.BACK,  EdgePosition.LEFT),
                  (Layer.DOWN,  EdgePosition.RIGHT),  (Layer.FRONT, EdgePosition.RIGHT)]
}


def get_edge(face: list[Color], layer_amount: int, position: EdgePosition, cube_size: int) -> list[Color]:
    """
    Extracts an edge as a list based on position and which layer it needs to fetch.

    For position "top" we take the first "n" stickers where "n" is the size of the cube.
    For position "bottom" we take the last "n" stickers where "n" is the size of the cube.
    For position "left" we take every "n"th stickers, starting from 0 where "n" is the size of the cube.
    For position "right" we take every "n"th stickers, starting from "n" - 1 where "n" is the size of the cube.

    :param face: The face of the cube
    :param layer_amount: The amount of layers
    :param position: The position of the face
    :param cube_size: The size of the cube
    :return: The list of colors on the specified adjacent face
    """

    if layer_amount <= 0:
        raise ValueError(f"Invalid layer amount: {layer_amount}")
    if cube_size <= 0:
        raise ValueError(f"Invalid cube size: {cube_size}")

    if position == EdgePosition.TOP:
        return face[cube_size * (layer_amount - 1) : cube_size * layer_amount]
    elif position == EdgePosition.BOTTOM:
        return face[cube_size * (cube_size - layer_amount) : cube_size * (cube_size - layer_amount + 1)]
    elif position == EdgePosition.LEFT:
        return [face[i * cube_size + layer_amount - 1] for i in range(cube_size)]
    elif position == EdgePosition.RIGHT:
        return [face[i * cube_size + cube_size - layer_amount] for i in range(cube_size)]
    else:
        raise ValueError(f"Unknown edge position: {position}")


def set_edge(face: list[Color], layer_amount: int, position: EdgePosition, cube_size: int, values: list[Color]) -> None:
    """
    Writes an edge back into the face.

    For position "top" we write the first "n" stickers where "n" is the size of the cube.
    For position "bottom" we write the last "n" stickers where "n" is the size of the cube.
    For position "left" we write every "n"th stickers, starting from 0 where "n" is the size of the cube.
    For position "right" we write every "n"th stickers, starting from "n" - 1 where "n" is the size of the cube.

    :param face: The face of the cube
    :param layer_amount: The amount of layers
    :param position: The position of the face
    :param cube_size: The size of the cube
    :param values: The new values for the edge
    :return: None
    """

    if layer_amount <= 0:
        raise ValueError(f"Invalid layer amount: {layer_amount}")
    if cube_size <= 0:
        raise ValueError(f"Invalid cube size: {cube_size}")

    if position == EdgePosition.TOP:
        face[cube_size * (layer_amount - 1) : cube_size * layer_amount] = values
    elif position == EdgePosition.BOTTOM:
        face[cube_size * (cube_size - layer_amount) : cube_size * (cube_size - layer_amount + 1)] = values
    elif position == EdgePosition.LEFT:
        for i in range(cube_size):
            face[i * cube_size + layer_amount - 1] = values[i]
    elif position == EdgePosition.RIGHT:
        for i in range(cube_size):
            face[i * cube_size + cube_size - layer_amount] = values[i]
    else:
        raise ValueError(f"Unknown edge position: {position}")


def should_flip_edge(turned_layer: Layer, direction: Direction, adj_layer: Layer) -> bool:
    """
    Checks if an edge should be flipped before assigning it to the cube.
    Due to the 2D representation of the cube, 'F', 'B', 'L', and 'R' moves require some edge flips of the side stickers.
    The check is performed to the target adjacent face.

    :param turned_layer: The layer which is being turned
    :param direction: The direction of the turn
    :param adj_layer: The target adjacent layer of the turned layer
    :return: True if the edge should be flipped, False otherwise
    """

    # Combinations of (turned layer, direction, [origin adjacent face])
    # that require edge flip because of the 2D representation
    combinations = defaultdict(list, {
        # FRONT face
        (Layer.FRONT, Direction.CW):     [Layer.UP,    Layer.DOWN],
        (Layer.FRONT, Direction.CCW):    [Layer.LEFT,  Layer.RIGHT],
        (Layer.FRONT, Direction.DOUBLE): [Layer.UP,    Layer.DOWN, Layer.LEFT, Layer.RIGHT],
        # BACK face
        (Layer.BACK,  Direction.CW):     [Layer.LEFT,  Layer.RIGHT],
        (Layer.BACK,  Direction.CCW):    [Layer.UP,    Layer.DOWN],
        (Layer.BACK,  Direction.DOUBLE): [Layer.UP,    Layer.DOWN, Layer.LEFT, Layer.RIGHT],
        # LEFT face
        (Layer.LEFT,  Direction.CW):     [Layer.UP,    Layer.BACK],
        (Layer.LEFT,  Direction.CCW):    [Layer.BACK,  Layer.DOWN],
        (Layer.LEFT,  Direction.DOUBLE): [Layer.FRONT, Layer.BACK],
        # RIGHT face
        (Layer.RIGHT, Direction.CW):     [Layer.BACK,  Layer.DOWN],
        (Layer.RIGHT, Direction.CCW):    [Layer.UP,    Layer.BACK],
        (Layer.RIGHT, Direction.DOUBLE): [Layer.FRONT, Layer.BACK],
    })
    # Check which layers for the specific combination require flip
    layers_to_flip = combinations.get((turned_layer, direction), [])

    return adj_layer in layers_to_flip


def rotate_sides(cube: Cube, layer: Layer, direction: Direction, layer_amount: int) -> None:
    """
    Rotates the edges of the adjacent faces

    :param cube: The cube
    :param layer: The layer of the cube
    :param direction: The direction of the rotation
    :param layer_amount: The amount of layers
    :return: None
    """
    # Get the adjacent faces of the layer which is being rotated
    adj = ADJACENT_FACES[layer]

    # Check if not too many layers are being turned
    if cube.size // layer_amount < 2:
        raise ValueError(f"Cube size {cube.size} is too small to rotate {layer_amount} layers")
    if layer_amount <= 0:
        raise ValueError(f"Invalid layer amount: {layer_amount}")

    # Iterate all layers
    for layer_index in range(1, layer_amount + 1):
        # Extract the edges connected to the face which is being rotated
        edges = [get_edge(cube.layers[f], layer_index, pos, cube.size) for f, pos in adj]

        # Determine rotation order
        if direction == Direction.CW:
            # Clockwise -> last edge becomes first, the rest move 1 forwards
            rotated_edges = [edges[-1]] + edges[:-1]
        elif direction == Direction.CCW:
            # Counter-clockwise -> first edge becomes last, the rest move 1 backward
            rotated_edges = edges[1:] + [edges[0]]
        elif direction == Direction.DOUBLE:
            # Double -> all edges move 2 in any direction (as it is a cube)
            rotated_edges = edges[2:] + edges[:2]
        else:
            raise ValueError("Invalid rotation direction")

        # Write back rotated edges
        for (f, pos), edge in zip(adj, rotated_edges):
            # Some edges need to be reversed to match orientation
            if should_flip_edge(layer, direction, f):
                edge = edge[::-1]
            set_edge(cube.layers[f], layer_index, pos, cube.size, edge)
