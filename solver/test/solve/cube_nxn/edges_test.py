# Python imports
import random
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.scramble.scrambler import Scrambler
from rubik_cube_solver.solve.cube_nxn.centers import build_first_four_centers
from rubik_cube_solver.solve.cube_nxn.edges import (
    EDGES_DOWN_CYCLE,
    EDGES_MIDDLE_CYCLE,
    EDGES_UP_CYCLE,
    block_turn,
    build_edge,
    build_first_eight_edges,
    cycle_quarters,
    edge_rows,
    face_turn,
    find_wings,
    fix_free_slice,
    flip,
    front_left_stickers,
    is_paired,
    lined_up,
    open_slot,
    pivot_row,
    slice_turn,
    store_route,
    wing_cells,
    wing_colors,
    wing_routes,
)
from rubik_cube_solver.solve.cube_nxn.last_centers import build_last_two_centers
from rubik_cube_solver.solve.cube_nxn.pieces import Sticker
from rubik_cube_solver.solve.cube_nxn.routes import inverse_of, trial

# Outer face turns only, so every edge of the cube stays paired while the edges are mixed up.
OUTER_TURNS: str = "R U2 F L2 D B R2 U F2 L D2 B' U R F' D L'"

# The whole-cube rotation that turns a solved cube into the grip the centers end in, white on LEFT.
EDGES_GRIP: str = "z'"


def _center_is(cube: Cube, face: Layer, color: Color) -> bool:
    """
    Checks whether every center cell of a face holds a colour, by reading raw stickers.

    :param cube: The cube
    :param face: The face
    :param color: The colour
    :return: Whether the whole center of the face is that colour
    """

    size = cube.size

    return all(cube.layers[face][row * size + col] is color for row in range(1, size - 1) for col in range(1, size - 1))


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


def _paired_on_up_and_down(cube: Cube) -> int:
    """
    Counts the edges of UP and DOWN whose wings all show the same colours.

    :param cube: The cube
    :return: The number of paired edges on UP and DOWN
    """

    return sum(len(set(_wings(cube, slot))) == 1 for slot in EDGES_UP_CYCLE + EDGES_DOWN_CYCLE)


