# Python imports
import random
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation
from rubik_cube_solver.scramble.scrambler import Scrambler
from rubik_cube_solver.solve.cube_nxn.edges import EDGES_DOWN_CYCLE, EDGES_UP_CYCLE, is_paired
from rubik_cube_solver.solve.cube_nxn.solve_nxn import SolveNxN

FIRST_FOUR: set[Color] = {Color.YELLOW, Color.WHITE, Color.GREEN, Color.RED}
ALL_SIX: set[Color] = set(Color)


def _built_centers(cube: Cube) -> set[Color]:
    """
    Returns the colours whose whole center sits on one face, by reading raw stickers. The face is not
    checked, since the solution has its regrips removed and so leaves the cube in another grip.

    :param cube: The cube
    :return: The colours with a finished center
    """

    size = cube.size
    colors = [
        {cube.layers[face][row * size + col] for row in range(1, size - 1) for col in range(1, size - 1)}
        for face in Layer
    ]

    return {face_colors.pop() for face_colors in colors if len(face_colors) == 1}


def _paired_edges(cube: Cube, slots: tuple[EdgeSlot, ...]) -> int:
    """
    Counts the paired edges among some slots.

    :param cube: The cube
    :param slots: The slots
    :return: The number of slots whose edge is paired
    """

    return sum(is_paired(cube, slot) for slot in slots)


class TestSolveNxNInit:
    # fmt: off
    @pytest.mark.parametrize("cube_size", [4, 5, 6, 7, 8])
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that a cube of size 4 or more, even or odd, is accepted without error.

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
        Tests that a cube smaller than 4 raises a ValueError naming its size.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        with pytest.raises(ValueError, match=f"SolveNxN supports only cubes of size 4 or more, got size {cube_size}"):
            SolveNxN(cube)


class TestSolveNxNSteps:
    def test_returns_the_steps_in_order(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `_steps` returns the first-four-centers step, the last-two-centers step, the
        first-eight-edges step, then the last-four-edges step.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "")
        solve = SolveNxN(cube)

        # Assert
        assert solve._steps() == [
            solve._first_four_centers,
            solve._last_two_centers,
            solve._first_eight_edges,
            solve._last_four_edges,
        ]


class TestSolveNxNFirstFourCenters:
    def test_builds_the_centers(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the step turns the cube until yellow, white, green and red are built, and records
        every move it makes in the solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "Rw U2 Lw' F Dw")
        solve = SolveNxN(cube)

        # Run the step
        solve._first_four_centers()

        # Assert
        replay = generate_cube(4, "Rw U2 Lw' F Dw")
        Rotator(replay).apply(solve.solution)
        assert FIRST_FOUR <= _built_centers(cube)
        assert replay.layers == cube.layers


class TestSolveNxNLastTwoCenters:
    def test_builds_the_centers(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the step, run after the first four centers, turns the cube until every center is
        built, and records every move it makes in the solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(5, "Rw U2 Lw' F Dw")
        solve = SolveNxN(cube)

        # Run the steps
        solve._first_four_centers()
        solve._last_two_centers()

        # Assert
        replay = generate_cube(5, "Rw U2 Lw' F Dw")
        Rotator(replay).apply(solve.solution)
        assert _built_centers(cube) == ALL_SIX
        assert replay.layers == cube.layers


class TestSolveNxNFirstEightEdges:
    def test_builds_the_edges(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the step, run after the centers, pairs eight edges on UP and DOWN with every center
        still built, and records every move it makes in the solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(5, "Rw U2 Lw' F Dw")
        solve = SolveNxN(cube)

        # Run the steps
        solve._first_four_centers()
        solve._last_two_centers()
        solve._first_eight_edges()

        # Assert
        replay = generate_cube(5, "Rw U2 Lw' F Dw")
        Rotator(replay).apply(solve.solution)
        assert _built_centers(cube) == ALL_SIX
        assert _paired_edges(cube, EDGES_UP_CYCLE + EDGES_DOWN_CYCLE) == 8
        assert replay.layers == cube.layers


class TestSolveNxNLastFourEdges:
    def test_builds_the_edges(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the step, run after the first eight edges, pairs every edge but FR's with every center
        still built, and records every move it makes in the solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(5, "Rw U2 Lw' F Dw")
        solve = SolveNxN(cube)

        # Run the steps
        solve._first_four_centers()
        solve._last_two_centers()
        solve._first_eight_edges()
        solve._last_four_edges()

        # Assert
        replay = generate_cube(5, "Rw U2 Lw' F Dw")
        Rotator(replay).apply(solve.solution)
        assert _built_centers(cube) == ALL_SIX
        assert _paired_edges(cube, tuple(set(EdgeSlot) - {EdgeSlot.FR})) == 11
        assert replay.layers == cube.layers


class TestSolveNxNSolve:
    # fmt: off
    @pytest.mark.parametrize("cube_size", [4, 5, 6, 7])
    # fmt: on
    def test_solves_random_scrambles(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that solving builds every center and pairs every edge but FR's, and that the returned
        solution holds no whole-cube rotation and does the same when replayed on the scramble. The replay
        ends in another grip, so its paired edges are counted over every slot.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        random.seed(cube_size)

        for _ in range(3):
            # Scramble the cube
            scramble = str(Algorithm(Scrambler().generate_scramble(cube_size)))
            cube = generate_cube(cube_size, scramble)

            # Solve it
            solution = SolveNxN(cube).solve()

            # Replay the solution
            replay = generate_cube(cube_size, scramble)
            Rotator(replay).apply(solution)

            # Assert
            assert _built_centers(cube) == ALL_SIX, scramble
            assert _built_centers(replay) == ALL_SIX, scramble
            assert _paired_edges(cube, tuple(set(EdgeSlot) - {EdgeSlot.FR})) == 11, scramble
            assert _paired_edges(replay, tuple(EdgeSlot)) >= 11, scramble
            assert not any(isinstance(move.layer, Rotation) for move in solution.moves)
