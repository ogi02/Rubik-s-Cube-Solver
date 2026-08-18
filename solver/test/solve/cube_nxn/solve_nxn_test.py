# Python imports
import random
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation
from rubik_cube_solver.scramble.scrambler import Scrambler
from rubik_cube_solver.solve.cube_nxn.solve_nxn import SolveNxN

# Scrambles that leave the centers in a variety of states, chosen so that the pieces of the two
# colors start spread over every face, including the face the center is built on and the one
# opposite it. The last three start the cube in another orientation, which only an odd cube has
# fixed centers to correct.
# fmt: off
FIRST_CENTERS_SCRAMBLES: list[str] = [
    "",
    "Rw U2 F Lw' B",
    "Uw R2 Fw' D L2 Bw",
    "R Uw2 Lw F2 Dw' B R2",
    "x Rw' U F2 Dw",
    "y2 Fw D2 Rw B' Uw2",
    "z Lw2 U' Bw R Dw",
]
# fmt: on


def _face_is_solid(cube: Cube, layer: Layer, color: Color) -> bool:
    """
    Checks whether the center of a face is solved, by reading raw stickers rather than going through
    `search_center`, so the oracle is independent of the production code it is verifying.

    Every inner cell of the face - the fixed center of an odd cube among them - has to show the
    color, which is all a center has to be, since the four pieces of one color and position type are
    interchangeable.

    :param cube: The Cube instance to check
    :param layer: The face to check
    :param color: The color the center is built in
    :return: True if every center cell of the face shows that color, False otherwise
    """

    size = cube.size

    return all(
        cube.layers[layer][row * size + col] == color for row in range(1, size - 1) for col in range(1, size - 1)
    )


class TestSolveNxNInit:
    # fmt: off
    @pytest.mark.parametrize("cube_size", [4, 5, 6])
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that a big cube of any size is accepted without error.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        assert SolveNxN(cube).cube is cube

    # fmt: off
    @pytest.mark.parametrize("cube_size", [2, 3])
    # fmt: on
    def test_invalid_size(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that a cube smaller than 4x4, which has no center pieces to solve, raises a ValueError
        naming the given size.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        with pytest.raises(ValueError, match=f"SolveNxN supports only big cubes, got size {cube_size}"):
            SolveNxN(cube)


class TestSolveNxNSteps:
    def test_returns_the_steps_in_order(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `_steps` returns the first two centers.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "")
        solve = SolveNxN(cube)

        # Assert
        assert solve._steps() == [solve._first_centers]


class TestSolveNxNBuildCenter:
    # fmt: off
    @pytest.mark.parametrize("cube_size", [4, 5, 6])
    @pytest.mark.parametrize("algorithm", FIRST_CENTERS_SCRAMBLES)
    # fmt: on
    def test_builds_the_center_on_up(
        self, generate_cube: Callable[[int, str], Cube], cube_size: int, algorithm: str
    ) -> None:
        """
        Tests that `_build_center` gathers a whole center on the UP face, from a variety of
        scrambles that start the pieces on every face of the cube.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param algorithm: The scramble applied before building the center
        :return: None
        """

        # Generate the cube and build the center of the color its UP face already shows
        cube = generate_cube(cube_size, algorithm)
        color = cube.layers[Layer.UP][cube_size * cube_size // 2]
        SolveNxN(cube)._build_center(color)

        # Assert
        assert _face_is_solid(cube, Layer.UP, color)

    def test_already_solved_center(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `_build_center` leaves an already solved center solved. The face is taken apart
        on the way, because a line is staged and inserted as a whole and the pieces the staging
        needs are the ones lying on the face, so the step does turn the cube here.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube and build the white center
        cube = generate_cube(4, "")
        SolveNxN(cube)._build_center(Color.WHITE)

        # Assert
        assert _face_is_solid(cube, Layer.UP, Color.WHITE)


class TestSolveNxNFirstCenters:
    # fmt: off
    @pytest.mark.parametrize("cube_size", [4, 5, 6])
    @pytest.mark.parametrize("algorithm", FIRST_CENTERS_SCRAMBLES)
    # fmt: on
    def test_solves_both_centers_from_scramble(
        self, generate_cube: Callable[[int, str], Cube], cube_size: int, algorithm: str
    ) -> None:
        """
        Tests that `_first_centers` leaves the yellow center on DOWN and the white one on UP, from a
        variety of scrambles, including ones that start the cube in another orientation.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param algorithm: The scramble applied before solving the centers
        :return: None
        """

        # Generate the cube and solve the first two centers
        cube = generate_cube(cube_size, algorithm)
        SolveNxN(cube)._first_centers()

        # Assert
        assert _face_is_solid(cube, Layer.DOWN, Color.YELLOW)
        assert _face_is_solid(cube, Layer.UP, Color.WHITE)

    # fmt: off
    @pytest.mark.parametrize("cube_size", [4, 5, 6])
    # fmt: on
    def test_solves_random_scrambles(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that `_first_centers` solves a hundred randomly scrambled cubes of each size, which
        reach far more cases between them than the scrambles picked by hand. The random number
        generator is seeded, so a failing run can be reproduced exactly.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        random.seed(0)
        for _ in range(100):
            # Generate a scrambled cube and solve the first two centers
            cube = generate_cube(cube_size, str(Algorithm(Scrambler().generate_scramble(cube_size))))
            SolveNxN(cube)._first_centers()

            # Assert
            assert _face_is_solid(cube, Layer.DOWN, Color.YELLOW)
            assert _face_is_solid(cube, Layer.UP, Color.WHITE)


class TestSolveNxNSolve:
    # fmt: off
    @pytest.mark.parametrize("cube_size", [4, 5])
    # fmt: on
    def test_solves_the_centers_with_no_rotations_in_solution(
        self, generate_cube: Callable[[int, str], Cube], cube_size: int
    ) -> None:
        """
        Tests that `solve` runs the step on the live cube, leaving the two centers solved, and that
        the returned algorithm contains no whole-cube rotations.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube and solve it
        cube = generate_cube(cube_size, "Rw U2 F Lw' B Uw R2")
        result = SolveNxN(cube).solve()

        # Assert the step landed on the live cube
        assert _face_is_solid(cube, Layer.DOWN, Color.YELLOW)
        assert _face_is_solid(cube, Layer.UP, Color.WHITE)

        # Assert the solution contains no whole-cube rotations
        assert all(not isinstance(move.layer, Rotation) for move in result.moves)

    def test_solution_reproduces_the_state(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the returned solution is the algorithm that solves the centers, and not just a
        record of what the step happened to turn: applied to a second cube scrambled the same way,
        it leaves the two centers solved as well. The rotations are stripped from the solution, so
        the centers end up on an opposite pair of faces rather than on DOWN and UP.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Solve one cube and apply its solution to another scrambled the same way
        cube = generate_cube(4, "Uw R2 Fw' D L2 Bw")
        result = SolveNxN(cube).solve()
        replayed = generate_cube(4, f"Uw R2 Fw' D L2 Bw {result}")

        # Assert
        assert [layer for layer in Layer if _face_is_solid(replayed, layer, Color.YELLOW)] != []
        assert [layer for layer in Layer if _face_is_solid(replayed, layer, Color.WHITE)] != []
