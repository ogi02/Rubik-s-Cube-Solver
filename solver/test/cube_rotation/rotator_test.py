# Python imports
from typing import Callable
from unittest.mock import patch

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation


@pytest.fixture
def scrambled_2x2_cube() -> Cube:
    """
    Fixture to return a scrambled 2x2x2 cube.
    Scramble used: R' F R U' F' U2 R

    :return: a scrambled 2x2x2 cube
    """
    # fmt: off
    layers = {
        Layer.UP:    [Color.RED,    Color.WHITE,
                      Color.WHITE,  Color.WHITE],
        Layer.DOWN:  [Color.BLUE,   Color.BLUE,
                      Color.YELLOW, Color.YELLOW],
        Layer.LEFT:  [Color.YELLOW, Color.RED,
                      Color.ORANGE, Color.WHITE],
        Layer.RIGHT: [Color.RED,    Color.ORANGE,
                      Color.RED,    Color.ORANGE],
        Layer.FRONT: [Color.BLUE,   Color.GREEN,
                      Color.ORANGE, Color.YELLOW],
        Layer.BACK:  [Color.GREEN,  Color.GREEN,
                      Color.GREEN,  Color.BLUE],
    }
    # fmt: on
    return Cube(2, layers)


@pytest.fixture
def scrambled_3x3_cube() -> Cube:
    """
    Fixture to return a scrambled 3x3x3 cube.
    Scramble used: D2 L2 B2 L' D2 R' B2 R' U2 L2 F2 D2 F U2 F' R' B' D' F' U' L

    :return: a scrambled 3x3x3 cube
    """
    # fmt: off
    layers = {
        Layer.UP:    [Color.BLUE,   Color.GREEN,  Color.YELLOW,
                      Color.BLUE,   Color.WHITE,  Color.ORANGE,
                      Color.ORANGE, Color.BLUE,   Color.WHITE],
        Layer.DOWN:  [Color.WHITE,  Color.WHITE,  Color.BLUE,
                      Color.BLUE,   Color.YELLOW, Color.RED,
                      Color.BLUE,   Color.WHITE,  Color.RED],
        Layer.LEFT:  [Color.WHITE,  Color.YELLOW, Color.GREEN,
                      Color.GREEN,  Color.ORANGE, Color.WHITE,
                      Color.RED,    Color.WHITE,  Color.BLUE],
        Layer.RIGHT: [Color.RED,    Color.YELLOW, Color.GREEN,
                      Color.BLUE,   Color.RED,    Color.ORANGE,
                      Color.YELLOW, Color.YELLOW, Color.YELLOW],
        Layer.FRONT: [Color.WHITE,  Color.ORANGE, Color.GREEN,
                      Color.ORANGE, Color.GREEN,  Color.RED,
                      Color.RED,    Color.GREEN,  Color.ORANGE],
        Layer.BACK:  [Color.ORANGE, Color.RED,    Color.ORANGE,
                      Color.GREEN,  Color.BLUE,   Color.YELLOW,
                      Color.GREEN,  Color.RED,    Color.YELLOW],
    }
    # fmt: on
    return Cube(3, layers)


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
        "cube_fixture, rotation, direction, expected_layers", [
            ("scrambled_2x2_cube", Rotation.X, Direction.CW, {
                Layer.UP:    [Color.BLUE,   Color.GREEN,
                              Color.ORANGE, Color.YELLOW],
                Layer.DOWN:  [Color.BLUE,   Color.GREEN,
                              Color.GREEN,  Color.GREEN],
                Layer.LEFT:  [Color.RED,    Color.WHITE,
                              Color.YELLOW, Color.ORANGE],
                Layer.RIGHT: [Color.RED,    Color.RED,
                              Color.ORANGE, Color.ORANGE],
                Layer.FRONT: [Color.BLUE,   Color.BLUE,
                              Color.YELLOW, Color.YELLOW],
                Layer.BACK:  [Color.WHITE,  Color.WHITE,
                              Color.WHITE,  Color.RED],
            }),
            ("scrambled_2x2_cube", Rotation.X, Direction.CCW, {
                Layer.UP:    [Color.BLUE,   Color.GREEN,
                              Color.GREEN,  Color.GREEN],
                Layer.DOWN:  [Color.BLUE,   Color.GREEN,
                              Color.ORANGE, Color.YELLOW],
                Layer.LEFT:  [Color.ORANGE, Color.YELLOW,
                              Color.WHITE,  Color.RED],
                Layer.RIGHT: [Color.ORANGE, Color.ORANGE,
                              Color.RED,    Color.RED],
                Layer.FRONT: [Color.RED,    Color.WHITE,
                              Color.WHITE,  Color.WHITE],
                Layer.BACK:  [Color.YELLOW, Color.YELLOW,
                              Color.BLUE,   Color.BLUE],
            }),
            ("scrambled_2x2_cube", Rotation.X, Direction.DOUBLE, {
                Layer.UP:    [Color.BLUE,   Color.BLUE,
                              Color.YELLOW, Color.YELLOW],
                Layer.DOWN:  [Color.RED,    Color.WHITE,
                              Color.WHITE,  Color.WHITE],
                Layer.LEFT:  [Color.WHITE,  Color.ORANGE,
                              Color.RED,    Color.YELLOW],
                Layer.RIGHT: [Color.ORANGE, Color.RED,
                              Color.ORANGE, Color.RED],
                Layer.FRONT: [Color.BLUE,   Color.GREEN,
                              Color.GREEN,  Color.GREEN],
                Layer.BACK:  [Color.YELLOW, Color.ORANGE,
                              Color.GREEN,  Color.BLUE],
            }),
            ("scrambled_2x2_cube", Rotation.Y, Direction.CW, {
                Layer.UP:    [Color.WHITE,  Color.RED,
                              Color.WHITE,  Color.WHITE],
                Layer.DOWN:  [Color.BLUE,   Color.YELLOW,
                              Color.BLUE,   Color.YELLOW],
                Layer.LEFT:  [Color.BLUE,   Color.GREEN,
                              Color.ORANGE, Color.YELLOW],
                Layer.RIGHT: [Color.GREEN,  Color.GREEN,
                              Color.GREEN,  Color.BLUE],
                Layer.FRONT: [Color.RED,    Color.ORANGE,
                              Color.RED,    Color.ORANGE],
                Layer.BACK:  [Color.YELLOW, Color.RED,
                              Color.ORANGE, Color.WHITE],
            }),
            ("scrambled_2x2_cube", Rotation.Y, Direction.CCW, {
                Layer.UP:    [Color.WHITE,  Color.WHITE,
                              Color.RED,    Color.WHITE],
                Layer.DOWN:  [Color.YELLOW, Color.BLUE,
                              Color.YELLOW, Color.BLUE],
                Layer.LEFT:  [Color.GREEN,  Color.GREEN,
                              Color.GREEN,  Color.BLUE],
                Layer.RIGHT: [Color.BLUE,   Color.GREEN,
                              Color.ORANGE, Color.YELLOW],
                Layer.FRONT: [Color.YELLOW, Color.RED,
                              Color.ORANGE, Color.WHITE],
                Layer.BACK:  [Color.RED,    Color.ORANGE,
                              Color.RED,    Color.ORANGE],
            }),
            ("scrambled_2x2_cube", Rotation.Y, Direction.DOUBLE, {
                Layer.UP:    [Color.WHITE, Color.WHITE,
                              Color.WHITE, Color.RED],
                Layer.DOWN:  [Color.YELLOW, Color.YELLOW,
                              Color.BLUE, Color.BLUE],
                Layer.LEFT:  [Color.RED,    Color.ORANGE,
                              Color.RED,    Color.ORANGE],
                Layer.RIGHT: [Color.YELLOW, Color.RED,
                              Color.ORANGE, Color.WHITE],
                Layer.FRONT: [Color.GREEN,  Color.GREEN,
                              Color.GREEN,  Color.BLUE],
                Layer.BACK:  [Color.BLUE,   Color.GREEN,
                              Color.ORANGE, Color.YELLOW],
            }),
            ("scrambled_2x2_cube", Rotation.Z, Direction.CW, {
                Layer.UP:    [Color.ORANGE, Color.YELLOW,
                              Color.WHITE,  Color.RED],
                Layer.DOWN:  [Color.RED,    Color.RED,
                              Color.ORANGE, Color.ORANGE],
                Layer.LEFT:  [Color.YELLOW, Color.BLUE,
                              Color.YELLOW, Color.BLUE],
                Layer.RIGHT: [Color.WHITE,  Color.RED,
                              Color.WHITE,  Color.WHITE],
                Layer.FRONT: [Color.ORANGE, Color.BLUE,
                              Color.YELLOW, Color.GREEN],
                Layer.BACK:  [Color.GREEN,  Color.BLUE,
                              Color.GREEN,  Color.GREEN],
            }),
            ("scrambled_2x2_cube", Rotation.Z, Direction.CCW, {
                Layer.UP: [Color.ORANGE, Color.ORANGE,
                           Color.RED, Color.RED],
                Layer.DOWN: [Color.RED, Color.WHITE,
                             Color.YELLOW, Color.ORANGE],
                Layer.LEFT: [Color.WHITE, Color.WHITE,
                             Color.RED, Color.WHITE],
                Layer.RIGHT: [Color.BLUE, Color.YELLOW,
                              Color.BLUE, Color.YELLOW],
                Layer.FRONT: [Color.GREEN, Color.YELLOW,
                              Color.BLUE, Color.ORANGE],
                Layer.BACK: [Color.GREEN, Color.GREEN,
                             Color.BLUE, Color.GREEN],
            }),
            ("scrambled_2x2_cube", Rotation.Z, Direction.DOUBLE, {
                Layer.UP:    [Color.YELLOW, Color.YELLOW,
                              Color.BLUE,   Color.BLUE],
                Layer.DOWN:  [Color.WHITE,  Color.WHITE,
                              Color.WHITE,  Color.RED],
                Layer.LEFT:  [Color.ORANGE, Color.RED,
                              Color.ORANGE, Color.RED],
                Layer.RIGHT: [Color.WHITE,  Color.ORANGE,
                              Color.RED,    Color.YELLOW],
                Layer.FRONT: [Color.YELLOW, Color.ORANGE,
                              Color.GREEN,  Color.BLUE],
                Layer.BACK:  [Color.BLUE,   Color.GREEN,
                              Color.GREEN,  Color.GREEN],
            }),
            ("scrambled_3x3_cube", Rotation.X, Direction.CW, {
                Layer.UP:    [Color.WHITE,  Color.ORANGE, Color.GREEN,
                              Color.ORANGE, Color.GREEN,  Color.RED,
                              Color.RED,    Color.GREEN,  Color.ORANGE],
                Layer.DOWN:  [Color.YELLOW, Color.RED,    Color.GREEN,
                              Color.YELLOW, Color.BLUE,   Color.GREEN,
                              Color.ORANGE, Color.RED,    Color.ORANGE],
                Layer.LEFT:  [Color.GREEN,  Color.WHITE,  Color.BLUE,
                              Color.YELLOW, Color.ORANGE, Color.WHITE,
                              Color.WHITE,  Color.GREEN,  Color.RED],
                Layer.RIGHT: [Color.YELLOW, Color.BLUE,   Color.RED,
                              Color.YELLOW, Color.RED,    Color.YELLOW,
                              Color.YELLOW, Color.ORANGE, Color.GREEN],
                Layer.FRONT: [Color.WHITE,  Color.WHITE,  Color.BLUE,
                              Color.BLUE,   Color.YELLOW, Color.RED,
                              Color.BLUE,   Color.WHITE,  Color.RED],
                Layer.BACK:  [Color.WHITE,  Color.BLUE,   Color.ORANGE,
                              Color.ORANGE, Color.WHITE,  Color.BLUE,
                              Color.YELLOW, Color.GREEN,  Color.BLUE],
            }),
            ("scrambled_3x3_cube", Rotation.X, Direction.CCW, {
                Layer.UP:    [Color.YELLOW, Color.RED,    Color.GREEN,
                              Color.YELLOW, Color.BLUE,   Color.GREEN,
                              Color.ORANGE, Color.RED,    Color.ORANGE],
                Layer.DOWN:  [Color.WHITE,  Color.ORANGE, Color.GREEN,
                              Color.ORANGE, Color.GREEN,  Color.RED,
                              Color.RED,    Color.GREEN,  Color.ORANGE],
                Layer.LEFT:  [Color.RED,    Color.GREEN,  Color.WHITE,
                              Color.WHITE,  Color.ORANGE, Color.YELLOW,
                              Color.BLUE,   Color.WHITE,  Color.GREEN],
                Layer.RIGHT: [Color.GREEN,  Color.ORANGE, Color.YELLOW,
                              Color.YELLOW, Color.RED,    Color.YELLOW,
                              Color.RED,    Color.BLUE,   Color.YELLOW],
                Layer.FRONT: [Color.BLUE,   Color.GREEN,  Color.YELLOW,
                              Color.BLUE,   Color.WHITE,  Color.ORANGE,
                              Color.ORANGE, Color.BLUE,   Color.WHITE],
                Layer.BACK:  [Color.RED,    Color.WHITE,  Color.BLUE,
                              Color.RED,    Color.YELLOW, Color.BLUE,
                              Color.BLUE,   Color.WHITE,  Color.WHITE],
            }),
            ("scrambled_3x3_cube", Rotation.X, Direction.DOUBLE, {
                Layer.UP:    [Color.WHITE,  Color.WHITE,  Color.BLUE,
                              Color.BLUE,   Color.YELLOW, Color.RED,
                              Color.BLUE,   Color.WHITE,  Color.RED],
                Layer.DOWN:  [Color.BLUE,   Color.GREEN,  Color.YELLOW,
                              Color.BLUE,   Color.WHITE,  Color.ORANGE,
                              Color.ORANGE, Color.BLUE,   Color.WHITE],
                Layer.LEFT:  [Color.BLUE,   Color.WHITE,  Color.RED,
                              Color.WHITE,  Color.ORANGE, Color.GREEN,
                              Color.GREEN,  Color.YELLOW, Color.WHITE],
                Layer.RIGHT: [Color.YELLOW, Color.YELLOW, Color.YELLOW,
                              Color.ORANGE, Color.RED,    Color.BLUE,
                              Color.GREEN,  Color.YELLOW, Color.RED],
                Layer.FRONT: [Color.YELLOW, Color.RED,    Color.GREEN,
                              Color.YELLOW, Color.BLUE,   Color.GREEN,
                              Color.ORANGE, Color.RED,    Color.ORANGE],
                Layer.BACK:  [Color.ORANGE, Color.GREEN,  Color.RED,
                              Color.RED,    Color.GREEN,  Color.ORANGE,
                              Color.GREEN,  Color.ORANGE, Color.WHITE],
            }),
            ("scrambled_3x3_cube", Rotation.Y, Direction.CW, {
                Layer.UP:    [Color.ORANGE, Color.BLUE,   Color.BLUE,
                              Color.BLUE,   Color.WHITE,  Color.GREEN,
                              Color.WHITE,  Color.ORANGE, Color.YELLOW],
                Layer.DOWN:  [Color.BLUE,   Color.RED,    Color.RED,
                              Color.WHITE,  Color.YELLOW, Color.WHITE,
                              Color.WHITE,  Color.BLUE,   Color.BLUE],
                Layer.LEFT:  [Color.WHITE, Color.ORANGE, Color.GREEN,
                              Color.ORANGE, Color.GREEN,  Color.RED,
                              Color.RED,    Color.GREEN,  Color.ORANGE],
                Layer.RIGHT: [Color.ORANGE, Color.RED,    Color.ORANGE,
                              Color.GREEN,  Color.BLUE,   Color.YELLOW,
                              Color.GREEN,  Color.RED,    Color.YELLOW],
                Layer.FRONT: [Color.RED,    Color.YELLOW, Color.GREEN,
                              Color.BLUE,   Color.RED,    Color.ORANGE,
                              Color.YELLOW, Color.YELLOW, Color.YELLOW],
                Layer.BACK:  [Color.WHITE,  Color.YELLOW, Color.GREEN,
                              Color.GREEN,  Color.ORANGE, Color.WHITE,
                              Color.RED,    Color.WHITE,  Color.BLUE],
            }),
            ("scrambled_3x3_cube", Rotation.Y, Direction.CCW, {
                Layer.UP:    [Color.YELLOW, Color.ORANGE, Color.WHITE,
                              Color.GREEN,  Color.WHITE,  Color.BLUE,
                              Color.BLUE,   Color.BLUE,   Color.ORANGE],
                Layer.DOWN:  [Color.BLUE,   Color.BLUE,   Color.WHITE,
                              Color.WHITE,  Color.YELLOW, Color.WHITE,
                              Color.RED,    Color.RED,    Color.BLUE],
                Layer.LEFT:  [Color.ORANGE, Color.RED,    Color.ORANGE,
                              Color.GREEN,  Color.BLUE,   Color.YELLOW,
                              Color.GREEN,  Color.RED,    Color.YELLOW],
                Layer.RIGHT: [Color.WHITE,  Color.ORANGE, Color.GREEN,
                              Color.ORANGE, Color.GREEN,  Color.RED,
                              Color.RED,    Color.GREEN,  Color.ORANGE],
                Layer.FRONT: [Color.WHITE,  Color.YELLOW, Color.GREEN,
                              Color.GREEN,  Color.ORANGE, Color.WHITE,
                              Color.RED,    Color.WHITE,  Color.BLUE],
                Layer.BACK:  [Color.RED,    Color.YELLOW, Color.GREEN,
                              Color.BLUE,   Color.RED,    Color.ORANGE,
                              Color.YELLOW, Color.YELLOW, Color.YELLOW],
            }),
            ("scrambled_3x3_cube", Rotation.Y, Direction.DOUBLE, {
                Layer.UP:    [Color.WHITE,  Color.BLUE,   Color.ORANGE,
                              Color.ORANGE, Color.WHITE,  Color.BLUE,
                              Color.YELLOW, Color.GREEN,  Color.BLUE],
                Layer.DOWN:  [Color.RED,    Color.WHITE,  Color.BLUE,
                              Color.RED,    Color.YELLOW, Color.BLUE,
                              Color.BLUE,   Color.WHITE,  Color.WHITE],
                Layer.LEFT:  [Color.RED,    Color.YELLOW, Color.GREEN,
                              Color.BLUE,   Color.RED,    Color.ORANGE,
                              Color.YELLOW, Color.YELLOW, Color.YELLOW],
                Layer.RIGHT: [Color.WHITE,  Color.YELLOW, Color.GREEN,
                              Color.GREEN,  Color.ORANGE, Color.WHITE,
                              Color.RED,    Color.WHITE,  Color.BLUE],
                Layer.FRONT: [Color.ORANGE, Color.RED,    Color.ORANGE,
                              Color.GREEN,  Color.BLUE,   Color.YELLOW,
                              Color.GREEN,  Color.RED,    Color.YELLOW],
                Layer.BACK:  [Color.WHITE,  Color.ORANGE, Color.GREEN,
                              Color.ORANGE, Color.GREEN,  Color.RED,
                              Color.RED,    Color.GREEN,  Color.ORANGE],
            }),
            ("scrambled_3x3_cube", Rotation.Z, Direction.CW, {
                Layer.UP:    [Color.RED,    Color.GREEN,  Color.WHITE,
                              Color.WHITE,  Color.ORANGE, Color.YELLOW,
                              Color.BLUE,   Color.WHITE,  Color.GREEN],
                Layer.DOWN:  [Color.YELLOW, Color.BLUE,   Color.RED,
                              Color.YELLOW, Color.RED,    Color.YELLOW,
                              Color.YELLOW, Color.ORANGE, Color.GREEN],
                Layer.LEFT:  [Color.BLUE,   Color.BLUE,   Color.WHITE,
                              Color.WHITE,  Color.YELLOW, Color.WHITE,
                              Color.RED,    Color.RED,    Color.BLUE],
                Layer.RIGHT: [Color.ORANGE, Color.BLUE,   Color.BLUE,
                              Color.BLUE,   Color.WHITE,  Color.GREEN,
                              Color.WHITE,  Color.ORANGE, Color.YELLOW],
                Layer.FRONT: [Color.RED,    Color.ORANGE, Color.WHITE,
                              Color.GREEN,  Color.GREEN,  Color.ORANGE,
                              Color.ORANGE, Color.RED,    Color.GREEN],
                Layer.BACK:  [Color.ORANGE, Color.YELLOW, Color.YELLOW,
                              Color.RED,    Color.BLUE,   Color.RED,
                              Color.ORANGE, Color.GREEN,  Color.GREEN,],
            }),
            ("scrambled_3x3_cube", Rotation.Z, Direction.CCW, {
                Layer.UP:    [Color.GREEN,  Color.ORANGE, Color.YELLOW,
                              Color.YELLOW, Color.RED,    Color.YELLOW,
                              Color.RED,    Color.BLUE,   Color.YELLOW],
                Layer.DOWN:  [Color.GREEN,  Color.WHITE,  Color.BLUE,
                              Color.YELLOW, Color.ORANGE, Color.WHITE,
                              Color.WHITE,  Color.GREEN,  Color.RED],
                Layer.LEFT:  [Color.YELLOW, Color.ORANGE, Color.WHITE,
                              Color.GREEN,  Color.WHITE,  Color.BLUE,
                              Color.BLUE,   Color.BLUE,   Color.ORANGE],
                Layer.RIGHT: [Color.BLUE,   Color.RED,    Color.RED,
                              Color.WHITE,  Color.YELLOW, Color.WHITE,
                              Color.WHITE,  Color.BLUE,   Color.BLUE],
                Layer.FRONT: [Color.GREEN,  Color.RED,    Color.ORANGE,
                              Color.ORANGE, Color.GREEN,  Color.GREEN,
                              Color.WHITE,  Color.ORANGE, Color.RED],
                Layer.BACK:  [Color.GREEN,  Color.GREEN,  Color.ORANGE,
                              Color.RED,    Color.BLUE,   Color.RED,
                              Color.YELLOW, Color.YELLOW, Color.ORANGE],
            }),
            ("scrambled_3x3_cube", Rotation.Z, Direction.DOUBLE, {
                Layer.UP:    [Color.RED,    Color.WHITE,  Color.BLUE,
                              Color.RED,    Color.YELLOW, Color.BLUE,
                              Color.BLUE,   Color.WHITE,  Color.WHITE],
                Layer.DOWN:  [Color.WHITE,  Color.BLUE,   Color.ORANGE,
                              Color.ORANGE, Color.WHITE,  Color.BLUE,
                              Color.YELLOW, Color.GREEN,  Color.BLUE],
                Layer.LEFT:  [Color.YELLOW, Color.YELLOW, Color.YELLOW,
                              Color.ORANGE, Color.RED,    Color.BLUE,
                              Color.GREEN,  Color.YELLOW, Color.RED],
                Layer.RIGHT: [Color.BLUE,   Color.WHITE,  Color.RED,
                              Color.WHITE,  Color.ORANGE, Color.GREEN,
                              Color.GREEN,  Color.YELLOW, Color.WHITE],
                Layer.FRONT: [Color.ORANGE, Color.GREEN,  Color.RED,
                              Color.RED,    Color.GREEN,  Color.ORANGE,
                              Color.GREEN,  Color.ORANGE, Color.WHITE],
                Layer.BACK:  [Color.YELLOW, Color.RED,    Color.GREEN,
                              Color.YELLOW, Color.BLUE,   Color.GREEN,
                              Color.ORANGE, Color.RED,    Color.ORANGE],
            }),
        ]
    )
    # fmt: on
    def test_success(
        self,
        request: pytest.FixtureRequest,
        cube_fixture: str,
        rotation: Rotation,
        direction: Direction,
        expected_layers: dict[Layer, list[Color]],
        generate_rotator: Callable[[Cube], Rotator],
    ) -> None:
        """
        Test that rotate() dispatches to the correct private axis handler.

        :param request: The request fixture
        :param cube_fixture: Fixture to generate a scrambled cube
        :param rotation: The rotation axis
        :param direction: The direction of the rotation
        :param expected_layers: The expected layers after the rotation
        :param generate_rotator: Fixture to generate a rotator
        :return: None
        """

        cube = request.getfixturevalue(cube_fixture)
        rotator = generate_rotator(cube)
        rotator.rotate(rotation, direction)

        assert cube.layers == expected_layers
