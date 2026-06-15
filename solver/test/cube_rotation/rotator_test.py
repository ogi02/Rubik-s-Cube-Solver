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
from rubik_cube_solver.enums.Rotation import Rotation


class TestRotatorTurn:
    # fmt: off
    @pytest.mark.parametrize(
        "layer, direction, layer_amount", [
            (Layer.UP,    Direction.CW,     1),
            (Layer.FRONT, Direction.CCW,    2),
            (Layer.LEFT,  Direction.DOUBLE, 3),
        ]
    )
    # fmt: on
    def test_success(
        self,
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


class TestRotationEnum:
    # fmt: off
    @pytest.mark.parametrize(
        "rotation, expected_value", [
            (Rotation.X, "x"),
            (Rotation.Y, "y"),
            (Rotation.Z, "z"),
        ]
    )
    # fmt: on
    def test_value(self, rotation: Rotation, expected_value: str) -> None:
        """
        Test that the string value of a Rotation member is correct.

        :param rotation: The Rotation enum member
        :param expected_value: The expected string value
        :return: None
        """
        assert rotation.value == expected_value


class TestRotatorRotate:
    # fmt: off
    @pytest.mark.parametrize(
        "rotation, expected_private_method", [
            (Rotation.X, "_Rotator__rotate_x"),
            (Rotation.Y, "_Rotator__rotate_y"),
            (Rotation.Z, "_Rotator__rotate_z"),
        ]
    )
    # fmt: on
    def test_dispatches_to_correct_axis_handler(
        self,
        generate_cube: Callable[[int], Cube],
        generate_rotator: Callable[[Cube], Rotator],
        rotation: Rotation,
        expected_private_method: str,
    ) -> None:
        """
        Test that rotate() dispatches to the correct private axis handler.

        :param generate_cube: Fixture to generate a cube
        :param generate_rotator: Fixture to generate a rotator
        :param rotation: The rotation axis
        :param expected_private_method: The name-mangled private method to expect
        :return: None
        """
        cube = generate_cube(3)
        rotator = generate_rotator(cube)

        with patch.object(rotator, expected_private_method) as mock_handler:
            rotator.rotate(rotation, 1)
            mock_handler.assert_called_once_with(1)

    # fmt: off
    @pytest.mark.parametrize(
        "invalid_amount", [
            0, 3, -2, 4, -3, 10,
        ]
    )
    # fmt: on
    def test_invalid_amount(
        self,
        generate_cube: Callable[[int], Cube],
        generate_rotator: Callable[[Cube], Rotator],
        invalid_amount: int,
    ) -> None:
        """
        Test that a ValueError is raised for invalid rotation amounts.

        :param generate_cube: Fixture to generate a cube
        :param generate_rotator: Fixture to generate a rotator
        :param invalid_amount: An invalid rotation amount
        :return: None
        """
        cube = generate_cube(3)
        rotator = generate_rotator(cube)

        with pytest.raises(ValueError, match="Invalid rotation amount"):
            rotator.rotate(Rotation.X, invalid_amount)
