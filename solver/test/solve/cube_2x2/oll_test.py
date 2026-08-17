# Python imports
from itertools import permutations, product
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.cube_2x2.oll import OLL_TABLE, up_corner_orientations

# The three stickers of each UP-layer corner of a 2x2, in the clockwise order the orientation index
# counts through, and the three colors that corner shows once it is home and oriented. Both are
# spelled out here rather than imported from the production module, so the expectations are
# independent of the constants they are checking, and both are in the slot order the OLL_TABLE key
# uses.
# fmt: off
UP_CORNER_STICKERS: tuple[tuple[tuple[Layer, int], ...], ...] = (
    ((Layer.UP, 3), (Layer.RIGHT, 0), (Layer.FRONT, 1)),  # UFR
    ((Layer.UP, 1), (Layer.BACK,  0), (Layer.RIGHT, 1)),  # UBR
    ((Layer.UP, 0), (Layer.LEFT,  0), (Layer.BACK,  1)),  # UBL
    ((Layer.UP, 2), (Layer.FRONT, 0), (Layer.LEFT,  1)),  # UFL
)

UP_CORNER_COLORS: tuple[tuple[Color, ...], ...] = (
    (Color.WHITE, Color.RED,    Color.GREEN),   # UFR
    (Color.WHITE, Color.BLUE,   Color.RED),     # UBR
    (Color.WHITE, Color.ORANGE, Color.BLUE),    # UBL
    (Color.WHITE, Color.GREEN,  Color.ORANGE),  # UFL
)

# The color each side face shows on its bottom row once the first layer is solved.
FIRST_LAYER_SIDE_COLORS: dict[Layer, Color] = {
    Layer.FRONT: Color.GREEN,
    Layer.RIGHT: Color.RED,
    Layer.BACK:  Color.BLUE,
    Layer.LEFT:  Color.ORANGE,
}
# fmt: on


def _paint_last_layer(cube: Cube, orientations: tuple[int, ...], permutation: tuple[int, ...]) -> None:
    """
    Paints the four UP corners of a cube into the given case, leaving the first layer as it is.

    Each slot is given the colors of the corner that belongs in the slot the permutation names for
    it, rotated so the white sticker lands at the index the orientation names. Painting the case
    rather than turning into it is what lets an orientation be set up in every permutation.

    :param cube: The Cube instance to paint
    :param orientations: The orientation to paint into each slot
    :param permutation: The home slot of the corner to paint into each slot
    :return: None
    """

    for slot, (orientation, home) in enumerate(zip(orientations, permutation)):
        colors = UP_CORNER_COLORS[home]
        colors = colors[-orientation:] + colors[:-orientation] if orientation else colors
        for (layer, sticker), color in zip(UP_CORNER_STICKERS[slot], colors):
            cube.layers[layer][sticker] = color


def _last_layer_is_oriented(cube: Cube) -> bool:
    """
    Checks whether the last layer is oriented, by reading raw stickers rather than going through the
    production reader, so the oracle is independent of the code it is verifying.

    Every sticker of the UP face must be white. A 2x2 has no center to compare a face against, so
    the color scheme the first layer was built in is the reference.

    :param cube: The Cube instance to check
    :return: True if the whole UP face shows white, False otherwise
    """

    return all(color == Color.WHITE for color in cube.layers[Layer.UP])


def _first_layer_is_solved(cube: Cube) -> bool:
    """
    Checks whether the yellow first layer on DOWN is solved, by reading raw stickers rather than
    going through the search helpers, so the oracle is independent of the code it is verifying.

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


class TestUpCornerOrientations:
    # fmt: off
    @pytest.mark.parametrize("position", [0, 1, 2, 3])
    @pytest.mark.parametrize("orientation", [0, 1, 2])
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], position: int, orientation: int) -> None:
        """
        Tests that the orientation of a UP-layer corner is read as the index within its clockwise
        sticker triple at which the white sticker lies. The corner under test is painted in place
        rather than turned into position, so the reader is exercised on its own, and every other
        corner is left oriented so it has to report zero.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param position: The index of the corner under test in the slot order of the table key
        :param orientation: The index of the triple the white sticker is painted onto
        :return: None
        """

        # Generate a solved cube and twist the corner under test in place
        cube = generate_cube(2, "")
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
        cube = generate_cube(2, "")

        # Assert
        assert up_corner_orientations(cube) == (0, 0, 0, 0)


class TestOllTable:
    @pytest.mark.parametrize("case, algorithm", list(OLL_TABLE.items()))
    def test_orients_the_last_layer(
        self,
        generate_2x2_oll_case: Callable[[str], Cube],
        case: tuple[int, ...],
        algorithm: str,
    ) -> None:
        """
        Tests every OLL_TABLE entry against the real Rotator: the case it is keyed by is set up by
        applying the entry backwards to a solved cube, which is then asserted to really be that case
        before the entry is applied forwards and has to orient the whole last layer without breaking
        the first one.

        Reading the case back off the cube is what makes this more than a tautology - it is the key,
        not the algorithm, that recognition has to agree with.

        :param generate_2x2_oll_case: Fixture generating the case a given orientation algorithm solves
        :param case: The corner orientations the entry is keyed by
        :param algorithm: The orientation algorithm of that entry
        :return: None
        """

        # Generate the case by applying the entry backwards to a solved cube
        cube = generate_2x2_oll_case(algorithm)
        rotator = Rotator(cube)

        # Assert the cube really is in the case the entry is keyed by
        assert up_corner_orientations(cube) == case

        # Orient the last layer
        rotator.apply(Algorithm.from_str(algorithm))

        # Assert
        assert _last_layer_is_oriented(cube)
        assert _first_layer_is_solved(cube)

    @pytest.mark.parametrize("case, algorithm", list(OLL_TABLE.items()))
    def test_orients_the_case_in_every_permutation(
        self,
        generate_cube: Callable[[int, str], Cube],
        case: tuple[int, ...],
        algorithm: str,
    ) -> None:
        """
        Tests that an entry solves its case whichever corner sits in which slot, which is what lets
        the table be keyed by orientation alone. The case is painted into all 24 permutations of the
        last layer in turn, since applying the entry backwards can only produce one of them.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param case: The corner orientations the entry is keyed by
        :param algorithm: The orientation algorithm of that entry
        :return: None
        """

        for permutation in permutations(range(4)):
            # Paint the case into the last layer of a solved cube
            cube = generate_cube(2, "")
            _paint_last_layer(cube, case, permutation)

            # Assert the cube really is in the case the entry is keyed by
            assert up_corner_orientations(cube) == case

            # Orient the last layer
            Rotator(cube).apply(Algorithm.from_str(algorithm))

            # Assert
            assert _last_layer_is_oriented(cube)
            assert _first_layer_is_solved(cube)

    def test_covers_every_orientation_case(self) -> None:
        """
        Tests that the table holds an entry for every state the step can meet: each of the four UP
        corners is twisted one of three ways, and a cube is only solvable when the twists sum to a
        multiple of three, which leaves 27 of the 81 states.

        :return: None
        """

        # Build every reachable combination of corner orientations
        states = [state for state in product(range(3), repeat=4) if sum(state) % 3 == 0]

        # Assert
        assert set(OLL_TABLE) == set(states)
