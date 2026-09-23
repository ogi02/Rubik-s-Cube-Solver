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


def _is_solved(cube: Cube) -> bool:
    """
    Returns whether every face of a cube shows one colour, by reading raw stickers. The faces' colours are
    not checked, since the solution has its regrips removed and so leaves the cube in another grip.

    :param cube: The cube
    :return: Whether the cube is solved
    """

    return all(len(set(stickers)) == 1 for stickers in cube.layers.values())


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
        Tests that `_steps` returns the four individual center steps, the last-two-centers step,
        the edges step, then the 3x3 step, named and bound to the solver's own methods.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "")
        solve = SolveNxN(cube)

        # Assert
        assert solve._steps() == {
            "1st center": solve._first_center,
            "2nd center": solve._second_center,
            "3rd center": solve._third_center,
            "4th center": solve._fourth_center,
            "last 2 centers": solve._last_two_centers,
            "edges": solve._edges,
            "3x3 stage": solve._solve_as_3x3,
        }


class TestSolveNxNFirstCenter:
    def test_builds_the_center(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the step turns the cube until the yellow center is built, and records every move
        it makes in the solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "Rw U2 Lw' F Dw")
        solve = SolveNxN(cube)

        # Run the step
        solve._first_center()

        # Assert
        replay = generate_cube(4, "Rw U2 Lw' F Dw")
        Rotator(replay).apply(solve.solution)
        assert {Color.YELLOW} <= _built_centers(cube)
        assert replay.layers == cube.layers


class TestSolveNxNSecondCenter:
    def test_builds_the_center(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the step, run after the first center, turns the cube until yellow and white are
        built, and records every move it makes in the solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "Rw U2 Lw' F Dw")
        solve = SolveNxN(cube)

        # Run the steps
        solve._first_center()
        solve._second_center()

        # Assert
        replay = generate_cube(4, "Rw U2 Lw' F Dw")
        Rotator(replay).apply(solve.solution)
        assert {Color.YELLOW, Color.WHITE} <= _built_centers(cube)
        assert replay.layers == cube.layers


class TestSolveNxNThirdCenter:
    def test_builds_the_center(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the step, run after the first two centers, turns the cube until yellow, white and
        green are built, and records every move it makes in the solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "Rw U2 Lw' F Dw")
        solve = SolveNxN(cube)

        # Run the steps
        solve._first_center()
        solve._second_center()
        solve._third_center()

        # Assert
        replay = generate_cube(4, "Rw U2 Lw' F Dw")
        Rotator(replay).apply(solve.solution)
        assert {Color.YELLOW, Color.WHITE, Color.GREEN} <= _built_centers(cube)
        assert replay.layers == cube.layers


class TestSolveNxNFourthCenter:
    def test_builds_the_center(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the step, run after the first three centers, turns the cube until yellow, white,
        green and red are built, and records every move it makes in the solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "Rw U2 Lw' F Dw")
        solve = SolveNxN(cube)

        # Run the steps
        solve._first_center()
        solve._second_center()
        solve._third_center()
        solve._fourth_center()

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
        solve._first_center()
        solve._second_center()
        solve._third_center()
        solve._fourth_center()
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
        solve._first_center()
        solve._second_center()
        solve._third_center()
        solve._fourth_center()
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
        solve._first_center()
        solve._second_center()
        solve._third_center()
        solve._fourth_center()
        solve._last_two_centers()
        solve._first_eight_edges()
        solve._last_four_edges()

        # Assert
        replay = generate_cube(5, "Rw U2 Lw' F Dw")
        Rotator(replay).apply(solve.solution)
        assert _built_centers(cube) == ALL_SIX
        assert _paired_edges(cube, tuple(set(EdgeSlot) - {EdgeSlot.FR})) == 11
        assert replay.layers == cube.layers


class TestSolveNxNParity:
    # fmt: off
    @pytest.mark.parametrize("cube_size", [4, 5])
    # fmt: on
    def test_pairs_every_edge(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that the step, run after the last four edges, pairs every edge with every center still
        built, and records every move it makes in the solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "Rw U2 Lw' F Dw")
        solve = SolveNxN(cube)

        # Run the steps
        solve._first_center()
        solve._second_center()
        solve._third_center()
        solve._fourth_center()
        solve._last_two_centers()
        solve._first_eight_edges()
        solve._last_four_edges()
        solve._parity()

        # Assert
        replay = generate_cube(cube_size, "Rw U2 Lw' F Dw")
        Rotator(replay).apply(solve.solution)
        assert _built_centers(cube) == ALL_SIX
        assert _paired_edges(cube, tuple(EdgeSlot)) == 12
        assert replay.layers == cube.layers


