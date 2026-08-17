# Python imports
from itertools import combinations, permutations, product
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.pll import PLL_TABLE, up_corner_permutation, up_edge_permutation

# The two side stickers of each UP-layer corner and the side sticker of each UP-layer edge, as
# (face, flat sticker index) pairs. Both are spelled out here rather than imported from the
# production module, so the expectations are independent of the constants they are checking, and
# both are in the slot order the PLL_TABLE key uses.
# fmt: off
UP_CORNER_SIDE_STICKERS: tuple[tuple[tuple[Layer, int], ...], ...] = (
    ((Layer.FRONT, 2), (Layer.RIGHT, 0)),  # UFR
    ((Layer.RIGHT, 2), (Layer.BACK,  0)),  # UBR
    ((Layer.BACK,  2), (Layer.LEFT,  0)),  # UBL
    ((Layer.LEFT,  2), (Layer.FRONT, 0)),  # UFL
)

UP_EDGE_SIDE_STICKERS: tuple[tuple[Layer, int], ...] = (
    (Layer.FRONT, 1),  # UF
    (Layer.RIGHT, 1),  # UR
    (Layer.BACK,  1),  # UB
    (Layer.LEFT,  1),  # UL
)
# fmt: on


def _cube_is_solved(cube: Cube) -> bool:
    """
    Checks whether the whole cube is solved, by reading raw stickers rather than going through the
    search helpers, so the oracle is independent of the code it is verifying.

    Every sticker of every face must match that face's own center sticker.

    :param cube: The Cube instance to check
    :return: True if every face shows one color, False otherwise
    """

    return all(all(color == face[4] for color in face) for face in cube.layers.values())


def _permutation_parity(permutation: tuple[int, ...]) -> int:
    """
    Returns the parity of a permutation as the number of pairs it holds in the wrong order, modulo
    two - zero for an even permutation and one for an odd one.

    :param permutation: The permutation to measure
    :return: The parity of the permutation
    """

    return sum(permutation[first] > permutation[second] for first, second in combinations(range(4), 2)) % 2


class TestUpCornerPermutation:
    @pytest.mark.parametrize("permutation", list(permutations(range(4))))
    def test_success(self, generate_cube: Callable[[int, str], Cube], permutation: tuple[int, ...]) -> None:
        """
        Tests that each UP-layer corner is reported as belonging in the slot whose two centers show
        the colors on its two side stickers. Every corner is painted in place rather than turned
        into position, so the reader is exercised on its own, over all 24 permutations.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param permutation: The home slot of the corner painted into each slot
        :return: None
        """

        # Generate a solved cube and paint each corner with the colors of the slot it belongs in
        cube = generate_cube(3, "")
        colors = [[cube.layers[layer][4] for layer, _ in stickers] for stickers in UP_CORNER_SIDE_STICKERS]
        for slot, home in enumerate(permutation):
            for (layer, sticker), color in zip(UP_CORNER_SIDE_STICKERS[slot], colors[home]):
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
        cube = generate_cube(3, "")

        # Assert
        assert up_corner_permutation(cube) == (0, 1, 2, 3)


class TestUpEdgePermutation:
    @pytest.mark.parametrize("permutation", list(permutations(range(4))))
    def test_success(self, generate_cube: Callable[[int, str], Cube], permutation: tuple[int, ...]) -> None:
        """
        Tests that each UP-layer edge is reported as belonging in the slot on the face whose center
        shows the color on its side sticker. Every edge is painted in place rather than turned into
        position, so the reader is exercised on its own, over all 24 permutations.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param permutation: The home slot of the edge painted into each slot
        :return: None
        """

        # Generate a solved cube and paint each edge with the color of the slot it belongs in
        cube = generate_cube(3, "")
        colors = [cube.layers[layer][4] for layer, _ in UP_EDGE_SIDE_STICKERS]
        for slot, home in enumerate(permutation):
            layer, sticker = UP_EDGE_SIDE_STICKERS[slot]
            cube.layers[layer][sticker] = colors[home]

        # Assert
        assert up_edge_permutation(cube) == permutation

    def test_solved_cube(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that every edge of a solved cube is reported as being in its own slot.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube
        cube = generate_cube(3, "")

        # Assert
        assert up_edge_permutation(cube) == (0, 1, 2, 3)


class TestPllTable:
    @pytest.mark.parametrize("case, algorithm", list(PLL_TABLE.items()))
    def test_permutes_the_last_layer(
        self,
        generate_pll_case: Callable[[str], Cube],
        case: tuple[tuple[int, ...], tuple[int, ...]],
        algorithm: str,
    ) -> None:
        """
        Tests every PLL_TABLE entry against the real Rotator: the case it is keyed by is set up by
        applying the entry backwards to a solved cube, which is then asserted to really be that
        case before the entry is applied forwards and has to finish the whole cube.

        Reading the case back off the cube is what makes this more than a tautology - it is the
        key, not the algorithm, that recognition has to agree with.

        :param generate_pll_case: Fixture generating the case a given permutation algorithm solves
        :param case: The corner permutation and the edge permutation the entry is keyed by
        :param algorithm: The permutation algorithm of that entry
        :return: None
        """

        # Generate the case by applying the entry backwards to a solved cube
        corner_permutation, edge_permutation = case
        cube = generate_pll_case(algorithm)
        rotator = Rotator(cube)

        # Assert the cube really is in the case the entry is keyed by
        assert up_corner_permutation(cube) == corner_permutation
        assert up_edge_permutation(cube) == edge_permutation

        # Permute the last layer
        rotator.apply(Algorithm.from_str(algorithm))

        # Assert
        assert _cube_is_solved(cube)

    def test_covers_every_permutation_case(self) -> None:
        """
        Tests that the table holds an entry for every state the step can meet: the four UP corners
        and the four UP edges are each in one of 24 permutations, and a cube with its first two
        layers solved is only solvable when the two have the same parity, which pairs them into 288
        states.

        :return: None
        """

        # Build every reachable combination of a corner and an edge permutation
        states = [
            (corners, edges)
            for corners, edges in product(permutations(range(4)), repeat=2)
            if _permutation_parity(corners) == _permutation_parity(edges)
        ]

        # Assert
        assert set(PLL_TABLE) == set(states)
