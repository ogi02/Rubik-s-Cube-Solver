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
def test_success_get_edge(generate_face: Callable[[int], list[Color]], layer_amount: int,
                          position: EdgePosition, cube_size: int, expected_edge: list[Color]) -> None:
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


def test_success_set_edge(generate_white_only_face: Callable[[int], list[Color]], layer_amount: int,
                          position: EdgePosition, cube_size: int, generate_edge: Callable[[int], list[Color]]) -> None:
    """
    Tests the setter of the edge based on the position.

    :param generate_white_only_face: Fixture to generate a face with only white stickers
    :param layer_amount: The amount of layers
    :param position: The position of the edge
    :param cube_size: The size of the cube
    :param generate_edge: Fixture to generate an edge with repeating Rubik's colors
    :return: None
    """




def test_exception_set_edge() -> None:
    """
    Tests that set_edge() raises an exception when the parameters are not valid.

    :return: None
    """
    pass
