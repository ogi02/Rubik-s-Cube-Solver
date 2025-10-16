from pickle import FALSE

import pytest

from typing import Callable
from unittest.mock import patch

from src.solver.cube import Cube
from src.solver.enums.Color import Color
from src.solver.enums.Direction import Direction
from src.solver.enums.EdgePosition import EdgePosition
from src.solver.enums.Layer import Layer
import src.solver.cube_rotation.side_stickers_rotation as ssr

# -----------------------
# Tests
# -----------------------

@pytest.mark.parametrize("layer_amount, position, cube_size, expected_edge", [
    (1, EdgePosition.TOP,    3, [Color.WHITE,  Color.YELLOW, Color.ORANGE]),
    (1, EdgePosition.BOTTOM, 3, [Color.WHITE,  Color.YELLOW, Color.ORANGE]),
    (1, EdgePosition.LEFT,   3, [Color.WHITE,  Color.RED,    Color.WHITE]),
    (1, EdgePosition.RIGHT,  3, [Color.ORANGE, Color.BLUE,   Color.ORANGE]),
    (1, EdgePosition.TOP,    2, [Color.WHITE,  Color.YELLOW]),
    (1, EdgePosition.BOTTOM, 2, [Color.ORANGE, Color.RED]),
    (1, EdgePosition.LEFT,   2, [Color.WHITE,  Color.ORANGE]),
    (1, EdgePosition.RIGHT,  2, [Color.YELLOW, Color.RED]),
    (1, EdgePosition.TOP,    5, [Color.WHITE,  Color.YELLOW, Color.ORANGE, Color.RED,    Color.GREEN]),
    (1, EdgePosition.BOTTOM, 5, [Color.ORANGE, Color.RED,    Color.GREEN,  Color.BLUE,   Color.WHITE]),
    (1, EdgePosition.LEFT,   5, [Color.WHITE,  Color.BLUE,   Color.GREEN,  Color.RED,    Color.ORANGE]),
    (1, EdgePosition.RIGHT,  5, [Color.GREEN,  Color.RED,    Color.ORANGE, Color.YELLOW, Color.WHITE]),
    (2, EdgePosition.TOP,    5, [Color.BLUE,   Color.WHITE,  Color.YELLOW, Color.ORANGE, Color.RED]),
    (2, EdgePosition.BOTTOM, 5, [Color.RED,    Color.GREEN,  Color.BLUE,   Color.WHITE,  Color.YELLOW]),
    (2, EdgePosition.LEFT,   5, [Color.YELLOW, Color.WHITE,  Color.BLUE,   Color.GREEN,  Color.RED]),
    (2, EdgePosition.RIGHT,  5, [Color.RED,    Color.ORANGE, Color.YELLOW, Color.WHITE,  Color.BLUE]),
])
def test_success_get_edge(generate_face: Callable[[int], list[Color]],
                          layer_amount: int, position: EdgePosition, cube_size: int,
                          expected_edge: list[Color]) -> None:
    """
    Tests the getter of an edge based on the position.

    :param generate_face: Fixture to generate a face
    :param layer_amount: The amount of layers
    :param position: The position of the edge
    :param cube_size: The size of the cube
    :param expected_edge: The expected edge
    :return: None
    """

    assert ssr.get_edge(generate_face(cube_size), layer_amount, position, cube_size) == expected_edge


@pytest.mark.parametrize("layer_amount, position, cube_size, expected_exception_type, expected_exception", [
    (1, None,             3, ValueError, "Unknown edge position: None"),
    (0, EdgePosition.TOP, 3, ValueError, "Invalid layer amount: 0"),
    (1, EdgePosition.TOP, 0, ValueError, "Invalid cube size: 0")
])
def test_exception_get_edge(generate_face: Callable[[int], list[Color]],
                            layer_amount: int, position: EdgePosition, cube_size: int,
                            expected_exception_type: BaseException.__type_params__, expected_exception: str) -> None:
    """
    Tests that get_edge() raises an exception when the parameters are not valid.

    :param generate_face: Fixture to generate a face
    :param layer_amount: The amount of layers
    :param position: The position of the edge
    :param cube_size: The size of the cube
    :param expected_exception_type: The expected exception type
    :param expected_exception: The expected exception
    :return: None
    """

    with pytest.raises(expected_exception_type, match=expected_exception):
        ssr.get_edge(generate_face(cube_size), layer_amount, position, cube_size)


