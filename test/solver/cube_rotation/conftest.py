import pytest
from typing import Callable

from src.solver.cube import Cube
from src.solver.enums.Color import Color

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


@pytest.fixture
def generate_white_only_face() -> Callable[[int], list[Color]]:
    """
    Returns a method to generate an n x n face with only white stickers.

    :return: The callable method
    """
    def _generate(n: int) -> list[Color]:
        """
        Generates an n x n face with only white stickers.

        :param n: Cube size
        :return: Face with only white stickers
        """
        return [Color.WHITE] * (n * n)

    return _generate


@pytest.fixture
def generate_edge() -> Callable[[int], list[Color]]:
    """
    Returns a method to generate an edge with repeating Rubik's colors.

    :return: The callable method
    """
    def _generate(n: int) -> list[Color]:
        """
        Generates an edge with repeating Rubik's colors.

        :param n: Cube size
        :return: Edge with repeating Rubik's colors
        """
        edge: list[Color] = []
        for i in range(n):
            edge.append(RUBIKS_CUBE_COLORS[i % len(RUBIKS_CUBE_COLORS)])
        return edge

    return _generate
