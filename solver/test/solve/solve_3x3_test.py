# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation
from rubik_cube_solver.solve.cross import face_center_color
from rubik_cube_solver.solve.solve_3x3 import Solve3x3


def _cross_is_solved(cube: Cube) -> bool:
    """
    Checks whether the yellow cross on DOWN is solved, by reading raw stickers rather than going
    through `search_edge`, so the oracle is independent of the production code it is verifying.

    The DOWN face's four edge stickers (flat-list indices 1, 3, 5, 7 on a 3x3 face) must all be
    yellow, and for each of FRONT, RIGHT, BACK and LEFT, the sticker adjacent to DOWN (flat-list
    index 7, empirically confirmed with a D turn on a solved cube: it is the index that ends up
    carrying the neighboring face's color) must match that face's own center color.

    :param cube: The Cube instance to check
    :return: True if the cross is solved, False otherwise
    """

    down = cube.layers[Layer.DOWN]
    if any(down[index] != Color.YELLOW for index in (1, 3, 5, 7)):
        return False

    for layer in (Layer.FRONT, Layer.RIGHT, Layer.BACK, Layer.LEFT):
        if cube.layers[layer][7] != face_center_color(cube, layer):
            return False

    return True


# Setup algorithm that reorients a solved cube so its yellow center lands on the given layer,
# exercising every ORIENTATION_TABLE case when passed through `_cross`.
# fmt: off
ORIENTATION_CASES: dict[Layer, str] = {
    Layer.DOWN:  "",
    Layer.UP:    "x2",
    Layer.FRONT: "x",
    Layer.BACK:  "x'",
    Layer.LEFT:  "z",
    Layer.RIGHT: "z'",
}
# fmt: on

# 13 scrambles that, applied to a solved cube, leave `_cross` to solve the cross from a variety of
# starting cases. Chosen so that between them every EXTRACTION_TABLE, ALIGNMENT_TABLE and
# INSERTION_TABLE entry fires at least once - confirmed by instrumenting `_solve_cross_edge` and
# recording which entry of each table each scramble exercises.
# fmt: off
CROSS_SCRAMBLES: list[str] = [
    "R U R' U'",
    "F R U R' U' F'",
    "R U2 R' U' R U' R'",
    "U R U' L' U R' U' L",
    "F2 R2 U2 L2 B2",
    "R U R' F R F'",
    "U2 F B' R L' U2 F' B",
    "D R F' U L2 D' B R'",
    "L' U R U' L U R'",
    "U R2 F2 U' L2 B2 U",
    "R' F U B' L2 D R",
    "F U' B D2 R' L U",
    "D U R F L",
]
# fmt: on


class TestSolve3x3Init:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a 3x3 cube is accepted without error.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")

        # Assert
        assert Solve3x3(cube).cube is cube

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size", [
            2,
            4,
            5,
        ]
    )
    # fmt: on
    def test_invalid_size(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that a non-3x3 cube raises a ValueError naming the given size.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        with pytest.raises(ValueError, match=f"Solve3x3 supports only 3x3 cubes, got size {cube_size}"):
            Solve3x3(cube)


class TestSolve3x3Steps:
    def test_returns_cross_only(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `_steps` returns exactly the cross step.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")
        solve = Solve3x3(cube)

        # Assert
        assert solve._steps() == [solve._cross]


class TestSolve3x3Cross:
    # fmt: off
    @pytest.mark.parametrize("algorithm", CROSS_SCRAMBLES)
    # fmt: on
    def test_solves_cross_from_scramble(self, generate_cube: Callable[[int, str], Cube], algorithm: str) -> None:
        """
        Tests that `_cross` solves the yellow cross starting from a variety of scrambles, chosen
        so that every EXTRACTION_TABLE, ALIGNMENT_TABLE and INSERTION_TABLE entry is exercised
        somewhere in the table.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The scramble applied before solving the cross
        :return: None
        """

        # Generate the cube and solve the cross
        cube = generate_cube(3, algorithm)
        Solve3x3(cube)._cross()

        # Assert
        assert _cross_is_solved(cube)

    def test_already_solved_cross(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `_cross` adds no moves to the solution when the cross is already solved.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube and solve the cross
        cube = generate_cube(3, "")
        solve = Solve3x3(cube)
        solve._cross()

        # Assert
        assert _cross_is_solved(cube)
        assert solve.solution == Algorithm([])

    def test_partially_solved_cross(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `_cross` solves the cross when it starts partially solved: an `R` turn leaves
        the DL, DB and DF cross edges in place and only DR out of place.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube and solve the cross
        cube = generate_cube(3, "R")
        Solve3x3(cube)._cross()

        # Assert
        assert _cross_is_solved(cube)

    # fmt: off
    @pytest.mark.parametrize(
        "layer", [
            Layer.DOWN,
            Layer.UP,
            Layer.FRONT,
            Layer.BACK,
            Layer.LEFT,
            Layer.RIGHT,
        ]
    )
    # fmt: on
    def test_solves_cross_from_every_orientation(self, generate_cube: Callable[[int, str], Cube], layer: Layer) -> None:
        """
        Tests that `_cross` solves the cross starting from a cube reoriented so the yellow center
        sits on each of the six possible layers in turn, exercising every ORIENTATION_TABLE entry.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param layer: The layer the yellow center starts on
        :return: None
        """

        # Generate the reoriented cube and solve the cross
        cube = generate_cube(3, ORIENTATION_CASES[layer])
        Solve3x3(cube)._cross()

        # Assert
        assert _cross_is_solved(cube)


class TestSolve3x3Solve:
    # fmt: off
    @pytest.mark.parametrize(
        "algorithm", [
            "R U R' U'",
            "x2 D R F' U L2 D' B R'",
        ]
    )
    # fmt: on
    def test_solves_cross_with_no_rotations_in_solution(
        self, generate_cube: Callable[[int, str], Cube], algorithm: str
    ) -> None:
        """
        Tests that `solve` solves the cross on the live cube end to end, and that the returned
        algorithm contains no whole-cube rotations. One scramble starts already yellow-down, the
        other is reoriented first with the even `x2` rotation, which the validator accepts.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The scramble solved end to end
        :return: None
        """

        # Generate the cube and solve it
        cube = generate_cube(3, algorithm)
        result = Solve3x3(cube).solve()

        # Assert the cross is solved on the live cube
        assert _cross_is_solved(cube)

        # Assert the solution contains no whole-cube rotations
        assert all(not isinstance(move.layer, Rotation) for move in result.moves)
