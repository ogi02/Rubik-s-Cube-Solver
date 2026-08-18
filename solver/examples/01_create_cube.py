"""
Creating cubes.

A `Cube` is six flat sticker lists, one per face, each of length `size * size`. Index `r * size + c`
addresses row `r`, column `c` of a face. This example creates cubes of a few sizes, prints them,
reads individual stickers and builds a cube from an explicit sticker layout.

Run it with:

    python examples/01_create_cube.py
"""

# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer


def create_cubes_of_different_sizes() -> None:
    """
    Creates a 2x2, a 3x3 and a 5x5 cube and prints each of them.

    A new cube is always solved, with WHITE on UP, YELLOW on DOWN, ORANGE on LEFT, RED on RIGHT,
    GREEN on FRONT and BLUE on BACK. Printing a cube renders it as the familiar unfolded net.

    :return: None
    """

    for size in (2, 3, 5):
        cube = Cube(size=size)
        print(f"A solved {size}x{size} cube:")
        print(cube)


def read_individual_stickers() -> None:
    """
    Reads single stickers out of a cube's `layers` dictionary.

    :return: None
    """

    cube = Cube(size=3)

    # Every face is one flat list of `size * size` colors, in reading order
    front = cube.layers[Layer.FRONT]
    print(f"The FRONT face of a solved 3x3: {[color.value for color in front]}")

    # Row `r`, column `c` of a face lives at index `r * size + c`
    row, col = 1, 2
    center_right = front[row * cube.size + col]
    print(f"The sticker at row {row}, column {col} of FRONT is {center_right.name}")


def create_cube_from_explicit_layers() -> None:
    """
    Creates a cube from a sticker layout instead of letting it start solved.

    Passing `layers` is how a cube is rebuilt from a scan, a saved state or a hand-written case. The
    layout below is a solved cube with the UP and FRONT faces swapped, which is not a state a real
    cube can reach - the validator in `05_validating.py` is what rejects layouts like this.

    :return: None
    """

    size = 3
    layers = {
        Layer.UP: [Color.GREEN] * size * size,
        Layer.DOWN: [Color.YELLOW] * size * size,
        Layer.LEFT: [Color.ORANGE] * size * size,
        Layer.RIGHT: [Color.RED] * size * size,
        Layer.FRONT: [Color.WHITE] * size * size,
        Layer.BACK: [Color.BLUE] * size * size,
    }

    cube = Cube(size=size, layers=layers)
    print("A cube built from an explicit sticker layout:")
    print(cube)


# The sections of this example, in the order `main` runs them
SECTIONS: list[tuple[str, Callable[[], None]]] = [
    ("Cubes of different sizes", create_cubes_of_different_sizes),
    ("Reading individual stickers", read_individual_stickers),
    ("A cube from an explicit sticker layout", create_cube_from_explicit_layers),
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
