# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.solve.cube_nxn.reduced_3x3 import as_3x3


class TestAs3x3:
    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6, 7])
    # fmt: on
    def test_solved(self, generate_cube: Callable[[int, str], Cube], size: int) -> None:
        """
        Tests that a solved big cube stands for a solved 3x3.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The size of the big cube
        :return: None
        """

        # Generate the cube
        cube = generate_cube(size, "")

        # Assert
        result = as_3x3(cube)
        assert result.size == 3
        assert result.layers == generate_cube(3, "").layers

    # fmt: off
    @pytest.mark.parametrize("size, algorithm", [
        (4, "R U R' U'"),
        (5, "F2 D' L B2"),
        (6, "R U F' L2 D B' R2 U'"),
        (7, "x U y' R2 z F'"),
    ])
    # fmt: on
    def test_outer_turns(self, generate_cube: Callable[[int, str], Cube], size: int, algorithm: str) -> None:
        """
        Tests that a big cube turned only by outer faces and whole-cube rotations stands for the 3x3 turned
        by the same algorithm.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The size of the big cube
        :param algorithm: The outer-face turns and rotations applied to both cubes
        :return: None
        """

        # Generate the cube
        cube = generate_cube(size, algorithm)

        # Assert
        assert as_3x3(cube).layers == generate_cube(3, algorithm).layers

    def test_leaves_the_cube_unchanged(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that building the 3x3 leaves the big cube it is read from untouched.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(5, "R U F'")

        # Build the 3x3
        as_3x3(cube)

        # Assert
        assert cube.layers == generate_cube(5, "R U F'").layers
