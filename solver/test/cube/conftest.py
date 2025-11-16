# Python imports
import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer


@pytest.fixture
def solved_3x3_cube() -> Cube:
    """
    Fixture that returns a solved 3x3 Rubik's Cube.

    :return: A solved Cube instance of size 3
    """

    return Cube(size=3)


@pytest.fixture
def scrambled_3x3_cube() -> Cube:
    """
    Fixture that returns a scrambled 3x3 Rubik's Cube.

    :return: A scrambled Cube instance of size 3
    """

    # fmt: off
    cube = Cube(
        size=3,
        layers={
            Layer.UP:    [Color.YELLOW, Color.WHITE,  Color.WHITE,
                          Color.YELLOW, Color.WHITE,  Color.ORANGE,
                          Color.YELLOW, Color.YELLOW, Color.ORANGE],
            Layer.DOWN:  [Color.WHITE,  Color.BLUE,   Color.RED,
                          Color.GREEN,  Color.YELLOW, Color.RED,
                          Color.GREEN,  Color.WHITE,  Color.RED],
            Layer.LEFT:  [Color.BLUE,   Color.ORANGE, Color.BLUE,
                          Color.BLUE,   Color.ORANGE, Color.ORANGE,
                          Color.ORANGE, Color.YELLOW, Color.GREEN],
            Layer.RIGHT: [Color.BLUE,   Color.GREEN,  Color.RED,
                          Color.RED,    Color.RED,    Color.BLUE,
                          Color.WHITE,  Color.YELLOW, Color.YELLOW],
            Layer.FRONT: [Color.RED,    Color.BLUE,   Color.WHITE,
                          Color.WHITE,  Color.GREEN,  Color.GREEN,
                          Color.ORANGE, Color.ORANGE, Color.GREEN],
            Layer.BACK:  [Color.BLUE,   Color.RED,    Color.ORANGE,
                          Color.WHITE,  Color.BLUE,   Color.RED,
                          Color.GREEN,  Color.GREEN,  Color.YELLOW],
        }
    )
    # fmt: on
    return cube


@pytest.fixture
def solved_4x4_cube() -> Cube:
    """
    Fixture that returns a solved 4x4 Rubik's Cube.

    :return: A solved Cube instance of size 4
    """

    return Cube(size=4)


@pytest.fixture
def scrambled_4x4_cube() -> Cube:
    """
    Fixture that returns a scrambled 4x4 Rubik's Cube.

    :return: A scrambled Cube instance of size 4
    """

    # fmt: off
    cube = Cube(
        size=4,
        layers={

            Layer.UP:    [Color.GREEN,  Color.ORANGE, Color.BLUE,   Color.YELLOW,
                          Color.RED,    Color.YELLOW, Color.WHITE,  Color.RED,
                          Color.BLUE,   Color.GREEN,  Color.ORANGE, Color.RED,
                          Color.RED,    Color.GREEN,  Color.ORANGE, Color.YELLOW],
            Layer.DOWN:  [Color.BLUE,   Color.WHITE,  Color.WHITE,  Color.BLUE,
                          Color.GREEN,  Color.BLUE,   Color.RED,    Color.YELLOW,
                          Color.GREEN,  Color.YELLOW, Color.ORANGE, Color.RED,
                          Color.RED,    Color.WHITE,  Color.RED,    Color.BLUE],
            Layer.LEFT:  [Color.ORANGE, Color.BLUE,   Color.YELLOW, Color.GREEN,
                          Color.YELLOW, Color.BLUE,   Color.WHITE,  Color.YELLOW,
                          Color.ORANGE, Color.RED,    Color.RED,    Color.WHITE,
                          Color.WHITE,  Color.YELLOW, Color.YELLOW, Color.WHITE],
            Layer.RIGHT: [Color.ORANGE, Color.WHITE,  Color.BLUE,   Color.ORANGE,
                          Color.ORANGE, Color.GREEN,  Color.YELLOW, Color.GREEN,
                          Color.ORANGE, Color.RED,    Color.ORANGE, Color.RED,
                          Color.RED,    Color.BLUE,   Color.GREEN,  Color.RED],
            Layer.FRONT: [Color.YELLOW, Color.WHITE,  Color.YELLOW, Color.GREEN,
                          Color.ORANGE, Color.YELLOW, Color.WHITE,  Color.BLUE,
                          Color.RED,    Color.WHITE,  Color.GREEN,  Color.GREEN,
                          Color.ORANGE, Color.ORANGE, Color.GREEN,  Color.YELLOW],
            Layer.BACK:  [Color.BLUE,   Color.WHITE,  Color.BLUE,   Color.WHITE,
                          Color.ORANGE, Color.GREEN,  Color.BLUE,   Color.RED,
                          Color.YELLOW, Color.ORANGE, Color.BLUE,   Color.WHITE,
                          Color.WHITE,  Color.GREEN,  Color.BLUE,   Color.GREEN],
        }
    )
    # fmt: on
    return cube


