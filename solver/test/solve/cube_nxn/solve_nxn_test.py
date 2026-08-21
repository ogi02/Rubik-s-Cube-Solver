# Python imports
import random
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation
from rubik_cube_solver.scramble.scrambler import Scrambler
from rubik_cube_solver.solve.cube_nxn.solve_nxn import SolveNxN

# The sizes every big cube test runs on: a 4x4 has a single position type, a 5x5 adds the + center
# and the fixed center that is skipped, and a 6x6 is the smallest cube whose two obliques are
# different pieces and whose deepest layer cannot be named by a wide turn.
SIZES: tuple[int, ...] = (4, 5, 6)

# The colors the four centers are built in, and the face each of them ends up on.
CENTER_FACES: dict[Layer, Color] = {
    Layer.UP: Color.WHITE,
    Layer.DOWN: Color.YELLOW,
    Layer.FRONT: Color.GREEN,
    Layer.RIGHT: Color.RED,
}

# Scrambles chosen to spread the center pieces of the four colors over every face, including the
# ones they end up on. The last three start the cube in another orientation, which only an odd
# cube has fixed centers to correct - an even one is built on whichever face is already there.
# fmt: off
CENTERS_SCRAMBLES: list[str] = [
    "",
    "Rw U2 F Lw' B",
    "Uw R2 Fw' D L2 Bw",
    "R Uw2 Lw F2 Dw' B R2",
    "x Rw' U F2 Dw",
    "y2 Fw D2 Rw B' Uw2",
    "z Lw2 U' Bw R Dw",
]
# fmt: on


def face_is_solid(cube: Cube, layer: Layer, color: Color) -> bool:
    """
    Checks whether the center of a face is built, by reading raw stickers rather than going through
    `search_center`, so the oracle is independent of the production code it is verifying.

    Every inner cell of the face - the fixed center of an odd cube among them - has to show the
    color, which is all a center has to be, since the four pieces of one color and position type
    are interchangeable.

    :param cube: The Cube instance to check
    :param layer: The face to check
    :param color: The color the center is built in
    :return: Whether every center cell of the face shows that color
    """

    size = cube.size

    return all(
        cube.layers[layer][row * size + col] == color for row in range(1, size - 1) for col in range(1, size - 1)
    )


def solid_faces(cube: Cube) -> list[Color]:
    """
    Returns the color of every face whose center is built, in no particular order.

    A solution has its whole-cube rotations stripped before it is handed back, so replaying it on
    another cube finishes the centers on a different set of faces. Which colors came out solid is
    the part of the result that does not depend on how the cube was held.

    :param cube: The Cube instance to check
    :return: The colors whose centers are built
    """

    return [color for layer in Layer for color in Color if face_is_solid(cube, layer, color)]


class TestSolveNxNInit:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that a big cube of any size is accepted, and that the solver holds the very cube it
        was given rather than a copy of it.

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
        Tests that a cube smaller than 4x4, which has no center pieces to build at all, raises a
        ValueError naming the given size at construction rather than part-way through a step.

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
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the reduction has the centers as its only step so far, so a solve runs it and
        nothing else.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the solver
        solver = SolveNxN(generate_cube(4, ""))

        # Assert
        assert [step.__name__ for step in solver._steps()] == ["_centers"]


class TestSolveNxNCenters:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    @pytest.mark.parametrize("scramble", CENTERS_SCRAMBLES)
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], cube_size: int, scramble: str) -> None:
        """
        Tests that the step builds all four centers on the faces they belong on, from a scramble
        and from a cube held any way up, and that it never turns the cube into a state the earlier
        centers do not survive.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param scramble: The scramble to apply before solving
        :return: None
        """

        # Solve the centers
        cube = generate_cube(cube_size, scramble)
        SolveNxN(cube).solve()

        # Assert
        for layer, color in CENTER_FACES.items():
            assert face_is_solid(cube, layer, color)

    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    # fmt: on
    def test_random_scrambles(self, cube_size: int) -> None:
        """
        Tests the step over a batch of random scrambles, seeded so that a failure reproduces, since
        the states the centers can start in are far more varied than a curated list can cover.

        :param cube_size: The cube size
        :return: None
        """

        # Solve every scrambled cube
        random.seed(0)
        for _ in range(20):
            cube = Cube(cube_size)
            Rotator(cube).apply(Algorithm(Scrambler().generate_scramble(cube_size)))
            SolveNxN(cube).solve()

            # Assert
            for layer, color in CENTER_FACES.items():
                assert face_is_solid(cube, layer, color)

    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    # fmt: on
    def test_solution_replays(self, cube_size: int) -> None:
        """
        Tests that the algorithm handed back is the one that did the work: it holds no whole-cube
        rotation, and replaying it on a second cube scrambled the same way builds the same four
        centers. The rotations are stripped, so the replayed cube finishes them on another set of
        faces, and only the colors that came out solid can be compared.

        :param cube_size: The cube size
        :return: None
        """

        # Solve one cube and replay the solution on another
        random.seed(1)
        for _ in range(5):
            scramble = Scrambler().generate_scramble(cube_size)
            cube = Cube(cube_size)
            Rotator(cube).apply(Algorithm(list(scramble)))
            replayed = Cube(cube_size)
            Rotator(replayed).apply(Algorithm(list(scramble)))

            solution = SolveNxN(cube).solve()
            Rotator(replayed).apply(Algorithm(list(solution.moves)))

            # Assert
            assert not any(isinstance(move.layer, Rotation) for move in solution.moves)
            assert sorted(solid_faces(replayed), key=str) == sorted(solid_faces(cube), key=str)
