# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.CornerSlot import CornerSlot
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation
from rubik_cube_solver.solve.corner_search import search_corner
from rubik_cube_solver.solve.cross import face_center_color
from rubik_cube_solver.solve.edge_search import search_edge
from rubik_cube_solver.solve.f2l import F2L_PAIR_INSERTION_TABLE
from rubik_cube_solver.solve.oll import OLL_TABLE
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


def _pair_is_solved(cube: Cube) -> bool:
    """
    Checks whether the front-right F2L pair fills its slot, by reading raw stickers rather than
    going through `search_corner` and `search_edge`, so the oracle is independent of the production
    code it is verifying.

    The DFR corner shows flat-list index 2 on DOWN, 8 on FRONT and 6 on RIGHT, and the FR edge shows
    index 5 on FRONT and 3 on RIGHT. All five must match the center color of the face they lie on.

    :param cube: The Cube instance to check
    :return: True if the pair fills the front-right slot, False otherwise
    """

    # fmt: off
    pair_stickers = (
        (Layer.DOWN,  2),
        (Layer.FRONT, 8),
        (Layer.RIGHT, 6),
        (Layer.FRONT, 5),
        (Layer.RIGHT, 3),
    )
    # fmt: on

    return all(cube.layers[layer][index] == face_center_color(cube, layer) for layer, index in pair_stickers)


def _first_two_layers_are_solved(cube: Cube) -> bool:
    """
    Checks whether the first two layers are solved, by reading raw stickers rather than going
    through the search helpers, so the oracle is independent of the production code it is verifying.

    Every sticker of the DOWN face must match its center, and on each side face the bottom two rows
    - flat-list indices 3 to 8 on a 3x3 face - must match that face's center.

    :param cube: The Cube instance to check
    :return: True if the first two layers are solved, False otherwise
    """

    if any(color != face_center_color(cube, Layer.DOWN) for color in cube.layers[Layer.DOWN]):
        return False

    for layer in (Layer.FRONT, Layer.RIGHT, Layer.BACK, Layer.LEFT):
        if any(cube.layers[layer][index] != face_center_color(cube, layer) for index in range(3, 9)):
            return False

    return True


def _last_layer_is_oriented(cube: Cube) -> bool:
    """
    Checks whether the last layer is oriented, by reading raw stickers rather than going through
    the OLL readers, so the oracle is independent of the production code it is verifying.

    Every sticker of the UP face must match the UP face's own center sticker.

    :param cube: The Cube instance to check
    :return: True if the whole UP face shows one color, False otherwise
    """

    return all(color == face_center_color(cube, Layer.UP) for color in cube.layers[Layer.UP])


# Setup algorithm that reorients a solved cube so its yellow center lands on the given layer,
# exercising every CROSS_ORIENTATION_TABLE case when passed through `_cross`.
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
# starting cases. Chosen so that between them every CROSS_EXTRACTION_TABLE, CROSS_ALIGNMENT_TABLE and
# CROSS_INSERTION_TABLE entry fires at least once - confirmed by instrumenting `_solve_cross_edge` and
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

# Scrambles that, once `_cross` has run, leave the first pair with its corner in the given
# DOWN-layer slot and its edge in the given equatorial or UP-layer slot. Chosen so that between
# them every F2L_CORNER_EXTRACTION_TABLE and F2L_EDGE_EXTRACTION_TABLE entry fires at least once -
# confirmed by searching random scrambles and recording where each one leaves the pair.
# fmt: off
F2L_EXTRACTION_CASES: list[tuple[str, CornerSlot, EdgeSlot]] = [
    ("F' U2 F' D U' F",   CornerSlot.DFL, EdgeSlot.UB),
    ("U' D' F' B2",       CornerSlot.DFR, EdgeSlot.UB),
    ("L D2 R D U2 R B2",  CornerSlot.DBL, EdgeSlot.BL),
    ("L2 D U' L R' F U2", CornerSlot.DBR, EdgeSlot.BL),
    ("D' U' B2 L2 U' R",  CornerSlot.UBR, EdgeSlot.FL),
    ("F2 L D2 R'",        CornerSlot.DFL, EdgeSlot.FR),
    ("R2 U2 L F2 L2",     CornerSlot.UFR, EdgeSlot.BR),
]

# Scrambles that leave all four pairs to be solved, covering both a cube that is already yellow-down
# and cubes the cross step has to reorient first.
F2L_SCRAMBLES: list[str] = [
    "R U R' U' F R F'",
    "F2 R2 U2 L2 B2 D R F' U",
    "x D R F' U L2 D' B R'",
    "z2 U2 F B' R L' U2 F' B",
    "y' L' U R U' L U R' D2",
]