@pytest.mark.parametrize("layer_amount, position, cube_size, expected_face", [
    (1, EdgePosition.TOP,    3, [Color.WHITE,  Color.YELLOW, Color.ORANGE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE]),
    (1, EdgePosition.BOTTOM, 3, [Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.YELLOW, Color.ORANGE]),
    (1, EdgePosition.LEFT,   3, [Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.YELLOW, Color.WHITE,  Color.WHITE,
                                 Color.ORANGE, Color.WHITE,  Color.WHITE]),
    (1, EdgePosition.RIGHT,  3, [Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.YELLOW,
                                 Color.WHITE,  Color.WHITE,  Color.ORANGE]),
    (1, EdgePosition.TOP,    2, [Color.WHITE,  Color.YELLOW,
                                 Color.WHITE,  Color.WHITE]),
    (1, EdgePosition.BOTTOM, 2, [Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.YELLOW]),
    (1, EdgePosition.LEFT,   2, [Color.WHITE,  Color.WHITE,
                                 Color.YELLOW, Color.WHITE]),
    (1, EdgePosition.RIGHT,  2, [Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.YELLOW]),
    (1, EdgePosition.TOP,    5, [Color.WHITE,  Color.YELLOW, Color.ORANGE, Color.RED,    Color.GREEN,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE]),
    (1, EdgePosition.BOTTOM, 5, [Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.YELLOW, Color.ORANGE, Color.RED,    Color.GREEN]),
    (1, EdgePosition.LEFT,   5, [Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.YELLOW, Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.ORANGE, Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.RED,    Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.GREEN,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE]),
    (1, EdgePosition.RIGHT,  5, [Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.YELLOW,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.ORANGE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.RED,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.GREEN]),
    (2, EdgePosition.TOP,    5, [Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.YELLOW, Color.ORANGE, Color.RED,    Color.GREEN,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE]),
    (2, EdgePosition.BOTTOM, 5, [Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.YELLOW, Color.ORANGE, Color.RED,    Color.GREEN,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE]),
    (2, EdgePosition.LEFT,   5, [Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.YELLOW, Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.ORANGE, Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.RED,    Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.GREEN,  Color.WHITE,  Color.WHITE,  Color.WHITE]),
    (2, EdgePosition.RIGHT,  5, [Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.YELLOW, Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.ORANGE, Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.RED,    Color.WHITE,
                                 Color.WHITE,  Color.WHITE,  Color.WHITE,  Color.GREEN,  Color.WHITE])
])
def test_success_set_edge(generate_one_color_only_face: Callable[[int, Color], list[Color]],
                          generate_edge: Callable[[int], list[Color]],
                          layer_amount: int, position: EdgePosition, cube_size: int,
                          expected_face: list[Color]) -> None:
    """
    Tests the setter of the edge based on the position.

    :param generate_one_color_only_face: Fixture to generate a face with only white stickers
    :param layer_amount: The amount of layers
    :param position: The position of the edge
    :param cube_size: The size of the cube
    :param generate_edge: Fixture to generate an edge with repeating Rubik's colors
    :return: None
    """

    # Mock the face
    actual_face = generate_one_color_only_face(cube_size, Color.WHITE)

    # Set the edge
    ssr.set_edge(actual_face, layer_amount, position, cube_size, generate_edge(cube_size))

    # Assert
    assert actual_face == expected_face