class TestWingCells:
    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6, 7])
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], size: int) -> None:
        """
        Tests that the cells of every slot pair up correctly: on a cube mixed by outer face turns only,
        every edge is still paired, so every wing of a slot shows the same colours in the same order.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(size, OUTER_TURNS)

        # Assert
        for slot in EdgeSlot:
            assert len(set(_wings(cube, slot))) == 1, slot

    # fmt: off
    @pytest.mark.parametrize("slot, cells", [
        (EdgeSlot.FL, ((Layer.FRONT, 1, 0), (Layer.LEFT,  1, 4))),
        (EdgeSlot.UB, ((Layer.UP,    0, 3), (Layer.BACK,  0, 1))),
        (EdgeSlot.DL, ((Layer.DOWN,  3, 0), (Layer.LEFT,  4, 1))),
        (EdgeSlot.BR, ((Layer.BACK,  1, 0), (Layer.RIGHT, 1, 4))),
    ])
    # fmt: on
    def test_cells(self, slot: EdgeSlot, cells: tuple[tuple[Layer, int, int], tuple[Layer, int, int]]) -> None:
        """
        Tests the cells of the first wing of a few slots of a 5x5.

        :param slot: The edge slot
        :param cells: The expected cells
        :return: None
        """

        # Assert
        assert wing_cells(5, slot, 1) == cells


class TestWingColors:
    # fmt: off
    @pytest.mark.parametrize("slot, colors", [
        (EdgeSlot.FL, (Color.GREEN,  Color.ORANGE)),
        (EdgeSlot.UB, (Color.WHITE,  Color.BLUE)),
        (EdgeSlot.DR, (Color.YELLOW, Color.RED)),
    ])
    # fmt: on
    def test_success(
        self, generate_cube: Callable[[int, str], Cube], slot: EdgeSlot, colors: tuple[Color, Color]
    ) -> None:
        """
        Tests that a wing's colours are read in the order of the slot's faces.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param slot: The edge slot
        :param colors: The expected colours on a solved cube
        :return: None
        """

        # Assert
        assert wing_colors(generate_cube(4, ""), slot, 2) == colors


class TestPivotRow:
    # fmt: off
    @pytest.mark.parametrize("size, row", [(4, 1), (5, 2), (6, 2), (7, 3), (8, 3)])
    # fmt: on
    def test_success(self, size: int, row: int) -> None:
        """
        Tests that the pivot is the middle row of an odd cube and the upper middle row of an even one.

        :param size: The cube size
        :param row: The expected row
        :return: None
        """

        # Assert
        assert pivot_row(size) == row


class TestEdgeRows:
    # fmt: off
    @pytest.mark.parametrize("size, rows", [
        (4, [2]),
        (5, [1, 3]),
        (6, [3, 1, 4]),
        (7, [2, 4, 1, 5]),
        (8, [4, 2, 5, 1, 6]),
    ])
    # fmt: on
    def test_success(self, size: int, rows: list[int]) -> None:
        """
        Tests that the rows go from the middle out, upper before lower, and that on an even cube the
        lower middle row comes straight after the pivot.

        :param size: The cube size
        :param rows: The expected rows
        :return: None
        """

        # Assert
        assert edge_rows(size) == rows


class TestIsPaired:
    # fmt: off
    @pytest.mark.parametrize("algorithm, slot, paired", [
        ("",   EdgeSlot.FL, True),
        ("Uw", EdgeSlot.FL, False),
        ("Uw", EdgeSlot.UF, True),
        ("Dw", EdgeSlot.BR, False),
    ])
    # fmt: on
    def test_success(
        self, generate_cube: Callable[[int, str], Cube], algorithm: str, slot: EdgeSlot, paired: bool
    ) -> None:
        """
        Tests that an edge is paired only when every wing matches.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The algorithm applied to a solved 5x5
        :param slot: The edge slot
        :param paired: Whether the edge is expected to be paired
        :return: None
        """

        # Assert
        assert is_paired(generate_cube(5, algorithm), slot) is paired


class TestFindWings:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that both wings of a colour pair in a row and its mirror are found, and nothing else.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "Uw")

        # Assert
        assert find_wings(cube, {Color.GREEN, Color.ORANGE}, 2) == [(EdgeSlot.FL, 2), (EdgeSlot.BL, 1)]

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6, 7])
    # fmt: on
    def test_random_scrambles(self, generate_cube: Callable[[int, str], Cube], size: int) -> None:
        """
        Tests on seeded scrambles that two wings of every colour pair are found for every row, and that
        each found wing holds those colours.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        random.seed(size)
        cube = generate_cube(size, str(Algorithm(Scrambler().generate_scramble(size))))
        pairs = {frozenset(_wings(generate_cube(size, ""), slot)[0]) for slot in EdgeSlot}

        for colors in pairs:
            for row in edge_rows(size):
                # Find the wings
                found = find_wings(cube, set(colors), row)

                # Assert
                assert len(found) == 2
                assert all(set(wing_colors(cube, slot, index)) == colors for slot, index in found)


class TestBlockTurn:
    # fmt: off
    @pytest.mark.parametrize("size, row, direction, turn", [
        (6, 1, Direction.CW,     "Uw"),
        (6, 2, Direction.DOUBLE, "3Uw2"),
        (6, 3, Direction.CCW,    "3Dw'"),
        (5, 3, Direction.CW,     "Dw"),
    ])
    # fmt: on
    def test_success(self, size: int, row: int, direction: Direction, turn: str) -> None:
        """
        Tests that a row is reached from the nearer face, with a block that ends at it.

        :param size: The cube size
        :param row: The row
        :param direction: The direction
        :param turn: The expected turn
        :return: None
        """

        # Assert
        assert block_turn(size, row, direction) == turn


