"""
Building the first four centers of a big cube.

`create_solver` returns `SolveNxN` for any cube of 4x4 and up. That solver reduces a big cube to a
3x3 before solving it as one, and the first step of the reduction is the centers: white, yellow,
green and red, in that order. Each line of a face is assembled as a bar on another face and put in
place in one go, since the algorithm that inserts a line replaces the whole of it.

The rest of the reduction - the last two centers, the edges, the parity cases and the handover to
the 3x3 solver - is not written yet, so `solve()` returns an algorithm that builds those four
centers and leaves the cube unsolved. The four are always built white up, yellow down, green front
and red right, whichever way the cube was held, so the two centers left over end up on LEFT and on
BACK.

Run it with:

    python examples/08_solve_big_cube.py
"""

# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.solver import create_solver

# Fixed scrambles, so that the output of this example is the same on every run
SCRAMBLE_4X4 = "Rw U2 F Lw' B R2 Uw F2 D' Lw B2 U Rw' F D2"
SCRAMBLE_5X5 = "Uw R2 Fw' D L2 Bw U' Rw B2 Dw F R' Uw2 L Fw2"


def center_color(cube: Cube, layer: Layer) -> Color | None:
    """
    Returns the color a face's center is built in, or None when the face is still mixed.

    :param cube: The Cube instance to read
    :param layer: The face to read
    :return: The color of the center, or None
    """

    size = cube.size
    colors = {cube.layers[layer][row * size + col] for row in range(1, size - 1) for col in range(1, size - 1)}

    return colors.pop() if len(colors) == 1 else None


def print_centers(cube: Cube) -> None:
    """
    Prints, face by face, which center is built and which is still mixed.

    :param cube: The Cube instance to read
    :return: None
    """

    for layer in Layer:
        color = center_color(cube, layer)
        print(f"  {layer.name:<6} {color.name if color else 'still mixed'}")


def build_the_centers_of_a_4x4() -> None:
    """
    Scrambles a 4x4, runs the reduction solver on it and prints the centers it built.

    :return: None
    """

    cube = Cube(size=4)
    Rotator(cube).apply(Algorithm.from_str(SCRAMBLE_4X4))

    print(f"Scramble: {SCRAMBLE_4X4}")
    print(f"create_solver picked: {type(create_solver(cube)).__name__}")

    solution = create_solver(cube).solve()

    print(f"Solution: {solution}")
    print(f"Moves: {len(solution.moves)}")
    print("Centers afterwards:")
    print_centers(cube)


def build_the_centers_of_a_5x5() -> None:
    """
    Does the same for a 5x5, whose fixed centers decide which face every color belongs on.

    :return: None
    """

    cube = Cube(size=5)
    Rotator(cube).apply(Algorithm.from_str(SCRAMBLE_5X5))

    print(f"Scramble: {SCRAMBLE_5X5}")

    create_solver(cube).solve()

    print("Centers afterwards:")
    print_centers(cube)


def show_the_cube_is_not_solved_yet() -> None:
    """
    Shows what the reduction has not done yet: two centers are still mixed, and so is everything
    else, because only the first step of the method exists.

    :return: None
    """

    cube = Cube(size=4)
    Rotator(cube).apply(Algorithm.from_str(SCRAMBLE_4X4))
    create_solver(cube).solve()

    mixed = [layer.name for layer in Layer if center_color(cube, layer) is None]

    print(f"Centers still mixed: {', '.join(mixed)}")
    print(f"Cube solved: {str(cube) == str(Cube(size=4))}")


# The sections of this example, in the order `main` runs them
SECTIONS: list[tuple[str, Callable[[], None]]] = [
    ("Building the centers of a 4x4", build_the_centers_of_a_4x4),
    ("Building the centers of a 5x5", build_the_centers_of_a_5x5),
    ("What the reduction has not done yet", show_the_cube_is_not_solved_yet),
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
