"""
Solving big cubes - 4x4, 5x5 and 9x9.

`create_solver` is the entry point for solving any cube: it reads the cube's size and returns the
solver for it, so nothing here names `SolveNxN` directly. Every cube of size 4 and up gets the same
solver and the same method - reduction. All six centers are built first, then the edges are paired
until the cube behaves like a 3x3 with fat stickers, and that reduced cube is finally solved with
the CFOP method of `Solve3x3`. Nothing about the method is specific to one size, so the same code
path solves a 4x4 and a 9x9; only the amount of work grows.

`solve()` mutates the cube it was given, so afterwards the same object is solved and the returned
`Algorithm` is what got it there. The solution grows quickly with size, because a bigger cube has
more center pieces to place and more wings to pair: a 4x4 takes a few hundred moves and a 9x9 takes
well over a thousand.

Run it with:

    python examples/08_solve_big_cubes.py
"""

# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.solver import create_solver

# Fixed scrambles, so that the output of this example is the same on every run
SCRAMBLE_4X4 = (
    "F' U2 R' Dw' D L B2 Uw Dw' R D2 R Rw' U2 F2 Dw2 R L2 Dw Rw' "
    "R' D' F2 B' U' Bw Dw' D' L Uw B2 R Fw2 Bw2 Rw L Bw D' Rw2 Dw"
)
SCRAMBLE_5X5 = (
    "L' B2 Uw2 U' R' D2 Lw' R' Bw2 Rw2 Lw R' Uw B' U' Fw U Lw2 Uw' U "
    "L2 D L' U' L R U2 B2 U' Rw D' Rw' Bw U2 Rw2 Fw2 Bw2 Rw L2 U Dw2 "
    "Bw2 Dw2 R' B R' U' L Lw2 F Lw2 Rw Dw' D2 F2 Rw2 R Bw' Fw' Dw'"
)
SCRAMBLE_9X9 = (
    "3Rw 3Uw2 D Uw2 3Fw2 3Dw' F' Fw2 Uw 3Uw R' 3Uw2 4Dw 3Fw 4Uw2 D' 4Fw' 3Uw' B' 3Rw "
    "U' 3Lw D2 3Bw 4Rw 3Uw Uw' 4Dw' 4Rw' 3Fw2 4Fw2 4Uw R' 3Bw' D L 3Lw' Dw' 4Lw Uw' "
    "3Uw 4Lw2 R' L2 Fw2 R2 4Uw 3Fw 4Uw' 3Dw' 4Fw' F' Fw 4Rw' 3Uw2 Rw 4Dw2 4Rw' 4Lw 4Uw "
    "L' 3Dw' L 4Lw 3Lw2 3Uw' 4Uw2 Bw B2 4Bw2 L 4Fw2 Bw 4Bw' 3Dw' 3Rw2 F2 4Bw2 4Rw' 3Uw' "
    "Lw' B2 4Fw' 3Bw' Dw2 4Dw2 3Uw2 F' 3Uw2 3Fw Lw' 4Bw 4Uw2 Rw Lw' B F' Bw2 D 3Bw2 "
    "4Bw2 Uw' B' 3Fw2 4Uw R' Uw U2 L2 4Lw2 4Dw2 U2 3Dw2 4Fw 4Bw2 Lw 4Bw 4Dw Bw' D "
    "3Fw2 3Bw' 4Uw2 3Uw U D' 3Bw 4Lw 3Rw' B' 4Lw' 4Uw Bw' L2 U 4Rw2 U 4Rw' 4Dw2 3Lw2"
)


def scramble_cube(size: int, scramble: str) -> Cube:
    """
    Builds a cube of the given size and applies the scramble to it.

    :param size: The size of the cube
    :param scramble: The scramble, in standard notation
    :return: The scrambled cube
    """

    cube = Cube(size=size)
    Rotator(cube).apply(Algorithm.from_str(scramble))

    return cube


def is_solved(cube: Cube) -> bool:
    """
    Checks whether every face of the cube shows a single color.

    :param cube: The cube to check
    :return: Whether the cube is solved
    """

    return all(len(set(stickers)) == 1 for stickers in cube.layers.values())


