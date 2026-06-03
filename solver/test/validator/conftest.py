# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.validator.validator import Validator


@pytest.fixture
def validator() -> Validator:
    """
    Returns a Validator instance.

    :return: The Validator instance
    """

    return Validator()


@pytest.fixture
def generate_cube() -> Callable[[int], Cube]:
    """
    Returns a method to generate a solved cube of a given size.

    :return: The callable method
    """

    def _generate(size: int) -> Cube:
        """
        Generates a solved cube of given size.

        :param size: The size of the cube
        :return: The Cube instance
        """

        return Cube(size=size)

    return _generate


@pytest.fixture
def generate_corners() -> Callable[..., list[tuple[Color, Color, Color]]]:
    """
    Returns a factory for building a list of 8 corner tuples directly,
    used to patch _get_corners in isolation tests.

    :return: The callable method
    """

    def _generate(*corners: tuple[Color, Color, Color]) -> list[tuple[Color, Color, Color]]:
        """
        Generates a list of corner tuples.

        :param corners: The corner tuples to include
        :return: The list of corner tuples
        """

        return list(corners)

    return _generate
