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
from rubik_cube_solver.solve.cube_2x2.solve_2x2 import Solve2x2

# The color each side face shows on its bottom row once the first layer is solved. A 2x2 has no
# centers, so the layer is built in the fixed color scheme of a solved cube and these colors are
# the reference the oracle compares against.
# fmt: off
FIRST_LAYER_SIDE_COLORS: dict[Layer, Color] = {
    Layer.FRONT: Color.GREEN,
    Layer.RIGHT: Color.RED,
    Layer.BACK:  Color.BLUE,
    Layer.LEFT:  Color.ORANGE,
}

# Scrambles that leave `_first_layer` a variety of cases, chosen so that every
# FIRST_LAYER_EXTRACTION_TABLE, FIRST_LAYER_ALIGNMENT_TABLE and FIRST_LAYER_INSERTION_TABLE entry is
# exercised somewhere in the list, together with corners that are already solved and skipped. The
# last four start the cube in another orientation, which the step has no rotation of its own to
# correct.
FIRST_LAYER_SCRAMBLES: list[str] = [
    "R",
    "U R U' R'",
    "F' U R2 F'",
    "R2 F R F",
    "L' B D2 R",
    "y",
    "x U R2 D'",
    "y2 F2 D R B",
    "z2 F L D",
]
# fmt: on


def _first_layer_is_solved(cube: Cube) -> bool:
    """
    Checks whether the yellow first layer on DOWN is solved, by reading raw stickers rather than
    going through `search_corner`, so the oracle is independent of the production code it is
    verifying.

    Every sticker of the DOWN face must be yellow, and the bottom row of each side face - flat-list
    indices 2 and 3 on a 2x2 face - must show that face's color in a solved cube's color scheme.

    :param cube: The Cube instance to check
    :return: True if the first layer is solved, False otherwise
    """

    if any(color != Color.YELLOW for color in cube.layers[Layer.DOWN]):
        return False

    return all(
        cube.layers[layer][index] == color for layer, color in FIRST_LAYER_SIDE_COLORS.items() for index in (2, 3)
    )


class TestSolve2x2Init:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a 2x2 cube is accepted without error.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(2, "")

        # Assert
        assert Solve2x2(cube).cube is cube

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size", [
            3,
            4,
            5,
        ]
    )
    # fmt: on
    def test_invalid_size(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that a non-2x2 cube raises a ValueError naming the given size.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        with pytest.raises(ValueError, match=f"Solve2x2 supports only 2x2 cubes, got size {cube_size}"):
            Solve2x2(cube)


class TestSolve2x2Steps:
    def test_returns_first_layer(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `_steps` returns the first-layer step.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(2, "")
        solve = Solve2x2(cube)

        # Assert
        assert solve._steps() == [solve._first_layer]


class TestSolve2x2SolveFirstLayerCorner:
    def test_solves_the_front_right_corner(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `_solve_first_layer_corner` places the corner it is given into the front-right
        slot of the DOWN layer, from a scramble that leaves it in the UP layer.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube and solve the corner
        cube = generate_cube(2, "R U R'")
        Solve2x2(cube)._solve_first_layer_corner(Color.GREEN, Color.RED)

        # Assert
        assert cube.layers[Layer.DOWN][1] == Color.YELLOW
        assert cube.layers[Layer.FRONT][3] == Color.GREEN
        assert cube.layers[Layer.RIGHT][2] == Color.RED

    def test_already_solved_corner(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `_solve_first_layer_corner` adds no moves to the solution when the corner already
        sits in the front-right slot with its yellow sticker on DOWN.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube and solve the corner
        cube = generate_cube(2, "")
        solve = Solve2x2(cube)
        solve._solve_first_layer_corner(Color.GREEN, Color.RED)

        # Assert
        assert _first_layer_is_solved(cube)
        assert solve.solution == Algorithm([])


class TestSolve2x2FirstLayer:
    # fmt: off
    @pytest.mark.parametrize("algorithm", FIRST_LAYER_SCRAMBLES)
    # fmt: on
    def test_solves_first_layer_from_scramble(self, generate_cube: Callable[[int, str], Cube], algorithm: str) -> None:
        """
        Tests that `_first_layer` solves the yellow layer starting from a variety of scrambles,
        chosen so that every FIRST_LAYER_EXTRACTION_TABLE, FIRST_LAYER_ALIGNMENT_TABLE and
        FIRST_LAYER_INSERTION_TABLE entry is exercised somewhere in the table.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The scramble applied before solving the first layer
        :return: None
        """

        # Generate the cube and solve the first layer
        cube = generate_cube(2, algorithm)
        Solve2x2(cube)._first_layer()

        # Assert
        assert _first_layer_is_solved(cube)

    def test_already_solved_first_layer(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `_first_layer` adds no moves to the solution when the layer is already solved.
        The four `y` rotations the step turns the cube with add up to a full turn, so they cancel
        each other out of the solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube and solve the first layer
        cube = generate_cube(2, "")
        solve = Solve2x2(cube)
        solve._first_layer()

        # Assert
        assert _first_layer_is_solved(cube)
        assert solve.solution == Algorithm([])


class TestSolve2x2Solve:
    # fmt: off
    @pytest.mark.parametrize(
        "algorithm", [
            "R U R' U'",
            "x U R2 F' U R'",
        ]
    )
    # fmt: on
    def test_solves_first_layer_with_no_rotations_in_solution(
        self, generate_cube: Callable[[int, str], Cube], algorithm: str
    ) -> None:
        """
        Tests that `solve` runs the first-layer step on the live cube end to end, leaving the layer
        solved, and that the returned algorithm contains no whole-cube rotations. One scramble
        starts in the orientation of a solved cube, the other is turned on its side first.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The scramble solved end to end
        :return: None
        """

        # Generate the cube and solve it
        cube = generate_cube(2, algorithm)
        result = Solve2x2(cube).solve()

        # Assert the step landed on the live cube
        assert _first_layer_is_solved(cube)

        # Assert the solution contains no whole-cube rotations
        assert all(not isinstance(move.layer, Rotation) for move in result.moves)

    def test_solution_reproduces_the_state(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the returned solution is the algorithm that solves the cube, and not just a
        record of what the step happened to turn: applied to a second cube scrambled the same way,
        it leaves that cube in the same state as the solve left the first one.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Solve one cube and apply its solution to another scrambled the same way
        cube = generate_cube(2, "F R' U2 F' R")
        result = Solve2x2(cube).solve()
        replayed = generate_cube(2, f"F R' U2 F' R {result}")

        # Assert
        assert _first_layer_is_solved(replayed)
        assert replayed.layers == cube.layers

    def test_solves_random_scrambles(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `solve` solves the first layer of a hundred randomly scrambled cubes, which reach
        far more cases between them than the scrambles picked by hand for the step. The random
        number generator is seeded, so a failing run can be reproduced exactly.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Solve a hundred scrambled cubes
        random.seed(0)
        for _ in range(100):
            cube = generate_cube(2, str(Algorithm(Scrambler().generate_scramble(2))))
            Solve2x2(cube).solve()

            # Assert
            assert _first_layer_is_solved(cube)
