"""
Solving a 3x3 cube.

`Solve3x3` is a human, CFOP-style solver: cross, first two layers, orientation of the last layer,
then permutation of the last layer. Every step recognises a case with the piece searches and looks
up an algorithm for it, rather than searching for a move sequence, so the solution it returns is not
the shortest one.

`solve()` mutates the cube it was given, so afterwards the same object is solved and the returned
`Algorithm` is what got it there. The cross is built on DOWN around whichever center is yellow, so a
cube that started in another orientation ends up solved in the orientation the cross rotated it
into - every face shows one color, but not necessarily the one it started with.

Run it with:

    python examples/07_solve_3x3.py
"""

# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.cube_3x3.solve_3x3 import Solve3x3

# A fixed scramble, so that the output of this example is the same on every run
SCRAMBLE = "D2 F2 D B' L2 B R F U L2 B2 F' L' D2 L2 F' R2 L' B' R2"


def solve_a_scrambled_cube() -> None:
    """
    Scrambles a 3x3, solves it, and prints the solution.

    :return: None
    """

    cube = Cube(size=3)
    Rotator(cube).apply(Algorithm.from_str(SCRAMBLE))

    print(f"Scramble: {SCRAMBLE}")
    print("Scrambled 3x3:")
    print(cube)

    solution = Solve3x3(cube).solve()

    print(f"Solution ({len(solution.moves)} moves): {solution}")
    print("Solved 3x3:")
    print(cube)

    # Every face shows a single color, though not necessarily the one it started with
    single_colored = {layer: len(set(stickers)) == 1 for layer, stickers in cube.layers.items()}
    print(f"Every face is a single color: {all(single_colored.values())}")


def read_the_solution_back() -> None:
    """
    Prints the first few moves of the solution and the color each face ended up showing.

    :return: None
    """

    cube = Cube(size=3)
    Rotator(cube).apply(Algorithm.from_str(SCRAMBLE))
    solution = Solve3x3(cube).solve()

    print(f"First ten moves of the solution: {Algorithm(solution.moves[:10])}")

    for layer in Layer:
        print(f"  {layer.name:<6} ended up {cube.layers[layer][0].name}")


def reject_the_wrong_size() -> None:
    """
    Shows that `Solve3x3` refuses anything that is not a 3x3, at construction time.

    :return: None
    """

    try:
        Solve3x3(Cube(size=4))
    except ValueError as error:
        print(f"A 4x4 is rejected: {error}")


# The sections of this example, in the order `main` runs them
SECTIONS: list[tuple[str, Callable[[], None]]] = [
    ("Solving a scrambled 3x3", solve_a_scrambled_cube),
    ("Reading the solution back", read_the_solution_back),
    ("The size check", reject_the_wrong_size),
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
