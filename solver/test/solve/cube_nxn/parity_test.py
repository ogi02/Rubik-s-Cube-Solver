# Python imports
import random
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.scramble.scrambler import Scrambler
from rubik_cube_solver.solve.cube_nxn.centers import build_first_four_centers
from rubik_cube_solver.solve.cube_nxn.edges import build_first_eight_edges, wing_cells
from rubik_cube_solver.solve.cube_nxn.last_centers import build_last_two_centers
from rubik_cube_solver.solve.cube_nxn.last_edges import build_last_four_edges
from rubik_cube_solver.solve.cube_nxn.parity import (
    PARITY_SETUP,
    build_parity,
    flipped_edges,
    oll_parity,
    pair_last_edge,
    permutation_parities_differ,
    pll_parity,
)
from rubik_cube_solver.solve.cube_nxn.routes import trial
from rubik_cube_solver.validator.validator import Validator

# The two edges of UP that both parity algorithms exchange, as whole paired edges.
SWAPPED: set[EdgeSlot] = {EdgeSlot.UL, EdgeSlot.UR}


def _wings(cube: Cube, slot: EdgeSlot) -> list[tuple[Color, Color]]:
    """
    Returns the colours of every wing of a slot, read straight from the raw stickers.

    :param cube: The cube
    :param slot: The edge slot
    :return: The colours of each wing, by index
    """

    size = cube.size

    return [
        tuple(cube.layers[layer][row * size + col] for layer, row, col in wing_cells(size, slot, index))
        for index in range(1, size - 1)
    ]


def _paired(cube: Cube, slot: EdgeSlot) -> bool:
    """
    Checks whether every wing of a slot shows the same colours, by reading raw stickers.

    :param cube: The cube
    :param slot: The edge slot
    :return: Whether the edge in the slot is paired
    """

    return len(set(_wings(cube, slot))) == 1


def _centers(cube: Cube) -> dict[Layer, list[Color]]:
    """
    Returns the center stickers of every face, by reading raw stickers.

    :param cube: The cube
    :return: The center stickers of each face, row by row
    """

    size = cube.size

    return {
        face: [cube.layers[face][row * size + col] for row in range(1, size - 1) for col in range(1, size - 1)]
        for face in Layer
    }


def _corners(cube: Cube) -> dict[Layer, list[Color]]:
    """
    Returns the corner stickers of every face, by reading raw stickers.

    :param cube: The cube
    :return: The four corner stickers of each face
    """

    last = cube.size - 1

    return {
        face: [cube.layers[face][row * cube.size + col] for row in (0, last) for col in (0, last)] for face in Layer
    }


def _as_3x3(cube: Cube) -> Cube:
    """
    Returns the 3x3 a reduced big cube stands for, built from its corners, its outer wings and a center
    sticker of each face.

    :param cube: The big cube, with every center built and every edge paired
    :return: The 3x3
    """

    size = cube.size
    small = Cube(3)
    cells = (0, 1, size - 1)
    small.layers = {face: [cube.layers[face][row * size + col] for row in cells for col in cells] for face in Layer}

    return small


def _reduce_to_last_edge(generate_cube: Callable[[int, str], Cube], size: int, scramble: str) -> Cube:
    """
    Scrambles a cube, builds its centers and pairs every edge but the one in FR.

    :param generate_cube: Fixture generating a cube with an algorithm applied
    :param size: The cube size
    :param scramble: The scramble
    :return: The cube
    """

    cube = generate_cube(size, scramble)
    for step in (build_first_four_centers, build_last_two_centers, build_first_eight_edges, build_last_four_edges):
        cube = trial(cube, " ".join(step(cube)))

    return cube


