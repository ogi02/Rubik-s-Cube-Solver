# Python imports
import re
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer


class TestMoveStr:
    # fmt: off
    @pytest.mark.parametrize(
        "layer, direction, layer_amount, move_str", [
            (Layer.UP,    Direction.CW,     1, "U"),
            (Layer.FRONT, Direction.CCW,    2, "Fw'"),
            (Layer.LEFT,  Direction.DOUBLE, 3, "3Lw2"),
        ]
    )
    # fmt: on
    def test_success(
        self,
        generate_move: Callable[[Layer, Direction, int], Move],
        layer: Layer,
        direction: Direction,
        layer_amount: int,
        move_str: str,
    ) -> None:
        """
        Tests the string representation of the Move class.

        :param generate_move: Fixture to generate a move
        :param layer: The layer to turn
        :param direction: The direction of the turn
        :param layer_amount: The amount of layers to turn
        :param move_str: The expected string representation of the move
        :return: None
        """

        # Mock the move
        move = generate_move(layer, direction, layer_amount)

        # Assert
        assert str(move) == move_str


class TestMoveEq:
    # fmt: off
    @pytest.mark.parametrize(
        "layer, direction, layer_amount, other_layer, other_direction, other_layer_amount, expected", [
            (Layer.UP,    Direction.CW,     1, Layer.UP,    Direction.CW,     1, True),
            (Layer.UP,    Direction.CCW,    1, Layer.DOWN,  Direction.CW,     1, False),
            (Layer.FRONT, Direction.CCW,    2, Layer.FRONT, Direction.CCW,    2, True),
            (Layer.FRONT, Direction.CW,     2, Layer.FRONT, Direction.CCW,    2, False),
            (Layer.LEFT,  Direction.DOUBLE, 3, Layer.LEFT,  Direction.DOUBLE, 3, True),
            (Layer.LEFT,  Direction.DOUBLE, 3, Layer.LEFT,  Direction.DOUBLE, 2, False),
        ]
    )
    # fmt: on
    def test_success(
        self,
        generate_move: Callable[[Layer, Direction, int], Move],
        layer: Layer,
        direction: Direction,
        layer_amount: int,
        other_layer: Layer,
        other_direction: Direction,
        other_layer_amount: int,
        expected: bool,
    ) -> None:
        """
        Tests the equality method of the Move class.

        :param generate_move: Fixture to generate a move
        :param layer: The layer of the first move
        :param direction: The direction of the first move
        :param layer_amount: The layer amount of the first move
        :param other_layer: The layer of the second move
        :param other_direction: The direction of the second move
        :param other_layer_amount: The layer amount of the second move
        :param expected: The expected result of the equality comparison
        :return: None
        """

        move = generate_move(layer, direction, layer_amount)
        other_move = generate_move(other_layer, other_direction, other_layer_amount)

        assert (move == other_move) == expected

    # fmt: off
    @pytest.mark.parametrize(
        "layer, direction, layer_amount", [
            (Layer.UP, Direction.CW, 1)
        ]
    )
    # fmt: on
    def test_different_type(
        self,
        generate_move: Callable[[Layer, Direction, int], Move],
        layer: Layer,
        direction: Direction,
        layer_amount: int,
    ) -> None:
        """
        Tests the equality method of the Move class when compared to a different type.

        :param generate_move: Fixture to generate a move
        :param layer: The layer of the first move
        :param direction: The direction of the first move
        :param layer_amount: The layer amount of the first move
        :return: None
        """

        move = generate_move(layer, direction, layer_amount)
        other_move = "Not a Move"

        assert move != other_move


class TestMoveFromStr:
    # fmt: off
    @pytest.mark.parametrize(
        "move_string, layer, direction, layer_amount", [
            ("U",       Layer.UP,    Direction.CW,     1),
            ("R'",      Layer.RIGHT, Direction.CCW,    1),
            ("F2",      Layer.FRONT, Direction.DOUBLE, 1),
            ("Uw",      Layer.UP,    Direction.CW,     2),
            ("Rw'",     Layer.RIGHT, Direction.CCW,    2),
            ("Fw2",     Layer.FRONT, Direction.DOUBLE, 2),
            ("3Lw2",    Layer.LEFT,  Direction.DOUBLE, 3),
            ("4Rw",     Layer.RIGHT, Direction.CW,     4),
            ("  U  ",   Layer.UP,    Direction.CW,     1),
            ("\tRw'\t", Layer.RIGHT, Direction.CCW,    2),
        ]
    )
    # fmt: on
    def test_success(
        self,
        move_string: str,
        layer: Layer,
        direction: Direction,
        layer_amount: int,
    ) -> None:
        """
        Tests creating a Move from string.

        :param move_string: The string representation of the move
        :param layer: The expected layer of the move
        :param direction: The expected direction of the move
        :param layer_amount: The expected layer amount of the move
        :return: None
        """

        # Act
        move = Move.from_str(move_string)

        # Assert
        assert move == Move(layer, direction, layer_amount)

    # fmt: off
    @pytest.mark.parametrize(
        "move_string", [
            "",
            "X",
            "RR",
            "R3",
            "Rw3",
            "3R",
            "1Rw",
            "0Rw",
            "r",
            "R '",
        ]
    )
    # fmt: on
    def test_invalid_notation(self, move_string: str) -> None:
        """
        Tests that creating a Move from an invalid string raises a ValueError.

        :param move_string: The string representation of the move
        :return: None
        """

        # Assert
        with pytest.raises(ValueError, match=re.escape(f"Couldn't parse move notation: {move_string}")):
            Move.from_str(move_string)
