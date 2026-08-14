# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator


@pytest.fixture
def generate_cube() -> Callable[[int, str], Cube]:
    """
    Returns a function that generates a solved cube of the given size and applies an algorithm to it.

    :return: A function that generates a cube of the given size with the given algorithm applied
    """

    def _generate(cube_size: int, algorithm: str) -> Cube:
        """
        Generates a solved cube of the given size and applies an algorithm to it.

        :param cube_size: The cube size
        :param algorithm: The algorithm in standard notation, empty for a solved cube
        :return: The cube with the algorithm applied
        """

        cube = Cube(cube_size)
        rotator = Rotator(cube)
        for move in Algorithm.from_str(algorithm).moves:
            rotator.turn(move)

        return cube

    return _generate
