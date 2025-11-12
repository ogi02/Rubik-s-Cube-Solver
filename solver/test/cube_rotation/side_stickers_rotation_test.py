from typing import Callable
from unittest.mock import call, patch

import pytest

import rubik_cube_solver.cube_rotation.side_stickers_rotation as ssr
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.EdgePosition import EdgePosition
from rubik_cube_solver.enums.Layer import Layer


# fmt: off
@pytest.mark.parametrize(
    "layer_amount, position, cube_size, expected_edge", [
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
    ]
)
# fmt: on
def test_get_edge_success(
    generate_face: Callable[[int], list[Color]],
    layer_amount: int,
    position: EdgePosition,
    cube_size: int,
    expected_edge: list[Color],
) -> None:
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


# fmt: off
@pytest.mark.parametrize(
    "layer_amount, position, cube_size, expected_exception_type, expected_exception", [
        (1, None,             3, ValueError, "Unknown edge position: None"),
        (0, EdgePosition.TOP, 3, ValueError, "Invalid layer amount: 0"),
        (1, EdgePosition.TOP, 0, ValueError, "Invalid cube size: 0")
    ]
)
# fmt: on
def test_get_edge_exception(
    generate_face: Callable[[int], list[Color]],
    layer_amount: int,
    position: EdgePosition,
    cube_size: int,
    expected_exception_type: type[BaseException],
    expected_exception: str,
) -> None:
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


# fmt: off
@pytest.mark.parametrize(
    "layer_amount, position, cube_size, expected_face", [
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
    ]
)
# fmt: on
def test_set_edge_success(
    generate_one_color_only_face: Callable[[int, Color], list[Color]],
    generate_edge: Callable[[int], list[Color]],
    layer_amount: int,
    position: EdgePosition,
    cube_size: int,
    expected_face: list[Color],
) -> None:
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