class TestCycleQuarters:
    # fmt: off
    @pytest.mark.parametrize("start, end, quarters", [
        (EdgeSlot.FR, EdgeSlot.FL, 1),
        (EdgeSlot.BR, EdgeSlot.FL, 2),
        (EdgeSlot.BL, EdgeSlot.FL, 3),
        (EdgeSlot.FL, EdgeSlot.FL, 0),
    ])
    # fmt: on
    def test_success(self, start: EdgeSlot, end: EdgeSlot, quarters: int) -> None:
        """
        Tests the number of clockwise quarter turns between two slots of the middle cycle.

        :param start: The slot turned from
        :param end: The slot turned to
        :param quarters: The expected number of quarter turns
        :return: None
        """

        # Assert
        assert cycle_quarters(EDGES_MIDDLE_CYCLE, start, end) == quarters


class TestSliceTurn:
    # fmt: off
    @pytest.mark.parametrize("size, row, start, end, turn", [
        (5, 1, EdgeSlot.FR, EdgeSlot.FL, "Uw"),
        (5, 3, EdgeSlot.FR, EdgeSlot.FL, "Dw'"),
        (5, 3, EdgeSlot.FL, EdgeSlot.FR, "Dw"),
        (7, 2, EdgeSlot.BR, EdgeSlot.FL, "3Uw2"),
        (6, 3, EdgeSlot.BL, EdgeSlot.FL, "3Dw"),
    ])
    # fmt: on
    def test_success(
        self, generate_cube: Callable[[int, str], Cube], size: int, row: int, start: EdgeSlot, end: EdgeSlot, turn: str
    ) -> None:
        """
        Tests the turn, and that it really carries the wing in the start slot's row into the end slot.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :param row: The row
        :param start: The slot the row is carried from
        :param end: The slot the row is carried to
        :param turn: The expected turn
        :return: None
        """

        # Generate the cube
        cube = generate_cube(size, OUTER_TURNS)

        # Turn the row
        result = trial(cube, slice_turn(size, row, start, end))

        # Assert
        assert slice_turn(size, row, start, end) == turn
        assert set(wing_colors(result, end, row)) == set(wing_colors(cube, start, row))


