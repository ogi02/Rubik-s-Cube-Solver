# Python imports
from itertools import product
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.cube_3x3.oll import OLL_TABLE, up_corner_orientations, up_edge_orientations

# The three stickers of each UP-layer corner, in the clockwise order the orientation index counts
# through, and the UP-face sticker of each UP-layer edge. Both are spelled out here rather than
# imported from the production module, so the expectations are independent of the constants they
# are checking, and both are in the slot order the OLL_TABLE key uses.
# fmt: off
UP_CORNER_STICKERS: tuple[tuple[tuple[Layer, int], ...], ...] = (
    ((Layer.UP, 8), (Layer.RIGHT, 0), (Layer.FRONT, 2)),  # UFR
    ((Layer.UP, 2), (Layer.BACK,  0), (Layer.RIGHT, 2)),  # UBR
    ((Layer.UP, 0), (Layer.LEFT,  0), (Layer.BACK,  2)),  # UBL
    ((Layer.UP, 6), (Layer.FRONT, 0), (Layer.LEFT,  2)),  # UFL
)

UP_EDGE_STICKERS: tuple[int, ...] = (7, 5, 1, 3)  # UF, UR, UB, UL
# fmt: on


def _last_layer_is_oriented(cube: Cube) -> bool:
    """
    Checks whether the last layer is oriented, by reading raw stickers rather than going through
    the production readers, so the oracle is independent of the code it is verifying.

    Every sticker of the UP face must match the UP face's own center sticker.

    :param cube: The Cube instance to check
    :return: True if the whole UP face shows one color, False otherwise
    """

    up = cube.layers[Layer.UP]

    return all(color == up[4] for color in up)


def _first_two_layers_are_solved(cube: Cube) -> bool:
    """
    Checks whether the first two layers are solved, by reading raw stickers rather than going
    through the search helpers, so the oracle is independent of the code it is verifying.

    Every sticker of the DOWN face must match its center, and on each side face the bottom two rows
    - flat-list indices 3 to 8 on a 3x3 face - must match that face's center.

    :param cube: The Cube instance to check
    :return: True if the first two layers are solved, False otherwise
    """

    down = cube.layers[Layer.DOWN]
    if any(color != down[4] for color in down):
        return False

    for layer in (Layer.FRONT, Layer.RIGHT, Layer.BACK, Layer.LEFT):
        face = cube.layers[layer]
        if any(face[index] != face[4] for index in range(3, 9)):
            return False

    return True


class TestUpCornerOrientations:
    # fmt: off
    @pytest.mark.parametrize("position", [0, 1, 2, 3])
    @pytest.mark.parametrize("orientation", [0, 1, 2])
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], position: int, orientation: int) -> None:
        """
        Tests that the orientation of a UP-layer corner is read as the index within its clockwise
        sticker triple at which the UP center's color lies. The corner under test is painted in
        place rather than turned into position, so the reader is exercised on its own, and every
        other corner is left oriented so it has to report zero.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param position: The index of the corner under test in the slot order of the table key
        :param orientation: The index of the triple the white sticker is painted onto
        :return: None
        """

        # Generate a solved cube and twist the corner under test in place
        cube = generate_cube(3, "")
        for index, (layer, sticker) in enumerate(UP_CORNER_STICKERS[position]):
            cube.layers[layer][sticker] = Color.WHITE if index == orientation else Color.GREEN

        # Assert
        expected = tuple(orientation if index == position else 0 for index in range(4))
        assert up_corner_orientations(cube) == expected

    def test_solved_cube(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that every corner of a solved cube is reported as oriented.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube
        cube = generate_cube(3, "")

        # Assert
        assert up_corner_orientations(cube) == (0, 0, 0, 0)


class TestUpEdgeOrientations:
    # fmt: off
    @pytest.mark.parametrize("position", [0, 1, 2, 3])
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], position: int) -> None:
        """
        Tests that a UP-layer edge is reported as unoriented once its UP sticker no longer shows
        the UP center's color, and that the other three are unaffected.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param position: The index of the edge under test in the slot order of the table key
        :return: None
        """

        # Generate a solved cube and flip the edge under test in place
        cube = generate_cube(3, "")
        cube.layers[Layer.UP][UP_EDGE_STICKERS[position]] = Color.GREEN

        # Assert
        expected = tuple(index != position for index in range(4))
        assert up_edge_orientations(cube) == expected

    def test_solved_cube(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that every edge of a solved cube is reported as oriented.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube
        cube = generate_cube(3, "")

        # Assert
        assert up_edge_orientations(cube) == (True, True, True, True)


class TestOllTable:
    @pytest.mark.parametrize("case, algorithm", list(OLL_TABLE.items()))
    def test_orients_the_last_layer(
        self,
        generate_3x3_oll_case: Callable[[str], Cube],
        case: tuple[tuple[int, ...], tuple[bool, ...]],
        algorithm: str,
    ) -> None:
        """
        Tests every OLL_TABLE entry against the real Rotator: the case it is keyed by is set up by
        applying the entry backwards to a solved cube, which is then asserted to really be that
        case before the entry is applied forwards and has to orient the whole last layer.

        Reading the case back off the cube is what makes this more than a tautology - it is the
        key, not the algorithm, that recognition has to agree with.

        :param generate_3x3_oll_case: Fixture generating the case a given orientation algorithm solves
        :param case: The corner orientations and the edge orientations the entry is keyed by
        :param algorithm: The orientation algorithm of that entry
        :return: None
        """

        # Generate the case by applying the entry backwards to a solved cube
        corner_orientations, edge_orientations = case
        cube = generate_3x3_oll_case(algorithm)
        rotator = Rotator(cube)

        # Assert the cube really is in the case the entry is keyed by
        assert up_corner_orientations(cube) == corner_orientations
        assert up_edge_orientations(cube) == edge_orientations

        # Orient the last layer
        rotator.apply(Algorithm.from_str(algorithm))

        # Assert
        assert _last_layer_is_oriented(cube)
        assert _first_two_layers_are_solved(cube)

    def test_covers_every_orientation_case(self) -> None:
        """
        Tests that the table holds an entry for every state the step can meet: each of the four UP
        corners is oriented one of three ways and each of the four UP edges one of two, and a cube
        is only solvable when the corner twists sum to a multiple of three and an even number of
        edges is flipped, which leaves 27 corner states and 8 edge states.

        :return: None
        """

        # Build every reachable combination of corner and edge orientations
        corner_states = [state for state in product(range(3), repeat=4) if sum(state) % 3 == 0]
        edge_states = [state for state in product([True, False], repeat=4) if sum(state) % 2 == 0]

        # Assert
        assert set(OLL_TABLE) == set(product(corner_states, edge_states))
