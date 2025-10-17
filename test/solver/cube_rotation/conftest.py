import pytest
from typing import Callable

from src.solver.cube import Cube
from src.solver.enums.Color import Color
from src.solver.enums.EdgePosition import EdgePosition
from src.solver.enums.Layer import Layer

RUBIKS_CUBE_COLORS: list[Color] = [Color.WHITE, Color.YELLOW, Color.ORANGE, Color.RED, Color.GREEN, Color.BLUE]


@pytest.fixture
def get_adjacent_edge() -> Callable[[Layer], list[tuple[Layer, EdgePosition]]]:
    """
    Returns a method to get the adjacent edges for a given edge position.

    :return: The callable method
    """

    def _get(layer: Layer) -> list[tuple[Layer, EdgePosition]]:
        """
        Gets the adjacent edges for a given edge position.

        :param layer: The layer to get the adjacent edges for
        :return: The adjacent edges
        """

        adjacent_faces = {
            Layer.UP:    [(Layer.BACK,  EdgePosition.TOP),    (Layer.RIGHT, EdgePosition.TOP),
                          (Layer.FRONT, EdgePosition.TOP),    (Layer.LEFT,  EdgePosition.TOP)],
            Layer.DOWN:  [(Layer.FRONT, EdgePosition.BOTTOM), (Layer.RIGHT, EdgePosition.BOTTOM),
                          (Layer.BACK,  EdgePosition.BOTTOM), (Layer.LEFT,  EdgePosition.BOTTOM)],
            Layer.FRONT: [(Layer.UP,    EdgePosition.BOTTOM), (Layer.RIGHT, EdgePosition.LEFT),
                          (Layer.DOWN,  EdgePosition.TOP),    (Layer.LEFT,  EdgePosition.RIGHT)],
            Layer.BACK:  [(Layer.UP,    EdgePosition.TOP),    (Layer.LEFT,  EdgePosition.LEFT),
                          (Layer.DOWN,  EdgePosition.BOTTOM), (Layer.RIGHT, EdgePosition.RIGHT)],
            Layer.LEFT:  [(Layer.UP,    EdgePosition.LEFT),   (Layer.FRONT, EdgePosition.LEFT),
                          (Layer.DOWN,  EdgePosition.LEFT),   (Layer.BACK,  EdgePosition.RIGHT)],
            Layer.RIGHT: [(Layer.UP,    EdgePosition.RIGHT),  (Layer.BACK,  EdgePosition.LEFT),
                          (Layer.DOWN,  EdgePosition.RIGHT),  (Layer.FRONT, EdgePosition.RIGHT)]
        }

        return adjacent_faces[layer]

    return _get


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
def generate_one_color_only_face() -> Callable[[int, Color], list[Color]]:
    """
    Returns a method to generate an n x n face with only one color stickers.

    :return: The callable method
    """

    def _generate(n: int, color: Color) -> list[Color]:
        """
        Generates an n x n face with only white stickers.

        :param n: Cube size
        :param color: The color of the stickers
        :return: Face with only white stickers
        """
        return [color] * (n * n)

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


@pytest.fixture
def generate_one_color_only_edge() -> Callable[[int, Color], list[Color]]:
    """
    Returns a method to generate an edge with only one color stickers.

    :return: The callable method
    """

    def _generate(n: int, color: Color) -> list[Color]:
        """
        Generates an edge with only white stickers.

        :param n: Cube size
        :param color: The color of the stickers
        :return: Edge with only white stickers
        """
        return [color] * n

    return _generate
