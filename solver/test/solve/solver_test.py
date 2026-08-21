# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.solve.cube_2x2.solve_2x2 import Solve2x2
from rubik_cube_solver.solve.cube_3x3.solve_3x3 import Solve3x3
from rubik_cube_solver.solve.cube_nxn.solve_nxn import SolveNxN
from rubik_cube_solver.solve.solve import Solve
from rubik_cube_solver.solve.solver import create_solver

SCRAMBLE_2X2 = "R U' F2 R' U R2 F' U2 R"
SCRAMBLE_3X3 = "D2 F2 D B' R2 U' L F U2 R' B2 D' F2 U R2 F2"


class TestCreateSolver:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, expected_type",
        [
            (2, Solve2x2),
            (3, Solve3x3),
            (4, SolveNxN),
            (5, SolveNxN),
        ],
    )
    # fmt: on
    def test_success(
        self, generate_cube: Callable[[int, str], Cube], cube_size: int, expected_type: type[Solve]
    ) -> None:
        """
        Tests that a cube of a supported size returns the solver for that size, holding the very
        cube it was given rather than a copy of it.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param expected_type: The solver class expected for that size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")
        solver = create_solver(cube)

        # Assert
        assert isinstance(solver, expected_type)
        assert solver.cube is cube

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, scramble",
        [
            (2, SCRAMBLE_2X2),
            (3, SCRAMBLE_3X3),
        ],
    )
    # fmt: on
    def test_solves_a_scrambled_cube(
        self, generate_cube: Callable[[int, str], Cube], cube_size: int, scramble: str
    ) -> None:
        """
        Tests that the returned solver solves the cube end to end, so the entry point is usable
        without naming the concrete solver, and that the solution it collected is reachable through
        the solver afterwards.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param scramble: The scramble to apply before solving
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, scramble)
        solver = create_solver(cube)
        solution = solver.solve()

        # Assert
        assert str(cube) == str(Cube(cube_size))
        assert solver.solution == solution

    # fmt: off
    @pytest.mark.parametrize("cube_size", [4, 5])
    # fmt: on
    def test_reduces_a_big_cube(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that a big cube goes through the reduction solver, which builds the first four centers
        and so leaves the cube unsolved until the rest of the reduction is written.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, SCRAMBLE_3X3)
        solver = create_solver(cube)
        solution = solver.solve()

        # Assert
        assert str(cube) != str(Cube(cube_size))
        assert solver.solution == solution

    # fmt: off
    @pytest.mark.parametrize("cube_size", [0, 1])
    # fmt: on
    def test_invalid_size(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that a cube of a size no solver handles raises a ValueError naming that size, rather
        than returning a solver that would fail part-way through.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The unsupported cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        with pytest.raises(ValueError, match=f"No solver for cubes of size {cube_size}"):
            create_solver(cube)
