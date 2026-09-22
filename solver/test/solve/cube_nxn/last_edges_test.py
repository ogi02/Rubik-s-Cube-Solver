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
from rubik_cube_solver.solve.cube_nxn.edges import (
    EDGES_DOWN_CYCLE,
    EDGES_UP_CYCLE,
    build_first_eight_edges,
    find_wings,
    pivot_row,
    wing_cells,
    wing_colors,
)
from rubik_cube_solver.solve.cube_nxn.last_centers import build_last_two_centers
from rubik_cube_solver.solve.cube_nxn.last_edges import (
    LAST_EDGES_ENTRIES,
    LAST_EDGES_SETUP,
    build_last_four_edges,
    last_pair_routes,
    middle_routes,
    right_insertion,
)
from rubik_cube_solver.solve.cube_nxn.routes import inverse_of, trial

# Outer face turns, then turns of the inner rows only, so the edges of UP and DOWN stay paired while every
# edge between the side faces is split.
SPLIT_MIDDLE: str = "R U2 F L2 D B R2 U F2 L D2 B' U R F' D L' Uw U' 3Dw' D"


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


def _centers_built(cube: Cube) -> bool:
    """
    Checks whether every face's center is one colour, by reading raw stickers.

    :param cube: The cube
    :return: Whether all six centers are built
    """

    size = cube.size

    return all(
        len({cube.layers[face][row * size + col] for row in range(1, size - 1) for col in range(1, size - 1)}) == 1
        for face in Layer
    )


def _routes_for(cube: Cube, row: int, generate: Callable[[int, int, EdgeSlot, int], list[str]]) -> list[str]:
    """
    Returns every route generated for the wings that can fill a row of FL with the pivot's colours.

    :param cube: The cube
    :param row: The row of FL being filled
    :param generate: The route generator
    :return: The routes, in standard notation
    """

    colors = set(wing_colors(cube, EdgeSlot.FL, pivot_row(cube.size)))

    return [route for slot, index in find_wings(cube, colors, row) for route in generate(cube.size, row, slot, index)]


class TestRightInsertion:
    # fmt: off
    @pytest.mark.parametrize("size, row, helper, route", [
        # The turn of the row also turns the helper face, which is turned back around the store
        (5, 1, Layer.UP,   "Uw U' L' U L Uw' U' L' U L U2"),
        (5, 3, Layer.DOWN, "Dw' D L D' L' Dw D L D' L' D2"),
        # The turn of the row leaves the helper face alone
        (5, 3, Layer.UP,   "Dw' L' U L Dw U2 L' U L U2"),
        (6, 1, Layer.DOWN, "Uw L D' L' Uw' D2 L D' L' D2"),
    ])
    # fmt: on
    def test_success(self, size: int, row: int, helper: Layer, route: str) -> None:
        """
        Tests the insertion for a row reached from each face, with the helper edge on each face.

        :param size: The cube size
        :param row: The row
        :param helper: The face whose front slot holds the unpaired edge
        :param route: The expected insertion
        :return: None
        """

        # Assert
        assert right_insertion(size, row, helper) == route

    # fmt: off
    @pytest.mark.parametrize("row, helper, front, others", [
        (1, Layer.UP,   EdgeSlot.UF, EDGES_DOWN_CYCLE),
        (4, Layer.UP,   EdgeSlot.UF, EDGES_DOWN_CYCLE),
        (1, Layer.DOWN, EdgeSlot.DF, EDGES_UP_CYCLE),
        (4, Layer.DOWN, EdgeSlot.DF, EDGES_UP_CYCLE),
    ])
    # fmt: on
    def test_carries_the_wing(
        self,
        generate_cube: Callable[[int, str], Cube],
        row: int,
        helper: Layer,
        front: EdgeSlot,
        others: tuple[EdgeSlot, ...],
    ) -> None:
        """
        Tests that the wing in FR's row comes into FL's row, that BL, BR and the other face are not
        moved, and that the edges of the helper face stay paired but for the one in its front slot.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param row: The row
        :param helper: The face whose front slot holds the unpaired edge
        :param front: The front slot of the helper face
        :param others: The slots of the other face
        :return: None
        """

        # Generate the cube
        cube = generate_cube(6, SPLIT_MIDDLE)

        # Insert the wing
        result = trial(cube, right_insertion(6, row, helper))

        # Assert
        wing = wing_colors(cube, EdgeSlot.FR, row)
        helper_slots = EDGES_UP_CYCLE if helper is Layer.UP else EDGES_DOWN_CYCLE
        assert wing_colors(result, EdgeSlot.FL, row) == (wing[1], wing[0])
        for slot in (EdgeSlot.BL, EdgeSlot.BR) + others:
            assert _wings(result, slot) == _wings(cube, slot), slot
        for slot in set(helper_slots) - {front}:
            assert _paired(result, slot), slot


