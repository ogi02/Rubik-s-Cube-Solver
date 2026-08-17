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


@pytest.fixture
def generate_f2l_case(generate_cube: Callable[[int, str], Cube]) -> Callable[[str], Cube]:
    """
    Returns a function that generates the F2L case a given insertion algorithm solves.

    :param generate_cube: Fixture generating a cube with an algorithm applied
    :return: A function that generates the case solved by the given algorithm
    """

    def _generate(algorithm: str) -> Cube:
        """
        Generates the F2L case a given insertion algorithm solves, by applying it backwards to a
        solved cube. Everything outside the UP layer stays solved, so the cross is intact and only
        the front-right pair is out of its slot.

        :param algorithm: The insertion algorithm in standard notation
        :return: The cube in the case that algorithm solves
        """

        moves = []
        for move in reversed(algorithm.split()):
            if move.endswith("'"):
                moves.append(move[:-1])
            elif move.endswith("2"):
                moves.append(move)
            else:
                moves.append(f"{move}'")

        return generate_cube(3, " ".join(moves))

    return _generate