class TestOllParity:
    # fmt: off
    @pytest.mark.parametrize("size, depth, route", [
        (4, 2, "Rw U2 x Rw U2 Rw U2 Rw' U2 Lw U2 x' Lw' U2 Rw U2 Rw' U2 Rw'"),
        (6, 3, "3Rw U2 x 3Rw U2 3Rw U2 3Rw' U2 3Lw U2 x' 3Lw' U2 3Rw U2 3Rw' U2 3Rw'"),
    ])
    # fmt: on
    def test_success(self, size: int, depth: int, route: str) -> None:
        """
        Tests that the algorithm is written with wide turns of the depth, and a rotation and its inverse.

        :param size: The cube size
        :param depth: The depth of the wide turns
        :param route: The expected algorithm
        :return: None
        """

        # Assert
        assert oll_parity(size, depth) == route

    # fmt: off
    @pytest.mark.parametrize("size, depth, flipped", [
        (4, 2, [1, 2]),
        (5, 2, [1, 3]),
        (6, 2, [1, 4]),
        (6, 3, [1, 2, 3, 4]),
        (7, 2, [1, 5]),
        (7, 3, [1, 2, 4, 5]),
    ])
    # fmt: on
    def test_flips_the_wings(
        self, generate_cube: Callable[[int, str], Cube], size: int, depth: int, flipped: list[int]
    ) -> None:
        """
        Tests that the algorithm turns over exactly the wings of UF the wide turns reach past the outer
        layer and their mirrors, exchanges UL and UR whole, and leaves every other edge and every center
        where it was.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :param depth: The depth of the wide turns
        :param flipped: The indices of UF's wings expected to be turned over
        :return: None
        """

        # Generate the cube
        solved = generate_cube(size, "")
        cube = generate_cube(size, oll_parity(size, depth))

        # Read the wings of UF
        home = _wings(solved, EdgeSlot.UF)[0]
        wings = _wings(cube, EdgeSlot.UF)

        # Assert
        assert [index for index, wing in enumerate(wings, 1) if wing != home] == flipped
        assert all(wings[index - 1] == home[::-1] for index in flipped)
        assert _wings(cube, EdgeSlot.UL) == _wings(solved, EdgeSlot.UR)
        assert _wings(cube, EdgeSlot.UR) == _wings(solved, EdgeSlot.UL)
        assert all(_wings(cube, slot) == _wings(solved, slot) for slot in set(EdgeSlot) - SWAPPED - {EdgeSlot.UF})
        assert _centers(cube) == _centers(solved)


