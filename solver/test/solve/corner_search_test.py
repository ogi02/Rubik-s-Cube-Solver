# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.CornerSlot import CornerSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.corner_search import search_corner


class TestSearchCorner:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size", [
            2,
            3,
            4,
            5,
        ]
    )
    @pytest.mark.parametrize(
        "first_color, second_color, third_color, expected_slot", [
            (Color.WHITE,  Color.GREEN, Color.ORANGE, CornerSlot.UFL),
            (Color.WHITE,  Color.RED,   Color.GREEN,  CornerSlot.UFR),
            (Color.WHITE,  Color.BLUE,  Color.ORANGE, CornerSlot.UBL),
            (Color.WHITE,  Color.BLUE,  Color.RED,    CornerSlot.UBR),
            (Color.YELLOW, Color.GREEN, Color.ORANGE, CornerSlot.DFL),
            (Color.YELLOW, Color.GREEN, Color.RED,    CornerSlot.DFR),
            (Color.YELLOW, Color.BLUE,  Color.ORANGE, CornerSlot.DBL),
            (Color.YELLOW, Color.BLUE,  Color.RED,    CornerSlot.DBR),
        ]
    )
    # fmt: on
    def test_solved_cube(
        self,
        generate_cube: Callable[[int, str], Cube],
        cube_size: int,
        first_color: Color,
        second_color: Color,
        third_color: Color,
        expected_slot: CornerSlot,
    ) -> None:
        """
        Tests that every corner piece of a solved cube is found in its home slot and is oriented.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param first_color: The first color of the searched corner piece
        :param second_color: The second color of the searched corner piece
        :param third_color: The third color of the searched corner piece
        :param expected_slot: The expected slot of the corner piece
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        assert search_corner(cube, first_color, second_color, third_color) == (expected_slot, 0)

    # fmt: off
    @pytest.mark.parametrize(
        "first_color, second_color, third_color", [
            (Color.WHITE, Color.GREEN, Color.ORANGE),
            (Color.WHITE, Color.ORANGE, Color.GREEN),
            (Color.GREEN, Color.WHITE, Color.ORANGE),
            (Color.GREEN, Color.ORANGE, Color.WHITE),
            (Color.ORANGE, Color.WHITE, Color.GREEN),
            (Color.ORANGE, Color.GREEN, Color.WHITE),
        ]
    )
    # fmt: on
    def test_color_order_is_irrelevant(
        self,
        generate_cube: Callable[[int, str], Cube],
        first_color: Color,
        second_color: Color,
        third_color: Color,
    ) -> None:
        """
        Tests that the three colors of the searched corner piece can be given in any order.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param first_color: The first color of the searched corner piece
        :param second_color: The second color of the searched corner piece
        :param third_color: The third color of the searched corner piece
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")

        # Assert
        assert search_corner(cube, first_color, second_color, third_color) == (CornerSlot.UFL, 0)

    # fmt: off
    @pytest.mark.parametrize(
        "algorithm, first_color, second_color, third_color, expected_slot, expected_orientation", [
            # A U turn moves an UP corner piece within the UP layer and keeps it oriented
            ("U",  Color.WHITE,  Color.GREEN, Color.ORANGE, CornerSlot.UBL, 0),
            # An R turn moves an UP corner piece to another UP slot and twists it one way
            ("R",  Color.WHITE,  Color.RED,   Color.GREEN,  CornerSlot.UBR, 1),
            # An R turn moves an UP corner piece into a DOWN slot and twists it the other way
            ("R",  Color.WHITE,  Color.BLUE,  Color.RED,    CornerSlot.DBR, 2),
            # An F turn moves an UP corner piece within the FRONT layer and twists it one way
            ("F",  Color.WHITE,  Color.GREEN, Color.ORANGE, CornerSlot.UFR, 1),
            # An F turn moves a DOWN corner piece into an UP slot and twists it the other way
            ("F",  Color.YELLOW, Color.GREEN, Color.ORANGE, CornerSlot.UFL, 2),
            # An F turn leaves the corner pieces outside the FRONT layer untouched
            ("F",  Color.WHITE,  Color.BLUE,  Color.ORANGE, CornerSlot.UBL, 0),
            # An F2 turn moves an UP corner piece into a DOWN slot but does not twist it
            ("F2", Color.WHITE,  Color.GREEN, Color.ORANGE, CornerSlot.DFR, 0),
        ]
    )
    # fmt: on
    def test_after_algorithm(
        self,
        generate_cube: Callable[[int, str], Cube],
        algorithm: str,
        first_color: Color,
        second_color: Color,
        third_color: Color,
        expected_slot: CornerSlot,
        expected_orientation: int,
    ) -> None:
        """
        Tests that a corner piece is found in the slot the algorithm moved it to, with the correct orientation.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The algorithm applied to the cube
        :param first_color: The first color of the searched corner piece
        :param second_color: The second color of the searched corner piece
        :param third_color: The third color of the searched corner piece
        :param expected_slot: The expected slot of the corner piece
        :param expected_orientation: The expected orientation of the corner piece
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, algorithm)

        # Assert
        assert search_corner(cube, first_color, second_color, third_color) == (expected_slot, expected_orientation)

    # fmt: off
    @pytest.mark.parametrize(
        "first_color, second_color, third_color", [
            (Color.WHITE, Color.YELLOW, Color.GREEN),
            (Color.ORANGE, Color.RED, Color.WHITE),
            (Color.GREEN, Color.BLUE, Color.WHITE),
            (Color.WHITE, Color.GREEN, Color.GREEN),
        ]
    )
    # fmt: on
    def test_invalid_colors(
        self,
        generate_cube: Callable[[int, str], Cube],
        first_color: Color,
        second_color: Color,
        third_color: Color,
    ) -> None:
        """
        Tests that searching a corner piece with a color triple that is not a valid corner raises a ValueError.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param first_color: The first color of the searched corner piece
        :param second_color: The second color of the searched corner piece
        :param third_color: The third color of the searched corner piece
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")

        # Assert
        with pytest.raises(ValueError, match="Invalid corner piece: "):
            search_corner(cube, first_color, second_color, third_color)

    def test_corner_not_found(self) -> None:
        """
        Tests that searching a valid corner piece that is not present on the cube raises a ValueError.

        :return: None
        """

        # Build a cube with all stickers of the same color, so that no corner piece matches
        cube = Cube(3, {layer: [Color.WHITE] * 9 for layer in Layer})

        # Assert
        with pytest.raises(ValueError, match="Corner piece not found: "):
            search_corner(cube, Color.WHITE, Color.GREEN, Color.ORANGE)
