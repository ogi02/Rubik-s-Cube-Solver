# Python imports
from typing import Callable
from unittest.mock import patch

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer


# fmt: off
@pytest.mark.parametrize(
    "layer, direction, layer_amount", [
        (Layer.UP,    Direction.CW,     1),
        (Layer.FRONT, Direction.CCW,    2),
        (Layer.LEFT,  Direction.DOUBLE, 3),
    ]
)
# fmt: on
def test_turn_success(
    generate_cube: Callable[[int], Cube],
    generate_rotator: Callable[[Cube], Rotator],
    generate_move: Callable[[Layer, Direction, int], Move],
    layer: Layer,
    direction: Direction,
    layer_amount: int,
) -> None:
    """
    Tests the turn method of the Rotator class.

    :param generate_cube: Fixture to generate a cube
    :param generate_rotator: Fixture to generate a rotator
    :param generate_move: Fixture to generate a move
    :param layer: The layer to turn
    :param direction: The direction of the turn
    :param layer_amount: The amount of layers to turn
    :return: None
    """

    # Mock the cube
    cube = generate_cube(3)

    # Mock the rotator class
    rotator = generate_rotator(cube)

    # Mock the move
    move = generate_move(layer, direction, layer_amount)

    with (
        patch("rubik_cube_solver.cube_rotation.rotator.rotate_face") as mocked_rotate_face,
        patch("rubik_cube_solver.cube_rotation.rotator.rotate_sides") as mocked_rotate_sides,
    ):

        # Perform the turn
        rotator.turn(move)

        # Assert that rotate_face was called once with correct parameters
        mocked_rotate_face.assert_called_once_with(cube, layer, direction)

        # Assert that rotate_sides was called once with correct parameters
        mocked_rotate_sides.assert_called_once_with(cube, layer, direction, layer_amount)