class TestPllParity:
    # fmt: off
    @pytest.mark.parametrize("size, route", [
        (4, "Rw2 R2 U2 Rw2 R2 Uw2 Rw2 R2 Uw2"),
        (6, "3Rw2 R2 U2 3Rw2 R2 3Uw2 3Rw2 R2 3Uw2"),
    ])
    # fmt: on
    def test_success(self, size: int, route: str) -> None:
        """
        Tests that the algorithm is written with turns of half the cube's layers.

        :param size: The cube size
        :param route: The expected algorithm
        :return: None
        """

        # Assert
        assert pll_parity(size) == route

    # fmt: off
    @pytest.mark.parametrize("size", [4, 6])
    # fmt: on
    def test_swaps_two_edges(self, generate_cube: Callable[[int, str], Cube], size: int) -> None:
        """
        Tests that the algorithm exchanges UL and UR whole, leaves every other edge and every center where
        it was, and moves the corners only as `U2` does, so it swaps one pair of edges more than it swaps
        pairs of corners.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        # Generate the cube
        solved = generate_cube(size, "")
        cube = generate_cube(size, pll_parity(size))

        # Assert
        assert _wings(cube, EdgeSlot.UL) == _wings(solved, EdgeSlot.UR)
        assert _wings(cube, EdgeSlot.UR) == _wings(solved, EdgeSlot.UL)
        assert all(_wings(cube, slot) == _wings(solved, slot) for slot in set(EdgeSlot) - SWAPPED)
        assert _centers(cube) == _centers(solved)
        assert _corners(cube) == _corners(generate_cube(size, "U2"))


class TestFlippedEdges:
    # fmt: off
    @pytest.mark.parametrize("size, algorithm, flipped", [
        (4, "",               0),
        (4, "U R D L",        0),
        (4, "F",              4),
        (5, "B'",             4),
        (4, oll_parity(4, 2), 1),
        (6, oll_parity(6, 3), 1),
    ])
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], size: int, algorithm: str, flipped: int) -> None:
        """
        Tests the count on reduced cubes: turns of UP, DOWN, LEFT and RIGHT flip no edge, a quarter turn
        of FRONT or BACK flips four, and the OLL parity algorithm at the innermost depth flips one.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :param algorithm: The algorithm applied to a solved cube
        :param flipped: The expected number of flipped edges
        :return: None
        """

        # Assert
        assert flipped_edges(generate_cube(size, algorithm)) == flipped


class TestPermutationParitiesDiffer:
    # fmt: off
    @pytest.mark.parametrize("size, algorithm, differ", [
        (4, "",                   False),
        (4, "U",                  False),
        (4, "R U R' U'",          False),
        (4, "x y",                False),
        (4, pll_parity(4),        True),
        (6, pll_parity(6),        True),
        (4, f"y {pll_parity(4)}", True),
    ])
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], size: int, algorithm: str, differ: bool) -> None:
        """
        Tests reduced cubes: a face turn moves corners and edges with the same parity, a whole-cube
        rotation carries the centers with the pieces and so changes nothing, and the PLL parity algorithm
        makes the parities differ in any grip.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :param algorithm: The algorithm applied to a solved cube
        :param differ: Whether the parities are expected to differ
        :return: None
        """

        # Assert
        assert permutation_parities_differ(generate_cube(size, algorithm)) is differ


class TestPairLastEdge:
    # fmt: off
    @pytest.mark.parametrize("size, flips, depths", [
        # Already paired
        (4, [],     []),
        (5, [],     []),
        # One pair of wings the other way round
        (5, [2],    [2]),
        (6, [2],    [2]),
        (7, [2],    [2]),
        # Two pairs the other way round, flipped together
        (7, [3],    [3]),
        # The inner pair alone the other way round: flipping it flips the outer pair, which is flipped back
        (7, [3, 2], [3, 2]),
        # The whole edge of an even cube the other way round is still paired
        (6, [3],    []),
    ])
    # fmt: on
    def test_success(
        self, generate_cube: Callable[[int, str], Cube], size: int, flips: list[int], depths: list[int]
    ) -> None:
        """
        Tests that UF's wings are compared with the pivot from the middle outwards, that the OLL parity
        algorithm is applied at the depth of each row found the other way round, and that the edge is
        paired afterwards.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :param flips: The depths of the OLL parity algorithms that set the case up
        :param depths: The depths of the OLL parity algorithms expected to pair the edge
        :return: None
        """

        # Generate the cube
        cube = generate_cube(size, " ".join(oll_parity(size, depth) for depth in flips))

        # Pair the edge
        moves, result = pair_last_edge(cube)

        # Assert
        assert moves == [oll_parity(size, depth) for depth in depths]
        assert _paired(result, EdgeSlot.UF)
        assert result.layers == trial(cube, " ".join(moves)).layers


class TestBuildParity:
    # fmt: off
    @pytest.mark.parametrize("size, algorithm, fixes", [
        # Nothing to fix
        (4, "",                      []),
        (5, "",                      []),
        # The outer wings of FR the other way round on an odd cube
        (5, f"{oll_parity(5, 2)} F", [oll_parity(5, 2)]),
        # A single flipped edge on an even cube
        (4, f"{oll_parity(4, 2)} F", [oll_parity(4, 2)]),
        (6, f"{oll_parity(6, 3)} F", [oll_parity(6, 3)]),
        # Two edges swapped on an even cube
        (4, pll_parity(4),           [pll_parity(4)]),
    ])
    # fmt: on
    def test_success(
        self, generate_cube: Callable[[int, str], Cube], size: int, algorithm: str, fixes: list[str]
    ) -> None:
        """
        Tests that the edge in FR is brought into UF and paired, and that only an even cube is checked for
        a flipped edge and then for swapped edges.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :param algorithm: The algorithm applied to a solved cube
        :param fixes: The algorithms expected after the setup
        :return: None
        """

        # Generate the cube
        cube = generate_cube(size, algorithm)

        # Fix the parities
        moves = build_parity(cube)
        result = trial(cube, " ".join(moves))

        # Assert
        assert moves == [PARITY_SETUP] + fixes
        assert all(_paired(result, slot) for slot in EdgeSlot)
        Validator().validate(_as_3x3(result))

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6, 7])
    # fmt: on
    def test_random_scrambles(self, generate_cube: Callable[[int, str], Cube], size: int) -> None:
        """
        Tests on seeded scrambles that, once the centers are built and eleven edges are paired, every edge
        is paired, every center is still built, and the 3x3 the cube stands for is a legal one.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        random.seed(size)

        for _ in range(3):
            # Scramble the cube and pair every edge but FR's
            scramble = str(Algorithm(Scrambler().generate_scramble(size)))
            cube = _reduce_to_last_edge(generate_cube, size, scramble)

            # Fix the parities
            result = trial(cube, " ".join(build_parity(cube)))

            # Assert
            assert all(_paired(result, slot) for slot in EdgeSlot), scramble
            assert all(len(set(stickers)) == 1 for stickers in _centers(result).values()), scramble
            Validator().validate(_as_3x3(result))