@pytest.mark.parametrize("layer_amount, position, cube_size, expected_exception_type, expected_exception", [
    (1, None,             3, ValueError, "Unknown edge position: None"),
    (0, EdgePosition.TOP, 3, ValueError, "Invalid layer amount: 0"),
    (1, EdgePosition.TOP, 0, ValueError, "Invalid cube size: 0")
])
def test_exception_set_edge(generate_one_color_only_face: Callable[[int, Color], list[Color]],
                            generate_edge: Callable[[int], list[Color]],
                            layer_amount: int, position: EdgePosition, cube_size: int,
                            expected_exception_type: BaseException.__type_params__, expected_exception: str) -> None:
    """
    Tests that get_edge() raises an exception when the parameters are not valid.

    :param generate_one_color_only_face: Fixture to generate a face
    :param generate_edge: Fixture to generate an edge
    :param layer_amount: The amount of layers
    :param position: The position of the edge
    :param cube_size: The size of the cube
    :param expected_exception_type: The expected exception type
    :param expected_exception: The expected exception
    :return: None
    """

    with pytest.raises(expected_exception_type, match=expected_exception):
        face = generate_one_color_only_face(cube_size, Color.WHITE)
        ssr.set_edge(face, layer_amount, position, cube_size, generate_edge(cube_size))


