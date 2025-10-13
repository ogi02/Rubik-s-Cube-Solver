import pytest

from typing import Callable
from unittest.mock import patch


from src.solver.cube import Cube
from src.solver.cube_rotation.face_stickers_rotation import (
    generate_clockwise_rotation_map, generate_counter_clockwise_rotation_map,
    generate_double_rotation_map, generate_rotation_map, rotate_face
)
from src.solver.enums.Color import Color
from src.solver.enums.Direction import Direction
from src.solver.enums.Layer import Layer

# -----------------------
# Fixtures
# -----------------------
RUBIKS_CUBE_COLORS: list[Color] = [Color.WHITE, Color.YELLOW, Color.ORANGE, Color.RED, Color.GREEN, Color.BLUE]


@pytest.fixture
def generate_cube() -> Callable[[int], Cube]:
    """
    Returns a method to generate an n x n cube.

    :return: The callable method
    """
    def _generate(n: int) -> Cube:
        """
        Generates an n x n cube.

        :param n: Cube size
        :return: The cube
        """
        return Cube(n)

    return _generate


@pytest.fixture
def generate_face() -> Callable[[int], list[Color]]:
    """
    Returns a method to generate an n x n face with repeating Rubik's colors.

    :return: The callable method
    """
    def _generate(n: int) -> list[Color]:
        """
        Generates an n x n face with repeating Rubik's colors.

        :param n: Cube size
        :return: Face with repeating Rubik's colors
        """
        face: list[Color] = []
        for i in range(n * n):
            face.append(RUBIKS_CUBE_COLORS[i % len(RUBIKS_CUBE_COLORS)])
        return face

    return _generate


# -----------------------
# Tests
# -----------------------
@pytest.mark.parametrize("cube_size, expected_rotation_map", [
    (2, [1, 3,
         0, 2]),
    (3, [2, 5, 8,
         1, 4, 7,
         0, 3, 6]),
    (4, [3, 7, 11, 15,
         2, 6, 10, 14,
         1, 5, 9,  13,
         0, 4, 8,  12]),
    (5, [4, 9, 14, 19, 24,
         3, 8, 13, 18, 23,
         2, 7, 12, 17, 22,
         1, 6, 11, 16, 21,
         0, 5, 10, 15, 20]),
    (6, [5, 11, 17, 23, 29, 35,
         4, 10, 16, 22, 28, 34,
         3, 9,  15, 21, 27, 33,
         2, 8,  14, 20, 26, 32,
         1, 7,  13, 19, 25, 31,
         0, 6,  12, 18, 24, 30]),
    (7, [6, 13, 20, 27, 34, 41, 48,
         5, 12, 19, 26, 33, 40, 47,
         4, 11, 18, 25, 32, 39, 46,
         3, 10, 17, 24, 31, 38, 45,
         2, 9,  16, 23, 30, 37, 44,
         1, 8,  15, 22, 29, 36, 43,
         0, 7,  14, 21, 28, 35, 42])
])
def test_success_generate_clockwise_rotation_map(cube_size: int, expected_rotation_map: list[int]) -> None:
    """
    Tests the generation of the map for a clockwise rotation.

    :param cube_size: Cube size
    :param expected_rotation_map: The expected rotation map
    :return: None
    """

    assert generate_clockwise_rotation_map(cube_size) == expected_rotation_map


@pytest.mark.parametrize("cube_size, expected_rotation_map", [
    (2, [2, 0,
         3, 1]),
    (3, [6, 3, 0,
         7, 4, 1,
         8, 5, 2]),
    (4, [12, 8, 4, 0,
         13, 9, 5, 1,
         14, 10, 6, 2,
         15, 11, 7, 3]),
    (5, [20, 15, 10, 5, 0,
         21, 16, 11, 6, 1,
         22, 17, 12, 7, 2,
         23, 18, 13, 8, 3,
         24, 19, 14, 9, 4]),
    (6, [30, 24, 18, 12, 6, 0,
         31, 25, 19, 13, 7, 1,
         32, 26, 20, 14, 8, 2,
         33, 27, 21, 15, 9, 3,
         34, 28, 22, 16, 10, 4,
         35, 29, 23, 17, 11, 5]),
    (7, [42, 35, 28, 21, 14, 7, 0,
         43, 36, 29, 22, 15, 8, 1,
         44, 37, 30, 23, 16, 9, 2,
         45, 38, 31, 24, 17, 10, 3,
         46, 39, 32, 25, 18, 11, 4,
         47, 40, 33, 26, 19, 12, 5,
         48, 41, 34, 27, 20, 13, 6])

])
def test_success_generate_counter_clockwise_rotation_map(cube_size: int, expected_rotation_map: list[int]) -> None:
    """
    Tests the generation of the map for a counter-clockwise rotation.

    :param cube_size: Cube size
    :param expected_rotation_map: The expected rotation map
    :return: None
    """

    assert generate_counter_clockwise_rotation_map(cube_size) == expected_rotation_map


