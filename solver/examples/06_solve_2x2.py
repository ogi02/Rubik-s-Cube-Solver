"""
Solving a 2x2 cube.

`create_solver` is the entry point for solving any cube: it reads the cube's size and returns the
solver for it, so nothing here names `Solve2x2` directly. For a 2x2 that solver is a human,
layer-by-layer one: it builds the yellow first layer on DOWN, then orients the last layer and
permutes it, each step recognising a case and looking up an algorithm rather than searching. The
solution it returns is therefore not the shortest one.

`solve()` mutates the cube it was given, so afterwards the same object is solved and the returned
`Algorithm` is what got it there. A 2x2 has no centers, so nothing on the cube says which face is
which - it is always solved into the color scheme of a fresh `Cube(2)`.

Run it with:

    python examples/06_solve_2x2.py
"""

# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.solve.solver import create_solver

# A fixed scramble, so that the output of this example is the same on every run
SCRAMBLE = "R U' F2 R2 U R' F U2 R' U'"


def solve_a_scrambled_cube() -> None:
    """
    Scrambles a 2x2, solves it, and prints the solution.

    :return: None
    """

    cube = Cube(size=2)
    Rotator(cube).apply(Algorithm.from_str(SCRAMBLE))

    print(f"Scramble: {SCRAMBLE}")
    print("Scrambled 2x2:")
    print(cube)

    solver = create_solver(cube)
    print(f"create_solver picked: {type(solver).__name__}")

    solution = solver.solve()

    print(f"Solution ({len(solution.moves)} moves): {solution}")
    print("Solved 2x2:")
    print(cube)

    # A solved 2x2 always matches a fresh cube, whatever orientation it was scrambled from
    print(f"Matches a fresh Cube(2): {cube.layers == Cube(size=2).layers}")


def replay_the_solution() -> None:
    """
    Applies the solution to a second, identically scrambled cube.

    The solution contains layer turns only - `solve()` strips whole-cube rotations before returning,
    because the machine that executes a solution can only turn layers.

    :return: None
    """

    solving_cube = Cube(size=2)
    Rotator(solving_cube).apply(Algorithm.from_str(SCRAMBLE))
    solution = create_solver(solving_cube).solve()

    replay_cube = Cube(size=2)
    replay_rotator = Rotator(replay_cube)
    replay_rotator.apply(Algorithm.from_str(SCRAMBLE))
    replay_rotator.apply(solution)

    print(f"Replaying the solution on a second cube solves it: {replay_cube.layers == Cube(size=2).layers}")


def reject_a_cube_with_no_solver() -> None:
    """
    Shows that `create_solver` refuses a size no solver handles, before any solving starts.

    :return: None
    """

    try:
        create_solver(Cube(size=4))
    except ValueError as error:
        print(f"A 4x4 is rejected: {error}")


# The sections of this example, in the order `main` runs them
SECTIONS: list[tuple[str, Callable[[], None]]] = [
    ("Solving a scrambled 2x2", solve_a_scrambled_cube),
    ("Replaying the solution on a second cube", replay_the_solution),
    ("Cubes with no solver", reject_a_cube_with_no_solver),
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