class TestMiddleRoutes:
    # fmt: off
    @pytest.mark.parametrize("size, row, slot, index, helper, routes", [
        # On FL in the mirrored row: turned into FR, flipped, turned back, then inserted
        (5, 1, EdgeSlot.FL, 3, Layer.UP,   ["Dw R U R' F R' F' R U' Dw' Uw U' L' U L Uw' U' L' U L U2"]),
        # On FL in the row: nothing to bring
        (5, 1, EdgeSlot.FL, 1, Layer.UP,   []),
        # On FR in the row: inserted
        (5, 1, EdgeSlot.FR, 1, Layer.DOWN, ["Uw L D' L' Uw' D2 L D' L' D2"]),
        # On FR in the mirrored row: flipped first
        (5, 1, EdgeSlot.FR, 3, Layer.UP,   ["R U R' F R' F' R U' Uw U' L' U L Uw' U' L' U L U2"]),
        # On UF or DF: brought into FR keeping or turning over its sticker, then inserted
        (4, 2, EdgeSlot.UF, 1, Layer.UP,   ["R U' R' U2 Dw' L' U L Dw U2 L' U L U2",
                                            "U' F' U F U' Dw' L' U L Dw U2 L' U L U2"]),
        (4, 2, EdgeSlot.DF, 2, Layer.DOWN, ["R' D R D2 Dw' D L D' L' Dw D L D' L' D2",
                                            "D F D' F' D Dw' D L D' L' Dw D L D' L' D2"]),
        # Anywhere else: no route
        (5, 1, EdgeSlot.BL, 1, Layer.UP,   []),
    ])
    # fmt: on
    def test_success(self, size: int, row: int, slot: EdgeSlot, index: int, helper: Layer, routes: list[str]) -> None:
        """
        Tests the routes for each place a wing can be in.

        :param size: The cube size
        :param row: The row of FL being filled
        :param slot: The slot the wing is in
        :param index: The wing's index in the slot
        :param helper: The face whose front slot holds the unpaired edge
        :param routes: The expected routes
        :return: None
        """

        # Assert
        assert middle_routes(size, row, slot, index, helper) == routes

    # fmt: off
    @pytest.mark.parametrize("row, helper, entry", [
        (1, Layer.UP,   ""),
        (4, Layer.DOWN, ""),
        (4, Layer.UP,   "R U R' F R' F' R U'"),
        (2, Layer.UP,   LAST_EDGES_ENTRIES[0][1]),
        (5, Layer.UP,   LAST_EDGES_ENTRIES[0][2]),
        (1, Layer.DOWN, LAST_EDGES_ENTRIES[1][1]),
        (2, Layer.DOWN, LAST_EDGES_ENTRIES[1][2]),
    ])
    # fmt: on
    def test_fills_the_row(
        self, generate_cube: Callable[[int, str], Cube], row: int, helper: Layer, entry: str
    ) -> None:
        """
        Tests that, from a cube where a route's inverse took FL's wing away, that route is generated
        for the wing and puts it back without moving the pivot.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param row: The row of FL being filled
        :param helper: The face whose front slot holds the unpaired edge
        :param entry: What the route does before the insertion
        :return: None
        """

        # Generate the cube
        route = f"{entry} {right_insertion(7, row, helper)}".strip()
        cube = generate_cube(7, inverse_of(route))
        wing = wing_colors(generate_cube(7, ""), EdgeSlot.FL, row)

        # Find the routes for the wing
        routes = _routes_for(cube, row, lambda size, r, slot, index: middle_routes(size, r, slot, index, helper))
        result = trial(cube, route)

        # Assert
        assert route in routes
        assert wing_colors(result, EdgeSlot.FL, row) == wing
        assert wing_colors(result, EdgeSlot.FL, pivot_row(7)) == wing


