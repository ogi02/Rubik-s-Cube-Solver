import pytest

from typing import Callable
from unittest.mock import patch

from src.solver.cube import Cube
from src.solver.cube_rotation.rotator import Rotator
from src.solver.enums.Direction import Direction
from src.solver.enums.Layer import Layer

# -----------------------
# Tests
# -----------------------

@pytest.mark.parametrize("layer, direction, layer_amount", [
    (Layer.UP,    Direction.CW,     1),
    (Layer.FRONT, Direction.CCW,    2),
    (Layer.LEFT,  Direction.DOUBLE, 3),
])
def test_success_turn(generate_cube: Callable[[int], Cube],
                      generate_rotator: Callable[[Cube], Rotator],
                      layer: Layer, direction: Direction, layer_amount: int) -> None:
    """
    Tests the turn method of the Rotator class.

    :param generate_cube: Fixture to generate a cube
    :param generate_rotator: Fixture to generate a rotator
    :param layer: The layer to turn
    :param direction: The direction of the turn
    :param layer_amount: The amount of layers to turn
    :return: None
    """

    # Mock the cube
    cube = generate_cube(3)

    # Mock the rotator class
    rotator = generate_rotator(cube)

    with patch("src.solver.cube_rotation.rotator.rotate_face") as mocked_rotate_face, \
         patch("src.solver.cube_rotation.rotator.rotate_sides") as mocked_rotate_sides:

        # Perform the turn
        rotator.turn(layer, layer_amount, direction)

        # Assert that rotate_face was called once with correct parameters
        mocked_rotate_face.assert_called_once_with(cube, layer, direction)

        # Assert that rotate_sides was called once with correct parameters
        mocked_rotate_sides.assert_called_once_with(cube, layer, direction, layer_amount)