@pytest.mark.parametrize("turned_layer, direction, adj_layer, should_flip_edge", [
    (Layer.UP,    Direction.CW,     Layer.FRONT, False),
    (Layer.UP,    Direction.CCW,    Layer.FRONT, False),
    (Layer.UP,    Direction.DOUBLE, Layer.FRONT, False),
    (Layer.UP,    Direction.CW,     Layer.BACK,  False),
    (Layer.UP,    Direction.CCW,    Layer.BACK,  False),
    (Layer.UP,    Direction.DOUBLE, Layer.BACK,  False),
    (Layer.UP,    Direction.CW,     Layer.LEFT,  False),
    (Layer.UP,    Direction.CCW,    Layer.LEFT,  False),
    (Layer.UP,    Direction.DOUBLE, Layer.LEFT,  False),
    (Layer.UP,    Direction.CW,     Layer.RIGHT, False),
    (Layer.UP,    Direction.CCW,    Layer.RIGHT, False),
    (Layer.UP,    Direction.DOUBLE, Layer.RIGHT, False),
    (Layer.DOWN,  Direction.CW,     Layer.FRONT, False),
    (Layer.DOWN,  Direction.CCW,    Layer.FRONT, False),
    (Layer.DOWN,  Direction.DOUBLE, Layer.FRONT, False),
    (Layer.DOWN,  Direction.CW,     Layer.BACK,  False),
    (Layer.DOWN,  Direction.CCW,    Layer.BACK,  False),
    (Layer.DOWN,  Direction.DOUBLE, Layer.BACK,  False),
    (Layer.DOWN,  Direction.CW,     Layer.LEFT,  False),
    (Layer.DOWN,  Direction.CCW,    Layer.LEFT,  False),
    (Layer.DOWN,  Direction.DOUBLE, Layer.LEFT,  False),
    (Layer.DOWN,  Direction.CW,     Layer.RIGHT, False),
    (Layer.DOWN,  Direction.CCW,    Layer.RIGHT, False),
    (Layer.DOWN,  Direction.DOUBLE, Layer.RIGHT, False),
    (Layer.FRONT, Direction.CW,     Layer.UP,    True),
    (Layer.FRONT, Direction.CCW,    Layer.UP,    False),
    (Layer.FRONT, Direction.DOUBLE, Layer.UP,    True),
    (Layer.FRONT, Direction.CW,     Layer.DOWN,  True),
    (Layer.FRONT, Direction.CCW,    Layer.DOWN,  False),
    (Layer.FRONT, Direction.DOUBLE, Layer.DOWN,  True),
    (Layer.FRONT, Direction.CW,     Layer.LEFT,  False),
    (Layer.FRONT, Direction.CCW,    Layer.LEFT,  True),
    (Layer.FRONT, Direction.DOUBLE, Layer.LEFT,  True),
    (Layer.FRONT, Direction.CW,     Layer.RIGHT, False),
    (Layer.FRONT, Direction.CCW,    Layer.RIGHT, True),
    (Layer.FRONT, Direction.DOUBLE, Layer.RIGHT, True),
    (Layer.BACK,  Direction.CW,     Layer.UP, False),
    (Layer.BACK,  Direction.CCW,    Layer.UP, True),
    (Layer.BACK,  Direction.DOUBLE, Layer.UP, True),
    (Layer.BACK,  Direction.CW,     Layer.DOWN, False),
    (Layer.BACK,  Direction.CCW,    Layer.DOWN, True),
    (Layer.BACK,  Direction.DOUBLE, Layer.DOWN, True),
    (Layer.BACK,  Direction.CW,     Layer.LEFT, True),
    (Layer.BACK,  Direction.CCW,    Layer.LEFT, False),
    (Layer.BACK,  Direction.DOUBLE, Layer.LEFT, True),
    (Layer.BACK,  Direction.CW,     Layer.RIGHT, True),
    (Layer.BACK,  Direction.CCW,    Layer.RIGHT, False),
    (Layer.BACK,  Direction.DOUBLE, Layer.RIGHT, True),
    (Layer.LEFT,  Direction.CW,     Layer.UP,    True),
    (Layer.LEFT,  Direction.CCW,    Layer.UP,    False),
    (Layer.LEFT,  Direction.DOUBLE, Layer.UP,    False),
    (Layer.LEFT,  Direction.CW,     Layer.DOWN,  False),
    (Layer.LEFT,  Direction.CCW,    Layer.DOWN,  True),
    (Layer.LEFT,  Direction.DOUBLE, Layer.DOWN,  False),
    (Layer.LEFT,  Direction.CW,     Layer.FRONT, False),
    (Layer.LEFT,  Direction.CCW,    Layer.FRONT, False),
    (Layer.LEFT,  Direction.DOUBLE, Layer.FRONT, True),
    (Layer.LEFT,  Direction.CW,     Layer.BACK,  True),
    (Layer.LEFT,  Direction.CCW,    Layer.BACK,  True),
    (Layer.LEFT,  Direction.DOUBLE, Layer.BACK,  True),
    (Layer.RIGHT, Direction.CW,     Layer.UP,    False),
    (Layer.RIGHT, Direction.CCW,    Layer.UP,    True),
    (Layer.RIGHT, Direction.DOUBLE, Layer.UP,    False),
    (Layer.RIGHT, Direction.CW,     Layer.DOWN,  True),
    (Layer.RIGHT, Direction.CCW,    Layer.DOWN,  False),
    (Layer.RIGHT, Direction.DOUBLE, Layer.DOWN,  False),
    (Layer.RIGHT, Direction.CW,     Layer.FRONT, False),
    (Layer.RIGHT, Direction.CCW,    Layer.FRONT, False),
    (Layer.RIGHT, Direction.DOUBLE, Layer.FRONT, True),
    (Layer.RIGHT, Direction.CW,     Layer.BACK,  True),
    (Layer.RIGHT, Direction.CCW,    Layer.BACK,  True),
    (Layer.RIGHT, Direction.DOUBLE, Layer.BACK,  True),
])
def test_success_should_flip_edge(turned_layer: Layer, direction: Direction,
                                  adj_layer: Layer, should_flip_edge: bool) -> None:
    """
    Tests whether the edge should be flipped.

    :param turned_layer: The layer that is turned
    :param direction: The direction of the turn
    :param adj_layer: The adjacent layer
    :param should_flip_edge: Whether the edge should be flipped
    :return: None
    """

    assert ssr.should_flip_edge(turned_layer, direction, adj_layer) == should_flip_edge


def test_success_rotate_sides() -> None:
    """
    Tests the rotation of the side stickers.

    :return: None
    """

