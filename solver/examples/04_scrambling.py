"""
Generating scrambles.

`Scrambler` produces a random sequence of moves for a cube of a given size. It never repeats a face
immediately and caps how many moves in a row may share an axis, so the scramble it returns is the
length it claims to be. Scramble length scales with cube size.

The output of this example differs on every run, because the scrambles are random. The other
examples use fixed scramble strings instead, so that their output is reproducible.

Run it with:

    python examples/04_scrambling.py
"""

# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.scramble.scrambler import Scrambler


def generate_scrambles_for_different_sizes() -> None:
    """
    Generates one scramble per cube size and prints it.

    `generate_scramble` returns a `list[Move]`, which `Algorithm` wraps when the whole sequence is
    wanted as one object.

    :return: None
    """

    scrambler = Scrambler()

    for size in (2, 3, 4, 5):
        scramble = Algorithm(scrambler.generate_scramble(cube_size=size))
        print(f"{size}x{size} ({len(scramble.moves)} moves): {scramble}")


def scramble_a_cube() -> None:
    """
    Generates a scramble and applies it to a 3x3 cube.

    :return: None
    """

    cube = Cube(size=3)
    rotator = Rotator(cube)
    scrambler = Scrambler()

    print("Solved 3x3:")
    print(cube)

    scramble = Algorithm(scrambler.generate_scramble(cube_size=3))
    print(f"Scramble: {scramble}")

    rotator.apply(scramble)
    print("Scrambled 3x3:")
    print(cube)


def reject_an_impossible_size() -> None:
    """
    Shows that a cube smaller than 2x2 has no scramble.

    :return: None
    """

    scrambler = Scrambler()

    try:
        scrambler.generate_scramble(cube_size=1)
    except ValueError as error:
        print(f"A 1x1 cube is rejected: {error}")


# The sections of this example, in the order `main` runs them
SECTIONS: list[tuple[str, Callable[[], None]]] = [
    ("Scrambles for different cube sizes", generate_scrambles_for_different_sizes),
    ("Scrambling a cube", scramble_a_cube),
    ("An impossible cube size", reject_an_impossible_size),
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
