"""
Building and applying algorithms.

An `Algorithm` is an ordered list of `Move` objects. It is the unit a whole sequence of turns is
passed around in - `Rotator.apply` runs one, `Algorithm.from_str` parses one from notation, and
`str` writes one back out. This example applies the sexy move, shows that six repetitions of it
restore a solved cube, and builds an algorithm from `Move` objects instead of a string.

Run it with:

    python examples/03_algorithms.py
"""

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer

# The "sexy move" - the most repeated trigger in human solving methods
SEXY_MOVE = "R U R' U'"


def apply_an_algorithm() -> None:
    """
    Parses an algorithm from notation and runs it on a 3x3 cube.

    :return: None
    """

    cube = Cube(size=3)
    rotator = Rotator(cube)

    algorithm = Algorithm.from_str(SEXY_MOVE)
    print(f"Applying {algorithm} ({len(algorithm.moves)} moves):")

    rotator.apply(algorithm)
    print(cube)


def notation_round_trips() -> None:
    """
    Shows that parsing and printing an algorithm are inverses.

    `from_str` splits on any whitespace and maps the empty string to an empty algorithm, so `str`
    always returns the canonical spelling of the same sequence.

    :return: None
    """

    for notation in ("R U R' U'", "  F2   B'  ", "x R U R' U'", ""):
        algorithm = Algorithm.from_str(notation)
        print(f"{notation!r:>16}  ->  {str(algorithm)!r}")


def repeat_until_solved() -> None:
    """
    Applies the sexy move six times, which returns a solved cube to the solved state.

    Every algorithm has an order - a number of repetitions after which the cube is back where it
    started. For `R U R' U'` that number is 6.

    :return: None
    """

    cube = Cube(size=3)
    rotator = Rotator(cube)
    solved = Cube(size=3)

    algorithm = Algorithm.from_str(SEXY_MOVE)
    for repetition in range(1, 7):
        rotator.apply(algorithm)
        is_solved = cube.layers == solved.layers
        print(f"After {repetition} x ({algorithm}): solved = {is_solved}")


def build_an_algorithm_from_moves() -> None:
    """
    Builds an algorithm out of `Move` objects rather than parsing a string.

    This is the form solving code uses, where the moves are computed rather than written down.

    :return: None
    """

    algorithm = Algorithm(
        [
            Move(layer=Layer.RIGHT, direction=Direction.CW, layer_amount=1),
            Move(layer=Layer.UP, direction=Direction.CW, layer_amount=1),
            Move(layer=Layer.RIGHT, direction=Direction.CCW, layer_amount=1),
            Move(layer=Layer.UP, direction=Direction.CCW, layer_amount=1),
        ]
    )

    print(f"Built from Move objects: {algorithm}")
    print(f"Equal to the parsed one:  {algorithm == Algorithm.from_str(SEXY_MOVE)}")


def main() -> None:
    """
    Runs every part of the example.

    :return: None
    """

    apply_an_algorithm()
    notation_round_trips()
    print()
    repeat_until_solved()
    print()
    build_an_algorithm_from_moves()


if __name__ == "__main__":
    main()