class TestFaceTurn:
    # fmt: off
    @pytest.mark.parametrize("face, cycle, start, end, turn", [
        (Layer.UP,   EDGES_UP_CYCLE,   EdgeSlot.UB, EdgeSlot.UF, "U2"),
        (Layer.UP,   EDGES_UP_CYCLE,   EdgeSlot.UR, EdgeSlot.UF, "U"),
        (Layer.UP,   EDGES_UP_CYCLE,   EdgeSlot.UF, EdgeSlot.UF, ""),
        (Layer.DOWN, EDGES_DOWN_CYCLE, EdgeSlot.DL, EdgeSlot.DF, "D"),
        (Layer.DOWN, EDGES_DOWN_CYCLE, EdgeSlot.DR, EdgeSlot.DF, "D'"),
    ])
    # fmt: on
    def test_success(
        self,
        generate_cube: Callable[[int, str], Cube],
        face: Layer,
        cycle: tuple[EdgeSlot, ...],
        start: EdgeSlot,
        end: EdgeSlot,
        turn: str,
    ) -> None:
        """
        Tests the turn, and that it really carries the edge in the start slot to the end slot.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param face: The face turned
        :param cycle: The face's edge slots
        :param start: The slot the edge is in
        :param end: The slot the edge is carried to
        :param turn: The expected turn
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, OUTER_TURNS)

        # Assert
        assert face_turn(face, cycle, start, end) == turn
        assert set(_wings(trial(cube, turn), end)[0]) == set(_wings(cube, start)[0])


class TestFlip:
    # fmt: off
    @pytest.mark.parametrize("slot", [EdgeSlot.FR, EdgeSlot.BR, EdgeSlot.BL])
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], slot: EdgeSlot) -> None:
        """
        Tests that the edge in the slot is flipped in place, every wing trading places with the one in
        the mirrored row, and that no edge but UP's is moved.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param slot: The slot flipped
        :return: None
        """

        # Generate the cube: split the edges, so every wing is told apart
        cube = generate_cube(6, f"{OUTER_TURNS} Uw 3Dw' R2 Uw2")

        # Flip the edge
        result = trial(cube, flip(slot))

        # Assert
        assert _wings(result, slot) == [(second, first) for first, second in reversed(_wings(cube, slot))]
        for other in set(EdgeSlot) - {slot} - set(EDGES_UP_CYCLE):
            assert _wings(result, other) == _wings(cube, other), other

    def test_rotations(self) -> None:
        """
        Tests that the edge in FR is flipped with no whole-cube rotation around it, and any other slot
        with the rotation that brings it to FR and back.

        :return: None
        """

        # Assert
        assert flip(EdgeSlot.FR) == "R U R' F R' F' R"
        assert flip(EdgeSlot.BL) == "y2 R U R' F R' F' R y2"


class TestWingRoutes:
    # fmt: off
    @pytest.mark.parametrize("size, row, slot, index, routes", [
        # On FL in the mirrored row: turned into FR, flipped, turned back
        (5, 1, EdgeSlot.FL, 3, ["Dw R U R' F R' F' R Uw"]),
        (5, 3, EdgeSlot.FL, 1, ["Uw' R U R' F R' F' R Dw'"]),
        # On FL in the row: nothing to bring
        (5, 1, EdgeSlot.FL, 1, []),
        # Between the side faces, in the row: turned straight in
        (5, 1, EdgeSlot.BR, 1, ["Uw2"]),
        (5, 3, EdgeSlot.BL, 3, ["Dw"]),
        # Between the side faces, in the mirrored row: flipped in place first
        (5, 1, EdgeSlot.FR, 3, ["R U R' F R' F' R Uw"]),
        (5, 1, EdgeSlot.BL, 3, ["y2 R U R' F R' F' R y2 Uw'"]),
        # On UP or DOWN: turned to the front or to the right, then brought in
        (5, 1, EdgeSlot.UB, 1, ["U2 R U' R' Uw", "U F' U F Uw"]),
        (6, 3, EdgeSlot.DL, 2, ["D R' D R 3Dw'", "D2 F D' F' 3Dw'"]),
        (6, 3, EdgeSlot.DF, 2, ["R' D R 3Dw'", "D F D' F' 3Dw'"]),
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
        assert wing_routes(size, row, slot, index) == routes

    # fmt: off
    @pytest.mark.parametrize("size, row, route", [
        (7, 2, "3Dw R U R' F R' F' R 3Uw"),
        (7, 4, "3Dw2"),
        (7, 1, "y R U R' F R' F' R y' Uw2"),
        (7, 5, "U R U' R' Dw'"),
        (7, 2, "U2 F' U F 3Uw"),
        (6, 3, "D2 R' D R 3Dw'"),
        (6, 1, "D' F D' F' Uw"),
    ])
    # fmt: on
    def test_fills_the_row(self, generate_cube: Callable[[int, str], Cube], size: int, row: int, route: str) -> None:
        """
        Tests that, from a cube where a route's inverse took FL's wing away, that route is generated
        for the wing and puts it back without moving the rest of FL.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :param row: The row of FL being filled
        :param route: The route
        :return: None
        """

        # Generate the cube
        cube = generate_cube(size, inverse_of(route))
        wing = wing_colors(generate_cube(size, ""), EdgeSlot.FL, row)

        # Find the routes for the wing
        routes = [
            generated
            for slot, index in find_wings(cube, set(wing), row)
            for generated in wing_routes(size, row, slot, index)
        ]
        result = trial(cube, route)

        # Assert
        assert route in routes
        assert wing_colors(result, EdgeSlot.FL, row) == wing
        assert wing_colors(result, EdgeSlot.FL, pivot_row(size)) == wing


class TestFrontLeftStickers:
    def test_success(self) -> None:
        """
        Tests that both stickers of a wing of FL are tagged with their colours.

        :return: None
        """

        # Assert
        assert front_left_stickers(4, 2, Color.GREEN, Color.ORANGE) == (
            Sticker(Layer.FRONT, 2, 0, Color.GREEN),
            Sticker(Layer.LEFT, 2, 3, Color.ORANGE),
        )


class TestBuildEdge:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the edge in FL is paired around its pivot.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "Uw")

        # Build the edge
        moves, result = build_edge(cube)

        # Assert
        assert moves == ["Dw'"]
        assert is_paired(result, EdgeSlot.FL)

    def test_already_paired(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a paired edge in FL needs no moves.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(5, OUTER_TURNS)

        # Assert
        assert build_edge(cube) == ([], cube)

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6, 7, 8])
    # fmt: on
    def test_random_scrambles(self, generate_cube: Callable[[int, str], Cube], size: int) -> None:
        """
        Tests on seeded scrambles that the edge in FL is paired around the pivot it started with, and
        that the edges of UP and DOWN paired before stay paired.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        random.seed(size)

        for _ in range(3):
            # Scramble the cube, then pair the edges of UP and DOWN with outer turns only
            scramble = f"{Algorithm(Scrambler().generate_scramble(size))}"
            cube = generate_cube(size, scramble)
            pivot = wing_colors(cube, EdgeSlot.FL, pivot_row(size))
            paired = [slot for slot in EDGES_UP_CYCLE + EDGES_DOWN_CYCLE if is_paired(cube, slot)]

            # Build the edge
            _, result = build_edge(cube)

            # Assert
            assert set(_wings(result, EdgeSlot.FL)) == {pivot}, scramble
            assert _paired_on_up_and_down(result) >= len(paired), scramble

    def test_invalid_edge(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a ValueError names the row and the edge when no wing can fill it: the only other
        wing of the pivot's colours was recoloured.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: FL's lower wing no longer shows orange
        cube = generate_cube(4, "")
        cube.layers[Layer.LEFT][2 * 4 + 3] = Color.WHITE

        # Assert
        with pytest.raises(ValueError, match="No route fills row 2 of the GREEN-ORANGE edge"):
            build_edge(cube)


class TestOpenSlot:
    # fmt: off
    @pytest.mark.parametrize("algorithm, slot", [
        ("Uw",          None),
        ("Uw L' U L",   EdgeSlot.UB),
        ("Uw L D' L'",  EdgeSlot.DB),
        ("",            None),
    ])
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], algorithm: str, slot: EdgeSlot | None) -> None:
        """
        Tests that the first unpaired slot of UP is found, then of DOWN.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The algorithm applied to a solved 4x4
        :param slot: The expected slot
        :return: None
        """

        # Assert
        assert open_slot(generate_cube(4, algorithm)) == slot


