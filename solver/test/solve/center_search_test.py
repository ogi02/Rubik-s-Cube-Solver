# Python imports
import random
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.scramble.scrambler import Scrambler
from rubik_cube_solver.solve.center_search import search_center

# One representative cell of every center piece position type of each tested cube size.
CENTER_POSITION_TYPES: dict[int, list[tuple[int, int]]] = {
    4: [(1, 1)],
    5: [(1, 1), (1, 2)],
    6: [(1, 1), (1, 2), (2, 1), (2, 2)],
}


class TestSearchCenter:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, row, col, expected_cells", [
            # A 4x4 cube has a single position type, the x center
            (4, 1, 1, [(1, 1), (1, 2), (2, 1), (2, 2)]),
            # A 5x5 cube adds the + center, and its fixed center is not a piece
            (5, 1, 1, [(1, 1), (1, 3), (3, 1), (3, 3)]),
            (5, 1, 2, [(1, 2), (2, 1), (2, 3), (3, 2)]),
            # A 6x6 cube has the outer x center, the two obliques and the inner x center
            (6, 1, 1, [(1, 1), (1, 4), (4, 1), (4, 4)]),
            (6, 1, 2, [(1, 2), (2, 4), (3, 1), (4, 3)]),
            (6, 2, 1, [(1, 3), (2, 1), (3, 4), (4, 2)]),
            (6, 2, 2, [(2, 2), (2, 3), (3, 2), (3, 3)]),
        ]
    )
    @pytest.mark.parametrize(
        "color, expected_layer", [
            (Color.WHITE,  Layer.UP),
            (Color.YELLOW, Layer.DOWN),
            (Color.ORANGE, Layer.LEFT),
            (Color.RED,    Layer.RIGHT),
            (Color.GREEN,  Layer.FRONT),
            (Color.BLUE,   Layer.BACK),
        ]
    )
    # fmt: on
    def test_solved_cube(
        self,
        generate_cube: Callable[[int, str], Cube],
        cube_size: int,
        row: int,
        col: int,
        expected_cells: list[tuple[int, int]],
        color: Color,
        expected_layer: Layer,
    ) -> None:
        """
        Tests that on a solved cube every position type is found four times, all four pieces on the
        single face of that color and on the four cells the type occupies.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param row: The row of the searched position type
        :param col: The column of the searched position type
        :param expected_cells: The four cells the position type occupies on a face
        :param color: The color of the searched center pieces
        :param expected_layer: The face the center pieces of that color lie on
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        assert search_center(cube, color, row, col) == [(expected_layer, r, c) for r, c in expected_cells]

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, row, col, expected_cells", [
            # Every cell of the 5x5 x center names the same position type
            (5, 1, 1, [(1, 1), (1, 3), (3, 1), (3, 3)]),
            (5, 1, 3, [(1, 1), (1, 3), (3, 1), (3, 3)]),
            (5, 3, 1, [(1, 1), (1, 3), (3, 1), (3, 3)]),
            (5, 3, 3, [(1, 1), (1, 3), (3, 1), (3, 3)]),
            # Every cell of the 5x5 + center names the same position type
            (5, 1, 2, [(1, 2), (2, 1), (2, 3), (3, 2)]),
            (5, 2, 1, [(1, 2), (2, 1), (2, 3), (3, 2)]),
            (5, 2, 3, [(1, 2), (2, 1), (2, 3), (3, 2)]),
            (5, 3, 2, [(1, 2), (2, 1), (2, 3), (3, 2)]),
            # Every cell of one 6x6 oblique names the same position type
            (6, 1, 2, [(1, 2), (2, 4), (3, 1), (4, 3)]),
            (6, 2, 4, [(1, 2), (2, 4), (3, 1), (4, 3)]),
            (6, 3, 1, [(1, 2), (2, 4), (3, 1), (4, 3)]),
            (6, 4, 3, [(1, 2), (2, 4), (3, 1), (4, 3)]),
        ]
    )
    # fmt: on
    def test_any_cell_of_the_position_type(
        self,
        generate_cube: Callable[[int, str], Cube],
        cube_size: int,
        row: int,
        col: int,
        expected_cells: list[tuple[int, int]],
    ) -> None:
        """
        Tests that any of the four cells a position type occupies names that whole type, so the
        caller can pass the cell it cares about rather than a canonical one.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param row: The row of the cell naming the position type
        :param col: The column of the cell naming the position type
        :param expected_cells: The four cells the position type occupies on a face
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        assert search_center(cube, Color.WHITE, row, col) == [(Layer.UP, r, c) for r, c in expected_cells]

    def test_obliques_are_different_position_types(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the two oblique position types of an even cube are kept apart. They are mirror
        images of each other and no turn ever swaps them, so a piece of one can never fill a cell
        of the other.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(6, "")

        # Assert the two obliques occupy disjoint sets of cells
        first_oblique = {(result.row, result.col) for result in search_center(cube, Color.WHITE, 1, 2)}
        second_oblique = {(result.row, result.col) for result in search_center(cube, Color.WHITE, 2, 1)}
        assert first_oblique.isdisjoint(second_oblique)

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, algorithm, row, col, expected", [
            # An F turn is an outer slice and leaves the UP center pieces where they are
            (4, "F", 1, 1, [(Layer.UP, 1, 1), (Layer.UP, 1, 2), (Layer.UP, 2, 1), (Layer.UP, 2, 2)]),
            # A wide turn takes one piece off the UP face and puts it on the FRONT face
            (4, "Rw U Rw'", 1, 1, [(Layer.UP, 1, 1), (Layer.UP, 1, 2), (Layer.UP, 2, 2), (Layer.FRONT, 1, 2)]),
            # A double wide turn moves half of the UP center pieces onto the DOWN face
            (4, "Rw2", 1, 1, [(Layer.UP, 1, 1), (Layer.UP, 2, 1), (Layer.DOWN, 1, 2), (Layer.DOWN, 2, 2)]),
            # The pieces of one type can end up spread over three faces at once
            (4, "Rw U2 Rw' Uw", 1, 1, [(Layer.UP, 2, 1), (Layer.UP, 2, 2), (Layer.LEFT, 1, 2), (Layer.FRONT, 2, 2)]),
            # The x center and the + center of a 5x5 cube move independently of each other
            (5, "Rw U Rw'", 1, 1, [(Layer.UP, 1, 1), (Layer.UP, 1, 3), (Layer.UP, 3, 3), (Layer.FRONT, 1, 3)]),
            (5, "Rw U Rw'", 1, 2, [(Layer.UP, 1, 2), (Layer.UP, 2, 1), (Layer.UP, 2, 3), (Layer.FRONT, 2, 3)]),
            # So do the two obliques of a 6x6 cube, while its inner x center stays inside the slice
            (6, "Rw U Rw'", 1, 2, [(Layer.UP, 1, 2), (Layer.UP, 2, 4), (Layer.UP, 3, 1), (Layer.FRONT, 2, 4)]),
            (6, "Rw U Rw'", 2, 1, [(Layer.UP, 1, 3), (Layer.UP, 2, 1), (Layer.UP, 3, 4), (Layer.FRONT, 3, 4)]),
            (6, "Rw U Rw'", 2, 2, [(Layer.UP, 2, 2), (Layer.UP, 2, 3), (Layer.UP, 3, 2), (Layer.UP, 3, 3)]),
        ]
    )
    # fmt: on
    def test_after_algorithm(
        self,
        generate_cube: Callable[[int, str], Cube],
        cube_size: int,
        algorithm: str,
        row: int,
        col: int,
        expected: list[tuple[Layer, int, int]],
    ) -> None:
        """
        Tests that the center pieces are found on the faces and cells the algorithm moved them to.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param algorithm: The algorithm applied to the cube
        :param row: The row of the searched position type
        :param col: The column of the searched position type
        :param expected: The expected location of every center piece of the searched type
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, algorithm)

        # Assert
        assert search_center(cube, Color.WHITE, row, col) == expected

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size", [
            4,
            5,
            6,
        ]
    )
    # fmt: on
    def test_scrambled_cube(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that on scrambled cubes every color and position type is found exactly four times and
        that every returned location really holds a sticker of that color. The scrambles reach far
        more arrangements than the algorithms picked by hand, and the random number generator is
        seeded so a failing run can be reproduced exactly.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Scramble twenty cubes
        random.seed(0)
        for _ in range(20):
            cube = generate_cube(cube_size, str(Algorithm(Scrambler().generate_scramble(cube_size))))

            for row, col in CENTER_POSITION_TYPES[cube_size]:
                for color in Color:
                    results = search_center(cube, color, row, col)

                    # Assert every color of a position type is on the cube exactly four times
                    assert len(results) == 4

                    # Assert every location holds a sticker of the searched color
                    for result in results:
                        assert cube.layers[result.layer][result.row * cube_size + result.col] == color

    def test_no_pieces_of_that_color(self) -> None:
        """
        Tests that searching a color the cube has no center piece of returns an empty list.

        :return: None
        """

        # Build a cube with all stickers of the same color
        cube = Cube(4, {layer: [Color.WHITE] * 16 for layer in Layer})

        # Assert
        assert search_center(cube, Color.GREEN, 1, 1) == []

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size", [
            2,
            3,
        ]
    )
    # fmt: on
    def test_small_cube(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that searching a center piece on a cube smaller than 4x4 raises a ValueError. Such a
        cube has no center pieces at all - a 2x2 has no center stickers and the single center
        sticker of a 3x3 face is fixed.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        with pytest.raises(ValueError, match=f"Center search is supported only on big cubes, got size {cube_size}"):
            search_center(cube, Color.WHITE, 1, 1)

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, row, col", [
            # The outer ring of a face holds corner and edge pieces, not center pieces
            (4, 0, 1),
            (4, 1, 0),
            (4, 1, 3),
            (4, 3, 1),
            (5, 0, 4),
            (6, 5, 5),
            # A cell outside the face altogether
            (4, 1, 7),
            (5, -1, 1),
        ]
    )
    # fmt: on
    def test_invalid_position(
        self,
        generate_cube: Callable[[int, str], Cube],
        cube_size: int,
        row: int,
        col: int,
    ) -> None:
        """
        Tests that searching a cell that holds no center piece raises a ValueError.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param row: The row of the searched position type
        :param col: The column of the searched position type
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        with pytest.raises(ValueError, match=f"Invalid center piece position: row {row}, col {col}."):
            search_center(cube, Color.WHITE, row, col)

    def test_fixed_center_position(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that searching the fixed center of an odd sized cube raises a ValueError. That
        sticker never leaves its face, so it is not a center piece the solve can move.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(5, "")

        # Assert
        with pytest.raises(ValueError, match="Fixed center piece position: row 2, col 2."):
            search_center(cube, Color.WHITE, 2, 2)
