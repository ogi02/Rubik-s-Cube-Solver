# Python imports
from itertools import permutations
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.cube_2x2.pll import PLL_TABLE, up_corner_permutation

# The two side stickers of each UP-layer corner of a 2x2 and the two colors that corner shows once
# it is home. Both are spelled out here rather than imported from the production module, so the
# expectations are independent of the constants they are checking, and both are in the slot order
# the PLL_TABLE key uses.
# fmt: off
UP_CORNER_SIDE_STICKERS: tuple[tuple[tuple[Layer, int], ...], ...] = (
    ((Layer.FRONT, 1), (Layer.RIGHT, 0)),  # UFR
    ((Layer.RIGHT, 1), (Layer.BACK,  0)),  # UBR
    ((Layer.BACK,  1), (Layer.LEFT,  0)),  # UBL
    ((Layer.LEFT,  1), (Layer.FRONT, 0)),  # UFL
)

UP_CORNER_SIDE_COLORS: tuple[tuple[Color, ...], ...] = (
    (Color.GREEN,  Color.RED),     # UFR
    (Color.RED,    Color.BLUE),    # UBR
    (Color.BLUE,   Color.ORANGE),  # UBL
    (Color.ORANGE, Color.GREEN),   # UFL
)
# fmt: on


def _cube_is_solved(cube: Cube, solved: Cube) -> bool:
    """
    Checks whether the whole cube is solved, by comparing it sticker for sticker with a freshly
    generated solved cube rather than going through the search helpers, so the oracle is independent
    of the code it is verifying.

    A 2x2 has no centers to compare a face against, so the color scheme of a solved cube is the
    reference - which is also the scheme the first layer was built in.

    :param cube: The Cube instance to check
    :param solved: A solved Cube instance of the same size
    :return: True if the cube is solved, False otherwise
    """

    return cube.layers == solved.layers


class TestUpCornerPermutation:
    @pytest.mark.parametrize("permutation", list(permutations(range(4))))
    def test_success(self, generate_cube: Callable[[int, str], Cube], permutation: tuple[int, ...]) -> None:
        """
        Tests that each UP-layer corner is reported as belonging in the slot whose two colors are
        the ones on its two side stickers. Every corner is painted in place rather than turned into
        position, so the reader is exercised on its own, over all 24 permutations.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param permutation: The home slot of the corner painted into each slot
        :return: None
        """

        # Generate a solved cube and paint each corner with the colors of the slot it belongs in
        cube = generate_cube(2, "")
        for slot, home in enumerate(permutation):
            for (layer, sticker), color in zip(UP_CORNER_SIDE_STICKERS[slot], UP_CORNER_SIDE_COLORS[home]):
                cube.layers[layer][sticker] = color

        # Assert
        assert up_corner_permutation(cube) == permutation

    def test_solved_cube(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that every corner of a solved cube is reported as being in its own slot.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube
        cube = generate_cube(2, "")

        # Assert
        assert up_corner_permutation(cube) == (0, 1, 2, 3)


class TestPllTable:
    @pytest.mark.parametrize("case, algorithm", list(PLL_TABLE.items()))
    def test_permutes_the_last_layer(
        self,
        generate_2x2_pll_case: Callable[[str], Cube],
        generate_cube: Callable[[int, str], Cube],
        case: tuple[int, ...],
        algorithm: str,
    ) -> None:
        """
        Tests every PLL_TABLE entry against the real Rotator: the case it is keyed by is set up by
        applying the entry backwards to a solved cube, which is then asserted to really be that case
        before the entry is applied forwards and has to finish the whole cube.

        Reading the case back off the cube is what makes this more than a tautology - it is the key,
        not the algorithm, that recognition has to agree with.

        :param generate_2x2_pll_case: Fixture generating the case a given permutation algorithm solves
        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param case: The corner permutation the entry is keyed by
        :param algorithm: The permutation algorithm of that entry
        :return: None
        """

        # Generate the case by applying the entry backwards to a solved cube
        cube = generate_2x2_pll_case(algorithm)
        rotator = Rotator(cube)

        # Assert the cube really is in the case the entry is keyed by
        assert up_corner_permutation(cube) == case

        # Permute the last layer
        rotator.apply(Algorithm.from_str(algorithm))

        # Assert
        assert _cube_is_solved(cube, generate_cube(2, ""))

    def test_covers_every_permutation_case(self) -> None:
        """
        Tests that the table holds an entry for every state the step can meet: the four UP corners
        are in one of 24 permutations, and a 2x2 has no edges for their parity to have to match, so
        every one of them is reachable.

        :return: None
        """

        # Assert
        assert set(PLL_TABLE) == set(permutations(range(4)))