# Scrambles that leave `_oll` a variety of cases once the cross and the first two layers are done -
# every last-layer edge already oriented, none of them oriented, and states in between - again
# covering both a cube that is already yellow-down and cubes the cross step has to reorient first.
OLL_SCRAMBLES: list[str] = [
    "U2 L2 B' R2 D2 R2 L' B2",
    "R F2 R F R2 U",
    "U B D2 L2 R U D'",
    "U D B' D' F' L",
    "U2 L' U2 L2 D F2 U R'",
    "z2 D U2 D2 R' L D2 B' F2",
    "y' R' U2 L2 U' D2 F' U2 L2 U",
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
    def test_returns_cross_then_f2l_then_oll(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `_steps` returns the cross step, then the first-two-layers step, then the
        orientation step, in that order.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")
        solve = Solve3x3(cube)

        # Assert
        assert solve._steps() == [solve._cross, solve._f2l, solve._oll]


class TestSolve3x3Cross:
    # fmt: off
    @pytest.mark.parametrize("algorithm", CROSS_SCRAMBLES)
    # fmt: on
    def test_solves_cross_from_scramble(self, generate_cube: Callable[[int, str], Cube], algorithm: str) -> None:
        """
        Tests that `_cross` solves the yellow cross starting from a variety of scrambles, chosen
        so that every CROSS_EXTRACTION_TABLE, CROSS_ALIGNMENT_TABLE and CROSS_INSERTION_TABLE entry is exercised
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
        sits on each of the six possible layers in turn, exercising every CROSS_ORIENTATION_TABLE entry.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param layer: The layer the yellow center starts on
        :return: None
        """

        # Generate the reoriented cube and solve the cross
        cube = generate_cube(3, ORIENTATION_CASES[layer])
        Solve3x3(cube)._cross()

        # Assert
        assert _cross_is_solved(cube)


class TestSolve3x3SolveF2LPair:
    @pytest.mark.parametrize("case, algorithm", list(F2L_PAIR_INSERTION_TABLE.items()))
    def test_solves_every_insertion_case(
        self,
        generate_f2l_case: Callable[[str], Cube],
        case: tuple[int, EdgeSlot, bool],
        algorithm: str,
    ) -> None:
        """
        Tests that `_solve_f2l_pair` solves every case of F2L_PAIR_INSERTION_TABLE. Each case is set up
        by applying its entry backwards to a solved cube, so this exercises the whole path the entry
        is reached by - reading the corner's orientation, the edge's slot and the edge's UP sticker,
        and picking the entry keyed by them.

        :param generate_f2l_case: Fixture generating the case a given insertion algorithm solves
        :param case: The corner orientation, edge slot and edge orientation the entry is keyed by
        :param algorithm: The insertion algorithm of that entry
        :return: None
        """

        # Generate the case and solve the pair
        cube = generate_f2l_case(algorithm)
        Solve3x3(cube)._solve_f2l_pair()

        # Assert
        assert _pair_is_solved(cube)
        assert _cross_is_solved(cube)

    # fmt: off
    @pytest.mark.parametrize("algorithm, corner_slot, edge_slot", F2L_EXTRACTION_CASES)
    # fmt: on
    def test_solves_pair_needing_extraction(
        self,
        generate_cube: Callable[[int, str], Cube],
        algorithm: str,
        corner_slot: CornerSlot,
        edge_slot: EdgeSlot,
    ) -> None:
        """
        Tests that `_solve_f2l_pair` solves the pair when one or both of its pieces start buried in
        the first two layers, exercising every F2L_CORNER_EXTRACTION_TABLE and F2L_EDGE_EXTRACTION_TABLE
        entry between them.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The scramble applied before the cross is solved
        :param corner_slot: The slot the pair's corner sits in once the cross is solved
        :param edge_slot: The slot the pair's edge sits in once the cross is solved
        :return: None
        """

        # Generate the cube and solve the cross, which is what the pair is solved on top of
        cube = generate_cube(3, algorithm)
        solve = Solve3x3(cube)
        solve._cross()

        # Assert the scramble really leaves the pair in the slots it is chosen for
        front_color = face_center_color(cube, Layer.FRONT)
        right_color = face_center_color(cube, Layer.RIGHT)
        assert search_corner(cube, Color.YELLOW, front_color, right_color).slot is corner_slot
        assert search_edge(cube, front_color, right_color).slot is edge_slot

        # Solve the pair
        solve._solve_f2l_pair()

        # Assert
        assert _pair_is_solved(cube)
        assert _cross_is_solved(cube)

    def test_already_solved_pair(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `_solve_f2l_pair` adds no moves to the solution when the pair already fills the
        front-right slot.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube and solve the pair
        cube = generate_cube(3, "")
        solve = Solve3x3(cube)
        solve._solve_f2l_pair()

        # Assert
        assert _pair_is_solved(cube)
        assert solve.solution == Algorithm([])


class TestSolve3x3F2L:
    # fmt: off
    @pytest.mark.parametrize("algorithm", F2L_SCRAMBLES)
    # fmt: on
    def test_solves_first_two_layers(self, generate_cube: Callable[[int, str], Cube], algorithm: str) -> None:
        """
        Tests that `_f2l` solves all four pairs on top of the cross, from scrambles that leave every
        pair to be solved and from cubes the cross step has to reorient first.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The scramble applied before solving
        :return: None
        """

        # Generate the cube and solve the cross and the first two layers
        cube = generate_cube(3, algorithm)
        solve = Solve3x3(cube)
        solve._cross()
        solve._f2l()

        # Assert
        assert _first_two_layers_are_solved(cube)

    def test_already_solved_first_two_layers(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `_f2l` adds no moves to the solution when all four pairs are already solved. The
        four `y` rotations that carry it round the cube cancel each other out.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube and solve the first two layers
        cube = generate_cube(3, "")
        solve = Solve3x3(cube)
        solve._f2l()

        # Assert
        assert _first_two_layers_are_solved(cube)
        assert solve.solution == Algorithm([])


class TestSolve3x3Oll:
    @pytest.mark.parametrize("case, algorithm", list(OLL_TABLE.items()))
    def test_solves_every_case(
        self,
        generate_oll_case: Callable[[str], Cube],
        case: tuple[tuple[int, ...], tuple[bool, ...]],
        algorithm: str,
    ) -> None:
        """
        Tests that `_oll` orients the last layer in every case of OLL_TABLE. Each case is set up by
        applying its entry backwards to a solved cube, so this exercises the whole path the entry is
        reached by - reading the orientation of the four UP corners and the four UP edges, and
        picking the entry keyed by them.

        :param generate_oll_case: Fixture generating the case a given orientation algorithm solves
        :param case: The corner orientations and the edge orientations the entry is keyed by
        :param algorithm: The orientation algorithm of that entry
        :return: None
        """

        # Generate the case and orient the last layer
        cube = generate_oll_case(algorithm)
        Solve3x3(cube)._oll()

        # Assert
        assert _last_layer_is_oriented(cube)
        assert _first_two_layers_are_solved(cube)

    # fmt: off
    @pytest.mark.parametrize("algorithm", OLL_SCRAMBLES)
    # fmt: on
    def test_orients_last_layer_after_first_two_layers(
        self, generate_cube: Callable[[int, str], Cube], algorithm: str
    ) -> None:
        """
        Tests that `_oll` orients the last layer on top of a finished first two layers, from
        scrambles that reach it through the cross and F2L steps rather than through a constructed
        case.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The scramble applied before solving
        :return: None
        """

        # Generate the cube and solve the cross, the first two layers and the orientation
        cube = generate_cube(3, algorithm)
        solve = Solve3x3(cube)
        solve._cross()
        solve._f2l()
        solve._oll()

        # Assert
        assert _last_layer_is_oriented(cube)
        assert _first_two_layers_are_solved(cube)

    def test_already_oriented_last_layer(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `_oll` adds no moves to the solution when the last layer is already oriented.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube and orient the last layer
        cube = generate_cube(3, "")
        solve = Solve3x3(cube)
        solve._oll()

        # Assert
        assert _last_layer_is_oriented(cube)
        assert solve.solution == Algorithm([])


class TestSolve3x3Solve:
    # fmt: off
    @pytest.mark.parametrize(
        "algorithm", [
            "R U R' U'",
            "x D R F' U L2 D' B R'",
        ]
    )
    # fmt: on
    def test_solves_every_step_with_no_rotations_in_solution(
        self, generate_cube: Callable[[int, str], Cube], algorithm: str
    ) -> None:
        """
        Tests that `solve` runs every step on the live cube end to end - the cross, the first two
        layers and the orientation of the last layer - and that the returned algorithm contains no
        whole-cube rotations. One scramble starts already yellow-down, the other is reoriented first.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The scramble solved end to end
        :return: None
        """

        # Generate the cube and solve it
        cube = generate_cube(3, algorithm)
        result = Solve3x3(cube).solve()

        # Assert every step landed on the live cube
        assert _cross_is_solved(cube)
        assert _first_two_layers_are_solved(cube)
        assert _last_layer_is_oriented(cube)

        # Assert the solution contains no whole-cube rotations
        assert all(not isinstance(move.layer, Rotation) for move in result.moves)
