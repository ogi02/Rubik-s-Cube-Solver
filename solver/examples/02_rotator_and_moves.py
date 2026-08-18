"""
Turning the cube with a `Rotator` and a `Move`.

`Rotator` is the only class that mutates a `Cube`. A `Move` describes one turn - which layer, in
which direction, and how many layers deep - or one whole-cube rotation. This example builds moves
both from their parts and from standard notation, turns single and wide layers, and reorients the
whole cube.

Run it with:

    python examples/02_rotator_and_moves.py
"""

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation


def turn_a_single_layer() -> None:
    """
    Turns one layer of a 3x3 cube.

    A `Rotator` holds the cube it turns, so `turn` mutates the cube that was passed to the
    constructor rather than returning a new one.

    :return: None
    """

    cube = Cube(size=3)
    rotator = Rotator(cube)

    # U - the UP layer, one layer deep, clockwise
    rotator.turn(Move(layer=Layer.UP, direction=Direction.CW, layer_amount=1))
    print("After U:")
    print(cube)

    # R' - the RIGHT layer, counter-clockwise
    rotator.turn(Move(layer=Layer.RIGHT, direction=Direction.CCW, layer_amount=1))
    print("After U R':")
    print(cube)


def build_moves_from_notation() -> None:
    """
    Parses moves from standard notation and prints them back.

    `Move.from_str` and `Move.__str__` are strict inverses, so notation never has to be assembled by
    hand. A numeric prefix requires the `w` and must be at least 2, so `R`, `Rw'` and `3Lw2` parse
    while `3R` and `1Rw` raise a `ValueError`.

    :return: None
    """

    for notation in ("R", "U'", "F2", "Rw'", "3Lw2", "y", "x2"):
        move = Move.from_str(notation)
        print(f"{notation:>5}  ->  layer={move.layer.name:<6} direction={move.direction.name:<6} " f"str={str(move)!r}")

    try:
        Move.from_str("3R")
    except ValueError as error:
        print(f"Invalid notation is rejected: {error}")


def turn_a_wide_layer() -> None:
    """
    Turns more than one layer at once on a 5x5 cube.

    `layer_amount` is how deep the turn reaches. A wide turn may name at most half of the cube's
    layers, so `Rw` is legal on a 5x5 while `3Rw` is not - no move can reach the middle layer or
    past it. A deeper block is written from the far side instead, as a whole-cube rotation with the
    layers on the other side turned back.

    :return: None
    """

    cube = Cube(size=5)
    rotator = Rotator(cube)

    # Rw - the two layers on the RIGHT side, clockwise
    rotator.turn(Move(layer=Layer.RIGHT, direction=Direction.CW, layer_amount=2))
    print("A 5x5 after Rw:")
    print(cube)

    try:
        rotator.turn(Move(layer=Layer.RIGHT, direction=Direction.CW, layer_amount=3))
    except ValueError as error:
        print(f"A turn deeper than half the cube is rejected: {error}")


def rotate_the_whole_cube() -> None:
    """
    Reorients the whole cube without changing which pieces sit next to which.

    A whole-cube rotation only relabels which face is UP, FRONT and so on - `y` turns the cube about
    the vertical axis. It can be applied through `rotate` or, since it is also a `Move`, through
    `turn`.

    :return: None
    """

    cube = Cube(size=3)
    rotator = Rotator(cube)

    rotator.rotate(Rotation.Y, Direction.CW)
    print("After a y rotation - GREEN has moved off the FRONT face:")
    print(cube)

    # The same rotation expressed as a move
    rotator.turn(Move.from_str("y'"))
    print("After y', back to the starting orientation:")
    print(cube)


def main() -> None:
    """
    Runs every part of the example.

    :return: None
    """

    turn_a_single_layer()
    build_moves_from_notation()
    print()
    turn_a_wide_layer()
    rotate_the_whole_cube()


if __name__ == "__main__":
    main()
