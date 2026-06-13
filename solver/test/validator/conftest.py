# Python imports
from math import ceil
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.scramble.scrambler import Scrambler
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


@pytest.fixture(scope="session")
def scrambled_2x2_cube() -> Cube:
    """
    Returns a 2x2 cube that has been scrambled via the Scrambler and Rotator.

    :return: A scrambled 2x2 Cube instance
    """

    cube = Cube(2)
    scramble = Scrambler().generate_scramble(2)
    rotator = Rotator(cube)
    for move in scramble:
        rotator.turn(move)
    return cube


@pytest.fixture(scope="session")
def scrambled_3x3_cube() -> Cube:
    """
    Returns a 3x3 cube that has been scrambled via the Scrambler and Rotator.

    :return: A scrambled 3x3 Cube instance
    """

    cube = Cube(3)
    scramble = Scrambler().generate_scramble(3)
    rotator = Rotator(cube)
    for move in scramble:
        rotator.turn(move)
    return cube


@pytest.fixture(scope="session")
def scrambled_4x4_cube() -> Cube:
    """
    Returns a 4x4 cube that has been scrambled via the Scrambler and Rotator.

    :return: A scrambled 4x4 Cube instance
    """

    cube = Cube(4)
    scramble = Scrambler().generate_scramble(4)
    rotator = Rotator(cube)
    for move in scramble:
        rotator.turn(move)
    return cube


@pytest.fixture(scope="session")
def scrambled_5x5_cube() -> Cube:
    """
    Returns a 5x5 cube that has been scrambled via the Scrambler and Rotator.

    :return: A scrambled 5x5 Cube instance
    """

    cube = Cube(5)
    scramble = Scrambler().generate_scramble(5)
    rotator = Rotator(cube)
    for move in scramble:
        rotator.turn(move)
    return cube


@pytest.fixture(scope="session")
def scrambled_6x6_cube() -> Cube:
    """
    Returns a 6x6 cube that has been scrambled via the Scrambler and Rotator.

    :return: A scrambled 6x6 Cube instance
    """

    cube = Cube(6)
    scramble = Scrambler().generate_scramble(6)
    rotator = Rotator(cube)
    for move in scramble:
        rotator.turn(move)
    return cube


@pytest.fixture(scope="session")
def scrambled_7x7_cube() -> Cube:
    """
    Returns a 7x7 cube that has been scrambled via the Scrambler and Rotator.

    :return: A scrambled 7x7 Cube instance
    """

    cube = Cube(7)
    scramble = Scrambler().generate_scramble(7)
    rotator = Rotator(cube)
    for move in scramble:
        rotator.turn(move)
    return cube