@pytest.fixture
def solved_5x5_cube() -> Cube:
    """
    Fixture that returns a solved 5x5 Rubik's Cube.

    :return: A solved Cube instance of size 5
    """

    return Cube(size=5)


@pytest.fixture
def scrambled_5x5_cube() -> Cube:
    """
    Fixture that returns a scrambled 5x5 Rubik's Cube.

    :return: A scrambled Cube instance of size 5
    """

    # fmt: off
    cube = Cube(
        size=5,
        layers={
            Layer.UP:    [Color.GREEN,  Color.GREEN,  Color.ORANGE, Color.ORANGE, Color.BLUE,
                          Color.WHITE,  Color.RED,    Color.ORANGE, Color.YELLOW, Color.WHITE,
                          Color.ORANGE, Color.GREEN,  Color.WHITE,  Color.WHITE,  Color.GREEN,
                          Color.RED,    Color.RED,    Color.RED,    Color.WHITE,  Color.WHITE,
                          Color.BLUE,   Color.ORANGE, Color.WHITE,  Color.RED,    Color.YELLOW],
            Layer.DOWN:  [Color.RED,    Color.BLUE,   Color.ORANGE, Color.RED,    Color.WHITE,
                          Color.YELLOW, Color.GREEN,  Color.YELLOW, Color.RED,    Color.RED,
                          Color.BLUE,   Color.ORANGE, Color.YELLOW, Color.YELLOW, Color.RED,
                          Color.BLUE,   Color.WHITE,  Color.BLUE,   Color.YELLOW, Color.BLUE,
                          Color.WHITE,  Color.ORANGE, Color.YELLOW, Color.WHITE,  Color.ORANGE],
            Layer.LEFT:  [Color.ORANGE, Color.ORANGE, Color.BLUE,   Color.WHITE,  Color.RED,
                          Color.GREEN,  Color.BLUE,   Color.GREEN,  Color.ORANGE, Color.GREEN,
                          Color.RED,    Color.GREEN,  Color.ORANGE, Color.YELLOW, Color.YELLOW,
                          Color.WHITE,  Color.GREEN,  Color.RED,    Color.YELLOW, Color.BLUE,
                          Color.GREEN,  Color.RED,    Color.WHITE,  Color.ORANGE, Color.YELLOW],
            Layer.RIGHT: [Color.ORANGE, Color.BLUE,   Color.WHITE,  Color.RED,    Color.ORANGE,
                          Color.RED,    Color.WHITE,  Color.WHITE,  Color.ORANGE, Color.YELLOW,
                          Color.GREEN,  Color.ORANGE, Color.RED,    Color.BLUE,   Color.RED,
                          Color.WHITE,  Color.BLUE,   Color.BLUE,   Color.RED,    Color.YELLOW,
                          Color.RED,    Color.BLUE,   Color.WHITE,  Color.ORANGE, Color.YELLOW],
            Layer.FRONT: [Color.YELLOW, Color.GREEN,  Color.ORANGE, Color.GREEN,  Color.GREEN,
                          Color.YELLOW, Color.YELLOW, Color.WHITE,  Color.WHITE,  Color.YELLOW,
                          Color.BLUE,   Color.RED,    Color.GREEN,  Color.ORANGE, Color.RED,
                          Color.YELLOW, Color.ORANGE, Color.BLUE,   Color.BLUE,   Color.ORANGE,
                          Color.GREEN,  Color.YELLOW, Color.YELLOW, Color.GREEN,  Color.BLUE],
            Layer.BACK:  [Color.GREEN,  Color.YELLOW, Color.GREEN,  Color.WHITE,  Color.WHITE,
                          Color.GREEN,  Color.GREEN,  Color.RED,    Color.BLUE,   Color.ORANGE,
                          Color.YELLOW, Color.YELLOW, Color.BLUE,   Color.GREEN,  Color.BLUE,
                          Color.RED,    Color.ORANGE, Color.WHITE,  Color.GREEN,  Color.BLUE,
                          Color.BLUE,   Color.GREEN,  Color.GREEN,  Color.BLUE,   Color.RED],
        }
    )
    # fmt: on
    return cube
