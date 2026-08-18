"""
Validating a cube state.

`Validator.validate` raises a `ValueError` on the first invariant a cube violates, and returns
`None` when the state is reachable by turning a real cube. It is what protects the solvers from
being handed an impossible state - a scan that misread a sticker, or a cube that was taken apart and
reassembled wrongly.

This example validates a solved and a scrambled cube, then walks through three kinds of broken
state: a miscounted color, a single twisted corner, and a single swapped pair of edges.

Run it with:

    python examples/05_validating.py
"""

# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.validator.validator import Validator

# A fixed scramble, so that the output of this example is the same on every run
SCRAMBLE = "D2 F2 D B' L2 B R F U L2 B2 F' L' D2 L2 F' R2 L' B' R2"


def report(description: str, cube: Cube) -> None:
    """
    Validates a cube and prints either a confirmation or the error it raised.

    :param description: What the cube is, for the printed line
    :param cube: The cube to validate
    :return: None
    """

    try:
        Validator().validate(cube)
        print(f"{description}: valid")
    except ValueError as error:
        print(f"{description}: {error}")


def validate_reachable_states() -> None:
    """
    Validates a solved cube and a scrambled one. Both are reachable, so neither raises.

    :return: None
    """

    report("Solved 3x3", Cube(size=3))

    cube = Cube(size=3)
    Rotator(cube).apply(Algorithm.from_str(SCRAMBLE))
    report("Scrambled 3x3", cube)


def validate_a_miscounted_color() -> None:
    """
    Recolors two UP stickers, leaving the cube with seven WHITE and eleven RED stickers.

    This is the cheapest invariant to violate and the first one the validator checks after the size.

    :return: None
    """

    cube = Cube(size=3)
    cube.layers[Layer.UP][0] = Color.RED
    cube.layers[Layer.UP][1] = Color.RED

    report("Two WHITE stickers repainted RED", cube)


def validate_a_twisted_corner() -> None:
    """
    Twists one corner in place, leaving every color count correct.

    The UBL corner is made of UP[0], LEFT[0] and BACK[2]. Cycling those three stickers rotates the
    piece without moving it, which no sequence of turns can do to a single corner - the total corner
    twist of a real cube is always a multiple of three.

    :return: None
    """

    cube = Cube(size=3)
    up, left, back = cube.layers[Layer.UP], cube.layers[Layer.LEFT], cube.layers[Layer.BACK]
    up[0], left[0], back[2] = back[2], up[0], left[0]

    report("One corner twisted in place", cube)


def validate_a_swapped_edge_pair() -> None:
    """
    Swaps two edge pieces and leaves everything else alone.

    The UF edge is UP[7] and FRONT[1]; the UR edge is UP[5] and RIGHT[1]. Exchanging both pieces is a
    single transposition, and a real cube can only ever be in an even permutation of its pieces.

    :return: None
    """

    cube = Cube(size=3)
    up, front, right = cube.layers[Layer.UP], cube.layers[Layer.FRONT], cube.layers[Layer.RIGHT]
    up[7], front[1], up[5], right[1] = up[5], right[1], up[7], front[1]

    report("Two edges swapped", cube)


# The sections of this example, in the order `main` runs them
SECTIONS: list[tuple[str, Callable[[], None]]] = [
    ("Reachable states", validate_reachable_states),
    ("A miscounted color", validate_a_miscounted_color),
    ("A twisted corner", validate_a_twisted_corner),
    ("A swapped pair of edges", validate_a_swapped_edge_pair),
]


def main() -> None:
    """
    Runs every section of the example, printing a numbered header before each one.

    :return: None
    """

    for number, (title, section) in enumerate(SECTIONS, start=1):
        print("=" * 100)
        print(f"[{number}] {title}")
        print("=" * 100)
        print()
        section()
        print()


if __name__ == "__main__":
    main()
