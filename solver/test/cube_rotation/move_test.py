from typing import Callable

import pytest

from cube_rotation.move import Move
from enums.Direction import Direction
from enums.Layer import Layer


# fmt: off
@pytest.mark.parametrize(
    "layer, direction, layer_amount, move_str", [
        (Layer.UP,    Direction.CW,     1, "U"),
        (Layer.FRONT, Direction.CCW,    2, "Fw'"),
        (Layer.LEFT,  Direction.DOUBLE, 3, "3Lw2"),
    ]
)
# fmt: on
def test_move_str(
    generate_move: Callable[[Layer, Direction, int], Move],
    layer: Layer,
    direction: Direction,
    layer_amount: int,
    move_str: str,
) -> None:
    """
    Tests the turn method of the Rotator class.

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
def test_move_eq(
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
