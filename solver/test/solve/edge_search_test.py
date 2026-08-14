# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.edge_search import search_edge


class TestSearchEdge:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size", [
            3,
            5,
            7,
        ]
    )
    @pytest.mark.parametrize(
        "first_color, second_color, expected_slot", [
            (Color.WHITE,  Color.GREEN,  EdgeSlot.UF),
            (Color.WHITE,  Color.BLUE,   EdgeSlot.UB),
            (Color.WHITE,  Color.ORANGE, EdgeSlot.UL),
            (Color.WHITE,  Color.RED,    EdgeSlot.UR),
            (Color.YELLOW, Color.GREEN,  EdgeSlot.DF),
            (Color.YELLOW, Color.BLUE,   EdgeSlot.DB),
            (Color.YELLOW, Color.ORANGE, EdgeSlot.DL),
            (Color.YELLOW, Color.RED,    EdgeSlot.DR),
            (Color.GREEN,  Color.ORANGE, EdgeSlot.FL),
            (Color.GREEN,  Color.RED,    EdgeSlot.FR),
            (Color.BLUE,   Color.ORANGE, EdgeSlot.BL),
            (Color.BLUE,   Color.RED,    EdgeSlot.BR),
        ]
    )
    # fmt: on
    def test_solved_cube(
        self,
        generate_cube: Callable[[int, str], Cube],
        cube_size: int,
        first_color: Color,
        second_color: Color,
        expected_slot: EdgeSlot,
    ) -> None:
        """
        Tests that every edge piece of a solved cube is found in its home slot and is oriented.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param first_color: The first color of the searched edge piece
        :param second_color: The second color of the searched edge piece
        :param expected_slot: The expected slot of the edge piece
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        assert search_edge(cube, first_color, second_color) == (expected_slot, True)

    # fmt: off
    @pytest.mark.parametrize(
        "first_color, second_color", [
            (Color.WHITE, Color.GREEN),
            (Color.GREEN, Color.WHITE),
        ]
    )
    # fmt: on
    def test_color_order_is_irrelevant(
        self,
        generate_cube: Callable[[int, str], Cube],
        first_color: Color,
        second_color: Color,
    ) -> None:
        """
        Tests that the two colors of the searched edge piece can be given in any order.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param first_color: The first color of the searched edge piece
        :param second_color: The second color of the searched edge piece
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")

        # Assert
        assert search_edge(cube, first_color, second_color) == (EdgeSlot.UF, True)

    # fmt: off
    @pytest.mark.parametrize(
        "algorithm, first_color, second_color, expected_slot, expected_is_good", [
            # A U turn moves an UP edge piece within the UP layer and keeps it oriented
            ("U",  Color.WHITE, Color.GREEN, EdgeSlot.UL, True),
            # An R turn moves an UP edge piece into an equatorial slot and keeps it oriented
            ("R",  Color.WHITE, Color.RED,   EdgeSlot.BR, True),
            # An F turn moves an UP edge piece into an equatorial slot and disorients it
            ("F",  Color.WHITE, Color.GREEN, EdgeSlot.FR, False),
            # An F turn moves an equatorial edge piece into a DOWN slot and disorients it
            ("F",  Color.GREEN, Color.RED,   EdgeSlot.DF, False),
            # An F turn leaves the edge pieces outside the FRONT layer untouched
            ("F",  Color.WHITE, Color.BLUE,  EdgeSlot.UB, True),
            # An F2 turn moves an UP edge piece into a DOWN slot and keeps it oriented
            ("F2", Color.WHITE, Color.GREEN, EdgeSlot.DF, True),
            # Two F turns in a row restore the orientation of an equatorial edge piece
            ("F F", Color.GREEN, Color.RED,  EdgeSlot.FL, True),
        ]
    )
    # fmt: on
    def test_after_algorithm(
        self,
        generate_cube: Callable[[int, str], Cube],
        algorithm: str,
        first_color: Color,
        second_color: Color,
        expected_slot: EdgeSlot,
        expected_is_good: bool,
    ) -> None:
        """
        Tests that an edge piece is found in the slot the algorithm moved it to, with the correct orientation.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The algorithm applied to the cube
        :param first_color: The first color of the searched edge piece
        :param second_color: The second color of the searched edge piece
        :param expected_slot: The expected slot of the edge piece
        :param expected_is_good: The expected orientation flag of the edge piece
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, algorithm)

        # Assert
        assert search_edge(cube, first_color, second_color) == (expected_slot, expected_is_good)

    def test_flipped_in_home_slot(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that an edge piece flipped in its home slot is found there and reported as not oriented.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube and flip the UF edge piece in place
        cube = generate_cube(3, "")
        cube.layers[Layer.UP][7] = Color.GREEN
        cube.layers[Layer.FRONT][1] = Color.WHITE

        # Assert
        assert search_edge(cube, Color.WHITE, Color.GREEN) == (EdgeSlot.UF, False)

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size", [
            2,
            4,
            6,
        ]
    )
    # fmt: on
    def test_even_sized_cube(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that searching an edge piece on an even-sized cube raises a ValueError.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        with pytest.raises(ValueError, match=f"Edge search is supported only on odd-sized cubes, got size {cube_size}"):
            search_edge(cube, Color.WHITE, Color.GREEN)

    # fmt: off
    @pytest.mark.parametrize(
        "first_color, second_color", [
            (Color.WHITE,  Color.YELLOW),
            (Color.ORANGE, Color.RED),
            (Color.GREEN,  Color.BLUE),
            (Color.WHITE,  Color.WHITE),
        ]
    )
    # fmt: on
    def test_invalid_colors(
        self,
        generate_cube: Callable[[int, str], Cube],
        first_color: Color,
        second_color: Color,
    ) -> None:
        """
        Tests that searching an edge piece with a color pair that is not a valid edge raises a ValueError.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param first_color: The first color of the searched edge piece
        :param second_color: The second color of the searched edge piece
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")

        # Assert
        with pytest.raises(ValueError, match="Invalid edge piece: "):
            search_edge(cube, first_color, second_color)

    def test_edge_not_found(self) -> None:
        """
        Tests that searching a valid edge piece that is not present on the cube raises a ValueError.

        :return: None
        """

        # Build a cube with all stickers of the same color, so that no edge piece matches
        cube = Cube(3, {layer: [Color.WHITE] * 9 for layer in Layer})

        # Assert
        with pytest.raises(ValueError, match="Edge piece not found: "):
            search_edge(cube, Color.WHITE, Color.GREEN)