@pytest.mark.parametrize("cube_size, expected_rotation_map", [
    (2, [3, 2,
         1, 0]),
    (3, [8, 7, 6,
         5, 4, 3,
         2, 1, 0]),
    (4, [15, 14, 13, 12,
         11, 10, 9, 8,
         7, 6, 5, 4,
         3, 2, 1, 0]),
    (5, [24, 23, 22, 21, 20,
         19, 18, 17, 16, 15,
         14, 13, 12, 11, 10,
         9, 8, 7, 6, 5,
         4, 3, 2, 1, 0]),
    (6, [35, 34, 33, 32, 31, 30,
         29, 28, 27, 26, 25, 24,
         23, 22, 21, 20, 19, 18,
         17, 16, 15, 14, 13, 12,
         11, 10, 9, 8, 7, 6,
         5, 4, 3, 2, 1, 0]),
    (7, [48, 47, 46, 45, 44, 43, 42,
         41, 40, 39, 38, 37, 36, 35,
         34, 33, 32, 31, 30, 29, 28,
         27, 26, 25, 24, 23, 22, 21,
         20, 19, 18, 17, 16, 15, 14,
         13, 12, 11, 10, 9, 8, 7,
         6, 5, 4, 3, 2, 1, 0]),
])
def test_success_generate_double_rotation_map(cube_size: int, expected_rotation_map: list[int]) -> None:
    """
    Tests the generation of the map for a double rotation.

    :param cube_size: Cube size
    :param expected_rotation_map: The expected rotation map
    :return: None
    """

    assert generate_double_rotation_map(cube_size) == expected_rotation_map


@pytest.mark.parametrize("direction, cube_size, expected_method", [
    (Direction.CW, 3, generate_clockwise_rotation_map),
    (Direction.CCW, 4, generate_counter_clockwise_rotation_map),
    (Direction.DOUBLE, 5, generate_double_rotation_map)
])
def test_success_generate_rotation_map(direction: Direction, cube_size: int, expected_method: Callable[[int], list[int]]) -> None:
    """
    Tests the generation of an n x n rotation map.

    :param direction: The direction of the turn
    :param cube_size: The size of the cube
    :param expected_method: The expected method which is called
    :return: None
    """

    with patch(f"src.solver.cube_rotation.face_stickers_rotation.{expected_method.__name__}") as mocked_method:
        # Dummy value
        mocked_method.return_value = [1, 2, 3]

        result = generate_rotation_map(direction, cube_size)

        # Assert
        mocked_method.assert_called_once_with(cube_size)
        assert result == [1, 2, 3]


@pytest.mark.parametrize("direction, cube_size", [(None, 3)])
def test_exception_generate_rotation_map(direction: Direction | None, cube_size: int) -> None:
    """
    Tests exception during the generation of an n x n rotation map.

    :param direction: The direction of the turn
    :param cube_size: The size of the cube
    :return: None
    """

    with pytest.raises(ValueError, match="Unexpected direction when trying to rotate face!"):
        generate_rotation_map(direction, cube_size)

@pytest.mark.parametrize("direction, cube_size, rotation_map, expected_face", [
    (Direction.CW, 3, [2, 5, 8,
                       1, 4, 7,
                       0, 3, 6], [Color.WHITE,  Color.RED,   Color.WHITE,
                                  Color.YELLOW, Color.GREEN, Color.YELLOW,
                                  Color.ORANGE, Color.BLUE,  Color.ORANGE]),
    (Direction.CCW, 3, [6, 3, 0,
                        7, 4, 1,
                        8, 5, 2], [Color.ORANGE, Color.BLUE,  Color.ORANGE,
                                   Color.YELLOW, Color.GREEN, Color.YELLOW,
                                   Color.WHITE,  Color.RED,   Color.WHITE]),
    (Direction.DOUBLE, 3, [8, 7, 6,
                           5, 4, 3,
                           2, 1, 0], [Color.ORANGE, Color.YELLOW, Color.WHITE,
                                      Color.BLUE,   Color.GREEN,  Color.RED,
                                      Color.ORANGE, Color.YELLOW, Color.WHITE]),
    (Direction.CW, 2, [1, 3,
                       0, 2], [Color.ORANGE, Color.WHITE,
                               Color.RED,    Color.YELLOW]),
    (Direction.CCW, 4, [12, 8, 4, 0,
                        13, 9, 5, 1,
                        14, 10, 6, 2,
                        15, 11, 7, 3], [Color.RED,    Color.YELLOW, Color.BLUE, Color.RED,
                                        Color.ORANGE, Color.WHITE,  Color.GREEN, Color.ORANGE,
                                        Color.YELLOW, Color.BLUE,   Color.RED,  Color.YELLOW,
                                        Color.WHITE,  Color.GREEN,  Color.ORANGE, Color.WHITE]),
])
def test_success_rotate_face(
        generate_cube: Callable[[int], Cube], generate_face: Callable[[int], list[Color]],
        direction: Direction, cube_size: int, rotation_map: list[int], expected_face: list[Color]
) -> None:
    """
    Tests the rotation of a face.

    :param generate_cube: Fixture to generate a cube
    :param generate_face: Fixture to generate a face
    :param direction: The direction of the turn
    :param cube_size: The size of the cube
    :param rotation_map: The mocked rotation map
    :param expected_face: The expected face after the turn
    :return: None
    """

    # Mock the cube
    cube = generate_cube(cube_size)
    cube.layers = {
        Layer.UP: generate_face(cube_size),
    }

    with patch("src.solver.cube_rotation.face_stickers_rotation.generate_rotation_map") as mocked_method:
        # Mock the generate_rotation_map() method
        mocked_method.return_value = rotation_map

        # Run
        rotate_face(cube, Layer.UP, direction)

        # Assert
        mocked_method.assert_called_once_with(direction, cube_size)

        assert cube.layers.get(Layer.UP) == expected_face
