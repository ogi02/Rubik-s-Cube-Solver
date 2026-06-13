# Python imports
from math import ceil
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.validator.validator import Validator
from rubik_cube_solver.validator.validator_constants import CENTER_COLORS_OPPOSITES


@pytest.fixture
def validator() -> Validator:
    """
    Returns a Validator instance.

    :return: The Validator instance
    """

    return Validator()


@pytest.fixture
def generate_expected_centers() -> Callable:
    """
    Returns a function that generates the expected centers based on the cube size

    :return: A function that generates the expected centers based on the cube size
    """

    def _generate(cube_size: int) -> list[tuple[Color, int, int]]:
        """
        Generates the expected centers based on the cube size

        :param cube_size: The cube size
        :return: The expected centers based on the cube size
        """

        centers: list[tuple[Color, int, int]] = []

        for color in [Color.WHITE, Color.YELLOW, Color.ORANGE, Color.RED, Color.GREEN, Color.BLUE]:
            for row in range(1, ceil(cube_size / 2)):
                for col in range(1, ceil(cube_size / 2)):
                    if cube_size % 2 == 1 and row == cube_size // 2 and col == cube_size // 2:
                        continue
                    for _ in range(4):
                        centers.append((color, row, col))

        return centers

    return _generate


@pytest.fixture
def generate_expected_wing_edges() -> Callable:
    """
    Returns a function that generates the expected wing edges based on the cube size

    :return: A function that generates the expected wing edges based on the cube size
    """

    def _generate(cube_size: int) -> list[tuple[int, Color, Color]]:
        """
        Generates the expected wing edges based on the cube size

        :param cube_size: The cube size
        :return: The expected wing edges based on the cube size
        """

        wing_edges: list[tuple[int, Color, Color]] = []
        all_colors = [Color.WHITE, Color.YELLOW, Color.ORANGE, Color.RED, Color.GREEN, Color.BLUE]

        for primary_color in all_colors:
            for secondary_color in all_colors:
                if primary_color == secondary_color or CENTER_COLORS_OPPOSITES[primary_color] == secondary_color:
                    continue
                for index in range(1, ceil(cube_size / 2)):
                    wing_edges.append((index, primary_color, secondary_color))

        return wing_edges

    return _generate
