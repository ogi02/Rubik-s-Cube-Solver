# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
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
