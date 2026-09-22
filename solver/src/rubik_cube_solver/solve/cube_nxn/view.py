# Project imports
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.orientation import Orientation
from rubik_cube_solver.enums.Layer import Layer

# The faces a viewer of the cube sees, so work happening on any other one is turned into view
VIEWED_LAYERS: tuple[Layer, ...] = (Layer.UP, Layer.FRONT, Layer.RIGHT)


def viewing_grip(target: Layer) -> Algorithm:
    """
    Returns the shortest whole-cube rotation that brings a face into view.

    A face already in view needs no turning. Any other one is brought to FRONT, which also keeps the
    face it displaces in view: LEFT comes forward with `y'`, sending FRONT to RIGHT, and DOWN with
    `x`, sending FRONT to UP.

    Example:

        >>> str(viewing_grip(Layer.RIGHT)), str(viewing_grip(Layer.LEFT)), str(viewing_grip(Layer.DOWN))
        ('', "y'", 'x')

    :param target: The face to bring into view
    :return: The rotation that brings the face into view, empty if it is already in view
    """

    if target in VIEWED_LAYERS:
        return Algorithm([])

    sequences = Orientation.shortest_sequences()
    facing = (moves for orientation, moves in sequences.items() if orientation.layers[Layer.FRONT] is target)

    return Algorithm(min(facing, key=len))


def held_in_view(moves: list[str], target: Layer) -> list[str]:
    """
    Returns algorithms with the cube held so the face they work on can be seen.

    The cube is turned so the target faces the viewer, every move is renamed to the face it is called
    by once the cube is turned, and the cube is turned back afterwards. The same pieces are turned in
    the same order, so the work and its result are exactly what they were; only the way the cube is
    held while it happens changes, the way a person turns the cube to see what they are doing.
    Removing the rotations gives the original algorithms straight back.

    Example, the white center's `Lw L'` fetch renamed to `Fw F'` and framed by the turn into view:

        >>> held_in_view(["Lw L'", "Dw R2 Dw' R2"], Layer.LEFT)
        ["y'", "Fw F'", "Dw B2 Dw' B2", 'y']

    :param moves: The algorithms to perform
    :param target: The face the work is done on
    :return: The algorithms with the cube held so the work can be seen
    """

    grip = viewing_grip(target)
    if not grip.moves:
        return moves

    held = [Algorithm.from_str(algorithm) for algorithm in moves]
    for algorithm in held:
        algorithm.rename(grip)

    return [str(grip)] + [str(algorithm) for algorithm in held] + [str(grip.inverse())]