class TestSolveNxNEdges:
    # fmt: off
    @pytest.mark.parametrize("cube_size", [4, 5])
    # fmt: on
    def test_pairs_every_edge(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that the step, run after every center, pairs every edge by running the first-eight-edges,
        last-four-edges and parity steps in turn, and records every move it makes in the solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "Rw U2 Lw' F Dw")
        solve = SolveNxN(cube)

        # Run the steps
        solve._first_center()
        solve._second_center()
        solve._third_center()
        solve._fourth_center()
        solve._last_two_centers()
        solve._edges()

        # Assert
        replay = generate_cube(cube_size, "Rw U2 Lw' F Dw")
        Rotator(replay).apply(solve.solution)
        assert _built_centers(cube) == ALL_SIX
        assert _paired_edges(cube, tuple(EdgeSlot)) == 12
        assert replay.layers == cube.layers


class TestSolveNxNSolveAs3x3:
    # fmt: off
    @pytest.mark.parametrize("cube_size", [4, 5])
    # fmt: on
    def test_solves_the_cube(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that the step, run after the parity step, solves the cube, and records every move it makes in
        the solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "Rw U2 Lw' F Dw")
        solve = SolveNxN(cube)

        # Run the steps
        solve._first_center()
        solve._second_center()
        solve._third_center()
        solve._fourth_center()
        solve._last_two_centers()
        solve._first_eight_edges()
        solve._last_four_edges()
        solve._parity()
        solve._solve_as_3x3()

        # Assert
        replay = generate_cube(cube_size, "Rw U2 Lw' F Dw")
        Rotator(replay).apply(solve.solution)
        assert _is_solved(cube)
        assert replay.layers == cube.layers

    def test_outer_turns_only(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the step alone solves a big cube scrambled by outer-face turns only, which is already
        reduced.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(6, "R U F' L2 D B' R2 U'")
        solve = SolveNxN(cube)

        # Run the step
        solve._solve_as_3x3()

        # Assert
        assert _is_solved(cube)


class TestSolveNxNSolve:
    # fmt: off
    @pytest.mark.parametrize("cube_size", [4, 5, 6, 7])
    # fmt: on
    def test_solves_random_scrambles(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that solving leaves the cube solved, and that the returned solution holds no whole-cube
        rotation and solves the scramble when replayed on it.

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
            assert _is_solved(cube), scramble
            assert _is_solved(replay), scramble
            assert not any(isinstance(move.layer, Rotation) for move in solution.moves)

    # fmt: off
    @pytest.mark.parametrize("cube_size", [4, 5])
    # fmt: on
    def test_steps_true_returns_named_rotation_free_steps_that_solve(
        self, generate_cube: Callable[[int, str], Cube], cube_size: int
    ) -> None:
        """
        Tests that `solve(steps=True)` returns the seven named steps in order, each free of
        whole-cube rotations, that replaying them in order on a cube scrambled the same way solves
        it, and that the solver's own cube ends up solved too. Covers an even and an odd big cube.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube and solve it, split into steps
        scramble = "Rw U2 Lw' F Dw"
        cube = generate_cube(cube_size, scramble)
        steps = SolveNxN(cube).solve(steps=True)

        # Assert the keys and their order
        assert list(steps) == [
            "1st center",
            "2nd center",
            "3rd center",
            "4th center",
            "last 2 centers",
            "edges",
            "3x3 stage",
        ]

        # Assert every step is free of whole-cube rotations
        assert all(not isinstance(move.layer, Rotation) for algorithm in steps.values() for move in algorithm.moves)

        # Assert replaying the steps in order solves a cube scrambled the same way
        replay = " ".join(str(algorithm) for algorithm in steps.values())
        replayed = generate_cube(cube_size, f"{scramble} {replay}")
        assert _is_solved(replayed)

        # Assert the solver's own cube is solved too
        assert _is_solved(cube)
