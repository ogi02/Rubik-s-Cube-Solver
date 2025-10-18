from typing import Callable

import pytest

from cube_rotation.move import Move
from enums.Direction import Direction
from enums.Layer import Layer
from scramble.scrambler import Scrambler


@pytest.fixture
def scrambler() -> Scrambler:
    """
    Returns a Scrambler instance.

    :return: The Scrambler instance
    """

    return Scrambler()


@pytest.fixture
def generate_move() -> Callable[[Layer, Direction, int], Move]:
    """
    Returns a method to generate a move.

    :return: The callable method
    """

    def _generate(layer: Layer, direction: Direction, amount: int) -> Move:
        """
        Generates a move.

        :param layer: The layer to rotate
        :param direction: The direction to rotate
        :param amount: The amount of layers to rotate
        :return: The move
        """

        return Move(layer, direction, amount)

    return _generate


@pytest.fixture
def generate_previous_moves() -> Callable[[list[Move]], list[Move]]:
    """
    Returns a method to generate previous moves.

    :return: The callable method
    """

    def _generate(moves: list[Move]) -> list[Move]:
        """
        Generates previous moves.

        :param moves: List of moves
        :return: Previous moves
        """
        return moves

    return _generate