class TestLastPairRoutes:
    # fmt: off
    @pytest.mark.parametrize("size, row, slot, index, routes", [
        # On FL in the mirrored row: both rows turned into FR, flipped, turned back
        (5, 1, EdgeSlot.FL, 3, ["Uw' Dw R U R' F R' F' R U' Dw' Uw"]),
        # On FL in the row: nothing to bring
        (5, 1, EdgeSlot.FL, 1, []),
        # On FR in the row: taken to BR and flipped there
        (5, 1, EdgeSlot.FR, 1, ["R2 Uw2 y R U R' F R' F' R y' Uw2 R2"]),
        (6, 4, EdgeSlot.FR, 4, ["R2 Dw2 y R U R' F R' F' R y' Dw2 R2"]),
        # On FR in the mirrored row: the row turned into FR, flipped, turned back
        (6, 4, EdgeSlot.FR, 1, ["Dw R U R' F R' F' R U' Dw'"]),
        # Anywhere else: no route
        (5, 1, EdgeSlot.UF, 1, []),
    ])
    # fmt: on
    def test_success(self, size: int, row: int, slot: EdgeSlot, index: int, routes: list[str]) -> None:
        """
        Tests the routes for each place a wing can be in.

        :param size: The cube size
        :param row: The row of FL being filled
        :param slot: The slot the wing is in
        :param index: The wing's index in the slot
        :param routes: The expected routes
        :return: None
        """

        # Assert
        assert last_pair_routes(size, row, slot, index) == routes

    # fmt: off
    @pytest.mark.parametrize("row, slot, index", [
        (1, EdgeSlot.FL, 5),
        (2, EdgeSlot.FR, 2),
        (4, EdgeSlot.FR, 2),
    ])
    # fmt: on
    def test_fills_the_row(
        self, generate_cube: Callable[[int, str], Cube], row: int, slot: EdgeSlot, index: int
    ) -> None:
        """
        Tests that, from a cube where a route's inverse took FL's wing away, that route is generated
        for the wing and puts it back without moving the pivot, BL or BR.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param row: The row of FL being filled
        :param slot: The slot the route brings the wing from
        :param index: The wing's index in the slot
        :return: None
        """

        # Generate the cube
        [route] = last_pair_routes(7, row, slot, index)
        cube = generate_cube(7, inverse_of(route))
        solved = generate_cube(7, "")

        # Find the routes for the wing
        routes = _routes_for(cube, row, last_pair_routes)
        result = trial(cube, route)

        # Assert
        assert route in routes
        assert wing_colors(result, EdgeSlot.FL, row) == wing_colors(solved, EdgeSlot.FL, row)
        assert wing_colors(result, EdgeSlot.FL, pivot_row(7)) == wing_colors(solved, EdgeSlot.FL, row)
        assert _wings(result, EdgeSlot.BL) == _wings(solved, EdgeSlot.BL)
        assert _wings(result, EdgeSlot.BR) == _wings(solved, EdgeSlot.BR)


class TestBuildLastFourEdges:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the setup brings two edges to UF and DF, that each of the first two edges is paired
        in FL and stored, and that the third is paired in FL, leaving every other edge paired.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "Uw")

        # Build the edges
        moves = build_last_four_edges(cube)
        result = trial(cube, " ".join(moves))

        # Assert
        assert moves == [
            LAST_EDGES_SETUP,
            "Dw' L' U L Dw U2 L' U L U2",
            "L' U L",
            "L D' L'",
            "Dw R U R' F R' F' R U' Dw'",
        ]
        assert all(_paired(result, slot) for slot in EdgeSlot)

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6, 7])
    # fmt: on
    def test_random_scrambles(self, generate_cube: Callable[[int, str], Cube], size: int) -> None:
        """
        Tests on seeded scrambles that, once the centers are built and eight edges are stored, every edge
        but FR's is paired, FR holds the wings of one colour pair, and every center is still built.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        random.seed(size)

        for _ in range(3):
            # Scramble the cube, build the centers and store eight edges
            scramble = str(Algorithm(Scrambler().generate_scramble(size)))
            cube = generate_cube(size, scramble)
            for step in (build_first_four_centers, build_last_two_centers, build_first_eight_edges):
                cube = trial(cube, " ".join(step(cube)))

            # Build the edges
            result = trial(cube, " ".join(build_last_four_edges(cube)))

            # Assert
            assert all(_paired(result, slot) for slot in set(EdgeSlot) - {EdgeSlot.FR}), scramble
            assert len({frozenset(wing) for wing in _wings(result, EdgeSlot.FR)}) == 1, scramble
            assert _centers_built(result), scramble