class TestStoreRoute:
    # fmt: off
    @pytest.mark.parametrize("slot, route", [
        (EdgeSlot.UF, "L' U L"),
        (EdgeSlot.UL, "U' L' U L"),
        (EdgeSlot.UB, "U2 L' U L"),
        (EdgeSlot.UR, "U L' U L"),
        (EdgeSlot.DF, "L D' L'"),
        (EdgeSlot.DR, "D' L D' L'"),
        (EdgeSlot.DB, "D2 L D' L'"),
        (EdgeSlot.DL, "D L D' L'"),
    ])
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], slot: EdgeSlot, route: str) -> None:
        """
        Tests the route, and that it swaps the edge in FL with the edge in the slot.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param slot: The slot stored into
        :param route: The expected route
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, OUTER_TURNS)
        result = trial(cube, route)
        face_slots = EDGES_UP_CYCLE if slot in EDGES_UP_CYCLE else EDGES_DOWN_CYCLE

        # Assert
        assert store_route(slot) == route
        assert set(_wings(result, EdgeSlot.FL)[0]) == set(_wings(cube, slot)[0])
        assert set(_wings(cube, EdgeSlot.FL)[0]) in [set(_wings(result, other)[0]) for other in face_slots]


class TestLinedUp:
    # fmt: off
    @pytest.mark.parametrize("size, algorithm, row, lined", [
        (4, "",      2, True),
        (4, "Dw",    2, False),
        (4, "Dw",    1, True),
        (5, "Uw Dw", 1, False),
        (5, "Uw Dw", 3, False),
    ])
    # fmt: on
    def test_success(
        self, generate_cube: Callable[[int, str], Cube], size: int, algorithm: str, row: int, lined: bool
    ) -> None:
        """
        Tests that a row is lined up only when it shows the pivot row's colour on every side face.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :param algorithm: The algorithm applied to a solved cube
        :param row: The row
        :param lined: Whether the row is expected to be lined up
        :return: None
        """

        # Assert
        assert lined_up(generate_cube(size, algorithm), row) is lined


class TestFixFreeSlice:
    # fmt: off
    @pytest.mark.parametrize("size, algorithm, moves", [
        (4, "Dw",           ["Dw'"]),
        (5, "Uw Dw2",       ["Uw'", "Dw2"]),
        (6, "3Dw Uw",       ["3Dw'", "Uw'"]),
        (7, "Uw 3Uw' Dw",   ["3Uw", "Uw'", "Dw'"]),
        (5, "",             []),
    ])
    # fmt: on
    def test_success(
        self, generate_cube: Callable[[int, str], Cube], size: int, algorithm: str, moves: list[str]
    ) -> None:
        """
        Tests that the rows are lined back up from the middle out, and that the centers end up built.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :param algorithm: The algorithm applied to a solved cube
        :param moves: The expected turns
        :return: None
        """

        # Generate the cube
        cube = generate_cube(size, algorithm)

        # Fix the free slice
        result = fix_free_slice(cube)

        # Assert
        assert result == moves
        assert _centers_built(trial(cube, " ".join(result)))


class TestBuildFirstEightEdges:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the cube is regripped with white on UP, the split edge is paired and stored, and the
        free slice is fixed.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, f"Uw L' U L Uw' {EDGES_GRIP}")

        # Build the edges
        moves = build_first_eight_edges(cube)
        result = trial(cube, " ".join(moves))

        # Assert
        assert moves == ["z", "U2 F' U F Dw'", "U' L' U L", "Dw"]
        assert _paired_on_up_and_down(result) == 8
        assert _center_is(result, Layer.UP, Color.WHITE)
        assert _center_is(result, Layer.DOWN, Color.YELLOW)

    def test_nothing_left_to_store(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that no store follows an edge whose pairing also paired the last open edge of UP and DOWN:
        the only split edge on UP is brought into FR, and the paired edge it swaps with goes up.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, f"Dw R U R' {EDGES_GRIP}")

        # Build the edges
        moves = build_first_eight_edges(cube)

        # Assert
        assert moves == ["z", "R U' R' Dw'"]
        assert _paired_on_up_and_down(trial(cube, " ".join(moves))) == 8

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6, 7])
    # fmt: on
    def test_random_scrambles(self, generate_cube: Callable[[int, str], Cube], size: int) -> None:
        """
        Tests on seeded scrambles that, once the centers are built, eight edges end up paired on UP and
        DOWN, white is on UP, and every center is still built.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        random.seed(size)

        for _ in range(3):
            # Scramble the cube and build the centers
            scramble = str(Algorithm(Scrambler().generate_scramble(size)))
            cube = generate_cube(size, scramble)
            cube = trial(cube, " ".join(build_first_four_centers(cube)))
            cube = trial(cube, " ".join(build_last_two_centers(cube)))

            # Build the edges
            result = trial(cube, " ".join(build_first_eight_edges(cube)))

            # Assert
            assert _paired_on_up_and_down(result) == 8, scramble
            assert _center_is(result, Layer.UP, Color.WHITE), scramble
            assert _centers_built(result), scramble