# fmt: off
@pytest.mark.parametrize(
    "layer_amount, position, cube_size, expected_exception_type, expected_exception", [
        (1, None,             3, ValueError, "Unknown edge position: None"),
        (0, EdgePosition.TOP, 3, ValueError, "Invalid layer amount: 0"),
        (1, EdgePosition.TOP, 0, ValueError, "Invalid cube size: 0")
    ]
)
# fmt: on
def test_set_edge_exception(
    generate_one_color_only_face: Callable[[int, Color], list[Color]],
    generate_edge: Callable[[int], list[Color]],
    layer_amount: int,
    position: EdgePosition,
    cube_size: int,
    expected_exception_type: type[BaseException],
    expected_exception: str,
) -> None:
    """
    Tests that set_edge() raises an exception when the parameters are not valid.

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


# fmt: off
@pytest.mark.parametrize(
    "turned_layer, direction, adj_layer, should_flip_edge", [
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
    ]
)
# fmt: on
def test_should_flip_edge_success(
    turned_layer: Layer, direction: Direction, adj_layer: Layer, should_flip_edge: bool
) -> None:
    """
    Tests whether the edge should be flipped.

    :param turned_layer: The layer that is turned
    :param direction: The direction of the turn
    :param adj_layer: The adjacent layer
    :param should_flip_edge: Whether the edge should be flipped
    :return: None
    """

    assert ssr.should_flip_edge(turned_layer, direction, adj_layer) == should_flip_edge


# fmt: off
@pytest.mark.parametrize(
    "cube_size, turned_layer, direction, layer_amount, original_edges", [
        (3, Layer.UP,    Direction.CW,     1, [Color.BLUE,  Color.RED,    Color.GREEN,  Color.ORANGE]),
        (3, Layer.UP,    Direction.CCW,    1, [Color.BLUE,  Color.RED,    Color.GREEN,  Color.ORANGE]),
        (3, Layer.UP,    Direction.DOUBLE, 1, [Color.BLUE,  Color.RED,    Color.GREEN,  Color.ORANGE]),
        (3, Layer.DOWN,  Direction.CW,     1, [Color.GREEN, Color.RED,    Color.BLUE,   Color.ORANGE]),
        (3, Layer.DOWN,  Direction.CCW,    1, [Color.GREEN, Color.RED,    Color.BLUE,   Color.ORANGE]),
        (3, Layer.DOWN,  Direction.DOUBLE, 1, [Color.GREEN, Color.RED,    Color.BLUE,   Color.ORANGE]),
        (3, Layer.FRONT, Direction.CW,     1, [Color.WHITE, Color.RED,    Color.YELLOW, Color.ORANGE]),
        (3, Layer.FRONT, Direction.CCW,    1, [Color.WHITE, Color.RED,    Color.YELLOW, Color.ORANGE]),
        (3, Layer.FRONT, Direction.DOUBLE, 1, [Color.WHITE, Color.RED,    Color.YELLOW, Color.ORANGE]),
        (3, Layer.BACK,  Direction.CW,     1, [Color.WHITE, Color.ORANGE, Color.YELLOW, Color.RED]),
        (3, Layer.BACK,  Direction.CCW,    1, [Color.WHITE, Color.ORANGE, Color.YELLOW, Color.RED]),
        (3, Layer.BACK,  Direction.DOUBLE, 1, [Color.WHITE, Color.ORANGE, Color.YELLOW, Color.RED]),
        (3, Layer.LEFT,  Direction.CW,     1, [Color.WHITE, Color.GREEN,  Color.YELLOW, Color.BLUE]),
        (3, Layer.LEFT,  Direction.CCW,    1, [Color.WHITE, Color.GREEN,  Color.YELLOW, Color.BLUE]),
        (3, Layer.LEFT,  Direction.DOUBLE, 1, [Color.WHITE, Color.GREEN,  Color.YELLOW, Color.BLUE]),
        (3, Layer.RIGHT, Direction.CW,     1, [Color.WHITE, Color.BLUE,   Color.YELLOW, Color.GREEN]),
        (3, Layer.RIGHT, Direction.CCW,    1, [Color.WHITE, Color.BLUE,   Color.YELLOW, Color.GREEN]),
        (3, Layer.RIGHT, Direction.DOUBLE, 1, [Color.WHITE, Color.BLUE,   Color.YELLOW, Color.GREEN]),
        (2, Layer.UP,    Direction.CW,     1, [Color.BLUE,  Color.RED,    Color.GREEN,  Color.ORANGE]),
        (2, Layer.UP,    Direction.CCW,    1, [Color.BLUE,  Color.RED,    Color.GREEN,  Color.ORANGE]),
        (2, Layer.UP,    Direction.DOUBLE, 1, [Color.BLUE,  Color.RED,    Color.GREEN,  Color.ORANGE]),
        (2, Layer.DOWN,  Direction.CW,     1, [Color.GREEN, Color.RED,    Color.BLUE,   Color.ORANGE]),
        (2, Layer.DOWN,  Direction.CCW,    1, [Color.GREEN, Color.RED,    Color.BLUE,   Color.ORANGE]),
        (2, Layer.DOWN,  Direction.DOUBLE, 1, [Color.GREEN, Color.RED,    Color.BLUE,   Color.ORANGE]),
        (2, Layer.FRONT, Direction.CW,     1, [Color.WHITE, Color.RED,    Color.YELLOW, Color.ORANGE]),
        (2, Layer.FRONT, Direction.CCW,    1, [Color.WHITE, Color.RED,    Color.YELLOW, Color.ORANGE]),
        (2, Layer.FRONT, Direction.DOUBLE, 1, [Color.WHITE, Color.RED,    Color.YELLOW, Color.ORANGE]),
        (2, Layer.BACK,  Direction.CW,     1, [Color.WHITE, Color.ORANGE, Color.YELLOW, Color.RED]),
        (2, Layer.BACK,  Direction.CCW,    1, [Color.WHITE, Color.ORANGE, Color.YELLOW, Color.RED]),
        (2, Layer.BACK,  Direction.DOUBLE, 1, [Color.WHITE, Color.ORANGE, Color.YELLOW, Color.RED]),
        (2, Layer.LEFT,  Direction.CW,     1, [Color.WHITE, Color.GREEN,  Color.YELLOW, Color.BLUE]),
        (2, Layer.LEFT,  Direction.CCW,    1, [Color.WHITE, Color.GREEN,  Color.YELLOW, Color.BLUE]),
        (2, Layer.LEFT,  Direction.DOUBLE, 1, [Color.WHITE, Color.GREEN,  Color.YELLOW, Color.BLUE]),
        (2, Layer.RIGHT, Direction.CW,     1, [Color.WHITE, Color.BLUE,   Color.YELLOW, Color.GREEN]),
        (2, Layer.RIGHT, Direction.CCW,    1, [Color.WHITE, Color.BLUE,   Color.YELLOW, Color.GREEN]),
        (2, Layer.RIGHT, Direction.DOUBLE, 1, [Color.WHITE, Color.BLUE,   Color.YELLOW, Color.GREEN]),
        (5, Layer.UP,    Direction.CW,     1, [Color.BLUE,  Color.RED,    Color.GREEN,  Color.ORANGE]),
        (5, Layer.UP,    Direction.CCW,    1, [Color.BLUE,  Color.RED,    Color.GREEN,  Color.ORANGE]),
        (5, Layer.UP,    Direction.DOUBLE, 1, [Color.BLUE,  Color.RED,    Color.GREEN,  Color.ORANGE]),
        (5, Layer.DOWN,  Direction.CW,     1, [Color.GREEN, Color.RED,    Color.BLUE,   Color.ORANGE]),
        (5, Layer.DOWN,  Direction.CCW,    1, [Color.GREEN, Color.RED,    Color.BLUE,   Color.ORANGE]),
        (5, Layer.DOWN,  Direction.DOUBLE, 1, [Color.GREEN, Color.RED,    Color.BLUE,   Color.ORANGE]),
        (5, Layer.FRONT, Direction.CW,     1, [Color.WHITE, Color.RED,    Color.YELLOW, Color.ORANGE]),
        (5, Layer.FRONT, Direction.CCW,    1, [Color.WHITE, Color.RED,    Color.YELLOW, Color.ORANGE]),
        (5, Layer.FRONT, Direction.DOUBLE, 1, [Color.WHITE, Color.RED,    Color.YELLOW, Color.ORANGE]),
        (5, Layer.BACK,  Direction.CW,     1, [Color.WHITE, Color.ORANGE, Color.YELLOW, Color.RED]),
        (5, Layer.BACK,  Direction.CCW,    1, [Color.WHITE, Color.ORANGE, Color.YELLOW, Color.RED]),
        (5, Layer.BACK,  Direction.DOUBLE, 1, [Color.WHITE, Color.ORANGE, Color.YELLOW, Color.RED]),
        (5, Layer.LEFT,  Direction.CW,     1, [Color.WHITE, Color.GREEN,  Color.YELLOW, Color.BLUE]),
        (5, Layer.LEFT,  Direction.CCW,    1, [Color.WHITE, Color.GREEN,  Color.YELLOW, Color.BLUE]),
        (5, Layer.LEFT,  Direction.DOUBLE, 1, [Color.WHITE, Color.GREEN,  Color.YELLOW, Color.BLUE]),
        (5, Layer.RIGHT, Direction.CW,     1, [Color.WHITE, Color.BLUE,   Color.YELLOW, Color.GREEN]),
        (5, Layer.RIGHT, Direction.CCW,    1, [Color.WHITE, Color.BLUE,   Color.YELLOW, Color.GREEN]),
        (5, Layer.RIGHT, Direction.DOUBLE, 1, [Color.WHITE, Color.BLUE,   Color.YELLOW, Color.GREEN]),
        (5, Layer.UP,    Direction.CW,     2, [Color.BLUE,  Color.RED,    Color.GREEN,  Color.ORANGE]),
        (5, Layer.UP,    Direction.CCW,    2, [Color.BLUE,  Color.RED,    Color.GREEN,  Color.ORANGE]),
        (5, Layer.UP,    Direction.DOUBLE, 2, [Color.BLUE,  Color.RED,    Color.GREEN,  Color.ORANGE]),
        (5, Layer.DOWN,  Direction.CW,     2, [Color.GREEN, Color.RED,    Color.BLUE,   Color.ORANGE]),
        (5, Layer.DOWN,  Direction.CCW,    2, [Color.GREEN, Color.RED,    Color.BLUE,   Color.ORANGE]),
        (5, Layer.DOWN,  Direction.DOUBLE, 2, [Color.GREEN, Color.RED,    Color.BLUE,   Color.ORANGE]),
        (5, Layer.FRONT, Direction.CW,     2, [Color.WHITE, Color.RED,    Color.YELLOW, Color.ORANGE]),
        (5, Layer.FRONT, Direction.CCW,    2, [Color.WHITE, Color.RED,    Color.YELLOW, Color.ORANGE]),
        (5, Layer.FRONT, Direction.DOUBLE, 2, [Color.WHITE, Color.RED,    Color.YELLOW, Color.ORANGE]),
        (5, Layer.BACK,  Direction.CW,     2, [Color.WHITE, Color.ORANGE, Color.YELLOW, Color.RED]),
        (5, Layer.BACK,  Direction.CCW,    2, [Color.WHITE, Color.ORANGE, Color.YELLOW, Color.RED]),
        (5, Layer.BACK,  Direction.DOUBLE, 2, [Color.WHITE, Color.ORANGE, Color.YELLOW, Color.RED]),
        (5, Layer.LEFT,  Direction.CW,     2, [Color.WHITE, Color.GREEN,  Color.YELLOW, Color.BLUE]),
        (5, Layer.LEFT,  Direction.CCW,    2, [Color.WHITE, Color.GREEN,  Color.YELLOW, Color.BLUE]),
        (5, Layer.LEFT,  Direction.DOUBLE, 2, [Color.WHITE, Color.GREEN,  Color.YELLOW, Color.BLUE]),
        (5, Layer.RIGHT, Direction.CW,     2, [Color.WHITE, Color.BLUE,   Color.YELLOW, Color.GREEN]),
        (5, Layer.RIGHT, Direction.CCW,    2, [Color.WHITE, Color.BLUE,   Color.YELLOW, Color.GREEN]),
        (5, Layer.RIGHT, Direction.DOUBLE, 2, [Color.WHITE, Color.BLUE,   Color.YELLOW, Color.GREEN])
    ]
)
# fmt: on
def test_rotate_sides_success(
    generate_cube: Callable[[int], Cube],
    generate_one_color_only_edge: Callable[[int, Color], list[Color]],
    generate_one_color_only_face: Callable[[int, Color], list[Color]],
    get_adjacent_edge: Callable[[Layer], list[tuple[Layer, EdgePosition]]],
    cube_size: int,
    turned_layer: Layer,
    direction: Direction,
    layer_amount: int,
    original_edges: list[list[Color]],
) -> None:
    """
    Tests the rotation of the side stickers.

    :param generate_cube: Fixture to generate a cube
    :param generate_one_color_only_edge: Fixture to generate an edge with only one color
    :param generate_one_color_only_face: Fixture to generate a face with only one color
    :param get_adjacent_edge: Fixture to get the adjacent edges
    :param cube_size: The size of the cube
    :param turned_layer: The layer that is turned
    :param direction: The direction of the turn
    :param layer_amount: The amount of layers
    :return: None
    """

    # Mock the cube
    cube = generate_cube(cube_size)
    cube.layers = {
        Layer.UP: generate_one_color_only_face(cube_size, Color.WHITE),
        Layer.DOWN: generate_one_color_only_face(cube_size, Color.YELLOW),
        Layer.FRONT: generate_one_color_only_face(cube_size, Color.GREEN),
        Layer.BACK: generate_one_color_only_face(cube_size, Color.BLUE),
        Layer.LEFT: generate_one_color_only_face(cube_size, Color.ORANGE),
        Layer.RIGHT: generate_one_color_only_face(cube_size, Color.RED),
    }

    # Prepare all expected calls before the loop
    expected_calls_get_edge_method = []
    expected_calls_should_flip_edge_method = []
    expected_calls_set_edge_method = []
    rotated_edges = []

    # Multiply original edges for all layers
    original_edges = [
        [original_edges[0]] * cube_size,
        [original_edges[1]] * cube_size,
        [original_edges[2]] * cube_size,
        [original_edges[3]] * cube_size,
    ]

    for layer_index in range(1, layer_amount + 1):
        # Adjacent edges for this layer
        adjacent_edges = get_adjacent_edge(turned_layer)

        # Rotated edges for this layer
        if direction == Direction.CW:
            rotated_edges = [original_edges[3], original_edges[0], original_edges[1], original_edges[2]]
        elif direction == Direction.CCW:
            rotated_edges = [original_edges[1], original_edges[2], original_edges[3], original_edges[0]]
        elif direction == Direction.DOUBLE:
            rotated_edges = [original_edges[2], original_edges[3], original_edges[0], original_edges[1]]

        # Append expected calls for all layers
        for i in range(4):
            adjacent_layer, position = adjacent_edges[i]
            expected_calls_get_edge_method.append(
                # Params: face, layer amount, position, cube size
                call(cube.layers[adjacent_layer], layer_index, position, cube.size)
            )
            expected_calls_should_flip_edge_method.append(
                # Params: turned layer, direction, adjacent layer
                call(turned_layer, direction, adjacent_layer)
            )
            expected_calls_set_edge_method.append(
                # Params: face, layer amount, position, cube size, rotated edge
                call(cube.layers[adjacent_layer], layer_index, position, cube.size, rotated_edges[i])
            )

        print(expected_calls_get_edge_method)
        print(expected_calls_should_flip_edge_method)
        print(expected_calls_set_edge_method)

    # Patch
    with (
        patch("rubik_cube_solver.cube_rotation.side_stickers_rotation.get_edge") as mock_get_edge,
        patch("rubik_cube_solver.cube_rotation.side_stickers_rotation.should_flip_edge") as mock_should_flip_edge,
        patch("rubik_cube_solver.cube_rotation.side_stickers_rotation.set_edge") as mock_set_edge,
    ):

        # Mock get_edge() return values for all calls
        mock_get_edge.side_effect = original_edges * layer_amount

        # Call the method under test
        ssr.rotate_sides(cube, turned_layer, direction, layer_amount)

        # Assert calls across all layers
        assert mock_get_edge.call_args_list == expected_calls_get_edge_method
        assert mock_get_edge.call_count == 4 * layer_amount

        assert mock_should_flip_edge.call_args_list == expected_calls_should_flip_edge_method
        assert mock_should_flip_edge.call_count == 4 * layer_amount

        assert mock_set_edge.call_args_list == expected_calls_set_edge_method
        assert mock_set_edge.call_count == 4 * layer_amount


# fmt: off
@pytest.mark.parametrize(
    "cube_size, turned_layer, direction, layer_amount, expected_exception_type, expected_exception",
    [
        (3, Layer.UP, Direction.CW, 2, ValueError, "Cube size 3 is too small to rotate 2 layers"),
        (3, Layer.UP, Direction.CW, 0, ValueError, "Invalid layer amount: 0"),
        (3, Layer.UP, None,         1, ValueError, "Invalid rotation direction"),
    ],
)
# fmt: on
def test_rotate_sides_exception(
    generate_cube: Callable[[int], Cube],
    cube_size: int,
    turned_layer: Layer,
    direction: Direction | None,
    layer_amount: int,
    expected_exception_type: type[BaseException],
    expected_exception: str,
) -> None:
    """
    Tests that rotate_sides() raises an exception when the parameters are not valid.

    :param generate_cube: Fixture to generate a cube
    :param cube_size: The size of the cube
    :param turned_layer: The layer that is turned
    :param direction: The direction of the turn
    :param layer_amount: The amount of layers
    :param expected_exception_type: The expected exception type
    :param expected_exception: The expected exception
    :return: None
    """

    # Patch the get_edge() method to avoid unnecessary calls
    with patch("rubik_cube_solver.cube_rotation.side_stickers_rotation.get_edge"):

        # Mock the cube
        cube = generate_cube(cube_size)

        # Assert exception
        with pytest.raises(expected_exception_type, match=expected_exception):
            ssr.rotate_sides(cube, turned_layer, direction, layer_amount)