def solve_a_scrambled_4x4() -> None:
    """
    Scrambles a 4x4, solves it, and prints the solution and both nets.

    :return: None
    """

    cube = scramble_cube(size=4, scramble=SCRAMBLE_4X4)

    print(f"Scramble: {SCRAMBLE_4X4}")
    print("Scrambled 4x4:")
    print(cube)

    solver = create_solver(cube)
    print(f"create_solver picked: {type(solver).__name__}")

    solution = solver.solve()

    print(f"Solution ({len(solution.moves)} moves): {solution}")
    print("Solved 4x4:")
    print(cube)


def solve_a_scrambled_5x5() -> None:
    """
    Scrambles a 5x5, solves it, and prints the solution and both nets.

    The same solver handles it - only the size of the cube it was built around differs.

    :return: None
    """

    cube = scramble_cube(size=5, scramble=SCRAMBLE_5X5)

    print(f"Scramble: {SCRAMBLE_5X5}")
    print("Scrambled 5x5:")
    print(cube)

    solver = create_solver(cube)
    print(f"create_solver picked: {type(solver).__name__}")

    solution = solver.solve()

    print(f"Solution ({len(solution.moves)} moves): {solution}")
    print("Solved 5x5:")
    print(cube)


def solve_a_scrambled_9x9() -> None:
    """
    Scrambles a 9x9 and solves it.

    A 9x9 net is 27 rows tall and its solution runs to well over a thousand moves, so this section
    prints the move count and the first ten moves instead of either in full.

    :return: None
    """

    cube = scramble_cube(size=9, scramble=SCRAMBLE_9X9)

    print(f"Scramble ({len(Algorithm.from_str(SCRAMBLE_9X9).moves)} moves): {SCRAMBLE_9X9}")

    solution = create_solver(cube).solve()

    print(f"Solution: {len(solution.moves)} moves")
    print(f"First ten moves of the solution: {Algorithm(solution.moves[:10])}")
    print(f"Every face is a single color: {is_solved(cube)}")


def replay_the_solution() -> None:
    """
    Applies a 4x4 solution to a second, identically scrambled cube.

    The solution contains layer turns only - `solve()` strips whole-cube rotations before returning,
    because the machine that executes a solution can only turn layers. Big-cube solutions also hold
    wide turns, such as `Rw` and `3Rw`, which turn several layers at once.

    :return: None
    """

    solving_cube = scramble_cube(size=4, scramble=SCRAMBLE_4X4)
    solution = create_solver(solving_cube).solve()

    replay_cube = scramble_cube(size=4, scramble=SCRAMBLE_4X4)
    Rotator(replay_cube).apply(solution)

    wide_turns = [move for move in solution.moves if move.layer_amount > 1]
    print(f"The solution holds {len(wide_turns)} wide turns out of {len(solution.moves)} moves")
    print(f"Replaying the solution on a second cube solves it: {is_solved(replay_cube)}")


def even_and_odd_cubes() -> None:
    """
    Shows what the size of a big cube changes about solving it.

    An odd cube has a fixed center piece in the middle of every face, so its color scheme is decided
    before the solve starts. An even cube has none, so the solver picks which face each color is
    built on. Both are solved into the same orientation, because the method builds the yellow center
    on DOWN either way.

    The size also decides which parities can appear. Pairing the last edge is needed at any size,
    but only an even cube can be left with a single flipped edge or a single pair of swapped edges
    once it is reduced, so only there does the parity step check for them.

    :return: None
    """

    for size, scramble in ((4, SCRAMBLE_4X4), (5, SCRAMBLE_5X5), (9, SCRAMBLE_9X9)):
        cube = scramble_cube(size=size, scramble=scramble)
        create_solver(cube).solve()

        fixed_centers = size % 2 == 1
        print(f"{size}x{size}:")
        print(f"  Fixed center on every face: {fixed_centers}")
        print(f"  Can need the even-cube parity fixes: {not fixed_centers}")
        print(f"  Solved with {', '.join(f'{layer.name} {cube.layers[layer][0].name}' for layer in Layer)}")


# The sections of this example, in the order `main` runs them
SECTIONS: list[tuple[str, Callable[[], None]]] = [
    ("Solving a scrambled 4x4", solve_a_scrambled_4x4),
    ("Solving a scrambled 5x5", solve_a_scrambled_5x5),
    ("Solving a scrambled 9x9", solve_a_scrambled_9x9),
    ("Replaying the solution on a second cube", replay_the_solution),
    ("Even and odd cubes", even_and_odd_cubes),
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
